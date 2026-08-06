"""Human-readable model information derived from the verified serving manifest."""

from __future__ import annotations

from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .artifact import ArtifactIntegrityError
from .schemas import (
    ApiIdentity,
    ArtifactIdentity,
    ModelInfoResponse as LegacyModelInfoResponse,
    ModelServingIdentity,
    ProjectIdentity,
)

DIAGNOSTIC_STATUS = "diagnostic_only_previously_inspected"
HIGH_VALUE_RISK = (
    "Imóveis de maior valor mantêm erro absoluto e viés negativo mais elevados."
)

LIMITATION_INTERPRETATIONS: dict[str, tuple[str, str, str, str]] = {
    "O período temporal mais recente foi consultado e possui uso diagnóstico.": (
        "diagnostic_period_previously_inspected",
        "medium",
        "model_evaluation",
        "Não tratar o período como teste final intocado; validar em dados temporais futuros.",
    ),
    "Os dados de treinamento cobrem uma região e um intervalo temporal limitado.": (
        "limited_spatiotemporal_coverage",
        "high",
        "generalization",
        "Verificar cobertura geográfica e temporal e exigir revisão humana fora do domínio.",
    ),
    HIGH_VALUE_RISK: (
        "high_value_underprediction",
        "high",
        "high_value_properties",
        "Exigir revisão humana para imóveis de alto valor e decisões consequenciais.",
    ),
    "O CEP permanece como categoria geográfica e pode representar disparidades contextuais.": (
        "zipcode_contextual_disparity",
        "medium",
        "geographic_context",
        (
            "Monitorar resultados por CEP e não interpretar a variável como causa "
            "ou garantia de equidade."
        ),
    ),
}


class PerformanceSummary(BaseModel):
    """Human-readable metrics for the latest diagnostic period."""

    evaluation_scope: Literal["latest_period_diagnostic"] = Field(
        default="latest_period_diagnostic",
        description="Período do manifesto usado neste resumo humano.",
    )
    currency: Literal["USD"] = Field(
        default="USD", description="Moeda aplicável aos valores de MAE e RMSE."
    )
    mae_usd: float = Field(
        ge=0, description="Erro absoluto médio diagnóstico, em USD, sem novo arredondamento."
    )
    rmse_usd: float = Field(
        ge=0, description="Raiz do erro quadrático médio diagnóstico, em USD."
    )
    mape_fraction: float = Field(
        ge=0, description="MAPE técnico original do manifesto, armazenado como fração."
    )
    mape_percent: float = Field(
        ge=0, description="MAPE em percentual, calculado como mape_fraction × 100."
    )
    r2: float = Field(description="Coeficiente R² do período diagnóstico.")
    underprediction_rate_fraction: float = Field(
        ge=0, le=1, description="Taxa técnica de subestimação armazenada como fração."
    )
    underprediction_rate_percent: float = Field(
        ge=0, le=100, description="Taxa de subestimação em percentual."
    )
    underprediction_tendency: str = Field(
        min_length=1, description="Interpretação textual da tendência de subestimação."
    )
    principal_known_risk: str = Field(
        min_length=1, description="Principal risco conhecido copiado das limitações originais."
    )


class EvaluationStatus(BaseModel):
    """Human interpretation of the diagnostic evaluation status."""

    technical_status: str = Field(
        min_length=1, description="Status técnico original registrado no manifesto."
    )
    label: str = Field(min_length=1, description="Rótulo humano do status diagnóstico.")
    explanation: str = Field(
        min_length=1, description="Explica por que o período não é um teste final intocado."
    )
    is_untouched_test_set: Literal[False] = Field(
        default=False,
        description="Sempre falso para diagnostic_only_previously_inspected.",
    )


class ServingDecision(BaseModel):
    """Governance decision that approved the physical model for serving."""

    status: Literal["approved"] = Field(
        default="approved", description="Status da decisão de serving."
    )
    decision_basis: Literal["governance"] = Field(
        default="governance", description="Indica decisão de governança."
    )
    feature_set: str = Field(min_length=1, description="Feature set do modelo aprovado.")
    selection_reason: str = Field(
        min_length=1,
        description="Justificativa copiada fielmente de model.selection_reason no manifesto.",
    )
    is_statistical_winner_claim: Literal[False] = Field(
        default=False,
        description="A aprovação não afirma vencedor estatístico automático.",
    )
    human_review_recommended: Literal[True] = Field(
        default=True,
        description="Recomenda revisão humana para usos consequenciais e imóveis de alto valor.",
    )
    human_review_contexts: list[str] = Field(
        min_length=2, description="Contextos em que a revisão humana é recomendada."
    )


class StructuredLimitation(BaseModel):
    """Stable interpretation metadata for one original manifest limitation."""

    code: str = Field(
        pattern=r"^[a-z0-9_]+$", description="Código estável e legível da limitação."
    )
    severity: Literal["medium", "high"] = Field(
        description="Severidade operacional da limitação."
    )
    affected_scope: str = Field(min_length=1, description="Escopo principalmente afetado.")
    description: str = Field(
        min_length=1, description="Texto original da limitação, preservado sem reescrita."
    )
    recommended_action: str = Field(
        min_length=1, description="Ação de mitigação recomendada para uso responsável."
    )


EXAMPLE = {
    "name": "property_value_hist_gradient_boosting_physical",
    "model_version": "0.4.0-rc1",
    "algorithm": "HistGradientBoostingRegressor",
    "feature_set": "physical",
    "feature_columns": ["bedrooms", "bathrooms", "sqft_living"],
    "created_at_utc": "2026-08-03T23:24:44.139717+00:00",
    "artifact_sha256": "90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439",
    "evaluation": {"latest_period_diagnostic": {"mape": 0.120651}},
    "limitations": [HIGH_VALUE_RISK],
    "project": {"name": "property-value-insights", "release": "1.0.0"},
    "api": {"version": "0.5.0-rc1"},
    "model": {
        "display_name": "HistGradientBoostingRegressor (physical feature set)",
        "technical_name": "property_value_hist_gradient_boosting_physical",
        "version": "0.4.0-rc1",
        "algorithm": "HistGradientBoostingRegressor",
        "feature_set": "physical",
        "serving_status": "approved",
    },
    "artifact": {
        "sha256": "90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439",
        "created_at_utc": "2026-08-03T23:24:44.139717+00:00",
        "schema_version": "1.0",
    },
    "performance_summary": {
        "evaluation_scope": "latest_period_diagnostic",
        "currency": "USD",
        "mae_usd": 67105.708262,
        "rmse_usd": 116547.248993,
        "mape_fraction": 0.120651,
        "mape_percent": 12.0651,
        "r2": 0.899781,
        "underprediction_rate_fraction": 0.587716,
        "underprediction_rate_percent": 58.7716,
        "underprediction_tendency": "A subestimação ocorreu em mais da metade das observações.",
        "principal_known_risk": HIGH_VALUE_RISK,
    },
    "evaluation_status": {
        "technical_status": DIAGNOSTIC_STATUS,
        "label": "Período diagnóstico previamente inspecionado",
        "explanation": "O período já foi consultado e não é um teste final intocado.",
        "is_untouched_test_set": False,
    },
    "serving_decision": {
        "status": "approved",
        "decision_basis": "governance",
        "feature_set": "physical",
        "selection_reason": "Modelo físico aprovado após avaliação de governança.",
        "is_statistical_winner_claim": False,
        "human_review_recommended": True,
        "human_review_contexts": ["usos consequenciais", "imóveis de alto valor"],
    },
    "structured_limitations": [
        {
            "code": "high_value_underprediction",
            "severity": "high",
            "affected_scope": "high_value_properties",
            "description": HIGH_VALUE_RISK,
            "recommended_action": "Exigir revisão humana para imóveis de alto valor.",
        }
    ],
}


class ModelInfoResponse(LegacyModelInfoResponse):
    """Technical metadata plus additive human-readable interpretation blocks."""

    model_config = ConfigDict(json_schema_extra={"examples": [EXAMPLE]})

    performance_summary: PerformanceSummary = Field(
        description="Resumo humano das métricas do período diagnóstico mais recente."
    )
    evaluation_status: EvaluationStatus = Field(
        description="Interpretação humana do status técnico da avaliação diagnóstica."
    )
    serving_decision: ServingDecision = Field(
        description="Decisão de governança que aprovou o modelo físico para serving."
    )
    structured_limitations: list[StructuredLimitation] = Field(
        min_length=1,
        description="Limitações originais enriquecidas com códigos e ações estáveis.",
    )


def _number(mapping: Mapping[str, Any], key: str) -> float:
    value = mapping[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{key} must be numeric")
    return float(value)


def _tendency(rate: float) -> str:
    if rate > 0.5:
        return "A subestimação ocorreu em mais da metade das observações do período diagnóstico."
    if rate < 0.5:
        return "A subestimação ocorreu em menos da metade das observações do período diagnóstico."
    return "A subestimação ocorreu em metade das observações do período diagnóstico."


def _structured(limitations: list[str]) -> list[StructuredLimitation]:
    result = []
    for description in limitations:
        interpretation = LIMITATION_INTERPRETATIONS.get(description)
        if interpretation is None:
            raise ValueError("Manifest limitation has no governed structured interpretation")
        code, severity, scope, action = interpretation
        result.append(
            StructuredLimitation(
                code=code,
                severity=severity,
                affected_scope=scope,
                description=description,
                recommended_action=action,
            )
        )
    return result


def build_model_info(
    manifest: Mapping[str, Any],
    *,
    project: ProjectIdentity,
    api_version: str,
) -> ModelInfoResponse:
    """Build public model information from validated manifest data."""

    try:
        model = manifest["model"]
        artifact = manifest["artifact"]
        evaluation = manifest["evaluation"]
        diagnostic = evaluation["latest_period_diagnostic"]
        limitations = manifest["limitations"]
        sections = (model, artifact, evaluation, diagnostic)
        if not all(isinstance(value, Mapping) for value in sections):
            raise TypeError("manifest sections must be mappings")
        if not isinstance(limitations, list) or not all(
            isinstance(item, str) and item for item in limitations
        ):
            raise TypeError("limitations must be non-empty strings")
        if HIGH_VALUE_RISK not in limitations:
            raise ValueError("high-value risk limitation is missing")
        status = diagnostic["status"]
        if status != DIAGNOSTIC_STATUS:
            raise ValueError("unsupported diagnostic evaluation status")
        selection_reason = model["selection_reason"]
        if not isinstance(selection_reason, str) or not selection_reason:
            raise TypeError("selection_reason must be a non-empty string")

        mae = _number(diagnostic, "mae")
        rmse = _number(diagnostic, "rmse")
        mape = _number(diagnostic, "mape")
        r2 = _number(diagnostic, "r2")
        underprediction = _number(diagnostic, "underprediction_rate")

        return ModelInfoResponse(
            name=model["name"],
            model_version=model["version"],
            algorithm=model["algorithm"],
            feature_set=model["feature_set"],
            feature_columns=model["feature_columns"],
            created_at_utc=manifest["created_at_utc"],
            artifact_sha256=artifact["sha256"],
            evaluation=evaluation,
            limitations=limitations,
            project=project,
            api=ApiIdentity(version=api_version),
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
            performance_summary=PerformanceSummary(
                mae_usd=mae,
                rmse_usd=rmse,
                mape_fraction=mape,
                mape_percent=mape * 100.0,
                r2=r2,
                underprediction_rate_fraction=underprediction,
                underprediction_rate_percent=underprediction * 100.0,
                underprediction_tendency=_tendency(underprediction),
                principal_known_risk=HIGH_VALUE_RISK,
            ),
            evaluation_status=EvaluationStatus(
                technical_status=status,
                label="Período diagnóstico previamente inspecionado",
                explanation=(
                    "O período temporal mais recente foi usado para diagnóstico e já foi "
                    "consultado; não é um teste final intocado."
                ),
                is_untouched_test_set=False,
            ),
            serving_decision=ServingDecision(
                feature_set=model["feature_set"],
                selection_reason=selection_reason,
                human_review_contexts=["usos consequenciais", "imóveis de alto valor"],
            ),
            structured_limitations=_structured(limitations),
        )
    except (KeyError, TypeError, ValueError, ValidationError) as error:
        raise ArtifactIntegrityError(
            "Model manifest contains invalid human-readable serving metadata"
        ) from error


__all__ = [
    "EvaluationStatus",
    "ModelInfoResponse",
    "PerformanceSummary",
    "ServingDecision",
    "StructuredLimitation",
    "build_model_info",
]
