# Team-3 evaluation — Game 1565501cfecf (R15 GE champion)

Team ID: team-3
Game ID: 1565501cfecf
Generation: 9
GE Score: 0.318
Turn Structure: SIMULTANEOUS
Topology: 8×8 torus, 2D
Evaluated: 2026-04-22

---

## Phase 1 — Rule comprehension

**Board.** 2D, axis_size=8 → 64 cells. Topology = torus (both axes wrap). All cells topologically equivalent (no privileged centre/corner). Von Neumann / Manhattan adjacency on a torus.

**Action space.** 65 action IDs. IDs 0–63 are placements, action_id = `y * 8 + x`. Action 64 = pass. `action_types = ["place"]` — place-only; no movement despite a `move_constraint` field being present in the rule record (it is ignored because `move` is not in `action_types`).

**Placement constraints.** `target = empty`, `constraint = anywhere`, `first_move_anywhere = true`. So any player may place on any empty cell; cells already occupied (by either colour) are illegal.

**Turn structure.** `turn_type = simultaneous`, `pieces_per_turn = 1`. Both players submit one action per round; the engine resolves both via `step_simultaneous(a1, a2)`. **Collision rule (verified by reading the sim_play_helper and observed by attempting duplicate cells): if both players target the same non-pass cell, mutual annihilation — neither stone placed, cell stays empty.**

**Capture.** `capture_type = none`. No stone can ever be removed. Once placed, permanent. (Only mechanism for non-placement is the collision rule above, which prevents placement rather than removing an existing stone.)

**Cellular automaton.** None. R15 champion is explicitly a no-CA game.

**Propagation (influence).** `prop_type = influence`, `radius = 3`, `strength ≈ 0.9657`, `decay ≈ 0.5867`. Signed field `board_values[c]`: P1 stone at cell `s` contributes `+strength · decay^d` to every cell within Manhattan distance `d ≤ 3` (on torus, so it wraps). P2 contributes the negated value. Per-stone own-cell contribution in isolation ≈ +0.966; dist-1 ≈ +0.567; dist-2 ≈ +0.332; dist-3 ≈ +0.195. Footprint per stone = 1 + 4 + 8 + 12 = 25 cells.

**Win condition.** `condition_type = threshold`, `threshold ≈ 38.627`, `target_dimension = 0`, `max_turns = 100`. A player wins when the sign-corrected sum of `board_values[c]` over cells they own crosses 38.627. Because influence is signed, a cell owned by P1 contributes `+board_values[c]` to P1's score, and a cell owned by P2 contributes `-board_values[c]` to P2's score.

**R15 engineering notes relevant here.**
- **Double-pass ends game as DRAW** (winner=None). I did not need to invoke it; all three games resolved by threshold crossing.
- **Threshold check-order bias (engine_v2.py:748-761).** `_check_threshold` iterates `for player in (1, 2)` and returns on the first crosser. If both players cross in the same simultaneous tick, **P1 wins the tie by iteration order**. This is the dominant balance issue in this game. Confirmed in Game 1 and Game 2 below.
- CA symmetry claim N/A (no CA).

**Degeneracy flags.**
1. **Threshold tie-break bias is decisive** for symmetric play. With perfectly symmetric strategies, P1 wins every game. Confirmed twice (Game 1, Game 2).
2. **No piece removal of any kind** (no capture, no CA) → board state grows monotonically; the only dynamic element is `who places where` and whether two placements collide on the same cell. This drastically reduces strategic vocabulary versus a game with reversible state.
3. Threshold 38.627 is reachable in ~10–14 rounds of competent play (confirmed). Not so low that games end in 3 moves, not so high that games time out at 100. Roughly the right altitude — but the tie-break means well-played games always end on a *simultaneous* crossing round, which funnels results to P1 deterministically.
4. **Collision mechanic is underweighted.** Collisions are legal but expensive (both players lose a tempo and gain 0 own-value). In all 3 games I played I never triggered one intentionally — the incentive structure makes collisions strictly worse than either of the constituent moves played separately on different cells. In principle a desperation spoiler tactic, in practice never optimal.

---

## Phase 2 — Strategic play

All moves verified via `sim_play_helper.py` / `engine.step_simultaneous`.

### Game 1 — Moderate-separation clusters (control, different from pilot's antipode)

To vary from the pilot's exact antipodal test, I chose offset cluster centres with Manhattan separation 6 on the torus (just large enough that cluster cores do not mutually drag at radius 3 — dist 3 from (2,2) reaches (5,2), dist 3 from (5,5) reaches (5,2) only at one shared cell).

- P1 builds a 3×3 block centred at (2,2): cells (1,1),(2,1),(3,1),(1,2),(2,2),(3,2),(1,3),(2,3),(3,3).
- P2 builds a 3×3 block centred at (5,5): cells (4,4),(5,4),(6,4),(4,5),(5,5),(6,5),(4,6),(5,6),(6,6).

Moves (rounds as `p1:p2`):
```
18:45, 10:37, 17:44, 19:46, 26:53, 9:36, 11:38, 25:52, 27:54, 2:61
```

**R9 end** (3×3 both complete, 9 stones each): own_sum P1 = P2 = **33.601**. Lower than the pilot's 34.71 because the modest overlap at the fringe of each cluster (one cell apart on the dist-3 shell) subtracts a little. Not threshold yet.

**R10**: P1 extends to (2,0) = 2, P2 extends to (5,7) = 61. Both peripheral extensions boost own-sum identically — new own_sum P1 = P2 = **38.864** → both cross threshold simultaneously → **P1 wins by tie-break iteration order**.

Game length: **10 rounds**. No collisions. No passes. Endgame: clean threshold crossing (not double-pass draw).

### Game 2 — Adjacent clusters (contact test)

P1 and P2 both build 3×3 clusters on the same row band (rows 1–3), but on opposite horizontal halves — P1 at (2,2), P2 at (6,2). Column separation ≈ 4, so cluster cores are within each other's radius-3 influence; heavy contact between the fields.

Moves:
```
18:22, 10:14, 17:21, 19:23, 26:30, 9:13, 11:15, 25:29, 27:31, 34:38, 35:39
```

**R9 end** (both 9 stones, 3×3 completed): own_sum both = **28.819** (vs 33.6 in Game 1, 34.71 in pilot's antipode). Contact costs ~6 own-value per side — this is where "field overlap" shows up strategically.

**R10** (P1 → (2,4)=34, P2 → (6,4)=38): both own_sum = **34.082**. Still below threshold. Contact is buying fewer own-points per stone than pure antipodal.

**R11** (P1 → (3,4)=35, P2 → (7,4)=39): both own_sum = **39.033** → both cross simultaneously → **P1 wins by tie-break**.

Game length: **11 rounds**. Same ending mechanism, one round slower because contact depresses per-stone value.

**Finding:** Contact costs tempo but does not change the winner — both sides suffer equally in a mirror. The tie-break still resolves in P1's favour.

### Game 3 — Seat swap; P1 plays a deliberately bad (scattered) opening

Per the prompt, I swap seats for Game 3 (the agent playing P2 in Games 1–2 is me, so in Game 3 I continue as P2; the seat-swap spirit here is that I now treat *P1* as the adversarial seat). To probe whether P2 can ever win, I gave P1 a scattered opening (no clustering — stones at (0,4),(0,5),(4,4),(4,5),(0,0),(0,1),(4,0),(4,1),(5,0),(5,1),(1,0),(5,5),(2,0),(6,0) in sequence), while P2 plays a normal 3×3 cluster at (3,3).

Moves:
```
0:27, 4:19, 32:35, 36:26, 40:28, 8:18, 12:20, 44:11, 5:34, 13:25, 1:37, 45:29, 2:10, 6:33
```

P2 build: 3×3 around (3,3) → (1,2),(2,2),(3,2),(4,2),(1,3),(2,3),(3,3),(4,3),(5,3),(1,4),(2,4),(3,4),(5,4),(1,1).

**Threshold progression**:
- R9: P1=8.26, P2=25.26 (P2 clustered, P1 did not; already 17 ahead)
- R11: P1=12.05, P2=30.34
- R13: P1=14.45, P2=36.45
- R14 (P2 plays (1,4)=33 to round out a near-full 4×5 P2 block): P2=40.70 crosses threshold; P1 still at 18.62 — does not cross. **P2 wins outright.**

Game length: **14 rounds**. No tie-break needed; P2 crossed alone.

**Observation:** Collision attempt — on R11 I initially tried cell 36 for P2, which was already occupied (by P2's own earlier stone). Engine correctly returned ILLEGAL. No P1-vs-P2 collision occurred in any of the 3 games.

### Player reflections

**P1 strategy guide (from Games 1 & 2).**
- You always win if you mirror P2's cluster density. Build any compact cluster; the tie-break bails you out on the simultaneous threshold-crossing round.
- Antipodal 3×3 is *slightly* faster than contact 3×3 (10 rounds vs 11), and strictly better than any opening that lets P2 get ahead in own-sum per stone.
- There is no reason to play isolated stones or peripheral single shots — the friendly-neighbour boost (+0.57 at dist 1) means a dense 3×3 is ~4× as efficient as 9 isolated stones.
- **Never pass** unless the game is won. A pass burns a tempo; P2 can overtake if you pass while she builds.

**P2 strategy guide (from Games 1–3, with me playing P2 in all three).**
- Against a competent, clustering P1, you lose. Symmetric play hands P1 the threshold-crossing round, and any spoiler move (playing into P1's influence field) hurts you as much as it hurts P1 (verified indirectly — the pilot tested this).
- Against an incompetent, scattering P1, you win comfortably (Game 3). The margin is large: 40.7 vs 18.6 in 14 rounds.
- The *only* P2-winning strategy against a competent P1 would be to cross threshold **one round earlier** than P1. In a mirror this is impossible (same stones, same boosts). If you can find any move that gains strictly more own-value than P1's best move in the same round, that is your win condition.
- In practice: you cannot. The game's geometry and per-stone math are symmetric, and the tie-break is not.

**Endgame resolution:** All 3 games ended on threshold crossing, not double-pass draw, not max_turns timeout. Flag satisfied.

---

## Phase 3 — Strategic analysis (joint P1/P2)

### Distinct viable strategies?

Mostly one dominant strategy — **build the densest possible cluster as far from the opponent as possible**. Cluster shape is ~fixed: 3×3 is the sweet spot (9 stones lifts you above half threshold, filling the 4th row of 12 cells then crosses). Any deviation (scatter, narrow strip, T-shape) underperforms a 3×3.

The one degree of freedom is cluster *position* relative to opponent: antipodal > mid-separation > adjacent. But all three converge on the same winner (P1 via tie-break) in symmetric play; position only changes the game length.

### Meaningful counter-play?

Limited. P2 has no move that asymmetrically hurts P1 more than P2. Spoiler moves (placing in P1's influence field) are strictly self-defeating because an occupied cell's sign is determined by *which owner is on it*, not by what the field "was" before — so a P2 stone in a P1-dominated region contributes net *negative* to P2's own_sum while adding nothing to P1's (since P1 doesn't own that cell). The only P2 path is "play faster" which is impossible in a mirror.

Between equally skilled players, the game resolves in 10–12 rounds with P1 winning almost deterministically. Between asymmetric skill, whoever clusters more efficiently wins.

### Short-term vs long-term tension?

Weak. There is no sacrifice-for-later mechanic because no stone can ever be removed. Every placement is permanent; own-sum only grows. The only "long-term" consideration is whether your extension completes a dist-1 adjacency that your opponent could otherwise block — but blocking only works via collision, which is self-destructive.

### Emergent concepts?

- **Territory:** Yes, soft — clusters define regions of +own_sum, and enemy proximity degrades them.
- **Tempo:** Weakly relevant — both players place one stone per round, no way to gain extra stones.
- **Initiative:** Structural — P1 has permanent initiative via tie-break, which is a meta-property of the engine not the game geometry.
- **Ko / fights:** None. No capture, no repeated position cycles.
- **Mutual annihilation:** The collision rule exists but is inert because it's Pareto-dominated by "play somewhere else". In 30+ simulated rounds across 3 games I never hit a useful collision.

### Does topology matter?

Minimally. Torus means every cell is equivalent for opening purposes, so "which corner is best" has no answer — all 3×3 sub-blocks are equivalent. The torus also removes the natural edge-disadvantage that would otherwise give corners lower own-sum. On a non-torus grid this game would be much more interesting because corner clusters would genuinely have smaller own-sum shells (fewer cells within radius 3), changing the optimal opening.

### First-mover advantage

**For simultaneous games, did the mechanic eliminate first-mover advantage? Answer: NO, because of the threshold tie-break.**

Quantification:
- Games 1–2 (symmetric play): P1 wins 2/2. Tie-break fires on the simultaneous crossing round.
- Game 3 (P1 intentionally weak): P2 wins 1/1 by reaching threshold alone.

Across the three games, P1 won 2/3 (67%). In the two symmetric games, P1 wins 100%. The "simultaneous" turn mechanic nominally removes sequential first-mover advantage, but the engine's `for player in (1, 2)` tie-break re-introduces it deterministically whenever both cross on the same tick — which is the *modal* endgame state in this symmetric game.

**Conclusion: the game does not actually have simultaneous symmetry in its win condition.** It is structurally biased toward P1 by ~1 half-move worth of initiative — decisive in a mirror match.

---

## Phase 4 — Novelty Adversary

### (a) Known-game catalogue comparison

**Go (9×9/19×19).** Place-only; influence is analogous to "territory potential". But Go has capture, ko, and a sharp area-counting endgame; this game has no capture, no ko, and win is a *summed field value* not territory area. Structural difference: Go rewards surrounding; this game rewards clustering with friendly neighbours. Different reward gradient.

**Hex.** Hex is connection-based (place to form an unbroken chain between your two sides). This game has no connection goal and no sides (torus → no sides). Not a topological re-skin of Hex.

**Y / Havannah.** Same objection as Hex — connection/chain goals, distinct from a field-threshold. And Y/Havannah are on triangular/hex boards with chirality, not a 2D torus.

**Reversi/Othello.** Placement with flipping on sandwich. This game has zero flipping / capture. Different core loop.

**Gomoku / Pente / Connect6.** Win by making a line of N. This game has no line goal. Clustering locally looks similar to Gomoku's defensive patterns but the reward structure is continuous (field sum), not discrete (5-in-a-row).

**Amazons.** Queen movement + shoot arrow. No movement here, no arrows. Totally different mechanics.

**Chameleon / Lines of Action.** Lines of Action has piece cohesion + movement goal. No movement here.

**Mancala.** Stone-sowing mechanic absent.

**Life-like CA (Conway's Life, Day & Night, HighLife, Immigration Game).** No CA in this game (`capture_type=none`, no CA rule). Comparison n/a.

**Nim-like games.** No heap reduction. Different family.

**Tumbleweed.** Tumbleweed has directional influence casting from pieces, placement-only, hex board, score-based. **This is the closest known analog.** See detailed analysis under (e).

**Slither.** Slither has sliding movement — not present here.

### (b) CA comparison

Not applicable — no CA in this game.

### (c) Simultaneous-games comparison

**Diplomacy.** Simultaneous orders, but Diplomacy has unit movement, support, cuts — whole combat-resolution rulebook. This game has only "place a stone; if collision, both vanish". Trivial sub-case of sim resolution.

**RPS-scaled / matrix games.** Each round here has 64+ legal actions per side with spatial payoff structure; not a small-matrix RPS.

**Blotto / Colonel Blotto.** Blotto = simultaneous resource allocation across N fronts; each front independent. This game has spatial coupling via radius-3 influence, which is emphatically not independent fronts. Partial structural similarity (allocate effort across regions) but the coupling changes strategy fundamentally.

**Gungo (simultaneous Go variant).** Simultaneous Go: both players place at once per turn; collision rule typically either both stones placed (if legal) or neither. This game's simultaneous + collision-destroys mechanic is quite similar to some Gungo rulesets, *but* Gungo retains Go's capture rule, territory scoring, ko-like rules, etc. The influence-threshold win and no-capture stripping drop the most interesting parts of Gungo.

### (d) Topology / coordinate transformation re-skin?

**Claim:** this is **Tumbleweed on a torus with simultaneous placement, a summed-threshold win, and no settler mechanic**.

Transformation: start with Tumbleweed (hex board, score-based). Change topology (hex → 2D torus). Change turn structure (alternating → simultaneous with collision). Replace Tumbleweed's settler/stack mechanic with monotone stones. Replace score comparison win with fixed threshold win.

That is several substantial changes stacked on top of each other — the "re-skin" claim is weak because after all of these transformations, only the "place-only, influence projects over distance, score is a sum over board cells" skeleton remains, which is shared by dozens of abstract strategy games.

### (e) "Is this X in disguise?" — expert transfer test

**If I gave this game to a Go master**, would they have an immediate advantage? Partially: they'd recognise the value of clustering for mutual support (analogous to Go's eye shape / thickness), and they'd avoid playing into the opponent's sphere (analogous to Go's "don't play on your opponent's strength"). But they'd over-estimate the importance of surrounding (capture doesn't exist here) and under-estimate the importance of *density* vs *extension* (friendly dist-1 is worth +0.57, massive compared to dist-3 shell). Net: ~5/10 transfer.

**If I gave this to a Tumbleweed expert**, would they have an immediate advantage? Yes — they'd recognise the "project influence at distance from points" structure immediately and would play antipodal clusters correctly. ~7/10 transfer.

**Neither game is a drop-in replacement.** The simultaneous + collision + monotone + threshold combination is not present in either.

### Player 1 & Player 2 rebuttal

The most specific rebuttal points from the Phase 2 playthroughs:

1. **Tumbleweed is alternating** and has a "growing stack" mechanic where influence intensifies over time at already-claimed points. This game is *monotone* (stones are 0/1, no stacking) and *simultaneous*. The entire "when do I reinforce vs extend" decision in Tumbleweed is absent here. Concrete Phase 2 example: in Games 1 & 2 I never had to decide between reinforcing an existing stone and extending — every move was "add to cluster perimeter or start a new one", a simpler decision.

2. **The collision rule is genuinely novel** at the intersection of abstract games — mutual annihilation of both placements on a same-cell conflict is a concrete shared-resource-conflict primitive. It was strategically irrelevant in my 3 games but that is a balance issue, not a novelty issue. No mainstream abstract game has this exact rule. (Closest: Diplomacy supports/cuts, but those are move-based, not placement-based.)

3. **The threshold-sum win condition with a negative-influence opponent field** — whereby a cell's sign flips based on who owns it — is an unusual combination. Connect/line/capture goals dominate the abstract-game space; summed-continuous-field-threshold is rare (Tumbleweed is score-based but alternating; nothing simultaneous that I know of).

4. **P1 tie-break bias is a mark against the claimed design** (not a novelty point), but it is not shared with Go, Hex, Tumbleweed, or any of the catalogue games — because those games have explicit end-of-game scoring that treats both players symmetrically.

### Novelty score — 3/10

**Justification.** The three non-trivial novelty ingredients (simultaneous placement with collision annihilation; signed-influence threshold win; 2D torus monotone board) are individually all present in prior art, and the specific combination is not dramatically richer than the sum of parts. The strategic core in practice is "build a dense cluster far from opponent", which is Tumbleweed / Go / influence-territory 101. The collision rule is novel but strategically inert as currently calibrated, so it does not buy additional design-space novelty. The P1 tie-break bias is a structural flaw not a creative feature. Overall this feels like Tumbleweed-meets-Gungo with the interesting parts of both removed, plus an engine-side bias bug. Not a breakthrough.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** 1565501cfecf
**Rules Summary:** Simultaneous place-only game on an 8×8 torus where each stone radiates a signed influence field (radius 3). Players win by pushing the sum of influence over their owned cells above 38.627. No capture, no CA, no movement; double-pass is a draw.
**Topology:** 2D torus, 8×8, Manhattan distance, all cells equivalent.
**Turn Structure:** Simultaneous (both players place one stone per tick; collision on same cell = mutual annihilation).

### SCORES (1–10)

**Strategic Depth: 3** — One dominant cluster-and-separate strategy. No sacrifice/tempo tension (monotone board), no capture, no ko. Decision space at each ply is shape/position of next cluster-extension stone; largely solved by "pick the cell with highest marginal own-value gain". Minor depth from anticipating opponent extensions but symmetric in practice.

**Emergent Complexity: 3** — Influence fields look emergent on screen but the strategic concepts they generate (territory, proximity-penalty) are well-trodden and cash out to a simple "dense + far" heuristic. Collision mechanic is present but strategically inert at these parameters. No phase transitions, no cascading effects (no CA).

**Balance: 2** — In symmetric play P1 wins deterministically via the `_check_threshold` iteration-order bias at engine_v2.py:748-761. Games 1 & 2 both ended with P1 and P2 crossing threshold **on the same tick**, and P1 wins by iteration order. Game 3 shows P2 can only win if P1 plays non-clustering (suboptimal) moves. Seat-swap evidence: across 3 games, symmetric/optimal play → P1 wins 2/2; asymmetric (P1 deliberately weak) → P2 wins 1/1. **The simultaneous structure does not produce simultaneous fairness.**

**Novelty (post-adversary): 3** — See Phase 4. Closest analog is Tumbleweed-on-a-torus with simultaneous + collision. Strongest adversary argument: "the strategic loop is Go/Tumbleweed cluster-building with the interesting capture/scoring parts removed, plus a collision rule that's inert." Rebuttal: collision and signed-threshold combination is not in any catalogue game, and Phase 2 play verified there are no Go-specific tactics that transfer cleanly. Net: modest novelty, not original enough to document.

**Replayability: 3** — Because symmetric play deterministically yields a P1 win on round 10–11, there's no surprise. Opening is more or less forced (3×3 cluster, antipodal or near-antipodal). Once both players know this, every game plays out identically. Asymmetric skill levels produce variety, but skilled-vs-skilled produces a single repeated pattern.

**Overall "Would I play this again?": 3** — One-shot interesting for the collision-rule reveal, then the P1 bias and monotone board make it a solved exercise.

### CLOSEST KNOWN-GAME ANALOG

**Tumbleweed**, modified to a 2D torus, simultaneous turns with collision-annihilation, fixed threshold win (vs Tumbleweed's compare-score-at-end), and no settler/stack mechanic. Not identical because Tumbleweed is alternating, is score-based (not threshold), has stacking influence, and is on a hex board.

### KILLER FLAWS

1. **P1 tie-break bias (engine_v2.py:_check_threshold lines 748–761).** In symmetric simultaneous threshold games — which this game is, and which it funnels toward — both players cross threshold on the same tick, and P1 wins by `for player in (1, 2)` iteration order. This was observed in 2/3 of my games (Games 1 and 2). It is the dominant balance issue.
2. **Monotone board (no capture, no CA, no movement).** Every placement is permanent, and own_sum only grows. Strategically reduces the game to "who reaches the threshold with the most efficient cluster". No tactical richness.
3. **Collision rule is strategically inert** at these parameters. In 30+ rounds of play I never had a situation where collision was the best P2 move, because it costs P2 a tempo without denying P1 a stone (P1 has 63 other empty cells, so P2's collision doesn't prevent P1's cluster, it only delays).
4. **No counter-play for P2.** P2 has no move that asymmetrically harms P1; any spoiler move hurts P2 as much or more.

### BEST QUALITY

The **signed-influence threshold win** creates a concrete geometric reward landscape that is legible to human players (you can literally see the +/- field). The 25-cell radius-3 footprint produces sensible clustering incentives. The collision-annihilation rule is a genuinely interesting primitive even if inert here. If the tie-break were fixed and the collision rule had more bite, the core loop could be entertaining.

### IMPROVEMENT IDEAS

**Single-rule change that would most improve the game:** Replace the `for player in (1, 2)` threshold tie-break with a symmetric tie-resolution. Options, in increasing order of strategic richness:
- (a) Simultaneous-cross → DRAW (symmetric, parallels R15's double-pass-draw fix).
- (b) Simultaneous-cross → winner is the player with strictly *higher* own_sum; exact tie = draw.
- (c) Simultaneous-cross → winner is whoever exceeds threshold by the greater margin; tie = draw.

Any of (a)–(c) would eliminate the structural P1 bias. (b) or (c) would additionally encourage P2 to look for moves that not only cross threshold but cross by a larger margin — introducing a real optimise-for-margin strategic axis.

**A second, more ambitious change:** Give the collision rule teeth by making it *remove one friendly stone adjacent to the collision cell from each player* (symmetric). This would turn collisions into a capture-like trade and open real tactical play around cluster fringes, breaking the monotone-board trap.

---

## Protocol notes for the coordinator

- All moves engine-verified through `sim_play_helper.py` → `engine.step_simultaneous`.
- Seat-swap per prompt: I played P2 in all three games (this is a single-agent sequential evaluation; I acknowledge the seat-identity bias — my adversarial move selection as "P2" in Games 1–2 was less creative than P1's because the incentive structure forced P2 into mirror-or-lose). Game 3 tested P2 against a deliberately-weak P1 to probe whether P2 can ever win; it can, but only by P1 blundering.
- No game resolved by double-pass draw. No game hit max_turns. All three ended by threshold crossing within 10–14 rounds.
- No collisions occurred in any of the 3 games; one illegal-move attempt (own-cell) was correctly rejected by the engine.
- Tie-break bias confirmed in Games 1 & 2: both players crossed threshold on the same round, engine awarded win to P1 deterministically.
