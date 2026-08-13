# Evaluation Protocol

## Public reconstruction: locked-test design

The public pipeline deliberately separates model development from final evaluation:

1. **Train:** fit candidate local-updating models.
2. **Validation-calibration subset:** fit probability calibrators.
3. **Validation-selection subset:** select model class and calibration method.
4. **Lock the selected model.**
5. **Test:** evaluate the locked model once and compare it with the fixed baseline prediction.

The validation split is divided at patient level so repeated exams from one patient do not cross calibration and selection subsets.

## Why this differs from the retrospective exploratory workflow

The private independent extension was exploratory and compared multiple model, calibration, and blending alternatives on held-out data. Some final "best observed" choices were therefore informed by held-out performance.

For that reason, private headline adaptation values are described as **observed exploratory held-out performance**. They should not be read as estimates from a single model whose entire design was fixed before any test-set comparison.

The public reconstruction keeps the scientific questions but implements a cleaner evaluation protocol suitable for a reusable technical demonstration.

## Capstone vs independent-extension evaluation contexts

Two historical evaluation contexts remain distinct:

- the capstone external-validation analysis used the full eligible screening cohort as the primary Original Mirai evaluation context;
- the independent extension introduced a patient-level train / validation / test framework for model updating.

Local-adaptation gains belong to the latter held-out framework and should not be calculated by mixing metrics from the two contexts.

## How this repository handles two evidence layers

This repository has two evidence layers:

1. **Private retrospective evidence context:** curated aggregate summaries from the original capstone and independent extension.
2. **Public runnable reconstruction:** synthetic data and generic schema implementing a cleaner locked-test protocol.

These layers should not be confused. Private headline results document the original exploratory project. Public synthetic outputs demonstrate how the methodology is implemented.
