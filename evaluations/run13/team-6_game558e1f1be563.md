# Evaluation — Run 13 — team-6

**Game ID:** 558e1f1be563
**Rank:** 2 (GE 0.486, ELO 1003.4)
**Run 13 DB:** `genesis_v2_run13.db`
**Class:** Classic (no CA), 2D hex, threshold win

---

## PHASE 1 — RULE COMPREHENSION

### Board / Topology
- 2D 8×8 hex board (64 cells, 6-connectivity using offset-coordinate "pointy-top" layout).
- State dim 131; 65 actions (64 cells + 1 PASS).

### Turn Structure
- Alternating turns, 1 piece per turn.
- Game ends at `max_game_steps = 100` if no one hits threshold.

### Actions & Placement
- **Place only** (no movement). `action_rule.action_types = ["place"]`.
- Target = empty cell.
- Constraint = `adjacent_to_any` — from move 2 onward, placement must be hex-adjacent to any existing stone (own or enemy). First move is anywhere.

### Capture
- **None.** `capture_type = "none"`. Once placed, a stone never changes color or is removed.

### Propagation — INFLUENCE
- `prop_type = "influence"`, radius 1, strength **1.4192**, decay **0.4560**.
- On every placement, cells within **Manhattan distance 1** of the placed cell receive a delta:
  - dist 0: ±1.4192 (the placed cell itself)
  - dist 1: ±0.6472 (the 4 orthogonal neighbors)
  - sign = +1 for P1, −1 for P2
- **Critical mismatch:** adjacency-for-placement uses hex 6-connectivity; influence uses Manhattan distance on (x,y). The two "hex diagonals" of a cell (odd-row NE/SE or even-row NW/SW) are hex-neighbors but Manhattan-distance 2 → *no influence exchange* even though placement is legal. This is the game's single novel strategic gadget.

### Win Condition — THRESHOLD
- `condition_type = "threshold"`, threshold **39.66**, target_dimension = 0 (unused for threshold — the win rule sums all board_values on your own cells).
- P1 wins if sum of `board_values` on cells P1 owns > 39.66.
- P2 wins if the negative of that sum on P2's own cells > 39.66.
- Double-pass → majority by piece count.

### Degenerate / Flag Check
- Threshold ≈ 39.66 is reachable: each own stone self-contributes +1.42 baseline and can collect up to +2.59 extra from neighboring own stones (4 Manhattan neighbors × 0.647). Tight cluster of 14-16 own stones hits threshold.
- Training avg game length 31.5 moves → ≈15-16 stones per player. Matches analytical expectation.
- Trained vs random = 0.96 both runs; final winrate 0.5 both runs → game is *learnable* and *balanced under learned play*. No obvious degeneracy.

---

## PHASE 2 — STRATEGIC PLAY

(All moves engine-verified via the `simulate_move`/`_save_state` pattern. Greedy policy: pick move with max (own-score-delta − opponent-score-delta). Immediate-win moves taken if available.)

### Game 1 — P1 center, P2 adjacent
- Opening: P1 = (4,4) center. P2 = (3,3) [hex-adjacent + Manhattan-distance 2, a bypass].
- Play continued greedy. Sequence (27 moves):
  `36, 27, 35, 28, 37, 29, 44, 21, 43, 20, 45, 19, 34, 11, 42, 12, 26, 13, 18, 10, 41, 2, 33, 3, 25, 4, 17`
- **Result:** P1 wins, 40.58 vs 37.86. Tempo advantage was decisive (P1 crossed threshold first by one turn).

### Game 2 — P1 corner, P2 edge-follow
- Opening: P1 = (0,0) corner. P2 = (0,1) [hex-adjacent to corner, starting the left-edge chain].
- Play continued greedy. Sequence (34 moves):
  `0, 8, 1, 16, 9, 17, 10, 18, 2, 19, 3, 11, 4, 12, 5, 20, 6, 13, 7, 21, 14, 22, 15, 23, 24, 25, 32, 26, 33, 27, 40, 28, 41, 29`
- **Result:** P2 wins, 43.54 vs 38.36. Corner opening surrenders the tempo because P1's cluster has only 3 usable hex neighbors, limiting its influence-field; P2 wraps around and out-scores.

### Game 3 — Seat swap (I play P2); bypass-then-extend
- Opening: P1 = (4,4). P2 (me) = (3,5) [hex-adj + Manhattan-2 bypass]. P1 = (4,3) [greedy]. P2 greedy thereafter.
- Sequence (28 moves):
  `36, 43, 28, 42, 20, 34, 12, 35, 4, 26, 3, 27, 11, 18, 19, 17, 2, 25, 10, 33, 1, 41, 9, 16, 0, 24, 8, 32`
- **Result:** P2 wins, 41.23 vs 38.64. The bypass opening denies P1 the Manhattan-1 value-exchange on move 2, then P2 extends into the empty left half, collecting full-strength placements with clean neighborhoods.

### Per-side reflections

**Player 1 guide.** Open on the center or one ring from center (NOT a corner). After P2's response, resist greedy contact-extension — instead mirror P2's direction of expansion so you don't waste tempo on partially-devalued cells. Keep your cluster convex so Manhattan-1 neighbors include as many own stones as possible (each own-neighbor of an own-stone adds +0.647 to your threshold). Aim to cross threshold around move 27-29.

**Player 2 guide.** Answer a center opening with a **hex-diagonal bypass** (Manhattan-2 from P1's first stone). Avoid playing Manhattan-adjacent to P1 on move 2 — it donates ~0.65 of your value to P1's cell for no positional gain. After bypass, extend into the large empty region, building a convex cluster. If P1 opens a corner or edge, take any hex-adjacent cell immediately — P1's restricted corner cluster cannot keep pace.

### Surprises
- The Manhattan/hex adjacency mismatch is *the* strategic axis. Two of a hex neighbor's 6 cells are "influence-cold" and those are the right places to put your first contact stone.
- Double-pass never triggered in any of the 3 games (threshold was always met first).
- Games converge in ~27-34 moves — never remotely close to the 100-turn cap. No non-convergence issues.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**Distinct viable strategies?** Yes — at least two:
1. **Contact race** (greedy tempo): build a tight cluster in direct contact with opponent; trust your one-move lead.
2. **Bypass-and-extend**: use hex/Manhattan mismatch to place without value exchange, then expand in the cold half of the board.

These produce measurably different outcomes (Game 1 favored contact-race P1; Games 2 & 3 favored bypass P2).

**Counter-play?** Moderate. P1 cannot force the contact-race line if P2 insists on bypass; P1 must choose between chasing P2 into the cold zone (losing contact exchange) or building own cluster (losing territory pressure). P2's response choice depends on P1's opening (corner → edge follow; center → hex-diagonal bypass).

**Short-term vs long-term?** Weakly present. Every placement immediately adds to your threshold, and stones never leave the board, so there's no "sacrifice" concept. Long-term tension is entirely about cluster geometry (convexity → more own-neighbor bonuses).

**Emergent concepts?**
- *Tempo* — real, ~1-move worth of threshold (~1.4).
- *Influence geometry* — an implicit 4-vs-6 mismatch gadget.
- *Territory orientation* — convex vs linear clusters matter.
- *Ko / liveness / capture* — absent; game is strictly monotonic.

**Does topology matter?** Yes but partly by accident. The hex topology itself is a minor re-skin; what matters is the *mismatch* between hex adjacency and Manhattan influence, which is arguably a propagation-code bug that happens to produce strategic texture.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary's case (against novelty)

(a) **Catalog check.**
- *Go / Hex / Havannah / Y / Connect6:* Different goal class (capture/connection/line). Not this game.
- *Othello/Reversi:* No flipping, no outflanking. Not this.
- *Gomoku / Pente:* No in-a-row goal. Not this.
- *Amazons / LoA / Chameleon:* Movement-based. Not this (place-only).
- *Mancala variants:* Stone sowing, different structure. Not this.
- *Life-like CA (Conway, Day&Night, HighLife):* CA-driven, not this (classic, no CA).
- **Closest known game: Tumbleweed (Mike Zapawa, 2021)** — hex-based influence/territory game where each placement contributes LOS-weighted strength to cells. Also *Blooms*, *Star*, *Havannah* influence variants. This game's "place → numeric influence adds to neighbors → sum on your cells wins" IS a direct structural parallel.

(b) **CA literature:** N/A — classic game, no CA rule.

(c) **Re-skin claim:** This is "Tumbleweed-lite on an 8×8 hex grid with Manhattan-1 influence and an adjacent-chain placement constraint and a threshold win at 39.66". All four ingredients (hex board, additive numerical influence, connected placement, first-to-threshold) pre-exist in the abstract-game literature.

(d) **Expert transfer:** A Tumbleweed expert would carry over the "cluster convexly, reinforce your own stones" heuristic directly. A Go player's intuition about "do not let your stones be adjacent to enemy" transfers partially (enemy-adjacent cells cost you ~1.3 net points). So experts in neighboring games have real leverage here.

### Rebuttal

- **P1 rebuttal:** Tumbleweed uses *line-of-sight* weighting that is isotropic w.r.t. the hex; *this* game uses Manhattan-1 influence on a hex-adjacency graph, creating two hex-adjacent-but-influence-cold cells per stone. This gadget is the single best move of Game 3 (P2's (3,5) bypass). No Tumbleweed or Go intuition produces this move — it's an artifact of how the engine computes `cells_within_radius` (code path: `topology.py:267` uses Manhattan on coords regardless of topology). A Tumbleweed expert *would not* find this move natural.
- **P2 rebuttal:** Strict monotonicity (no capture, no overwriting, no flipping) makes this *unlike* any influence game we could name. Tumbleweed has overwriting; Reversi has flipping; Go has removal. The "place forever + threshold" class of game is rare in the design literature.

### Resolution — Novelty score

The game is a recognizable additive-influence territory game with one genuinely novel (or at least accidental) strategic gadget and an unusual strict-monotonic flavor. It would be recognizable to a Tumbleweed player but not identical. **Novelty = 4/10.**

---

## PHASE 5 — VERDICT

**Team ID:** team-6
**Game ID:** 558e1f1be563
**Rules Summary:** Place stones alternately on an 8×8 hex board, each placement must be hex-adjacent to any existing stone; every placement adds ±1.42/±0.65 influence to the placed cell and its Manhattan-1 neighbors; first player whose own-cell influence sum exceeds 39.66 wins.
**Topology:** 2D 8×8 hex (pointy-top offset coords, 6-connectivity).

### SCORES (1-10)

- **Strategic Depth: 5** — Two distinct strategy archetypes (contact-race vs bypass) produce divergent outcomes; the hex/Manhattan mismatch creates a real decision space. But no ko, no capture, no sacrifice, and the horizon is short (≈27 moves), so depth is bounded.
- **Emergent Complexity: 4** — Tempo, cluster convexity, and the bypass gadget emerge. Nothing like life-and-death groups, ko fights, or long-range combinatorics.
- **Balance: 6** — With learned play, win rates are 50/50 (confirmed by training stats and by our Games 2-3 where P2 wins with correct response). Greedy P1 from center slightly favored, but P2 has a known refutation. A human first-time advantage does exist but is not dominant.
- **Novelty (post-adversary): 4** — Strongest adversary argument: "This is Tumbleweed-on-hex with Manhattan influence and a threshold win." Rebuttal: The 6-vs-4 adjacency mismatch and strict monotonicity produce a strategic gadget (the hex-diagonal bypass) absent from Tumbleweed and all other catalogued influence games.
- **Replayability: 4** — Opening forces very real branching (corner/edge/center × bypass/contact). Mid-game collapses into local greedy once clusters form. Replayable 5-10 times; not likely to sustain a regular player.
- **Overall "Would I play this again?": 4** — It's fine. I'd play it twice to explore the bypass gadget, then switch to Hex or Tumbleweed, which dominate it on depth.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed** (Mike Zapawa, 2021). Both are hex-based, additive-influence, territory-threshold games. This game is *not* identical because (i) influence uses Manhattan distance on coordinates (a mismatch with hex adjacency), and (ii) placements are strictly monotonic (no overwriting, no LOS blocking).

### KILLER FLAWS
- **Topology-influence mismatch** is either a bug or a very lucky accident. The "radius" parameter uses Manhattan distance regardless of the topology type, so hex adjacency is never realized in influence. This undermines the "hex-ness" of the game and reduces it closer to a Manhattan-grid influence game where only the placement constraint is hex.
- **No ko, no capture, no liveness** → no tactical richness beyond placement choice. Every interesting Go/Hex concept is absent.
- **Short horizon** (~27 moves) limits strategic planning depth.

### BEST QUALITY
The accidental hex-diagonal bypass gadget. Once a player discovers that a hex-neighbor at Manhattan-distance-2 is an "influence-cold" placement, the opening becomes genuinely textured: should I contact (race) or bypass (build clean)? This single decision point carries the game.

### IMPROVEMENT IDEAS
**One rule change:** Change the influence propagation to use hex graph-distance (i.e., replace `topology.distance` from Manhattan to BFS-on-neighbors). This removes the bypass gadget — **which is actually the game's best feature**, so this is *anti*-advice.

**Better alternative:** Add **capture** — e.g., "a stone whose cell value is < -threshold/2 is removed at the end of each turn." This would restore ko-like dynamics, life-and-death, and make the monotonic race game into a dynamic battle for contested cells. Would likely raise strategic depth to 7-8/10.

### FINAL VERDICT
A competent but minor additive-influence territory game. Training metrics (ELO 1003, GE 0.486) overestimate its strategic quality — the game converges quickly and its depth is bounded. Its single genuinely interesting feature (the hex-vs-Manhattan bypass) is an accidental artifact of the engine's distance function, not an intentional design. **Final scores: Depth 5 / Emergence 4 / Balance 6 / Novelty 4 / Replayability 4 / Would-play-again 4.**
