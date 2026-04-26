# Team-5 Evaluation — Game `8d12c8b92b71` (R16 GE Champion)

Team ID: `team-5`
Game ID: `8d12c8b92b71`
Generation: 7 (root/seed game; ELO 1263.3; GE strategic-depth metric 0.69, non-triviality 1.00)

---

## Phase 1 — Rule Comprehension

**Board.** 2D hex topology, 8×8 (64 cells). Verified against `topology.py`: real 6-neighbor hex (not the von-Neumann label `play_helper rules` prints). Offset coordinates with parity-dependent neighbor sets.

**Turn structure.** **ALTERNATING.** Confirmed via `turn_structure.turn_type = "alternating"` and the rule output. One placement per turn. (No simultaneous collision logic to worry about.)

**Action types.** `place` only. 65 actions: 0–63 are placements at `y*8 + x`, action 64 is pass. Legal target = empty cells.

**Capture.** None (`capture_type: "none"`). Once placed, stones never leave the board.

**Cellular Automaton.** None (classic engine path). No CA tables to evaluate.

**Propagation — influence.**
- Radius 2, strength **0.9843**, decay **0.6946**.
- A placement adds `sign * strength * decay^dist` to every cell within hex distance 2, where sign = +1 for P1, –1 for P2.
- Per-stone deposits: self = +0.984, dist-1 (6 neighbors) = ±0.684, dist-2 (12 cells in interior) = ±0.475. Maximum field contribution from one interior stone ≈ ±10.78 distributed.
- Values clamped to [-100, 100].

**Win condition — threshold.**
- Player wins when **sum of `board_values` over their own cells** crosses 34.129 (effective absolute value). P1 reads the raw positive sum; P2 negates the sum.
- R16 margin-rule: same-tick crossing → higher effective margin wins; tie → draw.
- `max_turns = 100`; on overflow, majority-piece-count wins.

**Degeneracy check.**
- Threshold reachable: yes — from clean simulation, a tight central cluster crosses ~34 by move 8–9 of own pieces (round 8 of alternating play).
- No dominant single-cell forced-win pattern (radius-2 plus 8×8 board means ~20 stones per side in worst case).
- No CA dead-rules issue.
- No "pass into draw" trap, but pass is available; double-pass ends game (`_end_by_double_pass`). No reason to pass with empty cells available unless intentionally drawing.
- One real distortion: edge/corner placements are weaker — corner has 2 neighbors and only ~5 cells within radius 2, vs interior's 19 cells. This skews opening choice and creates a clear "center is strong" prior.

No degenerate flags raised; rules are coherent.

---

## Phase 2 — Strategic Play

All moves engine-verified via `engine.step()` from `factory.create_engine(game)` and cross-checked with `play_helper.py`. Effective values pulled from `engine.board_values`.

### Game 1 — P1 (me) center cluster vs P2 corner cluster

P1 plan: tight cluster around (3,3). Reasoning: center maximizes radius-2 reach (all 19 in-radius cells exist on the board), and a tight pack means each stone's own-cell receives positive contributions from every neighbor stone too.

P2 plan: tight cluster around (0,7). Reasoning: stay far from P1 to avoid mutual sign-cancellation; mirror cluster structure.

| Round | P1 move | P2 move | P1 eff | P2 eff |
|-------|---------|---------|--------|--------|
| 1 | (3,3) | (0,7) | 0.98 | 0.98 |
| 2 | (4,3) | (1,7) | 3.34 | 3.34 |
| 3 | (3,4) | (0,6) | 6.64 | 6.64 |
| 4 | (2,3) | (1,6) | 11.31 | 11.72 |
| 5 | (4,2) | (2,7) | 16.93 | 15.98 |
| 6 | (3,2) | (2,6) | 23.91 | 22.49 |
| 7 | (2,4) | (0,5) | 28.10 | 27.63 |
| 8 | **(4,4)** | — | **36.52** | 27.63 |

**P1 wins on move 8 (step_count=15)**. Center crossed first because corner stones leak influence onto off-board cells (lost to clamping at the edges). Predicted P2 response — a (1,5) tightener — wouldn't have helped: P1 gets the tempo win because P1's cluster yields more own-cell receivers per stone.

P1 reflection: center is structurally better than corner; first-mover tempo plus the center bias was decisive. Would I do anything different? Only if I expected P2 to also play center — then I would race to the highest-connectivity orbit first.

P2 reflection: corner choice surrendered ~1.5 effective per round vs a mid-edge cluster. Should have either matched center (forced into Game 2) or picked an even-row mid-board position. Endgame reached via threshold, no double-pass.

### Game 2 — P1 center vs P2 adjacent contest

P1 plan: same center cluster.
P2 plan: place stones **adjacent to P1 stones** to negate P1 own-cell influence (each adjacent P2 stone reduces a P1 cell by 0.684).

| Round | P1 eff | P2 eff |
|-------|--------|--------|
| 5 | 4.50 | -0.13 |
| 10 | 13.17 | -2.10 |
| 15 | 20.88 | -2.29 |
| 20 | 27.70 | -6.52 |

After 20 rounds (40 stones placed) **neither side hit threshold** — P2's cells received heavy positive contribution from surrounding P1 stones, which made P2's own-cell sum **negative**, sending P2's effective score negative. P1 was around 27.7, climbing too slowly because P1's cells were also being eroded by adjacent P2 stones.

Engine state at step 40 confirmed `winner=None`. The game would have continued to max_turns and resolved by piece-count majority (tied at 20–20 → draw).

P1 reflection: the adjacent-contest line is a poor strategy for P2 but it does drag the game out. To break it, P1 should plant **two separate cluster seeds** so that P2 cannot smother both simultaneously. Surprised by how effectively P2 prevented threshold even though P2 can never win that way.

P2 reflection (adversarial, this seat): contest fails — but it weaponizes a draw, which is roughly +0.5 EV vs a loss. If draws don't count for me in the tournament, this is bad. If they do, it's a real defensive tool.

### Game 3 — Seat swap. P1 (was P2 strategy) center vs P2 (was P1) mid-edge

Both played "tight cluster" but P1 took center (3,3), P2 took mid-edge (0,4).

| R | P1 eff | P2 eff |
|---|--------|--------|
| 1 | 0.98 | 0.98 |
| 5 | 13.87 | 14.28 |
| 7 | 21.57 | 21.15 |
| 8 | 29.03 | 26.71 |
| 9 | **36.07** | 26.24 |

**P1 wins on move 9 (step_count=17)**. Same dynamic as Game 1: P1's center reach plus tempo lead. The mid-edge cluster is better than corner (more in-radius cells than corner) but still trails center.

### Greedy-vs-greedy probe (deterministic, 5 reruns identical)

I ran a greedy agent (maximize `own_eff - opp_eff` lookahead-1) on both sides:

```
Trial 1-5: winner=P2, P1 eff=33.37, P2 eff=36.64 (final tick)
```

**P2 wins greedy 5/5.** Trace shows P1 opens at (0,0) — the literal corner, scored highest by 1-ply greedy because no neighbor exists yet for the score function to discount. P2 then takes (1,0), (2,0), (3,0)… building a perfect line along the top edge. By round 10, P2 has overtaken P1's effective. On turn 20 both cross 34.13 simultaneously; R16's margin tiebreaker awards P2 (margin 2.51 vs 0.76).

This is a clean **R16 fix demo**: under R15's first-checked-wins rule, P1 would have won that exact same position. Now P2 correctly takes it.

### Random-vs-random sanity (50 trials)

P1 16 / P2 12 / draws 22. Roughly balanced under random play, with a high draw rate consistent with the contest-stall dynamic from Game 2.

### Strategy guide — Player 1
1. Play (3,3) or (4,4) first; do **not** play a corner.
2. Build the closest hex cluster you can — six neighbors all in-board.
3. If P2 contests adjacently, plant a second cluster seed on the opposite quadrant before move 4 to avoid the smother-draw.
4. Track effective scores; pivot when your `own_eff` stops growing per move (stop adding to a saturated region; open a new one).

### Strategy guide — Player 2
1. **Mirror P1's first move**, but offset by one ring so your cluster is in a different region of the board with full radius-2 reach.
2. Resist the urge to "block" P1 directly. Each adjacent P2 stone bleeds your own effective via positive influence on your own cell.
3. If P1 picks the corner (rare under good play), take the center yourself; you will out-race them.
4. If you fall behind on tempo, pivot to the contest line — you can usually force a draw via mutual saturation.

---

## Phase 3 — Strategic Analysis (joint)

(Acknowledged seat-identity bias: same agent played both sides; reflections were finalized in writing before swapping.)

**Distinct viable strategies?** Yes, three:
1. **Cluster builder** (greedy own-eff growth) — wins if uncontested.
2. **Contestant** (place adjacent to enemy) — cannot win, but forces draws via mutual saturation. Real defensive tool.
3. **Greedy 1-ply maximizer** — surprisingly different from cluster: pulls toward edges/lines because empty edge cells yield more "marginal" eff than rejoining a saturated cluster. Beats naïve cluster (per R16 greedy probe).

**Counter-play.** Cluster vs cluster reduces to "who reaches threshold first," which is a tempo race. Contestant disrupts that. Greedy's edge-hugging is itself counterable by mid-board cluster if the cluster player has enough tempo.

**Short-term vs long-term tension.** Mild. Strength=0.984 with decay=0.69 means current move has ~70% the impact of last move's overflow. Saturation arrives ~move 10; after that, marginal returns shrink and positional choice dominates. Not deep — closer to "race to fill the most efficient region first."

**Emergent concepts.**
- **Influence territory**: yes — the field is exactly territory in the influence sense, similar to Go's framework but quantitative.
- **Tempo / initiative**: yes, very strongly. P1 has a one-move lead which translates directly to one extra round of accumulated own-eff.
- **Saturation**: each cell caps near 10 effective due to the radius-2 limit; once a cluster saturates, players must expand outward.
- **Mutual annihilation**: the contest line is exactly this — neighbors cancel each other's signs.
- **No ko, no capture races, no surround tactics.**

**Topology.** Hex matters: 6-neighbor packing is denser than grid (4) and gives radius-2 cells the 19-cell footprint that makes the threshold reachable around 8–9 own stones. On a 4-neighbor grid the threshold (held fixed) would be much harder to reach and the game would resolve to majority/timeout more often. Hex is doing real work.

**First-mover advantage.** Mixed picture:
- Hand-played cluster vs cluster (Games 1, 3): **P1 wins both** — clear FMA.
- Greedy vs greedy: **P2 wins** because P1's greedy opening is corner-biased and P2 corrects to better cells. This is an artifact of greedy heuristic, not strategic depth.
- Random: roughly balanced (16/12/22 over 50). 
- Net: there is structural FMA in cluster play but the game is not P1-decided. Imbalance is real but not pathological.

Quantified seat-swap: Game 3 was the swap; P1 won there too with center cluster. The seat doesn't matter as much as **who plays center**. Center is the dominant first move; if both players know that, P1 takes it and gets the FMA. So the FMA is "P1 takes center" rather than something deeper.

---

## Phase 4 — Novelty Adversary

**Adversary's case (game is not novel):**

(a) **Catalog comparison.** This is closest to:
- **Tumbleweed** (Mike Zapawa, 2020): hex board, place stones with "shadow" influence, control via majority. Identical board. Tumbleweed has line-of-sight stack heights; this game has radius-2 decay influence. Both are "place to project influence on hex; threshold/territory wins." A Tumbleweed expert would pick this up in 5 minutes.
- **Reversi/Othello**: territory via flipping. Not the same — no flipping here. Skip.
- **Go**: hex go with no capture and threshold scoring. The "no capture + influence" reduction is essentially Go's territory-counting phase done continuously.
- **Hex (Connection)**: nope, no connection win condition.

(b) **CA literature.** Not applicable, no CA.

(c) **Simultaneous catalog.** Not applicable, alternating.

(d) **Re-skin argument.** "Tumbleweed on 8×8 with smooth decay instead of stacked shadows and a numeric threshold instead of majority." Strong analogy. Or: "Go without capture, with a continuous influence function and a scalar win threshold." Either of these gets you 80% of the way to the rules from first explanation.

(e) **Expert transfer.** A Go or Tumbleweed player would transfer immediately and play the cluster strategy without instruction. The contest stall would be a mild surprise (in Go you can also self-fill but it's almost always bad; here it's worse).

**Player 1 / Player 2 rebuttal:**

- **Tumbleweed shadows are line-of-sight, not radius-decay**. In Tumbleweed, a long row of friendly stones gives shadow on all empty cells in line; here, only cells within hex distance 2 receive any contribution. That changes opening theory completely: in Tumbleweed, a long line is strong; here it's much weaker than a tight cluster. **Game 1's center cluster vs P2 corner showed exactly this** — corners can't get the 12 dist-2 cells, and lost despite P1 and P2 having identical relative placements.
- **No capture changes endgame structure**. In Go, large territories require alive groups; here, a stone is permanent the moment it's placed, so the entire game is constructive and saturation-bounded. The contest stall in Game 2 has no Go analog — in Go, that pattern would lead to seki or capture races, not a flat draw at -2.10 vs 27.70.
- **Numeric threshold vs majority**. Tumbleweed needs more-than-half-of-territory; this game's 34.13 threshold is reachable with a tight ~9-stone cluster, far before the board fills. So the strategic horizon is ~16 alternating moves, not 60+. This compresses the game and removes most middlegame Go/Tumbleweed maneuvering.
- **R16 margin-tiebreak is genuinely novel.** No standard board game I know of resolves "both crossed threshold this turn" with margin comparison. Most use turn order or draw. Greedy-vs-greedy demonstrated this rule firing.

**Phase-2 evidence the analogy fails:** Game 2's effective P2 score going **negative** (-6.52) is impossible in Tumbleweed (shadows don't subtract from your own count) and weird in Go (you can't have negative territory). The contest stall is a feature of this specific game's signed-influence math.

**Novelty score: 4/10.**
- Direct analog (Tumbleweed) exists and transfers ~80%.
- The signed-influence math + scalar threshold + center-bias is a real twist, not just topology change.
- Above "X on a hex board" (which would be 2-3) but below "emergent dynamics with no analog" (7+).

---

## Phase 5 — Verdict

**Team ID:** `team-5`
**Game ID:** `8d12c8b92b71`
**Rules Summary:** Alternating placement on 8×8 hex; each stone projects signed radius-2 influence (+ for P1, – for P2); first player whose total board-value on their own cells exceeds 34.13 wins (margin tiebreak on simultaneous crossings).
**Topology:** 8×8 hex, true 6-neighbor.
**Turn Structure:** Alternating.

### SCORES (1–10)

- **Strategic Depth: 4** — Real but shallow. The dominant strategy is "tight cluster near center"; the only meaningful counter is the contest-stall draw. Greedy 1-ply diverges from cluster play in informative ways (Phase 2 showed the divergence) but the optimal frontier is narrow.
- **Emergent Complexity: 4** — Tempo, saturation, and mutual-cancellation are real emergent patterns, but the saturation point (~9 own stones) bounds the game horizon to ~16 plies. No combinatorial blow-up; no second-order tactics.
- **Balance: 4** — Mixed seat-balance. Cluster-cluster favors P1 (won both Game 1 and Game 3). Greedy-vs-greedy favors P2 (5/5, validating R16's worst-of-three probe). Random 16/12 with 22 draws. Net: imbalance is real but not extreme; the R16 margin fix is doing visible work, but the game still has a center-grab FMA for whichever side picks center first.
- **Novelty (post-adversary): 4** — Tumbleweed analog is strong; signed-influence + scalar threshold is a meaningful but limited innovation.
- **Replayability: 3** — Dominant strategy is known after 2 games; subsequent variation is limited to opening cell choice (a few good options) and whether to deploy the contest-stall. After ~5 games you have explored the game.
- **Overall "Would I play this again?": 3** — It is a clean, working game without bugs, and the R16 engine fixes are visibly correct. But it lacks the tactical surprise that drives repeat play.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed** (Zapawa 2020). Not identical because: signed continuous influence with hex-distance decay (vs line-of-sight shadows), scalar threshold (vs majority territory), no neutral stones / passing strategy. Secondary analog: Go's territory-counting phase made into the entire game, with capture removed.

### KILLER FLAWS

- **Center-grab dominates opening.** First mover plays (3,3) or equivalent center cell; corner placements are strictly worse because the radius-2 neighborhood truncates against board edges. This collapses meaningful opening choice to ~4 cells.
- **Contest-stall draw weapon.** P2 can weaponize adjacent contest to deny P1 a win — Phase 2 Game 2 went 40 plies with no winner; only the piece-count tiebreak resolves it (and it ties at 20–20). High-skill play may converge on draw-or-loss for P2, which is undesirable.
- **Greedy 1-ply heuristic is biased toward edges**, which produces unintuitive strategy under self-play training and likely explains the seat-imbalance signal R16's worst-of-three probe captures.

### BEST QUALITY

The signed-influence / mutual-cancellation dynamic in adjacent-contest play is genuinely interesting. It produces a "ko-like" flat region where both players' own-effective scores stagnate or go negative, rewarding strategic separation rather than direct confrontation. This is not a Go-style mechanism and it is not a Tumbleweed-style mechanism — it's specific to this rule set.

### IMPROVEMENT IDEAS

**Single rule change:** lower the threshold from 34.13 to ~22, OR penalize own-cell influence saturation (clamp per-cell contribution at e.g. 3.0). Either change shortens the cluster-build phase and forces players to commit to multiple small clusters rather than one fat central one. That would (a) reduce the center-grab dominance, (b) make the contest-stall less effective (fewer plies for P2 to drag the game), and (c) introduce a real "where do I expand next?" decision that the current parameters elide.

Alternative single change: **swap-pie rule on move 1** (P2 may take P1's first stone). This is a Tumbleweed/Hex-style fix that directly neutralizes the center-grab FMA without changing the engine.
