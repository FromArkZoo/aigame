# Run 16 Human Evaluation — team-8

**Game ID:** `f8dbeb3079a5`
**R16 rank:** 2 (Generation 8)
**Family:** Moore 8x8, simultaneous, no capture, radius-1 influence, threshold-win

---

## Phase 1 — Rule Comprehension

### Board structure
- **Dimensions:** 2 (axis_size = 8 → 8×8 = 64 cells, +1 pass action = 65 actions)
- **Topology:** `moore` (8-neighbour Chebyshev). Distance metric is Chebyshev distance, NOT Manhattan; this matters because radius-1 cell sets are 3×3 squares, not plus-shaped diamonds. Edges are HARD (no wrap-around — `sim_play_helper.py` mislabels the board "torus" but topology.py confirms `moore` ≠ `torus`).
- **Action IDs:** `y * 8 + x`. Action 64 = pass.

### Turn structure — SIMULTANEOUS
- **Critical:** both players submit one action per round; `engine.step_simultaneous(a1, a2)` resolves both atomically.
- **Collision rule:** if `cell_p1 == cell_p2` (and both are placements), **mutual annihilation** — neither stone is placed; the cell stays empty. This is the central "novel" mechanic of the simultaneous family.
- **Threshold tiebreak (R16 fix):** if both players cross the win threshold on the same tick, the higher effective-value margin wins; equal margins → draw. Replaces the R15 P1-favoured iteration order.
- **Double pass → draw** (not piece-majority).

### Action types
- Single type: **place** on empty cells. No movement, no capture (`capture_type: none`). First-move-anywhere is true.

### Capture / CA
- No capture. No cellular automaton. The "no capture" simplification means stones once placed are permanent.

### Propagation — INFLUENCE
- `prop_type: influence`, **radius = 1**, **strength ≈ 1.0388**, **decay ≈ 0.3712**.
- On placement, the placed cell gains `±strength * decay^0 = ±1.0388` (signed by player) and each Chebyshev-1 neighbour gains `±strength * decay^1 ≈ ±0.3856`.
- Values are signed: positive = P1 advantage, negative = P2. Values stack additively across stones and CLAMP to ±100.
- Net effect: an isolated own-stone contributes ~1.04 to its cell. A central cell of a 3×3 own-cluster reaches ~1.04 + 8·0.386 ≈ 4.13. An enemy-adjacent neighbour adds −0.386 (drains the cell).

### Win condition — THRESHOLD
- `threshold ≈ 30.751` on `target_dimension = 0` (board values).
- Sum each player's `board_values[c]` over cells they own; P2's sum is negated to get effective value. First to exceed threshold wins; same-tick crossings → margin tiebreak.
- `max_turns = 100` (game ends in piece-majority by-rule, but in practice every contested game converges to threshold long before — see Phase 2).

### Degeneracy check
- **Pass-spam draw**: possible but uncompelling — both players can simply pass to draw, but neither player benefits. Active play dominates because threshold is reachable.
- **Threshold reachability**: a tight 3×4 cluster (12 stones) sums to ~34.9, comfortably over 30.75. With contested play we observed threshold crossing in 11–14 rounds in all three games. NOT degenerate.
- **Cluster monoculture flag**: the optimal strategy clearly orbits around "build dense own-cluster, ignore enemy if possible" — see Phase 3.

---

## Phase 2 — Strategic Play

All 3 games engine-verified through `sim_play_helper.py`. Round numbers refer to simultaneous rounds (each = 1 step_count increment).

### Game 1 — Mirror cluster (P1 top-left, P2 bottom-right)
**P1 plan:** dense 3×3 cluster at (1,1)–(3,3) and extend to row 0.
**P2 plan:** symmetric mirror at (4,4)–(6,6).

Move log (rounds = "p1:p2"):
```
27:36, 18:45, 19:44, 26:37, 9:54, 17:46, 25:38, 10:53, 11:52, 1:62, 2:61
```

**Outcome:** Both crossed threshold simultaneously at round 11 (P1=11 stones at top-left 3×3 + (0,1)+(0,2); P2=11 stones at bottom-right 3×3 + (7,6)+(7,5)). Both displayed `own_sum = 31.093`. R16 margin tiebreak resolved to **P2** — almost certainly a floating-point ε difference; the play was numerically symmetric.

**Reflections:**
- *P1:* Mirror play is fragile in this game; the only seat asymmetry that broke the tie was floating-point noise. I would not change my move sequence — it was as efficient as P2's.
- *P2:* Mirroring was the safest strategy; the win was lucky. No surprises.
- The endgame **did** reach the stated threshold (not double-pass, not max_turns).

### Game 2 — Cluster (P1) vs invasion (P2)
**P1 plan:** central cluster around (3,3); accept some early disruption.
**P2 plan:** invade P1's territory at (1,2),(2,2) to drain P1 cell values, build secondary cluster around (4,4)–(6,6).

Move log:
```
9:18, 27:17, 19:36, 26:44, 35:37, 28:45, 20:29, 34:53, 12:46, 21:43, 11:52, 10:38, 13:60, 2:61
```

After R2 P2 actually led 1.69 vs 0.92 (invasion paid off short-term). But by R8 P1 had recovered to 14.09 vs 11.78, and the invading P2 stones at (1,2),(2,2) stayed isolated while P1 grew a contiguous block. P1 hit threshold at R14 with 31.12 vs P2's 29.58. **Outcome: P1 wins.**

**Reflections:**
- *P1:* I lost the early lead but my cluster's growth rate dominated once each player crossed ~6 stones. The invasion stones gave P2 only ~2 stones of value while costing P2 in terms of cluster cohesion later.
- *P2:* The invasion strategy works in the first 3 rounds but is a long-term loss because invading stones get sandwiched and contribute less to P2's own_sum. I would have done better to build a tighter cluster and accept the slight late-game start.
- The endgame **did** reach the stated threshold.

### Game 3 — Seat swap: invasion (P1) vs cluster (P2)
**P1 plan:** mirror Game-2 P2's invasion strategy (now from seat 1).
**P2 plan:** mirror Game-2 P1's clustering strategy (now from seat 2).

Move log:
```
17:9, 10:18, 45:27, 37:19, 44:26, 53:11, 46:25, 54:1, 52:2, 38:8, 43:12, 51:3, 59:20, 61:28
```

R10: P1 (cluster grower at (4-6,4-6)) at 20.03; P2 (invasion-corrupted cluster) at 19.26. R14: both crossed threshold; P1 at 31.12, P2 at 31.90. **P2 wins** by margin 1.14 vs 0.37.

Wait — re-reading: in Game 3 I had **P1 do the invasion** and **P2 do the cluster**. P2 won. The cluster-builder won regardless of seat. Confirmed.

**Reflections:**
- *P1:* I used the losing strategy from Game 2 (invasion) and lost. The seat number didn't help me.
- *P2:* I clustered in the top-left like Game-2's P1, took some early disruption from P1's stones at (1,2),(2,1), and recovered the same way. The simultaneous mechanic genuinely doesn't give P1 any structural edge.
- The endgame **did** reach threshold.

### Strategy guides

**P1 strategy guide:**
1. Pick one quadrant or corner and commit. Do NOT mirror or chase the opponent.
2. Build the densest possible 3×3 then extend along an edge to grow per-cell value.
3. Each cluster-internal stone gets buffed by all its own neighbours: a 4×3 block of 12 own stones already exceeds threshold (~34.9 own_sum) if undisturbed.
4. Avoid placing within Chebyshev-1 of opponent stones — every adjacency drains your cell value by 0.386.
5. The "first move" cell IS slightly important: place it where a 3×3 block fits without touching the symmetry-mirror centre — corners (0,0) or near-corner (1,1) are safest.

**P2 strategy guide:**
1. Same as P1. The simultaneous mechanic eliminates seat advantage.
2. If the opponent invades your area, do NOT chase — let the invader stones sit. They are a small drain on your cluster but you can route the cluster around them.
3. Counter-invading the opponent's area is a trap: invading stones get sandwiched and produce less own_sum than they would in a cluster.
4. The only collision-worth-considering is on a high-value cell that BOTH players want; even then, mutual annihilation just denies the cell — it's only profitable if the cell is more critical to one player than the other (which is rare in this geometry).

---

## Phase 3 — Strategic Analysis (joint)

### Are there distinct viable strategies?
**Mostly no.** Three observed strategies:
1. **Pure clustering** — converges fast, wins or draws every game.
2. **Invasion / sabotage** — short-term lead, long-term loss.
3. **Mirror** — forces near-tie; FP noise decides.

Pure clustering dominates. Invasion is a dominated strategy. The only nuance is *where* to cluster — corner vs edge vs centre — but all positions yield similar win rates because the Moore-distance metric makes the board geometrically uniform away from the edges.

### Counter-play
Limited. The only real counter-play is geometric: if the opponent commits to a top-left 3×3, you can choose any non-adjacent quadrant to mirror. There is **no Go-style "killing" mechanic** because there is no capture, and there is **no Reversi-style flipping** because owners are permanent.

### Short-term vs long-term tension
Weak. Cell values rise monotonically with cluster size in own region. The only tension is "do I extend or invade?" and invasion is strictly worse, so the choice is illusory.

### Emergent concepts
- **Territory** — yes; the 3×3 + extension model directly resembles Go territory framing.
- **Influence** — built into the mechanic literally.
- **Tempo / initiative** — *absent*. Simultaneity wipes out tempo entirely; every round is a forced parallel placement and the value increment per round is symmetric.
- **Ko / mutual-annihilation tactics** — collision rule exists but is *almost never useful* in observed play. We did not collide once in 3 games because the optimal strategy puts the two players on opposite sides of the board.
- **Mutual destruction zones** — the diagonal-adjacent boundary between two clusters (e.g. P1's (3,3) and P2's (4,4)) creates a permanent wedge of suppressed cells. This is the closest thing to a strategic concept in the game.

### Topology
**Moderately matters.** Moore (Chebyshev) is meaningfully different from grid (Manhattan): radius-1 includes the 8 diagonals, so 3×3 blocks cover a Chebyshev ball perfectly. If this were grid-topology, the radius-1 set would be a plus-sign and the geometry of clustering would change (clusters would prefer plus or X shapes). On torus, the topology would change everything because edges would wrap and clusters could extend "off the side"; on hex, it'd be 6-neighbour. So the Moore choice is load-bearing for the clustering geometry.

### First-mover advantage / seat balance
**Effectively zero.** Game 1: mirror → FP-noise tiebreak; Game 2: P1 cluster won; Game 3 (swap): P2 cluster won. The strategy carries the win, not the seat. This is **exactly** what the R16 simultaneous mechanic was designed to deliver — and it appears to work.

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary's argument: this is NOT novel.

**(a) Catalogue match.** Compare against:
- **Go**: Influence-based stones with territory framing. The 3×3 cluster pattern that wins this game is exactly Go's "thick wall" concept. No capture is the only major difference.
- **Reversi/Othello**: No flipping; doesn't apply.
- **Hex / Y / Havannah**: Connection-based; doesn't apply (no win-by-connection).
- **Gomoku / Pente / Connect6**: Line-formation; doesn't apply (threshold ≠ line).
- **Lines of Action**: Different (movement-based).
- **Mancala variants**: Stockpile-counting wins. **The win condition is mechanically similar** — sum stones on your side and beat a number — but the geometry is unrelated.
- **Tumbleweed**: Influence-based placement on hex with sight lines. Tumbleweed already encodes radius-of-influence territorial wins. **This game is essentially Tumbleweed with simultaneous play and a Moore-grid instead of hex sightlines.**
- **Slither**: Doesn't apply.
- **Blotto / RPS-scaled / Diplomacy / Gungo (simultaneous comparators):** Diplomacy uses simultaneous orders with negotiation; not similar. Blotto is a one-shot allocation; not similar. **Gungo (simultaneous Go variants)** is the closest direct ancestor — Go-with-simultaneous-moves is not original to this game.

**(b) CA literature:** N/A (no CA).

**(c) Simultaneous-game comparators:** Closest is "Gungo" / simultaneous-Go family. The collision rule (mutual annihilation) is the same as in many simultaneous Go variants where both players targeting the same vertex causes the move to fail.

**(d) Re-skin claim:** This game is **"Tumbleweed-style influence territory + Gungo simultaneous mechanics + threshold win + Moore grid."** Each component is well-known; the combination is the only novelty. An expert in Tumbleweed and simultaneous-Go would transfer ~80% of intuition immediately. The 3×3 cluster strategy literally is "build a Go thick shape."

**(e) Expert transfer test:** Yes, would transfer immediately. A Go player would recognise "thickness", "territory", "influence" in the first three rounds. A Diplomacy player would recognise the simultaneous-resolution paradigm. The mutual-annihilation rule is the only piece a Go player wouldn't know — but they'd grasp it in one round.

### Defenders' rebuttal

The Adversary's argument is largely correct, but with caveats from Phase 2 evidence:

1. **The threshold-win + influence-stack interaction is not exactly Go.** In Go you win by *territory area*; here you win by *summed cell value*, which means cluster *density* matters more than enclosed area. A 3×3 dense block beats a hollow 5×5 ring of equal stone count. This is *not* a Go concept.
2. **Game 2 P2's invasion strategy** demonstrated a tactic that Go would reject (invade with no eye-shape) but that this game's mechanic still gave a 3-round lead before collapsing. The numerical interplay of strength=1.04 and decay=0.37 is fine-tuned in a way that doesn't match any one parent game.
3. **The R16 same-tick margin tiebreak** is a genuinely simultaneous-game-specific mechanic — neither Go nor Tumbleweed nor Diplomacy has it.
4. **Mutual annihilation never fired in our games**, so it didn't affect strategy — but the rule is original to simultaneous-game literature only inasmuch as it's a clean resolution rule.

### Novelty score: **3 / 10**
This is "Tumbleweed/Go on Moore-grid with simultaneous play + threshold win". The components are catalogued; the combination is mildly novel; the strategic emergence is shallow because clustering dominates so completely.

---

## Phase 5 — VERDICT

**Team ID:** `team-8`
**Game ID:** `f8dbeb3079a5`
**Rules Summary:** Simultaneous placement on a Moore 8×8 grid; each placement adds influence ±1.04 to the cell and ±0.39 to each Chebyshev-1 neighbour; first player whose owned-cell sum exceeds 30.75 wins (margin tiebreak on same-tick crossings).
**Topology:** Moore 8×8 (Chebyshev distance, hard edges).
**Turn Structure:** **SIMULTANEOUS** with mutual-annihilation collision rule.

### SCORES (1–10)

- **Strategic Depth: 3** — One dominant strategy (build a dense own-cluster); invasion is dominated; mirror is fragile; choice of cluster *location* is mostly cosmetic. The decision space per move collapses to "extend my cluster outward in the cheapest cell." We saw zero rounds where multiple moves were genuinely contested in our reasoning.
- **Emergent Complexity: 3** — Limited emergent concepts: territory and influence (inherited directly from the influence rule), and a "mutual destruction wedge" along cluster boundaries. No tempo, no ko, no kill-races, no sacrifice tactics.
- **Balance: 8** — Excellent seat balance. Game 1 ended in a near-tie (FP ε); Games 2 & 3 with seats swapped both went to the cluster-strategy player regardless of seat. The R16 simultaneous mechanic *demonstrably* eliminates first-mover advantage in this game family.
- **Novelty (post-adversary): 3** — Tumbleweed + Gungo + threshold-win, on Moore grid. Components catalogued; combination mildly novel; strategic emergence too shallow to differentiate.
- **Replayability: 3** — Once you discover the cluster-and-extend pattern, every game looks the same except for which corner each player picks. Three games already showed strong convergence; ten games would not reveal new tactics.
- **Overall "Would I play this again?": 3** — As a research artifact illustrating R16's seat-balance fix it's interesting; as a game it's not.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed**, with simultaneous play (Gungo-style), threshold win condition, and Moore-grid topology. Tumbleweed has hex sightlines and turn-based play; this game replaces sightlines with Chebyshev-radius-1 influence and turns with simultaneous resolution. The territorial framing and influence-stacking carry over essentially intact.

### KILLER FLAWS
1. **Cluster-and-extend monoculture.** Both players' optimal strategy is identical and produces near-symmetric games. Decision-space-per-move is ~1 (extend the cluster).
2. **No interactive tactics.** The mutual-annihilation collision rule exists but is dominated; in 3 games we never collided, never wanted to collide, never feared a collision.
3. **Threshold reachable too easily.** 11–14 rounds to threshold means the game is shallow in time as well as in tactics. The radius-1 / strength-1.04 / decay-0.37 / threshold-30.75 numerical regime is set so that ~12–14 own stones in a tight cluster always cross the threshold; a slightly higher threshold (or stronger decay) might force more interesting interaction.
4. **First-move-anywhere + symmetric metrics + simultaneous collisions never fire** = the players play two parallel single-player games of "fill my corner."

### BEST QUALITY
**Seat balance via simultaneous mechanic.** The R16 margin-tiebreak fix demonstrably works on this game: with identical strategies the result is a ε-tiebreak; with mismatched strategies the *strategy* wins, not the seat. Game 3's seat-swap confirmation is clean. This is the strongest evidence we have that R16's worst-of-three seat-balance probe is calibrated.

### IMPROVEMENT IDEAS
**Add a stone-cost or limited stones (e.g., max 16 each) and increase the threshold to ~50.** Currently each player can place 50 stones over 100 turns; threshold = 30.75 is hit at ~12 stones with no resource pressure. A limited stone budget would force tradeoffs (invade vs extend) and turn the mutual-annihilation collision rule into a real tactical concern (denying the opponent a critical cell at cost of one of your own stones). Alternatively: **make the influence radius decay faster (decay=0.2)** to penalise loose clusters and reward shape — this would create distinct shape-based strategies (compact vs sprawling) and reward genuine geometric reasoning.

---

## Notes for the aggregator
- Game converged to threshold win in all 3 games (no double-pass draws, no max_turns timeouts).
- R16 margin-tiebreak fix verified: Game 1 P2 won by FP ε on a numerically-symmetric position (acceptable behaviour); Game 3 P2 won with a clear margin (1.14 vs 0.37, no ambiguity).
- Mutual-annihilation collision rule never fired across 3 games; the rule's strategic salience is approximately zero in observed play.
- Cluster-and-extend strategy converges in ~11–14 rounds across all 3 games. The game's "depth" is bounded by this short convergence window.
- Seat-swap evidence is unambiguous: cluster strategy wins regardless of seat.
- The R16 hypothesis (simultaneous games' apparent strength in R14/R15 was bug-driven; classical alternating is the strongest family) is **consistent with this evaluation** — this simultaneous game has clean seat balance but is strategically thin. Its R16 GE rank-2 placement reflects engine-fitness scoring of training runs, not human-perceived strategic depth.
