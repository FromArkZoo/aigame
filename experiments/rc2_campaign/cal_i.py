"""RC2 pre-campaign gate — CAL-I: instrument check [§5].

Pre-data instrument measurement (no campaign data). Before any search spend,
the runner (run_campaign.py::load_cal_i) refuses to start a REAL campaign
without a cal_i.json verdict of PASS. CAL-I demonstrates that the T1
planning-gap instrument (net-free UCT@128 vs UCT@16, the campaign's per-
genome quality signal — pg_eval.py / anchor_calibration.py conventions)
still separates the registered anchor pair at the campaign's own instrument
settings, on FRESH streams disjoint from every other reserved slot (anchor
42/43, full-conv REACH 44/45, CAL-R/CAL-G's own slots, the campaign base-19
streams) — the same fresh-stream discipline CAL-R used for REACH-v3 (§4).

Protocol (registered §5)
-------------------------
  Instrument : play_cell (rc2_planning_gap/anchor_calibration.py, LOCKED —
               imported, never modified), deep_sims=128, shallow_sims=16
               (the T1 instrument, NOT anchor_calibration's own 256v16
               full-conv default).
  Games      : d4015a646ae3 (blind-preferred connection control) and S4
               (maximally-close Goodharted elite, part of the registered
               closeness-confound pair) — the anchor_calibration binding
               pair minus S5 (S5 is diagnostic-only for CAL-I; the §5
               obligation is the single scalar separation below).
  Streams    : 46, 47 (fresh — reserved anchor slot; disjoint from every
               other CAL-*/campaign stream). 12 games/stream -> n=24/game.
  Signal     : PG(game) = mean(score) - 0.5, same convention as
               anchor_calibration.summarise / pg_eval.pg_summarise (draws
               score 0.5, deep side's perspective, seat-balanced).

PASS bar (binding, registered)
-------------------------------
  PG(d4015a646ae3) - PG(S4) >= bars.CAL_I_THRESHOLD (imported, never
  hardcoded here). FAIL -> PROBE_INVALID; no campaign.

File contract (belt-and-braces, owner-gated real spend)
---------------------------------------------------------
  --real      Run the REAL n=24/game measurement; writes cal_i.json +
              CAL_I.md next to this file. This is the ONLY invocation that
              produces the artifact run_campaign.py::load_cal_i requires to
              unlock a real campaign.
  --dry-run   Tiny wiring check (n=4/game, sims 32v8, same two games/
              streams); writes cal_i_dryrun.json + CAL_I_DRYRUN.md. NEVER
              writes cal_i.json/CAL_I.md — a dry run can never unlock a
              campaign.
  (neither)  Refuses to run anything (real spend is owner-gated) and
              prints how to invoke either mode.
  --from-cache  Re-derives verdict + MD from the existing JSON for the
              selected mode (--real or --dry-run) without re-running
              games (mirrors cal_g.py's --from-cache pattern).

Output: cal_i.json + CAL_I.md (real) or cal_i_dryrun.json + CAL_I_DRYRUN.md
(dry run), next to this file.
Run:    .venv/bin/python experiments/rc2_campaign/cal_i.py --real
        .venv/bin/python experiments/rc2_campaign/cal_i.py --dry-run
        .venv/bin/python experiments/rc2_campaign/cal_i.py --real --from-cache
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

from experiments.rc2_campaign.bars import CAL_I_THRESHOLD  # noqa: E402
from experiments.rc2_descriptor_v2.run_probe import ROSTER  # noqa: E402
from experiments.rc2_planning_gap.anchor_calibration import play_cell  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "cal_i.json"           # REAL artifact — unlocks the campaign
OUT_MD = HERE / "CAL_I.md"
DRYRUN_JSON = HERE / "cal_i_dryrun.json"  # dry-run artifact — never unlocks it
DRYRUN_MD = HERE / "CAL_I_DRYRUN.md"

DEEP_SIMS = 128            # T1 instrument (campaign's own per-genome signal)
SHALLOW_SIMS = 16
STREAMS = (46, 47)         # fresh — reserved anchor slot, campaign-disjoint
GAMES_PER_STREAM = 12      # -> n=24
WORKERS = 7
BINDING = ("d4015a646ae3", "S4")   # registered §5 pair

# --dry-run wiring-check sizing — tiny, non-binding, never touches OUT_JSON.
DRY_DEEP_SIMS = 32
DRY_SHALLOW_SIMS = 8
DRY_GAMES_PER_STREAM = 2   # -> n=4


def summarise(key: str, cells: list[dict]) -> dict:
    """Per-game PG summary — mirrors anchor_calibration.summarise."""
    n = len(cells)
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
        n=n,
        planning_gap=float(np.mean(scores)) - 0.5,
        per_stream=by_stream,
        wins=sum(1 for c in cells if c["score"] == 1.0),
        draws=sum(1 for c in cells if c["score"] == 0.5),
        losses=sum(1 for c in cells if c["score"] == 0.0),
        mean_length=float(np.mean([c["length"] for c in cells])),
    )


def verdict_from_pg(pg_d4015: float, pg_s4: float) -> tuple[str, float, str]:
    """Pure §5 bar: PG(d4015) - PG(S4) >= CAL_I_THRESHOLD -> PASS else FAIL."""
    separation = pg_d4015 - pg_s4
    verdict = "PASS" if separation >= CAL_I_THRESHOLD else "FAIL"
    detail = (f"PG(d4015a646ae3) {pg_d4015:+.4f} - PG(S4) {pg_s4:+.4f} = "
              f"separation {separation:+.4f} vs bar >= {CAL_I_THRESHOLD} "
              f"-> {verdict}")
    return verdict, separation, detail


def route_paths(dry_run: bool) -> tuple[Path, Path]:
    """File-contract routing (belt-and-braces): a dry run NEVER returns the
    real cal_i.json/CAL_I.md paths — those are the only paths
    run_campaign.py::load_cal_i reads to unlock a real campaign."""
    return (DRYRUN_JSON, DRYRUN_MD) if dry_run else (OUT_JSON, OUT_MD)


def build_state(results: dict[str, dict], *, elapsed: float,
                streams: tuple[int, ...], games_per_stream: int,
                deep_sims: int, shallow_sims: int, dry_run: bool,
                from_cache: bool) -> dict:
    """Pure JSON-state builder — the contract run_campaign.py::load_cal_i
    consumes (`{"verdict": ...}` at minimum). Never touches disk."""
    verdict, separation, detail = verdict_from_pg(
        results["d4015a646ae3"]["planning_gap"], results["S4"]["planning_gap"])
    return dict(
        obligation="cal_i",
        dry_run=dry_run,
        from_cache=from_cache,
        protocol=dict(
            instrument=f"UCT@{deep_sims} vs UCT@{shallow_sims} (T1, "
                       "net-free, play_cell)",
            streams=list(streams),
            games_per_stream=games_per_stream,
            n=2 * games_per_stream,
            deep_sims=deep_sims,
            shallow_sims=shallow_sims,
            binding=list(BINDING),
            threshold=CAL_I_THRESHOLD,
            bar="PG(d4015a646ae3) - PG(S4) >= CAL_I_THRESHOLD",
        ),
        results=results,
        separation=separation,
        verdict=verdict,
        verdict_detail=detail,
        elapsed_s=round(elapsed, 1),
    )


def render_md(state: dict) -> str:
    p = state["protocol"]
    lines = [
        "# CAL-I — pre-campaign instrument check  [§5]"
        + (" (DRY RUN — wiring check only, NOT the binding measurement)"
           if state["dry_run"] else ""),
        "",
        f"RC2 §5 pre-campaign gate. T1 instrument (UCT@{p['deep_sims']} vs "
        f"UCT@{p['shallow_sims']}, net-free, play_cell), fresh streams "
        f"{p['streams']}, n={p['n']}, threshold CAL_I_THRESHOLD="
        f"{p['threshold']} (bars.py, imported).", "",
        "| game | blind mean | family | n | PG (mean) | per-stream PG | "
        "W/D/L (deep) | mean plies |",
        "|---|---:|---|---:|---:|---|---|---:|",
    ]
    for key in BINDING:
        r = state["results"][key]
        per_stream = ", ".join(f"{v:+.3f}" for v in r["per_stream"].values())
        lines.append(
            f"| {key} | {r['blind_mean']} | {r['family']} | {r['n']} "
            f"| **{r['planning_gap']:+.3f}** | {per_stream} "
            f"| {r['wins']}/{r['draws']}/{r['losses']} "
            f"| {r['mean_length']:.1f} |")
    lines += [
        "", f"## Verdict: **{state['verdict']}**", "", state["verdict_detail"],
        "",
        "Bar: PG(d4015a646ae3) - PG(S4) >= CAL_I_THRESHOLD. FAIL -> "
        "PROBE_INVALID (prereg §9); no campaign.", "",
        f"{'(verdict re-derived from cached results; no game re-run)' if state['from_cache'] else ''}",
        f"Wall time: {state['elapsed_s']}s. "
        f"{'DRY RUN — non-binding' if state['dry_run'] else 'COMPLETE'}", "",
    ]
    return "\n".join(lines)


def finalize(results: dict[str, dict], *, elapsed: float,
            streams: tuple[int, ...], games_per_stream: int,
            deep_sims: int, shallow_sims: int, dry_run: bool,
            from_cache: bool) -> dict:
    """Builds state, writes JSON+MD to the routed paths, prints the verdict.
    Returns the state dict."""
    state = build_state(results, elapsed=elapsed, streams=streams,
                        games_per_stream=games_per_stream,
                        deep_sims=deep_sims, shallow_sims=shallow_sims,
                        dry_run=dry_run, from_cache=from_cache)
    out_json, out_md = route_paths(dry_run)
    out_json.write_text(json.dumps(state, indent=2))
    out_md.write_text(render_md(state))
    print(f"\nVERDICT: {state['verdict']} — {state['verdict_detail']}")
    print(f"wrote {out_json.name}, {out_md.name} in {state['elapsed_s']}s",
          flush=True)
    return state


def run_measurement(*, deep_sims: int, shallow_sims: int,
                    games_per_stream: int, workers: int, dry_run: bool,
                    from_cache: bool) -> dict:
    out_json, _ = route_paths(dry_run)
    if from_cache:
        cached = json.loads(out_json.read_text())
        return finalize(cached["results"], elapsed=0.0, streams=STREAMS,
                        games_per_stream=cached["protocol"]["games_per_stream"],
                        deep_sims=cached["protocol"]["deep_sims"],
                        shallow_sims=cached["protocol"]["shallow_sims"],
                        dry_run=dry_run, from_cache=True)

    t0 = time.time()
    keys = list(BINDING)
    tasks = [(k, stream, idx) for k in keys for stream in STREAMS
             for idx in range(games_per_stream)]
    cells: dict[str, list[dict]] = {k: [] for k in keys}
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(play_cell, k, stream, idx,
                            deep_sims=deep_sims, shallow_sims=shallow_sims,
                            games_per_stream=games_per_stream): k
                for k, stream, idx in tasks}
        for fut in as_completed(futs):
            cell = fut.result()
            cells[cell["key"]].append(cell)
            done += 1
            if done % 8 == 0 or done == len(tasks):
                print(f"  {done}/{len(tasks)} games "
                      f"({time.time() - t0:.0f}s)", flush=True)
    results = {k: summarise(k, cells[k]) for k in keys}
    for k in keys:
        r = results[k]
        print(f"  {k}: PG {r['planning_gap']:+.3f} (n={r['n']})", flush=True)
    return finalize(results, elapsed=time.time() - t0, streams=STREAMS,
                    games_per_stream=games_per_stream, deep_sims=deep_sims,
                    shallow_sims=shallow_sims, dry_run=dry_run,
                    from_cache=False)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--real", action="store_true",
                      help="Run the REAL CAL-I measurement (n=24/game, "
                           "owner-gated real spend). Writes cal_i.json — "
                           "the only artifact that unlocks a real campaign.")
    mode.add_argument("--dry-run", action="store_true",
                      help="Tiny wiring check (n=4/game, sims 32v8). Writes "
                           "cal_i_dryrun.json — NEVER cal_i.json.")
    parser.add_argument("--from-cache", action="store_true",
                        help="Re-derive verdict + MD from the existing JSON "
                             "for the selected mode; no games re-run.")
    parser.add_argument("--workers", type=int, default=WORKERS)
    args = parser.parse_args(argv)

    if not args.real and not args.dry_run:
        print(
            "CAL-I: refusing to run without an explicit mode.\n"
            "This is the prereg §5 pre-campaign instrument gate — real "
            "spend is owner-gated (a run writes cal_i.json, which unlocks "
            "the real campaign).\n"
            "  Wiring check (tiny, non-binding): "
            "--dry-run\n"
            "  Real measurement (n=24/game, owner-gated): --real",
            flush=True)
        return

    if args.dry_run:
        deep_sims, shallow_sims = DRY_DEEP_SIMS, DRY_SHALLOW_SIMS
        games_per_stream = DRY_GAMES_PER_STREAM
    else:
        deep_sims, shallow_sims = DEEP_SIMS, SHALLOW_SIMS
        games_per_stream = GAMES_PER_STREAM

    run_measurement(deep_sims=deep_sims, shallow_sims=shallow_sims,
                    games_per_stream=games_per_stream, workers=args.workers,
                    dry_run=args.dry_run, from_cache=args.from_cache)


if __name__ == "__main__":
    main()
