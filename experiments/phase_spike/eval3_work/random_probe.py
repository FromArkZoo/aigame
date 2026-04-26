"""50-game random-vs-random probe for phase-extended c6bb58075520."""
from __future__ import annotations

import sys
import os
# go up 3 levels from eval3_work/ to project root
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))

import numpy as np
from collections import Counter

from experiments.phase_spike.phase_game import (
    PhaseGame, PASS_ACTION, decode_action,
    P1_POS, P1_NEG, P2_POS, P2_NEG,
)


def run_one(seed: int) -> dict:
    g = PhaseGame(seed=seed)
    rng = np.random.default_rng(seed)
    p1_camo_placed = 0
    p2_camo_placed = 0
    p1_natural_placed = 0
    p2_natural_placed = 0
    while not g.done:
        actions = g.get_legal_actions()
        a = int(rng.choice(actions))
        d = decode_action(a)
        player = g.current_player
        if d["type"] == "place":
            phase = d["phase"]
            if player == 1 and phase == 1:
                p1_natural_placed += 1
            elif player == 1 and phase == -1:
                p1_camo_placed += 1
            elif player == 2 and phase == -1:
                p2_natural_placed += 1
            elif player == 2 and phase == 1:
                p2_camo_placed += 1
        g.step(a)
    # count remaining stones on board
    p1_natural_alive = int(np.sum(g.board == P1_POS))
    p1_camo_alive = int(np.sum(g.board == P1_NEG))
    p2_natural_alive = int(np.sum(g.board == P2_NEG))
    p2_camo_alive = int(np.sum(g.board == P2_POS))
    return {
        "winner": g.winner,
        "steps": g.step_count,
        "score_p1": g.player_score(1),
        "score_p2": g.player_score(2),
        "p1_natural_placed": p1_natural_placed,
        "p1_camo_placed": p1_camo_placed,
        "p2_natural_placed": p2_natural_placed,
        "p2_camo_placed": p2_camo_placed,
        "p1_natural_alive": p1_natural_alive,
        "p1_camo_alive": p1_camo_alive,
        "p2_natural_alive": p2_natural_alive,
        "p2_camo_alive": p2_camo_alive,
        "end_reason": "threshold" if g.winner is not None and g.step_count < 100 else (
            "max_turns" if g.step_count >= 100 else "draw"),
    }


def main():
    n = 50
    results = [run_one(seed) for seed in range(n)]
    win_counts = Counter(r["winner"] for r in results)
    avg_steps = np.mean([r["steps"] for r in results])
    avg_p1_camo_placed = np.mean([r["p1_camo_placed"] for r in results])
    avg_p2_camo_placed = np.mean([r["p2_camo_placed"] for r in results])
    avg_p1_natural_placed = np.mean([r["p1_natural_placed"] for r in results])
    avg_p2_natural_placed = np.mean([r["p2_natural_placed"] for r in results])
    avg_p1_camo_alive = np.mean([r["p1_camo_alive"] for r in results])
    avg_p2_camo_alive = np.mean([r["p2_camo_alive"] for r in results])
    avg_p1_natural_alive = np.mean([r["p1_natural_alive"] for r in results])
    avg_p2_natural_alive = np.mean([r["p2_natural_alive"] for r in results])
    avg_score_p1 = np.mean([r["score_p1"] for r in results])
    avg_score_p2 = np.mean([r["score_p2"] for r in results])
    threshold_wins = sum(1 for r in results if r["steps"] < 100 and r["winner"] is not None)
    max_turn_games = sum(1 for r in results if r["steps"] >= 100)

    print(f"=== 50-Game Random-vs-Random Probe ===")
    print(f"Wins: P1={win_counts[1]}, P2={win_counts[2]}, Draws={win_counts[None]}")
    print(f"Avg game length: {avg_steps:.1f} steps")
    print(f"Threshold wins: {threshold_wins}/{n}")
    print(f"Reached max turns (100): {max_turn_games}/{n}")
    print()
    print(f"Avg score P1: {avg_score_p1:.3f}, P2: {avg_score_p2:.3f}  (threshold = 22.65)")
    print()
    print(f"Stone PLACEMENT counts (mean per game):")
    print(f"  P1 natural (+1):    {avg_p1_natural_placed:.2f}")
    print(f"  P1 camouflage (-1): {avg_p1_camo_placed:.2f}")
    print(f"  P2 natural (-1):    {avg_p2_natural_placed:.2f}")
    print(f"  P2 camouflage (+1): {avg_p2_camo_placed:.2f}")
    print()
    print(f"Stone ALIVE counts at game end (mean):")
    print(f"  P1 natural (+1):    {avg_p1_natural_alive:.2f}")
    print(f"  P1 camouflage (-1): {avg_p1_camo_alive:.2f}")
    print(f"  P2 natural (-1):    {avg_p2_natural_alive:.2f}")
    print(f"  P2 camouflage (+1): {avg_p2_camo_alive:.2f}")
    print()
    print(f"Camouflage usage rate (placements per game):")
    print(f"  P1 camo / P1 total = {avg_p1_camo_placed/(avg_p1_camo_placed+avg_p1_natural_placed):.1%}")
    print(f"  P2 camo / P2 total = {avg_p2_camo_placed/(avg_p2_camo_placed+avg_p2_natural_placed):.1%}")
    print()
    print(f"Camouflage SURVIVAL rate (alive / placed):")
    if avg_p1_camo_placed > 0:
        print(f"  P1 camo: {avg_p1_camo_alive/avg_p1_camo_placed:.1%}")
    if avg_p2_camo_placed > 0:
        print(f"  P2 camo: {avg_p2_camo_alive/avg_p2_camo_placed:.1%}")
    print(f"Natural SURVIVAL rate:")
    if avg_p1_natural_placed > 0:
        print(f"  P1 natural: {avg_p1_natural_alive/avg_p1_natural_placed:.1%}")
    if avg_p2_natural_placed > 0:
        print(f"  P2 natural: {avg_p2_natural_alive/avg_p2_natural_placed:.1%}")


if __name__ == "__main__":
    main()
