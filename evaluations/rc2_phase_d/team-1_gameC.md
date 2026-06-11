# Team 1 — Game C verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words: Hex board, 8×8 = 64 active cells, 6-neighbour
  interior adjacency. Pure PLACE game (ids 0–63 = cell index, 64 = PASS). The
  one structural rule: **a placement must be adjacent to at least one ENEMY
  stone** — waived only while you have ZERO stones (so the very first stone of
  each colour goes anywhere; with no capture this waiver never re-arms). No
  capture, no influence field, no propagation (the threshold/radius/decay
  fields are vestigial per `--rules`). **Win = stone-count race: the instant
  you own ≥ 28 of 64 cells (> 0.4276·64) you win.** komi_p2 = 0. Turn limit 100
  → more-stones tiebreak; two consecutive passes → immediate DRAW.
- What actually ends the game: In every competitive line I played the game
  ended by the **win condition firing at exactly 28 stones**, around ply 55–56.
  Double-pass draw is reachable but only by mutual refusal to play
  (verified: `36,64,64` → "double pass -> draw"). I never saw the 100-step
  tiebreak because the board saturates to a decision near ply 55 first.
- Surprises: (1) Because you must touch enemy stones, the two colours are
  forced to interlock — there is no "build my own corner" option. (2) A player
  CAN be forced to PASS mid-board if their own expansion strands them with no
  empty cell adjacent to an enemy stone — I induced exactly this (P1 pass at
  ply 29 in one line), and it flips the whole race.

## Phase 2 — Strategic play (≥3 full lines, both roles)

### Line 1 — you as P1
- Moves: `36,37,28,20,27,26,19,10,2,43,3,9,1,21,11,8,0,12,4,29,5,6,7,14,13,44,15,23,22,30,31,39,16,24,17,25,18,35,32,40,33,41,34,42,38,46,47,55,63,45,48,49,56,57,50`
- Plan and what happened: I opened centre (4,4), and as P1 I filled
  **compactly** — always taking a contact cell that kept a live frontier
  (never stranding myself), so I was never forced to pass. P2 responded by
  spreading for maximum future frontier (a competent expansion). Because I move
  first and neither side ever passed, I simply reached the 28th stone one
  tempo ahead.
- Result: **P1 wins, win condition at 28 stones, 55 plies (P1=28, P2=27).**

### Line 2 — you as P2
- Moves: `36,37,28,20,11,3,2,1,0,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,29,30,31,32,33,34,35,38,39,40,41,42,43,44,45,46,47,49,48,50,51,52,53,54`
- Plan and what happened: Here I drove P2 and tried every responder line I
  could to get ahead, while P1 played a clean non-stranding fill. The result
  was invariant: I (P2) am always exactly one placement behind. When P1 laid
  its 28th stone (ply 55) I had 27 and the game ended before my turn. No P2
  responder line I found overcomes the first-move tempo against competent P1.
- Result: **P1 wins, 55 plies (P1=28, P2=27)** — I (P2) lost by one tempo.

### Line 3 — adversarial / novelty-stress
- Moves: `36,37,29,44,52,60,38,59,51,58,50,57,49,56,28,53,54,62,55,63,43,61,45,48,40,47,39,46,64,42,34,41,33,35,26,32,24,31,23,30,22,27,19,25,17,21,12,20,11,18,9,16,13,15,7,14`
- What you tried to break / stress: I made P1 expand **greedily into open
  space** (max-frontier spread) to see if growth quality matters, while P2
  hugged edges. P1's greedy spread **stranded itself**: at ply 29 P1 had no
  empty cell adjacent to any P2 stone and was **forced to PASS** (token `64`).
  That single lost tempo handed the race to P2. I separately confirmed the
  double-pass DRAW path (`36,64,64`).
- Result: **P2 wins at ply 56 (P1=27, P2=28)** — purely because P1 was forced
  to pass once. Also confirmed: double-pass → DRAW.

### Additional lines (optional)
I swept all 16 combinations of four policies (compact-fill, edge-fill,
max-spread, min-spread) for both sides from the centre opening. Outcome:
**14/16 → P1 wins ply-55 28–27; 2/16 → P2 wins ply-56 28–27 (both caused by a
P1 self-strand pass); 0 draws.** The result is astonishingly invariant to
strategy.

## Phase 3 — Joint strategic analysis

- Core tactical loop: "Place a stone touching the enemy that does NOT exhaust
  your own future frontier, every single turn." A good move is almost any
  legal move that doesn't strand you; the only real error is one that forces a
  later pass. There is essentially no positional payoff structure beyond
  parity.
- Counterplay: Responding to the opponent barely matters — I could not find a
  P2 response that beats competent P1, and P1's win was independent of P2's
  shape. The only "counterplay" is the negative kind: hope the opponent
  strands themselves into a pass.
- Topology/board effects: Hex 6-connectivity gives generous frontiers, which
  is precisely why the frontier almost never dries up and the race runs to a
  clean fill. The topology removes the only source of tension (running out of
  contact cells), making the tempo race even more deterministic.
- Emergent concepts: Essentially **none** beyond "don't strand your own
  frontier / never pass first." No territory shaping, no captures, no influence
  — the vestigial fields confirm a stripped-down ruleset.
- Player agency: **Very low.** Across 16 competitive self-play lines the result
  was the same parity outcome; choices only mattered in the degenerate case of
  a player sabotaging themselves into a forced pass. The race structure, not
  the players, decides the game.

## Phase 4 — Novelty adversary

- Strongest re-skin case: This is **Go with capture, influence, and territory
  scoring all removed**, leaving only a stone-count race with a
  must-touch-enemy constraint — i.e. a parity/tempo filling race close to
  combinatorial "filling" games (Col/Snort-family adjacency placement) but even
  thinner because there is no capture or forbidden-colour interaction. The
  must-be-adjacent-to-enemy rule is the only non-trivial twist, and it serves
  mainly to force interlock, not to create decisions.
- Honest novelty assessment: **Low.** The forced-contact placement rule is a
  mildly interesting constraint, but with no capture, no influence, and a flat
  count-to-28 win, it collapses to a first-player tempo race that any competent
  player wins on schedule. Nothing emergent or strategically deep appeared in
  ~17 full lines.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): **3.0** — you win almost automatically,
  but the win feels handed to you by move order, not earned.
- P2-role experience sub-score (1-10): **2.5** — you are structurally one tempo
  behind and no responder line escapes it; play feels inconsequential.
- Role-averaged sub-score: **2.75**
- **Fairness perception (1–5): 2** — Strongly P1-favored: with competent play
  P1 won 14/16 sweep lines and every both-sides-competent line by exactly one
  tempo (28–27 at ply 55); P2 only ever won when P1 sabotaged itself into a
  pass.
- **Overall (1-10): 2.7**
- Justification: Anchoring DOWN against drift (R21 3.69, R20 3.73), Game C sits
  clearly below those. My Phase 2 lines show a game whose outcome is invariant
  to strategy — Line 1 and Line 2 are the same 28–27 ply-55 result with the
  roles' fates fixed by tempo, and the only deviation (Line 3) required a
  player to strand itself into a forced pass. There is no capture, no
  influence, no emergent concept, and near-zero player agency, plus a clear
  structural P1 advantage. It is a clean, bug-free implementation of a thin
  idea — a tempo fill race — which keeps it off the floor, but it lands at
  **2.7**, well under the anchor band.
