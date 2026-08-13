from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

HORIZONS = (1, 2, 3, 4, 5)


@dataclass(frozen=True)
class SplitConfig:
    train_fraction: float = 0.70
    validation_fraction: float = 0.15
    seed: int = 20260812


def build_cumulative_endpoints(
    df: pd.DataFrame,
    horizons: Iterable[int] = HORIZONS,
    exam_date_col: str = "exam_date",
    event_date_col: str = "cancer_date",
    followup_end_col: str = "followup_end",
) -> pd.DataFrame:
    """Create horizon-specific cumulative labels and follow-up eligibility.

    An exam is eligible for horizon k if either an event occurs within k years
    after that exam or the exam has at least k years of observed follow-up.
    """
    out = df.copy()
    exam_date = pd.to_datetime(out[exam_date_col])
    event_date = pd.to_datetime(out[event_date_col])
    followup_end = pd.to_datetime(out[followup_end_col])

    time_to_event = (event_date - exam_date).dt.days / 365.25
    followup_years = (followup_end - exam_date).dt.days / 365.25
    observed_event = event_date.notna() & event_date.le(followup_end)

    for h in horizons:
        event_within = observed_event & time_to_event.gt(0) & time_to_event.le(h)
        eligible = event_within | followup_years.ge(h)
        out[f"label_{h}yr"] = np.where(eligible, event_within.astype(int), np.nan)
        out[f"eligible_{h}yr"] = eligible.astype(int)

    return out


def assign_patient_split(
    df: pd.DataFrame,
    patient_col: str = "patient_id",
    config: SplitConfig = SplitConfig(),
) -> pd.DataFrame:
    """Assign train/validation/test splits at patient level."""
    if not 0 < config.train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    if not 0 < config.validation_fraction < 1:
        raise ValueError("validation_fraction must be between 0 and 1")
    if config.train_fraction + config.validation_fraction >= 1:
        raise ValueError("train + validation fractions must be < 1")

    out = df.copy()
    patients = pd.Index(out[patient_col].dropna().astype(str).unique())
    rng = np.random.default_rng(config.seed)
    shuffled = patients.to_numpy(copy=True)
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(round(n * config.train_fraction))
    n_val = int(round(n * config.validation_fraction))
    mapping = {}
    mapping.update({p: "train" for p in shuffled[:n_train]})
    mapping.update({p: "validation" for p in shuffled[n_train:n_train + n_val]})
    mapping.update({p: "test" for p in shuffled[n_train + n_val:]})

    out["split"] = out[patient_col].astype(str).map(mapping)
    return out


def add_screening_history(
    df: pd.DataFrame,
    patient_col: str = "patient_id",
    exam_date_col: str = "exam_date",
) -> pd.DataFrame:
    """Add exam order, prior-exam count, and first-exam indicator."""
    out = df.sort_values([patient_col, exam_date_col]).copy()
    out["exam_order"] = out.groupby(patient_col).cumcount() + 1
    out["prior_exam_count"] = out["exam_order"] - 1
    out["is_first_exam"] = (out["exam_order"] == 1).astype(int)
    return out


def assert_no_patient_leakage(
    df: pd.DataFrame,
    patient_col: str = "patient_id",
    split_col: str = "split",
) -> None:
    counts = df[[patient_col, split_col]].drop_duplicates().groupby(patient_col)[split_col].nunique()
    crossing = counts[counts > 1]
    if len(crossing):
        raise ValueError(f"{len(crossing)} patients appear in multiple splits")


def first_exam_only(df: pd.DataFrame) -> pd.DataFrame:
    if "is_first_exam" not in df.columns:
        df = add_screening_history(df)
    return df.loc[df["is_first_exam"] == 1].copy()
