# Run 19 Evaluation — team-1 — Game 98739cb0838a

**Team ID:** team-1
**Game ID:** `98739cb0838a` (Menger rank-2, GE 0.3213, ELO 2402.6)
**Substrate:** Menger sponge (axis 9, 400/729 active, max_degree 6 nominal)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 98739cb0838a` (briefing: `briefing_menger_rank2.md`).

---

## Phase 1 — Rule Comprehension

**Board / turn structure / actions.** Same as menger rank-1: 9³ menger sponge, 400 active cells, place-only (D1 hybrid ban active), alternating, P1 first. Max 100 turns (vs 89 in rank-1).

**Capture (outnumber, threshold 2).** Identical mechanic to rank-1.

**Propagation (influence, r=2, s=0.9895, d=0.3037).** Two key differences from rank-1:
- **r=2 not r=1.** Distance-2 active cells now receive influence (≈ ±0.0903 = 0.9895 × 0.3037²).
- **Decay 0.30 not 0.50.** Distance-1 reinforcement is +0.30 (vs +0.50 in rank-1) — steeper.

Effective reach is wider but each shell is thinner. Empirical check on the canonical 4-stone "plus" at corner: P1 = +6.31 (vs rank-1's +7.0). **Pilot reported +5.07 for the same sequence — that's wrong; the helper output here is +6.309 unambiguously.** Per-stone reinforcement at adjacency: +1.29 dist-1 ledger contribution, +0.09 dist-2 ledger contribution. The dist-2 reach buys back about 60% of what the steeper decay loses.

**Win (threshold-race > 38.959).** **+31% above rank-1's 29.71.** Combined with lower per-stone reinforcement, requires noticeably more stones to win. Trained-vs-trained avg game length 54.2 moves vs rank-1's 38.8 confirms the longer arc.

**Degeneracy check.**
- No soft violations.
- The rule blob has stayed unchanged through 8 generations of evolution (direct seed). This is either a stable local optimum or a basin the engine couldn't escape.
- Same hole pattern as rank-1: most active cells have 3-4 neighbours, 6-neighbour cells are rare and only exist at sub-cube corners.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror tempo baseline (long horizon)

Sequence: `0,728,1,727,9,719,81,647,2,726,18,710,162,566,3,725,4,724,11,717,12,716,19,709,27,701,99,629,83,645` (29 plies, mirror through 14-each + P1 ahead by 1).

Plot:
- P1 builds a 15-stone anchored fan at (0,0,0): same shape as rank-1's Game 1.
- P2 mirrors at (8,8,8) corner.
- At ply 8 (4 stones each, the canonical plus): both at +6.31. Per-stone at this stage: +1.58.
- At ply 29 (P1=15, P2=14): both at +27.87. **Per-stone average +1.86** as fan grows and dist-2 cross-contributions accumulate.
- Linear extrapolation: P1 needs ~21 stones to cross threshold 38.96 → P1 wins around ply 41-43.
- **Mirror = P1 wins by tempo, exactly as rank-1, just on a longer arc.**

Reflection (P1): The longer horizon doesn't change the structural P1 win — it just means P2 has more plies to find a non-mirror line before tempo catches up. The +1.86/stone rate is slightly below rank-1's +2.0/stone (lower decay), but the fan still scales linearly with stones placed.

### Game 2 — P2 corner sandwich

Sequence: `0,1,9,81` (4 plies).

Plot:
- P1 (0,0,0). P2 (1,0,0). P1 (0,1,0). **P2 (0,0,1) → captures (0,0,0).**
- After ply 4: P1 = 1 stone (0,1,0), score +1.107. P2 = 2 stones (1,0,0)+(0,0,1), score +1.378.
- **P2 ahead on score by +0.27** (whereas in rank-1 the same sequence ended with P1 and P2 tied at +1.0). Why: r=2 means cross-cluster dist-2 contributions matter — (1,0,0) and (0,0,1) are at dist 2 (path through captured (0,0,0)), so they reinforce each other slightly (≈ +0.18 paired contribution vs 0 in rank-1's r=1). The longer reach gives clustered captors a small advantage.

Reflection (P2): **Sandwich is slightly more profitable for P2 in rank-2 than in rank-1** because the wider influence kernel rewards even non-adjacent attackers. This is a real difference between the two games — same family, different parameters, slightly different attacker-economy.

### Game 3 — Long-horizon novelty adversary

Sequence: I ran the mirror through ply 29 (Game 1 above). The novelty-adversary play here is to **stretch the game** rather than test sandwich primitives:

Hypothesis tested: **does the long-horizon game open new strategies absent from rank-1?**

Findings (from extended-play observation + rule reading, not all engine-verified):
1. **Cluster preservation matters more than cluster expansion.** A 20-stone fan is +37 (close to threshold). Losing 2 stones to sandwich = −4 score (each captured stone removes its current and dist-1 contributions plus the dist-2 cross-terms). Rebuilding at +1.86/stone = 2-3 plies. Trade ratio vs rank-1: similar, just on a longer board.
2. **Late-game opportunistic sandwich works**. Once P1 has ~15 stones, ANY interior P1 stone is sandwich-vulnerable to a 2-move P2 investment. The extra plies past ~20-each are a "raid window" P2 can use without tempo cost.
3. **Re-occupy mechanic from rank-1 generalizes**. After P2 captures (0,0,0), P1 can re-occupy and the corner is permanently safe (same logic — P2 can't reach 2 P1-friendlies without placing on already-P2 cells). On rank-2 this matters MORE because each ledger-debt contribution at (0,0,0) is worth +0.99 + dist-1 + dist-2 = roughly +1.5 over a longer game's accumulation.

These plus the engine-verified moves above give me three viable strategies with the same arms-race shape as rank-1 (mirror → sandwich → re-occupy) but on a stretched timeline.

### Strategy guides

**P1 (offence/threshold push):** Same as rank-1 — anchor a corner, fan in 3 axes. Per-stone is +1.86 instead of +2.0 (rank-1), so you need ~21 stones instead of ~15 to cross threshold. **The longer game gives P2 more sandwich opportunities — defend cluster integrity by preferring fan-cells with 1-2 active neighbours (sandwich-immune) over interior multi-neighbour cells.** Counter-intuitive: low-degree cells are tactically safer.

**P2 (defence + offence):** Mirror loses to tempo (~ply 42-43 vs ply 29 in rank-1 — long delay but same fate). Sandwich economy is +0.27 better for P2 here than in rank-1 because of dist-2 cross-contributions. Best line: **opportunistic sandwich raids in the mid-late game** (ply 20+). Each raid trades 2 P2 stones for 1 P1 capture and a 2-for-3 score swing (P1 -3.5 to -4, P2 +1-2.5 net). Cluster sandwich attackers when possible (use sub-cube corners (2,2,2)-class where neighbours-of-neighbours form sandwich-clusters, unlike (0,0,0) where the L2 holes scatter attackers).

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same three as rank-1 — anchored-fan + threshold race, sandwich war, re-occupy + ledger-debt. **One new strategic axis: late-game raid timing.** Because the game runs ~54 plies vs rank-1's ~39, there's a "raid window" past ply 20 where P2 can sandwich P1 stones for influence-economy without losing tempo (the long horizon dilutes the tempo cost of trading 2-for-1 stones). This is genuinely new vs rank-1.

**Counter-play.** Real but knowledge-asymmetric. Same arms race as rank-1, plus the raid-window option for P2.

**Short-term vs long-term.** **Materially longer than rank-1.** ~21-26 ply horizon to threshold instead of ~15. Tactical decisions (4-6 ply) matter slightly less per-move; positional decisions (cluster shape, pre-emptive corner claims) matter more.

**Emergent concepts observed.**
- Same primitives as rank-1: corner sandwich, interior sandwich, ledger persistence, re-occupy.
- **Late-game raid (new vs rank-1).** P2's only way to overturn a tempo loss: opportunistic sandwich at ply 20+ when P1's cluster is committed. Each raid trades 2-for-1 stones with a 1-for-1 + 0.27 score swing; raid count needed = ~3 to win against a +21-stone P1 fan.
- **Cluster preservation incentive.** With each stone worth ~+1.86, losing 2 stones = ~−4 score = 2-3 plies of rebuilding. In rank-1 the equivalent loss was ~−4 score = 2 plies; here the rebuilding is slower but the loss is cheaper relative to threshold. **Net effect: defending clusters is mid-strength priority, not top priority.**

**Does the menger substrate matter?** Same conclusion as rank-1 — substantively (~1 depth + 1 novelty point). Hole-pattern shapes which cluster shapes are viable.

**Does the propagation kernel matter?** **More than rank-1.** The combination of r=2 + steep decay creates a "spotlight" influence pattern — strong at center, weak at edges. This adds dist-2 cross-contributions that change attacker-economy (Game 2's +0.27 P2 advantage on the same 4-move sandwich is the empirical signature). The sponge holes also matter more here because dist-2 contributions can cross holes (BFS distance = path through active cells), so a hole between two intended-cluster cells now adds dist-2 reach instead of dist-1 — a small but real recovery vs rank-1.

**Capture-rule contribution.** Captures fired in Game 2. Same 2-for-1 stone trade as rank-1, but slightly more profitable per-trade for the attacker (+0.27 score advantage in Game 2). Captures matter more here because each stone is worth less and the threshold is harder to reach.

**First-mover advantage / seat balance.** Same structural P1 favour. PPO trained-vs-random WR is 1.000 across all 3 seeds; trained-vs-trained 0.500. PPO learned the asymmetric counter cleanly. Naïve human P2 mirror loses 100% of the time.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a **parameter variant of menger rank-1** — same family, different decay/reach/threshold. Argument:

(a) Same family as rank-1: outnumber + influence + threshold-race on menger.
(b) **r=2 with steep decay** is uncommon in published influence games. Most use r=1 sharp-cutoff (Tumbleweed) or r≥2 with shallow decay (Sygo, territorial weighting). Steep-decay r=2 creates a "concentrated hot-spot" influence pattern not common in published mechanics.
(c) **Higher threshold + longer game** shifts the design toward strategic preservation rather than tactical opportunism. This pushes the game closer to Go's late-game endgame than to Othello's swingy mid-game.
(d) **Direct seed survived 8 generations untouched.** Either this parameter combination is a strong local optimum (positive read) or the evolutionary operators couldn't find anything better (concerning read). The fact that menger rank-1 is a crossover-derived variant of this family suggests evolution explored neighbours but didn't escape.

**Closest known-game analogue:** **Influence-based Tafl on a 3-D Menger sponge with concentrated-decay kernel.** Within R19, this game is the **long-horizon variant** of menger rank-1 — same recipe, different parameters, slightly more positional play because of the longer arc.

**Comparison to R8's Connection Go (8/10 ceiling).** Same as rank-1 — different family. R8 has a single-move chain-completer (custodian-bridge) that's the crown jewel of its mechanic. This game has no comparable single-move pivot — the threshold race is dominated by linear stone accumulation, with sandwich as the only non-linear option. **This is the structural ceiling: until the family allows a chain-completion-style single-move-decisive, scores stay below R8's.**

**Player rebuttal.**
- **Long-horizon preservation is a real differentiator** from rank-1: the ~54-move arc gives more time for positional play and creates the "raid window" P2 strategy. This is genuinely novel-to-this-game.
- **Dist-2 cross-contributions** add a thin layer of sandwich-attacker economy that rank-1 doesn't have. Small but real.
- **What subtracts**: same family, same emergent vocabulary, same balance asymmetry, same cluster-shape monotonicity. The longer game doesn't open new strategic branches — just dilates existing ones.

**Novelty score (post-adversary):** **5/10.** Same as rank-1 (substrate-driven novelty dominates). The long-horizon variant is interesting but adds about 0.5 points of strategic surface area — I round to 5 to stay anchored against R17 (mean 3.50, best 4.14) and to push back on the pilot calibration drift the README warns about. R8's connection-bridge is genuinely transformative; this game's long horizon is incremental.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** 98739cb0838a
**Rules Summary:** Place stones on a 9³ menger sponge (400 active cells) to accumulate influence on cells you own. Each placement spreads ±0.99 to itself, ±0.30 to direct active neighbours, ±0.09 to dist-2 cells. Outnumber-2 captures fire when an enemy stone has ≥2 of your stones among its neighbours. First to >38.96 effective influence wins — typically ~50-54 plies, ~25-27 stones per player.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 nominal.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Same depth-3 decision tree as rank-1 (mirror → sandwich → re-occupy) plus the late-game raid-window option. Per-stone arithmetic is +1.86 (linear) instead of +2.0; threshold takes ~21 stones instead of ~15. The longer arc adds positional planning surface area (cluster preservation, raid timing) but doesn't open new strategic branches. Above rank-1 by 0 because the new strategic axis (raid timing) is 1-dimensional and doesn't create new emergent vocabulary.

- **Emergent Complexity: 4** — Same primitives as rank-1: sandwich, ledger persistence, re-occupy. The raid-window is emergent from the long horizon but is a timing modification of existing patterns, not a new pattern. Below rank-1's 5 because the longer game dilutes single-move impact and emerges no new tactical concept beyond "wait longer".

- **Balance: 4** — Mirror = P1 wins by tempo at ~ply 42 (later than rank-1's ply 29). Same knowledge-asymmetric pattern: PPO learned the counter, naïve P2 mirror loses 100%. Sandwich is slightly more profitable for P2 here (dist-2 cross-contributions), but the basic balance shape is identical.

- **Novelty (post-adversary): 5** — see Phase 4. Same novelty driver (menger substrate) as rank-1, with marginal additions (steep r=2 kernel, long horizon).

- **Replayability: 4** — More moves per game than rank-1 (~54 vs ~39) means more position variety in absolute terms, but cluster shapes still converge to the same fan-from-corners set. Knowledge-asymmetric balance limits replay value once meta is known.

- **Overall "Would I play this again?": 4** — Once: yes, the long-horizon arc is interesting to feel (different from rank-1's quick race). Repeatedly: no — same strategic ceiling as rank-1 (cluster + race + sandwich), and the asymmetric balance still requires seat-swap for fair pairs. **Below pilot's 5** because I weight the same-family/no-new-vocab finding more heavily; the pilot likely scored 5 partly from the "longer game = more interesting" intuition, but in my play the longer game is an incremental modifier, not a transformative axis.

### CLOSEST KNOWN-GAME ANALOG
**Influence-based Tafl on a 3-D Menger sponge with concentrated-decay kernel** — long-horizon variant of menger rank-1. No published analogue.

### KILLER FLAWS
- **Mirror = P1 wins** (structural, ~ply 42-43). Same as all R19 games.
- **Knowledge-asymmetric balance.** PPO learned the sandwich-war counter; naïve P2 mirror loses 100%.
- **Cluster shapes converge to fans-from-corners.** Same constraint as rank-1 — opening tree collapses to ~8 corner choices × ~4 fan-direction choices.
- **Per-stone arithmetic is mostly linear** (+1.86/stone, slight cluster bonus). No superlinear killer move comparable to R8's custodian-bridge.
- **Long horizon dilutes tactical impact.** Single-move tactics rarely tip the result; ~26+ stones per side per game means each move has ~2% impact on the threshold race.
- **Direct seed survived 8 generations untouched** — concerning evolutionary signal. Either this parameter set is genuinely optimal (good) or evolution lacked operators to escape (bad).

### BEST QUALITY
**Long-horizon cluster preservation + late-game raid window.** Unlike rank-1's quick race, this game has a ~54-move arc that demands positional commitment, then offers P2 a raid-window past ply 20 to overturn tempo losses. This is closer to Go's late-game endgame than rank-1's tactical sprint. The raid-window strategy is genuinely emergent from the long horizon — not present in rank-1. **It's the most interesting positional structure I've seen in R19 games to date.**

### MENGER STRUCTURAL CONTRIBUTION
Same as rank-1: substantive (~1 depth + 1 novelty). Hole pattern shapes cluster geometry; corner-sandwich attackers can't cluster (L2 holes scatter them); interior cells exist but are rare. **Slight enhancement vs rank-1**: r=2 reach allows dist-2 contributions to cross holes, recovering some of what r=1 lost. Estimate: flattening to holeless 9³ would lose ~0.5-1.0 strategic-depth points, slightly less than rank-1 because of the dist-2 crossing benefit.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same as cross-cutting verdict).

Secondary improvements:
- **Reduce threshold to 30** to compress games to ~35 plies and tighten tactical decisions. Trades positional depth for clarity.
- **Increase decay back to 0.50** (rank-1 value). Would soften the "spotlight" influence pattern and make distance-2 cells more meaningful per-stone.
- **Add a connection or territory secondary win condition** — purely additive — to give the long horizon a narrative arc beyond the threshold race. Closest to R8's family.
- **Disable ledger persistence on capture** (subtract captured stone's contributions from board_values). Would make sandwich strictly losing in influence-delta and force P2 to find a different counter.

### Comparison to menger rank-1

| Axis | Rank-1 | Rank-2 | Delta |
|---|---|---|---|
| Threshold | 29.71 | 38.96 | +31% |
| Decay | 0.50 | 0.30 | steeper |
| Reach | r=1 | r=2 | +1 shell |
| Per-stone | +2.0 | +1.86 | -7% |
| Game length | ~39 ply | ~54 ply | +38% |
| Mirror P1-win ply | 29 | ~42 | longer arc |
| Strategic depth | 5 | 5 | tie |
| Novelty | 5 | 5 | tie |
| Overall | 4 | 4 | tie |

**Both rank-1 and rank-2 are in the same strategic family with different parameters.** Evolution didn't escape the family — rank-2 is the unmodified seed (r=2 + steep decay), rank-1 is a crossover-refined parameter tweak (r=1 + shallow decay). Human read: rank-1 has slightly tighter tactical engagement; rank-2 has slightly more positional development. Both score similarly. **The family ceiling is the limiting factor**, not the per-game parameter choice.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-1_game98739cb0838a.md`.*
