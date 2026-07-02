"""RC2 §0 lock obligation — CAL-G [C2]: RUSH/TILT guard revalidation at n=24.

Pre-data instrument measurement (no campaign data). The campaign guard stage
(§4) runs the RUSH/TILT guards at n=24 (12 mirrored TacticalAgent pairs), a
quarter of the n=100 at which experiments/rc2_descriptor_v2 validated them.
This obligation confirms the guard pattern transfers to the smaller n and
RE-PRICES the constants where n=24 forces it (§4: "constants re-priced at
CAL-G"; cf. CAL-R's REACH 0.25x48 -> 5/24).

Finding: RUSH (0.25) transfers flawlessly — S1 fires 18/18 decisive <=6 plies,
every control 0.00, flip-prob 0.000. TILT at the descriptor-v2 0.80 is
UNRESOLVABLE at n=24 — S4/S5 land at 19/24=0.79 (flip-prob 0.42, a coin-flip).
TILT is re-priced to 0.625 (=15/24), the count equidistant (~2 sigma) from the
S4/S5 targets (19/24) and the highest control d4015 (11/24); at 0.625 the
binding B-TILT PASSES with re-run flip-prob ~0.01.

Reuse (not copy): guard rollout harness, mirrored-seed scheme and loader are
imported from experiments.rc2_descriptor_v2.run_probe. --from-cache re-derives
the verdict from a prior run's saved shares (the field-connection games cost
~45 min at n=24; re-pricing needs no re-run).

PASS bars (binding)
  B-RUSH: RUSH (0.25) fires on S1; silent on all four controls.
  B-TILT: TILT (re-priced 0.625) fires on >=1 of {S4, S5}; silent on
          s_flip_r2, a1_field_connect (d4015/e1453 also reported silent).

Output: cal_g.json + CAL_G.md next to this file.
Run:    .venv/bin/python experiments/rc2_campaign/cal_g.py [--workers N]
        .venv/bin/python experiments/rc2_campaign/cal_g.py --from-cache
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
    TILT_SHARE as TILT_DESCRIPTOR_V2,
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
# Re-priced TILT for the n=24 instrument (CAL-G, §4). descriptor-v2's 0.80 is
# unresolvable at n=24; 0.625=15/24 sits ~2 sigma from both the S4/S5 targets
# (19/24) and the highest control d4015 (11/24). RUSH is unchanged at 0.25.
TILT_REPRICED = 0.625
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
    tilt_f80, tilt_share = guard_tilt(records)          # 0.80 (context)
    return _diag_from_shares(len(records), d, rush_f, rush_share, tilt_share)


def _diag_from_shares(n: int, d: int, rush_f: bool, rush_share: float,
                      tilt_share: float) -> dict:
    """Verdict-relevant diagnostics at the BINDING thresholds (RUSH 0.25,
    TILT re-priced 0.625). Pure — used by both the fresh run and --from-cache."""
    tilt_f = tilt_share >= TILT_REPRICED
    tilt_f80 = tilt_share >= TILT_DESCRIPTOR_V2
    diag = dict(n=n, decisive=d,
                rush_fires=rush_f, rush_share=rush_share,
                tilt_fires=tilt_f, tilt_p1_share=tilt_share,
                tilt_fires_v2_080=tilt_f80)
    if d > 0:
        k_rush = math.ceil(RUSH_SHARE * d)
        k_tilt = math.ceil(TILT_REPRICED * d)
        p_rush_fire = binom_sf_ge(k_rush, d, rush_share)
        p_tilt_fire = binom_sf_ge(k_tilt, d, tilt_share)
        diag["rush_flip_prob"] = p_rush_fire if not rush_f else 1 - p_rush_fire
        diag["tilt_flip_prob"] = p_tilt_fire if not tilt_f else 1 - p_tilt_fire
    else:
        diag["rush_flip_prob"] = float("nan")
        diag["tilt_flip_prob"] = float("nan")
    return diag


def evaluate(results: dict[str, dict]) -> tuple[str, str, dict]:
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
        f"B-TILT@{TILT_REPRICED}: {'PASS' if b_tilt else 'FAIL'} "
        f"(S4|S5 fires={tilt_target_fires}, field controls silent="
        f"{tilt_controls_silent})"
    )
    return verdict, detail, dict(b_rush=b_rush, b_tilt=b_tilt)


def finalize(results: dict[str, dict], elapsed: float, from_cache: bool) -> None:
    verdict, detail, _ = evaluate(results)
    state = dict(
        obligation="cal_g",
        protocol=dict(n_pairs=N_PAIRS, n=2 * N_PAIRS,
                      rush_ply_cap=RUSH_PLY_CAP, rush_share=RUSH_SHARE,
                      tilt_share_binding=TILT_REPRICED,
                      tilt_share_descriptor_v2=TILT_DESCRIPTOR_V2,
                      rush_target=RUSH_TARGET, tilt_targets=list(TILT_TARGETS),
                      controls=list(CONTROLS),
                      reprice_note="TILT re-priced 0.80->0.625 for n=24 (§4); "
                                   "RUSH unchanged at 0.25",
                      bars="B-RUSH: S1 fires, controls silent; "
                           "B-TILT: >=1 of {S4,S5} fires, field controls silent"),
        results=results, verdict=verdict, verdict_detail=detail,
        from_cache=from_cache, elapsed_s=round(elapsed, 1),
    )
    OUT_JSON.write_text(json.dumps(state, indent=2))

    lines = [
        "# CAL-G — RUSH/TILT guard revalidation at n=24  [C2]", "",
        f"RC2 §0 lock obligation. 12 mirrored TacticalAgent pairs -> n=24, "
        f"pair_seeds(0..11); guards + harness reused from the locked "
        f"descriptor-v2 runner. RUSH: >=25% decisive in <=6 plies. "
        f"**TILT re-priced 0.80 -> {TILT_REPRICED} for n=24** (§4); RUSH "
        f"unchanged at 0.25.", "",
        "| game | role | n | dec | RUSH (share) | TILT P1 share | fires@0.625 "
        "| would fire@0.80 | flip-prob TILT |",
        "|---|---|---:|---:|---|---:|---|---|---:|",
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
            f"| {r['tilt_p1_share']:.2f} "
            f"| {'FIRES' if r['tilt_fires'] else '—'} "
            f"| {'fires' if r['tilt_fires_v2_080'] else '—'} "
            f"| {r['tilt_flip_prob']:.3f} |")
    lines += [
        "", f"## Verdict: **{verdict}**", "", detail, "",
        f"Re-pricing rationale: at descriptor-v2's TILT=0.80, S4/S5 (19/24="
        f"0.79) do NOT fire and flip-prob=0.42 — the guard is a coin-flip at "
        f"n=24. TILT={TILT_REPRICED} (15/24) is equidistant from the S4/S5 "
        f"targets (19) and the highest control d4015 (11) — ~2σ each side; at "
        f"0.625 flip-prob≈0.01. RUSH needs no re-pricing (S1 fires 18/18, "
        f"controls 0.00, flip-prob 0.000).",
        "",
        "flip-prob = P an independent n=24 re-run flips the guard flag "
        "(observed share as point estimate); reported, not binding.",
        "",
        f"{'(verdict re-derived from cached shares; no game re-run)' if from_cache else ''}",
        f"Wall time: {state['elapsed_s']}s. COMPLETE", ""]
    OUT_MD.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nVERDICT: {verdict} — {detail}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--from-cache", action="store_true",
                        help="re-derive verdict from a prior cal_g.json's "
                             "saved shares (no game re-run).")
    args = parser.parse_args()

    if args.from_cache:
        cached = json.loads(OUT_JSON.read_text())["results"]
        results = {k: _diag_from_shares(
            cached[k]["n"], cached[k]["decisive"],
            cached[k]["rush_fires"], cached[k]["rush_share"],
            cached[k]["tilt_p1_share"]) for k in GAMES}
        finalize(results, elapsed=0.0, from_cache=True)
        return

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
    finalize(results, elapsed=time.time() - t0, from_cache=False)


if __name__ == "__main__":
    main()
