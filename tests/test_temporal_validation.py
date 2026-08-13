import pandas as pd

from src.temporal_validation import split_validation_patients_temporal


def test_temporal_validation_calibration_selection_patient_disjoint():
    df = pd.DataFrame({
        "patient_id": [f"P{i:03d}" for i in range(100) for _ in range(2)],
        "x": range(200),
    })

    cal, sel = split_validation_patients_temporal(df, seed=123)

    cal_patients = set(cal["patient_id"].astype(str))
    sel_patients = set(sel["patient_id"].astype(str))

    assert cal_patients
    assert sel_patients
    assert cal_patients.isdisjoint(sel_patients)
    assert cal_patients | sel_patients == set(df["patient_id"].astype(str))
