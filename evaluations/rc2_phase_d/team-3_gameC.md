# Team 3 — Game C verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 hex-adjacency board (up to 6 neighbours). Players alternate placing one
  stone. **No capture, no influence.** The only placement rule: a stone must be
  placed on an empty cell **adjacent to at least one ENEMY stone** (waived only
  while you have zero stones, so each player's first move is anywhere; it would
  re-arm if all your stones were removed, but with no capture that never
  happens). **Win = first to own ≥28 stones** (>0.4276×64). No komi. Because
  stones are never removed, "own" = "have placed," so the win is simply a race
  to place 28 stones. If 100 steps pass with no winner, more stones wins; double
  pass = draw.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw): The 28-stone
  win condition fired in every real race — Line 1 (P1 @ ply55, 28-27), Line 2
  (P1 @ ply55, 28-27), Line 3 (P2 @ ply56, 28-27 after a P1 pass). Confirmed
  double-pass → DRAW. The 100-step tiebreak never triggered because 28 is
  reached at ply 55/56 with cells still empty.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Nothing mechanically surprising — but it surprised me how
  *little* the placement constraint constrains: through 55 plies neither player
  was ever forced to pass, because the board still has ~9 empty cells when
  someone hits 28, and enemy-adjacent empties are always abundant.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,28,20,11,3,2,1,0,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,21,22,23,24,25,26,29,30,31,33,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,49,48,50,51,52,53,54`
- Plan and what happened: I drove P1 as a compact-fill racer; P2 responded
  competently, also placing on every turn (the only sensible play, since each
  placement is +1 toward 28). Both grew one stone per ply. I reached 28 first
  by my move-1 tempo lead.
- Result (winner, end cause, plies): **P1 win**, win condition, ply 55, 28-27.

### Line 2 — you as P2
- Moves: `27,28,37,45,54,62,63,61,60,59,58,57,56,55,53,52,51,50,49,48,47,46,44,43,42,41,40,39,38,36,35,34,33,32,31,30,29,26,25,24,23,22,21,20,19,18,17,16,14,15,13,12,11,10,9`
- Plan and what happened: I drove P2 with a deliberately *different* geometry
  (spread to the opposite edge of the board) to test whether placement choice
  could let the second player overtake or strand P1. It made no difference: both
  still incremented every ply and P1's tempo lead held.
- Result: **P1 win**, win condition, ply 55, 28-27 — identical margin to Line 1.

### Line 3 — adversarial / novelty-stress
- Moves: `64,28,27, …` (P1 opens with a PASS, then both race greedily) — full
  line ran 56 plies.
- What you tried to break / stress, and what happened: I tested whether the
  result is anything other than a pure tempo count. I gave P1 a single wasted
  PASS on ply 1; the entire outcome flipped — **P2 won 28-27 at ply 56.** I also
  confirmed there is no way to *force* the opponent to pass before the race ends
  (denying P1 a move would require every P2 stone to be fully surrounded, i.e. a
  nearly-full board, which only occurs after someone has already reached 28), and
  that a mutual pass is the only route to a draw.
- Result: P2 win 28-27 (P1 pass) — demonstrating the game is decided **solely by
  who holds the tempo lead**, nothing else.

### Additional lines (optional)
Two independent greedy fills (compact vs. spread) plus the pass-penalty line
were enough to confirm determinism; further lines reproduce the same 28-27 race.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why): There isn't one of
  consequence. Every turn you place one legal stone (always available) and gain
  exactly +1 toward 28; *where* you place changes nothing about your count or
  the opponent's options. The only "skill" is never wasting a turn on a pass.
- Counterplay: None observed. In Line 2 I tried an opposite-edge spread as P2 to
  strand or out-tempo P1 and it changed nothing — P1 still won 28-27. The second
  player has no mechanism to overtake without a first-player error (Line 3).
- Topology/board effects on strategy: The hex adjacency and the enemy-adjacency
  constraint keep the two colours interlocked into one growing contested blob,
  but with 64 cells and a 28-stone target, frontier cells never run out, so the
  topology is cosmetic to the result.
- Emergent concepts you'd name (or "none observed"): None observed. The
  interlocked-growth aesthetic is mildly pretty but produces no decisions.
- Player agency: Effectively zero. Lines 1 and 2 (different P-driven geometries)
  gave the identical 28-27 result; Line 3 shows the result is a function purely
  of tempo (who passes), not of any choice made on the board.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior: It's a degenerate
  **majority/territory race** — first to a fixed count on a fixed board, with a
  contact rule (place adjacent to enemy) borrowed from go-like contact play but
  with the captures removed. With no capture and no influence, it reduces to
  "both players add one stone per turn until someone hits the quota," which is
  the parity-decided fill that earlier project notes flagged as the banned
  *majority-win* failure mode in a thin disguise.
- Honest novelty assessment after arguing that case: Very low. The lone
  distinctive ingredient — the must-touch-enemy placement constraint — is real
  and does shape the *shape* of play, but it never creates a *decision* because
  legal cells are always plentiful and your count rises regardless of where you
  put the stone. Strip the contact rule and the outcome is unchanged.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.0 — you win, but by fiat (tempo), not
  by anything you did.
- P2-role experience sub-score (1-10): 2.2 — you cannot win against competent
  play and your choices are inert (Line 2).
- Role-averaged sub-score: 2.6
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** **1** — P1 won by the
  identical 28-27 tempo margin under two different P2 strategies, and P2 could
  only win when P1 voluntarily wasted a pass (Line 3); the second player has no
  counterplay.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 2.6**
- One-paragraph justification of the Overall, citing your Phase 2 lines: This is
  a near-trivial, fully-determined first-player race. Line 1 and Line 2 produced
  the exact same 28-27 result despite deliberately opposite P2 geometries,
  showing placement choice is irrelevant; Line 3 shows the only variable that
  matters is tempo (a single P1 pass hands P2 the win). With no capture, no
  influence, abundant legal cells, and no possibility of forcing the opponent to
  pass before the quota is hit, there is essentially no agency or counterplay.
  The enemy-adjacency constraint is a fresh-looking coat of paint over what is
  fundamentally the banned parity/majority race, which lands it clearly below
  every anchor (R8 4.10, R20 3.73, R21 3.69). **Overall 2.6.**
