"""Seat-swap probe: under greedy-vs-greedy, ALL games are deterministic (no RNG
in greedy). So all 30 seeds produce the SAME game. Verify that and then test
"P2 starts" (give P1 a forced pass) to see if move-order alone causes the
imbalance.
"""

from __future__ import annotations

import copy
import os
import sys
import time

_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(_THIS))))

from experiments.phase_spike.phase_game_v2 import (
    PhaseGameV2, encode_action, decode_action, PASS_ACTION, PHASE_NAMES,
)


def greedy_action(game: PhaseGameV2, tiebreak_rng=None) -> int:
    actions = game.get_legal_actions()
    best_score = -float("inf")
    best_actions = []
    me = game.current_player
    other = 3 - me
    for a in actions:
        sim = copy.deepcopy(game)
        try:
            sim.step(a)
        except Exception:
            continue
        own = sim.player_score(me)
        opp = sim.player_score(other)
        diff = own - opp
        if a == PASS_ACTION:
            diff -= 1e-6
        if diff > best_score + 1e-9:
            best_score = diff
            best_actions = [a]
        elif diff > best_score - 1e-9:
            best_actions.append(a)
    if tiebreak_rng is not None and len(best_actions) > 1:
        return int(tiebreak_rng.choice(best_actions))
    return best_actions[0]


def run_game(seed=None, p1_pass_first=False):
    """If p1_pass_first, P1's first move is forced to PASS, giving P2 effective
    first-mover advantage."""
    import numpy as np
    rng = np.random.default_rng(seed) if seed is not None else None
    g = PhaseGameV2()
    while not g.done:
        if p1_pass_first and g.step_count == 0 and g.current_player == 1:
            g.step(PASS_ACTION)
            continue
        a = greedy_action(g, tiebreak_rng=rng)
        g.step(a)
        if g.step_count > 200:
            break
    return {
        "winner": g.winner,
        "steps": g.step_count,
        "p1_score": g.player_score(1),
        "p2_score": g.player_score(2),
        "end_reason": g.move_log[-1].get("end_reason", "?") if g.move_log else "?",
    }


def main():
    print("=== Determinism check: greedy is deterministic if no ties ===")
    r0 = run_game(seed=None)
    print(f"  Game 1 (no rng): winner={r0['winner']}  P1={r0['p1_score']:+.3f}  "
          f"P2={r0['p2_score']:+.3f}  steps={r0['steps']}")
    r1 = run_game(seed=None)
    print(f"  Game 2 (no rng): winner={r1['winner']}  P1={r1['p1_score']:+.3f}  "
          f"P2={r1['p2_score']:+.3f}  steps={r1['steps']}")
    print(f"  Identical? {r0 == r1}")
    print()

    print("=== Random tie-break: 30 seeds, greedy with random tiebreak ===")
    p1w = p2w = draws = 0
    for seed in range(30):
        r = run_game(seed=seed)
        if r["winner"] == 1: p1w += 1
        elif r["winner"] == 2: p2w += 1
        else: draws += 1
    print(f"  P1 wins: {p1w}/30  P2 wins: {p2w}/30  Draws: {draws}/30")
    print()

    print("=== Forced-pass-first test: P1 passes first, then both play greedy ===")
    print("    (This gives P2 effective first-move advantage.)")
    p1w = p2w = draws = 0
    for seed in range(30):
        r = run_game(seed=seed, p1_pass_first=True)
        if r["winner"] == 1: p1w += 1
        elif r["winner"] == 2: p2w += 1
        else: draws += 1
    print(f"  With P1 passing first: P1 wins: {p1w}/30  P2 wins: {p2w}/30  Draws: {draws}/30")


if __name__ == "__main__":
    main()
