from pathlib import Path

import pandas as pd
import pytest

from property_value_insights.data_contract import DataContractError, load_raw_data
from property_value_insights.eda import (
    MergeAudit,
    iqr_outlier_summary,
    merge_historical_with_demographics,
    numeric_correlations,
    quality_summary,
    write_quality_report,
)

DATA_DIR = Path(__file__).parents[1] / "data" / "raw"


def test_merge_preserves_historical_rows_and_records_coverage() -> None:
    historical, demographics, _ = load_raw_data(DATA_DIR)

    merged, audit = merge_historical_with_demographics(historical, demographics)

    assert len(merged) == len(historical)
    assert audit.merged_rows == audit.historical_rows
    assert audit.unmatched_rows == 0
    assert audit.zipcode_coverage_pct == 100.0
    assert "medn_hshld_incm_amt" in merged.columns


def test_merge_rejects_duplicate_demographic_zipcodes() -> None:
    historical, demographics, _ = load_raw_data(DATA_DIR)
    duplicated = pd.concat([demographics, demographics.iloc[[0]]], ignore_index=True)

    with pytest.raises(DataContractError, match="one row per zipcode"):
        merge_historical_with_demographics(historical, duplicated)


def test_quality_summary_reports_missing_and_duplicate_rows() -> None:
    frame = pd.DataFrame({"zipcode": ["00001", "00001"], "value": [1, None]})

    summary = quality_summary(frame, "sample")

    assert summary.loc[0, "rows"] == 2
    assert summary.loc[0, "missing_cells"] == 1
    assert summary.loc[0, "exact_duplicate_rows"] == 0
    assert summary.loc[0, "unique_zipcodes"] == 1


def test_iqr_outlier_summary_counts_extreme_values() -> None:
    frame = pd.DataFrame({"price": [1, 2, 3, 100]})

    summary = iqr_outlier_summary(frame, ["price"])

    assert summary.loc[0, "outlier_rows"] == 1


def test_numeric_correlations_returns_ranked_features() -> None:
    frame = pd.DataFrame(
        {
            "price": [1, 2, 3, 4],
            "strong": [1, 2, 3, 4],
            "weak": [4, 1, 3, 2],
        }
    )

    correlations = numeric_correlations(frame, top_n=2)

    assert correlations.iloc[0]["feature"] == "strong"
    assert len(correlations) == 2


def test_quality_report_is_written(tmp_path: Path) -> None:
    output_path = tmp_path / "eda_quality.md"
    audit = MergeAudit(10, 10, 2, 2, 2, 0)
    quality = pd.DataFrame([{"dataset": "sample", "rows": 10}])
    outliers = pd.DataFrame([{"column": "price", "outlier_rows": 1}])
    correlations = pd.DataFrame([{"feature": "grade", "correlation": 0.8}])

    write_quality_report(
        output_path,
        audit=audit,
        quality=quality,
        outliers=outliers,
        correlations=correlations,
        duplicate_id_keys=2,
        exact_duplicate_rows=0,
    )

    report = output_path.read_text(encoding="utf-8")
    assert "Cobertura de CEP: 100.00%" in report
    assert "Chaves de ID repetidas: 2" in report
