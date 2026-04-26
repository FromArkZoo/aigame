"""Team-pilot evaluation helper for Run 16 game 8d12c8b92b71.

Usage:
    .venv/bin/python team_pilot_helper.py --moves "10,25,11"
    .venv/bin/python team_pilot_helper.py --moves "..." --show-values
    .venv/bin/python team_pilot_helper.py --moves "..." --show-totals
"""

import argparse
import json
import sqlite3
import sys
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


DB_PATH = "/Users/jamesbrowne/aigame/genesis_v2_run16.db"
GAME_ID = "8d12c8b92b71"


def load_game(db_path: str, game_id: str) -> GameDefV2:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)
    ).fetchone()
    conn.close()
    rules = json.loads(row["rule_representation"])
    return GameDefV2.from_dict(rules)


def cell_xy(topo, cell):
    return topo.cell_to_coords(cell)


def render_board(engine, game, show_values=False):
    topo = game.get_topology()
    size = game.axis_size
    lines = []
    lines.append(f"  Board ({size}x{size}) hex  Player 1=X  Player 2=O  Empty=.")
    lines.append("  " + " ".join(f"{c:>2}" for c in range(size)))
    for row in range(size):
        cells = []
        for col in range(size):
            idx = topo.coords_to_cell((col, row))
            owner = engine.board_owners[idx]
            if owner == 1:
                cells.append(" X")
            elif owner == 2:
                cells.append(" O")
            else:
                cells.append(" .")
        # Indent odd rows for hex visualization
        indent = " " if row % 2 == 1 else ""
        lines.append(f"{row:>2}{indent}" + "".join(cells))
    if show_values:
        lines.append("\nBoard influence values (X positive, O negative):")
        for row in range(size):
            cells_str = []
            for col in range(size):
                idx = topo.coords_to_cell((col, row))
                v = engine.board_values[idx]
                cells_str.append(f"{v:+5.2f}")
            indent = "   " if row % 2 == 1 else ""
            lines.append(f"{row:>2}{indent} " + " ".join(cells_str))
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--moves", default="")
    p.add_argument("--show-values", action="store_true")
    p.add_argument("--show-totals", action="store_true")
    p.add_argument("--show-legal", action="store_true")
    args = p.parse_args()

    game = load_game(DB_PATH, GAME_ID)
    engine = create_engine(game)
    engine.reset()

    moves = [int(m.strip()) for m in args.moves.split(",") if m.strip()]
    topo = game.get_topology()
    threshold = game.win_condition.threshold

    print(f"Threshold: {threshold:.4f}")
    print(f"Initial player: {engine.current_player}")
    print()

    for i, action in enumerate(moves):
        player = engine.current_player
        legal = list(engine.get_legal_actions())
        if action not in legal:
            print(f"Move {i+1}: action {action} ILLEGAL for player {player}")
            print(f"  Legal subset: {legal[:20]}")
            sys.exit(1)
        if action < 64:
            x, y = cell_xy(topo, action)
            print(f"Move {i+1}: P{player} -> action {action} = ({x},{y})")
        else:
            print(f"Move {i+1}: P{player} -> PASS")
        obs, rew, done, info = engine.step(action)
        # Compute current totals
        p1_tot = sum(
            engine.board_values[c]
            for c in range(64)
            if engine.board_owners[c] == 1
        )
        p2_tot = sum(
            engine.board_values[c]
            for c in range(64)
            if engine.board_owners[c] == 2
        )
        # P1 effective is p1_tot, P2 effective is -p2_tot
        print(
            f"  P1 effective={p1_tot:+.3f} (own cells), P2 effective={-p2_tot:+.3f} (own cells)"
        )
        print(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
        if done:
            print(f"  GAME OVER: winner={engine._winner}")
            break

    print()
    print(render_board(engine, game, show_values=args.show_values))

    if args.show_totals:
        p1_tot = sum(
            engine.board_values[c]
            for c in range(64)
            if engine.board_owners[c] == 1
        )
        p2_tot = sum(
            engine.board_values[c]
            for c in range(64)
            if engine.board_owners[c] == 2
        )
        print(f"\nP1 total on own cells: {p1_tot:+.4f} (threshold {threshold:.4f})")
        print(f"P2 total on own cells: {p2_tot:+.4f} (effective {-p2_tot:+.4f})")
        print(f"Done: {engine.done}, winner: {engine._winner}")

    if args.show_legal and not engine.done:
        legal = list(engine.get_legal_actions())
        print(f"\nNext to move: P{engine.current_player}")
        print(f"Legal: {len(legal)} actions ({sum(1 for a in legal if a<64)} placements + pass)")


if __name__ == "__main__":
    main()
