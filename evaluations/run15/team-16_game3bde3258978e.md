# Team-16 Evaluation — Game `3bde3258978e`

Run 15 · Generation 10 · GE 0.2005 · Non-Triviality 1.00

---

## PHASE 1 — RULE COMPREHENSION

### Board
- **Dimensions:** 2D
- **Axis size:** 8 (total 64 cells)
- **Topology:** `moore` — every cell has up to 8 neighbors (face + diagonal). This is the adjacency graph used for both *influence propagation* and *surround-capture liberties*.
- **No torus wraparound** (corners/edges have fewer neighbors).

(Side-note: `play_helper.py`'s `--action rules` output mis-labels this as "von Neumann". The topology class `build_moore_neighbors` clearly builds 8-neighbor adjacency — verified empirically: one stone's influence reaches all 8 surrounding cells at radius 1.)

### Turn structure
- **Alternating.** 1 piece placed per turn. Standard "P1 then P2 then P1…".

### Actions
- 65 actions: 0–63 place on empty cell `idx = y*8 + x`; action 64 = PASS.
- Placement target: empty cells, anywhere. `first_move_anywhere: true` (no restriction on the opening).
- Illegal placements (non-empty cell) are silently excluded from `get_legal_actions()`.

### Capture — `surround` with threshold 1
- Classic Go-style: after placing, any enemy group on Moore-adjacency whose liberty count drops to 0 is removed.
- Because topology is Moore (8-connected), groups are highly connected and liberties are plentiful — **captures are rare in open play**. Verified that a single stone in a corner *can* be captured (only 3 Moore neighbors to fill), but a single stone in the interior needs all 8 Moore neighbors occupied by the opponent simultaneously — essentially never happens mid-game.

### Propagation — `influence`
- Radius 1, **strength 0.9323, decay 0.5097**.
- When a player places at cell *c*, every Moore cell within radius 1 (so *c* itself plus up to 8 neighbors) has its `board_values` incremented by `strength · decay^dist` with sign **+** for P1 and **−** for P2.
- Empirically: a lone P1 piece radiates `+0.932` on itself and `+0.475` on each of its 8 neighbors.
- Values are per-cell signed floats (one number per cell, not per player). Enemy pieces nearby partially cancel your own values.

### Win condition — `threshold = 22.645` on `target_dimension=0`
- At end of each turn, engine iterates `for player in (1, 2)`: sums `board_values[c]` over cells where `board_owners[c] == player`, flips sign for P2, and declares winner if `effective > 22.645`.
- **Max turns 100.** If max_turns is reached without a threshold cross, winner is decided by piece-count majority (R15 engine — `_end_by_max_turns` still uses majority; only *double-pass* resolves to draw).
- Target dimension is 0 (irrelevant for a 2D single-board game — just indexing convention).

### Flags / degeneracy check
- **Capture is near-inert in contested play.** Moore 8-connectivity makes groups very hard to surround once they have any diagonal liberty. I constructed exactly one capture in testing — a corner stone. In all 3 play-throughs, no capture occurred.
- **Threshold is reachable.** ~9 well-packed adjacent pieces (a 3×3 dense block at a corner) accumulates own-cell influence ≥ 22.645. Verified: P1 with 8–10 tightly packed pieces wins every Phase-2 game tested.
- **Not degenerate but strongly first-mover biased.** Because value accrues super-linearly with cluster density (each new stone both adds its own 0.932 and boosts adjacent owned cells by 0.475 each), and because P1 gets a 1-piece head start, P1 reaches the threshold first in fully-symmetric play. See Phase 2.
- **No double-pass resolutions in our tests.** Every game I played ended via threshold cross.
- **Pilot "threshold check-order bias" (P1 wins ties):** only material in simultaneous threshold games. This game is alternating — only one player changes influence per tick — so ties on the same tick are effectively impossible. Bias does not apply.

---

## PHASE 2 — STRATEGIC PLAY

All moves were engine-verified via `play_helper.py --action play --moves "…"`. The three games are listed in move order as comma-separated action IDs, with cell coordinates and my reasoning.

### Game 1 — P1 and P2 build opposite-corner clusters (no interference)

**Moves:** `0, 63, 1, 62, 8, 55, 9, 54, 2, 61, 10, 53, 16, 47, 17`
(cells: `(0,0)(7,7) (1,0)(7,6) (0,1)(6,7) (1,1)(6,6) (2,0)(5,7) (2,1)(5,6) (0,2)(7,5) (1,2)`)

- Move 1 (P1 0,0): opening at a corner — corners maximise the *density* of neighbors available per stone inside a small cluster; nothing is "wasted" radiating off-board since off-board doesn't exist. A corner 3×3 block is objectively denser than a center 3×3 (in the sense that all 9 of its stones share a compact footprint with no pressure from outside influence).
- Move 2 (P2 7,7): mirror — a natural rational response because contesting the corner is costly (P1 has a head-start there).
- Moves 3–14: each player grows their corner block outward along the edges. No captures. No collisions (alternating).
- Move 15 (P1 1,2): P1's 8th stone creates the final adjacency that lifts own-cell sum past 22.645. **P1 wins on move 15, 8 pieces placed.**

P1's reflection: The race was symmetric up to the move count, but P1 always has one more stone placed. With no interference, the game is a strict tempo race — P1 wins by a single move. P2 has no realistic defence if they mirror.

P2's reflection (same agent, acknowledged bias): mirroring is tempting but concedes the race. A better P2 plan is to invade P1's cluster early and break the density. Tried this in Game 2.

**Outcome:** Threshold cross (P1 wins, own-cell sum ~23.6). Not a double-pass draw.

### Game 2 — P1 center block; P2 pressures adjacent then retreats

**Moves:** `27, 28, 26, 19, 25, 20, 35, 36, 34, 43, 33, 42, 24, 50, 32, 51, 40, 45, 41`
(cells P1: `(3,3)(2,3)(1,3)(3,4)(2,4)(1,4)(0,3)(0,4)(0,5)(1,5)`; P2: `(4,3)(3,2)(4,2)(4,4)(3,5)(2,5)(2,6)(3,6)(5,5)`)

- P1 opens center (3,3). P2 plays contact at (4,3), trying to pin P1's block.
- Moves 3–12: both players build 3×3-ish clusters jammed against each other. After 12 moves influence stood at **P1 10.35 / P2 5.59** (P1 was winning the jam because every P1 placement on the left side is adjacent to two other P1 stones with no opposing pieces in that direction, whereas P2's east-side placements are flanked by P1 diagonals).
- Moves 13–19: P1 extends west/south (0,3)(0,4)(0,5)(1,5) — unopposed territory. P2 chases (2,6)(3,6) but never closes the influence gap.
- **P1 wins on move 19, P1=10 / P2=9 pieces.** Own-cell sum ~23.1.

P1 strategy insight: when opponent contests your cluster, extend along the *free* side. A contested block loses roughly ½ the own-cell value per contested face; an uncontested extension adds the full `0.932 + 0.475·k` where *k* counts already-owned Moore neighbors.

P2 strategy insight: contact fighting in this rule set *transfers* influence from both sides because `+influence − influence` values cancel on both cells. The player with more pre-committed stones (P1, by virtue of going first) wins the exchange. P2 should rather play one-gap-away plays that protect their own cluster density without canceling P1's.

**Outcome:** Threshold cross (P1 wins). No captures. No double-pass.

### Game 3 — Seat swap: primary-agent plays P2; P1 (secondary role) spreads out

**Moves:** `0, 27, 7, 28, 56, 35, 63, 36, 2, 26, 5, 19, 14, 20, 23, 29`
(P1: corners & edges `(0,0)(7,0)(0,7)(7,7)(2,0)(5,0)(6,1)(7,2)`; P2 center block `(3,3)(4,3)(3,4)(4,4)(2,3)(3,2)(4,2)(5,3)`)

- P1 deliberately spreads stones to all four corners + top-edge fillers — a *bad* strategy chosen to test whether P2 can win given space.
- P2 builds a tight 3×3 around the center: (3,3),(4,3),(3,4),(4,4),(2,3),(3,2),(4,2),(5,3). 8 stones, 3×3 packed plus one east extension.
- **P2 wins on move 16, P2=8 pieces.** Own-cell sum >22.645.

P2 reflection (primary role, Game 3): compact central play straightforwardly beats dispersed P1 play even when moving second. The key insight is that compactness compounds: each new stone adjacent to *k* owned stones contributes `0.932 + k·0.475` to own-cell sum. A stone with 4 friendly Moore neighbors contributes ~2.83 to the sum, vs ~0.932 alone.

P1 reflection (secondary role, Game 3): I intentionally sandbagged to probe the strategy space. A competent P1 wins this matchup by copying P2's cluster or contesting it directly (Games 1 and 2 confirm).

**Outcome:** Threshold cross (P2 wins). No captures. No double-pass.

### Seat-swap results summary
| Game | Seat-1 strategy | Seat-2 strategy | Winner | Turns |
|------|----------------|----------------|--------|-------|
| 1 | Corner cluster (0,0) | Opposite corner (7,7) | **P1** | 15 |
| 2 | Center cluster (3,3) | Contest center | **P1** | 19 |
| 3 | Dispersed (corners) | Compact center | **P2** | 16 |

- In the 2 "fair" games (1 and 2) P1 wins due to tempo.
- In the 1 game where P1 plays a hand-crafted bad strategy, P2 wins.
- **No double-pass resolutions.** All three games ended cleanly by threshold.

### Strategy guides

**Player 1 guide:**
1. Open at a corner (best) or the center. Do NOT spread. Cluster density is the entire game.
2. Keep every placement adjacent to at least one existing own-stone. Two-friendly-neighbor placements contribute ~1.88 to own-cell sum; a zero-neighbor placement contributes only 0.93.
3. Ignore opponent placements unless they touch your cluster; then extend along the unblocked face rather than contest.
4. Expect to need 8–10 well-placed stones. Budget ≈ 15–20 turns.

**Player 2 guide:**
1. Mirror P1's corner — you lose the race by one tempo but keep the option of winning if P1 mis-plays.
2. If P1 plays center, contest diagonally-adjacent rather than directly adjacent (both players cancel each other on direct contact).
3. If P1 disperses (rare), build a tight 3×3 anywhere uncontested — 8 pieces suffices.
4. Capture rule is essentially dead in practice — do not plan for surrounds except in the opening corner case.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**Distinct strategies?** Two viable families: "corner pack" and "center pack". Corner is slightly faster (8 stones to threshold vs 9) but committed; center trades flexibility for exposure to contact fighting. A third family — "distributed influence-spreading" — is dominated; pieces must cluster or they waste per-cell contribution.

**Counter-play?** Weak. The dominant response to a corner opening is to mirror (opposite corner), which accepts losing the tempo race. The alternative — direct contact — wastes value on both sides because the signed-influence field cancels. There is no known move order that reliably flips the first-mover advantage when both players play cluster strategies.

**Short-term vs long-term tension?** Minimal. Almost every stone is a direct value play; there are no "lose-now-to-win-later" tactical sacrifices because the capture rule is effectively inert in open play. The only long-term question is cluster *shape* (compact 3×3 vs 2×4 rectangle) which is tactical flavor, not strategic depth.

**Emergent concepts?** 
- *Cluster density / mass* (clear emergent concept — the dominant optimization target).
- *Contact cancellation* (a minor emergent Reversi-like idea: adjacent opposite stones partially cancel).
- Not really *territory* in the Go sense (no score from influenced-but-unoccupied cells — only own-cell influence counts).
- No *tempo* beyond the trivial "P1 moves first".
- No *ko*, no *life-and-death*, no *initiative-transfer*.

**Does topology matter?** Partially. Moore adjacency matters because it determines the neighborhood of the influence radius (9 cells instead of 5 for von Neumann). Corners matter because they limit cluster footprint. The 8×8 grid fits exactly one 3×3 block at each of four corners, which makes corner play dominant. If the board were 5×5 or a torus, the calculus would change.

**First-mover advantage:** Strong and observed. In 2/3 games P1 won. In game 3 P1 lost only because I deliberately sandbagged P1's strategy. I estimate under optimal play P1 wins 100% of games — this is functionally a solved tempo race with very slight variance from cluster-placement tactics.

Seat-identity bias acknowledgment: I ran both players as one agent sequentially. To counteract, I (a) kept an explicit "P2 strategy" note between moves when reasoning as P2 and only ran P2's moves through the engine between P1's decisions, (b) swapped seats in game 3, and (c) in game 3 had P2 (the "primary" role) play a known-good strategy (tight center cluster) while P1 (secondary) played a known-bad strategy (dispersion). That the bad-P1 strategy lost confirms the seat mechanic is secondary to strategy quality once a good strategy is found.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary's case (the game is NOT novel):

**(a) Known-game catalog:**

- **vs Go:** This IS Go with (i) Moore-style 8-connectivity instead of 4-connectivity, and (ii) a scalar-influence win condition replacing Go's territory count. "Place stones, groups die when surrounded" IS Go. Influence fields are widely studied under the "Zobrist influence" / "Benson influence" literature for Go position evaluation. Saying "we replaced Go's endgame scoring with a running total of Zobrist influence on own stones" does not make a new game — it renames it. An intermediate-strength Go player would recognize every move in my Phase 2 games as a standard Go concept (contact play, extension, corner/center tension).

- **vs Hex/Y/Havannah:** No direct match — those games are about connection, not density.

- **vs Reversi/Othello:** Partial match in the "influence propagates" dimension. Othello flips stones based on bracketing; this game *weights* them. But the *race-to-threshold-of-own-value* is a distinct mechanic.

- **vs Gomoku/Pente/Connect6:** No — this game does not reward lines, it rewards clusters. The only shared ancestry is "place-stones-on-a-grid".

- **vs Lines of Action:** No — no movement.

- **vs Tumbleweed / Slither:** Slither rewards connectivity with a twist. Tumbleweed has influence/population mechanics that are actually very close to this game. In Tumbleweed, each cell is claimed by whichever color has the higher line-of-sight count; here each cell's "influence value" is the signed sum of neighboring-stones times decay. **Tumbleweed is the closest analog.** This game is essentially "Tumbleweed on a grid with a threshold trigger and optional Go-capture".

- **vs Life-like CA / Conway-family:** Not a CA — no step rule. Irrelevant.

- **vs Diplomacy / Gungo / simultaneous-Go:** Irrelevant — this game is alternating.

**(b) CA check:** No CA in this game. Skip.

**(c) Simultaneous check:** Not a simultaneous game. Skip.

**(d) Topology/coordinate re-skin:** The Moore-adjacency 8×8 grid can be re-coordinatized as a king-move graph — identical to Chess's king adjacency. Under this relabeling, the game is "Tumbleweed-light on a king-graph with a density threshold". This is a real re-skin — the "novelty" is one knob away from a well-defined existing game family.

**(e) Expert-carryover test:** Would a strong Go player have an immediate advantage? **Yes.** Go intuitions about shape, thickness, keshi/invasion, and liberty-counting translate directly. A Go shodan given 10 minutes to read the rule sheet would play this game competitively against me. That is strong circumstantial evidence it's not a meaningfully new abstract game.

### Player rebuttal:

**Rebuttal 1 (quantitative threshold breaks Go parity):** In Go, the endgame is scored by counting territory, and *every* stone can in principle matter. Here the win condition is a specific numerical threshold on own-cell influence, which means the game has a *race* structure that Go lacks. In Game 1 (moves 1–15) the game was over in 15 moves because the threshold was reached — a Go player trained on 200-move endings has no intuition for a race-to-22.645. This is a meaningful deviation.

**Rebuttal 2 (contact-cancellation is foreign to Go):** Go stones are binary — either yours or captured. Here, two adjacent enemy stones contribute `±0.475` that partially cancel, so *holding* adjacent-enemy-contact costs you. A Go player would read contact plays as territory-neutral "fights" — here, contact strictly *reduces both players' totals*. My Phase 2 Game 2 showed that P1 dominated by avoiding direct contact and extending the free side, which is the opposite of Go principles where contact fighting gains thickness.

**Rebuttal 3 (capture rule is essentially dead in open play):** Go's entire strategic corpus revolves around liberties, ko, seki, life-and-death. Here, Moore-8 connectivity means interior stones need 8 surrounding enemies to capture — functionally impossible in a game that resolves in 15–20 turns. So "this is Go" misses that the game's defining tactic (group life) is absent.

**Rebuttal 4 (Tumbleweed is closer but still different):** Tumbleweed uses line-of-sight population; this game uses radius-1 decay influence. They are related but the mechanics produce different strategic textures. Tumbleweed rewards open lines; this game rewards tight clusters. Not the same game.

### Resolution: Novelty = **4/10**.

- Strongest adversary argument: the game is a numerical-threshold wrapper around Go-with-Moore-adjacency plus Tumbleweed-like influence. A Go+Tumbleweed hybrid player would adapt in minutes.
- Strongest defense: the *race to threshold* plus *contact cancellation* produces a different optimization target (cluster density rather than territory or connectivity). This is a genuine twist but not a deep one.

---

## PHASE 5 — VERDICT

**Team ID:** team-16
**Game ID:** 3bde3258978e
**Rules Summary:** 8×8 Moore-adjacency board, alternating stone placement, Go-style surround capture (effectively inert), radius-1 signed-influence propagation; first player whose own-cell influence sum exceeds 22.645 wins.
**Topology:** 2D Moore (8-connected), non-wrapping, axis size 8.
**Turn Structure:** alternating.

**SCORES (1-10):**

- **Strategic Depth: 3** — The game collapses to a tempo race with one dominant strategy family ("tight cluster, ideally at a corner"). Counter-play exists (invasion) but is dominated. Capture is dead in practice. No ko, no life-and-death, no meaningful sacrifice.

- **Emergent Complexity: 4** — *Cluster density*, *contact cancellation*, and *corner-value bonus* emerge cleanly from rules. But that's the whole list. No higher-order emergence (no tempo exchanges, no shape hierarchies, no territorial patterns).

- **Balance: 3** — Strong first-mover advantage. In 2/3 games P1 won under symmetric play; the only P2 win required P1 to play a deliberately handicapped strategy. Under optimal play I estimate P1 wins ~100%. Seat-swap evidence supports this.

- **Novelty (post-adversary): 4** — Best defended as "Go-with-Moore-adjacency + Tumbleweed-like influence + threshold-race victory". Each ingredient is known; the combination is not exactly published but it's one mutation away from well-known games. A Go/Tumbleweed player adapts in an hour.

- **Replayability: 3** — Once you see the cluster-at-corner strategy, there's little reason to play again. The decision tree is narrow.

- **Overall "Would I play this again?": 3**

**CLOSEST KNOWN-GAME ANALOG:** Tumbleweed (for the influence field) crossed with Go (for the surround capture). Not identical because Tumbleweed uses line-of-sight population counts on hex and this game uses radius-1 decay influence on Moore-grid, and Go lacks the influence-threshold win condition.

**KILLER FLAWS:**
1. **Strong P1 advantage** (~100% under symmetric play) — the key failure mode for an "evolved balanced game".
2. **Capture rule is inert** in typical play due to Moore 8-connectivity (verified: a single interior stone would need all 8 neighbors as enemies to be captured — never happens in 15–20-turn games). Rule adds nothing to strategy despite being listed as a core mechanic.
3. **Dominant strategy (tight-corner-cluster)** narrows the decision tree — the "influence" and "surround" mechanics don't actually interact meaningfully.
4. Note: not a double-pass problem. All games resolved by threshold.

**BEST QUALITY:** The *contact-cancellation* emergent property is actually interesting — having your stones touch enemy stones reduces *both* players' totals simultaneously, creating a "neither-player-wins-the-exchange" dynamic that's different from Go fighting. This is the one genuine strategic texture the game offers.

**IMPROVEMENT IDEAS:** Introduce a **pie rule** (P2 can swap sides after P1's first move) to neutralize first-mover advantage. Alternatively, make the threshold a *combined* target — e.g. "first to reach (own_value − opponent_value) > threshold" — which would make contact cancellation a live strategic lever rather than a mutual-waste situation, and force both players to *both* build *and* invade. A third option: change topology to von Neumann (4-connectivity) to make the capture rule meaningful; right now the declared mechanic is inert.

---

*Evaluation complete. 3 games played, all engine-verified. No double-pass resolutions. Seat-swap executed in Game 3. Novelty adversary rebutted with concrete moves from Phase 2.*
