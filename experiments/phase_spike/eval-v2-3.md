# Eval v2-3 — 4-Phase Complex (Round 3 Spike) — Novelty Adversary Angle

**Evaluator:** evaluator-3
**Game:** `phase_game_v2.py` (4-phase extension of `c6bb58075520`)
**Focus:** novelty axis — does the 4-phase design add something the source didn't have?

---

## Mechanical recap (verified)

- 8×8 torus, von-Neumann adjacency (4 neighbors).
- 4 phases at the cardinal points: N (0°), E (90°), S (180°), W (270°).
- Stones radiate `(cos φ, sin φ) * 0.9323` at self plus `* 0.5097` at radius-1 neighbors.
- Player score = sum over **own** cells of x-component (P1) or −x-component (P2). E and W stones contribute **0** to either score because their flux is on the y-axis.
- Capture rule: stone at φ dies if Σ over occupied neighbors of `−cos(φ − φ_n) > 2`. Self-aligned −1, orthogonal 0, anti-aligned +1.
  - N ↔ S: anti-aligned (lethal).
  - E ↔ W: anti-aligned (lethal).
  - N/S ↔ E/W: orthogonal (no interaction).
- Win at score > 22.6453. Action space = 64 × 4 + 1 = 257 (vs 65 in source).

---

## ADVERSARY — "this is just the source with extra paint"

### A1. Greedy never plays E or W
Empirical: in 20 self-play games where each side picks the move maximizing 1-ply (own_score − opp_score) with win-bonus, the phase distribution was:

```
phases used = {'N': 240, 'S': 220, 'E': 0, 'W': 0}
P1 wins:  20 / 20
```

E and W are never selected by a competent local optimizer. The 192 extra "actions" added to the action space (going from 65 → 257) are pure structural overhead — they exist in the encoding but are never reached by best-response play.

### A2. The greedy mirror line is identical to the source
Hand-played greedy mirror (P1 N row 3, P2 S row 4, then second-row pile-on) reaches:

```
move 21: P1 21.660, P2 19.777   (P1 to win on move 23 with cell 21 N)
```

This is the **same** "tempo-1 wins on the row-orbit" pattern that team-12's source eval flagged as the killer flaw of `c6bb58075520`. Adding two new phases has not changed the dominant line at all.

### A3. The E/W axis is a sideshow
Because E and W stones contribute zero to both scores, *placing one is a strict score concession*. In the pre-game position with `P1 N at {19,20,21,27,29}` and P2 to move:

```
Top 15 P2 moves are all "S far away" (cell 50–63 region), value −5.65 to −7.53.
First non-S move appears below rank 15.
```

The "secondary axis" never triggers in any line that doesn't first lose the main race. By the time you'd want a capture-immune blocker, you've already conceded the tempo.

### A4. Action-space inflation is just RL/MCTS friction
Going from 65 to 257 actions multiplies branching factor by ~4 with no compensating strategic depth. For any learning agent (MCTS, AlphaZero-style), the policy head now has to resolve 4 phases per cell when 2 of them (E/W) are essentially never explored on policy. That's pure overhead — equivalent to handing a Go engine a "rotate stone 90°" no-op action.

### A5. Closest-known-game analogy is unchanged
The source eval named **Tumbleweed** as the closest analog. The 4-phase variant does **not** make that analogy weaker; if anything it makes it stronger because the strategic kernel is identical (build a torus row, win by tempo). The E/W axis is decorative — it does not connect to the score axis at all (orthogonal by construction). Compare: this is exactly the kind of "add an irrelevant dimension" move that is commonly proposed and commonly rejected as non-novel.

### A6. The "elegant orthogonality" is a self-defeating design
The author's framing is that "E/W are true neutral occupiers — capture-immune from N/S." But neutrality means *they don't help you score*. In a threshold-race game, this is structurally a tempo loss. There is no scoring-related reason to ever play one. The capture-immunity is a defense against an attack that is itself irrational (no one wants to capture E because no one would play E).

---

## PLAYER — concrete positions where 4-phase is meaningfully different

### P1. The capture-immune permanent denial

**Position:** P1 has N stones at cells 20, 27, 29 (three of the four neighbors of cell 28). P2 to move.

```
. . . . . . . .
. . . . A^ . . .
. . . A^ . A^ . .
. . . . . . . .
... (rest empty)
```

Cell 28's two empty neighbors are 36 (and the fourth, 21, is adjacent to row 2). Score state: P1 = 2.797, P2 = 0.

P2's options at cell 28 by phase (engine-verified):

| phase | result | P1 score | P2 score | captured? |
|-------|--------|----------|----------|-----------|
| N | self-harm (P2 plants enemy flux on own cell) | 4.222 | −2.358 | no |
| E | persists, blocks cell 28 permanently from P1 | **2.797** | −1.426 | no |
| W | symmetric to E | 2.797 | −1.426 | no |
| S | captured immediately (3 anti-aligned > 2 threshold) | 2.797 | 0.000 | **yes** |

**Two-move continuation (P2's perspective):**

- P2 plays S → captured → P1 plays N at 28 next turn → final P1 = 6.580, P2 = 0 (P1 leads by 6.58).
- P2 plays E → persists → P1 forced to play elsewhere (e.g. 45 N) → final P1 = 3.729, P2 = −1.426 (P1 leads by 5.16).

**E saves P2 ~1.4 points** vs S in this contested cell. That's a non-trivial fraction of the 22.65 threshold and is a strategic primitive that does not exist in the source game (which has only one capture phase).

**This is a position where E is uniquely the BEST move** if you've been forced to spend a stone in this contested cell.

### P2. A new capture geometry: outnumber threshold flips by phase

In the source (`c6bb58075520`), capture is "≥2 enemy neighbors." Here, capture is "Σ −cos(Δφ) > 2." With four neighbors:

- Source: 2 enemies suffice — capture is **trivially easy**, leading to the team-12 finding "any P2 stone in von-Neumann reach of two P1 stones is sacrifice-bait."
- 4-phase variant: 2 anti-aligned neighbors give exactly 2 (= threshold, not > threshold) → **survive**. You need 3+ anti-aligned to capture.

Engine-verified (cell 28 with 2 N at 27, 29; P2 plays S):
```
2 N nbrs: P2 S at 28: P1 1.865 → 0.914  P2=−0.018  captured?=False
```

This **raises the capture threshold** versus the source. Combined with E/W being capture-immune from the N/S axis, P2 can defend cells that would have been instant losses in the source. The "sacrifice-bait" pattern that doomed the source's strategic depth is **mitigated** in the 4-phase variant. That is a real change to the strategic character.

### P3. E vs W mini-game on the secondary axis

E and W *do* mutually capture each other on the same threshold. If both players ever build E/W structures, a parallel mini-Reversi-like contest arises that doesn't affect either player's score but does affect *which player gets to occupy a key flux cell on the main axis*. Engine-verified:

```
E stone at 28 with 3 W stones around it: captured (state 0)
```

So if P1 plays E to deny a cell, P2 can play 3 W at the surrounding cells to liberate it (at the cost of P2's own moves, of course). A second axis of conflict that doesn't exist in the source.

### P4. Phase-decoupled-from-owner enables anti-stones for setup
Each player can place any phase. P1 can place an S stone (which radiates −x and *helps* P2's score) — irrational by itself, but in the source the corresponding move (place an enemy-color stone) doesn't even exist. Here it's legal. This opens the door to (rare but possible) sacrifice motifs:

- P1 places S at a cell next to a future P2-target → gives P2 capture-fodder if P1 has 3 N nearby. Engine-verified: P1@S at 28 with 3 N around it → S captured, cell 28 returns empty. P1 has consumed P2's potential placement target while also losing its own stone.

This is technically possible but not yet found to be on the optimal frontier.

---

## Net novelty vs source `c6bb58075520`

The source's signature emergent dynamic was:
1. **Active capture** — 2-neighbor outnumber rule punishes adjacency aggressively.
2. **Signed influence** — single global field where +/− phase is fixed by ownership.
3. Result: optimal play collapses to "build a torus orbit, win by tempo." Novelty 4/10.

The 4-phase variant changes:
1. **Capture threshold rises** (need 3, not 2, anti-aligned in the symmetric case).
2. **Phase decoupled from ownership** — anti-stones are legal but rarely rational.
3. **E/W introduce a second orthogonal axis** with mutual-capture but score-neutrality.
4. **Capture-immune permanent denial** is a new strategic primitive (Player P1 above).

Of these, (1) and (4) are real strategic additions. (2) and (3) appear novel but in greedy play don't trigger.

**Critical concession to the Adversary:** the 4-phase variant retains the source's tempo-race kernel. Greedy mirror still wins for P1 in roughly the same 21–23 moves with the same 100% bias. The new mechanics affect the **margin** (sub-optimal continuations), not the **dominant line**.

**Critical concession to the Player:** the source's killer flaw — "any stone in 2-neighbor reach of an enemy is sacrifice-bait" — is genuinely relaxed here. The capture-immune E/W stones plus the higher de-facto capture threshold give the second player at least one defensive primitive that didn't exist in the source. It probably doesn't fix the tempo asymmetry, but it changes the texture of contested play.

---

## Verdict on novelty

The 4-phase extension is **a non-trivial mechanical addition that hits a single concrete new strategic primitive (capture-immune denial)** but **fails to escape the source game's dominant tempo-race motif**. In greedy / 1-ply / 2-ply play the new dimension is invisible. In hand-constructed contested-cell positions it produces a real distinction worth ~1.4 points.

This is exactly the "mechanical novelty without emergent novelty" pattern team-12 flagged for the source — except the source scored 4/10 because its mechanical novelty was at least *strategically central* (the capture rule is what makes the row-orbit work). Here, the mechanical novelty (E/W) is on a strategic side-channel that competent play avoids.

### Score: **4/10** on novelty (same as source)

Reasoning:
- +1 for the capture-immune-denial primitive (genuinely new strategic consideration).
- +1 for the higher de-facto capture threshold (changes the safety geometry).
- 0 for the E/W secondary axis — it exists but is dominated.
- 0 for the action-space inflation — pure structural cost.
- The kernel strategic character (build torus orbit, win by tempo, P1 dominates) is **unchanged**, so the source's novelty score (4) is the right reference and there's no clear reason to move it.

Compared to the source's "active capture + signed influence" which at least *forced* the dominant strategy, 4-phase's "orthogonal score axis" is *optional* — and optional means dominated, in a tempo race.

---

## Recommendation

1. **Do not promote 4-phase as a novelty win over the source.** The greedy phase histogram (240 N, 220 S, 0 E, 0 W) is decisive: under any locally-rational play the new axis is invisible.
2. **If keeping 4-phase mechanics, pair them with a rule that punishes pure-N/pure-S play** — e.g. "score also includes y-axis component for the player who placed more E than W stones." That would force E/W into the score race and convert the orthogonal axis from decoration to mandatory bidding.
3. **Consider asymmetric capture thresholds** — e.g. capture threshold 1 on the main axis and 2 on the secondary. That would reproduce the source's punishing capture geometry on N/S while preserving the secondary axis as a safe haven.
4. **The fundamental tempo flaw inherited from the source remains.** Until something resolves the first-mover-wins-the-row-orbit dynamic, no amount of phase decoration will deliver the strategic depth/replayability gains the spike is reaching for. Recommend de-prioritizing 4-phase complexity in favor of fixing the kernel.

---

## Summary table

| Adversary point | Status |
|---|---|
| Greedy never plays E/W | **Confirmed** (240/220/0/0 over 20 games) |
| Tempo race kernel unchanged | **Confirmed** (P1 wins 20/20 in ~23 moves) |
| Action-space 65→257 is overhead | **Confirmed** for greedy; possibly mitigated for deep-search agents |
| E/W is decorative | **Mostly confirmed** — only triggers in contested-cell sub-games |

| Player point | Status |
|---|---|
| E uniquely best when surrounded by ≥3 anti-aligned | **Confirmed** (~1.4-pt edge) |
| Capture threshold raised vs source | **Confirmed** (2 N nbrs: S survives) |
| E vs W secondary axis exists | **Confirmed** (3-W kills E) |
| Anti-stones (mismatched-phase placement) | Confirmed legal; not seen on-policy |

**Final novelty score: 4/10** — same as source, with mechanical additions that don't move the strategic-novelty needle.
