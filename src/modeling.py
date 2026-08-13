from __future__ import annotations

import warnings
warnings.filterwarnings("ignore", message="X does not have valid feature names.*")

from dataclasses import dataclass

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .calibration import make_calibrator
from .leakage_audit import PRE_SCREEN_FEATURES, assert_prediction_time_safe
from .metrics import discrimination_calibration_metrics


@dataclass
class SelectedModel:
    model_name: str
    calibration: str
    estimator: object
    calibrator: object
    feature_columns: list[str]


def feature_columns(horizon: int) -> list[str]:
    cols = [f"mirai_risk_{horizon}yr"] + PRE_SCREEN_FEATURES
    assert_prediction_time_safe(cols)
    return cols


def _preprocessor(df: pd.DataFrame, cols: list[str]):
    numeric = [c for c in cols if c not in {"density", "family_history", "prior_biopsy"}]
    categorical = [c for c in cols if c not in numeric]
    return ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])


def _make_estimator(name: str, df: pd.DataFrame, cols: list[str], seed: int):
    prep = _preprocessor(df, cols)
    if name == "logistic":
        model = LogisticRegression(C=1.0, max_iter=1500, class_weight=None, solver="lbfgs")
    elif name == "lightgbm":
        model = LGBMClassifier(objective="binary", n_estimators=180, learning_rate=0.035, num_leaves=15, max_depth=4, min_child_samples=60, subsample=0.85, colsample_bytree=0.85, reg_lambda=1.0, random_state=seed, n_jobs=4, verbosity=-1)
    else:
        raise ValueError(name)
    return Pipeline([("prep", prep), ("model", model)])


def _eligible(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    ycol = f"label_{horizon}yr"
    ecol = f"eligible_{horizon}yr"
    return df.loc[(df[ecol] == 1) & df[ycol].notna()].copy()


def split_validation_patients(df: pd.DataFrame, seed: int = 20260812):
    pats = df["patient_id"].astype(str).drop_duplicates().to_numpy()
    rng = np.random.default_rng(seed)
    rng.shuffle(pats)
    cut = max(1, len(pats) // 2)
    cal = set(pats[:cut])
    return df[df["patient_id"].astype(str).isin(cal)].copy(), df[~df["patient_id"].astype(str).isin(cal)].copy()


def _selection_score(metrics: dict) -> tuple:
    return (metrics["auc"], -metrics["brier"], -abs(metrics["e_o_ratio"] - 1))


def fit_locked_horizon(df: pd.DataFrame, horizon: int, candidate_models=("logistic", "lightgbm"), calibration_methods=("none", "platt", "isotonic", "beta_style"), seed: int = 20260812):
    """Select model/calibration without touching the final test set."""
    cols = feature_columns(horizon)
    d = _eligible(df, horizon)
    train = d[d["split"] == "train"].copy()
    val = d[d["split"] == "validation"].copy()
    test = d[d["split"] == "test"].copy()
    if min(len(train), len(val), len(test)) == 0:
        raise ValueError(f"Missing split data for horizon {horizon}")

    val_cal, val_select = split_validation_patients(val, seed + horizon)
    ycol = f"label_{horizon}yr"
    candidates = []

    for model_name in candidate_models:
        estimator = _make_estimator(model_name, train, cols, seed + horizon)
        estimator.fit(train[cols], train[ycol].astype(int))
        p_cal_raw = estimator.predict_proba(val_cal[cols])[:, 1]
        p_sel_raw = estimator.predict_proba(val_select[cols])[:, 1]

        for cal_name in calibration_methods:
            calibrator = make_calibrator(cal_name).fit(p_cal_raw, val_cal[ycol].astype(int).to_numpy())
            p_sel = calibrator.predict(p_sel_raw)
            met = discrimination_calibration_metrics(val_select[ycol].astype(int), p_sel)
            candidates.append({"model": model_name, "calibration": cal_name, **met, "_estimator": estimator, "_calibrator": calibrator})

    winner = max(candidates, key=lambda r: _selection_score(r))
    selected = SelectedModel(model_name=winner["model"], calibration=winner["calibration"], estimator=winner["_estimator"], calibrator=winner["_calibrator"], feature_columns=cols)

    p_test_raw = selected.estimator.predict_proba(test[cols])[:, 1]
    p_test = selected.calibrator.predict(p_test_raw)
    original = test[f"mirai_risk_{horizon}yr"].astype(float).to_numpy()

    return {
        "selected": selected,
        "selection_table": pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in candidates]),
        "test": test,
        "y_test": test[ycol].astype(int).to_numpy(),
        "p_original": original,
        "p_adapted": p_test,
        "original_metrics": discrimination_calibration_metrics(test[ycol].astype(int), original),
        "adapted_metrics": discrimination_calibration_metrics(test[ycol].astype(int), p_test),
    }


def fit_all_horizons(df: pd.DataFrame, horizons=(1, 2, 3, 4, 5), seed: int = 20260812):
    outputs, summary, predictions, selections = {}, [], [], []
    for h in horizons:
        out = fit_locked_horizon(df, h, seed=seed)
        outputs[h] = out
        om, am = out["original_metrics"], out["adapted_metrics"]
        summary.append({
            "horizon": f"{h}yr", "horizon_years": h,
            "selected_model": out["selected"].model_name,
            "selected_calibration": out["selected"].calibration,
            "original_auc": om["auc"], "adapted_auc": am["auc"], "delta_auc": am["auc"] - om["auc"],
            "original_brier": om["brier"], "adapted_brier": am["brier"], "delta_brier": am["brier"] - om["brier"],
            "original_e_o_ratio": om["e_o_ratio"], "adapted_e_o_ratio": am["e_o_ratio"],
            "adapted_calibration_intercept": am["calibration_intercept"], "adapted_calibration_slope": am["calibration_slope"],
            "test_n": am["n"], "test_cases": am["cases"],
        })
        pred = out["test"][["patient_id", "exam_id", "exam_date", "screen_year", "is_first_exam"]].copy()
        pred["horizon"] = f"{h}yr"; pred["label"] = out["y_test"]; pred["original_mirai"] = out["p_original"]; pred["adapted_model"] = out["p_adapted"]
        predictions.append(pred)
        st = out["selection_table"].copy(); st.insert(0, "horizon", f"{h}yr"); selections.append(st)
    return outputs, pd.DataFrame(summary), pd.concat(predictions, ignore_index=True), pd.concat(selections, ignore_index=True)
