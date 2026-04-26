"""Team-4 helper: play a sequence of moves and print board_values + totals."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
import json
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def load_game(db_path, game_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT rule_representation FROM games WHERE game_id = ?", (game_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"Game {game_id} not found")
    rule_dict = json.loads(row[0])
    return GameDefV2.from_dict(rule_dict)


def play_and_show(db_path, game_id, moves):
    game = load_game(db_path, game_id)
    engine = create_engine(game)
    print(f"=== Playing game {game_id} ===")
    print(f"threshold={game.win_condition.threshold:.4f}")
    for i, m in enumerate(moves):
        player_0indexed = engine.get_current_player()
        player = player_0indexed + 1
        legal = engine.get_legal_actions()
        if m not in legal:
            print(f"ILLEGAL: move {i+1} action {m} by player {player}; legal subset: {sorted(legal)[:20]}... total {len(legal)}")
            return engine
        obs, rewards, done, info = engine.step(m)
        x = m % 8
        y = m // 8
        ptag = 'X' if player == 1 else 'O'
        print(f"\n--- Move {i+1}: P{player}({ptag}) -> action {m} = cell ({x},{y}) ---")
        render_board(engine)
        p1_sum, p2_sum = compute_totals(engine)
        print(f"  P1 pieces={engine.piece_counts[0]} P2 pieces={engine.piece_counts[1]}")
        print(f"  P1 effective value (positive on own) = {p1_sum:+.3f}")
        print(f"  P2 effective value (negated on own)  = {p2_sum:+.3f}")
        print(f"  threshold = {game.win_condition.threshold:.3f}")
        if done:
            winner = engine._winner
            print(f"GAME OVER. Winner: {winner}  (step={engine.step_count})")
            return engine
    print("\n--- Legal actions for next player ---")
    legal = sorted(engine.get_legal_actions())
    print(f"  next player: {engine.get_current_player() + 1}")
    print(f"  total legal: {len(legal)}; pass=64 {'in' if 64 in legal else 'not in'} legal")
    return engine


def render_board(engine):
    print("   0  1  2  3  4  5  6  7")
    for y in range(8):
        row = f" {y} "
        for x in range(8):
            idx = y * 8 + x
            o = engine.board_owners[idx]
            v = engine.board_values[idx]
            if o == 1:
                row += " X "
            elif o == 2:
                row += " O "
            else:
                row += " . "
        # add a values line
        vals = []
        for x in range(8):
            idx = y * 8 + x
            vals.append(f"{engine.board_values[idx]:+5.2f}")
        print(row + "   " + " ".join(vals))


def compute_totals(engine):
    """Return (p1_effective, p2_effective). P1 wants positive sum on own cells;
    P2's effective is -sum of values on own cells (since P2's additions are negative).
    """
    p1 = 0.0
    p2 = 0.0
    for i in range(64):
        if engine.board_owners[i] == 1:
            p1 += engine.board_values[i]
        elif engine.board_owners[i] == 2:
            p2 += engine.board_values[i]
    return p1, -p2


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", default="genesis_v2_run14.db")
    ap.add_argument("--game-id", required=True)
    ap.add_argument("--moves", default="")
    args = ap.parse_args()
    moves = []
    if args.moves.strip():
        moves = [int(x) for x in args.moves.split(",")]
    play_and_show(args.db_path, args.game_id, moves)
