"""Fast tests for experiments/frontline/metrics.py (plan Task 11 Step 1).

Run via:
    .venv/bin/python -m pytest experiments/frontline/test_frontline_metrics.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.frontline.metrics import (  # noqa: E402
    score_share_progress,
    winner_behindness,
)


def test_score_share_progress_zero_scores_is_zero():
    # max(1, ...) guards the 0/0 ply: progress 0.0, not NaN.
    assert score_share_progress(0, 0) == 0.0


def test_score_share_progress_three_one():
    assert score_share_progress(3, 1) == 0.75


def test_winner_behindness_tied_trace_is_zero():
    # Never behind -> drama 0.0 (siege formula re-exported unchanged).
    assert winner_behindness([0.5], [0.5]) == 0.0
