"""Greedy-vs-Greedy 30-game probe for phase_game_v2 (4-phase complex).

Greedy heuristic: 1-ply lookahead.
For each legal action, simulate the move (full capture+propagation), compute
(own_score - other_score) AFTER capture, and pick the action that maximizes this.
"""

from __future__ import annotations

import copy
import os
import sys
import time
from collections import Counter

_THIS = os.path.dirname(os.path.abspath(__file__))
# eval_v2_4_work / phase_spike / experiments / aigame
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(_THIS))))

from experiments.phase_spike.phase_game_v2 import (
    PhaseGameV2, encode_action, decode_action, PASS_ACTION, PHASE_NAMES,
)


def greedy_action(game: PhaseGameV2) -> int:
    """1-ply lookahead: pick action maximizing (own - other) score after move."""
    actions = game.get_legal_actions()
    best_score = -float("inf")
    best_action = PASS_ACTION
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
        if diff > best_score:
            best_score = diff
            best_action = a
    return best_action


def run_one_game(seed: int = 0) -> dict:
    g = PhaseGameV2(seed=seed)
    phase_counts = {1: Counter(), 2: Counter()}
    while not g.done:
        player = g.current_player
        a = greedy_action(g)
        d = decode_action(a)
        if d["type"] == "place":
            phase_counts[player][d["phase_name"]] += 1
        info = g.step(a)
        if g.step_count > 200:
            break
    return {
        "winner": g.winner,
        "steps": g.step_count,
        "p1_score": g.player_score(1),
        "p2_score": g.player_score(2),
        "phase_counts": phase_counts,
        "end_reason": g.move_log[-1].get("end_reason", "?") if g.move_log else "?",
    }


def main():
    n_games = 30
    results = []
    t0 = time.time()
    for seed in range(n_games):
        r = run_one_game(seed=seed)
        results.append(r)
        elapsed = time.time() - t0
        print(f"  seed={seed:2d}  winner={r['winner']}  steps={r['steps']:3d}  "
              f"p1={r['p1_score']:+.2f}  p2={r['p2_score']:+.2f}  "
              f"end={r['end_reason']}  ({elapsed:.1f}s elapsed)")

    p1_wins = sum(1 for r in results if r["winner"] == 1)
    p2_wins = sum(1 for r in results if r["winner"] == 2)
    draws = sum(1 for r in results if r["winner"] is None)
    decisive = p1_wins + p2_wins
    mean_steps = sum(r["steps"] for r in results) / n_games

    total_phase = {1: Counter(), 2: Counter()}
    for r in results:
        for p in (1, 2):
            total_phase[p].update(r["phase_counts"][p])

    print()
    print("=" * 60)
    print(f"30-GAME GREEDY-vs-GREEDY RESULTS (4-phase complex v2)")
    print("=" * 60)
    print(f"P1 wins:  {p1_wins} ({100*p1_wins/n_games:.0f}%)")
    print(f"P2 wins:  {p2_wins} ({100*p2_wins/n_games:.0f}%)")
    print(f"Draws:    {draws} ({100*draws/n_games:.0f}%)")
    print(f"Decisive rate: {100*decisive/n_games:.0f}%")
    print(f"Mean steps: {mean_steps:.1f}")
    print()
    print("Phase usage by player (placements only):")
    for p in (1, 2):
        total = sum(total_phase[p].values())
        if total == 0:
            print(f"  P{p}: no placements")
            continue
        bits = []
        for phase in PHASE_NAMES:
            cnt = total_phase[p][phase]
            pct = 100 * cnt / total
            bits.append(f"{phase}={cnt}({pct:.0f}%)")
        print(f"  P{p} (total={total}): {' '.join(bits)}")
    print()
    print(f"End reason histogram:")
    end_reasons = Counter(r["end_reason"] for r in results)
    for er, c in end_reasons.most_common():
        print(f"  {er}: {c}")
    print(f"Total time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
