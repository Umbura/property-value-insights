from pathlib import Path

import pandas as pd
import pytest

from property_value_insights.data_contract import (
    DataContractError,
    load_raw_data,
    validate_demographics_frame,
    validate_future_frame,
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
