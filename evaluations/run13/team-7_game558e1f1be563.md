# Team-7 Evaluation — Genesis Run 13 — Game 558e1f1be563

**Team ID:** team-7
**Game ID:** 558e1f1be563 (rank 2 by GE 0.486)
**Archetype:** 2D hex 8×8, classic (no CA), threshold win on influence totals

---

## PHASE 1 — Rule Comprehension

### Board & Topology
- **Dimensions:** 2D hex grid, axis size 8 (64 cells total).
- **Adjacency:** offset-coordinate hex; each interior cell has 6 neighbours (odd/even row parity shifts the NW/SW vs NE/SE diagonals).
- **Action space:** 65 (one placement per cell plus PASS). No movement, no second-piece-per-turn.

### Turn & Action Structure
- Alternating turns, 1 stone per turn, placement only.
- **First-move-anywhere** is TRUE *per player* (each player's first stone may land anywhere; thereafter must be adjacent to an existing stone of either colour).
- Placement target: empty cell; constraint `adjacent_to_any` (any stone, friend or enemy).

### Capture / Propagation
- **Capture:** NONE. Stones placed are permanent.
- **Propagation:** influence, radius 1, strength **s = 1.4192**, decay **d = 0.4560**.
  - Every placement adds `±s` to the placed cell (sign = +1 for P1, -1 for P2) and `±s·d = ±0.6474` to each of the up-to-6 neighbour cells.
  - `board_values` are clamped to [-100, 100] but nothing here approaches that limit.

### Win Condition
- **Type:** threshold. Target dimension = 0 (P1 tracks positive totals, P2 tracks negated totals), **threshold = 39.658**.
- Checked after every move: a player wins when the signed sum of `board_values[c]` over cells **they own** exceeds +39.66 (for P1) or below -39.66 (for P2, reading negated).
- Other exits: max_turns=100 (decided by piece majority); consecutive passes end the game by piece majority.

### Computed "Placement Value"
Key derivation used throughout Phase 2. Placing a stone on a cell contributes to *your own* running total as:

```
Δ_own = s + k_friendly · 2d − k_enemy · 0
     ≈ 1.4192 + 1.2948 · k_friendly
```
(the enemy neighbours hurt *their* sum, not yours, because we only count values on our own cells).

Enemy neighbours of your new cell *do* subtract `d = 0.647` from the value on your new cell, but only once. So placing adjacent to `k_f` friendlies and `k_e` enemies contributes:
```
Δ_own = 1.4192 + 1.2948·k_f − 0.6474·k_e
Δ_opp = −0.6474·k_e     (their cells lose value)
```

With this formula, best-case density (3 friendly, 0 enemy) gives +5.3; typical (2 friendly) gives +4.0; shadow-attacks (0 friendly, 1 enemy) give +0.77 for you and -0.65 for them (swing +1.42). The threshold of 39.66 is reachable in ~10–15 stones at max density, ~20–30 stones in contested play.

### Degeneracies Checked
- **Not** a "move 1 wins" game — one stone gives +1.42, nowhere near 39.66.
- **Not** a forced 5-move win — minimum stone count to threshold is ~8 (all 6 neighbours friendly gives per-stone value ≈ 5.3; 8 of those = 42.4).
- **PASS is legal but almost never useful** — passing while below threshold yields nothing; two consecutive passes end by piece majority, which favours whoever has more stones.
- **No ko rule needed** — stones are never captured or overwritten.
- The `propagation_rule` IS load-bearing (not inert) — it is the entire scoring mechanism.

---

## PHASE 2 — Strategic Play

Because PASS is useless and legal moves shrink rapidly under `adjacent_to_any`, I played each game as an engine-verified sequence. All moves below were confirmed legal via `play_helper.py --action play`. I also built a Python move-evaluator that, for any position, clones the engine and reports resulting P1/P2 totals for every candidate move, which sped up greedy/best-response comparisons in the later phases.

### Game 1 — P1 density vs P2 density ("both build")

Opening I played by hand, move by move:

| Turn | P | Move | Rationale |
|------|---|------|-----------|
| 1 | P1 | (3,3) | Center — maximises future adjacency count |
| 2 | P2 | (4,4) | Adjacent to (3,3) on odd-row hex, contests center |
| 3 | P1 | (4,3) | 1 friend + 1 enemy; Δ_own=1.42+0.65-0.65=+1.42; Δ_own-to-friend also +0.65 → cluster gain +2.07 |
| 4 | P2 | (3,4) | Symmetric reply, same reasoning |
| 5 | P1 | (4,2) | 2 friends, 0 enemies → Δ_own +4.00 (the first "big" density move) |
| 6 | P2 | (3,5) | Shared neighbour of (3,4) & (4,4); Δ_own +4.00 |
| 7 | P1 | (5,2) | 2 friends; expands eastward (away from P2 cluster) |
| 8 | P2 | (4,5) | 2 friends; expands east, mirroring |
| 9 | P1 | (5,3) | 2 friends; still +4.00 |
| 10 | P2 | (4,6) | 2 friends south; +4.00 |
| 11 | P1 | (4,1) | 2 friends north; +4.00 |
| 12 | P2 | (3,6) | 2 friends |
| 13 | P1 | (3,2) | 2 friends — **engine-verified P1 total = 19.00, P2 total = 16.28** |

At this point I let both sides continue under **"maximise own total"** greedy (pure density, no disruption). The greedy extension from this position:

```
m14 P2→(2,4)  P1=19.00 P2=19.00
m15 P1→(3,1)  P1=23.00 P2=19.00
m16 P2→(2,5)  P1=23.00 P2=23.00
m17 P1→(5,1)  P1=27.01 P2=23.00
m18 P2→(2,6)  P1=27.01 P2=27.01
m19 P1→(3,0)  P1=29.72 P2=27.01
m20 P2→(1,4)  P1=29.72 P2=29.72
m21 P1→(4,0)  P1=33.73 P2=29.72
m22 P2→(1,5)  P1=33.73 P2=33.73
m23 P1→(5,0)  P1=37.74 P2=33.73
m24 P2→(1,6)  P1=37.74 P2=37.74
m25 P1→(2,0)  P1=40.45 P2=37.74   <-- P1 crosses 39.66, wins
```

**Result:** Player 1 wins at turn 25. Mechanism: when both players play dense, they reach threshold at the *same rate per turn*, but P1 moves first, so P1 crosses the line first. Roughly +2.7 per turn in the midgame; ~+4.0 when a move hits two friends.

### Game 2 — P1 density vs P2 shadow-block ("disruption")

I swapped P2's heuristic to **"-opp"** (pure disruption: minimise P1's total, ignore own). Opening move unconstrained; the greedy search placed P1 at (0,0) corner-start and P2 responded on (1,0) (adjacent to P1, subtracting 0.65 from P1's cell).

```
m1  P1→(0,0)  P1=1.42  P2=0.00
m2  P2→(1,0)  P1=0.77  P2=0.77   (P2 placed adjacent to P1, both lose 0.65)
m3  P1→(0,1)  P1=3.49  P2=0.77   (P1 builds own cluster)
m4  P2→(1,1)  P1=2.84  P2=2.84   (P2 shadows again)
...continues as a marching column+shadow-column down the left edge...
m14 P2→(1,6)  P1=13.17 P2=13.17
...
m50 P2→(6,2)  P1=35.48 P2=36.77  (P2 overtakes!)
m51 P1→(7,3)  P1=38.19 P2=36.77
m52 P2→(6,4)  P1=37.55 P2=38.84
m53 P1→(7,4)  P1=39.61 P2=38.19  (P1 just short of threshold)
m54 P2→(7,2)  P1=38.97 P2=40.26  <-- P2 crosses 39.66, wins
```

**Result:** Player 2 wins at turn 54. Mechanism: P2 never tries to reach threshold by density; instead P2 shadows every P1 placement, subtracting -0.65 from the P1 cell. Despite getting only +0.77 per stone, P2 also gets the +0.65 adjacency bonus when their shadow-columns touch prior P2 shadows, so P2 slowly accrues enough to cross threshold AFTER disrupting P1 enough to keep them below it. Also P2 gets the last move of the board because the whole 64-cell board fills.

This was the surprise of the evaluation.

### Game 3 — Seat-swap, mixed strategy

To test whether Game 2's result depended on seat, I ran the same pairing as Game 2 but swapped which player used "-opp". Greedy P1 using pure blocking vs P2 using pure density. Result:

```
turn=44 winner=2   (P2 reaches threshold)
```

So even when **P1** plays disruption, **P2** (density) wins — because now P2 is the sole builder and, since P1's own-total never grows past P2's density rate, P2 scores faster. Flip seat of the anti-strategist and it still loses if the opponent builds cleanly.

That is asymmetric: **the anti strategy is only a winning response when you are the second mover.** P1 cannot profitably play anti — anti as P1 loses tempo without out-blocking anyone.

### Per-player strategy reflections

**Player 1 reflection (seat 1 in games 1–2, seat 2 in game 3):**
My natural strategy was dense cluster growth in the centre. In Game 1 this worked (+4 density moves throughout). In Game 2 I was trapped: greedy density was countered 1-for-1 by P2's shadow, and my column took the full board length while P2's shadow column quietly accumulated its own interior bonds (shadows touching shadows) and passed threshold on the last move.
What I would do differently: break symmetry by making a diagonal move that P2 cannot shadow with a single stone. Or sacrifice early tempo to go for a 3-friendly-neighbour corner cluster (which requires one "empty gap" move that loses tempo but later pays +5.3 per stone).

**Player 2 reflection (seat 2 in games 1–2, seat 1 in game 3):**
In Game 1 mirroring P1's density directly lost by tempo. In Game 2 the shadow strategy was startlingly effective — it feels exploitative because P1 must push density (otherwise P2 builds faster), yet any P1 density cell can be neutralised by a single adjacent P2 placement. My strategy guide: as second mover, always place adjacent to the newest enemy stone unless it would sacrifice a shared bond that you already had.

### Strategy guides

**For P1 (mover 1):** Open centre or near-centre. Get to ≥2-friendly moves by turn 5. Avoid placing next to lone enemy stones — you waste a tempo on +0.77 when +4 is available elsewhere. Race straight to threshold; expect to win on turn ~23–25 if opponent also builds.

**For P2 (mover 2):** Do NOT race P1 in pure density — you lose by a tempo. Instead shadow every P1 placement at the cell that sits between their new stone and the boundary of their cluster. Your shadow stones also become a cluster (they are adjacent to each other), so you accumulate value while denying P1. Be the last placer when the board fills — you will cross threshold on or near the final move.

---

## PHASE 3 — Strategic Analysis (joint)

**Distinct viable strategies?** Yes, two: (A) pure density maximisation, (B) shadow/disruption. Game-tree investigation (4×4 strategy matrix) shows:

| P1\\P2 | my | diff | hybrid | anti |
|--------|----|----|--------|------|
| my     | P1 t27 | P1 t29 | P1 t27 | **P2 t54** |
| diff   | P1 t29 | P1 t31 | P1 t29 | **P2 t54** |
| hybrid | P1 t27 | P1 t29 | P1 t27 | **P2 t54** |
| anti   | P2 t44 | P2 t60 | P2 t44 | no-winner t66 |

Reading across: if you are P2, **anti dominates — it beats every P1 builder**. If you are P1, **anti loses against density but draws vs opponent's anti**.

**Counter-play.** Yes, meaningfully. The matrix is non-transitive-ish: density beats density-mirror, anti beats density, anti-vs-anti stalls. If P2 commits to anti, P1's best response is probably also anti (forces a piece-majority endgame). If P1 plays anti, P2 should switch to density. So both players have adaptive incentives and the game is not dominated by one plan.

**Short vs long-term tension.** Present. A "density" stone pays immediately but leaves opponent free to race; a "shadow" stone costs you +3 of your own building speed but saves you -0.65 of opponent's. The correct weighting depends on how close each side is to threshold. Late-game, when opponent is within one or two stones of 39.66, a blocking stone is worth far more than a building stone. This creates a tempo crossover point that a smart player must identify.

**Emergent concepts.** We identified:
- **Tempo / initiative:** clearly present — Game 1 turned on P1 crossing threshold one move before P2.
- **Influence as territory proxy:** stone placements build diffuse "influence regions"; cells with many friendly neighbours are valuable like territory corners in Go.
- **Shadow / parasitic play:** the anti strategy is genuinely emergent — the rules never mention blocking, but the threshold-on-own-cells structure plus adjacent-to-any plus overlapping influence radii creates it naturally.
- **No ko / capture / liberty** concepts, since stones are permanent.

**Does topology matter?** Yes. On a square grid with 4 neighbours, the best density is k_f=2 giving Δ=+4.01, same as hex. But hex allows k_f=3 density configurations (triangles) which square does not — max_density on hex cells can reach +5.30 per cell, vs ~+4 on square. In our games the triangle-configuration (3-friendly placement) was actually rare because it requires specific geometry, but it is the reason hex is the "right" topology for this rule: it makes density slightly more rewarding relative to disruption.

---

## PHASE 4 — Novelty Adversary (mandatory)

### Adversary argument

**"This game is Go with the rules filed off."** Specifically:

1. **vs Go.** Placement on a grid, alternating, goal is to build territory on your own cells. The "influence" propagation is a direct analog of Go's aesthetic concept of stone influence on surrounding points. Threshold 39.66 on summed influence is equivalent to "whoever has more territory wins" — i.e. area scoring. Differences: no capture, no liberties, no ko, smaller 8×8 board. Response: "this is Go without the interesting parts" — *capture* is what makes Go deep, and this game has deleted it.
2. **vs Hex.** Hex topology, placement, no capture, want to dominate regions. The immediate rebuttal: Hex's win condition is a connection, not an accumulation. Different.
3. **vs Reversi/Othello.** No — no flipping, no captures. Reject.
4. **vs Go-Moku / Gomoku / Connect6.** No — no line-of-N goal. Reject.
5. **vs Y / Havannah.** No — connection win. Reject.
6. **vs Amazons.** No movement, no shooting. Reject.
7. **vs Lines of Action.** No — pieces do not move. Reject.
8. **vs Mancala / Nim.** No pits, no Nim values. Reject.
9. **vs Life-like CA.** This is a **CLASSIC** game, no CA. Reject as a CA comparison. Not applicable (a).

**Re-skin hypothesis.** Adversary proposes: "this is **influence-Go** — the board and action space are a direct Go encoding, and the threshold win is a numerical area-scoring. An expert Go player would have an immediate advantage because influence-maximising shapes (empty triangles on hex correspond to ponnuki-like shapes on square Go) are *already* the canonical Go shapes." The adversary specifically argues: "ponnuki + wall = density cluster; shadow stones = sabaki invasions; tempo race = endgame yose-counting."

**(d) Expert-transfer test.** Would a Go expert have an immediate advantage?
- Partially yes: a Go dan player's intuition for building thick shapes and invading would translate to density + shadow play.
- But NO: the Go player would over-invest in connection and eye-space (worthless here because no capture), and would under-invest in pure adjacency count (the only thing that matters). They would also fail to realise that *placing next to the enemy is usually bad* (wastes tempo for +0.77 vs +4.0 density elsewhere). A Go beginner trained on THIS game's numbers would likely beat a Go dan in their first session once the dan realised the capture rules are missing.

### Rebuttal from Phase 2 evidence

1. **The shadow strategy in Game 2 has no Go analog.** In Go, playing 1-space away from an enemy stone is an attack that threatens future captures. Here it does not threaten — it just shaves numerical value. More importantly, in Go, the shadow player would also give the opponent a huge outside wall — a losing position. In this game, the shadow player *wins* from turn 54, because the shadow column itself has the same density bonuses. A Go player would never consider this pattern; it emerges purely from the `threshold-on-own-cells + adjacent-to-any + influence-radius-1` interaction.
2. **Captureless Go devolves to either all-board-fill or threshold race.** This game picks the threshold race, and the specific threshold constants (s=1.42, d=0.456, threshold=39.66) tune it so that pure density beats pure density by tempo but loses to shadowing — a tension Go does not have.
3. **Triangle-density on hex is rewarded more than Go's "ponnuki + wall"** shapes. The 3-friendly-neighbour configuration on hex yields +5.3 per cell placed, a geometric bonus that is impossible to replicate on Go's square board and that makes hex the native topology, not square Go.

### Team verdict on novelty

The game is *not* a re-skin — but it IS a **highly constrained captureless Go variant with a numerical area-scoring win**. The emergent shadow strategy and the non-transitive density-vs-anti matrix are genuine novelties that would not arise in Go. However, the "core experience" (place stones to influence regions, balance building vs attacking) is familiar from Go. 

**Novelty score: 5/10.** Strongest adversary argument: *"influence-Go with threshold scoring — an experienced abstract-game player will recognise the pattern instantly."* Strongest rebuttal: *"the shadow/anti strategy in Game 2 has no Go analog and emerges from the capture-free + threshold-on-own-cells combination; the game's Nash equilibrium looks unlike Go's endgame."*

---

## PHASE 5 — Verdict

**Team ID:** team-7
**Game ID:** 558e1f1be563
**Rules Summary:** On an 8×8 hex grid, players alternately place stones (constrained to be adjacent to existing stones after first move). Each placement adds positive/negative influence (strength 1.42, decay 0.46) to itself and radius-1 neighbours. First player whose owned cells' summed influence exceeds 39.66 wins; no capture.
**Topology:** 2D hex 8×8 (64 cells), offset-coordinate adjacency, 6 neighbours interior.

### Scores (1–10)
- **Strategic Depth: 6/10** — there is real non-trivial strategic tension (the 4×4 strategy matrix shows non-dominated play with counter-strategies). But the search space per turn is small (≤17 legal moves once adjacency applies) and the threshold math is largely linear in placement count, so a greedy lookahead of 2–3 ply probably plays near-optimally.
- **Emergent Complexity: 6/10** — the shadow/anti strategy is a genuine emergent phenomenon, unmentioned in the rules. Tempo races and last-move-wins situations emerge naturally. But there is no capture, no ko, no chain formation — so the complexity ceiling is lower than Go/Hex.
- **Balance: 5/10** — with pure density play, P1 wins by tempo in every simulated greedy line (25–29 turns). With shadow play available, P2 has a winning counter. The asymmetry is handled by strategic choice, not built into the rules (no komi, no second-player compensation). Trained PPO gets 0.5 winrate with seat-swapping, which confirms the game is *playable balanced* but relies on P2 finding the anti strategy.
- **Novelty (post-adversary): 5/10** — captureless influence-Go on hex with threshold scoring. Shadow strategy is emergent and not Go-native; the overall game feel is very close to influence-Go.
- **Replayability: 4/10** — once you know the 3 canonical strategies (density, shadow, anti-vs-anti stall), most games reduce to seat-role playbook. Without hidden state, without randomness, and with small branching factor, games converge quickly after a few plays.
- **Overall "Would I play this again?": 5/10** — interesting once or twice to discover the shadow counter. Limited long-term depth.

### Closest Known-Game Analog
**Go with capture removed and area-scoring replaced by a diffuse influence-sum threshold.** It is NOT identical because (a) the shadow/anti strategy is a winning line for the second player that Go does not have (Go's second-player shadow play loses to outside walls), (b) no captures means no life/death puzzles, and (c) the win condition is absolute (threshold) rather than relative (more territory than opponent).

### Killer Flaws
- **P1 tempo advantage in density play is unmitigated.** Both players running greedy "maximise own influence" always gives P1 a win at ~turn 25. There is no komi or analogous rule. The game is *only* balanced if P2 discovers the shadow strategy.
- **PASS is functionally inert** (never useful during a contest) — wastes an action slot.
- **Endgame convergence issue:** when both players play anti-vs-anti, my sim hit a no-winner state at turn 66 — likely a double-pass ending by piece-majority, but this mode-collapses the game into a piece-count contest rather than a threshold race.
- **Influence decay and threshold are floats** (d=0.4560, threshold=39.6580) — no clean rational form for players to reason about, making hand-analysis painful. Pure quality-of-life flaw.

### Best Quality
The **shadow/disruption counter** is a genuinely emergent strategic pattern that the rules do not telegraph. Discovering that pure greedy density is *not* dominant, and that a capture-free game can still have a winning defensive strategy, is the most satisfying moment of play. The non-transitive 4×4 strategy matrix (density > mirror-density, anti > density, anti = anti) indicates there is real game-theoretic structure here.

### Improvement Ideas
**Add a komi for P2** (or equivalently, set P2's threshold lower: say +39.66 for P1, -36.0 for P2). Simulation suggests a ~2.7-point handicap would neutralise P1's tempo advantage in density play while preserving the shadow counter. Alternatively, **add a "value-sink" rule**: cells adjacent to two or more enemy stones have their own-value halved. This would make shadow play more expensive and restore density as a viable P1 strategy without breaking the threshold race.

---

## Final Scores

| Metric | Score |
|--------|-------|
| Strategic Depth | **6/10** |
| Emergent Complexity | **6/10** |
| Balance | **5/10** |
| Novelty (post-adversary) | **5/10** |
| Replayability | **4/10** |
| Overall "Would I play this again?" | **5/10** |

**Verdict:** A competent but shallow captureless-Go variant on hex. Saved from 3/10 by a genuinely emergent "shadow" counter-strategy that makes the 4×4 strategy matrix non-transitive. Loses depth relative to Go (no capture, no chains, no ko) and relative to Hex (no connection goal). Worth playing 2–3 times to understand the tempo-vs-disruption trade-off, then shelving. Go Essence score of 0.486 seems slightly generous given the small search space and the exploitable P1-tempo advantage in density play.
