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
    metrics = json.loads(outputs["metrics"].read_text(encoding="utf-8"))
    assert metrics["period"]["status"] == "diagnostic_only_previously_inspected"
    assert metrics["model"]["mae"] == 67105.708262
    assert metrics["model"]["r2"] == 0.899781
    assert metrics["comparison"]["mae_reduction_pct"] > 70
