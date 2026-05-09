# Run 20 Agent-Team Eval — team-pilot — Game a6385db22c0b

**Team ID:** team-pilot
**Game ID:** a6385db22c0b (menger top-1, 15-seed mean GE 0.241, σ 0.120, depth 0.763)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game a6385db22c0b` (see `briefing_menger_a6385db22c0b.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive holes carved out per the level-2 Menger sponge fractal pattern (active=400). Cell index = z·81 + y·9 + x. A cell is inactive iff ≥2 of its three base-3 coordinate digits at the level-1 scale are 1 (the central slabs `y=3,4,5 ∧ z=3,4,5`, etc., are removed). Result: cells in the exterior shell + tunnel-axes are active; the bulk core and the 6 face-centers are hollow.

Critical structural consequence: many cells have **degree 2 or 3** rather than the grid maximum of 6. E.g. `(1,0,0)` has only `(0,0,0)` and `(2,0,0)` as live neighbours — the `y=1` and `z=1` neighbours are holes. Outnumber-2 capture and influence compounding both depend heavily on local degree.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. Placement legal at any empty active cell (401 legal initially).

**Placement & capture.** Capture rule = **outnumber-2**: when a stone is placed at `c`, every adjacent enemy stone `d` is checked; if `d` has ≥2 friendly (placer-coloured) stones among its active neighbours (counting `c`), `d` is **cleared** (the cell becomes empty, not flipped). Verified empirically (Game 3, move 3): after `0,1,2` the P2 stone at `(1,0,0)` is captured the moment P1 places at `(2,0,0)` because `(1,0,0)`'s only 2 active neighbours are now both P1.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). On placement at `c`, engine adds ±1.0 to `board_values[c]` and ±0.5 to each of c's ≤6 active axis-neighbours. Sign = +1 if P1, −1 if P2. Clamped to [−100, 100]. Crucially, the value at the captured cell is **not reset** when a stone is cleared — earlier deposits persist. This means a captured cell can leave residual −0.5 / −1.5 traps that the recapturer pays for.

**Win condition.** Threshold-race. After every move, sum `board_values` over each player's currently-owned cells. First player whose owned-sum exceeds **57.974** wins. `target_dimension_p2 = -1` ⇒ P2's effective sum = −1·sum(values on P2-owned cells), so P2 wants its cells to be very negative. Equal margins → draw. Max-turn timeout: highest effective sum wins.

**Pie rule.** Off (lost in crossover before the `ac9e642` fix).

**Degeneracy check.**
- The Menger hole pattern truncates many cells to degree 2–3, which makes outnumber-2 captures **easy to execute and equally easy to walk into** — degree-2 cells in particular are capture traps for the placer.
- No inert fields. Influence is on, capture is on, both fire empirically.
- Threshold 57.97 with strength=1.0, decay=0.5 ⇒ a fully-clustered stone contributes `1 + 0.5·deg_friendly` to its own owned-sum; a 1D line gives ~3L−2, a 2D patch ~3·N_stones, a packed 3D corner up to ~4·N_stones. Crossover-win is ~25–30 stones each side.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — P1 corner cluster vs P2 mirror corner cluster

Sequence (51 plies, P1 wins): `0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60,3,77,12,68,21,59,27,53,28,52,29,51,81,161,83,159,84,158,4,76,22,58,36,44,38,42,99,233,101,235,165,140,110,239,164`.

Plot:
- P1 builds a dense 3×3 patch on z=0 in the (0..3, 0..3) corner, then extends into z=1 and z=2 via the few non-hole tunnel cells (`(0,0,1)=81`, `(2,0,1)=83`, `(3,0,1)=84`).
- P2 builds the symmetric (6..8, 6..8) corner cluster.
- The clusters are physically disjoint (z-axis separation through the menger core, which is mostly holes), so no captures and no contention.
- Linear influence accumulation: at move 16 both at +16; at move 32 both at +36; at move 48 P1=+53, P2=+51. P1 leads by 2 throughout — pure tempo from going first.
- Move 49 P1 plays `(2,3,1)=110` (Δ+3 because it picks up two friendly-deposited +0.5 neighbours: `(2,3,0)` and `(2,2,1)`). P1 score → 56.
- Move 50 P2 mirrors `(5,8,2)=239` (Δ+3 by analogous compounding). P2 score → 53.
- Move 51 P1 plays `(2,0,2)=164` (Δ+3, adj to `(2,0,1)=83`). P1 score → 59. **P1 wins**.

P1 reflection: Cluster compounding is the only knob. The Menger holes thin out the 3×3×3 corner to ~20 active cells, so a cluster has fewer adjacencies than a flat 3×3×3 cube — but enough to dominate the board.

P2 reflection: Mirroring is fine if you have first-equivalent tempo; here P1 starts with one stone of free advantage and never gives it back.

### Game 2 — P1 corner cluster vs P2 wall-line through P1's expansion lane

Sequence (51 plies, P1 wins): `0,4,1,6,2,5,9,7,11,8,18,17,19,26,20,35,3,44,12,53,21,62,27,71,28,80,29,79,81,78,83,161,99,159,101,158,102,76,110,75,84,240,108,242,180,224,164,222,162,238,183`.

Plot:
- P1 starts `(0,0,0)`. P2 plays `(4,0,0)`: P2 occupies a degree-2 cell *between* P1's expansion zones, baiting an attack.
- P1 ignores the bait and keeps building its corner cluster.
- P2 tries to convert into an L-shaped wall along z=0 face perimeter `(4..8, 0)` then `(8, 0..8)`.
- Through move 36 the score gap is only P1=+39.5 vs P2=+34.5 — wall-density is roughly 1.5 / stone vs cluster 2.0 / stone.
- The wall-line never captures; P1's `(3,0,0)` placement creates only 1 P1 neighbour to `(4,0,0)=P2`, and `(4,0,0)` has only 2 active neighbours total, so it's effectively un-capturable as long as `(5,0,0)` stays P2.
- By move 48 P1 has spread into z=1/z=2 and the gap is +12. Move 51 P1 finishes at +59.5 vs P2=+44.5 — **P1 wins by 15**.

P1 reflection: The cluster outscores the wall by ~0.5 per stone over a long game. Wall geometry on the z=0 face also butts up against y=0/8/y=1 hole rows, making each wall stone effectively degree 2.

P2 reflection: Choosing an asymmetric wall geometry over a cluster gives up ~10–15 effective points. The "block P1 expansion" idea doesn't translate to threshold value because P1 just builds elsewhere — the board has 400 cells.

### Game 3 — Adversarial / capture-bait line

Sequence (probe; 5 plies): `0,1,2,81,162`. Game continues, but the capture pattern is the relevant finding.

Plot:
- Move 1: P1 `(0,0,0)`. Move 2: P2 `(1,0,0)` (degree-2, bait).
- **Move 3: P1 `(2,0,0)`. Outnumber-2 fires immediately.** `(1,0,0)` has only 2 active neighbours `(0,0,0)` and `(2,0,0)`, both now P1 ⇒ P2 stone cleared. Engine: P2 piece count 1→0.
- The captured cell retains the deposited values: P2's `(1,0,0)` placement deposited −0.5 at `(0,0,0)`. After capture and P1's `(2,0,0)` placement, `(0,0,0)` value is +0.5 (down from a maximum +1.5 had P2 not played). So the capture **costs P1 net 0.5 effective influence** — the gain is the lost P2 stone's would-be future contribution, not direct points.
- Move 4: P2 `(0,0,1)` (also degree-2 in the menger structure: neighbours are `(0,0,0)`, `(0,0,2)`, `(1,0,1)hole`, `(0,1,1)hole`). Move 5: P1 `(0,0,2)`. Capture again: `(0,0,1)` flanked by `(0,0,0)`+`(0,0,2)`, both P1.

Reflection: **Outnumber-2 + low-degree menger cells = capture trap for the placer.** P2's aggressive infiltrations into P1's expansion neighbourhood are auto-captured because the menger holes leave only 2 active neighbours, both of which P1 already has or can easily acquire. This is the *opposite* of intuition: lower degree ⇒ easier capture, not harder.

### Strategy guides

**P1 (offence/threshold push):** Open at any corner-adjacent cell `(0,0,0)`, `(2,0,0)`, `(0,2,0)`. Build the 3×3 patch on z=0, then climb to z=1 via the tunnel cells `(0,0,1), (2,0,1), (0,2,1), (2,2,1)`, then z=2 via `(0,0,2), (2,0,2), …`. Push for 25–30 stones with 2+ friendly neighbours per placement. Total game length ~50–55 plies under naive play; PPO play (~85 plies) suggests both sides spread thinner.

**P2 (defence + threshold contest):** Mirror cluster in the (6..8, 6..8) corner. Do **not** infiltrate degree-2 cells in P1's corner — every such stone is auto-captured. Do **not** build a wall — line geometry gives ~0.5 less per stone than a cluster. The only correction for the +1 P1 first-move tempo is "play a strictly better cluster shape" — but the substrate is symmetric and P1 has the same shape available, so balance is structurally tilted.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Effectively **one**: cluster compounding. Wall geometry, infiltration, and capture-bait all underperform mirror cluster in head-to-head play. The "depth" the engine measures (0.763) is mostly *which exact cells you cluster on* — the menger active-cell graph has irregular structure so optimal cluster shape isn't trivial — not "what kind of strategy".

**Counter-play.** Partial. Mirror cluster (the only viable counter) has no real way to overcome P1's first-move advantage. Trained-vs-trained 0.667 P1-favoured matches my findings exactly: a sub-+1.5 P2 deficit per game, no pie rule available to reset.

**Short-term vs long-term.** Short-term entirely. Each placement's value is fully determined by current active-neighbour count; there is no medium-term concept (no territory, no threats, no shape-building). Plan horizon = 1 ply.

**Emergent concepts observed.**
- **Compounding density**: 1 + 0.5·friendly-degree per placement. Drives the entire game.
- **Capture trap**: degree-2 cells are bad for both placers; the *lower* the degree, the easier it is to flank.
- **Residual value persistence**: captured cells keep their accumulated value; recapturing gives sub-par influence.
- I did **not** observe ko-fights, mutual annihilation, sub-volume territorial control, race-tempo manoeuvres, or any non-trivial influence-shape strategy. The game is a parallel sum of local additions.

**Does menger matter?** *Marginally and negatively.* The fractal hole pattern truncates degrees and breaks the 3D corner volumes, but doesn't add any strategic dimension that a flat 9×9 grid wouldn't have: in either case it's "build a dense cluster". The menger contribution is essentially an irregular cell-degree table that makes top-K placement value-ordering slightly more interesting (you learn which corners are degree-3 vs degree-4) without changing the strategic shape. **Could be flattened** to grid_control with negligible loss in dynamics — and indeed `fcedbc14043d` (R20 grid champion) is closely related.

**Does the propagation kernel matter?** Yes, but only the value of `decay`. With decay=0.5 and r=1, a stone's contribution scales linearly in its friendly-degree. With decay=0.0 each stone is worth exactly +1.0 regardless of context — the "cluster" idea would vanish. With decay=1.0 distant stones would also count, encouraging spread. The 0.5 / r=1 setting basically *defines* the "cluster compounding" mechanic that makes this game work.

**Capture-rule contribution.** Outnumber-2 fires reliably when triggered, but **almost never gets triggered in mirror-cluster play** because both sides build at opposite corners with no shared frontier. Game 3 demonstrated captures only by deliberately baiting. In trained-vs-trained PPO play the avg game length 85 is consistent with no major capture cascades — captures would shorten games sharply by removing N stones in 1 turn.

**First-mover advantage / seat balance.** Strong. My 3 games: P1 wins all 3. Trained-vs-trained 0.667 P1-favoured matches. Pie rule is OFF (engine briefing notes "lost in crossover before the `ac9e642` fix"). The structural P1 advantage is roughly +1.5 per game, exactly the value of "go first into an empty cell that becomes a friendly anchor".

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of well-known mechanics. Argument:

(a) **Threshold-race influence games** are essentially Othello scoring without flipping, or weighted territorial counting in Go. Closest published analogy: "majority sum" voting games, or *Influence* (a published 1990s board game using influence radius scoring). The race-to-threshold variant resembles Connect-style sum-races but on continuous influence.
(b) **Outnumber-N capture** is closest to **Tafl / Hnefatafl** (sandwich-and-remove) and **Ataxx** (overwhelm-and-flip). The "remove" semantics (cell becomes empty, not flipped) is Tafl-family. The "any 2 friendly nbrs" formulation is more permissive than Tafl's "fully surround".
(c) **The combination "outnumber-2 + influence + threshold-race"** is a known pattern in this project's R10–R19 corpus — it's the dominant menger family. The R19 menger top-1 `1f9191b5d4e6` is structurally the same recipe; this game is a parameter-blend descendant.
(d) **Menger substrate.** Has fractal Hausdorff-dim play been studied? Not in board games at axis-9 level-2. But the "irregular-degree active cell graph" reduces to "play on a graph" which is studied (Hex on irregular graphs, e.g.). The hole pattern doesn't introduce any new mechanic — it just truncates degrees.
(e) **Expert-transfer test.** A Go + Othello + Ataxx player would understand this game in 5 minutes. The "novel" piece is *only* the irregular cell graph, which they'd treat as "play on a Hex-like irregular graph". 90% of the strategy transfers.

**Closest known-game analogue:** **Influence Othello on a Menger-sponge graph** — equivalently, "Tafl-style outnumber capture + Othello-style positional scoring + first-to-N race, on a fractal lattice". No published game does exactly this combination, but each component is well-studied.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2D 8×8 grid. This game is outnumber-2 + influence + threshold-race on a 3D menger sponge. **Different family entirely.** R8 had a *connection* win condition that drives long-range planning ("does my chain reach the opposite face?") and a *flip* capture that interconnects offense/defense ("each capture extends my chain"). This game has neither: threshold-race is a parallel sum (no chain dynamics) and outnumber-removal cleans cells (no chain extension). R20 sits **structurally lower** than R8: shallower planning horizon, fewer interactions between mechanics, no shape strategy.

**Comparison to R19 best.** R19 menger top-1 (`1f9191b5d4e6`, 4.8/10) is the same family with similar parameters. R19 menger top-3 (`5048f71b62fd`, surround capture, 5.0/10) had a *surround* capture rule which is more Go-like and gave it slightly more emergent depth (chain-life-and-death possibilities). This game is in the middle: capture-2 is a weak version of surround. Its 15-seed mean GE 0.241 is close to R19's menger-top values, suggesting depth is roughly equal.

**Player rebuttal (P1 + P2).**
- The **degree-truncation capture trap** (degree-2 menger cells are auto-flank zones) is genuinely substrate-specific — doesn't appear in flat-grid Tafl. But it's a degenerate case, not a strategic asset: it means low-degree cells are simply unplayable for the second-mover. Net: a *minus* to depth, not a plus.
- The **persisting captured-cell value** (residual influence after capture) is a project-specific quirk that creates a small "anti-recapture" force, but is mostly cosmetic.
- The **3D substrate** doesn't add strategic dimension — z-axis adjacencies are just additional graph edges, not a new strategic axis. The asymmetry in R8 (P1 connects z, P2 connects x) is what made 3D *strategically* matter; here both players race the same threshold so 3D is just extra cell count.

**Novelty score (post-adversary):** **3/10.** Above pure re-skin (2) because the menger irregular-degree graph + influence + outnumber-2 combination doesn't exist in published games. Below 5 because R19 already produced this family multiple times, the components are individually well-known, and the substrate adds essentially no new strategic dimension (it just changes which cells are valuable). Anchoring against R17 mean (3.50), this is *below* the R17 mean — R20's "best" by GE is structurally weaker than R17 average because R17's connection-wins family produces more strategic depth than R20's threshold-race family.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** a6385db22c0b
**Rules Summary:** 9×9×9 menger sponge; alternating placement on 400 active cells; each placement deposits ±1 at the placed cell and ±0.5 at each axis-neighbour; an enemy stone with 2+ friendly neighbours after placement is removed (cleared, not flipped). First player whose stones' total deposited values exceed 57.97 wins. Pie rule off.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — One viable strategy (cluster compounding), one knob (which corner / which cells), zero medium-term concepts. The 0.763 engine-measured depth reflects per-placement value variance from irregular menger degrees (top-K greedy outputs vary across +1, +2, +3 cells depending on neighbourhood) but doesn't translate to multi-ply planning. Compares to R17 best (4.14): roughly equivalent depth, fewer tactical branches.
- **Emergent Complexity: 3** — Compounding density and degree-2 capture trap are emergent but trivially derived from the 1+0.5·deg formula. No higher-order patterns (no ko, no shape, no race-tempo manoeuvre).
- **Balance: 3** — Trained-vs-trained 0.667 P1-favoured (briefing) matches my 3/3 P1-wins. The +1.5/game first-mover advantage has no in-game corrector since pie rule is off. R8 had pie rule + seat-swap correction which kept it balanced; this game lost both.
- **Novelty (post-adversary): 3** — see Phase 4. Pure family-member of the R19 menger lineage; substrate is decorative; capture mechanic is weaker than surround.
- **Replayability: 3** — Once the cluster-compounding strategy is known, opening play collapses to "any of the 8 corner regions". Game outcomes deterministic. PPO winrate convergence (~98% trained-vs-random, 0.667 trained-vs-trained) confirms a small set of dominant strategies.
- **Overall "Would an agent team play this again?": 3** — Once: yes, to verify the menger-degree mechanic. Repeatedly: no — the depth ceiling is hit fast and the imbalance is uncorrectable without the pie rule. Anchors: R8 = 8, R17 mean = 3.5, R17 best = 4.14, R19 menger top = 4.8. This game lands a notch below R19 menger top because pie is off and depth is similar.

### CLOSEST KNOWN-GAME ANALOG
"Influence Othello on a Menger-sponge graph" — no published game matches exactly, but each component (territorial influence scoring, Tafl-style outnumber removal, race-to-threshold) is well-studied. Inside this project's corpus, R19 menger top-1 `1f9191b5d4e6` is the immediate sibling.

### KILLER FLAWS
- **Pie rule off** under a measured 0.667 P1-favoured imbalance — the briefing flags this as "lost in crossover". Without seat-swap correction, the game is structurally tilted by ~+1.5 per game and there is no way to fix it within the rule blob.
- **Single viable strategy** (cluster compounding) collapses opening variety. PPO learns one mode and loops it.
- **Substrate decorative.** Menger holes change which cells are valuable but not how to play. Could be flattened to grid_control with no strategic loss (and grid_control still has the 9×9 axis).
- **Capture mechanic almost never fires in equilibrium play** because both sides build disjoint corner clusters. The capture rule pays no rent.

### BEST QUALITY
The **degree-truncation cell value variance** is the only mildly interesting feature. Players (or PPO) must learn that `(0,0,0)` cluster compounds harder than `(8,4,0)` cluster, because the active-cell graph has different connectivity in different corners. This is a real micro-optimization knob — it's just not a *strategic* one.

### menger STRUCTURAL CONTRIBUTION
Modest and arguably **negative**. The fractal hole pattern (a) truncates many cells to degree 2, which makes capture trivially easy on those cells (auto-flank capture trap), (b) breaks 3D corner volumes into ~20-cell pockets, reducing the number of "interesting" cluster shapes, (c) doesn't introduce any new strategic concept that wouldn't appear on a flat grid. R19's finding that "menger > carpet > grid for substrate quality" doesn't survive close inspection on this game — a 5×5×5 solid cube would offer denser clusters and more capture interaction. **Could plausibly be flattened to a 9×9 grid + influence + outnumber-2 with no strategic loss.**

### IMPROVEMENT IDEAS
**Single best change:** Restore the **pie rule** (or invent a structural rebalancer) — this is the single biggest correction and the briefing already identifies it as a known regression. With pie rule on, the +1.5 first-mover advantage becomes a fair-priced auction.

Secondary improvements:
- Switch capture rule to **surround** (R19 menger top-3 used surround and scored 5.0). Surround creates chain life-and-death and more strategic depth than outnumber-removal.
- Switch win condition to **connection** (R8's family). Threshold-race is a parallel sum and produces no emergent strategy beyond compounding density.
- Reduce threshold to ~30 to force decisive games in 30–40 plies — at 57.97 the game grinds to ~85 plies of mostly redundant compounding.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-pilot_gamea6385db22c0b.md`.*
