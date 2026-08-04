from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from property_value_insights.explainability import (
    DEFAULT_PERMUTATION_CYCLES,
    MAX_RELATIVE_ADDITIVITY_ERROR,
    evaluate_shap_explanations,
    write_shap_artifacts,
)
from property_value_insights.modeling import PHYSICAL_FEATURES

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_shap_artifacts_explain_verified_physical_model(tmp_path: Path) -> None:
    outputs = write_shap_artifacts(
        PROJECT_ROOT,
        tmp_path,
        background_size=10,
        explanation_size=4,
    )

    assert outputs["figure"].read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    global_importance = pd.read_csv(outputs["global_importance"])
    assert set(global_importance["feature"]) == set(PHYSICAL_FEATURES)
    assert global_importance["rank"].tolist() == list(range(1, 19))
    assert (global_importance["mean_permutation_std"] >= 0).all()
    local = pd.read_csv(outputs["local_explanations"])
    assert local["example"].nunique() == 3
    assert local.groupby("example")["row_id"].first().nunique() == 3
    assert len(local) == 3 * len(PHYSICAL_FEATURES)
    assert local["additivity_error"].max() < 1e-5
    metadata = json.loads(outputs["metadata"].read_text(encoding="utf-8"))
    assert metadata["explained_rows"] == 4
    assert metadata["background_rows"] == 10
    assert metadata["permutation_cycles"] == DEFAULT_PERMUTATION_CYCLES
    assert metadata["max_relative_additivity_error"] < MAX_RELATIVE_ADDITIVITY_ERROR
    assert len(metadata["model_identity"]["artifact_sha256"]) == 64


@pytest.mark.parametrize("explanation_size", [1, 2])
def test_shap_analysis_requires_three_distinct_local_examples(
    explanation_size: int,
) -> None:
    with pytest.raises(ValueError, match="at least three"):
        evaluate_shap_explanations(
            PROJECT_ROOT,
            background_size=10,
            explanation_size=explanation_size,
        )


def test_shap_analysis_rejects_non_positive_permutation_cycles() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        evaluate_shap_explanations(
            PROJECT_ROOT,
            background_size=10,
            explanation_size=3,
            permutation_cycles=0,
        )
