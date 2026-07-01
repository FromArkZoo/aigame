"""RC2 §0 lock obligation — CAL-R [C8]: REACH-v3 revalidated at the T1 instrument.

Pre-data instrument measurement (no campaign data). The campaign's guard-stage
REACH-v3 (§4) fires on the T1 instrument, not the full-conv instrument that the
original reach_v3.py validated (256v16, n=48, streams 44/45, share>=0.25). This
obligation revalidates the guard at the T1 conventions and the re-priced
absolute threshold registered in §4.

Protocol (registered §0/§4)
---------------------------
  Instrument : net-free UCT@128 vs UCT@16 (T1), seat-balanced, max_steps=400
               (play_cell, anchor_calibration.py conventions).
  Games      : S2 and e1453dac5445 (the threshold family), n=24 each
               (12 per stream), FRESH streams 46/47 (reserved anchor slot,
               disjoint from anchor 42/43, full-conv REACH 44/45, and the
               campaign base-19 streams).
  Guard      : REACH-v3 fires iff the genome's own T1 games with winner None
               >= 5/24 (re-priced from 0.25x48 so the validated positive S2
               sits >=1 sigma inside the firing region).

PASS bars (binding — mirror reach_v3.py wording at the T1 instrument)
  B1: FIRES on S2 (winner-None count >= 5/24).
  B2: does NOT fire on e1453dac5445.

Output: cal_r.json + CAL_R.md next to this file.
Run:    .venv/bin/python experiments/rc2_campaign/cal_r.py [--workers N]
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
from experiments.rc2_planning_gap.anchor_calibration import play_cell  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "cal_r.json"
OUT_MD = HERE / "CAL_R.md"

DEEP_SIMS = 128            # T1 instrument (NOT the 256 full-conv)
SHALLOW_SIMS = 16
STREAMS = (46, 47)        # fresh — reserved anchor slot, campaign-disjoint
GAMES_PER_STREAM = 12     # -> n=24
FIRE_COUNT = 5            # >= 5/24 winner-None (re-priced §4 threshold)
BINDING = ("S2", "e1453dac5445")


def summarise(key: str, cells: list[dict]) -> dict:
    n = len(cells)
    none_games = sum(1 for c in cells if c["winner"] is None)
    by_stream = {
        str(s): sum(1 for c in cells if c["stream"] == s
                    and c["winner"] is None)
        for s in STREAMS
    }
    return dict(key=key, blind_mean=ROSTER[key].get("blind_mean"), n=n,
                winner_none=none_games, draw_share=none_games / n,
                per_stream_none=by_stream,
                fires=none_games >= FIRE_COUNT,
                mean_length=float(np.mean([c["length"] for c in cells])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    keys = list(BINDING)
    t0 = time.time()
    tasks = [(k, stream, idx) for k in keys for stream in STREAMS
             for idx in range(GAMES_PER_STREAM)]
    cells: dict[str, list[dict]] = {k: [] for k in keys}
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(play_cell, k, stream, idx,
                            deep_sims=DEEP_SIMS, shallow_sims=SHALLOW_SIMS,
                            games_per_stream=GAMES_PER_STREAM): k
                for k, stream, idx in tasks}
        for fut in as_completed(futs):
            cell = fut.result()
            cells[cell["key"]].append(cell)
            done += 1
            if done % 12 == 0 or done == len(tasks):
                print(f"  {done}/{len(tasks)} games "
                      f"({time.time() - t0:.0f}s)", flush=True)
    results = {k: summarise(k, cells[k]) for k in keys}
    for k in keys:
        r = results[k]
        print(f"  {k}: winner_none {r['winner_none']}/{r['n']} "
              f"(share {r['draw_share']:.3f}) fires={r['fires']}", flush=True)

    b1 = results["S2"]["fires"]
    b2 = not results["e1453dac5445"]["fires"]
    verdict = "PASS" if (b1 and b2) else "FAIL"
    detail = (f"B1 fires-on-S2: {'PASS' if b1 else 'FAIL'} "
              f"(winner_none {results['S2']['winner_none']}/24); "
              f"B2 silent-on-e1453: {'PASS' if b2 else 'FAIL'} "
              f"(winner_none {results['e1453dac5445']['winner_none']}/24)")

    state = dict(
        obligation="cal_r",
        protocol=dict(instrument=f"UCT@{DEEP_SIMS} vs UCT@{SHALLOW_SIMS} (T1)",
                      streams=list(STREAMS), games_per_stream=GAMES_PER_STREAM,
                      n=2 * GAMES_PER_STREAM, fire_count=FIRE_COUNT,
                      definition=f"fires iff winner-None games >= {FIRE_COUNT}/24",
                      bars="B1 fires on S2; B2 silent on e1453"),
        results=results,
        verdict=verdict,
        verdict_detail=detail,
        elapsed_s=round(time.time() - t0, 1),
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# CAL-R — REACH-v3 revalidated at the T1 instrument  [C8]", "",
        f"RC2 §0 lock obligation. T1 instrument (UCT@{DEEP_SIMS} vs "
        f"UCT@{SHALLOW_SIMS}), fresh streams {list(STREAMS)}, n="
        f"{2 * GAMES_PER_STREAM}, re-priced threshold "
        f"winner-None >= {FIRE_COUNT}/24 (§4).", "",
        "| game | blind mean | n | winner-None | share | per-stream None "
        "| fires | mean plies |",
        "|---|---:|---:|---:|---:|---|---|---:|",
    ]
    for k in ["S2", "e1453dac5445"]:
        r = results[k]
        per_stream = ", ".join(str(v) for v in r["per_stream_none"].values())
        lines.append(
            f"| {k} (binding) | {r['blind_mean']} | {r['n']} "
            f"| **{r['winner_none']}** | {r['draw_share']:.3f} | {per_stream} "
            f"| {'FIRES' if r['fires'] else '—'} | {r['mean_length']:.1f} |")
    lines += ["", f"## Verdict: **{verdict}**", "", detail, "",
              f"Wall time: {state['elapsed_s']}s. COMPLETE", ""]
    OUT_MD.write_text("\n".join(lines))
    print(f"\nVERDICT: {verdict} — {detail}")
    print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
          flush=True)


if __name__ == "__main__":
    main()
