"""Construct a critical position where the BEST move is camouflage.

Idea: build P1 to where placing at ANY of cells {C1, C2} would push over
threshold. P2 must use camo to occupy cell C1 because:
- P2's natural at C1 would be captured (surrounded by 5+ P1 +1 stones), so it
  doesn't hold and P1 can play C2 to win anyway.
- P2's camo (b @ C1) is a +1 stone and won't be captured by +1 neighbors. The
  +1 stone radiates +0.94 INTO the cell P1 wants — but P2 occupies it so P1
  can't place there. P1 must instead try C2 (or accept score increase).

Key construction: pick C1 where P2's natural -1 placement would CAPTURE
itself (outnumbered by +1 neighbors), so the only way to occupy C1 is with
camo +1.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from experiments.phase_spike.phase_game import (
    PhaseGame, encode_action, decode_action, PASS_ACTION,
    cell_phase, cell_owner, EMPTY, P1_POS, P1_NEG, P2_POS, P2_NEG,
    WIN_THRESHOLD,
)
import numpy as np


def clone_game(g):
    g2 = PhaseGame.__new__(PhaseGame)
    g2.topo = g.topo
    g2.board = g.board.copy()
    g2.current_player = g.current_player
    g2.step_count = g.step_count
    g2.consecutive_passes = g.consecutive_passes
    g2.done = g.done
    g2.winner = g.winner
    g2.move_log = []
    g2.rng = g.rng
    return g2


# Manually construct the board: a 5x5 P1 cluster with one hole, P2's small cluster
# off to the side. P2 to move. The hole's neighbors are all +1, so P2 natural -1 there
# would be captured immediately.

def construct():
    g = PhaseGame()
    # Bypass step() to set the board state directly. Track move count for P2's turn.
    # P1 cells: a 5x5 block at (1..5, 1..5) but with a hole at (3,3)=27
    p1_cells = []
    for y in range(1, 6):
        for x in range(1, 6):
            idx = y * 8 + x
            if idx != 27:  # leave (3,3) empty
                p1_cells.append(idx)
    # That's 24 cells. Way too many vs P2 in alternating play. Reduce.

    # Try a smaller construction: P1 has 8 cells around (3,3); 8 P2 cells in lower right.
    # The cell (3,3)=27 is surrounded by 8 P1 +1 stones (8-neighborhood — wait,
    # neighbors are 4-connected since this is a 2D torus. Let me check.)

    return None


# Check the topology — what's the neighborhood?
g = PhaseGame()
print(f"Neighbors of cell 27 (i.e. (3,3)): {g.topo.get_neighbors(27)}")
print(f"Neighbors of cell 0: {g.topo.get_neighbors(0)}")
# So 4-connected. To outnumber-capture cell C with phase -1, need (count of +1 nbrs)
# > (count of -1 nbrs) + 2. With 4 nbrs, need all 4 +1 and 0 -1, since 4 > 0+2. ✓

# Now construct: cell C surrounded by 4 P1 +1 stones (so P2's natural -1 is captured immediately).
# Cell C's neighbors: pick C=27, neighbors = 19, 26, 28, 35.
# All 4 set to +1 (P1) → P2 natural at 27 would be 4 opp, 0 same, captured.
# But P2 camo at 27 is phase +1, would have 4 same, 0 opp; not captured.
# P2 camo BLOCKS the cell from P1 occupation.

# Build the position by direct board manipulation (bypass alternation) for the
# illustrative tactic, then re-anchor turn count.

g = PhaseGame()
# Manually plant stones to construct the puzzle position.
# Avoid step() since we need P2 to be to-move with a specific position.
# Use direct board manipulation; this is a constructed puzzle, not a real game.
g.board[19] = P1_POS  # (3,2)
g.board[26] = P1_POS  # (2,3)
g.board[28] = P1_POS  # (4,3)
g.board[35] = P1_POS  # (3,4)
# Add a few more P1 stones to push score high
g.board[18] = P1_POS  # (2,2)
g.board[20] = P1_POS  # (4,2)
g.board[34] = P1_POS  # (2,4)
g.board[36] = P1_POS  # (4,4)
# P2 cluster lower-right
g.board[44] = P2_NEG  # (4,5)
g.board[45] = P2_NEG  # (5,5)
g.board[52] = P2_NEG  # (4,6)
g.board[53] = P2_NEG  # (5,6)
g.board[60] = P2_NEG  # (4,7)
g.board[61] = P2_NEG  # (5,7)
g.board[46] = P2_NEG  # (6,5)
g.board[54] = P2_NEG  # (6,6)

# Make it P2's turn so we can study P2's move.
g.current_player = 2

print()
print("CONSTRUCTED PUZZLE POSITION (P2 to move):")
print(g.render())

# Check: if P1 were to play 27+ next, would P1 win?
g_test = clone_game(g)
g_test.current_player = 1
g_test.step(encode_action(27, +1))
print(f"\nHypothetical: P1 plays 27+ → P1 score {g_test.player_score(1):.3f}, "
      f"done={g_test.done}, winner={g_test.winner}")

# Check: if P2 plays 27- (natural), what happens?
g_test = clone_game(g)
g_test.step(encode_action(27, -1))
print(f"\nHypothetical: P2 plays 27- (natural) → "
      f"P1 score {g_test.player_score(1):.3f}, P2 score {g_test.player_score(2):.3f}, "
      f"captured={'27' if g_test.board[27]==EMPTY else 'no'}")

# Check: if P2 plays 27+ (camo), what happens?
g_test = clone_game(g)
g_test.step(encode_action(27, +1))
print(f"\nHypothetical: P2 plays 27+ (CAMO) → "
      f"P1 score {g_test.player_score(1):.3f}, P2 score {g_test.player_score(2):.3f}, "
      f"captured={'27' if g_test.board[27]==EMPTY else 'no'}, "
      f"P2 owns 27: {cell_owner(int(g_test.board[27]))==2}")

# Now: after P2 plays 27+ (camo), can P1 still push to threshold on next move?
g_after_camo = clone_game(g)
g_after_camo.step(encode_action(27, +1))  # P2 camo at 27
# Now P1 to move. Find P1's best response.
me_p1 = 1
best_diff = -1e18
best_a = None
for a in g_after_camo.get_legal_actions():
    if a == PASS_ACTION:
        continue
    sim = clone_game(g_after_camo)
    sim.step(a)
    diff = sim.player_score(1) - sim.player_score(2)
    if diff > best_diff:
        best_diff = diff
        best_a = a
        best_sim = sim
print(f"\nP1's best response after P2 camo-27+:")
d = decode_action(best_a)
ph = "+" if d["phase"] == 1 else "-"
print(f"  P1 plays {d['cell']}{ph}: scores P1={best_sim.player_score(1):.3f} "
      f"P2={best_sim.player_score(2):.3f}, "
      f"done={best_sim.done}, winner={best_sim.winner}")

# Compare to P2's best NATURAL move:
me = 2
best_diff = -1e18
best_a = None
for a in g.get_legal_actions():
    if a == PASS_ACTION:
        continue
    d = decode_action(a)
    if d["phase"] == 1:  # camo for P2
        continue
    sim = clone_game(g)
    sim.step(a)
    diff = sim.player_score(2) - sim.player_score(1)
    if diff > best_diff:
        best_diff = diff
        best_a = a
        best_sim = sim
d = decode_action(best_a)
ph = "+" if d["phase"] == 1 else "-"
print(f"\nP2's best NATURAL move: {d['cell']}{ph}, "
      f"P2={best_sim.player_score(2):.3f} P1={best_sim.player_score(1):.3f}")
# Now what does P1 play in response?
g_after_nat = best_sim
me_p1 = 1
best_diff = -1e18
best_a = None
for a in g_after_nat.get_legal_actions():
    if a == PASS_ACTION:
        continue
    sim = clone_game(g_after_nat)
    sim.step(a)
    diff = sim.player_score(1) - sim.player_score(2)
    if diff > best_diff:
        best_diff = diff
        best_a = a
        best_sim2 = sim
d = decode_action(best_a)
ph = "+" if d["phase"] == 1 else "-"
print(f"  P1 best response: {d['cell']}{ph}: scores P1={best_sim2.player_score(1):.3f} "
      f"P2={best_sim2.player_score(2):.3f}, "
      f"done={best_sim2.done}, winner={best_sim2.winner}")
