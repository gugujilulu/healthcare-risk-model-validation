from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import expit

from .cohort import add_screening_history, assign_patient_split, build_cumulative_endpoints


def generate_synthetic_screening_data(n_patients: int = 12000, seed: int = 20260812) -> pd.DataFrame:
    """Generate a synthetic longitudinal screening cohort.

    The data are illustrative only. They are designed to exercise the same
    validation logic as the public reconstruction without reproducing any
    private patient-level data or internal schema.
    """
    rng = np.random.default_rng(seed)
    rows = []
    density_levels = np.array(["A", "B", "C", "D"])

    for pid in range(1, n_patients + 1):
        base_age = np.clip(rng.normal(56, 8), 40, 74)
        density = rng.choice(density_levels, p=[0.10, 0.39, 0.39, 0.12])
        family = rng.choice(["no", "yes"], p=[0.82, 0.18])
        biopsy = rng.choice(["no", "yes"], p=[0.88, 0.12])
        start_year = int(rng.integers(2011, 2017))
        n_exams = int(rng.integers(1, 5))

        density_effect = {"A": -0.35, "B": -0.10, "C": 0.20, "D": 0.45}[density]
        event_latent = (
            -4.65
            + 0.050 * (base_age - 55)
            + 0.65 * density_effect
            + 0.70 * (family == "yes")
            + 0.55 * (biopsy == "yes")
            + rng.normal(0, 0.45)
        )
        annual_hazard = np.exp(event_latent)
        # The fixed baseline score captures meaningful but incomplete signal.
        # Local structured variables therefore have room to add information.
        baseline_latent = (
            -4.55
            + 0.040 * (base_age - 55)
            + 0.50 * density_effect
            + 0.12 * (family == "yes")
            + rng.normal(0, 0.28)
        )
        baseline_annual_hazard = np.exp(baseline_latent)
        event_delay = rng.exponential(1 / annual_hazard)
        has_event = event_delay < 10

        first_exam_date = pd.Timestamp(year=start_year, month=int(rng.integers(1, 13)), day=15)
        latent_cancer_date = (
            first_exam_date + pd.to_timedelta(event_delay * 365.25, unit="D")
            if has_event
            else pd.NaT
        )
        admin_followup_end = pd.Timestamp("2021-12-31")
        # Some patients have earlier last-known follow-up to create horizon-specific eligibility.
        if rng.random() < 0.18:
            admin_followup_end = min(
                admin_followup_end,
                first_exam_date + pd.to_timedelta(rng.uniform(2.0, 7.0) * 365.25, unit="D"),
            )
        observed_cancer_date = (
            latent_cancer_date
            if pd.notna(latent_cancer_date) and latent_cancer_date <= admin_followup_end
            else pd.NaT
        )

        for j in range(n_exams):
            exam_date = first_exam_date + pd.DateOffset(years=2 * j)
            if exam_date > pd.Timestamp("2019-12-31"):
                break
            if exam_date > admin_followup_end:
                break
            if pd.notna(observed_cancer_date) and exam_date >= observed_cancer_date:
                break

            age = base_age + 2 * j
            annual_prob = 1 - np.exp(-baseline_annual_hazard)
            mirai_noise = rng.normal(0, 0.26)
            # Fixed image-model outputs: one probability per cumulative horizon.
            risks = {}
            for h in range(1, 6):
                base_p = 1 - (1 - annual_prob) ** h
                logit_p = np.log(np.clip(base_p, 1e-5, 1 - 1e-5) / np.clip(1 - base_p, 1e-5, 1))
                risks[h] = expit(logit_p + mirai_noise + rng.normal(0, 0.10))

            # Post-screen findings are intentionally later-time information and are isolated from the main model.
            tte = ((latent_cancer_date - exam_date).days / 365.25) if pd.notna(latent_cancer_date) else np.inf
            imminent = np.exp(-max(tte, 0) / 1.2) if np.isfinite(tte) else 0.0
            finding_mass = rng.binomial(1, np.clip(0.04 + 0.65 * imminent, 0, 0.9))
            finding_calc = rng.binomial(1, np.clip(0.05 + 0.40 * imminent, 0, 0.8))
            finding_asymm = rng.binomial(1, np.clip(0.08 + 0.20 * imminent, 0, 0.6))
            result_score = finding_mass + finding_calc + finding_asymm
            result_category = "routine" if result_score == 0 else ("review" if result_score == 1 else "follow_up")

            row = {
                "patient_id": f"P{pid:06d}",
                "exam_id": f"P{pid:06d}_{exam_date:%Y%m%d}",
                "exam_date": exam_date,
                "screen_year": exam_date.year,
                "cancer_date": observed_cancer_date,
                "followup_end": admin_followup_end,
                "age": float(age),
                "density": density,
                "family_history": family,
                "prior_biopsy": biopsy,
                "finding_mass": finding_mass,
                "finding_calcification": finding_calc,
                "finding_asymmetry": finding_asymm,
                "result_category": result_category,
            }
            for h, p in risks.items():
                row[f"mirai_risk_{h}yr"] = float(p)
            rows.append(row)

    df = pd.DataFrame(rows)
    df = build_cumulative_endpoints(df)
    df = add_screening_history(df)
    df = assign_patient_split(df)
    return df.reset_index(drop=True)
