"""Probe A/B — evaluator entry point. Usage:
    python evaluations/probe_ab/play.py --game Q [--moves "..."] [--rules] [--control]
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
runpy.run_path(str(ROOT / "experiments" / "field_connect_probe"
                   / "eval_helper.py"), run_name="__main__")
