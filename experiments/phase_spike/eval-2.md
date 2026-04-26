# eval-2: Phase-Extended c6bb58075520 — evaluator-2 findings

**Evaluator:** evaluator-2
**Date:** 2026-04-22
**Source comparison:** `c6bb58075520` (R16 human winner, scored 4.40/10)
**Engine:** `experiments/phase_spike/phase_game.py`
**Helper:** `experiments/phase_spike/phase_play_helper.py`

---

## TL;DR

**Score: 2/10. Recommendation: DROP (or refine the score formula and re-run).**

The phase-extension idea is conceptually interesting (decoupled owner/phase, camouflage in enemy territory), but the engine as currently implemented has a **critical sign-asymmetry in `player_score`** that makes P2 effectively unable to win via threshold and makes the camouflage mechanic strategically irrational for the placer. The mechanic does not pay off — it actively HELPS the opponent in nearly every realistic situation. The "depth" added is one degree of freedom in action space, but no real strategic depth materialises.

---

## Critical engine finding (BUG)

`PhaseGame.player_score(player=2)` computes `cell_val * (-stone_phase)` for P2-owned cells. For a natural P2 stone (phase = -1) sitting in a -1-influence region (cell_val negative), this evaluates to `(negative) * (+1) = negative`. **Natural P2 play accumulates negative score**, even though the win condition is `score > 22.6453`.

Empirical verification (clean P2 -1 cluster, no P1 nearby):
- 9 P2@-1 stones in a 3x3 block → P2 score = **-19.80**, P1 score = +15.99 (P1 has its own cluster)
- All P2-owned cell values negative (e.g. cell 9: -2.83) → P2 score formula sums them as-is.

This is almost certainly a sign-error. The formula likely should be `cell_val * stone_phase` for P2 too (so P2@-1 in -1 zone = positive), OR `cell_val * stone_phase * (-1 if owner is P2 else 1)` flipped at the cell-value level. Either way, **as written, P2 can ONLY win via `max_turns_majority` (piece count after 100 moves)**. P2 can never cross the threshold.

This bug invalidates clean comparison to source `c6bb58075520`, where the win condition is symmetric.

---

## Game 1 — greedy/natural play, both players use natural phases

**Move sequence:** `27+,36-,28+,35-,19+,44-,20+,43-,18+,42-,11+,51-,12+,50-,26+,34-,17+,33-,25+,41-,4+,49-,5+`

P1 builds a +1 cluster in rows 0-3 cols 1-4. P2 mirrors with a -1 cluster in rows 4-6.

Trajectory:
- Move 1: P1=0.93 P2=0
- Move 8: P1=6.58 P2=-6.58 (perfect mirror)
- Move 22: P1=21.66 P2=-22.61
- **Move 23: P1 5+ → P1=23.54 crosses threshold. P1 wins (`P1_threshold`).**

Final board: two opposing 3x3+ clusters, mirror-symmetric. P1 wins by tempo (first-mover advantage on a symmetric race). No captures occurred — both clusters expanded without contact.

**Outcome: P1 wins at move 23. P1=23.54, P2=-22.61.**

---

## Game 2 — P2 plays aggressive camouflage (b stones in P1 territory)

**Move sequence:** `27+,28+,19+,20+,18+,11+,12+,26+,17+,25+,3+,4+,10+,2+,9+,1+,33+,32+,41+`

P1 plays natural A's clustering at the centre. P2 plays exclusively b (P2@+1) into and around the P1 cluster.

Trajectory:
- Move 7 (P1=8.01, P2=-6.12) — already further along than Game 1 step 7 (P1=3.75)
- Move 16 (P1=20.29, P2=-17.44)
- **Move 19: P1 41+ → P1=24.05 crosses threshold. P1 wins.**

**Final board:**
```
0 |  .  b  b  A  b  .  .  .
1 |  .  A  A  b  A  .  .  .
2 |  .  A  A  A  b  .  .  .
3 |  .  b  b  A  b  .  .  .
4 |  b  A  .  .  .  .  .  .
5 |  .  A  .  .  .  .  .  .
```

**Does the camouflage strategy pay off? NO — it actively HURTS P2.**

Mechanism: every b stone radiates +1 influence into P1's surrounding A cells, raising P1's cell values. P1's score grows ~25% faster per move than in Game 1. P1 wins in 19 moves vs 23 in Game 1.

The camouflage stones are uncapturable (same phase as surrounding A's), but their influence radiation gifts P1 score. P2's score formula gets even more negative because the b cells have positive `cell_val` and `cell_val * -(+1)` is negative.

The ONLY benefit of camouflage is "blocking" P1 from claiming a high-value cell — but P1 has 64 cells to choose from and can simply expand around the camouflage. Net effect: pure tempo gift to P1.

---

## Game 3 — seat-swap of Game 2: P1 plays aggressive camouflage (a stones)

**Move sequence:** `27-,28-,19-,20-,18-,11-,12-,26-,17-,25-,3-,4-,10-,2-,9-,1-,33-,32-,41-`

Same cells as Game 2, all phases flipped to -1. P1 plays "a" everywhere (camouflage). P2 plays natural B everywhere.

Trajectory: **byte-for-byte identical to Game 2.**
- Move 16: P1=20.29 P2=-17.44
- **Move 19: P1=24.05 wins (`P1_threshold`).**

**Final board:**
```
0 |  .  B  B  a  B  .  .  .
1 |  .  a  a  B  a  .  .  .
2 |  .  a  a  a  B  .  .  .
3 |  .  B  B  a  B  .  .  .
4 |  B  a  .  .  .  .  .  .
5 |  .  a  .  .  .  .  .  .
```

**Does the dynamic flip cleanly? NO.**

The seat-swap does NOT flip the dynamic. Two reasons:

1. **Score asymmetry bug (above):** P1's camouflage (a, phase=-1) sitting on a -1-cell-value cell scores `cell_val(-) * phase(-1) = positive`. So P1 a-stones in P2's -1 zone score POSITIVELY for P1, just like A-stones in +1 zones. P1 still wins.

2. **First-mover advantage persists:** P1 still moves first; the pattern of moves is mathematically symmetric under phase-flip, so the same race-to-threshold outcome occurs.

A clean seat-swap would require swapping *who plays first* and fixing the score formula — neither holds.

---

## Capture mechanic (sanity check)

Captures work as documented:
- A P2@-1 stone surrounded by 4 P1@+1 (radius-1 torus neighbours) → outnumber score 4 vs 0, threshold 2 → captured. Verified.
- A P2@+1 (b camouflage) surrounded by 4 P1@+1 (A) → all same phase → no capture. Verified.

The phase-based (vs owner-based) capture rule is implemented correctly. But it never fires in symmetric-cluster play because each side's stones are surrounded by their own same-phase friends.

---

## Comparison to source `c6bb58075520` (mean 4.40/10)

| Dimension | Source `c6bb58075520` | Phase-extended |
|---|---|---|
| Decision space per turn | ~64 placements | 128 placements (cell × phase) |
| Strategic axes | 1 (where to place) | 2 in theory; 1 in practice |
| Asymmetry | Clean (P1/P2 mirror) | Broken (P2 score sign-bug) |
| New mechanic depth | n/a | Camouflage exists but is strictly dominated |
| Capture nuance | Owner-based | Phase-based (subtle, could matter, never fires in observed play) |
| Tempo character | Race to threshold via cluster | Same race; camo is a tempo gift |

The source game scored 4.40/10 — already a marginal game. The phase extension does not improve any of the dimensions that made `c6bb58075520` weak (mainly: monotone race to threshold with limited interaction). Instead it adds:
- A doubled action space that creates illusion of choice (the +1/-1 dimension is dominated for both players)
- A bug that breaks the win condition for P2
- A "novel" camouflage mechanic that is strictly bad for the player who uses it

---

## Is camouflage tactical depth or one-trick gimmick?

**Neither — it is actively negative-EV in this engine.** The camouflage stone:
- Costs the placer score (own-cell value × -phase = negative for either side trying to use it)
- Radiates the *opposite* of the placer's preferred influence onto neighbours, helping the opponent's same-phase clusters grow faster
- Survives capture only because neighbours match its phase — but those neighbours are the opponent's cluster, which it is feeding

There is one narrow theoretical use: place a single camouflage stone on a cell the opponent uniquely needs to hit threshold, late-game, when the radiation cost is no longer relevant. But on a 64-cell board with only ~20 played stones at threshold time, the opponent can always route around. I did not find a single position where camouflage was a positive-EV move.

A different scoring formula (e.g. `cell_val * |phase|` weighted by team alignment differently, or owner-based capture combined with phase-only-for-influence) might rescue the mechanic, but as currently calibrated, the camouflage is a trap for whoever falls into using it.

---

## Recommendation: DROP

- **Drop** in current form — the score-formula bug alone disqualifies it as a playable game, and even if fixed, the camouflage mechanic is dominated.
- If pursued further, **refine** (do not integrate as-is):
  1. Fix `player_score` for P2 — it appears to use the wrong sign on `stone_phase`; expected behavior likely `cell_val * stone_phase * team_sign(player)` where `team_sign(P2) = -1`.
  2. Re-investigate camouflage scoring — possibly cell influence should NOT count for the placer of a camouflage (block-only, no influence radiation), to remove the "feed the enemy" anti-pattern.
  3. Consider owner-based capture instead of phase-based, to give camouflage stones genuine survivability tactics.
  4. After fixes, re-evaluate whether the phase axis adds depth that source `c6bb58075520` lacked.
- **Score: 2/10** vs source 4.40/10. The extension is strictly worse than the source on both correctness (bug) and strategic interest (dominated camouflage). It would be unfair to score it higher because the source is at least playable as designed.

---

## Files & references

- Engine: `/Users/jamesbrowne/aigame/experiments/phase_spike/phase_game.py`
  - Bug location: `player_score()` lines 169-188 — sign on P2's `cell_val * (-phase)` term.
- Helper: `/Users/jamesbrowne/aigame/experiments/phase_spike/phase_play_helper.py`
- Source game id: `c6bb58075520`
