#!/usr/bin/env python3
"""Pie rule tests (R20 blocker S1).

Pie rule design (per R20_plan.md):
  - GameDefV2.pie_rule: bool field. When True, action space gains a trailing
    pie_swap action (swap_action_idx == num_actions - 1).
  - The swap is legal exactly once: at P2's first action (current_player==2,
    step_count==1), and only if not already resolved.
  - Swap effect: flip board_owners 1↔2, negate signed influence values, swap
    piece counts, advance turn to P1, mark _pie_resolved/_pie_used True, and
    reset super-ko history to start from the post-swap state.
  - Pie offer expires after P2's first action regardless of choice.

Run as: .venv/bin/python test_pie_rule.py
"""
from __future__ import annotations

import sys
import traceback

import numpy as np

from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)


# ----------------------------------------------------------------------
# Test scaffolding
# ----------------------------------------------------------------------

passed: list[str] = []
failed: list[tuple[str, str]] = []


def case(name: str, fn) -> None:
    try:
        fn()
        passed.append(name)
        print(f"  PASS  {name}")
    except Exception as e:  # noqa: BLE001
        failed.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}: {e}")


def make_game(
    *,
    pie_rule: bool = False,
    propagation_rule: PropagationRule | None = None,
    capture_type: str = "none",
    win_type: str = "territory",
) -> GameDefV2:
    """Minimal valid 4x4 grid game (axis 4, 2D)."""
    return GameDefV2(
        game_id=f"pie_test_pie={int(pie_rule)}",
        num_dimensions=2,
        axis_size=4,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type=capture_type),
        propagation_rule=propagation_rule or PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type=win_type, threshold=0.5, max_turns=50,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=pie_rule,
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_no_pie_no_swap_action() -> None:
    """pie_rule=False: num_actions excludes swap; legal actions never contain it."""
    game = make_game(pie_rule=False)
    expected_n = game.total_cells + 1  # place + pass, no move
    assert game.num_actions == expected_n, (
        f"expected num_actions={expected_n}, got {game.num_actions}"
    )
    engine = GameEngineV2(game)
    engine.reset()
    # Swap idx accessor must raise on disabled pie_rule.
    try:
        _ = game.swap_action_idx
        raise AssertionError("swap_action_idx should raise when pie_rule=False")
    except ValueError:
        pass
    # Walk a few plies; no legal action should equal the would-be swap idx.
    legals = engine.get_legal_actions()
    forbidden = expected_n  # one past the last valid action
    assert forbidden not in legals, (
        f"pie_rule=False but action {forbidden} appeared in legal set {legals}"
    )


def test_swap_idx_layout() -> None:
    """pie_rule=True: num_actions += 1; swap idx is the trailing index."""
    game = make_game(pie_rule=True)
    expected_n = game.total_cells + 1 + 1  # place + pass + swap
    assert game.num_actions == expected_n, (
        f"expected num_actions={expected_n}, got {game.num_actions}"
    )
    assert game.swap_action_idx == expected_n - 1, (
        f"swap_action_idx mismatch: {game.swap_action_idx} vs {expected_n - 1}"
    )


def test_swap_legal_only_at_p2_first_move() -> None:
    """Swap must appear exactly when current_player==2 and step_count==1."""
    game = make_game(pie_rule=True)
    engine = GameEngineV2(game)
    engine.reset()

    # P1 first move: swap NOT in legal actions.
    assert game.swap_action_idx not in engine.get_legal_actions(), (
        "swap should not be legal at P1's first move"
    )

    # P1 places at cell 0.
    engine.step(0)
    assert engine.current_player == 2, "after P1 move, current_player must be 2"
    assert engine.step_count == 1, f"step_count={engine.step_count}, expected 1"

    # P2's first action: swap IS in legal actions.
    assert game.swap_action_idx in engine.get_legal_actions(), (
        "swap should be legal at P2's first move"
    )

    # P2 plays normally (cell 5) — pie offer should now expire.
    engine.step(5)
    # Subsequent legal actions (P1's turn 2) should NOT include swap.
    assert game.swap_action_idx not in engine.get_legal_actions(), (
        "swap leaked into post-resolution legal actions"
    )


def test_swap_flips_owners_and_advances_turn() -> None:
    """Swap action: P1's stone becomes P2's; turn passes to P1; step_count=2."""
    game = make_game(pie_rule=True)
    engine = GameEngineV2(game)
    engine.reset()

    engine.step(0)  # P1 places at cell 0
    assert engine.board_owners[0] == 1
    assert engine.piece_counts == [1, 0]

    engine.step(game.swap_action_idx)  # P2 swaps

    assert engine.board_owners[0] == 2, (
        f"after swap, cell 0 owner should be 2, got {engine.board_owners[0]}"
    )
    assert engine.piece_counts == [0, 1], (
        f"piece counts not swapped: {engine.piece_counts}"
    )
    assert engine.current_player == 1, (
        f"after swap, current_player should be 1, got {engine.current_player}"
    )
    assert engine.step_count == 2, (
        f"after swap, step_count should be 2, got {engine.step_count}"
    )
    assert engine._pie_resolved is True
    assert engine._pie_used is True
    assert not engine.done, "swap should not end the game"


def test_swap_negates_influence_values() -> None:
    """If P1's first move propagates positive influence, after swap those
    values must be negated (P2 owns the position now)."""
    game = make_game(
        pie_rule=True,
        propagation_rule=PropagationRule(
            prop_type="influence", radius=1, strength=1.0, decay=0.5,
        ),
    )
    engine = GameEngineV2(game)
    engine.reset()

    engine.step(5)  # P1 places — influence propagates positive around cell 5
    pre_swap = engine.board_values.copy()
    assert pre_swap[5] > 0, f"expected positive influence at cell 5, got {pre_swap[5]}"

    engine.step(game.swap_action_idx)
    post_swap = engine.board_values

    np.testing.assert_allclose(
        post_swap, -pre_swap,
        err_msg="board_values not negated by swap",
    )


def test_decline_swap_normal_p2_move() -> None:
    """If P2 plays a normal move at ply 2, no flip happens but pie offer
    still expires (one-shot offer)."""
    game = make_game(pie_rule=True)
    engine = GameEngineV2(game)
    engine.reset()

    engine.step(0)  # P1 cell 0
    engine.step(5)  # P2 cell 5 (normal move, declines pie)

    assert engine.board_owners[0] == 1, "P1 stone must remain P1"
    assert engine.board_owners[5] == 2, "P2 stone must be at cell 5"
    assert engine.piece_counts == [1, 1]
    assert engine._pie_resolved is True, "pie offer should be resolved after P2 move"
    assert engine._pie_used is False, "no swap occurred → _pie_used must be False"

    # Sanity: ply 3 is P1's turn, swap not legal.
    assert engine.current_player == 1
    assert game.swap_action_idx not in engine.get_legal_actions()


def test_swap_only_legal_once() -> None:
    """If P2 swaps, the offer must never reappear later in the game."""
    game = make_game(pie_rule=True)
    engine = GameEngineV2(game)
    engine.reset()

    engine.step(0)
    engine.step(game.swap_action_idx)

    # Walk several plies; swap must never reappear.
    for cell in (1, 2, 3, 4, 6, 7):
        if engine.done:
            break
        legals = engine.get_legal_actions()
        assert game.swap_action_idx not in legals, (
            f"swap reappeared at step {engine.step_count}, player {engine.current_player}"
        )
        if cell in legals:
            engine.step(cell)
        else:
            engine.step(legals[0])


def test_serialization_roundtrip() -> None:
    """to_dict/from_dict preserves pie_rule. Version bumps to 5."""
    game = make_game(pie_rule=True)
    d = game.to_dict()
    assert d.get("pie_rule") is True, f"to_dict missing pie_rule=True: {d}"
    assert d.get("version") == 5, f"version should be 5, got {d.get('version')}"

    restored = GameDefV2.from_dict(d)
    assert restored.pie_rule is True
    assert restored.num_actions == game.num_actions
    assert restored.swap_action_idx == game.swap_action_idx

    # Backward compat: dict missing pie_rule must default to False.
    d_no_pie = {**d}
    del d_no_pie["pie_rule"]
    d_no_pie["version"] = 3
    restored2 = GameDefV2.from_dict(d_no_pie)
    assert restored2.pie_rule is False


def test_complexity_increments_with_pie_rule() -> None:
    """total_complexity gains 1 when pie_rule is enabled (Go Essence input)."""
    base = make_game(pie_rule=False).total_complexity()
    with_pie = make_game(pie_rule=True).total_complexity()
    assert with_pie == base + 1, (
        f"complexity delta wrong: {base} -> {with_pie}"
    )


def test_swap_resets_ko_history() -> None:
    """After swap, super-ko history starts fresh from the post-swap board.

    This avoids the pre-swap colour-1 history being matched against the
    post-swap colour-2 board hash on every subsequent move.
    """
    game = make_game(
        pie_rule=True,
        capture_type="custodian",  # forces needs_ko_rule=True
    )
    engine = GameEngineV2(game)
    engine.reset()
    assert engine._needs_ko, "test needs a ko-tracking game"

    engine.step(0)  # P1
    pre_swap_history = set(engine._position_history)
    engine.step(game.swap_action_idx)

    # History must contain exactly one entry: the post-swap board hash.
    post_history = engine._position_history
    assert len(post_history) == 1, (
        f"expected 1 post-swap history entry, got {len(post_history)}"
    )
    # And that entry must be the current state's hash.
    assert engine._board_hash() in post_history
    # Pre-swap history entries must not bleed through (they referred to a
    # different colour assignment).
    bleed = pre_swap_history & post_history
    assert not bleed, f"pre-swap history bled into post-swap: {bleed}"


def test_decode_swap_action() -> None:
    """decode_action returns {'type': 'pie_swap'} for the swap idx."""
    game = make_game(pie_rule=True)
    decoded = game.decode_action(game.swap_action_idx)
    assert decoded == {"type": "pie_swap"}, f"unexpected decode: {decoded}"


def _make_connection_game(*, axis: int = 5, pie_rule: bool = True) -> GameDefV2:
    """Tiny grid with connection win — P1 connects dim-0, P2 connects dim-1."""
    return GameDefV2(
        game_id="conn_test",
        num_dimensions=2,
        axis_size=axis,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="connection",
            target_dimension=0,
            target_dimension_p2=1,
            threshold=0.5,
            max_turns=100,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=pie_rule,
    )


def test_swap_flips_connection_goals_p1() -> None:
    """After pie swap, colour 1's goal becomes the ORIGINAL P2 goal (dim-1).
    A colour-1 line that connects dim-1 faces wins; a colour-1 line that
    only connects dim-0 faces does not.

    Coord convention (verified): cell = c0 + c1 * axis with dim 0 varying
    fastest — so cells 1, 6, 11, 16, 21 form a dim-1-connecting line at
    fixed dim-0=1.
    """
    game = _make_connection_game(axis=5)
    engine = GameEngineV2(game)
    engine.reset()
    # P1 first stone at (0,0) = cell 0
    engine.step(0)
    # P2 swaps; goals flip. cell 0 now colour 2; current_player = 1.
    engine.step(game.swap_action_idx)
    assert engine._goals_swapped is True

    # Move sequence: colour 1 builds a dim-1 line at dim-0=1 column
    # (cells 1, 6, 11, 16, 21). Colour 2 plays a corner cluster that
    # cannot reach the cell-0 stone (the dim-0=1 wall blocks it).
    moves = [
        1,   # cur=1: cell (1,0)  — touches dim-1=0 face
        24,  # cur=2: cell (4,4)
        6,   # cur=1: cell (1,1)
        23,  # cur=2: cell (3,4)
        11,  # cur=1: cell (1,2)
        22,  # cur=2: cell (2,4)
        16,  # cur=1: cell (1,3)
        17,  # cur=2: cell (2,3)
        21,  # cur=1: cell (1,4) — completes dim-1 line for colour 1
    ]
    for m in moves:
        if engine.done:
            break
        engine.step(m)

    assert engine.done, (
        "colour 1 should have completed the dim-1 line and won "
        f"(step={engine.step_count}, board_owners snippet={engine.board_owners[:25]})"
    )
    assert engine._winner == 1, (
        f"colour 1 should win after dim-1 line, got winner={engine._winner}"
    )


def test_no_swap_no_goal_change() -> None:
    """If P2 declines the pie offer, _goals_swapped stays False and the
    standard P1=dim0 / P2=dim1 mapping holds."""
    game = _make_connection_game(axis=5)
    engine = GameEngineV2(game)
    engine.reset()
    engine.step(0)         # P1 cell 0
    engine.step(12)        # P2 declines (places cell 12)
    assert engine._goals_swapped is False
    assert engine._pie_resolved is True


def test_goals_swapped_serializes_with_engine_state() -> None:
    """The flag is engine state, not game-def state — fresh engines on the
    same game start with _goals_swapped=False even if a prior engine swapped."""
    game = _make_connection_game(axis=4)
    e1 = GameEngineV2(game)
    e1.reset()
    e1.step(0)
    e1.step(game.swap_action_idx)
    assert e1._goals_swapped is True
    # Fresh engine on the same game def must NOT inherit the flag.
    e2 = GameEngineV2(game)
    e2.reset()
    assert e2._goals_swapped is False, (
        "_goals_swapped leaked across engines via shared GameDefV2"
    )


def test_goals_swap_does_not_affect_non_connection_wins() -> None:
    """Threshold-race / territory wins are symmetric; the goals_swapped flag
    must be a no-op on those win-condition checks (no exception, normal
    behaviour)."""
    # Territory win: build engine, do P1 move + pie swap, then run a few more
    # plies; the absence of an exception under territory is the signal.
    game = make_game(
        pie_rule=True,
        capture_type="custodian",
        win_type="territory",
    )
    engine = GameEngineV2(game)
    engine.reset()
    engine.step(0)
    engine.step(game.swap_action_idx)
    # Should run a few non-game-ending plies cleanly.
    for cell in (1, 2, 3, 4, 5, 6, 7):
        if engine.done:
            break
        legals = engine.get_legal_actions()
        chosen = cell if cell in legals else legals[0]
        engine.step(chosen)
    # Engine still consistent — that's the assertion (no crash on territory
    # while _goals_swapped is True).
    assert engine._goals_swapped is True


def test_swap_on_empty_board_is_safe() -> None:
    """If P1 passes (legal first action), P2's swap on an empty board is a
    no-op flip but still resolves the pie offer and advances the turn."""
    game = make_game(pie_rule=True)
    engine = GameEngineV2(game)
    engine.reset()

    # P1 passes (action == total_cells)
    engine.step(game.total_cells)
    assert engine.current_player == 2
    assert engine.step_count == 1
    assert engine.piece_counts == [0, 0]

    # P2 swaps — board is empty, owner-flip is a no-op but state must advance.
    engine.step(game.swap_action_idx)
    assert engine._pie_resolved is True
    assert engine._pie_used is True
    assert engine.current_player == 1
    assert engine.piece_counts == [0, 0]


# ----------------------------------------------------------------------
# Evolution-pipeline propagation regression (R20 bug 2026-05-07)
# ----------------------------------------------------------------------
#
# Original R20 launch lost pie_rule across crossover and immigrant injection
# because evolution/operators_v2.py and game_engine/generator_v2.py both
# constructed GameDefV2 without forwarding pie_rule, defaulting it to False.
# These tests pin the propagation behaviour: mutation via deepcopy preserves;
# crossover ORs both parents; immigrants honour the generator attribute.


def test_mutation_preserves_pie_rule() -> None:
    from config import EvolutionConfig
    from evolution.operators_v2 import MutationOperatorV2
    parent = make_game(pie_rule=True, capture_type="custodian")
    op = MutationOperatorV2(EvolutionConfig(), np.random.default_rng(0))
    for s in range(20):
        op.rng = np.random.default_rng(s)
        child = op.mutate_game(parent)
        assert child.pie_rule is True, (
            f"mutation seed={s} dropped pie_rule"
        )


def test_crossover_or_semantics() -> None:
    from config import EvolutionConfig
    from evolution.operators_v2 import CrossoverOperatorV2
    a_pie = make_game(pie_rule=True, capture_type="custodian")
    b_pie = make_game(pie_rule=True, capture_type="surround")
    a_no = make_game(pie_rule=False, capture_type="custodian")
    b_no = make_game(pie_rule=False, capture_type="surround")
    op = CrossoverOperatorV2(EvolutionConfig(), np.random.default_rng(0))

    # Both pie => child pie. Sample many strategies via varied rng seeds.
    for s in range(30):
        op.rng = np.random.default_rng(s)
        child = op.crossover_games(a_pie, b_pie)
        assert child.pie_rule is True, (
            f"crossover(pie,pie) seed={s} dropped pie_rule"
        )

    # One pie + one no => child pie (OR semantics).
    for s in range(30):
        op.rng = np.random.default_rng(100 + s)
        child = op.crossover_games(a_pie, b_no)
        assert child.pie_rule is True, (
            f"crossover(pie,no) seed={s} dropped pie_rule"
        )

    # Neither pie => child no pie.
    for s in range(30):
        op.rng = np.random.default_rng(200 + s)
        child = op.crossover_games(a_no, b_no)
        assert child.pie_rule is False, (
            f"crossover(no,no) seed={s} unexpectedly enabled pie_rule"
        )


def test_immigrant_generator_honours_pie_rule_attr() -> None:
    from config import GameConfig
    from game_engine.generator_v2 import GameGeneratorV2
    cfg = GameConfig()
    # Default: pie_rule=False -> immigrants pie_rule=False.
    gen_off = GameGeneratorV2(cfg, seed=1)
    assert gen_off.pie_rule is False
    for s in range(5):
        g = gen_off.generate_game(seed=1000 + s)
        assert g.pie_rule is False, (
            f"immigrant seed={s} got pie_rule=True under default"
        )
    # pie_rule=True kw -> all immigrants pie_rule=True.
    gen_on = GameGeneratorV2(cfg, seed=1, pie_rule=True)
    assert gen_on.pie_rule is True
    for s in range(5):
        g = gen_on.generate_game(seed=2000 + s)
        assert g.pie_rule is True, (
            f"immigrant seed={s} dropped pie_rule with pie_rule=True generator"
        )


def test_loop_propagates_pie_from_seeds() -> None:
    from config import GenesisConfig
    from evolution.loop import EvolutionaryLoop
    cfg = GenesisConfig()
    cfg.evolution.population_size = 3
    seed_with_pie = make_game(pie_rule=True, capture_type="custodian")
    loop = EvolutionaryLoop(cfg, seed=42)
    # Pre-init: generator should default to False.
    assert loop.generator.pie_rule is False
    loop.initialize_population(seed_games=[seed_with_pie])
    # Post-init: loop should have detected pie in seeds and flipped generator.
    assert loop.generator.pie_rule is True, (
        "loop did not propagate pie_rule from seed_games to generator"
    )


# ----------------------------------------------------------------------
# Entry
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== Pie rule tests (S1, R20) ===\n")

    case("pie_rule=False: no swap action in num_actions or legals",
         test_no_pie_no_swap_action)
    case("pie_rule=True: num_actions+1, swap idx is trailing",
         test_swap_idx_layout)
    case("swap legal only at P2's first move", test_swap_legal_only_at_p2_first_move)
    case("swap flips owners + advances turn", test_swap_flips_owners_and_advances_turn)
    case("swap negates signed influence values", test_swap_negates_influence_values)
    case("declined swap: normal P2 move resolves offer", test_decline_swap_normal_p2_move)
    case("swap is one-shot, never reappears", test_swap_only_legal_once)
    case("to_dict/from_dict roundtrip preserves pie_rule", test_serialization_roundtrip)
    case("total_complexity +1 when pie_rule=True", test_complexity_increments_with_pie_rule)
    case("swap resets super-ko history", test_swap_resets_ko_history)
    case("decode_action handles swap idx", test_decode_swap_action)
    case("swap on empty board is safe (P1 pass + P2 swap)",
         test_swap_on_empty_board_is_safe)
    case("swap flips connection goals (colour-1 wins on what was P2's dim)",
         test_swap_flips_connection_goals_p1)
    case("no swap → no goal change", test_no_swap_no_goal_change)
    case("goals_swapped is engine state, not game-def state",
         test_goals_swapped_serializes_with_engine_state)
    case("goals_swap is no-op on territory/threshold/etc.",
         test_goals_swap_does_not_affect_non_connection_wins)

    # R20 evo-pipeline propagation regression (2026-05-07).
    case("mutation preserves pie_rule via deepcopy",
         test_mutation_preserves_pie_rule)
    case("crossover ORs pie_rule from both parents",
         test_crossover_or_semantics)
    case("immigrant generator honours pie_rule attr",
         test_immigrant_generator_honours_pie_rule_attr)
    case("loop propagates pie_rule from seeds to immigrant generator",
         test_loop_propagates_pie_from_seeds)

    print(f"\n{len(passed)} passed, {len(failed)} failed")
    if failed:
        print("\n--- failures ---")
        for name, tb in failed:
            print(f"\n{name}:\n{tb}")
        sys.exit(1)
    sys.exit(0)
