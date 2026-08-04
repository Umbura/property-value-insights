from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from property_value_insights.explainability import write_shap_artifacts
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
    local = pd.read_csv(outputs["local_explanations"])
    assert local["example"].nunique() == 3
    assert len(local) == 3 * len(PHYSICAL_FEATURES)
    assert local["additivity_error"].max() < 1e-5
    metadata = json.loads(outputs["metadata"].read_text(encoding="utf-8"))
    assert metadata["explained_rows"] == 4
    assert metadata["background_rows"] == 10
    assert metadata["max_additivity_error"] < 1e-5
    assert len(metadata["model_identity"]["artifact_sha256"]) == 64
