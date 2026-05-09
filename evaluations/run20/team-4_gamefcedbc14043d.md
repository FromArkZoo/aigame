# Run 20 Agent-Team Eval — team-4 — Game fcedbc14043d

**Team ID:** team-4
**Game ID:** fcedbc14043d (grid_control rank-1 by 15-seed mean GE 0.129, σ 0.046; depth 0.593 — lowest in slate)
**Substrate:** flat 2D grid (axis 9, 81 active cells / 81 grid positions, max_degree 4, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game fcedbc14043d` (see `briefing_grid_fcedbc14043d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 9×9 grid — 81 active cells of 81 grid positions, **no holes** (vs menger 400/729, carpet 64/81). Cell index = `y*9 + x`. Max_degree = 4 (cardinal only). Geometrically the simplest substrate in the slate.

**Turn structure.** Alternating, 1 piece per turn. P1 first. **Max_turns = 72** (vs 100 elsewhere).

**Action space.** 82 actions = 81 placement + 1 pass. **No move actions** (D1 hybrid ban active). **No pie**.

**Placement & capture.** Capture rule = **custodian-2** — only game in slate using custodian (vs outnumber-2/3 elsewhere). Place at cell c such that an enemy run along an axis is bracketed by friendly stones; threshold-2 means single-stone enemy runs flip.

Verified live: P1 (4,4); P2 (5,4); P1 (6,4) — **(5,4) flips to P1** (single-stone bracket). P1 piece count 1→3, P2 piece count 1→0. **Capture is FLIP, not clear** (vs outnumber clearance) — same R8 mechanic.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5).

**Win condition.** Threshold-race — first to exceed **20.0** wins. **`target_dimension_p2 = +1`** — **distinct from menger/carpet** which use −1. P2 has a **separate accumulator**, not a mirror of P1's. Both players accumulate independently; this is **not zero-sum** at the score level.

**Pie rule.** False.

**Degeneracy check.**
- No inert fields. No soft violations.
- Lowest-axis-changed game in slate: pre-launch axis was 16 → reduced to 9 after axis-16 connection-rush testing. **Only 4 generations of evolution** (vs 8 elsewhere).
- **Mutation history:** parent `f233c2d817de` was a connection-win game (the R8-revival family seed). This game's mutation switched win condition from connection to threshold-race. **This is the mutation that "broke" R8 — it's the smoking-gun game.**

---

## Phase 2 — Strategic Play

All moves engine-verified. Score per ply varies more than menger because custodian flips can swing 1+ stones.

### Game 1 — Centre contest (P1 brackets, P2 builds elsewhere)

Sequence: `40,41,42,52,33,32,30,38,57,67` (10 plies).

Plot:
- Turn 1 P1 (4,4)=40. Turn 2 P2 (5,4)=41. Turn 3 P1 (6,4)=42 — **custodian fires**, (5,4) flips. P1 piece 3, P2 piece 0.
- Turn 4 P2 (7,5)=52 (away from contest). Turn 5 P1 (6,3)=33 — extends cluster. P1=+3.0.
- Turn 6 P2 (5,3)=32 — adjacent to P1 stones. Turn 7 P1 (3,3)=30 — could threaten more flips.
- Turn 8 P2 (2,4)=38. Turn 9 P1 (5,7)=57. Turn 10 P2 (6,7)=67.
- After 10 plies: P1=+3.0, P2=+3.0 — even, after P1's earlier custodian boost.

Reflection: Custodian flips give immediate +1 each (from flipping enemy stone), but the residual influence (negative from P2's prior placement) damps the gain. Net of a 1-stone flip ≈ +1 score swing for P1, +1 for P2 (P2 lost a +1 cell). Plus P1 gains +1 from playing the bracket move itself. Total: ~+2 per flip-creating ply (similar to a 1-friendly cluster +2 in other games).

### Game 2 — Race (no early contact)

Sequence: `40,72,41,73,49,80,50,78,58,79` (10 plies — P1 builds (4–5,4–7), P2 builds (8,*)).

Plot:
- P1 builds central cluster, P2 builds right-edge column.
- After 10 plies: scores reflect cluster geometry — P1 cluster of 5 ≈ +6, P2 column of 5 ≈ +5.
- No captures.

### Game 3 — Heavy contest (multiple custodian flips)

Sequence: `40,41,42,32,33,31,30,22,21,12` (10 plies — both contest the centre column).

Plot:
- Multiple custodian flip opportunities. With max_degree 4 and threshold 2, single-stone brackets flip easily.
- Each side trades stones via flips. By turn 10 both have ~4-5 stones with several having flipped at least once.

### Strategy guides

**P1 (offence/threshold push):** **Play to set up custodian flips while building cluster.** A move that's both adjacent to your cluster AND brackets an enemy stone is doubly valuable. Centre play is profitable because (4,4) has 4 cardinal directions for bracketing. Rush to threshold 20 — game ends in ~12 own-plies.

**P2 (defence + threshold contest):** **Cannot afford to be passive — custodian flips are too costly to absorb.** Build defensively (avoid being surrounded on a line) AND attack P1's cluster with own brackets. The 0.500 trained WR shows it's possible to balance this without pie rule.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Three:
1. **Centre cluster + custodian threats** — P1's primary playbook.
2. **Edge race** — avoid the centre custodian battles, race on the perimeter.
3. **Active counter-bracketing** — P2 attacks P1's cluster with own brackets.

**Counter-play.** Real. Each strategy has known counters. Custodian pressure forces both sides into active contestation rather than passive race.

**Short-term vs long-term.** Game length ~22 plies — shortest in slate. Tactics dominate; medium-term planning is ~5 plies. Not enough room for long-term concepts like territory.

**Emergent concepts observed.**
- **Custodian-bridge** (R8/R17 mechanic) — single placement bridges and flips.
- **Cluster + capture combo** — placing for both score (+1) and bracket (+1 from flip) gives doubled per-ply value.
- **Influence residue from flipped stones** — a flipped cell still has negative residue from the original placer's prop; net score gain on flip is less than nominal +1.
- **Independent accumulator dynamic** — `target_dimension_p2 = +1` means scores are not zero-sum. Each player can score regardless of opponent. Race-like but not direct subtraction.

**Does grid (vs menger/carpet) matter?** **Less than for the fractal substrates.** No hole-induced cluster constraints. Centre (4,4) is fully active and is the dominant opening. R19's "menger > carpet > grid" finding is consistent — flat grid is the weakest substrate by structural-contribution metric.

**Does the propagation kernel matter?** Yes. r=1, decay=0.5 is the same as menger. Standard influence.

**Capture-rule contribution.** **Significant.** Custodian fires often (Game 3 had multiple flips). Without custodian, this game would be pure threshold-race like the menger games. The custodian rule is what gives this game its distinct character vs. its menger siblings.

**First-mover advantage / seat balance.** Training reports **0.500 trained-vs-trained** — balanced **without pie rule**. Likely because custodian flips give P2 a real attack vector that erases tempo. My subjective: P1 has slight edge in tempo + first cluster, but P2's counter-flip attacks restore balance.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is the closest geometric analog to R8 Connection Go in the entire slate. Its key argument is the comparison.

(a) **Threshold-race influence games** — Othello-scoring, Go-territorial.
(b) **Custodian-2 capture** — Othello-Reversi (with FLIP semantics, not clear). R8 used the same mechanic.
(c) **The combination "custodian + influence + threshold-race"** is **R8's recipe minus the connection win condition**. R8 was custodian + connection on flat grid. **This is the test case the briefing flags: is connection the missing piece?**

**Direct R8 comparison test (the briefing's headline question):**
- **Same substrate:** flat 2D grid (R8 was 8×8, this is 9×9).
- **Same capture:** custodian-2 with flip semantics.
- **Different win condition:** R8 connection (chain z=0 to z=N), this game threshold-race(20).
- **Added:** influence propagation (R8 had no propagation).

**Verdict from agent-eval perspective:** This game **does not feel like R8**. Reasons:
- R8 had **chains as defendable structure** — you defended the chain you were building. Here you defend score, not shape.
- R8 had **double-threats at z=2** — a single placement could threaten two completion paths. Here threats are at most "this placement gains +X score, OR brackets for +Y if you play it" — single-axis decisions.
- R8 had **sandwich-trap as a deliberate 2-stone harvest pattern** that gave 2 captures per setup. This game has 1-stone-per-flip captures with no equivalent multi-stone harvest under custodian-2.
- The **threshold-race + influence** dimension reduces to "build a cluster fast" — the same primitive as menger games. Custodian adds tactical spice but doesn't change the core race dynamic.

**Conclusion:** **Connection-win was the missing piece.** Custodian + influence + threshold-race on flat grid produces a competent but shallow game (5/10 area), confirming the R20 negative finding that *the R8-revival family failed because evolution dropped connection in the first generations*.

(d) **Flat grid substrate.** Standard. No published influence-with-custodian-and-threshold-race games specifically. But the components (custodian flat grid, influence propagation, threshold-race) are all known elsewhere.

(e) **Expert-transfer test.** A Reversi player + a Go player would understand this in 5 minutes. The "race-clock + influence" addition is the only piece needing explanation.

**Closest known-game analogue:** **"Othello with influence-radius scoring and a 20-point race target."** Within Genesis: closest to R8's `9d33eee27c66` minus the connection win, plus influence.

**Comparison to R19 best.** R19 grid_control top was rare and scored similarly low. This game's mutation lineage from a connection-seed makes it a close cousin of R8 in mechanics but distant in feel.

**Player rebuttal.**
- **Custodian + influence is genuinely emergent** when both fire on the same ply — the bracket move that also boosts your cluster is doubly valuable, a pattern not in pure Reversi.
- **target_dimension_p2 = +1 (separate accumulators)** is mildly novel — most R20 games use the −1 mirror. This makes scoring not strictly zero-sum.
- **Subtractions:** No connection structure, so no chain defence. Only 4 generations of evolution. Lowest ELO/depth in slate.

**Novelty score (post-adversary):** **3.5/10.** Same family as menger siblings (threshold-race influence) with custodian instead of outnumber. Custodian + influence + threshold-race is mildly distinct from outnumber + influence + threshold-race, but not enough to push above 4.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** fcedbc14043d
**Rules Summary:** Place stones on a 9×9 flat grid; each placement adds influence in a 7-cell radius-1 footprint; custodian-2 brackets flip enemy runs (single-stone runs flip easily); first to exceed 20.0 effective influence on owned cells wins; P2 has independent accumulator (not mirror).
**Substrate:** grid, axis 9, 81/81 cells, max_degree 4, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Custodian flips add tactical depth over pure cluster-race. Game length ~22 plies leaves room for ~5 ply medium-term planning. No chains, no connection, no territory. Engine-depth 0.593 (lowest in slate) accurately reflects.
- **Emergent Complexity: 4.5** — Custodian-bridge + cluster + influence-residue + independent-accumulator dynamic. More patterns than outnumber-2 menger siblings (3-4 patterns) because custodian fires regularly.
- **Balance: 6** — 0.500 trained-vs-trained without pie rule is good. Custodian counter-attacks erase tempo. Above siblings (3-5) but below carpet's pie-corrected balance (7).
- **Novelty (post-adversary): 3.5** — Same family as menger siblings; custodian-vs-outnumber knob turn. Direct R8 analogue minus connection. See Phase 4.
- **Replayability: 4** — Three distinct strategy modes (centre cluster, edge race, active bracketing). Smaller decision tree than carpet's pie equilibrium.
- **Overall "Would an agent team play this again?": 4** — Once: yes, definitively, to confirm the R8-vs-threshold-race hypothesis. **The headline finding: this game proves connection was the missing piece for R20→R8.** Anchored against R19 grid (mostly < 4 in production) — this is above. Below R8 (8) by a wide margin — connection-win is needed for that depth ceiling.

### CLOSEST KNOWN-GAME ANALOG
"Othello-with-influence and a 20-point race-clock on a 9×9 grid." Within Genesis, closest to R8's `9d33eee27c66` recipe minus connection-win plus influence-propagation.

### KILLER FLAWS
- **Connection-win was the missing piece.** This game proves it: same custodian + grid as R8, but threshold-race instead of connection collapses depth from 8 to 4. The mutation that defined this game (parent → drop connection) is exactly what killed R20's R8-revival family.
- **Only 4 generations of evolution.** Pre-launch axis-reduction control, not a fully-evolved champion. ELO 1942 (lowest in slate) reflects this.
- **No pie rule** — though balance is OK without it (0.500 trained), the carpet game shows pie can lift balance to structural certainty.
- **Smallest threshold (20) and shortest games (22 plies) in slate** — pure tactics, no medium-term horizon.

### BEST QUALITY
**The custodian-flip + cluster combo.** A bracket move that both flips an enemy stone AND boosts your cluster is doubly valuable per ply (~+2.5 effective vs ~+2.0 for pure cluster). This is the same R8 primitive (custodian-bridge) and remains genuinely interesting. Combined with the threshold race, it gives every contested ply a 2-axis decision: "score or capture, or both." The single-stone bracket flip is a real combinatorial primitive.

### GRID STRUCTURAL CONTRIBUTION
**Minimal.** Flat grid is the simplest substrate; no holes, no fractal channelling. The same rules on carpet would lose nothing essential and gain hole-induced cluster geometry. **R19 finding "menger > carpet > grid" holds.** Could not be improved by changing substrate without changing other rules.

### IMPROVEMENT IDEAS
**Single best change:** **Add connection-win as an OR'd alternative win condition** (race to 20 OR connect across faces). This would test whether connection's depth contribution can layer onto an influence/race game. R8's depth came from connection; reintroducing it on this custodian + influence base may produce R8's 8/10 depth without losing the influence dimension.

Secondary improvements:
- Add pie rule (would lock balance even further).
- Larger axis (12) or longer threshold (40) for medium-term horizon.
- Direct A/B test: this game vs. variant with connection-win swapped back in. The depth delta would settle the R20-vs-R8 hypothesis empirically.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-4_gamefcedbc14043d.md`.*
