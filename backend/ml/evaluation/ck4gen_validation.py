"""CK4Gen validation metrics for synthetic clinical data."""

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from scipy import stats

from ml.evaluation.metrics import ks_test_recovery
from ml.survival.coxph import DURATION_COL, EVENT_COL, FEATURE_COLUMNS, prepare_features

CLINICAL_COLS = ["Age", "Disease_Severity", "Gene_5_Mutation", "Gene_12_Mutation", "Gene_18_Expr"]


def correlation_preservation(
    source: pd.DataFrame, synthetic: pd.DataFrame, columns: list[str] | None = None
) -> dict[str, float]:
    cols = columns or [c for c in CLINICAL_COLS if c in source.columns and c in synthetic.columns]
    if len(cols) < 2:
        return {"mean_abs_corr_diff": 0.0, "max_abs_corr_diff": 0.0}

    src_corr = source[cols].astype(float).corr().values
    syn_corr = synthetic[cols].astype(float).corr().values
    diff = np.abs(src_corr - syn_corr)
    upper = diff[np.triu_indices_from(diff, k=1)]
    return {
        "mean_abs_corr_diff": float(np.mean(upper)),
        "max_abs_corr_diff": float(np.max(upper)),
    }


def evaluate_c_index(model: CoxPHFitter, df: pd.DataFrame) -> float:
    prepared = prepare_features(df)
    eval_df = prepared[FEATURE_COLUMNS + [DURATION_COL, EVENT_COL]].dropna()
    if len(eval_df) < 10:
        return 0.0
    return float(model.score(eval_df, scoring_method="concordance_index"))


def validate_ck4gen(
    source_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    cox_model: CoxPHFitter,
    source_c_index: float,
    ks_alpha: float = 0.05,
    max_c_index_gap: float = 0.1,
    max_corr_diff: float = 0.25,
) -> dict:
    ks = ks_test_recovery(
        source_df[DURATION_COL].astype(float),
        synthetic_df[DURATION_COL].astype(float),
    )
    corr = correlation_preservation(source_df, synthetic_df)
    synthetic_c_index = evaluate_c_index(cox_model, synthetic_df)
    c_index_gap = abs(source_c_index - synthetic_c_index)

    checks = {
        "ks_test_passed": ks["ks_pvalue"] >= ks_alpha,
        "correlation_preserved": corr["mean_abs_corr_diff"] <= max_corr_diff,
        "c_index_preserved": c_index_gap <= max_c_index_gap,
        "all_records_synthetic": bool(synthetic_df["synthetic"].all())
        if "synthetic" in synthetic_df.columns
        else False,
    }

    return {
        "ks_statistic": ks["ks_statistic"],
        "ks_pvalue": ks["ks_pvalue"],
        "correlation": corr,
        "source_c_index": source_c_index,
        "synthetic_c_index": synthetic_c_index,
        "c_index_gap": c_index_gap,
        "checks": checks,
        "accepted": all(checks.values()),
    }
