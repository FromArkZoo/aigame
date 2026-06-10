"""SIEGE screen metrics (pre-registered Stage 1.5/2 definitions).

Per-role progress traces, both normalized to [0,1]:
  - connection roles: span fraction along own target axis of the largest
    connected controlled component (control at the game's margin);
  - Breaker: max(quota_frac, step_frac) — quota and clock are both win paths.
    quota_frac may exceed 1.0 on a terminal move (per-move tick cap 2 can
    overshoot capture_quota); deliberately not clamped — the pre-registered
    formula has no clip, and overshoot only reduces 'behindness'.
Per-role drama = mean over plies of sqrt(max(0, loser_prog - winner_prog)).

Reuse decisions
---------------
IMPORTED from experiments.field_connect_probe.metrics:
  - controlled_sets(engine, margin) -> (p1_cells, p2_cells): exact match —
    P1 = {c: board_values[c] > margin}, P2 = {c: board_values[c] < -margin}.

REFERENCE (not imported):
  - largest_component(topo, cells): used as a structural REFERENCE for the
    flood-fill in maker_progress_span; it returns only the component SIZE,
    while the span metric needs the component's cell set to count distinct
    axis coords, so the algorithm is adapted inline to return the set.

NOT imported (new code below):
  - maker_progress_span: needs axis-span count of the largest component,
    not just its size. The probe's progress_diff_field returns a scalar
    difference of component sizes; it doesn't expose distinct-coord counting.
  - winner_behindness: new function; the probe has no per-role drama concept.
  - breaker_progress: new function; probe has no quota/clock composite.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import numpy as np

# Ensure repo root is importable regardless of how pytest is invoked.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from experiments.field_connect_probe.metrics import (  # noqa: E402
    controlled_sets,
)


# ---------------------------------------------------------------------------
# winner_behindness
# ---------------------------------------------------------------------------

def winner_behindness(
    winner_trace: Sequence[float],
    loser_trace: Sequence[float],
) -> float:
    """Per-role drama: mean over plies of sqrt(max(0, loser_prog - winner_prog)).

    Pre-registered formula (PREREGISTRATION.md Stage 1.5/2):
      drama = mean_t( sqrt( max(0, loser_t - winner_t) ) )

    Returns 0.0 on empty traces.
    """
    if len(winner_trace) == 0:
        return 0.0
    w = np.asarray(winner_trace, dtype=float)
    lo = np.asarray(loser_trace, dtype=float)
    return float(np.mean(np.sqrt(np.maximum(0.0, lo - w))))


# ---------------------------------------------------------------------------
# maker_progress_span
# ---------------------------------------------------------------------------

def maker_progress_span(
    engine,
    player: int,
    axis: int,
    margin: float,
) -> float:
    """Largest-controlled-component axis-span fraction for a connection role.

    Normalized to [0,1]: distinct values of coords[axis] present in the
    largest controlled component, divided by axis_size.

    Parameters
    ----------
    engine  : live EngineV2 instance
    player  : 1 or 2
    axis    : target dimension (0 for Maker in default SIEGE config)
    margin  : control margin from the game's WinCondition (typically 0.0)

    Algorithm
    ---------
    1. Extract controlled cell-sets via the probe's controlled_sets().
    2. Find the largest connected component (via the probe's largest_component
       flooding, adapted to return the component itself, not just its size).
    3. Count distinct axis coords in that component / axis_size.
    """
    p1_cells, p2_cells = controlled_sets(engine, margin)
    cells = p1_cells if player == 1 else p2_cells

    if not cells:
        return 0.0

    # Flood-fill: find the actual largest component (not just its size).
    best_component: set[int] = set()
    unseen = set(cells)
    while unseen:
        start = unseen.pop()
        component: set[int] = {start}
        stack = [start]
        while stack:
            c = stack.pop()
            for n in engine.topo.get_neighbors(c):
                if n in unseen:
                    unseen.remove(n)
                    component.add(n)
                    stack.append(n)
        if len(component) > len(best_component):
            best_component = component

    # Count distinct axis coordinates in the largest component.
    axis_size = engine.topo.axis_size
    distinct_coords = {engine.topo.cell_to_coords(c)[axis] for c in best_component}
    return len(distinct_coords) / axis_size


# ---------------------------------------------------------------------------
# breaker_progress
# ---------------------------------------------------------------------------

def breaker_progress(engine) -> float:
    """Breaker's composite progress: max(quota_frac, step_frac).

    Pre-registered formula (PREREGISTRATION.md Stage 1.5/2):
      quota_frac = _quota_ticks / capture_quota  (0.0 if quota == 0)
      step_frac  = step_count / max_game_steps
      breaker_progress = max(quota_frac, step_frac)

    Both quota and clock are win paths for the Breaker; we take the
    more-advanced one as the progress estimate.

    Edge case: quota_frac may exceed 1.0 on a terminal move — the per-move
    tick cap of 2 means _quota_ticks can overshoot capture_quota by 1.
    The result is deliberately NOT clamped: the pre-registered formula has
    no clip, and overshoot only reduces 'behindness' (it makes the Breaker
    look further ahead, never spuriously behind).
    """
    wc = engine.game.win_condition
    quota = getattr(wc, "capture_quota", 0)
    quota_frac = (engine._quota_ticks / quota) if quota > 0 else 0.0
    step_frac = engine.step_count / engine.game.max_game_steps
    return float(max(quota_frac, step_frac))
