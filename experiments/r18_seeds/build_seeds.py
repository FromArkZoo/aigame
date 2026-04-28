#!/usr/bin/env python3
"""B3 — generate the 15 R18 seed games (3 rule combos × 5 substrates).

R18 is a substrate comparator: each substrate runs its own per-substrate
evolution, seeded from the same 3 rule combos so cross-substrate
comparison is apples-to-apples on the rule-family axis. Plan A locked
2026-04-28: 5 substrates (hexaflake dropped).

Combos:
  c1 — custodian + connection-win
       Classic capture-and-connect. P1 connects axis-0; P2 connects
       axis-1. No propagation. Distinct from c2/c3 by win condition.

  c2 — outnumber-2 + threshold-race + radius-1 influence
       Influence-driven race: each stone radiates strength to neighbors
       within radius 1; P1 or P2 wins when their accumulated board value
       crosses a threshold first. Outnumber-2 is the capture trigger.
       This is the natural pairing for influence — _fix_consistency
       requires propagation=influence iff win=threshold.

  c3 — surround + territory
       Encoded as the post-_fix_consistency form. The plan called for
       "radius-1 signed influence + territory," but _fix_consistency
       demotes influence on non-threshold wins (vestigial, no consumer).
       Encoding the demoted form keeps the seed honest about what the
       engine will actually run. Capture is surround so territory has
       captures to score.

Substrates (Plan A, 5 rows):
  vicsek                axis=27 dims=2  active=125  dim 1.465
  sierpinski_triangle   axis=32 dims=2  active=243  dim 1.585
  sierpinski (carpet)   axis=9  dims=2  active=64   dim 1.893
  grid                  axis=16 dims=2  active=256  dim 2.0   (control)
  menger                axis=9  dims=3  active=400  dim 2.727

Caveat — sierpinski + threshold-race (c2 on carpet substrate):
  _fix_consistency demotes (sierpinski, threshold) -> (sierpinski,
  connection) per R17 sierpinski_threshold_inert audit rule. Seed JSON
  encodes the threshold-race intent — the engine runs it at load time
  WITHOUT _fix_consistency, so the seed game itself is fine. But if the
  evolution mutates the seed and re-applies _fix_consistency, threshold
  will demote to connection unless run.py runs that substrate with
  --audit-soft-rules. The R18 sierpinski sub-evolution should set
  audit_soft_rules=True so the threshold-race combo can train.

Run as:
    python experiments/r18_seeds/build_seeds.py
    # writes 15 JSONs to experiments/r18_seeds/seeds/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make repo importable when run directly.
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
# Substrate set (Plan A)
# ----------------------------------------------------------------------

# Each entry: (label, topology_type, axis_size, num_dimensions)
# label is what shows up in filenames; topology_type is the engine string.
SUBSTRATES: list[tuple[str, str, int, int]] = [
    ("vicsek",     "vicsek",              27, 2),
    ("triangle",   "sierpinski_triangle", 32, 2),
    ("carpet",     "sierpinski",          9,  2),
    ("grid",       "grid",                16, 2),
    ("menger",     "menger",              9,  3),
]

# Sanity: the 4 fractal substrates must match SUBSTRATE_INVARIANTS exactly.
for label, topo, axis, dims in SUBSTRATES:
    if topo in SUBSTRATE_INVARIANTS:
        expected = SUBSTRATE_INVARIANTS[topo]
        assert (axis, dims) == expected, (
            f"seed substrate {label}/{topo} ({axis},{dims}) != invariant {expected}"
        )


# ----------------------------------------------------------------------
# Rule-combo factories — one per combo, takes substrate dims as input
# ----------------------------------------------------------------------

def _connection_dims(num_dimensions: int) -> tuple[int, int]:
    """Pick two distinct target dimensions for connection win."""
    return (0, 1)  # always available for dims >= 2 (R18 substrates)


def make_c1_custodian_connection(num_dimensions: int) -> dict:
    """Combo 1 — custodian capture + connection win."""
    p1, p2 = _connection_dims(num_dimensions)
    return dict(
        placement_rule=PlacementRule(
            target="empty", constraint="anywhere", first_move_anywhere=True,
        ),
        capture_rule=CaptureRule(capture_type="custodian"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="connection",
            target_dimension=p1,
            target_dimension_p2=p2,
            threshold=0.5,
            max_turns=100,
        ),
        turn_structure=TurnStructure(turn_type="alternating", pieces_per_turn=1),
        action_rule=ActionRule(action_types=("place",)),
    )


def make_c2_outnumber_threshold(num_dimensions: int) -> dict:
    """Combo 2 — outnumber-2 + threshold-race + radius-1 influence."""
    return dict(
        placement_rule=PlacementRule(
            target="empty", constraint="anywhere", first_move_anywhere=True,
        ),
        capture_rule=CaptureRule(capture_type="outnumber", threshold=2),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=1, strength=1.0, decay=0.5,
        ),
        win_condition=WinCondition(
            condition_type="threshold",
            threshold=20.0,  # min_threshold=10 * strength * (1+radius) = 20.0
            target_dimension=0,
            max_turns=100,
        ),
        turn_structure=TurnStructure(turn_type="alternating", pieces_per_turn=1),
        action_rule=ActionRule(action_types=("place",)),
    )


def make_c3_surround_territory(num_dimensions: int) -> dict:
    """Combo 3 — surround capture + territory win.

    Plan called for radius-1 influence here, but _fix_consistency demotes
    influence on non-threshold wins (vestigial); encode the post-fix form.
    """
    return dict(
        placement_rule=PlacementRule(
            target="empty", constraint="anywhere", first_move_anywhere=True,
        ),
        capture_rule=CaptureRule(capture_type="surround"),
        propagation_rule=PropagationRule(prop_type="none"),
        win_condition=WinCondition(
            condition_type="territory",
            threshold=0.5,
            target_dimension=0,
            max_turns=100,
        ),
        turn_structure=TurnStructure(turn_type="alternating", pieces_per_turn=1),
        action_rule=ActionRule(action_types=("place",)),
    )


COMBOS = [
    ("c1_custodian_connection",  make_c1_custodian_connection),
    ("c2_outnumber_threshold",   make_c2_outnumber_threshold),
    ("c3_surround_territory",    make_c3_surround_territory),
]


# ----------------------------------------------------------------------
# Substrate-specific adjustments (R17 audit + capture/topology gates)
# ----------------------------------------------------------------------

def _adjust_for_substrate(rules: dict, topology_type: str) -> dict:
    """Apply capture/topology adjustments that _fix_consistency would do
    at run time. Keeps seeds in their natural (post-fix) form so engine
    construction doesn't surprise."""
    out = dict(rules)
    cap = out["capture_rule"].capture_type
    # Custodian incompatible with hex/moore, but neither in our substrate
    # set. moore + surround would downgrade; not in our set either.
    # Fractal + custodian + connection is fine on all our substrates.

    # NOTE: sierpinski + threshold demote stays encoded — see module
    # docstring caveat. The seed JSON keeps threshold; audit-mode at
    # evolution time is the operator's job.
    return out


# ----------------------------------------------------------------------
# Seed assembly + write
# ----------------------------------------------------------------------

def build_seed(
    combo_label: str,
    combo_factory,
    substrate_label: str,
    topology_type: str,
    axis_size: int,
    num_dimensions: int,
) -> GameDefV2:
    rules = _adjust_for_substrate(
        combo_factory(num_dimensions), topology_type
    )
    return GameDefV2(
        game_id=f"{combo_label}__{substrate_label}",
        num_dimensions=num_dimensions,
        axis_size=axis_size,
        topology_type=topology_type,
        **rules,
        metadata={
            "source": "B3 R18 seed",
            "combo": combo_label,
            "substrate": substrate_label,
        },
    )


def validate_seed(game: GameDefV2, max_steps: int = 50) -> tuple[int, int | None]:
    """Build engine and run a 50-step random rollout. Returns (length, winner)."""
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
    print(f"\nBuilding 15 R18 seeds → {out_dir}\n")

    for combo_label, combo_factory in COMBOS:
        for sub_label, topo, axis, dims in SUBSTRATES:
            game = build_seed(
                combo_label, combo_factory, sub_label, topo, axis, dims,
            )
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
                f"  OK    {game.game_id:50s}  rollout_len={length:>3} "
                f"winner={winner}"
            )

    print(f"\n=== {15 - len(failures)} seeds OK, {len(failures)} failed ===")
    if failures:
        print("\nFailures:")
        for gid, msg in failures:
            print(f"  {gid}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
