"""Reusable temporal modeling and evaluation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from time import perf_counter
from typing import Literal, Mapping

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
    median_absolute_error,
    r2_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted

from .data_contract import DEMOGRAPHICS_COLUMNS, HISTORICAL_COLUMNS, validate_historical_frame

FeatureSet = Literal["physical", "with_demographics"]
TargetTransform = Literal["raw", "log", "log_smearing", "log_temporal_smearing"]
ModelLoss = Literal["squared_error", "absolute_error", "gamma", "poisson", "quantile"]

PHYSICAL_FEATURES = (
    "bedrooms",
    "bathrooms",
    "sqft_living",
    "sqft_lot",
    "floors",
    "waterfront",
    "view",
    "condition",
    "grade",
    "sqft_above",
    "sqft_basement",
    "yr_built",
    "yr_renovated",
    "zipcode",
    "lat",
    "long",
    "sqft_living15",
    "sqft_lot15",
)

DEMOGRAPHIC_FEATURES = tuple(sorted(DEMOGRAPHICS_COLUMNS - {"zipcode"}))
FEATURE_SETS: dict[FeatureSet, tuple[str, ...]] = {
    "physical": PHYSICAL_FEATURES,
    "with_demographics": PHYSICAL_FEATURES + DEMOGRAPHIC_FEATURES,
}


@dataclass(frozen=True)
class TemporalSplit:
    """Chronological train and test partitions with a date boundary."""

    train: pd.DataFrame
    test: pd.DataFrame
    train_end: pd.Timestamp
    test_start: pd.Timestamp


@dataclass(frozen=True)
class FittedEvaluation:
    """A fitted estimator, holdout predictions and measured metrics."""

    estimator: RegressorMixin
    predictions: pd.Series
    metrics: dict[str, float]
    fit_seconds: float


@dataclass(frozen=True)
class CandidateSelection:
    """Champion and challenger selected from temporal validation results."""

    champion: str
    challenger: str
    relative_tolerance: float


@dataclass(frozen=True)
class CalibrationSelection:
    """Result of the calibration promotion gate."""

    champion: str
    reference: str
    relative_tolerance: float
    minimum_improved_folds: int
    promoted: bool


class SmearingRegressor(RegressorMixin, BaseEstimator):
    """Fit a regressor on log1p(y) and correct predictions after retransformation.

    When ``calibration_fraction`` is set, the factor is estimated on the final
    fraction of the chronologically ordered training rows. The base regressor is
    then refitted on the complete training partition.
    """

    def __init__(
        self,
        regressor: RegressorMixin,
        *,
        calibration_fraction: float | None = None,
    ) -> None:
        self.regressor = regressor
        self.calibration_fraction = calibration_fraction

    def fit(self, X: object, y: object) -> SmearingRegressor:
        """Fit the log-scale model and estimate the smearing factor."""

        target = np.asarray(y, dtype=float)
        if target.ndim != 1:
            target = target.reshape(-1)
        if len(target) < 3:
            raise ValueError("Smearing calibration requires at least three rows")
        if not np.isfinite(target).all() or (target <= 0).any():
            raise ValueError("Smearing calibration requires finite positive targets")

        transformed = np.log1p(target)
        if self.calibration_fraction is None:
            self.regressor_ = clone(self.regressor).fit(X, transformed)
            calibration_prediction = self.regressor_.predict(X)
            calibration_target = transformed
        else:
            if not 0 < self.calibration_fraction < 0.5:
                raise ValueError("calibration_fraction must be between 0 and 0.5")
            calibration_rows = max(1, ceil(len(target) * self.calibration_fraction))
            split_at = len(target) - calibration_rows
            if split_at < 2:
                raise ValueError("Calibration split must leave at least two training rows")

            calibration_regressor = clone(self.regressor).fit(
                _row_slice(X, 0, split_at),
                transformed[:split_at],
            )
            calibration_prediction = calibration_regressor.predict(
                _row_slice(X, split_at, len(target))
            )
            calibration_target = transformed[split_at:]
            self.regressor_ = clone(self.regressor).fit(X, transformed)

        log_residuals = calibration_target - np.asarray(calibration_prediction, dtype=float)
        self.smearing_factor_ = float(np.mean(np.exp(log_residuals)))
        if not np.isfinite(self.smearing_factor_) or self.smearing_factor_ <= 0:
            raise ValueError("Smearing calibration produced an invalid factor")
        return self

    def predict(self, X: object) -> np.ndarray:
        """Predict on the original target scale."""

        check_is_fitted(self, attributes=["regressor_", "smearing_factor_"])
        log_prediction = np.asarray(self.regressor_.predict(X), dtype=float)
        return np.exp(log_prediction) * self.smearing_factor_ - 1.0


def _row_slice(data: object, start: int, stop: int) -> object:
    """Slice rows without changing pandas column metadata."""

    if hasattr(data, "iloc"):
        return data.iloc[start:stop]  # type: ignore[union-attr]
    return data[start:stop]  # type: ignore[index]


def feature_columns(feature_set: FeatureSet) -> list[str]:
    """Return the ordered feature columns for a supported feature set."""

    if feature_set not in FEATURE_SETS:
        raise ValueError(f"Unsupported feature set: {feature_set}")
    return list(FEATURE_SETS[feature_set])


def temporal_train_test_split(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.2,
) -> TemporalSplit:
    """Split a historical frame by complete dates, keeping the latest dates in test."""

    validate_historical_frame(frame.loc[:, sorted(HISTORICAL_COLUMNS)])
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")

    dated = frame.copy()
    dated["_parsed_date"] = pd.to_datetime(dated["date"], format="mixed", errors="raise")
    dated = dated.sort_values(["_parsed_date", "id"], kind="mergesort").reset_index(drop=True)
    unique_dates = pd.Series(dated["_parsed_date"].unique()).sort_values().reset_index(drop=True)
    test_date_count = max(1, ceil(len(unique_dates) * test_size))
    test_start = pd.Timestamp(unique_dates.iloc[-test_date_count])

    train = dated.loc[dated["_parsed_date"] < test_start].drop(columns="_parsed_date")
    test = dated.loc[dated["_parsed_date"] >= test_start].drop(columns="_parsed_date")
    if train.empty or test.empty:
        raise ValueError("Temporal split must produce non-empty train and test frames")

    return TemporalSplit(
        train=train.reset_index(drop=True),
        test=test.reset_index(drop=True),
        train_end=pd.Timestamp(train["date"].map(pd.to_datetime).max()),
        test_start=test_start,
    )


def _preprocessor(feature_set: FeatureSet, *, scale_numeric: bool) -> ColumnTransformer:
    features = feature_columns(feature_set)
    categorical = ["zipcode"]
    numeric = [column for column in features if column not in categorical]

    numeric_steps: list[tuple[str, object]] = [
        ("imputer", SimpleImputer(strategy="median")),
    ]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(numeric_steps),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "one_hot",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                categorical,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_estimator(
    model_name: Literal["ridge", "hist_gradient_boosting"],
    feature_set: FeatureSet,
    *,
    target_transform: TargetTransform = "raw",
    model_params: dict[str, object] | None = None,
) -> RegressorMixin:
    """Build a preprocessing and regression pipeline."""

    params = model_params or {}
    if model_name == "ridge":
        model = Ridge(alpha=float(params.get("alpha", 10.0)))
        preprocessor = _preprocessor(feature_set, scale_numeric=True)
    elif model_name == "hist_gradient_boosting":
        loss = str(params.get("loss", "squared_error"))
        supported_losses = {"squared_error", "absolute_error", "gamma", "poisson", "quantile"}
        if loss not in supported_losses:
            raise ValueError(f"Unsupported histogram gradient boosting loss: {loss}")
        model = HistGradientBoostingRegressor(
            loss=loss,
            learning_rate=float(params.get("learning_rate", 0.06)),
            max_iter=int(params.get("max_iter", 300)),
            max_leaf_nodes=int(params.get("max_leaf_nodes", 31)),
            l2_regularization=float(params.get("l2_regularization", 0.1)),
            random_state=42,
        )
        preprocessor = _preprocessor(feature_set, scale_numeric=False)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
    if target_transform == "raw":
        return pipeline
    if target_transform == "log":
        return TransformedTargetRegressor(
            regressor=pipeline,
            func=np.log1p,
            inverse_func=np.expm1,
        )
    if target_transform == "log_smearing":
        return SmearingRegressor(pipeline)
    if target_transform == "log_temporal_smearing":
        return SmearingRegressor(
            pipeline,
            calibration_fraction=float(params.get("calibration_fraction", 0.1)),
        )
    raise ValueError(f"Unsupported target transform: {target_transform}")


def regression_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    """Calculate regression metrics on the original price scale."""

    actual = np.asarray(y_true, dtype=float)
    predicted = np.clip(np.asarray(y_pred, dtype=float), a_min=0, a_max=None)
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "rmsle": float(np.sqrt(mean_squared_log_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
        "median_absolute_error": float(median_absolute_error(actual, predicted)),
    }


def vertical_equity_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    """Calculate calibration and price-related uniformity diagnostics.

    The ratio-study metrics are adapted for predictive monitoring and do not
    represent a formal tax-assessment compliance determination.
    """

    actual = np.asarray(y_true, dtype=float)
    predicted = np.clip(np.asarray(y_pred, dtype=float), a_min=0, a_max=None)
    if len(actual) == 0 or len(actual) != len(predicted):
        raise ValueError("Actual and predicted values must have the same non-zero length")
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Actual and predicted values must be finite")
    if (actual <= 0).any():
        raise ValueError("Vertical equity metrics require positive actual values")

    errors = predicted - actual
    ratios = predicted / actual
    median_ratio = float(np.median(ratios))
    weighted_mean_ratio = float(predicted.sum() / actual.sum())
    if median_ratio <= 0 or weighted_mean_ratio <= 0:
        raise ValueError("Vertical equity ratios require positive predictions")

    return {
        "mape": float(np.mean(np.abs(errors) / actual)),
        "mean_error": float(np.mean(errors)),
        "mean_percentage_error": float(np.mean(errors / actual)),
        "underprediction_rate": float(np.mean(errors < 0)),
        "median_prediction_ratio": median_ratio,
        "coefficient_of_dispersion": float(
            100 * np.mean(np.abs(ratios - median_ratio)) / median_ratio
        ),
        "price_related_differential": float(np.mean(ratios) / weighted_mean_ratio),
    }


def _fold_metrics(
    training_target: pd.Series,
    validation_target: pd.Series,
    predictions: np.ndarray | pd.Series,
    *,
    high_price_quantile: float = 0.75,
) -> dict[str, float | int]:
    """Calculate overall and upper-price diagnostics for one temporal fold."""

    if not 0 < high_price_quantile < 1:
        raise ValueError("high_price_quantile must be between 0 and 1")
    prediction_series = pd.Series(
        np.clip(np.asarray(predictions, dtype=float), a_min=0, a_max=None),
        index=validation_target.index,
    )
    threshold = float(training_target.quantile(high_price_quantile))
    high_mask = validation_target >= threshold
    if not high_mask.any():
        raise ValueError("The validation fold has no observations in the upper-price segment")

    overall = {
        **regression_metrics(validation_target, prediction_series),
        **vertical_equity_metrics(validation_target, prediction_series),
    }
    high_regression = regression_metrics(
        validation_target.loc[high_mask],
        prediction_series.loc[high_mask],
    )
    high_vertical = vertical_equity_metrics(
        validation_target.loc[high_mask],
        prediction_series.loc[high_mask],
    )
    return {
        **overall,
        "high_price_threshold": threshold,
        "high_price_rows": int(high_mask.sum()),
        "high_price_mae": high_regression["mae"],
        "high_price_rmse": high_regression["rmse"],
        "high_price_mape": high_vertical["mape"],
        "high_price_mean_error": high_vertical["mean_error"],
        "high_price_underprediction_rate": high_vertical["underprediction_rate"],
        "high_price_median_prediction_ratio": high_vertical["median_prediction_ratio"],
    }


def cross_validate_temporal(
    estimator: RegressorMixin,
    frame: pd.DataFrame,
    *,
    feature_set: FeatureSet,
    n_splits: int = 3,
) -> pd.DataFrame:
    """Evaluate an estimator with expanding temporal folds."""

    ordered = frame.copy()
    ordered["_parsed_date"] = pd.to_datetime(ordered["date"], format="mixed", errors="raise")
    ordered = ordered.sort_values(["_parsed_date", "id"], kind="mergesort").reset_index(drop=True)
    X = ordered[feature_columns(feature_set)]
    y = ordered["price"]
    rows: list[dict[str, object]] = []

    for fold, train_idx, validation_idx in _complete_date_folds(ordered, n_splits):
        fitted = clone(estimator)
        fitted.fit(X.iloc[train_idx], y.iloc[train_idx])
        predictions = fitted.predict(X.iloc[validation_idx])
        metrics = _fold_metrics(
            y.iloc[train_idx],
            y.iloc[validation_idx],
            predictions,
        )
        rows.append(
            {
                "fold": fold,
                "train_end": ordered.iloc[train_idx]["_parsed_date"].max(),
                "validation_start": ordered.iloc[validation_idx]["_parsed_date"].min(),
                "validation_end": ordered.iloc[validation_idx]["_parsed_date"].max(),
                "train_rows": len(train_idx),
                "validation_rows": len(validation_idx),
                **metrics,
            }
        )

    return pd.DataFrame(rows)


def fit_and_evaluate(
    estimator: RegressorMixin,
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    feature_set: FeatureSet,
) -> FittedEvaluation:
    """Fit on the development partition and evaluate on the temporal holdout."""

    columns = feature_columns(feature_set)
    fitted = clone(estimator)
    started = perf_counter()
    fitted.fit(train[columns], train["price"])
    fit_seconds = perf_counter() - started
    predictions = pd.Series(
        np.clip(fitted.predict(test[columns]), a_min=0, a_max=None),
        index=test.index,
        name="prediction",
    )
    return FittedEvaluation(
        estimator=fitted,
        predictions=predictions,
        metrics=regression_metrics(test["price"], predictions),
        fit_seconds=fit_seconds,
    )


def median_baseline_prediction(train: pd.DataFrame, test: pd.DataFrame) -> pd.Series:
    """Predict the training median for every row in the test frame."""

    return pd.Series(
        float(train["price"].median()),
        index=test.index,
        name="prediction",
    )


def cross_validate_median_baseline(
    frame: pd.DataFrame,
    *,
    n_splits: int = 3,
) -> pd.DataFrame:
    """Evaluate the median baseline with expanding temporal folds."""

    ordered = frame.copy()
    ordered["_parsed_date"] = pd.to_datetime(ordered["date"], format="mixed", errors="raise")
    ordered = ordered.sort_values(["_parsed_date", "id"], kind="mergesort").reset_index(drop=True)
    y = ordered["price"]
    rows: list[dict[str, object]] = []

    for fold, train_idx, validation_idx in _complete_date_folds(ordered, n_splits):
        predictions = pd.Series(float(y.iloc[train_idx].median()), index=validation_idx)
        metrics = _fold_metrics(
            y.iloc[train_idx],
            y.iloc[validation_idx],
            predictions,
        )
        rows.append(
            {
                "fold": fold,
                "train_end": ordered.iloc[train_idx]["_parsed_date"].max(),
                "validation_start": ordered.iloc[validation_idx]["_parsed_date"].min(),
                "validation_end": ordered.iloc[validation_idx]["_parsed_date"].max(),
                "train_rows": len(train_idx),
                "validation_rows": len(validation_idx),
                **metrics,
            }
        )

    return pd.DataFrame(rows)


def _complete_date_folds(
    ordered: pd.DataFrame,
    n_splits: int,
) -> list[tuple[int, np.ndarray, np.ndarray]]:
    """Build expanding folds without placing one date in two partitions."""

    unique_dates = pd.Series(ordered["_parsed_date"].unique()).sort_values().reset_index(drop=True)
    splitter = TimeSeriesSplit(n_splits=n_splits)
    folds: list[tuple[int, np.ndarray, np.ndarray]] = []

    for fold, (train_dates, validation_dates) in enumerate(
        splitter.split(unique_dates),
        start=1,
    ):
        train_end = unique_dates.iloc[train_dates[-1]]
        validation_start = unique_dates.iloc[validation_dates[0]]
        validation_end = unique_dates.iloc[validation_dates[-1]]
        train_idx = np.flatnonzero(ordered["_parsed_date"].le(train_end).to_numpy())
        validation_idx = np.flatnonzero(
            ordered["_parsed_date"].between(validation_start, validation_end).to_numpy()
        )
        folds.append((fold, train_idx, validation_idx))

    return folds


def summarize_temporal_validation(
    results: Mapping[str, pd.DataFrame],
    *,
    reference_candidate: str | None = None,
) -> pd.DataFrame:
    """Aggregate temporal validation metrics for comparable candidates."""

    if not results:
        raise ValueError("At least one validation result is required")

    if reference_candidate is not None and reference_candidate not in results:
        raise ValueError(f"Unknown reference candidate: {reference_candidate}")

    rows: list[dict[str, float | int | str]] = []
    required_columns = {"mae", "rmse", "rmsle"}
    for candidate, scores in results.items():
        missing = required_columns - set(scores.columns)
        if missing:
            missing_columns = ", ".join(sorted(missing))
            raise ValueError(f"Validation result for {candidate} is missing: {missing_columns}")
        row: dict[str, float | int | str] = {
            "candidate": candidate,
            "cv_mae_mean": float(scores["mae"].mean()),
            "cv_mae_std": float(scores["mae"].std(ddof=0)),
            "cv_mae_worst": float(scores["mae"].max()),
            "cv_rmse_mean": float(scores["rmse"].mean()),
            "cv_rmsle_mean": float(scores["rmsle"].mean()),
        }
        vertical_columns = {
            "mape": "cv_mape_mean",
            "mean_error": "cv_mean_error_mean",
            "underprediction_rate": "cv_underprediction_rate_mean",
            "median_prediction_ratio": "cv_median_prediction_ratio_mean",
            "price_related_differential": "cv_prd_mean",
            "high_price_mae": "cv_high_price_mae_mean",
            "high_price_mape": "cv_high_price_mape_mean",
            "high_price_mean_error": "cv_high_price_mean_error_mean",
            "high_price_underprediction_rate": "cv_high_price_underprediction_rate_mean",
            "high_price_median_prediction_ratio": "cv_high_price_median_ratio_mean",
        }
        for source, destination in vertical_columns.items():
            if source in scores:
                row[destination] = float(scores[source].mean())
        if "mean_error" in scores:
            row["cv_abs_mean_error_mean"] = float(scores["mean_error"].abs().mean())
        if "price_related_differential" in scores:
            row["cv_prd_deviation_mean"] = float(
                (scores["price_related_differential"] - 1).abs().mean()
            )
        if "high_price_mean_error" in scores:
            row["cv_high_price_abs_mean_error_mean"] = float(
                scores["high_price_mean_error"].abs().mean()
            )
        if reference_candidate is not None:
            reference_scores = results[reference_candidate]
            required_tail_columns = {"fold", "high_price_mae"}
            candidate_has_tail = required_tail_columns.issubset(scores.columns)
            reference_has_tail = required_tail_columns.issubset(reference_scores.columns)
            if not candidate_has_tail or not reference_has_tail:
                raise ValueError("Tail comparison requires fold and high_price_mae columns")
            comparison = scores.loc[:, ["fold", "high_price_mae"]].merge(
                reference_scores.loc[:, ["fold", "high_price_mae"]],
                on="fold",
                suffixes=("", "_reference"),
                validate="one_to_one",
            )
            row["high_price_mae_improved_folds"] = int(
                (comparison["high_price_mae"] < comparison["high_price_mae_reference"]).sum()
            )
        rows.append(row)

    return pd.DataFrame(rows).sort_values(
        ["cv_mae_mean", "cv_mae_std"],
        ignore_index=True,
    )


def select_calibrated_candidate(
    summary: pd.DataFrame,
    *,
    reference_candidate: str,
    relative_tolerance: float = 0.005,
    minimum_improved_folds: int = 4,
) -> CalibrationSelection:
    """Promote a calibration only when general and upper-tail gates are satisfied."""

    if not 0 <= relative_tolerance < 1:
        raise ValueError("relative_tolerance must be between 0 and 1")
    if minimum_improved_folds < 1:
        raise ValueError("minimum_improved_folds must be positive")
    required_columns = {
        "candidate",
        "cv_mae_mean",
        "cv_mae_worst",
        "cv_high_price_mae_mean",
        "cv_high_price_abs_mean_error_mean",
        "cv_prd_deviation_mean",
        "high_price_mae_improved_folds",
    }
    missing = required_columns - set(summary.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Calibration summary is missing: {missing_columns}")
    reference_rows = summary.loc[summary["candidate"] == reference_candidate]
    if len(reference_rows) != 1:
        raise ValueError("Calibration summary must contain the reference candidate exactly once")

    reference = reference_rows.iloc[0]
    best_mean = float(summary["cv_mae_mean"].min())
    eligible = summary.loc[
        (summary["candidate"] != reference_candidate)
        & (summary["cv_mae_mean"] <= best_mean * (1 + relative_tolerance))
        & (
            summary["cv_mae_mean"]
            <= float(reference["cv_mae_mean"]) * (1 + relative_tolerance)
        )
        & (summary["cv_high_price_mae_mean"] < float(reference["cv_high_price_mae_mean"]))
        & (
            summary["cv_high_price_abs_mean_error_mean"]
            < float(reference["cv_high_price_abs_mean_error_mean"])
        )
        & (summary["high_price_mae_improved_folds"] >= minimum_improved_folds)
    ].sort_values(
        [
            "cv_high_price_mae_mean",
            "cv_high_price_abs_mean_error_mean",
            "cv_prd_deviation_mean",
            "cv_mae_worst",
        ],
        ignore_index=True,
    )

    promoted = not eligible.empty
    champion = str(eligible.iloc[0]["candidate"]) if promoted else reference_candidate
    return CalibrationSelection(
        champion=champion,
        reference=reference_candidate,
        relative_tolerance=relative_tolerance,
        minimum_improved_folds=minimum_improved_folds,
        promoted=promoted,
    )


def select_temporal_candidates(
    summary: pd.DataFrame,
    *,
    relative_tolerance: float = 0.005,
) -> CandidateSelection:
    """Select a stable champion and the best-mean challenger without holdout data."""

    if not 0 <= relative_tolerance < 1:
        raise ValueError("relative_tolerance must be between 0 and 1")
    required_columns = {"candidate", "cv_mae_mean", "cv_mae_std", "cv_mae_worst"}
    missing = required_columns - set(summary.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Validation summary is missing: {missing_columns}")
    if len(summary) < 2:
        raise ValueError("At least two candidates are required")

    ranked = summary.sort_values(
        ["cv_mae_mean", "cv_mae_std"],
        ignore_index=True,
    )
    best_mean = float(ranked.iloc[0]["cv_mae_mean"])
    eligible = ranked.loc[
        ranked["cv_mae_mean"] <= best_mean * (1 + relative_tolerance)
    ].sort_values(
        ["cv_mae_worst", "cv_mae_std", "cv_mae_mean"],
        ignore_index=True,
    )
    champion = str(eligible.iloc[0]["candidate"])
    challenger = str(ranked.loc[ranked["candidate"] != champion].iloc[0]["candidate"])
    return CandidateSelection(
        champion=champion,
        challenger=challenger,
        relative_tolerance=relative_tolerance,
    )


def segment_metrics(
    y_true: pd.Series,
    y_pred: pd.Series,
    segments: pd.Series,
    *,
    segment_name: str = "segment",
) -> pd.DataFrame:
    """Calculate error metrics for each segment."""

    values = pd.DataFrame(
        {
            segment_name: segments.reset_index(drop=True),
            "actual": y_true.reset_index(drop=True),
            "prediction": y_pred.reset_index(drop=True),
        }
    )
    rows: list[dict[str, object]] = []
    for value, group in values.groupby(segment_name, sort=True, dropna=False, observed=True):
        metrics = {
            **regression_metrics(group["actual"], group["prediction"]),
            **vertical_equity_metrics(group["actual"], group["prediction"]),
        }
        rows.append(
            {
                segment_name: value,
                "rows": len(group),
                **metrics,
            }
        )
    return pd.DataFrame(rows)
