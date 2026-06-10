"""Unit tests for the phase-1.5 control-flip metrics."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.fc_phase15.metrics import (  # noqa: E402
    controller_signs,
    count_controller_changes,
)


class _FakeEngine:
    def __init__(self, bv):
        self.board_values = np.asarray(bv, dtype=np.float64)


def test_controller_signs_trichotomy() -> None:
    e = _FakeEngine([0.5, -0.5, 0.25, -0.25, 0.0, 0.26])
    s = controller_signs(e, margin=0.25)
    assert s.tolist() == [1, -1, 0, 0, 0, 1]


def test_count_controller_changes() -> None:
    a = np.array([1, -1, 0, 0], dtype=np.int8)
    b = np.array([1, 0, -1, 0], dtype=np.int8)
    assert count_controller_changes(a, b) == 2
    assert count_controller_changes(a, a) == 0
