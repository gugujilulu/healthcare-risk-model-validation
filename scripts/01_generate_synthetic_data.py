#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cohort import assert_no_patient_leakage
from src.synthetic import generate_synthetic_screening_data


def main():
    out = ROOT / "data" / "synthetic" / "screening_demo.csv"
    df = generate_synthetic_screening_data()
    assert_no_patient_leakage(df)
    df.to_csv(out, index=False)

    qa = []
    for h in range(1, 6):
        d = df[df[f"eligible_{h}yr"] == 1]
        qa.append({
            "horizon": f"{h}yr",
            "eligible_exams": len(d),
            "cases": int(d[f"label_{h}yr"].sum()),
            "event_rate": float(d[f"label_{h}yr"].mean()),
        })
    import pandas as pd
    pd.DataFrame(qa).to_csv(ROOT / "results" / "tables" / "synthetic_cohort_qa.csv", index=False)
    print(f"Saved {out} ({len(df):,} exams; {df.patient_id.nunique():,} patients)")


if __name__ == "__main__":
    main()
