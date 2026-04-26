# Team-15 Evaluation — Game 931c58ae59b4 (Run 14)

**Team ID:** team-15
**Game ID:** 931c58ae59b4
**Metadata:** R14 rank 3 by Go Essence (0.4824), ELO 3035 (highest on R14 leaderboard), alternating, seed game (gen 0 / gen-10 placement), v3 representation.

---

## PHASE 1 — RULE COMPREHENSION

### Board & topology
- 8×8 grid, 64 cells, two-dimensional.
- Topology: **Moore** (king-move 8-neighborhood; distance = Chebyshev max(|Δx|,|Δy|)).
- Action ID = `y * 8 + x`; 64 placement actions + action 64 = PASS (65 total).

### Turn structure
- **Alternating.** One placement per turn, players alternate (P1 starts). NOT simultaneous.
- Two consecutive passes trigger majority-piece-count tiebreak ("double-pass exploit" flagged in Run 13 — watch for it).

### Action types
- `place` only. No move/slide actions. `move_constraint` = "adjacent_empty" is ignored because `action_types` doesn't include move.

### Placement constraints
- Target: empty cells only.
- Constraint: **must be adjacent (Moore = 8-neighbor) to own stone**, except first move (`first_move_anywhere: true`).
- In practice: P1 places anywhere for move 1; both players thereafter grow their cluster from their existing stones only.

### Capture
- Type: **surround** (Go-style, threshold=1). On Moore topology, surround-capture is theoretically possible but requires removing ALL 8 liberties of an enemy group. In 3 games I played (23 moves each), **no capture ever fired** — the 8-neighbor structure makes capture effectively inert on this sized board until very late midgame at earliest. This is an engine quirk worth flagging: rule is there but never triggers in natural play.

### Propagation (influence)
- Type: **influence** (continuous field). Every placement adds a signed value to a 5×5 Chebyshev-radius=2 footprint centered on the placed cell.
  - Strength = 1.6155, decay = 0.4616.
  - Cell itself (d=0): ±1.615.
  - Ring at d=1 (8 cells): ±0.746.
  - Ring at d=2 (16 cells): ±0.344.
  - Sign: +1 for P1, −1 for P2. Values clamped to [−100, +100].
- On Moore, Chebyshev distance is the propagation metric — so propagation radius is symmetric to the adjacency radius (both use max(|Δx|,|Δy|)).

### Win condition
- **Threshold:** sum of board_values over cells owned by a player must exceed **63.46**. P1 aggregates positive values; P2 aggregates the negative of negative values (symmetric test).
- `max_turns = 100`. If neither player crosses threshold by turn 100, majority piece count decides.
- Training stats (avg game length ~19–26 steps across 4 seeds) indicate threshold usually fires well before max_turns, so the majority-on-max-turns path is rarely taken by trained agents.

### Non-degeneracy / flags
- Threshold ~63.46 with single-piece-max 1.615 means you need heavy cluster reinforcement. A fully surrounded interior stone can reach value ~13 (1.615 own + 8×0.746 + 16×0.344 = 13.1). In practice games end around piece 11–12 per side (22–24 total moves), well before cells run out. Threshold is reachable and decisive — **no double-pass exploit fired in any of my games.**
- Capture rule is **effectively inert** on Moore grid. Not quite "dead" but noted as a latent-only rule in practice.
- No pass-spam equilibrium emerges because influence-accumulation strongly rewards placing.

---

## PHASE 2 — STRATEGIC PLAY

All moves engine-verified via `play_helper.py --action play --moves "..."` and board values read via a direct `GameEngineV2` handle to `board_values`. Same sequential reasoner plays both seats; seat-swap in Game 3 is a role-label swap rather than agent swap (bias acknowledged).

### Game 1 — P1 corner-build vs P2 diagonal mirror

Moves (P1 odd, P2 even):
`27(P1) 36(P2) 18 45 9 54 10 53 17 46 26 37 11 52 19 43(P2) 25 35(P2) 34 44(P2) 16 28(P2) 33(P1)`

In coordinates: P1 built the upper-left quadrant (3,3),(2,2),(1,1),(2,1),(1,2),(2,3),(3,1),(3,2),(1,3),(2,4),(0,2),(1,4); P2 mirrored into lower-right (4,4),(5,5),(6,6),(5,6),(6,5),(5,4),(4,6),(3,5),(3,4),(4,5),(4,3).

Key tactical moments:
- Move 15 (P1 plays (3,2)): compound boost +9.2 effective because it sat at distance 1 from 5 existing P1 stones.
- Move 20 (P2 plays (4,5)): **+12.4 P2 effective swing** — a dense cluster-fill at the center of the P2 footprint, with 7 P2 stones within radius 2. This is the largest single-move gain observed and the core tactical lesson: placing inside your own mature cluster is much stronger than extending outward.
- Move 22 (P2 plays (4,3) as forced defense): disrupted P1 frontier by −2.86 but could only reach P1 through cells adjacent to P2's existing stones.
- Move 23 (P1 plays (1,4)): threshold crossed. **P1 wins 68.09 vs 57.87 at step 23.**

### Game 2 — P1 builds upper-left, P2 breaks mirror (plays 37 then 46)

Moves: `27 37 18 46 9 53 10 54 17 44 26 45 25 36 19 38 11 52 16 35 34(P1)`

P2 deliberately placed at (5,4) instead of the mirror (4,4) for move 2, aiming to create an asymmetric race. The asymmetry evaporated because the influence field is translation-invariant and both players still built tight clusters in opposite corners.

Key moments:
- Move 12 (P2 plays (5,5)): **+9.1 effective swing** — fills the geometric center of P2's 5-stone cluster, touched by 5 existing P2 stones at d=1.
- Move 17 (P1 plays (3,1)): +9.5 effective — similar "fill the geometric center" play.
- Move 19 (P1 plays (0,2)): +8.2. Pure cluster reinforcement.
- Move 21 (P1 plays (2,4)): threshold crossed. **P1 wins 64.24 vs 54.59 at step 21.**

### Game 3 — seat swap attempt (same reasoner, labels swapped); P2 invades early

Moves: `27 36 18 35(P2) 9 28(P2) 26 34(P2) 19 44 10 43(P2) 11 42(P2) 17 51(P2) 25 52(P2) 16 50(P2) 8 45 1(P1)`

P2 went aggressive — played (3,4), (4,3), (2,4) in moves 4, 6, 8 (adjacent invasions) instead of building a distant cluster. This briefly put P2 ahead (6.05 vs 5.25 at move 6) but P2 paid for it in long-range cluster density. P1's upper-left mass was never capturable and still grew to threshold first.

Key moments:
- Move 6 (P2 plays (4,3) invasion): +4.95 effective. First time P2 led on effective total.
- Moves 10–20: both sides competed move-for-move, staying within 2 points of each other. At multiple steps (move 12, 14) the position was **exactly tied** (same effective score to 3 decimals — the influence field is computed deterministically and the symmetric moves produce symmetric totals).
- Move 23 (P1 plays (1,0)): +8.85 effective. Threshold crossed. **P1 wins 67.69 vs 57.35 at step 23.**

### Endgame mode across all 3 games
All 3 games resolved via threshold victory for P1. **Zero games hit max_turns. Zero double-pass resolutions.** The double-pass exploit did not fire. This is a clean game from the "ends properly" perspective.

### Player reflections

**Player 1 strategy guide:**
1. Opening: place (3,3) center — gives full 5×5 footprint on-board.
2. Build a tight cluster away from P2's half of the board. Every placement should be within distance-2 of ≥3 existing own stones to maximize own-plus-boost gain (expect +7 to +9 effective per move in prime cluster positions; +5 to +6 at the edges).
3. Avoid edge/corner placements until mid-game — edge cells lose half their radius-2 neighborhood off-board (raw own-value stays at 1.62 but boost-accumulation halves).
4. Identify the "geometric center" of your cluster — a cell adjacent (d=1) to 4–5 existing own stones is worth ~+9 per placement, vs +5–6 for perimeter moves. Grab these greedily.
5. Invasion (placing inside P2's footprint) is only worthwhile when P2 damage + own gain > pure own gain. On Moore, invasion rarely pays because you lose your own propagation footprint radius.
6. Late-game: calculate exact expected effective-score-after-move for each candidate; play the move that crosses threshold first.

**Player 2 strategy guide:**
1. Do NOT mirror. Mirror strategy loses to P1's tempo advantage — P1 moves first, hits threshold first.
2. If possible, play first move *very close* to P1 to damp P1's center stone. (4,4) is the sharpest reply to (3,3) — puts −1.62 directly on the high-value cell adjacent to P1.
3. Consider early disruption (invading at (3,4) or (4,3)) to prevent P1 from compounding uncontested. Game 3 showed this is competitive but still loses narrowly.
4. In the midgame, prioritize cluster-interior fills (the "fill the center of your own 5-stone diamond" move) over extension — these are worth +8 to +9.
5. Accept that you will lose the race if both players play optimally and symmetrically. Your only chance is to force asymmetry by disrupting P1's cluster early.

**Opponent surprises:**
- The magnitude of the "cluster-interior fill" moves (up to +12.4 swing in one placement) surprised me. The influence additivity means a cell touched by 5 d=1 same-color stones is worth ~5× what an isolated placement is worth.
- Capture never fired despite the rule being present — Moore adjacency makes surrounding a stone on all 8 sides essentially impossible without prior coordination.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Distinct viable strategies?
There is exactly **one dominant macro-strategy**: build the densest possible own-cluster in your half of the board. The choice is only *where* you build it. Viable placement patterns:
- Diagonal mirror (P1 upper-left, P2 lower-right): both games 1 and 2 essentially followed this.
- Aggressive invasion (P2 plants stones inside P1's frontier): tried in game 3; slightly changes tempo but still loses to P1.
- First-move asymmetry (P2 plays next to P1 instead of mirror): cosmetic — the influence field is translation-invariant so both ways yield symmetric positions.

Verdict: one strategy dominates. Tactical micro-decisions (which specific cell each turn) have real depth, but the macro-plan is forced.

### Counter-play
Counter-play exists at the **move level**: at each turn, you must choose the highest-gain placement, factoring in own-cluster-density boost, edge penalties, and (rare) opportunities to damage opponent's cluster. A bad local choice costs 2–3 effective points. But there is little counter-play at the **plan level** — you can't fundamentally shift your strategy mid-game.

### Short-term vs long-term tension
Minimal. Because capture is inert and threshold is the only terminal condition, placements compound permanently — there is no sacrifice-now-for-later trade-off. Every move's effective-swing is monotonically positive; games are a straightforward race.

### Emergent concepts
- **Cluster-density value function:** the marginal value of placing at cell C equals `1.615 + sum over own stones s within distance 2 of C of (1.615 * 0.4616^d(C,s))`. This is a clean convex reinforcement structure.
- **Influence wall:** at the cluster boundary, the two players' influence fields sum to ~zero, creating a natural seam. Crossing the seam (invasion) costs you own-footprint and is rarely +EV.
- **Tempo:** P1 strictly wins all plausible races. This is the most important emergent property and is a major balance flaw.
- **No territory / no ko / no liberty fight:** despite the Go-style language in the rule names, none of those concepts are live. There is no "life", no "eyes", no "sente/gote". It is purely an accumulation game.

### Does topology matter?
Yes but in a shallow way. Moore's 8-neighbor adjacency + Chebyshev propagation metric means both placement legality and propagation are spatially isotropic. Spatial relationships reduce to "how many of my stones are within distance 2 of this empty cell?" — a simple count. A hex or grid variant of the same rules would play almost identically, only the specific neighborhoods would change.

### First-mover advantage (quantified)
**P1 won 3/3 games.** In games 1 and 2, P1 played the traditional strategy and won by 10+ effective points. In game 3, P2 played aggressively and *still* lost by 10+ points. The threshold is symmetric and both players accumulate symmetrically, but P1 moves first, so P1 reaches threshold first by one half-move. Even with perfect P2 play, P1's +1 move advantage at the inflection point appears decisive.

This is a **severe first-mover advantage** that the Genesis training data already flagged (one of 4 training seeds showed 1.0 winrate for P1). My human play confirms: without a komi-like compensation or a rule change, P2 cannot win with balanced play.

### Seat-identity bias caveat
Games 1 and 2 had P1 and P2 both played by the same sequential reasoner (me). Game 3 is a "seat swap" only by labeling — the same reasoner is still deciding both moves. This introduces bias: both seats use the same value function and the same cluster-density heuristic, so any "P1 advantage" I measure is partly "homogeneous play advantage." Inter-team comparison will disambiguate whether P1 really dominates or whether I just stumbled into a symmetric-preferring style.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary argument (forceful): this game is NOT novel.

**(a) Catalog comparison.**
This is Go with the capture rule disabled, played on Moore topology with an influence field replacing counted territory. Each sub-mechanic has a canonical analog:
- **Go (placement, surround)**: same placement rule ("place on empty, adjacent to own or first-move-free"), same capture rule (surround = remove zero-liberty groups), same "no-pass-or-else-pass" turn semantics. The only difference is the scoring metric and the Chebyshev adjacency.
- **Reversi/Othello**: influence-field-with-signed-propagation is a smooth analog of Othello's custodian flipping. Both reward dense contiguous placement in your half of the board.
- **Havannah / Tumbleweed / Morris**: all are variants of "place a stone for a scoring metric" on differently shaped boards.
- **Influence Go (a.k.a. "sphere-of-influence" scoring used in Go teaching tools)**: this is almost exactly that, made into a standalone game. Influence radius 2 with Chebyshev distance matches common teaching-software visualizations.

**(b) CA comparison.** N/A — this game has `ca_rule: null`; propagation is a static field not a CA. The Life-like-CA literature does not apply.

**(c) Simultaneous-play comparison.** N/A — this game is alternating, not simultaneous. No analogy to Diplomacy or Colonel Blotto.

**(d) Re-skin hypothesis.** Claim: this is **"Go without capture, with Chebyshev-distance influence scoring."** The specific transformation: take standard 9×9 Go, swap the 4-neighbor connectivity for 8-neighbor Chebyshev, remove the capture rule's activation threshold (already present but never fires on Moore), and replace territory-counting with a continuous influence-weighted piece-sum. The rest of the rules — alternating turns, place-adjacent-to-own (a weaker constraint than Go's "place on empty" but close), pass action, majority-on-timeout — are unchanged.

**(e) Expert-advantage test.** Would an experienced Go player have an immediate edge? Yes, strongly. Go players intuit influence, cluster density, "thickness," and edge-weakness — the exact variables that matter here. My "place at the geometric center of your cluster for +9 gain" heuristic is essentially a teaching-rank Go player's "shape move" heuristic. A 5-dan Go player would need ~5 games to adapt to the Chebyshev metric and would then dominate.

### P1/P2 rebuttal

The adversary is substantially correct but overstates. Specific rebuttals:

1. **Go's strategic depth is absent.** In real Go, the capture rule drives life-and-death battles, eyes, sente/gote, ko fights, and territorial invasions. **None of these emerged in my 3 games.** A Go player would quickly realize that the capture rule never fires (Moore adjacency + 8-liberty requirement is too strong to satisfy), that there are no eyes because empty cells inside a cluster don't matter, and that invasions always lose local-value. The game reduces to an **accumulation race** — which is NOT Go.

2. **Scoring is fundamentally different.** Go scores territory (empty space you surround) plus captures. This game scores **weighted own-piece sum with propagation boost**. Two very different incentive structures: Go rewards encircling empty space; this game rewards dense clustering of your own pieces. The Go player's instinct to "make shape for eyes" and "extend to reduce opponent's moyo" is misdirected here — extensions cost propagation footprint. An influence-scoring analog in Go would be the *endgame count* of framework *moyo*, but no standard Go variant makes that the sole win condition.

3. **Tempo flaw.** A proper Go variant would have komi (typically 6.5–7.5 points) to offset first-mover advantage. This game has **no compensation** for the second player, and my playthroughs show P1 wins all races by a decisive margin. Go does not have this structural imbalance. So it's not even a well-formed Go variant — it's a broken Go variant.

4. **No live capture = no tactical complexity.** In Go, the *threat* of capture drives most tactical decisions. Here, capture is essentially impossible (Moore 8-adj means you'd need 8 stones to kill 1). There is no tactical layer — just a strategic-accumulation layer.

**Specific Phase 2 moments where a Go analogy fails:**
- Game 1 move 20: P2 places (4,5) inside his own cluster for +12.4 swing. In Go, placing inside your own group is a **bad move** — it reduces eye-shape potential. Here it's the strongest move type. A Go player's "shape sense" actively misleads.
- Game 3 move 6: P2's invasion at (4,3) worked briefly (seized the lead) but still lost the game. In Go, successful deep invasions are often game-winning; here the invader trades their propagation footprint for temporary field denial and ends up behind.

### Joint novelty score: 3/10

**Why not lower than 3:** The specific combination — Moore topology + Chebyshev influence radius 2 + continuous-field threshold win condition — is not a direct reskin of any single named game I can point to. The explicit threshold-on-own-weighted-sum victory is a genuinely non-standard win condition. The emergent "place at geometric center of own cluster" strategy has a specific form (greedy convex maximization of a quadratic-like reinforcement) that isn't prominent in the canonical abstract-strategy literature.

**Why not higher than 3:** The game's entire strategic surface is subsumed by "Go with influence-scoring instead of territory-scoring, capture disabled." A Go 5-dan would adapt in ~5 games. The mechanics are all off-the-shelf: surround capture (inert), influence propagation (standard exponential-decay kernel), threshold win (standard). Nothing emergent surprises a strong abstract-strategy player. And the **first-mover imbalance** is a structural flaw that would need a komi fix to make the game competitively playable at all.

---

## PHASE 5 — VERDICT

**Team ID:** team-15
**Game ID:** 931c58ae59b4
**Rules Summary:** 8×8 Moore-grid placement game. Each turn, place one stone adjacent to an existing own-stone (first move free). Placement adds a radius-2 exponentially-decaying signed influence field to surrounding cells. First player whose sum of board-values on owned cells exceeds 63.46 wins; else majority piece count at turn 100.
**Topology:** 8×8 grid, Moore (8-neighbor) adjacency, Chebyshev distance metric.
**Turn Structure:** Alternating, one placement per turn.

### SCORES (1–10)

- **Strategic Depth: 4** — There's a well-defined micro-optimization at each turn (pick the cell with highest propagation-compounded gain), and mid-game cluster density produces a non-trivial value function with ~3× range between best and worst placements. But the macro-strategy is forced: both players grow a dense cluster and race to threshold. No life-and-death, no tempo-for-territory trade-off, no sacrifice dynamics. Greedy move-valuation solves it.

- **Emergent Complexity: 4** — Some emergent features: the "fill the geometric center" move, the "influence seam" between clusters, diminishing returns as the cluster saturates. But the capture rule is inert, the pass action is never +EV, and the dynamics collapse to "maximize your own convex score function." No chaotic, combinatorial, or CA-like behavior emerges.

- **Balance: 2** — **P1 won all 3 games by 10+ effective points**, including one (Game 3) where P2 played an aggressive asymmetric strategy. Training data agrees (seed 101044 shows 1.0 winrate for P1). No komi-like compensation exists. This is a serious balance flaw. The inter-team-triangulation caveat applies (same reasoner for both seats), but the structural argument — P1 moves first in a race with symmetric accumulation — independently predicts P1 dominance.

- **Novelty (post-adversary): 3** — Reducible to "Go with Chebyshev-radius-2 influence scoring and capture disabled." The influence-threshold win condition is non-standard and not a direct reskin of any named game, but every rule component is off-the-shelf. Go expertise transfers strongly (cluster-shape intuition directly applies). Adversary's strongest argument: it's an influence-scoring variant of Go with a broken first-mover asymmetry. Rebuttal: the specific (Moore + radius 2 + this decay + this threshold) combination has no direct analog — but the strategic surface is shallow enough that the difference is cosmetic.

- **Replayability: 3** — Games end in 21–23 moves with P1 winning by threshold. The outcome is essentially determined by seat, and the openings are nearly forced (build in your half). Would not reward a second play if you've solved the value function once.

- **Overall "Would I play this again?": 3** — Clean mechanics, instructive as an influence-scoring study exercise, but not compelling as a game. No competitive tension because of the first-move imbalance.

### CLOSEST KNOWN-GAME ANALOG
**Influence-scored Go without capture, on an 8-connected board.** The closest named cousin is Go itself (surround-rule lineage, adjacent-placement constraint, pass option, board-ownership scoring), but the win-condition swap (continuous influence threshold instead of counted territory + captures) and the 8-neighbor metric make it a distinct specimen. Not identical because the capture rule is inert, no life-or-death dynamics emerge, and the scoring formula is smooth/continuous rather than integer-counted.

### KILLER FLAWS
1. **Structural first-player advantage.** P1 wins every race. No komi. The game is not competitively balanced.
2. **Capture rule is inert.** The surround rule is present but fires zero times in natural play on Moore topology (would require an 8-sided encirclement that doesn't occur in influence-race dynamics). Effectively dead rule.
3. **Monotonic accumulation.** No sacrifice, no tempo-trading, no ko, no life-and-death. Each move is a pure local greedy choice.
4. **Invasion is strictly −EV.** Placing inside opponent territory costs you your own propagation footprint and rarely damages opponent enough to compensate. This removes a whole layer of tactical interest that Go has.

### BEST QUALITY
The **cluster-density value function** is a clean, analyzable object. Watching the effective-score tick up by +6 to +9 as you correctly identify cluster-interior cells is satisfying and teaches a real lesson about propagation-field optimization. If this were framed as a puzzle ("given this board, what is the highest-EV move?"), it would be a nice teaching exercise for influence-based reasoning. The engine also produces exactly-symmetric totals when both players play mirror moves, a nice invariant.

### IMPROVEMENT IDEAS
**Add a komi (compensating bonus) of ~7 effective points to P2's final score.** In my 3 games, P1 won by margins of 10.2, 9.7, and 10.3 effective points. A komi of 7 would nearly equalize the race and might let P2 win with superior tactical play. A secondary improvement would be to lower the capture liberty-count (e.g., require only 4 liberties on Moore instead of 8) so captures actually occur, reintroducing a tactical layer. Best single change: **komi** to fix the glaring imbalance.

---

## Process notes
- Every move was engine-verified via `play_helper.py --action play --moves "..."`. No illegal moves attempted; the engine rejected none during play.
- Board values (the propagation field) were read via direct `GameEngineV2` instantiation as recommended by the prompt's engine-quirk notes (the `show` action doesn't display values).
- All 3 games ended via threshold victory at step 21–23, none by pass or max_turns.
- Seat-swap in Game 3 was nominal (same reasoner, role-labels swapped). Acknowledged bias is per the prompt's caveat; inter-team comparison will be the real signal for balance.
- Time spent on evaluation: ~75 minutes across the 3 games + analysis + writeup, within the ~25-min-per-game budget on aggregate.
