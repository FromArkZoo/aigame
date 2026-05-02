# Run 19 Evaluation — team-2 — Game ce3a09e05cef

**Team ID:** team-2
**Game ID:** `ce3a09e05cef` (Carpet rank-1, GE 0.3547, ELO 2280.5 — **highest GE in R19**)
**Substrate:** Sierpinski carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game ce3a09e05cef` (see `briefing_carpet_rank1.md`).
**Soft violation flagged:** `sierpinski_threshold_inert`.

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 grid with 17 inactive holes per the level-2 Sierpinski carpet pattern. Holes: the central 3×3 at (3..5, 3..5) = 9 holes, plus 8 sub-block-center holes at (1,1), (4,1), (7,1), (1,4), (7,4), (1,7), (4,7), (7,7). 64 active cells. Cell index = y·9 + x. Max degree 4 (axis-aligned only).

**Max-degree-4 cells (the "carpet anchors")**: (2,2)=20, (2,6)=56, (6,2)=24, (6,6)=60 — exactly 4 cells where all 4 axis-neighbours are active. These are analogous to menger's 8 6-degree interior anchors.

**Turn structure.** Alternating, P1 first. Max 100 turns.

**Action space.** 82 actions = 81 placements + 1 pass. Place-only — D1 hybrid ban active.

**Capture (outnumber-2).** Engine code (`engine_v2.py:_capture_outnumber`): for each enemy neighbour of the placement, count P1 (placer) stones among the enemy's active neighbours (`topo.get_neighbors`, holes excluded); if count ≥ 2, remove. **Holes do NOT count toward the count** — they're simply excluded from the neighbour set. Captures are straight removal, not flip.

**Propagation.** Influence, **r=2, strength=1.0, decay=0.5**. Adds ±1.0 to placed cell, ±0.5 to BFS-distance-1 active cells, ±0.25 to BFS-distance-2 active cells. **Holes block propagation paths** — graph distance is computed through active cells only, not Manhattan.

Per-stone yield at 4-degree interior anchor (verified):
- 1-stone anchor: +1.0
- 5-stone "plus" cluster (anchor + 4 neighbours): **+12.0** = +2.4/stone average
- Adjacent shell-2 cells: +3.5/move (highest greedy hint).

Compare pilot's corner anchor:
- 4-stone corner cluster ((0,0)+(2,0)+(0,2)+(2,2)): +5.0 = +1.25/stone — half the per-stone yield.

**Win condition.** Threshold-race > **30.0**. Mirror with 4-degree interior anchor reaches threshold at ~12 stones / 23 plies (verified Game 1).

**Degeneracy check.**
- `sierpinski_threshold_inert` soft violation: threshold may be borderline reachable. Empirically I crossed it at ply 23 in mirror — well within max_turns=100, so the soft violation appears benign in practice.
- Holes block influence path AND reduce neighbour count; both effects compound at hole-edge cells.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`. Action IDs = y·9 + x.

### Game 1 — Mirror at the 4-degree interior anchor (full play-through)

Sequence: `20,60,11,59,21,61,19,51,29,69,12,52,28,68,2,58,18,42,38,22,4,76,3` (23 plies).

Plot:
- Plies 1-10: anchor + cluster construction. P1 anchors at (2,2)=20; P2 at (6,6)=60. Both build 5-stone "plus" by ply 10. P1 = +12.0, P2 = +12.0 (mirrored exactly). The 5-stone plus cluster yields **+12.0 — vs the pilot's 4-stone corner cluster's +5.0** — 140% more per cluster.
- Plies 11-18: shell-2 expansion (cells at distance 2 from anchor: (3,1), (1,3), (2,0), (0,2), (4,2), (2,4) for P1's anchor). Each yields +2.5 to +3.5 per move from the helper greedy hints (own +1.0 + 0.5 from up to 2 own 1-neighbours + 0.25 from up to 4 own 2-neighbours). Both at +25.0 by ply 18.
- Plies 19-22: more expansion. P1 at +29.0 by ply 21; P2 mirrors at +26.5 by ply 22.
- **Ply 23 P1 plays (3,0)=3.** P1 score = +34.0 > 30.0 → **P1 wins.** P2 has 11 stones at +26.5; never gets a 12th turn.

**Mirror = P1 wins by 1 ply at 12-vs-11 stones.** Same structural P1-by-1-ply tempo as all the menger games and pilot's corner mirror (which ended ply 21).

The pilot's mirror at corner (0,0) ended at ply 21 — 2 plies faster than my interior-anchor mirror. The corner anchor is slightly stone-efficient (boundary cells reach off-board "free" cells less often, making each placement marginally more impactful in the middle game). However, the corner is much more sandwich-vulnerable (Game 2 below).

### Game 2 — P2 sandwich attack vs P1 counter-sandwich at the 4-degree anchor

Sequence: `20,19,18` (3 plies).

Plot:
- P1 (2,2)=20 — interior anchor.
- **P2 (1,2)=19 — sandwich attack from west.**
- **P1 (0,2)=18 — counter-sandwich.** Verified: P2's (1,2) has P1 neighbours {(0,2), (2,2)} = 2 P1 stones among its 3 active neighbours. Outnumber-2 fires → **(1,2) is captured.** Score: P1 = +1.5, P2 = 0.

**Counter-sandwich at the 4-degree interior anchor works. The sandwich attack costs P2 1 stone net (attacker captured + tempo lost).**

### Game 2b — P2 sandwich attack vs P1 counter-sandwich at the corner anchor (0,0)

Sequence: `0,9,18` (3 plies).

Plot:
- P1 (0,0)=0 — corner anchor.
- P2 (0,1)=9 — sandwich attack from south.
- **P1 (0,2)=18 — counter-sandwich.** P2's (0,1) has P1 neighbours {(0,0), (0,2)} = 2 P1 stones among its 2 active neighbours (the (1,1) hole excludes the third axis direction). Outnumber-2 fires → **(0,1) is captured.** Score: P1 = +1.5, P2 = 0.

**This is the major independent finding.** The pilot's Game 2 sequence (`0, 9, 2, 1`) had P1 mistakenly play (2,0) at move 3 instead of the counter-sandwich (0,2). The pilot's "P2 sandwich is the genuine counter" claim **rests on a P1 mistake.** With correct P1 play, the sandwich attack at the corner is **also a losing line for P2** — same as at the interior anchor.

The capture economics:
- P2's sandwich attack: 2 stones invested, 1 P1 capture.
- **P1's counter-sandwich: 1 stone invested, 1 P2 capture, with the residual P2 stones at distance 2 (no influence reinforcement) for both sides.**
- Net: P2 spends 2 stones + loses tempo for 0 net captures. P1 spends 1 counter-stone + gains tempo for 1 net capture.

The carpet's hole pattern *helps* P1's counter-sandwich at the corner: (0,1) has only 2 active neighbours, both of which P1 can occupy with the (0,0) anchor + (0,2) counter. The hole at (1,1) eliminates the third axis direction that would otherwise be P2's escape.

### Game 3 — Novelty adversary: explore "what if P1 picks a sandwich-immune anchor?"

I attempted to find an anchor where neither sandwich nor counter-sandwich is available — e.g., a cell with so few active neighbours that no 2-of-N count is reachable.

Cells with only 2 active neighbours are common around the central hole: (4,2), (2,4), (4,6), (6,4) each have only 2 active neighbours. Anchoring at these:
- Per-stone yield: +1.0 (no neighbour bonus) plus distance-1 reach to 2 cells gives +2.0 kernel sum.
- Sandwich: P2 needs 2 P2 neighbours to capture. With only 2 active neighbours, P2 must place at BOTH simultaneously — same 2-stone investment as anywhere else.
- Counter-sandwich: P1 has fewer counter options because each P2 attacker has fewer adjacent escape routes.

**Hole-edge anchors are LESS sandwich-resistant in practice, not more.** The pilot's Game 3 finding ("hole-edge anchoring doesn't fix tempo asymmetry") is correct and matches my analysis. Hole-edge anchors give up cluster reinforcement (lower per-stone yield) for no real defensive gain.

**Conclusion of adversary game:** No sandwich-immune anchor exists; counter-sandwich is universally available at any anchor; P1's optimal strategy is interior 4-degree cluster + counter-sandwich whenever P2 attacks.

### Strategy guides

**P1 (offence/threshold push):** Anchor at one of the 4 max-degree-4 cells: (2,2), (2,6), (6,2), (6,6). Build the 5-stone plus cluster (anchor + 4 axis neighbours) for +12.0. Expand to shell-2 cells for +3.0+/move. **Always counter-sandwich any P2 attack** by placing the second cell along the attacker's axis — captures the attacker, preserves your anchor, costs you 1 stone for 1 P2 stone gain. Threshold reached at ~12 stones / 23 plies.

**P2 (defence + threshold contest):** Mirror loses by 1 ply (Game 1). Sandwich attack loses to counter-sandwich at all anchor types (Games 2 and 2b). **There is NO winning P2 line under perfect P1 play.** Best line is mirror with one attempted sandwich harassment in plies 5-8 to disrupt P1's tempo by 1-2 points; this still loses but minimises the deficit.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two for P1, zero clear winners for P2:
1. **Interior 4-degree anchor cluster** (my recommended P1 playbook). Highest per-stone yield, sandwich-resistant via counter-sandwich.
2. **Corner anchor cluster** (pilot's playbook). Slightly faster to threshold under mirror; same sandwich-resistance via counter-sandwich.

For P2: mirror (loses by 1 ply) and sandwich-harassment (loses but minimises deficit). **No structurally winning P2 line.**

**Counter-play.** **Substantially weaker than the pilot claimed.** The pilot's "knowledge-asymmetric balance" via P2 sandwich is actually a P1 mistake-driven balance — under best P1 play (counter-sandwich), the game is structurally P1-favoured. The PPO reported 0.500 trained-vs-trained must reflect (a) PPO never finding the counter-sandwich line, (b) PPO converging to a knowledge-asymmetric equilibrium where P1 plays suboptimal corner anchors and P2 plays sandwich attacks — but this equilibrium dissolves once P1 learns counter-sandwich.

**Short-term vs long-term.** ~10-ply tactical horizon, ~3-ply strategic horizon (anchor selection + first sandwich exchange). **Limited long-form planning** — the threshold race compresses everything into the cluster-build phase.

**Emergent concepts observed.**
- **4-degree interior anchors** (the (2,2)-class cells) and the +12.0 plus cluster they enable.
- **Counter-sandwich at all anchor types** including corners — a universal P1 defense made possible by the carpet's hole-induced low-neighbour-count cells.
- **Hole-blocked influence paths.** A stone near the central hole reaches fewer cells via BFS distance than a stone in the open grid. Real but minor.
- **Per-cluster-stone density premium for interior anchors.** +2.4/stone vs +1.25/stone — substantial but not strategy-changing because both cluster types still win under mirror.

**Does the carpet substrate matter?** *Modestly.* The 4 max-degree-4 anchor cells exist because of the boundary of the carpet's center hole; the hole-edge low-neighbour cells exist because of the corner sub-block holes. Both are substrate-driven. **Estimated contribution vs flattened 9×9 all-active: ~0.5 point of depth, ~1 point of novelty.** Same magnitude as menger rank-1's substrate contribution.

**Does the propagation kernel matter?** *Yes, substantially.* The r=2, decay=0.5 kernel is well-tuned: distance-1 reinforcement (+0.5) is strong enough to reward adjacency, distance-2 reach (+0.25) extends the cluster's influence beyond immediate neighbours. r=1 (menger rank-1) would force tighter clusters; r=3 would dilute the cluster premium. **Higher than menger rank-1's r=1 in expressive power.**

**Capture-rule contribution.** Captures fire only in early plies (5-8) during sandwich exchanges. Once both sides establish clusters with ≥2 own-cluster neighbours per stone (as in menger rank-1's "cluster sandwich-immunity"), captures stop firing. **Net contribution: tactical decoration in early game, inactive in mid/late game.**

**First-mover advantage / seat balance.** **Strongly P1-favoured under best play.** Mirror = P1 wins by 1 ply (Game 1). Sandwich = P1 wins via counter-sandwich at all anchor types (Games 2 and 2b). **The PPO 0.500 winrate reflects suboptimal P1 play, not true balance.** Same structural issue as menger rank-1.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + outnumber + threshold-race on a 2D fractal substrate. Argument:

(a) **Influence-based scoring** — same family as Tumbleweed (2020, 2D hex), Sygo (Go territory weights). Threshold-race-as-win is Yinsh-adjacent (cross 5 ring-removals first) but with continuous influence rather than discrete events.

(b) **Outnumber-2 capture** — Tafl/Ataxx-adjacent. Same as menger rank-1.

(c) **The combination** "outnumber + influence + threshold-race" — same R19-novel combination as the menger games. **Cross-substrate confirmation:** the same family appears on both 2D carpet and 3D menger, suggesting R19's evolution found one recipe across substrates rather than substrate-specific recipes.

(d) **Sierpinski carpet substrate.** 2D fractal. Closest published abstract-game case is Connection Hex (hex grid, not fractal). The carpet's specific hole pattern is a genuine novelty axis — but compared to the 3D menger sponge, the carpet is less unprecedented (2D fractals are studied in mathematics; 3D fractals less so).

(e) **Expert-transfer test.** Go + Othello + Hex + Tumbleweed player would understand the rules in 5 minutes. The non-obvious pieces: (i) holes block influence paths (introduces graph-distance scoring), (ii) outnumber-2 trigger condition (counts neighbours of the *enemy*, not the placement target), (iii) hole-edge cells with 2 active neighbours (low-yield but capture-cheap). Total: ~10 minutes to functional understanding.

**Closest known-game analogue:** **Tumbleweed-on-Sierpinski-with-Ataxx-captures.** No exact published analogue. Within R19, this game's strategic skeleton matches menger rank-1 (sibling on different substrate).

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2D grid. R19 carpet rank-1 is outnumber + influence + threshold-race on a 2D fractal. **Different family.** R8's narrative arc (build a chain to win) provides clear tactical climax; R19 carpet rank-1 is a "fill-space efficiently" game without climax. R8 wins on narrative tension and tactical structure; R19 wins on... not much, actually — the strategic skeleton is recognisable from many existing games, and the substrate adds modest novelty.

**Player rebuttal (P1 + P2).**
- The 4 max-degree-4 anchor structure is genuinely substrate-driven (analogous to menger's 8 6-degree anchors).
- The counter-sandwich at hole-edge corners (Game 2b) **is enhanced by the carpet's hole pattern** — the (1,1) hole eliminates one of (0,1)'s axis directions, making counter-sandwich at the corner trivial. This is a clean substrate-driven mechanic.
- Subtracting from novelty: the strategic skeleton (cluster + race) is well-established; the carpet substrate adds local geometric flavour but doesn't change the strategic family.

**Novelty score (post-adversary):** **4/10.** Below the pilot's 5 by 1 because: (a) my counter-sandwich finding shows the game is more P1-dominated than the pilot acknowledged, reducing the strategic interest, (b) the 2D carpet substrate is less unprecedented than the 3D menger substrate (which I scored 5 for novelty), (c) the strategic family is the same as menger rank-1/2 — R19 is exploring one recipe across substrates, not multiple recipes. Above R17 mean (3.50) because the substrate-specific corner counter-sandwich is a clean mechanic.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** ce3a09e05cef
**Rules Summary:** Place stones on a 9×9 Sierpinski carpet (64 of 81 cells active) to accumulate influence on cells you own. Each placement adds ±1.0 to itself, ±0.5 to active 1-neighbours, ±0.25 to active 2-neighbours; an enemy stone is removed if it has ≥2 of your stones among its active (non-hole) neighbours when you place. First to >30.0 effective influence wins.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4 (4 cells reach the max).
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** `sierpinski_threshold_inert` — verified harmless in practice (threshold reached at ply 23 of 100 max in mirror).

### Scores (1–10)

- **Strategic Depth: 4** — Cluster + sandwich + counter-sandwich + threshold race. The strategic surface is shallower than the pilot scored (5) because the counter-sandwich is universally available, removing P2's "balance counter" and reducing the game to "P1 picks anchor, P1 wins by 1 ply." Real decisions are concentrated in the first 8 plies.

- **Emergent Complexity: 4** — Sandwich + counter-sandwich exchange, hole-edge corner cells with their unique 2-active-neighbour topology, cluster reinforcement at 4-degree anchors. Below the pilot's 5 because the counter-sandwich removes one half of the sandwich emergent (the trade economics that pilot found interesting).

- **Balance: 3** — Mirror = P1 wins by 1 ply (verified Game 1, ply 23). Sandwich at all anchor types = P1 wins via counter-sandwich (verified Games 2 and 2b). **PPO 0.500 reflects suboptimal anchor + missing counter-sandwich, not true balance.** Same structural issue as menger rank-1. Below pilot's 4 because my counter-sandwich finding worsens the balance picture.

- **Novelty (post-adversary): 4** — see Phase 4. Below pilot's 5 because the carpet substrate is less unprecedented than the menger 3D substrate, and my counter-sandwich finding reduces strategic novelty.

- **Replayability: 4** — Same 4-anchor or 4-corner opening tree, with sandwich exchanges in plies 5-8. Once known strategies are public (interior anchor + counter-sandwich), openings collapse to a small set. Same as pilot's 4.

- **Overall "Would I play this again?": 4** — Once: marginal interest beyond menger rank-1 (same dynamics, 2D substrate). Repeatedly: no — the structural P1-by-1-ply advantage and the sandwich-counter-sandwich predictability cap interest. **Below pilot's 5 by 1.** Anchored against R17 mean (3.50): meaningfully above floor; well below R8 ceiling (8/10).

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed-on-Sierpinski-with-Ataxx-captures.** No exact published analogue. Inside this project corpus, **R19 menger rank-1 (`1f9191b5d4e6`) is the 3D version of this game** — sibling rule sets across substrates.

### KILLER FLAWS
- **Mirror = P1 wins by 1 ply** (verified ply 23, 12 stones vs 11).
- **Counter-sandwich is universally available** at both interior 4-degree anchors AND corner cells. The pilot's "P2 sandwich is the real counter" claim relies on a suboptimal P1 line. With correct P1 play, **P2 has no winning line** — the game is structurally P1-favoured.
- **Sandwich is a losing exchange for P2** (2 stones invested, 0 net captures, +1 tempo loss).
- **Cluster sandwich-immunity once consolidated** (same as menger games) — captures stop firing in mid/late game once both sides have ≥2 own-cluster neighbours per stone.
- **Soft violation** `sierpinski_threshold_inert` is benign in practice (threshold reached at ply 23, far before max 100), but its presence in the rule blob suggests evolution kept this rule despite a flagged violation — possibly indicating the violation criterion is too lax.

### BEST QUALITY
**The carpet's hole-pattern enables corner counter-sandwich.** At corner (0,0), the (1,1) hole eliminates (0,1)'s third axis direction. P1 can counter-sandwich at (0,2) and capture (0,1) using only 2 P1 neighbours. **This is genuinely substrate-driven** — on a hole-free 9×9 grid, (0,1) would have 3 active neighbours and counter-sandwich would still need only 2 P1 neighbours, but the (1,1) hole makes it more visible/triggerable in the corner geometry. Combined with the 4-degree interior anchors at (2,2)/(2,6)/(6,2)/(6,6), the carpet gives P1 strong defensive options.

### CARPET STRUCTURAL CONTRIBUTION
**Modest, similar magnitude to menger rank-1.** The carpet's 4 max-degree-4 anchors and the hole-induced low-neighbour-count cells are real substrate effects, but the underlying strategic family (cluster + race + sandwich) survives flattening to a regular 9×9 grid with minor strategy adjustments. **Estimated loss from flattening: ~0.5 point of depth, ~1 point of novelty.** The carpet's contribution is roughly equivalent to menger rank-1's but in 2D, so without the additional 3D-novelty multiplier.

### IMPROVEMENT IDEAS
**Single best change:** **Pie rule.** Same as all R19 games. After P1's first move, P2 may swap colours. Punishes any P1 anchor strong enough to win under mirror; restores seat balance.

Secondary improvements:
- **Increase capture threshold to 3** to make sandwich attacks require 3 P2 stones for 1 capture, deepening the capture trade calculus and likely making sandwiches viable for P2 (counter-sandwich would also need 3 P1 neighbours, often unavailable).
- **Reduce r to 1** (matching menger rank-1's kernel) to force tighter clusters and reduce the "reach" advantage of central anchors.
- **Add a connection secondary win condition** — e.g. connect opposite edges of the carpet — to give the game narrative tension. R8's family (custodian + connection) on the carpet substrate would be an R20 candidate.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-2_gamece3a09e05cef.md`.*
