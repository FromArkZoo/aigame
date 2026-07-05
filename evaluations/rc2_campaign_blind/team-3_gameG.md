# Team 3 — Game G verdict

> Copy this template to `team-3_gameG.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game G` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 board with MOORE adjacency (all Chebyshev-1 neighbors — 7 to 26 per cell).
  Placement may target ANY cell: empty, enemy (replacement), or your own (legal no-op);
  it must be adjacent to one of your stones (anywhere at zero stones; re-arms). After
  EVERY action — including passes and no-ops — a totalistic CA runs THREE iterations
  from the actor's perspective, with 13 non-identity entries (births at 3F+3E empties;
  various flips/deaths at exact small counts; counts above 4 per side never match).
  Classic capture/propagation disabled. Win by connection: P1 spans d2=0→3, P2 spans
  d0=0→3 (Moore adjacency makes 4-stone diagonal chains legal paths). 141-step limit →
  most stones; double pass → draw; super-ko rolls repeats back to a pass, checked on
  the post-CA position.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection win both full lines: P1 (me) at ply 9 in Line 1; P1 (scripted) at ply 13
  in Line 2 — the second via a CA cascade rather than a hand-built chain. Stress probes
  ended without termination (no turn-limit or draw reached in my play).
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules:
  Constantly — this game out-computed my hand analysis more than any other. (1) The
  3-iteration CA chains: converting an enemy stone in iteration 1 raised my own stone
  to exactly 3 friendly neighbors and it died of "overcrowding" in iteration 2 (Line 1,
  ply 5). (2) A PASS can create material: my ply-12 pass in a dense position birthed a
  stone for ME via the 3F+3E rule ("harvest pass"). (3) A no-op placement on my own
  stone also triggers the CA — a free detonator. (4) The natural spite reply (seed
  adjacent to P1's first stone, forcing mutual annihilation) is BANNED by super-ko:
  the post-CA board would be empty with P1 to move, recreating the initial position,
  so the engine converts it to a pass. (5) Placed stones can defect on arrival (a
  replacement landing at an exact bad count flips or dies in the same action's CA).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `4,48,21,37,38,63,55,42,20`
- Plan and what happened: I rushed a d2-spanning diagonal (0,1,0)-(1,1,1)-(2,1,2)-
  (3,1,3), which is CA-stable while linear (middles at 2 friendly neighbors match no
  table entry). Scripted P2 contested the shared space with a contact pair. My ply-5
  extension detonated the actor-side CA: P2's contact stone at (1,1,2) had exactly 2 of
  my stones + 1 support, so it CONVERTED to me (2F+1E rule); their now-unsupported seed
  at (0,0,3) died (1F+0E); and my own (1,1,1) — raised to exactly 3 friendly neighbors
  by the conversion — emptied in iteration 2. Net: 3 stones to 0 in one action. P2
  re-seeded far away; my converted stone had rebuilt the span shape, and one linking
  placement at (0,1,1) completed d2=0..3.
- Result (winner, end cause, plies): P1 (me) won by connection at ply 9, 5 stones to 2.
  The actor-perspective CA is a first-mover's weapon: the player who touches a contact
  cluster first converts it.

### Line 2 — you as P2
- Moves: `4,4,58,25,42,46,26,58,62,62,31,31,31` (P1 won at ply 13; rest of script ignored)
- Plan and what happened: I opened with the tempo-steal I found in analysis: REPLACE
  P1's first stone (placement target 'any' + first-move-anywhere), after which P1's
  re-replacement is super-ko-illegal — P1 must concede the initiative or reset. The
  early middlegame went well: when P1's contact play flipped my stones, I replaced his
  d2=3 anchor (my stone at (2,2,3) stuck at a safe 1F+1E count), and my surviving
  "venom" stone at (2,2,2) locked his expansion — every d2=0 or d2=3 extension he
  owned sat at exactly 3F+1E on his own action and would have defected to me. He was
  reduced to replacement wars over single cells. But the war fed board density, and at
  ply 11 his placement triggered a NINE-cell cascade (births at 3F+3E, flips both
  ways), and at ply 13 a second cascade birthed d2=0 stones that completed his span.
- Result: P1 won by connection at ply 13, 12 stones to 5 — the winning path was mostly
  CA-born, not hand-placed. My opening steal and venom lock were real, but P1's extra
  tempo meant he was the actor at the two moments the automaton went critical.

### Line 3 — adversarial / novelty-stress
- Moves: `4,5` and `4,4,58,25,42,46,26,58,62,62,31,64`
- What you tried to break / stress, and what happened: (a) Mutual-annihilation reply:
  P2 seeding adjacent to P1's lone stone should kill both (actor 0F+1E empties; enemy
  1F+0E empties), leaving the initial empty board — the engine correctly detected the
  post-CA repetition and rolled the action back to a PASS (super-ko preventing a
  board-reset exploit). (b) Pass-CA: with a dense board, my PASS birthed a P2 stone at
  (2,1,1) — passes are not neutral; the passer "acts" for CA purposes and can harvest
  births. Also observed within Line 2: a no-op self-placement that changed the board
  only through its CA step.
- Result: Both edge behaviors confirmed; no crash or rules/engine mismatch beyond the
  documented weirdness.

### Additional lines (optional)
Several `--legal` probes to decode replacement legality (any cell in a friendly stone's
Moore neighborhood, including occupied ones) and to ground-truth positions after
cascades my hand analysis got wrong — twice my predicted CA outcome differed from the
engine's, which is itself evaluation-relevant: the 3-iteration Moore CA exceeds
practical human simulation at density.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  In the sparse phase, real principles exist: keep your chain LINEAR (exactly 1–2
  friendly neighbors per stone — 3 friendly is death-by-overcrowding on your own
  action); convert enemy contact stones by engineering 2-friendly+1-enemy counts around
  them before they do it to you; plant "venom" stones that pre-load the enemy's cells
  to exactly 2 friendly + 1 enemy so their own reinforcement flips them (my lock in
  Line 2); use replacements to erase anchors, knowing repeat-replacements die to
  super-ko. In the dense phase the loop degenerates into "be the actor when the
  automaton goes critical".
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all?
  Heavily, in the sparse phase: P2's contact pair in Line 1 was punished by conversion;
  P1's anchor in Line 2 was punished by replacement; my venom stone punished every
  chain extension he owned. But the ultimate punishments were dealt by the automaton,
  and the triple-iteration cascades eventually reward tempo more than reading.
- Topology/board effects on strategy: Moore adjacency makes connection trivially easy
  (any 4-diagonal spans the board) and blocking geometrically hopeless, so ALL defense
  is CA-tactical (conversion, venom, replacement) — a genuinely unusual strategic
  regime. 26-neighborhoods also mean everything interacts with everything: there is no
  "far away" on a 4×4×4 Moore board, which is why density explodes.
- Emergent concepts you'd name (or "none observed"): "linear-or-die" (3-friendly
  overcrowd suicide), "conversion race" (actor flips contact stones), "venom stone"
  (pre-loading 3F+1E defection), "harvest pass", "replace-war parity" (super-ko decides
  who wins a cell exchange), "cascade criticality" (the density point where the
  3-iteration CA takes over the game).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Split verdict: my Line 1 win was chosen (the
  conversion at ply 5 was planned and worked); Line 2's finish was substantially the
  automaton's — I could trace WHY each cascade fired after the fact, but could not
  practically foresee 9-cell chains three iterations deep. Sparse-phase agency high,
  dense-phase agency low, and the first mover gets to schedule when density arrives.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  Its skeleton is the same as the pack's other CA game: Hex-style crosswise connection
  goals + actor-perspective totalistic CA + territory/turn-limit scaffolding, so one
  can argue it is "the same generator with a different random table" — Life-family CA
  plus connection goals, both known ideas.
- Honest novelty assessment after arguing that case: The parameter changes are not
  cosmetic: Moore-3D adjacency (26 neighbors), THREE CA iterations per action, and
  replacement/no-op placements produce qualitatively new phenomena I've never seen in
  any published game — overcrowd suicide shaping stones into worms, venom-stone
  defection traps, harvest passes, super-ko-banned annihilations. As a rules object it
  is the most novel game in this pack; as a playable contest it teeters on the edge of
  chaos.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — the family resemblance to the pack's other CA game is
  observable from the rules text alone; I do not recognize this specific game or any
  prior score.
- P1-role experience sub-score (1-10): 4.4
- P2-role experience sub-score (1-10): 3.8
- Role-averaged sub-score: 4.1
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 2 — P1 won both full lines
  (plies 9 and 13), the actor-biased CA rewards whoever touches a contact cluster
  first, and P1's one-ply tempo lead meant he was the actor at both cascade-critical
  moments despite my successful opening tempo-steal as P2.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.2**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  The sparse phase delivered some of the most original tactics of the whole pack —
  Line 1's planned conversion-cascade (flip their stone, watch my own die of
  overcrowding, still win at ply 9) and Line 2's venom lock (every extension he owned
  poised to defect) were thrilling to construct and engine-verified. The stress probes
  revealed coherent, even elegant edge-rule interactions (super-ko banning the
  annihilation reset; harvest passes). It loses ground for the dense phase, where
  triple-iteration Moore cascades (a 9-cell explosion at ply 11 of Line 2) exceed
  human lookahead and effectively hand the game to the tempo holder — both my lines
  went to P1, and games are over by ply ~13, more detonation than contest at the end.
  Slightly above R8's 4.10 on novelty and sparse-phase depth, short of R19: 4.2.
