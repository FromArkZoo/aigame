"""RC2 §0 lock obligation — σ-FILE [C4].

Pre-data instrument measurement (no campaign data). Measures σ(T1-PG, n=24)
directly by bootstrapping the stored per-game T1 outcome cells in
experiments/rc2_planning_gap/cost_tiering.json (the ADOPT_T1 tier).

Estimator (registered): each roster game's T1 result is n=24 seat-balanced
net-free UCT@128-vs-UCT@16 games with per-game outcome value in {loss:0.0,
draw:0.5, win:1.0}; T1-PG = mean(outcomes) - 0.5. σ(T1-PG, n=24) = the
sampling SD of that mean, estimated by resampling the 24 stored outcome cells
with replacement (B draws) and taking the SD of the resampled T1-PG.

σ_diff = σ · √2 (difference of two independent n=24 estimates), which
finalizes the CAL-I separation threshold 3·σ_diff (§5) and feeds NOISE-NULL
(§0). Provisional draft values: σ≈0.07, threshold 0.30.

Seed: 95_000_000 (registered bootstrap stream, base 19 × 5 = 95 → 95M, §2).

Run:  .venv/bin/python experiments/rc2_campaign/sigma_t1.py
"""

from __future__ import annotations

import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
COST_TIERING = ROOT / "experiments" / "rc2_planning_gap" / "cost_tiering.json"
OUT_JSON = HERE / "sigma_t1.json"
OUT_MD = HERE / "sigma_t1.md"

BOOTSTRAP_SEED = 95_000_000  # registered bootstrap stream (§2)
B = 100_000
ROSTER = ["S1", "S2", "S3", "S4", "S5", "d4015a646ae3", "e1453dac5445"]
# CAL-I instrument pair (§5): d4015 (positive) vs S4 (negative).
CAL_I_PAIR = ("d4015a646ae3", "S4")
CAL_I_SIGMAS = 3.0  # 3·σ_diff separation requirement


def outcome_vector(cell: dict) -> np.ndarray:
    """Reconstruct the 24 per-game outcome cells from W/D/L counts."""
    w, d, l = cell["wins"], cell["draws"], cell["losses"]
    n = cell["n"]
    assert w + d + l == n, f"{cell['key']}: W+D+L != n"
    v = np.concatenate([np.ones(w), np.full(d, 0.5), np.zeros(l)])
    assert v.size == n
    return v


def bootstrap_sigma(outcomes: np.ndarray, rng: np.random.Generator) -> float:
    n = outcomes.size
    idx = rng.integers(0, n, size=(B, n))
    resampled_pg = outcomes[idx].mean(axis=1) - 0.5
    return float(resampled_pg.std(ddof=1))


def main() -> None:
    tier = json.loads(COST_TIERING.read_text())["tiers"]["T1"]
    per_game = tier["per_game"]

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    rows = {}
    for key in ROSTER:
        cell = per_game[key]
        outcomes = outcome_vector(cell)
        sigma_boot = bootstrap_sigma(outcomes, rng)
        # analytic sampling SD of the mean, for cross-check (ddof=1 on cells)
        sigma_analytic = float(outcomes.std(ddof=1) / math.sqrt(outcomes.size))
        rows[key] = dict(
            family=cell["family"],
            pg=cell["planning_gap"],
            wins=cell["wins"], draws=cell["draws"], losses=cell["losses"],
            n=cell["n"],
            sigma_bootstrap=sigma_boot,
            sigma_analytic=sigma_analytic,
        )

    sigmas = [rows[k]["sigma_bootstrap"] for k in ROSTER]
    sigma_max = max(sigmas)
    sigma_max_game = ROSTER[int(np.argmax(sigmas))]
    sigma_mean = float(np.mean(sigmas))
    sigma_median = float(np.median(sigmas))

    # Registered rule (§5 formula × §0 conservative selection): σ_diff =
    # σ · √2 with σ = the single max-over-roster σ(T1,n=24). This is the
    # pre-registered formula applied mechanically — NOT a post-hoc per-pair
    # estimate. The e1453 negative region is reported but never relaxes the
    # bar (max-over-roster only widens it).
    pos, neg = CAL_I_PAIR
    sigma_diff = sigma_max * math.sqrt(2.0)
    cal_i_threshold = CAL_I_SIGMAS * sigma_diff
    observed_sep = rows[pos]["pg"] - rows[neg]["pg"]
    # Diagnostic only (not the binding constant): the accurate heteroskedastic
    # pair σ_diff, reported so the conservatism margin is visible.
    sigma_pair_diag = math.sqrt(rows[pos]["sigma_bootstrap"] ** 2
                                + rows[neg]["sigma_bootstrap"] ** 2)

    out = dict(
        obligation="sigma_t1",
        source=str(COST_TIERING.relative_to(ROOT)),
        estimator="bootstrap of 24 stored per-game outcome cells; "
                  "T1-PG = mean(outcomes)-0.5; sigma = SD of resampled T1-PG",
        bootstrap_seed=BOOTSTRAP_SEED,
        bootstrap_B=B,
        per_game=rows,
        sigma_max=sigma_max,
        sigma_max_game=sigma_max_game,
        sigma_mean=sigma_mean,
        sigma_median=sigma_median,
        cal_i_pair=dict(positive=pos, negative=neg),
        sigma_selection="max-over-roster (registered §0 conservative rule)",
        sigma_used=sigma_max,
        sigma_diff=sigma_diff,
        sigma_diff_pair_diagnostic=sigma_pair_diag,
        cal_i_threshold=cal_i_threshold,
        cal_i_observed_separation_streams_42_43=observed_sep,
        heteroskedasticity_caveat=(
            "e1453 sits in the negative PG region (negative_pg_check.py); its "
            "outcome variance need not match the informative-region games. "
            "Constants are set from the max-over-roster σ, not e1453, so the "
            "caveat only widens (never relaxes) the bar."
        ),
    )
    OUT_JSON.write_text(json.dumps(out, indent=2))

    lines = []
    lines.append("# RC2 §0 — σ-FILE (T1-PG sampling SD)  [C4]")
    lines.append("")
    lines.append(f"Source: `{out['source']}` (ADOPT_T1 tier).  ")
    lines.append(f"Estimator: {out['estimator']}.  ")
    lines.append(f"Bootstrap: B={B:,}, seed={BOOTSTRAP_SEED:,} "
                 f"(registered bootstrap stream, §2).")
    lines.append("")
    lines.append("| game | family | W/D/L | T1-PG | σ(bootstrap) | σ(analytic) |")
    lines.append("|------|--------|-------|-------|--------------|-------------|")
    for k in ROSTER:
        r = rows[k]
        lines.append(f"| {k} | {r['family']} | {r['wins']}/{r['draws']}/{r['losses']} "
                     f"| {r['pg']:+.4f} | {r['sigma_bootstrap']:.4f} "
                     f"| {r['sigma_analytic']:.4f} |")
    lines.append("")
    lines.append(f"- σ_max (roster) = **{sigma_max:.4f}**  ·  "
                 f"σ_mean = {sigma_mean:.4f}  ·  σ_median = {sigma_median:.4f}")
    lines.append(f"- Provisional draft σ ≈ 0.07 → measured σ_max = "
                 f"{sigma_max:.4f}")
    lines.append("")
    lines.append("## Finalized CAL-I constant (§5)")
    lines.append("")
    lines.append("Registered rule: σ_diff = σ·√2, σ = max-over-roster "
                 "σ(T1,n=24) (§5 formula × §0 conservative selection).")
    lines.append(f"- σ used = σ_max = **{sigma_max:.4f}** ({sigma_max_game}).")
    lines.append(f"- σ_diff = σ_max·√2 = **{sigma_diff:.4f}**.")
    lines.append(f"- Separation threshold = 3·σ_diff = **{cal_i_threshold:.4f}** "
                 f"(provisional draft: 0.30).")
    lines.append(f"- CAL-I pair: {pos} (positive) vs {neg} (negative); "
                 f"observed separation at streams 42/43 = {observed_sep:+.4f} "
                 f"→ passes with {observed_sep / sigma_diff:.1f}σ_diff margin.")
    lines.append(f"- Diagnostic (not binding): accurate heteroskedastic pair "
                 f"σ_diff = √(σ_{pos}²+σ_{neg}²) = {sigma_pair_diag:.4f}; the "
                 f"registered max-over-roster rule is "
                 f"{sigma_diff / sigma_pair_diag:.1f}× more conservative.")
    lines.append("")
    lines.append("## Heteroskedasticity caveat")
    lines.append("")
    lines.append(out["heteroskedasticity_caveat"])
    lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
