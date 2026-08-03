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
    select_calibrated_candidate,
    select_temporal_candidates,
    summarize_temporal_validation,
    temporal_train_test_split,
    vertical_equity_metrics,
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


def test_vertical_equity_metrics_are_calibrated_for_perfect_predictions() -> None:
    values = pd.Series([100.0, 200.0, 300.0])

    metrics = vertical_equity_metrics(values, values)

    assert metrics["mape"] == 0.0
    assert metrics["mean_error"] == 0.0
    assert metrics["underprediction_rate"] == 0.0
    assert metrics["median_prediction_ratio"] == 1.0
    assert metrics["price_related_differential"] == 1.0


def test_median_baseline_uses_only_the_training_partition() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)
    split = temporal_train_test_split(historical, test_size=0.2)

    predictions = median_baseline_prediction(split.train, split.test)
    results = cross_validate_median_baseline(split.train, n_splits=2)

    assert predictions.nunique() == 1
    assert len(results) == 2
    assert results["mae"].notna().all()
    assert (results["train_end"] < results["validation_start"]).all()


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
    assert results["high_price_mae"].notna().all()
    assert results["price_related_differential"].notna().all()
    assert (results["train_end"] < results["validation_start"]).all()


def test_temporal_smearing_pipeline_estimates_positive_factor() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)
    ordered = historical.sort_values("date").head(800).reset_index(drop=True)
    split = temporal_train_test_split(ordered, test_size=0.2)
    estimator = build_estimator(
        "ridge",
        "physical",
        target_transform="log_temporal_smearing",
        model_params={"calibration_fraction": 0.1},
    )

    evaluation = fit_and_evaluate(
        estimator,
        split.train,
        split.test,
        feature_set="physical",
    )

    assert evaluation.estimator.smearing_factor_ > 0
    assert np.isfinite(evaluation.predictions).all()


def test_temporal_cross_validation_keeps_complete_dates_in_each_partition() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)
    repeated_dates = historical.sort_values("date").head(1200).reset_index(drop=True)
    estimator = build_estimator("ridge", "physical")

    results = cross_validate_temporal(
        estimator,
        repeated_dates,
        feature_set="physical",
        n_splits=3,
    )

    assert (results["train_end"] < results["validation_start"]).all()
    assert (results["validation_start"] <= results["validation_end"]).all()


def test_temporal_summary_reports_mean_variation_and_worst_fold() -> None:
    results = {
        "candidate_a": pd.DataFrame(
            {
                "mae": [100.0, 110.0],
                "rmse": [120.0, 130.0],
                "rmsle": [0.10, 0.12],
            }
        ),
        "candidate_b": pd.DataFrame(
            {
                "mae": [105.0, 106.0],
                "rmse": [125.0, 126.0],
                "rmsle": [0.11, 0.11],
            }
        ),
    }

    summary = summarize_temporal_validation(results)

    candidate_a = summary.loc[summary["candidate"] == "candidate_a"].iloc[0]
    assert candidate_a["cv_mae_mean"] == 105.0
    assert candidate_a["cv_mae_std"] == 5.0
    assert candidate_a["cv_mae_worst"] == 110.0


def test_candidate_selection_prefers_stability_within_tolerance() -> None:
    summary = pd.DataFrame(
        [
            {
                "candidate": "best_mean",
                "cv_mae_mean": 100.0,
                "cv_mae_std": 8.0,
                "cv_mae_worst": 115.0,
            },
            {
                "candidate": "stable",
                "cv_mae_mean": 100.4,
                "cv_mae_std": 2.0,
                "cv_mae_worst": 104.0,
            },
            {
                "candidate": "outside_tolerance",
                "cv_mae_mean": 101.0,
                "cv_mae_std": 1.0,
                "cv_mae_worst": 102.0,
            },
        ]
    )

    selection = select_temporal_candidates(summary, relative_tolerance=0.005)

    assert selection.champion == "stable"
    assert selection.challenger == "best_mean"


def test_calibration_selection_requires_general_and_upper_tail_improvement() -> None:
    summary = pd.DataFrame(
        [
            {
                "candidate": "reference",
                "cv_mae_mean": 100.0,
                "cv_mae_worst": 105.0,
                "cv_high_price_mae_mean": 200.0,
                "cv_high_price_abs_mean_error_mean": 120.0,
                "cv_prd_deviation_mean": 0.04,
                "high_price_mae_improved_folds": 0,
            },
            {
                "candidate": "calibrated",
                "cv_mae_mean": 100.2,
                "cv_mae_worst": 104.0,
                "cv_high_price_mae_mean": 190.0,
                "cv_high_price_abs_mean_error_mean": 90.0,
                "cv_prd_deviation_mean": 0.02,
                "high_price_mae_improved_folds": 4,
            },
            {
                "candidate": "unstable_tail",
                "cv_mae_mean": 99.9,
                "cv_mae_worst": 103.0,
                "cv_high_price_mae_mean": 185.0,
                "cv_high_price_abs_mean_error_mean": 80.0,
                "cv_prd_deviation_mean": 0.01,
                "high_price_mae_improved_folds": 3,
            },
        ]
    )

    selection = select_calibrated_candidate(
        summary,
        reference_candidate="reference",
    )

    assert selection.promoted
    assert selection.champion == "calibrated"


def test_segment_metrics_reports_group_sizes() -> None:
    actual = pd.Series([100.0, 200.0, 300.0, 400.0])
    predicted = pd.Series([110.0, 190.0, 330.0, 360.0])
    segments = pd.Series(["low", "low", "high", "high"])

    results = segment_metrics(actual, predicted, segments)

    assert set(results["segment"]) == {"low", "high"}
    assert results["rows"].sum() == 4
