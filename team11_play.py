#!/usr/bin/env python3
"""Team-11 play helper for game d8f2ae54f399 (alternating, grid, surround, influence threshold)."""
import sys
sys.path.insert(0, '.')
from game_engine.factory import create_engine
from game_engine.game_def_v2 import GameDefV2
import sqlite3, json
import numpy as np

def load_game(game_id='d8f2ae54f399'):
    conn = sqlite3.connect('genesis_v2_run15.db')
    row = conn.execute(
        "SELECT rule_representation FROM games WHERE game_id=?", (game_id,)
    ).fetchone()
    rules = json.loads(row[0])
    return GameDefV2.from_dict(rules)

def play_moves(moves, show_every=None):
    """Replay moves and return engine + history."""
    game = load_game()
    engine = create_engine(game)
    engine.reset()
    history = []
    for i, m in enumerate(moves):
        cp = engine.current_player
        engine.step(m)
        vals = engine.board_values.copy()
        p1_eff = sum(vals[c] for c in range(64) if engine.board_owners[c]==1)
        p2_eff = -sum(vals[c] for c in range(64) if engine.board_owners[c]==2)
        history.append({
            'move_num': i+1,
            'player': cp,
            'action': m,
            'yx': (m//8, m%8) if m < 64 else 'PASS',
            'pieces_p1': int(engine.piece_counts[0]),
            'pieces_p2': int(engine.piece_counts[1]),
            'p1_eff': p1_eff,
            'p2_eff': p2_eff,
            'done': engine.done,
            'winner': engine._winner,
        })
        if engine.done:
            break
    return engine, history

def show(engine):
    np.set_printoptions(precision=2, suppress=True, linewidth=200)
    print('Board owners:')
    print(engine.board_owners.reshape(8,8))
    print('Influence values:')
    print(engine.board_values.reshape(8,8))
    p1_eff = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==1)
    p2_eff = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c]==2)
    print(f'P1 effective: {p1_eff:.3f} / 22.645')
    print(f'P2 effective: {p2_eff:.3f} / 22.645')
    print(f'P1 pieces={engine.piece_counts[0]}, P2 pieces={engine.piece_counts[1]}')
    print(f'Done: {engine.done}, Winner: {engine._winner}, Next: P{engine.current_player}')
    legal = engine.get_legal_actions() if not engine.done else []
    if legal:
        print(f'Legal actions: {len(legal)} total')

def legal_candidates(engine, top_k=5):
    """Return (action, score) for 'score' being how much that move increases P1_eff - P2_eff after placement."""
    if engine.done:
        return []
    cp = engine.current_player
    legal = engine.get_legal_actions()
    results = []
    for a in legal:
        if a == 64:
            continue
        # simulate
        import copy
        e2 = copy.deepcopy(engine)
        try:
            e2.step(a)
        except Exception:
            continue
        p1_eff = sum(e2.board_values[c] for c in range(64) if e2.board_owners[c]==1)
        p2_eff = -sum(e2.board_values[c] for c in range(64) if e2.board_owners[c]==2)
        score = p1_eff - p2_eff if cp == 1 else p2_eff - p1_eff
        results.append((a, score, e2._winner, (e2.piece_counts[0], e2.piece_counts[1])))
    results.sort(key=lambda r: -r[1])
    return results[:top_k]

if __name__ == '__main__':
    moves_str = sys.argv[1] if len(sys.argv) > 1 else ''
    moves = [int(x) for x in moves_str.split(',') if x.strip()] if moves_str else []
    engine, hist = play_moves(moves)
    for h in hist[-5:]:
        print(h)
    print('---')
    show(engine)
    print('---')
    print('Top candidate moves for current player:')
    for a, s, w, pc in legal_candidates(engine, top_k=12):
        print(f'  action {a} y={a//8},x={a%8}: delta={s:.3f} (pc after P1={pc[0]},P2={pc[1]}, winner={w})')
