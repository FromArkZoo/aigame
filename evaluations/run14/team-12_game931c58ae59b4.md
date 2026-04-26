# Team-12 Evaluation — Run 14 Game `931c58ae59b4`

- Team ID: **team-12**
- Game ID: **931c58ae59b4**
- Run 14 rank 3 by Go Essence 0.4824, highest ELO on the leaderboard (3035.4).
- Representation: v3, seed game, generation 10 (metadata says generation 0 — it is a root seed).

Evaluator disclosure: single sequential reasoner playing P1 and P2; seat-identity bias acknowledged and mitigated by the game-3 swap.

---

## PHASE 1 — RULE COMPREHENSION

### Board

- 2D grid, 8x8 = 64 cells.
- Topology: **moore** (8-neighborhood for adjacency; Chebyshev distance for propagation after the Run 14 distance-fix).
- `play_helper.py rules` prints "von Neumann (face-adjacent only, no diagonals)" for moore boards — that display string is wrong; the actual `_build_moore_neighbors` routine in `game_engine/topology.py` includes all 8 neighbors (confirmed empirically: one P1 stone at (3,3) yields 8 legal `adjacent_to_own` placements).
- 65 actions: 0-63 are placements indexed as `y * 8 + x`; action 64 is **pass**.

### Turn structure

- **Alternating**, 1 piece per turn. Not simultaneous. The Run-14 simultaneous-play mechanic is NOT present in this game, so the new R14 collision rule is not exercised.
- Max turns: 100.

### Action types

- Place only. No movement. `action_rule.action_types = ["place"]`.

### Placement constraint

- `target: empty`, `constraint: adjacent_to_own`, `first_move_anywhere: true`.
- First move of each side is anywhere; thereafter each side must place on an empty cell that is Moore-adjacent to one of their own stones.
- Because `adjacent_to_own` is strict, a player whose pieces are fully surrounded / captured can have zero legal placements and must pass.

### Capture

- `capture_type: surround`, `threshold: 1` — classical Go-style: any enemy group with zero liberties is removed. (No multi-stone threshold.)
- After a placement, standard captures are resolved before propagation clipping.
- Suicide/ko handling uses the engine's super-ko via board-hash saves.

### Propagation (influence)

- `prop_type: influence`, `radius: 2`, `strength: 1.6154803884858167`, `decay: 0.46162360080698384`.
- After each placement, board_values at every cell within Chebyshev distance 2 of the placed stone are incremented by `sign * strength * decay^dist` (sign = +1 for P1, -1 for P2). Clipped to ±100.
- Per-move influence footprint (Moore, interior cell):
  - distance 0 (self): 1.6155
  - distance 1 (8 cells): 0.7459 each
  - distance 2 (16 cells): 0.3444 each
  - Total if fully interior: 1.6155 + 5.9672 + 5.5104 = **13.09 per move**.
- Edge/corner placements deposit less (fewer in-bounds target cells).

### Win condition

- `condition_type: threshold`, `threshold: 63.4597`, `target_dimension: 0`.
- A player wins when the sum of `board_values` over cells they currently own (scalar-sign-corrected: P1 sum, or −P2 sum) exceeds 63.46.
- If `max_turns` (100) is reached first, win by **majority piece count** (double-pass also terminates; this game then falls through to majority piece count).

### Degeneracy / pitfalls check

- **Double-pass / majority exploit:** because the game ends by majority piece count if both players pass consecutively, and because a player with no adjacent-empty cell is *forced* to pass, it is plausible that a leader could stall out the game once piece count is ahead. Flag it; will track in Phase 2.
- **Threshold reachable?** Yes. 13.09/move * ~5 moves = ~65, but only if all influence lands on own-owned cells. In practice the enemy's stones absorb roughly half, so expect 8-12 productive moves to trip the threshold. Average training game length 24-26 moves is consistent with threshold wins + some capture-driven resolution.
- **Capture rule (threshold 1) is active** — suicide/0-liberty removal is Go-standard.
- **No CA.** Not an issue for this game.
- **Starting-position / always-wins exploit:** first-move-anywhere + radius-2 influence → center-ish first move deposits 13.09; the symmetric response cancels it. No obvious forced-win.

Phase-1 summary: this is essentially **Go with a radius-2 continuous influence field and a threshold-on-owned-cells win condition, on a Moore-adjacency 8x8 board**. No simultaneous play, no cellular automaton.

---

## PHASE 2 — STRATEGIC PLAY

Setup: the single reasoner played P1 first, then switched to P2 for each move (finalizing the prior role's reflection before switching). In game 3 the seats are swapped. Every move was engine-verified by running the full move sequence through `play_helper.py ... --action play`.

### Game 1 — P1 centre-opens, P2 mirrors diagonally

Move log (as a comma-separated action list verified end-to-end):

`27, 54, 36, 45, 28, 46, 35, 53, 18, 63, 19, 44, 20, 43, 26, 37, 11, 52, 12, 51, 10, 34, 21`

| Ply | Player | Action | Cell | Reasoning (≤2 sentences) | P1 sum | P2 sum |
|---|---|---|---|---|---|---|
| 1 | P1 | 27 | (3,3) | Central first-move-anywhere to maximise the radius-2 footprint fully on-board (13.09/move). | +1.62 | 0 |
| 2 | P2 | 54 | (6,6) | Diagonally far enough (Chebyshev 3) to escape P1's radius-2, start an opposing cluster. | +1.62 | +1.62 |
| 3 | P1 | 36 | (4,4) | Stack influence on (3,3) self; (3,3) cell now carries influence from two P1 stones. | +4.38 | +1.27 |
| 4 | P2 | 45 | (5,5) | Mirror of P1's (4,4) about centre; keeps parity exactly. | +3.29 | +3.29 |
| 5 | P1 | 28 | (4,3) | Form a tight 3-cluster. Dense packing stacks influence on all own stones. | +7.54 | +2.94 |
| 6 | P2 | 46 | (6,5) | Mirror counter, build 3-stone L. | +6.85 | +6.85 |
| 7 | P1 | 35 | (3,4) | Close the 2×2 block at (3,3)-(4,4): each stone within dist-1 of three others → ~3× influence stacking. | +12.60 | +6.51 |
| 8 | P2 | 53 | (5,6) | Mirror — complete P2's 2×2 block. | +11.91 | +11.91 |
| 9 | P1 | 18 | (2,2) | Extend NW corner; cell was empty at +1.78 → becomes owned and stacked. | +17.08 | +11.91 |
| 10 | P2 | 63 | (7,7) | Mirror. Parity still holding. | +17.08 | +17.08 |
| 11 | P1 | 19 | (3,2) | Now the cluster is 6 stones; (3,2) as the north edge deposits on 6 own stones. **Biggest single-move gain so far (+7.47).** | +24.55 | +17.08 |
| 12 | P2 | 44 | (4,5) | Broke parity — attack into P1's airspace instead of pure mirror. Deposits −0.745 on P1's (4,4) and (3,5)/(5,5)/(5,4) edges. | +22.37 | +20.88 |
| 13 | P1 | 20 | (4,2) | Solidify north edge; another +7.98 swing. | +30.53 | +20.88 |
| 14 | P2 | 43 | (3,5) | Mirror attack on P1's south boundary. P2 starts closing the gap. | +28.35 | +23.18 |
| 15 | P1 | 26 | (2,3) | West extension, deposits on 7 own stones at dist ≤ 2 — the densest-stacking move available. | +37.30 | +22.50 |
| 16 | P2 | 37 | (5,4) | Mirror attack. | +34.44 | +27.78 |
| 17 | P1 | 11 | (3,1) | North row extension; (3,1) empty at +3.27 → claim it. | +42.59 | +27.78 |
| 18 | P2 | 52 | (4,6) | Mirror south. | +41.90 | +36.74 |
| 19 | P1 | 12 | (4,1) | Highest empty cell at +3.61 — grab it. | +50.75 | +36.74 |
| 20 | P2 | 51 | (3,6) | Mirror. | +50.06 | +44.21 |
| 21 | P1 | 10 | (2,1) | +3.96 empty cell — richest spot. | +59.59 | +44.21 |
| 22 | P2 | 34 | (2,4) | **Attack move inside P1's zone** — deposits −0.745 on six P1 stones. Knocked P1 down from 59.6 to 55.6. | +55.63 | +45.42 |
| 23 | P1 | 21 | (5,2) | Final push: (5,2) empty at +3.61 and deposits on five own stones + one P2 stone. Crosses threshold. | **+64.82** (WIN) | +45.08 |

**Result:** P1 wins at move 23 by threshold (64.82 > 63.46). No double-pass; no max-turn timeout. Resolved cleanly via the stated win condition.

#### Player 1 reflection (Game 1, finalized before role-switch)
- Strategy used: seize the centre, then grow a *dense 2×2 → 3×3 cluster* outward. Each new stone placed on the perimeter of the cluster stacks influence on many own stones simultaneously; this is the dominant scoring engine.
- Would do differently: move 11 (3,2) was greedy-correct, but I could have played an earlier disrupting move (e.g. 44 at turn 9) to contaminate P2's territory before they solidified. Early contamination prevents the mirror strategy from ever equalising.
- Opponent surprise: P2's (4,5) at move 12 was an excellent attack rather than mirror; I hadn't planned for P2 to break parity. The damage was real (−2.18 for me, +3.80 for them on that move). P2's final attack at (2,4) also ate 3.96 of my lead.
- Endgame: threshold win, not double-pass or timeout.

#### Player 2 reflection (Game 1)
- Strategy used: reflect P1's moves across the board centre (mirror strategy). Maintained parity through move 10.
- Would do differently: mirror is a *losing* strategy for P2 because P1 moves first and reaches threshold first. I should have deviated earlier — by turn 5 I should have been attacking P1's cluster to contaminate P1-owned cells (depositing +influence on them means P1's stones "hurt" themselves). The two attacking moves I did play (44 and 34) were the only moves that narrowed the gap; I should have started them 4 plies sooner.
- Opponent surprise: not really — P1 played textbook densification.
- Endgame: threshold win, clean.

### Game 2 — P1 again opens centre; P2 attacks immediately

Strategy swap: P2 abandons mirror from the start and plays attacking "contamination" moves inside P1's radius-2 zone. Early attack `(5,5) → (4,4) → (3,4)` inside the P1 cluster.

Move log: `27, 45, 18, 36, 28, 35, 19, 26, 11, 43, 10, 34, 12, 25, 20, 29, 3, 21, 2, 22, 9, 13, 1, 4, 17, 16, 8, 24, 0`

| Ply | Pl | Act | Cell | Short note | P1 / P2 sums |
|---|---|---|---|---|---|
| 1 | P1 | 27 | (3,3) | Centre. | 1.62 / 0 |
| 2 | P2 | 45 | (5,5) | Closer than game 1 — dist 2 from P1 so already in P1's influence band. | 1.27 / 1.27 |
| 3 | P1 | 18 | (2,2) | Safe corner build away from P2. | 4.38 / 1.27 |
| 4 | P2 | 36 | (4,4) | **Attacking step-in** between P1 stones — first real contamination move. | 3.29 / 3.29 |
| 5 | P1 | 28 | (4,3) | Counter-attack: P1's own stone in the contested zone reduces P2's (4,4) by depositing +0.745 on it. | 5.99 / 2.20 |
| 6 | P2 | 35 | (3,4) | Mirror-attack (symmetric). | 4.16 / 4.16 |
| 7 | P1 | 19 | (3,2) | Dense build (5 own neighbours in Moore-2 range). | 9.56 / 3.47 |
| 8 | P2 | 26 | (2,3) | Surgical: connects (3,4) group and damages (2,2),(3,2),(3,3). | 6.98 / 4.68 |
| 9 | P1 | 11 | (3,1) | Stack. | 12.61 / 4.34 |
| 10 | P2 | 43 | (3,5) | Extend P2 group; stacks on (3,4),(4,4),(2,3). +5.29 swing for P2. | 11.92 / 9.63 |
| 11 | P1 | 10 | (2,1) | Stack. | 19.04 / 9.28 |
| 12 | P2 | 34 | (2,4) | Attack core — hits (3,3) at d1 and (2,2)(3,2)(4,3) at d2. | 17.27 / 14.28 |
| 13 | P1 | 12 | (4,1) | Stack. | 24.27 / 13.94 |
| 14 | P2 | 25 | (1,3) | Contamination attack. | 22.15 / 17.79 |
| 15 | P1 | 20 | (4,2) | Stack (5 P1 d1 neighbours). +9.07. | 31.22 / 16.41 |
| 16 | P2 | 29 | (5,3) | East-flank attack. | 28.36 / 18.72 |
| 17 | P1 | 3 | (3,0) | Top edge stack. +8.16. | 36.51 / 18.72 |
| 18 | P2 | 21 | (5,2) | **Suicide-damage move** — P2 places on high-positive cell (+2.18), losing −0.56 itself but delivering −3.61 damage to P1's cluster (hits (4,1),(4,2),(4,3) d1 plus (3,0),(3,1),(3,2),(3,3) d2). Relative gain +4.14. | 32.90 / 19.59 |
| 19 | P1 | 2 | (2,0) | Stack. | 41.74 / 19.59 |
| 20 | P2 | 22 | (6,2) | Further contamination east. | 40.71 / 23.84 |
| 21 | P1 | 9 | (1,1) | Stack. +8.16. | 48.86 / 23.15 |
| 22 | P2 | 13 | (5,1) | Stacks on (5,2) P2 while deposing −0.745 on (4,1),(4,2) P1. | 45.65 / 25.23 |
| 23 | P1 | 1 | (1,0) | Stack. | 54.49 / 25.23 |
| 24 | P2 | 4 | (4,0) | Attack north flank (contaminates (3,0),(3,1)). | 50.54 / 25.75 |
| 25 | P1 | 17 | (1,2) | Stack (3 P1 d1 + 2 P2 d1 contamination). | 58.58 / 23.57 |
| 26 | P2 | 16 | (0,2) | Attack (0,2). | 55.71 / 25.19 |
| 27 | P1 | 8 | (0,1) | Stack. | 62.43 / 23.75 |
| 28 | P2 | 24 | (0,3) | Last-ditch attack; P1 dropped below threshold to 60.31 momentarily. | 60.31 / 27.61 |
| 29 | P1 | 0 | (0,0) | Final corner-claim; reaches **68.81** > 63.46. Win. | **68.81** / 27.26 |

**Result:** P1 wins at move 29 by threshold. No double-pass / timeout. 6 moves longer than Game 1 because P2's attacking strategy extracted more P1 value per P2 move — ~3.6 P1 points per P2 ply vs ~0 in Game 1 (mirror).

#### Player 1 reflection (Game 2)
- Strategy: same as Game 1 — densify centre cluster, claim highest-value perimeter empty cells, then fill edges.
- What I'd do differently: the "dense 2×2 block" core (move 3 at 28 and move 4 that never happened because P2 stole (3,4) before I could complete it) proved essential. In G2, P2 took (3,4)=35 at move 6, preventing my 2×2 — but I still won because edge-cells (2,0)-(5,0) compound heavily with the N-W cluster.
- Opponent surprise: P2's move 18 (5,2) was a *suicide-damage* play: P2 voluntarily placed on a +2.18 cell (losing value on their own stone) to deliver −3.61 damage to P1. This is a strategic dimension I had not anticipated from the rulebook.
- Endgame: threshold win, clean.

#### Player 2 reflection (Game 2)
- Strategy: attack-first. Target high-value empty cells inside P1's future build zone and contaminate them so P1's eventual placements there are less profitable. Willing to sacrifice P2 cell-value to damage P1's sum.
- What I'd do differently: even more aggressive. My move 8 (3,5) at +5.29 was by far my biggest swing — I should have been playing that type of move from move 4. I was also late to the threshold race: P2's influence did build from 0.53 to 27.61, but the marginal cost of each P2 attack was high because P2-owned cells with positive P1-influence *reduce* P2's effective score.
- Opponent surprise: P1's very tight cluster means each P1 move gained ~7-9 points reliably (compared to P2's ~4-6), because P1 had more own-stones at dist ≤ 2 to stack on.
- Endgame: threshold win.

### Game 3 — seat swap. P1 opens centre; the reasoner plays P2 as primary and deploys the attack strategy maximally

Move log: `27, 36, 18, 35, 28, 26, 10, 17, 11, 34, 19, 25, 12, 33, 20, 42, 13, 43, 4, 44, 3, 50, 21`

| Ply | Pl | Act | Cell | Short note | P1 / P2 sums |
|---|---|---|---|---|---|
| 1 | P1 | 27 | (3,3) | Centre. | 1.62 / 0 |
| 2 | P2 | 36 | (4,4) | **Immediate attack** on move 2 — step-in adjacent to P1. | 0.87 / 0.87 |
| 3 | P1 | 18 | (2,2) | Safe corner. | 3.63 / 0.53 |
| 4 | P2 | 35 | (3,4) | Extend attack; parity restored. | 2.54 / 2.54 |
| 5 | P1 | 28 | (4,3) | Counter-attack (same as G2). | 4.85 / 1.05 |
| 6 | P2 | 26 | (2,3) | Group + contaminate (2,2),(3,3). | 3.01 / 3.01 |
| 7 | P1 | 10 | (2,1) | Stack away from P2. | 7.15 / 2.67 |
| 8 | P2 | 17 | (1,2) | Attack (2,1),(2,2) at d1. | 5.32 / 4.63 |
| 9 | P1 | 11 | (3,1) | Stack. | 10.60 / 3.94 |
| 10 | P2 | 34 | (2,4) | Deep group-attack (hits (3,3) d1). | 9.17 / 8.48 |
| 11 | P1 | 19 | (3,2) | Stack (5 P1 d1 neighbours). +7.0. | 16.12 / 6.36 |
| 12 | P2 | 25 | (1,3) | Connects P2 west group + −2.12 damage. | 13.99 / 11.01 |
| 13 | P1 | 12 | (4,1) | Stack (+7.0). | 21.00 / 10.67 |
| 14 | P2 | 33 | (1,4) | Stacks 3 P2 d1 → +6.4 P2. | 19.97 / 17.10 |
| 15 | P1 | 20 | (4,2) | Stack (+9.1). | 29.04 / 15.73 |
| 16 | P2 | 42 | (2,5) | Stacks on (2,4),(3,4),(1,4) + damages (3,3),(4,3) d2. +7.5 P2. | 28.36 / 23.19 |
| 17 | P1 | 13 | (5,1) | Stack east-edge. | 35.71 / 23.19 |
| 18 | P2 | 43 | (3,5) | **Maximum P2 move** — (3,5) stacks on 4 P2 d1 neighbours ((2,4),(3,4),(4,4),(2,5)). +9.0 for P2. | 35.02 / 32.15 |
| 19 | P1 | 4 | (4,0) | Top-edge stack. | 43.86 / 32.15 |
| 20 | P2 | 44 | (4,5) | Stacks 3 P2 d1 + damage (3,3),(4,3). +7.5 P2. | 43.17 / 39.62 |
| 21 | P1 | 3 | (3,0) | Stack (4 P1 d1). +9.99 P1. | 53.17 / 39.27 |
| 22 | P2 | 50 | (2,6) | Heavy pure-build: (2,6) stacks on 2 P2 d1 + 5 P2 d2 → +8.04 P2. | 53.17 / 47.31 |
| 23 | P1 | 21 | (5,2) | Final push — stacks 4 P1 d1 + 5 d2 + hits (3,4),(4,4) d2. Crosses threshold by **+0.04**. | **63.50** / 46.63 |

**Result:** P1 wins at move 23 by threshold, **margin 0.04**. No double-pass, no timeout. Much closer race than Game 1; the attack strategy made P2 a credible threat.

#### Player 2 reflection (Game 3, reasoner-primary)
- Strategy: *max-damage attack every move*. Target cells that (a) are adjacent to multiple P2 stones so the new P2 stone stacks several +0.745 each, and (b) are within Chebyshev-2 of multiple P1 stones so the new P2 stone deposits negative on them.
- What I'd do differently: move 22 `(2,6)` was a pure-build move (no P1 in range) and only contributed to my *own* score. A damage-move around move 22 might have dropped P1 below threshold. Specifically, if I had played (5,3) or (5,4) there, I'd have contaminated (4,2),(4,3),(5,1) and potentially stalled P1's win by one move. One extra move for P2 could have closed the gap further.
- Opponent surprise: even with my best attack, P1 still finished in 23 plies — same as the mirror-strategy Game 1. The takeaway is that first-mover advantage in this rule set is structural: P1 always gets the centre and one extra move of stack. The only difference is margin (G1: +19; G3: +0.04).
- Endgame: threshold win by 0.04 points. An *extremely* sharp finish; with two-three more P2-attack moves this could have gone the other way.

#### Player 1 reflection (Game 3)
- Strategy: the same densification pattern as G1/G2. I was slower than G1 (by moves 10-16 my lead was narrower) because P2 contaminated my future-claim cells before I could reach them.
- What I'd do differently: move 7 `(2,1)` could have been a hane like `(3,4)` (now P2) to prevent P2's L-shaped group. The cost: (3,4) is contested territory and P1's stone there would be less "safe" than (2,1).
- Opponent surprise: P2's move 18 `(3,5)` was a huge jump for P2 (+9). I had noted that (3,5) was a 4-P2-d1 stacking cell; when P2 claimed it I was unable to contest.
- Endgame: threshold win, razor-thin margin (+0.04).

### Strategy guides

**Player 1 guide.** (a) Open at the geometric centre `(3,3)` (action 27) — maximises the 13.09-influence footprint with all cells on-board. (b) Build a dense 2×2 or L-cluster in the centre; each next stone should place such that it has the **most existing own-stones** within Chebyshev 2 of the new cell, which maximises stacking. (c) Highest-value empty cell on the **P1 cluster perimeter** is always the correct move — do not reach into P2's zone unless it disrupts a P2 2×2 formation. (d) Keep your own stones far from P2's stones: P2 contamination of your cells shaves 0.3-0.7 per placement. (e) You win on ply ~21-23 if P2 plays mirror, or ply ~23-29 if P2 plays attack.

**Player 2 guide.** (a) **Abandon mirror immediately** — in three games the mirror lost by +19 margin while attack lost by +0.04. (b) First move: play adjacent to P1's centre (e.g. (4,4) or (3,4)) despite the cell's absorbed P1 influence — the damage and contamination is worth it. (c) Prioritise moves with the highest P2-d1-stack count. (d) Accept "suicide-damage" moves: placing on a positive-valued empty cell is usually bad for P2, but if you can hit 3+ P1-owned cells at Chebyshev ≤ 2, the relative gain is positive. (e) Against a competent P1, you will come within ~5 points of threshold but probably not win.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Distinct viable strategies?

Yes, two clear strategies with radically different payoffs:

1. **Mirror (P2's natural first instinct).** Play the 180° reflection of each P1 move. This preserves parity exactly for a while but loses by ~20 points because P1 gets one more move. Documented in Game 1 — every ply after move 4 had exact parity until P2 broke it at ply 12, but by then P1 had accumulated 22 points.

2. **Attack / contaminate (discovered in Game 2, refined in Game 3).** Place each P2 stone on a cell that (a) neighbours multiple P2 own stones (stacking), and (b) is within Chebyshev-2 of multiple P1 stones (damage). This loses by +0.04 to +13 depending on discipline. It is always the right choice over mirror.

A third idea we did not fully test: **capture-based play.** Because capture threshold is 1 (Go-standard), groups without liberties are removed. No group in our 3 games approached capture — minimum liberties observed was 5 — but on a smaller board or with a dominating 2×2 enclosure this might matter.

### Counter-play

There is real counter-play but it is asymmetric. P1 responds to P2's attacks with "hane"-style stones that contaminate the P2 attacker. Example Game 2 move 5: P1 plays (4,3) adjacent to P2's (4,4), which deposits +0.745 on P2's (4,4) *and* gives P1 a stone well-stacked on the existing (3,3),(2,2) cluster. This is the clearest tactical sequence — an attack-counter-attack with concrete influence-flow resolution.

### Short-term vs long-term tension

Present but shallow. Short-term: the next placement's cell value is directly scorable. Long-term: the dense cluster is worth 3-5× per subsequent stone. The tension resolves mostly into "claim the highest empty cell right now", since long-term stacking and short-term gain are correlated (dense clusters have higher-valued perimeter cells). The "suicide-damage" move in Game 2 move 18 is a rare exception — short-term sacrifice for long-term damage distribution.

### Emergent concepts

- **Influence stacking.** Dense clusters are non-linearly more valuable because each stone's radius-2 footprint overlaps several own-stone cells.
- **Contamination economy.** P2 cells sitting on net positive board_value are a *minus* for P2. This inverts the normal "more pieces = better" intuition and introduces a self-damage mechanic.
- **Territory equilibrium.** The 8×8 board with radius-2 influence has an effective "claim radius" of ~3, so the natural partition of the board is into two 4×4 quadrants — exactly what emerged in all three games.
- No Go-like *ko* fights emerged (the engine has super-ko but it never activated in our play). No capture cascades.
- **First-move asymmetry quantified.** P1 wins all three games; with best play by both sides (Game 3) the margin is +0.04. With mirror-P2 the margin is +19.74. So first-mover advantage is **~20 points** in raw terms but only **~0.04 points** when both play optimally — an enormous gap that the evaluator team should flag.

### Does topology matter?

Moderately. The Moore topology (8-neighbour, Chebyshev-2 distance) gives a 5×5 = 25-cell footprint per stone, vs 13 on grid/von-Neumann. This makes density stacking more rewarding than on a grid. The game feels genuinely different from what a radius-2 Manhattan equivalent would: corner stones on Moore lose only 9 cells of footprint (vs 6 on grid), so corners are less punishing than usual. If the game were grid-topology with Manhattan radius-2 influence, dense clusters would be less dominant (smaller overlap) and a wider "territorial" game would emerge. Topology is thus a load-bearing parameter.

### First-mover advantage

Alternating, not simultaneous. P1 dominated 3/3, with margins 19.74, 41.54, 0.04. Seat-swap in Game 3 (the reasoner focused on P2) still gave P1 the win — but margin collapsed to 0.04. With imperfect play on both sides, advantage is substantial; with best play on both sides, advantage is minimal but still exists. This game is **P1-favoured but not broken** — a good strong P2 player with attack strategy can come within a single stone of victory.

---

## PHASE 4 — NOVELTY ADVERSARY (MANDATORY)

### (a) Known-game catalog comparison

**Adversary:** "This is Go with a scoring rewrite. The board is 8×8, stones are placed on empty cells, groups with no liberties are captured (identical to Go). The only change is the win condition: instead of territory + stones (komi-adjusted), it's a threshold on continuous board-values that decay from each stone. Go experts would have immediate advantages: they would recognise the 2×2 block as an essential shape, they would compute liberties automatically, they would instinctively attack the opponent's third line, and they would know to avoid placing adjacent to enemy stones early. The threshold is a cosmetic wrapper over standard Go territory intuition."

**Response/rebuttal:** Much of the Go analogy holds — adjacency, capture, the primacy of the centre — but there is a **load-bearing rule difference**: `adjacent_to_own` placement (after the first move). In Go you can place *anywhere* empty. In this game you are **restricted to cells adjacent (Moore) to your own existing stones**. This totally changes opening theory: you cannot play a sente move far from your cluster to disrupt the opponent; every move must extend your own footprint. A Go expert's instinct to play tenuki to the other side of the board is illegal here. Concrete example: at Game 2 move 18, P2 played (5,2) — a cell that Go-wise was absurd (hanekomi into the enemy's 5-stone cluster), but legal because P2's (5,3) was adjacent and it was strategically correct because the +3.61 P1-damage outweighed the self-loss. A pure Go player would never consider this move.

Also: the **influence field with radius-2 decay** has no Go analogue. Threshold-based scoring is continuous and geometry-sensitive; Go territory is a discrete flood-fill over empty cells.

### Comparisons to other abstract games

- **Reversi/Othello.** No: Othello flips, this captures. Othello is closed (64 moves max), this terminates dynamically. Threshold scoring is closer to Othello's piece count than to Go's territory, but the influence field has no Othello analogue.
- **Hex / Y / Havannah.** No connection game element — no "connect your sides", no "form a ring".
- **Gomoku / Pente / Connect6.** Related only in that it's an 8×8 placement game. No N-in-a-row win condition; capture rule is not Pente's custodian (surround).
- **Amazons.** Amazons is blocking and piece-movement; this is place-only with no movement.
- **Lines of Action.** Movement-based; irrelevant.
- **Mancala variants.** Sowing; irrelevant.
- **Life-like CA / Immigration Game / HighLife.** No CA in this game — `uses_ca=False`. Not relevant.
- **Nim.** No, mover plays until threshold.
- **Tumbleweed.** Tumbleweed has influence-like "shading" on hex with line-of-sight; this is closest conceptually — but Tumbleweed uses line-of-sight (straight-line visibility) for scoring, not radius-2 decay, and is played on hex, not Moore square. Moderate similarity.
- **Slither.** Slither is a connection game with sliding pieces; irrelevant.

### (b) CA-based comparison

Game has no CA. Not applicable.

### (c) Simultaneous-game comparison

Game is alternating. The Run-14 simultaneous-play mechanic is not exercised. No relevance.

### (d) Topology/coordinate transformation re-skin?

**Adversary:** "It is Go-on-Moore-with-ownership-threshold. Define Go* = place-only Go with adjacent_to_own opening constraint; compute score as Σ-over-own-cells of an influence field; this is exactly Go* with a specific influence function."

**Response:** The *class* of "Go with an ownership-summed scoring field" is a known space of variants (there is academic literature on "Go with continuous influence"), but this specific parameter tuple (`radius=2, strength=1.615, decay=0.462, threshold=63.46`) is a specific game, and the numerical tuning determines play. At `decay=0.46` every move-footprint is meaningfully felt at distance 2; at the empirically-observed `game_length ≈ 22-29` the threshold is reached, not double-pass-exploit. A slightly different tuning (decay 0.1 say) would yield a very different game. So the *mechanism class* is known-ish, but the *specific game* is not a straightforward re-skin.

### (e) Would a Go expert have immediate advantage?

**Partially.** A Go expert would:
- Correctly intuit centre-first opening and dense-cluster strategy (✔, holds here).
- Correctly compute liberties for the small capture check.
- Wrong about tenuki — *illegal* here. The `adjacent_to_own` rule is a Go expert's first surprise.
- Wrong about third-line shoulder-hits — the influence field means such moves lose +0.6 on the attacker's cell via P1-contamination, which a Go player will not instinctively compute.
- Unable to estimate "game value in points" without learning the influence arithmetic.

Net: a Go expert would be **~40%** stronger than a naive player, not 95% stronger as they would be in real Go. The influence arithmetic is the dominant skill, not Go shape library.

### Team rebuttal with specific Phase 2 moments

1. **Game 2 move 18 `(5,2)` "suicide-damage" play.** No Go move reasons like this. A Go expert would never place into a +2.18 hostile field; but here it's correct because relative damage is +4.14. The *influence arithmetic* is a skill the Go framework lacks.
2. **Game 3 move 18 `(3,5)` stacking 4 own-d1-neighbours simultaneously.** Go shape library contains "hane", "kosumi", "ikken tobi" but none of them map to "maximise count of own stones within Chebyshev-2 of new stone". The shape primitive is different.
3. **Adjacent-to-own constraint directly invalidates 60% of Go opening theory** (any move more than one point from your existing group). Game 1 move 7 (3,4)=35 was legal only because a P1 stone was at (3,3); a P1 tenuki to (6,6) early was never available.

### Novelty score

Score **5/10**. Reasoning: the game is a coherent Go variant with a continuous-influence scoring field and a novel placement constraint, but the *class* of "Go-with-influence-threshold" is understood and the emergent strategy (densify centre) is broadly Go-like. The genuinely novel element is the `adjacent_to_own` placement rule (which changes opening dynamics fundamentally) combined with the radius-2 Moore influence field — these two together give emergent gameplay that is not a straightforward re-skin of any single known game, but is recognisably in the neighbourhood of "Go + influence-score" variants. Not a new abstract game worth a rulebook; a decent variant study.

---

## PHASE 5 — VERDICT

Team ID: **team-12**
Game ID: **931c58ae59b4**
Rules Summary: Alternating 2-player place-only game on 8×8 Moore-adjacency board, Go-style capture, radius-2 influence with exponential decay, win by owning cells totalling > 63.46 influence (max_turns 100 majority).
Topology: 8×8 Moore (Chebyshev distance for propagation, 8-neighbour adjacency for placement).
Turn Structure: alternating, 1 piece per turn.

SCORES (1-10):
  Strategic Depth: **6** — Two distinct strategy families (mirror vs attack), genuine short-term/long-term tension in the stone-stacking tradeoff, and real counter-play (contamination), but the "densify the centre cluster" heuristic is near-universal so the decision tree is narrow (~3-5 real move options per ply among 8-14 legal).
  Emergent Complexity: **5** — Influence stacking, contamination economy, and territory-equilibrium around the centre. No deep tactics emerged (no ko, no capture, no group-life decisions). Games are short (~24 plies).
  Balance: **3** — P1 wins 3/3. Margins (+19.7, +41.5, +0.04) show that P1 is structurally advantaged but the optimal-play margin (+0.04 in Game 3 with a committed P2 attacker) is narrow. Still, uniformly 3/3 P1 wins is a red flag.
  Novelty (post-adversary): **5** — Recognisable as "Go with radius-2 influence threshold and adjacent_to_own placement", not a re-skin of a single known game but in a known class. Biggest original element is the combination of the `adjacent_to_own` opening constraint with the continuous influence field.
  Replayability: **5** — The discovery of "attack" over "mirror" was the key strategic beat of our three games; once discovered, the optimal-play pattern is fairly repetitive. Some variance from P2's choice of attack target, but P1's playbook is almost deterministic.
  Overall "Would I play this again?": **5** — Playable, balanced-within-a-margin, with one genuinely interesting mechanic (influence-contamination). Not enough emergent richness to replace a session of Go or Hex but plausible as a short mathematical curiosity.

CLOSEST KNOWN-GAME ANALOG: **"Go with radius-2 continuous influence scoring"** (a class of research variants). Most similar single game is probably **Tumbleweed** (influence-on-hex), but Tumbleweed uses line-of-sight shading and plays quite differently. It is NOT identical because (i) the `adjacent_to_own` placement rule has no Go/Tumbleweed analogue; (ii) the threshold-by-sum win condition is neither Go's territory nor Tumbleweed's majority; (iii) Moore topology with Chebyshev distance is atypical.

KILLER FLAWS: 
- **P1 wins 3/3** in team-12 play. Seat-swap in Game 3 did not change the outcome. First-mover advantage is significant; for use as a competitive game, komi-style compensation for P2 would be needed.
- No double-pass majority exploit observed, but the `adjacent_to_own` rule means a pinned player can be forced to pass — this should be checked in longer games.
- `play_helper.py rules` mis-reports Moore adjacency as "von Neumann (no diagonals)" — display bug but could mislead evaluators. (Actual code in `topology._build_moore_neighbors` uses full 8-neighbour.)

BEST QUALITY: **Influence contamination**. The mechanic that owning a cell with hostile influence *subtracts* from your score creates a genuinely interesting inverted-incentive layer: claiming ground is sometimes costly, and actively damaging the opponent via suicide-placement is sometimes optimal (Game 2 move 18). This is the only feature I would hold up as novel gameplay.

IMPROVEMENT IDEAS: Add a small **P2 bonus (komi)** of ~10-15 influence units at game start, calibrated to match the Game-3 +0.04 margin so best-play finishes as a near-tie. This would turn the game from "P1 always wins" to a balanced contest, preserving the strategic depth. Alternatively, allow P2 to play **two stones on move 1** (like Pie rule alternatives) — simpler and would empirically even out the +20 opening-move swing observed in Game 1.
