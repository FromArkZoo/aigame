"""RC2 §0 lock obligation — CAL-G [C2]: RUSH/TILT guard revalidation at n=24.

Pre-data instrument measurement (no campaign data). The campaign guard stage
(§4) runs the RUSH/TILT guards at n=24 (12 mirrored TacticalAgent pairs), a
quarter of the n=100 at which experiments/rc2_descriptor_v2 validated them.
This obligation confirms the guard pattern still holds at the smaller n and
publishes the binomial false-fire diagnostics that the drop to n=24 incurs.

Reuse (not copy): the guard functions, rollout harness, mirrored-seed scheme
and loader are imported from experiments.rc2_descriptor_v2.run_probe (the
locked descriptor-v2 runner). Only n and the game subset change here.

Protocol (registered §0/§4)
---------------------------
  Games      : S1 (RUSH target), S4/S5 (TILT targets), and the four negative
               controls d4015a646ae3, e1453dac5445, s_flip_r2, a1_field_connect.
  Rollouts   : 12 mirrored pairs -> n=24 tactical-vs-tactical games/game,
               pair_seeds(i) for i=0..11 (run_probe mirrored-seed scheme).
  Guards     : RUSH fires iff >=25% of DECISIVE games end in <=6 plies;
               TILT fires iff P1 wins >=80% of DECISIVE games. (Constants are
               the descriptor-v2 values; §4 re-prices nothing here — CAL-G
               confirms they transfer to n=24.)

PASS bars (binding)
  B-RUSH: RUSH fires on S1; silent on all four controls.
  B-TILT: TILT fires on >=1 of {S4, S5}; silent on s_flip_r2, a1_field_connect
          (d4015/e1453 also reported silent).

Reported, not binding: per-game binomial false-fire / miss probabilities at
n=24 (P that an independent re-run flips the guard, using the game's observed
rate as the point estimate) — the resolution cost of n=24 vs n=100.

Output: cal_g.json + CAL_G.md next to this file.
Run:    .venv/bin/python experiments/rc2_campaign/cal_g.py [--workers N]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.rc2_descriptor_v2.run_probe import (  # noqa: E402
    RUSH_PLY_CAP,
    RUSH_SHARE,
    TILT_SHARE,
    guard_rush,
    guard_tilt,
    load_roster_game,
    pair_seeds,
    rollout_tactical,
)

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "cal_g.json"
OUT_MD = HERE / "CAL_G.md"

N_PAIRS = 12                       # -> n=24 (§4)
RUSH_TARGET = "S1"
TILT_TARGETS = ("S4", "S5")
CONTROLS = ("d4015a646ae3", "e1453dac5445", "s_flip_r2", "a1_field_connect")
GAMES = (RUSH_TARGET, *TILT_TARGETS, *CONTROLS)


def binom_sf_ge(k: int, n: int, p: float) -> float:
    """P(Binomial(n, p) >= k), exact (n small)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return float(sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j)
                     for j in range(k, n + 1)))


def rollout_game(task: tuple[str, int]) -> tuple[str, list[dict]]:
    key, n_pairs = task
    game = load_roster_game(key)
    records: list[dict] = []
    for i in range(n_pairs):
        for (s1, s2) in pair_seeds(i):
            r = rollout_tactical(game, s1, s2)
            records.append(dict(winner=r["winner"], plies=r["plies"]))
    return key, records


def guard_diagnostics(records: list[dict]) -> dict:
    decisive = [r for r in records if r["winner"] is not None]
    d = len(decisive)
    rush_f, rush_share = guard_rush(records)
    tilt_f, tilt_share = guard_tilt(records)
    diag = dict(n=len(records), decisive=d,
                rush_fires=rush_f, rush_share=rush_share,
                tilt_fires=tilt_f, tilt_p1_share=tilt_share)
    if d > 0:
        # false-fire (if currently silent) or miss (if currently firing):
        # probability an independent n=24 re-run flips the flag, using the
        # observed share as the point estimate. k = smallest count that fires.
        k_rush = math.ceil(RUSH_SHARE * d)
        k_tilt = math.ceil(TILT_SHARE * d)
        p_rush_fire = binom_sf_ge(k_rush, d, rush_share)
        p_tilt_fire = binom_sf_ge(k_tilt, d, tilt_share)
        diag["rush_flip_prob"] = p_rush_fire if not rush_f else 1 - p_rush_fire
        diag["tilt_flip_prob"] = p_tilt_fire if not tilt_f else 1 - p_tilt_fire
    else:
        diag["rush_flip_prob"] = float("nan")
        diag["tilt_flip_prob"] = float("nan")
    return diag


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    t0 = time.time()
    results: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(rollout_game, (k, N_PAIRS)): k for k in GAMES}
        for fut in as_completed(futs):
            key, records = fut.result()
            results[key] = guard_diagnostics(records)
            r = results[key]
            print(f"  [{key}] n={r['n']} dec={r['decisive']} "
                  f"RUSH={'FIRES' if r['rush_fires'] else '—'} "
                  f"({r['rush_share']:.2f}) "
                  f"TILT={'FIRES' if r['tilt_fires'] else '—'} "
                  f"({r['tilt_p1_share']:.2f}) ({time.time()-t0:.0f}s)",
                  flush=True)

    rush_target_fires = results[RUSH_TARGET]["rush_fires"]
    rush_controls_silent = all(not results[c]["rush_fires"] for c in CONTROLS)
    tilt_target_fires = any(results[t]["tilt_fires"] for t in TILT_TARGETS)
    tilt_controls_silent = (not results["s_flip_r2"]["tilt_fires"]
                            and not results["a1_field_connect"]["tilt_fires"])

    b_rush = rush_target_fires and rush_controls_silent
    b_tilt = tilt_target_fires and tilt_controls_silent
    verdict = "PASS" if (b_rush and b_tilt) else "FAIL"
    detail = (
        f"B-RUSH: {'PASS' if b_rush else 'FAIL'} "
        f"(S1 fires={rush_target_fires}, controls silent={rush_controls_silent}); "
        f"B-TILT: {'PASS' if b_tilt else 'FAIL'} "
        f"(S4|S5 fires={tilt_target_fires}, field controls silent="
        f"{tilt_controls_silent})"
    )

    state = dict(
        obligation="cal_g",
        protocol=dict(n_pairs=N_PAIRS, n=2 * N_PAIRS,
                      rush_ply_cap=RUSH_PLY_CAP, rush_share=RUSH_SHARE,
                      tilt_share=TILT_SHARE,
                      rush_target=RUSH_TARGET, tilt_targets=list(TILT_TARGETS),
                      controls=list(CONTROLS),
                      bars="B-RUSH: S1 fires, controls silent; "
                           "B-TILT: >=1 of {S4,S5} fires, field controls silent"),
        results=results, verdict=verdict, verdict_detail=detail,
        elapsed_s=round(time.time() - t0, 1),
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# CAL-G — RUSH/TILT guard revalidation at n=24  [C2]", "",
        f"RC2 §0 lock obligation. 12 mirrored TacticalAgent pairs -> n=24, "
        f"pair_seeds(0..11); guards + harness reused from the locked "
        f"descriptor-v2 runner. RUSH: >=25% decisive in <=6 plies. "
        f"TILT: P1 >=80% of decisive.", "",
        "| game | role | n | decisive | RUSH (share) | TILT (P1 share) "
        "| flip-prob RUSH | flip-prob TILT |",
        "|---|---|---:|---:|---|---|---:|---:|",
    ]
    roles = {RUSH_TARGET: "RUSH target", "S4": "TILT target",
             "S5": "TILT target", "d4015a646ae3": "control",
             "e1453dac5445": "control", "s_flip_r2": "control (field)",
             "a1_field_connect": "control (field)"}
    for k in GAMES:
        r = results[k]
        lines.append(
            f"| {k} | {roles[k]} | {r['n']} | {r['decisive']} "
            f"| {'FIRES' if r['rush_fires'] else '—'} ({r['rush_share']:.2f}) "
            f"| {'FIRES' if r['tilt_fires'] else '—'} ({r['tilt_p1_share']:.2f}) "
            f"| {r['rush_flip_prob']:.3f} | {r['tilt_flip_prob']:.3f} |")
    lines += ["", f"## Verdict: **{verdict}**", "", detail, "",
              "flip-prob = P an independent n=24 re-run flips the guard flag "
              "(observed share as point estimate); reported, not binding — the "
              "resolution cost of n=24. Low on silent controls = robustly "
              "silent.", "",
              f"Wall time: {state['elapsed_s']}s. COMPLETE", ""]
    OUT_MD.write_text("\n".join(lines))
    print(f"\nVERDICT: {verdict} — {detail}")
    print(f"wrote {OUT_JSON.name}, {OUT_MD.name} in {state['elapsed_s']}s",
          flush=True)


if __name__ == "__main__":
    main()
