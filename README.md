# Healthcare Risk Model Validation

**Public-safe evidence package and runnable reconstruction of a real mammography-based breast cancer risk-model validation and local adaptation project.**

The underlying work originated in a UBC Master of Data Science capstone with BC Cancer and was later extended independently into local recalibration, prediction-level model updating, calibration-method comparison, patient-cluster bootstrap, temporal future-period validation, first-exam sensitivity, feature-availability auditing, decision-curve analysis, and post-screen triage.

> **Public boundary:** this repository includes selected aggregate context, public-safe figures, generic methodology, and synthetic runnable code. It does not include patient-level data, internal BC Cancer field mappings, private modeling datasets, original private scripts, the internal technical manual, or full private result tables. See [`NOTICE.md`](NOTICE.md) for how the MIT license relates to the public reconstruction code and curated aggregate evidence.

## Project context and public reconstruction

| Private retrospective analysis context | Public repository artifact |
|---|---|
| Provincial screening cohort with up to **438,571 eligible screening exams** | Synthetic longitudinal screening cohort implementing the same evaluation logic |
| **1–5 year cumulative risk horizons** with horizon-specific follow-up eligibility | Public endpoint builder with censoring-aware eligibility |
| Original Mirai external validation using AUC, Brier, E/O, calibration and subgroup analyses | Curated aggregate evidence + synthetic external-validation pipeline |
| Prediction-level local adaptation using fixed Mirai outputs + structured variables | Logistic and LightGBM updating with validation-only model/calibration selection |
| Patient-cluster bootstrap and future-period temporal validation | Public paired bootstrap and temporal stress-test modules |
| Explicit pre-screen vs post-screen information boundary | Leakage audit + separate post-screen triage branch |

Two historical evaluation contexts are kept separate. The capstone full-cohort external validation produced AUCs of approximately **0.731 to 0.665** across 1–5 years. The later independent extension used a patient-level held-out framework, where Original Mirai AUCs were approximately **0.742 to 0.691** and the strongest observed exploratory adapted AUCs were approximately **0.774 to 0.835**. Under future-period temporal validation, the larger random-split gains contracted to approximately **+0.007 to +0.017**.

The private best-observed adaptation values are **exploratory held-out results**, not a claim that one fully pre-locked model was evaluated once on an untouched test set. The public reconstruction implements a cleaner locked-test protocol; see [`docs/evaluation_protocol.md`](docs/evaluation_protocol.md).

## Evidence highlights

### 1. External validation across 1–5 year horizons

![ROC curves across 1–5 year horizons](evidence/figures/original_style/external_validation_roc_curves_1_5yr.png)

Original Mirai retained useful discrimination in the BC Cancer screening cohort across 1–5 year cumulative horizons. This is a static aggregate visual summary from the private retrospective analysis; patient-level predictions and ROC coordinate tables are not included.

![External validation AUC summary](evidence/figures/external_validation_auc_1_5yr.svg)

The companion summary keeps the capstone full-cohort external-validation context separate from the later held-out baseline used in the independent extension.

### 2. Calibration is a separate problem from ranking

![Decile calibration across 1–5 year horizons](evidence/figures/original_style/external_validation_calibration_decile_1_5yr.png)

Calibration was evaluated separately from discrimination. The original validation analysis used grouped observed-versus-predicted risk, Brier score, E/O ratio, and calibration slope/intercept to assess whether predicted probabilities were numerically reliable.

![External validation calibration context](evidence/figures/external_validation_calibration_context.svg)

The companion summary provides a compact horizon-level view of probability burden without publishing the private calibration table in full.

### 3. Local adaptation adds retrospective signal

![Local adaptation summary](evidence/figures/local_adaptation_auc_summary.svg)

The independent extension evaluated recalibration, logistic updating, and calibrated LightGBM model updating. The headline adapted values are reported as observed exploratory held-out performance and are explicitly separated from the public locked-test demo.

### 4. Temporal validation contracts random-split gains

![Temporal validation contraction](evidence/figures/temporal_validation_contraction.svg)

Future-period testing reduced the larger random-split gains to a small positive advantage. This contraction is a central interpretation boundary, not a detail hidden in limitations.

### 5. Repeated-exam sensitivity

![First-exam-only sensitivity](evidence/figures/original_style/first_exam_only_auc.svg)

After reducing the held-out set to one earliest observed exam per patient, the tuned nonlinear model retained the main discrimination improvement pattern. The full visual gallery also includes subgroup AUC forest plots and imaging-finding analyses; see [`docs/analysis_gallery.md`](docs/analysis_gallery.md).

## What this repository demonstrates

- **External validation:** exam-level prediction origins, cumulative 1–5y endpoints, follow-up eligibility, AUC, Brier, E/O and calibration.
- **Patient-level dependence:** all exams from one patient remain together for splitting; bootstrap resampling occurs at patient level.
- **Local model updating:** fixed horizon-specific Mirai probabilities are combined with generic pre-screen structured variables using logistic regression and LightGBM.
- **Calibration:** probability calibration is evaluated separately from ranking, with model/calibration selection completed before the public test evaluation.
- **Robustness:** patient-cluster bootstrap, subgroup analysis, first-exam-only sensitivity and decision-curve analysis.
- **Transportability:** later calendar periods are used to stress-test whether random-split adaptation gains persist over time.
- **Prediction-time control:** current findings/result variables are blocked from the main risk-updating model and isolated in a later post-screen triage task.
- **Public-safe reproducibility:** synthetic data reproduce the analytical structure without releasing private patient-level assets.

## Evidence package

| Document | What it adds |
|---|---|
| [`docs/project_evidence_map.md`](docs/project_evidence_map.md) | Maps the private analysis chain to public-safe repository artifacts |
| [`docs/external_validation_evidence.md`](docs/external_validation_evidence.md) | Cohort, follow-up, capstone full-cohort validation, held-out baseline, calibration and subgroup evidence |
| [`docs/local_adaptation_evidence.md`](docs/local_adaptation_evidence.md) | Recalibration, logistic updating, tuned LightGBM and horizon-specific observed winners |
| [`docs/robustness_and_transportability.md`](docs/robustness_and_transportability.md) | Patient bootstrap, temporal validation, first-exam sensitivity and leakage audit |
| [`docs/clinical_use_analyses.md`](docs/clinical_use_analyses.md) | High-risk capture, DCA, blending and post-screen triage |
| [`docs/technical_decisions.md`](docs/technical_decisions.md) | Key analytical choices and their rationale |
| [`docs/analysis_gallery.md`](docs/analysis_gallery.md) | Curated visual evidence with interpretation notes |
| [`reports/public_evidence_summary.md`](reports/public_evidence_summary.md) | Compact narrative summary of the evidence chain |

The aggregate context files themselves are separated under [`evidence/`](evidence/README.md). Synthetic generated outputs remain under `results/`.

## Runnable synthetic pipeline

```bash
git clone https://github.com/gugujilulu/healthcare-risk-model-validation.git
cd healthcare-risk-model-validation
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_all.py
```

The pipeline will:

1. generate a synthetic longitudinal screening cohort;
2. construct cumulative endpoints and horizon-specific follow-up eligibility;
3. run synthetic external validation of the fixed baseline risk outputs;
4. select and calibrate local-updating models without using the test set for selection;
5. run paired patient-cluster bootstrap, subgroup, first-exam, decision-curve and temporal analyses;
6. run the separate post-screen triage branch;
7. regenerate synthetic figures/tables; and
8. rebuild the public evidence summary from the curated aggregate tables.

Run tests with:

```bash
pytest -q
```

CI runs both `pytest -q` and the complete `python run_all.py` pipeline.

## Repository structure

```text
healthcare-risk-model-validation/
├── README.md
├── NOTICE.md
├── requirements.txt
├── run_all.py
├── data/
│   ├── README.md
│   └── synthetic/
│       └── screening_demo_sample.csv
├── src/
│   ├── cohort.py
│   ├── synthetic.py
│   ├── metrics.py
│   ├── calibration.py
│   ├── modeling.py
│   ├── bootstrap.py
│   ├── temporal_validation.py
│   ├── leakage_audit.py
│   ├── subgroup.py
│   ├── decision_curve.py
│   ├── post_screen.py
│   └── plotting.py
├── scripts/
│   ├── 01_generate_synthetic_data.py
│   ├── 02_external_validation.py
│   ├── 03_local_adaptation.py
│   ├── 04_robustness.py
│   ├── 05_temporal_validation.py
│   ├── 06_post_screen_triage.py
│   ├── 07_make_figures.py
│   └── 08_make_public_evidence_summary.py
├── results/                 # synthetic generated outputs
│   ├── tables/
│   └── figures/
├── evidence/                # curated aggregate private-project context
│   ├── README.md
│   ├── tables/
│   └── figures/
├── docs/
│   ├── methodology.md
│   ├── public_boundary.md
│   ├── evaluation_protocol.md
│   ├── interpretation.md
│   ├── limitations.md
│   ├── project_evidence_map.md
│   ├── external_validation_evidence.md
│   ├── local_adaptation_evidence.md
│   ├── robustness_and_transportability.md
│   ├── clinical_use_analyses.md
│   ├── technical_decisions.md
│   └── analysis_gallery.md
├── reports/
│   └── public_evidence_summary.md
└── tests/
```

## Interpretation boundary

This repository demonstrates **external validation and prediction-level local adaptation of fixed Mirai risk outputs**. It does **not** retrain or fine-tune the Mirai image network, claim clinical deployment, establish prospective utility, or represent an official BC Cancer model release.

Private-context figures/tables are curated aggregate evidence. Synthetic outputs are runnable demonstrations. They are intentionally not presented as the same evidence source.

The separate post-screen branch uses information available after the screening exam and therefore answers a different prediction-time question from the main pre-screen/general risk-updating workflow.

## My role

I implemented the analytical code and validation workflow for the capstone external-validation analysis, including cohort construction, outcome definition, model evaluation, calibration tables, patient-cluster bootstrap, subgroup analysis, follow-up availability summaries, and validation figures.

I later independently extended the work into local recalibration, logistic and LightGBM model updating, calibration-method comparison, robustness analysis, patient-cluster bootstrap, temporal future-period validation, first-exam sensitivity, feature-availability audit, decision-curve analysis, post-screen triage, and this public-safe reconstruction.

## Additional documentation

- [`docs/methodology.md`](docs/methodology.md) — public analytical design and method definitions
- [`docs/evaluation_protocol.md`](docs/evaluation_protocol.md) — locked-test public protocol vs retrospective exploratory context
- [`docs/public_boundary.md`](docs/public_boundary.md) — asset-level public/private boundary
- [`docs/interpretation.md`](docs/interpretation.md) — model/task interpretation
- [`docs/limitations.md`](docs/limitations.md) — limitations and non-claims
