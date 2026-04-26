"""Game 1 — P1 = me (anchor, upper-left), P2 = me (mirror, lower-right)."""
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
        print(f'  ILLEGAL action {action} ({action%8},{action//8}) — legal: {legal[:10]}...')
        return False
    engine.step(action)
    print(f'  [P{player}] {label} @ ({action%8},{action//8})  '
          f'=> P1 eff={p1_eff():.2f}  P2 eff={p2_eff():.2f}  '
          f'pieces P1={engine.piece_counts[0]} P2={engine.piece_counts[1]}  done={engine.done}')
    return True


def render():
    for y in range(8):
        row = []
        for x in range(8):
            o = engine.board_owners[y*8+x]
            row.append('X' if o == 1 else 'O' if o == 2 else '.')
        print(''.join(row))


# Moves played so far
moves = [
    (27, 'center'),          # P1 (3,3)
    (45, 'mirror SE (5,5)'), # P2
    (18, 'diag up-left'),    # P1 (2,2)
    (54, 'mirror (6,6)'),    # P2
    (9, 'diag (1,1)'),       # P1
]
for a, l in moves:
    play(a, l)


# Continue play. Strategy:
# P1: build 3x3-4x3 cluster in upper-left (rows 1-3, cols 1-3, then extend)
# P2: mirror in lower-right (rows 5-7, cols 5-7)
# P2 moves after P1. P2 should play (7,7) next — mirrors (1,1).
more_moves = [
    (63, 'diag (7,7)'),      # P2 mirror
    (10, 'fill (2,1)'),      # P1 extending cluster
    (62, 'mirror (6,7)'),    # P2
    (19, 'fill (3,2)'),      # P1 (3,2)
    (55, 'mirror (7,6)'),    # P2 (7,6)
    (11, 'fill (3,1)'),      # P1 — builds 3x3 upper-left
    (47, 'mirror (7,5)'),    # P2 (7,5)
    (26, 'fill (2,3)'),      # P1 (2,3)
    (46, 'mirror (6,5)'),    # P2 (6,5)
    (17, 'fill (1,2)'),      # P1 (1,2)
    (53, 'mirror (5,6)'),    # P2 (5,6)
    (25, 'fill (1,3)'),      # P1 (1,3)
    (44, 'mirror (4,5)'),    # P2 (4,5)
]
for a, l in more_moves:
    if engine.done:
        print('Game ended early, winner =', engine._winner)
        break
    play(a, l)



# Continue. P2 switched to pressuring (4,5). P1 should extend safely upper-left.
# Options for P1 (adjacent_to_own): (0,0),(1,0),(2,0),(0,1),(0,2),(4,1),(0,3),(0,4),(1,4),(2,4),(3,4),(4,2),(4,3),(4,4)
# (0,2) extends into corner region safely — Chebyshev from P2's (4,5) is 3. Good.
continue_moves = [
    (16, 'P1 extend (0,2)'),  # P1
    (36, 'P2 press (4,4)'),   # P2
    (8,  'P1 extend (0,1)'),   # P1
    (37, 'P2 press (5,4)'),   # P2
    (24, 'P1 extend (0,3)'),   # P1
]
for a, l in continue_moves:
    if engine.done:
        print('Game ended, winner =', engine._winner)
        break
    play(a, l)


render()
print()
print('Winner:', engine._winner, 'Done:', engine.done)
print('P1 eff:', p1_eff(), 'P2 eff:', p2_eff(), 'threshold 63.46')
