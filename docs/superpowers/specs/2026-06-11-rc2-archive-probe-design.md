# RC2 Phase C — archive-integration probe (MAP-Elites over the generator's genome space)

Registered origin: `experiments/rc2_anchor/RESULTS.md` "Registered next" (PHASE_C_GO, commit
`6284894`): MAP-Elites archive over the generator's genome space with obs_drama as the quality
signal (GE diagnostic-only), interaction_rate + game_length as candidate axes; inherits
challenger eval-count matching, cross-cell blind slates, and periodic full-archive re-eval from
the panel's MAP-Elites seats (`docs/pivot_menu_synthesis_2026-06-10.md` graft 10, candidates
4/5). Required pre-registrations before building: a within-family separation bar on a FRESH
genome sample, and honest-noise sample sizes derived from Phase B's CIs (drama CI half-width
≈ ±0.015 at n=200).

## 1. Problem

Phase B proved obs_drama separates agent-judged quality pods 3× where GE fails — but on a
10-game anchor set where family confounds pod membership (the ABOVE pod has no threshold game;
the BELOW pod is all-threshold). Two questions block archive integration into the evolution
loop and are answerable cheaply (rollouts only, zero PPO):

1. **Within-family discrimination (the confound check):** on fresh generator output, does
   obs_drama vary meaningfully WITHIN families, or is it a family detector? If the latter, a
   drama-quality archive degenerates into family ranking and integration is pointless.
2. **Search value (the integration check):** at matched eval budget, does an archive +
   the existing `MutationOperatorV2` actually climb drama better than random generation?
   This is heritability-under-mutation — the property the evolution loop would exploit.

External-methods note: noise handling follows the noisy-QD literature — MAP-Elites (Mouret &
Clune 2015), archive re-evaluation / Deep Grids (Flageat & Cully 2020), QD-score (Pugh et al.
2016). Challenger eval-count matching + periodic full-archive re-eval are the registered
operationalizations; uniform-over-cells selection is the canonical baseline variant.

## 2. Scope

- **This probe:** Stage 0 (calibration + fresh-sample within-family bar) and Stage 1
  (two-arm archive search probe). No loop changes; `run.py`/`loop.py` untouched. No PPO.
  GE is not computed anywhere (it requires training; declared diagnostic-absent).
- **NOT this probe:** loop integration (only specced on ARCHIVE_GO), cross-cell blind-slate
  agent eval (registered as the Phase D follow-on on ARCHIVE_GO — it is the expensive
  agent-team stage), field_connection/capture_quota genes (not generator-emittable; the
  genome space is the LEGACY generator space, as registered), the hex_rhombus win-graph fix
  and the Frontline rebuild (separate registrations, unaffected).

## 3. Shared machinery

### 3.1 Genome evaluation (one "eval" = the budget unit)

A genome eval runs `metrics.rollout_traces.run_protocol(game, n, base_seed=eval_seed)` (the
locked Phase A harness: half random-pair / half greedy-pair) and aggregates with
`metrics.descriptors.descriptor_row` (locked). Per-genome eval seeds are deterministic and
CONTENT-derived (game_id is uuid4 and run-varying; canonical_hash is not):
`eval_seed = (int(canonical_hash[:16], 16) + 7919 * batch_index) % 2**31`, so identical
runs are bit-reproducible and schedule-invariant. Per-eval wall timeout 180s → genome
marked EVAL_TIMEOUT, excluded, counted; harness/engine exceptions likewise → EVAL_ERROR;
the eval still consumes budget (compute was spent). Pre-eval rejections (quick_reject,
dedup) consume none; each Stage-1 step caps candidate re-draws at 50, then the step is
skipped and counted (skipped steps consume no budget; the arm continues to its full B).

### 3.2 Archive (new module `evolution/qd_archive.py`, fully unit-tested)

- **Cell key:** (family, interaction_bin, length_bin).
  - family = `win_condition.condition_type` ∈ {territory, elimination, connection, threshold}.
  - interaction_rate bins (5), edges pinned from Phase B's observed range [0.08, 0.30]:
    [0, 0.05, 0.12, 0.20, 0.30, 1.0].
  - normalized length = mean(game_length) / win_condition.max_turns, clipped to [0,1];
    bins (5): [0, 0.2, 0.4, 0.6, 0.8, 1.0]. Upper edge inclusive on the last bin.
  - 4 × 5 × 5 = 100 cells.
- **Quality:** obs_drama, stored as the POOLED MEAN over all batches the genome has received,
  with pooled n tracked.
- **Insertion validity guard (registered, applies to every candidate):** non-draw rollouts
  ≥ 50% of the batch AND mean game_length ≥ 6 AND obs_drama is not nan. Invalid candidates
  consume their eval (rollouts were spent) and are counted by reason.
- **Challenger eval-count matching (inherited safeguard):** a challenger whose first-batch
  mean beats the incumbent's pooled mean is topped up in n=50 batches until its pooled n ≥
  the incumbent's pooled n; it replaces the incumbent iff its pooled mean still wins. Top-up
  rollouts are counted separately from the genome-eval budget (reported).
- **Periodic full-archive re-eval (inherited safeguard, the R21-S5 phantom-elite lesson):**
  every 100 genome-evals (i.e. after evals 100, 200, and 300 = final), every elite receives
  one fresh n=50 batch; stored values become the new pooled means. Re-eval never evicts; it
  re-prices. ALL bar computations use post-final-re-eval pooled means, so every surviving
  elite has ≥ 2 independent batches — phantom protection is structural, not a bar.
- **Dedup (R21 S1a):** candidates whose `canonical_hash()` matches any genome previously
  seen by that arm are rejected pre-eval (no budget consumed), counted; 5 re-draw retries.
- **quick_reject:** strict-mode pass required for all candidates (pre-eval, no budget).

## 4. Stage 0 — calibration + fresh sample + within-family bar

1. **CAL (instrument check, the 15-min-probe rule):** re-evaluate reference games
   573562833174 and e1453dac5445 (loaded from their R21 DBs as in Phase B) at n=100, probe
   seeds. CAL passes iff drama(573) − drama(e1453) ≥ 0.15 (Phase B gap 0.256 ± ~0.02; floor
   leaves 5σ headroom at n=100). CAL fail → PROBE_INVALID, stop. Reference rows are
   report-only; they are NEVER inserted into any archive.
2. **Fresh sample:** generate genomes with `GameGeneratorV2` (probe seed stream), strict
   quick_reject + dedup; evaluate each at n=100 until EITHER every family has ≥ 15 valid
   (insertion-guard-passing) genomes AND total valid ≥ 120, OR 160 genomes have been
   evaluated, OR 2000 generation attempts are exhausted. Families still under 15 at the stop
   are UNSAMPLED (excluded from BAR W, reported).
3. **BAR W (within-family separation, the registered gate):** a sampled family is
   drama-LIVE iff P90 − P10 of its genomes' obs_drama point estimates ≥ 0.064
   (= 3 × hw(100); hw(n) = 0.015·√(200/n) from Phase B, so hw(100) ≈ 0.0212). BAR W passes
   iff ≥ 2 sampled families are LIVE. Per-family spreads, generator probability mass of LIVE
   families, and draw/validity attrition are all reported.

BAR W fail → ARCHIVE_KILL: no Stage 1, descriptor redesign required before any archive work
(Frontline rebuild continues in parallel as already registered).

## 5. Stage 1 — two-arm search probe (matched budget)

Both arms start from identical archives initialized with ALL Stage-0 valid genomes (inserted
under §3.2 rules), then receive exactly B = 300 additional genome-evals at n=50:

- **Arm R (random baseline):** each step evaluates a fresh generator genome
  (quick_reject + dedup pre-filtered) and offers it to the archive.
- **Arm M (MAP-Elites):** each step picks a uniformly random filled cell, mutates its elite
  with `MutationOperatorV2` (mutation-only; crossover deferred to integration), pre-filters,
  evaluates, offers to the archive. Every step logs (parent_id, parent pooled drama,
  child_id, child batch drama) for the heritability diagnostic.

The genome-eval count is the matched unit (the search-relevant cost); top-up and re-eval
rollouts are reported per arm. Wall cap 10h for the whole probe → PROBE_INCOMPLETE if hit.
Checkpoint every 25 evals (JSON, resumable).

**BAR H (search value):** mean obs_drama of the TOP-10 elites (global across cells,
post-final-re-eval pooled means) satisfies top10(M) − top10(R) ≥ 0.03 (= hw(50); pooled n of
compared elites is ≥ 100, so the floor is ≥ 4σ on the difference of 10-elite means).

Reported, not binding: coverage per arm, QD-score (sum of elite dramas), per-cell paired
wins on jointly-filled cells, family composition of each arm's top-10 (collapse diagnostic),
re-eval re-pricing magnitudes (phantom diagnostic), all rejection/dedup/timeout counters.

## 6. Decision grammar (to be locked verbatim in the PREREGISTRATION)

- CAL fail → **PROBE_INVALID** (instrument broken at probe n; no verdict).
- BAR W fail → **ARCHIVE_KILL** (drama is a family detector on fresh genomes; descriptor
  redesign before any archive integration).
- BAR W pass ∧ BAR H pass → **ARCHIVE_GO**: register Phase D = cross-cell blind-slate
  agent-team eval of arm M's top elites + the loop-integration spec (swap point
  `run.py:593` scores_map).
- BAR W pass ∧ BAR H fail → **ARCHIVE_NEUTRAL**: archive mechanics validated, no search
  uplift at this budget. Registered next: compute the parent-child drama heritability r from
  arm M's logs (no new compute); if r ≥ 0.3 → one 2×-budget replicate is registered; if
  r < 0.3 → mutation-operator/descriptor work precedes any replicate.
- Any stage incomplete (wall cap, attempt caps, unloadable reference games) →
  **PROBE_INCOMPLETE**: partial tables reported, no verdict token.

## 7. Compute (honest)

~12k rollouts CAL+Stage 0 (160 × 100 + 200) + ~30k Stage 1 arms (2 × 300 × 50) + ~12k
re-evals/top-ups ≈ 55k rollouts ≈ 4–5h wall at Phase B's ~0.27 s/rollout, single process.
Zero PPO, zero training. Build estimate ~3h (archive module + runner + tests, two-stage
review), comparable to Phase A+B.

## 8. Artifacts

- `evolution/qd_archive.py` — archive (binning, insertion, matching, re-eval, persistence).
- `experiments/rc2_archive/PREREGISTRATION.md` — locked before any probe data.
- `experiments/rc2_archive/run_probe.py` — CAL + Stage 0 + Stage 1 + verdict emission, with
  bar-transcription comments and synthetic tests of every verdict branch (Phase B pattern).
- `test_rc2_archive.py` — unit tests: bin edges/boundaries, insertion order-independence,
  matching top-up, pooled-mean bookkeeping, re-eval re-pricing, validity guard, dedup,
  determinism (same seed → identical archive), verdict branches.
- `experiments/rc2_archive/{probe_results.md,probe_results.csv,RESULTS.md}` — outputs.

## 9. Known inputs, not commitments

- Phase B's family-confound caveat (RESULTS §honest-synthesis 3) is what BAR W answers.
- interaction_rate passed Phase B as the cheap-skeptic column; here it is an archive AXIS,
  exactly the registered division of labor (drama = quality, interaction = diversity).
- The R21-S5 elite re-eval lesson and R20's lucky-elite seed bias motivate matching +
  re-eval; both are structural in §3.2, not post-hoc analysis choices.
- mcts_phase1's σ_WR 0.105–0.224 is why no MCTS/PPO fitness column appears in this probe.
