# RC2 Campaign — design spec

Date: 2026-06-12. Status: owner-approved design (four owner decisions recorded
below); feeds `experiments/rc2_campaign/PREREGISTRATION_DRAFT.md`, which is
ultracode-panel-reviewed BEFORE locking. Nothing runs until the prereg locks.

## Question

Does planning-gap-driven QD search produce games that escape the 3.5–4.0
agent-eval plateau? This is the first campaign run with a quality signal that
passed both registered validations (closeness-confound pair gate AND
blind-seven range check — `experiments/rc2_planning_gap/`), after GE, two
drama variants, and naive learnability all failed. Exactly one variable
changes from the ARCHIVE_GO configuration (quality: drama → PG), so a failure
is attributable.

## Owner decisions (recorded 2026-06-12)

1. **Success bar: R8-parity.** GO iff ≥1 archive elite reaches blind team
   mean ≥ 4.10 AND PG-rank binarily separates agent-judged top from bottom
   (graft-10 formulation, not Spearman).
2. **Budget: B=600 per arm** (the validated Phase-C replicate scale), hard
   wall cap registered alongside.
3. **Slate: one end-of-campaign slate, 3 independent blind tmux teams**,
   ~7 games, blind-packed per the stage3_ab convention.
4. **Maximand: drop-in swap.** Phase C archive machinery verbatim; T1-PG
   replaces drama as quality; no other machinery change.

## Architecture

- **Search space**: GameGeneratorV2 DEFAULT config and MutationOperatorV2
  DEFAULT, as in Phase C — with one registered scope exclusion:
  **simultaneous-move genomes are quick-rejected** (~30% of generator space;
  the UCT instrument cannot evaluate them). Elimination family remains under
  the existing validity guards (known rollout-degenerate as generated —
  Phase C finding).
- **Archive**: Phase C verbatim — `metrics.descriptors.descriptor_row` cells,
  dedup, quick_reject, validity guards, per-eval timeout, content-derived
  eval seeds, re-eval noise pricing, challenger eval-count matching, M
  (archive+mutate) vs R (fresh generator) arms.
- **Quality**: `max(PG_T1, 0)` — T1 screening convention (net-free UCT
  128v16, n=24 seat-balanced, draws 0.5; `cost_tiering.py` ADOPT_T1).
  Flooring encodes the registered informative-region rule (ordering among
  negative-PG games is rollout-model noise). Raw values always recorded.
  Insertion requires strict improvement on floored PG.
- **Elite re-evals**: full-convention PG (256v16, n=48) at scaled Phase-C
  checkpoints, replacing the drama re-eval ladder.
- **Insertion guards (veto, never deletion)**: RUSH ≥ 0.25 and TILT ≥ 0.80
  from the descriptor tactical rollouts the pipeline already runs
  (descriptor-v2 validated constants); REACH-v3 draw-share ≥ 0.25 from the
  genome's own T1 games (threshold family, validated on fresh streams;
  zero extra cost).

## Pre-campaign CAL (before any search spend)

(a) Instrument check: T1-PG on fresh seed streams separates d4015 from S4 by
≥ 0.30 (3× the difference noise σ_diff ≈ 0.10, from measured σ(T1,n=24) ≈
0.07; observed separation 0.834 at streams 42/43). (b) Cost calibration: ~20 fresh genomes → per-genome cost; projected
campaign must fit the wall cap or the campaign is re-scoped BEFORE launch.
CAL fail → PROBE_INVALID, no campaign.

## Bars and decision grammar (constants pinned in the prereg draft)

- **BAR W-PG** (within-family validity): within-family T1-PG spread must
  exceed 3× measurement noise in all sampled families. Fail → ARCHIVE_KILL.
- **BAR H-PG** (search value): top-10 mean floored full-conv PG, M − R ≥
  floor derived from measured T1/full σ. Coverage, QD-score, per-cell wins
  reported, not binding. Fail → SEARCH_NEUTRAL with the Phase-C heritability
  trigger (parent-child PG r ≥ 0.3 → one 2×-budget replicate registered,
  launched on owner confirmation).
- **Slate runs only on BAR W ∧ BAR H pass** (token discipline).
- **Slate bars**: GO iff ≥1 M-elite team mean ≥ 4.10 AND binary separation
  (pooled mean of top-2-by-PG slate elites exceeds bottom-2-by-PG by a
  pinned margin). In-slate d4015 outside its validity band →
  CAMPAIGN_UNRESOLVED → cheap 2-team replicate slate, never closure.
- **PROBE_INCOMPLETE**: wall cap hit, either archive < 10 elites, < 2
  families sampled, unloadable anchors.

## Slate composition

Top-5 M-arm elites by full-convention PG, cross-cell (max 1 per cell), plus
d4015 (campaign-validity anchor) and S3 (registered carry-in from the
blind-seven validation — its PG-vs-agent-depth question; reported, not
binding). 3 blind tmux teams → 21 verdicts.

## Verdict consequences

- GO → register loop integration at the Phase-C-named `run.py:593 scores_map`
  hook.
- NO-GO with valid instrument → PG returns to analysis with which/why;
  periodic-agent-slates-only becomes the registered selection fallback.
- All KILL/NEUTRAL/UNRESOLVED branches per the grammar above; no archive
  re-registration (house grammar).

## Build shape and cost

`experiments/rc2_campaign/`: PREREGISTRATION.md (locked pre-data after the
ultracode panel), runner with bars as constants applied by a pure
`decide_verdict` (all branches synthetically tested pre-run, house style),
blind-pack tooling reused from stage3_ab. Estimated compute 1.5–3 hr wall
(cap 8 hr, 7 workers); owner tokens: 3 tmux teams + the ultracode panel.

## Process note

The prereg draft goes to an ultracode adversarial panel (methodology /
degeneracy / Goodhart-surface lenses, the SIEGE-panel shape) before locking.
Panel catches are grafted with named sources, then the registration locks and
the build begins.
