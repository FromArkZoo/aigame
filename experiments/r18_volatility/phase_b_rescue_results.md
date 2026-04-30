# Phase B — R18 multi-seed rescue results

Companion to `phase_a_results.md`. Phase A measured the *volatility* of
per-game GE; Phase B uses C2 (multi-seed averaging) to **re-derive**
each R18 game's headline GE from the per-run training_runs data already
in the DB. No retraining.

Method recap (`rescue_multiseed.py`):

1. For each game with N≥2 runs, compute `partial_orig` from run-0 inputs
   only (the inputs R18 actually used for headline GE) and `partial_resc`
   from C2-averaged inputs (point-wise mean curve, mean tvr/p0/avg_len
   across all N runs). Both pass through the same `composite_score` +
   `length_factor` math as the engine.
2. `rescued_ge = stored_ge × (partial_resc / partial_orig)`.

The ratio approach is exact: seat_balance, timeout, novelty bonus, and
stability all cancel out (they are PPO-seed-independent or use the full
per-run list in both numerator and denominator). What changes is exactly
the multi-seed-averaging effect.

Inputs: 5 R18 DBs, 436 games rescuable (N≥2 runs).

## Headline: which substrates' rankings change?

| Substrate | Stored top-1 GE | Rescued top-1 GE | Same top-1? | Top-5 overlap |
|-----------|-----------------|------------------|-------------|---------------|
| menger    | 0.3368 | **0.2689** | yes | 5/5 |
| carpet    | 0.1633 | **0.3465** | yes | 5/5 |
| vicsek    | 0.0525 | **0.0238** | **no** (rank-2 takes over) | 5/5 (reordered) |
| grid      | 0.0432 | **0.0105** | **no** (rank-5 takes over) | 2/5 |
| triangle  | 0.0629 | 0.0596 | yes | 2/5 |

The pattern matches Phase A's volatility split: where Phase A flagged a
substrate as **noisy**, the multi-seed rescue moves the headline number
substantially; where Phase A flagged **reliable**, the rescue confirms.

## Per-substrate findings

### carpet — champion was UNDERESTIMATED 2.1×

`8776b2026957` (gen 7, custodian + outnumber-2): stored 0.1633 → rescued
**0.3465** (+0.183, ratio 2.12). The averaged learning curve has higher
AUC and the averaged tvr is 0.78 vs run-0's 0.54 — run-0 was a *low* draw
of the distribution, not a good one.

This flips the R18 narrative for carpet. The eval report had carpet at
"moderate, not breakthrough"; the rescue puts it at par with menger's
peak (0.4649 per-gen) and ahead of menger's stable end-of-run (0.3368
→ 0.2689 after rescue).

| game_id | stored | rescued | Δ | n_runs |
|---|---|---|---|---|
| 8776b2026957 | 0.1633 | **0.3465** | +0.183 | 9 |
| 1f74e2e49e77 | 0.0275 | 0.0037 | −0.024 | 3 |
| 90c76de9b665 | 0.0176 | 0.0033 | −0.014 | 3 |

### menger — champion was MILDLY OVERESTIMATED, ranking holds

`0f5e931fa3e1` (gen 7, capture+influence+threshold): stored 0.3368 →
rescued **0.2689** (−0.068, ratio 0.80). Within Phase A's measured
volatility band (0.014 std on top games × 5 ≈ 0.07). Top-1 stays top-1;
top-5 overlap perfect; menger ranking holds.

Top-2 swap: `2bd596c4b551` (stored rank 2) drops to rank 5 (−0.061);
`c9cd739516e7` rises rank 3 → 2 (+0.002). Headline number is still
~0.27 — well above grid's rescued top-1 (0.011) and within Phase A's
expected drift for menger.

### vicsek — top-1 changes

`1e11adebcc35` (stored top-1, ge 0.0525, n=12) → rescued ge **0.0051**.
Run-0 had tvr 0.94 vs averaged 0.45; depth dropped 0.79 → 0.44. R18's
"vicsek peak" was a single-seed spike.

Rescued top-1 is `ab8bd83e558a` at 0.0238 — but even this is small.
Vicsek substrate-level GE remains low across the rescued ranking; the
*identity* of the top game changes, but the *substrate-level conclusion*
doesn't (vicsek doesn't produce strong games at axis-27).

### grid — control behaves like a control

`ab7270a81cd6` (stored top-1, ge 0.0432) → rescued ge **0.0083**, drops
to rank 3. Rescued top-1 is `7d4762b79839` at 0.0105. Same story as
vicsek: noise spike inflated the original headline, ranking reshuffles
in the low-GE noise band where it doesn't matter.

Top-5 overlap 2/5 is the worst of any substrate. Grid is genuinely the
control: nothing in its ranking is signal.

### triangle — mostly tied, mostly noise

`558be82199a8` stays top-1 (rescued 0.060 vs stored 0.063) — its peak
status was real. The rest of the top-10 is the multi-way tie at ~0.0009
that Phase A already flagged: all those games have neutral
strategic_diversity, low depth, and they reshuffle in the rescued
ranking because the absolute deltas (~0.0007) are larger than the
absolute values themselves. None of this matters. Triangle is the
weakest substrate and stays so.

## Substrate-level deltas

(rescuable games only — those with N ≥ 2 runs)

| substrate | n_resc | Δ mean | Δ std | rescued/stored ratio (mean / median) | sign(Δ): + / − / ≈0 |
|-----------|--------|--------|-------|--------------------------------------|---------------------|
| vicsek    | 47 | −0.003 | 0.009 | 1.03 / 1.00 | 1 / 4 / 42 |
| triangle  | 49 | +0.000 | 0.001 | 1.65 / 1.34 | 30 / 7 / 12 |
| carpet    |  5 | +0.029 | 0.078 | 0.68 / 0.20 | 1 / 4 / 0  |
| grid      | 32 | −0.002 | 0.008 | 1.66 / 1.00 | 12 / 15 / 5 |
| menger    | 26 | −0.006 | 0.017 | 1.26 / 0.97 | 12 / 14 / 0 |

Triangle and grid have *high mean ratios* but tiny absolute deltas — the
ratio is meaningful only in the rare cases where stored GE is non-zero.
Carpet's median ratio of 0.20 (most rescuable carpet games go DOWN
substantially) plus the champion going UP 2.1× shows the spread: the
top-1 was atypical even within carpet.

## What this means for R18 conclusions

Updated relative to `evaluation_report_run18.md`:

1. **Carpet rises**: rescued top-1 0.3465 is comparable to menger's
   stable end-of-run (0.2689 after rescue). The R18 eval report's
   characterization of carpet as "stable but moderate" undersold it.
   Carpet champion `8776b2026957` (custodian + outnumber-2) is now a
   plausible R19 candidate alongside menger.
2. **Menger holds**: 0.2689 still the highest-stable-GE single game
   across all 5 substrates; ranking holds; volatility expectation matches
   Phase A. R19 commit-to-menger conclusion is unchanged.
3. **Vicsek and grid headlines were single-run noise**: original top-1s
   demote out of top-1; rescued top-1s are still small. Substrate-level
   verdicts unchanged but the specific game IDs in those rankings are
   not load-bearing.
4. **Triangle is unchanged**: weakest, mostly tied at ~10⁻³, peak game
   real but small.

## Implications for R19

- C2 must land before R19 evolution starts. The carpet-champion case
  shows that without averaging, a *good* game can be misranked as
  middling because run-0 was unlucky — and elite-carry-over selection
  (R17 introduced this) will then prune the genuine top games early.
- Per Phase A noise floor + this rescue: carpet should be **kept** for
  R19, contrary to the R18 eval report's lean toward menger-only. The
  rescued carpet champion clears the same bar as menger.
- Grid as control is validated: rescued grid top-1 (0.011) is the
  noise floor we should expect any R19 result to clear.

## Files

- `rescue_multiseed.py` — script
- `phase_b_rescue_per_game.csv` — full per-game rescue records
- `phase_b_rescue_results.md` — this report
