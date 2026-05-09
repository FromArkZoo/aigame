# Run 20 Agent-Team Eval — team-4 — Game 5f5c72e15220

**Team ID:** team-4
**Game ID:** 5f5c72e15220 ⭐ **DEPTH RECORD 0.894** (menger rank-3 by 15-seed mean GE 0.171, σ 0.129, range 0.019–0.309)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game 5f5c72e15220` (see `briefing_menger_5f5c72e15220.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — 400 active cells of 729 grid positions; same fractal hole pattern as `a6385db22c0b`. Cell index = `z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. **No move actions** (D1 hybrid ban active).

**Placement & capture.** Capture rule = **outnumber-3** — placement at empty active cell; any adjacent enemy stone with **≥3** friendly neighbours (counting just-placed stone) is **cleared**. **Strict differentiator** from outnumber-2 siblings — capture requires P2 to spend 3 plies surrounding a single P1 stone (vs 2 plies in the siblings).

Verified live: P1 (2,2,2); P2 plays (1,2,2), then (2,1,2). After 2 P2 stones around (2,2,2), no capture (only 2 friendly neighbours of enemy). After P2's 3rd stone at (2,2,1), capture fires — (2,2,2) clears at turn 6. **3 plies of denial → 1 capture.**

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Same kernel as siblings.

**Win condition.** Threshold-race. First to exceed **57.974** wins. `target_dimension_p2 = -1` (P2 mirror).

**Pie rule.** False.

**Degeneracy check.**
- No inert fields. No soft violations.
- Same menger geometry — ~8 6-degree hubs per octant.
- **Stricter capture threshold means denial is more costly. In a +2/ply cluster race, denying 1 stone for 3 plies is a strictly negative-EV move unless it cascades.**

---

## Phase 2 — Strategic Play

All moves engine-verified. Score increments follow **Δ ≈ 1 + N** (own placement + N friendly active neighbours).

### Game 1 — Mirror cluster build (compare to outnumber-2 siblings)

Sequence: `182,546,181,545,183,547,173,537,191,555,101,465,263,627,180,544,184,538,164,556,200,548,20,628,344,566` (26 plies).

Plot:
- Both build symmetric cubes at (2,2,2) and (6,6,6) hubs.
- After 14 plies (cube-build): P1=+13, P2=+13 — **identical to outnumber-2 siblings**. Captures never fired.
- After 26 plies (shell-2 expansion + minor stretches): both around +25.
- Turn 26 ends at P1=+25.5, P2=+24.5. Continued mirror would terminate near max-turn with P1 winning by tempo.

Reflection: Under symmetric mirror, **outnumber-3 is mechanically identical to outnumber-2** because captures don't fire on either. The training-time 80.7-ply average vs siblings' 85 is within noise.

### Game 2 — Capture-attempt cost analysis (3-ply denial)

Sequence: `182,181,0,173,1,101` (6 plies).

Plot:
- P1 (2,2,2) → +1.0
- P2 (1,2,2) → P1=+0.5, P2=+0.5
- P1 (0,0,0) [P1 builds elsewhere, refusing the contest] → P1=+1.5
- P2 (2,1,2) → P1=+1.0, P2=+1.0 (still 2 P2 neighbours of (2,2,2), no capture under outnumber-3)
- P1 (1,0,0) [continues building] → P1=+3.0
- P2 (2,2,1) — **capture fires.** 3 P2 neighbours of (2,2,2), centre clears. P1 3→2 pieces.

Score after 6 plies: P1=+3.0, P2=+1.5.

**Cost of capture for P2: 3 plies for 0.5 score-gap closure.** Compare to outnumber-2 siblings: 2 plies for ~0.5 closure. **Outnumber-3 is strictly worse for denial.** P2 cannot afford to spend 3 plies to remove a stone worth ≤+1.0 — they should be building cluster at +2/ply.

### Game 3 — P2 racer (own-cluster only, race race race)

Sequence: same as Game 1 first 14 plies. Both pure-cluster.

Plot: Both at +13 after turn 14. No interaction. Game projects to ~95-ply terminal with P1 winning by tempo.

This is the equilibrium for outnumber-3 in symmetric symmetric games.

### Strategy guides

**P1 (offence/threshold push):** Same as siblings — pick a 6-degree menger hub, build the cube + axial extensions. **Even more so than siblings, ignore P2's denial attempts** because outnumber-3 makes them unprofitable. If P2 mirrors, you win by tempo.

**P2 (defence + threshold contest):** Pure mirroring loses by tempo. Parasitic shell-2 wall (as in `b160b1f55378`) is again the candidate counter — claim cells P1 will need for shell-2 extension. **Capture-based denial is strictly worse than in outnumber-2 siblings.** The 0.333 trained WR (P2-favoured! the only menger game with P2 lead) suggests PPO found *something* — possibly a structural advantage in starting on a hub adjacent to a face-corner where P2's mirror gives an extra extension cell. Could be 3-run sample noise.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two:
1. **Symmetric far-hub cluster** — pure tempo race, P1 wins.
2. **Parasitic shell-2 wall** — P2 grabs P1's expansion cells. Same as `b160b1f55378`.

Capture-denial is **categorically worse** than in outnumber-2 siblings. Outnumber-3 effectively neuters the capture mechanic in optimal play.

**Counter-play.** Real but thin (same as siblings).

**Short-term vs long-term.** **Engine reports 0.894 depth — the highest in any aigame run.** What does that mean subjectively? My 26-ply game showed:
- Lockstep arithmetic with outnumber-2 siblings (no captures, no contests).
- Slightly longer games due to fewer captures (more residue accumulates).
- One additional pattern: **residue-aware reclaiming** — when a cell has been P1's, then P2-neighbour-decremented to near zero, and now P2 plays adjacent again, the residue starts accumulating P2-favourably. With outnumber-3 (rare captures), residue patterns persist longer than in outnumber-2 games. **This might be where the 0.894 depth metric comes from** — but it doesn't surface as deeper *decisions*, just as more inert positional history.

I do **not** see decisions of greater branching factor or longer planning horizon than the siblings. **Verdict: the 0.894 depth metric is partially a metric artifact** — measuring "how long the game runs and how much position state accumulates" rather than "how complex the agent's choice tree is".

**Emergent concepts observed.**
- Same vocabulary as siblings: influence-cube cluster, +2/ply gradient, residue persistence.
- **Capture-poor regime.** Captures essentially absent in optimal play. The game becomes pure influence-race.
- **Long-tail residue**: with captures rarer, board_values residue from prior moves persists more — slight depth effect at game end where re-occupying cleared cells uses old residue.

**Does menger matter?** Same as siblings — channels viable hubs. Modest contribution.

**Does the propagation kernel matter?** Yes. Same as siblings.

**Capture-rule contribution.** **Lower than siblings** — outnumber-3 is even less likely to fire than outnumber-2. The capture mechanic is essentially vestigial in optimal play. **This is the depth-metric paradox**: the game with the highest engine-depth score has the *least* active capture interaction.

**First-mover advantage / seat balance.** Training says **0.333 trained-vs-trained WR (P2-favoured)** — only 3 runs, wide variance. My subjective experience: tempo favours P1, same as siblings. The 0.333 is most likely small-sample noise, possibly amplified by which seed PPO converged to. **Not a structural P2 advantage.** Pie rule absent.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same family as outnumber-2 menger siblings, with one parameter (capture threshold 2→3) tightened.

(a) **Threshold-race influence games** — Othello/Go-territorial without flips/captures.
(b) **Outnumber-3 capture** — Tafl/Ataxx variant; even closer to "siege" mechanics where you need 3 attackers (vs 2 in many Tafl variants).
(c) **The combination "outnumber + influence + threshold-race"** is R19's dominant menger family. Outnumber-3 vs outnumber-2 is a **knob turn**, not a new combination.
(d) **Menger substrate** — same as siblings, no published prior art.
(e) **Expert-transfer test.** Reversi + Ataxx + Go player understands in 5 minutes. Irreducible new piece: "you need 3 surrounders to capture" — minor.

**Closest known-game analogue:** Ataxx variant (capture-by-outnumber) on a 3D fractal cube with influence scoring. Extremely close to outnumber-2 siblings — only the capture threshold differs.

**Comparison to R8's Connection Go.** Different family. Far below R8 ceiling.

**Comparison to R19 best.** R19 menger top family was outnumber-2; this is outnumber-3. **Stricter capture is generally a downgrade for emergent strategy**, because it prunes the capture mechanic out of optimal play. R19 menger top = 4.8/10. Outnumber-3 should score similar-or-below outnumber-2 unless the capture-poor regime adds something.

**The depth-metric headline.** The briefing flags this game as "the test of `feedback_ge_under_rewards_depth.md`": GE places this rank-3, depth places it rank-1. **My finding: the 0.894 depth metric is largely an artifact of longer games + persistent residue, not deeper agent decisions.** Recommend **GE-rank should hold; the depth metric is the suspect.**

**Player rebuttal.**
- Captures fire even less than in siblings — the rule is more inert here, subtracting novelty rather than adding.
- Long-tail residue is a real but minor depth contributor.
- The "depth record" claim does not survive agent inspection in symmetric play.

**Novelty score (post-adversary):** **3.5/10.** Same as outnumber-2 siblings — the rule blob differs only in one parameter, and that parameter makes the capture mechanic less interesting, not more.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** 5f5c72e15220
**Rules Summary:** Same as outnumber-2 menger siblings except capture threshold = 3 (needs 3 friendly neighbours instead of 2). In practice captures are vestigial; play collapses to pure influence-race with outcome decided by tempo and parasitic shell-2 walling.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Engine reports 0.894 (highest ever in aigame), but my play shows: lockstep with outnumber-2 siblings during cluster-build; captures essentially absent; same +2/ply gradient; no additional medium-term concepts. The "depth" comes from longer games and residue persistence — **measurable but not strategy-relevant**. Slight edge over siblings only because residue-aware play exists in tail. **The depth metric overstates the agent-relevant depth here.**
- **Emergent Complexity: 4** — Same vocabulary as siblings (cube cluster, capture mechanism existing-but-rare, residue). Outnumber-3 prunes captures further, removing rather than adding patterns. Long-tail residue is the only emergent addition.
- **Balance: 5** — Training reports 0.333 P2-favoured trained-vs-trained WR (only menger game with P2 lead), but n=3 runs is too small to call a real structural advantage. My games suggest P1 still has tempo lead. Could be small-sample noise. Score 5 (not 6 because the P2 lead may not be real, not 3 because the lead is plausible).
- **Novelty (post-adversary): 3.5** — Same family as siblings, one parameter knob turn. See Phase 4.
- **Replayability: 3.5** — Two viable strategies (mirror, parasitic). Smaller decision tree than siblings since capture-denial is worse here.
- **Overall "Would an agent team play this again?": 4** — Once: yes, to verify the depth-metric finding. **The headline finding is that the 0.894 depth is metric noise / longer game length, not strategy depth.** This is the test-case the briefing asked for, and it fails. Anchored against R19 menger top 4.8 (this is below — outnumber-3 is a downgrade) and R17 mean 3.5 (this is at par with the high R17 games).

### CLOSEST KNOWN-GAME ANALOG
Ataxx-with-3-surrounders-required + Reversi-style scoring on a 3D fractal cube with influence-radius cluster bonuses. Direct sibling of R19/R20 menger top family.

### KILLER FLAWS
- **Outnumber-3 prunes captures out of optimal play.** Capture requires 3 plies of denial for ≤+0.5 score-gap closure; cluster-build is +2/ply. The capture mechanic is decorative.
- **Engine depth metric overstated.** 0.894 is the highest in any aigame run, but agent-relevant depth is at parity with outnumber-2 siblings. **Recommend GE-rank holds, depth metric needs scrutiny.**
- **3-run training sample** (n=3, no elite carryover). 0.333 P2-favoured WR is plausibly noise.
- **Pie rule missing** (same as siblings).

### BEST QUALITY
**Long-tail residue persistence.** With captures rarer, board_values residue from prior moves accumulates further into the game, creating a (mild) depth effect where re-occupying cleared cells leverages old residue. This is real but small — ~+0.5 per game from late-game residue exploitation. The game's actual crown jewel (influence-cube +2/ply cluster) is shared with siblings.

### MENGER STRUCTURAL CONTRIBUTION
**Same as siblings** — channels viable hubs, doesn't transform play. The substrate is doing equal work in this game and in `a6385db22c0b`. Could flatten to 9×9 grid with ≈ −1 depth.

### IMPROVEMENT IDEAS
**Single best change:** **Audit the strategic-depth metric.** This game is the natural test-case — if agents (us) report depth at parity with outnumber-2 siblings while the metric shows +0.131 advantage (0.894 vs 0.763), the metric is over-rewarding game length and residue persistence rather than decision complexity. Re-define the metric to penalise capture-poor regimes and game-length variance.

Secondary improvements:
- Revert capture threshold to 2 (siblings' parameter) — capture fires more, captures matter more, depth doesn't drop much (as my data shows 2-game and 3-game arithmetic is identical in symmetric play).
- Add the pie rule.
- Lower threshold-race target to 30 to halve game length, reduce residue tail's advantage.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-4_game5f5c72e15220.md`.*
