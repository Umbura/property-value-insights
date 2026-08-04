"""Evaluate empirical temporal prediction intervals for the approved model."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from .modeling import (
    fit_and_evaluate,
    regression_metrics,
    temporal_train_test_split,
    temporal_validation_predictions,
    vertical_equity_metrics,
)
from .stakeholder_reporting import validate_diagnostic_against_manifest
from .training import FEATURE_SET, approved_estimator, filter_temporally_consistent_rows


@dataclass(frozen=True)
class TemporalUncertaintyDiagnostics:
    """Calibrated interval scores and latest-period diagnostic results."""

    calibration_rows: pd.DataFrame
    diagnostic_rows: pd.DataFrame
    price_bands: pd.DataFrame
    calibration_folds: pd.DataFrame
    confidence_level: float
    quantile_level: float
    score_quantile: float
    metrics: dict[str, float]
    model_identity: dict[str, str]
    period_start: pd.Timestamp
    period_end: pd.Timestamp


def finite_sample_quantile_level(sample_size: int, confidence_level: float) -> float:
    """Return the finite-sample empirical quantile level for a target coverage."""

    if sample_size < 1:
        raise ValueError("sample_size must be positive")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")
    return min(1.0, ceil((sample_size + 1) * confidence_level) / sample_size)


def empirical_log_interval(
    predictions: pd.Series | np.ndarray,
    score_quantile: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a symmetric interval in log1p space and return it on the price scale."""

    values = np.asarray(predictions, dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("predictions must contain finite non-negative values")
    if not np.isfinite(score_quantile) or score_quantile < 0:
        raise ValueError("score_quantile must be finite and non-negative")
    center = np.log1p(values)
    lower = np.maximum(0.0, np.expm1(center - score_quantile))
    upper = np.expm1(center + score_quantile)
    return lower, upper


def evaluate_temporal_uncertainty(
    project_root: str | Path,
    *,
    confidence_level: float = 0.9,
) -> TemporalUncertaintyDiagnostics:
    """Calibrate on development folds and evaluate on the latest diagnostic period."""

    root = Path(project_root)
    historical_path = root / "data" / "raw" / "kc_house_data.csv"
    historical = pd.read_csv(historical_path, dtype={"zipcode": "string"})
    consistent, _ = filter_temporally_consistent_rows(historical)
    split = temporal_train_test_split(consistent, test_size=0.2)

    calibration = temporal_validation_predictions(
        approved_estimator(),
        split.train,
        feature_set=FEATURE_SET,
        n_splits=5,
    )
    calibration["log_absolute_error"] = np.abs(
        np.log1p(calibration["observed_price"])
        - np.log1p(calibration["predicted_price"])
    )
    quantile_level = finite_sample_quantile_level(len(calibration), confidence_level)
    score_quantile = float(
        np.quantile(
            calibration["log_absolute_error"],
            quantile_level,
            method="higher",
        )
    )

    evaluation = fit_and_evaluate(
        approved_estimator(),
        split.train,
        split.test,
        feature_set=FEATURE_SET,
    )
    observed = split.test["price"].astype(float).reset_index(drop=True)
    predicted = evaluation.predictions.astype(float).reset_index(drop=True)
    lower, upper = empirical_log_interval(predicted, score_quantile)
    diagnostic = pd.DataFrame(
        {
            "property_id": split.test["id"].reset_index(drop=True),
            "date": pd.to_datetime(
                split.test["date"].reset_index(drop=True),
                format="mixed",
                errors="raise",
            ),
            "observed_price": observed,
            "predicted_price": predicted,
            "lower_bound": lower,
            "upper_bound": upper,
        }
    )
    diagnostic["covered"] = diagnostic["observed_price"].between(
        diagnostic["lower_bound"], diagnostic["upper_bound"]
    )
    diagnostic["interval_width"] = (
        diagnostic["upper_bound"] - diagnostic["lower_bound"]
    )
    diagnostic["relative_width"] = (
        diagnostic["interval_width"] / diagnostic["predicted_price"].clip(lower=1.0)
    )
    diagnostic["price_band"] = pd.qcut(
        diagnostic["observed_price"],
        q=4,
        labels=["Q1", "Q2", "Q3", "Q4"],
    )

    price_bands = (
        diagnostic.groupby("price_band", observed=True)
        .agg(
            rows=("observed_price", "size"),
            observed_min=("observed_price", "min"),
            observed_max=("observed_price", "max"),
            coverage=("covered", "mean"),
            mean_width=("interval_width", "mean"),
            median_width=("interval_width", "median"),
            mean_relative_width=("relative_width", "mean"),
        )
        .reset_index()
    )
    calibration_folds = (
        calibration.groupby("fold", sort=True)
        .agg(
            rows=("log_absolute_error", "size"),
            train_end=("train_end", "first"),
            validation_start=("validation_start", "first"),
            validation_end=("validation_end", "first"),
            median_score=("log_absolute_error", "median"),
            mean_score=("log_absolute_error", "mean"),
            score_q90=(
                "log_absolute_error",
                lambda values: values.quantile(0.9, interpolation="higher"),
            ),
        )
        .reset_index()
    )
    metrics = {
        "coverage": float(diagnostic["covered"].mean()),
        "mean_width": float(diagnostic["interval_width"].mean()),
        "median_width": float(diagnostic["interval_width"].median()),
        "mean_relative_width": float(diagnostic["relative_width"].mean()),
    }
    diagnostic_metrics = {
        **regression_metrics(observed, predicted),
        **vertical_equity_metrics(observed, predicted),
    }
    period_end = diagnostic["date"].max()
    manifest = validate_diagnostic_against_manifest(
        root,
        diagnostic_metrics,
        len(diagnostic),
        split.test_start,
        pd.Timestamp(period_end),
        historical_path,
    )
    model = manifest["model"]
    return TemporalUncertaintyDiagnostics(
        calibration_rows=calibration,
        diagnostic_rows=diagnostic,
        price_bands=price_bands,
        calibration_folds=calibration_folds,
        confidence_level=confidence_level,
        quantile_level=quantile_level,
        score_quantile=score_quantile,
        metrics=metrics,
        model_identity={
            "name": str(model["name"]),
            "version": str(model["version"]),
            "artifact_sha256": str(manifest["artifact"]["sha256"]),
            "training_data_sha256": str(manifest["training_data"]["sha256"]),
        },
        period_start=split.test_start,
        period_end=pd.Timestamp(period_end),
    )


def write_uncertainty_artifacts(
    project_root: str | Path,
    output_dir: str | Path | None = None,
    *,
    confidence_level: float = 0.9,
) -> dict[str, Path]:
    """Write reproducible uncertainty tables, metadata and diagnostic figure."""

    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    root = Path(project_root)
    destination = Path(output_dir) if output_dir else root / "reports"
    figure_dir = destination / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = evaluate_temporal_uncertainty(
        root,
        confidence_level=confidence_level,
    )

    summary_path = destination / "uncertainty_summary.json"
    bands_path = destination / "uncertainty_by_price_band.csv"
    folds_path = destination / "uncertainty_calibration_folds.csv"
    figure_path = figure_dir / "uncertainty_diagnostic.png"

    diagnostics.price_bands.round(
        {
            "observed_min": 2,
            "observed_max": 2,
            "coverage": 6,
            "mean_width": 2,
            "median_width": 2,
            "mean_relative_width": 6,
        }
    ).to_csv(bands_path, index=False, encoding="utf-8", lineterminator="\n")
    folds = diagnostics.calibration_folds.copy()
    for column in ["train_end", "validation_start", "validation_end"]:
        folds[column] = pd.to_datetime(folds[column]).dt.date
    folds.round(
        {"median_score": 6, "mean_score": 6, "score_q90": 6}
    ).to_csv(folds_path, index=False, encoding="utf-8", lineterminator="\n")
    summary_path.write_text(
        json.dumps(
            {
                "method": "empirical_temporal_log_residual_interval",
                "status": "diagnostic_not_formal_coverage_guarantee",
                "model_identity": diagnostics.model_identity,
                "calibration": {
                    "folds": 5,
                    "rows": len(diagnostics.calibration_rows),
                    "confidence_level": diagnostics.confidence_level,
                    "finite_sample_quantile_level": diagnostics.quantile_level,
                    "log_absolute_error_quantile": diagnostics.score_quantile,
                },
                "diagnostic_period": {
                    "start": diagnostics.period_start.date().isoformat(),
                    "end": diagnostics.period_end.date().isoformat(),
                    "rows": len(diagnostics.diagnostic_rows),
                },
                "metrics": {
                    name: round(value, 6) for name, value in diagnostics.metrics.items()
                },
                "limitations": [
                    "Temporal dependence and distribution shift may change future coverage.",
                    "Coverage and interval width must be interpreted together.",
                    "The latest period is diagnostic because it was previously inspected.",
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    bands = diagnostics.price_bands
    positions = np.arange(len(bands))
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    figure.patch.set_facecolor("#F7F8F5")
    for axis in axes:
        axis.set_facecolor("#FFFFFF")
        axis.grid(axis="y", color="#D8DED8", linewidth=0.7, alpha=0.8)
        axis.spines[["top", "right"]].set_visible(False)

    axes[0].bar(positions, bands["coverage"] * 100, color="#176B66")
    axes[0].axhline(
        diagnostics.confidence_level * 100,
        color="#D1495B",
        linestyle="--",
        linewidth=1.6,
        label="Nível nominal",
    )
    axes[0].set_title("Cobertura por faixa de preço")
    axes[0].set_xlabel("Quartil do preço observado")
    axes[0].set_ylabel("Cobertura")
    axes[0].set_xticks(positions, bands["price_band"].astype(str))
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    axes[0].legend(frameon=False)

    axes[1].bar(positions, bands["mean_width"], color="#D9A441")
    axes[1].set_title("Largura média por faixa de preço")
    axes[1].set_xlabel("Quartil do preço observado")
    axes[1].set_ylabel("Largura do intervalo")
    axes[1].set_xticks(positions, bands["price_band"].astype(str))
    axes[1].yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"US$ {value / 1_000:.0f} mil")
    )
    figure.suptitle(
        "Intervalo empírico temporal do modelo aprovado\n"
        f"Nível nominal de {diagnostics.confidence_level:.0%} · "
        f"cobertura observada de {diagnostics.metrics['coverage']:.1%}"
    )
    figure.savefig(figure_path, dpi=160, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return {
        "summary": summary_path,
        "price_bands": bands_path,
        "calibration_folds": folds_path,
        "figure": figure_path,
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--confidence-level", type=float, default=0.9)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    outputs = write_uncertainty_artifacts(
        args.project_root,
        args.output_dir,
        confidence_level=args.confidence_level,
    )
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
