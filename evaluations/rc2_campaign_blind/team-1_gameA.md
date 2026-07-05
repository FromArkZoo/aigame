# Team 1 — Game A verdict

> Copy this template to `team-1_gameA.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game A` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  9×9 Sierpinski-carpet board: 64 active cells, 17 holes (a 3×3 central
  block plus eight singletons) that block both adjacency and capture
  lines. Placement must touch one of YOUR stones (waived at zero stones,
  re-arming), so each side grows one crawling connected blob — no jumps.
  Custodian (Othello-style) flips run along the two axes from the placed
  cell; holes terminate lines (engine-verified: a run ending at a hole
  does not flip). Hex-style asymmetric connection: P1 joins x=0 to x=8,
  P2 joins y=0 to y=8. 100-step cap with most-stones tiebreak, double
  pass draws, super-ko (provably dead — flips never remove stones, so
  occupancy grows monotonically and positions cannot repeat).
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection wins in both main lines (P1 at step 21; P2 at step 18) —
  the fastest decisive games in my whole evaluation. Double-pass draw in
  the stress line (step 7). Turn-limit tiebreak never approached; between
  players who both keep racing, games end decisively around ply 17–22.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The custodian capture layer turns out to be nearly
  suppressed by the own-adjacency placement rule: completing a sandwich
  requires placing the near bread-slice adjacent to your own blob, so
  flips only arise along deep contact seams (an enemy tendril poking
  between two arms of your territory). Across 46 plies of my three lines,
  not one flip actually fired — though flip THREATS shaped play (my
  Line-1 crossing plan, and his refuted counter-flip at (6,7), which
  own-adjacency made illegal for him). Hole-termination of capture lines
  was confirmed by direct probe.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `36,4,45,5,46,14,47,15,56,24,57,33,58,42,59,51,60,52,61,53,62`
- Plan and what happened: Opening theory I derived: naive lane sprints
  lose to the opponent's "counter-corner" (their free first placement
  caps your lane's far end, and the fractal's hole-pockets — e.g., (7,0)
  is a dead end because (7,1) is a hole — make detours cost 3–4 tempi).
  The correct P1 opening is a face-column cell: my (0,4) claims the x=0
  face AND cuts his col-0 expressway in a spot where the (1,4) hole
  leaves no bypass. Scripted P2 mirrored with (4,0) (his y-face + cutting
  my row 0 over the (4,1) hole). Both blobs then crawled toward the
  decisive crossing at (6,6) — his col-6 vs my row-6 — which I won by
  exactly the first-player tempo (my ply 17 vs his would-be 18). His
  blockade tries at (7,5)/(8,5) were one step behind; his flip-repair at
  (6,7) was illegal (no friendly stone adjacent). 62=(8,6) completed
  x=0→x=8.
- Result (winner, end cause, plies): P1 wins by connection at step 21 of
  100; 11 stones v 10.

### Line 2 — you as P2
- Moves: `0,8,1,17,2,26,3,35,4,44,5,53,6,62,15,71,24,80`
- Plan and what happened: I demonstrated the counter-corner weapon from
  the P2 seat. Scripted P1 committed to the classic row-0 corner sprint
  from (0,0); my reply (8,0) took his row's far end (an unflippable
  corner) AND the top of column 8 — which is P2 gold because column 8 IS
  the entire x=8 face: sprinting it both completes my y-path and starves
  his connection. His forced detour into the (6,1)/(6,2) channel was 4
  tempi slower and my column was flip-immune throughout (edge column:
  x-line walks fall off the board; holes shield row 1). 80=(8,8)
  finished y=0→y=8 one ply before his earliest possible completion.
- Result: P2 (me) wins by connection at step 18 of 100; 9 stones v 9.

### Line 3 — adversarial / novelty-stress
- Moves: `36,28,45,29,27,81,81`
- What you tried to break / stress, and what happened: (1) Hole capture-
  blocking: with his stones at (1,3),(2,3) and the (3,3) hole beyond, my
  placement at (0,3) walked the line [his,his]→hole and correctly flipped
  NOTHING (delta showed only my placed stone) — holes are not anchors and
  terminate custodian walks. (2) Double-pass termination verified at step
  7. (3) Confirmed super-ko can never fire (no removals; occupancy
  monotone — no rollback was ever flagged in any line).
- Result: DRAW by double pass at step 7; both probes behaved exactly per
  the rules text.

### Additional lines (optional)
An aborted earlier Line-1 draft (19 plies, helper-verified) produced the
key negative discovery: my planned far-side flip of his crossing stone
was ILLEGAL because the flipping cell touched only enemy stones —
own-adjacency quietly deletes most of the custodian layer's offense.
That draft also mapped the "gate cells" (4,0),(0,4),(8,4),(4,8): each
cuts an entire edge corridor because the adjacent hole leaves no bypass,
and each doubles as a face cell for one player — they are the board's
opening-theory hotspots.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Crawl your blob along the shortest lane toward BOTH faces while timing
  arrival at the one contested crossing ahead of the opponent's crawl;
  spend your single "teleport" (the first placement) on a cell that is
  simultaneously face-claiming and corridor-cutting. Distance-to-crossing
  arithmetic decides everything, so counting tempo along both blobs'
  frontiers is the whole skill.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Sharply: the counter-corner
  refutes naive sprints (Line 2 — a one-stone response that wins the
  game), face-column openings refute the counter-corner (Line 1), and
  hole-pockets punish anyone who runs a lane into a capped end. Blocks
  are only reachable by crawling, so counterplay must be PLANNED tempi in
  advance — reactive defense arrives one ply late, which is exactly how
  both my wins happened.
- Topology/board effects on strategy: The fractal is the game: edge
  columns/rows double as entire faces (owning column 8 starves the
  horizontal player), the 3×3 central hole block funnels all crossings
  into four 2-wide channels, singleton holes create dead-end pockets and
  flip-proof cells, and hole-terminated capture lines make edge lanes
  immune expressways.
- Emergent concepts you'd name (or "none observed"): "counter-corner"
  (the far-end cap with the free first move), "gate cells" (hole-backed
  corridor cutters), "face-column overlap" (edge lanes that double as
  goal faces), "crawl-tempo arithmetic", "flip suppression" (own-
  adjacency deleting the capture layer's offense).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Fully choice-driven and highly
  legible — the most human-playable game in my set. Both decisive lines
  came down to opening-theory decisions made at ply 1–2 plus correct
  tempo counting; nothing hidden, no cascade surprises, mistakes clearly
  attributable.
- 
## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is a Hex-family connection race (asymmetric opposite-face goals)
  with a blob-growth placement restriction found in various games, plus
  an Othello capture rule so suppressed it barely fires — on a board
  whose "fractal" is really just a hole pattern, and holed connection
  boards are known territory. One could call it "Hex with connected
  placement on a punched board".
- Honest novelty assessment after arguing that case: The synthesis has
  real identity: the own-adjacency rule turns Hex's anywhere-placement
  strategy into dual-blob crawl-tempo racing (a genuinely different
  skill), and the Sierpinski punching creates the gate-cell/face-overlap
  opening theory that dominated my lines. The near-vestigial capture
  layer is a design blemish but the threat-shadow it casts still
  influenced two refutations. Moderate novelty — a fresh-feeling family
  member rather than a new family.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — Hex-family resemblance is generic; I do
  not recognize this specific design or recall a score.
- P1-role experience sub-score (1-10): 4.1
- P2-role experience sub-score (1-10): 4.2
- Role-averaged sub-score: 4.15
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — the counter-
  corner makes P2 crushing against naive P1 openings (my Line 2 win), but
  P1's face-column opening restores a clean one-tempo win (Line 1's
  crossing race), so with best play the seats look balanced-to-slightly-P1
  and my record split one win each.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.1**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game A delivers the crispest decisive games of my set (18–21 plies,
  both ending in genuine one-tempo photo finishes at engine-verified
  crossings) and real discovered opening theory: counter-corners, gate
  cells, and the face-column defense — all consequences of the fractal
  holes interacting with blob growth. It is highly legible and mistake-
  attributable, with none of the draw pathologies that plagued the other
  connection games (blocks must be crawled to, so stalling is hard). It
  loses ground for its half-dead capture mechanic — a headline rule that
  fired zero times in 46 competitive plies — and for depth that feels
  narrower than C's once the opening theory is known: after the first
  two placements, much of the game is forced tempo-counting. Solidly at
  the R8 anchor: 4.1.
