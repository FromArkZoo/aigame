# Team 3 — Game D verdict

> Copy this template to `team-3_gameD.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game D` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  3×3×3×3 torus (81 cells). Adjacency is orthogonal per axis, and because each axis is
  a 3-cycle, two cells are adjacent exactly when they differ in ONE coordinate (by any
  amount) — every cell has degree 8, no edges or corners, and nothing is farther than
  4 steps. Placements go on empty cells adjacent to your own stones (first move
  anywhere; re-arms on extinction). After every action a 1-iteration actor-perspective
  CA runs with 17 non-identity entries — notably: mixed-3 empties (1F+2E, 2F+1E) birth
  a stone for the ACTOR; various exact counts kill stones; there are NO color flips in
  this game, only births and deaths. Win: own ≥17 stones (>20% of 81). 98-step limit →
  most stones; double pass → draw; super-ko → pass conversion.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Territory threshold fired decisively and quickly in both full lines (P1 at ply 21
  with 18 stones in Line 1; P2 — me — at ply 20 with 19 stones in Line 2). The stress
  line ended in a scripted double-pass draw at ply 21. No turn-limit games; this is the
  fastest, most decisive game in the pack.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules:
  (1) Harvest strikes are enormous: one placement into a poised boundary layer birthed
  FOUR extra stones (ply 19 of Line 1: +5 total in one action), and my Line 2 strike
  chain produced +5 then +6 swings. (2) The 3-cycle wrap means a cell's two axis
  neighbors are BOTH other values — "distance" barely exists, yet planes offset in two
  coordinates genuinely never touch, so separation strategy still works. (3) Passes
  turned out to be CA-neutral in practice (my poised-position pass produced no
  mutations — the harvest patterns need the placement itself). (4) Unlike the pack's
  other CA games, contact is stable at low density (a lone stone next to an enemy
  survives both players' actions) — no annihilation openings, no zombie analogues; the
  engine behavior matched the printed table everywhere I checked.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `0,40,1,41,2,39,3,43,4,44,5,42,6,37,7,38,8,36,9,64,13,66,14,67,16`
- Plan and what happened: I filled the (·,·,0,0) plane (9 cells, mutually safe — a
  wrapped 3×3 plane has no CA-matching counts), while scripted P2 mirrored in the
  (·,·,1,1) plane, offset in two coordinates so the clusters never touch. The
  intermediate layer (·,·,1,0) touches BOTH planes (one friendly + one enemy neighbor
  per cell), so it was a poised minefield: my 10th placement there (ply 19) tipped four
  neighboring cells to 2F+1E and birthed four stones in one action (9→14). P2's mirror
  strike also harvested (+3), but one tempo behind. I then banked quiet cells (the
  harvested layer had gone 3F+1E — one friendly too many to birth) and crossed the
  threshold.
- Result (winner, end cause, plies): P1 (me) won by territory threshold at ply 21,
  18–12 — my final placement birthed 3 more stones inside P2's own layer for an
  emphatic finish.

### Line 2 — you as P2
- Moves: `0,40,1,37,2,38,3,36,4,39,5,41,6,42,7,43,8,13,22,49`
- Plan and what happened: Scripted P1 played Line 1's winning recipe verbatim
  (complete the plane at ply 17, strike the boundary at ply 19). My counter: STRIKE
  FIRST. At ply 18, with my plane deliberately one cell short, I placed into the
  boundary layer (1,1,1,0) — +4 births (8→13, jumping ahead 13–9). P1's counter-strike
  at (1,1,2,0) harvested +6 (15–13 him), but that opened a SECOND poised zone for me:
  (·,·,2,1) touches my plane (d2) and his fresh layer (d3), and my ply-20 strike at
  (1,1,2,1) birthed five more stones (13→19).
- Result: P2 (me) won by territory threshold at ply 20, 19–15. The strike-ladder
  analysis says a perfect P1 should strike at ply 17 instead of completing the plane
  (and then wins the ladder by tempo), but against the plane-first strategy the
  first-strike counter is decisive — an earned, legible P2 win.

### Line 3 — adversarial / novelty-stress
- Moves: `0,40,1,37,2,38,3,36,4,39,5,41,6,42,7,43,8,13,22,81,81`
- What you tried to break / stress, and what happened: (a) Pass-harvest test: in the
  poised ply-20 position (where a placement would have birthed +5) I passed instead —
  the CA produced ZERO mutations, confirming passes don't harvest here (harvest
  patterns require the new stone's own contribution). (b) Double-pass: P1 then passed
  too (a scripted rules-demo blunder while sitting at 15/17), and the game ended as an
  immediate draw — the draw rule outranks a nearly-won position. (c) Earlier probes:
  contact seeds don't annihilate (1F+0E is not in this game's opponent-cell table),
  and I found no zombie/immortality analogues — deaths are count-based and reciprocal.
- Result: Draw by double pass at ply 21; no degenerate exploit found — notably the
  ONLY game in my seven where I failed to find one.

### Additional lines (optional)
An earlier 33-ply pure-separation script (both sides plane-filling plus layer
expansion) confirmed the no-interaction race math: P1's 17th placement lands one ply
before P2's; several `--legal` probes confirmed birthed stones grant placement
adjacency and occupy cells (my original ply-21 was illegal because a birth had already
filled it).

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Build CA-quiet structure (planes and lines whose cells match no table entry), then
  time the "harvest strike": place into a layer where every neighboring empty cell
  sits at exactly 1 friendly + 1 enemy, so your stone tips them all to 2F+1E and
  births a stone for you at each. Good moves are measured in births-per-action; quiet
  +1 placements are only for consolidating after a zone is spent (harvested layers
  jump to 3F+1E — one friendly too many). Deny the opponent's strikes by pre-filling
  or pre-spending shared boundary zones.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all?
  Yes, at the strategic level: P1's plane-completion tempo in Line 2 was punished by
  my first-strike; my strike was answered by his counter-strike into a fresh zone
  (+6); his counter-strike created the very boundary my winning strike needed. It's
  less a move-by-move dogfight than a zone-timing duel — but the zones are created by
  the opponent's shape, so you are always playing against their structure.
- Topology/board effects on strategy: The 3^4 torus is the star: single-coordinate
  adjacency makes each axis a 3-clique, "distance" almost disappears, yet
  two-coordinate offsets give genuine separation — a counterintuitive geometry you
  must internalize to play at all. No edges means no fortress terrain; safety comes
  from count-engineering, not position.
- Emergent concepts you'd name (or "none observed"): "quiet shapes" (structures whose
  every cell matches no CA entry), "poised layer" (boundary zone where every cell is
  1F+1E), "harvest strike" (+4..+6 in one action), "strike ladder" (alternating
  fresh-zone detonations), "spent zone" (3F+1E after harvest), "first-strike tempo"
  (the plane's 9th cell is worth less than striking first).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? High agency of an unusual kind: the CA is
  deterministic and single-iteration, so strikes are exactly calculable (all my
  predicted birth counts matched the engine within one cell), and both wins trace to
  chosen strike timing. The race structure sets the tempo clock underneath, favoring
  P1 at perfection, but the winner in both my lines was decided by who read the zones
  better.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It shares the pack's CA-game chassis (actor-perspective totalistic table + territory
  threshold + own-adjacency placement), so one can argue it's the same generator as
  the other CA entries with a different random table and board — and "Life-like CA
  plus scoring" is a known genre.
- Honest novelty assessment after arguing that case: The realized game is distinct
  from both siblings and from anything published I know: a 4D 3-torus where adjacency
  is coordinate-difference, no flips (births/deaths only), a low territory bar that
  ends games in ~20 plies, and a strategy layer (quiet shapes, poised layers, strike
  ladders) that I derived from scratch and that actually worked as calculated. Where
  the sibling CA games tip into chaos, this one stays computable — the novelty here
  produces STRATEGY rather than noise. Most playable novel design in the pack.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — chassis resemblance to the pack's other CA games is
  from rules text alone; no recognition of this specific game or a prior score.
- P1-role experience sub-score (1-10): 4.5
- P2-role experience sub-score (1-10): 4.4
- Role-averaged sub-score: 4.45
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — my lines split 1–1 with
  the winner decided by strike timing rather than seat, though the underlying race
  math (17th placement lands one ply earlier for P1, and the strike ladder inherits
  that tempo) suggests a mild P1 edge at perfect play.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.6**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  This was the pack's best marriage of novelty and playability: the 4D 3-torus forced
  me to relearn what "near" means, the no-flip CA made positions calculable enough
  that my planned harvest strikes landed exactly as computed (Line 1's +5 detonation;
  Line 2's first-strike into second-strike for a 19-stone finish at ply 20), and both
  competitive games ended decisively inside 21 plies with the result traceable to a
  single identifiable timing decision. It is also the only game of my seven with no
  degeneracy found — the stress line's pass tests came back clean. Held below the 5.0
  ceiling because the strategy space, once the strike-ladder pattern is seen, may be
  narrow (zone timing is most of the game), and the perfect-play tempo edge likely
  belongs to P1. Best-in-pack for me alongside F, and cleaner than F: 4.6.
