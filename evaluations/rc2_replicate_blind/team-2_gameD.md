# Team 2 — Game D verdict

> Copy this template to `team-2_gameD.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game D` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 grid (64 cells), von Neumann (orthogonal) adjacency, no wrap. Players alternate placing one stone on an empty cell, with a hard constraint: the cell must be adjacent to at least one ENEMY stone (waived while you have zero stones, and the waiver re-arms if all your stones are flipped away). After each placement, custodian (Othello-style) capture runs along the three axis lines through the placed cell: consecutive enemy stones terminating on one of your stones flip to you. Win by connection, asymmetric goals: P1 connects the d1=0 face to the d1=3 face; P2 connects d2=0 to d2=3 (paths use board adjacency, own stones only). PASS is always legal; two consecutive passes end the game as a DRAW. 100-step limit, then most-stones tiebreak. Super-ko converts repetition-creating actions into passes.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Win condition fired in 3 of my 4 lines (Line 1: P2 connection at ply 14; Line 2: P2 connection at ply 20; Line 4: P1 connection at ply 17 — all three completions were delivered BY a custodian flip, not a plain placement). Double-pass draw ended Line 3 (deliberately triggered; engine reported "double pass -> draw" even at 12-vs-1 stones). Turn-limit tiebreak never fired in my play but is strategically live (see pass-stalling below).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Three genuine surprises, all engine-verified. (1) The enemy-adjacency placement constraint means you frequently CANNOT play the move a connection game trains you to want: completing cells and blocking cells next to only your own stones are illegal — I hit "ILLEGAL" twice trying moves that would be routine in Hex (e.g., ply 15 of Line 2: P1 cannot occupy (1,0,2) to defend a bracket because only his own stone is adjacent). (2) Stone count is monotonically non-decreasing (flips convert, never remove), so a previous position can never recur after a placement — the advertised super-ko rule appears to be dead code in this game; I could not construct any trigger. (3) Flipping a player to ZERO stones re-arms place-anywhere for them (verified at ply 19 of Line 3: "PLACE: every empty active cell"), and simultaneously the leader loses ALL placements (nothing is enemy-adjacent), which is what makes pass-stalling a real device.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `21,5,1,20,9,13,14,15,29,45,61,60,28,62`
- Plan and what happened: I (P1) opened center (1,1,1), built the classic bracket: 1=(1,0,0) then 9=(1,2,0) flipped P2's (1,1,0), giving me a d1-column of 3 with a one-move win threat at (1,3,0). Scripted-competent P2 blocked (13), counter-flipped my wing probe (15 re-flipped (2,3,0)), and captured my (1,3,1) probe with 45=(1,3,2) — which built P2 a d2-column (1,3,0..2). I then blundered instructively: 61=(1,3,3) "blocked" P2's completion cell, but that completion was actually ILLEGAL for P2 (no X adjacent — a fake threat), and my block handed P2 an adjacency anchor. P2 played 60=(0,3,3) (unflippable corner) and 62=(2,3,3), whose bracket flipped my (1,3,3) to O and completed P2's d2=0→d2=3 path on the spot. I verified there was no defense at ply 13: the block cell was illegal for me, the bracket anchor unflippable, and flip-completions admit no interposition.
- Result (winner, end cause, plies): P2 win, connection (win condition fired), 14 plies.

### Line 2 — you as P2
- Moves: `21,15,31,47,63,5,1,0,9,2,3,20,17,22,25,33,49,48,34,50`
- Plan and what happened: As P2 I played the corner-fortress strategy discovered in Line 1: 15=(3,3,0) is unflippable (edge-anchored on all three lines) and every P1 approach to it feeds me a bracket. P1 fed (3,3,1); I flipped via 47 building an unflippable d2-column to depth 2; P1 capped (3,3,3). I then took safe central territory, answered P1's Line-1-style column attack with the corner counter (0=(0,0,0) then 2=(2,0,0) beheaded his column by re-flipping (1,0,0)), captured the center twice (22 flipped (1,1,1); after his 25 recapture, 33 flipped (1,0,1) and gave me a second d2-column (1,0,0..2)). His 49=(1,0,3) blocked my column's face cell but hung to 48=(0,0,3) (unflippable corner) threatening 50=(2,0,3), whose bracket flips (1,0,3) and completes my column — he could not legally occupy the flip cell (only his own stone adjacent). 50 flipped (1,0,3) and won.
- Result: P2 (me) win, connection (win condition fired), 20 plies.

### Line 3 — adversarial / novelty-stress
- Moves: `21,5,1,37,9,13,64,4,64,6,64,0,64,2,64,8,64,10,63,64,64`
- What you tried to break / stress, and what happened: Three stress targets. (a) Zero-stone re-arm: I used d0-axis brackets (4+6, 0+2, 8+10) to flip every P1 stone while P1 passed; at P1=0 stones the engine re-armed place-anywhere (53 legal placements). (b) Leader starvation: with P1 at zero stones I had ZERO legal placements despite 12 stones — placement legality requires enemy adjacency, so annihilating the opponent paralyzes you. (c) Double-pass draw: after P1's re-arm placement (63), pass-pass ended the game as a DRAW at 12-vs-1 stones — confirming a lost player can pass-stall toward a draw whenever the leader's legal placements dry up before step 100. I also tried to trigger the super-ko rollback and established it is unreachable: every placement strictly grows the stone count, so no prior position can recur.
- Result: DRAW, "double pass -> draw", 21 plies.

### Additional lines (optional)
Line 4 — fairness check by construction. Moves: `51,21,17,1,0,33,2,3,20,5,22,37,9,13,12,10,14`. I replayed Line 2 under the d1↔d2 reflection with roles swapped (P1 takes the corner fortress at (3,0,3), P2 plays my Line-2 P1 script mirrored). Result: P1 win by connection at ply 17, completing (1,0,0)-(1,1,0)-(1,2,0)-(1,3,0) via the mirrored bracket flip. This engine-verifies that the asymmetric goals are geometrically equivalent — the same strategy wins for either role, and it wins 3 plies FASTER when the fortress player also has first-mover tempo.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  A good move does at least two of: (a) sits on a cell whose axis lines are edge- or own-stone-terminated (unflippable — corners are absolutely safe, faces safer than center); (b) sets up a custodian bracket whose far anchor you already own, so the flip threat is one placement, not two; (c) manages LEGALITY — either denying the opponent an adjacency anchor near their key cells or forcing them to hand you one near yours. The deepest recurring motif: your winning face cells are usually illegal for you (only your own stones adjacent), so wins are delivered by flipping an enemy stone that sits on your path — and flip-completions cannot be interposed against. All three decisive lines ended exactly this way.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Extremely responsive game. Every bracket threat I made had a real answer in at least one line: Line 1's (2,3,0) probe was met by 15, which both re-flipped the stone and dissolved my follow-up bracket (the flip removed the anchor); Line 2's center capture (22) was met by an immediate re-capture (25) using a different axis. The signature punishments are: re-flip along a second axis, and the "fake threat" call — correctly reading that an apparently winning completion is illegal for the opponent and ignoring it. Conversely the game punishes reflex-blocking brutally: my Line 1 loss traces entirely to blocking a fake threat and thereby legalizing P2's kill.
- Topology/board effects on strategy: The 3D orthogonal board is load-bearing. Each cell lies on exactly 3 capture lines, and edge/corner cells lose bracket lines — corners are unflippable fortresses, and a 4-long column whose flanks are edges (e.g. (3,3,*), (1,0,*) after support) becomes permanently safe. Because the two players connect along DIFFERENT axes, the same column is a win for one player and mere material for the other, which makes flipped stones genuinely dual-purpose. Minimal winning paths are only 4 stones, so the game is fast and every tempo matters.
- Emergent concepts you'd name (or "none observed"): (1) "Legality starvation / escort requirement" — you cannot approach your own goal without enemy stones nearby, so progress requires luring the opponent toward your target face. (2) "Fake threats" — completions that look forced but are illegal for the mover. (3) "Poisoned blocks" — defensive placements that legalize the opponent's next placement (Line 1's losing 61). (4) "Legality fuel" — keeping enemy stones alive on purpose so you retain legal moves (annihilation self-paralyzes, Line 3). (5) "Pass-stall swindle" — a lost player passes repeatedly; if the leader's placements dry up, double-pass forces a draw.
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decided everything. All three decisive games ended by concrete tactical sequences I could verify and, in Line 1, refute (the loss traces to one identifiable wrong move with a better alternative available). No hidden dynamics, no between-turn engine drift — the board only changes on placements. The one agency-limiting wart is the pass-stall draw, which can deny a strategically won position its win.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  "This is Othello × Hex on a 3D board": custodian capture is lifted verbatim from Reversi/Othello (the rules text even admits a vestigial capture-threshold field), the win condition is Hex/TwixT-style face-to-face connection with per-player goals, and 4×4×4 connection games and 3D Reversi variants both exist. Even the enemy-contact placement rule has precedent in contact-placement games. Under this reading the game is three known mechanics stapled together, and the asymmetric axis goals are just Hex's two-player coloring transplanted to 3D.
- Honest novelty assessment after arguing that case: The components are indeed all known, but the interaction is not reducible to any of the priors. Othello's strategy (mobility, parity, corner grabbing) survives only as "corners are safe"; Hex's strategy (ladders, bridges) is warped beyond recognition because you may not place next to only your own stones — no prior connection game I know forbids extending your own group into free space. The dominant dynamics of this game — legality starvation, fake threats, flip-delivered uninterposable connections, keeping enemies alive as placement fuel — do not exist in Othello, Hex, or their documented hybrids. This is a genuine hybrid with emergent play, not a re-skin; novelty is real but the parts are recognizable.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — I do not recognize this specific game or recall any prior score for it.
- P1-role experience sub-score (1-10): 4.5
- P2-role experience sub-score (1-10): 4.5
- Role-averaged sub-score: 4.5
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — the d1↔d2 reflection makes the roles geometrically equivalent (Line 4 engine-verified the same strategy winning for P1 that won Line 2 for P2), with at most a slight first-mover tempo edge (the mirrored win landed 3 plies earlier when the fortress player moved first).
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.5**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  This game earned the top of my range honestly: every decisive line (1, 2, 4) ended in a concrete, engine-verified tactical kill whose defense I exhaustively checked and found genuinely absent, and the losses were attributable to identifiable, learnable mistakes (Line 1's fake-threat block). The rule interaction produces at least five nameable emergent concepts (legality starvation, fake threats, poisoned blocks, legality fuel, pass-stall) none of which are inherited from the parent mechanics — that is the signature of real design depth rather than a mashup. I withhold the remaining half-point for two structural warts verified in Line 3: the pass-stall draw swindle can deny a won position, and mutual corner-fortress play plausibly collapses to an early double-pass draw at high skill, so perfect play may be drawish in an unsatisfying way. Against the anchors (R19's 4.375 the best prior mean, 5.0 never cleared), 4.5 for a single game with this much verified depth and only latent degeneracy feels right; anchoring down from initial enthusiasm (~4.7) per the drift warning.
