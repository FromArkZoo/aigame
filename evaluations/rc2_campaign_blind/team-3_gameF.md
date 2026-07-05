# Team 3 — Game F verdict

> Copy this template to `team-3_gameF.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game F` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid. Actions: PLACE on an empty cell adjacent to any stone (waived while
  you have zero stones, and it re-arms after extinction — engine-verified), PASS, or MOVE
  one of your stones to an adjacent cell, overwriting an enemy stone there. After EVERY
  action (including passes) a cellular automaton applies once, evaluated from the ACTING
  player's perspective: empty cells with exactly 3 occupied neighbors, mixed 1-2 or 2-1,
  become the ACTOR's stone regardless of who has the majority; an enemy stone with exactly
  3 friendly + 1 enemy neighbors flips to the actor; any stone with zero occupied
  neighbors flips to whoever did NOT just... precisely: the actor's isolated stones flip
  to the opponent and the opponent's isolated stones flip to the actor. Classic capture
  and propagation are disabled. Win: first to own 30+ cells (>0.4659×64); turn-limit 100
  with most-stones tiebreak; double pass draws; super-ko converts repeating actions to a
  pass (checked on the post-CA position).
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Territory threshold fired twice (Line 1: P2 reached 30 stones at ply 60, winning 30–29;
  Line 2: I reached 30 at ply 54 as P2, winning 30–26). Double-pass draw fired once in the
  stress line (ply 3). No game reached the 100-step tiebreak.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules:
  Plenty. (1) Your very first stone flips to the opponent (isolated, 0F+0E) — the "gift
  opening". (2) A PASS still runs the CA: passing while owning the only isolated stone
  gives it away (verified: `27,64` flipped the stone back to P1). (3) The game-ENDING pass
  skips its CA step — the double-pass draw froze the board where the CA would otherwise
  have flipped a stone. (4) MOVE catastrophe: moving one stone of an adjacent pair to
  overwrite an enemy left BOTH stones isolated; the CA flipped both and I went from 2
  stones to 0 in my own action (engine-verified at Line 3 ply 5). (5) Edge and corner
  cells have <4 neighbors, so the 3F+1E/1F+3E flip patterns can never match there —
  border stones are CA-immortal, which quietly makes edge/corner farming the dominant
  strategy. (6) A lone stone fully surrounded by 4 enemies never flips (4F+0E is not in
  the table) — it can only be removed by MOVE-overwrite.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `64,27,28,35,36,43,34,44,42,51,52,45,212,245,275,50,243,58,37,57,29,49,20,56,19,48,21,40,33,59,12,32,11,60,45,24,13,25,18,16,10,8,4,0,3,1,5,61,6,62,14,63,22,55,30,47,38,54,7,39`
- Plan and what happened: I opened with PASS to dodge the gift-flip, making P2 place the
  first (defecting) stone. Early middlegame I found strong CA tactics: placing 34
  completed a 3F+1E pattern and flipped O@35; the MOVE-overwrite 212 ((4,4)→(4,5))
  simultaneously killed O@44 and flipped O@43, putting me up 8–2. But scripted P2
  counterattacked with its own overwrite (which birthed a stone inside my shape), then
  pivoted to farming the CA-immortal west column and south edge, harvesting "border
  births" (each placement at distance 2 from my wall created a 2F+1E empty cell that
  birthed a free stone for P2). The endgame became a pure parity race to 30.
- Result (winner, end cause, plies): P2 won 30–29 by territory threshold at ply 60. My
  opening PASS saved me a stone but cost me the odd tempo — at 29–29 it was P2's turn,
  and any safe placement won. Brutal, legible, and traceable to a ply-1 decision.

### Line 2 — you as P2
- Moves: `27,28,20,19,12,35,4,34,13,43,5,51,21,59,29,36,37,44,45,52,53,60,61,26,62,18,54,10,46,2,38,25,30,33,22,41,14,49,6,57,15,17,7,9,23,1,31,24,39,32,47,40,55,48,63,56` (game ended at ply 54)
- Plan and what happened: Scripted P1 opened with a placement, gifting me the first stone.
  I built a connected wall down column 3, claimed the doom-cell 36 before P1 could use it
  (an enemy stone at (4,4) would have made my 28 flippable), pre-empted P1's birth cell at
  52, and then farmed the entire west half plus the south — always placing edge-adjacent,
  immune cells while P1 mirrored down the east side. I denied every mixed-3 birth cell on
  my border; P1 got no free stones.
- Result: I (P2) won 30–26 by territory threshold at ply 54. The center column I owned
  meant my farm was simply bigger than P1's east strip; no drama at the end, just a
  counted-out win.

### Line 3 — adversarial / novelty-stress
- Moves: `27,64,64` and `64,27,28,35,176,36` (+ `--legal` probes)
- What you tried to break / stress, and what happened: (a) Pass ping-pong: P1 placed (stone
  flipped to P2), P2 passed — the CA on the PASS flipped the stone back to P1 — then P1
  passed and the double-pass draw fired, with the terminal pass's CA visibly skipped
  (board delta: none). A lone-stone game can thus end 1–0-ish as a "draw" in 3 plies.
  (b) Overwrite catastrophe: with an adjacent pair X@27,28 I moved 27 onto O@35 (action
  176). The move succeeded but vacating 27 isolated both my stones: the CA flipped the
  moved stone AND 28 to P2 — P1 went from 2 stones to 0 in its own action, and P2 stood
  at 2 with P1 extinct. (c) `--legal` after extinction confirmed the placement constraint
  re-arms ("every empty active cell"), though the isolation flip means the only cells
  where a re-entering player can actually KEEP a stone are those adjacent to enemy stones.
- Result: Draw by double pass at ply 3 in (a); self-extinction demonstrated in (b);
  re-arm confirmed in (c).

### Additional lines (optional)
Numerous short probes to decode CA behavior: verified that births go to the actor even
when the opponent holds the 2-majority around the cell, that a placement completing
3F+1E flips the enemy stone in the same step, and that neighbor ordering for MOVE ids is
west/east/north/south via `--legal` decoding.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Every action is really two moves: the placement/move itself plus a global CA harvest.
  A good move (1) scoops every mixed-3 empty cell on the board (they birth to YOU no
  matter the local majority), (2) completes 3F+1E surrounds to flip enemy interior
  stones, (3) never leaves any of your stones isolated or at 1F+3E, and (4) banks
  CA-immortal territory on edges and corners. The MOVE-overwrite is a scalpel — my
  action-212 combo killed one stone and flipped another in a single tempo — but it
  vacates the origin, and the isolation flip turns careless overwrites into suicide.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all?
  Yes, heavily in the middlegame: P2's counter-overwrite at ply 14 of Line 1 punished the
  hole my own overwrite left (its CA step birthed a stone INSIDE my shape); my
  pre-emptive capture of birth-cell 52 in Line 2 denied P1 a free +2. In the endgame the
  interaction fades: both sides farm disjoint immune territory and the game reduces to
  arithmetic — the only "response" that matters is denying border birth cells.
- Topology/board effects on strategy: The <4-neighbor rim is the dominant terrain
  feature: no flip pattern can match on edge/corner cells, so the rim is safe storage,
  and both winning strategies (mine and the script's) were rim-first farming. The
  interior is where all CA violence happens; interior stones are conditional assets.
- Emergent concepts you'd name (or "none observed"): "gift opening" (first stone always
  defects), "birth engineering" (creating the third mixed neighbor of an empty cell on
  your own action), "doom cell" (the one empty cell that would make an enemy stone
  flippable — worth taking defensively), "rim immortality", "overwrite suicide"
  (isolation flip after a careless MOVE), "parity endgame" (the race to 30 is decided by
  who holds the odd tempo when both farms saturate).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? High agency with a visible skill curve: Line 1's
  loss traces to my ply-1 PASS (tempo) and my mid-game trade decisions; Line 2's win
  traces to doom-cell/birth-cell denial. The CA is deterministic and fully readable if
  you do the work — nothing felt random — though the reading burden is heavy.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is "two-player Life meets Reversi": totalistic birth/flip tables come straight from
  the cellular-automaton tradition (Life variants like Immigration/black-vs-white Life),
  the flip-by-surround echoes Reversi/Ataxx, territory-threshold wins echo Go-ish scoring,
  and MOVE-with-overwrite echoes Ataxx jumps. One could claim it's a parameterized
  CA-board-game hybrid that any generator could emit by rolling a random transition
  table.
- Honest novelty assessment after arguing that case: The actor-perspective asymmetric CA
  — the same board position transforms differently depending on WHO just moved, and
  births always favor the actor — is genuinely unlike Reversi, Ataxx, or symmetric Life
  variants I know, and it produces original strategic concepts (rim immortality, birth
  engineering, pass-flip zugzwang) that I derived at the table rather than imported.
  Rules elegance is middling (a 9-entry lookup table is arbitrary-feeling), but the
  strategic identity is distinct. This is the most novel-feeling design I have evaluated
  in this pack so far.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — the CA-family resemblance argued in Phase 4 is
  structural, not a recognition of a specific prior game or score.
- P1-role experience sub-score (1-10): 4.3
- P2-role experience sub-score (1-10): 4.7
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 4 — P2 won both full games
  (30–29, 30–26), the gift-flip punishes whoever establishes first, and the pass-opening
  workaround still handed P2 the winning endgame parity in Line 1.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.6**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Both full games were decided races (one by a single stone at ply 60) in which every
  swing was traceable to a readable decision: my Line 1 loss follows causally from the
  ply-1 PASS and two mid-game trades, and my Line 2 win from doom-cell and birth-cell
  denial — that is real, learnable depth layered on a genuinely novel actor-perspective
  CA. The tactical combos (the 212 overwrite-plus-flip; the 34 surround-flip) were
  delightful to find and engine-verified. It anchors above R19's 4.375 for me on novelty
  plus tension, but is held below the 5.0 ceiling by real blemishes: a degenerate gift/
  pass opening, an arbitrary-feeling 9-entry rule table that makes the game nearly
  unlearnable without probing, endgames that collapse into farming arithmetic, and
  edge-case absurdities (self-extinction moves, immortal surrounded singletons, the
  terminal-pass CA skip). Overall: 4.6.
