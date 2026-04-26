"""Team-16 driver for 931c58ae59b4 — engine-verified move-by-move play with board_value readouts."""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from play_helper import load_game
from game_engine.factory import create_engine


def fresh():
    game = load_game('genesis_v2_run14.db', '931c58ae59b4')
    engine = create_engine(game)
    engine.reset()
    return game, engine


def p1_eff(engine):
    return sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 1)


def p2_eff(engine):
    return -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 2)


def render(engine):
    print('    ' + ' '.join(f'{x:>5}' for x in range(8)))
    for y in range(8):
        row_o = []
        row_v = []
        for x in range(8):
            c = y*8 + x
            o = engine.board_owners[c]
            v = engine.board_values[c]
            ch = 'X' if o == 1 else 'O' if o == 2 else '.'
            row_o.append(f'{ch:>5}')
            row_v.append(f'{v:+.2f}')
        print(f'{y}: ' + ' '.join(row_o))
    print(f'  P1 eff: {p1_eff(engine):.3f}  P2 eff: {p2_eff(engine):.3f}  threshold 63.46')
    print(f'  pieces: P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}  turn player {engine.current_player}')


def coord_to_action(x, y):
    return y*8 + x


def play(engine, action, label=''):
    legal = engine.get_legal_actions()
    if action not in legal:
        print(f'  ILLEGAL {action} ({action%8},{action//8})')
        return False
    engine.step(action)
    return True


if __name__ == '__main__':
    game, engine = fresh()
    print('Initial threshold:', game.win_condition.threshold)
    print('max_turns:', game.win_condition.max_turns)
    render(engine)
