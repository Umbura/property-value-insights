"""Reusable temporal modeling and evaluation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from time import perf_counter
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.base import RegressorMixin, clone
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

from .data_contract import DEMOGRAPHICS_COLUMNS, HISTORICAL_COLUMNS, validate_historical_frame

FeatureSet = Literal["physical", "with_demographics"]
TargetTransform = Literal["raw", "log"]

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
        model = HistGradientBoostingRegressor(
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
    splitter = TimeSeriesSplit(n_splits=n_splits)
    rows: list[dict[str, float | int]] = []

    for fold, (train_idx, validation_idx) in enumerate(splitter.split(X), start=1):
        fitted = clone(estimator)
        fitted.fit(X.iloc[train_idx], y.iloc[train_idx])
        predictions = fitted.predict(X.iloc[validation_idx])
        metrics = regression_metrics(y.iloc[validation_idx], predictions)
        rows.append({"fold": fold, **metrics})

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
    splitter = TimeSeriesSplit(n_splits=n_splits)
    rows: list[dict[str, float | int]] = []

    for fold, (train_idx, validation_idx) in enumerate(splitter.split(y), start=1):
        predictions = pd.Series(float(y.iloc[train_idx].median()), index=validation_idx)
        metrics = regression_metrics(y.iloc[validation_idx], predictions)
        rows.append({"fold": fold, **metrics})

    return pd.DataFrame(rows)


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
        metrics = regression_metrics(group["actual"], group["prediction"])
        rows.append(
            {
                segment_name: value,
                "rows": len(group),
                **metrics,
            }
        )
    return pd.DataFrame(rows)
