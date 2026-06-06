# Run 21 Agent-Team Eval — team-5 — Game e1453dac5445

**Team ID:** team-5
**Game ID:** e1453dac5445 (menger R21 top by 20-seed mean GE 0.177, σ 0.101, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e1453dac5445` (see `briefing_menger_e1453dac5445.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 Menger sponge, level-2 holes punched. 400 active cells, 329 dead. The active set is a thin shell: the central 3×3×3 and recursive sub-cubes are gone, z=1/3/4/5/7 layers heavily punched. Cell index `c = z*81 + y*9 + x`. max_degree 6 but most active cells touch far fewer than 6 neighbours because adjacent positions are holes. Verified live against the rendered board.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100.

**Action space.** 731 actions = 729 placement ids + pass (729) + pie/swap (730). Placement legal on any empty active cell — `move_constraint=adjacent_empty` is **vestigial** (verified: scattered non-adjacent placements across rows y=0 and y=8 were all legal; 383 legal after 18 moves).

**Placement & capture.** Capture = **outnumber, threshold 2**. A stone is cleared to empty when the opponent outnumbers its owner by ≥2 among its radius-1 lattice neighbours. **Verified live:** P1 stone at (1,0,0) (only 2 active neighbours, cells 0 and 2) was cleared once P2 occupied both — cost P2 two plies to remove one P1 stone.

**Propagation.** influence, radius 1, strength 1.0, **decay 1.0**. Each placed stone deposits ±1 on its own cell **and ±1 (no falloff) on every active neighbour**. This flat decay is the structural signature distinguishing R21 from R20's decay-0.5–0.7 champions.

**Win condition.** **threshold-race** (dispatch verified: threshold, not connection). First player whose effective owned-influence accumulator exceeds **30.0** wins. `target_dimension_p2=-1` ⇒ P2 mirrors P1's accumulator — both race the **same** owned-influence sum, separate accumulators. **Engine-verified scoring:** score = Σ over owned active cells of `board_values` (P1 positive, P2 negated). **Komi is multiplicative: `komi_p2 × threshold`** (engine `_check_threshold`), here 0.00 × 30 = 0. Timeout (max_turns) resolves by **piece-count majority**, not score.

**Pie rule.** True. Swap id = 730. After P1's first move P2 may swap (takes P1's stone; it becomes P1's move with P2 ahead by one tempo).

**Degeneracy check.**
- Helper's displayed P2 komi is a flat `+komi_p2` (here +0.00) — for games with komi>0 it **understates the real komi by ×threshold**. Trust engine Done/Winner, not the helper score line. (No effect here since komi=0.)
- `adjacent_empty` constraint vestigial (placement is anywhere-empty).
- No inert win-field: threshold is live, propagation live, pie wired. Only soft flag: komi gate did NOT lock in (residual P1 bias 0.060; positive komi over-corrects to P2, so 0 was served).

---

## Phase 2 — Strategic Play

All moves engine-verified. Placement ids = cell indices; pie = 730.

### Game 1 — P1 straight-line push, P2 mirrors opposite face
Sequence: `0,72,1,73,2,74,3,75,4,76,5,77,6,78,7,79,8,80` (18 plies).
Plot: P1 builds the 9-cell contiguous row y=0,z=0; P2 mirrors row y=8. A straight 9-line scores exactly **+25** (formula 3N−2: ends worth 2, interior worth 3). Both reach +25 simultaneously, P1 one tempo ahead.
Reflection: a straight line is sub-optimal — it leaves adjacency "on the table." Greedy correctly suggests contiguous expansion (+3/stone) over fresh lines (+2/stone).

### Game 2 — Compact-cluster race (both pack a 3×3-ish blob)
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28` (P1 wins ply 19).
Plot: P1 packs the (x0–2,y0–3) corner region; P2 mirrors (x6–8). A **compact cluster compounds at +3 to +5 per stone** — the move completing an interior cell (cell 20) jumped P1 +5 because it claimed pre-existing influence from 3 friendly neighbours plus boosted them. P1 leads the mirror by exactly one tempo at every step and crosses 30 first at ply 19 (10 stones vs 9). **P1 wins by pure first-mover parity.**
Reflection: the binding constraint is tempo. With identical (mirrored) packing, whoever moves first wins; komi=0 provides no offset.

### Game 3 — Adversary: P2 saps into P1's cluster + capture probe + pie
Sequence (sap): `0,1,9,2,18,11,19,20,27` — P2 plays *into* P1's region; its negative deposits dropped P1's accumulator (e.g. +9→+8 on one contact move). Mutually destructive: P2's invading stone is also sapped by P1's neighbours.
Sequence (capture): `1,0,72,2` — P2 cleared P1's isolated (1,0,0) by occupying its only two neighbours — **two P2 plies to remove one P1 stone = tempo-negative in a race.**
Sequence (pie): `20,730,11` — P2 swap takes P1's opening stone; the position becomes P1-to-move with P2 +1. Since every opening stone is worth exactly +1, the swap is a clean Hex-style tempo transfer.

### Strategy guides
**P1 (offence):** Open anywhere, then pack the densest contiguous active region you can find (full edge column / face strip avoiding the sponge holes). Each contiguous addition compounds at +3 to +5. Win in ~19 plies. Do **not** detour into the opponent — contact fighting is tempo-neutral at best.
**P2 (defence, komi=0):** You cannot win a clean mirror — P1 is always one tempo ahead. Your only real lever is the **pie swap** to seize first-mover tempo yourself, or hope P1 mis-packs around the holes. Captures cost more tempo than they buy.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Largely **no** — play converges on "build the densest contiguous blob fastest." strategic_diversity 0.181 (lowest in the menger pod) matches what I saw. The only choice is *which* contiguous shell region packs best around the holes.
**Counter-play.** Weak. Sapping and captures exist but are tempo-negative for the trailing player; the leader just keeps packing. Pie is the only structural counter and it merely transfers tempo.
**Short-term vs long-term.** Horizon ≈ "pack the next adjacency." 19-ply games leave little room for medium-term plans. The 3D hole navigation (which shell region compounds best) is the closest thing to a positional consideration.
**Emergent concepts observed.** Compounding clusters (claiming pre-existing influence), boundary sapping (−1/contact), tempo-parity decisiveness. No multi-step combinations.
**Does menger matter?** Partially. The holes force you to find contiguous active runs (a packing puzzle), and max_degree 6 lets clusters stack across z-layers. But the *answer* is always "densest blob," so the topology adds a navigation wrinkle, not a strategic axis. A flat 9×9 with the same race would play similarly minus the hole-navigation.
**Does the propagation kernel matter?** It IS the game (influence = the scored quantity). But **decay 1.0 removes the gradient** — every adjacency is worth the same, so there are no "influence wells" or falloff subtleties, only adjacency-count maximisation. Flat decay makes this *shallower*, not richer, than R20's decay-0.7 games.
**Capture-rule contribution.** Real but marginal. Outnumber-2 fires (verified) and clearing a high-degree cluster cell would drop several neighbour values — but reaching such a cell costs prohibitive tempo. In a race, captures are a paper threat (cf. R8 finding).
**First-mover advantage / seat balance.** P1 wins the clean mirror by one tempo. Komi=0 (the gate could not lock — positive komi over-corrects to P2). Pie transfers tempo but doesn't neutralise it. Residual bias 0.060. **Fragile balance.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This is an influence-accumulation race re-skinned onto a Menger sponge.
(a) Threshold-race-on-owned-influence ≈ territorial/area scoring with a finish line; the "race to N points" is a generic mechanic.
(b) Outnumber-2 capture ≈ Tafl/Ataxx custodial-by-count; here largely inert in a race.
(c) "outnumber + flat-influence + threshold-race" has no single published analogue, but each layer is familiar and the flat decay actively *reduces* the strategic content of the influence layer.
(d) Fractal substrate: Menger play is unusual, but the hole pattern functions as a packing-navigation constraint, not a new strategic dimension.
(e) Expert-transfer: a Go/Reversi player learns the whole game in ~5 minutes ("pack a dense blob, race to 30, first mover wins"). The irreducible new piece is small.

**Closest known-game analogue:** a 3D "majority/area race" (Ataxx-like accumulation) on a sponge lattice. Inside the corpus: a faster, flatter cousin of the R20 decay-0.7 influence-race champions.
**Comparison to R8 Connection Go (4.10 anchor).** Different family (race vs connection). R8 had a deep *backbone* (Hex) crippled by scale; this has a shallow backbone (packing race) executed cleanly. Roughly comparable overall once R8's inflation is removed.
**Comparison to R19/R20 best.** Thinner than R19 menger top (4.8, where outnumber-2 captures fired constantly). Comparable to R20 production champions but with flat decay making it *less* positional. The "did R21 find something new?" answer: structurally yes (flat decay, faster race), strategically no (it's a faster sprint, not a deeper game).

**Novelty score (post-adversary):** 3.5/10. Above re-skin (2–3) because flat-decay + 3D sponge packing is a genuinely distinct *configuration*; below rule-combination novelty (4–5) because the flat decay removes the influence layer's depth and play collapses to densest-packing.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** e1453dac5445
**Rules Summary:** On a Menger sponge, alternately place stones that radiate flat (no-falloff) influence to neighbours; first to amass +30 of owned influence wins. In practice it is a fast race to pack the densest contiguous blob, and the first mover wins by a tempo.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** helper komi display is flat (≠ engine's ×threshold) — cosmetic here (komi=0); `adjacent_empty` vestigial; komi gate did not lock (residual P1 bias 0.060).

### Scores (1–10)
- **Strategic Depth: 3.5** — ~19 meaningful placements but play converges on densest-packing (diversity 0.181). Hole-navigation in 3D is the only real positional wrinkle. DB strategic_depth 0.595 reads as generous subjectively.
- **Emergent Complexity: 3.0** — compounding clusters and boundary sapping arise, but flat decay removes gradient subtlety; nothing multi-step.
- **Balance: 3.0** — P1 wins clean mirror by tempo; komi gate could not lock (0 served, residual bias 0.060); pie only transfers tempo. Fragile.
- **Novelty (post-adversary): 3.5** — flat-decay sponge race is a distinct configuration but strategically a faster sprint. See Phase 4.
- **Replayability: 3.0** — low diversity; openings converge to the same packing problem.
- **Overall "Would an agent team play this again?": 3.5** — clean, fast, structurally distinct, but shallow and fragile in balance. Between R17 mean (3.5) and R20 production (3.73). Does **not** clear the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
An Ataxx/area-majority *race* on a 3D fractal lattice. Inside the corpus: a flatter, faster relative of the R20 decay-0.7 influence-race champions.

### KILLER FLAWS
- **Flat decay 1.0 collapses the influence layer to adjacency-counting** → densest-packing is dominant; no gradient play.
- **First-mover wins the clean mirror by one tempo**; komi could not be calibrated (0 served), pie only transfers the edge.
- **Captures are tempo-negative paper threats** in the race.

### BEST QUALITY
The compounding-cluster mechanic is real and satisfying: completing an interior cell can swing +5 by claiming accumulated neighbour influence. The 3D sponge makes "find the densest contiguous shell region" a small spatial puzzle.

### MENGER STRUCTURAL CONTRIBUTION
Moderate-negative-to-neutral. The holes add a packing-navigation constraint and z-layer stacking, but the dominant strategy is unchanged from a flat grid. Consistent with R19's menger>carpet>grid ranking, but the flat decay blunts the substrate's contribution.

### IMPROVEMENT IDEAS
**Single best change:** restore distance falloff (decay ≤ 0.7) so the influence field has a gradient — this is the difference between "count adjacencies" and "shape a field," and is exactly what the sibling games keep. (Equivalently: this game's headline novelty, flat decay, is its main weakness.)
Secondary:
- Make captures matter in-race (e.g. outnumber-2 also transfers influence, not just clears) so the trailing player has a real comeback lever.
- Resolve the komi gate (the current 0 leaves a measurable P1 edge); consider an asymmetric first-move restriction instead of komi.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-5_gamee1453dac5445.md`.*
