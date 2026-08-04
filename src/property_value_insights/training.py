"""Train, evaluate and package the approved property value model."""

from __future__ import annotations

import argparse
import platform
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any, Sequence

import joblib
import numpy as np
import pandas as pd
import sklearn

from .artifact import (
    ARTIFACT_SCHEMA_VERSION,
    create_model_bundle,
    load_model_bundle,
    predict_future,
    save_model_bundle,
    sha256_file,
    sha256_normalized_text_file,
    write_json,
)
from .data_contract import (
    HISTORICAL_COLUMNS,
    validate_future_frame,
    validate_historical_frame,
)
from .modeling import (
    build_estimator,
    cross_validate_temporal,
    feature_columns,
    fit_and_evaluate,
    regression_metrics,
    summarize_temporal_validation,
    temporal_train_test_split,
    vertical_equity_metrics,
)

MODEL_NAME = "property_value_hist_gradient_boosting_physical"
MODEL_VERSION = "0.4.0-rc1"
FEATURE_SET = "physical"
TARGET_TRANSFORM = "log_temporal_smearing"
MODEL_PARAMS: dict[str, object] = {"calibration_fraction": 0.1}


@dataclass(frozen=True)
class TemporalConsistencyAudit:
    """Training rows excluded because a property event occurs after its sale."""

    input_rows: int
    construction_after_sale_rows: int
    renovation_after_sale_rows: int
    excluded_rows: int
    retained_rows: int


def filter_temporally_consistent_rows(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, TemporalConsistencyAudit]:
    """Exclude rows containing construction or renovation years after sale."""

    validate_historical_frame(frame.loc[:, sorted(HISTORICAL_COLUMNS)])
    sale_year = pd.to_datetime(frame["date"], format="mixed", errors="raise").dt.year
    construction_after_sale = frame["yr_built"] > sale_year
    renovation_after_sale = (frame["yr_renovated"] > 0) & (
        frame["yr_renovated"] > sale_year
    )
    excluded = construction_after_sale | renovation_after_sale
    retained = frame.loc[~excluded].copy().reset_index(drop=True)
    audit = TemporalConsistencyAudit(
        input_rows=len(frame),
        construction_after_sale_rows=int(construction_after_sale.sum()),
        renovation_after_sale_rows=int(renovation_after_sale.sum()),
        excluded_rows=int(excluded.sum()),
        retained_rows=len(retained),
    )
    return retained, audit


def approved_estimator() -> object:
    """Build the physical-only calibrated estimator approved for packaging."""

    return build_estimator(
        "hist_gradient_boosting",
        FEATURE_SET,
        target_transform=TARGET_TRANSFORM,
        model_params=MODEL_PARAMS,
    )


def _json_metrics(metrics: dict[str, float]) -> dict[str, float]:
    return {name: round(float(value), 6) for name, value in metrics.items()}


def evaluate_model(frame: pd.DataFrame) -> dict[str, Any]:
    """Reproduce development validation and the latest-period diagnostic."""

    split = temporal_train_test_split(frame, test_size=0.2)
    validation = cross_validate_temporal(
        approved_estimator(),
        split.train,
        feature_set=FEATURE_SET,
        n_splits=5,
    )
    summary = summarize_temporal_validation({MODEL_NAME: validation}).iloc[0]
    diagnostic = fit_and_evaluate(
        approved_estimator(),
        split.train,
        split.test,
        feature_set=FEATURE_SET,
    )
    diagnostic_metrics = {
        **regression_metrics(split.test["price"], diagnostic.predictions),
        **vertical_equity_metrics(split.test["price"], diagnostic.predictions),
    }
    return {
        "protocol": "five expanding temporal folds on the development period",
        "folds": 5,
        "development_rows": len(split.train),
        "diagnostic_rows": len(split.test),
        "development_end": split.train_end.date().isoformat(),
        "diagnostic_start": split.test_start.date().isoformat(),
        "cross_validation": {
            "mae_mean": round(float(summary["cv_mae_mean"]), 6),
            "mae_std": round(float(summary["cv_mae_std"]), 6),
            "mae_worst": round(float(summary["cv_mae_worst"]), 6),
            "rmse_mean": round(float(summary["cv_rmse_mean"]), 6),
            "rmsle_mean": round(float(summary["cv_rmsle_mean"]), 6),
        },
        "latest_period_diagnostic": {
            **_json_metrics(diagnostic_metrics),
            "status": "diagnostic_only_previously_inspected",
        },
    }


def fit_final_model(frame: pd.DataFrame) -> object:
    """Fit the approved estimator on all chronologically ordered valid rows."""

    ordered = frame.assign(
        _parsed_date=pd.to_datetime(frame["date"], format="mixed", errors="raise")
    ).sort_values(["_parsed_date", "id"], kind="mergesort")
    features = feature_columns(FEATURE_SET)
    estimator = approved_estimator()
    estimator.fit(ordered[features], ordered["price"])
    return estimator


def _source_revision(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return "unavailable"
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def _manifest(
    *,
    project_root: Path,
    artifact_path: Path,
    predictions_path: Path,
    historical_path: Path,
    future_path: Path,
    training_frame: pd.DataFrame,
    audit: TemporalConsistencyAudit,
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    dates = pd.to_datetime(training_frame["date"], format="mixed", errors="raise")
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source_revision": _source_revision(project_root),
        "artifact": {
            "path": artifact_path.relative_to(project_root).as_posix(),
            "sha256": sha256_file(artifact_path),
        },
        "model": {
            "name": MODEL_NAME,
            "version": MODEL_VERSION,
            "feature_set": FEATURE_SET,
            "feature_columns": feature_columns(FEATURE_SET),
            "target_transform": TARGET_TRANSFORM,
            "parameters": MODEL_PARAMS,
            "algorithm": "HistGradientBoostingRegressor",
            "calibration": "smearing temporal nos 10% finais de cada treino",
            "selection_reason": (
                "Modelo somente físico selecionado após avaliação de governança porque "
                "a alternativa demográfica apresentou ganho marginal de MAE e introduziu "
                "risco de proxies socioeconômicas."
            ),
        },
        "training_data": {
            "path": historical_path.relative_to(project_root).as_posix(),
            "sha256": sha256_normalized_text_file(historical_path),
            "hash_normalization": "line endings normalized to LF",
            "date_start": dates.min().date().isoformat(),
            "date_end": dates.max().date().isoformat(),
            **asdict(audit),
        },
        "evaluation": evaluation,
        "prediction_output": {
            "path": predictions_path.relative_to(project_root).as_posix(),
            "sha256": sha256_normalized_text_file(predictions_path),
            "hash_normalization": "line endings normalized to LF",
            "rows": int(pd.read_csv(predictions_path).shape[0]),
            "source_path": future_path.relative_to(project_root).as_posix(),
            "source_sha256": sha256_normalized_text_file(future_path),
            "source_hash_normalization": "line endings normalized to LF",
        },
        "runtime": {
            "python": platform.python_version(),
            "property_value_insights": version("property-value-insights"),
            "scikit_learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "joblib": joblib.__version__,
        },
        "limitations": [
            "O período temporal mais recente foi consultado e possui uso diagnóstico.",
            "Os dados de treinamento cobrem uma região e um intervalo temporal limitado.",
            "Imóveis de maior valor mantêm erro absoluto e viés negativo mais elevados.",
            (
                "O CEP permanece como categoria geográfica e pode representar "
                "disparidades contextuais."
            ),
        ],
    }


def _write_training_summary(
    path: Path,
    *,
    audit: TemporalConsistencyAudit,
    evaluation: dict[str, Any],
    predictions: pd.DataFrame,
) -> None:
    cv = evaluation["cross_validation"]
    diagnostic = evaluation["latest_period_diagnostic"]
    lines = [
        "# Resumo do treinamento final",
        "",
        "## Decisão",
        "",
        "O artefato principal utiliza somente características físicas e espaciais. Os dados",
        "demográficos permanecem como experimento documentado e não entram no pipeline final.",
        "",
        "## Integridade temporal",
        "",
        f"- Linhas recebidas: {audit.input_rows:,}.",
        f"- Linhas excluídas: {audit.excluded_rows}.",
        f"- Linhas usadas no treinamento final: {audit.retained_rows:,}.",
        "- Motivo da exclusão: construção ou reforma registrada após a data da venda.",
        "",
        "## Avaliação reproduzida",
        "",
        f"- MAE temporal média: US$ {cv['mae_mean']:,.2f}.",
        f"- MAE no período diagnóstico: US$ {diagnostic['mae']:,.2f}.",
        f"- R² no período diagnóstico: {diagnostic['r2']:.4f}.",
        "- O período mais recente é diagnóstico, pois já havia sido consultado.",
        "",
        "## Inferência futura",
        "",
        f"- Previsões geradas: {len(predictions)}.",
        f"- Menor previsão: US$ {predictions['predicted_price'].min():,.2f}.",
        f"- Mediana das previsões: US$ {predictions['predicted_price'].median():,.2f}.",
        f"- Maior previsão: US$ {predictions['predicted_price'].max():,.2f}.",
        "",
        "As previsões não são métricas de acurácia porque os exemplos futuros não possuem alvo.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_training(project_root: str | Path) -> dict[str, Path]:
    """Execute the complete Phase 3 training and packaging workflow."""

    root = Path(project_root).resolve()
    data_dir = root / "data" / "raw"
    artifact_path = root / "artifacts" / "property_value_model.joblib"
    manifest_path = root / "artifacts" / "model_manifest.json"
    predictions_path = root / "reports" / "future_predictions.csv"
    summary_path = root / "reports" / "training_summary.md"
    historical_path = data_dir / "kc_house_data.csv"
    future_path = data_dir / "future_unseen_examples.csv"

    historical = pd.read_csv(historical_path, dtype={"zipcode": "string"})
    future = pd.read_csv(future_path, dtype={"zipcode": "string"})
    validate_historical_frame(historical)
    validate_future_frame(future)
    training_frame, audit = filter_temporally_consistent_rows(historical)
    evaluation = evaluate_model(training_frame)
    estimator = fit_final_model(training_frame)
    bundle = create_model_bundle(
        estimator,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        feature_columns=feature_columns(FEATURE_SET),
    )
    save_model_bundle(bundle, artifact_path)
    predictions = predict_future(bundle, future)
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(predictions_path, index=False, encoding="utf-8", lineterminator="\n")

    manifest = _manifest(
        project_root=root,
        artifact_path=artifact_path,
        predictions_path=predictions_path,
        historical_path=historical_path,
        future_path=future_path,
        training_frame=training_frame,
        audit=audit,
        evaluation=evaluation,
    )
    write_json(manifest_path, manifest)
    loaded = load_model_bundle(artifact_path, manifest_path=manifest_path)
    loaded_predictions = predict_future(loaded, future)
    if not predictions.equals(loaded_predictions):
        raise RuntimeError("Persisted artifact did not reproduce the generated predictions")
    _write_training_summary(
        summary_path,
        audit=audit,
        evaluation=evaluation,
        predictions=predictions,
    )
    return {
        "artifact": artifact_path,
        "manifest": manifest_path,
        "predictions": predictions_path,
        "summary": summary_path,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Run the training workflow from the command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing data/raw, artifacts and reports.",
    )
    args = parser.parse_args(argv)
    outputs = run_training(args.project_root)
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
