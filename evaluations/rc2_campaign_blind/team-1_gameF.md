# Team 1 — Game F verdict

> Copy this template to `team-1_gameF.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game F` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid. Actions: place on an empty cell adjacent to ANY
  stone (either colour; anywhere while you have zero stones, re-arming),
  MOVE one of your stones to an adjacent cell — overwriting an enemy stone
  there — or pass. After every action one CA step runs from the actor's
  perspective: empty cells at exactly 2 friendly + 1 enemy or 1 friendly +
  2 enemy become the ACTOR's; any stone with zero neighbours flips to the
  other side; a stone with 1 own + 3 enemy neighbours flips to the enemy
  (and 3 + 1 to the actor). Win by owning ≥30 of 64 cells, else most
  stones at step 100; double pass draws; positional super-ko (never fired
  in my lines).
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  One 30-stone threshold win (Line 1, step 67 — the only threshold
  termination I achieved anywhere in this campaign's territory games),
  one step-100 piece-count tiebreak (Line 2, 28–20), one double-pass draw
  (Line 3, step 9). Decisive games are long grinds: 67–100 plies with the
  count flickering every action as the CA churns.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) The poisoned opening: the first stone of the game is
  isolated, so it flips to the opponent in its own tick — P1's opener is
  a forced donation (engine: ".->O@(3,3)" on MY placement). (2) The
  isolation oscillator: a lone stone flips on EVERY action including
  passes (verified: his pass flipped my donated stone back to me).
  (3) Overwrite-moves kill directly (my MOVE onto his stone removed it),
  but moving into an unsupported cell donates the mover via the isolation
  rule. (4) Outcomes are knife-edge: in controlled experiments, changing
  a single equal-looking placement at ply 4, 6, or 8 swung the final
  result from a P2 +8 tiebreak win to a P1 threshold blowout.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,28,26,19,18,10,138,35,17,9,36,1,8,0,209,2,11,12,4,115,77,25,16,70,78,33,24,74,13,29,42,37,120,44,51,78,152,13,184,149,110,79,3,74,22,75,2,70,147,20,5,75,2,70,6,118,147,82,115,78,117,38,31,15,13,86,46`
- Plan and what happened: I opened with the forced donation (27 flipped to
  P2), rebuilt contact on the donated pair, and won the harvest war: my
  placements repeatedly created 2-friendly+1-enemy births while my MOVE
  actions (ids >64 in the list: 138, 209, 115, 184, …) recycled stones
  into overwrites and birth-triggers instead of spending new ones.
  Scripted P2's ply-6 consolidation at 10 — one of several equal-looking
  +1 moves — turned out to concede the initiative permanently; from
  ~ply 30 I was up double digits and ground to exactly 30 stones.
- Result (winner, end cause, plies): P1 (me) wins by the 30-stone
  threshold at step 67 of 100; 30 stones v 12.

### Line 2 — you as P2
- Moves: `27,28,26,19,18,20,17,21,25,16,24,29,22,30,9,8,1,131,0,98,2,31,3,12,101,129,9,130,138,175,133,97,17,99,170,161,34,36,43,4,5,14,155,23,110,83,78,115,38,45,111,11,85,113,119,97,71,134,104,141,133,177,112,172,28,167,124,14,24,32,137,194,41,51,40,163,49,269,135,195,52,59,57,48,131,165,193,25,194,171,141,175,162,121,145,171,14,165,141,167`
- Plan and what happened: The receiving side of the donation: I accepted
  P1's flipped opener, consolidated the pair, and played the responder's
  game — matching his births, using overwrite-moves to erase his frontier
  stones, and keeping my count ahead through the endless CA churn (the
  count see-sawed by 1–2 stones nearly every ply from step 60 on). Neither
  side could approach 30; at the horn I led by the margin built in the
  middlegame.
- Result: P2 (me) wins by max-turns piece-count tiebreak at step 100;
  28 stones v 20.

### Line 3 — adversarial / novelty-stress
- Moves: `27,64,19,20,28,64,179,64,64`
- What you tried to break / stress, and what happened: (1) Oscillator:
  after my donated opener, his PASS flipped the lone stone back to me —
  an unowned stone ping-pongs on every action until someone gives it a
  neighbour. (2) Overwrite-move: action 179 slid my supported stone onto
  his (4,2) stone, removing it (P2 to zero stones — re-arm state) while
  my mover survived on its remaining support. (3) Double-pass termination
  verified at step 9. Super-ko never fired across all 176 engine plies of
  my three lines.
- Result: DRAW by double pass at step 9; every exotic rule behaved exactly
  per the table.

### Additional lines (optional)
Deviation experiments (all engine-checkable): from the Line-2 base,
substituting a single different +1 placement for P2 at ply 4 (36), ply 6
(10), or ply 8 (29) flipped the outcome to P1 wins of 28–26, 30–12, and
27–16 respectively. The donation/receiver margins are razor thin, and the
game tree is chaotically sensitive — relevant both to fairness and to how
much "strategy" versus knife-edge tactics decides results. Opening
theory: if both players refuse to donate, the game is a 2-ply double-pass
draw; the first mover bears the donation burden by rule.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  As in the other harvest-CA game: create cells that sit at exactly
  2-friendly+1-enemy after YOUR action (births to you), deny the mirror
  cells, and keep every stone at 1+ friendly neighbour (isolation
  donates; 1v3 surround flips). MOVEs are the sharpest tool: an overwrite
  removes an enemy stone AND can land your mover on a birth-trigger, all
  without spending material.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Constantly: every birth I set
  up could be claimed by him first (actor-claims-mixed-cells), every
  frontier stone I left at 1-support invited a surround-flip or
  overwrite, and the opening donation is pure punishment for moving
  first. But unlike Game D's clean seesaw, here the feedback is noisy —
  the CA churn means even good responses wobble the count for dozens of
  plies before an edge shows.
- Topology/board effects on strategy: Flat 8×8 with 4-neighbour caps
  keeps the CA tame (no cascade avalanches — births arrive one or two at
  a time), edges lower neighbour counts and so breed isolation accidents,
  and the 30-stone bar at only 47% of the board is reachable — my Line 1
  hit it exactly — but only after a collapse, not against resistance.
- Emergent concepts you'd name (or "none observed"): "poisoned opener /
  donation zugzwang", "isolation oscillator", "overwrite tempo",
  "harvest parity" (whose action claims the mixed cells), "churn"
  (the endgame's perpetual ±1 count noise).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Mixed. Choices matter — my wins
  in both seats came from consistent harvest discipline — but the
  deviation experiments show single innocuous-looking moves swinging
  ~16-stone final margins, which means much of the tree is chaos that
  neither human intuition nor shallow search can reliably navigate.
  Agency is real but poorly legible.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is the same actor-perspective birth-CA economy as this pack's 4-D
  torus game (mixed 2:1 cells birth to the actor) transplanted to a flat
  8×8 with a stone-majority goal — i.e., a sibling design, not an
  independent one — and the components (two-player Life variants,
  majority scoring, piece relocation) are all known.
- Honest novelty assessment after arguing that case: Within the pack it
  reads as "the tame flat version of D". Its distinct contributions are
  the isolation-flip rule — which single-handedly creates the poisoned
  opening, the oscillator, and the donation zugzwang, none of which exist
  in D — and overwrite-moves. Mild-to-moderate novelty: one genuinely
  clever rule on a familiar chassis.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — no recognition of this specific game;
  the sibling-of-D observation above is internal to this blind pack.
- P1-role experience sub-score (1-10): 4.0
- P2-role experience sub-score (1-10): 4.0
- Role-averaged sub-score: 4.0
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3.5 — the rules
  make P1's compulsory first placement a literal donation to P2 (pass-
  standoffs draw, so someone must pay), and my base line saw the receiver
  win the tiebreak; but my deviation tests swung wins to P1 three times
  and I won my own P1 line by threshold, so the lean is mild and
  swamped by tactical noise.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.95**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game F's isolation-flip rule earns real credit: the poisoned opening
  and move-1 zugzwang (Line 3's oscillator demo; the pass-standoff
  analysis) are the most original single-rule consequences I found in
  this pack, and both my wins (threshold at step 67 as P1; tiebreak 28–20
  as P2) required sustained, correct harvest play with the overwrite-move
  adding honest tactical spice. It stays below the R8 anchor's
  neighbourhood because the experience is a fog: 67–100-ply grinds whose
  count flickers every action, outcomes chaotically sensitive to
  interchangeable-looking moves (my three one-move deviation tests each
  reversed the result), and a threshold win that only materializes after
  the game is already decided. Clever rule, muddy game: 3.95.
