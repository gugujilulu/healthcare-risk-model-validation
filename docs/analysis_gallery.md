# Analysis Gallery

All figures in this gallery are generated from **curated aggregate project-context tables**. They contain no patient-level records, no exam-level private predictions, and no internal BC Cancer field mappings. Synthetic runnable outputs live separately under `results/`.

## Original-style aggregate figures

These figures are static aggregate visual summaries from the private retrospective analysis. They preserve the visual evidence structure of the original project while keeping patient-level data, ROC coordinate tables, prediction rows, internal mappings, and private scripts out of the public repository.

### ROC curves across 1–5 year horizons

![ROC curves](../evidence/figures/original_style/external_validation_roc_curves_1_5yr.png)

This figure shows the original external-validation ROC curves and horizon-specific AUC confidence intervals. It provides the clearest visual evidence of the baseline discrimination analysis.

### Decile calibration across 1–5 year horizons

![Calibration deciles](../evidence/figures/original_style/external_validation_calibration_decile_1_5yr.png)

This figure shows grouped observed event rates against mean predicted risks. It demonstrates why calibration was evaluated separately from AUC.

### Subgroup AUC forest plot

![Subgroup AUC forest](../evidence/figures/original_style/subgroup_auc_forest_1yr.svg)

The subgroup forest plot summarizes descriptive discrimination heterogeneity across density, age, ethnicity, family history, and imaging-finding strata. It is not interpreted as causal evidence or as proof of clinical utility.

### First-exam-only sensitivity: AUC

![First-exam AUC](../evidence/figures/original_style/first_exam_only_auc.svg)

This analysis checks whether discrimination patterns persist after reducing repeated exams to one earliest observed exam per patient.

### First-exam-only sensitivity: Brier score

![First-exam Brier](../evidence/figures/original_style/first_exam_only_brier.svg)

This companion figure evaluates probability error, not only ranking, under the first-exam-only sensitivity design.

## A. External validation

### A1. Original Mirai discrimination across 1–5 year horizons
![External validation AUC](../evidence/figures/external_validation_auc_1_5yr.svg)

The capstone full-cohort external-validation context and the later independent-extension held-out baseline are shown separately. This avoids collapsing two different evaluation populations into one performance series.

### A2. Calibration burden across horizons
![Calibration context](../evidence/figures/external_validation_calibration_context.svg)

Expected/observed burden varies by horizon. E/O is interpreted together with Brier score, calibration intercept/slope, and grouped observed-versus-predicted risk.

### A3. Follow-up availability
![Follow-up availability](../evidence/figures/followup_availability.svg)

Eligibility declines at the longer horizons because later screening exams do not all have complete 4–5 year follow-up. This is why horizon-specific denominators are required.

### A4. Subgroup discrimination
![Subgroup forest](../evidence/figures/subgroup_auc_forest.svg)

Subgroup AUC is descriptive and uncertainty is shown explicitly. Small groups with insufficient cases are excluded from the public forest rather than presented as stable estimates.

### A5. Imaging-finding deep dive
![Imaging event rate](../evidence/figures/imaging_findings_event_rate.svg)

![Imaging AUC](../evidence/figures/imaging_findings_auc.svg)

Current imaging findings identify strongly enriched short-horizon groups while also changing the within-group discrimination problem. This helped motivate a strict prediction-time boundary between general risk updating and post-screen triage.

## B. Local adaptation

### B1. Held-out AUC comparison
![Local adaptation AUC](../evidence/figures/local_adaptation_auc_summary.svg)

The independent extension compared Original Mirai, an interpretable logistic update, and stronger nonlinear local updating. The strongest values are reported as observed exploratory held-out performance.

### B2. Probability error
![Brier comparison](../evidence/figures/brier_score_comparison.svg)

Brier score is tracked separately from ranking performance.

### B3. Aggregate calibration burden
![E/O comparison](../evidence/figures/eo_ratio_comparison.svg)

E/O provides a direct summary of predicted versus observed event burden.

### B4. Recalibration parameters
![Calibration parameters](../evidence/figures/calibration_before_after.svg)

Monotonic recalibration corrects probability scale but does not create new ranking information.

## C. Robustness and transportability

### C1. Patient-cluster bootstrap
![Bootstrap delta AUC](../evidence/figures/bootstrap_delta_auc_ci.svg)

Paired bootstrap resampling occurs at patient level so repeated exams remain clustered.

### C2. First-exam-only sensitivity
![First exam AUC](../evidence/figures/first_exam_only_auc.svg)

![First exam Brier](../evidence/figures/first_exam_only_brier.svg)

Reducing each patient to one earliest observed exam checks whether conclusions are driven only by repeated screening records.

### C3. Future-period temporal validation
![Temporal contraction](../evidence/figures/temporal_validation_contraction.svg)

Random patient-split gains contract markedly when models are evaluated on later screening periods. This is a central interpretation result.

## D. Clinical-use-oriented analyses

### D1. High-risk case capture
![High-risk capture](../evidence/figures/high_risk_capture.svg)

Capacity-based top-risk groups quantify concentration of observed cases without turning the analysis into a deployment recommendation.

### D2. Decision-curve summary
![DCA summary](../evidence/figures/decision_curve_summary.svg)

The figure summarizes retrospective net-benefit deltas over selected threshold ranges; it is not a prospective clinical-utility claim.

### D3. Post-screen triage
![Post-screen triage](../evidence/figures/post_screen_triage_summary.svg)

Current findings/result information is used only in this later-time branch together with horizon-specific Mirai risk. It answers a different question from the main pre-screen/general risk-updating workflow.
