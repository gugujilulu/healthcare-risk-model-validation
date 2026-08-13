from __future__ import annotations

import warnings
warnings.filterwarnings("ignore", message="X does not have valid feature names.*")

import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .calibration import PlattCalibrator
from .metrics import discrimination_calibration_metrics, top_risk_capture

POST_FEATURES = [
    "age",
    "density",
    "prior_exam_count",
    "finding_mass",
    "finding_calcification",
    "finding_asymmetry",
    "result_category",
]


def post_screen_feature_columns(horizon: int) -> list[str]:
    """Return the later-time triage feature set for one risk horizon."""
    if horizon not in (1, 2):
        raise ValueError("Post-screen public demo is defined for 1- and 2-year horizons")
    return [f"mirai_risk_{horizon}yr"] + POST_FEATURES


def run_post_screen_triage(df: pd.DataFrame, horizons=(1, 2), seed: int = 20260812):
    """Evaluate a separate later-time triage branch.

    This branch intentionally combines the horizon-specific fixed baseline risk
    with current findings/result category. It answers a post-screen short-
    horizon triage question and is never used as the main pre-screen adapter.
    """
    summaries = []
    captures = []
    for h in horizons:
        ecol, ycol = f"eligible_{h}yr", f"label_{h}yr"
        d = df[(df[ecol] == 1) & df[ycol].notna()].copy()
        tr, va, te = (d[d.split == s].copy() for s in ["train", "validation", "test"])
        feature_cols = post_screen_feature_columns(h)
        risk_col = f"mirai_risk_{h}yr"
        numeric = [
            risk_col,
            "age",
            "prior_exam_count",
            "finding_mass",
            "finding_calcification",
            "finding_asymmetry",
        ]
        categorical = ["density", "result_category"]
        prep = ColumnTransformer([
            ("num", SimpleImputer(strategy="median"), numeric),
            (
                "cat",
                Pipeline([
                    ("imp", SimpleImputer(strategy="most_frequent")),
                    ("oh", OneHotEncoder(handle_unknown="ignore")),
                ]),
                categorical,
            ),
        ])
        model = LGBMClassifier(
            objective="binary",
            n_estimators=120,
            learning_rate=.05,
            num_leaves=11,
            max_depth=4,
            min_child_samples=60,
            reg_lambda=1.0,
            random_state=seed + h,
            n_jobs=1,
            verbosity=-1,
        )
        pipe = Pipeline([("prep", prep), ("model", model)])
        pipe.fit(tr[feature_cols], tr[ycol].astype(int))
        pv = pipe.predict_proba(va[feature_cols])[:, 1]
        cal = PlattCalibrator().fit(pv, va[ycol].astype(int))
        pt = cal.predict(pipe.predict_proba(te[feature_cols])[:, 1])
        met = discrimination_calibration_metrics(te[ycol].astype(int), pt)
        summaries.append({"horizon": f"{h}yr", **met})
        cap = top_risk_capture(te[ycol].astype(int), pt)
        cap.insert(0, "horizon", f"{h}yr")
        captures.append(cap)
    return pd.DataFrame(summaries), pd.concat(captures, ignore_index=True)
