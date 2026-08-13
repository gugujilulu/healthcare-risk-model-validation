#!/usr/bin/env python3
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.modeling import fit_all_horizons


def main():
    df = pd.read_csv(ROOT / "data" / "synthetic" / "screening_demo.csv", parse_dates=["exam_date", "cancer_date", "followup_end"])
    _, summary, predictions, selections = fit_all_horizons(df)
    summary.to_csv(ROOT / "results" / "tables" / "locked_test_model_summary.csv", index=False)
    predictions.to_csv(ROOT / "results" / "tables" / "locked_test_predictions.csv", index=False)
    selections.to_csv(ROOT / "results" / "tables" / "validation_model_selection.csv", index=False)
    print(summary[["horizon", "selected_model", "selected_calibration", "original_auc", "adapted_auc", "delta_auc"]].to_string(index=False))


if __name__ == "__main__":
    main()
