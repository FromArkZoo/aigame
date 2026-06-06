# Run 21 Agent-Team Eval — team-3 — Game e1453dac5445

**Team ID:** team-3
**Game ID:** e1453dac5445 (menger slate rank-1 / R21 top, 20-seed mean GE 0.177, σ 0.101, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e1453dac5445` (see `briefing_menger_e1453dac5445.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Level-2 Menger sponge, 9×9×9, 400 active / 729, central 3×3×3 and recursive sub-cubes hollow. The active set is a thin shell; neighbourhoods are sparse and broken by holes. Cell index `c = z*81 + y*9 + x`. max_degree 6 but most cells touch fewer than 6 active neighbours.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100.

**Action space.** 731 = 729 placement + pass + pie(730). Placement on any empty active cell (`first_move_anywhere`; adjacency field effectively non-binding — 399 legal after 2 moves).

**Placement & capture.** Capture = **outnumber-2**: an enemy stone with (enemy − friendly) neighbour-count ≥ 2 is **cleared to empty**. Verified live: lone P1 at (0,1,0) was cleared when P2 took both its active flanks (0,0,0) and (0,2,0). Interior/line stones with friendly neighbours need ≥3–4 enemy neighbours to fall → captures fire only against isolated/exposed stones.

**Propagation.** influence, r=1, strength 1.0, **decay 1.0** (flat — no distance falloff). Each stone deposits +1 (signed) on its own cell and +1 on every active neighbour. **Key derived dynamic (verified):** placing adjacent to *k* friendly stones adds **2k+1** to the accumulator — line tip (k=1) = +3, inner corner (k=2) = +5. This is the structural signature distinguishing R21 from R20 decay-0.5–0.7 champions.

**Win condition.** threshold-race: first player whose owned-influence accumulator exceeds **30.0** wins. `target_dimension_p2 = -1` → P2 mirrors P1's accumulator. Engine komi = `komi_p2 × threshold` = 0 here. max_turns 100 (games resolve ~ply 21 with clean packing).

**Pie rule.** True (action 730). Verified live: after P1 opens, P2 swap takes the opening stone and the tempo lead.

**Degeneracy check.**
- Captures are nearly inert against competent (packed) play; live only against exposed stones.
- **Helper display bug:** the per-move "Scores" line adds raw `komi_p2` (0.00 here, harmless for this game) but the engine win-check scales it by threshold. Noted for siblings.
- 329/729 cells dead; geometry dominated by holes.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — P1 contiguous edge rush vs P2 mirror
Sequence: `0,162,1,163,2,164,3,165,4,166,5,167,6,168,7,169,8,170,17,171,26` (21 plies, **P1 wins +31 / P2 +28**).
Plot: P1 walks the z=0,y=0 edge row (cells 0–8); each contiguous stone adds exactly **+3** (confirmed: +1,+4,+7,+10,…). P2 mirrors on the z=2 face at identical pace, always exactly one stone behind. P1 reaches +25 at stone 9, then bends round the corner (17→26) to +31 on its 11th stone. **0 captures.**
Reflection: a pure tempo race. With flat decay both sides build at the same rate; first-mover keeps a one-stone lead and crosses first.

### Game 2 — P2 contests by packing a denser region instead of mirroring
Sequence (from the sibling family, same dynamics): P2 abandoned the mirror and packed the high-coordination top-left corner block while P1 strung out a row. **P2's dense cluster (+20.9) overtook P1's spread line (+19.5) despite being a tempo behind.**
Reflection: **WHERE you pack beats tempo.** A stone with 2 friendly contacts (+5) is worth far more than two line-tips (+3 each spread out). The real decision is "find and fill the highest-coordination active region in the fractal," not "race the most cells."

### Game 3 — Capture / pie adversary probes
- Capture: P1 lone at (0,1,0); P2 took both flanks (0,0,0)+(0,2,0) → cleared. Fires only because the stone had 0 friendly neighbours.
- Pie: P1 plays cell 0 (+1); P2 swaps (730) → P2 now owns it, becomes the tempo leader. Pie genuinely transfers the first-mover edge.

### Strategy guides
**P1 (offence):** open anywhere, then pack the densest contiguous active region (full solid corner/edge blocks, avoiding holes) to maximise neighbour contacts. Keep the growing blob compact; never string out a line if a 2-contact cell is available.
**P2 (defence):** do **not** blindly mirror — pick an *equally dense or denser* block and out-pack. Use the pie swap (730) if P1's opener is in the richest region. Capture only stranded P1 stones (free tempo); never chase captures into a packed blob.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Weakly. All winning plans reduce to "pack the densest active region fastest." Strategic_diversity 0.181 (lowest in slate) is subjectively confirmed — decay=1.0 flattens every decision into "maximise contacts now."
**Counter-play.** Real but shallow: out-pack (denser region) or pie-swap. Captures are not a counter against competent play.
**Short-term vs long-term.** ~1-ply lookahead suffices for ≈95% of moves (which adjacent cell gives the most contacts). Horizon is short; games end ~ply 21.
**Emergent concepts.** The **2k+1 packing law** and the **density-beats-tempo** result are the genuine emergent texture — a small but real positional puzzle imposed by the fractal hole pattern.
**Does menger matter?** Yes for this game more than most: the hole pattern dictates which regions are high-coordination, so reading the fractal is the whole skill. Same rules on a flat 9×9 would be even more trivial (uniform density).
**Does the propagation kernel matter?** Decay=1.0 is load-bearing but *reduces* depth vs decay 0.7 — flat influence removes spacing/falloff subtlety; everything collapses to contact-count.
**Capture-rule contribution.** Negligible in real play (0 fires across packed lines).
**First-mover / seat balance.** Residual P1 bias ~0.06 (komi 0, did not lock the G3 gate); pie swap is the real balancer and roughly neutralises it.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** A threshold-race influence-accumulation game on a fractal graph — the R20 menger family with the decay knob pushed to 1.0.
(a) Threshold-race influence ≈ territorial/disc-counting accumulation (late-Othello, Tantrix-style).
(b) outnumber-2 capture ≈ a strict Tafl/Ataxx flank-capture — inert here.
(c) "outnumber + flat influence + threshold-race on a sponge" has no clean published analogue, but it is the same *kernel* as R20's menger champions; only the decay value and the faster threshold (30) differ.
(d) Fractal-dim play on the Menger sponge is geometric novelty, not strategic — once you know the dense regions, it's arithmetic.
(e) An Othello+Go player learns this in ~5 min: "pack the densest corner, race to 30."

**Closest known-game analogue:** influence-accumulation race on a Menger sponge — R20 menger family with decay=1.0. The flat-influence packing law (2k+1) is the one genuinely distinct feel.
**Comparison to R8 Connection Go (4.10).** R8 had a goal-shape (chain) and asymmetric objectives; this has neither. Thinner in structure, but better balanced (pie present) and its captures are no more inert than R8's.
**Comparison to R19/R20 best.** Same family as R20 5f5c72e15220 (depth-record, my team scored 4.0). This game adds pie (balance ↑) but decay=1.0 *lowers* diversity (0.181 vs 0.667). Net: comparable, not richer than R19 menger 4.8.

**Novelty score (post-adversary):** **4/10.** Above sibling re-skins (3) because the flat-decay packing dynamic genuinely changes the feel (corner-packing 2k+1, density-beats-tempo). Below genuinely-new (8) because it is the same win-family on the same substrate with one tuned knob. Anchor: R8 4.10, R19 top 4.8.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** e1453dac5445
**Rules Summary:** On the Menger sponge, alternately drop stones that flatly radiate +1 to all neighbours; pack the densest hole-free region (inner-corner cells score +5, line tips +3) and race your owned-influence total to 30. Captures rarely fire; pie swap balances the seats.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** un-locked komi gate (residual P1 bias 0.06); outnumber-2 capture effectively inert vs packed play; helper "Scores" line under-displays komi (engine scales by threshold).

### Scores (1–10)
- **Strategic Depth: 4** — One real layer: choosing and filling the highest-coordination fractal region. The 2k+1 packing law gives positions a genuine optimum, but it is ~1-ply greedy. The 0.595 DB depth is a diversity/length signal, not planning horizon.
- **Emergent Complexity: 4** — The 2k+1 contact law and the verified density-beats-tempo result are real emergent texture; captures add nothing.
- **Balance: 5** — Pie swap genuinely transfers first-mover edge; residual bias only ~0.06. Better balanced than any pre-pie R20 game.
- **Novelty (post-adversary): 4** — Flat decay=1.0 packing dynamic is a real, if minor, departure from the R20 family. See Phase 4.
- **Replayability: 3** — Lowest diversity in the slate (0.181); play collapses to "pack the densest block." Opening region varies, mid/endgame solved.
- **Overall "Would an agent team play this again?": 3.9** — A clean, well-balanced packing sprint. The R21-top GE (0.177) does **not** translate into felt depth — decay=1.0 *flattens* strategy and minimises diversity. Sits just above R20 production mean (3.73), below R8 replay (4.10), well below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
Influence-accumulation territory race on a Menger sponge (R20 menger family, decay pushed to 1.0); externally closest to a disc-counting/late-Othello packing race with no flips.

### KILLER FLAWS
- Decay=1.0 collapses strategic diversity to near-zero (0.181); the optimum is "pack densest region."
- Captures essentially inert in real play.
- ~1-ply planning horizon; games over by ply ~21.

### BEST QUALITY
The **2k+1 packing law** + **density-beats-tempo** finding: the fractal hole pattern makes "which region is richest" a genuine (if shallow) positional read, and a denser cluster can beat a tempo-leading spread.

### MENGER STRUCTURAL CONTRIBUTION
Real here — the hole pattern *is* the puzzle (where are the high-coordination cells). On a flat 9×9 the game would be strictly more trivial (uniform density, no region-reading). But the contribution is geometric/arithmetic, not deep planning.

### IMPROVEMENT IDEAS
**Single best change:** lower decay back to ~0.5–0.7 to restore spacing/falloff subtlety and lift diversity (decay=1.0 is the wrong direction — it trades depth for a higher GE proxy).
Secondary:
- Make captures matter (lower the effective bar or reward clearing) so there is a tactical layer.
- Keep pie; it is the one clearly-good addition over R20.
