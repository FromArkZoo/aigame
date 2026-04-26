# Run 16 Human Evaluation — team-4 — Game 8d12c8b92b71

**Team ID:** team-4
**Game ID:** 8d12c8b92b71
**Run:** 16 (GE champion of R16)

---

## Phase 1 — Rule Comprehension

### Board structure
- 2D, axis size 8, **hex topology** (pointy-top offset coordinates with 6-neighbor adjacency for interior cells; edges have fewer neighbours; non-wrapping).
- 65 actions: 64 placement cells (`action_id = y*8 + x`) plus action 64 = **pass**.

### Turn structure
- **Alternating** (`turn_type=alternating`, `pieces_per_turn=1`). Players place 1 stone per turn.
- Two consecutive passes end the game as a draw (R13+ engine fix).
- `max_turns = 100`.

### Action types and constraints
- Placement only — no movement, no capture.
- Target = empty cells, anywhere on the board. First move anywhere allowed.

### Capture / CA
- `capture_type: none`. **No capture mechanic at all.** No CA either (`Cellular Automaton: No (classic)`).

### Propagation / influence
- `prop_type=influence`, **radius=2 (hex distance)**, **strength≈0.984**, **decay≈0.6946** per ring.
- Self cell value = 0.984; ring-1 (6 hex neighbours) = 0.684; ring-2 (12 hex cells in the radius-2 ring) = 0.475.
- Player 1's stones add positive influence; player 2's stones add negative influence; `board_values` is signed and additive (capped at ±100).
- A single isolated stone radiates ~7.4 total signed value over a ~19-cell hex neighbourhood.

### Win condition
- `condition_type=threshold`, **target_dimension=0**, `target_dimension_p2=-1` (so P1 sums on dim 0; P2 sums on dim 0 too via the negation in `_check_threshold`).
- A player wins when the sum of `board_values` over the cells **they own** exceeds **34.129**.
- R16 margin-tiebreak: if both players cross on the same tick, higher margin wins; equal margins → draw.
- Crucially the threshold sum only counts cells the player actually owns (a stone there). Empty-cell influence does NOT count toward the score, but it boosts the value of any future stones placed there.

### Degenerate-rule check
- No degenerate auto-wins: 34.13 is reachable but not trivial. With dense own-cluster mutual reinforcement (~0.984 self + 6×~0.684 ring-1 boosts cumulating), a single contiguous blob of ~10–13 stones can clear threshold. Greedy-vs-greedy converges in 15–17 plies (well under max_turns). Random play averages 54 turns and resolves ~67% of the time without hitting double-pass or max_turns.
- No dead rules: every parameter (radius 2, decay, threshold) is in the active regime.

---

## Phase 2 — Strategic Play

All moves verified through the engine via `factory.create_engine(game)` + `engine.step()` and `engine.board_values`. Action IDs are `y*8 + x`. Coordinates printed as `(x,y)`.

### Strategies used

- **Greedy-build** (G): one-ply lookahead picking action `a` to maximise `own_score - 0.5 * opp_score`. Naturally clusters stones for self-reinforcement.
- **Disruptor** (D): one-ply lookahead picking `a` to maximise `-2 * opp_score + 0.5 * own_score`. Crowds opponent's growing cluster with negative-influence stones to suppress their cell values.
- **Mirror** (M, used only in seat-balance tests): plays `63 - last_opponent_move`.

### Game 1 — P1 Greedy vs P2 Greedy

P1 opens (0,0). Both players build symmetric corner clusters. Because P2 mirrors P1 every turn, scores stay perfectly tied through plies 4, 6, 8, 10, 12, 14 (`s1 == s2`), but on every odd ply P1 has a one-stone lead. **P1 hits 40.08 on turn 17 while P2 sits at 33.93** (one stone behind threshold) → **P1 wins by tempo**.

| Turn | Player | Action (x,y) | s1 | s2 |
|------|--------|--------------|----|----|
| 1 | P1 | 0 (0,0) | 0.98 | 0.00 |
| 2 | P2 | 3 (3,0) | 0.98 | 0.98 |
| ... | ... | ... | ... | ... |
| 16 | P2 | 13 (5,1) | 33.51 | 33.93 |
| 17 | P1 | 25 (1,3) | **40.08** | 33.93 |

**P1 reflection:** "I built a tight 9-stone hex blob in the NW quadrant. Mirroring the opponent's tempo for free was the entire game; I never had to actively defend. I would not change anything — when both sides build, the second-mover always loses by ≥6 points."

**P2 reflection:** "Building a competing blob loses by tempo. Greedy is a trap from the second seat. Surprise: even sitting in the diagonally-opposite corner with full freedom, the threshold is symmetric and P1's clock is unbeatable. Endgame reached the threshold cleanly (no double-pass)."

### Game 2 — P1 Greedy vs P2 Disruptor

P2 sits *next to* P1's first stone, then ladders alongside P1's growing pillar. After ply 21 P1 has built a full left column (s1=15.20) but it's surrounded by P2 stones on column 1, capping the cell-values at ~1 each. **From turn 22 onward P2 abandons the disruption and walks into the wide-open centre and right side**, building a new cluster around (3,4)/(3,5)/(3,6) that has no opposition. **P2 wins on turn 30 with s2=38.98 vs s1=21.81** — a >17-point margin.

Key inflection: by ply 18 P2 had only 7.8 effective points of its own but had pinned P1 to a poorly-reinforcing strip. Once P2 broke off and built freely in the centre, the centre's higher hex-neighbour count (interior cells have 6 neighbours vs 3 at the corner) **gave each centre stone ~1.6× the value of an edge stone**.

**P1 reflection:** "Greedy locked me into the corner. I should have either (a) opened in the centre, or (b) noticed the disruption and played a *splitting* move into the centre myself once P2 stopped following. The endgame did reach threshold (no draw)."

**P2 reflection:** "Disruption alone wouldn't have crossed threshold (negative influence on opponent's cells doesn't translate to my own score). I needed the second phase: once the opponent is contained, **abandon them and build freely**. The transition at ply 22 was the entire game."

### Game 3 — Seat swap. P1 Disruptor vs P2 Greedy

I deliberately put the Disruptor on the disadvantaged second-mover... no, on the *first* seat to test if Disruption + first-mover wins. **It does not.** P1 spent moves 1–22 sitting next to and across from P2's developing top-right cluster (cells 4..7 of rows 0–4). P2 ignored disruption and just built. By ply 22 s1=9.82 but s2=17.30. P1 belatedly switched to building from ply 23, but by then P2 was already past 25 and the centre was contested. Game ended ply 40 with **P2 wins, s1=32.70, s2=35.85**.

**P1 reflection (Disruptor seat):** "Pure disruption is strategically bankrupt — you spend negative-influence stones suppressing the opponent without growing your own threshold count. By the time I switched to building, the opponent had occupied the centre. The strategy needed an earlier transition (~ply 8 not ply 23). Did reach threshold."

**P2 reflection (Greedy seat 2):** "Even from the second seat, pure-build wins against pure-disruption because the threshold counts only my own cells. The opponent's negative influence on the cells I own *does* hurt me — at ply 30 my centre cells were running 0.7 instead of 1.4 — but they suppress my growth, not stop it. I won by 3.15 points; closer than Game 2 but still decisive."

### Strategy Guides

**P1 (alternating, first mover) — strategy guide:**
1. Open in or near the centre (rows 3–4, cols 3–4) — interior hex cells have 6 neighbours vs 3 at corners, yielding ~1.6× cell value at threshold time.
2. Build a tight contiguous blob — every adjacent self-stone adds +0.684 to each of its 6 neighbours' threshold-counted values (i.e. each interior stone gets ~+4 from a fully-surrounding hex flower).
3. Ignore the opponent unless they place inside your radius-2 envelope; their negative influence on cells you own subtracts roughly 0.475–0.684 per intrusion.
4. Tempo wins. From ply 1 you have +1 stone forever; threshold is symmetric, so you will cross first if mirroring.

**P2 (alternating, second mover) — strategy guide:**
1. Do **not** mirror — you will lose by tempo (Game 1 demonstrates).
2. Either: (a) play *adjacent* to P1's stones early to cap their cell-value reinforcement, then around ply 6–8 break off and build your own cluster on the far side; or (b) immediately establish a separate cluster as far from P1 as possible (≥ hex-distance 5) and try to out-shape P1 by exploiting more interior cells.
3. The Disruptor-then-Build hybrid (Game 2 P2) won decisively. Pure-build (Game 1 P2) lost. Pure-disrupt (Game 3 P1) lost.
4. Watch the influence-field, not the stone count. Two adjacent P2 stones in interior territory > four P2 stones in a corner.

---

## Phase 3 — Strategic Analysis (joint)

### Seat-identity bias acknowledgment
One agent played all six roles. We mitigated by separating each role's reasoning in writing before switching, by relying on the engine's authoritative scoring, and by using deterministic strategies (Greedy/Disruptor) so seat-of-the-author didn't flavour the play.

### Distinct viable strategies?
Yes — at least three:
- **Pure-build** (greedy clustering): wins from seat 1, loses from seat 2.
- **Pure-disrupt** (anti-cluster): loses from either seat (no threshold contribution).
- **Disrupt-then-build** (hybrid): wins from seat 2 against pure-build (Game 2 result).

The win matrix from our 3 games + extra seat-balance probes:

| P1 strategy | P2 strategy | Winner | Margin |
|------------|-------------|--------|--------|
| Greedy | Greedy | P1 | +6.15 |
| Greedy | Disrupt-then-build | P2 | +17.17 |
| Disrupt-then-build | Greedy | P2 | +3.15 |
| Greedy | Mirror | P1 | +7.52 |

### Counter-play?
Yes — Disrupt-then-build is a real counter to Greedy, demonstrating non-trivial best-response structure. But there's no Rock-Paper-Scissors triangle: Pure-disrupt loses to everything, and there's no apparent counter to Disrupt-then-build other than meta-disruption (we did not have time to test).

### Short vs long-term tension
**Yes**, sharply. Pure-greedy plays for immediate score; Disruptor plays for future suppression at the cost of present score. The ply-22 inflection in Game 2 is exactly this tension resolving — disruption capital paid off when converted to building.

### Emergent concepts
- **Territory** — clusters function like Go territory; the influence field makes interior cells more valuable than corners.
- **Tempo / initiative** — first-mover always has +1 stone; in symmetric play this is decisive.
- **Mutual annihilation** — adjacent enemy stones cancel each other's cell-values (P1 stone next to P2 stone makes both cells radiate 0.984 + (-0.984) = 0 in net contribution). This creates a "wall" mechanic where contact lines are dead zones.
- **Edge penalty** — corner stones see 3 instead of 6 ring-1 cells, losing ~50% of their reinforcement. Hex topology bakes this in geometrically.
- No ko fights (no capture), no connection (no connection win), no piece-counting endgame (threshold).

### Topology
**Yes, the hex topology matters.** With 6 interior neighbours vs grid-4, the same radius gives 19 vs 13 affected cells, increasing cluster-density payoff. Hex also makes the geometry rotationally smoother, removing the diagonal/orthogonal asymmetry that would otherwise create dominant axes. Without hex this becomes Go-like territory on a square grid; the hex is integral.

### First-mover advantage
**Severe.** In greedy-vs-greedy across 6 different P1 openings, P1 won every game by 6–8 effective points and 15–17 plies. The R16 metric of "worst-of-three across trained / random / greedy probes" *should* have caught this — yet this game scored highest. **This is evidence that the seat-balance fitness probe is not fully calibrated even after R16's fix.**

The only way to take the first-mover advantage out of this game would be to add a *pie rule*, a handicap, or to remove the threshold mechanic in favor of something less tempo-sensitive (e.g. piece-majority at max_turns).

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary's case (the game is not novel)

(a) **Vs Go:** Identical board (8×8, but in hex instead of square), placement-only, no capture rule. The threshold-with-influence acts like Go's "territory" but counted by sum-of-radiating-influence instead of sum-of-empty-cells-bordered-by-one-color. The closest direct analogue is **Tumbleweed** — a hex placement game where pieces radiate "line of sight" influence toward empty cells, and you build "stacks" of influence; the strategic shape is dense-cluster-vs-disruption, just like this game. **Verdict: ≈70% Tumbleweed.**

(b) **Vs Tumbleweed specifically:** Tumbleweed uses line-of-sight, not radius-2 isotropic decay; pieces are stacks of variable height; no win threshold but a final majority count. So the *mechanic* differs but the *strategic surface* (place to radiate, build clusters, edge=weak) is identical.

(c) **Vs Y / Hex / Havannah:** Unlike all of those, no connection win, no capture. Different family.

(d) **Vs Reversi/Othello:** Both have radiating influence (Othello flips along lines) and edges-are-weak corners-are-strong (corners in Othello). But Othello flips, this doesn't. Different family.

(e) **Vs CA / Life-like:** No CA at all. Not relevant.

(f) **Vs Blotto / simultaneous games:** Alternating, not simultaneous. Not relevant.

(g) **Coordinate-transformation argument:** Replace the influence kernel with "Go-like territory counting" and you get hex Go without capture. Replace the threshold with "majority at max_turns" and you get a heavily-simplified Tumbleweed. **The adversary claims this is "Tumbleweed lite on hex with a kernel-counting score and a hard threshold."**

(h) **Expert transfer test:** Would a Tumbleweed expert transfer immediately? Partially. They'd correctly identify centre > edge, dense > sparse, contact-walls = dead zones. They'd misjudge the threshold tempo (Tumbleweed has no race; this game has). They'd misjudge the Disruptor strategy (Tumbleweed lacks negative-influence). About **70% transfer**, 30% novel structure.

### P1 + P2 rebuttal

We point to specific Phase-2 moments where the Tumbleweed/Go analogies fail:

1. **Game 2, ply 22 — the abandonment inflection.** In Tumbleweed and Go you do not abandon a disrupted territory and start over; you can't, because every turn is a building move. In this game, *because* there is no capture and *because* the threshold counts only own-stone cells, walking away from a contested zone is a valid strategy — it's the entire game in Game 2. Tumbleweed has no parallel.

2. **Game 1 tempo loss.** Pure-symmetric mirroring loses in this game by exactly one stone's worth (≈6 points). Go and Tumbleweed both can be drawn or even won by mirror-strategy from seat 2 with a komi/handicap. Here, the threshold race makes mirror unwinnable without a pie rule. This is a structural property of the threshold mechanic that's absent from both reference games.

3. **Negative-influence walls.** In Game 3, P1's (3,3) stone next to P2's (3,4) made both cells contribute 0 net to threshold sums of their respective owners. Go's contact lines don't have this property (stones don't radiate); Tumbleweed pieces add their stack height regardless of opponent proximity. The **mutual-annihilation contact line** is genuinely a property of this scoring rule, not of either reference game.

4. **Threshold-race endgame.** Both Go and Tumbleweed end at predetermined endpoints (passes / board fill). This game ends *the moment* a threshold is crossed — meaning the actual race is to get to ~10–12 well-placed stones first. That race structure is closer to **Pente / Connect6** (race to a pattern) than to a territory game, even though the influence mechanic looks territorial.

### Novelty score

We rate **5/10**. Same family as Tumbleweed but with three real innovations: (a) negative-influence contact-walls, (b) abandonment-and-rebuild as a viable second-seat strategy due to the threshold mechanic, (c) the threshold race endgame replacing endpoint scoring. The 8×8 hex board and influence kernel are off-the-shelf; the threshold-counts-only-own-cells rule is the genuinely original piece. Not "X on a hex board" (would be 2-3); not fully emergent (would be 7+). Five.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** 8d12c8b92b71
**Rules Summary:** Alternating placement on an 8×8 hex board. Each stone radiates ±0.984 influence with hex-radius-2 decay (≈0.69 per ring). First player whose sum of influence on cells they own exceeds 34.13 wins; no capture, no CA. Pass action available; double-pass = draw; max 100 turns.
**Topology:** 8×8 hex (pointy-top offset, 6 interior neighbours, non-wrapping)
**Turn Structure:** Alternating

### Scores (1–10)

- **Strategic Depth: 6** — Three distinguishable strategies (Greedy / Disruptor / Disrupt-then-build) with non-trivial best-response (Hybrid beats Greedy, Greedy beats Mirror and Pure-Disrupt). The ply-22 inflection in Game 2 is a genuine strategic decision point. But the depth ceiling is low: most games resolve in 15–30 plies, the threshold race dominates, and there is no long endgame.

- **Emergent Complexity: 6** — Negative-influence contact walls, edge-vs-centre cell-value asymmetry baked in by hex geometry, abandonment-and-rebuild dynamic. No CA emergence, no connection emergence. Mid-tier.

- **Balance: 3** — P1 wins greedy-vs-greedy across all 6 openings tested, by 6–8 points and 1–2 plies. P1 also wins greedy-vs-mirror. P2 only wins by playing a hybrid Disrupt-then-build strategy that requires deliberate strategic choice. The threshold mechanic is fundamentally tempo-sensitive in a way that punishes the second seat — no pie rule or komi exists. **This is a real first-mover bias the R16 seat-balance probe failed to penalise**, which is interesting evaluation evidence in itself.

- **Novelty (post-adversary): 5** — Tumbleweed-adjacent on hex; threshold race + own-cell-only counting + negative-influence walls are the genuine innovations. Not a re-skin but not emergent.

- **Replayability: 5** — Three viable strategies and a fast (15–30 ply) game length make it easy to play many rounds, but the dominant role of P1 advantage means competitive play needs a pie rule. The strategy space, once explored, plateaus quickly.

- **Overall "Would I play this again?": 5** — Pleasant, fast, compact. Tempo bias is a deal-breaker for serious play, but the abandonment dynamic is genuinely interesting and the hex influence map is visually elegant.

### Closest known-game analog
**Tumbleweed** (Mike Zapawa, 2018), a hex placement game where stones radiate line-of-sight influence and players build stacks. This game replaces line-of-sight with isotropic radius-2 hex decay, replaces stack-height with signed additive influence (so opponent stones cancel), and replaces majority-at-end with first-to-cross-threshold. Same strategic family — cluster building, edge weakness, contact walls — different scoring metric.

### Killer flaws
1. **Severe first-mover advantage** in symmetric strategies (greedy vs greedy, mirror, etc.). P1 wins 100% of greedy probes from 6 openings tested. No pie rule means competitive play would require explicit handicap.
2. **Pure-disruptor strategy is strictly dominated** — disruption stones don't add to threshold count, so a player who only disrupts can never win. Limits strategic diversity.
3. The R16 fitness metric (worst-of-three across trained/random/greedy) should have flagged the greedy-vs-greedy P1 dominance and didn't — this game scored highest in R16. **Evidence the seat-balance fix is incomplete.**

### Best quality
The **negative-influence contact wall** mechanic. Adjacent enemy stones zero each other's threshold contribution, creating "dead zones" along contact lines. This is a structurally novel territory mechanic absent from Go and Tumbleweed, and it directly motivates the abandonment-and-rebuild strategy that gave Game 2 its strategic high point.

### Improvement ideas
**Add a pie rule** (or equivalent komi of ~6 effective points to P2's threshold target). This would equalise the greedy-vs-greedy seat balance and force genuinely diverse opening theory rather than "P1 wins on tempo." A simpler alternative: lower the threshold to ~28 so games end earlier and P1's tempo advantage scales down with shorter games (though this also reduces strategic depth). Best: pie rule.
