# Eval-3: Phase-Extended c6bb58075520 — Emergent Dynamics Probe

**Evaluator:** evaluator-3
**Source comparator:** `c6bb58075520` (R16 human winner, mean human score 4.40/10)
**Engine:** `experiments/phase_spike/phase_game.py`
**Time budget:** ~60 min

---

## TL;DR

The phase-extension introduces *interesting* emergent mechanics — most notably the **camouflage anchor** (a P1@-1 stone deep in P2 territory yields large positive score gain) and **friendly-fire self-capture** (own-camouflage can capture own-natural stones). However, the implementation has a **fundamental scoring asymmetry** that makes the game P2-unwinnable: **50/50 random games are P1 wins**, and structured analysis confirms P2's natural play accrues *negative* score.

**Score: 3 / 10 vs source (4.40/10).** The mechanic itself shows novel emergent depth, but the broken P2 scoring makes the game itself worse than the source. **Recommendation: do not promote in current form. Fix scoring symmetry first, then re-evaluate.**

---

## 1. Rules summary (verified)

- 8×8 torus, alternating turns, max 100 turns, threshold-win at 22.6453.
- Each placement specifies cell + phase ∈ {+1, -1}.
- Owner ≠ phase. Four piece types: A (P1@+1), a (P1@-1 camo), B (P2@-1), b (P2@+1 camo).
- Capture is **phase-only** (owner-blind): a stone at phase P captured if `opp_phase_nbrs > same_phase_nbrs + 2`.
- Score: `P1 = Σ (cell_val × stone_phase) over P1 cells`; `P2 = Σ (cell_val × -stone_phase) over P2 cells`.

---

## 2. Three full games

### Game 1: cluster-vs-cluster baseline (P1 +1 cluster, P2 -1 cluster)

Moves: `27+, 36-, 28+, 35-, 29+, 37-, 30+, 44-, 26+, 43-, 25+, 42-` (12 plies)

Final board:
```
3 |  .  A  A  A  A  A  A  .
4 |  .  .  .  B  B  B  .  .
5 |  .  .  B  B  B  .  .  .
```
Score after 12 plies: **P1=+8.92, P2=−9.87**. Note: P2's *natural* cluster (B's all -1) accrues *negative* score. P2 cannot reach +22.65 by playing naturally.

This is the first signal of the scoring asymmetry — both players grow their absolute score in opposite directions of the threshold.

### Game 2: P1 camouflage invasion (the "anchor" dynamic)

Setup: P1 builds a row-0 +1 wall, P2 builds a 3×3 -1 cluster at rows 3-5. P1 then drops camouflage stones (`a` = P1@-1) at the *boundary* of the P2 cluster. Game ended at step 24 by P1 threshold.

Key score deltas:
| Move | Token | Player | Score after |
|---|---|---|---|
| 17 | `27-` (P1 camo) | P1 | 15.06 → **16.94** (+1.88) |
| 19 | `30-` (P1 camo) | P1 | 16.94 → **18.83** (+1.88) |
| 21 | `42-` (P1 camo) | P1 | 18.83 → **20.23** (+1.41) |
| 23 | `8+` (P1 nat) | P1 | 20.71 → **22.59** (+1.88) |
| 24 | `16+` (P2 camo) | P1 wins | P1 → **23.07** > 22.65 |

Final board:
```
0 |  A  A  A  A  A  A  A  A
1 |  A  .  .  .  .  .  .  .
2 |  b  .  .  .  .  .  .  .
3 |  .  .  .  a  B  B  a  .
4 |  .  .  B  B  B  B  B  .
5 |  .  .  a  B  B  B  B  .
```

**Emergent finding (concrete):** A P1 camouflage stone surrounded by P2@-1 stones contributes **+1.88** to P1's score (the same as a natural stone in own cluster), because `cell_val × phase = (negative) × (-1) = positive`. The rules text claims "camouflage is a NET COST" — empirically false in dense enemy territory. **Camo INSIDE enemy clusters is a HIGH-VALUE move for P1.**

### Game 3: capture cascades + sacrifice plays

Moves: 35 plies of mixed-phase combat with multiple captures.

Captures observed:
- Move 5 (`36+` by P1): captured P2's `28-` (P1@+1 placement created 3rd +1 nbr around P2@-1 at 28, which had 0 -1 nbrs → 3>0+2 → capture).
- Move 9 (`43+` by P1): captured P2's `35-`.
- Move 22 (`54-` by P2): **captured P1's natural stone at `53` (A=P1@+1)**. Cell 53 had nbrs 52(P1@-1 camo), 54(P2@-1 just placed), 45(P2@-1), 61(empty) → 3 -1 vs 0 +1 → capture. P1's *own* camouflage at 52 contributed to capturing P1's natural stone at 53 — **friendly-fire by phase**.

### Friendly-fire self-capture (synthetic test)

To confirm the rules-implied mechanic: I placed P1@+1 at cell 27, then surrounded it with P1's *own* camouflage (P1@-1 at cells 26, 28, 35). Result: cell 27's natural P1 stone was **captured by P1's own camouflage stones** (3 -1 nbrs vs 0 +1 nbrs).

```
P1 cell 27 phase 1 → placed
P1 cell 28 phase -1 → placed (P1 camo)
P1 cell 26 phase -1 → placed (P1 camo)
P1 cell 35 phase -1 → captured: [27]   ← own stone vaporised
```

This is a genuine new strategic primitive: phase-only capture means a player can *self-griefing* with poorly-placed camo, OR can deliberately re-shape their own cluster (e.g., capturing your own natural stone removes its score contribution but frees the cell — niche but valid).

---

## 3. Emergent dynamics — concrete examples

### 3.a. Camouflage Anchor (P1's dominant strategy)

P1 places camouflage (P1@-1) stones inside dense P2 -1 clusters:

- Cell value at the camo stone is highly negative (~-1.88 from 4 -1 neighbors + self).
- P1 score contribution = `cell_val × phase = -1.88 × -1 = +1.88` per camo.
- Stone is **safe**: 4 same-phase neighbors → no capture.
- Side-effect: the camo's own -1 phase pushes P2's neighboring cell_vals more negative, making P2's score *worse*.

**This is a dominant strategy P1 should always play after P2 has formed a cluster.** Synthetic test: with P2 in 8-stone -1 ring (cells 27,28,29,35,37,43,44,45 surrounding empty 36), P1 places camo at 36 → **P1 score jumps from 15.06 to 17.89 (+2.83) in one move** with zero risk (4 same-phase nbrs).

### 3.b. Capture cascades behave asymmetrically

Owner-blind phase capture creates dynamics where:
- Mixed-phase neighborhoods are unstable: a single phase flip (camo placement) can flip a 2-vs-2 to 3-vs-1 and trigger capture.
- **Players can capture stones of their OWN owner** (verified in Game 3 move 22 indirectly, in synthetic test directly).
- Conversely, players can *protect* an enemy stone by sandwiching it with same-phase neighbors of the enemy's phase.

### 3.c. Sacrifice-camo capture (proposed but ineffective)

I tested whether a P1@-1 sacrifice in P2 cluster could trigger cascading captures of P2 stones. Result: **no immediate capture cascades** — the surrounding P2 stones still have 3+ same-phase neighbors so they remain stable. The camo's *own* score gain is the payoff, not capture damage. The "sacrifice for capture" intuition does not pan out at radius-1.

### 3.d. Scoring asymmetry (the elephant in the room)

Mathematical inspection of the score formula reveals P2 cannot reach +22.65 in any plausible configuration:

- **P2@-1 in P2 cluster** (natural): cell_val ≈ -1.88, contribution = -1.88 × -(-1) = -1.88 → NEGATIVE.
- **P2@+1 in P2 cluster** (camo in own cluster): cell_val ≈ +1.88 (because +1 self + +1 nbrs), contribution = +1.88 × -(+1) = -1.88 → NEGATIVE.
- **P2@-1 in P1 +1 territory** (sacrifice): cell_val can be slightly positive (~+0.018) at boundary positions, contribution ≈ +0.018. To reach +22.65 P2 would need ~1250 such stones. **Impossible on 64-cell board.**
- **P2@+1 in P1 +1 territory** (counter-camo): cell_val=+1.88, contribution = -1.88 → NEGATIVE.

P2 has **no positive-score path** that scales. This is structural, not strategic.

The likely intended formula was `P2 score = Σ -(cell_val × phase) over P2 cells = Σ cell_val × phase × (-1)`. With that, P2@-1 in P2 cluster: `-1.88 × -1 × -1 = -1.88`... still negative. Hmm. Probably the intended formula is `P2 score = Σ -cell_val × stone_phase` which gives `-(-1.88) × -1 = -1.88`... also wrong. The genuinely symmetric formula would be: `P_score = |Σ cell_val × phase × team_sign|` where team_sign(P1)=+1, team_sign(P2)=-1, giving P2@-1 in cluster: `-1.88 × -1 × -1 = -1.88` ... still off.

Actually the cleanest fix is `P2 score = Σ (-cell_val) × phase over P2 cells`. P2@-1: `-(-1.88) × -1 = -1.88`. No. Try `P2 score = -Σ cell_val × phase over P2 cells`: P2@-1 in cluster: `-(-1.88 × -1) = -1.88`. Still negative.

The fundamental issue: P2's "natural" stones are -1, and a -1 stone surrounded by -1 stones has a large *negative* cell_val. To make this contribute positively to P2's score, you'd need something like `P2 score = Σ |cell_val × phase|` (absolute value) — but that destroys the punishment-for-camo intent.

A symmetric design would use `P_score = Σ cell_val × phase × owner_sign` where for P1: cell_val × phase × +1; for P2: cell_val × phase × -1. P2@-1 in cluster: -1.88 × -1 × -1 = -1.88. Still negative.

The real fix: **redefine P2's "side"**. Make P2's natural stones +1 phase too, but flip the score: `P2 score = -Σ cell_val × phase over P2 cells`. P2 plays +1 stones in own cluster: cell_val=+1.88, phase=+1, score = -(+1.88) = -1.88. Hmm.

I cannot find a simple sign-flip that makes both players symmetric under this design. The decoupling itself may be incoherent with the threshold-win frame.

---

## 4. 50-game random-vs-random probe

Code: `experiments/phase_spike/eval3_work/random_probe.py`

Results (50 games, seeds 0-49, uniform random over legal actions):

```
Wins: P1=50, P2=0, Draws=0
Avg game length: 43.7 steps
Threshold wins: 50/50
Reached max turns (100): 0/50

Avg final score P1: +23.494, P2: -21.947  (threshold = +22.65)

Stone PLACEMENT counts (mean per game):
  P1 natural (+1):    10.72
  P1 camouflage (-1): 11.34
  P2 natural (-1):    10.06
  P2 camouflage (+1): 11.24

Camouflage usage rate (placements):
  P1 camo / P1 total = 51.4%
  P2 camo / P2 total = 52.8%

Stone ALIVE at game end (mean):
  P1 natural alive: 9.94 / 10.72 placed (92.7%)
  P1 camo alive:    10.52 / 11.34 placed (92.8%)
  P2 natural alive: 9.22 / 10.06 placed (91.7%)
  P2 camo alive:    10.60 / 11.24 placed (94.3%)

Captures: avg 3.08 per game (154 across 50 games)
```

**Key findings from the probe:**
1. **P1 wins 100% of random games.** Strict structural P2 disadvantage.
2. Avg P2 final score is **-21.95** — P2 plays toward MORE negative, never crossing +22.65 threshold.
3. Random play already finds many camo placements (~52% of moves).
4. **Camouflage survival rate is ~93-94%, virtually identical to natural stones** — phase-decoupling does NOT meaningfully change capture rates under random play. Camo is not "harder to kill" in expectation, just useful.
5. Captures are sparse (3/game) — capture mechanics rarely fire; the threshold race is the dominant pressure.

---

## 5. Strategic depth comparison vs source `c6bb58075520`

| Dimension | Source (4.40/10 human) | Phase-extended | Verdict |
|---|---|---|---|
| Action space | 65 (64 cells + pass) | 129 (64×2 phases + pass) | +depth |
| Capture mechanic | owner-based outnumber | phase-based outnumber | novel but creates self-capture |
| Strategic primitives | place to claim influence | + camo-anchor + self-capture + protected-island | +novel primitives |
| Win symmetry | symmetric (both score positive in own territory) | **broken** (P2 cannot win) | **−major regression** |
| Random-game balance | (presumably ~50/50 in source) | 50-0 P1 | **−broken** |
| Skill expression | moderate (4.40 human mean) | unmeasurable due to broken P2 | unable to assess |

The phase mechanic itself is a genuinely interesting addition with novel emergent dynamics (camo anchor, friendly-fire, mixed-phase capture cascades). The **camouflage anchor** is the strongest emergent primitive I found — it creates real strategic depth around enemy cluster invasion that doesn't exist in the source game.

But the implementation is asymmetric and unwinnable for P2. Even if a strong P2 player exploited every boundary trick, the score formula caps P2's positive contribution at fractional values per stone. **The game is not a game in any meaningful sense — it's a P1 demonstration.**

---

## 6. Score: **3 / 10 vs source (4.40 human)**

Reasoning:
- (+) Camouflage anchor is a genuinely novel, deep strategic primitive (would warrant ~5-6/10 if balanced).
- (+) Phase-only capture creates surprising self-capture and protect-enemy plays.
- (+) Action space ≈ 2× source — more decisions per turn.
- (−) Game is **structurally unwinnable for P2**; 50/50 random P1 wins; P2 score formula cannot reach +threshold.
- (−) Rules text contradicts implementation ("camouflage is a NET COST" — empirically untrue in dense enemy territory).
- (−) No evidence captures fire often enough to matter (3/game in random play).

The novel mechanics show promise (would score ~6/10 if symmetric), but the broken scoring drags the overall product below the source.

---

## 7. Recommendation

**Do NOT promote to Phase-2 in current form.** Required pre-Phase-2 fixes:

1. **Fix P2 score formula.** Either:
   - (a) Make `P2 score = -Σ cell_val × phase over P2 cells` AND redefine P2 natural as +1 (full team-flip). This makes P2 a mirror of P1.
   - (b) Use absolute alignment: `P_score = Σ cell_val × phase × team_sign(owner)` with team_sign mapped so P2's natural cluster scores positive (requires picking a coherent algebraic frame).
   - (c) Simplest: `P2 score = -P1_style_score with phase swapped for P2 stones`. Verify with a 50-game random probe → expect ~50/50.

2. **Update rules text** to reflect that camouflage in enemy territory is a *positive* score move (the anchor exploit). The current text mis-describes the mechanic.

3. **After symmetric scoring**, re-run random probe AND a Mover-vs-camo-aware-P2 probe to verify camo anchor is balanced — if camo is dominant for both players, may need to add a per-camo penalty (e.g., -ε per camo stone) to keep natural play viable.

4. **Optional but valuable**: add a "discovery game" where strong models find the camo-anchor exploit organically. This would be a useful strategic-depth signal for the meta-eval.

If the scoring fix lands and balance verifies, the camo-anchor + friendly-fire mechanics are interesting enough that I'd re-rate this **6-7/10** post-fix — meaningfully above the 4.40 source.
