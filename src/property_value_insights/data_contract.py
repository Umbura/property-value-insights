"""Validation rules for the raw datasets supplied with the challenge."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


class DataContractError(ValueError):
    """Raised when a raw dataset violates the project data contract."""


HISTORICAL_COLUMNS = frozenset(
    {
        "id",
        "date",
        "price",
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
    }
)

DEMOGRAPHICS_COLUMNS = frozenset(
    {
        "ppltn_qty",
        "urbn_ppltn_qty",
        "sbrbn_ppltn_qty",
        "farm_ppltn_qty",
        "non_farm_qty",
        "medn_hshld_incm_amt",
        "medn_incm_per_prsn_amt",
        "hous_val_amt",
        "edctn_less_than_9_qty",
        "edctn_9_12_qty",
        "edctn_high_schl_qty",
        "edctn_some_clg_qty",
        "edctn_assoc_dgre_qty",
        "edctn_bchlr_dgre_qty",
        "edctn_prfsnl_qty",
        "per_urbn",
        "per_sbrbn",
        "per_farm",
        "per_non_farm",
        "per_less_than_9",
        "per_9_to_12",
        "per_hsd",
        "per_some_clg",
        "per_assoc",
        "per_bchlr",
        "per_prfsnl",
        "zipcode",
    }
)

FUTURE_COLUMNS = frozenset(HISTORICAL_COLUMNS - {"id", "date", "price"})

_HISTORICAL_NUMERIC_COLUMNS = frozenset(HISTORICAL_COLUMNS - {"date", "zipcode"})
_DEMOGRAPHICS_NUMERIC_COLUMNS = frozenset(DEMOGRAPHICS_COLUMNS - {"zipcode"})
_FUTURE_NUMERIC_COLUMNS = frozenset(FUTURE_COLUMNS - {"zipcode"})

_HISTORICAL_NON_NEGATIVE_COLUMNS = frozenset(
    {
        "id",
        "price",
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
        "sqft_living15",
        "sqft_lot15",
    }
)
_DEMOGRAPHICS_NON_NEGATIVE_COLUMNS = _DEMOGRAPHICS_NUMERIC_COLUMNS
_FUTURE_NON_NEGATIVE_COLUMNS = frozenset(_FUTURE_NUMERIC_COLUMNS - {"lat", "long"})

_PERCENTAGE_COLUMNS = frozenset(
    {
        "per_urbn",
        "per_sbrbn",
        "per_farm",
        "per_non_farm",
        "per_less_than_9",
        "per_9_to_12",
        "per_hsd",
        "per_some_clg",
        "per_assoc",
        "per_bchlr",
        "per_prfsnl",
    }
)


@dataclass(frozen=True)
class HistoricalAudit:
    """Stable facts used to document the supplied historical dataset."""

    rows: int
    duplicate_id_keys: int
    exact_duplicate_rows: int
    unique_zipcodes: int


def _validate_columns(frame: pd.DataFrame, expected: Iterable[str], dataset_name: str) -> None:
    expected_set = set(expected)
    actual_set = set(frame.columns)
    missing = sorted(expected_set - actual_set)
    unexpected = sorted(actual_set - expected_set)
    if missing or unexpected or len(frame.columns) != len(actual_set):
        details = []
        if missing:
            details.append(f"missing={missing}")
        if unexpected:
            details.append(f"unexpected={unexpected}")
        if len(frame.columns) != len(actual_set):
            details.append("duplicate_column_names=True")
        raise DataContractError(f"Invalid columns for {dataset_name}: " + "; ".join(details))


def _validate_numeric_columns(
    frame: pd.DataFrame,
    columns: Iterable[str],
    dataset_name: str,
) -> None:
    for column in sorted(columns):
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any():
            raise DataContractError(f"Non-numeric values found in {dataset_name}.{column}")


def _validate_non_negative(
    frame: pd.DataFrame,
    columns: Iterable[str],
    dataset_name: str,
) -> None:
    for column in sorted(columns):
        values = pd.to_numeric(frame[column], errors="coerce")
        if (values < 0).any():
            raise DataContractError(f"Negative values found in {dataset_name}.{column}")


def _validate_range(
    frame: pd.DataFrame,
    column: str,
    dataset_name: str,
    *,
    minimum: float,
    maximum: float,
    integer: bool = False,
) -> None:
    values = pd.to_numeric(frame[column], errors="coerce")
    if (values < minimum).any() or (values > maximum).any():
        raise DataContractError(
            f"Values outside [{minimum}, {maximum}] found in {dataset_name}.{column}"
        )
    if integer and not values.mod(1).eq(0).all():
        raise DataContractError(f"Non-integer values found in {dataset_name}.{column}")


def _validate_positive(frame: pd.DataFrame, column: str, dataset_name: str) -> None:
    values = pd.to_numeric(frame[column], errors="coerce")
    if (values <= 0).any():
        raise DataContractError(f"Non-positive values found in {dataset_name}.{column}")


def _validate_zipcodes(frame: pd.DataFrame, dataset_name: str) -> None:
    values = frame["zipcode"].astype("string")
    if not values.str.fullmatch(r"\d{5}", na=False).all():
        raise DataContractError(f"Zipcodes must contain exactly five digits in {dataset_name}")


def validate_historical_frame(frame: pd.DataFrame) -> HistoricalAudit:
    """Validate the labeled dataset without assuming that `id` is unique."""

    _validate_columns(frame, HISTORICAL_COLUMNS, "historical data")
    if frame.empty:
        raise DataContractError("Historical data cannot be empty")
    if frame[["id", "date", "price", "zipcode"]].isna().any().any():
        raise DataContractError("Historical identifiers, date, price and zipcode cannot be null")
    _validate_zipcodes(frame, "historical data")
    _validate_numeric_columns(frame, _HISTORICAL_NUMERIC_COLUMNS, "historical data")
    _validate_non_negative(frame, _HISTORICAL_NON_NEGATIVE_COLUMNS, "historical data")
    _validate_positive(frame, "price", "historical data")
    _validate_range(frame, "waterfront", "historical data", minimum=0, maximum=1, integer=True)
    _validate_range(frame, "view", "historical data", minimum=0, maximum=4, integer=True)
    _validate_range(frame, "condition", "historical data", minimum=1, maximum=5, integer=True)
    _validate_range(frame, "grade", "historical data", minimum=1, maximum=13, integer=True)
    _validate_range(frame, "lat", "historical data", minimum=-90, maximum=90)
    _validate_range(frame, "long", "historical data", minimum=-180, maximum=180)
    if not pd.to_datetime(frame["date"], format="mixed", errors="coerce").notna().all():
        raise DataContractError("Historical date column contains invalid values")

    duplicate_id_keys = int(frame["id"].duplicated(keep=False).groupby(frame["id"]).any().sum())
    exact_duplicate_rows = int(frame.duplicated(keep=False).sum())
    return HistoricalAudit(
        rows=len(frame),
        duplicate_id_keys=duplicate_id_keys,
        exact_duplicate_rows=exact_duplicate_rows,
        unique_zipcodes=int(frame["zipcode"].nunique()),
    )


def validate_demographics_frame(frame: pd.DataFrame) -> None:
    """Validate the one-row-per-zipcode demographic lookup."""

    _validate_columns(frame, DEMOGRAPHICS_COLUMNS, "zipcode demographics")
    if frame.empty:
        raise DataContractError("Zipcode demographics cannot be empty")
    _validate_zipcodes(frame, "zipcode demographics")
    if frame["zipcode"].astype("string").duplicated().any():
        raise DataContractError("Zipcode demographics must contain one row per zipcode")
    _validate_numeric_columns(frame, _DEMOGRAPHICS_NUMERIC_COLUMNS, "zipcode demographics")
    _validate_non_negative(
        frame,
        _DEMOGRAPHICS_NON_NEGATIVE_COLUMNS,
        "zipcode demographics",
    )
    for column in sorted(_PERCENTAGE_COLUMNS):
        _validate_range(
            frame,
            column,
            "zipcode demographics",
            minimum=0,
            maximum=100,
        )


def validate_future_frame(frame: pd.DataFrame) -> None:
    """Validate the unlabeled examples reserved for final inference."""

    _validate_columns(frame, FUTURE_COLUMNS, "future examples")
    if frame.empty:
        raise DataContractError("Future examples cannot be empty")
    _validate_zipcodes(frame, "future examples")
    _validate_numeric_columns(frame, _FUTURE_NUMERIC_COLUMNS, "future examples")
    _validate_non_negative(frame, _FUTURE_NON_NEGATIVE_COLUMNS, "future examples")
    _validate_range(frame, "waterfront", "future examples", minimum=0, maximum=1, integer=True)
    _validate_range(frame, "view", "future examples", minimum=0, maximum=4, integer=True)
    _validate_range(frame, "condition", "future examples", minimum=1, maximum=5, integer=True)
    _validate_range(frame, "grade", "future examples", minimum=1, maximum=13, integer=True)
    _validate_range(frame, "lat", "future examples", minimum=-90, maximum=90)
    _validate_range(frame, "long", "future examples", minimum=-180, maximum=180)


def validate_zipcode_coverage(
    historical: pd.DataFrame,
    demographics: pd.DataFrame,
    future: pd.DataFrame,
) -> None:
    """Ensure every observed historical and future zipcode has a lookup row."""

    demographic_zipcodes = set(demographics["zipcode"].astype("string"))
    for name, frame in (("historical", historical), ("future", future)):
        missing = sorted(set(frame["zipcode"].astype("string")) - demographic_zipcodes)
        if missing:
            raise DataContractError(f"Missing demographic zipcodes for {name}: {missing}")


def load_raw_data(data_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load and validate the three supplied CSV files."""

    root = Path(data_dir)
    historical = pd.read_csv(root / "kc_house_data.csv", dtype={"zipcode": "string"})
    demographics = pd.read_csv(root / "zipcode_demographics.csv", dtype={"zipcode": "string"})
    future = pd.read_csv(root / "future_unseen_examples.csv", dtype={"zipcode": "string"})

    validate_historical_frame(historical)
    validate_demographics_frame(demographics)
    validate_future_frame(future)
    validate_zipcode_coverage(historical, demographics, future)
    return historical, demographics, future
