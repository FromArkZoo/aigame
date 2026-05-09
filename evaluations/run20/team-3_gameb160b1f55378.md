# Run 20 Agent-Team Eval — team-3 — Game b160b1f55378

**Team ID:** team-3
**Game ID:** b160b1f55378 (menger rank-2 by 15-seed mean GE 0.180, σ 0.074, depth 0.690, ELO 2409)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game b160b1f55378` (see `briefing_menger_b160b1f55378.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Identical menger sponge as `a6385db22c0b` — 400 active cells in 9³ grid, 8 deg-6 hubs at `{2,6}³`, 24 deg-5 cells one step from each hub face. Cell index `c = z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. **No move actions** (D1 hybrid ban active). Placement legal at any empty active cell.

**Placement & capture.** Capture rule = **outnumber-2** (threshold 2). On placement at A: every enemy stone N adjacent to A is checked; if N has ≥ 2 friendly stones (counting just-placed) among its active neighbours, N is **cleared to empty** (ownership → 0; influence stays as unowned value).

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). ±1.0 self, ±0.5 neighbours, P1 sign +, P2 sign −. Clamped [−100,100].

**Win condition.** Threshold-race > 57.974. `target_dimension_p2 = -1` (mirror). Margin tie → draw. Max-turn timeout → highest sum.

**Pie rule.** False — same crossover loss as Game 1. P1's first-mover advantage uncorrected.

**Degeneracy check.**
- **Byte-identical rule blob to `a6385db22c0b` and `d1dbc6568fc7`** — confirmed engine output matches across all rule headers. Differences across these 3 are lineage-only.
- All rules fire (capture, propagation, threshold-race) — no dead paths.

---

## Phase 2 — Strategic Play

All moves engine-verified. Action IDs = cell indices for placement; pass = 729.

### Game 1 — P1 hub-rush (replay of `a6385db22c0b` Game 1)

Sequence: same hub-rush 8 hubs + 24 hub-neighbours + overlap finishes — `182,506,186,510,218,542,222,546,…` ending in P1 win at ply 59 with P1 +58.0 / P2 +55.0. **Engine output bit-identical** to Game 1's run on `a6385db22c0b` for this sequence. The "rank-2" identity is a 15-seed-mean noise effect, not a structural difference.

Plot: identical to a6385db22c0b Game 1 — hubs split z=2 / z=6, then mechanical neighbour walk at +2/ply. P1 wins by tempo at ply 59.

### Game 2 — P2 hub denial (cross-layer contest)

Sequence: `182,222,218,186,506,542,510,546,…` (53 plies, P1 wins).

Plot: P2 grabs P1's preferred z=2 hubs (222 first, then 186); P1 must take z=2 hubs (2,6,2), (2,2,2). Hubs end split 2 z=2 each + 2 z=6 each on each side. Mid-game neighbour walk converges to identical end-state. P1 wins +58 / P2 +56.

Reflection: Cross-layer denial buys nothing — symmetric hub geometry preserves equality, and P1's tempo advantage compounds the same way regardless of opening choice.

### Game 3 — Adversarial capture race (greedy capture-aware)

Sequence: same as a6385db22c0b Game 3 (since rules are byte-identical, search produces same result). 71 plies, P1 wins +58 / P2 +54.5. Same capture-loop pattern at the (0,0,0) corner: cell 11 flipped 3× empty/P1 cycle.

### Strategy guides

**P1:** Same as `a6385db22c0b`: hub-rush + 24-neighbour walk + overlap finish. Reaches +58 around ply 53–59 depending on contest pattern.

**P2:** Same as `a6385db22c0b`: mirror hub claim, accept 3-ply tempo deficit. Without pie, no path to balance.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two near-equivalent hub-claim variants for each side, plus capture-driven defence which loses to clean accumulation. Same as `a6385db22c0b`.

**Counter-play.** Limited; mirror loses to tempo, denial doesn't help, capture is a drag.

**Short-term vs long-term.** Long game (53–71 plies) but shallow horizon — most decisions are 1-ply lookahead.

**Emergent concepts observed.**
- 8-hub menger scaffold (substrate-driven).
- Hub-neighbour +2 walk (mechanical).
- Fortification dilemma when adversarial capture is a threat.
- Capture-loop as engine-ko-like cycle (Game 3, rare).
- Overlap mining for +2.5 endgame placements.

**Does menger matter?** Same as `a6385db22c0b` — substantial for opening, irrelevant by mid-game.

**Does the propagation kernel matter?** Yes — r=1 decay=0.5 produces +2/ply hub-neighbour walks that calibrate the 58-threshold against the 100-turn cap. Well-tuned.

**Capture-rule contribution.** Same as Game 1 — fires 0–1 times in clean play, only adversarial play exposes it. Structural deterrent more than active mechanic.

**First-mover advantage / seat balance.** This game's training reference is **0.500 trained-vs-trained** (vs 0.667 for `a6385db22c0b`). Tightest noise band (σ 0.074) in the slate. **But the rules are identical to `a6385db22c0b`** — the trained 0.500 is a PPO seed-equilibrium artefact, not a structural balance property. My direct play (P1 won 3/3) confirms a real ~3-ply tempo lead persists. The "balanced" headline is a training-time effect, not a true balance. Pie rule (off) would have been the real balance fix.

---

## Phase 4 — Novelty Adversary (mandatory)

Identical adversary case as `a6385db22c0b`:

(a) **Threshold-race influence games** ≈ Othello disc-counting without flip + Tantrix-style accumulation.
(b) **Outnumber-2 capture** ≈ Ataxx / Tafl with clear-on-capture instead of flip.
(c) **Combination "outnumber-2 + influence + threshold-race"** = R19 menger top-1 family rediscovered. No published external analogue.
(d) **Menger substrate.** No published analogue. The 8-hub scaffold is structural.
(e) **Expert-transfer test.** Go + Othello + Tantrix player understands in ~10 min.

**Closest known-game analogue:** "Ataxx-on-Menger with influence scoring." Inside Genesis: `a6385db22c0b` (this game's parameter twin) and R19 `1f9191b5d4e6` (4.8/10).

**Comparison to R8 Connection Go (8/10).** Different family — connection wins are goal-shaped (build a path); this is pure arithmetic accumulation. Significantly thinner.

**Comparison to R19.** Re-run of R19's outnumber-2 menger family with parameter retuning. **Family-level redundant.**

**Player rebuttal.** Capture-loops and 8-hub scaffold are the only genuine emergents. Substrate adds maybe +1 novelty point. Threshold-race subtracts (replaces goal-seeking with arithmetic). Pie OFF is a balance-flaw not a feature.

**Novelty score (post-adversary):** **3/10.** Same reasoning as `a6385db22c0b`.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** b160b1f55378
**Rules Summary:** Byte-identical recipe to `a6385db22c0b`: alternating placement on a 9³ Menger sponge with outnumber-2 capture, ±1.0/±0.5 propagation, threshold-race to >57.97. Differs from sibling games only by 15-seed-mean noise (tightest band σ=0.074) and lineage.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** **lineage redundancy** — parameter-sibling to `a6385db22c0b` and `d1dbc6568fc7`. Three slate slots, one game.

### Scores (1–10)

- **Strategic Depth: 4** — Identical decision structure to `a6385db22c0b`. Hub-claim opening (~8 plies of real choice), then mechanical neighbour walk. Engine 0.690 depth understates this slot's identity-with-Game-1; the depth is whatever the recipe gives, parameter-sibling games should not be scored differently for this measure.
- **Emergent Complexity: 4** — Same emergents: capture-loops, fortification dilemma, overlap mining. No mechanism diff.
- **Balance: 4** — Trained-vs-trained 0.500 (better than Game 1's 0.667) but rules are identical, so the 0.500 is PPO seed luck. My direct play P1 3/3. Slight bonus over `a6385db22c0b` because the lower variance suggests *some* play patterns balance, but the structural P1-favoured tempo lead persists. Calibration: not 5 because clean play still gives P1 the +2-tempo advantage; not 3 because the trained reference at least admits balanced equilibria.
- **Novelty (post-adversary): 3** — Same as `a6385db22c0b`. Re-skin of R19 menger outnumber-2 family.
- **Replayability: 3** — Same; openings collapse to a small set, mid-game is mechanical.
- **Overall "Would an agent team play this again?": 3** — Same as `a6385db22c0b`. The "rank-2" identity is a 15-seed-mean artefact; the game itself is the same recipe with one extra layer of training-luck balance.

### CLOSEST KNOWN-GAME ANALOG
"Ataxx-on-a-Menger-sponge with Othello-style influence scoring." Inside Genesis: `a6385db22c0b` and `d1dbc6568fc7` (rule-identical siblings); R19 `1f9191b5d4e6` (4.8/10) at the family level.

### KILLER FLAWS
- **Lineage redundancy.** Three of seven slate slots are this same recipe. Any structural insight from this game already applies to `a6385db22c0b` and `d1dbc6568fc7`.
- **Pie rule OFF.** P1 tempo advantage uncorrected; trained 0.500 is seed-luck, real play is P1-biased.
- **Mechanical mid-game.** Same +2-walk dominance as Game 1.
- **Capture rarely fires** in clean play (0–1×); shapes opening only.

### BEST QUALITY
Same as `a6385db22c0b`: opening 5–8 plies are non-trivial because of hub claims + fortification dilemma. The **tightest noise band (σ=0.074)** is the only headline this game owns alone — meaning whatever score it gets here, it will return to within ±0.07 across 15 fresh PPO seeds. Reproducible mediocrity.

### MENGER STRUCTURAL CONTRIBUTION
Identical to `a6385db22c0b`. The menger hole pattern provides 8 isolated hubs and a real opening structure; mid- and end-game would play similarly on any sparse high-degree graph.

### IMPROVEMENT IDEAS
**Single best change:** **Restore pie rule** — same recommendation as `a6385db22c0b`, same code path (`ac9e642`), would close the structural P1-bias.

Secondary improvements:
- **Deduplicate sibling games at the slate level.** This game and `a6385db22c0b` should not both occupy slate slots — they are not distinct experiments. R20's 5-menger slate effectively contains 3 games.
- Lower threshold to ~40 for sharper endgame (same as Game 1).
- Capture clears value as well as ownership (same as Game 1).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-3_gameb160b1f55378.md`.*
