#!/usr/bin/env python3
"""R19 seed builder — 19 seeds for the menger + carpet champion run.

Per R19_plan_v3.md "Seed design" section:

  Menger (8): 5 in-family (* + influence(r=1) + threshold-race) + 3 probes
  Carpet (8): 5 in-family (* + influence(r=2) + threshold-race) + 3 probes
  Grid    (3): R8 Connection Go + cross-substrate influence + HYBRID validator

The grid hybrid validator is the cheapest end-to-end D1 verification. After
the grid control finishes, its scoring row is expected to carry
``hybrid_action_penalty=0.2`` and never appear in any gen-2 top-10.

Run as:
    .venv/bin/python experiments/r19_seeds/build_seeds.py
    # writes 19 JSONs to experiments/r19_seeds/seeds/

Threshold floors per game_engine.operators_v2._fix_consistency:
    min_threshold = 10 * strength * (1 + radius)
  so r=1 -> 20, r=2 -> 30, r=3 -> 40 (with strength=1.0). All thresholds
  below are set to the floor so the win condition is reachable from the
  earliest possible moment in the game.

Note on custodian-1 vs custodian-2 in the plan: the engine's CaptureRule
ignores ``threshold`` for custodian capture. Both seeds are functionally
identical at construction time but carry different ``threshold`` field
values for downstream legibility.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from game_engine.topology import SUBSTRATE_INVARIANTS  # noqa: E402
from training.utils import RandomAgent, play_game  # noqa: E402


# ----------------------------------------------------------------------
# Substrate config
# ----------------------------------------------------------------------

# (label, topology_type, axis_size, num_dimensions)
SUBSTRATES: dict[str, tuple[str, int, int]] = {
    "menger": ("menger", 9, 3),
    "carpet": ("sierpinski", 9, 2),
    "grid":   ("grid", 16, 2),
}

for label, (topo, axis, dims) in SUBSTRATES.items():
    if topo in SUBSTRATE_INVARIANTS:
        expected = SUBSTRATE_INVARIANTS[topo]
        assert (axis, dims) == expected, (
            f"R19 substrate {label}/{topo} ({axis},{dims}) != invariant {expected}"
        )


# ----------------------------------------------------------------------
# Rule builders — kept small so each seed reads as data
# ----------------------------------------------------------------------

def _placement() -> PlacementRule:
    return PlacementRule(
        target="empty", constraint="anywhere", first_move_anywhere=True,
    )


def _alt_turn() -> TurnStructure:
    return TurnStructure(turn_type="alternating", pieces_per_turn=1)


def _place_only() -> ActionRule:
    return ActionRule(action_types=("place",))


def _place_and_move() -> ActionRule:
    return ActionRule(action_types=("place", "move"))


def _capture(kind: str, threshold: int = 1) -> CaptureRule:
    return CaptureRule(capture_type=kind, threshold=threshold)


def _influence(radius: int, strength: float = 1.0, decay: float = 0.5) -> PropagationRule:
    return PropagationRule(
        prop_type="influence", radius=radius, strength=strength, decay=decay,
    )


def _no_prop() -> PropagationRule:
    return PropagationRule(prop_type="none")


def _threshold_win(radius: int, strength: float = 1.0, max_turns: int = 100) -> WinCondition:
    """Threshold-race win at the floor required by _fix_consistency."""
    threshold = 10.0 * strength * (1.0 + radius)
    return WinCondition(
        condition_type="threshold",
        threshold=threshold,
        target_dimension=0,
        max_turns=max_turns,
    )


def _connection_win(max_turns: int = 100) -> WinCondition:
    return WinCondition(
        condition_type="connection",
        target_dimension=0,
        target_dimension_p2=1,
        threshold=0.5,
        max_turns=max_turns,
    )


def _territory_win(max_turns: int = 100) -> WinCondition:
    return WinCondition(
        condition_type="territory",
        threshold=0.5,
        target_dimension=0,
        max_turns=max_turns,
    )


# ----------------------------------------------------------------------
# Seed table — (combo_id, substrate, rules dict)
# ----------------------------------------------------------------------

def _menger_seeds() -> list[tuple[str, dict]]:
    """5 in-family + 3 off-family probes. All on menger axis-9 / 3D."""
    R = 1  # in-family influence radius
    return [
        # In-family: * + influence(r=1) + threshold-race
        ("m1_custodian2_inf1_threshold", dict(
            capture_rule=_capture("custodian", threshold=2),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("m2_custodian1_inf1_threshold", dict(
            capture_rule=_capture("custodian", threshold=1),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("m3_surround_inf1_threshold", dict(
            capture_rule=_capture("surround"),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("m4_outnumber2_inf1_threshold", dict(
            capture_rule=_capture("outnumber", threshold=2),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("m5_none_inf1_threshold", dict(
            capture_rule=_capture("none"),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        # Off-family probes
        ("m6_custodian2_territory", dict(
            capture_rule=_capture("custodian", threshold=2),
            propagation_rule=_no_prop(),
            win_condition=_territory_win(),
            action_rule=_place_only(),
        )),
        ("m7_surround_connection", dict(
            capture_rule=_capture("surround"),
            propagation_rule=_no_prop(),
            win_condition=_connection_win(),
            action_rule=_place_only(),
        )),
        ("m8_outnumber2_inf2_threshold", dict(
            capture_rule=_capture("outnumber", threshold=2),
            propagation_rule=_influence(2),
            win_condition=_threshold_win(2),
            action_rule=_place_only(),
        )),
    ]


def _carpet_seeds() -> list[tuple[str, dict]]:
    """5 in-family + 3 off-family probes. Carpet uses r=2 in-family
    (matches R18 winner 8776b2026957)."""
    R = 2  # in-family influence radius
    return [
        # In-family: * + influence(r=2) + threshold-race
        ("c1_outnumber2_inf2_threshold", dict(
            capture_rule=_capture("outnumber", threshold=2),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("c2_outnumber3_inf2_threshold", dict(
            capture_rule=_capture("outnumber", threshold=3),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("c3_custodian2_inf2_threshold", dict(
            capture_rule=_capture("custodian", threshold=2),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("c4_surround_inf2_threshold", dict(
            capture_rule=_capture("surround"),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        ("c5_none_inf2_threshold", dict(
            capture_rule=_capture("none"),
            propagation_rule=_influence(R),
            win_condition=_threshold_win(R),
            action_rule=_place_only(),
        )),
        # Off-family probes
        ("c6_outnumber2_territory", dict(
            capture_rule=_capture("outnumber", threshold=2),
            propagation_rule=_no_prop(),
            win_condition=_territory_win(),
            action_rule=_place_only(),
        )),
        # carpet + connection: _fix_consistency would normally demote
        # connection on small axis but axis=9 >= 3 so it survives.
        ("c7_custodian_connection", dict(
            capture_rule=_capture("custodian", threshold=1),
            propagation_rule=_no_prop(),
            win_condition=_connection_win(),
            action_rule=_place_only(),
        )),
        ("c8_outnumber2_inf3_threshold", dict(
            capture_rule=_capture("outnumber", threshold=2),
            propagation_rule=_influence(3),
            win_condition=_threshold_win(3),
            action_rule=_place_only(),
        )),
    ]


def _grid_seeds() -> list[tuple[str, dict]]:
    """3 grid control seeds incl. hybrid validator for D1."""
    return [
        ("g1_custodian1_connection", dict(
            capture_rule=_capture("custodian", threshold=1),
            propagation_rule=_no_prop(),
            win_condition=_connection_win(),
            action_rule=_place_only(),
        )),
        ("g2_outnumber2_inf1_threshold", dict(
            capture_rule=_capture("outnumber", threshold=2),
            propagation_rule=_influence(1),
            win_condition=_threshold_win(1),
            action_rule=_place_only(),
        )),
        # HYBRID validator: place+move with custodian + connection.
        # Should construct cleanly (capture != none satisfies the
        # move-only fix_consistency check) but score with
        # hybrid_action_penalty=0.2 in metrics/scoring.py.
        ("g3_hybrid_validator", dict(
            capture_rule=_capture("custodian", threshold=1),
            propagation_rule=_no_prop(),
            win_condition=_connection_win(),
            action_rule=_place_and_move(),
        )),
    ]


SEED_TABLE: list[tuple[str, str, dict]] = (
    [(combo, "menger", rules) for combo, rules in _menger_seeds()]
    + [(combo, "carpet", rules) for combo, rules in _carpet_seeds()]
    + [(combo, "grid", rules) for combo, rules in _grid_seeds()]
)


# ----------------------------------------------------------------------
# Build + validate
# ----------------------------------------------------------------------

def build_seed(combo_id: str, substrate_label: str, rules: dict) -> GameDefV2:
    topo, axis, dims = SUBSTRATES[substrate_label]
    return GameDefV2(
        game_id=f"{combo_id}__{substrate_label}",
        num_dimensions=dims,
        axis_size=axis,
        topology_type=topo,
        placement_rule=_placement(),
        turn_structure=_alt_turn(),
        **rules,
        metadata={
            "source": "R19 seed",
            "combo": combo_id,
            "substrate": substrate_label,
        },
    )


def validate_seed(game: GameDefV2, max_steps: int = 50) -> tuple[int, int | None]:
    """Build engine and run a 50-step random rollout."""
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
    print(f"\nBuilding {len(SEED_TABLE)} R19 seeds → {out_dir}\n")

    for combo_id, substrate_label, rules in SEED_TABLE:
        game = build_seed(combo_id, substrate_label, rules)
        try:
            length, winner = validate_seed(game)
        except Exception as e:
            failures.append((game.game_id, repr(e)))
            print(f"  FAIL  {game.game_id}: {e}")
            continue

        out_path = out_dir / f"{game.game_id}.json"
        with open(out_path, "w") as f:
            json.dump(game.to_dict(), f, indent=2)
        print(
            f"  OK    {game.game_id:55s}  rollout_len={length:>3} "
            f"winner={winner}"
        )

    print(f"\n=== {len(SEED_TABLE) - len(failures)} seeds OK, "
          f"{len(failures)} failed ===")
    if failures:
        print("\nFailures:")
        for gid, msg in failures:
            print(f"  {gid}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
