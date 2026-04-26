"""Find positions where camo is the BEST move for the to-move player.

Strategy: After each move in a self-play game, evaluate every legal action
including camo. Flag any state where the highest-scoring action is a camo move.

Also test the 'threshold denial' construction: when P1 is one move from winning,
can P2 deny by occupying a single critical cell with a camo stone (which won't
be captured)?
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from experiments.phase_spike.phase_game import (
    PhaseGame, encode_action, decode_action, PASS_ACTION,
    cell_phase, cell_owner, EMPTY, P1_POS, P1_NEG, P2_POS, P2_NEG,
    WIN_THRESHOLD,
)


def clone_game(g: PhaseGame) -> PhaseGame:
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


def score_action_2ply(g: PhaseGame, a: int, depth_remaining: int = 1) -> float:
    """Apply action a, then have opponent respond optimally (1-ply greedy),
    return (me - other) score after opponent's reply.
    """
    me = g.current_player
    sim = clone_game(g)
    info = sim.step(a)
    if sim.done:
        # If I won, return huge positive; if I lost, huge negative.
        if sim.winner == me:
            return 1000.0
        elif sim.winner is None:
            return 0.0
        else:
            return -1000.0
    # opponent moves greedily
    other = sim.current_player
    legal = sim.get_legal_actions()
    placements = [aa for aa in legal if aa != PASS_ACTION]
    best_diff_other = -1e18
    best_a_other = None
    for aa in placements:
        sim2 = clone_game(sim)
        sim2.step(aa)
        diff = sim2.player_score(other) - sim2.player_score(me)
        if diff > best_diff_other:
            best_diff_other = diff
            best_a_other = aa
    if best_a_other is None:
        return sim.player_score(me) - sim.player_score(other)
    sim3 = clone_game(sim)
    sim3.step(best_a_other)
    return sim3.player_score(me) - sim3.player_score(other)


def show_2ply_top(g, label):
    print(f"\n=== Position: {label} (P{g.current_player} to move) ===")
    print(g.render())
    me = g.current_player
    legal = g.get_legal_actions()
    placements = [a for a in legal if a != PASS_ACTION]
    rows = []
    for a in placements:
        d = decode_action(a)
        nat_phase = 1 if me == 1 else -1
        is_camo = d["phase"] != nat_phase
        v = score_action_2ply(g, a)
        rows.append((v, d["cell"], d["phase"], is_camo))
    rows.sort(key=lambda r: -r[0])
    print("Top 8 actions by 2-ply (me - other) score, opponent best-responds:")
    print(f"  {'rank':<5}{'cell':<6}{'phase':<7}{'camo':<6}{'2ply diff'}")
    for i, (v, cell, phase, is_camo) in enumerate(rows[:8], 1):
        ph = "+1" if phase == 1 else "-1"
        camo = "CAMO" if is_camo else "nat"
        print(f"  {i:<5}{cell:<6}{ph:<7}{camo:<6}{v:+.4f}")
    # Also report best NATURAL and best CAMO separately
    nat_rows = [r for r in rows if not r[3]]
    camo_rows = [r for r in rows if r[3]]
    if nat_rows and camo_rows:
        print(f"\n  Best natural: {nat_rows[0][0]:+.4f}    Best camo: {camo_rows[0][0]:+.4f}")
        print(f"  Camo beats natural? {'YES' if camo_rows[0][0] > nat_rows[0][0] else 'no'}")


# Construct a "P1 is one move from threshold" position with multiple equally
# attractive cells. P2 must deny one with camo.

# Build manually: fill an L-shape for P1 in upper-left, and a smaller P2 cluster
# on the lower-right, such that P1's NEXT move puts him over threshold.

def build_threshold_denial_setup():
    """Build a position where:
    - It's P2's turn
    - P1 is just below threshold; P1's next move could push over
    - P2 trails. Camo denial by P2 might be the only way to block P1's plan.
    """
    g = PhaseGame()
    # Same opening as Game 1, but stop just before P1 hits 22.65.
    # Game 1 had P1 at 20.73 after move 19 (P1 plays 21+). Then move 20: P2 plays 42-,
    # then move 21: P1 plays 13+ → P1=23.56 (win).
    # We want to STOP at "P1=20.73, P2=20.73, after move 20" so it's P1's turn next.
    # Hmm — we want it to be P2's turn so P2 can consider denial.
    # So stop after move 19 (P2's turn): P1=20.73, P2=18.84.
    moves = [
        (1, 27, +1), (2, 36, -1),
        (1, 28, +1), (2, 35, -1),
        (1, 19, +1), (2, 44, -1),
        (1, 20, +1), (2, 43, -1),
        (1, 26, +1), (2, 37, -1),
        (1, 18, +1), (2, 45, -1),
        (1, 11, +1), (2, 52, -1),
        (1, 12, +1), (2, 51, -1),
        (1, 10, +1), (2, 53, -1),
        (1, 21, +1),  # move 19
        # P2 to move (move 20). Position: P1=20.73, P2=18.84.
    ]
    for player, cell, phase in moves:
        a = encode_action(cell, phase)
        g.step(a)
    return g, None, None


print("=" * 72)
print("THRESHOLD-DENIAL SETUP")
print("=" * 72)
g, _, _ = build_threshold_denial_setup()
print(g.render())
print(f"P1 score: {g.player_score(1):.3f}, P2 score: {g.player_score(2):.3f}")
print(f"To-move: P{g.current_player}")

# Now run a 2-ply analysis on P2's best move including all camo options.
show_2ply_top(g, "P2 to move; P1 leads, P2 must consider denial")
