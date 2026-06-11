# Team 3 — Game D verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  3D **torus**, axis 4 (64 cells, every cell degree 6, all axes wrap). PLACE
  must be adjacent to an ENEMY stone (first move anywhere). **Influence**: each
  placement adds 1.098·0.797^dist to all cells within distance 2 (P1 +, P2 −),
  permanent. **Win = influence threshold**: own-cell influence sum must exceed
  **36.942** (P2 sign-corrected); a stone on net-enemy influence subtracts.
  **Capture = custodian/Othello**: bracketed enemy lines flip to your colour,
  but the line-walk **clamps at the 0..3 bounds — it does NOT wrap** the torus.
  **Ghost influence**: a flipped stone keeps its ORIGINAL (enemy) influence sign
  forever. No pie rule. Double pass = draw; super-ko; 100-step stone-count
  tiebreak.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw): **Double-pass
  DRAW in every full line** (Line 1 @ step63, Line 2 @ step65) — the board
  saturates, no enemy-adjacent empties remain, both pass. The 36.942 threshold
  was **never approached** (peaks ~+10). No decisive result occurred.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: How unreachable the win threshold is. Peak P1 score across a
  full greedy game was **+9.95** — about a quarter of the 36.94 target — and it
  *declined* to +1.25 as the board filled. The interlocking constraint plus
  ghost-flip craters cap scores far below the threshold.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `21,22,6,2,1,0,3,5,4,7,11,8,9,10,12,13,14,15,16,17,18,19,20,23,24,25,26,27,31,28,29,30,35,32,33,34,36,37,38,39,43,40,41,42,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,63`
- Plan and what happened: I drove P1 to fill an interlocked contested blob while
  P2 responded competently (also filling, also flipping). P1's score peaked at
  **+9.95** mid-game, then saturation + accumulated P2 negative influence and
  flip-ghosts dragged it down to **+1.25**. When the board filled, the
  adjacent-to-enemy constraint left no legal placements and both sides passed.
- Result (winner, end cause, plies): **DRAW** (double pass), step 63; final
  P1=+1.25, P2=−17.97 — neither near 36.94.

### Line 2 — you as P2
- Moves: full last-legal greedy line, 64 plies (drove P2's placements).
- Plan and what happened: I drove P2 with a different fill geometry to test
  whether the threshold is reachable from the second seat or via more captures.
  Same outcome: scores peaked low and the game saturated into a pass-draw. P1
  again out-scored P2 (P1=+10.86 vs P2=−11.15) but neither side could convert.
- Result: **DRAW** (double pass), step 65; threshold unreached.

### Line 3 — adversarial / novelty-stress
- Moves: `1,2,3`
- What you tried to break / stress, and what happened: I isolated the
  custodian+ghost interaction. P1@(1,0,0), P2@(2,0,0), then P1@(3,0,0)
  **flipped** P2's stone (delta `O->X@(2,0,0)`, P1=3/P2=0). But P1's score was
  only **+2.49 for 3 stones**, because the flipped cell keeps its −1.098 ghost —
  exactly the drag that, multiplied across a full game of flips, keeps the
  threshold out of reach. I also confirmed the documented no-wrap clamp on the
  custodian walk.
- Result: flip works but is ghost-penalised; this is the mechanism behind the
  game's draw-proneness.

### Additional lines (optional)
Two independent full games (P1-driven and P2-driven) plus the flip probe were
enough to establish that no reasonable play approaches the win threshold.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why): Place where your
  influence dominates and avoid feeding enemy flips; but the adjacent-to-enemy
  constraint forces every stone next to enemy negative influence, so net score
  per stone stays low. Custodian flips convert stones but plant permanent ghost
  craters, so aggressive capturing is self-defeating for the score.
- Counterplay: There is positional counterplay (suppress by sitting negative
  influence on the leader's cells; flip to convert), and unlike the parity
  games, *where* you place matters — but none of it produces a win, because the
  threshold is unreachable. The dominant outcome is a draw regardless.
- Topology/board effects on strategy: The torus removes edges (all degree 6) so
  there's no safe corner to build a clean cluster; combined with the
  enemy-adjacency rule, every region is contested, which is what suppresses
  scores. The clamp-don't-wrap custodian quirk limits flips to non-wrapping
  lines.
- Emergent concepts you'd name (or "none observed"): Ghost-crater drag (flips
  hurt your own score) and influence saturation pulling both scores toward zero.
  These are emergent but they emerge into *stalemate*, not strategy.
- Player agency: Real but futile — placement choice changes the score
  trajectory (peaks ranged ~+10, end-states varied), yet no line could break the
  threshold, so choices decide the *margin of a draw*, not the result.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior: It's the same
  influence-threshold skeleton as Game B (own-cell influence sum to a target)
  with Othello-style custodian capture swapped in for outnumber, on a torus.
  Strip the dressing and it's "interlocked influence race" — but with a target
  set so high it never resolves.
- Honest novelty assessment after arguing that case: The mechanics (torus +
  no-wrap custodian + radius-2 influence + ghost) are a genuinely different mix
  from B, but the defining experiential feature is a **broken/unreachable win
  condition** that turns every game into a saturation draw. That's not novelty,
  it's a calibration failure; the interesting parts never get to matter.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.0 — you out-score the opponent and have
  real positional choices, but you cannot win (Line 1 draw).
- P2-role experience sub-score (1-10): 2.7 — you trail on score and also cannot
  win; outcome is a draw either way (Line 2).
- Role-averaged sub-score: 2.85
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** **2** — P1 out-scored
  P2 in every line (Line 1 +1.25 vs −17.97; Line 2 +10.86 vs −11.15) with no pie
  rule to correct the first-move edge, though both games still drew.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 2.9**
- One-paragraph justification of the Overall, citing your Phase 2 lines: Game D
  has more genuine positional content than the trivial parity/connection games —
  placement choice moves the score (Line 1 peaked +9.95 before saturating; Line 2
  +10.86) and the custodian/ghost mechanics create real tactics (Line 3 flip
  penalised to +2.49 for 3 stones). But its win threshold of 36.942 is
  effectively unreachable: two independent full games, P1-driven and P2-driven,
  both ended in saturation **double-pass draws** with peaks barely over a quarter
  of the target, because the adjacent-to-enemy constraint and flip-ghost craters
  pin scores near zero. A game that cannot produce a decisive result is a
  different failure mode from the trivial races but still a failure; the richer
  mechanics lift it slightly above C/G, while the broken win condition keeps it
  well below the anchors. **Overall 2.9.**
