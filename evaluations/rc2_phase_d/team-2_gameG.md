# Team 2 — Game G verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words:
  A 2D **hex** board, 8×8 (64 cells, degree 2–6). Players alternate one action:
  **PLACE** on an empty cell that is **adjacent to at least one ENEMY stone**
  (first-move-anywhere while you have none), **MOVE** one of your stones to an
  adjacent empty cell, or PASS. **No capture, no influence** (both declared
  none — no vestigial clutter). **Win = territory / stone count**: the instant
  you own **≥28 stones** (> 0.4276×64). Turn-limit (100) tiebreak = more stones
  (equal → draw); double-pass → draw. The defining twist is the **parasitic
  placement constraint**: you can only grow next to the opponent, so the two
  colours fill the board as one intertwined blob, and managing your own
  enemy-adjacent frontier (so you never run out of legal placements) is the
  whole game.
- What actually ends the game / frequency: of the full games I drove, two ended
  by **threshold win** (P1 28–27; P2 28–23) and one **stalled** near 26–26 with
  neither side able to keep placing — heading to a turn-limit tiebreak (a likely
  draw). So: win-condition under competent filling, turn-limit/draw under mutual
  frontier exhaustion.
- Surprises: (1) a player can get **stuck** (no empty cell adjacent to an enemy
  stone) and be forced to MOVE/PASS, conceding the race — this, not tempo,
  decided my P2 win. (2) MOVE never increases your count, so it's a fallback,
  not an engine of progress.

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,28,20,11,3,2,1,0,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,21,22,23,24,25,26,29,30,31,33,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,49,48,50,51,52,53,54`
- Plan and what happened: I (P1) and a competent P2 both greedily took a live
  enemy-adjacent frontier cell each turn, filling the board as one blob. Because
  I place on odd plies, I reached 28 one tempo before P2.
- Result: **P1 win, threshold, 55 plies** (28 vs 27) — verified directly via
  play.py.

### Line 2 — you as P2
- Moves: `27,28,37,19,36,20,29,21,26,18,25,17,24,16,22,13,14,6,12,4,11,3,10,2,9,1,8,0,7,5,108,7,153,14,199,22,204,23,210,24,33,34,42,35,43,38,46,39,47,40,49,41,50,44,53,45`
- Plan and what happened: I (P2) kept my frontier alive while P1 placed
  carelessly and stranded itself — P1 ran out of enemy-adjacent empties and was
  forced into MOVE actions (ids 108/153/199/204/210) that gained nothing, while
  I kept claiming cells to 28. I won **from the second seat**, beating the tempo
  deficit purely by better frontier management.
- Result: **P2 win, threshold, 56 plies** (28 vs 23) — verified directly via
  play.py.

### Line 3 — adversarial / novelty-stress
- Moves: greedy P1 vs a frontier-starving P2 policy (drive script,
  engine-verified each step).
- What I tried to break / stress: I had both sides place so as to consume the
  shared frontier badly. The game **stalled at ~26–26** with neither able to
  reach 28 — every remaining empty cell stopped being adjacent to an enemy
  stone for the side to move. This demonstrates the threshold is NOT guaranteed
  reachable; mutual mis-management yields a turn-limit tiebreak/draw.
- Result: **no decisive winner — stall ~26–26** heading to turn-limit.

### Additional lines (optional)
Sanity: P1 greedy vs P2 MOVE-only → P1 28–3 (declining to place just loses);
P1 MOVE-only vs P2 greedy → P2 28–2. Confirms placing is the only path.

## Phase 3 — Joint strategic analysis

- Core tactical loop: each turn, take an enemy-adjacent empty cell that (a)
  advances your count and (b) preserves the most future enemy-adjacent empties
  for you while shrinking them for the opponent. Avoid placements that wall off
  your own frontier.
- Counterplay: yes — getting the opponent **stuck** (no legal PLACE) wins the
  race regardless of seat; my Line 2 P2 win came entirely from out-managing the
  frontier, not from tempo. So skill can override the first-move edge.
- Topology effects: hex 6-connectivity keeps the blob's frontier large and hard
  to fully starve, which is why competent filling usually reaches 28 rather than
  stalling; edges/corners (lower degree) are where frontiers die.
- Emergent concepts: frontier management, mutual parasitic growth, self-
  stranding, stuck-out.
- Player agency: real — placement choice decided two of my games (Lines 2–3),
  and only under symmetric greedy play does raw tempo (Line 1) decide.

## Phase 4 — Novelty adversary

- Strongest re-skin case: it's a **majority/territory fill race** — claim more
  than ~43% of cells — a very old idea; MOVE adds little.
- Honest novelty assessment: moderate. The distinctive element is the
  **must-place-adjacent-to-enemy** constraint, which turns a dull fill race into
  a frontier-management problem and makes self-stranding a real loss condition.
  That's a genuine, if modest, twist, and unlike several sibling games it has
  **no vestigial subsystems** — the rules are exactly what matters. Docked
  because the strategic ceiling is low (the dominant idea is "don't run out of
  frontier") and equal play hands the first mover a one-stone win.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.9
- P2-role experience sub-score (1-10): 3.8 (must out-place to overcome tempo)
- Role-averaged sub-score: 3.85
- **Fairness perception (1-5):** 3 — Razor-thin P1 tempo edge under symmetric
  play (Line 1, 28–27) with no pie rule, but a better-placing P2 wins from the
  second seat (Line 2, 28–23), so skill dominates structure → effectively
  balanced.
- **Overall (1-10, anchored): 3.9**
- One-paragraph justification: G is a clean, comprehensible game with no
  vestigial machinery, and it carries genuine (if shallow) strategy: Lines 2 and
  3 prove that frontier management — not seat order — usually decides, since a
  careless player strands itself out of legal placements (my P2 won from behind,
  28–23) and mutual mismanagement stalls the race entirely. Against that, the
  strategic ceiling is modest (the whole game is "keep an enemy-adjacent empty
  available"), and under equal competent filling the first mover takes it by a
  single stone with no balancing rule. Decisive, fair-ish, and honest about its
  rules, but not deep — I anchor it just below F at 3.9.
