"""RC2 planning-gap — cost/noise tiering for in-loop use (r18_noise_floor precedent).

Full-convention PG (UCT@256 vs UCT@16, n=48) costs ~10-45 CPU-min per game —
fine for calibration, unusable as a per-candidate fitness call. This probe
asks which cheaper tier preserves what a SCREENING signal must preserve,
with full-convention PG reserved for survivors.

Tiers (pre-committed; cheapest passing tier is adopted as the screening tier)
------------------------------------------------------------------------------
  T1: deep 128 vs shallow 16, n=24  (~4x cheaper than full convention)
  T2: deep  64 vs shallow  8, n=24  (~8x)
  T3: deep  64 vs shallow  8, n=12  (~16x)
All other protocol elements identical to anchor_calibration.py (same
play_cell, seed derivation, seat balance, streams 42/43, draws 0.5).
Reference values: the full-convention blind seven (anchor_calibration.json
+ blind_seven_validation.json), measured under the frozen protocol.

Acceptance bars (binding, per tier)
-----------------------------------
  A1 (sign separation): min tier-PG over P = {S2, S3, d4015a646ae3}
      (full-convention PG >= +0.198) strictly exceeds max tier-PG over
      N = {S1, S4, e1453dac5445} (full-convention PG <= 0.000).
      S5 (+0.052, borderline at full convention) is unconstrained.
  A2 (band-pass utility): the tier's argmax-PG game is in {S3, d4015a646ae3}
      (the full-convention co-leaders).

Registration honesty: the full-convention values are known; the bars test
whether a cheap tier REPRODUCES them, which is the probe's entire question —
there is nothing to blind.

Diagnostics (non-binding): Spearman(tier PG, full PG) over the seven,
per-stream spread, measured CPU cost per game, projected per-candidate cost.

Output: cost_tiering.json + COST_TIERING.md next to this file.
Run:    .venv/bin/python experiments/rc2_planning_gap/cost_tiering.py
        [--workers N]
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

from experiments.rc2_descriptor_v2.run_probe import ROSTER  # noqa: E402
from experiments.rc2_planning_gap.anchor_calibration import (  # noqa: E402
    STREAMS,
    play_cell,
    summarise,
)
from experiments.rc2_planning_gap.blind_seven_validation import (  # noqa: E402
    spearman,
)

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "cost_tiering.json"
OUT_MD = HERE / "COST_TIERING.md"

SEVEN = ("S1", "S2", "S3", "S4", "S5", "d4015a646ae3", "e1453dac5445")
POS = ("S2", "S3", "d4015a646ae3")        # full-convention PG >= +0.198
NEG = ("S1", "S4", "e1453dac5445")        # full-convention PG <= 0.000
LEADERS = ("S3", "d4015a646ae3")
TIERS = (
    dict(name="T1", deep=128, shallow=16, games_per_stream=12),
    dict(name="T2", deep=64, shallow=8, games_per_stream=12),
    dict(name="T3", deep=64, shallow=8, games_per_stream=6),
)
FULL_PG_SOURCES = ("anchor_calibration.json", "blind_seven_validation.json")


def full_reference() -> dict[str, float]:
    """Full-convention PG for the seven, from the merged probe records."""
    ref: dict[str, float] = {}
    for fname in FULL_PG_SOURCES:
        data = json.loads((HERE / fname).read_text())
        for k, r in data["results"].items():
            ref[k] = r["planning_gap"]
    assert all(k in ref for k in SEVEN)
    return ref


def tier_bars(tier_pg: dict[str, float]) -> tuple[bool, bool]:
    a1 = min(tier_pg[k] for k in POS) > max(tier_pg[k] for k in NEG)
    a2 = max(tier_pg, key=tier_pg.get) in LEADERS
    return a1, a2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    ref = full_reference()
    t0 = time.time()
    tasks = [(t["name"], key, stream, idx, t["deep"], t["shallow"],
              t["games_per_stream"])
             for t in TIERS for key in SEVEN for stream in STREAMS
             for idx in range(t["games_per_stream"])]
    cells: dict[tuple[str, str], list[dict]] = {}
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(play_cell, key, stream, idx,
                            deep_sims=deep, shallow_sims=shallow,
                            games_per_stream=gps): (tier, key)
                for tier, key, stream, idx, deep, shallow, gps in tasks}
        for fut in as_completed(futs):
            tier, key = futs[fut]
            cells.setdefault((tier, key), []).append(fut.result())
            done += 1
            if done % 40 == 0 or done == len(tasks):
                print(f"  {done}/{len(tasks)} games "
                      f"({time.time() - t0:.0f}s)", flush=True)

    tiers_out = {}
    for t in TIERS:
        name = t["name"]
        per_game = {key: summarise(key, cells[(name, key)]) for key in SEVEN}
        tier_pg = {k: per_game[k]["planning_gap"] for k in SEVEN}
        a1, a2 = tier_bars(tier_pg)
        cpu_s = {k: sum(c["elapsed_s"] for c in cells[(name, k)])
                 for k in SEVEN}
        tiers_out[name] = dict(
            config={k: t[k] for k in ("deep", "shallow", "games_per_stream")},
            n=2 * t["games_per_stream"],
            per_game=per_game,
            bars=dict(A1_sign_separation=a1, A2_leader=a2,
                      passes=a1 and a2),
            spearman_vs_full=spearman([tier_pg[k] for k in SEVEN],
                                      [ref[k] for k in SEVEN]),
            cpu_s_per_game=cpu_s,
            cpu_s_total=round(sum(cpu_s.values()), 1),
        )

    passing = [t["name"] for t in TIERS if tiers_out[t["name"]]["bars"]["passes"]]
    # Cheapest = last in TIERS order (T1 -> T3 is descending cost).
    adopted = passing[-1] if passing else None
    verdict = f"ADOPT_{adopted}" if adopted else "NO_TIER_QUALIFIES"
    detail = "; ".join(
        f"{n}: A1={tiers_out[n]['bars']['A1_sign_separation']} "
        f"A2={tiers_out[n]['bars']['A2_leader']} "
        f"rho={tiers_out[n]['spearman_vs_full']:+.2f} "
        f"cpu={tiers_out[n]['cpu_s_total']:.0f}s"
        for n in (t["name"] for t in TIERS))

    state = dict(
        protocol=dict(tiers=[dict(t) for t in TIERS],
                      bars="A1 min(PG over P) > max(PG over N), S5 free; "
                           "A2 argmax in {S3, d4015}; cheapest passing "
                           "tier adopted",
                      reference="full-convention PG from " +
                                " + ".join(FULL_PG_SOURCES)),
        full_reference=ref,
        tiers=tiers_out,
        verdict=verdict,
        verdict_detail=detail,
        elapsed_s=round(time.time() - t0, 1),
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# RC2 planning-gap — cost/noise tiering", "",
        "Which cheap tier preserves the full-convention screening "
        "properties? Bars pre-committed in `cost_tiering.py` (A1 sign "
        "separation of the positive set over the non-positive set, S5 "
        "free; A2 leader in {S3, d4015}); cheapest passing tier adopted "
        "for in-loop screening, full convention reserved for survivors.", "",
        "| tier | config | A1 | A2 | Spearman vs full | CPU total | "
        "CPU/game range |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for t in TIERS:
        n = t["name"]
        o = tiers_out[n]
        cg = o["cpu_s_per_game"]
        lines.append(
            f"| {n} | {t['deep']}v{t['shallow']}, n={2*t['games_per_stream']} "
            f"| {'PASS' if o['bars']['A1_sign_separation'] else 'FAIL'} "
            f"| {'PASS' if o['bars']['A2_leader'] else 'FAIL'} "
            f"| {o['spearman_vs_full']:+.2f} | {o['cpu_s_total']:.0f}s "
            f"| {min(cg.values()):.0f}–{max(cg.values()):.0f}s |")
    lines += ["", "## Per-game PG by tier", "",
              "| game | full | " + " | ".join(t["name"] for t in TIERS) + " |",
              "|---|---:|" + "---:|" * len(TIERS)]
    for key in SEVEN:
        row = f"| {key} | {ref[key]:+.3f} "
        for t in TIERS:
            row += (f"| {tiers_out[t['name']]['per_game'][key]['planning_gap']:+.3f} ")
        lines.append(row + "|")
    lines += ["", f"## Verdict: **{verdict}**", "", detail, "",
              f"Wall time: {state['elapsed_s']}s. COMPLETE", ""]
    OUT_MD.write_text("\n".join(lines))
    print(f"\nVERDICT: {verdict}")
    print(detail)
    print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
          flush=True)


if __name__ == "__main__":
    main()
