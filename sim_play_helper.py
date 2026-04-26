"""Simultaneous play helper for team-pilot R15 evaluation.

Handles sim turn structure (two moves per round via step_simultaneous),
renders influence field, and prints threshold progress.
"""
import sys
import argparse
import json
import sqlite3
import numpy as np
from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2


def load_game(db_path, game_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?", (game_id,)).fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"Game {game_id} not found")
    rules = json.loads(row["rule_representation"])
    return GameDefV2.from_dict(rules)


def render(engine, game, show_values=False):
    size = game.axis_size
    lines = [f"  Board ({size}x{size}) torus  P1=X  P2=O  .=empty"]
    header = "     " + " ".join(f"{x:>2}" for x in range(size))
    lines.append(header)
    for y in range(size):
        row = f"  {y:>2} "
        for x in range(size):
            c = y * size + x
            v = int(engine.board_owners[c])
            row += " X" if v == 1 else (" O" if v == 2 else " .")
            row += " "
        lines.append(row)
    lines.append(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
    # Threshold progress
    thr = game.win_condition.threshold
    vals = engine.board_values
    owns = engine.board_owners
    p1_score = sum(vals[c] for c in range(game.total_cells) if owns[c] == 1)
    p2_score = -sum(vals[c] for c in range(game.total_cells) if owns[c] == 2)
    lines.append(f"  Threshold={thr:.3f}  P1_own_sum={p1_score:+.3f}  P2_own_sum={p2_score:+.3f}")

    if show_values:
        lines.append("  Influence field (signed; + favors P1, - favors P2):")
        for y in range(size):
            row = f"  {y:>2} "
            for x in range(size):
                c = y * size + x
                row += f"{vals[c]:+5.2f} "
            lines.append(row)
    return "\n".join(lines)


def coord_str(a, size, total_cells):
    if a == total_cells:
        return "PASS"
    return f"a{a}({a % size},{a // size})"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", default="genesis_v2_run15.db")
    p.add_argument("--game-id", required=True)
    # Rounds: comma-separated "p1:p2" pairs, e.g. "27:36,28:35"
    # Use "pass" for the pass action
    p.add_argument("--rounds", default="")
    p.add_argument("--show-legal", action="store_true")
    p.add_argument("--show-values", action="store_true")
    args = p.parse_args()

    game = load_game(args.db_path, args.game_id)
    engine = create_engine(game)
    engine.reset()

    print(render(engine, game, show_values=args.show_values))

    if args.rounds:
        rounds = []
        for token in args.rounds.split(","):
            token = token.strip()
            if not token:
                continue
            a, b = token.split(":")
            def parse(x):
                x = x.strip().lower()
                if x == "pass":
                    return game.total_cells
                return int(x)
            rounds.append((parse(a), parse(b)))

        for i, (a1, a2) in enumerate(rounds, 1):
            legal_p1 = engine.get_legal_actions(player=1)
            legal_p2 = engine.get_legal_actions(player=2)
            if a1 not in legal_p1:
                print(f"\n!!! Round {i}: action {a1} ILLEGAL for P1. Legal head: {legal_p1[:20]}")
                break
            if a2 not in legal_p2:
                print(f"\n!!! Round {i}: action {a2} ILLEGAL for P2. Legal head: {legal_p2[:20]}")
                break
            obs, rewards, done, info = engine.step_simultaneous(a1, a2)
            print(f"\n--- Round {i}: P1={coord_str(a1,game.axis_size,game.total_cells)}  P2={coord_str(a2,game.axis_size,game.total_cells)}  collision={info.get('collision')} ---")
            print(render(engine, game, show_values=args.show_values))
            if done:
                w = info.get("winner")
                if w is not None:
                    print(f"\n*** GAME OVER: Player {w+1} wins! ***")
                else:
                    print(f"\n*** GAME OVER: Draw ***")
                print(f"  Rewards: P1={rewards[0]:.2f} P2={rewards[1]:.2f}")
                print(f"  Step count: {engine.step_count}")
                break

    if args.show_legal:
        l1 = engine.get_legal_actions(player=1)
        l2 = engine.get_legal_actions(player=2)
        print(f"\nLegal for P1 ({len(l1)} total): {l1[:30]}")
        print(f"Legal for P2 ({len(l2)} total): {l2[:30]}")

    print(f"\nStep count: {engine.step_count}, max turns: {game.max_game_steps}")
    thr = game.win_condition.threshold
    print(f"Threshold: {thr:.4f}")


if __name__ == "__main__":
    main()
