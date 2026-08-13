#!/usr/bin/env python3
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.post_screen import run_post_screen_triage


def main():
    df = pd.read_csv(ROOT / "data" / "synthetic" / "screening_demo.csv", parse_dates=["exam_date", "cancer_date", "followup_end"])
    summary, capture = run_post_screen_triage(df)
    summary.to_csv(ROOT / "results" / "tables" / "post_screen_triage.csv", index=False)
    capture.to_csv(ROOT / "results" / "tables" / "post_screen_top_risk_capture.csv", index=False)
    print(summary[["horizon", "auc", "brier", "e_o_ratio"]].to_string(index=False))


if __name__ == "__main__":
    main()
