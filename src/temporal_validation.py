from __future__ import annotations

import warnings
warnings.filterwarnings("ignore", message="X does not have valid feature names.*")

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .calibration import PlattCalibrator
from .leakage_audit import PRE_SCREEN_FEATURES
from .metrics import discrimination_calibration_metrics


def temporal_periods(df: pd.DataFrame, horizon: int):
    ecol, ycol = f"eligible_{horizon}yr", f"label_{horizon}yr"
    d = df[(df[ecol] == 1) & df[ycol].notna()].copy()
    by_year = d.groupby("screen_year")[ycol].agg(["size", "sum"]).reset_index()
    usable = by_year[(by_year["size"] >= 100) & (by_year["sum"] >= 5) & ((by_year["size"] - by_year["sum"]) >= 100)]["screen_year"].astype(int).tolist()
    if len(usable) < 4:
        raise ValueError(f"Not enough temporally eligible years for {horizon}yr")
    # Use the latest eligible year(s) as future-period test, the immediately
    # preceding year as validation, and all earlier years as training.
    n_test = 2 if len(usable) >= 6 and horizon <= 3 else 1
    test_years = usable[-n_test:]
    val_year = usable[-n_test-1]
    train_years = usable[:-n_test-1]
    return train_years, [val_year], test_years


def _pipeline(model_name: str, numeric, categorical, seed):
    prep = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    if model_name == "logistic":
        model = LogisticRegression(max_iter=1500)
    else:
        model = LGBMClassifier(objective="binary", n_estimators=140, learning_rate=.04, num_leaves=11, max_depth=4, min_child_samples=60, reg_lambda=1.0, random_state=seed, n_jobs=1, verbosity=-1)
    return Pipeline([("prep", prep), ("model", model)])


def run_temporal_validation(df: pd.DataFrame, horizons=(1,2,3,4,5), seed: int = 20260812) -> pd.DataFrame:
    rows = []
    for h in horizons:
        train_years, val_years, test_years = temporal_periods(df, h)
        ecol, ycol, rcol = f"eligible_{h}yr", f"label_{h}yr", f"mirai_risk_{h}yr"
        d = df[(df[ecol] == 1) & df[ycol].notna()].copy()
        tr = d[d["screen_year"].isin(train_years)]
        va = d[d["screen_year"].isin(val_years)]
        te = d[d["screen_year"].isin(test_years)]
        if min(len(tr), len(va), len(te)) == 0 or te[ycol].sum() == 0:
            continue
        cols = [rcol] + PRE_SCREEN_FEATURES
        numeric = [c for c in cols if c not in {"density", "family_history", "prior_biopsy"}]
        categorical = [c for c in cols if c not in numeric]
        candidates = []
        for name in ["logistic", "lightgbm"]:
            pipe = _pipeline(name, numeric, categorical, seed+h)
            pipe.fit(tr[cols], tr[ycol].astype(int))
            pv = pipe.predict_proba(va[cols])[:,1]
            cal = PlattCalibrator().fit(pv, va[ycol].astype(int))
            mv = discrimination_calibration_metrics(va[ycol].astype(int), cal.predict(pv))
            candidates.append((mv["auc"], -mv["brier"], name, pipe, cal))
        _, _, name, pipe, cal = max(candidates, key=lambda x: (x[0], x[1]))
        pt = cal.predict(pipe.predict_proba(te[cols])[:,1])
        m0 = discrimination_calibration_metrics(te[ycol].astype(int), te[rcol].astype(float))
        m1 = discrimination_calibration_metrics(te[ycol].astype(int), pt)
        rows.append({
            "horizon": f"{h}yr",
            "train_years": f"{min(train_years)}-{max(train_years)}",
            "validation_years": ",".join(map(str, val_years)),
            "test_years": ",".join(map(str, test_years)),
            "selected_model": name,
            "original_auc": m0["auc"],
            "adapted_auc": m1["auc"],
            "delta_auc": m1["auc"] - m0["auc"],
            "original_brier": m0["brier"],
            "adapted_brier": m1["brier"],
            "adapted_e_o_ratio": m1["e_o_ratio"],
            "test_n": m1["n"],
            "test_cases": m1["cases"],
        })
    return pd.DataFrame(rows)
