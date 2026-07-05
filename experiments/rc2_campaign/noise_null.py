"""RC2 §0 lock obligation — NOISE-NULL [C4]: Monte-Carlo null floor for BAR W-PG.

Pre-data instrument measurement (no campaign data). BAR W-PG (§6) declares a
Stage-0 family LIVE iff its observed P90-P10 of floored T1-PG exceeds a
noise-only floor at that family's N. This script registers that floor.

Null model (registered, faithful to the T1-PG estimator of §3)
--------------------------------------------------------------
  A family is "noise-only" if every genome's TRUE T1-PG = 0 — any observed
  P90-P10 spread is pure n=24 sampling noise. Each null genome draws 24 i.i.d.
  game outcomes in {loss:0.0, draw:0.5, win:1.0} with P(win)=P(loss)=(1-d)/2,
  P(draw)=d, so E[outcome]=0.5 and true PG=0. Observed T1-PG = mean-0.5,
  floored at 0 (informative-region rule, §3). For N such genomes we take
  P90-P10 of the floored values; the floor = the 95th percentile of that
  statistic over many Monte-Carlo family draws.

  Draw rate d is calibrated so the per-genome T1-PG SD equals the null sigma:
  Var(outcome)=0.25(1-d) -> SD(mean over 24)=sqrt(0.25(1-d)/24). BINDING sigma
  = sigma_max from the sigma-FILE (max-over-roster, the same conservative
  selection used for CAL-I; higher sigma -> wider null -> higher floor ->
  harder to falsely certify a noise-only family as LIVE). A cross-check at the
  draft's registered reference sigma=0.087 must reproduce the registered
  reference point (approx 0.28 at N=20).

Output: noise_null.json + NOISE_NULL.md next to this file.
Run:    .venv/bin/python experiments/rc2_campaign/noise_null.py
"""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SIGMA_FILE = HERE / "sigma_t1.json"
OUT_JSON = HERE / "noise_null.json"
OUT_MD = HERE / "NOISE_NULL.md"

N_GAMES = 24              # T1 ledger n (§3)
MC_SEED = 95_000_000      # registered instrument stream (§2)
MC_REPS = 100_000
REFERENCE_SIGMA = 0.087   # draft registered reference (approx 0.28 at N=20)
GRID_N = [20, 24, 30, 40, 50, 75, 100, 150]
OUTCOMES = np.array([0.0, 0.5, 1.0])


def draw_rate_for_sigma(sigma: float) -> float:
    """d such that SD(T1-PG over N_GAMES) == sigma under the null (PG=0)."""
    d = 1.0 - (sigma ** 2) * N_GAMES / 0.25
    return float(min(1.0, max(0.0, d)))


def sample_family_floored_pg(n_family: int, d: float,
                             rng: np.random.Generator,
                             floored: bool = True) -> np.ndarray:
    """N genomes x 24 null games -> T1-PG per genome (floored iff floored)."""
    p_side = (1.0 - d) / 2.0
    probs = [p_side, d, p_side]
    draws = rng.choice(OUTCOMES, size=(n_family, N_GAMES), p=probs)
    pg = draws.mean(axis=1) - 0.5
    return np.maximum(pg, 0.0) if floored else pg


def p90_minus_p10(values: np.ndarray) -> float:
    return float(np.percentile(values, 90) - np.percentile(values, 10))


def noise_null_floor(n_family: int, sigma: float, reps: int,
                     rng: np.random.Generator, floored: bool = True) -> float:
    d = draw_rate_for_sigma(sigma)
    spreads = np.empty(reps)
    for i in range(reps):
        spreads[i] = p90_minus_p10(
            sample_family_floored_pg(n_family, d, rng, floored=floored))
    return float(np.percentile(spreads, 95))


def _load_sigma_max() -> float:
    return float(json.loads(SIGMA_FILE.read_text())["sigma_max"])


def main() -> None:
    sigma_max = _load_sigma_max()
    d_bind = draw_rate_for_sigma(sigma_max)

    # BINDING: floored T1-PG (matches §3/§6 "floored" wording) at sigma_max.
    rng = np.random.default_rng(MC_SEED)
    binding = {n: noise_null_floor(n, sigma_max, MC_REPS, rng, floored=True)
               for n in GRID_N}
    # Reconciliation of the draft's provisional reference (approx 0.28 @ N=20,
    # sigma=0.087): that number was computed on RAW (signed) T1-PG, not floored.
    rng_raw = np.random.default_rng(MC_SEED)
    raw_ref20 = noise_null_floor(20, REFERENCE_SIGMA, MC_REPS, rng_raw,
                                 floored=False)
    rng_fl = np.random.default_rng(MC_SEED)
    floored_ref20 = noise_null_floor(20, REFERENCE_SIGMA, MC_REPS, rng_fl,
                                     floored=True)
    raw_matches_draft = 0.24 <= raw_ref20 <= 0.32

    out = dict(
        obligation="noise_null",
        model="discrete T1-PG estimator (24 games in {0,0.5,1.0}), true PG=0, "
              "FLOORED (max(PG,0)); floor = 95th pct of P90-P10 over MC draws",
        n_games=N_GAMES, mc_reps=MC_REPS, mc_seed=MC_SEED,
        binding_sigma=sigma_max, binding_draw_rate=d_bind,
        floor_binding=binding,
        draft_reference_reconciliation=dict(
            note="draft §0 provisional 'approx 0.28 at N=20, sigma=0.087' was "
                 "computed on RAW T1-PG; §6's bar compares FLOORED T1-PG. The "
                 "internally-consistent (floored) floor is used as binding.",
            raw_floor_n20_sigma087=raw_ref20,
            floored_floor_n20_sigma087=floored_ref20,
            raw_reproduces_draft_0_28=raw_matches_draft,
        ),
    )
    OUT_JSON.write_text(json.dumps(out, indent=2))

    lines = [
        "# RC2 §0 — NOISE-NULL (BAR W-PG floor)  [C4]", "",
        "95th-percentile noise-only floor for P90-P10 of **floored** T1-PG, "
        "per family N. A Stage-0 family is LIVE (§6) iff its observed P90-P10 "
        "of floored T1-PG meets/exceeds the floor at its N.", "",
        f"- Model: {out['model']}.",
        f"- MC: reps={MC_REPS:,}, seed={MC_SEED:,} (registered instrument "
        f"stream, §2), n_games={N_GAMES}.",
        f"- **Binding sigma = sigma_max = {sigma_max:.4f}** (from sigma-FILE, "
        f"max-over-roster) -> draw-rate d={d_bind:.3f}.",
        "",
        "| N | floor (binding, floored, sigma_max) |",
        "|---:|---:|",
    ]
    for n in GRID_N:
        lines.append(f"| {n} | **{binding[n]:.4f}** |")
    lines += [
        "",
        "## Reconciliation with the draft's provisional reference",
        "",
        f"Draft §0 registered 'approx 0.28 at N=20, sigma=0.087'. That number "
        f"reproduces on **raw** (unfloored) T1-PG: raw floor = "
        f"{raw_ref20:.4f} ({'matches' if raw_matches_draft else 'does NOT match'}"
        f" approx 0.28). The **floored** floor at the same N/sigma is "
        f"{floored_ref20:.4f}. Because §3/§6 define the bar on FLOORED T1-PG, "
        f"the floored floor is binding and the draft's raw-based 0.28 is "
        f"superseded — the §0 reference text needs a one-line correction at "
        f"lock. Floored is also LESS conservative (lower floor), so BAR W is "
        f"easier to pass than the raw 0.28 would have made it (guards against "
        f"false ARCHIVE_KILL of a valid archive).",
        "",
        "The binding floor uses sigma_max (conservative across roster). The "
        "per-family floor is looked up at the family's actual N at Stage-0 "
        "close using this locked model/seed; intermediate N are linearly "
        "interpolated on this grid.", "",
        "COMPLETE", "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
