from __future__ import annotations

import numpy as np
import pandas as pd


def net_benefit(y_true, y_prob, threshold: float) -> float:
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(y_prob, dtype=float)
    pred = p >= threshold
    tp = np.sum(pred & (y == 1))
    fp = np.sum(pred & (y == 0))
    n = len(y)
    odds = threshold / (1 - threshold)
    return float(tp / n - fp / n * odds)


def decision_curve(y_true, predictions: dict[str, np.ndarray], thresholds) -> pd.DataFrame:
    y = np.asarray(y_true, dtype=int)
    rows = []
    for t in thresholds:
        treat_all = y.mean() - (1 - y.mean()) * t / (1 - t)
        rows.append({"threshold": t, "model": "Treat all", "net_benefit": treat_all})
        rows.append({"threshold": t, "model": "Treat none", "net_benefit": 0.0})
        for name, p in predictions.items():
            rows.append({"threshold": t, "model": name, "net_benefit": net_benefit(y, p, t)})
    return pd.DataFrame(rows)
