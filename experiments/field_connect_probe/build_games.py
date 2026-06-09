"""Field-Connect probe — build the A1 (treatment) and A0 (control) game
defs on the shared hex_rhombus W=22 board, then random-rollout smoke them.

Spec: docs/superpowers/specs/2026-06-07-field-connect-probe-design.md (v2).
Pre-registered defaults (spec §9): W=22; A1 influence r=2/s=1.0/d=0.5,
margin 0.0; A0 = R21 menger plateau family (outnumber-2 + influence
r=1/d=0.7 + threshold 36 = R21's 30 scaled by 484/400); max_turns 200;
pie on; komi calibrated later (calibrate.py).

Usage:
    python experiments/field_connect_probe/build_games.py [--smoke 50]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.engine_v2 import GameEngineV2  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.rules import (  # noqa: E402
    ActionRule,
    CaptureRule,
    PlacementRule,
    PropagationRule,
    TurnStructure,
    WinCondition,
)

HERE = Path(__file__).resolve().parent
GAMES_DIR = HERE / "games"

W = 22  # 484 cells

COMMON = dict(
    num_dimensions=2,
    axis_size=W,
    topology_type="hex_rhombus",
    placement_rule=PlacementRule(target="empty", constraint="anywhere"),
    turn_structure=TurnStructure(turn_type="alternating"),
    action_rule=ActionRule(action_types=("place",)),
    pie_rule=True,
)


def build_a1() -> GameDefV2:
    """Field-Connect: influence IS the win condition + surround capture."""
    return GameDefV2(
        game_id="fc_probe_a1_field_connect",
        capture_rule=CaptureRule(capture_type="surround"),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=2, strength=1.0, decay=0.5,
        ),
        win_condition=WinCondition(
            condition_type="field_connection",
            control_margin=0.0,
            target_dimension=1,      # P1 connects r=0 <-> r=W-1
            target_dimension_p2=0,   # P2 connects q=0 <-> q=W-1
            max_turns=200,
        ),
        **COMMON,
    )


def build_a0() -> GameDefV2:
    """Plateau baseline: R20/R21 menger family, board held constant."""
    return GameDefV2(
        game_id="fc_probe_a0_baseline",
        capture_rule=CaptureRule(capture_type="outnumber", threshold=2),
        propagation_rule=PropagationRule(
            prop_type="influence", radius=1, strength=1.0, decay=0.7,
        ),
        win_condition=WinCondition(
            condition_type="threshold",
            threshold=36.0,          # R21's 30 x (484/400)
            max_turns=200,
        ),
        **COMMON,
    )


def smoke(game: GameDefV2, episodes: int, seed: int = 0) -> dict:
    """Uniform-random rollouts: the game must terminate, never error, and
    show every end cause is reachable."""
    rng = np.random.default_rng(seed)
    causes = {"win_condition": 0, "timeout": 0, "draw": 0}
    lengths = []
    for _ in range(episodes):
        e = GameEngineV2(game)
        e.reset()
        while not e.done:
            legal = e.get_legal_actions()
            if not legal:
                break
            e.step(int(rng.choice(legal)))
        lengths.append(e.step_count)
        timeout = e.step_count >= game.max_game_steps
        if e._winner is None:
            causes["draw"] += 1
        elif timeout:
            causes["timeout"] += 1
        else:
            causes["win_condition"] += 1
    return {"avg_length": float(np.mean(lengths)), **causes}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke", type=int, default=50)
    args = p.parse_args()

    GAMES_DIR.mkdir(parents=True, exist_ok=True)
    for game in (build_a1(), build_a0()):
        out = GAMES_DIR / f"{game.game_id.removeprefix('fc_probe_')}.json"
        with open(out, "w") as f:
            json.dump(game.to_dict(), f, indent=2)
        print(f"wrote {out}")
        if args.smoke:
            print(f"  smoke({args.smoke}): {smoke(game, args.smoke)}")


if __name__ == "__main__":
    main()
