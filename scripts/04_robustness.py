#!/usr/bin/env python3
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bootstrap import patient_cluster_bootstrap
from src.cohort import first_exam_only
from src.decision_curve import decision_curve
from src.metrics import discrimination_calibration_metrics
from src.subgroup import evaluate_subgroups


def main():
    df = pd.read_csv(ROOT / "data" / "synthetic" / "screening_demo.csv", parse_dates=["exam_date", "cancer_date", "followup_end"])
    pred = pd.read_csv(ROOT / "results" / "tables" / "locked_test_predictions.csv", parse_dates=["exam_date"])

    boot = patient_cluster_bootstrap(pred, n_boot=100)
    boot.to_csv(ROOT / "results" / "tables" / "bootstrap_improvement_ci.csv", index=False)

    subgroup = evaluate_subgroups(df, pred, horizon=1)
    subgroup.to_csv(ROOT / "results" / "tables" / "subgroup_robustness_1yr.csv", index=False)

    first = first_exam_only(pred)
    rows = []
    for hz, g in first.groupby("horizon"):
        m0 = discrimination_calibration_metrics(g["label"].astype(int), g["original_mirai"])
        m1 = discrimination_calibration_metrics(g["label"].astype(int), g["adapted_model"])
        rows.append({"horizon": hz, "n": len(g), "cases": int(g.label.sum()), "original_auc": m0["auc"], "adapted_auc": m1["auc"], "delta_auc": m1["auc"]-m0["auc"], "original_brier": m0["brier"], "adapted_brier": m1["brier"]})
    pd.DataFrame(rows).to_csv(ROOT / "results" / "tables" / "first_exam_sensitivity.csv", index=False)

    for hz, thresholds in [("1yr", np.linspace(.002, .08, 40)), ("5yr", np.linspace(.005, .25, 50))]:
        g = pred[pred.horizon == hz]
        dca = decision_curve(g["label"].astype(int), {"Baseline": g["original_mirai"].to_numpy(), "Updated": g["adapted_model"].to_numpy()}, thresholds)
        dca.insert(0, "horizon", hz)
        dca.to_csv(ROOT / "results" / "tables" / f"decision_curve_{hz}.csv", index=False)

    print(boot[["horizon", "delta_auc_mean", "delta_auc_ci_low", "delta_auc_ci_high"]].to_string(index=False))


if __name__ == "__main__":
    main()
