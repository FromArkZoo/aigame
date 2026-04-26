"""Test if P2 can EVER win, even with smart strategy.

Strategy: P2 plays only +1 stones (camouflage) attempting to invade P1 territory.
For P2 to score positively, P2 needs cell_val * (-phase) > 0.
- P2@-1: -phase=+1, need cell_val>0 → P2 stone with mostly +1 neighbors
- P2@+1: -phase=-1, need cell_val<0 → P2 stone with mostly -1 neighbors

So P2 camo (P2@+1) wants to be near OTHER -1 stones (their own or P1's camo).
P2 natural (P2@-1) wants to be near +1 stones (P1's natural or P2 camo).

But wait — for P2@-1 in P1@+1 territory: cell_val>0 (positive neighbors), and -phase=+1, score=+. Yes! P2 natural in P1 territory scores POSITIVELY for P2.
But the stone gets captured if 3+ +1 neighbors with no -1.

So P2's only positive-scoring path is:
  - P2@-1 stone in P1@+1 territory with 1-2 +1 neighbors (not captured: opp-same<=2)
  - P2@+1 (camo) in P2@-1 cluster (always +1)... wait check: cell_val<0 (negative neighbors), -phase=-1, contribution = -cell_val = -(-)=+. YES! P2 camo in own cluster scores positive.

Let's test: pure-camo P2 strategy.
"""

from __future__ import annotations
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))

import numpy as np
from experiments.phase_spike.phase_game import PhaseGame, encode_action, PASS_ACTION


def main():
    g = PhaseGame()
    # P2 strategy: build a cluster with P2@+1 stones (so -phase=-1 mirrors P1)
    # Both players play +1 for fair comparison
    moves = [
        (27,1),(28,1),  # mover 1-2: P1 27+, P2 28+
        (35,1),(36,1),
        (29,1),(37,1),
        (43,1),(44,1),
        (45,1),(34,1),
        (26,1),(33,1),
        (25,1),(42,1),
    ]
    for cell, phase in moves:
        info = g.step(encode_action(cell, phase))
        print(f"  step {info['step']} P{info['player']} cell {cell} phase {phase} captured={info.get('captured', [])} P1={g.player_score(1):.3f} P2={g.player_score(2):.3f}")
    print()
    print(g.render())


if __name__ == "__main__":
    main()
