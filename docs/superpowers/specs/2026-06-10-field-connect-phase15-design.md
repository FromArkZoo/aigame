# Field-Connect phase-1.5 rules rethink — design spec

**Date:** 2026-06-10
**Status:** DESIGN — slate locked, decision rule pre-registered below (§7); no training run until the implementation plan locks bars verbatim.
**Parent:** `2026-06-07-field-connect-probe-design.md` (probe NO-GO per §8c; rules-rethink branch). Readout: `experiments/field_connect_probe/RESULTS.md`.
**Context docs:** `analysis_post_r21.md`, `evaluations/run21/SUMMARY.md`.

## 1. Motivation

The Field-Connect probe returned **NO-GO (lever wrong as parameterized)**: mechanical screen 2/4, blind A/B +0.70 < +1.0. But its core property was validated unanimously and blind — both teams independently named the interaction-forcing win condition as the differentiator, and the treatment landed at R8 parity (4.15) on its first build. The failures were specific and convergent (RESULTS.md §4):

1. **Surround capture is dead** — structurally 0.000 capture rate on an open degree-6 board; "the capture adds nothing."
2. **Radius-2 influence blurs tactics** — fights resolve in 1–2 stones; Hex edge templates fuzzed.
3. **The contested third state is not load-bearing** at ε = 0, so the game is "recognizably Hex" and novelty caps at ~4.

Phase 1.5 redesigns the *rules* (not the board — substrate work stays gated per the registered NO-GO branch) to make the non-Hex ingredients load-bearing, then re-runs the probe gates.

**External anchors** (canonical games sitting on RESULTS.md §4's candidates, de-risking the slate):

- **Sygo** (Christian Freeling): connection win on hex where captured stones flip colour rather than being removed — "capture-driven field flips" as a proven mechanic.
- **Gonnect** (João Pedro Neto): Go capture + connection win; capture and connection are synergistic when capture actually fires.
- **Tumbleweed** (Mike Zapawa): placement/replacement rights from line-of-sight control majority — control-margin-as-capture, the closest published analogue to "capture on field encirclement."

## 2. Goal & hypothesis

**Hypothesis:** with a sharp field (r=1, ε>0) and a capture/terrain mechanic that is field-native and structurally fires, the Field-Connect family produces agent-judged depth that clears the plateau bar (+1.0 over baseline) — not just R8 parity.

**This experiment decides:** which (if any) of three candidate rule-sets clears the pre-registered probe bars. GO un-gates substrate work (parent spec §12). NO-GO escalates past the Field-Connect family entirely.

**Non-goals (YAGNI):** no evolution, no GE, no MAP-Elites, no new boards, no production campaign. Single board, three arms, one blind A/B.

## 3. Shared base (all candidates)

Identical to probe A1 except the field:

- hex_rhombus, W = 22 (484 cells); pie rule on; place-only; max_turns 200.
- Win: `field_connection`, P1 connects r-axis (target_dimension 1), P2 connects q-axis (0).
- **Field: influence r = 1, strength 1.0, decay 0.5, control_margin ε = 0.25.**

Why ε = 0.25: at r=1/d=0.5 every stone contributes 1.0 to its own cell and 0.5 to each neighbor, so all field values are multiples of 0.5. ε = 0.25 therefore means *any nonzero net controls a cell, and exact ties are contested*. Contested cells occur constantly along fight frontiers — the third state becomes real rather than measure-zero (the ε = 0 degeneracy). The same ε is used everywhere "control" appears (win check, C1 flip, C2 gate, C3 replace) — one definition of control, no per-mechanic thresholds.

## 4. The three candidates

### C1 — Flip (`capture_type = "field_flip"`, Sygo-anchored)

After each placement and field update, every enemy stone standing on a cell the **mover now controls** — `board_values` at the stone's cell beyond ±ε *including the stone's own ±1.0 self-contribution* — flips colour. Each flip updates the field (sign change = ±2× the stone's kernel) and resolution repeats to a fixed point.

- **Structurally fires:** the field at an enemy stone's cell is −1.0 (self) + 0.5·(m − t), with m/t = mover/enemy adjacent stones. Flip requires that to exceed +ε, i.e. **m − t ≥ 3**: three net adjacent attackers flip a lone stone. Go-like effort, field-native, no liberty code. Each friendly neighbor adds 0.5 of support — defense is emergent.
- **Cascades terminate provably:** after P1 places, every flip is P2→P1 and raises P1's field monotonically, so resolution is bounded by the number of enemy stones. No damping rule.
- **No ko rule needed:** stones are never removed, so the board fills monotonically and positions cannot repeat.

### C2 — Contested terrain (capture none, placement `constraint = "not_enemy_controlled"`)

No capture. The field gates **moves**: a player may place only on empty cells not enemy-controlled (for P1: `board_values ≥ −ε`; contested and own-controlled cells are placeable by both). Frontiers are exactly where legal-move sets overlap; fights are about tipping contested cells. Connection already requires self-controlled cells, so contested cells block both players' paths natively.

- **No-legal-move rule:** if the mover has no legal placement, the game ends immediately and the max_turns tiebreak applies (controlled-cell count, komi applied, draw if equal).
- Cheapest arm (no capture code); tests RESULTS.md §4's "drop capture and let the field recompute carry all the dynamics" branch. Known risk: most Hex-like of the three; may cap novelty.

### C3 — Control capture (`capture_type = "field_replace"`, Tumbleweed-anchored)

C1's flip condition as a **chosen action**: a player may place onto an enemy-occupied cell iff they control that cell beyond ε with the enemy stone's contribution included (same > threshold semantics as C1). The enemy stone is removed and the mover's stone placed.

- **No-instant-recapture:** the cell just replaced cannot be replaced on the immediately following turn (ko-like; one flag, cleared after one turn). *Implementation note (2026-06-10, pre-data):* under instantaneous-field control this rule is provably never binding at ANY parameterization — the replacement itself shifts the cell by +2·strength, so the opponent cannot control it on the next ply (analytic proof + empirical probes in the Task-5 review cycle). It ships as specified, as an inert safety net; superko is what actually prevents replacement cycles.
- Removal means board fill is not monotone; max_turns backstops stalls and the screen's game-length band catches replacement wars.

## 5. Engine changes (all additive + gated; legacy bit-identical)

1. `CAPTURE_TYPES` += `"field_flip"`, `"field_replace"` with resolution logic per §4 (C1 post-move fixed-point; C3 legality + replace + recapture flag). Field updates may use the existing gated full recompute; delta updates are an optimization, not required.
2. `PlacementRule` constraint += `"not_enemy_controlled"` (C2), evaluated against `board_values` with ε at move-legality time; plus the no-legal-move termination.
3. Tests: unit tests per mechanic (flip threshold arithmetic incl. self-contribution, cascade monotonicity/termination, C2 gate + no-legal-move end, C3 legality + recapture flag), plus a legacy bit-identity regression run (same suite the probe's engine gains used).

## 6. Experiment protocol

Three stages, same shape as the probe.

**6a. Build + smoke + calibration.** Build C1/C2/C3 game defs (mirroring `experiments/field_connect_probe/build_games.py`), random-rollout smoke (≥50 games each: terminations, no hangs, flips/replacements actually occur), then komi-calibrate each arm with the existing `calibrate.py` harness (n=200; pass = first-move bias < 0.10).

**6b. Mechanical screen.** PPO budget 5000, seeds 42/43/44 per arm, instrumented sampled mirror eval n=200/seed. **Four signals, all movable by every arm** (fixing RESULTS.md §3's flaw — the probe's capture_rate and decisiveness could never favor A1):

| signal | bar |
|---|---|
| lead_changes | beats A0's value under identical instrumentation |
| game_length | more central in [30, 160] than A0 |
| **control-flip rate** (new) | mean cells changing controller per turn beats A0 — measures whether field dynamics are load-bearing; movable even by capture-free C2 |
| **connection-win fraction** (new) | end-cause = connection (via the exact end-cause flag) ≥ 0.80 — replaces decisiveness, which a threshold race saturates by construction |

A0 (and A1, for reference) are re-evaluated under the new instrumentation from their saved probe checkpoints; if checkpoints are unavailable, A0 is retrained at the same budget (+~25 min) — bars always compare like-for-like instrumentation.

Screen GO per arm: **≥ 3/4**. The screen ranks arms; ties broken by control-flip rate. Only the top arm advances. If no arm clears 3/4, stop: report NO-GO without spending the blind campaign.

**6c. Blind agent A/B.** Three-game blind campaign: **Q′ = A0 baseline, Y′ = A1 (probe parameterization), Z′ = screen winner**, two independent agent teams (this is agent-team eval, not human eval). Fresh neutral labels distinct from the probe's Q/Z; neutral entry path; sanitized errors; symmetric templates; sealed mapping opened by the orchestrator only after all six verdicts are filed. Including A1 in-campaign anchors calibration — its 4.15 came from a different campaign and cross-campaign comparison is noisy.

**Sanity gates (any failure invalidates the arm, not the experiment):** learnability trained_vs_random ≥ 0.80; draw rate ≤ 0.05; post-komi seat bias ≤ 0.10.

## 7. Pre-registered decision rule (locked at spec commit; not altered after data)

With campaign means Z (winner), Y (A1), Q (A0):

- **GO:** Z − Q ≥ +1.0 AND Z > Y → the rethink is plateau-breaking. Substrate work (parent spec §12 carpet-family fractional-dimension test) un-gates, carrying the winning rule-set.
- **PARTIAL:** Z > Y AND Z − Q < +1.0 → the rethink improved the lever but is not plateau-breaking. One more parameterization iteration is justified; substrate work stays gated.
- **NO-GO:** Z ≤ Y → the rethink added nothing over plain A1. Escalate past the Field-Connect family (pivot menu: different win-condition family or QD-selection work first).
- **Corner case (replicate-check, takes precedence over NO-GO):** if Y ≥ Z and Y − Q ≥ +1.0, the probe's registered A1 verdict is in doubt (two campaigns disagree). Re-run one cheap blind A1-vs-A0 A/B before classifying; do not declare GO from Y alone.

## 8. Pre-registered defaults

| parameter | value |
|---|---|
| board | hex_rhombus W=22, pie on, max_turns 200 |
| field | influence r=1, s=1.0, d=0.5 |
| ε (uniform: win/flip/gate/replace) | 0.25 |
| C3 recapture lockout | 1 turn |
| screen | PPO 5000, seeds 42/43/44, mirror eval n=200/seed |
| calibration | n=200, bias < 0.10 |
| blind campaign | 3 games × 2 teams, fresh labels, sealed mapping |
| decision bars | §7, verbatim |

## 9. Budget

~1 day build (three small gated engine changes + tests + game defs), ~10 min calibration, ~75 min screen compute (3 arms × ~25 min; +25 min if A0 retrain needed), ~50 min blind campaign. Same cost envelope as the probe.
