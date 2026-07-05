# Team 1 — Game B verdict

> Copy this template to `team-1_gameB.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game B` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid, free placement on any empty cell (no adjacency
  constraint), Go-style surround capture: after your placement, adjacent
  enemy groups with zero liberties are removed. Crucially there is NO
  self-capture check: suicide placements are legal and the zero-liberty
  stones STAY on the board ("undead" stones — engine-verified). Wins are
  Hex-style asymmetric connections with orthogonal path adjacency: P1
  connects row 0 to row 7, P2 connects column 0 to column 7. Passing is
  legal; two consecutive passes draw; positional super-ko rolls repeating
  placements back into passes; 100-step limit with most-stones tiebreak.
  An influence field exists but is provably irrelevant to the result
  (connection is the only win path), including its documented "ghost"
  quirk, which I verified numerically: after my corner stone was captured,
  cell (0,0) read −0.36 = the captured stone's +0.715 ghost plus the two
  capturing stones' −1.074, instead of the −1.074 a live-only field would
  show.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection wins twice (Line 1: P2 at step 48; Line 2: P2 at step 34);
  double-pass draws in both stress games (the ko demo — where a super-ko
  rollback itself supplied the first pass — and the ghost-influence probe).
  The turn-limit tiebreak never fired, and my endgame analysis found it is
  structurally hard to reach: a player losing on stone count can fill the
  board, forcing consecutive passes and a draw before step 100, unless
  captures keep empty cells alive — a significant loophole.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) Suicide stones persist at zero liberties and are then
  PERMANENT — capture only triggers when a placement is adjacent to a
  zero-lib group, and no placement can ever be adjacent to a group with no
  empty neighbors; my Line 2 opponent exploited this with an "undead wedge"
  in the only gap of my wall (it failed only because I had a detour).
  (2) Classic Go ko emerges from positional super-ko, but the rolled-back
  recapture counts as a PASS toward the double-pass draw — a ko fight can
  literally terminate the game as a draw (verified: my recapture was rolled
  back, opponent passed, game over).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `28,36,35,44,43,27,51,37,29,45,38,46,47,59,60,58,39,61,52,54,53,62,55,63,34,18,26,17,25,16,20,12,21,13,22,14,23,15,19,11,10,9,8,1,2,3,0,2`
- Plan and what happened: I raced a center column, fought a running battle
  around his row-4 core, and won the central semeai spectacularly — his
  9-stone center group self-sealed at zero liberties. But the scripted P2's
  blocking stones were relentlessly dual-purpose: every stone he used to
  block my top-row access was also a link in his own left-right snake.
  In the endgame I missed that my cutting pair (2,0),(2,1) was in self-atari
  (his (3,0) captured it, snapback-style) and his wall regained liberties;
  at ply 48 he completed x=0→x=7 through the very stones that had been
  "blocking" me.
- Result (winner, end cause, plies): P2 wins by connection at step 48 of
  100; 23 stones v 22. An honest loss — my one-purpose attack stones lost
  the tempo war against his two-purpose defense.

### Line 2 — you as P2
- Moves: `28,32,20,33,12,34,4,35,36,44,37,45,38,46,39,47,43,51,42,50,41,49,40,48,43,42,52,53,60,61,59,58,43,52`
- Plan and what happened: Applying the lesson from Line 1, I built a
  staircase wall (row 4 for x≤3, row 5 for x≥4) where every stone was
  simultaneously my left-right path and a block of his column. His column
  sidesteps (37, 38, 39) each got met by a wall stone until his whole group
  was sealed with no route to row 7 — his connection was dead by ply 16.
  His counterplay: wedging the staircase's single diagonal gap at (3,5).
  I captured his first wedge with a ladder that died on the board edge
  (4 stones), his re-wedge in a snapback (1 stone), and his third wedge —
  placed at zero liberties as a permanent undead blocker — failed because
  my path detoured through the territory his dead ladders had vacated.
- Result: P2 (me) wins by connection at step 34 of 100; 17 stones v 9.

### Line 3 — adversarial / novelty-stress
- Moves: `20,35,27,37,29,44,36,28,36,64` (ko/super-ko) and `0,1,63,8,64,64`
  (ghost influence + suicide corner probes)
- What you tried to break / stress, and what happened: (1) Built a textbook
  Go ko: my throw-in at (4,4) was captured by his (4,3); my immediate
  recapture was flagged SUPER-KO, rolled back, and counted as a pass; his
  pass then ended the game as a draw — ko fights here can end the game
  outright. (2) Verified suicide-into-corner: a stone placed with zero
  liberties survives (no self-capture) and is permanently uncapturable once
  no empty cell borders its group. (3) Verified ghost influence numerically
  (see Phase 1). (4) Verified double-pass termination in both games.
- Result: DRAW by double pass in both (steps 10 and 6); every quirk behaved
  exactly as documented.

### Additional lines (optional)
Race-count analysis (shortest-completion BFS, which I re-derived
independently and used to steer both main lines) confirmed the endgames:
in Line 1 my connection cost was infinite at ply 47 while his was 1; in
Line 2 his was infinite by ply 16. I also identified analytically — though
did not fully play out — the fill-out loophole: with both connections dead,
the side losing the stone-count tiebreak can fill the board and force a
double-pass draw before step 100, making the tiebreak nearly unreachable
between competent players.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Dual-purpose placement is everything: the winning stones in both decisive
  lines simultaneously extended the owner's connection and blocked the
  opponent's. Free placement makes single-purpose moves a tempo loss, so a
  good move is found by overlaying both players' cheapest completion paths
  and taking a cell on the intersection. Around contact, standard Go
  reading (liberties, ladders, snapbacks, semeai counts) decides whether
  walls hold.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Deeply. My Line-1 loss was
  precisely a failure of counterplay bookkeeping (a missed self-atari); my
  Line-2 win was built from punishments: two of his wedges died to a ladder
  and a snapback, and his sealed core was worthless. Blocks that are not
  backed by liberty counts get captured; blocks that are backed become
  paths.
- Topology/board effects on strategy: Orthogonal-only adjacency (for both
  movement and winning paths) means diagonal "bridges" are not connections
  — walls must be solid, and a staircase wall has exactly one wedge point
  per step, which becomes the natural battleground. Edges kill ladders
  (both my ladder captures ended on the edge), and corners make suicide
  probes cheap. The two goals crossing at 90° force every game through a
  central crossing fight.
- Emergent concepts you'd name (or "none observed"): "dual-purpose stone"
  (the game's core currency), "staircase wall" and its "wedge point",
  "undead wedge" (zero-lib suicide as a permanent blocker), "edge ladder",
  "fill-out draw" (the tiebreak loophole), "ko-to-draw" (super-ko rollback
  feeding the pass counter).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Almost entirely my choices: this is
  a transparent, human-readable game where I could plan five-move races,
  count semeai, and be punished for concrete reading errors. The one
  structural intrusion is the draw loopholes, which let a lost player
  steer toward a draw rather than a loss.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is very nearly Gonnect (Neto, 2000): Go capture rules on a small
  board, win by connecting opposite sides, placement anywhere. The
  asymmetric goals (P1 rows, P2 columns) are standard Hex/TwixT-style
  assignment. Free placement + orthogonal connection + surround capture:
  every load-bearing mechanic is prior art, and the strategy that emerged
  (dual-purpose stones, crossing fights) is exactly Gonnect strategy.
- Honest novelty assessment after arguing that case: Largely a known
  design. The genuine deviations are: legal suicide with persistent
  zero-liberty stones (Gonnect/Go forbid or remove these) — which creates
  the truly novel undead-wedge/permanent-wall tactic — plus pass-with-
  double-pass-draw (Gonnect bans passing to guarantee decisiveness, and
  this game's draw loopholes show why), and the cosmetic influence layer.
  Net: a Gonnect variant with one interesting house rule and one
  decisiveness-weakening rule. Low-to-moderate novelty.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): partial — I recognize the design as essentially
  Gonnect (Go + connection win) with asymmetric Hex-style goals and a
  no-self-capture house rule. I do not recognize this specific instance or
  recall any prior score for it.
- P1-role experience sub-score (1-10): 4.2
- P2-role experience sub-score (1-10): 4.4
- Role-averaged sub-score: 4.3
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — P2 won both
  decisive lines, but in Line 1 the decisive factor was my concrete reading
  errors as P1 rather than seat structure, and race-count analysis showed
  the first-move tempo edge and the crossing-fight geometry are symmetric;
  small-sample lean, not structural evidence.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.2**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game B is the most humanly playable and legible entry I evaluated: my
  Line 1 loss traced to identifiable reading mistakes (a missed snapback)
  rather than opaque dynamics, and my Line 2 win was a satisfying arc of
  doctrine (staircase wall), punishment (edge ladder, snapback), and a
  genuinely novel defensive idea from the opponent (the undead wedge).
  Depth and agency are excellent; games end decisively when players play
  to win. It loses points on novelty — it is Gonnect with asymmetric goals
  in all but name (Phase 4), so the design contribution is one house rule
  — and on the endgame warts: the fill-out loophole and ko-to-draw
  interaction give losing players draw escapes that undermine the win
  condition. Above R8's 4.10 on play quality, held below R19's 4.375 by
  the recognizable prior: 4.2.
