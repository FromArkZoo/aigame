"""Game 2: P2 plays an aggressive contesting strategy.
Theory: Plant P2 stones inside P1's would-be cluster zone to deny synergy.
Each P2 stone in P1's radius-2 zone adds NEGATIVE value where P1 wants
to place, draining P1's effective cell values.
"""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from team6_run16_helper import load_engine, coords

# P1 same opening: (3,3)
# P2: instead of distant cluster, plant at (4,4) — hex neighbor of (3,3).
#   This denies the cell, AND P2's influence reduces P1's surrounding cells.
# P1: must extend cluster while it can; pick (2,3) or NW direction.
# P2: keep contesting with (3,4) or other neighbor

moves = [
    27,  # P1 (3,3)
    36,  # P2 (4,4) — adjacent, contesting
    19,  # P1 (3,2) — extend NW
    35,  # P2 (3,4) — keep contesting
    11,  # P1 (3,1) — extend further N
    44,  # P2 (4,5) — extend P2 cluster S
    18,  # P1 (2,2) — diversify cluster
    37,  # P2 (5,4) — extend
    10,  # P1 (2,1) — extend N cluster
    45,  # P2 (5,5) — extend
    26,  # P1 (2,3) — bridge
    53,  # P2 (5,6) — extend
    9,   # P1 (1,1)
    46,  # P2 (6,5)
    17,  # P1 (1,2)
    54,  # P2 (6,6)
    3,   # P1 (3,0) extend
    62,  # P2 (6,7)
    2,   # P1 (2,0)
    63,  # P2 (7,7)
]


def main():
    engine, game = load_engine()
    import numpy as np
    np.set_printoptions(precision=2, suppress=True, linewidth=200)
    for i, m in enumerate(moves):
        legal = engine.get_legal_actions()
        if m not in legal:
            print(f'!!! illegal move {m} ({coords(m)}) at step {i}')
            return
        player = engine.current_player
        engine.step(m)
        p1 = engine.board_values[engine.board_owners == 1].sum()
        p2 = -engine.board_values[engine.board_owners == 2].sum()
        print(f'Move {i+1}: P{player} -> {m} {coords(m)}   P1={p1:.2f}  P2={p2:.2f}  done={engine.done}')
        if engine.done:
            print(f'GAME OVER. winner={getattr(engine, "_winner", None)}')
            break
    print()
    print('Final owners:'); print(engine.board_owners.reshape(8, 8))


if __name__ == '__main__':
    main()
