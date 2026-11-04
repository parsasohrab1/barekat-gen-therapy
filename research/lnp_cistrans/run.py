"""Cis/trans lipid pairs in the LANTERN transfection table (real data, supplied separately).

Usage:
  python -m research.lnp_cistrans.run --xlsx LNPs_TE_SMILES_Transfection_Extract.xlsx \
      --out research/lnp_cistrans/results.json

Question 1: within lipid pairs that differ only in E/Z geometry and were measured under identical
conditions, is transfection different between cis and trans?
Question 2: does giving a random forest the stereo information help it order the two isomers of a
held-out pair? (leave-one-pair-out, whole structures held out)
The data file is not stored in the repository (licence of the LANTERN resource).
"""

from __future__ import annotations

import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor

from research.lnp_cistrans.stereo import (
    add_structure_columns,
    find_pairs,
    morgan_counts,
    stereo_features,
)

VALUE = "Transfection_Efficiency_normalized"
FEATURES = ("morgan_blind", "morgan_chirality", "morgan_blind+ZE")


def design(isos: list[str], kind: str) -> np.ndarray:
    if kind == "morgan_blind":
        return morgan_counts(isos, chirality=False)
    if kind == "morgan_chirality":
        return morgan_counts(isos, chirality=True)
    return np.c_[morgan_counts(isos, chirality=False), stereo_features(isos)]


def boot_ci(x: np.ndarray, fn, n: int = 5000, seed: int = 0) -> list[float]:
    rng = np.random.default_rng(seed)
    v = [fn(x[rng.integers(0, len(x), len(x))]) for _ in range(n)]
    return [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)]


def paired_stats(pairs: pd.DataFrame) -> dict:
    d = (pairs["y_cis"] - pairs["y_trans"]).to_numpy()
    nz = d[d != 0]
    k = int((nz > 0).sum())
    return {
        "n_pairs": len(d),
        "mean_diff_cis_minus_trans": round(float(d.mean()), 3),
        "median_diff": round(float(np.median(d)), 3),
        "mean_diff_ci95": boot_ci(d, np.mean),
        "median_diff_ci95": boot_ci(d, np.median),
        "cis_higher": k, "trans_higher": int(len(nz) - k),
        "sign_test_p": round(float(stats.binomtest(k, len(nz), 0.5).pvalue), 4),
        "wilcoxon_p": round(float(stats.wilcoxon(d).pvalue), 4),
        "sd_of_all_values_in_dataset": None,
    }


def leave_one_pair_out(d: pd.DataFrame, pairs: pd.DataFrame, seeds=(0, 1, 2, 3, 4)) -> dict:
    """d: one row per lipid (mean value over repeated rows). Whole flat-structure groups held out."""
    d = d.reset_index(drop=True)
    X = {k: design(d["iso"].tolist(), k) for k in FEATURES}
    y = d["y"].to_numpy()
    idx = {iso: i for i, iso in enumerate(d["iso"])}
    out = {k: {"order_correct": [], "rmse": []} for k in FEATURES}
    for p in pairs.itertuples():
        held = d.index[d["flat"] == p.flat].to_numpy()
        tr = np.setdiff1d(np.arange(len(d)), held)
        ic, it = idx[p.cis], idx[p.trans]
        for k in FEATURES:
            pc, pt = [], []
            for s in seeds:
                m = RandomForestRegressor(n_estimators=300, random_state=s, n_jobs=-1)
                m.fit(X[k][tr], y[tr])
                pr = m.predict(X[k][[ic, it]])
                pc.append(pr[0]); pt.append(pr[1])
            pc, pt = float(np.mean(pc)), float(np.mean(pt))
            truth = y[ic] - y[it]
            diff = pc - pt
            ok = 0.5 if abs(diff) < 1e-12 else float(np.sign(diff) == np.sign(truth))
            out[k]["order_correct"].append(ok)
            out[k]["rmse"].append(((pc - y[ic]) ** 2 + (pt - y[it]) ** 2) / 2)
    res = {}
    for k in FEATURES:
        oc = np.array(out[k]["order_correct"]); mse = np.array(out[k]["rmse"])
        res[k] = {
            "order_accuracy": round(float(oc.mean()), 3),
            "order_accuracy_ci95": boot_ci(oc, np.mean),
            "ties": int((oc == 0.5).sum()),
            "rmse_on_held_out_pairs": round(float(np.sqrt(mse.mean())), 3),
        }
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--out", default="research/lnp_cistrans/results.json")
    a = ap.parse_args()
    with open(a.xlsx, "rb") as fh:
        raw = fh.read()
    df = pd.read_excel(a.xlsx, sheet_name="SMILES_TE")
    s = add_structure_columns(df)
    pairs = find_pairs(df, VALUE)
    res: dict = {"file_sha256": hashlib.sha256(raw).hexdigest(), "rows": len(df),
                 "unique_structures": int(s["iso"].nunique()),
                 "pair_rows_by_dataset": pairs["Dataset"].value_counts().to_dict(),
                 "paired": paired_stats(pairs)}
    # Prediction analysis restricted to datasets that contain cis/trans pairs
    ds = pairs["Dataset"].unique().tolist()
    sub = s[s["Dataset"].isin(ds)]
    res["prediction_datasets"] = ds
    res["dataset_sd_normalized_te"] = {x: round(float(sub[sub.Dataset == x][VALUE].std()), 3) for x in ds}
    res["paired"]["sd_of_all_values_in_dataset"] = res["dataset_sd_normalized_te"]
    lip = sub.groupby(["iso", "flat"], as_index=False).agg(y=(VALUE, "mean"))
    res["n_lipids_in_prediction_set"] = len(lip)
    res["leave_one_pair_out"] = leave_one_pair_out(lip, pairs)
    dd = (pairs["y_cis"] - pairs["y_trans"]).to_numpy()
    res["constant_rules_order_accuracy"] = {
        "always_trans_higher": round(float(((dd < 0) + 0.5 * (dd == 0)).mean()), 3),
        "always_cis_higher": round(float(((dd > 0) + 0.5 * (dd == 0)).mean()), 3),
    }
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
