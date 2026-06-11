# Team 1 — Game G verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words: Hex board, 8×8 = 64 active cells, 6-neighbour
  adjacency. **PLACE** (ids 0–63) with the same forced-contact rule as a
  contact race: a placement must be **adjacent to an enemy stone**, waived only
  while you have zero stones. **No capture, no influence** (both vestigial per
  `--rules`). **Win = stone-count race to ≥ 28 of 64** (> 0.4276·64); komi 0;
  turn-limit-100 → more-stones tiebreak; double-pass → DRAW. The new element vs
  a bare placement race is a **MOVE action** (ids 65–448): relocate one of your
  stones to an adjacent EMPTY cell (no enemy-adjacency constraint on the
  destination). **Super-ko** is active (position repetition → rollback to pass).
- What actually ends the game: the **win condition firing at 28 stones around
  ply 55** in every competitive line; double-pass draw reachable by mutual
  refusal. I never reached the turn limit.
- Surprises: (1) **MOVE does not change your stone count** (verified:
  `36,37,282` left P1 at 1 stone) — so in a race to 28 *placements*, every MOVE
  is a wasted tempo. (2) **Super-ko genuinely fires**: I built a 2-stone
  oscillation (`36,37,282,287,275,294`) and ply 6 was flagged
  "SUPER-KO … rolled back and treated as a PASS."

## Phase 2 — Strategic play (≥3 full lines, both roles)

### Line 1 — you as P1
- Moves: `36,37,28,20,27,26,19,10,2,43,3,9,1,21,11,8,0,12,4,29,5,6,7,14,13,44,15,23,22,30,31,39,16,24,17,25,18,35,32,40,33,41,34,42,38,46,47,55,63,45,48,49,56,57,50`
- Plan and what happened: As P1 I ignored MOVE entirely (it cannot advance the
  count) and simply placed a contact stone every turn, keeping a live frontier
  so I never had to pass. P2 expanded competently. I reached 28 one tempo
  ahead.
- Result: **P1 wins, win condition at 28, 55 plies (P1=28, P2=27).**

### Line 2 — you as P2
- Moves: `36,37,29,21,12,4,45,5,11,3,10,2,9,1,22,8,17,13,14,6,20,7,38,15,44,16,24,18,26,19,23,25,33,27,34,28,35,30,39,31,0,32,40,41,50,42,51,43,49,46,54,47,52,48,55`
- Plan and what happened: Driving P2, I looked for any way MOVE could let me
  overcome the first-move deficit — relocating to deny P1 frontier, etc. Every
  such idea costs a placement and so loses count, while P1 keeps placing. The
  best I could do was place every turn too, and I still finished exactly one
  stone behind.
- Result: **P1 wins, 55 plies (P1=28, P2=27)** — I (P2) lost by one tempo.

### Line 3 — adversarial / novelty-stress
- Moves: `36,37,282,287,275,294`
- What you tried to break / stress: I stress-tested the only feature that
  distinguishes G from a bare contact race — the MOVE action — by oscillating
  two stones back to a prior position. The engine fired **super-ko** on ply 6
  and converted it to a pass (board delta: none). This both confirms the
  repetition rule and underlines that MOVE produces no progress: you can shuffle
  stones forever and your count never rises.
- Result: super-ko rollback confirmed; MOVE demonstrated to be count-inert.

### Additional lines (optional)
Placement-only policy sweep (compact-fill / max-spread / min-spread for both
sides) from the centre opening: **every combination → P1 wins ply 55, 28–27**,
identical to a bare contact race. No policy and no use of MOVE changed the
outcome.

## Phase 3 — Joint strategic analysis

- Core tactical loop: "Place a contact stone every turn that keeps your frontier
  alive; never pass; never MOVE." That is the entire optimal strategy — MOVE and
  super-ko are present but never advance a competent player's goal.
- Counterplay: Essentially none. As in the bare contact race, responding to the
  opponent does not change the tempo verdict; the one theoretical use of MOVE
  (relocate to shrink the opponent's placement frontier and force them to pass)
  costs you a placement, so it cannot net you tempo against a player who just
  keeps placing.
- Topology/board effects: Hex 6-connectivity keeps frontiers generous, so the
  race runs cleanly to a fill and the tempo leader (P1) wins; the MOVE option,
  if anything, lets a player *avoid* the rare self-strand, making P1's edge even
  more robust.
- Emergent concepts: **None.** The added MOVE/super-ko machinery generated no
  emergent strategy — only a verified rollback curiosity.
- Player agency: **Very low.** Outcome invariant across the policy sweep; MOVE
  adds nominal options that are all strictly dominated by "place again."

## Phase 4 — Novelty adversary

- Strongest re-skin case: This is a **stone-count contact race** (Go stripped of
  capture/influence) with a bolted-on movement action — i.e. a filling/tempo
  race with extra, non-functional verbs. The MOVE action superficially evokes a
  movement game, but because the win is a *placement* count, movement is
  strictly tempo-negative and never used.
- Honest novelty assessment: **Very low — arguably negative.** The only novel
  additions (MOVE, super-ko) do not interact with the win condition in any
  useful way; they enlarge the rulebook and action space without adding depth.
  The played experience is indistinguishable from a bare first-player tempo
  race.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): **3.0** — you win near-automatically by
  tempo; MOVE is noise.
- P2-role experience sub-score (1-10): **2.3** — structurally one tempo behind
  with no lever (MOVE can't recover count) to escape it.
- Role-averaged sub-score: **2.65**
- **Fairness perception (1–5): 2** — Strongly P1-favored: every swept line and
  both competent role lines ended 28–27 for P1 by one tempo, and MOVE lets P1
  dodge the only fluke (self-strand) that ever flips such a race.
- **Overall (1-10): 2.6**
- Justification: Anchoring DOWN against drift (R21 3.69, R20 3.73), G lands
  clearly below the band and slightly below a clean contact race, because the
  one thing that distinguishes it — the MOVE action (plus super-ko) — adds
  rulebook and action-space complexity with **zero strategic payoff**: Line 3
  shows MOVE is count-inert and only triggers a super-ko rollback, while the
  policy sweep and Lines 1–2 show the same invariant 28–27 first-player tempo
  win as a bare race. Near-zero agency, a structural P1 advantage, and
  non-functional added mechanics put it at **2.6** — a hair under a clean race
  for the wasted complexity.
