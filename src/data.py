from __future__ import annotations

import numpy as np
import pandas as pd


def make_synthetic_series(n: int = 240, seed: int = 0) -> pd.DataFrame:
    # Deterministic synthetic series: trend + sinusoid + regime shift + noise
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float)

    y = 0.02 * t + 0.2 * np.sin(2.0 * np.pi * t / 24.0)
    k = n // 2
    y[k:] = y[k:] + 1.0 + 0.04 * (t[k:] - float(k))

    y = y + rng.normal(loc=0.0, scale=0.15, size=n)
    return pd.DataFrame({"t": t, "y": y})


def train_test_split_time(df: pd.DataFrame, train_frac: float = 0.7):
    n = len(df)
    k = int(round(n * train_frac))
    return df.iloc[:k].copy(), df.iloc[k:].copy()
