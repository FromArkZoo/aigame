# Phase-1 MCTS evaluator — results

Per-game empirical σ across reruns of MCTS@N-vs-ladder winrate, at sim counts [16, 64, 256].

## Per-(game, sim_count) winrate

| Substrate | Dim | Game | Sims | n_reruns | mean WR | σ WR | min | max |
|---|---|---|---:|---:|---:|---:|---:|---:|
| vicsek | 1.465 | `1e11adebcc35` | 16 | 5 | 0.475 | 0.105 | 0.375 | 0.625 |
| vicsek | 1.465 | `1e11adebcc35` | 64 | 5 | 0.625 | 0.153 | 0.500 | 0.875 |
| vicsek | 1.465 | `1e11adebcc35` | 256 | 5 | 0.825 | 0.143 | 0.625 | 1.000 |
| triangle | 1.585 | `558be82199a8` | 16 | 5 | 0.675 | 0.112 | 0.500 | 0.750 |
| triangle | 1.585 | `558be82199a8` | 64 | 5 | 0.700 | 0.143 | 0.500 | 0.875 |
| triangle | 1.585 | `558be82199a8` | 256 | 5 | 0.775 | 0.185 | 0.500 | 1.000 |
| carpet | 1.893 | `8776b2026957` | 16 | 5 | 0.613 | 0.190 | 0.438 | 0.875 |
| carpet | 1.893 | `8776b2026957` | 64 | 5 | 0.625 | 0.177 | 0.375 | 0.750 |
| carpet | 1.893 | `8776b2026957` | 256 | 5 | 0.725 | 0.224 | 0.500 | 1.000 |
| grid | 2.0 | `ab7270a81cd6` | 16 | 5 | 0.600 | 0.105 | 0.500 | 0.750 |
| grid | 2.0 | `ab7270a81cd6` | 64 | 5 | 0.625 | 0.125 | 0.500 | 0.812 |
| grid | 2.0 | `ab7270a81cd6` | 256 | 5 | 0.725 | 0.205 | 0.500 | 0.938 |
| menger | 2.727 | `0f5e931fa3e1` | 16 | 5 | 0.650 | 0.163 | 0.375 | 0.750 |
| menger | 2.727 | `0f5e931fa3e1` | 64 | 5 | 0.750 | 0.125 | 0.625 | 0.875 |
| menger | 2.727 | `0f5e931fa3e1` | 256 | 5 | 0.725 | 0.163 | 0.500 | 0.875 |

## Scaling-slope per game (N=16 → N=256, 4.0 doublings)

Slope = (WR@max − WR@min) / log2(max/min). σ across reruns is the noise floor of this candidate fitness metric.

| Substrate | Dim | Game | n_reruns | mean slope | σ slope | mean Δ WR |
|---|---|---|---:|---:|---:|---:|
| vicsek | 1.465 | `1e11adebcc35` | 5 | +0.0875 | 0.0464 | +0.350 |
| triangle | 1.585 | `558be82199a8` | 5 | +0.0250 | 0.0513 | +0.100 |
| carpet | 1.893 | `8776b2026957` | 5 | +0.0281 | 0.0859 | +0.113 |
| grid | 2.0 | `ab7270a81cd6` | 5 | +0.0312 | 0.0442 | +0.125 |
| menger | 2.727 | `0f5e931fa3e1` | 5 | +0.0187 | 0.0648 | +0.075 |

## Comparison against GE noise floor

From `experiments/r18_noise_floor/noise_floor_summary.md`, the production-stack GE σ floor is **0.05–0.09** on top games (menger 0.091, carpet 0.072, triangle 0.056). The Phase-1 σ columns above measure noise on a *different* metric: winrate in [0, 1] and slope in [-0.25, 0.25] (max), vs GE in roughly [0, 0.4]. Direct numeric comparison is approximate; the meaningful signal is whether **slope σ < 0.03** (roughly a third of GE σ on its own scale).

**Decision criteria for Phase 2 (OpenSpiel / expanded ladder):**
- slope σ ≤ 0.02 on all 5 substrates: scaling slope is a viable   GE replacement → Phase 2 worth doing.
- slope σ in 0.02–0.05: marginal → Phase 2 only on substrates   that look promising.
- slope σ > 0.05 broadly: Phase 1 MCTS doesn't beat GE → hold   off on OpenSpiel and revisit metric design instead.

**Opponent.** Configured as `ladder`. For `ladder` mode the weak side is MCTS@(N/ladder_ratio) using the same nets, with Dirichlet root noise on both sides for per-game variance. Ladder is saturation-proof — winrate stays around 0.5–0.8 regardless of overall policy strength, so the slope reflects true sim-budget value rather than baseline weakness.
