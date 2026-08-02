from pathlib import Path

import pandas as pd
import pytest

from property_value_insights.data_contract import (
    DataContractError,
    load_raw_data,
    validate_demographics_frame,
    validate_future_frame,
    validate_historical_frame,
    validate_zipcode_coverage,
)

DATA_DIR = Path(__file__).parents[1] / "data" / "raw"


def test_supplied_datasets_satisfy_the_contract() -> None:
    historical, demographics, future = load_raw_data(DATA_DIR)

    assert len(historical) == 21_613
    assert len(demographics) == 70
    assert len(future) == 100
    assert historical["price"].gt(0).all()
    assert "price" not in future.columns


def test_historical_ids_are_reference_values_not_unique_keys() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)

    assert historical["id"].duplicated().any()
    assert not historical.duplicated(keep=False).any()


def test_demographics_reject_duplicate_zipcodes() -> None:
    frame = pd.read_csv(DATA_DIR / "zipcode_demographics.csv", dtype={"zipcode": "string"})
    frame = pd.concat([frame.iloc[[0]], frame.iloc[[0]]], ignore_index=True)

    with pytest.raises(DataContractError, match="one row per zipcode"):
        validate_demographics_frame(frame)


def test_future_examples_reject_a_target_column() -> None:
    frame = pd.read_csv(DATA_DIR / "future_unseen_examples.csv", dtype={"zipcode": "string"})
    frame["price"] = 1

    with pytest.raises(DataContractError, match="Invalid columns"):
        validate_future_frame(frame)


def test_demographics_reject_missing_numeric_values() -> None:
    frame = pd.read_csv(DATA_DIR / "zipcode_demographics.csv", dtype={"zipcode": "string"})
    frame.loc[0, "ppltn_qty"] = None

    with pytest.raises(DataContractError, match="Non-numeric values"):
        validate_demographics_frame(frame)


def test_demographics_reject_percentages_outside_business_range() -> None:
    frame = pd.read_csv(DATA_DIR / "zipcode_demographics.csv", dtype={"zipcode": "string"})
    frame.loc[0, "per_urbn"] = 101

    with pytest.raises(DataContractError, match=r"outside \[0, 100\]"):
        validate_demographics_frame(frame)


def test_future_examples_reject_non_numeric_coordinates() -> None:
    frame = pd.read_csv(DATA_DIR / "future_unseen_examples.csv", dtype={"zipcode": "string"})
    frame["lat"] = frame["lat"].astype(object)
    frame.loc[0, "lat"] = "invalid"

    with pytest.raises(DataContractError, match="Non-numeric values"):
        validate_future_frame(frame)


def test_future_examples_reject_invalid_categorical_values() -> None:
    frame = pd.read_csv(DATA_DIR / "future_unseen_examples.csv", dtype={"zipcode": "string"})
    frame.loc[0, "waterfront"] = 2

    with pytest.raises(DataContractError, match=r"outside \[0, 1\]"):
        validate_future_frame(frame)


def test_future_examples_reject_malformed_zipcodes() -> None:
    frame = pd.read_csv(DATA_DIR / "future_unseen_examples.csv", dtype={"zipcode": "string"})
    frame.loc[0, "zipcode"] = "1234"

    with pytest.raises(DataContractError, match="exactly five digits"):
        validate_future_frame(frame)


def test_historical_data_reject_invalid_grade_values() -> None:
    frame = pd.read_csv(DATA_DIR / "kc_house_data.csv", dtype={"zipcode": "string"})
    frame.loc[0, "grade"] = 99

    with pytest.raises(DataContractError, match=r"outside \[1, 13\]"):
        validate_historical_frame(frame)


def test_historical_data_reject_invalid_dates() -> None:
    frame = pd.read_csv(DATA_DIR / "kc_house_data.csv", dtype={"zipcode": "string"})
    frame.loc[0, "date"] = "not-a-date"

    with pytest.raises(DataContractError, match="invalid values"):
        validate_historical_frame(frame)


def test_zipcode_coverage_rejects_missing_lookup_rows() -> None:
    historical, demographics, future = load_raw_data(DATA_DIR)
    target_zipcode = historical["zipcode"].iloc[0]
    reduced_demographics = demographics[demographics["zipcode"] != target_zipcode]

    with pytest.raises(DataContractError, match="Missing demographic zipcodes"):
        validate_zipcode_coverage(historical, reduced_demographics, future)
