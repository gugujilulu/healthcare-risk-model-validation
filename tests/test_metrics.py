import numpy as np

from src.metrics import calibration_table, discrimination_calibration_metrics


def test_metrics_return_expected_keys():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.05, 0.2, 0.7, 0.9])
    out = discrimination_calibration_metrics(y, p)
    assert 0.5 <= out["auc"] <= 1
    assert out["brier"] >= 0
    assert out["e_o_ratio"] > 0


def test_calibration_table_counts_rows():
    y = np.array([0, 0, 0, 1, 1, 1] * 10)
    p = np.linspace(.01, .8, len(y))
    tab = calibration_table(y, p, n_bins=5)
    assert tab["n"].sum() == len(y)
