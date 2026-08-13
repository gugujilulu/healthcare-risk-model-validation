#!/usr/bin/env python3
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.decision_curve import decision_curve
from src.plotting import plot_auc_comparison, plot_bootstrap_ci, plot_calibration, plot_decision_curve, plot_temporal


def main():
    tables = ROOT / "results" / "tables"
    figs = ROOT / "results" / "figures"
    summary = pd.read_csv(tables / "locked_test_model_summary.csv")
    pred = pd.read_csv(tables / "locked_test_predictions.csv")
    boot = pd.read_csv(tables / "bootstrap_improvement_ci.csv")
    temporal = pd.read_csv(tables / "temporal_validation.csv")
    plot_auc_comparison(summary, figs / "auc_comparison.svg")
    plot_calibration(pred, "5yr", figs / "calibration_5yr.svg")
    plot_bootstrap_ci(boot, figs / "bootstrap_delta_auc_ci.svg")
    plot_temporal(temporal, figs / "temporal_validation.svg")
    for hz in ["1yr", "5yr"]:
        dca = pd.read_csv(tables / f"decision_curve_{hz}.csv")
        plot_decision_curve(dca, figs / f"decision_curve_{hz}.svg", title=f"Synthetic demo: decision curve ({hz})")
    print(f"Saved figures to {figs}")


if __name__ == "__main__":
    main()
