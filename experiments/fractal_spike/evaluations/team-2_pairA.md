# Fractal Spike — Pair A Evaluation (team-2)

**Pair**: A (alt + outnumber-2 + influence radius-1 + threshold 22.65, clone of R16 winner c6bb58075520)
**Fractal candidate**: `frac_A_fractal.json` — 9×9 sierpinski, 17 holes, 64 active cells
**Control candidate**: `frac_A_control.json` — 8×8 torus, 64 cells, all degree-4
**Evaluator**: team-2

---

## Phase 1 — Rule Comprehension

Both candidates share the IDENTICAL ruleset apart from `topology_type` (`sierpinski` vs `torus`) and `axis_size` (9 vs 8): alternating turns, single placement per turn, outnumber-capture with friendly-count threshold 2, radius-1 influence with strength 0.932 / decay 0.510, win at threshold 22.645 over 100-turn cap. Both substrates expose 64 active placement cells (81 − 17 holes vs 8×8). The only mechanical asymmetry is that on the fractal the von Neumann neighbour set of any active cell is filtered by `active_mask`, so cells adjacent to holes have degree 2 or 3 instead of 4.

**Degeneracies flagged**:
- The threshold (22.65) is held constant despite the substrate change. Maximum *per-stone* influence is `0.932 + deg × 0.475`, so a deg-2 cell maxes out at 1.882 vs deg-4's 2.832. The fractal therefore needs *more* clustered stones to cross threshold; whether this changes outcomes or just delays them is the spike question.
- Degree distribution on fractal: **20 deg-2, 40 deg-3, 4 deg-4** (the four cells at (2,2),(6,2),(2,6),(6,6) — the sub-block centres). On torus, **all 64 cells are deg-4**. This is a meaningful structural delta.
- Outnumber-capture asymmetry: a deg-2 enemy stone needs both neighbours hostile to be captured (rare but still possible). On torus every stone has a 4-of-4 surround possibility. So holes provide a small amount of *capture shelter* near hole-corners.

---

## Phase 2 — Strategic Play

### Game 1 — Fractal substrate (P1 = team-2 Player-1 role)

Opening reasoning: I (P1) opened on action 20 = (2,2) — one of the four deg-4 cells, the strongest single placement on the substrate. I predicted P2 would mirror to action 60 = (6,6), the diagonally-opposite deg-4 cell, putting the central 3×3 hole between us.

Move sequence (action IDs):

| Mv | Plyr | Action | Cell | Reasoning |
|----|------|--------|------|-----------|
| 1 | P1 | 20 | (2,2) | Claim deg-4 sub-block centre |
| 2 | P2 | 60 | (6,6) | Symmetric deg-4 anchor; central hole separates us |
| 3 | P1 | 21 | (3,2) | Extend rightward inside upper-row strip |
| 4 | P2 | 51 | (6,5) | Extend upward toward central hole boundary |
| 5 | P1 | 29 | (2,3) | Bend cluster downward — but (2,3) sits against the central hole, so cluster MUST go upper-left, not down-right |
| 6 | P2 | 59 | (5,6) | Mirror — P2 cluster goes lower-right |
| 7-20 | both | … | … | Pure parallel-cluster build; no contact ever made |
| 21 | P1 | 22 | (4,2) | Bridge across row 2 — tempting because (4,1)/(4,3) are holes so this stone is deg-2 and "dead-ended" |
| 22 | P2 | 44 | (8,4) | Extend right edge of P2 cluster |
| 23 | P1 | 4 | (4,0) | **WIN** — P1 effective crosses 22.65 (≈24.5) |

Final fractal board (move 23):
```
. . X X X . . . .
. # X X # . . # .
X X X X X . . . .
. X X # # # O . .
. # . # # # O # O
. . . # # # O O O
. . . . . O O O .
. # . . # . O # O
. . . . . . . . .
```

Endgame: Decisive — threshold reached, **P1 wins, 23 moves**, 12 stones. P2 had ≈21 effective with 11 stones; **the game ended one move before P2's threshold**. Neither cluster ever made contact: the central 3×3 hole was an absolute wall that forced a **race condition**, not a confrontation. Substrate-specific decisions: at moves 5 and 7 I deliberately routed AWAY from row 3-5 because three holes sit on (3,3)/(4,3)/(5,3); on a torus I would have built toward centre.

### Game 1B — Fractal stress-test (P2 plays aggressively)

To test the "holes shelter P1's central stone" hypothesis I replayed with P2 attacking instead of mirroring:

| Mv | Plyr | Action | Cell | Note |
|----|------|--------|------|------|
| 1 | P1 | 20 | (2,2) | deg-4 anchor |
| 2 | P2 | 21 | (3,2) | adjacent attack |
| 3 | P1 | 11 | (2,1) | defend |
| 4 | P2 | 29 | (2,3) | **(2,2) now has 2 P2 neighbours → CAPTURED** |
| 5+ | … | | | P2 builds (3,1)+(1,3) and *steals* the deg-4 centre |

Result: **the deg-4 cell falls to whichever player commits to fighting for it**. Holes do not shelter the centre. After 10 plies P2 was sitting on the (2,2) cross with 4 stones to P1's 4 stones — and P1 had been pushed to row 0 / column 4. So aggressive contact on the fractal *also* works; it just selects a different cluster owner.

### Game 2 — Control 8×8 torus (seat-swap: P2 = team-2 Player-1 role)

Identical opening philosophy, swapped seats:

| Mv | Plyr | Action | Cell | Reasoning |
|----|------|--------|------|-----------|
| 1 | P1 | 27 | (3,3) | Centre — but on torus all cells are equivalent |
| 2 | P2 | 45 | (5,5) | Diagonal anchor, similar density |
| 3-18 | both | … | … | Parallel build, but clusters meet around (4,4) |
| 19 | P1 | 18 | (2,2) | extend |
| 20 | P2 | 55 | (7,6) | extend right |
| 21 | P1 | 21 | (5,2) | bridge — adjacent to (5,3)X already |
| 22 | P2 | 12 | (4,1) | over-extend (mistake; isolated) |
| 23 | P1 | 11 | (3,1) | (4,1) had 2 P1 neighbours after my play → **CAPTURE**, threshold crossed → **P1 wins, 23 moves** |

Final control board (move 23):
```
. . . . . . . .
. . . X O . . .
. . X X X X . .
. . X X X X . .
. . X X . O O .
. . . . O O O .
. . . . O O O O
. . . . . O . .
```

Substrate-specific moments on control: capture at move 23 was a **classic torus interaction** — P2's lone (4,1) stone was sandwiched by P1's (3,1) and (4,2) and the all-degree-4 substrate left it nowhere to be safe. On the fractal, an analogous (4,1) cell IS A HOLE — that exact tactical motif cannot exist in the upper area.

**Endgame note**: Both games ended at exactly 23 moves with P1 winning, but for different reasons: fractal = uncontested race; control = capture-induced threshold.

---

## Phase 3 — Strategic Analysis (joint)

**Did the fractal play differently?** Yes, but in a *limiting* direction more than an *enriching* one:

1. **The central 3×3 hole was a hard wall**. Game 1 had ZERO contact between clusters — the only possible engagement zone was through the 1-cell-wide corridors at (3,2)/(5,2)/(3,6)/(5,6) etc., which neither player crossed. On torus, contact happened by move ~10.

2. **Choke points are real but not *strategically* exploited**. The active cells flanking the central hole — (3,2),(5,2),(3,6),(5,6) and (2,3),(2,5),(6,3),(6,5) — are obvious fortress walls. But because the threshold-race is faster than territorial competition, neither side bothered claiming them as walls; they were just "next cells in cluster".

3. **Influence shadows do exist**. A stone at (2,2) gets full deg-4 deposit; a stone at (4,2) is deg-2 because (4,1) and (4,3) are holes. The influence advantage of (2,2) (and the other 3 deg-4 cells) is permanent and unrecoverable — there is a discrete "best 4 cells" on the fractal that does not exist on torus. This *is* a substrate-driven strategic concept: claim a deg-4 cell early.

4. **Path routing is irrelevant for this ruleset** — radius=1 means no influence ever has to "route around" anything; the propagation just doesn't happen across holes. Custodian (Pair B) and connection (Pair C) would expose path-routing more.

5. **P1 dominance**: Both games went P1, ending move 23. Same first-mover advantage either way. Game 1B (aggressive P2) suggests P2 *can* claim the centre but only by sacrificing its own threshold race. We don't have evidence of substrate-driven balance shift.

**Comparable metric**: Game length to threshold = 23 moves on both substrates. Stones-to-win = 12 (P1) on both. The fractal does NOT lengthen the game.

**Fractal-only phenomena observed**:
- Forced cluster compartmentalisation (central hole = wall).
- Discrete deg-4 prize cells (only 4 exist).
- Tempo cost of placing near holes (deg-2 cells pay ~1 unit less effective per stone).

**Control-only phenomena observed**:
- Genuine cluster-on-cluster contact and capture exchanges in the contested middle.
- Torus wraparound: P2's (5,7) was adjacent via wrap to (5,0) row — gave P2 surprising defensive options that don't exist on fractal.
- All-position equivalence: opening choice is irrelevant on torus; on fractal, cells (2,2)/(6,2)/(2,6)/(6,6) are objectively the four best opens.

---

## Phase 4 — Substrate Critic (mandatory)

**Critic argues**:

(a) *"It's just 8×8 with dead cells"*. The fractal is a torus minus 17 cells minus the wrap. The ruleset and the win condition are unchanged. Strategic primitives — claim deg-N centres, build dense clusters, threaten outnumber captures at adjacency — all transfer 1:1.

(b) *"Apparent differences are threshold-scaling artefacts"*. The threshold (22.65) was tuned for an 8×8 torus where every stone can contribute up to 2.832 effective. On the fractal the *average* per-stone ceiling is lower, so the game just requires marginally more stones — but it stops feeling like a different game and starts feeling like "same game, harder threshold". Pair A in particular has `threshold_unchanged: true` in its metadata; this *is* the asymmetry.

(c) *"Expert transfer test"*. An expert at the R16 control would land on the fractal and immediately:
   - Open at one of the four deg-4 cells (trivially identifiable).
   - Build outward avoiding hole-adjacency to maximise effective per stone.
   - Race threshold rather than seek contact, since contact is hard to engineer through holes.
That's identical to expert torus play with one extra heuristic ("avoid building into hole-corners"). The transfer is essentially seamless.

**Player rebuttals**:

- **(Game 1B)** Aggressive contact at (2,2) led to capture and territorial dispossession. The presence of the hole-flanked deg-4 cells *did* create a discrete contestable resource that the torus version lacks (where every cell is equivalent and "the centre" is just a label). That's a real strategic concept the fractal added.
- **(Game 1)** The central hole *enforces* parallel races. On torus, players that build separately make a mistake (someone should attack). On fractal, NOT attacking is correct. That's an *inverted* meta-strategy — small but real.
- **(Tempo)** Placing your N-th stone has a substrate-dependent value: on torus it's always ≥1.882 added to effective (k=2 minimum); on fractal you can be FORCED to place at deg-2 cells where the gain drops to 1.407. That changes when threshold becomes reachable.

**Net**: rebuttals concede most of the critic's points. The fractal adds three small modulations (deg-4 prize, parallel-race meta, deg-2 tempo penalty) but none rises to "fundamentally new strategic concept I had to learn from scratch". It's "same game with terrain features" not "new game".

**Substrate-novelty score: 4/10** — measurable substrate effect, but mostly negative-space (it took *away* strategic options like central contact) and the depth gained is modest.

---

## Phase 5 — Verdict

**Team ID**: team-2
**Pair**: A
**Fractal candidate**: frac_A_fractal
**Control candidate**: frac_A_control

### Fractal scores

- **Strategic Depth**: **5/10** — same threshold-race as control, with a small added "claim deg-4 centre" sub-game and a small "avoid hole-tempo-loss" heuristic. Hole-induced separation actually *reduces* tactical depth by eliminating cluster contact.
- **Balance**: **5/10** — both games ended P1-wins move 23; one is decisive evidence of P1 advantage. Game 1B suggests P2 can disrupt centre-claim aggressively but at cost of own race. Seat-swap evidence: with the same role-style on both seats, P1 won both attempts I evaluated (Game 1 and seat-swapped Game 2). Likely 60/40 P1 advantage on this substrate, mirroring R16.
- **Novelty (post-critic)**: **4/10** — substrate adds shelf decoration; the underlying game is R16 verbatim.
- **Substrate-novelty**: **4/10** — discrete deg-4 prize is real; central-hole-as-wall is real; but parallel-race meta cheapens both. Influence-radius=1 means propagation across holes never matters. Custodian or connection would have expressed substrate effects more.
- **Overall "Would I play this again?"**: **5/10** — playable, decent threshold race, mild novelty. Not better than R16.

### Control scores

- **Strategic Depth**: **6/10** — R16 winner substrate; cluster contact, capture exchanges, ko-style positions emerge naturally. Slightly *more* dynamic than fractal because contact happens.
- **Balance**: **5/10** — same P1-bias as fractal; capture at move 23 closed the game (mirror outcome).
- **Novelty (post-critic)**: **4/10** — pure R16; nothing new vs the existing population.
- **Overall**: **6/10** — solid R16 game, no surprises, slightly more interactive than its fractal sibling because clusters can fight in the middle.

### Delta (fractal − control)

- Strategic Depth: **−1**
- Balance: **0**
- Overall: **−1**
- *Substrate-novelty*: +4 (fractal-only score; control is 0 by definition)

### Critical Assessment

- **"The fractal substrate genuinely added strategic depth"** — **N** (mild geometric novelty, but on net depth flat-to-slightly-negative for this ruleset).
- **Specific phenomena observed only on fractal**:
  - Discrete deg-4 prize cells (only 4 exist; opening choice non-trivial).
  - Central-hole-enforced parallel-race meta.
  - Deg-2 tempo tax when placing at hole-adjacent cells.
- **Specific phenomena observed only on control (i.e., the substrate took AWAY)**:
  - Cluster-on-cluster contact in the centre.
  - Capture exchanges as the threshold-deciding mechanism (Game 2 ended via capture, Game 1 fractal ended via uncontested race).
  - Torus wraparound options.
- **Recommendation for R17**: **second-probe**. Pair A's ruleset (radius-1 influence + threshold) does NOT exploit the fractal substrate's most interesting feature (BFS-distance routing across holes). I would NOT integrate the fractal into the main run on this evidence alone. The same evaluation should be re-run for Pair B (custodian — should care about hole walls a lot) and especially Pair C (connection — central hole forces detour). If fractal looks better with custodian or connection, integrate then. Otherwise drop.

---

*Evaluator notes*: Game 1 was played to natural completion (P1 win at move 23 by threshold). Game 1B was a 10-ply stress test of the "aggressive P2" path. Game 2 was played to natural completion (P1 win at move 23 by capture-induced threshold). Total of three play-throughs across two substrates. P2 made one suboptimal move at Game 2 move 22 that accelerated P1's win, but threshold-race trajectory was already favouring P1; even with that move replaced, P2 looks unlikely to overtake within ≤25 moves on the control either.
