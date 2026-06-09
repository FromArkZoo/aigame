# Field-Connect probe — go/no-go readout

**Date:** 2026-06-09
**Spec:** `docs/superpowers/specs/2026-06-07-field-connect-probe-design.md` (v2 lean, `0f99cb8`)
**Decision criteria:** pre-registered in spec §8c and locked in the implementation plan (`docs/superpowers/plans/2026-06-09-field-connect-probe.md`) before any training run. None were altered after data was seen.

## Decision: **NO-GO (lever wrong as parameterized)** — with a strongly validated core mechanism

Both pre-registered legs fail:

- **Mechanical screen: A1 wins 2/4** (GO requires ≥ 3).
- **Blind agent A/B: A1 − A0 = +0.70 Overall** (GO requires ≥ +1.0).
- **Learnability guard (spec §10): PASS** — A1 `trained_vs_random` = 0.863, so this is a clean *lever-wrong* no-go, **not** an unlearnable false negative.

Per spec §8c's NO-GO branch: rethink the rules (not the boards) before any further substrate work.

## 1. Mechanical screen (PPO budget 5000, seeds 42/43/44, instrumented sampled mirror eval n=200/seed)

| metric | A1 (Field-Connect) | A0 (baseline) | A1 wins? |
|---|---:|---:|:---:|
| capture_rate | 0.000 | 3.225 | no |
| decisiveness | 0.990 | 1.000 | no |
| lead_changes | 6.285 | 5.285 | YES |
| game_length | 70.395 | 61.892 | YES (more central in band [30,160]) |
| seat_balance | 0.060 | 0.065 | — |
| draw_rate | 0.002 | 0.000 | — |
| trained_vs_random | 0.863 | 0.993 | — |

Komi calibration (pre-screen): both games PASS at komi 0.00 — the pie rule alone balances both (A1 bias 0.050, A0 bias 0.015, n=200). Full table: `calibration.md`.

## 2. Blind agent A/B (2 independent teams, 4 verdicts, blind labels Q=A0 / Z=A1; unblinded by orchestrator)

| | team-1 | team-2 | mean |
|---|---:|---:|---:|
| **Z = A1 Field-Connect** | 4.1 | 4.2 | **4.15** |
| **Q = A0 baseline** | 3.3 | 3.6 | **3.45** |
| differential | +0.8 | +0.6 | **+0.70** |

Preference: **2/2 teams prefer Z.** Verdicts: `evaluations/probe_ab/team-{1,2}_game{Q,Z}.md`.

**Convergent blind findings** (both teams, independently):
- The **win condition is the differentiator**: Z's connection objective *forces board-spanning interaction* ("you can never ignore the opponent"); Q "tends toward two solitaire cluster-builds." This reproduces the R21 plateau diagnosis essentially verbatim — from evaluators who were blind to it.
- **Z's surround capture is dead** ("the capture adds nothing") — matching the mechanical screen's capture_rate = 0.000 exactly.
- **Z's radius-2 influence blur coarsens tactics** (fights resolve in 1–2 stones; Hex edge templates "fuzzed").
- Z is **recognizably Hex** (novelty 3.5–4.0): "Hex on Hex's own board with a dead capture rule," plus a draw-admitting contested third state.

Calibration evidence: Q's blind scores (3.45 mean) reproduce the known plateau-family campaign means (R20 3.73, R21 3.69); Z lands at R8 parity (4.10), the corpus's all-time anchor — on its first build.

## 3. Honest synthesis (what the probe actually established)

1. **The interaction-forcing property of influence-in-the-win-condition is validated** — unanimously, blind, with the mechanism named unprompted. The plateau's root cause (win conditions that never force contact) is confirmed from a second independent direction.
2. **This parameterization wastes part of the lever.** ε=0 with radius-2/decay-0.5 makes Field-Connect play as "thick Hex": the field adds connection thickness but blurs tactics, and surround capture — the spec's chosen synergy mechanic — never fires (structurally: open degree-6 boards give groups too many liberties). A1 is R8-parity-good but not plateau-breaking, and the pre-registered bars were set at plateau-breaking.
3. **Post-hoc observation on the screen criteria** (labeled as such; the registered result stands): two of the four mechanical signals could never have favored A1 — capture_rate is structurally 0 for surround-on-open-hex, and a threshold race saturates decisiveness at 1.0 by construction. A future screen should pick signals both arms can move.

## 4. What a phase-1.5 rules rethink should consider (input, not commitment)

- **Replace or fix the capture mechanic**: surround never fires at radius-2 influence on an open board. Candidates: capture on *field* encirclement (control-based, not liberty-based), or drop capture and let the field recompute carry all the dynamics.
- **Sharpen the field**: smaller radius (1) and/or ε > 0 so control is harder-won and tactics regain precision (both teams' top critique).
- **Differentiate from Hex**: the contested third state and capture-driven field flips are the non-Hex ingredients; make them load-bearing or the novelty ceiling stays ~4.
- Substrate work (spec §12 carpet-family fractional-dimension test) remains **gated** behind a rules configuration that clears the bars — per the registered NO-GO branch, boards don't fix rules.

## 5. Pre-registration audit

- §8c criteria applied verbatim; the lead-change proxy and length band were locked in the plan before any run; the pie-swap exclusion and exact end-cause flag were locked before screen data existed (commits `c9467d9`, `094225f`).
- Blindness held: evaluators saw neutral labels Q/Z, a neutral entry path (`evaluations/probe_ab/play.py`), sanitized errors, and symmetric templates; the sealed mapping was opened by the orchestrator only after all four verdicts were filed.
- Cost: ~1 day build + ~40 min total compute (calibration 5.5 min, screen 25 min) + ~35 min blind campaign.
