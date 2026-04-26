# Team-4 Evaluation — Game `deb4dfe0382d` (Run 14 Champion)

**Team ID:** team-4
**Game ID:** deb4dfe0382d
**Run:** 14
**GE score (DB):** 0.5174 (rank #1)
**Evaluator role separation:** All three roles (P1, P2, Novelty Adversary) were played by a single agent in sequence. Residual seat-identity bias is acknowledged; seat-swap in Game 3 helps but does not eliminate it.

---

## PHASE 1 — RULE COMPREHENSION

### Board & topology
- **Dimensions:** 2D, axis size 8 (so 64 cells).
- **Topology:** `torus` (von Neumann adjacency with wraparound on both axes).
- **Action space:** 65 (actions 0–63 place at cell `y*8 + x`; action 64 is **pass**).

### Turn structure
- **Alternating** (`turn_type: alternating`, `pieces_per_turn: 1`). Not simultaneous.
- P1 moves first; P2 responds.

### Action types
- Place only (no movement). Placement target is empty cells, `anywhere`, `first_move_anywhere: true`.

### Capture: custodian, threshold 1
- Othello-style: after a placement at cell C, walk along each axis (±x, ±y). Collect consecutive enemy cells until you either hit a friendly cell (→ flip the run) or an empty cell / board edge (→ no capture).
- **Key engine quirk:** custodian walks **do NOT wrap** on the torus (engine loop `while 0 <= pos < axis_size`). Influence propagation, in contrast, **does** wrap — this asymmetry is real and strategically meaningful.

### Propagation: influence (radius 1)
- Strength = 1.8741653769745463
- Decay = 0.40188260272471954
- After a placement, add `±strength * decay^distance` to every cell within radius 1 (so the placed cell itself gets `±1.874` and each of its 4 VN neighbors gets `±0.753`). Sign is + for P1, − for P2.
- Values are **cumulative and permanent** — a captured P2 piece leaves its `-1.874` contamination on the cell and `-0.753` on neighboring cells, which persists even after ownership flips. This is the most strategically-interesting engine detail.

### Win condition
- `condition_type: threshold`, threshold = 38.61643, target_dimension 0 (P1 wants positive total), max_turns = 102.
- Engine formula: P1 wins if `Σ board_values[c] for c where owner[c] == 1 > 38.616`. P2 wins with the negated sum (Σ of negated values on P2 cells) > 38.616.

### Cellular Automaton
- None. Classic mechanics (`uses_ca = False`).

### Degenerate-rule check
- **Threshold reachable?** Yes. A 4×3 rectangle (12 pieces, 17 edges) scores 48.1; an 11-piece cluster with E=15 scores 43.2; an 11-piece cluster with E=14 scores 41.7. The minimum piece count to exceed threshold is **11 pieces** (a 3×3 block plus 2 pieces that together add 3 new edges). A 3×3 (9 pieces, 12 edges) gives 34.94 — just short; adding a 10th 1-friendly extension reaches **exactly 38.325**, still short of 38.616 (i.e. "10 pieces is never enough by a hair"). The threshold is tuned tightly, which is strategically interesting.
- **Value formula:** I confirmed empirically that total value on own cells = `1.874 * N + 1.506 * E` where N = piece count and E = friendly-adjacent edges. So maximizing edges per piece is the dominant strategic imperative.
- **Pass exploit (double-pass majority):** If both players pass consecutively, the game resolves by majority piece count. In the three games I played, this never fired — P1 is so far ahead in piece count that P2 passing would lose by majority. Pass is effectively useless for P2 in this game.
- **Custodian works?** Yes, fires reliably on row/column intrusions, but never wraps around the torus axis.

**No degenerate mechanics found.** All rules are active.

---

## PHASE 2 — STRATEGIC PLAY

All moves engine-verified with `play_helper.py --action play --moves "..."`. A helper `team4_play.py` was written to also show `board_values` and P1/P2 effective totals each turn.

### Game 1 — both sides play symmetric "compact cluster" strategy

**Moves (action ids):** `27,63,28,62,35,55,36,54,19,47,20,53,26,46,18,45,34,61,29,21,37`

| Turn | Player | Action | Cell | P1 val | P2 val | Notes |
|------|--------|--------|------|--------|--------|-------|
| 1 | P1 | 27 | (3,3) | 1.87 | 0.00 | Central opener |
| 2 | P2 | 63 | (7,7) | 1.87 | 1.87 | Far corner, opposite torus cluster |
| 3 | P1 | 28 | (4,3) | 5.26 | 1.87 | Extend cluster |
| 4 | P2 | 62 | (6,7) | 5.26 | 5.26 | Mirror extension |
| 5 | P1 | 35 | (3,4) | 8.64 | 5.26 | Build L |
| 6 | P2 | 55 | (7,6) | 8.64 | 8.64 | Mirror |
| 7 | P1 | 36 | (4,4) | 13.52 | 8.64 | Close 2x2 |
| 8 | P2 | 54 | (6,6) | 13.52 | 13.52 | Mirror |
| 9 | P1 | 19 | (3,2) | 16.90 | 13.52 | Extend up |
| 10 | P2 | 47 | (7,5) | 16.90 | 16.90 | Mirror |
| 11 | P1 | 20 | (4,2) | 21.79 | 16.90 | 2-friendly placement |
| 12 | P2 | 53 | (5,6) | 21.79 | 20.28 | Extend |
| 13 | P1 | 26 | (2,3) | 25.17 | 20.28 | 1-friendly |
| 14 | P2 | 46 | (6,5) | 25.17 | 25.17 | 2-friendly (tied) |
| 15 | P1 | 18 | (2,2) | 30.06 | 25.17 | 2-friendly |
| 16 | P2 | 45 | (5,5) | 30.06 | 30.06 | 2-friendly |
| 17 | P1 | 34 | (2,4) | 34.94 | 30.06 | 2-friendly → 3×3 done |
| 18 | P2 | 61 | (5,7) | 34.94 | 34.94 | 2-friendly (tied again) |
| 19 | P1 | 29 | (5,3) | 35.31 | 35.31 | Begin 11-piece extension |
| 20 | P2 | 21 | (5,2) | 35.31 | 35.31 | Block P1's next 2-friendly cell (best defense) |
| 21 | P1 | 37 | (5,4) | **40.95** | 34.56 | 11th piece, 2 friendlies → **WIN** |

**Result:** P1 wins at move 21, value 40.95 vs threshold 38.616.

Notable: P2's block on move 20 was the correct defensive play (blocking the 2-friendly (5,2) cell) but P1 simply switched to (5,4), which was also 2-friendly and not contaminated.

### Game 2 — P2 tries sacrifice-and-build hybrid

**Moves:** `27,28,29,54,19,55,26,62,18,63,34,61,20,46,21,47,35,53,36,45,37,44,52,60,43`

Strategy: P2 opens with an adjacent sacrifice at (4,3), knowing P1 will custodian-capture it at (5,3), then switches to building a compact 3×3 in the corner. Mid-game, P2 sacrifices again at (4,5) to contaminate P1's expansion.

| Turn | Player | Action | Highlight |
|------|--------|--------|-----------|
| 2 | P2 | 28=(4,3) | **Sacrifice adjacent to P1** |
| 3 | P1 | 29=(5,3) | **Custodian capture** of (4,3) — row 3 scans (5,3)X,(4,3)O,(3,3)X → flip |
| 4 | P2 | 54=(6,6) | Pivot to building own cluster |
| 5-18 | — | both build | P2 reaches value parity at key milestones despite piece deficit |
| 20 | P2 | 45=(5,5) | Completes 3×3 for P2 at value 34.94 (same as P1 after move 17) |
| 21 | P1 | 37=(5,4) | P1 reaches 37.57 — just short of threshold |
| 22 | P2 | 44=(4,5) | **Second sacrifice** adjacent to P1's (4,4) and (5,4) |
| 23 | P1 | 52=(4,6) | Custodian capture of (4,5) — but net 0 value gain for P1 |
| 24 | P2 | 60=(4,7) | Build adjacent to (5,7)O — value 36.82 |
| 25 | P1 | 43=(3,5) | 2-friendly (adj to (3,4)X, (4,5)X-captured) — **value 38.69, WIN** |

**Result:** P1 wins at move 25, value 38.69 vs threshold 38.616.

The P2 sacrifice strategy cost P2 2 pieces and 2 tempos, but delayed P1's win from move 21 to move 25 and reduced P1's winning value from 40.95 to 38.69. At the winning moment, P2 was at 36.82 — so P2's sacrifice strategy brought P2 *closer* to winning than in Game 1 (34.56), but still clearly behind.

**Key finding:** P2's sacrifice is net-negative because of an elegant engine detail: when P2 plays adjacent to P1's cluster and is custodian-captured, the captured cell retains its negative board_value (≈ −0.37 after partial re-dressing by P1's bracketing piece). P1 gains 2 pieces but the cluster carries a "dead weight" cell worth −0.37. Over many sacrifices, this damage is real — but not enough to overcome the tempo loss.

### Game 3 — seat swap; P2 plays 1 surgical sacrifice then builds

**Moves:** `27,63,28,35,43,54,36,62,44,55,42,47,34,46,26,45,18,53,19,37,20,61,25`

Note on seat-swap bias: I played "P1 as P1" in games 1-2 and "P2 as the more interesting side to analyze" in game 3 by giving P2 the sacrifice-then-build strategy from the start, while P1 played straight optimal building. Since the same agent handles both seats, this swap does NOT eliminate my own evaluator bias — but it does re-test whether the sacrifice-first P2 strategy (which partially worked in Game 2) can overcome P1's advantage when both sides play optimally.

| Turn | Player | Action | Key moment |
|------|--------|--------|-----------|
| 4 | P2 | 35=(3,4) | Early sacrifice |
| 5 | P1 | 43=(3,5) | Custodian capture |
| 6 | P2 | 54=(6,6) | Pivot to building |
| 7-20 | — | both build compactly | Both reach 31.93 at move 20 |
| 21 | P1 | 20=(4,2) | 2-friendly, P1 → 36.80 |
| 22 | P2 | 61=(5,7) | 2-friendly, P2 → 36.82 |
| 23 | P1 | 25=(1,3) | 1-friendly clean cell, P1 → **40.20, WIN** |

**Result:** P1 wins at move 23, value 40.20 vs threshold 38.616. P2 final value: 36.82.

### Endgame summary (double-pass / max_turns check)
- Game 1: threshold at move 21 ✅
- Game 2: threshold at move 25 ✅
- Game 3: threshold at move 23 ✅

**None of the 3 games resolved by double-pass, and none hit max_turns.** Pass was never played. No Run-13-style exploit appeared.

### Player reflections

**P1 strategy guide (the winning side):**
1. Open centrally and begin a compact 2×2, then expand to 3×3 — the value formula `1.874N + 1.506E` rewards edge density, not piece count.
2. Each turn, prioritize placements with the maximum number of friendly VN neighbors. Early game this is 1 per move, later you can often find cells with 2 friendly neighbors (they add +4.89 vs +3.38).
3. Respond to adjacent P2 intrusions with custodian captures only when the captured cell's net value is positive — often it isn't, and you should instead expand in a fresh direction to avoid reinforcing contamination.
4. P1's single biggest edge is pure tempo: with alternating turns and piece-per-turn placement, P1 will always have one more piece than P2 after P1's turn.
5. Target an 11-piece cluster with E ≥ 14 — the minimum winning configuration. If you can complete it by move 21–23, you win.

**P2 strategy guide (the losing side):**
1. Symmetric mirror-building leads to a tied value race where P1 wins by tempo every time — so you need something more.
2. Adjacent sacrifices: place next to a P1 piece, get custodian-captured next turn. The captured cell retains negative influence (−0.37 ownership + −0.75 to each pre-existing P1 neighbor). Damage per sacrifice is ≈ −1.1 to P1's future ceiling.
3. But sacrifice costs you 1 piece + 1 tempo; P1 gets 1 extra piece for free. Net value exchange is slightly P1-positive. Sacrifice works only as a delaying tactic, not a winning one.
4. Best-effort P2 line: 1–2 surgical sacrifices during middle-game (when P1's cluster is 5–7 pieces) to contaminate a single key "2-friendly" cell P1 would otherwise use to reach threshold efficiently. This pushes P1's win from move 21 to move 23–25.
5. Torus symmetry means the far corner and center are equivalent — don't waste tempo searching for a "better" starting position.

### Opponent surprise / would-do-differently
- **Did P2 surprise P1?** Partially. In Game 2, P2's sacrifice+capture forced P1's (4,3) cell to be permanently contaminated — when P1 later expanded to (4,2) and (4,4), the gain was 3.37 instead of the expected 4.89. I did not fully appreciate the magnitude of cumulative contamination until computing it out.
- **Did P1 surprise P2?** No. P1's core strategy (build compact 3×3, extend to 11 pieces) was obvious from Phase 1 analysis.
- **What would I do differently as P2?** Try simultaneous 2-sided intrusions: place P2 pieces on opposite ends of P1's emerging cluster so that P1 must capture one at a time, leaving permanent contamination and forcing P1 to burn tempo. This is limited by the alternating structure but theoretically the best P2 strategy.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint P1/P2)

### Are there distinct viable strategies?
Two approaches are viable for P1:
- **Compact builder (dominant):** Build a 3×3 block, extend by 2–3 pieces, reach threshold at move 21–23. Wins in all 3 games.
- **Territorial expander (weak):** Spread pieces in a less-compact shape. Doesn't reach threshold in time.

For P2, the strategies are:
- **Symmetric mirror builder:** Fails by tempo.
- **All-sacrifice:** Fails by losing all pieces (P1 wins via majority at max_turns, never threshold).
- **Hybrid (1–2 sacrifices + build):** Best for P2 — delays P1 win but does not reverse it.

**One approach dominates (compact building with tempo advantage).** P2 has no winning strategy against optimal P1 play.

### Counterplay
Limited. P2 cannot bracket any P1 piece in a single move (requires 2 pieces on opposite sides, which P1 will prevent by capturing the first). Custodian capture is essentially a one-way weapon: P1 can use it freely against P2 intrusions, but P2 cannot set up brackets against P1.

### Short-term vs long-term tension
Present. The sacrifice strategy illustrates this clearly: each P2 sacrifice is immediately bad (lose a piece) but deposits permanent negative influence on P1's cluster that matters 5–10 moves later. In Game 2, P1 won at a value of 38.69 — if P2 had done one more sacrifice contaminating (5,4) pre-emptively, P1's winning move might have failed.

### Emergent concepts
- **Contamination as strategic currency:** Negative board_values from P2 placements persist through capture; P2 can spend pieces to buy permanent damage.
- **Edge density:** The value formula `1.874N + 1.506E` makes edges the dominant currency. A 3×3 block (12 edges) is strictly better than a 9-piece "+" shape (8 edges).
- **Tempo:** As in Go, the first-move advantage compounds through a piece-count edge.
- **Custodian ratchet:** P1's compact cluster is self-reinforcing — every P2 adjacent intrusion becomes a bracket target, growing P1's piece count by 2 while P1 spends only 1 turn.

### Does topology matter?
Somewhat. The torus removes edge/corner asymmetries for placement, but custodian capture still stops at the hard axis boundary. This creates a subtle mismatch: influence propagation is topology-aware (wraps), but capture is not. In practice this was not decisive in my 3 games — both players built inside a single 3×3 region without using wrap for either influence or capture.

### First-mover advantage
**Extreme P1 dominance:** 3/3 games won by P1. Value differential at game end: P1 40.95 vs P2 34.56 (Game 1), P1 38.69 vs P2 36.82 (Game 2), P1 40.20 vs P2 36.82 (Game 3). Even with seat swap in Game 3 and maximal P2 effort, P1 still won by 3.4 value points.

**The "simultaneous play" framing of Run 14 does NOT apply here** — this game has `turn_type: alternating`. The entire P1-advantage pattern from Runs 11–13 persists.

---

## PHASE 4 — NOVELTY ADVERSARY

### (a) Known-game comparison

**Reversi/Othello:** Strongest direct analog. Custodian capture is Othello's *defining* mechanic, ported here with two twists: (i) the board is a torus (not an 8×8 grid with hard edges), and (ii) the win condition is threshold-on-influence, not majority-at-end. Strategy would look very familiar to an Othello player (wedge placements, parity, mobility).

**Go:** The "influence" score is reminiscent of Go territory, but radius-1 decay-0.4 spreading is NOT how Go territory works. In Go, territory is counted only in fully-enclosed empty regions; here, influence is a scalar field that radiates from every stone regardless of enclosure. An expert Go player would be misled by the "influence = territory" analogy.

**Hex, Y, Havannah, Connect6:** Not applicable — no connection-win condition here.

**Gomoku, Pente:** Not applicable — no line-of-5 win.

**Amazons, Chameleon:** Not applicable — no movement.

**Lines of Action:** Not applicable — no movement.

**Tumbleweed:** Partial analog. Tumbleweed has radiating influence (line-of-sight sum) and placement based on influence ≥ enemy's. Our game's influence is distance-decayed, radius 1 only, and the win condition is sum-threshold not contested-placement. The *flavor* is similar but the mechanics are distinct.

**Slither:** Not applicable.

**Life-like CA / Day & Night / HighLife / Immigration:** Not applicable — no CA in this game.

**Diplomacy / Blotto / Gungo (simultaneous games):** Not applicable — alternating turns.

### (b) CA literature check
Not applicable — `uses_ca: false`.

### (c) Simultaneous-game comparison
Not applicable — alternating turns.

### (d) Re-skin argument

The adversary's strongest case: **this is essentially Reversi on a torus with an influence-threshold win condition replacing majority.** The transformation:
- Same capture rule (custodian along axes).
- Same first-move-anywhere rule.
- Replace 8×8 grid with 8×8 torus.
- Replace "who has more pieces at end" with "who first exceeds a cumulative influence threshold".
- Add radius-1 influence propagation with decay 0.40.

A reasonable player familiar with Reversi would recognize 80% of the strategic landscape: mobility, wedge tactics, custodian capture, corner control (modulated here by torus symmetry — no real corners).

### (e) Expert-advantage test
**Would an Othello expert dominate here?** Partially yes for the capture game, but they would need to rediscover:
- The `1.874N + 1.506E` value formula (not present in Othello).
- The contamination-persistence phenomenon (not present in Othello — there's no "influence" that persists after flip).
- The "minimum 11 pieces to win" threshold calculus.
- The irrelevance of traditional Othello corner strategy (torus has no corners).
- The irrelevance of end-game parity (this game is a build race, not an end-game majority count).

An Othello expert's intuition would be useful for the first 10 moves but would mislead them about the crucial middle-game: in Othello, you *want* to control the board's edges; in this game, compact clusters win and edges are irrelevant.

### Rebuttal (P1 + P2 joint)

**Specific Phase 2 moments that break the Othello analogy:**

1. **Game 1, move 11:** P1 played (4,2) and gained 4.89 value because (4,2) was adjacent to two existing P1 pieces. In Othello, (4,2) would gain either 0 or 1 captures — no continuous gradient. The value-accumulation mechanic creates a "mass times topology" optimization problem that Othello does not have.

2. **Game 2, move 23:** P1 custodian-captured P2's sacrifice at (4,5). In Othello, this capture is uniformly good (you gain pieces and the opponent loses them). Here, the net change in P1's threshold-total was approximately *zero* — because the flipped cell retained its negative influence value. An Othello expert's instinct to "always capture" is actively wrong here.

3. **Game 3, move 23:** P1 won by playing a 1-friendly clean cell at (1,3), NOT by capture, NOT by extending the 3×3 further. The winning move was chosen based on "add a piece to a value-zero cell to get +3.38" — a purely influence-threshold calculation with no Othello analog.

4. **Contamination as persistent cost (entire Game 2):** P2's sacrifices left the (4,3) cell at value −0.37 even after P1 owned it. P1's subsequent expansion at (4,2) gained only 3.37 instead of the "clean" 4.89 — a 1.5-point penalty that an Othello player would not even see (there are no hidden cell values in Othello).

5. **Threshold calculus and minimum-piece count:** The existence of a precise "11 pieces minimum for P1" game-theoretic pivot is a property of the continuous value function, not of any piece-counting game. Games 1, 2, 3 all ended at moves 21, 25, 23 respectively — with P1's winning value in the range 38.7–40.9 and P2's losing value in 34.6–36.8. This narrow corridor is characteristic of a threshold game, not Othello.

6. **Torus influence wrap without capture wrap:** This asymmetry is a novel engine quirk. Influence propagation wraps (a piece at (0,0) contributes to (7,0) via the x-wrap at distance 1) but custodian capture does not. No known abstract-strategy game has this split.

### Novelty score (joint): **5**

**Why 5 and not higher:** The game is essentially "Reversi + influence field + threshold win + torus". Each of those ingredients is individually known (Reversi custodian, Tumbleweed-like influence, threshold wins appear in games like Blokus Trigon via score cutoffs, torus boards appear in Go variants). The combination is novel, but a strategic player can map 60–70% of play patterns onto Othello/Tumbleweed intuition.

**Why 5 and not lower:** The continuous influence field + threshold win condition genuinely changes the strategic calculus — contamination-persistence, minimum-piece calculus, and the `1.874N + 1.506E` edge-density formula have no direct Othello analog. The custodian/influence asymmetry on the torus is a novel structural detail. The "sacrifice cascade" strategy for P2 is non-trivial to analyze and has no direct Othello equivalent. Moves are engine-verified legal throughout; the game is a coherent whole.

---

## PHASE 5 — VERDICT

**Team ID:** team-4
**Game ID:** deb4dfe0382d
**Rules Summary:** 8×8 torus, alternating place-only, Othello-style custodian capture (threshold 1) with added influence-radius-1 field (strength 1.874, decay 0.402); first player to exceed influence sum of 38.616 on own cells wins, else majority at max_turns 102.
**Topology:** 2D torus, axis size 8 (64 cells).
**Turn Structure:** alternating (one placement per turn).

### SCORES (1–10)

- **Strategic Depth: 5** — There is a clear winning recipe (compact 3×3 + 2 extensions, 11 pieces, E ≥ 14) that an analyst can derive from the value formula in under an hour. The contamination/sacrifice subgame adds real depth (P2's optimal line matters), but once both sides know it, the game converges quickly. A self-play agent's learning curve in the DB (50%/50% final win-rate at 347K steps seed 80066, and 50/50 at 374K seed 81066) is consistent with a first-player-dominated game in which P1 always has a winning response.

- **Emergent Complexity: 6** — Influence contamination is a genuinely emergent concept: the continuous value field + custodian capture interact in ways that are not obvious from either rule alone (a P2 sacrifice leaves permanent damage proportional to the number of adjacent P1 pieces at the moment of placement). Edge-density optimization forces players to think about piece *shapes*, not just positions. However, the emergent layers are shallow — 2 or 3 concepts, not 5–10.

- **Balance: 2** — **Severely P1-favored.** 3/3 games won by P1 in 21, 25, and 23 moves. Winning-value differentials were 6.4, 1.9, and 3.4 — Game 2 was "close" only because P2 played sacrifice-disruption, but P2 still never threatened to win. Seat-swap in Game 3 did not change the outcome. The training runs in the DB show balanced 50/50 final win-rates, which might reflect a different equilibrium discovered by RL, but my tactical analysis shows no P2-winning path against optimal P1 play. The single piece-per-turn tempo advantage is decisive.

- **Novelty (post-adversary): 5** — Core mechanics (custodian + torus + influence field + threshold) are individually known. Combination is specific to this evolutionary run. Strongest adversary argument: "Reversi + Tumbleweed-like influence + threshold + torus re-skin." Strongest rebuttal: contamination-persistence and the continuous value function create strategic moments (ignore-capture-to-build-fresh, sacrifice-for-permanent-damage) that have no direct Othello/Tumbleweed analog.

- **Replayability: 4** — The dominant strategy (compact 3×3 builder) is findable in 1–2 games. Once both players know the winning recipe, games become formulaic and first-player wins. There is some tactical variance from sacrifice timing, but not enough to sustain repeated play. A self-play agent would quickly converge to short, tempo-optimized games (average game length 22.5 in seed 80066, 32.5 in seed 81066).

- **Overall "Would I play this again?": 3** — Interesting enough to play once or twice to explore the contamination mechanic. After that, it collapses to a solved opening/midgame.

### CLOSEST KNOWN-GAME ANALOG
**Reversi/Othello** on a torus, with a Tumbleweed-like influence field and threshold-win replacing the majority-at-end condition. Not identical: the continuous value function creates contamination-persistence and edge-density optimization, which Othello does not have.

### KILLER FLAWS
- **Severe first-mover advantage** (3/3 games won by P1). The alternating turn structure + placement-only + threshold-win makes this effectively a "whoever builds 11 compact pieces first" race, which P1 always wins. This is the same Run-11/12/13 pattern: alternating placement + threshold → P1 dominance.
- **No viable P2 winning strategy.** Every disruption P2 can attempt is net-negative in value terms because of the 1-move bracket-capture response.
- Double-pass exploit does NOT fire here (P2 is always behind in piece count, so passing loses by majority). This is a clean engine behavior — no exploit to flag — but it also means P2 has literally no tool against a competent P1.

### BEST QUALITY
**Contamination-persistence.** When P2 sacrifices adjacent to P1 and is custodian-captured, the captured cell retains ≈ −0.37 of its original negative influence, and surrounding P1 cells retain their −0.75 damage. This creates a genuine temporal-cost mechanic where past placements have permanent value consequences. It's the one mechanic of this game I'd genuinely want to see explored further in a better-balanced variant.

### IMPROVEMENT IDEAS
**Single rule change to add depth:** increase `pieces_per_turn` to 2 (double placement per turn). This would:
1. Let P2 set up 2-sided brackets (capture P1 pieces) in one turn, eliminating the one-way-capture dominance.
2. Reduce first-mover advantage (P1 still has the "first placement" but P2 can respond with 2 placements each turn).
3. Raise the effective threshold calculus — more pieces per turn means the game might need a different threshold to remain balanced.

Alternatively: **flip the win condition to `threshold_diff`** (P1 wins when P1_sum − P2_sum > threshold), which rewards contamination / disruption equally on both sides. Under current rules, contaminating P1 is useful only defensively; under a diff-threshold rule, it would also help P2 win directly.

---

**Evaluation complete. All three games engine-verified. No max_turns hits, no double-pass resolutions, no illegal moves attempted.**
