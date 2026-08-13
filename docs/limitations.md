# Limitations

- The public dataset is synthetic and cannot reproduce the clinical distribution of the private screening cohort.
- Synthetic figures demonstrate workflow behavior; curated files under `evidence/` provide aggregate retrospective context from a separate evidence layer.
- The original independent extension was exploratory, and some best-observed held-out choices were informed by held-out comparisons.
- The public reconstruction uses a cleaner selection protocol but does not retroactively change how the original exploratory values were obtained.
- Future-period temporal validation is a stronger stress test than random splitting but remains retrospective and within the same healthcare system.
- Prospective evaluation and operational study would be required to assess clinical utility, deployment behavior, treatment benefit, or resource-effectiveness.
- Decision-curve outputs depend on the threshold range, assumed action rule, and probability estimates.
- Subgroup analyses are descriptive and do not establish causal differences or subgroup-specific clinical utility.
- The post-screen triage branch is a separate prediction-time task from pre-screen/general long-term risk estimation.
- The baseline Mirai image network remains fixed throughout the project; adaptation occurs at the prediction level.
