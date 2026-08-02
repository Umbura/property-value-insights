"""Reusable exploratory analysis and merge-quality helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .data_contract import validate_demographics_frame, validate_historical_frame


@dataclass(frozen=True)
class MergeAudit:
    """Cardinality and coverage facts for the property-demographics merge."""

    historical_rows: int
    merged_rows: int
    demographic_rows: int
    historical_zipcodes: int
    matched_zipcodes: int
    unmatched_rows: int

    @property
    def row_retention_pct(self) -> float:
        """Return the percentage of historical rows retained by the merge."""

        if self.historical_rows == 0:
            return 0.0
        return self.merged_rows / self.historical_rows * 100

    @property
    def zipcode_coverage_pct(self) -> float:
        """Return the percentage of historical ZIP codes with a lookup row."""

        if self.historical_zipcodes == 0:
            return 0.0
        return self.matched_zipcodes / self.historical_zipcodes * 100


def merge_historical_with_demographics(
    historical: pd.DataFrame,
    demographics: pd.DataFrame,
) -> tuple[pd.DataFrame, MergeAudit]:
    """Merge historical properties with one demographic row per ZIP code."""

    validate_historical_frame(historical)
    validate_demographics_frame(demographics)

    historical_zipcodes = set(historical["zipcode"].astype("string"))
    demographic_zipcodes = set(demographics["zipcode"].astype("string"))
    matched_zipcodes = historical_zipcodes & demographic_zipcodes

    merged = historical.merge(
        demographics,
        on="zipcode",
        how="left",
        validate="many_to_one",
        indicator=True,
        suffixes=("", "_demographics"),
    )
    unmatched_rows = int((merged["_merge"] == "left_only").sum())
    merged = merged.drop(columns="_merge")

    audit = MergeAudit(
        historical_rows=len(historical),
        merged_rows=len(merged),
        demographic_rows=len(demographics),
        historical_zipcodes=len(historical_zipcodes),
        matched_zipcodes=len(matched_zipcodes),
        unmatched_rows=unmatched_rows,
    )
    return merged, audit


def quality_summary(frame: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Return a compact quality summary for a dataset."""

    return pd.DataFrame(
        [
            {
                "dataset": dataset_name,
                "rows": len(frame),
                "columns": len(frame.columns),
                "missing_cells": int(frame.isna().sum().sum()),
                "exact_duplicate_rows": int(frame.duplicated(keep=False).sum()),
                "unique_zipcodes": int(frame["zipcode"].nunique())
                if "zipcode" in frame.columns
                else None,
            }
        ]
    )


def iqr_outlier_summary(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Summarize IQR outliers for selected numeric columns."""

    summaries = []
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce").dropna()
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = values[(values < lower) | (values > upper)]
        summaries.append(
            {
                "column": column,
                "q1": q1,
                "q3": q3,
                "lower_bound": lower,
                "upper_bound": upper,
                "outlier_rows": len(outliers),
                "outlier_pct": len(outliers) / len(values) * 100 if len(values) else 0.0,
            }
        )
    return pd.DataFrame(summaries)


def numeric_correlations(
    frame: pd.DataFrame,
    target: str = "price",
    top_n: int = 10,
) -> pd.DataFrame:
    """Return the strongest numeric Pearson correlations with a target."""

    numeric = frame.select_dtypes(include="number")
    correlations = numeric.corr(numeric_only=True)[target].drop(labels=target)
    result = correlations.abs().sort_values(ascending=False).head(top_n).index
    return (
        correlations.loc[result]
        .rename("correlation")
        .to_frame()
        .assign(abs_correlation=lambda data: data["correlation"].abs())
        .reset_index(names="feature")
    )


def write_quality_report(
    output_path: str | Path,
    *,
    audit: MergeAudit,
    quality: pd.DataFrame,
    outliers: pd.DataFrame,
    correlations: pd.DataFrame,
    duplicate_id_keys: int = 0,
    exact_duplicate_rows: int = 0,
) -> None:
    """Write the reproducible quality findings as a Markdown report."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Relatorio de EDA e qualidade dos dados",
        "",
        "## Qualidade estrutural",
        "",
        quality.to_markdown(index=False),
        "",
        "## Merge por CEP",
        "",
        f"- Linhas historicas: {audit.historical_rows:,}.",
        f"- Linhas apos o merge: {audit.merged_rows:,}.",
        f"- Retencao de linhas: {audit.row_retention_pct:.2f}%.",
        f"- CEPs historicos: {audit.historical_zipcodes}.",
        f"- CEPs com correspondencia: {audit.matched_zipcodes}.",
        f"- Cobertura de CEP: {audit.zipcode_coverage_pct:.2f}%.",
        f"- Linhas sem correspondencia: {audit.unmatched_rows}.",
        f"- Chaves de ID repetidas: {duplicate_id_keys}.",
        f"- Linhas inteiramente duplicadas: {exact_duplicate_rows}.",
        "",
        "O merge foi configurado como muitos-para-um. Nenhuma linha historica e",
        "removida automaticamente.",
        "",
        "## Outliers pelo criterio IQR",
        "",
        outliers.to_markdown(index=False),
        "",
        "## Correlacoes numericas com o preco",
        "",
        correlations.to_markdown(index=False),
        "",
        "## Decisoes para a modelagem",
        "",
        "- `id` sera mantido para rastreabilidade, mas excluido das features.",
        "- `date` sera usada para ordenacao e separacao temporal, nao como feature",
        "  final, pois nao aparece nos exemplos futuros.",
        "- `zipcode` sera tratado como categoria e os dados demograficos serao",
        "  avaliados com estudo de ablation.",
        "- Outliers serao investigados e nao removidos apenas por regra estatistica.",
        "",
    ]
    destination.write_text("\n".join(lines), encoding="utf-8")
