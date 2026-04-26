"""Team-6 helper for evaluating game 8d12c8b92b71 in Run 16.

Provides a function to build engine, run a sequence of moves, and report
the per-cell influence values plus per-player effective score.
"""
import sys, json, sqlite3
sys.path.insert(0, '/Users/jamesbrowne/aigame')
import numpy as np

from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine

DB = '/Users/jamesbrowne/aigame/genesis_v2_run16.db'
GAME_ID = '8d12c8b92b71'


def load_engine():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT rule_representation FROM games WHERE game_id = ?',
                       (GAME_ID,)).fetchone()
    conn.close()
    rules = json.loads(row['rule_representation'])
    game = GameDefV2.from_dict(rules)
    engine = create_engine(game)
    engine.reset()
    return engine, game


def cell(x, y, axis=8):
    return y * axis + x


def coords(c, axis=8):
    return (c % axis, c // axis)


def show(engine, label=''):
    np.set_printoptions(precision=2, suppress=True, linewidth=200)
    print(f'--- {label} step={engine.step_count} player_to_move={engine.current_player} ---')
    print('owners:'); print(engine.board_owners.reshape(8, 8))
    print('values:'); print(engine.board_values.reshape(8, 8))
    p1_score = engine.board_values[engine.board_owners == 1].sum()
    p2_score = -engine.board_values[engine.board_owners == 2].sum()
    print(f'P1 effective score: {p1_score:.3f}   P2 effective score: {p2_score:.3f}   '
          f'(threshold 34.129)')
    print(f'pieces: P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}, done={engine.done}, '
          f'winner={getattr(engine, "_winner", None)}')


def play_seq(moves, label='', show_each=False):
    engine, game = load_engine()
    for i, m in enumerate(moves):
        legal = engine.get_legal_actions()
        if m not in legal:
            print(f'!!! illegal move {m} at step {i}; legal sample={legal[:10]}')
            return engine
        engine.step(m)
        if show_each:
            show(engine, label=f'{label} after move{i}={m} ({coords(m) if m<64 else "PASS"})')
        if engine.done:
            break
    show(engine, label=f'{label} FINAL')
    return engine


def best_score_move(engine, player):
    """Return action that maximizes player's effective score after the move (greedy)."""
    legal = engine.get_legal_actions()
    best_a, best_v = None, -1e9
    for a in legal:
        if a == 64:
            continue
        clone = engine.clone()
        clone.step(a)
        if player == 1:
            v = clone.board_values[clone.board_owners == 1].sum()
        else:
            v = -clone.board_values[clone.board_owners == 2].sum()
        if v > best_v:
            best_v, best_a = v, a
    return best_a, best_v


def best_margin_move(engine, player):
    """Return action that maximizes player's effective score MINUS opponent's."""
    legal = engine.get_legal_actions()
    best_a, best_v = None, -1e9
    for a in legal:
        if a == 64:
            continue
        clone = engine.clone()
        clone.step(a)
        p1 = clone.board_values[clone.board_owners == 1].sum()
        p2 = -clone.board_values[clone.board_owners == 2].sum()
        v = (p1 - p2) if player == 1 else (p2 - p1)
        if v > best_v:
            best_v, best_a = v, a
    return best_a, best_v


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--moves', type=str, default='')
    p.add_argument('--show-each', action='store_true')
    args = p.parse_args()
    moves = [int(x) for x in args.moves.split(',') if x.strip()] if args.moves else []
    play_seq(moves, show_each=args.show_each)
