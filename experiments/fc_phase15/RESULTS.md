# FC phase-1.5 rules rethink — readout

**Date:** 2026-06-10
**Spec:** `docs/superpowers/specs/2026-06-10-field-connect-phase15-design.md` (`1cd2cf3`; pre-data implementation notes `12da021`, `41e4774`)
**Pre-registration:** `experiments/fc_phase15/PREREGISTRATION.md` (`889c8b5`) — locked before any training run; no bar, signal, or ranking rule altered after data.

## Decision: **NO-GO at the mechanical screen** (spec §6b: stop before the blind campaign)

No arm cleared 3/4 signals + sanity. Per the registered branch mapping this is the §7 NO-GO outcome — the rethink added nothing over plain A1 — and the registered consequence applies: **escalate past the Field-Connect family** (pivot menu: different win-condition family or QD-selection work). The PARTIAL branch (one more parameterization iteration) did **not** fire and is not licensed by this experiment.

## 1. Calibration (budget 3000, seed 42, n=200; full table `calibration.md`)

| arm | komi | bias | verdict |
|---|---:|---:|:---:|
| c1_field_flip | 0.00 | 0.090 | PASS |
| c3_control_capture | 0.10 | 0.085 | PASS |
| c2_contested_terrain | — (grid 0.00–0.30) | 0.285–0.315 | **BIAS_UNRESOLVED → arm invalidated** |

C2 (the capture-free contested-terrain arm) was degenerate under self-play: 60%+ draws at every komi, bias immovable because komi only enters the timeout tiebreak. The slate's most Hex-like candidate — the one both probe teams scored lowest on novelty ceiling — also failed first contact with training.

## 2. Mechanical screen (budget 5000, seeds 42/43/44, instrumented mirror eval n=200/seed)

| signal | C1 field_flip | C3 control_capture | A0 baseline | A1 (probe params) |
|---|---:|---:|---:|---:|
| lead_changes | **5.713** | **5.355** | 5.285 | 6.285 |
| game_length | 155.1 | 154.6 | 61.9 | 70.4 |
| control_flip_rate | 4.187 | 4.154 | 5.298 | **10.606** |
| connection_win_fraction | 0.697 | 0.712 | 1.000 | 0.990 |
| **signals won (bar: ≥3/4)** | **1/4** | **1/4** | — | — |
| trained_vs_random (gate ≥0.80) | 0.470 ✗ | 0.503 ✗ | 0.993 | 0.863 |
| seat_balance (gate ≤0.10) | 0.178 ✗ | 0.162 ✗ | 0.065 | 0.060 |
| draw_rate (gate ≤0.05) | 0.015 ✓ | 0.000 ✓ | 0.000 | 0.002 |

Both C arms: 1/4 signals AND sanity FAIL → screen NO-GO with no arm to advance.

**Training instability:** each C arm suffered a full PPO collapse on one seed (C1 seed 42 tvr = 0.000; C3 seed 44 tvr = 0.010; other seeds 0.56–0.85). The collapsed seed drives C3's seat-balance failure (0.300 on the collapsed seed; 0.093 — a pass — without it); C1's seat-balance failure comes from its two *healthy* seeds (0.290, 0.245; the collapsed seed sits at 0.000). The r=1/ε=0.25 base is *harder* to learn than either reference, not easier.

**Determinism validation:** A0 and A1, retrained from scratch under the new instrumentation, reproduced their probe-era numbers exactly (A1: lead 6.285, length 70.395, tvr 0.863 — bit-identical). The comparison table is therefore strictly like-for-like, and the kernel-cache engine optimization (`1ce17b6`) is confirmed bit-transparent at experiment scale.

## 3. Honest synthesis

1. **The slate's shared base — r=1, ε=0.25 ("sharpen the field") — is what failed, and it failed on the experiment's own terms.** A1's reference row dominates both C arms on all four registered signals, and most tellingly on the signal built to measure field dynamics: control_flip_rate 10.606 (A1, r=2) vs ~4.2 (C arms, r=1) vs 5.3 (A0). Radius-2 overlap is what makes control contestable; r=1 + quantized ε makes control nearly permanent once established (a placed stone's own cell is essentially unflippable terrain at distance 0). The blind teams' "radius-2 blur" critique, implemented as r=1/ε=0.25, *reduced* the interactivity it was meant to restore.
2. **The flip mechanic itself worked as designed.** C1's capture_events = 7.09/game where the probe's surround capture was structurally 0.000 — RESULTS.md §4's "replace the capture mechanic with one that fires" was achieved, and C1 won lead_changes outright. The mechanic is not the failure; the field it operates on is.
3. **C3's control-capture barely fires** (0.26 replacements/game) — building 3 net attackers adjacent to an enemy stone is rarely worth a full action when simply extending wins the race; and the one-turn lockout was separately proven inert (spec §4 note).
4. **C2's placement gate stalls the game** rather than forcing fights: with moves gated by enemy control, self-play converges on mutual territory-sealing and 60% draws.
5. *(Post-hoc observation, input not commitment, mirroring probe §4):* the untested combination is **flip-capture on the r=2 field** — A1's parameterization with C1's firing capture. Nothing in this experiment licenses running it under the Field-Connect family's registered rules; if the family is ever revisited after the pivot work, that is the natural first candidate.

## 4. Pre-registration audit

- PREREGISTRATION.md committed (`889c8b5`) before any training; bars quoted from spec §6b/§7 and applied verbatim by `run_screen.py` (committed `be67f80` before the run; the only post-commit edit was the loud-skip handling for calibration-invalidated arms, `2a2b7b7`, which touches no bar).
- C2's invalidation followed the pre-registered sanity-gate rule (calibration bias ≤ 0.10), decided by `calibrate.py` before any screen data existed.
- The blind campaign was **not** run, per the registered §6b stop rule — no agent-team scores exist for this slate; the K/M/T pack was never built.
- Engine work merged with full two-stage review; legacy suite green throughout (239 passed; pre-existing `test_ca_integration` collection artifact only).
- Cost: ~1 day build (three gated engine mechanics + harness) + ~1.3 h calibration + ~1.9 h screen compute (sum of per-seed elapsed_s in `screen_results.csv`). The blind campaign's ~50 min was saved by the stop rule.
