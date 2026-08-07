from __future__ import annotations

import json
from datetime import datetime
from importlib.metadata import metadata as package_metadata
from pathlib import Path

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


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_model_info_preserves_legacy_fields_and_adds_structured_identity() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    installed = package_metadata("property-value-insights")

    with TestClient(create_app(_settings())) as client:
        model_info_response = client.get("/model-info")
        health_response = client.get("/health")
        openapi_response = client.get("/openapi.json")

    assert model_info_response.status_code == 200
    body = model_info_response.json()
    health = health_response.json()
    openapi = openapi_response.json()

    legacy_fields = {
        "name",
        "model_version",
        "algorithm",
        "feature_set",
        "feature_columns",
        "created_at_utc",
        "artifact_sha256",
        "evaluation",
        "limitations",
    }
    assert legacy_fields.issubset(body)
    assert body["name"] == manifest["model"]["name"]
    assert body["model_version"] == manifest["model"]["version"]
    assert body["algorithm"] == manifest["model"]["algorithm"]
    assert body["feature_set"] == manifest["model"]["feature_set"]
    assert body["feature_columns"] == manifest["model"]["feature_columns"]
    assert _parse_utc(body["created_at_utc"]) == _parse_utc(manifest["created_at_utc"])
    assert body["artifact_sha256"] == manifest["artifact"]["sha256"]
    assert body["evaluation"] == manifest["evaluation"]
    assert body["limitations"] == manifest["limitations"]

    assert body["project"] == {
        "name": installed["Name"],
        "release": installed["Version"],
    }
    assert body["project"]["release"] == "1.0.1"
    assert body["api"]["version"] == health["api_version"]
    assert body["api"]["version"] == openapi["info"]["version"]

    assert body["model"] == {
        "display_name": "HistGradientBoostingRegressor (physical feature set)",
        "technical_name": manifest["model"]["name"],
        "version": manifest["model"]["version"],
        "algorithm": manifest["model"]["algorithm"],
        "feature_set": manifest["model"]["feature_set"],
        "serving_status": "approved",
    }
    assert body["model"]["version"] == body["model_version"]
    assert body["model"]["version"] == health["model_version"]
    assert "demographic" not in body["model"]["technical_name"]

    assert body["artifact"]["sha256"] == body["artifact_sha256"]
    assert _parse_utc(body["artifact"]["created_at_utc"]) == _parse_utc(
        manifest["created_at_utc"]
    )
    assert body["artifact"]["schema_version"] == manifest["schema_version"]
    assert "path" not in body["artifact"]


def test_model_info_openapi_documents_additive_identity_blocks() -> None:
    with TestClient(create_app(_settings())) as client:
        spec = client.get("/openapi.json").json()

    operation = spec["paths"]["/model-info"]["get"]
    assert operation["summary"] == "View project, API, model, and artifact identity"
    assert "campos históricos" in operation["description"]
    assert "modelo aprovado para serving" in operation["description"]

    schema = spec["components"]["schemas"]["ModelInfoResponse"]
    properties = schema["properties"]
    assert {"project", "api", "model", "artifact"}.issubset(properties)
    assert properties["project"]["description"] == (
        "Identidade e release do projeto instalado."
    )
    assert properties["api"]["description"] == "Identidade versionada do contrato da API."
    assert "aprovado para serving" in properties["model"]["description"]
    assert "artefato" in properties["artifact"]["description"]

    model_schema = spec["components"]["schemas"]["ModelServingIdentity"]
    assert "vencedor estatístico" in model_schema["properties"]["serving_status"][
        "description"
    ]
    artifact_schema = spec["components"]["schemas"]["ArtifactIdentity"]
    assert "SHA-256" in artifact_schema["properties"]["sha256"]["description"]
    assert "schema" in artifact_schema["properties"]["schema_version"]["description"]

    example = schema["examples"][0]
    assert example["project"]["release"] == "1.0.1"
    assert example["api"]["version"] == "0.5.0-rc1"
    assert example["model"]["version"] == "0.4.0-rc1"
    assert example["model"]["serving_status"] == "approved"
    assert example["artifact"]["sha256"] == example["artifact_sha256"]
