# RC2 selection layer — phase A/B design (observer field + anchor probe)

Registered origin: `experiments/siege/PREREGISTRATION.md` "Registered follow-on" + `docs/pivot_menu_synthesis_2026-06-10.md` graft 10. Fires regardless of the SIEGE outcome (which was NO-GO; see `experiments/siege/RESULTS.md` §7). GE stays diagnostic-only throughout.

## 1. Problem

GE anti-correlates with agent-judged depth at the extremes (R21: GE-top ranked 6/7, GE-bottom tied 1st) and its dominant noise source is the 3-sample non_triviality estimator (variance share 0.450, `analysis_post_r21.md`). The QD pivot candidates both died at the panel screen on one verified code fact: `generator_v2.py:209-228` forces `prop_type='none'` for every non-threshold win condition, so `board_values` stays zero and every field-based behavior descriptor (controller_signs/control_flip_rate, controlled_sets, progress_diff_field, maker_progress_span) is structurally dead for most of the genome space. No selection-layer work is meaningful until descriptors are defined for ALL genomes.

New asset since the panel: the per-role winner-behindness drama signal is **anchor-validated** (SIEGE Stage 1.5: ranks the R21 extremes opposite to GE and aligned with agent judgment — 573=0.177 top, e1453=0.046 bottom, n=200, DRAMA_ANCHORED).

## 2. Scope of THIS workstream (phases A + B only)

- **Phase A — observer field + descriptor library** (instrumentation; no selection change, no archive).
- **Phase B — pre-registered anchor probe**: do descriptor-derived signals separate the known agent-judged quality pods? Cheap (rollouts only, zero PPO). KILL gate before any archive machinery.
- **Phase C (NOT this build)**: MAP-Elites archive integration into the evolution loop — only registered if B passes, inheriting challenger eval-count matching, cross-cell blind slates, periodic full-archive re-eval from the panel's MAP-Elites seats.

## 3. Phase A — measurement-only observer field

`metrics/observer_field.py` (new; engine-adjacent but NOT inside engine_v2.py):

```python
def observer_field(topo, board_owners, radius=2, strength=1.0, decay=0.5) -> np.ndarray
```

- Pure function over `(topo, board_owners)`; reuses `engine_v2._influence_kernels` (cache shared); same ±100 clip; NEVER written to engine state, never read by legality/wins/observations. Default params = the validated FC field (r=2/s=1.0/d=0.5).
- Parity invariant (the core test): for any `prop_type='influence'` game whose propagation params equal the observer defaults, `observer_field(topo, board_owners)` must be byte-equal to the engine's `_recompute_field()` result. For `prop_type='none'` games it must be non-zero whenever stones exist, and the engine's own `board_values` must remain zero (no leakage — assert engine state unchanged after measurement).
- Observer-based descriptor library `metrics/descriptors.py`, all computed from per-ply rollout traces (policy-agnostic; no PPO):
  - `obs_control_flip_rate` — controller_signs/count_controller_changes on the observer field (margin 0).
  - `obs_lead_changes` — count_lead_changes on the observer progress differential (largest-component span diff, both players).
  - `obs_drama` — winner_behindness on per-player observer progress traces (the SIEGE-validated formulation, generalized: connection-family progress = largest controlled-component span; threshold-family = effective score/threshold as in anchor_drama; draws skipped).
  - `interaction_rate` — captures per game (prop-agnostic, from piece-count drops) + fraction of plies within graph-distance 2 of an enemy stone (contact tempo).
  - `decisiveness_margin`, `game_length` — carried through for archive axes later; NOT candidate fitness.
- Rollout harness: reuse anchor_drama's random+greedy half-and-half protocol verbatim (seeded, n configurable), factored into `metrics/rollout_traces.py` so anchor_drama and Phase B share one implementation (anchor_drama is NOT modified in this build; consolidation is a later cleanup).

## 4. Phase B — anchor probe (pre-registered before any probe data)

**Question:** does a cheap, observer-based signal separate games agents judged deep from plateau games — where GE provably does not?

**Anchor set (every game with an agent-team verdict on the 1–10 scale):**

| pod | games (agent mean) |
|---|---|
| ABOVE (≥ 4.0) | R8 anchor `d4015a646ae3` (4.10); s_flip_r2 (4.10); a1_field_connect (3.90 — boundary, assigned ABOVE as the blind-preferred reference); 573562833174 (R21 tied-1st) |
| BELOW (plateau, ≤ 3.7-class) | e1453dac5445 (R21 GE-top, agent 6/7) + the remaining R21 slate games with agent means below 3.8 (exact list pinned from `evaluations/run21/SUMMARY.md` at prereg time) |

**Candidate signals (each a separate pre-registered column; computed at n=200 rollouts/game, seed 11, random+greedy halves):**
1. `obs_drama` alone (primary — already 4-game-validated).
2. `obs_drama × obs_lead_changes` blend (geometric mean of min-max-normalized values; normalization bounds pinned at prereg from the anchor set itself — declared, since this is a ranking test not an absolute scale).
3. `interaction_rate` alone (cheap-skeptic column: if raw contact explains the pods, drama adds nothing).
4. GE (diagnostic column, expected to FAIL — the control).

**Bars (binary separation, no cross-campaign Spearman):**
- PASS for a candidate iff: pod means separated with the ABOVE pod higher, AND at most 1 boundary inversion (one BELOW game above the lowest ABOVE game), AND e1453 is NOT ranked above any ABOVE-pod game.
- Probe verdict: GO for Phase C iff candidate 1 or 2 PASSES. If only 3 passes → interaction_rate becomes the registered primary and drama is demoted to archive-axis-only. If none pass → KILL: descriptor redesign required before any archive work; report and stop.
- Noise: per-game bootstrap CI (1000 resamples over rollouts) reported for every column; a PASS with overlapping pod CIs is flagged PASS-FRAGILE (still a pass — bars are on point estimates, fragility informs Phase C sample sizes).

**Cost:** ~10–12 anchor games × n=200 engine rollouts ≈ anchor_drama scale (~6 min/game) → under ~90 minutes, zero PPO.

## 5. Engine/loop changes in this build

NONE. The evolution loop, GE scorer, and generator gate are untouched. The selection-signal swap point (`run.py:593` scores_map) is documented for Phase C but not exercised.

## 6. Decision grammar (locked at prereg commit)

- Candidate-1-or-2 PASS → register Phase C (archive integration probe) as next.
- Only-candidate-3 PASS → register Phase C with interaction_rate primary.
- All FAIL → RC2 returns to descriptor design; Frontline rebuild becomes the sole active registered thread.
- GE column PASSING (unexpected) → flag for honest synthesis; does not change the above.

## 7. Known inputs, not commitments

- The hex_rhombus win-graph asymmetry (SIEGE RESULTS §5) — engine fix candidate, separate registration.
- Per-role tvr floors for asymmetric families — irrelevant here (no training in this build).
- mcts_phase1's σ_WR 0.105–0.224 evidence — why no MCTS/PPO-based fitness column is included in Phase B.
