# Team-18 Evaluation — Game 992bf7dfc9f4 (Run 14)

Team ID: team-18
Game ID: 992bf7dfc9f4
Rank/metrics: R14 rank 5 by GE=0.4196, ELO 2953. Simultaneous + CA hybrid (the R15 premise candidate). Representation v4, generation 10 but listed as "seed game" (root of its lineage branch).

---

## Phase 1 — Rule Comprehension

**Board / topology.**
- 8x8 grid, 64 cells, 2D, von-Neumann (N/S/E/W) adjacency, no wrap (`topology_type=grid`).
- Observation: full. 2 players. 65-action space (cells 0..63 + action 64 = pass). Action index = y*8 + x.

**Turn structure — SIMULTANEOUS.**
- Both players submit moves the same tick. Resolution (from `engine_v2.step_simultaneous`):
  1. Same non-pass cell → **mutual annihilation** (both placements dropped; cell stays empty).
  2. Otherwise both placements land; captures apply (here: none, since capture_rule=none).
  3. **One CA step runs from "acting_player" = 1 if step_idx % 2 == 0, 2 otherwise**; steps_per_turn=1, so `i=0` always → CA ALWAYS runs from Player-1's perspective. This is a structural P1-bias (see flag below).
  4. Super-ko check; win condition check; max_turns check.
  5. Both passes → game ends by majority piece count.

**Action types.** Place only (no move). Placement constraint = `adjacent_to_own`, but `first_move_anywhere=True` — so a player's first piece (while they have 0 pieces) can go anywhere, including adjacent to enemy.

**Capture / propagation.** Both disabled (`capture_type=none`, `prop_type=none`). All dynamics come from CA.

**Cellular automaton (the interesting part).**
- Transition keyed by `(state, friendly_count, enemy_count)` where "friendly" is the acting player's colour. 75-entry table (3 states × 5 f × 5 e), **16 non-trivial / 59 identity**.
- Non-trivial rules (with perspective = acting_player):
  - BIRTH (s=0 → 1, i.e. empty spawns friendly): `(0,2,0), (0,2,1), (0,2,4), (0,3,4), (0,4,0), (0,4,1)` — 6 rules. Most common trigger: empty cell with ≥2 friendly neighbours and e ∈ {0,1}.
  - DEATH (s=1 → 0): `(1,0,2), (1,1,2), (1,1,3), (1,3,4)` — 4 rules. Isolated or over-attacked friendly pieces die.
  - CONVERSION friendly→enemy (s=1 → 2): `(1,0,1), (1,2,3)` — 2 rules. Critically, `(1,0,1)` flips an isolated friendly piece when a single enemy is adjacent.
  - CONVERSION enemy→friendly (s=2 → 1): `(2,2,0)` — 1 rule. Enemy surrounded by 2 friends & no enemies flips.
  - ENEMY DEATH (s=2 → 0): `(2,3,0), (2,3,2), (2,4,3)` — 3 rules.
- NO rule is of form "(0, f, e) → 2" — i.e. there is **no way for empty cells to spawn an ENEMY piece from any perspective**. Combined with steps_per_turn=1 fixing acting_player=1 every round, this means **Player 1's empty cells with f(P1)≥2 birth FREE P1 pieces every round**, and Player 2 never gets that privilege. P2 can only gain board material from placements.

**Win condition.** `territory` with threshold 0.6253 → **41 / 64 cells** needed. Max_turns = 100. If reached via double-pass, majority tie-breaks (P1 wins ties only if strictly >).

**Degeneracy flags (Phase-1 level).**
- **CA is P1-biased by construction.** The perspective-alternation in `step_simultaneous` only actually alternates across CA *sub-steps* within a round (`for i in range(steps_per_turn)`). With steps_per_turn=1 the loop fires once with `i=0 → acting=1`. This is almost certainly unintended by the generator (which presumably assumed steps_per_turn≥2) but is the *actual engine behaviour* we must evaluate. All three of my games confirm the bias empirically.
- CA rules do fire — 16 of 75 are non-identity, and several trigger every single round of normal play (I counted roughly 1–3 births per round throughout Games 1 and 2). This is not the "mostly dormant" failure mode from Run 13.
- The `first_move_anywhere=True` flag combined with rule `(1,0,1)→2` creates a dramatic opening counter for P2 (verified in Game 3): P2's first move can be placed directly adjacent to P1's first move, and the CA that round immediately flips P1's piece to P2. P2 finishes round 1 with **2 pieces to P1's 0**. This is a genuine strategic mechanic, not a bug.

---

## Phase 2 — Strategic Play

All moves engine-verified via `team18_sim_helper.py` (my thin wrapper around `engine.step_simultaneous`, because `play_helper.py --action play` uses `engine.step()` which naively alternates the current_player field and does NOT resolve simultaneous collisions/annihilations correctly for this game family). Helper at `/Users/jamesbrowne/aigame/team18_sim_helper.py`.

### Game 1 — "standard" openings

| Rd | P1 | P2 | After-CA P1 | P2 | Notes |
|----|----|----|----|----|----|
| 1 | 27 (3,3) | 36 (4,4) | 1 | 1 | no collision; both centre-diagonal |
| 2 | 19 (3,2) | 44 (4,5) | 2 | 2 | cluster start each |
| 3 | 20 (4,2) | 28 (4,3) | 3 | 3 | P2 blocks the birth at (4,3) |
| 4 | 26 (2,3) | 37 (5,4) | 5 | 4 | birth (2,2) for P1 |
| 5 | 25 (1,3) | 45 (5,5) | 7 | 5 | birth (1,2) |
| 6 | 24 (0,3) | 53 (5,6) | 9 | 6 | birth (0,2) |
| 7 | 12 (4,1) | 29 (5,3) | 11 | 7 | birth (3,1) |
| 8 | 13 (5,1) | 30 (6,3) | 14 | 8 | 2 births: (2,1), (5,2) |
| 9 | 14 (6,1) | 22 (6,2) | 16 | 9 | P2 blocks (6,2); birth (1,1) |
| 10 | 4 (4,0) | 31 (7,3) | 20 | 10 | **4-birth round**: (3,0),(5,0),(0,1),(4,0-placed) — CA cascade kicks in |
| 11 | 1 (1,0) | 23 (7,2) | 23 | 11 | births (0,0),(6,0) |
| 12 | 32 (0,4) | 38 (6,4) | 25 | 12 | birth (1,4) |
| 13 | 40 (0,5) | 39 (7,4) | 28 | 13 | births (1,5),(2,4) |
| 14 | 48 (0,6) | 47 (7,5) | 32 | 14 | **3-birth round**: (1,6),(3,4),(2,5) |
| 15 | 50 (2,6) | 43 (3,5) | 33 | 15 | P2 blocks (3,5); no birth |
| 16 | 58 (2,7) | 46 (6,5) | 35 | 16 | birth (1,7) |
| 17 | 51 (3,6) | 54 (6,6) | 38 | 17 | births (3,7),(0,7) |
| 18 | 52 (4,6) | 55 (7,6) | 39 | 18 | birth (4,7) |
| 19 | 7 (7,0) | 63 (7,7) | **41** | 19 | birth (7,1) → **P1 wins territory 41/64** |

Result: **P1 wins round 19 by territory**. Collisions: 0. No P1 pieces were ever killed or flipped.

### Game 2 — P1 off-centre opening, includes pass-exploit

| Rd | P1 | P2 | P1 | P2 | Notes |
|----|----|----|----|----|----|
| 1 | 18 (2,2) | 45 (5,5) | 1 | 1 | |
| 2 | 19 (3,2) | 44 (4,5) | 2 | 2 | |
| 3 | 26 (2,3) | 36 (4,4) | 4 | 3 | birth (3,3) |
| 4 | 20 (4,2) | 28 (4,3) | 5 | 4 | P2 blocks |
| 5 | 25 (1,3) | 37 (5,4) | 7 | 5 | birth (1,2) |
| 6 | 24 (0,3) | 29 (5,3) | 9 | 6 | birth (0,2) |
| 7 | 12 (4,1) | 30 (6,3) | 11 | 7 | birth (3,1) |
| 8 | 13 (5,1) | 21 (5,2) | 13 | 8 | P2 blocks (5,2); (2,1) birth |
| 9 | 4 (4,0) | 22 (6,2) | 17 | 9 | 3 births: (3,0),(5,0),(1,1) |
| 10 | 32 (0,4) | 31 (7,3) | 21 | 10 | 3 births incl (2,0) |
| 11 | 40 (0,5) | 39 (7,4) | 25 | 11 | 3 births |
| 12 | 48 (0,6) | 38 (6,4) | 30 | 12 | **4 gains**: placement + (0,0),(1,6),(3,4) |
| 13 | 56 (0,7) | 47 (7,5) | 34 | 13 | 3 births |
| 14 | **PASS** | 55 (7,6) | **36** | 14 | **Key find: P1 passes, still gains 2 births (3,6) & (2,7)** — CA fires every round |
| 15 | 52 (4,6) | 63 (7,7) | 38 | 15 | birth (3,7) |
| 16 | 53 (5,6) | 62 (6,7) | 40 | 16 | birth (4,7) |
| 17 | **PASS** | 61 (5,7) | **39** | 17 | **P1 piece (5,6) DIES**. P2's (5,7) blocks (1,1,2)-deaths on (5,6). P1 went 40→39 |
| 18 | 6 (6,0) | 46 (6,5) | **41** | 18 | birth (6,1) → **P1 wins** |

Result: **P1 wins round 18 by territory, 41–18**. Collisions: 0. **One P1 death** at round 17 — confirms the death mechanic is live. Pass-exploit confirmed: Round 14 pass still netted P1 +2 via CA births; key novel tactic.

### Game 3 — SEAT SWAP. Same reasoner plays "P2 aggressive" role, "P1 defensive" on first seat.

Deliberately opened with a sharp P2 first-move counter.

| Rd | P1 | P2 | P1 | P2 | Notes |
|----|----|----|----|----|----|
| 1 | 27 (3,3) | 35 (3,4) | **0** | **2** | **P2 first-move counter: CA rule (1,0,1)→2 flips P1's lone (3,3) into a P2 piece.** P2 finishes round with 2 stones, P1 with 0. |
| 2 | 0 (0,0) | 43 (3,5) | 1 | 3 | P1 re-opens in a corner (first_move_anywhere re-applies since count=0) |
| 3 | 1 (1,0) | 36 (4,4) | 2 | 4 | |
| 4 | 8 (0,1) | 34 (2,4) | 4 | 5 | birth (1,1) |
| 5 | 2 (2,0) | 44 (4,5) | 6 | 6 | birth (2,1) — P1 catches up |
| 6 | 3 (3,0) | 42 (2,5) | 8 | 7 | birth (3,1) |
| 7 | 4 (4,0) | 37 (5,4) | 10 | 8 | birth (4,1) |
| 8 | 5 (5,0) | 45 (5,5) | 12 | 9 | birth (5,1) |
| 9 | 6 (6,0) | 51 (3,6) | 14 | 10 | birth (6,1) |
| 10 | 7 (7,0) | 52 (4,6) | 16 | 11 | birth (7,1) |
| 11 | 16 (0,2) | 26 (2,3) | 18 | 12 | birth (1,2) |
| 12 | 19 (3,2) | 28 (4,3) | 20 | 13 | birth (4,2) |
| 13 | 21 (5,2) | 29 (5,3) | 22 | 14 | birth (6,2) |
| 14 | 18 (2,2) | 53 (5,6) | 24 | 15 | birth (7,2) |
| 15 | 24 (0,3) | 50 (2,6) | 26 | 16 | birth (1,3) |
| 16 | 30 (6,3) | 49 (1,6) | 28 | 17 | birth (7,3) |
| 17 | 39 (7,4) | 48 (0,6) | 30 | 18 | birth (6,4) |
| 18 | 47 (7,5) | 59 (3,7) | 32 | 19 | birth (6,5) |
| 19 | 55 (7,6) | 56 (0,7) | 34 | 20 | birth (6,6) |
| 20 | 63 (7,7) | 57 (1,7) | 36 | 21 | birth (6,7) |
| 21 | 32 (0,4) | 33 (1,4) | 37 | 22 | P2 blocks (1,4) birth; no CA gain |
| 22 | 40 (0,5) | 41 (1,5) | **37** | **23** | **P1 placement DIES**: (0,5) had f(P1)=1, e(P2)=2 after P2's (1,5) → (1,1,2) death; P1 0 net gain |
| 23 | 61 (5,7) | 58 (2,7) | 38 | 24 | (5,7) survives |
| 24 | **PASS** | **PASS** | 38 | 24 | **Double-pass ends game; majority P1 wins 38–24** |

Result: **P1 wins by DOUBLE-PASS MAJORITY, 38–24**. P1 DID NOT reach the 41 territory threshold — failed to find any legal move that would add a third piece (only remaining empty cells (0,5), (4,7) were all death-traps for any P1 placement). **This is the exact failure mode flagged in the eval prompt (double-pass majority exploit / timeout).**

### Per-player reflections

**P1 strategy guide.**
- Open (3,3) or nearby-centre. Cluster aggressively along an axis to manufacture f=2 empty cells every round; each birth is a free piece.
- Grow along edges — edge cells have 3 neighbours, so fewer f-slots needed for births; cascade easier.
- Once your cluster occupies ~5 rows, consider passing when you have no birth-creating placement, because CA will still fire in your favour.
- Avoid leaving any P1 piece with 0 P1 neighbours (invites `(1,0,1)` flip) and avoid isolated fronts where a P1 piece has 1 friend + 2 enemies (invites `(1,1,2)` death) — specifically the "one-cell-pokes-into-enemy-territory" shape.
- In the endgame you may saturate with placements that can't both grow and stay safe — plan to pass rather than die.

**P2 strategy guide.**
- **Open adjacent to P1's predicted first move**, exploiting the (1,0,1) flip if they open centre. If they don't, you've placed a safe stone anyway.
- Your pieces will never benefit from CA births — you only grow by placement and occasional `(2,2,0)` re-flips of overshot P1 pieces. Keep every P2 piece with ≥1 P2 neighbour (no isolation, since (2,0,x) is identity only for x=0,2; for x=1 it's identity too, actually fine — but a lone P2 is fragile to being isolated by subsequent P1 encirclement).
- **Late-game defence via death-trap.** If you can place at a cell adjacent to a P1 piece that currently has 1 friend and you provide a second enemy, `(1,1,2)` death fires and the P1 piece dies. I executed this in Games 2 (rd 17) and 3 (rd 22), killing one P1 piece each time. Kept the game from closing.
- Block candidate birth-cells that are 1-away from your own cluster (each block denies 1 free P1 piece).
- **You cannot win from behind** absent P1 errors. The structural asymmetry (CA bias) always favours P1 — but you CAN force double-pass majority if you hold enough territory, and you can delay the 41-threshold indefinitely by death-trapping the last remaining empty cells.

### Endgame resolution flag

Games 1 and 2 reached the stated territory threshold (41/64). **Game 3 resolved by double-pass majority** (38–24). That is 1 of 3 games — below the "≥2 of 3" Run-13 failure criterion, but close enough to flag. In that game the exploit was necessary because all remaining legal placements for P1 were one-round death-traps — endgame placement legality is the crux, not a full-board stall.

---

## Phase 3 — Strategic Analysis (joint)

**Viable strategies / dominance.** P1's dominant strategy is "compact cluster → f≥2 everywhere at front → CA snowball." Every reasonable P1 opening I tried produced similar win patterns in 18–20 rounds. P2 has two-and-a-half viable strategies: (i) first-move flip counter, (ii) perimeter blocking of specific birth cells, (iii) endgame death-traps to force majority resolution. None of these actually win — they slow P1 down.

**Counter-play.** Yes, partially. P2's Game-3 opening cost P1 ~6 rounds of growth; P2's death-trap in Game 2 killed one P1 piece. These are concrete, repeatable counter-tactics, not just stalling. But the CA structural bias limits P2 to damage-reduction.

**Short-term vs long-term tension.** Mild. The main tension is "place at an empty cell that births vs place at one that doesn't vs pass." Not much multi-move planning — CA is 1-step lookahead deterministic.

**Emergent concepts.**
- **Tempo via pass** (novel-feeling): passing is sometimes the best move because CA still runs. This would be perverse in Go but natural here.
- **Birth chains / cascades**: f=2-boundaries sweep across the board like a wavefront.
- **Death traps** via (1,1,2) deaths: a genuinely tactical micromoment.
- **Mutual annihilation**: never fired in my 3 games. Both P1 and P2 have strong incentives not to step on the same cell (P1 loses a birth, P2 loses its only growth lever), so collision avoidance is free — the mechanic exists but is latent.

**Does topology matter?** Moderately. 8×8 grid with von-Neumann means edges/corners reduce max-neighbours, which asymmetrises birth probability. Corner f=2 needs only 2 of 2 neighbours to be P1 (likely); interior f=2 of 4 is rarer. P1's corner-growth is demonstrably faster than interior expansion in all 3 games.

**First-mover advantage (seat-swap evidence).**
- Game 1: P1 won 41–19 at round 19. P1 never lost a piece.
- Game 2: P1 won 41–18 at round 18. One P1 piece died mid-game.
- Game 3 (seat-swap test, same reasoner): "P2 seat with strong reasoning" still lost 24–38 by double-pass majority. P2's opening-flip netted 2 pieces immediately AND P2 blocked several births, yet P1 still ran away with the game.

Conclusion: **simultaneous turn structure does NOT eliminate first-mover advantage in this game.** P1 wins decisively under both seat assignments. The bias is structural (CA perspective = P1-only) rather than temporal — simultaneous play cannot fix a rule asymmetry. Margin estimate: P1 wins ≥85–90% between strong players; the only way P2 scores is by surviving to max_turns (which requires active death-trapping) or by a P1 early blunder.

Residual seat-identity bias: same reasoner; Game 3 seat-swap gave "strong" reasoning to P2 and "defensive" to P1, and P1 still won. That's a reasonably strong data point against the asymmetry being bias-driven.

---

## Phase 4 — Novelty Adversary

### Adversary brief

**(a) Catalog comparison.**
- **Go.** Share placement-on-grid and territory-ish win. Differ fundamentally: no captures, no liberties, majority CA dynamics instead of chain-based capture. This game's 62.5% territory threshold + active board-birth mechanic is NOT Go. Expert Go players would have *zero* transferable life-and-death reasoning — there are no groups in the liberty sense.
- **Reversi / Othello.** Both flip stones via adjacency rules. But Othello flipping is direction-based-line-enclosure, not count-based neighbour automaton. The (2,2,0)→1 rule vaguely resembles Othello's "surrounded flips," but Othello requires a full line of enemy stones bracketed at both ends, not a 2-of-4 neighbour count. Not the same game.
- **Gomoku / Pente / Connect6.** Win by N-in-a-row; this game wins by count. Different family.
- **Hex / Y / Havannah / Tumbleweed.** Connection-based. This game has no connection condition.
- **Conway's Life / Day & Night / Immigration Game.** Closest CA analogs. Life rule is B3/S23 on uncoloured state. Immigration Game (Life with two colours) uses majority-colour-of-parents for births. This game's 6 birth rules indexed by (friendly, enemy) pairs generalise Immigration Game, but the specific table is NOT B3/S23 nor any published Life-like rule (B2,2-variants, death at (1,1,2), flip at (1,0,1)). It is structurally Immigration-Game-like (two-colour Life) but the actual rule-set is idiosyncratic — not a known named CA.
- **Simultaneous variants.** Diplomacy is move-resolution not placement. Blotto is resource allocation, no board. Scaled RPS is payoff-matrix. Gungo (simultaneous Go) resolves collisions by mutual removal — **this is the closest simultaneous-play analog, and the collision rule is identical.**
- **Amazons, Lines of Action, Chameleon, Slither, Nim.** Not structurally related.

**(b) CA-specifically.** Neither B3/S23 nor any entry in the common Life-like "Bxx/Sxx" catalog, extended with immigration colouring. The rule table is **idiosyncratic but not random**: death configs make physical sense (over-attacked pieces die), birth configs make sense (well-supported empties come to life), and the isolated-flip (1,0,1)→2 is a coherent "enemy captures a lone stone" rule. It is NOT a trivial perturbation of a named CA — I cannot match it to a known published rule.

**(c) Simultaneous-specifically.** Gungo (simultaneous Go) with collision → mutual-remove is the closest precedent. Gungo lacks CA. So this game is Gungo + Life-family CA, neither of which alone is novel, but the combination does not appear in the literature (that I am aware of in the abstract-strategy catalog).

**(d) Re-skin argument.** "This is Immigration Game + territory scoring + simultaneous moves + placement constraint." Under a topology transformation, not really — grid is natural for CA, no coordinate trick simplifies it. Under a semantic transformation, "two-player Immigration Game where players control next-placement and scoring is end-of-game territory" — that's a reasonable description, but Immigration Game has no placement step at all (it's pure automaton evolution from initial state). So the placement+CA coupling is genuinely non-trivial.

**(e) Expert transfer test.** A Conway's Life expert would have moderate transfer: understanding birth/death counts and what makes stable structures (blocks, beehives). A Go expert would have very little transfer. A Gungo or Diplomacy expert would have minimal transfer (only the simultaneous-submission discipline). No single game's expertise dominates.

### Rebuttal

**Specific moments where known-game analogies fail:**
1. **Game 3 round 1** — P2's (1,0,1) opening flip. A Go expert would never dream of placing adjacent to the opponent's only stone on turn 1 (it's an ataritable move with no support); here it's devastatingly effective. A Life expert recognises the pattern but Life has no adversarial placement. Uniquely enabled by place+CA+simultaneous composition.
2. **Game 2 round 14** — P1 PASSES and gains 2 pieces via CA. No adversarial game in the literature rewards passing with board gains; most penalise pass (Go ends game, Othello forces skip). The CA-then-pass exploit is unique.
3. **Game 2 round 17** — P2 plays (5,7) and P1's adjacent (5,6) dies via (1,1,2). The "place to kill by count" tactic is not in Go (no counts), not in Othello (no deaths of already-placed stones), not in Immigration Game (no adversarial placement).
4. **Game 3 rounds 22–24** — endgame where every legal P1 placement is a one-round suicide, forcing P1 into majority-win-by-pass. This configuration (territory unreachable but majority-secure) has no Go analog — Go doesn't have death-on-placement rules.

The adversary's strongest argument is **(b)-collapse**: "This is Immigration Game with a custom rule table plus placement plus simultaneous collision." That description is accurate. But the emergent interplay of (i) placement legality via `adjacent_to_own` creating tactical reachability, (ii) first_move_anywhere + (1,0,1) creating the opening counter, (iii) (1,1,2) death traps creating endgame sharpness, and (iv) pass being a growth-positive action for P1, collectively constitute a strategic texture that neither Immigration Game nor Gungo alone possesses. These are not paper-thin — I used each of them in one of the three games.

**Novelty score: 6/10.** Mechanically this is a known-archetype composition (Immigration-Game-like CA + Gungo-simultaneity + placement-constraint Go). But the specific rule table, and especially the structural P1 bias via step_simultaneous/steps_per_turn=1, means it is not an exact re-skin of any published game. The pass-as-growth and the (1,0,1) opening flip are concrete strategic phenomena I have not seen described elsewhere. Docks 4 points because (1) the P1-bias is likely an engine-level oversight rather than intentional design; (2) the strategy space collapses to a dominant P1 snowball with P2 damage-control, which is a thin solution tree; (3) the collision mechanic never fired in 3 games — it's latent rather than active.

---

## Phase 5 — Verdict

Team ID: team-18
Game ID: 992bf7dfc9f4
Rules Summary: 8×8 grid; simultaneous-placement two-player Immigration-Game-like CA with territory-majority win at 41/64, placement constrained to adjacent-own except first move, 16 non-trivial CA transitions, collision = mutual annihilation.
Topology: 8×8 grid, von-Neumann adjacency, no wrap.
Turn Structure: simultaneous.

SCORES (1-10):
- **Strategic Depth: 4** — P1's growth is largely formulaic (cluster + place adjacent + collect births); P2's counter-play is real but shallow (opening flip, blocking, death traps). Games converge in 18–24 rounds with little deep branching. Emergent ideas (pass-as-growth, (1,0,1)-opening) add ~1 point over pure formula.
- **Emergent Complexity: 5** — Birth cascades, death traps, pass exploits, and first-move flips are genuine emergent phenomena from the rule interaction. More interesting than a pure territory game but constrained by the P1-bias.
- **Balance: 2** — P1 wins overwhelmingly. Games 1, 2, 3 all P1 wins (41–19, 41–18, 38–24 majority). Seat-swap with same reasoner did not reverse outcome; the bias is structural not informational. Simultaneous play does NOT eliminate first-mover advantage here because the bias is in the CA perspective-selection, not the turn order. One of three games (33%) resolved by double-pass majority rather than the stated 41-cell threshold — close to the Run-13 failure mode.
- **Novelty (post-adversary): 6** — Closest prior art: Immigration Game (Life with two colours) + Gungo (simultaneous Go). Neither alone covers this; their composition plus placement-constraint and the specific custom CA table gives texture the adversary cannot reduce to "X-in-disguise." The pass-as-growth and (1,0,1)-opening are findings I cannot place in known literature. Strongest adversary argument: "custom Immigration-Game with placement." Rebuttal: placement + simultaneity + the specific 16-rule table produce opening, mid, and endgame phenomena that Immigration-Game alone (pure automaton) does not have.
- **Replayability: 3** — Opening is ~1 dominant P1 line + ~1 counter for P2; mid-game becomes shape-snowball; endgame resolves in 1 of 2 known patterns (threshold vs majority). Experienced players would converge to similar play quickly. Some texture from placement-constraint puzzles but not much.
- **Overall "Would I play this again?": 3** — Educational to play once to see the CA snowball and the Round-1 flip; not compelling for repeat play because P1 wins essentially by default and the strategic menu is small.

CLOSEST KNOWN-GAME ANALOG: Immigration Game (two-colour Conway-like CA) augmented with adversarial placement and Gungo-style simultaneous-collision resolution. Not identical because: no published Immigration variant uses this specific 16-rule non-trivial table; no published Gungo variant has a CA; no published game I know couples `first_move_anywhere` + `(1,0,1)` in a way that lets P2 flip P1's opening on round 1.

KILLER FLAWS:
1. **Structural P1 bias from steps_per_turn=1.** `step_simultaneous` loops `for i in range(steps_per_turn)` with `acting_player = 1 if i%2==0 else 2`. With steps_per_turn=1 only i=0 fires, always from P1's perspective. This makes every CA step P1-biased. It is arguably an engine bug manifesting at the game-generation level — generators that pair simultaneous + CA should require steps_per_turn ≥ 2.
2. **Dominant P1 strategy.** Game effectively solved: P1 clusters → snowballs → wins in ~20 rounds unless P2 pulls the round-1 flip AND P2 doesn't blunder.
3. **Double-pass majority resolution.** 1 of 3 games ended this way, without reaching the stated threshold. Not catastrophic (P1 still won by majority as expected) but the threshold rule is partially vestigial.
4. **Collisions never fire.** Both players are structurally incentivised to avoid the same cell, so the distinguishing feature of simultaneous play is dormant in practice.

BEST QUALITY: The CA genuinely fires and creates a growing-frontier dynamic that feels distinct from Go. The `(1,0,1)` opening flip for P2 and the `(1,1,2)` endgame death-trap are sharp, memorable tactical primitives. Pass-as-growth is a genuinely novel tempo notion.

IMPROVEMENT IDEAS:
- **Set steps_per_turn=2** so the CA alternates perspective within each simultaneous round. This would symmetrise births: empty cells with ≥2 P2 neighbours would also birth P2 stones each round, restoring balance. I expect this single change to lift Balance from 2 to ~6 and to elevate the overall game meaningfully — this is likely THE fix for the simultaneous+CA archetype. It is probably what the generator *intended*, and the fact that it produced steps_per_turn=1 is the real story for R15.

---

### Engine-verification audit

- Every move in all 3 games was submitted through `engine.step_simultaneous(action_p1, action_p2)` via `team18_sim_helper.py` before being committed to my notes. No hand-reasoning was allowed to override the engine.
- The standard `play_helper.py --action play` path was verified to NOT resolve simultaneous semantics (it calls `engine.step()` which alternates current_player), so I wrote a thin wrapper. This is a reporting caveat for other teams using `play_helper.py` on simultaneous games.
- Legal-action rejections I hit during play: (6,3)=23 confusion in Game 1 round 8 (I momentarily confused axis order; corrected to (6,3)=30). No other rejections.
- Tables and cell→coord mappings double-checked programmatically (`topo.cell_to_coords`); action_id = y*8 + x confirmed.

Helper scripts written for this eval (stored in repo root but not critical to keep):
- `/Users/jamesbrowne/aigame/team18_sim_helper.py` — simultaneous-play stepper.
- `/Users/jamesbrowne/aigame/team18_ca_analysis.py` — CA table decomposition (6 birth, 4 death, 3 conversion, plus the enemy-death triplet).
