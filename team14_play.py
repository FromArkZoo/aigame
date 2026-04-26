"""Team-14 play harness for game c6bb58075520.

Plays a sequence of moves (alternating) and reports board, board_values,
piece counts, P1/P2 effective scores, captures, and game-over status.
"""
import sys
import argparse

sys.path.insert(0, '/Users/jamesbrowne/aigame')
from play_helper import load_game
from game_engine.factory import create_engine
import numpy as np


def play(game_id: str, moves: list[int], db: str = 'genesis_v2_run16.db') -> None:
    g = load_game(db, game_id)
    e = create_engine(g)
    for i, m in enumerate(moves):
        legal = e.get_legal_actions()
        if m not in legal:
            print(f"Move {i+1} action {m} ILLEGAL. legal={legal[:10]}...")
            return
        prev_p1 = e.piece_counts[0]
        prev_p2 = e.piece_counts[1]
        cur = e.current_player
        e.step(m)
        delta_p1 = e.piece_counts[0] - prev_p1
        delta_p2 = e.piece_counts[1] - prev_p2
        captured_str = ""
        if cur == 1 and delta_p2 < 0:
            captured_str = f" (captured {-delta_p2} P2)"
        elif cur == 2 and delta_p1 < 0:
            captured_str = f" (captured {-delta_p1} P1)"
        x = m % 8
        y = m // 8
        print(f"M{i+1:2d} P{cur} -> cell ({x},{y}) action={m}{captured_str}")
        if e.done:
            w = getattr(e, '_winner', None)
            print(f"  GAME OVER: winner={w}")
            break
    print()
    print_board(e)
    p1_score = sum(e.board_values[c] for c in range(64) if e.board_owners[c] == 1)
    p2_score_raw = sum(e.board_values[c] for c in range(64) if e.board_owners[c] == 2)
    p2_score = -p2_score_raw
    print(f"P1 effective: {p1_score:.3f}   P2 effective: {p2_score:.3f}   threshold: 22.645")
    print(f"P1 pieces: {e.piece_counts[0]}    P2 pieces: {e.piece_counts[1]}")
    if e.done:
        print(f"WINNER: {getattr(e, '_winner', None)}")


def print_board(e):
    print("    " + "  ".join(str(x) for x in range(8)))
    for y in range(8):
        row = []
        for x in range(8):
            c = y * 8 + x
            o = e.board_owners[c]
            row.append("X" if o == 1 else ("O" if o == 2 else "."))
        print(f" {y}  " + "  ".join(row))
    print()
    # Influence values (just own-cell positions)
    print("  Influence values:")
    print("    " + "    ".join(f"{x:2d}" for x in range(8)))
    for y in range(8):
        row = []
        for x in range(8):
            c = y * 8 + x
            row.append(f"{e.board_values[c]:+.2f}")
        print(f" {y}  " + " ".join(row))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--moves", required=True)
    p.add_argument("--game-id", default="c6bb58075520")
    p.add_argument("--db", default="genesis_v2_run16.db")
    args = p.parse_args()
    moves = [int(m) for m in args.moves.split(",") if m.strip()]
    play(args.game_id, moves, args.db)
