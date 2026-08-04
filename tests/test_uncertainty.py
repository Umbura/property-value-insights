from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from property_value_insights.uncertainty import (
    empirical_log_interval,
    finite_sample_quantile_level,
    write_uncertainty_artifacts,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_finite_sample_quantile_level_applies_upper_correction() -> None:
    assert finite_sample_quantile_level(100, 0.9) == 0.91
    assert finite_sample_quantile_level(9, 0.9) == 1.0


def test_empirical_log_interval_contains_its_center() -> None:
    predictions = np.array([100_000.0, 500_000.0])

    lower, upper = empirical_log_interval(predictions, 0.25)

    assert (lower < predictions).all()
    assert (upper > predictions).all()
    assert np.isfinite(lower).all()
    assert np.isfinite(upper).all()


def test_uncertainty_artifacts_preserve_temporal_diagnostic(tmp_path: Path) -> None:
    outputs = write_uncertainty_artifacts(PROJECT_ROOT, tmp_path)

    assert outputs["figure"].read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    summary = json.loads(outputs["summary"].read_text(encoding="utf-8"))
    assert summary["method"] == "empirical_temporal_log_residual_interval"
    assert summary["calibration"]["rows"] == 13_724
    assert summary["diagnostic_period"]["rows"] == 4_640
    assert summary["metrics"]["coverage"] == pytest.approx(0.893966, abs=1e-6)
    assert summary["metrics"]["mean_relative_width"] == pytest.approx(
        0.52938, abs=1e-6
    )
    bands = pd.read_csv(outputs["price_bands"])
    assert bands["price_band"].tolist() == ["Q1", "Q2", "Q3", "Q4"]
    assert int(bands["rows"].sum()) == 4_640
    assert bands.loc[bands["price_band"] == "Q4", "coverage"].iloc[0] < 0.9
    folds = pd.read_csv(outputs["calibration_folds"])
    assert folds["fold"].tolist() == [1, 2, 3, 4, 5]
    assert (pd.to_datetime(folds["train_end"]) < pd.to_datetime(folds["validation_start"])).all()
