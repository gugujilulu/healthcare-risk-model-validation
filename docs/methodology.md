# Methodology

## 1. Unit of analysis

The analytical unit is a screening exam. Patients can contribute multiple exams, which creates within-patient dependence. Patient identity is therefore treated as the clustering unit for splitting and bootstrap resampling.

## 2. Cumulative outcomes and follow-up eligibility

For each exam and horizon `k` (1–5 years):

- `label_kyr = 1` when cancer occurs after the exam and within `k` years;
- `label_kyr = 0` when no event occurs within `k` years and at least `k` years of follow-up are observed;
- the exam is ineligible when follow-up is shorter than `k` years and no event has yet occurred.

This prevents incompletely observed negatives from being treated as controls.

## 3. Patient-level data splitting

All exams from the same patient remain in one split. The synthetic public pipeline uses train / validation / test partitions assigned at patient level and checks that no patient crosses splits.

## 4. External validation metrics

The public pipeline evaluates the fixed baseline probability for each horizon using:

- ROC AUC;
- Brier score;
- expected-to-observed (E/O) ratio;
- calibration intercept;
- calibration slope; and
- decile-based calibration tables.

These metrics separate risk ranking from probability accuracy.

## 5. Local model updating

Local adaptation operates at the prediction level. The baseline image-model risk output is fixed and combined with generic structured variables that are available before the prediction-time boundary.

Public candidate models:

- logistic regression updating;
- LightGBM updating.

The image network itself is not retrained.

## 6. Calibration

The reconstruction compares four probability treatments:

- none;
- Platt calibration;
- isotonic calibration; and
- beta-style calibration.

Calibration selection occurs before final test evaluation. See `evaluation_protocol.md`.

## 7. Patient-cluster bootstrap

Paired bootstrap samples patients with replacement and carries all exams belonging to each sampled patient. The same bootstrap draw is used for baseline and adapted predictions so that improvement metrics are paired.

Reported improvement quantities include:

- ΔAUC;
- ΔBrier; and
- change in absolute E/O error.

## 8. Temporal validation

Temporal validation trains on earlier screening years, uses the immediately subsequent period for validation, and evaluates on later eligible exams. Horizon-specific eligibility is respected before constructing the temporal partitions.

The purpose is to stress-test whether gains seen in random patient splits persist under calendar-time shift.

## 9. Feature-availability audit

The main adaptation model only admits pre-screen/general variables. Variables representing screening findings or result categories are explicitly marked as post-screen and blocked from the main feature set.

This prevents a later-time signal from being misrepresented as pre-screen risk prediction.

## 10. Robustness analyses

The public reconstruction includes:

- subgroup evaluation;
- first-exam-only sensitivity;
- patient-cluster bootstrap;
- decision-curve analysis; and
- future-period temporal validation.

A separate post-screen branch is retained as a distinct task rather than merged into the main adaptation model.
