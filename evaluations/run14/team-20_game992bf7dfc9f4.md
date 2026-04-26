# Team-20 Evaluation: Game 992bf7dfc9f4 (Run 14, rank 5)

**Team ID:** team-20
**Game ID:** 992bf7dfc9f4
**GE:** 0.4196, **ELO:** 2953, **Run 14 rank:** 5
**Turn structure:** SIMULTANEOUS + active CA (the sim×CA hybrid premised for R15)

---

## Phase 1 — Rule Comprehension

### Board
- **8×8 grid**, von Neumann adjacency (4-neighborhood, no diagonals, no wrap).
- 64 cells total.

### Turn structure — SIMULTANEOUS
Both players submit moves per round; `engine_v2.step_simultaneous` resolves:
1. If both target the same cell → **mutual annihilation** (cell stays as it was; neither piece lands).
2. Otherwise both placements land.
3. CA step(s) run after placement.
4. Super-ko check, then win-condition check.

### Action space
- 65 actions: placements 0..63 (action = `y*8 + x`) plus pass (64).
- **Placement constraint:** `adjacent_to_own` (must touch an existing own piece) **except** the first move for each player, which is `first_move_anywhere`.
- Action type: place only (no moves).

### Win condition
- **Territory**: first player to own **>62.53% of cells** (> 40.02 cells → 41+) wins.
- `max_turns = 100`. If both players pass in the same round, game ends and majority wins.

### Cellular Automaton (THE DEFINING FEATURE)
- `steps_per_turn = 1`. Critically, the CA loop in `step_simultaneous` is:
  ```python
  for i in range(steps_per_turn):
      acting_player = 1 if i % 2 == 0 else 2
      self._run_ca_step(acting_player)
  ```
  With `steps_per_turn=1`, **only i=0 fires → acting_player is ALWAYS 1**. The CA is *never* run from P2's perspective. This is a huge structural asymmetry.
- `max_neighbors = 4`.
- 147-entry transition table, but with max_neighbors=4 only **45 entries are reachable**. Of those:
  - **36 identity transitions** (no change).
  - **9 non-trivial transitions** — enumerated below with "friendly = acting player (always P1)":

| State       | Friendly nbrs | Enemy nbrs | → New state |
|-------------|--------------:|-----------:|-------------|
| empty       | 2 | 0 | **friendly (P1) BIRTH** |
| empty       | 2 | 1 | **friendly (P1) BIRTH** |
| empty       | 4 | 0 | **friendly (P1) BIRTH** |
| friendly P1 | 0 | 1 | **enemy (P2) — P1 FLIP** |
| friendly P1 | 0 | 2 | empty (P1 dies) |
| friendly P1 | 1 | 2 | empty (P1 dies) |
| friendly P1 | 1 | 3 | empty (P1 dies) |
| enemy P2    | 2 | 0 | **friendly (P1) — P2 CONVERT** |
| enemy P2    | 3 | 0 | empty (P2 dies) |

So the CA is highly active (9/45 ≈ 20% non-trivial) and highly ASYMMETRIC in favor of P1 (P1 can birth, convert P2, and kill P2; P2 cannot do any of the equivalents).

### Flagged degeneracies
1. **CA is structurally asymmetric** — `steps_per_turn=1` never reaches the `i=1 → player 2` branch. Every CA step treats P1 as "friendly." P2's stones can never trigger births, convert P1, or kill P1. This is the game's central flaw.
2. **The `1,0,1 → 2` flip rule** punishes P1 for placing an isolated stone adjacent to any P2 stone — but also hands P2 a first-strike: if P2 plays adjacent to P1's first-move stone, **P1's stone flips to P2 on that same round's CA step** (see Phase 2 Game 3, round 1). This partially counteracts the otherwise P1-dominant CA.
3. **Territory threshold 41/64 is reachable but not trivially so.** In 2/3 of my playthroughs, P1 ended up at 32 or 37 pieces (below threshold) and the game resolved via **double-pass majority** — the Run 13 known failure mode. The threshold is reachable in the very best line (Game 1 hit 41 on round 16) but a minimally competent P2 can keep P1 below threshold via invasion.
4. **Placement constraint + no-capture means groups can't be killed by placement alone.** Territory is monotonic for each player (modulo CA flips). This bounds game length.

---

## Phase 2 — Strategic Play (3 games, engine-verified)

All moves were engine-verified via a local runner (`/tmp/play_sim.py`) that calls `GameEngineV2.step_simultaneous(a1, a2)` directly. Regular `play_helper.py --action play` **sequentializes** simultaneous moves and does NOT exercise true simultaneous collision / CA semantics — I had to bypass it for correctness.

### Game 1 — Baseline: P1 growth, P2 far-corner mirror
Moves (P1, P2): (27,56) (28,57) (35,48) (29,49) (30,50) (31,58) (19,59) (26,42) (25,43) (12,44) (14,45) (4,46) (16,47) (32,60) (0,61) (40,62).

P1 built a compact block from (3,3). Each placement usually triggered 1–3 CA births at adjacent empties with f=2 (e.g., placing at (3,4) after (3,3)(4,3) births (4,4); placing at (6,1) births (7,1) etc.). P2 built an isolated L-shape in opposite corner that never triggered any CA growth (CA from P1's perspective → empty cell with 2 P2 neighbors is "0,0,2 → 0", no birth).

**Result:** P1 wins on **round 16** via territory threshold (41 / 64 = 64.06% > 62.53%). Final piece count 41 vs 16.

### Game 2 — P2 aggressive invasion strategy
Moves (truncated, see above). P2 pivoted from mirror to invading P1's territory at (3,2)=19 and (2,2)=18 around round 11. Key finding: **a P2 stone adjacent to 2+ P1 stones and 2+ P2 stones (f=2,e=2) is stable** ("2,2,2→2"), but a P1 placement adjacent to 2 P2 + 1 P1 dies ("1,1,2→0"). So P2 invaders create "death cells" that poison nearby P1 placements.

P2's invasion cluster at (2,2)(3,2) did slow P1 — by round 20 only 4-5 empty cells remained for P1 and they were all flanked by 2+ P2 enemies. P1 was forced to pass.

**Result:** Game reached max-turn plateau long before turn 100; I ended via **double-pass majority** at round 22. **P1 wins 32 vs 22**. Did NOT hit territory threshold.

### Game 3 — Seat-swap test: P2 aggressive first-move flip
Key opening: (27, 28) — P1 plays (3,3), P2 plays adjacent (4,3). Round-1 CA: P1's isolated (3,3) has f=0,e=1 → "1,0,1→2" → **flips to P2**. P1 ends round 1 with **0 pieces, P2 with 2**.

Round 2: P1 plays (2,3)=adj to P2's (3,3). Same flip → P1 still 0, P2 up to 4. This was the most interesting moment of the evaluation — it shows **P2 has a real opening-phase counter** to centralized P1 play, via the flip rule.

Round 3: P1 retreated to corner (0,0), started over, built an L-shape there. P2 kept extending toward P1. P1 eventually pulled ahead via CA births (P2 still can't birth via CA) and won.

**Result:** Double-pass majority. **P1 wins 37 vs 24**. Did NOT hit territory threshold.

### Player reflections

**Player 1 (me, seats 1-2):** My strategy was "build a compact block around the first-move center/corner; exploit f=2 birth rule by extending in L-shapes; avoid placing isolated stones adjacent to P2 (the flip rule)." This worked in all three games. The key insight is that the CA gives P1 ~+1.5 pieces per placement on average (1 placed + ~0.5 birthed) while P2 gets +1 per placement. This compounding advantage is sufficient to win even if P2 plays perfectly, except in the specific opening-flip line where P2 can delete P1's first move.

**Player 2 (me, seats 2-1):** I tried three approaches: (a) mirror in far corner — totally ineffective, P1 wins effortlessly; (b) march toward P1 in a snake — slightly better but P2 still gets outpaced because P2 can't CA-birth; (c) aggressive adjacency flip on turn 1 — this is the ONLY thing that works and even it only delays P1, doesn't win. P2 has no positive-sum action in the mid-to-late game; the best P2 can do is poison P1's growth cells by forming 2-stone enemy clusters inside P1's region (Game 2).

**Endgame:** 2/3 games resolved by double-pass majority — **flag this as a Run 13 failure-mode recurrence**. Only Game 1 hit the territory threshold cleanly. In Games 2 and 3, both players had few-to-zero viable placements and passed to end.

### Strategy guides

**P1 strategy guide:**
1. Opening: play near center (NOT edge/corner — central gives more CA birth neighbors later). If P2 plays adjacent on round 1, accept the flip and replay first-move-anywhere at a safe distance.
2. Build L-shapes and corners to maximize f=2 birth cells. Every placement should create at least one adjacent empty cell with f=2.
3. Avoid placing lone stones with 1-2 enemy neighbors unless already backed by friends (f ≥ 2). The `1,1,2→0` and `1,0,1→2` rules are the main killers.
4. Once you have a solid cluster, "double up" along its edge — each new stone on the outside births one neighbor inward/onward.
5. If P2 invades with a 2-stone cluster, don't try to place in their adjacent cells; grow *around* them instead. A P2 2-cluster is stable and will survive, but it can't grow.

**P2 strategy guide:**
1. Round 1: if P1 plays near-central, **immediately play adjacent** to flip P1's stone via `1,0,1→2`. This is the single most valuable move P2 has.
2. Keep playing adjacent to P1's isolated stones in the first few rounds before P1 can form a 2x2 block.
3. Once P1 has a solid group, invade with **pairs** (place two stones adjacent to each other, adjacent to P1's frontier). A P2 pair with f=2,e=2 at `2,2,2→2` is stable; isolated P2 stones with `2,2,0` are converted back to P1.
4. Recognize you cannot win on territory threshold. Your only path to victory is to starve P1 of legal placements and hit max_turns with more P2 pieces than P1 — which requires choking P1's growth early.
5. In practice, **P2 loses almost always**, and I couldn't find a line where P2 wins against competent P1.

---

## Phase 3 — Strategic Analysis (joint)

### First-mover / seat-identity
The game is SIMULTANEOUS in form, but the CA asymmetry creates a **strong P1 bias** that simultaneous play does NOT eliminate. In my 3 games:
- Game 1 P1 wins 41–16 (threshold)
- Game 2 P1 wins 32–22 (majority)
- Game 3 P1 wins 37–24 (majority, and P1 survived an opening flip attack)

**All 3 games won by P1.** Training-run data claim final-winrate 0.500 across 4 seeds, but "trained vs random" is 0.86–0.94 — consistent with both-sides-trained agents converging to a draw by forcing non-convergence, not genuine balance. My hand-play says the game is ~90%+ P1-biased with a skilled P1.

**The simultaneous mechanic does not fix first-mover advantage here** because the asymmetry isn't about "who moves first" but "whose perspective the CA uses." Making play simultaneous on top of an asymmetric CA just means both players submit at once while the CA still favors P1.

### Distinct strategies
- P1: single dominant strategy (compact block growth via L-shape CA births). Minor variations in direction only.
- P2: (a) mirror (loses), (b) extend-and-march (loses), (c) opening flip (delays but doesn't win), (d) invade-to-poison (slows P1 but doesn't win). The invasion strategy in Game 2 is the deepest; it forced Game 2 into a double-pass majority instead of threshold.

### Short vs long term tension
Mild. The flip rule (`1,0,1→2`) means P1 must avoid lone extensions near P2, which creates a small sacrifice-now vs build-now choice. But with `first_move_anywhere`, P1 can always start over cheaply, so sacrifice pressure is low.

### Emergent concepts
- **CA birth chains** — placing one stone creates a "tail" of births in one direction; the geometry matters (L-shape > straight line).
- **Poison cells** — empty cells surrounded by 2 P2 and 1 P1 become graveyards for future P1 placements (1,1,2→0 kills).
- **Opening flip** — a P2-specific tempo weapon in round 1, unique-feeling.
- **Mutual annihilation** — in 3 games this never fired (no collision). With P1 always wanting adjacent-to-own cells and P2 wanting adjacent-to-own from a different base, the only collision scenario is both going first-move-anywhere to the exact same cell on round 1, which is an anti-coordination game. Neither of us tested it.

### Topology
8×8 grid with no wrap — fairly standard. The corners are significantly less birth-productive than open-board positions (fewer empty neighbors to birth into). Center start > corner start for P1.

---

## Phase 4 — Novelty Adversary

### Prosecution: "This game is not novel"

**(a) Known abstract-game analogs.**
- **Go**: Similar adjacency (4-neighborhood), territory win, but Go has surround-capture and alternating turns. This game has no explicit capture, simultaneous turns, and CA.
- **Conway's Life / HighLife / Day&Night**: The CA transition table is NOT a known Life-family rule. Life is 2-state (B3/S23). This game has 3 states (empty/friendly/enemy) and uses an f/e split, not a total-neighbor count. However, the rule `0,2,0→1` (empty with 2 friendly, no enemy → friendly) IS just "B2"-like birth. Combined with `1,0,2→0` and `1,1,2→0` death rules, it echoes **B2/S03** (a known instability rule in totalistic land). The player-split makes it non-totalistic, but the birth-at-2 rule is familiar.
- **Reversi/Othello**: The `1,0,1→2` flip rule looks like Othello capture in microcosm: a lone stone adjacent to an enemy flips. But Othello requires bracketing (enemy-enemy-...-friendly), here we just need adjacency. So it's a much weaker flip.
- **Immigration Game** (Life with 2 colors): An existing 3-state CA where two colors compete. This game's CA is directly in the Immigration Game family, just with a custom (non-B3/S23) rule table.
- **Gungo / simultaneous Go variants**: Simultaneous Go exists in academic variants (Gungo, Phantom Go). The simultaneous-placement idea with same-cell annihilation is not unique to this game.
- **Blotto / Colonel Blotto**: N/A — no resource-allocation mechanic.

**(b) CA literature.** The rule is an outer-totalistic 2-color CA on a grid with a custom transition table. The closest literature match: **Two-species Lenia / 2-color Life / Immigration Game**. The specific rules "empty+2friendly→friendly" and "friendly+1enemy→enemy" are reminiscent of predator-prey CAs but with a single-sided perspective (only P1's). The single-sided CA step is an engine quirk, not a deliberate design.

**(c) Simultaneous games.** Diplomacy has simultaneous orders but the resolution is complex. Rock-Paper-Scissors lacks spatial structure. **Gungo** (Go where both players make one move simultaneously, collisions annihilate) is the direct analog of this game's turn structure. If Gungo + any CA layer exists in the literature, this is a direct combination.

**(d) Re-skin hypothesis.** The game is plausibly "Immigration Game CA + Gungo turn structure + territory win condition + `adjacent_to_own` placement constraint". Each component is known; the combination might be novel but feels assembled rather than discovered.

**(e) Expert transfer.** A skilled Go player would bring territory-intuition and cluster-building, but the CA birth rule inverts Go's "extend thin, surround wide" heuristic — here you want tight clusters. A skilled Life player would recognize the birth-at-2 rule immediately and build L-shapes. A Life+Go hybrid player would have 60-70% of the intuition.

### Rebuttal

Specific strategic moments from Phase 2 that don't fit known analogs:

1. **Game 3, round 1 flip**: a one-move tempo weapon where P2 deletes P1's opening by placing adjacent. No Go or Life player would predict this — it emerges from the specific transition `1,0,1→2`. Closest analog is Othello, but Othello needs bracketing; here mere adjacency suffices for a 1-stone flip.

2. **Game 2, round 12 P2-invasion stability**: a P2 stone placed at (2,2) with f=2 and e=2 neighbors survives (stable at `2,2,2→2`), but a P2 stone with f=2,e=0 is captured by P1 (`2,2,0→1`). This non-monotonic stability (enemy crowding *helps* you survive P1) has no Go/Life analog I can identify.

3. **CA asymmetry itself**: in any natural 2-color CA, both colors are symmetric. Here the engine runs CA only from P1's side. This creates a strategic world unlike any known abstract game — P2 is playing "evade the Life grid" while P1 plays "feed the Life grid." It's more like a single-player Life puzzle with an adversary than a two-player game.

### Joint novelty score: **4 / 10**

The components are each derivable from known games (Gungo + Immigration Game + placement-adjacency constraint). The combination is fresh, but the most striking behaviors (asymmetric CA, opening flip) are arguably *emergent bugs* of the engine (steps_per_turn=1 never reaching P2's perspective) rather than intended design. A cleaner version with `steps_per_turn=2` would have a symmetric CA and likely be less interesting, losing even the novel dynamics. **Net: moderate-low novelty; the game's distinctive features are partly accidental.**

---

## Phase 5 — Verdict

**Team ID:** team-20
**Game ID:** 992bf7dfc9f4
**Rules Summary:** 8×8 grid, simultaneous placement with `adjacent_to_own` constraint (first move anywhere), mutual annihilation on collision, 1 CA step per round, territory win at >62.5% of cells.
**Topology:** 2D grid, axis_size 8, von Neumann adjacency, no wrap.
**Turn Structure:** SIMULTANEOUS (but CA runs from P1's perspective every round — structural asymmetry).

### Scores (1-10)

- **Strategic Depth: 4**
  Single dominant P1 strategy (L-shape growth). P2 has a narrow counter (opening flip + invasion poisoning) but no win path. Moves feel mechanical: most placements have an obvious "best" that maximizes CA births. The strategic depth that exists is almost entirely on the P2 side trying to slow the loss.

- **Emergent Complexity: 5**
  The CA produces non-trivial growth patterns (L-shapes → 2x2 squares → extended rectangles) and some non-obvious interactions (poison cells, flip-on-adjacency, enemy-cluster stability). But with only 9 active transitions, the complexity is bounded. The same patterns recur across games.

- **Balance: 2**
  3/3 games P1 wins, including one where P2 got a 2-0 stone lead via opening flip. Training runs report 0.50 win rate, but my read is this reflects agents learning to draw/stall, not genuine balance. The simultaneous mechanic does NOT compensate for CA asymmetry. Seat-swap evidence: limited because I played both sides, but the game-3 opening-flip test shows even a maximally aggressive P2 start is insufficient.

- **Novelty (post-adversary): 4**
  Gungo-style simultaneous + 2-color Immigration-Game CA + placement-adjacency constraint = components are all known, combination is fresh but derivative. The most striking emergent behaviors are partially artifacts of `steps_per_turn=1` never firing the P2-perspective CA branch.

- **Replayability: 3**
  Once you know the L-shape/birth trick and the flip rule, games play out similarly. Low branching factor in the late game (legal actions often single-digit). I'd happily play 2-3 games to learn, then be done.

- **Overall "Would I play this again?": 3**
  The game is interesting to analyze but mechanically one-sided. Its main value is as a research datapoint on sim×CA interaction, not as a game to play.

### Closest known-game analog
**Gungo + Immigration Game CA** (simultaneous Go meets two-color Conway's Life). Not identical because: (i) Gungo lacks a CA layer, (ii) Immigration Game is symmetric in color and doesn't have a placement phase, and (iii) the `1,0,1→2` flip rule has no clean analog in either.

### KILLER FLAWS
1. **CA asymmetry bug-feature.** `steps_per_turn=1` means the CA always runs from P1's perspective. P2 cannot birth, cannot convert P1, cannot capture-by-surround. This is almost certainly an engine bug that happens to produce an interestingly unbalanced game — but "interesting by accident" is not strategic design.
2. **Double-pass majority resolution in 2/3 games.** The territory threshold (41 cells) is reachable only in the best-line scenario; against any competent P2 interference, the game resolves by passing when placements run out. Same failure mode as Run 13.
3. **P1 opening is essentially solved.** Play near center, build L-shape, extend toward open space. There's no meaningful early-game decision.
4. **Simultaneous play adds nothing.** No collisions occurred in any of my 3 games — neither player ever had an incentive to target the same cell. The mechanic is decorative.

### BEST QUALITY
The opening flip dynamic (`1,0,1→2` triggered by P2 placing adjacent to P1's first move) is genuinely novel feeling — a tempo weapon specific to the round-1 geometry that no Go or Reversi player would intuit. It creates one interesting decision per game.

### IMPROVEMENT IDEAS
The single rule change that would most deepen the game: **`steps_per_turn = 2`** (alternate P1 and P2 CA perspectives, one step each). This would give P2 access to symmetric birth / capture / flip dynamics and likely produce a genuinely balanced sim×CA game. Secondary improvement: make `first_move_anywhere` apply only to the very first round (not every time a player returns to 0 pieces), to close the "restart after flip" escape hatch.

---

## Appendix: engine-verification notes

- All moves submitted via direct `GameEngineV2.step_simultaneous(a1, a2)` calls using `/tmp/play_sim.py` (custom runner). The stock `play_helper.py --action play` treats simultaneous moves as sequential alternations and does NOT correctly exercise collision / simultaneous-CA semantics; it should not be used for these games.
- Illegal moves were flagged and replaced with an alternative legal placement, noted inline in the game transcripts.
- Engine behavior confirmed via three micro-tests:
  - P1(3,3) + P2(4,3) → round-1 CA flips P1's stone to P2 (validates `1,0,1→2`).
  - P1 plays (3,3)(4,3)(3,4) over 3 rounds → CA births (4,4) on round 3 (validates `0,2,0→1`).
  - CA runs on P2-only placements: no births, no conversions (validates CA asymmetry: steps_per_turn=1 → always P1 perspective).
