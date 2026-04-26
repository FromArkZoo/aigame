"""Game 3: Seat swap. I play with P2 mindset trying hardest to win.
P1 plays the same strong center opening.
P2 strategy: build asymmetric corner cluster to maximize edge-of-board
density, OR start contesting at distance 2 (in P1's radius) to drain
P1's score before pulling back.

Key insight: P1 will reach threshold first if P2 plays purely separately
(Game 1 showed P1 wins by ~1 move). So P2 needs to either
  (a) deny P1 a tempo move (place inside P1's radius without losing tempo)
  (b) play efficiently in corner/edge where each move gets max synergy
"""
import sys
sys.path.insert(0, '/Users/jamesbrowne/aigame')
from team6_run16_helper import load_engine, coords

# Strategy: P2 builds in a corner where less periphery is wasted off-board.
# Hex 8x8 corners (0,0), (7,0), (0,7), (7,7) have 3 in-board neighbors at d=1.
# The most efficient cluster is actually mid-center where all 6 neighbors exist.
# But against P1 who claims center, P2 picks the FAR-CENTER (5,5) area where
# all 6 neighbors are still on-board.
#
# Tweak vs Game 1: P2 plays opposite-mirror so each stone overlaps tightly.
# Also at end-game, P2 may need to PASS-equivalent (place sub-optimally) but
# we don't have a stall option; both must place until threshold.

moves = [
    27,  # P1 (3,3) center
    44,  # P2 (4,5) — distance 2 from (3,3)? Actually plant at corner-of-center
    # Let's go: P2 (5,4) action 37 or (5,5) action 45 — (5,5) is hex-d=3, safer
]
moves = [
    27,  # P1 (3,3)
    45,  # P2 (5,5)
    19,  # P1 (3,2) extend N
    54,  # P2 (6,6) extend SE
    11,  # P1 (3,1) extend further
    37,  # P2 (5,4) tight cluster around (5,5) towards center
    18,  # P1 (2,2)
    46,  # P2 (6,5) cluster
    20,  # P1 (4,2) — eastward push, contesting
    53,  # P2 (5,6) cluster
    10,  # P1 (2,1)
    62,  # P2 (6,7) cluster
    26,  # P1 (2,3)
    63,  # P2 (7,7) cluster
    34,  # P1 (2,4)
    61,  # P2 (5,7) — extending
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
