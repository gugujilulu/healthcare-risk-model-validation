#!/usr/bin/env python3
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.temporal_validation import run_temporal_validation


def main():
    df = pd.read_csv(ROOT / "data" / "synthetic" / "screening_demo.csv", parse_dates=["exam_date", "cancer_date", "followup_end"])
    out = run_temporal_validation(df)
    out.to_csv(ROOT / "results" / "tables" / "temporal_validation.csv", index=False)
    print(out[["horizon", "selected_model", "original_auc", "adapted_auc", "delta_auc"]].to_string(index=False))


if __name__ == "__main__":
    main()
