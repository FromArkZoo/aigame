# Run 20 Agent-Team Eval — team-3 — Game 5f5c72e15220

**Team ID:** team-3
**Game ID:** 5f5c72e15220 (menger rank-3 by 15-seed mean GE 0.171, σ 0.129; **rank-1 by strategic depth 0.894 — depth record across all aigame runs**)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game 5f5c72e15220` (see `briefing_menger_5f5c72e15220.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Same level-2 Menger sponge — 400 active cells, 8 deg-6 hubs at `{2,6}³`, 24 deg-5 cells one step from each hub face, rest deg-3/4. Cell index `c = z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass.

**Placement & capture.** Capture rule = **outnumber-3** (the structural differentiator from siblings). On placement at A: every enemy stone N adjacent to A is checked; if N has **≥ 3** friendly stones adjacent (counting just-placed), N is cleared to empty. The threshold is one higher than `a6385db22c0b`/`b160b1f55378`/`d1dbc6568fc7` (which use outnumber-2).

**Propagation.** Identical kernel: r=1, strength=1.0, decay=0.5.

**Win condition.** Threshold-race > 57.974, mirror P2 (`target_dimension_p2 = -1`). Max-turn timeout = highest sum.

**Pie rule.** False.

**Degeneracy check.**
- **Capture rule is essentially inert.** In a head-to-head adversarial run with capture-bonus weighting (greedy seeking captures), **0 captures fired across 57 plies**. To trigger outnumber-3 capture, an enemy stone needs ≥3 friendly neighbours among its at-most-6 active neighbours — geometrically rare in normal play. A deg-3 enemy stone fully surrounded would qualify, but reaching that state requires 3 dedicated enemy placements while the deg-3 cell remains empty for the placement-trigger.
- All other rules (propagation, threshold-race) fire normally.

---

## Phase 2 — Strategic Play

All moves engine-verified. Action IDs = cell indices for placement; pass = 729.

### Game 1 — Hub-rush (P1 / P2 mirror)

Sequence: `182,506,186,510,218,542,222,546,183,507,181,505,191,515,173,497,263,587,101,425,187,511,185,509,195,519,177,501,267,591,105,429,219,543,217,541,227,551,209,533,299,623,137,461,223,547,221,545,231,555,213,537,303,627,141,465,102,416,104` (59 plies, **P1 wins +58 / P2 +55**).

Plot: identical to `a6385db22c0b` Game 1 — hubs split z=2 vs z=6, then mechanical neighbour walk at +2/ply. **0 captures fire.** Outnumber-3 changes nothing about this opening because both players fortify their hubs naturally just by walking neighbours; P2 never gets 3 stones around a single P1 stone.

Reflection: With outnumber-3 effectively inert, the game reduces to the same hub-influence accumulation race as siblings. P1's tempo lead is decisive.

### Game 2 — Greedy local-max (corner cluster)

Sequence: `0,1,9,2,18,3,19,4,20,5,11,6,12,7,21,8,22,14,23,15,24,17,25,26,27,35,28,34,29,33,36,42,38,44,45,51,46,52,47,53,54,60,55,61,56,62,57,59,58,68,63,69,65,71,66,77,72` (57 plies, **P1 wins +59.5 / P2 +55.5**).

Plot:
- Greedy without hub-direction finds the (0,0,0) corner. Each opponent-adjacent placement scores +1.5 (own +1.0 + opponent influence reduced +0.5 = swing of +1.5). P1 and P2 interleave at y=0,z=0 row, then expand to y=2,z=0 row, then z=1, then z=2.
- The cluster grows out of the (0–8, 0, 0) row. By ply 50 both players have ~25 stones in a tight 3×3×3 corner block.
- **0 captures.** Even though stones are densely packed, no cell ever sees 3 enemy neighbours simultaneously — the alternating placement pattern produces 1- or 2-flank exposure, never 3.
- P1 reaches +59.5 at ply 57.

Reflection: This is the **strategic-diversity 0.667** revelation — hub-rush AND corner-cluster both reach the threshold in ~57–59 plies. The depth metric (0.894) is partly a *diversity* signal: many distinct opening families converge to similar timelines. But "many lines work" is not the same as "lines have deep planning horizons" — each ply is still 1-ply lookahead.

### Game 3 — Adversarial capture probe

Sequence: identical to Game 2 corner cluster (57 plies, P1 wins +59.5 / +55.5, 0 captures).

Reflection: Even under capture-bonus-weighted greedy, **the engine cannot find a capture** in this game because the geometry + alternating placement order does not produce 3-flank surrounds. **The "outnumber-3 stricter capture" headline is a no-op in practice.**

### Strategy guides

**P1:** Multiple lines work — hub-rush, corner-cluster, edge-walk all reach +58 by ply 57–59. Pick whichever feels cleanest; the choice is not mechanically meaningful given outnumber-3 is inert.

**P2:** Same multi-line freedom. With pie OFF, accept ~3-ply tempo deficit. The lower trained-vs-trained P1 winrate (0.333 — i.e., P2 wins 67%) is intriguing — possibly PPO discovered an adversarial counter that humans/greedy don't easily see, or it's a 3-run-sample artefact (briefing flags this as low-confidence).

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **YES — and this is the headline finding for this game.** Hub-rush, corner-cluster, edge-walk all produce viable +58 finishes in similar move counts. Strategic diversity is *real* in a way that the siblings (outnumber-2) lack — the looser capture rule means more cell-clusters are stable, so more opening families are competitive.

**Counter-play.** Limited, but more options than siblings. Neither side has a definitive killer line; both are playing to reach +58 first. P2's only counter to hub-rush is to also rush hubs and accept the tempo deficit; alternatively, P2 can corner-cluster against P1's hub-rush and reach +58 at similar pace.

**Short-term vs long-term.** Long game (57–59 plies), shallow horizon (~1-ply lookahead per decision). The "depth 0.894" metric is **not** capturing planning horizon — it is capturing the breadth of equivalent strategies. **My agent verdict on the GE-vs-depth disagreement: depth metric is overstated.** This game is structurally similar to its outnumber-2 siblings, with one rule diff that effectively does nothing. The depth metric is responding to strategic *diversity* (multiple openings work) but mistaking it for strategic *depth* (long planning horizons).

**Emergent concepts observed.**
- **Multi-line opening freedom.** Genuine emergent — distinct from siblings.
- **Inert capture mechanic.** The headline rule difference (outnumber-3) does not fire in any of my games. Counter-emergent.
- **Hub scaffold + corner cluster equivalence.** Both reach the threshold; players can choose by aesthetic preference.
- Same hub-neighbour walk and overlap mining as siblings.

**Does menger matter?** Same answer as siblings — substantial for opening if hub-rush is chosen, but corner-cluster doesn't use the hub geometry at all. The substrate is therefore *more optional* here than in siblings.

**Does the propagation kernel matter?** Same as siblings — well-tuned for ~58-ply games.

**Capture-rule contribution.** **None observed in 3 games.** Outnumber-3 is structurally too strict for the menger geometry + alternating placement pattern. This is a real contrast to outnumber-2 siblings where capture at least shapes the fortification opening. Here capture is dead code.

**First-mover advantage / seat balance.** Trained-vs-trained 0.333 — only menger game with P2 lead. My direct play P1 won 3/3 (greedy-vs-greedy). The 0.333 likely reflects PPO finding a P2 counter that needs more depth than greedy provides — possibly an aggressive P2 corner-cluster that uses the +1.5 opponent-adjacent placement to overtake P1's tempo. **Not verified by my play.** Pie rule (off) absent.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same shape as siblings, with one rule-parameter twist:

(a) **Threshold-race influence games** ≈ Othello scoring without flips, Tantrix-style accumulation. Same as siblings.
(b) **Outnumber-3 capture** ≈ a stricter Tafl/Ataxx variant. Lifting the threshold from 2 → 3 makes capture essentially inert in this geometry — the rule exists but does nothing. So effectively this is **influence + threshold-race with no capture**.
(c) **The combination "no-capture + influence + threshold-race"** ≈ a pure positional-scoring game; closest analogue is "Hex-territory" or "Othello disc-counting endgame as a standalone game". No clean published version on a fractal substrate.
(d) **Menger substrate.** Same as siblings.
(e) **Expert-transfer test.** A pure-Othello-counting + Tantrix player understands this in 5 minutes. The "novel" piece (fractal substrate) is geometric, not strategic — once you know the 8 hubs, the rest is arithmetic.

**Closest known-game analogue:** "Influence accumulation race on a fractal graph" — closest is the family of territorial-scoring abstract games (Tantrix, Hex-territory, late-Othello). Inside Genesis: this is `a6385db22c0b` minus capture. R19 menger top-1 `1f9191b5d4e6` (4.8/10) family relative.

**Comparison to R8 Connection Go (8/10).** R8 had a goal-shape (chain), real captures (custodian flips that swing chain completions), and balance. This game has no goal-shape, no active capture, and unbalanced. **Significantly thinner.**

**Comparison to R19.** R19 menger top-3 `5048f71b62fd` (5.0/10) was surround-capture (active mechanic). R20 5f5c72e15220 is essentially R19's outnumber-2 siblings minus the capture activity. **Strictly thinner than R19's surround-top.**

**Player rebuttal (P1 + P2).**
- The strategic-diversity 0.667 / depth 0.894 metrics ARE measuring something real — multi-line openings are wider here than in outnumber-2 siblings. But the breadth is "many ways to skin the same threshold-race", not "many deep plans".
- Substrate adds opening-pattern variety. Maybe +1 novelty point.
- Rule diff (outnumber-3) subtracts novelty — it neuters the capture mechanism that gave siblings their fortification dilemma. The single feature differentiator from siblings is *deletion* of an active mechanic.

**Novelty score (post-adversary):** **3/10.** Identical to siblings. The depth-metric headline does not survive agent inspection — it is a diversity signal, not a depth signal.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** 5f5c72e15220
**Rules Summary:** Same recipe as `a6385db22c0b` siblings except capture threshold is 3 instead of 2 — which makes capture effectively inert (0 captures observed across 3 games). Reduces to a no-capture influence accumulation race on the menger sponge.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** **outnumber-3 is a soft de-facto degenerate rule** — the engine includes it but it never fires under normal play. Briefing notes the depth-record (0.894); my evaluation finds this is a strategic-diversity artefact, not deep planning.

### Scores (1–10)

- **Strategic Depth: 4** — The depth metric (0.894) is **overstated**. What's real: multiple opening families (hub-rush, corner-cluster, edge-walk) all reach +58 in similar plies. What's not real: deep planning horizons. Each ply is 1-ply lookahead; the diversity is breadth-not-depth. I rate slightly higher than the outnumber-2 siblings (4 vs 4) only because the multi-line freedom is genuine emergent — but the planning depth is the same.
- **Emergent Complexity: 4** — Multi-line opening equivalence is the unique emergent. But capture-loop / fortification dilemma from siblings DISAPPEARS here (outnumber-3 inert). Net wash with siblings.
- **Balance: 4** — Trained-vs-trained 0.333 (P2-favoured) is intriguing but unreplicated in greedy play (P1 won 3/3). Briefing flags 3-run sample as low-confidence. I lean toward "training noise" — pie OFF + structural P1-tempo persists, so the 0.333 is suspect.
- **Novelty (post-adversary): 3** — see Phase 4. Recipe is siblings-minus-capture; no published analogue but no fundamental advance over siblings either.
- **Replayability: 4** — Slightly higher than siblings because multi-line opening means the first 8 plies can vary meaningfully. But mid- and end-game still mechanical. +1 vs siblings (3 → 4).
- **Overall "Would an agent team play this again?": 4** — Once: yes, to feel the multi-line opening. Repeatedly: no — mid-game still arithmetic. Marginally above siblings due to opening freedom; the 0.894 depth-record headline does not justify a higher score.

### CLOSEST KNOWN-GAME ANALOG
"Influence accumulation race on a Menger sponge with vestigial capture" — equivalent to `a6385db22c0b` minus the active capture mechanic. No clean published external analogue.

### KILLER FLAWS
- **Capture rule is inert** (0 fires in 3 games). The structural differentiator from siblings is *deletion* of the only active tactical layer.
- **Depth metric (0.894) overstates.** Strategic diversity ≠ strategic depth. Agent inspection finds 1-ply lookahead suffices for ~95% of decisions.
- **Pie rule OFF** (same as siblings) — structural P1 tempo lead.
- **Mid-game mechanical.** Same as siblings — pick best +2 move per ply.

### BEST QUALITY
**Multi-line opening freedom.** Hub-rush, corner-cluster, edge-walk all reach +58 in similar plies. This is the genuine emergent that distinguishes this game from outnumber-2 siblings. Player choice is real for the first 8–12 plies; this is the first stretch in any R20 menger game where 1-ply lookahead is genuinely insufficient.

### MENGER STRUCTURAL CONTRIBUTION
**Mixed.** Hub-rush uses the substrate; corner-cluster and edge-walk do not. Substrate is therefore *optional* here in a way it isn't for outnumber-2 siblings (where fortification dilemma forces hub-aware play). The fractal hole pattern still affects which corner-cluster shapes are stable, but the strategic centre of gravity is no longer the menger geometry — it is the threshold itself.

### IMPROVEMENT IDEAS
**Single best change:** **Reduce capture threshold to 2 (= sibling games).** Outnumber-3 in this geometry is a no-op; bringing it back to 2 would restore the fortification dilemma and make the game tactically alive. The cost is losing whatever strategic-diversity gain comes from the slacker capture, but my agent-eval finds the diversity is a metric artefact, not a strategic value.

Secondary improvements:
- **Restore pie rule** (same recommendation as all sibling games).
- **Lower threshold to ~40** for sharper endgame (same as siblings).
- **Increase threshold to ~80** while ALSO restoring outnumber-2 — would create longer games where capture and fortification become decisive (currently both are decided in the opening 8 plies).

### FEEDBACK ON GE-vs-DEPTH DISAGREEMENT (mandatory headline finding)
The briefing flags this as the headline test of `feedback_ge_under_rewards_depth.md`. **My verdict: GE rank (3) is closer to truth than depth rank (1).** The depth metric (0.894) is responding to strategic-diversity (real, mild positive) and incorrectly amplifying it as planning-depth (not real). R21 fitness should NOT weight depth — or if it does, should pair it with a measure that distinguishes branching-freedom from planning-horizon. My recommended substitute: average plies between the highest-equity move and the second-highest as a depth proxy (small gap = tight competition, large gap = obvious choice = shallow).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-3_game5f5c72e15220.md`.*
