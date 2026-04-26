"""Greedy-vs-Greedy 50-game probe for phase_game_v2.

Greedy heuristic: 1-ply lookahead.
For each legal action, simulate the move (full capture+propagation), compute
(own_score - other_score) AFTER capture, and pick the action that maximizes this.

Two probes:
  1) DETERMINISTIC tie-breaks (lowest action index): 50 games purely for confirming
     greedy converges to one canonical line. (All 50 games identical.)
  2) RANDOMIZED tie-breaks (within epsilon=1e-9 of best): seed varies the
     tie-break so we get diverse trajectories and still see whether decision
     surface yields multiple distinct games.
"""

from __future__ import annotations

import copy
import os
import sys
import time
import random
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))

from experiments.phase_spike.phase_game_v2 import (
    PhaseGameV2, encode_action, decode_action, PASS_ACTION, PHASE_NAMES,
)


def greedy_action(game: PhaseGameV2, rng: random.Random | None = None,
                  eps: float = 1e-9) -> int:
    """1-ply lookahead. With rng provided, breaks ties (within eps) randomly."""
    actions = game.get_legal_actions()
    me = game.current_player
    other = 3 - me
    scored = []
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
        scored.append((diff, a))

    best = max(s[0] for s in scored)
    top = [a for d, a in scored if d >= best - eps]
    if rng is not None and len(top) > 1:
        return rng.choice(top)
    return min(top)  # deterministic: lowest action index


def run_one_game(seed: int = 0, randomize: bool = True) -> dict:
    g = PhaseGameV2(seed=seed)
    rng = random.Random(seed) if randomize else None
    phase_counts = {1: Counter(), 2: Counter()}
    while not g.done:
        player = g.current_player
        a = greedy_action(g, rng=rng)
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
        "moves": [m for m in g.move_log],
    }


def summarize(label: str, results: list[dict]) -> str:
    n_games = len(results)
    p1_wins = sum(1 for r in results if r["winner"] == 1)
    p2_wins = sum(1 for r in results if r["winner"] == 2)
    draws = sum(1 for r in results if r["winner"] is None)
    decisive = p1_wins + p2_wins
    mean_steps = sum(r["steps"] for r in results) / n_games

    total_phase = {1: Counter(), 2: Counter()}
    for r in results:
        for p in (1, 2):
            total_phase[p].update(r["phase_counts"][p])

    lines = [
        "=" * 60,
        f"{label}",
        "=" * 60,
        f"Games:       {n_games}",
        f"P1 wins:     {p1_wins} ({100*p1_wins/n_games:.0f}%)",
        f"P2 wins:     {p2_wins} ({100*p2_wins/n_games:.0f}%)",
        f"Draws:       {draws} ({100*draws/n_games:.0f}%)",
        f"Decisive:    {100*decisive/n_games:.0f}%",
        f"Mean steps:  {mean_steps:.1f}",
        f"Min/max:     {min(r['steps'] for r in results)} / {max(r['steps'] for r in results)}",
        "",
        "Phase usage by player (placements only):",
    ]
    for p in (1, 2):
        total = sum(total_phase[p].values())
        if total == 0:
            lines.append(f"  P{p}: no placements")
            continue
        bits = []
        for phase in PHASE_NAMES:
            cnt = total_phase[p][phase]
            pct = 100 * cnt / total
            bits.append(f"{phase}={cnt}({pct:.0f}%)")
        lines.append(f"  P{p} (total={total}): {' '.join(bits)}")
    end_reasons = Counter(r["end_reason"] for r in results)
    lines.append("End reasons:")
    for er, c in end_reasons.most_common():
        lines.append(f"  {er}: {c}")
    # Distinct game count
    sigs = set((r["winner"], r["steps"], round(r["p1_score"], 3), round(r["p2_score"], 3))
               for r in results)
    lines.append(f"Distinct (winner,steps,p1,p2) signatures: {len(sigs)}")
    return "\n".join(lines)


def main():
    n_games = 50

    # Probe 1: deterministic
    t0 = time.time()
    print("=== Probe 1: DETERMINISTIC tie-breaks (lowest action index) ===")
    det_results = []
    for seed in range(n_games):
        r = run_one_game(seed=seed, randomize=False)
        det_results.append(r)
        if seed in (0, 1, 5, 10, 25, 49):
            print(f"  seed={seed:2d}  winner={r['winner']}  steps={r['steps']:3d}  "
                  f"p1={r['p1_score']:+.2f}  p2={r['p2_score']:+.2f}  end={r['end_reason']}")
    print(f"  ... (50 games in {time.time()-t0:.1f}s)")
    print()
    print(summarize("DETERMINISTIC GREEDY 50-GAME PROBE", det_results))

    # Probe 2: randomized
    t1 = time.time()
    print()
    print("=== Probe 2: RANDOMIZED tie-breaks (eps=1e-9) ===")
    rand_results = []
    for seed in range(n_games):
        r = run_one_game(seed=seed, randomize=True)
        rand_results.append(r)
        if seed in (0, 1, 5, 10, 25, 49) or r["winner"] != 1:
            print(f"  seed={seed:2d}  winner={r['winner']}  steps={r['steps']:3d}  "
                  f"p1={r['p1_score']:+.2f}  p2={r['p2_score']:+.2f}  end={r['end_reason']}")
    print(f"  ... (50 games in {time.time()-t1:.1f}s)")
    print()
    print(summarize("RANDOMIZED GREEDY 50-GAME PROBE", rand_results))
    print()
    print(f"Total time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
