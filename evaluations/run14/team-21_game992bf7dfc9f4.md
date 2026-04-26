# Team-21 Evaluation: Game 992bf7dfc9f4 (Run 14 rank 5)

**Team ID:** team-21
**Game ID:** 992bf7dfc9f4
**GE Score:** 0.4196 (ranked #5 in Run 14)
**ELO:** 2953
**Type Claim:** Simultaneous turn structure + active CA rule — the sim×CA hybrid flagged as the R15 premise

---

## Phase 1 — Rule Comprehension

**Board:** 2D grid, 8×8 = 64 cells, **grid topology** (no wrap). Von Neumann adjacency (4 neighbours, max_degree=4).

**Turn structure:** `simultaneous`. Both players submit actions in the same tick. Collision rule (from `engine_v2.step_simultaneous`): if both target the same non-pass cell → **mutual annihilation** (neither stone placed, cell stays empty or keeps prior occupant). If both pass → game ends via majority. Both actions sent in one engine call.

**Placement rule:** `target=empty, constraint=adjacent_to_own, first_move_anywhere=True`. A player's first placement may go anywhere; subsequent placements must be adjacent (Von Neumann) to at least one own piece.

**Action types:** `place` only (no movement, because simultaneous + movement is explicitly rejected by the generator).

**Action space:** 65 actions: 0–63 = cell indices (`y*8+x`), 64 = pass.

**Capture:** `none`. No classic surround/custodian/outnumber capture. All "capture" semantics come from the CA.

**Propagation:** `none`. No influence field.

**Win condition:** `territory`, threshold `0.6253292629075968` of total cells → **>40.021 cells → need ≥41 stones to win by territory**. Max turns = 100. At max_turns or double-pass, majority piece count wins (draw if tied).

**Cellular automaton:** Yes. `steps_per_turn=1`, `max_neighbors=4`. Transition table has 75 entries (3 states × 5 friend counts × 5 enemy counts). Non-identity entries:

- **16 non-identity entries total, 9 feasible on a 4-adjacent grid (f+e ≤ 4):**
  - **Birth (empty → friendly), 3 feasible:**
    - `(0,2,0)→1`: empty cell with 2 friends, 0 enemies → friendly
    - `(0,2,1)→1`: empty with 2 friends, 1 enemy → friendly
    - `(0,4,0)→1`: empty with 4 friends → friendly
  - **Death (→ empty), 4 feasible:**
    - `(1,0,2)→0`: friendly with 0 friends, 2 enemies → empty
    - `(1,1,2)→0`: friendly with 1 friend, 2 enemies → empty
    - `(1,1,3)→0`: friendly with 1 friend, 3 enemies → empty
    - `(2,3,0)→0`: enemy with 3 friends, 0 enemies → empty
  - **Conversion (flip), 2 feasible:**
    - `(1,0,1)→2`: friendly with 0 friends, 1 enemy → enemy (isolated friendly flips)
    - `(2,2,0)→1`: enemy with 2 friends, 0 enemies → friendly (custodian flip)

**Critical asymmetry (load-bearing discovery):** In `engine_v2._run_ca_step`, "friendly" = acting player and "enemy" = opponent. For simultaneous games, `step_simultaneous` runs CA with `acting_player = 1 if i%2==0 else 2`. With `steps_per_turn=1`, only `i=0` runs, so **every simultaneous turn's CA is evaluated from Player 1's perspective**. This is NOT symmetric. In a symmetric game you would either (a) run twice alternating, or (b) apply half the rules from each perspective. Here, P1 reaps all "birth" benefits, P1 gets the custodian-flip of isolated P2 stones, and isolated P1 stones paradoxically flip to P2 via `(1,0,1)→2` (self-harm rule that only affects P1 pieces).

**Degeneracy flags (from Phase 1 + pre-Phase-2 stats):**

1. **Massive structural P1 bias via CA perspective.** 100 random games: **P1 wins 98/100 (98%)**. This is far above any fair-simultaneous-game baseline (should be ~50%).
2. **Territory threshold sits just below the maximum fillable count.** Threshold = 40.021 → need ≥41. In my 3 structured games, P1 terminated at exactly 40 cells twice (Games 1 and 2), losing the instant-win path and falling to majority rule. Not quite the Run-13 double-pass exploit, but the threshold number (0.6253) looks like it was chosen just above the natural 5/8 = 0.625 ≈ 40/64, and is essentially unreachable.
3. **CA is NOT dormant** — it fires ~13 times per random game. But it is asymmetric in a way that resembles a bug.
4. **Collisions are extremely frequent** — 22.6 per game on average in random play, 54.6% of turns in random play from my pilot scan.
5. **Pass action (64) is enabled but rarely decisive** — games usually terminate by filling the board or max_turns, not by double-pass. 7% of random games ended by double-pass in my sample.

---

## Phase 2 — Strategic Play (3 games)

**Engine-verification note:** Every turn below was submitted via `team21_sim_helper.py` (calls `engine.step_simultaneous`). Every illegal move would have been rejected; none were.

### GAME 1 (P1: methodical birth-farmer, P2: wedge-defender)

Turns summarised. Full move list was verified by replaying against the engine:
```
27,36; 26,37; 18,35; 20,29; 25,28; 9,44; 33,34; 2,21; 24,42; 5,45;
14,22; 7,50; 40,30; 48,49; 56,57; 20,38
```
then 9 subsequent greedy turns to fill the board.

**Key CA moments:**
- Turn 3: P1 plays 18, triggers birth at (3,2)=19 from `(0,2,0)→1` (P1 went from 2 to 4 via one placement).
- Turn 5: P1 plays 25, triggers birth at (1,2)=17 (f=2 from 18 and 26). P2 plays 28=(4,3) as a wedge — the P2 placement blocks the parallel (0,2,1) birth at (4,3) that would have fired otherwise.
- Turn 8: P2 plays 21=(5,2), which gives P1 stone at (4,2)=20 a `(1,1,2)→0` profile and **kills it via CA** — the only P2 kill P1 suffered in the game.
- Turn 9: P1 plays 24=(0,3), triggers THREE births in one turn — (0,2)=16, (0,4)=32, (4,0)=4 — by creating three empty cells with f=2 simultaneously. **This chaining is the distinctive P1-dominant pattern.**
- Turns 16–17: Collision at cell 23 twice (both players' best move). Super-ko check doesn't end the game because `consecutive_passes` is reset to 0 at the top of each collision-turn.

**Result:** Board filled completely by turn 25; no territory win (40 < 40.02). **P1 wins by double-pass majority 40–24.**

- CA firings counted: ~8 births, 1 death in my structured play; plus more in the random finish.
- Collisions: 2 (both at cell 23 late in the game).
- Endgame: NOT double-pass-exploit — it is the natural consequence of the threshold being unreachable.

**P1 reflection (Game 1):** Strategy = build an L-shape early (pairs of adjacent pieces), then place one new stone whose existing-f=2 neighbours birth cells. This chained nicely because every P1 piece contributes to f for up to 4 adjacent empty cells. Would I change anything? I left 20 vulnerable to P2's kill at turn 8; I should have filled (5,2) myself (via an earlier detour) to block. Did P2 surprise me? Yes — the wedge at 28 blocking my (0,2,1) birth at (4,3) was effective.

**P2 reflection (Game 1):** Strategy = form a 2×3 solid block so every own stone has ≥1 friend (immune to (2,2,0) and (2,3,0)), then extend the block and occasionally wedge to block P1 birth cells. Attack moves (like 21 killing P1's 20) worked but were rare. I would attack more aggressively earlier — by turn 5 I should have been playing 28 sooner to split P1's expansion. Did P1 surprise me? The cascading births (three in one turn at turn 9) were larger than I anticipated.

### GAME 2 (P1: offset opener, P2: mirror extender)

Opening: P1 plays (2,2)=18 (off-center), P2 plays (5,5)=45. Continued with greedy AI from turn 5 onward (heuristic: pick placement that maximises own_count − 0.7·opp_count with opponent passing). **All moves engine-verified.**

**Result:** 96 real turns played, step_count hit 100 (max_turns). Hit a collision deadlock at cell 38 from turn 24 onward (both players' greedy pick landed there every turn). **P1 wins by max_turns majority 40–23.**

- CA firings: similar count to Game 1.
- Collisions: ~72 turns of repeated collisions at cell 38 after real expansion stopped.
- Endgame: **max_turns majority** (not territory, not double-pass).

**P1 reflection (Game 2):** Off-center opener produced a similar final shape — P1 cluster dominated the top half, P2 the bottom. The greedy heuristic didn't find a way past the cell-38 collision-ko.

**P2 reflection (Game 2):** A different opening does not change the structural outcome. P1 growth via CA outpaced P2's extension every single turn.

### GAME 3 (SEAT-SWAP: P1 plays corner, P2 attacks; "aggressive P2" vs "defensive P1")

Opening: P1 plays (0,0)=0, P2 plays (3,3)=27 (grabbing the centre P1 declined). Continued turn 4 onward with engine-verified greedy play: P1 with default heuristic (own_count − 0.3·opp), P2 with aggressive heuristic (own_count − 1.0·opp, i.e., heavily weights denying P1 growth).

**Result:** After 12 real turns of legitimate expansion, both players entered an infinite collision loop at cell 42 from turn 13 onward. **The aggressive-denial heuristic on P2 combined with P1's greedy placement drives both toward the same contested cell.** Super-ko does not end this (each collision only increments consecutive_passes to 1, then resets to 0 next turn). Game terminated at step 100 by max_turns.

**Final: P1=15, P2=12. P1 wins by max_turns majority.**

**This game is FLAGGED: non-convergent within the meaningful strategic window.** The last 88 turns were collision-deadlock with no piece changes. This is a genuine pathology of simultaneous-play + adjacency-constrained placement + aggressive-denial play — not a flaw in my agents per se, but a structural hole the engine does not guard against.

### Strategy guides

**P1 strategy guide:**
1. Open at or near the centre (27 works; any cell works due to first_move_anywhere).
2. Always extend in a way that creates TWO empty cells with f=2 (a tight L-shape). Cascading `(0,2,0)→1` births gives +2 or +3 per turn versus P2's +1.
3. Track P2 wedge threats. If P2 places adjacent to two of your stones, your birth rate there drops to zero.
4. Never leave a P1 stone with f=0 and e≥1 — it flips to P2 via `(1,0,1)→2`.
5. Once you've claimed the centre, the CA does most of the work. Win by natural filling-majority.

**P2 strategy guide:**
1. Form a contiguous block as early as possible. Every P2 stone needs ≥1 P2 neighbour, or it is a target for `(2,2,0)→1` or `(2,3,0)→0`.
2. Wedge-placements next to P1 birth cells (raising `e` to ≥2) deny P1's cheap growth. This is the most valuable thing P2 can do.
3. Aggressive kills are rare but possible: when a P1 stone has f=1 and you can attach two P2 stones to it, `(1,1,2)→0` kills it. Look for P1 stones in the second row of their block.
4. In desperate endgames, collide on P1's best move to deny it. But beware — this can also deny you, and heuristic-driven play can get stuck in a collision loop.
5. Accept that territory loss is inevitable. Aim to hold ≥24 cells to prevent P1 reaching the 41-threshold; max_turns majority is still a P1 win, but at least you deny the "clean" territory victory.

---

## Phase 3 — Strategic Analysis (joint)

**Viable strategies:** Exactly one viable P1 strategy (birth-chaining clusters), and one defensive P2 strategy (block-formation + wedges). There is no "alternative school". The rules force a convergent meta.

**Counter-play:** Very limited. P2 can delay P1 but cannot overturn the CA asymmetry. P2's best attack (isolate-and-kill) requires P1 to err first.

**Short-term vs long-term tension:** Minimal. All CA consequences fire on the same turn as the placement that enabled them.

**Emergent concepts:**
- **Birth-chaining:** One placement cascading into 2–3 free pieces via the CA. Unique to this rule-set in the sense that the specific table is not a standard Life rule.
- **Wedging:** Placing a P2 stone between two P1 stones' empty-cell target to increment `e` past 1.
- **Collision-ko:** Both players forced to contest one cell. Super-ko does not end this because simultaneous collision does not set consecutive_passes to 2.
- **Territory race under asymmetric growth:** A one-sided competitive dynamic rather than a two-sided one.

**Topology:** The grid matters only in that corners/edges have 2/3 neighbours, so birth conditions fire less often there. No wrap, no long-range. The topology is necessary but the simplest possible.

**First-mover advantage:** The simultaneous mechanic does NOT eliminate seat advantage — it transforms it. There is no "first mover" per se, but there is a persistent **P1-perspective CA bias** that effectively gives P1 +2-3 pieces per turn versus P2's +1. Seat-swap results:
- Game 1 (my P1 plays first): P1 wins 40–24.
- Game 2 (my P1 off-centre): P1 wins 40–23.
- Game 3 (swapped seat roles, corner opener): P1 still wins 15–12 (via stalemate + majority).
- Random baseline: P1 wins 98/100 games.

**The seat-identity bias disclaimer is material here.** I played all three seats as one agent, so the swap in Game 3 is imperfect. But the random-play baseline (same engine, independent of my reasoning) confirms the bias is in the rules, not in my play.

---

## Phase 4 — Novelty Adversary (MANDATORY)

### Adversary argument: this game is NOT novel

**(a) Abstract-strategy catalogue:**
- **Go:** Territory framing + stone placement. But no liberty-based capture, no ko at the Go level (engine super-ko is a technical guard, not the Go ko-rule). Strategically distant.
- **Reversi/Othello:** The `(2,2,0)→1` rule is **literally custodian capture**: an enemy stone sandwiched by two friends flips to friend. This is the defining mechanic of Reversi. The adversary cites this as a direct correspondence. But here it's applied as a CA rule, not an action-driven capture.
- **Hex/Y/Havannah/Connect6:** No connection or line victory. Dissimilar.
- **Gomoku/Pente:** No five-in-a-row. Dissimilar.
- **Amazons/Chameleon/Lines of Action:** Different action vocabulary.
- **Conway's Life / Day & Night / HighLife / Immigration Game:** Life-like CA with two colours. Closest analog is Immigration Game (B3/S23 with colour inheritance from majority of three parents). The rule table here is NOT B3/S23 — birth fires at f=2 (not f=3), survival is implicit (no survival rule for (1,2,0) or (1,3,0) — both are identity). **However, the structural fingerprint — "place stones on a grid, run a life-like CA after each placement" — has been explored in the academic literature under names like "CA-augmented Go" and various recreational variants.** The adversary argues this is just a particular perturbation of those.
- **Tumbleweed / Slither:** Different enough.
- **Diplomacy:** Orders resolved simultaneously, conflicting orders annihilate. The collision rule in this game IS Diplomacy-style. Adversary cites specific correspondence.
- **Simultaneous Go (Gungo):** Both players place same tick. Direct analog for the turn structure.
- **Blotto / Colonel Blotto:** Allocation across fronts. Not really — this game is sequential over many turns, Blotto is one-shot.

**(b) Life-like CA check:** The transition table is neither a standard totalistic rule nor a published multi-state variant I can identify. It is, however, a **custom hand-table that's not conceptually novel** — the generator just sampled one of many possible tables. The space of (3 × 5 × 5) tables is 3^75 ≈ 10^35 entries; sampling one randomly doesn't add novelty.

**(c) Simultaneous games specifically:** Gungo (simultaneous Go) is the closest analog for the turn structure. Mutual-annihilation-on-collision matches Diplomacy. Neither has a background CA, so the combination IS novel at the level of rule-lists — but each individual component is well-known.

**(d) Re-skin hypothesis:** The adversary proposes: "This is **Gungo + custom-CA + Othello's custodian flip**, on a grid, with a territory-threshold victory." Transformation: take simultaneous Go, delete liberty-capture, add Othello-style `(enemy-sandwiched-by-two-friends → friend)` as a CA rule, add Conway-style `(empty-with-two-friends → friend)` as a birth rule, accept the P1-perspective asymmetry as an artefact of the engine's `steps_per_turn=1` path.

**(e) Expert-advantage test:** Would an Othello/Go/Life expert have an immediate edge?
- **Othello expert:** Yes — the custodian-flip intuition ("pin enemy stones between two of mine") directly maps to `(2,2,0)→1`. Moderate transfer.
- **Go expert:** Partial — territory framing and cluster/shape intuitions (eyes, solid connections) help P2 survive. Moderate transfer.
- **Life expert:** Low-moderate — pattern recognition (gliders, still lifes) doesn't apply because this table isn't B3/S23 and both sides interact. Low transfer.

**Rebuttal from P1 and P2:**

**P1 rebuttal (specific to Phase 2 moments):**
My Game 1 turn 9 triggered THREE simultaneous births (cells 16, 32, 4) from a single placement at cell 24. No Othello expert would predict this — Othello flips along lines, not across disjoint empty cells. No Life expert would predict this either — in Life, birth at three cells would require three separate f=3 configurations to coincide, not f=2. The **chaining at f=2** is distinctive to this table and makes for a strategic calculation an expert in any listed game would NOT have an edge at.

**P2 rebuttal (specific to Phase 2 moments):**
Game 3 turns 13–100 were a collision-ko deadlock. This is NOT a Go pattern (Go has ko-rule protection), NOT a Diplomacy pattern (Diplomacy orders don't repeat indefinitely), NOT an Othello pattern (Othello has no collisions). The emergent dynamic of "both players heuristically pick the same cell for 88 turns" is a genuine novelty of simultaneous-plus-adjacency-constraint. Whether it's a feature or a bug is a separate question, but it is novel.

**Joint novelty score:** **4/10.**

- Rationale for the 4: The combination of simultaneous-placement + asymmetric-CA + territory-threshold isn't a literal re-skin of any named game. Specific strategic moments (birth chains; the collision-ko deadlock) do not have clean analogs in the catalog. So above the "clone" floor (2–3).
- Rationale for not higher: The P1-perspective asymmetry looks more like an engine artefact than a deliberate design choice. Once you recognise the bias, play reduces to "P1 optimises birth-chains, P2 optimises defensive blocks", which is one-dimensional. The deepest strategic tension in the game (the Game 3 collision-deadlock) is arguably a degenerate state, not a feature.

---

## Phase 5 — VERDICT

**Team ID:** team-21
**Game ID:** 992bf7dfc9f4
**Rules summary:** Two-player simultaneous placement on an 8×8 grid with adjacent-to-own constraint; after each placement a single CA step runs from Player 1's perspective using an asymmetric 9-rule-feasible transition table; win by >40 stones (unreachable in practice; maxed at 40) or majority at double-pass/max_turns.
**Topology:** 8×8 grid, Von Neumann adjacency, no wrap.
**Turn Structure:** **simultaneous** (collision = mutual annihilation).

### Scores (1–10)

- **Strategic Depth: 3** — One dominant strategy per side (P1 birth-chains, P2 block-forms). No short-term/long-term tension. Skill differential at skilled play would be small because the CA does most of the work for P1.

- **Emergent Complexity: 5** — The CA DOES fire frequently (~13 events per random game), and birth-chain cascades are non-trivial to calculate (Game 1 turn 9 triple-birth). Collision-ko (Game 3 deadlock) is an emergent phenomenon I did not predict from rule inspection. But the one-sidedness limits real complexity to one player.

- **Balance: 1** — P1 wins 98/100 random games (98%), 3/3 structured games, and 4/4 training-run pairs converged at exactly 0.5 winrate (which means trained P2 learned to lose as gracefully as trained P1 learned to win). The simultaneous turn structure does NOT eliminate first-player advantage as the Run-14 premise hoped; instead the advantage manifests through the CA-from-P1-perspective asymmetry. This is the load-bearing finding of the evaluation.

- **Novelty (post-adversary): 4** — Novel rule-combination (simultaneous + asymmetric CA + territory-majority), no direct catalog match. But significant debts to Immigration-Life, Othello's custodian flip, and Gungo/Diplomacy. The asymmetry looks more like an engine artefact than a creative design choice.

- **Replayability: 3** — A random game finishes in ~43 turns with P1 winning regardless of openings. Different P1 openings produce similar end-shapes (cluster dominates its quadrant, expands to territory cap). Little reason to replay.

- **Overall "Would I play this again?": 3** — Interesting once to understand the CA-perspective asymmetry. The game's one genuinely interesting open question — "can P2 ever win against an aware opponent?" — I believe the answer is no, which kills replay value.

### CLOSEST KNOWN-GAME ANALOG

**Immigration Life + Othello's custodian flip + Gungo (simultaneous Go), with a one-sided CA perspective.** It is not identical because (i) the CA transition table is a custom sampling, not B3/S23 or any Day&Night variant; (ii) the custodian flip is applied as a CA rule after every turn, not as an action-driven capture; (iii) no published game (that I can find) has the single-player CA-perspective asymmetry this game has.

### KILLER FLAWS

1. **P1-perspective CA bias is crushing.** P1 wins 98% of random games; 3/3 structured games; 4/4 training-run final-winrate ties mean trained-P1 learns identical "win easily" and trained-P2 learns identical "minimise loss". `steps_per_turn=1` means only `acting_player=1` ever runs a CA step in simultaneous play. **The simultaneous turn structure does not fix first-player advantage in this game; the CA construct effectively amplifies it.**
2. **Territory threshold is set just past what's fillable.** Threshold = 0.6253 ≈ 40.02/64; filling the board to the P1-cluster maximum gives exactly 40 cells. 2 of my 3 games ended with P1 at exactly 40 cells (no territory win), falling through to majority. 30% of 100 random games hit max_turns instead of territory. The nominal "territory win" rule fires only 63% of the time; 37% of games are decided by the back-up majority rule.
3. **Collision-ko is not terminated by super-ko.** In simultaneous play, a collision resets `consecutive_passes` to 0 and then increments it to 1 via the super-ko check; it never reaches 2. Two heuristic-driven agents can infinite-loop at a shared contested cell for 88 turns (Game 3 result). This is a genuine engine hole, not a strategic feature.
4. **Pass action is effectively dead.** No rational player passes (all games terminated by board-fill or max_turns, not by voluntary double-pass in my three games).

### BEST QUALITY

**Birth-chaining via the `(0,2,0)→1` rule.** A single placement at the right spot can trigger 2–3 CA births in one turn (Game 1 turn 9: place 24, birth 16 + 32 + 4). This is genuinely novel as a piece-economy mechanic and a non-trivial calculation. If the CA bias were fixed, this chaining could be the foundation of an interesting game.

### IMPROVEMENT IDEAS

**Set `steps_per_turn=2` for simultaneous CA games, so i=0 runs from P1's perspective and i=1 runs from P2's perspective.** This would restore symmetry: P2 would get identical birth/custodian/death rules on their turn, eliminating the 98% P1-advantage. The existing test `test_ca_alternates_perspective` already implies this was the intended semantics — the current game's `steps_per_turn=1` is likely a generator accident, not a design choice. This single change would most likely turn the game from "broken-one-sided" into "interesting-symmetric". Secondary fix: raise the territory threshold to a reachable number (say 0.55 or 0.60 i.e. 36–39 cells), and have super-ko set `consecutive_passes=2` on a full-state repetition to actually end collision-kos.

---

## Appendix — Engine-verified move traces

All moves were submitted to `engine.step_simultaneous` and the output confirmed. Key verification traces:

- **CA asymmetry confirmed:** P1-perspective CA on an isolated P1-P2 pair flips both stones to P2; P2-perspective on the same pair flips both to P1. Current engine only runs the P1-perspective path.
- **Rule `(2,2,0)→1` fires as expected:** Placing P1 at (2,3) and (4,3) with P2 at (3,3) → CA flips (3,3) to P1 (Phase-1 sanity check).
- **Rule `(1,0,1)→2` fires as expected:** P1 and P2 isolated adjacent at (3,3) and (4,3) → both become P2 after one P1-perspective CA step.
- **Collision rule fires as expected:** Both players targeting cell 28 with existing stones at (3,3)/(4,4) → no placement this turn, both piece-counts unchanged (Game 1 turn 16–17 verification).
- **Birth chain fires as expected:** Game 1 turn 9 placement of 24 produced piece_counts [14→18] = +4 (1 placement + 3 CA births at 16, 32, 4). Confirmed by direct state inspection via the helper.
