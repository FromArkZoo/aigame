"""Team-7 interactive driver for game 1ca924cc3062.

Runs moves through the engine, prints state + influence, verifies legality.
"""

import json
import sqlite3
import sys
import os
sys.path.insert(0, '/Users/jamesbrowne/aigame')
os.chdir('/Users/jamesbrowne/aigame')
from game_engine.game_def_v2 import GameDefV2
from game_engine.factory import create_engine


def load_engine():
    conn = sqlite3.connect('/Users/jamesbrowne/aigame/genesis_v2_run14.db')
    row = conn.execute("SELECT rule_representation FROM games WHERE game_id = ?",
                       ('1ca924cc3062',)).fetchone()
    conn.close()
    rules = json.loads(row[0])
    game = GameDefV2.from_dict(rules)
    engine = create_engine(game)
    return engine, game


def describe(engine):
    p1_total = sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 1)
    p2_total = -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 2)
    p1_count = sum(1 for c in range(64) if engine.board_owners[c] == 1)
    p2_count = sum(1 for c in range(64) if engine.board_owners[c] == 2)
    print(f"P1 influence on own: {p1_total:.3f}  | P2 influence on own (magnitude): {p2_total:.3f}"
          f"  | P1 pieces: {p1_count}, P2 pieces: {p2_count}"
          f"  | Done: {engine.done}  | Winner: {engine._winner}"
          f"  | To move: P{engine.current_player}")


def print_board(engine):
    syms = {0: '.', 1: 'X', 2: 'O'}
    header = '   ' + ' '.join(f'{x:>2}' for x in range(8))
    print(header)
    for y in range(8):
        row = f' {y} ' + ' '.join(f' {syms[int(engine.board_owners[y*8+x])]}' for x in range(8))
        print(row)


def print_values(engine):
    print("Board values (influence field):")
    for y in range(8):
        row = ' '.join(f'{engine.board_values[y*8+x]:+.2f}' for x in range(8))
        print(f' {y}: {row}')


def cell(x, y):
    return y*8 + x


def play(moves):
    engine, game = load_engine()
    for i, m in enumerate(moves):
        legal = engine.get_legal_actions()
        if m not in legal:
            print(f"ILLEGAL move {m} at step {i}. Current player: P{engine.current_player}")
            print(f"Legal actions: {sorted(legal)[:20]}...")
            sys.exit(1)
        player = engine.current_player
        engine.step(m)
        x, y = m % 8, m // 8
        if m == 64:
            print(f"Move {i+1}: P{player} PASS")
        else:
            print(f"Move {i+1}: P{player} plays cell {m} = ({x},{y})")
    print_board(engine)
    print()
    print_values(engine)
    print()
    describe(engine)
    return engine


if __name__ == '__main__':
    moves_str = sys.argv[1] if len(sys.argv) > 1 else ''
    moves = [int(x) for x in moves_str.split(',') if x.strip()]
    play(moves)
