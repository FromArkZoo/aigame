# Team 1 — Game D verdict

> Copy this template to `team-1_gameD.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game D` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  A 3^4 torus (81 cells, 4 axes of size 3). Because each axis wraps with only
  3 cells, every axis-line of 3 cells is a mutual triangle, every cell has
  exactly 8 neighbors (±1 on each axis), and the graph diameter is 4. Players
  alternate placing one stone on an empty cell adjacent to their own stones
  (waived while a player has zero stones, and this re-arms after total
  annihilation — engine-verified in my Line 3). After EVERY action (including
  passes) one synchronous totalistic CA step runs *from the acting player's
  perspective*: the 17 non-identity entries birth stones on mixed-count empty
  cells (mostly 2F+1E and 1F+2E → actor's stone), empty weakly-supported
  stones (e.g., own stone at 0F+3E dies; enemy stone at 3F+0E or 5F+1E dies).
  First to own ≥17 of 81 cells wins; 98-step limit with most-stones tiebreak;
  two consecutive passes draw; super-ko rolls repeating actions back into
  passes (checked post-CA).
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Win condition fired in Lines 1 and 2 (steps 18 and 15 of 98 — far short of
  the limit, because CA cascades of +3..+5 stones per action accelerate the
  race brutally). Double-pass draw ended Line 3 (engineered stress). I never
  reached the turn-limit tiebreak; decisive cascades arrive long before
  step 98.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: Three surprises, all engine-confirmed as rule-consistent:
  (1) a placement can die in its own CA tick yet still kill an adjacent enemy
  stone ("suicide-strike": Line 1 ply 14, O placed 46, the stone died at 1F+5E
  while my 52 died at 5F+1E — net delta was a pure assassination); (2) a pure
  suicide placement produces "board delta: none" (Line 3 ply 13); (3) the
  1F+2E→actor rule means any mixed 2:1 contact cell is claimed by *whoever
  acts next*, so "my" birth sites are also the opponent's birth sites — only
  tempo decides.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `40,41,39,38,37,44,31,35,49,53,29,33,27,46,48,6,1,11`
- Plan and what happened: I raced with a compact 2×2 block and predicted the
  CA precisely enough to engineer a birth (my ply-5 placement at 37 birthed 36
  via 2F+1E, exactly as I calculated: 4–2). Scripted-P2's reply 44 was a
  double-birth coup (+3: 42 and 43 both 1F+2E from his perspective) — 4–5.
  The opening plane filled; the war moved to fresh layers with alternating
  harvest cascades (my 49 was +5; his 35 and 53 +3 each). At 13–12 he played a
  suicide-strike (46) killing my 52, and after the slab froze he invaded layer
  d3=0 first (6). Deep search confirmed I was already lost: my best defense 1
  (+3, reaching 16 — one stone short) left him the +5 cascade 11.
- Result (winner, end cause, plies): P2 wins by win condition (18 ≥ 17),
  step 18; final 18–16.

### Line 2 — you as P2
- Moves: `40,41,13,68,12,81,3,5,21,32,49,58,18,2,24` (I drove O: 41, 68,
  pass, 5, 32, 58, 2; P1 was scripted as a compact racer that harvests any
  ≥+2 cascade)
- Plan and what happened: I contested immediately (41), then took a +3
  triangle harvest with 68 (1→4). His counter-harvest 12 (+3) filled the
  shared plane with him holding 5/9 and me structurally behind. My zugzwang
  pass-probe failed — he had safe +1 expansions while all mine fed him. The
  seesaw was real (my 32 harvested +4, briefly 9–10), but each of my cascades
  left more counter-harvest food than his; from 13–10 down my nets were ≤ +1
  while he kept +3s. His final 24 cascaded to 17.
- Result: P1 wins by win condition (17 ≥ 17), step 15; final 17–14.

### Line 3 — adversarial / novelty-stress
- Moves: `0,40,81,39,81,36,81,9,81,18,81,27,0,81,0`
- What you tried to break / stress, and what happened: I engineered, and the
  engine handled cleanly, all of: (1) total annihilation — O's 27 was the
  third enemy neighbor of my unsupported stone at 0 (3F+0E) and killed my
  last stone; (2) placement re-arm — with zero stones I legally placed at a
  cell adjacent to no friendly stone; (3) pure suicide — that placement at 0
  (0F+3E) died in its own tick, "board delta: none"; (4) super-ko — replaying
  0 after O's pass recreated a prior position and the engine rolled it back
  to a PASS with an explicit flag, which completed (5) the double-pass draw.
  No crashes, no inconsistent states, every flag fired as documented.
- Result: DRAW by double pass (with super-ko rollback), step 15; final 0–6.

### Additional lines (optional)
I verified every single ply of Lines 1–2 against an independent CA
re-implementation I wrote from the rules text alone; the engine and my model
agreed on all births/deaths/counts at every step, including +5 cascades. That
is strong evidence the printed rule table is exactly what the engine runs.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Scan for "ripe" cells — empties that after your placement hit exactly
  2 friendly + 1 enemy or 1 friendly + 2 enemy — and place to convert them
  (each conversion is +1 beyond your placement; multi-conversion "coups" are
  +2/+3 extra). Symmetrically, never leave a mixed 2:1 cell or a touchable
  pure pair on the board at the end of your turn, because the opponent-actor
  claims it. Good moves harvest AND leave no food.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Counterplay is the whole game:
  the responder systematically profits (initiating contact structures feeds
  the opponent's harvest — this decided both decisive lines in opposite
  directions). Over-extension is punished automatically: every cascade you
  win leaves fresh mixed frontier the opponent harvests back (seesaw in
  Line 2: 6→10, then his +4 reply). The suicide-strike is a dedicated
  punishment tool against exactly-one-support stones.
- Topology/board effects on strategy: The size-3 torus dominates everything:
  each line is a 3-clique so a 2-stone line "pair" instantly makes the third
  cell contested; there are NO buffers (any two parallel layers are
  adjacent), so racing apart is geometrically impossible and contact is
  forced early; diameter 4 means no part of the board is ever safe. Fresh
  layers above a full mixed slab are explosive — the second invader usually
  wins the cascade war there (Line 1's finish).
- Emergent concepts you'd name (or "none observed"): "coup" (multi-birth
  placement), "suicide-strike" (sacrificial placement that assassinates),
  "responder's harvest" (mixed 2:1 cells belong to whoever moves next),
  "cold war" (frozen positions where every placement loses material, so
  passes and zugzwang probes appear), "layer-invasion timing".
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Agency is high but calculation-gated:
  the CA is deterministic and I could predict every birth/death exactly, so
  outcomes traced directly to move choices (my engineered birth at 36, the
  engineered stress line). The flip side: without deep calculation the
  cascades feel like chaos; my depth-4 search misjudged a position that
  depth-5 showed was lost, which is real depth but also real opacity.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is a two-player colored Life variant (family of Immigration Game /
  p2life / Black-vs-White Life) crossed with Go-like placement: alternating
  stone placement plus a totalistic birth/survival CA on a torus, race to a
  cell-count majority-style target, super-ko. Every ingredient exists in
  prior art: two-color CA combat games, adjacency-constrained growth
  (expansion games), stone-count victory, torus boards.
- Honest novelty assessment after arguing that case: The composite is
  genuinely more than the sum: (1) the CA runs *per action from the actor's
  perspective* rather than in synchronized generations, which creates the
  tempo-based "responder's harvest" economy that has no analogue in p2life;
  (2) the 3^4 torus with triangle lines and zero buffers is a materially
  different arena from any 2D Life board; (3) the asymmetric 17-entry table
  (births only on mixed neighborhoods) forces contact-seeking rather than
  Life-style pattern gardening. Moderately-to-substantially novel; not a
  re-skin, though the family resemblance to two-player Life variants is
  honest prior art.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — I do not recognize this specific game or
  recall any prior score for it; the p2life family resemblance noted in
  Phase 4 is generic prior art, not recognition.
- P1-role experience sub-score (1-10): 4.5
- P2-role experience sub-score (1-10): 4.3
- Role-averaged sub-score: 4.4
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — each side won
  once in my decisive lines (P2 won Line 1, P1 won Line 2), and the dominant
  advantage was positional (whoever avoids initiating contact structures),
  not seat order; P1's one-tempo race edge is real but was fully offset by
  the responder's harvest dynamic in actual play.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.4**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  This is the strongest kind of blind entry: deterministic, fully verifiable
  rules that produced three genuinely different games — a cascade loss from a
  winning-looking race (Line 1: I hit 16 of 17 and was dead anyway), a
  strategic grind where the seesaw economy punished my over-harvesting
  (Line 2), and a stress line where every exotic rule (re-arm, suicide,
  super-ko, double-pass) fired exactly as documented (Line 3). Emergent
  tactics (coup, suicide-strike, responder's harvest, cold-war zugzwang) are
  nameable and reusable, which is rare. What keeps it below the ceiling: the
  17-entry table is arbitrary-feeling and humanly unmemorizable, 8-neighbor
  counting in 4D is effectively machine-only, and games end in cascade
  avalanches (15–18 plies of a 98 cap) that would read as chaos to anyone
  not running exact lookahead. Slightly above R19's 4.375 on depth and
  emergence, anchored down for playability — 4.4.
