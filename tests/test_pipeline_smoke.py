import pandas as pd

from src.cohort import assert_no_patient_leakage
from src.synthetic import generate_synthetic_screening_data


def test_small_synthetic_pipeline_runs():
    df = generate_synthetic_screening_data(n_patients=300, seed=321)
    assert len(df) > 0
    assert df["patient_id"].nunique() > 0
    assert_no_patient_leakage(df)

    for h in range(1, 6):
        assert f"eligible_{h}yr" in df.columns
        assert f"label_{h}yr" in df.columns
        eligible = df[f"eligible_{h}yr"] == 1
        if eligible.any():
            assert pd.to_numeric(df.loc[eligible, f"label_{h}yr"], errors="raise").notna().all()
