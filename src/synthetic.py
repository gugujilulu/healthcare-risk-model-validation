from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import expit

from .cohort import add_screening_history, assign_patient_split, build_cumulative_endpoints


DENSITY_LEVELS = np.array(["A", "B", "C", "D"])
DENSITY_EFFECT = {"A": -0.45, "B": -0.15, "C": 0.20, "D": 0.50}
HORIZON_LOGIT_BIAS = {1: -0.18, 2: 0.10, 3: 0.12, 4: 0.03, 5: -0.08}
HORIZON_NOISE_SD = {1: 0.09, 2: 0.14, 3: 0.21, 4: 0.29, 5: 0.38}


def _local_signal_scale(calendar_year: int) -> float:
    """Introduce a controlled calendar-time shift for the synthetic stress test.

    The image-derived latent signal remains stable, while the association of
    local structured variables with the event process weakens over later
    calendar years. This creates a realistic demonstration in which random-
    split adaptation can look stronger than future-period transportability.
    """
    if calendar_year <= 2014:
        return 1.20
    if calendar_year == 2015:
        return 1.10
    if calendar_year == 2016:
        return 0.95
    if calendar_year == 2017:
        return 0.55
    return 0.35


def _observed_local_value(true_value, rng: np.random.Generator, screen_year: int, *, density: bool = False):
    """Apply mild calendar-time missingness to public synthetic local fields."""
    late_years = max(screen_year - 2015, 0)
    missing_rate = min((0.015 if density else 0.025) + (0.05 if density else 0.08) * late_years, 0.30 if density else 0.34)
    if rng.random() < missing_rate:
        return None
    return true_value


def generate_synthetic_screening_data(n_patients: int = 12000, seed: int = 20260812) -> pd.DataFrame:
    """Generate a public synthetic longitudinal screening cohort.

    Design goals are structural rather than numerical replication of the
    private study. The generator creates:

    - 1--4 repeated exams per patient;
    - cumulative 1--5 year outcomes with horizon-specific eligibility;
    - a useful but imperfect fixed image-risk signal;
    - local structured variables that add retrospective signal;
    - calendar-time shift that can contract adaptation gains;
    - a stronger, later-time post-screen triage signal; and
    - administrative censoring with internally consistent time axes.

    No private record, internal field mapping, or fitted private model object is
    used to generate these data.
    """
    rng = np.random.default_rng(seed)
    rows: list[dict] = []

    for pid in range(1, n_patients + 1):
        base_age = float(np.clip(rng.normal(56, 8), 40, 74))
        true_density = str(rng.choice(DENSITY_LEVELS, p=[0.10, 0.39, 0.39, 0.12]))
        true_family = str(rng.choice(["no", "yes"], p=[0.82, 0.18]))
        true_biopsy = str(rng.choice(["no", "yes"], p=[0.88, 0.12]))

        # Latent image signal is public-simulation-only. It is never written to
        # the dataset; the public artifact exposes only horizon risk outputs.
        image_signal = float(rng.normal())
        start_year = int(
            rng.choice(
                np.arange(2011, 2018),
                p=[0.10, 0.11, 0.13, 0.15, 0.17, 0.18, 0.16],
            )
        )
        n_exams = int(rng.choice([1, 2, 3, 4], p=[0.30, 0.34, 0.23, 0.13]))
        first_exam_date = pd.Timestamp(year=start_year, month=int(rng.integers(1, 13)), day=15)

        admin_followup_end = pd.Timestamp("2021-12-31")
        if rng.random() < 0.18:
            admin_followup_end = min(
                admin_followup_end,
                first_exam_date + pd.to_timedelta(rng.uniform(2.0, 7.0) * 365.25, unit="D"),
            )

        # Simulate a latent diagnosis time in quarterly intervals. Local
        # structured-signal strength is intentionally weaker in later years,
        # while the image signal remains stable, so temporal validation is a
        # meaningful stress test rather than a second random split.
        density_effect = DENSITY_EFFECT[true_density]
        latent_cancer_date = pd.NaT
        t = first_exam_date
        max_latent_date = min(
            first_exam_date + pd.to_timedelta(10.0 * 365.25, unit="D"),
            pd.Timestamp("2023-12-31"),
        )
        while t < max_latent_date:
            age_t = base_age + (t - first_exam_date).days / 365.25
            scale = _local_signal_scale(t.year)
            log_annual_hazard = (
                -5.18
                + 0.85 * image_signal
                + scale
                * (
                    0.080 * (age_t - 55)
                    + 1.05 * density_effect
                    + 1.40 * (true_family == "yes")
                    + 1.20 * (true_biopsy == "yes")
                )
            )
            quarter_event_prob = 1 - np.exp(-np.exp(log_annual_hazard) * 0.25)
            if rng.random() < quarter_event_prob:
                latent_cancer_date = t + pd.to_timedelta(rng.uniform(0, 0.25) * 365.25, unit="D")
                break
            t += pd.to_timedelta(0.25 * 365.25, unit="D")

        # Only an event observed before the last known follow-up date is exposed
        # as cancer_date. Later latent events are administratively censored.
        observed_cancer_date = (
            latent_cancer_date
            if pd.notna(latent_cancer_date) and latent_cancer_date <= admin_followup_end
            else pd.NaT
        )

        for exam_index in range(n_exams):
            exam_date = first_exam_date + pd.DateOffset(years=2 * exam_index)
            if exam_date > pd.Timestamp("2019-12-31"):
                break
            if exam_date > admin_followup_end:
                break
            if pd.notna(observed_cancer_date) and exam_date >= observed_cancer_date:
                break

            age = base_age + 2 * exam_index
            observed_density = _observed_local_value(true_density, rng, exam_date.year, density=True)
            observed_family = _observed_local_value(true_family, rng, exam_date.year)
            observed_biopsy = _observed_local_value(true_biopsy, rng, exam_date.year)

            # Fixed image-model risk outputs: useful but incomplete signal.
            # Horizon noise increases gradually to avoid an unrealistically
            # identical discrimination profile at every cumulative horizon.
            log_annual_baseline = (
                -5.10
                + 0.78 * image_signal
                + 0.012 * (age - 55)
                + 0.08 * density_effect
                + rng.normal(0, 0.12)
            )
            annual_prob = 1 - np.exp(-np.exp(log_annual_baseline))
            shared_noise = rng.normal(0, 0.07)
            raw_risks = []
            for h in range(1, 6):
                base_p = 1 - (1 - annual_prob) ** h
                logit_p = np.log(np.clip(base_p, 1e-6, 1 - 1e-6) / np.clip(1 - base_p, 1e-6, 1))
                raw_risks.append(
                    float(
                        expit(
                            logit_p
                            + HORIZON_LOGIT_BIAS[h]
                            + shared_noise
                            + rng.normal(0, HORIZON_NOISE_SD[h])
                        )
                    )
                )
            # Mirai-style cumulative risks should remain monotone by horizon.
            monotone_risks = np.maximum.accumulate(np.asarray(raw_risks, dtype=float))

            # Later-time findings are deliberately strong for imminent events.
            # They are exposed only to the separate post-screen triage branch.
            time_to_latent_event = (
                (latent_cancer_date - exam_date).days / 365.25
                if pd.notna(latent_cancer_date)
                else np.inf
            )
            imminent = np.exp(-max(time_to_latent_event, 0) / 1.00) if np.isfinite(time_to_latent_event) else 0.0
            finding_mass = rng.binomial(1, np.clip(0.020 + 0.90 * imminent, 0, 0.98))
            finding_calc = rng.binomial(1, np.clip(0.035 + 0.72 * imminent, 0, 0.96))
            finding_asymm = rng.binomial(1, np.clip(0.055 + 0.45 * imminent, 0, 0.86))
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
                "density": observed_density,
                "family_history": observed_family,
                "prior_biopsy": observed_biopsy,
                "finding_mass": int(finding_mass),
                "finding_calcification": int(finding_calc),
                "finding_asymmetry": int(finding_asymm),
                "result_category": result_category,
            }
            for h, risk in enumerate(monotone_risks, start=1):
                row[f"mirai_risk_{h}yr"] = float(risk)
            rows.append(row)

    df = pd.DataFrame(rows)
    df = build_cumulative_endpoints(df)
    df = add_screening_history(df)
    df = assign_patient_split(df)
    return df.reset_index(drop=True)
