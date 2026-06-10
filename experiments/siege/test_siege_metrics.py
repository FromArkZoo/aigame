"""Tests for experiments/siege/metrics.py (pre-registered SIEGE drama signal).

Run via:
    .venv/bin/python -m pytest experiments/siege/test_siege_metrics.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np
import pytest

from experiments.siege.metrics import (
    breaker_progress,
    maker_progress_span,
    winner_behindness,
)


# ---------------------------------------------------------------------------
# winner_behindness
# ---------------------------------------------------------------------------

def test_winner_behindness_basic():
    # winner always ahead -> deficit max(0, loser-winner) is always 0 -> drama 0.0
    assert winner_behindness([0.5, 0.8], [0.1, 0.2]) == 0.0

    # winner at [0.25, 0.6], loser at [0.5, 0.6]:
    #   ply 0: max(0, 0.5 - 0.25) = 0.25 -> sqrt(0.25) = 0.5
    #   ply 1: max(0, 0.6 - 0.6)  = 0.0  -> sqrt(0.0)  = 0.0
    #   mean = 0.25
    assert abs(winner_behindness([0.25, 0.6], [0.5, 0.6]) - 0.25) < 1e-12


def test_winner_behindness_empty():
    assert winner_behindness([], []) == 0.0


def test_winner_behindness_winner_always_behind():
    # winner at 0.0, loser at 1.0 every ply -> sqrt(1.0) = 1.0 per ply -> mean 1.0
    assert abs(winner_behindness([0.0, 0.0], [1.0, 1.0]) - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# maker_progress_span (engine fixture)
# ---------------------------------------------------------------------------

def _make_siege_engine(quota: int = 3, max_turns: int = 200, axis: int = 5):
    """Build a SIEGE engine using the same pattern as test_siege_engine.py."""
    from game_engine.factory import create_engine
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        CaptureRule, PlacementRule, PropagationRule, TurnStructure, WinCondition,
    )

    game = GameDefV2(
        game_id="siege_metrics_test",
        num_dimensions=2,
        axis_size=axis,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(prop_type="influence",
                                         radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(
            condition_type="field_connection",
            condition_type_p2="capture_quota",
            capture_quota=quota,
            timeout_winner=2,
            target_dimension=0,
            control_margin=0.0,
            max_turns=max_turns,
        ),
        turn_structure=TurnStructure(),
    )
    engine = create_engine(game)
    engine.reset()
    return engine


def test_maker_progress_span_engine_fixture():
    """5×5 hex_rhombus SIEGE engine: verify maker_progress_span is correct.

    Executed cases:
      1. Empty board: no P1 controlled cells -> progress 0.0.
      2. Single P1 stone at center (2,2): radius-2 influence spans q=0..4
         (all 5 axis-0 values) -> progress exactly 1.0.
      3. Single P1 stone at corner (0,0): radius-2 influence spans q=0..2
         -> largest component holds >= 3 distinct q-coords -> progress
         in [3/5, 1.0].

    Geometry note (illustration only, NOT exercised below): radius-2
    influence from a stone at (q0, r0) covers q = q0-2 .. q0+2 clamped to
    the board, so e.g. stones at (0,2)+(2,2)+(4,2) would jointly cover all
    of q=0..4. The executed cases above are the single-stone reductions of
    that picture.

    The controlled set at margin=0 includes any cell with board_values > 0
    (control flows through influence, not stone ownership).
    """
    engine = _make_siege_engine(axis=5)

    # Empty board: P1 has no controlled cells -> 0.0
    p = maker_progress_span(engine, player=1, axis=0, margin=0.0)
    assert p == 0.0, f"empty board: expected 0.0, got {p}"

    # Place one P1 stone at (2, 2) (center) — radius-2 covers entire 5×5 board
    topo = engine.topo
    center = topo.coords_to_cell((2, 2))
    engine.step(center)  # P1 places stone

    p_center = maker_progress_span(engine, player=1, axis=0, margin=0.0)
    assert p_center == 1.0, f"center stone: expected 1.0, got {p_center}"

    # Reset and place P1 stone at corner (0,0) only: radius-2 spans q=0..2 -> 3/5
    engine2 = _make_siege_engine(axis=5)
    corner = engine2.topo.coords_to_cell((0, 0))
    engine2.step(corner)  # P1 plays
    p_corner = maker_progress_span(engine2, player=1, axis=0, margin=0.0)
    assert p_corner >= 3 / 5 - 1e-9, f"corner: expected >= 0.6, got {p_corner}"
    assert p_corner <= 1.0, f"corner: expected <= 1.0, got {p_corner}"

    # All P1 controlled cells must span ALL q=0..4 for a full-board stone
    engine3 = _make_siege_engine(axis=5)
    engine3.step(engine3.topo.coords_to_cell((2, 2)))
    p_full = maker_progress_span(engine3, player=1, axis=0, margin=0.0)
    assert p_full == 1.0, f"full span: expected 1.0, got {p_full}"


# ---------------------------------------------------------------------------
# breaker_progress
# ---------------------------------------------------------------------------

def test_breaker_progress():
    """Verify the max(quota_frac, step_frac) formula."""
    engine = _make_siege_engine(quota=4, max_turns=100, axis=5)

    # Tick quota manually and advance steps
    engine._quota_ticks = 1
    engine.step_count = 10
    bp = breaker_progress(engine)
    # quota_frac = 1/4 = 0.25, step_frac = 10/100 = 0.10 -> max = 0.25
    assert abs(bp - 0.25) < 1e-9, f"expected 0.25, got {bp}"

    # step_frac dominates: quota_ticks=0, step=60/100=0.60
    engine._quota_ticks = 0
    engine.step_count = 60
    bp2 = breaker_progress(engine)
    assert abs(bp2 - 0.60) < 1e-9, f"expected 0.60, got {bp2}"

    # Both equal: quota_frac = 2/4=0.5, step_frac=50/100=0.5 -> 0.5
    engine._quota_ticks = 2
    engine.step_count = 50
    bp3 = breaker_progress(engine)
    assert abs(bp3 - 0.5) < 1e-9, f"expected 0.5, got {bp3}"


def test_breaker_progress_zero_quota_fallback():
    """If capture_quota == 0 (degenerate), quota_frac = 0.0; step_frac governs."""
    # Build a non-SIEGE engine (no capture_quota set)
    from game_engine.factory import create_engine
    from game_engine.game_def_v2 import GameDefV2
    from game_engine.rules import (
        CaptureRule, PlacementRule, PropagationRule, TurnStructure, WinCondition,
    )

    game = GameDefV2(
        game_id="degenerate_quota_test",
        num_dimensions=2, axis_size=5,
        topology_type="hex_rhombus",
        placement_rule=PlacementRule(),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(prop_type="influence",
                                         radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(condition_type="field_connection",
                                   capture_quota=0,
                                   max_turns=100),
        turn_structure=TurnStructure(),
    )
    engine = create_engine(game)
    engine.reset()
    engine.step_count = 30
    bp = breaker_progress(engine)
    # quota_frac = 0 (degenerate guard), step_frac = 30/100 = 0.30
    assert abs(bp - 0.30) < 1e-9, f"expected 0.30, got {bp}"
