# Eval-postfix-A: Phase-Extended c6bb58075520 — Re-evaluation after P2 score-sign fix

**Evaluator:** evaluator-postfix-A
**Source comparator:** `c6bb58075520` (R16 human winner, mean 4.40/10)
**Engine:** `experiments/phase_spike/phase_game.py` (post-fix; `target = -1` for P2 in `player_score`)
**Time budget:** ~45 min

---

## TL;DR

The score-sign fix DOES restore seat symmetry (random-play balance is now ~50/50, vs 100/0 pre-fix). However, fixing the sign also **kills the camouflage anchor exploit that was the most interesting emergent primitive in eval-3.** Post-fix, camouflage is now strictly bad: it costs you ~1.88 per stone AND helps the opponent ~0.95 by radiating their natural phase. The mechanic is mathematically dominated.

Net result: the game is now BALANCED but BORING. Friendly-fire still works as a strategic primitive, but is also strictly disadvantageous to the camo-placer. The phase action space (~129 vs 65) is mostly degenerate — half the actions (camo) are dominated.

**Score: 4 / 10 vs source (4.40/10).** Slightly below source. The phase distinction adds action-space surface area without strategic depth post-fix. Camo only fires in random play, never in skilled play.

**Recommendation: refine more (re-introduce camo asymmetry that doesn't break P2) OR drop the phase mechanic entirely.** Current state is a wash vs the simpler source game.

---

## 1. Verification of fix

In `phase_game.py:185`, score formula now uses:
- P1: `total += cell_val × +1`
- P2: `total += cell_val × -1`

This gives both players a "team alignment" they can score with. Verified in Game 1 below: P2's natural cluster now accrues positive score symmetrically with P1's.

---

## 2. Game 1: greedy mostly-natural play (seat balance test)

Both players build mirrored natural clusters; P1 starts.

Moves: `27+,36-,28+,35-,29+,37-,26+,44-,25+,43-,30+,42-,33+,38-,18+,46-,17+,53-,19+,54-,11+,55-,12+,52-,20+`

Final (step 25):
```
0 |  .  .  .  .  .  .  .  .
1 |  .  .  .  A  A  .  .  .
2 |  .  A  A  A  A  .  .  .
3 |  .  A  A  A  A  A  A  .
4 |  .  A  .  B  B  B  B  .
5 |  .  .  B  B  B  .  B  .
6 |  .  .  .  .  B  B  B  B
7 |  .  .  .  .  .  .  .  .
```

Outcome: **P1 wins by threshold at step 25 (P1=25.43, P2=21.64).** Note: P2 is only 1.0 behind threshold — within one move of winning. This is a clean tempo race.

If P1 passes anywhere in the late midgame (verified by `…,11+,55-,pass,52-`), P2 reaches 21.64 and is one move from threshold while P1 stalls. So the game is genuinely **decided by tempo**, which is an expected property of an alternating board game. Seat balance is acceptable.

Random-play probe (50 seeds, uniform legal-action policy): **P1=4 wins, P2=5 wins, Draws=41.** Symmetric. The high draw rate is because random camo placements (~50% of moves) drag scores away from threshold — neither player can converge.

Natural-only-restricted random (P1 always +1, P2 always -1): **P1=35, P2=15, draws=0.** First-move advantage is large here, but this is a *strategic* asymmetry, not a structural one — comparable to the source game.

---

## 3. Game 2: camouflage anchor (the formerly-dominant tactic)

Eval-3 found that placing P1@-1 inside dense P2 territory gave P1 +1.88 to score (with the buggy formula). Test post-fix:

Setup: P1 builds row-0 wall, P2 builds 3×3 -1 cluster ringed around cell 36.
Moves: `0+,27-,1+,28-,2+,29-,3+,35-,4+,37-,5+,43-,6+,44-,7+,45-,36-`

After move 16 (P2 closes ring at 45-): P1=15.06, P2=15.06.

Move 17: P1 plays **camo at 36** (P1@-1) — formerly the +1.88 anchor exploit.

```
3 |  .  .  .  B  B  B  .  .
4 |  .  .  .  B  a  B  .  .
5 |  .  .  .  B  B  B  .  .
```

**Result: P1=12.23 (DROPPED -2.83), P2=16.96 (GAINED +1.90).** A -4.7 swing AGAINST P1.

Math: cell-value at 36 ≈ -1.88 (4 -1 nbrs + self). Post-fix P1 contribution = `-1.88 × +1 = -1.88` (negative for P1). Plus the camo's own -1 radiation pushes the 4 surrounding P2@-1 cell-values further negative, which boosts P2 score by `+0.95` total.

**Verdict: camouflage anchor is now a STRICTLY DOMINATED move.** The "interesting" emergent primitive of eval-3 was an artifact of the sign bug. Post-fix, no rational player ever places camouflage. Compare: same setup, P1 plays NATURAL `36+` instead → captured immediately (4 -1 nbrs vs 0 +1, threshold 2 → capture). So the choice at cell 36 is camo (lose ~2 score) or natural (lose stone, no score change). Both bad. **Best move at 36 is don't play there at all.**

This kills the most interesting emergent dynamic from eval-3.

---

## 4. Game 3: friendly-fire self-capture

Eval-3 noted phase-only capture lets a player capture their own stones. Verified post-fix:

Moves: `27+,0-,28-,1-,26-,2-,35-`

Setup: P1 places natural at 27, then surrounds with own camo (28-, 26-, 35-). P2 plays elsewhere.

After move 7 (`P1 35-`):
```
3 |  .  .  a  .  a  .  .  .
4 |  .  .  .  a  .  .  .  .
```

`captured=[27]` — P1's own A stone at 27 was captured by P1's own camo (3 -1 phase nbrs vs 0 +1). Score: P1 = -2.797, P2 = 4.698.

**Friendly-fire works as described.** But: deliberately capturing your own stone via your own camo costs:
- The captured A stone (would have been +1 phase contribution).
- 3× -1 phase contributions from the camos (-2.83 to your score).
- A radiating boost to any nearby enemy.

This is a triple loss. **Friendly-fire is a real mechanic but a strictly suicidal one.** I cannot construct a position where deliberately capturing your own stone via your own camo is the best move.

There IS a passive flavor: a sloppy P1 player can accidentally self-capture if they place camo near their own naturals. But "don't shoot yourself in the foot" is a degenerate strategic primitive, not depth.

---

## 5. Capture mechanics in mixed play

Tested mixed-phase capture cascades work (e.g., P2 plays `21-` next to P1's `29+` with adjacent P2@-1 stones triggers capture of 29). These captures are real — but they're equivalent to the source game's owner-based capture in the natural-phase regime (both players play their natural phase). The phase distinction only changes outcomes when somebody plays camo, which post-fix is a strictly bad move.

Random-play captures: 10.14/game post-fix vs 3.08/game pre-fix. The increase is because random play places ~50% camo, which causes phase-mismatch captures. Skilled play would not place camo, returning to source-like capture rates.

---

## 6. Strategic depth comparison vs source

| Dimension | Source (4.40/10) | Phase post-fix | Verdict |
|---|---|---|---|
| Action space | 65 | 129 (but ~half dominated) | nominal +; effective same |
| Win symmetry | yes | yes (fixed) | parity |
| Capture mechanic | owner-based | phase-based | equivalent if both play natural |
| Emergent primitive: camo anchor | n/a | dominated post-fix | net zero |
| Emergent primitive: friendly-fire | n/a | suicidal | net zero |
| Interesting decisions per turn | ~1 (where to place) | ~1 (where to place; phase = always natural) | parity |

The phase mechanic was supposed to add a real strategic axis. Post-fix, the dominant strategy is "always play natural phase" because:
1. Camo costs your score (~-1.88 in enemy territory, ~0 in own territory if isolated).
2. Camo helps the enemy (radiates their natural phase).
3. Camo can capture your own stones (friendly fire).
4. Natural-phase plays cannot do any of these bad things.

Therefore, the entire phase action axis collapses to a single dominant choice: phase = your natural. The game becomes effectively the source game with extra (dominated) actions.

---

## 7. Score: **4 / 10 vs source (4.40 human)**

Reasoning:
- (+) Seat symmetry fixed; random play is balanced now.
- (+) Capture mechanic is mathematically interesting (phase-based outnumber).
- (−) Camouflage anchor — the strongest emergent primitive in eval-3 — is now mathematically dominated.
- (−) Friendly-fire self-capture is real but strictly suicidal; not a meaningful strategic primitive.
- (−) Phase action axis collapses to "always pick natural" under any rational play.
- (−) Net: nothing meaningfully novel vs source. Source game is simpler with the same effective decision space.

Slightly below source because the action-space inflation (129 vs 65) adds search/UX cost without compensating depth. A player who didn't realize camo was dominated would lose; once you know it's dominated, the game is identical to the source.

---

## 8. Recommendation: **refine more** (or drop)

Two paths forward:

### Path A: refine (preferred if pursuing this further)
The fundamental tension is: how do you make camouflage have a *positive* strategic use case without making it a free anchor exploit?

Options:
1. **Asymmetric camo cost**: camo contributes 0 to score (not negative), but blocks a cell and survives in enemy territory. Then camo is a pure denial tool at cost = 1 turn. Test if denial value exceeds tempo.
2. **Camo enables capture**: a camo stone counts double for triggering capture (so P1@-1 in P2 cluster could chain-capture P2 stones). Re-introduces the offensive use that eval-3 hoped for.
3. **Phase flips on capture**: when a stone is captured, instead of removing, flip its phase to opposite owner. This makes phase-mismatch capture a *territorial transfer* primitive (more strategic than removal).
4. **Owner-aware cell-value**: cell_val for scoring only counts own-influence (your stones boost your cells, opponent stones don't subtract). Then camo in enemy territory has near-zero score effect, becoming a pure block.

Each option needs a fresh small-spike eval.

### Path B: drop the phase mechanic
The simplest conclusion is that the phase decoupling is incoherent with threshold-win territory scoring. The source game (4.40/10) is already a working game. The phase extension as currently designed adds nothing and complicates UX. **Strong recommendation: do NOT integrate into the main evolutionary lineage in current form.** If the team wants to explore complex/phase mechanics, prototype options 1-4 above as separate spikes first.

---

## 9. Concrete game logs

All three games above were engine-verified via `phase_play_helper.py --action play`. Move logs and final boards are reproduced verbatim from CLI output.

Game 1: 25 plies, P1 threshold win, both players above 21 at end (close race).
Game 2: 17 plies, P1 plays camo anchor at 36 → P1 score drops -2.83, P2 score rises +1.90 (camo is dominated).
Game 3: 7 plies including engineered self-capture; P1's own A stone vaporized by P1's own camo (-2.83 own-score cost, plus loss of original +0.93 stone).

Random probe (50 games, all-legal-action): P1=4, P2=5, Draw=41. Game length avg 75.8 steps.
Natural-only random probe (50 games): P1=35, P2=15, Draw=0. Game length avg 42.5 steps. Tempo advantage to P1, similar to source.
