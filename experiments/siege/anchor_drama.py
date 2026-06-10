"""Stage 1.5: anchor-calibrate per-role drama BEFORE it becomes a screen bar.

Retro-computes drama on fresh rollout traces (random + greedy, n/2 each) for:
a0_baseline, a1_field_connect, e1453dac5445 (R21 GE-top), 573562833174 (R21 GE-bottom).
BAR (prereg): drama(a1) > drama(a0) AND e1453 NOT ranked top of the four.
FAIL -> prints DRAMA_DEMOTED: drama becomes diagnostic; screen GO = 2/2
of the remaining comparatives (run_screen.py --anchor-result demoted).
PASS -> prints DRAMA_ANCHORED (run_screen.py --anchor-result pass).

Game families:
  a0_baseline       : threshold   (experiments/siege/games/a0_baseline.json)
  a1_field_connect  : field_connection  (experiments/siege/games/a1_field_connect.json)
  e1453dac5445      : threshold   (genesis_v2_run21_menger.db, R21 GE-top)
  573562833174      : connection  (genesis_v2_run21_grid.db, R21 GE-bottom)

Progress trace per family:
  threshold    : per-player effective score / threshold (p1 = +values; p2 = neg(values)+komi)
  field_connection: maker_progress_span from experiments/siege/metrics.py (field control span)
  connection   : owner_progress_span — largest OWNED component's axis-span fraction
                 (board_owners == player); local helper, does NOT modify metrics.py.

Usage:
    .venv/bin/python experiments/siege/anchor_drama.py [--n 200] [--games a0,a1,e1453,573] [--seed 11]
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
from pathlib import Path
from typing import Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from training.utils import RandomAgent, GreedyAgent  # noqa: E402
from experiments.siege.metrics import maker_progress_span, winner_behindness  # noqa: E402

# ---------------------------------------------------------------------------
# Constants — game IDs and DB paths (prereg § Step 1)
# ---------------------------------------------------------------------------
GAMES_DIR = HERE / "games"

GAME_SPECS: dict[str, dict] = {
    "a0": {
        "key": "a0",
        "label": "a0_baseline",
        "family": "threshold",
        "source": "json",
        "path": GAMES_DIR / "a0_baseline.json",
    },
    "a1": {
        "key": "a1",
        "label": "a1_field_connect",
        "family": "field_connection",
        "source": "json",
        "path": GAMES_DIR / "a1_field_connect.json",
    },
    "e1453": {
        "key": "e1453",
        "label": "e1453dac5445",
        "family": "threshold",
        "source": "db",
        "db": "genesis_v2_run21_menger.db",
        "game_id": "e1453dac5445",
    },
    "573": {
        "key": "573",
        "label": "573562833174",
        "family": "connection",
        "source": "db",
        "db": "genesis_v2_run21_grid.db",
        "game_id": "573562833174",
    },
}

SHORT_TO_KEY = {k: k for k in GAME_SPECS}


# ---------------------------------------------------------------------------
# Game loading
# ---------------------------------------------------------------------------

def load_game_from_json(path: Path) -> GameDefV2:
    d = json.loads(path.read_text())
    return GameDefV2.from_dict(d)


def load_game_from_db(db_name: str, game_id: str) -> GameDefV2:
    db_path = ROOT / db_name
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)
    ).fetchone()
    con.close()
    if row is None:
        raise SystemExit(f"game {game_id} not found in {db_name}")
    return GameDefV2.from_dict(json.loads(row["rule_representation"]))


def load_spec(spec: dict) -> GameDefV2:
    if spec["source"] == "json":
        return load_game_from_json(spec["path"])
    else:
        return load_game_from_db(spec["db"], spec["game_id"])


# ---------------------------------------------------------------------------
# Per-player progress helpers
# ---------------------------------------------------------------------------

def threshold_progress_p1(engine) -> float:
    """P1 effective threshold-race score / threshold (replicates engine _check_threshold for P1).

    P1's values are positive. effective_p1 = sum(board_values[c] for c in P1-owned cells).
    Normalized by threshold so progress ∈ [0, ~1] during play (may exceed 1 at win).
    Not clamped — the pre-registered formula for behindness has no clip.
    """
    threshold = engine.game.win_condition.threshold
    if threshold == 0:
        return 0.0
    total = sum(
        float(engine.board_values[c])
        for c in engine.topo.active_cells
        if engine.board_owners[c] == 1
    )
    return total / threshold


def threshold_progress_p2(engine) -> float:
    """P2 effective threshold-race score / threshold (replicates engine _check_threshold for P2).

    P2 values are negative; effective = -total + komi (komi = komi_p2 * threshold).
    Normalized by threshold.
    """
    threshold = engine.game.win_condition.threshold
    if threshold == 0:
        return 0.0
    komi = getattr(engine.game, "komi_p2", 0.0) * threshold
    total = sum(
        float(engine.board_values[c])
        for c in engine.topo.active_cells
        if engine.board_owners[c] == 2
    )
    effective_p2 = -total + komi
    return effective_p2 / threshold


def owner_progress_span(engine, player: int, axis: int) -> float:
    """Largest connected component of player's OWNED cells axis-span fraction.

    For plain ``connection`` win-condition games (e.g. 573562833174) where
    progress is measured by board_owners (stones), not field values.

    Algorithm mirrors maker_progress_span (experiments/siege/metrics.py) but
    operates on board_owners instead of controlled field cells. Written here
    (NOT in metrics.py) to keep the pre-registered module untouched.

    Returns distinct axis-coord count of largest OWNED component / axis_size.
    """
    cells = {c for c in engine.topo.active_cells if engine.board_owners[c] == player}
    if not cells:
        return 0.0

    best_component: set[int] = set()
    unseen = set(cells)
    while unseen:
        start = unseen.pop()
        component: set[int] = {start}
        stack = [start]
        while stack:
            c = stack.pop()
            for n in engine.topo.get_neighbors(c):
                if n in unseen:
                    unseen.remove(n)
                    component.add(n)
                    stack.append(n)
        if len(component) > len(best_component):
            best_component = component

    axis_size = engine.topo.axis_size
    distinct_coords = {engine.topo.cell_to_coords(c)[axis] for c in best_component}
    return len(distinct_coords) / axis_size


def get_axis_for_player(game: GameDefV2, player: int) -> int:
    """Return the target axis for a given player in connection/field_connection games.

    Mirrors engine_v2.py _check_connection logic (line 1235-1242):
      P1 axis = wc.target_dimension
      P2 axis = wc.target_dimension_p2 if >= 0 else (target_dimension + 1) % num_dimensions
    No _goals_swapped handling (anchor_drama uses fresh rollouts without pie-swap tracking;
    a0/e1453 are threshold games so this is irrelevant for them).
    """
    wc = game.win_condition
    p1_axis = wc.target_dimension
    p2_axis_raw = wc.target_dimension_p2
    if p2_axis_raw < 0:
        p2_axis = (p1_axis + 1) % game.num_dimensions
    else:
        p2_axis = p2_axis_raw
    return p1_axis if player == 1 else p2_axis


# ---------------------------------------------------------------------------
# Per-ply progress trace recording
# ---------------------------------------------------------------------------

def record_progress(engine, game: GameDefV2, family: str, player: int) -> float:
    """Return per-player progress at the CURRENT board state.

    family == "threshold"      : threshold_progress_p{player}
    family == "field_connection": maker_progress_span (uses field control + margin)
    family == "connection"     : owner_progress_span (uses board_owners)
    """
    wc = game.win_condition
    if family == "threshold":
        return threshold_progress_p1(engine) if player == 1 else threshold_progress_p2(engine)
    elif family == "field_connection":
        margin = getattr(wc, "control_margin", 0.0)
        axis = get_axis_for_player(game, player)
        return maker_progress_span(engine, player, axis, margin)
    elif family == "connection":
        axis = get_axis_for_player(game, player)
        return owner_progress_span(engine, player, axis)
    else:
        raise ValueError(f"Unknown family: {family}")


# ---------------------------------------------------------------------------
# Rollout with trace collection
# ---------------------------------------------------------------------------

def play_with_trace(
    engine,
    game: GameDefV2,
    family: str,
    agent0,
    agent1,
    max_steps: int | None = None,
    deterministic: bool = False,
) -> tuple[int | None, list[float], list[float]]:
    """Play one game, recording per-ply P1/P2 progress traces.

    Returns (winner_player, p1_trace, p2_trace).
    winner_player is engine._winner (1, 2, or None).
    Traces include the reading AFTER each step (post-move board state).
    """
    agents = [agent0, agent1]
    engine.reset()
    done = False
    step_count = 0
    if max_steps is None:
        max_steps = game.max_game_steps

    p1_trace: list[float] = []
    p2_trace: list[float] = []

    while not done and step_count < max_steps:
        current_player = engine.get_current_player()
        legal_actions = engine.get_legal_actions()
        if len(legal_actions) == 0:
            break
        action, _, _ = agents[current_player].select_action(
            None, legal_actions=legal_actions, deterministic=deterministic
        )
        _, _, done, _ = engine.step(action)
        step_count += 1
        p1_trace.append(record_progress(engine, game, family, 1))
        p2_trace.append(record_progress(engine, game, family, 2))

    return engine._winner, p1_trace, p2_trace


# ---------------------------------------------------------------------------
# Per-game drama computation over n rollouts
# ---------------------------------------------------------------------------

def compute_drama_for_game(
    spec: dict,
    n: int,
    base_seed: int,
) -> dict:
    """Run n rollouts (n/2 random-pair, n/2 greedy-pair) for one game spec.

    Returns dict with: key, label, family, n_requested, n_used, draws_skipped, mean_drama.
    """
    game = load_spec(spec)
    family = spec["family"]
    key = spec["key"]
    label = spec["label"]
    max_steps = game.max_game_steps

    n_random = n // 2
    n_greedy = n - n_random  # handles odd n: greedy gets the extra rollout

    drama_values: list[float] = []
    draws_skipped = 0

    # --- random-pair rollouts ---
    for i in range(n_random):
        engine = create_engine(game)
        seed_r = base_seed * 10_000 + i
        rand0 = RandomAgent(seed=seed_r)
        rand1 = RandomAgent(seed=seed_r + 1)
        winner, p1_trace, p2_trace = play_with_trace(
            engine, game, family, rand0, rand1,
            max_steps=max_steps, deterministic=False,
        )
        if winner is None:
            draws_skipped += 1
            continue
        # winner is 1 or 2; engine._winner uses 1-indexed players
        if winner == 1:
            drama_values.append(winner_behindness(p1_trace, p2_trace))
        else:
            drama_values.append(winner_behindness(p2_trace, p1_trace))

    # --- greedy-pair rollouts (mirrors trainer.evaluate seed idiom) ---
    for i in range(n_greedy):
        engine = create_engine(game)
        # Seed derivation matches trainer.evaluate: seed_offset = seed * 29 + 31 * i
        # We substitute base_seed for trainer seed; offset by i (episode index)
        seed_offset = base_seed * 29 + 31 * i
        greedy0 = GreedyAgent(engine, player_num=1, seed=seed_offset)
        greedy1 = GreedyAgent(engine, player_num=2, seed=seed_offset + 7)
        winner, p1_trace, p2_trace = play_with_trace(
            engine, game, family, greedy0, greedy1,
            max_steps=max_steps, deterministic=False,
        )
        if winner is None:
            draws_skipped += 1
            continue
        if winner == 1:
            drama_values.append(winner_behindness(p1_trace, p2_trace))
        else:
            drama_values.append(winner_behindness(p2_trace, p1_trace))

    n_used = len(drama_values)
    mean_drama = float(np.mean(drama_values)) if drama_values else float("nan")

    return {
        "key": key,
        "label": label,
        "family": family,
        "n_requested": n,
        "n_used": n_used,
        "draws_skipped": draws_skipped,
        "mean_drama": mean_drama,
    }


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage-1.5 anchor-calibrate per-role drama (a0/a1 + R21 extremes)."
    )
    parser.add_argument(
        "--n", type=int, default=200,
        help="Total rollouts per game (n/2 random-pair + n/2 greedy-pair). Default: 200.",
    )
    parser.add_argument(
        "--games", type=str, default="a0,a1,e1453,573",
        help="Comma-separated short keys to run (subset = ANCHOR_INCOMPLETE). Default: a0,a1,e1453,573.",
    )
    parser.add_argument(
        "--seed", type=int, default=11,
        help="Base seed for all rollouts. Default: 11.",
    )
    args = parser.parse_args()

    requested_keys = [k.strip() for k in args.games.split(",") if k.strip()]
    all_keys = set(GAME_SPECS.keys())
    unknown = [k for k in requested_keys if k not in all_keys]
    if unknown:
        print(f"ERROR: Unknown game keys: {unknown}. Valid: {sorted(all_keys)}", file=sys.stderr)
        sys.exit(1)

    full_run = set(requested_keys) == all_keys

    print(f"anchor_drama: n={args.n}, games={requested_keys}, seed={args.seed}")
    print(f"Full run (all 4 games): {full_run}")
    print()

    results: list[dict] = []
    for key in requested_keys:
        spec = GAME_SPECS[key]
        print(f"  [{key}] {spec['label']} (family={spec['family']}) — {args.n} rollouts ...", flush=True)
        row = compute_drama_for_game(spec, args.n, args.seed)
        results.append(row)
        print(f"         n_used={row['n_used']}, draws_skipped={row['draws_skipped']}, mean_drama={row['mean_drama']:.4f}")

    print()

    # Table header
    header = f"{'key':<8} {'family':<16} {'n':<6} {'draws_skip':<12} {'mean_drama':<12}"
    sep = "-" * len(header)
    table_lines = [header, sep]
    for row in results:
        table_lines.append(
            f"{row['key']:<8} {row['family']:<16} {row['n_used']:<6} {row['draws_skipped']:<12} {row['mean_drama']:<12.4f}"
        )
    table_str = "\n".join(table_lines)
    print(table_str)
    print()

    # Verdict logic
    if not full_run:
        verdict = "ANCHOR_INCOMPLETE (subset — no verdict)"
        print(verdict)
        print()
        print("NOTE: --games is a subset of {a0,a1,e1453,573}. Rerun with all 4 games for a verdict.")
        # No md written for subset runs.
        return

    # Full run: compute verdict
    by_key = {r["key"]: r for r in results}
    drama_a0 = by_key["a0"]["mean_drama"]
    drama_a1 = by_key["a1"]["mean_drama"]
    drama_e1453 = by_key["e1453"]["mean_drama"]
    drama_573 = by_key["573"]["mean_drama"]

    all_dramas = {
        "a0": drama_a0,
        "a1": drama_a1,
        "e1453": drama_e1453,
        "573": drama_573,
    }
    max_key = max(all_dramas, key=lambda k: all_dramas[k])

    bar_a1_gt_a0 = drama_a1 > drama_a0
    bar_e1453_not_top = (max_key != "e1453")

    print(f"BAR check:")
    print(f"  drama(a1)={drama_a1:.4f} > drama(a0)={drama_a0:.4f} : {bar_a1_gt_a0}")
    print(f"  e1453 NOT ranked top (max is '{max_key}') : {bar_e1453_not_top}")
    print()

    if bar_a1_gt_a0 and bar_e1453_not_top:
        verdict = "DRAMA_ANCHORED"
        verdict_note = (
            "Per-role drama PASSES anchor calibration. May proceed as a screen comparative. "
            "Pass --anchor-result pass to run_screen.py."
        )
    else:
        verdict = "DRAMA_DEMOTED"
        verdict_note = (
            "Per-role drama FAILS anchor calibration. Demoted to diagnostic only. "
            "Screen GO = 2/2 of the remaining comparatives. "
            "Pass --anchor-result demoted to run_screen.py."
        )

    print(verdict)

    # Write anchor_drama.md
    md_path = HERE / "anchor_drama.md"
    md_lines = [
        "# Stage 1.5: Drama Anchor Calibration",
        "",
        f"n={args.n}, seed={args.seed}, games={requested_keys}",
        "",
        "## Results",
        "",
        table_str,
        "",
        "## BAR Check (pre-registered)",
        "",
        f"- drama(a1) > drama(a0): {drama_a1:.4f} > {drama_a0:.4f} → **{bar_a1_gt_a0}**",
        f"- e1453 NOT ranked top (max drama is '{max_key}'): **{bar_e1453_not_top}**",
        "",
        f"## Verdict",
        "",
        f"```",
        verdict,
        f"```",
        "",
        verdict_note,
        "",
        "## Notes",
        "",
        "- n/2 random-pair + n/2 greedy-pair rollouts per game (draws skipped from drama calc).",
        "- a0/e1453: threshold family — per-player progress = effective_score / threshold.",
        "- a1: field_connection family — progress = maker_progress_span (field-controlled axis span).",
        "- 573: connection family — progress = owner_progress_span (board_owners stone axis span).",
        "- metrics.py is pre-registered and was NOT modified; new helpers live only in this file.",
    ]
    md_path.write_text("\n".join(md_lines) + "\n")
    print(f"\nWrote {md_path}")


if __name__ == "__main__":
    main()
