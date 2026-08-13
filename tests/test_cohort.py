import pandas as pd

from src.cohort import assign_patient_split, assert_no_patient_leakage, build_cumulative_endpoints


def test_endpoint_eligibility_and_censoring():
    df = pd.DataFrame({
        "exam_date": pd.to_datetime(["2020-01-01", "2020-01-01", "2020-01-01"]),
        "cancer_date": pd.to_datetime(["2020-08-01", None, None]),
        "followup_end": pd.to_datetime(["2020-08-01", "2022-02-01", "2020-09-01"]),
    })
    out = build_cumulative_endpoints(df, horizons=[1, 2])
    assert out.loc[0, "eligible_1yr"] == 1 and out.loc[0, "label_1yr"] == 1
    assert out.loc[1, "eligible_2yr"] == 1 and out.loc[1, "label_2yr"] == 0
    assert out.loc[2, "eligible_1yr"] == 0 and pd.isna(out.loc[2, "label_1yr"])


def test_patient_split_has_no_crossing_patients():
    df = pd.DataFrame({"patient_id": ["a", "a", "b", "c", "c", "d"]})
    out = assign_patient_split(df)
    assert_no_patient_leakage(out)
    assert out.groupby("patient_id")["split"].nunique().max() == 1
