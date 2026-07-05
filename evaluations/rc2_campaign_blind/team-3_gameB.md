# Team 3 — Game B verdict

> Copy this template to `team-3_gameB.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game B` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid (von Neumann adjacency, no wrap). Players alternate placing one
  stone on any empty cell; PASS (id 64) is legal and two consecutive passes draw the game.
  Captures are Go-like surround: after a placement, any ADJACENT enemy group with zero
  liberties is removed. Win is Hex-style connection with ASYMMETRIC goals: P1 wins by
  connecting the y=0 edge to the y=7 edge with a chain of P1 stones; P2 wins by connecting
  x=0 to x=7. Same-tick double completion is a draw. At 100 steps, more stones on the
  board wins (equal = draw). Super-ko: any action recreating a previous position is rolled
  back and treated as a PASS (engine flags it). An influence field is rendered via
  `--values` (each placement radiates strength 0.715, decay 0.751, radius 3) but it has no
  mechanical effect on captures or the win condition — it is decorative here.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win fired twice (Line 1: P1 at ply 29; Line 2: P1 at ply 37). Double-pass
  draw fired once, in the stress line (a super-ko-converted pass followed by a real pass
  ended the game as a DRAW at ply 11). I never reached the 100-step tiebreak.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules:
  (1) A super-ko-converted pass COUNTS as the first of the "two consecutive passes" — a
  ko recapture attempt plus one opponent pass instantly draws the game. (2) Suicide is not
  checked: I placed a zero-liberty stone at (0,0) against X at (1,0),(0,1) and it was
  accepted and SURVIVES indefinitely (capture checks only run against groups adjacent to a
  new placement, and no empty neighbor exists), creating an immortal "zombie" stone.
  (3) Ghost influence verified: after my corner stone was captured, the influence at (0,0)
  read −0.36 (= +0.715 ghost + 2×−0.537 from the capturers) instead of −1.07 — captured
  stones radiate forever. Since influence is mechanically inert in this game, (3) is
  cosmetic.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,35,36,44,28,20,12,4,19,21,11,3,2,5,10,43,26,45,34,46,42,47,50,58,41,51,49,59,57`
- Plan and what happened: I built a central column (cells 27/28/36), used dual-purpose
  atari threats (19 threatened the O stone at 20 while extending my chain; 2 ataried the
  O pair 3-4 while reaching the top edge), then re-routed my descent down column 2 when
  P2 glued a blocking blob at (3,4)-(3,5)-(4,5). Scripted P2 played competent dual-purpose
  blocks: its row-5 wall (cells 43,44,45,46,47) simultaneously blocked my descent and
  built five columns of its own left-right path, and its 58/51/59 corner moves gave it
  columns 2–7 connected. The game became a pure tempo race down the west side.
- Result (winner, end cause, plies): P1 (me) won by connection at ply 29 — my chain
  (2,0)-(2,1)-(3,1)-(3,2)-(3,3)-(2,3)-(2,4)-(2,5)-(1,5)-(1,6)-(1,7) completed exactly one
  move before P2, who needed only (1,7)+(0,7). My winning move 57 doubled as the block of
  P2's path — the decisive tempo came from taking the contested cell (2,5) earlier.

### Line 2 — you as P2
- Moves: `28,36,27,35,34,42,33,41,25,43,37,45,29,44,46,40,38,53,54,62,55,61,63,12,13,21,5,14,3,11,10,19,18,22,26,1,2`
- Plan and what happened: My strategy was the "wall-under" plan: block P1's descent with a
  horizontal row-4/row-5 wall, which is simultaneously my own left-right path. It worked
  beautifully across columns 0–5 (my O wall 40–45 plus 35/36), but scripted P1 broke the
  pattern with wall-break stones (34, 33), claimed the southeast corner first (46, 54, 55,
  63 — reaching the bottom edge), and then went for the top. I capped P1's northern pushes
  on row 1 (caps 12, 14, 11 — each cap also being a cell of a potential row-1 path for
  me), but my caps were thin single stones. P1's floaters (3, 5, 13) plus the snake's
  row-3 head gave P1 a column-2 lane (2-10-18-26 linking into the snake at 27) that I
  could not block: both blocking cells (26 and 2) were 1-liberty points for me, and my
  attempted desperado block at 2 was simply captured.
- Result: P1 won by connection at ply 37 (chain from (2,0) on the top edge through
  10-18-26 into the snake down to (7,7)). I lost despite "owning" more territory —
  columns 0–6 were connected for me the whole endgame; I could never touch column 7.

### Line 3 — adversarial / novelty-stress
- Moves: `1,2,8,11,17,18,63,9,10,9,64` (plus variants `...,9,10,0,55,3` and `0,1,63,8` with `--values`)
- What you tried to break / stress, and what happened: I built a textbook ko: X 1/8/17
  vs O 2/11/18, O threw in at 9, X captured with 10 (engine removed the O stone
  correctly). O's immediate recapture at 9 was rolled back by super-ko and converted to a
  PASS with a clear `!! SUPER-KO` flag. X then passed — and the game ENDED AS A DRAW,
  proving a converted pass chains with a real pass to end the game. Variant A: O placed
  into the zero-liberty corner (0,0); the engine accepted it and the dead-on-arrival stone
  persisted for the rest of the game (no suicide rule, and capture checks never revisit
  it). Variant B: X corner stone captured by O at 1+8, then `--values` showed the captured
  stone's positive influence still radiating (corner value −0.36, not −1.07) — ghost
  influence confirmed, though inert in this game.
- Result: DRAW by double pass at ply 11 in the main stress line; two rule-edge quirks
  (zombie suicide stones, ghost influence) documented; super-ko flag works as advertised.

### Additional lines (optional)
Short probes of the opening (8-ply prefix of Line 1 with `--legal`) confirmed the action
space stays "every empty cell + pass" and that captures update the piece counts
immediately. No between-turn dynamics exist — the board only changes on placements.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  The best moves are dual-purpose: because the two goals are orthogonal (P1 needs a
  vertical chain, P2 a horizontal one), a stone that BLOCKS the opponent's crossing is
  very often a stone ON your own path. P2 blocking under P1's descent builds P2's row;
  P1 capping P2's row builds P1's column... but crucially the reverse of each is dead
  weight (P1's horizontal blocking wall does nothing for P1). A good move blocks, extends
  your span toward an open edge, AND keeps group liberties ≥2; single-stone "thin" walls
  invite the cutting/atari tactics that decided Line 2. Capture threats are tempo engines:
  my atari at 19 in Line 1 forced a save and gained a free extension.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all?
  Constantly. When P2's blob blocked my column-3 descent in Line 1, re-routing down
  column 2 while taking the contested cell (2,5) punished the blob's slowness. When I
  laddered along row 4 in planning, the refutation was that every P2 block was a row-5
  path cell for P2 — so I abandoned that plan. In Line 2, my thin row-1 caps were
  punished by the 10/18/26 lane and double-atari cuts. Ignoring the opponent for even one
  move near the end loses the race by exactly that tempo (Line 1 was decided by one).
- Topology/board effects on strategy: Orthogonal-only adjacency makes diagonal stones
  non-connecting for BOTH sides, so unlike Hex there is no "cannot be blocked" theorem —
  full walls really seal (my row-1 cap analysis), and the game can rationally end in
  mutual blockade (double-pass draw is reachable from real play). Edges are
  capture-friendly (fewer liberties) which makes the four corner regions the sharpest
  battlegrounds — the southeast corner fight decided Line 2.
- Emergent concepts you'd name (or "none observed"): "Dual-purpose wall" (block that is
  also path), "cap race" (defender's caps accumulate into the defender's own crossing
  line), "dead-weight block" (a block orthogonal to your own goal), "desperado block"
  (1-liberty blocking stone that only delays by one capture tempo), "zombie stone"
  (suicide placement that persists — could theoretically deny a path cell forever for one
  move, though I found no line where it was better than a normal block).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Agency is very high. All three results traced to
  identifiable choices: my contested-cell timing won Line 1; my thin caps and late corner
  contest lost Line 2; the draw in Line 3 was manufactured deliberately. There are no
  between-turn dynamics — every board change is a chosen move.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is Gonnect (Go with a connect-opposite-sides win) crossed with Gale/Bridg-It's
  assigned crosswise goals: Go's surround capture + super-ko on a square orthogonal
  board, Hex/Bridg-It's edge-connection win with P1 top-bottom and P2 left-right. Every
  individual mechanic — placement, surround capture, super-ko, connection goal,
  double-pass draw — exists verbatim in the Go/Gonnect/connection-game family. The
  influence field is inert, so it cannot claim novelty; the "quirks" (zombie stones,
  ghost influence, ko-pass-draw) read as edge-case behaviors rather than designed
  mechanics.
- Honest novelty assessment after arguing that case: The combination is nonetheless not
  any single prior game: Gonnect gives both players the SAME goal (either pair of sides),
  while the asymmetric crosswise goals here change the strategy space materially — the
  dual-purpose-wall economy (your block is your path, but only in one orientation) is a
  genuinely distinct and elegant tension I have not experienced in Go, Hex, or Bridg-It
  proper. Novelty is real but incremental: a well-chosen recombination, not a new
  mechanic.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — I do not recognize this as a specific game I have
  evaluated before; the strong structural resemblance to Gonnect/Bridg-It is argued in
  Phase 4 from first principles, not from recall of a prior run or score.
- P1-role experience sub-score (1-10): 4.8
- P2-role experience sub-score (1-10): 4.2
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 2 — P1 won both decisive lines
  (including against my full attention as P2 in Line 2), and the first-move initiative
  let P1 dictate which corner fight mattered while P2's blocking duties always ran one
  tempo behind.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.5**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  This game produced the most engaged play I can ask of a 29–37 ply session: Line 1 was
  a genuine one-tempo photo-finish decided by a contested dual-purpose cell, and Line 2
  was a strategically legible loss — I could reconstruct exactly which of my capping
  choices left the column-2 lane open, which is the signature of a deep game rather than
  a chaotic one. Captures, connection racing, and tempo interlock cleanly; the rules are
  short but the tactics (atari-for-tempo, thin-wall cuts, cap races) emerge unforced.
  It loses points for incremental novelty (a Gonnect/Bridg-It recombination, Phase 4),
  a perceptible P1 tilt (fairness 2), and edge-case blemishes (zombie stones, the
  ko-pass instant draw) that a polished design would clean up. Anchoring down against
  the 4.375 top anchor but above R8's 4.10: 4.5.
