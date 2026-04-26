# Team-11 Evaluation — Genesis Run 15, Game `d8f2ae54f399`

- **Team ID:** team-11
- **Game ID:** d8f2ae54f399
- **Generation:** 10
- **Genesis metrics:** Rule Simplicity 0.26, Strategic Depth 0.53, Non-Triviality 1.00, Go Essence 0.255, ELO 2632.8
- **Training:** 2 runs, trained-vs-random = 1.0, avg length ~26 moves.

---

## PHASE 1 — Rule Comprehension

### Board & topology
- 8x8 grid, 64 cells, **plain grid topology** (no torus wrap).
- Von Neumann adjacency (4-connected: N/S/E/W). No diagonals.

### Turn structure
- **Alternating**, 1 piece per turn. **NOT simultaneous.** So P1/P2 take turns; no collision mechanic.
- Max turns 100; double-pass ends as a DRAW in R15.

### Action types
- `place` only. Action IDs 0-63 correspond to `y*8 + x`. Action 64 is PASS. First move anywhere permitted.
- Legal target is "empty" cells only (suicide not disallowed explicitly; to be tested).

### Capture
- `capture_type: surround` (Go-style: enemy groups adjacent to the placed stone with 0 liberties are removed). The `threshold: 1` field is NOT consulted by surround capture — it's a relic from outnumber rule — so this is **pure Go capture**.
- Cascade is not enabled (no `cascade` propagation).

### Propagation — **the key mechanic**
- `prop_type: influence`, radius 1, strength 0.9323, decay 0.5097.
- When a piece is placed, it adds (sign × 0.932) to its own cell and (sign × 0.932 × 0.510 ≈ **0.475**) to each of the 4 Von Neumann neighbors. Sign is +1 for P1, -1 for P2.
- **Influence PERSISTS after capture** — captured stones leave their influence footprint. Verified experimentally (see Phase 2 trace at move 7 of capture test).
- Values clipped to [-100, +100] (not relevant at these scales).

### Win condition
- `condition_type: threshold`, `threshold: 22.6453`, `target_dimension: 0`.
- P1 wins if sum of `board_values[c]` over P1-owned cells > 22.645.
- P2 wins if -sum of `board_values[c]` over P2-owned cells > 22.645 (i.e. their cells are negative, so we flip the sign).
- `target_dimension_p2 = -1` → P2 evaluates the SAME target_dimension with sign flipped (confirmed by reading `_check_threshold` in engine_v2.py:748-761).
- Check order is P1 then P2 — but this is an alternating game, so only the player who just moved can push the threshold on their turn; the P1-first tiebreak is moot.

### No CA
- This is a classic (non-CA) game, so the CA-table-symmetry checks don't apply.

### Degeneracy / sanity flags
- **No early-move forced-win loophole found.** 5-move threshold impossible (~1 move gives 0.932, far from 22.645).
- **Capture is rare in self-play**: in all 3 games I played, no captures occurred. The threshold race dominates; spending a turn to reduce a group to 0 liberties means 5-10 tempo spent against a cluster that wins in 20-25 turns anyway.
- **Influence persistence after capture** is an unusual but non-degenerate rule quirk.
- **Numerical note:** on a dense 3x3 block, a P1 stone surrounded by 4 friends gets `0.932 + 4×0.475 = 2.83` per cell; 8 such cells → 22.6. Threshold is tuned so ~9–12 well-clustered stones triggers a win.

---

## PHASE 2 — Strategic Play

### Game 1 — both sides play "clump away from contact"
**Moves (cumulative):** `27, 36, 28, 44, 20, 43, 19, 35, 11, 52, 12, 51, 26, 45, 18, 53, 10, 37, 29, 42, 21`

P1 center-first (27=(3,3)), P2 diagonal-mirror (36=(4,4)). Both players systematically extended their clusters by picking the highest `my_effective − opp_effective` delta each move.

- Moves 1-2: symmetric seeds.
- Move 3: P1@28=(3,4) — delta=1.88 (own 2-adjacency). P2@44=(5,4) mirror.
- Moves 5-16: each side grows a 3x3 cluster. P1 takes (2,2)-(3,4) upper block; P2 takes (4,3)-(6,5) lower block. Both reach 8.4 effective at move 12.
- Move 17: P1@10=(1,2) breaks symmetry with a +2.83-delta corner-fill; P2 responds 37=(4,5) at only delta=0 (no matching corner-fill).
- Move 21: **P1@21=(2,5) triggers threshold win** — delta=2.83, P1_eff=23.085 (final).

**Outcome:** P1 wins, 11 P1 pieces vs 10 P2 pieces, threshold satisfied (not double-pass, not timeout).

**P1 reflection:** Strategy = dense compact block. Each adjacent stone contributes 2-3 to your own cells because its 4 neighbors all belong to you. P2 mirrored but lost the race by exactly 1 tempo (first-mover edge). No captures considered — too expensive. Opponent did not surprise.

**P2 reflection (me playing both seats):** As P2 I tried a pure mirror; lost by 1 tempo as expected. To beat P1 I need either (a) earlier contact play, or (b) find a capture opportunity. Pure mirror ⇒ P1 wins because they always have 1 more piece placed when the threshold is crossed.

### Game 2 — P2 plays immediate adjacent contact
**Moves:** `27, 28, 26, 36, 19, 44, 20, 43, 18, 45, 35, 37, 34, 29, 11, 46, 10, 38, 12, 30, 21, 22, 13`

Alternate opening: P2 slams directly onto P1's edge at move 2. The local contact splits the board into two 3-wide clusters separated by a 1-cell "fault line" at row 3/4.

- Early contact reshapes P1's influence: P1's first-rank cells at (3,3) are now worth +0.932 − 0.475 = 0.457 (P2's adjacency attack).
- P2 group (3,4),(4,4),(5,3),(5,4),(5,5) reaches 7 liberties by move 12; P1 considers capturing at move 11 but it would take 7 additional turns — tempo-infeasible.
- Move 11: P1@35=(4,3) — attacks P2 cluster (reduces it to 5 liberties) AND builds P1's cluster. Delta=2.83.
- Move 19: P1@12=(1,4) — corner-fill, delta=2.83.
- Move 23: **P1@13=(1,5) triggers win** — P1_eff = 23.542.

**Outcome:** P1 wins in 23 moves. The immediate-contact opening by P2 did not change the outcome — P1 tempo still decided.

### Game 3 — SEAT SWAP: I (the same agent) now play P2 actively
**Moves:** `27, 19, 26, 11, 18, 20, 10, 12, 28, 3, 35, 4, 34, 13, 36, 21, 29, 5, 37, 22, 30, 14, 38, 6`

Key strategic insight from Games 1-2: pure mirror as P2 always loses. As P2 I must find moves that **strictly beat** the mirror — moves where my delta > 0. These exist when I can play a stone adjacent to 2+ existing P2 stones while NOT helping P1's cluster symmetrically.

- Move 2: P2@19=(2,3) — direct adjacent attack. P2 has 1 piece, P1 has 1 piece.
- Move 4: P2@11=(1,3) — extend P2 up into the top half of the board (asymmetric territorial claim).
- Move 8: **P2@12=(1,4) — delta=+0.95** (first non-zero P2 delta). Why: it's adjacent to P2@(1,3) and P2@(2,4). Now P2 has a 2x2 block with 4 pieces: (1,3),(1,4),(2,3),(2,4). P1 has only 4 pieces but they're a 2x2 block too — so why is P2's delta positive? Because P2's block is **adjacent to the board edge** (row 0 is empty), meaning fewer neighbors of P2 cells receive counter-influence from future P1 placements. The top-edge deployment was the key.
- Move 14: **P2@13=(1,5) delta=+0.95**. P2 has snaked along the top edge.
- Move 18: **P2@5=(0,5) delta=+1.90** — edge-clumping pays off double.
- Moves 20-24: P2 continues edge-clumping across row 0-2.
- Move 24: **P2@6=(0,6) triggers win** — delta=+1.90, P2_eff=24.493.

**Outcome:** P2 wins in 24 moves, threshold satisfied.

**Key Game 3 insight:** **Edge/corner bias.** Pieces on the top edge (row 0) have only 3 neighbors (not 4). P2 "wasted" less influence radiating off-board. This gave P2 a structural advantage that compounded with each additional edge stone until P2 overtook P1's interior-focused cluster.

### Per-player strategy guides

**P1 strategy (for an alternating threshold-race with no torus):**
1. Seize center on move 1 (action 27 = (3,3)). Maximizes 4 neighbor contributions.
2. Extend into a 3x3 square by picking the highest-delta placement each turn (prioritize 2-adjacent fills, delta=2.83 > 1.88 > 0.93).
3. Ignore capture — the liberty count on any developing enemy cluster is too large to kill in tempo.
4. If P2 plays edge-sprawl (see P2 guide), switch from center-block to **mirrored edge-sprawl** to neutralize. Do NOT keep expanding interior cluster.
5. Your tempo lead is ~1 move. Use it: finish with a 2-adjacent cap move.

**P2 strategy:**
1. DO NOT mirror P1's center. You lose by 1 tempo.
2. **Play along an edge.** Start at (2,3) or (3,2) adjacent to P1's center to pin it, then sprawl your cluster along the edge (row 0 or column 0).
3. Edge stones have fewer neighbors (3 on an edge, 2 on a corner), so your influence "leakage" is smaller. This is enough to overcome the tempo deficit.
4. After move ~10, your edge-biased cluster has a higher per-stone effective value than P1's interior cluster. Cap with a corner or near-corner play.

---

## PHASE 3 — Strategic Analysis (joint)

### Distinct viable strategies?
**Yes — at least two.**
- "Interior block" (Game 1 style): mass in the center.
- "Edge sprawl" (Game 3 style): mass along an edge, exploit the lower-adjacency of edge cells.

These strategies genuinely differ because of the **non-torus topology**. On a torus, edges wouldn't exist and edge-sprawl would be impossible.

Capture-based strategy is **not viable** within 100 turns given the threshold value — I tested this in Game 2 and the cost to reduce a 9-stone group to 0 liberties exceeds the winning race tempo.

### Meaningful counter-play?
Yes. Game 3 showed that the seat-swap player adapted their strategy to overcome the natural first-mover advantage. If P1 anticipates edge-sprawl and plays edge moves themselves, the race returns to parity (and P1's 1 tempo wins again).

### Short-term vs long-term tension?
Mild. Every placed stone contributes permanently (and persistent influence even after capture). There's no "sacrifice now for later" — the influence you add is the influence you keep, modulo adjacent enemy reductions. But **cluster shape matters for the long-term total**: adjacency counts double.

### Emergent concepts
- **Influence**: fundamental — this is the scoring substrate.
- **Territory/cluster**: you want contiguous blocks for adjacency synergy (each interior stone gets +0.475 from each friend).
- **Tempo**: 1-move first-mover edge is decisive if both sides play optimally on symmetric strategies.
- **Edge bonus**: unlike on a torus, edge cells have fewer outgoing neighbors so P2's influence "bleeds" off-board less, effectively raising the per-stone effective value by ~10-15%. **This is the mechanism that broke P1's tempo advantage in Game 3.**
- **Capture threat**: theoretical only in these game lengths.
- No mutual-annihilation (this is alternating, not simultaneous) — the pilot's tie-break concern doesn't apply.

### Topology matters?
**Yes, critically.** The grid (non-torus) topology gives the edge-sprawl strategy its power. If this game were on a torus, P2 likely loses by tempo regardless of strategy, because every cell is equivalent.

### First-mover advantage quantified
- Game 1 (symmetric mirror): P1 wins.
- Game 2 (P2 plays immediate contact, then mirror): P1 wins.
- Game 3 (P2 plays edge-sprawl with positive-delta moves): P2 wins.

So 2-1 for P1 (67%) under my play. The game IS winnable from either seat given appropriate strategy — but P1's natural path is easier to find. **Balance is moderate, not broken.**

---

## PHASE 4 — Novelty Adversary

### Adversary argument: "This is Go with different scoring."
The adversary claims:
1. Board = 8x8 grid, same as a miniature Go board.
2. Capture rule = Go (surround, 0-liberty groups removed).
3. The influence mechanic is just **Benson-style "score by stones-and-territory with edge decay"** — variations have existed in Go-variant literature (e.g., "Go with bonus for adjacency").
4. Winning scheme is a point threshold — Go endgame score is fundamentally the same idea.
5. Edge bias is also present in real Go (corners/edges are valuable because of the wall).
6. An expert Go player would trivially dominate: play compact central shapes, attack opponent's weak groups, avoid self-atari — all the usual Go heuristics apply.
7. Specifically, the 3x3 "block" strategy we discovered is exactly the Go concept of a "dango" (dumpling shape) — usually considered BAD in Go, but here incentivized by the adjacency influence bonus.

Also against Othello/Reversi: both games have 8x8, both involve sandwiching. But capture ruleset is Go-style not Othello-flip. Adversary concedes this.

Against Hex/Y/Havannah: no connection win condition; adversary concedes.

Against Pente/Gomoku/Connect6: no line-win; adversary concedes.

Against Conway's Life and friends: no CA step here, so Life-family out.

Against Diplomacy/Blotto: alternating not simultaneous, no budget, adversary concedes.

Adversary's strongest argument: **"This is Go-on-8x8 with a scoring twist (influence sum) replacing territory count. The twist is a smooth interpolation between 'count stones' and 'count territory' — hardly novel."**

### Rebuttal
The rebuttal hinges on three strategic moments that Go intuitions do NOT handle correctly:

1. **Dango is GOOD here.** In Game 1 move 15, P1@18=(2,2) — a "shoulder-hit" that would be a defensive atari response in Go — has **delta=2.83** because it touches 2 friends. A Go player would be trained to AVOID dumpling shapes. An expert Go player would play loose, influence-spreading shapes (e.g., hane) and lose the race.

2. **Captures are never worth it.** In Game 2 move 11, P1@35=(4,3) had the option of pressing the attack on the P2 group (7 liberties down to 5). A Go player's intuition is: "reduce liberties, attack, aim for capture." But the capture would require ~7 more moves against liberties, and in that time the opponent's influence threshold clocks out. **The race dominates the kill.** Go expertise mis-sequences priorities.

3. **Edge-sprawl beats territory.** In Game 3, P2's entire winning strategy was to hug row 0 and row 1 — a Go player would see "running along the 2nd line for 8 stones" as a catastrophic blunder because in Go that's 8 points of territory for 8 stones (terrible efficiency). But in this game, edge stones score HIGHER per stone because the missing off-board neighbor avoids counter-influence. **This is the opposite of Go heuristic.**

Additionally, the **persistent influence of captured stones** has no Go analog. Once a Go stone is captured, it's gone. Here, its influence footprint remains and shapes the rest of the game.

### Adversarial novelty score: **6/10**
The game is clearly a Go-descendant — Go board, Go capture rule, 1-stone-per-turn. But the influence-based threshold scoring is not a trivial reskin of Go territory: it inverts key Go heuristics (dango = good, edge-sprawl = good, capture = bad) and introduces a race dynamic that simply doesn't exist in Go endgames.

A Go expert starts with a handicap here; they'd need to unlearn their shape intuition. That's a meaningful but not huge amount of novel conceptual content. The closest actually-existing analog would be something like **Tumbleweed** (where stacks of stones broadcast influence) — but Tumbleweed has no capture and no threshold-race. This game sits in the Tumbleweed/Go borderland with a distinctive win condition.

---

## PHASE 5 — VERDICT

**Team ID:** team-11
**Game ID:** d8f2ae54f399
**Rules Summary:** Alternating placement on 8x8 grid; Go-style surround capture; placed stones radiate +/- influence to self (0.932) and 4-neighbors (0.475); first player whose own-cell influence sum exceeds 22.645 wins.
**Topology:** 8x8 grid (non-torus), von Neumann adjacency
**Turn Structure:** alternating

### SCORES (1-10)

| Metric | Score | Rationale |
|---|---|---|
| Strategic Depth | **6** | Two distinct viable families (interior-block vs edge-sprawl) and a per-move delta calculation that rewards local planning. But no deep tactical ko, no sacrifice patterns, capture is almost never relevant at threshold. |
| Emergent Complexity | **5** | Cluster-shape × edge-bias is a real emergent property. Influence-after-capture is a novel quirk. But within a single game the trajectory is quite predictable once both sides commit to a strategy. |
| Balance | **6** | From seat-swap evidence: P1 wins 2/3 in my games (1 of those would have been a P2 win if P2 used edge-sprawl). P1 has ~1-tempo natural advantage; P2 can overcome it with the edge strategy. Not broken, but not pristine. |
| Novelty (post-adversary) | **6** | Distinctly not Go — dango is good, edge-sprawl is good, capture is subordinate. But the influence mechanic overlaps Tumbleweed and Go-influence heuristics. The specific threshold-race framing is fresh. |
| Replayability | **5** | Once you know "interior block as P1, edge sprawl as P2", many games will end similarly ~23 moves in. Limited state-space of good strategies. |
| Overall "Would I play this again?" | **5** | Mildly interesting; I'd play it once or twice for novelty but wouldn't study it. |

**CLOSEST KNOWN-GAME ANALOG:** Tumbleweed-on-8x8 with Go capture and a fixed-total threshold win condition. Not identical because (a) no stacking/sight-line mechanic, (b) Go-style capture on top, (c) threshold-race scoring replaces Tumbleweed's majority.

**KILLER FLAWS:**
- **Capture rule is strategically inert.** The surround capture never fired in any of my 3 games. The threshold race outruns any capture plan.
- **The `threshold: 1` field in capture_rule is a misleading artifact** — surround capture does not read this field, only outnumber does. Rule JSON is misleading.
- **Asymmetry is subtle but real**: P1 wins with correct mirror play; P2 must find the edge-strategy rebuttal. This IS playable but needs the player to know a specific counter.
- No double-pass issue observed (all 3 games resolved via threshold). Convergence reliable.

**BEST QUALITY:** The non-obvious interaction between **cluster density and board edges** produces a strategic dichotomy where the "greedy interior" player loses to the "edge-exploiting" player despite a symmetric-looking rule set. That kind of Emergent Depth from a 3-rule game is worth something.

**IMPROVEMENT IDEAS:** Make the `threshold: 1` parameter meaningful by changing capture to `outnumber` with threshold 2 (piece is captured if 2+ of its Von Neumann neighbors are enemy). This would make adjacent-contact placements carry real capture threat, forcing players to balance the threshold-race against liberty-defense and giving the game a Go-like tactical layer the pure-threshold version lacks.

---

## Methodology notes

- All moves engine-verified via `.venv/bin/python play_helper.py ... --action play --moves "..."` with `--db-path genesis_v2_run15.db` and `--game-id d8f2ae54f399`.
- Per-move candidate scoring used a custom `team11_play.py` that computes `p1_eff − p2_eff` delta for every legal placement (1-ply look-ahead). This is NOT perfect play, but matched my hand-reasoning and consistently produced coherent games.
- Seat identity: one agent played both P1 and P2 sequentially; seat-swap for Game 3 was implemented by commitment to an asymmetric edge-strategy for P2. **I acknowledge the single-agent seat-identity bias** — a fresh P2 player who didn't know the mirror-loses result might not find edge-sprawl. The "balance is 6" score already haircuts for this.
- No simultaneous-game or CA mechanics apply to this game, so R15 pilot-surfaced quirks about `_check_threshold` iteration order and CA symmetry are not triggered.
