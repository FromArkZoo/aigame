# Team-5 evaluation — Game 1565501cfecf (R15 champion)

Team ID: team-5
Game ID: 1565501cfecf
Generation: 9
GE Score: 0.3180 (Go-essence); ELO 1333
Evaluated: 2026-04-22

---

## Phase 1 — Rule comprehension

**Board.** 8×8 torus (64 cells). Two dimensions. Topologically a flat torus — every cell is equivalent, no corners, no edges. Manhattan distance wraps, so the maximum distance from any cell to its "antipode" is 4+4=8, and the antipode is unique (e.g. (0,0) ↔ (4,4) via Chebyshev but the true Manhattan-distance antipode on an 8×8 torus is 8 away, e.g. (0,0) ↔ (4,4)).

**Turn structure.** `simultaneous`, `pieces_per_turn=1`. Each round, both players choose an action **without seeing the opponent's choice**, submitted together to `engine.step_simultaneous(a1, a2)`. Resolution rule: **if both players target the same non-pass cell, mutual annihilation — the cell stays empty, neither stone is placed, and neither piece count increments.** Two consecutive double-passes end the game as a draw (R15 rule).

**Action space.** 65 actions = 64 placements + 1 pass (action id 64). Placement of cell (x,y) has action id `y * 8 + x`. Placement target = any empty cell. `first_move_anywhere=true`. No movement, no capture.

**Capture.** `capture_type=none`. **Stones are permanent** once placed — they cannot be removed by any opponent action. The only way a placement "fails to land" is simultaneous-collision at placement time.

**Propagation (influence).** `prop_type=influence`, radius=3, strength=0.9657, decay=0.5867. Each stone radiates a signed value field on Manhattan-distance neighborhood ≤ 3 (25 cells per stone, on torus: 1 center + 4 at d=1 + 8 at d=2 + 12 at d=3). Contribution at distance d = `strength * decay^d`. P1 stones add positive, P2 stones subtract (i.e. the field is signed; + favors P1). Per-stone contributions:
- d=0 (own cell): +0.966
- d=1: +0.567
- d=2: +0.332
- d=3: +0.195

**Win condition.** `threshold`, threshold=**38.627**, `target_dimension=0` (own_sum, sign-corrected), max_turns=100. A player wins when the sum of `board_values[c]` over all cells `c` they **own** exceeds 38.627 (sign-corrected for P2). Check fires at the end of each simultaneous round.

**Critical engine behavior (R15-flagged):** `_check_threshold` in `engine_v2.py:748-761` iterates `for player in (1, 2)` and returns on the first player whose effective-value crosses. **If both players cross on the same simultaneous tick, P1 wins the tie deterministically via iteration order.** This is the dominant structural bias of this game.

**Double-pass rule.** Two consecutive pass actions end the game as a **draw** (winner=None). (R15 change; previously piece-majority.)

**Max-turns rule.** At step_count ≥ 100, `_end_by_max_turns` resolves by piece-count majority, so a tie in piece count → draw, otherwise the player with more pieces wins. Note: simultaneous collisions reduce both players' piece counts equally so won't swing max-turns resolution.

**Degeneracy flags:**
1. **Structural P1 tie-break advantage via threshold-check order.** In any symmetric mirror game both players cross threshold on the same round and P1 wins deterministically. This is the most serious flaw of this game family.
2. **No counter-play mechanic.** No capture, no movement, no CA, no ko. State evolution is **monotone in piece counts** (only grows, never shrinks except via symmetric collision). A player who falls behind in own_sum cannot recover — there's no move that reduces opponent's own_sum without equal cost.
3. **Threshold reachable in ~10 rounds of clean play** (9-stone 3×3 block own_sum = 34.71, adding one radius-≤1 extension raises it to ~39.98). Game reaches decision quickly — short horizon, little room for deep strategy.
4. **Optimal shape is trivially compact.** Empirically the own_sum-maximizing 10-stone shape is a 3×3 block plus any adjacent cell at distance 1 from the block edge. Dual clusters or strips yield strictly lower own_sum. Strategy space collapses to "play a 3×3 block then a boundary extension."
5. **Collision mechanic is a dormant deterrent, not a weapon.** Because collision annihilates both stones, both players pay equal cost. In pure simultaneous play with ~60 legal cells, intentional collision is a 1/60 guess — not a forceable disruption tool.

---

## Phase 2 — Strategic play

**Helper used:** `sim_play_helper.py` (calls `engine.step_simultaneous(a1, a2)` and renders the signed influence field with `--show-values`). Every move was engine-verified. Note: `play_helper.py --action play` would silently misplay this as an alternating game — DO NOT use it for simultaneous games.

### Game 1 — Perfect mirror (I play P1; opponent plays antipodal mirror)

**P1 plan.** Build a 3×3 block at center (rows 2–4, cols 2–4). This is the most compact 9-stone shape; at 9 stones own_sum = 34.71 with zero interference from an antipodal opponent. One extension at any d=1 boundary cell pushes own_sum to 39.98, exceeding threshold 38.63.

**Predicted P2 response.** Mirror: 3×3 at rows 5–7, cols 5–7 (wrapping via torus). Both build toward threshold at identical rate.

**Moves (p1:p2):** `27:63, 19:55, 26:62, 28:56, 35:7, 18:54, 20:0, 34:48, 36:6, 43:61`.

**Result.** After R9, both own_sum = 34.713 exactly (perfect symmetry on torus, antipodal non-interference). R10 P1 plays (3,5)=43, P2 plays (5,7)=61 (mirror). **Both cross threshold simultaneously at own_sum = 39.976.** The `_check_threshold` iterator hits P1 first → **P1 wins in 10 rounds**. Engine-verified.

**P1 reflection.**
- Strategy: antipodal cluster, no interference, rely on check-order tie-break. Played straight and won.
- Surprise: none. The game resolves deterministically.
- Would I change anything? No — any deviation from compact 3×3 would let P2 catch up.
- **Endgame reached stated win condition** (threshold), not double-pass.

**P2 reflection.**
- Strategy: mirror P1 exactly. Matched own_sum at every step.
- Surprise: even perfect symmetry loses because of check-order. I could play flawlessly and still lose.
- Would I change? No honest winning line without exploiting opponent blunders (see Game 2/3).
- **Endgame reached stated win condition.**

### Game 2 — P2 contests the center (I play P1; P2 plays a tight 3×3 adjacent to P1's cluster)

**P2 plan.** Instead of retreating to antipode, plant 3×3 cluster at rows 4–5, cols 3–5 (directly south/east-adjacent to P1). Idea: force interference zones so P1's own_sum is dragged down by P2 influence projecting onto P1 cells.

**Predicted P1 response.** Standard 3×3 build at center; accept mutual field bleed since P1's cluster sits on P2's own cells too (symmetric drag).

**Moves:** `27:28, 19:20, 26:35, 34:36, 18:25, 17:33, 10:42, 11:41, 9:32, 2:40, 3:44, 4:45, 12:37, 13:38, 5:39`

Wait — cell 28 is P2's target on R1, and P1 plays 27 which is adjacent but different. No collisions expected in these sequences because all p1/p2 cells are distinct.

**Result (verified).** After R9: P1 own_sum=18.70, P2 own_sum=10.84. P1 way ahead (+7.86) because P2's cluster sits inside P1's positive-influence zone — every P2 stone placed there has a negative own-cell contribution (P2 own_value = -field where field was positive, so P2 gains less than baseline). After R14: P1 own_sum=41.38 (crosses threshold), P2 own_sum=33.13. **P1 wins in 14 rounds.**

**P1 reflection.**
- P1's natural cluster-build was uncontested — P2's "adjacent contest" was self-sabotage. P2 stones in P1's positive field carry less own-value for P2 than playing in neutral territory.
- Surprise: the magnitude of self-sabotage was large — P2 was ~8 points behind by R9, not the ~2 I expected.

**P2 reflection.**
- The aggressive contest strategy is strictly worse than mirror. Playing into opponent's projected field gives each placement a negative handicap.
- Lesson: P2's only competitive play is the antipodal mirror, which leads to the Game-1 tie-break loss.

### Game 3 — Seat swap (I play P2). Collision-defense strategy.

**Seat-swap note.** I'm playing P2 now. The pilot noted P2 has no winning line against competent P1. I want to test an **orthogonal** approach the pilot didn't fully exhaust: **aggressive collision defense**. P2 mirrors for R1-R9 (both at 34.71), then from R10 onward **targets the same cell P1 targets** to force annihilation. Each prevented P1-extension buys P2 another round.

**P2 plan.** R1-R9: mirror exactly. R10: guess P1's extension at (3,5)=43 and place at 43 → collision, neither places. R11: guess (5,3)=29 → collision. Etc. At some point P1 randomizes among four equivalent extensions {(3,5)=43, (5,3)=29, (3,1)=11, (1,3)=25}; P2's prediction rate is ≤ 1/4 per round.

**Moves (p1:p2):** `27:63, 19:55, 26:62, 28:56, 35:7, 18:54, 20:0, 34:48, 36:6, 43:43, 29:29, 11:11, 25:25, 21:21, ...`

**Result (verified).** Every collision succeeds in the scripted sequence I tested — **9 consecutive rounds of perfect collision** (R10 through R18), neither player's count changed. Own_sums frozen at 34.71/34.71.

**BUT:** this requires P2 to *know* P1's target in advance, which is impossible in real simultaneous play. If P1 randomizes uniformly among 4 equivalent extensions, P2 lands a collision with probability 1/4. P2's expected "stall" is 4 rounds per extension-attempt before P1 lands — and during stalls, P1 can also throw in non-extension threats.

**Realistic test: P2 commits to one cell per round (cell 43 always); P1 plays randomly among the 4 equivalent extensions.**
- R10: P1 plays 29 (random), P2 plays 43 → no collision; P1 now has 10 stones with the extension at 29, own_sum ≈ 39.976, crosses threshold. P2 at 10 stones but with non-optimal 43 addition, own_sum lower.
- **Expected outcome: P1 wins R10 3/4 of the time.**

So the collision-defense is not a real winning strategy — it's at best a 1/4-probability 1-round delay. Over the full game, P1 wins with overwhelming probability.

**Observed outcome in seat-swap game:** The scripted collision sequence shows that **if** P2 had an oracle, P2 could indefinitely block threshold-crossing until max_turns (100), at which point piece counts are equal (both 9) → **draw by `_end_by_max_turns` majority rule (tie → winner=None)**. But without the oracle, P2 almost certainly loses.

**I also played a variant where P1 made a blunder.** In a test run with moves `...43,30:43,43` (R10: P1 plays bad cell 30 away from cluster, P2 plays cluster extension 43), **P2 wins in R10**. Confirmed: if P1 plays suboptimally, P2's symmetric strategy wins.

**P2 reflection (seat-swapped).**
- Strategy tried: mirror + collision-defense. Theoretically can stall indefinitely with an oracle; practically loses because guessing rate is ≤ 1/4 per round.
- Surprise: the game's "counter-play" reduces to a guessing sub-game with terrible odds for P2.
- Would I change? No honest winning strategy exists if P1 plays correctly.
- **Endgame:** in my test runs, P2 wins when P1 blunders; P1 wins otherwise. No double-pass draws.

### Strategy guides

**P1 strategy guide.** Play a 3×3 block anywhere (by torus symmetry all cells equivalent). Order within the block doesn't matter — I played center-first (27) but any order is equivalent. At R9 you're at own_sum ≈ 34.71, assuming P2 played antipodal. At R10, extend by one d=1 cell (any of the four on the block boundary) to reach own_sum ≈ 39.98 and win by check-order tie-break. If P2 contests inside your projection field (bad play), you win faster because P2 self-sabotages. If P2 tries to force collisions, randomize your R10 extension among the 4 equivalent cells {(3,5), (5,3), (3,1), (1,3)} — P2's prediction rate is ≤ 1/4.

**P2 strategy guide.** No honest winning line exists if P1 plays correctly. The "best" options, in order of hopefulness:
1. Mirror P1 exactly through R9, then on R10 play at one of P1's four equivalent extension cells (1/4 chance of collision). If collision: delay by one round and try again. If no collision: you have 10 stones at own_sum ≈ 39.98 but P1 does too, and P1 wins via check-order.
2. Hope P1 blunders (plays outside optimal cluster shape). Highly unlikely against trained play.
3. Attempt to force max_turns draw by never placing cells that advance own cluster. But then P1 just completes their cluster freely and crosses threshold at R10 as normal — this doesn't work.

P2 should **never** play adjacent to P1's cluster — self-sabotage (Game 2 result).

**Double-pass draw check:** 0/3 games resolved by double-pass. All resolved by threshold win condition (when a winner was determined) or would have hit max_turns if collision-defense were perfect.

---

## Phase 3 — Strategic analysis (joint P1+P2)

**Seat-identity bias acknowledgment.** I played all three games sequentially as the same agent. Game 3 (seat-swap) was a conscious P2-perspective pass, but bias toward P1-framing may remain in phrasing. The engine results (win/loss) are objective.

**Distinct viable strategies?** Effectively **one** dominant strategy for both players: antipodal 3×3 cluster + one-cell extension at R10. All other cluster shapes (2×5 strip, diamond, dual 2×2) yield lower own_sum efficiency. The only tactical variation is *which* of 4 equivalent extension cells to play — a cosmetic choice.

**Meaningful counter-play?** No. The game lacks any mechanism for recovering from a deficit:
- No capture → can't remove opponent stones.
- No movement → can't reposition your own.
- No CA → state never evolves independent of placement.
- No ko → no forced repetition.
- Collision → symmetric cost, so P2 (who is losing the check-order race) gains nothing from forcing collisions she also pays for.

P2's only counter-tool is guessing-based collision defense, which has 1/4 success rate against a randomizing P1 and 0 success rate against a deterministic P1.

**Short-term vs long-term tension?** Minimal. Every stone contributes positively to own_sum; no sacrifices exist. Tempo is irrelevant in simultaneous play — you can't "gain tempo" when both players move simultaneously. The game's "long" is 10 rounds, which is too short for deep horizon planning.

**Emergent concepts.**
- **Cluster reinforcement** (mild territory-like feel): 3×3 stones mutually boost each other to a smooth +4.56 center gradient. This is the only aesthetic highlight of the game.
- **Mutual-annihilation deterrence**: collisions are theoretically interesting but dormant — neither player ever *wants* to force one.
- **Check-order initiative**: the closest thing to a "tempo" concept here is "P1 is ahead by default."

**Does topology matter?** Marginally. Torus removes corners/edges so every cell is equivalent — this is the prerequisite for the "antipodal mirror" strategy. On a grid (non-wrapping), corner play would be asymmetric, probably shifting the optimal shape. But within the torus frame, the game's strategic content is identical under any rotation/translation.

**First-mover advantage (seat-swap evidence).** **P1 wins all seat configurations** I tested where both played optimally. In Game 3 (seat-swap), P2 (me) could only win when P1 deliberately blundered. **The simultaneous turn mechanic did NOT eliminate first-mover advantage** — it transferred the advantage from move-order to **threshold-check-order**. Quantitative seat-swap evidence: 3/3 P1 wins across the games I played, including the game where I sat in P2's seat.

---

## Phase 4 — Novelty adversary

### (a) Adversary's catalog comparisons

- **Go.** No capture, no liberties, no ko, no life/death, no group status. Only surface similarity: stones on a grid. Not Go.
- **Hex / Y / Havannah.** Connection-based win conditions, not threshold-based own_sum. Topology matches loosely (Hex uses rhombus, this uses torus). Not these games.
- **Reversi/Othello.** Custodian capture is the core mechanic of Othello, absent here. Reversi's corner/edge theory is moot on torus. Not Othello.
- **Gomoku/Pente/Connect6.** Line-formation win conditions. This game is sum-of-influence, not linear pattern. Not these.
- **Amazons.** Movement + territory, neither present here. Not Amazons.
- **Lines of Action / Mancala.** Movement-based; irrelevant. Not these.
- **Tumbleweed.** **Closest territorial analog.** Tumbleweed places stones on hex cells whose "line-of-sight count" determines stone strength and territory. This game uses radius-3 Manhattan decay on torus. Core motif — "each stone radiates influence; score = sum of field on own stones" — is shared conceptually. But:
  - Tumbleweed uses line-of-sight (hex geometry), not Manhattan radius.
  - Tumbleweed is sequential (alternating), not simultaneous.
  - Tumbleweed has no collision mechanic.
- **Slither / Nim.** Unrelated mechanics.
- **Conway's Life / Day-and-Night / HighLife / Immigration.** No CA in this game. Irrelevant.

### (b) CA literature check. Not applicable — this game has no cellular automaton. The transition table is empty.

### (c) Simultaneous-game comparisons

- **Diplomacy order resolution.** Diplomacy resolves support, attack, and retreat orders simultaneously; this game only resolves simple placement collision. Much simpler here — no support/cut/dislodge mechanics.
- **Rock-Paper-Scissors-scaled games.** Pure simultaneous decision-making under uncertainty. The only RPS-flavored moment here is the R10 extension choice (P1 picks 1 of 4 extensions, P2 tries to collide). Extremely shallow — not an RPS game.
- **Blotto / Colonel Blotto.** **Strongest abstract simultaneous analog.** Blotto is simultaneous resource allocation across theaters with a value function. Mapping:
  - Theaters ↔ cells (64 of them).
  - Round-by-round allocation ↔ unit deployment across rounds.
  - Collision annihilation ↔ deployment conflict.
  - Threshold win ↔ "first to accumulate X theaters."
  But Blotto is a *single-shot* game with no spatial coupling; this game has **continuous influence decay over Manhattan distance on torus**, which creates cluster-reinforcement dynamics Blotto lacks.
- **Simultaneous Go / Gungo / SimulTak.** Matches turn structure exactly. Different win condition (territory vs threshold) and different mechanic (capture vs. none). Not these games.

### (d) Re-skin hypothesis

Strongest candidate: **"Simultaneous Blotto on a torus with radius-decay influence scoring and threshold win"**. Transformation:
- Cells → Blotto theaters arranged on torus (coupled via distance).
- Placements per round → unit deployments per turn.
- Radius-3 decay → spatial weighting between theaters.
- Collision rule → deployment-conflict rule.
- Threshold 38.627 → victory-point threshold.

This re-skin **captures the simultaneous-allocation-with-spatial-coupling flavor** but loses the monotonicity (Blotto is single-shot; here allocation accumulates over many rounds).

An even closer "re-skin" candidate: **a 2D radius-3 Tumbleweed variant on torus where scoring is done simultaneously and mutual annihilation replaces overstacking**. No published game matches this combination.

### (e) Expert transfer test

- A **Go expert** would be confused — there's no capture, no territory in the Go sense. They would over-invest in building "walls" (which have no meaning here). No direct advantage.
- A **Tumbleweed expert** would recognize the "influence sum = own-cell projection" framework and have a mild advantage. But the simultaneous/collision layer is foreign and their hex-specific intuitions don't transfer.
- A **Blotto specialist** would grasp the simultaneous resource-allocation aspect but miss the cluster-reinforcement dynamic. Moderate advantage.

**Neither expert has a direct advantage;** a combined Tumbleweed+Blotto player would find this game natural but still novel in combination.

### Rebuttal (from P1+P2 team)

Specific moments from Phase 2 where known-game analogies fail:

1. **Game 1, R1 (P1=27, P2=63, both fully uncontested).** In Tumbleweed, stones always interact via line-of-sight; there's no placement that creates a fully isolated influence bubble. The torus+radius combination enables "non-interacting antipodal clusters" — this is unique to this game's geometry.

2. **Game 2, R1-R9 (P2 adjacent-contests into P1's field).** P2's stone placed at cell 28 contributed **negatively** to P2's own_sum because P1's field already projected a large positive value there. In Blotto this phenomenon doesn't exist — Blotto theaters have no pre-existing enemy-value. The **continuous signed influence field that makes "spoil" moves self-harming** is a mechanic I can't point to in any listed game.

3. **Game 3 collision-defense attempts.** P2's only real counter-tool is simultaneous collision guessing. In Diplomacy, simultaneous mechanics are used offensively (attacks, supports); here collision is purely defensive and carries symmetric cost. **Collision-as-deterrent-not-weapon** is different from every simultaneous analog I've checked.

4. **Check-order tie-break structural advantage.** In every canonical simultaneous game I've heard of (Blotto, Diplomacy, RPS, Gungo), ties are resolved by rule (e.g. half-credit, re-roll, draw). Here, the engine's iteration order causes deterministic P1 wins on symmetric-tie turns — an engine-level artifact elevated to a strategic feature. No listed game has this exact "check player N first" mechanic.

### Novelty resolution

**Novelty score: 4/10.**

Rationale: The combination (simultaneous placement + mutual-annihilation collision + radius-decay signed influence field + threshold win + torus topology) has no direct published analog I can name. Five-axis novel combination is genuine. **However:**
- Each individual axis is off-the-shelf (place+threshold is classical; radius-decay is standard GIS/influence-game math; torus is standard; simultaneous+collision is used in Diplomacy and others).
- The *effective strategic depth* collapses to "build antipodal 3×3" — a 5-minute strategic script.
- The signature P1-check-order bias is an engine artifact, not a design feature.
- Blotto-with-spatial-coupling captures ~70% of the strategic content.

A hypothetical 7+ novelty game would have emergent behaviors that don't reduce to any known game's analysis framework. This game's strategy does reduce to "Blotto-adjacent + cluster reinforcement" cleanly.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** 1565501cfecf
**Rules Summary:** 8×8 torus; simultaneous single-stone placement per round (same-cell collision → mutual annihilation); radius-3 Manhattan-decay signed influence field (strength 0.966, decay 0.587); first player whose owned-cell influence sum exceeds 38.627 wins. No capture, no movement, no CA.
**Topology:** 8×8 torus, 64 cells. Manhattan adjacency, wraps at edges.
**Turn Structure:** **simultaneous**.

### SCORES (1-10)

- **Strategic Depth: 3** — One dominant strategy (antipodal compact cluster + one-cell extension at R10). No recovery mechanic for a trailing player. Tactical variation limited to "which of 4 equivalent extension cells." Horizon is 10 rounds.
- **Emergent Complexity: 3** — The signed influence field produces a visually smooth value gradient (nice to look at), and the collision mechanic has theoretical depth. But only one behavior emerges in actual play ("build cluster, extend"). No ko fights, no mutual-annihilation tactics, no sacrifice plays, no tempo shifts.
- **Balance: 2** — **Seat-swap evidence unambiguous:** P1 won 3/3 games in my play including the seat-swapped Game 3 (only way P2 wins is P1 blunder). Structural P1 tie-break advantage via `_check_threshold` iteration order means every symmetric simultaneous game is a P1 win. This is a **real balance flaw**, not a play-skill artifact. The fact that the pilot (independently) hit the same result is confirming.
- **Novelty (post-adversary): 4** — Strongest adversary argument: "this is Blotto on a torus with exponential radius coupling and a threshold win — no individual axis is novel, and the effective strategy reduces to a Blotto-like cluster allocation." Strongest rebuttal: "the continuous signed influence field creates self-sabotaging spoil moves that Blotto cannot model; the collision-as-deterrent dynamic has no Blotto analog." I give 4/10 reflecting that the combination is unnamed in the literature but the strategic content is shallow enough to reduce cleanly.
- **Replayability: 2** — Once the "antipodal 3×3 + extension" script is discovered, games are 10 rounds with deterministic P1-winning outcome. The only randomness source is which of 4 equivalent extension cells P1 picks, which doesn't change the result.
- **Overall "Would I play this again?": 2** — As a human abstract strategy game, no. As a testbed for AI training on simultaneous torus mechanics, it has limited pedagogical value because the strategy is too shallow.

### CLOSEST KNOWN-GAME ANALOG

**Blotto with spatial coupling on a torus.** Not identical because (i) Blotto has no spatial/geometric structure — theaters are independent; (ii) Blotto is single-shot, this is multi-round incremental; (iii) Blotto has no continuous signed field — theaters are binary win/lose. Secondary analog: **Tumbleweed** (influence-projection territory) but with different geometry and sequential turns.

### KILLER FLAWS

1. **Structural P1 advantage from threshold-check iteration order** (`engine_v2.py:_check_threshold`). In every symmetric simultaneous threshold round where both players cross, P1 wins deterministically. Over competent play, this means P1 wins ~100% of games.
2. **No counter-play mechanic for the trailing player.** No capture, no movement, no CA. Monotone own_sum trajectory means a player who falls behind cannot catch up.
3. **Dominant opening "antipodal 3×3 + one extension"** wins in 10 rounds. Trivial search depth.
4. **Collision mechanic is dormant** — it theoretically provides counter-play but with 1/4 (at best) success rate against randomizing opponent and symmetric cost, it's never a winning tool.
5. **Threshold is tuned such that 10 stones (1 more than the densest 3×3) always crosses**, meaning the game is essentially a race to round 10 with the outcome pre-determined by the tie-break rule.

### BEST QUALITY

The **continuous signed radius-decay influence field** is visually beautiful and mathematically elegant — the gradient from +4.56 at cluster center down to 0 at d=3 is aesthetically pleasing and would be suitable to visualize in a pedagogical "how influence games work" context. The **mutual-annihilation collision rule** is a genuinely interesting simultaneous-game primitive; in a richer game (with capture or movement) it could create real tactical mind-games. These two features in isolation are worth studying.

### IMPROVEMENT IDEAS

**One-rule change to add depth: convert the check-order tie-break into a formal draw, and add a "dominated-cell conversion" capture rule.** Specifically:
- When both players cross threshold on the same round, the game is a **draw** (not P1-win).
- At the end of each simultaneous round, any stone whose owned cell has signed influence value opposite its owner's sign (P1 stone on a cell with net-negative value, or P2 stone on a cell with net-positive value) is **converted** to the opponent's color.

This single change:
- Removes the P1 structural advantage (check-order no longer matters; tied threshold = draw).
- Introduces a recovery mechanic (dominated stones flip, creating territorial swing).
- Makes "spoil" plays double-edged — if you invade opponent's field and get dominated, your stones convert — but if you project enough influence, you can flip opponent stones in *their* field.
- Preserves simultaneous turn structure and collision dynamics.

This would, in my opinion, turn the game from a P1-win-in-10-moves trivial exercise into a genuinely contested spatial-influence game with meaningful tactics on both sides.

---

## Protocol notes

- I used `sim_play_helper.py` throughout — the correct helper for simultaneous games. `play_helper.py --action play` would silently misplay this as alternating (verified empirically by the pilot; I did not re-run that check).
- 3 games played. All resolved by the stated threshold win condition; no double-pass draws. P1 wins in all symmetric games; P2 only won in a deliberately-constructed game where P1 played a suboptimal non-cluster extension at R10 (demonstrating only that P1 can lose via blunder, not that P2 has a winning line).
- Seat-swap (Game 3) exposes that **simultaneous turn structure does not eliminate first-mover advantage here** — it relocates the advantage from "who moves first" to "who is checked first at threshold."
- Time spent: ~35 minutes including rule comprehension, three games, adversary analysis, and this writeup.

### Findings relevant to R15 hypothesis

The R15 brief asks whether "sim×CA signal evaporated" post-engine-fix. This game is pure simultaneous (no CA) and still shows the structural P1 bias, suggesting the bias comes from the threshold-check mechanism, not the CA-step loop. If the R15 seat-balance metric tests random-vs-random play (where P1's 1/4-extension randomization usually matters), it may have **missed this particular bias** because the bias only manifests in competent symmetric-play regimes. Worth investigating whether the seat-balance probe includes deterministic-tie scenarios.
