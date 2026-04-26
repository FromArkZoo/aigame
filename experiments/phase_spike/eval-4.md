# Evaluator-4: Phase-Extended `c6bb58075520` — Novelty Adversary Review

**Evaluator role**: argue the phase extension is NOT meaningfully different from existing
abstract games, then rebut. Score on the NOVELTY axis only (vs source 4.40/10 human mean).

**Methodology**: read rules, played 2 random-policy games (seeds 1 and 7) to ground myself,
then ran ~6 calibrated micro-positions to probe whether the camouflage stone delivers
strategic value not reducible to a known primitive. Total budget ~45 min.

---

## 1. Adversary Phase — "It's not new"

### A1. Camouflage = relabeled "stone strength" / "Quantum Tic-Tac-Toe lite"
Each stone is one of four states {P1@+1, P1@-1, P2@+1, P2@-1}, but capture and
influence are decided **purely by phase**, not owner. Strip away the owner labels and
the board reduces to a two-color (+/-) game where score is computed by attaching an
ownership tag at end. That is essentially a Reversi/Othello variant with a *delayed
attribution* annotation. Quantum Tic-Tac-Toe (Goff 2006) and various "spy stone"
Hex variants already explore identity hiding.

### A2. The decoupling is a re-skin of "tag-team Reversi"
P1@+1 and P2@+1 are mechanically indistinguishable for capture and influence — they
are both "+1 team" stones. So the board is really a four-stone-type game where
two colors play on each side. This is structurally identical to a 2-player game
where each player commands two coalitions, scored by "which coalition do I claim?"
That is just two-player tag-team Othello / Lines-of-Action, no new primitive.

### A3. "Stone strength" relabeled
A camouflage stone is a "0-strength stone" or "blocker stone" that produces a
fixed influence with the wrong sign for its owner. Many area-influence games
(Go's stone-strength variants, Tak's flat/wall distinction, Onitama's wind spirit)
already include "stones that occupy a cell but don't score." This is a re-skin
of the wall / blocker mechanic from Tak.

### A4. It's a trivial transformation of the source
Mechanically the source game `c6bb58075520` is owner-determined: P1 places +1,
P2 places -1, capture is "outnumbered by opposite color". The extension just
adds 1 bit per move (phase choice). On any well-played game, the extra bit is
**strictly dominated** by the natural choice — a quick probe (see Evidence E1
below) shows camouflage stones almost always REDUCE the placing player's score,
because they radiate the wrong-sign influence into their own surrounding
territory. So the extra action just expands the move space without adding
genuinely useful options. That's not a new game primitive; it's noise.

### A5. The "invade enemy territory" pitch is empty
The headline pitch is "camouflage stones survive in enemy territory." But:
- A natural stone in enemy territory is captured only if outnumbered by 3+,
  which requires 4+ opposite-colored neighbors. On an 8x8 torus with sparse
  early-game placement, captures are rare anyway.
- A camouflage stone that survives in enemy territory **boosts the enemy's
  score** (proven in E1). So the survival is anti-strategic.
- Therefore the unique thing camo offers (deep-territory survival) is actively
  bad for the camouflager. There is no use case where this primitive earns its
  keep. It is a "feature" the ruleset describes but the strategy never wants.

---

## 2. Player Phase — Rebuttals

### R1. The arithmetic disaster of camo IS the novel content
Yes, in the positions I tested camo is mostly a self-own. But that itself is a
novel constraint: the game asks players to evaluate "which cells in enemy
territory am I willing to amplify?" and "is the threshold-deny worth the score
boost I gift the opponent?" That's a tradeoff *no analog game presents in the
same shape* — Tak walls don't radiate negative own-score, Reversi flips don't
have signed influence, Quantum TTT collapses are not a continuous score
gradient. The arithmetic shape is genuinely new even if the answer is usually
"don't use camo."

### R2. Concrete moment — threshold-denial in a tied endgame
Setup (probed): P1 score 17.88, one move from a 22.61 threshold win at cell 36.
P2 to move.
- Natural B at 36 → captured (8 P1 +1 neighbors, 0 same → outnumbered by 8).
- Camo b at 36 → survives. Cell denied. P1 score jumps to 19.78 (camo's +1
  influence boosts the 8 surrounding P1 cells), but P1 cannot complete the
  winning configuration at 36.

In a tighter board where alternative high-value cells are blocked, this
denial is the only legal way to extend the game past P1's win threshold.
NO Reversi-family game has the property that "you can occupy enemy territory
but pay a points tax to do so." This is a knob no analog game offers.

### R3. Concrete moment — camo as fence/seed
A P1 camo stone (P1@-1) placed at the boundary of P1's +1 cluster acts as a
"fence" that P2 can't easily attack with -1 stones (they'd be amplifying
the camo's value). It also seeds future P1 -1 territory. Two-phase territory
construction is not a thing in Othello, Reversi, Lines-of-Action, or Hex.

### R4. The phase-capture rule is genuinely new
Capture by phase (not owner) means a P1 camo can be captured by other P1's
+1 stones on adjacent cells. **Friendly fire is possible.** That is not a
property of any Reversi/Go/Hex variant I can name. Quantum TTT collapses
happen via classical play and don't have a "your own piece kills your other
piece" rule.

### R5. Move-space expansion changes search topology
The action space doubles (every cell has +/- placement). Even if camo is
usually wrong, the threat of camo is a real strategic object: the
opponent must compute "could opponent camo this cell to deny my plan?"
That's a new branch in tactical reading.

---

## 3. Net Novelty Verdict

The phase extension introduces *one* genuinely novel primitive: **owner-phase
decoupling with friendly-fire capture**. That is not present in Reversi,
Othello, Go, Hex, Lines-of-Action, Tak, or Quantum TTT.

However, the primitive is **strategically stillborn in the calibrated source
ruleset**: the influence/score accounting makes camouflage an almost-strictly
losing move (E1, E2). The novelty exists as a rule on paper but rarely
manifests in chosen play. The strongest case (R2 threshold denial) is real
but narrow, and on a torus with many equivalent high-value cells, even that
denial is often easily routed around (verified: P1 found another move at
cell 10 with identical 22.61 score).

So the extension is "shallow new" — formally novel, practically inert. It
adds a rule but doesn't change the game's strategic surface much. A human
would notice the extra option in the move list but quickly stop using it.

**Compared to source `c6bb58075520` (4.40/10 human novelty mean)**: the
source already has the unusual "outnumber-by-2 capture on a torus with
signed influence" hook. The phase extension layers on but doesn't earn its
weight — most games will look identical to source play with occasional
camouflage stones that the loser placed.

### Score: **5.0 / 10** on novelty

Reasoning: source is 4.40. The phase rule is genuinely a new primitive
(+1.0 raw novelty), but its strategic dead-weight subtracts most of that
gain (-0.4). Net +0.6 over source.

---

## 4. Evidence Summary

**E1 — Camo in deep enemy territory is self-defeating.**
Setup: P1 has a +1 cluster (8 stones around cell 36). P2 to move.
- Camo b at 36 (deep enemy): P1 score went 15.06 → 16.96 (+1.9). P2 got -2.83.
- No move (counterfactual): P1 = 15.06, P2 = 0.
The camo stone radiates +1 influence into 8 P1 cells while sitting on a
high-value cell that subtracts from P2.

**E2 — Camo in mild enemy territory is also negative.**
Setup: 11 moves into a game, P2 to move.
- A: P2 camo b at 36 → P2 = -11.30 (score moved -2.83 from baseline -8.46)
- B: P2 natural B at 29 → P2 = -8.45 (basically neutral)
- C: P2 natural B at 40 → P2 = -9.40
- D: P2 camo b at 29 → P2 = -10.35
The two camo options (A, D) are the worst two; both natural options dominate.

**E3 — Threshold denial via camo works but is routable.**
Setup: P1 at 17.88, one-shot win at cell 36 → 22.61 (over 22.65 threshold).
- P2 camo b at 36 blocks the win at the cell, but P1 can still play 10+ for
  the same 22.61. So the denial buys at most one tempo.

**E4 — Random games look like source games with extra noise.**
Random-policy games at seeds 1 and 7 ended in 35 and 53 steps respectively
(P1 winning both). The camo stones placed by random play scattered without
strategic intent. Visual inspection of final boards shows clusters and
captures qualitatively indistinguishable from source `c6bb58075520`.

---

## 5. Recommendation

**Do not promote phase-extended `c6bb58075520` to a flagship variant.**

Reasons:
1. The novel primitive (owner-phase decoupling, friendly-fire capture) is real
   but rarely worth using under the source's calibrated influence/score
   constants. Players will discover within a few games that camouflage is a
   trap.
2. The doubled action space adds search-tree noise without adding strategic
   richness — it expands the branching factor but most extra branches are
   strictly dominated.
3. The R2 threshold-denial scenario is the only place camo earns its keep,
   and it's narrow and often routable on the torus.

**If you want this primitive to deliver:**
- Re-tune so camouflage stones radiate ZERO influence (or greatly attenuated)
  rather than full opposite-sign influence. This makes camo a true blocker
  rather than an own-goal.
- OR raise the outnumber-capture threshold so natural stones can't survive
  in enemy territory; this would force camo as the ONLY invasion mode and
  make the primitive load-bearing.
- OR add a phase-flip mechanic (a stone can swap phase under some condition)
  so phase becomes a dynamic state, not a placement annotation. That would
  give the "complex number" framing actual strategic content.

Without one of those changes, the extension is a re-skin with a rule no one
will use. Score 5.0/10 stands.
