"""Construct a position where cell C is surrounded by 4 P1+1 stones such that:
- P2 natural -1 at C: captured immediately (cell empty after move)
- P2 camo +1 at C: not captured, denies P1
- The deny matters: P1's natural alternative move is restricted.

Position: a chunky P1 cluster with hole at C=27. The 4 nbrs of 27 = {19, 26, 28, 35} are all P1+1.
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


def make_position():
    g = PhaseGame()
    # P1 cluster: 9 cells around 27, plus a few more for score.
    # 4-nbrs of 27: 19, 26, 28, 35. These MUST be P1+1.
    # Plus their nbrs to support: 18, 20, 34, 36, 11, 25, 29, 43.
    # Make a 3x3 minus center pattern.
    # Just the ring around 27 — P1 score will be lower so adding camo +1 at 27
    # won't push past threshold. The 4 nbrs (19, 26, 28, 35) being P1+1 is what
    # makes natural-27 captured. Score: 8 × 1.8831 = 15.06 (no neighbors counted on 27).
    p1 = [18, 19, 20, 26, 28, 34, 35, 36]  # ring around 27 (8 cells)
    for c in p1:
        g.board[c] = P1_POS

    # P2 cluster — make it strong enough that P2 isn't hopelessly behind.
    p2 = [49, 50, 51, 57, 58, 59]
    for c in p2:
        g.board[c] = P2_NEG

    return g


g = make_position()
g.current_player = 2
print("Position:")
print(g.render())
print()

# Test scenarios
print("--- Tests ---")

# A: P1 plays 27+ now (P2 had passed, hypothetical)
g_test = clone_game(g)
g_test.current_player = 1
g_test.step(encode_action(27, +1))
print(f"If P1 plays 27+: P1={g_test.player_score(1):.3f} P2={g_test.player_score(2):.3f} "
      f"done={g_test.done} winner={g_test.winner}")

# Capture check: is 27- captured? 4 P1+1 neighbors → 4 opp, 0 same → 4 > 0+2 ✓ captured.
g_test = clone_game(g)
g_test.step(encode_action(27, -1))
print(f"P2 plays 27- (natural): P1={g_test.player_score(1):.3f} P2={g_test.player_score(2):.3f} "
      f"cell27={'empty' if g_test.board[27]==EMPTY else g_test.board[27]} "
      f"(captured if empty)")

# Camo check
g_test = clone_game(g)
g_test.step(encode_action(27, +1))
print(f"P2 plays 27+ (CAMO): P1={g_test.player_score(1):.3f} P2={g_test.player_score(2):.3f} "
      f"cell27_owner={cell_owner(int(g_test.board[27]))}")

# Now: search ALL P2 moves and rank by 2-ply (P2 - P1) after P1's best response.
def best_p1_response(g):
    legal = g.get_legal_actions()
    placements = [a for a in legal if a != PASS_ACTION]
    best_score = -1e18
    best_a = None
    best_sim = None
    for a in placements:
        sim = clone_game(g)
        sim.step(a)
        if sim.done and sim.winner == 1:
            return a, sim, "P1 WINS"
        score = sim.player_score(1) - sim.player_score(2)
        if score > best_score:
            best_score = score
            best_a = a
            best_sim = sim
    return best_a, best_sim, "no immediate win"


print()
print("Full P2 action search (2-ply, P1 best-responds):")
results = []
for a in g.get_legal_actions():
    if a == PASS_ACTION:
        continue
    sim = clone_game(g)
    info = sim.step(a)
    if sim.done:
        if sim.winner == 2:
            score_after = 1000.0
        elif sim.winner is None:
            score_after = 0.0
        else:
            score_after = -1000.0
        d = decode_action(a)
        results.append((score_after, d["cell"], d["phase"], "DONE"))
        continue
    p1_a, p1_sim, note = best_p1_response(sim)
    if p1_sim is None:
        score_after = sim.player_score(2) - sim.player_score(1)
        note = "P1 has no move"
    elif p1_sim.done and p1_sim.winner == 1:
        score_after = -1000.0
    else:
        score_after = p1_sim.player_score(2) - p1_sim.player_score(1)
    d = decode_action(a)
    p1_d = decode_action(p1_a) if p1_a is not None else None
    p1_label = f"P1->{p1_d['cell']}{'+' if p1_d['phase']==1 else '-'}" if p1_d else "P1->none"
    results.append((score_after, d["cell"], d["phase"], f"{note}, {p1_label}"))

results.sort(key=lambda r: -r[0])
print(f"  {'rank':<5}{'cell':<6}{'phase':<7}{'camo':<6}{'P2-P1 (2ply)':<16}note")
print("Top 5:")
for i, (s, cell, phase, note) in enumerate(results[:5], 1):
    is_camo = phase != -1
    camo = "CAMO" if is_camo else "nat"
    ph = "+1" if phase == 1 else "-1"
    if s > 500:
        marker = " P2 WIN"
    elif s < -500:
        marker = " P1 WINS"
    else:
        marker = ""
    print(f"  {i:<5}{cell:<6}{ph:<7}{camo:<6}{s:+.3f}  {marker}    {note}")

# Then print only the CAMO and cell-27 results explicitly:
print("\nCamo and cell-27 entries (any rank):")
for i, (s, cell, phase, note) in enumerate(results, 1):
    is_camo = phase != -1
    if not is_camo and cell != 27:
        continue
    camo = "CAMO" if is_camo else "nat"
    ph = "+1" if phase == 1 else "-1"
    if s > 500:
        marker = " P2 WIN"
    elif s < -500:
        marker = " P1 WINS"
    else:
        marker = ""
    print(f"  rank {i:<4}cell {cell:<4}{ph:<7}{camo:<6}{s:+.3f}{marker}    {note}")
