"""Hand-played Game 1: both players natural-only, to verify it plays like the source.

Strategy: I (the human evaluator) will play both sides, choosing reasonable moves.
For natural play: pick (a) center-clustering moves to build score; (b) when behind,
attempt to outnumber-capture opponent stones at the cluster edge.
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from experiments.phase_spike.phase_game import PhaseGame, encode_action

# Cell index = y*8 + x. Center cells are around (3,3)=27, (4,4)=36, etc.
moves = [
    # Both players build small clusters in opposite corners-ish, simulating
    # the source game's typical opening pattern (alternating natural placement).
    (1, 27, +1),   # P1 center natural
    (2, 36, -1),   # P2 diagonal-adjacent natural
    (1, 28, +1),   # P1 extend cluster
    (2, 35, -1),   # P2 attack along the diagonal
    (1, 19, +1),   # P1 extend up
    (2, 44, -1),   # P2 extend down
    (1, 20, +1),
    (2, 43, -1),
    (1, 26, +1),
    (2, 37, -1),
    (1, 18, +1),
    (2, 45, -1),
    (1, 11, +1),   # P1 push north
    (2, 52, -1),   # P2 push south
    (1, 12, +1),
    (2, 51, -1),
    (1, 10, +1),
    (2, 53, -1),
    (1, 21, +1),   # P1 extend east
    (2, 42, -1),   # P2 extend west
    (1, 13, +1),
    (2, 50, -1),
]

g = PhaseGame()
print("HAND-PLAYED GAME 1 — Natural-only play")
print("=" * 60)

for i, (player, cell, phase) in enumerate(moves, 1):
    if g.done:
        print(f"-- game ended before move {i} --")
        break
    assert g.current_player == player, f"move {i}: expected P{player} but it's P{g.current_player}'s turn"
    a = encode_action(cell, phase)
    info = g.step(a)
    cap = info.get("captured", [])
    cap_str = f"  CAPTURED={cap}" if cap else ""
    end = info.get("end_reason", "")
    end_str = f"  END={end}" if end else ""
    print(f"  move {i:2d}: P{player} plays {cell}{'+' if phase==1 else '-'}"
          f"  scores P1={info['score_p1']:+.2f} P2={info['score_p2']:+.2f}{cap_str}{end_str}")

print()
print(g.render())
