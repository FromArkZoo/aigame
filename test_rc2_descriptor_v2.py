"""Unit tests for the RC2 descriptor-v2 probe: TacticalAgent behavior,
mirrored-pair seed scheme, guard arithmetic, bar evaluators, and every
decide_verdict branch (synthetically, before any probe data — the Phase B
pattern).
"""
from __future__ import annotations

import copy

import numpy as np
import pytest

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)
import metrics.tactical_agent as ta
from metrics.tactical_agent import (
    TacticalAgent,
    restore_engine,
    snapshot_engine,
)
from experiments.rc2_descriptor_v2.run_probe import (
    decide_verdict,
    eval_bar_g_reach,
    eval_bar_g_rush,
    eval_bar_g_tilt,
    eval_bar_v2_nonreg,
    eval_bar_v2_rank,
    guard_reach,
    guard_rush,
    guard_tilt,
    pair_seeds,
    rollout_tactical,
    spearman,
)


# ---------------------------------------------------------------------------
# Test games (tiny 3x3 grid; connection win along dim 0 for P1, dim 1 for P2)
# Cell layout (little-endian, topology.py cell_to_coords: coords[0] is the
# FASTEST-varying dimension): cell = coord0 + coord1 * 3, so
#   cells 0,1,2 = coord1 row 0 with coord0 = 0,1,2 (a dim-0 spanning line),
#   cells 0,3,6 = coord0 column 0 with coord1 = 0,1,2 (a dim-1 line).
# ---------------------------------------------------------------------------

def tiny_game(**overrides) -> GameDefV2:
    kwargs = dict(
        game_id="tiny",
        num_dimensions=2,
        axis_size=3,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere",
                                     first_move_anywhere=True),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(condition_type="connection",
                                   threshold=0.5, target_dimension=0,
                                   target_dimension_p2=1, max_turns=50),
        turn_structure=TurnStructure(turn_type="alternating",
                                     pieces_per_turn=1),
        action_rule=ActionRule(action_types=("place",)),
    )
    kwargs.update(overrides)
    return GameDefV2(**kwargs)


def play(engine, *actions):
    obs = None
    for a in actions:
        obs, _, _, _ = engine.step(a)
    return obs


# ---------------------------------------------------------------------------
# TacticalAgent: WIN-IN-1
# ---------------------------------------------------------------------------

def test_plays_win_in_1_placement():
    # P1 at 0,1 (coord0=0,1) after replaying moves; placing 2 (coord0=2)
    # completes the dim-0 face-to-face connection. P2 at 3,4 (both
    # coord1=1) has no win-in-1.
    engine = create_engine(tiny_game())
    obs = engine.reset()
    obs = play(engine, 0, 3, 1, 4)  # P1: 0, 1; P2: 3, 4; P1 to move
    agent = TacticalAgent(engine, player_num=1, seed=0)
    action, lp, val = agent.select_action(
        obs, legal_actions=engine.get_legal_actions())
    assert (action, lp, val) == (2, 0.0, 0.0)
    # The winning action actually wins when played on the live engine.
    engine.step(2)
    assert engine.done and engine._winner == 1


def test_plays_win_in_1_via_move_action():
    # Move-only game: P1 stones 0,1,5; moving 5 -> 2 yields {0,1,2}
    # spanning dim 0 (a win via move counts in the <=512 exhaustive scan).
    # P2 stones 6,7 (both coord1=2) cannot win by any single move.
    game = tiny_game(action_rule=ActionRule(action_types=("move",)))
    engine = create_engine(game)
    engine.reset()
    engine.board_owners[[0, 1, 5]] = 1
    engine.board_owners[[6, 7]] = 2
    engine.piece_counts = [3, 2]
    agent = TacticalAgent(engine, player_num=1, seed=0)
    legal = engine.get_legal_actions()
    action, _, _ = agent.select_action(None, legal_actions=legal)
    decoded = game.decode_action(action)
    assert decoded == {"type": "move", "from_cell": 5, "to_cell": 2}
    engine.step(action)
    assert engine.done and engine._winner == 1


# ---------------------------------------------------------------------------
# TacticalAgent: BLOCK-WIN-IN-1
# ---------------------------------------------------------------------------

def test_blocks_opponent_win_in_1():
    # P1: 0, 1 (threatens 2); P2: 4 only — P2 has no win-in-1, must block 2.
    engine = create_engine(tiny_game())
    obs = engine.reset()
    obs = play(engine, 0, 4, 1)  # P2 to move
    agent = TacticalAgent(engine, player_num=2, seed=0)
    action, _, _ = agent.select_action(
        obs, legal_actions=engine.get_legal_actions())
    assert action == 2


def test_own_win_beats_block():
    # P1 at 0,1 threatens 2 (dim-0 span). P2 at 5=(2,1), 8=(2,2) also wins
    # at 2=(2,0): {2,5,8} is a connected coord1-spanning line. Cell 2 is
    # simultaneously P2's own win AND the block; the agent must find it via
    # the WIN-IN-1 path and actually win when it is played.
    engine = create_engine(tiny_game())
    engine.reset()
    engine.board_owners[[0, 1]] = 1
    engine.board_owners[[5, 8]] = 2
    engine.piece_counts = [2, 2]
    engine.current_player = 2
    engine.step_count = 4
    agent = TacticalAgent(engine, player_num=2, seed=0)
    action, _, _ = agent.select_action(
        None, legal_actions=engine.get_legal_actions())
    assert action == 2
    engine.step(2)
    assert engine.done and engine._winner == 2


# ---------------------------------------------------------------------------
# TacticalAgent: densify fallback
# ---------------------------------------------------------------------------

def test_densify_fallback_maximizes_adjacency():
    # No win/block anywhere: P1 at center (4), P2 at corner (0). P1's best
    # placements by (friendly_adj - enemy_adj) are 5 and 7 (score 1; cells
    # 1 and 3 touch both stones, score 0).
    engine = create_engine(tiny_game())
    obs = engine.reset()
    obs = play(engine, 4, 0)  # P1: 4; P2: 0; P1 to move
    for seed in range(5):
        agent = TacticalAgent(engine, player_num=1, seed=seed)
        action, _, _ = agent.select_action(
            obs, legal_actions=engine.get_legal_actions())
        assert action in (5, 7)


def test_densify_fallback_passes_without_placements():
    # Move-only game with no win available: fallback restricts to
    # placements + pass -> pass (no placements exist).
    game = tiny_game(action_rule=ActionRule(action_types=("move",)))
    engine = create_engine(game)
    engine.reset()
    engine.board_owners[[4]] = 1
    engine.board_owners[[0]] = 2
    engine.piece_counts = [1, 1]
    agent = TacticalAgent(engine, player_num=1, seed=0)
    action, _, _ = agent.select_action(
        None, legal_actions=engine.get_legal_actions())
    assert action == game.total_cells  # pass


# ---------------------------------------------------------------------------
# TacticalAgent: pie rule
# ---------------------------------------------------------------------------

def test_always_swaps_on_pie():
    engine = create_engine(tiny_game(pie_rule=True))
    obs = engine.reset()
    obs = play(engine, 4)  # P1 played center; P2 offered the swap
    agent = TacticalAgent(engine, player_num=2, seed=0)
    legal = engine.get_legal_actions()
    assert engine.game.swap_action_idx in legal
    action, _, _ = agent.select_action(obs, legal_actions=legal)
    assert action == engine.game.swap_action_idx


# ---------------------------------------------------------------------------
# Clone machinery: non-mutation + deepcopy equivalence
# ---------------------------------------------------------------------------

def _snap_equal(a: dict, b: dict) -> bool:
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, np.ndarray):
            if not np.array_equal(va, vb):
                return False
        elif va != vb:
            return False
    return True


def test_scans_do_not_mutate_live_engine():
    engine = create_engine(tiny_game())
    obs = engine.reset()
    obs = play(engine, 0, 2, 3)  # P2 to move (block scenario: heavy scans)
    before = snapshot_engine(engine)
    agent = TacticalAgent(engine, player_num=2, seed=0)
    agent.select_action(obs, legal_actions=engine.get_legal_actions())
    assert _snap_equal(before, snapshot_engine(engine))


def test_snapshot_restore_step_matches_deepcopy_step():
    # Custodian-capture game exercises piece_counts + board mutation paths.
    game = tiny_game(capture_rule=CaptureRule(capture_type="custodian"))
    engine = create_engine(game)
    engine.reset()
    play(engine, 4, 5, 0)  # P1: 4, 0; P2: 5; P2 to move
    snap = snapshot_engine(engine)
    scratch = create_engine(game)
    scratch.reset()
    for action in engine.get_legal_actions():
        ref = copy.deepcopy(engine)
        ref.step(action)
        restore_engine(scratch, snap)
        scratch.step(action)
        assert np.array_equal(ref.board_owners, scratch.board_owners)
        assert np.array_equal(ref.board_values, scratch.board_values)
        assert (ref.done, ref._winner, ref.step_count, ref.current_player,
                ref.piece_counts, ref.consecutive_passes) == \
               (scratch.done, scratch._winner, scratch.step_count,
                scratch.current_player, scratch.piece_counts,
                scratch.consecutive_passes)
    # Live engine untouched throughout.
    assert _snap_equal(snap, snapshot_engine(engine))


# ---------------------------------------------------------------------------
# Scan-set sizing rule (SCAN_LIMIT / HEURISTIC_TOP_K)
# ---------------------------------------------------------------------------

def test_win_scan_includes_pass_and_excludes_swap_when_small():
    engine = create_engine(tiny_game(pie_rule=True))
    engine.reset()
    agent = TacticalAgent(engine, player_num=1, seed=0)
    legal = list(range(9)) + [9, engine.game.swap_action_idx]
    cands = agent._win_scan_candidates(legal, 1)
    assert 9 in cands                            # pass included
    assert engine.game.swap_action_idx not in cands  # swap excluded


def test_win_scan_top_k_when_over_limit(monkeypatch):
    monkeypatch.setattr(ta, "SCAN_LIMIT", 3)
    monkeypatch.setattr(ta, "HEURISTIC_TOP_K", 2)
    engine = create_engine(tiny_game())
    obs = engine.reset()
    obs = play(engine, 4, 0)  # P1 at 4 -> neighbors of 4 score 1 for P1
    agent = TacticalAgent(engine, player_num=1, seed=0)
    legal = engine.get_legal_actions()  # 7 placements + pass > limit 3
    cands = agent._win_scan_candidates(legal, 1)
    # top-2 placements by densify score: 1 and 3 score... neighbors of 4
    # are 1,3,5,7 (score 1 each, but 1 and 3 also touch P2's 0 -> score 0).
    # Highest scorers are 5 and 7 (score 1); tie-break ascending index.
    assert cands == [5, 7]
    assert len(cands) == 2
    assert all(a < engine.total_cells for a in cands)


# ---------------------------------------------------------------------------
# Mirrored-pair seed scheme
# ---------------------------------------------------------------------------

def test_pair_seeds_scheme():
    assert pair_seeds(0) == ((1, 2), (2, 1))
    assert pair_seeds(7) == ((7001, 7002), (7002, 7001))
    assert pair_seeds(49) == ((49001, 49002), (49002, 49001))


def test_pair_seeds_mirror_swaps_seats():
    for i in range(50):
        (a1, a2), (b1, b2) = pair_seeds(i)
        assert (a1, a2) == (b2, b1)
        assert a1 != a2


def test_mirrored_rollouts_swap_seat_outcomes_on_symmetric_game():
    # Sanity: the mirror really runs (same game, seeds swapped) and both
    # rollouts complete with a recorded winner / trace shape.
    game = tiny_game()
    (s1, s2), (m1, m2) = pair_seeds(3)
    r_a = rollout_tactical(game, s1, s2)
    r_b = rollout_tactical(game, m1, m2)
    for r in (r_a, r_b):
        assert r["plies"] == len(r["owner_snapshots"])
        assert r["winner"] in (1, 2, None)


# ---------------------------------------------------------------------------
# Guard arithmetic (synthetic counts)
# ---------------------------------------------------------------------------

def rec(winner, plies=20, timeout=False):
    return dict(winner=winner, plies=plies, timeout=timeout)


def test_guard_rush_boundary_inclusive():
    # 1 of 4 decisive rollouts won in <=6 plies -> 25% -> fires (>=).
    records = [rec(1, 6), rec(2, 30), rec(1, 30), rec(2, 30),
               rec(None, 100)]
    fires, share = guard_rush(records)
    assert fires and share == pytest.approx(0.25)
    # 7 plies is not <=6; share drops below the bar.
    records = [rec(1, 7), rec(2, 30), rec(1, 30), rec(2, 30)]
    fires, share = guard_rush(records)
    assert not fires and share == pytest.approx(0.0)


def test_guard_rush_denominator_is_decisive_only():
    records = [rec(1, 3)] + [rec(None, 3)] * 99  # draws don't dilute
    fires, share = guard_rush(records)
    assert fires and share == pytest.approx(1.0)
    assert guard_rush([rec(None)] * 10) == (False, pytest.approx(float("nan"), nan_ok=True))


def test_guard_reach_threshold_only_and_strict():
    # Non-threshold: n/a.
    fires, _ = guard_reach([rec(1)] * 10, "connection")
    assert fires is None
    # 19/100 decisive before max_turns -> fires (< 20%).
    records = ([rec(1, timeout=False)] * 19
               + [rec(1, timeout=True)] * 31 + [rec(None)] * 50)
    fires, share = guard_reach(records, "threshold")
    assert fires is True and share == pytest.approx(0.19)
    # exactly 20% -> does NOT fire (strict <).
    records = ([rec(1, timeout=False)] * 20
               + [rec(1, timeout=True)] * 30 + [rec(None)] * 50)
    fires, share = guard_reach(records, "threshold")
    assert fires is False and share == pytest.approx(0.20)


def test_guard_reach_timeout_decisives_do_not_count():
    # All decisive but every one at max_turns -> 0% before max -> fires.
    fires, share = guard_reach([rec(1, timeout=True)] * 100, "threshold")
    assert fires is True and share == 0.0


def test_guard_tilt_boundary_inclusive_and_decisive_only():
    records = [rec(1)] * 8 + [rec(2)] * 2 + [rec(None)] * 90
    fires, share = guard_tilt(records)
    assert fires and share == pytest.approx(0.80)
    records = [rec(1)] * 79 + [rec(2)] * 21
    fires, share = guard_tilt(records)
    assert not fires and share == pytest.approx(0.79)
    assert guard_tilt([rec(None)] * 4)[0] is False


# ---------------------------------------------------------------------------
# Bar evaluators (synthetic)
# ---------------------------------------------------------------------------

PROTECTED_RUSH = ("e1453dac5445", "d4015a646ae3", "s_flip_r2",
                  "a1_field_connect")


def test_bar_g_rush():
    rush = {k: False for k in PROTECTED_RUSH}
    rush["S1"] = True
    assert eval_bar_g_rush(rush)[0]
    rush["d4015a646ae3"] = True            # protected negative fires
    assert not eval_bar_g_rush(rush)[0]
    rush["d4015a646ae3"] = False
    rush["S1"] = False                      # known positive misses
    assert not eval_bar_g_rush(rush)[0]


def test_bar_g_reach():
    assert eval_bar_g_reach({"S2": True, "e1453dac5445": False})[0]
    assert not eval_bar_g_reach({"S2": False, "e1453dac5445": False})[0]
    assert not eval_bar_g_reach({"S2": True, "e1453dac5445": True})[0]


def test_bar_g_tilt():
    base = {"S4": False, "S5": True, "s_flip_r2": False,
            "a1_field_connect": False}
    assert eval_bar_g_tilt(base)[0]                       # >=1 of S4/S5
    assert eval_bar_g_tilt({**base, "S4": True})[0]
    assert not eval_bar_g_tilt({**base, "S5": False})[0]  # neither fires
    assert not eval_bar_g_tilt({**base, "s_flip_r2": True})[0]
    assert not eval_bar_g_tilt({**base, "a1_field_connect": True})[0]


def _rank_inputs(s_dramas, fired_s, e1453=0.50, d4015=0.55):
    drama = {"e1453dac5445": e1453, "d4015a646ae3": d4015}
    fired = {}
    for s, v in s_dramas.items():
        drama[s] = v
        fired[s] = s in fired_s
    return drama, fired


def test_bar_v2_rank_pass():
    drama, fired = _rank_inputs(
        {"S1": 0.40, "S2": 0.30, "S3": 0.52, "S4": 0.20, "S5": 0.10},
        fired_s={"S1", "S2", "S4", "S5"})
    # fired all < min(controls)=0.50; clean S3=0.52 <= max(controls)=0.55.
    ok, _ = eval_bar_v2_rank(drama, fired)
    assert ok


def test_bar_v2_rank_fails_when_fired_s_beats_a_control():
    drama, fired = _rank_inputs(
        {"S1": 0.51, "S2": 0.30, "S3": 0.40, "S4": 0.20, "S5": 0.10},
        fired_s={"S1"})  # 0.51 >= min(controls) 0.50
    assert not eval_bar_v2_rank(drama, fired)[0]


def test_bar_v2_rank_fails_when_clean_s_outranks_both_controls():
    drama, fired = _rank_inputs(
        {"S1": 0.40, "S2": 0.30, "S3": 0.60, "S4": 0.20, "S5": 0.10},
        fired_s={"S1"})  # clean S3 0.60 > max(controls) 0.55
    assert not eval_bar_v2_rank(drama, fired)[0]


def test_bar_v2_rank_vacuous_with_no_fired_s_games():
    drama, fired = _rank_inputs(
        {"S1": 0.40, "S2": 0.30, "S3": 0.20, "S4": 0.10, "S5": 0.05},
        fired_s=set())
    assert eval_bar_v2_rank(drama, fired)[0]


def test_bar_v2_rank_not_evaluable_on_nan():
    drama, fired = _rank_inputs(
        {"S1": float("nan"), "S2": 0.3, "S3": 0.2, "S4": 0.1, "S5": 0.1},
        fired_s=set())
    ok, detail = eval_bar_v2_rank(drama, fired)
    assert not ok and "not evaluable" in detail


def _nonreg_dramas(**overrides):
    d = {
        # ABOVE
        "d4015a646ae3": 0.30, "s_flip_r2": 0.28, "a1_field_connect": 0.26,
        # BELOW
        "e52e8889517a": 0.10, "bfd1bb7ced76": 0.12,
        "e1453dac5445": 0.08, "1fea3357dca4": 0.11,
        # secondary pair partner (BUFFER)
        "573562833174": 0.20,
    }
    d.update(overrides)
    return d


def test_bar_v2_nonreg_pass():
    ok, detail = eval_bar_v2_nonreg(_nonreg_dramas())
    assert ok


def test_bar_v2_nonreg_fails_each_subbar():
    # 1. mean(ABOVE) <= mean(BELOW)
    assert not eval_bar_v2_nonreg(_nonreg_dramas(
        d4015a646ae3=0.01, s_flip_r2=0.01, a1_field_connect=0.01,
        e1453dac5445=0.005, **{"573562833174": 0.02}))[0]
    # 2. two BELOW games above min(ABOVE) (=0.26)
    assert not eval_bar_v2_nonreg(_nonreg_dramas(
        e52e8889517a=0.27, bfd1bb7ced76=0.29))[0]
    # 3. e1453 above an ABOVE game (one inversion passes bar 2 but the
    # inverted game being e1453 fails bar 3)
    assert not eval_bar_v2_nonreg(_nonreg_dramas(
        e1453dac5445=0.27, **{"573562833174": 0.30}))[0]
    # 4. secondary inversion: 573 <= e1453
    assert not eval_bar_v2_nonreg(_nonreg_dramas(
        **{"573562833174": 0.05}))[0]


def test_bar_v2_nonreg_one_inversion_tolerated():
    # Exactly one BELOW game above min(ABOVE), and it is not e1453 -> PASS.
    ok, _ = eval_bar_v2_nonreg(_nonreg_dramas(bfd1bb7ced76=0.27))
    assert ok


# ---------------------------------------------------------------------------
# Decision grammar — every branch
# ---------------------------------------------------------------------------

def _bars(g_rush=True, g_reach=True, g_tilt=True, rank=True, nonreg=True):
    return {"G-RUSH": g_rush, "G-REACH": g_reach, "G-TILT": g_tilt,
            "V2-RANK": rank, "V2-NONREG": nonreg}


def test_verdict_go_when_all_five_pass():
    assert decide_verdict(_bars()) == "DESCRIPTOR_V2_GO"


def test_verdict_guards_only_when_rank_fails():
    assert decide_verdict(_bars(rank=False)) == "GUARDS_ONLY"


def test_verdict_guards_only_when_nonreg_fails():
    assert decide_verdict(_bars(nonreg=False)) == "GUARDS_ONLY"


def test_verdict_guards_only_when_both_quality_bars_fail():
    assert decide_verdict(_bars(rank=False, nonreg=False)) == "GUARDS_ONLY"


def test_verdict_kill_on_any_g_bar_failure():
    assert decide_verdict(_bars(g_rush=False)) == "DESCRIPTOR_V2_KILL"
    assert decide_verdict(_bars(g_reach=False)) == "DESCRIPTOR_V2_KILL"
    assert decide_verdict(_bars(g_tilt=False)) == "DESCRIPTOR_V2_KILL"
    # KILL outranks the quality bars (even if they pass or fail).
    assert decide_verdict(_bars(g_tilt=False, rank=False)) \
        == "DESCRIPTOR_V2_KILL"


def test_verdict_incomplete_dominates():
    assert decide_verdict(_bars(), incomplete="wall cap") \
        == "PROBE_INCOMPLETE"
    assert decide_verdict(_bars(g_rush=False), incomplete="unloadable") \
        == "PROBE_INCOMPLETE"


# ---------------------------------------------------------------------------
# Spearman helper
# ---------------------------------------------------------------------------

def test_spearman_perfect_and_inverted():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)


def test_spearman_matches_scipy_with_ties():
    scipy_stats = pytest.importorskip("scipy.stats")
    xs = [0.38, 0.34, 0.31, 0.28, 0.26, 0.12, 0.05]
    ys = [1.77, 3.20, 3.10, 3.00, 3.07, 3.83, 3.83]  # tie in ys
    expected = scipy_stats.spearmanr(xs, ys).statistic
    assert spearman(xs, ys) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# End-to-end rollout sanity on the tiny game
# ---------------------------------------------------------------------------

def test_rollout_tactical_trace_shape():
    r = rollout_tactical(tiny_game(), 1, 2)
    assert r["plies"] == len(r["owner_snapshots"])
    assert r["winner"] in (1, 2, None)
    assert isinstance(r["timeout"], bool)
    assert r["game_length"] >= r["plies"]
    # Tactical play on a 3x3 connection game must be decisive and short:
    # the win-in-1 scan guarantees no winning placement is ever missed.
    assert r["winner"] is not None
    assert r["plies"] <= 9
