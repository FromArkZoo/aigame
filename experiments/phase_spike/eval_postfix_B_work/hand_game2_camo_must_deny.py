"""Find a position where P2's only non-losing move is camo.

Setup: P1 is one move from winning (cell 27 placement crosses 22.65).
P2 cannot win on this turn. P2's options:
  - Natural -1 placement somewhere (won't deny cell 27; P1 wins next turn).
  - Pass: P1 wins next turn.
  - Natural -1 at cell 27: captured immediately, cell becomes empty, P1 wins next turn.
  - CAMO +1 at cell 27: cell stays occupied, P1 cannot place there.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from experiments.phase_spike.phase_game import (
    PhaseGame, encode_action, decode_action, PASS_ACTION,
    cell_phase, cell_owner, EMPTY, P1_POS, P1_NEG, P2_POS, P2_NEG,
    WIN_THRESHOLD,
)


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


# We need P1 score-without-cell-27 to be just under threshold,
# but with cell 27 to be just over.
# Each P1 +1 stone with k P1 +1 neighbors contributes:
#   own self: 0.9323 (always positive)
#   neighbors: each gets 0.4754 (decay × strength)
# Score for P1 cell C = 0.9323 + 0.4754 * (# P1-+1 neighbors)
# Plus, if cell C is empty's neighbor and surrounded by k P1+1 stones, those
# project 0.4754 each onto C — but C empty doesn't score.

# Let's just experiment. Goal: stones such that P1 score is near 22.0 and
# placing any +1 stone at cell 27 would push to 22.65+ via radiation.

g = PhaseGame()

# Layout: a 5x5 P1 cluster centered on (3,3) but with hole at 27
# Neighbors of 27 = {19, 26, 28, 35}. Each of those gets +0.4754 from 27 if filled.
# So we WANT cells 19, 26, 28, 35 to be P1+1 (so when P2 fills 27 with camo +1,
# those P1 cells get a BIG boost). Wait, that's backwards: we want
# P1 score to JUMP when P1 places at 27, not when P2 does.

# Compute by hand. With P1+1 stones at A = {18, 19, 20, 26, 28, 34, 35, 36}
# (the 8 cells surrounding 27 in the king-neighborhood, but capture only uses
# 4-connected so 8-cell ring works fine), P1's score:
# - Self-contribution: 8 * 0.9323 = 7.4584
# - Neighbor-contribution: count edges from each P1 stone to other P1 stones × 0.4754.
#   Stones: 18, 19, 20, 26, 28, 34, 35, 36. Edges (4-connected):
#   18-19, 18-26, 19-20, 19-27(empty), 20-28, 26-27(empty), 26-34, 27-28(empty), 27-35(empty),
#   28-36, 34-35, 35-36. Wait, 27 is empty so no contribution there.
#   P1-to-P1 edges:
#     18-19, 18-26, 19-20, 20-28, 26-34, 28-36, 34-35, 35-36
#   That's 8 edges. Each contributes 2 × 0.4754 (each side gets it from the other).
# Score boost per stone from being a neighbor of another stone: each P1 stone
# accrues 0.4754 per +1 neighbor. So total = sum over P1 stones of (0.4754 × #+1 nbrs).
# Stone 18: nbrs are 17(empty), 19, 10(empty), 26 → 2 P1+1 nbrs → 2 × 0.4754
# Stone 19: nbrs 18, 20, 11(empty), 27(empty) → 2 nbrs
# Stone 20: nbrs 19, 21(empty), 12(empty), 28 → 2 nbrs
# Stone 26: nbrs 25(empty), 27(empty), 18, 34 → 2 nbrs
# Stone 28: nbrs 27(empty), 29(empty), 20, 36 → 2 nbrs
# Stone 34: nbrs 33(empty), 35, 26, 42(empty) → 2 nbrs
# Stone 35: nbrs 34, 36, 27(empty), 43(empty) → 2 nbrs
# Stone 36: nbrs 35, 37(empty), 28, 44(empty) → 2 nbrs
# Total nbr-contributions: 8 × 2 × 0.4754 = 7.6064
# Self-contribs: 8 × 0.9323 = 7.4584
# P1 score = 7.4584 + 7.6064 = 15.06  (need to add at-self 0.9323 each, that's already counted)
# Actually p1_score = sum over P1 cells of cell_value × +1 = sum cell_values
# cell_value(18) = 0.9323 + 0.4754 × (#stones at distance 1 with phase ±)
# We don't include 27 (empty), so cell_value(18) = 0.9323 + 0.4754 × 2 = 1.8831
# Same for 19, 20, 26, 28, 34, 35, 36 → all 1.8831
# Total = 8 × 1.8831 = 15.06

# Now place ONE more P1+1 stone somewhere it adds a lot. Say cell 11 (above 19):
# - Self: 0.9323
# - Cell 11's nbrs in P1: 19 (yes), 10 (no), 12 (no), 3 (no). → 1 nbr
# - cell_value(11) = 0.9323 + 0.4754 × 1 = 1.4077
# Plus, cell 19's nbr count goes up by 1: now 19 has 3 P1 nbrs → cell_value(19) = 0.9323 + 0.4754×3 = 2.358
# So P1 increment = 1.4077 + 0.4754 = 1.883
# Total: 16.94

# Let's add more cells. We need to reach close to but below 22.65. Try cluster 6x3.
# Or instead, just make it a 4x4 minus corner: cells (1..4, 1..4) = {9,10,11,12, 17,18,19,20, 25,26,27,28, 33,34,35,36}
# Replace 27 with empty.

cells_in_cluster = [9, 10, 11, 12, 17, 18, 19, 20, 25, 26, 28, 33, 34, 35, 36]
# That's 15 cells (4x4 minus 27).
for c in cells_in_cluster:
    g.board[c] = P1_POS

# Compute P1 score
print(f"Plan: P1 has 15 stones. P1 score = {g.player_score(1):.3f}")

# Let's see if it's near threshold
print(f"Threshold: {WIN_THRESHOLD:.3f}")
# If P1 played 27+: simulate
g_test = PhaseGame()
for c in cells_in_cluster:
    g_test.board[c] = P1_POS
g_test.current_player = 1
g_test.step(encode_action(27, +1))
print(f"If P1 plays 27+: P1 score = {g_test.player_score(1):.3f}, done={g_test.done}, winner={g_test.winner}")

# Need to also have some P2 stones for context. Add a small P2 cluster far away.
p2_cells = [60, 61, 62, 63]
for c in p2_cells:
    g.board[c] = P2_NEG
print(f"After adding P2 corner cluster: P1 score = {g.player_score(1):.3f}, "
      f"P2 score = {g.player_score(2):.3f}")

# OK now make this P2's turn.
g.current_player = 2
print()
print("PUZZLE POSITION (P2 to move):")
print(g.render())

# Test all P2 options at cell 27 and other key cells
print("\n--- Tests ---")
for label, action in [
    ("P2 natural (27-)", encode_action(27, -1)),
    ("P2 CAMO (27+)", encode_action(27, +1)),
    ("P2 natural elsewhere (53-)", encode_action(53, -1)),
    ("P2 PASS", PASS_ACTION),
]:
    g_test = clone_game(g)
    info = g_test.step(action)
    p1_owned_27 = (cell_owner(int(g_test.board[27])) == 1) if not g_test.done else False
    cap = info.get("captured", [])
    print(f"  {label}: P1={g_test.player_score(1):.3f} P2={g_test.player_score(2):.3f}  "
          f"cell27_owner={cell_owner(int(g_test.board[27]))}  captured={cap}")
    if g_test.done:
        print(f"    GAME ENDED: winner=P{g_test.winner}, reason={info.get('end_reason')}")
        continue
    # Now P1's best response
    legal = g_test.get_legal_actions()
    placements = [a for a in legal if a != PASS_ACTION]
    best_diff = -1e18
    best_a = None
    for a in placements:
        sim = clone_game(g_test)
        sim.step(a)
        diff = sim.player_score(1) - sim.player_score(2)
        if diff > best_diff:
            best_diff = diff
            best_a = a
            best_sim = sim
    if best_a is not None:
        d = decode_action(best_a)
        ph = "+" if d["phase"] == 1 else "-"
        won = "WIN-P1" if best_sim.winner == 1 else ("DONE" if best_sim.done else "ongoing")
        print(f"    Then P1's best move: {d['cell']}{ph} -> P1={best_sim.player_score(1):.3f} "
              f"P2={best_sim.player_score(2):.3f}  ({won})")
