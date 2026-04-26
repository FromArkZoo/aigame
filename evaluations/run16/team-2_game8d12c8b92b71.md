# Run 16 Human Evaluation — team-2

**Game ID:** `8d12c8b92b71` (R16 Genesis Engine champion, GE 0.160)
**Team ID:** `team-2`
**Date:** 2026-04-22

---

## PHASE 1 — RULE COMPREHENSION

### Board structure
- 2D hex topology, axis size 8 → 64 cells.
- "Hex" topology in `topology.py` builds 6-neighbor axial-hex adjacency for interior cells (not the von Neumann that `play_helper.py rules` mislabels). Verified: cell (3,3)=27 has neighbors `[20, 19, 26, 28, 35, 36]`. Corner cells have 2 neighbors only (e.g. (0,0) → `[1, 8]`), edge cells have 3-4. So influence reach is asymmetric across the board: an interior cell touches 19 cells within radius 2 (1 + 6 + 12); a corner touches only 6 (1 + 2 + 3). This will matter.
- Action space: 65 actions = 64 placements (action `y*8+x`) + action 64 = pass.

### Turn structure
- **ALTERNATING** (turn_type: `alternating`, pieces_per_turn: 1). Used `play_helper.py`/`engine.step()`.
- No simultaneous resolution; the R16 margin-based threshold fix still applies if both players cross threshold on a single tick (post-propagation), but in alternating mode that effectively never happens because only one player moves per step.

### Action types & constraints
- `place` only. Target must be empty. `first_move_anywhere=True`. No swap rule, no first-move restriction. P1 may open at the geometric centre.
- Pass (action 64) is always legal. Two consecutive passes end the game **as a draw** (R13+ fix).

### Capture / CA dynamics
- `capture_type: none`. **No capture mechanic.** Stones placed are permanent.
- No cellular automaton (`Cellular Automaton: No (classic)` confirmed in inspect_game).

### Propagation
- `prop_type: influence`, `radius: 2`, `strength: 0.984`, `decay: 0.695`.
- Each placement adds to `board_values`: signed `+0.984·0.695^d` for P1, `−0.984·0.695^d` for P2 at every cell within hex-distance d ≤ 2 of the placed stone (d=0: ±0.984; d=1: ±0.684; d=2: ±0.475).
- A single interior stone seeds about +7.4 of total signed influence (1·0.98 + 6·0.68 + 12·0.47 = 7.74 ideally, less near edges).
- Influence accumulates linearly from every same-coloured stone. No decay over time. No cleanup on capture (since none).

### Win condition
- `condition_type: threshold`, `threshold: 34.129…`, `target_dimension: 0`, `max_turns: 100`.
- The relevant code path (`engine_v2._check_threshold`) sums `board_values[c]` over cells where `board_owners[c] == player` (P2's signed values are negated). A player wins when this **own-cell signed influence** exceeds 34.13. The R16 margin fix matters only on simultaneous crossings, which alternating play essentially eliminates.
- Max 100 turns; if exhausted, majority piece count wins (`_end_by_max_turns`).

### Degeneracy flags
- **No degenerate single-action win.** Reaching the threshold requires sustained cluster building.
- The threshold (34.13) is reachable but tight — equals roughly the influence sum of an 8-9-stone cluster on connected interior cells. In Phase 2 testing P1 reached threshold around turn 13-17 with a tight central cluster.
- **Pass is always legal but useless**: passing wastes a turn, and the leading player can always force the trailing player into a worse position by continuing to place. No `pass` strategy emerged. The double-pass-draw escape hatch never fires under sane play.
- **Threshold reachability is not symmetric**: a player who builds a tight 8-stone hex cluster around an interior cell can hit ~37 effective; the same stones split or near edges may only hit ~22. A 100-turn timeout outcome is plausible only if both players actively interfere.
- **No CA rules to be inert** (none exist). No torus + connection wrap-win risk (hex topology, no connection win).

---

## PHASE 2 — STRATEGIC PLAY

All moves engine-verified by stepping the actual `GameEngineV2`. `board_values` and effective P1/P2 scores tracked after every move. Each game logged below.

### Game 1 — P1 cluster vs P2 mirror cluster

**Setup:** P1 plays from a central seed and grows outward. P2 mirrors symmetrically (also clustering, not interfering).

**Move log (action, cell):**

| Step | Player | Move | Cell | P1 eff | P2 eff |
|------|--------|------|------|--------|--------|
| 1 | P1 | 27 | (3,3) | 0.98 | 0.00 |
| 2 | P2 | 36 | (4,4) | 0.30 | 0.30 |
| 3 | P1 | 35 | (3,4) | 1.97 | -0.38 |
| 4 | P2 | 28 | (4,3) | 0.81 | 0.81 |
| 5 | P1 | 26 | (2,3) | 3.58 | -0.14 |
| 6 | P2 | 37 | (5,4) | 2.63 | 2.63 |
| 7 | P1 | 34 | (2,4) | 6.82 | 2.15 |
| 8 | P2 | 29 | (5,3) | 6.35 | 6.35 |
| 9 | P1 | 19 | (3,2) | 11.02 | 5.40 |
| 10 | P2 | 44 | (4,5) | 10.07 | 10.07 |
| 11 | P1 | 18 | (2,2) | 16.64 | 10.07 |
| 12 | P2 | 45 | (5,5) | 16.64 | 16.64 |
| 13 | P1 | 25 | (1,3) | 24.57 | 16.64 |
| 14 | P2 | 38 | (6,4) | 24.57 | 24.57 |
| 15 | P1 | 17 | (1,2) | 31.14 | 24.57 |
| 16 | P2 | 30 | (6,3) | 31.14 | 31.14 |
| 17 | P1 | 10 | (2,1) | **38.66** | 31.14 | → **P1 wins** |

**Reasoning by player:**

- **P1 (every odd move)**: "I want to build a 3×3 hex hex-cluster around the centre. Each new piece adjacent to two existing pieces gets +0.98 self + a slug of +0.68 from each neighbour reinforcement. With perfect mirroring, P2 reaches my score one move late — i.e. on every even step."
- **P2 (every even move)**: "Symmetric mirror is the safe play that maximizes my own influence growth, but it concedes tempo. After step 16 we're tied at 31.14. Step 17 will push P1 over."

**Reflections (Game 1):**
- P1: "Mirror cluster is a fatal P2 trap — by construction, P1 hits any threshold one move ahead. Strategy was just 'extend cluster radially'; there is no hard tactical decision."
- P2: "I never had a chance with mirror. In the rematch I should disrupt rather than parallel-build. Did opponent surprise me? No — the game is fully deterministic given strategy."
- Endgame: reached threshold cleanly (38.66 > 34.13). No double-pass, no timeout.

---

### Game 2 — P1 cluster vs P2 interference

**Setup:** Same P1 cluster strategy. P2 places **adjacent to or on top-of** P1's intended cluster cells, stealing ownership of cells with high P1 influence.

**Highlights of move log (key positions):**

| Step | Player | Cell | P1 eff | P2 eff | Note |
|------|--------|------|--------|--------|------|
| 1 | P1 | (3,3) | 0.98 | 0.00 | centre seed |
| 2 | P2 | (2,3) | 0.30 | 0.30 | adj P1, steals neighbour |
| 3 | P1 | (4,3) | 2.18 | -0.17 | extends right |
| 4 | P2 | (5,3) | 1.02 | -0.35 | further interference |
| 5 | P1 | (3,4) | 3.64 | -1.03 | |
| 6 | P2 | (3,2) | 2.00 | -0.31 | sandwiches P1 |
| 7 | P1 | (2,4) | 4.15 | -1.47 | |
| 8 | P2 | (4,4) | 1.62 | -0.16 | steals P1's high-value cell |
| ... | ... | ... | ... | ... | both keep contesting centre |
| 26 | P2 | (3,1) | 13.78 | 6.95 | game still wide open |
| 27 | P1 | (4,7)·heuristic | 20.35 | 6.95 | |
| 28 | P2 | (1,1) | 20.35 | 14.46 | |
| ... | greedy phase | ... | ... | ... | |
| 31 | P1 | (2,6) | **34.97** | 20.50 | → **P1 wins** at step 31 |

**Reasoning:**
- **P1**: "Interference makes my cluster grow slower because P2's stones sit right on top of cells that would otherwise hold my +0.68/+0.47 contributions. I have to spread further to find clean territory."
- **P2 (interfering)**: "Each adjacent placement subtracts ~1.4 from P1's effective score relative to ceding the cell, and adds ~0.6-0.9 to mine. If I can keep the rate above 1.0/move, P1 cannot reach 34.13 in 17 moves."

**Reflections (Game 2):**
- P1: "Interference doubled the game length (17 → 31 moves). I had to abandon a perfect cluster and build a second pocket on the bottom. The win still came, but the margin was much tighter and required many more careful moves."
- P2: "Interference is the right idea but I was still 1 tempo behind. To actually win I'd need to pre-empt P1's next move, not chase. Need to play **proactive** rather than reactive interference."
- Endgame: threshold cleanly hit (34.97 > 34.13). Decisive.

---

### Game 3 — Seat swap: greedy-vs-greedy with self-max heuristic

**Setup:** Both sides use the same heuristic — score a candidate placement by the influence it adds to its own colour, considering the cells' current owners. We rotate the seat assignment of "the team" — now **team-2 plays from the P2 seat** while running an identical heuristic in seat 1.

**Move log (greedy vs greedy):**

```
step  1: P1 a=0   (0,0) corner
step  2: P2 a=3   (3,0)
step  3: P1 a=8   (0,1)
step  4: P2 a=4   (4,0)
step  5: P1 a=16  (0,2)
step  6: P2 a=11  (3,1)
step  7: P1 a=17  (1,2)
step  8: P2 a=12  (4,1)
step  9: P1 a=1   (1,0)
step 10: P2 a=5   (5,0)
step 11: P1 a=9   (1,1)
step 12: P2 a=20  (4,2)
step 13: P1 a=24  (0,3)
step 14: P2 a=13  (5,1)
step 15: P1 a=25  (1,3)  →  P1 effective 34.67  → P1 WINS
```

**Final**: P1 effective = 34.67, P2 effective = 29.05. P1 wins on **move 15**.

**Reflections (Game 3):**
- Seat-bias acknowledged: I (the team) played both seats with the same heuristic, but the simulator dispatches greedy to whichever colour is `current_player`. The heuristic is symmetric.
- The greedy heuristic finds corners — they have only 6 cells in radius-2 vs 19 for interior — so it is suboptimal. Yet **P1 still wins on move 15** because 8 corner-edge stones cluster perfectly along the top-left axis. Tempo of one move is a structural advantage no symmetric strategy escapes.
- No double-pass, no timeout. Threshold reached.

---

### Side experiments (60+ additional engine-verified trials)

Run beyond the three required games to test sensitivity:

| Configuration | Outcome |
|---|---|
| P1 corner-cluster vs P2 centre-cluster | P1 wins step 17, eff 37.7 vs 30.2 |
| P1 self-max vs P2 interfere (interfere weight ×1.5) | **P2 wins step 34**, eff 26.3 vs 34.2 |
| P1 interfere vs P2 self-max | **P1 wins step 31**, eff 35.9 vs 25.1 |
| Both interfere (×1.5) | Hits 100-turn cap, draw, scores -5.7 / 1.3 |
| Random vs Random (50 trials) | P1 = 16 wins, P2 = 12, **22 draws** (timeout) |
| Greedy vs Random (50 trials, P1 greedy) | P1 = 50, P2 = 0 |
| Greedy vs Random (50 trials, P2 greedy) | P1 = 0, P2 = 50 |

**Key takeaway:** strategy dominates seat. A greedy player annihilates a random player from either seat. Random vs Random is mildly P1-favoured but most games time out — the threshold is hard to reach without competent play, but trivially reachable with one. Mutual interference can drag the game to time-out draws, but a marginal asymmetry (one side switches to self-max) is decisive.

### Strategy guides

**P1 strategy guide:**
- Open in the geometric centre (3,3 or 4,4) for max radius-2 reach.
- Build a connected hex cluster: each new stone should be adjacent to ≥2 existing stones to compound the +0.68 accumulation on each.
- If P2 plays interference (cells adjacent to your cluster), pivot to the *opposite* edge of your cluster so the stone you place still has 6 high-value neighbours empty.
- Don't pass. Don't defend. Race to threshold; tempo wins.
- Approximate threshold-hit count: 9 well-placed interior stones (≈18 ply) without P2 interference; 12-14 stones with interference.

**P2 strategy guide:**
- Mirror is fatal — P1 wins by 1 ply.
- Best: **proactive interference + own cluster.** Place P2 stones on cells that P1 was about to use for cluster expansion. Each such stone subtracts ~1.4 from P1's potential gain (cell flips ownership and P1's contributed influence becomes a P2-own-cell value, summed with negative sign → big P2 gain).
- Build your own cluster near, but not inside, P1's. Use the row-2 / row-5 hex bands.
- If you can keep P1 below the threshold for 100 ply, the game ends in a piece-count majority — but you must not pass into a draw.
- Don't go too aggressive on interference (×1.5 weight in heuristic) — it can starve your own cluster and lead to mutual-stall timeout.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**Are there distinct viable strategies?**
Yes, qualitatively three: (a) self-max cluster, (b) mirror cluster, (c) interference. Mirror is a P2 trap. Self-max and interference are both viable; interference can flip the seat advantage in one-vs-passive matchups. So there's a small but real strategic phase space.

**Meaningful counter-play?**
Limited but present. A pure self-max player loses to an interferer — the interferer denies cells with already-deposited friendly influence. A pure interferer loses to a player who builds clusters far from the contested zone (the interferer's own influence accumulates slowly). The Nash-equilibrium feel is *"build a cluster but always be looking for the most damaging steal."*

**Short-term vs long-term tension?**
Modest. Each move is purely additive (no capture, no decay). The "long-term" horizon is just "which cells will I want to own in 15 ply?" — a one-step heuristic captures most of the value. There's no piece sacrifice, no ko fight, no positional bind that pays off three moves later.

**Emergent concepts?**
- **Tempo**: yes, ironclad. Each ply translates to ~1.6 effective for the moving player.
- **Territory**: weakly. Cells around your stones are de facto yours, but there's no border, no liberties, no contiguous-region concept.
- **Influence**: the explicit core mechanic.
- **Initiative**: yes — first-mover advantage is structural.
- **Ko / mutual annihilation**: none (no capture).
- **Sacrifice**: none.

**Topology importance?**
Hex matters: 6-neighbor adjacency (vs grid's 4) gives a denser, more connected cluster. Radius-2 reach on hex is 19 cells (vs 13 on grid). The asymmetry between interior (19) and corner (6) reach also makes opening choice non-trivial — corners are objectively worse than centre. Topology is part of the strategy, not skin-deep.

**First-mover advantage (alternating game):**
Confirmed strong. In every test where both sides played comparable strategies, P1 won. Random vs Random had P1=16 vs P2=12 with 22 draws (so P1 wins 32% vs P2 24% in completed games — not crushing because random play often times out). Greedy vs greedy with corner-bias: P1 wins move 15. Mirror cluster: P1 wins move 17. The only way P2 won in our experiments was when P1 was passive (self-max) and P2 was actively interfering — i.e. mismatched strategies. The R16 margin-based threshold fix doesn't help P2 here because alternating play essentially never produces simultaneous threshold crossings.

**Quantified seat-swap evidence:**
- Same heuristic both sides: P1 wins (Game 3, step 15).
- P1 mirror, P2 mirror: P1 wins (Game 1, step 17).
- P1 self-max, P2 interfere: P2 wins, step 34. (Strategy mismatch.)
- P1 interfere, P2 self-max: P1 wins, step 31. (Mirror condition reversed.)
- Random vs random over 50 trials: P1 32% wins, P2 24%, 44% draws.

This is **not a balanced game**. The R16 worst-of-three seat-balance probe should have caught this; if it scored well, that's a calibration concern.

---

## PHASE 4 — NOVELTY ADVERSARY (mandatory)

### Adversary's argument: this game is NOT novel

(a) **Catalogue comparison.**
- **Othello/Reversi**: also influence-driven, also threshold (majority). But Othello has flips (capture); this game does not. So not Othello.
- **Go**: territory + capture; this has neither. Not Go.
- **Hex/Y/Havannah**: connection wins; this is threshold. Not those.
- **Gomoku/Pente/Connect6**: line-of-N; this is influence-mass. Not those.
- **Reversi-with-radius**: closer. The "spread points around your stones, accumulate to threshold" pattern resembles Othello's flip-and-count if you squint, but Othello's influence is point-and-flip, not radial-decay.
- **Tumbleweed**: definitely the closest analogue. Tumbleweed is a 2-player connection-and-influence-accumulation game on a hex board, where each cell's owner is determined by line-of-sight stone counts from each player. **This game is Tumbleweed-lite** — same family (hex board, influence, threshold), but Tumbleweed uses *line-of-sight* rather than *radius-2 distance decay*, and Tumbleweed has stacking rather than threshold.
- **Slither**: not relevant.
- **Lines of Action / Amazons**: movement games, not placement-only. Not relevant.

(b) **CA literature**: irrelevant — no CA in this game.

(c) **Simultaneous catalogue**: irrelevant — alternating game.

(d) **Re-skin claim:** *"This is just Reversi/Othello on a hex board with a radius-2 influence kernel and threshold-counting instead of flip-counting."* That argument has bite: the **family** is the same (place stones, accumulate influence, threshold-style scoring). But the kernel is different (decaying gaussian-ish vs flip), and the absence of capture/flip changes the game-tree dramatically.

(e) **Expert transfer test:** A Tumbleweed player would feel instantly at home on this board. They would recognise:
   - Hex topology — same.
   - Open placement — same.
   - Influence accumulation — same family.
   - Threshold-style scoring — analogous to Tumbleweed's territory count.

But would they immediately know the *optimal openings*? No: Tumbleweed's line-of-sight changes the geometry of cluster expansion compared to radius-2 decay. They would be a strong novice but not a master.

### Novelty score deliberation

- Direct analogue: **Tumbleweed** family (placement + influence + hex). 
- Distinguishing features: (1) radius-2 gaussian-decay influence kernel rather than line-of-sight; (2) explicit numeric threshold (34.13) rather than territory count; (3) stones do not stack; (4) no defensive structure (no liberties, no capture).
- These are genuine but small differences. The strategic concepts (cluster, tempo, interference) are recognisable from Reversi-on-hex / Tumbleweed.

**Novelty score: 4/10.** "Influence game on hex with decaying kernel + threshold win" — has analogues in Tumbleweed and (loosely) hex Reversi variants. Not a re-skin (the radius-decay kernel and own-cell-only scoring change things) but no fundamentally new mechanic.

### Rebuttals from Phase 2 moments

- **Game 2, step 8** (P2 places (4,4) "stealing" a P1-influenced cell): the placement *converted* P1's deposited influence into a P2 own-cell value (effective swing of ~+1.4 P2). In Tumbleweed line-of-sight rules, you cannot place a stone that becomes more valuable because your opponent has stones near it — Tumbleweed's transfer rule depends on line-count, not radial deposit. So the "interference steal" tactic does not transfer directly.
- **Game 1, the symmetric mirror loss**: in Tumbleweed, the equivalent would be a literal mirror — but Tumbleweed has a swap rule (P2 may steal P1's first placement). This game has no swap, so mirror is fatal in a way it wouldn't be in Tumbleweed. That's a real (if unfortunate) distinguishing dynamic.
- **Random-play 22/50 draws (44%)**: in Tumbleweed, random play almost never deadlocks because line-of-sight pieces always shift ownership. Here, mutual interference can lock both players below threshold — a different drawing dynamic.

These three moments show the game does have small specific tactical wrinkles (steal-by-placement-on-deposit, no-swap fatal-mirror, interference-stall draw) that aren't a 1:1 with any catalogued game.

---

## PHASE 5 — VERDICT

**Team ID:** team-2
**Game ID:** 8d12c8b92b71
**Rules Summary:** Place stones alternately on a hex 8×8 board; each stone deposits radially decaying signed influence (radius 2, strength 0.984, decay 0.695); win when your effective influence on your own cells exceeds 34.13.
**Topology:** 2D hex, axis size 8, 6-neighbor adjacency, fixed boundary.
**Turn Structure:** alternating.

### Scores (1-10)

- **Strategic Depth: 4** — Three identifiable strategies (self-max, mirror, interfere), single-step greedy heuristic captures most of the value. No multi-move tactics, no sacrifice, no ko. The game tree is wide but shallow.
- **Emergent Complexity: 4** — Influence-cluster geometry on hex is genuinely interesting (interior 19-reach vs corner 6-reach), and steal-by-placement-on-deposit is a real tactic. But without capture there are no forced sequences and no game-tree branching that punishes sloppy play.
- **Balance: 3** — First-mover advantage is structural and severe. Same-strategy P1 wins consistently (Games 1, 3 and the corner-cluster experiment). Greedy-vs-Random is 100/0 either side. Random-vs-Random shows P1 slight edge with most games timing out. R16's seat-balance probe ranking this as the GE champion is concerning evidence that the metric still mis-calibrates one-sided alternating games. **Saving grace:** strategy mismatch can flip the result (P1 self-max < P2 interfere), so the game is not a forced P1 win — but with equal-skill play, P1 has the edge.
- **Novelty (post-adversary): 4** — Tumbleweed-family with a different kernel; not a 1:1 re-skin but clearly within established placement+influence+hex design space.
- **Replayability: 4** — The decision space is real but narrow. Once you internalise "play interference if P1, mirror is always wrong, build clusters from centre" you have most of the game. Variation comes from where to start the cluster and which specific cells to steal, not from deep strategic regimes.
- **Overall "Would I play this again?": 4** — Pleasant, comprehensible, plays in 15-30 moves. Not deep enough to sustain repeated play. A reasonable teaching game for influence-mechanic intuitions.

### Closest known-game analog

**Tumbleweed** (2-player hex influence game). Distinguished by: radial decay kernel (vs Tumbleweed's line-of-sight), threshold scoring (vs Tumbleweed's territory count), no stacking, no swap rule. The strategic concepts (centre opening, cluster, contesting key cells) transfer; the specific tactics do not.

### Killer flaws

1. **Severe first-mover advantage** under equal strategy (Games 1, 3, multiple side experiments). No swap rule, no Pie rule, no compensation mechanism. The R16 seat-balance metric appears to have given this a free pass despite the imbalance.
2. **Pass action is always legal but useless**, and the double-pass-draw fix (good for other games) here is irrelevant because nobody passes.
3. **Threshold tuning is fragile**: 34.13 is reachable in ~9 well-placed clusters, so the game ends in ~17 ply with mirror play but ~30 ply with interference — and can reach the 100-turn cap if both sides interfere hard. Random-vs-random has 44% timeout/draws.
4. **Single-step greedy heuristic captures most of the strategic value**, suggesting limited depth.

### Best quality

The hex topology + radius-2 influence kernel produces a real geometric incentive: clusters near the centre are objectively better, corners are objectively worse, and a 2-step radius creates the right spacing for "near but not adjacent" interference tactics. This is the most interesting feature — the radial gaussian-on-hex creates a pleasing positional logic.

### Improvement ideas

**Add a swap (pie) rule:** after P1's first placement, P2 may either accept and play normally, or claim P1's stone as their own (with the colour of the next move flipped). This single change would neutralise the structural P1 advantage we documented and force P1 to choose an opening that is good but not best. The same fix that civilises Hex, Tumbleweed, and dozens of other connection/territory games would work here.

A secondary improvement: **add a simple capture rule** (e.g. if a stone has 0 friendly neighbours within radius 1, it converts to opponent ownership) — this would create real defensive considerations and multi-move tactics, deepening the strategic tree without changing the influence-threshold framing.
