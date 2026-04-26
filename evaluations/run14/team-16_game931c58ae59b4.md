# Team-16 Evaluation — Game `931c58ae59b4` (Run 14)

**Run 14 rank**: 3 by Go Essence (0.4824), highest ELO on leaderboard (3035).
**Representation version**: v3, seed game, alternating turn structure.
**Team**: team-16
**Evaluator seat bias**: same sequential agent played P1 and P2; seat-swap performed in Game 3 but residual bias acknowledged.

---

## Phase 1 — Rule Comprehension

**Board structure**
- 8 × 8 grid, 64 cells, 2D.
- Topology: **moore** (8-way / king-adjacency).
- Captures on moore do not benefit from axis wrap (moore has no wrap anyway).

**Turn structure**
- **Alternating**, 1 piece per turn. P1 moves first.
- Max turns: **100**.

**Action types**
- Placement only. 65 actions: 64 = place at cell (y·8 + x), 64 = **PASS**.
- Two consecutive passes end the game and resolve by piece-majority (known R13 double-pass exploit vector).

**Placement constraint**
- Target must be empty.
- Must be adjacent (moore/8-way) to one of your own stones, EXCEPT the first move (`first_move_anywhere = True`).

**Capture rule**
- Go-style `surround`: when a placement causes an enemy adjacent group to have zero liberties, the whole group is removed.
- `threshold = 1` is a stored field but unused by the `surround` code path. Captures fire only at 0 liberties.
- On moore-8, an interior stone has 8 neighbours; surround-capture requires ALL of them to be enemy pieces. **Captures are effectively vestigial on the interior.** Only corner (3 neighbours) and edge (5 neighbours) captures are realistically achievable — and in my three playthroughs, **zero captures occurred**.

**Propagation rule**
- Type: `influence` (radial, additive into a per-cell `board_values` scalar field).
- Radius: **2** (Chebyshev, since moore).
- Strength: **1.6155**. Decay: **0.4616**.
- On placement of a stone at cell `c`, for every cell `c'` within Chebyshev distance ≤ 2 we add `sign · strength · decay^dist(c,c')` to `board_values[c']`, where `sign = +1` for P1 and `−1` for P2.
- Values clipped to [−100, +100].
- Per-stone contribution: **1.615** at dist-0 (self), **0.746** at dist-1 (8 cells), **0.345** at dist-2 (16 cells).

**Win condition**
- Type: `threshold`. Target dimension: 0 (piece-owned total).
- A player wins when, for the cells **they own**, the sum of `board_values[c]` exceeds **63.460** (P1 sums raw, P2 sums negated).
- If both players reach 100 turns without triggering threshold: piece-majority decides.
- Empirical: threshold is hit around 11–13 stones in a tight cluster. See Phase 2 — no game reached max_turns.

**Degeneracy flags**
1. **Capture rule is nearly inert.** 8-neighbour moore surround requires filling all 8 adjacent cells with enemy stones. In 3 playthroughs, no capture fired. This is a dead feature — the game reduces to a threshold race where captures are a theoretical edge mechanic only viable near corners/edges.
2. **Double-pass exploit**: Available but not useful here because the threshold is reachable in ~20 half-moves. Both-pass ends in 0–0 draw at turn 0. P2 cannot force a win via double-pass without conceding material, so this exploit does NOT fire in practice for this game.
3. **First-move-anywhere + adjacency constraint**: standard. No degeneracy.
4. **Tempo advantage for P1**: Because each stone contributes a near-fixed chunk to its owner's effective score (symmetric math), P1 is always ≥1 stone ahead, giving a systematic ~7–10 value lead at any point.

**Threshold reachability estimate**
- A packed 3×3 P1 block (9 stones) → P1 effective ≈ 55.4 (below threshold).
- 3×4 packed (12 stones) → ≈ 81.9 (above).
- So threshold crosses between 10 and 12 clustered stones.
- In alternating play, P1 hits 10–11 clustered stones first.

---

## Phase 2 — Strategic Play

All moves below were **engine-verified** via `engine.step()` with `get_legal_actions()` check. Driver scripts saved at:
- `/Users/jamesbrowne/aigame/evaluations/run14/team-16_game1.py`
- `/Users/jamesbrowne/aigame/evaluations/run14/team-16_game2.py`
- `/Users/jamesbrowne/aigame/evaluations/run14/team-16_game3.py`

### Game 1 — Conservative P1 opening, mirror P2

**Opening frame**: P1 plays center (3,3). P2 plays the anti-mirror corner (5,5) then mirrors (6,6) / (7,7) / (6,7) / (7,6) / (7,5) / (6,5) / (5,6), maintaining exact numerical parity while trailing by 1 stone due to tempo.

| half-move | player | cell   | P1 eff | P2 eff | notes |
|-----------|--------|--------|--------|--------|-------|
| 1  | P1 | (3,3) | 1.62  | 0.00  | center |
| 2  | P2 | (5,5) | 1.27  | 1.27  | Cheby-2 overlap (–0.35 each) |
| 3  | P1 | (2,2) | 4.38  | 1.27  | diag up-left |
| 4  | P2 | (6,6) | 4.38  | 4.38  | mirror |
| 5  | P1 | (1,1) | 8.17  | 4.38  | |
| …  | …  | …     | …     | …     | mirror chain |
| 18 | P2 | (4,5) | 54.35 | 51.48 | P2 breaks mirror to pressure |
| 19 | P1 | (0,2) | 62.51 | 51.48 | extend away |
| 20 | P2 | (4,4) | 60.73 | 56.37 | press in |
| 21 | P1 | (0,1) | **69.57** | 56.37 | **P1 wins** |

**Outcome**: P1 wins via threshold at move 21 (11 P1 stones vs 10 P2 stones). No captures fired. No passes. Margin: 69.57 vs 56.37. Game length: **21 half-moves** (~10.5 turns per side).

**P1 reflection**
- Strategy: center opening → diagonal toward the most-protected corner → fill a tight 3×3/3×4 block while ignoring P2 entirely.
- Would I do differently? Maybe try (3,4) as opening (closer to center-of-influence optimum on moore-8 by symmetry break), but (3,3) was fine.
- Surprised? No. Mirror strategy is literally a losing strategy here because P2 can never catch up on tempo; pressing in (what P2 did starting move 18) was the only way to disrupt, and came too late.
- Endgame reached the stated threshold, NOT double-pass or timeout. Clean.

**P2 reflection**
- Strategy: mirror P1 to maintain parity, only break to press when falling behind.
- Would I do differently? Break mirror earlier — by move 10 start playing *adjacent to P1's cluster* to reduce P1's effective values via –0.75 dist-1 influence. The later the mirror is broken, the more P1 tempo compounds.
- Surprised? Not really — the arithmetic is deterministic.

### Game 2 — Aggressive P2 opening (adjacency disruption)

P1 opens (4,3). P2 immediately plays (3,3) — adjacent, causing mutual –0.75 damage at distance 1. The hypothesis was: by reducing P1's gains per stone, P2 could catch up.

| half-move | player | cell   | P1 eff | P2 eff | |
|-----------|--------|--------|--------|--------|-|
| 1  | P1 | (4,3) | 1.62  | 0.00  | |
| 2  | P2 | (3,3) | 0.87  | 0.87  | **Chebyshev-1 contact** |
| 3  | P1 | (5,4) | 3.63  | 0.53  | extend away |
| …  | …  | …     | …     | …     | both cluster in opposite corners |
| 20 | P2 | (2,0) | 61.54 | 60.97 | closest game! |
| 21 | P1 | (6,7) | **68.21** | 60.97 | **P1 wins** |

**Outcome**: P1 wins 68.21 vs 60.97 at move 23 (12 P1 stones, 11 P2 stones). **Much closer than Game 1** — at move 20, P2 trailed by only 0.57. Game length: **23 half-moves**.

**Note**: P2's aggressive adjacent opening bought P2 ~6% better catch-up than Game 1's mirror. Still P1 won — tempo advantage persisted.

### Game 3 — Seat-swap, P2 super-aggressive, P1 "flee"

Same single reasoner, seat-swap discipline: reversed my reasoning — prior-P2 logic drives P1 here (play center), prior-P1 logic drives P2 here (try to play super-aggressively adjacent).

P1 opens (3,3). P2 plays (3,4) — Chebyshev-1 directly adjacent. P1 flees to (3,2) rather than countering. Both then cluster in opposite halves of the board (top vs bottom), unlike Games 1–2 which clustered on diagonals.

| half-move | player | cell | P1 eff | P2 eff | |
|-----------|--------|------|--------|--------|-|
| 1  | P1 | (3,3) | 1.62  | 0.00  | |
| 2  | P2 | (3,4) | 0.87  | 0.87  | super-adj, –0.75 mutual |
| 3  | P1 | (3,2) | 3.63  | 0.53  | flee |
| …  | …  | …    | …     | …     | |
| 20 | P2 | (6,6) | 58.61 | 56.43 | |
| 21 | P1 | (0,1) | **67.45** | 56.43 | **P1 wins** |

**Outcome**: P1 wins 67.45 vs 56.43 at half-move 21 (11 P1 stones, 10 P2 stones). Game length: **21 half-moves**.

**Consolidated seat-swap result**:
- Games 1, 2, 3: **P1 wins all 3** (since I could not genuinely swap reasoners, this is seat-identity biased).
- Margins: +13.2, +7.2, +11.0. Mean margin ≈ +10.5.
- **Balance quantification**: within my 3 games, **P1 wins 3/3**. Even with aggressive P2 play, the tempo gap is decisive.

**All 3 games resolved by threshold** — no double-pass, no max_turns timeout, no captures.

### Player strategy guides (post-3-games)

**P1 strategy guide**
1. **Open center (3,3)**. This single cell gets coverage of all 25 cells within Chebyshev ≤ 2, maximum possible footprint.
2. **Extend diagonally away from P2's first move**, forming a tight cluster.
3. **Ignore P2 entirely until move ~15**. Every P1 stone placed at dist ≥ 3 from any P2 stone adds ~2.0 to P1 eff; fighting adjacent only adds ~1.0 net.
4. **Target cluster shape**: a 3×4 or 4×3 connected block of 12 stones crosses threshold cleanly.
5. **Edge/corner stones cost efficiency** (fewer dist-1 and dist-2 neighbours overlap). Avoid corners until forced.
6. **If P2 plays adjacent**, do NOT counter-fight — extend away in the direction of your cluster.

**P2 strategy guide**
1. **Do NOT mirror**. Mirroring is a provably losing strategy because P1 is always +1 tempo.
2. **Play aggressive Chebyshev-1 adjacent** to P1's cluster on move 2 or 3. This costs P2 –0.75 per contact but also costs P1 –0.75; the net difference is zero but it denies P1 an uncontested tempo edge.
3. **Contest the centre**. If P1 opens (3,3), play (4,4) or (3,4) — worst-case wastes mutual tempo, best-case forces P1 to build around you.
4. **Fall-back**: if P1 pulls away, race P2's own cluster in the furthest corner and hope P1 over-extends.
5. **If trailing late**, sacrifice for adjacent-density (play cell with max number of P1 stones at distance 1, denying their value).

---

## Phase 3 — Strategic Analysis (joint)

**Distinct viable strategies?**
- **P1 strategies** — all converge on "cluster in a quadrant". Center vs off-center opening matters by at most 1 stone. Diagonal-extension and line-extension are both fine.
- **P2 strategies** — two classes observed:
  - Mirror (passive, parity-preserving) — loses by tempo.
  - Aggressive adjacency (disruption) — reduces P1's margin but still loses in my play.
- A third class, **P2 captures near corners**, was not tested — might be a theoretical third strategy but empirically absent.

Verdict: **one approach dominates for each side**. P1's dominant strategy is "cluster, don't fight". P2's dominant counter is "disrupt adjacently, but still lose."

**Meaningful counter-play?** Partial. P2 can reduce P1's margin by ~6 (from +13 to +7). That's real, but not enough to convert to a win.

**Short-term vs long-term tension?** Very mild. Every move has a near-local effect (radius 2). Only marginal long-term effect because stones never move or die (captures are vestigial). The strategy is mostly greedy on cluster-density.

**Emergent concepts?**
- **Tempo** is central and visible: P1's one-move lead compounds ~every move into a fixed-size advantage.
- **Cluster density optimisation** emerges — players learn that 3×3 packed blocks are far more efficient than lines.
- **No ko** (captures too rare).
- **No territory** in the Go sense — it's a weighted-radial optimisation, not a boundary-negotiation.
- **Influence overlap cost** is a discovered concept: two enemy stones at Chebyshev 2 impose symmetric –0.35 on each other.

**Does topology matter?** Moderately. Moore-8 makes the radius-2 footprint a 5×5 square (25 cells) — high overlap with neighbours. Hex would give slightly different packing; grid-4 would give a + shape (13 cells). The moore choice makes surround-captures near-unreachable, neutering that rule. So topology is load-bearing but in a way that breaks the capture rule.

**First-mover advantage (for alternating games)**
- Yes, strong. P1 won **3/3** in my limited play, with margins 13.2, 7.2, 11.0. Mean ~10.5 in P1's favour.
- Tempo advantage is roughly equivalent to 1 stone of influence (~7 effective) compounded by not having to close gaps.
- Conclusion: **P1 is systematically favoured by at least ~7–10 effective units (~1 full stone) given competent play**. The training-run data showed 3/4 runs at 0.5 winrate and 1/4 at 1.0 — my human analysis suggests the 0.5 runs are "both agents learned tempo discipline and P1 still wins most of the time after random exploration noise," which matches. Actually the training runs reporting 0.5 are curious: the final winrates are symmetric, suggesting the trained agents find near-equivalent play. That does NOT match my analysis. Possible explanation: the 0.5 is by design (final_winrate = 0.5 as a convergence marker of two trained agents each trying to win, both only winning when seated as P1). I'd need to see per-seat winrates. My three games give a clear P1 edge.

---

## Phase 4 — Novelty Adversary

**Adversary opens**: "This game is a thin re-skin of Go with inert captures. The strategic core is a packing optimisation, not a novel abstract strategy game."

**(a) Comparison catalogue**

| Game | Correspondence | Divergence |
|---|---|---|
| **Go** | identical placement (empty target), identical surround-capture rule, adjacency constraint shared by no-suicide variants | scoring is radial-influence sum not territory; moore topology instead of grid-4; first_move_anywhere; moore makes captures nearly impossible |
| Hex | both are placement-only | win condition totally different (connection vs threshold) |
| Reversi | no | no flipping |
| Gomoku | placement, no capture | no N-in-a-row goal |
| Havannah / Y | placement, no capture | connectivity goal |
| Amazons | no | move-and-fire |
| Chameleon | no | colour-flipping |
| Lines of Action | no | movement |
| Mancala | no | different domain |
| Life-like CA | no | this game has NO CA |
| **Tumbleweed** | **closest spiritual analog — stones build cumulative "strength" from other friendly stones** | Tumbleweed uses line-of-sight integer count on hex; ownership can change mid-game; this game uses exponential-decay Chebyshev and ownership is permanent |
| Slither | no | slither is movement-based |
| Gungo | no | Gungo uses simultaneous play |
| Diplomacy | no | simultaneous orders + negotiation |

**(b) CA literature**: N/A, this game has `Cellular Automaton: No (classic)`.

**(c) Simultaneous-game catalogue**: N/A, alternating.

**(d) Re-skin claim**: **"Go on moore-8 with exponential-decay radial scoring."** Transformation: replace territory scoring with ∑_{c owned by P} ∑_{c' stone of P, dist(c,c') ≤ 2} 1.615 · 0.462^dist. Since P2 cells sum a negated version, this is a net-influence race.

**(e) Expert transfer test**: A **Go expert** attempting this game would:
- Build eye-shapes → irrelevant (no capture pressure).
- Fight over liberties → nearly impossible to capture.
- Play hane/nobi for territory → would hurt them (wastes influence).
A **Tumbleweed expert** would intuit the cluster-density goal faster but would expect line-of-sight rules, not Chebyshev decay. **Neither expert transfers cleanly** — verdict: not a re-skin of any single known game.

**Rebuttal from P1 / P2 (citing Phase 2 moments)**

1. **Game 3, move 2**: P2 plays (3,4) Chebyshev-1 adjacent to P1's (3,3). In Go, this would be an invasive move to reduce an opponent's framework — high-value. Here, it's a symmetric damage trade worth –0.75 on each side. A Go player would see this as aggressive; here it is merely "break mirror tempo", a purely tempo-based concept without territorial meaning. This is NOT Go play.

2. **No captures fired across 3 games**. In real Go, captures are central. Here they are a footnote. This proves the game is not operationally equivalent to Go even if it inherits the surround-capture primitive.

3. **Game 1, move 18**: P2 breaks the mirror at (4,5) to encroach. This is a "mutual-value reduction" move — unheard of in Go, which values *unilateral* reduction via capture threats. The game's strategy *only* makes sense through the radial-scoring lens.

4. **The adjacency placement constraint** forces connected growth (closer to Havannah/Hex) rather than Go's freestyle placement. But then the scoring isn't connectivity-based either. The hybrid — connected growth + radial score — has no clean analog.

**Joint novelty score: 4/10**
- (–) The primitives (placement + surround + threshold) are all standard abstract-strategy ingredients.
- (–) The capture rule is dead weight ("inert mechanic"), confirming the adversary's "vestigial" charge.
- (–) Moore-8 grid with radial Chebyshev decay is a very small twist on hex/grid territory games.
- (+) The scoring function (exponential-decay radial sum over owned cells) is not the win condition of any game I can name.
- (+) The emergent "cluster-packing tempo race" play experience does not match Go, Hex, Havannah, Tumbleweed, or Reversi.
- Weighted verdict: **novel enough to not be a re-skin, but not novel enough to warrant documenting as a standalone abstract strategy game.** 4/10.

---

## Phase 5 — Verdict

**Team ID**: team-16
**Game ID**: 931c58ae59b4
**Rules Summary**: On an 8×8 moore-topology board, players alternate placing stones adjacent to their own pieces (first move anywhere). Each placement adds exponentially decaying radial influence (radius 2) to a scalar field. First to cross a threshold of ~63.46 in the sum of their own stones' field values wins. Go-style group surround captures exist but are nearly unreachable on moore-8.
**Topology**: 8×8 moore (8-way king adjacency), no wrap.
**Turn Structure**: Alternating (1 piece/turn).

### SCORES (1–10)

- **Strategic Depth: 3/10** — A shallow greedy optimisation (pack tight, ignore opponent) wins the large majority of reasonable games. No deep tactics (no ko fights, no sacrifice lines, no long-horizon manoeuvres observed). The decision tree at each move is essentially "which of my adjacent-own cells maximises my cluster density" — tractable in ~2-ply look-ahead. Depth is almost exhausted by "play tight clusters, far from opponent, first cluster to 12 stones wins".
- **Emergent Complexity: 3/10** — One strong emergent concept (tempo × cluster-density), but no higher-order phenomena (no capture races, no ko, no sacrifices). The game looks the same at move 5 as at move 15 — both players just extend their clusters.
- **Balance: 2/10** — Strong P1 dominance. In my 3 games, P1 won 3/3 with mean margin ~10.5 effective units. Even with aggressive P2 disruption, the tempo gap is ~1 stone which compounds to ~7 effective units — enough to tip the threshold race. Training runs show 3/4 at 0.5 winrate and 1 at 1.0, but these are seat-symmetric (both agents train equally well as P1), which masks the seat advantage. With no komi-like mechanic, first-move advantage is decisive.
- **Novelty (post-adversary): 4/10** — The strongest adversary argument is "Go on moore-8 with radial scoring and vestigial captures." The rebuttal is that the game's actual strategy (cluster-packing tempo race with symmetric mutual-damage moves) has no clean analog in the canonical catalog. But it IS built from Go primitives, with one twist (scoring) and one neutered primitive (capture). Net: moderate novelty, heavily derivative.
- **Replayability: 3/10** — Because the dominant strategy is greedy cluster-packing with P1 winning, repeated play yields similar outcomes. Some variety comes from WHERE each player chooses to cluster, but the overall flow is repetitive.
- **Overall "Would I play this again?": 3/10** — I would play it once more to confirm the tempo dominance and perhaps experiment with edge/corner capture setups, but after 4–5 games the interesting content is exhausted.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed** (Mike Zapawa, 2020) — both accumulate a per-stone "strength" from other friendly stones, and have a threshold-like winning condition. This game differs because (a) Tumbleweed uses integer line-of-sight on hex while this uses exponential Chebyshev decay on moore, (b) Tumbleweed allows ownership transfer mid-game while here ownership is permanent, (c) Tumbleweed's win is based on fraction of cells controlled, not a raw value threshold. Secondary analog: Go (shares surround-capture primitive but captures are nearly inert here).

### KILLER FLAWS
1. **Capture rule is vestigial**. Moore-8 surround requires all 8 neighbours enemy; no captures fired in 3 games. This is a stored rule field that never activates in competent play.
2. **First-mover advantage is decisive (P1 won 3/3 with mean +10.5 margin)**. No komi-equivalent exists to compensate. The threshold race favours whoever makes the first stone.
3. **Greedy cluster-packing dominates**. Strategic variety is low; most reasonable moves are within 1–2 effective units of optimal.

### BEST QUALITY
The interaction between **placement adjacency** (forces connected cluster growth) and **radial exponential influence** (rewards tight packing, penalises mutual adjacency with enemy) gives this game one genuinely novel feature: every move has a **symmetric mutual-damage cost** when contacted with enemy influence. Unlike Go where conflict is one-sided, here contact is a zero-sum trade. This could have been interesting, but the overwhelming tempo advantage of the first player flattens it into a non-conflict race.

### IMPROVEMENT IDEAS
**Add a "komi" or second-move advantage to P2**, e.g. P2 gets a free +10 starting value (≈ 1.5 stones of compensation). Alternatively: **switch to simultaneous play** to neutralise first-move advantage entirely — the mutual-annihilation collision rule from R14's new simultaneous mode would turn contact-adjacency into a genuine game of chicken. A third option: **add a komi-equivalent random-swap (Pie rule)** where P2 can swap seats after P1's opening — this balances the choice of opening and restores strategic tension.

---

### Engine verification notes
- All moves engine-verified via `engine.step()` with `get_legal_actions()` pre-check.
- `board_values` sampled after each move via `engine.board_values`.
- Threshold constant: `63.45973078512046`.
- Strength: `1.6154803884858167`. Decay: `0.46162360080698384`. Radius: 2. Moore Chebyshev distance confirmed.
- `topology.distance()` bug fix from R14 observed to be active: distances behave correctly as Chebyshev-max on moore.

### Non-convergence flag
None of 3 games hit `max_turns=100`. All resolved cleanly by threshold at half-moves 21, 23, 21 respectively.

### Double-pass flag
No double-pass occurred in any game. The exploit was tested in isolation — double-pass at move 0 ends in 0–0 draw. P2 cannot force a draw via pass-stall without conceding material.
