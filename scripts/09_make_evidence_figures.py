#!/usr/bin/env python3
"""Generate public-safe evidence figures from curated aggregate context tables.

These figures are intentionally aggregate-only. They do not require or expose
patient-level data, exam-level private predictions, or internal field mappings.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "evidence" / "tables"
FIGURES = ROOT / "evidence" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["font.size"] = 9

def load(name):
    return pd.read_csv(TABLES / name)

def finish(fig, name):
    fig.tight_layout()
    fig.savefig(FIGURES / name, format="svg", bbox_inches="tight")
    plt.close(fig)

def main():
    cohort = load("private_context_cohort_summary.csv")
    full = load("private_context_full_cohort_baseline_metrics.csv")
    held = load("private_context_heldout_baseline_metrics.csv")
    logit = load("private_context_logistic_update_summary.csv")
    adapt = load("private_context_adaptation_summary.csv")
    boot = load("private_context_bootstrap_summary.csv")
    temporal = load("private_context_temporal_summary.csv")
    first = load("private_context_first_exam_summary.csv")
    post = load("private_context_post_screen_summary.csv")
    dca = load("private_context_dca_summary.csv")
    high = load("private_context_high_risk_capture.csv")
    rec = load("private_context_recalibration_summary.csv")
    subgroup = load("private_context_subgroup_summary.csv")
    imaging = load("private_context_imaging_findings_summary.csv")

    x = np.arange(5)
    horizons = [f"{i}y" for i in range(1, 6)]

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(x, full.auc, marker="o", label="Capstone full-cohort external validation")
    ax.fill_between(x, full.ci_low, full.ci_high, alpha=.12)
    ax.plot(x, held.auc, marker="o", linestyle="--", label="Independent-extension held-out baseline")
    ax.set_xticks(x, horizons); ax.set_ylim(.62, .78); ax.set_ylabel("ROC AUC")
    ax.set_title("Original Mirai external validation across cumulative horizons")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    ax.text(.01, -.19, "Aggregate private-project context; no patient-level predictions are included.",
            transform=ax.transAxes, fontsize=8)
    finish(fig, "external_validation_auc_1_5yr.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.axhline(1, color="gray", lw=1, ls="--", label="E/O = 1")
    ax.plot(x, full.e_o_ratio, marker="o", label="Capstone full cohort")
    ax.plot(x, held.e_o_ratio, marker="o", ls="--", label="Held-out baseline")
    ax.set_xticks(x, horizons); ax.set_ylabel("Expected / observed events (E/O)")
    ax.set_title("Calibration burden varies by horizon")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    ax.text(.01, -.19, "E/O complements Brier score, calibration intercept/slope, and grouped calibration.",
            transform=ax.transAxes, fontsize=8)
    finish(fig, "external_validation_calibration_context.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.bar(x, cohort.eligible_exams / 1000, label="Eligible exams (thousands)", alpha=.8)
    ax.set_ylabel("Eligible exams (thousands)"); ax.set_xticks(x, horizons)
    ax2 = ax.twinx(); ax2.plot(x, cohort.event_rate_percent, marker="o", label="Event rate (%)")
    ax2.set_ylabel("Cumulative event rate (%)")
    ax.set_title("Horizon-specific follow-up availability")
    ax.grid(axis="y", alpha=.2)
    l1, a1 = ax.get_legend_handles_labels(); l2, a2 = ax2.get_legend_handles_labels()
    ax.legend(l1 + l2, a1 + a2, frameon=False, fontsize=8, loc="upper left")
    finish(fig, "followup_availability.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(x, adapt.original_heldout_auc, marker="o", label="Original Mirai")
    ax.plot(x, logit.logistic_updated_auc, marker="o", label="Logistic updated")
    ax.plot(x, adapt.best_observed_adapted_auc, marker="o", label="Best observed adapted")
    ax.set_xticks(x, horizons); ax.set_ylim(.66, .86); ax.set_ylabel("ROC AUC")
    ax.set_title("Independent extension: observed held-out local adaptation")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    ax.text(.01, -.19, "Exploratory held-out context; public runnable code uses a locked-test protocol.",
            transform=ax.transAxes, fontsize=8)
    finish(fig, "local_adaptation_auc_summary.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(x, held.brier, marker="o", label="Original Mirai")
    ax.plot(x, logit.logistic_updated_brier, marker="o", label="Logistic updated")
    ax.plot(x, adapt.adapted_brier, marker="o", label="Best observed adapted")
    ax.set_xticks(x, horizons); ax.set_ylabel("Brier score"); ax.set_title("Probability error across horizons")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "brier_score_comparison.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.axhline(1, color="gray", ls="--", lw=1)
    ax.plot(x, held.e_o_ratio, marker="o", label="Original Mirai")
    ax.plot(x, logit.logistic_updated_e_o_ratio, marker="o", label="Logistic updated")
    ax.plot(x, adapt.adapted_e_o_ratio, marker="o", label="Best observed adapted")
    ax.set_xticks(x, horizons); ax.set_ylabel("Expected / observed events (E/O)")
    ax.set_title("Aggregate calibration burden across horizons")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "eo_ratio_comparison.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.axhline(1, color="gray", ls="--", lw=1, label="Ideal = 1")
    ax.plot(x, held.calibration_slope, marker="o", label="Original held-out calibration slope")
    ax.plot(x, rec.recalibration_slope_beta, marker="o", label="Recalibration fitted beta")
    ax.set_xticks(x, horizons); ax.set_ylabel("Slope"); ax.set_title("Probability-scale recalibration parameters")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "calibration_before_after.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(x, adapt.delta_auc, marker="o", label="Random patient-split observed ΔAUC")
    ax.plot(x, temporal.delta_auc, marker="o", label="Future-period temporal ΔAUC")
    ax.axhline(0, color="gray", lw=1)
    ax.set_xticks(x, horizons); ax.set_ylabel("ΔAUC vs Original Mirai")
    ax.set_title("Temporal validation contracts random-split gains")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "temporal_validation_contraction.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    y = boot.delta_auc_mean.to_numpy()
    lo = y - boot.delta_auc_ci_low.to_numpy()
    hi = boot.delta_auc_ci_high.to_numpy() - y
    ax.errorbar(x, y, yerr=np.vstack([lo, hi]), fmt="o", capsize=4)
    ax.axhline(0, color="gray", lw=1)
    ax.set_xticks(x, horizons); ax.set_ylabel("Paired ΔAUC")
    ax.set_title("Patient-cluster bootstrap: adapted vs Original Mirai")
    ax.grid(axis="y", alpha=.25)
    finish(fig, "bootstrap_delta_auc_ci.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(x, first.original_auc, marker="o", label="Original Mirai")
    ax.plot(x, first.logistic_updated_auc, marker="o", label="Logistic updated")
    ax.plot(x, first.final_tuned_auc, marker="o", label="Final tuned")
    ax.set_xticks(x, horizons); ax.set_ylabel("ROC AUC"); ax.set_ylim(.64, .85)
    ax.set_title("First-exam-only sensitivity: discrimination")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "first_exam_only_auc.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(x, first.original_brier, marker="o", label="Original Mirai")
    ax.plot(x, first.logistic_updated_brier, marker="o", label="Logistic updated")
    ax.plot(x, first.final_tuned_brier, marker="o", label="Final tuned")
    ax.set_xticks(x, horizons); ax.set_ylabel("Brier score")
    ax.set_title("First-exam-only sensitivity: probability error")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "first_exam_only_brier.svg")

    s = subgroup.copy()
    labels = (s.dimension.astype(str) + " — " + s.subgroup_clean.astype(str)).tolist()
    yy = np.arange(len(s))[::-1]
    fig, ax = plt.subplots(figsize=(8.4, max(6, .28 * len(s) + 1.5)))
    auc = s.auc.to_numpy(); lo = auc - s.ci_low.to_numpy(); hi = s.ci_high.to_numpy() - auc
    ax.errorbar(auc, yy, xerr=np.vstack([lo, hi]), fmt="o", capsize=2, markersize=3)
    ax.axvline(full.loc[0, "auc"], color="gray", ls="--", lw=1,
               label=f"Overall 1y AUC {full.loc[0, 'auc']:.3f}")
    ax.set_yticks(yy, labels); ax.set_xlim(.56, .90); ax.set_xlabel("ROC AUC (95% CI)")
    ax.set_title("1-year subgroup discrimination — descriptive analysis")
    ax.grid(axis="x", alpha=.2); ax.legend(frameon=False, fontsize=8, loc="lower right")
    finish(fig, "subgroup_auc_forest.svg")

    has = imaging[imaging.finding_status == "Has"].copy()
    no = imaging[imaging.finding_status == "No"].copy()
    findings = has.finding.tolist(); yy = np.arange(len(findings))
    no_er = no.set_index("finding").event_rate_pct; has_er = has.set_index("finding").event_rate_pct
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.scatter([no_er[f] for f in findings], yy, label="Finding absent")
    ax.scatter([has_er[f] for f in findings], yy, label="Finding present")
    for i, f in enumerate(findings): ax.plot([no_er[f], has_er[f]], [i, i], alpha=.45)
    ax.set_yticks(yy, findings); ax.set_xlabel("1-year observed event rate (%)")
    ax.set_title("Imaging findings define enriched short-horizon subgroups")
    ax.grid(axis="x", alpha=.2); ax.legend(frameon=False, fontsize=8)
    finish(fig, "imaging_findings_event_rate.svg")

    no_auc = no.set_index("finding").auc; has_auc = has.set_index("finding").auc
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.scatter([no_auc[f] for f in findings], yy, label="Finding absent")
    ax.scatter([has_auc[f] for f in findings], yy, label="Finding present")
    for i, f in enumerate(findings): ax.plot([no_auc[f], has_auc[f]], [i, i], alpha=.45)
    ax.set_yticks(yy, findings); ax.set_xlabel("1-year ROC AUC")
    ax.set_title("Within-subgroup discrimination after current findings are known")
    ax.grid(axis="x", alpha=.2); ax.legend(frameon=False, fontsize=8)
    finish(fig, "imaging_findings_auc.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for h, label in [("1yr", "1y"), ("5yr", "5y")]:
        d = high[high.horizon == h]
        ax.plot(d.threshold_pct * 100, d.sensitivity_cancer_capture * 100, marker="o", label=label)
    ax.set_xticks([1, 5, 10, 20]); ax.set_xlabel("Top-risk group size (%)")
    ax.set_ylabel("Cancer case capture (%)"); ax.set_title("Capacity-based high-risk stratification")
    ax.grid(alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "high_risk_capture.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    labels = (dca.horizon.astype(str) + " " + dca.threshold_range.astype(str)).tolist()
    vals = dca.mean_net_benefit_delta_vs_original.to_numpy()
    ax.barh(np.arange(len(vals)), vals)
    ax.set_yticks(np.arange(len(vals)), labels); ax.invert_yaxis()
    ax.set_xlabel("Mean net-benefit Δ vs Original Mirai")
    ax.set_title("Decision-curve summary across threshold ranges")
    ax.grid(axis="x", alpha=.25)
    finish(fig, "decision_curve_summary.svg")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for task, label in [("original_mirai", "Original Mirai"),
                        ("final_pre_screen", "Final pre-screen"),
                        ("post_screen_calibrated", "Post-screen triage")]:
        d = post[post.task == task]
        ax.plot([0, 1], d.auc, marker="o", label=label)
    ax.set_xticks([0, 1], ["1y", "2y"]); ax.set_ylim(.70, 1.0); ax.set_ylabel("ROC AUC")
    ax.set_title("Post-screen triage is a separate, later-time task")
    ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, fontsize=8)
    finish(fig, "post_screen_triage_summary.svg")

    print(f"Saved aggregate evidence figures to {FIGURES}")

if __name__ == "__main__":
    main()
