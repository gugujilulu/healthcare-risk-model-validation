# Technical Decisions

This file records the analytical choices that shaped the project and the reason each choice matters.

## 1. Why exam-level analysis?

Each screening exam is a distinct prediction origin. A patient can have multiple exams, and each exam starts a new future-risk window. The analysis therefore remains exam-level even though patient identity is used for splitting and clustered uncertainty estimation.

## 2. Why patient-level split?

Randomly splitting exams would allow related records from the same patient to appear in both model-development and test partitions. Patient-level splitting keeps all exams from one patient together.

## 3. Why horizon-specific eligibility?

A record with two years of event-free follow-up can be a valid 1- or 2-year control but cannot be assigned a 5-year negative label. Each cumulative horizon therefore has its own eligibility mask.

## 4. Why AUC is insufficient?

AUC measures ranking. It does not determine whether predicted probabilities are numerically reliable. Brier score, E/O ratio, calibration intercept/slope, and risk-bin calibration answer different probability-quality questions.

## 5. Why recalibration and model updating are separate?

Recalibration changes the probability mapping of an existing score and generally preserves ranking. Model updating adds structured variables and can change both ranking and probability calibration.

## 6. Why does LightGBM require explicit calibration?

Rare-event training can benefit from negative downsampling, but the altered class balance distorts raw tree probabilities. Calibration is therefore required before the raw score can be interpreted as an absolute risk estimate.

## 7. Why is temporal validation central?

Random patient splits can reveal local signal while still preserving the same calendar-time environment. Future-period validation asks a stronger question: whether the gain survives changes in cohort mix, coding, screening practice, follow-up structure, and data availability over time.

## 8. Why are post-screen variables separated?

Current findings and result categories are strong predictors precisely because they become available later in the screening pathway. They are valid inputs for a post-screen triage task but invalid for the main prediction-origin risk update.

## 9. Why does the public repository use synthetic data?

The public implementation demonstrates cohort construction, censoring, splitting, calibration, model updating, bootstrap, temporal validation, and prediction-time controls without releasing patient-level data, internal mappings, private scripts, or the full private evidence package.

## 10. Why are private headline values labeled exploratory observed results?

The independent extension compared multiple model, calibration, and blending choices on held-out data. The reported private best-observed values therefore reflect exploratory comparison. The public code uses a cleaner locked-test protocol rather than retroactively rewriting the original analysis history.

## 11. Why keep full-cohort and held-out baselines separate?

The capstone external-validation analysis and the independent model-development extension answer different questions and use different evaluation sets. Full-cohort capstone AUCs should not be used as the denominator for held-out adaptation gains.

## 12. Why is the public evidence package curated rather than exhaustive?

A useful public portfolio artifact should expose the analytical evidence chain without recreating the private study archive. Curated aggregate figures/tables show the work performed and the key findings while keeping private raw outputs, prediction-level rows, and internal source assets out of the repository.
