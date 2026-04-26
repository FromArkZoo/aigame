# Eval-v2-1: 4-Phase Complex Extension of c6bb58075520 (Round 3)

**Evaluator:** evaluator-1
**Source comparator:** `c6bb58075520` (R16 human winner, mean 4.40/10)
**Engine:** `experiments/phase_spike/phase_game_v2.py` (4-phase complex; N/E/S/W on unit circle)
**Time budget:** ~45 min

---

## TL;DR

The 4-phase complex redesign achieves what Round 1+2 binary {+1,-1} could not: it produces a **mathematically real** "neutral occupier" primitive. E and W stones are genuinely orthogonal to the N/S score axis (cos(90°)=0) AND capture-immune to N/S attackers. I verified both properties on the engine.

**However, the strategic value of E/W stones in skilled play is essentially zero.** The denial value of an E-stone (preventing the enemy from filling that cell with their natural S/N stone) is consistently dominated by the opportunity cost of the missed natural N/S extension. Across every position I constructed — including the "ideal" E-denial fortress (Game 2's 4-S-ringed cell 37) — playing the natural N is at least as good as playing E, and usually better.

The game collapses to source-game-equivalent play under skilled strategy: both players play their natural phase only. Random play breaks the threshold race because ~50% of moves are "wasted" on E/W → 48/50 random games are draws (vs source's natural balance). Natural-only random play returns to near-source statistics (P1=29, P2=21, 41 steps avg).

**Score: 4 / 10 vs source (4.40/10).** Same as postfix-A. The 4-phase axis adds richer mathematical structure (true orthogonality) but the same strategic conclusion: the orthogonal axis is dominated under any rational scoring strategy. Search-space inflation (257 actions vs source 65) without compensating decision depth.

**Recommendation: refine more (or drop).** Current v2 has the same fundamental design pathology as v1: orthogonal phases create a real but dominated action axis. Path forward needs to either cap E/W cost lower OR add a non-score reward for E/W presence (territory, capture multiplier, etc.) to make the axis live in equilibrium.

---

## 1. Engine verification

Confirmed properties hand-on-engine:
- **E/W = 0 score contribution from self-radiation:** Verified via Game 3B — pure E-vs-W game, both scores stuck at 0.000 for 12+ moves.
- **E capture-immune to N/S:** Game 2D, P1 plays 37E surrounded by 4 P2@S → stone survives. Same position with 37N → stone captured immediately (Game 2 baseline `…,37N`).
- **E-vs-W mutual capture works:** Game 3B move 11 — P1 plays 37E with 3 W-nbrs, captured immediately. cos(π/2 - 3π/2) = -1 → +1 per W-nbr × 3 > threshold 2.
- **N/S do not capture E/W and vice versa:** Verified via Game 3B and Game 2D survival.
- **Score truly orthogonal:** P1 plays 37E in Game 2D — P2 score unchanged from move 16→17 (15.061 → 15.061).

---

## 2. Game 1: pure N-vs-S baseline

```
27N,36S,28N,35S,29N,37S,26N,44S,25N,43S,30N,42S,33N,38S,18N,46S,17N,53S,19N,54S,11N,55S,12N,52S,20N
```

Final state at step 25:
```
0 |  .  .  .  .  .  .  .  .
1 |  .  .  .  A^ A^ .  .  .
2 |  .  A^ A^ A^ A^ .  .  .
3 |  .  A^ A^ A^ A^ A^ A^ .
4 |  .  A^ .  Bv Bv Bv Bv .
5 |  .  .  Bv Bv Bv .  Bv .
6 |  .  .  .  .  Bv Bv Bv Bv
7 |  .  .  .  .  .  .  .  .
```

**Outcome:** P1 wins by threshold at step 25 (P1=25.425, P2=21.642). Identical to postfix-A baseline.

This confirms pure N-vs-S play in v2 is functionally identical to the source game (when both players play natural phase). Same scores, same step count, same end-state. The 4-phase mechanic does not interfere with the source dynamic.

---

## 3. Game 2: E-stone capture-immune denial test

### Setup: build a P2 ring around cell 37 (3×3 minus center).

```
0N,28S,8N,29S,16N,30S,1N,36S,2N,38S,9N,44S,17N,45S,10N,46S
```

State at move 16:
```
0 |  A^ A^ A^ .  .  .  .  .
1 |  A^ A^ A^ .  .  .  .  .
2 |  A^ A^ .  .  .  .  .  .
3 |  .  .  .  .  Bv Bv Bv .
4 |  .  .  .  .  Bv .  Bv .
5 |  .  .  .  .  Bv Bv Bv .
```
Scores: P1=16.962, P2=15.061. Cell 37 has 4 P2@S nbrs (29, 36, 38, 45).

### Variant A — P1 plays 37E (capture-immune denial):

Move 17 `37E` → engine accepts. Stone survives the 4 surrounding S nbrs.
- P1 score 16.962 → 15.061 (lost 1.9 to occupy a -x cell).
- P2 score 15.061 → 15.061 (unchanged; E radiates 0 in x).

After P2's best rational response (53S extends downward):
- Move 18 `53S` → P2=16.944.
- **Position: P1=15.061, P2=16.944.** P1 is behind by 1.883.

### Variant B — N at 37 (illegal-feeling but engine-legal):

Move 17 `37N` → engine accepts placement, captures immediately (4 anti-aligned nbrs > 2).
- Board reverts to 16.962 / 15.061 (stone captured, no net change).
- Wasted tempo.

### Variant C — natural extension 18N (the strong move):

Move 17 `18N` → P1=19.795.
- Move 18 P2 fills 37S (perfect closure) → P2=19.795.
- **Position: P1=19.795, P2=19.795.** Tied at higher level, same tempo deficit.

### Verdict for Game 2

The capture-immunity of E is **mathematically real** (Variant A worked, Variant B failed). But strategically:
- Variant A nets P1 -1.883 vs P2.
- Variant C nets P1 0.000 vs P2.

Variant C dominates A by 1.883 score-equivalent. **The denial value of E (preventing P2's +2.83 cluster fill) is overshadowed by the +1.88 opportunity cost of the missed natural N extension.**

I tried this in 3 different positions (initial 12-move, the Game 2 ring, plus a 14-move with column extension). In every case, "natural N somewhere safe" beats "denial E in enemy territory." E only wins when the alternative natural N moves are exhausted, which doesn't happen until very late in a 100-step game where the score race is already decided.

**E stones provide a real but dominated strategic option in skilled play.**

---

## 4. Game 3: E-vs-W secondary axis

### Pure E-vs-W race (no scoring):

```
27E,28W,26E,29W,35E,36W,34E,30W,33E,38W
```

After 10 moves: P1=0.000, P2=0.000. Predicted: E and W radiate ±y, dot with score targets (±x) = 0. **Both scores frozen at zero.** Confirmed by engine.

### E-vs-W mutual capture (move 11):

```
…,37E
```

Cell 37 has 3 W nbrs (29, 36, 38). E-stone capture score = -cos(π/2 - 3π/2) × 3 = +3 > 2 → captured. Engine output: `captured=[37]`. Matches theory.

### Mixed game W-as-suboptimal-substitute:

Tested whether P2 mid-game would prefer 38W over 38S. With opening
```
27N,36S,28N,37S,29N,44S,26N,45S,18N,53S,11N,52S,12N,38W
```
- 38W: P2 +0.475 (only the +x from 37S nbr radiating into the cell).
- 38S (alternative): P2 would have gained +1.883 (own self contribution + nbr).

P2's 38W is dominated by 38S by exactly the +0.93 self-contribution that S gives. **No rational P2 plays W in active scoring race.**

### Random-play probe (50 games):

```
P1=1, P2=1, draws=48, avg steps=70.2 (E/W move ratio 0.481, captures 3.66/game)
```

48/50 random games end in draws. The random policy spends ~50% of moves on E/W which contributes 0 score. Both players stall below threshold; game ends at 100 steps via piece-count majority (mostly equal).

### Natural-only-restricted random (50 games):

```
P1=29, P2=21, draws=0, avg steps=41.1, captures 2.70/game
```

When restricted to natural phase, balance returns. **This is the source-game regime.** Statistics match the postfix-A natural probe (35/15) within seed-noise variance.

### Verdict for Game 3

The E-vs-W axis is a **mathematically valid secondary territory game** with its own local capture mechanic. But it cannot coexist with the N/S scoring race because:
1. Each E/W move costs 1 turn of N/S progress.
2. The scoring race forces both players to be N/S-first or lose tempo to threshold.
3. Even if both players agree to play E/W, neither approaches the win threshold — the game stalls until step 100 majority, which is decided by who happened to place more stones.

There's no emergent "mutual blocking" dynamic in equilibrium because either player who switches back to N/S immediately wins the score race against an E/W-committed opponent.

---

## 5. Comparison vs source (`c6bb58075520`, mean 4.40/10)

| Dimension | Source (4.40/10) | v2 4-phase | Verdict |
|---|---|---|---|
| Action space | 65 | 257 | nominal +; effective same (E/W dominated) |
| Win symmetry | yes | yes (engine random P1=29 / P2=21 natural) | parity |
| Capture mechanic | owner-based | phase-cosine (real generalization) | technically richer |
| Phase orthogonality (the headline feature) | n/a | mathematically clean | engine-correct |
| E/W as denial primitive | n/a | dominated by N/S in any active scoring race | ineffective |
| E/W vs E/W secondary game | n/a | exists but cannot coexist with score race | structural conflict |
| Skilled-play decision depth | ~1 (where to N/S) | ~1 (where to N/S) — phase choice degenerates to natural | parity |
| Random-play game completion rate | most games complete | 4% complete (96% draws) | regression |

The v2 design genuinely solves the binary-phase symmetry pathology — E/W stones now have phase-coherent neutrality and capture-immunity, both verifiable in engine. But it inherits a structural problem from v1: **the orthogonal axis competes with the scoring axis for tempo without offering enough denial value to be worth the trade.**

A natural N/S move gains +1.88 score (own self-contribution) plus claims the cell. An E denial move gains 0–0.5 score but pays 1.0–1.9 to occupy a hostile cell. The math doesn't close the gap.

The clean orthogonality also has a perverse side-effect: random or weak play (50% E/W) prevents the game from terminating via threshold. This suggests the search/learning surface for an RL agent would be much harder than the source — agents would need to learn to ignore half the action space.

---

## 6. Score: **4 / 10 vs source (4.40)**

Reasoning:
- (+) Engine implementation is correct and elegant. All four properties (orthogonal score, immune capture, E-vs-W capture, N/S parity) verified mathematically and on engine.
- (+) v2 fixes the v1 binary-phase friendly-fire / camo-anchor pathologies. E stones are genuinely neutral in phase-cosine sense.
- (+) Pure N-vs-S play replicates source perfectly (Game 1 same outcome and scores as postfix-A).
- (−) E/W stones are dominated under any rational play optimizing for threshold-win. Denial value < N/S opportunity cost.
- (−) Random play 96% draws (vs source's natural completion). Action space inflation creates a learning/search obstacle.
- (−) The "secondary E-vs-W axis" cannot coexist with the scoring race. Structural conflict, not emergent depth.
- (−) Net: same conclusion as postfix-A. Effective decision space = source. Phase axis is mathematically real but strategically inert.

Slightly below source because the action-space inflation (257 vs 65) adds search/UX cost without compensating depth. A skilled player makes identical decisions to the source game but selects from 4× the action set.

---

## 7. Recommendation: **refine more (or drop)**

Two paths:

### Path A: re-tune phase economics

The fundamental issue: orthogonal phases pay 0 score per turn while natural phases pay ~+1.88. To make E/W competitive in equilibrium, one of these must change:

1. **Reduce N/S self-contribution** (decrease `INFLUENCE_STRENGTH`): would lower the natural-extension reward closer to E/W denial value. But this changes the feel of the source game.
2. **Add territory bonus for E/W**: e.g., +0.5 score per E/W stone owned at game end (independent of cell vec). Makes E/W a small positive sink, perhaps tipping marginal positions.
3. **E/W enables capture against N/S**: e.g., E neighbor of S contributes +0.3 (not 0) to S's capture math. Breaks orthogonality slightly but gives E offensive purpose.
4. **Tempo-immune E/W**: E/W moves count as half-turns (place + still your turn). Encodes the "wasted" feel into a bonus, but requires turn-engine surgery.
5. **Lower threshold**: 22.65 → 18 would make denial value relatively higher.

Each option needs a fresh small-spike eval. Path A is plausible but requires multiple iterations.

### Path B: drop phase mechanic

Same conclusion as postfix-A. The threshold-win territory game is incoherent with orthogonal phases — either the orthogonal phase is dominated (current state) or it bleeds enough energy back into scoring to break the orthogonality (path A options 2–4).

The source `c6bb58075520` (4.40/10) is a working game. **Strong recommendation: do NOT integrate v2 into the main evolutionary lineage in current form.** Two consecutive phase-spike attempts (binary v1 postfix-A and complex v2) have landed at the same 4/10 score with the same dominated-axis pathology. The phase concept itself may be incompatible with this scoring system. Suggest pivoting: try alternate scoring rules (e.g., first to 16 occupied cells, or mass-conservation captures) before another phase-mechanic spike.

---

## 8. Concrete game logs

All games engine-verified via `phase_play_helper_v2.py --action play`.

- **Game 1 (`27N,36S,28N,35S,…,20N`):** 25 plies, P1 threshold win 25.43 vs 21.64. Identical to postfix-A baseline.
- **Game 2A (`…,37E`):** P1 places E at 37 surrounded by 4 P2@S. Captured? **No** (cell 37 has 4 W contributing 0 each to E-capture math). Survives. Score: P1 16.96 → 15.06 (paid 1.9 for occupation).
- **Game 2B (`…,37N`):** Same setup, P1 plays N. Captured immediately (4 anti-aligned > threshold 2). Cell back to empty.
- **Game 2C (`…,18N,37S`):** Natural alternative. P1 reaches 19.79 from extending top cluster, P2 fills 37S to 19.79. Tied at higher level, P1 same relative position. **Strictly better than 37E variant by 1.883.**
- **Game 3A (E-only race):** Both scores frozen at 0.000 for 10 moves. Confirms orthogonality.
- **Game 3B (`…,37E` against W ring):** P1's E captured immediately by 3 W nbrs. E-vs-W capture verified.
- **Game 3C (P2's `38W` mid-game):** P2 gains only +0.475 from 38W vs +1.88 from 38S. Strictly dominated.

### Random-play probes:
- All-legal random (50 seeds): P1=1, P2=1, draws=48, avg 70.2 steps. ~96% incomplete.
- Natural-only random (50 seeds): P1=29, P2=21, draws=0, avg 41.1 steps. Source-like.

The huge gap between these two probes is the key statistical evidence that the E/W phase axis is dominated and structurally collapses the game when played randomly.
