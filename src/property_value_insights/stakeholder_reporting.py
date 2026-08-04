"""Reproduce stakeholder-facing diagnostics for the approved model."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from .modeling import (
    fit_and_evaluate,
    median_baseline_prediction,
    regression_metrics,
    temporal_train_test_split,
    vertical_equity_metrics,
)
from .training import FEATURE_SET, approved_estimator, filter_temporally_consistent_rows


@dataclass(frozen=True)
class StakeholderDiagnostics:
    """Predictions and summaries for the latest diagnostic period."""

    rows: pd.DataFrame
    price_bands: pd.DataFrame
    metrics: dict[str, float]
    baseline_metrics: dict[str, float]
    period_start: pd.Timestamp
    period_end: pd.Timestamp


def evaluate_stakeholder_diagnostics(project_root: str | Path) -> StakeholderDiagnostics:
    """Recreate the approved model's latest-period diagnostic results."""

    root = Path(project_root)
    historical = pd.read_csv(
        root / "data" / "raw" / "kc_house_data.csv",
        dtype={"zipcode": "string"},
    )
    consistent, _ = filter_temporally_consistent_rows(historical)
    split = temporal_train_test_split(consistent, test_size=0.2)
    evaluation = fit_and_evaluate(
        approved_estimator(),
        split.train,
        split.test,
        feature_set=FEATURE_SET,
    )
    observed = split.test["price"].astype(float).reset_index(drop=True)
    predicted = evaluation.predictions.astype(float).reset_index(drop=True)
    rows = pd.DataFrame(
        {
            "observed_price": observed,
            "predicted_price": predicted,
            "signed_error": predicted - observed,
            "absolute_error": (predicted - observed).abs(),
        }
    )
    rows["price_band"] = pd.qcut(
        rows["observed_price"],
        q=4,
        labels=["Q1", "Q2", "Q3", "Q4"],
    )
    price_bands = (
        rows.groupby("price_band", observed=True)
        .agg(
            rows=("observed_price", "size"),
            observed_min=("observed_price", "min"),
            observed_max=("observed_price", "max"),
            mae=("absolute_error", "mean"),
            mean_error=("signed_error", "mean"),
            underprediction_rate=("signed_error", lambda values: float((values < 0).mean())),
        )
        .reset_index()
    )
    metrics = {
        **regression_metrics(observed, predicted),
        **vertical_equity_metrics(observed, predicted),
    }
    baseline = median_baseline_prediction(split.train, split.test).reset_index(drop=True)
    baseline_metrics = regression_metrics(observed, baseline)
    _validate_against_manifest(root, metrics, len(rows), split.test_start)
    period_end = pd.to_datetime(split.test["date"], format="mixed", errors="raise").max()
    return StakeholderDiagnostics(
        rows=rows,
        price_bands=price_bands,
        metrics=metrics,
        baseline_metrics=baseline_metrics,
        period_start=split.test_start,
        period_end=pd.Timestamp(period_end),
    )


def _validate_against_manifest(
    project_root: Path,
    metrics: dict[str, float],
    rows: int,
    period_start: pd.Timestamp,
) -> None:
    manifest = json.loads(
        (project_root / "artifacts" / "model_manifest.json").read_text(encoding="utf-8")
    )
    evaluation = manifest["evaluation"]
    expected = evaluation["latest_period_diagnostic"]
    if rows != evaluation["diagnostic_rows"]:
        raise ValueError("Diagnostic row count does not match the model manifest")
    if period_start.date().isoformat() != evaluation["diagnostic_start"]:
        raise ValueError("Diagnostic period does not match the model manifest")
    for name, value in metrics.items():
        if name in expected and not np.isclose(value, expected[name], rtol=0, atol=1e-6):
            raise ValueError(f"Diagnostic metric {name} does not match the model manifest")


def write_stakeholder_artifacts(
    project_root: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write the diagnostic figure and segment table used by the business summary."""

    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    root = Path(project_root)
    destination = Path(output_dir) if output_dir else root / "reports"
    figure_dir = destination / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = evaluate_stakeholder_diagnostics(root)

    figure_path = figure_dir / "approved_model_diagnostic.png"
    table_path = destination / "approved_model_price_bands.csv"
    metrics_path = destination / "approved_model_stakeholder_metrics.json"
    diagnostics.price_bands.assign(
        observed_min=lambda frame: frame["observed_min"].round(2),
        observed_max=lambda frame: frame["observed_max"].round(2),
        mae=lambda frame: frame["mae"].round(2),
        mean_error=lambda frame: frame["mean_error"].round(2),
        underprediction_rate=lambda frame: frame["underprediction_rate"].round(6),
    ).to_csv(table_path, index=False)
    metrics_path.write_text(
        json.dumps(
            {
                "period": {
                    "start": diagnostics.period_start.date().isoformat(),
                    "end": diagnostics.period_end.date().isoformat(),
                    "rows": len(diagnostics.rows),
                    "status": "diagnostic_only_previously_inspected",
                },
                "model": {name: round(value, 6) for name, value in diagnostics.metrics.items()},
                "median_baseline": {
                    name: round(value, 6)
                    for name, value in diagnostics.baseline_metrics.items()
                },
                "comparison": {
                    "mae_reduction_pct": round(
                        100
                        * (
                            1
                            - diagnostics.metrics["mae"]
                            / diagnostics.baseline_metrics["mae"]
                        ),
                        6,
                    ),
                    "rmse_reduction_pct": round(
                        100
                        * (
                            1
                            - diagnostics.metrics["rmse"]
                            / diagnostics.baseline_metrics["rmse"]
                        ),
                        6,
                    ),
                },
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    currency = FuncFormatter(lambda value, _: f"US$ {value / 1_000_000:.1f} mi")
    figure, axes = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)
    figure.patch.set_facecolor("#F7F8F5")
    for axis in axes:
        axis.set_facecolor("#FFFFFF")
        axis.grid(axis="y", color="#D8DED8", linewidth=0.7, alpha=0.8)
        axis.spines[["top", "right"]].set_visible(False)

    maximum = float(
        max(
            diagnostics.rows["observed_price"].max(),
            diagnostics.rows["predicted_price"].max(),
        )
    )
    axes[0].scatter(
        diagnostics.rows["observed_price"],
        diagnostics.rows["predicted_price"],
        s=12,
        alpha=0.28,
        color="#176B66",
        edgecolors="none",
    )
    axes[0].plot([0, maximum], [0, maximum], color="#D1495B", linestyle="--", linewidth=1.8)
    axes[0].set_title("Preço observado e estimado")
    axes[0].set_xlabel("Preço observado")
    axes[0].set_ylabel("Preço estimado")
    axes[0].xaxis.set_major_formatter(currency)
    axes[0].yaxis.set_major_formatter(currency)

    bands = diagnostics.price_bands
    positions = np.arange(len(bands))
    width = 0.36
    axes[1].bar(
        positions - width / 2,
        bands["mae"],
        width,
        label="Erro absoluto médio",
        color="#176B66",
    )
    axes[1].bar(
        positions + width / 2,
        bands["mean_error"],
        width,
        label="Viés médio",
        color="#D1495B",
    )
    axes[1].axhline(0, color="#2F3E46", linewidth=0.9)
    axes[1].set_title("Erro por faixa de preço")
    axes[1].set_xlabel("Quartil do preço observado")
    axes[1].set_ylabel("Valor em dólares")
    axes[1].set_xticks(positions, bands["price_band"].astype(str))
    axes[1].yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"US$ {value / 1_000:.0f} mil")
    )
    axes[1].legend(frameon=False, loc="upper left")

    figure.suptitle(
        "Diagnóstico temporal do modelo aprovado\n"
        f"{diagnostics.period_start:%d/%m/%Y} a {diagnostics.period_end:%d/%m/%Y} · "
        f"{len(diagnostics.rows):,} imóveis · período previamente inspecionado".replace(",", "."),
        fontsize=13,
    )
    figure.savefig(figure_path, dpi=160, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return {
        "figure": figure_path,
        "price_bands": table_path,
        "metrics": metrics_path,
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate reproducible stakeholder diagnostics for the approved model."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    outputs = write_stakeholder_artifacts(args.project_root, args.output_dir)
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
