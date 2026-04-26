"""Game 2 — P1 opens at (2,2) off-center; P2 plays aggressively adjacent at (3,3)."""
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


# P1 opens (3,4) -- center-ish but off-center enough to leave room in both halves.
# Then P2 plays aggressively adjacent — (2,3) to disrupt.
# Moves
moves = [
    (3*8+4, 'P1 open (4,3)'),      # action 28 — P1 at (4,3)
    (3*8+3, 'P2 adj (3,3)'),       # action 27 — P2 immediately adjacent
    (4*8+5, 'P1 extend (5,4)'),    # action 37
    (2*8+2, 'P2 extend (2,2)'),    # action 18
    (3*8+6, 'P1 (6,3)'),           # action 30
    (1*8+1, 'P2 (1,1)'),           # action 9
    (4*8+6, 'P1 (6,4)'),           # action 38
    (2*8+1, 'P2 (1,2)'),           # action 17
    (5*8+5, 'P1 (5,5)'),           # action 45
    (1*8+2, 'P2 (2,1)'),           # action 10
    (5*8+6, 'P1 (6,5)'),           # action 46
    (0*8+0, 'P2 (0,0)'),           # action 0
    (4*8+4, 'P1 (4,4)'),           # action 36
    (3*8+2, 'P2 (2,3)'),           # action 26  — this is adjacent_to_P2 own; let's see legality
    (5*8+4, 'P1 (4,5)'),           # action 44
    (3*8+1, 'P2 (1,3)'),           # action 25
    (6*8+6, 'P1 (6,6)'),           # action 54
    (2*8+3, 'P2 (3,2)'),           # action 19 — contesting P1
    (5*8+3, 'P1 (3,5)'),           # action 43
    (0*8+1, 'P2 (1,0)'),           # action 1
    (6*8+5, 'P1 (5,6)'),           # action 53
]
for a, l in moves:
    if engine.done:
        print('Game ended, winner =', engine._winner)
        break
    play(a, l)


# Continue. P2 at 52.12 still trailing. P2 needs to extend while also not letting P1 pack more.
# P1 can extend (7,6) or (5,7) to boost cluster. P2 must extend or block.
continue_moves = [
    (0*8+2, 'P2 (2,0)'),           # action 2
    (7*8+6, 'P1 (6,7)'),           # action 62
    (0*8+3, 'P2 (3,0)'),           # action 3
    (7*8+5, 'P1 (5,7)'),           # action 61 — P1 should win here
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
