#!/usr/bin/env python3
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import calibration_table, discrimination_calibration_metrics


def main():
    df = pd.read_csv(ROOT / "data" / "synthetic" / "screening_demo.csv")
    rows = []
    cal = []
    for h in range(1, 6):
        ecol, ycol, pcol = f"eligible_{h}yr", f"label_{h}yr", f"mirai_risk_{h}yr"
        d = df[(df[ecol] == 1) & df[ycol].notna()].copy()
        met = discrimination_calibration_metrics(d[ycol].astype(int), d[pcol].astype(float))
        rows.append({"horizon": f"{h}yr", "horizon_years": h, **met})
        c = calibration_table(d[ycol].astype(int), d[pcol].astype(float))
        c.insert(0, "horizon", f"{h}yr")
        cal.append(c)
    pd.DataFrame(rows).to_csv(ROOT / "results" / "tables" / "external_validation_metrics.csv", index=False)
    pd.concat(cal, ignore_index=True).to_csv(ROOT / "results" / "tables" / "external_validation_calibration.csv", index=False)
    print(pd.DataFrame(rows)[["horizon", "n", "cases", "auc", "brier", "e_o_ratio"]].to_string(index=False))


if __name__ == "__main__":
    main()
