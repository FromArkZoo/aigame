# Run 21 Agent-Team Eval — team-1 — Game d995cf010504

**Team ID:** team-1
**Game ID:** d995cf010504 (carpet slate **TOP**, 20-seed mean GE 0.103, σ 0.071, calibrated komi_p2 0.05; the re-injected R20 anchor `625bfc1f3f49`)
**Substrate:** sierpinski/carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game d995cf010504` (see `briefing_carpet_d995cf010504.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 Sierpinski carpet, 64/81 active (Hausdorff 1.893). Cell = y·9 + x. The central 3×3 (x,y∈{3,4,5}) is a hole, and each 3×3 sub-block has its center punched. Net geometry: **eight solid corner/edge 3×3 blocks surrounding an empty 3×3 core.**

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100 (race ends ~ply 15).

**Action space.** 83 actions = 81 place + pass (81) + pie (82). Place-only; `adjacent_empty` vestigial (anywhere-empty confirmed).

**Placement & capture.** **outnumber-2** on a max_degree-4 board: a stone is cleared when enemy neighbors exceed friendly by ≥2. Edge/corner stones (fewer neighbors) are easier to bracket; interior block stones are protected.

**Propagation.** influence, **radius 2**, strength 1.0, decay 0.7. **Verified: distance is graph (BFS) distance, NOT Chebyshev** — a stone at (2,2) deposits +0.49 on (3,1) (graph dist 2 around the hole at (1,1)), not +0.70. Consequence: **the central void genuinely blocks/routes the field** — influence cannot cross the 3-wide void (>2 graph distance), so the eight blocks are quasi-independent battlegrounds. r=2 means stones two cells apart still interact (deposit ±0.49 on each other's cells).

**Win condition.** threshold-race. Effective owned-influence > **25.0**. `target_dimension_p2=-1` mirror. **Komi = komi_p2 × threshold = 0.05 × 25 = 1.25** (helper under-displays as 0.05).

**Pie rule.** True (action 82).

**Degeneracy check.**
- Helper komi under-display (true komi 1.25).
- `adjacent_empty` vestigial.
- The r=2 graph-distance field is **load-bearing and structurally interesting** — the void routing is a genuine substrate effect, not decoration.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 81; pie = 82.

### Game 1 — P1 corner-block race vs P2 opposite-corner block (uncontested)
Sequence: `0,8,1,7,2,6,9,17,11,15,18,26,19,25,20,24,27,35,28,34,29,33,36,44,38,42,...` (resolves ply 15).
Plot: each side packs a corner block; r=2 compounds hard (~3.4/stone). **Ply 15 P1 → +27.04 > 25, Winner=1** while P2 at +21.33. P1's full-tempo lead (~5.7) exceeds komi 1.25, so P1 wins the clean corner race.
Reflection: with r=2 a tight block compounds even faster than menger; binding constraint is still block density, and P1 keeps the tempo.

### Game 2 — Field-suppression contest (the carpet-specific lever)
Compared two lines for the **same** P1 7-stone corner block:
- P1 block, P2 plays **far away**: P1 = **+21.28**.
- P1 block, P2 plays **adjacent (within r=2)**: P1 = **+15.75** — a **~26% suppression** with no capture.
Plot: P2's stones deposit negative influence onto P1's owned cells, dragging P1's accumulator down while P2 builds its own score on the same contested frontier (both ended ~15.8). This is a genuine **two-way proximity contest** — placement *relative to the enemy* materially changes both scores.
Reflection: this is the depth the menger r=1 games lack. But it is **mutual/symmetric** — a suppressed player can relocate to one of the other (8) blocks and develop uncontested, so suppression is a tempo trade, not a dominating counter-strategy.

### Game 3 — Capture / block-choice line
Sequence: corner build with an outnumber-2 bracket on an exposed edge stone (verified clears as elsewhere in the slate).
Plot: capture fires on edge stones; the real decision is *which block to fight for vs which to concede*, since the void splits the board into independent theaters.

### Strategy guides
**P1:** seize a corner block and pack it (r=2 compounds); if P2 invades, either out-tempo in place or relocate to a fresh block. Ride the tempo to 25.
**P2:** mirror-pack a different block (komi 1.25 keeps you close), or invade P1's frontier to suppress ~25% of their field — but only if you can do so without falling behind in your own block.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two and a half: (1) pack a fresh block (dominant), (2) invade-and-suppress the enemy frontier, (3) block-selection meta (which of 8 theaters to contest). Richer than the menger pod's single plan.
**Counter-play.** Real but symmetric — suppression is answered by relocation; komi/pie balance the seats.
**Short-term vs long-term.** Short race (~15 plies) but with a genuine *positional* layer (where to fight) that menger lacks.
**Emergent concepts observed.** Field suppression via r=2 overlap; void-routing of influence; quasi-independent theaters; contiguity-as-armor. The most emergent of my menger+carpet set.
**Does the carpet substrate matter?** **Yes, more than menger's sponge does.** The void genuinely partitions the field (graph-distance r=2 can't cross it), creating 8 theaters and a "where to fight" decision. Flattening to a full 9×9 grid would *remove* this partition and collapse the block meta. This is a real substrate contribution.
**Does the propagation kernel matter?** Strongly — r=2 graph-distance is what creates suppression and routing. Drop to r=1 and it becomes the menger packing race.
**Capture contribution.** Deterrent on edge stones; secondary to field suppression.
**First-mover advantage / seat balance.** Pure corner race favors P1 by a full tempo (> komi 1.25), but the briefing's sampled-agent calibration found the **cleanest balance in the slate (bias +0.005)** — relocation/suppression options let P2 equalize in practice. Best-balanced game I evaluated.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** An influence **territory/area race** with proximity suppression and flanking capture on a fractal.
(a) Threshold-race on net influence ≈ Go-style territorial scoring; the r=2 mutual suppression ≈ influence-stone games (e.g. *Influence*/*Tumbleweed*-adjacent field dynamics).
(b) outnumber-2 ≈ Ataxx/Tafl flanking.
(c) The specific combo "r=2 graph-distance influence + outnumber capture + threshold race on a Sierpinski carpet" has no published analogue; the carpet partition is the genuinely unusual ingredient.
(d) Substrate: fractal-hole play *does* something here (theater partition), unlike menger where it only restricted.
(e) Expert-transfer: a Go/Tumbleweed player learns it in ~10 min; the void-routing of influence is the one mildly novel piece.

**Closest known-game analogue:** an area/influence race closest in spirit to *Tumbleweed*-style field accumulation, partitioned into theaters by fractal holes.
**Comparison to R8 (4.10).** Comparable playability; R8 has a cleaner asymmetric counter-strategy (the cut), carpet has a richer *field* but its contest is symmetric. Roughly a tie, different strengths.
**Comparison to R19/R20.** This is the re-injected R20 carpet anchor; the r=2 suppression makes it the strongest of my menger+carpet set, in line with R19 carpet top (4.4). Not at R20's depth-record (4.80).

**Novelty score (post-adversary): 4.0/10.** Above the menger pod (3.5) because the r=2 graph-distance field genuinely uses the carpet topology (void routing, theater partition, two-way suppression). Below R19 top (4.8)/R8(4.10-family) because the core is still "accumulate the most influence" and the contest is symmetric.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** d995cf010504
**Rules Summary:** On a Sierpinski carpet split by a central void into eight theaters, both players race to 25 points of own-color influence; a radius-2 graph-distance field means packing a block compounds fast AND that placing next to an enemy suppresses ~25% of their field, so play is a positional race over which theaters to develop and which to contest.
**Substrate:** sierpinski/carpet, axis 9, 64/81 cells, max_degree 4, pie_rule=True, komi_p2=0.05 (effective 1.25).
**Turn Structure:** alternating, 1 piece/turn.
**Hybrid actions:** no.
**Soft violations flagged:** helper komi under-display (true 1.25); vestigial `adjacent_empty`.

### Scores (1–10)
- **Strategic Depth: 4.5** — packing race PLUS a real positional layer (suppress vs relocate, which theater to fight). Deeper than the menger pod, though the contest is symmetric so no clean dominant counter-strategy.
- **Emergent Complexity: 4.5** — r=2 field suppression, void-routing of influence, and theater partition all emerge from simple rules. The richest emergent set in my menger+carpet games.
- **Balance: 4.5** — the slate's cleanest calibration (bias +0.005); komi 1.25 + pie + relocation options balance the seats well, despite a full-tempo edge in the pure corner race.
- **Novelty (post-adversary): 4.0** — see Phase 4; the carpet topology is genuinely used (unlike menger).
- **Replayability: 4.0** — 8 theaters + contest/develop choices give real opening variety; more than the menger pod, less than a true positional game.
- **Overall "Would an agent team play this again?": 4.2** — The strongest of my menger+carpet set: a clean influence race with a genuine positional contest the substrate actually shapes. Above R20 production mean (3.73), around R8 (4.10) and R19 carpet top (4.4), below the R20 depth-record (4.80) and the 5.0 G1 ceiling.

### CLOSEST KNOWN-GAME ANALOG
A *Tumbleweed*-style influence/area race partitioned into theaters by fractal holes, with Ataxx-style flanking capture. Inside the corpus, the re-injected R20 carpet anchor.

### KILLER FLAWS
- Core is still "accumulate the most influence"; dense-pack remains the dominant plan.
- The field-suppression contest is **symmetric** — answered by relocation, so it adds texture but no clean winning counter-strategy.
- Helper komi mis-display obscures the real 1.25 balancing.

### BEST QUALITY
The **radius-2 graph-distance field on a holed board**: it makes proximity a two-edged sword (compounding for you, suppressing the enemy) and lets the central void partition the board into real theaters. This is the one place in my menger+carpet set where the *substrate genuinely changes the strategy*.

### CARPET STRUCTURAL CONTRIBUTION
Real and positive. The void routes influence (graph distance r=2 can't cross it) and partitions the board into eight quasi-independent theaters — a "where to fight" meta that a flat 9×9 grid would erase. This is the carpet earning its place, unlike the menger sponge (which only restricted). Consistent with R19's menger>carpet ordering being driven by metric artifacts rather than genuine topology-use — by *use*, carpet here outperforms the menger pod.

### IMPROVEMENT IDEAS
**Single best change:** make the suppression *asymmetric* — e.g. let a player who controls a theater's majority deny the opponent's influence there entirely (a capture-the-theater bonus). That would turn the symmetric suppression into a real winnable contest and reward the block-selection meta.
Secondary:
- Lower decay or raise r at the void edges to make routing-around-the-void a sharper tactical choice.
- Fix the helper komi display.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-1_gamed995cf010504.md`.*
