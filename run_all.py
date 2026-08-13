#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
STAGES = [
    "01_generate_synthetic_data.py",
    "02_external_validation.py",
    "03_local_adaptation.py",
    "04_robustness.py",
    "05_temporal_validation.py",
    "06_post_screen_triage.py",
    "07_make_figures.py",
    "08_make_public_evidence_summary.py",
    "09_make_evidence_figures.py",
]


def main():
    env = os.environ.copy()
    # Keep CI and local runs deterministic and avoid thread oversubscription.
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    for stage in STAGES:
        print(f"\n=== {stage} ===", flush=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / stage)], check=True, cwd=ROOT, env=env)
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
