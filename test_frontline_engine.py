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


def _lead_board(engine):
    """Board with S1-S2 = +1 (the straggler config, spec §4.2 exact)."""
    x, d1, d2 = _interior_cell(engine.topo)
    _set_board(engine, {x: 2, d1[0]: 1, d1[1]: 1, d2[0]: 1})


def test_early_end_streak_fires_at_3_ending_odd():
    g = make_cm_game(end_margin=1, min_turns=20)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (21, 22):
        engine.step_count = sc
        engine._check_contested_majority(wc)
        assert not engine.done
    engine.step_count = 23   # 3rd consecutive check, odd → round-end
    engine._check_contested_majority(wc)
    assert engine.done and engine._winner == 1
    assert engine._ended_by_score_margin


def test_early_end_streak_does_not_fire_at_even_parity():
    g = make_cm_game(end_margin=1, min_turns=20)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (20, 21, 22):   # 3rd check lands EVEN → must not fire yet
        engine.step_count = sc
        engine._check_contested_majority(wc)
    assert not engine.done
    engine.step_count = 23    # 4th check, odd → fires now
    engine._check_contested_majority(wc)
    assert engine.done and engine._winner == 1


def test_early_end_min_turns_blocks_streak():
    g = make_cm_game(end_margin=1, min_turns=20)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (15, 16, 17, 18, 19):
        engine.step_count = sc
        engine._check_contested_majority(wc)
    assert not engine.done and engine._cm_streak == 0


def test_early_end_leader_flip_resets_streak():
    g = make_cm_game(end_margin=1, min_turns=0)
    engine = create_engine(g)
    engine.reset()
    wc = g.win_condition
    _lead_board(engine)                  # P1 leads
    engine.step_count = 20
    engine._check_contested_majority(wc)
    assert engine._cm_streak == 1
    # Mirror ownership: now P2 leads — streak must restart at -1.
    x, d1, d2 = _interior_cell(engine.topo)
    _set_board(engine, {x: 1, d1[0]: 2, d1[1]: 2, d2[0]: 2})
    engine.step_count = 21
    engine._check_contested_majority(wc)
    assert engine._cm_streak == -1 and not engine.done


def test_early_end_komi_shifts_qualification():
    # komi_cells=1 turns P1's +1 raw lead into 0 → P1 never qualifies.
    g = make_cm_game(end_margin=1, min_turns=0, komi_cells=1)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)
    wc = g.win_condition
    for sc in (20, 21, 22, 23):
        engine.step_count = sc
        engine._check_contested_majority(wc)
    assert not engine.done and engine._cm_streak == 0


def test_double_pass_exact_tie_equal_stones_is_draw():
    # Exact komi-adjusted tie + equal stones → the final draw fallthrough
    # in _resolve_contested_by_score (both players placed, so the
    # participation clause does not apply).
    g = make_cm_game(end_margin=999, min_turns=4, max_turns=200)
    engine = create_engine(g)
    engine.reset()
    engine.step(0)      # P1
    engine.step(176)    # P2 (far away, no engagement)
    engine.step(8)      # P1
    engine.step(184)    # P2
    engine.step(PASS)   # P1
    engine.step(PASS)   # P2 → 0-0 tie, stones 2-2 → draw
    assert engine.done and engine._winner is None
    assert engine._ended_by_double_pass


def test_state_dim_legacy_unchanged():
    src = (Path(__file__).parent
           / "experiments/fc_phase15/games/calibrated/a1_field_connect.json")
    g = GameDefV2.from_dict(json.loads(src.read_text()))
    assert g.state_dim == g.total_cells * 2 + 3


def test_state_dim_contested_adds_three():
    g = make_cm_game()
    assert g.state_dim == g.total_cells * 2 + 3 + 3


def test_obs_floats_present_and_perspective_signed():
    g = make_cm_game(end_margin=8, min_turns=0)
    engine = create_engine(g)
    obs = engine.reset()
    assert obs.shape == (g.state_dim,)
    # Empty board: margin 0, engaged 0, armed 0.
    assert np.allclose(obs[-3:], [0.0, 0.0, 0.0])
    # Build the +1 P1 lead and a +2 streak, then check both perspectives.
    _lead_board(engine)
    engine._cm_streak = 2
    engine.current_player = 1
    obs1 = engine._observe()
    engine.current_player = 2
    obs2 = engine._observe()
    assert obs1[-3] == pytest.approx(1 / 8)      # score_margin_frac, own view
    assert obs2[-3] == pytest.approx(-1 / 8)
    assert obs1[-2] > 0                          # engaged_frac
    assert obs1[-1] == pytest.approx(2 / 3)      # armed_frac, leader view
    assert obs2[-1] == pytest.approx(-2 / 3)


def test_obs_clips_pin_margin_and_streak():
    # Mutation guards: removing EITHER np.clip in _observe's contested
    # block must fail here (margin and streak are pinned at their clip
    # boundaries, not just signed).
    g = make_cm_game(end_margin=1, min_turns=0)
    engine = create_engine(g)
    engine.reset()
    # Three pairwise-far straggler configs (each +1 to S1, no interaction:
    # centers > 8 apart so stones from different clusters are >= 5 apart
    # and no cell sits within radius 2 of both). Lead 3 > 2*end_margin.
    centers: list[int] = []
    stones: dict[int, int] = {}
    for cell in engine.topo.active_cells:
        if any(engine.topo.distance(cell, c) <= 8 for c in centers):
            continue
        d1 = [c for c in engine.topo.cells_within_radius(cell, 1)
              if c != cell]
        d2 = [c for c in engine.topo.cells_within_radius(cell, 2)
              if engine.topo.distance(cell, c) == 2]
        if len(d1) == 6 and len(d2) == 12:
            centers.append(cell)
            stones.update({cell: 2, d1[0]: 1, d1[1]: 1, d2[0]: 1})
            if len(centers) == 3:
                break
    assert len(centers) == 3
    _set_board(engine, stones)
    assert engine.contested_scores()[:2] == (3, 0)
    engine._cm_streak = 4
    engine.current_player = 1
    obs1 = engine._observe()
    engine.current_player = 2
    obs2 = engine._observe()
    # Margin clip: raw lead/m = 3 -> clipped to exactly +/-2.
    assert obs1[-3] == 2.0 and obs2[-3] == -2.0
    # Streak clip: raw 4/3 -> clipped to exactly +/-1.
    assert obs1[-1] == 1.0 and obs2[-1] == -1.0


def test_per_player_fields_bit_identical_after_perf_path():
    # flatnonzero iteration must reproduce the all-cells loop exactly:
    # signed reconstruction I1 - I2 equals _recompute_field's board_values.
    engine = create_engine(make_cm_game())
    rng = np.random.default_rng(3)
    cells = rng.choice(engine.total_cells, size=60, replace=False)
    stones = {int(c): int(1 + (i % 2)) for i, c in enumerate(cells)}
    _set_board(engine, stones)
    i1, i2 = engine._per_player_fields()
    assert np.array_equal(i1 - i2, engine.board_values)


def test_contested_majority_requires_positive_end_margin():
    import dataclasses
    g = make_cm_game()
    g = dataclasses.replace(
        g, win_condition=dataclasses.replace(g.win_condition, end_margin=0))
    with pytest.raises(ValueError, match="end_margin"):
        create_engine(g)


def test_double_pass_min_turns_boundary():
    # The resolving (2nd) pass fires _end_by_double_pass BEFORE step_count
    # increments, so the gate sees the pre-increment count. min_turns=5:
    # passes at plies 4,5 → gate sees step_count 5 >= 5 → resolves by
    # score (decisive via komi). Passes at plies 3,4 → gate sees 4 < 5 →
    # legacy draw.
    for first_pass_ply, expect_winner in ((4, 2), (3, None)):
        g = make_cm_game(end_margin=999, min_turns=5, komi_cells=1,
                         max_turns=200)
        engine = create_engine(g)
        engine.reset()
        cells = [0, 176, 8, 184]
        for c in cells[:first_pass_ply]:
            engine.step(c)
        engine.step(PASS)
        engine.step(PASS)
        assert engine.done
        assert engine._winner == expect_winner, (
            f"first_pass_ply={first_pass_ply}")


def test_full_random_game_terminates_with_known_end_cause():
    from training.utils import RandomAgent
    g = make_cm_game(pie=True)   # the real arm config has pie ON
    engine = create_engine(g)
    rng = np.random.default_rng(11)
    obs = engine.reset()
    agents = [RandomAgent(seed=int(rng.integers(2**31))) for _ in range(2)]
    while not engine.done:
        legal = engine.get_legal_actions()
        a, _, _ = agents[engine.get_current_player()].select_action(
            obs, legal_actions=legal, deterministic=False)
        obs, _, done, info = engine.step(a)
    causes = [engine._ended_by_score_margin,
              engine._ended_by_double_pass,
              engine._ended_by_max_turns]
    assert any(causes), "game must end via a known FRONTLINE cause"
    assert engine.step_count <= g.win_condition.max_turns


def test_early_end_fires_through_real_step_flow():
    # Kills the dispatch-deletion mutant: if the contested_majority elif
    # in _check_win_conditions is removed, the done flag is never set and
    # the loop runs to the step_count guard (engine.done never becomes True).
    g = make_cm_game(end_margin=1, min_turns=0)
    engine = create_engine(g)
    engine.reset()
    _lead_board(engine)          # P1 lead +1; P1 to move
    far = [400, 408, 416, 424, 448, 440]   # far from the lead cluster: no flips,
    i = 0                        # no engagement change, lead persists
    while not engine.done and engine.step_count < 12:
        if engine.current_player == 1:
            engine.step(PASS)    # P1 passes (never consecutively: P2 places between)
        else:
            engine.step(far[i]); i += 1
    assert engine.done          # FIRST: done must fire before checking cause/winner
    assert engine._winner == 1
    assert engine._ended_by_score_margin
    # Fire happens at the pre-increment ODD check; step() then increments.
    assert engine.step_count % 2 == 0


def test_scripted_agents_basic_behavior():
    from experiments.frontline.scripted_agents import (
        MutualPacker, PassBot, MirrorAgent)
    g = make_cm_game(max_turns=40, min_turns=0, end_margin=999)
    engine = create_engine(g)
    obs = engine.reset()

    # PassBot always passes.
    pb = PassBot(player=2).bind(engine)
    a, _, _ = pb.select_action(obs, legal_actions=engine.get_legal_actions())
    assert a == engine.total_cells

    # MutualPacker stays >= 5 from every enemy stone.
    engine.reset()
    x, _, _ = _interior_cell(engine.topo)
    engine.board_owners[x] = 2
    engine._recompute_field()
    mp = MutualPacker(player=1).bind(engine)
    a, _, _ = mp.select_action(None, legal_actions=engine.get_legal_actions())
    assert engine.topo.distance(a, x) >= 5

    # MirrorAgent mirrors the opponent's last placement through the
    # point reflection c -> W*W-1-c.
    engine.reset()
    mi = MirrorAgent(player=2).bind(engine)
    mi.select_action(None, legal_actions=[engine.total_cells])  # snapshot empty board
    engine.step(45)   # P1 places
    a, _, _ = mi.select_action(None, legal_actions=engine.get_legal_actions())
    assert a == W * W - 1 - 45


def test_stage0_pinned_geometry_assumptions():
    engine = create_engine(make_cm_game())
    topo = engine.topo
    x, _, _ = _interior_cell(topo)
    assert topo.distance(x, x + 1) == 1
    assert topo.distance(x, x + 2) == 2
    assert topo.distance(x, x + W) == 1   # next row is adjacent on hex_rhombus
