"""Team-15 evaluation helper: play games and also inspect influence field."""
import argparse
import sqlite3

import numpy as np

from game_engine import factory
from game_engine.game_def_v2 import GameDefV2 as GameV2


def load_game(db_path: str, game_id: str) -> GameV2:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT rule_representation FROM games WHERE game_id = ?",
        (game_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise SystemExit(f"Game {game_id} not found in {db_path}")
    import json
    rule = json.loads(row["rule_representation"])
    game = GameV2.from_dict(rule)
    return game


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", required=True)
    ap.add_argument("--game-id", required=True)
    ap.add_argument("--moves", required=True, help="comma-separated action ids")
    args = ap.parse_args()

    game = load_game(args.db_path, args.game_id)
    engine = factory.create_engine(game)
    engine.reset()

    moves = [int(m.strip()) for m in args.moves.split(",") if m.strip()]
    axis = engine.topo.axis_size

    for i, a in enumerate(moves):
        player = engine.current_player
        if a < axis * axis:
            y = a // axis
            x = a % axis
        else:
            y = x = -1
        obs, rew, done, info = engine.step(a)
        print(f"Move {i+1}: P{player} action={a} ({x},{y}) done={done} rew={rew}")
        if done:
            print(f"  Winner: {engine._winner}")
            break

    # Print owners
    print("\nBoard owners (8x8):")
    owners = engine.board_owners.reshape(axis, axis)
    for y in range(axis):
        row_chars = []
        for x in range(axis):
            o = int(owners[y, x])
            row_chars.append("X" if o == 1 else "O" if o == 2 else ".")
        print(f" {y} " + " ".join(row_chars))

    # Print values
    values = engine.board_values.reshape(axis, axis)
    print("\nBoard values (8x8):")
    for y in range(axis):
        row_str = []
        for x in range(axis):
            v = values[y, x]
            row_str.append(f"{v:+.3f}")
        print(f" {y} " + " ".join(row_str))

    # Compute per-player effective win score
    owners_flat = engine.board_owners
    values_flat = engine.board_values
    p1_sum = float(np.sum(values_flat[owners_flat == 1]))
    p2_sum = float(np.sum(values_flat[owners_flat == 2]))
    print(f"\nP1 effective (sum of values on P1 cells):  {p1_sum:+.4f}")
    print(f"P2 effective (negated sum on P2 cells):    {-p2_sum:+.4f}")
    print(f"Threshold: {game.win_condition.threshold:.4f}")
    print(f"Piece counts: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
    print(f"Current player: P{engine.current_player}")
    print(f"Done: {engine.done}, Winner: {engine._winner}")


if __name__ == "__main__":
    main()
