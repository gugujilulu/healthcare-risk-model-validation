# Model and task interpretation

## Fixed baseline risk model

The baseline input is treated as a fixed set of horizon-specific risk probabilities produced by an existing image-based model. The public reconstruction does not train images or alter image-network weights.

## Local adaptation

Local adaptation means prediction-level model updating:

`fixed baseline probability + structured pre-screen variables -> updated local probability`

The public implementation demonstrates both an interpretable logistic layer and a nonlinear LightGBM layer.

## Calibration vs model updating

Recalibration changes the probability mapping of an existing score. Model updating adds structured predictors and can change patient ranking as well as calibration. The repository keeps these ideas separate.

## Temporal validation

Future-period evaluation is treated as a transportability stress test. A reduction in gain under temporal holdout is substantively important because it can reveal cohort, calendar-time, missingness, or workflow effects that are less visible under random splitting.

## Separate post-screen triage task

Post-screen findings and result categories are information available after the screening exam. They can provide a strong short-horizon triage signal, but they answer a later-time prediction question.

The repository therefore isolates them in `src/post_screen.py` and never allows them into the main pre-screen/general adaptation feature set.
