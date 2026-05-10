# R20 champion-finalization results

Per-game GE distribution from 5 outer reruns × `num_independent_runs=3` C2 averaging = 15 unique PPO seeds per game.

| Substrate | Game | original_GE | n | mean GE | std GE | min | max | range | Δ vs original |
|---|---|---|---|---|---|---|---|---|---|
| menger | `77f8288387d9` | 0.2150 | 5 | 0.1295 | 0.0899 | 0.0646 | 0.2802 | 0.2155 | -0.0855 |
| menger | `2f378e8c18b5` | 0.2383 | 5 | 0.1150 | 0.0633 | 0.0193 | 0.1714 | 0.1521 | -0.1233 |
| menger | `66c7c98d3745` | 0.2152 | 5 | 0.0943 | 0.0423 | 0.0318 | 0.1293 | 0.0975 | -0.1208 |

## Read
- `std GE` is the post-15-seed measurement noise. Goal: < 0.04 on menger, < 0.03 on carpet (vs Phase A under-estimates of 0.014/0.155).
- `Δ vs original` shows where the production-stack 3-seed scoring was over- or under-estimating. Large positive Δ = the original was an unlucky-seed underestimate (carpet's Phase B finding).
- Cross-substrate comparisons are honest only when |Δmean| > max(σ_a, σ_b). Annotate substrate-vs-substrate claims accordingly.
