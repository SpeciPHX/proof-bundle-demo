from __future__ import annotations

import numpy as np
import pandas as pd

def candidate_exp_smoothing(train: pd.DataFrame, test: pd.DataFrame, alpha: float = 0.35) -> np.ndarray:
    y_train = train["y"].to_numpy(dtype=float)
    y_test = test["y"].to_numpy(dtype=float)
    level = float(y_train[0])
    for v in y_train[1:]:
        level = alpha * float(v) + (1.0 - alpha) * level
    return np.full(shape=len(y_test), fill_value=level, dtype=float)
