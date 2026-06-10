"""FC phase-1.5 — build C1/C2/C3 game defs on the probe's hex_rhombus W=22
board, copy the probe-calibrated A0/A1 comparators, random-rollout smoke all.

Spec: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md.
Shared base (spec §3): r=1/s=1.0/d=0.5, control_margin 0.25, pie on,
max_turns 200, komi 0.0 pre-calibration.

Usage:
    python experiments/fc_phase15/build_games.py [--smoke 50]
"""
from __future__ import annotations

import argparse
import json
import shutil
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
PROBE_CAL = ROOT / "experiments" / "field_connect_probe" / "games" / "calibrated"

W = 22

COMMON = dict(
    num_dimensions=2,
    axis_size=W,
    topology_type="hex_rhombus",
    turn_structure=TurnStructure(turn_type="alternating"),
    action_rule=ActionRule(action_types=("place",)),
    pie_rule=True,
)

WIN = dict(
    condition_type="field_connection",
    control_margin=0.25,
    target_dimension=1,
    target_dimension_p2=0,
    max_turns=200,
)

FIELD = dict(prop_type="influence", radius=1, strength=1.0, decay=0.5)


def build_c1() -> GameDefV2:
    return GameDefV2(
        game_id="p15_c1_field_flip",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_flip"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(**WIN),
        **COMMON,
    )


def build_c2() -> GameDefV2:
    # first_move_anywhere=False: the default True would waive the gate on
    # each player's first stone, violating spec §4 C2. On an empty board
    # the gate excludes nothing anyway (field is 0).
    return GameDefV2(
        game_id="p15_c2_contested_terrain",
        placement_rule=PlacementRule(
            target="empty", constraint="not_enemy_controlled",
            first_move_anywhere=False,
        ),
        capture_rule=CaptureRule(capture_type="none"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(**WIN),
        **COMMON,
    )


def build_c3() -> GameDefV2:
    return GameDefV2(
        game_id="p15_c3_control_capture",
        placement_rule=PlacementRule(target="empty", constraint="anywhere"),
        capture_rule=CaptureRule(capture_type="field_replace"),
        propagation_rule=PropagationRule(**FIELD),
        win_condition=WinCondition(**WIN),
        **COMMON,
    )


def smoke(game: GameDefV2, n: int, rng: np.random.Generator) -> dict:
    lengths, capture_events, draws, timeouts, stranded, gate_seen = [], 0, 0, 0, 0, 0
    for _ in range(n):
        e = GameEngineV2(game)
        e.reset()
        prev_counts = list(e.piece_counts)
        while not e.done:
            legal = e.get_legal_actions()
            if game.placement_rule.constraint == "not_enemy_controlled":
                empties = sum(1 for c in e.topo.active_cells
                              if e.board_owners[c] == 0)
                if sum(1 for a in legal if a < e.total_cells) < empties:
                    gate_seen += 1
            e.step(int(rng.choice(legal)))
            for p in (0, 1):
                drop = prev_counts[p] - e.piece_counts[p]
                if drop > 0:
                    capture_events += drop
            prev_counts = list(e.piece_counts)
        lengths.append(e.step_count)
        draws += e._winner is None
        timeouts += e._ended_by_max_turns
        stranded += getattr(e, "_ended_by_no_moves", False)
    return dict(
        game_id=game.game_id, n=n, mean_len=float(np.mean(lengths)),
        capture_events=capture_events, draws=draws, timeouts=timeouts,
        stranded=stranded, gate_seen=gate_seen,
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke", type=int, default=50)
    args = p.parse_args()

    GAMES_DIR.mkdir(exist_ok=True)
    games = [build_c1(), build_c2(), build_c3()]
    for g in games:
        path = GAMES_DIR / f"{g.game_id.removeprefix('p15_')}.json"
        json.dump(g.to_dict(), open(path, "w"), indent=2)
        print(f"wrote {path}")
    for src in ("a0_baseline.json", "a1_field_connect.json"):
        shutil.copy(PROBE_CAL / src, GAMES_DIR / src)
        print(f"copied probe-calibrated {src}")

    rng = np.random.default_rng(0)
    for g in games:
        r = smoke(g, args.smoke, rng)
        print(r)
        assert r["mean_len"] <= g.win_condition.max_turns + 1
        if g.game_id == "p15_c1_field_flip":
            assert r["capture_events"] > 0, "C1 smoke: no flips ever fired"
        if g.game_id == "p15_c3_control_capture":
            assert r["capture_events"] > 0, "C3 smoke: no replacements fired"
        if g.game_id == "p15_c2_contested_terrain":
            assert r["gate_seen"] > 0, "C2 smoke: gate never restricted moves"
    print("SMOKE OK")


if __name__ == "__main__":
    main()
