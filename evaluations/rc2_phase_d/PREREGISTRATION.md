# RC2 Phase D — cross-cell blind-slate agent-team eval (pre-registration, locked before any verdict data)

Registered origin: Phase C ARCHIVE_GO (`experiments/rc2_archive/RESULTS.md`, merged
`de787df`). Question: do archive-discovered high-drama games clear blind agent judgment
where GE-evolved games plateaued (R21 campaign mean 3.69)? This doc doubles as the Phase D
design spec (declared single-doc deviation from the two-file pattern; nothing is omitted).

## Slate (locked; mechanical selection rule)

Archive games: from R2 arm M's final archive (`experiments/rc2_archive/replicate2x/
checkpoint.json`), take elites in DESCENDING pooled drama, skipping any whose signature
(family, topology_type, num_dimensions, axis_size, turn_type, capture_type, ca_present,
sorted action_types) duplicates an already-selected elite (near-twin guard), until 5 are
selected. Applied result (cells unique by construction; 3 families):

| slate id | canon (12) | pooled drama | genome summary |
|---|---|---|---|
| S1 | 3020796b254c | 0.3838 | connection, moore 5D axis-3, multi_place, CA, no capture |
| S2 | 636a263a05a4 | 0.3444 | threshold, torus 3D axis-4, custodian, alternating |
| S3 | 0165399e5aef | 0.3055 | connection, moore 3D axis-4, alternating, CA |
| S4 | ae3eabac990f | 0.2795 | territory, hex 2D axis-8, move+place, no capture |
| S5 | 39fea7a7b721 | 0.2615 | territory, hex 2D axis-8, place, no capture |

Blind controls (loaded from their DBs as in Phase B/C; never identified to evaluators):

| ctrl | game | prior agent mean | role |
|---|---|---|---|
| C+ | d4015a646ae3 (genesis_v2_run8.db) | 4.10 | validity anchor (R8) |
| C− | e1453dac5445 (genesis_v2_run21_menger.db) | 3.66 | plateau / GE-top control |

7 games total, blind labels A–G assigned by a seed-99 shuffle (mapping in
`.blind_mapping.json`, orchestrator-only). No komi calibration is applied to S1–S5
(played as generated; the fairness probe captures imbalance — an unbalanced elite scoring
low blind is honest signal against the archive). C− keeps its R21 calibrated komi (0.00);
C+ is played as in its R8/Phase-B form.

## Protocol

- **3 independent agent teammates** (tmux agent-team, the project's standard evaluator
  harness), each evaluating ALL 7 games in a per-team randomized order (seed-99 derived).
  21 verdicts total.
- Evaluators are blind: briefing forbids reading `.blind_mapping.json`, `experiments/`,
  `evaluations/run21/`, helper source beyond usage, and any git commands. Interaction
  ONLY via `evaluations/rc2_phase_d/play.py`.
- Per-game protocol = the SIEGE/R21 5-phase template: rules comprehension (from `--rules`
  + observed behavior only), ≥3 full lines per game covering both roles + one
  adversarial/novelty-stress line, joint analysis, novelty adversary, verdict with
  per-role sub-scores, fairness probe (1–5), Overall 1–10.
- Scoring anchors (verbatim from prior campaigns): R8 4.10, R19 4.375 (top 5.0),
  R20 3.73, R21 3.69; anchor DOWN against drift; 5.0 = the never-cleared G1 ceiling.
- Verdicts filed to `evaluations/rc2_phase_d/team-{N}_game{A..G}.md`; unblinding ONLY
  after all 21 are filed.

## Bars (on blind means; applied after unblinding, transcribed verbatim)

- **VALIDITY band:** mean(C+) across the 3 teams ∈ [3.7, 4.5]. Outside →
  **CAMPAIGN_UNRESOLVED**: no classification of any slate game; exactly one blind
  replicate (fresh teams) is licensed (z_flip_r2 graft; protects against drift/harness
  failure, never against an unwelcome answer).
- **BAR D1 (beats the plateau):** mean(all 15 S-verdicts) − mean(C−) ≥ +0.3.
- **BAR D2 (anchor-class top):** max over S1–S5 of the per-game blind mean ≥ 3.9
  (the Phase B ABOVE-pod boundary).

## Decision grammar (locked)

- VALIDITY fail → CAMPAIGN_UNRESOLVED (above; grammar below applies only when valid).
- D1 ∧ D2 → **PHASE_D_GO**: the loop-integration spec (run.py:593 scores_map swap,
  drama-archive selection replacing GE) is authorized as the next registration.
- exactly one of D1, D2 → **PHASE_D_PARTIAL**: one licensed follow-up, chosen at
  results time and registered before running: either a slate redesign (e.g., komi
  calibration for unbalanced elites) or a quality-signal fix (e.g., CA-churn guard) —
  not both, no integration meanwhile.
- neither → **PHASE_D_NOGO**: high drama does not transfer to agent-judged quality
  beyond the anchor range; archive integration shelved; descriptor redesign (CA-churn
  and agency-weighting first candidates) precedes any further archive spend.

Reported, not binding: Spearman(pooled drama, blind mean) over all 7 games; per-game
fairness flags + role win splits; the CA-churn question — S1/S3 are CA games whose drama
may be board churn rather than player agency; evaluators' Phase-2 experience decides,
not us.

## Honesty notes (pre-committed)

- Drama 0.26–0.38 is ABOVE the validated anchor range (≤0.304); Phase D is an
  extrapolation test, and a NOGO is a real, reportable outcome.
- The orchestrator builds the pack and is not blind; evaluator independence + the
  post-hoc bars carry the inference (project-standard since R21).
- Helper rendering for 5D/3D substrates is new build surface; each slate game is
  smoke-verified (rules + legal-action decode + a scripted line) BEFORE teams launch,
  and the pack commit pre-dates all verdicts.
