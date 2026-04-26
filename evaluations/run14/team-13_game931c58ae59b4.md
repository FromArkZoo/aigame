# Team-13 — Evaluation of Game `931c58ae59b4` (Run 14, rank 3 by GE 0.4824, ELO 3035)

Evaluator: team-13 (single-agent, three-role sequential with seat-swap in Game 3)

## Phase 1 — Rule Comprehension

**Board.** 8×8 grid, 64 cells. Topology type is declared `moore`, which in this engine means **8-neighbour (king/Chebyshev) adjacency**. (Note: `play_helper.py rules` prints "von Neumann" for Moore — that description string is misleading; confirmed the effective adjacency is 8-neighbour by checking the legal-action set after a first move and by reading `topology.py::_build_moore_neighbors`.)

**Turn structure.** **Alternating**, one placement per turn. Not simultaneous.

**Action types.** Placement only. Action 64 = PASS. Two consecutive passes end the game by piece-count majority. Action IDs 0–63 encode `y*8 + x`.

**Placement constraint.** Empty target, `adjacent_to_own` — after your first move (which can be anywhere), every subsequent stone must touch one of your own stones under Moore adjacency (so 8-neighbour). First stone is exempt (`first_move_anywhere=true`).

**Capture rule.** `surround`, threshold 1. Standard Go-style group capture: any group with zero liberties (empty adjacent cells under Moore) is removed. In practice with +dense clustering strategies neither side gets captured in my 3 games — capture was never triggered.

**Propagation.** `influence`, radius 2, strength 1.6155, decay 0.4616. Every placement adds signed contributions to `board_values` on all cells within Chebyshev distance 2:
- distance 0: +1.6155
- distance 1: +0.746
- distance 2: +0.345
Sign is + for P1, − for P2. Values clamp to ±100.

**Win condition.** `threshold` on dimension 0. Sum `board_values[c]` over all cells c owned by player P; flip sign if P==2; if that effective sum > **63.46**, player P wins. Max turns = 100.

**Non-degeneracies observed.**
- Threshold is reachable: a tight ~3×3 block of 10–12 stones gets each cell ~+5 to +7 of stacked influence, so total effective sum crosses 63.46 at 10–12 stones. Games converge at turns 21–23 in my play, far inside max_turns.
- Double-pass exploit: NOT triggered in any of my games; the threshold is reached first. No player would voluntarily pass unless already winning by piece count, and a pass costs tempo in the influence race.
- Capture rule is effectively dormant under rational play — groups in cluster formations have many internal liberties. Still, a mis-extended single stone could be captured; engine-verified it's not broken.
- No CA rules (classic mechanics).
- The Manhattan-distance-bug fix in Run 14: this game uses Moore distance = Chebyshev, which the radius-2 neighbourhood walks; behaved as expected. No anomalies.

## Phase 2 — Strategic Play

Single-agent played all three roles sequentially; seat-identity bias acknowledged. Every move engine-verified via `play_helper.py ... --action play` and independently via a helper that prints `effective` sums (P1 total on own cells vs −P2 total on own cells).

### Game 1 — P1 center opening, P2 contests

Moves: `27, 36, 28, 45, 35, 44, 19, 43, 26, 52, 18, 53, 20, 37, 11, 54, 10, 46, 9, 38, 17, 29, 25`

P1 opened center (3,3)=27; P2 contested diagonally at (4,4)=36. From move 3 both players grew L-shapes and then 2×2 blocks in opposite quadrants. Influence was almost perfectly balanced after every pair of moves (P1=4.62, P2=4.62; P1=8.12, P2=8.12; …). The key observation: **each player's choice of highest-density move is near-symmetric, so the game is a pure tempo race.** P1's tempo (one extra move per cycle) is the decisive factor.

Critical moments:
- Move 20 (P2 plays 38=(6,4)): briefly overtook P1 on effective influence (51.5 vs 49.3). P2's (6,4) touched 2 existing P2 stones AND put negative influence on P1's border cells.
- Move 22 (P2 plays 29=(5,3)): took lead again 57.5 vs 56.8.
- Move 23 (P1 plays 25=(1,3)): 4-P1-neighbour spot, effective jumped to 66.66 > 63.46. P1 wins on threshold.

End: 12 P1 stones, 11 P2 stones, turn 23, threshold win (not double-pass).

### Game 2 — P1 corner opening, P2 center

Moves: `10, 27, 9, 36, 17, 35, 18, 44, 25, 43, 26, 34, 19, 28, 11, 42, 33, 51, 24, 52, 16, 45, 8`

P1 played (2,1)=10 (near-corner); P2 took center (3,3)=27. Pattern mirrored Game 1 with P1 building a NW block and P2 building a SE block. Several inversions: after move 18 P2 led 37.66 vs 36.17; after move 20 P2 led 45.81 vs 44.32; after move 22 P2 led 55.00 vs 54.31. Each time a 3-neighbour placement swings ~+7. P1 closed with move 23 = 8=(0,1), a 3-P1-neighbour spot → 63.85 > 63.46.

End: 12 P1 stones, 11 P2 stones, turn 23, threshold win (not double-pass).

### Game 3 — Seat swap (this agent played the "opposite" frame for each side)

Moves: `45, 18, 46, 9, 54, 10, 53, 17, 52, 19, 44, 11, 61, 26, 60, 25, 62, 27, 51, 16, 59`

P1 opened (5,5)=45, P2 responded (2,2)=18 — spatially symmetric opposite corners. Both built near-mirror 3×3 clusters, with numerical parity after almost every paired move (eventually tied at 62.51 just before P1 closed). P1's turn-21 push 59=(3,7) exceeded threshold (71.35).

End: 11 P1 stones, 10 P2 stones, turn 21, threshold win (not double-pass).

### Per-side reflections

**Player 1 strategy guide.**
1. Open anywhere central-ish; slight off-center (not the corner) is fine because the first move is free (first_move_anywhere) — but corners lose only 3/8 of the radius-2 region, so they're only slightly worse.
2. Pack density. The fastest per-move gain comes from placements with ≥3 own-colour Moore neighbours (new-cell self-value 1.615 + 0.746 × 3 = ~3.85), plus the cross-boost you give each of those 3 neighbours (0.746 each). That's ~+7 effective per such move. 1-neighbour extensions are half that.
3. Avoid invading the opponent's dense zone unless it both reduces their total (by placing own-colour on a cell near their stones) AND builds density for you. Usually your own cluster has better ratios.
4. Don't pass. Passing is strictly losing unless you have the threshold.

**Player 2 strategy guide.**
1. Treat P1's first move as orientation. Place at maximum Chebyshev distance ≥ 4 from it so your radius-2 influence doesn't overlap theirs. (Overlap wastes influence on cells the opponent's stones cover — which won't count towards either threshold.)
2. Strong countermove: play a cell that is (a) dense relative to your cluster and (b) near the opponent's border so negative influence subtracts from *their* effective sum on cells they own.
3. P2 is typically 1 move behind P1 in the tempo race — you must squeeze every density advantage to close the gap before P1 hits 63.46.
4. Passing is a trap; never pass before threshold.

**Did opponent surprise me?** Yes — the P2 "invasion near own cluster edge" plays (moves like (6,4), (5,3), (2,4)) repeatedly flipped the lead. Net: P2 is very close to parity, not crushed.

**Double-pass check.** 0/3 games ended by double-pass. All 3 resolved via threshold. No degeneracy observed on this axis.

## Phase 3 — Strategic Analysis (joint)

**Distinct strategies?** Two archetypes emerged:
- **Own-cluster maximiser.** Every move goes to highest-density own spot. Pure greedy on effective sum.
- **Edge-invader.** Some moves placed at the border between the clusters to both build own density AND subtract from opponent's effective sum via negative influence on their cells.

Under optimal-ish play they converge: the edge-invader is strictly better when a legal move gives both benefits, and when that's unavailable the maximiser move is the same. So there's really one dominant strategy family with a decision rule ("play the move that maximises (your delta) − (opponent's delta)"). This is narrower than it first appears.

**Counter-play.** Yes, but weak. The main counter is ordering: you choose *which* dense spot to take now vs. later, robbing future moves from the opponent when clusters contact. In the endgame (turns 15+) you can plan 2 moves ahead to see which pair of cells together pushes over threshold first. But there's no "style counter" — no zugzwang trick or sacrifice-for-later trick I could find.

**Short-term vs long-term tension.** Minimal. The game rewards immediate density; I found no move where sacrificing short-term for long-term paid off. Capture never triggered in rational play, so there is no ko, no life/death, no seki analogue. This is a significant gap vs Go.

**Emergent concepts.** Two clear ones:
- **Tempo in a race to threshold.** The first-to-threshold dynamic gives tempo a very clean meaning. Unlike Go territory, it's a strictly cumulative numeric race.
- **Density economics.** The decay 0.462 radius 2 profile gives clean convex returns on clustering: each additional neighbour in your Moore ring is worth a known ~+0.75, and each mutual own-pair double-counts that bonus. This is visible in play; I computed move EVs on the fly.

Notably **absent**: territory, influence sacrifice, life-and-death, initiative reversal, ko.

**Topology matters?** Slightly. Moore adjacency (8-neighbour) makes 2×2 blocks very efficient (each stone has 3 own neighbours); von-Neumann would have made the race slower and more linear. But there's no topological subtlety (no hex/torus wrapping tricks). Corners/edges are mildly worse for density.

**First-mover advantage.** Strong. P1 won **3/3** games (two with the same agent reasoner, one with seat-swap). Every game converged at P1-stones = P2-stones + 1. With identical dense-play heuristics for both sides, the first-mover tempo is decisive — P2 is always one density-move behind. Seat-swap Game 3 didn't rescue P2; P1 still won because tempo trumps style.

**Acknowledged bias.** Single-agent sequential play means the "novelty" of each move is shared across both sides. Inter-team triangulation is the proper balance check. But the tempo argument above is structural — I expect other teams to see P1 dominance too.

## Phase 4 — Novelty Adversary (mandatory)

### Adversary's attack

The adversary argues this game is **not meaningfully novel**.

(a) **Against known abstract games.**
- **Go.** Same board size range, same Go-style `surround` capture with liberties, same placement mechanic, same ko hash detection (super-ko). The *only* deltas are (i) Moore instead of von Neumann adjacency, (ii) `adjacent_to_own` placement restriction, (iii) the win condition is a weighted-influence threshold rather than territory. It is **Go on Moore with a restricted-placement rule and a numeric-win-threshold overlay**. Every ingredient has a clear Go counterpart.
- **Gomoku/Pente.** Placement-only on 8×8 with an influence-region goal is structurally Gomoku-ish; the influence radius-2 just generalizes the "5-in-a-row" line to a 5×5 disk.
- **Reversi/Othello.** No flipping, but the "sum of influence on your discs" win condition is close in spirit to Othello's final-count mechanic, lifted from piece count to radius-2 weighted sum.
- **Tumbleweed.** Tumbleweed on hex uses a placement+influence+threshold win condition — this is functionally isomorphic except on Moore with adjacency constraint.

(b) **No CA.** Not applicable; classic mechanics.

(c) **No simultaneous play.** Not applicable.

(d) **Topology re-skin hypothesis.** The game is structurally **"Tumbleweed-style influence-threshold Go on an 8×8 Moore board with adjacent-to-own placement"**. The transformation is: start with generic Go, add (a) Moore adjacency, (b) `adjacent_to_own` placement restriction (similar to Havannah/Y "connection"-style placement hints), (c) replace Go's territory-counting with a decayed-influence numeric threshold.

(e) **Expert transfer.** A Tumbleweed expert would transfer *most* intuition to this game: "cluster your high-value cells, subtract opponent's reach near theirs, tempo matters". A Go expert would transfer cluster-density intuition and liberty awareness. Neither expert would be lost.

**Adversary's verdict.** Novelty ≈ 2–3 / 10: a re-parameterization of Tumbleweed/Go-with-influence. The specific numeric constants (threshold 63.46, strength 1.615, decay 0.46) are a dial-twist, not a new mechanic.

### Rebuttal (P1 + P2, citing Phase 2 moments)

The adversary is right that no single mechanic is unprecedented — but the adversary overstates the Tumbleweed analogy. Specific rebuttals from play:

- **Against Go.** In Go, capture and territory are primary; in this game, capture never fired in 3/3 games. The strategic loop is numeric-race-to-threshold, not life-and-death. A Go expert's reading-deep-for-life skill is dead-weight here. Game 1 move 20 (P2's (6,4)) and Game 2 move 18 (P2's (5,6)) show: the winning plays are *influence-arithmetic* choices, not Go-reading choices — you're computing ∆effective, not life/death.

- **Against Gomoku/Pente.** Placement is not n-in-a-row; there is *no* line-reading. All 3 games ended with square-ish blobs, not lines.

- **Against Othello.** No flipping; the captured-piece dynamic is absent. Density economics, not edge-bounding corner strategy, dominates.

- **Against Tumbleweed.** Closest match, but Tumbleweed uses stacked tokens on hex with a visibility-based influence (line-of-sight); this game uses planar decayed kernel on a Moore square with adjacent-to-own placement. These are genuinely different: in Tumbleweed you *cap* heights by visibility; here you build blobs bounded only by opponent presence. In Game 3 both sides built mirror 3×3 blobs in opposite corners with zero capture and zero visibility — a Tumbleweed player would look for the visibility levers and find none.

- **The `adjacent_to_own` constraint** specifically is not present in Go, Othello, or Tumbleweed. It enforces **connected growth**, which converts the game into a directed expansion problem, with a first-move placement that sets your *only* anchor. This is a non-trivial rule-space point: it is Havannah-like in requiring connection, but Havannah wins by bridge/ring/fork and has no influence numerics.

- **Mutual dense clustering** with no capture and no flipping produces a tempo race that doesn't exist in any of the named games. The numeric moments from Phase 2 (scores flipping within 1–2 points across 8+ consecutive half-moves) show a race structure more like a competitive-programming-style optimization game than a classical board game.

**Joint novelty score (post-adversary): 4/10.**

Rationale: each individual mechanic is known (Go capture, influence propagation, threshold win, adjacent growth). The specific *combination* plus the `adjacent_to_own` + threshold + Moore-decay numeric envelope isn't a re-skin of any single classical game. But it also lacks emergent properties absent from the closest ancestor **Tumbleweed-plus-Go-capture**; there is no new idea here, just a tuned composition. Not a re-skin (would have been 2). Not emergent (would have been 7+). Sits at 4.

## Phase 5 — Verdict

**Team ID:** team-13
**Game ID:** 931c58ae59b4
**Rules Summary:** 8×8 Moore-adjacency Go-like placement game with `adjacent_to_own` constraint, radius-2 decayed influence propagation, standard Go liberty capture, and a win condition of effective influence sum on own cells exceeding 63.46. Alternating turns, max 100 turns.
**Topology:** 2D 8×8, Moore (8-neighbour Chebyshev) adjacency.
**Turn Structure:** Alternating.

### Scores (1–10)

- **Strategic Depth: 4/10.** Single dominant strategy (maximise own density, minimise opponent's on contested edges). No life/death reading. Capture rule effectively dormant. Tempo race with clean arithmetic; move choices are usually within 1–2 candidates of a greedy optimum.
- **Emergent Complexity: 3/10.** The only emergent concept is "density economics" with a cross-influence bonus — measurable but not surprising given the parameters. No ko, no sacrifice, no life/death emerged in any game. The game is essentially solved by convex-greedy cluster growth.
- **Balance: 3/10.** First-mover P1 won **3/3** games, including Game 3 with seat-swap. Final piece counts: 12–11, 12–11, 11–10 — P1 always placed the last pre-threshold stone. There is no komi-equivalent to offset P1 tempo. Seat-swap was imperfect (same reasoner) but the tempo argument is structural and I expect other teams to see the same P1 dominance.
- **Novelty (post-adversary): 4/10.** Strongest adversary argument: "Tumbleweed with Go capture on Moore, minus visibility, plus adjacent growth — parameter-tuned composition of known parts." Strongest rebuttal: the `adjacent_to_own` + decayed-influence + threshold combination is not equivalent to any of Go, Tumbleweed, Othello, Gomoku, Havannah individually; an expert in any one of them transfers only partial intuition. But the combination is additive, not emergent. Settles at 4.
- **Replayability: 3/10.** With density-economics as the dominant heuristic and tempo as the decisive factor, two reasonable players will produce very similar games (my Games 1 and 3 ended nearly identically). Opening variation changes which quadrant clusters form in, but the tempo arithmetic is invariant.
- **Overall "Would I play this again?": 3/10.** Quick to learn, computable by hand, but narrow once understood. Not bad as a teaching game for influence + decay mechanics; not a game I'd play for entertainment.

### Closest Known-Game Analog
**Tumbleweed + Go capture on an 8×8 Moore board, with the `adjacent_to_own` growth rule from connection games like Havannah, and a decayed-influence threshold win.** It is not identical because (a) no visibility/line-of-sight mechanic from Tumbleweed; (b) no territory scoring from Go; (c) no connection-win from Havannah; (d) Moore adjacency instead of hex; (e) the explicit threshold number (63.46) is a game-defining parameter rather than a decision-time-count. But the intersection of these borrowings is narrower than any single ancestor claims.

### Killer Flaws
- **Strong first-mover advantage.** 3/3 seat-independent wins for P1, with no komi mechanism. Given the pure tempo race, this is structural not accidental.
- **Capture rule is dormant.** In rational dense-cluster play, groups always have enough liberties. `surround` + threshold-1 + `adjacent_to_own` pushes both sides into compact blobs; the capture rule contributes almost nothing.
- **Opening choice near-inconsequential.** First-move location shifts which quadrant your blob lives in, but not who wins or by how much. Games 1 (P1 (3,3)), 2 (P1 (2,1)), 3 (P1 (5,5)) all followed the same tempo arc.
- **Greedy-myopic exploit.** A simple "play the move that maximises (my effective Δ − opponent's effective Δ)" is very close to optimal. I used this in the endgame of Game 3 and found the winning move without deeper search.

### Best Quality
**Transparent, hand-computable influence economics.** The radius-2 decayed kernel makes every move score-able on the fly; players actually see *why* a move is worth +7 effective vs +4. This is pedagogically clean and makes the game a decent explainer for "influence" as a concept without Go's life/death opacity. It has real aesthetic value as a simplification.

### Improvement Ideas
Pick one of:
1. **Add a komi-equivalent.** Subtract a fixed offset (e.g. 2.0) from P1's effective sum at the threshold check. With current play, this might flip ~1/3 of games to P2, closing the balance gap.
2. **Change placement constraint from `adjacent_to_own` to `not_adjacent_to_own`** (like Y's edge rule) or alternate constraint that forbids neighbour-stacking. This would kill the dense-cluster-greedy exploit and force distributed placements, which would interact non-trivially with the radius-2 kernel and probably create actual positional tension.
3. **Make the threshold decrease over turns** (e.g. threshold = 63.46 − 0.3·turn). This creates both a strategic deadline and makes passing vs playing meaningfully trade-off.

Of these, (2) is the most interesting game-design lever; it would produce a fundamentally different game from what this is. The GE rank 3 rating (0.4824) seems to me generous given the greedy-solvable nature — this is a rank-5-or-lower game in strategic terms, though the clean numeric exposition is a fair reason for the GE heuristic to like it.
