# Run 19 Evaluation — team-1 — Game ce3a09e05cef

**Team ID:** team-1
**Game ID:** `ce3a09e05cef` (Carpet rank-1, GE 0.3547, ELO 2280.5 — **highest GE in R19**)
**Substrate:** Sierpinski carpet (axis 9, 64 active / 81 grid positions, max_degree 4)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game ce3a09e05cef` (briefing: `briefing_carpet_rank1.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 grid with 17 inactive holes per the level-2 Sierpinski carpet pattern: a central 3×3 hole at rows/cols 3-5 (9 cells) plus 8 corner-of-subcarpet holes at (1,1), (4,1), (7,1), (1,4), (7,4), (1,7), (4,7), (7,7). 64 active cells. Cell index = `y·9 + x`. Max degree 4 (axis-aligned).

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max 100 turns.

**Action space.** 82 actions = 81 placements + pass. Place-only (D1 hybrid ban active).

**Capture (outnumber, threshold 2).** Same mechanic as menger rank-1: place a stone, each enemy stone adjacent to it is removed if it has ≥2 of YOUR stones among its own neighbours.

**Propagation (influence, r=2, s=1.0, d=0.5).** Each placement adds ±1.0 to placed cell, ±0.5 to BFS-distance-1 active neighbours, ±0.25 to BFS-distance-2 active cells. **Holes block BFS paths**: a cell adjacent to a hole has reduced reach (no dist-1 contribution through the hole).

**Win (threshold-race > 30.0).** Same scoring as menger family.

**Degeneracy check.**
- Soft violation flagged: `sierpinski_threshold_inert`. Worth probing. Empirical: mirror reaches threshold 30 at ply 21 (P1 score 31.25), so the threshold IS reachable in real play. The "inert" violation likely refers to a corner case where the rule blob's threshold field is overridden or mis-typed; it doesn't affect win-condition firing in normal play.
- Hole pattern creates **two distinct sandwich-resistance classes**: (i) 4 truly hole-edge cells with only 2 active neighbours: (4,2), (4,6), (2,4), (6,4). To sandwich these, P2 must commit BOTH of the 2 active neighbours. (ii) Other hole-adjacent cells like (3,1) or (5,1) have 3 active neighbours — P2 needs 2 of 3, slightly easier than uniform 2-of-4.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Pure mirror (tempo baseline)

Sequence: `0,8,2,6,18,26,20,24,1,7,9,17,11,15,19,25,3,5,12,14,21` (21 plies, **P1 wins**).

Plot:
- P1 builds the (0..2, 0..2) corner cluster minus the (1,1) hole (8 stones). P2 mirrors at the (6..8, 0..2) corner minus (7,1).
- After ply 16, both at +20.0 with 8 stones — symmetric.
- P1 expands to row-3 col 3,4,5 — but those are central hole. So P1 expands along the row-2/col-3 edge: (3,0), (3,1), (3,2)=12. P2 mirrors (5,0), (5,1), (5,2)=14.
- **Move 21: P1 plays (3,2)=cell 21 → +31.25, crosses threshold 30. P1 wins.** P2 stuck at +26.75.

Reflection (P1): **First-mover decides under symmetric play.** The 9×9 carpet is small enough that mirror-tempo win is fast (~21 plies vs menger's ~29). Per-stone +2.5 average — high because the r=2 kernel + dist-2 contributions reinforce strongly inside an 8-stone cluster.

### Game 2 — P2 sandwich war

Sequence: `0,9,2,1,18,11,20,3,4,12,5` (11 plies, in progress).

Plot:
- P1 (0,0); P2 (0,1); P1 (2,0); **P2 (1,0) → captures (0,0)** ((1,0)'s P1 neighbour (0,0) has P2 friendlies (0,1) and (1,0) just placed = 2 → captured).
- P1 (0,2); **P2 (2,1) → captures (2,0)** (same pattern).
- P1 (2,2); P2 (3,0); P1 (4,0); P2 (3,1); P1 (5,0).
- After ply 11: P1 = 4 stones, P2 = 5 stones, **scores tied at +4.0**.

Reflection: **2-for-1 stone trade is influence-neutral** — each P2 capture removes 1 P1 stone (loss of +1.0 own contribution) but P2 invests 2 stones × +1.0 = +2.0. Net P2 gain ~ +1.0; P2 captures 2 P1 stones over 4 plies = +2.0 P2 advantage that costs ~4 plies. P1's straight-cluster build over the same 4 plies adds ~+8.0 (+2.0/stone in cluster). **Sandwich is roughly break-even on score-per-ply.** Pilot's "P2 ahead despite P1 going first" claim is correct only mid-trade; over the full game, the tempo advantage re-asserts.

### Game 3 — Hole-edge anchor + capture exchange (independent novelty test)

Sequence: `22,21,23,24,14,15,12,5` (8 plies, in progress).

Plot:
- P1 anchors at (4,2)=22 — a 2-active-neighbour hole-edge cell sandwich-immune to a single-neighbour attack.
- P2 (3,2) — committing one sandwich attacker.
- P1 (5,2) — claims the second neighbour preemptively. (4,2) is now safe.
- P2 (6,2) — extends, threatens (5,2). (5,2)'s 3 active neighbours: (4,2) P1, (6,2) P2, (5,1) empty, (5,3)#. To sandwich (5,2), P2 needs 2 of (4,2)/(6,2)/(5,1). (4,2) is P1, so P2 needs (6,2) AND (5,1) — 2 plies. Currently has just (6,2) = 1.
- P1 (5,1)=14 — denies the sandwich. (5,1) joins the cluster.
- P2 (6,1)=15 — building.
- **P1 (3,1)=12 → captures (3,2)** (P2's isolated stone, P1 friendly count = (4,2) + (3,1) = 2).
- **P2 (5,0)=5 → captures (5,1)** ((5,1)'s P2 friendly count = (5,0) + (6,1) = 2 → outnumber-2 fires).

After ply 8: **P1 = 3 stones (+2.75), P2 = 3 stones (+2.0).** 1-for-1 capture exchange. P1 slightly ahead because of better cluster geometry — (4,2)+(5,2) is a 2-stone hole-edge cluster mutually adjacent with strong dist-2 reinforcement; P2's (6,2)+(6,1) cluster is similar but with one less dist-2 cross-contribution.

Reflection: **Hole-edge anchoring genuinely shifts the capture trade economics**, but only for the truly 2-active-neighbour cells (4 such cells exist on this carpet). Once P1 extends to a 3-active-neighbour cell like (5,1) or (3,1), those cells become sandwich-vulnerable in 2 P2 plies. **The pilot's "hole-edge anchoring is sandwich-resistant" framing is accurate for the anchor cell but breaks down as soon as the cluster extends.** Net effect: the geometric variation adds 0.5-1.0 strategic decisions per game (where to extend vs which cells to defend), not a transformative new strategic axis.

### Strategy guides

**P1 (offence/threshold push):** Anchor at corner (0,0)/(8,0)/(0,8)/(8,8) and immediately fan out into the 3×3-minus-hole sub-carpet. Per-stone +2.0-2.5 in cluster; threshold 30 reached at ~14 stones (~ply 27). **If P2 plays sandwich**, defend by playing the second-neighbour pre-emptively: when P2 places adjacent to a P1 stone, immediately play the OTHER non-hole neighbour to deny the sandwich. **Hole-edge anchor at (4,2)/(2,4)/(6,4)/(4,6)** as alternative — sandwich-immune for the anchor itself, but extensions are sandwich-vulnerable.

**P2 (defence + offence):** Mirror loses by tempo (+31.25 P1 vs +26.75 P2 at ply 21). Sandwich war is the only viable counter — trade 2 P2 stones for 1 P1 capture. The trade is roughly break-even in influence (per-ply); the goal isn't to win on captures but to **slow P1's tempo by 2 plies per capture**. ~3 captures × 2 plies = 6 ply tempo gain → P1 hits threshold at ply ~33 instead of ~27 → P2 has ply 32 to cross instead of P1's ply 27 — within 5-6 plies of each other. **Sandwich war is "play to a draw on tempo" rather than "win on stones".** Best targets: 4-neighbour interior cells (sandwich requires 2 of 4 = 50% coverage); avoid 2-neighbour hole-edge cells (sandwich needs 100% coverage).

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two well-defined ones plus one minor variant:
1. **Cluster-and-race** (P1's playbook). Build a mutually-reinforcing 3×3-minus-hole corner cluster; expand toward the central column. Wins under mirror via tempo.
2. **Sandwich-and-pivot** (P2's playbook). 2-for-1 stone trades at corners; build cluster from sandwich attackers as side-effect. Breaks even on influence per ply, slows P1 tempo by ~2 plies per capture.
3. **Hole-edge anchor variant** (P1's defense). Anchor at one of 4 sandwich-immune hole-edge cells; extensions are still vulnerable but the anchor cell is permanent. Adds 0.5-1.0 strategic decisions per game.

**Counter-play.** Real but knowledge-asymmetric. Mirror = P1 wins; sandwich war = roughly even on tempo; hole-edge anchor = slight edge to P1 if extensions are managed. **Counter-play is depth-2** (mirror→sandwich, sandwich→preempt-the-second-neighbour). Less rich than menger rank-1's depth-3 (mirror→sandwich→re-occupy).

**Short-term vs long-term.** Threshold 30 / per-stone gain ≈ +2.0-2.5 → ~12-15 stones needed (~ply 24-30). Real games average 32 moves. Tactical decisions are 4-6 plies deep. No 10+ ply planning.

**Emergent concepts observed.**
- **Sandwich attack** (same family as menger rank-1 corner sandwich, slightly different geometry).
- **Cluster reinforcement** (dist-1 +0.5, dist-2 +0.25 — strong cluster bonus on r=2).
- **Hole-bottleneck** (BFS path through holes blocks dist-1 reach; central 3×3 hole splits the board into top-half / bottom-half subgames where dist-2 contributions can't cross).
- **Hole-edge anchor immunity** (cells with 2 active neighbours can't be sandwiched without 100% surround).
- **Pre-empt-the-second-neighbour** (P1's defensive response to P2's first sandwich attacker — claim the second cell before P2 can).

**Does the carpet substrate matter?** *Modestly.* The hole pattern creates: (i) 4 sandwich-immune anchor cells, (ii) hole-bottleneck BFS effects on dist-2 propagation, (iii) two distinct sub-game halves separated by the central hole. **But the broad strategic loop — cluster, race, sandwich — works on a holeless 9×9 grid too.** Estimate: substrate adds ~+0.5 strategic-depth points and ~+0.5 novelty points vs holeless 9×9. **Less substrate-coupling than menger games.**

**Does the propagation kernel matter?** Yes, critically — without influence, capture would be meaningless on a 64-cell board. The r=2, decay=0.5 kernel is well-tuned to the carpet's hole spacing (the central 3×3 hole spans about half the board, so r=2 is enough for a corner cluster to influence its inside-edge but not the opposite corner).

**Capture-rule contribution.** Captures fired in 2 of 3 games (Games 2 and 3). Without captures, the game is pure tempo race won by P1. **Captures are the only real balance mechanism.** Captures are decisive when they occur because the trade is influence-neutral but tempo-positive for P2.

**First-mover advantage / seat balance.** Heavily P1-favoured under mirror and hole-edge-mirror (Games 1 and pilot's Game 3). Balanced when P2 plays sandwich war (Game 2 + my Game 3). Knowledge-asymmetric balance.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + capture + threshold-race on a 2-D fractal substrate. Argument:

(a) **Influence-based scoring** is established (Tumbleweed, Sygo, territorial Go).
(b) **Outnumber-2 capture** is Tafl/Ataxx-adjacent — sandwich-and-remove.
(c) **The combination "outnumber + influence + threshold"** isn't published but is an obvious composition.
(d) **Sierpinski carpet substrate** is rare in published abstract games. Most non-rectangular substrates are hex (Hex, Connection Hex) or torus (Torus Go); fractal substrates are essentially un-explored. **This is the strongest novelty axis.** Note: the sierpinski carpet is more well-known than menger sponge, so the substrate novelty here is slightly LESS than menger's.
(e) **Expert-transfer test.** Go + Othello + Hex player would understand in 5-10 minutes. Novel pieces: (i) influence-as-scoring with explicit weights, (ii) outnumber-2 capture trigger, (iii) hole-bottleneck BFS effects.

**Closest known-game analogue:** **A short-range Tafl-Othello hybrid with weight-based threshold scoring on a Sierpinski carpet.** No exact published analogue. *Tumbleweed* (Mike Zapawa, 2020) is closest in influence-scoring pedigree but on hex with no captures.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 = custodian + connection on 2-D grid. R19 carpet rank-1 = outnumber + influence + threshold on 2-D carpet. **Different families.** R19 is "spatial" (board_values as scoring substrate); R8 is "narrative" (build a chain). R8's strength: a single-move chain-completer (custodian-bridge) that's the crown jewel. R19 carpet rank-1 has no comparable single-move pivot — sandwich is binary, threshold-race is linear. **R19 is structurally below R8 because the strategic ceiling is set by linear arithmetic + binary captures, not by a transformative single-move mechanic.**

**Player rebuttal.**
- The **sandwich-as-cluster-builder** combinatorial side-effect is a real discovery — Tafl removes captured stones but doesn't create a P2 cluster from the attackers; Reversi flips ownership but doesn't trade stones for cluster shape; this game's outnumber-2 + influence does both at once.
- **Hole-edge anchor immunity + extension vulnerability** is substrate-specific. The geometry creates strategic heterogeneity that a uniform grid lacks.
- **What subtracts**: (i) the 64-cell board is small — opening tree collapses fast, (ii) the carpet's hole pattern is more well-known than menger's, reducing substrate novelty, (iii) the per-stone arithmetic is mostly linear with one cluster bonus tier, no exponential emergent scaling.

**Novelty score (post-adversary):** **4/10.** Above pure re-skin (2-3) because the outnumber+influence+threshold combination produces sandwich-as-cluster-builder dynamics. Below 5 because the carpet substrate is more well-known than menger and the 2-D board has less spatial richness than 3-D. Anchored against R17 mean 3.50 (a 4 means "modestly above R17 average because of the substrate + family combination, but cluster geometry converges faster than 3-D substrates"). Below pilot's 5 by 1 — the pilot weighted the soft-violation flag less heavily than I do, and the pilot's "hole-edge anchor as sandwich-resistant" claim is true only for 4 of 64 cells, an edge case rather than a strategic axis.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** ce3a09e05cef
**Rules Summary:** Place stones on a 9×9 sierpinski carpet (64 active cells, 17 holes) to accumulate influence on cells you own. Each placement spreads ±1.0 to itself, ±0.5 to BFS-dist-1 active neighbours, ±0.25 to BFS-dist-2 active cells. Outnumber-2 captures fire when an enemy has ≥2 of your stones among its neighbours. First to >30.0 effective influence wins.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** `sierpinski_threshold_inert` — verified in play that threshold IS reachable (mirror crosses at ply 21).

### Scores (1–10)

- **Strategic Depth: 4** — Two viable strategies (cluster-and-race, sandwich-and-pivot) with one geometric variant (hole-edge anchor). Depth-2 decision tree (less than menger rank-1's depth-3). Per-stone arithmetic is linear (+2.0-2.5/stone). 4-6 ply tactical horizon. **Below pilot's 5** because the hole-edge anchor offers fewer options than I'd hoped — only 4 truly sandwich-immune cells.

- **Emergent Complexity: 4** — Sandwich, cluster reinforcement, hole-bottleneck, hole-edge anchor immunity. Same vocabulary as menger rank-1 minus the z-tunnel and re-occupy mechanics (which are 3D-only). The 2D substrate is structurally simpler.

- **Balance: 4** — Mirror = P1 wins by tempo at ply 21 (faster than menger games). Sandwich war is the asymmetric counter, roughly break-even on score-per-ply but tempo-positive for P2. Knowledge-asymmetric balance: PPO learned the counter (trained-vs-trained 0.500), naïve P2 mirror loses 100%.

- **Novelty (post-adversary): 4** — see Phase 4. Carpet substrate is less novel than menger (sierpinski 2-D is more well-known than menger 3-D); strategic family is the same. Below pilot's 5 by 1.

- **Replayability: 3** — 64-cell board with cluster shapes converging to "3×3-minus-hole around any corner" + the 4 hole-edge anchor variants. ~12 distinct opening positions. Below carpet's expected replayability vs menger's 400-cell board. Below pilot's 4.

- **Overall "Would I play this again?": 4** — Once: yes, the sandwich war and hole-edge anchor immunity are interesting to feel. Repeatedly: no — same strategic ceiling as menger rank-1 in 2-D, less spatial richness, opening tree collapses faster. Below pilot's 5 by 1, anchored against R17 mean 3.50.

### CLOSEST KNOWN-GAME ANALOG
**A short-range Tafl-Othello hybrid with weight-based threshold scoring on a Sierpinski carpet.** No exact published analogue. Within R19, this is the **2-D version of menger rank-1's family** — same strategic skeleton, smaller board, less spatial richness.

### KILLER FLAWS
- **Mirror = P1 wins** (structural, ply 21). Same as all R19 games.
- **Knowledge-asymmetric balance.** PPO learned the counter; naïve P2 mirror loses 100%.
- **64-cell board limits opening variety.** ~12 distinct opening positions; opening tree collapses faster than menger games.
- **Cluster shapes converge to "3×3-minus-hole".** Once meta is known, position variety is small.
- **`sierpinski_threshold_inert` soft violation** is flagged but doesn't affect win-condition firing in normal play (verified: threshold reached at ply 21 in mirror). Likely a typo or unused field in the rule blob.
- **Per-stone arithmetic is linear.** No superlinear "killer move" comparable to R8's custodian-bridge.

### BEST QUALITY
**Sandwich-as-cluster-builder.** When P2 sandwiches a P1 corner stone, the 2 P2 attackers form a tight 2-stone cluster as side-effect of attack. This is the same crown-jewel pattern from menger rank-1, transferred to 2-D. **Combinatorially**: attack creates structure, not just removes it. The pilot framed this as the "real prize" of sandwich — I agree. The hole-edge anchor immunity is a secondary virtue but applies to only 4 cells out of 64.

### CARPET STRUCTURAL CONTRIBUTION
**Modest, not transformative.** The carpet adds: (a) sandwich-immunity at 4 hole-edge cells, (b) BFS-distance hole-bottleneck for influence propagation, (c) a top-half/bottom-half subgame split via the central 3×3 hole. **But the broad strategic loop works on a holeless 9×9 grid.** Estimate: flattening to 9×9 would lose ~0.5-1.0 strategic-depth points and ~0.5 novelty points. **Lower substrate-coupling than menger games** because 2-D + 21% hole density is less geometrically rich than 3-D + 45% hole density.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (cross-cutting verdict).

Secondary improvements:
- **Increase threshold to 35-40** to extend games and force more positional development. R17 found shorter games scored worse on depth — this might trade tactical sharpness for strategic surface area.
- **Increase capture threshold to 3** to make sandwich attacks require 3 attackers (impossible at hole-edge cells with 2 neighbours, so corner becomes safe). This shifts balance toward P1 but might be desirable as a balancing knob.
- **Replace central 3×3 hole with 4 separate 1×1 holes** (more like Vicsek) to distribute hole-bottlenecks more evenly and possibly create more mid-board interaction.
- **Add a connection or territory secondary win condition** — purely additive — to give the game a narrative arc beyond the threshold race. R8-family direction.
- **Disable ledger persistence on capture** to make sandwich strictly losing in influence-delta (not just neutral).

### Independent comparison to pilot

| Score | Pilot | Team-1 | Delta |
|---|---|---|---|
| Strategic Depth | 5 | 4 | -1 |
| Emergent Complexity | 5 | 4 | -1 |
| Balance | 4 | 4 | 0 |
| Novelty | 5 | 4 | -1 |
| Replayability | 4 | 3 | -1 |
| Overall | 5 | 4 | -1 |

Disagreement is uniform: I'm 1 point lower on most axes. **Two reasons**: (i) I weight R17 anchoring more heavily and explicitly counter the pilot calibration drift the README warns about; (ii) my hole-edge anchor exploration revealed fewer truly sandwich-immune cells than the pilot's framing suggested (4 of 64 vs the pilot's broader "hole-edge anchoring" recommendation). The actual strategic axis here is narrower than the pilot framed.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-1_gamece3a09e05cef.md`.*
