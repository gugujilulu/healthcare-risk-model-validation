from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .metrics import calibration_table


def _save(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_auc_comparison(summary: pd.DataFrame, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    x = summary["horizon_years"]
    ax.plot(x, summary["original_auc"], marker="o", label="Baseline risk model")
    ax.plot(x, summary["adapted_auc"], marker="o", label="Locally updated model")
    ax.set_xlabel("Prediction horizon (years)")
    ax.set_ylabel("ROC AUC")
    ax.set_xticks(x)
    ax.set_title("Synthetic demo: discrimination across horizons")
    ax.grid(alpha=.25)
    ax.legend()
    _save(fig, path)


def plot_calibration(predictions: pd.DataFrame, horizon: str, path):
    d = predictions[predictions["horizon"] == horizon]
    c0 = calibration_table(d["label"], d["original_mirai"])
    c1 = calibration_table(d["label"], d["adapted_model"])
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    ax.plot([0, 1], [0, 1], linestyle="--", label="Perfect calibration")
    ax.plot(c0["mean_predicted_risk"], c0["observed_event_rate"], marker="o", label="Baseline")
    ax.plot(c1["mean_predicted_risk"], c1["observed_event_rate"], marker="o", label="Updated")
    mx = max(c0["mean_predicted_risk"].max(), c1["mean_predicted_risk"].max(), c0["observed_event_rate"].max(), c1["observed_event_rate"].max())
    ax.set_xlim(0, mx * 1.08)
    ax.set_ylim(0, mx * 1.08)
    ax.set_xlabel("Mean predicted risk")
    ax.set_ylabel("Observed event rate")
    ax.set_title(f"Synthetic demo: calibration ({horizon})")
    ax.legend()
    ax.grid(alpha=.2)
    _save(fig, path)


def plot_bootstrap_ci(boot: pd.DataFrame, path):
    d = boot.copy().sort_values("horizon")
    y = np.arange(len(d))
    mean = d["delta_auc_mean"].to_numpy()
    lo = d["delta_auc_ci_low"].to_numpy()
    hi = d["delta_auc_ci_high"].to_numpy()
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.errorbar(mean, y, xerr=[mean-lo, hi-mean], fmt="o", capsize=4)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.set_yticks(y, d["horizon"])
    ax.set_xlabel("ΔAUC (updated − baseline)")
    ax.set_title("Synthetic demo: patient-cluster bootstrap")
    ax.grid(axis="x", alpha=.25)
    _save(fig, path)


def plot_temporal(temporal: pd.DataFrame, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    x = temporal["horizon"].str.replace("yr", "").astype(int)
    ax.plot(x, temporal["original_auc"], marker="o", label="Baseline")
    ax.plot(x, temporal["adapted_auc"], marker="o", label="Updated")
    ax.set_xlabel("Prediction horizon (years)")
    ax.set_ylabel("ROC AUC")
    ax.set_xticks(x)
    ax.set_title("Synthetic demo: future-period temporal validation")
    ax.grid(alpha=.25)
    ax.legend()
    _save(fig, path)


def plot_decision_curve(dca: pd.DataFrame, path, title="Synthetic demo: decision curve"):
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for model, g in dca.groupby("model"):
        ax.plot(g["threshold"], g["net_benefit"], label=model)
    ax.set_xlabel("Risk threshold")
    ax.set_ylabel("Net benefit")
    ax.set_title(title)
    ax.grid(alpha=.25)
    ax.legend(fontsize=8)
    _save(fig, path)
