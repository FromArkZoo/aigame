#!/usr/bin/env python3
"""Komi (R21 S4) tests.

`komi_p2: float` on GameDefV2 is the fractional bonus added to P2's
effective score / count at win-condition check time:
  - threshold-race: P2's effective gain is ``komi_p2 * threshold``.
  - territory: P2's piece count gain is ``komi_p2 * num_active_cells``.

These tests poke the win-condition check directly via constructed
board states rather than running PPO, so they're millisecond-fast.

Run as: .venv/bin/python test_komi.py
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


def make_threshold_game(
    *,
    threshold: float = 10.0,
    komi_p2: float = 0.0,
    propagation_decay: float = 1.0,
) -> GameDefV2:
    """4x4 grid, threshold-race, influence-r=1 propagation. With decay=1.0,
    each placed stone contributes 1.0 to its own cell + 1.0 to each of its
    4 neighbours = 5.0 max (less near edges)."""
    return GameDefV2(
        game_id="komi_thresh",
        num_dimensions=2,
        axis_size=4,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=1, decay=propagation_decay,
        ),
        win_condition=WinCondition(
            condition_type="threshold", threshold=threshold, max_turns=50,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        komi_p2=komi_p2,
    )


def make_territory_game(
    *,
    threshold: float = 0.4,
    komi_p2: float = 0.0,
) -> GameDefV2:
    """4x4 grid, territory win at 40% of cells = 6.4 cells (P1 needs ≥7,
    P2 needs ≥7 by default — komi shifts P2's effective count up)."""
    return GameDefV2(
        game_id="komi_terr",
        num_dimensions=2,
        axis_size=4,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="territory", threshold=threshold, max_turns=50,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        komi_p2=komi_p2,
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_komi_zero_preserves_baseline_threshold() -> None:
    """komi_p2=0.0: threshold win behaves exactly as before R21 S4 — P1
    crosses threshold first → P1 wins."""
    game = make_threshold_game(threshold=4.0, komi_p2=0.0)
    engine = GameEngineV2(game)
    engine.reset()
    # Give P1 a score of 5.0, P2 a score of 3.0 → P1 effective=5, P2 effective=3.
    # Threshold=4 → only P1 crosses → P1 wins.
    engine.board_owners[0] = 1
    engine.board_values[0] = 5.0
    engine.board_owners[5] = 2
    engine.board_values[5] = -3.0
    engine._check_threshold(4.0)
    assert engine._winner == 1, (
        f"komi=0 baseline: P1 5.0 vs P2 3.0 over threshold 4 should give P1 win, got {engine._winner}"
    )


def test_komi_flips_marginal_threshold_to_p2() -> None:
    """A marginal P1 lead (effective P1=4.5, threshold=4) should flip to
    P2 win once komi_p2 = 0.15 (P2 effective = 3.0 + 0.15*4 = 3.6 — still
    < 4, so neither wins). Use a stronger setup: komi covers the gap."""
    # Setup: P1 effective = 4.5 (>4 → would win), P2 raw = 3.0.
    # komi_p2 = 0.5 → P2 effective = 3.0 + 0.5*4 = 5.0 > 4. Both cross.
    # Margins: P1 = 4.5 - 4 = 0.5; P2 = 5.0 - 4 = 1.0 → P2 wins.
    game = make_threshold_game(threshold=4.0, komi_p2=0.5)
    engine = GameEngineV2(game)
    engine.reset()
    engine.board_owners[0] = 1
    engine.board_values[0] = 4.5
    engine.board_owners[5] = 2
    engine.board_values[5] = -3.0
    engine._check_threshold(4.0)
    assert engine._winner == 2, (
        f"komi=0.5 + P1 effective=4.5 + P2 effective=5.0 should flip to P2, got {engine._winner}"
    )


def test_large_p1_lead_still_wins_under_komi() -> None:
    """Komi compensates for marginal seat bias, not structural lopsidedness.
    P1 effective = 8, P2 effective = 2, threshold = 4. Even with komi_p2=0.30
    (P2 +1.2), P2 effective stays at 3.2 < 4 → only P1 crosses → P1 wins."""
    game = make_threshold_game(threshold=4.0, komi_p2=0.30)
    engine = GameEngineV2(game)
    engine.reset()
    engine.board_owners[0] = 1
    engine.board_values[0] = 8.0
    engine.board_owners[5] = 2
    engine.board_values[5] = -2.0
    engine._check_threshold(4.0)
    assert engine._winner == 1, (
        f"large P1 lead 8 vs 2 under komi=0.30 should still give P1 win, got {engine._winner}"
    )


def test_komi_zero_preserves_baseline_territory() -> None:
    """Territory baseline (komi=0): 7 P1 cells out of 16 = 43.75% > 40% → P1 wins."""
    game = make_territory_game(threshold=0.4, komi_p2=0.0)
    engine = GameEngineV2(game)
    engine.reset()
    # Give P1 7 cells, P2 6 cells.
    for c in range(7):
        engine.board_owners[c] = 1
    for c in range(7, 13):
        engine.board_owners[c] = 2
    engine.piece_counts = [7, 6]
    engine._check_territory(0.4)
    assert engine._winner == 1, (
        f"komi=0 baseline territory: P1=7, P2=6 over 40% (~6.4 cells) should give P1 win, got {engine._winner}"
    )


def test_komi_flips_marginal_territory_to_p2() -> None:
    """Territory + komi_p2 large enough that P2's effective count crosses
    first. 16 cells × threshold=0.4 = 6.4 target. P1=7 cells (would win),
    P2=5 cells. komi_p2=0.20 → P2 effective = 5 + 0.20*16 = 5 + 3.2 = 8.2
    > 6.4. _check_territory iterates (1, 2) and short-circuits — P1 wins
    first under this iteration order even though P2 also qualifies. So
    drop P1 below threshold: P1=6 cells (effective 6), P2=4 cells
    (effective 4 + 3.2 = 7.2 > 6.4). Now only P2 crosses → P2 wins."""
    game = make_territory_game(threshold=0.4, komi_p2=0.20)
    engine = GameEngineV2(game)
    engine.reset()
    for c in range(6):
        engine.board_owners[c] = 1
    for c in range(6, 10):
        engine.board_owners[c] = 2
    engine.piece_counts = [6, 4]
    engine._check_territory(0.4)
    assert engine._winner == 2, (
        f"komi=0.20 + P1=6 + P2=4 should flip to P2 (P2 effective 7.2 > 6.4), got {engine._winner}"
    )


def test_to_dict_from_dict_roundtrip() -> None:
    """komi_p2 survives serialisation."""
    game = make_threshold_game(threshold=10.0, komi_p2=0.15)
    d = game.to_dict()
    assert "komi_p2" in d, "to_dict must include komi_p2 when non-zero"
    assert abs(d["komi_p2"] - 0.15) < 1e-9
    assert d["version"] == 6, f"version bumps to 6 when komi_p2 set, got {d.get('version')}"
    restored = GameDefV2.from_dict(d)
    assert abs(restored.komi_p2 - 0.15) < 1e-9, (
        f"from_dict must restore komi_p2, got {restored.komi_p2}"
    )


def test_to_dict_omits_komi_when_zero() -> None:
    """komi_p2=0.0 is backward-compatible — omitted from to_dict so older
    consumers don't break and DBs without the field round-trip cleanly."""
    game = make_threshold_game(threshold=10.0, komi_p2=0.0)
    d = game.to_dict()
    assert "komi_p2" not in d, (
        f"komi_p2=0.0 must not appear in to_dict, got {d.get('komi_p2')}"
    )
    assert d["version"] <= 5, f"version stays ≤5 when komi off, got {d.get('version')}"


def test_canonical_hash_distinguishes_komi() -> None:
    """S1a regression: different komi_p2 values must produce different
    canonical hashes (so the slate-dedup picks up komi as a kernel field)."""
    a = make_threshold_game(threshold=10.0, komi_p2=0.0)
    b = make_threshold_game(threshold=10.0, komi_p2=0.10)
    c = make_threshold_game(threshold=10.0, komi_p2=0.20)
    assert a.canonical_hash() != b.canonical_hash(), (
        "komi 0.0 vs 0.10 must produce distinct canonical hashes"
    )
    assert b.canonical_hash() != c.canonical_hash(), (
        "komi 0.10 vs 0.20 must produce distinct canonical hashes"
    )


def test_complexity_increments_with_komi() -> None:
    """total_complexity() picks up komi_p2 as a meaningful rule parameter."""
    base = make_threshold_game(threshold=10.0, komi_p2=0.0).total_complexity()
    with_komi = make_threshold_game(threshold=10.0, komi_p2=0.15).total_complexity()
    assert with_komi == base + 1, (
        f"total_complexity must += 1 when komi_p2 set: base={base}, with={with_komi}"
    )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Komi tests (R21 S4)")
    print("-" * 50)
    case("komi_zero_preserves_baseline_threshold", test_komi_zero_preserves_baseline_threshold)
    case("komi_flips_marginal_threshold_to_p2", test_komi_flips_marginal_threshold_to_p2)
    case("large_p1_lead_still_wins_under_komi", test_large_p1_lead_still_wins_under_komi)
    case("komi_zero_preserves_baseline_territory", test_komi_zero_preserves_baseline_territory)
    case("komi_flips_marginal_territory_to_p2", test_komi_flips_marginal_territory_to_p2)
    case("to_dict_from_dict_roundtrip", test_to_dict_from_dict_roundtrip)
    case("to_dict_omits_komi_when_zero", test_to_dict_omits_komi_when_zero)
    case("canonical_hash_distinguishes_komi", test_canonical_hash_distinguishes_komi)
    case("complexity_increments_with_komi", test_complexity_increments_with_komi)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
