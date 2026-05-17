# R21 carpet champion-finalization results

Per-game GE distribution from 20 outer reruns × `num_independent_runs=3` C2 averaging = 60 unique PPO seeds per game.

Header line "R20" and "15 unique PPO seeds" in the auto-generated output are stale strings in `experiments/r20_finalization/finalize_champions.py:329-332` — corrected here at commit time; upstream fix queued for R22.

| Substrate | Game | original_GE | n | mean GE | std GE | min | max | range | Δ vs original |
|---|---|---|---|---|---|---|---|---|---|
| carpet | `d995cf010504` | 0.0936 | 20 | 0.1031 | 0.0725 | 0.0000 | 0.2448 | 0.2448 | +0.0095 |
| carpet | `c438ddfd2f5c` | 0.1754 | 20 | 0.0908 | 0.0647 | 0.0023 | 0.1858 | 0.1835 | -0.0846 |
| carpet | `aa6299e181a9` | 0.0142 | 20 | 0.0585 | 0.0775 | 0.0029 | 0.2461 | 0.2432 | +0.0442 |
| carpet | `2c735c592631` | 0.1333 | 20 | 0.0286 | 0.0552 | 0.0025 | 0.2185 | 0.2161 | -0.1048 |
| carpet | `5c79329a9ddd` | 0.0160 | 20 | 0.0159 | 0.0441 | 0.0003 | 0.1990 | 0.1987 | -0.0001 |

## Read
- `std GE` is the post-15-seed measurement noise. Goal: < 0.04 on menger, < 0.03 on carpet (vs Phase A under-estimates of 0.014/0.155).
- `Δ vs original` shows where the production-stack 3-seed scoring was over- or under-estimating. Large positive Δ = the original was an unlucky-seed underestimate (carpet's Phase B finding).
- Cross-substrate comparisons are honest only when |Δmean| > max(σ_a, σ_b). Annotate substrate-vs-substrate claims accordingly.
