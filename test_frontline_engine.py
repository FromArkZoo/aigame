"""FRONTLINE engine tests (contested_majority — spec §3/§5, prereg-locked).

Run: .venv/bin/python -m pytest test_frontline_engine.py -q
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import numpy as np
import pytest

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule, CaptureRule, PlacementRule, PropagationRule,
    TurnStructure, WinCondition, WIN_CONDITION_TYPES,
)

W = 22


def make_cm_game(
    engage_threshold: float = 1.0,
    end_margin: int = 8,
    min_turns: int = 20,
    komi_cells: int = 0,
    max_turns: int = 200,
    pie: bool = False,
) -> GameDefV2:
    """Frontline test fixture — prereg arm config, pie OFF by default so
    tests drive deterministic sequences (pie covered by its own test)."""
    return GameDefV2(
        game_id="f_test",
        num_dimensions=2,
        axis_size=W,
        topology_type="hex_rhombus",
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=2, strength=1.0, decay=0.5),
        win_condition=WinCondition(
            condition_type="contested_majority",
            engage_threshold=engage_threshold,
            end_margin=end_margin,
            min_turns_score_end=min_turns,
            komi_cells=komi_cells,
            max_turns=max_turns,
            control_margin=0.0,
        ),
        pie_rule=pie,
    )


def test_wincondition_serde_roundtrip():
    wc = WinCondition(
        condition_type="contested_majority", engage_threshold=1.0,
        end_margin=8, min_turns_score_end=20, komi_cells=1, max_turns=200,
    )
    d = wc.to_dict()
    wc2 = WinCondition.from_dict(d)
    assert wc2.engage_threshold == 1.0
    assert wc2.end_margin == 8
    assert wc2.min_turns_score_end == 20
    assert wc2.komi_cells == 1


def test_legacy_serde_omits_frontline_keys():
    legacy = WinCondition(condition_type="connection")
    d = legacy.to_dict()
    for key in ("engage_threshold", "end_margin",
                "min_turns_score_end", "komi_cells"):
        assert key not in d, f"legacy to_dict leaked {key}"
    # back-compat: from_dict on a dict without the new keys
    wc = WinCondition.from_dict({"condition_type": "connection"})
    assert wc.engage_threshold == 0.0 and wc.komi_cells == 0


def test_contested_majority_not_generated():
    assert "contested_majority" not in WIN_CONDITION_TYPES


GOLDEN_A1_HASH = "d7d847e07ba98a34ca4ea3d3948a6cc1ff9ee1436d2d2808a88114cb98d637f5"


def test_legacy_canonical_hash_unchanged():
    src = Path(__file__).parent / "experiments/fc_phase15/games/calibrated/a1_field_connect.json"
    g = GameDefV2.from_dict(json.loads(src.read_text()))
    g2 = GameDefV2.from_dict(json.loads(json.dumps(g.to_dict())))
    assert g2.canonical_hash() == g.canonical_hash()
    assert g.canonical_hash() == GOLDEN_A1_HASH


def _interior_cell(topo):
    """First cell with full 6/12 rings (mirrors siege stage0_memo)."""
    for cell in topo.active_cells:
        d1 = [c for c in topo.cells_within_radius(cell, 1) if c != cell]
        d2 = [c for c in topo.cells_within_radius(cell, 2)
              if topo.distance(cell, c) == 2]
        if len(d1) == 6 and len(d2) == 12:
            return cell, d1, d2
    raise RuntimeError("no interior cell")


def _set_board(engine, stones: dict[int, int]):
    engine.board_owners[:] = 0
    for c, owner in stones.items():
        engine.board_owners[c] = owner
    engine._recompute_field()


def test_contested_scores_straggler():
    engine = create_engine(make_cm_game())
    x, d1, d2 = _interior_cell(engine.topo)
    _set_board(engine, {x: 2, d1[0]: 1, d1[1]: 1, d2[0]: 1})
    s1, s2, engaged = engine.contested_scores()
    assert (s1, s2, engaged) == (1, 0, 1)   # spec §4.2 exact


def test_contested_scores_packing_zero():
    engine = create_engine(make_cm_game())
    x, _, _ = _interior_cell(engine.topo)
    far = x + 8  # same row, distance 8 > 2*r: kernels cannot overlap
    _set_board(engine, {x: 1, far: 2})
    assert engine.contested_scores() == (0, 0, 0)


def test_contested_scores_tie_cell_scores_no_one():
    engine = create_engine(make_cm_game())
    x, d1, _ = _interior_cell(engine.topo)
    # Empty cell x with one P1 and one P2 stone adjacent on opposite
    # sides: I1(x)=I2(x)=0.5 < E → not engaged at E=1.0. At E=0.5:
    # engaged, exact tie → neither scores. Engaged set = the 2 common
    # neighbors of the two stones, both exactly tied (0.5 vs 0.5).
    engine_lo = create_engine(make_cm_game(engage_threshold=0.5))
    _set_board(engine_lo, {d1[0]: 1, d1[3]: 2})
    s1, s2, engaged = engine_lo.contested_scores()
    assert (s1, s2, engaged) == (0, 0, 2)


PASS = W * W  # pass action index (engine convention: total_cells = pass)


def test_passbot_loses_stones_tiebreak_at_komi0():
    # P1 places far-apart stones (no engagement → 0-0), P2 always passes.
    # Timeout: exact 0-0 tie → stones tiebreak → P1 wins (spec §4.4).
    g = make_cm_game(end_margin=999, min_turns=0, max_turns=8)
    engine = create_engine(g)
    engine.reset()
    p1_cells = [0, 8, 16, 176]  # pairwise distance > 4: never engaged
    i = 0
    while not engine.done:
        if engine.current_player == 1:
            engine.step(p1_cells[i]); i += 1
        else:
            engine.step(PASS)
    assert engine._ended_by_max_turns
    assert engine._winner == 1


def test_participation_clause_komi_passbot_draw():
    # komi_cells=1: zero-stone P2 would win 1 > 0 on score — the
    # participation clause downgrades to draw (spec §3.7).
    g = make_cm_game(end_margin=999, min_turns=0, komi_cells=1, max_turns=8)
    engine = create_engine(g)
    engine.reset()
    p1_cells = [0, 8, 16, 176]
    i = 0
    while not engine.done:
        if engine.current_player == 1:
            engine.step(p1_cells[i]); i += 1
        else:
            engine.step(PASS)
    assert engine._winner is None


def test_double_pass_before_min_turns_is_draw():
    g = make_cm_game(min_turns=20, max_turns=200)
    engine = create_engine(g)
    engine.reset()
    engine.step(0)      # P1 places (avoid empty-board double-pass edge)
    engine.step(PASS)   # P2
    engine.step(PASS)   # P1 → double-pass at step_count 2 < 20 → draw
    assert engine.done and engine._winner is None
    assert engine._ended_by_double_pass


def test_double_pass_after_min_turns_resolves_by_score():
    # komi_cells=1 makes the resolution DECISIVE (s1=0 vs s2_eff=1 → P2),
    # so this kills the restore-legacy-draw mutant: deleting the contested
    # branch from _end_by_double_pass would draw instead.
    g = make_cm_game(end_margin=999, min_turns=4, komi_cells=1, max_turns=200)
    engine = create_engine(g)
    engine.reset()
    engine.step(0)      # P1
    engine.step(176)    # P2 (far away, no engagement)
    engine.step(8)      # P1 (all pairwise distance > 4: scores stay 0-0)
    engine.step(184)    # P2
    engine.step(PASS)   # P1, step_count 4 >= min_turns
    engine.step(PASS)   # P2 → resolve by score: s1=0 < s2_eff=0+1 → P2 wins
    assert engine.done and engine._winner == 2
    assert engine._ended_by_double_pass


def test_placement_increments_count():
    g = make_cm_game()
    engine = create_engine(g)
    engine.reset()
    engine.step(0)
    assert engine._placements_made == [1, 0]


def test_score_beats_stones_at_timeout():
    # R13/14 headline property: at timeout the score-leader wins even when
    # the opponent holds piece majority — pieces only break EXACT score
    # ties, so the legacy piece-majority exploit cannot recur. Kills the
    # mutant that deletes the contested branch from _end_by_max_turns
    # (legacy piece-majority would crown P2 here). Direct-state
    # construction, mirroring how Task 4's streak tests drive
    # _check_contested_majority directly.
    engine = create_engine(make_cm_game())
    x, d1, d2 = _interior_cell(engine.topo)
    stones = {x: 2, d1[0]: 1, d1[1]: 1, d2[0]: 1}  # straggler: s1=1, s2=0
    far = [c for c in engine.topo.active_cells
           if engine.topo.distance(x, c) > 8][:4]
    stones.update({c: 2 for c in far})  # piece majority to P2 (3 vs 5)
    _set_board(engine, stones)
    engine.piece_counts = [3, 5]
    engine._placements_made = [3, 5]
    assert engine.contested_scores()[:2] == (1, 0)
    engine._end_by_max_turns()
    assert engine._winner == 1


def test_contested_majority_rejects_simultaneous():
    g = dataclasses.replace(
        make_cm_game(),
        turn_structure=TurnStructure(turn_type="simultaneous"),
        # capture "none" so the simultaneous+field-capture guard doesn't
        # fire first — this must exercise the CM alternating guard.
        capture_rule=CaptureRule(capture_type="none"),
    )
    with pytest.raises(ValueError, match="contested_majority"):
        create_engine(g)
