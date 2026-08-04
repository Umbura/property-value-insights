"""Versioned model artifact persistence and batch inference utilities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import joblib
import numpy as np
import pandas as pd

from .data_contract import validate_future_frame

ARTIFACT_SCHEMA_VERSION = "1.0"


class ArtifactIntegrityError(ValueError):
    """Raised when an artifact or its metadata fails integrity validation."""


def sha256_file(path: str | Path) -> str:
    """Calculate a SHA-256 digest without loading the complete file in memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_normalized_text_file(path: str | Path) -> str:
    """Calculate a cross-platform text digest with line endings normalized to LF."""

    content = Path(path).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


def create_model_bundle(
    estimator: object,
    *,
    model_name: str,
    model_version: str,
    feature_columns: list[str],
) -> dict[str, Any]:
    """Create the stable payload persisted as the model artifact."""

    if not model_name.strip() or not model_version.strip():
        raise ValueError("Model name and version cannot be empty")
    if not feature_columns or len(feature_columns) != len(set(feature_columns)):
        raise ValueError("Feature columns must be a non-empty unique list")
    if not hasattr(estimator, "predict"):
        raise TypeError("Estimator must provide a predict method")
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "model_name": model_name,
        "model_version": model_version,
        "feature_columns": list(feature_columns),
        "estimator": estimator,
    }


def validate_model_bundle(bundle: object) -> Mapping[str, Any]:
    """Validate the structure required by training and serving code."""

    if not isinstance(bundle, Mapping):
        raise ArtifactIntegrityError("Model artifact must contain a mapping")
    required = {
        "schema_version",
        "model_name",
        "model_version",
        "feature_columns",
        "estimator",
    }
    missing = required - set(bundle)
    if missing:
        raise ArtifactIntegrityError(
            "Model artifact is missing fields: " + ", ".join(sorted(missing))
        )
    if bundle["schema_version"] != ARTIFACT_SCHEMA_VERSION:
        raise ArtifactIntegrityError("Unsupported model artifact schema version")
    for field in ("model_name", "model_version"):
        if not isinstance(bundle[field], str) or not bundle[field].strip():
            raise ArtifactIntegrityError(f"Model artifact contains an invalid {field}")
    features = bundle["feature_columns"]
    if not isinstance(features, list) or not features or len(features) != len(set(features)):
        raise ArtifactIntegrityError("Model artifact contains invalid feature columns")
    if not all(isinstance(column, str) and column for column in features):
        raise ArtifactIntegrityError("Model artifact feature names must be non-empty strings")
    if not hasattr(bundle["estimator"], "predict"):
        raise ArtifactIntegrityError("Model artifact estimator does not support prediction")
    return bundle


def save_model_bundle(bundle: Mapping[str, Any], path: str | Path) -> Path:
    """Persist a validated model bundle with compression."""

    validate_model_bundle(bundle)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(dict(bundle), destination, compress=3)
    return destination


def load_model_bundle(
    path: str | Path,
    *,
    manifest_path: str | Path,
) -> Mapping[str, Any]:
    """Load a model bundle after verifying its hash and manifest metadata."""

    bundle, _ = load_model_bundle_with_manifest(path, manifest_path=manifest_path)
    return bundle


def load_model_bundle_with_manifest(
    path: str | Path,
    *,
    manifest_path: str | Path,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Load a model bundle and return the exact manifest used for verification."""

    source = Path(path)
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactIntegrityError("Model manifest could not be read") from error
    if not isinstance(manifest, Mapping):
        raise ArtifactIntegrityError("Model manifest must contain a mapping")
    if manifest.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
        raise ArtifactIntegrityError("Unsupported model manifest schema version")

    artifact_metadata = manifest.get("artifact")
    model_metadata = manifest.get("model")
    if not isinstance(artifact_metadata, Mapping) or not isinstance(model_metadata, Mapping):
        raise ArtifactIntegrityError("Model manifest is missing artifact or model metadata")
    expected_hash = artifact_metadata.get("sha256")
    if not isinstance(expected_hash, str) or sha256_file(source) != expected_hash:
        raise ArtifactIntegrityError("Model artifact hash does not match the manifest")

    bundle = validate_model_bundle(joblib.load(source))
    manifest_fields = {
        "name": "model_name",
        "version": "model_version",
        "feature_columns": "feature_columns",
    }
    for manifest_field, bundle_field in manifest_fields.items():
        if model_metadata.get(manifest_field) != bundle[bundle_field]:
            raise ArtifactIntegrityError(
                f"Model manifest {manifest_field} does not match the artifact"
            )
    return bundle, manifest


def predict_future(bundle: Mapping[str, Any], frame: pd.DataFrame) -> pd.DataFrame:
    """Validate future examples and produce the public batch output schema."""

    validated = validate_model_bundle(bundle)
    validate_future_frame(frame)
    features = list(validated["feature_columns"])
    missing = sorted(set(features) - set(frame.columns))
    if missing:
        raise ArtifactIntegrityError(
            "Inference frame is missing artifact features: " + ", ".join(missing)
        )

    predictions = np.asarray(validated["estimator"].predict(frame[features]), dtype=float)
    if predictions.ndim != 1 or len(predictions) != len(frame):
        raise ArtifactIntegrityError("Estimator returned an incompatible prediction shape")
    if not np.isfinite(predictions).all() or (predictions <= 0).any():
        raise ArtifactIntegrityError("Estimator returned non-positive or non-finite prices")

    return pd.DataFrame(
        {
            "row_id": np.arange(1, len(frame) + 1, dtype=int),
            "predicted_price": np.round(predictions, 2),
            "model_version": str(validated["model_version"]),
        }
    )


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    """Write deterministic, human-readable UTF-8 JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
