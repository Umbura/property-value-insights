from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from property_value_insights.artifact import (
    ARTIFACT_SCHEMA_VERSION,
    ArtifactIntegrityError,
    create_model_bundle,
    load_model_bundle,
    predict_future,
    save_model_bundle,
    sha256_file,
)
from property_value_insights.data_contract import load_raw_data
from property_value_insights.modeling import build_estimator, feature_columns
from property_value_insights.training import filter_temporally_consistent_rows

DATA_DIR = Path(__file__).parents[1] / "data" / "raw"


def _fitted_bundle() -> tuple[dict[str, object], pd.DataFrame]:
    historical, _, future = load_raw_data(DATA_DIR)
    training = historical.sort_values("date").head(600)
    features = feature_columns("physical")
    estimator = build_estimator(
        "ridge",
        "physical",
        target_transform="log_temporal_smearing",
        model_params={"calibration_fraction": 0.1},
    )
    estimator.fit(training[features], training["price"])
    bundle = create_model_bundle(
        estimator,
        model_name="test-model",
        model_version="test-version",
        feature_columns=features,
    )
    return bundle, future.head(5)


def test_temporal_consistency_filter_excludes_future_property_events() -> None:
    historical, _, _ = load_raw_data(DATA_DIR)

    filtered, audit = filter_temporally_consistent_rows(historical)

    sale_year = pd.to_datetime(filtered["date"]).dt.year
    assert audit.input_rows == 21613
    assert audit.construction_after_sale_rows == 12
    assert audit.renovation_after_sale_rows == 6
    assert audit.excluded_rows == 18
    assert audit.retained_rows == 21595
    assert (filtered["yr_built"] <= sale_year).all()
    assert ((filtered["yr_renovated"] == 0) | (filtered["yr_renovated"] <= sale_year)).all()


def test_persisted_bundle_reproduces_predictions(tmp_path: Path) -> None:
    bundle, future = _fitted_bundle()
    artifact_path = save_model_bundle(bundle, tmp_path / "model.joblib")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "artifact": {"sha256": sha256_file(artifact_path)},
            }
        ),
        encoding="utf-8",
    )

    before = predict_future(bundle, future)
    loaded = load_model_bundle(artifact_path, manifest_path=manifest_path)
    after = predict_future(loaded, future)

    pd.testing.assert_frame_equal(before, after)
    assert list(after.columns) == ["row_id", "predicted_price", "model_version"]
    assert after["row_id"].tolist() == [1, 2, 3, 4, 5]
    assert np.isfinite(after["predicted_price"]).all()


def test_loading_rejects_artifact_hash_mismatch(tmp_path: Path) -> None:
    bundle, _ = _fitted_bundle()
    artifact_path = save_model_bundle(bundle, tmp_path / "model.joblib")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps({"artifact": {"sha256": "0" * 64}}),
        encoding="utf-8",
    )

    with pytest.raises(ArtifactIntegrityError, match="hash"):
        load_model_bundle(artifact_path, manifest_path=manifest_path)
