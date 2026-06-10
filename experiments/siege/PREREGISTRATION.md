# SIEGE campaign — pre-registration (locked before any training run)

Spec of record: docs/pivot_menu_synthesis_2026-06-10.md (probe skeleton).
Decision grammar shape: docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md §7.

## Arms (4 in screen, 3 in blind)
- m_siege (treatment): P1 Maker wins field_connection; P2 Breaker wins capture_quota
  (N distinct-Maker-stone flip ticks, per-move tick cap 2) OR timeout (timeout_winner=2 at T).
  Both players field_flip. hex_rhombus W=22, influence r=2/s=1.0/d=0.5, control_margin 0.0,
  pie OFF (roles fixed; role-pie is the registered lever of last resort, one retry max).
  Observation adds quota_frac; clock_frac ≡ existing step_frac (verified present, not duplicated).
- s_flip_r2 (control): symmetric field_flip + field_connection on the identical substrate
  (= a1_field_connect + field_flip capture). Fresh pre-registration of the phase-1.5
  post-hoc candidate. Single manipulated variable vs m_siege = win-structure asymmetry.
- a1_field_connect (comparator): retrained in-campaign from
  experiments/fc_phase15/games/calibrated/a1_field_connect.json.
- a0_baseline (comparator, screen only): retrained in-campaign from
  experiments/fc_phase15/games/calibrated/a0_baseline.json.

## Stage 0 (pre-training kills)
- 0a flip-threshold memo on CHAINS at r=2/d=0.5/eps=0, computed from the engine's own kernels.
  KILL: lone-stone flip needs > 4 coordinated attackers.
- 0b 1000 random rollouts + 200 scripted chain-builder rollouts per arm (m_siege, s_flip_r2),
  flip-locus (frontier vs straggler) logged.
  KILL: < 1 flip/game in m_siege or s_flip_r2 under EITHER policy.

## Stage 1 calibration (PPO 3000, n≈200/cell)
- m_siege: (N,T) grid {3,5,8}x{80,120,160}, seeds 42/43/44. Per cell, gate ORDER:
  (1) per-role skill gates FIRST: role tvr >= 0.80 AND >= +0.15 over that role's
      random-vs-random baseline; a collapsed seed (role tvr < 0.20) triggers ONE
      fresh-seed rerun (45 then 46), never exclusion;
  (2) role bias = |mean Maker win rate - 0.5| <= 0.10 over the 3x3 cross-seed
      role matrix (198 games);
  (3) quota share of Breaker wins >= 0.20; timeout share <= 0.25 of ALL games.
  Tie-break among passing cells: max quota share, then min |bias|.
  Fallback (one registered retry): role-pie (P2 chooses role after move 1).
  KILL: grid + role-pie retry all leave bias > 0.10 -> m_siege dead; campaign CONTINUES
  as s_flip_r2 vs a1 vs a0 under the z_flip_r2 bars below.
- s_flip_r2: pie ON at komi 0.00 first; komi grid 0.05..0.30 step 0.05 fallback; bias <= 0.10.
- One eps=0.25 @ r=2 sensitivity cell on s_flip_r2, DIAGNOSTIC ONLY; pre-bound as the single
  licensed PARTIAL re-parameterization knob.

## Stage 1.5 signal anchor-calibration (before drama becomes a bar)
Per-role drama = mean over plies of sqrt(max(0, loser_progress - winner_progress)) on each
player's OWN normalized progress trace (connection roles: largest-controlled-component span
fraction along own axis; Breaker: max(quota_frac, step_frac)).
Retro-compute on fresh a0/a1 rollout traces + R21 extremes (e1453, 573).
BAR: drama(a1) > drama(a0) AND e1453 not ranked top. FAIL: drama demoted to diagnostic;
screen GO becomes 2/2 of the remaining comparatives.

## Stage 2 screen (PPO 5000, seeds 42/43/44, mirror eval n=200/seed)
Comparative signals, m_siege vs s_flip_r2, with effect-size floors:
1. control_flip_rate (identical r=2 instrumentation all field arms) — floor delta >= 0.5 absolute.
2. game_length centrality in [30,160], center 95 — floor >= 10 turns more central.
3. per-role drama (if anchor-calibrated) — floor delta >= 0.05.
Band-only sanity (NOT comparative): m_siege flip events/game in [1,20] AND
distinct-stones-flipped >= 0.5 x flip events; quota share >= 0.20 and timeout share <= 0.25
RE-ASSERTED at 5000; draw rate <= 0.05 (s/a1/a0 only; m_siege structurally drawless — stated,
not credited); per-role skill gates as Stage 1 with mandatory per-seed inspection;
role/seat bias <= 0.10.
GO: m_siege >= 2/3 comparatives + all bands. STOP RULES: m_siege fails but s_flip_r2 clears
the z_flip_r2 template (>= 3/4 vs a0: lead_changes, game_length, control_flip_rate,
connection_win_fraction >= 0.80) -> blind runs s vs a1 only. Both fail -> NO blind, NO-GO.

## Stage 3 blind (2 independent teams, fresh labels D/V/X, sealed mapping, role-swapped
matches, role-averaged verdicts; fairness-perception probe question in protocol; role win
split logged, flag > 80/20)
- CAMPAIGN VALIDITY: a1 blind mean in [3.9, 4.4]; outside -> CAMPAIGN_UNRESOLVED -> one cheap
  blind replicate, no permanent classification.
- GO: M - A1 >= +1.0 AND M > S with |M - S| >= 0.3.
- PARTIAL: |M - S| < 0.3, or M > S but M - A1 < +1.0 -> exactly one licensed
  re-parameterization: the eps=0.25@r2 cell. Nothing else.
- M <= S: asymmetric-objectives direction RETIRED. S adjudicated under z_flip_r2 grammar:
  S - A1 >= +1.0 reopens the FC family; S <= A1 closes it permanently (validity band guards
  the closure).
- Both NO-GO: registered escalation -> Frontline rebuilt (margin ~1.0, decoupled flip_margin,
  score-margin early-end, double-pass resolves by main score) as the next family.

## Registered follow-on (fires on ANY outcome)
RC2 selection-layer workstream: build measurement-only observer influence field
(generator_v2.py:213-224 zeroes descriptors off-threshold), then QD anchor probe with
within-R21 binary separation bars. GE stays diagnostic-only meanwhile.

Locked constants table: see docs/superpowers/plans/2026-06-10-siege-campaign.md.
Not altered after data.
