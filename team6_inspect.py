"""Helper to play a sequence of moves and inspect influence values."""
import sys
import argparse
import json
import sqlite3
import numpy as np
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def load_game(db_path, game_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)).fetchone()
    conn.close()
    rules = json.loads(row["rule_representation"])
    return GameDefV2.from_dict(rules)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", required=True)
    ap.add_argument("--game-id", required=True)
    ap.add_argument("--moves", default="", help="comma-separated actions")
    args = ap.parse_args()

    game = load_game(args.db_path, args.game_id)
    engine = create_engine(game)
    engine.reset()

    if args.moves.strip():
        actions = [int(m) for m in args.moves.split(",") if m.strip()]
    else:
        actions = []

    for a in actions:
        if engine.done:
            print(f"GAME OVER before action {a}; winner={engine._winner}")
            break
        engine.step(a)

    # Print board
    axis = game.axis_size
    print(f"\nBoard (owners), axis={axis}, topology={game.topology_type}")
    print("   " + " ".join(f"{x:5d}" for x in range(axis)))
    for y in range(axis):
        row = []
        for x in range(axis):
            c = y * axis + x
            o = int(engine.board_owners[c])
            s = {0: " .   ", 1: " X   ", 2: " O   "}[o]
            row.append(s)
        print(f"{y:2d} " + "".join(row))

    print(f"\nPiece counts: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
    print(f"Current player to move: {engine.current_player}")
    print(f"Done: {engine.done}, Winner: {engine._winner}")
    print(f"Consecutive passes: {engine.consecutive_passes}")

    # Print board_values
    print("\nBoard values (influence field):")
    print("   " + " ".join(f"{x:6d}" for x in range(axis)))
    for y in range(axis):
        row = []
        for x in range(axis):
            c = y * axis + x
            v = float(engine.board_values[c])
            row.append(f"{v:+6.2f}")
        print(f"{y:2d} " + " ".join(row))

    # Compute effective influence totals per side
    p1_total = sum(float(engine.board_values[c]) for c in range(engine.total_cells) if int(engine.board_owners[c]) == 1)
    p2_total_signed = sum(float(engine.board_values[c]) for c in range(engine.total_cells) if int(engine.board_owners[c]) == 2)
    p2_effective = -p2_total_signed  # since p2's values are negative
    threshold = game.win_condition.threshold
    print(f"\nThreshold target: {threshold:.4f}")
    print(f"P1 total influence on own cells: {p1_total:+.4f}  (remaining: {threshold - p1_total:+.4f})")
    print(f"P2 effective influence on own cells: {p2_effective:+.4f}  (remaining: {threshold - p2_effective:+.4f})")


if __name__ == "__main__":
    main()
