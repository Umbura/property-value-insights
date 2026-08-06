"""FastAPI application serving the approved property value model."""

from __future__ import annotations

import re
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, metadata as package_metadata
from time import perf_counter
from typing import Any, AsyncIterator, Mapping
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .artifact import ArtifactIntegrityError, load_model_bundle_with_manifest, predict_future
from .config import Settings
from .observability import OperationalMetrics, configure_logging
from .schemas import (
    ApiIdentity,
    ArtifactIdentity,
    BatchPredictionItem,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    InternalErrorResponse,
    ModelInfoResponse,
    ModelServingIdentity,
    PredictionResponse,
    ProjectIdentity,
    PropertyFeatures,
)

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
PROJECT_DISTRIBUTION = "property-value-insights"
API_VERSION = "0.5.0-rc1"


def _request_id(request: Request) -> str:
    supplied = request.headers.get("X-Request-ID", "")
    return supplied if REQUEST_ID_PATTERN.fullmatch(supplied) else uuid4().hex


def _prediction_frame(items: list[PropertyFeatures]) -> pd.DataFrame:
    return pd.DataFrame([item.model_dump() for item in items])


def _project_identity() -> ProjectIdentity:
    try:
        installed_metadata = package_metadata(PROJECT_DISTRIBUTION)
    except PackageNotFoundError as error:
        raise ArtifactIntegrityError("Installed project metadata is unavailable") from error

    name = installed_metadata.get("Name")
    release = installed_metadata.get("Version")
    if not isinstance(name, str) or not name or not isinstance(release, str) or not release:
        raise ArtifactIntegrityError("Installed project metadata is incomplete")
    return ProjectIdentity(name=name, release=release)


def _model_info_from_manifest(manifest: Mapping[str, Any]) -> ModelInfoResponse:
    try:
        model = manifest["model"]
        artifact = manifest["artifact"]
        return ModelInfoResponse(
            name=model["name"],
            model_version=model["version"],
            algorithm=model["algorithm"],
            feature_set=model["feature_set"],
            feature_columns=model["feature_columns"],
            created_at_utc=manifest["created_at_utc"],
            artifact_sha256=artifact["sha256"],
            evaluation=manifest["evaluation"],
            limitations=manifest["limitations"],
            project=_project_identity(),
            api=ApiIdentity(version=API_VERSION),
            model=ModelServingIdentity(
                display_name=f"{model['algorithm']} ({model['feature_set']} feature set)",
                technical_name=model["name"],
                version=model["version"],
                algorithm=model["algorithm"],
                feature_set=model["feature_set"],
                serving_status="approved",
            ),
            artifact=ArtifactIdentity(
                sha256=artifact["sha256"],
                created_at_utc=manifest["created_at_utc"],
                schema_version=manifest["schema_version"],
            ),
        )
    except (KeyError, TypeError, ValidationError) as error:
        raise ArtifactIntegrityError(
            "Model manifest contains invalid serving metadata"
        ) from error


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an isolated API instance with its own model state and metrics."""

    runtime_settings = settings or Settings.from_env()
    logger = configure_logging(runtime_settings.log_level)
    metrics = OperationalMetrics()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        bundle, manifest = load_model_bundle_with_manifest(
            runtime_settings.artifact_path,
            manifest_path=runtime_settings.manifest_path,
        )
        model_info = _model_info_from_manifest(manifest)
        app.state.bundle = bundle
        app.state.model_info = model_info
        logger.info(
            "model_loaded",
            extra={"model_version": bundle["model_version"]},
        )
        yield
        app.state.bundle = None

    app = FastAPI(
        title="Property Value Insights API",
        version=API_VERSION,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "Service Operations",
                "description": (
                    "Operações de serviço para verificar disponibilidade e consultar "
                    "metadados do modelo servido."
                ),
            },
            {
                "name": "Model Inference",
                "description": (
                    "Operações de inferência para previsão de valor de imóveis em modo "
                    "único ou em lote."
                ),
            },
        ],
    )
    app.state.settings = runtime_settings
    app.state.metrics = metrics

    @app.middleware("http")
    async def observe_request(request: Request, call_next: Any) -> Response:
        request_id = _request_id(request)
        request.state.request_id = request_id
        started = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            elapsed = perf_counter() - started
            route = getattr(request.scope.get("route"), "path", "unmatched")
            metrics.requests.labels(request.method, route, str(status_code)).inc()
            metrics.duration.labels(request.method, route).observe(elapsed)
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": route,
                    "status_code": status_code,
                    "duration_ms": round(elapsed * 1000, 3),
                },
            )
            if "response" in locals():
                response.headers["X-Request-ID"] = request_id

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", uuid4().hex)
        metrics.failures.labels(type(error).__name__).inc()
        logger.exception(
            "request_failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
            },
        )
        payload = InternalErrorResponse(request_id=request_id)
        return JSONResponse(
            status_code=500,
            content=payload.model_dump(),
            headers={"X-Request-ID": request_id},
        )

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Service Operations"],
        summary="Check service startup readiness",
        description=(
            "Confirma que o processo da API concluiu a inicialização e que o bundle do "
            "modelo está carregado após o artefato e o manifesto terem sido aceitos pelas "
            "verificações executadas no startup. A chamada não executa inferência, não "
            "testa conectividade com serviços externos e não relê nem recalcula o hash do "
            "artefato a cada requisição."
        ),
    )
    def health(request: Request) -> HealthResponse:
        return HealthResponse(
            status="healthy",
            api_version=API_VERSION,
            model_version=request.app.state.bundle["model_version"],
        )

    @app.get(
        "/model-info",
        response_model=ModelInfoResponse,
        tags=["Service Operations"],
        summary="View project, API, model, and artifact identity",
        description=(
            "Expõe os campos históricos de metadados e adiciona blocos estruturados para "
            "distinguir a release do projeto, a versão da API, a identidade do modelo "
            "aprovado para serving e a identidade do artefato verificado."
        ),
    )
    def model_info(request: Request) -> ModelInfoResponse:
        return request.app.state.model_info

    @app.post(
        "/predict",
        response_model=PredictionResponse,
        responses={500: {"model": InternalErrorResponse}},
        tags=["Model Inference"],
        summary="Predict one property value",
        description=(
            "Calcula a previsão de valor para um único imóvel com base nas features "
            "informadas e retorna preço previsto, versão do modelo e request_id."
        ),
    )
    def predict(payload: PropertyFeatures, request: Request) -> PredictionResponse:
        result = predict_future(request.app.state.bundle, _prediction_frame([payload])).iloc[0]
        metrics.predictions.labels("single").inc()
        return PredictionResponse(
            predicted_price=float(result["predicted_price"]),
            model_version=str(result["model_version"]),
            request_id=request.state.request_id,
        )

    @app.post(
        "/predict/batch",
        response_model=BatchPredictionResponse,
        responses={
            413: {
                "description": (
                    "O lote excede o limite atual de "
                    f"{runtime_settings.max_batch_size} itens. O padrão é 100 e "
                    "MAX_BATCH_SIZE pode ser configurado entre 1 e 1000."
                ),
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["detail"],
                            "properties": {"detail": {"type": "string"}},
                        },
                        "example": {
                            "detail": (
                                "Batch exceeds the limit of "
                                f"{runtime_settings.max_batch_size} items"
                            )
                        },
                    }
                },
            },
            500: {
                "model": InternalErrorResponse,
                "description": (
                    "Falha inesperada de processamento, correlacionada pelo request_id."
                ),
            },
        },
        openapi_extra={
            "responses": {
                "422": {
                    "description": (
                        "Falha de validação antes da inferência. O lote usa política "
                        "all-or-nothing: qualquer item inválido rejeita a requisição "
                        "inteira, sem resultados parciais."
                    )
                }
            }
        },
        tags=["Model Inference"],
        summary="Predict multiple property values",
        description=(
            "Processa múltiplos imóveis em uma única requisição, preserva a ordem de "
            "entrada e aplica o limite máximo de itens por lote configurado no serviço."
        ),
    )
    def predict_batch(
        payload: BatchPredictionRequest,
        request: Request,
    ) -> BatchPredictionResponse:
        if len(payload.items) > runtime_settings.max_batch_size:
            raise HTTPException(
                status_code=413,
                detail=f"Batch exceeds the limit of {runtime_settings.max_batch_size} items",
            )
        result = predict_future(request.app.state.bundle, _prediction_frame(payload.items))
        metrics.predictions.labels("batch").inc(len(result))
        logger.info(
            "prediction_batch_completed",
            extra={
                "request_id": request.state.request_id,
                "model_version": result["model_version"].iloc[0],
                "prediction_count": len(result),
            },
        )
        return BatchPredictionResponse(
            predictions=[
                BatchPredictionItem(
                    item_id=int(row.row_id),
                    predicted_price=float(row.predicted_price),
                )
                for row in result.itertuples(index=False)
            ],
            model_version=str(result["model_version"].iloc[0]),
            request_id=request.state.request_id,
        )

    @app.get("/metrics", include_in_schema=False)
    def prometheus_metrics() -> Response:
        content, content_type = metrics.render()
        return Response(content=content, headers={"Content-Type": content_type})

    return app


app = create_app()


__all__ = ["app", "create_app", "ArtifactIntegrityError"]
