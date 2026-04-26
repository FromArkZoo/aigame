"""Find a tactical position where P2's only non-losing move is camo-deny.

Setup: P1 has score X with X < 22.65. There exists cell C such that:
- placing P1 +1 at C → P1 score > 22.65 (P1 wins)
- placing P2 -1 at C → captured immediately (cell empty), P1 still threatens
- placing P2 +1 (camo) at C → cell remains occupied by P2, P1 can't place there
- After P2 camo, P1 has no winning placement on the next move.

Then compare to the best alternative for P2 to confirm camo is uniquely best.
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


def setup_position():
    """Build: P1 cluster ~3x3 around (3,3) with hole at 27. Plus P2 cluster
    in lower right.

    P1 cells: 18, 19, 20, 26, 28, 34, 35, 36 (8 cells around 27).
    P2 cells: an equally sized cluster to keep board balanced.
    Then add a couple more P1 stones to nudge P1 close to threshold.
    """
    g = PhaseGame()
    p1 = [18, 19, 20, 26, 28, 34, 35, 36]  # 8 cells, ring around 27
    for c in p1:
        g.board[c] = P1_POS
    # P2 cluster much smaller — P2 trails by a lot, can't win this turn.
    p2 = [44, 53, 62]  # 3 sparse P2 stones (low score)
    for c in p2:
        g.board[c] = P2_NEG
    # Add 2 more P1 stones; choose cells that give bigger boost.
    extra_p1 = [11, 17]
    for c in extra_p1:
        g.board[c] = P1_POS
    return g


g = setup_position()
g.current_player = 2
print("Setup:")
print(g.render())

# Score check: what does P1 get for placing at 27?
g_p1_wins = clone_game(g)
g_p1_wins.current_player = 1
info = g_p1_wins.step(encode_action(27, +1))
print(f"If P1 plays 27+ NOW: P1 score = {g_p1_wins.player_score(1):.3f}, "
      f"P2 score = {g_p1_wins.player_score(2):.3f}, done={g_p1_wins.done}, winner={g_p1_wins.winner}")

print()
print("=" * 70)
print("ANALYSIS: P2 to move, P1 threatens to win with 27+")
print("=" * 70)

def best_p1_response(g):
    legal = g.get_legal_actions()
    placements = [a for a in legal if a != PASS_ACTION]
    best_diff = -1e18
    best_a = None
    best_sim = None
    for a in placements:
        sim = clone_game(g)
        sim.step(a)
        if sim.done and sim.winner == 1:
            return a, sim, "P1 WINS"
        diff = sim.player_score(1) - sim.player_score(2)
        if diff > best_diff:
            best_diff = diff
            best_a = a
            best_sim = sim
    return best_a, best_sim, "no immediate win"

# P2 options:
options = [
    ("P2 nat 27- (will be captured)", encode_action(27, -1)),
    ("P2 CAMO 27+ (denial)", encode_action(27, +1)),
    ("P2 nat 21- (extend cluster)", encode_action(21, -1)),  # next to P2 cluster... actually 21 is near P1 cluster
    ("P2 nat 47- (extend SE)", encode_action(47, -1)),
    ("P2 nat 63- (corner)", encode_action(63, -1)),
    ("P2 PASS", PASS_ACTION),
]

# Now also try ALL possible P2 actions and rank them by 2-ply outcome:
# After P2 move, P1 picks the move that maximizes P1's score-P2's score.
# P2 wants to MINIMIZE that.

print("\nFull search of all P2 actions, ranked by (P2-P1) after P1's best response:")
me = g.current_player  # P2
results = []
for a in g.get_legal_actions():
    if a == PASS_ACTION:
        continue
    sim = clone_game(g)
    info = sim.step(a)
    if sim.done:
        # P2 lost or won immediately?
        if sim.winner == 2:
            score = 1000.0
        elif sim.winner == 1:
            score = -1000.0
        else:
            score = 0.0
        d = decode_action(a)
        results.append((score, d["cell"], d["phase"], "DONE"))
        continue
    # P1 plays best response
    p1_a, p1_sim, note = best_p1_response(sim)
    if p1_sim is None:
        score = sim.player_score(2) - sim.player_score(1)
    elif p1_sim.done and p1_sim.winner == 1:
        score = -1000.0
    else:
        score = p1_sim.player_score(2) - p1_sim.player_score(1)
    d = decode_action(a)
    results.append((score, d["cell"], d["phase"], note))

# Sort high-to-low (P2's perspective)
results.sort(key=lambda r: -r[0])
print(f"  {'rank':<5}{'cell':<6}{'phase':<7}{'camo':<6}{'P2-P1 after P1 reply':<24}{'note'}")
for i, (s, cell, phase, note) in enumerate(results[:15], 1):
    nat_phase = -1  # P2 natural
    is_camo = phase != nat_phase
    camo = "CAMO" if is_camo else "nat"
    ph = "+1" if phase == 1 else "-1"
    if s > 500:
        marker = " <-- P2 WIN"
    elif s < -500:
        marker = " <-- P1 wins"
    else:
        marker = ""
    print(f"  {i:<5}{cell:<6}{ph:<7}{camo:<6}{s:+.3f}{marker:<20}  {note}")
print()
print("INTERPRETATION:")
print("  Best move(s) = highest score in column. Camo of cell 27 should be the unique")
print("  non-losing move if construction worked.")

