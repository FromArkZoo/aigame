#!/usr/bin/env python3
"""R20 seed builder — 12 seeds for the rule-family-comparator round.

Per R20_plan.md § Seed pool design:

  4 rule families × 3 substrates = 12 seeds pre-smoke

  Families (held constant across substrates; all use the connection win
  condition that's load-bearing for the R8-family hypothesis):
    F1  custodian-1 + connection            (R8 exact)
    F2  custodian-2 + connection            (heavier capture × R8 win)
    F3  surround + connection               (tests team-3 depth hypothesis)
    F4  outnumber-2 + connection            (R19's strongest capture × R8 win)

  Substrates:
    menger        (axis 9, 3D, dim 2.727 — R19 strongest validated)
    carpet        (axis 9, 2D, dim 1.893 — tests connection on score-neutral 2D)
    grid_control  (axis 16, 2D — R8's native; G1 success criterion)

  All seeds: pie_rule=True (R19 30/30 verdicts unanimous), place-only
  (D1 hybrid penalty), threshold defaults from _fix_consistency floors.

Run:
    .venv/bin/python experiments/r20_seeds/build_seeds.py

Writes 12 JSONs to experiments/r20_seeds/seeds/. Each seed is validated
with a 50-step random rollout before being written; failures are listed
at end and exit code is non-zero.

Naming: <family_id>_<rule_summary>__<substrate>.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evolution.operators_v2 import _SUBSTRATE_INVARIANTS as SUBSTRATE_INVARIANTS  # noqa: E402
from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.rules import (  # noqa: E402
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)
from training.utils import RandomAgent, play_game  # noqa: E402


# ----------------------------------------------------------------------
# Substrate config (label -> topology_type, axis, dims)
# ----------------------------------------------------------------------

SUBSTRATES: dict[str, tuple[str, int, int]] = {
    "menger":       ("menger",     9,  3),
    "carpet":       ("sierpinski", 9,  2),
    "grid_control": ("grid",       16, 2),
}

for label, (topo, axis, dims) in SUBSTRATES.items():
    if topo in SUBSTRATE_INVARIANTS:
        expected = SUBSTRATE_INVARIANTS[topo]
        assert (axis, dims) == expected, (
            f"R20 substrate {label}/{topo} ({axis},{dims}) != invariant {expected}"
        )


# ----------------------------------------------------------------------
# Rule builders
# ----------------------------------------------------------------------

def _placement() -> PlacementRule:
    return PlacementRule(
        target="empty", constraint="anywhere", first_move_anywhere=True,
    )


def _alt_turn() -> TurnStructure:
    return TurnStructure(turn_type="alternating", pieces_per_turn=1)


def _place_only() -> ActionRule:
    return ActionRule(action_types=("place",))


def _capture(kind: str, threshold: int = 1) -> CaptureRule:
    return CaptureRule(capture_type=kind, threshold=threshold)


def _no_prop() -> PropagationRule:
    return PropagationRule(prop_type="none")


def _connection_win(num_dims: int, max_turns: int = 100) -> WinCondition:
    """Connection win along dim 0 for P1, dim 1 for P2 (engine default).

    On 3D substrates (menger), target_dimension_p2 wraps via
    `(target_dimension + 1) % num_dimensions` in engine_v2._check_connection.
    Explicit wiring here keeps the seed self-documenting.
    """
    p2_dim = 1 if num_dims >= 2 else 0
    return WinCondition(
        condition_type="connection",
        target_dimension=0,
        target_dimension_p2=p2_dim,
        threshold=0.5,
        max_turns=max_turns,
    )


# ----------------------------------------------------------------------
# Rule families (all share connection win + place-only + pie_rule=True)
# ----------------------------------------------------------------------

# (family_id, descriptive_short_id, capture_rule_factory)
FAMILIES: list[tuple[str, str, callable]] = [
    ("F1", "custodian1_conn", lambda: _capture("custodian", threshold=1)),
    ("F2", "custodian2_conn", lambda: _capture("custodian", threshold=2)),
    ("F3", "surround_conn",   lambda: _capture("surround")),
    ("F4", "outnumber2_conn", lambda: _capture("outnumber", threshold=2)),
]


# ----------------------------------------------------------------------
# Seed table
# ----------------------------------------------------------------------

SEED_TABLE: list[tuple[str, str, str, callable]] = [
    (family_id, short_id, substrate_label, capture_factory)
    for family_id, short_id, capture_factory in FAMILIES
    for substrate_label in SUBSTRATES
]


def build_seed(
    family_id: str,
    short_id: str,
    substrate_label: str,
    capture_factory: callable,
) -> GameDefV2:
    topo, axis, dims = SUBSTRATES[substrate_label]
    game_id = f"{family_id}_{short_id}__{substrate_label}"
    return GameDefV2(
        game_id=game_id,
        num_dimensions=dims,
        axis_size=axis,
        topology_type=topo,
        placement_rule=_placement(),
        capture_rule=capture_factory(),
        propagation_rule=_no_prop(),
        win_condition=_connection_win(num_dims=dims),
        turn_structure=_alt_turn(),
        action_rule=_place_only(),
        pie_rule=True,
        metadata={
            "source": "R20 seed",
            "family": family_id,
            "rule_summary": short_id,
            "substrate": substrate_label,
        },
    )


def validate_seed(game: GameDefV2, max_steps: int = 50) -> tuple[int, int | None]:
    """Build engine + 50-step random rollout. Confirms construction is
    valid and the engine can drive the game to a terminal or step-limit."""
    engine = create_engine(game)
    a0 = RandomAgent(seed=1)
    a1 = RandomAgent(seed=2)
    winner, length, _ = play_game(
        engine, a0, a1, deterministic=False, max_steps=max_steps,
    )
    return length, winner


def main() -> int:
    out_dir = Path(__file__).parent / "seeds"
    out_dir.mkdir(parents=True, exist_ok=True)

    failures: list[tuple[str, str]] = []
    print(f"\nBuilding {len(SEED_TABLE)} R20 seeds → {out_dir}\n")

    for family_id, short_id, substrate_label, capture_factory in SEED_TABLE:
        game = build_seed(family_id, short_id, substrate_label, capture_factory)
        try:
            length, winner = validate_seed(game)
        except Exception as e:  # noqa: BLE001
            failures.append((game.game_id, repr(e)))
            print(f"  FAIL  {game.game_id}: {e}")
            continue

        # Sanity: pie_rule must be True in serialized form (catches a
        # silent regression in to_dict).
        d = game.to_dict()
        assert d.get("pie_rule") is True, (
            f"{game.game_id}: pie_rule missing from to_dict output"
        )
        # And num_actions must include the swap action.
        expected_swap_idx = game.num_actions - 1
        assert game.swap_action_idx == expected_swap_idx, (
            f"{game.game_id}: swap_action_idx {game.swap_action_idx} != "
            f"expected {expected_swap_idx}"
        )

        out_path = out_dir / f"{game.game_id}.json"
        with open(out_path, "w") as f:
            json.dump(d, f, indent=2)
        print(
            f"  OK    {game.game_id:42s}  rollout_len={length:>3} "
            f"winner={winner}  swap_idx={game.swap_action_idx}"
        )

    print(
        f"\n=== {len(SEED_TABLE) - len(failures)} seeds OK, "
        f"{len(failures)} failed ==="
    )
    if failures:
        print("\nFailures:")
        for gid, msg in failures:
            print(f"  {gid}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
