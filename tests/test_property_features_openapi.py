from __future__ import annotations

import csv
from pathlib import Path

from fastapi.testclient import TestClient

from property_value_insights.api import create_app
from property_value_insights.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "property_value_model.joblib"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "model_manifest.json"
FUTURE_PATH = PROJECT_ROOT / "data" / "raw" / "future_unseen_examples.csv"

INTEGER_FIELDS = {
    "bedrooms",
    "sqft_living",
    "sqft_lot",
    "waterfront",
    "view",
    "condition",
    "grade",
    "sqft_above",
    "sqft_basement",
    "yr_built",
    "yr_renovated",
    "sqft_living15",
    "sqft_lot15",
}
FLOAT_FIELDS = {"bathrooms", "floors", "lat", "long"}


def _settings() -> Settings:
    return Settings(
        artifact_path=ARTIFACT_PATH,
        manifest_path=MANIFEST_PATH,
        log_level="INFO",
        max_batch_size=100,
    )


def _versioned_property_example() -> dict[str, object]:
    with FUTURE_PATH.open(encoding="utf-8", newline="") as source:
        row = next(csv.DictReader(source))

    return {
        name: int(value)
        if name in INTEGER_FIELDS
        else float(value)
        if name in FLOAT_FIELDS
        else value
        for name, value in row.items()
    }


def test_property_features_openapi_documents_all_fields_and_valid_examples() -> None:
    expected_example = _versioned_property_example()

    with TestClient(create_app(_settings())) as client:
        openapi_response = client.get("/openapi.json")
        prediction_response = client.post("/predict", json=expected_example)

    assert openapi_response.status_code == 200
    spec = openapi_response.json()
    property_schema = spec["components"]["schemas"]["PropertyFeatures"]
    properties = property_schema["properties"]

    assert set(properties) == set(expected_example)
    assert len(properties) == 18
    assert property_schema["examples"] == [expected_example]
    for field_name, example_value in expected_example.items():
        assert properties[field_name]["description"]
        assert properties[field_name]["examples"] == [example_value]

    batch_schema = spec["components"]["schemas"]["BatchPredictionRequest"]
    assert batch_schema["examples"][0]["items"][0] == expected_example

    assert prediction_response.status_code == 200
