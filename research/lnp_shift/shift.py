"""Coverage of split-conformal intervals under random versus group (chemical-series) splits."""
import numpy as np


def split(groups, mode, rng, frac=(0.6, 0.2)):
    n = len(groups); idx = np.arange(n)
    if mode == "random":
        rng.shuffle(idx)
    else:                                  # whole groups go to one part
        ug = np.unique(groups); rng.shuffle(ug); order = {g: i for i, g in enumerate(ug)}; idx = np.argsort([order[g] for g in groups], kind="stable")
    a, b = int(frac[0] * n), int((frac[0] + frac[1]) * n); return idx[:a], idx[a:b], idx[b:]


def coverage(X, y, groups, mode, seed=0, alpha=0.1):
    rng = np.random.default_rng(seed); tr, ca, te = split(groups, mode, rng)
    A = np.c_[X[tr], np.ones(len(tr))]; w = np.linalg.lstsq(A.T @ A + 1e-3 * np.eye(A.shape[1]), A.T @ y[tr], rcond=None)[0]
    f = lambda i: np.c_[X[i], np.ones(len(i))] @ w
    r = np.sort(np.abs(y[ca] - f(ca))); q = r[min(int(np.ceil((len(ca) + 1) * (1 - alpha))), len(ca)) - 1]
    return float((np.abs(y[te] - f(te)) <= q).mean())
