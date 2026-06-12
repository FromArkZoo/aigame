"""RC2 planning-gap — blind-seven range validation (Phase-D-style Spearman).

The anchor calibration PASSED on the registered confound pair. This probe
asks the question that killed drama at Phase D: does the signal survive the
FULL blind seven, or does it Goodhart immediately beyond the anchor pair?
(Random-rollout drama: Spearman −0.68 over these games; competent-trace
drama: −0.31.)

Protocol: IDENTICAL to anchor_calibration.py (net-free UCT@256 vs UCT@16,
n=48 seat-balanced, streams 42/43, draws 0.5, same per-(stream,idx) seed
derivation). S1, S2, S3 are measured fresh; S4, S5, d4015, e1453 are
REUSED verbatim from anchor_calibration.json — same protocol and seeds, so
a re-run would reproduce them; reuse is stated, not hidden.

Registration honesty: four of the seven PG values are KNOWN at registration
time. The bar below was checked for fairness against them — with e1453's
known misrank the maximum achievable Spearman is bounded near +0.4, so the
bar is set at the no-inversion line, mirroring how Phase D used the
statistic (a −0.68 was damning; the ask here is the sign).

PASS bar (binding)
------------------
  Spearman(raw PG, blind mean) over the seven  >  0

Diagnostics (non-binding, reported only)
----------------------------------------
  - Spearman over the SIX excluding e1453, the one game where the two
    ground truths disagree (blind 3.90 vs R21 agent depth rank 6/7; the
    anchor-calibration addendum already argued PG sides with the agents).
  - Spearman with PG floored at 0 (informative-region rule).
  - Per-game table.

Output: blind_seven_validation.json + BLIND_SEVEN_VALIDATION.md.
Run:    .venv/bin/python experiments/rc2_planning_gap/blind_seven_validation.py
"""
from __future__ import annotations

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
    GAMES_PER_STREAM,
    STREAMS,
    WORKERS,
    play_cell,
    summarise,
)

HERE = Path(__file__).resolve().parent
ANCHOR_JSON = HERE / "anchor_calibration.json"
OUT_JSON = HERE / "blind_seven_validation.json"
OUT_MD = HERE / "BLIND_SEVEN_VALIDATION.md"

FRESH = ("S1", "S2", "S3")
REUSED = ("S4", "S5", "d4015a646ae3", "e1453dac5445")
CONTESTED = "e1453dac5445"


def spearman(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation, average ranks on ties (n is tiny)."""
    def ranks(v):
        order = np.argsort(v)
        r = np.empty(len(v))
        r[order] = np.arange(1, len(v) + 1, dtype=float)
        # average ties
        vals = np.asarray(v, dtype=float)
        for u in np.unique(vals):
            mask = vals == u
            if mask.sum() > 1:
                r[mask] = r[mask].mean()
        return r
    rx, ry = ranks(x), ranks(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = float(np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))
    return float((rx * ry).sum() / denom) if denom else 0.0


def main() -> None:
    t0 = time.time()
    anchor = json.loads(ANCHOR_JSON.read_text())
    assert anchor["complete"] and anchor["verdict"] == "PASS"
    results: dict[str, dict] = {k: anchor["results"][k] for k in REUSED}

    tasks = [(key, stream, idx) for key in FRESH for stream in STREAMS
             for idx in range(GAMES_PER_STREAM)]
    cells: dict[str, list[dict]] = {key: [] for key in FRESH}
    done = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(play_cell, *t): t for t in tasks}
        for fut in as_completed(futures):
            cell = fut.result()
            cells[cell["key"]].append(cell)
            done += 1
            if done % 16 == 0 or done == len(tasks):
                print(f"  {done}/{len(tasks)} games "
                      f"({time.time() - t0:.0f}s)", flush=True)
    for key in FRESH:
        results[key] = summarise(key, cells[key])

    seven = sorted(results, key=lambda k: ROSTER[k]["blind_mean"])
    pg = [results[k]["planning_gap"] for k in seven]
    blind = [ROSTER[k]["blind_mean"] for k in seven]
    rho_raw = spearman(pg, blind)
    six = [k for k in seven if k != CONTESTED]
    rho_six = spearman([results[k]["planning_gap"] for k in six],
                       [ROSTER[k]["blind_mean"] for k in six])
    rho_floor = spearman([max(p, 0.0) for p in pg], blind)
    verdict = "PASS" if rho_raw > 0 else "FAIL"
    detail = (f"Spearman(raw PG, blind) over seven = {rho_raw:+.3f} — "
              f"bar: > 0; diagnostics: six excl. e1453 {rho_six:+.3f}, "
              f"floored {rho_floor:+.3f}")

    state = dict(
        protocol="anchor_calibration.py frozen protocol; S1/S2/S3 fresh, "
                 "S4/S5/d4015/e1453 reused verbatim from "
                 "anchor_calibration.json (identical protocol + seeds)",
        bar="Spearman(raw PG, blind mean) over the seven > 0",
        results=results,
        spearman=dict(raw_seven=rho_raw, six_excl_e1453=rho_six,
                      floored_seven=rho_floor),
        verdict=verdict,
        verdict_detail=detail,
        elapsed_s=round(time.time() - t0, 1),
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# RC2 planning-gap — blind-seven range validation", "",
        "Phase-D-style Spearman over the full blind seven — the check that "
        "killed drama (−0.68 random-rollout, −0.31 competent-trace). "
        "Protocol frozen in `anchor_calibration.py`; S1/S2/S3 fresh, the "
        "four anchors reused verbatim (identical protocol + seeds). Bar "
        "pre-committed in `blind_seven_validation.py` with four of seven "
        "values known; fairness against the known values is argued in the "
        "script docstring.", "",
        "| game | blind mean | family | PG | per-stream | W/D/L (deep) |",
        "|---|---:|---|---:|---|---|",
    ]
    for k in seven:
        r = results[k]
        per_stream = ", ".join(f"{v:+.3f}" for v in r["per_stream"].values())
        lines.append(f"| {k}{' (contested)' if k == CONTESTED else ''} "
                     f"| {r['blind_mean']} | {r['family']} "
                     f"| **{r['planning_gap']:+.3f}** | {per_stream} "
                     f"| {r['wins']}/{r['draws']}/{r['losses']} |")
    lines += [
        "", f"## Verdict: **{verdict}**", "", detail, "",
        f"Wall time: {state['elapsed_s']}s. COMPLETE", "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"\nVERDICT: {verdict} — {detail}")
    print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
          flush=True)


if __name__ == "__main__":
    main()
