from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from property_value_insights.api import create_app
from property_value_insights.artifact import ArtifactIntegrityError
from property_value_insights.config import Settings
from property_value_insights.observability import JsonFormatter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "property_value_model.joblib"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "model_manifest.json"
FUTURE_PATH = PROJECT_ROOT / "data" / "raw" / "future_unseen_examples.csv"
PREDICTIONS_PATH = PROJECT_ROOT / "reports" / "future_predictions.csv"


def _settings(**overrides: object) -> Settings:
    values = {
        "artifact_path": ARTIFACT_PATH,
        "manifest_path": MANIFEST_PATH,
        "log_level": "INFO",
        "max_batch_size": 100,
    }
    values.update(overrides)
    return Settings(**values)


@pytest.fixture(scope="module")
def property_payloads() -> list[dict[str, object]]:
    frame = pd.read_csv(FUTURE_PATH, dtype={"zipcode": "string"})
    return frame.head(8).to_dict(orient="records")


def test_health_and_model_info_expose_loaded_model_metadata() -> None:
    with TestClient(create_app(_settings())) as client:
        health = client.get("/health", headers={"X-Request-ID": "health-check-1"})
        model_info = client.get("/model-info")
        openapi = client.get("/openapi.json")

    assert health.status_code == 200
    assert health.headers["X-Request-ID"] == "health-check-1"
    assert health.json() == {
        "status": "healthy",
        "api_version": "0.5.0-rc1",
        "model_version": "0.4.0-rc1",
    }
    assert model_info.status_code == 200
    assert model_info.json()["model_version"] == "0.4.0-rc1"
    assert model_info.json()["feature_set"] == "physical"
    assert model_info.json()["algorithm"] == "HistGradientBoostingRegressor"
    assert len(model_info.json()["feature_columns"]) == 18
    assert openapi.json()["info"]["version"] == "0.5.0-rc1"
    assert openapi.json()["info"]["version"] != model_info.json()["model_version"]


def test_single_prediction_matches_the_versioned_batch_output(
    property_payloads: list[dict[str, object]],
) -> None:
    expected = pd.read_csv(PREDICTIONS_PATH).iloc[0]
    with TestClient(create_app(_settings())) as client:
        response = client.post("/predict", json=property_payloads[0])

    assert response.status_code == 200
    assert response.json()["currency"] == "USD"
    assert response.json()["model_version"] == expected["model_version"]
    assert response.json()["predicted_price"] == pytest.approx(expected["predicted_price"])
    assert response.headers["X-Request-ID"] == response.json()["request_id"]


def test_batch_prediction_preserves_input_order(
    property_payloads: list[dict[str, object]],
) -> None:
    expected = pd.read_csv(PREDICTIONS_PATH).head(3)
    with TestClient(create_app(_settings())) as client:
        response = client.post("/predict/batch", json={"items": property_payloads[:3]})

    assert response.status_code == 200
    assert response.json()["currency"] == "USD"
    assert [item["item_id"] for item in response.json()["predictions"]] == [1, 2, 3]
    assert [item["predicted_price"] for item in response.json()["predictions"]] == pytest.approx(
        expected["predicted_price"].tolist()
    )


def test_invalid_payload_and_oversized_batch_are_rejected(
    property_payloads: list[dict[str, object]],
) -> None:
    invalid = dict(property_payloads[0])
    invalid["zipcode"] = "9811"
    invalid["unknown_feature"] = 1
    incorrect_type = dict(property_payloads[0])
    incorrect_type["bedrooms"] = "4"

    with TestClient(create_app(_settings(max_batch_size=1))) as client:
        invalid_response = client.post("/predict", json=invalid)
        incorrect_type_response = client.post("/predict", json=incorrect_type)
        oversized_response = client.post(
            "/predict/batch",
            json={"items": property_payloads[:2]},
        )

    assert invalid_response.status_code == 422
    assert incorrect_type_response.status_code == 422
    assert oversized_response.status_code == 413
    assert oversized_response.json()["detail"] == "Batch exceeds the limit of 1 items"


def test_metrics_report_requests_and_predictions(
    property_payloads: list[dict[str, object]],
) -> None:
    with TestClient(create_app(_settings())) as client:
        client.post("/predict", json=property_payloads[0])
        response = client.get("/metrics")

    assert response.status_code == 200
    assert "pvi_http_requests_total" in response.text
    assert 'pvi_predictions_total{mode="single"} 1.0' in response.text
    assert "pvi_http_request_duration_seconds" in response.text


def test_invalid_artifact_prevents_service_startup(tmp_path: Path) -> None:
    invalid_artifact = tmp_path / "model.joblib"
    invalid_artifact.write_bytes(b"not-a-model")

    with pytest.raises(ArtifactIntegrityError, match="hash does not match"):
        with TestClient(create_app(_settings(artifact_path=invalid_artifact))):
            pass


def test_incomplete_serving_manifest_prevents_service_startup(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest.pop("evaluation")
    incomplete_manifest = tmp_path / "model_manifest.json"
    incomplete_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ArtifactIntegrityError, match="serving metadata"):
        with TestClient(create_app(_settings(manifest_path=incomplete_manifest))):
            pass


def test_unexpected_failure_returns_correlated_structured_error(
    property_payloads: list[dict[str, object]],
) -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("property_value_insights.api")
    logger.addHandler(handler)
    try:
        with TestClient(create_app(_settings()), raise_server_exceptions=False) as client:
            with patch(
                "property_value_insights.api.predict_future",
                side_effect=RuntimeError("forced failure"),
            ):
                response = client.post(
                    "/predict",
                    json=property_payloads[0],
                    headers={"X-Request-ID": "failed-request"},
                )
            metrics = client.get("/metrics").text
    finally:
        logger.removeHandler(handler)

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "failed-request"
    assert response.json() == {
        "detail": "Internal server error",
        "request_id": "failed-request",
    }
    assert 'pvi_request_failures_total{exception_type="RuntimeError"} 1.0' in metrics
    records = [json.loads(line) for line in stream.getvalue().splitlines() if line]
    error_record = next(record for record in records if record["message"] == "request_failed")
    assert error_record["level"] == "ERROR"
    assert error_record["request_id"] == "failed-request"
    assert "RuntimeError: forced failure" in error_record["exception"]


def test_concurrent_requests_return_stable_predictions(
    property_payloads: list[dict[str, object]],
) -> None:
    with TestClient(create_app(_settings())) as client:

        def predict_once(index: int) -> tuple[int, str]:
            response = client.post("/predict", json=property_payloads[index % 4])
            return response.status_code, response.json()["model_version"]

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(predict_once, range(8)))

    assert results == [(200, "0.4.0-rc1")] * 8


def test_logs_are_structured_and_do_not_include_request_payload(
    property_payloads: list[dict[str, object]],
) -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("property_value_insights.api")
    logger.addHandler(handler)
    try:
        with TestClient(create_app(_settings())) as client:
            response = client.post("/predict", json=property_payloads[0])
    finally:
        logger.removeHandler(handler)

    records = [json.loads(line) for line in stream.getvalue().splitlines() if line]
    request_record = next(record for record in records if record["message"] == "request_completed")
    assert request_record["request_id"] == response.json()["request_id"]
    assert request_record["path"] == "/predict"
    assert "zipcode" not in request_record
