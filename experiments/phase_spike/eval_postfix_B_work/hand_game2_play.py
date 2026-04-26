"""HAND-PLAYED GAME 2: each player allowed camouflage.

I (the human evaluator) play both sides, picking moves I find strategically
appealing. After each move I evaluate whether camo would have been better.
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


def evaluate_alt(g, my_action, label=""):
    """Print 1-ply diff for my_action and the best alternative."""
    me = g.current_player
    sim = clone_game(g)
    info = sim.step(my_action)
    s_me = sim.player_score(me)
    s_other = sim.player_score(3 - me)
    diff = s_me - s_other
    captured = info.get("captured", [])
    end = info.get("end_reason", "")
    d = decode_action(my_action)
    print(f"  Played: cell {d['cell']} phase {'+' if d['phase']==1 else '-'} "
          f"({label})  →  P{me}={s_me:.3f}  P{3-me}={s_other:.3f}  diff={diff:+.3f} "
          f"captured={captured} end={end}")

    # Best alternative
    best_diff = -1e18
    best_a = None
    for a in g.get_legal_actions():
        if a == PASS_ACTION or a == my_action:
            continue
        sim2 = clone_game(g)
        sim2.step(a)
        d2 = sim2.player_score(me) - sim2.player_score(3 - me)
        if d2 > best_diff:
            best_diff = d2
            best_a = a
    if best_a is not None:
        d2 = decode_action(best_a)
        nat = 1 if me == 1 else -1
        is_camo = d2["phase"] != nat
        camo_label = " [CAMO]" if is_camo else ""
        print(f"    Best alt: cell {d2['cell']} phase {'+' if d2['phase']==1 else '-'}"
              f"{camo_label} would yield diff {best_diff:+.3f}")
    return sim, info


# I'll play a more aggressive game where I deliberately try camo as a
# "spoiler" move and see if it pays off.

g = PhaseGame()

# OPENING — natural moves to establish clusters
print("=" * 70)
print("HAND-PLAYED GAME 2 — camouflage allowed")
print("=" * 70)

moves_with_commentary = [
    # (player, cell, phase, comment)
    (1, 27, +1, "P1 opens center natural"),
    (2, 36, -1, "P2 mirror diagonal natural"),
    (1, 28, +1, "P1 extends east"),
    (2, 35, -1, "P2 mirror west"),
    (1, 19, +1, "P1 extends north"),
    (2, 44, -1, "P2 extends south"),
    (1, 20, +1, "P1 fills 4-cell square"),
    (2, 43, -1, "P2 fills 4-cell square"),
    # Now try a CAMO move for P1
    (1, 37, -1, "P1 CAMO at 37 — INTERESTING. 37 is between P1 and P2 clusters."
                " 37 nbrs are 36(P2-1), 38, 29, 45. Currently 1 same-phase (-1), so"
                " P1@-1 there has 1 same nbr, 0 opp; not capturable. P1 score impact?"),
]

for player, cell, phase, comment in moves_with_commentary:
    if g.done:
        print(f"-- game ended --")
        break
    a = encode_action(cell, phase)
    print(f"\nMove {g.step_count + 1}: P{player} plays {cell}{'+' if phase==1 else '-'}")
    print(f"  Reasoning: {comment}")
    sim, info = evaluate_alt(g, a, label="my pick")
    g.step(a)

print("\nBoard after move 9:")
print(g.render())
print()

# Continue. We need to see whether camo at 37 was good.
# After P1 camo at 37: P1 score = ? let's see.
# Cell 37 nbrs are 36 (P2-1), 38 (empty), 29 (empty), 45 (empty). 1 same, 0 opp, no capture.
# P1 score: lose value at 37 contribution (camo radiates -1 into 36, 38, 29, 45 — but
# these don't contribute to P1 score except radiated values to 28, 36's neighbors).
# Cell 38 was empty; now influenced by 37's -1 phase. Doesn't matter directly for P1's score.
# P1 owns 37 with phase -1 → contributes value(37) × +1 to P1.
# value(37) = sum of nbrs' phases × strength × decay = 36's -1 × 0.4754 + 37's own -1 × 0.9323
#           = -0.4754 + (-0.9323) = -1.4077
# So P1 score gets -1.4077 from this cell. NEGATIVE!

# This was a deliberately bad camo to confirm camo penalty.

# Now let P2 respond and continue.
moves_continue = [
    (2, 45, -1, "P2 extends pressing the camo cell from below"),
    (1, 26, +1, "P1 extends west natural — safer than camo"),
    (2, 51, -1, "P2 extends west"),
    (1, 18, +1, "P1 extends NW"),
    (2, 52, -1, "P2 extends SW"),
    (1, 11, +1, "P1 pushes north"),
    (2, 53, -1, "P2 pushes east"),
    (1, 21, +1, "P1 pushes east"),
    (2, 42, -1, "P2 pushes west"),
    (1, 12, +1, "P1 final push to threshold"),
]

for player, cell, phase, comment in moves_continue:
    if g.done:
        print(f"-- game ended --")
        break
    a = encode_action(cell, phase)
    print(f"\nMove {g.step_count + 1}: P{player} plays {cell}{'+' if phase==1 else '-'}")
    print(f"  Reasoning: {comment}")
    sim, info = evaluate_alt(g, a, label="my pick")
    g.step(a)

print("\nFinal board:")
print(g.render())
