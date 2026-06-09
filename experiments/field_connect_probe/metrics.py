"""Pre-registered mechanical-screen metrics for the Field-Connect probe.

Lead-change proxy (spec §8a, concretized here BEFORE any results exist):
  A1 (field_connection): d_t = largest P1-controlled component size
                               - largest P2-controlled component size
  A0 (threshold):        d_t = P1 score - (P2 score + komi_p2 * threshold)
lead_changes = sign flips of d_t over the game, zeros skipped.
"""
from __future__ import annotations

from typing import Iterable


def count_lead_changes(series: Iterable[float]) -> int:
    """Sign flips in *series*, ignoring zeros."""
    flips = 0
    prev = 0
    for v in series:
        s = (v > 0) - (v < 0)
        if s != 0:
            if prev != 0 and s != prev:
                flips += 1
            prev = s
    return flips


def largest_component(topo, cells: set[int]) -> int:
    """Size of the largest connected component of *cells* under *topo*
    adjacency."""
    best = 0
    unseen = set(cells)
    while unseen:
        start = unseen.pop()
        size = 1
        stack = [start]
        while stack:
            c = stack.pop()
            for n in topo.get_neighbors(c):
                if n in unseen:
                    unseen.remove(n)
                    size += 1
                    stack.append(n)
        best = max(best, size)
    return best


def controlled_sets(engine, margin: float) -> tuple[set[int], set[int]]:
    """(P1-controlled, P2-controlled) cell sets by field sign + margin."""
    p1 = {c for c in engine.topo.active_cells if engine.board_values[c] > margin}
    p2 = {c for c in engine.topo.active_cells if engine.board_values[c] < -margin}
    return p1, p2


def progress_diff_field(engine, margin: float) -> float:
    """A1 lead proxy: largest-controlled-component size differential."""
    p1, p2 = controlled_sets(engine, margin)
    return float(
        largest_component(engine.topo, p1) - largest_component(engine.topo, p2)
    )


def progress_diff_threshold(engine) -> float:
    """A0 lead proxy: effective threshold-race score differential,
    replicating the engine's scoring (engine_v2.py:_check_threshold) incl. komi.

    Verification notes (2026-06-09):
    Engine computes per player in _check_threshold (lines ~1076-1083):
      P1: total_value = sum(board_values[c] for active_cells if owner==1)
          effective = total_value   (P1 values are positive)
      P2: total_value = sum(board_values[c] for active_cells if owner==2)
          effective = -total_value + komi   (P2 values are negative; negated)
      komi = komi_p2 * threshold
    This function returns effective_p1 - effective_p2 as a continuous proxy
    (no > threshold gate — that is intentional; we want a smooth signal).
    The replication is faithful.
    """
    p1 = sum(
        float(engine.board_values[c])
        for c in engine.topo.active_cells
        if engine.board_owners[c] == 1
    )
    p2 = sum(
        -float(engine.board_values[c])
        for c in engine.topo.active_cells
        if engine.board_owners[c] == 2
    )
    komi = getattr(engine.game, "komi_p2", 0.0) * engine.game.win_condition.threshold
    return p1 - (p2 + komi)
