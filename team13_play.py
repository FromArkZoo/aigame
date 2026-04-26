"""Team-13 play helper: verify moves and show influence after each."""
import sys
from play_helper import load_game
from game_engine.factory import create_engine
import numpy as np

def run(moves_csv):
    g = load_game('genesis_v2_run14.db', '931c58ae59b4')
    eng = create_engine(g)
    eng.reset()
    moves = [int(m) for m in moves_csv.split(',')] if moves_csv else []
    for i, m in enumerate(moves):
        pid = eng.current_player
        legal = eng.get_legal_actions()
        if m not in legal:
            print(f"MOVE {i+1} (P{pid}) ILLEGAL: {m}. Legal: {legal}")
            return
        eng.step(m)
    print(f"Owners:\n{eng.board_owners.reshape(8,8)}")
    print(f"Values:\n{eng.board_values.reshape(8,8).round(2)}")
    p1 = sum(eng.board_values[c] for c in range(64) if eng.board_owners[c]==1)
    p2 = -sum(eng.board_values[c] for c in range(64) if eng.board_owners[c]==2)
    print(f"P1 effective: {p1:.3f}  P2 effective: {p2:.3f}  Threshold: 63.46")
    print(f"Pieces: P1={eng.piece_counts[0]} P2={eng.piece_counts[1]}")
    print(f"Current turn: P{eng.current_player}  Done: {eng.done}  Winner: {eng._winner}")
    if not eng.done:
        la = eng.get_legal_actions()
        print(f"Legal moves ({len(la)}): {la[:20]}{'...' if len(la)>20 else ''}")

if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv)>1 else '')
