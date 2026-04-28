# Run 17 Evaluation Report

**Database**: `genesis_v2_run17.db`
**Config**: 11 generations × 50 population × 10000 episode budget. Seeded with `frac_C_fractal` (sierpinski carpet substrate) and R16 carry-overs. Soft-rule audit enabled. Phase-1 engine prerequisites + Phase-2 generator/seeding + Phase-3 balance preflight + Phase-4 evolutionary run all shipped (commits `c70ccbc` → `6235cdf`).
**Run completed**: 2026-04-28
**Human evaluation**: 22-team headline eval on top-4 GE-ranked games (1 pilot + 6 production on rank 1; 5 each on ranks 2, 3, 4)

---

## Executive Summary

R17 is the **first run in months where engineering shipped clean but games regressed**. The R17 champion (`44f6630277b3`, mean **4.14/10**) underperforms R16's human winner (`c6bb58075520`, 4.40/10) by 0.26 — outside the SD bands of either game. Overall mean across the four evaluated games is **3.50/10**.

The headline finding is structural: **no fractal substrate appears in the top 4**. All four GE-ranked games are 3D cubic grids (4×4×4 = 64 cells). The seeded sierpinski-carpet candidate (`frac_C_fractal`) collapsed under PPO training — the trained agent produced 2-step games, average length 2.0, despite passing the mechanical 300-episode balance probe.

**What actually said positive things about the run:**
- The Phase-1 seat-balance hard-zero correctly killed both R16 winners (both had documented P1 bias). The metric is now more honest.
- One genuinely novel mechanic surfaced: team-6 on the champion described "Reversi-meets-Hex on 4³ with capture-completes-connection in 2 of 4 games."
- Knowledge-asymmetry, not seat-asymmetry, is the dominant balance failure mode in R17 games — a more interesting failure than R13-R16's "P1 always wins."

**What said negative things:**
- The R17 mean of 3.50 ranks third-worst across R13-R17 (only R15's 2.43 is clearly worse).
- GE-vs-human disagreement remains severe: GE rank-3 (`275978116158`, GE 0.2865) was unanimously called broken (mean 2.60); GE rank-2 (`a3a6bd2b1b5b`, GE 0.3582) effectively tied GE rank-1 in human eval (4.00 vs 4.14).
- Hybrid actions (place+move) confirmed unanimously dead. Across 22 verdicts, **0 move actions** were used in skilled play. The `total_cells × max_degree` action-space bloat is wasted training budget.
- `_fix_consistency` does not enforce substrate-specific invariants: sierpinski crossovers produced two illegal `topology=sierpinski + axis=8 + dims!=2` instances during the run, caught by engine WARN and skipped — invisibly removing fractal genotypes from the surviving population.

R8's Connection Go (8/10) remains the all-time ceiling. R13-R17 plateau remains 4-5/10.

---

## Final Leaderboard — GE vs Human

| GE Rank | Game ID | GE | Mechanics | n | Human Mean | SD | Δ |
|---------|---------|------|-----------|---|------------|-----|---|
| 1 | `44f6630277b3` | 0.3773 | 3D 4³ grid + custodian + connection (asymmetric P1=z, P2=x) + place+move | 7 | **4.14** | 1.07 | 0 |
| 2 | `a3a6bd2b1b5b` | 0.3582 | 3D 4³ grid + surround + perpendicular-axis connection | 5 | 4.00 | 0.71 | 0 |
| 3 | `275978116158` | 0.2865 | 3D moore + outnumber-2 + connection + place+move | 5 | **2.60** | 0.55 | −2 |
| 4 | `9841cb9e6750` | (rank 4) | 3D 4³ + surround + radius-2 influence + threshold-race | 5 | 3.00 | 0.71 | 0 |

**Overall mean**: 3.50/10 across 22 verdicts.

**Run-over-run trend (best human-evaluated game in run):**
- R8: 8.0
- R13: 5.0
- R14: 4.57
- R15: 2.43
- R16: 4.40
- R17: **4.14** (regression vs R16 by 0.26)

---

## Per-Game Findings

### Rank 1 — `44f6630277b3` "3D Custodian Connect" (R17 champion)

**Format**: 3D 4×4×4 grid (64 cells, max degree 6). Alternating, place+move actions (move = adjacent_empty, capture-on-landing). Custodian capture, threshold 1, axis-aligned. Asymmetric connection win: P1 connects z-faces, P2 connects x-faces. `prop_type=none` (radius/strength/decay fields are inert noise). Gen 11.

**Team-by-team Overall scores**: pilot 3, team-1 5, team-2 4, team-3 4, team-4 3, team-5 4, team-6 6 → **mean 4.14, SD 1.07**.

**Consensus findings:**
- Asymmetric connection objective (P1 vertical, P2 horizontal) creates a knowledge-asymmetry rather than seat-asymmetry. Pilot's "P1 dominance" read was wrong: teams 2, 3, and 5 each found different decisive lines, with at least three viable winning patterns across teams.
- Custodian capture is mechanically active and produces capture-completes-connection moments (team-6 saw this in 2 of 4 games).
- Movement actions are unused. The 64×6 = 384 move actions out of 449 total are wasted training budget. The agents never benefit from picking up a stone and moving it — placement dominates.
- Genuine 3D winding paths surfaced (team-5). Multi-axis chain dynamics are something genuinely novel vs the 2D R8-R16 corpus.

**Killer flaws:**
1. Hybrid action space wastes ~85% of the action vocabulary
2. Knowledge-asymmetry imbalance — first-time players default-pick wrong axis
3. 4³ with degree-3-to-6 cells means surrounded captures rarely fire on edges/corners

**Best quality**: capture-completes-connection. R8's Connection Go and capture-influence-threshold (R16's c6bb58075520) point at this design family; R17's champion adds 3D + asymmetric objectives as a genuine new dimension.

---

### Rank 2 — `a3a6bd2b1b5b` "3D Surround Perpendicular Connect"

**Format**: 3D 4³ grid + surround capture + perpendicular-axis connection win. Gen 11.

**Team-by-team Overall scores**: team-7 4, team-8 4, team-9 3, team-10 4, team-11 5 → **mean 4.00, SD 0.71**.

**Consensus findings:**
- Effectively ties the GE rank-1 champion (4.00 vs 4.14) — within SD bands. GE penalised this game by 0.0191 vs rank-1 but humans don't see the gap.
- Surround capture is *partially* dead in 3D-4³: interior cells have degree 6 but edge/corner cells have degree 3-4, so surround firing depends heavily on board location. Less catastrophic than the moore→grid R16 case but in the same family.
- Some teams flagged that the 3D substrate "added nothing" — playable as a 2D variant — challenging whether 3D is justified at axis-size 4.

**Killer flaws:**
1. Surround capture is geometry-dependent, not strategy-dependent
2. Axis_size 4 too small for 3D — liberty counts 3-6 make most surrounds inert

**Best quality**: perpendicular-axis connection objectives reuse the asymmetric-objective pattern from rank-1 cleanly.

---

### Rank 3 — `275978116158` "3D Moore Outnumber Connect" — UNANIMOUSLY BROKEN

**Format**: 3D moore (28-neighbour Chebyshev in 3D) + outnumber-2 capture + connection + place+move. Gen 10-ish.

**Team-by-team Overall scores**: team-12 2, team-13 3, team-14 2, team-15 3, team-16 3 → **mean 2.60, SD 0.55**.

**Consensus findings (5/5 teams):**
- **Early forced wins**. P1 reaches a winning configuration before P2 has placed enough stones to contest. Greedy probes show P1 wins 8/10 to 10/10 across teams.
- **3D moore is cataclysmic for outnumber-2**: 28-neighbour adjacency means stones are surrounded by default — outnumber-2 fires on placement at almost any interior cell.
- This is the **largest GE-vs-human disagreement in R17**: GE 0.2865 ranked it 3rd; humans rank it last with high agreement (SD 0.55, the tightest in the run). The metric over-rewards complexity over playability.

**Killer flaws:**
1. P1 forced wins under skilled play
2. Outnumber-2 + 3D-moore makes capture trivial
3. Hybrid action space — moves unused as elsewhere

**Why this slipped through GE**: the broken game has high non-trivial-game-rate (captures fire constantly) and high ELO separation between trained and random agents (because the trained agent rapidly learns the forced-win line). GE rewards both. But the line is *brittle* — knowing the winning sequence is the whole game.

---

### Rank 4 — `9841cb9e6750` "3D Surround Influence Threshold-Race"

**Format**: 3D 4³ grid + surround capture + radius-2 signed influence + threshold-race win.

**Team-by-team Overall scores**: team-17 3, team-18 2, team-19 4, team-20 3, team-21 3 → **mean 3.00, SD 0.71**.

**Consensus findings:**
- P1 forced wins in greedy and probe play. Less catastrophic than rank-3 but still common.
- Radius-2 influence in 3D produces a 33-cell footprint — far larger than 2D radius-2 (13 cells). Center-grab strategy is even more dominant in 3D.
- Threshold-race win condition with no capture-recovery mechanism (surround being dead in 3D-4³, see rank 2) means whoever reaches threshold first wins — and that's whoever grabs center first.

**Killer flaws:**
1. P1 first-mover with center-grab dominates
2. Surround capture inert (same as rank 2)
3. Threshold-race + influence + no working capture = R13-R14-style flat strategic surface

**Best quality**: the only thing that's *not* broken is influence math — the radial kernel works correctly in 3D.

---

## Cross-Cutting Discoveries

### 1. NEW engine issue: `_fix_consistency` skips substrate-specific invariants

**Severity**: HIGH — blocks fractals from surviving evolution
**Reporters**: R17 run logs (2× WARN: `topology=sierpinski + axis=8 + dims!=2`)

**Details**: `evolution/operators_v2.py:_fix_consistency` enforces some constraints (the moore→grid downgrade for surround capture from R16 was apparently still missing — see R16 lesson 2) but does not enforce substrate-shape invariants. Sierpinski substrates require axis=9 and dims=2; vicsek requires axis=8 and dims=2; 3D fractals like menger require axis=27 and dims=3. When mutation/crossover flips the topology field without consistent axis/dims fields, the resulting genotype is invalid; the engine logs WARN and silently skips during evaluation.

**Impact**: Every fractal genotype that survives to evaluation is a survivor of a filter that biases against fractals. The seeded sierpinski candidate (`frac_C_fractal`) couldn't propagate genes — by gen 11, the population is entirely 3D cubic grids. **This is the #1 reason R17 has no fractal in top 4.**

**Fix direction**: Land BEFORE R18. Add per-substrate invariant enforcement (sierpinski → axis=9, dims=2; vicsek → axis=8, dims=2; menger → axis=27, dims=3; hexaflake → axis=7, dims=2). Add a round-trip mutate+crossover unit test.

---

### 2. NEW engine issue: mechanical balance probe doesn't catch PPO collapse

**Severity**: HIGH — wastes seed budget, masks broken seeds
**Reporter**: R17 Phase-3 (balance preflight on `frac_C_fractal`)

**Details**: Phase-3 balance preflight ran a 300-episode greedy-vs-greedy probe on `frac_C_fractal` and reported it balanced. Phase-4 trained PPO on it for the full 10k-episode budget; the resulting agent produced average game length **2.0 turns**. The mechanical probe didn't catch that the substrate's strategic surface, under PPO optimization, collapses to a near-immediate forced sequence.

**Impact**: One of the two seeded genotypes contributed nothing to R17. With multi-seed-per-substrate (R18 plan B3), this failure mode would silently waste 1/3 to 1/N of the seed budget per round.

**Fix direction**: Replace the 300-episode mechanical probe with a 3000-episode PPO smoke. Gate: drop seed if `avg_length < max(8, 0.10 × cells)` OR P1 forced-win rate > 30%. Land BEFORE R18 seed generation.

---

### 3. CONFIRMED dead: hybrid place+move action space

**Severity**: MEDIUM — wastes training budget, doesn't break games
**Reporters**: All 22 R17 verdicts (unanimous)

**Details**: R17 ranks 1 and 3 used hybrid place+move action space. Total action vocabulary is `total_cells + 1 + total_cells × max_degree`. For 64-cell 3D-4³ grid, that's 64+1+384 = 449 actions, of which ~86% are move actions. **Across all 22 evaluations, zero move actions were observed in skilled play**. PPO learns that move dominates only as a degenerate "free pass" in degenerate positions and never picks it as a positive-utility action.

**Impact**: ~5-7× the action space, ~5-7× the policy-network parameter count, no observed strategic benefit. R17's 10k-episode budget is effectively a 1.5k-episode budget on the actually-useful part of the action space.

**Fix direction (R19, not R18)**: Ban hybrid actions unless empirical move-action usage during PPO training exceeds 10%. Make the threshold an evolutionary fitness penalty rather than a hard ban.

---

### 4. CONFIRMED working: Phase-1 seat-balance hard-zero

**Severity**: positive — engine improvement landed cleanly
**Reporters**: R17 metric outputs vs R16 ground-truth comparison

**Details**: R16's two human-evaluated winners (`8d12c8b92b71` GE rank-1, `c6bb58075520` GE rank-3) both had documented P1 bias. R17's Phase-1 seat-balance hard-zero correctly returns 0 fitness when greedy-vs-greedy probe shows >87% same-seat wins. Both R16 winners would have been killed by the new metric.

**Impact**: The metric is more honest. R17's regression isn't because the metric got worse — it's because the population didn't find anything that beat the higher bar.

**Status**: Keep as-is for R18.

---

### 5. CONFIRMED: GE-vs-human disagreement is over-rewarding complexity

**Severity**: MEDIUM — affects fitness signal calibration
**Reporters**: R13, R14, R15, R16, R17 (every run)

**Details**: R17's rank-3 game has GE 0.2865 (above 0.25 = "interesting" threshold) and is unanimously called broken. R17's rank-2 (GE 0.3582) effectively ties rank-1 (GE 0.3773) in human eval. The pattern across runs: GE detects high-action-rate, high-ELO-gap, non-trivial games. It does *not* detect "the strategy collapses to a known forced line."

**Fix direction (R19+, not R18)**: Add a "playability sanity" component to GE — perhaps a heuristic that detects if greedy-vs-best-trained shows the same player winning >85% of games OR if game length distribution has its mode at <8% of max-turns.

For R18 specifically: the 3-team-per-substrate human eval gate must include an explicit playability check (forced-win <10 moves OR avg length <8 → mark broken regardless of GE).

---

## Soft-rule audit (run 2026-04-28 on `genesis_v2_run17.db`)

```
rule                         n   go_essence       strategic_depth   strategic_diversity
sierpinski_ca_unvalidated    2   0.000*Δ-0.012   0.074*Δ-0.174    0.000*Δ-0.373
sierpinski_threshold_inert   3   0.000*Δ-0.012   0.074*Δ-0.174    0.000*Δ-0.373
```

Both rules show negative Δ across all three metrics with p<0.05 — **the soft rules are justified** (violating games score worse than clean games). However, sample size is tiny (n=2 and n=3). Recommendation: **keep both as soft for R18**, expecting fractal-scan multi-seed to grow N. Promote to hard for R19 if R18 produces ≥30 violations per rule and the negative Δ holds.

---

## Implications for R18

R17 establishes the engineering preconditions for a **fractal Hausdorff-dimension scan** as R18:

**Pre-launch blockers** (must land before R18 evolution):
1. **B1** — `_fix_consistency` substrate invariant fix (operators_v2.py)
2. **B2** — 3000-episode PPO smoke gate, replacing the mechanical balance probe
3. **B3** — multi-seed: 3 rule combos × 6 substrates = 18 seeds

**Architecture**: 6 independent per-substrate evolutions (not one big run). Single-population evolution will collapse to whatever the fitness landscape favors — R17's "no fractal in top 4" is direct evidence. Drop the substrate-novelty multiplier (it's irrelevant under separate-runs architecture).

**Substrate set** (6 rows, dim 1.46 → 2.73, cells 250-625):

| Substrate | Hausdorff dim | Iter | Cells |
|-----------|---------------|------|-------|
| Vicsek (2D) | 1.465 | 4 | 625 |
| Sierpinski tri | 1.585 | 5 | 243 |
| Hexaflake | 1.771 | 3 | 343 |
| Sierpinski carpet | 1.893 | 3 | 512 |
| 2D grid (control) | 2.0 | — | 256 |
| Menger sponge | 2.727 | 2 | 400 |

**Eval style**: 3-team per substrate × 6 substrates = 18 evals. Each team plays one game on one substrate's top-1, with explicit playability sanity gate. Output: dim → fitness curve. R19 picks the sweet-spot dim and goes for a champion run.

**Deferred to R19**: pie-rule for knowledge-asymmetry balance, hybrid-action ban, axis-size 5+ for 3D substrates, GE playability component.

---

## Files & References

- 22 verdicts: `evaluations/run17/`
- R17 plots: committed in `6235cdf`
- R17 final db: `genesis_v2_run17.db`
- Soft-rule audit script: `scripts/audit_soft_rules.py`
- R17 commits: `c70ccbc` → `193290f` (cumulative phases + verdicts + helper-script gitignore)
- R18 plan v2: drafted 2026-04-28 (this session); see project-state memory for canonical plan
