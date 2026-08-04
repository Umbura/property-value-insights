from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from property_value_insights.stakeholder_reporting import write_stakeholder_artifacts

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_stakeholder_artifacts_reproduce_approved_diagnostic(tmp_path: Path) -> None:
    outputs = write_stakeholder_artifacts(PROJECT_ROOT, tmp_path)

    assert outputs["figure"].read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    price_bands = pd.read_csv(outputs["price_bands"])
    assert price_bands["price_band"].tolist() == ["Q1", "Q2", "Q3", "Q4"]
    assert int(price_bands["rows"].sum()) == 4640
    assert price_bands["mae"].is_monotonic_increasing
    assert price_bands.iloc[-1]["mean_error"] < 0
    feature_importance = pd.read_csv(outputs["feature_importance"])
    assert feature_importance["feature"].head(4).tolist() == [
        "lat",
        "sqft_living",
        "grade",
        "long",
    ]
    assert (feature_importance["mae_increase"] > 0).all()
    metrics = json.loads(outputs["metrics"].read_text(encoding="utf-8"))
    assert metrics["period"]["status"] == "diagnostic_only_previously_inspected"
    assert metrics["model_identity"]["name"] == (
        "property_value_hist_gradient_boosting_physical"
    )
    assert metrics["model_identity"]["version"] == "0.4.0-rc1"
    assert len(metrics["model_identity"]["artifact_sha256"]) == 64
    assert metrics["model"]["mae"] == 67105.708262
    assert metrics["model"]["r2"] == 0.899781
    assert metrics["comparison"]["mae_reduction_pct"] > 70
