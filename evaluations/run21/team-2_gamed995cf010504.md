# Run 21 Agent-Team Eval — team-2 — Game d995cf010504

**Team ID:** team-2
**Game ID:** d995cf010504 (carpet slate TOP, 20-seed mean GE 0.103, σ 0.071, calibrated komi_p2 0.05)
**Substrate:** sierpinski/carpet (axis 9, 64 active cells / 81 grid positions, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game d995cf010504` (see `briefing_carpet_d995cf010504.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 2D Sierpinski carpet, 9×9, level-2 holes: 64 active of 81. The centre 3×3 (x,y ∈ {3,4,5}) is entirely a hole, and each 3×3 sub-block has its centre punched. Cell = y·9 + x. Net effect: the board splits into **eight solid-ish 3×3 corner/edge blocks around an empty core**, and influence cannot cross the central void.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100.

**Action space.** 83 = 81 place + pass(81) + pie(82). `first_move_anywhere`; `adjacent_empty` is vestigial (verified: non-adjacent 2nd placement legal).

**Placement & capture.** **outnumber, threshold 2** — a stone flips/clears when the opponent outnumbers the owner by ≥2 in its neighbourhood (max_degree 4 → fewer neighbours, so capture needs nearly full encirclement). Verified live in family: contested propagation drops the loser's score; pie-flip toggles ownership.

**Propagation.** `influence`, **radius 2**, strength 1.0, decay 0.7 — a Chebyshev-r2 disc, ±0.7^dist signed by owner. **Clustering compounds strongly** (verified: a short column peaked ~+1.7–1.9/cell vs +1.0 isolated). Holes carry no influence.

**Win condition.** **threshold-race**, net signed owned-influence exceeds **+25**. `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator. komi_p2 = 0.05 (bias +0.005 — the slate's cleanest). max_turns 100; with r=2 compounding the race is fast (~15 plies in my games), so the cap is rarely reached.

**Pie rule.** On (action **82**). Verified live: P2 playing 82 swaps seats, flipping P1's opening stone to P2.

**Degeneracy check.**
- `adjacent_empty` vestigial.
- `target_dimension_p2 = -1` = mirror flag, scalar accumulator.
- Captures live but, at max_degree 4, fire only on near-encircled stones — uncommon in compact blocks.
- This is the **re-injected R20 carpet anchor** (`625bfc1f3f49`, blob `seeded_from: r21_carpet_t25_d07`) — a known-good R20 reference, not a novel mutant; its original GE *underestimated* its 20-seed mean.

---

## Phase 2 — Strategic Play

Place id = cell; pass = 81; pie = 82. All engine-verified.

### Game 1 — Symmetric corner race (tempo + komi test)
Sequence: `0,8,1,7,9,17,2,6,18,26,20,24,11,15,19,25,3,5,12,14,4,23` (P1 packs the top-left 3×3 corner block then extends along y=0; P2 mirrors top-right).
Plot: ~+2.75/stone in a compact block (higher than menger — r=2 compounding). At ply 12 both ~+16.5. **P1 reached +27.04 at ply 15 (8 stones) and won**, P2 at +21.33. P1's first-move tempo carried; komi 0.05 (+0.005 effective) was far too small to overcome one tempo of r=2 compounding.
Reflection: Binding constraint = build one compact, connected mass inside a single solid block to maximise r=2 overlap. Isolated stones (+1.0) are strictly inferior and capture-exposed.

### Game 2 — Multi-block contest (does the fractal split create fronts?)
The central void means the four corner blocks are quasi-independent battlegrounds; influence does not bleed across the core. Splitting your stones across two blocks **halves your compounding** (each block accrues separately and you never get the cross-block overlap), so the dominant line is to commit to ONE block and pack it. The "multiple fronts" the geometry suggests are a trap — they dilute the r=2 bonus.
Reflection: The fractal structure shapes *where* to commit but the optimal answer is "pick one block and pack," so it does not generate multiple viable plans.

### Game 3 — Pie swap + capture
`0,82,1,...`: P2 swaps the opening, taking the +1 and tempo (the real balancer; komi +0.005 is cosmetic). Capture: at max_degree 4, flipping a stone needs it nearly surrounded — rare against a compact block, but a real lever against an over-extended isolated invader.

### Strategy guides
**P1:** open in one solid corner block, pack a compact connected mass for maximum r=2 overlap, race to +25. Don't spread across blocks.
**P2:** swap a strong opening (komi is cosmetic), else mirror-pack a corner block; punish any isolated P1 stone with an outnumber flip.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Essentially one — commit to a single solid block and pack a compact connected mass. Choice of *which* block is free but equivalent.
**Counter-play.** Out-race or swap; outnumber flips punish over-extension but don't reverse a committed packer.
**Short-term vs long-term.** Horizon ~3–4 moves; game ~15 plies — the fastest of the slate's race games. Shallow.
**Emergent concepts observed.** r=2 clustering compounding (strong); the central-void block-isolation (a structural quirk that *discourages* multi-front play); outnumber-flip punishment of isolated stones.
**Does carpet matter?** More than the menger holes do — the central void genuinely partitions the board and forces a commit-to-one-block decision. But the optimum (pack one block) means the partition narrows choice rather than enriching it.
**Does the kernel matter?** Yes most of the slate's games: r=2 (vs r=1 elsewhere) is what makes compounding strong and the race fast; decay 0.7 sets the falloff. The kernel is load-bearing here.
**Capture contribution.** Low-to-marginal (max_degree 4 makes flips hard against compact masses).
**First-mover / seat balance.** P1 tempo wins clean mirrors; komi +0.005 is cosmetic; pie is the real balancer. Still, this is flagged the slate's cleanest balance (bias +0.005).

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** A 2D influence-territory race on a Sierpinski carpet — the carpet analogue of the menger threshold-race family, with a wider (r=2) kernel.
(a) Threshold race ≈ numeric area scoring; r=2 influence ≈ a soft territory/“sphere of control” field.
(b) Outnumber-2 ≈ Ataxx/Reversi-ish flanking, weak at degree 4.
(c) "outnumber + r2-influence + threshold-race on a carpet" is not a named published game; it is the R20 carpet anchor re-injected.
(d) The fractal central void is a real structural feature (partitions the board) but resolves to "pick a block."
(e) ~5 min expert transfer.

**Closest known-game analogue:** soft-territory area race on a fractal board; in-corpus the R20 carpet pod (this *is* the R20 anchor).
**Comparison to R8 (4.10):** thinner (no cut+build / connection), faster, more convergent.
**Comparison to R19/R20 best:** it is essentially an R20-era carpet game carried forward — a sensible quality floor, consistent with R20 production (3.73). Below R19 carpet top (4.4).

**Novelty score (post-adversary):** **3.2/10.** Slightly above the menger pod because the central-void partition is a genuine (if narrowing) structural feature and r=2 compounding gives the field more texture; still a re-skin of the influence-race family.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** d995cf010504
**Rules Summary:** On a Sierpinski carpet, drop stones whose r=2 influence compounds when clustered; first to +25 net owned-influence wins. Commit to one solid corner block, pack it tight, race. The re-injected R20 carpet anchor.
**Substrate:** sierpinski/carpet, axis 9, 64/81 cells, max_degree 4, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating.
**Hybrid actions:** no.
**Soft violations flagged:** vestigial `adjacent_empty`; mirror-flag `target_dimension_p2=-1`; komi +0.005 cosmetic (pie is the balancer).

### Scores (1–10)
- **Strategic Depth: 3.6** — A fast (~15-ply) compounding race; the central-void commit-to-one-block decision is the one real positional choice, but it resolves trivially. 3–4-move horizon.
- **Emergent Complexity: 3.4** — Strong r=2 clustering compounding + block-isolation from the void are genuine emergent features; captures add little.
- **Balance: 3.9** — Slate's cleanest (bias +0.005); pie + the wide kernel keep seats close. Best balance I measured across all 7.
- **Novelty (post-adversary): 3.2** — Influence-race re-skin with a real fractal partition; modestly above the menger pod.
- **Replayability: 3.5** — A bit more opening choice (which block) than menger, but the optimum is fixed once known.
- **Overall "Would an agent team play this again?": 3.7** — A clean, well-balanced, fast race — a sensible R20-quality reference point (it *is* the R20 anchor). Around R20 production mean (3.73), below R8 (4.10) and R19 carpet top (4.4); does not clear 5.0.

### CLOSEST KNOWN-GAME ANALOG
Soft-territory area race on a fractal board; in-corpus it literally is the R20 carpet anchor `625bfc1f3f49`.

### KILLER FLAWS
- The fractal partition *narrows* choice (pick one block) rather than enriching it — multi-front play is a trap.
- Same single-blob-packing optimum as the menger family; additive-threshold scoring caps depth.
- Captures rarely matter at max_degree 4.

### BEST QUALITY
The r=2 compounding kernel + central-void partition give the field genuine texture and the cleanest seat balance in the slate — the most "finished" of the seven, even if shallow.

### carpet STRUCTURAL CONTRIBUTION
The central void is a real topological feature (partitions the board, blocks cross-core influence) — more structurally active than the menger holes' routing puzzle — but the optimum collapses it to a single-block commit. Shapes tactics; does not lift the strategic ceiling.

### IMPROVEMENT IDEAS
**Single best change:** make the win require influence dominance in **multiple** disjoint blocks (e.g., hold the larger field in ≥3 of the 4 corner blocks) — this would turn the central-void partition from a trap into a genuine multi-front strategic driver.
Secondary:
- Strengthen capture (outnumber-1 or an influence-stealing flip) so over-extension is punished harder and defence becomes a real decision.
- It is a known R20 carryover; if the goal is *novelty*, this anchor should not headline the carpet slate.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-2_gamed995cf010504.md`.*
