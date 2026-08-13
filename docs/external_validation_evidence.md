# External Validation Evidence

## 1. Analysis unit and cohort construction

The primary unit is a **screening exam**. Patients can contribute repeated exams, so the analysis keeps exam-level prediction origins while using patient identity for clustered uncertainty estimation and later patient-level model-development splits.

Each horizon has its own follow-up eligibility rule. An event-free exam with two years of observed follow-up can be a valid control for the 1- and 2-year endpoints, but it cannot be treated as a 5-year negative.

| Horizon | Eligible exams | Cases | Eligible test exams | Test cases | Eligible % |
|---|---:|---:|---:|---:|---:|
| 1 year | 438,571 | 2,676 | 21,937 | 126 | 100.0% |
| 2 years | 438,571 | 3,705 | 21,937 | 173 | 100.0% |
| 3 years | 438,571 | 5,550 | 21,937 | 270 | 100.0% |
| 4 years | 379,203 | 6,670 | 18,989 | 327 | 86.46% |
| 5 years | 303,929 | 8,011 | 15,231 | 393 | 69.30% |

The curated source table is [`evidence/tables/private_context_cohort_summary.csv`](../evidence/tables/private_context_cohort_summary.csv).

## 2. Capstone primary external validation: full eligible cohort

The capstone external-validation analysis used all eligible screening exams as the primary evaluation set. Repeated exams were retained, with patient-level cluster bootstrap used for uncertainty.

| Horizon | AUC | 95% CI | Brier | E/O |
|---|---:|---:|---:|---:|
| 1 year | 0.7312 | 0.7205–0.7409 | 0.005915 | 0.804 |
| 2 years | 0.7149 | 0.7057–0.7233 | 0.008215 | 1.104 |
| 3 years | 0.6889 | 0.6799–0.6975 | 0.012275 | 1.056 |
| 4 years | 0.6774 | 0.6692–0.6856 | 0.016966 | 1.001 |
| 5 years | 0.6648 | 0.6567–0.6728 | 0.025156 | 0.808 |

These metrics belong to the **capstone full-cohort context**. They should not be mixed with the held-out baseline used later for local model updating.

## 3. Held-out baseline used by the independent extension

The independent extension introduced a patient-level train / validation / test framework. The fixed Original Mirai predictions in that held-out test set were:

| Horizon | Test exams | Cases | AUC | Brier | E/O |
|---|---:|---:|---:|---:|---:|
| 1 year | 21,937 | 126 | 0.7422 | 0.005611 | 0.881 |
| 2 years | 21,937 | 173 | 0.7404 | 0.007718 | 1.210 |
| 3 years | 21,937 | 270 | 0.7146 | 0.011977 | 1.105 |
| 4 years | 18,989 | 327 | 0.7029 | 0.016686 | 1.038 |
| 5 years | 15,231 | 393 | 0.6906 | 0.024693 | 0.841 |

This held-out baseline is the correct comparator for the independent-extension adaptation gains reported elsewhere in the repository.

## 4. Discrimination and calibration are separate questions

### Original-style ROC evidence

![ROC curves across 1–5 year horizons](../evidence/figures/original_style/external_validation_roc_curves_1_5yr.png)

This static aggregate figure preserves the original validation visual structure. It shows the horizon-specific ROC curves and patient-cluster bootstrap confidence intervals for the capstone full-cohort context. The underlying ROC coordinates and prediction-level rows are not published.

![External validation AUC](../evidence/figures/external_validation_auc_1_5yr.svg)

*Aggregate context from the private retrospective analysis. The public repository does not include the underlying clinical dataset or patient-level predictions.*

Original Mirai retained useful discrimination across all cumulative horizons, with ranking performance declining as the prediction window lengthened.

### Original-style calibration evidence

![Decile calibration across 1–5 year horizons](../evidence/figures/original_style/external_validation_calibration_decile_1_5yr.png)

Grouped calibration makes the probability-scale problem visible. It complements the compact E/O and Brier metrics reported in the curated tables.

![Calibration context](../evidence/figures/external_validation_calibration_context.svg)

*Aggregate context from the private retrospective analysis.*

AUC measures ranking, not absolute probability accuracy. The project therefore evaluates Brier score, E/O ratio, calibration intercept/slope, and risk-bin calibration alongside AUC.

## 5. Follow-up availability

![Follow-up availability](../evidence/figures/followup_availability.svg)

The later horizons illustrate the core censoring problem directly: cumulative case counts increase, but the number of exams with complete follow-up falls sharply at four and five years.

## 6. Subgroup and imaging-finding analyses

![Original-style subgroup forest](../evidence/figures/original_style/subgroup_auc_forest_1yr.svg)

The original-style forest plot is included as a static aggregate visual summary. The curated table behind the public summary is available as [`private_context_subgroup_summary.csv`](../evidence/tables/private_context_subgroup_summary.csv); raw patient-level subgroup predictions are not included.

![Subgroup AUC forest](../evidence/figures/subgroup_auc_forest.svg)

Subgroup AUC analysis is descriptive. It evaluates whether discrimination differs across clinically relevant strata and whether subgroup estimates are stable enough to interpret. It is not a causal analysis and does not establish differential clinical utility.

![Imaging finding event-rate comparison](../evidence/figures/imaging_findings_event_rate.svg)

![Imaging finding AUC comparison](../evidence/figures/imaging_findings_auc.svg)

Visible imaging findings define clinically enriched groups with much higher short-horizon event rates. Within those enriched groups, Original Mirai showed lower within-subgroup AUC for several findings. That pattern helped motivate a strict distinction between the general risk-prediction origin and the later post-screen triage task.

## Public boundary

The figures and compact tables in this document are aggregate evidence summaries. The repository does not publish the raw capstone source file, patient-level predictions, internal variable mappings, source extracts, or the full private output directory.
