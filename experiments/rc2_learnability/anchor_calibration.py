"""RC2 learnability — closeness-confound anchor calibration.

Registered obligation (rc2_descriptor_v2/RESULTS.md, "Registered next", binding
input (c)): any successor quality signal "must be demonstrated on a
closeness-confound pair (S4/S5 vs d4015) BEFORE any search spend — a 15-minute
calibration that this probe makes mechanical."

This script is that calibration for the LEARNABILITY candidate. Protocol
committed before the run; nothing below the bar definition is altered after
data.

Signal (pre-committed)
----------------------
  L(game, seed) = tvr_trained - tvr_untrained
  tvr           = seat-swapped trained-vs-random win share, n=100 games,
                  stochastic (deterministic=False), max_steps=400 — the
                  identical convention behind the FRONTLINE Stage-1 gate and
                  its S/A1 anchors (play_game methodology of record).
  trainer       = SelfPlayTrainer, TrainingConfig(training_budget=3000,
                  eval_episodes=100), MetricsConfig(learning_curve_checkpoints=4)
                  — the siege/frontline train_one shape, seeds 42 and 43.
  L(game)       = mean over the 2 seeds.

PASS bar (binding, the registered pair only)
--------------------------------------------
  L(d4015a646ae3) > L(S4)  AND  L(d4015a646ae3) > L(S5)

  d4015 (blind agent mean 3.83) is the control the blind teams preferred;
  S4/S5 (blind 3.00/3.07) are the maximally-close Goodharted elites (28-27
  parity races, TILT-flagged P1 share 0.80) that drama_v2 wrongly ranked
  above it (0.312/0.312 vs 0.108). A valid quality signal must not reproduce
  that inversion.

Diagnostics (non-binding, reported only)
----------------------------------------
  - e1453dac5445 (second control, blind 3.90) — run LAST (heavy board).
  - Per-seed L, raw trained/untrained tvr, learning curves, wall time.
  - Calibration context: FRONTLINE clean-kill datum — dead family L ~ +0.04,
    live families (S/A1) L >= +0.28 at this budget/convention.

Output: anchor_calibration.json + ANCHOR_CALIBRATION.md next to this file.
Run:    .venv/bin/python experiments/rc2_learnability/anchor_calibration.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import MetricsConfig, TrainingConfig  # noqa: E402
from game_engine.factory import create_engine  # noqa: E402
from training.trainer import SelfPlayTrainer  # noqa: E402
from training.utils import RandomAgent  # noqa: E402
from experiments.field_connect_probe.calibrate import play_game  # noqa: E402
# Drift-guarded loaders + blind means — the machinery the descriptor-v2
# probe registered as making this calibration mechanical.
from experiments.rc2_descriptor_v2.run_probe import (  # noqa: E402
    ROSTER,
    load_roster_game,
)

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "anchor_calibration.json"
OUT_MD = HERE / "ANCHOR_CALIBRATION.md"

BUDGET = 3000
SEEDS = (42, 43)
TVR_N = 100
MAX_STEPS = 400
BINDING = ("S4", "S5", "d4015a646ae3")   # registered pair + its control
DIAGNOSTIC = ("e1453dac5445",)           # non-binding, heavy board, run last


def tvr(trainer, n: int = TVR_N, deterministic: bool = False) -> float:
    """Seat-swapped trained-vs-random win share (frontline convention)."""
    wins = 0
    half = n // 2
    for i in range(n):
        engine = create_engine(trainer.game)
        if i < half:
            a0, a1, seat = trainer.agents[0], RandomAgent(seed=9000 + i), 0
        else:
            a0, a1, seat = RandomAgent(seed=9000 + i), trainer.agents[1], 1
        winner, _, _ = play_game(engine, a0, a1, deterministic=deterministic,
                                 max_steps=MAX_STEPS)
        wins += int(winner == seat)
    return wins / n


def measure(key: str) -> dict:
    game = load_roster_game(key)
    rows = []
    for seed in SEEDS:
        t0 = time.time()
        trainer = SelfPlayTrainer(
            game, TrainingConfig(training_budget=BUDGET, eval_episodes=100),
            MetricsConfig(learning_curve_checkpoints=4), seed=seed)
        untrained = tvr(trainer)
        curve = trainer.train()["learning_curve"]
        trained = tvr(trainer)
        rows.append(dict(seed=seed, untrained=untrained, trained=trained,
                         learnability=trained - untrained,
                         curve=[[ep, wo, wr] for ep, wo, wr in curve],
                         elapsed_s=round(time.time() - t0, 1)))
        print(f"  {key} seed {seed}: untrained {untrained:.3f} -> trained "
              f"{trained:.3f}  L {trained - untrained:+.3f} "
              f"({rows[-1]['elapsed_s']}s)", flush=True)
    return dict(
        key=key,
        family=ROSTER[key]["family"],
        blind_mean=ROSTER[key].get("blind_mean"),
        seeds=rows,
        learnability=float(np.mean([r["learnability"] for r in rows])),
        trained_mean=float(np.mean([r["trained"] for r in rows])),
        untrained_mean=float(np.mean([r["untrained"] for r in rows])),
    )


def main() -> None:
    t0 = time.time()
    results: dict[str, dict] = {}
    for key in (*BINDING, *DIAGNOSTIC):
        print(f"measuring {key} (blind {ROSTER[key].get('blind_mean')}, "
              f"{ROSTER[key]['family']})", flush=True)
        results[key] = measure(key)
        _write(results, t0, final=False)  # checkpoint (crash safety)

    _write(results, t0, final=True)


def _verdict(results: dict[str, dict]) -> tuple[str, str] | None:
    if not all(k in results for k in BINDING):
        return None
    ld = results["d4015a646ae3"]["learnability"]
    l4 = results["S4"]["learnability"]
    l5 = results["S5"]["learnability"]
    ok = ld > l4 and ld > l5
    detail = (f"L(d4015) {ld:+.3f} vs L(S4) {l4:+.3f}, L(S5) {l5:+.3f} — "
              f"bar: L(d4015) strictly above both")
    return ("PASS" if ok else "FAIL"), detail


def _write(results: dict, t0: float, final: bool) -> None:
    verdict = _verdict(results)
    state = dict(
        protocol=dict(budget=BUDGET, seeds=list(SEEDS), tvr_n=TVR_N,
                      max_steps=MAX_STEPS, signal="trained-untrained tvr",
                      bar="L(d4015) > L(S4) AND L(d4015) > L(S5)"),
        results=results,
        verdict=verdict[0] if verdict else "INCOMPLETE",
        verdict_detail=verdict[1] if verdict else None,
        elapsed_s=round(time.time() - t0, 1),
        complete=final,
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# RC2 learnability — closeness-confound anchor calibration", "",
        "Registered obligation: rc2_descriptor_v2/RESULTS.md binding input "
        "(c) — quality signal demonstrated on the S4/S5 vs d4015 pair "
        "BEFORE any search spend. Protocol pre-committed in "
        "`anchor_calibration.py`; bar applied verbatim.", "",
        f"Signal: L = tvr(trained) − tvr(untrained); PPO budget {BUDGET}, "
        f"seeds {list(SEEDS)}, tvr n={TVR_N} seat-swapped stochastic "
        "(frontline/siege convention).", "",
        "| game | blind mean | family | L (mean) | per-seed L | "
        "untrained → trained |",
        "|---|---:|---|---:|---|---|",
    ]
    for key, r in results.items():
        per_seed = ", ".join(f"{row['learnability']:+.3f}" for row in r["seeds"])
        lines.append(
            f"| {key}{'' if key in BINDING else ' (diagnostic)'} "
            f"| {r['blind_mean']} | {r['family']} "
            f"| **{r['learnability']:+.3f}** | {per_seed} "
            f"| {r['untrained_mean']:.3f} → {r['trained_mean']:.3f} |")
    if verdict:
        lines += ["", f"## Verdict: **{verdict[0]}**", "", verdict[1], ""]
    lines += [
        "Context (non-binding): FRONTLINE clean-kill datum at the same "
        "budget/convention — dead family L ≈ +0.04; live families S/A1 "
        "L ≥ +0.28.", "",
        f"Wall time: {state['elapsed_s']}s. "
        f"{'COMPLETE' if final else 'CHECKPOINT (run in progress)'}", "",
    ]
    OUT_MD.write_text("\n".join(lines))
    if final:
        print(f"\nVERDICT: {state['verdict']} — {state['verdict_detail']}")
        print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
              flush=True)


if __name__ == "__main__":
    main()
