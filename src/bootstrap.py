from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def _weighted_metrics(y, p, w):
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    w = np.asarray(w, dtype=float)
    auc = roc_auc_score(y, p, sample_weight=w) if len(np.unique(y[w > 0])) == 2 else np.nan
    brier = np.average((y - p) ** 2, weights=w)
    observed = np.sum(w * y)
    expected = np.sum(w * p)
    eo = expected / observed if observed > 0 else np.nan
    return auc, brier, eo


def patient_cluster_bootstrap(
    predictions: pd.DataFrame,
    n_boot: int = 300,
    seed: int = 20260812,
) -> pd.DataFrame:
    """Paired patient-cluster bootstrap using patient multiplicity as row weights."""
    rng = np.random.default_rng(seed)
    rows = []
    for horizon, d in predictions.groupby("horizon"):
        d = d.copy()
        pats = d["patient_id"].astype(str)
        unique = pats.unique()
        patient_index = {p: i for i, p in enumerate(unique)}
        row_patient_idx = pats.map(patient_index).to_numpy()
        y = d["label"].astype(int).to_numpy()
        p0 = d["original_mirai"].astype(float).to_numpy()
        p1 = d["adapted_model"].astype(float).to_numpy()
        vals = []
        for _ in range(n_boot):
            sampled = rng.integers(0, len(unique), size=len(unique))
            counts = np.bincount(sampled, minlength=len(unique))
            w = counts[row_patient_idx]
            a0, b0, e0 = _weighted_metrics(y, p0, w)
            a1, b1, e1 = _weighted_metrics(y, p1, w)
            vals.append((a1-a0, b1-b0, abs(e1-1)-abs(e0-1)))
        bdf = pd.DataFrame(vals, columns=["delta_auc", "delta_brier", "delta_abs_eo_error"])
        row = {"horizon": horizon, "n_boot": n_boot}
        for metric in bdf.columns:
            s = bdf[metric].dropna()
            row[f"{metric}_mean"] = s.mean()
            row[f"{metric}_ci_low"] = s.quantile(.025)
            row[f"{metric}_ci_high"] = s.quantile(.975)
        row["pct_delta_auc_positive"] = float((bdf["delta_auc"] > 0).mean())
        rows.append(row)
    return pd.DataFrame(rows)
