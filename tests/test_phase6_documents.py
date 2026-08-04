from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE6_DOCUMENTS = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "MODEL_CARD.md",
    PROJECT_ROOT / "docs" / "OPTIONAL_ANALYSIS_PROTOCOL.md",
    PROJECT_ROOT / "docs" / "reviews" / "phase-6.md",
    PROJECT_ROOT / "reports" / "optional_analysis.md",
)
LOCAL_LINK = re.compile(r"!?\[[^]]*\]\((?!https?://|mailto:|#)([^)]+)\)")


def _format_br_number(value: float) -> str:
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _format_br_integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


@pytest.mark.parametrize("document", PHASE6_DOCUMENTS, ids=lambda path: path.name)
def test_phase6_document_links_resolve(document: Path) -> None:
    content = document.read_text(encoding="utf-8")
    for destination in LOCAL_LINK.findall(content):
        path_text = unquote(destination.split("#", maxsplit=1)[0])
        assert (document.parent / path_text).resolve().exists(), (
            f"Broken local link in {document.name}: {destination}"
        )


def test_optional_report_matches_generated_uncertainty_results() -> None:
    report = (PROJECT_ROOT / "reports" / "optional_analysis.md").read_text(
        encoding="utf-8"
    )
    summary = json.loads(
        (PROJECT_ROOT / "reports" / "uncertainty_summary.json").read_text(
            encoding="utf-8"
        )
    )
    bands = pd.read_csv(PROJECT_ROOT / "reports" / "uncertainty_by_price_band.csv")

    assert _format_br_number(100 * summary["metrics"]["coverage"]) + "%" in report
    assert _format_br_number(summary["metrics"]["mean_width"]) in report
    for row in bands.itertuples(index=False):
        expected = (
            f"| {row.price_band} | {_format_br_integer(int(row.rows))} | "
            f"{_format_br_number(100 * row.coverage)}% | "
            f"US$ {_format_br_number(row.mean_width)} | "
            f"US$ {_format_br_number(row.median_width)} |"
        )
        assert expected in report


def test_optional_report_matches_generated_shap_results() -> None:
    report = (PROJECT_ROOT / "reports" / "optional_analysis.md").read_text(
        encoding="utf-8"
    )
    metadata = json.loads(
        (PROJECT_ROOT / "reports" / "shap_metadata.json").read_text(encoding="utf-8")
    )
    importance = pd.read_csv(PROJECT_ROOT / "reports" / "shap_global_importance.csv")

    assert metadata["explained_rows"] == 100
    assert metadata["background_rows"] == 50
    assert "elapsed_seconds" not in metadata
    assert metadata["model_identity"]["artifact_sha256"] in report
    labels = {
        "lat": "Latitude",
        "sqft_living": "Área habitável",
        "grade": "Padrão construtivo",
        "long": "Longitude",
        "sqft_lot": "Área do terreno",
        "yr_built": "Ano de construção",
    }
    for row in importance.head(6).itertuples(index=False):
        expected = (
            f"| {labels[row.feature]} | "
            f"US$ {_format_br_number(row.mean_absolute_shap)} |"
        )
        assert expected in report


def test_optional_dependencies_remain_outside_serving_runtime() -> None:
    configuration = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text("utf-8"))
    base_dependencies = configuration["project"]["dependencies"]
    explainability = configuration["project"]["optional-dependencies"]["explainability"]
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert not any(dependency.startswith("shap") for dependency in base_dependencies)
    assert any(dependency.startswith("shap==") for dependency in explainability)
    assert "uv sync --locked --no-dev --no-install-project" in dockerfile
    assert "uv sync --locked --no-dev --no-editable" in dockerfile
    assert "--extra explainability" not in dockerfile
    assert ".[explainability]" not in dockerfile


def test_phase6_figures_are_valid_png_files() -> None:
    figures = (
        PROJECT_ROOT / "reports" / "figures" / "uncertainty_diagnostic.png",
        PROJECT_ROOT / "reports" / "figures" / "shap_explanations.png",
    )
    for figure in figures:
        assert figure.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
