import pandas as pd

from src.synthetic import generate_synthetic_screening_data


def test_synthetic_timeline_is_observationally_consistent():
    df = generate_synthetic_screening_data(n_patients=250, seed=123)
    exam_date = pd.to_datetime(df["exam_date"])
    followup_end = pd.to_datetime(df["followup_end"])
    cancer_date = pd.to_datetime(df["cancer_date"])

    assert exam_date.le(followup_end).all()
    observed = cancer_date.notna()
    assert cancer_date.loc[observed].le(followup_end.loc[observed]).all()
