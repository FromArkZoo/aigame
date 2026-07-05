# RC2 §0 — σ-FILE (T1-PG sampling SD)  [C4]

Source: `experiments/rc2_planning_gap/cost_tiering.json` (ADOPT_T1 tier).  
Estimator: bootstrap of 24 stored per-game outcome cells; T1-PG = mean(outcomes)-0.5; sigma = SD of resampled T1-PG.  
Bootstrap: B=100,000, seed=95,000,000 (registered bootstrap stream, §2).

| game | family | W/D/L | T1-PG | σ(bootstrap) | σ(analytic) |
|------|--------|-------|-------|--------------|-------------|
| S1 | connection | 10/3/11 | -0.0208 | 0.0952 | 0.0974 |
| S2 | threshold | 10/6/8 | +0.0417 | 0.0879 | 0.0899 |
| S3 | connection | 23/0/1 | +0.4583 | 0.0406 | 0.0417 |
| S4 | territory | 2/0/22 | -0.4167 | 0.0566 | 0.0576 |
| S5 | territory | 13/0/11 | +0.0417 | 0.1016 | 0.1039 |
| d4015a646ae3 | connection | 22/0/2 | +0.4167 | 0.0564 | 0.0576 |
| e1453dac5445 | threshold | 9/0/15 | -0.1250 | 0.0989 | 0.1009 |

- σ_max (roster) = **0.1016**  ·  σ_mean = 0.0767  ·  σ_median = 0.0879
- Provisional draft σ ≈ 0.07 → measured σ_max = 0.1016

## Finalized CAL-I constant (§5)

Registered rule: σ_diff = σ·√2, σ = max-over-roster σ(T1,n=24) (§5 formula × §0 conservative selection).
- σ used = σ_max = **0.1016** (S5).
- σ_diff = σ_max·√2 = **0.1437**.
- Separation threshold = 3·σ_diff = **0.4310** (provisional draft: 0.30).
- CAL-I pair: d4015a646ae3 (positive) vs S4 (negative); observed separation at streams 42/43 = +0.8333 → passes with 5.8σ_diff margin.
- Diagnostic (not binding): accurate heteroskedastic pair σ_diff = √(σ_d4015a646ae3²+σ_S4²) = 0.0799; the registered max-over-roster rule is 1.8× more conservative.

## Heteroskedasticity caveat

e1453 sits in the negative PG region (negative_pg_check.py); its outcome variance need not match the informative-region games. Constants are set from the max-over-roster σ, not e1453, so the caveat only widens (never relaxes) the bar.
