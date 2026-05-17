# R21 grid champion-finalization results

Per-game GE distribution from 20 outer reruns × `num_independent_runs=3` C2 averaging = 60 unique PPO seeds per game.

Header line "R20" and "15 unique PPO seeds" in the auto-generated output are stale strings in `experiments/r20_finalization/finalize_champions.py:329-332` — corrected here at commit time; upstream fix queued for R22.

| Substrate | Game | original_GE | n | mean GE | std GE | min | max | range | Δ vs original |
|---|---|---|---|---|---|---|---|---|---|
| grid | `b12ff78f1c1d` | 0.1503 | 20 | 0.0985 | 0.0517 | 0.0239 | 0.2064 | 0.1825 | -0.0518 |
| grid | `e7c85d3409e6` | 0.1734 | 20 | 0.0886 | 0.0627 | 0.0000 | 0.2141 | 0.2141 | -0.0847 |
| grid | `edb473f0872b` | 0.0021 | 20 | 0.0045 | 0.0033 | 0.0007 | 0.0101 | 0.0095 | +0.0024 |
| grid | `283129d9fffe` | 0.0016 | 20 | 0.0044 | 0.0074 | 0.0000 | 0.0318 | 0.0318 | +0.0028 |
| grid | `573562833174` | 0.0027 | 20 | 0.0021 | 0.0022 | 0.0000 | 0.0086 | 0.0086 | -0.0007 |

## Read
- `std GE` is the post-15-seed measurement noise. Goal: < 0.04 on menger, < 0.03 on carpet (vs Phase A under-estimates of 0.014/0.155).
- `Δ vs original` shows where the production-stack 3-seed scoring was over- or under-estimating. Large positive Δ = the original was an unlucky-seed underestimate (carpet's Phase B finding).
- Cross-substrate comparisons are honest only when |Δmean| > max(σ_a, σ_b). Annotate substrate-vs-substrate claims accordingly.
