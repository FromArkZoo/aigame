# Run 20 Agent-Team Eval — team-4 — Game f98b9414f638

**Team ID:** team-4
**Game ID:** f98b9414f638 (menger rank-5 by 15-seed mean GE 0.129, σ 0.089; **Δ-0.159 — biggest collapse in slate**; depth 0.597)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game f98b9414f638` (see `briefing_menger_f98b9414f638.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — 400 active cells of 729 grid positions; same fractal hole pattern as siblings. Cell index = `z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece per turn. P1 first. **Max_turns = 89** (vs 100 for siblings).

**Action space.** 730 actions = 729 placement + 1 pass. **No move actions** (D1 hybrid ban active).

**Placement & capture.** Capture rule = **outnumber-2** — same as `a6385db22c0b`/`b160b1f55378`/`d1dbc6568fc7`. Adjacent enemy with ≥2 friendly neighbours clears.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5).

**Win condition.** Threshold-race — **first to exceed 29.709 wins** (vs 57.974 for siblings — **half the threshold**). `target_dimension_p2 = -1` (mirror).

**Pie rule.** False.

**Degeneracy check.**
- No inert fields. No soft violations.
- **Structural odd-one-out in the menger slate.** Same family but threshold halved → game length halved (~38 plies vs ~85).
- Largest finalization collapse (Δ-0.159) — flagged in the report as production-score-inflated.
- Strategic-diversity 0.333 — lowest in slate. Predicted: fewer viable strategies because the racier game collapses to "build cube fastest".

---

## Phase 2 — Strategic Play

All moves engine-verified. Same +2/ply gradient as siblings; threshold-race ends at ~15 own-plies per side.

### Game 1 — Mirror cluster build (race version)

Sequence: `182,546,181,545,183,547,173,537,191,555,101,465,263,627,180,544,184,548,164,538,200` (21 plies).

Plot:
- Same arithmetic as siblings: cube-build at +2/ply each.
- Turn 14: P1=+13, P2=+13 (pure mirror).
- **Turn 20 P2 plays (7,5,6) — a shell-2 cell with 2 friendly neighbours → +3 score.** P2 jumps to +20, ahead of P1's +19.
- Turn 21 P1 plays (2,4,2) — 1-friendly-neighbour, +2 → P1=+21.
- Both well within reach of threshold 29.7 — about 5 more plies each.

Reflection: The race version is dominated by **availability of 2-neighbour shell-2 cells**. Each side's cluster geometry produces 2-3 such cells; the ply that hits one gets +3 instead of +2. Tempo can flip mid-race based on which side's cluster geometry happens to expose a 2-neighbour cell on its turn.

### Game 2 — Race-no-contact (asymmetric far hubs)

Sequence: `182,627,181,556,183,536` (6 plies — both build at distant hubs).

Plot: both build pure clusters. After 6 plies, P1=+5, P2=+3. Race continues; P1 wins by tempo if both pure-cluster.

### Game 3 — Capture verification

Sequence: `182,181,183,173` (4 plies). Turn 4: capture fires (P2's 2nd stone), P1 piece count 2→1. Same outnumber-2 mechanics as siblings.

### Strategy guides

**P1 (offence/threshold push):** Build a 6-degree menger hub fastest. With short race, every +0.5 from a friendly neighbour matters. Pre-plan extension order to maximize 2-neighbour shell-2 cells in late game (these give +3 instead of +2). Tempo is preserved if you don't let P2 reach a 2-neighbour cell before you.

**P2 (defence + threshold contest):** **Cannot afford the parasitic shell-2 strategy** — game is too short to recover from low-rate early plies. **Mirror with cluster geometry that exposes 2-neighbour cells slightly earlier** is the candidate counter. Training reports 0.500 balanced WR — likely PPO converged to seed-dependent equilibria where each lineage's cluster geometry trades 2-neighbour timing.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **One** clearly viable: **fastest cluster + best 2-neighbour timing**. The strategic-diversity 0.333 (lowest in slate) tracks this — racier threshold prunes parasitic walls and capture-denial out of optimal play.

**Counter-play.** Thin. Both sides play essentially the same strategy with seed-dependent cluster-geometry choices. Captures cost too many plies for a short race.

**Short-term vs long-term.** **Pure short-term.** Game ends in ~15 own-plies, no medium-term planning. Each ply has 1–2 +3 candidates and many +2/+1 candidates; +3 is always best when available. Tactical-only.

**Emergent concepts observed.**
- Same vocabulary as siblings: influence-cube cluster, +2/ply gradient. Plus:
- **2-neighbour shell-2 jackpot.** A cell with 2 already-friendly neighbours gives +3 score. With short race, this timing matters more.
- **No parasitic, no capture-denial, no residue-tail.** Pure race.

**Does menger matter?** **Less than for siblings.** With shorter games, the substrate's role of channeling viable hubs is less binding — there's no time to use the geometric variety. Could flatten to 9×9 grid with very minimal loss.

**Does the propagation kernel matter?** Yes — the +2/ply gradient is the entire game.

**Capture-rule contribution.** Negligible. Captures fire only if both sides intentionally provoke (Game 3 verifies they still work). In optimal play, captures don't happen.

**First-mover advantage / seat balance.** Training reports **0.500 balanced** — but this is likely seed-noise (n=12 runs, racier games have more variance). My subjective: P1 should win in pure mirror by tempo, but the 2-neighbour-jackpot timing variance can flip outcomes within ±1 ply. Pie rule absent.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same family as outnumber-2 menger siblings, with one parameter (threshold 57.97 → 29.71) halved.

(a) **Threshold-race influence games** — Othello/Go-territorial without flips/captures.
(b) **Outnumber-2 capture** — Tafl/Ataxx family.
(c) **The combination** — R19's dominant menger family.
(d) **Menger substrate** — same as siblings.
(e) **Expert-transfer test.** 3–5 minutes for Reversi+Ataxx+Go player. The racier threshold makes the game easier to learn (less endgame to navigate).

**Closest known-game analogue:** Ataxx-with-influence-scoring-and-low-target on a 3D fractal cube. Direct lineage from R19/R20 menger family.

**Comparison to R8.** Different family. Far below R8 ceiling.

**Comparison to R19 best.** R19 menger top family was outnumber-2 with similar threshold. This is the racier variant — generally a downgrade because shorter games admit fewer strategies.

**Player rebuttal.**
- Influence-cube cluster is shared with siblings.
- The **racier-threshold axis** is a structural variation worth measuring against the longer-grind axis. **My finding: shorter race reduces strategic diversity and depth.** This game's 0.333 strategic-diversity score and 0.597 depth (lowest in menger slate) confirm.
- **Subtraction:** the parasitic strategy that gives `b160b1f55378` its balance has no time to develop here.

**Novelty score (post-adversary):** **3.0/10.** Below outnumber-2 siblings (3.5) because the racier threshold prunes strategic variety. The "racier vs grindier" axis is a knob, not a new mechanic.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** f98b9414f638
**Rules Summary:** Same as outnumber-2 menger siblings except threshold = 29.71 (vs 57.97). Game length ~38 plies (half of siblings). Race-only — no time for parasitic walls, capture-denial, or residue-tail. Outcome decided by 2-neighbour-shell-2 timing.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none (but **largest finalization collapse Δ-0.159** is a production-score-inflation flag from the briefing).

### Scores (1–10)

- **Strategic Depth: 3.5** — Engine reports 0.597 (lowest in menger slate). Subjectively at parity: race ends in ~15 own-plies, no medium-term concepts, no residue-tail (game ends before residue accumulates). Tactical-only depth. Below other menger games.
- **Emergent Complexity: 3.5** — Same vocabulary as siblings minus residue-tail. The 2-neighbour-jackpot is the only race-specific pattern — but it's a rule arithmetic, not emergence.
- **Balance: 5** — Training reports 0.500 balanced. Likely seed-noise variance from racier dynamics; my subjective is P1-leaning by tempo. Score 5 (could be 4–6, calling it 5 to reflect training data + uncertainty).
- **Novelty (post-adversary): 3** — Below outnumber-2 siblings (3.5). Racier threshold knob, not new mechanic. See Phase 4.
- **Replayability: 3** — Single dominant strategy (cluster-build with 2-neighbour timing). Strategic-diversity 0.333 confirms minimal opening tree.
- **Overall "Would an agent team play this again?": 3** — Once: yes, to verify the racier-threshold dynamic. Repeatedly: no — the depth ceiling is hit on first game. Below R19 menger top (4.8) and R17 mean (3.5). The largest-collapse-in-slate finalization Δ supports a low overall score.

### CLOSEST KNOWN-GAME ANALOG
Ataxx-with-low-target-threshold on a 3D fractal cube with influence-radius cluster bonuses. Racier variant of R19/R20 menger family.

### KILLER FLAWS
- **Largest finalization collapse in slate (Δ-0.159).** Production score was inflated; honest GE 0.129 reflects a thin game.
- **Strategic-diversity 0.333 — lowest in slate.** Racier threshold prunes parasitic and capture-denial strategies.
- **Pie rule missing** (would matter even more here because tempo is decisive).
- **Captures effectively dead in optimal play** — game ends before captures can develop.

### BEST QUALITY
**The 2-neighbour-shell-2 jackpot timing.** When extending a cube cluster, certain shell-2 cells become 2-neighbour (e.g. (7,5,6) is adjacent to both (6,5,6) and (7,6,6) once both are placed). Hitting one of these cells on your ply gives +3 instead of +2. With a short race, +1 score gap can flip the outcome. This is a real timing puzzle, but it's *one* puzzle and doesn't sustain replay value.

### MENGER STRUCTURAL CONTRIBUTION
**Less than siblings.** With shorter games, the fractal hole pattern's role of channeling viable hubs is less binding. Could flatten to 9×9 grid with even less loss than siblings (~−0.5 depth).

### IMPROVEMENT IDEAS
**Single best change:** **Lower the threshold further (e.g. 15) or much higher (e.g. 80)** to make the racier-vs-grindier axis a real choice rather than the current "halfway" point. The current threshold sits in a flat zone of strategic variety.

Secondary improvements:
- Add the pie rule (would correct tempo bias).
- Penalize the "lowest-σ-among-top-5" inflation in fitness (this game's high original-GE was production noise).
- Combine with outnumber-3 to test whether stricter capture restores depth in a racier game.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-4_gamef98b9414f638.md`.*
