"""Greedy self-play probe for fractal-topology spike candidates.

For each of the six candidate games, run N greedy-vs-greedy games and
report seat balance, mean game length, decisive-end rate, and (where
applicable) capture frequency. Emit JSON + markdown summary.

Run as: .venv/bin/python experiments/fractal_spike/probe.py [--games N]
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from game_engine.engine_v2 import GameEngineV2
from game_engine.game_def_v2 import GameDefV2
from training.utils import GreedyAgent, play_game


CANDIDATES_DIR = os.path.join(_HERE, "candidates")


def _load_candidate(name: str) -> GameDefV2:
    with open(os.path.join(CANDIDATES_DIR, f"{name}.json")) as fp:
        return GameDefV2.from_dict(json.load(fp))


def _probe_game(game: GameDefV2, num_games: int, base_seed: int = 0) -> dict:
    """Run num_games greedy-vs-greedy games. Tracks per-game outcomes."""
    p0_wins = 0
    p1_wins = 0
    draws = 0
    lengths: list[int] = []
    pieces_at_end_p0: list[int] = []
    pieces_at_end_p1: list[int] = []

    t_start = time.time()
    for i in range(num_games):
        eng = GameEngineV2(game)
        a0 = GreedyAgent(eng, player_num=1, seed=base_seed + 2 * i)
        a1 = GreedyAgent(eng, player_num=2, seed=base_seed + 2 * i + 1)
        winner, length, _ = play_game(eng, a0, a1, deterministic=True)
        lengths.append(length)
        pieces_at_end_p0.append(int(eng.piece_counts[0]))
        pieces_at_end_p1.append(int(eng.piece_counts[1]))
        if winner is None:
            draws += 1
        elif winner == 0:
            p0_wins += 1
        else:
            p1_wins += 1
    elapsed = time.time() - t_start

    n = max(num_games, 1)
    return {
        "num_games": num_games,
        "p0_winrate": p0_wins / n,
        "p1_winrate": p1_wins / n,
        "draw_rate": draws / n,
        "decisive_rate": (p0_wins + p1_wins) / n,
        "mean_length": statistics.mean(lengths),
        "median_length": statistics.median(lengths),
        "stdev_length": statistics.stdev(lengths) if len(lengths) > 1 else 0.0,
        "mean_pieces_end_p0": statistics.mean(pieces_at_end_p0),
        "mean_pieces_end_p1": statistics.mean(pieces_at_end_p1),
        "elapsed_sec": elapsed,
    }


def _format_md(results: dict) -> str:
    lines = []
    lines.append("# Fractal-spike probe results\n")
    lines.append(
        "Greedy-vs-greedy probe for each candidate. Greedy picks the "
        "placement with highest (friendly_neighbors − enemy_neighbors); "
        "ties broken randomly. Lopsided P0 winrate indicates seat bias "
        "in the rules+topology combination.\n"
    )
    lines.append(
        "| Candidate | Topology | P0 win | P1 win | Draw | Mean len | "
        "Decisive | P0 pieces | P1 pieces |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for name, r in sorted(results.items()):
        topo = r["meta"]["topology_type"]
        lines.append(
            f"| {name} | {topo} "
            f"| {r['p0_winrate']:.2f} | {r['p1_winrate']:.2f} | {r['draw_rate']:.2f} "
            f"| {r['mean_length']:.1f} | {r['decisive_rate']:.2f} "
            f"| {r['mean_pieces_end_p0']:.1f} | {r['mean_pieces_end_p1']:.1f} |"
        )

    lines.append("\n## Per-pair delta (fractal − control)\n")
    for pair in ("A", "B", "C"):
        ctrl = results.get(f"frac_{pair}_control")
        frac = results.get(f"frac_{pair}_fractal")
        if not ctrl or not frac:
            continue
        lines.append(f"### Pair {pair}")
        lines.append(
            f"- P0 winrate: control {ctrl['p0_winrate']:.2f} / "
            f"fractal {frac['p0_winrate']:.2f} "
            f"(Δ {frac['p0_winrate'] - ctrl['p0_winrate']:+.2f})"
        )
        lines.append(
            f"- Decisive rate: control {ctrl['decisive_rate']:.2f} / "
            f"fractal {frac['decisive_rate']:.2f} "
            f"(Δ {frac['decisive_rate'] - ctrl['decisive_rate']:+.2f})"
        )
        lines.append(
            f"- Mean length: control {ctrl['mean_length']:.1f} / "
            f"fractal {frac['mean_length']:.1f}"
        )
        lines.append("")
    return "\n".join(lines)


def _seat_balance_check(results: dict) -> list[str]:
    """Flag any candidate where P0 winrate deviates from 50% by > 15pp."""
    flags = []
    for name, r in results.items():
        bias = abs(r["p0_winrate"] - 0.5)
        if bias > 0.15:
            flags.append(
                f"  {name}: p0_winrate={r['p0_winrate']:.2f} "
                f"(|bias|={bias:.2f} > 0.15)"
            )
    return flags


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=200)
    args = parser.parse_args()

    candidate_names = [
        "frac_A_control", "frac_A_fractal",
        "frac_B_control", "frac_B_fractal",
        "frac_C_control", "frac_C_fractal",
    ]

    results: dict = {}
    for name in candidate_names:
        print(f"  probing {name}...", flush=True)
        game = _load_candidate(name)
        stats = _probe_game(game, args.games, base_seed=hash(name) & 0x7FFFFFFF)
        stats["meta"] = {
            "game_id": game.game_id,
            "topology_type": game.topology_type,
            "axis_size": game.axis_size,
            "capture_type": game.capture_rule.capture_type,
            "win_condition": game.win_condition.condition_type,
        }
        results[name] = stats
        print(
            f"    p0={stats['p0_winrate']:.2f} p1={stats['p1_winrate']:.2f} "
            f"draw={stats['draw_rate']:.2f} mean_len={stats['mean_length']:.1f} "
            f"({stats['elapsed_sec']:.1f}s)"
        )

    json_path = os.path.join(_HERE, "probe_results.json")
    with open(json_path, "w") as fp:
        json.dump(results, fp, indent=2)
    print(f"\n  wrote {os.path.relpath(json_path, _REPO)}")

    md_path = os.path.join(_HERE, "probe_results.md")
    with open(md_path, "w") as fp:
        fp.write(_format_md(results))
    print(f"  wrote {os.path.relpath(md_path, _REPO)}")

    flags = _seat_balance_check(results)
    if flags:
        print("\n  SEAT BALANCE FLAGS (|p0 - 0.5| > 0.15):")
        for f in flags:
            print(f)
    else:
        print("\n  All candidates within seat-balance tolerance (|p0 - 0.5| <= 0.15).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
