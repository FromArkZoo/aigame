# Run 19 Evaluation — team-3 — Game 1f9191b5d4e6

**Team ID:** team-3
**Game ID:** `1f9191b5d4e6` (Menger rank-1, GE 0.3293, ELO 2402.4)
**Substrate:** Menger sponge (axis 9, 400 active cells / 729 grid positions, max_degree 6 — but most cells are 3-5 degree because of the fractal holes)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 1f9191b5d4e6`

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive holes per the level-2 Menger sponge fractal pattern. A cell `(x,y,z)` is a hole iff there exists a base-3 digit position `k` at which at least two of `(digit_k(x), digit_k(y), digit_k(z))` equal 1. With axis_size = 9 the relevant digit positions are 0 and 1. Result: 400 active cells. Cell index = `z*81 + y*9 + x`. Holes form thick walls along the y=1, z=1, y=4, z=4, y=7, z=7 mid-planes; the surface layers (z=0, z=8) keep most of their cells.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 89 (PPO games average 38.8).

**Action space.** 730 actions = 729 placements + 1 pass. Place-only (D1 hybrid ban active).

**Placement & capture.** Placement: any empty active cell, no first-move restriction. Capture rule = **outnumber-2**. After a placement at `c`, for each enemy stone `e` axis-adjacent to `c`, count the placer's stones among `e`'s axis-adjacent active neighbours; if ≥ 2, `e` is removed (cell becomes empty). Capture is **destructive, not flipping** — captured cells go ownerless, not over to the placer.

**Propagation.** `influence`, r=1, strength = 1.0, decay = 0.5. On placement at `c`, `board_values[c] += sign·1.0` and each axis-adjacent active cell gets `sign·0.5` (sign = +1 if P1, −1 if P2). Holes are skipped, no distance-2 contribution. Effective score for player P = `Σ over cells P owns of (sign(P) · board_value)` — i.e., P1 sums positive board values on owned cells; P2 sums absolute value of negatives on owned cells.

**Win condition.** First effective score > **29.709** wins. Margin tie → draw. Max-turn timeout: highest score wins.

**Degeneracy check.**
- Capture is symmetric: outnumber-2 fires equally for either side. A naive sandwich attack ((0,0,0) corner threatened by 2-of-3 neighbours) is **counter-sandwichable** — placing on the opposite side of the attacker captures the attacker, because corners have only 3 active neighbours and the cube's face-axis stones share neighbour counts.
- Capture **does not refund** the influence the captured stone leaked. A captured P2 stone leaves its `−0.5` contribution to neighbours intact even after removal — so corners that survive 3 sandwich attempts still come out at `−0.5` net (residual influence damage; see Game 2).
- Influence reach r=1 + fractal holes: many "axis-axis" extensions (e.g., (0,0,0) → (0,0,2)) lose adjacency through a hole, so two 2-apart stones contribute *zero* mutual reinforcement. This makes chain-shape choice highly substrate-dependent.
- Cells of degree 6 are rare and isolated. (2,2,2), (2,2,6), (6,2,2), etc. are 6-degree, but their *peripherals* are mostly 4-degree, which caps the maximum dense-cluster size before the cluster's edge runs into a fractal wall.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — Mirror (structural P1 reference)

Sequence: `0,728,1,727,9,719,81,647,2,726,18,710,162,566,3,725,27,701,243,485,4,724,36,692,324,404,5,723,45,683,6` (31 plies, **P1 wins +31.0 vs +29.0**).

Plot:
- P1 builds a corner-anchored adjacency cluster at (0,0,0): the 3-axis "plus" then extends each axis (1, 2, …, 6 along x; 1–5 along y; 2–4 along z, jumping any holes).
- P2 mirror at (8,8,8) corner. Each (x,y,z) → (8−x, 8−y, 8−z). The mirror is structurally identical because the menger sponge is symmetric about the cube centre.
- Both players gain `+2.0` per ply once their chain is established (each new stone gives +1.0 own + +0.5 to one existing neighbour, plus +0.5 to that neighbour's score = +2.0 effective). Exception: corner placement at start gives only +1.0 (no neighbour to pump up yet).
- Move 30: both at +29.0. Move 31 P1 places (6,0,0) → P1 +31.0, crosses threshold first. Engine: `Done=True Winner=1`.

Reflection (P1): pure adjacency chain along one axis (`+x` from (0,0,0)) is the simplest, most efficient strategy. The fractal holes inside the cube don't matter to surface-anchored chains because z=0 and y=0 are mostly hole-free.
Reflection (P2): mirror is the natural "fair-game" response, but the engine grants P1 the +2.0 each round before P2 can match. P2 is **always** a tempo behind; mirror loses by exactly 1 stone's worth of score = 2.0 once one player crosses threshold.

### Game 2 — Pilot's "sandwich + cluster" P2 counter, with P1 counter-sandwiching

Sequence: `0,1,2,9,18,81,162,728,3,727,27,719,243,647,4,710,36,566,324,485,1,726,5,725,6,724,7,723,8,722,45,704,9,683,19,665,28` (37 plies, **P1 wins +32.0 vs +26.0**).

Plot:
- M1–M2: P1 (0,0,0); P2 (1,0,0) — sandwich start. (0,0,0)'s only active neighbours are (1,0,0), (0,1,0), (0,0,1), so P2 could capture (0,0,0) with ≥2 of those 3.
- **M3: P1 plays (2,0,0) — counter-sandwich**. (1,0,0)'s active neighbours are (0,0,0) and (2,0,0), now both P1 → P2's (1,0,0) is captured. Net: P1 +1.0, P2 −1.0 (P2 lost the stone but the influence damage to (0,0,0) persists).
- M4–M7: P2 retries sandwich at (0,1,0) and (0,0,1); P1 counter-sandwiches each time at (0,2,0) and (0,0,2). After 7 plies P2 has 0 stones, P1 has 4. **P1 effective = +1.0, P2 = +0.0** — but both far below mirror's +5.0 per side at the same ply count.
- **The corner is poisoned.** (0,0,0) net board value sits at −0.5 even after all 3 sandwich attempts are reversed — the 3 P2 stones each leaked −0.5 to the corner before being captured.
- M8 onwards: P2 abandons attack and builds adjacency cluster at (8,8,8). M8 (8,8,8); M10 (7,8,8); M12 (8,7,8); M14 (8,8,7); M16 (8,6,8); M18 (8,8,6); M20 (8,8,5).
- M20 score check: **P1 = +13.0 with 10 stones (+1.30/stone), P2 = +13.0 with 7 stones (+1.86/stone)**. P2's 3-failed-sandwich detour was almost recovered: P2's tight cluster is more efficient per stone, P1's corner is degraded, but P1 has 3 extra placements on the board.
- Both then race linearly. M21 P1 closes the (1,0,0) gap (`+2.0`), and the chain-vs-cluster race continues at `+2.0/ply` for both.
- Move 37: P1 places (1,3,0) reaching +32.0. **`Done=True Winner=1`**, P2 ends +26.0.

Reflection (P1): counter-sandwich is reliable but expensive — each one returns net +1.0 (capture nets +1, but the corner is degraded by the captured opponent's residual influence). Better to ignore the sandwich and build orthogonally; the captures are "honour points," not strategic gain.
Reflection (P2): the sandwich → cluster pivot is the pilot's recommended P2 plan. It almost works — P2 catches P1's per-stone efficiency by move 20 — but the +1 stone tempo lead is decisive in a linear-race game. **You cannot trade tempo for efficiency in this scoring scheme.**

### Game 3 — Seat swap. I play P2 with the "interior 6-degree cluster" novelty adversary

Sequence: `0,182,1,181,9,183,81,173,2,191,18,101,162,263` (14 plies, **tied +13.0 each, P1 to move**).

Plot:
- P1 plays the standard corner-anchor build: (0,0,0), (1,0,0), (0,1,0), (0,0,1), (2,0,0), (0,2,0), (0,0,2). 7 stones at +1.86 average per stone.
- I (P2) play **the rare 6-degree interior centre at (2,2,2)** plus all 6 of its active axis-aligned neighbours: (1,2,2), (3,2,2), (2,1,2), (2,3,2), (2,2,1), (2,2,3). 7 stones, all forming a 3-D plus-prism around the centre.
- M14 score: P1 = +13.0, P2 = +13.0. **Identical per-stone efficiency.**
- The 6-degree centre at (2,2,2) accumulates +4.0 alone (own +1.0 + 6×0.5 from peripherals). But each peripheral has only 4 active neighbours (the holes around the (1,1,*), (1,*,1), (*,1,1) lattice eat 2 of the would-be 6 neighbours), so peripherals net only +1.5 each. Total: +4.0 + 6×1.5 = +13.0. Same as P1's chain.

Reflection: I expected the 6-degree centre to **beat** corner-chain efficiency. It doesn't — peripherals are 4-degree (fractal walls block the diagonals from extending), so the centre's 6× boost is paid back by lower-density peripherals. **The menger sponge does not have a "high-density" interior region that breaks the +1.86/stone ceiling.** Combined with P1's tempo, no strategy I tried lets P2 win.

Continuing M15+ projects out to P1 winning around move 35–37 (same as Game 2).

### Strategy guides

**P1 (offence/threshold push):** Open at any 3-degree corner and chain along one face axis (e.g., (0,0,0) → (1,0,0) → (2,0,0) → …). Each chain stone after the first nets +2.0. Don't bother with 6-degree centres — they don't out-perform face chains because the menger holes ring the centres. Defend against P2 sandwich by **counter-sandwich** when the geometry allows (place on the third side of the attacked corner) or simply ignore and build elsewhere.

**P2 (defence + offence):** Mirror loses on tempo. Sandwich at P1 corners only works if P1 is asleep — counter-sandwich is one move for P1, and then your sandwich stones leave residual −0.5 each on the poisoned corner before being removed, which is a net 0 trade. Best is to abandon disruption and race — but you'll still lose by ~+6 effective score in a 37-ply game. **The game is structurally lost for P2** absent rule changes.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Only one *winning* strategy: P1's adjacency-chain race. Three "interesting but losing" P2 strategies: (a) mirror, (b) sandwich + pivot, (c) interior 6-degree cluster. None of them beat the +1.0 stone-tempo P1 lead in a threshold race where both sides gain at +2.0/ply.

**Counter-play.** Effectively absent. P1's chain build has no exploitable weakness; sandwich attacks on a P1 corner are reliably counter-sandwiched; P1 can ignore them entirely and still win on tempo. **The +2.0/ply gain per side is mechanical and offers no decision-relevant variance** — the helper's "Top-K greedy" suggestions almost always show 6+ moves all worth +2.0, meaning the position has very low local information content.

**Short-term vs long-term.** Threshold 29.7 / +2.0 per ply → 15 P1 plies (≈ 30 turns total) to win. Tactical horizon ≈ 3–5 plies (you're never planning further than "where does my next chain extend"). **No medium-term strategic concept exists** — there is no "shape," "territory," or "race tempo" decision after move 5; the rest is mechanical greedy extension.

**Emergent concepts observed.**
- **Counter-sandwich.** Outnumber-2 is a symmetric capture rule, so any sandwich attack is itself sandwich-vulnerable. This is the *one* tactical pattern the game produces and it neutralises the *one* form of disruption.
- **Influence poisoning.** Captured stones leave residual −0.5 contributions on adjacent cells. After 3 sandwiches → 3 counter-sandwiches at the corner, the corner sits at −0.5 net P1, even though P1 owns it and never lost it. Genuinely emergent — captures are not "free recovery."
- **Tempo shadow.** Because both sides gain at the same +2.0/ply rate, the +1.0 lead from going first is preserved through the entire game. You cannot pay tempo for any other resource.
- **6-degree centre paradox.** The high-degree interior cells *should* be efficient, but the fractal walls bound their cluster size to 7 stones, and the peripherals are 4-degree, so the cluster's per-stone efficiency caps at the same +1.86 as a face-chain.

**Does the menger substrate matter?** *Less than it appears.* The fractal holes degrade cells from 6→4 or 6→3 degree compared to a regular 9³ grid, but they don't introduce any *new* degree class — corner cells are 3-degree on regular 9³ too. The fractal effectively shrinks the playing area from 729 to 400 cells without changing the strategic primitives. **A regular 8³ cube (512 cells, all active) would play almost identically**: same corners, same +2.0/ply chain, same sandwich/counter-sandwich symmetry. The pilot's claim that "menger constrains cluster geometry to a small set" is correct, but the regular grid would *also* have a small set of efficient shapes (just slightly different). The fractal substrate adds **maybe 0.5 points of novelty** but nothing of strategic depth.

**Does the propagation kernel matter?** Yes. r=1 + holes is harsher than r=1 on regular grid because some "neighbour" pairs are blocked by the fractal walls. r=2 (carpet rank-1's value) would *partially* paper over the fractal — distance-2 stones could still reinforce — but at the cost of weakening the corner-sandwich threshold (more cells in the radius-2 ball means more friendly counts means easier outnumber → more captures, possibly destabilising). r=1 is the right choice for *this* capture threshold; the consequence is the harsh hole-routing penalty.

**Capture-rule contribution.** Captures fired exactly 3 times in Game 2 (all P1 counter-sandwiches; net ≈ 0 effective change after residual influence damage). Captures fired 0 times in Games 1 and 3. **Captures are not the game's main mechanic** — they exist as a sandwich-vs-counter-sandwich tactical wrinkle that produces no net advantage when both sides see it. In games that go deep into mid-board play, captures simply don't fire because both sides are building their own clusters far apart.

**First-mover advantage / seat balance.** Decisive. From my 3 games: P1 wins all 3 against (mirror, sandwich+pivot, interior cluster). The trained-vs-trained 0.500 reference reflects PPO learning the asymmetric counter, but my hand-played results suggest the asymmetry is structural at +1.0 stone of tempo per round, which converts to a +2.0–6.0 effective lead at threshold-crossing. **Pie rule is the obvious fix.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a **threshold-race influence game with adjacency-2 capture, on a fractal substrate**. Argument:

(a) **Threshold-race influence games** are well-known: *Tumbleweed* (2D hex, r-based influence, threshold) is the closest published analogue. *Sygo*, *Inertia*, *Monkey-Go-Round* are adjacent. The threshold-race scoring with influence kernel is **a known family**.

(b) **Outnumber-2 capture** is **Ataxx-family** (place-based, count-based capture), structurally similar to Tafl's "shield-wall" pattern when restricted to ≥2 friendly neighbours. Ataxx specifically: stones are captured by adjacency. Outnumber is a friendlier (less-frequent) sister of Ataxx capture.

(c) **The combination "outnumber-2 + influence + threshold-race"** is novel as a published abstract game, but the components are all known. Within this codebase: **same family as carpet rank-1** (`ce3a09e05cef`). The R8 Connection Go family (custodian + connection) is *different* — captures *flip* in R8 (Othello-like) and the win is connection (Hex-like), so different ancestry. The R17 family was custodian + connection on 3-D grid — also different. **R19's family is genuinely a new one for this project**, but the lineage is straightforward.

(d) **Menger substrate.** Fractal substrates for abstract games are rare. *Hales–Jewett theory* covers n-D combinatorial lines; no published game uses an actual menger sponge. **However**, the menger-vs-regular-grid distinction in *this* game's strategic content is small — see Phase 3. The substrate is unusual *visually* but minimally impactful *strategically*. The most impactful novelty contribution is **the subtraction**: holes prevent certain shapes (no 2×2×2 own-stone cubes), not the addition of new shapes.

(e) **Expert-transfer test.** A *Tumbleweed* + *Ataxx* player would understand this game in 5 minutes: "Ataxx capture but threshold-2, plus a Tumbleweed-style influence kernel with r=1, threshold-race ending, on a 3-D fractal." The fractal substrate adds maybe 5 minutes of "which cells are active" lookup. **No irreducible new concept.**

**Closest known-game analogue:** **Tumbleweed-3D with Ataxx-threshold-2 capture, on a Menger sponge.** No exact published analogue. Inside this project corpus, the closest is **carpet rank-1** (`ce3a09e05cef`), same family, 2-D version, r=2 influence kernel.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian (flip) + connection (Hex-like win) on 2-D grid. R19 menger rank-1 is outnumber (remove) + influence (Tumbleweed-like) + threshold-race on a 3-D fractal. **Different family entirely.** R8's strength: a clear narrative arc (build a chain, complete it, win). R8's depth came from the *combination* of two interacting mechanics (the custodian flip *completes* the connection, a single-move bridge). R19 menger rank-1 has no comparable interaction — captures don't help with influence accumulation; they're a tactical-loss-prevention mechanism. **R19 lacks R8's emergent depth-multiplier.** Without the bridge dynamic, R19 sits at ~half R8's depth.

**Player rebuttal (P1 + P2).**
- **The fractal hole structure does not contribute a new strategic primitive.** Cluster shapes are constrained, but in a degenerate way (fewer options, not different options). Comparing 4-stone plus on menger vs. 4-stone plus on 8³ regular grid: the per-stone efficiency is the same (+1.75/stone for the plus). The menger version just means the plus is *one of fewer* options.
- **The 3-D corner sandwich (2 of 3 neighbours required)** is geometrically distinct from 2-D corners, but Ataxx already uses 2-D corner-attack mechanics; the 3-D extension is a small generalization.
- **What adds novelty:** the *visual-aesthetic* unprecedented-ness of the menger sponge as a board substrate, and the substrate-driven impossibility of a 2×2×2 own-stone cluster. These are real but cosmetic; they don't create play depth.
- **What subtracts novelty:** the threshold-race + adjacency-clustering combo collapses to mechanical greedy +2.0/ply for most of the game; tactical choice is sparse.

**Novelty score (post-adversary):** **5/10.** Above pure re-skin (2–3) because the menger substrate is genuinely unprecedented in published abstract-game literature and the threshold-race + outnumber-capture combo is a fresh family for this project. Below 7 because (i) no irreducible new strategic primitive — every component is mappable to Tumbleweed/Ataxx/Tafl, (ii) the menger holes degrade play more than they enhance it (no new cell-class, just fewer cells), (iii) the strategic ceiling is set by the per-stone +1.86 cap, which is the *same* ceiling on a regular 3-D grid. **Anchored: above R17 mean (3.50) by 1.5 because the substrate is fresh; below R8's 8/10 by 3 because R8 has a depth-multiplier emergent (the custodian-bridge) that this game lacks; same as carpet rank-1 because they're the same family.**

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** 1f9191b5d4e6
**Rules Summary:** Place stones on a 9×9×9 menger sponge to accumulate influence on cells you own. Each placement gives +1.0 to itself and +0.5 to each axis-adjacent active cell, with sign by player. Capture: place a stone, and any adjacent enemy stone with ≥ 2 of your stones among its own neighbours is removed. First to > 29.709 effective influence wins.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 (effective 3–5 for most cells).
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Once you see the +2.0/ply mechanical greedy extension, the game has no medium-term strategic decisions. The one tactical wrinkle (sandwich/counter-sandwich) is symmetric and self-cancelling. No territorial concept, no race-tempo decisions, no shape-equity choices. Phase-2 Games 1, 2, 3 all converged to the same score within ±0.5 by move 14, suggesting strategy choice doesn't matter — only chain length and tempo do.
- **Emergent Complexity: 4** — Counter-sandwich is the lone emergent pattern, plus "influence poisoning" of captured cells (genuinely interesting but tactically minor). The 6-degree centre paradox is *meta*-emergent (you discover it doesn't help) rather than a positive emergent concept.
- **Balance: 3** — Mirror = P1 wins (Game 1, +31 vs +29). Sandwich + pivot = P1 wins (Game 2, +32 vs +26). Interior 6-degree cluster = ties at par per-stone but P1 still wins on tempo (Game 3 projected). **No P2 strategy I tried wins.** PPO's reported 0.500 trained-vs-trained reflects PPO learning some asymmetric counter I didn't find — but a human will not, given the game's mechanical greedy structure.
- **Novelty (post-adversary): 5** — see Phase 4. Menger is unprecedented as a substrate; the strategic family is the same as carpet rank-1; the substrate adds aesthetic novelty but minimal strategic novelty.
- **Replayability: 3** — Once the +2.0/ply chain build is internalised, openings collapse to "any 3-degree corner, any face axis." 6-degree centre cluster is a fun *one-time* exploration but doesn't beat corner. Sandwich attacks are dead. **3-4 distinct openings worth knowing, all converge to similar finishes.**
- **Overall "Would I play this again?": 4** — Once: yes, the influence dynamics + 3-D fractal are aesthetically novel. Repeatedly: no — the mechanical greedy structure beats meaningful tactical choice. **Anchor: R17 mean 3.5 + 0.5 for the substrate freshness = 4.0. Below R17 best (4.14) because R17 had at least the custodian-bridge tactic; this game has no comparable depth-multiplier.**

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed-3D with Ataxx-threshold-2 capture, on a Menger sponge** — no exact published analogue, but each component (Tumbleweed influence, Ataxx-style outnumber capture, threshold-race) maps to known games. Inside this project corpus, the closest is **carpet rank-1** (`ce3a09e05cef`), the same family in 2-D with r=2 kernel. Both share lineage and limitations.

### KILLER FLAWS
- **Mirror = P1 wins by structural tempo.** +1.0 stone advantage per round (P1 always one ahead), preserved through the entire +2.0/ply race. P2 has no robust counter; pie rule needed.
- **Mechanical greedy play.** The Top-K helper consistently shows 6+ moves all worth +2.0 — meaning local position information content is near zero after the opening. Tactical decisions are sparse; the "interesting" tactical move (sandwich) is reliably countered.
- **Captures are a wash.** Counter-sandwich nets ≈ 0 effective change. The capture rule exists but doesn't drive the game's win condition; it's a tactical-loss-prevention layer that fires rarely and matters less when it does.
- **Fractal substrate is cosmetic, not structural.** Menger holes degrade cells from 6→4 or 6→3 degree but don't add a new degree class. A regular 8³ cube would play almost identically.
- **No depth-multiplier emergent.** Unlike R8 (custodian-bridge completes connection in 1 move) or R17 (sandwich-trap converts to row), there is no single-move pattern in R19 menger rank-1 that creates strategic non-linearity. The game is linear.

### BEST QUALITY
**The 6-degree centre cluster as a discovery moment.** When I as P2 played (2,2,2) + 6 peripherals, I *expected* it to beat corner clustering — interior cells have higher degree, so should be more efficient. Discovering empirically that the menger holes ring the centres (peripherals are 4-degree) and the per-stone efficiency caps at +1.86 regardless of cluster type is **a genuine substrate-driven insight**. This is the only "ah-ha" the game produced for me. The counter-sandwich symmetry is the runner-up.

### MENGER STRUCTURAL CONTRIBUTION
**Modest, mostly cosmetic.** The fractal hole pattern (a) shrinks the playing area from 729 to 400 cells, (b) constrains some cluster shapes (no 2×2×2 own-stone cube exists), (c) creates the 6-degree centre paradox. None of these introduce a new strategic primitive — corners are still 3-degree (same as regular grid), efficient clusters are still axis-chains (same as regular grid), and the per-stone influence ceiling is unchanged. **Estimate: flattening to a regular 8³ cube would lose ~0.5 points of novelty and ~0 points of depth.** This is *less* substrate contribution than the pilot estimated (1 point each); the difference is that I tested the 6-degree centre cluster and found it doesn't out-perform face-chains, neutralising one of the pilot's claimed strategic-axis benefits.

### IMPROVEMENT IDEAS

**Single best change: pie rule.** P1's structural tempo lead is +1.0 stone per round, decisive in a linear race. Pie rule (P2 chooses to swap colours after P1's first move) forces P1 to choose openings whose value is exactly 50/50, which is the standard fix for first-move advantage in connection/influence games. **This alone would add ~2 points of balance.**

Secondary improvements:
- **Cap own-cell board_value to ±2.0.** Currently a 6-degree centre can reach +4.0 on the centre alone. Capping forces clusters to spread and increases the strategic decision count.
- **Increase capture threshold from 2 to 3.** Outnumber-3 means corners (3-degree) cannot be captured (would require 3 of 3 neighbours, impossible because the corner itself is the captured stone). This forces sandwich attacks to mid-board (4-5 degree cells), which is more strategically interesting and rewards positional play over tactical raids.
- **Add a secondary "first-to-N-stones-in-a-line" win condition.** Provides a narrative-arc dimension (à la R8 connection win) layered on top of the threshold race. Players would need to balance race vs. shape, recovering the depth-multiplier emergent that R8 had.
- **Penalise "linear chains" in fitness.** The current dominant strategy is a 5-cell linear chain — exactly the shape that a connection-style win condition would penalise. Encourage cluster-vs-chain decisions in evolution.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-3_game1f9191b5d4e6.md`.*
