#!/usr/bin/env python3
"""Round-trip invariant tests for R18 fractal substrates.

R17 logged WARN-and-skipped invalid sierpinski crossovers — children with
topology_type=sierpinski but axis/dims pulled from a non-sierpinski parent.
B1 fixes this in `_fix_consistency` via `_SUBSTRATE_INVARIANTS`.

This test verifies the fix for the four invariant-bearing R18 substrates
(sierpinski, vicsek, hexaflake, menger) and exercises the 2D grid as control.
The plan's "six R18 substrates" splits sierpinski into triangle + carpet;
both share the (axis=9, dims=2) invariant in the current implementation, so
they collapse to one row here. They will diverge when the level-3 carpet and
triangle substrates land in topology.py.

Run as: .venv/bin/python test_substrate_invariants.py
"""
from __future__ import annotations

import sys
import traceback

import numpy as np

from config import EvolutionConfig
from evolution.operators_v2 import (
    CrossoverOperatorV2,
    MutationOperatorV2,
    _SUBSTRATE_INVARIANTS,
    _fix_consistency,
)
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
    except Exception as e:
        failed.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}: {e}")


def make_game(
    *,
    game_id: str,
    topology_type: str,
    axis_size: int,
    num_dimensions: int,
    capture_type: str = "surround",
    win_type: str = "territory",
) -> GameDefV2:
    """Build a minimal valid GameDefV2 with the given topology fields."""
    return GameDefV2(
        game_id=game_id,
        num_dimensions=num_dimensions,
        axis_size=axis_size,
        topology_type=topology_type,
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type=capture_type),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type=win_type, threshold=0.5, max_turns=50,
        ),
        turn_structure=TurnStructure(turn_type="alternating"),
        action_rule=ActionRule(action_types=("place",)),
    )


# Substrates under test: the four invariant-bearing fractal substrates plus
# the 2D grid control. The 2D grid has no entry in _SUBSTRATE_INVARIANTS;
# crossover/mutation operates on it freely without invariant check.
SUBSTRATES = list(_SUBSTRATE_INVARIANTS.keys())
GRID_CONTROL = ("grid", 4, 2)


def assert_substrate_invariants(game: GameDefV2, ctx: str) -> None:
    """If game.topology_type is a substrate, axis/dims must match invariants."""
    inv = _SUBSTRATE_INVARIANTS.get(game.topology_type)
    if inv is None:
        return
    expected_axis, expected_dims = inv
    if game.axis_size != expected_axis or game.num_dimensions != expected_dims:
        raise AssertionError(
            f"{ctx}: substrate {game.topology_type!r} invariant violated — "
            f"got axis={game.axis_size}, dims={game.num_dimensions}; "
            f"expected axis={expected_axis}, dims={expected_dims}"
        )


# ----------------------------------------------------------------------
# Test 1 — direct invariant fix on deliberately broken inputs
# ----------------------------------------------------------------------

def test_direct_fix() -> None:
    """For each substrate, deliberately mismatch axis/dims; _fix_consistency
    must restore them."""
    for topo, (expected_axis, expected_dims) in _SUBSTRATE_INVARIANTS.items():
        # Wrong axis, wrong dims — closest to what crossover produces.
        broken = make_game(
            game_id=f"broken_{topo}",
            topology_type=topo,
            axis_size=4,
            num_dimensions=2 if expected_dims != 2 else 3,
        )
        _fix_consistency(broken)
        assert broken.axis_size == expected_axis, (
            f"{topo}: axis_size not restored ({broken.axis_size} != {expected_axis})"
        )
        assert broken.num_dimensions == expected_dims, (
            f"{topo}: num_dimensions not restored "
            f"({broken.num_dimensions} != {expected_dims})"
        )


# ----------------------------------------------------------------------
# Test 2 — round-trip mutation
# ----------------------------------------------------------------------

def test_round_trip_mutation() -> None:
    """Repeatedly mutate each substrate; if topology_type stays on a substrate,
    invariants must hold every time."""
    config = EvolutionConfig()
    rng = np.random.default_rng(seed=42)
    mutator = MutationOperatorV2(config, rng)

    for topo, (axis, dims) in _SUBSTRATE_INVARIANTS.items():
        game = make_game(
            game_id=f"seed_{topo}",
            topology_type=topo,
            axis_size=axis,
            num_dimensions=dims,
        )
        # Mutation already calls _fix_consistency internally.
        for i in range(200):
            game = mutator.mutate_game(game)
            assert_substrate_invariants(
                game, f"mutate iter={i} from seed={topo}"
            )


# ----------------------------------------------------------------------
# Test 3 — round-trip crossover (each substrate × grid)
# ----------------------------------------------------------------------

def test_round_trip_crossover_with_grid() -> None:
    """Cross each substrate with the 2D grid control. R17's actual failure
    mode: child copies axis_size from grid parent but topology_type from the
    substrate parent."""
    config = EvolutionConfig()
    rng = np.random.default_rng(seed=43)
    crosser = CrossoverOperatorV2(config, rng)

    grid_game = make_game(
        game_id="grid_parent",
        topology_type=GRID_CONTROL[0],
        axis_size=GRID_CONTROL[1],
        num_dimensions=GRID_CONTROL[2],
    )

    for topo, (axis, dims) in _SUBSTRATE_INVARIANTS.items():
        substrate_game = make_game(
            game_id=f"{topo}_parent",
            topology_type=topo,
            axis_size=axis,
            num_dimensions=dims,
        )
        for i in range(200):
            child = crosser.crossover_games(grid_game, substrate_game)
            assert_substrate_invariants(
                child, f"crossover iter={i} grid×{topo}"
            )
            # Reverse parent order — code paths are not strictly symmetric.
            child = crosser.crossover_games(substrate_game, grid_game)
            assert_substrate_invariants(
                child, f"crossover iter={i} {topo}×grid"
            )


# ----------------------------------------------------------------------
# Test 4 — round-trip crossover between two substrates
# ----------------------------------------------------------------------

def test_round_trip_crossover_substrate_pairs() -> None:
    """Cross every distinct pair of fractal substrates. With component_swap
    or blend_topology, the child's topology_type is one parent's but axis/dims
    can come from either — invariants must still hold."""
    config = EvolutionConfig()
    rng = np.random.default_rng(seed=44)
    crosser = CrossoverOperatorV2(config, rng)

    parents = {
        topo: make_game(
            game_id=f"{topo}_parent",
            topology_type=topo,
            axis_size=axis,
            num_dimensions=dims,
        )
        for topo, (axis, dims) in _SUBSTRATE_INVARIANTS.items()
    }
    topos = list(parents.keys())
    for i, a in enumerate(topos):
        for b in topos[i + 1:]:
            for k in range(80):
                child = crosser.crossover_games(parents[a], parents[b])
                assert_substrate_invariants(
                    child, f"crossover iter={k} {a}×{b}"
                )


# ----------------------------------------------------------------------
# Entry
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== Substrate-invariant tests (B1, R18) ===\n")

    case("direct _fix_consistency restores invariants", test_direct_fix)
    case("mutation round-trip preserves invariants", test_round_trip_mutation)
    case(
        "crossover round-trip (substrate × grid) preserves invariants",
        test_round_trip_crossover_with_grid,
    )
    case(
        "crossover round-trip (substrate × substrate) preserves invariants",
        test_round_trip_crossover_substrate_pairs,
    )

    print(f"\n{len(passed)} passed, {len(failed)} failed")
    if failed:
        print("\n--- failures ---")
        for name, tb in failed:
            print(f"\n{name}:\n{tb}")
        sys.exit(1)
    sys.exit(0)
