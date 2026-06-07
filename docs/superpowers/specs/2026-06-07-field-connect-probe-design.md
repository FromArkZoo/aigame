# Field-Connect probe — design spec

**Date:** 2026-06-07
**Status:** design, pending user review → implementation plan
**Context docs:** `analysis_post_r21.md`, `evaluations/run21/SUMMARY.md` (the R21 saturation finding), `figures/koch_substrate/` (Koch board exploration)

## 1. Motivation

R21's agent-team eval was decisive: across 5 independent teams, **no game cleared Overall 5.0**, the cross-run mean (3.69) sits below R19 (4.375), and GE now *anti-correlates* with agent-judged depth (the GE-top game ranked 6/7; the GE-last connection game tied 1st). The pre-committed decision rule fired **PIVOT + SATURATION**: the rule-grammar + GE-evolution regime is empirically exhausted. The eval teams converged on a specific diagnosis — the plateaued games are non-interactive packing races because (a) the win condition (threshold-race) never forces contact, and (b) the influence field is decorative, never entering win logic.

This probe tests the **smallest decisive version of the pivot's rule lever** before committing to a full pivot (new substrates + Quality-Diversity + replacing GE). It is a go/no-go experiment, not a production run.

## 2. Goal & hypothesis

**Hypothesis:** A game in which influence *is* the win condition — you win by connecting your two sides through cells your influence dominates — combined with permanent-cut surround capture, on a bigger degree-6 board, produces agent-judged strategic depth that the threshold-race family never did.

**This probe decides:** does the new rule set beat the plateaued baseline (a) on cheap mechanical depth signals and (b) on a small blind agent A/B? If yes, the pivot's rule lever is real and worth building out. If no, the rule lever is wrong and the pivot needs rethinking before any substrate work.

**Non-goals (YAGNI):** no evolution, no GE, no MAP-Elites yet, no production eval campaign, no new substrate family beyond the two boards below. Those come *after* this probe says the lever works.

## 3. The new game: "Field-Connect"

Played on a degree-6 triangular lattice (existing `hex` adjacency).

1. **Placement.** Players alternate placing one stone on any empty cell. P1 first. Pie rule on (P2 may swap after P1's first move). Place-only (D1 ban).
2. **Influence.** Each stone emits influence via the existing propagation rule: `board_values[c] += sign · strength · decay^dist` for cells within `radius`, sign = +1 (P1) / −1 (P2), clamped. (Reuses `propagation_rule`.)
3. **Control.** A cell is **P1-controlled** if `board_values[c] > +ε`, **P2-controlled** if `< −ε`, otherwise **contested** (controlled by neither). Default `ε = 0` (simple sign).
4. **Capture.** Surround (Go-liberty) capture: a stone group with zero empty-adjacent liberties is removed. Removal recomputes the field, so control can flip and connections break or form. **Permanent cut** (removed stones are gone, unlike reclaimable custodian).
5. **Win.** Each player has two **target boundary regions**. A player wins the instant there exists a path of adjacent, **self-controlled** cells linking their two targets. (Hex, played on the influence field rather than on stones.) Mutual-exclusion and draw behavior depend on board geometry (see §5).
6. **Komi** `komi_p2` available for seat balance (existing mechanism), calibrated per board before the agent A/B.
7. **Termination.** Connection win, or `max_turns` timeout → tiebreak by larger controlled-cell count (komi applied), draw if equal.

**Why this is the strongest test of the hypothesis:** influence is now fully load-bearing — it *is* the connectivity. Stones matter only through the field they project and the captures they enable. This is the maximal fix for the "decorative influence" critique.

## 4. Engine change (the one new mechanic)

Add `win_condition.condition_type = "field_connection"` to the engine:

- New method `EngineV2._check_field_connection()` called after each step:
  1. Threshold `board_values` into per-player controlled-cell sets using `ε`.
  2. For the player who just moved, BFS/union-find over their controlled cells (lattice adjacency) from target-region A; win if the component reaches target-region B.
  3. Return winner or None.
- `ε` (`control_margin`) is a config field on the win condition; default 0.0.
- Target boundary regions are precomputed per board from the topology (see §5) and stored on the game def.
- Additive and isolated: reuses `board_values` (already maintained) and lattice adjacency (already in topology). No change to placement, capture, or propagation. Fully unit-testable with hand-built positions (e.g. a known winning field → asserts win; a contested-cell gap → asserts no win; a capture that breaks a path → asserts win revoked).

**Effort:** ~½ day incl. tests.

## 5. Boards & connection targets

Two boards, both degree-6 triangular lattice, matched size (~400–600 active cells), komi-calibrated.

### 5a. Primary — rhombus "Hex board" (REFINEMENT, flagged for review)
**Refinement vs the brainstormed "hexagon":** a regular hexagon has 6 edges, making 2-player connection targets ambiguous. A **rhombus** (parallelogram region of the triangular lattice) with degree-6 adjacency *is* the canonical Hex board — 4 sides, unambiguous targets. This is the cleanest test of "does Field-Connect work at all," and is bigger than R8's 9×9.

- Region: `i ∈ [0,W), j ∈ [0,W)` on the lattice basis, `W ≈ 22` (~484 cells).
- P1 targets: row `j=0` ↔ row `j=W−1`. P2 targets: col `i=0` ↔ col `i=W−1`.
- On a rhombus these are mutually exclusive (Hex theorem analog): exactly one player can complete a crossing → **no draws by construction** (modulo the contested-cell wrinkle below).
- **Contested-cell wrinkle:** because cells can be *contested* (neither-controlled), the Hex no-draw guarantee does NOT strictly hold — a board can be split by a contested wall. That is itself an interesting dynamic; timeout tiebreak (§3.7) handles it. Verify draw rate in the mechanical screen.

### 5b. Rider — Koch snowflake
The fjorded board from `figures/koch_substrate/` (degree-6 lattice masked to an iteration-2 Koch snowflake interior, ~600 cells). Its value is precisely that its connection geometry is non-trivial (fjords = pockets/chokepoints).

- P1 targets: the 3 "upward" star-points; P2 targets: the 3 "downward" star-points (point cells identified as the lowest-degree promontory clusters per region). Exact target-cell selection is a build detail; the spec requires "two disjoint, roughly-opposite boundary-region sets."
- Purpose: does the fjorded boundary measurably change play vs the clean rhombus, under the *same* rules?

### 5c. Engineering for boards
- Rhombus: trivial active-mask (all lattice cells in range) — may already be expressible as `grid` with hex adjacency; confirm during implementation.
- Koch: add `_koch_active(axis_size, n_iter)` to `topology.py` (point-in-snowflake test, from the exploration script) + constructor wiring + `SUBSTRATE_INVARIANTS` entry + invariant tests. ~2 hr.

## 6. Baseline (control)

The plateaued family, on the *same two boards*, so board is held constant and only the rules vary:
**outnumber-2 capture + influence(decorative) + threshold-race**, pie on, komi-calibrated. This is the R20/R21 menger family that scored ~3.5–3.8. (Open parameter — §9 — whether to additionally baseline against the R21 connection game `573`, which scored well on design.)

## 7. Experimental matrix

| | Field-Connect (treatment) | Plateaued baseline (control) |
|---|---|---|
| **rhombus** (primary) | A1 | A0 |
| **Koch snowflake** (rider) | B1 | B0 |

4 games. (Optional absolute anchor: the current best menger game, for scale.)

## 8. Measurement → pre-registered criteria

### 8a. Mechanical screen (all 4 games; a few PPO seeds each, reuse finalization/G4 machinery)
Per game, from sampled trained-vs-trained play:
- **game_length** — mean plies to termination.
- **capture_rate** — mean captures per game (tests whether surround actually fires — the menger pod's failure was captures never firing).
- **decisiveness** — fraction of games ending by the win condition vs timeout.
- **lead_changes** — mean sign-changes of the connection-progress differential, where progress = (P1 largest controlled component spanning toward its targets) − (P2 equivalent). Concrete proxy defined at implementation; the point is "does the lead swing, or is it monotone."
- **seat_balance** — `|P1 winrate − 0.5|` mirror, post-komi (reuse `experiments/r20_5_g4` / komi driver).
- **draw_rate** — for the contested-wall wrinkle (§5a).

### 8b. Agent A/B (survivors only)
2 independent agent teams (tmux), each plays **A1 (hex×Field-Connect)** and **A0 (hex×baseline)** **blind to which is "new,"** ≥3 lines each, score on the Phase 1–5 rubric. If A1 looks promising, add B1 (Koch) for the rider question.

### 8c. Pre-registered decision (set BEFORE running)
- **GO (pivot lever is real):** A1 beats A0 on **≥3 of {capture_rate, decisiveness, lead_changes, game_length-in-a-healthy-band}** in the mechanical screen, **AND** A1 scores **≥ +1.0 Overall above A0** in the agent A/B (ideally A1 ≥ 5.0). → proceed to design the full pivot (more boards, QD, GE-replacement).
- **KOCH EARNS A PLACE:** only if B1 ≥ A1 on the boundary-sensitive signals (lead_changes, decisiveness) — i.e. the fjords measurably help. Else Koch is dropped and the pivot uses plain Hex boards.
- **NO-GO (lever is wrong):** A1 does **not** beat A0. → the pivot's rule hypothesis is falsified; rethink the rules (not the boards) before any further substrate work. This is a cheap, valuable negative.

## 9. Open parameters (decide at implementation; defaults given)
- **`ε` control margin** — default 0.0 (sign of influence). If control is too volatile/noisy, raise to a small positive margin so a cell needs clear dominance.
- **Connection-target geometry** — rhombus is unambiguous; Koch targets need a concrete cell-selection rule.
- **Baseline choice** — menger plateau family (default) vs also including the `573` connection game as a second control.
- **Board size `W`** and Koch resolution — default ~480–600 cells; matched across boards.

## 10. Risks
- **Field-Connect may be PPO-unlearnable / agent-unreadable** (too complex) → a no-go could be a false negative from complexity, not shallowness. Mitigation: the mechanical screen checks whether PPO learns *anything* (trained-vs-random); if PPO can't learn it at all, that's reported distinctly from "learnable but shallow."
- **Contested-wall draws** (§5a) could dominate → measured via draw_rate; if pathological, raise `ε` or add a tiebreak.
- **Seat balance** — connection + first-move advantage; handled by komi calibration before the A/B (same gate as R21).

## 11. Scope & sequence (~1.5–2 days)
1. Engine `field_connection` win condition + unit tests (½ day).
2. Koch `topology.py` active-mask + rhombus board config + invariant tests (~2 hr).
3. Build the 4 game defs; komi-calibrate each (reuse komi driver).
4. Train PPO on the 4 games (few seeds) + compute mechanical metrics (few hr compute).
5. Agent A/B (2 teams, blind) on the survivors (~1–2 hr).
6. Synthesis + go/no-go readout against §8c; recommend next step.
