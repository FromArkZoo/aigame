"""Phase-1.5 screen metrics (pre-registered in PREREGISTRATION.md).

control_flip_rate: per non-swap ply, the number of cells whose controller
sign (+1 P1 / -1 P2 / 0 contested, at the game's control margin) changed
vs the previous ply. Pie-swap plies are excluded by the caller — the swap
negates the whole field and would register ~half the board as flipped.
"""
from __future__ import annotations

import numpy as np


def controller_signs(engine, margin: float) -> np.ndarray:
    """Trichotomous controller array over all cells: {-1, 0, +1}."""
    bv = engine.board_values
    return (bv > margin).astype(np.int8) - (bv < -margin).astype(np.int8)


def count_controller_changes(prev: np.ndarray, cur: np.ndarray) -> int:
    """Cells whose controller sign differs between two snapshots."""
    return int(np.count_nonzero(prev != cur))
