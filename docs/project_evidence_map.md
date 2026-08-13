# Project Evidence Map

This document maps the private retrospective analysis chain to public-safe repository artifacts. The public repository is **not a dump of private analysis files**; it is a structured public translation of the evidence chain.

| Analytical layer | Private analysis component | Public-safe representation | Repository artifact |
|---|---|---|---|
| Prediction unit | Exam-level Mirai risk outputs linked to screening records | Synthetic exam-level longitudinal cohort | `src/synthetic.py`, `src/cohort.py` |
| Cumulative endpoints | 1–5y labels with horizon-specific follow-up eligibility | Public endpoint construction logic | `build_cumulative_endpoints()` |
| External validation | Original Mirai AUC, Brier, E/O, calibration, follow-up availability | Curated aggregate context + synthetic validation pipeline | `docs/external_validation_evidence.md`, `scripts/02_external_validation.py` |
| Repeated-exam dependence | Multiple exams per patient | Patient-level split and patient-cluster bootstrap | `assign_patient_split()`, `src/bootstrap.py` |
| Recalibration | Horizon-specific logistic recalibration | Public calibration module + curated coefficients | `src/calibration.py`, `docs/local_adaptation_evidence.md` |
| Local model updating | Logistic Updated and calibrated LightGBM | Public logistic / LightGBM updating pipeline | `src/modeling.py` |
| Model selection | Exploratory private comparisons; public locked-test reconstruction | Explicit protocol separation | `docs/evaluation_protocol.md` |
| Bootstrap uncertainty | Paired patient-cluster ΔAUC / ΔBrier / E/O-error uncertainty | Public bootstrap module + curated intervals | `src/bootstrap.py`, `docs/robustness_and_transportability.md` |
| Temporal validation | Future-period calendar-time stress test | Public temporal module + curated aggregate summary | `src/temporal_validation.py` |
| First-exam sensitivity | One earliest observed test exam per patient | Aggregate figure/table + public robustness logic | `docs/robustness_and_transportability.md` |
| Feature availability | Pre-screen vs post-screen information states | Explicit leakage audit | `src/leakage_audit.py` |
| Subgroup analysis | Density, age, family history, imaging-finding and other strata | Curated aggregate figure + interpretation | `docs/external_validation_evidence.md` |
| Use-case analyses | High-risk capture, DCA, blending, post-screen triage | Public-safe summaries and separate later-time branch | `docs/clinical_use_analyses.md`, `src/post_screen.py` |
| Reproducibility | 24-script private chain and technical manual | Public dependency map + runnable synthetic pipeline | `run_all.py`, `reports/public_evidence_summary.md` |

## Two evidence layers

The repository intentionally keeps two evidence layers distinct:

1. **Private retrospective evidence context** — selected aggregate figures and tables documenting what was evaluated and what high-level patterns were observed.
2. **Public runnable reconstruction** — synthetic data, generic schema, and a cleaner locked-test implementation that demonstrates the analytical workflow reproducibly.

Private-context artifacts document the original work. Synthetic outputs demonstrate implementation. They should not be interpreted as the same evidence source.
