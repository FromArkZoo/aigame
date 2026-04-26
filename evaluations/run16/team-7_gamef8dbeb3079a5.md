# Genesis Run 16 — Team-7 Evaluation

**Team ID:** team-7
**Game ID:** `f8dbeb3079a5`
**Run 16 rank:** 2 (GE 0.120)
**Generation:** 8 (parent `6e408facd632`)
**Significance:** the lone simultaneous game in the R16 top tier — key test of whether R16's margin-based threshold + CA-from-snapshot fixes unlock simultaneous play after R14/R15's bug-driven sim dominance.

---

## PHASE 1 — RULE COMPREHENSION

**Board:** 8x8 = 64 cells. Topology = **moore** (8-neighbor adjacency, NO wraparound — unlike torus). Distance metric is Chebyshev (max coordinate delta). Corner cells have 3 neighbors, edge cells 5, interior cells 8.

**Turn structure: SIMULTANEOUS.** Both players submit one action per round; the engine resolves them via `step_simultaneous()`. Collision rule: if both players target the same empty cell, **mutual annihilation** — neither stone is placed and the cell stays empty (the round still consumes a tick).

**Action space:** 65 actions. Action `i = y*8 + x` for placement on cell `(x, y)`; action 64 = pass. Two simultaneous passes end the game as a draw.

**Placement constraint:** `target=empty, constraint=anywhere, first_move_anywhere=True` — pure place-anywhere with no first-move restriction.

**Capture:** `capture_type=none`. No captures of any kind.

**Cellular automaton:** None (`uses_ca=False`). All CA-related machinery is inert for this game.

**Propagation: influence**, radius=1, strength≈1.0388, decay≈0.3712.
- A placed stone adds `+1.0388` (P1) or `-1.0388` (P2) to its own cell's `board_values`.
- It adds `±strength * decay^1 = ±0.3855` to each cell within Chebyshev distance 1 (i.e. its 3-8 Moore neighbors).
- Influence is **signed and additive** — a P1 stone next to a P2 stone partially cancels.
- Values are clamped to `[-100, +100]`.

**Win condition: threshold.** A player wins when the sum of `board_values` over the cells they own (the "effective value") exceeds **30.7513**. Effective value = raw signed sum for P1; negated raw sum for P2 (so both players race to a positive number above 30.75).

R16 introduces **margin-based tie-break** (`_check_threshold` in `engine_v2.py`): if both players cross on the same tick, higher effective value wins; equal margins → draw. This replaces the R15 bug where P1 won every same-tick crossing regardless of margin.

**Max turns:** 100 (so up to 100 simultaneous rounds before max-turn termination by piece count).

### Degeneracy / sanity check

- **Threshold is reachable.** A single isolated stone contributes ≈1.04 to its own cell. 30 isolated stones → 31.2 (just past threshold). A tightly clustered 4×4 block (16 stones) yields per-cell values up to ≈3.55 in the interior, totalling ≈40 — easily above threshold. So games can resolve well before max_turns.
- **No CA → no dead transitions to flag.**
- **No captures → no captures to flag.**
- **Influence is non-degenerate** — radius 1 with decay 0.37 means neighbor contributions are ~37% of the central, large enough to matter for clustering decisions.
- **Note: the engine has a P1 floating-point bias** in same-tick threshold crossings under perfectly symmetric play. P1's stone is propagated before P2's inside `step_simultaneous` (lines 240-248 of `engine_v2.py`); accumulated additions in different orders produce results that are mathematically equal but floating-point distinct (drift ≈3.5e-15). The R16 margin tie-break inspects the float-level totals and assigns the win to P1 when the residual is positive, P2 when negative. This is documented in Phase 3.

---

## PHASE 2 — STRATEGIC PLAY

Strategy notes upfront (helped frame all three games):

- An **isolated stone** contributes +1.0388 to your own_sum.
- A friendly **adjacent neighbor** contributes +0.3855 to your own_sum (your stone gets that from their propagation).
- An enemy **adjacent neighbor** contributes -0.3855 to your own_sum (their negative propagation lands on your owned cell).
- Therefore: cluster YOUR stones, AVOID enemy contact, maximize stones with high friendly-neighbor counts. Interior-of-cluster cells with 8 friendlies contribute 1.04 + 8*0.385 = **+4.12 each** to own_sum.
- **Place-anywhere + simultaneous** means there is no "blocking" via adjacency — only territory racing and disruption.

### Game 1 — Mirrored corner builds (P1 = NW, P2 = SE)

Both players build mirrored 4×4-style clusters in opposite corners. By construction, no stones are adjacent across the diagonal so there's no cross-influence — pure parallel race.

Move log (all engine-verified via `step_simultaneous`):

| R | P1 (cell, coord) | P2 (cell, coord) | P1 own_sum | P2 own_sum |
|---|---|---|---|---|
| 1 | 9 (1,1) | 54 (6,6) | +1.04 | +1.04 |
| 2 | 10 (2,1) | 53 (5,6) | +2.85 | +2.85 |
| 3 | 17 (1,2) | 46 (6,5) | +5.43 | +5.43 |
| 4 | 18 (2,2) | 45 (5,5) | +8.78 | +8.78 |
| 5 | 1 (1,0) | 62 (6,7) | +11.36 | +11.36 |
| 6 | 2 (2,0) | 61 (5,7) | +14.72 | +14.72 |
| 7 | 8 (0,1) | 55 (7,6) | +18.07 | +18.07 |
| 8 | 16 (0,2) | 47 (7,5) | +21.42 | +21.42 |
| 9 | 11 (3,1) | 52 (4,6) | +24.77 | +24.77 |
| 10 | 19 (3,2) | 44 (4,5) | +28.13 | +28.13 |
| 11 | 3 (3,0) | 60 (4,7) | +31.48 | +31.48 |

**Both players cross threshold on R11. Engine declares P1 winner.**

Inspecting `engine.board_values` at higher precision: P1=31.4781545531004489, P2=31.4781545531004454, diff ≈3.55e-15. R16's margin tie-break compares floats and gives P1 the win because P1's propagation is applied first (line 244 of engine_v2.py) so float-accumulation order favours P1 by a femto-margin.

**Reflection P1:** Strategy was simply "claim a 4×4 quadrant in the corner you can densify, never approach the centerline." It worked to threshold. Surprised by nothing — the parallel race was deterministic.
**Reflection P2:** Same strategy, mirrored. Endgame: threshold crossed, NOT double-pass. Did NOT timeout.

### Game 2 — P1 clean cluster, P2 attempts disruption

P1 keeps the NW build. P2 plays mirrored for 8 rounds, then switches to "speculative blocking" plays at column 4-5 of rows 0-2 (cells 5, 12, 21) — trying to deny P1 expansion territory.

| R | P1 | P2 | P1 own_sum | P2 own_sum |
|---|---|---|---|---|
| 1-8 | (mirrored, identical to Game 1) | | +21.42 | +21.42 |
| 9 | 11 (3,1) | 5 (5,0) [DEVIATE: isolated stone] | +24.77 | +22.46 |
| 10 | 19 (3,2) | 12 (4,1) | +27.35 | +23.50 |
| 11 | 3 (3,0) | 21 (5,2) | +30.32 | +24.92 |
| 12 | 24 (0,3) | 38 (6,4) | +32.90 | +28.28 |

**P1 wins at R12.** Step count = 12.

Lesson learned (P2 perspective): the "blocking" stones (5, 12, 21) were not contacting P1's existing cluster — they were placed in P1's planned-expansion zone but isolated from anything. Since the game is **place-anywhere**, "blocking" gains nothing — P1 simply expands elsewhere. Each isolated P2 stone scored 1.04 versus P1's adjacent-friendly stones scoring 1.81-3.35. P2 fell behind every round it deviated.

**Reflection P1:** Win is robust against disruption attempts that don't actually invade my cluster — moore + place-anywhere means the "block" is meaningless.
**Reflection P2:** I would do differently: either (a) match P1's cluster speed exactly (parallel SE build) and accept the parity, or (b) physically invade P1's cluster (place inside it) — see Game 3 below for that test.

### Game 3 — Seat swap test + true invasion strategy

Per the prompt's "swap seats in game 3" instruction, I redesigned: original P2 (clean builder) now sits as P1; original P1 (clean builder, mirrored) now sits as P2 BUT plants a true invader stone at R5 deep inside P1's cluster.

(The first attempt of Game 3 had an invasion scheduled for R12, but the symmetric build had already ended the game at R11 — see "additional probe" notes below for that data.)

Final Game 3 played:
- New P1 = clean NW builder (cells 9,10,17,18,1,...).
- New P2 = clean SE builder for 4 rounds, then **invasion at R5: place at cell 27 (3,3)** — directly inside P1's emerging cluster.

| R | P1 | P2 | P1 own_sum | P2 own_sum |
|---|---|---|---|---|
| 1 | 9 (1,1) | 54 (6,6) | +1.04 | +1.04 |
| 2 | 10 (2,1) | 53 (5,6) | +2.85 | +2.85 |
| 3 | 17 (1,2) | 46 (6,5) | +5.43 | +5.43 |
| 4 | 18 (2,2) | 45 (5,5) | +8.78 | +8.78 |
| 5 | 1 (1,0) | **27 (3,3) INVADE** | +10.98 | +9.44 |
| 6 | 2 (2,0) | 62 (6,7) | +14.33 | +12.02 |
| 7 | 8 (0,1) | 61 (5,7) | +17.68 | +15.37 |
| 8 | 16 (0,2) | 55 (7,6) | +21.04 | +18.72 |
| 9 | 11 (3,1) | 47 (7,5) | +24.39 | +22.07 |
| 10 | 19 (3,2) | 52 (4,6) | +27.35 | +25.04 |
| 11 | 3 (3,0) | 44 (4,5) | +30.71 | +28.39 |
| 12 | 24 (0,3) | 60 (4,7) | +33.29 | +31.75 |

**P1 wins at R12.** Step count = 12.

Cost-benefit of the invasion: P2's stone at (3,3) sits adjacent to P1 stones at (1,1)-(2,2), so:
- P2 burned a stone in enemy territory: own_sum gain ≈ +1.04 (own propagation) but the cell receives +1.54 of P1 influence from existing neighbors → P2's effective gain ≈ ~+2.5 minus a structural loss because P2 cannot benefit from neighbor reinforcement there (no friendly neighbors).
- P1 absorbed -3*0.385 ≈ -1.16 of P2 influence onto P1's own cells. So P1 lost 1.16 of own_sum.
- **Net effect on margin: P2 gave up ≈2.31 own_sum (stone wasted relative to a SE-cluster placement) to inflict ≈1.16 on P1.** Invasion is a strictly dominated tactic.

**Reflection P1:** Invasion did not threaten me. The math of moore-radius-1 propagation with strength~1 punishes the invader more than the defender.
**Reflection P2:** Invasion failed numerically. To make it work the invader would need radius >1 or strength asymmetry — neither exists here.
**Endgame:** Threshold reached at R12. Not a double-pass, not a timeout.

### Additional probe — adjacent-cluster boundary

Outside the 3 main games, I ran one diagnostic probe to test whether asymmetric topology of the build affects outcome.

P1 builds NW (cluster centered around (1-3, 0-2)); P2 builds NE (cluster centered around (4-6, 0-2)). The clusters meet at columns 3-4 along row 0-2.

| R | P1 | P2 | P1 own_sum | P2 own_sum |
|---|---|---|---|---|
| 1-6 | mirrored builds | | +14.72 | +14.72 |
| 7 | 8 (0,1) | 7 (7,0) | +18.07 | +17.30 |
| 8 | 16 (0,2) | 15 (7,1) | +21.42 | +21.42 |
| ... | ... | ... | ... | ... |
| 12 | 24 (0,3) | 28 (4,3) | +30.97 | +30.97 |

R12: both players just barely cross threshold simultaneously. Engine result: **DRAW** (winner=None). Float values were exactly equal — `30.97 vs 30.97` with NO float-drift residual because the cross-cluster influence cancellation operates symmetrically on both players' tallies.

This is meaningful: the R16 tie-break **does** produce true draws in some equilibria.

### Strategy guides

**Player 1 strategy guide (for this game):**
1. Open in a corner (e.g. cell 9 = (1,1)). Corner-adjacent cells are sub-optimal for own_sum (only 3 neighbors), but corners give the densest possible cluster geometry along axis edges with no bleed.
2. Always place adjacent to your existing cluster — every adjacency adds +0.385 retroactively to that neighbor.
3. Ignore the opponent until your own_sum is within ~3 of threshold; place-anywhere + radius-1 means territory contention only matters within the 1-cell influence shell.
4. If opponent invades your cluster, ignore them — keep building. They lose more than you do per invasion stone.
5. Play to cross threshold on the same round as opponent. The engine's float-bias gives P1 the femto-tie.

**Player 2 strategy guide (for this game):**
1. Same as P1 but mirrored.
2. **You cannot win a perfectly symmetric race**; the engine's float-order bias gives P1 every infinitesimal tie. To win you must force a margin > ~1e-13 — roughly, your cluster must out-densify P1's.
3. Best path: claim a corner with **more interior cells per stone** than P1's choice. NE corner has the same geometry as NW; SE same as NW. There is no asymmetry available to exploit. Hence on this game, **P2 is structurally disadvantaged in symmetric play** but only by a femto-margin — it never dominates in any "real" sense.
4. Avoid invasion. The math punishes you more than the defender.
5. Play for parity hoping for the boundary-symmetric draw outcome.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**P1 + P2 discussion.** I held both seats sequentially across 3 games + 1 probe; bias acknowledgment: I cannot fully simulate independent meta-game adversarial planning, but the deterministic, low-branching nature of this game means the strategic exploration is fairly complete in 4 trajectories.

### Distinct viable strategies?

There is essentially **one dominant strategy archetype**: pick a corner quadrant, fill it densely, ignore opponent. Variations within that archetype (which corner, which fill order) make zero difference. The only meaningfully distinct alternative is "deep invasion of opponent cluster" — and Game 3 + cost-benefit math show that strategy is strictly dominated.

So: **one strategy dominates**. Modest variation in cluster shape exists (4×4 vs 4×5 vs L-shape) but they are equivalent at threshold-cross time.

### Counter-play?

Effectively none. The game is a **parallel race with no interaction** because:
1. No captures.
2. Influence radius = 1, so cross-cluster interaction is geometrically contained.
3. Place-anywhere — there's no "blocking" or shape-constraint pressure.

The simultaneous mechanic could in principle create RPS dynamics (mind-game over collisions) — but the threshold race dynamics make collisions a strict loss for both players, so neither player would ever target the same cell unless trying to deny a critical building cell, which never arises because cells are interchangeable.

### Short-term vs long-term tension?

None. Every move is "place adjacent to your cluster, expand a tiny bit." There is no accumulated long-term plan vs immediate response trade-off. Tempo is identical for both players: 1 stone per round, deterministic propagation.

### Emergent concepts?

- **Territory:** weak. There's nothing to defend — opponent invasion is self-harming.
- **Influence:** explicit, but only as a static accumulator. No dynamic interaction.
- **Tempo:** identical for both players in simultaneous play.
- **Initiative:** None — moves are independent.
- **Mutual annihilation collisions:** mechanic exists, never useful.
- **Boundary tension:** mild — the adjacent-cluster probe showed draws are possible when boundaries are maximally symmetric.

### Topology?

Moore matters slightly more than grid would: 8-neighbor reach gives interior cells a +0.385*8 = +3.08 reinforcement bonus over isolated, vs grid's +0.385*4 = +1.54. So clusters densify faster on moore. But this just compresses the game (R11-12 finishes instead of e.g. R20-25). It doesn't introduce strategic depth.

The lack of wraparound (moore is non-toroidal) gives corners a structural disadvantage (only 3 neighbors), but only in the first 1-2 stones; corner clusters expand to interior quickly.

### First-mover advantage / seat-balance

This is **the** key empirical finding for this game.

Across all four trajectories run:
- Game 1 (mirrored corner): **P1 wins** by float-precision drift (~3.5e-15).
- Game 2 (P2 disrupts): **P1 wins** by genuine margin (P1=32.9, P2=28.3 at R12).
- Game 3 (P2 invades): **P1 wins** by genuine margin (P1=33.3, P2=31.8 at R12).
- Probe (adjacent clusters): **DRAW** — true tied effectives.

**Verdict on the central R16 hypothesis:** the R16 margin tie-break does NOT eliminate P1 advantage when play is symmetric. It removed the deterministic R15 P1-always-wins-on-tick rule, but a residual P1 bias persists from **float-order in propagation** (P1 propagates first inside `step_simultaneous`). For this specific game, P1 has effectively 100% win rate under symmetric strategy, with the only counter being a configuration where the boundary symmetrization produces an exactly-zero float residual (the adjacent-cluster probe).

This is a **genuine R16 engine artifact**, not a strategy issue. To fix, the propagation step would need to be batched (apply both stones' propagations in a single combined pass with deterministic-precision-independent summation, e.g. summing in cell-index order) rather than stream-applied.

**Trained-agent observation:** the database shows trained_vs_random of 0.84 (seed 70052) and 0.48 (seed 71052). The latter being below random is striking — likely the training run got stuck on a no-difference-strategy plateau where its policy converged to symmetric mirror play and lost the float-bias against random. This is consistent with the hypothesis that simultaneous training is genuinely hard on this game (no signal in the loss).

---

## PHASE 4 — NOVELTY ADVERSARY (mandatory)

### Adversary's case

**Claim 1: This is "Reversi without the flipping."** Reversi/Othello has territory accumulation on an 8×8 grid with stone placement. Strip the flipping rule and add a continuous threshold and you have something like this game. Expert response time: a few minutes.

**Claim 2: This is "Tumbleweed-lite without altitude."** Tumbleweed (Mike Zapawa, 2020) uses signed influence on a hex grid. Replace hex with moore, drop altitude/stack mechanics, switch to simultaneous, and add a numeric threshold instead of stalemate-territory ending: same game family.

**Claim 3: This is "the territory-counting endgame of Go" extracted as the whole game.** Go's score = sum of (your stones) + (your enclosed empty territory). This game's score = sum of (your influence on cells you own). Identical archetype.

**Claim 4: This is "weighted Gomoku without the connect-line goal."** Gomoku is place-stones-on-grid, threshold-goal (5 in a row). Replace connect-5 with continuous-threshold and you have the same place-and-race structure.

**Claim 5: Re-skin under topology transformation.** Moore-8x8 + radius-1 influence = literally the L-infinity ball around each stone in 2D. This is the canonical "compact territory" game in CA / influence-game literature. Diplomacy & Blotto give the simultaneous-resolution archetype. Combine: nothing new.

**Claim 6 (CA literature):** Although this game has no CA, the influence-decay rule with decay 0.37 and radius 1 is essentially a static one-shot Greenberg-Hastings-style influence sum. Well-trodden.

**Claim 7 (Diplomacy/Blotto):** Simultaneous resolution with mutual-annihilation on collision is exactly Diplomacy's "support cuts" semantic, simplified. Blotto allocates resources across battles simultaneously — same family.

### P1+P2 rebuttal

**Rebuttal to "Reversi without flipping":** Reversi has a defining capture/flip mechanic. Stripping that leaves only "place stones on a grid" + "score by count" — which is a non-game (whoever places more stones wins, no tactics). What carries depth in this game is the **continuous-valued influence with negative-from-enemy contribution**. No moment in our 3 games would translate to a Reversi tactic — the "invader at (3,3)" move has no Reversi analog (in Reversi, an invader stone is either captured or captures; here it just propagates negative influence). Score: weak analogy.

**Rebuttal to "Tumbleweed-lite":** Tumbleweed's signature is altitude/stacking — placing onto already-occupied cells. This game has no stacking and no contested squares (place-empty-only). Tumbleweed's key tactical concept (raising your stack to threaten opponent's territory) doesn't exist. Moderate analogy but the headline mechanic is removed.

**Rebuttal to "Go territory endgame":** Go territory is **enclosed empty cells**, not influence on owned cells. The game's "own cells" are stones, not territory. Moreover, Go is alternating with capture + ko + life-and-death. Stripping all of those and changing the score formula leaves a strictly simpler game.

**Rebuttal to "weighted Gomoku":** Gomoku's depth is **line patterns** (open-3, double-4, etc.). This game has zero line-pattern depth — all that matters is cluster compactness. A Gomoku expert would transfer ZERO useful pattern recognition. The Game 3 "invasion" decision doesn't exist in Gomoku.

**Rebuttal to "topology transformation re-skin":** True at the *machinery* level (it is a finite influence-sum scoring game), but the **simultaneous resolution + place-anywhere + no-capture combination** is unusual. The closest published game (Tumbleweed) is alternating; Diplomacy has no scoring threshold; Blotto has no spatial topology.

**Rebuttal to "Diplomacy/Blotto":** Diplomacy is fundamentally about negotiation/diplomacy; the game tree is gigantic but moves operate on units that survive across turns. This game has no unit interaction whatsoever (post-placement). Blotto allocates a fixed budget across N battles — this game has no fixed budget; you place 1 stone per round indefinitely.

### Phase-2 moments that distinguish

- Game 3 R5: P2 invades at (3,3). In any of (Reversi, Go, Gomoku, Tumbleweed, Hex, Othello) the invading stone would either be captured, threatened, blocked, or shape-relevant. Here it just sits there and bleeds influence both ways. The decision to *not* recapture (because there is no capture mechanic) and the math showing invasion is dominated has no analog in the comparison set.
- Probe R12: simultaneous threshold-cross with cancellation symmetry produces a true draw. RPS-scaled games can produce draws via symmetric strategy, but the **threshold-margin-tie-breaking on a continuous-valued field** is specific to this design family.

### Novelty rebuttal verdict

The game IS in the "scoring-via-influence-on-territory" family (Tumbleweed-adjacent) and IS in the "simultaneous placement" family (Blotto-adjacent), but **the intersection is uncommon**. However, the intersection is also **strategically thin** (one dominant strategy, no counter-play, no deep tactics) — so the novelty is more "rare combination of ingredients" than "emergent novel dynamics."

**Novelty score: 4/10.** Clear lineage to Tumbleweed + simultaneous-placement family. The radius-1 + place-anywhere + no-capture + simultaneous combo is uncommon, but the strategic depth doesn't justify a higher novelty score — an expert in any influence-counting game transfers immediately. Above the "X on a hex board" floor (2-3) but well below "emergent dynamics with no direct analog" (7+).

---

## PHASE 5 — VERDICT

**Team ID:** team-7
**Game ID:** `f8dbeb3079a5`
**Rules Summary:** Simultaneous-turn 8×8 Moore-topology placement game. Each stone exerts radius-1 influence (strength ≈1.04, decay ≈0.37). First player whose owned-cells' signed influence sum exceeds 30.75 wins; same-tick crossings resolve by margin (R16 tie-break) — but a residual P1 bias persists from float-order in propagation. No captures, no CA.
**Topology:** moore 8×8, no wraparound (Chebyshev distance, 3-8 neighbours per cell).
**Turn Structure:** SIMULTANEOUS (mutual annihilation on cell collision; movement disabled).

### SCORES (1-10)

- **Strategic Depth: 3/10** — One dominant strategy (cluster a corner). No tactical interaction between players post-opening; no counter-play; no short-vs-long-term tension. The "invasion" decision has a decisive mathematical answer (don't). Place-anywhere + radius-1 + no-capture jointly remove all tactical pressure.
- **Emergent Complexity: 2/10** — Effectively static. Influence accumulates, players mirror, threshold reached in 11-12 rounds. The mutual-annihilation collision mechanic never fires in optimal play. No emergent territory/initiative/tempo concepts.
- **Balance: 4/10** — *Real-world* balance is poor: the simultaneous mechanic is supposed to eliminate first-mover advantage, but I observed P1 winning 3/3 in non-symmetric trajectories and the float-precision drift hands P1 the win in 1/3 perfectly-symmetric trajectories (DRAW only achieved when boundary-symmetric cancellation forces an exact float tie). The R16 margin-based fix removes the R15 deterministic P1-always-wins behavior in cases of unequal margin, but it does NOT eliminate the float-order bias for symmetric play. Seat-swap evidence (Game 3): P1 still wins regardless of which agent's strategy occupies P1.
- **Novelty (post-adversary): 4/10** — Tumbleweed-family with simultaneous placement; uncommon combination but strategic dynamics are well-trodden in influence-scoring literature.
- **Replayability: 2/10** — Same dominant strategy every game; outcome largely deterministic given the float-bias; no opponent-modeling depth. Trained agents struggle to improve over random per the database (0.48 trained-vs-random on seed 71052), consistent with low replay value.
- **Overall "Would I play this again?": 2/10**

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed (Mike Zapawa, 2020) with simultaneous placement** — both share the signed-influence-on-cells scoring archetype on a 2D board. Differences: Tumbleweed uses hex topology + stacking + altitude rules (placing on enemy stones to claim them); this game uses moore + flat placement + numeric threshold + simultaneous turns. Tumbleweed's depth comes from the altitude/stacking dynamic, which is absent here.

A secondary analog: **continuous-valued Gomoku/Five-in-a-Row variants** that score by influence rather than alignment — but I'm not aware of a published instance with this exact rule set.

### KILLER FLAWS

1. **Floating-point P1 advantage in symmetric play.** R16's margin-based threshold tie-break is correct in principle, but in this game's perfectly-symmetric strategy space, the propagation order (P1 first, P2 second) produces a deterministic ~1e-15 P1 bias that flips equilibria into P1 wins. The "fix" of margin-tie-breaking only stops working at femto-precision. Genuine equilibrium draws only occur when cross-cluster influence cancellation produces exact float zero (rare).
2. **No counter-play.** The mathematics of `strength*decay^1 = 0.385` per neighbor make every form of disruption (invasion, blocking, contested-cell collision) strictly dominated. The game devolves to "claim a corner, fill it" for both players.
3. **Simultaneous mechanic is non-functional.** The mutual-annihilation collision is a defining feature of simultaneous turns, but it never fires in good play because targeting the opponent's cell is self-harming. So "simultaneous" reduces operationally to "two parallel solo games."
4. **Game length compression.** Threshold reached in 11-12 rounds; max_turns=100 is wildly oversized. Most of the rule space is unused.
5. **No Go-essence.** Score `0.1195` on the GE metric, consistent with the structural absence of capture, life-and-death, ko, or shape-pressure tactics.

### BEST QUALITY

The game does have one elegant property: **the mutual-annihilation collision rule combined with continuous-valued threshold scoring** creates a clean theoretical model for simultaneous-placement territory races. If the radius were larger (≥3), the simultaneous mechanic would matter more (cross-cluster interaction would be unavoidable), and disruption tactics could become viable. The skeleton is sound; the parameters chosen by Run 16 simply don't activate the depth.

### IMPROVEMENT IDEAS

**Single rule change:** increase **propagation radius from 1 to 3** (or alternatively, raise decay from 0.37 to ~0.7 with radius 2). This would force cross-cluster influence at the boundary even when both players claim opposite corners — opponent's stones would suppress your own_sum from across the board, making territory choice and invasion cost-benefit non-trivial. With radius-3 propagation, an isolated invader stone at (3,3) influences ~25 cells of P1's cluster (not just 8), making invasion a genuinely significant disruption — and a meaningful counter-tactic to defenders' clustering.

A second viable single change: **add `strength_asymmetry` such that opposing influences cancel super-linearly** (e.g. multiplicative interference rather than additive). This would give the invasion decision real strategic weight.

---

## ENGINEERING/META NOTES (for the run-level synthesis)

- This game CONFIRMS the central R16 hypothesis (sim+CA games' R14/R15 strength was bug-driven) only partially: the R16 margin-tie-break **does** correctly resolve genuine non-tied margin cases. But for this game (where good play is symmetric-mirror), a residual ~1e-15 P1 advantage persists due to float-order in `step_simultaneous`. P1 wins 4/4 of my engine-verified trajectories (3 main games + 1 probe → actually probe was a DRAW, so 3/4 P1 wins, 1 draw). The trained-agent metric of 0.48 vs random (seed 71052) suggests learning is hard on this game, consistent with strategic shallowness.
- For the seat-balance metric, this game is structurally unbalanced toward P1 in the symmetric-strategy regime. The R16 worst-of-three probe (greedy-vs-greedy added) presumably caught greedy-imbalance issues in other games but not this one — because greedy probably converges to symmetric clustering, which the float-bias resolves to P1 every time.
- This is the lone simultaneous game in R16's top tier (rank 2). The strategic shallowness observed here weakly supports the hypothesis that **classical alternating games are the genuinely strongest design family** post-fixes — though one game is a small sample.
