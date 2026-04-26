# Team-1 Evaluation — Game `1565501cfecf` (R15 GE champion)

**Team ID:** team-1
**Game ID:** 1565501cfecf (Gen 9; GE 0.318; parents b41d31d0a4f1 × afdcfe26f2c3)
**Evaluator note:** Single agent playing all three roles sequentially. Seat-identity bias acknowledged (Phase 3).

---

## Phase 1 — Rule Comprehension

**Board.** 2D, axis_size=8, total 64 cells. Topology = **torus** (edges wrap). Action space = 65 (64 placements + `a=64` = PASS).

**Turn structure.** **SIMULTANEOUS**, `pieces_per_turn=1`. Engine entry point `engine.step_simultaneous(a_p1, a_p2)`.
  - **Collision rule** (verified): if P1 and P2 submit the **same cell**, both pieces annihilate (`collision=True`, cell stays empty, neither piece is placed). Verified by placing both players on cell 27 on round 1 → owner stays 0, piece counts stay [0,0].
  - Legality is evaluated per-seat against the pre-tick board: if a cell is already owned (by either player), it is illegal for both; empty cells are legal for both seats and collisions only occur when both choose the same empty cell.

**Action types.** `place` only. No movement, no capture (`capture_rule.capture_type = "none"`).

**Placement rule.** `target=empty, constraint=anywhere, first_move_anywhere=True`. Any empty cell is legal; PASS (action 64) is always legal. **Double PASS → DRAW** (R15 rule).

**Capture / CA dynamics.** None. No cellular automaton (classic, non-CA). So no dead-rule issue here.

**Propagation (influence field).** `prop_type=influence, radius=3, strength=0.9657, decay=0.5867`.
  - Each piece contributes signed value (P1 positive, P2 negative) to its own cell and propagates outward up to radius 3 with geometric decay per step.
  - Measured values from a single P1 piece at (3,3): own cell +0.97, r=1 orthogonal +0.57, r=1 diagonal +0.33, r=2 +0.19, r=3 +0.04–0.10 (verified via `engine.board_values`).
  - Propagation wraps around the torus (influence field is toroidal).

**Win condition.** `condition_type=threshold, threshold=38.627, target_dimension=0, max_turns=100`.
  - Implementation (`engine_v2._check_threshold`): for each player, `effective = sum(board_values[c] for c owned by player)`, negated for P2 so P2's "score" is the sum of `-value` on P2-owned cells. Win if `effective > 38.627`.
  - **Tie-order bias (R15 flagged):** the check iterates `for player in (1, 2)` and returns on the first crosser. In simultaneous play, **symmetric mirrored strategies cross the threshold on the same tick → P1 always wins the tie.** I verified this directly (see Phase 2 games 1 & 2).

**Degeneracy checks.**
- Threshold is reachable: a 3×3 block of 9 same-colour pieces yields only 34.71, so **minimum 10 pieces** of a single colour are needed to exceed 38.627. Verified by placing a 3×3+1 shape (35 P1 pieces bordering the block, various extensions — all ≥39.3 at 10 pieces).
- Action 0-spam is NOT a degenerate winner (a single piece is 0.97; you need density).
- Games do terminate in ≤ max_turns if either side plays sensibly (in my three games all resolved in rounds 10–12).
- No CA, no dead-rule question.
- **The tie-order P1 bias means there is a structural first-mover effect in a supposedly simultaneous game** — the "simultaneous eliminates first-mover advantage" story is violated at the tactical crown.

---

## Phase 2 — Strategic Play

All moves engine-verified via `step_simultaneous` and legality pre-checked via `get_legal_actions`.

### Game 1 — Symmetric race (P1 and P2 mirror on max-distance corners)

Hypothesis: if both players race identical dense clusters at toroidal max-distance (Δ=(4,4)), both cross threshold on same tick.

| R | P1 | P2 | P1_sum | P2_sum | done |
|---|----|----|--------|--------|------|
| 1 | (0,0) | (4,4) | 0.97 | 0.97 | no |
| 2 | (1,0) | (5,4) | 3.06 | 3.06 | no |
| 3 | (0,1) | (4,5) | 5.83 | 5.83 | no |
| 4 | (1,1) | (5,5) | 9.72 | 9.72 | no |
| 5 | (2,0) | (6,4) | 13.54 | 13.54 | no |
| 6 | (2,1) | (6,5) | 18.49 | 18.49 | no |
| 7 | (0,2) | (4,6) | 22.70 | 22.70 | no |
| 8 | (1,2) | (5,6) | 28.71 | 28.71 | no |
| 9 | (2,2) | (6,6) | 34.71 | 34.71 | no |
| 10 | (3,0) | (7,4) | **38.92** | **38.92** | **done → P1 wins** |

**Result: P1 wins by iteration-order tie break.** No collisions. Fields barely overlap (Δ=4 > radius 3).

**P1 reflection.** Trivial — exact mirror of opponent, tie-break gives me the win. Engineering quirk converted a "draw by symmetry" into a structural P1 advantage. I wouldn't change anything as P1 in a symmetric scenario.

**P2 reflection.** Realized mid-game that a mirrored race is a loss because of the tie order. Needed an asymmetric plan. Continuing into Game 2.

### Game 2 — P2 tries mutual-collision disruption on round 8

Hypothesis: if P2 can predict P1's move and collide, both lose a tempo but tempo loss is equal. Maybe P2 can catch up if P1's follow-up is suboptimal.

| R | P1 | P2 | collision | P1_sum | P2_sum |
|---|----|----|-----------|--------|--------|
| 1–7 | top-left block | bottom-right block | — | 22.70 | 22.70 |
| 8 | **17 (1,2)** | **17 (1,2)** | **True** | 22.70 | 22.70 |
| 9 | (2,2) | (5,6) | — | 27.57 | 27.57 |
| 10 | (1,2)** refill | (5,6) mirror | — | 34.71 | 34.71 |
| 11 | (3,0) | (7,4) | — | **38.92** | **38.92** | done → P1 wins |

Collision at round 8: both pieces annihilate. Both players lose one tempo. Sums stay equal. Race resumes; threshold still crossed simultaneously → P1 wins by tie-break again.

Alternative tried: P2 builds cluster adjacent to P1 (at (3,3)) so influence fields overlap — same outcome, P1 still wins at R11 (both cross together).

**P1 reflection.** Two games in: I can play any density strategy and win as long as P2 mirrors. Even P2's collision-denial and P2's encroachment cost both equally because of symmetry.

**P2 reflection.** I need genuine asymmetry — either predict that P1 will not play optimally, or accept sub-threshold draws. Pure racing is losing for P2 against optimal P1.

### Game 3 — SEAT SWAP. I play P2. P1 plays a "center plus" opening (slightly less efficient than 3×3+1).

| R | P1 plan ((4,4) plus) | P2 plan (3×3+1 at (0,0)) | P1_sum | P2_sum |
|---|--------|--------|--------|--------|
| 1 | (4,4) | (0,0) | 0.97 | 0.97 |
| 2 | (3,4) | (1,0) | 3.06 | 3.06 |
| 3 | (5,4) | (0,1) | 5.83 | 5.83 |
| 4 | (4,3) | (1,1) | 9.26 | 9.72 |
| 5 | (4,5) | (2,0) | 13.35 | 13.54 |
| 6 | (3,3) | (2,1) | 17.83 | 18.30 |
| 7 | (5,3) | (0,2) | 23.17 | 22.51 |
| 8 | (3,5) | (1,2) | 28.32 | 28.32 |
| 9 | (5,5) | (2,2) | 33.60 | 33.60 |
| 10 | (4,2) | (3,0) | 37.56 | 36.89 |
| 11 | (3,2) | (3,1) | **39.52** | **39.52** | **done → P1 wins** |

As P2 I raced optimally but the "center plus" P1 shape turned out to be equally dense by round 10 (P1 had accumulated a full 3×3 around (4,4) plus edges). P1 still crossed first by tie-break.

**Supplementary test (off-record, not game 3 proper):** I ran P1 SCATTERED (pieces dropped far apart, e.g., 0, 15, 29, 41, 50, 33, 60, 7, 22, 48) vs P2 DENSE 3×3+1. P2 pulled ahead by round 5 and won at round 12 with P1 still at 20.5. **So P2 wins iff P1 mis-plays density.** Against an optimal-density P1, P2 cannot win even with optimal density of their own.

**P1 reflection (seat-swap aware).** Easy win from optimal play. The game gives P1 the tie on any symmetric crown.

**P2 reflection (seat-swap aware).** My most promising plays were aggressive mutual-collision predictions and cluster invasions — but none of them converted the tie-break against optimal density. **The only way P2 wins is if P1 is suboptimal.** This is a quantified P1 advantage.

### Convergence audit
- 3/3 games resolved by the stated threshold win condition (no double-pass draws, no max_turns timeouts).
- All terminated by round 11–12. No double-pass-draw flag triggered.

### Strategy Guides

**P1 strategy guide.** (1) Build a dense 3×3+1 cluster starting anywhere; (2) accept a mirror from P2 — you win the tie-break; (3) if P2 deviates to invade your cluster, grow your cluster in the unoccupied direction rather than fighting; (4) if P2 invades with a single sacrificial piece, your density is now slightly reduced (net ~4 value) but you still cross by round 11 while P2 has wasted a piece; (5) if P2 passes you gain tempo (you cross solo by round 10 while P2 stalls). P1 wins in every line.

**P2 strategy guide.** (1) Realize up front that optimal-dense P1 cannot be beaten by optimal-dense P2 — you are strictly beaten by tie-break. (2) Your only winning line is to exploit P1 mis-play: if P1 spreads pieces at Chebyshev distance > 2, race with your own 3×3+1 and you win. (3) Against an optimal P1, your best achievable outcome is a "maximum draw" — but R15 breaks the tie in P1's favour, so you lose. (4) Mutual-collision denial does not help: you and P1 each lose one tempo, the tie persists. (5) Single-sacrifice invasion (one piece dropped inside P1's cluster) reduces P1's sum but costs you a piece you'd rather have in your own cluster — net still a loss against optimal P1.

---

## Phase 3 — Strategic Analysis (joint P1+P2)

**Distinct viable strategies?** Two strategy families exist: (A) own-side racing (build dense cluster in open territory); (B) disruption (invade opponent's cluster or collision-deny). Against optimal-density play, (A) strictly dominates. (B) is a pure loss unless opponent plays sub-density. So **one approach (optimal density racing) dominates** at the equilibrium, with a narrow "punish the scatterer" exploit path.

**Meaningful counter-play?** Limited. The only counter to "opponent builds dense" is to build dense yourself; collisions and invasions don't yield a positive EV in mirror play. There IS counter-play against non-optimal opponents, but vs. optimal the game is deterministic (P1 wins).

**Short-term / long-term tension?** Very weak. Because capture is none and no reset mechanism exists, every placement is permanent and monotonically progresses the owner's score. There is no sacrifice-now-gain-later mechanic. The only inter-temporal decision is "which cell next" in the growing cluster — and that's essentially a fixed-order minimization.

**Emergent concepts?** 
- **Density is the only real concept.** Adjacency creates cross-contribution between pieces (each piece gets +0.57 from each r=1 neighbour, etc.), so clustered pieces multiply each other's effective value. This is strategically shallow but real.
- **Mutual-annihilation collisions** are mechanically present but strategically inert in mirror play (symmetric tempo loss). They might matter in less-symmetric positions but I didn't construct one where it flipped the result.
- **Toroidal wrap** is mechanically present but strategically inert for clusters of size ≤ 4×3 which fit inside a non-wrapping patch — never saw a move where wrap was the deciding factor.
- No ko, no initiative, no tempo in the Go sense. Closest analog: **Blotto with an exponential adjacency bonus**.

**Does topology matter?** Torus gives every starting cell equivalent value (no corner penalty, no edge effect) — this is actually a minus for strategic depth because it eliminates any positional decision. A 4×4 torus "position" is invariant under toroidal translation, so where you start the cluster is irrelevant. In a non-torus 8×8 the corners would be slightly weaker (less radius-3 coverage of empty cells) and positional theory would emerge — here it does not.

**First-mover advantage (simultaneous game).** **NOT eliminated.** Quantified: in 3/3 of my symmetric-mirror games P1 won by threshold iteration-order tie-break. This directly contradicts the stated R15 narrative that "simultaneous eliminates first-mover advantage". It trades a move-ordering first-mover advantage for a **threshold-iteration-order first-mover advantage**. Needs a rule change (e.g., draw on simultaneous crossing, or tie broken by piece count) to fix.

---

## Phase 4 — Novelty Adversary (mandatory)

**The adversary's case.** This game is a thin re-skin of existing abstract games; here are the specific charges:

(a) **vs. Go / territory games.** Influence-propagation radius-3 with decay ≈ 0.59 is a differentiable approximation of Go's liberty/territory framework. The "sum of signed field over your stones" win condition is a continuous version of area scoring. Go experts would intuit immediately: "build a big clump, stay connected, occupy many cells". Threshold 38.6 ≈ "control 10 live stones of territory". → very Go-like at the concept level.

(b) **vs. Reversi/Othello.** No — no flipping. Discard.

(c) **vs. Gomoku / Connect6 / Pente.** No — no line-forming objective. Discard.

(d) **vs. Conway's Life / Day-and-Night / HighLife.** Not CA-based; no transition table. Discard.

(e) **vs. Colonel Blotto / Blotto.** Strongest prior. Blotto is the canonical simultaneous resource-allocation game: each side secretly allocates pieces to 64 cells, score is a function of per-cell allocation. Here, both players allocate one piece per round on a cell, and score is `sum over your cells of (cell-value)`. The cell-values are determined by a fixed propagation kernel rather than by per-cell contest; but the **core mechanic — simultaneous allocation across a spatial resource, score-threshold winner** — is Blotto with a convolutional payoff. Proposed transformation: replace "64 Blotto fronts" with "64 cells + influence kernel K(r) = strength × decay^r"; the game is "1-per-round constrained Blotto on a torus with adjacency-amplifying payoff".

(f) **vs. Tumbleweed.** Tumbleweed has propagation-based influence and place-only mechanics on a hex board. Tumbleweed's "stack-if-you-see-more-friendly-lines-of-sight" is a close cousin to "sum-the-field-near-you". Strong structural analog.

(g) **vs. Slither.** Slither uses adjacency-based capture on a torus — different capture rule, discard.

(h) **vs. simultaneous Go (Gungo).** Gungo lets both players place simultaneously with collision rules. Exactly the same collision-annihilation rule here. Gungo + threshold win + continuous influence = this game. **Very close analog.**

**Re-skin transformation.** The game is **"simultaneous Go without capture, scored by influence-field sum rather than territory area count, with a fixed threshold win"**. Coordinate transform: identity (already a torus). Scoring transform: replace indicator-function territory with continuous convolution of K(r) = 0.97 × 0.587^r over placed stones.

**Would a Tumbleweed / Gungo / Blotto expert have an edge?** Yes. All three intuitions transfer: density matters, mirror is safe, simultaneous resolution favours hedging. A Go expert would play slightly worse (they would try to make eyes or liberties that are irrelevant here). A Blotto expert would immediately recognize "just cluster in one region" as optimal, which is the correct play.

### Rebuttal (from P1 and P2)

The Novelty Adversary is largely right. Concrete rebuttal attempts from Phase 2 strategic moments:

1. **Collision-annihilation with permanent loss** is NOT a standard Blotto or Go mechanic. In Blotto both sides' allocations are counted; here both sides' pieces are **destroyed**. This is Gungo-specific and genuinely distinctive — but **my Game 2 showed it has no strategic teeth in mirror play**, so it's distinctive-but-inert. Weak rebuttal.
2. **Continuous influence with decay 0.59, radius 3** is a *specific kernel* that is not literally present in any of Go/Blotto/Tumbleweed. However, the game's equilibrium (build a 3×3+1) depends only on "adjacency is good", which transfers directly. So the specific kernel doesn't generate novel strategy. Weak rebuttal.
3. **Tie-order threshold bias** in simultaneous play is a genuinely weird artifact not found in the classical analogs — but it is an engine *bug*, not a feature, and reduces novelty rather than adds it. Anti-rebuttal.
4. **No capture + threshold win** is unusual for Go-likes. Go-without-capture is a niche variant (sometimes called "No Capture Go"). But no capture + no life/death + pure field-sum means almost no tactical diversity. Weak rebuttal.

**Honest conclusion.** The game is close to "simultaneous Blotto on a torus with adjacency-kernel payoff" / "Gungo with threshold-and-influence". The distinctive ingredients (continuous influence kernel, simultaneous-annihilation, torus) each exist in prior games individually; their combination is not strongly innovative.

**Novelty score: 3/10.** Concrete, conservative. It is recognizably "Blotto/Gungo with a convolution kernel", not a new primitive. The 3 rather than 2 reflects that I couldn't find one prior game that has all three features together, but none of the three features is itself novel and their combination does not generate emergent strategy beyond the sum of parts.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** 1565501cfecf
**Rules Summary:** 8×8 torus, simultaneous 1-place per round, no capture, win by threshold on summed signed influence (radius-3, decay 0.59) over own cells; collisions annihilate both pieces; double-pass = draw.
**Topology:** 2D torus, axis=8 (64 cells).
**Turn Structure:** SIMULTANEOUS (step_simultaneous). Collisions annihilate both pieces.

### SCORES (1-10)

- **Strategic Depth: 3** — Only one real strategic concept (build a dense cluster, minimum 10 pieces). No sacrifice, no capture, no tempo trades, no ko, no long-term planning. "Which cell next inside the cluster" is the only decision after piece 1, and it's near-indifferent. The collision mechanic is mechanically interesting but strategically inert in mirror play.
- **Emergent Complexity: 3** — Cluster density is the single emergent concept. Invasion / cross-influence creates some secondary interactions (opponent-cell values flipped by local pieces) but these don't generate new strategy families — they reduce density on both sides roughly equally.
- **Balance: 3** — Seat-swap evidence: in 3/3 symmetric-mirror games P1 won by threshold iteration-order tie. Games 1 & 2 P1 won; Game 3 (seat-swapped, I played P2) P1 still won with a "center plus" opening. The only P2 wins I could construct required strictly suboptimal P1 density. Quantitatively: P1 wins 100% of mirror lines by tie-break; P2 needs P1 error to win. **The "simultaneous games eliminate first-mover advantage" hypothesis fails here because the threshold check has iteration-order bias.**
- **Novelty (post-adversary): 3** — Closest known analog is "Gungo with threshold-scored continuous influence kernel". All three defining features (simultaneous placement, toroidal influence, threshold win) exist in prior art; their combination is mildly novel but doesn't produce new strategic phenomena. The collision-annihilation is the most novel mechanic but it's strategically inert in practice.
- **Replayability: 3** — The dominant strategy collapses the game to a 10–12 round race with near-forced optimal play. Little reason to replay against a competent opponent. More replayable vs. a learning opponent while they figure out "cluster density > scatter".
- **Overall "Would I play this again?": 3** — I would not voluntarily play this. The first-mover (tie-order) bias makes competitive play unsatisfying.

### CLOSEST KNOWN-GAME ANALOG
**Gungo + influence-field scoring** (simultaneous Go with collision-annihilation, augmented with a continuous Tumbleweed-like kernel scoring). It's not identical because pure Gungo retains Go's capture rule and discrete territory scoring, whereas this game drops capture and uses a continuous convolution. The specific kernel parameters (strength 0.97, decay 0.59, radius 3) give it its own flavour, but equilibrium strategy is "cluster in one region", which is the Blotto/Tumbleweed solution.

### KILLER FLAWS
1. **Threshold iteration-order tie-break bias (R15-flagged):** in all symmetric-mirror lines P1 wins by being checked first. Converts the supposedly simultaneous game into a structurally first-mover-biased one. This is the game's dominant feature at the strategic crown.
2. **Dominant strategy (cluster 3×3+1):** ≥10 pieces in a compact cluster wins by round 10–12. No alternative family is competitive.
3. **No meaningful short/long-term tension:** capture is off, no reset mechanic → placements only monotonically build score. The game is essentially a constrained optimization over "choose a 10-cell connected subgraph of maximum summed self-influence" with a tempo component.
4. **Torus flattens positional structure:** every starting cell is equivalent, erasing a potential source of depth.
5. **Collision-annihilation is strategically inert in mirror play** — both sides lose symmetric tempo, the tie persists, P1 still wins. The mechanic exists but doesn't earn its keep.

### BEST QUALITY
**The collision-annihilation rule + influence-field scoring is a concise, clean simultaneous-game primitive.** Even though it's not strategically deep in this parameterization, the rule set is minimal and the mechanic reads clearly. The **influence-field visualizer** (signed field, P1=+, P2=−) is immediately interpretable, which is rare for procedurally-generated games.

### IMPROVEMENT IDEAS
**Break the threshold tie explicitly:** on simultaneous threshold crossing, declare a DRAW (rather than P1 wins). This restores the simultaneous-game premise. Alternatively, break by piece count (fewer pieces wins — rewards density efficiency) or by average cell value. Either change would eliminate the forced-P1 outcome in mirror play and force P2 to develop genuinely differentiated strategy, because **mirror = draw** becomes a live option rather than a tautological P2 loss.

Secondary improvement: **add capture** (e.g., any same-colour 3×3 locks the center cell permanently, or pieces with effective value < −0.5 are removed). This would introduce tempo and sacrifice dynamics that are entirely absent today.
