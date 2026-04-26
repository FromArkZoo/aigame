#!/usr/bin/env python3
"""R17 balance preflight: seat-swap probe on frac_C_fractal.

Pair C teams flagged Δ Balance −0.20 across the 5-team eval — fractal-
connection slightly amplifies P1 first-mover advantage. This script runs
greedy and random agents on frac_C_fractal.json (and frac_C_control as a
baseline comparison) and reports P1 winrate.

Decision rule:
- P1 winrate <= 55%: balance is fine, ship as-is for R17.
- 55% < P1 winrate <= 65%: borderline; consider komi=1 or document.
- P1 winrate > 65%: add komi=2 (P2 starts with 2 pre-placed stones) or
  first-move restriction before R17 kickoff.

Usage:
    python experiments/r17_balance_preflight/probe.py
    python experiments/r17_balance_preflight/probe.py --episodes 200
"""

import argparse
import json
import math
import random
import sys
from pathlib import Path

# Make repo importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from training.utils import GreedyAgent, RandomAgent, play_game


CANDIDATES_DIR = Path(__file__).resolve().parents[1] / "fractal_spike" / "candidates"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--episodes", type=int, default=100,
                   help="Episodes per regime (random / greedy)")
    p.add_argument("--seed", type=int, default=20260426)
    p.add_argument("--game", type=str, nargs="+",
                   default=["frac_C_fractal", "frac_C_control"],
                   help="Game JSONs (without .json) to probe; default both Pair C")
    return p.parse_args()


def load_game(name: str) -> GameDefV2:
    path = CANDIDATES_DIR / f"{name}.json"
    with open(path) as f:
        return GameDefV2.from_dict(json.load(f))


def run_random_probe(game: GameDefV2, episodes: int, base_seed: int) -> dict:
    """Random-vs-random with seat-swap. Two distinct rng streams swap halves."""
    half = episodes // 2
    p1_wins = 0
    p2_wins = 0
    decisive = 0
    rand_a = RandomAgent(seed=base_seed * 7 + 11)
    rand_b = RandomAgent(seed=base_seed * 7 + 23)
    max_steps = game.win_condition.max_turns
    for i in range(episodes):
        engine = GameEngineV2(game)
        a0, a1 = (rand_a, rand_b) if i < half else (rand_b, rand_a)
        winner, _, _ = play_game(
            engine, a0, a1, deterministic=False, max_steps=max_steps,
        )
        if winner is not None:
            decisive += 1
            if winner == 0:
                p1_wins += 1
            else:
                p2_wins += 1
    return {
        "regime": "random",
        "episodes": episodes,
        "decisive": decisive,
        "p1_wins": p1_wins,
        "p2_wins": p2_wins,
        "p1_winrate": p1_wins / decisive if decisive else 0.5,
        "decisive_rate": decisive / episodes,
    }


def run_greedy_probe(game: GameDefV2, episodes: int, base_seed: int) -> dict:
    """Greedy-vs-greedy with seat-swap; new engine each game."""
    p1_wins = 0
    p2_wins = 0
    decisive = 0
    max_steps = game.win_condition.max_turns
    for i in range(episodes):
        engine = GameEngineV2(game)
        seed_offset = base_seed * 29 + 31 * i
        a0 = GreedyAgent(engine, player_num=1, seed=seed_offset)
        a1 = GreedyAgent(engine, player_num=2, seed=seed_offset + 7)
        winner, _, _ = play_game(
            engine, a0, a1, deterministic=False, max_steps=max_steps,
        )
        if winner is not None:
            decisive += 1
            if winner == 0:
                p1_wins += 1
            else:
                p2_wins += 1
    return {
        "regime": "greedy",
        "episodes": episodes,
        "decisive": decisive,
        "p1_wins": p1_wins,
        "p2_wins": p2_wins,
        "p1_winrate": p1_wins / decisive if decisive else 0.5,
        "decisive_rate": decisive / episodes,
    }


def wilson_ci(wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95% CI for a binomial proportion. Tighter than normal at small n."""
    if n == 0:
        return (0.0, 1.0)
    p = wins / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def verdict(p1_winrate: float) -> str:
    if p1_winrate <= 0.55:
        return "BALANCED — ship as-is"
    if p1_winrate <= 0.65:
        return "BORDERLINE — consider komi=1"
    return "UNBALANCED — add komi=2 or first-move restriction"


def main() -> None:
    args = parse_args()

    print(f"\n=== R17 balance preflight ===")
    print(f"Games: {', '.join(args.game)}")
    print(f"Episodes per regime: {args.episodes}\n")

    all_results: dict[str, dict] = {}

    for name in args.game:
        game = load_game(name)
        print(f"--- {name} ({game.topology_type}, {game.capture_rule.capture_type}, "
              f"{game.win_condition.condition_type}) ---")

        results = {}
        for runner in (run_random_probe, run_greedy_probe):
            r = runner(game, args.episodes, args.seed)
            ci_lo, ci_hi = wilson_ci(r["p1_wins"], r["decisive"]) if r["decisive"] else (0, 1)
            print(
                f"  {r['regime']:>7}: P1 {r['p1_wins']}/{r['decisive']} "
                f"({r['p1_winrate']:.1%}, 95% CI [{ci_lo:.1%}, {ci_hi:.1%}]) "
                f"decisive {r['decisive_rate']:.0%} "
                f"-> {verdict(r['p1_winrate'])}"
            )
            results[r["regime"]] = r

        all_results[name] = results
        print()

    # Comparison: fractal vs control
    if "frac_C_fractal" in all_results and "frac_C_control" in all_results:
        print("--- Fractal vs Control delta (P1 winrate) ---")
        for regime in ("random", "greedy"):
            f = all_results["frac_C_fractal"][regime]["p1_winrate"]
            c = all_results["frac_C_control"][regime]["p1_winrate"]
            delta = f - c
            print(f"  {regime:>7}: fractal {f:.1%} − control {c:.1%} = "
                  f"{delta:+.1%} {'(fractal more biased)' if delta > 0.05 else ''}")

    # Persist for the writeup
    out_path = Path(__file__).parent / "probe_results.json"
    with open(out_path, "w") as f:
        json.dump(
            {"args": vars(args), "results": all_results},
            f, indent=2,
        )
    print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()
