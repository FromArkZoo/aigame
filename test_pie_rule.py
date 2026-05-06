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

    print(f"\n{len(passed)} passed, {len(failed)} failed")
    if failed:
        print("\n--- failures ---")
        for name, tb in failed:
            print(f"\n{name}:\n{tb}")
        sys.exit(1)
    sys.exit(0)
