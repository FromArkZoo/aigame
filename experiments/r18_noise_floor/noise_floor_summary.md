# R18 noise-floor results

Per-game GE distribution from 5 fresh PPO retrains (each retrain = num_independent_runs=3, training_budget=5000).

Comparing against the substrate-comparison figure's reported error bars:

| Substrate | Dim | Game | Phase A σ (chart) | n | mean GE | std GE | min | max | range |
|---|---|---|---|---|---|---|---|---|---|
| vicsek | 1.465 | `1e11adebcc35` | 0.171 | 5 | 0.0037 | 0.0047 | 0.0000 | 0.0119 | 0.0119 |
| triangle | 1.585 | `558be82199a8` | 0.018 | 5 | 0.0862 | 0.0557 | 0.0333 | 0.1707 | 0.1374 |
| carpet | 1.893 | `8776b2026957` | 0.155 | 5 | 0.0847 | 0.0719 | 0.0196 | 0.2060 | 0.1864 |
| grid | 2.0 | `ab7270a81cd6` | 0.102 | 5 | 0.0022 | 0.0019 | 0.0000 | 0.0042 | 0.0042 |
| menger | 2.727 | `0f5e931fa3e1` | 0.014 | 5 | 0.1843 | 0.0910 | 0.0716 | 0.2798 | 0.2083 |

**Read:** if `std GE` is materially lower than `Phase A σ (chart)` for the noisy substrates (carpet/grid/vicsek), C2 multi-seed averaging is doing its job and the chart's worst error bars over-state real noise. If `std GE` ≈ `Phase A σ (chart)`, the chart's bars are honest and most rankings are noise.

**Decision criteria:**
- carpet std > 0.10 → carpet's rescued 0.347 is single-rescue noise, drops out
- carpet std < 0.05 AND mean > 0.20 → thesis breaks (carpet at dim 1.893 outperforms menger at 2.727)
- menger std stays ~0.014: chart's reliability tags hold
