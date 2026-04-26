"""Simultaneous-turn play driver for team-22 evaluating 992bf7dfc9f4.

Usage:
    .venv/bin/python evaluations/run14/team-22_driver.py \
        --moves "12,51;13,52;..." [--verbose]

Each semicolon-separated entry is a simultaneous round "p1_action,p2_action".
Action 64 == pass.

Also supports --show to render the state after a given sequence.
"""
import argparse
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from play_helper import load_game
from game_engine.engine_v2 import GameEngineV2


def render(engine):
    n = engine.game.axis_size
    rows = []
    rows.append('   ' + ' '.join(f'{c:2d}' for c in range(n)))
    for y in range(n):
        row = [f'{y:2d} ']
        for x in range(n):
            cell = y * n + x
            o = int(engine.board_owners[cell])
            row.append(' X' if o == 1 else (' O' if o == 2 else ' .'))
        rows.append(''.join(row))
    rows.append(f'Pieces: P1={engine.piece_counts[0]}, P2={engine.piece_counts[1]}')
    return '\n'.join(rows)


def parse_moves(s: str):
    out = []
    if not s.strip():
        return out
    for part in s.split(';'):
        a, b = part.split(',')
        out.append((int(a.strip()), int(b.strip())))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='/Users/jamesbrowne/aigame/genesis_v2_run14.db')
    p.add_argument('--game', default='992bf7dfc9f4')
    p.add_argument('--moves', default='')
    p.add_argument('--verbose', action='store_true')
    p.add_argument('--show-legal', action='store_true')
    args = p.parse_args()

    game = load_game(args.db, args.game)
    engine = GameEngineV2(game)
    engine.reset()

    rounds = parse_moves(args.moves)

    for i, (a1, a2) in enumerate(rounds, 1):
        legal1 = engine.get_legal_actions(1)
        legal2 = engine.get_legal_actions(2)
        if a1 not in legal1:
            print(f'!!! Round {i}: P1 action {a1} ILLEGAL. Legal: {legal1}')
            return 1
        if a2 not in legal2:
            print(f'!!! Round {i}: P2 action {a2} ILLEGAL. Legal: {legal2}')
            return 1
        obs, rew, done, info = engine.step_simultaneous(a1, a2)
        if args.verbose or done:
            print(f'--- Round {i}: P1={a1}  P2={a2}  collision={info.get("collision")} ---')
            print(render(engine))
        if done:
            w = info.get('winner')
            print(f'\n*** GAME OVER round {i}: winner={"draw" if w is None else f"P{w+1}"} (rewards={rew}) ***')
            return 0

    # Final status
    print(f'\n=== After {len(rounds)} rounds (not done) ===')
    print(render(engine))
    if args.show_legal:
        l1 = engine.get_legal_actions(1)
        l2 = engine.get_legal_actions(2)
        print(f'Legal P1 ({len(l1)}): {l1[:30]}{"..." if len(l1)>30 else ""}')
        print(f'Legal P2 ({len(l2)}): {l2[:30]}{"..." if len(l2)>30 else ""}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
