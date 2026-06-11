# FRONTLINE campaign — pre-registration (locked before any engine code or training run)

Spec of record: docs/superpowers/specs/2026-06-11-frontline-rebuild-design.md (incl. §8 locked
constants table and §11 pre-lock review provenance). Registered escalation provenance:
experiments/siege/RESULTS.md §7.1.
Decision grammar shape: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md §7.

## Arms (4 in screen, 3 in blind)
- f_frontline (treatment): contested_majority on the proven flip substrate. hex_rhombus W=22,
  influence r=2/s=1.0/d=0.5/eps=0, field_flip at control_margin 0.0 (decoupled), pie ON
  (positional superko present but provably inert — spec §3). Engagement min(I1,I2) >= E; score =
  engaged cells led (dyadic-exact, FP tol 1e-9 tie-only); early-end = same leader >= M_end
  (komi-adjusted) at 3 consecutive ply-checks ending at a round-end (round-end = post-P2 check),
  step_count >= 20, leader-signed counter; double-pass before turn 20 = draw, at/after = score
  resolution; timeout T=200 = score resolution. Score resolution order: score+komi -> a player
  with zero stones placed can never win -> stones-on-board tiebreak -> draw.
  Obs adds score_margin_frac (clip +/-2), engaged_frac, armed_frac.
- s_flip_r2 (comparator): retrained in-campaign from its SIEGE recipe; its own komi ladder is its
  SIEGE-registered fractional one (komi 0 first). S's SIEGE adjudication (+0.2 sub-bar) is settled
  and NOT re-litigated here.
- a1_field_connect (anchor): retrained in-campaign (bit-identical retraining proven twice).
- a0_baseline (screen only): registered job = instrumentation-reproduction check (see Stage 2).

Comparator-failure rule (all stages): S or A1 failing its own health checks (collapsed seed,
bias > 0.10, tvr floor) -> CAMPAIGN_UNRESOLVED -> one retrain. Never a family verdict.

## Stage 0 (pre-training kills — arithmetic & mechanism-liveness ONLY)
Per spec §6: NO kill bars on random-rollout behavioral rates (early-end frequency, draw rate,
double-pass share are logged diagnostics) — the original Frontline's false-kill defect.
- 0a kernel memo (script on engine kernels, no engine edits):
  (1) re-derived flip-threshold table INCLUDING own-side d2 support (the SIEGE memo's chain rows
  drop it: a linear 3-chain end has I2 = 1.75, so the memo's d1+d1+d1+d2 profile gives net 0.0000
  — no flip; corrected: 4x d1. Interior L>=4: 6 attackers);
  (2) engagement-saturation table at E in {0.75, 1.0, 1.25} x fill {10%, 20%, 41%};
  (3) flip margin-swing Delta(S_cap - S_opp) on the pinned canonical set at E = 1.0 — geometries
  pinned by exact axial coordinates in the memo BEFORE computing: straggler (lone stone,
  attackers d1+d1+d2), 2-chain end (memo profile), 3-chain end (4x d1), each in vacuum AND with a
  second-rank enemy support row at d2 behind the chain. Expected exact vacuum values -1 to -2.
  KILL-0a1: mean margin swing across the pinned canonical front set < -2 (anti-synergy
  unrepaired). KILL-0a2: analytic engaged_share at 20% fill, E=1.0 > 0.60 (saturation unrepaired;
  spec §4.1 predicts 0.11 — fires only if the design arithmetic is wrong ~6x).
- 0b post-build smoke, configuration PINNED: E=1.00, M_end=8, komi_cells=0, seed 7.
  1000 random rollouts + 200 per scripted matchup: front-builder vs front-builder, mutual-packer
  vs mutual-packer (packers build in opposite corners, all cross-player stone distances >= 5 so
  kernels cannot overlap at r=2), mirror vs front-builder, pass-bot vs front-builder.
  Logged: flips, engaged_share trajectory, end-causes, scores, margin swings per flip.
  KILL-0b1 (build-regression check; mechanic identical to S's on-disk 3.59/70.5): < 1 flip/game
  under BOTH random and front-builder play.
  KILL-0b2: mutual-packer mean total score > 2 cells/game (packing-scores-zero violated).
  KILL-0b3 (design-model validation kill, spec §6): random-rollout engaged_share at
  min(turn 80, final ply), all games, outside (0.01, 0.60).
  MIRROR CONTINGENCY (pre-Stage-1, one use): mirror secures >= draw in >= 30% of games vs
  front-builder -> switch board to W=21, restart from Stage 0a (one licensed switch; S/A1 stay
  W=22 — comparability cost recorded).

## Stage 1 calibration (PPO 3000, n=200/cell, seeds 42/43/44)
- f_frontline grid: E {0.75, 1.00, 1.25} x M_end {8, 12} = 6 cells. Per cell, gate ORDER:
  (1) skill: tvr mean >= 0.75 AND no seed < 0.65 (floor set below the blind-validated S's
      measured 0.780 — a 0.80 floor is a calibrated false-kill; the +0.15-over-random-baseline
      clause is inert for symmetric games and is dropped). Collapsed seed (tvr < 0.20) -> ONE
      fresh-seed rerun, reserves 45 then 46 consumed in order, at most one rerun per original
      seed; the rerun REPLACES the collapsed seed in all aggregates (mean over the 3 final
      seeds); a third collapse -> cell INVALID;
  (2) seat bias <= 0.10 with pie ON at komi_cells 0; fallback ladder komi_cells {+-1, +-2} —
      smallest |komi| passing, direction by the measured bias sign at komi 0 (one pass);
  (3) end-cause health: timeout share <= 0.25 of ALL games (denominator pinned); draw <= 0.05;
      score_margin end-cause share >= 0.25 (the rebuilt mechanism must be load-bearing).
      Double-pass share logged, yellow flag > 0.50 (diagnostic, not a gate);
  (4) engaged_share (final-ply mean over ALL games, all end-causes) in [0.02, 0.60].
  Tie-break among passing cells: game_length centrality closest to 95, then max score_margin
  share, then min |bias|.
  KILL: all 6 cells (+ komi ladder) fail -> family dead, campaign NO-GO, no screen/blind spend —
  subject to the KILL_INVALID branch (Decision rule, below).
- s_flip_r2 / a1: re-assert SIEGE/fc_phase15 calibration artifacts (komi 0 PASS on disk); full
  recalibration only if retraining drifts bias > 0.10; recalibration failure -> comparator rule.

## Stage 1.5 drama (DIAGNOSTIC ONLY — never a comparative or bar)
Drama is demoted by registration: F's score-share trace (progress_p = S_p/max(1, S_p+S_opp)) is
closeness-by-construction — the rc2_descriptor_v2 Goodhart relocated — and is incommensurable
with the component-span traces behind the on-disk DRAMA_ANCHORED result. Computed and logged on
fresh n=200 trace-instrumented rollouts of the winning cell's seed-42 policy pair (yellow flag:
< 30% of games with per-game drama > 0.01), reported alongside the anchored S/A1 values for the
post-campaign writeup. No licensing role: Stage-2 GO is 2/2 of the two comparatives below.

## Stage 2 screen (PPO 5000, seeds 42/43/44, mirror eval n=200/seed)
All statistics computed over EVERY eval game of the 3 final seeds; no game- or seed-level
filtering of any comparative or band (R21 Probe B survivorship lesson).
Comparatives, DIRECTIONAL, f_frontline vs s_flip_r2 — GO requires 2/2:
1. control_flip_rate: F - S >= +0.5 absolute (identical r=2 instrumentation).
2. game_length centrality, band [30,160] center 95: F >= 10 turns more central than S.
Band-only sanity, scored on F (S/A1 owe only the comparator health checks):
flip events/game in [1,20] AND distinct-stones-flipped >= 0.5 x events; engaged_share in
[0.02, 0.60]; timeout <= 0.25, draw <= 0.05, score_margin share >= 0.25 RE-ASSERTED at 5000;
tvr gates as Stage 1 with mandatory per-seed inspection; seat bias <= 0.10; packing-scores-zero
re-asserted (mutual-packer vs mutual-packer on the final F config: mean total score <= 2
cells/game); exploiter bands: trained F beats pass-bot >= 0.90 and beats mirror >= 0.70 of games
(each seat).
Instrumentation-reproduction check (A0's registered job): a1/a0 control_flip_rate must reproduce
the on-disk ordering with a1 - a0 >= 3.0 (on-disk 10.6 vs 5.3); failure -> instrumentation
INVALID -> CAMPAIGN_UNRESOLVED, never a family verdict.
GO to blind: F passes 2/2 comparatives + ALL bands. F fails -> NO blind, campaign NO-GO.

## Stage 3 blind (2 independent agent teams, fresh labels G/J/P, sealed mapping opened only
after all verdicts; seat-swapped matches, seat-averaged verdicts; opposite evaluation orders;
no cross-reads; fairness-perception probe question; neutral pack name)
Verdict instrument: the evaluations/stage3_ab BRIEFING.md template (Overall 1-10, same anchors),
adapted only by label substitution.
Games: F, S, A1.
- CAMPAIGN VALIDITY: A1 in [3.7, 4.4] (widened from [3.9, 4.4] on the two on-disk observations
  3.90 and 4.15); outside -> CAMPAIGN_UNRESOLVED -> one cheap blind replicate, whose numbers then
  adjudicate alone; a second consecutive validity failure -> CAMPAIGN_INVALID (F undecided,
  family neither GO'd nor retired, rules track NOT declared exhausted).
  S sanity flag: S outside [3.7, 4.5] -> verdicts provisional -> one replicate.
- GO: F - A1 >= +1.0 AND F > S with F - S >= +0.3.
- PARTIAL: (F > S AND F - A1 < +1.0) OR |F - S| < 0.3 -> exactly one licensed
  re-parameterization: the runner-up Stage-1 cell by the registered tie-break (re-assert its
  Stage-1 gates at its registered komi — no new grid — then screen, then blind once; the second
  blind is adjudicated GO-else-NO-GO, no further PARTIAL, no further knobs). If no second cell
  passed Stage 1, the knob is VOID and PARTIAL -> NO-GO.
- NO-GO (F <= S outside the tie band, or a clean kill at any earlier stage): contested_majority
  RETIRED; the 2026-06-10 pivot menu is exhausted on the rules side; the RC2 selection-layer
  workstream becomes the sole registered track (quality-signal candidates per
  experiments/rc2_descriptor_v2/RESULTS.md: planning-gap / learnability / periodic agent slates).
- KILL_INVALID branch: a Stage-0/1 kill attributable on inspection to implementation error
  (not design arithmetic) -> fix and rerun that stage ONCE; only a clean kill, or the rerun's
  kill, maps to RETIRED.

## Compute (honest)
Build ~1-1.5 days + Stage 0a ~2h + Stage 1 ~1.5h + Stage 1.5 ~10 min + Stage 2 ~2h +
Stage 3 ~1h. Total ~2-2.5 days wall (+~0.5 day if the W=21 mirror contingency fires).

Locked constants: spec §8. Not altered after data.
