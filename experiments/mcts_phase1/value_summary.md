# Phase-1 MCTS evaluator — results

Per-game empirical σ across reruns of MCTS@N-vs-ladder winrate, at sim counts [16, 64, 256].

## Per-(game, sim_count) winrate

| Substrate | Dim | Game | Sims | n_reruns | mean WR | σ WR | min | max |
|---|---|---|---:|---:|---:|---:|---:|---:|
| triangle | 1.585 | `558be82199a8` | 16 | 1 | 0.875 | 0.000 | 0.875 | 0.875 |
| triangle | 1.585 | `558be82199a8` | 64 | 1 | 0.875 | 0.000 | 0.875 | 0.875 |
| triangle | 1.585 | `558be82199a8` | 256 | 1 | 0.750 | 0.000 | 0.750 | 0.750 |

## Scaling-slope per game (N=16 → N=256, 4.0 doublings)

Slope = (WR@max − WR@min) / log2(max/min). σ across reruns is the noise floor of this candidate fitness metric.

| Substrate | Dim | Game | n_reruns | mean slope | σ slope | mean Δ WR |
|---|---|---|---:|---:|---:|---:|
| triangle | 1.585 | `558be82199a8` | 1 | -0.0312 | 0.0000 | -0.125 |

## Comparison against GE noise floor

From `experiments/r18_noise_floor/noise_floor_summary.md`, the production-stack GE σ floor is **0.05–0.09** on top games (menger 0.091, carpet 0.072, triangle 0.056). The Phase-1 σ columns above measure noise on a *different* metric: winrate in [0, 1] and slope in [-0.25, 0.25] (max), vs GE in roughly [0, 0.4]. Direct numeric comparison is approximate; the meaningful signal is whether **slope σ < 0.03** (roughly a third of GE σ on its own scale).

**Decision criteria for Phase 2 (OpenSpiel / expanded ladder):**
- slope σ ≤ 0.02 on all 5 substrates: scaling slope is a viable   GE replacement → Phase 2 worth doing.
- slope σ in 0.02–0.05: marginal → Phase 2 only on substrates   that look promising.
- slope σ > 0.05 broadly: Phase 1 MCTS doesn't beat GE → hold   off on OpenSpiel and revisit metric design instead.

**Opponent.** Configured as `ladder`. For `ladder` mode the weak side is MCTS@(N/ladder_ratio) using the same nets, with Dirichlet root noise on both sides for per-game variance. Ladder is saturation-proof — winrate stays around 0.5–0.8 regardless of overall policy strength, so the slope reflects true sim-budget value rather than baseline weakness.
