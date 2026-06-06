# Run 21 Agent-Team Eval — team-4 — Game d995cf010504

**Team ID:** team-4
**Game ID:** d995cf010504 (carpet slate TOP, 20-seed mean GE 0.103, σ 0.071, calibrated komi_p2 0.05)
**Substrate:** carpet/sierpinski (axis 9, 64 active / 81 grid positions, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game d995cf010504` (see `briefing_carpet_d995cf010504.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 Sierpinski carpet, 64 active / 81; cell = y·9 + x. 17 holes: the central 3×3 (x,y∈{3,4,5}) plus the center of each 3×3 block. The active set is **eight solid 3×3 corner/edge blocks** (8 active cells each, center hole) ringing an empty core. max_degree 4.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100.

**Action space.** 83 = 81 place + pass + pie (82). Place-only; `adjacent_empty` vestigial (verified non-adjacent 2nd placement legal).

**Placement & capture.** outnumber, **threshold 2**; **cleared to empty**. Verified live: P2 at (1,0) flanked by P1 at (0,0),(2,0) → `Captures (cleared to empty): ['(1,0)']`. Same anti-synergistic clearing as menger, but radius-2 influence partly mitigates (the two flankers still see each other at distance 2, so the capturer retained +1.58 vs menger's +0.00).

**Propagation.** influence, **radius 2**, strength 1.0, **decay 0.7** (Chebyshev-r2 disc; deposits 0.7 at d1, 0.49 at d2). Radius 2 is the carpet's signature — far stronger compounding than the radius-1 menger pod.

**Win condition.** threshold-race, **> 25.0**, `target_dimension_p2=-1` (P2 mirrors P1). komi_p2 = 0.05 (bias +0.005 — slate's cleanest).

**Pie rule.** True (action 82). Verified: P1 plays 0, P2 plays 82 → P2 owns the stone, Next: P1.

**Degeneracy check.** Anti-synergistic capture (mitigated by r2); `adjacent_empty` vestigial; influence cannot cross the central void, so the four corner blocks are quasi-independent. Provenance: gen-5 immigrant = the **re-injected R20 carpet anchor `625bfc1f3f49`** (known-good reference, not a novel mutant).

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 81; pie = 82.

### Game 1 — Symmetric block race (P1 top-left block, P2 bottom-right)
Sequence: `0,80,1,79,2,78,9,71,11,69,18,62,19,61,20,60`
Plot: **P1 wins at step 15 (8 stones).** A single fully-packed 3×3 corner block (8 active cells) reaches > 25 — because radius 2 + the compact block means every stone reinforces all 7 others. Fastest race in the whole slate.
Reflection: The binding constraint is "pack ONE corner block." The radius-2 kernel is so strong that 8 stones win; the other 56 active cells never matter.

### Game 2 — Contest / capture line
Sequence: `0,1,2` and co-occupation probes.
Plot: outnumber capture fires (`(1,0)` cleared); under sustained contest both fields drop. Radius-2 makes contested blocks partly recoverable (capturer kept +1.58), so contest is *less* purely destructive than menger — but still a losing use of tempo vs just packing your own block.
Reflection: As in the menger pod, the dominant line ignores the opponent and packs a separate block; contest only bleeds tempo.

### Game 3 — Pie / opening
Sequence: `0,82`.
Plot: Swap transfers the opening; opening is non-committal (any corner block equivalent), so pie barely bites; komi 0.05 (bias +0.005) is tiny vs the +25 target.
Reflection: My symmetric race went to P1 despite komi 0.05 — the cleanest balance in the slate still shows a mild residual first-mover edge.

### Strategy guides
**P1:** Pack a corner block contiguously (8 stones = win). Do not interact.
**P2:** Pack a different corner block; the +0.005 komi nearly but not quite cancels P1's tempo; swap is marginal.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Barely. Four interchangeable corner blocks to pack — a *choice of which*, but not a *plan*. Effectively one strategy.
**Counter-play.** Weak — contest bleeds tempo; the quasi-independent blocks mean you can't deny a determined opponent their own block.
**Short-term vs long-term.** Neither — 15-ply game, no medium-term horizon.
**Emergent concepts observed.** Quasi-independent battlegrounds (the void splits the board into 4 corner arenas) is the one mildly interesting structural property — but play never needs more than one arena. Clustering-compounds (rule restatement). Capture-poisoning (negative, r2-mitigated).
**Does carpet matter?** More than menger, slightly: the central void genuinely partitions influence, creating the 4-arena structure. But since one arena suffices to win, the partition is decorative in practice.
**Does the propagation kernel matter?** Yes — radius 2 is what makes a single 8-cell block reach 25. It also makes the race *faster/shallower* (fewer stones, less interaction).
**Capture-rule contribution.** Net slightly-negative (r2-mitigated vs menger).
**First-mover advantage / seat balance.** Cleanest in slate (bias +0.005) but my symmetric race still went P1. Residual mild edge.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Influence-area accumulation to a target, anti-synergistic outnumber, fractal substrate.
(a) Threshold-race = area/influence scoring (Tumbleweed/Reversi-count) to a fixed target.
(b) outnumber-2 → custodial-by-count, a liability.
(c) "outnumber + r2-influence + threshold-race on a Sierpinski carpet" — no published game; but the *play* is generic block-packing.
(d) Sierpinski carpet play exists in the corpus (R11/R12 carpet); the hole pattern's 4-arena partition is the one substrate contribution, but unused.
(e) Expert-transfer <3 min ("pack a corner block fastest").

**Closest known-game analogue:** influence-area race; within corpus, an R20 carpet threshold-race (literally — this is the re-injected R20 anchor).
**Comparison to R8 (4.10):** thinner (no topology objective, no real interaction).
**Comparison to R19/R20 best:** ≈ R20 production (3.73), below R19 carpet top 4.4.

**Novelty score (post-adversary):** **3.2/10.** Marginally above the menger pod for the genuine (if unused) 4-arena partition; otherwise generic block-packing. It is explicitly a re-injected R20 game, so no R21 novelty is claimed.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** d995cf010504
**Rules Summary:** Pack one Sierpinski corner block (radius-2 influence makes 8 stones reach 25) and you win — the fastest, cleanest-balanced fill-race in the slate, and a known-good re-injected R20 carpet anchor rather than an R21 discovery.
**Substrate:** carpet/sierpinski, axis 9, 64/81 cells, max_degree 4, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** anti-synergistic capture (r2-mitigated); `adjacent_empty` vestigial; 4-arena partition unused in optimal play; residual P1 edge despite cleanest komi.

### Scores (1–10)
- **Strategic Depth: 3.3** — One plan (pack a corner block), 15-ply game, choice-of-which-arena but no real planning.
- **Emergent Complexity: 3.2** — The void's 4-arena partition is a genuine structural emergent, but unused; capture-poisoning is r2-mitigated.
- **Balance: 4.2** — Cleanest in slate (bias +0.005), but my symmetric race still went P1. Mild residual edge.
- **Novelty (post-adversary): 3.2** — Generic block-packing; explicitly a re-injected R20 anchor.
- **Replayability: 3.2** — Converges to corner-pack; 4 interchangeable arenas give thin opening variety.
- **Overall "Would an agent team play this again?": 3.4** — ≈ R20 production (3.73), below R8 (4.10) and R19 carpet top (4.4). A clean, fast, known-good fill-race — not an R21 advance.

### CLOSEST KNOWN-GAME ANALOG
Influence-area race (Tumbleweed/Reversi-count to a target); within corpus, literally the re-injected R20 carpet anchor `625bfc1f3f49`.

### KILLER FLAWS
- Radius-2 makes the race a 15-ply sprint — one block wins, 56 cells wasted.
- Anti-synergistic capture; weak counterplay.
- The interesting structure (4-arena void partition) is never needed.

### BEST QUALITY
The central void genuinely partitions the influence field into four quasi-independent corner arenas — the one substrate-driven idea in the slate, even if optimal play only ever uses one arena.

### CARPET STRUCTURAL CONTRIBUTION
Real but unrealized: the fractal void creates 4 insulated battlegrounds (more than menger's decorative holes), but a single arena suffices to win, so the structure adds flavor, not strategy. Consistent with R19's menger > carpet > grid ordering only weakly.

### IMPROVEMENT IDEAS
**Single best change:** Raise the threshold (or shrink influence radius to 1) so that no single corner block can win — forcing players to fight across the 4 arenas and actually use the partition.
Secondary:
- Fix capture (pod-wide) to remove deposited influence so contest becomes a real lever.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-4_gamed995cf010504.md`.*
