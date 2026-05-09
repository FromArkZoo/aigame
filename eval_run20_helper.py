"""R20 agent-team-eval helper — unified for all 7 Option-C slate games.

All 7 R20 top games share the place-only / influence / threshold-race shape.
Routes a game_id to its R20 DB. Same per-move + end-of-sequence rendering as
eval_run19_helper.py; values render is essential for threshold-race games.

Substrates in this slate:
  - menger:        3D, axis 9, 729 grid cells / 400 active (Hausdorff 2.727)
  - sierpinski:    2D, axis 9,  81 grid cells /  64 active (Hausdorff 1.893)  [carpet]
  - grid:          2D, axis 9,  81 grid cells /  81 active (control, no fractal holes)

Holes are rendered as `#`, empty active cells as `.`, P1 as `X`, P2 as `O`.

Usage:
    .venv/bin/python eval_run20_helper.py --game a6385db22c0b [--moves "21,42,..."] [--values]

Game IDs (Option-C 7-game slate from evaluation_report_run20.md):
    Menger top-5:  a6385db22c0b  b160b1f55378  5f5c72e15220  d1dbc6568fc7  f98b9414f638
    Carpet top-1:  625bfc1f3f49
    Grid top-1:    fcedbc14043d

The DB is auto-selected from substrate. Override with --db PATH if needed.

Per-move output:
  - decoded action (PLACE @ (x,y[,z]) or PASS)
  - captures (cells cleared / flipped since previous owner snapshot)
  - piece counts, P1/P2 effective scores, distance to threshold
  - termination flags (Done, Winner)

End-of-sequence output:
  - rendered board (per z-layer for menger)
  - optional influence-field render (--values)
  - top-K greedy moves for the side to move
"""
import argparse
import json
import sqlite3
import sys
from typing import List, Tuple

import numpy as np

from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2

MENGER_DB = "genesis_v2_run20_menger.db"
CARPET_DB = "genesis_v2_run20_carpet.db"
GRID_DB = "genesis_v2_run20_grid_control.db"

GAME_TO_DB = {
    "a6385db22c0b": MENGER_DB,
    "b160b1f55378": MENGER_DB,
    "5f5c72e15220": MENGER_DB,
    "d1dbc6568fc7": MENGER_DB,
    "f98b9414f638": MENGER_DB,
    "625bfc1f3f49": CARPET_DB,
    "fcedbc14043d": GRID_DB,
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


def header(game, threshold: float) -> str:
    topo = game.get_topology()
    cap = game.capture_rule
    prop = game.propagation_rule
    return (
        f"Substrate: {game.topology_type} | "
        f"axis={game.axis_size} dims={game.num_dimensions} | "
        f"active_cells={topo.num_active_cells} / total_cells={topo.total_cells} | "
        f"max_degree={topo.max_degree} | pie_rule={game.pie_rule}\n"
        f"Capture: {cap.capture_type}, threshold={cap.threshold}\n"
        f"Propagation: {prop.prop_type}, r={prop.radius}, "
        f"strength={prop.strength:.4f}, decay={prop.decay:.4f}\n"
        f"Win: threshold-race > {threshold:.3f} | "
        f"max_turns={game.win_condition.max_turns}\n"
        f"Actions: {game.action_rule.action_types} | num_actions={game.num_actions}"
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game", required=True, help="game_id (e.g. a6385db22c0b)")
    p.add_argument("--db", default=None, help="DB path (auto from game_id if omitted)")
    p.add_argument("--moves", default="", help="csv of action ids; empty=initial state")
    p.add_argument("--values", action="store_true", help="render influence field")
    args = p.parse_args()

    db = args.db or GAME_TO_DB.get(args.game)
    if db is None:
        sys.exit(f"!! unknown game {args.game}; pass --db explicitly")

    game = load_rules(args.game, db)
    engine = create_engine(game)
    topo = game.get_topology()
    threshold = game.win_condition.threshold

    print(f"=== Game {args.game} ({db}) ===")
    print(header(game, threshold))

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
        print(
            f"    Scores: P1={p1:+.3f}  P2={p2:+.3f}  "
            f"P1_to_threshold={threshold - p1:+.3f}  "
            f"P2_to_threshold={threshold - p2:+.3f}"
        )

    print("\n=== Final board (X=P1, O=P2, .=empty active, #=hole) ===")
    print(render_board(engine, game))
    if args.values:
        print("=== Influence field (board_values) ===")
        print(render_values(engine, game))
    p1, p2 = compute_scores(engine, game)
    print(f"P1 effective score = {p1:+.3f}   (need > {threshold:.3f})")
    print(f"P2 effective score = {p2:+.3f}   (need > {threshold:.3f})")
    print(
        f"Done: {engine.done}  Winner: {engine._winner}  Step#: {engine.step_count}  "
        f"Next: P{engine.current_player}"
    )
    print(f"\nLegal actions: {len(engine.get_legal_actions())}")
    if not engine.done:
        topk = greedy_topk(engine, game, 8)
        print(f"\nTop-8 greedy moves for P{engine.current_player}:")
        for a, d in topk:
            print(f"   {decode(game, topo, a):28s}  Δscore≈{d:+.3f}")


if __name__ == "__main__":
    main()
