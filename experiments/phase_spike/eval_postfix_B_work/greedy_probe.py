"""50-game greedy-vs-greedy probe for the post-fix phase-extended game.

Greedy heuristic: pick the (cell, phase) action that maximizes
  (own player score after move) - (other player score after move)
using a 1-ply simulation. Pass is allowed only if no placements exist.

Tracks: P1 wins / P2 wins / draws, decisive rate, camouflage usage rate,
end-reason histogram, mean game length.
"""

from __future__ import annotations

import sys
import os
import copy
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import numpy as np

from experiments.phase_spike.phase_game import (
    PhaseGame, encode_action, decode_action, PASS_ACTION,
    P1_POS, P1_NEG, P2_POS, P2_NEG, EMPTY,
    cell_owner, cell_phase,
)


def clone_game(g: PhaseGame) -> PhaseGame:
    g2 = PhaseGame.__new__(PhaseGame)
    g2.topo = g.topo  # safe: read-only
    g2.board = g.board.copy()
    g2.current_player = g.current_player
    g2.step_count = g.step_count
    g2.consecutive_passes = g.consecutive_passes
    g2.done = g.done
    g2.winner = g.winner
    g2.move_log = []  # don't deep-copy log for speed
    g2.rng = g.rng
    return g2


def greedy_action(g: PhaseGame, rng=None) -> int:
    """Pick action maximizing (own - other) score after 1-ply simulation.

    Ties are broken uniformly at random using `rng` so that 50 games with
    different seeds produce 50 distinct trajectories. A tiny tolerance is
    used when comparing diffs so floating-point ties register as ties.
    """
    me = g.current_player
    other = 3 - me
    legal = g.get_legal_actions()
    placements = [a for a in legal if a != PASS_ACTION]
    if not placements:
        return PASS_ACTION

    scored = []
    for a in placements:
        sim = clone_game(g)
        try:
            sim.step(a)
        except Exception:
            continue
        diff = sim.player_score(me) - sim.player_score(other)
        scored.append((diff, a))

    best_diff = max(s[0] for s in scored)
    eps = 1e-9
    best = [a for (d, a) in scored if d >= best_diff - eps]
    if rng is None or len(best) == 1:
        return best[0]
    return int(rng.choice(best))


def run_one_game(seed: int) -> dict:
    g = PhaseGame(seed=seed)
    rng = np.random.default_rng(seed)
    camo_count = {1: 0, 2: 0}
    natural_count = {1: 0, 2: 0}
    while not g.done:
        a = greedy_action(g, rng=rng)
        player_before = g.current_player
        if a != PASS_ACTION:
            d = decode_action(a)
            phase = d["phase"]
            owner_target_phase = 1 if player_before == 1 else -1
            if phase == owner_target_phase:
                natural_count[player_before] += 1
            else:
                camo_count[player_before] += 1
        info = g.step(a)
    p1_pieces = int(np.sum((g.board == P1_POS) | (g.board == P1_NEG)))
    p2_pieces = int(np.sum((g.board == P2_POS) | (g.board == P2_NEG)))
    return {
        "seed": seed,
        "winner": g.winner,
        "steps": g.step_count,
        "score_p1": g.player_score(1),
        "score_p2": g.player_score(2),
        "end_reason": g.move_log[-1].get("end_reason") if g.move_log else None,
        "p1_natural": natural_count[1],
        "p1_camo": camo_count[1],
        "p2_natural": natural_count[2],
        "p2_camo": camo_count[2],
        "p1_pieces_final": p1_pieces,
        "p2_pieces_final": p2_pieces,
    }


def main():
    t0 = time.time()
    results = []
    for seed in range(50):
        r = run_one_game(seed)
        results.append(r)
        print(
            f"seed {seed:3d}: winner={r['winner']} steps={r['steps']:3d} "
            f"end={r['end_reason']:<22} "
            f"P1(nat={r['p1_natural']:2d},camo={r['p1_camo']:2d}) "
            f"P2(nat={r['p2_natural']:2d},camo={r['p2_camo']:2d}) "
            f"scores=({r['score_p1']:+.2f},{r['score_p2']:+.2f})"
        )
    elapsed = time.time() - t0

    n = len(results)
    p1_wins = sum(1 for r in results if r["winner"] == 1)
    p2_wins = sum(1 for r in results if r["winner"] == 2)
    draws = sum(1 for r in results if r["winner"] is None)
    total_camo = sum(r["p1_camo"] + r["p2_camo"] for r in results)
    total_nat = sum(r["p1_natural"] + r["p2_natural"] for r in results)
    total_placements = total_camo + total_nat
    camo_rate = total_camo / total_placements if total_placements else 0.0
    p1_camo_rate = sum(r["p1_camo"] for r in results) / max(1, sum(r["p1_camo"] + r["p1_natural"] for r in results))
    p2_camo_rate = sum(r["p2_camo"] for r in results) / max(1, sum(r["p2_camo"] + r["p2_natural"] for r in results))
    end_reasons = Counter(r["end_reason"] for r in results)
    mean_steps = sum(r["steps"] for r in results) / n
    decisive_rate = (p1_wins + p2_wins) / n

    print()
    print("=" * 72)
    print(f"50-game greedy-vs-greedy summary (elapsed {elapsed:.1f}s)")
    print(f"  P1 wins: {p1_wins}  P2 wins: {p2_wins}  Draws: {draws}")
    print(f"  Decisive rate: {decisive_rate:.2%}")
    print(f"  Mean game length: {mean_steps:.1f} steps")
    print(f"  Total placements: {total_placements}  natural: {total_nat}  camo: {total_camo}")
    print(f"  Overall camo rate: {camo_rate:.2%}")
    print(f"  P1 camo rate: {p1_camo_rate:.2%}   P2 camo rate: {p2_camo_rate:.2%}")
    print(f"  End reasons: {dict(end_reasons)}")


if __name__ == "__main__":
    main()
