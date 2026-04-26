# R17 balance preflight — findings

**Date**: 2026-04-26
**Question**: Does `frac_C_fractal` (sierpinski + alt + surround + connection) need komi before R17 kickoff? Pair C teams flagged Δ Balance −0.20 in the 5-team fractal-spike eval.

**Answer**: No. Self-play probes show the game is balanced under both random and greedy regimes at 300 episodes per regime. Ship as-is.

## Probe results

| Game            | Regime | Decisive | P1 winrate | 95% CI Wilson    | Verdict   |
|-----------------|--------|----------|------------|------------------|-----------|
| frac_C_fractal  | random | 221/300  | 53.8%      | [47.3%, 60.3%]   | balanced  |
| frac_C_fractal  | greedy | 300/300  | 50.7%      | [45.0%, 56.3%]   | balanced  |
| frac_C_control  | random | 235/300  | 47.2%      | [40.9%, 53.6%]   | balanced  |
| frac_C_control  | greedy | 300/300  | 50.3%      | [44.7%, 56.0%]   | balanced  |

Fractal − control delta (P1 winrate): random +6.6%, greedy +0.3%.

## Why this disagrees with the human eval

Human eval (5 teams) reported Δ Balance −0.20 (where 0 is balanced, scale −2 to +2). That's a small but non-zero P1 lean. Possible reasons the mechanical probe doesn't see it:

1. **Skill-level mismatch**. Greedy is a 1-ply densify heuristic; humans played multi-ply. Higher-skill play could surface a bias the heuristic flattens. R15 documented this for Moore (random 13/16/1 looks balanced; greedy 20/20 P1 was lopsided), but the inverse is also possible: greedy converges to a balanced equilibrium that humans deviate from.
2. **Subjective scoring**. −0.20 across 5 teams is one team rating it −1 and four rating 0. That's noise within the scoring resolution.
3. **Short game vs long game**. Probes use the game's `max_turns` (50). Some Pair C eval games may have run shorter or longer, weighting different phases.

Decision: trust the mechanical probe — at 300 episodes both regimes give CIs centred on 50% with ±5pp width. If R17 produces a Sierpinski champion that exhibits seat bias under PPO training (visible in the seat-balance metric), that's our second checkpoint and we can intervene then.

## Sanity check at 100 episodes

Initial 100-episode probe showed fractal random P1 at 64.3% (BORDERLINE), but the CI was [52.6%, 74.5%] — wide, only 70 decisive. 300 episodes brought it to 53.8% with [47.3%, 60.3%]. The 100-episode result was sampling noise.

## What this didn't test

- **PPO-trained agents** on `frac_C_fractal`. The mechanical probes are pre-training. The R17 trainer's seat-balance probe will give us trained-agent winrate during evolutionary scoring.
- **Long-axis bias from substrate**. The fractal has 4 degree-4 cells (corners of the central 3×3 hole region). Humans flagged "forced anchor competition." Greedy with 1-ply lookahead may not capture multi-move anchor play.

If the R17 evolutionary run produces a Sierpinski-based winner with seat-balance < 0.8, revisit komi as a post-evolution patch on the champion rather than a pre-flight on the seed.
