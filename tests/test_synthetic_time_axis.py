import numpy as np
import pandas as pd

from src.synthetic import generate_synthetic_screening_data


def test_no_exam_after_followup():
    df = generate_synthetic_screening_data(n_patients=500, seed=123)
    exam = pd.to_datetime(df["exam_date"])
    followup = pd.to_datetime(df["followup_end"])
    assert exam.le(followup).all()


def test_no_observed_cancer_after_followup():
    df = generate_synthetic_screening_data(n_patients=500, seed=456)
    cancer = pd.to_datetime(df["cancer_date"])
    followup = pd.to_datetime(df["followup_end"])
    assert (cancer.isna() | cancer.le(followup)).all()


def test_cumulative_risk_outputs_are_monotone():
    df = generate_synthetic_screening_data(n_patients=250, seed=789)
    risks = df[[f"mirai_risk_{h}yr" for h in range(1, 6)]].to_numpy(float)
    assert np.all(np.diff(risks, axis=1) >= -1e-12)
