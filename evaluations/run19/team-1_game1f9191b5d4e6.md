# Run 19 Evaluation — team-1 — Game 1f9191b5d4e6

**Team ID:** team-1
**Game ID:** `1f9191b5d4e6` (Menger rank-1, GE 0.3293, ELO 2402.4)
**Substrate:** Menger sponge (axis 9, 400 active / 729 grid positions, max_degree 6 nominal — most active cells have 3-4 neighbours due to the level-2 hole pattern)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 1f9191b5d4e6` (briefing: `briefing_menger_rank1.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive cells per the level-2 Menger sponge. Active-cell rule: at every base-3 digit, at most one of (x_digit, y_digit, z_digit) equals 1. Cell index = `z·81 + y·9 + x`. 400 active cells. Max degree 6 nominal but rare — every column on a "hole-line" (e.g., x=1,y=4) is fully inactive, so most active cells have 3-4 neighbours, corners 3.

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max 89 turns.

**Action space.** 730 actions = 729 placements + pass. Place-only (D1 hybrid ban active). Legal at any empty active cell.

**Capture (outnumber, threshold 2).** When P places a stone at cell c, for each enemy stone E adjacent to c, if E has ≥2 P-friendly stones among E's own neighbours, E is removed. Capture fires only on the placer's turn.

**Propagation (influence, r=1, s=1.0, d=0.5).** Each placement adds ±1.0 to the placed cell and ±0.5 to its BFS-distance-1 active neighbours (sign = +1 P1, −1 P2). Distance is computed on the holes-removed graph. **Critical**: I confirmed empirically that influence contributions persist after capture (the engine doesn't roll them back), so a captured stone leaves a permanent ledger entry on board_values for both itself and its neighbours.

**Win condition (threshold race > 29.709).** After every move the engine sums each player's `board_values` over cells they currently own. P1's effective = +sum; P2's effective = −sum (because P2 placements are negative). First strict crossing wins; if both cross same-tick, higher margin wins; tie within FP tolerance → draw.

**Degeneracy check.**
- No soft violations flagged.
- Hole pattern is harsh at the level-1 scale: y=3,4,5 z=3,4,5 forms a 3×3 hole-block that severs many cross-substrate routes; (x,y,z) with x_low=y_low=1 etc. is dead. **Result: BFS distance ≠ Manhattan for many pairs**, and cluster shapes that look adjacent in 3D ambient space may be separated on the active graph.
- 6-neighbour cells exist only where all three ternary digits avoid the "1" position at both levels — these are sub-cube corners like (2,2,2), (2,2,6), (6,6,6) etc. Pilot's "interior cells are safer from sandwich" argument applies only to those rare cells.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — Pure mirror (tempo baseline)

Sequence: `0,728,1,727,9,719,81,647,2,726,18,710,162,566,3,725,4,724,11,717,12,716,19,709,27,701,99,629,83` (29 plies, **P1 wins**).

Plot:
- P1 builds an anchored cluster at the (0,0,0) corner — fans out along x, y, z axes as far as the active graph permits. Stones placed: (0,0,0), (1,0,0), (0,1,0), (0,0,1), (2,0,0), (0,2,0), (0,0,2), (3,0,0), (4,0,0), (2,1,0), (3,1,0), (1,2,0), (0,3,0), (0,2,1), (2,0,1).
- P2 mirrors at the (8,8,8) corner (each P1 (x,y,z) → P2 (8−x, 8−y, 8−z)).
- Through move 16 (8 stones each): both at +15.0. Per-stone +1.875 — better than the pilot's +1.75 plus-shape because the anchored fan touches more own-stone neighbours per cell (the corner stone has 3 own-neighbours, each fan-cell has 2).
- Linear tempo: each subsequent stone-pair adds +2.0 each (each stone has 2 own neighbours by the time it's placed). At ply 26 (13 stones each) both at +26.0.
- **Move 27 P1 plays (0,2,1) → +28.0**. Move 28 P2 plays (8,6,7) → +28.0. **Move 29 P1 plays (2,0,1) → +30.0 > threshold 29.709. P1 wins**, P2 stuck at +28.0.

Reflection (P1): The mirror tempo win is purely arithmetic — both sides accumulate at +2.0/stone on a fan, and P1's first move means P1 crosses threshold one ply ahead. P2 has no asymmetric option here unless P2 abandons mirror.

### Game 2 — P2 sandwich war on an interior cell

Sequence: `164,163,263,173,546,547,545,537,544,555` (10 plies, in progress).

Plot:
- P1 anchors at **(2,0,2)** [cell 164] — interior-ish cell with 5 active neighbours, picked because the pilot played at the 3-neighbour corner. Hypothesis: harder to sandwich.
- P2 (1,0,2) [163] adjacent attack.
- P1 extends to (2,0,3) [263] up the z-axis.
- **P2 (2,1,2) [173] — captures (2,0,2) immediately.** Even though (2,0,2) has 5 active neighbours, P2 only needs 2 of them — (1,0,2) + (2,1,2) suffice. The pilot's "interior 5-6 neighbour cells are safer" claim is **only relatively true**: outnumber-2 still fires at 40% coverage of a 5-neighbour cell, which is a 2-move investment. Same trade economics as the corner.
- P1 pivots to far cluster: (6,6,6) [546], P2 chases (7,6,6) [547], P1 (5,6,6) [545], **P2 (6,5,6) [537] captures (6,6,6)** (now 2 P2 of (6,6,6)'s 4 active neighbours — note (5,5,6) and (5,6,5) inactive at L1).
- P1 (4,6,6) [544] — defensive cluster at safer x=4 cells (which only have 2 active neighbours so are sandwich-impossible without 100% surround).
- P2 (6,7,6) [555] — extends P2's far-corner pressure.

Final state at ply 10: **P1 = 3 stones, score +4.5; P2 = 5 stones, score +2.5.** P1 is ahead on score by +2.0 despite being down 2 pieces. **Why**: P1's two captured stones (164, 546) leave permanent +1.0 contributions on the board_values ledger plus +0.5 contributions on their living neighbours; P2's 5 stones are scattered (none mutually adjacent except the (7,6,6)+(6,7,6) pair).

Reflection (P2): The sandwich-as-attack trade is **2-for-1 in stones but ≈ 1-for-1 in influence delta**, because the influence ledger doesn't roll back on capture. P2 has to convert sandwiches into clustered captures — i.e., the captured-corner's neighbours (P2's 2 sandwich stones) need to be mutually adjacent — to net positive on the threshold race. With the menger fractal pattern, two of (1,0,2) and (2,1,2) are NOT axis-adjacent (Manhattan distance 2). So sandwich on interior cells leaves the P2 attackers as scattered singletons. **The pilot's "P2 plays sandwich" verdict is accurate for capture count but underweights the influence-economics: sandwich isn't strictly winning for P2.**

### Game 3 — Seat-swap novelty adversary: "double anchor + ledger-debt"

I play P2 trying to break the game by attacking the threshold race in three different ways: (i) re-occupying captured corners (claim the +1.0 ledger debt); (ii) interfering with P1 cluster scoring by placing P2 stones near P1 stones (each adjacent P2 placement subtracts 0.5 from a P1-owned cell on board_values); (iii) racing my own scattered cluster.

Sequence: `0,1,728,9` (4 plies, intentional check — confirm corner sandwich).

Plot:
- P1 (0,0,0). P2 (1,0,0). P1 (8,8,8) — pivot far. P2 (0,1,0) — captures (0,0,0). After move 4: P1 = 1 stone (8,8,8); P2 = 2 stones (1,0,0), (0,1,0). P1 score +1.0 (own (8,8,8)), P2 score +1.0.

I extended this mentally rather than playing more plies — the dynamic generalizes:
- **Re-occupy mechanic**: After capture, (0,0,0) is empty. If P1 plays (0,0,0) again, it cannot be re-captured because (0,0,0)'s 3 active neighbours are all already P2 — P2 cannot trigger the outnumber rule from any placement adjacent to (0,0,0) (P2 must place at one of (0,0,0)'s active neighbours, but all three are already P2 stones — so P2 cannot place there at all). **The re-occupied corner becomes permanently safe**, and the +1.0 ledger from P1's first (0,0,0) placement plus the new +1.0 own placement = +2.0 on P1's owned cell. This is a genuinely emergent pattern not in the pilot's analysis.
- **Interference mechanic**: P2 placing adjacent to a P1 cluster cell adds −0.5 to that cell's board_values. P1 owns the cell, so P1's score drops by 0.5. Net swing per P2 interference move: P2 score +1.0 (own placement) + 0.5 (P1 score loss) = ~+1.5 swing, vs +2.0 for a clustered P2 own placement. **Interference is slightly worse than building an own cluster**, but it's the only thing P2 can do once P1 has occupied all the high-degree corners.

Engine-verified: corner sandwich at move 4 ✓. Re-occupy / interference patterns derived from rule reading + ledger-persistence empirical check; they are real but rate-limited by the cell topology around captured stones.

### Strategy guides

**P1 (offence/threshold push):** Anchor at one corner (3-neighbour) and immediately fan out in 3 axis directions. The corner's fan is +1.0 own + 1.5 from 3 fan neighbours = +2.5/stone for the first 4 stones, then +2.0/stone for cluster extensions. A 15-stone fan reaches +30 at move 29 (mirror) or earlier (against non-mirror). **If P2 sandwiches the corner anchor, just re-place there once P2's 3 wall-stones are committed — the corner is permanently safe afterward.** Build a second anchor at the opposite corner pre-emptively to deny P2 the "near-origin sandwich + far-corner mirror" double strategy.

**P2 (defence + offence):** Mirror loses by tempo (Game 1, +30 vs +28 at move 29). Sandwich at corners trades 2 stones for 1 capture but the trade is roughly even in influence-delta (Game 2: +4.5 vs +2.5 P2 ahead-on-pieces but P1 ahead-on-score). The only winning P2 line is **clustered sandwiches**: pick a P1 corner where TWO of P2's sandwich-attackers can be mutually-adjacent (which on menger requires the corner's neighbours to themselves be mutually-neighbour). At (0,0,0), the 3 active neighbours (1,0,0), (0,1,0), (0,0,1) are pairwise NOT adjacent (the level-2 hole pattern kills (1,1,0), (1,0,1), (0,1,1)). **So pure-corner sandwich on this menger never gives P2 the clustered-attacker bonus**; P2's 2-stone investment scatters. P2 needs to find a high-degree interior cell where neighbours-of-neighbours form a tight pair; (2,2,2)-class cells have this.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Three.
1. **Anchored fan + threshold race** (P1 mirror-beats and most non-mirror lines). Per-stone +2.0 average; threshold reachable at ~15 stones (~ply 30). Confirmed in Game 1.
2. **Sandwich war** (P2's only counter; +1 stone, −2 stone trade but ≈ break-even on score). Confirmed in Game 2.
3. **Re-occupy + ledger-debt** (P1's counter to P2's sandwich; corner becomes permanently safe after first capture). Theoretical from rule reading + Game 3 short play; the ledger-persistence + neighbour-saturation interaction is emergent.

**Counter-play.** Real but knowledge-asymmetric. The arms race is: mirror (P1 wins by tempo) → sandwich (P2 trades stones) → re-occupy (P1 reclaims corner) → no clean P2 counter past this. **There's a depth-3 strategic decision tree, not depth-2** — that's stronger than I expected for a substrate game.

**Short-term vs long-term.** Threshold 29.7 / per-move gain ≈ +2.0 P1 / +1.5 P2 → ~15-20 plies per side. Real games average 38.8 moves. ~6-10 ply tactical horizon. **The game is fundamentally a race with local capture tactics**, not a positional game. The 400-cell board is large enough that local choices don't immediately constrain global threshold trajectory.

**Emergent concepts observed.**
- **Corner sandwich (3-neighbour sandwich)** — same as pilot.
- **Interior sandwich (5-neighbour, 2/5 ≈ 40% coverage)** — almost as fast as corner; "interior cells are safer" claim from pilot is overstated. Confirmed in Game 2.
- **Ledger persistence** — captured stones leave permanent contributions on board_values. This makes 2-for-1 sandwich trades roughly even in influence-delta, not strictly winning for P2. **This is the most important non-pilot finding in my eval.**
- **Re-occupy mechanic** — captured corner cell becomes permanently safe after re-occupation when all of its active neighbours are already P2. Novel emergent option.
- **Interference attack** — P2 placement adjacent to P1 stones costs P1 −0.5 per neighbour pair. Non-capture pressure on P1's score.

**Does the menger substrate matter?** *Yes, substantially.* The level-2 hole pattern at the (1, 1, *) and (*, 1, 1) etc. lines breaks Manhattan adjacency in non-trivial ways. (1,0,0) and (0,1,0) are NOT adjacent on the active graph (the L1-(0,0,0) sub-cube center (1,1,0) is a hole). So sandwich-attackers at corners CAN'T cluster — limits P2's best play. Flattening to a holeless 9³ cube would give corners 3 mutually-adjacent neighbours and make P2's clustered-sandwich play ~1.0 point of depth stronger. **The menger structure here actively shapes which strategies are viable.**

**Does the propagation kernel matter?** Critically — r=1 vs carpet's r=2. With r=1, distance-2 stones are functionally isolated (no reinforcement). On a fractal substrate where 1-cell holes are common, this means a single hole between intended-adjacent stones breaks the cluster bonus entirely. The optimal P1 cluster shape is forced into "axis fans from corners" — the cell-pattern in active 3D-corners is the only place where 3+ mutually-adjacent stones exist densely.

**Capture-rule contribution.** Captures fired in Games 2 and 3. Frequency: 2 in 10 moves (Game 2). Each capture is 2-for-1 in stones; 1-for-1 in influence (ledger persistence). **Captures buy P2 stone-count parity with P1 (which P2 needs because P1 has tempo advantage), not score advantage.** This is more nuanced than a pure tempo balance mechanism.

**First-mover advantage / seat balance.** P1 wins under mirror (Game 1, +30 vs +28). P1 ahead under P2-sandwich-war (Game 2 partial, +4.5 vs +2.5 at ply 10). Trained-vs-trained 0.500 confirms PPO learned the asymmetric counter, but in human play the P1 advantage is real and substantial. **Knowledge-asymmetric: a P2 player who knows the sandwich war and can build clustered captures might reach 0.4 winrate; pure mirror P2 is doomed.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of known mechanics. Argument:

(a) **Threshold-race influence games** include *Tumbleweed* (2-D hex influence game with own-piece "shoots" replacing placement), *Sygo* (Go territorial weights). The "race to N influence points on a threshold" pattern is published.

(b) **Outnumber-2 capture** is **Tafl/Ataxx-adjacent** (adjacent enemy with majority-friendly). Specifically Ataxx has "infect adjacent" mechanic, Tafl has "sandwich-and-remove"; outnumber-2 sits between them.

(c) **The combination "outnumber + influence + threshold-race"** isn't a published combination but is an obvious composition of (a)+(b). This combination existed in **R18 carpet champions** (this codebase's prior generation) and is the dominant family across R19's top-10.

(d) **3-D fractal substrate.** Menger sponge as a board-game substrate is unprecedented in published literature. 3-D abstract games are rare (Score Four, Qubic, Connect 4-3D); none use influence weights, none use fractal substrates. **This is the strongest novelty axis.**

(e) **Expert-transfer test.** A Go + Othello + Hex + Qubic player would understand the rules in 10 minutes. The novel pieces they'd internalize: (i) the active-cell pattern, (ii) influence-as-scoring with the r=1 short range, (iii) the 3-D outnumber dynamics with hole-pattern-shaped neighbour graphs. The strategic vocabulary they'd build over 10-20 games: corner-sandwich, ledger-debt re-occupation, interference attack — the third is novel-to-me-on-this-eval.

**Closest known-game analogue:** **Influence-based Tafl on a 3-D Menger sponge.** No published analogue. Within this project corpus, the closest is **carpet rank-1** (`ce3a09e05cef`) — same family in 2D with r=2 kernel. R8's Connection Go is a **different family** (capture + connection, not capture + influence + threshold).

**Comparison to R8's Connection Go (8/10 ceiling).** R8 is custodian + connection; this game is outnumber + influence + threshold. **Different families.** R19 is more "spatial" (board_values as scoring substrate); R8 is more "narrative" (build a chain across the board). R19's strengths over R8: (i) the substrate itself adds genuine strategic depth (cluster-shape feasibility), (ii) ledger-persistence creates non-trivial value-economy on captures. R19's weaknesses vs R8: (i) no clear narrative arc — players don't have a "complete a path" goal, (ii) cluster shapes converge to a small set of fan + extensions, (iii) the threshold-race is fundamentally arithmetic, not positional.

**Player rebuttal (P1 + P2).**
- **Ledger-persistence on captures** is the most non-obvious mechanism. Capture = stone removal but NOT influence rollback. This means the board_values is path-history dependent, and "reclaim a captured corner" is a real strategic move, not just a board-state matter. I haven't seen this mechanic in any published abstract game — Tafl, Othello, and Ataxx all have full rollback or no-rollback-because-no-such-substrate.
- **Fractal substrate breaks the 6-neighbour assumption** even for axis-aligned cells. Most active cells have 3-4 neighbours; 6 only at sub-cube corners. The strategic geography is more like Hex on a non-uniform graph than 3-D grid Tafl.
- **What subtracts novelty**: (i) the strategic skeleton (cluster + race + sandwich) is recognizable from carpet rank-1, (ii) the per-stone arithmetic is mostly linear (+2.0/stone for fan, +1.0/stone for isolated, +1.5/stone for partial cluster) — not a multiplicative or non-monotonic structure, (iii) movement is absent (D1 hybrid ban), so the action space is cleanly placement-only, but that's the same for all R19 games.

**Novelty score (post-adversary):** **5/10.** Above pure re-skin (2-3) because: (i) menger substrate is unprecedented and shapes strategy, (ii) ledger-persistence + re-occupy is a genuinely novel emergent pattern, (iii) corner-sandwich-without-clustered-attackers (because of L2 hole at (1,1,0) etc.) is substrate-specific. Below 7-8 because: (i) the strategic family (capture + influence + race) is shared with carpet rank-1, (ii) the cluster shapes converge to "fans from corners", (iii) the per-stone arithmetic is dominantly linear. Anchored against R17 mean 3.50 (a 5 means "noticeably above R17 average because of the substrate, but no headline mechanic that R8 didn't already have") and R8 8/10 (significantly below — R8's connection-bridge is a single-move chain-completer, this game has no comparable single-move pivot).

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** 1f9191b5d4e6
**Rules Summary:** Place stones on a 9×9×9 menger sponge (400 active cells of 729) to accumulate influence on cells you own. Each placement spreads ±1.0 to itself and ±0.5 to direct active neighbours; outnumber-2 captures fire when an enemy stone has ≥2 of your stones among its neighbours (capture removes the stone but the influence-ledger persists). First to >29.709 effective influence wins.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 nominal but typically 3-4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Three viable strategies (anchored-fan, sandwich war, re-occupy/interference) form a depth-3 decision tree. Per-stone arithmetic is dominantly linear, but the ledger-persistence + cluster-shape constraint adds mild non-linearity. Cluster shape forced by the level-2 hole pattern into "fans from sub-cube corners". Above carpet rank-1 expectation by ~0.5 because the third strategy (re-occupy) is genuinely novel-to-this-substrate. Below the R17 best (4.14) by enough that I round to 5; below R8 (8) by considerable margin.

- **Emergent Complexity: 5** — Sandwich + cluster + ledger-debt + interference is a non-trivial emergent vocabulary. The ledger-persistence on captures is the standout — creates a "state-history matters even after stones disappear" property absent from clean Tafl or pure Othello. Corner re-occupy as permanent-safety is emergent. But cluster shapes still converge to a small set, capping emergent variety.

- **Balance: 4** — Mirror = P1 wins by 2 points at move 29 (Game 1). P2's only line is sandwich war which is influence-neutral (Game 2: P1 +4.5 vs P2 +2.5 with P2 up 2 stones). Knowledge-asymmetric: PPO learned the counter, but a player without the sandwich-war book-learning is doomed to lose 100% as P2. The trained-vs-trained 0.500 reflects a learned counter, not a structurally fair game.

- **Novelty (post-adversary): 5** — see Phase 4. The menger substrate + ledger-persistence is the novelty driver. The strategic family (capture + influence + race) is shared with carpet rank-1.

- **Replayability: 4** — 400 cells gives more variety than carpet's 64, but cluster shapes converge to fans from sub-cube corners (8 such corners). Once the sandwich-war/re-occupy meta is known, opening branches collapse. Below carpet rank-1 by 1 because the 3-D substrate doesn't open as many distinct openings as the cell count alone would suggest.

- **Overall "Would I play this again?": 4** — Once: yes, the ledger-persistence + re-occupy interaction is interesting to feel. Repeatedly: no — the strategic ceiling caps around "find the right cluster shape and race", and the asymmetric balance (P1 mirror-wins) makes seat-swap mandatory for fair pairs. Below pilot's 5 because I weight the cluster-shape monotonicity and balance-asymmetry more heavily than the novelty-driver.

### CLOSEST KNOWN-GAME ANALOG
**Influence-based Tafl on a 3-D Menger sponge.** No published analogue. Within this project corpus, the closest is **carpet rank-1** (`ce3a09e05cef`) — same strategic family, 2D version with bigger r=2 kernel; or **R18's outnumber-influence champions** which used the same family on 2D grid.

### KILLER FLAWS
- **Mirror = P1 wins** (structural, +30 vs +28 at move 29). Same as carpet rank-1 and all R19 games. Pie rule is the obvious fix.
- **Knowledge-asymmetric balance.** PPO learned the sandwich-war counter; naïve P2 mirror loses 100%. The asymmetry is a 0.5 → 0.0 shift conditioned on P2 strategy depth.
- **Cluster shapes converge.** Once you know "anchored fan from a 3-neighbour corner", the opening tree collapses to ~8 corner choices × ~4 fan-direction choices. Not many genuinely different positions reachable.
- **Per-stone arithmetic is mostly linear.** +2.0/stone for fan, +1.5 for partial cluster, +1.0 for isolated. There's no superlinear "killer move" comparable to R8's custodian-bridge chain-completer.
- **r=1 amplifies hole-routing penalty.** A single 1-cell hole between two intended-adjacent stones eliminates reinforcement entirely; r=2 would soften this.

### BEST QUALITY
**Ledger-persistence on captures + the re-occupy mechanic.** Captures don't roll back board_values, so a captured stone leaves a permanent +1.0 contribution on its cell. Re-occupying a captured corner (whose 3 active neighbours are all the P2 attackers) creates a permanently-safe P1 cell — P2 can't trigger another sandwich because all of (0,0,0)'s neighbours are already P2 and outnumber-2 fires only on the placer's turn. This generates a depth-3 strategic decision tree (mirror → sandwich → re-occupy) that's genuinely substrate-shaped, not just rule-shaped. The pilot didn't surface this, and it's the most interesting thing about the game.

### MENGER STRUCTURAL CONTRIBUTION
**Substantial. The fractal pattern shapes which strategies are viable**, not just which cells exist. Specifically: the level-2 holes at (1,1,*), (1,*,1), (*,1,1) etc. mean **corner-sandwich attackers are NEVER mutually adjacent** (the L1 sub-cube center is always a hole), so P2's sandwich attackers always scatter — limiting P2's score economy. On a holeless 9³ cube, the same rules would let P2 cluster sandwich-attackers, gaining ~1.0 point of P2's score economy. **The menger substrate makes the game more P1-favoured than its rules alone would**, and that's a real substrate-driven strategic axis. Estimate: flattening to holeless 9³ would lose ~0.5-1.0 strategic-depth points and shift balance from P1-favoured to roughly even (gross balance, not seat-swapped).

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same as pilot, same as cross-cutting verdict). Mirror = P1 win is the structural problem, and pie rule punishes any opening strong enough to mirror profitably.

Secondary improvements:
- **r=2 propagation** would soften the hole-routing penalty and let players span single-cell holes, opening up cluster shapes beyond fans-from-corners.
- **Increase capture threshold to 3** would make corner-sandwich impossible (3-neighbour cells need 3 attackers, but only 3 neighbours exist). This shifts balance toward P1 (corners safe) and might introduce a new dynamic where P2 attacks higher-degree interior cells exclusively.
- **Add a secondary win condition** (e.g., 3-stone connected line through the board) — purely additive — to give the game a narrative arc beyond the threshold race. Closest to R8's family that the eval report identifies as the all-time ceiling.
- **Penalize ledger-persistence**: subtract captured stones' contributions from board_values on capture. This would make sandwich strictly losing in influence-delta and force P2 to a different strategy entirely. May tank PPO learning curves; safer as an experimental fork.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-1_game1f9191b5d4e6.md`.*
