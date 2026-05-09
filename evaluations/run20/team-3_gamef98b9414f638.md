# Run 20 Agent-Team Eval — team-3 — Game f98b9414f638

**Team ID:** team-3
**Game ID:** f98b9414f638 (menger rank-5 by 15-seed mean GE 0.129, σ 0.089, depth 0.597, ELO 2407, **threshold = 29.71** — racier than siblings)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game f98b9414f638` (see `briefing_menger_f98b9414f638.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Same level-2 Menger sponge — 400 active cells, 8 deg-6 hubs, 24 deg-5 cells.

**Turn structure.** Alternating, 1 piece per turn. P1 first. **Max_turns = 89** (vs 100 for siblings).

**Action space.** 730 actions = 729 placement + 1 pass.

**Placement & capture.** Capture rule = **outnumber-2** (same as `a6385db22c0b`/`b160b1f55378`/`d1dbc6568fc7`).

**Propagation.** Identical kernel: r=1, strength=1.0, decay=0.5.

**Win condition.** Threshold-race > **29.709** (vs 57.974 for siblings — half the target). `target_dimension_p2 = -1` (mirror).

**Pie rule.** False.

**Degeneracy check.**
- The structural odd-one-out in the menger group: same rule kernel as outnumber-2 siblings except threshold is halved. Game length should be ~half (training reference: 38.8 avg plies vs 85 for siblings).
- All rules fire normally; capture is *more* active here than in siblings because each captured stone is a larger fraction of the smaller target.

---

## Phase 2 — Strategic Play

### Game 1 — Hub-rush

Sequence: `182,506,186,510,218,542,222,546,183,507,181,505,191,515,173,497,263,587,101,425,187,511,185,509,195,519,177,501,267,591,105,429,219` (33 plies, **P1 wins +30 / P2 +28**).

Plot:
- Plies 1–8: each side claims 4 hubs as in siblings. After ply 8: P1 +4 / P2 +4.
- Plies 9–32: hub-neighbour walk at +2/ply. Score grows linearly.
- Ply 33 (P1's 17th move): P1 places `(2,5,5)` neighbour and crosses 29.71. P2 still at 28.0.

Reflection: With threshold halved, the game ends after ~17 placements per side (vs ~28 for siblings). The mid-game neighbour walk barely starts before the race ends — strategic complexity is compressed into the opening.

### Game 2 — Greedy local-max (corner cluster)

Sequence: `0,1,9,2,18,3,19,4,20,5,11,6,12,7,21,8,22,14,23,15,24,17,25,26,27,35,28,34,25,33,24,42,29` (33 plies, **P1 wins +31.5 / P2 +26**).

Plot: Corner-cluster from (0,0,0) outward. Same +1.5–2.0 swing per opponent-adjacent placement as in siblings. Ends at +31.5 in 33 plies — equivalent length to hub-rush. Neither strategy dominates.

Reflection: Two equally-fast paths to threshold; P1's tempo lead decisive in both.

### Game 3 — Adversarial capture race

Sequence (greedy capture-aware): 45 plies, **P1 wins +32 / P2 +24.5, 10 captures fired**.

Plot:
- Same corner-cluster start as Game 2, but capture-bonus drives P2 to specifically target P1 stones.
- Cell 11 = (2,1,0) flipped 3× (P1 places, P2 captures, P1 re-places, P2 re-captures, P1 re-places) — this game has the same engine-ko-like cycle as siblings.
- Cell 12 = (3,1,0) flipped multiple times; cells 23, 24 also flipped.
- **10 captures across 45 plies** (~22% capture rate per move) — substantially more than siblings (0–1% rate). The lower threshold makes each captured stone a bigger fraction of the target, so capture investment pays off relatively better.
- Despite captures, P1 still wins by tempo. Capture extends game by ~12 plies but doesn't flip the result.

Reflection: **Capture is meaningfully more active here than in any sibling game.** Outnumber-2 + low threshold = capture's economic value is amplified. This is the closest any R20 menger game gets to capture being a live tactical layer rather than vestigial.

### Strategy guides

**P1 (offence):** Hub-rush as fast as possible. The threshold is reachable in 17 P1 placements — every pty matters. Don't waste plies on captures unless P2 has placed multiple stones surrounding one of your high-value cells; in normal play, accumulation outpaces capture.

**P2 (defence + counter):** Without pie, accept ~3-ply tempo deficit on a 33-ply race. Capture is **viable** here in a way it isn't for siblings — a captured P1 stone with neighbours built up costs P1 ~+2–4 worth of value, comparable to 1–2 P2 plies. Look for hub-capture opportunities once P1 has fortified ≤4 of 6 neighbours.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, but fewer than `5f5c72e15220`:
1. Hub-rush + neighbour walk.
2. Corner-cluster + opponent-adjacent +1.5 swing.
3. Capture-driven defence (P2 only) — viable here, not in siblings.

Strategic-diversity 0.333 (lowest in slate) is consistent with a shorter race — fewer plies = fewer decision points = fewer alternative attractors.

**Counter-play.** Capture-driven defence is the best P2 has. It still loses to clean P1 hub-rush in my games, but the loss margin is small (P2 +24.5 vs threshold 29.7 — within 5 of the target when game ends).

**Short-term vs long-term.** Compressed. Game length 33–45 plies with ~half spent on opening hub-claims. Mid-game is 5–10 plies of decisive neighbour-walk; end-game is 1–3 plies of crossing the threshold.

**Emergent concepts observed.**
- All siblings' emergents (8-hub scaffold, hub-neighbour walk, fortification dilemma, overlap mining).
- **Active capture economics.** With threshold halved, capture's swing-to-cost ratio is roughly doubled. Capture is a real tactical option here, not a vestigial deterrent.
- **Compressed opening.** ~16 plies of opening-feel-territory is the entire game; closing 5–10 plies decide who crosses first. Resembles speed-chess timing.

**Does menger matter?** Same as siblings — substantial for hub-rush opening, optional for corner-cluster.

**Does the propagation kernel matter?** Yes — and **more critically here** because the threshold is tighter. A single +2 vs +1.5 difference per ply across 17 plies = +8.5 difference, ≈ 30% of the target. Sibling games have 28-ply per side, so per-ply differences are diluted. Here every ply is a 6% target-fraction.

**Capture-rule contribution.** **Real and active.** 10 captures in 45 adversarial plies. The fortification dilemma is sharper because losing a hub at +4 value is 13% of target (vs 7% for siblings). This is the most-alive capture mechanic in any R20 menger game.

**First-mover advantage / seat balance.** Trained-vs-trained 0.500 (balanced). My games P1 won 3/3. Pie OFF. The trained 0.500 suggests PPO can find good P2 counters that exploit the active capture; my greedy doesn't replicate this.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same family as siblings, with one structural diff:

(a) **Threshold-race influence games** ≈ Othello scoring without flips. Same as siblings.
(b) **Outnumber-2 capture** ≈ Ataxx/Tafl with clear-on-capture. Same as siblings.
(c) **Combination on menger substrate** = R19 menger top-1 family. Internal redundancy.
(d) **The threshold = 29.71 variant** is a parameter difference, not a structural one — and parameter differences are in the noise floor of "novelty" claims. **Subtracts** rather than adds (it makes the game shorter, not different).
(e) **Expert-transfer test.** Same as siblings; ~10-min onboarding for Go + Othello + Tantrix players.

**Closest known-game analogue:** "Speed-Ataxx-on-Menger" — same recipe as siblings with a tighter clock. Inside Genesis: parameter sibling of `a6385db22c0b`/`b160b1f55378`/`d1dbc6568fc7` with threshold halved. Externally: no clean analogue.

**Comparison to R8 (8/10).** Different family. Threshold-race ≠ goal-shape connection. Significantly thinner.

**Comparison to R19.** R19 menger top-1 `1f9191b5d4e6` (4.8/10) targeted similar threshold. This is the same family with a slight retune. **Family-level redundant.**

**Player rebuttal (P1 + P2).**
- The active capture economics is a genuine emergent benefit over siblings — captures fire 10× more often per game, the fortification dilemma actually matters in mid-game.
- Shorter game length = sharper tempo decisions — every ply is decisive in a way siblings don't see until the last 5 plies.
- Subtracts: strategic-diversity 0.333 is lowest in slate; openings collapse to fewer lines. Game is sharper but narrower.

**Novelty score (post-adversary):** **3/10.** Same as siblings on the absolute scale. The active-capture differentiator is an internal-comparison benefit, not an external-novelty benefit.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** f98b9414f638
**Rules Summary:** Same recipe as outnumber-2 siblings on the Menger sponge but with threshold halved to 29.71 — a racier 33-ply game where capture economics are doubly important and the fortification dilemma is alive throughout.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** none. The threshold-29.71 is a deliberate parameter choice, not a degeneracy.

### Scores (1–10)

- **Strategic Depth: 4** — Compressed game (33 plies) with capture-active mid-game. Slightly fewer viable strategies than siblings (diversity 0.333), but each strategy has *more* decision-pressure per ply because the threshold is tighter. Net: comparable depth to siblings, just compressed.
- **Emergent Complexity: 5** — **Bumped from siblings** because capture is genuinely active (10 captures per adversarial game vs 0–1 in siblings). The fortification dilemma is alive throughout play, not just at opening. Capture-loops emerge naturally; tempo + capture economics interact.
- **Balance: 4** — Trained-vs-trained 0.500 (balanced) is the menger group's only balanced-by-training game (along with `b160b1f55378` which is rule-identical to `a6385db22c0b` so 0.500 there is suspect). My greedy play P1 3/3, but PPO finding 0.500 suggests P2 has a real counter — possibly active capture exploiting hub-fortification gaps. Pie OFF still.
- **Novelty (post-adversary): 3** — Same as siblings on absolute scale. Active capture is differentiator internally, not externally.
- **Replayability: 4** — Shorter game with sharper decisions might reward repeated play more than siblings — each opening choice has bigger consequences. Slight bump over siblings (3 → 4).
- **Overall "Would an agent team play this again?": 4** — **Highest of the menger group**. The compressed format + active capture make this the only menger game where mid-game tactics are alive. Slightly above sibling baseline.

### CLOSEST KNOWN-GAME ANALOG
"Speed-Ataxx-on-Menger with influence scoring." Inside Genesis: parameter twin of outnumber-2 siblings with threshold halved. Externally: no clean analogue.

### KILLER FLAWS
- **Pie rule OFF** — same structural P1-tempo lead as siblings.
- **Lower strategic diversity (0.333)** — shorter game collapses opening-line variety.
- **Largest finalization collapse (Δ −0.159)** — flagged in finalization report as the most production-bias-affected game in the slate.
- **Family redundancy** with siblings (still the same recipe at the rule kernel level).

### BEST QUALITY
**Capture is alive here.** The lower threshold (29.71) doubles capture's economic value, and adversarial play produces 10 captures per game vs 0–1 in siblings. The fortification dilemma actually shapes mid-game decisions — placing a hub-neighbour vs capturing an opponent's hub-neighbour is a real choice, not a routine accumulation step. **This is the only R20 menger game where the capture mechanic is meaningfully active in normal play.**

### MENGER STRUCTURAL CONTRIBUTION
Same as siblings — 8-hub scaffold provides opening structure. With shorter game length, hubs matter relatively less (fewer plies for hub-neighbour walks to dominate); and corner-cluster strategies become competitive earlier. The substrate's contribution is therefore *partial* in this variant.

### IMPROVEMENT IDEAS
**Single best change:** **Restore pie rule** — same recommendation as all siblings. Especially important here because the shorter game amplifies tempo lead.

Secondary improvements:
- **Try threshold = 40** as a midpoint between racey-29 and grindy-58 — would extend mid-game capture-active phase without diluting tempo.
- **Combine racier threshold with outnumber-3** — would test whether the active-capture benefit comes from the threshold or the rule. Currently outnumber-3 + thresh-58 is a no-op (`5f5c72e15220`); maybe outnumber-3 + thresh-30 would be different.
- The largest finalization collapse warrants caution: this game is the most-likely-to-be-overrated in the production scoring pipeline. Re-test with more seeds.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-3_gamef98b9414f638.md`.*
