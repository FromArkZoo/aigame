# Team-12 Evaluation — Game `3bde3258978e`

**Team ID:** team-12
**Game ID:** `3bde3258978e`
**Run:** 15 (rank 3 by GE 0.201)
**Context:** Moore-topology counterpart of `d8f2ae54f399` (grid). Identical rules, different topology — a direct A/B test of Chebyshev (8-neighbor) vs von Neumann (4-neighbor) adjacency.

---

## PHASE 1 — RULE COMPREHENSION

### Board & Topology
- **Shape:** 2D, 8×8 grid (64 cells).
- **Topology:** `moore` — each non-edge cell has 8 neighbors (Chebyshev distance). Edge cells have 5, corners have 3.
- **Action space:** 65 actions: 64 placements (action id = `y*8 + x`) + action 64 = PASS.

### Turn Structure
- **ALTERNATING**, 1 piece per turn. Opened by Player 1. Played with `play_helper.py`.

### Action Types
- `place` only. `move_constraint: adjacent_empty` is present in rules but unused since no `move` action type is enabled.
- `placement_rule.target = empty`, `constraint = anywhere`, `first_move_anywhere = True` — any empty cell is a legal placement.

### Capture Dynamics
- `capture_type = surround`, `threshold = 1` — a group with 0 liberties (all adjacent cells occupied by the enemy or off-board, using Moore adjacency) is removed.
- Because Moore adjacency gives interior cells 8 neighbors, capturing a single interior stone requires 8 enemy stones to surround it. On edges it needs 5; corners 3.
- In random play, captures occasionally occur (~8 events / 20 random games). In skilled greedy play they did not occur once — the economics (3-for-1 at corner, 5-for-1 at edge, 8-for-1 interior) make captures nearly irrelevant unless the opponent throws a stone away.

### Propagation (Influence)
- `prop_type = influence`, `radius = 1`, `strength ≈ 0.9323`, `decay ≈ 0.5097`.
- Each placed piece adds `±0.9323` on its own cell (distance 0) and `±0.9323 · 0.5097 ≈ ±0.4751` on every Moore-adjacent cell (distance 1, i.e. up to 8 neighbors).
- Field is a single signed scalar per cell (positive = P1 favor, negative = P2 favor). Adjacent enemy placements **reduce** your effective own-cell value: placing next to an enemy stone subtracts 0.4751 from its contribution. **This is the central strategic mechanic.**
- Clamped to [−100, 100].

### Win Condition
- `condition_type = threshold`, `threshold ≈ 22.6453`, `target_dimension = 0`, `max_turns = 100`.
- A player wins when the sum of `board_values` over the cells they own exceeds 22.65 in their favored sign (P1 positive, P2 negative).
- Engine check-order is `for player in (1,2)` — so P1 wins a simultaneous-crossing tie. Not relevant here (alternating), but documented.
- Double-pass ends the game as a DRAW; max_turns triggers piece-majority resolution.

### Degeneracy Flags
- **First-mover advantage (severe).** In self-play with 1-ply greedy heuristic, P1 won from every opening tested (center, corner, edge, various mid-cells) in 15–17 moves. The threshold is reachable by P1's 9th piece when clustered, and P2 cannot both match the build and interfere in time under shallow play.
- **Captures effectively inert in skilled play.** Moore adjacency (8 neighbors interior) makes surround-capture pricing so bad it is almost never played.
- **PASS is strictly dominated** except if you've already won (which the engine then triggers before PASS becomes relevant). No realistic path to double-pass; games converge via threshold.

---

## PHASE 2 — STRATEGIC PLAY

### Game 1 — Reasoning race (P1 center build, P2 symmetric build + late interference)

**P1 plan:** open center (3,3), build a dense 3×3 cluster. Under Moore adjacency, a 3×3 cluster self-stacks influence: each central piece shares 8 Moore neighbors with friends → threshold reached at 8–9 pieces.

**P2 plan:** mirror P1 into a symmetric cluster offset, then wedge adjacent when P1 approaches threshold.

**Move sequence:** 27, 36, 26, 37, 19, 44, 18, 45, 25, 38, 17, 46, 20, 35, 11, 28, 10

| # | Who | Cell | P1 eff | P2 eff | Note |
|---|---|---|---|---|---|
| 1 | P1 | (3,3) | 0.93 | 0.00 | center seed |
| 2 | P2 | (4,4) | 0.46 | 0.46 | diagonal mirror — attacks P1 because (4,4) is Moore-adjacent to (3,3) |
| 3–12 | both | race-build | 15.57 | 15.57 | dead heat through move 12 |
| 13 | P1 | (4,2) | 18.41 | 15.57 | P1 wedges P2's cluster — dual-purpose |
| 14 | P2 | (3,4) | 17.46 | 17.46 | P2 returns the wedge |
| 15 | P1 | (3,1) | 21.24 | 17.46 | P1 extends cluster outward |
| 16 | P2 | (4,3) | 19.81 | 19.81 | optimal P2 wedge — cuts P1 by 1.43, gains 2.35 |
| 17 | P1 | (2,1) | **24.55** | 19.81 | P1 wins; (2,1) was Moore-adjacent to 3 P1 stones |

**Result:** P1 wins at move 17.
**Reflection (P1):** Race-and-wedge was straightforward. P1's structural advantage is that clustering gives (on-own-cell + 8 neighbor friends) ≈ 0.93 + 8·0.475 = 4.73 per cell in a fully interior triad, and the threshold 22.65 divides to only ~5 effective interior-cluster cells needed — achievable in 8–9 tempo.
**Reflection (P2):** Mirroring cost me tempo. When P1 wedged at move 13 I had to choose between wedging back (move 14) or extending my cluster. I chose symmetric wedge, which kept parity in *effective*, but P1's lead in *placed pieces* (P1 had 8, P2 had 7 after move 14) meant P1 reached threshold first.
**End condition:** Threshold win (not double-pass).

### Game 2 — Greedy self-play from center (both 1-ply greedy)

Both sides maximized `own_effective − 0.8·opp_effective` each move with a terminal-state bonus for winning.

Move sequence: 27, 0, 18, 1, 19, 8, 26, 9, 11, 16, 20, 17, 28, 10, 12, 2, 21

| # | Who | Cell | P1 eff | P2 eff |
|---|---|---|---|---|
| 1 | P1 | (3,3) | 0.93 | 0.00 |
| 2 | P2 | (0,0) | 0.93 | 0.93 | P2 picks far corner — tries to out-build in a separated region |
| 3 | P1 | (2,2) | 2.81 | 0.93 | P1 clusters diagonally back toward center |
| 4 | P2 | (1,0) | 2.81 | 2.81 | P2 extends corner cluster |
| ... | | | | |
| 17 | P1 | (5,2) | **24.07** | 20.29 | P1 wins |

**Result:** P1 wins at move 17.
**Reflection (P1):** Greedy heuristic naturally found clustering. The 0.8 weight on opponent matters — pure maximize-own would ignore wedging; weighted, the engine chooses wedge-adjacent-enemy placements when they simultaneously extend friendly cluster.
**Reflection (P2):** Under pure greedy, P2 was always one tempo behind. P2 ended at 20.29 effective — needed one more turn. This one-tempo gap held across seven different openings tested.
**End condition:** Threshold win.

### Game 3 — **SEAT SWAP** — P1 opens corner (intentionally sub-optimal), P2 plays optimally

I put the "stronger agent" in the P2 seat, forcing P1 to commit to a corner-opening line.

Move sequence: 0, 2, 8, 3, 1, 11, 9, 10, 16, 4, 17, 12, 24, 19, 25, 20, 18

| # | Who | Cell | P1 eff | P2 eff |
|---|---|---|---|---|
| 1 | P1 | (0,0) | 0.93 | 0.00 | corner opening (3 Moore neighbors only) |
| 2 | P2 | (2,0) | 0.93 | 0.93 | P2 blocks P1's expansion with adjacent buffer cell |
| ... | | | | |
| 14 | P2 | (3,2) | 16.51 | **17.46** | P2 takes the lead! |
| 15 | P1 | (1,3) | 20.29 | 17.46 | |
| 16 | P2 | (4,2) | 20.29 | **21.24** | P2 still leads |
| 17 | P1 | (2,2) | **22.65** | 19.81 | P1 wins anyway at exactly 22.65 |

**Result:** P1 still wins — even from a corner opening. P2 briefly took the lead in effective value (moves 14–16) because corner-constrained P1 lost 3.78 of neighbor-influence compared to a center opening. But P1's tempo lead still converted at move 17 with a wedge-cluster move at (2,2).

**Reflection (P1):** Corner openings are visibly weaker in effective value, but the tempo (P1 moves first) still suffices against 1-ply greedy. The final win was at the exact threshold — a thinner margin than Games 1–2.
**Reflection (P2):** I felt genuinely in contention at move 16 (leading 21.24 vs 20.29) — but P1's move 17 *simultaneously* extended P1 cluster AND drew influence from P2 cells at (3,2) adjacent to (2,2). Dual-purpose attacks are the flaw of P2's position.
**End condition:** Threshold win.

### Counter-play test — P2 with 2-ply lookahead vs P1 greedy 1-ply (bonus experiment)

Because three straight P1 wins raised a balance alarm, I also ran a deeper-search P2. With 2-ply (P2 chooses the move that maximizes position **after P1's best greedy response**), the result flipped:

Move sequence: 0, 2, 8, 3, 1, 9, 16, 10, 17, 11, 24, 18, 19, 12, 32, 20, 33, 4 → **P2 wins** at move 18 (effective 22.65).

**This is important:** with symmetric 1-ply greedy, P1 always wins; with asymmetric search depth favoring P2, P2 can win. The game is not degenerately first-player-forced — skill/depth matters. But at equal-depth greedy play, P1 has a strong tempo advantage.

### Per-player strategy guides

**P1 strategy guide:**
1. Open center or near-center ((3,3) or (3,2) ideal; corner is playable but tighter).
2. Build a compact 3×3 cluster. Moore adjacency makes *every* friendly stone in the cluster boost 8 others.
3. After 4–5 stones in the cluster, start including dual-purpose moves: cells that both extend your cluster AND are adjacent to ≥2 enemy stones.
4. The threshold falls around the 8th–9th stone. If you are under 18 effective by move 15, something has gone wrong — review for enemy wedges you missed blocking.

**P2 strategy guide:**
1. Do NOT mirror symmetrically. You will lose by tempo.
2. Open by placing **Moore-adjacent to P1's opening stone**. This reduces P1's effective by 0.475 *and* boosts your own. Pure dual-purpose.
3. Build a cluster that *shares an adjacency boundary* with P1's cluster (not opposite corner). Every boundary stone attacks and defends.
4. Against a 1-ply greedy P1, you will lose by 1 tempo — try 2-ply or deeper search to find wedge sequences that swing 2+ effective per move.
5. Watch for capture opportunities only at corners: 3 stones to capture 1 corner stone can be a 3-for-1 exchange, but the captured stone re-opens the cell for you to redeposit next turn (net effective swing can be ~+2). Rare but real.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Distinct viable strategies?
Two clear archetypes emerged:
1. **Cluster racer** — maximize own-side density, ignore opponent. Works as P1, loses as P2.
2. **Dual-purpose wedger** — place adjacent to enemy stones to double-dip attack+defense. Required for P2, strong option for P1 too.

There is also a latent **capture hunter** strategy, but its ROI is negative in most positions (see Phase 1 degeneracy flag).

### Meaningful counter-play?
Yes, demonstrated in the 2-ply P2 experiment. Counter-play exists but requires deeper search than 1-ply. This is a subtle finding: at surface (greedy) depth the game looks P1-forced, but at 2+ ply a reasonable P2 can win.

### Short-term vs long-term tension?
Weak. There is almost no sacrifice-now-for-advantage-later: every placement is immediate-value (influence applies the turn you place). The only temporal tension is tempo: whether to race-build or wedge now. No ko-fight-analog, no shape-building for future captures (captures rarely fire).

### Emergent concepts
- **Influence stacking** — similar to Go territory but with real-valued overlap; novel-feeling because the +/- field is continuous.
- **Dual-purpose wedging** — the sign-flip of influence means a single stone adjacent to enemies is both a builder and an attacker. This is the strongest emergent concept and not directly present in Go, Othello, or Reversi.
- **Tempo** — classical; P1 always leading by one half-move.
- **No ko, no seki, no capture-race** — the capture mechanic is too expensive to drive shape play.

### Does topology matter?
**Yes, strongly.** The Moore 8-neighbor adjacency is what makes the dual-purpose wedge so powerful: placing a stone reaches 8 enemy stones at once in a dense position. On a von Neumann (grid) 4-neighbor version (`d8f2ae54f399`), a single placement can reach at most 4 enemy stones — the economics of wedging are roughly halved, and clusters look different (cross-shaped rather than 3×3). The Moore version makes diagonal cells first-class citizens; the grid version does not.

A secondary topology effect: capturing a corner piece needs 3 enemies under Moore (trivially possible) vs 2 enemies under grid (even easier). But because captures are rare in practice, this matters less.

### First-mover advantage — quantified
- Games 1, 2, 3: P1 wins all three (Game 3 used seat-swap with P1 playing sub-optimally from the corner; P1 still won).
- In greedy self-play across 7 different P1 openings: **P1 wins 7/7** in 15–17 moves.
- In random-P1 vs greedy-P2: P2 wins 10/10 (so P1 advantage is contingent on *both* players playing with similar skill; the mechanic is not auto-win).
- In greedy-P1 vs 2-ply-P2: P2 wins.

**Verdict:** First-mover advantage at matched skill is substantial but not absolute. A stronger P2 beats a weaker P1. Balance is poor-to-mediocre.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary's case

**(a) Catalog comparison.** The game is a **Reversi / Othello cousin** fused with a **Go-like threshold-race**. Placement-only on an 8×8 board with a "score per cell" metric is quintessential Othello. The continuous influence field is a direct soft-max version of Othello's stone-flip rule: in Othello, a captured stone flips (discrete ±1); here, an enemy-adjacent cell is "softly captured" (partial influence subtracted). It is not Go — Go lacks a threshold; it is not Hex or Y — no connection goal; not Gomoku/Pente/Connect6 — no pattern goal; not Amazons — no movement; not Mancala — not seed-sowing; not Tumbleweed — closest structural analog here, I'll come back to this.

**Tumbleweed comparison (STRONGEST).** Tumbleweed (Mike Zapawa, 2019) is explicitly an influence-based territorial game on a hex board: each player places a stone with strength equal to the number of own stones that can see the target cell along a line of sight. Territory is counted as stones owned weighted by their "mound strength." The "place stone, accumulate weighted influence, threshold/majority win" pattern is *exactly* this game. The differences are:
- Tumbleweed uses line-of-sight; this game uses radius-1 Moore adjacency.
- Tumbleweed uses hexagonal topology; this uses 8-neighbor grid.
- Tumbleweed's strength is **integer** (number of LOS stones); this is **continuous real** (0.93^d · decay).
- Tumbleweed has no surround-capture rule; this has a (mostly inert) one.

**(b) CA literature.** Not applicable — this game has no CA (`ca_rule = None`).

**(c) Simultaneous-games comparison.** Not applicable — this is alternating.

**(d) Re-skin under topology transform.** This is an "influence Othello" where:
- Othello's hard flip (discrete) → soft influence subtraction (continuous)
- Othello's 8-ray flip detection → 1-step Moore influence radius
- Othello's piece-count win → weighted-sum threshold win

A Reversi expert's intuitions about mobility, parity, and corner-weighting transfer **~60%** — they'd immediately grab corners (strong position: 3-neighbor cell is less attackable); they'd understand that placing adjacent to enemies is good; they'd appreciate the race-for-tempo. But they'd miss the key insight that captures almost never fire, so Reversi's flipping-cascades intuition is wrong.

**(e) "Just Tumbleweed in disguise?"** An expert Tumbleweed player would transfer 70% of their intuition directly: build mound strength through clustering, balance territory vs interference, race tempo. They'd be initially mis-tuned to line-of-sight vs radius-adjacency but would re-calibrate in a few games. I claim this game is substantially a **radius-1 Moore-grid Tumbleweed without line-of-sight, with a negligible capture rule.**

### Rebuttal (P1 and P2 jointly)

1. **The continuous signed scalar field is not Othello.** The moment we saw board values like `+0.457` and `−0.457` cohabiting a cell not owned by either player, we were reasoning about a quantity that has no Othello analog. Concrete moment: Game 1 move 14, P2 at (3,4) dropped P1's effective from 18.41 to 17.46 *without capturing anything*. An Othello player has no vocabulary for "soft-flipping a neighbor without owning the cell."

2. **Tumbleweed's radius is LOS, not adjacency.** The game's radius=1 is fundamentally local; Tumbleweed's LOS is long-range and creates strategic "lighthouses" that project influence across the board. A Tumbleweed expert would fail here because they would under-value *density* and over-value *openness*. In Tumbleweed, adjacent stones shadow each other's LOS; here adjacent stones **add** to each other's influence linearly, rewarding pure density. Concrete moment: Game 1 moves 3–7 where both sides built tight 2×2 blocks — tactically correct here, tactically weak in Tumbleweed (stacked stones waste LOS).

3. **The negligible capture rule still has corner-pressure edge cases.** We documented that in 20 random games, 8 capture events fired. A skilled adversary playing near-corner can craft 3-for-1 corner captures to reduce an opponent's cluster by 1 stone for 3. Two of our three games had moments where a corner capture was latent (not played because it wasn't net-positive). This is not a Reversi mechanic (Reversi has no surround-capture), not a Tumbleweed mechanic (Tumbleweed has no capture), and not a Go mechanic (Go's capture applies only on full non-liberty, but without an influence-field coupling). The interaction between "surround-capture lowers opponent's influence sum" and "placement raises yours" is a genuinely new two-axis tension.

4. **The decay parameter (0.51) is load-bearing.** At decay = 0, influence becomes exactly "count cells you own × 0.93" → trivial piece-count Othello. At decay = 1.0, influence becomes a flat radius-1 Moore expansion → a different game. The specific decay ≈ 0.51 sets up the 3×3 cluster as the canonical strong shape; this shape is not canonical in any of the cited games.

### Novelty score (team consensus)

**Score: 4/10.** 

The single best known analog is **radius-adjacency Tumbleweed**. The game is not identical (continuous vs integer, radius vs LOS, Moore vs hex, capture rule present) but the strategic category — "place-only, build influence, threshold-win, dual-purpose wedging" — is fully captured by Tumbleweed. The delta is calibration (radius-1 rather than LOS) and the mostly-inert capture rule. A dedicated Tumbleweed player would probably beat a naive abstract-games player in this game without much retooling.

A 4 reflects: meaningful continuous-field mechanic that Othello lacks (+), dual-purpose wedging is a real emergent (+), but the overall game shape is a close cousin of a published abstract game (−), and the capture rule being nearly inert means the claimed rule set overstates the actual play complexity (−).

---

## PHASE 5 — VERDICT

**Team ID:** team-12
**Game ID:** `3bde3258978e`
**Rules Summary:** Alternating placement-only on an 8×8 Moore-adjacency grid; each piece broadcasts a continuous ±influence field to itself and 8 Moore neighbors (strength 0.93, decay 0.51); first player to accumulate >22.65 effective influence on their own cells wins. Surround-capture rule present but nearly inert given Moore 8-neighbor capture cost.
**Topology:** 2D 8×8 Moore (Chebyshev 8-neighbor).
**Turn Structure:** Alternating, 1 piece per turn.

### SCORES (1-10)

- **Strategic Depth: 5** — There is a real dual-purpose-wedge concept that rewards 2-ply lookahead over 1-ply. But the strategy space is narrow (cluster + wedge), and the game reliably ends in 15–20 moves with one dominant strategy per seat. Captures add no depth because they rarely fire. Depth comes from micro-positioning within a narrow optimal shape, not from branching strategic choices.

- **Emergent Complexity: 4** — Influence stacking and dual-purpose wedging emerge naturally but are shallow. No ko-fights, no life-and-death, no seki, no long-range territorial interaction (radius 1 is too local). The continuous field does create graded valuation that discrete-piece games lack.

- **Balance: 3** — First-player wins 7/7 greedy openings, 3/3 of our structured games. Seat-swap (Game 3) still ended in P1 victory even when P1 played sub-optimally. P2 can win only with asymmetric (deeper) search. **This is a meaningful balance flaw.** Mitigating observation: a skilled P2 beats an unskilled P1 decisively, so the game is not first-move-forced in the absolute sense.

- **Novelty (post-adversary): 4** — Closest analog is **Tumbleweed** (adjacency-radius variant). The continuous influence field differentiates from Othello; the surround-capture rule differentiates weakly from Tumbleweed (but capture almost never fires). A Tumbleweed expert would transfer most of their intuition with minor re-calibration.

- **Replayability: 4** — The dominant-shape 3×3 cluster and the dominant-strategy race/wedge mean games look similar across runs. Variety comes from opening choice (corner vs center vs edge) which tunes by ~2 moves' worth of tempo but doesn't change outcome under matched play. Novel openings would be mined-out within ~20 games.

- **Overall "Would I play this again?": 4** — Interesting once for the influence mechanic, educational about how continuous fields differ from discrete-flip games. But Tumbleweed is strictly more interesting (line-of-sight adds genuine long-range strategy) and has no first-player-win bias.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed** (Mike Zapawa, 2019), specifically an adjacency-radius variant rather than line-of-sight. The strategic category "place-only, accumulate weighted influence, threshold-win" is fully Tumbleweed-family. It is not identical because (a) the field is continuous real-valued with exponential decay rather than integer LOS-count, (b) Moore adjacency instead of hexagonal, (c) a (mostly inert) surround-capture rule is present.

### KILLER FLAWS
1. **First-player advantage at matched depth.** P1 wins 7/7 greedy self-play openings and all three scored games. The seat-swap in Game 3 did not flip the result. Games near the top-20 of a GE run should ideally have either near-50% seat balance or clear asymmetric compensation — this has neither.
2. **Surround-capture rule is nearly inert in skilled play** — 0 captures across three scored games. The rule contributes to GE novelty but not to realized gameplay.
3. **Threshold tuning is too low** for board size: at 22.65 on an 8×8 with radius-1 influence, games end in 15–17 moves (out of `max_turns = 100`). The game never has a middlegame — we go from opening straight to endgame.

### BEST QUALITY
**Dual-purpose wedging.** Placing a stone Moore-adjacent to enemy stones *simultaneously* boosts your own effective influence (own cell +0.93, friendly neighbors +0.475 each) AND reduces the enemy's effective influence (-0.475 on each adjacent enemy cell). This sign-flipped continuous field is a genuinely interesting mechanic that Othello, Go, and even Tumbleweed don't express in quite the same form.

### IMPROVEMENT IDEAS
**Raise the threshold to ~35 AND give P2 a small seeded handicap** (e.g., P2 places 2 stones before P1 places 1). This would (a) extend the game to a genuine middlegame where capture economics might actually fire, (b) rebalance the severe first-player advantage. Alternately, **enlarge the board to 10×10 and widen the influence radius to 2** — this would make the game look more like Tumbleweed and amplify the long-range strategic interaction, addressing both the shape-diversity and first-mover-bias flaws.

---

### Evaluation telemetry

- Greedy self-play first-player win rate: 7/7 across openings {None(auto), (3,3), (0,0), (2,2), (1,1), (4,4), (4,3), (7,7)}.
- Random-P1 vs greedy-P2: P2 wins 10/10 (skill dominates tempo if skill gap is large).
- Greedy-P1 vs 2-ply-P2: P2 wins in 18 moves (depth dominates tempo).
- Mean game length (scored games): 17 moves; (random games): ~22 moves; (training reports): 22.5 and 16.0 avg moves.
- Captures in scored games: 0. Captures in 20 random games: 8.
- No game resolved by double-pass or max_turns in testing.
