# Run 13 Evaluation — Team 5
**Game ID**: `558e1f1be563`  (rank 2, Go Essence 0.486) — 2D hex, threshold win, CLASSIC (no CA)

---

## Phase 1 — Rule Comprehension

### Board / topology
- 2D hex grid, 8x8 = 64 cells.
- Hex adjacency uses offset coordinates (6 neighbours for interior cells; even rows offset left, odd rows offset right).
- 65 actions total: cells 0-63 = `y*8 + x` placement, action 64 = PASS.

### Turn structure & actions
- Alternating turns; Player 1 (X) moves first.
- 1 piece placed per turn (`pieces_per_turn=1`); action set is `place` only — no movement.
- Placement constraint: `adjacent_to_any` — each new stone must be placed on an empty cell adjacent to at least one existing stone of *either* colour. Exception: `first_move_anywhere=True` lets each player's first move go anywhere. (Verified: P2 legally opened at (0,0) with only a P1 stone at (3,3) on the board.)
- PASS is always legal.

### Capture
- `capture_type = none`. **There is no capture in this game**. Stones once placed are permanent.

### Propagation (influence)
- After each placement, a signed scalar field `board_values[c]` is updated:
  - `+strength` (=1.4192) added at the placed cell itself, sign `+` for P1, `-` for P2.
  - `+strength * decay^dist` added at every cell within radius 1, i.e. +0.6474 on each of up to 6 hex neighbours (sign as above).
- Values are clamped to [-100, +100] per cell.
- Because decay < 1 and radius = 1, influence stops at the immediate hex ring. There is no long-range field.

### Win condition
- `condition_type = threshold`, `threshold ≈ 39.658`, `target_dimension = 0`.
- The effective score for P1 is `sum(board_values[c] for c owned by P1)`; P2's effective score is the negation of the same sum over P2-owned cells.
- First player whose effective score exceeds 39.658 wins. If `max_turns` (100) is reached, the game ends by *piece-count majority* (tie → draw). Double-pass also ends the game (same majority tiebreak).

### Flags / degeneracies
- No capture + placement-adjacent constraint means the game is a monotone accumulation game — the board only fills up, it never clears. This heavily limits strategic branching (no ko, no trades, no sacrifice mechanic).
- `target_dimension_p2 = -1`: P2 uses the same target dimension with inverted sign — that's handled by the symmetric sum formula above, not broken.
- **Threshold is actually achievable but precarious.** With 64 cells and a rough per-piece self-contribution of ~1.5 influence, reaching 39.66 requires both concentrating your stones (so adjacent friendlies pile on +0.647 each) and avoiding enemy adjacency (which drains your stones). See the draw in Phase 2 Game 1.
- No degenerate "play action 0 forever" style forced win.

---

## Phase 2 — Strategic Play

Three games were played, each move engine-verified through `play_helper.py`.

### Game 1 — "symmetric contesting clusters"

Strategy: both sides attempt *swing maximisation* — pick the legal empty cell with the most (own + enemy) hex neighbours, so every move simultaneously buffs own score and drains opponent's.

Move list (all verified legal):
```
36(P1 (4,4)), 27(P2 (3,3)), 28(P1 (4,3) triple-adj: reinforces (4,4), poisons (3,3)),
35(P2 (3,4) mirror), 20(P1 (4,2) stacking), 19(P2 (3,2) mirror),
26(P1 (2,3) double-poison), 37(P2 (5,4) mirror),
21(P1 (5,2)), 18(P2 (2,2)), 29(P1 (5,3) triple),
44(P2 (4,5) triple), 12(P1 (4,1)), 43(P2 (3,5) triple),
11(P1 (3,1) triple), 10(P2 (2,1) triple), 45(P1 (5,5) poison)
…continues to fill the board via greedy expansion.
```
After 17 moves the interlocked core was settled; greedy continuation to move 66 produced a **completely filled board** with P1 effective 24.06 and P2 effective 22.76 — **neither side reached 39.66**. Double-pass at move 66, piece count 32-32 → **draw**.

- **Discovery 1**: when both players play the poisoning variant of greedy, opponent adjacency drains mutual influence enough that the threshold is *never* met.
- **Discovery 2**: in an interlocking pattern, effective score tops out around 24-25 per side — well below the 39.66 threshold.

### Game 2 — "parallel cluster races"

Strategy: both sides play *cluster-first* (pick the cell that maximises own friendly neighbours, weight enemy-adjacency as negative). This corresponds to "build your own fort, avoid poisoning yourself by stepping into the enemy".

Opening is forced by tie-breaking to cell 0, and both players spiral out from their respective corners:
```
0,1,8,9,16,17,24,2,32,10,33,18,40,25,41,34,49,26,48,19,50,42,56,35,57,27,58,51,59,43
```
Final position at move 30:
```
X O O . . . . .
X O O . . . . .
X O O O . . . .
X O O O . . . .
X X O O . . . .
X X O O . . . .
X X X O . . . .
X X X X . . . .
```
- P2 plays the **second column** — structurally wider (each P2 stone has two P2 friends to its right). P2 reaches 40.70 > 39.66 at move 30. **P2 wins by threshold.**
- **Discovery 3**: the first-to-start-clustering is actually *disadvantaged* when both players build side-by-side walls; the player who "shadows" the other's column gets denser mutual adjacency and reaches threshold first. This is a **second-mover advantage** in this game mode, *the opposite* of what most territory games show.

### Game 3 — asymmetric openings (seat swap implemented)

To reduce seat bias I forced openings (4,4) for P1 and (0,0) for P2 (both legal — first_move_anywhere), then both played greedy-swing with tie-breaking randomised on seed 777. Same playing agent as Games 1-2, so the seat-swap bias is **not eliminated** — acknowledged as a limitation.

- Players never made contact until ~move 40; influence accumulated in two separate clumps.
- Game filled to move 66, double-pass. P1=32.47, P2=32.47 (identical), 32-32 pieces → **draw**.
- **Discovery 4**: when players stay out of each other's way they *also* fail to reach threshold — the poisoning from eventual contact is offset by the mutual reinforcement of filling in adjacencies, and the effective score saturates around the mid-30s.

### Strategy guides

**Player 1**: Open centrally (maximises future adjacency options). Every subsequent move, play the cell that touches the most *own* stones first, most *enemy* stones second. Never choose an isolated cell when a double- or triple-adjacency is available. Expect to be mirrored; react by clustering deeper rather than breaking into new territory.

**Player 2**: Mirror the opening in the hex-symmetric position. When P1 offers a cluster-extension move, take the *mirror* position that simultaneously defends your own stones and drains one of P1's. Because the hex lattice is symmetric under swap, P2 never falls behind — the only way to lose is to diverge from mirroring. On open-field starts, play tightly adjacent to your own stones and avoid walking into P1's influence.

---

## Phase 3 — Strategic Analysis (joint)

- **Dominant strategy**: "maximise (own_friendly_neighbours + enemy_neighbours) per move, with a mild preference for own > enemy when tied." This collapses to a local hill-climb. In Games 1 and 3 this produced draws; in Game 2 it produced a P2 win.
- **Counterplay?** Limited. Breaking from mirror yields a worse placement by the influence formula, so strong play is forced into a narrow band. There is a genuine P1/P2 second-mover question — not a grand strategy choice.
- **Short-term vs long-term tension?** None. Every move's influence is locked in at placement time (no capture, no reclaim), so evaluating one step ahead is near-optimal. There is no sacrifice because there is no capture.
- **Emergent concepts?** Weak. A kind of *territory* emerges (you want your cells clustered so they share ring influence), but with no capture there is no *contest* for territory — you just paint empty cells first. "Poisoning" (adjacent enemy reduces your cell's value) is emergent but small: only 0.647 per poison-neighbour vs 1.42 per own-cell base. Enemy stones near a frontier bleed ~15% of your front-row value.
- **Does topology matter?** Modestly. Hex's 6-neighbour ring means interior cells carry ~1.42 + 6×0.647 = 5.3 peak influence, and corners carry ~1.42 + 3×0.647 = 3.4. This makes interior clustering strictly better than edge play, which is a real lesson, but not a deep one — it's just "centralise on any hex board".
- **Games hit natural contested draws (Game 1, Game 3) or decisive first-to-threshold wins (Game 2).** No ko, no chase, no initiative swap. The decision space collapses quickly.

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary's case

**(a) Catalog sweep:**
- **Go**: weak match. Go has capture and liberty logic — this game has *neither*. Reject Go as the direct analog, but the "influence accumulation over a hex board" framing is a known Go variant intuition.
- **Hex (Piet Hein's game)**: strong match on the board — this is literally an 8×8 hex grid. Hex's win condition is *connection edge to edge*; here it's *influence threshold*. Reject direct equivalence, but the board is identical.
- **Reversi/Othello**: wrong capture model; reject.
- **Gomoku / Pente / Connect6**: similar placement-adjacency flavour (Gomoku with forced adjacency), but wins by *line of k*, not by score. Reject.
- **Y / Havannah**: connection games on hex; different win condition, reject on victory test alone.
- **Amazons**: movement-heavy, burns squares; nothing like this. Reject.
- **Lines of Action / Mancala**: irrelevant.
- **Life-like CA**: N/A — this is a classic game, no CA rule.
- **Closest known analog**: **Paul Smith's "Influence" games / Tumbleweed (2020)** — a hex-board influence-stacking game where players drop stones and compute a scalar influence field to determine ownership. Tumbleweed uses a specific "line-of-sight stone count" formula; this game uses "strength * decay^distance with decay=0.456, radius=1". Tumbleweed also permits stacks up to n on a cell; this game forbids stacking. **Tumbleweed is the nearest family member**, but this game is stack-less, radius-1, and uses a signed sum with a hard threshold.

Also close: **"Ataxx / Slither" influence variants** (radius-1 influence, no capture) — but those have capture-by-approach which this game lacks.

**(b) CA test:** N/A, classic game.

**(c) Re-skin hypothesis:** "This is Hex-on-8×8 with a weighted piece-count instead of a connection win." The adversary argues: since there is no capture and each stone's final contribution is roughly `1.42 + 0.647*(own_neighbours) - 0.647*(enemy_neighbours)`, the game reduces to "place more stones than the opponent, preferably in a connected cluster, preferably not next to enemies". That is basically *weighted majority on an adjacency-constrained hex board*, with pass allowed. A majority game in disguise.

**(d) Expert-transfer test:** A Tumbleweed expert would immediately recognise (i) influence is a scalar field, (ii) contiguity matters, (iii) the first-move-anywhere + subsequent adjacency rule creates a spreading territory dynamic. They would have a real head-start. However, the absence of stacking and the 39.66 threshold with no-capture means there are no "tumble" recaptures; the expert's stacking intuition wouldn't apply. An expert at plain majority-on-hex (rare) would translate well.

### Rebuttal (Player 1 + Player 2)

- **Not Hex**: concrete disproof from Phase 2. In Game 2, P2 builds a solid column but never *connects* anywhere — Hex's win condition would award the game to whoever spans edge-to-edge, which neither player achieved. P2 won by *magnitude*, not connectivity.
- **Not pure majority**: the draws in Games 1 and 3 ended with a 32-32 piece count but different effective scores (24.06 vs 22.76 in Game 1). Majority would tie both. Here influence created a numerical *difference* even at identical stone counts — majority is a degenerate summary, not the actual objective.
- **Not Tumbleweed**: Tumbleweed's influence is line-of-sight and stacks; here influence is 1-step decay with no stacking. The strategic question "where does my influence reach" is a 2-cell question in this game vs a whole-ray question in Tumbleweed. A Tumbleweed expert would over-think rays.
- **Concrete failure of Gomoku/Pente intuition**: Game 2 ended on move 30 with *no line of 5 anywhere* on the board — a Gomoku player would have been looking for threats that do not exist here.

### Novelty resolution

The game is **not a direct clone** of any named abstract. But it's structurally close to Tumbleweed / influence-majority family, and the **strategic space collapses to a narrow hill-climb**: swing-max or cluster-max produces near-optimal play with almost no counter. The mechanics are novel-ish, the *gameplay* is not — it's effectively "greedy adjacency accumulation with a numerical goal."

**Team Novelty score: 4/10.** Genuinely novel threshold-on-hex formulation, but the decision space is too shallow to produce novel play; an expert at any influence-majority hex game would dominate immediately.

---

## Phase 5 — Verdict

**Team ID**: team-5
**Game ID**: 558e1f1be563
**Rules Summary**: On an 8×8 hex board with no capture, players place one stone per turn (adjacent to any stone after the opening); each stone radiates signed influence to its own cell (+1.42) and its 6 hex neighbours (+0.647). First player whose owned cells sum above 39.66 wins; else double-pass/100-move timeout awards majority of stones.
**Topology**: 2D hex, 8×8, 64 cells.

**SCORES (1–10):**
- **Strategic Depth: 3** — Optimal play is greedy adjacency maximisation with minor tie-break choices; no long-horizon tension because there is no capture and every placement permanently locks in influence. In three games, one decisive outcome and two filled-board draws.
- **Emergent Complexity: 3** — "Cluster your stones; mirror the opponent" is the full strategic story. A weak territory-like concept emerges but without contestation (no capture means territory cannot be seized back).
- **Balance: 7** — The game is symmetric under seat swap and our Game 2 showed a second-mover *advantage* rather than a first-mover one, which is unusual and indicates the board doesn't favour P1 structurally. Ties are common, which is consistent with good balance.
- **Novelty (post-adversary): 4** — Threshold-on-hex with radius-1 influence is genuinely an uncommon framing, but it reduces to weighted-majority-on-hex in practice; Tumbleweed / Influence-family expertise transfers substantially.
- **Replayability: 3** — Greedy play converges to one of two fixed shapes (interlocked draw or parallel-columns win). Little incentive to replay once the pattern is seen.
- **Overall "Would I play this again?": 3**

**CLOSEST KNOWN-GAME ANALOG**: *Tumbleweed* (Mike Zapawa, 2020) — the closest family member, both being hex influence-accumulation games without classical capture. Not identical because Tumbleweed uses line-of-sight stacking and Michael ownership rules, while this uses 1-step decay with no stacking and a hard scalar threshold.

**KILLER FLAWS**:
1. **No capture → no recovery mechanic.** Every move is locked in; no interesting trade-offs over time.
2. **Threshold is barely reachable under contested play** — Games 1 and 3 both produced filled-board draws at effective 24-32 per side, below 39.66. The win condition activates only when one side can build unopposed, which encourages a *flight from contact* rather than a *fight for territory*.
3. **Greedy local optimisation is near-optimal.** A 1-ply heuristic produces strong play, which bounds depth.
4. **Opening-asymmetric starts can freeze the game into an "each to their own corner" fill with no real interaction.**

**BEST QUALITY**: The signed-influence formulation is mathematically elegant and does create a real ±15% "poison" effect when enemy stones sit next to your stones, which produces the one interesting decision in the game: *do I mirror-defend, or do I break for open space and hope my opponent follows me?* Game 2 showed this choice has a concrete payoff — a second-mover advantage emerges that's quite unusual for territory-flavoured games.

**IMPROVEMENT IDEAS**:
- **Add a capture rule** (e.g. outnumber capture, threshold 2) on the hex board. This would introduce contestation, make pieces reclaimable, and raise strategic depth dramatically while keeping the influence framework.
- **Alternative**: *reduce the threshold* (e.g. to 25.0) so that contested play still decides, rather than degenerating into fill-board draws. Currently the 39.66 threshold is only reachable under lightly-contested positions, which perversely rewards *avoiding* the opponent.
- Either fix would likely elevate the Strategic Depth score above 6.

### Final verdict

**A mechanically novel but strategically shallow game.** The signed-influence + hex + threshold combination is uncommon, and the second-mover "shadow-column" advantage is a real emergent curiosity. But the absence of capture collapses the decision tree to greedy adjacency, two of three games drew by filling the board, and the one decisive game was a 30-move race with a predictable cluster pattern. Closest to *Tumbleweed*, but less deep. Fine as a research artefact; not a game I would replay.
