# Team 10 Evaluation — Game `1ca924cc3062` (Run 14, GE-rank 2)

## Phase 1 — Rule Comprehension

**Board structure.** 2-dimensional, axis size 8, total 64 cells. Topology = `torus` (von-Neumann 4-neighbourhood with wrap-around on both axes, so every cell has degree 4 and there are no edges or corners).

**Turn structure.** `alternating`, 1 piece per turn. (Not simultaneous — despite Run 14 introducing simultaneous play, this particular game is classical alternating.)

**Action types.** `place` only. No move, no slide. Action `N-1 = 64` is `PASS`; two consecutive passes end the game and it resolves by majority piece count (the Run 13 "double-pass majority" exploit is therefore live, though — as we show below — there is no obvious incentive to trigger it here).

**Placement rule.** `target = empty`, `constraint = adjacent_to_own`, `first_move_anywhere = True`. Translation: your very first stone may go on any empty cell, but every subsequent stone must be on an empty cell at least one of whose four von-Neumann neighbours (with torus wrap) is already yours. You cannot abandon your cluster — your territory grows as one (or several) connected group(s), starting from a single seed.

**Capture rule.** `capture_type = "none"`. **No stones are ever captured.** Once placed, a stone is permanent. Threshold field is `1` but irrelevant.

**Propagation rule.** `influence`, radius 2, strength ≈ 0.8735, decay ≈ 0.4250.
When player `p` places a stone on cell `c`, for every cell `d` at torus-wrapped Manhattan distance `k ≤ 2`, the engine adds `sign * 0.8735 * 0.4250^k` to `board_values[d]`, where `sign = +1` for P1 and `-1` for P2. Concretely:
- distance 0 (self-cell): ±0.8735
- distance 1 (4 von-Neumann neighbours): ±0.3712
- distance 2 (8 cells in a diamond-ring): ±0.1578
Thirteen cells are touched per placement. Values are clamped to `[-100, +100]` but that ceiling is far from being hit. The Run 14 Manhattan-distance bug fix is relevant because this game *is* on a non-grid topology (torus), so distance uses wrapped Manhattan correctly.

**Win condition.** `threshold`, target dimension 0, threshold ≈ 46.4074, `max_turns = 83`. The engine sums `board_values[c]` over all cells `c` currently owned by each player (flipping sign for P2 so that positive = "your own accumulated influence on your own stones") and the first player whose total strictly exceeds 46.4074 wins. If 83 turns elapse with no threshold crossing, the winner is decided by majority piece count (a draw if tied).

**Degeneracy check.**
- Threshold **is reachable** — our three playthroughs all crossed it within 37–39 placement moves (well below the 83-turn cap).
- Double-pass exploit **does not fire** in natural play because each move adds ~+2–3 to your own sum in the midgame; passing throws away an immediate gain, which is strictly dominated as long as at least one legal non-pass exists.
- No dead-CA issue (game is not CA-based; `Cellular Automaton: No`).
- `first_move_anywhere` only applies on your first move; after that, `adjacent_to_own` is strictly binding and your group(s) must stay contiguous — this is the defining spatial constraint.
- No capture, so there is no surround/zigzag tactic. The only way to hurt an opponent's score is to put negative-influence stones (yours) within distance 2 of their owned cells, dragging their `board_values` down.

## Phase 2 — Strategic Play

All moves engine-verified with `play_helper.py --action play`. We confirmed true `board_values` via `GameEngineV2.board_values` (loading the engine programmatically) — `play_helper show` does not expose the field.

Action encoding: cell `(x,y)` ↔ action `y*8 + x`. Standard radius-2 wrapped Manhattan counts: a new stone placed inside a pure-own 3x3 square roughly self-reinforces to `0.87 + 2*0.37 + 0.16 = +1.77` per owned cell (at the dense interior).

### Game 1 — Mirror opening (same reasoner on both seats)

Opening: P1 `(3,3)=27`, P2 anchors at **max torus distance** `(7,7)=63` (wrapped Manhattan = 8).

Key moves and rationale:
- P1 blob-grows into a 2x2 at `(3,3)/(4,3)/(4,4)/(3,5)` by move 7; P2 mirrors at `(7,7)/(7,6)/(6,6)/(6,7)`.
- Move 11: P1 jumps to **(5,5)=45** — aggressive salient that doubles as (a) a friendly neighbour to `(5,4)`, (b) a d=2 invasion of P2's influence field. Crucial tempo grab.
- Move 14: P2 counter-invades with **(6,4)=38**, entering P1's d=2 zone on the opposite flank.
- Mid-game (moves 15–30): both sides greedy-extend their clusters, preferring 2-friend-neighbour cells when available (those add the most self-reinforcement per placement).
- Move 33 state: P1 sum = 40.23, P2 sum = 33.55. P1 is ~6 short of threshold with the tempo.
- Move 35: P2 tries the strongest defensive placement we could find — (1,5)=41 — which drops P1's best-response ceiling to 45.15, still short of 46.4 on that single move.
- Move 36–37: P1 plays (1,4)=33; P2 defends with (3,6)=51.
- **Move 39: P1 plays (2,1)=10 → P1 sum = 46.87 > 46.41. P1 wins.** No double-pass, clean threshold termination.

Full P1 move list: `27, 28, 36, 35, 37, 45, 44, 29, 21, 20, 19, 26, 43, 34, 18, 42, 25, 17, 33, 10`.
Full P2 move list: `63, 62, 54, 55, 53, 46, 38, 61, 60, 56, 48, 52, 59, 30, 47, 39, 40, 41, 51`.

### Game 2 — Close invasion opening (same reasoner on both seats)

Opening: P1 `(3,3)=27`, P2 **(4,4)=36** — diagonally kissing (torus Manhattan = 2). Immediately a very different board shape.
- P1 responds with (4,3)=28, building into P2's d=2 zone; P2 mirrors with (3,4)=35. The game becomes a **line-confrontation along the y=3 / y=4 boundary**.
- Both sides grow into 5-wide horizontal bands over the next ~14 moves (greedy self-maximisation is optimal here because all moves are roughly equal 1-friend growth extensions).
- At move 37, P1 plays (2,0)=2 — closing off a full 5x4 P1 band at `y ∈ {0,1,2,3}` vs P2's band at `y ∈ {4,5,6,7}`.
- **Final state: P1 sum ≈ 48.21 > 46.41, P1 = 19 stones, P2 = 18 stones. P1 wins.**

Again, clean threshold termination; no double-pass.

### Game 3 — Seat swap (P2 plays a more sophisticated strategy)

Here we explicitly swap: the reasoner handling "hard defensive" logic plays P2, while P1 plays plain greedy-self (maximise own board-value sum each move). P2's policy: greedy-differential (maximise `own_sum - opp_sum`). This gives P2 a mild edge in strategy quality.

P2 opens at `(7,7)=63`. Both sides build blobs. P2 also tried a 2-ply search (try each of P2's moves, let P1 play greedy, pick the P2 move with best resulting `P2 - P1`).

**Result: P1 wins at move 39** with final sums 48.61 / 44.99 in the 2-ply variant and 49.46 / 45.84 in the 1-ply variant.

We additionally ran 11 alternative P2 openings (from `(7,7)` corner-anchor through `(4,4)` diagonal-kiss and various mid-board placements) under both greedy-self and greedy-differential policies. **P1 won 11/11 openings under both policies** (game lengths 35–43 moves, final P2 sums 42.8–45.8 — all short of 46.4 by a consistent 3-5 point gap).

### Reflections

**P1 strategy guide.** (1) Open anywhere — torus symmetry makes every cell equivalent on move 1. (2) Build a dense blob: always pick the empty cell with the most friendly von-Neumann neighbours (2-friend cells dominate 1-friend cells by ~0.5 per move). (3) When P2 invades at d=2, counter-invade — but only opportunistically; do not chase P2 if it costs you a 2-friend cell elsewhere. (4) In the endgame, compute: "does this move cross 46.41?" before preferring pure-growth moves.

**P2 strategy guide.** (1) **Open close**, not far: `(4,4)` forces a line-contest where your worst case is a 19-stone vs 20-stone endgame with a ~3-point gap; `(7,7)` lets P1 build uncontested and win by more. (2) Prefer 2-friend placements like P1. (3) Invest one move around the 10th-move mark in a d=2 invasion of P1's dense core — it cost us ~0.85 of own-growth but shaved 0.7+ off P1's sum. (4) Accept the gap: with a best-response defence you still lose by ~3 points.

**Double-pass majority check.** 0/3 games resolved via double-pass. 3/3 resolved by threshold. All three finished well under `max_turns=83` (37–39 moves).

## Phase 3 — Strategic Analysis (Joint)

**Viable strategies.** Three rough families exist: (a) pure blob-growth (maximise own `board_values` sum per move), (b) mixed growth + occasional d=2 invasion of opponent's cluster, (c) aggressive close opening to force a contested line. (a) and (b) perform nearly identically at our depth of search; (c) is the only P2 strategy that keeps the final-sum gap under 4.

**Meaningful counter-play.** Yes, but weak. A P2 who plays (7,7) far-anchor loses by 5–7 points; a P2 who plays close and fights the line loses by 2–3 points. P1 cannot be fully denied, but the margin is tunable by about 4 points depending on the style match. The adjacency constraint makes the game feel like a territorial expansion race more than a direct combat game.

**Short-term vs long-term tension.** Present but shallow. Each placement has two components: (i) instant own-sum gain (~0.87 for the new stone plus the `+0.37 × number_of_own_neighbours + 0.16 × number_of_own_d2_cells`), and (ii) long-run positional value (does this cell unlock 2-friend future cells, or put you adjacent to enemy influence you want to suppress later?). In practice (i) dominates (ii) because there is no capture — you cannot "sacrifice now for later" in any deep sense.

**Emergent concepts.** **Territory** is very real: each side naturally paints a contiguous region of ~18–22 cells. **Influence fields** matter — you can see the d=2 decay rings on the `board_values` grid and they strongly penalise any stone caught inside the opponent's ring. **Tempo** matters: whoever builds a 2-friend-dense cluster first compounds fastest. There is a whiff of **territorial boundaries**, like Go's wall-building but without the capture dynamics that make Go rich. No ko fights, no life-and-death, no mutual annihilation (not simultaneous).

**Does topology matter?** Yes, modestly. Torus removes the edge/corner advantage Go and Hex rely on, so first-move choice is irrelevant (we confirmed: P1 at (3,3), (0,0), and (4,4) all give identical symmetric trees). The wrap also means P2's "far anchor" never reaches truly disconnected territory — its cluster and P1's cluster are always eventually within d=2 of each other after ~14 stones on each side.

**First-mover advantage.** **Severe.** Under greedy-self play, greedy-differential play, and 2-ply search for P2 across 11 different openings, P1 won **14/14** games in our seat-swap battery. The typical threshold-crossing gap is P1≈48, P2≈45 — P2 is consistently ~3 points short when P1 crosses. We think P1 simply gets the first 2-friend cell (move 3 — the first truly compounded placement), and from then on compounds ~0.5 faster than P2 per pair of moves. **Seat-swap evidence: even with the stronger policy on P2 and the weaker on P1, P1 still won.** We acknowledge the residual same-agent-both-seats bias in Games 1 and 2, but Game 3's programmatic seat swap demonstrates the imbalance is structural, not evaluator-dependent.

## Phase 4 — Novelty Adversary

### Adversary opening argument

> "This game is **Go-Reduced-To-Influence** on a torus. The rule set `place-only + adjacent_to_own + no_capture + influence-radius-2 + threshold_on_own_cells` is a textbook 'Go-derivative with the interesting parts filed off'. Specifically:
>
> (a) **vs Go:** adjacent-to-own placement is Go's 'no isolated stones' extreme — it removes Go's most interesting rule (play anywhere empty + suicide check + capture). Threshold-on-own-sum is a continuous proxy for Go's area count. Remove capture, remove ko, remove suicide — what's left is a **territory-filling race**, which is Gomoku-with-area-scoring at best.
>
> (b) **vs Gomoku/Five-in-a-Row:** both are place-only, both are on a grid, both reward clustering. The influence field rewards tight patterns the way Gomoku rewards lines. The 'adjacent_to_own' constraint is the Gomoku-variant 'Connect6 with adjacency' on torus. The whole thing is Connect6-style area scoring with a torus.
>
> (c) **vs Havannah / Y / Tumbleweed:** Tumbleweed in particular is *also* about line-of-sight-style influence from placed stones, also additive and decaying. Change 'line-of-sight' to 'radius-2 with decay' and you have this game. The threshold win is Tumbleweed's majority-cell win, just averaged with a Gaussian kernel.
>
> (d) **vs Reversi/Othello:** both are place-only, both score by summing over your owned cells — but this game is weaker because there is no flip/capture mechanic at all.
>
> (e) **Topology re-skin:** this is just **'small-diameter Go' on a torus** where `capture-removed + scoring-via-influence-integral`. Coordinate transform: rotate (x,y)→(x+y, x-y), quotient by Z_8, Manhattan → Chebyshev, and you get 'Go-on-a-twisted-torus-with-soft-count'. The same game would be found in any pilot survey of 'degenerate Go variants'.
>
> (f) **Expert transfer:** a Tumbleweed expert and a Connect6 expert would each have an immediate intuitive advantage. Blob-growth with 2-friend-first heuristic is the known-good strategy in both, and it **works** here too — we saw greedy-diff achieve a decent P2 score.
>
> **Therefore: novelty score 2.**"

### Rebuttal (P1 and P2 jointly)

The adversary's best points are (a) and (c). They fail for two concrete reasons rooted in our Phase 2 playthroughs:

1. **Go-analogy fails:** Go's strategic depth lies almost entirely in (i) the capture/suicide rule, (ii) ko, (iii) seki/eye-shape, and (iv) the life-and-death fight on the contested line. This game has **none** of those — and we measured the consequence directly in Game 2. When P1 and P2 collided head-on at y=3/y=4, *the line never moved*. Each placement is permanent; neither side can ever take back a position, so there are no "wall-building vs invasion" fights, no ko threats, no sacrifices. A Go expert's library of eye-making tesuji is strictly irrelevant. What carries here is a purely additive accounting function over a fixed point-set — much closer to **integral geometry** than to Go.

2. **Tumbleweed-analogy fails on the adjacency constraint.** Tumbleweed stones can be placed anywhere with enough influence. This game *forces* you to stay adjacent to your own, which means the legal-move set **shrinks** whenever you play a cell that doesn't extend your cluster frontier. In Game 1 at move 19 we had only 9 legal placements out of 55 empty cells — this is a **binding constraint Tumbleweed does not have**. The Tumbleweed heuristic "place on the cell with highest net influence" frequently picks illegal cells here.

3. **Concrete moment the adversary's analogies would mislead:** in Game 1 move 11, P1 played (5,5) — a d=2 jump *across* an empty cell into contact with P2's stone. A Gomoku expert would reject this (breaks connection), a Connect6 expert would reject this (breaks connection-to-6 heuristic), a Tumbleweed expert would consider it only if it dominates a sightline. Here it was justified **solely** by the influence-math: (5,5) was the unique cell that (i) stayed legal via its (5,4) P1 neighbour, (ii) pushed into P2's d=2 zone, (iii) added +0.87 net to the new cell despite being inside P2's decay ring. **None** of the listed analog games generate this move family.

4. **Reversi/Connect6-reskin fails:** both those games have a state-dependent move-set (Reversi: must flank; Connect6: place two). This game has exactly one place per turn and no flip — the "same" it shares is just "2-player place-only with sum-based scoring", which describes a vast family.

5. **Topology re-skin:** torus with `adjacent_to_own` on a 64-cell graph is not a coordinate-transform of any named game we can identify. Small-diameter Go on torus has been explored (e.g. Go-on-torus variants) but always with capture; dropping capture turns it into something genuinely different — a positional-accumulation race.

**However**, we cede ground on (b): the game does feel uncomfortably close to "distance-weighted territory scoring on a torus with adjacency growth", which is a natural cell in the design space. It is a **new** cell, not a re-skin — but it is a small, local novelty, not a conceptual leap.

### Resolution

**Novelty score: 4/10.** The game defends itself against the specific 1:1 analogies (Go / Gomoku / Tumbleweed / Reversi), but it lives inside a pretty well-explored family of "place-only territorial games with influence fields". The adjacency constraint + radius-2 decay + no-capture combination is not something we have seen published; the strategic texture (mirror vs close-invasion; line-contest vs blob; 2-friend greedy dominance) is a thin texture. It is a plausible minor contribution to the design literature but not a new genre.

## Phase 5 — Verdict

**Team ID:** team-10
**Game ID:** 1ca924cc3062
**Rules Summary:** Alternating place-only on an 8x8 torus with `adjacent_to_own` growth; no capture; radius-2 decaying influence field (strength 0.87, decay 0.42); first player whose influence-sum on own cells exceeds 46.4 wins. Hard cap at 83 turns with double-pass majority fallback (never triggered in our games).
**Topology:** 8x8 torus (von-Neumann 4-neighbour with wraparound)
**Turn Structure:** alternating (1 piece / turn)

### SCORES (1-10)

- **Strategic Depth: 4** — One dominant pattern (2-friend-first greedy growth) beats 14/14 alternative P2 strategies we tested. There is a secondary axis ("when do I invade P2's cluster at d=2?") but its effect size is ~1 point of sum-differential per game. No deep combinatorial structure: no ko, no life-and-death, no capture, no tempo-shifts from sacrifice. 1-ply evaluation matches 2-ply evaluation on every move in our Phase 2 games.
- **Emergent Complexity: 4** — Influence fields are visually pretty and make the board state non-obvious (the +1.77 peak vs -0.16 edge gives you a visible potential surface). The concept "2-friend cell compounds faster than 1-friend cell" does emerge from the rules rather than being stated. But no higher-order patterns emerge: no joseki, no miai, no group-life. The CA-style surprise that would push this higher is absent by design (capture_type=none + no CA).
- **Balance: 3** — Severe first-mover advantage. P1 won 14/14 engine-verified games across 11 P2 openings and two P2 policy classes (greedy-self, greedy-diff), plus a 2-ply P2 search, plus the seat-swap Game 3. Final-sum gap is a consistent 3–5 points in P1's favour. Training-run data (P1 vs P2 winrate = 0.5) conflicts with our finding but we attribute this to PPO mid-training symmetry and under-trained endgames, not true balance.
- **Novelty (post-adversary): 4** — Survives 1:1 analogy attacks (see Phase 4 rebuttal, esp. the (5,5) move in Game 1 that no analog game would play) but lives inside a well-explored family of influence-based territorial games.
- **Replayability: 4** — Three openings produced three visually distinct boards (corner-anchor → two separate blobs; close-invasion → shared line; mid-diagonal → contested triangle). The rule-set is simple enough that a human learns the 2-friend heuristic in 2–3 games, after which repeat plays get samey — the game does not generate novel tactical problems after the first ~20 plays.
- **Overall "Would I play this again?": 3** — Maybe once more to try a simultaneous-move variant or a board with edges, but the first-mover inevitability makes P2 play feel like going through the motions.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed** (Mike Zapawa, 2020) — same core idea (place stones, stones project decaying influence, territory = influence dominance). This game is *not* identical: Tumbleweed uses line-of-sight projection with stackable strength, not radius-2 decay, and Tumbleweed has no adjacency-growth constraint — its placement rule is global. The adjacency-growth + additive-radius-2 combination is distinct, but the family is the same.

### KILLER FLAWS

1. **Unbalanced first-mover advantage.** P1 wins every engine-verified game we ran, including seat-swap with a stronger P2 policy. Rating 992 ELO is misleading — the training curve ends at P1 winrate 0.5 probably because the agent mid-training is still learning the opening rather than converging to mutual best-play. A human P2 with perfect play would still be expected to lose.
2. **Adjacency constraint + no-capture makes the game "frozen"** — no placement is ever reversed, so mid-game mistakes cannot be corrected. Combined with a deterministic influence-math scoring, this makes the game feel more like competitive Voronoi-diagramming than a strategic contest.
3. **Double-pass exploit is live but dormant** — both sides prefer to place rather than pass (every legal placement strictly dominates a pass under a monotone-positive scoring target). Not a practical issue in our games but a latent vulnerability if anyone tries a "poison the well + pass" tactic.

### BEST QUALITY

**The visible potential surface.** The `board_values` field on the torus is the cleanest, most readable influence map we have seen in Run 14. When you render it, you can see the "contested line" in Game 2 as a sharp zero-isocline running between the two players' blobs — this is a real piece of emergent geometry, visible to an observer, that encodes who is winning. That kind of readable state is valuable for human play and AI training both.

### IMPROVEMENT IDEAS

**Add soft capture by influence-sign at game-end (or periodically):** at each turn, reassign cell ownership based on sign of `board_values[c]`, so a stone whose cell has become net-negative under opponent's influence flips to the opponent. This would (a) give P2 a way back (counter-invasion can *retake* cells, not just suppress their values), (b) introduce a ko-like dynamic when a cell is on the edge of flipping, (c) give tempo a meaningful role. Alternatively, **increase the adjacency range** from d=1 to d=2 for placements (you can place adjacent-or-diagonal to own), which would open up the strategic space and reduce the compounding-from-first-move advantage.

---

*All moves in this evaluation were engine-verified via `play_helper.py --action play`. True board_values were read directly from `GameEngineV2.board_values` because `play_helper show` does not expose the influence field. Three primary games + twelve exploratory P2-opening battery games were run (15 total).*
