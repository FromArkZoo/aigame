"""Simultaneous play helper for team-18 evaluation of game 992bf7dfc9f4."""
import sys
import argparse
import json
import sqlite3
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


def render(engine, game):
    size = game.axis_size
    lines = [f"  Board ({size}x{size})  P1=X  P2=O  .=empty"]
    header = "   " + " ".join(f"{x}" for x in range(size))
    lines.append(header)
    for y in range(size):
        row = f" {y} "
        for x in range(size):
            c = y * size + x
            v = int(engine.board_owners[c])
            row += "X " if v == 1 else ("O " if v == 2 else ". ")
        lines.append(row)
    lines.append(f"  Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}")
    return "\n".join(lines)


def legal_for(engine, player):
    return engine.get_legal_actions(player=player)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", default="genesis_v2_run14.db")
    p.add_argument("--game-id", required=True)
    # Rounds: comma-separated "p1:p2" pairs, e.g. "27:36,28:35"
    p.add_argument("--rounds", default="")
    p.add_argument("--show-legal", action="store_true")
    args = p.parse_args()

    game = load_game(args.db_path, args.game_id)
    engine = create_engine(game)
    engine.reset()

    print(render(engine, game))

    if args.rounds:
        rounds = []
        for token in args.rounds.split(","):
            token = token.strip()
            if not token:
                continue
            a, b = token.split(":")
            rounds.append((int(a.strip()), int(b.strip())))

        for i, (a1, a2) in enumerate(rounds, 1):
            legal_p1 = engine.get_legal_actions(player=1)
            legal_p2 = engine.get_legal_actions(player=2)
            if a1 not in legal_p1:
                print(f"\n!!! Round {i}: action {a1} ILLEGAL for P1. Legal: {legal_p1[:20]}{'...' if len(legal_p1) > 20 else ''}")
                break
            if a2 not in legal_p2:
                print(f"\n!!! Round {i}: action {a2} ILLEGAL for P2. Legal: {legal_p2[:20]}{'...' if len(legal_p2) > 20 else ''}")
                break
            obs, rewards, done, info = engine.step_simultaneous(a1, a2)
            size = game.axis_size
            def coord(a):
                if a == game.total_cells:
                    return "PASS"
                return f"cell {a} ({a % size},{a // size})"
            print(f"\n--- Round {i}: P1={coord(a1)}  P2={coord(a2)}  collision={info.get('collision')} ---")
            print(render(engine, game))
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
        print(f"\nLegal for P1 ({len(l1)} total): {l1[:30]}{'...' if len(l1) > 30 else ''}")
        print(f"Legal for P2 ({len(l2)} total): {l2[:30]}{'...' if len(l2) > 30 else ''}")

    print(f"\nStep count: {engine.step_count}, max turns: {game.max_game_steps}")
    print(f"Territory threshold: {game.win_condition.threshold:.4f} ({int(game.win_condition.threshold * game.total_cells) + 1}/{game.total_cells} cells to win)")


if __name__ == "__main__":
    main()
