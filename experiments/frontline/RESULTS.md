# FRONTLINE campaign — go/no-go readout

**Decision criteria:** pre-registered in `PREREGISTRATION.md` (locked `3a378dd`, before any
engine code or training run). None were altered after data.

## Decision: **CAMPAIGN NO-GO — contested_majority RETIRED at Stage 1 (clean kill, KILL_INVALID inspection passed); the rules-side pivot menu is EXHAUSTED; the RC2 selection-layer workstream becomes the sole registered track**

- **F_GRID_UNRESOLVED:** all 6 (E, M_end) cells failed the FIRST gate (skill) — tvr means
  0.500–0.587 against the 0.75 floor, per-seed minima 0.430–0.550 against the 0.65 floor.
  No seed collapsed (< 0.20), so the replace-in-slot rerun branch never fired and reserves
  45/46 were never consumed; gates 2–4 (bias / end-cause / engaged) were structurally
  unreached on every cell. The komi ladder was never entered. No runner-up cell exists, so
  the Stage-3 PARTIAL knob is VOID — moot, since the campaign dies here.
- **KILL_INVALID inspection (registered branch): CLEAN KILL.** Every implementation-error
  candidate was ruled out by direct evidence (section 3). The kill is the design's own
  arithmetic: the family prices initiative negatively at the tactical level, and PPO
  descends that gradient into passivity that loses even to random.
- **Registered consequence (prereg Decision rule, verbatim):** "NO-GO (… a clean kill at any
  earlier stage): contested_majority RETIRED; the 2026-06-10 pivot menu is exhausted on the
  rules side; the RC2 selection-layer workstream becomes the sole registered track
  (quality-signal candidates per experiments/rc2_descriptor_v2/RESULTS.md: planning-gap /
  learnability / periodic agent slates)."
- **No screen/blind spend** (registered: Stage-1 kill → no Stage 1.5/2/3). Comparator
  provenance stub PASS (s_flip_r2 / a1_field_connect present with registered calibration
  provenance).

## 1. Stage 0 (pre-training kills) — PASS at build time; mirror contingency resolved W=22

- 0a kernel memo: mean front-margin swing +1.14 (bar < −2) PASS; analytic engaged@20% fill
  0.107 (bar > 0.60, spec §4.1 predicted 0.11) PASS — the engine demonstrably implements the
  design arithmetic.
- 0b pinned smoke (E=1.00, M_end=8, komi 0, seed 7): flips/game 29.242 (≥ 1.0) PASS;
  mutual-packer total score 0.000 (≤ 2.0) PASS; random engaged@min(80, end) 0.024 ∈
  (0.01, 0.60) PASS. Random-vs-random: mean length 168.2, 66.4% score_margin / 33.5%
  timeout, draws 0.0%, P1 51.5%.
- **MIRROR_CONTINGENCY fired at 100%** (threshold ≥ 30%): mirror secured ≥ draw in every
  game vs front-builder (and chain_vs_mirror: mirror as P2 won 100%). Owner decision
  (2026-06-12, recorded pre-Stage-1, commit `e95c3be`): **stay at W=22**; the one licensed
  W=21 switch forfeited. Post-hoc note (honest, not load-bearing): board parity affects
  mirror strategies, not the sign of the mover-margin arithmetic that killed Stage 1 — there
  is no basis to expect a different skill-gate outcome at W=21.
- Two warning signs visible at Stage 0, in hindsight: the mover-signed margin swing per
  flip-ply was already **negative** under all play styles (random −1.05, chain −1.00, vs
  mirror −1.50; the −2 bar priced only catastrophic anti-initiative), and the mirror
  contingency's 100% firing was the same defense-dominance showing through a second window.

## 2. Stage 1 calibration (PPO 3000, n=200/cell, seeds 42/43/44) — **F_GRID_UNRESOLVED**

| cell | tvr 42/43/44 | mean (≥ 0.75) | min (≥ 0.65) | verdict |
|---|---|---:|---:|---|
| E0p75_M8  | 0.530 / 0.540 / 0.510 | 0.527 | 0.510 | FAIL skill |
| E0p75_M12 | 0.550 / 0.590 / 0.590 | 0.577 | 0.550 | FAIL skill |
| E1p00_M8  | 0.550 / 0.550 / 0.580 | 0.560 | 0.550 | FAIL skill |
| E1p00_M12 | 0.570 / 0.640 / 0.550 | 0.587 | 0.550 | FAIL skill |
| E1p25_M8  | 0.570 / 0.430 / 0.500 | 0.500 | 0.430 | FAIL skill |
| E1p25_M12 | 0.600 / 0.560 / 0.510 | 0.557 | 0.510 | FAIL skill |

Grid mean 0.551; best single seed 0.640 (E1p00_M12 seed 43) — still under the per-seed
floor. The floor is anchored: 0.75 was registered just below the blind-validated S's
measured 0.780 on the identical metric and convention (seat-swapped, stochastic
`deterministic=False`, draws count to neither side's wins; S 0.780 / A1 0.863 / A0 0.993 at
the SIEGE screen). All 100 tvr games per seed enter the statistic — no filtering (R21
survivorship pin). Full per-gate detail: `calibration.md` / `calibration.json`.

Cost: 7,653 s (~2h08m) — over the registered ~1.5 h estimate, within the runbook's recorded
2.5–3.5 h drift note.

## 3. KILL_INVALID inspection — **clean kill (design arithmetic, not implementation error)**

Registered branch: "a Stage-0/1 kill attributable on inspection to implementation error (not
design arithmetic) → fix and rerun that stage ONCE; only a clean kill, or the rerun's kill,
maps to RETIRED." Inspection artifacts: `kill_inspection.py` / `kill_inspection.log`
(diagnostic only — replaces no stage numbers).

Implementation-error candidates, each ruled out by direct evidence:

1. **tvr harness** — untrained-policy baseline measures 0.45 (≈ coin flip), draws 0%,
   end-causes healthy (68% score_margin / 32% timeout), mean length 169 ≈ the Stage-0b
   random-vs-random 168.2. The instrument is sane.
2. **Draws counted as losses** — measured draw share in trained-vs-random games: 0/100
   stochastic, 1/100 deterministic. Nothing is masking wins.
3. **Reward wiring** — `_compute_rewards` emits +1/−1/0 from the resolved winner;
   `play_game` derives winners from those same rewards; Stage-0b's sane win shares validate
   the contested_majority resolution path end-to-end.
4. **Observation** — `_observe` encodes the spec §3.9 CM state (own-perspective margin
   clipped ±2, engaged share, leader-signed persistence counter). The agent sees the
   decisive state.
5. **Harness parity** — the identical `train_one` (siege copy, fc_phase15 config shape) took
   S to 0.780 and A1 to 0.863. The trainer learns games that reward skill.
6. **Anchor commensurability** — S's 0.780 was measured under the same play_game seat-swap
   stochastic convention; the floor was registered with that knowledge.

What the instrumented retrain (pinned cell E1p00_M8, seed 42; Stage-1 measured 0.55) shows:

| probe | tvr | draws | end-causes |
|---|---:|---:|---|
| untrained, stochastic | 0.45 | 0 | 68% score_margin / 32% timeout |
| trained 3000, stochastic | 0.49 | 0 | 59% score_margin / 37% timeout / 4% double_pass |
| trained 3000, **deterministic** | **0.28** | 1 | **6% score_margin / 83% timeout / 11% double_pass** |

Trainer's own learning curve (wr vs random, eval n=100): **0.49 @ 750 → 0.32 @ 1500 →
0.08 @ 2250 → 0.30 @ 3000.** Gradients flow and the policy MOVES — away from winning.
Training is not silently broken; it is faithfully optimizing a landscape whose local
gradient points away from initiative. The deterministic argmax policy is the smoking gun: it
converges to disengaged, pass-adjacent stalling (83% timeouts, score_margin share collapsing
to 6%) and loses 71% to random. More budget would not rescue this — the curve degrades with
training, it does not plateau.

**Mechanism (coheres with the Stage-0 measurements):** every flip-ply costs the mover margin
on average (−1.0 to −1.5); answering a front beats building one (mirror ≥ draw 100%). A
policy-gradient learner is punished every time it initiates contact, so it learns not to —
and a policy that does not initiate cannot beat even random's accidental territory. Neither
grid axis can fix this: E scales the influence kernel, M_end the end-streak; neither flips
the sign of the mover-margin arithmetic. The kill is the design, working as measured.

(Minor anomaly, recorded not load-bearing: the trainer's deterministic self-play eval showed
wr_vs_opp 0.0 at 3 of 4 checkpoints — agents[1] strictly dominating agents[0]. Generic
trainer behavior under a degenerate policy pair; tvr, the registered gate, is unaffected.)

## 4. Stages 1.5 / 2 / 3 — NOT RUN (registered)

Stage-1 kill → family dead, no screen/blind spend (prereg Stage 1 KILL clause). The blind
pack was never built; no agent-team time was spent.

## 5. Honest synthesis

- **What died:** the contested_majority (FRONTLINE) rebuild — the registered escalation from
  the SIEGE campaign — at the cheapest post-training gate, for the most fundamental reason a
  game family can fail: skill does not pay. The margin~1.0 / decoupled-flip / score-margin
  early-end redesign fixed SIEGE's structural complaints but inherited (and measured, at
  Stage 0a) an anti-initiative tactical arithmetic, and accepted it because the bar priced
  only the catastrophic case (< −2).
- **The miss was cheap to have caught:** a 1-seed PPO learnability smoke (~7 min, exactly
  what `kill_inspection.py` runs) at Stage 0 would have killed the family before the 2h08m
  grid spend — and before the build's full Stage-1/2 harness was written. Registered lesson
  for any future training-gated family (in whatever track): put a minimal-budget learnability
  probe in Stage 0, and treat a negative mover-signed margin under ALL play styles as a kill
  sign, not a tolerance.
- **The mirror contingency was the same finding in disguise.** It fired at 100% (threshold
  30%) and was treated as a board-parity question (W=21 vs W=22). It was actually the
  defense-dominance arithmetic showing through a second window — parity was never going to
  change the sign. The owner's W=22 decision was correct in the narrow sense (it cost
  nothing) and immaterial in the broad one.
- **The program's instruments worked.** The gate order spent compute in the right order
  (skill first, 0 wasted bias/end-cause evals); the anchored floor (set below a
  blind-validated good game's 0.780) cleanly separated a skill-expressing family from a
  skill-suppressing one; the KILL_INVALID branch forced the inspection that distinguishes
  "design outcome" from "harness bug" — and the inspection toolkit (untrained baseline,
  learning curve, deterministic probe, draw decomposition) is now reusable.
- **Where the program goes (registered, not a choice):** the rules-side pivot menu is
  exhausted; the RC2 selection-layer workstream is the sole track — planning-gap /
  learnability / periodic agent slates per `experiments/rc2_descriptor_v2/RESULTS.md`. Note
  the convergence: this campaign's skill gate IS a learnability probe — Stage-1 tvr deltas
  over an untrained baseline are exactly the "learnability" quality-signal candidate. The
  FRONTLINE kill is its first validation datum: learnability separated a dead family from
  live ones (F ≈ +0.04 over untrained vs S/A1 ≥ +0.28) at 7 minutes per seed.

## 6. Pre-registration audit

- Prereg locked `3a378dd` before any engine code; gates applied verbatim; structural gate
  order honored (no cell computed gate 2+ after a gate-1 failure).
- All statistics over every eval game; no game- or seed-level filtering (R21 Probe B pin).
- Collapse/reserve branch: never triggered (no seed < 0.20); reserves 45/46 unconsumed.
- Komi ladder: never reached (gate-1 failures; ladder is gate-2 machinery).
- MIRROR_CONTINGENCY: owner decision (stay W=22) made and committed (`e95c3be`) BEFORE
  Stage 1 ran, as the prereg requires.
- KILL_INVALID branch: applied before classification; verdict clean kill; the one licensed
  fix-and-rerun is therefore NOT exercised (it exists only for implementation-error kills).
  Inspection was diagnostic-only — no stage statistic was replaced.
- Stage-3 PARTIAL knob: VOID (no Stage-1 runner-up) — moot at NO-GO.
- Decision grammar: NO-GO via "a clean kill at any earlier stage" → contested_majority
  RETIRED → rules-side pivot menu exhausted → RC2 selection-layer sole registered track.
  Nothing was altered after data.

## Cost (honest)

Stage 0a ~2 h + build (per plan) + Stage 1 7,653 s (~2h08m) + KILL_INVALID inspection ~11
min (378 s train + evals). Stages 1.5/2/3: 0 (not licensed). Registered total estimate was
~2–2.5 days wall including build; the campaign's post-build live spend was ~2.3 h.
