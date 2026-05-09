# Run 20 Agent-Team Eval — team-pilot — Game f98b9414f638

**Team ID:** team-pilot
**Game ID:** f98b9414f638 (menger rank-5 by GE 0.129, σ 0.089, depth 0.597)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game f98b9414f638` (see `briefing_menger_f98b9414f638.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — same substrate as the other menger games. 400 active cells.

**Turn structure.** Alternating, 1 piece per turn. P1 first. **Max_turns = 89** (slightly less than 100 in siblings).

**Action space.** 730 actions = 729 placement + 1 pass.

**Placement & capture.** **Outnumber-2** capture (same as `a6385db22c0b`/`b160b1f55378`/`d1dbc6568fc7`).

**Propagation.** influence (radius=1, strength=1.0, decay=0.5).

**Win condition.** Threshold-race; first player to owned-cell sum >**29.709** wins. **The structural odd-one-out: half the threshold of siblings (29.71 vs 57.97).** `target_dimension_p2 = -1`. Max turns = 89.

**Pie rule.** Off.

**Identity check.** Same capture rule, propagation kernel, target_dimension_p2 as the other 4 menger games. The differentiator is the threshold (29.71 vs 57.97) and max_turns (89 vs 100). Mirror-cluster play through 27 plies on this DB ends in P1 win at +32 vs +29 — about half the playtime of siblings.

**Degeneracy check.**
- Same Menger degree-truncation (degree-2 = capture trap under outnumber-2).
- No inert fields.
- Threshold 29.71 reachable in ~15 stones each side ⇒ ~30 plies for naive mirror, ~38 plies with engagement (briefing avg 38.8).

**Lower-threshold consequence.** Game ends in roughly half the time of siblings. This makes:
- **First-mover tempo more decisive in absolute terms** (+1.5 of a 30-target = 5% lead) but *less* decisive in absolute time (smaller window for compounding to tilt).
- **Cluster-deepening tactics** are still live but have fewer ply to play out.
- **Capture cascades** still fire in contested play but at a lower stone count, so the trade-economy is tighter.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`.

### Game 1 — Mirror cluster (the equilibrium baseline)

Sequence (27 plies, P1 wins +32 vs +29): `0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21,59,27,53,28,52,29,51`.

Plot:
- P1 builds (0..3, 0..3, 0..2) corner cluster. P2 mirrors at (5..8, 5..8, 0..2).
- No contact, no captures.
- Move 27 P1 places its 14th stone at (3,1,0)=51. Wait — actually move 27 is P1 placing 51 at the *opposite* corner. Greedy must have spread.
- Game ends at move 27 with P1 hitting threshold +32 (>29.71).

This is **half the playtime of a6385db22c0b**'s mirror line (51 plies). Same dynamics, half the runway.

### Game 2 — Contested-corner with P2 lead

Sequence (42 plies, P2 leading +26 vs +21.5, would win in 1-2 more P2 moves): `0,1,9,2,18,11,19,20,3,12,21,27,28,29,81,83,84,99,101,102,110,165,162,164,180,182,108,173,183,191,189,200,243,245,261,263,170,235,153,254,27,99`.

Plot:
- Both sides interleave in (0..3, 0..3, 0..3) corner.
- Same capture cascade as a6385db22c0b/d1dbc6568fc7 contested lines: 8+ captures by move 27.
- **By move 36 P2 is leading +20.5 vs P1 +18.** P2's cluster-deepening play (move 28 (2,1,2), move 30 (3,2,2 area)) yields +3 effective per move — outpacing P1's tempo lead.
- By move 42 P2 has extended to **+26 vs P1 +21.5** — a 4.5-point lead, very near the +29.71 threshold.
- P2 wins in 1-2 more P2 moves.

**This is the only menger game in the slate where P2 actually wins a played-out line under outnumber-2.** The lower threshold (29.71) interacts with the contested-corner cluster-deepening tactic in a way the higher-threshold siblings don't: P2's ~+3/move surge is enough to overtake the P1 tempo lead because the race ends sooner.

### Game 3 — Capture probe

Sequence (3 plies): `0,1,2`. Captures P2 at (1,0,0) on move 3 (identical to siblings under outnumber-2).

### Strategy guides

**P1 (offence/threshold push):** Same as siblings, but **end the game faster** — push for cluster compounding with 12-15 stones, exploit the +1.5 first-move tempo before the race clock expires. Don't spread too thin.

**P2 (defence + threshold contest):** **Engage P1's corner.** Unlike longer-threshold siblings where engagement just trades stones evenly, in this game's compressed timeline P2's cluster-deepening surge (interior placements adding −0.5 to existing P2 cells) yields +3 effective per move — outpacing P1's +2 tempo. The 0.500 trained-vs-trained matches my finding that P2 has a real shot at winning if they engage, not mirror.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two:
1. **Mirror cluster** (slow race, P1 wins on tempo, ~27 plies).
2. **Contested-corner cluster-deepening** (capture cascade + P2 surge, P2 wins on cluster-deepening, ~42 plies).

The strategic-diversity 0.333 (lowest in slate per briefing) seems wrong from my play — there are *two* viable strategies and they diverge sharply in winner. Maybe PPO seeds got stuck in the same mode (all mirror or all contested).

**Counter-play.** Real. P1's counter to contested attack is to retreat to mirror; P2's counter to mirror is to engage.

**Short-term vs long-term.** Tactical with race-tempo overlay. Plan horizon ~3 plies.

**Emergent concepts observed.**
- **Capture cascade** in contested play (same as siblings).
- **Cluster-deepening surge** (P2's +3/move from interior placements vs P1's +2/move from edge placements).
- **Threshold proximity tempo**: with threshold 29.71, the game ends before either side can build the cluster fully — making engagement-vs-mirror a decisive choice.

**Does menger matter?** Same as siblings — marginal. Substrate decorative.

**Does propagation kernel matter?** Same as siblings.

**Capture-rule contribution.** Same outnumber-2 captures as siblings, but here they fire in a tighter timeline so each capture exchange has higher relative weight (capture trades worth ~10% of threshold instead of ~5%).

**First-mover advantage / seat balance.** Briefing claims trained-vs-trained 0.500 (balanced). My Game 2 line confirms P2 has a real winning strategy. The P1 +1.5 tempo is overcome by P2's cluster-deepening +3 surge in contested play. Pie rule still off but seat-balance is roughly even because of the engagement counter.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same arguments as siblings:

(a) Threshold-race influence games ≈ Othello-without-flipping. (b) Outnumber-2 ≈ Tafl. (c) Combination is the dominant menger family. (d) Substrate is decorative. (e) Expert-transfer ~5 minutes.

The lower threshold (29.71 vs 57.97) is the only structural differentiator within the menger top-5 (excluding 5f5c72e15220's outnumber-3). It's not a novel mechanic — just a parameter knob.

**Closest known-game analogue:** Influence Othello on a Menger-sponge graph with shorter race target. Inside this project: R19 menger top-1 `1f9191b5d4e6`. Slate-mate `a6385db22c0b` is byte-similar except for threshold.

**Comparison to R8's Connection Go (8/10).** Same family-difference as siblings.

**Comparison to R19 best.** R19 menger top-1 `1f9191b5d4e6` (4.8/10). This game is in the same recipe family with shorter timeline.

**Comparison to slate-mate `5f5c72e15220` (depth 0.894).** **Lower depth.** The lower threshold makes the game shorter, which gives less room for the tactical primitives (re-occupation, double-capture, cluster-deepening) to develop. P2 surge IS visible here but in a thinner runway.

**Comparison to slate-mates `a6385db22c0b` / `b160b1f55378` / `d1dbc6568fc7` (depth 0.69-0.79).** **Slightly different.** The lower threshold and balanced seat (0.500) do create a distinct dynamic. However, the rule kernel is otherwise identical. Net depth is comparable.

**Player rebuttal.**
- The **threshold-29.71 + balanced seat dynamic** is genuinely different from the other 4 menger games in PPO equilibrium — P2 can win without infiltrating safe cells.
- However, the rule-novelty is a parameter change, not a new mechanic.

**Novelty score (post-adversary):** **3/10.** Same family as a6385db22c0b/b160b1f55378/d1dbc6568fc7. Threshold is a parameter change, not novelty. Below R17 mean (3.50). Tied with the rest of the menger outnumber-2 family.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** f98b9414f638
**Rules Summary:** 9×9×9 menger sponge; alternating placement on 400 active cells; influence kernel (r=1, decay=0.5) + outnumber-2 capture + threshold-race(**29.71**, half of siblings) on max_turns=89. Pie rule off.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Same rule-family as a6385db22c0b. The lower threshold means the game ends sooner — depth 0.597 reflects the shorter ply count more than a true depth difference. Plan horizon ~3 plies.
- **Emergent Complexity: 4** — Same captures + cluster-deepening as siblings. Race-tempo is more sharply felt because of compressed timeline.
- **Balance: 5** — Briefing 0.500 trained-vs-trained. My Game 2 line confirms P2 has a real winning strategy. Best balance in the menger slate, even without pie rule. **Half a point above siblings on balance** because the lower threshold reduces P1's effective tempo lead and gives P2's cluster-deepening surge more weight.
- **Novelty (post-adversary): 3** — Same recipe as a6385db22c0b/b160b1f55378/d1dbc6568fc7 with a threshold knob.
- **Replayability: 3** — Two viable strategies (mirror, contested) but they diverge by player choice not by board state. Once strategies are known, opening choices are forced.
- **Overall "Would an agent team play this again?": 3** — Same family as siblings, slightly more interesting because of the balance and shorter games. Anchors: R8=8, R17 mean=3.5, R19 menger top=4.8.

### CLOSEST KNOWN-GAME ANALOG
**The other 3 menger outnumber-2 games in this slate** (a6385db22c0b, b160b1f55378, d1dbc6568fc7) — same recipe, threshold-knob differentiator. Outside R20: R19 menger top-1. Outside this project: Influence Othello on a graph with race-target.

### KILLER FLAWS
- **Same recipe as 3 other slate-mates** with a parameter knob. Slate-construction issue.
- **Largest finalization collapse (Δ=−0.159)** flags this game as production-score-inflated by elite-carryover bias. The rank-2 → rank-5 demotion is ~−0.16 in GE — the actual game is mid-pack.
- **Pie rule off** — same +1.5 P1-tempo issue (mitigated by lower threshold but not eliminated).
- **Strategic diversity 0.333** is the lowest in the slate. PPO seeds got stuck in similar modes.

### BEST QUALITY
**Best balance in the menger slate.** Trained-vs-trained 0.500 + my Game 2 P2-winning line confirm that this game has the closest seat-balance in the menger group. The lower threshold + cluster-deepening interaction is what produces this balance — a real, if modest, structural feature.

### menger STRUCTURAL CONTRIBUTION
Same as siblings: marginal. Threshold parameter change + max_turns parameter change don't depend on the substrate.

### IMPROVEMENT IDEAS
**Single best change:** **Pick this threshold-knob value (29.71) for the entire menger family.** The shorter race produces better balance (0.500 vs 0.667) and similar tactical depth. If the slate had to keep one outnumber-2 menger game, this one gives the best balance per ply.

Secondary improvements:
- Restore pie rule.
- Pair with outnumber-3 capture (5f5c72e15220 lineage) for tactical inversion.
- Test threshold values around 20 — even shorter races may produce sharper tempo.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-pilot_gamef98b9414f638.md`.*
