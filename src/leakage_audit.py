from __future__ import annotations

import pandas as pd

PRE_SCREEN_FEATURES = [
    "age",
    "density",
    "family_history",
    "prior_biopsy",
    "prior_exam_count",
    "is_first_exam",
]

POST_SCREEN_FEATURES = [
    "finding_mass",
    "finding_calcification",
    "finding_asymmetry",
    "result_category",
]


def feature_availability_table() -> pd.DataFrame:
    rows = []
    for f in PRE_SCREEN_FEATURES:
        rows.append({"feature": f, "availability": "pre_screen", "main_model_allowed": True})
    for f in POST_SCREEN_FEATURES:
        rows.append({"feature": f, "availability": "post_screen", "main_model_allowed": False})
    return pd.DataFrame(rows)


def assert_prediction_time_safe(features) -> None:
    blocked = sorted(set(features).intersection(POST_SCREEN_FEATURES))
    if blocked:
        raise ValueError(
            "Post-screen variables cannot enter the main pre-screen adaptation model: "
            + ", ".join(blocked)
        )
