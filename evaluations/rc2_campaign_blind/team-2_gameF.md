# Team 2 — Game F verdict

> Copy this template to `team-2_gameF.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game F` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid. Actions: PLACE (must touch ANY stone, either color; anywhere when you have zero stones), PASS, and MOVE (relocate one of your stones to an adjacent cell, overwriting an enemy stone there). After every action a CA step runs from the actor's perspective. Effective entries on this ≤4-neighbor board: empty cells at (1 friendly, 2 enemy) or (2,1) become the actor's; the actor's own stone at (0,0) — isolated — or (1,3) flips to the OPPONENT; an opponent stone at (0,0) or (3,1) flips to the actor. The CA never removes stones, only flips/births; the only removal is MOVE-overwrite. Win at 30+ stones (>46.6% of board); 100-step limit → stone majority; double pass = draw; super-ko rolls repeats back into a pass.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  The 30-stone threshold was NEVER reached in any line (max seen: 26). Both full-length games ended by max-turns piece-count tiebreak (P2 26-14; P1 25-16 in the mirror). Two draws by double pass: the rational 2-ply draw, and an accidental one where a super-ko rollback (counted as a pass) chained with a real pass.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) The isolation rule makes the game's FIRST placement a donation: P1's opening stone flipped to P2 on P1's own action (engine: `.->O@(3,3)`, P1=0 P2=1). (2) A pass donates a lone stone right back (`O->X@(3,3)`) — the opening is a hot-potato. (3) A super-ko rollback is literally a pass, so it can complete a double-pass and END the game as a draw (verified at ply 13). (4) MOVE is a landmine: relocating my connector stone orphaned two of my own stones, and the (0,0) rule flipped both to the opponent on my own action — one move lost me 2 net stones.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `64,27,19,11,18,10,20,2,9,1,28,71,1,29,0,36,37,108,8,73,141,2,109,101,105,11,101,17,25,34,167,33,24,207,35,43,213,101,172,69,135,129,71,65,41,199,32,165,137,163,199,112,11,138,109,3,106,141,109,139,4,13,81,5,78,0,18,106,79,74,81,106,73,103,77,85,5,136,78,70,14,79,139,134,17,30,33,38,124,45,210,6,15,78,31,83,85,112,51,243`
- Plan and what happened: As P1 I refused the poisoned opening: I PASSED. Scripted P2 declined the mutual draw by placing — and its stone flipped to me. From there both sides played the strongest policy I had (a depth-2 search over a rules-derived CA calculator that I first validated to reproduce a full 100-ply engine game move-for-move). The +1 donation snowballed steadily through birth-denial and 3v1 flip exchanges; nobody ever came near the 30-stone threshold.
- Result (winner, end cause, plies): P1 win, max-turns piece-count tiebreak (25 vs 16), 100 plies. Engine-verified verbatim, no rollbacks.

### Line 2 — you as P2
- Moves: `27,19,11,18,10,20,2,9,1,28,71,1,29,0,36,37,108,8,73,141,2,109,101,105,11,101,17,25,34,167,33,24,207,35,43,213,101,172,69,135,129,71,65,41,199,32,165,137,163,199,112,11,138,109,3,106,141,109,139,4,13,81,5,78,0,18,106,79,74,81,106,73,103,77,85,5,136,78,70,14,79,139,134,17,30,33,38,124,45,210,6,15,78,31,83,85,112,51,243,184`
- Plan and what happened: The exact mirror: scripted P1 opened (donating its first stone to me), and I drove P2 with the same policy. The game is the same sequence one ply shifted — the two lines together demonstrate that the ENTIRE 100-ply game is determined by who eats the opening donation. Mid-game featured heavy MOVE usage by both sides (repositioning instead of placing preserves the (2,1)/(1,2) birth geometry), and the margin grew from +1 to +12.
- Result: P2 win, max-turns piece-count tiebreak (26 vs 14), 100 plies. Engine-verified verbatim.

### Line 3 — adversarial / novelty-stress
- Moves: `27,28,26,20,25,21,34,12,168,64,199,64,168` (super-ko); `27,28,26,20,25,21,34,12,19,22,35` (3v1 flip); `27,28,26,20,25,21,34,12,170` (overwrite backfire); `64,64` and `27,64` (opening probes)
- What you tried to break / stress, and what happened: (1) Opening degeneracy: `64,64` is an immediate draw; any first placement donates; a pass with a lone stone on the board donates it back — so from the empty board, rational play by both sides is a 2-ply draw, and every decisive game requires someone to voluntarily accept -1. (2) Super-ko: shuffling a stone out and back (168/199/168 with opponent passes between) triggered the rollback — and because a rolled-back action counts as a pass, it completed a double-pass and ended the game as a DRAW at 3 stones to 5: a repetition attempt is a draw trigger, exploitable by a losing player as an escape hatch. (3) The (3,1) conversion works as advertised: placing my third stone around O@(3,3) flipped it (`O->X@(3,3)`) for a +2 swing. (4) MOVE-overwrite: capturing O@(3,3) by overwrite succeeded but orphaned my (1,3) and (2,4) stones, both of which the isolation rule flipped to O on my own action — net -2 for a "capture."
- Result: super-ko line: DRAW (double pass via rollback), 13 plies; flip demo: +2 swing verified; overwrite demo: catastrophic backfire verified.

### Additional lines (optional)
Baseline: unmodified depth-2 self-play from a P1 opening placement — P2 wins 26-14 at the turn limit (identical to Line 2). Method note: my calculator reproduced full engine games exactly (all 100 plies, both lines), so all quoted dynamics are engine-verified, not simulated.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Keep every stone connected to at least one other stone (the (0,0) isolation flip converts strays to the enemy on your OWN action), assemble 3-vs-1 envelopes to flip enemy stones (+2 swings), claim (2,1)/(1,2) birth cells before the opponent's action does, and use MOVE only when the relocation doesn't orphan anything — which is rare and why moves that look like free captures are often net losses.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Yes at the tactical level: birth cells belong to whoever acts next, so every (2,1) configuration you leave is the opponent's on their ply; 3v1 envelopes force the defender to reinforce or lose the stone. But strategically, counterplay never overcame the opening donation in equal-strength play — the margin only grew.
- Topology/board effects on strategy: The flat 8×8 board (max 4 neighbors) makes the effective CA table tiny: only (1,2)/(2,1) births and (0,0)/(1,3)/(3,1) flips can ever fire — the (4,x)/(x,4) entries are dead letters on interior cells. Edges reduce neighbor counts, making edge stones easier to 3v1 (only 3 neighbors needed... in fact a 2-neighbor corner stone can never satisfy (3,1) — corners are flip-proof).
- Emergent concepts you'd name (or "none observed"): "opening donation / hot-potato" (the first placement is a gift; passes gift lone stones back), "isolation suicide" (breaking your own connectivity flips your stones), "rollback draw-trap" (super-ko + double-pass interaction lets a loser force a draw via engineered repetition), "overwrite backfire" (MOVE captures that orphan neighbors are net-negative).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? At the ply level, choices matter (flips, births, connectivity). At the game level, agency is hollow: rational play is a 2-ply draw, and once someone accepts the donation, my two mirrored 100-ply games suggest the outcome is essentially decided at ply 1 under equal strength. The win threshold (30) was never within reach, so every real game is a slow count race to the turn limit.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is Game-D's actor-perspective CA formula transplanted to a flat 8×8 grid with a smaller table — i.e., arguably a re-parameterization of a sibling design rather than a new game — and the genre (two-color Life variants, p2life/Immigration) is established prior art; the MOVE action is stock (Amazons/queen-move games have relocation, and overwrite-capture is ordinary).
- Honest novelty assessment after arguing that case: The isolation hot-potato rule ((0,0) flips BOTH ways depending on cell ownership) is genuinely unusual — I know no prior game where placing the first stone donates it, or where a pass returns it. But everything novel about it is dysfunctional: it degenerates the opening into draw-or-donate, and combined with the unreachable 46.6% territory threshold it reduces the game to a turn-limit counting race with a preordained winner. Novel table, broken game.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — genre recognized (two-player CA territory race, sibling of my Game D), specific game and scores unknown.
- P1-role experience sub-score (1-10): 2.5
- P2-role experience sub-score (1-10): 3.0
- Role-averaged sub-score: 2.75
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 4 — the player to move first must either offer a draw (pass) or donate a stone (engine-verified flip of the opening placement), and my two mirrored 100-ply games show the donation recipient winning by +9 and +12 with identical policies, so the structural burden falls on P1.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.0**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The tactical layer is not empty — Line 3's 3v1 conversion, the birth-cell tempo economy, and the connectivity discipline forced by the isolation rule are real decisions, and the overwrite-backfire is a genuinely instructive trap. But the game is broken at the root: rational play from the empty board is a verified 2-ply draw; every decisive game requires a voluntary self-handicap; my mirrored Lines 1 and 2 (P1 25-16, P2 26-14, both engine-verified over 100 plies) show that handicap deciding the whole game under equal play; the nominal win condition (30 stones) was never approached, so all real games devolve into turn-limit counting; and the super-ko rollback doubles as a draw-escape exploit for a losing player. Those are disqualifying structural defects that place it clearly below the playable-but-flawed anchors R20/R21: 3.0.
