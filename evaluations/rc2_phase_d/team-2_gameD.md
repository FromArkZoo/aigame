# Team 2 — Game D verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words:
  A 3D **torus**, axis_size 4 (64 cells, every cell degree 6, all axes wrap).
  Players alternate **PLACE** (empty cell, must be **adjacent to an ENEMY
  stone**; first-move-anywhere while you have none) or PASS. Capture is
  **custodian/Othello**: after placing, each axis-aligned line of consecutive
  enemy stones bracketed by your stones flips to you — but the line-walk
  **clamps at the 0..3 bounds and does NOT wrap** even though adjacency does.
  Every placement also lays **influence** (strength 1.098, decay 0.797, radius
  2); flipped stones keep their **original-sign** influence forever (ghost).
  **Win = influence threshold**: own-cell influence sum > **36.942** (P2 sign-
  corrected); a stone on net-enemy influence subtracts. Turn-limit (100)
  tiebreak = more stones; double-pass → immediate draw.
- What actually ends the game / frequency: in practice the threshold is **never
  reached** — I filled the board greedily to 61 stones and the scores were
  **P1 −0.7, P2 −19.9** (vs a +36.942 target). So games actually resolve by
  turn-limit stone count or, very often, by **double-pass draw** once both sides
  run out of enemy-adjacent empties. I confirmed the double-pass draw directly.
- Surprises: (1) The **headline win condition is effectively dead** — parasitic
  placement keeps every stone next to enemies (subtracting), and custodian
  flips poison their own cells via ghost influence, so own-score hovers near 0
  or goes deeply negative; 36.942 is unreachable with legal play. (2) Capturing
  ALL adjacent enemies can **strand you** (no enemy left to place beside →
  forced pass). (3) Torus adjacency wraps but custodian capture doesn't — an
  internal inconsistency.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: greedy custodian stone-race (full sequence via engine-verified driver;
  opens `21,22,…` filling the torus with custodian flips).
- Plan and what happened: I (P1) placed beside enemy stones to set up Othello
  flips, steadily converting P2 lines. The board filled to 61 stones with me
  ahead **34–27** on stones, but **neither score came within 37 of the
  threshold** (P1 −0.7), and the position stalled toward a turn-limit/double-
  pass ending rather than a clean win.
- Result: **P1 stone-lead 34–27, no threshold win — heads to turn-limit/draw.**

### Line 2 — you as P2
- Moves: `21,22,18,20`
- Plan and what happened: I (P2) set up an Othello sandwich — with P2 stones at
  (2,1,1) and (0,1,1) bracketing P1's (1,1,1) along d0, my placement at (0,1,1)
  **flipped (1,1,1) to P2**. Material swung to **P2 3 – P1 1**. This is the real
  tactical layer: line-flips, not influence, move the needle.
- Result: **P2 material swing (3–1) via custodian; game continues.**

### Line 3 — adversarial / novelty-stress
- Moves: full-board greedy fill, then `21,22,64,64`.
- What I tried to break / stress: I tested whether the stated objective is
  reachable and whether a stone leader can actually win. The full board scored
  **P1 −0.7 / P2 −19.9** (threshold 36.942 never approached). I then forced a
  double pass and the engine ruled **DRAW** — meaning even a side leading on
  stones can be denied a win when both get stuck and must pass.
- Result: **threshold unreachable; double-pass → DRAW** (a leader can be drawn
  out of a win).

### Additional lines (optional)
Custodian sanity `21,22,23`: P1's placement at (3,1,1) flipped P2's (2,1,1)
(bracketed by P1 at (1,1,1)) — capture verified, score +2.49.

## Phase 3 — Joint strategic analysis

- Core tactical loop: place next to enemy stones to set up custodian flips that
  convert enemy lines (gaining stones), while avoiding capturing yourself into a
  stranded, pass-forced position. Influence is almost irrelevant to the result.
- Counterplay: real at the capture level — both sides flip lines (Lines 1–2),
  and over-capturing strands the aggressor. But there's little counterplay
  toward the *stated* objective because no one can reach it.
- Topology effects: the torus gives uniform degree-6 cells (no safe corners),
  but custodian's no-wrap clamp means captures still behave like a bounded
  4×4×4 box — the wrap helps adjacency/placement, not capture.
- Emergent concepts: Othello line-flips, capture-yourself-stranded, ghost-
  poison; the influence/threshold layer is inert in practice.
- Player agency: moderate at the stone level (flips are chosen), but the game's
  declared goal is decided by neither player — it's simply never met, so the
  outcome defaults to stone count or a draw.

## Phase 4 — Novelty adversary

- Strongest re-skin case: strip the dead influence layer and it's **3D Othello
  on a torus with a parasitic placement rule** — custodian capture is directly
  Reversi, and a stone-count finish is a majority game.
- Honest novelty assessment: low. The interesting-sounding combination (torus +
  influence-threshold + custodian + ghost) collapses because the influence
  threshold can't be met, leaving a Reversi-flavoured stone-race. The genuinely
  novel parts (ghost-poison, threshold) are exactly the parts that don't
  function. The custodian-no-wrap-on-a-torus is a curiosity, not a feature.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.4
- P2-role experience sub-score (1-10): 3.2
- Role-averaged sub-score: 3.3
- **Fairness perception (1-5):** 2 — Leaning P1-favored: greedy play gave P1 a
  consistent stone lead (34–27) from first-mover + flips, though draws are
  common and the threshold is moot for both.
- **Overall (1-10, anchored): 3.3**
- One-paragraph justification: D's stated objective — an influence sum above
  36.942 — is **practically unreachable**: I filled the board and scores were
  −0.7 and −19.9, and intertwined parasitic placement plus ghost-poisoned
  captures keep per-stone scores near zero (Lines 1, 3). That guts most of the
  game's machinery and leaves a Reversi-style stone-race that frequently
  **draws by forced double-pass** even when one side leads (Line 3). The
  custodian capture is a genuine, working tactical layer (Line 2's P2 flip), and
  it lifts D above a non-game, but a dead headline win condition, heavy draw-
  proneness, and a torus whose capture ignores the wrap are serious coherence
  faults. Below the clean stone-race G and the reachable-threshold B; I anchor
  it at 3.3.
