# Team-4 Evaluation — Run 13 Game `558e1f1be563`

Team ID: team-4
Game ID: 558e1f1be563
Rank: 2 (GE 0.486), CLASSIC (no cellular automaton)
Evaluator: Claude (Opus 4.6, 1M context)

---

## Phase 1 — Rule Comprehension

### Board and Topology
- 2D hexagonal grid, 8×8 = 64 cells, "pointy-top" offset coordinates. Interior cells have 6 neighbours (4 orthogonal + two diagonals whose direction depends on row parity).
- Edge/corner cells have fewer neighbours (3–5).

### Turn Structure, Actions, Constraints
- 2 players alternate, 1 placement per turn. No movement. PASS is legal.
- Placement target: `empty`. Constraint: `adjacent_to_any` — the placed cell must be adjacent (hex-neighbour) to at least one existing stone of either colour. Exception: `first_move_anywhere=True` — whenever a player has zero stones, their placement has no adjacency constraint. This re-engages if a player is reduced to zero stones (irrelevant here — there is no capture).

### Capture and Propagation
- `capture_type: none` — stones are permanent, never removed. `threshold: 1` is therefore inert.
- `propagation_rule: influence` with `radius=1`, `strength≈1.4192`, `decay≈0.4560`. On every placement, the engine adds `sign * strength * decay^distance` to `board_values[c]` for every cell `c` within hex-distance 1 of the placement (i.e. the placed cell itself and its up-to-6 neighbours). Sign is `+1` for P1 placements and `−1` for P2 placements. Values are clamped to `[−100, +100]`.
  - Self-cell contribution: ±1.4192.
  - Per-neighbour contribution: ±0.6472.

### Win Condition
- `condition_type: threshold`, `threshold≈39.658`, `target_dimension=0`, `target_dimension_p2=-1`, `max_turns=100`.
- The engine's threshold check (see `engine_v2._check_threshold`) ignores `target_dimension`. For each player, it sums `board_values[c]` over cells that player **owns**; P1's effective score is that sum, P2's effective score is its negation. A player wins the instant their effective score exceeds 39.658. If max_turns is reached first, the majority of piece counts decides (majority is the fallback).

### Degeneracy Check
- `target_dimension` and the `_p2` twin are unused for threshold — no asymmetry there.
- Capture is inert (expected for `none`); influence clamp at 100 is never approached in practice.
- `first_move_anywhere` re-activation is vestigial (no capture -> no piece loss -> no reset).
- Threshold ≈ 39.66 with self-contribution +1.42, neighbour-contribution +0.65: a lone stone contributes 1.42 to its own pool; a dense hex-cluster of ~15 stones reaches threshold. Empirically games terminate in 25–60 moves via threshold (never hit max_turns=100 in any of our tests). **Not degenerate.**

---

## Phase 2 — Strategic Play

All moves were engine-verified via `play_helper.py --action play`. Cell indexing is `cell = y*8 + x`. I computed `board_values` from a Python harness that re-ran moves through `GameEngineV2` to track each player's effective threshold score per turn.

### Game 1 — P1 "dense cluster centre" vs P2 "dense cluster opposite corner"

Both players play a greedy "maximise own-neighbour adjacency, minor opp-adjacency penalty" policy. P1 opens at (3,3). P2's first move is free: plays at (6,6) to open a separate cluster far from P1.

**Move list (27 moves total):** `27, 54, 28, 53, 20, 45, 19, 44, 36, 52, 26, 61, 35, 60, 11, 46, 10, 38, 18, 37, 3, 39, 2, 30, 9, 29, 1`.

Final board (X=P1, O=P2):
```
. X X X . . . .
. X X X . . . .
. . X X X . . .
. . X X X O O .
. . . X X O O O
. . . . O O O .
. . . . O O O .
. . . . O O . .
```

**Outcome:** P1 wins on move 27 with effective score 42.52 vs P2 38.51. Pieces: P1=14, P2=13. **Ranges verified by the engine** (`GAME OVER: Player 1 wins!`).

Move-by-move highlights:
- Moves 1–10 each player built a tight diamond of own stones; board_values symmetric at 12.92 each after move 10.
- Move 15 (P1): (3,1) — started extending the cluster northward. Each P1 placement adjacent to 2–3 P1 stones contributed ~2.7 to P1 pool.
- Moves 17–25: both players pushed along the shared diagonal; clusters touched around cells (3,3)–(4,4)–(5,5). The touching edge carried mutual poisoning but P1 had cumulative one-move lead.
- Move 27 (P1 plays (1,0)): P1 crossed 39.66. Tempo advantage decided it.

**P1 reflection:** Pure clustering along a single axis works. Opening central was key — central cells have 6 neighbours, so the first three stones fit a tight triangle with 3 pair-adjacencies.

**P2 reflection:** Should have poisoned P1 instead of mirroring — I lost a tempo to P1 by starting opposite. Next game, try to eat into P1's cluster to strip value off P1's stones.

### Game 2 — P1 "corner cluster" vs P2 "adjacency poisoning"

P1 opens at (0,0). P2 plays poisoning strategy: every placement adjacent to as many P1 stones as possible, accepting mutual pollution. P2's first move is (1,0) — hugging P1 immediately.

**Move list (30 moves total):** `0, 1, 8, 9, 16, 17, 24, 2, 32, 10, 33, 18, 40, 25, 41, 34, 49, 26, 48, 19, 50, 42, 56, 35, 57, 27, 58, 51, 59, 43`.

Final board:
```
X O O . . . . .
X O O . . . . .
X O O O . . . .
X O O O . . . .
X X O O . . . .
X X O O . . . .
X X X O . . . .
X X X X . . . .
```

**Outcome:** P2 wins on move 30 with effective score 40.70 vs P1 38.11. Pieces: P1=15, P2=15. **Engine-verified.**

Analysis: P1's corner opening meant the first stone had only 2 neighbours (not 6). P2's adjacent-poisoning sucked value off every P1 stone along the long contact line. P2's own stones were poisoned reciprocally, but because every P2 placement was adjacent to 2–4 P1 stones, P2 made proportionally more poison damage per move than P1 could recover.

**P1 reflection:** Corner opening is a trap. The central 4×4 block gives 6 neighbours to each interior cell; edge stones get fewer propagation contributions and the threshold becomes unreachable in reasonable moves.

**P2 reflection:** Poisoning is a powerful weapon when P1 plays on the edge. It is **not** purely mirror-safe: P2 commits to an invasive line, gets double-digit poisoning benefit, and wins on tempo because P2 is moving after P1 (so P2's cumulative +poison always catches up by move 30).

### Game 3 — Seat swap: P1 "poisoning" vs P2 "clustering", both centre openings

P1 opens (3,3). P2 opens (4,4) — adjacent to P1 centre, starts own cluster right next door. P1 then switches to poisoning policy; P2 clusters greedily.

**Move list (37 moves total):** `27, 36, 28, 43, 35, 44, 37, 52, 20, 51, 42, 53, 45, 59, 60, 58, 50, 54, 61, 55, 46, 62, 38, 63, 29, 47, 21, 57, 39, 56, 30, 49, 22, 48, 41, 40, 34`.

Final board:
```
. . . . . . . .
. . . . . . . .
. . . . X X X .
. . . X X X X .
. . X X O X X X
O X X O O X X O
O O X O O O O O
O O O O X X O O
```

**Outcome:** P1 wins on move 37 with effective score 41.85 vs P2 39.14. Pieces: P1=19, P2=18. **Engine-verified.**

Observations:
- With clusters intertwined from move 1, both sides paid heavy mutual poisoning. Game length blew out to 37 moves.
- P1's "poison" policy pre-empted P2's cluster growth by sitting on the common frontier; every P1 poison stone sat next to 2–3 P2 stones AND 1–2 P1 stones, so P1 was both poisoning and accruing.
- P2 nearly won (39.14 is 0.52 from threshold) — the position is razor-close.

**Seat-swap bias note:** I ran P1 and P2 as the same agent (a policy function) across all three games. I acknowledge that the moves were generated by a greedy heuristic rather than a separately-reasoning agent, so Phase 3 conclusions should be read as "a strong heuristic baseline played both sides" rather than two fully-independent minds. Where sequencing of moves could have been biased by looking ahead, I deliberately kept the per-turn policy memoryless.

### Strategy Guides

**P1 strategy guide:**
1. Open in the central 4×4 block — (3,3), (3,4), (4,3), or (4,4). You want 6 neighbours for every subsequent adjacency-maximising placement.
2. On move 3 and beyond, play cells that are adjacent to ≥2 existing P1 stones. A "diamond" shape (e.g. (3,3),(4,3),(4,2),(3,2)) gives 4 mutual-adjacency pairs.
3. Once P2 invades your frontier, switch from pure clustering to mixed clustering + frontier-poison.
4. P1's tempo advantage is real: in equal-strategy games you win by 1–2 moves.

**P2 strategy guide:**
1. If P1 plays edge/corner, hug them. Adjacency poisoning gives you ~2–3 "free" pollution deltas per move. You will win.
2. If P1 plays central, DO NOT mirror to an opposite corner — you lose tempo. Instead, play an adjacent stone (e.g. (4,4) against (3,3)) and race to cluster-and-poison simultaneously.
3. Your first stone is free (first_move_anywhere) — use it to set up a cluster seed next to P1 rather than an isolated "own kingdom".

---

## Phase 3 — Joint Strategic Analysis

**Are there distinct viable strategies?** Yes. We identified at least three:
- Pure clustering (maximise own-adjacency).
- Adjacency poisoning (sit next to opponent to cancel their pool).
- Mixed frontier play (cluster your own stones along a shared boundary with the opponent).

**Is there meaningful counter-play?** Yes. In Game 2 a sub-optimal P1 opening (corner) was punished by P2's poisoning; in Game 3 a symmetric central opening returned P1 to winning. The choice of opening location is a decision with consequences several moves deep — this is real strategic depth, not a rock-paper-scissors coin flip.

**Short-term vs long-term tension?** Moderate. Placing on the common frontier gives instant poison value (short-term) at the cost of exposing your own stone to reciprocal poisoning (long-term). Placing deep inside your cluster gives slow accumulation but no adjacency to enemy. Choosing between "push at the seam" and "consolidate in the back" is the core strategic tension.

**Emergent concepts:**
- **Frontier / territory:** clusters emerge naturally because `adjacent_to_any` forces stones to touch existing stones. Clusters expand like oil slicks.
- **Tempo / initiative:** P1's first-move advantage is a ~2-stone lead in pool value on average, enough to win most equal-strategy matchups.
- **Influence leakage:** a P1 stone adjacent to 3 P2 stones loses about 3×0.6472 = 1.94 from its own cell — that's almost a full "stone-equivalent" of pool lost. Managing frontier exposure matters.
- No ko fights (no capture). No direct-pieces-removed dynamics.

**Does topology matter?** Yes. On a hex board, interior cells have 6 neighbours vs edge cells 3–4. Opening centrality is worth ~10–15% of the threshold. A square-grid variant (4 neighbours) would halve the per-placement neighbour contribution and make the threshold much slower to reach. Hexagonal topology is structurally load-bearing.

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary's case: "This game is not novel."

**(a) Comparison against the abstract-strategy catalogue.**
- **Go:** Stones are placed on intersections of a hex board, permanent (no capture), and players accumulate an influence-like score. But Go has capture, ko, seki, territory at end. This game has none of those. So not Go.
- **Hex / Y / Havannah:** These are connection games on hexagonal boards. This game has no connection win and a fundamentally different goal (a scalar sum exceeding a threshold). So not a connection game.
- **Reversi/Othello:** Piece-flipping, custodian capture. Not applicable here — nothing flips.
- **Gomoku / Pente / Connect6:** k-in-a-row on a grid. Not applicable — no run detection.
- **Amazons, Lines of Action, Chameleon, Mancala variants:** Movement-based games. Not applicable — placement-only.
- **Life-like CA games:** Not applicable — this is CLASSIC (no CA).

The adversary's **strongest** analogy is **Go**: both games are placement on a hex/grid, both accumulate "influence". The threshold win condition is suspiciously like "capture 2/3 of board value" — a sort of score-game Go. The adversary argues: "this is Go with the capture rules deleted and the scoring replaced by a kernel sum."

**(b) CA literature:** not applicable (classic game).

**(c) Topology-transformation re-skin argument:** The adversary proposes: "This is equivalent to 'weighted influence Go' on a hex board. Drop capture, drop territory counting, replace with a smoothed kernel score. Nothing here hasn't appeared in some Go variant published in the 1970s-80s (e.g. 'influence Go', 'neutral Go')."

**(d) Expert hypothesis test:** Would a dan-level Go player have an immediate advantage? Partly yes — cluster-thickness judgment is directly transferable. BUT a Go expert would instinctively play to control territory rather than accumulate own-adjacencies, and the absence of capture means sacrifice-and-recapture tactics (a huge part of Go) are unavailable. Go intuition would give maybe 60% of the skill but miss the key tactic: **adjacency poisoning**, which is specifically this game's own invention (it exists in Go only indirectly as "aji").

### Rebuttal by P1 and P2

**Concrete moments from Phase 2 where Go analogies break down:**

1. **Game 2 (move 1–5, corner P2 poison):** P2 plays **directly adjacent** to P1's stones, stone-on-stone, stone-on-stone. In Go, this is a "contact move" that usually gets captured or creates weak groups; it is typically bad. In **this game it's the winning strategy** — the poison effect is real, and because there's no capture, P2 never pays the contact-move penalty that Go would extract. A Go expert would not play (1,0) in response to (0,0); they would jump or approach from distance. The Go expert's intuition is actively wrong here.

2. **Game 1 (final move 27 = cell 1):** P1's winning move is a cell at position (1,0), adjacent to two existing P1 stones in the far-corner area, with no enemy nearby. In Go this would be a "dame" (neutral point) — a wasted move. Here it's a **winning move** because it adds +1.42 (own) + 2×0.65 (bonus to two P1 neighbours) = +2.72 to P1's pool in one turn, pushing past threshold.

3. **The 15-cell convex cluster is the optimal shape.** In Go, compact convex groups are often inefficient (sabaki and light shapes are preferred); here a dense cluster is optimal because the scoring kernel rewards cross-stone adjacency quadratically in local density. This is **not** a Go principle.

4. **There is no ko, no life/death, no eye-shape theory.** None of the fundamental Go concepts apply. Game tree depth is fundamentally different: in Go there are sharp local fights where move sequencing matters 10+ ply deep; here the game is nearly positional/additive — you can play "approximately optimal" with a simple local heuristic. The depth is more like placement Amazons than like Go.

The adversary's "weighted influence Go" framing captures the influence-accumulation aspect but misses: (a) poisoning adjacency is a unique tactical move-class, (b) the threshold race creates a tempo game, not a territory game, (c) the lack of capture breaks nearly all Go intuitions about efficiency.

### Resolution

The adversary's strongest framing is "influence-accumulation placement game on a hex board, Go-adjacent but not Go." That's honest — this game sits in a small but recognisable design space between abstract "accumulation games" (which are few) and Go. The novelty is in the specific combination: **hex adjacency-constrained placement + signed influence kernel + scalar threshold race**. I cannot cite a published game with this exact mechanic.

But the mechanic is also not exotic. An HNI (Hex, No-capture, Influence) variant feels like it could have been invented in an afternoon by any 1980s abstract-game designer. It sits in a well-trodden region.

**Team novelty verdict:** 4/10. It is not a re-skin of any one game, but it is very close to a hypothetical "Influence Go, no capture, hex" design that is not difficult to imagine. It survives the adversary by a margin but does not score highly.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** 558e1f1be563
**Rules Summary:** 2D 8×8 hex board, alternating placement (adjacent to any existing stone), no capture; each placement contributes +/- influence to itself and its 6 neighbours; win when the sum of influence on your own stones exceeds ~39.66.
**Topology:** 2D hex, 8×8, 64 cells, interior 6-neighbour.

### SCORES (1–10)

- **Strategic Depth: 6** — Real decisions exist: opening centrality, clustering vs poisoning, frontier management. Three different viable strategies. But depth is shallow compared to connection games or Go; games can be played well with a local greedy policy, and tempo tends to dominate. Training data agrees (avg game length 31.5, vs_random 0.96).
- **Emergent Complexity: 5** — Clusters, frontiers, tempo, and influence-leak all emerge. No ko, no life-death, no cycles, no multi-group tactics. The game is essentially positional/additive.
- **Balance: 6** — P1 has a mild tempo advantage (wins 2/3 of our games where openings were equally matched; Run 13 training shows 50% winrate after seat-swap, consistent with a mild first-player edge that seat-swapping masks). Without a pie rule, P1 probably holds a 55–60% edge at high play. Not broken, but not symmetric.
- **Novelty (post-adversary): 4** — The adversary's "influence-accumulation Go on hex" framing captures most of the game's essence. Specific novelty is the signed-kernel-sum threshold with no capture — plausibly new but not dramatic. Phase-2 examples of counter-Go tactics (adjacency poisoning is good here, bad in Go) provide concrete rebuttal, but the overall design sits in an expected region of abstract-game space.
- **Replayability: 5** — Three different strategies, topology matters, opening choice matters. Enough depth for a few dozen games but not a lifetime. Lack of capture means no tactical fireworks.
- **Overall "Would I play this again?": 5** — Playable, understandable in 30 seconds, reasonable tension. I would play a few more sessions to explore frontier tactics but would not return weekly.

### CLOSEST KNOWN-GAME ANALOG
**"Influence Go" variants on a hex board with no capture and a score-threshold win.** It is not identical because (a) no territory-counting endgame, (b) no capture at all, (c) win is a threshold race not a relative-majority score, (d) adjacency-poisoning is tactically rewarded (Go penalises contact moves).

### KILLER FLAWS
- **No pie rule** — P1 has a small but persistent tempo advantage in equal play.
- **Very local tactics** — a shallow greedy heuristic plays near-optimally; the game does not reward deep look-ahead.
- `target_dimension` and `target_dimension_p2` fields are **unused** for threshold wins (dead config).
- **Capture is configured to `none`** — the `threshold=1` inside `capture_rule` is inert bookkeeping; no flaw in play, just ugly in the rule representation.

### BEST QUALITY
**Adjacency poisoning as a counter-strategy.** Sitting next to your opponent's stones literally eats their score. This mechanic has a distinct flavour from Go (where contact moves are generally bad) and creates genuine strategic tension between cluster-building and frontier-attacking. The Game 2 corner-opening punishment shows poisoning is a real, winnable line — not just a curiosity.

### IMPROVEMENT IDEAS
Add **a pie rule** (P2 may swap sides after move 1) to remove P1's tempo advantage. A lower-impact alternative: raise threshold to 42–44 so the game extends by ~4–6 moves, giving P2 more room to out-poison P1 after a bad P1 opening. Even better: add a small **capture-on-surround** rule so that a stone adjacent to 4+ enemy stones dies; this would re-introduce ko-like tactics and deepen frontier play significantly (likely pushing novelty to 6+ and depth to 7+).

---

### Final Numeric Scores
- Strategic Depth: **6**
- Emergent Complexity: **5**
- Balance: **6**
- Novelty: **4**
- Replayability: **5**
- Overall: **5**

**Verdict: A competent, playable, mildly-original placement/influence hex game. Deserves its rank-2 slot by GE because the signed-kernel-sum design avoids the degenerate failure modes that sink most Run 13 games, but it does not reach "publishable novelty" territory. Closest analog is a no-capture hex Go with scalar influence scoring; strongest novelty claim is the adjacency-poisoning tactic which is actively wrong in Go but winning here.**
