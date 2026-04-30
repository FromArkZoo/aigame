"""Phase A — mine existing R18 DBs for free volatility data.

For every game with >=3 training_runs rows we recompute strategic_depth from
each persisted learning_curve and pull trained_vs_random + avg_game_length
distributions. Outputs:
  - per-substrate CSV of (game_id, n_runs, tvr_mean, tvr_std, depth_mean,
    depth_std, partial_ge_mean, partial_ge_std)
  - top-N-per-substrate box-plot of (depth, tvr, partial_ge)
  - markdown summary with noise-floor numbers

Partial GE here uses (rule_simplicity, depth, tvr-competence). It does NOT
include p1_winrate balance, cross_play diversity, seat balance, or the
length/timeout/seat-balance penalties — those inputs are not persisted in
training_runs. Use this as a partial-volatility proxy, not as a full GE
re-derivation.
"""

from __future__ import annotations

import json
import math
import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/Users/jamesbrowne/aigame")
sys.path.insert(0, str(ROOT))

from metrics.scoring import (
    _compute_auc,
    _estimate_plateau_fraction,
)

OUT = ROOT / "experiments" / "r18_volatility"
OUT.mkdir(parents=True, exist_ok=True)
PLOTS = OUT / "plots"
PLOTS.mkdir(exist_ok=True)

SUBSTRATES = [
    ("vicsek",   1.465, "genesis_v2_run18_vicsek.db"),
    ("triangle", 1.585, "genesis_v2_run18_triangle.db"),
    ("carpet",   1.893, "genesis_v2_run18_carpet.db"),
    ("grid",     2.000, "genesis_v2_run18_grid.db"),
    ("menger",   2.727, "genesis_v2_run18_menger.db"),
]


def strategic_depth_from_curve(learning_curve: list[tuple[int, float]]) -> float:
    """Reproduces metrics.scoring.GoEssenceScorer.strategic_depth.

    Inlined here so we don't need to instantiate a config for thousands of
    re-derivations. Identical math to the engine code.
    """
    if not learning_curve or len(learning_curve) < 2:
        return 0.0
    ep = np.array([p[0] for p in learning_curve], dtype=np.float64)
    wr = np.array([p[1] for p in learning_curve], dtype=np.float64)
    bad = ~np.isfinite(wr)
    if np.any(bad):
        wr[bad] = 0.0
    bad_e = ~np.isfinite(ep)
    if np.any(bad_e):
        ep[bad_e] = 0.0
    idx = np.argsort(ep)
    ep, wr = ep[idx], idx[idx]  # placeholder — will fix below
    # (the above line is wrong — fix to use idx for both)
    ep = np.sort(ep)
    wr = np.array([p[1] for p in learning_curve], dtype=np.float64)[np.argsort(np.array([p[0] for p in learning_curve]))]
    wr = np.clip(wr, 0.0, 1.0)
    auc = _compute_auc(ep, wr)
    plateau = _estimate_plateau_fraction(ep, wr)
    mid = len(wr) // 2
    if mid > 0:
        first = float(np.mean(wr[:mid]))
        second = float(np.mean(wr[mid:]))
        late = max(0.0, second - first)
        late = min(late / 0.5, 1.0)
    else:
        late = 0.0
    depth = (auc + plateau + late) / 3.0
    return float(np.clip(depth, 0.0, 1.0))


def rule_simplicity_from_complexity(rule_complexity: int) -> float:
    """Reproduces metrics.scoring.GoEssenceScorer.rule_simplicity."""
    n = max(rule_complexity, 1)
    return float(np.clip(1.0 / (1.0 + math.log(n)), 0.0, 1.0))


def competence_factor(tvr: float) -> float:
    """The non_triviality 'competence' subterm — reproduces scoring.py."""
    tvr = float(np.clip(tvr, 0.0, 1.0))
    edge = max(0.0, tvr - 0.5) * 2.0
    return float(edge ** 0.5)


def partial_ge(simplicity: float, depth: float, tvr: float) -> float:
    """Partial GE proxy.

    Real composite_score is:
        numerator = depth^w_d * (0.2 + 0.8*diversity)^w_div * (0.1 + 0.9*non_triv)
        denom = (1 - simplicity)^w_s + eps
        raw = numerator / denom
        score = raw / (raw + 1)

    Partial GE here pins diversity = 0.5 (neutral) and non_triv = competence
    (i.e. balance factor pinned at 1.0 — best-case). Useful as a relative
    ranking/volatility proxy, NOT a real GE re-derivation.
    """
    w_d, w_div, w_s = 1.0, 0.5, 1.0  # default weights from MetricsConfig
    eps = 1e-8
    diversity_factor = 0.2 + 0.8 * 0.5  # neutral diversity
    competence = competence_factor(tvr)
    non_triv_factor = 0.1 + 0.9 * competence  # balance pinned at 1.0
    num = (depth ** w_d) * (diversity_factor ** w_div) * non_triv_factor
    denom = (1.0 - simplicity) ** w_s + eps
    raw = num / denom
    return float(np.clip(raw / (raw + 1.0), 0.0, 1.0))


def collect_substrate(name: str, dim: float, db_path: Path) -> list[dict]:
    """For each game with N>=3 training_runs, build per-run records."""
    con = sqlite3.connect(db_path)
    rows = con.execute("""
        SELECT t.game_id, t.run_id, t.run_seed, t.learning_curve,
               t.trained_vs_random, t.avg_game_length,
               g.rule_complexity, g.generation, s.go_essence
        FROM training_runs t
        JOIN games g ON g.game_id = t.game_id
        LEFT JOIN scores s ON s.game_id = t.game_id
        WHERE t.game_id IN (
            SELECT game_id FROM training_runs
            GROUP BY game_id HAVING COUNT(*) >= 3
        )
        ORDER BY t.game_id, t.run_id
    """).fetchall()
    records = []
    for game_id, run_id, run_seed, lc_json, tvr, alen, complexity, gen, score in rows:
        try:
            curve = json.loads(lc_json)
        except (TypeError, json.JSONDecodeError):
            continue
        if not curve:
            continue
        # Sort and clean curve data
        curve_sorted = sorted(curve, key=lambda p: p[0])
        episodes = np.array([p[0] for p in curve_sorted], dtype=np.float64)
        winrates = np.array([p[1] for p in curve_sorted], dtype=np.float64)
        winrates = np.clip(winrates, 0.0, 1.0)
        # Inline depth (avoid the buggy helper above)
        if len(episodes) < 2:
            depth = 0.0
        else:
            auc = _compute_auc(episodes, winrates)
            plat = _estimate_plateau_fraction(episodes, winrates)
            mid = len(winrates) // 2
            if mid > 0:
                first = float(np.mean(winrates[:mid]))
                second = float(np.mean(winrates[mid:]))
                late = max(0.0, second - first)
                late = min(late / 0.5, 1.0)
            else:
                late = 0.0
            depth = float(np.clip((auc + plat + late) / 3.0, 0.0, 1.0))
        simp = rule_simplicity_from_complexity(complexity or 1)
        tvr_v = float(tvr) if tvr is not None and math.isfinite(tvr) else 0.0
        pg = partial_ge(simp, depth, tvr_v)
        records.append({
            "substrate": name,
            "dim": dim,
            "game_id": game_id,
            "run_id": run_id,
            "run_seed": run_seed,
            "generation": gen,
            "tvr": tvr_v,
            "avg_game_length": float(alen) if alen is not None else 0.0,
            "rule_simplicity": simp,
            "depth": depth,
            "partial_ge": pg,
            "stored_ge": float(score) if score is not None else 0.0,
        })
    con.close()
    return records


def aggregate_per_game(records: list[dict]) -> list[dict]:
    by_game: dict[str, list[dict]] = {}
    for r in records:
        by_game.setdefault(r["game_id"], []).append(r)
    out = []
    for gid, runs in by_game.items():
        tvr = np.array([r["tvr"] for r in runs])
        depth = np.array([r["depth"] for r in runs])
        pge = np.array([r["partial_ge"] for r in runs])
        alen = np.array([r["avg_game_length"] for r in runs])
        out.append({
            "game_id": gid,
            "substrate": runs[0]["substrate"],
            "dim": runs[0]["dim"],
            "n_runs": len(runs),
            "tvr_mean": float(tvr.mean()),
            "tvr_std": float(tvr.std()),
            "tvr_min": float(tvr.min()),
            "tvr_max": float(tvr.max()),
            "depth_mean": float(depth.mean()),
            "depth_std": float(depth.std()),
            "pge_mean": float(pge.mean()),
            "pge_std": float(pge.std()),
            "pge_min": float(pge.min()),
            "pge_max": float(pge.max()),
            "alen_mean": float(alen.mean()),
            "alen_std": float(alen.std()),
            "stored_ge": runs[0]["stored_ge"],
        })
    return out


def plot_per_substrate_distributions(per_game: list[dict], all_records: list[dict]):
    """Top-N games per substrate: box-plot of tvr / depth / partial_ge."""
    by_substrate: dict[str, list[dict]] = {}
    for g in per_game:
        by_substrate.setdefault(g["substrate"], []).append(g)
    for sub_name, sub_games in by_substrate.items():
        # Top games by stored_ge
        top = sorted(sub_games, key=lambda x: -x["stored_ge"])[:8]
        if not top:
            continue
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        for col, key, title, ylim in [
            (0, "tvr", "trained_vs_random", (-0.05, 1.05)),
            (1, "depth", "strategic_depth", (-0.05, 1.05)),
            (2, "partial_ge", "partial-GE proxy", (-0.05, 1.05)),
        ]:
            data = []
            labels = []
            for g in top:
                runs = [r for r in all_records if r["game_id"] == g["game_id"]]
                data.append([r[key] for r in runs])
                labels.append(f"{g['game_id'][:8]}\nGE={g['stored_ge']:.3f}\nn={g['n_runs']}")
            axes[col].boxplot(data, tick_labels=labels)
            axes[col].set_ylim(*ylim)
            axes[col].set_title(f"{sub_name} ({len(top)} top games) — {title}")
            axes[col].grid(True, alpha=0.3)
            axes[col].tick_params(axis='x', rotation=45, labelsize=7)
        plt.tight_layout()
        out = PLOTS / f"phase_a_{sub_name}.png"
        plt.savefig(out, dpi=110)
        plt.close(fig)
        print(f"  wrote {out}")


def plot_noise_summary(per_game: list[dict]):
    """One-shot summary plot — std of partial_ge per game, by substrate."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    by_sub: dict[str, list[float]] = {}
    for g in per_game:
        by_sub.setdefault(g["substrate"], []).append(g["pge_std"])
    names, values, dims = [], [], []
    sub_order = sorted(by_sub.keys(), key=lambda s: {
        "vicsek": 1.465, "triangle": 1.585, "carpet": 1.893,
        "grid": 2.000, "menger": 2.727,
    }[s])
    positions = []
    for i, sub in enumerate(sub_order):
        vals = by_sub[sub]
        positions.append(i + 1)
        names.append(f"{sub}\nn={len(vals)} games")
        values.append(vals)
    ax.boxplot(values, positions=positions, tick_labels=names, widths=0.6)
    ax.set_ylabel("std(partial-GE) per game across N persisted training runs")
    ax.set_title("R18 partial-GE volatility — per-substrate distribution of per-game std")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = PLOTS / "phase_a_noise_summary.png"
    plt.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    print("Phase A — mining R18 DBs for volatility data\n")
    all_records: list[dict] = []
    all_per_game: list[dict] = []
    summary_lines = []
    for name, dim, db_name in SUBSTRATES:
        path = ROOT / db_name
        recs = collect_substrate(name, dim, path)
        per_game = aggregate_per_game(recs)
        # sort by stored_ge desc
        per_game.sort(key=lambda x: -x["stored_ge"])
        print(f"=== {name} (dim {dim}) — {len(per_game)} games with >=3 runs ({len(recs)} runs) ===")
        line = f"## {name} (dim {dim})\n\n{len(per_game)} games with >=3 training runs ({len(recs)} runs total)\n\n"
        line += "| game_id | n | stored_GE | tvr mean±std (min..max) | depth mean±std | partial_GE mean±std |\n"
        line += "|---|---|---|---|---|---|\n"
        for g in per_game[:10]:
            line += (
                f"| {g['game_id'][:8]} | {g['n_runs']} | {g['stored_ge']:.4f} "
                f"| {g['tvr_mean']:.3f}±{g['tvr_std']:.3f} ({g['tvr_min']:.2f}..{g['tvr_max']:.2f}) "
                f"| {g['depth_mean']:.3f}±{g['depth_std']:.3f} "
                f"| {g['pge_mean']:.3f}±{g['pge_std']:.3f} ({g['pge_min']:.2f}..{g['pge_max']:.2f}) |\n"
            )
            print(
                f"  {g['game_id']} n={g['n_runs']:>2} GE_db={g['stored_ge']:.4f} "
                f"tvr={g['tvr_mean']:.3f}±{g['tvr_std']:.3f} "
                f"depth={g['depth_mean']:.3f}±{g['depth_std']:.3f} "
                f"pge={g['pge_mean']:.3f}±{g['pge_std']:.3f}"
            )
        # Substrate-level noise summary
        if per_game:
            stds = np.array([g["pge_std"] for g in per_game])
            line += (
                f"\n**Substrate-level partial-GE std**: median {np.median(stds):.4f}, "
                f"p90 {np.percentile(stds, 90):.4f}, max {stds.max():.4f}\n\n"
            )
            print(
                f"  -> partial-GE std median {np.median(stds):.4f}, "
                f"p90 {np.percentile(stds, 90):.4f}, max {stds.max():.4f}\n"
            )
        summary_lines.append(line)
        all_records.extend(recs)
        all_per_game.extend(per_game)
    # Plot
    print("Plots:")
    plot_per_substrate_distributions(all_per_game, all_records)
    plot_noise_summary(all_per_game)
    # CSV
    import csv
    csv_path = OUT / "phase_a_per_game.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_per_game[0].keys()))
        w.writeheader()
        w.writerows(all_per_game)
    print(f"\n  wrote {csv_path}")
    # Markdown summary
    md_path = OUT / "phase_a_results.md"
    overall_stds = np.array([g["pge_std"] for g in all_per_game if g["n_runs"] >= 3])
    overall_tvr_stds = np.array([g["tvr_std"] for g in all_per_game if g["n_runs"] >= 3])
    overall_depth_stds = np.array([g["depth_std"] for g in all_per_game if g["n_runs"] >= 3])
    md_path.write_text(
        "# Phase A — R18 partial-GE volatility from existing training_runs data\n\n"
        f"Source: 5 R18 DBs, {sum(g['n_runs'] for g in all_per_game)} training runs across "
        f"{len(all_per_game)} games (each with >=3 runs).\n\n"
        "## Headline noise floor\n\n"
        f"Across the {len(all_per_game)} games with >=3 persisted training runs:\n\n"
        f"- **tvr std**: median {np.median(overall_tvr_stds):.3f}, p90 {np.percentile(overall_tvr_stds, 90):.3f}, max {overall_tvr_stds.max():.3f}\n"
        f"- **depth std**: median {np.median(overall_depth_stds):.3f}, p90 {np.percentile(overall_depth_stds, 90):.3f}, max {overall_depth_stds.max():.3f}\n"
        f"- **partial-GE std**: median {np.median(overall_stds):.3f}, p90 {np.percentile(overall_stds, 90):.3f}, max {overall_stds.max():.3f}\n\n"
        "Partial GE pins balance and diversity at neutral; this is a LOWER BOUND on real-GE volatility "
        "(the unrecoverable balance and cross-play components add additional variance).\n\n"
        "Plots: `plots/phase_a_<substrate>.png` (top-8 games per substrate, tvr/depth/partial-GE box plots), "
        "`plots/phase_a_noise_summary.png` (per-substrate distribution of per-game partial-GE std).\n\n"
        + "\n".join(summary_lines)
    )
    print(f"  wrote {md_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
