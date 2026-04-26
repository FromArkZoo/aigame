"""Game 3 — seat-swap. Now treating 'me' as P2, and 'prior P2 reasoner' as P1.
P1 opens center (3,3). P2 plays SUPER aggressive: (3,4) adjacent (Chebyshev-1),
maximizing mutual influence cancellation to force P1 into a fight rather than a race.
P2 will then try to build their OWN cluster faster by exploiting P1's lost tempo.
"""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from play_helper import load_game
from game_engine.factory import create_engine

game = load_game('genesis_v2_run14.db', '931c58ae59b4')
engine = create_engine(game)
engine.reset()


def p1_eff():
    return sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 1)


def p2_eff():
    return -sum(engine.board_values[c] for c in range(64) if engine.board_owners[c] == 2)


def play(action, label):
    player = engine.current_player
    legal = engine.get_legal_actions()
    if action not in legal:
        print(f'  ILLEGAL {action} ({action%8},{action//8}) — legal: {legal[:15]}...')
        return False
    engine.step(action)
    print(f'  [P{player}] {label} @ ({action%8},{action//8})  P1={p1_eff():.2f} P2={p2_eff():.2f} pieces={engine.piece_counts[0]}/{engine.piece_counts[1]} done={engine.done}')
    return True


def render():
    for y in range(8):
        row = []
        for x in range(8):
            o = engine.board_owners[y*8+x]
            row.append('X' if o == 1 else 'O' if o == 2 else '.')
        print(''.join(row))


# P1 plays center (3,3). P2 plays (3,4) immediately adjacent — disrupts P1.
# Then P1 will try to extend away (say up-left), and P2 extends lower-right.
# Note: P2 starts 1 tempo down, so P2 needs efficient moves.

moves = [
    (27, 'P1 center (3,3)'),       # 27
    (35, 'P2 super-adj (3,4)'),    # 35 = y*8+x = 4*8+3
    (19, 'P1 flee (3,2)'),         # 19 — move away from P2 influence
    (43, 'P2 extend (3,5)'),       # 43 = 5*8+3
    (18, 'P1 (2,2)'),              # 18
    (44, 'P2 (4,5)'),              # 44 = 5*8+4
    (11, 'P1 (3,1)'),              # 11 = 1*8+3
    (52, 'P2 (4,6)'),              # 52 = 6*8+4
    (10, 'P1 (2,1)'),              # 10
    (51, 'P2 (3,6)'),              # 51 = 6*8+3
    (17, 'P1 (1,2)'),              # 17 = 2*8+1
    (53, 'P2 (5,6)'),              # 53
    (9,  'P1 (1,1)'),              # 9
    (45, 'P2 (5,5)'),              # 45
    (26, 'P1 (2,3)'),              # 26 — risky, near P2
    (60, 'P2 (4,7)'),              # 60 = 7*8+4
    (25, 'P1 (1,3)'),              # 25
    (61, 'P2 (5,7)'),              # 61
    (16, 'P1 (0,2)'),              # 16
    (54, 'P2 (6,6)'),              # 54
]
for a, l in moves:
    if engine.done:
        print('Game ended, winner =', engine._winner)
        break
    play(a, l)


continue_moves = [
    (8,  'P1 (0,1)'),     # 8 — extend corner
    (62, 'P2 (6,7)'),     # 62
    (0,  'P1 (0,0)'),     # 0 — corner — loses a bit of efficiency but P1 needs threshold
]
for a, l in continue_moves:
    if engine.done:
        print('Game ended, winner =', engine._winner)
        break
    play(a, l)

render()
print()
print('Winner:', engine._winner, 'Done:', engine.done)
print(f'P1 eff: {p1_eff():.3f}  P2 eff: {p2_eff():.3f}  threshold 63.46')
