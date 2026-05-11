#!/usr/bin/env python3
"""Canonical-blob dedup tests (R21 blocker S1a).

Canonical-form spec (per R21_plan.md § S1a):
  - (a) sort rule list by (rule_type, parameter_tuple_lex_order)
  - (b) round all float parameters to 6 decimals
  - (c) emit JSON with sort_keys=True
  - (d) include: capture rule, win condition, topology, axis_size, max_turns,
        propagation_decay, pie_rule, komi_p2 (post-S4)
  - (e) exclude: game_id, parent_ids, generation, score_history, ELO, metadata

Run as: .venv/bin/python test_canonical_blob.py
"""
from __future__ import annotations

import sys
import traceback

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
    game_id: str = "abc123",
    threshold: float = 57.97,
    propagation_decay: float = 0.7,
    capture_type: str = "outnumber",
    capture_threshold: int = 2,
    pie_rule: bool = True,
    metadata: dict | None = None,
    axis_size: int = 9,
    max_turns: int = 100,
) -> GameDefV2:
    return GameDefV2(
        game_id=game_id,
        num_dimensions=2,
        axis_size=axis_size,
        topology_type="grid",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(
            capture_type=capture_type,
            threshold=capture_threshold,
        ),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=1, decay=propagation_decay,
        ),
        win_condition=WinCondition(
            condition_type="threshold",
            threshold=threshold,
            max_turns=max_turns,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
        pie_rule=pie_rule,
        metadata=metadata if metadata is not None else {},
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_identity_same_hash() -> None:
    """Two identical games produce identical canonical_hash."""
    a = make_game(game_id="alpha")
    b = make_game(game_id="alpha")
    assert a.canonical_hash() == b.canonical_hash(), (
        "identical games must share canonical_hash"
    )


def test_game_id_excluded() -> None:
    """game_id is ephemeral and must not affect canonical_hash."""
    a = make_game(game_id="aaaaaaaaaaaa")
    b = make_game(game_id="ffffffffffff")
    assert a.canonical_hash() == b.canonical_hash(), (
        f"different game_ids must not change hash: {a.canonical_hash()} vs {b.canonical_hash()}"
    )


def test_metadata_excluded() -> None:
    """metadata (lineage, generation, etc.) must not affect canonical_hash."""
    a = make_game(metadata={})
    b = make_game(metadata={
        "generation": 5,
        "parent_ids": ["xxx", "yyy"],
        "score_history": [0.1, 0.2, 0.3],
    })
    assert a.canonical_hash() == b.canonical_hash(), (
        "metadata diffs must not change canonical_hash"
    )


def test_float_drift_collapses() -> None:
    """Float drift of ±1e-7 collapses (rounded to 6 decimals)."""
    a = make_game(threshold=57.97, propagation_decay=0.7)
    b = make_game(threshold=57.97 + 1e-9, propagation_decay=0.7 - 1e-9)
    assert a.canonical_hash() == b.canonical_hash(), (
        f"±1e-9 float drift must collapse at 6-decimal rounding: "
        f"{a.canonical_hash()} vs {b.canonical_hash()}"
    )


def test_float_distinction_preserved() -> None:
    """Differences above the 6-decimal threshold remain distinct."""
    a = make_game(threshold=57.97)
    b = make_game(threshold=57.99)
    assert a.canonical_hash() != b.canonical_hash(), (
        "thresholds 57.97 vs 57.99 must remain distinct under 6-decimal rounding"
    )


def test_pie_rule_affects_hash() -> None:
    """pie_rule is a kernel-level field — toggling it changes the hash."""
    a = make_game(pie_rule=True)
    b = make_game(pie_rule=False)
    assert a.canonical_hash() != b.canonical_hash(), (
        "pie_rule on/off must produce distinct canonical_hashes"
    )


def test_holes_order_invariant() -> None:
    """The holes list is semantically a set — reorderings yield the same hash."""
    a = make_game()
    b = make_game()
    a.holes = [3, 1, 7, 5]
    b.holes = [5, 7, 1, 3]
    assert a.canonical_hash() == b.canonical_hash(), (
        "holes list ordering must not affect canonical_hash"
    )


def test_different_holes_distinguished() -> None:
    """Different hole sets must produce different hashes."""
    a = make_game()
    b = make_game()
    a.holes = [1, 2, 3]
    b.holes = [1, 2, 4]
    assert a.canonical_hash() != b.canonical_hash(), (
        "hole-set membership change must alter canonical_hash"
    )


def test_kernel_param_changes_hash() -> None:
    """Capture-rule threshold differences alter the hash."""
    a = make_game(capture_threshold=2)
    b = make_game(capture_threshold=3)
    assert a.canonical_hash() != b.canonical_hash(), (
        "capture-rule threshold (2 vs 3) must alter canonical_hash"
    )


def test_blob_is_bytes_hash_is_hex() -> None:
    """API: canonical_blob() returns bytes; canonical_hash() returns 64-char hex."""
    g = make_game()
    blob = g.canonical_blob()
    h = g.canonical_hash()
    assert isinstance(blob, bytes), f"canonical_blob must return bytes, got {type(blob)}"
    assert isinstance(h, str) and len(h) == 64, (
        f"canonical_hash must return 64-char hex string, got {h!r}"
    )
    # Determinism: calling twice must yield the same blob/hash.
    assert blob == g.canonical_blob()
    assert h == g.canonical_hash()


def test_r20_byte_identical_positive_control() -> None:
    """Positive control: two games hand-crafted to match R20's byte-identical trio
    (a6385db / b160b1 / d1dbc6 — same outnumber-2 + influence(r=1) + threshold-race
    kernel, distinct game_ids) must share canonical_hash."""
    kernel = dict(
        threshold=57.97, propagation_decay=1.0,
        capture_type="outnumber", capture_threshold=2,
        pie_rule=False, max_turns=100,
    )
    a = make_game(game_id="a6385db22c0b", metadata={"generation": 3}, **kernel)
    b = make_game(game_id="b160b1f55378", metadata={"generation": 6}, **kernel)
    c = make_game(game_id="d1dbc6568fc7", metadata={"generation": 6}, **kernel)
    h_a, h_b, h_c = a.canonical_hash(), b.canonical_hash(), c.canonical_hash()
    assert h_a == h_b == h_c, (
        f"R20 byte-identical-trio analog must canonical-hash equal: "
        f"{h_a} / {h_b} / {h_c}"
    )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Canonical-blob dedup tests (R21 S1a)")
    print("-" * 50)
    case("identity_same_hash", test_identity_same_hash)
    case("game_id_excluded", test_game_id_excluded)
    case("metadata_excluded", test_metadata_excluded)
    case("float_drift_collapses", test_float_drift_collapses)
    case("float_distinction_preserved", test_float_distinction_preserved)
    case("pie_rule_affects_hash", test_pie_rule_affects_hash)
    case("holes_order_invariant", test_holes_order_invariant)
    case("different_holes_distinguished", test_different_holes_distinguished)
    case("kernel_param_changes_hash", test_kernel_param_changes_hash)
    case("blob_is_bytes_hash_is_hex", test_blob_is_bytes_hash_is_hex)
    case("r20_byte_identical_positive_control", test_r20_byte_identical_positive_control)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
