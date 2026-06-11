"""RC2 anchor probe runner — descriptor separation over the registered anchors.

Implements experiments/rc2_anchor/PREREGISTRATION.md (the locked contract):
10 anchor games in three pods (ABOVE / BUFFER / BELOW), four candidate
columns (obs_drama, blend, interaction_rate, go_essence control), seeded
rollouts via metrics.rollout_traces.run_protocol (anchor_drama seeding
verbatim), per-game 1000-resample bootstrap 95% CIs, the four pre-registered
separation bars evaluated per column, and the locked decision grammar
(PHASE_C_GO / PHASE_C_GO_INTERACTION / RC2_KILL / PROBE_INCOMPLETE, plus the
GE_CONTROL_PASSED flag).

metrics/descriptors.py is LOCKED: the per-rollout values needed for the
bootstrap are assembled HERE from its public per-rollout functions
(obs_drama_for_rollout, obs_lead_changes_from_snapshots,
interaction_rate_for_rollout), and the resulting means are cross-checked
against descriptor_row on the first game processed (exact-equality assert).

Conventions mirror experiments/siege/anchor_drama.py: GAME_SPECS with a
family-drift guard (SystemExit on condition_type mismatch), contextlib.closing
DB loads, loud missing-file errors, md report, subset --games -> no verdict.

Usage:
    .venv/bin/python experiments/rc2_anchor/run_probe.py \
        [--n 200] [--seed 11] [--games all|key1,key2,...] \
        [--out experiments/rc2_anchor]
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
import warnings
from contextlib import closing
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from metrics.rollout_traces import run_protocol  # noqa: E402
from metrics.descriptors import (  # noqa: E402
    descriptor_row,
    interaction_rate_for_rollout,
    obs_drama_for_rollout,
    obs_lead_changes_from_snapshots,
)
# Public per-player axis resolution (same formula as descriptors' private
# _axis_for_player; both mirror engine_v2's _check_connection dispatch).
from experiments.siege.anchor_drama import get_axis_for_player  # noqa: E402

# ---------------------------------------------------------------------------
# Pre-registered constants — experiments/rc2_anchor/PREREGISTRATION.md.
# Transcribed as data; not altered after data.
# ---------------------------------------------------------------------------
N_BOOT = 1000          # "Per-game bootstrap CI (1000 resamples)"
CI_LO, CI_HI = 2.5, 97.5

# Pods (prereg "Anchor set"): ABOVE = agent mean >= 3.9; BUFFER = 3.7 < mean
# < 3.9 (reported, excluded from binary separation bars); BELOW = mean <= 3.7.
ABOVE_KEYS = ("d4015a646ae3", "s_flip_r2", "a1_field_connect")
BUFFER_KEYS = ("d995cf010504", "573562833174", "b12ff78f1c1d")
BELOW_KEYS = ("e52e8889517a", "bfd1bb7ced76", "e1453dac5445", "1fea3357dca4")

GE_TOP = "e1453dac5445"      # secondary-check pair (prereg "Secondary check")
GE_BOTTOM = "573562833174"

# Bars (prereg "Bars" section, verbatim): "A candidate PASSES iff ALL four
# conditions hold". BUFFER games are excluded from bars; the secondary
# GE-inversion check is binding and evaluated separately from the pods.
BAR_TEXTS = (
    "1. mean(ABOVE) > mean(BELOW)",
    "2. boundary inversions: count of BELOW games above min(ABOVE) <= 1",
    "3. e1453dac5445 does not score above any ABOVE-pod game",
    "4. secondary (binding): signal(573562833174) > signal(e1453dac5445)",
)

# Candidate columns (prereg "Candidate columns"): 1 obs_drama (primary),
# 2 blend = sqrt(norm(obs_drama) x norm(obs_lead_changes)), 3 interaction_rate
# (cheap-skeptic control), 4 go_essence (expected-FAIL control; R21 DBs only).
CANDIDATES = ("obs_drama", "blend", "interaction_rate", "go_essence")

# GAME_SPECS: families hardcoded from a one-time development load of every
# source (2026-06-11); the drift guard below catches any future divergence.
# ge_db: prereg candidate 4 registers go_essence for the R21 games ONLY and
# '—' for d4015a646ae3, s_flip_r2, a1_field_connect. NOTE (documented, not a
# deviation): genesis_v2_run8.db DOES hold a run8-era go_essence for
# d4015a646ae3 (0.3858), but the registered column definition excludes it
# (R8-era GE is not comparable to R21 GE), so ge_db stays None there.
GAME_SPECS: dict[str, dict] = {
    "d4015a646ae3": dict(
        pod="ABOVE", agent_mean=4.10, family="connection",
        source="db", db="genesis_v2_run8.db", game_id="d4015a646ae3",
        ge_db=None,
    ),
    "s_flip_r2": dict(
        pod="ABOVE", agent_mean=4.10, family="field_connection",
        source="json",
        path=ROOT / "experiments/siege/games/calibrated/s_flip_r2.json",
        ge_db=None,
    ),
    "a1_field_connect": dict(
        pod="ABOVE", agent_mean=3.90, family="field_connection",
        source="json",
        path=ROOT / "experiments/siege/games/a1_field_connect.json",
        ge_db=None,
    ),
    "d995cf010504": dict(
        pod="BUFFER", agent_mean=3.78, family="threshold",
        source="db", db="genesis_v2_run21_carpet.db", game_id="d995cf010504",
        ge_db="genesis_v2_run21_carpet.db",
    ),
    "573562833174": dict(
        pod="BUFFER", agent_mean=3.78, family="connection",
        source="db", db="genesis_v2_run21_grid.db", game_id="573562833174",
        ge_db="genesis_v2_run21_grid.db",
    ),
    "b12ff78f1c1d": dict(
        pod="BUFFER", agent_mean=3.72, family="threshold",
        source="db", db="genesis_v2_run21_grid.db", game_id="b12ff78f1c1d",
        ge_db="genesis_v2_run21_grid.db",
    ),
    "e52e8889517a": dict(
        pod="BELOW", agent_mean=3.68, family="threshold",
        source="db", db="genesis_v2_run21_menger.db", game_id="e52e8889517a",
        ge_db="genesis_v2_run21_menger.db",
    ),
    "bfd1bb7ced76": dict(
        pod="BELOW", agent_mean=3.68, family="threshold",
        source="db", db="genesis_v2_run21_menger.db", game_id="bfd1bb7ced76",
        ge_db="genesis_v2_run21_menger.db",
    ),
    "e1453dac5445": dict(
        pod="BELOW", agent_mean=3.66, family="threshold",
        source="db", db="genesis_v2_run21_menger.db", game_id="e1453dac5445",
        ge_db="genesis_v2_run21_menger.db",
    ),
    "1fea3357dca4": dict(
        pod="BELOW", agent_mean=3.50, family="threshold",
        source="db", db="genesis_v2_run21_menger.db", game_id="1fea3357dca4",
        ge_db="genesis_v2_run21_menger.db",
    ),
}


# ---------------------------------------------------------------------------
# Game + GE loading (anchor_drama conventions)
# ---------------------------------------------------------------------------

def load_game_from_json(path: Path) -> GameDefV2:
    if not path.exists():
        raise SystemExit(f"game JSON not found: {path}")
    return GameDefV2.from_dict(json.loads(path.read_text()))


def load_game_from_db(db_name: str, game_id: str) -> GameDefV2:
    db_path = ROOT / db_name
    if not db_path.exists():
        raise SystemExit(
            f"DB not found: {db_path} (ROOT={ROOT}, db_name={db_name})"
        )
    # contextlib.closing: sqlite3's own context manager only commits/rolls
    # back — it does NOT close. closing() guarantees the connection closes.
    with closing(sqlite3.connect(str(db_path))) as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT rule_representation FROM games WHERE game_id = ?",
            (game_id,),
        ).fetchone()
    if row is None:
        raise SystemExit(f"game {game_id} not found in {db_name}")
    return GameDefV2.from_dict(json.loads(row["rule_representation"]))


def load_spec(spec: dict) -> GameDefV2:
    if spec["source"] == "json":
        return load_game_from_json(spec["path"])
    return load_game_from_db(spec["db"], spec["game_id"])


def load_go_essence(spec: dict) -> float | None:
    """go_essence from the registered source DB scores table; None = '—'.

    Registered as present for every R21 anchor — a missing scores row is DB
    drift and fails loud rather than silently degrading the control column.
    """
    if spec["ge_db"] is None:
        return None
    db_path = ROOT / spec["ge_db"]
    if not db_path.exists():
        raise SystemExit(f"GE source DB not found: {db_path}")
    with closing(sqlite3.connect(str(db_path))) as con:
        row = con.execute(
            "SELECT go_essence FROM scores WHERE game_id = ?",
            (spec["game_id"],),
        ).fetchone()
    if row is None or row[0] is None:
        raise SystemExit(
            f"go_essence missing from {spec['ge_db']} scores table for "
            f"{spec['game_id']} — registered as present (DB drift?)"
        )
    return float(row[0])


# ---------------------------------------------------------------------------
# Per-game probe: rollouts -> per-rollout descriptor values -> bootstraps
# ---------------------------------------------------------------------------

def probe_game(key: str, spec: dict, game: GameDefV2, n: int,
               base_seed: int) -> tuple[dict, list[dict]]:
    """Run the registered protocol on one game; per-rollout values + boots.

    Per-rollout values are assembled from metrics.descriptors' PUBLIC
    per-rollout functions (descriptors.py is locked; descriptor_row only
    exposes means). The means computed here are descriptor_row-identical by
    construction (same functions, same order) — asserted by cross_check().
    """
    topo = game.get_topology()
    axis_p1 = get_axis_for_player(game, 1)
    axis_p2 = get_axis_for_player(game, 2)

    rollouts = run_protocol(game, n, base_seed)

    drama_aligned: list[float | None] = []   # None for draws, rollout-aligned
    leads: list[int] = []
    inters: list[float] = []
    lengths: list[int] = []
    for r in rollouts:
        drama_aligned.append(obs_drama_for_rollout(game, topo, r))
        leads.append(obs_lead_changes_from_snapshots(
            topo, r["owner_snapshots"], axis_p1, axis_p2))
        inters.append(interaction_rate_for_rollout(topo, r))
        lengths.append(r["game_length"])

    dramas = [d for d in drama_aligned if d is not None]
    draws = sum(1 for d in drama_aligned if d is None)

    res = dict(
        key=key,
        pod=spec["pod"],
        agent_mean=spec["agent_mean"],
        family=spec["family"],
        n=n,
        n_used=len(dramas),
        draws=draws,
        obs_drama=float(np.mean(dramas)) if dramas else float("nan"),
        obs_lead_changes=float(np.mean(leads)) if leads else 0.0,
        interaction_rate=float(np.mean(inters)) if inters else 0.0,
        game_length=float(np.mean(lengths)) if lengths else 0.0,
        go_essence=load_go_essence(spec),
    )

    # Bootstrap resamples (deterministic: seeded by base seed + the game's
    # registered index, so identical regardless of --games selection/order).
    rng = np.random.default_rng([base_seed, list(GAME_SPECS).index(key)])

    # Column 1 (obs_drama): resample the n_used per-rollout drama values.
    if dramas:
        d_arr = np.asarray(dramas, dtype=float)
        idx = rng.integers(0, len(d_arr), size=(N_BOOT, len(d_arr)))
        res["boot_drama"] = d_arr[idx].mean(axis=1)
    else:
        res["boot_drama"] = np.full(N_BOOT, np.nan)

    # Column 3 (interaction_rate): resample the n per-rollout values.
    i_arr = np.asarray(inters, dtype=float)
    idx = rng.integers(0, len(i_arr), size=(N_BOOT, len(i_arr)))
    res["boot_inter"] = i_arr[idx].mean(axis=1)

    # Column 2 (blend) inputs: drama and lead resampled JOINTLY — one shared
    # rollout-index resample per replicate, so the drama/lead correlation
    # within rollouts is preserved. Draws contribute nan to the drama side
    # and are skipped via nanmean (an all-draw resample yields nan and is
    # dropped from the CI, counted in blend_nan_resamples).
    da_arr = np.asarray(
        [np.nan if d is None else d for d in drama_aligned], dtype=float)
    l_arr = np.asarray(leads, dtype=float)
    idx = rng.integers(0, len(rollouts), size=(N_BOOT, len(rollouts)))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # all-nan slices
        res["boot_joint_drama"] = np.nanmean(da_arr[idx], axis=1)
    res["boot_joint_lead"] = l_arr[idx].mean(axis=1)

    return res, rollouts


def cross_check(key: str, game: GameDefV2, rollouts: list[dict],
                res: dict) -> None:
    """Assert run_probe's per-rollout aggregation == descriptor_row's means.

    Exact equality is expected: identical public functions, identical input
    order, identical float(np.mean(...)) aggregation.
    """
    row = descriptor_row(game, rollouts)

    def eq(a, b) -> bool:
        if isinstance(a, float) and isinstance(b, float) \
                and np.isnan(a) and np.isnan(b):
            return True
        return a == b

    checks = [
        ("obs_drama", res["obs_drama"], row["obs_drama"]),
        ("obs_drama_n", res["n_used"], row["obs_drama_n"]),
        ("draws", res["draws"], row["draws"]),
        ("obs_lead_changes", res["obs_lead_changes"], row["obs_lead_changes"]),
        ("interaction_rate", res["interaction_rate"], row["interaction_rate"]),
        ("game_length", res["game_length"], row["game_length"]),
    ]
    for name, mine, theirs in checks:
        assert eq(mine, theirs), (
            f"[{key}] cross-check FAILED on {name}: "
            f"run_probe={mine!r} vs descriptor_row={theirs!r}"
        )
    print(f"  [{key}] cross-check vs descriptor_row: PASSED "
          f"(exact equality on {', '.join(c[0] for c in checks)})",
          flush=True)


# ---------------------------------------------------------------------------
# Blend (candidate 2): min-max norms over the FULL anchor-set point estimates
# ---------------------------------------------------------------------------

def _norm_point(x: float, pool: list[float]) -> float:
    """Min-max norm of x against pool (pool includes x for point estimates).

    Degenerate-flat guard (documented): if max == min over the pool the norm
    is 0.5 for all games — a flat metric carries no ranking signal and 0.5
    keeps sqrt(norm*norm) finite and uninformative rather than 0/0.
    nan-aware: nan inputs propagate to nan.
    """
    if not np.isfinite(x):
        return float("nan")
    arr = np.asarray(pool, dtype=float)
    mn, mx = np.nanmin(arr), np.nanmax(arr)
    if not np.isfinite(mn) or not np.isfinite(mx):
        return float("nan")
    if mx == mn:
        return 0.5
    return (x - mn) / (mx - mn)


def compute_blend(results: dict[str, dict]) -> None:
    """Attach blend point estimates + bootstrap arrays to each result row.

    Point estimate: norms over ALL loaded games' point estimates (the "FULL
    anchor set" of the prereg — BUFFER included; norms feed ranking only).

    Bootstrap (documented choice): per resample, ONE game's jointly-resampled
    (drama, lead) pair is re-normalized against the OTHER games' FIXED point
    estimates (pool = other games' points + this game's resampled value).
    Re-normalizing one game against fixed others isolates THAT game's
    sampling noise; resampling all ten norm pools at once would mix every
    game's noise into every CI. Because the resampled value joins its own
    pool, norms stay in [0, 1] by construction (no clipping needed).
    """
    keys = list(results)
    drama_pts = {k: results[k]["obs_drama"] for k in keys}
    lead_pts = {k: results[k]["obs_lead_changes"] for k in keys}

    for k in keys:
        nd = _norm_point(drama_pts[k], list(drama_pts.values()))
        nl = _norm_point(lead_pts[k], list(lead_pts.values()))
        results[k]["blend"] = float(np.sqrt(nd * nl)) \
            if np.isfinite(nd) and np.isfinite(nl) else float("nan")

    for k in keys:
        others_d = np.asarray(
            [drama_pts[o] for o in keys if o != k], dtype=float)
        others_l = np.asarray(
            [lead_pts[o] for o in keys if o != k], dtype=float)
        bd = results[k]["boot_joint_drama"]
        bl = results[k]["boot_joint_lead"]
        boot = np.full(N_BOOT, np.nan)
        if others_d.size and not np.all(np.isnan(others_d)):
            od_mn, od_mx = np.nanmin(others_d), np.nanmax(others_d)
            ol_mn, ol_mx = np.nanmin(others_l), np.nanmax(others_l)
            mn_d, mx_d = np.minimum(od_mn, bd), np.maximum(od_mx, bd)
            mn_l, mx_l = np.minimum(ol_mn, bl), np.maximum(ol_mx, bl)
            with np.errstate(invalid="ignore", divide="ignore"):
                norm_d = np.where(mx_d == mn_d, 0.5,
                                  (bd - mn_d) / (mx_d - mn_d))
                norm_l = np.where(mx_l == mn_l, 0.5,
                                  (bl - mn_l) / (mx_l - mn_l))
                boot = np.sqrt(norm_d * norm_l)
        results[k]["boot_blend"] = boot
        results[k]["blend_nan_resamples"] = int(np.sum(~np.isfinite(boot)))


def ci_bounds(arr: np.ndarray | None) -> tuple[float, float]:
    """95% percentile CI over the finite bootstrap means; (nan, nan) if none."""
    if arr is None:
        return float("nan"), float("nan")
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return float("nan"), float("nan")
    return (float(np.percentile(valid, CI_LO)),
            float(np.percentile(valid, CI_HI)))


# ---------------------------------------------------------------------------
# Bars (prereg "Bars" section — evaluated on point estimates; CIs reported,
# fragility flagged, "not a gate")
# ---------------------------------------------------------------------------

def evaluate_column(points: dict[str, float | None],
                    boots: dict[str, np.ndarray] | None,
                    above: list[str], below: list[str]) -> list[dict]:
    """The four pre-registered bars for one candidate column.

    FRAGILE operationalization of the prereg's "95% CI overlaps the
    separation threshold" clause: a bar that passes by point estimate is
    flagged FRAGILE when its defining inequality fails in more than 2.5% of
    the bootstrap resamples (i.e. holds in < 97.5%). Flag only — not a gate.
    Resamples where any needed value is non-finite (all-draw drama) are
    dropped from the fraction. For blend the per-game resamples are each
    renormalized against fixed others (see compute_blend), so the joint
    fraction is an approximation — acceptable for a non-gating flag.
    """
    def ok_val(k: str) -> bool:
        v = points.get(k)
        return v is not None and np.isfinite(v)

    def frac(needed: list[str], cond) -> float | None:
        if boots is None:
            return None
        mat = np.vstack([boots[k] for k in needed])
        valid = np.all(np.isfinite(mat), axis=0)
        if not valid.any():
            return None
        sub = {k: boots[k][valid] for k in needed}
        return float(np.mean(cond(sub)))

    bars: list[dict] = []

    # Bar 1: mean(ABOVE) > mean(BELOW).
    needed = above + below
    if all(ok_val(k) for k in needed):
        am = float(np.mean([points[k] for k in above]))
        bm = float(np.mean([points[k] for k in below]))
        ok = am > bm
        detail = f"mean(ABOVE)={am:.4f} vs mean(BELOW)={bm:.4f}"
        f = frac(needed, lambda s: (
            np.mean([s[k] for k in above], axis=0)
            > np.mean([s[k] for k in below], axis=0))) if ok else None
    else:
        ok, detail, f = False, "not evaluable (missing column values)", None
    bars.append(dict(name=BAR_TEXTS[0], ok=ok, detail=detail, frac=f))

    # Bar 2: count of BELOW games above min(ABOVE) <= 1.
    if all(ok_val(k) for k in needed):
        min_above = min(points[k] for k in above)
        inv = sum(1 for k in below if points[k] > min_above)
        ok = inv <= 1
        detail = f"inversions={inv} (min ABOVE={min_above:.4f})"

        def cond2(s, above=above, below=below):
            mn = np.min(np.vstack([s[k] for k in above]), axis=0)
            inv_b = np.sum(np.vstack([s[k] > mn for k in below]), axis=0)
            return inv_b <= 1

        f = frac(needed, cond2) if ok else None
    else:
        ok, detail, f = False, "not evaluable (missing column values)", None
    bars.append(dict(name=BAR_TEXTS[1], ok=ok, detail=detail, frac=f))

    # Bar 3: e1453dac5445 does not score above ANY ABOVE-pod game.
    needed3 = above + [GE_TOP]
    if all(ok_val(k) for k in needed3):
        min_above = min(points[k] for k in above)
        ok = points[GE_TOP] <= min_above
        detail = (f"{GE_TOP}={points[GE_TOP]:.4f} vs "
                  f"min(ABOVE)={min_above:.4f}")

        def cond3(s, above=above):
            mn = np.min(np.vstack([s[k] for k in above]), axis=0)
            return s[GE_TOP] <= mn

        f = frac(needed3, cond3) if ok else None
    else:
        ok, detail, f = False, "not evaluable (missing column values)", None
    bars.append(dict(name=BAR_TEXTS[2], ok=ok, detail=detail, frac=f))

    # Bar 4 (secondary, binding): signal(573562833174) > signal(e1453dac5445).
    needed4 = [GE_BOTTOM, GE_TOP]
    if all(ok_val(k) for k in needed4):
        ok = points[GE_BOTTOM] > points[GE_TOP]
        detail = (f"{GE_BOTTOM}={points[GE_BOTTOM]:.4f} vs "
                  f"{GE_TOP}={points[GE_TOP]:.4f}")
        f = frac(needed4, lambda s: s[GE_BOTTOM] > s[GE_TOP]) if ok else None
    else:
        ok, detail, f = False, "not evaluable (missing column values)", None
    bars.append(dict(name=BAR_TEXTS[3], ok=ok, detail=detail, frac=f))

    for b in bars:
        b["fragile"] = (b["ok"] and b["frac"] is not None
                        and b["frac"] < 0.975)
    return bars


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def fmt(v) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    return f"{v:.4f}"


def fmt_ci(v, lo, hi) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    return f"{v:.4f} [{fmt(lo)}, {fmt(hi)}]"


def fragile_str(bar: dict) -> str:
    if not bar["ok"] or bar["frac"] is None:
        return "—"
    if bar["fragile"]:
        return f"FRAGILE (holds in {100 * bar['frac']:.1f}% of resamples)"
    return f"no ({100 * bar['frac']:.1f}%)"


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="RC2 anchor probe — pre-registered descriptor "
                    "separation test (PREREGISTRATION.md).")
    parser.add_argument("--n", type=int, default=200,
                        help="Rollouts per game (n/2 random-pair + n/2 "
                             "greedy-pair). Default: 200.")
    parser.add_argument("--seed", type=int, default=11,
                        help="Base seed (anchor_drama scheme). Default: 11.")
    parser.add_argument("--games", type=str, default="all",
                        help="'all' or comma-separated game keys "
                             "(subset = PROBE_INCOMPLETE, no files).")
    parser.add_argument("--out", type=str, default="experiments/rc2_anchor",
                        help="Output directory for probe_results.md/.csv "
                             "(full runs only).")
    args = parser.parse_args()

    if args.games.strip() == "all":
        requested = list(GAME_SPECS)
    else:
        requested = [k.strip() for k in args.games.split(",") if k.strip()]
    unknown = [k for k in requested if k not in GAME_SPECS]
    if unknown:
        print(f"ERROR: unknown game keys: {unknown}. "
              f"Valid: {list(GAME_SPECS)}", file=sys.stderr)
        sys.exit(1)
    requested_set = set(requested)
    subset_run = requested_set != set(GAME_SPECS)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    print(f"rc2 anchor probe: n={args.n}, seed={args.seed}, "
          f"games={'all' if not subset_run else requested}")
    print(f"Full run (all {len(GAME_SPECS)} anchors): {not subset_run}")
    print()

    # ------------------------------------------------------------------
    # Load + probe each game (registered order). d4015a646ae3 carries the
    # prereg's registered loadability fallback: if it alone is unloadable
    # the probe runs without it, ABOVE = s_flip_r2 + a1_field_connect, and
    # a verdict IS permitted. Any other load failure stays loud + fatal.
    # ------------------------------------------------------------------
    results: dict[str, dict] = {}
    d4015_fallback = False
    checked = False
    for key in (k for k in GAME_SPECS if k in requested_set):
        spec = GAME_SPECS[key]
        try:
            game = load_spec(spec)
        except SystemExit as exc:
            if key == "d4015a646ae3":
                d4015_fallback = True
                print(f"WARNING: d4015a646ae3 unloadable ({exc}) — "
                      f"registered fallback: probe runs without it, "
                      f"ABOVE pod = s_flip_r2 + a1_field_connect, "
                      f"verdict permitted (PREREGISTRATION.md).", flush=True)
                continue
            raise
        # Family-drift guard (anchor_drama pattern): descriptor dispatch
        # keys off the registered family; loud failure beats silent drift.
        actual = game.win_condition.condition_type
        if actual != spec["family"]:
            raise SystemExit(
                f"[{key}] family mismatch: expected '{spec['family']}', "
                f"loaded condition_type '{actual}' — DB drift or wrong "
                f"game_id?"
            )
        print(f"  [{key}] pod={spec['pod']} family={spec['family']} — "
              f"{args.n} rollouts ...", flush=True)
        res, rollouts = probe_game(key, spec, game, args.n, args.seed)
        if not checked:
            # Locked-module cross-check on the first game processed.
            cross_check(key, game, rollouts, res)
            checked = True
        results[key] = res
        print(f"         n_used={res['n_used']} draws={res['draws']} "
              f"obs_drama={fmt(res['obs_drama'])} "
              f"lead={fmt(res['obs_lead_changes'])} "
              f"interaction={fmt(res['interaction_rate'])} "
              f"ge={fmt(res['go_essence'])}", flush=True)

    if not results:
        print("FATAL: no game produced results", file=sys.stderr)
        sys.exit(1)

    compute_blend(results)

    # Per-game CIs.
    for res in results.values():
        res["obs_drama_lo"], res["obs_drama_hi"] = ci_bounds(res["boot_drama"])
        res["blend_lo"], res["blend_hi"] = ci_bounds(res["boot_blend"])
        res["interaction_rate_lo"], res["interaction_rate_hi"] = \
            ci_bounds(res["boot_inter"])

    # ------------------------------------------------------------------
    # Per-game table
    # ------------------------------------------------------------------
    header = (f"{'game':<18} {'pod':<7} {'family':<17} {'n_used':<7} "
              f"{'draws':<6} {'obs_drama':<26} {'blend':<26} "
              f"{'interaction_rate':<26} {'go_essence':<10}")
    table_lines = [header, "-" * len(header)]
    for res in results.values():
        table_lines.append(
            f"{res['key']:<18} {res['pod']:<7} {res['family']:<17} "
            f"{res['n_used']:<7} {res['draws']:<6} "
            f"{fmt_ci(res['obs_drama'], res['obs_drama_lo'], res['obs_drama_hi']):<26} "
            f"{fmt_ci(res['blend'], res['blend_lo'], res['blend_hi']):<26} "
            f"{fmt_ci(res['interaction_rate'], res['interaction_rate_lo'], res['interaction_rate_hi']):<26} "
            f"{fmt(res['go_essence']):<10}")
    table_str = "\n".join(table_lines)
    print()
    print(table_str)
    print()

    # ------------------------------------------------------------------
    # Subset runs: partial table reported, NO verdict token, no files.
    # ------------------------------------------------------------------
    if subset_run:
        print("PROBE_INCOMPLETE (subset — no verdict)")
        print()
        print("Prereg clause: \"Probe run on a subset of anchor games (any "
              "--games filter, or d4015a646ae3 unloadable at runtime) -> "
              "PROBE_INCOMPLETE: partial table reported, NO verdict token "
              "emitted; the grammar above applies only when every loadable "
              "registered anchor game is present.\"")
        print("NOTE: blend norms above span only the games in this run.")
        return

    # ------------------------------------------------------------------
    # Bars per candidate column (BUFFER excluded; point estimates).
    # ------------------------------------------------------------------
    loaded = list(results)
    above = [k for k in ABOVE_KEYS if k in loaded]
    below = [k for k in BELOW_KEYS if k in loaded]

    column_points = {
        "obs_drama": {k: results[k]["obs_drama"] for k in loaded},
        "blend": {k: results[k]["blend"] for k in loaded},
        "interaction_rate": {k: results[k]["interaction_rate"]
                             for k in loaded},
        "go_essence": {k: results[k]["go_essence"] for k in loaded},
    }
    column_boots = {
        "obs_drama": {k: results[k]["boot_drama"] for k in loaded},
        "blend": {k: results[k]["boot_blend"] for k in loaded},
        "interaction_rate": {k: results[k]["boot_inter"] for k in loaded},
        "go_essence": None,  # DB point values; no sampling distribution
    }

    bars_by_col: dict[str, list[dict]] = {}
    col_pass: dict[str, bool] = {}
    for col in CANDIDATES:
        bars = evaluate_column(column_points[col], column_boots[col],
                               above, below)
        bars_by_col[col] = bars
        col_pass[col] = all(b["ok"] for b in bars)
        print(f"Candidate column: {col} "
              f"({'PASS' if col_pass[col] else 'FAIL'})")
        for b in bars:
            print(f"  {b['name']}: {b['detail']} -> "
                  f"{'YES' if b['ok'] else 'no'}"
                  f"{' [' + fragile_str(b) + ']' if b['ok'] and b['frac'] is not None else ''}")
        print()

    # ------------------------------------------------------------------
    # Verdict (prereg "Decision grammar (locked)")
    # ------------------------------------------------------------------
    if col_pass["obs_drama"] or col_pass["blend"]:
        verdict = "PHASE_C_GO"
        note = ("Candidate 1 (obs_drama) or 2 (blend) PASS -> register the "
                "archive-integration probe; obs_drama or blend is the "
                "primary archive-axis descriptor.")
    elif col_pass["interaction_rate"]:
        verdict = "PHASE_C_GO_INTERACTION"
        note = ("Only candidate 3 (interaction_rate) PASS -> "
                "interaction_rate primary; obs_drama demoted to "
                "archive-axis-only.")
    else:
        verdict = "RC2_KILL"
        note = ("None of candidates 1, 2, 3 PASS -> descriptor redesign; "
                "Frontline becomes the sole active registered thread.")
    flags = ["GE_CONTROL_PASSED"] if col_pass["go_essence"] else []

    print(f"VERDICT: {verdict}"
          + (f" + {' + '.join(flags)}" if flags else ""))
    print(note)
    if d4015_fallback:
        print("(registered fallback active: d4015a646ae3 unloadable; "
              "ABOVE = s_flip_r2 + a1_field_connect)")

    # ------------------------------------------------------------------
    # probe_results.md + probe_results.csv (full runs only)
    # ------------------------------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)

    md = [
        "# RC2 anchor probe — results",
        "",
        f"n={args.n} rollouts/game (n/2 random-pair + n/2 greedy-pair, "
        f"anchor_drama seeding), base_seed={args.seed}, "
        f"games={'all ' + str(len(results)) + ' anchors' if not subset_run else requested}.",
        "Protocol + bars per experiments/rc2_anchor/PREREGISTRATION.md "
        "(locked): observer defaults r=2/strength=1.0/decay=0.5; "
        "threshold-family progress traces at the game's own propagation "
        "params (registered dual parameterization; observer measures "
        "current-stone influence — ghost-influence divergence documented "
        "in the prereg). Draws skipped from obs_drama and counted. "
        f"Bootstrap: {N_BOOT} resamples, 95% percentile CIs.",
        "",
    ]
    if d4015_fallback:
        md += ["**Registered fallback active: d4015a646ae3 unloadable at "
               "probe time — probe ran without it; ABOVE pod = s_flip_r2 + "
               "a1_field_connect; verdict permitted.**", ""]
    md += [
        "## Per-game table",
        "",
        "| game | pod | family | n_used | draws | obs_drama [95% CI] | "
        "blend [95% CI] | interaction_rate [95% CI] | go_essence |",
        "|---|---|---|---:|---:|---|---|---|---:|",
    ]
    for res in results.values():
        md.append(
            f"| {res['key']} | {res['pod']} | {res['family']} "
            f"| {res['n_used']} | {res['draws']} "
            f"| {fmt_ci(res['obs_drama'], res['obs_drama_lo'], res['obs_drama_hi'])} "
            f"| {fmt_ci(res['blend'], res['blend_lo'], res['blend_hi'])} "
            f"| {fmt_ci(res['interaction_rate'], res['interaction_rate_lo'], res['interaction_rate_hi'])} "
            f"| {fmt(res['go_essence'])} |")
    md += [
        "",
        "BUFFER games (d995cf010504, 573562833174, b12ff78f1c1d) are "
        "reported above but excluded from the binary separation bars "
        "(prereg pod rule). 573562833174 enters only via the binding "
        "secondary check.",
        "",
        "## Bars per candidate column (point estimates; "
        "PASS iff ALL four hold)",
        "",
    ]
    for col in CANDIDATES:
        md += [f"### {col} — {'PASS' if col_pass[col] else 'FAIL'}", "",
               "| bar | detail | pass | fragile |",
               "|---|---|:---:|---|"]
        for b in bars_by_col[col]:
            md.append(f"| {b['name']} | {b['detail']} "
                      f"| {'YES' if b['ok'] else 'no'} "
                      f"| {fragile_str(b)} |")
        md.append("")
        if col == "go_essence" and not any(
                b["ok"] for b in bars_by_col[col][:3]):
            md += ["GE control note: bars 1–3 are not evaluable — the "
                   "prereg registers go_essence for the R21 games only "
                   "('—' for all three ABOVE-pod games), so the "
                   "expected-FAIL control column cannot pass them. "
                   "(genesis_v2_run8.db does hold a run8-era go_essence "
                   "for d4015a646ae3, 0.3858, but the registered column "
                   "definition excludes it: R8-era GE is not comparable "
                   "to R21 GE.)", ""]
    md += [
        "## Verdict",
        "",
        "```",
        verdict + (f" + {' + '.join(flags)}" if flags else ""),
        "```",
        "",
        note,
        "",
        "## Notes",
        "",
        "- blend = sqrt(norm(obs_drama) x norm(obs_lead_changes)); min-max "
        "norms over the full anchor-set point estimates (degenerate-flat "
        "guard: max==min -> norm 0.5 for all). Blend CIs: drama/lead "
        "resampled jointly per game, re-normalized per resample against "
        "the OTHER games' fixed point estimates (isolates that game's "
        "sampling noise).",
        "- FRAGILE flag (not a gate): bar passes by point estimate but its "
        "defining inequality fails in > 2.5% of bootstrap resamples — the "
        "operationalization of the prereg's CI-overlap clause.",
        "- go_essence read from each R21 game's source DB scores table "
        "(the registered column source). Informational GE values quoted "
        "in the prereg pod tables came from the R21 report and differ "
        "slightly for some games; the bar outcomes are identical under "
        "either set.",
        "- metrics/descriptors.py and metrics/rollout_traces.py are locked; "
        "per-rollout values were assembled from their public functions and "
        "cross-checked against descriptor_row (exact-equality assert) on "
        "the first game processed.",
    ]
    md_path = out_dir / "probe_results.md"
    md_path.write_text("\n".join(md) + "\n")

    csv_path = out_dir / "probe_results.csv"
    fieldnames = ["key", "pod", "family", "agent_mean", "n", "n_used",
                  "draws", "obs_drama", "obs_drama_lo", "obs_drama_hi",
                  "blend", "blend_lo", "blend_hi", "interaction_rate",
                  "interaction_rate_lo", "interaction_rate_hi",
                  "go_essence"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for res in results.values():
            w.writerow({k: ("" if res.get(k) is None else res[k])
                        for k in fieldnames})

    print(f"\nWrote {md_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
