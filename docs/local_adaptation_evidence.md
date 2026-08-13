# Local Adaptation Evidence

## 1. Model boundary

**Original Mirai is fixed.** The project does not retrain or fine-tune the image network. Local adaptation begins after Mirai inference:

```text
fixed horizon-specific Mirai probability
        + structured local variables
        -> locally updated probability
```

This distinction matters because recalibration, logistic updating, and LightGBM updating operate on existing risk outputs; none changes the original image-network weights.

## 2. Logistic recalibration

Horizon-specific logistic recalibration changes the probability scale while preserving rank order under a monotone map.

| Horizon | Intercept α | Slope β |
|---|---:|---:|
| 1 year | -0.766455 | 0.781502 |
| 2 years | -0.662342 | 0.863072 |
| 3 years | -0.414324 | 0.908135 |
| 4 years | -0.387337 | 0.894726 |
| 5 years | -0.131518 | 0.899491 |

AUC is unchanged by monotone recalibration; Brier, E/O, calibration intercept, and calibration slope can change materially.

![Calibration before and after local adjustment](../evidence/figures/calibration_before_after.svg)

*Aggregate context from the private retrospective analysis.*

## 3. Logistic model updating

The interpretable local benchmark combines the fixed Mirai risk with structured pre-screen variables through regularized multivariable logistic regression.

| Horizon | Original AUC | Logistic Updated AUC | ΔAUC | Logistic Updated E/O |
|---|---:|---:|---:|---:|
| 1 year | 0.742 | 0.790 | +0.048 | 1.078 |
| 2 years | 0.740 | 0.773 | +0.032 | 1.091 |
| 3 years | 0.715 | 0.741 | +0.026 | 1.044 |
| 4 years | 0.703 | 0.722 | +0.019 | 1.034 |
| 5 years | 0.691 | 0.718 | +0.028 | 1.036 |

The logistic model establishes that local structured information adds discrimination beyond the fixed image-model score before nonlinear tree models are introduced.

## 4. Tuned and calibrated LightGBM

LightGBM was used to capture nonlinear relationships and interactions among fixed Mirai outputs and local structured variables. Because rare-event training used negative downsampling in the private workflow, raw tree probabilities required calibration before absolute-risk interpretation.

### Best observed exploratory held-out AUC by horizon

> The following table is a curated aggregate summary of observed exploratory held-out patterns from the private extension after public-safe reduction. It documents the project evidence chain and model-comparison structure and is kept separate from the synthetic locked-test pipeline.

| Horizon | Original held-out AUC | Best observed adapted AUC | ΔAUC | Selected private candidate |
|---|---:|---:|---:|---|
| 1 year | 0.742 | 0.835 | +0.093 | second-round tuned LightGBM + Platt |
| 2 years | 0.740 | 0.825 | +0.085 | second-round tuned LightGBM + Platt |
| 3 years | 0.715 | 0.774 | +0.059 | first-round tuned LightGBM + beta-style calibration |
| 4 years | 0.703 | 0.791 | +0.088 | second-round tuned LightGBM + Platt |
| 5 years | 0.691 | 0.811 | +0.120 | first-round tuned LightGBM + beta-style calibration |

![Local adaptation AUC summary](../evidence/figures/local_adaptation_auc_summary.svg)

![Brier comparison](../evidence/figures/brier_score_comparison.svg)

![E/O comparison](../evidence/figures/eo_ratio_comparison.svg)

These are **observed exploratory held-out results** from the private independent extension. Candidate choices were informed by held-out comparisons, whereas the public reconstruction implements a cleaner validation-selection / locked-test protocol.

The public reconstruction protocol is:

```text
train -> validation calibration / selection -> lock -> one final test evaluation
```

See [`evaluation_protocol.md`](evaluation_protocol.md).

## 5. Horizon-specific winners are part of the finding

The private analysis did not produce one universal five-horizon adapter. Different candidate variants/calibration methods won the AUC comparison at different horizons. That is preserved in the public evidence narrative rather than simplified into a single model claim.

The curated context tables are in [`evidence/tables/`](../evidence/tables/), especially:

- `private_context_recalibration_summary.csv`
- `private_context_logistic_update_summary.csv`
- `private_context_adaptation_summary.csv`
