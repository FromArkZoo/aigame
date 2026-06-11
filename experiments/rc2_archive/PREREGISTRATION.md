# RC2 Phase C archive-integration probe — pre-registration (locked before any probe data)

Spec: docs/superpowers/specs/2026-06-11-rc2-archive-probe-design.md (commit 02483de + the
canonical-hash seeding amendment committed with this file).
Registered origin: experiments/rc2_anchor/RESULTS.md "Registered next" (PHASE_C_GO).
Questions: (W) does obs_drama discriminate WITHIN families on fresh generator output, or is
it a family detector? (H) at matched eval budget, does a MAP-Elites archive + the existing
mutation operator climb drama better than random generation? Zero PPO; rollouts only; GE is
not computed anywhere in this probe.

---

## Protocol constants (all pinned)

- base_seed = 13.
- Seed streams: Stage-0 generation attempt i → generate_game(seed = 13_000_000 + i);
  arm R candidate step-attempts → generate_game(seed = 26_000_000 + j) with j a global
  attempt counter; arm M mutation rng = np.random.default_rng(39_000_000); arm M cell
  selection rng = np.random.default_rng(52_000_000); bootstrap rng (reports only) =
  np.random.default_rng(65_000_000).
- Genome eval = metrics.rollout_traces.run_protocol (locked Phase A harness) aggregated by
  metrics.descriptors.descriptor_row (locked). Eval seeds are content-derived:
  eval_seed = (int(canonical_hash()[:16], 16) + 7919 × batch_index) mod 2^31, batch_index
  counting all batches that genome has ever received (init batch 0, then top-ups/re-evals).
- Batch sizes: Stage 0 and CAL n=100; all Stage-1 batches (candidate, top-up, re-eval) n=50.
- Noise model (from Phase B, the registered source): hw(n) = 0.015 × sqrt(200/n);
  hw(100) ≈ 0.0212, hw(50) = 0.030.
- Genome space: GameGeneratorV2 with DEFAULT GameConfig (topology_types grid/torus/hex/
  moore/sierpinski, dims 2–6, max_total_cells 64, movement 0.3, CA 0.2, simultaneous 0.30);
  MutationOperatorV2 with DEFAULT EvolutionConfig. Strict quick_reject required everywhere.
- Per-eval wall timeout 180 s → EVAL_TIMEOUT; harness/engine exception → EVAL_ERROR. Both
  consume the eval's budget slot, are excluded from archives/bars, and are counted by
  reason. Pre-eval rejections (quick_reject fail, canonical-hash duplicate) consume no
  budget; per-step candidate re-draw cap 50, then the step is skipped (counted; skipped
  steps consume no budget).
- Global wall cap 10 h → PROBE_INCOMPLETE. Checkpoint every 25 evals (resumable).

## Archive mechanics (identical for both arms; the genome SOURCE is the only difference)

- Cell key (family, interaction_bin, length_bin):
  family = win_condition.condition_type ∈ {territory, elimination, connection, threshold};
  interaction_rate bin edges [0, 0.05, 0.12, 0.20, 0.30, 1.0] (5 bins; values > 1.0 clamp
  into the top bin); normalized length = mean game_length / win_condition.max_turns clipped
  to [0,1], bin edges [0, 0.2, 0.4, 0.6, 0.8, 1.0] (5 bins; last bin upper-inclusive).
  100 cells total.
- Quality = obs_drama as the pooled mean over all batches received (pooled n tracked).
- Insertion validity guard: non-draw rollouts ≥ 50% of the batch AND mean game_length ≥ 6
  AND obs_drama not nan; invalid candidates consume budget and are counted by reason.
- Challenger eval-count matching: challenger first-batch mean must beat the incumbent's
  pooled mean; then the challenger is topped up in n=50 batches until challenger pooled n ≥
  incumbent pooled n; replacement iff the challenger's pooled mean still beats the
  incumbent's pooled mean. Top-up rollouts counted separately (not genome-eval budget).
- Periodic full-archive re-eval: after genome-evals 100, 200, 300 (final), every elite gets
  one fresh n=50 batch; stored value = new pooled mean. Re-eval never evicts. ALL bar
  computations use post-final-re-eval pooled means.
- Dedup: canonical_hash duplicates (vs everything previously seen by that arm, including
  Stage-0 candidates) rejected pre-eval.

## Stage CAL (instrument check; reference rows never enter any archive)

Load 573562833174 (genesis_v2_run21_grid.db) and e1453dac5445 (genesis_v2_run21_menger.db)
exactly as Phase B did; evaluate each at n=100 with this probe's content-derived seeds.

- **CAL bar:** obs_drama(573562833174) − obs_drama(e1453dac5445) ≥ 0.15 (point estimates).
- CAL fail → PROBE_INVALID (no verdict). Either reference unloadable → PROBE_INCOMPLETE.

## Stage 0 (fresh sample + BAR W)

Generate from the Stage-0 seed stream with strict quick_reject + dedup; evaluate each
accepted genome at n=100; stop when EITHER (every family has ≥ 15 VALID genomes AND total
VALID ≥ 120) OR 160 genomes have been evaluated OR 2000 generation attempts are exhausted.
VALID = passes the insertion validity guard. Families with < 15 VALID genomes at stop are
UNSAMPLED (excluded from BAR W, reported).

- **BAR W:** a sampled family is LIVE iff P90 − P10 of its VALID genomes' obs_drama point
  estimates ≥ 0.064 (= 3 × hw(100); percentiles via numpy default linear interpolation).
  BAR W passes iff ≥ 2 sampled families are LIVE.
- BAR W fail → ARCHIVE_KILL; Stage 1 does not run.
- Fewer than 2 families sampled at all → PROBE_INCOMPLETE (grammar cannot evaluate).

## Stage 1 (two arms, matched budget)

Both arms initialize their archive with ALL Stage-0 VALID genomes (insertion rules above,
same order), then receive exactly B = 300 genome-evals at n=50:

- Arm R: fresh generator genomes from the arm-R seed stream.
- Arm M: uniform-random filled cell → mutate that cell's elite once with MutationOperatorV2
  (mutation only, no crossover) → pre-filter → evaluate → offer. Per-step log of
  (parent canonical_hash, parent pooled drama at selection, child canonical_hash, child
  first-batch drama) for the heritability diagnostic.

- **BAR H:** mean obs_drama of the top-10 elites per arm (global across cells,
  post-final-re-eval pooled means) satisfies top10(M) − top10(R) ≥ 0.03 (= hw(50)). If
  either final archive holds fewer than 10 elites, BAR H is not evaluable →
  PROBE_INCOMPLETE.

Reported, not binding: per-arm coverage, QD-score (sum of elite pooled dramas), per-cell
paired wins on jointly filled cells, family composition of each top-10, re-eval re-pricing
magnitudes, parent-child heritability r (Pearson, arm-M log), all counters (dedup,
quick_reject, validity, timeout/error, skipped steps, top-up/re-eval rollouts).

## Decision grammar (locked; applied verbatim by the runner)

- CAL bar fail → **PROBE_INVALID**.
- BAR W fail → **ARCHIVE_KILL** (descriptor redesign precedes any archive integration;
  Frontline rebuild continues in parallel as already registered).
- BAR W pass ∧ BAR H pass → **ARCHIVE_GO** (register Phase D: cross-cell blind-slate
  agent-team eval of arm M top elites + loop-integration spec at run.py:593 scores_map).
- BAR W pass ∧ BAR H fail → **ARCHIVE_NEUTRAL**. Registered next step: heritability r from
  the arm-M log (no new compute); r ≥ 0.3 → one 2×-budget replicate is registered;
  r < 0.3 → mutation-operator/descriptor work precedes any replicate.
- Wall cap hit, attempt caps exhausted before quotas, unloadable reference games, < 2
  sampled families, or either archive < 10 elites → **PROBE_INCOMPLETE**: partial tables,
  no verdict token.

GE does not appear in this probe; there is no GE column to pass or fail.

## Pre-registration audit note

Committed before any probe data. Bars derive solely from: Phase B's published CIs
(experiments/rc2_anchor/probe_results.md: hw ≈ ±0.015 at n=200; 573/e1453 gap 0.256), the
Phase B family-confound caveat (RESULTS.md honest-synthesis §3), and the registered
safeguards (pivot_menu_synthesis graft 10). No fresh-genome drama values were observed
before this lock; harness smoke tests during the build use seed streams disjoint from the
probe streams above and their drama values do not inform bars. Synthetic tests of every
verdict branch run before the probe (Phase B pattern).
