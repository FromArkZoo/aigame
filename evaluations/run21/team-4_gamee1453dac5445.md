# Run 21 Agent-Team Eval — team-4 — Game e1453dac5445

**Team ID:** team-4
**Game ID:** e1453dac5445 (menger rank 1 / slate top, 20-seed mean GE 0.177, σ 0.101, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e1453dac5445` (see `briefing_menger_e1453dac5445.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge, level-2 holes punched at every center-cross cell. 400 active of 729; cell = z·81 + y·9 + x. The active set is a thin fractal shell: corner 3×3×3 subcubes are themselves level-1 menger sponges (20 active each), interior is hollow. Verified live: z=1/4/7 layers are heavily punched (full rows of `#`).

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 100 (hard cap; games end *far* sooner — see Phase 2).

**Action space.** 731 actions = 729 placement + pass (729) + pie/swap (730). Place-only (D1 ban). `first_move_anywhere=True`; the blob's `adjacent_empty` constraint is vestigial (397 legal after 4 moves — anywhere-empty).

**Placement & capture.** Capture = **outnumber, threshold 2**. A stone is **cleared to empty** when enemies outnumber friendlies by ≥2 in its radius-1 (≤6) neighborhood. Verified live: P2 at (1,0,0) flanked by P1 at (0,0,0) and (2,0,0) → `Captures (cleared to empty): ['(1,0,0)']`.

**Propagation.** influence, radius 1, strength 1.0, **decay 1.0** (flat — no distance falloff). Each placed stone deposits ±1 on its own cell and ±1 on every active radius-1 neighbor. This decay=1.0 is the structural signature distinguishing it from the R20 decay-0.5–0.7 champions.

**Win condition.** threshold-race. First player whose effective owned-influence accumulator (sum of `board_values` over cells they own) exceeds **30.0** wins. `target_dimension_p2=-1` ⇒ P2 mirrors P1's accumulator (symmetric race). komi_p2=0.

**Pie rule.** True. Action 730. Verified live: P1 plays 0, P2 plays 730 → P1=0 pieces / P2=1 (P2 takes the opening stone), Next: P1.

**Degeneracy check.**
- **Captures are anti-synergistic (key finding).** Verified live: P1 capturing P2's (1,0,0) left P1 at **+0.000** despite owning two stones — the captured stone's already-deposited negative influence is NOT recomputed away; the engine leaves stale −1 deposits on the capturer's cells. Capturing actively *suppresses your own score*. This makes the capture rule a trap, not a tool.
- Holes reduce neighbor count, so edge columns are nearly capture-proof (≤2 active neighbors can't be outnumbered by 2).
- `adjacent_empty` vestigial. No connection/threshold dispatch confusion (genuinely threshold-race).

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — P1 corner-cube pack vs P2 opposite corner (symmetric race)
Sequence: `0,60,1,61,2,62,9,69,11,71,18,78,19,79,20,80,81,141,83,143,99,159,101,161,...` (P1 fills the origin 3×3×3 menger subcube, P2 mirrors in the (6-8)³ subcube).
Plot: At step 19 (P1's 10th stone) P1 = **+30.000**, P2 = **+27.000** — P1 led the whole way by one tempo. P1 crosses >30 and **wins at step 21 (11 stones)**.
Reflection: The binding constraint is *pure tempo*. Two identical solitaire blob-builds; first mover wins by one move. The decay=1.0 flat kernel makes a dense corner subcube compound at ~+3/stone, so the threshold is reached in ~10 stones — the fastest race in the menger pod.

### Game 2 — Contested corner (P2 co-occupies P1's region)
Sequence: `0,1,2,9,18,11,20,19,81,83,99,101,162,163,164,171,180,173,182,181` (both fight for the origin subcube).
Plot: Repeated captures fire (`(2,1,2)`, `(2,2,2)` cleared). After 20 plies P1 = **+2.000**, P2 = **−3.000** — both accumulators collapsed.
Reflection: Contesting is **mutually destructive**. Co-occupation triggers outnumber captures and stale-negative poisoning that crater both scores. The game-theoretic consequence: rational players do NOT interact — they build separate blobs and let tempo/komi decide. This is the mechanical root of the briefing's strategic_diversity 0.181.

### Game 3 — Pie / seat-swap line
Sequence: `0,730` → P2 swaps, takes the (0,0,0) stone, P1 on move.
Plot: Swap transfers the opening cleanly. But because every corner subcube is interchangeable, P1's opening commits to nothing — P2 gains a stone but the symmetric tempo structure re-establishes immediately.
Reflection: **Pie is weak here.** Pie balances games where the opening is a meaningful commitment; in an "any-corner-equivalent" packing race it merely trades one equivalent opening for another, so the first-mover tempo edge largely survives — consistent with the un-locked komi gate (residual bias 0.060).

### Strategy guides
**P1 (offence):** Open in a corner level-1 subcube (highest internal adjacency → fastest compounding). Pack contiguously; never enter the opponent's region. Win on tempo.
**P2 (defence):** Do NOT contest (self-harm). Build your own corner cube and rely on the swap to claw back P1's one-tempo lead; accept a residual disadvantage at komi 0.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** No. One dominant plan: pack the densest corner subcube. Contesting and capturing are strictly self-harming (Games 2 + degeneracy check). Strategic_diversity 0.181 confirmed subjectively.
**Counter-play.** Effectively absent. The only "counter" (denial via co-occupation) destroys the denier's own score faster than the target's.
**Short-term vs long-term.** Neither — the game is over in ~21 plies before any medium-term plan can develop. No tactical branching beyond "next densest cell."
**Emergent concepts observed.** One, and it is *negative*: capture-poisoning (capturing zeroes your accumulator). The only positive emergent property is "contiguous clustering compounds," which is a direct restatement of the influence rule, not emergence.
**Does menger matter?** Marginally. The corner-subcube high-adjacency packing is a fractal artifact, but the same dynamic exists on any substrate with a dense corner. The other 396 active cells are never used — play collapses to one 20-cell subcube. The 3D sponge is mostly decorative.
**Does the propagation kernel matter?** Yes mechanically (it IS the score) but decay=1.0 makes it *worse*: flat falloff = steeper compounding = faster sprint = less depth. The headline "structurally distinct" decay=1.0 produces a shallower game, not a richer one.
**Capture-rule contribution.** Net negative. Captures fire only under contest and crater both scores. In optimal (non-interacting) play captures never fire.
**First-mover advantage / seat balance.** Real and uncorrected. My symmetric race: P1 led +30 vs +27 throughout and won. komi gate did not lock (bias 0.060); pie is weak (Game 3). Mild but persistent P1 edge.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This is a re-skin of generic area/influence accumulation.
(a) Threshold-race on summed owned-influence ≈ territorial/area-control scoring (Go territory, Reversi disc-count, Tumbleweed influence) with a fixed target.
(b) Capture analog: outnumber-2 → Ataxx/Tafl-style custodial-by-count, but here it is a *liability* (anti-synergistic), so it contributes nothing a player would use.
(c) "outnumber + flat-influence + threshold-race" is just "race to accumulate area." No published game needs the fractal substrate.
(d) Fractal-substrate play exists (menger appeared R10–R20); the hole pattern here only selects which corner to pack — it subtracts more (dead cells, capture-proof edges) than it adds.
(e) Expert-transfer: a Go/Reversi player learns this in <3 minutes ("pack a dense corner fastest, never touch the enemy"). No irreducible new piece.

**Closest known-game analogue:** Tumbleweed / influence-area race — accumulate the larger field to a fixed target. With a self-defeating capture bolt-on.
**Comparison to R8 Connection Go (4.10).** Far thinner. R8's connection-win imposes global-topology planning and a genuine intersection fight; this is a local packing sprint with no interaction.
**Comparison to R19/R20 best.** Thinner than R19 menger top (4.8) and at/below R20 production (3.73). decay=1.0 made it faster, hence shallower, than the R20 decay-0.7 games.

**Novelty score (post-adversary):** **3.0/10.** Above pure re-skin (2) only because the capture-poisoning interaction is an unusual (if undesirable) emergent property. Below 4 because the dominant mechanic is vanilla influence-area accumulation and the substrate is decorative.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** e1453dac5445
**Rules Summary:** Race to pack the densest fractal corner with stones until your summed influence hits 30; whoever moves first usually wins because interacting (capturing/contesting) only hurts you.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** komi gate un-locked (bias 0.060); capture rule anti-synergistic (capturing zeroes your score); `adjacent_empty` vestigial; ~396 of 400 active cells never used.

### Scores (1–10)
- **Strategic Depth: 3.5** — Single dominant plan (pack a corner subcube), ~21-ply games, near-zero branching. The 0.595 engine depth is a metric artifact of clustering, not subjective depth.
- **Emergent Complexity: 3.0** — Only emergent property is negative (capture-poisoning). Clustering-compounds is a restatement of the rule, not emergence.
- **Balance: 4.0** — Residual P1 tempo edge; komi gate didn't lock (0.060); pie weak because opening is non-committal. My symmetric race went to P1.
- **Novelty (post-adversary): 3.0** — Influence-area accumulation re-skin; decay=1.0 makes it shallower, not newer.
- **Replayability: 3.0** — Converges to corner-pack every game; opening choice is interchangeable.
- **Overall "Would an agent team play this again?": 3.4** — Below R8 (4.10) and R20 best (4.80), roughly at/under R20 production (3.73). **GE ranks this #1 of the slate; agent play ranks it near the bottom** — the decay=1.0 "headline new" structure is a faster, thinner sprint. This is the slate's clearest GE-vs-eval disagreement.

### CLOSEST KNOWN-GAME ANALOG
Influence-area race (Tumbleweed-like accumulation to a fixed target) with a self-defeating capture bolt-on; within the corpus, a faster R20 menger threshold-race.

### KILLER FLAWS
- Capture is anti-synergistic — capturing leaves stale enemy influence and zeroes your own accumulator (verified +0.000).
- Counterplay is mutually destructive → play collapses to two non-interacting solitaire builds; diversity 0.181.
- decay=1.0 + threshold 30 = ~10-stone sprint; the game ends before any depth can emerge.

### BEST QUALITY
The only thing lifting it off the floor: the *fast, legible compounding* of contiguous fractal-corner packing makes the race readable — but legibility here equals shallowness.

### MENGER STRUCTURAL CONTRIBUTION
Decorative. Play uses one 20-cell corner subcube; the other ~380 active cells and the 3D sponge geometry never enter optimal play. Flattening to a dense 2D corner would lose almost nothing.

### IMPROVEMENT IDEAS
**Single best change:** Fix the capture engine so clearing a stone also removes its deposited influence (recompute `board_values` on capture). That alone would make captures a usable lever and create real interaction/counterplay.
Secondary:
- Lower decay (back toward 0.5) and/or raise the threshold so the race lasts long enough for interaction to matter.
- Tie influence to capture-resistance so the substrate's high-degree interior is worth fighting over (currently corners dominate and the sponge is wasted).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-4_gamee1453dac5445.md`.*
