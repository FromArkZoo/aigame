# Team-19 Evaluation — Game 992bf7dfc9f4 (R14 rank 5, GE 0.4196, ELO 2953)

## PHASE 1 — RULE COMPREHENSION

**Board:** 8x8 grid (von Neumann 4-neighborhood), topology=grid.
**Players:** 2. **State dimension:** 131. **Actions:** 65 (64 placements + pass at index 64).

**Turn structure: SIMULTANEOUS** with `turn_type=simultaneous`, `pieces_per_turn=1`.
- Both players submit one action per round; engine resolves via `step_simultaneous()`.
- **Collision rule:** if both players target the same cell, MUTUAL ANNIHILATION — neither stone is placed, cell stays as-is.
- **Double-pass rule:** both passing ends the game and resolves by majority piece count.
- If only one passes, only that player skips placement; CA still runs; game continues.

**Action types:** `place` only (no move). **Placement rule:**
- Target: empty cells.
- Constraint: `adjacent_to_own` (must be orthogonally adjacent to an existing own stone), EXCEPT `first_move_anywhere=True` — if the player has 0 stones, they may place anywhere empty.

**Capture rule:** `capture_type=none` (no classical Go capture). All interactions are via the CA.

**Propagation rule:** `prop_type=none`. No influence field.

**Cellular automaton:** 75 total transition entries covering (cell_state ∈ {0=empty, 1=OWN, 2=ENEMY}) × (friendly_count 0-4) × (enemy_count 0-4). **16 entries are non-trivial** (new_state ≠ current_state). Breakdown:
- **Births (empty → OWN): 6 entries** — `(0,2,0), (0,2,1), (0,2,4), (0,3,4), (0,4,0), (0,4,1) → 1`
- **OWN deaths (OWN → empty): 4 entries** — `(1,0,2), (1,1,2), (1,1,3), (1,3,4) → 0`
- **OWN flip to ENEMY: 2 entries** — `(1,0,1), (1,2,3) → 2`
- **ENEMY deaths (ENEMY → empty): 3 entries** — `(2,3,0), (2,3,2), (2,4,3) → 0`
- **ENEMY flip to OWN: 1 entry** — `(2,2,0) → 1`

**CA runs `steps_per_turn=1` per round.** Engine code (`engine_v2.py:250-254`): `for i in range(steps_per_turn): acting_player = 1 if i % 2 == 0 else 2`. With `steps_per_turn=1`, ONLY i=0 runs, so **CA always runs from Player 1's perspective**. "OWN" = P1; "ENEMY" = P2. This produces a severe structural asymmetry (see balance below).

**Win condition:** `condition_type=territory, threshold=0.6253`, `max_turns=100`. Player wins if they own > 62.53% of 64 cells = 41+ stones. If no one hits threshold and game ends by double-pass or max_turns, the majority piece count wins.

### Flagged degeneracies

1. **CA asymmetry (major):** Because `steps_per_turn=1`, the "alternating perspective" logic never alternates — P1 is always the CA-acting player. Births only create P1 stones, surround-captures only convert P2→P1, and the `(OWN, f=0, e=1) → ENEMY` flip only affects P1 stones. P2 has NO CA-driven offensive tool. This is likely a generator oversight (the alternating-perspective code only activates if `steps_per_turn≥2`).
2. **Double-pass majority resolution** exists and was triggered in Game 2. Relevant because threshold of 41/64 is steep; defensive games can stall below threshold and end by majority.
3. **P2 opening-flip attack (major strategic knob):** P2 can play adjacent to P1's opening stone, exploiting `(OWN, f=0, e=1) → ENEMY`. Result: P1's stone flips to P2 → P2 has 2 stones, P1 has 0. Recoverable by P1 (first_move_anywhere lets P1 re-open), but costs tempo.
4. **CA rules not inert** — 16/75 non-trivial transitions, ~4 of them fired in every game I played (births dominated). NOT dormant.

---

## PHASE 2 — STRATEGIC PLAY

### Game 1: Conservative openings, symmetric build-up
- **R1:** P1→(3,3)=27, P2→(4,4)=36. Diagonal, not adjacent. Both survive.
- **R2:** P1→19, P2→44. Both build vertical pairs.
- **R3:** P1→26 forming 2x2 at rows 2-3 cols 2-3. CA births P1 at (2,2). P1=4, P2=3.
- **R4-R10:** P1 extends cluster, every placement triggers 1-3 CA births. Typical gain: P1 +2 to +4/round, P2 +1/round.
- **R14:** P1→49 triggers births at 48, 50, and naturally at 0. P1 reaches 41 → **territory win**.
- **Final:** P1=41, P2=14. **P1 wins by threshold.**
- **Collisions:** 0. **Flips:** 0. **Deaths:** 0. Resolved cleanly by win condition.

### Game 2: P2 aggressive opening flip attack
- **R1:** P1→27, P2→35. P2's stone at (3,4) is adjacent to P1's (3,3) — P1 stone flips to P2. **P1=0, P2=2.**
- **R2:** P1→0 (corner, far from P2 to hide). P2→36. P1=1, P2=3.
- **R3-R5:** P1 rebuilds in top-left corner via (0,0)→(1,0)→(0,1)→(1,2)+births. P2 builds cluster mid-board.
- **R6:** P1→10, P2→18. **TRAP PLAY:** P1's new stone at 10 becomes OWN with f=1 (from 9=P1), e=2 (P2 at 11, 18). Rule `(1,1,2)=0` → P1's placement DIES! Net: P1 gains a birth at 2 only. P1=7, P2=7.
- **R9:** P1→40. **BLOCK:** P2 plays 41 to occupy the cell where P1 was about to birth. P1=12 (lost the birth), P2=10.
- **R12-R18:** Both players alternate slow placement. P1 builds top-row extension. P2 builds south. No more flips or traps.
- **R24:** P1's cluster saturates; only legal moves are isolated pockets. P1 forced to pass, P2 plays 58 (collision intended).
- **R29:** Both play cell 60 (last empty cell between clusters) — COLLISION, neither places.
- **R31:** Both pass → game ends by majority. **P1=34, P2=29. P1 wins by double-pass majority.**
- **Collisions:** 1 (R29). **Flips:** 1 (R1). **Deaths:** 1 (P1's cell 10 at R6). **Pass-resolution: YES.**

### Game 3: Seat-swap acknowledgment; distant openings
- **R1:** P1→27, P2→38 (far apart, not adjacent). P1=1, P2=1.
- **R2-R15:** P1 builds dense cluster in NW, P2 builds in SE. P1's CA-birth machine outgrows P2 by ~2x.
- **R12:** P2 has no legal placements other than pass — P1 has engulfed most of the adjacent empty space around P2's cluster.
- **R15:** P1→37 (attempts birth trigger), CA births P1 to 43 stones. **P1=43 > 41 threshold. P1 wins by territory.**
- **Final:** P1=43, P2=11.
- **Collisions:** 0. **Flips:** 0. **Deaths:** 0. No pass-resolution.

### Non-convergence/double-pass: Game 2 resolved by double-pass majority. Games 1 and 3 resolved cleanly by territory threshold. 1/3 by double-pass.

### Player 1 strategy guide

1. **Opening:** central cell (e.g., 27). Accept ~6% flip risk.
2. **Round 2-3:** play orthogonal neighbors of R1 to form a 2x2 block ASAP.
3. **Rounds 4+:** every round, find a placement that triggers at least 1 CA birth via `(empty, f=2, e=?) → OWN`. Typical targets: an empty cell with 1 P1 neighbor, placing a stone that becomes its second P1 neighbor.
4. **Avoid placing with f≤1 and e≥2** — will die via `(1,1,2)=0` or `(1,0,2)=0`.
5. **Expect to win by R14-R16** with territory threshold.

### Player 2 strategy guide

1. **Opening flip attack:** play a cell adjacent to 3+ plausible P1 openings (e.g., 35). Success = +2 stones.
2. **Block-play:** when P1 is about to place at cell X to trigger a birth at Y, if Y is adjacent to your cluster, occupy Y preemptively.
3. **Trap-play:** in the simultaneous round, if P1 is about to place a stone that will become a weak-f neighbor to your cluster, make the placement dense enough (e≥2) around P1's target cell to kill it via `(1, f≤1, 2) → empty`.
4. **You have no birth rule.** Every round, your growth is exactly +1 (placement only).
5. **Realistic expectation:** lose unless training opponent makes mistakes. The structural P1-favor from the CA is unrecoverable.

---

## PHASE 3 — STRATEGIC ANALYSIS (JOINT)

**Seat-identity bias caveat:** all three games were played by the same sequential reasoner. Game 3's seat-swap is nominal only. Inter-team comparison needed to triangulate true balance.

- **Distinct viable strategies?** NO. Each role has essentially one dominant strategy (cluster+birth for P1; flip+block for P2). No room for variety.
- **Counter-play?** LIMITED. P2's trap play and block play are real responses (G2 R6, R9). P1's only counter is to avoid placing near P2 boundary. Depth 1-2 moves.
- **Short-term vs long-term tension?** MINIMAL. Greedy +piece-count per round is near-optimal. Sacrifice rarely beneficial.
- **Emergent concepts:**
  - **Territory** (explicit in win condition).
  - **Clump-as-organism** (2x2 P1 block self-replicates).
  - **Asymmetric CA-perspective advantage** — P1's structural dominance.
  - **Collision denial** (theoretical; used 1/3 games).
  - **Trap plays** (simultaneous-only; used 1/3 games).
  - **Blind commitment tension** in opening (Matching-Pennies mixed strategy).
- **Topology relevance:** von Neumann 4-neighbor grid affects birth triggers (corners can't reach f=4). 8x8 + 62.5% threshold = dominant-win required. Does influence play significantly.
- **First-mover advantage / simultaneity check:** Simultaneity DOES eliminate temporal first-mover advantage — neither player knows what the other does in round 1. But it **does NOT eliminate seat-identity advantage** because the CA runs from P1's perspective, not alternately. This is the key finding for Run 15: **simultaneity + active CA together do NOT necessarily produce balance** — the CA's perspective is independently fixed.
- **Seat-swap evidence:** Games 1, 2, 3 all won by P1 (41-14, 34-29, 43-11). Training data nonetheless shows 50/50 P1 vs P2 winrates — suggesting either (a) trained agents find a non-greedy Nash equilibrium I didn't discover, (b) training win-rate averaging obscures true balance, or (c) the specific opening moves in training happen to neutralize P1's advantage. Manual play shows **P1 dominant 3/3**.

---

## PHASE 4 — NOVELTY ADVERSARY

**Adversary argued:**
- Core mechanics decomposition: Go (territory threshold + placement), Reversi (flip-via-flank = `(OWN, f=0, e=1) → ENEMY`), Life B2-like CA (birth at f=2 in empty cells), Gungo (simultaneous Go), Diplomacy order-resolution (collision handling), Colonel Blotto (blind allocation to same cell).
- The CA is a standard two-color totalistic von-Neumann CA; the specific transitions are near-arbitrary parameter choices.
- Topology transformation: strip simultaneity + birth → Reversi-on-4-neighbors. Strip placement → 2-color Life.
- Expert transfer test: An Othello + Conway's Life dual expert would immediately recognize and exploit the combined mechanics (and this is exactly what I did in Phase 2).

**P1/P2 Rebuttal (strongest points):**
- The CA asymmetry (always runs from P1's view) creates unintended structural imbalance that isn't a feature of Reversi or Gungo; novel (if broken).
- The birth rule is NOT Othello (Othello doesn't create stones from nothing). Combining birth + territorial win + simultaneity is an unusual composition.
- Trap plays (G2 R6) are a simultaneous-only mechanic — alternating Reversi wouldn't have them.
- The `adjacent_to_own` placement with `first_move_anywhere=True` creates a specific frontier-expansion dynamic absent from pure Reversi/Life.

**However:** Every dynamic I observed was predictable from component analysis. No emergent surprise. The game is a readable composition.

### Novelty score: **4/10**

Rationale: Well-known components combined in a specific way with an unintentional asymmetry. An expert at any 2 of {Othello, Life, Go, simultaneous games} would have an immediate advantage. Does NOT break new strategic ground.

---

## PHASE 5 — VERDICT

**Team ID:** team-19  
**Game ID:** 992bf7dfc9f4  
**Rules Summary:** 8x8 simultaneous-placement territory game where both players submit one placement per round; CA then evolves the board using a fixed P1-perspective totalistic rule (births, deaths, flips) and wins declared by 62.5% territory or double-pass majority.  
**Topology:** 2D grid, 8×8, von Neumann (4-neighbor).  
**Turn Structure:** simultaneous.

### SCORES

- **Strategic Depth: 3/10.** P1 has an obvious dominant strategy (cluster+birth). P2 has limited counter-play (opening flip + trap + block, all tactical and 1-2 moves deep). No deep sacrifice-tempo-initiative dynamics. Most rounds are greedy "maximize this round's gain."
- **Emergent Complexity: 4/10.** The CA does produce interesting self-propagating clumps (P1's 2x2 → 3x3 cascade), and trap plays under simultaneous commitment are genuinely simultaneous-only phenomena. But the complexity is surface-level — no chains of reasoning or meaningful long-range effects.
- **Balance: 2/10.** I played 3 games, P1 won 3/3 (scores 41-14, 34-29, 43-11). The `steps_per_turn=1` with always-P1-perspective CA means P1 gets all the productive transitions (births, surround-captures) while P2 gets only placement. Training data shows 50/50 winrate, which I cannot reconcile with my hands-on result — either agent-specific convergence artifact or a Nash strategy I missed. **Observed seat advantage: heavily to P1.**
- **Novelty (post-adversary): 4/10.** Strongest adversary argument: this is Reversi-flanking + Life-B2-birth + Go-territory + Gungo-simultaneity composed on 8x8 von Neumann grid — every component is published; the combination is specific but readable. Rebuttal: trap plays and the unintended CA asymmetry add some uniqueness. Net: compositional novelty only.
- **Replayability: 3/10.** Because strategies are near-solved (cluster+birth dominant; P2 has essentially one path), repeat play reveals little new. Different openings (G1/G2/G3) still converge to the same endgame shape. Training data average length of 29 rounds confirms quick convergence.
- **Overall "Would I play this again?" : 3/10.** Not fun because strategy is solved. Useful as a research artifact (shows CA-asymmetry failure mode of "simultaneous balancing").

### CLOSEST KNOWN-GAME ANALOG

**Reversi/Othello crossed with Conway's Life on an 8x8 von Neumann grid, with simultaneous turns.** Not identical because: (a) Reversi does not create new stones from empty cells (the CA birth rule is distinctly Life-ish); (b) classical Life has only one color; (c) simultaneous turns with collision-annihilation is Gungo-style, absent from Reversi/Life. The combination into a territory-win game is unpublished but the parts are trivially familiar.

### KILLER FLAWS

1. **CA always runs from P1's perspective (structural asymmetry).** With `steps_per_turn=1`, the intended "alternate perspective" never alternates. P1 gets all birth and capture benefits; P2 gets none. Manual play shows P1 wins 3/3.
2. **P1's cluster growth is self-sustaining.** Even passing lets P1 gain stones via CA natural births. This undermines any defensive strategy.
3. **P2's only offensive tool is the R1 opening flip**, which is probabilistic (requires correct guess of P1's opening) and recoverable by P1 via `first_move_anywhere`.
4. **The 62.5% territory threshold requires a blowout** (41/64 stones). Either P1 wins with dominant CA growth, or the game stalls below threshold and resolves by double-pass majority — which P1 also tends to win.

### BEST QUALITY

**The trap-play mechanic under simultaneous commitment** (Game 2 Round 6): P2 placing a cell that rendered P1's simultaneously-placed stone vulnerable to immediate CA death. This is a genuinely simultaneous-only dynamic — in alternating play, P1 would see the trap before committing. A deliberate symmetric version of this mechanic could be interesting as the basis of a better game.

### IMPROVEMENT IDEAS

**Critical fix: make the CA alternate perspective reliably.** Set `steps_per_turn=2` and run one step from P1 view, one from P2 view (the engine logic already does this when `steps_per_turn≥2`). This would symmetrize births/captures/flips between players and restore balance. Alternatively, restructure the CA rule to be state-symmetric by design (e.g., introduce corresponding `(empty, f=0, e=2) → ENEMY` and `(ENEMY, f=0, e=1) → OWN` rules so both colors can birth and flip mirror-wise).

A secondary improvement: lower the win threshold to ~51% (majority) and let double-pass be the DEFAULT endgame. This would emphasize contested boundaries over dominant-blowout wins.
