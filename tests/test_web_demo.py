from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from property_value_insights.config import Settings
from property_value_insights.cors_app import create_cors_app, parse_cors_origins

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "property_value_model.joblib"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "model_manifest.json"


def _settings() -> Settings:
    return Settings(
        artifact_path=ARTIFACT_PATH,
        manifest_path=MANIFEST_PATH,
        log_level="INFO",
        max_batch_size=100,
    )


def test_cors_origin_parser_is_explicit_and_deduplicated() -> None:
    assert parse_cors_origins(
        " https://umbura.github.io/, https://example.com, https://umbura.github.io "
    ) == ("https://umbura.github.io", "https://example.com")
    assert parse_cors_origins("") == ()


def test_pages_origin_can_call_prediction_api() -> None:
    app = create_cors_app(_settings(), origins=("https://umbura.github.io",))
    with TestClient(app) as client:
        response = client.options(
            "/predict",
            headers={
                "Origin": "https://umbura.github.io",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://umbura.github.io"
    assert "POST" in response.headers["access-control-allow-methods"]


def test_unlisted_browser_origin_is_rejected_by_preflight() -> None:
    app = create_cors_app(_settings(), origins=("https://umbura.github.io",))
    with TestClient(app) as client:
        response = client.options(
            "/predict",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_stakeholder_site_contains_all_required_prediction_features() -> None:
    app_js = (PROJECT_ROOT / "site" / "app.js").read_text(encoding="utf-8")
    required = {
        "bedrooms",
        "bathrooms",
        "sqft_living",
        "sqft_lot",
        "floors",
        "waterfront",
        "view",
        "condition",
        "grade",
        "sqft_above",
        "sqft_basement",
        "yr_built",
        "yr_renovated",
        "zipcode",
        "lat",
        "long",
        "sqft_living15",
        "sqft_lot15",
    }

    for field in required:
        assert f'name: "{field}"' in app_js

    index = (PROJECT_ROOT / "site" / "index.html").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "site" / "styles.css").read_text(encoding="utf-8")
    mobile = (PROJECT_ROOT / "site" / "mobile.css").read_text(encoding="utf-8")
    assert "Teste o modelo diretamente no navegador" in index
    assert 'id="prediction-form"' in index
    assert "assets/approved_model_diagnostic.png" in index
    assert "FastAPI · contrato 0.5.0-rc1" in index
    assert 'class="assembly-intro"' in index
    assert 'href="mobile.css"' in index
    assert "piece-lock" in styles
    assert "--bg: #050706" in styles
    assert "prefers-reduced-motion: reduce" in styles
    assert "@media (max-width: 580px)" in mobile
    assert "@media (max-width: 380px)" in mobile
    assert ".hero-actions .button" in mobile
    assert ".api-state" in mobile
    assert "setupRevealAnimations" in app_js


def test_deployment_configuration_keeps_api_url_externalized() -> None:
    config = (PROJECT_ROOT / "site" / "config.js").read_text(encoding="utf-8")
    pages = (PROJECT_ROOT / ".github" / "workflows" / "pages.yml").read_text(
        encoding="utf-8"
    )
    render = (PROJECT_ROOT / "render.yaml").read_text(encoding="utf-8")

    assert 'apiBaseUrl: ""' in config
    assert "vars.PVI_API_BASE_URL" in pages
    assert "property_value_insights.cors_app:app" in render
    assert "healthCheckPath: /health" in render
    assert 'key: PORT\n        value: "8000"' in render
    assert (
        "dockerCommand: uvicorn property_value_insights.cors_app:app "
        "--host 0.0.0.0 --port 8000"
    ) in render
    assert "/bin/sh -c" not in render
