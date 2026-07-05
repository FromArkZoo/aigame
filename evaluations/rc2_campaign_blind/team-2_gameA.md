# Team 2 — Game A verdict

> Copy this template to `team-2_gameA.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game A` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  9×9 grid with 17 holes in a Sierpinski-carpet pattern (64 active cells). Players alternate placing stones; after your first stone every placement must be orthogonally adjacent to one of your own stones (the "anywhere" right re-arms if you ever drop to zero stones). After each placement, Othello-style custodian capture runs along the two axis lines from the placed cell: a contiguous enemy run terminated by your own stone flips to you (holes and empty cells break the line — engine-verified). Win conditions are Hex-like and asymmetric: P1 connects the x=0 face to the x=8 face, P2 connects y=0 to y=8, via orthogonal paths of own stones. Two consecutive passes = draw; at 100 steps, more stones wins. Super-ko exists in the rules but can never fire here: stones are only ever added or recolored, so no position can repeat.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win in 3 of 4 lines (plies 17, 18, 28); one engineered double-pass draw in the mechanics-stress line. Turn-limit tiebreak never came close (rule read but not observed).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) Mobility is far tighter than the rules suggest — at ply 5 of one line P1 had exactly 3 legal placements, and one blob had only 2; holes plus the adjacency constraint choke growth severely. (2) Custodian capture only fires from the newly placed stone, so a pre-existing sandwich (my (5,2)-O-(7,2) in Line 3) never resolves. (3) The flip delta is flagged cleanly by the engine (`X->O@(6,2)`), and flipping a player's last stone verifiably re-arms first-move-anywhere (P2's legal actions jumped to all 56 empty cells + pass). (4) A single pass alternating with opponent moves does NOT end the game — only two consecutive plies of passes.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `22,6,23,15,24,7,25,8,26,5,21,4,20,3,19,2,18`
- Plan and what happened: I opened on the degree-2 "tunnel" cell (4,2) and raced row 2, which is both P1's shortest path and (once complete) a total cut of the board. Scripted P2 answered with a column-6 wall but anchored it at the wrong row ((6,0) instead of taking the (6,2) intersection), so I broke through the wall's line at (6,2) on ply 5, sealed P2's eastern pocket by taking (8,2) before P2's wall could turn south, and then completed row 2 westward unopposed. P2's late western pivot ((5,0),(4,0),(3,0),(2,0)) could never cross my completed row.
- Result (winner, end cause, plies): P1 win, connection (full row 2), 17 plies.

### Line 2 — you as P2
- Moves: `22,24,23,15,14,6,21,33,20,42,29,51,38,60,47,69,56,78`
- Plan and what happened: P1 (scripted competently) played the same strong (4,2) tunnel opening that won Line 1. As P2 I executed the informed counter-wall: take the intersection of P1's row with a clean column immediately ((6,2) on ply 2), extend to the near edge before P1's seal race arrives ((6,1) ply 4, (6,0) ply 6 — P1's counter-seal via (5,2),(5,1),(5,0),(6,0) arrives ply 9, three plies too late), then stroll the column south. P1's tries — the north seal, a western row completion, and a southern reroute down col 2 — all failed: my column, once complete, is itself a total cut, and every horizontal bracket against it is immune (holes at (7,1),(5,3),(5,5),(7,7) shield it; the (6,6) bracket needs cells P1 could only reach around ply 19+).
- Result: P2 win, connection (full column 6), 18 plies.

### Line 3 — adversarial / novelty-stress
- Moves: `22,6,23,7,24,8,25,17,21,26,20,35,19,34,18,33,29,15,38,42,47,51,56,60,57,69,58,78`
- What you tried to break / stress, and what happened: I stressed the custodian mechanic, which never fired in normal lines. P2 blocked at (6,0), deliberately let P1 punch through at (6,2), then wrapped around through (8,0),(8,1),(8,2),(8,3),(7,3) to (6,3), and on ply 18 played (6,1): the engine flipped (6,2) X→O exactly as the custodian rule promises (delta `.->O@(6,1)  X->O@(6,2)`), breaking P1's completed-in-the-middle row and welding P2's column shut. Three further findings: P1's (7,2) was left permanently isolated (its neighbors are a hole, an O, and O-territory); the pre-existing X-O-X sandwich on row 2 never resolved (flips fire only from the placed stone); and the custodian walk west from (6,3) stopped dead at the (5,3) hole. In a companion micro-line (`0,9,1,81,2,81,11,81,20,81,19,81,18,60,81,81`) I flipped P2's only stone to zero — the engine re-armed place-anywhere (57 legal actions) — and confirmed alternating single passes don't end the game but a double pass draws it.
- Result: P2 win, connection (column 6), 28 plies; micro-line ended DRAW by double pass at ply 16.

### Additional lines (optional)
Opening probe (`4,6,3,15` + reachability analysis): a center-top opening (4,0) loses outright to P2's (6,0) column wall — P1's snake can never cross the growing wall, and every col-6 cell from (6,2) down is reached by the wall first. This probe is what revealed the wall-race structure of the game.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  A good move advances your own cut-line (a completed row for P1 / column for P2 is simultaneously a win and an absolute barrier) while denying the opponent's. Because every placement must touch your blob, tempo is everything: you cannot defend a distant cell, so good moves are the ones that arrive at contested intersections exactly one ply before the opponent. The four hole-protected "tunnel" cells ((4,2),(4,6),(2,4),(6,4)) and the four crossing cells each player has through the central band (P2 must cross y=4 at x∈{0,2,6,8}; P1 must cross x=4 at y∈{0,2,6,8}) are the whole strategic map.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Strongly. When scripted P2 anchored its wall at the wrong row (Line 1), taking the wall's line-intersection cell punished it immediately and permanently. When P1 opened with a committed tunnel cell (Line 2), the informed counter-wall — intersection first, near-edge seal second, column stroll third — refuted it by exactly one ply at every contact point. The game is almost entirely about responding to the opponent; pure racing only wins against a misplaced block.
- Topology/board effects on strategy: The fractal holes do real work: they create degree-2 tunnel cells that are unflippable and unbypassable, they grant flip-immunity to most lane cells (a bracket needs both flanking cells to exist), and combined with walls they create "seal pockets" that entomb a blob forever (P2's 5-stone eastern pocket in Line 1, P1's whole position in Line 2). A completed line is a perfect cut because orthogonal adjacency admits no way around.
- Emergent concepts you'd name (or "none observed"): "tunnel cells" (hole-flanked degree-2 chokepoints), "wall-win duality" (your winning path doubles as total blockade), "seal pockets" (adjacency growth + holes let walls permanently entomb a blob), "wrap flips" (captures require presence on both sides of an enemy line, so they only occur after an encirclement — rare but game-breaking when they land, as in Line 3).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decided everything — the engine is deterministic with no between-turn dynamics. But agency is front-loaded: the first ~6 plies essentially decide the game (one misplaced wall anchor in Line 1 was unrecoverable), and comeback mechanisms are almost absent since flips are so hard to assemble.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  Every component is borrowed: Hex/Crossway's asymmetric edge-connection goals, Othello/Hasami-Shogi custodian capture, Go's super-ko, and a Sierpinski-carpet board (a stock "fractal variant" gimmick). One can argue it is simply "Hex with Othello captures on a holey board," and that the adjacency-growth rule is Twixt/Trax-style chain-building — so the whole is a four-way mashup with no new atomic mechanic.
- Honest novelty assessment after arguing that case: The mashup produces one genuinely non-obvious interaction: the adjacency-growth constraint nearly *neutralizes* the custodian mechanic (you can't reach the far side of an enemy run without having already encircled it), turning a capture game into a pure tempo/blocking race — and the fractal holes then decide which cells are even theoretically flippable. "Your win-path is also a perfect wall" is a real emergent identity that Hex (hexagonal, two-color crossing possible) does not have. But no single mechanic is new, the super-ko rule is provably dead weight here, and the emergent game likely collapses to an informed second-player counter-wall. Moderately novel combination, not a novel game idea.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — I recognize the component genres (Hex, Othello, Sierpinski boards) but not this specific game, and I recall no prior score for it.
- P1-role experience sub-score (1-10): 4.0
- P2-role experience sub-score (1-10): 4.5
- Role-averaged sub-score: 4.25
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 4 — P2 moves with full information about P1's committed, adjacency-chained opening, and my Line 2 counter-wall beat the strongest P1 opening I could find by exactly one ply at every contact point, while P1's only win (Line 1) required a scripted P2 mis-anchor; P1's nominal one-ply tempo edge never survives an informed reply.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.1**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The game delivers real strategic content: Line 1 (P1 win, ply 17) and Line 2 (P2 win, ply 18) are mirror demonstrations that intersection-tempo and edge-sealing genuinely decide games, and Line 3's engineered wrap-flip (ply 18, X→O@(6,2)) shows the capture mechanic can shatter a wall when encirclement is achieved. The fractal topology contributes actual strategy (tunnels, immune lanes, seal pockets), not just decoration. Against that: the custodian mechanic is nearly inert in honest play (zero flips in both competitive lines), the super-ko rule is provably vestigial, comebacks are structurally rare, and the informed counter-wall looks close to a second-player cookbook win, which caps replay depth. That is better than R21/R20 (3.69/3.73) because the interaction is real and the topology earns its place, and about at R8 (4.10) but clearly below the R19 ceiling since one mechanic is dead weight and the opening may be close to solved: 4.1.
