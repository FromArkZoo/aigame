# Team-9 Evaluation — Game `f8dbeb3079a5` (Run 16, GE rank 2)

Team ID: `team-9`
Game ID: `f8dbeb3079a5`
DB: `/Users/jamesbrowne/aigame/genesis_v2_run16.db`
Engine: `step_simultaneous()` via `sim_play_helper.py` and direct invocation.

---

## Phase 1 — Rule Comprehension

### Board structure
- 2-dimensional, axis_size = 8 → 64 cells, 65 actions (64 placements + 1 pass at action 64).
- Topology: **`moore`** (8-neighbor: orthogonal + diagonal), **non-wrapping** despite what `sim_play_helper.py`'s render header says ("torus" label is hard-coded incorrect — verified by inspecting `topo.get_neighbors(0)` = `[1, 8, 9]`, only 3 neighbours; an 8-corner cell on a torus would have 8).
- The R16 generator note says it normally downgrades moore → grid when surround capture is present; here capture is `none` so moore (8-adjacency) survives.

### Turn structure — **SIMULTANEOUS**
- `turn_type = "simultaneous"`, `pieces_per_turn = 1`. Both players submit one action per round; `engine.step_simultaneous(a1, a2)` resolves both.
- **Collision rule**: if `a1 == a2` and both are placements, the cell stays empty — *mutual annihilation*. Neither piece is placed; influence is unchanged. (Confirmed in `engine_v2.py:223–228`.)
- **Both pass**: ends the game as a draw immediately (`_end_by_double_pass`, R13 fix).
- **Movement actions are not legal** in sim mode (engine raises `NotImplementedError`).

### Action types
- `action_types = ["place"]`. Place on any empty cell. `first_move_anywhere = True` (no special opening). No movement, no capture.

### Capture / CA
- `capture_type = "none"` — no captures, no CA. Stones, once placed, cannot be removed.

### Propagation — influence
- `prop_type = "influence"`, `radius = 1`, `strength ≈ 1.0388`, `decay ≈ 0.3712`.
- On placement, the placed cell's `board_values` gets `±strength` (P1=+, P2=−). Each radius-1 neighbour gets `±strength · decay¹ ≈ ±0.3856`.
- Effective per-stone self-contribution to your effective score: 1.039 (own cell value, assuming the cell has no opponent value already on it).
- A friendly Moore-adjacent neighbour adds an extra +0.386 to *your* effective score (because it adds influence to a cell you own).
- An adjacent enemy stone subtracts ~0.386 from your effective score (their negative influence lands on your cell).

### Win condition — threshold
- `condition_type = "threshold"`, `threshold = 30.751`, `target_dimension = 0`, `max_turns = 100`.
- Win condition: a player's effective score = sum of `board_values[c]` over cells they own (sign-flipped for P2) must exceed 30.751.
- **R16 margin-based resolution** (`_check_threshold`, `engine_v2.py:826`): if both cross on the same tick, larger margin wins; equal margins → **draw**.
- Max-turns fallback: at step 100, majority by piece count (draw if equal). Double-pass: immediate draw.

### Quick degeneracy / sanity flags
- **DETERMINISTIC-MIRROR DEADLOCK (significant flaw).** Two deterministic greedy bots (each picks the cell that maximizes its own effective gain, ties broken by lowest cell index) collide every round forever. I ran this and got 50/50 collisions, board still empty. The game requires the agents to randomize tie-breaking or otherwise break symmetry; otherwise no game progresses.
- **Pass = always draw.** A losing player can pass; if the leader also passes (or after both pass once), the game is over as a draw. This caps maximum decisive value: a leader is forced to keep playing every round, but if both decide to pass it's a draw. Note: both-pass ends the game *on the same round*, no setup of "consecutive double pass" is needed. This is a valid escape valve.
- Threshold 30.75 is reachable. With N stones contributing self-value 1.039 and average ~2 friendly Moore neighbours each (+0.386 × 2 = 0.772 per stone), reaching 30.75 takes ~17 stones. Random play games hit threshold around step 30–35 (verified). Greedy clustering reaches it in 11 rounds (≈11 stones each, with high cluster bonus).
- No CA (uses_ca = False) so no dead CA rules to worry about.

---

## Phase 2 — Strategic Play

All moves engine-verified via `engine.step_simultaneous(a1, a2)`. Action coords are `(x, y)` with id = `y*8 + x`. Action 64 = pass.

### Game 1 — P1 = pure greedy cluster, P2 = greedy + opponent-deny

P1 picks the placement that maximizes its own effective score gain (1.039 + Σ neighbour-contributions, weighted by Moore distance and ownership). Tie-break: random among top-3 (seed 1). P2 uses same gain function plus a 0.7× weight on "what would my opponent gain from this cell"; tie-break top-3 (seed 2).

Pre-move reasoning: an empty corner gives 1.039 (self) and seeds future cluster growth. A 4-cell corner cluster yields 4·1.039 + (2 edge-adjacencies + 2 diag-adjacencies) × 0.386 ≈ 5.7 effective. P1 anticipated P2 would mirror centrally; instead P2 chose its own corner.

| R | P1 | reason | P2 | reason | P1 eff | P2 eff |
|---|---|---|---|---|---|---|
| 1 | (6,5) | seed corner | (0,7) | seed corner | +1.04 | +1.04 |
| 2 | (6,6) | extend cluster | (1,7) | extend | +2.85 | +2.85 |
| 3 | (7,5) | extend | (1,6) | extend | +5.43 | +5.43 |
| 4 | (7,6) | fill 2×2 | (2,7) | fill | +8.78 | +8.01 |
| 5 | (5,5) | extend | (0,5) | extend | +11.36 | +9.82 |
| 6 | (6,4) | extend | (0,6) | extend | +14.72 | +13.94 |
| 7 | (7,4) | extend | (1,4) | extend | +18.07 | +15.75 |
| 8 | (5,4) | extend | (2,5) | jump | +21.42 | +18.34 |
| 9 | (5,6) | extend | (3,6) | jump | +24.77 | +20.92 |
| 10 | (6,7) | extend | (2,4) | extend | +28.13 | +23.50 |
| 11 | (5,7) | extend | (1,5) | extend | +31.48 | +29.16 |

**Result**: P1 wins at step 11. P1_eff = 31.48 (margin +0.73 over threshold), P2_eff = 29.16 (still 1.59 short).

P1 reflection: pure cluster greedy works — every neighbour-completing placement gains ≈3.35 (1.039 + 6 friendly Moore neighbours? actually the cell I'm filling already has +0.386 each from existing friendly neighbours, so its own value gives me extra). Winning move was choosing exclusively cluster-extension cells. P2's "deny" weighting actually slowed it down because it forced P2 to consider P1's cluster, but its own cluster suffered from less consistent extension. Surprised that even with deny logic P2 lost; deny on a non-contested area is wasted.

P2 reflection: deny weighting was poorly calibrated — at this radius the propagation falloff is so steep (decay 0.37) that two clusters >2 cells apart are *strategically independent*. Denying P1's far corner does nothing. Better strategy: ignore opponent, race to threshold with maximum cluster density. Endgame reached threshold (decisive), not double-pass.

### Game 2 — P1 = edge sweep (column 0/1), P2 = greedy cluster (seed 3)

P1 commits to building down the left edge (cells 0,8,16,24,32,40,48,56 then 1,9,...). Hypothesis: edge cells have only 5 Moore neighbours (vs 8 interior), so own-stone density is higher per stone but cluster bonus is lower. The hypothesis was that low-collision and structural simplicity outweigh interior bonus.

| R | P1 | reason | P2 | reason | P1 eff | P2 eff |
|---|---|---|---|---|---|---|
| 1 | (0,0) | edge plan | (1,4) | greedy | +1.04 | +1.04 |
| 2 | (0,1) | edge plan | (0,5) | greedy | +2.85 | +2.85 |
| 3 | (0,2) | edge plan | (0,4) | greedy | +4.66 | +5.43 |
| ... | ... | ... | ... | ... | ... | ... |
| 12 | (2,2) | fallback (col 1 done) | (4,5) | greedy | +25.19 | +30.59 |
| 13 | (2,1) | fallback | (4,4) | greedy | +29.31 | +33.94 |

**Result**: P2 wins at step 13. P2 effective 33.94 vs P1 29.31. Edge sweep is a clearly inferior strategy: linear edge clusters lose ~25% of their potential cluster-bonus density compared with 2D interior clusters.

P1 reflection: edge sweep bad — interior cluster strategy outperforms because Moore adjacency gives 8 neighbours, and a 2D NxN cluster has more interior-pair bonuses than a 1×N column. Would switch to 2D cluster build next time.

P2 reflection: cluster-greedy is robust against any non-cluster strategy. Endgame reached threshold (decisive).

### Game 3 — SEAT SWAP of Game 1 (P1 = greedy+deny seed 2, P2 = greedy seed 1)

Same exact strategies as Game 1 but seats swapped. If the simultaneous mechanic eliminates seat advantage, this game should mirror Game 1 with the winner being whoever has the better strategy.

| R | P1 | reason | P2 | reason | P1 eff | P2 eff |
|---|---|---|---|---|---|---|
| 1 | (0,7) | greedy+deny | (6,5) | greedy | +1.04 | +1.04 |
| ... | ... | ... | ... | ... | ... | ... |
| 11 | (1,5) | greedy+deny | (5,7) | greedy | +29.16 | +31.48 |

**Result**: P2 wins at step 11, with the same 31.48 vs 29.16 split. **Same strategy wins regardless of seat.** Both games used 11 rounds and produced identical final effective scores. This is *strong* evidence the seat is symmetric and the winner is determined by strategy quality.

P1 reflection (game 3): playing the deny strategy in P1 seat was just as bad as in P2 seat. The mechanic itself is genuinely seat-symmetric. Endgame reached threshold (decisive).

### Strategy guides

**P1 strategy guide**:
1. Pick a single corner or edge as your build site (corners give 3 cluster-growth neighbours; interior 4×4 gives 8 but exposes more flanks to opponent influence).
2. Greedy: each round, place the empty cell that maximises (own self-value 1.039 + sum over already-friendly Moore neighbours of 0.386 + on-cell bonus from existing friendly influence). Don't bother with "deny" weighting unless opponent's cluster is within 2 cells of yours.
3. Randomize among top-3 candidates each round; otherwise you collide on cell 0 forever against a mirror.
4. Aim for ≥9-stone 2D cluster. With 11 stones in a 3×4 block you cross threshold.
5. Never pass first; passing only locks in a draw.

**P2 strategy guide**: identical. The game is seat-symmetric; the only optimization is *avoid opponent's influence cone* (build on the opposite side of the 8×8 board).

---

## Phase 3 — Strategic Analysis (joint, P1 + P2)

**Acknowledgment of seat-identity bias**: a single agent ran both seats. Phase 2 Games 1 and 3 are seat-swap pairs and produce mirror-identical results, which mitigates this concern for this specific game.

**Distinct viable strategies**: Limited. The dominant strategy is "build the densest 2D cluster you can in the corner farthest from the opponent's cluster". Variants:
- *Mirror cluster*: place opposite the opponent — this is what made Games 1 and 3 produce identical scores.
- *Aggressive intrusion*: place adjacent to opponent's cluster to subtract their influence. This costs you cluster density. Math: an enemy stone you place in their cluster loses you 1.039 self (you place on a cell with their −0.386 already there → only +0.65 net) and subtracts at most 0.386 from each of their stones. So you spend ≈1.04 to remove ≈3 × 0.386 = 1.16 from them — narrowly positive in expected value, but only if you can place adjacent to ≥3 of their stones. Requires waiting until they cluster up, by which time they're already winning. **Non-viable in practice.**
- *Edge sweep*: dominated by 2D cluster. (Demonstrated in Game 2.)
- *Pass abuse*: passing just trades for a draw. The leader will not pass, so the trailing player passing only forces draw at best.

**Counter-play**: very weak. Because propagation has decay 0.37 and radius 1, two clusters >2 cells apart have no interaction. The game decomposes into two parallel single-player score-builders racing to 30.75. The simultaneous mechanic only matters when players target the *same* cell, and clusters in opposite corners never share a target. After move 1, every round is essentially independent ("solitaire score-up").

**Short-term vs long-term tension**: minimal. Greedy local maximization is optimal because the propagation field is very local (radius 1, fast decay). There is no equivalent of Go's "moyo" or Hex's "bridges" — every placement's value is fully determined by its 1-step neighbourhood at the time of placement.

**Emergent concepts**: 
- Tempo / race: yes, both players race to threshold; the one whose cluster is denser per piece wins.
- Mutual annihilation: technically present (collisions), but in practice greedy agents pick different far-apart corners so collisions don't happen after random tie-breaking.
- Influence territory: vestigially present but non-interacting (decay 0.37 makes the "field" 1-cell-thick).
- Initiative / first-move advantage: **none** (see seat balance below).
- Ko fights, captures: absent by design.

**Topology mattering**: Moore vs grid (4-neighbour) matters quantitatively. With Moore, a corner stone has 3 cluster-growth neighbours (each at 0.386); with grid it would have 2. Cluster bonus per piece is higher under Moore by ~50% in the interior. Switching to torus would dramatically change strategy: corners would no longer be defensive havens, and influence would wrap, creating contested zones — much more interesting. As-is on bounded Moore, the corners are unambiguous best build-sites.

**First-mover advantage**: 
- In simultaneous play, "first mover" is meaningless — both move per round.
- Empirically: my 20-game **greedy-vs-greedy seat-balance probe** (top-3 randomised tie-break) returned **P1=9, P2=8, Draw=3**. That's near-perfect symmetry. The R16 simultaneous mechanic + R16 margin-based threshold resolution have eliminated the seat bias.
- Phase 2 Games 1 and 3 (deliberate seat swap) confirm: same strategy wins regardless of seat, with bit-identical effective scores.

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary case — "this is not novel"

(a) **Catalog comparison.** This game is essentially **Reversi/Othello with simultaneous moves and influence-radius scoring instead of flipping**, on a smaller board with no captures. Specifically:
- *Reversi* uses 8-neighbour line-flips; this uses 8-neighbour additive influence with decay.
- *Tumbleweed* uses sightline-based piece strength on a hex board — same flavor (board-position adds value to neighboring cells); this is just Tumbleweed-on-Moore-with-decay-0.37.
- *Slither / Lines of Action / Connect6*: not closely related (those have movement / line wins).
- *Go*: fundamental difference — no captures, no liberties. Stones, once placed, are permanent and inert except for their influence cone. Strategically much shallower than Go.
- *Hex / Y / Havannah*: connectivity-based; this is sum-based. Different family.

(b) **CA literature**: doesn't apply (no CA).

(c) **Simultaneous-game literature**: 
- *Diplomacy* / *Blotto* / *Gungo* / *Rock-Paper-Scissors-scaled*: In simultaneous-action games the meaningful tension is *anticipating opponent's identical-target choice* — bluff, mixed strategies, prediction.
- This game's payoff structure removes that tension: clusters in different corners never share a target cell, so bluffing/prediction never matters. Effectively it's **two parallel solitaires** with a max-turn budget.

(d) **Re-skin claim**: Genuinely close to "**simultaneous Reversi-without-flipping on Moore-8 with influence-decay scoring**" or "**simultaneous Tumbleweed-with-decay**". An expert at Reversi or Tumbleweed would transfer almost immediately — the only new thing to learn is the collision rule, which is trivial.

(e) **Expert transfer test**: A Tumbleweed expert told "place on Moore-8 grid, score = Σ value-on-your-cells, threshold 30.75, simultaneous moves with collision = annihilation" would be at a competent level within 5 minutes. The strategic landscape is just "build dense cluster, far from opponent". No novel mechanic emerges from the simultaneous resolution because clusters don't share targets in the equilibrium strategy.

### Rebuttal (P1 + P2)

The adversary's strongest point is the Tumbleweed analogy. But two real differences:
1. **Decay 0.37 + radius 1** makes influence essentially binary (cell-and-neighbour only), unlike Tumbleweed's sightline-based decay-by-distance which can stretch across the board. Strategic feel is much more local.
2. **Simultaneous + collision = mutual-annihilation** is a real novel rule, but Phase-2 evidence shows it almost never fires in equilibrium play (deterministic-mirror was the only setup that triggered chronic collisions, and that's a buggy strategy not a real game position).

So the adversary mostly wins. The ostensibly novel mechanic (simultaneous + collision) is degenerate in this parameterisation because the influence radius is so small that the natural strategy splits the board into independent corners. **The mechanic is novel in name; in practice it does not change play.**

**Novelty score**: **3 / 10**. Closest analog: Tumbleweed-on-Moore-with-decay + simultaneous-collision-stub. The simultaneous mechanic does not alter strategy because game decomposes into independent races.

---

## Phase 5 — Verdict

```
Team ID: team-9
Game ID: f8dbeb3079a5
Rules Summary: Simultaneous-placement game on 8×8 Moore-non-wrap board; no captures; placing a stone adds +1.04 self-influence and ±0.39 to each Moore-neighbour (sign by player); first to sum effective influence > 30.75 wins; collisions on identical target = mutual annihilation (cell stays empty).
Topology: 8×8 grid, Moore (8-neighbour) adjacency, NO wraparound.
Turn Structure: SIMULTANEOUS (engine.step_simultaneous(a1, a2)); collision = mutual annihilation; both-pass = draw.
```

### SCORES (1–10)

- **Strategic Depth: 3** — the influence radius (1) and decay (0.37) localise interactions so much that the game decomposes into two parallel single-player score-races. Greedy local maximisation is near-optimal. No emergent territory, tempo, or mutual-threat tension.
- **Emergent Complexity: 2** — no captures, no CA, no ko, no movement; collisions theoretically interesting but rare in equilibrium play. Two clusters in opposite corners never share a target. The "simultaneous" mechanic is a strategic null in this parameterisation.
- **Balance: 9** — 20-game greedy-vs-greedy probe: P1=9, P2=8, Draw=3. Phase-2 seat-swap (Game 1 vs Game 3) produced bit-identical effective scores (31.48 vs 29.16) with the *same strategy* winning regardless of seat. R16 simultaneous + margin-threshold genuinely eliminate seat bias. *(Caveat: a sample of 20 greedy games has confidence interval roughly ±20%; deeper sampling could refine.)*
- **Novelty (post-adversary): 3** — Tumbleweed-with-decay + simultaneous-collision-stub. Simultaneous mechanic does not produce novel dynamics because the radius/decay parameters make targets non-overlapping in the equilibrium.
- **Replayability: 3** — once you find "build a 2D cluster in a corner far from the opponent" the game is essentially solved at the strategic level. The only variability is which corner, and that's symmetric. After a few games there's nothing new to discover.
- **Overall "Would I play this again?": 2** — short (11–35 rounds), perfectly balanced, but mechanically thin. Functional as an RL benchmark exactly *because* it's clean and balanced, but not interesting as a human game.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed** with two key changes: (1) on Moore-8 grid with hard fast decay (0.37) instead of hex sightlines, (2) simultaneous-moves with mutual-annihilation collision instead of alternating. The mutual-annihilation rule is a real change but never fires in equilibrium play.

### KILLER FLAWS

1. **Deterministic-mirror deadlock**: two greedy bots with deterministic tie-breaking can collide indefinitely (50/50 collisions in a 50-round test). Real play requires explicit symmetry-breaking. This is a soft flaw — RL agents will learn stochastic policies — but it means the game is undefined for purely deterministic agents.
2. **Strategy collapse**: cluster-in-corner-greedy dominates the strategy space. Non-cluster (edge-sweep) strategies lose by 4-5 effective. There is no meaningful counter-play because the influence radius (1) and decay (0.37) localise effects so far that opposite-corner clusters never interact.
3. **Pass-to-draw**: the trailing player can always force a draw by passing (both-pass ends as draw). This means decisiveness depends on the leader continuing to move, which they will, but the trailing player has zero incentive to keep playing once they realize they are behind. (Mitigated by the fact that both-pass is required, but in equilibrium a leader will keep playing and the trailer is forced to keep playing too because passing solo doesn't help them; the rule is harmless here but worth flagging.)
4. **No interaction between clusters**: with decay 0.37 and radius 1, two clusters separated by ≥2 cells exert no influence on each other. In the empirical games, the two clusters never touched.

### BEST QUALITY

The seat-balance is genuinely excellent. Empirically (20 games + seat-swap) the simultaneous mechanic with R16 margin-based threshold resolution removes the first-player advantage cleanly. This is a *positive demonstration that R16's engine fixes work*, even if the underlying game strategy is shallow. As a sanity-check fixture for the engine, this game is good evidence the R16 fixes are correctly calibrated.

### IMPROVEMENT IDEAS

The single change that would deepen this game most:

- **Increase influence radius to 2 (or 3) and reduce decay to ~0.7**, so opposite-corner clusters interact. Currently with radius 1 / decay 0.37, two clusters >2 cells apart have zero strategic interaction. With radius 2 / decay 0.7, an interior stone projects ±1.04 self, ±0.73 to 8 r=1 neighbours, ±0.51 to 16 r=2 neighbours — meaning a stone placed near the opponent's cluster can drain ≈3.5 effective from them at the cost of ≈1.04 self. That creates real strategic tension: do I race or attack? It would also make the simultaneous-collision mechanic actually matter because contested cells would be common.

Alternative single change: **switch topology to torus**. That makes corners non-special, makes "build in a far corner" unavailable, and forces clusters to interact along the wrap. Lighter-touch fix and probably what the generator should have produced.

---

## Appendix — Engine-verified raw data

### 20-game greedy-vs-greedy probe (top-3 stochastic tie-break)
- P1 wins: 9 / 20 (45%)
- P2 wins: 8 / 20 (40%)
- Draws: 3 / 20 (15%)

### Phase-2 game move logs (action ids)

- Game 1 P1 vs P2 (cluster vs deny): `[(46,56),(54,57),(47,49),(55,58),(45,40),(38,48),(39,33),(37,42),(53,51),(62,34),(61,41)]` → P1 wins 31.48 vs 29.16, 11 steps.
- Game 2 P1 vs P2 (edge sweep vs cluster): `[(0,33),(8,40),(16,32),(24,41),(48,49),(56,42),(1,34),(9,50),(17,43),(25,51),(57,35),(18,44),(10,36)]` → P2 wins 33.94 vs 29.31, 13 steps.
- Game 3 P1 vs P2 (deny vs cluster, seat swap of game 1): `[(56,46),(57,54),(49,47),(58,55),(40,45),(48,38),(33,39),(42,37),(51,53),(34,62),(41,61)]` → P2 wins 31.48 vs 29.16, 11 steps.

### Engine quirks confirmed
- `sim_play_helper.py render()` says "torus" even when topology is `moore` non-wrap (line 28). Verify topology by reading the rule JSON, not the render header.
- Action 64 = pass.
- `engine.topo.get_neighbors(c)` (not `neighbors`).
- Action ids: `y * axis_size + x` confirmed, e.g. `(3,3)` → 27, `(0,0)` → 0, `(7,7)` → 63.
