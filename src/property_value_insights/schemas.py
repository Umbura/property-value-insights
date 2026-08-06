"""Public request and response schemas for property value inference."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PROPERTY_EXAMPLE: dict[str, object] = {
    "bedrooms": 4,
    "bathrooms": 1.0,
    "sqft_living": 1680,
    "sqft_lot": 5043,
    "floors": 1.5,
    "waterfront": 0,
    "view": 0,
    "condition": 4,
    "grade": 6,
    "sqft_above": 1680,
    "sqft_basement": 0,
    "yr_built": 1911,
    "yr_renovated": 0,
    "zipcode": "98118",
    "lat": 47.5354,
    "long": -122.273,
    "sqft_living15": 1560,
    "sqft_lot15": 5765,
}

SECOND_PROPERTY_EXAMPLE: dict[str, object] = {
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft_living": 2220,
    "sqft_lot": 6380,
    "floors": 1.5,
    "waterfront": 0,
    "view": 0,
    "condition": 4,
    "grade": 8,
    "sqft_above": 1660,
    "sqft_basement": 560,
    "yr_built": 1931,
    "yr_renovated": 0,
    "zipcode": "98115",
    "lat": 47.6974,
    "long": -122.313,
    "sqft_living15": 950,
    "sqft_lot15": 6380,
}


class PropertyFeatures(BaseModel):
    """Features available for one property at inference time."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        json_schema_extra={"examples": [PROPERTY_EXAMPLE]},
    )

    bedrooms: int = Field(
        ge=0,
        description="Quantidade de quartos do imóvel.",
        examples=[4],
    )
    bathrooms: float = Field(
        ge=0,
        description=(
            "Quantidade de banheiros do imóvel; valores fracionários representam "
            "banheiros parciais."
        ),
        examples=[1.0],
    )
    sqft_living: int = Field(
        ge=0,
        description="Área interna habitável do imóvel, em pés quadrados.",
        examples=[1680],
    )
    sqft_lot: int = Field(
        ge=0,
        description="Área total do terreno, em pés quadrados.",
        examples=[5043],
    )
    floors: float = Field(
        ge=0,
        description=(
            "Quantidade de pavimentos; valores fracionários representam configurações "
            "com meio pavimento."
        ),
        examples=[1.5],
    )
    waterfront: int = Field(
        ge=0,
        le=1,
        description="Indicador binário de frente para água: 0 = não; 1 = sim.",
        examples=[0],
    )
    view: int = Field(
        ge=0,
        le=4,
        description="Código ordinal da avaliação da vista, de 0 a 4.",
        examples=[0],
    )
    condition: int = Field(
        ge=1,
        le=5,
        description="Código ordinal da condição geral do imóvel, de 1 a 5.",
        examples=[4],
    )
    grade: int = Field(
        ge=1,
        le=13,
        description="Código ordinal da qualidade de construção e projeto, de 1 a 13.",
        examples=[6],
    )
    sqft_above: int = Field(
        ge=0,
        description="Área habitável acima do nível do solo, em pés quadrados.",
        examples=[1680],
    )
    sqft_basement: int = Field(
        ge=0,
        description=(
            "Área do porão, em pés quadrados; 0 indica ausência de área de porão "
            "registrada."
        ),
        examples=[0],
    )
    yr_built: int = Field(
        ge=0,
        description="Ano de construção do imóvel.",
        examples=[1911],
    )
    yr_renovated: int = Field(
        ge=0,
        description="Ano da última reforma; 0 indica que não há reforma registrada.",
        examples=[0],
    )
    zipcode: str = Field(
        pattern=r"^\d{5}$",
        description=(
            "Código postal dos Estados Unidos com exatamente cinco dígitos; o "
            "formato válido não confirma cobertura do modelo."
        ),
        examples=["98118"],
    )
    lat: float = Field(
        ge=-90,
        le=90,
        description=(
            "Latitude da localização do imóvel, em graus decimais; o limite "
            "formal não confirma cobertura geográfica do modelo."
        ),
        examples=[47.5354],
    )
    long: float = Field(
        ge=-180,
        le=180,
        description=(
            "Longitude da localização do imóvel, em graus decimais; o limite "
            "formal não confirma cobertura geográfica do modelo."
        ),
        examples=[-122.273],
    )
    sqft_living15: int = Field(
        ge=0,
        description=(
            "Área habitável de referência da vizinhança, em pés quadrados; não é a "
            "área do imóvel consultado."
        ),
        examples=[1560],
    )
    sqft_lot15: int = Field(
        ge=0,
        description=(
            "Área de terreno de referência da vizinhança, em pés quadrados; não é a "
            "área do imóvel consultado."
        ),
        examples=[5765],
    )


class BatchPredictionRequest(BaseModel):
    """Ordered, all-or-nothing collection of properties for one inference request."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        PROPERTY_EXAMPLE,
                        SECOND_PROPERTY_EXAMPLE,
                    ]
                }
            ]
        },
    )

    items: list[PropertyFeatures] = Field(
        min_length=1,
        description=(
            "Lista ordenada com pelo menos um imóvel. Qualquer item inválido rejeita o "
            "lote inteiro antes da inferência. O limite máximo é definido por "
            "MAX_BATCH_SIZE, com padrão 100 e faixa operacional de 1 a 1000."
        ),
    )


class PredictionResponse(BaseModel):
    """Prediction returned for one property."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "predicted_price": 372953.43,
                    "currency": "USD",
                    "model_version": "0.4.0-rc1",
                    "request_id": "example-request-001",
                }
            ]
        }
    )

    predicted_price: float
    currency: Literal["USD"] = "USD"
    model_version: str
    request_id: str


class BatchPredictionItem(BaseModel):
    """One positional result in the same order as the batch input."""

    item_id: int = Field(
        description=(
            "Posição 1-based do item no lote de entrada; não é identificador único do "
            "imóvel e não deriva do zipcode."
        )
    )
    predicted_price: float = Field(description="Preço previsto para o item, em USD.")


class BatchPredictionResponse(BaseModel):
    """Ordered predictions and traceability metadata for one complete batch request."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "predictions": [
                        {"item_id": 1, "predicted_price": 372953.43},
                        {"item_id": 2, "predicted_price": 685890.91},
                    ],
                    "currency": "USD",
                    "model_version": "0.4.0-rc1",
                    "request_id": "example-request-002",
                }
            ]
        }
    )

    predictions: list[BatchPredictionItem] = Field(
        description="Resultados preservados na mesma ordem dos itens recebidos."
    )
    currency: Literal["USD"] = Field(
        default="USD",
        description="Moeda comum a todas as previsões do lote.",
    )
    model_version: str = Field(description="Versão do modelo usada para todo o lote.")
    request_id: str = Field(
        description=(
            "Identificador da requisição completa, também retornado no cabeçalho "
            "X-Request-ID; não identifica itens individualmente."
        )
    )


class HealthResponse(BaseModel):
    """Startup readiness information for the loaded API process."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "healthy",
                    "api_version": "0.5.0-rc1",
                    "model_version": "0.4.0-rc1",
                }
            ]
        }
    )

    status: str = Field(
        description=(
            "Indica que o processo concluiu o startup e mantém o bundle do modelo "
            "carregado após as verificações de inicialização."
        )
    )
    api_version: str = Field(
        min_length=1,
        description="Versão do contrato HTTP/OpenAPI exposto pela aplicação.",
    )
    model_version: str = Field(
        min_length=1,
        description="Versão do modelo carregado e atualmente servido pelo processo.",
    )


class ProjectIdentity(BaseModel):
    """Installed project package identity."""

    name: str = Field(
        min_length=1,
        description="Nome da distribuição instalada do projeto.",
    )
    release: str = Field(
        min_length=1,
        description="Release do projeto obtida do metadata do pacote instalado.",
    )


class ApiIdentity(BaseModel):
    """Public HTTP/OpenAPI contract identity."""

    version: str = Field(
        min_length=1,
        description="Versão do contrato HTTP/OpenAPI exposto pela aplicação.",
    )


class ModelServingIdentity(BaseModel):
    """Identity of the model approved and loaded for serving."""

    display_name: str = Field(
        min_length=1,
        description="Nome legível derivado do algoritmo e do conjunto de features.",
    )
    technical_name: str = Field(
        min_length=1,
        description="Nome técnico versionado no manifesto e no bundle do modelo.",
    )
    version: str = Field(
        min_length=1,
        description="Versão do modelo servido, distinta da release e da API.",
    )
    algorithm: str = Field(
        min_length=1,
        description="Algoritmo do modelo aprovado para serving.",
    )
    feature_set: str = Field(
        min_length=1,
        description="Conjunto de features usado pelo modelo servido.",
    )
    serving_status: Literal["approved"] = Field(
        default="approved",
        description=(
            "Decisão de governança para serving; não significa vencedor estatístico "
            "automático entre todas as variantes."
        ),
    )


class ArtifactIdentity(BaseModel):
    """Identity of the verified artifact and its manifest."""

    sha256: str = Field(
        pattern=r"^[a-f0-9]{64}$",
        description="SHA-256 do artefato verificado durante o startup.",
    )
    created_at_utc: datetime = Field(
        description="Data de criação registrada no manifesto, em UTC.",
    )
    schema_version: str = Field(
        min_length=1,
        description="Versão do schema do artefato e do manifesto.",
    )


class ModelInfoResponse(BaseModel):
    """Backward-compatible metadata plus structured technical identity blocks."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "property_value_hist_gradient_boosting_physical",
                    "model_version": "0.4.0-rc1",
                    "algorithm": "HistGradientBoostingRegressor",
                    "feature_set": "physical",
                    "feature_columns": ["bedrooms", "bathrooms", "sqft_living"],
                    "created_at_utc": "2026-08-03T23:24:44.139717+00:00",
                    "artifact_sha256": (
                        "90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439"
                    ),
                    "evaluation": {
                        "protocol": "five expanding temporal folds on the development period"
                    },
                    "limitations": [
                        "Os dados cobrem uma região e um intervalo temporal limitado."
                    ],
                    "project": {
                        "name": "property-value-insights",
                        "release": "1.0.0",
                    },
                    "api": {"version": "0.5.0-rc1"},
                    "model": {
                        "display_name": (
                            "HistGradientBoostingRegressor (physical feature set)"
                        ),
                        "technical_name": (
                            "property_value_hist_gradient_boosting_physical"
                        ),
                        "version": "0.4.0-rc1",
                        "algorithm": "HistGradientBoostingRegressor",
                        "feature_set": "physical",
                        "serving_status": "approved",
                    },
                    "artifact": {
                        "sha256": (
                            "90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439"
                        ),
                        "created_at_utc": "2026-08-03T23:24:44.139717+00:00",
                        "schema_version": "1.0",
                    },
                }
            ]
        }
    )

    name: str = Field(
        min_length=1,
        description="Nome técnico histórico do modelo, preservado por compatibilidade.",
    )
    model_version: str = Field(
        min_length=1,
        description="Versão histórica top-level do modelo servido.",
    )
    algorithm: str = Field(
        min_length=1,
        description="Algoritmo histórico top-level do modelo servido.",
    )
    feature_set: str = Field(
        min_length=1,
        description="Conjunto histórico top-level de features do modelo.",
    )
    feature_columns: list[str] = Field(
        min_length=1,
        description="Colunas de entrada esperadas pelo modelo servido.",
    )
    created_at_utc: datetime = Field(
        description="Data de criação histórica registrada no manifesto.",
    )
    artifact_sha256: str = Field(
        pattern=r"^[a-f0-9]{64}$",
        description="SHA-256 histórico top-level, preservado por compatibilidade.",
    )
    evaluation: dict[str, Any] = Field(
        min_length=1,
        description="Avaliação original do manifesto, preservada sem reformatação.",
    )
    limitations: list[str] = Field(
        min_length=1,
        description="Limitações originais do manifesto, preservadas sem reformatação.",
    )
    project: ProjectIdentity = Field(
        description="Identidade e release do projeto instalado.",
    )
    api: ApiIdentity = Field(
        description="Identidade versionada do contrato da API.",
    )
    model: ModelServingIdentity = Field(
        description="Identidade estruturada do modelo aprovado para serving.",
    )
    artifact: ArtifactIdentity = Field(
        description="Identidade estruturada do artefato e do manifesto verificados.",
    )


class InternalErrorResponse(BaseModel):
    detail: Literal["Internal server error"] = "Internal server error"
    request_id: str
