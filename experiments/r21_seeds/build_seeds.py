#!/usr/bin/env python3
"""R21 seed builder — purpose-built per-substrate seed pools.

Per R21_plan.md § Seed pool design, R21 is a **focusing run, not a
breadth run**: each substrate's seed pool is hand-shaped, not a uniform
cross-family matrix.

Menger — tune-not-search (36 seeds):
  Family locked to `outnumber-2 + influence(r=1) + threshold-race + pie`.
  Cartesian sweep over:
    threshold ∈ {30, 40, 50, 60}     (R20 winners clustered around ~58 — sweep both sides)
    propagation_decay ∈ {0.5, 0.7, 1.0}
    max_turns ∈ {100, 150, 200}
  → 4 × 3 × 3 = 36 candidates → smoke filter → ~15-20 survivors. Pop 15, gens 4.

Carpet — retain-not-explore (6 sibling seeds):
  Family: `outnumber-2 + influence(r=2) + threshold-race + pie`. Anchor
  game `625bfc1f3f49` (R20's only above-R19 result, 4.70) is loaded as a
  carry-over at launch time via the driver's --seed-db; this builder
  emits 6 parameter-sweep siblings around it:
    threshold ∈ {25, 30, 35}, propagation_decay ∈ {0.5, 0.7}.
  Pop 15, gens 5.

Grid — restore-connection / R8-revival v2 (4 family seeds):
  Per team-1's R20 finding ("R8 minus connection-win = 4-point gap").
  R20 grid winner used custodian + threshold-race; R8 used custodian +
  connection. R21 grid restores connection-win as a candidate family
  with pie active (which R20's pie-bug prevented from testing on grid).
    G1  custodian-1 + connection + pie   (R8 exact + pie)
    G2  custodian-2 + connection + pie   (heavier capture × R8 win)
    G3  outnumber-2 + connection + pie   (R20's working capture × R8 win)
    G4  custodian-1 + threshold-race + pie  (R20-grid winner-style, head-to-head anchor)
  Pop 15, gens 5.

Total: 36 + 6 + 4 = 46 raw candidates. Smoke filter runs separately at
pre-launch (deferred compute — same pattern as S2 A/B, S4 komi driver,
S6 finalization parallelization, S1b slate dedup).

Every seed: pie_rule=True (post-ac9e642), komi_p2=0.0 default
(auto-calibrated post-evolution by S4 driver), place-only actions,
first_move_anywhere=True.

Run:
    .venv/bin/python experiments/r21_seeds/build_seeds.py

Writes JSON seed files to experiments/r21_seeds/seeds/<substrate>/.
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
    "menger": ("menger",     9, 3),
    "carpet": ("sierpinski", 9, 2),
    "grid":   ("grid",       9, 2),
}

for label, (topo, axis, dims) in SUBSTRATES.items():
    if topo in SUBSTRATE_INVARIANTS:
        expected = SUBSTRATE_INVARIANTS[topo]
        assert (axis, dims) == expected, (
            f"R21 substrate {label}/{topo} ({axis},{dims}) != invariant {expected}"
        )


# ----------------------------------------------------------------------
# Rule builders (per-game atoms)
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


def _influence(radius: int, decay: float, strength: float = 1.0) -> PropagationRule:
    return PropagationRule(
        prop_type="influence", radius=radius, strength=strength, decay=decay,
    )


def _threshold_race(threshold: float, max_turns: int) -> WinCondition:
    return WinCondition(
        condition_type="threshold", threshold=threshold, max_turns=max_turns,
    )


def _connection_win(num_dims: int, max_turns: int = 100) -> WinCondition:
    p2_dim = 1 if num_dims >= 2 else 0
    return WinCondition(
        condition_type="connection",
        target_dimension=0,
        target_dimension_p2=p2_dim,
        threshold=0.5,
        max_turns=max_turns,
    )


# ----------------------------------------------------------------------
# Menger pool — 4 × 3 × 3 = 36 seeds
# ----------------------------------------------------------------------

MENGER_THRESHOLDS = (30, 40, 50, 60)
MENGER_DECAYS = (0.5, 0.7, 1.0)
MENGER_MAX_TURNS = (100, 150, 200)


def build_menger_seeds() -> list[GameDefV2]:
    """Family locked: outnumber-2 + influence(r=1) + threshold-race + pie.
    Cartesian sweep over (threshold, decay, max_turns) — 36 seeds."""
    topo, axis, dims = SUBSTRATES["menger"]
    seeds: list[GameDefV2] = []
    for threshold in MENGER_THRESHOLDS:
        for decay in MENGER_DECAYS:
            for max_turns in MENGER_MAX_TURNS:
                # Encode parameters into game_id for traceability — also makes
                # the JSON filenames self-describing.
                gid = f"r21_menger_t{threshold}_d{int(decay*10):02d}_mt{max_turns}"
                seeds.append(GameDefV2(
                    game_id=gid,
                    num_dimensions=dims,
                    axis_size=axis,
                    topology_type=topo,
                    placement_rule=_placement(),
                    capture_rule=_capture("outnumber", threshold=2),
                    propagation_rule=_influence(radius=1, decay=decay),
                    win_condition=_threshold_race(threshold, max_turns),
                    turn_structure=_alt_turn(),
                    action_rule=_place_only(),
                    pie_rule=True,
                    metadata={
                        "source": "R21 seed",
                        "substrate": "menger",
                        "family": "outnumber2_inf1_thresh_pie",
                        "threshold": threshold,
                        "decay": decay,
                        "max_turns": max_turns,
                    },
                ))
    return seeds


# ----------------------------------------------------------------------
# Carpet pool — 6 sibling seeds
# ----------------------------------------------------------------------

CARPET_THRESHOLDS = (25, 30, 35)
CARPET_DECAYS = (0.5, 0.7)
CARPET_MAX_TURNS = 100  # R20 anchor used 100; not swept


def build_carpet_seeds() -> list[GameDefV2]:
    """Family locked: outnumber-2 + influence(r=2) + threshold-race + pie.
    Cartesian sweep over (threshold, decay) — 6 seeds. R20's anchor
    625bfc1f3f49 is added at launch via the driver's --seed-db (not
    duplicated here)."""
    topo, axis, dims = SUBSTRATES["carpet"]
    seeds: list[GameDefV2] = []
    for threshold in CARPET_THRESHOLDS:
        for decay in CARPET_DECAYS:
            gid = f"r21_carpet_t{threshold}_d{int(decay*10):02d}"
            seeds.append(GameDefV2(
                game_id=gid,
                num_dimensions=dims,
                axis_size=axis,
                topology_type=topo,
                placement_rule=_placement(),
                capture_rule=_capture("outnumber", threshold=2),
                propagation_rule=_influence(radius=2, decay=decay),
                win_condition=_threshold_race(threshold, CARPET_MAX_TURNS),
                turn_structure=_alt_turn(),
                action_rule=_place_only(),
                pie_rule=True,
                metadata={
                    "source": "R21 seed",
                    "substrate": "carpet",
                    "family": "outnumber2_inf2_thresh_pie",
                    "threshold": threshold,
                    "decay": decay,
                    "max_turns": CARPET_MAX_TURNS,
                },
            ))
    return seeds


# ----------------------------------------------------------------------
# Grid pool — 4 family seeds (R8-revival v2)
# ----------------------------------------------------------------------

GRID_MAX_TURNS = 100
GRID_THRESH_TURNS = 72  # R20's `fcedbc14043d` used 72
GRID_THRESH_VALUE = 20.0  # R20's `fcedbc14043d` used 20


def build_grid_seeds() -> list[GameDefV2]:
    """4 hand-picked families for R8-revival v2:
      G1  custodian-1 + connection + pie    (R8 exact + pie)
      G2  custodian-2 + connection + pie    (heavier capture × R8 win)
      G3  outnumber-2 + connection + pie    (R20's working capture × R8 win)
      G4  custodian-1 + threshold-race + pie  (head-to-head anchor for fcedbc14043d-style)
    """
    topo, axis, dims = SUBSTRATES["grid"]
    common = dict(
        num_dimensions=dims,
        axis_size=axis,
        topology_type=topo,
        placement_rule=_placement(),
        turn_structure=_alt_turn(),
        action_rule=_place_only(),
        pie_rule=True,
    )
    grid_families: list[tuple[str, str, CaptureRule, WinCondition, PropagationRule]] = [
        (
            "G1", "cust1_conn",
            _capture("custodian", threshold=1),
            _connection_win(dims, max_turns=GRID_MAX_TURNS),
            PropagationRule(prop_type="none"),
        ),
        (
            "G2", "cust2_conn",
            _capture("custodian", threshold=2),
            _connection_win(dims, max_turns=GRID_MAX_TURNS),
            PropagationRule(prop_type="none"),
        ),
        (
            "G3", "outn2_conn",
            _capture("outnumber", threshold=2),
            _connection_win(dims, max_turns=GRID_MAX_TURNS),
            PropagationRule(prop_type="none"),
        ),
        (
            "G4", "cust1_thresh",
            _capture("custodian", threshold=1),
            _threshold_race(GRID_THRESH_VALUE, GRID_THRESH_TURNS),
            _influence(radius=1, decay=0.5),
        ),
    ]
    seeds: list[GameDefV2] = []
    for family_id, short_id, capture, win, propagation in grid_families:
        gid = f"r21_grid_{family_id}_{short_id}"
        seeds.append(GameDefV2(
            game_id=gid,
            capture_rule=capture,
            propagation_rule=propagation,
            win_condition=win,
            metadata={
                "source": "R21 seed",
                "substrate": "grid",
                "family": family_id,
                "rule_summary": short_id,
            },
            **common,
        ))
    return seeds


# ----------------------------------------------------------------------
# Validation + main
# ----------------------------------------------------------------------

def validate_seed(game: GameDefV2, max_steps: int = 50) -> tuple[int, int | None]:
    engine = create_engine(game)
    a0 = RandomAgent(seed=1)
    a1 = RandomAgent(seed=2)
    winner, length, _ = play_game(
        engine, a0, a1, deterministic=False, max_steps=max_steps,
    )
    return length, winner


def all_seeds() -> list[GameDefV2]:
    """Single entry-point assembling the full R21 seed pool."""
    return (
        build_menger_seeds()
        + build_carpet_seeds()
        + build_grid_seeds()
    )


def main() -> int:
    out_base = Path(__file__).parent / "seeds"
    out_base.mkdir(parents=True, exist_ok=True)
    for sub in ("menger", "carpet", "grid"):
        (out_base / sub).mkdir(parents=True, exist_ok=True)

    seeds = all_seeds()
    print(f"\nBuilding {len(seeds)} R21 seeds → {out_base}\n")

    seen_canonical: dict[str, str] = {}
    failures: list[tuple[str, str]] = []
    for game in seeds:
        try:
            length, winner = validate_seed(game)
        except Exception as e:  # noqa: BLE001
            failures.append((game.game_id, repr(e)))
            print(f"  FAIL  {game.game_id}: {e}")
            continue

        # Sanity: pie_rule must serialise and swap action must be in place.
        d = game.to_dict()
        assert d.get("pie_rule") is True, (
            f"{game.game_id}: pie_rule missing from to_dict output"
        )
        assert game.swap_action_idx == game.num_actions - 1, (
            f"{game.game_id}: swap_action_idx mismatch"
        )

        # S1a sanity: no internal canonical duplicates inside the seed pool.
        h = game.canonical_hash()
        if h in seen_canonical:
            failures.append((
                game.game_id,
                f"canonical-hash collision with {seen_canonical[h]} "
                f"(both produce the same rule kernel)",
            ))
            print(f"  DUP   {game.game_id} ≡ {seen_canonical[h]}")
            continue
        seen_canonical[h] = game.game_id

        substrate = game.metadata.get("substrate", "unknown")
        out_path = out_base / substrate / f"{game.game_id}.json"
        with open(out_path, "w") as f:
            json.dump(d, f, indent=2)
        print(
            f"  OK    {game.game_id:42s}  rollout_len={length:>3}  winner={winner}"
        )

    print(
        f"\n=== {len(seeds) - len(failures)} seeds OK, "
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
