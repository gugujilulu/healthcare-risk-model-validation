from src.post_screen import post_screen_feature_columns


def test_post_screen_uses_horizon_specific_baseline_risk():
    one_year = post_screen_feature_columns(1)
    two_year = post_screen_feature_columns(2)
    assert "mirai_risk_1yr" in one_year
    assert "mirai_risk_2yr" in two_year
    assert "finding_mass" in one_year
    assert "result_category" in two_year
