from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_EVIDENCE_FIGURES = [
    "evidence/figures/external_validation_auc_1_5yr.svg",
    "evidence/figures/external_validation_calibration_context.svg",
    "evidence/figures/local_adaptation_auc_summary.svg",
    "evidence/figures/temporal_validation_contraction.svg",
    "evidence/figures/bootstrap_delta_auc_ci.svg",
    "evidence/figures/first_exam_only_auc.svg",
    "evidence/figures/first_exam_only_brier.svg",
    "evidence/figures/subgroup_auc_forest.svg",
    "evidence/figures/post_screen_triage_summary.svg",
    "evidence/figures/original_style/external_validation_roc_curves_1_5yr.png",
    "evidence/figures/original_style/external_validation_calibration_decile_1_5yr.png",
    "evidence/figures/original_style/subgroup_auc_forest_1yr.png",
    "evidence/figures/original_style/first_exam_only_auc.png",
    "evidence/figures/original_style/first_exam_only_brier.png",
]

REQUIRED_EVIDENCE_TABLES = [
    "evidence/tables/private_context_cohort_summary.csv",
    "evidence/tables/private_context_full_cohort_baseline_metrics.csv",
    "evidence/tables/private_context_heldout_baseline_metrics.csv",
    "evidence/tables/private_context_adaptation_summary.csv",
    "evidence/tables/private_context_bootstrap_summary.csv",
    "evidence/tables/private_context_temporal_summary.csv",
    "evidence/tables/private_context_first_exam_summary.csv",
    "evidence/tables/private_context_post_screen_summary.csv",
]


def test_required_evidence_figures_exist():
    missing = [p for p in REQUIRED_EVIDENCE_FIGURES if not (ROOT / p).exists()]
    assert not missing, f"Missing evidence figures: {missing}"


def test_required_evidence_tables_exist():
    missing = [p for p in REQUIRED_EVIDENCE_TABLES if not (ROOT / p).exists()]
    assert not missing, f"Missing evidence tables: {missing}"
