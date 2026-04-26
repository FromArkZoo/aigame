# Team-22 Evaluation — Game 992bf7dfc9f4

**Run 14 rank 5**, GE 0.4196, ELO 2953, v4 representation. Marketed as the SIMULTANEOUS + active CA hybrid, the "R15 premise" candidate.

---

## PHASE 1 — RULE COMPREHENSION

### Board
- 8×8 grid (64 cells), `topology_type=grid`, von Neumann adjacency (4 neighbors, fewer on edges/corners).

### Turn structure — SIMULTANEOUS
- `turn_type=simultaneous`, `pieces_per_turn=1`. Both players submit one action per round; resolved together.
- **Collision rule:** if both play the same cell, mutual annihilation — neither stone is placed, cell stays empty.
- Non-colliding placements both land on the board.

### Action space
- 65 actions total (64 placements + pass). `action_rule.action_types=['place']`.

### Placement constraints
- `target=empty`, `constraint=adjacent_to_own`, `first_move_anywhere=True`.
- CRITICAL: the "first-move-anywhere" predicate triggers whenever the player currently has **zero pieces** — not just on literal move 1. If a player's pieces all disappear (via CA death/conversion), they can re-place anywhere.

### Capture — none.

### Propagation — none.

### Cellular Automaton (`steps_per_turn=1`, `max_neighbors=4`)
- Totalistic player-symmetric table mapping `(state, friendly_count, enemy_count) → new_state`. Table has 75 entries, 16 non-identity nominally.
- **Reachability analysis:** on a grid with 4 max neighbors, `f+e ≤ 4`. Filtering: **only 9 non-trivial transitions are ever reachable**. The other 7 (e.g. `(1,2,3)→2`, `(0,3,4)→1`) require ≥5 neighbors and are **dead rules**.
- **Acting-player asymmetry (LOAD-BEARING):** With `steps_per_turn=1`, the engine always runs one CA step per round and its loop uses `acting_player = 1 if i%2==0 else 2`. At `i=0` this is **always P1**. So the CA *always* evaluates with "friendly = P1". The rule table itself is NOT symmetric under 1↔2 swap, so "friendly" vs "enemy" is not interchangeable.

The 9 live rules, expanded (1=friendly/P1, 2=enemy/P2):

| key | meaning | effect |
|---|---|---|
| (1,0,1)→2 | isolated P1 next to 1 P2 | **P1 flips to P2** |
| (1,0,2)→0 | isolated P1 with 2 P2 | **P1 dies** |
| (1,1,2)→0 | P1 with 1 friend, 2 enemies | **P1 dies** |
| (1,1,3)→0 | P1 with 1 friend, 3 enemies | **P1 dies** |
| (0,2,0)→1 | empty with 2 P1, 0 P2 | **P1 birth** |
| (0,2,1)→1 | empty with 2 P1, 1 P2 | **P1 birth** |
| (0,4,0)→1 | empty fully surrounded by P1 | P1 birth |
| (2,2,0)→1 | P2 with 2 P1 neighbors, 0 P2 | **P2 converts to P1** |
| (2,3,0)→0 | P2 with 3 P1, 0 P2 | **P2 dies** |

**Asymmetry summary:**
- P1 has 3 birth rules (from empty). **P2 has zero birth rules.** (No transition `(0,*,*)→2` exists in the table.)
- P1 pieces can die OR flip to P2; P2 pieces can die OR flip to P1. But the conversion requires 2 adjacent pieces of the other color. P1 can convert P2 via `(2,2,0)→1`; P2 converts P1 only via the weaker `(1,0,1)→2` (flips a totally isolated piece, without needing a flanker pair).
- Net: **CA is structurally pro-P1.** Empirically verified: tight P1 clusters birth ~2 new P1 pieces per round; P2 never gains anything from CA.

### Win condition
- `condition_type=territory`, `threshold=0.6253...`. Win requires **> 40.02 cells** (i.e. ≥41 of 64).
- `max_turns=100`. On either a double-pass or max turns reached, the game is decided by simple piece-count majority.

### Degeneracy flags
1. **CA player-asymmetry.** The CA table is strongly pro-P1 (births and conversions favor P1); `steps_per_turn=1` forces the only active step to be from P1's perspective, cementing the bias.
2. **Round-1 flank attack.** If P1 opens at a high-degree cell (interior) and P2 plays an adjacent cell, P1's opener is immediately flipped to P2 by `(1,0,1)→2`. P2 leads 2-0 after round 1. P1 must play defensively (corner/edge, hope P2 doesn't flank) — but with `first_move_anywhere`, even after losing their opening piece, P1 can re-seed anywhere, effectively resetting.
3. **Double-pass majority exploit confirmed.** In 3/3 of our games the winning player never reached the 41-cell territory threshold; the game terminated by mutual pass once neither side could expand further. Win went to whoever had more pieces.
4. **7 of 16 nominally non-trivial CA rules are unreachable** (f+e > 4). A more careful fitness function would penalize this.

---

## PHASE 2 — STRATEGIC PLAY

All moves engine-verified via `step_simultaneous`. Full move logs embedded in `/Users/jamesbrowne/aigame/evaluations/run14/team-22_driver.py` runs.

### Game 1 — P1: "central opener + birth-chain", P2: "central counter + block contested cells"

- R1: P1=27, P2=36 (diagonal, no flank → both pieces survive).
- R2: P1=26 (build column), P2=28 (aims for future 27 kill).
- R3: P1=35, P2=35 → **first collision**, both annihilated.
- R4: P1=19, P2=29 → first CA birth fires: cell 18 = `(0,2,0)`, births P1. P1 leads 4-3.
- R5-9: P1 plays 17, 34, 10, 2, 8. Each placement triggers **1-2 births** because P1 builds tight 2x2 clusters that saturate empty cells with 2 P1 neighbors. P2 plays 20, 35, 43, 42, 41 — pure placements, no CA benefit.
- R9 end: P1=17, P2=8. P1 has a 4×4 wedge in NW quadrant.
- R10-11: both sides contest cell 12 → double collision. CA still fires for P1 from stale birth triggers (cell 24 and 32 birth because adjacent P1 pieces are now there). **This is the "snapshot lag" phenomenon: births can fire even when both players collide.**
- R12-23: slower +1 per round phase. P1 experiences CA kills on its edge salients (cells 47, 58 die via `(1,1,2)→0` when flanked by 2 P2). P2 cannot convert any P1 cluster (all P1 pieces have ≥2 P1 friends — the convertible state `(2,2,0)` never materializes for P2).
- R31: double pass. Final P1=35, P2=27. **P1 wins by majority, not by territory threshold.**

### Game 2 — P1: "central opener", P2: "ADJACENT FLANK attack"

Test whether P2 can exploit `(1,0,1)→2`.

- R1: P1=27, P2=28 → **P1's 27 flips to P2 via CA.** P2 leads 2-0; P1 is pieceless.
- R2: P1 (pieceless, `first_move_anywhere` re-triggers) plays corner **0**; P2 plays 36.
- R3-7: P1 builds a corner 2×N block. CA births fire as soon as P1 has 2 adjacent pieces (cells 9, 10, 11 all birth in the first 3 rounds of corner expansion).
- R7 end: P1=10, P2=8. **P1 has already regained the lead despite losing the opening piece**, because the CA birth engine compounds faster than P2 can expand from the center.
- R25: double-pass. **Final P1=35, P2=25. P1 wins.**

Takeaway: the P2 flank attack is Pyrrhic — it wins 1 piece immediately but gives P1 license to restart in a corner, which is the *ideal* birth-engine terrain.

### Game 3 — SEAT SWAP. Primary reasoning as P2; P1 played by same agent as a "fair opponent".

- R1: P1=27, P2=28 → P1's 27 flips (repeating game-2 opening to see if a smarter P2 build can exploit).
- R2-10: P1 rebuilds corner {0,1,8,9,2,10,3,11-wait 11 is P2}. I (as P2) tried a new plan: **extend aggressively NORTHWARD into row 1 to block P1's east-side births.** Placed P2 pieces at 11, 12, 13, 14, 15 along row 1.
- R10 end: P1=11, P2=11 **TIED**. The blocking strategy worked — row 1 is a P2 wall, denying P1's east-side birth sites.
- R11-18: P1 still births on the SW flank (cells 16, 17, 24, 25 birth in sequence). I continue to extend but each of my placements is only +1, while P1's placements often trigger +2 via birth.
- R26: double-pass. **Final P1=39, P2=25. P1 wins.** P1 reached 39, just short of 41, and mostly through compounded CA births on the SW quadrant.

### Player reflections

**P1 strategy guide:**
1. Open anywhere, but expect a round-1 flank loss from a smart P2. It's recoverable.
2. If flanked, restart in a corner — `first_move_anywhere` re-fires when you're pieceless.
3. Build tight 2×N blocks. Every "2 P1 adjacent to an empty cell" is a guaranteed birth next round.
4. Don't send salients into P2 territory without 2 P1 escort pieces. Lone/paired P1 stones next to 2 P2 die via `(1,1,2)→0`.
5. When legal moves dry up, pass — the double-pass path wins you any game you lead on piece count.

**P2 strategy guide:**
1. Flank P1 at round 1 — the 2-0 tempo is real.
2. After that, you have no CA engine. Play for territorial density and try to wall off P1's birth fronts.
3. Avoid spreading thin: a P2 stone with 0 friendly + 1 enemy flips via `(1,0,1)` applied in reverse — actually wait, this rule is specifically for P1 pieces. P2 stones are safe from this since the rule table is asymmetric. But P2 stones with `(2,2,0)` convert, so always keep ≥1 P2 support adjacent.
4. Recognize that **you cannot win a cleanly-contested game**. Your only realistic win path is if P1 opens badly AND you prevent recovery — essentially impossible given `first_move_anywhere` re-firing.
5. Don't pass first unless you are ahead on piece count. Passing ends via majority.

### Convergence / outcome type

| Game | P1 | P2 | End type | Reached territory threshold? |
|---|---|---|---|---|
| 1 | 35 | 27 | double-pass | No |
| 2 | 35 | 25 | double-pass | No |
| 3 | 39 | 25 | double-pass | No |

**3 of 3 games ended via double-pass majority.** This is exactly the failure mode flagged in Run 13 and the evaluation prompt. The territory threshold (>40.02 cells ≈ 41) was never reached, though game 3 got closest (39).

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Did simultaneous play eliminate first-mover advantage?
**No — it inverted it locally and then P1 won globally anyway.**

- **Round-1 mechanic:** The SIMULTANEOUS turn structure combined with the `(1,0,1)→2` CA rule creates a one-round tactical advantage for **P2**, not P1: if P2 plays adjacent to P1's opener, P1 loses their piece. We verified this empirically in games 2-3.
- **Long-run dynamic:** The CA birth rules (`(0,2,0)→1`, `(0,2,1)→1`, `(2,2,0)→1`) all produce P1 pieces. P2 gains nothing from the CA. Over 20-30 rounds this +2-3 pieces/round compounding overwhelms the 2-piece round-1 loss.
- **Seat-swap result:** In game 3 (seat swap), the "P1" seat still won 39-25. Across 3 games, **P1 won 3/3 by margins of 8-14 pieces.** Seat identity trumped any round-1 advantage P2 had.
- **Bias disclaimer:** All three games were played by the same reasoner, so cross-seat bias cannot be fully controlled. But the dominant effect is clearly the CA rule asymmetry (structural, provable), not a subjective bias.

### Viable strategies / counter-play
- P1 has ~2 strategic archetypes: (a) build tight core for birth maximization; (b) ignore P2 and race to 41. In practice both converge.
- P2 has no equivalent. Every P2 strategic choice is defensive: flank, block birth fronts, or spread to maximize placements. None of them win.
- **Verdict: dominated game.** P1 has a dominant meta-strategy; P2 has no counter.

### Short vs long term tension
Limited but present:
- P1 must sometimes choose between (a) building safely deep in own territory (+3 pieces/round via birth), and (b) sending salients toward P2 that risk CA death. Salients risk `(1,1,2)→0`; rational P1 usually passes on salients.
- P2 must choose between tactical flank (round 1 +2) and building territory fast. No real tension later because P2's placements are all +1.

### Emergent concepts
- **Birth chains** are the central emergent phenomenon: placing one stone in the right spot triggers 1-2 CA births in the same round, creating +2-3 piece rounds for P1.
- **Collisions** happened in 2-3 rounds per game over ~25-30 rounds. They matter only when the contested cell is tactically critical (e.g. cell 35 in game 1, cell 12 in game 1). The simultaneous-annihilation mechanic is the one genuinely novel feature but is rarely used because the rest of the game incentivizes spatial separation.
- **Territorial walls** emerge as each player saturates an arm of the board; boundaries become stable because adjacent-to-own-only placement prevents crossing.
- No ko, no tempo in the Go sense, no sacrifice patterns.

### Topology matters?
Weakly. 8×8 grid is generic. Corner/edge cells have 2-3 neighbors, which reduces CA density. The only topology-specific effect is that **corner play is stable for P1 because edge pieces can't be flanked on all sides**, and P2 can't reach corners easily due to adjacent-to-own constraint.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary opens

**This game is a mild perturbation of well-known mechanics, not a novel contribution.**

(a) **Catalog comparison.**
- **Go?** No capture, no liberties, no territory scoring beyond raw piece count. The `adjacent_to_own` constraint is closer to Gomoku / Connect6 placement rules than Go's place-anywhere rule.
- **Reversi/Othello?** The CA conversion rule `(2,2,0)→1` and `(1,0,1)→2` are literally flipping rules. They are **weaker Othello**: Othello flips along an entire line bounded by two of your pieces; here you only flip stones that are *adjacent* to you under a specific neighbor-count condition. This is "Othello on a CA timer," not a new mechanic.
- **Conway's Life / Day&Night / HighLife?** The transition table is a 2-color Life variant. The rules `(0,2,0)→1` and `(0,2,1)→1` are birth rules with minimum 2 neighbors — a reduced-threshold Life. The death rules `(1,0,2)→0`, `(1,1,2)→0` are overcrowding/isolation deaths. This is a 2-color Life variant. There is a whole literature on 2-color Life (Immigration Game, QuadLife, etc.). The specific table may be new, but it's a standard construction.
- **Gomoku / Connect6?** Closest match for the simultaneous variant: a known Gomoku variant ("Connect6") places 2 stones per turn. Our game places 1 each simultaneously, but the strategic feel (place adjacent to own, build toward threshold) is similar.
- **Slither / Tumbleweed / Hex / Havannah / Amazons?** Not a match — those use different movement/capture structures.
- **Blotto / Colonel Blotto?** No resource allocation; our game places 1 stone at a time.
- **Gungo (simultaneous Go)?** YES — closest match. Gungo is a known simultaneous variant of Go with mutual-annihilation on same-cell collision. Our game removes Go's capture and scoring, adds a Life-like CA overlay, but the **simultaneous-placement-with-collision is not novel.**

(b) **CA-specific check.**
The specific transition table has:
- Birth from empty at 2-neighbor threshold — same as the B2 birth rule in Life-likes. "B2" CA rules are well-documented (e.g. "Seeds" is B2/S — pure birth, no survive).
- Death from 2+ enemy neighbors — this is an "immigration" variant where states have owners.
- Conversion rules `(1,0,1)→2` and `(2,2,0)→1` — these are the "Immigration Game" or "QuadLife" flavor.
This is a **2-color Life with modified B2/S234 bands.** Not a new CA.

(c) **Simultaneous-specific check.**
The collision = mutual annihilation rule is literally **Diplomacy's support-and-bounce logic** applied to a grid, and **Gungo's same-intersection rule.** Not novel.

(d) **Reskin hypothesis.**
This game is "**Seeds-like 2-color CA with owner semantics + Gungo's simultaneous placement + Gomoku's adjacent-to-own placement + majority-count scoring.**" Every ingredient exists in the literature; only the specific combination is "new", and even then the combination is almost equivalent to running a 2-color Life where players seed cells on their turn.

(e) **Expert-carry-over test.**
Would a Conway's Game of Life expert immediately understand this game? **Yes.** They would immediately identify:
1. "Birth at 2 neighbors → tight clusters grow."
2. "Death at 1 friend + 2 enemies → avoid weak salients."
3. "With simultaneous play, I want to seed in safe clusters and let the CA do the work."

Nothing about this game's strategy requires understanding that isn't covered by Life + Othello + simultaneous-place primitives.

### Rebuttal from players

Specific moments from play that break the analogies:

1. **`first_move_anywhere` re-firing when a player goes pieceless** (game 2, round 2: P1 plays at corner 0 after losing piece) is not in Gungo or Life. This is a genuine rule quirk — call it "phoenix rule" — but it also undermines the ostensible novelty by making the game resistant to the tactical flank exploit.

2. **Snapshot-lag CA births during a collision round** (game 1, rounds 10-11: P1 gains pieces from cell 24 and cell 32 even though both players collided at cell 12). This is emergent from the simultaneous-step+CA-step interaction. A Life expert would need a minute to work this out but it is derivable from first principles.

3. **Tactical 2:1 conversion** (`(2,2,0)→1`): To convert a P2 stone you need **two P1 escorts** plus the target cell being orphaned from P2 support. This is more demanding than Othello's line-flipping but simpler than Go's group-capture. Distinctive but not emergent.

No Phase-2 moment was "un-analogizable". Every tactical decision mapped onto existing Life-like or Gomoku-like heuristics.

### Novelty score: **3/10**

The game is a combinator of three known mechanics (2-color Life, Gungo-simultaneous, Gomoku adjacent-to-own) with a win-by-threshold-on-territory. The specific combo is uncommon but not genuinely novel. The CA rule table is strongly asymmetric (favors P1), which makes this more of an **imbalanced Life variant** than a balanced game.

Scoring reasoning: it's not "X on a hex board" (→ 2) because the CA layer does add active mid-round dynamics. But it's also not 7+ because every mechanic has a direct, well-known ancestor and the tactics transfer cleanly.

---

## PHASE 5 — VERDICT

- **Team ID:** team-22
- **Game ID:** 992bf7dfc9f4
- **Rules Summary:** 8×8 grid with SIMULTANEOUS placement (same-cell collisions → mutual annihilation), placements must be adjacent to own, and a 2-color Life-like cellular automaton runs once per round from P1's perspective. Win by owning >40 of 64 cells or by majority on double-pass.
- **Topology:** 8×8 grid, von Neumann adjacency, `axis_size=8`.
- **Turn Structure:** SIMULTANEOUS (explicit).

### SCORES (1-10)

**Strategic Depth: 4** — Two real decision axes: (1) where to build to maximize birth triggers, (2) collision-risk management. The second is thin because only 2-3 rounds per game have contested cells. Branching is constrained by `adjacent_to_own` + small legal action sets (often ≤10 per player). Endgame is rigid — players pass once expansion dries up.

**Emergent Complexity: 4** — Birth chains, snapshot-lag births during collisions, and conversion tactics (`(2,2,0)→1` requires a 2-escort setup) are genuine emergent behaviors. But they are not surprises — Life-like intuitions predict them all. No emergent concepts that required re-thinking.

**Balance: 2** — **Strongly P1-biased.** The CA rule table produces births and conversions that always benefit P1 (because `steps_per_turn=1` locks the perspective). P2 has no CA engine. P1 won 3/3 games by margins of 8, 10, and 14 pieces. Training runs show P1-vs-P1 final winrate = 0.500 (random draws between symmetric agents), but cross-seat evaluation isn't captured by those metrics — they are self-play on the CA-asymmetric engine. Seat-swap game 3 still produced a P1 win.

**Novelty (post-adversary): 3** — Closest analog: 2-color Life with Gomoku-style placement and Gungo-style simultaneous resolution. Every ingredient is catalogued; the specific blend is uncommon but transfers cleanly to a Life-expert intuition.

**Replayability: 3** — With P1 dominance confirmed and only ~65 legal actions collapsing to ~5-10 after a few rounds, replay value is low. The round-1 flank gambit adds one strategic layer but doesn't create variety.

**Overall "Would I play this again?": 3** — Playable once for the CA curiosity, but not a game I'd reach for. The imbalance kills competitive interest.

### CLOSEST KNOWN-GAME ANALOG
**Gungo (simultaneous Go) + 2-color Conway's Life.** Not identical because (a) Gungo uses Go scoring and no CA, (b) 2-color Life doesn't have player placements. This game is the Cartesian product, but the product has fewer strategic dimensions than either parent.

### KILLER FLAWS
1. **CA player-asymmetry** — birth and conversion rules structurally favor P1. The `steps_per_turn=1 + acting_player = 1 if i%2==0 else 2` construction makes this unavoidable. The R14 CA design should have enforced that the CA table is symmetric under 1↔2 swap, OR run two CA steps per round (alternating perspective) to nullify the bias.
2. **Double-pass majority exploit — all 3 games.** The stated territory threshold (>40.02 cells) was never reached. The game resolves by piece-count majority on mutual pass, which defeats the purpose of having a territory threshold.
3. **7 of 16 nominally non-trivial CA rules are unreachable** on the grid topology (require f+e > 4). The apparent rule complexity is inflated.
4. **Round-1 CA tactic creates no real game tension** because the losing side re-spawns via `first_move_anywhere`.

### BEST QUALITY
The mutual-annihilation-on-collision mechanic combined with CA-birth-on-snapshot creates one interesting scenario: a P1 can deliberately play into a collision to let a CA birth fire "for free" in an adjacent cell. This is the most novel micro-tactic in the game (game 1 round 10-11 demonstrated it), though it was not decisive.

### IMPROVEMENT IDEAS
**Make the CA table player-symmetric** (enforce `rule(s,f,e) ↔ rule(swap(s),e,f)` with states also swapped). This would neutralize the P1 structural advantage and force players to compete on placement strategy alone. A secondary improvement: run the CA as **two steps per round with acting-player alternating**, so both perspectives fire each round, restoring symmetry dynamically even with an asymmetric table.

Alternative improvement: remove the `first_move_anywhere` re-firing when pieceless. This would make the round-1 flank attack a genuine strategic decision (preserving the simultaneous-play interest) rather than an immediately-undone gambit.
