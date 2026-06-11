# RC2 anchor probe — pre-registration (locked before any probe data)

Spec: docs/superpowers/specs/2026-06-11-rc2-selection-layer-design.md (commit 0453e60).
Question: do cheap observer-based descriptor signals separate agent-judged quality
pods where GE provably does not? Zero PPO; rollouts only.

---

## Anchor set (every game with an agent-team verdict; pod rule applied to means)

Pod boundaries: ABOVE = agent mean >= 3.9; BUFFER = 3.7 < mean < 3.9 (reported,
excluded from binary separation bars); BELOW = mean <= 3.7.

### ABOVE pod (agent mean >= 3.9)

| Game ID | Source | Agent mean | GE | Loadability |
|---|---|---|---|---|
| d4015a646ae3 | genesis_v2_run8.db | 4.10 | — | R8 DB located on disk; if unloadable at probe time the probe runs without it and the ABOVE pod is s_flip_r2 + a1_field_connect only (registered fallback) |
| s_flip_r2 | experiments/siege/games/calibrated/s_flip_r2.json | 4.10 | — | siege JSON on disk |
| a1_field_connect | experiments/siege/games/a1_field_connect.json | 3.90 | — | siege JSON on disk |

### BUFFER (3.7 < mean < 3.9, reported but excluded from binary separation bars)

| Game ID | Source DB | Agent mean | GE | Loadability |
|---|---|---|---|---|
| d995cf010504 | genesis_v2_run21_carpet.db | 3.78 | 0.103 | run21 carpet DB on disk |
| 573562833174 | genesis_v2_run21_grid.db | 3.78 | 0.002 | run21 grid DB on disk |
| b12ff78f1c1d | genesis_v2_run21_grid.db | 3.72 | 0.099 | run21 grid DB on disk |

Note on b12ff78f1c1d: mean 3.72 is strictly > 3.70 → BUFFER by the pod
boundary rule, not BELOW. Excluded from binary bars alongside d995 and 573.

### BELOW pod (mean <= 3.7)

| Game ID | Source DB | Agent mean | GE | Loadability |
|---|---|---|---|---|
| e52e8889517a | genesis_v2_run21_menger.db | 3.68 | 0.138 | run21 menger DB on disk |
| bfd1bb7ced76 | genesis_v2_run21_menger.db | 3.68 | 0.126 | run21 menger DB on disk |
| e1453dac5445 | genesis_v2_run21_menger.db | 3.66 | 0.177 (GE-top) | run21 menger DB on disk |
| 1fea3357dca4 | genesis_v2_run21_menger.db | 3.50 | 0.118 | run21 menger DB on disk |

All agent means taken from evaluations/run21/SUMMARY.md per-game table (mean of
5 team scores; all values are unambiguous single point estimates in that table).

### Secondary check (binding — GE-inversion pair)

For any PASSING candidate: signal(573562833174) > signal(e1453dac5445).

Rationale: 573562833174 is GE-bottom (0.002) yet agent-tied-1st at 3.78;
e1453dac5445 is GE-top (0.177) yet agent-ranked 6/7 at 3.66. Any descriptor
tracking agent-judged depth must rank these correctly.

---

## Protocol

n=200 rollouts/game (100 random-pair + 100 greedy-pair), base_seed=11, the
anchor_drama seeding scheme verbatim (random seed: base_seed * 10_000 + i;
greedy seed: base_seed * 29 + 31 * i). Observer field r=2, strength=1.0,
decay=0.5, margin=0. Draws skipped and counted. Per-game bootstrap CI
(1000 resamples).

---

## Candidate columns

1. **obs_drama** (primary). Per-rollout: winner-behindness series over per-ply
   observer-field-based progress traces. For threshold-family games: observer
   analogue = sum of sign-adjusted observer field over owned cells / threshold
   (declared approximation; exact anchor_drama threshold_progress uses engine
   board_values, which are zero for prop_type='none'; documented deviation).
   For connection/field-family games: obs_progress_span fraction along the
   game's target axis. Aggregated as mean over non-draw rollouts; draws
   excluded and counted.

2. **blend** = sqrt(norm(obs_drama) × norm(obs_lead_changes)); min-max norms
   computed over the full anchor set after all games are evaluated (declared:
   ranking test only, not absolute scale).

3. **interaction_rate** (cheap-skeptic control). Per-rollout: mean of
   (captures_total / max(1, plies)) and contact fraction (fraction of plies
   where the most recent placement is within graph distance 2 of an enemy
   stone, derived from consecutive ownership snapshots).

4. **go_essence** from the source DB scores table (R21 games only; '—' for
   d4015a646ae3, s_flip_r2, a1_field_connect) — expected-FAIL control column.

---

## Bars (binary separation, point estimates; CIs reported, fragility flagged)

The ABOVE pod is {d4015a646ae3, s_flip_r2, a1_field_connect}.
The BELOW pod is {e52e8889517a, bfd1bb7ced76, e1453dac5445, 1fea3357dca4}.
BUFFER games are excluded from bars.

A candidate PASSES iff ALL four conditions hold:

1. mean(ABOVE) > mean(BELOW) for that candidate column.
2. At most 1 boundary inversion: count of BELOW games scoring above the lowest
   ABOVE-pod game (min of the three ABOVE values) is <= 1.
3. e1453dac5445 does not score above any ABOVE-pod game for that column.
4. Secondary GE-inversion check: signal(573562833174) > signal(e1453dac5445)
   (573 is BUFFER; the secondary check is evaluated separately from the bars).

CIs reported alongside point estimates. If a bar passes by point estimate but
its 95% CI overlaps the separation threshold, flagged as FRAGILE (not a gate).

---

## Decision grammar (locked)

- Candidate 1 (obs_drama) or 2 (blend) PASS
  → PHASE_C_GO: register the archive-integration probe; obs_drama or blend
  is the primary archive-axis descriptor.

- Only candidate 3 (interaction_rate) PASS
  → PHASE_C_GO_INTERACTION: interaction_rate primary; obs_drama demoted to
  archive-axis-only.

- None of candidates 1, 2, 3 PASS
  → RC2_KILL: descriptor redesign; Frontline becomes the sole active
  registered thread.

- GE column (candidate 4) passing (unexpected)
  → flagged as GE_CONTROL_PASSED for honest synthesis; decision grammar above
  is NOT altered by this outcome.

Not altered after data.

---

## Pre-registration audit note

Committed before any rollout data was collected. Pod boundaries and all bars
derived solely from:
- evaluations/run21/SUMMARY.md (R21 per-game agent means)
- experiments/siege/RESULTS.md §5 (s_flip_r2 4.10, a1_field_connect 3.90)
- evaluations/r8_replay/SUMMARY.md (d4015a646ae3 4.10)
No probe data was consulted.

Buffer-pod refinement (spec amendment): the plan's §4 pod table listed 573
in ABOVE; this prereg supersedes with the buffer rule because 573's agent mean
(3.78) sits below A1 (3.90) — forcing it into ABOVE would let the buffer
dominate the bars. Committed before any data; registration discipline holds.
