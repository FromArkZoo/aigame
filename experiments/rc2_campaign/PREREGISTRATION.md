# RC2 Campaign — PREREGISTRATION (constants finalized from §0 — pending lock-commit)

Status: **Constants finalized from §0; pending the lock-commit.** v1 was
reviewed by an ultracode adversarial panel (`PANEL_FINDINGS.md`: 53 raw → 15
confirmed under 2-refuter verification, 11 refuted). All 15 confirmed findings
are grafted below, tagged [C#]. Lock gates BOTH satisfied: (a) owner sign-off
received (2026-07-01: TILT re-priced to 0.625; NOISE-NULL floored floor
adopted); (b) the four §0 lock obligations complete — see the §0 status block.
This file is renamed PREREGISTRATION.md and lock-committed pre-data on the
owner's final go.
Design authority: `docs/superpowers/specs/2026-06-12-rc2-campaign-design.md`.
Lineage: Phase C ARCHIVE_GO machinery (`experiments/rc2_archive/`),
planning-gap validations (`experiments/rc2_planning_gap/`), guards
(`rc2_descriptor_v2` RUSH/TILT, `reach_endcause` REACH-v3).

## 0. Lock obligations (pre-data instrument measurements; no campaign data)

**§0 STATUS: COMPLETE (2026-07-01).** All four measured on the anchor roster
(no campaign data); artifacts committed under `experiments/rc2_campaign/`.
Finalized constants flow into §4/§5/§6 below.

- **σ-FILE** [C4] — DONE (`sigma_t1.md`/`.json`): bootstrap of the 24 stored
  per-game T1 outcome cells in `cost_tiering.json` per roster game (B=100k,
  seed 95M). Estimator + e1453 negative-region heteroskedasticity caveat
  named in the file. Result: **σ_max = 0.1016** (S5; roster mean 0.077, vs
  the draft's provisional σ≈0.07). Registered rule σ_diff = σ_max·√2 →
  **CAL-I threshold finalized 0.30 → 0.431** (§5); BAR W-PG floor finalized
  via NOISE-NULL below.
- **NOISE-NULL** [C4] — DONE (`NOISE_NULL.md`/`.json`, `test_noise_null.py`):
  Monte-Carlo noise null for BAR W-PG — 95th percentile of noise-only
  P90−P10 of **floored** T1-PG at each qualifying family's N, at binding
  σ_max (reps=100k, seed 95M). Result: **floor ≈ 0.167 across N** (finalized).
  *Correction adopted at lock:* the draft's provisional "≈0.28 at N=20,
  σ=0.087" was computed on RAW (signed) T1-PG (reproduced: raw = 0.273); §3/§6
  define the bar on FLOORED T1-PG, so the internally-consistent floored floor
  (0.148 at that N/σ) binds — the raw 0.28 reference is superseded.
- **CAL-G** [C2] — DONE (`CAL_G.md`/`.json`): guard revalidation at the
  campaign guard-stage n=24 (12 mirrored TacticalAgent pairs). **RUSH
  confirmed at 0.25** (S1 fires 18/18 decisive ≤6 plies; every control 0.00;
  flip-prob 0.000). **TILT re-priced 0.80 → 0.625 (15/24)** [§4]: 0.80 is
  unresolvable at n=24 (S4/S5 = 19/24 = 0.79, flip-prob 0.42); 0.625 sits ~2σ
  from the S4/S5 targets and the top control d4015 (11/24) → S4/S5 fire
  (flip-prob 0.017), d4015/e1453/s_flip_r2/a1_field_connect silent → **PASS**.
  Binomial flip-probs published in the file.
- **CAL-R** [C8] — DONE (`CAL_R.md`/`.json`): REACH-v3 revalidated at the T1
  instrument (S2 + e1453 at 128v16, n=24, fresh streams 46/47) at the
  re-priced 5/24 threshold (§4). Result: **PASS** — S2 fires 10/24, e1453
  silent 1/24.

## 1. Question

Does PG-driven QD search produce games that escape the 3.5–4.0 agent-eval
plateau? One variable changes from ARCHIVE_GO: quality = planning-gap, not
drama.

## 2. Search space, Stage 0, and arms

- GameGeneratorV2 DEFAULT GameConfig, MutationOperatorV2 DEFAULT
  EvolutionConfig (Phase C verbatim), strict quick_reject everywhere, PLUS
  one registered exclusion: genomes with simultaneous moves are
  quick-rejected (UCT instrument constraint; ~30% of generator space;
  counted and reported).
- **Stage 0 (registered)** [C5]: fresh CAL-disjoint generation sample;
  stop when every sampleable family has ≥ 20 valid genomes AND total valid
  ≥ 150; caps 240 evaluated / 3000 attempts (elimination expected
  unsampleable — Phase C finding — stated, reported as UNSAMPLED). Phase C
  re-draw and attempt-cap rules carry over. **Both arms' archives
  initialize from the same Stage-0 valid set.** BAR W-PG is decided at
  Stage-0 close and preempts the arms (§9 precedence).
- Arms: R = fresh generator genomes; M = uniform-random filled cell →
  mutate elite once → pre-filter → evaluate → offer. **B = 600 evaluated
  genomes per arm** (owner decision; the validated replicate scale).
- **Seed streams** [C1]: base **19** by the established ×{1..5} rule —
  Stage-0/CAL generation 19M; arm R 38M; arm M mutation rng 57M; arm M
  cell-selection rng 76M; **bootstrap 95M** (v1 omitted it). The runner
  executes a hard disjointness assert against ALL recorded streams —
  base-13 and base-17 families (with attempt offsets), anchor streams
  42–47, smoke offsets — and refuses to start on overlap. (v1 registered
  17M/34M/51M/68M as "fresh"; those are exactly Phase C R2's recorded
  streams.)
- Eval seeds content-derived per the Phase C formula:
  eval_seed = (int(canonical_hash()[:16], 16) + 7919 × batch_index) mod 2^31.
- Per-eval wall timeout 180 s → EVAL_TIMEOUT; engine exception →
  EVAL_ERROR; both consume the budget slot, are excluded from archives and
  bars, counted.

## 3. Quality signal — two ledgers, never mixed [C9]

- **T1 ledger** (every genome): T1-PG = seat-balanced score of net-free
  UCT@128 vs UCT@16 − 0.5; n=24 (12 per stream), draws 0.5, max_steps=400,
  anchor_calibration.py conventions. Used for: insertion comparisons,
  challenger fights, eval-count matching — within-instrument only.
- **Full-conv ledger** (elites only): full-convention PG (UCT@256 vs
  UCT@16, n=48), written ONLY at archive-wide re-eval checkpoints — eval
  counts **300/600 per arm (cadence: 2 checkpoints) [AMENDED pre-data by
  BUILD_LOG erratum #13, 2026-07-03: was 150/300/450/600 (4 checkpoints).
  CAL-C measured the checkpoint term at 52% of projected wall (pessimistic
  9.32h vs the 8h cap); the cadence was declared below as a cost choice
  made BEFORE full-conv pricing was measured on generated genomes; owner-
  ratified re-price, B and all instruments unchanged]** (v1's "Phase C
  checkpoints ×2" mislabel corrected — the validated R2 replicate
  re-evaluated every 100; the checkpoint count is a cost choice under
  full-conv pricing, declared as a deviation). An elite lacking a
  full-conv batch at bar time receives one before the bar is computed.
  Read by: top-10 selection, BAR H-PG, slate selection.
- **Quality for insertion/QD = max(T1-PG, 0)** (informative-region rule;
  raw always recorded). Insertion requires STRICT improvement on floored
  T1-PG; 0-vs-0 never displaces (first occupancy still counts coverage).

## 4. Insertion-offer pipeline (in order; each stage veto-on-entry,
budget-consuming, counted by reason)

1. quick_reject (incl. simultaneous exclusion) — pre-evaluation.
2. T1 evaluation (n=24).
3. **Validity guard** [C13] (Phase C transcription, PG era): non-draw T1
   share ≥ 0.50; mean T1 game length ≥ 6 plies; T1-PG non-nan.
4. **Guard stage** [C2] — runs ONLY for genomes whose floored T1-PG beats
   the incumbent cell elite (cost scales with offers, not B): 12 mirrored
   TacticalAgent pairs (n=24), run_probe.py mirrored-seed scheme with
   content-derived base seeds; `rollout_tactical`/TacticalAgent lifted into
   metrics/ as a registered build item. Guards (constants re-priced at
   CAL-G):
   - RUSH: ≥ 25% of decisive tactical games end in ≤ 6 plies (CAL-G
     confirmed — unchanged at n=24).
   - TILT: P1 wins ≥ **62.5%** (15/24) of decisive tactical games (mirrored
     pairs) — **re-priced from 0.80 at CAL-G** (§0): 0.80 is unresolvable at
     n=24 (S4/S5 = 0.79, flip-prob 0.42); 0.625 sits ~2σ from the S4/S5
     targets and the top control d4015.
   - REACH-v3 [C8] (threshold family only): ≥ **5/24** of the genome's own
     T1 games end winner-None (re-priced from 0.25×48 so the validated
     positive S2 sits ≥1σ inside the firing region; **CAL-R validated: PASS**
     — S2 fires 10/24, e1453 silent 1/24).
5. Archive insertion on floored T1-PG strict improvement.

## 5. Pre-campaign CAL (before any search spend)

- CAL-I (instrument): T1-PG on fresh streams (46, 47):
  PG(d4015a646ae3) − PG(S4) ≥ **3 × σ_diff**, with σ_diff = σ_max·√2 =
  **0.1437** (σ_max = 0.1016 from the σ-FILE) → threshold **3·σ_diff = 0.431**
  (finalized; draft provisional was 0.30). Observed separation 0.834 at
  streams 42/43 clears it by 5.8σ_diff. Fail → **PROBE_INVALID**, no campaign.
- CAL-C (cost): 20 fresh genomes (CAL stream) timed end-to-end through the
  FULL per-genome pipeline **including the guard stage and a full-conv
  re-eval** [C2] → projected campaign wall. Projection over the cap →
  re-scoped BEFORE launch (re-registration of B, never a silent change).

## 6. Bars (binding; constants finalized from §0 files — see §0)

- **BAR W-PG** (within-family validity) [C3, C4, C5]: population = Stage-0
  valid genomes' **floored** T1-PG. Qualifying family = ≥ 20 valid at
  Stage-0 close. Per family: LIVE iff P90 − P10 of floored T1-PG ≥ the
  NOISE-NULL 95th-percentile floor at that family's N (finalized floored
  floor ≈ **0.167** across N at binding σ_max; `NOISE_NULL.md` — the draft's
  raw-based 0.28 reference is superseded, see §0). **BAR W passes iff
  ≥ 2 qualifying families are LIVE** (Phase C quantifier; v1's
  any-family-kill would have killed Phase C's own validated replicate).
  Per-family LIVE/DEAD reported; DEAD families' cells are slate-ineligible.
  < 2 qualifying families → PROBE_INCOMPLETE. < 2 LIVE → **ARCHIVE_KILL**.
- **BAR H-PG** (search value): mean floored full-conv PG of the top-10
  elites per arm (full-conv ledger, post-final-checkpoint pooled),
  top10(M) − top10(R) ≥ **0.05**. Either archive < 10 elites → not
  evaluable → PROBE_INCOMPLETE.
  **Saturation contingency** [C7]: R_top10 is reported alongside; if
  R_top10 ≥ **0.40** (the +0.5 ceiling compresses the difference), the
  binding search-value metric switches — registered here, pre-data — to
  paired per-cell wins on jointly filled cells: M strictly better on
  ≥ **60%** of jointly filled cells, ≥ 20 joint cells required (fewer →
  PROBE_INCOMPLETE for this bar). SEARCH_NEUTRAL must not be reachable by
  ceiling arithmetic alone.
- **Slate trigger**: slate runs only on BAR W-PG pass ∧ BAR H-PG pass.
  BAR H-PG fail → **SEARCH_NEUTRAL**; registered next step: parent-child
  heritability on **raw** T1-PG [C14] (Pearson r, parent pooled-at-selection
  vs child first-batch, restricted to parents with floored PG > 0;
  timeout/error children excluded and counted; floored-r reported as
  diagnostic); r ≥ 0.3 → one 2×-budget replicate registered, launched on
  owner confirmation; r < 0.3 → mutation/signal interaction analysis first.
- **SLATE bars** (3 independent blind tmux teams; per-game score = mean of
  the 3 team verdicts [C12]):
  - S-GO-1: ≥ 1 of the top-3 M-elites reaches game score ≥ **4.10**
    (R8-parity, owner decision).
  - S-GO-2 (PG validation, graft-10 binary separation) [C6]: pooled mean
    over verdicts of the top-3 pool (9 verdicts) − pooled mean of the
    contrast-2 pool (6 verdicts) ≥ **+0.4** (~2σ at team-verdict SD 0.38).
    **Minimum-contrast precondition**: if full-PG(top-pool min) −
    full-PG(contrast-pool max) < 0.15 (≈3σ at n=48), declare
    **SEPARATION_UNDERDETERMINED** (reported; the slate verdict then rests
    on S-GO-1 + d4015 validity) — never a silent NO-GO. (v1's top-2 vs
    bottom-2 of an all-elite slate failed its own validation data — the
    blind-seven gives margin +0.015 — and had no contrast by construction.)
  - GO requires S-GO-1 ∧ S-GO-2 (or S-GO-1 ∧ SEPARATION_UNDERDETERMINED
    declared with d4015 in band — reported as **GO-PARTIAL**, loop
    integration registered but gated on one confirmatory slate).
  - Campaign validity: in-slate d4015 game score within **[3.48, 4.18]**;
    outside → **CAMPAIGN_UNRESOLVED** → one cheap 2-team replicate slate;
    never permanent closure.
- **PROBE_INCOMPLETE**: search-phase wall cap **8 h** hit (see salvage,
  §9); either archive < 10 elites; < 2 qualifying families; anchors
  unloadable.

## 7. Slate composition and blinding

- **Composition** [C6, C10]: 7 games = top-3 M-elites by full-conv PG
  + 2 contrast elites (guard-passing M-archive elites from the lowest
  tertile of floored full-conv PG) + d4015a646ae3 (validity anchor) + S3
  (registered carry-in; reported, not binding; excluded from all binding
  pools). Selection order: descending full-conv PG; ties broken
  lexicographically on canonical_hash [C12]. Constraints applied in PG
  order with next-best substitution (all substitutions reported):
  (1) family cap — max 2 of the top-3 per win-condition family;
  (2) near-duplicate screen — skip a candidate iff identical family +
  identical board/topology + descriptor_row distance below the pinned
  floor, or rules-diff limited to komi/max_turns. (v1's "max 1 per cell"
  was dead text — distinct cells do not imply distinct games.)
- **Blinding** [C11, C15]: pack per the rc2_phase_d convention (7 labels,
  registered shuffle seed, per-team verdict files, unblind only after all
  filed), keeping stage3_ab's fairness-perception probe, cross-game
  comparison section, and role win-split logging; play.py help regenerated
  per game's actual action space. Out-of-bounds list registered HERE:
  everything under evaluations/ except the new pack dir; experiments/;
  docs/; analysis*.md; memory files; git metadata. Verdict template
  includes a mandatory recognition-disclosure line ("if you believe you
  can identify this game or recall a prior score, say so and continue");
  the orchestrator greps filed verdicts for identifier strings (d4015,
  Connection Go, S3, run8, …) before unblinding.

## 8. Reported, not binding

Per-arm coverage and QD-score (floored), per-cell paired wins, family
composition of top-10s, guard-veto counts by guard and stage, validity-
guard counts by reason, simultaneous-quick-reject count, raw PG
distributions, re-eval re-pricing magnitudes, heritability r (raw +
floored diagnostic), Stage-0 family table with UNSAMPLED marks, S-GO
substitution log, recognition disclosures, S3 slate read, R_top10, all
counters.

## 9. Decision grammar — precedence chain [C12]

Evaluated strictly in order; exactly one verdict per run:
1. **PROBE_INVALID** (CAL-I fail).
2. **PROBE_INCOMPLETE** (§6 conditions; cap = search-phase wall only.
   Salvage: if cap hits after BOTH arms passed the **300-eval checkpoint
   [erratum #13: was 450 — the penultimate registered checkpoint at the
   amended §3 cadence]**, bars are evaluated at the last mutual checkpoint
   with B_effective reported; else PROBE_INCOMPLETE).
3. **ARCHIVE_KILL** (BAR W-PG, decided at Stage-0 close — preempts arms).
4. **SEARCH_NEUTRAL** (BAR H-PG fail, incl. saturation-switched metric).
5. Slate verdicts: **GO / GO-PARTIAL / NO-GO / CAMPAIGN_UNRESOLVED /
   SLATE_INCOMPLETE** (slate not completed: its own handling, never the
   search-phase cap; one relaunch attempt then SLATE_INCOMPLETE recorded).

Consequences: GO → register loop integration at run.py:593 scores_map.
NO-GO (valid instrument) → PG returns to analysis with which/why;
periodic-agent-slates-only becomes the registered selection fallback.
No archive re-registration (house grammar).

## 10. Build and audit obligations

Runner applies bars via a pure `decide_verdict` over the precedence chain
with ALL branches synthetically tested pre-run; bars transcribed as
constants from the §0 lock files; prereg locked pre-data; post-lock code
changes must be pre-data and review-logged (Phase C audit pattern);
checkpointing + unbuffered logs. Build items: guard stage lift into
metrics/ [C2]; two-ledger store [C9]; slate builder with constraints and
substitution log [C10]; blind-pack generator per §7 [C15]; disjointness
assert [C1].

## Grafts applied (panel finding → section)

C1 seeds §2 · C2 guard stage §0/§4/§5/§10 · C3 BAR W quantifier §6 ·
C4 σ provenance + noise null §0/§5/§6 · C5 Stage 0 §2/§6/§9 ·
C6 slate recomposition + S-GO-2 §6/§7 · C7 BAR H saturation §6 ·
C8 REACH-v3 re-pricing §0/§4 · C9 two ledgers §3 · C10 slate diversity §7 ·
C11 blinding out-of-bounds §7 · C12 precedence/estimators §6/§9 ·
C13 validity guard §4 · C14 heritability inputs §6 · C15 pack convention §7.
