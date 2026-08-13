from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score

EPS = 1e-6


def clip_prob(p):
    return np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)


def logit(p):
    p = clip_prob(p)
    return np.log(p / (1 - p))


def discrimination_calibration_metrics(y_true, y_prob) -> dict:
    y = np.asarray(y_true, dtype=int)
    p = clip_prob(y_prob)
    n = len(y)
    cases = int(y.sum())

    auc = roc_auc_score(y, p) if 0 < cases < n else np.nan
    brier = brier_score_loss(y, p) if n else np.nan
    expected = float(p.sum())
    observed = float(cases)
    e_o = expected / observed if observed > 0 else np.nan

    intercept = slope = np.nan
    if 0 < cases < n:
        model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        model.fit(logit(p).reshape(-1, 1), y)
        intercept = float(model.intercept_[0])
        slope = float(model.coef_[0][0])

    return {
        "n": n,
        "cases": cases,
        "event_rate": observed / n if n else np.nan,
        "auc": float(auc) if np.isfinite(auc) else np.nan,
        "brier": float(brier) if np.isfinite(brier) else np.nan,
        "expected_cases": expected,
        "observed_cases": observed,
        "e_o_ratio": float(e_o) if np.isfinite(e_o) else np.nan,
        "calibration_intercept": intercept,
        "calibration_slope": slope,
    }


def calibration_table(y_true, y_prob, n_bins: int = 10) -> pd.DataFrame:
    d = pd.DataFrame({"y": np.asarray(y_true, dtype=int), "p": clip_prob(y_prob)})
    q = min(n_bins, max(2, len(d) // 20))
    d["risk_bin"] = pd.qcut(d["p"].rank(method="first"), q, labels=False) + 1
    out = (
        d.groupby("risk_bin", observed=False)
        .agg(
            n=("y", "size"),
            observed_cases=("y", "sum"),
            mean_predicted_risk=("p", "mean"),
            min_predicted_risk=("p", "min"),
            max_predicted_risk=("p", "max"),
        )
        .reset_index()
    )
    out["observed_event_rate"] = out["observed_cases"] / out["n"]
    out["abs_calibration_error"] = (
        out["mean_predicted_risk"] - out["observed_event_rate"]
    ).abs()
    return out


def top_risk_capture(y_true, y_prob, top_percent=(1, 2, 5, 10)) -> pd.DataFrame:
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(y_prob, dtype=float)
    overall = y.mean()
    rows = []
    for pct in top_percent:
        cutoff = np.quantile(p, 1 - pct / 100)
        mask = p >= cutoff
        rate = y[mask].mean() if mask.any() else np.nan
        rows.append(
            {
                "top_percent": pct,
                "n_top": int(mask.sum()),
                "cases_top": int(y[mask].sum()),
                "event_rate_top": float(rate),
                "overall_event_rate": float(overall),
                "enrichment": float(rate / overall) if overall > 0 else np.nan,
                "case_capture": float(y[mask].sum() / y.sum()) if y.sum() else np.nan,
            }
        )
    return pd.DataFrame(rows)
