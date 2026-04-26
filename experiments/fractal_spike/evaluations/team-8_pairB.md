# Team-8 — Pair B (Fractal vs Control) Evaluation

**Pair:** B
**Fractal candidate:** `frac_B_fractal` (sierpinski 9×9, 64 active cells, 17 holes)
**Control candidate:** `frac_B_control` (torus 8×8, 64 cells)
**Rule family:** alt + custodian + radius-1 influence + threshold-38.6 (clone of R14 winner `deb4dfe0382d`)

---

## Phase 1 — Rule Comprehension

The two JSONs are byte-identical apart from `axis_size` (9 vs 8) and `topology_type` (sierpinski vs torus); all other fields — placement, capture (custodian), propagation (influence r=1, strength=1.874, decay=0.402), win-condition (threshold=38.616 over signed influence on own cells, max_turns=102), turn-structure (alternating, 1 piece/turn), action-rule (place only) — match. Both substrates expose 64 legal placement cells, so an "average" turn-budget is identical.

Shared ruleset (3-sentence summary): Players alternate placing one stone per turn on any empty cell. Each placement triggers an Othello-style custodian sweep along axis-aligned rays (terminating at empty cells, the substrate boundary, or — on the fractal — at hole cells used as walls). The first player whose total signed influence summed over their own stones exceeds 38.616 wins; otherwise the game expires at turn 102.

**Degeneracies flagged**:
- *Threshold-tempo dominance* (rule-family wide, both substrates): probe shows P0 winrate 1.00 on torus and 0.92 on fractal — first mover almost always crosses threshold one stone earlier. Confirmed in my own play (see Phase 2). This is *not* substrate-induced; it is the known R14 family bug.
- *Degree-4 cell scarcity on fractal*: only 4 cells in the entire substrate have all 4 von Neumann neighbours active — `(2,2), (6,2), (2,6), (6,6)` (the four "T-junction" diagonals between corner sub-blocks and the central hole). On the torus every cell has degree 4. The threshold (38.616) is unchanged, so it costs marginally more stones to reach it on the fractal because each stone delivers fewer reciprocal-friend pairs on average.
- *Custodian on torus does NOT wrap.* Verified by looking at `engine_v2.py:_capture_custodian` (line 522: `while 0 <= pos < self.topo.axis_size`). So "torus" here is geometrically identical to grid for capture purposes; the only torus-specific feature is wrap for distance/influence. This collapses one of the expected control-only advantages.
- *Fortress cells on fractal*: cells with two adjacent holes on a single axis (e.g. `(4,2)`, `(4,6)`, `(2,4)`, `(6,4)` — adjacent to the central 3×3 block) are custodian-immune from that axis. Fewer than half of fractal cells have full custodian exposure.

---

## Phase 2 — Strategic Play

### Game 1 — Fractal (frac_B_fractal). Seat: I play P1, mirror P2.

Move sequence (action ids): `20, 60, 19, 61, 28, 52, 21, 59, 11, 69, 18, 62, 27, 53, 36, 44, 12, 68, 29, 51, 38`

Opening rationale (P1, T1): action 20 `(2,2)` — this is one of only four degree-4 cells on the substrate and a natural anchor for an upper-left cluster that can lean against the central 3×3 hole as a defensive wall on the south. **This is a substrate-specific opening:** on the torus there is nothing to "lean against", and any cell would be equally good.

P2 (T2): action 60 `(6,6)` — diagonal-mirror anchor (also degree 4). Predicted P1 reaction: extend west toward `(1,2)`.

T3–T18 (extension phase, 8 moves each side):
- P1 grows a contiguous block touching the central hole on its NE/E faces and the `(1,1)` hole on the NW: `(1,2), (1,3), (3,2), (2,1), (0,2), (0,3), (0,4), (3,1)`.
- P2 mirrors symmetrically around `(6,6)`: `(7,6), (7,5), (5,6), (6,7), (8,6), (8,5), (8,4), (5,7)`.
- Substrate-specific concern noted at T7 (P1 plays `(3,2)`): this stone would be custodian-vulnerable along its row, but the hole at `(3,3)` makes it permanently immune from a southern N-S bracket (no enemy stone can ever sit at `(3,3)`). I chose `(3,2)` knowing the hole-shielded south face means P2 can only attack along E-W. **This decision has no analog on the torus.**
- No contact between clusters (the central 3×3 hole physically separates the two halves of the board), so no captures possible. Threshold race is the only mechanic in play.

T19 (P1, action 29 `(2,3)`): the unique k=2 placement available — neighbours `(2,2)X` and `(1,3)X`. Marginal influence gain = 4.886. This is the highest-value remaining placement on either side of the board.

T20 (P2, action 51 `(6,5)`): mirror k=2, same gain.

T21 (P1, action 38 `(2,4)`): k=1 with `(2,3)`. Gain 3.380. **Crosses threshold.** Final P1 sum = 40.20, P2 sum = 36.82.

**Game 1 endgame:** Reached the threshold win condition on turn 21. Turn budget 21/102. P2 had no defensive option — the cluster separation (forced by the central hole + my opening choice) meant capture was impossible, and P2's mirror strategy ensured equal accumulation but always one tempo behind.

**Substrate-only strategies adopted:**
- *Anchor at degree-4 cell.* On fractal there are only 4 such cells; choosing one of them is non-trivial. On torus the choice is arbitrary.
- *Cluster against the central 3×3 hole-wall.* The hole blocks influence propagation, but it also acts as an unbreakable defensive boundary — any stone next to the hole has one fewer attack vector. I deliberately placed `(2,3)` knowing its south face was hole-protected.

### Game 2 — Control (frac_B_control). Seats swapped: I-as-Player-2-from-Game-1 plays P1.

Move sequence: `54, 18, 53, 17, 46, 10, 55, 19, 62, 26, 45, 9, 47, 11, 61, 25, 63, 27, 38, 28, 30`

Opening rationale (now-P1, T1): action 54 `(6,6)` — there are no anchor cells per se on a torus (every cell is degree 4); chose `(6,6)` to be substrate-position-comparable to my Game 1 P2 cluster. Predicted ex-P1 (now P2) builds at `(2,2)`.

Strategy: build a 3×3 block by spiral-out from `(6,6)`. There is no central wall to lean on, but also no stone-position is more or less defensively advantaged.

T1–T10 (5 stones each side as a + shape centered on `(6,6)` and `(2,2)`):
- Each + has 4 friend pairs → 5 stones × 1.874 + 4 × 1.506 = 15.40. Symmetric.
- Substrate observation: I considered playing `(7,6)`-`(7,7)`-`(0,7)` torus-wrap into the corner to build asymmetry — but custodian on torus does **not** wrap (verified), so wrap-around offers no tactical benefit, only a small influence-shadow benefit. Skipped.

T11–T18 (P1 fills corners of `(6,6)`-block; P2 mirrors at `(2,2)`):
- P1: `(5,5), (7,5), (5,7), (7,7)`. Each is k=2 (touches 2 stones of the +). Marginal +4.886 each.
- P2: `(1,1), (3,1), (1,3), (3,3)`. Same.
- After T18 each side has a clean 3×3 block. Sums P1 = P2 = 34.94.

T19 (P1, action 38 `(6,4)`): k=1 expansion north of the block. +3.380. Sum 38.32 — under threshold by ~0.3.

T20 (P2, action 28 `(4,3)`): k=1 expansion. Sum 38.32. Mirror.

T21 (P1, action 30 `(6,3)`): k=1 (touching the new `(6,4)` and `(7,3)` if any — actually only `(6,4)` ≈ k=1, plus board_values gives 41.71). **Crosses threshold.** Final P1 sum = 41.71, P2 sum = 38.33.

**Game 2 endgame:** Threshold win on turn 21. Turn budget 21/102. Identical decisive turn to Game 1; identical margin (~3.4). Seat-swap evidence: the same agent (formerly P2) won as P1 here, and lost as P2 in Game 1 — so the result is purely tempo, not skill.

**Substrate-only strategies adopted on control: NONE.** No analog of the "lean against the hole-wall" tactic exists.

---

## Phase 3 — Strategic Analysis (joint)

### Did the fractal play differently?

**Yes, but only at the opening.** The 4-degree-4 anchor cell scarcity created a forced opening choice that does not exist on the torus:
- Fractal: P1's only sensible openings are `{20, 60, 24, 52}` (the four degree-4 cells). All other openings start the cluster with at most degree-3 anchor cells, costing ~1 friend-pair-equivalent of long-term accumulation. There is real positional theory here.
- Torus: any opening is equivalent up to symmetry. There is no opening theory.

**By move 6 the divergence stops being visible.** Once both clusters were anchored and started spiralling, the substrate stopped influencing decisions. Both games progressed to a 21-move threshold-tempo win.

### Choke points / districts

Yes on fractal: the central 3×3 hole physically partitions the board into two large districts (NW-NE-SW-SE quadrants connected only by 4 corridor cells: `(2,4), (6,4), (4,2), (4,6)`). These four "corridor" cells are the only routes by which an opponent's influence can ever cross the central hole region. None of them are degree-4 (each has 2 hole neighbours). No torus equivalent.

In our games, neither player traversed a corridor cell — clusters stayed in their own quadrant. This is **option value left unexercised** by the rule set.

### Influence shadows

Confirmed and observable in the value-grid output: the 17 hole cells block influence propagation entirely (no value at hole positions, no through-conduction). For the four corridor cells `(2,4), (4,2), (6,4), (4,6)`, this means a stone there has only 2 active neighbours instead of 4 — its accumulation potential is 50% of a torus cell.

### Path routing

Not applicable to Pair B (no connection win condition).

### Tempo / first-move advantage

| | Fractal | Control |
|---|---|---|
| P0 winrate (probe, n=200) | 0.92 | 1.00 |
| Decisive turn (this team) | 21 | 21 |
| Final margin (winner − loser) | 3.38 | 3.38 |
| Mean game length (probe) | 21.2 | 21.0 |

Tempo dominance is essentially identical. The 0.08 winrate gap on probe is the only fractal-specific signal — likely due to occasional greedy draws over which of the 4 anchor cells to claim, costing P1 a tempo. Under skilled play the gap should disappear (since the optimal opening is unambiguous).

### Comparable metric

Both games: **21 moves, ~3.4-point margin, P0 wins.** Substrate does not change the decisive turn or margin in optimal play.

---

## Phase 4 — Substrate Critic (mandatory)

### The Critic argues:

(a) *"It's just an 8×8 grid with extra dead cells."* The 17 holes are removed cells; nothing genuinely new is added. The custodian and influence rules are unchanged; capture lines are merely cropped. Strategically equivalent to playing the torus version with an instruction sheet that says "imagine these 17 cells are permanent walls".

(b) *"Apparent difference is artifact of constant threshold."* The probe's 0.08 winrate shift is fully explained by the substrate having lower average cell connectivity (≈3.16 on fractal vs 4.00 on torus) without a compensating threshold reduction. Adjust threshold to 38.616 × 64/64 × (3.16/4.00) ≈ 30.5 and the probe difference would vanish. So the fractal is not a new game — it's the same game with a *miscalibrated* threshold.

(c) *"Would a torus-expert transfer immediately?"* Yes. The opening principle (cluster around an anchor, build a friend-dense block, race to threshold) transfers verbatim. The only new consideration is the 4-anchor-cell selection at T1, which is a 30-second adjustment. Both games here were resolved with the same mirror-cluster strategy with *no genuine adaptation*.

### Rebuttals (P1 + P2)

- **Defensive anchoring against hole-walls is genuinely new.** When I placed `(2,3)` in Game 1 knowing its south face was hole-protected, I was making a decision with no torus analog. The hole-wall acts as a permanent friendly defender — a free 0.753 "phantom influence shield" that no torus cell can offer. **Acknowledged but minor**: in the threshold-race rule family, defensive positioning is rarely tested because no captures occur.
- **The 4-anchor opening is a concrete new theory.** Choosing among `{(2,2), (6,2), (2,6), (6,6)}` matters; choosing among 64 torus cells does not. **Acknowledged but minor**: this is essentially a one-move adjustment.
- **Corridor cells are option value the rule set doesn't unlock.** True — but Pair C (connection-win) might. For Pair B specifically, the option goes unexercised.

### Net Critic verdict

The Critic's strongest point — "miscalibrated threshold" — is a real claim. The fractal is meaningfully different *only* in opening-theory and defensive-anchoring; the body of the game plays the same threshold-race that the R14 family always plays, on either substrate, regardless of how the corridor cells could *in principle* be used.

**Substrate-novelty score: 4/10.** Real positional novelty at openings and at hole-adjacent cells, but the rule family does not reward exploring it. A connection-win or capture-rich rule family would expose it; the threshold race does not.

---

## Phase 5 — Verdict

**Team ID:** team-8
**Pair:** B
**Fractal candidate:** `frac_B_fractal`
**Control candidate:** `frac_B_control`

### SCORES

**Fractal (`frac_B_fractal`)**
- Strategic Depth: **3** — Threshold-tempo race; choices reduce to "extend cluster". The 4-anchor opening adds one decision but everything after is mirror-and-grow. Hole-wall defensive theory is real but never required because clusters never make contact.
- Balance: **2** — P0 dominance is severe (probe 0.92 P0). My seat-swapped games both had P0 win on T21 by 3.4 points. Threshold-tempo bug fully present.
- Novelty (post-critic): **3** — Custodian + influence + threshold is the well-mined R14 winner family. The fractal substrate adds a thin slice of opening theory and defensive anchoring; not enough to change the strategic character.
- Substrate-novelty: **4** — Hole-wall capture-immunity, corridor cells, 4-anchor opening, and influence shadows are all real new phenomena. They appear during play but do not need to be exploited under this ruleset. *(Score 0 for control, by definition.)*
- Overall "Would I play this again?": **3** — Same race-to-threshold experience; substrate adds one minute of opening contemplation then becomes irrelevant.

**Control (`frac_B_control`)**
- Strategic Depth: **3** — Identical race-to-threshold; arbitrary opening then mirror-and-grow. Custodian on torus is not wraparound, so the torus contributes essentially nothing strategically beyond the grid baseline.
- Balance: **1** — P0 winrate 1.00 in probe; my game also P0 win on T21 by 3.4 points. The least balanced of the two.
- Novelty (post-critic): **3** — Standard R14 family; nothing new.
- Overall "Would I play this again?": **3** — Same race; nothing about the torus matters.

### DELTA (fractal − control)
- Strategic Depth: **+0**
- Balance: **+1** (fractal is marginally less degenerate because the 4-anchor opening introduces one greedy-tie-breaking decision that occasionally hurts P0)
- Overall: **+0**

### CRITICAL ASSESSMENT

- **"The fractal substrate genuinely added strategic depth"**: **N**.

- **Specific phenomena observed only on fractal**:
  1. Forced opening choice among 4 degree-4 anchor cells `{(2,2), (6,2), (2,6), (6,6)}`.
  2. Hole-wall capture immunity for stones adjacent to holes (e.g. `(3,2)` cannot be N-S custodian-bracketed because `(3,3)` is a hole).
  3. "Corridor cells" `(2,4), (4,2), (6,4), (4,6)` as the only routes through the central 3×3 hole — option value for board-spanning strategies.
  4. The central 3×3 hole physically separates the cluster zones, guaranteeing zero capture interaction in mirror-cluster play.
  5. Influence shadows — board_values map shows hole cells as gaps, not zeroed sums.

- **Specific phenomena observed only on control (i.e. things the fractal took AWAY)**:
  1. Full custodian capture exposure on every cell — but on torus *most* cells are unused tactically anyway, so this is option-not-exercised.
  2. Smooth opening (any cell ≈ any other) — *removes* opening theory rather than adding it. Whether this is good or bad is taste; for novelty it is a minus.
  3. None that meaningfully matter under this rule set.

- **Recommendation for R17**: **second-probe**. The Pair B rule family masks the substrate's contribution: with no capture interaction in the body of the game, the hole-walls and corridor cells stay decorative. **Do not integrate `sierpinski` based on Pair B alone.** Wait for Pair C (connection win) results — the corridor-routing observation is the substrate's strongest claim, and Pair C is the rule family that would actually exercise it. If Pair C also returns Δ ≤ +0.3 then the substrate should be dropped per the spike's decision rule. If Pair C returns Δ ≥ +0.5, integrate `sierpinski` for connection-style rule families only (gated against threshold-race families like B).

### Quantitative summary table

| | Fractal | Control | Δ |
|---|---|---|---|
| Decisive turn (this team) | 21 | 21 | 0 |
| Winning-margin sum | 3.38 | 3.38 | 0 |
| P0 winrate (probe n=200) | 0.92 | 1.00 | −0.08 |
| Strategic Depth | 3 | 3 | 0 |
| Balance | 2 | 1 | +1 |
| Novelty | 3 | 3 | 0 |
| Substrate-novelty | 4 | 0 | +4 |
| Would play again | 3 | 3 | 0 |
