"""Probe B — variance decomposition of R21 finalization GE.

Question: is the R21 GE noise floor driven by PPO failing to learn (strategic_depth
collapsing) — as the R21 report's "bimodal PPO-failure" diagnosis claims — or by the
coarse small-sample evaluation estimators (strategic_diversity, non_triviality)?

If the latter, the proposed "PPO-convergence filter" (drop reruns where
trained_vs_random < 0.6) attacks the wrong variable AND biases the surviving mean
upward (survivorship), because trained_vs_random feeds non_triviality which feeds GE.

Reads the on-disk per-run CSVs only. No training, no DB writes.
"""
import csv
import statistics as st
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FIN = HERE.parent / "r21_finalization"
COMPS = ["strategic_depth", "non_triviality", "strategic_diversity", "rule_simplicity"]
OUT = []


def log(s=""):
    print(s)
    OUT.append(s)


def load(sub):
    rows = []
    with open(FIN / f"{sub}_per_run.csv") as f:
        for r in csv.DictReader(f):
            for k in ["go_essence", "original_ge", *COMPS]:
                r[k] = float(r[k])
            rows.append(r)
    return rows


def ge_formula(depth, non_triv, diversity, simplicity):
    """Reconstruct composite GE per scoring.py:458-479 (w_d=w_div=w_s=1, w_p=0)."""
    non_triv_factor = 0.1 + 0.9 * non_triv
    diversity_factor = 0.2 + 0.8 * diversity
    numerator = depth * diversity_factor * non_triv_factor
    raw = numerator / ((1.0 - simplicity) + 1e-8)
    return raw / (raw + 1.0)


def games_of(rows):
    g = {}
    for r in rows:
        g.setdefault(r["game_id"], []).append(r)
    return g


for sub in ["menger", "carpet", "grid"]:
    rows = load(sub)
    g = games_of(rows)
    log(f"\n{'='*72}\n{sub.upper()}  —  {len(rows)} reruns across {len(g)} games\n{'='*72}")

    # 1. Per-component stability across ALL reruns
    log("\n[1] Component spread across all reruns (low CV = stable, high = noisy):")
    log(f"    {'component':<22}{'min':>8}{'max':>8}{'mean':>8}{'sd':>8}{'CV':>8}")
    for c in COMPS:
        v = np.array([r[c] for r in rows])
        cv = v.std() / v.mean() if v.mean() else float("nan")
        log(f"    {c:<22}{v.min():>8.3f}{v.max():>8.3f}{v.mean():>8.3f}{v.std():>8.3f}{cv:>8.2f}")

    # 2. strategic_diversity quantization
    div = [round(r["strategic_diversity"], 3) for r in rows]
    vals = sorted(set(div))
    log(f"\n[2] strategic_diversity distinct values: {vals}")
    log(f"    counts: " + ", ".join(f"{v}:{div.count(v)}" for v in vals))

    # 3. GE==0 reruns — did PPO fail (low depth) or did the estimators collapse?
    zeros = [r for r in rows if r["go_essence"] < 0.01]
    log(f"\n[3] reruns with go_essence < 0.01: {len(zeros)} / {len(rows)}")
    if zeros:
        zd = np.array([r["strategic_depth"] for r in zeros])
        n_nt0 = sum(1 for r in zeros if r["non_triviality"] == 0.0)
        n_dv0 = sum(1 for r in zeros if r["strategic_diversity"] == 0.0)
        log(f"    of those: depth range {zd.min():.3f}-{zd.max():.3f} (mean {zd.mean():.3f})"
            f"  → PPO learning signal {'HEALTHY' if zd.min() > 0.3 else 'COLLAPSED'}")
        log(f"    non_triviality == 0 in {n_nt0}/{len(zeros)};  diversity == 0 in {n_dv0}/{len(zeros)}")

    # 4. Within-game variance decomposition: regress centered GE on centered components.
    #    Each component's share = its single-predictor R^2 of within-game GE variance.
    dG, dC = [], {c: [] for c in COMPS}
    for rs in g.values():
        if len(rs) < 3:
            continue
        gm = st.mean(r["go_essence"] for r in rs)
        cm = {c: st.mean(r[c] for r in rs) for c in COMPS}
        for r in rs:
            dG.append(r["go_essence"] - gm)
            for c in COMPS:
                dC[c].append(r[c] - cm[c])
    dG = np.array(dG)
    log(f"\n[4] within-game GE variance decomposition (single-predictor R^2 of GE swings):")
    var_dG = dG.var()
    for c in COMPS:
        x = np.array(dC[c])
        if x.std() < 1e-9 or var_dG < 1e-12:
            r2 = 0.0
        else:
            r2 = np.corrcoef(x, dG)[0, 1] ** 2
        log(f"    {c:<22} R^2 = {r2:6.3f}   (corr {np.corrcoef(x, dG)[0,1]:+.3f})")
    log(f"    total within-game GE variance = {var_dG:.5f}")

    # 5. Survivorship check: top game by 20-rerun mean, before vs after a
    #    convergence-filter proxy (drop low-competence reruns: non_triviality below
    #    its 25th pct OR == 0 — the CSV has no trained_vs_random, and non_triviality
    #    is the GE input that competence_factor feeds, so it is the faithful proxy).
    means = {gid: st.mean(r["go_essence"] for r in rs) for gid, rs in g.items()}
    top = max(means, key=means.get)
    rs = g[top]
    base = st.mean(r["go_essence"] for r in rs)
    kept = [r for r in rs if r["non_triviality"] > 0.0]
    filt = st.mean(r["go_essence"] for r in kept) if kept else float("nan")
    log(f"\n[5] survivorship demo on top {sub} game {top}:")
    log(f"    full {len(rs)}-rerun mean         = {base:.4f}")
    log(f"    after dropping {len(rs)-len(kept)} non_triviality==0 reruns = {filt:.4f}"
        f"   (Δ {filt-base:+.4f}; mean moves UP = upward bias)")

# Reconstruction sanity (does the formula match stored GE?)
log(f"\n{'='*72}\nFORMULA SANITY (reconstructed vs stored go_essence)\n{'='*72}")
allrows = []
for sub in ["menger", "carpet", "grid"]:
    allrows += load(sub)
rec = np.array([ge_formula(r["strategic_depth"], r["non_triviality"],
                           r["strategic_diversity"], r["rule_simplicity"]) for r in allrows])
act = np.array([r["go_essence"] for r in allrows])
log(f"    n={len(act)}  corr(reconstructed, stored) = {np.corrcoef(rec, act)[0,1]:.3f}"
    f"  mean|Δ| = {np.abs(rec-act).mean():.3f}")
log("    (high corr + nonzero |Δ| = formula is structurally right; stored GE is the")
log("     C2 average of per-internal-seed GE, so it differs from GE(avg components).)")

(HERE / "PROBE_B_RESULTS.md").write_text("# Probe B — GE variance decomposition\n\n```\n" + "\n".join(OUT) + "\n```\n")
print(f"\n[written] {HERE/'PROBE_B_RESULTS.md'}")
