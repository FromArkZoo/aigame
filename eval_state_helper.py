#!/usr/bin/env python3
"""Helper to play moves and show full state (board, owners, values, threshold sums)."""
import argparse
import json
import sqlite3
import sys

from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default="genesis_v2_run14.db")
    parser.add_argument("--game-id", required=True)
    parser.add_argument("--moves", default="")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db_path)
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", (args.game_id,)).fetchone()
    conn.close()
    rules = json.loads(row[0])
    game = GameDefV2.from_dict(rules)
    engine = create_engine(game)
    engine.reset()

    moves = [int(m.strip()) for m in args.moves.split(",") if m.strip()]
    done = False
    winner = None
    for i, m in enumerate(moves):
        legal = engine.get_legal_actions()
        if m not in legal:
            print(f"ILLEGAL move {m} at step {i+1}")
            sys.exit(1)
        obs, rewards, done, info = engine.step(m)
        if done:
            winner = info.get("winner")
            print(f"*** GAME OVER after move {i+1} (player {(i%2)+1} played {m}) ***")
            print(f"Winner: {winner+1 if winner is not None else 'Draw'}")
            print(f"Final rewards: {rewards}")
            break

    # Print board owners
    size = game.axis_size
    print("\n  Board (X=P1, O=P2):")
    print("     " + " ".join(f"{c:>2}" for c in range(size)))
    for row in range(size):
        cells = []
        for col in range(size):
            idx = row * size + col
            o = engine.board_owners[idx]
            cells.append(" X" if o == 1 else " O" if o == 2 else " .")
        print(f"  {row:>2}" + "".join(cells))

    print(f"\nPieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
    print(f"Current player: {engine.current_player}")
    print(f"Turn/step: {engine.turn_count if hasattr(engine,'turn_count') else 'n/a'}")

    # Print board_values
    print("\n  Board values (positive = P1 influence, negative = P2):")
    print("     " + " ".join(f"{c:>6}" for c in range(size)))
    for row in range(size):
        vals = []
        for col in range(size):
            idx = row * size + col
            vals.append(f"{engine.board_values[idx]:+6.2f}")
        print(f"  {row:>2} " + " ".join(vals))

    # Threshold sums
    p1_sum = sum(engine.board_values[c] for c in range(game.total_cells) if engine.board_owners[c] == 1)
    p2_sum = -sum(engine.board_values[c] for c in range(game.total_cells) if engine.board_owners[c] == 2)
    print(f"\nThreshold sums:")
    print(f"  P1 effective: {p1_sum:.3f}  (target > {game.win_condition.threshold:.3f})")
    print(f"  P2 effective: {p2_sum:.3f}  (target > {game.win_condition.threshold:.3f})")
    print(f"  Total placements so far: {len(moves)}")
    print(f"  Consecutive passes: {engine.consecutive_passes}")
    if not done:
        print(f"  Game continues. Next to play: P{engine.current_player}")


if __name__ == "__main__":
    main()
