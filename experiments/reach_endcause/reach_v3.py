"""REACH-v3 — end-cause guard under UCT play (successor registered by REACH_V2.md).

REACH-v2 established that threshold-unreachability is policy-relative:
TacticalAgent crosses S2's threshold in 100/100 rollouts, so no end-cause
definition over tactical rollouts can fire. REACH-v3 asks the same
end-cause question — is the game decided BY its win condition or not
decided at all — under the play that exhibits the pathology and is now
load-bearing for selection: the PG convention's UCT games.

Guard (pre-committed)
---------------------
  REACH-v3 (threshold-family only): fires iff
      draw_share = share of PG-convention games with winner None >= 0.25
  Games: net-free UCT@256 vs UCT@16, seat-balanced, play_game max_steps=400
  — anchor_calibration.py verbatim, but FRESH seed streams (44, 45), 24
  games each (n=48), so no recorded game is reused for a binding bar.

  Threshold 0.25 a priori: a quarter of competent games failing to produce
  a winner is the registered "draw-prone" line. Feasibility informed by
  recorded data (S2 0.354, all other blind-seven games <= 0.021 at streams
  42/43) — disclosed, not blinded; the binding test is fresh streams.

  In-loop cost is ZERO: the screening games a PG-based search already
  plays yield draw_share for free.

PASS bars (binding — mirrors the original G-REACH bar wording)
--------------------------------------------------------------
  B1: REACH-v3 FIRES on S2 (draw_share >= 0.25 on fresh streams).
  B2: REACH-v3 does NOT fire on e1453dac5445.
  Other threshold-family roster games: n=24 (streams 44/45, 12 each),
  reported, not binding.

Output: reach_v3.json + REACH_V3.md next to this file.
Run:    .venv/bin/python experiments/reach_endcause/reach_v3.py [--workers N]
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
    play_cell,
)

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "reach_v3.json"
OUT_MD = HERE / "REACH_V3.md"

STREAMS = (44, 45)          # fresh — never used by any recorded PG probe
DRAW_SHARE = 0.25
BINDING = ("S2", "e1453dac5445")
N_BINDING = 24              # per stream -> n=48
N_DIAG = 12                 # per stream -> n=24


def summarise(key: str, cells: list[dict], games_per_stream: int) -> dict:
    n = len(cells)
    draws = sum(1 for c in cells if c["winner"] is None)
    by_stream = {
        str(s): sum(1 for c in cells if c["stream"] == s
                    and c["winner"] is None) / games_per_stream
        for s in STREAMS
    }
    share = draws / n
    return dict(key=key, blind_mean=ROSTER[key].get("blind_mean"), n=n,
                draws=draws, draw_share=share, per_stream=by_stream,
                fires=share >= DRAW_SHARE,
                mean_length=float(np.mean([c["length"] for c in cells])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    keys = [k for k in ROSTER if ROSTER[k]["family"] == "threshold"]
    t0 = time.time()
    gps = {k: (N_BINDING if k in BINDING else N_DIAG) for k in keys}
    tasks = [(k, stream, idx) for k in keys for stream in STREAMS
             for idx in range(gps[k])]
    cells: dict[str, list[dict]] = {k: [] for k in keys}
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(play_cell, k, stream, idx,
                            games_per_stream=gps[k]): k
                for k, stream, idx in tasks}
        for fut in as_completed(futs):
            cell = fut.result()
            cells[cell["key"]].append(cell)
            done += 1
            if done % 24 == 0 or done == len(tasks):
                print(f"  {done}/{len(tasks)} games "
                      f"({time.time() - t0:.0f}s)", flush=True)
    results = {k: summarise(k, cells[k], gps[k]) for k in keys}
    for k in keys:
        r = results[k]
        print(f"  {k}: draw_share {r['draw_share']:.3f} (n={r['n']}) "
              f"fires={r['fires']}", flush=True)

    b1 = results["S2"]["fires"]
    b2 = not results["e1453dac5445"]["fires"]
    verdict = "PASS" if (b1 and b2) else "FAIL"
    detail = (f"B1 fires-on-S2: {'PASS' if b1 else 'FAIL'} "
              f"(draw_share {results['S2']['draw_share']:.3f}); "
              f"B2 silent-on-e1453: {'PASS' if b2 else 'FAIL'} "
              f"(draw_share {results['e1453dac5445']['draw_share']:.3f})")

    state = dict(
        protocol=dict(streams=list(STREAMS), draw_share_bar=DRAW_SHARE,
                      n_binding=2 * N_BINDING, n_diag=2 * N_DIAG,
                      definition="fires iff share of PG-convention UCT "
                                 "games with winner None >= 0.25",
                      bars="B1 fires on S2; B2 silent on e1453; others "
                           "reported, not binding"),
        results=results,
        verdict=verdict,
        verdict_detail=detail,
        elapsed_s=round(time.time() - t0, 1),
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# REACH-v3 — end-cause guard under UCT play", "",
        "Successor to REACH-v2 (FAIL: threshold-unreachability is policy-"
        "relative; tactical play crosses S2's threshold 100/100). Same "
        "end-cause question under the PG convention's UCT games on FRESH "
        "seed streams (44/45). Protocol pre-committed in `reach_v3.py`; "
        "bars mirror the original G-REACH wording.", "",
        "| game | blind mean | n | draw share | per-stream | fires "
        "| mean plies |",
        "|---|---:|---:|---:|---|---|---:|",
    ]
    order = ["S2", "e1453dac5445"] + sorted(
        k for k in results if k not in BINDING)
    for k in order:
        r = results[k]
        per_stream = ", ".join(f"{v:.3f}" for v in r["per_stream"].values())
        lines.append(
            f"| {k}{' (binding)' if k in BINDING else ''} "
            f"| {r['blind_mean']} | {r['n']} | **{r['draw_share']:.3f}** "
            f"| {per_stream} | {'FIRES' if r['fires'] else '—'} "
            f"| {r['mean_length']:.1f} |")
    lines += ["", f"## Verdict: **{verdict}**", "", detail, "",
              "In-loop cost: zero — a PG-based search already plays these "
              "games; draw_share falls out of the screening records.", "",
              f"Wall time: {state['elapsed_s']}s. COMPLETE", ""]
    OUT_MD.write_text("\n".join(lines))
    print(f"\nVERDICT: {verdict} — {detail}")
    print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
          flush=True)


if __name__ == "__main__":
    main()
