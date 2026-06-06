# Run 21 Agent-Team Eval — team-3 — Game d995cf010504

**Team ID:** team-3
**Game ID:** d995cf010504 (carpet slate TOP, 20-seed mean GE 0.103, σ 0.071, calibrated komi_p2 0.05; the re-injected R20 carpet anchor `625bfc1f3f49`)
**Substrate:** carpet/Sierpinski (axis 9, 64 active cells / 81 grid positions, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game d995cf010504` (see `briefing_carpet_d995cf010504.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Level-2 Sierpinski carpet, 9×9, 64 active / 81. Holes at the centre of every 3×3 block (the whole central 3×3 is void), fractally. The holes cut the board into **eight quasi-independent solid corner/edge 3×3 blocks** around an empty core; influence cannot cross the central void. Cell index `c = y*9 + x`. max_degree 4 (orthogonal only).

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **100**.

**Action space.** 83 = 81 place + pass + pie(82). Placement anywhere-empty (adjacency vestigial, verified).

**Placement & capture.** outnumber-2 → enemy stone with (enemy − friendly) ≥ 2 cleared. Max_degree 4 makes a lone stone capturable with just 2 enemy flanks; packed stones are protected.

**Propagation.** influence, **radius 2**, strength 1.0, decay 0.7 (Chebyshev). Self +1.0, dist-1 +0.7, dist-2 +0.49. **r=2 makes clustering very strong** — verified: an inner-corner stone (8th of a packed top-left block) gained **+5.76** to the accumulator (many friendly stones within the 5×5 footprint). This is the widest kernel in the slate.

**Win condition.** threshold-race net signed influence > **25.0**; mirror P2; **engine komi = 0.05 × 25 = 1.25** (helper shows 0.05 — soft violation). max_turns 100.

**Pie rule.** True (action 82).

**Degeneracy check.** `adjacent_empty` vestigial; helper under-displays komi (real +1.25). Threshold dispatch correct.

---

## Phase 2 — Strategic Play

### Game 1 — P1 corner pack vs P2 mirror (P1 overshoots and wins)
Sequence: `0,80,1,79,2,78,9,71,11,69,18,62,19,61,20,60,27,53,28,52,29,51` → ended ply 15 **P1 wins +27.04 / P2 +21.33**. With r=2, P1's packed top-left block compounds fast; the 8th inner-corner stone (cell 20) jumped P1 from +21.28 to **+27.04**, decisively overshooting 25 — so P1 wins on tempo *despite* P2's +1.25 komi. Contrast with the menger short-race (e52e), where P1 stalled just under threshold and komi flipped it: here r=2 clustering overshoots cleanly, so the tempo leader wins.
Reflection: **r=2 corner-packing is dominant** — pick a solid 3×3 corner block and fill it; the wide kernel rewards density even more than the menger games.

### Game 2 — P2 contests in the same block (capture/contest)
With max_degree 4, an exposed edge stone of a block can be outnumber-2 captured (2 enemy flanks, 0 friendly). But inside a packed block stones have friendly neighbours and are safe. P2's best contest is to **race its own corner block** (the 8 blocks are quasi-independent) rather than invade P1's — invading loses tempo and the influence can't cross the void anyway.

### Game 3 — Pie / seat probe
Pie (82) transfers tempo. Briefing reports the slate's cleanest balance (bias +0.005); my play shows P1 winning symmetric races by overshoot, so balance is good-but-P1-leaning, not perfect.

### Strategy guides
**P1:** claim the richest solid corner block and pack it densely; r=2 means a tight 3×3 cluster overshoots 25 in ~8 stones.
**P2:** race a *different* corner block at equal density (don't invade across the void); use pie if P1 takes the best block; capture only stranded P1 edge stones for free tempo.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Limited. The eight blocks are symmetric, so "pack your best corner" is the dominant plan for both — *lower* effective diversity than the menger diversity-1.0 games, because r=2 makes the corners so clearly optimal.
**Counter-play.** Out-pack a corner; pie; stranded-stone captures. No deep counter.
**Short-term vs long-term.** ~1-ply (which neighbour maximises r=2 contacts); the 8-block partition adds a small "which blocks to fight for" meta-decision but the race makes it "just take yours."
**Emergent concepts.** r=2 corner-pack dominance; the **8-quasi-independent-block** structure (influence can't cross the central void) is the carpet's genuine emergent geometry.
**Does carpet matter?** The hole pattern creates the 8-block partition — a real structural feature — but in a *race* (not territory) the partition mostly means "pack your corner," so it under-contributes vs what it could in a territory game.
**Does the kernel matter?** r=2 is load-bearing — it is what makes corner-packing overshoot the threshold; with r=1 this would play like the menger races.
**Capture contribution.** Minor — free tempo against stranded stones; not a real lever.
**First-mover / seat balance.** Cleanest in the slate (bias +0.005) via pie + komi 1.25, but my play shows P1 wins symmetric races by overshoot — slight residual P1 edge.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This is the **re-injected R20 carpet anchor `625bfc1f3f49`** — a known-good reference, explicitly *not* a novel mutant.
(a)(b) Threshold-race influence + outnumber on a Sierpinski carpet = R20 carpet family; r=2 field = a smooth territorial-influence race.
(c) "outnumber + r=2 influence + threshold-race on a carpet" = R20's carpet champion; no new external published analogue, but no advance over R20 either.
(d) The 8-block fractal partition is the substrate's contribution — present in R20.
(e) Expert transfer ~5 min ("pack a corner, race to 25").

**Closest known-game analogue:** R20 carpet threshold-race champion (this *is* it); externally a disc-counting/area-influence race on a partitioned board.
**Comparison to R8 (4.10).** No goal-shape; better balanced; the 8-block geometry is a nicer structure than R8's open grid, but the race objective is shallower than R8's connection goal.
**Comparison to R19/R20.** It is an R20 carpet champion re-served — a known reference point, neither richer nor thinner than R20.

**Novelty score (post-adversary):** **3/10.** A known R20 anchor; the r=2 carpet race is a recognised family member, not new. Anchor R8 4.10.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** d995cf010504
**Rules Summary:** On a Sierpinski carpet split into eight solid 3×3 blocks around a central void, drop stones with a wide r=2 influence field; pack a corner block densely (a tight cluster overshoots the +25 target in ~8 stones) and race. The re-injected R20 carpet anchor.
**Substrate:** carpet, axis 9, 64/81 cells, max_degree 4, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** helper under-displays komi (engine uses 1.25, helper 0.05); captures minor (stranded stones only); `adjacent_empty` vestigial.

### Scores (1–10)
- **Strategic Depth: 4** — One real layer (which corner block, how to pack it under r=2); ~1-ply. The wide kernel makes packing *more* dominant and decisions *more* obvious than the menger games.
- **Emergent Complexity: 4** — The 8-quasi-independent-block partition + r=2 compounding are genuine emergent geometry.
- **Balance: 5** — Cleanest balance in the slate (bias +0.005) via pie + komi; mild residual P1 overshoot edge.
- **Novelty (post-adversary): 3** — A re-injected R20 anchor; recognised carpet-race family.
- **Replayability: 3** — Corner-packing is near-solved; the symmetric 8 blocks reduce opening variety.
- **Overall "Would an agent team play this again?": 4.0** — A clean, well-balanced, known-good R20 carpet race; the r=2 corner-pack is satisfying but shallow and near-solved. Sits at R8-replay level (4.10)/just above R20 production (3.73); below the R19 ceiling. Confirms the carpet family is stable but not deepening.

### CLOSEST KNOWN-GAME ANALOG
R20 carpet threshold-race champion (`625bfc1f3f49`, this game); externally an area-influence/disc-counting race on a fractally-partitioned board.

### KILLER FLAWS
- r=2 makes corner-packing so dominant that diversity/depth drop; near-solved openings.
- Captures barely fire; the 8-block partition under-used by a race objective.

### BEST QUALITY
The **8-quasi-independent-block fractal partition** + the wide r=2 field that makes a tight corner cluster overshoot the threshold — a clean, legible influence-race with the slate's best seat balance.

### CARPET STRUCTURAL CONTRIBUTION
Real but under-exploited: the central void genuinely partitions the board into 8 blocks, but a *race* objective reduces this to "pack your corner." A territory/connection objective would make the partition matter far more (cf. R19's menger > carpet > grid ordering — carpet's structure shines under territorial, not race, scoring).

### IMPROVEMENT IDEAS
**Single best change:** pair this substrate with a **territory or per-block control objective** instead of a single-accumulator race — the 8-block partition is wasted on a race that collapses to corner-packing.
Secondary:
- Reduce r to 1 to restore some packing nuance/diversity, or keep r=2 but raise the threshold so blocks must be linked across edges.
- Fix helper komi display.
