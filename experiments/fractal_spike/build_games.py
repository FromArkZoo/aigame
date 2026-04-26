"""Build the six candidate games for the fractal-topology spike.

Three (fractal, control) pairs:

    A-fractal: c6bb58075520 (R16 winner) cloned onto sierpinski 9x9
    A-control: c6bb58075520 verbatim on torus 8x8

    B-fractal: deb4dfe0382d (R14 winner) cloned onto sierpinski 9x9
    B-control: deb4dfe0382d verbatim on torus 8x8

    C-fractal: alt + surround + connection on sierpinski 9x9
               (path-routing-around-central-hole is the substrate's biggest
               unique affordance)
    C-control: same rules on grid 8x8 (torus+connection is broken — quick-reject)

Run as: .venv/bin/python experiments/fractal_spike/build_games.py
"""

from __future__ import annotations

import copy
import json
import os
import sqlite3
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from game_engine.game_def_v2 import GameDefV2


CANDIDATES_DIR = os.path.join(_HERE, "candidates")


def _load_from_db(db_path: str, game_id: str) -> GameDefV2:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT rule_representation FROM games WHERE game_id = ?",
            (game_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise RuntimeError(f"{game_id} not found in {db_path}")
    return GameDefV2.from_dict(json.loads(row[0]))


def _save(game: GameDefV2, name: str) -> str:
    path = os.path.join(CANDIDATES_DIR, f"{name}.json")
    with open(path, "w") as fp:
        json.dump(game.to_dict(), fp, indent=2)
    return path


def build_pair_a() -> tuple[str, str]:
    """A-pair: R16 human winner c6bb58075520 (alt + outnumber-2 + influence-1 + threshold)."""
    base = _load_from_db(
        os.path.join(_REPO, "genesis_v2_run16.db"),
        "c6bb58075520",
    )

    control = copy.deepcopy(base)
    control.game_id = "frac_A_control"
    control.metadata = {
        "spike": "fractal",
        "pair": "A",
        "role": "control",
        "source_game": "c6bb58075520",
        "source_run": "R16",
    }

    fractal = copy.deepcopy(base)
    fractal.game_id = "frac_A_fractal"
    fractal.topology_type = "sierpinski"
    fractal.axis_size = 9
    fractal._topology = None  # invalidate lazy cache
    # Threshold kept identical: same 64-active-cell budget; harder to reach on
    # fractal because cells near holes have lower degree, but that's the test.
    fractal.metadata = {
        "spike": "fractal",
        "pair": "A",
        "role": "fractal",
        "source_game": "c6bb58075520",
        "source_run": "R16",
        "rule_family": "alt+outnumber+influence+threshold",
        "threshold_unchanged": True,
    }

    return _save(control, "frac_A_control"), _save(fractal, "frac_A_fractal")


def build_pair_b() -> tuple[str, str]:
    """B-pair: R14 winner deb4dfe0382d (alt + custodian + influence + threshold)."""
    base = _load_from_db(
        os.path.join(_REPO, "genesis_v2_run14.db"),
        "deb4dfe0382d",
    )

    control = copy.deepcopy(base)
    control.game_id = "frac_B_control"
    control.metadata = {
        "spike": "fractal",
        "pair": "B",
        "role": "control",
        "source_game": "deb4dfe0382d",
        "source_run": "R14",
    }

    fractal = copy.deepcopy(base)
    fractal.game_id = "frac_B_fractal"
    fractal.topology_type = "sierpinski"
    fractal.axis_size = 9
    fractal._topology = None
    fractal.metadata = {
        "spike": "fractal",
        "pair": "B",
        "role": "fractal",
        "source_game": "deb4dfe0382d",
        "source_run": "R14",
        "rule_family": "alt+custodian+influence+threshold",
        "threshold_unchanged": True,
        "note": "custodian walk treats holes as walls (engine_v2.py:_capture_custodian)",
    }

    return _save(control, "frac_B_control"), _save(fractal, "frac_B_fractal")


def build_pair_c() -> tuple[str, str]:
    """C-pair: connection-win — fractal-native test. Path routing around the
    central hole is the substrate's biggest unique affordance.

    Rules (consistency-safe per _fix_consistency):
      - alternating turns
      - surround capture
      - propagation: none (connection-win games can't use influence/threshold)
      - connection win, P1 axis 0, P2 axis 1
      - max_turns: 100
    """
    from game_engine.rules import (
        ActionRule, CaptureRule, PlacementRule, PropagationRule,
        TurnStructure, WinCondition,
    )

    common_rules = dict(
        placement_rule=PlacementRule(
            target="empty",
            constraint="anywhere",
            first_move_anywhere=True,
        ),
        capture_rule=CaptureRule(capture_type="surround", threshold=1),
        propagation_rule=PropagationRule(
            prop_type="none", radius=1, strength=1.0, decay=0.5,
        ),
        win_condition=WinCondition(
            condition_type="connection",
            threshold=0.5,
            target_dimension=0,
            target_dimension_p2=1,
            max_turns=100,
        ),
        turn_structure=TurnStructure(turn_type="alternating", pieces_per_turn=1),
        action_rule=ActionRule(
            action_types=("place",), move_constraint="adjacent_empty",
        ),
    )

    control = GameDefV2(
        game_id="frac_C_control",
        num_dimensions=2,
        axis_size=8,
        topology_type="grid",
        num_players=2,
        metadata={
            "spike": "fractal",
            "pair": "C",
            "role": "control",
            "source_game": "hand-crafted",
            "rule_family": "alt+surround+connection",
            "note": "grid 8x8 control (torus+connection is quick-rejected as broken)",
        },
        **common_rules,
    )

    fractal = GameDefV2(
        game_id="frac_C_fractal",
        num_dimensions=2,
        axis_size=9,
        topology_type="sierpinski",
        num_players=2,
        metadata={
            "spike": "fractal",
            "pair": "C",
            "role": "fractal",
            "source_game": "hand-crafted",
            "rule_family": "alt+surround+connection",
            "note": "Connection across the central 3x3 hole forces routing around terrain",
        },
        **common_rules,
    )

    return _save(control, "frac_C_control"), _save(fractal, "frac_C_fractal")


def main() -> None:
    os.makedirs(CANDIDATES_DIR, exist_ok=True)
    paths = []
    paths.extend(build_pair_a())
    paths.extend(build_pair_b())
    paths.extend(build_pair_c())
    for p in paths:
        print(f"  wrote {os.path.relpath(p, _REPO)}")
    print(f"\n{len(paths)} candidate game files saved.")


if __name__ == "__main__":
    main()
