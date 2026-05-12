#!/usr/bin/env python3
"""R21 driver tests (Z3).

Z3 ships per-substrate runner + parallel launch script. These tests
exercise the runner's seed-loading logic and config-construction
without invoking PPO. The launch script is sanity-checked via
`bash -n` from the test runner.

Run as: .venv/bin/python test_r21_driver.py
"""
from __future__ import annotations

import subprocess
import sys
import traceback
from pathlib import Path

# Driver module lives in experiments/r21_driver/.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "experiments" / "r21_driver"),
)
import run_r21_substrate as driver  # noqa: E402


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
# SUBSTRATE_CONFIG sanity
# ----------------------------------------------------------------------


def test_substrate_config_has_3_entries() -> None:
    assert set(driver.SUBSTRATE_CONFIG) == {"menger", "carpet", "grid"}, (
        f"R21 substrates must be {{menger, carpet, grid}}, got "
        f"{set(driver.SUBSTRATE_CONFIG)}"
    )


def test_substrate_config_matches_plan_run_config() -> None:
    """Per R21_plan.md § Run config: menger pop=15 gens=4 budget=10000;
    carpet pop=15 gens=5 budget=15000; grid pop=15 gens=5 budget=10000."""
    expected = {
        "menger": (15, 4, 10000, "menger", 3),
        "carpet": (15, 5, 15000, "sierpinski", 2),
        "grid":   (15, 5, 10000, "grid", 2),
    }
    for label, (pop, gens, budget, topo, dims) in expected.items():
        cfg = driver.SUBSTRATE_CONFIG[label]
        assert cfg["default_population"] == pop, f"{label} pop"
        assert cfg["default_generations"] == gens, f"{label} gens"
        assert cfg["default_training_budget"] == budget, f"{label} budget"
        assert cfg["topology_type"] == topo, f"{label} topo"
        assert cfg["dims"] == dims, f"{label} dims"


# ----------------------------------------------------------------------
# Seed loading
# ----------------------------------------------------------------------


def test_load_menger_seeds_loads_all_36() -> None:
    games = driver.load_substrate_seeds("menger")
    assert len(games) == 36, f"expected 36 menger seeds, got {len(games)}"


def test_load_carpet_seeds_loads_all_6() -> None:
    games = driver.load_substrate_seeds("carpet")
    assert len(games) == 6


def test_load_grid_seeds_loads_all_4() -> None:
    games = driver.load_substrate_seeds("grid")
    assert len(games) == 4


def test_max_seeds_caps_count() -> None:
    games = driver.load_substrate_seeds("menger", max_seeds=10)
    assert len(games) == 10, (
        f"--max-seeds=10 must trim menger to 10, got {len(games)}"
    )


def test_max_seeds_no_effect_when_below_total() -> None:
    """If max_seeds >= seed_count, all seeds load."""
    games = driver.load_substrate_seeds("grid", max_seeds=100)
    assert len(games) == 4


def test_smoke_passed_filter_restricts_to_named_subset() -> None:
    """Smoke-passed list of {G1, G3} → only G1 + G3 grid seeds loaded."""
    survivors = {"r21_grid_G1_cust1_conn", "r21_grid_G3_outn2_conn"}
    games = driver.load_substrate_seeds("grid", smoke_passed=survivors)
    assert len(games) == 2
    loaded_ids = {g.game_id for g in games}
    assert loaded_ids == survivors


def test_smoke_passed_filter_empty_set_loads_zero() -> None:
    """smoke_passed=set() means nothing survived — load no seeds."""
    games = driver.load_substrate_seeds("grid", smoke_passed=set())
    assert games == []


def test_loaded_seeds_have_pie_rule_true() -> None:
    """R21 stack mandates pie_rule=True on every seed."""
    for sub in ("menger", "carpet", "grid"):
        for game in driver.load_substrate_seeds(sub):
            assert game.pie_rule is True, (
                f"{sub} seed {game.game_id} loaded with pie_rule=False"
            )


def test_loaded_seeds_have_komi_zero() -> None:
    """Seeds ship with komi_p2=0; auto-calibrated post-evolution."""
    for sub in ("menger", "carpet", "grid"):
        for game in driver.load_substrate_seeds(sub):
            assert game.komi_p2 == 0.0


def test_loaded_seeds_topology_matches_substrate() -> None:
    """Each substrate's seeds must have the correct topology_type."""
    for sub, expected_topo in (
        ("menger", "menger"),
        ("carpet", "sierpinski"),
        ("grid", "grid"),
    ):
        for game in driver.load_substrate_seeds(sub):
            assert game.topology_type == expected_topo, (
                f"{sub} seed {game.game_id} has topology {game.topology_type}, "
                f"expected {expected_topo}"
            )


# ----------------------------------------------------------------------
# Launch script syntax
# ----------------------------------------------------------------------


def test_launch_r21_sh_passes_bash_n() -> None:
    """bash -n parses the shell script without execution; catches syntax errors."""
    script = Path(__file__).resolve().parent / "experiments" / "r21_driver" / "launch_r21.sh"
    assert script.exists(), f"launch script missing: {script}"
    proc = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, (
        f"bash -n failed: stderr={proc.stderr}"
    )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("R21 driver tests (Z3)")
    print("-" * 50)
    case("substrate_config_has_3_entries", test_substrate_config_has_3_entries)
    case("substrate_config_matches_plan_run_config", test_substrate_config_matches_plan_run_config)
    case("load_menger_seeds_loads_all_36", test_load_menger_seeds_loads_all_36)
    case("load_carpet_seeds_loads_all_6", test_load_carpet_seeds_loads_all_6)
    case("load_grid_seeds_loads_all_4", test_load_grid_seeds_loads_all_4)
    case("max_seeds_caps_count", test_max_seeds_caps_count)
    case("max_seeds_no_effect_when_below_total", test_max_seeds_no_effect_when_below_total)
    case("smoke_passed_filter_restricts_to_named_subset", test_smoke_passed_filter_restricts_to_named_subset)
    case("smoke_passed_filter_empty_set_loads_zero", test_smoke_passed_filter_empty_set_loads_zero)
    case("loaded_seeds_have_pie_rule_true", test_loaded_seeds_have_pie_rule_true)
    case("loaded_seeds_have_komi_zero", test_loaded_seeds_have_komi_zero)
    case("loaded_seeds_topology_matches_substrate", test_loaded_seeds_topology_matches_substrate)
    case("launch_r21_sh_passes_bash_n", test_launch_r21_sh_passes_bash_n)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
