from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

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

    assert "```mermaid" in architecture
    assert "```mermaid" in lifecycle
    assert "Implementada" in architecture and "Proposta" in architecture
    assert "property_value_hist_gradient_boosting_physical" in model_card
    assert "0.4.0-rc1" in model_card
    assert "70,22%" in stakeholder_summary
    assert (PROJECT_ROOT / "reports" / "figures" / "approved_model_diagnostic.png").exists()
