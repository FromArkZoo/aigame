# Run 16 Human Evaluation — team-20 — game 4d9c5796dd18

## Phase 1 — Rule Comprehension

**Board structure:** 2D, 8x8, **Moore topology** (8-neighbor / king's-moves adjacency).
*Note:* `play_helper.py rules` mislabels the topology as "von Neumann"; reading `topology.py` and inspecting `topo.get_neighbors((3,3))` confirms 8 diagonal+orthogonal neighbors. This is documented as a known prompt caveat.

**Turn structure:** **Alternating** (P1 then P2). One placement per turn. Used `play_helper.py` (NOT `sim_play_helper.py`).

**Action types:** `place` only — drop a stone on any empty cell. Action 64 is `pass`. 65 actions total. `first_move_anywhere = True`.

**Placement constraints:** target = empty, constraint = anywhere. No restriction.

**Capture dynamics:** **Surround capture** (Go-style) with `threshold=2`. Note: for `surround` capture, the `threshold` field is ignored — the engine just removes any enemy group adjacent to the placed stone whose liberties drop to zero. **On Moore topology this rule is effectively dead**: a single isolated stone has 8 Moore liberties, so capturing requires filling all 8 surrounding cells (or perfectly cornering on the edge with 5–8 enemy stones). In our 3 full games (52 total moves), zero captures fired. The R16 prompt explicitly notes that the generator now downgrades `moore → grid` when surround capture is present; this game (gen 10) predates that and exhibits the degenerate combination.

**No cellular automaton.** classic mechanics.

**Propagation (influence):** every placed stone radiates a signed scalar field via:
`value(c) += sign * strength * decay^moore_dist(c, placed_cell)` for cells within `radius`.

- `strength = 1.6836`, `decay = 0.7205`, `radius = 2`.
- Sign: P1 = `+`, P2 = `-`.
- Empirical contribution from a single stone: own-cell `1.68`, ring-1 (8 Moore neighbors) `1.21`, ring-2 (16 cells) `0.87`. So one stone contributes (in isolation) ~1.68 to its own-sum and radiates outward.

**Win condition:** `threshold` on `target_dimension=0` (own-stone influence sum). A player wins when:
`sum(board_values[c] for c in cells where owner==player) * sign  >  50.508`
(P1 sign +, P2 sign –). Max turns 100. R16 fix: simultaneous threshold-crossings now resolve by larger margin (draw if equal).

Empirically a solid 3x3 Moore cluster of 9 stones produces own-sum ≈ 57, which crosses the threshold; an 8-stone diamond can also cross. Threshold reachable in ~7–9 stones (~13–19 ply).

**Degeneracy flags:**
- **Capture rule is INERT** on Moore. Confirmed by 0 captures in 3 played games.
- Threshold reachable cleanly; not a double-pass-draw game.
- **First-mover advantage is severe** (see Phase 2/3 evidence).
- No CA, no torus, no connection — none of the R16 quick-rejects apply, but the moore+surround degeneracy is exactly the class R16's generator now suppresses.

---

## Phase 2 — Strategic Play

All moves engine-verified via `play_helper.py --action play`. Helper script: `/Users/jamesbrowne/aigame/eval_helper_team20.py`.

### Game 1 — P1 (cluster) vs P2 (disrupt-then-race)

| # | P | Move | Coord | P1sum | P2sum | Notes |
|---|---|---|---|---|---|---|
| 1 | 1 | a=27 | (3,3) | 1.68 | 0.00 | center |
| 2 | 2 | a=45 | (5,5) | 0.81 | 0.81 | far diag (avoid contamination) |
| 3 | 1 | a=18 | (2,2) | 4.92 | 0.81 | densify NW |
| 4 | 2 | a=36 | (4,4) | 2.83 | 2.83 | direct disruption |
| 5 | 1 | a=19 | (3,2) | 8.49 | 1.96 | densify |
| 6 | 2 | a=28 | (4,3) | 5.19 | 4.52 | wedge into P1 cluster |
| 7 | 1 | a=20 | (4,2) | 11.39 | 2.43 | repair, extend SE |
| 8 | 2 | a=35 | (3,4) | 7.56 | 6.88 | mirror disruption |
| 9 | 1 | a=10 | (2,1) | 16.71 | 6.00 | extend N |
| 10| 2 | a=26 | (2,3) | 11.33 | 8.22 | inside P1 cluster |
| 11| 1 | a=9  | (1,1) | 20.48 | 7.35 | extend NW corner |
| 12| 2 | a=11 | (3,1) | 13.88 | 5.93 | disruption (cost own-sum 3 to hit P1 6.6) |
| 13| 1 | a=17 | (1,2) | 23.38 | 2.97 | repair NW |
| 14| 2 | a=44 | (4,5) | 22.51 | 14.55 | switch to P2-cluster build |
| 15| 1 | a=3  | (3,0) | 34.14 | 13.34 | top edge, attacks P2 (3,1) |
| 16| 2 | a=43 | (3,5) | 33.27 | 26.67 | mass P2 cluster |
| 17| 1 | a=2  | (2,0) | 48.01 | 25.46 | near-threshold |
| 18| 2 | a=25 | (1,3) | 42.09 | 28.89 | last-ditch disrupt |
| 19| 1 | a=16 | (0,2) | **51.78** | 26.80 | **WIN by threshold** |

**Winner: P1, threshold cross at move 19.** Final P1 = 51.78, threshold 50.508.

P1 reflection: dense Moore-cluster wins. P2's disruption hurt me significantly (~5 own-sum per disruptive play) but I had enough cluster mass + tempo. Would have repaired NW earlier.

P2 reflection: move 12 (3,1) and move 18 (1,3) lost own-sum because they sat in P1's strong field. Better to commit to corner cluster early (as I did at move 14 (4,5)) — but by then I was 4 stones behind in cluster value. Captures never available.

### Game 2 — same seats, both race

Both players commit to symmetric corner clusters: P1 at NW, P2 at SE.

| # | P | Move | Coord | P1sum | P2sum |
|---|---|---|---|---|---|
| 1 | 1 | (3,3) | center | 1.68 | 0.00 |
| 2 | 2 | (6,6) | SE | 1.68 | 1.68 |
| 3 | 1 | (2,2) | | 5.79 | 1.68 |
| 4 | 2 | (5,5) | | 4.92 | 4.92 |
| 5 | 1 | (3,2) | | 11.46 | 4.92 |
| 6 | 2 | (6,5) | | 11.46 | 11.46 |
| 7 | 1 | (2,3) | | 20.42 | 11.46 |
| 8 | 2 | (5,6) | | 20.42 | 20.42 |
| 9 | 1 | (1,3) | | 30.45 | 20.42 |
| 10| 2 | (4,6) | | 30.45 | 30.45 |
| 11| 1 | (2,1) | | 42.23 | 30.45 |
| 12| 2 | (5,7) | | 42.23 | 42.91 |
| 13| 1 | (1,2) | **57.11** | 42.91 | **WIN** |

**Winner: P1, move 13 (7 stones).** Tempo decisive. P2 was even leading slightly at move 12 (42.91 vs 42.23) but P1 played first and crossed.

### Game 3 — SEAT SWAP — race symmetric

The previous P2-mindset agent now plays P1; previous P1-mindset agent plays P2.

| # | P | Move | P1sum | P2sum |
|---|---|---|---|---|
| 1 | 1 | (5,5) | 1.68 | 0 |
| 2 | 2 | (2,2) | 1.68 | 1.68 |
| 3 | 1 | (6,6) | 5.79 | 1.68 |
| 4 | 2 | (3,3) | 4.92 | 4.92 |
| 5 | 1 | (5,6) | 11.46 | 4.92 |
| 6 | 2 | (3,2) | 11.46 | 11.46 |
| 7 | 1 | (6,5) | 20.42 | 11.46 |
| 8 | 2 | (2,3) | 20.42 | 20.42 |
| 9 | 1 | (6,4) | 30.45 | 20.42 |
| 10| 2 | (1,3) | 30.45 | 30.45 |
| 11| 1 | (7,5) | 42.91 | 30.45 |
| 12| 2 | (1,2) | 42.91 | 42.91 |
| 13| 1 | (7,6) | **57.11** | 42.91 | **WIN** |

**Winner: P1, move 13.** Identical structural outcome to Game 2.

**Aggregate Phase 2: 3 games played, 3 P1 wins, 0 P2 wins, 0 draws. All wins by threshold cross. Zero captures across 52 placement moves.**

### Strategy guides

**P1 strategy guide:**
1. Place center or edge — pick a 3x3 region to grow.
2. Each new stone adjacent to the existing cluster adds 8–14 to own-sum (via overlap).
3. Ignore captures — they don't fire on Moore.
4. Threshold reachable in 7–9 stones if uncontested; 9–10 if P2 disrupts.
5. P2's disruptive plays inside your strong field hurt you ~5/move but cost P2 ~2 — accept the trade and keep building.

**P2 strategy guide:**
1. You're down 1 tempo. In a pure race, you lose by 1 stone (G2/G3).
2. Disruption only works if it reduces P1's sum by ~1.5x what it costs you. Avoid placing inside P1's strong field (cell stays positive after your placement = bad for P2).
3. Build P2 cluster from a "fresh" corner where P1 influence ≤ 0; place where you can radiate negative onto P1 cells AND get negative own-cell value.
4. Surround capture is unavailable — don't budget for it.
5. Realistic verdict: with optimal play from both sides, P1 wins. There is no robust P2 winning line.

---

## Phase 3 — Strategic Analysis (joint)

**Distinct viable strategies?** Two: (A) race-cluster, (B) disrupt-then-cluster. Race-cluster strictly dominates for P1 (tempo wins). For P2, disruption is the only counterplay, but it doesn't actually reverse the outcome — only delays.

**Counter-play?** Mechanically yes (disruption + capture), but in practice the capture rule is dead (Moore + 8 liberties) and disruption is too costly to convert.

**Short-term vs long-term tension?** Mild: placing inside opponent territory deals immediate damage but locks in a low-quality piece for the rest of the game (the cell stays positively-signed, which is bad for the placer if they're P2). We saw this in G1 m12 P2(3,1) — owned cell value +3.17, contributing -3.17 to P2's effective score for the remainder.

**Emergent concepts:**
- **Influence territory** (dominant): each player accumulates a continuous-valued field around their stones.
- **Cluster-overlap arithmetic**: a 9-stone diamond ≈ 57 own-sum; a 7-stone wedge ≈ 42; tempo of one stone is decisive.
- **Tempo/initiative**: P1's structural advantage.
- **Damage trades**: a disruptive placement sacrifices ~3 own-sum to reduce opponent ~6 — but P2 can't sustain this trade enough to overcome the tempo deficit.
- **Dead mechanics**: surround capture (Moore liberties too high). The game has 1 mechanic too many.

**Topology matter?** It matters for influence radiation pattern (Moore distance defines decay rings) and for capture-deadness. The same game on `grid` (4-neighbor) topology with the same influence rule (Chebyshev decay) would give nearly identical play except captures would actually fire. This game effectively IS a grid-influence-race with a vestigial Moore adjacency that breaks captures.

**First-mover advantage (alternating game):** **Severe.** 3/3 P1 wins; seat-swap (Game 3) confirmed P1 wins regardless of which agent occupies it. The threshold (50.508) requires 7–9 well-placed stones, and the symmetric-race game gives P1 +1 tempo per pair, which is exactly enough to cross first. **No P2 winning line was found in any game**, and analytical inspection (P2 at -1 tempo with identical cluster geometry) suggests no such line exists against optimal P1. Quantification: P1 win-rate in our team's games = 100% (3/3); training data shows trained-vs-trained final winrates 0.5/1.0/0.5/1.0 across 4 seeds (mean 0.75 favoring whichever side is exploited; high variance suggests RL convergence dependent).

---

## Phase 4 — Novelty Adversary

**Adversary's case:**

- **Go**: place + surround capture + territory. This game has the same skeleton but with: (i) Moore instead of grid (which kills captures), (ii) influence-threshold win instead of territory count, (iii) numeric threshold (50.508) instead of board-fraction. It's "Go with a thermometer instead of a scoresheet."
- **Reversi/Othello**: stones placed, no flipping here. Not a fit.
- **Hex/Y/Havannah**: connection wins. Not a fit (threshold not connection).
- **Gomoku/Pente**: line wins. Not a fit.
- **Lines of Action**: movement, not just placement. Not a fit.
- **Mancala variants**: capture by sowing. Not a fit.
- **Nim**: combinatorial subtraction. Not a fit.
- **Tumbleweed (closest analog)**: place stacks of stones at a strength proportional to lines-of-sight from your existing stacks; territory = sum of stack heights. **This game is structurally the same family**: place pieces, accumulate influence-weighted territory, race to a numeric threshold. The radial-decay influence here replaces Tumbleweed's LOS-stack model, but both produce "cluster-for-overlap" optimal play.
- **Slither / Connect6**: line/path wins. Not a fit.

**(d) Re-skin?** YES — this game is a **continuous-radial-decay variant of Tumbleweed**, with vestigial Go-capture grafted on (and dead due to topology mismatch). The strategic core (place stones to build overlapping influence regions, race to a fixed total) is identical to Tumbleweed.

**(e) Expert transfer?** A Tumbleweed player would IMMEDIATELY see the winning strategy (cluster for overlap), would correctly judge that captures don't fire, and would converge on the optimal play within 2–3 games. The capture rule and the Moore topology specifically would be cosmetic for them.

**Player rebuttal:**
- The continuous radial-decay influence has no exact analog in Tumbleweed; the math differs (Tumbleweed: integer line-of-sight; here: 1.68·0.72^d).
- The signed influence field (with +/– for owners) is genuinely a richer object than Tumbleweed's stack heights — disruption plays in our Game 1 (P2 inside P1's territory radiating negatively) have no exact Tumbleweed analog.
- BUT: these are quantitative, not qualitative differences. The decision-theoretic core ("which empty cell maximizes your own-sum minus opponent-sum?") is the same.
- The capture rule, on this topology, contributes **zero** strategic content. It's noise.

**Novelty score: 3/10.** This is "Tumbleweed with continuous decay + dead capture." Recognizable family, no genuine emergent dynamics not already present in Tumbleweed.

---

## Phase 5 — Verdict

**Team ID:** team-20
**Game ID:** 4d9c5796dd18
**Rules Summary:** Place a stone per turn on an 8x8 Moore board; each stone radiates a signed influence (radius 2, decay 0.72, strength 1.68); first player whose own-stones' total influence exceeds 50.508 wins. (Surround capture rule exists but never fires on Moore.)
**Topology:** 8x8 2D Moore (king's-moves adjacency).
**Turn Structure:** **Alternating**.

### SCORES (1–10):

- **Strategic Depth: 3** — Optimal strategy is "race-cluster". The disrupt vs. race tension is real but resolves in favor of race for both players. No deep tactical layers, no positional exchanges, no sequencing/timing puzzles. Captures are dead.
- **Emergent Complexity: 3** — Influence-overlap arithmetic produces a smooth landscape, but the decision rule reduces to a simple greedy (place where overlap with own pieces is highest). Greedy and trained agents converge to the same solution; learning curves flat or near-perfect from episode 1000.
- **Balance: 2** — **Severe P1 advantage.** 3/3 P1 wins in our games (including seat-swap). Symmetric race gives P1 a structural +1 tempo, sufficient to cross threshold first. Training data echoes this: trained-vs-trained final winrates are 0.5/1.0/0.5/1.0 across 4 seeds; trained-vs-random is 0.86–1.00 for P1.
- **Novelty (post-adversary): 3** — Recognizable Tumbleweed-family game with continuous-decay influence. The (inert) Go-capture grafting adds no novelty. Generator-detected degeneracy (moore + surround capture) is exactly what R16's downgrade rule was designed to catch.
- **Replayability: 2** — Once you discover "cluster centrally as P1, mirror as P2 and lose by 1 tempo," there's no reason to replay. No hidden strategies, no opening theory beyond "where to put the first stone."
- **Overall "Would I play this again?": 2**

**CLOSEST KNOWN-GAME ANALOG:** **Tumbleweed** — both are influence-territory-race games where clustering for overlap is optimal. Differences are quantitative (continuous radial decay vs. integer LOS stacks) and cosmetic (vestigial Go capture). Not identical, but same family.

**KILLER FLAWS:**
1. **Surround capture is dead** on Moore topology (single stones have 8 liberties; we observed 0 captures in 52 moves). The R16 generator was specifically updated to suppress this combination.
2. **Severe first-mover advantage** — P1's +1-tempo advantage in a symmetric-race game is enough to win every contest we played, including a seat swap. No P2 winning line found.
3. **Capture-rule threshold field (=2) is unused** for the `surround` capture type — the engine reads only `liberties == 0`. Dead parameter.
4. Strategic decision space collapses to greedy local-maximization once both players see the cluster-overlap pattern.

**BEST QUALITY:** The signed-influence field is a clean, smooth abstraction that produces visually understandable territory boundaries. Mid-game positions are easy to read at a glance: a player with a denser cluster is winning, and the influence-map confirms it. The game IS a clean instance of "influence territory" — it's just not a deep one.

**IMPROVEMENT IDEAS:** Replace `moore + surround` with `grid + surround`. On grid topology, a single stone has 4 liberties, and 1-stone groups can be captured by 4 surrounding enemies — making capture an ACTIVE mechanic that creates real positional tension. Combined with the existing influence-threshold win condition, this would give the disrupt-strategy genuine bite (a P2 disruption stone could be captured if P1 surrounds it, creating a tempo cost on the disrupter and rewarding tactical sequencing). Alternatively: **lower the threshold to ~30** so that 5–6 stones suffice — this would shorten the race so much that disruption tactics matter on the first few moves. Or: add a small handicap to P2 (an extra "second-move" placement on turn 2) to redress the tempo gap.
