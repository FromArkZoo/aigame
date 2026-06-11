# Team 2 — Game C verdict

## Phase 1 — Rule comprehension

- Mechanics in your own words:
  A 2D **hex** board, 8×8 (64 cells, degree 2–6). Players alternate **PLACE**
  on an empty cell **adjacent to at least one ENEMY stone** (first-move-anywhere
  while you have none) or **PASS**. **No capture, no influence, and — unlike
  some siblings — no MOVE action and no super-ko** (action space is just
  PLACE 0..63 + PASS). **Win = territory**: own **≥28 stones** (> 0.4276×64).
  Turn-limit (100) tiebreak = more stones (equal → draw); double-pass → draw.
  The whole game is the **parasitic-growth fill race**: both colours grow as one
  intertwined blob (each placement must touch the enemy), and the skill is
  managing your enemy-adjacent frontier so you reach 28 before running out of
  legal placements.
- What actually ends the game / frequency: of my full games, two ended by
  **threshold win** (P1 28–27; P2 28–27), one **stalled at 27–27** heading to a
  turn-limit/draw. With no MOVE, a stuck player can only PASS, so frontier
  exhaustion bites slightly harder than in the MOVE-bearing sibling.
- Surprises: none beyond the rules — without MOVE, getting **stuck** (no enemy-
  adjacent empty) simply forces a pass and usually concedes the race (my P2 win
  exploited exactly this: P1 had to pass, P2 kept claiming cells to 28).

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `27,28,20,11,3,2,1,0,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,21,22,23,24,25,26,29,30,31,33,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,49,48,50,51,52,53,54`
- Plan and what happened: I (P1) and a competent P2 each greedily took a live
  enemy-adjacent frontier cell, filling the board as one blob. Placing on odd
  plies, I reached 28 one tempo ahead.
- Result: **P1 win, threshold, 55 plies** (28 vs 27) — verified via play.py.

### Line 2 — you as P2
- Moves: `27,28,37,19,36,20,29,21,26,18,25,17,24,16,22,13,14,6,12,4,11,3,10,2,9,1,8,0,7,5,64,15,23,30,39,31,38,32,40,33,41,34,42,35,43,44,53,45,54,46,55,47,52,48,56,49`
- Plan and what happened: I (P2) kept my frontier alive while P1 placed itself
  into a corner and **ran out of legal placements** — P1 was forced to PASS
  (action 64 in the line) and stalled at 27, while I claimed the last cells to
  28. I won **from the second seat** purely on frontier management.
- Result: **P2 win, threshold, 56 plies** (28 vs 27) — verified via play.py.

### Line 3 — adversarial / novelty-stress
- Moves: greedy P1 vs frontier-starving P2 (engine-verified driver).
- What I tried to break / stress: I had both sides consume the shared frontier
  badly. The game **stalled at 27–27** with neither able to reach 28 — every
  remaining empty stopped being enemy-adjacent for the side to move. With no
  MOVE to reposition, this heads straight to a turn-limit tiebreak/draw.
- Result: **no decisive winner — stall 27–27.**

### Additional lines (optional)
Sanity: declining to place (pass when a place exists) just hands the opponent
the race, as in the sibling fill-race.

## Phase 3 — Joint strategic analysis

- Core tactical loop: each turn take an enemy-adjacent empty that advances your
  count while preserving your future frontier and shrinking the opponent's;
  never wall yourself off.
- Counterplay: real — strand the opponent (no legal PLACE) and the race is
  yours regardless of seat (Line 2's P2 win). With no MOVE, stranding is even
  more decisive than in the sibling game.
- Topology/board effects: hex 6-connectivity keeps the frontier broad and hard
  to fully starve, so competent filling usually reaches 28; the low-degree
  edges/corners are where a frontier dies.
- Emergent concepts: frontier management, mutual parasitic growth, self-
  stranding.
- Player agency: real — placement choice decided Lines 2–3; only symmetric
  greedy play (Line 1) lets raw tempo decide.

## Phase 4 — Novelty adversary

- Strongest re-skin case: a **majority/territory fill race** (own >43% of cells)
  — an old idea — distinguished only by the must-place-next-to-enemy rule. It is
  mechanically a stripped-down hex fill game.
- Honest novelty assessment: moderate, and identical in spirit to its MOVE-
  bearing sibling. The parasitic-adjacency constraint is the one real twist
  (it makes self-stranding a loss condition); dropping MOVE/super-ko makes C the
  leaner, cleaner expression of the same idea with no practical loss. Docked for
  the same reason: the strategic ceiling is "don't run out of frontier," and
  equal play gives the first mover a one-stone win with no balancing rule.

## Phase 5 — Verdict

- P1-role experience sub-score (1-10): 3.9
- P2-role experience sub-score (1-10): 3.8 (must out-place to overcome tempo)
- Role-averaged sub-score: 3.85
- **Fairness perception (1-5):** 3 — Razor-thin P1 tempo edge under symmetric
  play (Line 1, 28–27) and no pie rule, but a better-placing P2 wins from the
  second seat (Line 2, 28–27), so skill dominates structure → effectively
  balanced.
- **Overall (1-10, anchored): 3.9**
- One-paragraph justification: C is a clean, transparent hex territory race with
  no vestigial machinery, and it carries genuine if shallow strategy: Lines 2–3
  show frontier management — not seat order — usually decides, since a careless
  player strands itself out of legal placements (my P2 won from behind, 28–27)
  and mutual mismanagement stalls the race entirely. Against that, the strategic
  ceiling is modest and equal competent filling hands the first mover a single-
  stone win with no balancing rule. Removing MOVE/super-ko (vs the sibling) costs
  nothing in practice and arguably makes it the cleaner of the two. Decisive,
  fair-ish, honest about its rules, but not deep — anchored at 3.9.

---

## Cross-game comparison (all 7 games — Team 2)

Engine-verified per game; scored against R8 4.10 / R19 4.375 (top) / R20 3.73 /
R21 3.69, anchoring DOWN; 5.0 = never-cleared ceiling.

**Ranking by Overall (high → low):**
1. **B — 4.3** (Menger-sponge influence-threshold race; pie rule; ghost-poison capture)
2. **F — 4.0** (square-grid orthogonal connection race; Hex/Bridg-it-like)
3. **C — 3.9** (hex territory fill race, no MOVE) ┐ effectively co-ranked twins
3. **G — 3.9** (hex territory fill race, with MOVE) ┘ (mechanically near-identical)
5. **E — 3.7** (3D-Moore CA connection; genuine sacrificial disruption, but chaotic + first-mover tilt)
6. **D — 3.3** (torus Othello-capture race; influence threshold is unreachable/dead)
7. **A — 1.5** (5D-Moore CA connection; forced 3-ply first-player win, zero counterplay — broken)

**Most want to play again:** **B**, by **+0.3** over F. B is the only game whose
several subsystems genuinely interlock AND that ships a working balance mechanism;
I won and lost decisive games on my own decisions in it.

**Single most differentiating mechanic of the top game (B):** the
**ghost-influence-poison on capture** combined with a **functional pie rule**.
Capturing in B is a *liability* (the removed stone's enemy-sign influence stays,
cancelling your own — I forced a capture that netted 0 score), and the pie-swap
actually equalised a first-mover race I watched flip from a P1 win (32–27) to a
P2 win (32–27). No other game here has either property: F and D carry influence
fields that are inert, A/E have no balance rule and first-mover tilt, and C/G are
clean but shallow fill-races. Notable observation (from --rules only): **C and G
are mechanically identical hex territory races except C lacks MOVE/super-ko**,
and they played the same in my hands (P1 28–27 greedy; P2 28–27 from the second
seat; 27/27 stall) — I scored them equally.

**Role win-split log (from my filed game lines):**
- A: P1-role 1/1 P1 wins; P2-role win only when P1 declined → P1-tilt flag (>80/20).
- B: P1-role P1 win; P2-role P2 win (via pie) → balanced.
- C: P1-role P1 win; P2-role P2 win (from 2nd seat) → balanced.
- D: stone-lead P1 (34–27) but draws common; no threshold ever met.
- E: P1-role P1 win (ply 7); P2-role P2 win when P1 stalled; disruption denies P1 → P1-tilt.
- F: P1-role P1 win; P2-role P2 win → balanced.
- G: P1-role P1 win; P2-role P2 win (from 2nd seat) → balanced.
