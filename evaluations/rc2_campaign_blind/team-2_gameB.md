# Team 2 — Game B verdict

> Copy this template to `team-2_gameB.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game B` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  8×8 orthogonal grid, free placement anywhere empty, alternating turns. Go-style surround capture: after your placement, any adjacent enemy group with zero liberties is removed. Hex-style asymmetric goals: P1 connects the y=0 face to y=7, P2 connects x=0 to x=7, by orthogonal paths of own stones. An influence field accumulates per placement (strength 0.715, decay 0.751, radius 3) and is viewable with --values, but no rule reads it — it is mechanically inert, including the documented "ghost influence" of captured stones. Super-ko rolls repeated positions back into a pass. Double pass = draw; at 100 steps, stone majority wins. Crucially (engine-verified): suicide is LEGAL and the suicided stone PERSISTS at zero liberties — capture only ever fires against the placer's enemy.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection wins in all three main lines (P2 at ply 48 in Line 1 as-played; P1 at ply 59 in the corrected variation; P2 at ply 30 in Line 2). No turn-limit games (though my analysis found sealed positions where stone-majority would decide); no double passes.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: (1) Zero-liberty stones survive: O played into a cell with all four neighbors X — no capture, no removal, and since X can never again place adjacent to it, it is a PERMANENT blocker. This generalizes into the "suicide-replay" exploit: any 1-cell gap enclosed by your own stones can be taken forever by the opponent (capture their first intrusion and their replay is immortal). (2) Super-ko genuinely converts a ko recapture into a pass (engine flag verified). (3) The influence field really is dead weight — captures, wins, and legality never consult it.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,28,35,43,34,42,26,33,50,41,49,40,44,51,36,52,20,29,18,10,12,4,11,3,13,5,14,6,7,2,9,1,0,46,19,60,48,32,25,24,16,3,4,45,37,53,38,47` (as played, P2 wins ply 48); corrected variation: `...,45,37,53,47,54,55,62,63,30,31,22,23,15,38,21,39` (P1 wins ply 59)
- Plan and what happened: I drove a center opening into a two-front war. The high point was a 25-ply plan that worked exactly: my row-1 stones under P2's row-0 blocking crawl reduced the whole crawl to two liberties, and ply 33 captured SEVEN stones at once, opening five parallel routes to the north face. Then I threw the game away: chasing P2's 11-stone southern dragon, I filled outside liberties while its "desperate" extensions along row 5 were simultaneously P2's left-right connection — P2's (7,5) at ply 48 won by connection. In the corrected variation (block the edge at (7,5) first, then take the x=7 column cells), P1 wins by connection at ply 59 down the east edge. A further sub-variation punished me again for edge-crawling: P2's (7,4) captured my five first-line east-edge stones in one move.
- Result (winner, end cause, plies): As played: P2 win, connection, 48 plies. Corrected variation: P1 win, connection, 59 plies.

### Line 2 — you as P2
- Moves: `27,43,45,44,46,53,52,51,60,61,59,58,52,60,52,59,54,62,63,55,47,63,57,49,56,48,57,56,57,50`
- Plan and what happened: Applying Line 1's lessons, I built my left-right wall SOLIDLY (no capture-protected gaps) one row below P1's advance and bypassed obstructions via row 7. Scripted P1 fought hard: a cutting stone at (4,6) (I captured its 3-stone chain at ply 12), a re-cut that I re-captured at ply 14, then the suicide-replay at ply 15 creating an immortal X stone inside my wall — which I bypassed via (3,7). P1 blocked the east edge (I captured the (7,7) blocker, merged out of atari at ply 22), then the west (ply 26: my (0,6) captured his two row-7 blockers; ply 28: (0,7) captured the re-block; ply 29: his second immortal suicide stone at (1,7), bypassed again). Ply 30's (2,6) completed the path (0,7)-(0,6)-(1,6)-(2,6)-(3,6)-(3,7)-(4,7)-(5,7)-(5,6)-(6,7)-(7,7).
- Result: P2 win, connection, 30 plies.

### Line 3 — adversarial / novelty-stress
- Moves: `8,9,1,2,17,18,45,11,10,9` (super-ko), `8,9,1,2,17,18,45,25,10,9` (suicide-persistence), plus --values inspections
- What you tried to break / stress, and what happened: (1) Built a textbook ko: X captured the O stone at (1,1) with (2,1); O's recapture at (1,1) was flagged "SUPER-KO: rolled back and treated as a PASS" — verified. (2) In the mis-coordinated variant, O played (1,1) with all four neighbors X: legal, no capture, and the stone persists at zero liberties, permanently uncapturable — the discovery that reshaped all later wall theory. (3) Influence field: values accumulate and captured stones' influence remains with original sign (ghost influence), but nothing mechanical ever reads it. (4) The suicide-seal theory (a dragon self-filling its last liberty to become an uncapturable zero-liberty wall) follows from the verified persistence rule; in my actual endgame test the "seal" move turned out to be a legitimate 5-stone counter-capture instead — the engine's liberty accounting was consistently correct and my hand-reading was the thing that broke, twice.
- Result: Both probes behaved as the rules state; super-ko rollback and zero-liberty persistence confirmed; no crash or inconsistency found.

### Additional lines (optional)
The (7,1)/(7,4) sub-variation of Line 1 (moves `...,15,38,39,61`): P2's (7,4) captured my entire 5-stone east-edge chain — first-line crawls without eyes die exactly as in Go.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Every good move does two jobs: your blocking stones lie on your own winning line (P1's vertical blocks are P2's horizontal path cells and vice versa), so the game funnels both players into the same contact seams. Within a seam, Go tactics decide: count liberties before shape, never crawl the first line, capture blockers by surrounds, and never rely on a 1-cell gap (suicide-replay makes it opponent property). And above all, re-check the opponent's connection threat every ply — my Line 1 loss came from one ply of forgetting that a "fleeing" group was also a winning path.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Absolutely — this is the most response-driven game of my set. P2's row-0 crawl was punished by a 7-stone capture; my liberty-filling was punished by a connection win; P1's cutting stones were punished by 3-stone captures; my east-edge chain was punished by a 5-stone counter-capture; each immortal suicide-block was answered by a one-move bypass. Nearly every move in Lines 1-2 was forced or punishing.
- Topology/board effects on strategy: The plain 8×8 grid means edges are death for crawling groups and corners are capture traps ((7,7) died with one move). Both goals crossing the same board makes every wall dual-purpose, concentrating play into one or two seams. The 100-step stone-majority fallback looms over sealed positions and would reward degenerate suicide-stuffing if reached.
- Emergent concepts you'd name (or "none observed"): "dual-purpose dragon" (a group that is simultaneously escaping capture and completing its owner's connection — the thing that beat me), "suicide-replay immortality" (zero-liberty stones as permanent cuts), "bypass discipline" (always keep a second linking row available), "capture-race herding" (fights push stones in the winner's goal direction).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Entirely my choices — the engine is deterministic with no autonomous dynamics (the influence field does nothing). My Line 1 loss was a pure tactical error, and correcting a single move (ply 47) flipped the result; that is maximal agency.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  This is very close to Gonnect (Go rules with a connection win) with a dash of Hex: free placement, surround capture, super-ko, orthogonal connection goals. The differences — per-player asymmetric goal axes, a stone-majority turn-limit, an inert influence field — read as parameter noise, and the suicide-persistence rule could be dismissed as an unintended implementation quirk of "no suicide rule coded" rather than a designed mechanic.
- Honest novelty assessment after arguing that case: Largely a known design. The asymmetric goals do change opening theory versus Gonnect (each player has a preferred axis, so seams orient predictably), and zero-liberty persistence — whether intended or not — creates genuinely new wall theory (the suicide-replay cut and its bypass discipline dominated my Line 2). But the ghost-influence field is confirmed dead weight, several rule fields are self-described vestigial, and the core loop is recognizably Go-plus-connection. Low-to-moderate novelty as a design; high polish as an emergent tactical experience.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): I recognize the strong resemblance to Gonnect (Go-rules connection game); I do not recognize this exact variant and recall no prior score.
- P1-role experience sub-score (1-10): 4.5
- P2-role experience sub-score (1-10): 5.0
- Role-averaged sub-score: 4.75
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — across my lines P2 won at plies 48 and 30 and P1 won the corrected line at ply 59, with each loss traceable to a specific tactical error rather than structure; free placement removes the commitment asymmetry that plagued similar games, leaving only P1's mild first-move tempo.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.2**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  As a played experience this was the strongest of my set: Line 1 contains a genuinely dramatic arc (a 25-ply plan culminating in a 7-stone capture at ply 33, followed by my scripted opponent legitimately beating me at ply 48 with a dual-purpose dragon — the game punished a one-ply lapse in threat-reading), and Line 2 shows deep, learnable counterplay (solid walls, bypassing immortal suicide-cuts, three exact capture sequences). Tactical agency is total and every mechanic except one earns its keep. It scores below its play quality on design grounds: the influence field is verified dead weight, several fields are self-described vestigial, the suicide-persistence quirk (load-bearing in my lines) looks unintended and threatens degenerate stone-majority endgames, and the design itself is a recognizable Gonnect variant. Better than R8's 4.10 on play depth, held under the R19 anchor by the novelty discount and design noise: 4.2.
