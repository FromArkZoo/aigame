"""Observer-based per-game behavior descriptors (RC2 Phase A).

Every function takes ownership data (snapshots or arrays), computes the
observer field on demand, and reuses the validated metric implementations:
  - lead changes: experiments.field_connect_probe.metrics.count_lead_changes
    (imported as-is; prop-agnostic).
  - flip counting: experiments.fc_phase15.metrics.count_controller_changes
    (imported as-is; takes two sign arrays, engine-free). The controller-sign
    two-liner itself (fc_phase15/metrics.py:13-16 ``controller_signs``) reads
    ``engine.board_values`` from a live engine, so it is reimplemented
    locally (``_signs``) on observer-field output rather than fed a shim —
    same trichotomy {-1, 0, +1} at margin 0.
  - drama: experiments.siege.metrics.winner_behindness (imported as-is).
  - span flood-fill: the maker_progress_span algorithm
    (experiments/siege/metrics.py:75-126) adapted to observer-controlled
    cells; coordinate arithmetic uses the universal base-class accessor
    ``topo.cell_to_coords(c)[axis]`` (game_engine/topology.py:324), which is
    valid for ALL anchor topologies (grid, hex_rhombus, and the holes-based
    fractals menger/carpet — they share the base coords encoding).
  - threshold progress: observer ANALOGUE of anchor_drama.py's
    threshold_progress_p1/p2 (experiments/siege/anchor_drama.py:128-162),
    with the engine's komi arithmetic (komi_p2 * threshold added to P2's
    effective score), UNCLAMPED in both directions (anchor_drama precedent:
    threshold_progress_p1/p2 have no clip; the registered formula has none).

Dual observer parameterization for threshold-family PROGRESS TRACES only
(pre-registered amendment, PREREGISTRATION.md Protocol section, committed
before any probe data). Flip rate and lead changes use the observer defaults
for ALL families; the dual rule applies solely to the progress traces that
feed obs_drama:
  - THRESHOLD-family progress traces use the observer field at the GAME'S
    OWN propagation params (radius/strength/decay from its propagation_rule).
    Exact engine match absent captures; with captures the engine retains
    ghost influence from removed stones while the observer recomputes from
    current owners — the observer deliberately measures current-stone
    influence (divergence ≈ one ghost kernel per captured stone; per-rollout
    drama delta up to ~0.035 observed on e1453).
  - ALL OTHER families (connection/field_connection/elimination/majority/...)
    use the observer defaults (r=2, strength=1.0, decay=0.5): params are
    live for the field_connection games but equal the observer defaults
    (2/1.0/0.5) for this anchor set; inert only for prop_type='none' genomes.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from experiments.fc_phase15.metrics import count_controller_changes
from experiments.field_connect_probe.metrics import count_lead_changes
from experiments.siege.metrics import winner_behindness
from metrics.observer_field import observer_field


# ---------------------------------------------------------------------------
# Local helpers
# ---------------------------------------------------------------------------

def _controlled_cells(topo, field: np.ndarray, player: int,
                      margin: float = 0.0) -> set[int]:
    """Cells controlled by *player* on *field* (controlled_sets semantics:
    P1 = field > margin, P2 = field < -margin)."""
    sign = 1.0 if player == 1 else -1.0
    return {c for c in topo.active_cells if sign * field[c] > margin}


def _largest_component_cells(topo, cells: set[int]) -> set[int]:
    """Largest connected component of *cells* under topo adjacency.

    Flood-fill lifted from maker_progress_span (experiments/siege/
    metrics.py:106-121) — returns the component SET, not just its size.
    """
    best: set[int] = set()
    unseen = set(cells)
    while unseen:
        start = unseen.pop()
        component: set[int] = {start}
        stack = [start]
        while stack:
            c = stack.pop()
            for n in topo.get_neighbors(c):
                if n in unseen:
                    unseen.remove(n)
                    component.add(n)
                    stack.append(n)
        if len(component) > len(best):
            best = component
    return best


def _signs(field: np.ndarray) -> np.ndarray:
    """Trichotomous controller array {-1, 0, +1} at margin 0.

    Local reimplementation of fc_phase15.metrics.controller_signs, which
    reads engine.board_values; this operates on an observer-field array.
    """
    return (field > 0.0).astype(np.int8) - (field < 0.0).astype(np.int8)


def _axis_for_player(game, player: int) -> int:
    """Per-player target-axis resolution, verbatim from anchor_drama.py's
    get_axis_for_player (experiments/siege/anchor_drama.py:202-218):
      P1 axis = wc.target_dimension
      P2 axis = wc.target_dimension_p2 if >= 0
                else (target_dimension + 1) % num_dimensions
    """
    wc = game.win_condition
    p1_axis = wc.target_dimension
    p2_raw = wc.target_dimension_p2
    p2_axis = p2_raw if p2_raw >= 0 else (p1_axis + 1) % game.num_dimensions
    return p1_axis if player == 1 else p2_axis


# ---------------------------------------------------------------------------
# Span + snapshot-series descriptors
# ---------------------------------------------------------------------------

def obs_progress_span(topo, owners: np.ndarray, player: int,
                      axis: int) -> float:
    """Span fraction along *axis* of the largest connected observer-controlled
    component (mirror of siege.metrics.maker_progress_span, observer-based).

    Control at margin 0 on the observer field (defaults r=2/s=1.0/d=0.5);
    distinct axis coords of the largest component / axis_size.
    """
    field = observer_field(topo, owners)
    cells = _controlled_cells(topo, field, player)
    if not cells:
        return 0.0
    component = _largest_component_cells(topo, cells)
    distinct_coords = {topo.cell_to_coords(c)[axis] for c in component}
    return len(distinct_coords) / topo.axis_size


def obs_lead_changes_from_snapshots(topo, snapshots: Sequence[np.ndarray],
                                    axis_p1: int, axis_p2: int) -> int:
    """Lead changes over the per-snapshot span differential.

    Per snapshot: d = obs_progress_span(P1, axis_p1) -
    obs_progress_span(P2, axis_p2); count_lead_changes (sign flips, zeros
    skipped) over the series.
    """
    series = [
        obs_progress_span(topo, owners, 1, axis_p1)
        - obs_progress_span(topo, owners, 2, axis_p2)
        for owners in snapshots
    ]
    return count_lead_changes(series)


def obs_control_flip_rate_from_snapshots(topo,
                                         snapshots: Sequence[np.ndarray],
                                         ) -> float:
    """Mean controller-sign flips between CONSECUTIVE snapshots (per-ply rate).

    Controller signs at margin 0 on the OBSERVER field per snapshot; flip
    count between each consecutive pair via fc_phase15's
    count_controller_changes; mean over the len(snapshots)-1 transitions.
    No empty-board prefix: the series starts at the first snapshot (a
    2-snapshot series has exactly one transition). < 2 snapshots -> 0.0.
    """
    if len(snapshots) < 2:
        return 0.0
    sign_arrays = [_signs(observer_field(topo, owners))
                   for owners in snapshots]
    changes = [count_controller_changes(prev, cur)
               for prev, cur in zip(sign_arrays, sign_arrays[1:])]
    return float(np.mean(changes))


# ---------------------------------------------------------------------------
# Threshold-family observer progress + drama
# ---------------------------------------------------------------------------

def obs_threshold_progress(game, topo, owners: np.ndarray,
                           player: int) -> float:
    """Observer analogue of the engine's threshold-race progress.

    Per the pre-registered dual parameterization, the observer field is
    computed at the GAME'S OWN propagation params. Exact engine match absent
    captures; with captures the engine retains ghost influence from removed
    stones while the observer recomputes from current owners — the observer
    deliberately measures current-stone influence (divergence ≈ one ghost
    kernel per captured stone; per-rollout drama delta up to ~0.035 observed
    on e1453).
      p1_score = sum(field[c] for P1-owned c)         (positive contributions)
      p2_score = sum(-field[c] for P2-owned c) + komi_p2 * threshold
    progress = score / wc.threshold — UNCLAMPED in both directions
    (anchor_drama precedent: threshold_progress_p1/p2 have no clip; the
    registered formula has none).
    threshold == 0 -> 0.0 (anchor_drama edge-case behavior).
    """
    wc = game.win_condition
    threshold = wc.threshold
    if threshold == 0:
        return 0.0
    pr = game.propagation_rule
    field = observer_field(topo, owners, radius=pr.radius,
                           strength=pr.strength, decay=pr.decay)
    if player == 1:
        score = sum(
            float(field[c]) for c in topo.active_cells if owners[c] == 1
        )
    else:
        total = sum(
            float(field[c]) for c in topo.active_cells if owners[c] == 2
        )
        komi = getattr(game, "komi_p2", 0.0) * threshold
        score = -total + komi
    return score / threshold


def obs_drama_for_rollout(game, topo, rollout: dict) -> float | None:
    """Winner-behindness drama over per-ply observer progress traces.

    Family dispatch on game.win_condition.condition_type (anchor_drama's
    record_progress pattern):
      threshold -> obs_threshold_progress (game's own propagation params);
      everything else (connection/field_connection/elimination/majority/...)
        -> obs_progress_span per player at observer defaults, axes resolved
           via _axis_for_player.
    Winner from rollout["winner"]; draws (winner None) -> None.
    """
    winner = rollout["winner"]
    if winner is None:
        return None
    snapshots = rollout["owner_snapshots"]
    if game.win_condition.condition_type == "threshold":
        p1_trace = [obs_threshold_progress(game, topo, o, 1)
                    for o in snapshots]
        p2_trace = [obs_threshold_progress(game, topo, o, 2)
                    for o in snapshots]
    else:
        axis_p1 = _axis_for_player(game, 1)
        axis_p2 = _axis_for_player(game, 2)
        p1_trace = [obs_progress_span(topo, o, 1, axis_p1)
                    for o in snapshots]
        p2_trace = [obs_progress_span(topo, o, 2, axis_p2)
                    for o in snapshots]
    if winner == 1:
        return winner_behindness(p1_trace, p2_trace)
    return winner_behindness(p2_trace, p1_trace)


# ---------------------------------------------------------------------------
# Interaction rate
# ---------------------------------------------------------------------------

def _enemy_within_two(topo, board: np.ndarray, cell: int,
                      enemy: int) -> bool:
    """Any *enemy*-owned stone on *board* within graph distance <= 2 of
    *cell* (topology-aware distance via topo.cells_within_radius)."""
    return any(
        int(board[c]) == enemy for c in topo.cells_within_radius(cell, 2)
    )


def interaction_rate_for_rollout(topo, rollout: dict) -> float:
    """Mean of capture rate and contact fraction (pre-registered formula).

      capture_rate     = captures_total / max(1, plies)
      contact_fraction = fraction of plies whose newly placed cell (the
        single cell that changed 0 -> nonzero between consecutive snapshots;
        the first snapshot compares against the empty board) is within graph
        distance <= 2 of an enemy stone, enemy relative to the placer (the
        new stone's owner).

    Documented resolutions:
      - Enemy presence is checked on the PREVIOUS snapshot (pre-move state):
        contact means the placement engaged enemies that were on the board
        when it was played, so a placement that captures its contacted enemy
        still counts; the first ply (empty previous board) never counts.
      - Plies with no single identifiable placement (zero or multiple
        0 -> nonzero cells, e.g. capture-only changes) count as contact if
        ANY changed cell has an enemy within 2 — per changed cell, the
        reference owner is its new owner (or its previous owner if the cell
        was emptied) and the enemy is the other player. A flipped cell is
        its own pre-move enemy at distance 0, so flip-captures always
        register contact (they ARE interaction).
    """
    snapshots = rollout["owner_snapshots"]
    plies = rollout["plies"]
    assert plies == len(snapshots), (
        f"rollout['plies'] ({plies}) != len(owner_snapshots) "
        f"({len(snapshots)}) — inconsistent rollout dict"
    )
    capture_rate = rollout["captures_total"] / max(1, plies)
    contact = 0
    prev = np.zeros(topo.total_cells,
                    dtype=snapshots[0].dtype if snapshots else np.int8)
    for cur in snapshots:
        new_cells = [c for c in topo.active_cells
                     if prev[c] == 0 and cur[c] != 0]
        if len(new_cells) == 1:
            placed = new_cells[0]
            enemy = 3 - int(cur[placed])
            if _enemy_within_two(topo, prev, placed, enemy):
                contact += 1
        else:
            changed = [c for c in topo.active_cells if prev[c] != cur[c]]
            for c in changed:
                ref = int(cur[c]) if cur[c] != 0 else int(prev[c])
                if ref != 0 and _enemy_within_two(topo, prev, c, 3 - ref):
                    contact += 1
                    break
        prev = cur
    contact_fraction = contact / max(1, plies)
    return float((capture_rate + contact_fraction) / 2.0)


# ---------------------------------------------------------------------------
# Per-game aggregation
# ---------------------------------------------------------------------------

def descriptor_row(game, rollouts: list[dict]) -> dict:
    """Aggregate a game's descriptor values over a rollout list.

    Per-rollout obs_* values are computed from that rollout's snapshots;
    means over rollouts. obs_drama skips draws (None) and reports the count
    actually used (obs_drama_n); all-draw games get obs_drama = nan
    (anchor_drama precedent). draws = count of winner-None rollouts.
    """
    topo = game.get_topology()
    axis_p1 = _axis_for_player(game, 1)
    axis_p2 = _axis_for_player(game, 2)

    dramas: list[float] = []
    lead_changes: list[int] = []
    flip_rates: list[float] = []
    interaction_rates: list[float] = []
    lengths: list[int] = []
    draws = 0

    for rollout in rollouts:
        drama = obs_drama_for_rollout(game, topo, rollout)
        if drama is None:
            draws += 1
        else:
            dramas.append(drama)
        snapshots = rollout["owner_snapshots"]
        lead_changes.append(
            obs_lead_changes_from_snapshots(topo, snapshots, axis_p1, axis_p2)
        )
        flip_rates.append(obs_control_flip_rate_from_snapshots(topo, snapshots))
        interaction_rates.append(interaction_rate_for_rollout(topo, rollout))
        lengths.append(rollout["game_length"])

    return {
        "obs_drama": float(np.mean(dramas)) if dramas else float("nan"),
        "obs_drama_n": len(dramas),
        "obs_lead_changes": float(np.mean(lead_changes)) if lead_changes else 0.0,
        "obs_control_flip_rate": float(np.mean(flip_rates)) if flip_rates else 0.0,
        "interaction_rate": (
            float(np.mean(interaction_rates)) if interaction_rates else 0.0
        ),
        "game_length": float(np.mean(lengths)) if lengths else 0.0,
        "draws": draws,
    }
