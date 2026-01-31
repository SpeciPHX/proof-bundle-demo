from __future__ import annotations

import numpy as np

def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(yt - yp)))

def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((yt - yp) ** 2)))

def baseline_win(primary_metric: str, baseline_value: float, candidate_value: float, min_improvement_frac: float = 0.02) -> bool:
    name = primary_metric.strip().lower()
    if name in {"mae", "rmse"}:
        return candidate_value <= baseline_value * (1.0 - float(min_improvement_frac))
    return candidate_value < baseline_value
