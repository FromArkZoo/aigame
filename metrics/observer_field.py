"""Measurement-only observer influence field (RC2 Phase A).

Computes the influence field a game WOULD have under the validated
Field-Connect parameterization (r=2, strength 1.0, decay 0.5), from board
ownership alone. Pure function: never written to engine state, never read
by legality/wins/observations. Exists because generator_v2.py:209-228 forces
prop_type='none' for non-threshold win conditions, leaving board_values at
zero — which made every field-based behavior descriptor structurally dead
for most of the genome space (the fact that killed both QD pivot candidates
at the panel screen).

Parity guarantee: reuses engine_v2._influence_kernels (same cache, same
weights, same clip), so for an influence game with matching params the
observer field is array-equal to the engine's _recompute_field result.
"""
from __future__ import annotations

import numpy as np

from game_engine.engine_v2 import _influence_kernels

OBSERVER_RADIUS = 2
OBSERVER_STRENGTH = 1.0
OBSERVER_DECAY = 0.5


def observer_field(
    topo,
    board_owners: np.ndarray,
    radius: int = OBSERVER_RADIUS,
    strength: float = OBSERVER_STRENGTH,
    decay: float = OBSERVER_DECAY,
) -> np.ndarray:
    """Influence field implied by current stone ownership (P1 +, P2 -)."""
    field = np.zeros(topo.total_cells, dtype=np.float64)
    kernels = _influence_kernels(topo, radius, strength, decay)
    for cell in topo.active_cells:
        owner = int(board_owners[cell])
        if owner != 0:
            idx, w = kernels[cell]
            field[idx] += (1.0 if owner == 1 else -1.0) * w
    np.clip(field, -100.0, 100.0, out=field)
    return field
