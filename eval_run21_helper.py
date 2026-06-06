"""R21 agent-team-eval helper — unified for all 7 Option-C slate games.

Routes a game_id to its R21 DB and AUTO-APPLIES the game's calibrated komi_p2
(from experiments/r21_komi_calibration/r21_komi_calibrated.md — the smallest
komi bringing post-pie mirror seat bias < 0.10, per G3). Teams therefore play
the seat-balanced version. Same per-move + end-of-sequence rendering as
eval_run20_helper.py.

Fix vs R20 helper (R8-replay finding): the win line now dispatches on
win_condition.condition_type — connection-win games (573562833174) are no
longer mislabelled "threshold-race", and their vestigial threshold field is
called out.

Substrates:
  - menger:     3D, axis 9, 729 grid cells / 400 active (Hausdorff 2.727)
  - sierpinski: 2D, axis 9,  81 grid cells /  64 active (Hausdorff 1.893) [carpet]
  - grid:       2D, axis 9,  81 grid cells /  81 active (flat control)

Holes render as `#`, empty active cells `.`, P1 `X`, P2 `O`.

Usage:
    .venv/bin/python eval_run21_helper.py --game e1453dac5445 [--moves "21,42,..."] [--values]

Game IDs (Option-C 7-game slate, evaluation_report_run21.md + analysis_post_r21.md):
    Menger:  e1453dac5445(top) e52e8889517a bfd1bb7ced76 1fea3357dca4
    Carpet:  d995cf010504(top)
    Grid:    b12ff78f1c1d(top, gen-5 child) 573562833174(R8-revival, G6)

The DB + komi are auto-selected from game_id. Override DB with --db, komi with --komi.
"""
import argparse
import json
import sqlite3
import sys
from typing import List, Tuple

import numpy as np

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2

MENGER_DB = "genesis_v2_run21_menger.db"
CARPET_DB = "genesis_v2_run21_carpet.db"
GRID_DB = "genesis_v2_run21_grid.db"

GAME_TO_DB = {
    "e1453dac5445": MENGER_DB,
    "e52e8889517a": MENGER_DB,
    "bfd1bb7ced76": MENGER_DB,
    "1fea3357dca4": MENGER_DB,
    "d995cf010504": CARPET_DB,
    "b12ff78f1c1d": GRID_DB,
    "573562833174": GRID_DB,
}

# Calibrated komi_p2 per game (bias-minimizing value < 0.10 per G3 gate;
# 573562833174 is rush-broken at every komi — left at 0.0, flagged in briefing).
GAME_TO_KOMI = {
    "e1453dac5445": 0.00,
    "e52e8889517a": 0.05,
    "bfd1bb7ced76": 0.00,
    "1fea3357dca4": 0.05,
    "d995cf010504": 0.05,
    "b12ff78f1c1d": 0.05,
    "573562833174": 0.00,
}


def load_rules(game_id: str, db: str):
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT rule_representation FROM games WHERE game_id=?", (game_id,)
    ).fetchone()
    conn.close()
    if row is None:
        sys.exit(f"!! game {game_id} not found in {db}")
    return GameDefV2.from_dict(json.loads(row[0]))


def fmt_cell(topo, c: int) -> str:
    coords = topo.cell_to_coords(c)
    return "(" + ",".join(str(v) for v in coords) + ")"


def decode(game, topo, a: int) -> str:
    if a < game.total_cells:
        return f"PLACE @ {fmt_cell(topo, a)} [cell {a}]"
    if a == game.total_cells:
        return "PASS"
    if game.pie_rule and a == game.total_cells + 1:
        return "PIE (swap seats)"
    return f"<unknown action {a}>"


def render_board(engine, game) -> str:
    topo = game.get_topology()
    n = game.axis_size
    is_3d = game.num_dimensions == 3
    active = set(topo.active_cells)
    out = []
    z_range = range(n) if is_3d else [None]
    for z in z_range:
        if is_3d:
            out.append(f"  z={z} layer:")
        out.append("        x=" + "  ".join(str(x) for x in range(n)))
        for y in range(n):
            row = [f"   y={y}"]
            for x in range(n):
                c = topo.coords_to_cell((x, y, z) if is_3d else (x, y))
                if c not in active:
                    row.append(" # ")
                else:
                    v = engine.board_owners[c]
                    row.append(" X " if v == 1 else (" O " if v == 2 else " . "))
            out.append("  ".join(row))
        out.append("")
    return "\n".join(out)


def render_values(engine, game) -> str:
    topo = game.get_topology()
    n = game.axis_size
    is_3d = game.num_dimensions == 3
    active = set(topo.active_cells)
    out = []
    z_range = range(n) if is_3d else [None]
    for z in z_range:
        if is_3d:
            out.append(f"  z={z} influence:")
        for y in range(n):
            row = [f"   y={y}"]
            for x in range(n):
                c = topo.coords_to_cell((x, y, z) if is_3d else (x, y))
                if c not in active:
                    row.append("  ###")
                else:
                    row.append(f"{engine.board_values[c]:+5.2f}")
            out.append(" ".join(row))
        out.append("")
    return "\n".join(out)


def compute_scores(engine, game) -> Tuple[float, float]:
    topo = game.get_topology()
    p1 = 0.0
    p2 = 0.0
    for c in topo.active_cells:
        owner = int(engine.board_owners[c])
        v = float(engine.board_values[c])
        if owner == 1:
            p1 += v
        elif owner == 2:
            p2 += -v
    # komi (engine_v2.py:_check_threshold/_check_count): P2's effective score
    # gains komi_p2 * threshold (threshold-race) or komi_p2 * num_active_cells
    # (count-based). NOT the flat komi_p2 fraction.
    komi_frac = float(getattr(game, "komi_p2", 0.0))
    wc = game.win_condition
    if getattr(wc, "condition_type", "threshold") == "threshold":
        p2 += komi_frac * float(wc.threshold)
    else:
        p2 += komi_frac * topo.num_active_cells
    return p1, p2


def diff_owners(prev: List[int], cur: np.ndarray) -> Tuple[List[int], List[int]]:
    cleared, flipped = [], []
    for c, p in enumerate(prev):
        n = int(cur[c])
        if p != 0 and n == 0:
            cleared.append(c)
        elif p in (1, 2) and n in (1, 2) and p != n:
            flipped.append(c)
    return cleared, flipped


def greedy_topk(engine, game, k: int = 8):
    topo = game.get_topology()
    legal = engine.get_legal_actions()
    cur = engine.current_player
    rule = game.propagation_rule
    if getattr(rule, "prop_type", "none") == "none":
        return []  # no influence field to hill-climb (e.g. connection games)
    radius = rule.radius
    strength = rule.strength
    decay = rule.decay
    sign = +1 if cur == 1 else -1

    candidates = []
    for a in legal:
        if a >= game.total_cells:
            continue
        delta_eff = 0.0
        cells_in = topo.cells_within_radius(a, radius)
        for cell in cells_in:
            d = topo.distance(a, cell)
            mag = strength * (decay ** d)
            owner = int(engine.board_owners[cell])
            new_val = float(engine.board_values[cell]) + sign * mag
            if cell == a:
                delta_eff += new_val if cur == 1 else -new_val
            else:
                if owner == cur:
                    delta_eff += (new_val if cur == 1 else -new_val) - (
                        float(engine.board_values[cell]) if cur == 1 else -float(engine.board_values[cell])
                    )
        candidates.append((a, delta_eff))
    candidates.sort(key=lambda t: -t[1])
    return candidates[:k]


def header(game) -> str:
    topo = game.get_topology()
    cap = game.capture_rule
    prop = game.propagation_rule
    wc = game.win_condition
    komi = float(getattr(game, "komi_p2", 0.0))

    if getattr(prop, "prop_type", "none") == "none":
        prop_line = "Propagation: none (no influence field)"
    else:
        prop_line = (
            f"Propagation: {prop.prop_type}, r={prop.radius}, "
            f"strength={prop.strength:.4f}, decay={prop.decay:.4f}"
        )

    ctype = getattr(wc, "condition_type", "threshold")
    if ctype == "threshold":
        win_line = (
            f"Win: threshold-race | P-effective owned-influence > {wc.threshold:.3f} "
            f"| target_dimension_p2={wc.target_dimension_p2} "
            f"(-1 => P2 mirrors P1's accumulator)"
        )
    elif ctype == "connection":
        win_line = (
            "Win: CONNECTION (complete a connecting path of own stones) "
            f"| threshold field ({wc.threshold:.3f}) is VESTIGIAL under connection-win"
        )
    else:
        win_line = f"Win: {ctype} | threshold={wc.threshold:.3f}"

    return (
        f"Substrate: {game.topology_type} | "
        f"axis={game.axis_size} dims={game.num_dimensions} | "
        f"active_cells={topo.num_active_cells} / total_cells={topo.total_cells} | "
        f"max_degree={topo.max_degree} | pie_rule={game.pie_rule} | "
        f"komi_p2={komi:.2f}\n"
        f"Capture: {cap.capture_type}, threshold={cap.threshold}\n"
        f"{prop_line}\n"
        f"{win_line} | max_turns={wc.max_turns}\n"
        f"Actions: {game.action_rule.action_types} | num_actions={game.num_actions}"
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game", required=True, help="game_id (e.g. e1453dac5445)")
    p.add_argument("--db", default=None, help="DB path (auto from game_id if omitted)")
    p.add_argument("--komi", type=float, default=None,
                   help="override komi_p2 (auto from game_id if omitted)")
    p.add_argument("--moves", default="", help="csv of action ids; empty=initial state")
    p.add_argument("--values", action="store_true", help="render influence field")
    args = p.parse_args()

    db = args.db or GAME_TO_DB.get(args.game)
    if db is None:
        sys.exit(f"!! unknown game {args.game}; pass --db explicitly")

    game = load_rules(args.game, db)
    komi = args.komi if args.komi is not None else GAME_TO_KOMI.get(args.game, 0.0)
    game.komi_p2 = float(komi)
    engine = create_engine(game)
    topo = game.get_topology()
    wc = game.win_condition
    is_threshold = getattr(wc, "condition_type", "threshold") == "threshold"
    applied_komi = komi * float(wc.threshold) if is_threshold else komi * topo.num_active_cells

    print(f"=== Game {args.game} ({db}, komi_p2={komi:.2f} -> P2 effective bonus {applied_komi:+.2f}) ===")
    print(header(game))

    moves = [int(x) for x in args.moves.split(",") if x.strip()]
    for i, a in enumerate(moves):
        cur_player = engine.current_player
        legal = engine.get_legal_actions()
        if a not in legal:
            print(f"\n!! Move {i+1} action {a} ILLEGAL for P{cur_player}.")
            print(f"   Decoded: {decode(game, topo, a)}")
            print(f"   Legal count: {len(legal)} (sample: {legal[:12]}...)")
            sys.exit(2)
        prev = list(engine.board_owners)
        engine.step(a)
        cleared, flipped = diff_owners(prev, engine.board_owners)
        p1, p2 = compute_scores(engine, game)
        n_p1 = int(engine.piece_counts[0])
        n_p2 = int(engine.piece_counts[1])
        print(f"\n--- Turn {i+1} (P{cur_player}): action {a} = {decode(game, topo, a)}")
        if cleared:
            print(f"    Captures (cleared to empty): {[fmt_cell(topo, c) for c in cleared]}")
        if flipped:
            print(f"    Captures (flipped owner): {[fmt_cell(topo, c) for c in flipped]}")
        print(
            f"    Pieces: P1={n_p1}  P2={n_p2}  Step#={engine.step_count}  "
            f"Done={engine.done}  Winner={engine._winner}"
        )
        if is_threshold:
            print(
                f"    Scores: P1={p1:+.3f}  P2={p2:+.3f} (incl P2 komi {applied_komi:+.2f})  "
                f"P1_to_threshold={wc.threshold - p1:+.3f}  "
                f"P2_to_threshold={wc.threshold - p2:+.3f}"
            )
        else:
            print(f"    (connection-win: watch the board for a completed path; "
                  f"influence scores not the win metric)")

    print("\n=== Final board (X=P1, O=P2, .=empty active, #=hole) ===")
    print(render_board(engine, game))
    if args.values and getattr(game.propagation_rule, "prop_type", "none") != "none":
        print("=== Influence field (board_values) ===")
        print(render_values(engine, game))
    p1, p2 = compute_scores(engine, game)
    if is_threshold:
        print(f"P1 effective score = {p1:+.3f}   (need > {wc.threshold:.3f})")
        print(f"P2 effective score = {p2:+.3f}   (incl P2 komi {applied_komi:+.2f}; need > {wc.threshold:.3f})")
    print(
        f"Done: {engine.done}  Winner: {engine._winner}  Step#: {engine.step_count}  "
        f"Next: P{engine.current_player}"
    )
    print(f"\nLegal actions: {len(engine.get_legal_actions())}")
    if not engine.done:
        topk = greedy_topk(engine, game, 8)
        if topk:
            print(f"\nTop-8 greedy moves for P{engine.current_player} (influence-delta only; ignores captures):")
            for a, d in topk:
                print(f"   {decode(game, topo, a):28s}  Δscore≈{d:+.3f}")


if __name__ == "__main__":
    main()
