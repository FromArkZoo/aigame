"""RC2 planning-gap — closeness-confound anchor calibration.

Registered obligation (rc2_descriptor_v2/RESULTS.md, "Registered next", binding
input (c)): any successor quality signal "must be demonstrated on a
closeness-confound pair (S4/S5 vs d4015) BEFORE any search spend — a 15-minute
calibration that this probe makes mechanical."

This script is that calibration for the PLANNING-GAP candidate — the lead
candidate registered by rc2_learnability/ANCHOR_CALIBRATION.md after naive
self-play learnability failed (pass-collapse attractor). Protocol committed
before the run; nothing below the bar definition is altered after data.

Signal (pre-committed)
----------------------
  PG(game)  = mean over n=48 seat-balanced games of
              score(UCT@256 vs UCT@16) − 0.5
  score     = 1 win / 0.5 draw / 0 loss, from the deep (256-sim) side's
              perspective; play_game convention (training/utils.py),
              max_steps=400 (frontline/siege convention; these engines
              self-terminate at max_game_steps=100).
  UCT       = net-FREE vanilla PUCT: uniform prior, random-rollout leaf
              eval, c_puct 1.5, no Dirichlet noise — the mcts_phase1
              search machinery (experiments/mcts_phase1/mcts.py) with the
              PPO nets replaced by a uniform evaluator. Net-free is
              REQUIRED, not optional: rc2_learnability recorded that PPO
              at this scale collapses to the pass attractor on 3 of 4
              anchor games, so net-guided search would inherit poisoned
              priors. Per-game rollout randomness (independent rng seed
              per game, mcts_phase1 seed-derivation style) is the
              variance source; root selection is argmax visits.
  sims      = 16 (shallow) vs 256 (deep) — the registered endpoints of
              the mcts_phase1 scaling-slope metric (summary.md).
  n         = 48 games per anchor: 2 independent seed streams (42, 43),
              24 games each, seat-balanced within each stream (deep side
              plays P1 in half, P2 in half).

Reading: PG ≈ 0 — deep search buys nothing (greedy/parity race; planning
is irrelevant to the outcome). PG >> 0 — lookahead wins (live tactics).
The closeness confound predicts S4/S5 (28-27 parity races) sit near 0
while d4015 (the blind-preferred connection game) rewards planning.

PASS bar (binding, the registered pair only)
--------------------------------------------
  PG(d4015a646ae3) > PG(S4)  AND  PG(d4015a646ae3) > PG(S5)

  d4015 (blind agent mean 3.83) is the control the blind teams preferred;
  S4/S5 (blind 3.00/3.07) are the maximally-close Goodharted elites (28-27
  parity races, TILT-flagged P1 share 0.80) that drama_v2 wrongly ranked
  above it (0.312/0.312 vs 0.108). A valid quality signal must not
  reproduce that inversion.

Diagnostics (non-binding, reported only)
----------------------------------------
  - e1453dac5445 (second control, blind 3.90, known-shallow per R21 agent
    rank 6/7) — a healthy depth signal should NOT crown it (naive
    learnability did; that was its second strike).
  - Per-stream PG, win/draw/loss counts, mean game length, wall time.

Output: anchor_calibration.json + ANCHOR_CALIBRATION.md next to this file.
Run:    .venv/bin/python experiments/rc2_planning_gap/anchor_calibration.py
        [--smoke]  (plumbing check on a NON-binding roster game, n=4,
                    sims 8/32 — produces no anchor data)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from training.utils import play_game  # noqa: E402
from experiments.mcts_phase1.mcts import MCTSEvaluator  # noqa: E402
# Drift-guarded loaders + blind means — the machinery the descriptor-v2
# probe registered as making this calibration mechanical.
from experiments.rc2_descriptor_v2.run_probe import (  # noqa: E402
    ROSTER,
    load_roster_game,
)

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "anchor_calibration.json"
OUT_MD = HERE / "ANCHOR_CALIBRATION.md"

DEEP_SIMS = 256
SHALLOW_SIMS = 16
STREAMS = (42, 43)
GAMES_PER_STREAM = 24
MAX_STEPS = 400
WORKERS = 7
BINDING = ("S4", "S5", "d4015a646ae3")   # registered pair + its control
DIAGNOSTIC = ("e1453dac5445",)           # non-binding, heavy board
SMOKE_KEY = "573562833174"               # non-binding plumbing check only


class UniformEvaluator:
    """Net replacement: uniform prior over legal actions, neutral value.

    With leaf_eval='rollout' the value half is never consulted; returning
    0.0 keeps the (prior, value) contract of mcts._NetEvaluator.
    """

    def __call__(self, obs, legal_actions, to_move):
        n = len(legal_actions)
        return np.full(n, 1.0 / n, dtype=np.float32), 0.0


class UCTEvaluator(MCTSEvaluator):
    """mcts_phase1 PUCT search with the net swapped for UniformEvaluator."""

    def __init__(self, rng: np.random.Generator):
        self.evaluator = UniformEvaluator()
        self.c_puct = 1.5
        self.virtual_loss = 1
        self.dirichlet_eps = 0.0
        self.dirichlet_alpha = 0.3
        self.leaf_eval = "rollout"
        self.rng = rng


class UCTAgent:
    """play_game adapter (mirrors mcts_phase1.MCTSAgent, net-free)."""

    def __init__(self, engine, num_sims: int, rng_seed: int):
        self.engine = engine
        self.evaluator = UCTEvaluator(np.random.default_rng(rng_seed))
        self.num_sims = num_sims

    def select_action(self, obs, legal_actions=None, deterministic=True):
        action = self.evaluator.search(self.engine, self.num_sims)
        return action, 0.0, 0.0


def play_cell(key: str, stream: int, idx: int,
              deep_sims: int = DEEP_SIMS, shallow_sims: int = SHALLOW_SIMS,
              games_per_stream: int = GAMES_PER_STREAM) -> dict:
    """One deep-vs-shallow game. Top-level so ProcessPoolExecutor can spawn it."""
    game = load_roster_game(key)
    engine = create_engine(game)
    deep_seed = (stream * 1000033 + idx * 7 + 1) & 0x7FFFFFFF
    shallow_seed = (stream * 1000003 + idx) & 0x7FFFFFFF
    deep = UCTAgent(engine, deep_sims, deep_seed)
    shallow = UCTAgent(engine, shallow_sims, shallow_seed)
    deep_seat = 0 if idx < games_per_stream // 2 else 1
    agents = (deep, shallow) if deep_seat == 0 else (shallow, deep)
    t0 = time.time()
    winner, length, _ = play_game(engine, agents[0], agents[1],
                                  deterministic=True, max_steps=MAX_STEPS)
    score = 0.5 if winner is None else float(winner == deep_seat)
    return dict(key=key, stream=stream, idx=idx, deep_seat=deep_seat,
                score=score, winner=winner, length=length,
                elapsed_s=round(time.time() - t0, 1))


def summarise(key: str, cells: list[dict]) -> dict:
    scores = [c["score"] for c in cells]
    by_stream = {}
    for s in STREAMS:
        ss = [c["score"] for c in cells if c["stream"] == s]
        if ss:
            by_stream[str(s)] = round(float(np.mean(ss)) - 0.5, 4)
    return dict(
        key=key,
        family=ROSTER[key]["family"],
        blind_mean=ROSTER[key].get("blind_mean"),
        n=len(cells),
        planning_gap=float(np.mean(scores)) - 0.5,
        per_stream=by_stream,
        wins=sum(1 for c in cells if c["score"] == 1.0),
        draws=sum(1 for c in cells if c["score"] == 0.5),
        losses=sum(1 for c in cells if c["score"] == 0.0),
        mean_length=float(np.mean([c["length"] for c in cells])),
    )


def _verdict(results: dict[str, dict]) -> tuple[str, str] | None:
    if not all(k in results and results[k]["n"] == 2 * GAMES_PER_STREAM
               for k in BINDING):
        return None
    pd = results["d4015a646ae3"]["planning_gap"]
    p4 = results["S4"]["planning_gap"]
    p5 = results["S5"]["planning_gap"]
    ok = pd > p4 and pd > p5
    detail = (f"PG(d4015) {pd:+.3f} vs PG(S4) {p4:+.3f}, PG(S5) {p5:+.3f} — "
              f"bar: PG(d4015) strictly above both")
    return ("PASS" if ok else "FAIL"), detail


def _write(results: dict[str, dict], t0: float, final: bool) -> None:
    verdict = _verdict(results)
    state = dict(
        protocol=dict(deep_sims=DEEP_SIMS, shallow_sims=SHALLOW_SIMS,
                      streams=list(STREAMS),
                      games_per_stream=GAMES_PER_STREAM,
                      max_steps=MAX_STEPS,
                      signal="seat-balanced UCT@deep vs UCT@shallow score - 0.5"
                             " (net-free, uniform prior, rollout leaf)",
                      bar="PG(d4015) > PG(S4) AND PG(d4015) > PG(S5)"),
        results=results,
        verdict=verdict[0] if verdict else "INCOMPLETE",
        verdict_detail=verdict[1] if verdict else None,
        elapsed_s=round(time.time() - t0, 1),
        complete=final,
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# RC2 planning-gap — closeness-confound anchor calibration", "",
        "Registered obligation: rc2_descriptor_v2/RESULTS.md binding input "
        "(c) — quality signal demonstrated on the S4/S5 vs d4015 pair "
        "BEFORE any search spend. Protocol pre-committed in "
        "`anchor_calibration.py`; bar applied verbatim.", "",
        f"Signal: PG = seat-balanced score of net-free UCT@{DEEP_SIMS} vs "
        f"UCT@{SHALLOW_SIMS} − 0.5 (uniform prior, random-rollout leaf, "
        f"c_puct 1.5); n={2 * GAMES_PER_STREAM} per game "
        f"(streams {list(STREAMS)}, draws = 0.5). Net-free is required: "
        "rc2_learnability recorded PPO pass-collapse on 3/4 anchors, so "
        "net-guided search would inherit poisoned priors.", "",
        "| game | blind mean | family | PG (mean) | per-stream PG | "
        "W/D/L (deep) | mean plies |",
        "|---|---:|---|---:|---|---|---:|",
    ]
    for key in (*BINDING, *DIAGNOSTIC):
        if key not in results:
            continue
        r = results[key]
        per_stream = ", ".join(f"{v:+.3f}" for v in r["per_stream"].values())
        lines.append(
            f"| {key}{'' if key in BINDING else ' (diagnostic)'} "
            f"| {r['blind_mean']} | {r['family']} "
            f"| **{r['planning_gap']:+.3f}** | {per_stream} "
            f"| {r['wins']}/{r['draws']}/{r['losses']} "
            f"| {r['mean_length']:.1f} |")
    if verdict:
        lines += ["", f"## Verdict: **{verdict[0]}**", "", verdict[1], ""]
    lines += [
        "Reading: PG ≈ 0 — deep search buys nothing (parity race / greedy-"
        "sufficient play); PG >> 0 — lookahead wins (live tactics). The "
        "closeness confound predicts S4/S5 near 0, d4015 above.", "",
        f"Wall time: {state['elapsed_s']}s. "
        f"{'COMPLETE' if final else 'CHECKPOINT (run in progress)'}", "",
    ]
    OUT_MD.write_text("\n".join(lines))
    if final:
        print(f"\nVERDICT: {state['verdict']} — {state['verdict_detail']}")
        print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
              flush=True)


def smoke() -> None:
    """Plumbing check on a NON-binding roster game. No anchor data."""
    print(f"smoke: {SMOKE_KEY}, n=4, sims 8/32", flush=True)
    for idx in range(4):
        cell = play_cell(SMOKE_KEY, stream=7, idx=idx,
                         deep_sims=32, shallow_sims=8, games_per_stream=4)
        print(f"  game {idx}: deep_seat={cell['deep_seat']} "
              f"winner={cell['winner']} score={cell['score']} "
              f"len={cell['length']} ({cell['elapsed_s']}s)", flush=True)
    print("smoke OK", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        smoke()
        return

    t0 = time.time()
    tasks = [(key, stream, idx)
             for key in (*BINDING, *DIAGNOSTIC)
             for stream in STREAMS
             for idx in range(GAMES_PER_STREAM)]
    cells: dict[str, list[dict]] = {key: [] for key, _, _ in tasks}
    done = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(play_cell, *t): t for t in tasks}
        for fut in as_completed(futures):
            cell = fut.result()
            cells[cell["key"]].append(cell)
            done += 1
            if done % 16 == 0 or done == len(tasks):
                results = {k: summarise(k, v) for k, v in cells.items() if v}
                _write(results, t0, final=False)  # checkpoint (crash safety)
                print(f"  {done}/{len(tasks)} games "
                      f"({time.time() - t0:.0f}s)", flush=True)

    results = {k: summarise(k, v) for k, v in cells.items()}
    _write(results, t0, final=True)


if __name__ == "__main__":
    main()
