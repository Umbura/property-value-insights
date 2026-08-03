from pathlib import Path

import numpy as np
import pandas as pd

from property_value_insights.data_contract import load_raw_data
from property_value_insights.eda import merge_historical_with_demographics
from property_value_insights.modeling import (
    build_estimator,
    cross_validate_median_baseline,
    cross_validate_temporal,
    fit_and_evaluate,
    median_baseline_prediction,
    regression_metrics,
    segment_metrics,
    temporal_train_test_split,
)

DATA_DIR = Path(__file__).parents[1] / "data" / "raw"


def test_temporal_split_keeps_test_dates_after_training_dates() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)

    split = temporal_train_test_split(historical, test_size=0.2)

    assert split.train_end < split.test_start
    assert split.train["date"].max() < split.test["date"].min()
    assert len(split.train) + len(split.test) == len(historical)


def test_temporal_split_accepts_enriched_historical_frame() -> None:
    historical, demographics, _ = load_raw_data(DATA_DIR)
    merged, _ = merge_historical_with_demographics(historical, demographics)

    split = temporal_train_test_split(merged, test_size=0.2)

    assert "medn_hshld_incm_amt" in split.train.columns
    assert split.train_end < split.test_start


def test_regression_metrics_are_zero_for_perfect_predictions() -> None:
    values = pd.Series([100.0, 200.0, 300.0])

    metrics = regression_metrics(values, values)

    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
    assert metrics["rmsle"] == 0.0
    assert metrics["r2"] == 1.0


def test_median_baseline_uses_only_the_training_partition() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)
    split = temporal_train_test_split(historical, test_size=0.2)

    predictions = median_baseline_prediction(split.train, split.test)
    results = cross_validate_median_baseline(split.train, n_splits=2)

    assert predictions.nunique() == 1
    assert len(results) == 2
    assert results["mae"].notna().all()


def test_ridge_pipeline_fits_without_using_identifier_or_target() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)
    split = temporal_train_test_split(historical, test_size=0.2)
    estimator = build_estimator("ridge", "physical")

    evaluation = fit_and_evaluate(
        estimator,
        split.train.head(500),
        split.test.head(100),
        feature_set="physical",
    )

    assert len(evaluation.predictions) == 100
    assert np.isfinite(evaluation.predictions).all()
    assert evaluation.metrics["mae"] >= 0


def test_temporal_cross_validation_returns_one_row_per_fold() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)
    ordered = historical.sort_values("date").head(600).reset_index(drop=True)
    estimator = build_estimator("ridge", "physical")

    results = cross_validate_temporal(
        estimator,
        ordered,
        feature_set="physical",
        n_splits=2,
    )

    assert len(results) == 2
    assert results["mae"].notna().all()


def test_segment_metrics_reports_group_sizes() -> None:
    actual = pd.Series([100.0, 200.0, 300.0, 400.0])
    predicted = pd.Series([110.0, 190.0, 330.0, 360.0])
    segments = pd.Series(["low", "low", "high", "high"])

    results = segment_metrics(actual, predicted, segments)

    assert set(results["segment"]) == {"low", "high"}
    assert results["rows"].sum() == 4
