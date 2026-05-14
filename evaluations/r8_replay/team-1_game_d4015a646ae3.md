# R8 Replay Eval — team-1 — Game d4015a646ae3 (Connection Go)

**Team ID:** team-1
**Game ID:** `d4015a646ae3` (R8 top-1 by ELO, Feb-2026 rating 8/10; GE 0.386, depth 0.545, ELO 2304.6)
**Substrate:** flat 2D grid (axis 8, 64 active cells / 64 total, max_degree 4, pie_rule=False)
**Evaluator:** single agent team running P1, P2, and Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d4015a646ae3 --db genesis_v2_run8.db`

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, 64 active cells, no holes. Cell index = `y*8 + x`. Max_degree = 4 for interior cells (3 for edges, 2 for corners). **No diagonal adjacency.**

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100 (effectively non-binding — games end at 13–17 plies).

**Action space.** 65 actions = 64 placements + 1 pass. Place-only. No move actions.

**Placement.** Any empty cell, no first-move restriction.

**Capture rule — `surround`.** **The briefing is materially wrong here.** Briefing says "≥3 of the placer's stones adjacent to the enemy stone." Engine code (`engine_v2.py:606-620` `_capture_surround`) implements **real Go-style group capture by liberties**: after a placement, the engine collects all enemy groups adjacent to the placed cell, counts each group's empty-cell liberties, and clears any group with 0 liberties. The `threshold: 3` parameter is **completely ignored** by surround capture (it is consulted only by `_capture_outnumber`).

Verified empirically: a corner P1 stone at (0,0) with 2 liberties is captured exactly when both liberties (1,0), (0,1) are filled by P2 — pure Go semantics. With the briefing's outnumber-3 interpretation, this capture would NOT fire (2 < 3); with the actual liberty-zero implementation, it DOES fire.

This is good news for the game: real Go capture is strategically richer than outnumber-3 would be. But it is ALSO bad news for the briefing's strategic-notes paragraph 5 — interior single stones are NOT capturable by "3 of 4 neighbours" alone; they need full liberty-encirclement, which means filling all empty cells immediately adjacent. Corners (2 liberties) are easy; edges (3 liberties) are medium; interior stones embedded in friendly chains are nearly uncapturable.

**Propagation — `influence`, r=3, strength≈0.715, decay≈0.751.** On each placement, the engine adds `±strength·decay^d` to `board_values[cell]` for every cell within graph distance ≤3. Footprint per stone: d=0→±0.715, d=1→±0.537, d=2→±0.403, d=3→±0.303. Clamps to [−100,100]. **This field is observed but not load-bearing for the win condition.**

**Win condition — `connection` (Hex-style, asymmetric).** First player to form a contiguous 4-adjacent chain of their own stones from one assigned face to the opposite face wins. P1's goal: connect top (y=0) to bottom (y=7) through P1 stones. P2's goal: connect left (x=0) to right (x=7) through P2 stones. **The two goals cross.** This is structurally identical to Hex on a square grid — except square grid lacks Hex's diagonal-bridge connectivity, so chain-building is harder and chains are easier to cut.

The `threshold: 0.5` parameter on the connection rule is vestigial (`topology.py` BFSes on owned cells, ignores threshold).

Max-turn timeout: no draw-resolution rule for connection-wins; in practice 8×8 races finish in 13–17 plies, well below 100.

**Pie rule.** Off. R8 predates pie. First-mover advantage uncompensated.

**Helper warning.** The header line `Win: threshold-race > 0.500` is **hardcoded** garbage; the actual win is connection. The `P1/P2 effective score` numbers are influence-pressure metrics only; use `Done=True Winner=N` for actual win detection.

**Degeneracy check.**
- Briefing's surround capture description is wrong (outnumber-3 → actually Go liberties). Real semantics are richer and more interesting; this is a positive correction.
- Briefing's strategic note 5 ("single P2 cell at interior P1 chain captured when 3 of 4 neighbours are P1") is incorrect — group liberty semantics apply, not neighbour-count.
- 4-neighbor square grid + connection-win = Hex-without-bridges. Diagonal stones are NOT connected. This is a structural weakness relative to true Hex.
- No pie rule on a connection game with no compensating mechanic → P1 first-mover advantage is uncompensated.

---

## Phase 2 — Strategic Play

All sequences engine-verified through `eval_run20_helper.py`.

### Game 1 — Sanity: P1 unopposed vertical wall

Sequence: `0,7,8,15,16,23,24,31,32,39,40,47,48,55,56` (15 plies, P1 wins).

P1 walls x=0 column (cells 0,8,16,24,32,40,48,56 = y=0..7), P2 mirrors x=7 column. **P1 wins on move 15** by completing top↔bottom chain. P2's parallel x=7 wall is **structurally pointless** — P2 needs *horizontal* connection, not vertical. No captures.

Confirms asymmetric-goal property. P2 needs ≥9 plies after P1's first to win (8 stones + 1 extra to recover seat asymmetry), so P1's straight-wall race wins in 15 plies vs any same-strategy P2.

### Game 2 — P1 column-race vs P2 horizontal-race (correct seat assignment)

Sequence: `3,32,11,33,19,34,27,36,35,37,43,38,51,39,59` (15 plies, P1 wins).

Plot:
- P1 builds x=3 column (cells 3,11,19,27,35,43,51,59), 8 stones, y=0..7.
- P2 builds y=4 row (cells 32,33,34,36,37,38,39 = x=0,1,2,4,5,6,7), 7 stones, **with the y=4,x=3 cell taken by P1's chain**.
- P1 finishes vertical chain at move 15 (places at (3,7)). Even though P2 has y=4 row from x=0..2 and x=4..7, it is **split** by P1's stone at (3,4). P2's chain is two disjoint groups, neither connecting left to right.

This is the textbook racing outcome: **if both players naively race straight-line walls, P1 wins by tempo**. P1's chain also conveniently cuts P2's parallel chain at the same row.

### Game 3 — P2 blocker strategy

Sequence: `3,35,11,34,19,33,27,32,43,36,51,37,59,38,12,39` (16 plies, **P2 wins**).

Plot:
- P1 races x=3 column; **P2 plays (3,4)=cell 35 as move 2** to pre-place the cut.
- P1 reaches y=0..3 then jumps to y=5..7 (via (3,5), (3,6), (3,7)) — but **(3,4) is owned by P2**. P1 has two disjoint segments.
- P2 fills row y=4 left-of-cut: (2,4), (1,4), (0,4) — and right-of-cut: (4,4), (5,4), (6,4) — then completes at (7,4) on move 16.
- P1 attempted (4,1) on move 15 as a side-route stone but had no time to build a 10+ stone snake around the y=4 row.
- **P2 wins by completing left↔right horizontal chain at move 16.**

**This game contains the central tactical insight: a single early-placed P2 cut on P1's likely column completely defeats P1's straight race.** P2 trades 1 stone (the cut) to force P1 into a multi-move detour around row y=4 — a detour that requires ≥10 stones vs P2's 7 remaining row stones.

### Game 4 — P1 zig-zag escape attempt (FAILS — exposes a structural limitation)

Sequence: `3,35,11,34,19,33,27,32,28,36,29,37,21,38,22,39,…` (16 plies, P2 wins).

P1 tries to route around the y=4 block: (3,0), (3,1), (3,2), (3,3), then jumps right to (4,3), (5,3), (5,2), (6,2) — building a snake that goes up-and-around. But:
- Each detour step takes 1 ply.
- P2 only needs 7 more row-stones (after (3,4) cut + 4 more setup placements) to complete left-right wall.
- P1's snake needs to traverse ≥10 cells to bypass row y=4 from top half to bottom half.
- **P1 simply cannot keep tempo.**

P2 wins by completing y=4 row on move 16.

### Game 5 — Surround capture mechanics test

Sequence: `0,1,63,8,62` (5 plies, capture verified).

Plot:
- P1 at (0,0); P2 plays (1,0). P1 plays distant (7,7); P2 plays (0,1).
- After P2's move 4, P1's (0,0) group has 0 liberties (corner with 2 neighbours, both P2). **Capture fires.** Engine: `Captures (cleared to empty): ['(0,0)']`. P1 piece count drops 2→1.

**This is real Go capture, not outnumber-3.** Verified the engine implementation matches the source code (group liberty BFS), not the briefing's text.

### Game 6 — P1 diagonal-bridge naivety probe

Sequence: `3,32,12,33,21,34,30,35,46,36,55,37,63` (13 plies; not finished, illustrative).

P1 places along a diagonal: (3,0), (4,1), (5,2), (6,3), (6,5), (7,6), (7,7). **These stones are NOT connected** — 4-neighbor adjacency means (3,0) and (4,1) are non-adjacent. P1 has 7 stones forming 7 separate 1-stone groups.

This is a structural limitation of the substrate: real Hex has diagonal-bridge connectivity (two-step diagonals are protected), allowing flexible path-routing. **8×8 4-neighbor grid has no bridges** — chains must be strictly orthogonal. This makes counter-routing around an opponent block much harder than on Hex.

### Strategy guides

**P1 (offence, goal: top↔bottom):** Pick a column. Race up. If P2 cuts your column with a single stone, you almost certainly lose unless you've pre-built a wide threat across multiple columns. The substrate gives no path-flexibility (no bridges). Best practical play: start in a corner column where the opponent's blocker move has lower leverage (less central influence). Threaten two columns simultaneously if possible — but each requires its own stones, so this is hard.

**P2 (defence, goal: left↔right + denial):** **Play the cut.** Move 2 should be at (3,y_mid) or whichever column P1 picked, in the row you intend to use for your own connection. This single move converts the structural P1 advantage into a P2 advantage: it costs you 1 stone but forces P1 to detour ≥10 stones around your row. Then build your row. Total: 8 plies (cut + 7 horizontal) vs P1's ≥9 plies (start + 7 column + ≥1 detour); P2 wins by 1 move.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Two, asymmetric by seat:**
1. **P1 column race** — only works if P2 doesn't cut early.
2. **P2 blocker + horizontal race** — beats naive P1 in 16 plies.
3. (P1's counter — multi-column threat + detour — exists but I could not find a winning P1 line against committed P2 blocker on 8×8.)

So there's roughly *one and a half* strategies. P2 has the dominant strategy when P1 plays naively; P1's only counter is to threaten two columns at once, which dilutes their tempo.

**Counter-play.** **Partial.** Cut beats race; race-with-feints could beat cut, but the small 8×8 board doesn't give P1 enough room to feint convincingly. PPO would presumably learn this (verified by the briefing's `trained_vs_random: 0.84 / 0.56` — P1 win-rate vs random is higher than P2's, but symmetric trained-trained data wasn't quoted).

**Short-term vs long-term.** Decision horizon is short — 8 stones to win → 4 placements lookahead is sufficient for most plans. **The game ends in 13–17 plies.** No medium-term territory. No long-term ko-style threats (no captures fire in equilibrium race-play; only in adversarial setup tests).

**Emergent concepts observed.**
- **Single-stone cut.** A P2 stone at the midpoint of P1's column severs P1's vertical chain. Asymmetric to Hex where cuts cost more.
- **Tempo lockout.** Once P2 has committed the cut, P1's detour is structurally too long. The 8×8 axis is too short for path-feinting.
- **No bridges.** 4-neighbor grid means diagonals don't connect. Hex's signature ladder mechanic is absent.
- **Ghost capture mechanic.** Go-capture is technically present but virtually never fires in race-play because both players' chains have abundant liberties on the open sides. Only corner-suicide setups trigger it.
- **Influence is decorative.** The board_values field shapes the engine's threshold-race output for PPO observation but has zero effect on the connection-win outcome. PPO sees it; humans should ignore it.

**Does the 8×8 grid substrate matter?** Compared to:
- **A 9×9 or 11×11 grid:** larger axis would help P1 (more room to feint around a cut). 8×8 may be the smallest interesting axis for this rule set.
- **Hex topology (6-neighbor):** would add Hex's bridge connectivity → P1's detour cost drops significantly → game becomes closer to true Hex (which is well-known to be P1-favored without pie).
- **Carpet/menger fractal:** would add hole obstacles that constrain both players asymmetrically; unclear whether net positive.

**Does the propagation kernel matter?** **No.** Influence is observation noise. Removing it would not change the optimal strategy for either side. The Hex backbone (connection-win) does all the work. If anything, influence creates a *spurious* signal that PPO might over-weight; this could explain why the engine's threshold-race score (which influence does drive) shows large P1 leads even in games P2 wins (cf. Game 3, P1 effective score 12.6 > P2's 14.3 only at the final move, but P2 had won by connection earlier).

**Capture-rule contribution.** **Near-zero in equilibrium.** Go-style group capture is real and verified, but on 8×8 with chains running edge-to-edge, both players' connection chains have abundant outside liberties. Captures would only fire if a player voluntarily places a stone in a corner with both edges already blockaded, which is suicidal and never voluntarily played. **The capture rule is essentially vestigial under connection-win racing.** It could matter if max_turns were lowered and forced grinding-out battles, but as configured it's decoration.

**First-mover advantage / seat balance.** **Significant and uncompensated.** P1 wins straight-vs-straight races by 1 tempo (15 vs 16). But P2 can flip this with a cut + race (game 3). Net balance depends on whether PPO learns the cut strategy. R8-era `trained_vs_random` data (P1=0.84, P2=0.56) suggests P1-favoured, but this is vs random, not trained-trained. Without pie rule, this is a real flaw — Hex on a small board with no pie is famously broken for first-mover.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is **Hex on a square grid with Go capture layered on top and an influence field that PPO can observe but humans should ignore.**

(a) **Asymmetric face-connection goals** are **literally the defining property of Hex** (Hein/Nash 1942–47). A grid with two players each trying to connect their own opposing faces via a chain of their own stones is a well-explored design space.

(b) **Surround capture** is Go (Wei-Chi, ≥2000 BCE). The implementation is canonical liberty-zero group capture.

(c) **The combination "Go capture + Hex connection"** as a deliberate hybrid: I am not aware of a published commercial game with this exact recipe. The closest analog inside the broader board-game literature is *Slither* (Corey Clark, 2010-era abstract) which has Hex-style connection with stones that can move/shift, or perhaps *Connections* (Tom Cordell, 1990) which has connection + capture but on a custom topology. But none are well-known. **The hybrid IS novel as a published commercial design** — but not novel as a research design (4-neighbor connection variants of Hex have been studied academically).

(d) **8×8 square grid substrate.** Not novel. Maximally generic.

(e) **Expert-transfer test.** A Hex player + Go player would understand this game in **~5 minutes**. The Hex player learns "stones don't move and there are no bridges (4-neighbor)" → trivial. The Go player learns "you have an asymmetric connection goal; you can also capture by encircling liberties" → trivial. The only "irreducible new piece" is realizing that the influence field is a red herring for the win condition; a beginner might over-weight it.

**Closest known-game analogue:** **Hex on a square 4-neighbor grid, with Go capture as an auxiliary mechanic.** Inside the project corpus, this is the original Connection Go and there is no closer cousin in R17–R20 (all those games dropped connection in favour of threshold-race).

**Comparison to its own R8 reputation.** This is the game that scored 8/10 in Feb-2026 and 0.386 GE in R8. The 8/10 rating was generous in absolute terms but defensible *relative to R8's then-corpus* (the rest of R8 was substantially worse). Under the current R20 rubric, with anchors R17 mean 3.5, R19 mean 4.4, R20 mean 3.7, this game is genuinely better than its R20 contemporaries — but it is not 8/10 in absolute terms. It is "Hex minus bridges + Go capture as decoration + no pie." Real Hex is ~9/10 as a game; this is Hex degraded by substrate and by no-pie.

**Comparison to R19 best (menger top 4.8, carpet top 4.7).** R19 best games were all threshold-race influence games on fractal substrates — they had medium-term territory dynamics that this game lacks. But this game has something they lacked: a **clean, comprehensible win condition that forces global planning**. Connection-win > threshold-race for strategic depth, even on a worse substrate. Net: this game is **more strategically pure** than R19 menger top, but **less subtle**. I'd put it slightly above R19 menger top.

**Player rebuttal (P1 + P2).**
- The asymmetric goal *does* generate real strategic content (P2 blocker discovery is non-obvious). This is more than pure re-skin.
- The Go capture is a verified real mechanic, not a Potemkin rule. But it functions as a *deterrent* (no one places suicidally) rather than as an *active* mechanic, because race-tempo dominates.
- 8×8 axis without pie is genuinely a flaw — too short, too P1-favored. Real Hex is played at 11×11 or 13×13 with pie.
- Influence field is a vestigial PPO observation — adds nothing for game quality, but doesn't actively detract.

**Novelty score (post-adversary): 4/10.** Above pure re-skin (2-3) because the Go-capture + Hex-connection hybrid as a *commercial* game is non-trivial; the asymmetric goal is genuinely strategy-generating; the substrate adds nothing but doesn't subtract horribly. Below "genuinely new" (8-9) because the design is "two known games stuck together" rather than a new mechanic. Anchored against R8 Feb-2026 (8/10) — that rating overstated novelty; this is Hex+Go, neither half is new. Anchored against R19 menger top (4.8) — comparable: that was threshold-race+outnumber on fractal, this is connection+surround on grid. Same novelty tier.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** d4015a646ae3
**Rules Summary:** 8×8 flat grid, alternating placement. P1 wins by chain top↔bottom; P2 wins by chain left↔right (asymmetric Hex-style goals). Go-style liberty capture is available but rarely triggered in race-play. Influence field is observed by PPO but irrelevant for win detection. No pie rule.
**Substrate:** flat grid, axis 8, 64/64 cells, max_degree 4, pie_rule=False.
**Turn Structure:** alternating, 1 piece/turn, max_turns 100 (non-binding).
**Hybrid actions:** no.
**Soft violations flagged:**
- Briefing claims surround capture = outnumber-3 (≥3 placer neighbors). **Engine code implements real Go-style liberty-zero group capture instead.** This is a meaningful documentation bug.
- Briefing's strategic note 5 (corners uncapturable, single interior stones capturable by 3 neighbours) is wrong on both counts: corners ARE capturable (2 liberties → fill both); single interior stones are NOT capturable by neighbour count alone (they're capturable only when their group has zero liberties, which for a chain extending edge-to-edge essentially never happens).
- Briefing's "8×8 axis is narrow" note (point 4) understates: 8×8 is below the minimum interesting Hex size for play balance.
- Helper's `Win: threshold-race > 0.500` header is hardcoded garbage; ignore.

### Scores (1–10)

- **Strategic Depth: 5** — The race-vs-cut dynamic is a real strategic axis. P1 must choose: column-race (loses to cut) or multi-column threat (loses tempo). P2 must commit to cut early or risk pure race-loss. But the 8×8 board is too small to support deep mid-game positioning — 4-ply lookahead is usually enough. Real Hex at 11×11 has documented depth ~7; this 8×8 grid+capture variant is shallower because (a) no diagonal bridges, (b) board too small for ladder/escape lines, (c) capture rule is rarely live. **Engine depth 0.545 understates subjective depth slightly** — there's a real qualitative jump above pure cluster-compounding games, but not enough for Hex-level depth.

- **Emergent Complexity: 5** — The cut-strategy discovery is genuinely emergent (not obvious from rules; took 3 games to find). The "no diagonal bridges" structural surprise (Game 6) is a real player gotcha. Beyond those two, very little surfaces — captures don't fire in equilibrium, influence is irrelevant for play. Two emergent concepts is solid but not exceptional. Better than R20 production median, worse than well-tuned Hex.

- **Balance: 4** — Without pie rule, on an 8×8 connection game, P1 has a real first-mover advantage when both race straight (15 vs 16 ply); P2 has a real counter via the blocker strategy. Whether net balance is 50/50 depends on whether the cut strategy is consistently discoverable by PPO. R8's `trained_vs_random` data (P1=0.84, P2=0.56) suggests P1-favored. With no pie, this is uncorrected. Real Hex addresses this with pie rule precisely because the imbalance is otherwise severe. The fact that R8 predates pie is the binding flaw.

- **Novelty (post-adversary): 4** — see Phase 4. Hex + Go is a known hybrid concept; this game executes it cleanly but doesn't extend it. Influence is a fake fifth mechanic. Substrate is generic. Same novelty tier as R19 menger top (4.8) and R20 top games (4.8).

- **Replayability: 5** — Once the cut-vs-race-vs-multi-column meta is understood, position variety is moderate. P1's choice of column matters (corner vs center has different blocker leverage). P2's choice of which-row-to-block matters. There's enough decision branching that the game is not solved by PPO in 2-3 self-play seeds. But the small board caps the opening tree; openings will converge to a small set within 100 self-plays. Better than R20 production median (which often converges in 10 plies).

- **Overall "Would an agent team play this again?": 5** — A clean, comprehensible game with one genuine strategic axis (race vs cut) and one good emergent pattern (the no-bridges discovery). **Materially better than R20 production mean (3.73) and R19 production mean (4.375).** Slightly above R19 menger top (4.8) and R20 top (4.8) on strategic clarity, slightly below on substrate interest. **Materially worse than the February 8/10 rating.** I'd put it at 5/10 — strong solid above-mean game, but not "elite project anchor." The 8/10 was inflation, possibly because R8's surrounding corpus was so much weaker that this stood out.

### CLOSEST KNOWN-GAME ANALOG

**Hex on a square 4-neighbor grid** (well-studied as an academic curiosity; not commercially published in this form) **with Go-style liberty-capture as a vestigial auxiliary mechanic**. The Hex backbone is the load-bearing component; the Go capture and influence layers add color but do not generate dominant strategies in race-tempo play.

### KILLER FLAWS

- **No pie rule.** Connection games are notoriously broken without compensation for first-mover. Even with the cut counter-strategy, this is a real flaw. Real Hex universally uses pie.
- **8×8 is too small for the rules.** Cut strategy is too powerful because P1 has no room to feint. Real Hex starts at 11×11. The small axis collapses the strategic horizon.
- **No diagonal bridges on 4-neighbor grid.** Hex's strategic richness comes substantially from bridge connectivity; a 4-neighbor grid lacks this, making chains brittler and counter-routing infeasible. Game 6 directly illustrated this: P1 played 7 stones along a diagonal and had 7 disconnected groups.
- **Capture rule is decoration in equilibrium.** Go-style group capture verified to work, but never fires in race-play because chains have abundant outside liberties. The capture rule is real but unused.
- **Influence field is observation noise.** It shapes PPO's view but has zero effect on the connection-win outcome. Removing it would not change optimal play.
- **Briefing documentation is wrong about the capture rule** (outnumber-3 description vs actual Go-liberty implementation). This means the project's understanding of *why* this game scores well may be miscalibrated — it scores well not because of surround-3 + connection but because of Go-libcap + Hex-connection.

### BEST QUALITY

The **cut vs race vs multi-column-threat strategic axis** is the only crown-jewel mechanic, and it is good. P2's discovery of "play (3,4) at move 2 to defeat P1's column race" is a non-obvious, durable, replayable strategy. This is more than R20 production games offer — most R20 games are pure cluster-compounding with no counter-strategy. **Connection-win generating global-plan pressure is the unifying win-condition principle that should be preserved when designing R21+.**

### GRID STRUCTURAL CONTRIBUTION

**Flat 8×8 grid is the wrong substrate for connection-Hex hybrid.** The asymmetric goals + Go capture need *more* room and *richer* connectivity (hexagonal neighbours or larger axis) to support deep counter-strategies. R19's finding that menger > carpet > grid for substrate quality holds here — but with a caveat: the menger/carpet evaluations were of threshold-race games, not connection games. **Connection on hex 11×11 would likely be a 7/10 game.** Connection on this 8×8 grid is a 5/10. The substrate is degrading what would otherwise be a much better design.

### IMPROVEMENT IDEAS

**Single best change: enable pie rule.** Without pie, P1's tempo advantage on a small board is real and uncorrected. With pie, P2 can swap if P1 takes a centre-strong opening, neutralizing the imbalance. This is the standard Hex prescription and would immediately move this game from 5/10 toward 6/10.

Secondary improvements:
- **Move to hex topology (6-neighbor) or larger square axis (11×11).** Either would restore Hex's diagonal-bridge feel and give P1 enough room to feint against the cut.
- **Remove the influence field** — it adds nothing to play, and PPO may be over-weighting it during training. Cleaner observation → cleaner learned policy.
- **Reinstate surround capture as outnumber-3** (i.e., make the briefing's description true) — outnumber would actually fire in equilibrium play, creating real capture dynamics that the current Go-libcap implementation does not. Or alternatively, keep Go-libcap but lower max_turns so games are forced into closer territorial battles where capture fires.
- **Document the capture rule correctly** so the project's understanding of this game's strategic content is calibrated.

---

## Calibration note for the campaign

The R8 February 2026 rating of 8/10 on this game appears **inflated by ~3 points relative to current R20 rubric**. Under the current protocol with current anchors (R17 mean 3.5, R19 mean 4.4, R20 mean 3.7, R19 menger top 4.8, R20 top 4.8), I rate this game **5/10** — better than R20 production mean (3.73) and R19 production mean (4.375), comparable to R19 menger top (4.8), but not "elite anchor" territory.

If other teams in the parallel campaign converge on similar scores (4-6), the implication is: **the February rating was inflated, calibration has drifted up by ~3 points, R8 is not a stable depth anchor at 8/10 under current rubric**. The next-action implication: do not redesign GE around recovering an 8/10 for this game; redesign GE around recovering a 5–6/10 for this game and 7+/10 for any *new* design that genuinely matches Hex's depth (which would require larger axis + pie + better connectivity).

If other teams diverge widely (range >4 across teams), the implication is that agent-eval itself is the noisy instrument; that needs fixing before fitness redesign.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/r8_replay/team-1_game_d4015a646ae3.md`.*
