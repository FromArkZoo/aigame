# Team 1 — Game G verdict

> Copy this template to `team-1_gameG.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game G` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  4×4×4 board with Moore adjacency (all Chebyshev-1 neighbors, 7–26 per
  cell). Players alternate placements that may target ANY cell — empty,
  enemy (replaces it), or own (legal no-op) — constrained to be adjacent to
  an own stone (waived at zero stones, re-arming after annihilation). After
  every action the CA runs THREE synchronous iterations from the actor's
  perspective, with a table covering counts 0–4 per side only (higher counts
  freeze a cell). Key entries: your own stone dies at 3 friendly + 0 enemy
  (on your own action!), an isolated stone dies to one enemy contact, a
  stone with support 2 is immune to everything, dense enemy trios die, and
  several patterns flip ownership. Wins are Hex-style asymmetric
  connections: P1 joins the d2=0 and d2=3 faces, P2 joins d0=0 and d0=3.
  141-step limit (most stones wins), double pass draws, super-ko rolls
  repeating actions back into passes.
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  Connection wins twice (my Line 1 at step 7; my Line 2 at step 16).
  Double-pass draws three times — one of them (first Line 1 attempt) by an
  extraordinary route: two consecutive SUPER-KO rollbacks (both players'
  replacement attempts recreated prior positions) were converted to passes
  and ended the game. Turn-limit never reached, but it matters strategically:
  a player who stalls with harassment forever loses the most-stones tiebreak,
  which is what forces the harasser to eventually race.
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: The 3-iteration cascades repeatedly out-calculated me even
  with a verified simulator: (1) a flip can hand one of your stones a third
  friendly neighbor, triggering the 3F+0E self-destruct one iteration later
  (killed my hub twice); (2) my engineered 3F+3E birth fired and then
  ANNIHILATED its own parents — the newborn was each parent's third friendly
  neighbor, all three died in iteration 2, and the orphaned newborn died at
  0F+3E in iteration 3; (3) mutual annihilation of two lone adjacent stones
  recreates the empty board, so the "snipe" of a lone opener is super-ko
  rolled back into a pass; (4) completing a 2×2 square kills all four of
  your own stones on your own tick.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `21,60,41,12,5,13,57`
- Plan and what happened: Center opener (1,1,1), then the "supported snipe"
  doctrine: my ply-3 placement at 41=(1,2,2) was simultaneously adjacent to
  my 21 (support, so it survives at 1F+1E) and his lone 60 (which died at
  1 friendly + 0 enemy from his perspective) — and 41 sits on my d2 path.
  Scripted P2 rebuilt far away on his d0=0 face (12, 13) where his stones
  couldn't legally reach my cluster to replace anything; I completed the
  sparse diagonal chain 5(d2=0)–21–41–57(d2=3), keeping every stone at
  support ≤2 to dodge the self-destruct rules.
- Result (winner, end cause, plies): P1 wins by connection at step 7 of 141;
  4 stones v 2.

### Line 2 — you as P2
- Moves: `21,21,42,60,22,41,56,36,61,57,26,25,55,26,39,31` (I drove O: the
  ply-2 replacement-EAT of his center opener, 60, 41-snipe, 36, 57, 25, 26
  rebuild, and the 31 finish; P1 was scripted with his strongest tools:
  mutual-annihilation reset, fresh-center restarts, a spy, an eat)
- Plan and what happened: I answered 21 by placing ON it (replacement),
  deleting his opener. His best response — a lone adjacent placement forcing
  mutual annihilation back to an empty board with me to move — flipped the
  initiative to me. From there: corner foundation 60, a supported snipe at
  41 killing his center restart, a third-adjacent kill of his spy, and a
  sparse chain 36(d0=0)–25–26–31(d0=3). Two heavy lessons en route: my first
  kill-cells formed a support-2 triangle, which is a FROZEN structure (any
  growth pushes a member to 3F+0E death) and cost me a hub; and my first
  intended winner (27) actually flipped his 39 to me, overloading my 26 into
  self-destruction and breaking the path — I had to finish with 31, which
  completes the connection without triggering any flip.
- Result: P2 wins by connection at step 16 of 141; 5 stones v 2.

### Line 3 — adversarial / novelty-stress
- Moves: `0,42,1,38,4,41,0,64,64` (and a companion stress game
  `63,0,62,1,58,4,54,5,64,64`)
- What you tried to break / stress, and what happened: (1) Engineered the
  rare empty-cell 3F+3E birth with two opposing triangles around (1,1,1):
  the birth fired on the completing player's tick and then the whole
  structure self-annihilated over iterations 2–3 (parents died of 3F+0E,
  orphan died of 0F+3E) — P2 went from 3 stones to 0 by making a "natural"
  developing move. (2) Verified placing on your OWN stone is a legal no-op
  that still ticks the CA (a stall that avoids the pass counter). (3) In the
  companion game, P2 completed a 2×2 square and all four stones died on his
  own action; my own chain also lost a stone when a placement gave it a
  third friendly neighbor. (4) Both games closed with clean double-pass
  draws; earlier I also verified the double-super-ko ending (two rolled-back
  replacements in a row = two passes = draw).
- Result: DRAW by double pass in both stress games (steps 9 and 10); every
  engineered pathology behaved exactly per the printed table.

### Additional lines (optional)
First Line-1 attempt (`21,60,42,61,5,42,42,42,63`): P2 replaced my path stone
at 42; my naive retake recreated the ply-5 position (SUPER-KO → forced pass)
and his re-eat recreated the ply-6 position (second rollback → second pass)
— game ended DRAW by double pass at step 8 without either of us intending to
pass. A complete, engine-verified demonstration of the "founder's curse":
in any 1-cell ownership war, the player who first created a position state
runs out of legal recreations first.

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  Grow a SPARSE chain toward your two faces — every stone at support 1–2,
  never letting any stone reach exactly 3 friendly with 0 enemy — while
  looking for supported snipes (a placement adjacent to your cluster and to
  a lone enemy stone kills it for free) and replacement-eats of enemy path
  cells. Before every move you must simulate three CA iterations including
  flips, or your own structure detonates.
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? Constantly: lone stones are
  sniped; over-supported clusters die spontaneously (2×2 = instant death);
  replacement-eats punish thin paths, and the super-ko ledger punishes
  whoever founded a contested cell first (their recreations run out first).
  The deepest counterplay I found: answering P1's center opener by eating
  it, and answering the eat with mutual-annihilation to flip initiative.
  Both roles' key resources are reactions.
- Topology/board effects on strategy: Moore adjacency makes the board tiny
  (diameter 3) and dense: nothing is ever out of reach, any two stones near
  the center share many common neighbors (snipe cells always exist), and
  local growth around a hub is nearly impossible because new stones touch
  too many old ones (the 3F+0E tomb). Diagonal chains of 4 connect faces at
  minimum cost, so the game is a knife-edge race (7–16 plies) unless it
  collapses into ko-dance stalls.
- Emergent concepts you'd name (or "none observed"): "supported snipe",
  "replacement-eat", "mutual-annihilation reset" (initiative transfer),
  "founder's curse" (super-ko state parity), "frozen triangle" (support-2
  triangles cannot be grown), "2×2 suicide", "spy" (a lone stone adjacent
  to exactly two enemies survives at 0F+2E), "no-op stall" (placing on your
  own stone ticks the CA without passing).
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? Choices decide everything — this is
  a deterministic calculation game with zero randomness — but the effective
  agency belongs to whoever can simulate three Moore-CA iterations
  faultlessly. I had an exact rules-derived simulator and still lost pieces
  to fourth-order effects three separate times. A human playing unaided
  would experience the game as a series of inexplicable detonations.

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  It is Hex (asymmetric face-connection goals) played on a 3D Moore graph,
  crossed with a two-player Life variant (p2life family), with Go's
  positional super-ko and an overwrite-placement mechanic found in various
  abstract games. Each component exists in prior art, and "connection game
  + cellular automaton" is an obvious hybridization.
- Honest novelty assessment after arguing that case: The components are
  known but the emergent layer is not: the super-ko ledger interacting with
  deterministic mutual-annihilation creates a genuinely new kind of
  ko-parity combinatorics (founder's curse, initiative-transfer resets,
  double-rollback draws) that I have not seen in any published game, and the
  actor-perspective triple-iteration CA turns placement safety into a novel
  constraint system (frozen triangles, 2×2 suicide). High mechanical
  novelty; substantially more than a re-skin.

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): none — no recognition of this specific game; the
  Hex/p2life resemblances cited in Phase 4 are generic families.
- P1-role experience sub-score (1-10): 4.0
- P2-role experience sub-score (1-10): 4.2
- Role-averaged sub-score: 4.1
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** 3 — P1 won my
  Line 1 in 7 plies off the tempo race, but P2's move-2 replacement-eat of
  the opener (Line 2, P2 win in 16) is a full equalizer that converts P1's
  first-move edge into a symmetric ko-dance, and my decisive lines split
  one win each.
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 4.1**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  Game G packs more genuinely novel emergent structure than anything I know
  in its families — the founder's-curse super-ko parity war (Line 2's
  opening; the additional line's double-rollback draw), supported snipes and
  frozen triangles (both decisive lines), and self-annihilating births
  (Line 3) — and both seats have real, distinct winning plans (P1's 7-ply
  race in Line 1, P2's eat-equalizer grind in Line 2). It scores below
  Game-quality anchors' ceiling for one dominant reason: the treachery is
  unplayable-grade. Even with an exact simulator I detonated my own
  structures three times; unaided humans would find "legal move that doesn't
  kill your own stones" a research problem, and symmetric competence tends
  to collapse into super-ko pass-out draws (3 of my 5 completed games).
  Deep, novel, hostile: 4.1, just above R8.
