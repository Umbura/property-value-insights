from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from property_value_insights.api import create_app
from property_value_insights.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "property_value_model.joblib"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "model_manifest.json"
FUTURE_PATH = PROJECT_ROOT / "data" / "raw" / "future_unseen_examples.csv"


def _settings(*, max_batch_size: int) -> Settings:
    return Settings(
        artifact_path=ARTIFACT_PATH,
        manifest_path=MANIFEST_PATH,
        max_batch_size=max_batch_size,
    )


def _property_payloads() -> list[dict[str, object]]:
    frame = pd.read_csv(FUTURE_PATH, dtype={"zipcode": "string"})
    return frame.head(3).to_dict(orient="records")


def test_batch_openapi_documents_limit_policy_and_existing_error_formats() -> None:
    with TestClient(create_app(_settings(max_batch_size=2))) as client:
        spec = client.get("/openapi.json").json()

    operation = spec["paths"]["/predict/batch"]["post"]
    assert operation["summary"] == "Predict multiple property values"
    assert operation["description"] == (
        "Processa múltiplos imóveis em uma única requisição, preserva a ordem de "
        "entrada e aplica o limite máximo de itens por lote configurado no serviço."
    )

    responses = operation["responses"]
    assert "limite atual de 2 itens" in responses["413"]["description"]
    assert "padrão é 100" in responses["413"]["description"]
    assert "MAX_BATCH_SIZE" in responses["413"]["description"]
    assert responses["413"]["content"]["application/json"]["example"] == {
        "detail": "Batch exceeds the limit of 2 items"
    }
    assert "all-or-nothing" in responses["422"]["description"]
    assert responses["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/HTTPValidationError"
    }
    assert responses["500"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/InternalErrorResponse"
    }

    request_schema = spec["components"]["schemas"]["BatchPredictionRequest"]
    assert request_schema["properties"]["items"]["minItems"] == 1
    assert "qualquer item inválido rejeita o lote inteiro" in request_schema["properties"][
        "items"
    ]["description"].lower()
    assert "padrão 100" in request_schema["properties"]["items"]["description"]

    item_schema = spec["components"]["schemas"]["BatchPredictionItem"]
    assert "Posição 1-based" in item_schema["properties"]["item_id"]["description"]
    assert "não deriva do zipcode" in item_schema["properties"]["item_id"]["description"]

    response_schema = spec["components"]["schemas"]["BatchPredictionResponse"]
    assert "mesma ordem" in response_schema["properties"]["predictions"]["description"]
    assert "requisição completa" in response_schema["properties"]["request_id"][
        "description"
    ]


def test_batch_limit_order_traceability_and_single_consistency() -> None:
    payloads = _property_payloads()
    duplicate_items = [payloads[0], payloads[0]]

    with TestClient(create_app(_settings(max_batch_size=2))) as client:
        batch = client.post(
            "/predict/batch",
            json={"items": duplicate_items},
            headers={"X-Request-ID": "batch-limit-2"},
        )
        single = client.post("/predict", json=payloads[0])
        oversized = client.post(
            "/predict/batch",
            json={"items": payloads},
            headers={"X-Request-ID": "batch-too-large"},
        )
        empty = client.post("/predict/batch", json={"items": []})

    assert batch.status_code == 200
    assert batch.headers["X-Request-ID"] == "batch-limit-2"
    assert batch.json()["request_id"] == "batch-limit-2"
    assert [item["item_id"] for item in batch.json()["predictions"]] == [1, 2]
    assert len(batch.json()["predictions"]) == len(duplicate_items)
    assert batch.json()["predictions"][0]["predicted_price"] == pytest.approx(
        single.json()["predicted_price"]
    )
    assert batch.json()["predictions"][1]["predicted_price"] == pytest.approx(
        single.json()["predicted_price"]
    )

    assert oversized.status_code == 413
    assert oversized.headers["X-Request-ID"] == "batch-too-large"
    assert oversized.json() == {"detail": "Batch exceeds the limit of 2 items"}
    assert empty.status_code == 422


def test_batch_invalid_item_rejects_whole_request_before_inference() -> None:
    payloads = _property_payloads()
    invalid = dict(payloads[1])
    invalid["zipcode"] = "9811"

    with TestClient(create_app(_settings(max_batch_size=2))) as client:
        with patch("property_value_insights.api.predict_future") as predict_mock:
            response = client.post(
                "/predict/batch",
                json={"items": [payloads[0], invalid]},
                headers={"X-Request-ID": "invalid-batch"},
            )

    assert response.status_code == 422
    assert response.headers["X-Request-ID"] == "invalid-batch"
    predict_mock.assert_not_called()
