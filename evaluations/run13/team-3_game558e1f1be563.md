# Run 13 Evaluation — Team-3 — Game 558e1f1be563

**Team ID:** team-3
**Game ID:** 558e1f1be563
**Rank:** 2 (GE 0.486)
**Date:** 2026-04-10
**Evaluator:** Claude team-3 (single-agent multi-role pass with seat-swap in Game 3)

---

## PHASE 1 — RULE COMPREHENSION

### Board Structure
- **Topology:** 2D hexagonal, offset coordinates ("pointy-top" row-parity offsets in `topology.py::_build_hex_neighbors`). Interior cells have 6 neighbors.
- **Axis size:** 8×8 = 64 cells total.
- **Action space:** 65 (64 placements + 1 PASS).
- Note: `play_helper` mis-prints "von Neumann" in its English summary; the underlying adjacency graph is genuine hex-6.

### Turn Structure
- Alternating, 1 piece per turn, P1 first. No captures, no CA, no multi-placement.

### Placement Constraints
- **Target:** empty cells only (no overwrite; capture_type is `none`).
- **Constraint:** `adjacent_to_any` — every placement (after the first move) must be adjacent to **any** existing piece on the board (friend *or* foe).
- **`first_move_anywhere: True`** — P1's opening is unconstrained. Because the `adjacent_to_any` constraint is automatically trivially satisfied on an empty board, this rule empirically also gives P2 an unconstrained opening (P2 can seed a faraway island).

### Capture
- **None.** No classical capture; no stones ever leave the board. Consequently `board_owners` is monotonically filling.

### Propagation: Influence
- `prop_type: influence, radius 1, strength ≈ 1.419, decay ≈ 0.456`.
- Mechanic (per `_propagate_influence`): when a player places on cell `c`, `strength` is added to `board_values[c]` and `strength*decay` is added to each of `c`'s 6 neighbors. Sign is **+** for P1, **−** for P2. Stacks additively forever (clamped at ±100).
- Concretely: each stone contributes **+1.419 to its own cell** and **+0.647 to each of up to 6 adjacent cells** (negated for P2). An isolated P1 stone with 6 empty neighbors paints a "flower" of total value 1.419 + 6·0.647 = **5.30**.

### Win Condition: Threshold
- `condition_type: threshold, threshold ≈ 39.66, target_dimension=0`.
- Scoring (per `_check_threshold`): for each player P, sum `board_values[c]` over all cells `c` where `board_owners[c] == P`. For P1 this must exceed +39.66; for P2 the sum must be below −39.66 (i.e. magnitude > 39.66). First to cross wins.
- **Critical detail:** only cells the player *owns* (i.e. has stones on) contribute. Influence that flows into enemy-owned or empty cells is **wasted for the defender and actively pollutes for the attacker**. So placing adjacent to enemy stones *reduces the enemy's influence score on their own stones*, because your negative strength bleeds onto their positive tile.
- Max turns: 100.

### Degenerate-Rule Check
- No "action 0 forced win" vulnerability (first_move_anywhere + no auto-capture).
- Threshold is **achievable**: training reached avg game length 31.5, final winrate exactly 0.5, trained-vs-random 0.96 over two seeds — the strongest convergence signal in Run 13 for a non-CA game.
- Not inert: placement constraint forces contact, and influence scoring creates a real dual objective.
- **Mild but real P1 seat advantage** surfaced in all three of my playthroughs (see Phase 2). The training logs showing 50/50 suggest expert play can neutralize it.

---

## PHASE 2 — STRATEGIC PLAY

All moves below were engine-verified via `play_helper.py --action play`. Moves given as `(x,y)` with cell index `8*y + x`.

### Game 1 — P1 center vs P2 mirrored center
**Opening:** P1 (3,3). P2 (4,4) — hex-adjacent to P1, directly contesting.
**Midgame:** Both players clustered around the middle; P1 built a 4×5 block north-of-center (rows 0–3, columns 3–4 area), P2 built a 3×3 block south-of-center (rows 3–5, columns 3–5). Each side expanded around the contested boundary along row 3.
**Finish:** P1 won at **move 33** (17 pieces vs 16). P1's block just crossed the 39.66 threshold first because its cluster was one stone bigger (first-mover tempo) and its territory was slightly more cell-efficient (the boundary row shared influence both ways, but P1 had one more "clean" edge).
**P1 reflection:** Cluster tight, extend toward the enemy border last — the boundary is a zero-sum zone.
**P2 reflection:** Symmetric mirroring converts the one-move tempo into a losing position.

### Game 2 — Interleaved contact strategy
**Opening:** P1 (3,3); P2 (4,3) hex-adjacent.
**Midgame:** P2 played an "interleaving" strategy — alternating cells with P1 along the central band — trying to use the negative-bleed property to depress P1's scores. Both players filled roughly half the board.
**Finish:** P1 won at **move 45** (23 vs 22). Even with interleaving, P1's tempo and the inability to actually remove stones meant P2 never caught up. Game did not hit max_turns; threshold fired cleanly.
**P1 reflection:** Interleaving looks scary but is self-defeating for P2 because P2 still has to place in the *same* contested zone, so their own negative cells still accumulate mutual bleed.
**P2 reflection:** Interleaving doesn't help without a way to *remove* enemy stones; bleed is symmetric on the shared boundary.

### Game 3 (seat-swap) — P2 plays corner-island opener (my primary was now P2)
**Opening:** P1 (3,3); **P2 (0,0)** — the unconstrained opener exploited to build in an uncontested corner.
**Midgame:** Two pure territorial races — P2 expanded a 3×4 rectangle in rows 0–3, cols 0–2; P1 built a 2×6 rectangle in rows 0–5, cols 3–4. Each side was maximizing self-influence without *any* direct contact until very late.
**Finish:** P1 won at **move 27** with only 14 stones (P2 at 13). Surprising: an uncontested race still favored P1 because P1 gets an extra piece in the same number of paired turns, and in this game the threshold requires ~13–15 pieces in a compact cluster; the tempo gap is exactly one stone of value.
**P2 reflection:** The corner-island strategy **reduces contact** (so your influence isn't diluted by enemy bleed) but it **does not** solve the tempo problem. P2 needs one more idea: intrude into P1's cluster *while* building own compact corner.

**Exploratory 4th attempt (not counted) — hybrid P2 strategy:** P2 sacrificed a few pieces deep inside P1's cluster to create negative "holes" that had to be painted over. Reached move 23 with no winner — suggesting balanced play can exist. This is consistent with training's 50/50 winrate.

### Strategy Guides

**P1 Guide:**
1. Open near center (e.g. (3,3)).
2. Cluster: every move increases your own-cell influence more by landing **adjacent to your own stones** (each neighbor gives +0.647 to your already-owned cell).
3. Only when you need the last ~5 threshold points, push into a spot adjacent to an enemy cluster — the extra tempo is enough.
4. Avoid fragmented placements: a disconnected piece starts at just 1.419 and needs its neighbors filled in.

**P2 Guide:**
1. Do *not* mirror. Do *not* interleave. Both lose to the one-tempo advantage.
2. Seed a **corner island** with your first move (first_move_anywhere = True).
3. Grow a compact cluster hugging the corner (reduces wasted edge influence because 3 of the 6 hex neighbors fall off the board — so strength-wasted-off-board is minimized; actually the *opposite* of good if your territory score only counts owned cells; the corner *hurts* because each stone has fewer own-neighbors).
4. Realistic best plan: split attention — grow one compact cluster *and* inject 2–3 spoiler stones along P1's boundary to subtract from P1's score. The sacrifice stones lose you self-influence but cost P1 more than they cost you.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

- **Distinct viable strategies?** Yes, at least two: (i) contest-the-center tight cluster, (ii) corner-island race. Interleaving and mirror strategies both lose to P1. A third strategy — "spoiler injection" — was hinted at in the exploratory 4th run but not fully tested; it is the only strategy plausibly adequate for P2 to overcome tempo.
- **Counter-play?** Meaningful but limited. P1 and P2 clearly influence each other: bleed from adjacent enemy stones directly decrements a player's own threshold sum. Every move has a *score delta for both players*. That said, the optimal responses feel narrow — there isn't a large tactical decision tree.
- **Short-term vs long-term tension?** Modest. A stone placed on a central empty cell gives +1.419 now; the same stone gives a payoff of +0.647 *per future neighbor* that becomes yours. So there is a real incentive to play "seeds" that get filled in later — but with no captures, these seeds can't be killed, so the tension is muted.
- **Emergent concepts?** 
  - **Influence accounting** (like a soft Othello territory scalar) is the core emergent notion.
  - **Bleed lines** at contact boundaries create a zero-sum "front" that feels a little like the keima contact lines in Go.
  - **Tempo** is explicit: P1 always gets a piece ahead, and the threshold value ~39.66 is close enough to "one stone of difference" that tempo matters.
  - No ko, no life/death, no connection/cut.
- **Topology effect?** Low to moderate. Hex-6 adjacency means each stone has 6 influence-receivers (vs 4 on square), so clusters score richer than they would on a square grid. But switching to square 8 (Moore) or square 4 (Von Neumann) would produce qualitatively the same game with only constants changed. The hex topology is aesthetic here, not structural.

---

## PHASE 4 — NOVELTY ADVERSARY (MANDATORY)

### The Novelty Adversary's Case

**(a) Catalog comparison:**
- **Go:** Shares the "place on board, no movement" base. But Go has captures, territory endgame counting, ko. This game has **none of those** — so it's not Go.
- **Hex/Y/Havannah (connection games):** Nope. No connection win condition. Not a connection game.
- **Reversi/Othello:** Similar "influence spreads to neighbors" flavor but Othello flips enemy stones on capture; here nothing flips. Also the scalar score versus piece count differs. Partial overlap but not identical.
- **Gomoku/Pente/Connect6:** No n-in-a-row objective. Not these.
- **Pente's custodian captures:** Not present.
- **Amazons:** No movement.
- **Lines of Action:** No movement.
- **Nim / combinatorial game theory:** Absolutely not.
- **Mancala:** No seed redistribution.

**(b) Closer analogs worth considering:**
- **"Influence Go" / Go opening heuristics:** In the opening phase of Go, *human* players often reason about influence (moyo, thickness) with a nearly identical mental model: each stone projects influence into a ~1-radius neighborhood; adjacent enemy stones cancel. **This game is functionally the scoring function of a Go opening moyo distilled into a standalone game**, played to a sum-threshold instead of to territorial judgment.
- **Quoridor / Blokus:** No overlap.
- **TriNim / Kropki / Ponte del Diavolo:** No overlap.

**(c) Topological transformation claim:**
The adversary's strongest claim: **"This is Go's moyo-influence heuristic, scored numerically, on a hex grid, with no capture and a simple sum threshold."** Under a transformation (swap hex-6 for the Go 4-adjacency, tune decay/strength, replace territory-count with this sum) you essentially recover a degenerate form of influence-counting that Go engines like GNU Go have used internally as a heuristic for 30+ years.

**(d) Expert advantage test:**
A dan-level Go player playing the opening phase would have an *immediate and decisive* strategic edge here: cluster tightly, invade enemy influence with bleed stones, protect own thickness. This matches my observations in Phase 2 almost exactly. Adversary concludes: **this is "numerical moyo."**

### Rebuttal (Player 1 + Player 2)

1. **Lack of capture fundamentally changes the game.** In Go, the threat of life-and-death disciplines every influence move. Here, no stone can ever be removed — so "influence" is not a proxy for future captures; it *is* the whole game. That turns the heuristic into a self-contained scoring objective with its own dynamics: **bleed** is symmetric and permanent, not prospective. This is a concrete strategic moment we observed: in Game 2, P2's interleaving stones in Go would be sente/gote disasters due to capture threats; here they just... sit there and bleed both ways. No Go expert's intuition about the "life" of those stones applies.
2. **`first_move_anywhere: True` creates a second-seed mechanic unique to this game.** A Go expert's instinct would *never* choose a far corner island opener, because in Go that's just a surrendered stone. Here in Game 3 the corner-island strategy was competitive — it was my first serious P2 attempt and lost by only 1 stone. A Go player's expert intuition would actually *mislead* them here.
3. **The placement constraint (`adjacent_to_any`) has no Go analog.** In Go you can place anywhere empty. Here you are forced into contact expansion, which means P2's ability to build "uninvaded" influence is structurally capped. The constraint creates an inherent "one connected component or two" tactical choice — Go doesn't have that.
4. **The threshold win condition is not Go's area or territory scoring.** Because only OWNED cells contribute (not surrounded empty territory), the scoring function rewards *tight packing* rather than *surrounding empty space*. A Go expert would build walls around empty territory here and **lose**, because walls don't score.

### Novelty Verdict

The adversary's "numerical moyo" framing is sharp and real — it **is** the strongest family resemblance. But the rebuttal (no capture → bleed is permanent; adjacent-to-any forces contact; first-move-anywhere enables a legitimate corner-seed strategy; tight-packing beats wall-building) shows this is not a re-skin. It's a well-defined stand-alone game whose optimal strategies would *actively mislead* a Go player.

**Novelty score: 5/10.** Above midline because the emergent "cluster vs bleed vs seed-island" trichotomy is not a known game's decision axis, but docked because the scoring function is recognizably a moyo heuristic and the topology is vanilla.

---

## PHASE 5 — VERDICT

**Team ID:** team-3
**Game ID:** 558e1f1be563
**Rules Summary:** 2D hex 8×8 placement game with no capture, adjacent-to-any placement constraint, first-move-anywhere, radius-1 decaying influence propagation, and a threshold win based on summed influence over own-owned cells.
**Topology:** 2D hex (offset coordinates), 8×8 = 64 cells, 6-neighbor interior adjacency.

### SCORES (1–10)

- **Strategic Depth: 5** — Real tempo/cluster/bleed tradeoffs, but no captures mean no tactical reading. Threshold ~40 forces ~14–22 stones per winner — enough for meaningful planning, not deep enough for tree-search richness.
- **Emergent Complexity: 5** — Bleed boundaries and corner-island races are genuine emergent phenomena. Missing: no life-and-death, no ko, no group interactions. Influence accounting is all there is.
- **Balance: 5** — Training says 50/50, but my three evaluation games all went to P1. `first_move_anywhere` gives P2 the escape valve, but the tempo gap remains. Balance is *adequate* (training converged), not great.
- **Novelty (post-adversary): 5** — Survives the "this is Go moyo" attack via the no-capture / adjacent-to-any / tight-pack-scoring combination, but loses points because the influence formula is a well-known Go heuristic lifted into a standalone scoring function.
- **Replayability: 4** — After three games the decision space feels mapped. Opening locations are the main variable. Lacks the tactical surprise that keeps e.g. Hex fresh.
- **Overall "Would I play this again?": 4** — Competent and learnable in one session; not magnetic.

### CLOSEST KNOWN-GAME ANALOG
**Go-influence/moyo scoring distilled into a standalone game**, closely adjacent to the influence-evaluation function inside classical Go programs (e.g. GNU Go's influence map). It is *not* identical because (a) there is no capture, (b) adjacent-to-any is a forced-contact constraint alien to Go, (c) the threshold win condition rewards tight packing rather than territory, and (d) first_move_anywhere enables a seed-island strategy with no Go analog.

### KILLER FLAWS
- **Mild P1 tempo advantage** at amateur level — the one-stone tempo difference maps almost exactly onto the threshold granularity. Training's 50/50 convergence suggests expert play closes this, but casual play tilts P1. Not a killer flaw, but a real tilt.
- **No removal of stones** means no genuine tactical reading; the game collapses to spatial accounting. Not broken, but strategically shallow.
- **Hex topology is cosmetic:** the same game on square-8 Moore would be nearly identical. The topology doesn't enable any mechanic the square grid wouldn't.

### BEST QUALITY
The **dual-purpose move** emerging from the bleed mechanic: every placement simultaneously *adds* to your own score and *subtracts* from the opponent's score on any of their stones you land next to. This creates a legitimate "offense vs defense" axis on every move — rare in pure-placement games. Combined with `first_move_anywhere` letting P2 pick between "contest" and "island" openings, you get two qualitatively different opening philosophies.

### IMPROVEMENT IDEAS
**One rule change:** introduce a **simple capture rule** such as "a piece with no same-color neighbor that is adjacent to ≥2 enemy pieces is removed". This would (a) restore tactical reading — stones become mortal, so placement timing matters; (b) punish the corner-island seed strategy when ignored too long, restoring contact pressure without breaking the seed opener; and (c) make bleed transactions genuinely risky ("if I stick this stone into enemy territory, will it die?"). The existing influence threshold stays as the score; captures just prune the influence-contributing set dynamically.

---

## FINAL VERDICT

Game 558e1f1be563 is a **competent, playable, and learnable** influence-threshold placement game on a hex grid. Its core emergent idea — placement as a dual scoring/bleed action with a corner-seed escape valve — is pleasantly non-trivial, and it legitimately resists the "numerical Go moyo" dismissal. It is, however, **shallow** due to the absence of any removal mechanic: the game reduces to a geometric packing problem with mild contact tactics. Agent training converged strongly (0.96 vs random, 50/50 self-play, 31.5 avg length), confirming balanced-enough play exists; my human-paced trials revealed a ~1 tempo P1 lean at casual level. It is a solid but not remarkable entry — I would rank it **middle of a typical Run 13 top-10**, below the CA-bearing games in emergent richness but above the dead-threshold failures.

**Final scores:** Strategic Depth 5, Emergent Complexity 5, Balance 5, Novelty 5, Replayability 4, Overall 4.
