"""SYNTHETIC data: lipids in series with series-specific offsets, so random splits leak series information."""
import numpy as np
from research.lnp_shift import shift


def data(seed=0, n_series=20, per=60):
    rng = np.random.default_rng(seed); g = np.repeat(np.arange(n_series), per); off = rng.normal(0, 2, n_series)[g]
    X = rng.normal(size=(len(g), 3)); y = X @ [1, -1, 0.5] + off + rng.normal(0, 0.3, len(g)); return X, y, g


def test_random_split_covers_near_nominal():
    X, y, g = data(); c = np.mean([shift.coverage(X, y, g, "random", s) for s in range(10)]); assert abs(c - 0.9) < 0.05


def test_group_split_under_covers_when_series_shift():
    X, y, g = data(); c = np.mean([shift.coverage(X, y, g, "group", s) for s in range(10)]); assert c < 0.85
