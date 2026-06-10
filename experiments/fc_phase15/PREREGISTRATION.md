# FC phase-1.5 — pre-registration (locked before any training run)

Spec: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md (1cd2cf3).
This file concretizes measurement details; bars are quoted verbatim from spec §6b/§7.

## Arms
c1_field_flip, c2_contested_terrain, c3_control_capture (treatments);
a0_baseline, a1_field_connect (comparators, retrained — no probe checkpoints
exist — from the probe's komi-calibrated defs under identical new instrumentation).

## Screen signals (all movable by every arm; spec §6b)
1. lead_changes — proxy identical to probe metrics.py: field arms use
   largest-controlled-component differential at the arm's own control_margin
   (0.25 for C arms, 0.0 for A1); A0 uses the threshold-race score differential.
   Pie-swap plies excluded. Bar: arm mean > A0 mean.
2. game_length — bar: in [30,160] and at-least-as-central as A0
   (probe's exact lambda, band midpoint 95).
3. control_flip_rate (NEW) — per non-swap ply, count cells whose controller
   sign {-1,0,+1} (at the arm's margin) changed vs the previous ply; mean per
   ply, then mean over episodes/seeds. Bar: arm mean > A0 mean.
4. connection_win_fraction (NEW) — fraction of episodes ending by win-condition
   fire (engine._winner is not None and not engine._ended_by_max_turns).
   Bar: >= 0.80 (floor, not vs A0).

Screen GO per arm: >= 3/4. Ranking among GO arms: control_flip_rate, descending.
Only the top arm advances. If no arm clears 3/4: report NO-GO, stop before blind.

## Sanity gates (per arm; any failure invalidates the arm)
trained_vs_random >= 0.80; draw_rate <= 0.05; post-komi seat bias <= 0.10.

## Screen config
PPO budget 5000, seeds 42/43/44, sampled seat-swap mirror eval n=200/seed
(probe methodology). Komi: C arms calibrated by experiments/fc_phase15/calibrate.py
(grid 0.0..0.30 step 0.05, budget 3000, seed 42, bias <= 0.10 to pass);
A0/A1 keep their probe-calibrated komi.

## Blind campaign (spec §6c)
3 games x 2 independent agent teams = 6 verdicts. Fresh labels K/M/T
(mapping sealed in experiments/fc_phase15/eval_helper.py BLIND dict;
evaluators are instructed not to read harness internals — same protocol
that held in the probe). Unblinding only after all 6 verdicts are filed.

## Decision rule
Spec §7 verbatim (GO / PARTIAL / NO-GO / replicate-check). Not altered after data.
