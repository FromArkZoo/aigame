"""Hand-played Game 2 exploration — find a position where camouflage is actually
the BEST move under a 1-ply (own_score - other_score) criterion.

Strategy: Build the same shape as Game 1 up to a critical position, then for the
side facing imminent loss, evaluate ALL legal actions (including all camo moves)
to see if any camo move beats the best natural move.
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from experiments.phase_spike.phase_game import (
    PhaseGame, encode_action, decode_action, PASS_ACTION,
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


def evaluate_all_actions(g: PhaseGame, top_k: int = 8) -> list:
    me = g.current_player
    other = 3 - me
    legal = g.get_legal_actions()
    placements = [a for a in legal if a != PASS_ACTION]
    rows = []
    for a in placements:
        sim = clone_game(g)
        sim.step(a)
        s_me = sim.player_score(me)
        s_other = sim.player_score(other)
        d = decode_action(a)
        natural_phase = 1 if me == 1 else -1
        is_camo = d["phase"] != natural_phase
        rows.append((s_me - s_other, s_me, s_other, d["cell"], d["phase"], is_camo, sim.done, sim.winner))
    rows.sort(key=lambda r: -r[0])
    return rows[:top_k]


def show_top(g, label):
    print(f"\n=== Position: {label} (P{g.current_player} to move) ===")
    print(g.render())
    rows = evaluate_all_actions(g, top_k=10)
    print("Top 10 actions by (own - other) score:")
    print(f"  {'rank':<5}{'cell':<6}{'phase':<7}{'camo':<6}{'own':<8}{'other':<8}{'diff':<8}{'wins?'}")
    for i, (diff, s_me, s_other, cell, phase, is_camo, done, winner) in enumerate(rows, 1):
        ph = "+1" if phase == 1 else "-1"
        camo = "CAMO" if is_camo else "nat"
        end = ""
        if done:
            end = f"WIN-P{winner}" if winner == g.current_player else (f"LOSS-P{winner}" if winner else "DRAW")
        print(f"  {i:<5}{cell:<6}{ph:<7}{camo:<6}{s_me:+.3f}  {s_other:+.3f}  {diff:+.3f}  {end}")


# Reproduce game 1's setup but stop at move 14 to give P2 a chance to consider
# camo as a way to disrupt P1's escalating cluster.
moves = [
    (1, 27, +1),
    (2, 36, -1),
    (1, 28, +1),
    (2, 35, -1),
    (1, 19, +1),
    (2, 44, -1),
    (1, 20, +1),
    (2, 43, -1),
    (1, 26, +1),
    (2, 37, -1),
    (1, 18, +1),
    (2, 45, -1),
    (1, 11, +1),  # P1 score now ~13.18; about to outpace P2 because of move-1 lead
]

g = PhaseGame()
for i, (player, cell, phase) in enumerate(moves, 1):
    a = encode_action(cell, phase)
    g.step(a)
    print(f"  move {i:2d}: P{player} plays {cell}{'+' if phase==1 else '-'}"
          f"  scores P1={g.player_score(1):+.2f} P2={g.player_score(2):+.2f}")

# Now P2 to move. Let's see all candidate actions including camo.
show_top(g, "after move 13 (P1 just played 11+)")
