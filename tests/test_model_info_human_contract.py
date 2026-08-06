from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from property_value_insights.api import create_app
from property_value_insights.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "property_value_model.joblib"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "model_manifest.json"


def _settings() -> Settings:
    return Settings(
        artifact_path=ARTIFACT_PATH,
        manifest_path=MANIFEST_PATH,
    )


def test_model_info_human_blocks_are_derived_without_changing_technical_fields() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    diagnostic = manifest["evaluation"]["latest_period_diagnostic"]

    with TestClient(create_app(_settings())) as client:
        response = client.get("/model-info")

    assert response.status_code == 200
    body = response.json()

    assert body["evaluation"] == manifest["evaluation"]
    assert body["limitations"] == manifest["limitations"]
    assert body["artifact_sha256"] == manifest["artifact"]["sha256"]
    assert body["artifact"]["sha256"] == manifest["artifact"]["sha256"]

    performance = body["performance_summary"]
    assert performance["evaluation_scope"] == "latest_period_diagnostic"
    assert performance["currency"] == "USD"
    assert performance["mae_usd"] == diagnostic["mae"]
    assert performance["rmse_usd"] == diagnostic["rmse"]
    assert performance["mape_fraction"] == diagnostic["mape"]
    assert performance["mape_percent"] == pytest.approx(diagnostic["mape"] * 100)
    assert performance["r2"] == diagnostic["r2"]
    assert performance["underprediction_rate_fraction"] == diagnostic[
        "underprediction_rate"
    ]
    assert performance["underprediction_rate_percent"] == pytest.approx(
        diagnostic["underprediction_rate"] * 100
    )
    assert "mais da metade" in performance["underprediction_tendency"]
    assert performance["principal_known_risk"] in manifest["limitations"]

    evaluation_status = body["evaluation_status"]
    assert evaluation_status["technical_status"] == diagnostic["status"]
    assert evaluation_status["label"] == "Período diagnóstico previamente inspecionado"
    assert evaluation_status["is_untouched_test_set"] is False
    assert "não é um teste final intocado" in evaluation_status["explanation"]

    serving = body["serving_decision"]
    assert serving["status"] == "approved"
    assert serving["decision_basis"] == "governance"
    assert serving["feature_set"] == manifest["model"]["feature_set"]
    assert serving["selection_reason"] == manifest["model"]["selection_reason"]
    assert serving["is_statistical_winner_claim"] is False
    assert serving["human_review_recommended"] is True
    assert serving["human_review_contexts"] == [
        "usos consequenciais",
        "imóveis de alto valor",
    ]

    structured = body["structured_limitations"]
    assert [item["description"] for item in structured] == manifest["limitations"]
    assert [item["code"] for item in structured] == [
        "diagnostic_period_previously_inspected",
        "limited_spatiotemporal_coverage",
        "high_value_underprediction",
        "zipcode_contextual_disparity",
    ]
    high_value = next(item for item in structured if item["code"] == "high_value_underprediction")
    assert high_value["severity"] == "high"
    assert high_value["affected_scope"] == "high_value_properties"
    assert "revisão humana" in high_value["recommended_action"]
    assert "decisões consequenciais" in high_value["recommended_action"]


def test_model_info_openapi_documents_human_interpretation_and_formulas() -> None:
    app = create_app(_settings())
    spec = app.openapi()

    schema = spec["components"]["schemas"]["ModelInfoResponse"]
    properties = schema["properties"]
    assert {
        "performance_summary",
        "evaluation_status",
        "serving_decision",
        "structured_limitations",
    }.issubset(properties)

    performance_schema = spec["components"]["schemas"]["PerformanceSummary"]
    assert "USD" in performance_schema["properties"]["mae_usd"]["description"]
    assert "USD" in performance_schema["properties"]["rmse_usd"]["description"]
    assert "× 100" in performance_schema["properties"]["mape_percent"]["description"]
    assert "subestimação" in performance_schema["properties"][
        "underprediction_tendency"
    ]["description"]

    status_schema = spec["components"]["schemas"]["EvaluationStatus"]
    assert "diagnostic_only_previously_inspected" in status_schema["properties"][
        "is_untouched_test_set"
    ]["description"]

    serving_schema = spec["components"]["schemas"]["ServingDecision"]
    assert "model.selection_reason" in serving_schema["properties"]["selection_reason"][
        "description"
    ]
    assert "vencedor estatístico" in serving_schema["properties"][
        "is_statistical_winner_claim"
    ]["description"]
    assert "usos consequenciais" in serving_schema["properties"][
        "human_review_recommended"
    ]["description"]

    limitation_schema = spec["components"]["schemas"]["StructuredLimitation"]
    assert "Código estável" in limitation_schema["properties"]["code"]["description"]
    assert "Texto original" in limitation_schema["properties"]["description"][
        "description"
    ]
    assert "mitigação" in limitation_schema["properties"]["recommended_action"][
        "description"
    ]

    example = schema["examples"][0]
    assert example["performance_summary"]["mape_percent"] == pytest.approx(
        example["performance_summary"]["mape_fraction"] * 100
    )
    assert example["evaluation_status"]["is_untouched_test_set"] is False
    assert example["serving_decision"]["selection_reason"]
    assert example["structured_limitations"][0]["code"] == "high_value_underprediction"
