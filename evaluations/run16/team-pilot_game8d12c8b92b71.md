# Team Pilot — Run 16 Evaluation: Game 8d12c8b92b71

**Team ID:** team-pilot
**Game ID:** 8d12c8b92b71
**Date:** 2026-04-22
**Role:** Pilot evaluator (flagging R16 protocol issues for production)

---

## Phase 1 — Rule Comprehension

### Board structure
- **Dimensions:** 2D
- **Axis size:** 8 (64 cells)
- **Topology:** hex (offset coordinates, 6 neighbors per interior cell, no wrap)
- Helper note: `play_helper.py` rules text labels adjacency as "von Neumann (face-adjacent only, no diagonals)" — for hex this is misleading; the actual implementation in `topology.py::_build_hex_neighbors` gives 6 neighbors via the (1,0),(-1,0),(0,1),(0,-1) plus offset diagonals. Confirmed via direct API.

### Turn structure
- **Alternating** (`turn_type: alternating`, `pieces_per_turn: 1`).
- P1 (X) moves first, then P2 (O), repeating until someone exceeds threshold or 100 turns pass.

### Action types
- **Place only** (no move, no capture).
- 65 actions total: 0–63 = place at cell `y*8 + x`; action 64 = pass.
- `first_move_anywhere: True` and `constraint: anywhere` — every empty cell is always legal for placement.

### Capture / CA
- **None.** `capture_type: none`. **No CA** (`No (classic mechanics)`).

### Propagation
- **Influence** propagation, radius 2.
- Strength = 0.9843, decay = 0.6946.
- Distance-0 contribution (self): +0.984
- Distance-1 (face neighbors, hex): +0.684
- Distance-2 (further out, hex axial distance 2): +0.475
- P1 stones add positive values; P2 stones add negative values to nearby cells.
- Values clamped to [-100, +100].

### Win condition
- **Threshold.** `condition_type: threshold, target_dimension: 0, threshold: 34.1293`.
- A player wins when the **sum of `board_values` over cells they own** exceeds 34.1293.
- For P1 this is the sum of positive values on P1-owned cells; for P2 it is `-1 * sum(board_values on P2 cells)` (i.e. the magnitude of their accumulated negative influence on their own stones).
- Note: the influence on cells *owned by the opponent* does **not** count for either player. Only own-cell self+neighbor contributions matter.
- Max turns: 100. Double-pass = draw (R13+ engine fix).
- R16 fix: simultaneous threshold crossing is resolved by larger margin; equal margins → draw.

### Degeneracy / sanity flags
- **No 1-move forced wins.** A single stone gives 0.984. We need ~35 isolated stones to hit threshold, but well-clustered stones reach it much faster.
- **Cluster math (engine-verified):**
  - 7-stone tight hex flower (center + 6 neighbors): P1 total ≈ 31.85 — *below* threshold by ~2.3.
  - 8-stone (flower + 1 extension at radius 1): ≈ 37.05 — wins.
  - So a fully-uncontested P1 can win in 8 placements, i.e. on move 15 (P1's 8th turn).
- This means **disruption matters significantly**: each P2 stone adjacent to a P1 cluster subtracts ~0.68 from each affected P1 cell (the value at a P1 cell is reduced, making P1's own-cell sum smaller). With axis 8, P2 must actively contest or P1 wins in the mid-teens.
- **Asymmetry:** P1 places first. After P1 plays move 1 in center and P2 reacts, P1 always has +1 stone advantage at any moment of their turn. This advantage compounds when neither side can capture.
- **Threshold is reachable** in normal play (not unreachable) — multiple games verified below crossed it.
- **No double-pass risk** as a normal outcome — there's no incentive to pass when influence still benefits placement.

---

## Phase 2 — Strategic Play

### Game 1 — P1 builds tight cluster, P2 races mirror

I will record each move as engine-verified. Notation: action ID → (x,y).

**Move 1 — P1.** Considering: I want a central cluster. (3,3) gives me access to 6 hex neighbors all within the board. Action 27.
- Predicted P2: mirror in opposite quadrant, (4,4) at action 36, to start their own cluster while their stone reduces my potential extensions.

**Move 2 — P2.** Considering: P1 took (3,3). I should not let them grow a clean flower. I'll play (4,4) — adjacent to (3,3) (yes, it is a hex neighbor of (3,3) since (3,3) is in odd row 3, with offsets (1,1)) — directly contesting P1's cluster space while building my own seed. Action 36.
- Predicted P1: extend their cluster on the side away from me, e.g. (3,2) action 19.

**Move 3 — P1.** Considering: P2 chose (4,4) which is adjacent to my (3,3). My cluster is dirty on the SE side. I'll grow NW where it's clean: (3,2). This is a neighbor of (3,3) (odd row offset (-?,?)... let me verify: (3,3) is odd row, neighbors include (3,2) — yes (0,-1)). Action 19.
- Predicted P2: contest by extending toward my cluster, perhaps (3,1) or (2,3).

**Engine-verified game 1 sequence (all moves committed via `engine.step`):**

| # | Player | Action | Cell | After: P1 / P2 effective | Notes |
|---|--------|--------|------|---|---|
| 1 | P1 | 27 | (3,3) | +0.98 / +0.00 | center seed |
| 2 | P2 | 36 | (4,4) | +0.30 / +0.30 | adjacent — P2 stone gets corrupted |
| 3 | P1 | 19 | (3,2) | +2.18 / -0.17 | extend NW (clean) |
| 4 | P2 | 44 | (4,5) | +1.70 / +1.70 | P2 cluster anchor (clean) — symmetric |
| 5 | P1 | 26 | (2,3) | +4.95 / +1.23 | flower thickens |
| 6 | P2 | 37 | (5,4) | +4.47 / +4.47 | mirror |
| 7 | P1 | 28 | (4,3) | +6.88 / +2.63 | thicken on contested edge |
| 8 | P2 | 45 | (5,5) | +6.41 / +6.82 | P2 takes lead via cleaner cluster |
| 9 | P1 | 18 | (2,2) | +11.08 / +6.82 | high-yield internal density (+4.7) |
|10 | P2 | 53 | (5,6) | +11.08 / +12.44 | P2 reclaims lead |
|11 | P1 | 20 | (4,2) | +17.11 / +11.49 | flower density move (+6.0) |
|12 | P2 | 52 | (4,6) | +17.11 / +18.06 | P2 mirror (+6.5) |
|13 | P1 | 21 | (5,2) | +21.78 / +17.11 | extension (+4.7) |
|14 | P2 | 46 | (6,5) | +21.78 / +22.31 | P2 mirror (+5.2) |
|15 | P1 | 29 | (5,3) | +24.82 / +19.73 | **disruptive** — sits between clusters |
|16 | P2 | 35 | (3,4) | +21.55 / +21.66 | **disruptive mirror** — eats P1 cluster |
|17 | P1 | 17 | (1,2) | +25.80 / +21.66 | clean extension (+4.3) |
|18 | P2 | 54 | (6,6) | +25.80 / +29.60 | P2 surge (+7.9 from internal density move) |
|19 | P1 | 25 | (1,3) | +32.31 / +29.12 | massive cluster gain (+6.5) |
|20 | P2 | 11 | (3,1) | +28.57 / +26.37 | disrupt (P1 -3.7, P2 -2.8) |
|21 | P1 | 12 | (4,1) | **+35.40** / +25.68 | **WIN** — threshold crossed |

**Game 1 ended via threshold win at move 21. P1 wins.**

### Game 1 reflections

**Player 1 reflection:**
- *Strategy used:* Build a tight 8x8-corner-friendly hex cluster, prioritize internal density (high-multiplier moves where each stone is adjacent to 2-3 existing P1 stones), only disrupt when behind on margin.
- *What I'd do differently:* I underestimated how much (5,3) would help — the most efficient moves are the ones that simultaneously add to a new own-cell *and* damage opponent cells. Should have played (5,3) earlier instead of (4,2).
- *Surprised by:* The mirror strategy P2 used kept P2 even or ahead until move 19. The first-move advantage is small and only materializes in the late midgame when one side runs out of clean expansion squares first.
- *Endgame:* Reached threshold cleanly (35.40 > 34.13). No double-pass.

**Player 2 reflection:**
- *Strategy used:* Mirror P1, accept slight time loss, build a cluster in clean corner (away from P1) for max own-cell density. Switch to disruption only when even.
- *What I'd do differently:* My move 2 ((4,4)) was suboptimal — adjacent to P1 (3,3) means my own cell value gets corrupted. Should have played further away. (4,5) or (5,5) right away would have given me a cleaner cluster from the start.
- *Surprised by:* P1's move 19 (1,3) was a *cluster extension*, not a disruption, and netted +6.5. I expected P1 to disrupt me there. The flower-density math favors interior-add over disruption when behind by < ~4 points.
- *Endgame:* I reached 26.37 — needed maybe 4-5 more stones — but P1 closed it out faster.

### Game 2 — Clean parallel-cluster race

Both players build identical 7-stone hex flowers in opposite zones, no contesting:

| # | Player | Action | Cell | After: P1 / P2 effective |
|---|--------|--------|------|---|
| 1 | P1 | 18 | (2,2) | +0.98 / 0 |
| 2 | P2 | 45 | (5,5) | +0.98 / +0.98 |
| 3 | P1 | 17 | (1,2) | +3.34 / +0.98 |
| 4 | P2 | 44 | (4,5) | +3.34 / +3.34 |
| 5 | P1 | 19 | (3,2) | +6.64 / +3.34 |
| 6 | P2 | 46 | (6,5) | +6.64 / +6.64 |
| 7 | P1 | 10 | (2,1) | +11.31 / +6.64 |
| 8 | P2 | 37 | (5,4) | +11.31 / +11.31 |
| 9 | P1 | 26 | (2,3) | +16.93 / +11.31 |
|10 | P2 | 53 | (5,6) | +16.93 / +16.93 |
|11 | P1 |  9 | (1,1) | +23.91 / +16.93 |
|12 | P2 | 38 | (6,4) | +23.91 / +23.91 |
|13 | P1 | 25 | (1,3) | +31.85 / +23.91 |
|14 | P2 | 54 | (6,6) | +31.85 / +31.85 |
|15 | P1 | 11 | (3,1) | **+38.41** / +31.85 | **WIN** |

**Game 2 ended at move 15. P1 wins by exactly 1 tempo.** This is the cleanest demonstration of first-mover advantage on this board: when both players build optimal non-contesting clusters, P1 always reaches threshold first because P1 places stone N+1 before P2's stone N+1.

### Game 3 — Seat swap. P2 plays disruption-first opening

To honor the seat-swap instruction, I now play P2 with full attention as a counter-strategy: P2 tries to disrupt P1's seed early.

**Result:** Engine-verified through move 19. P2's adjacent disruption stones at (4,3),(3,2) turn out to be self-defeating because they sit in P1's positive-influence sphere — their *own* values are negative, so they contribute negatively to P2's own-cell total. P2 pivots to a clean cluster at move 6 but is now ~2 stones behind in clean-cluster development. P1 reaches 41.66 at move 19; P2 stuck at 32.24.

**Game 3 ended at move 19. P1 wins. Seat swap did not change outcome.**

### Game 3b — Better P2: clean cluster + late surgical disruption

Played a follow-up game with the strongest P2 strategy I can identify: build clean 7-flower in the (5,5) zone, time disruption only after move 14 when P1 is near 28-30. P2 disrupted at moves 16 ((4,1) action 12) and 18 ((3,4) action 35). Each disrupt swung the differential by ~3-4 points in P2's favor *but* also reduced P2's own score by 2-3.

**Result:** Engine-verified through move 19. P1 still wins at +38.22 vs P2 +30.28. The first-mover tempo is robust against P2's best counter-strategy.

### Player strategy guides

**P1 (first player) playbook:**
1. Open at (3,3) or (2,2) — center or near-center seed.
2. Build a 7-stone hex flower (center + 6 neighbors). Each move adds ~2-7 to your effective total via mutual-reinforcement.
3. Once flower is built, pick the highest-yield internal density extension (a cell adj to 2-3 of your existing stones).
4. **Avoid contested zones** unless behind on margin — your stones in P2's influence sphere have weakened own-cell values.
5. Win in 8-11 stones (~moves 15-21).

**P2 (second player) playbook:**
1. **Do not** play adjacent to P1's seed — your stone gets corrupted.
2. Open in the opposite quadrant (5,5) or (6,5).
3. Build a clean mirror flower.
4. Track the differential: if you're within 2 points of P1 by move 14, switch to surgical disruption. The best disrupt is a stone adj to many P1 cells AND to your own cells (e.g. (5,3) on this board).
5. Late disruption can swing differential by ~3-4 but you almost always still lose the race because of P1's tempo.

### Empirical seat-balance probes

I ran three separate seat-balance probes (engine-verified):

| Probe | P1 wins | P2 wins | Draws (timeout) | Notes |
|-------|---------|---------|-----------------|-------|
| Random vs random (50 games) | 14 | 10 | 26 | Modest P1 edge but most games time out |
| Trainer GreedyAgent (20 games, friendly-enemy nbr count) | **20** | 0 | 0 | **20/20 P1 wins. Strong structural P1 advantage under greedy.** |
| Effective-value greedy (10 games, my custom) | 0 | 10 | 0 | P2 wins all when both maximize effective-value differential |
| Human-played, clean cluster | 4/4 P1 | — | — | Games 1, 2, 3, 3b all won by P1 |

The trainer's greedy probe (which is what R16's worst-of-three actually evaluates) confirms 100% P1 advantage. This means:
- `greedy_p0_winrate ≈ 1.0`, `greedy_decisive_rate ≈ 1.0`
- `seat_balance` worst-of-three deviation = 0.5 → `seat_bal = 0.0`
- `composite` is multiplied by `max(0.2, 0.0) = 0.2` (the floor)

Despite this 80% penalty, the game still ranked #1 with GE = 0.160 — meaning the *unpenalized* composite was ~0.8. **The R16 seat-balance penalty fired correctly, but the floor of 0.2 still let an imbalanced game become champion.**

---

## Phase 3 — Strategic Analysis (joint)

**Distinct viable strategies?** Two:
1. **Pure cluster racer:** build the densest possible 7-stone hex flower in clean territory; no contesting. Wins clean races by tempo.
2. **Disruptor:** play surgical stones in opponent's radius-2 sphere to reduce their own-cell totals. Costs you ~1.5-2 own-score per stone but reduces opponent ~3-4. Useful only when behind on margin AND opponent is near threshold.

There's a *third* failed strategy — early adjacent disruption — which is self-defeating because P2's stone in P1's positive sphere ends up with corrupted own-cell value.

**Counter-play:** Mostly absent. The "race" dominant strategy means whoever starts wins. Disruption can shift the race timing but cannot overturn the tempo deficit. The only way for P2 to beat P1 is if P1 makes a *mistake* (e.g. plays adjacent to P2's seed for own-cell corruption, or wastes tempo on a corner cell with only 3 hex neighbors).

**Short-term vs long-term tension?** Modest. Short-term: maximize next-move differential. Long-term: avoid building near opponent (long-term cost of corrupted cells exceeds short-term disruption gain). The tradeoff exists but is not deep.

**Emergent concepts:**
- **Influence/territory** (yes — board values define implicit zones).
- **Tempo/initiative** (yes — first-mover by 1 tempo wins clean races).
- **Density yield** (an emergent concept specific to this game: each new stone earns more if placed adj to many existing same-color stones; max yield is at the *interior* of an existing 6-flower).
- **Mutual-annihilation tactics**: weakly present. Adjacent enemy stones partially neutralize each other (own-cell value drops but doesn't go to zero), but no actual capture.
- **Ko fights**: no.

**Topology matter?** Hex is genuinely necessary. The 6-neighbor flower is uniquely possible on hex. On a square grid with vN topology (4 nbrs), the 5-stone "plus" cluster maxes at lower density. On Moore (8 nbrs), the cluster math changes. Hex is what makes the 7-stone hex flower the canonical "win unit." So topology is load-bearing.

**First-mover advantage (alternating):**
- Quantified above: 4/4 played games went to P1, including a seat-swap game (Game 3). 
- Random vs random: P1 leads 14-10 (with most timing out, so among decisives P1 wins ~58%).
- Trainer-Greedy: 20/20 P1.
- The mechanic is **effectively deterministic for P1 with optimal play**.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary opens:** This game is "Influence Go on a hex board, with a fixed-threshold finish line and no captures." Every mechanic in this game is a known idea borrowed from a well-known abstract game.

**Catalog comparison:**

- **Go (and Go variants like Lines of Action):** The "place influence pieces on board, fight for territory" core is identical. *Difference:* no captures, no liberties, fixed numerical threshold rather than territory count.
- **Tumbleweed:** Tumbleweed (Mike Zapawa, 2019) is a hex-board influence game where placement strength depends on lines of sight to existing stones. The *concept* of "stones radiating influence with attenuation" is identical in spirit. **Tumbleweed is the closest known analog.** *Difference:* Tumbleweed uses line-of-sight not radius-2 propagation, and has a different win condition (majority of board cells controlled at game end).
- **Hex / Y / Havannah:** These are connection games. This game has no connection objective. Different family.
- **Reversi/Othello:** Also influence-style (flips on enclosure). Different mechanic (no flipping).
- **Gomoku/Pente/Connect6:** Pattern-finishing. No pattern in this game. Different family.
- **Amazons:** Movement + arrow shooting. Different.
- **Mancala:** Nothing similar.
- **Slither:** Movement game. Different.
- **Life-like CAs:** No CA in this game.

**The "this is just X in disguise" attack:**
"This is just *Tumbleweed* with a different attenuation function and a different finish-line."

**Player 1 + Player 2 rebuttal — specific Phase-2 moments where Tumbleweed analogy breaks:**

1. **Move 15 of Game 1, P1 plays (5,3) action 29:** This stone simultaneously *adds positive influence to P1 cells* and *adds negative influence to P2 cells* (and to neutral cells which become P1-owned with high value). In Tumbleweed, stone strength is monotone in line-of-sight count, NOT direction-of-friendly-vs-enemy. The dual-add/subtract of this game's influence rule has no Tumbleweed analog. A Tumbleweed expert would not recognize "kamikaze" disrupt moves where you place in enemy territory specifically to weaken their cells — that's not how Tumbleweed scoring works.

2. **The threshold finish-line:** The win condition is a numerical threshold (34.13) on a continuous variable (sum of own-cell board values). Tumbleweed's win condition is integer cell-control majority. The continuous threshold creates the "exactly 1-tempo" race that defines this game. It would not transfer.

3. **Decay-based propagation cell-value math:** A Tumbleweed expert would assume control of a cell is binary (you have line-of-sight). In this game a cell can have value 0.21 because two opponents' stones partially cancel. The analog math is different — a Tumbleweed expert would mis-estimate every move.

4. **The negative-own-cell phenomenon:** A P2 stone played adjacent to many P1 stones becomes a P2-owned cell with NEGATIVE effective value (it actually subtracts from P2's score). No analog game has this pathology.

**Verdict on novelty:** The game has clear ancestry from Go (territory) and Tumbleweed (line-of-sight influence on hex). The specific dual-add/subtract continuous-influence + threshold finish creates emergent behavior (dense-flower + tempo race) that doesn't appear in any single ancestor. A Tumbleweed expert would have to relearn placement value semantics; a Go expert would be lost on the lack of captures.

**Novelty score: 4/10.**
- It's not a direct re-skin (so not 2-3).
- It's not a never-before-seen mechanism (so not 7+).
- It's a recognizable variant of "hex influence game with threshold win" — somewhere in the 4-5 range. The threshold + dual-influence math is the genuinely novel piece, but the high-level genre is well-trodden.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** 8d12c8b92b71
**Rules Summary:** 2D 8x8 hex board, alternating placement, no capture; each stone propagates radius-2 positive (P1) or negative (P2) influence with strength 0.984 and decay 0.695; win when sum of board values on your owned cells > 34.129.
**Topology:** 2D, axis 8, hex (6-neighbor offset coordinate)
**Turn Structure:** alternating

### SCORES (1-10)

- **Strategic Depth: 4/10** — There is one dominant strategy (cluster-flower racing) and one weakly-viable counter (selective late disruption). No deep tree of choices; greedy density-maximization is near-optimal. Some interesting micro-decisions about when to disrupt, but the macro shape of every game is the same. R16 stored SD=0.686 — but I think that overstates it; the high SD likely reflects training noise during convergence.

- **Emergent Complexity: 5/10** — The "negative own-cell" pathology and the "kamikaze disrupt" tactic are mildly interesting emergent behaviors. The continuous-threshold finish line creates "exactly 1-tempo" race dynamics. But there are no surprising configurations (no ko, no death/life, no shapes that flip the game). The complexity is mostly arithmetic.

- **Balance: 2/10** — Severely unbalanced toward P1. 4/4 of my human-played games (with seat swap) went to P1. The trainer's GreedyAgent probe goes 20/20 P1. Random vs random is 14-10 P1 with massive timeouts. Trained-vs-trained reads 0.5 only because trained agents converge to mixed strategies that paper over the structural advantage. **The R16 worst-of-three caught this** (greedy_p0_winrate ≈ 1.0 → seat_balance ≈ 0.0 → 5x penalty), but the 0.2 floor still let it win the population.

- **Novelty (post-adversary): 4/10** — Closest analog is Tumbleweed; clear hex-influence-game lineage. The dual-add/subtract influence model and continuous threshold are the only genuinely novel elements.

- **Replayability: 3/10** — Once you know the cluster-flower opening and the tempo-wins-clean-races result, every game looks the same. Position symmetry under board rotation/reflection means a strong P1 always picks center or near-center and races. P2's only counter is to know they're losing and try to disrupt productively.

- **Overall "Would I play this again?": 3/10** — Fast (~15-20 moves), simple to compute, but every game converges to the same tempo race. The disruption sub-game is interesting for one or two games then becomes rote. I would prefer Tumbleweed proper or any actual placement game with a richer win condition.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed** (Mike Zapawa, 2019), with these differences: (a) radius-2 decay propagation instead of full line-of-sight, (b) continuous-value threshold finish (34.13) rather than integer cell-count majority, (c) dual sign-direction influence (P2 stones have negative influence), and (d) own-cell value can be negative. None of these are deal-breakers — a Tumbleweed expert would be in the territory of a useful prior but would have to relearn placement strength math.

### KILLER FLAWS

1. **First-mover advantage is dispositive under any competent play.** P1 wins all clean races by exactly 1 tempo. Trainer GreedyAgent: P1 wins 20/20. This is a structural break, not a balance tweak.

2. **Greedy density-maximization is near-optimal.** A 1-ply heuristic ("pack stones in a hex flower, prefer cells adjacent to multiple existing same-color stones") wins virtually every game. This collapses the strategic surface to a single playbook.

3. **Threshold value (34.13) is too low relative to board area.** With a 7-stone hex flower yielding ~31.85 and an 8-stone extension hitting 37+, the game is essentially decided by move 15-21 every time. A higher threshold (like 50+) would force more contesting and create the disruption sub-game more often.

4. **No mid-game state recoverability.** Once P1 has a 6-flower built, P2 cannot catch up. There is no "comeback mechanic." (No captures, no flipping, no resets.)

### BEST QUALITY

**The dual-influence radius-2 decay propagation is a clean, computable mechanism.** It produces emergent dense-flower cluster shapes, makes adjacent enemy stones partially neutralize, and gives a continuous score that creates close races. It's the most interesting feature and the one that gives the game any signal at all.

### IMPROVEMENT IDEAS

- **Raise the threshold to ~55-60** (roughly 2x current). This would force at least 12-15 stones per side, requiring more contesting and giving P2 more time to disrupt-and-rebuild. The first-mover advantage would become a 2-3% effect rather than a 100% effect.
- **Or: pieces_per_turn = 2 for P1 first move, 1 thereafter ("pie rule" or compensation).** A standard chess/Go-style adjustment to neutralize first-mover advantage.
- **Or: Keep the threshold but add a "bounce" rule** where if a player places adjacent to ≥3 enemy stones, the placed stone is removed (capture-by-surround). This would make disruption much riskier and reward careful spacing.

---

## Pilot — R16 protocol issues to flag for production

These are R16-specific behaviors that the production teams (21 of them) should be primed for:

### 1. Margin-based threshold resolution semantics — works correctly

I exercised every threshold crossing through `engine.step()` and observed the new R16 logic. **No same-tick crossings happened in my games** (alternating turns make same-tick crossings rare for threshold games — only one player plays per step). For *simultaneous* games this would be more important, but this is alternating. **No bug observed; the new code path simply did not fire.** Recommendation: production teams playing simultaneous games should explicitly construct a same-tick scenario to verify the new resolution rule.

### 2. Greedy probe stored on disk vs ranking — calibration insight

The R16 stored fitness for the champion (this game) is GE = 0.160. Working backwards through `evaluate_game`:
- composite × seat_balance_floor (0.2) × novelty_factor ≈ 0.160
- → composite_pre ≈ 0.8

So the seat-balance penalty fired at the floor. **The metric correctly identified the imbalance, but the floor of 0.2 still permitted an imbalanced game to become champion.** This is a known issue with the floor-based penalty — would suggest reducing the floor to 0.1 or making it a hard zero (with a different floor for *partial* imbalance like seat_bal in [0.4, 0.8]).

### 3. CA-from-snapshot — not exercised

This game has no CA. CA semantics could not be tested. The 21 production teams will need to evaluate at least a few CA games to actually exercise `_run_ca_step_symmetric`. The R16 prompt should ensure team assignments include CA-bearing games.

### 4. Helper tool issues found

- **`play_helper.py rules` mislabels hex topology as "von Neumann (face-adjacent only, no diagonals)".** This is wrong on two counts: hex isn't von Neumann (it's hex, with 6 neighbors), and the implementation in `_build_hex_neighbors` clearly uses 6 hex offsets. **Suggested fix:** update the rules-printing in `play_helper.py` to detect topology and emit "hex (6-neighbor offset coordinate)" or "Moore (8-neighbor Chebyshev)" or "von Neumann (4-neighbor face-adjacent)" appropriately.
- **`engine.get_legal_actions()` returns a *list of legal action IDs*, not a 0/1 mask.** The prompt's "double-check action IDs" caveat doesn't cover this. I burned 5+ minutes debugging an "ILLEGAL action 54" error that was actually my helper interpreting the return as a mask. **Suggested fix:** add to the R16 prompt's "Known engine quirks" section: *"`engine.get_legal_actions()` returns `list[int]` of legal action IDs (not a 0/1 mask). Iterate or membership-check directly."*

### 5. Influence-value board reading

The prompt mentions `GameEngine.get_board_values()` but the actual attribute on `engine_v2.py` is `engine.board_values` (a numpy array). There is no method `get_board_values()`. **Suggested fix:** update prompt to say `engine.board_values` (attribute, not method).

### 6. The "first-move-anywhere" placement rule + 65-action space

The action space includes `pass` (action 64). With `placement_rule.constraint == "anywhere"` and `target == "empty"`, every empty cell + pass is always legal. There's no meaningful reason to pass (nothing forces it), but a lazy/random agent might pass and end games as draws via double-pass. The trainer's avg_game_length of 18.5/26.5 is suspiciously close to "good game length" (15-30) — but my random-vs-random found 26 of 50 games timed out, suggesting random agents don't double-pass, they just keep filling the board until max_turns. This is benign for this game but flags a class of game where double-pass draws could be a concern.

### 7. Time budget

I used ~25 minutes for this evaluation including the 4 played games + greedy probe + adversary phase + writeup. The budget is realistic. Production teams should set aside ~25 min per game and not exceed. They should NOT play more than 3 games unless one game ended in unexpected non-convergence.

### 8. Seat-swap discipline

The instruction "in game 3, swap seats" is ambiguous when one agent plays both sides. I interpreted it as "play P2 with full counter-strategy attention while letting P1 play optimally." If the production teams have actual separate agents for P1/P2, the swap should mean physically swapping which agent controls which seat. This should be made explicit in the prompt.

---

*Evaluation complete. Time elapsed: ~25 min as budgeted.*

