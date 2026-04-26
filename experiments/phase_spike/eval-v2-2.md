# Eval-v2-2: 4-Phase Complex Extension of c6bb58075520 — Evaluator-2 (Round 3)

**Evaluator:** evaluator-2 (Claude Opus 4.7, 1M ctx)
**Date:** 2026-04-22
**Subject:** `phase_game_v2.py` — 4-phase complex extension of R16 winner `c6bb58075520`
**Source comparison:** `c6bb58075520` (R16 human winner, scored 4.40/10)
**Angle:** emergent dynamics + quantitative greedy probe (complement to eval-v2-1)

---

## TL;DR

**Score: 3 / 10 vs source (4.40/10). Recommendation: DROP.**

The 4-phase v2 design is mathematically clean — orthogonal E/W stones are *provably* zero-score and N/S-capture-immune, exactly as advertised. But under quantitative test, the orthogonal axis is **strictly dominated at 1-ply lookahead**: across **100 greedy-vs-greedy games (50 deterministic + 50 randomized tie-breaks), neither player ever placed a single E or W stone**. The phases that are supposed to provide novel strategic primitives are dead weight — the 4× action-space inflation buys zero observed strategic content under any policy that values "score now − opponent score now."

This is a stronger finding than the qualitative one in eval-v2-1: it's not just that natural-axis play *usually* wins — it's that even a 1-ply policy with randomized tie-breaks **never sees an E/W move as competitive** in 1,075 placements (561 P1 + 514 P2).

---

## 1. Quantitative greedy probe

Script: `experiments/phase_spike/eval_v2_2_work/greedy_probe.py`
Heuristic: 1-ply lookahead — for each legal action, simulate (with full capture+propagation), compute (own_score − opp_score) AFTER, pick max.

### 1a. Probe 1 — Deterministic tie-breaks (lowest action index)

| Metric | Value |
|---|---|
| Games | 50 |
| P1 wins | **50 (100%)** |
| P2 wins | 0 |
| Draws | 0 |
| Decisive rate | 100% |
| Mean steps | 23.0 (min 23 / max 23) |
| Distinct (winner, steps, p1, p2) signatures | **1** |
| P1 phase use | N=600 (100%), E=0, S=0, W=0 |
| P2 phase use | N=0, E=0, S=550 (100%), W=0 |

All 50 games are bit-identical (P1=24.97, P2=22.14, 23 steps, P1 wins via `P1_threshold`). Greedy converges to one canonical line; the seed has no effect.

### 1b. Probe 2 — Randomized tie-breaks (within ε=1e-9 of best)

| Metric | Value |
|---|---|
| Games | 50 |
| P1 wins | 47 (94%) |
| P2 wins | **3 (6%)** |
| Draws | 0 |
| Decisive rate | 100% |
| Mean steps | 21.5 (min 21 / max 23) |
| Distinct signatures | 14 |
| P1 phase use | N=561 (100%), E=0, S=0, W=0 |
| P2 phase use | N=0, E=0, S=514 (100%), W=0 |

Tie-break randomness yields 3 P2 wins (small first-move-advantage adjustment) and 14 distinct trajectories. **But still 0% E/W placements across 1,075 stones.**

### 1c. Headline finding

> Across 100 greedy games and 1,075 placements, **the orthogonal phases (E, W) were never the score-maximizing 1-ply move for either player**. The "true neutral occupier" primitive does not survive contact with a primitive policy.

---

## 2. Hand-played games

### Game 1 — Standard N-vs-S play (replicates source)

```
moves: 27N,36S,28N,37S,35N,44S,26N,45S,19N,52S,20N,53S,
       18N,51S,11N,60S,12N,61S,10N,59S,13N,62S,21N
```

Final state:
```
. . . . . . . .
. . A^A^A^A^. .
. . A^A^A^A^. .
. . A^A^A^. . .
. . . A^BvBv. .
. . . . BvBv. .
. . . BvBvBv. .
. . . BvBvBvBv.
```

P1=25.443, P2=22.610, 23 steps, P1 wins via `P1_threshold`. **Functionally identical to the source `c6bb58075520`.** When both players play natural phase, the 4-phase engine collapses to the source game.

### Game 2 — Engineered E/W decision points (orthogonal axis stress-test)

I constructed five micro-positions to test whether E/W ever changes optimal play.

**2a. P2 places E in own cluster (cell 52, after 9-move N/S exchange).**
- P2 plays 52E → score 6.580 → 7.056 (+0.476 from cell-vec ownership only)
- P2 plays 52S instead → score 6.580 → 8.463 (+1.88 — full natural-axis gain)
- **N beats E by +1.40** in own territory (the missing 0.93 is the self-contribution; the missing 0.47 is decay-decayed extra reach).

**2b. P2 places E in P1 territory (cell 26, after 5-move opening).**
- P2 plays 26E → score 2.340 → 1.389 (P2 LOSES 0.95 — owning a +x cell as P2 reads negative)
- P2 plays 27S anywhere natural → +1.88
- **E in enemy territory is a net negative for P2** by ≥2.8 score.

**2c. Capture-save via E.** Position: P2's stone at 36 has 2 N neighbours (28, 35), needs only one more to be captured.
- If 36 is S: when P1 plays 37N, cell 36 captured (P1 +1.88 from new stone, P2 +0.018 net since 36 was a liability).
- If 36 had been played as E originally: capture-immune (cos(180°−90°)=0), P2 score = 2.797 — but compared to "36S then captured" P2 = 4.222. **E saves the stone but at a 1.4 score cost** because the E-cell's +x field (from surrounding N stones) reads negative for P2 owner.
- Conclusion: **even capture immunity doesn't pay** — the ownership penalty exceeds the saved stone's value.

**2d. Pure E-vs-W "secondary axis" game.**
```
moves: 27E,36W,28E,37W,35E,44W,26E,45W
```
After 8 moves: P1=0.000, P2=0.000. **Sterile.** Neither player can score with only E/W. Game would proceed to 100-turn majority count — purely Go-like piece counting with no actual conflict resolution on the score axis.

**2e. E-vs-W mutual capture.**
```
moves: 27E,28W,26W,35W
```
Move 4 captures cell 27 (E with 3 W neighbors → -cos(90°−270°)·3 = +3 > 2). Capture works as designed but the entire interaction is **score-irrelevant** because neither player accumulates.

### Hypothesis tests

> **H1:** Can a player use E stones to block an enemy connection without enabling enemy score?

**Partial yes, but at high cost.** E does block (cell occupancy denies that placement to the enemy) and is capture-immune from N/S. But the player who places E pays:
- 0 self-contribution (vs +0.93 for natural N/S)
- +1.4 to +1.9 ownership penalty when placing E in enemy territory (cell-vec from enemy stones reads opposite to placer's score axis)

**The denial value of E (≤ 0.5–0.95 worth of denied enemy score) never exceeds the opportunity cost (1.4–1.9) of skipping a natural extension.** Verdict: H1 is technically true (the block exists) but strategically irrelevant.

> **H2:** Does E-vs-W secondary axis produce real conflict, or is it sterile?

**Sterile.** Pure E-vs-W games freeze both scores at 0.000. Mutual capture exists but produces no winning condition. Any player who defects to N/S immediately wins the score race. There is no Nash equilibrium where both players use E/W in mutual blocking — defection always pays.

---

## 3. Phase usage breakdown (across 100 greedy games)

| Player | N | E | S | W | Total |
|---|---|---|---|---|---|
| P1 | **1161 (100%)** | 0 | 0 | 0 | 1161 |
| P2 | 0 | 0 | **1064 (100%)** | 0 | 1064 |

**E and W combined: 0 placements out of 2225.** This is the cleanest possible falsification of the v2 design hypothesis ("orthogonal phases will see use in equilibrium").

For comparison: in random play (eval-v2-1, §3), E/W are placed ~50% of the time and games stall at threshold. The contrast between random (over-uses E/W and draws at 100 turns) and greedy (never uses E/W and finishes at step 21–23) reveals that the v2 mechanic pays only when the policy is too weak to recognize that natural-axis play strictly dominates.

---

## 4. Comparison to source `c6bb58075520` (4.40/10)

| Dimension | Source `c6bb58075520` | v2 (this eval) |
|---|---|---|
| Action space | 65 (64 cells + pass) | 257 (4× phase choice) |
| Greedy phase usage | binary single-stone choice | **0% E/W in 100 greedy games** |
| Greedy game length | ~23 steps | 21–23 steps (identical) |
| P1 win rate (greedy) | not directly comparable | 100% determ / 94% randomized |
| Distinct greedy games | 1 (deterministic) | 1 (deterministic) / 14 (random tie-break) |
| Hand-played feel | clean threshold race | **identical** when natural phase used |
| New strategic content | — | none observed in greedy / 5 hand-engineered positions |

**Net delta vs source: zero observed strategic content + 4× larger action space.** The action-space inflation is pure noise — 75% of legal actions (E/W placements) are dominated under any rational evaluator.

For a learning agent (PPO/MCTS), this likely manifests as wasted exploration: the policy must learn that 75% of legal moves are bad before it can play the source game's already-known optimal line. Action-space inflation without compensating depth is a **regression** for self-play training.

---

## 5. Score: **3 / 10 vs source (4.40)**

| Dimension | Score | Note |
|---|---|---|
| Mathematical correctness | 9 | Engine flawless. Orthogonality, capture immunity, E-vs-W capture all verified. |
| Adds genuine strategic novelty | **1** | 0% E/W use in 100 greedy games + 1,075 placements; no hand-played position favored E/W |
| Symmetry / fairness | 7 | P1 50/50 wins (determ), 47/3 (randomized) — small first-move edge, much better than v1 |
| Action-space utilization | **1** | 75% of action space (E/W) never used by greedy |
| Game-length / pace | 5 | Same as source (21–23 steps) |
| Replayability / decision diversity | 3 | 14 distinct greedy games out of 50 (random tie-breaks); all functionally same shape |
| Emergent dynamics | **1** | None — secondary axis is sterile (E-vs-W = score 0); orthogonal denial is strictly dominated |

Aggregate: **3 / 10**. Worse than source (4.40) because the source is a clean threshold race; v2 is the same threshold race plus a 4× inflated action space of dominated phantom moves.

(Note: eval-v2-1 scored 4/10 leaning on the engine correctness and the *theoretical* presence of orthogonality. My quantitative greedy result — 0/2225 E/W placements — argues for the lower mark: the orthogonal mechanic is not just suboptimal, it's invisible to any policy with a forward-looking evaluator.)

---

## 6. Recommendation: **DROP**

The v2 design has cleaner mathematics than v1 (true orthogonality, no sign bug), but its strategic surface is identical to the source under any non-trivial policy. Going forward into the evolutionary engine:

- Source `c6bb58075520` is a known 4.40/10 game.
- v2 = source + 4× action-space inflation with 0% utilization of the new dimensions.
- For self-play training, this is strictly harmful (more bad actions to prune).

If the design intent must be salvaged, two paths could conceivably make E/W live in equilibrium:

**Option A — Pay E/W bearer for denial.** Award score for E/W stones that *block* an enemy cluster from connecting (graph-theoretic denial bounty). This converts the orthogonal axis from "free occupier" into "negative-score occupier with a structural reward." Risk: hard to define cleanly; introduces a graph rule the source doesn't have.

**Option B — Reduce the ownership penalty for orthogonal stones.** If `score_p1 = Σ over P1 cells of max(0, dot(cell_vec, target))` (i.e., never penalize ownership of cells with hostile field), then E in enemy territory becomes free denial without negative cost. But this likely breaks the score-race tension elsewhere.

**Option C — Drop the spike entirely.** Most likely correct. The phase-extension family across Rounds 1–3 has not produced a game that beats the source on any dimension. The frontier worth exploring is unlikely to be "more axes of phase."

---

## 7. Files

- Engine: `/Users/jamesbrowne/aigame/experiments/phase_spike/phase_game_v2.py` — verified correct
- Helper CLI: `/Users/jamesbrowne/aigame/experiments/phase_spike/phase_play_helper_v2.py`
- Greedy probe script: `/Users/jamesbrowne/aigame/experiments/phase_spike/eval_v2_2_work/greedy_probe.py`
- Probe raw output: `/tmp/greedy_probe_out.txt` (preserved here in §1)
- Source reference: `genesis_v2_run16.db` row `c6bb58075520`
- Companion evals: `eval-v2-1.md` (qualitative, scored 4/10), `eval-1.md` & `eval-2.md` (v1 round)
