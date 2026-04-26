"""Build the four candidate games for the pattern-vs-random probe.

Four conditions, identical Pair-C ruleset (alt + surround + connection),
varying only the hole-set on the substrate:

    pat_fractal     : Sierpinski level-2 carpet on 9x9
    pat_random      : 17 random holes on 9x9 (fixed seed, face-connected)
    pat_structured  : 17 stride-2 lattice + centre holes on 9x9
    pat_grid        : pure 8x8 grid, no holes (shared control mirroring frac_C_control)

Run as: .venv/bin/python experiments/pattern_vs_random/build_games.py
"""

from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import (
    ActionRule, CaptureRule, PlacementRule, PropagationRule,
    TurnStructure, WinCondition,
)

from experiments.pattern_vs_random.hole_patterns import (
    AXIS_SIZE, RANDOM_SEED,
    sierpinski_holes, random_holes, structured_holes, render,
)


CANDIDATES_DIR = os.path.join(_HERE, "candidates")


def _save(game: GameDefV2, name: str) -> str:
    path = os.path.join(CANDIDATES_DIR, f"{name}.json")
    with open(path, "w") as fp:
        json.dump(game.to_dict(), fp, indent=2)
    return path


def _common_rules() -> dict:
    """Pair-C ruleset: alt + surround + connection. Locked across all four."""
    return dict(
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


def build_grid_control() -> str:
    """Pure 8x8 grid, no holes. Mirrors frac_C_control."""
    game = GameDefV2(
        game_id="pat_grid",
        num_dimensions=2,
        axis_size=8,
        topology_type="grid",
        num_players=2,
        metadata={
            "spike": "pattern_vs_random",
            "condition": "grid",
            "hole_count": 0,
            "active_cells": 64,
            "rule_family": "alt+surround+connection",
            "note": "shared control; identical to frac_C_control",
        },
        **_common_rules(),
    )
    return _save(game, "pat_grid")


def build_fractal() -> str:
    """Sierpinski level-2 carpet 9x9. Mirrors frac_C_fractal."""
    holes = sierpinski_holes()
    game = GameDefV2(
        game_id="pat_fractal",
        num_dimensions=2,
        axis_size=AXIS_SIZE,
        topology_type="sierpinski",
        num_players=2,
        metadata={
            "spike": "pattern_vs_random",
            "condition": "fractal",
            "hole_count": len(holes),
            "active_cells": AXIS_SIZE * AXIS_SIZE - len(holes),
            "rule_family": "alt+surround+connection",
            "hole_pattern_name": "sierpinski_level2",
            "ascii": render(holes),
        },
        **_common_rules(),
    )
    return _save(game, "pat_fractal")


def build_random() -> str:
    """Random 17-hole 9x9, locked seed. Topology type: holes."""
    holes = random_holes(RANDOM_SEED)
    game = GameDefV2(
        game_id="pat_random",
        num_dimensions=2,
        axis_size=AXIS_SIZE,
        topology_type="holes",
        num_players=2,
        holes=holes,
        metadata={
            "spike": "pattern_vs_random",
            "condition": "random",
            "hole_count": len(holes),
            "active_cells": AXIS_SIZE * AXIS_SIZE - len(holes),
            "rule_family": "alt+surround+connection",
            "hole_pattern_name": "random_seed_20260426",
            "random_seed": RANDOM_SEED,
            "ascii": render(holes),
        },
        **_common_rules(),
    )
    return _save(game, "pat_random")


def build_structured() -> str:
    """Stride-2 lattice + centre, 17 holes 9x9. Topology type: holes."""
    holes = structured_holes()
    game = GameDefV2(
        game_id="pat_structured",
        num_dimensions=2,
        axis_size=AXIS_SIZE,
        topology_type="holes",
        num_players=2,
        holes=holes,
        metadata={
            "spike": "pattern_vs_random",
            "condition": "structured",
            "hole_count": len(holes),
            "active_cells": AXIS_SIZE * AXIS_SIZE - len(holes),
            "rule_family": "alt+surround+connection",
            "hole_pattern_name": "stride2_lattice_plus_centre",
            "ascii": render(holes),
        },
        **_common_rules(),
    )
    return _save(game, "pat_structured")


def main() -> None:
    os.makedirs(CANDIDATES_DIR, exist_ok=True)
    paths = [
        build_grid_control(),
        build_fractal(),
        build_random(),
        build_structured(),
    ]
    for p in paths:
        print(f"  wrote {os.path.relpath(p, _REPO)}")
    print(f"\n{len(paths)} candidate game files saved.")


if __name__ == "__main__":
    main()
