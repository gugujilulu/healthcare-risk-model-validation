# Clinical-Use-Oriented Analyses

These analyses extend model evaluation toward possible use cases, but they remain retrospective analytical exercises rather than deployment claims.

## 1. High-risk stratification and case capture

Capacity-based top-risk groups ask a practical ranking question: if only a fixed fraction of exams can be prioritized, how concentrated are future events in that fraction?

Selected examples from the calibrated LightGBM analysis:

| Horizon | Top group | Exams | Cases | Event rate | Enrichment | Case capture |
|---|---:|---:|---:|---:|---:|---:|
| 1 year | top 1% | 220 | 20 | 9.09% | 15.83x | 15.87% |
| 1 year | top 5% | 1,097 | 44 | 4.01% | 6.98x | 34.92% |
| 1 year | top 10% | 2,194 | 60 | 2.73% | 4.76x | 47.62% |
| 1 year | top 20% | 4,388 | 83 | 1.89% | 3.29x | 65.87% |
| 5 years | top 5% | 762 | 169 | 22.18% | 8.60x | 43.00% |
| 5 years | top 20% | 3,047 | 255 | 8.37% | 3.24x | 64.89% |

![High-risk cancer capture](../evidence/figures/high_risk_capture.svg)

Rank-based top-p% groups should not be confused with fixed probability thresholds. A top 5% group always selects 5% of eligible exams even when calibration changes.

## 2. Decision Curve Analysis

Decision Curve Analysis (DCA) evaluates threshold-defined net benefit, explicitly weighting false positives according to the chosen risk threshold.

![Decision curve analysis](../evidence/figures/decision_curve_summary.svg)

Selected average net-benefit differences for the final tuned LightGBM versus Original Mirai were positive across all evaluated thresholds in the summarized bands:

| Horizon | Threshold band | Mean Δ net benefit vs Original | Thresholds above Original |
|---|---:|---:|---:|
| 1 year | 0.1%–1% | 0.000840 | 100% |
| 1 year | 1%–5% | 0.000366 | 100% |
| 1 year | 5%–10% | 0.000317 | 100% |
| 5 years | 0.5%–5% | 0.004867 | 100% |
| 5 years | 5%–15% | 0.007697 | 100% |
| 5 years | 15%–30% | 0.007562 | 100% |

DCA is **not** a deployment recommendation. It evaluates conditional net benefit under a stated threshold rule and retrospective probability estimates; it does not establish actual downstream outcomes, costs, workflow burden, or a universally correct action threshold.

## 3. Model blending

The independent extension also tested probability-scale and logit-scale blends of Logistic Updated and tuned LightGBM predictions. Some combinations produced small additional AUC gains, but the incremental improvement was limited and the weights were explored post hoc.

For that reason, blending is retained as an exploratory analysis rather than promoted as the main model-development conclusion.

## 4. Separate post-screen triage task

Current findings and result category become available after the screening encounter and therefore define a different prediction-time question. The post-screen branch combines the corresponding horizon-specific Mirai risk with structured variables and later-time findings/result information.

| Horizon | Model / task | AUC | Brier | E/O |
|---|---|---:|---:|---:|
| 1 year | Original Mirai | 0.742 | 0.005611 | 0.881 |
| 1 year | final pre-screen tuned model | 0.835 | 0.005487 | 0.941 |
| 1 year | calibrated post-screen triage | 0.964 | 0.004218 | 0.860 |
| 2 years | Original Mirai | 0.740 | 0.007718 | 1.210 |
| 2 years | final pre-screen tuned model | 0.825 | 0.007543 | 0.941 |
| 2 years | calibrated post-screen triage | 0.913 | 0.006542 | 0.909 |

![Post-screen triage summary](../evidence/figures/post_screen_triage_summary.svg)

The higher short-horizon AUC is expected because the triage model has access to later information. It should not be presented as an improvement to the original pre-screen/general long-term risk task.
