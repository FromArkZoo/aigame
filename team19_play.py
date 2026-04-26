"""Helper for team-19 to play game 4d9c5796dd18 with influence tracking."""
import sqlite3, json, sys
import numpy as np
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine

GAME_ID = '4d9c5796dd18'

def load():
    conn = sqlite3.connect('/Users/jamesbrowne/aigame/genesis_v2_run16.db')
    row = conn.execute('SELECT rule_representation FROM games WHERE game_id = ?', (GAME_ID,)).fetchone()
    return GameDefV2.from_dict(json.loads(row[0]))

def coords_to_action(x, y):
    return y * 8 + x

def action_to_coords(a):
    return (a % 8, a // 8)

def show(engine):
    print("    " + " ".join(f"{x:>5}" for x in range(8)))
    for y in range(8):
        line = f"{y:>2} "
        for x in range(8):
            idx = y * 8 + x
            owner = engine.board_owners[idx]
            v = engine.board_values[idx]
            if owner == 1: ch = 'X'
            elif owner == 2: ch = 'O'
            else: ch = '.'
            line += f" {ch}{v:>+5.1f}"
        print(line)
    p1 = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==1)
    p2 = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==2)
    print(f"  P1 effective: {p1:.2f}  P2 effective: {p2:.2f}  (threshold {load().win_condition.threshold:.2f})")
    print(f"  Pieces P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}  Next: P{engine.current_player}  done={engine.done}  winner={engine._winner}")

def predict_score(engine, action, player):
    """Predict effective score for `player` after they play `action`.
    Does NOT actually mutate `engine`; uses a deep copy.
    """
    import copy
    e = copy.deepcopy(engine)
    if e.current_player != player:
        e.current_player = player
    e.step(action)
    p1 = sum(e.board_values[c] for c in range(64) if e.board_owners[c]==1)
    p2 = -sum(e.board_values[c] for c in range(64) if e.board_owners[c]==2)
    return (p1, p2, e.done, e._winner)

def best_move_for(engine, player, candidates=None):
    """Find best action for `player` among legal actions (or candidates)."""
    legal = engine.get_legal_actions()
    if candidates is None:
        candidates = [a for a in legal if a != 64]  # skip pass
    else:
        candidates = [a for a in candidates if a in legal]
    best = None
    best_diff = -1e9
    for a in candidates:
        p1, p2, done, winner = predict_score(engine, a, player)
        # If this move wins immediately for `player`, take it
        if done and winner == player:
            return a, 1e6
        # Maximize own score minus opponent score (greedy)
        if player == 1:
            diff = p1 - p2
        else:
            diff = p2 - p1
        # Heavy penalty for moves that hand opponent the win
        if done and winner is not None and winner != player:
            diff -= 1000
        if diff > best_diff:
            best_diff = diff
            best = a
    return best, best_diff


def play_game(moves, label='Game'):
    game = load()
    engine = create_engine(game)
    engine.reset()
    print(f"\n=== {label} ===")
    for i, m in enumerate(moves):
        x, y = action_to_coords(m)
        cur = engine.current_player
        engine.step(m)
        p1 = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==1)
        p2 = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==2)
        print(f"  Move {i+1}: P{cur} -> ({x},{y}) [act {m}]  P1eff={p1:.2f} P2eff={p2:.2f}  done={engine.done} winner={engine._winner}")
        if engine.done:
            break
    show(engine)
    return engine
