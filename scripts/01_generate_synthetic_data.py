#!/usr/bin/env python3
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cohort import assert_no_patient_leakage
from src.synthetic import generate_synthetic_screening_data


def _split_leakage_count(df: pd.DataFrame) -> int:
    counts = (
        df[["patient_id", "split"]]
        .drop_duplicates()
        .groupby("patient_id")["split"]
        .nunique()
    )
    return int((counts > 1).sum())


def main():
    out = ROOT / "data" / "synthetic" / "screening_demo.csv"
    df = generate_synthetic_screening_data()
    assert_no_patient_leakage(df)
    df.to_csv(out, index=False)

    exam_date = pd.to_datetime(df["exam_date"])
    followup_end = pd.to_datetime(df["followup_end"])
    cancer_date = pd.to_datetime(df["cancer_date"])
    followup_years = (followup_end - exam_date).dt.days / 365.25

    global_qa = {
        "min_followup_years": float(followup_years.min()),
        "max_followup_years": float(followup_years.max()),
        "n_patients": int(df["patient_id"].nunique()),
        "n_exams": int(len(df)),
        "mean_exams_per_patient": float(len(df) / df["patient_id"].nunique()),
        "exam_after_followup_violations": int((exam_date > followup_end).sum()),
        "cancer_after_followup_violations": int((cancer_date.notna() & (cancer_date > followup_end)).sum()),
        "patient_split_leakage_violations": _split_leakage_count(df),
    }

    qa = []
    for h in range(1, 6):
        eligible_mask = df[f"eligible_{h}yr"] == 1
        d = df.loc[eligible_mask]
        qa.append(
            {
                "horizon": f"{h}yr",
                "eligible_exams": int(len(d)),
                "cases": int(d[f"label_{h}yr"].sum()),
                "event_rate": float(d[f"label_{h}yr"].mean()),
                "excluded_short_followup": int((~eligible_mask).sum()),
                **global_qa,
            }
        )

    qa_df = pd.DataFrame(qa)
    qa_df.to_csv(ROOT / "results" / "tables" / "synthetic_cohort_qa.csv", index=False)

    # Small committed sample for inspection; the full synthetic cohort is
    # generated locally/CI and remains gitignored.
    sample_cols = [
        "patient_id",
        "exam_id",
        "exam_date",
        "screen_year",
        "cancer_date",
        "followup_end",
        "age",
        "density",
        "family_history",
        "prior_biopsy",
        "finding_mass",
        "finding_calcification",
        "finding_asymmetry",
        "result_category",
        *[f"mirai_risk_{h}yr" for h in range(1, 6)],
        *[x for h in range(1, 6) for x in (f"label_{h}yr", f"eligible_{h}yr")],
        "exam_order",
        "prior_exam_count",
        "is_first_exam",
        "split",
    ]
    df.loc[:, sample_cols].head(20).to_csv(
        ROOT / "data" / "synthetic" / "screening_demo_sample.csv", index=False
    )

    if any(qa_df[c].max() != 0 for c in [
        "exam_after_followup_violations",
        "cancer_after_followup_violations",
        "patient_split_leakage_violations",
    ]):
        raise AssertionError("Synthetic cohort QA detected a timeline or split violation")

    print(
        f"Saved {out} ({len(df):,} exams; {df.patient_id.nunique():,} patients; "
        f"mean {len(df) / df.patient_id.nunique():.2f} exams/patient)"
    )


if __name__ == "__main__":
    main()
