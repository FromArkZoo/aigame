# SIEGE campaign — go/no-go readout

**Decision criteria:** pre-registered in `PREREGISTRATION.md` (locked `0e51297`, before any training). None were altered after data.

## Decision: **CAMPAIGN NO-GO — asymmetric objectives RETIRED at calibration; S confirms flip-capture as a real but sub-bar improvement (+0.2, far below +1.0)**

- **m_siege (treatment) never reached the screen.** `M_GRID_UNRESOLVED`: all 9 (N,T) cells failed the per-role skill gates (Stage 1). Per the registered KILL, the asymmetric-objectives direction is retired without blind spend on it.
- **s_flip_r2 (control, = the registered z_flip_r2 probe) ran the full registered path**: screen 4/4 vs a0, blind S − A1 = **+0.20** (S 4.10, A1 3.90; validity band met at its lower bound). Under the z_flip_r2 grammar: **does NOT reopen the FC family** (< +1.0) and **does NOT close it permanently** (S > A1) — the in-between case, recorded as: flip-capture is a real, unanimously perceived improvement that is not plateau-breaking.
- **Registered escalation fires:** neither arm GOed → **Frontline rebuilt** (margin ~1.0, decoupled flip threshold, score-margin early-end, double-pass resolves by main score) is the registered next family. The **RC2 selection-layer follow-on** fires regardless of outcome (observer influence field build, then QD anchor probe; GE stays diagnostic-only).

## 1. Stage 0 (pre-training kills) — PASS

- 0a kernel-computed flip thresholds (`STAGE0_MEMO.md`): lone stone 3 attackers (≥2 adjacent), chain-end 4, interior 5, dense 8; engine cross-check PASS. Kill bar (lone > 4) not hit.
- 0b smoke (seed 7): m_siege 5.20 flips/game random (2.50 quota ticks/g), 21.0 scripted; s_flip_r2 3.59 random / 70.5 scripted. Both kill gates (≥ 1 flip/game) PASS.

## 2. Stage 1 calibration (PPO 3000, n=200, seeds 42/43/44 + reserves) — M DEAD, S CALIBRATED

- **m_siege:** 0/9 cells passed. Failure is uniformly the **Breaker skill gate**, reached before any bias/quota gate (registered gate order): Maker tvr healthy (0.82–0.96 across most cells) but Breaker never cleared tvr ≥ 0.80 with +0.15 over its random-random baseline (best ≈ 0.75–0.78 vs baselines 0.48–0.71 — the timeout decree hands a random Breaker many free wins, which the baseline-adjusted gate correctly prices in). 5 cells had a collapsed seed (role tvr < 0.20, incl. three Breaker-side collapses to 0.00); all reserve reruns (seed 45) still failed. Role-pie was NOT applicable: it is the registered balance lever, and no cell ever reached the bias gate.
- Honest gate note (input, not commitment): several cells showed real Breaker learning (+0.15–0.23 over baseline) that missed only the 0.80 absolute floor — a floor calibrated on symmetric tvr. Any future asymmetric family should pre-register per-role absolute floors separately.
- **s_flip_r2:** PASS at komi 0.00 (bias 0.050, draws 0.000) — same komi-0 result as the probe's A1. ε=0.25 sensitivity cell recorded (bias 0.025, len 143.0): DIAGNOSTIC ONLY, the single licensed PARTIAL knob, unused (no PARTIAL fired).
- Cost: 7,031 s (~1h57m), well under the 4–5 h estimate.

## 3. Stage 1.5 drama anchor-calibration (n=200, seed 11) — **DRAMA_ANCHORED**

| game | family | mean drama |
|---|---|---|
| 573 (R21 GE-bottom, agent-tied-1st) | connection | **0.1765** (top) |
| a1_field_connect | field_connection | 0.1324 |
| a0_baseline | threshold | 0.0536 |
| e1453 (R21 GE-top, agent-ranked 6/7) | threshold | **0.0458** (bottom) |

Both bars passed — and the signal ranked the R21 extremes exactly opposite to GE and aligned with the agent-team eval. Per-role drama was licensed as screen comparative 3 (and would have been; the screen ran S-only).

## 4. Stage 2 screen (PPO 5000, seeds 42/43/44, n=200) — **S-ONLY BLIND (4/4)**

m_siege loud-skipped (registered outcome). s_flip_r2 vs a0 under the z_flip_r2 template:

| signal | s | a0 | win |
|---|---:|---:|:---:|
| lead_changes | 6.125 | 5.285 | ✓ |
| game_length (centrality, center 95) | 72.16 | 61.89 | ✓ |
| control_flip_rate | 10.584 | 5.298 | ✓ |
| connection_win_fraction (≥ 0.80) | 0.987 | — | ✓ |

- **Flip-capture FIRES at trained play: 7.84 events/game** (a1's surround: 0.000, the probe's dead mechanic) — and the field's contestability survived it (control_flip_rate 10.58 ≈ a1's 10.61).
- Reproduction check: a1 retrained in-campaign hit control_flip_rate 10.606 and tvr 0.863 — identical to the phase-1.5 on-disk values.
- Flag (recorded, not a gate): s tvr mean 0.780 (0.83/0.74/0.77) — a hair under the 0.80 symmetric sanity band; seed 43 dragged it.

## 5. Stage 3 blind (2 independent tmux teams, sealed labels V/X, role-swapped, role-averaged) — S 4.10, A1 3.90

| | team 1 | team 2 | mean |
|---|---:|---:|---:|
| **V = s_flip_r2** | 4.0 | 4.2 | **4.10** |
| **X = a1_field_connect** | 3.8 | 4.0 | **3.90** |

- **Validity band:** A1 3.90 ∈ [3.9, 4.4] — met exactly at the lower bound (recorded honestly; no replicate required by the registered rule).
- **Unanimity:** both teams, blind, in opposite evaluation orders, scored V exactly +0.2 over X and **independently named the capture rule as the only differentiator** — V's field-flip "live and central / coherent with the field win," X's surround "vestigial / strategically dead." The phase-1.5 thesis (mechanic works, field was wrong) is confirmed at r=2 by perception, not just instrumentation.
- **Grammar:** S − A1 = +0.20 < +1.0 → no reopening. S > A1 → no permanent closure. S at 4.10 = exact R8-anchor parity; the plateau (no game ≥ 5.0) stands.
- **New structural finding (team 2, both verdicts, engine-checked by the evaluator):** a shared win-graph asymmetry in `field_connection` on hex_rhombus — a fully P2-controlled row can fail to connect where the equivalent P1 squeeze wins (the horizontal-step exclusion); pie fixes tempo only. Fairness scored 2/5 on both games by team 2. This caps the family and is a concrete, fixable predicate target — input for any future registration, not licensed now.

## 6. Pre-registration audit

- PREREGISTRATION.md committed `0e51297` before any training; all gates applied verbatim by `calibrate.py` / `run_screen.py` / `anchor_drama.py` (constants cross-checked file-to-file in the final build review).
- Gate order (skill→bias→shares) enforced structurally; reserve-seed ladder used 5×, never exclusion; no role-pie improvisation.
- The screen's S-only branch and the blind's S-grammar followed the registered stop rules exactly; the ε=0.25 PARTIAL knob was never licensed to fire.
- Stage-0b smoke seed 7 (chosen at build time, after prereg lock — recorded here, prereg untouched).
- Blind hygiene: fresh labels D/V/X; pack renamed `stage3_ab` pre-campaign after review found "siege_ab" leaked treatment character; mapping opened only after all 4 verdicts filed; teams evaluated in opposite orders, no cross-reads.
- Cost: build ~1 day (33 commits incl. two-stage review per task) + Stage 1 1h57m + Stage 1.5 ~6 min + Stage 2 1h53m + Stage 3 ~1h05m.

## 7. What this campaign registered as next

1. **Frontline rebuild** (registered escalation): margin ~1.0, decoupled flip_margin, score-margin early-end rule, double-pass resolves by main score — fresh spec + prereg before any code.
2. **RC2 selection-layer workstream** (fires on ANY outcome): measurement-only observer influence field (generator_v2.py:213-224 zeroes descriptors off-threshold), then the QD anchor probe with within-R21 binary separation bars. **The drama signal's anchor result here (§3) is direct encouragement: it already separates the R21 extremes correctly.**
3. Input-not-commitment notes: per-role absolute tvr floors for any asymmetric family (§2); the hex_rhombus win-graph asymmetry fix (§5) as a candidate lever inside whichever family runs next.
