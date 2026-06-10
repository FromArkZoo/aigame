"""Stage 3 blind eval — evaluator entry point. Usage:
    python evaluations/stage3_ab/play.py --game D [--moves "..."] [--rules] [--control]
    python evaluations/stage3_ab/play.py --game V [--moves "..."] [--rules] [--control]
    python evaluations/stage3_ab/play.py --game X [--moves "..."] [--rules] [--control]
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
runpy.run_path(str(ROOT / "experiments" / "siege" / "eval_helper.py"),
               run_name="__main__")
