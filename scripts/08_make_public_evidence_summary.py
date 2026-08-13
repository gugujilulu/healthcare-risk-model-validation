#!/usr/bin/env python3
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _fmt(x, digits=3):
    return f"{float(x):.{digits}f}"


def main():
    evidence = ROOT / "evidence" / "tables"
    report_dir = ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    cohort = pd.read_csv(evidence / "private_context_cohort_summary.csv")
    baseline = pd.read_csv(evidence / "private_context_heldout_baseline_metrics.csv")
    adapted = pd.read_csv(evidence / "private_context_adaptation_summary.csv")
    temporal = pd.read_csv(evidence / "private_context_temporal_summary.csv")
    bootstrap = pd.read_csv(evidence / "private_context_bootstrap_summary.csv")
    post = pd.read_csv(evidence / "private_context_post_screen_summary.csv")

    max_exams = int(cohort["eligible_exams"].max())
    baseline_auc = f"{baseline['auc'].min():.3f}–{baseline['auc'].max():.3f}"
    adapted_auc = f"{adapted['best_observed_adapted_auc'].min():.3f}–{adapted['best_observed_adapted_auc'].max():.3f}"
    temporal_gain = f"+{temporal['delta_auc'].min():.3f} to +{temporal['delta_auc'].max():.3f}"
    bootstrap_min = bootstrap['delta_auc_ci_low'].min()
    triage_1 = post[(post.horizon == '1yr') & (post.task == 'post_screen_calibrated')].iloc[0]
    triage_2 = post[(post.horizon == '2yr') & (post.task == 'post_screen_calibrated')].iloc[0]

    text = f"""# Public Evidence Summary

## 1. Project question

Can a mammography-based risk model developed elsewhere be externally validated and locally adapted in a provincial screening cohort while preserving correct prediction-time, censoring, calibration, and transportability boundaries?

## 2. Validation foundation

- exam-level prediction origins with repeated exams per patient;
- 1–5 year cumulative endpoints;
- horizon-specific follow-up eligibility;
- patient-level splitting / clustered bootstrap;
- Original Mirai treated as a fixed image-model baseline.

The private retrospective project included up to **{max_exams:,} eligible screening exams** depending on horizon.

## 3. Baseline findings

In the independent-extension held-out framework, Original Mirai AUC ranged from approximately **{baseline_auc}** across the five cumulative horizons. Probability calibration varied by horizon, so AUC was interpreted alongside Brier score, E/O ratio, calibration intercept/slope, and grouped calibration.

## 4. Local adaptation findings

Local structured variables added retrospective discrimination beyond the fixed Mirai outputs. Logistic Updated served as an interpretable benchmark, while tuned and calibrated LightGBM produced the strongest **observed exploratory held-out** AUCs, approximately **{adapted_auc}** across horizons.

These headline values document the private exploratory project. The public reconstruction uses a cleaner validation-selection / locked-test protocol and does not claim that the private best-observed values came from a single pre-locked model.

## 5. Evidence strength

Paired patient-cluster bootstrap intervals for tuned-model ΔAUC versus Original Mirai remained positive in the held-out analysis; the lowest reported lower bound was approximately **{bootstrap_min:.3f}**. Temporal validation then provided the stronger stress test: the larger random-split gains contracted to approximately **{temporal_gain}** under future-period evaluation.

The correct interpretation is therefore bounded: the data contained substantial retrospective local signal, while only a smaller advantage transported to the tested later periods.

## 6. Robustness and prediction-time checks

The evidence chain also includes:

- first-exam-only sensitivity to reduce repeated-record weighting;
- subgroup discrimination and sample-size reliability checks;
- explicit feature-availability / leakage audit;
- high-risk capture and decision-curve analyses; and
- a separated post-screen triage task.

The calibrated post-screen branch reached approximately **{triage_1.auc:.3f} AUC at 1 year** and **{triage_2.auc:.3f} at 2 years**, reflecting access to later findings/result information. Those values answer a different prediction-time question from pre-screen/general risk updating.

## 7. Public reconstruction

The public codebase reproduces the analytical design with synthetic data and a generic feature schema. `python run_all.py` generates the synthetic cohort, builds cumulative endpoints, evaluates the fixed baseline, selects/calibrates local-updating models without using the test set for selection, runs robustness/temporal/post-screen analyses, and regenerates synthetic figures/tables.

The curated files under `evidence/` provide aggregate context only; they cannot reproduce the private clinical analysis without the underlying private data and source assets.

## 8. Non-claims

- no Mirai image-network fine-tuning;
- no official BC Cancer model release;
- no clinical deployment claim;
- no prospective utility claim;
- no patient-level data release;
- no claim that private exploratory best-observed results were generated under the public locked-test protocol.
"""

    out = report_dir / "public_evidence_summary.md"
    out.write_text(text, encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
