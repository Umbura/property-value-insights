from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE5_DOCUMENTS = (
    PROJECT_ROOT / "diagrams" / "production_architecture.md",
    PROJECT_ROOT / "diagrams" / "model_lifecycle.md",
    PROJECT_ROOT / "docs" / "CONTINUOUS_LEARNING.md",
    PROJECT_ROOT / "docs" / "MODEL_CARD.md",
    PROJECT_ROOT / "docs" / "REFERENCES.md",
    PROJECT_ROOT / "docs" / "reviews" / "phase-5.md",
    PROJECT_ROOT / "reports" / "stakeholder_summary.md",
)
LOCAL_LINK = re.compile(r"!?\[[^]]*\]\((?!https?://|mailto:|#)([^)]+)\)")


@pytest.mark.parametrize("document", PHASE5_DOCUMENTS, ids=lambda path: path.name)
def test_phase5_document_links_resolve(document: Path) -> None:
    content = document.read_text(encoding="utf-8")
    destinations = LOCAL_LINK.findall(content)

    for destination in destinations:
        path_text = unquote(destination.split("#", maxsplit=1)[0])
        assert (document.parent / path_text).resolve().exists(), (
            f"Broken local link in {document.name}: {destination}"
        )


def test_phase5_diagrams_and_business_artifacts_are_present() -> None:
    architecture = (PROJECT_ROOT / "diagrams" / "production_architecture.md").read_text(
        encoding="utf-8"
    )
    lifecycle = (PROJECT_ROOT / "diagrams" / "model_lifecycle.md").read_text(
        encoding="utf-8"
    )
    model_card = (PROJECT_ROOT / "docs" / "MODEL_CARD.md").read_text(encoding="utf-8")
    stakeholder_summary = (
        PROJECT_ROOT / "reports" / "stakeholder_summary.md"
    ).read_text(encoding="utf-8")
    manifest = json.loads(
        (PROJECT_ROOT / "artifacts" / "model_manifest.json").read_text(encoding="utf-8")
    )
    stakeholder_metrics = json.loads(
        (PROJECT_ROOT / "reports" / "approved_model_stakeholder_metrics.json").read_text(
            encoding="utf-8"
        )
    )

    assert "```mermaid" in architecture
    assert "```mermaid" in lifecycle
    assert "Implementada" in architecture and "Proposta" in architecture
    assert manifest["model"]["name"] in model_card
    assert manifest["model"]["version"] in model_card
    reduction = stakeholder_metrics["comparison"]["mae_reduction_pct"]
    assert f"{reduction:.2f}%".replace(".", ",") in stakeholder_summary
    assert (PROJECT_ROOT / "reports" / "figures" / "approved_model_diagnostic.png").exists()


def _format_br_number(value: float) -> str:
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _format_br_integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def test_stakeholder_tables_match_generated_artifacts() -> None:
    summary = (PROJECT_ROOT / "reports" / "stakeholder_summary.md").read_text(
        encoding="utf-8"
    )
    price_bands = pd.read_csv(PROJECT_ROOT / "reports" / "approved_model_price_bands.csv")
    feature_importance = pd.read_csv(
        PROJECT_ROOT / "reports" / "approved_model_feature_importance.csv"
    )

    for row in price_bands.itertuples(index=False):
        signed_error = (
            f"-US$ {_format_br_number(abs(row.mean_error))}"
            if row.mean_error < 0
            else f"US$ {_format_br_number(row.mean_error)}"
        )
        expected = (
            f"| {row.price_band} | {_format_br_integer(int(row.rows))} | "
            f"US$ {_format_br_number(row.mae)} | "
            f"{signed_error} | {_format_br_number(100 * row.underprediction_rate)}% |"
        )
        assert expected in summary

    feature_labels = {
        "lat": "Latitude",
        "sqft_living": "Área habitável",
        "grade": "Padrão construtivo",
        "long": "Longitude",
        "sqft_lot": "Área do terreno",
        "yr_built": "Ano de construção",
        "zipcode": "CEP",
        "view": "Qualidade da vista",
    }
    for row in feature_importance.head(8).itertuples(index=False):
        expected = f"| {feature_labels[row.feature]} | US$ {_format_br_number(row.mae_increase)} |"
        assert expected in summary
