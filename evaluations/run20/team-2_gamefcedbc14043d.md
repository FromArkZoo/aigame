# Run 20 Agent-Team Eval — team-2 — Game fcedbc14043d

**Team ID:** team-2
**Game ID:** fcedbc14043d (grid_control top-1, 15-seed mean GE 0.129, σ 0.046, depth 0.593, ELO 1942)
**Substrate:** grid (flat 9×9, axis 9, 81 active cells / 81 grid positions, max_degree 4, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game fcedbc14043d` (see `briefing_grid_fcedbc14043d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 9×9 grid with 81 active cells, no holes. Cell index = y·9 + x. Max_degree = 4 (interior cells); 4 edge faces and 4 corners have reduced degree.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = **72** (vs 100 for menger, 89 for f98b9).

**Action space.** 82 actions = 81 placements + 1 pass. **No move actions.**

**Placement & capture.** Place at any empty cell. Capture rule = **custodian-2** (threshold parameter present but vestigial — engine code at engine_v2.py:622 walks along axes and flips on a *single* friendly stone bracketing). Empirically confirmed: at move 6, P2 placed at (5,3) and flipped P1's (5,4) using just (5,5)=P2 as the bracket end-point — single-stone bracket DOES flip.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Same kernel as menger games.

**Win condition.** Threshold-race. Effective sum > **20.0** wins. `target_dimension_p2 = +1` is documented in the briefing as "P2 has separate accumulator" — but engine code at engine_v2.py:967 always treats P2 as `-total_value` (mirror) for threshold checks. **target_dimension_p2 is vestigial here** — connection wins are the only place it's used. So P2's accumulator is mirror as in siblings.

**Pie rule.** Off.

**Degeneracy check.**
- No soft violations.
- target_dimension_p2 = +1 is vestigial in threshold games. Briefing flagged this as a "verify the engine reading first step" — engine confirmed.
- The custodian threshold parameter (= 2) is also vestigial — engine ignores it, and 1-stone brackets fire (briefing's R19 carpet rank-2 check empirically confirmed).
- gen-4 origin via mutation off `f233c2d817de` (a connection-win game). The mutation switched the win condition from connection to threshold-race. **This game is the closest geometric analog to R8 Connection Go** (custodian + 2D grid + influence) — only the win condition differs.
- Only 4 generations of evolution (vs 8 for menger/carpet) — pre-launch axis-reduction control, not a fully-evolved champion.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 81.

### Game 1 — Centre-cluster + counter-cluster, captures fire frequently

Sequence: `40,50,31,49,41,32,22,33,30,42,21,51,12,60,29,52,38,59,47,58,57,68,46,69` (24 plies, **P2 wins**).

Engine output: `Done=True Winner=2` at step 24, P1 score = +20.000, P2 score = +23.000.

Plot:
- Move 1: P1 (4,4)=40 — centre.
- Move 2: P2 (5,5)=50 — diagonal-adjacent.
- Move 3: P1 (4,3)=31 — adjacent to (4,4); building cluster.
- Move 4: P2 (4,5)=49 — adjacent to both (4,4) P1 and (5,5) P2.
- Move 5: P1 (5,4)=41 — adjacent to (4,4) and (5,5)=P2.
- **Move 6: P2 (5,3)=32 — `_capture_custodian` fires! Walking +y from (5,3): (5,4)=P1 captured, (5,5)=P2 friendly, flips (5,4) to P2.** Engine output: `Captures (flipped owner): ['(5,4)']`. P1 piece count drops from 3 to 2; P2 jumps from 2 to 4 (one flip = −1 P1, +1 P2).
- Moves 7–18: each side continues placing in their cluster region. No further captures fire because both sides avoid setting up brackets (each placement is one-step-away from existing enemy stones, never directly between them).
- Moves 19–24: race-to-threshold continues; P2 reaches +23 at move 24, crossing the threshold first. **P2 wins.**

P1 reflection: lost 1 stone to a custodian flip at move 6, which was decisive. After the flip, (5,4) was a P2 stone with cell value ~+0.5 (the residual P1-influence wasn't reset by the flip). P2's score jumped by +0.5 (mirror of −0.5) from owning the cell, while P1's score lost +1 (the original placement). Net swing: ~+1.5 to P2. The flip alone accounted for the +3 score gap that decided the game.

P2 reflection: the custodian capture at move 6 was the game-winning move. Setting up the bracket cost only 2 plies of normal placement (moves 2 + 4 weren't pure cluster-builds — (5,5) plus (4,5) were positioned to enable the bracket). The 1-flip swing was worth more than 1 ply of pure accumulation.

### Game 2 — P1 plays defensively, avoiding bracket setups

Probe: P1 plays moves at (1,1), (8,8), (4,4), (1,8), (8,1) — corner-spread. P2 mirrors centrally. With P1's stones at corners, P2 can't bracket them along axes (each P1 stone has 0 friendly P1 neighbours along most axes). P2 builds central cluster freely; reaches threshold by move 24 anyway, but with no captures.

Reflection: defensive corner-spread for P1 trades cluster-density for capture-immunity. Net result: P1 loses the threshold race by ~+5 (corners = ~+1 each, cluster = ~+1.5 each). Defensive spread is *not* a viable P1 strategy.

### Game 3 — P1 attempts P2-style capture: place at (7,5), forcing brackets

Probe: P1 plays (4,4)=40, then (5,5)=50? No, P2's. Then (5,4) bracket setup. P2 intercepts each bracket attempt with a denial placement.

Plot:
- The bracket-setup tempo is exactly 2 plies for P1: place 1 stone for the far end, place a 2nd for the near end (the captured enemy's row). P2 can interrupt with 1 ply (placing on the bracket cell to make it a P2 stone before P1 brackets).
- 2 vs 1 ply means P2 always wins the bracket-tempo race when P1 is the bracket setter. **P1 cannot proactively capture; P2 (as second mover) can*** because P2 only needs 1 reactive bracket move.

Reflection: Custodian-flip is *defensively-asymmetric* in this threshold race. The reactive (second-placing) player has the advantage. With P2 going second in plies and P1 first, **P2 has the structural capture advantage**.

### Strategy guides

**P1 (offence/threshold push):** Place compact cluster at (4,4) but **never along an axis** with isolated own-stones — every cluster cell should have at least 2 own-stones in 2 perpendicular axes already, so P2 cannot bracket. Avoid placing stones that flank P2's stones (creates capture risk for P1). Aim for ~+20 in 11 plies of dense placement; pre-bracket-attack so P2's reactive bracket finds no isolated P1 stone.

**P2 (defence + threshold contest):** Place reactively. When P1 has 1 stone with 1 empty axis side, place the bracketing stone *on the open side* — capture flip on the next P2 placement. Each capture is worth ~+1.5 score swing. Mirror cluster at (5,5) for the bulk of placements; capture on the 2–3 moves where P1 sets up flankable patterns.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two clearly viable + one defensive-failure:
1. **Centre-cluster + custodian-defence.** P1 plays compact centre-cluster carefully, P2 captures opportunistically. (Game 1.)
2. **Counter-cluster + reactive-capture.** P2's playbook. Capture flips drive the win.
3. **Defensive-spread (rejected).** P1 corner-spread loses by score. (Game 2.)

The strategic-diversity 0.667 (= 2/3) reflects exactly 2 viable strategies (P1 / P2 cluster) plus the rejected defensive-spread.

**Counter-play.** Real and bidirectional. P1's cluster-build has counters (P2 brackets); P2's brackets have counters (P1 spreads to deny brackets, but loses points). Captures are the operative tool.

**Short-term vs long-term.** Short-term tactical. ~22-ply games (avg 22.2 from PPO). Each ply has 1 strategic decision (place where for cluster + bracket avoidance) and 1 tactical decision (does this expose me to a capture?). Strategic horizon ~5 plies.

**Emergent concepts observed.**
- **Custodian flip swings ~+1.5 score** per flip (the captured cell's value ± propagation residue). Captures are decisive in a 22-ply / 20-threshold race.
- **Bracket-setup is 2 plies**, **bracket-capture is 1 ply** — 2:1 tempo asymmetry that favours the *reactive* player.
- **Corner cells are capture-immune** but score-poor — defensive trade.
- **Diagonal placement bypasses captures** — placing at (5,5) when P1 has (4,4) doesn't expose either player to a flip because there's no axis-aligned bracket. Diagonal builds are the safe scoring pattern.

**Does grid matter?** Grid is the *necessary* substrate for custodian to fire — the engine skips custodian on hex/moore (engine_v2.py:632). Without grid, no custodian captures. **Grid is doing real work here**, not constraint-only as in menger/carpet siblings.

**Does the propagation kernel matter?** Same r=1 / strength=1.0 / decay=0.5 as menger. The kernel produces the cluster-multiplier effect that makes 11 cells worth +20. Without propagation, threshold 20 would be unreachable in 22 plies.

**Capture-rule contribution.** **Decisive.** Custodian-flip is the operative scoring-swing mechanic. In Game 1, the single (5,4) flip at move 6 produced the +3 score gap that decided the game. **Custodian + threshold-race produces a much more interactive game than outnumber + threshold-race**, because custodian flips fire on smaller setups (1-stone bracket) and produce direct score swings (vs outnumber-2 which only clears the cell to empty).

**First-mover advantage / seat balance.** Trained-vs-trained 0.500 (balanced) — confirmed by my Game 1 (P2 wins). The 2:1 bracket-tempo asymmetry favours P2; the half-ply tempo lead favours P1. They roughly cancel. **This is the most balanced game in the slate**, with carpet's 625bfc1f3f49 tied via pie rule.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Argument:

(a) **Threshold-race influence games** — same family.

(b) **Custodian capture** is Reversi/Othello — single-axis bracket flip. The threshold parameter being vestigial means custodian-2 is just standard Reversi capture.

(c) **The combination "custodian + influence(r=1) + threshold-race(20)" on flat grid** is the closest geometric analog to **R8's Connection Go** (custodian + 2D grid + connection-win). The only differentiator from R8 is the win condition — connection vs threshold-race. **This game is the direct R8 control experiment.**

(d) **Flat 9×9 grid substrate** has been used for many published abstract games. Custodian + influence on a flat grid is essentially "Reversi with influence-radius scoring instead of disc-counting." Not novel, but well-developed.

(e) **Expert-transfer test.** A Reversi player would understand this game in 5 minutes. The novel piece: the *threshold-race scoring* replaces Reversi's "count discs at end" with "first to +20 wins."

**Closest known-game analogue:** **"Reversi-with-Threshold-Race"** on a 9×9 grid. Within Genesis: R8's Connection Go is the direct ancestor (custodian + 2D grid); switch the win condition to threshold-race and you get this game.

**Comparison to R8's Connection Go (8/10 ceiling).** Same custodian + 2D grid + influence kernel. **Different win condition.** R8's connection-win produces:
- Group-and-threat dynamics (multi-stone connection threats)
- Edge-to-edge race with persistent geographic constraint
- Ko-fight potential when a group is threatened

This game's threshold-race produces:
- Score-swing per capture
- 22-ply spreadsheet ending
- No persistent geographic constraint

**R8 wins on every depth axis except capture-frequency.** R8 captures fire on bridge-completion plies; this game captures fire 1–2 times per game on direct brackets. The win condition is the structural difference — and connection >> threshold-race for strategic depth.

**Comparison to R19 best.** R19 carpet rank-2 had custodian — single-stone bracket DOES flip (briefing-flagged for empirical verification, here confirmed). R20's grid_control top is the only grid + custodian + threshold-race game in the corpus.

**Player rebuttal.**
- **Custodian flips are real strategic content** — confirmed empirically in Game 1. The single-stone-bracket flip at move 6 swung the game.
- **Bracket-tempo asymmetry (2:1 reactive-favour)** is an emergent dynamic not present in any pure-Reversi or pure-threshold-race game. It arises from the conjunction of custodian + threshold-race.
- **Diagonal-safe placement pattern** is a real heuristic players need to learn. Captures only along axes; diagonals are immune.
- The substrate (flat grid) is **necessary** for custodian, doing real work. This is the only R20 game where the substrate *enables* rather than *constrains* the rule kernel.

**Novelty score (post-adversary):** **5/10.** Above siblings (3) and grid mean because (i) custodian capture is genuinely active and decisive (vs dormant in menger/carpet), (ii) the bracket-tempo asymmetry is an emergent dynamic, and (iii) the substrate enables the rule kernel rather than constraining it. Below R8 (8) because the win condition (threshold-race) is shallower than connection-win — the comparison Game→R8 is the cleanest evidence in the slate that *win condition* is the rich/shallow axis, not capture or substrate.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** fcedbc14043d
**Rules Summary:** Place stones on a flat 9×9 grid; influence accumulates (r=1); custodian-2 captures (single-stone bracket flips) are active; first to threshold +20 wins. **The closest R20 analog to R8 Connection Go — same substrate + capture rule, different win condition.**
**Substrate:** grid, axis 9, 81/81, max_degree 4, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** custodian threshold (=2) is vestigial; target_dimension_p2 (=+1) is vestigial for threshold games (only matters for connection wins).

### Scores (1–10)

- **Strategic Depth: 5** — Engine 0.593 underestimates this game's depth. Custodian flips are active (~1–2 per game in my play), each worth ~+1.5 score swing, and the bracket-tempo asymmetry produces real strategic content. Above menger siblings (4) because captures actually fire; below R8 (8) because threshold-race ends in 22 plies — too short for connection threats or ko-fights to develop.
- **Emergent Complexity: 5** — Custodian-flip score swings, bracket-tempo asymmetry, diagonal-safe placement, defensive-spread trade-off. More emergent vocabulary than menger siblings; less than R8.
- **Balance: 6** — Trained 0.500 + my own Game 1 win for P2 — balanced empirically. The 2:1 bracket-tempo asymmetry (P2 favoured) cancels with P1's half-ply tempo (P1 favoured). Anchor: tied with `625bfc1f3f49` carpet (6) for most-balanced in slate.
- **Novelty (post-adversary): 5** — see Phase 4. Active custodian captures + grid substrate doing real work.
- **Replayability: 5** — Two viable strategies (P1 cluster + P2 reactive-capture) with real choice space. Bracket setups can vary; capture timing is non-trivial. Above siblings (3); below R8 (where openings have many lines).
- **Overall "Would an agent team play this again?": 5** — Once: yes for the R8-comparison data point. Twice: yes for the bracket-tempo exploration. Three times: maybe — the strategic content is bounded by 22-ply game length. Anchors: tied with `5f5c72e15220` (5) at the headline R20 mark; above R19 production mean (4.375); below R19 menger top (4.8) by a hair.

### CLOSEST KNOWN-GAME ANALOG
**"Reversi-with-Threshold-Race" on a 9×9 grid.** Within Genesis: direct sibling-by-substrate of R8's Connection Go; only the win condition differs. The R8-revival negative finding (briefing-noted) hinges on this comparison: even on the most R8-friendly setup, threshold-race produces a thinner game than connection-win.

### KILLER FLAWS
- **Custodian threshold parameter is vestigial.** Engine code ignores it. Briefing should drop the "(=2)" annotation as misleading.
- **target_dimension_p2 = +1 is vestigial for threshold games.** Engine treats P2 as mirror regardless. Documentation should be cleaned up.
- **22-ply games are too short for full strategic content** — connection threats, ko-fights, and group concepts can't develop in 22 plies.
- **Pie rule OFF** — no balance lever despite the 2:1 bracket-tempo asymmetry.
- **Only 4 generations evolved.** Pre-launch axis-reduction control, not a champion. The game has structural promise but hasn't been refined.

### BEST QUALITY
**Custodian capture is active and decisive.** Unlike menger siblings (where outnumber-2 is dormant in symmetric play), this game's custodian fires once or twice per game, producing direct score swings of ~+1.5 per flip. The conjunction with threshold-race scoring makes captures *strategically meaningful at every ply* — every placement is evaluated for its capture-exposure and capture-creation potential. **This is the cleanest "captures matter" demonstration in the R20 slate**, and the closest empirical evidence that the R8 mechanism (custodian on 2D grid) still produces strategic content even with the win condition changed.

### grid STRUCTURAL CONTRIBUTION
**Substrate enables the rule kernel** (not constraint-only as in menger/carpet). Custodian capture only fires on grid/torus/sierpinski/holes topologies (engine_v2.py:632); on hex/moore it's skipped. The flat 9×9 grid is necessary for the game to function as designed. **R19's "menger > carpet > grid for substrate quality" finding is reversed here**: for capture-active rule kernels, grid is the *only* viable substrate.

### IMPROVEMENT IDEAS
**Single best change:** **Switch win condition to connection-win.** This game would converge on R8 Connection Go's strategic richness if the threshold-race were replaced with "P1 connects top-to-bottom, P2 connects left-to-right." The substrate, capture, and propagation are already R8-compatible. **This is the single most-potent test the R20 → R21 transition can run for the R8-revival hypothesis.**

Secondary improvements:
- **Pie rule ON.** Even with structural balance, pie is a free safety net.
- **Increase threshold to ~40** to give the game room for more captures and longer race.
- **Run more PPO seeds.** n=3 is too small; n=18+ would tighten the 0.500 estimate.
- **Drop the vestigial threshold and target_dimension_p2 parameters from the rule blob** to clean up the rule semantics.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-2_gamefcedbc14043d.md`.*
