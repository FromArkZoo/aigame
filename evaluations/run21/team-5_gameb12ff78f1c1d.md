# Run 21 Agent-Team Eval — team-5 — Game b12ff78f1c1d

**Team ID:** team-5
**Game ID:** b12ff78f1c1d (grid slate TOP by 20-seed mean GE 0.0985, σ 0.0517 = **most stable in the project**; gen-5 crossover child, lineage `[07d19636abaa, 09150071c8cb]`; calibrated komi_p2 0.05, G3 verdict FAIL_RUSH_BROKEN)
**Substrate:** grid (axis 8, 64 active / 64 — flat, no holes, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game b12ff78f1c1d` (see `briefing_grid_b12ff78f1c1d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, **64/64 active, no holes**, `c=y*8+x`, max_degree 4. (Live game is grid-8, not the grid-9 in some slate notes — verified against the engine.)

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **72**.

**Action space.** 66 = 64 cells + slot 64 (unused/pass) + pie(65, P2-only on move 2). Anywhere-empty (`adjacent_empty` vestigial — verified 65 legal on move 1).

**Placement & capture.** **custodian, threshold 1** (Othello/Reversi-style flip). A stone (or a contiguous line of stones) bracketed by the mover on opposite orthogonal sides is **flipped to the mover** (ownership AND influence sign change). **Verified live:**
- Single flip: P1 (3,3)+(5,3) flipped P2's (4,3).
- **Line flip: P1 bracketing P2's 2-stone line (3,3),(4,3) at (2,3)+(5,3) flipped BOTH at once (P2 6→… count dropped to 0).**
- **Dense blocks are flip-immune:** P2 could not bracket into P1's filled 3×3 block (verified — no capture fired).

**Propagation.** influence, radius 1, strength 1.0, **decay 0.5** (self +1.0, each neighbour +0.5). Verified: lone stone +1.00 on-cell / +0.50 ×4 neighbours; contested neighbour summed to −1.00.

**Win condition.** **threshold-race**, target **20.0**, `target_dimension_p2=-1` (mirror). **Komi = 0.05 × 20 = 1.0** (engine multiplicative; helper flat +0.05). Timeout (72) → piece-count majority.

**Pie rule.** True (id 65, P2-only on move 2).

**Degeneracy check.** Helper komi flat (real 1.0); `adjacent_empty` vestigial; slot 64 unused. All of capture/influence/threshold/pie are live.

---

## Phase 2 — Strategic Play

### Game 1 — Mirror 3×3 block race
Sequence: `18,45,19,46,20,47,26,53,27,54,28,55,34,61,35,62,36,63` (P1 wins ply 17).
Plot: P1 packs a central 3×3 block (18,19,20,26,27,28,34,35,36), P2 mirrors. decay-0.5 compounding (interior cell = 1 + 0.5×4 = 3.0). **Engine: P1 crosses 20 first at ply 17 (raw 21 vs P2 18+komi), Winner=1.** Komi 1.0 < the 3-point tempo lead. **Confirms FAIL_RUSH_BROKEN: a flip-immune block rushes the threshold and P1 wins by tempo.**
Reflection: the rush is dominant *and* safe — a dense block is both the fastest accumulator and immune to custodian flips. The custodian mechanic never gets to bite.

### Game 2 — Custodian flips (the latent depth)
Single flip: `27,28,29` → P1's (3,3)+(5,3) flipped P2's (4,3) (P2 1→0, stolen + influence flips).
Line flip: `26,27,10,28,29` → P1 bracketing P2's (3,3),(4,3) line flipped **both** (P2 2→0, P1 2→5). A line-flip is a **multi-stone steal** — the strongest tactical swing in the slate.
Block-immunity: `18,17,19,21,20,25` → P2's bracket attempts into P1's block fired **no** capture. Dense shapes are safe.

### Game 3 — Pie swap
Sequence: `27,65,28` → P2 swap takes P1's opening stone; clean tempo transfer.

### Strategy guides
**P1:** Rush a compact 3×3 block (flip-immune, +3/interior stone); cross 20 by ply ~17, one tempo ahead. **Never build exposed lines** (they can be line-flipped). The rush is both optimal and safe.
**P2:** You cannot stop a clean block-rush (blocks are flip-immune and P1 is one tempo ahead) — komi 1.0 and pie are your only equalisers. Custodian flips only pay off if P1 mistakenly builds flippable lines.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two *exist* — dense-block rush (dominant) and line-extension (efficient but flip-exposed) — but the dominant one is strictly safer, so play converges to block-rush. DB strategic_diversity 1.0 overstates this.
**Counter-play.** The custodian flip is a powerful counter **against linear play** — line-flips steal multiple stones + influence. But the optimal block-rush sidesteps it entirely, so counter-play is mostly latent.
**Short-term vs long-term.** ~17-ply horizon; the one medium-term consideration is "keep my shape dense to stay flip-immune."
**Emergent concepts.** **Line-flip steals** (genuine and powerful), block flip-immunity, the resulting "build dense, not long" heuristic.
**Does the grid matter?** It's the flat control — no substrate structure. Custodian works cleanly on the grid; holes would only complicate bracketing.
**Does the kernel matter?** decay 0.5 makes dense blocks even more dominant (neighbour worth half), reinforcing the rush.
**Capture contribution.** The richest *potential* in the slate (Othello-style line-flips that swing ownership AND influence) but **under-utilised** because the dominant rush is flip-immune. A paper threat against optimal play, a game-changer against linear play.
**Seat balance.** **FAIL_RUSH_BROKEN.** Sampled P1 winrate 0.47 (looks balanced) but greedy P1 winrate 0.00 / greedy seat bias 0.50 — against a determined rusher the seats are fully determined. Komi 1.0 + pie are the least-bad fix, not a real one. My mirror confirmed P1 rushes a block and wins.

**Stability ↔ quality?** **No.** This is the lowest-σ game in the project, but the stability comes from a **deterministic dominant rush** — the same flip-immune block wins every time. Stable *because* the strategy space collapses, not because the game is rich.

---

## Phase 4 — Novelty Adversary

**Adversary case.** An influence-race with Othello-style custodian capture on a flat grid.
(a) threshold-race ≈ area race. (b) **custodian flip = Reversi/Othello** capture — the most recognisable analogue in the slate. (c) "Othello-flip + influence-race + threshold" is a fresher combination than the menger/carpet outnumber-races: the flip steals influence, not just clears. (d) flat grid = no substrate novelty. (e) expert-transfer: an Othello player recognises the flip instantly (~5 min), but the influence-race wrapper is new to them.
**Closest analogue:** Reversi crossed with an area-accumulation race, on a small board.
**Comparison to R8 (4.10):** different family; the custodian flip is a *firing* mechanic (R8's surround never fired), so on mechanic-liveness it is ahead — but the rush undercuts it.
**Comparison to R19/R20:** ≈ R20 production. The Othello-flip is more distinctive than the menger outnumber-clears, but the rush-broken balance and flat substrate hold it down.

**Novelty score (post-adversary):** 3.5/10. The Othello-style line-flip (stealing ownership + influence) is the freshest *mechanic* in the influence-race games — above re-skin — but it is largely defeated by the dominant block-rush, so it stays below rule-combination novelty.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** b12ff78f1c1d
**Rules Summary:** A decay-0.5 influence-race to +20 on a flat 8×8 grid with Othello-style custodian capture (bracketed lines flip ownership + influence). The flip is a powerful tactic against linear play, but the optimal dense-block rush is both faster and flip-immune, so the first mover rushes a block and wins.
**Substrate:** grid, axis 8, 64/64 cells, max_degree 4, pie_rule=True, komi_p2=0.05 (real ×20 = 1.0).
**Turn Structure:** alternating. **Hybrid actions:** no.
**Soft violations flagged:** helper komi flat (real 1.0); `adjacent_empty` vestigial; slot 64 unused; **G3 FAIL_RUSH_BROKEN** (greedy seat bias 0.50).

### Scores (1–10)
- **Strategic Depth: 3.5** — the custodian flip *could* add depth ("build dense, not long"), but the dominant rush collapses the choice; the one live consideration is shape safety.
- **Emergent Complexity: 3.5** — line-flip steals (ownership + influence in one move) are a genuine emergent tactic, even if avoidable.
- **Balance: 3.0** — FAIL_RUSH_BROKEN; greedy seat bias 0.50, komi/pie are least-bad patches, not fixes.
- **Novelty (post-adversary): 3.5** — Othello-flip in an influence-race is the freshest mechanic of the race games; undercut by the rush.
- **Replayability: 3.0** — most stable in the project *because* the dominant rush makes every game the same.
- **Overall: 3.5** — a stable, clean game whose richest mechanic (custodian line-flip) is defeated by its own dominant rush; stability ≠ depth. ≈ R17 (3.5)/R20 production (3.73)–. Below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
Reversi/Othello crossed with an area-accumulation race, on a small flat grid.

### KILLER FLAWS
- **FAIL_RUSH_BROKEN** — a flip-immune dense block rushes the threshold; P1 wins the clean mirror by tempo, balance unfixable by komi/pie.
- **The custodian mechanic is self-defeating** — the dominant rush (dense block) is exactly the shape that is flip-immune, so the game's best idea rarely fires.

### BEST QUALITY
The **custodian line-flip**: bracketing an enemy line steals every stone in it *and* flips its influence — the single most dynamic mechanic in the influence-race games. Against linear play it is a real comeback lever.

### GRID STRUCTURAL CONTRIBUTION
Flat control — no substrate structure. The grid lets custodian bracketing work cleanly, but contributes nothing strategically; this is the dullest substrate (consistent with R19's menger>carpet>grid finding).

### IMPROVEMENT IDEAS
**Single best change:** make dense blocks flip-vulnerable (e.g. custodian also fires on 2×N enclosures, or raise decay so lines beat blocks) so the rush no longer dodges the capture mechanic — that would force the build-dense-vs-build-long tension the game *almost* has into the open and likely fix both depth and the rush-broken balance.
Secondary: the gen-5 crossover lineage shows evolution *can* compound structurally on grid, but it compounded toward *stability*, not depth — fitness should not reward low-σ as a proxy for quality (this game is the proof).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-5_gameb12ff78f1c1d.md`.*
