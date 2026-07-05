# Team 2 — Game E verdict

> Copy this template to `team-2_gameE.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game E` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid, free placement on any empty cell, plus MOVE actions relocating one of your stones to an adjacent EMPTY cell, and PASS. Go-style surround capture — and engine-verified, captures fire after MOVE actions too, not just placements. Suicide is legal and the zero-liberty stone persists (same engine family as my Game B). Win by owning 41+ cells (63.3% of the board); at 100 steps stone-majority decides; double pass = draw; super-ko rolls repeated positions back into passes. No CA, no influence field.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  The 41-stone threshold was never reached (maximum seen: 33). Line 1 ended as a double-pass DRAW at ply 77 — the board filled completely, so both players were FORCED to pass, freezing a 33-31 P1 lead into a draw. Line 2 ran to the step-100 piece-count tiebreak (P1 wins 30-24). One natural super-ko rollback occurred mid-game (step 62).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) MOVE actions trigger captures (my (3,1)→(2,1) relocation captured a stone) — the rules text only says "after your placement." (2) The full-board freeze: when the last cell fills, no placements or moves exist, both sides must pass, and the leader is robbed by the double-pass draw — the majority tiebreak only exists at step 100. (3) Suicide-persistence means eyes confer NO life (see Line 2's kill of a two-eyed group). (4) Super-ko fired naturally in normal play (a capture-recapture cycle at step 62), unlike in my other games where I had to engineer it.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,36,20,29,34,43,11,18,25,38,45,52,13,22,41,50,9,54,31,59,4,32,2,3,16,12,5,19,10,21,17,26,148,20,35,42,33,14,86,5,4,7,3,47,13,6,24,61,40,57,37,44,23,46,30,15,39,255,47,287,55,317,63,60,53,273,52,49,58,32,48,56,0,1,8,64,64`
- Plan and what happened: I drove P1 with a liberty-aware capture-race policy (built from the printed rules and validated move-for-move against the engine — the entire 75-ply line replays identically). The game was a dense capture battle: multiple groups died on both sides (cells like (3,0),(4,0),(5,0) changed hands repeatedly), MOVE actions were used to flee ataris and to deliver capturing blows (e.g. actions 148, 86, 255). I built a winning count — 33-31 — and then the board filled completely: with zero empty cells there are no legal placements or moves, both sides were forced to pass, and the double-pass rule declared a DRAW, voiding my lead.
- Result (winner, end cause, plies): DRAW, double pass (forced by full board) at ply 77, with P1 ahead 33-31.

### Line 2 — you as P2
- Moves: `1,16,9,17,8,18,10,19,11,12,3,4,27,0,36,2,29,34,43,38,45,52,22,41,50,54,25,32,13,31,59,47,39,61,46,55,23,189,31,37,212,36,28,35,26,42,33,51,53,276,244,51,62,63,313,62,309,61,40,44,43,51,49,24,221,39,217,41,38,48,40,6,9,55,62,21,20,1,11,3,8,10,47,14,15,5,56,21,42,13,54,63,313,62,254,47,48,30,7,41`
- Plan and what happened: Scripted P1 opened with a textbook Go corner group — six stones with two real eyes at (0,0) and (2,0), unconditionally alive by Go rules. As P2 I demonstrated that this game has NO life: I walled the outside liberties, STUFFED eye (0,0) with a zero-liberty suicide stone (it persists and can never be captured), then filled eye (2,0) — the entire six-stone group died at ply 16 (P1 reduced to 2 stones). That +6 swing held as a 24-20 lead through ply 62 (where a capture-recapture loop hit super-ko and my recapture was rolled back into a pass). Then I lost the game: in the long endgame my play fed stones into P1's counter-races — P1 gained 10 stones over the final 38 plies while I gained none, and P1 took the step-100 count 30-24.
- Result: P1 win, max-turns piece-count tiebreak (30 vs 24), 100 plies. Engine-verified verbatim including the step-62 rollback.

### Line 3 — adversarial / novelty-stress
- Moves: `8,9,1,45,17,46,11,47,109` (move-capture), `8,9,1,2,17,18,45,11,10,9` (super-ko), `8,9,1,45,17,46,11,47,109,9` (suicide persistence)
- What you tried to break / stress, and what happened: (1) MOVE-capture: relocating (3,1)→(2,1) removed the surrounded O stone — confirmed captures fire on relocation. (2) Super-ko: an immediate ko recapture was rolled back and treated as a pass. (3) Suicide: O placed at (1,1) with zero liberties and persisted. (4) The structural stress tests emerged in Lines 1-2 by themselves: the full-board freeze-draw (Line 1) and the eye-stuffing no-life kill (Line 2). Combined, they imply a losing player can pursue a draw by stuffing the board toward the freeze — 1-cell gaps in enemy territory are permanently claimable (the stuffed stone is uncapturable), so the leader must burn plies self-filling gaps to deny this.
- Result: All probes behaved as documented; no crashes or inconsistencies; the engine's liberty/capture accounting matched my model on 175+ verified plies.

### Additional lines (optional)
None beyond the probes — Lines 1 and 2 each ran to a terminal state.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Pure liberty warfare: count liberties, win capture races, keep your groups' liberty counts above the opponent's attack tempo, and use MOVE to flee ataris or deliver the final liberty-fill (a relocation both vacates a cell and can capture). Since nothing is ever alive (eyes are stuffable), "settling" a group means keeping it big and liberties high, not eye-making — a genuinely different instinct from Go. In the endgame, gap parity dominates: 1-cell gaps are opponent-claimable forever, 2-cell gaps are capture-bait.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Yes, constantly — every extension changed a race's outcome, and unanswered ataris cost whole groups. My Line 2 kill punished P1's Go-style faith in two eyes; P1's endgame comeback punished my loose shapes with 10 stones of counter-captures. The super-ko rollback at step 62 even punished capture-recapture cycles.
- Topology/board effects on strategy: Plain 8×8: corners/edges reduce liberties, making edge groups fast to attack; the board's small size relative to the 100-step budget means it can FILL, which is where the freeze-draw lives. The 41-cell threshold (63%) is practically decorative — with both players placing every turn, nobody can own 2/3 of the board without the opponent being nearly annihilated.
- Emergent concepts you'd name (or "none observed"): "no-life" (eyes don't work — suicide-persistence lets eyes be stuffed one by one), "freeze-draw" (full board = forced double pass = leader robbed), "gap parity endgame" (1-cell gaps are opponent property, self-filling is mandatory), "move-capture tempo" (relocations as double-purpose liberty plays).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Fully choice-driven, no autonomous dynamics. My Line 2 collapse was my own endgame play, and Line 1's frozen draw was foreseeable and (probably) avoidable with better space management. The agency is real but the reward structure funnels everything into stone-count accounting, which blunts the drama of individual captures.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is stone-count Go with the serial numbers filed off: free placement, surround capture, super-ko — that's Go; winning by stone majority is stone-scoring/no-pass Go; even the "no suicide rule → weird life-and-death" territory is explored in Go variants (e.g. no-pass Go endgames where players must fill). The MOVE action is the only non-Go ingredient and it's stock in dozens of abstracts.
- Honest novelty assessment after arguing that case: Mostly a re-skin. The genuinely distinctive content is emergent from implementation quirks rather than design: suicide-persistence abolishing life entirely (eye-stuffing kills), captures firing on relocations, and the full-board freeze-draw. Those change strategy substantially — Go instincts actively mislead — but they read as side-effects, and two of them (freeze-draw, unreachable threshold) are structural defects rather than ideas. Low novelty with interesting accidents.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): the design is clearly Go-derived (stone-scoring Go with relocations); I don't recognize it as a specific published game and recall no prior score.
- P1-role experience sub-score (1-10): 4.0
- P2-role experience sub-score (1-10): 4.0
- Role-averaged sub-score: 4.0
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 2 — P1 held the count lead in both full games (33-31 frozen draw; 30-24 win), consistent with the first mover acting first in every capture race of a majority-count game; the effect looks mild but consistently one-directional.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.6**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The moment-to-moment play is legitimately engaging — Line 1 was a 75-ply capture brawl with move-flees and race reversals, and Line 2's eye-stuff execution (killing a "two-eyed alive" group, +6 swing) is the kind of rule-exploiting plan that rewards understanding the actual game rather than its Go ancestry. But the macro-structure leaks badly: the nominal win condition (41 cells) was never remotely reachable, so every game is really a step-100 counting race; the full-board freeze turned my earned 33-31 lead into a draw by FORCED double-pass, an outcome the trailing player can deliberately steer toward; and eye-stuffing/gap-parity gives late-game play a degenerate accounting flavor. Real tactics, broken framing — slightly below the R20/R21 anchors' neighborhood: 3.6.
