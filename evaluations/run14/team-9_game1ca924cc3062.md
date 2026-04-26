# Team-9 Evaluation — Game `1ca924cc3062` (Run 14, GE rank 2)

**Team ID:** team-9
**Game ID:** 1ca924cc3062
**Generation:** 7 (parent 6dcb11f4b352)
**GE score:** 0.5000 · **Strategic Depth metric:** 0.7790 · **ELO:** 992.8
**Training run final winrate (p0 vs p1):** 0.50 (both seeds)

---

## PHASE 1 — Rule Comprehension

**Board / Topology.** 2D, `axis_size=8`, `topology_type=torus` → 64 cells, edges wrap in both axes. 4-neighbour (von Neumann) adjacency was empirically confirmed: from (3,3) the only neighbours are (2,3),(4,3),(3,2),(3,4) — no diagonals.

**Turn structure.** **Alternating**, one piece per turn. `turn_structure.turn_type = "alternating"`. This game does **NOT** use the Run-14-new simultaneous mechanic — flagged because Run 14's advertised novelty is sim-play, but this rank-2 game is classical.

**Action types.** `place` only. 65 action IDs: `0..63` map to board cells as `y*8 + x`, and `64` = **pass**. Two consecutive passes end the game by piece-count majority (the "double-pass majority exploit" from Run 13).

**Placement constraint.** `target="empty"`, `constraint="adjacent_to_own"`, `first_move_anywhere=true`. Each player's first move is free; subsequent moves must be in an empty cell 4-adjacent to one of that player's own existing stones. Adjacency wraps on the torus.

**Capture.** `capture_type="none"`. **No captures at all.** Stones are permanent once placed.

**Propagation — influence.** `prop_type="influence"`, `radius=2`, `strength=0.8735`, `decay=0.4250`. When a P1 stone is placed at cell `c`, the engine adds `+strength * decay^dist` to `board_values[c']` for every cell `c'` within Manhattan radius 2 (torus-aware after the Run-14 fix). P2 adds the same magnitude with a negative sign. Values clamp to ±100. Verified: a lone P1 stone at (3,3) deposits +0.873 at its own cell, +0.371 at each of 4 distance-1 neighbours, and +0.158 at each of 8 distance-2 cells — total footprint ≈ 3.62.

**Win condition — threshold.** `condition_type="threshold"`, `threshold=46.407`, `target_dimension=0`, `max_turns=83`. After each move the engine scores each player as the signed sum of `board_values[c]` over cells they own; if |sum| > 46.407 for a player that player wins. Equivalent condition: a player wins when their owned cells aggregate > 46.4 in their favour.

Max turns is 83; if reached, decided by piece-count majority.

**Degeneracy check.**
- Double-pass exploit exists (confirmed by direct engine step). Not observed in actual play — no rational actor passes while behind, and the threshold is easily reached.
- Threshold IS reachable under normal play: isolated stones contribute +0.87 (would need 53), but clustered stones stack to ~3.6 per cell, so ~15–20 well-packed stones cross the line. Engine-verified in all three of my playthroughs; every game converged on threshold-win well under 83 turns.
- Capture rule is inert (capture_type=none, threshold=1 ignored).
- Run-14 simultaneous mechanic is NOT used here — this is a vanilla alternating Go-like.

No killer degeneracy. The rules as stated produce a playable game that converges cleanly on the threshold condition.

---

## PHASE 2 — Strategic Play (3 games, engine-verified)

Each move below was validated by stepping the live `GameEngineV2`; only legal moves were committed. Scores shown are the signed owned-cell sums used by the engine's win check.

**Seat-swap note.** I am one reasoner handling P1 and P2 sequentially. Game 3 swaps seats (I play P2 with full knowledge of games 1-2). Residual seat-identity bias acknowledged.

### Game 1 — P1 centre-cluster vs P2 far-corner mirror

Opening: P1 (3,3), P2 (7,7) (maximal torus distance). Both build 4×4 blocks outward from their anchor.

Key telemetry:

| Move | Player | Cell | P1 val | P2 val |
|---|---|---|---|---|
| 1  | P1 | (3,3) | 0.87  | 0.00  |
| 2  | P2 | (7,7) | 0.87  | 0.87  |
| 8  | P2 | (0,0) | 7.09  | 7.09  |
| 20 | P2 | (7,1) | 23.01 | 23.01 |
| 30 | P2 | (6,1) | 38.90 | 38.90 |
| **35** | **P1** | **(4,1)** | **47.28** | 43.98 |

**P1 wins at move 35, 18 stones to 17.** Scores are identical through move 30 because both clusters are structurally congruent under torus translation; the only asymmetry is tempo. P1's threshold crossing is exactly the "one-stone-ahead" tempo lead.

### Game 2 — P1 centre-cluster vs P2 adjacent-contest

P2 invades immediately: P1(3,3), P2(4,3). They build interlocking vertical strips in the centre.

| Move | P1 val | P2 val |
|---|---|---|
| 4  | 1.80  | 1.80  |
| 12 | 9.64  | 9.64  |
| 24 | 24.18 | 24.18 |
| 40 | ~45   | ~45   |
| **41** | **50.76** | 45.34 |

**P1 wins at move 41, 21-20.** The strips are symmetrical so scores track identically, and P1 again wins on the tempo move. Note a subtle effect: adjacent invading stones write *negative* influence into neighbouring cells the *other* player owns, depressing each cell's contribution to its owner's sum. The strips self-cancel this because both sides invade equally, but it means each stone counts LESS in contested zones. So tight adjacency slows both sides equally and preserves tempo.

### Game 3 — Seat swap: I play P2 with asymmetric-aggression strategy

I now play P2. P1 plays centre-cluster like before. I play *adjacent-invasion but non-matching* — I don't mirror vertically, I plant stones that maximally suppress P1's cells while still chaining for adjacency.

Engine-verified move sequence (abbreviated):
27 28 26 36 19 20 35 44 18 21 34 29 43 37 11 12 25 45 17 22 33 38 9 46 41 30 3 4 51 52 59 60 2 5 50 53 58 61 10 13 …

Progress:
- Move 12 (P2): P1=9.64, P2=8.58 (P1 ahead by tempo)
- Move 18 (P2): P1=15.16, P2=15.59 (**P2 overtakes**)
- Move 30 (P2): P1=29.39, P2=31.19 (P2 lead widening)
- **Move 40 (P2): P1=45.34, P2=47.14 — P2 wins**

**P2 wins, 20-20 on pieces, by threshold.** This is the load-bearing finding of the evaluation: the game has real counter-play and first-mover advantage is **not** decisive.

**Mechanism.** P2's invasion stones are placed on the cells that WOULD have had the highest future P1 value (the interior of P1's cluster). By converting those cells to P2-owned, P2 (a) captures that influence for itself on the torus (positive P2 accumulation from P2's own later stones) AND (b) denies P1 those high-value cells. P1 is forced to expand outward into lower-density frontier cells. Once the invasion overlap is dense enough, P2 surpasses P1 despite being a stone behind.

### Per-game reflection

- **P1 strategy guide.** Open centre. Build a 4×4 block. Prefer inside-first (maximise d=2 overlap). If the opponent invades, match them — don't panic and over-extend.
- **P2 strategy guide.** Don't mirror at maximal distance — that gives up the tempo race. INSTEAD, play adjacent to P1's opener and interleave strips. Even better: play *inside* P1's forming cluster to capture its highest-density cells for yourself. You will be a stone behind on count but will net higher threshold value.
- **Endgame resolution.** All three games resolved by threshold, not by double-pass or max-turns. No pass was ever legal-preferred. Flag = clean.

---

## PHASE 3 — Strategic Analysis (joint P1/P2)

**Distinct viable strategies?** Yes. At least three I engine-verified:
1. **Far-mirror (symmetric build).** Loses by one tempo.
2. **Adjacent strip-contest.** Loses by one tempo (self-cancels).
3. **Invasion / cluster-hijack.** Can win for P2. Exploits the fact that owned-cell scoring rewards cell *possession* more than influence emission, and torus has no corner advantage.

Validated by exhaustive greedy-lookahead self-play: when P2 uses `score = own - 2.5*opp` (heavy disruption weighting) while P1 uses `score = own - 1.0*opp` (balanced), **P2 wins** at move 42 (21-21 pieces, 46.94 vs 45.57). Symmetric strategies (both at `opp_weight=1.0`) yield a consistent P1 win 48.17/45.60. Equilibrium (both aggressive) reverts to P1 win by tempo. This is consistent with the training data: both RL runs converged to ~0.5 winrate — the nets found mixed strategies that stay balanced.

**Meaningful counter-play?** Yes. P2 must actively detect whether P1 is building open vs closed clusters and pre-emptively invade the highest-decay cells. This is non-trivial positional reasoning.

**Short-term vs long-term tension.** Strong. Each stone contributes up to ~3.62 "influence units" over its neighbourhood, but only to cells you OWN, and you can only own cells adjacent to existing pieces. So you are always choosing: (a) extend the cluster frontier (more own-cells for future overlap) vs (b) fill in high-density interior cells (higher current-stone value but no new frontier). In Game 3 my P2 play repeatedly traded frontier for density and it worked.

**Emergent concepts.**
- **Tempo:** exactly Go-like, but with arithmetic precision (each tempo ≈ 0.87 influence deposited immediately).
- **Territory/Density:** the threshold favours dense blobs, giving a clear territorial objective.
- **Cluster shape:** 4×4 > plus-shape > line, proven by influence arithmetic (a 4×4 block of 16 stones totals ≈ 42.5; a 3×5 block of 15 stones totals ≈ 38.9; 20 stones in a 5×4 reaches 55 — superlinear density return).
- **Invasion/denial:** novel variant. With no captures, invaded stones are permanent, so invasion is a permanent denial, not temporary.
- **Ko/initiative:** no repetition-based ko, but there's an initiative analog — the player who forces the other to respond to their cluster dictates the geometry.

**Does topology matter?** Yes, specifically:
- Torus removes edge/corner advantage — in Game 1 both 4×4 clusters are congruent.
- Torus shrinks effective distance: max Manhattan distance on 8×8 torus is 8, so even "opposite-corner" placements can eventually interact via wrap at move 30+.
- Torus + radius 2 means the entire board fits within ≈ 3 "influence hops", making the game fundamentally short (~40 moves).

**First-mover advantage.** Under naive/symmetric play, P1 wins 2/2 (Games 1 and 2). Under asymmetric-aggression play (Game 3 seat swap with invasion), P2 wins. Training runs converged to 0.50 — the optimal strategy is mixed. Net: first-mover advantage exists but is **counterable** by an aware P2. Seat-swap evidence supports Balance score ≈ 6–7.

---

## PHASE 4 — Novelty Adversary (and rebuttal)

### Adversary's case

**(a) Genre placement.** This is a place-only, no-capture, threshold-win abstract with influence propagation. It has direct analogues:
- **Tumbleweed** — both players add stones; each stone contributes a signed height to neighbouring cells with line-of-sight visibility; ownership decided by signed total. This game replaces line-of-sight with Manhattan-radius-2 exponential decay, but the core is the same "each stone casts a decaying vote on nearby cells" mechanic. Strong match.
- **Reversi/Othello** — place-only, cells change value based on neighbours. Weaker match because Othello flips ownership and this game never changes ownership.
- **Go** — threshold-ish territorial scoring. Weak match because Go counts empty territory and has captures.
- **Hex/Y/Havannah** — pure connection, no analogue to influence propagation. Not close.
- **Gomoku/Pente/Connect6** — placement + line-pattern wins. Not close; this game scores by area integral, not pattern recognition.
- **Amazons** — movement + territorial partition. Not close.
- **Conway's Life / HighLife / Day & Night** — this game has no CA step. Not applicable.
- **Diplomacy / simultaneous-move games** — not applicable; this game is alternating.
- **Slither** — place+slide snake, no influence. Not close.

The adversary's strongest analogue is **Tumbleweed**: "Tumbleweed with Manhattan-radius-2 exponential-decay influence on a torus, no visibility rule, no slow-start settlement phase." The transformation is:
- Replace "line-of-sight count within a ray" with "Manhattan distance ≤ 2 with exponential decay."
- Replace "settle phase (both first moves free)" with "only first move free per player."
- Replace "ownership by signed majority on each cell" with "signed influence sum as a global threshold."
- Add "adjacent_to_own" placement restriction (Tumbleweed has no such thing — any empty visible cell).
- Swap flat board for 8×8 torus.

**(b) CA lineage.** Not applicable (no CA).

**(c) Simultaneous lineage.** Not applicable (alternating).

**(d) Re-skin transformation.** Tumbleweed on torus with a bounded-radius kernel. The adversary claims the transformation preserves the essential structure.

**(e) Expert-advantage test.** Would an expert Tumbleweed player have an immediate edge? **Partially yes** — cluster density intuition and "deny opponent's high-influence cells" transfer directly. **But key knowledge does NOT transfer**: (1) the `adjacent_to_own` restriction forces chained placement, which is alien to Tumbleweed; (2) radius-2 Manhattan with exp decay is much more local than Tumbleweed's line-of-sight; (3) the signed-threshold global win condition creates race dynamics absent in Tumbleweed's per-cell majority.

### P1/P2 rebuttal (specific to Phase 2 moments)

1. **`adjacent_to_own` changes the geometry fundamentally.** In Game 2 my P1 could NOT play at (5,5) on move 3 even though it looked optimal — the only legal moves were the 4 neighbours of (3,3) plus pass. This chained-placement constraint is absent in every game the adversary cited. Every strategy has to reason about "what cells does my cluster make available next?" — a Tumbleweed expert has no intuition for this.

2. **Invasion-for-denial has no Tumbleweed analogue.** My Game 3 P2 invasion strategy only works because influence is *signed* at the board_values level AND ownership is permanent (no capture). In Tumbleweed, invading a cell either flips ownership or does nothing visible to the opponent's score; here, it permanently reduces both the contested cell AND its 4 neighbours in opponent's score. That exact mechanic (signed-influence writing to cells you don't own) is the game's signature trick, and it emerged in Phase 2 Game 3 as a winning strategy.

3. **Tempo arithmetic is exact.** Between move 17 (P1=20.44) and move 19 (P1=23.01), P1 gained exactly +2.57 from one stone that had 4 d=1 neighbours already P1-owned — this is a precise arithmetic optimisation problem, not a fuzzy positional judgment. Go/Tumbleweed experts have no edge on this; an engineer does.

4. **Torus + radius 2** creates wrap-around strategic interactions well before moves exhaust (Game 1 at move 25, my P1 cluster at (2,5)–(5,5) was interacting with P2's cluster at (0,7)–(7,7) via the wrap — evidenced by both sides' scores remaining locked). No flat-board game has this.

### Novelty score

**6/10.** The game is not purely novel — it sits in a Tumbleweed / Go-area-style lineage, and if you squint at the core "stones influence a neighbourhood" idea, there are precedents. But the specific combination — `adjacent_to_own` chained placement + signed-influence threshold + torus + permanent stones — produces strategic patterns (particularly the "invasion for denial of influence" mechanic in Game 3) that I have not seen in the catalog. Not a publishable-in-MathSci-Press game, but distinctly itself.

---

## PHASE 5 — Verdict

**Team ID:** team-9
**Game ID:** 1ca924cc3062
**Rules Summary:** Alternating placement on an 8×8 torus with `adjacent_to_own` chaining; each stone deposits ±influence in a Manhattan-radius-2 neighbourhood with 0.87 strength and 0.425 decay; first player to achieve ≥46.4 signed influence on their owned cells wins.
**Topology:** 8×8 torus, 4-neighbour adjacency.
**Turn Structure:** Alternating (Run 14's simultaneous mechanic is NOT used).

### SCORES (1–10)

- **Strategic Depth: 6** — Distinct viable strategies (mirror, contest, invasion), genuine short/long tension (frontier vs density), and torus-wraparound interactions. Loses points because games converge in ~40 moves and the action-branching factor stays small (legal-action count never exceeded ~25 in my playthroughs). Training runs' agent-vs-random score of 0.88 confirms non-trivial depth but not deep-search-worthy.
- **Emergent Complexity: 5** — Influence arithmetic produces clean, understandable emergent cluster-shape preferences (4×4 > 3×5 > 5×3 > line). The invasion-denial mechanic is a genuine emergent tactic. But no higher-order phenomena (no life-and-death, no sente/gote exchanges, no repetition patterns).
- **Balance: 6** — Naive P1 play wins 2/2; adversarial P2 wins 1/1 (seat-swap Game 3). Training runs converged to 0.50. First-mover advantage exists but is defeatable. I'd call this adequately but not impressively balanced.
- **Novelty (post-adversary): 6** — Strongest adversary argument: "Tumbleweed with a Manhattan kernel on a torus." Strongest rebuttal: the `adjacent_to_own` chain constraint plus the permanent-stone signed-influence creates an invasion-for-denial tactic that has no direct Tumbleweed analogue and emerged as a winning strategy in play.
- **Replayability: 5** — The strong symmetry on torus plus limited branching means openings don't vary much; cluster-build shapes are fairly predictable. Interesting once or twice for humans; more interesting as a benchmark environment.
- **Overall "Would I play this again?": 5** — I'd play it as a puzzle (find P2's winning invasion), not as a recreational abstract.

**CLOSEST KNOWN-GAME ANALOG:** Tumbleweed. Not identical because (a) radius-2 Manhattan exponential decay replaces line-of-sight, (b) `adjacent_to_own` forces chained placement, (c) global signed threshold replaces per-cell majority, (d) torus wrap eliminates edge advantage.

**KILLER FLAWS:**
- None that force a win. Double-pass exploit is present but irrational under normal play (threshold is reachable in ~40 moves well under max_turns=83).
- Minor: strong structural symmetry makes ~60% of possible positions strategically equivalent under torus translation — reduces genuine replayability.
- Note: Run 14's simultaneous-move innovation is NOT exercised by this game; it's a classical alternating design. If the GE metric rewarded this game as "Go-essence" it is identifying classical Go-shape without Run 14's new mechanic. Suggests GE at rank 2 is measuring familiar territorial dynamics, not Run-14 novelty — consistent with the evaluation prompt's concern about GE trustworthiness.

**BEST QUALITY:** The invasion-for-denial tactic. Because stones are permanent and influence is signed, an invasion permanently reshapes the board's value function — and it emerged spontaneously as the P2-winning strategy during Phase 2. This is the cleanest "small rule creates sharp tactical choice" feature of the game.

**IMPROVEMENT IDEAS:** Add a single "pie rule" on move 1 (P2 may swap seats after seeing P1's opener). This would neutralise the first-mover tempo advantage without changing any of the game's rules, and would make the invasion-vs-mirror decision happen before move 2 — sharpening all the strategy immediately.

---

### Appendix — Engine spot-checks

- Board scoring uses `sum(board_values[c] for c if owner==player)`, signed; verified at `engine_v2.py:_check_threshold` (line 744).
- Adjacency is 4-neighbour, torus-wrapping; verified by inspecting legal_actions after placement.
- Double-pass ends via `_end_by_max_turns`-style majority; verified by direct trial.
- Threshold 46.407 is reachable under mutual non-pass play in 35–42 turns; verified in all three games.
- Manhattan distance on torus behaves symmetrically (Run-14 fix confirmed); no anomalous influence behaviour observed.
