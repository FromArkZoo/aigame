"""RC2 descriptor-v2 probe runner — drama_v2 + insertion guards.

Implements experiments/rc2_descriptor_v2/PREREGISTRATION.md (the locked
contract): TacticalAgent-vs-TacticalAgent rollouts (n=100/game as 50
mirrored seed pairs), drama_v2 via the LOCKED
metrics.descriptors.obs_drama_for_rollout (imported, not copied), the
RUSH/REACH/TILT insertion guards, the five pre-registered bars (G-RUSH,
G-REACH, G-TILT, V2-RANK, V2-NONREG) and the locked decision grammar
(DESCRIPTOR_V2_GO / GUARDS_ONLY / DESCRIPTOR_V2_KILL / PROBE_INCOMPLETE).

Probe set: the Phase D seven (evaluations/rc2_phase_d/games/*.json,
identities per .blind_mapping.json) + the Phase B 10-game anchor set
(loaders imported from experiments.rc2_anchor.run_probe). The overlap pair
(d4015a646ae3, e1453dac5445) is evaluated ONCE — loaded from the registered
anchor source and asserted canonical-hash-identical to the blind-pack
F.json/B.json (verified equal at build time; the assert guards drift).

Rollout harness mirrors metrics/rollout_traces.py's loop shape (per-ply
owner snapshots on non-pie-swap steps, capture attribution by piece-count
drops, hard cap 2*max_game_steps) with TacticalAgent on both seats.

Parallelism note: per-rollout results depend only on (game, seed pair) —
TacticalAgent rollouts are fully deterministic given seeds — so farming
(game, pair-chunk) tasks over a process pool changes wall time only, never
results. Wall cap 2 h (prereg): exceeding it aborts to PROBE_INCOMPLETE.

Usage:
    .venv/bin/python -u experiments/rc2_descriptor_v2/run_probe.py \
        [--workers 7] [--games all|key1,key2,...] [--pairs 50]
    # any --games subset or --pairs != 50 => profiling mode: timing +
    # partial values printed, NO verdict, NO files (n=60 would need a
    # pre-data amendment commit; this runner never silently reduces n).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from metrics.descriptors import obs_drama_for_rollout  # noqa: E402
from metrics.tactical_agent import TacticalAgent  # noqa: E402
# Phase B anchor loaders + registered pod constants (locked runner; reused,
# not copied — the V2-NONREG bar applies the Phase B pods verbatim).
from experiments.rc2_anchor.run_probe import (  # noqa: E402
    ABOVE_KEYS,
    BELOW_KEYS,
    GAME_SPECS,
    GE_BOTTOM,
    GE_TOP,
    load_spec,
)

# ---------------------------------------------------------------------------
# Pre-registered constants — experiments/rc2_descriptor_v2/PREREGISTRATION.md.
# Transcribed as data; not altered after data.
# ---------------------------------------------------------------------------
N_PAIRS = 50          # "n=100 rollouts/game as 50 mirrored seed pairs"
WALL_CAP_S = 2 * 3600  # "wall cap 2 h"

RUSH_PLY_CAP = 6       # "winner in <= 6 plies"
RUSH_SHARE = 0.25      # ">= 25% of decisive tactical rollouts"
REACH_SHARE = 0.20     # "< 20% of tactical rollouts end decisively BEFORE max_turns"
TILT_SHARE = 0.80      # "P1 wins >= 80% of decisive games"

# Bars (prereg "Bars" section, verbatim).
BAR_TEXTS = {
    "G-RUSH": (
        "RUSH fires on S1; does NOT fire on e1453, d4015, s_flip_r2, "
        "a1_field_connect."
    ),
    "G-REACH": (
        "REACH fires on S2; does NOT fire on e1453. (Other threshold games "
        "reported, not binding.)"
    ),
    "G-TILT": (
        "TILT fires on >= 1 of {S4, S5}; does NOT fire on s_flip_r2 or "
        "a1_field_connect. (d4015 reported, not binding — its R8-era "
        "balance is unverified under tactical play.)"
    ),
    "V2-RANK": (
        "over the Phase D seven, drama_v2 of BOTH e1453 and d4015 exceeds "
        "drama_v2 of EVERY S-game on which at least one guard fires; and "
        "among guard-clean games, no S-game outranks both controls. "
        "(Spearman(drama_v2, blind mean) over all 7: reported, not binding.)"
    ),
    "V2-NONREG": (
        "the four Phase B bars (mean(ABOVE)>mean(BELOW); <=1 boundary "
        "inversion; e1453 above no ABOVE game; 573562833174 > e1453dac5445) "
        "PASS for drama_v2 on the Phase B pods."
    ),
}

# Phase D identities (evaluations/rc2_phase_d/.blind_mapping.json) + blind
# agent means (evaluations/rc2_phase_d/RESULTS.md unblinded table; same
# values quoted in this probe's prereg: 1.77/3.20/3.10/3.00/3.07/3.83/3.90).
PHASE_D_GAMES_DIR = ROOT / "evaluations/rc2_phase_d/games"
PHASE_D_SEVEN = ("S1", "S2", "S3", "S4", "S5",
                 "d4015a646ae3", "e1453dac5445")
S_GAMES = ("S1", "S2", "S3", "S4", "S5")
CONTROLS = ("e1453dac5445", "d4015a646ae3")

# ROSTER: every distinct game in the probe set (15 = Phase D 5 S-games +
# Phase B 10 anchors; the 2 controls overlap and are evaluated once).
# Families hardcoded from a one-time load of every source (2026-06-11);
# the drift guard in load_roster_game fails loud on divergence.
ROSTER: dict[str, dict] = {
    "S1": dict(source="phase_d", file="A", family="connection",
               blind_mean=1.77),
    "S2": dict(source="phase_d", file="D", family="threshold",
               blind_mean=3.20),
    "S3": dict(source="phase_d", file="E", family="connection",
               blind_mean=3.10),
    "S4": dict(source="phase_d", file="G", family="territory",
               blind_mean=3.00),
    "S5": dict(source="phase_d", file="C", family="territory",
               blind_mean=3.07),
    "d4015a646ae3": dict(source="anchor", check_file="F",
                         family="connection", blind_mean=3.83),
    "e1453dac5445": dict(source="anchor", check_file="B",
                         family="threshold", blind_mean=3.90),
    "s_flip_r2": dict(source="anchor", family="field_connection"),
    "a1_field_connect": dict(source="anchor", family="field_connection"),
    "d995cf010504": dict(source="anchor", family="threshold"),
    "573562833174": dict(source="anchor", family="connection"),
    "b12ff78f1c1d": dict(source="anchor", family="threshold"),
    "e52e8889517a": dict(source="anchor", family="threshold"),
    "bfd1bb7ced76": dict(source="anchor", family="threshold"),
    "1fea3357dca4": dict(source="anchor", family="threshold"),
}

# Cost ordering for task scheduling only (heavy boards first => better
# pool packing; zero effect on results).
_HEAVY_FIRST = (
    "s_flip_r2", "a1_field_connect", "e1453dac5445", "e52e8889517a",
    "bfd1bb7ced76", "1fea3357dca4", "S1", "S3", "d995cf010504",
    "573562833174", "b12ff78f1c1d", "S2", "S4", "S5", "d4015a646ae3",
)
assert set(_HEAVY_FIRST) == set(ROSTER)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_roster_game(key: str) -> GameDefV2:
    spec = ROSTER[key]
    if spec["source"] == "phase_d":
        path = PHASE_D_GAMES_DIR / f"{spec['file']}.json"
        if not path.exists():
            raise SystemExit(f"[{key}] blind-pack game not found: {path}")
        game = GameDefV2.from_dict(json.loads(path.read_text()))
    else:
        game = load_spec(GAME_SPECS[key])
        check_file = spec.get("check_file")
        if check_file:
            # Overlap pair: registered "evaluated once, used in both bar
            # sets" — assert the blind-pack copy is the same rule kernel.
            path = PHASE_D_GAMES_DIR / f"{check_file}.json"
            blind = GameDefV2.from_dict(json.loads(path.read_text()))
            if blind.canonical_hash() != game.canonical_hash():
                raise SystemExit(
                    f"[{key}] blind-pack {check_file}.json is not "
                    f"canonically identical to the anchor-source game — "
                    f"overlap reuse is invalid (drift?)"
                )
    actual = game.win_condition.condition_type
    if actual != spec["family"]:
        raise SystemExit(
            f"[{key}] family mismatch: registered '{spec['family']}', "
            f"loaded condition_type '{actual}'"
        )
    return game


# ---------------------------------------------------------------------------
# Rollout harness (mirrors metrics/rollout_traces.py's loop shape, with
# TacticalAgent on both seats)
# ---------------------------------------------------------------------------

def pair_seeds(i: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Pre-registered mirrored seed scheme: pair i -> agent seeds
    (1000*i+1, 1000*i+2); the mirrored game swaps them across seats.
    Pairs are indexed i = 0..N_PAIRS-1."""
    a, b = 1000 * i + 1, 1000 * i + 2
    return (a, b), (b, a)


def rollout_tactical(game: GameDefV2, seed_p1: int, seed_p2: int) -> dict:
    """One tactical-vs-tactical rollout; same trace dict shape as
    metrics.rollout_traces.rollout_with_traces."""
    engine = create_engine(game)
    obs = engine.reset()
    agents = [
        TacticalAgent(engine, player_num=1, seed=seed_p1),
        TacticalAgent(engine, player_num=2, seed=seed_p2),
    ]
    snapshots: list[np.ndarray] = []
    captures = 0
    prev_counts = list(engine.piece_counts)
    hard_cap = 2 * engine.game.max_game_steps

    while not engine.done and engine.step_count < hard_cap:
        legal = engine.get_legal_actions()
        agent = agents[engine.get_current_player()]  # 0-indexed
        action, _, _ = agent.select_action(obs, legal_actions=legal,
                                           deterministic=False)
        obs, _, _, info = engine.step(action)
        if not info.get("pie_swap"):
            for pidx in (0, 1):
                drop = prev_counts[pidx] - engine.piece_counts[pidx]
                if drop > 0:
                    captures += drop
            snapshots.append(engine.board_owners.copy())
        prev_counts = list(engine.piece_counts)

    return dict(
        policy="tactical",
        plies=len(snapshots),
        owner_snapshots=snapshots,
        winner=engine._winner,
        timeout=bool(getattr(engine, "_ended_by_max_turns", False)),
        captures_total=captures,
        game_length=engine.step_count,
    )


def run_pair_chunk(task: tuple[str, list[int]]) -> tuple[str, list[dict]]:
    """Worker: run a chunk of mirrored pairs for one game; return compact
    per-rollout records (drama computed in-worker via the LOCKED
    obs_drama_for_rollout; snapshots never cross the process boundary)."""
    key, pair_indices = task
    game = load_roster_game(key)
    topo = game.get_topology()
    records: list[dict] = []
    for i in pair_indices:
        for slot, (s1, s2) in enumerate(pair_seeds(i)):
            t0 = time.perf_counter()
            r = rollout_tactical(game, s1, s2)
            drama = obs_drama_for_rollout(game, topo, r)
            records.append(dict(
                pair=i, slot=slot, seed_p1=s1, seed_p2=s2,
                winner=r["winner"], plies=r["plies"],
                timeout=r["timeout"], game_length=r["game_length"],
                captures_total=r["captures_total"],
                drama=drama, wall_s=time.perf_counter() - t0,
            ))
    return key, records


# ---------------------------------------------------------------------------
# Guards (pure functions on per-rollout records; prereg "Insertion guards")
# ---------------------------------------------------------------------------

def guard_rush(records: list[dict]) -> tuple[bool, float]:
    """RUSH: fires iff >= 25% of decisive tactical rollouts end with a
    winner in <= 6 plies. Returns (fires, share). No decisive rollouts ->
    (False, nan)."""
    decisive = [r for r in records if r["winner"] is not None]
    if not decisive:
        return False, float("nan")
    share = sum(1 for r in decisive if r["plies"] <= RUSH_PLY_CAP) \
        / len(decisive)
    return share >= RUSH_SHARE, share


def guard_reach(records: list[dict], family: str) -> tuple[bool | None, float]:
    """REACH (threshold-family only): fires iff < 20% of tactical rollouts
    end decisively BEFORE max_turns (engine end-cause: winner set and not
    _ended_by_max_turns). Non-threshold families -> (None, nan) = n/a."""
    if family != "threshold":
        return None, float("nan")
    share = sum(1 for r in records
                if r["winner"] is not None and not r["timeout"]) \
        / len(records)
    return share < REACH_SHARE, share


def guard_tilt(records: list[dict]) -> tuple[bool, float]:
    """TILT: fires iff P1 wins >= 80% of decisive games across the
    mirrored pairs. Returns (fires, p1_share). No decisive -> (False, nan)."""
    decisive = [r for r in records if r["winner"] is not None]
    if not decisive:
        return False, float("nan")
    share = sum(1 for r in decisive if r["winner"] == 1) / len(decisive)
    return share >= TILT_SHARE, share


def guard_fired_any(rush: bool, reach: bool | None, tilt: bool) -> bool:
    return bool(rush) or bool(reach) or bool(tilt)


# ---------------------------------------------------------------------------
# Bars (pure functions; prereg "Bars" section)
# ---------------------------------------------------------------------------

def eval_bar_g_rush(rush: dict[str, bool]) -> tuple[bool, str]:
    protected = ("e1453dac5445", "d4015a646ae3", "s_flip_r2",
                 "a1_field_connect")
    ok = bool(rush["S1"]) and not any(rush[k] for k in protected)
    detail = (f"S1={'FIRES' if rush['S1'] else 'no'}; "
              + "; ".join(f"{k}={'FIRES' if rush[k] else 'no'}"
                          for k in protected))
    return ok, detail


def eval_bar_g_reach(reach: dict[str, bool | None]) -> tuple[bool, str]:
    ok = reach["S2"] is True and reach["e1453dac5445"] is False
    detail = (f"S2={'FIRES' if reach['S2'] else 'no'}; "
              f"e1453dac5445="
              f"{'FIRES' if reach['e1453dac5445'] else 'no'}")
    return ok, detail


def eval_bar_g_tilt(tilt: dict[str, bool]) -> tuple[bool, str]:
    ok = (bool(tilt["S4"]) or bool(tilt["S5"])) \
        and not tilt["s_flip_r2"] and not tilt["a1_field_connect"]
    detail = (f"S4={'FIRES' if tilt['S4'] else 'no'}, "
              f"S5={'FIRES' if tilt['S5'] else 'no'}; "
              f"s_flip_r2={'FIRES' if tilt['s_flip_r2'] else 'no'}, "
              f"a1_field_connect="
              f"{'FIRES' if tilt['a1_field_connect'] else 'no'}")
    return ok, detail


def eval_bar_v2_rank(drama: dict[str, float],
                     fired: dict[str, bool]) -> tuple[bool, str]:
    """V2-RANK over the Phase D seven (see BAR_TEXTS['V2-RANK']).

    fired: S-game -> "at least one guard fires". Conditions:
      (a) min(controls) > drama_v2 of every guard-fired S-game
          (vacuously true with no fired S-game);
      (b) no guard-clean S-game outranks BOTH controls, i.e. every clean
          S-game <= max(controls).
    Non-finite drama_v2 on any of the seven -> bar fails (not evaluable).
    """
    needed = list(S_GAMES) + list(CONTROLS)
    if not all(np.isfinite(drama.get(k, float("nan"))) for k in needed):
        return False, "not evaluable (non-finite drama_v2 among the seven)"
    cmin = min(drama[c] for c in CONTROLS)
    cmax = max(drama[c] for c in CONTROLS)
    fired_s = [s for s in S_GAMES if fired[s]]
    clean_s = [s for s in S_GAMES if not fired[s]]
    cond_a = all(cmin > drama[s] for s in fired_s)
    cond_b = all(drama[s] <= cmax for s in clean_s)
    detail = (
        f"controls e1453={drama['e1453dac5445']:.4f}, "
        f"d4015={drama['d4015a646ae3']:.4f}; "
        f"guard-fired S: "
        + (", ".join(f"{s}={drama[s]:.4f}" for s in fired_s) or "none")
        + f" (all < min(controls)={cmin:.4f}: {'YES' if cond_a else 'no'}); "
        f"guard-clean S: "
        + (", ".join(f"{s}={drama[s]:.4f}" for s in clean_s) or "none")
        + f" (none > max(controls)={cmax:.4f}: {'YES' if cond_b else 'no'})"
    )
    return cond_a and cond_b, detail


def eval_bar_v2_nonreg(drama: dict[str, float]) -> tuple[bool, str]:
    """V2-NONREG: the four Phase B bars applied to drama_v2 on the Phase B
    pods (experiments/rc2_anchor/PREREGISTRATION.md "Bars", verbatim:
    ABOVE pod {d4015a646ae3, s_flip_r2, a1_field_connect}, BELOW pod
    {e52e8889517a, bfd1bb7ced76, e1453dac5445, 1fea3357dca4}, BUFFER
    excluded; PASS iff ALL four hold):
      1. mean(ABOVE) > mean(BELOW)
      2. count of BELOW games above min(ABOVE) <= 1
      3. e1453dac5445 does not score above any ABOVE-pod game
      4. signal(573562833174) > signal(e1453dac5445)
    """
    needed = list(ABOVE_KEYS) + list(BELOW_KEYS) + [GE_BOTTOM]
    if not all(np.isfinite(drama.get(k, float("nan"))) for k in needed):
        return False, "not evaluable (non-finite drama_v2 among the pods)"
    above_mean = float(np.mean([drama[k] for k in ABOVE_KEYS]))
    below_mean = float(np.mean([drama[k] for k in BELOW_KEYS]))
    min_above = min(drama[k] for k in ABOVE_KEYS)
    inversions = sum(1 for k in BELOW_KEYS if drama[k] > min_above)
    b1 = above_mean > below_mean
    b2 = inversions <= 1
    b3 = drama[GE_TOP] <= min_above
    b4 = drama[GE_BOTTOM] > drama[GE_TOP]
    detail = (
        f"1. mean(ABOVE)={above_mean:.4f} vs mean(BELOW)={below_mean:.4f} "
        f"-> {'YES' if b1 else 'no'}; "
        f"2. inversions={inversions} (min ABOVE={min_above:.4f}) "
        f"-> {'YES' if b2 else 'no'}; "
        f"3. e1453={drama[GE_TOP]:.4f} <= min(ABOVE)={min_above:.4f} "
        f"-> {'YES' if b3 else 'no'}; "
        f"4. 573={drama[GE_BOTTOM]:.4f} > e1453={drama[GE_TOP]:.4f} "
        f"-> {'YES' if b4 else 'no'}"
    )
    return b1 and b2 and b3 and b4, detail


# ---------------------------------------------------------------------------
# Decision grammar (locked) — pure
# ---------------------------------------------------------------------------

def decide_verdict(bars: dict[str, bool],
                   incomplete: str | None = None) -> str:
    """Prereg "Decision grammar (locked)", verbatim:
      - All five bars pass -> DESCRIPTOR_V2_GO: re-registration of the
        archive probe (Phase C machinery + drama_v2 + the three guards at
        insertion) is authorized as next.
      - G-bars all pass, V2-RANK or V2-NONREG fails -> GUARDS_ONLY: guards
        adopted for any future archive work; quality signal stays open;
        the single registered escalation is one MCTS/planning-trace drama
        probe.
      - Any G-bar fails -> DESCRIPTOR_V2_KILL: that guard's design returns
        to analysis; no archive re-registration; report which and why.
      - Missing/unloadable games, wall cap (2 h), or harness failure ->
        PROBE_INCOMPLETE.
    """
    if incomplete:
        return "PROBE_INCOMPLETE"
    if not (bars["G-RUSH"] and bars["G-REACH"] and bars["G-TILT"]):
        return "DESCRIPTOR_V2_KILL"
    if bars["V2-RANK"] and bars["V2-NONREG"]:
        return "DESCRIPTOR_V2_GO"
    return "GUARDS_ONLY"


# ---------------------------------------------------------------------------
# Spearman (reported, not binding) — tie-aware, dependency-free
# ---------------------------------------------------------------------------

def _ranks(values: list[float]) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(len(v), dtype=float)
    i = 0
    sv = v[order]
    while i < len(v):
        j = i
        while j + 1 < len(v) and sv[j + 1] == sv[i]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        ranks[order[i:j + 1]] = avg
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    rx, ry = _ranks(xs), _ranks(ys)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = float(np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))
    if denom == 0.0:
        return float("nan")
    return float((rx * ry).sum() / denom)


# ---------------------------------------------------------------------------
# Aggregation + reporting
# ---------------------------------------------------------------------------

def summarize_game(key: str, records: list[dict]) -> dict:
    spec = ROSTER[key]
    dramas = [r["drama"] for r in records if r["drama"] is not None]
    draws = sum(1 for r in records if r["winner"] is None)
    decisive = len(records) - draws
    rush_f, rush_share = guard_rush(records)
    reach_f, reach_share = guard_reach(records, spec["family"])
    tilt_f, tilt_share = guard_tilt(records)
    agent_mean = spec.get(
        "blind_mean", GAME_SPECS.get(key, {}).get("agent_mean"))
    return dict(
        key=key,
        family=spec["family"],
        in_phase_d=key in PHASE_D_SEVEN,
        in_anchor=key in GAME_SPECS,
        agent_mean=agent_mean,
        n=len(records),
        decisive=decisive,
        draws=draws,
        drama_v2=float(np.mean(dramas)) if dramas else float("nan"),
        rush_fired=rush_f, rush_share=rush_share,
        reach_fired=reach_f, reach_share=reach_share,
        tilt_fired=tilt_f, tilt_p1_share=tilt_share,
        any_guard=guard_fired_any(rush_f, reach_f, tilt_f),
        mean_plies=float(np.mean([r["plies"] for r in records])),
        mean_length=float(np.mean([r["game_length"] for r in records])),
        wall_s=float(sum(r["wall_s"] for r in records)),
    )


def fmt(v, nd: int = 4) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    return f"{v:.{nd}f}"


def flag(fired) -> str:
    if fired is None:
        return "n/a"
    return "FIRES" if fired else "no"


def game_table_lines(rows: list[dict], md: bool = False) -> list[str]:
    if md:
        lines = [
            "| game | set | family | agent mean | n | decisive | draws "
            "| drama_v2 | RUSH (share) | REACH (share) | TILT (P1 share) "
            "| mean plies | wall s |",
            "|---|---|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|",
        ]
        for r in rows:
            sets = "+".join(s for s, has in
                            (("D", r["in_phase_d"]), ("B", r["in_anchor"]))
                            if has)
            lines.append(
                f"| {r['key']} | {sets} | {r['family']} "
                f"| {fmt(r['agent_mean'], 2)} | {r['n']} | {r['decisive']} "
                f"| {r['draws']} | {fmt(r['drama_v2'])} "
                f"| {flag(r['rush_fired'])} ({fmt(r['rush_share'], 2)}) "
                f"| {flag(r['reach_fired'])} ({fmt(r['reach_share'], 2)}) "
                f"| {flag(r['tilt_fired'])} ({fmt(r['tilt_p1_share'], 2)}) "
                f"| {fmt(r['mean_plies'], 1)} | {r['wall_s']:.0f} |")
        return lines
    header = (f"{'game':<18} {'set':<4} {'family':<17} {'mean':<5} "
              f"{'n':<4} {'dec':<4} {'draw':<5} {'drama_v2':<9} "
              f"{'RUSH':<12} {'REACH':<12} {'TILT(P1)':<13} "
              f"{'plies':<6} {'wall_s':<7}")
    lines = [header, "-" * len(header)]
    for r in rows:
        sets = "+".join(s for s, has in
                        (("D", r["in_phase_d"]), ("B", r["in_anchor"]))
                        if has)
        lines.append(
            f"{r['key']:<18} {sets:<4} {r['family']:<17} "
            f"{fmt(r['agent_mean'], 2):<5} {r['n']:<4} {r['decisive']:<4} "
            f"{r['draws']:<5} {fmt(r['drama_v2']):<9} "
            f"{flag(r['rush_fired']) + ' (' + fmt(r['rush_share'], 2) + ')':<12} "
            f"{flag(r['reach_fired']) + ' (' + fmt(r['reach_share'], 2) + ')':<12} "
            f"{flag(r['tilt_fired']) + ' (' + fmt(r['tilt_p1_share'], 2) + ')':<13} "
            f"{fmt(r['mean_plies'], 1):<6} {r['wall_s']:<7.0f}")
    return lines


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="RC2 descriptor-v2 probe — pre-registered drama_v2 + "
                    "guard calibration (PREREGISTRATION.md).")
    parser.add_argument("--pairs", type=int, default=N_PAIRS,
                        help="Mirrored seed pairs per game (registered: 50; "
                             "anything else => profiling mode, no verdict).")
    parser.add_argument("--games", type=str, default="all",
                        help="'all' or comma-separated keys (subset => "
                             "profiling mode, no verdict, no files).")
    parser.add_argument("--workers", type=int, default=7,
                        help="Process-pool size (results are scheduling-"
                             "independent). Default: 7.")
    parser.add_argument("--chunk", type=int, default=5,
                        help="Mirrored pairs per worker task. Default: 5.")
    parser.add_argument("--out", type=str,
                        default="experiments/rc2_descriptor_v2",
                        help="Output dir for probe_results.md/.csv "
                             "(full runs only).")
    args = parser.parse_args()

    t_start = time.time()

    if args.games.strip() == "all":
        requested = [k for k in _HEAVY_FIRST]
    else:
        requested = [k.strip() for k in args.games.split(",") if k.strip()]
        unknown = [k for k in requested if k not in ROSTER]
        if unknown:
            print(f"ERROR: unknown game keys {unknown}; valid: "
                  f"{list(ROSTER)}", file=sys.stderr)
            sys.exit(1)
        requested = [k for k in _HEAVY_FIRST if k in set(requested)]
    full_run = (set(requested) == set(ROSTER) and args.pairs == N_PAIRS)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    print(f"rc2 descriptor-v2 probe: pairs={args.pairs} "
          f"(n={2 * args.pairs}/game), games="
          f"{'all 15' if set(requested) == set(ROSTER) else requested}, "
          f"workers={args.workers}")
    print(f"Full registered run: {full_run}"
          + ("" if full_run else "  [profiling mode: NO verdict, NO files]"))
    print(flush=True)

    # Pre-flight: load every requested game in the main process. Unloadable
    # game on a full run => PROBE_INCOMPLETE per the locked grammar.
    incomplete: str | None = None
    try:
        for key in requested:
            load_roster_game(key)
    except SystemExit as exc:
        print(f"LOAD FAILURE: {exc}", file=sys.stderr)
        if not full_run:
            raise
        incomplete = f"unloadable game: {exc}"

    results: dict[str, dict] = {}
    if incomplete is None:
        tasks: list[tuple[str, list[int]]] = []
        for key in requested:
            pairs = list(range(args.pairs))
            for lo in range(0, len(pairs), args.chunk):
                tasks.append((key, pairs[lo:lo + args.chunk]))

        chunks_done: dict[str, int] = {k: 0 for k in requested}
        chunks_total: dict[str, int] = {k: 0 for k in requested}
        for key, _ in tasks:
            chunks_total[key] += 1
        records_by_game: dict[str, list[dict]] = {k: [] for k in requested}

        ctx = get_context("spawn")
        with ctx.Pool(processes=args.workers) as pool:
            it = pool.imap_unordered(run_pair_chunk, tasks)
            done_tasks = 0
            try:
                for key, records in it:
                    done_tasks += 1
                    records_by_game[key].extend(records)
                    chunks_done[key] += 1
                    elapsed = time.time() - t_start
                    if chunks_done[key] == chunks_total[key]:
                        n_rec = len(records_by_game[key])
                        dec = sum(1 for r in records_by_game[key]
                                  if r["winner"] is not None)
                        print(f"  [{key}] complete: n={n_rec} "
                              f"decisive={dec} "
                              f"game_wall={sum(r['wall_s'] for r in records_by_game[key]):.0f}s "
                              f"elapsed={elapsed:.0f}s "
                              f"({done_tasks}/{len(tasks)} tasks)",
                              flush=True)
                    else:
                        print(f"  [{key}] chunk {chunks_done[key]}/"
                              f"{chunks_total[key]} elapsed={elapsed:.0f}s "
                              f"({done_tasks}/{len(tasks)} tasks)",
                              flush=True)
                    if elapsed > WALL_CAP_S and done_tasks < len(tasks):
                        incomplete = (f"wall cap 2 h exceeded "
                                      f"({elapsed:.0f}s) with "
                                      f"{len(tasks) - done_tasks} tasks "
                                      f"outstanding")
                        pool.terminate()
                        break
            except Exception as exc:  # harness failure -> PROBE_INCOMPLETE
                if not full_run:
                    raise
                incomplete = f"harness failure: {exc!r}"
                pool.terminate()

        for key in requested:
            recs = records_by_game[key]
            if len(recs) == 2 * args.pairs:
                recs.sort(key=lambda r: (r["pair"], r["slot"]))
                results[key] = summarize_game(key, recs)
            elif incomplete is None and full_run:
                incomplete = f"game {key} incomplete ({len(recs)} rollouts)"

    wall = time.time() - t_start

    # ------------------------------------------------------------------
    # Per-game table
    # ------------------------------------------------------------------
    rows = [results[k] for k in ROSTER if k in results]
    print()
    for line in game_table_lines(rows):
        print(line)
    print()

    if not full_run:
        print("Profiling mode — no verdict, no files (registered protocol "
              "is all 15 games x 50 pairs; n reduction requires a pre-data "
              "amendment commit).")
        # Projection helper for the registered profiling step.
        for r in rows:
            per_rollout = r["wall_s"] / max(1, r["n"])
            print(f"  [{r['key']}] {per_rollout:.1f}s/rollout -> "
                  f"projected {per_rollout * 2 * N_PAIRS:.0f}s "
                  f"serial for n={2 * N_PAIRS}")
        return

    # ------------------------------------------------------------------
    # Bars + verdict (full runs only)
    # ------------------------------------------------------------------
    bars: dict[str, bool] = {}
    details: dict[str, str] = {}
    spear = float("nan")
    if incomplete is None:
        drama = {k: results[k]["drama_v2"] for k in results}
        rush = {k: results[k]["rush_fired"] for k in results}
        reach = {k: results[k]["reach_fired"] for k in results}
        tilt = {k: results[k]["tilt_fired"] for k in results}
        fired = {k: results[k]["any_guard"] for k in results}

        bars["G-RUSH"], details["G-RUSH"] = eval_bar_g_rush(rush)
        bars["G-REACH"], details["G-REACH"] = eval_bar_g_reach(reach)
        bars["G-TILT"], details["G-TILT"] = eval_bar_g_tilt(tilt)
        bars["V2-RANK"], details["V2-RANK"] = eval_bar_v2_rank(drama, fired)
        bars["V2-NONREG"], details["V2-NONREG"] = eval_bar_v2_nonreg(drama)

        ds = [drama[k] for k in PHASE_D_SEVEN]
        bs = [ROSTER[k]["blind_mean"] for k in PHASE_D_SEVEN]
        if all(np.isfinite(d) for d in ds):
            spear = spearman(ds, bs)

        for name in ("G-RUSH", "G-REACH", "G-TILT", "V2-RANK", "V2-NONREG"):
            print(f"BAR {name}: {'PASS' if bars[name] else 'FAIL'}")
            print(f"  text: {BAR_TEXTS[name]}")
            print(f"  detail: {details[name]}")
        print(f"Spearman(drama_v2, blind mean) over the Phase D seven: "
              f"{fmt(spear)} (reported, not binding)")
        print()

    verdict = decide_verdict(bars, incomplete)
    print(f"VERDICT: {verdict}")
    if incomplete:
        print(f"  reason: {incomplete}")
    print(f"Total wall: {wall:.0f}s")

    # ------------------------------------------------------------------
    # probe_results.md + probe_results.csv
    # ------------------------------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)

    md = [
        "# RC2 descriptor-v2 probe — results",
        "",
        f"n={2 * args.pairs} tactical-vs-tactical rollouts/game as "
        f"{args.pairs} mirrored seed pairs (pair i -> agent seeds "
        f"(1000*i+1, 1000*i+2), i=0..{args.pairs - 1}; mirrored game swaps "
        f"them across seats). TacticalAgent per "
        f"metrics/tactical_agent.py (WIN-IN-1 -> BLOCK-WIN-IN-1 -> densify; "
        f"always swaps on pie). drama_v2 = winner_behindness via the LOCKED "
        f"metrics.descriptors.obs_drama_for_rollout on tactical traces; "
        f"per-game mean over non-draw rollouts, draws counted. Hard cap "
        f"2*max_game_steps. Protocol + bars per "
        f"experiments/rc2_descriptor_v2/PREREGISTRATION.md (locked).",
        "",
        f"Total wall: {wall:.0f}s (cap {WALL_CAP_S}s). Workers: "
        f"{args.workers} (per-rollout results depend only on (game, seed "
        f"pair); scheduling cannot change them).",
        "",
        "## Per-game table",
        "",
        "Set: D = Phase D seven, B = Phase B anchor ten (overlap pair "
        "evaluated once, canonical-hash-checked against the blind pack). "
        "Agent mean: Phase D blind mean / Phase B registered agent mean "
        "(d4015 and e1453 carry their Phase D blind means 3.83 / 3.90).",
        "",
    ]
    md += game_table_lines(rows, md=True)
    md += ["", "## Bars (transcribed verbatim; point estimates)", ""]
    if incomplete is None:
        md += ["| bar | text | detail | pass |", "|---|---|---|:---:|"]
        for name in ("G-RUSH", "G-REACH", "G-TILT", "V2-RANK", "V2-NONREG"):
            md.append(f"| {name} | {BAR_TEXTS[name]} | {details[name]} "
                      f"| {'PASS' if bars[name] else 'FAIL'} |")
        md += [
            "",
            f"Spearman(drama_v2, blind mean) over the Phase D seven: "
            f"**{fmt(spear)}** (reported, not binding; Phase D "
            f"random-rollout drama scored −0.68 on the same seven).",
        ]
    else:
        md += [f"Bars not evaluated: {incomplete}"]
    md += [
        "",
        "## Verdict",
        "",
        "```",
        verdict,
        "```",
        "",
    ]
    if incomplete:
        md += [f"Reason: {incomplete}", ""]
    md += [
        "## Notes",
        "",
        "- BLOCK-WIN-IN-1 is constructed exactly (no win-condition-delta "
        "approximation): the engine's step() is trust-the-caller, so the "
        "forced opponent action is a scratch-clone restore + "
        "current_player override + step; the engine's own win check "
        "decides. Placement-only per the prereg (opponent pass/move/"
        "multi-place wins are not blocked; multi_place games are scanned "
        "one placement deep — the S1-style first-strike threat).",
        "- Clone = create-once scratch engine + full mutable-state "
        "snapshot/restore (measured faster than copy.deepcopy ~1.3 ms and "
        "re-create+replay ~15 ms per clone; verified state-identical to "
        "deepcopy+step in test_rc2_descriptor_v2.py). Live engines are "
        "never mutated by the scans.",
        "- REACH is threshold-family-only (n/a elsewhere); binding only on "
        "S2 (must fire) and e1453 (must not). Other threshold games' REACH "
        "flags are reported, not binding. TILT on d4015 is reported, not "
        "binding.",
        "- metrics/descriptors.py, metrics/rollout_traces.py, training/, "
        "game_engine/, evolution/ untouched; drama_v2 imports the locked "
        "obs_drama_for_rollout (threshold-family dual parameterization "
        "and all formula choices inherited unchanged).",
    ]
    md_path = out_dir / "probe_results.md"
    md_path.write_text("\n".join(md) + "\n")

    csv_path = out_dir / "probe_results.csv"
    fieldnames = ["key", "family", "in_phase_d", "in_anchor", "agent_mean",
                  "n", "decisive", "draws", "drama_v2",
                  "rush_fired", "rush_share", "reach_fired", "reach_share",
                  "tilt_fired", "tilt_p1_share", "any_guard",
                  "mean_plies", "mean_length", "wall_s"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r[k])
                        for k in fieldnames})

    print(f"\nWrote {md_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
