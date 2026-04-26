"""Check P1 cluster values at 9, 10, 11, 12 pieces."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team4_play import load_game
from game_engine.factory import create_engine

def sim(cells, label):
    game = load_game('genesis_v2_run14.db','deb4dfe0382d')
    engine = create_engine(game)
    for c in cells:
        engine.current_player = 1
        engine.board_owners[c] = 1
        engine.piece_counts[0] += 1
        engine._apply_propagation(c)
    p1_sum = sum(float(engine.board_values[i]) for i in range(64) if engine.board_owners[i]==1)
    print(f"{label} ({len(cells)} pieces): P1 = {p1_sum:.3f}")

# 2x3 (6 pieces)
sim([19,20,27,28,35,36], "2x3")
# 2x4 (8)
sim([18,19,20,21,26,27,28,29], "2x4 horiz")
# 3x3 (9)
sim([18,19,20,26,27,28,34,35,36], "3x3")
# 3x4 (12)
sim([18,19,20,26,27,28,34,35,36,42,43,44], "3x4")
# 4x3 (12)
sim([17,18,19,20,25,26,27,28,33,34,35,36], "4x3")
# 3x3 + 1 (10 pieces)
sim([18,19,20,26,27,28,34,35,36,17], "3x3+1 edge")
sim([18,19,20,26,27,28,34,35,36,25], "3x3+1 mid-edge")
sim([18,19,20,26,27,28,34,35,36,33], "3x3+1 corner-adj")

# 3x3 + 2 (11 pieces)
sim([18,19,20,26,27,28,34,35,36,25,33], "3x3+2 along left mid")
sim([18,19,20,26,27,28,34,35,36,17,21], "3x3+2 top edges")
sim([18,19,20,26,27,28,34,35,36,25,37], "3x3+2 both mids")

# 3x3 + 3 (12 pieces) — add full row/col
sim([18,19,20,26,27,28,34,35,36,25,33,41], "3x3+3 left col extension")
sim([18,19,20,26,27,28,34,35,36,17,21,29], "3x3+3 top+right")

# 2-piece thick cross
sim([18,19,20,21,26,27,28,29,34,35,36,37], "4x3 rect")

# L-shape
sim([18,19,20,26,27,28,34,35,36,37,38,39,30,22], "L-ish 14")
