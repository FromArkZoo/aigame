"""Play Game 1 of team-6 evaluation, with reasoning per move."""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from team6_run16_helper import load_engine, coords, cell

# Game 1 plan:
# P1 starts central (3,3)
# P2 starts opposite corner area to build parallel cluster (5,5)
# Both extend their clusters AWAY from contact, racing to threshold
# Strategy: tight hex cluster maximizes effective score per stone

moves = [
    27,  # P1 (3,3) center
    45,  # P2 (5,5) opposite, hex distance 3
    26,  # P1 (2,3) extend NW, away from P2
    54,  # P2 (6,6) extend SE
    35,  # P1 (3,4) hex neighbor of (3,3) and (2,3); creates triangle
    37,  # P2 (5,4) close P2 cluster (touches (5,5)? dist 1)
    19,  # P1 (3,2) form NW cluster row
    53,  # P2 (5,6) close cluster
    25,  # P1 (1,3) extend
    62,  # P2 (6,7) extend SE
    34,  # P1 (2,4) cluster
    46,  # P2 (6,5) cluster
    18,  # P1 (2,2) cluster
    63,  # P2 (7,7) cluster
    11,  # P1 (3,1) cluster
    61,  # P2 (5,7) cluster
]


def main():
    engine, game = load_engine()
    import numpy as np
    np.set_printoptions(precision=2, suppress=True, linewidth=200)
    for i, m in enumerate(moves):
        legal = engine.get_legal_actions()
        if m not in legal:
            print(f'!!! illegal move {m} ({coords(m)}) at step {i}; legal sample={legal[:8]}')
            return
        player = engine.current_player
        engine.step(m)
        p1 = engine.board_values[engine.board_owners == 1].sum()
        p2 = -engine.board_values[engine.board_owners == 2].sum()
        print(f'Move {i+1}: P{player} -> action {m} {coords(m)}   P1={p1:.2f}  P2={p2:.2f}  done={engine.done}')
        if engine.done:
            print(f'GAME OVER. winner={getattr(engine, "_winner", None)}')
            break
    print()
    print('Final owners:'); print(engine.board_owners.reshape(8, 8))
    print('Final values:'); print(engine.board_values.reshape(8, 8))


if __name__ == '__main__':
    main()
