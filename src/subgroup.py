from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import discrimination_calibration_metrics


def add_public_subgroups(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["age_group"] = pd.cut(out["age"], [39, 49, 59, 69, 90], labels=["40-49", "50-59", "60-69", "70+"])
    return out


def evaluate_subgroups(df: pd.DataFrame, predictions: pd.DataFrame, horizon: int = 1, min_cases: int = 5) -> pd.DataFrame:
    hz = f"{horizon}yr"
    p = predictions[predictions["horizon"] == hz].copy()
    keys = ["patient_id", "exam_id"]
    meta_cols = keys + ["age", "density", "family_history"]
    d = p.merge(df[meta_cols].drop_duplicates(keys), on=keys, how="left")
    d = add_public_subgroups(d)
    rows = []
    for dimension in ["age_group", "density", "family_history"]:
        for group, g in d.groupby(dimension, dropna=False, observed=False):
            y = g["label"].astype(int).to_numpy()
            if y.sum() < min_cases or len(np.unique(y)) < 2:
                rows.append({"horizon": hz, "dimension": dimension, "subgroup": str(group), "n": len(g), "cases": int(y.sum()), "original_auc": np.nan, "adapted_auc": np.nan})
                continue
            m0 = discrimination_calibration_metrics(y, g["original_mirai"])
            m1 = discrimination_calibration_metrics(y, g["adapted_model"])
            rows.append({
                "horizon": hz,
                "dimension": dimension,
                "subgroup": str(group),
                "n": len(g),
                "cases": int(y.sum()),
                "original_auc": m0["auc"],
                "adapted_auc": m1["auc"],
                "delta_auc": m1["auc"] - m0["auc"],
                "original_e_o_ratio": m0["e_o_ratio"],
                "adapted_e_o_ratio": m1["e_o_ratio"],
            })
    return pd.DataFrame(rows)
