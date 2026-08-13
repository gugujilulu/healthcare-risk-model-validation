# Public Evidence Summary

## 1. Project question

Can a mammography-based risk model developed elsewhere be externally validated and locally adapted in a provincial screening cohort while preserving correct prediction-time, censoring, calibration, and transportability boundaries?

## 2. Validation foundation

- exam-level prediction origins with repeated exams per patient;
- 1–5 year cumulative endpoints;
- horizon-specific follow-up eligibility;
- patient-level splitting / clustered bootstrap;
- Original Mirai treated as a fixed image-model baseline.

The private retrospective project included up to **438,571 eligible screening exams** depending on horizon.

## 3. Baseline findings

In the independent-extension held-out framework, Original Mirai AUC ranged from approximately **0.691–0.742** across the five cumulative horizons. Probability calibration varied by horizon, so AUC was interpreted alongside Brier score, E/O ratio, calibration intercept/slope, and grouped calibration.

## 4. Local adaptation findings

Local structured variables added retrospective discrimination beyond the fixed Mirai outputs. Logistic Updated served as an interpretable benchmark, while tuned and calibrated LightGBM produced the strongest **observed exploratory held-out** AUCs, approximately **0.774–0.835** across horizons.

These headline values document the private exploratory project. The public reconstruction uses a cleaner validation-selection / locked-test protocol, so the two evaluation contexts are kept separate.

## 5. Evidence strength

Paired patient-cluster bootstrap intervals for tuned-model ΔAUC versus Original Mirai remained positive in the held-out analysis; the lowest reported lower bound was approximately **0.031**. Temporal validation then provided the stronger stress test: the larger random-split gains contracted to approximately **+0.007 to +0.017** under future-period evaluation.

The correct interpretation is therefore bounded: the data contained substantial retrospective local signal, while only a smaller advantage transported to the tested later periods.

## 6. Robustness and prediction-time checks

The evidence chain also includes:

- first-exam-only sensitivity to reduce repeated-record weighting;
- subgroup discrimination and sample-size reliability checks;
- explicit feature-availability / leakage audit;
- high-risk capture and decision-curve analyses; and
- a separated post-screen triage task.

The calibrated post-screen branch reached approximately **0.964 AUC at 1 year** and **0.913 at 2 years**, reflecting access to later findings/result information. Those values answer a different prediction-time question from pre-screen/general risk updating.

## 7. Public reconstruction

The public codebase reproduces the analytical design with synthetic data and a generic feature schema. `python run_all.py` generates the synthetic cohort, builds cumulative endpoints, evaluates the fixed baseline, selects/calibrates local-updating models without using the test set for selection, runs robustness/temporal/post-screen analyses, and regenerates synthetic figures/tables.

The curated files under `evidence/` provide aggregate context from the private retrospective work, while `results/` contains outputs from the synthetic pipeline. The two layers are maintained separately to preserve provenance.

## 8. Scope

The evidence package focuses on external validation, calibration, prediction-level updating, robustness, and temporal transportability. The Original Mirai image network remains fixed throughout the work. Curated private-context evidence is presented only in aggregate form, while patient-level source assets remain outside the repository. The synthetic pipeline is a public reconstruction of the methodology and uses its own generated data.
