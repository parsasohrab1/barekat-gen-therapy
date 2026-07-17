"""Survival model evaluation metrics."""

import numpy as np
import pandas as pd
from scipy import stats


def compute_recovery_histogram(
    recovery_days: pd.Series, bins: int = 20
) -> dict[str, list[float]]:
    counts, edges = np.histogram(recovery_days, bins=bins)
    return {
        "bins": [float(x) for x in edges.tolist()],
        "counts": [int(x) for x in counts.tolist()],
    }


def ks_test_recovery(real: pd.Series, synthetic: pd.Series) -> dict[str, float]:
    statistic, pvalue = stats.ks_2samp(real, synthetic)
    return {"ks_statistic": float(statistic), "ks_pvalue": float(pvalue)}
