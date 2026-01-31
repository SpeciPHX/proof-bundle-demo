from __future__ import annotations

import numpy as np
import pandas as pd

def baseline_moving_average(train: pd.DataFrame, test: pd.DataFrame, window: int = 12) -> np.ndarray:
    y_all = pd.concat([train["y"], test["y"]], ignore_index=True)
    preds = []
    start = len(train)
    for i in range(start, start + len(test)):
        lo = max(0, i - window)
        preds.append(float(y_all.iloc[lo:i].mean()))
    return np.asarray(preds, dtype=float)
