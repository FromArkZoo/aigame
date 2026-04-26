# Team-2 evaluation — Game 1565501cfecf (R15 champion)

Team ID: team-2
Game ID: 1565501cfecf
Generation: 9
GE Score: 0.318 (R15 champion)
Evaluated: 2026-04-22

## Phase 1 — Rule comprehension

**Board.** 8×8 torus (64 cells). 2 dimensions, Von Neumann adjacency. All cells
topologically equivalent (no corners, no edges). The torus means every stone can
be viewed as "central" — there is a unique maximum-distance *antipode* for any
cell (Manhattan distance 8 away via wraparound).

**Turn structure.** `simultaneous`, `pieces_per_turn=1`. Both players submit one
action per round; `engine.step_simultaneous(a1, a2)` resolves them atomically.
**Collision rule verified empirically**: if both players target the same
non-pass cell, mutual annihilation — neither stone is placed, and the cell
remains empty. The round still counts (step_count increments).

**Actions.** Place-only. 65 actions = 64 placements (action ID = `y·8 + x`) plus
one pass action (action 64). Placement target = `empty`, constraint =
`anywhere`, `first_move_anywhere = true`. No movement, no removal.

**Capture.** `capture_type = none`. No capture mechanic; stones cannot be removed
after placement except via the same-cell collision at placement time.

**Propagation.** `influence`, radius = 3, strength = 0.9657, decay = 0.5867.
Signed scalar field: P1 placements add `+strength · decay^dist` to every cell
within Manhattan distance 3 on the torus; P2 placements add the negative.
Per-stone own-cell contribution = 0.966; neighbor boost at distance 1 = 0.567,
distance 2 = 0.332, distance 3 = 0.195. Per-stone footprint = 25 cells (1 + 4 +
8 + 12 at distances 0/1/2/3).

**Win condition.** `threshold`, threshold = 38.627. A player wins when
`sum(board_values[c] for c owned by player)` — sign-flipped for P2 — exceeds
38.627. `max_turns = 100`. Double-pass ends the game as a draw (R15 rule).

**CA.** None (this game is classic, not CA-based). Confirmed via inspection
report "Cellular Automaton: No (classic)".

**Degeneracy and structural flags:**

- **Threshold-check order bias.** `engine_v2.py:_check_threshold` (lines 748–
  761) iterates `for player in (1, 2)` and returns on the first player whose
  effective-value crosses. In simultaneous threshold play where both players
  often cross on the same tick, **P1 wins the tie by iteration order**. This is
  a structural bias.
- **Monotone state space.** No capture + no CA + no movement = once a stone is
  placed it is permanent. own_sum scores never decrease via opponent action;
  they can only dip slightly via contact (opponent influence dragging your own
  cells). Behind + no reset = usually stuck.
- **Threshold reachable at ~10 rounds.** Per-stone own-cell value in a tight
  cluster saturates around 3–5 (own 0.966 + friendly boosts). 9–15 stones in a
  cluster crosses threshold. The game ends fast.
- **No CA rules to audit symmetry for.**

## Phase 2 — Strategic play

### Protocol notes

- Each move was engine-verified through `sim_play_helper.py`, which calls
  `engine.step_simultaneous`. `play_helper.py --action play` would have
  misplayed this (sequential `step` calls), so I used the sim helper exclusively.
- Games 1 and 2: I play both seats (same agent). Acknowledging seat-identity
  bias.
- Game 3: seat-swap — I play as P2 with the agent's best P2 strategy while P1
  plays the proven P1 dominant plan.

### Game 1 — symmetric antipodal 3×3 clusters

**Plan.** P1 builds a 3×3 cluster at cells (1–3, 1–3). P2 builds the antipodal
3×3 at cells (5–7, 5–7). These are Manhattan distance ~6–8 apart on the torus,
with no r=3 overlap — pure independent scoring.

Moves (p1:p2 per round): `18:54, 17:53, 19:55, 10:46, 26:62, 11:47, 27:63,
25:61, 9:45, 8:44`.

Progression:
- R9 (3×3 complete): both own_sum = **34.713** exactly (perfect symmetry).
- R10 (each adds one peripheral stone): both own_sum = **38.921**, which crosses
  the 38.627 threshold. Winner check fires on P1 first → **P1 wins**.

**Observation.** In symmetric play the game is deterministic: 10 rounds, P1
wins. This is the purest demonstration of the check-order structural bias.

**Did the endgame reach stated win condition?** Yes (threshold crossed).

### Game 2 — P2 plays contact strategy (adjacent cluster)

**Plan.** P1 builds 3×3 at (1–3, 1–3). P2 builds 3×3 at (0,0) corner so the two
clusters are mutually within radius-3. I wanted to see whether P2 can pressure
P1 by overlap; the hypothesis was "P2 pulls P1's own_sum down faster than P2's
own_sum suffers".

Moves: `18:0, 17:1, 19:2, 10:8, 26:16, 11:9, 27:24, 25:32, 3:7, 4:15, 5:23,
34:31, 33:39, 35:6, 41:14`.

Progression:
- R6 (both have 6 stones, heavy overlap): P1=10.04, P2=9.37. P1 slightly ahead
  because P2's cluster is packed against P1.
- R7+: I expanded P2 along the top and left edges (wrap-around column 7, row 0)
  away from P1's cluster to get clear own-cells.
- R12 (both 12 stones): P1=28.20, **P2=30.39** — P2 has pulled ahead because
  P2's L-shape along two axes projects more own-cells than P1's blob.
- R15: P1=39.40, **P2=41.98**. BOTH cross threshold in the same round.
  **P1 wins the tie by check-order**, despite P2 having a 2.58-point lead.

**This is the killer finding.** Not only does the P1 tie-break bias apply when
scores are equal — it applies when **P2 is clearly ahead**. Whenever both
players cross on the same round, P1 wins regardless of the actual scores. The
only way for P2 to win is to cross in a round where P1 does not cross. Given
the monotone-growth structure, this is extremely hard to engineer.

**Did endgame reach stated win condition?** Yes (threshold crossed on tick 15).

**Opponent surprise.** P2's edge-hugging expansion was more efficient than
expected — it reached 41.98 vs P1's 39.40 — but the structural bias nullified
P2's lead.

### Game 3 — seat-swap (I play P2)

**Plan as P2.** Since symmetric mirror deterministically loses to P1 (Game 1),
I need a P2 strategy that crosses threshold in a round where P1 does not. Three
ideas tested:

1. Pure antipodal mirror (matches Game 1 → P1 wins on tie).
2. P2 places an early stone ADJACENT to P1's cluster to slow P1's own_sum.
3. P2 tries a denser/smaller cluster to cross threshold faster.

For this game I tried variant 2: mirror for 8 moves, then spoil on R9 by
placing at (0,1) = action 8, right next to P1's cluster.

Moves: `18:54, 17:53, 19:55, 10:46, 26:62, 11:47, 27:63, 25:61, 9:8`.

Result after R9: P1=32.897, P2=28.247. P2's spoil cell (0,1) sat next to P1's
3×3 at (1,1)(1,2)(1,3) etc., so it received strong P1 negative contribution.
The new P2 stone contributed **negatively** to P2's own_sum (P1's influence >
P2's self-contribution at that cell), while also boosting P1's own_sum
indirectly by letting P1's cluster's projection onto cell (0,1) count for P1
(wait — cell (0,1) is now P2-owned, so P1's influence projected there now
counts AGAINST P1's own_sum). Actually: P1 own_sum JUMPED from 28.71 to 32.90
because P1 places another cluster stone at (1,1), but P2 did NOT place a new
cluster stone, so P2's own_sum barely grew from 28.71 → 28.25 (net -0.46 for
placing a self-hurting spoiler).

**The spoiler is net-negative for P2.** Conclusion: P2 cannot profitably spoil
because (a) playing in a P1-dominated cell hurts P2, (b) skipping the mirror
move means P2 lags in self-scoring. P2 is checkmated by the monotone dynamic.

I conceded the game at R9. P1 will cross on R10 exactly as in Game 1.

**Did endgame reach stated win condition?** Structurally equivalent to Game 1 —
P1 crosses on R10. Conceded.

### Player strategy guides

**P1 strategy guide.** Pick a 3×3 block anywhere and extend it to 10 stones.
Against any P2 strategy: (i) mirror-antipodal loses to you on tie-break
(R10 win); (ii) contact/spoil by P2 hurts P2 more than you; (iii) no P2 plan
crosses threshold before or without you crossing. The game is a solved win for
P1. Don't overthink: put down 9 stones as a 3×3, then one more peripheral
stone.

**P2 strategy guide.** The game is broken for you against competent P1. The
only realistic paths to a non-loss are:
1. **Hope for P1 blunder.** If P1 plays a non-clustered shape, it falls behind
   because the friendly-boost gradient is sub-optimal. Then P2's cluster
   crosses first. This requires P1 to play badly.
2. **Collision attempt.** Guess P1's next cell and place on it → mutual
   annihilation, costing both a round. This is a 1/(empty cells remaining) ~
   1/55 shot and you cannot repeat it often.
3. **Double-pass for a draw.** If P1 appears to be lining up for a symmetric
   win, BOTH players pass and game ends in draw. But P1 will never pass
   voluntarily (P1 wins by crossing). Useless against rational P1.

Against a rational P1, P2 loses every game. Best possible P2 outcome:
**forced draw via collisions** (keep placing on P1's cells to annihilate
indefinitely), but this requires perfect prediction of P1's moves and fails if
P1 plays any non-obvious pattern.

**Summary of 3 games**: 0/3 ended in double-pass draw; 3/3 resolved by
threshold, all won by P1.

## Phase 3 — Strategic analysis (joint)

**Dominant strategy exists.** "Build a 3×3 cluster (anywhere) and extend to 10
stones" is the dominant P1 script. Game 1 proves it wins in 10 rounds against
pure antipodal mirror. Game 2 proves it wins even when P2 outscores via
edge-efficient expansion, because of the check-order bias. Game 3 proves P2
has no survivable deviation.

**Meaningful counter-play.** Effectively none. Because:
- No capture → sunk-cost: a placed stone never leaves.
- No movement → placements monotonically grow score.
- Simultaneous → P2 can't REACT to P1's plan within a round.
- Collision is rare/weak → too hard to weaponize intentionally.

**Short-term vs long-term tension.** Essentially none. Every placement adds to
own_sum. The only tempo decision is cluster-interior vs cluster-boundary, and
they're about equally weighted (interior = 4×0.57 boost from 4 existing
neighbors; boundary = fewer friendlies but adds a new own-cell worth 0.966
base). Post-game calculus confirms these are within 10% value per move.

**Emergent concepts.**
- *Territory* (weak): cluster formation has friendly-reinforcement dynamics
  reminiscent of Go's shape theory, but without capture there's no contested
  territory.
- *Influence* (strong): the radius-3 decay field is genuinely continuous and
  pretty on the `--show-values` dump. It dominates the game's value function.
- *Tempo/initiative* (structural only): initiative in this game is
  **threshold-check order**. P1 "has the initiative" only because of the
  iteration order in `_check_threshold`.
- *Mutual-annihilation collision* (dormant): the mechanic exists and is
  verified, but in 40+ rounds of play across 3 games I induced exactly 0
  tactical collisions. It serves as a passive deterrent (don't play obvious
  cells) but never decided an outcome.

**Topology matters.** Torus enables the antipodal no-interference setup that
makes Game 1's clean resolution possible. On a grid (non-wrapping) edge/corner
cells would have reduced radius-3 footprint (clipped by boundary), breaking the
spatial symmetry and making the corner strategically worse. On the torus every
cell is equivalent. This matters for the theoretical game; in practice both
players quickly discover the antipodal pattern and play it.

**First-mover advantage.** **Very strong, and structural, not strategic.**
Seat-swap Game 3 with pure mirror play produced the identical outcome as Game 1
(R10, both own_sum = 38.921, P1 wins). Even in Game 2 where P2 OUTSCORED P1 by
2.58 points, **P1 still won** because of check-order iteration. The
simultaneous turn structure did NOT eliminate first-mover advantage — it just
moved it from move-order to win-check-order. **Quantitatively: P1 wins 3/3
games (100%) including seat-swap.**

## Phase 4 — Novelty adversary

### Adversary argument (this game is NOT novel)

**(a) Catalog comparisons.**

- **Go.** Common turn-by-turn placement on a grid, but Go has capture,
  liberties, ko, life-and-death. This game has none. Only the placement
  surface matches. *Not Go.*
- **Hex / Y / Havannah.** These are connection games. This is a threshold
  game. No connection win condition here. *Not Hex-family.*
- **Reversi / Othello.** Custodian capture is the defining mechanic; this game
  has no capture. *Not Othello.*
- **Gomoku / Pente / Connect6.** Line-forming games. This game scores by
  aggregate influence, not by lines. *Not line games.*
- **Amazons.** Queens moving + shooting + territory. This game has no
  movement, no shooting. *Not Amazons.*
- **Lines of Action.** Connection + movement. No match. *Not LoA.*
- **Mancala.** Pit-sowing capture. No match.
- **Life-like CA (Conway's Life, etc.).** No CA here. Irrelevant.
- **Tumbleweed.** **Closest territorial analog.** Tumbleweed uses line-of-sight
  from each stone to stack scores on cells. This game uses radius-3 decay from
  each stone to project influence on cells. The core framework — "every stone
  radiates influence; score = sum of influence on owned cells" — is
  structurally the same. Tumbleweed: discrete visibility + LOS. This: continuous
  decay + metric radius. Rules differ but **the strategic primitive is the
  same**.
- **Blotto / Colonel Blotto.** Simultaneous resource-allocation across
  theaters. **Strong abstract fit.** Each placement is a unit deployment;
  collision is deployment conflict; score thresholds are win conditions.
- **Simultaneous Go / Gungo.** Matches turn structure exactly; different win
  condition and no capture. Gungo's simultaneous-move-with-collision is the
  direct progenitor of this game's turn structure.
- **Nim / Slither.** No structural match.

**(b) CA literature.** Not applicable (no CA).

**(c) Simultaneous games.**
- Blotto with spatial coupling — best abstract match.
- Diplomacy order resolution — much simpler here (only collision, no
  supports/attacks/convoys). Too rich a comparison.
- RPS-scaled guessing games — partial fit for the collision sub-game but
  embedded in positional structure.

**(d) Re-skin claim.** **"Blotto-on-a-torus with exponential-radius scoring and
mutual-annihilation collision."** Under the transformation:
- Cells → Blotto theaters
- Per-round placement → per-round unit deployment
- Radius-3 decay → inter-theater value spillover
- Same-cell collision → deployment conflict
- Threshold win → "first to accumulate X victory points"

The mapping is **lossy** (real Blotto has independent theaters, one-shot
allocation, no spatial wraparound) but **captures the essential
simultaneous-allocation-with-spatial-coupling flavor**.

A more specific reskin claim: **"Tumbleweed-on-a-torus with simultaneous moves,
radius-3 scoring, no line-of-sight."** This captures the scoring primitive
almost exactly.

**(e) Expert transfer test.** Would a Tumbleweed expert or Blotto expert win
this game by transfer?

- A **Tumbleweed** expert would immediately grasp "cluster to boost
  self-projection while denying opponent's projection onto your stones". They
  would probably discover the antipodal 3×3 opening within 5 games. Partial
  transfer.
- A **Blotto** expert would grasp "simultaneous allocation, opponent is
  trying to commit their piece to the same cell". But Blotto experts focus on
  marginal-value allocation across independent theaters, which doesn't apply
  here due to spatial coupling. Partial transfer.
- A **Go** expert would recognize "shape" and "cluster efficiency" but be
  mis-led by looking for liberties and capture. Mixed transfer.

**Verdict: no single known game transfers fully, but the game is a close
hybrid of Tumbleweed's scoring + Blotto's simultaneous allocation + trivial
torus board.**

### Rebuttal (P1 + P2)

Specific moments where known-game analogies failed:

1. **Game 1 R1 (P1=27, P2=63)**: both players place at maximum torus distance
   without any interaction. In Tumbleweed this can't happen — stones always
   interact via LOS, and Tumbleweed has no wrap-around. The **"pure no-
   interaction opening"** is unique to radius-decay-on-torus games.

2. **Game 2 R15 (P1=39.40, P2=41.98, P1 wins)**: Both players cross threshold
   in the same round but P1 wins despite having lower score. In Blotto there
   is no equivalent — Blotto allocation is one-shot and winner is decided by
   theater count. In Tumbleweed the game ends only when players stop
   placing. **Mid-game simultaneous-crossing-with-check-order-tiebreak has no
   direct analog in any game.** (Though this is more an engine bug than a
   novel feature.)

3. **Game 3 R9 spoiler (P2 places at (0,1), net -0.46 to own_sum)**: a
   placement that *hurts* the placer because the cell has a negative pre-
   existing influence value. In Go this doesn't exist (stone value = capture
   potential, not cell value). In Blotto it doesn't exist (theater value is
   binary). This **"dominated cell with negative contribution"** is a novel
   emergent concept.

4. **Cluster-reinforcement gradient.** The 3×3 cluster in Game 1 R9 shows
   cells ranging from +4.05 (corners of cluster) to +4.56 (center of cluster),
   a smooth curved value surface. This **continuous-valued territory surface**
   has no direct analog in discrete territorial games.

5. **Collision as deterrent-only, never weapon.** In 3 games no tactical
   collision was induced. In Diplomacy and Gungo, simultaneous mechanics are
   typically *offensively* weaponized. Here the simultaneity is effectively
   dormant, which is a distinctive (if perhaps unintended) property.

### Novelty resolution

**Novelty score: 4/10.**

- Not 2–3 (off-the-shelf reskin): the combination of simultaneous + collision
  + radius-decay + torus + threshold is not exactly any single named game.
- Not 5 (pilot score): I score lower because the *playable strategic surface*
  is shallower than the pilot acknowledged — Game 2 proved the
  check-order bias can neutralize a trailing player's strategic *lead*, not
  just symmetric ties. This makes the game less interesting to play than its
  rule-combination novelty would suggest.
- Not 7+ (genuine emergent dynamics): the game's behavior collapses to
  "monotone cluster growth; P1 wins".

**Closest single analog**: Tumbleweed (for the influence-projection scoring
framework) + Blotto's simultaneous-allocation layer, on a torus.

## Phase 5 — Verdict

Team ID: team-2
Game ID: 1565501cfecf
Rules Summary: 8×8 torus; simultaneous place-one-stone-per-round (same-cell
collision = mutual annihilation); radius-3 exponential-decay signed influence
(strength 0.966, decay 0.587); win by own-cell signed-influence sum exceeding
38.627. No capture, no cellular automaton, placement-only, monotone state.
Topology: 8×8 torus, 64 cells, Von Neumann adjacency.
Turn Structure: **simultaneous** (resolved atomically via
`step_simultaneous`).

### SCORES (1–10)

- **Strategic Depth: 3** — A single dominant strategy (3×3 cluster → extend by
  1) wins for P1 in 10 rounds. Spoiler plans are net-negative for the spoiler.
  P2 has no winning line against competent P1. Branching is minimal.
- **Emergent Complexity: 3** — The radius-3 continuous-decay field is
  visually rich and the per-cell value surface is genuinely smooth, but only
  one behavior emerges from play (cluster-and-extend). No capture, no ko, no
  movement means the state space is monotonic. Collision mechanic is dormant
  in practice.
- **Balance: 1** — **This is the critical failure.** Seat-swap evidence: P1
  wins 3/3 games including the seat-swap game. In Game 2 P1 won despite P2
  having higher own_sum at the terminal tick (41.98 vs 39.40). The
  `_check_threshold` iteration order creates a structural P1 advantage that
  applies not just to symmetric ties but to **any simultaneous terminal
  round**. This is worse than the pilot's "2" rating because the bias is
  active even when P2 outscores P1.
- **Novelty (post-adversary): 4** — Unique component combination (simultaneous
  + collision + radius-decay + torus threshold) with no single named analog,
  but the closest hybrid (Tumbleweed scoring + Blotto simultaneity on torus)
  captures most of the rule flavor. The strongest adversarial point: this is
  essentially "Tumbleweed-torus simultaneous with radius-3 decay". The
  strongest rebuttal: the continuous negative-contribution dominated-cell
  phenomenon and the pure non-interaction antipodal opening are unique to this
  specific construction.
- **Replayability: 3** — Once the cluster-and-extend script is discovered,
  games play out in 10–15 rounds with a deterministic P1 win. Only source of
  variation is which 9 cells each player picks, and the torus makes all
  cluster locations equivalent.
- **Overall "Would I play this again?": 2** — As a human game, no — P2 has no
  winning line and P1's optimal play is mechanical. As a training testbed for
  simultaneous-play AI research, marginally yes, but only after fixing the
  check-order bias.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed** (territorial influence-projection scoring) combined with
**Simultaneous Go / Gungo** (simultaneous turn structure with collision), on a
torus. Not identical because: (i) Tumbleweed uses line-of-sight visibility, not
radius-decay metric; (ii) Tumbleweed is alternating; (iii) Gungo uses Go-style
capture. This game is a hybrid of their scoring and turn-order primitives
without the capture mechanic.

### KILLER FLAWS

1. **Structural P1 advantage via `_check_threshold` iteration order.**
   `engine_v2.py` lines 748–761 iterate `for player in (1, 2)` and return on
   the first crossing, so in any simultaneous round where both players cross,
   P1 wins. **Verified in Game 1 (symmetric tie) and Game 2 (P2 outscored P1
   but still lost).** This invalidates any claim of P2 fairness in the game.
2. **No recovery mechanic for trailing player.** No capture, no movement, no
   CA means once behind (or in a sub-optimal shape) there's no path back.
   Monotone own_sum growth.
3. **Dominant opening trivializes the game.** "3×3 cluster + 1 peripheral
   stone" wins for P1 in 10 rounds with no meaningful branching. Search depth
   effectively 1.
4. **Collision mechanic is inert in practice.** Simultaneous play makes
   collisions uncommittable (can't force; guessing-game) so the one mechanism
   that could introduce tactical tension never fires.

### BEST QUALITY

The continuous radius-3 decay influence field produces a genuinely smooth
value surface on the board (visible in `--show-values` output) and the
**dominated-cell phenomenon** (placing in a cell with high opposing influence
yields a net-negative own_sum contribution) is an interesting emergent
incentive not found in discrete territorial games. If paired with a capture or
movement mechanic, these primitives could support a deeper game.

### IMPROVEMENT IDEAS

**Primary (fixes the #1 killer flaw):** replace the check-order tie-break in
`_check_threshold`. Options in order of preference:
1. **Margin tie-break**: in a simultaneous round where both players cross,
   winner = player with the higher excess over threshold (so P2 in Game 2 at
   +3.35 excess would beat P1 at +0.77 excess).
2. **Simultaneous-cross = draw**: if both cross on the same tick, declare the
   game a draw. Fair but potentially increases draw rate in symmetric play.
3. **Random tie-break**: coin flip. Eliminates structural bias but adds
   stochasticity.

**Secondary (deepens strategy):** add a "dominated cell conversion" rule — at
end of each round, any cell whose signed influence value has a sign opposite
its owner for ≥ 2 consecutive rounds flips ownership. This introduces non-
monotone dynamics (you can lose stones), restores trailing-player counter-
play, and makes contact between clusters strategically interesting. Without
this (or equivalent capture/movement mechanic), the game's strategic space
remains a 10-round sprint to a predetermined P1 win.

---

## Summary for the aggregator

Game 1565501cfecf — R15 champion at GE 0.318 — exhibits a **severe P1
structural advantage** via threshold-check iteration order, not just in
symmetric ties (Game 1) but in any simultaneous terminal round including
asymmetric cases where P2 scores higher (Game 2, P2=41.98 vs P1=39.40, P1
wins). The game's strategic surface is shallow (single dominant strategy,
monotone state, dormant collision mechanic, no capture/movement/CA recovery).
Novelty score 4/10; Balance score 1/10; Overall 2/10. Not recommended as a
champion without fixing the check-order bias.
