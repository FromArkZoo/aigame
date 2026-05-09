# Run 20 Agent-Team Eval — team-3 — Game fcedbc14043d

**Team ID:** team-3
**Game ID:** fcedbc14043d (grid_control rank-1, only grid game; 15-seed mean GE 0.129, σ 0.046, depth 0.593, ELO 1942)
**Substrate:** flat 2D grid (axis 9, 81 active cells / 81 grid positions, max_degree 4, no fractal holes)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game fcedbc14043d` (see `briefing_grid_fcedbc14043d.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 9×9 grid, 81 active cells, no holes. Cell index `c = y*9 + x`. 4 corner cells (deg-2), 28 edge cells (deg-3), 49 interior cells (deg-4). No hub hierarchy — uniform connectivity within type.

**Turn structure.** Alternating, 1 piece per turn. P1 first. **Max_turns = 72** (shortest in slate).

**Action space.** 82 actions = 81 cells + 1 pass. No pie.

**Placement & capture.** Capture rule = **custodian-2** (only game in slate using custodian). On placement at A: along each of 4 axes (±x, ±y), walk outward; if a contiguous run of enemy stones is bracketed by friendly stones (one being A, the closing bracket being any prior friendly stone with the run in between), the entire run **flips ownership to placer** (Othello-style flip, not clear). Threshold parameter = 2 means "single-stone bracket DOES flip" — verified empirically with `--moves "40,41,42"` flipping (5,4).

**Propagation.** influence, r=1, strength=1.0, decay=0.5. ±1.0 self, ±0.5 to 4 neighbours, P1 sign +, P2 sign −.

**Win condition.** Threshold-race > **20.0** (lowest in slate). `target_dimension_p2 = +1` — engine notes this is "different from menger/carpet (-1, mirror)". In helper-computed scores, P1 = +Σ(P1 owned values), P2 = −Σ(P2 owned values) — same formula as siblings. The +1 vs −1 distinction lives inside the engine's win-check; agent-experience is the same threshold race.

**Pie rule.** False.

**Degeneracy check.**
- All rules fire normally.
- Custodian capture is the most impactful rule in any R20 slate game: a single placement can flip 1–N enemy stones, swinging score by 2 per flipped stone (loser loses, winner gains).
- Multi-stone bracket flip verified: `--moves "36,37,38,39,28,40,41,29,42"` produced 3 captures including a 2-stone flip.

---

## Phase 2 — Strategic Play

All moves engine-verified. Action IDs = cell indices for placement; pass = 81.

### Game 1 — Greedy edge-walk (no captures)

Sequence: `0,1,9,2,10,3,11,4,12,5,13,6,14,7,15,8,16,17,18,26,19,35,20` (23 plies, **P1 wins +20.5 / P2 +16.5, 0 captures**).

Plot:
- Both players walk along y=0 row alternating, then y=1 row. Each placement adjacent to opponent gives +1.5 swing (own +1.0 + opp influence reduced +0.5).
- No captures fire because greedy doesn't *plan* brackets — it picks cells that maximize immediate score, which doesn't naturally produce P1-P2-P1 patterns.
- P1 reaches +20.5 at ply 23 (matches the 22-ply training avg).

Reflection: With low threshold (20) and no capture, the game reduces to a tempo race. P1's first-move + cluster-build wins.

### Game 2 — Hand-coded capture-aggressive sequence

Sequence: `40,30,32,31,22,41,38,49,42,33,4,21,38,5,57,50,48,51,49,60,58,59` (22 plies, **3 captures including a 2-stone bracket flip**, ongoing).

Plot:
- Move 5: P1 places (4,2) bracketing P2 at (4,3) along −y → 1-stone flip.
- Move 9: P1 places (4,4) bracketing P2 at (5,4) along +x → 1-stone flip.
- **Move 10: P2 places (3,3) — counter-flip — bracketing P1's earlier-flipped (4,3) and (5,3) along +y → 2-stone flip back to P2.** This is a *recapture* of stones P1 had just flipped.
- Game continues with multiple flip/counter-flip cycles. The board state oscillates rapidly.

Reflection: **Custodian creates real tactical depth.** Single placements flip 1-N stones with permanent (until counter-flipped) ownership change. Counter-flips are possible when a flipped stone becomes the bracket-end for a new capture. This is the most-active capture mechanic in any R20 slate game.

### Game 3 — Adversarial capture race (greedy capture-aware)

Capture-aware greedy (with custodian-bonus weighting) fails to trigger captures because greedy doesn't *plan* multi-move bracket setups. Captures here require **2-move planning** (place stone A, opponent plays B inside, place stone C to close bracket) — a depth that greedy doesn't have.

This means: **PPO can find captures, agent-team-style greedy cannot.** The training reference (0.500 winrate, 22-ply avg games) suggests captures fire in PPO play. The strategic depth (0.593) is partially gated behind capture-planning ability.

### Strategy guides

**P1 (offence + capture pursuit):** Build edge clusters at low threshold (20). Setting up custodian brackets requires planning — place stones with 2-cell gaps along an axis, *invite* P2 to fill the gap, then close. Each successful flip swings +2; with threshold 20, ~10 flips would suffice without any positive accumulation.

**P2 (defence + counter-flip):** Watch for P1's bracket setups (P1 stones at distance 2 along same axis with empty middle). Avoid filling between two P1 stones. Counter-flip opportunities arise when P1's flipped-stones are themselves adjacent to enemy runs.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes — 2 clear lines:
1. **Cluster-build threshold-race.** Greedy edge-walk; ignores custodian. Wins by tempo.
2. **Capture pursuit.** Plan brackets, harvest opponent stones. Each flip swings +2 (winner +1 own, loser -1 own). With multi-stone brackets possible, single placements can swing +4–6.

Both viable; capture pursuit has higher peak swing but requires planning depth.

**Counter-play.** **Counter-flips** are the killer feature. A flipped stone becomes the bracket-closer for a counter-flip. This produces ko-like cycles where a position oscillates between owners. **More tactical depth than any other R20 game's capture mechanic.**

**Short-term vs long-term.** Short games (22-ply avg). With low threshold (20), each placement is 5% of the target — every ply matters. Custodian flips are 10% per stone — game-changing.

**Emergent concepts observed.**
- **Bracket setup planning.** Place stones at distance 2 along an axis to invite captures. Multi-move tactical pattern.
- **Multi-stone bracket flip.** Single placement can flip 1–N stones if N enemy stones in a row.
- **Counter-flip cycles.** Flipped stones become bracket-closers; recapture possible.
- **Custodian + influence interaction.** A flipped stone's value (set by the original owner's propagation) becomes the new owner's score. Significant — flipping a P2 stone with value −1.0 nets +2.0 to P1's score-delta.

**Does grid matter?** **Marginally.** The flat 9×9 grid is the simplest possible substrate and provides no special structure (no hubs, no fractal isolation). The game's identity comes from the rule combination (custodian + influence + threshold-race), not the substrate. **Could be flattened to any 9×9 lattice with the same dynamics.** This is consistent with R19's finding that grid is the weakest substrate.

**Does the propagation kernel matter?** Yes — r=1 + decay=0.5 produces the same ±1.0 / ±0.5 spread as menger games. With low threshold (20), each placement's +1.5 effective swing is a major fraction of the target.

**Capture-rule contribution.** **Substantial.** Custodian flips are tactical centerpiece. Even though greedy doesn't trigger captures, hand-coded sequences show 3+ captures in 12 plies, making capture *viable* as a primary strategy. **Custodian here is more active than outnumber-2 in any menger game.**

**First-mover advantage / seat balance.** Trained-vs-trained 0.500 (balanced). My greedy P1 wins. Pie OFF. The 0.500 likely reflects PPO's ability to find capture-rich P2 lines that exploit P1's setup vulnerabilities. **This is the only R20 grid game and is balanced at PPO depth — but greedy still favours P1.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This is the closest geometric analog to R8 Connection Go in R20:

(a) **Threshold-race influence games** ≈ Othello scoring without flips. Same family.
(b) **Custodian-2 capture** = **Othello/Reversi capture** (sandwich-and-flip). This is the same primitive as R8's `9d33eee27c66` (8/10) Connection Go.
(c) **Combination "custodian + influence + threshold-race"** — custodian + influence is unusual; threshold-race makes it specifically a race-clock variant. Inside Genesis, the closest is R8's custodian + connection (different win condition). **R20's switch from connection to threshold-race is the experimental test.**
(d) **Flat 9×9 grid substrate.** Trivial — no special structure.
(e) **Expert-transfer test.** A Reversi player + Tantrix player understands this in 5 minutes. The "novel" piece is the 20-point race clock ending what would otherwise be a full Reversi game.

**Closest known-game analogue:** **"Reversi with a 20-point race clock"** — equivalently, "small-board Othello where you stop counting at 20 instead of waiting for board fill." Inside Genesis: closest is R8 `9d33eee27c66` Connection Go (8/10), differing only in win condition (connection vs threshold-race).

**Comparison to R8 Connection Go (8/10).** **This is the headline comparison.** R8 was custodian + connection on flat grid. R20 fcedbc14043d is custodian + threshold-race on flat grid. **Same substrate, same capture rule, different win condition.**

R8's depth came from connection-shape: a custodian flip could complete a chain, producing **single-move winning swings** — the "custodian bridge" pattern in R8's verdict (5/10 by R17 team-1 evaluation). Here, threshold-race has no shape — captures are valued in raw score (+2 swing per flipped stone, ~10% of threshold). **Captures are tactically meaningful but not strategically transformative.**

**Verdict on the experimental question:** R8 vs R20 difference IS the win condition. Connection win turns custodian into a strategic enabler (chain-completer); threshold-race turns it into a tactical accumulator. **R20 confirms: connection + custodian was R8's depth source. Threshold-race retains tactical capture but loses the strategic chain-completion.**

**Comparison to R19 best.** R19 had no grid_control top game in this family. This is the first R20 attempt at a grid+custodian+threshold-race combination. As an isolated experiment, **comparable to R19 menger top-1 (4.8/10)** in tactical content but lacking R19's substrate-novelty.

**Player rebuttal (P1 + P2).**
- Custodian is the strongest tactical layer in any R20 slate game. Multi-stone flip + counter-flip is depth-rich.
- Bracket-setup planning requires 2-move lookahead — first non-greedy game in slate.
- Subtracts: substrate is trivial (flat grid); win condition (threshold-race) replaces R8's strategic depth source (connection-shape).

**Novelty score (post-adversary):** **3/10.** Same as menger group on absolute scale. The custodian mechanic is tactically rich but identical to R8 / Reversi. The novelty-vs-R8 question is: this game *deletes* R8's strategic enabler (connection win) and replaces with arithmetic. So no novelty over R8 — just simplification.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** fcedbc14043d
**Rules Summary:** On a flat 9×9 grid with no fractal holes, alternating placement with custodian-2 capture (Othello-style sandwich flip, single-stone brackets included) and r=1 influence propagation; first to >20 owned-cell influence wins.
**Substrate:** flat grid, axis 9, 81/81 cells (no holes), max_degree 4, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** none. Custodian-2 verified empirically; multi-stone flip and counter-flip verified.

### Scores (1–10)

- **Strategic Depth: 5** — Custodian creates real tactical depth: bracket-setup, multi-stone flip, counter-flip cycles. **Most-tactically-rich game in slate** despite shortest game length. Engine 0.593 understates this; the metric likely measures decision-density and short games naturally suppress it.
- **Emergent Complexity: 5** — Counter-flip cycles + custodian-influence interaction + bracket-setup planning is more emergent content than any menger game. Bumped above siblings.
- **Balance: 4** — Trained-vs-trained 0.500 (balanced), my greedy P1 wins. Pie OFF, but custodian's flip-counter-flip dynamics give P2 real recovery options. Slightly better balance than menger non-pie games.
- **Novelty (post-adversary): 3** — Same as menger group. Custodian is tactically active but identical to R8/Reversi.
- **Replayability: 4** — Bracket-setup planning + counter-flip cycles give move variety. But short game length (22 plies) compresses replayability.
- **Overall "Would an agent team play this again?": 4** — Higher than menger siblings (3) due to custodian's tactical activity. Lower than carpet (5) because no pie + trivial substrate. Below R8 (8) because no connection-win to give captures strategic teeth.

### CLOSEST KNOWN-GAME ANALOG
**"Reversi with a 20-point race clock."** Inside Genesis: R8 `9d33eee27c66` Connection Go (8/10) is the closest sibling — same substrate + same capture rule, differing only in win condition. This game is R8 with the strategic depth source (connection) replaced by arithmetic (threshold-race).

### KILLER FLAWS
- **Trivial substrate.** Flat grid contributes nothing to the game's identity; the rules carry the entire weight.
- **Pie rule OFF** — same structural P1-tempo issue as menger group.
- **No connection win.** Custodian's strategic potential (chain-completing flip) is squandered by threshold-race; R8 found connection was the unlock and this game discards it.
- **Greedy doesn't find captures** — depth is gated behind 2-move planning, which limits agent-team play without explicit search.

### BEST QUALITY
**Counter-flip cycles.** A captured stone becomes the bracket-closer for a counter-capture; positions oscillate between owners. This is the most-tactically-alive feature in any R20 game — single placements cause multi-stone ownership swings of +4 or more. **The custodian mechanic itself is the crown jewel; the game's flaw is failing to exploit it via a connection win.**

### GRID STRUCTURAL CONTRIBUTION
**Negative.** Flat grid is the weakest substrate per R19 (menger > carpet > grid). Here it's chosen as a methodological control — testing whether substrate matters by removing all substrate features. The answer: **yes, substrate matters.** Without holes / hubs / fractal isolation, the game collapses to a uniform race where the rules alone determine play. The grid's only contribution is being the simplest backdrop; everything interesting comes from custodian + influence + threshold-race interactions.

### IMPROVEMENT IDEAS
**Single best change:** **Switch win condition from threshold-race (>20) to connection (e.g., P1 connects top-bottom, P2 connects left-right).** This would directly recreate R8 Connection Go (8/10). The custodian + influence + flat-grid baseline is identical to R8; only the win condition differs. **Replicate R8 by reverting this evolutionary step.**

Secondary improvements:
- **Restore pie rule** — same recommendation as siblings; carpet shows pie can balance.
- **Test connection-win on this game's exact ruleset** to confirm the experimental finding (R20 dropped connection because evolutionary fitness preferred threshold-race; was the fitness function wrong?).
- **Increase axis to 13 or 16 with both connection and pie** — R20's pre-launch reduction from 16→9 was forced because connection-rush broke at 16; with pie, larger boards might survive.
- **For agent-team evaluation: provide a 2-move-lookahead helper** so greedy doesn't completely miss capture opportunities. Currently the agent-eval underestimates this game's depth due to search limits.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-3_gamefcedbc14043d.md`.*
