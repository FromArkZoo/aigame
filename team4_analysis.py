"""Analytical scratchpad: what's max P1 value in a tight cluster if P2 doesn't disrupt?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team4_play import load_game
from game_engine.factory import create_engine

def simulate_p1_only(cells):
    """Hypothetically place pieces by P1 only (bypass turns) by calling engine directly."""
    game = load_game('genesis_v2_run14.db','deb4dfe0382d')
    engine = create_engine(game)
    # Directly call propagation as if player 1 played each cell
    for c in cells:
        engine.current_player = 1
        engine.board_owners[c] = 1
        engine.piece_counts[0] += 1
        engine._apply_propagation(c)
    p1_sum = sum(float(engine.board_values[i]) for i in range(64) if engine.board_owners[i]==1)
    print(f"cells={cells} -> P1 effective value = {p1_sum:.3f}")
    return p1_sum

# 3x3 block centered around (3,3) (y*8+x): coords 18=(2,2),19=(3,2),20=(4,2),26=(2,3),27=(3,3),28=(4,3),34=(2,4),35=(3,4),36=(4,4)
simulate_p1_only([18,19,20,26,27,28,34,35,36])

# 4x3
simulate_p1_only([17,18,19,20,25,26,27,28,33,34,35,36])

# 3x4
simulate_p1_only([18,19,20,26,27,28,34,35,36,42,43,44])

# 4x4
simulate_p1_only([17,18,19,20,25,26,27,28,33,34,35,36,41,42,43,44])

# torus full row (8 cells on torus row y=3)
simulate_p1_only([24,25,26,27,28,29,30,31])

# 5x3 (15 pieces)
simulate_p1_only([17,18,19,20,21,25,26,27,28,29,33,34,35,36,37])

# torus double-row (16 cells: two full rows adjacent) — very tight
simulate_p1_only([24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39])

# Full 8x3 (24 pieces — should definitely win)
simulate_p1_only(list(range(16,40)))
