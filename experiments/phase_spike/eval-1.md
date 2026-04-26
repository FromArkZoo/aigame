# Phase-Extended c6bb58075520 — Evaluator-1 Report

**Evaluator:** evaluator-1 (Claude Opus 4.7, 1M ctx)
**Date:** 2026-04-22
**Spike:** Phase-1 — phase-extended stone mechanics layered onto R16 winner `c6bb58075520`

---

## TL;DR

Aggregate score: **3 / 10**. Recommendation: **REFINE THE DESIGN BEFORE INTEGRATION** — and almost certainly fix what looks like a sign error in P2's score formula first. As implemented, the phase extension does add a modest layer of tactical choice (camouflage, phase-based capture) on top of the source rules, but the asymmetric scoring makes the game essentially unwinnable for P2 in any natural line, which collapses the strategic surface to "P1 builds a + cluster and optionally drops camo stones into P2 territory for free score." That is not richer than the source — it is the source plus an exploit.

---

## Game Logs

All three games played from the standard opening cell 27 (3,3) for P1 and 36 (4,4) for P2 (R16 source-style). Each row shows post-move scores. P1 win threshold is 22.6453.

### Game 1 — Standard non-camouflage play (P1 wins, step 23)

**Moves (full sequence):**
```
27+,36-,28+,37-,35+,44-,26+,45-,19+,52-,20+,53-,
18+,51-,11+,60-,12+,61-,10+,59-,13+,62-,21+
```

Both players build a connected mono-phase cluster in opposite corners of the torus. Symmetric play; no captures. Final position:
```
. . . . . . . .
. . A A A A . .
. . A A A A . .
. . A A A . . .
. . . A B B . .
. . . . B B . .
. . . B B B . .
. . . B B B B .
```
Final scores: P1 = 25.443, P2 = -22.610. P1 crosses threshold on move 23.

**Strategic feel:** identical to the source game's strategic feel — mono-phase cluster building. The phase choice is irrelevant when both players just play their "natural" phase.

### Game 2 — Deliberate camouflage experimentation (P1 wins, step 23)

**Moves:**
```
27+,36-,28+,37-,35+,44-,26+,45-,19+,52-,20+,53-,
18+,51-,11+,60-,12+,61-,10+,59-,46-,62-,38-
```

Identical opening to Game 1 through move 20. On move 21, P1 deviates with a CAMOUFLAGE play at cell 46 (P1@-1, "a") inside P2's -1 cluster. Then move 23 plays another camo at cell 38.

Camo stone 46 has one same-phase neighbor (45 = B, -1) and three empty neighbors: same=1, opp=0, safe from capture. Its cell_value ≈ -1.405. Because P1 score formula is `cell_val × phase`, the camo (phase=-1) contributes `-1.405 × -1 = +1.405` to P1's score — slightly BETTER than a natural isolated +1 stone (+0.93).

Final position:
```
. . . . . . . .
. . A A A . . .
. . A A A . . .
. . A A A . . .
. . . A B B a .
. . . . B B a .
. . . B B B . .
. . . B B B B .
```
Final scores: P1 = 24.493, P2 = -23.561. P1 wins on move 23 with 2 camo stones.

**Did camouflage pay off?** YES — clearly. Each camo stone added ~+1.4 to P1 and made P2's negative score worse (more negative) by reinforcing the local -1 field. Two camo stones bought P1 ~2.4 points without the surface-area cost of building a connected cluster. Once P2 has built a cluster, P1's marginal natural stone is worth maybe +1.9 (3 same-phase neighbors), but it has to be PLACED next to existing P1 stones — so the question is opportunity cost. Camo wins on flexibility, not raw delta.

The interesting tension I expected — "camo gives you territory but costs you score" — does not actually exist with this scoring. Camo is ALWAYS positive when placed next to same-phase (enemy) stones, because it harvests the negative cell_val that already exists.

### Game 3 — Balanced both-phases play (P1 wins, step 21)

**Moves:**
```
27+,36-,29+,38-,19+,30+,21+,46-,20+,45-,28+,37-,
12+,44-,11+,53-,13+,54-,55-,52-,47-
```

P1 builds a 3x3 cluster but mixes in two camo stones at the END (55-, 47-) once P2's -1 cluster is established. P2 even uses a camo of their own (30+ as "b") on move 6 — this turned out to be a NET COST for P2 (cell 30 had +0.93 cell_val × -phase = -0.93 contribution to P2).

Final position:
```
. . . . . . . .
. . . A A A . .
. . . A A A . .
. . . A A A b .
. . . . B B B .
. . . . B B B a
. . . . B B B a
. . . . . . . .
```
Final scores: P1 = 23.085, P2 = -20.252. **P1 wins in 21 moves — FASTER than pure-natural Game 1 (23 moves).** Mixed-phase strategy is strictly better.

---

## Strategic Observations

### 1. P2 cannot win — likely a sign error

The most important observation: under this engine, P2 cannot reach the win threshold in any normal line of play. The score formula at `phase_game.py:187` is

```python
total += cell_val * (-phase)   # for P2
```

For a P2 natural stone (P2@-1) in a -1 cluster, `cell_val` is strongly negative and `-phase = +1`, giving a strongly NEGATIVE contribution to P2's score. Both random play (`--action random-game --seed 42` produced P2 = -30.892) and every game I played show P2's score drifting more negative the more P2 plays. There is no placement that consistently grows P2's score upward, since:

- P2@-1 in -1 territory: `(neg) × (+1) = neg` (every natural stone hurts P2)
- P2@-1 in +1 territory: `(pos) × (+1) = pos`, but the stone gets captured (3+ opp neighbors)
- P2@+1 (camo) in +1 territory: `(pos) × (-1) = neg`
- P2@+1 (camo) in -1 territory: `(neg) × (-1) = pos`, but again capture risk

The threshold check uses `score_p2 > WIN_THRESHOLD`, so P2 needs to climb to +22.65 — practically unreachable. **This is the dominant finding.** It means every game devolves to "P1 races to +22.65 unopposed."

If the intended formula was `cell_val * phase` for both players (mirrored ownership accounting), or the threshold check was `abs(score) > threshold`, the asymmetry would disappear and the camo dynamics would actually have to be defended.

### 2. Camouflage is a free lunch for P1, dead weight for P2

With the current engine, P1 camo (P1@-1) placed adjacent to ANY -1 stone gives a positive contribution to P1's score AND degrades P2's score further. There is no scenario where a P1 camo stone next to one or more same-phase neighbors hurts P1 — only over-extension into a +1 cluster gets it captured (Game 3 capture-test: 27a captured by 19+,28+,35+).

P2 camo (P2@+1) is the opposite: it sits in a +1 (P1) area and contributes `cell_val × -phase = (pos) × (-1) = neg`. It actively hurts P2. The only reason to play it would be capture or blocking, but on a 64-cell board with 100-turn limit, blocking is rarely valuable.

The "tension" the rules text describes — camo as a NET COST — appears to be the design intent, but the math doesn't bear it out for P1. **The intended dual-edged dynamic is broken.**

### 3. Capture works as designed

The phase-based outnumber capture (`opp > same + 2`) does fire (verified at move 4 of an unscripted test: P2 camo b@36 captured by P1 stones at 19,28,35). The capture rule is OWNER-AGNOSTIC, which is the genuinely novel part of the design. In principle this means a P2 camo could be captured by P2's own natural stones (if a P2@+1 sat next to 3 P2@-1 stones), but I did not engineer such a position because both sides have strict score incentives to avoid them.

### 4. Total game length is unchanged

All three games finished in 21–23 placements vs the source's typical 20–30. The phase extension does not lengthen play meaningfully; it adds 1-2 strategic spice moves at the end.

### 5. Comparison to the source `c6bb58075520`

The source scored 4.40/10 in R16 human eval. Source strategic depth: 0.76; non_triviality: 1.0; strategic_diversity: 1.0. The source is a clean, symmetric, threshold-race game where placement choice and capture pressure interact.

The phase extension adds:
- **+** Per-move phase choice (2x action space, mostly trivial)
- **+** The camo idea: a stone that survives in enemy territory at score cost
- **+** Owner-agnostic capture (interesting in theory)
- **−** A scoring asymmetry that makes P2 unwinnable
- **−** The "cost" of camo is missing — for P1 it is currently a free score boost
- **−** Most positions admit a clean P1 win regardless of phase choice

**Verdict: this does not feel like a richer game than the source.** It feels like the source plus a one-sided exploit.

---

## Aggregate Score: 3 / 10

| Dimension | Score | Note |
|---|---|---|
| Adds genuine strategic novelty over source | 4 | camo is a real concept, but math doesn't enforce its cost |
| Symmetry / fairness | 1 | P2 can't win in normal play |
| Capture mechanics interesting | 6 | phase-based, owner-agnostic — solid idea |
| Action-space utilization | 3 | most phase choices are dominated |
| Game-length / pace | 5 | similar to source, no improvement or harm |
| Replayability / diverse positions | 3 | converges to same P1-cluster + camo-tap pattern |

Overall: **3 / 10**.

---

## Recommendation: REFINE THE DESIGN

Do not integrate to the full evolutionary engine in current state. Two paths forward:

### Option A: Fix the scoring (minimal change, retain spec intent)

Audit `player_score`. If the design intent is "each player wants their natural-phase stones in their natural-phase territory," then for P2 the formula should plausibly be:

```python
total += cell_val * phase * (-1)   # invert the cell_val sign for P2
```
i.e. P2's score should grow as their cluster of -1 stones thickens (`cell_val` becomes very negative, multiplied by -1 yields positive). With that change, both players race to +22.65 symmetrically and camo retains its intended cost (placing P1@-1 means -cell_val flipped is positive only when cell_val is negative i.e. enemy cluster, but it also FAILS to count toward P1's positive +1-cluster score, so opportunity cost reappears).

After fixing, re-run this eval. If both players can win in symmetric play, then judge whether the camo/capture dynamic adds depth.

### Option B: Drop camouflage, keep phase choice as a tactical capture tool

If after a fix the game still feels flat, simplify: still let each player choose phase per placement, but have score = sum of cell_val regardless of phase, and use phase only for capture interactions (so a P1 player might place a -1 stone purely to capture a P2 stone). This collapses the score-formula complexity and isolates the genuine novelty (phase capture).

### Option C: Drop entirely

If after Option A or B the game still feels like "source + cosmetic," drop the spike. The source is already a 4.40/10 game; the extension as-tested is closer to 3.

---

## Engineering notes for future evaluators

- The play helper is fine; engine-verified each move. Recommend adding a `--from-position` flag so an evaluator does not have to replay the whole sequence on each command (the helper currently re-applies the entire move list each call). For long games this gets slow.
- A `--show-cell-values` debug flag (printing `values[]` next to the board) would massively help reasoning about placement value.
- Add an assertion in `player_score` that catches the case where both players' natural play drives one of them strictly negative — would have flagged the suspected bug early.

## Files referenced

- `/Users/jamesbrowne/aigame/experiments/phase_spike/phase_game.py` — engine (suspected sign bug at line 187)
- `/Users/jamesbrowne/aigame/experiments/phase_spike/phase_play_helper.py` — CLI (works as designed)
- `/Users/jamesbrowne/aigame/genesis_v2_run16.db` — R16 db, source game `c6bb58075520`
