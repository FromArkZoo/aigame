# Run 20 Agent-Team Eval — team-4 — Game a6385db22c0b

**Team ID:** team-4
**Game ID:** a6385db22c0b (menger rank-1 by 15-seed mean GE 0.241, σ 0.120, depth 0.763)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game a6385db22c0b` (see `briefing_menger_a6385db22c0b.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — 400 active cells of 729 grid positions; 329 are inactive (holes) per the level-2 Menger fractal pattern. Cell index = `z*81 + y*9 + x`. The exterior surface (z=0, z=8, y=0, y=8, x=0, x=8 faces minus their fractal holes) is densely active; interior z=4 layer has only 24 active cells (a 3×3×3 micro-stamp pattern). Hausdorff dimension ≈ 2.727.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. **No move actions** (D1 hybrid ban active). Placement legal at any empty active cell.

**Placement & capture.** Placement: empty active cell, no first-move restriction. Capture rule = **outnumber-2** — when a stone is placed, every adjacent enemy stone is checked; any enemy with ≥2 friendly neighbours (counting the just-placed stone) is **cleared to empty** (not flipped — distinct from R17 custodian). Verified live: at move 4 of my Game 2, P2 plays (2,1,2) with (1,2,2) already adjacent to P1's (2,2,2); both flank → centre clears, P1 piece count 2→1.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). On placement, `board_values[cell] += ±1.0` and `board_values[neighbour] += ±0.5` for each of the ≤6 axis-aligned neighbours. Sign = +1 if P1 places, −1 if P2. Clamped to [−100, 100]. Residue persists after capture.

**Win condition.** Threshold-race. After every move, sum each player's `board_values` over cells they currently own. First to exceed **57.974** wins. `target_dimension_p2 = -1` ⇒ P2's accumulator is the negation of P1's — P2 owns "negative" cells and scores by negating. Margin tie → draw. Max-turn timeout (100 plies): highest effective sum wins.

**Pie rule.** False — lost in crossover before the `ac9e642` fix. P1 first-mover advantage is **not** corrected (training shows 0.667 P1 WR even after PPO).

**Degeneracy check.**
- No inert fields. All rule-blob params are active.
- Menger holes break adjacency irregularly. The level-2 sponge means cells like (1,1,*) along z are mostly hole; deep interior lattices (z=3, z=5 are largely hole-walls) restrict 3-D bridging to specific corridors. (2,2,2), (2,2,6), (6,2,2), (6,6,6) etc. are 6-degree hubs; most other cells have 2–4 active neighbours.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729. Score increments per placement follow the rule **Δ ≈ 1 + N** where N = own friendly active neighbours (residue + new prop on existing-own gives +0.5 each side).

### Game 1 — Mirror cluster build (P1 at (2,2,2), P2 at (6,6,6))

Sequence: `182,546,181,545,183,547,173,537,191,555,101,465,263,627,180,544,184,548,164,538,200` (21 plies).

Plot:
- Turns 1–2: each opens a 6-degree hub. Score 1.0/1.0.
- Turns 3–14: each completes its cube (centre + 6 axial neighbours). Score grows in lockstep at ≈ +2/ply (1 own + 0.5×2 friendly residue/boost). After turn 14 both at +13.0.
- Turns 15–20: shell-2 line extensions ((0,2,2), (4,2,2), (2,0,2), (2,4,2) for P1; analogous for P2). Each gives **+2** because the new cell has 1 friendly neighbour. Score still tracking lockstep.
- After 21 plies: P1=+21.0, P2=+20.0. No captures. ~17 more plies each → threshold.

Reflection (P1 / P2): With both clusters disjoint and uncontested, this is a pure tempo race. P1's 1-move lead (+1 cell of +1.0) is **persistent**: P1 reaches 57.97 a half-move before P2. Pie rule would erase this; without it, P1 wins by tempo if P2 mirrors. **The disjoint mirror is a P2-loss in expectation.**

### Game 2 — P2 contested cluster (attack P1's hub)

Sequence: `182,181,183,173,191,101,263,180,184,164,200,344,20` (13 plies — both fight over (2,2,*) hub cluster).

Plot:
- Turn 1 P1 (2,2,2). Turn 2 P2 plays (1,2,2) **directly attacking**. Each P2 stone adjacent to P1 cluster contributes its own +1 plus drains 0.5 from each adjacent P1-owned cell.
- **Turn 4: capture fires.** P2 (2,1,2) — now (1,2,2)+(2,1,2) are 2 P2-neighbours of (2,2,2). (2,2,2) clears. P1 piece count 2→1, P1 score 2.5→1.5.
- Turns 5–13: both sides keep planting on (2,2,*) hub neighbours, alternating axial expansions. P1 re-occupies the area but never the centre — board_values residue at cell 182 is now 0 (cancelled). Mid-game scores: P1=+8.5, P2=+5.5 after 13 plies.
- P1 ahead by **3 points** despite the centre capture, because P2 spent every move denying instead of building elsewhere.

Reflection (P1 / P2): Outnumber-2 captures **do** fire on contested hubs but cost P2 the +1 they could have got from a fresh 6-degree hub elsewhere on the menger surface. Denial is **negative-expectation** unless the captured cell would have given P1 an outsized +N cluster bonus. A 1-stone capture saves P1's accumulator at most ~1.0 × cluster-size. The +3 gap shows tempo>>denial here.

### Game 3 — P2 own-cluster on opposite hub (race, no contact)

Sequence: `182,564,181,556,183,627,173,465,191,545,101,547,263,537` (14 plies — P1 builds (2,2,*), P2 builds (6,*,*) shell).

Plot:
- Both build pure clusters with no contact. Score after 14 plies: P1 ~+13, P2 ~+13 (P2 catches up because cluster geometry symmetric — same 1+N gradient).
- No captures possible (clusters too far apart). Game projected to terminate near max-turn 100 with P1 winning by exactly +1.0 (the tempo lead) — matches the 85-ply training average and 0.667 P1 WR.

### Strategy guides

**P1 (offence/threshold push):** Pick a 6-degree menger hub (any of the eight (2/6, 2/6, 2/6) corner-octants, all 6-degree). Fill the central + 6 axials in any order (each +2). Then extend along axes (each +2). Avoid contested hubs with P2 — mirror denial costs more than it gains, but only if P2 plays cluster. **Never overplay near P2 stones**: each cell of yours next to P2 leaks 0.5 to them.

**P2 (defence + threshold contest):** **Do not mirror.** Pick a far hub on the opposite octant. Build with the same +2 gradient. The race is unwinnable by tempo alone, so look for one cheap capture late: if P1 ever extends a stone with 0 friendlies adjacent (a "salient"), and you have 1 stone already adjacent to it, your 2nd adjacent placement captures and saves +1. In all my games no such opportunity arose under symmetric play.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two, with one strictly weaker:
1. **Cluster-build at far hub** (race only, no contact). Slight P1 win.
2. **Contested hub denial** (P2 plays adjacent). One capture available per cluster, costs more than it saves.

A third candidate — **diffuse spread** (no clustering, just +1.0 per ply at unconnected cells) — is strictly worse: scoring rate +1.0 vs. +2.0 from clustering.

**Counter-play.** Real but thin. Counter-cluster on opposite octant guarantees a near-tie with tempo decided by who moved first. The pie rule (which would fix this) is OFF on this game.

**Short-term vs long-term.** Long-term planning is structural (which 6-degree hub do I commit to?). Tactical depth is shallow: each ply has ~1–2 +2 candidates and many +1 candidates, the +2 ones are obvious. Mid-game has no decision points worth medium-term planning. Game length 85+ plies feels like grind, not depth.

**Emergent concepts observed.**
- **Influence cube.** A 7-stone (centre + 6 axials) cluster is a stable unit producing +2/ply during expansion.
- **Capture cost-benefit gap.** Outnumber-2 single-stone capture = +1 saved to attacker, but takes the attacker 2 plies of denial vs. +2/ply of cluster-build. Almost always negative-EV unless capture cascades (none seen).
- **Tempo-locked race.** With clusters of equal value, P1's first-mover advantage persists exactly to game end.
- **No territory.** Captures clear cells, do not flip ownership; residue value persists. Compared to R8 connection-Go, no chains/groups to defend.

**Does menger matter?** Modestly. The hole pattern restricts where 6-degree hubs exist (only at coords (2/6, 2/6, 2/6) and analogous octant corners); a flat 9×9 grid + influence + outnumber-2 + threshold-race would lose the 3D bridging routes but preserve the cluster-race dynamic. The fractal hole pattern channels both players into a small set of viable hubs (~8 per octant), which paradoxically **reduces** strategy variety vs. a full 9³ cube. **Substrate adds geometric flavour, subtracts board freedom.**

**Does the propagation kernel matter?** Yes, decisively. r=1, decay=0.5 is exactly what makes clustering profitable — the 0.5 boost per friendly neighbour is the entire game. Larger r or smaller decay would change the optimal cluster shape. Without propagation, the game collapses to "place 58 stones".

**Capture-rule contribution.** Marginal. Captures fired in 1 of my 3 games (turn 4, Game 2). Rate of fire is bounded by need for 2 same-side neighbours of an enemy — typically requires P2 to spend 2 plies clustering against P1, and P1 has to oblige. Most P1 clusters are too dense (P1's own neighbours block P2 from a 2nd same-side neighbour). **Captures are present but rarely strategy-determining.**

**First-mover advantage / seat balance.** P1 has a persistent +1 tempo lead ≈ exact threshold gap. Training shows P1 WR = 0.667, my games show P1 ahead at every checkpoint in symmetric play. **Pie rule absent — bias is uncorrected.** The game is structurally P1-favoured.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of well-trodden material. Argument:

(a) **Threshold-race influence games** are closest to **Othello scoring without the flip** (count squares × value), or to **Go territorial scoring** with no captures. Tempo-by-stone-count is in Reversi family.
(b) **Outnumber-2 capture** is the **Tafl/Ataxx** rule — surrounded enemy stones get removed when outnumbered. Tafl sieges, Ataxx conversion.
(c) **The combination "outnumber + influence + threshold-race"** is what R19 produced multiple times (top-1 `1f9191b5d4e6` outnumber-2, 4.8/10). Within Genesis history, this is **the dominant menger family** — the prompt itself calls it that. Three games in this slate are byte-identical to this one.
(d) **Menger substrate.** Has fractal-Hausdorff play been studied? Combinatorial games on Menger-cube boards do not appear in published literature. The hole pattern adds geometric flavour but functions essentially as "9×9×9 with selected 329 cells removed" — not a new combinatorial structure. Hales–Jewett work on n-D cubes does not address fractal substrates specifically.
(e) **Expert-transfer test.** A Reversi + Ataxx + Go player understands this in **3–5 minutes**. Irreducible new piece: "your influence persists on captured/empty cells" (the residue rule, mildly novel). Otherwise: clusters + race + sparse captures, all familiar.

**Closest known-game analogue:** **Ataxx variant on a fractal 3D cube with influence-radius scoring.** Or: "Reversi where stones don't flip and the goal is point-threshold with cluster bonuses." Within Genesis: directly inherits R19 menger top family.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on 2D. This game is outnumber + influence + threshold-race on 3D menger. **Different family entirely.** R8's connection win drives chain-defending depth; this game has no chains and no connection. R20 sits well below R8's depth ceiling because (i) no chain/group concept, (ii) no shared-fate stones, (iii) no defensible structure beyond clusters which are uncontestable on opposite hubs.

**Comparison to R19 best.** R19 menger top-1 `1f9191b5d4e6` (outnumber-2, 4.8/10) is the **direct ancestor family**. R20 a6385db22c0b is `outnumber-2 + influence(r=1, decay=0.5) + threshold-race(57.97)` on menger — same recipe, different threshold/parameter values. Engine reports identical capture; the only mechanical change is parameter trim. **Should not score above R19's 4.8 unless something demonstrably better is happening.**

**Player rebuttal.**
- The **influence-cube cluster** as a stable +2/ply unit is genuinely emergent — no single ancestor produces this. Reversi has no influence; Ataxx has no influence; Go has no propagation. The +2/ply gradient on a 6-degree hub is novel-ish.
- **The menger hole pattern** does shape play modestly: only 8 viable cluster centres exist per octant scheme, channeling both players. Not transformative.
- **Subtractions:** Pie rule absent ⇒ P1-favoured by exact tempo, fixable degeneracy. Captures rare. No medium-term decision points after committing to a hub.

**Novelty score (post-adversary):** **3.5/10.** Above pure re-skin (2–3) because the influence-cube +2 gradient on a fractal substrate is a specific cluster shape no ancestor produces. Below R19 best (4.8) because (i) byte-identical to two siblings in this slate (`b160b1f55378`, `d1dbc6568fc7`), (ii) directly inherits R19's outnumber-2 menger family, (iii) the 0.241 GE is below R19 menger top, (iv) 0.667 P1 imbalance unmitigated.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** a6385db22c0b
**Rules Summary:** Place stones on a 9×9×9 menger sponge (400 active cells); each placement adds influence (1 own, 0.5 to each axial neighbour) of your sign; cluster of 7 stones gives +2/ply gradient; outnumber-2 surrounding clears enemy stones (residue persists); first to exceed 57.97 effective influence over owned cells wins, P2 sees mirror.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none. Pie rule absent due to crossover regression — flagged, not soft-violation.

### Scores (1–10)

- **Strategic Depth: 4** — Cluster-vs-cluster races have one binding decision (which hub) and a tempo-locked finish. 0.763 engine-depth metric does not subjectively show up: my games had ~1 inflection point (capture in Game 2) over 13–21 plies. No medium-term concepts beyond "build the cube". Below R17's 5/10 because no chains/no connection/no salvage tactics.
- **Emergent Complexity: 4** — Influence-cube cluster as a +2/ply unit is real emergence. Outnumber-2 captures on contested hubs are real but rare. No cascades, no ko-fights, no influence-shadow threats. Vocabulary is ~3 patterns wide.
- **Balance: 3** — Pie rule absent, P1 wins by exactly the tempo lead in symmetric play. Training 0.667 P1 WR is large and unmitigated. P2 has no asymmetric counter that erases the gap.
- **Novelty (post-adversary): 3.5** — direct R19 menger inheritance + Ataxx/Reversi-family rule combo + fractal substrate adds flavour but not strategy. See Phase 4.
- **Replayability: 3** — Once the 8 hub centres + cube-build pattern + "do not contest" rule are public, openings collapse. ~4 distinct opening trees per side, all leading to similar grinds. Game length 85+ plies amplifies tedium.
- **Overall "Would an agent team play this again?": 3.5** — Once: yes, to confirm cluster mechanics. Repeatedly: no — the depth ceiling is hit on game 2. Anchored against R19 menger top 4.8 (this is below) and R17 mean 3.5 (this is at-or-near).

### CLOSEST KNOWN-GAME ANALOG
Ataxx + Reversi-style scoring on a fractal 3D cube with influence-radius cluster bonuses. Within this project's corpus, direct lineage to R19 menger top-1 `1f9191b5d4e6` (outnumber-2 menger, 4.8/10).

### KILLER FLAWS
- **Pie rule missing.** P1 wins by tempo in any symmetric strategy. Training 0.667 confirms. Without pie correction, the game is structurally imbalanced.
- **Byte-identical to two slate siblings.** No structural differentiator from `b160b1f55378` and `d1dbc6568fc7` — depth differences are noise. This game's claim to rank-1 by 15-seed mean is a re-shuffle, not a discovery.
- **Captures rarely fire under correct play.** Outnumber-2 needs the placer to have 2 stones adjacent to a single enemy; cluster builders rarely give the opportunity.
- **Long grinds.** 85-ply average game is ~3× R17 length without 3× the depth — the threshold value is set too high relative to per-ply scoring rate.

### BEST QUALITY
The **+2/ply influence-cube** is the crown jewel: a 7-stone cluster on any 6-degree menger hub becomes a stable scoring engine, and shell-2 axial extensions preserve the gradient. This is a genuinely emergent stable structure that neither parent rule alone produces. It's the reason this game scores above floor.

### MENGER STRUCTURAL CONTRIBUTION
**Channels, doesn't transform.** The fractal hole pattern restricts viable cluster centres to ~8 octant hubs. A flat 9×9 grid with the same rules would lose 3D bridging but the cluster-race dynamic survives. Compared to R19 which found `menger > carpet > grid`, the menger advantage here is mostly "more 6-degree hubs available for symmetric octant builds". Could be flattened to 9×9 grid with ≈ −1 point of strategic depth and ≈ −1 point of novelty. The substrate is a flavour multiplier, not a structural pillar.

### IMPROVEMENT IDEAS
**Single best change:** **Add the pie rule** (the `ac9e642` fix that this game missed). The 0.667 P1 imbalance is the headline structural flaw and is correctable in one parameter flip.

Secondary improvements:
- Lower threshold (e.g. 28–35) to halve game length and force earlier conflict — the high 57.97 makes both sides race in parallel uncontested clusters.
- Outnumber threshold = 1 (capture on single contact) would force tactical contact in cluster build, raising depth.
- Replace `target_dimension_p2 = -1` mirror with separate accumulators to allow asymmetric strategies.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-4_gamea6385db22c0b.md`.*
