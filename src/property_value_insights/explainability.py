"""Generate offline SHAP explanations for the approved model artifact."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from .artifact import (
    load_model_bundle_with_manifest,
    sha256_normalized_text_file,
)
from .data_contract import validate_future_frame
from .training import filter_temporally_consistent_rows

DEFAULT_PERMUTATION_CYCLES = 10
SHAP_BASE_SEED = 42
MAX_RELATIVE_ADDITIVITY_ERROR = 1e-4


@dataclass(frozen=True)
class ShapDiagnostics:
    """Global and local SHAP results tied to a verified model artifact."""

    global_importance: pd.DataFrame
    local_explanations: pd.DataFrame
    explained_rows: int
    background_rows: int
    max_additivity_error: float
    max_relative_additivity_error: float
    elapsed_seconds: float
    base_value: float
    permutation_cycles: int
    model_identity: dict[str, str]


def _encoded_features(frame: pd.DataFrame, features: list[str]) -> np.ndarray:
    values = frame.loc[:, features].copy()
    values["zipcode"] = pd.to_numeric(values["zipcode"], errors="raise")
    return values.astype(float).to_numpy()


def _prediction_function(estimator: object, features: list[str]):
    def predict(values: np.ndarray) -> np.ndarray:
        frame = pd.DataFrame(values, columns=features)
        frame["zipcode"] = (
            frame["zipcode"]
            .round()
            .astype(int)
            .astype(str)
            .str.zfill(5)
            .astype("string")
        )
        return np.asarray(estimator.predict(frame), dtype=float)  # type: ignore[attr-defined]

    return predict


def _deterministic_positions(row_count: int, sample_size: int | None) -> np.ndarray:
    if row_count < 1:
        raise ValueError("At least one row is required")
    if sample_size is None:
        return np.arange(row_count, dtype=int)
    if sample_size < 1:
        raise ValueError("sample_size must be positive")
    return np.linspace(0, row_count - 1, min(sample_size, row_count), dtype=int)


def _validate_sources(
    root: Path,
    manifest: Mapping[str, Any],
    historical_path: Path,
    future_path: Path,
) -> None:
    expected_historical = manifest["training_data"]["sha256"]
    if sha256_normalized_text_file(historical_path) != expected_historical:
        raise ValueError("Historical data hash does not match the model manifest")
    expected_future = manifest["prediction_output"]["source_sha256"]
    if sha256_normalized_text_file(future_path) != expected_future:
        raise ValueError("Future data hash does not match the model manifest")
    expected_artifact_path = root / manifest["artifact"]["path"]
    approved_artifact_path = root / "artifacts" / "property_value_model.joblib"
    if expected_artifact_path.resolve() != approved_artifact_path.resolve():
        raise ValueError("Model manifest points to an unexpected artifact path")


def evaluate_shap_explanations(
    project_root: str | Path,
    *,
    background_size: int = 50,
    explanation_size: int | None = None,
    permutation_cycles: int = DEFAULT_PERMUTATION_CYCLES,
) -> ShapDiagnostics:
    """Explain future predictions with a deterministic permutation explainer."""

    if explanation_size is not None and explanation_size < 3:
        raise ValueError("explanation_size must be at least three")
    if permutation_cycles < 1:
        raise ValueError("permutation_cycles must be positive")

    import shap

    root = Path(project_root)
    artifact_path = root / "artifacts" / "property_value_model.joblib"
    manifest_path = root / "artifacts" / "model_manifest.json"
    historical_path = root / "data" / "raw" / "kc_house_data.csv"
    future_path = root / "data" / "raw" / "future_unseen_examples.csv"
    bundle, manifest = load_model_bundle_with_manifest(
        artifact_path,
        manifest_path=manifest_path,
    )
    _validate_sources(root, manifest, historical_path, future_path)
    features = list(bundle["feature_columns"])
    if features != list(manifest["model"]["feature_columns"]):
        raise ValueError("Explainer features do not match the model manifest")

    historical = pd.read_csv(historical_path, dtype={"zipcode": "string"})
    historical, _ = filter_temporally_consistent_rows(historical)
    historical = historical.assign(
        _parsed_date=pd.to_datetime(historical["date"], format="mixed", errors="raise")
    ).sort_values(["_parsed_date", "id"], kind="mergesort")
    future = pd.read_csv(future_path, dtype={"zipcode": "string"})
    validate_future_frame(future)

    background_positions = _deterministic_positions(len(historical), background_size)
    explanation_positions = _deterministic_positions(len(future), explanation_size)
    background = _encoded_features(historical.iloc[background_positions], features)
    explanation_frame = future.iloc[explanation_positions].reset_index(drop=True)
    explanation_values = _encoded_features(explanation_frame, features)
    predict = _prediction_function(bundle["estimator"], features)

    started = perf_counter()
    explainer = shap.PermutationExplainer(
        predict,
        background,
        feature_names=features,
        seed=SHAP_BASE_SEED,
    )
    explanation = explainer(
        explanation_values,
        max_evals=permutation_cycles * (2 * len(features) + 1),
        error_bounds=True,
        batch_size=min(20, len(explanation_values)),
        silent=True,
    )
    elapsed_seconds = perf_counter() - started
    shap_values = np.asarray(explanation.values, dtype=float)
    base_values = np.broadcast_to(
        np.asarray(explanation.base_values, dtype=float),
        len(explanation_values),
    )
    permutation_std = np.asarray(explanation.error_std, dtype=float)
    predictions = predict(explanation_values)
    reconstructed = base_values + shap_values.sum(axis=1)
    additivity_errors = np.abs(reconstructed - predictions)
    max_additivity_error = float(additivity_errors.max())
    relative_additivity_errors = additivity_errors / np.maximum(
        np.abs(predictions), 1.0
    )
    max_relative_additivity_error = float(relative_additivity_errors.max())
    if max_relative_additivity_error > MAX_RELATIVE_ADDITIVITY_ERROR:
        raise RuntimeError("SHAP contributions do not reproduce model predictions")

    global_importance = (
        pd.DataFrame(
            {
                "feature": features,
                "mean_absolute_shap": np.abs(shap_values).mean(axis=0),
                "mean_signed_shap": shap_values.mean(axis=0),
                "mean_permutation_std": permutation_std.mean(axis=0),
            }
        )
        .sort_values("mean_absolute_shap", ascending=False, kind="mergesort")
        .reset_index(drop=True)
    )
    global_importance.insert(0, "rank", np.arange(1, len(global_importance) + 1))

    ranked_rows = np.argsort(predictions, kind="stable")
    local_positions = [ranked_rows[0], ranked_rows[len(ranked_rows) // 2], ranked_rows[-1]]
    local_labels = ["lower_prediction", "median_prediction", "upper_prediction"]
    local_rows: list[dict[str, object]] = []
    for label, position in zip(local_labels, local_positions, strict=True):
        absolute_order = np.argsort(-np.abs(shap_values[position]), kind="stable")
        ranks = np.empty(len(features), dtype=int)
        ranks[absolute_order] = np.arange(1, len(features) + 1)
        source_row = explanation_frame.iloc[position]
        for feature_index, feature in enumerate(features):
            feature_value = source_row[feature]
            local_rows.append(
                {
                    "example": label,
                    "row_id": int(explanation_positions[position]) + 1,
                    "predicted_price": float(predictions[position]),
                    "base_value": float(base_values[position]),
                    "reconstructed_prediction": float(reconstructed[position]),
                    "additivity_error": float(additivity_errors[position]),
                    "feature": feature,
                    "feature_value": str(feature_value),
                    "shap_value": float(shap_values[position, feature_index]),
                    "absolute_rank": int(ranks[feature_index]),
                }
            )
    model = manifest["model"]
    return ShapDiagnostics(
        global_importance=global_importance,
        local_explanations=pd.DataFrame(local_rows),
        explained_rows=len(explanation_values),
        background_rows=len(background),
        max_additivity_error=max_additivity_error,
        max_relative_additivity_error=max_relative_additivity_error,
        elapsed_seconds=elapsed_seconds,
        base_value=float(base_values.mean()),
        permutation_cycles=permutation_cycles,
        model_identity={
            "name": str(model["name"]),
            "version": str(model["version"]),
            "artifact_sha256": str(manifest["artifact"]["sha256"]),
            "historical_data_sha256": str(manifest["training_data"]["sha256"]),
            "future_data_sha256": str(manifest["prediction_output"]["source_sha256"]),
        },
    )


def _local_plot_rows(local: pd.DataFrame, *, limit: int = 7) -> pd.DataFrame:
    ordered = local.sort_values("absolute_rank", kind="mergesort")
    selected = ordered.head(limit).loc[:, ["feature", "shap_value"]].copy()
    remaining = float(ordered.iloc[limit:]["shap_value"].sum())
    if len(ordered) > limit:
        selected.loc[len(selected)] = {"feature": "other_features", "shap_value": remaining}
    return selected.sort_values("shap_value", kind="mergesort")


def write_shap_artifacts(
    project_root: str | Path,
    output_dir: str | Path | None = None,
    *,
    background_size: int = 50,
    explanation_size: int | None = None,
    permutation_cycles: int = DEFAULT_PERMUTATION_CYCLES,
) -> dict[str, Path]:
    """Write SHAP tables, metadata and a compact global/local figure."""

    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter, MaxNLocator

    root = Path(project_root)
    destination = Path(output_dir) if output_dir else root / "reports"
    figure_dir = destination / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = evaluate_shap_explanations(
        root,
        background_size=background_size,
        explanation_size=explanation_size,
        permutation_cycles=permutation_cycles,
    )

    global_path = destination / "shap_global_importance.csv"
    local_path = destination / "shap_local_explanations.csv"
    metadata_path = destination / "shap_metadata.json"
    figure_path = figure_dir / "shap_explanations.png"
    diagnostics.global_importance.round(
        {
            "mean_absolute_shap": 2,
            "mean_signed_shap": 2,
            "mean_permutation_std": 2,
        }
    ).to_csv(global_path, index=False, encoding="utf-8", lineterminator="\n")
    diagnostics.local_explanations.round(
        {
            "predicted_price": 2,
            "base_value": 2,
            "reconstructed_prediction": 2,
            "additivity_error": 8,
            "shap_value": 2,
        }
    ).to_csv(local_path, index=False, encoding="utf-8", lineterminator="\n")
    metadata_path.write_text(
        json.dumps(
            {
                "method": "shap_permutation_explainer",
                "scope": "offline_behavioral_explanation_not_causal_effect",
                "model_identity": diagnostics.model_identity,
                "explained_rows": diagnostics.explained_rows,
                "background_rows": diagnostics.background_rows,
                "permutation_cycles": diagnostics.permutation_cycles,
                "base_value": round(diagnostics.base_value, 6),
                "max_additivity_error": diagnostics.max_additivity_error,
                "max_relative_additivity_error": (
                    diagnostics.max_relative_additivity_error
                ),
                "shap_version": version("shap"),
                "limitations": [
                    "Attributions are approximate estimates across recorded permutation cycles.",
                    "Contributions describe model behavior relative to the selected baseline.",
                    "SHAP values do not establish causal effects.",
                    "Correlated features may share or redistribute attribution.",
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    feature_labels = {
        "sqft_living": "Área habitável",
        "grade": "Padrão construtivo",
        "lat": "Latitude",
        "long": "Longitude",
        "sqft_living15": "Área habitável vizinha",
        "sqft_lot": "Área do terreno",
        "sqft_lot15": "Terreno vizinho",
        "bedrooms": "Quartos",
        "bathrooms": "Banheiros",
        "floors": "Andares",
        "yr_built": "Ano de construção",
        "yr_renovated": "Ano de reforma",
        "zipcode": "CEP",
        "waterfront": "Frente para água",
        "view": "Qualidade da vista",
        "condition": "Conservação",
        "sqft_above": "Área acima do solo",
        "sqft_basement": "Área de porão",
        "other_features": "Demais características",
    }

    def format_currency(value: float, _: float) -> str:
        sign = "-" if value < 0 else ""
        if abs(value) < 500:
            return f"{sign}US$ 0"
        return f"{sign}US$ {abs(value) / 1_000:.0f} mil"

    currency = FuncFormatter(format_currency)
    figure, axes = plt.subplots(2, 2, figsize=(15, 9), constrained_layout=True)
    figure.patch.set_facecolor("#F7F8F5")
    axes_flat = axes.ravel()
    for axis in axes_flat:
        axis.set_facecolor("#FFFFFF")
        axis.grid(axis="x", color="#D8DED8", linewidth=0.7, alpha=0.8)
        axis.spines[["top", "right"]].set_visible(False)

    global_top = diagnostics.global_importance.head(10).sort_values(
        "mean_absolute_shap", ascending=True
    )
    axes_flat[0].barh(
        global_top["feature"].map(lambda name: feature_labels.get(name, name)),
        global_top["mean_absolute_shap"],
        color="#176B66",
    )
    axes_flat[0].set_title("Importância global")
    axes_flat[0].set_xlabel("Contribuição SHAP absoluta média")
    axes_flat[0].xaxis.set_major_locator(MaxNLocator(nbins=5))
    axes_flat[0].xaxis.set_major_formatter(currency)

    panel_titles = {
        "lower_prediction": "Previsão baixa",
        "median_prediction": "Previsão mediana",
        "upper_prediction": "Previsão alta",
    }
    for axis, (example, local) in zip(
        axes_flat[1:],
        diagnostics.local_explanations.groupby("example", sort=False),
        strict=True,
    ):
        plot_rows = _local_plot_rows(local)
        colors = np.where(plot_rows["shap_value"] >= 0, "#176B66", "#D1495B")
        axis.barh(
            plot_rows["feature"].map(lambda name: feature_labels.get(name, name)),
            plot_rows["shap_value"],
            color=colors,
        )
        prediction = float(local["predicted_price"].iloc[0])
        axis.axvline(0, color="#2F3E46", linewidth=0.8)
        axis.set_title(f"{panel_titles[example]} · US$ {prediction:,.0f}")
        axis.set_xlabel("Contribuição para a previsão")
        axis.xaxis.set_major_locator(MaxNLocator(nbins=5))
        axis.xaxis.set_major_formatter(currency)

    figure.suptitle(
        "Explicações SHAP do artefato aprovado\n"
        f"{diagnostics.explained_rows} exemplos futuros · "
        f"baseline médio de US$ {diagnostics.base_value:,.0f}"
    )
    figure.savefig(figure_path, dpi=160, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return {
        "global_importance": global_path,
        "local_explanations": local_path,
        "metadata": metadata_path,
        "figure": figure_path,
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--background-size", type=int, default=50)
    parser.add_argument("--explanation-size", type=int)
    parser.add_argument(
        "--permutation-cycles",
        type=int,
        default=DEFAULT_PERMUTATION_CYCLES,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    outputs = write_shap_artifacts(
        args.project_root,
        args.output_dir,
        background_size=args.background_size,
        explanation_size=args.explanation_size,
        permutation_cycles=args.permutation_cycles,
    )
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
