#!/usr/bin/env python3
"""R21 seed-builder tests (Z2).

Z2 builds 46 pre-smoke seeds across 3 substrates per R21_plan.md
§ Seed pool design. These tests exercise the seed-construction logic —
counts, family invariants, canonical-blob uniqueness — without running
the smoke filter (which is deferred to pre-launch compute).

Run as: .venv/bin/python test_r21_seeds.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

# build_seeds lives in experiments/r21_seeds/.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "experiments" / "r21_seeds"),
)
from build_seeds import (  # noqa: E402
    MENGER_DECAYS,
    MENGER_MAX_TURNS,
    MENGER_THRESHOLDS,
    CARPET_DECAYS,
    CARPET_THRESHOLDS,
    all_seeds,
    build_carpet_seeds,
    build_grid_seeds,
    build_menger_seeds,
)


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


# ----------------------------------------------------------------------
# Menger pool
# ----------------------------------------------------------------------


def test_menger_count_is_full_cartesian() -> None:
    """4 thresholds × 3 decays × 3 max_turns = 36 seeds (per plan)."""
    seeds = build_menger_seeds()
    expected = len(MENGER_THRESHOLDS) * len(MENGER_DECAYS) * len(MENGER_MAX_TURNS)
    assert len(seeds) == expected == 36, (
        f"expected 36 menger seeds, got {len(seeds)} (cartesian product = {expected})"
    )


def test_menger_family_is_locked() -> None:
    """All menger seeds must share the locked family:
    outnumber-2 + influence(r=1) + threshold-race + pie + place-only +
    menger axis-9 3D."""
    for s in build_menger_seeds():
        assert s.capture_rule.capture_type == "outnumber"
        assert s.capture_rule.threshold == 2
        assert s.propagation_rule.prop_type == "influence"
        assert s.propagation_rule.radius == 1
        assert s.win_condition.condition_type == "threshold"
        assert s.pie_rule is True
        assert s.action_rule.action_types == ("place",)
        assert s.topology_type == "menger"
        assert s.num_dimensions == 3
        assert s.axis_size == 9


def test_menger_sweep_covers_each_parameter() -> None:
    """The 36 seeds must hit every (threshold, decay, max_turns) value
    in the cartesian product exactly once."""
    seeds = build_menger_seeds()
    triples = sorted(
        (s.win_condition.threshold, s.propagation_rule.decay, s.win_condition.max_turns)
        for s in seeds
    )
    expected_triples = sorted(
        (t, d, m)
        for t in MENGER_THRESHOLDS
        for d in MENGER_DECAYS
        for m in MENGER_MAX_TURNS
    )
    assert triples == expected_triples, (
        f"sweep missing parameter combos. got {triples[:3]}..., expected {expected_triples[:3]}..."
    )


# ----------------------------------------------------------------------
# Carpet pool
# ----------------------------------------------------------------------


def test_carpet_count_is_six_siblings() -> None:
    """3 thresholds × 2 decays = 6 siblings (per plan).
    The R20 anchor 625bfc1f3f49 is loaded via --seed-db at launch, not here."""
    seeds = build_carpet_seeds()
    expected = len(CARPET_THRESHOLDS) * len(CARPET_DECAYS)
    assert len(seeds) == expected == 6, (
        f"expected 6 carpet seeds, got {len(seeds)}"
    )


def test_carpet_family_is_outnumber2_influence2() -> None:
    """Family: outnumber-2 + influence(r=2) + threshold-race + pie."""
    for s in build_carpet_seeds():
        assert s.capture_rule.capture_type == "outnumber"
        assert s.capture_rule.threshold == 2
        assert s.propagation_rule.prop_type == "influence"
        assert s.propagation_rule.radius == 2, (
            f"carpet must use r=2 influence per plan, got r={s.propagation_rule.radius}"
        )
        assert s.win_condition.condition_type == "threshold"
        assert s.pie_rule is True
        assert s.topology_type == "sierpinski"


# ----------------------------------------------------------------------
# Grid pool
# ----------------------------------------------------------------------


def test_grid_count_is_four_families() -> None:
    """4 families: G1/G2/G3/G4."""
    seeds = build_grid_seeds()
    assert len(seeds) == 4, f"expected 4 grid family seeds, got {len(seeds)}"
    families = {s.metadata["family"] for s in seeds}
    assert families == {"G1", "G2", "G3", "G4"}, (
        f"grid family ids must be {{G1,G2,G3,G4}}, got {families}"
    )


def test_grid_g1_g2_g3_use_connection_win() -> None:
    """G1/G2/G3 are the R8-revival v2 candidates — all connection-win."""
    grid = {s.metadata["family"]: s for s in build_grid_seeds()}
    for f in ("G1", "G2", "G3"):
        s = grid[f]
        assert s.win_condition.condition_type == "connection", (
            f"{f} expected connection-win, got {s.win_condition.condition_type}"
        )


def test_grid_g4_uses_threshold_race() -> None:
    """G4 is the head-to-head anchor — threshold-race (R20 grid winner style)."""
    grid = {s.metadata["family"]: s for s in build_grid_seeds()}
    g4 = grid["G4"]
    assert g4.win_condition.condition_type == "threshold"
    assert g4.capture_rule.capture_type == "custodian"
    assert g4.capture_rule.threshold == 1
    # R20 fcedbc14043d-style — uses influence propagation, not none.
    assert g4.propagation_rule.prop_type == "influence"


def test_grid_capture_combinations() -> None:
    """G1: custodian-1, G2: custodian-2, G3: outnumber-2, G4: custodian-1."""
    grid = {s.metadata["family"]: s for s in build_grid_seeds()}
    assert (grid["G1"].capture_rule.capture_type, grid["G1"].capture_rule.threshold) == ("custodian", 1)
    assert (grid["G2"].capture_rule.capture_type, grid["G2"].capture_rule.threshold) == ("custodian", 2)
    assert (grid["G3"].capture_rule.capture_type, grid["G3"].capture_rule.threshold) == ("outnumber", 2)
    assert (grid["G4"].capture_rule.capture_type, grid["G4"].capture_rule.threshold) == ("custodian", 1)


# ----------------------------------------------------------------------
# Cross-pool invariants
# ----------------------------------------------------------------------


def test_total_seed_count() -> None:
    """Plan target: 36 menger + 6 carpet + 4 grid = 46."""
    assert len(all_seeds()) == 46, f"expected 46 total seeds, got {len(all_seeds())}"


def test_every_seed_has_pie_rule() -> None:
    """Post-ac9e642 stack: every R21 seed ships with pie_rule=True."""
    for s in all_seeds():
        assert s.pie_rule is True, (
            f"{s.game_id} ships without pie_rule — R21 stack requires it"
        )


def test_every_seed_has_komi_zero_default() -> None:
    """S4 sets komi_p2 auto-calibration post-evolution. Seeds start at 0.0."""
    for s in all_seeds():
        assert s.komi_p2 == 0.0, (
            f"{s.game_id} ships with non-zero komi_p2={s.komi_p2} — should be auto-calibrated, not seeded"
        )


def test_every_seed_is_place_only() -> None:
    """D1 hybrid-action ban — every seed is place-only (no move actions)."""
    for s in all_seeds():
        assert s.action_rule.action_types == ("place",), (
            f"{s.game_id} has hybrid action_types {s.action_rule.action_types}"
        )


def test_no_internal_canonical_duplicates() -> None:
    """S1a regression: no two seeds in the pool share a canonical_hash.
    If they did, the dedup logic would silently drop one before scoring."""
    hashes: dict[str, str] = {}
    for s in all_seeds():
        h = s.canonical_hash()
        if h in hashes:
            raise AssertionError(
                f"canonical-hash collision: {s.game_id} ≡ {hashes[h]} "
                f"(both have the same rule kernel)"
            )
        hashes[h] = s.game_id


def test_seeds_serialise_round_trip() -> None:
    """Every seed must to_dict / from_dict cleanly (the driver consumes
    the JSON form). Smoke-check a sample of one per pool."""
    from game_engine.game_def_v2 import GameDefV2
    for s in (
        build_menger_seeds()[0],
        build_carpet_seeds()[0],
        build_grid_seeds()[0],
    ):
        d = s.to_dict()
        restored = GameDefV2.from_dict(d)
        # Compare via canonical_hash since to_dict drops the cached topology.
        assert s.canonical_hash() == restored.canonical_hash(), (
            f"{s.game_id} canonical hash changed after to_dict/from_dict"
        )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("R21 seed-builder tests (Z2)")
    print("-" * 50)
    case("menger_count_is_full_cartesian", test_menger_count_is_full_cartesian)
    case("menger_family_is_locked", test_menger_family_is_locked)
    case("menger_sweep_covers_each_parameter", test_menger_sweep_covers_each_parameter)
    case("carpet_count_is_six_siblings", test_carpet_count_is_six_siblings)
    case("carpet_family_is_outnumber2_influence2", test_carpet_family_is_outnumber2_influence2)
    case("grid_count_is_four_families", test_grid_count_is_four_families)
    case("grid_g1_g2_g3_use_connection_win", test_grid_g1_g2_g3_use_connection_win)
    case("grid_g4_uses_threshold_race", test_grid_g4_uses_threshold_race)
    case("grid_capture_combinations", test_grid_capture_combinations)
    case("total_seed_count", test_total_seed_count)
    case("every_seed_has_pie_rule", test_every_seed_has_pie_rule)
    case("every_seed_has_komi_zero_default", test_every_seed_has_komi_zero_default)
    case("every_seed_is_place_only", test_every_seed_is_place_only)
    case("no_internal_canonical_duplicates", test_no_internal_canonical_duplicates)
    case("seeds_serialise_round_trip", test_seeds_serialise_round_trip)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
