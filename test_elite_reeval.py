#!/usr/bin/env python3
"""Elite re-evaluation tests (R21 S5).

S5's root-cause fix for the R20+R20.5 confirmed ~+0.11 upward bias in
production GE. The bug: R18's `deterministic_run_seed(game_id, run_idx)`
uses the same seed every generation, so once a game gets a lucky PPO
seed at its first scoring, it keeps that lucky score forever as an
elite carry-over. Selection filters in survivors; the leaderboard
inflates.

The fix is a seed-swap in run.py: carry-over elites (game whose
`metadata['generation']` is less than the current scoring gen) use
`carryover_run_seed(game_id, gen, run_idx)` instead — gen-dependent so
each re-eval is a fresh sample. Pure replace; variance handled by S6.

These tests poke the seed functions and the carry-over predicate
directly. The full integration runs PPO and is exercised at launch.

Run as: .venv/bin/python test_elite_reeval.py
"""
from __future__ import annotations

import sys
import traceback

from run import carryover_run_seed, deterministic_run_seed


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


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_deterministic_seed_is_gen_independent() -> None:
    """R18 regression: deterministic_run_seed must NOT depend on generation.

    A new mutant/crossover/immigrant scored once at its birth gen should
    get the same seed forever if it survives (under R18 framing; under
    R21 S5 the carry-over path takes over instead). The function itself
    must remain gen-independent.
    """
    s_idx0 = deterministic_run_seed("game_abc", run_idx=0)
    # The same call must give the same answer no matter when invoked.
    assert deterministic_run_seed("game_abc", run_idx=0) == s_idx0
    # Different run_idx must give a different seed (C2 multi-seed needs this).
    s_idx1 = deterministic_run_seed("game_abc", run_idx=1)
    assert s_idx1 != s_idx0, (
        f"run_idx=0 and run_idx=1 must differ: {s_idx0} vs {s_idx1}"
    )


def test_carryover_seed_is_gen_dependent() -> None:
    """The R21 S5 fix: different generations must produce different seeds
    for the same (game_id, run_idx) pair. Two consecutive gens must
    differ — otherwise the bias-removal property does not hold."""
    s_gen3 = carryover_run_seed("game_abc", generation=3, run_idx=0)
    s_gen4 = carryover_run_seed("game_abc", generation=4, run_idx=0)
    s_gen5 = carryover_run_seed("game_abc", generation=5, run_idx=0)
    assert s_gen3 != s_gen4, "consecutive gens must give different seeds"
    assert s_gen4 != s_gen5, "consecutive gens must give different seeds"
    assert s_gen3 != s_gen5, "non-adjacent gens must give different seeds"


def test_carryover_seed_is_deterministic() -> None:
    """Same (game_id, gen, run_idx) → same seed. Cross-process
    determinism: MD5-based, never depends on Python's hash randomization."""
    s_a = carryover_run_seed("game_xyz", generation=7, run_idx=2)
    s_b = carryover_run_seed("game_xyz", generation=7, run_idx=2)
    assert s_a == s_b, f"same args must give same seed: {s_a} vs {s_b}"


def test_carryover_seed_varies_across_run_idx() -> None:
    """C2 multi-seed averaging: per-game extras seeds must differ."""
    seeds = {
        carryover_run_seed("game_xyz", generation=7, run_idx=i)
        for i in range(3)
    }
    assert len(seeds) == 3, (
        f"run_idx 0/1/2 must give 3 distinct seeds, got {seeds}"
    )


def test_carryover_seed_varies_across_games() -> None:
    """No collision across games (R20 byte-identical trio used 3
    distinct game_ids; their seeds must also differ to give 3 honest
    PPO samples)."""
    seeds = {
        carryover_run_seed(gid, generation=4, run_idx=0)
        for gid in ("a6385db22c0b", "b160b1f55378", "d1dbc6568fc7")
    }
    assert len(seeds) == 3, (
        f"3 distinct game_ids must give 3 distinct seeds, got {seeds}"
    )


def test_deterministic_and_carryover_diverge_after_gen_zero() -> None:
    """Sanity: the two seed schemes give different answers as soon as
    generation > 0. At any positive generation, the carry-over path must
    not collide with the new-game path (otherwise the fix is a no-op)."""
    new_seed = deterministic_run_seed("game_abc", run_idx=0)
    for gen in (1, 2, 5, 10):
        co_seed = carryover_run_seed("game_abc", generation=gen, run_idx=0)
        assert co_seed != new_seed, (
            f"carry-over seed at gen={gen} collided with deterministic seed: {co_seed}"
        )


def test_carryover_detection_predicate() -> None:
    """Inline copy of the run.py detection predicate, exercised on
    representative metadata layouts: seed game (gen 0), mutant/crossover
    child (gen N), and carry-over elite (gen N when current is M>N)."""
    def is_carryover(metadata: dict, current_gen: int) -> bool:
        born_gen = metadata.get("generation", current_gen)
        return born_gen < current_gen

    # Gen-0 scoring: nothing is a carry-over.
    assert not is_carryover({"generation": 0}, current_gen=0)
    # Gen-1 scoring: gen-0 elites are carry-overs; gen-1 children are not.
    assert is_carryover({"generation": 0}, current_gen=1)
    assert not is_carryover({"generation": 1}, current_gen=1)
    # Gen-5: a gen-3 elite that survived twice is still a carry-over.
    assert is_carryover({"generation": 3}, current_gen=5)
    # Missing metadata.generation → defaults to current_gen → NOT carry-over
    # (conservative: don't penalise unknown-lineage games with a seed-swap).
    assert not is_carryover({}, current_gen=5)


def test_run_idx_0_and_extras_seeds_all_change_across_gens() -> None:
    """C2 averages num_independent_runs PPO trainings (run.py uses 3 by
    default). For the bias fix to work across the whole bundle, all
    three run_idx slots must vary by gen — not just the primary seed."""
    for run_idx in (0, 1, 2):
        s_gen3 = carryover_run_seed("game_abc", generation=3, run_idx=run_idx)
        s_gen4 = carryover_run_seed("game_abc", generation=4, run_idx=run_idx)
        assert s_gen3 != s_gen4, (
            f"run_idx={run_idx} must give different seeds at gen 3 vs gen 4"
        )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Elite re-evaluation tests (R21 S5)")
    print("-" * 50)
    case("deterministic_seed_is_gen_independent", test_deterministic_seed_is_gen_independent)
    case("carryover_seed_is_gen_dependent", test_carryover_seed_is_gen_dependent)
    case("carryover_seed_is_deterministic", test_carryover_seed_is_deterministic)
    case("carryover_seed_varies_across_run_idx", test_carryover_seed_varies_across_run_idx)
    case("carryover_seed_varies_across_games", test_carryover_seed_varies_across_games)
    case("deterministic_and_carryover_diverge_after_gen_zero", test_deterministic_and_carryover_diverge_after_gen_zero)
    case("carryover_detection_predicate", test_carryover_detection_predicate)
    case("run_idx_0_and_extras_seeds_all_change_across_gens", test_run_idx_0_and_extras_seeds_all_change_across_gens)
    print("-" * 50)
    print(f"{len(passed)} passed, {len(failed)} failed")
    if failed:
        for name, tb in failed:
            print(f"\n--- {name} ---\n{tb}")
        sys.exit(1)
