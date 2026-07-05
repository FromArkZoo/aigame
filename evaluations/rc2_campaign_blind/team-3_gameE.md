# Team 3 — Game E verdict

> Copy this template to `team-3_gameE.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game E` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid. Actions: PLACE on any empty cell, MOVE one of your stones to an
  adjacent EMPTY cell, or PASS. Go-like surround capture: after an action, any adjacent
  enemy group with zero liberties is removed — and engine testing shows MOVEs trigger
  captures too, not just placements. There is no suicide rule: you may fill your own
  group's last liberty (or place a 0-liberty stone) and it SURVIVES, because removal
  only ever triggers from a newly placed/moved stone adjacent to the group — a
  0-liberty group has no adjacent empty cell, so it can never be captured ("zombie"
  stones/masses). Win: own >40.48 cells, i.e. 41 of 64. 100-step limit → most stones;
  double pass at ANY point → immediate draw regardless of counts; super-ko converts
  repeating actions into passes.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  ALL THREE lines ended in double-pass draws (plies 89, 77, and 11) — never the
  threshold, never the turn-limit tiebreak. That is the game's story: decisive results
  are nearly impossible between aware players (see below).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules:
  (1) The forced-draw exploit: a trailing player can fill every remaining empty cell —
  including filling their OWN last liberty to become an uncapturable 0-liberty "zombie
  mass" — until the board is full; then both players' only action is PASS and the game
  is a DRAW no matter the stone difference (verified in Line 1: I led 39–25 and got a
  draw). (2) MOVE actions trigger captures despite the rules text saying "after your
  placement". (3) The MOVE-shuffle stalling idea (burn plies to reach the step-100
  most-stones tiebreak) fails: repeating a position converts the action to a PASS,
  which chains with an opponent pass into an instant draw (verified at ply 11 of the
  stress line). (4) Self-filling your last liberty is not just legal but a LIFE
  technique — "zombie life" makes any surrounded group immortal.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,36,28,35,44,43,20,34,26,42,50,51,58,59,49,41,33,25,17,52,60,53,45,37,29,21,13,12,11,10,46,38,30,39,47,31,23,32,54,61,40,14,62,15,63,22,60,6,33,5,19,7,23,4,43,3,42,2,35,1,34,9,41,8,36,0,37,16,18,24,38,13,39,56,51,57,48,55,52,31,53,59,61,56,57,23,56,64,64`
- Plan and what happened: A genuine Go game broke out: a central crosscut left P2 with an
  11-stone eyeless dragon (liberties 38/40/54/61) against my one-liberty pair. I saved
  the pair with 46, sealed the dragon's escape routes (30, 47, 23, 55...), survived two
  liberty-reopening counter-captures (P2's captures of my stones at (1,4) and (7,2) each
  gave the dragon a fresh liberty I had to re-fill), and killed the 15-stone dragon at
  ply 53. I then filled toward the 41-cell threshold while P2 harvested my top-edge
  weak stones and — critically — zombie-filled cells (a 0-liberty stone at (3,7)
  survived) and finally filled its own mass's last shared liberty at (7,2), becoming an
  uncapturable zombie-mass.
- Result (winner, end cause, plies): DRAW by double pass at ply 89, with me ahead 39–25.
  The threshold (41) was mathematically out of reach once the zombies denied 3 cells,
  and a full board forces mutual passes. Best play by the loser converts any lost game
  into a draw.

### Line 2 — you as P2
- Moves: `36,27,35,28,43,44,34,20,42,26,51,50,59,58,41,49,25,33,52,17,53,60,37,45,21,29,12,13,10,11,46,19,32,57,61,30,56,48,5,14,22,38,39,31,23,18,54,6,55,15,63,7,47,33,40,56,24,21,45,22,44,9,62,16,60,8,3,4,1,5,0,2,3,1,0,64,64`
- Plan and what happened: I transposed Line 1's opening with colors swapped — and the
  tempo flip decided the middlegame: as the dragon's owner P1 moved FIRST in the
  critical position and captured my two-stone pair instead of me saving it. Down
  material with fragmented groups, I defended with the full toolkit discovered in this
  game: a snapback-style capture at (7,2) (took two stones), a self-zombie single stone
  at (1,4) inside his dragon (immortal spite-stone stealing a liberty), "zombie life"
  for my six-stone south group (filling my own last liberty at (0,7) after his atari),
  and a three-stone corner capture at (2,0). I clawed back to a 33–28 lead.
- Result: DRAW by double pass at ply 77 (33–28 to me). Same lesson from the other side:
  even after outplaying the opponent in the endgame, conversion to a WIN is impossible
  — the threshold is too far and the board fills.

### Line 3 — adversarial / novelty-stress
- Moves: `0,1,9,20,3,21,77,64,74,64,77` (plus `--legal` decodes)
- What you tried to break / stress, and what happened: (a) MOVE-capture: relocating my
  stone from (3,0) to (2,0) filled an enemy stone's last liberty — the engine captured
  it, so moves DO trigger captures. (b) Stalling: I shuffled the same stone back
  (2,0)→(3,0)→(2,0) around opponent passes; the return move recreated a prior position,
  was rolled back to a PASS by super-ko, and chained with P2's preceding pass into an
  immediate DRAW at ply 11. Stalling toward the step-100 tiebreak is thus self-
  destructive — which closes the leader's last escape from the full-board draw.
- Result: DRAW by double pass at ply 11; both mechanics verified.

### Additional lines (optional)
Zombie behavior was verified repeatedly inside Lines 1–2 (0-liberty placements at
(7,6), (3,7), (1,4) all survived; a 25-stone 0-liberty mass survived at Line 1's end).

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Mid-game it is honest Go: count liberties, seal eyeless groups, save cuttable pairs,
  time your fills so sealing stones do double duty (my 46 both saved a pair and took
  dragon liberties). The novel layer is liberty bookkeeping under the zombie rule: a
  capture in your favor REOPENS cells that can become the enemy dragon's new liberties
  (this happened to me twice in Line 1), and the strongest defensive move is often
  filling YOUR OWN last liberty ("zombie life") — the exact move Go forbids as suicide.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all?
  Strongly, through the middlegame: the whole Line 1 dragon hunt was move-by-move
  punishment and response, and Line 2's defense was a chain of counter-captures. But in
  the endgame counterplay inverts into futility: whatever the leader does, the trailing
  player fills the board into a draw; the only "response" that matters is who times the
  zombie conversion correctly (fill your own last liberty yourself = immortal; let the
  opponent fill it = dead).
- Topology/board effects on strategy: Standard 8×8 orthogonal Go geometry — edge groups
  have fewer liberties, corners are cheapest to live in. Nothing exotic; all the
  strategic novelty comes from the rules, not the board.
- Emergent concepts you'd name (or "none observed"): "zombie life" (self-fill =
  unconditional life), "zombie spite-stone" (0-liberty placement denying a cell/liberty
  forever), "liberty reopening" (captures gift the surrounded group new liberties),
  "the full-board draw" (the loser's guaranteed escape), "stall-ko trap" (shuffling
  into super-ko passes accidentally ends the game).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Mid-game agency is high and Go-like — the
  15-stone dragon kill was earned. Final-result agency is near zero between aware
  players: all three lines ended in draws regardless of who outplayed whom, because
  the rule set hands the trailing player a forced draw.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It IS Go — surround capture, liberties, group life — on 8×8 with free placement, a
  stone-count winning threshold instead of territory scoring, plus a stone-shuffle MOVE.
  Every strategic concept I used (atari, sealing, snapback, eyes-ish thinking) imports
  directly from Go; the threshold is just Go scoring made binary.
- Honest novelty assessment after arguing that case: The deviations from Go (no suicide
  rule + capture-only-from-adjacent-placement + double-pass-draw + threshold win) are
  individually small but combine into a genuinely new — and genuinely broken — endgame
  regime of zombie masses and forced draws. That's novel emergent behavior, but it
  reads as an unintended interaction rather than design: the novelty actively destroys
  the contest. Low design novelty, high (accidental) emergent novelty.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — the Go resemblance is structural; I do not recognize
  this specific variant or any prior score.
- P1-role experience sub-score (1-10): 3.6
- P2-role experience sub-score (1-10): 3.4
- Role-averaged sub-score: 3.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — the mirrored Lines 1/2
  showed the tempo-holder wins the central fight whichever color has it, and both
  competitive lines converged to draws (39–25 my way as P1, 33–28 my way as P2), so
  neither seat is structurally favored; the draw engine dominates both.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.5**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The middlegame deserves real credit: Line 1's dragon hunt (sealing four liberties
  while my counter-captured stones kept reopening them) and Line 2's defensive
  toolkit (snapback, zombie life, spite-stones) are authentic, learnable Go-flavored
  tactics that I enjoyed finding. But the game cannot produce a decisive result
  between competent players: the 41-cell threshold is practically unreachable, the
  trailing player force-draws by zombie-filling the board (Line 1: my 39–25 lead →
  draw), and even stalling for the turn-limit is closed off by the super-ko pass trap
  (Line 3: instant draw at ply 11). Three lines, three draws, all end causes
  degenerate. Strong tactics inside a contest that structurally refuses to award wins:
  3.5, between R21's 3.69 and the broken-game floor.
