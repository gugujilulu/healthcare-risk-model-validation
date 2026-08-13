#!/usr/bin/env python3
from pathlib import Path
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
]


def main():
    for stage in STAGES:
        print(f"\n=== {stage} ===", flush=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / stage)], check=True, cwd=ROOT)
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
