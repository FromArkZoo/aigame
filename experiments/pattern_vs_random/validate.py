"""Sanity-check all four pattern-vs-random candidate games end-to-end.

For each game JSON:
  1. Load via GameDefV2.from_dict (verifies serialisation round-trip).
  2. Build the engine; verify hole counts and active-cell counts match metadata.
  3. Verify holes have no neighbours and reject placements.
  4. Play a random self-play game until termination; verify no exceptions
     and that legal_actions never includes hole cells.

Run as: .venv/bin/python experiments/pattern_vs_random/validate.py
"""

from __future__ import annotations

import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from game_engine.game_def_v2 import GameDefV2
from game_engine.engine_v2 import GameEngineV2

CANDIDATES_DIR = os.path.join(_HERE, "candidates")
NAMES = ["pat_grid", "pat_fractal", "pat_random", "pat_structured"]
SELF_PLAY_SEED = 1


def _load(name: str) -> GameDefV2:
    with open(os.path.join(CANDIDATES_DIR, f"{name}.json")) as fp:
        return GameDefV2.from_dict(json.load(fp))


def _check_topology(game: GameDefV2) -> dict:
    topo = game.get_topology()
    expected_active = game.metadata.get("active_cells", topo.total_cells)
    assert topo.num_active_cells == expected_active, (
        f"{game.game_id}: active_cells mismatch "
        f"(topo={topo.num_active_cells}, metadata={expected_active})"
    )
    # Holes must have empty neighbour lists
    if game.holes is not None:
        for h in game.holes:
            assert topo.get_neighbors(h) == [], (
                f"{game.game_id}: hole {h} has non-empty neighbours"
            )
            assert not topo.active_mask[h], (
                f"{game.game_id}: hole {h} marked active"
            )
    return {
        "topology_type": topo.topology_type,
        "active_cells": topo.num_active_cells,
        "max_degree": topo.max_degree,
        "holes": len(game.holes) if game.holes else 0,
    }


def _self_play(game: GameDefV2, seed: int) -> dict:
    rng = random.Random(seed)
    eng = GameEngineV2(game)
    eng.reset()
    holes = set(game.holes or [])
    if game.topology_type == "sierpinski":
        # Pull holes from topology since GameDefV2.holes is None for sierpinski
        holes = {c for c in range(eng.total_cells) if not eng.topo.active_mask[c]}
    steps = 0
    while not eng.done:
        legal = eng.get_legal_actions()
        # Hole placements should never be legal
        for cell in holes:
            assert cell not in legal, (
                f"{game.game_id} step {steps}: hole {cell} listed as legal action"
            )
        action = rng.choice(legal)
        eng.step(action)
        steps += 1
        if steps > 500:
            raise RuntimeError(f"{game.game_id}: self-play exceeded 500 steps")
    return {
        "steps": steps,
        "winner": eng._winner,
        "p1_pieces": eng.piece_counts[0],
        "p2_pieces": eng.piece_counts[1],
    }


def main() -> int:
    failures = 0
    for name in NAMES:
        try:
            game = _load(name)
            topo_info = _check_topology(game)
            play_info = _self_play(game, SELF_PLAY_SEED)
            print(
                f"  PASS  {name:18s}  "
                f"type={topo_info['topology_type']:11s}  "
                f"active={topo_info['active_cells']:3d}  "
                f"holes={topo_info['holes']:2d}  "
                f"max_deg={topo_info['max_degree']}  "
                f"steps={play_info['steps']:3d}  "
                f"winner={play_info['winner']}"
            )
        except Exception as e:
            failures += 1
            print(f"  FAIL  {name}: {type(e).__name__}: {e}")
    print()
    if failures:
        print(f"FAIL: {failures}/{len(NAMES)} games failed validation")
        return 1
    print(f"PASS: all {len(NAMES)} games validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
