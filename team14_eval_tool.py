"""Helper to inspect board_values and P1/P2 threshold totals after a move sequence.
Usage: .venv/bin/python team14_eval_tool.py --game-id 931c58ae59b4 --moves "27,28,26,..."
"""
import argparse
import sqlite3
import json
import sys
import numpy as np

from game_engine.game_def_v2 import GameDefV2  # type: ignore
from game_engine.engine_v2 import GameEngineV2  # type: ignore


def load_rules(db_path: str, game_id: str) -> dict:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT rule_representation FROM games WHERE game_id=?", (game_id,))
    row = cur.fetchone()
    con.close()
    if row is None:
        print(f"Game {game_id} not found", file=sys.stderr)
        sys.exit(1)
    return json.loads(row[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", default="genesis_v2_run14.db")
    ap.add_argument("--game-id", required=True)
    ap.add_argument("--moves", default="")
    args = ap.parse_args()

    rules = load_rules(args.db_path, args.game_id)
    game = GameDefV2.from_dict(rules)
    engine = GameEngineV2(game)
    engine.reset()

    moves = [int(m) for m in args.moves.split(",") if m.strip()]
    for i, mv in enumerate(moves):
        obs, reward, done, info = engine.step(mv)
        if done:
            print(f"Game ended after move {i+1} (action {mv}). Winner: {engine._winner}")
            break

    axis = game.axis_size
    total = game.total_cells
    bv = engine.board_values
    owners = engine.board_owners

    p1_cells_total = sum(bv[c] for c in range(total) if owners[c] == 1)
    p2_cells_total = sum(bv[c] for c in range(total) if owners[c] == 2)
    # Effective per _check_threshold: P1 effective = sum_over_p1_cells(bv); P2 effective = -sum_over_p2_cells(bv)
    p1_eff = p1_cells_total
    p2_eff = -p2_cells_total

    # Per winners logic threshold
    thresh = game.win_condition.threshold
    maxturns = game.win_condition.max_turns

    print(f"After {len(moves)} moves. Current player: {engine.current_player}  Done: {engine.done}  Winner: {engine._winner}")
    print(f"Piece counts: P1={engine.piece_counts[0]}  P2={engine.piece_counts[1]}  PassStreak={engine.consecutive_passes}")
    print(f"P1 effective threshold score: {p1_eff:.4f} / {thresh:.4f}")
    print(f"P2 effective threshold score: {p2_eff:.4f} / {thresh:.4f}")
    print(f"Max turns: {maxturns}. Current step_count={engine.step_count}")
    print()
    # Print board with values
    print("  Board owners (X=P1 O=P2 .=empty):")
    for y in range(axis):
        row = []
        for x in range(axis):
            c = y * axis + x
            o = owners[c]
            row.append("X" if o == 1 else ("O" if o == 2 else "."))
        print(" ", " ".join(row))
    print()
    print("  Board values (signed):")
    for y in range(axis):
        row = []
        for x in range(axis):
            c = y * axis + x
            row.append(f"{bv[c]:+.2f}")
        print(" ", "  ".join(row))


if __name__ == "__main__":
    main()
