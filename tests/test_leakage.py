import pytest

from src.leakage_audit import assert_prediction_time_safe, feature_availability_table


def test_post_screen_features_are_blocked_from_main_model():
    with pytest.raises(ValueError):
        assert_prediction_time_safe(["age", "finding_mass"])


def test_availability_table_marks_post_screen():
    tab = feature_availability_table()
    assert not tab.loc[tab.feature == "result_category", "main_model_allowed"].iloc[0]
