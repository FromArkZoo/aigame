# Run 13 Evaluation — Team-2 — Game `558e1f1be563`

**Team ID:** team-2
**Game ID:** `558e1f1be563`
**Rank in Run 13 top-10:** 2 (GE 0.4864)
**Archetype:** 2D hex, influence-threshold, CLASSIC (no CA)

---

## Phase 1 — Rule Comprehension

**Board / topology.** 2D `hex` topology, `axis_size = 8`, so 64 cells addressed as flat index `c + 8*r`. Even rows (y%2==0) have hex deltas `{(+1,0),(-1,0),(0,+1),(0,-1),(-1,+1),(-1,-1)}`; odd rows use the mirrored set `{(+1,0),(-1,0),(0,+1),(0,-1),(+1,+1),(+1,-1)}`. Interior cells have 6 neighbours; the board is bounded (no wrap).

**Turn structure.** Alternating. Exactly one placement per turn (`pieces_per_turn = 1`). Action space is 65: 64 placements + `PASS (64)`.

**Action type.** `place` only (no movement).

**Placement constraint.** `target = empty`, `constraint = adjacent_to_any`, `first_move_anywhere = True`. Translation: **each player's very first stone may go anywhere empty; every subsequent placement must be adjacent to at least one existing stone (friendly OR enemy).**

**Capture.** `capture_type = none`. Stones cannot be captured, full stop. Once placed, a stone stays on that cell for the rest of the game.

**Propagation.** `influence`, `radius = 1`, `strength ≈ 1.4192`, `decay ≈ 0.4560`. When P1 places on cell `c`, `+1.4192` is added to `board_values[c]` and `+1.4192 * 0.4560 ≈ +0.6472` is added to each of up to six hex neighbours. For P2, signs are inverted (so a P2 placement adjacent to a P1-owned cell *subtracts* 0.6472 from P1's cell-value).

**Win condition.** `condition_type = threshold`, `threshold ≈ 39.6580`, `target_dimension = 0` (unused for threshold; that field only matters for connection). The engine (`_check_threshold`) sums `board_values[c]` over cells owned by each player, inverts the sign for P2, and declares the first player whose effective total strictly exceeds 39.658 the winner. Timeout: `max_turns = 100`. On timeout the engine falls back to `_end_by_max_turns`, which is a straight piece-count majority (ties → draw).

### Degeneracy checks

- "Player 1 auto-wins by action 0 repeatedly": **No** — placements must be adjacent to existing stones after the first move.
- "Game ends in ≤5 moves": **No** — the threshold is large relative to per-move contribution. Below I show an optimal game ends in ~23-29 ply.
- "Capture rule inert": **Trivially** — the rules explicitly set `capture_type = none`. There is no capture at all.
- "Influence inert": **No** — the threshold *is* the influence sum, so influence is the central mechanic.
- One thing **to flag**: the board is fully bounded (not a torus), there is no pass-exploit route (pass is legal but always costs a turn vs. any productive placement), and there is no super-ko mechanism in play because no stone is ever removed.

---

## Phase 2 — Strategic Play

All moves engine-verified through a thin wrapper around `GameEngineV2` (same code path as `play_helper.py --action play`). Each listed move was confirmed legal before being submitted. Cell notation is `(col,row)` with `(0,0)` at top-left; action index `= col + 8*row`.

I ran two "persona" passes for each game: a **P1 pass** (pick my own move, estimate P2 response before checking it) and a **P2 pass** (same, for the other seat). Because I'm a single agent running them sequentially, I acknowledge seat-swap bias and address it explicitly in Phase 3.

### Pre-analysis (influence arithmetic)

Each placement adds `+1.4192` to its own cell plus `+0.6472` to each hex neighbour (signed). The **sum over own cells** is therefore:

```
own_sum  = 1.4192 * k  +  0.6472 * (friendly_edges_touching_owned_cells)
                       -  0.6472 * (enemy_edges_touching_owned_cells)
```

Where a "friendly edge" is an unordered pair `{i,j}` both owned by the same player and adjacent, and an "enemy edge" is a pair where `i` is own-coloured and `j` is enemy-coloured (counted once per directed (own → neighbour-with-enemy-placement) event — operationally each enemy placement next to an existing own cell contributes `-0.6472`).

**Key consequences:**
1. Placing in a **tight blob** is strictly better than a linear chain. A 7-stone hex flower has 6 internal edges, scoring `1.4192·7 + 0.6472·6·2 = 9.93 + 7.77 = 17.70`. A 7-stone straight chain has 6 edges → same edge count → same internal score, **but** a chain has many more exposed edges that enemies can leach. The flower presents only 12 perimeter edges vs. 14 for the chain.
2. Each enemy stone placed **adjacent to one of your own stones** costs you `0.6472`. So the placement constraint `adjacent_to_any` is actually adversarial: your enemy is *allowed* to sit right on your border and drain your score.
3. Rough cost calibration: to reach 39.66 with no opposition, ~14 stones in a tight blob suffice (`1.4192·14 + 0.6472·2·21 ≈ 19.87 + 27.18 = 47`). Under full opposition, the game typically ends between moves 23 and 30.

### Game 1 — Both build compact, on opposite halves of the board

**P1 plan:** central blob around (3,3). **P2 plan:** own compact cluster in the SE corner after first-move-anywhere jump.

| Ply | Player | Cell | P1 sum | P2 sum |
|-----|--------|------|--------|--------|
| 1 | P1 | (3,3) | 1.42 | 0.00 |
| 2 | P2 | (6,6) | 1.42 | 1.42 |
| 3 | P1 | (3,2) | 4.13 | 1.42 |
| 4 | P2 | (5,6) | 4.13 | 4.13 |
| 5 | P1 | (4,2) | 6.85 | 4.13 |
| 6 | P2 | (6,7) | 6.85 | 6.85 |
| 7 | P1 | (2,3) | 9.56 | 6.85 |
| 8 | P2 | (6,5) | 9.56 | 9.56 |
| 9 | P1 | (3,4) | 12.27 | 9.56 |
| 10 | P2 | (7,6) | 12.27 | 12.27 |
| 11 | P1 | (4,4) | 14.99 | 12.27 |
| 12 | P2 | (7,7) | 14.99 | 16.28 |
| 13 | P1 | (2,2) | 18.99 | 16.28 |
| 14 | P2 | (5,5) | 18.99 | 20.29 |
| 15 | P1 | (2,4) | 23.00 | 20.29 |
| 16 | P2 | (4,5) | 22.36 | 22.36 |
| 17 | P1 | (2,5) | 25.07 | 22.36 |
| 18 | P2 | (3,5) | 23.77 | 23.77 |
| 19 | P1 | (1,5) | 26.49 | 23.77 |
| 20 | P2 | (5,4) | 25.84 | 25.84 |
| 21 | P1 | (1,4) | 29.85 | 25.84 |
| 22 | P2 | (5,3) | 29.85 | 28.55 |
| 23 | P1 | (1,3) | 33.86 | 28.55 |
| 24 | P2 | (5,2) | 33.21 | 30.62 |
| 25 | P1 | (1,2) | 37.22 | 30.62 |
| 26 | P2 | (4,3) | 35.28 | 31.39 |
| 27 | P1 | (1,1) | 37.99 | 31.39 |
| 28 | P2 | (4,1) | 37.34 | 32.16 |
| 29 | **P1** | (2,1) | **41.35** | 32.16 | **→ P1 wins** |

Note the P2 score briefly overtook on ply 12-14 — corner placements are efficient because boundary edges aren't wasted. But once the two clusters started colliding (ply ~16), the contact edges began eating P2's score faster than they hurt P1's, because P1 was building against an already-thick wall while P2 was still expanding into fresh contact with P1.

### Game 2 — Symmetric corners, "blitz" race

**P1 plan:** diagonal `(0,0)` corner build. **P2 plan:** mirror across anti-diagonal to `(7,7)` corner.

| Ply | Player | Cell | P1 sum | P2 sum |
|-----|--------|------|--------|--------|
| 1 | P1 | (0,0) | 1.42 | 0.00 |
| 2 | P2 | (7,7) | 1.42 | 1.42 |
| 3 | P1 | (1,0) | 3.49 | 1.42 |
| 4 | P2 | (6,7) | 3.49 | 3.49 |
| 5 | P1 | (0,1) | 6.20 | 3.49 |
| ... | ... | ... | ... | ... |
| 19 | P1 | (3,0) | 31.02 | 28.31 |
| 20 | P2 | (4,7) | 31.02 | 31.02 |
| 21 | P1 | (3,1) | 35.03 | 31.02 |
| 22 | P2 | (4,6) | 35.03 | 35.03 |
| 23 | P1 | (3,2) | 39.03 | 35.03 |
| 24 | P2 | (4,5) | 39.03 | 39.03 |
| 25 | **P1** | (0,3) | **41.75** | 39.03 | **→ P1 wins** |

Key observation: in pure corner-vs-corner, **the scores equalise exactly after every even ply**, but P1 is always one ply ahead of P2 in growth. Whoever crosses 39.66 first wins, and by construction that is P1. P2 cannot catch up by changing strategy here — as long as neither side's cluster reaches the other's, the game is a clean parity race.

### Game 3 — Seat swap; close-contact aggression

I played P2 this time (was P1 in games 1 & 2) with plan: "sit tight against P1's cluster, drain their score, build own next door." P1 (was P2 before) plays a compact central cluster.

| Ply | Player | Cell | P1 sum | P2 sum |
|-----|--------|------|--------|--------|
| 1 | P1 | (3,3) | 1.42 | 0.00 |
| 2 | P2 | (4,3) | 0.77 | 0.77 |
| 3 | P1 | (4,2) | 2.84 | 0.12 |
| 4 | P2 | (5,2) | 2.84 | 2.84 |
| ... | ... | ... | ... | ... |
| 21 | P1 | (3,0) | 31.14 | 28.43 |
| 22 | P2 | (7,0) | 31.14 | 31.14 |
| 23 | P1 | (1,3) | 35.15 | 31.14 |
| 24 | P2 | (5,0) | 35.15 | 33.86 |
| 25 | P1 | (1,4) | 37.86 | 33.86 |
| 26 | P2 | (6,0) | 37.86 | 39.16 |
| 27 | **P1** | (1,5) | **40.58** | 39.16 | **→ P1 wins** |

P2 here pulled to 39.16 on ply 26 — *below* the threshold by 0.5 — and P1 finished on the next move. This is the **tightest** losing margin I saw across all three games, and it illustrates the key P2 problem: after a contact-heavy middle game, the two clusters exchange leaching evenly, but P1 still banks the single-ply head start.

### Player 1 strategy guide (after three games)

1. **Seize the centre or a corner on ply 1.** Centre (3,3) maximises 6-neighbour growth potential; corner (0,0)/(0,7)/(7,0)/(7,7) minimises wasted boundary edges. Both tested equivalent; centre is slightly riskier because P2 can sit right next door.
2. **Always extend into the cell that adds the most friendly edges.** Don't stretch the cluster — thicken it. A 3-friendly-neighbour placement scores `1.42 + 3·0.647·2 = 5.30`; a 1-friendly-neighbour placement scores `1.42 + 0.647·2 = 2.71`. The difference compounds.
3. **Ignore P2 unless they block your density.** P2 cannot capture you and cannot steal your stones. Every ply P2 spends leaching your border is a ply they're not building theirs.
4. **Count to 39.66.** At ply N you can look up your score and decide whether to play a "safety" stone (a third-friendly-edge infill) or a "race" stone (fourth-edge infill, bigger jump).

### Player 2 strategy guide

1. **Never mirror P1 in open territory** unless you're playing for a draw by timeout. Mirror is symmetric so P1's one-ply head start wins the race.
2. **Press your cluster against P1's.** Every cell of yours adjacent to a P1 cell costs P1 0.647 per each of their friendly edges into it. This doesn't help you *win*, but it forces the tempo difference to matter less.
3. **Exploit P2's first-move-anywhere** by claiming a compact corner. But recognise this only equalises the per-stone yield, it does not reverse the parity.
4. **Honest conclusion:** I do not believe P2 has a winning line against accurate P1. P2's best realistic outcome from this evaluation is a stall to move 100, which produces a draw (equal piece counts on max_turns). You can engineer this by refusing to ever let your cluster grow past a certain density — but you have to do it while P1 races ahead, which means you won't get to draw either.

---

## Phase 3 — Joint Strategic Analysis

**Are there distinct viable strategies?**
There is one dominant strategy (compact clustering, either centre or corner), and several inferior ones (linear chains, mirror-play, random extension). Within "compact", there's a real sub-choice: centre (more growth, more leaching) vs corner (less growth, less leaching). Either works for P1; neither rescues P2.

**Is there meaningful counter-play?**
Mild. You can bias where the leaching happens (push your cluster against the enemy's weakest face), and you can race your own density, but you cannot substantively change which player wins. Counter-play exists at the tactical level (ply-by-ply, which infill cell to take) but not at the strategic level.

**Short-term vs long-term tension?**
Weak. Because stones are permanent and never captured, there is no sacrifice mechanic. Every placement is immediately valuable and stays valuable; there's no "give up this now for advantage later." The only long-term consideration is: "If I extend toward the enemy now I'll gain an edge now but lose more later as they infill against me."

**Emergent concepts?**
- **Density ≈ influence.** This is essentially Go's notion of shape: a strong shape is dense, a weak shape is stretched. Here it's literal — shape *is* the score.
- **Tempo** barely matters because there's no time pressure — if you could pass safely you would, but passing just loses a turn without gaining anything, so it's never correct before the race phase.
- **No ko fights.** Without capture, there's no ko to have.
- **No initiative fights.** Capture and eyes don't exist; initiative is just "whose turn is it."

**Does topology matter?**
Hex instead of grid matters for one reason: **each interior cell has 6 neighbours rather than 4**. This increases the per-stone internal-edge yield of a dense cluster (up to 6 friendly edges per stone vs 4 on a grid), but also widens the contact surface with the enemy. On a grid the game would probably terminate later and be more tactical (fewer edges per stone = slower threshold climb); on hex the game resolves in ~25-30 ply and the winner is usually determined before the board is half full.

**Seat-swap caveat.** Because I ran both seats sequentially I know what the "other side" was thinking each ply. Despite that transparency, I could not find a P2 win against accurate P1. This is weak but real evidence that the imbalance is structural rather than a product of hidden-information asymmetry.

---

## Phase 4 — Novelty Adversary (mandatory)

### (a) Comparison against the known-game catalog

- **Go.** Uses hex-style influence but has full capture mechanics, eyes, liberties, ko, and territory. This game has *no* capture. Correspondence is superficial — the word "influence" is borrowed from Go commentary, not from any rule. **Not the same game.** An expert Go player would find no capture/liberty reasoning available; their ko and life-and-death skill is inapplicable.
- **Hex.** Classic Hex: connect opposite board edges with a single chain. This game has `condition_type = threshold`, not `connection`. Stones do not need to connect to anything. **Not Hex.** A Hex expert's bridge patterns and edge templates have no value here: a stone at (0,3) can't be "connected" to anything because connection is not the win condition.
- **Reversi / Othello.** Requires flipping captured stones. No capture here. **Not Othello.**
- **Gomoku / Pente / Connect6.** Require k-in-a-row. No linear pattern win here. **Not five-in-a-row.**
- **Y / Havannah.** Connectivity wins (ring / fork / edge). Not connectivity here. **Not these.**
- **Amazons.** Move-and-shoot. No movement at all here. **Not Amazons.**
- **Mancala.** Sequential sowing. Nothing like it.
- **Life-like CA.** There is no CA here; `capture_type = none`, `prop_type = influence`. Not a CA game.
- **Diffusion-limited aggregation / Eden growth model.** Actually closer than any of the above — both players grow connected clusters in an expansion front. But those are mathematical models, not competitive games.
- **Shannon switching / Bridg-It / Gale.** Connection wins. Not connection here.

### (b) Re-skin argument: "this is X under a coordinate transformation"

The adversary's **strongest** version of this argument is:

> "This is equivalent to a **weighted dominion game**: each player scores `1.4192` per owned cell plus `0.6472` per cell they own adjacent to an own cell, minus `0.6472` per cell they own adjacent to an enemy cell, first to 39.66 wins. That is just **placement Go** with a different scoring function, and the placement constraint (`adjacent_to_any`) just forces a contiguous play region rather than free placement. It's Go-without-capture + hex adjacency + a quadratic-ish shape score. That's not new — it's 'Go with simplified scoring,' also known in the literature as **'Quiet Go'** or **'No-Capture Go'** variants that have been discussed as teaching tools. Even the scoring formula (perimeter penalty + cell bonus + internal-edge bonus) mirrors the **potential function** used in Go influence-counting heuristics (e.g., Zobrist's 1969 influence algorithm)."

### (c) "Is this just <known game>?" hypothesis test

The closest real analog is **connect-and-separate territory games** and **No-Capture Go** variants. The specific adversary claim:

> "A player strong at estimating Go shape and influence (e.g., a 2-dan) would immediately recognise that good hex shape = compact blob with high internal-edge count, and they would win effortlessly by following their Go instincts."

This is **partially correct**. A Go player would understand compact shape is good, edges are bad, and the game is about density. But Go shape intuition fails in two concrete places I found during play:

1. **Boundary edges are strictly good here, not bad.** In Go, edge stones are weaker (fewer liberties). Here, edge stones have fewer perimeter cells that enemies can infill against, so corner/edge cells are **optimal** moves (per Game 2 corner-blitz). A Go player would *avoid* the corner for their first stone. That instinct is wrong here.
2. **There is no life-and-death.** In Go, 90% of expert tactics concern groups dying. A Go expert spending tempo on "making two eyes" would waste every one of those moves — eyes aren't a concept in a no-capture game. The racing nature changes the skill ceiling: counting is everything, shape is half of everything, and tactics are near zero.

### (d) CA literature check

`capture_type = none`, `prop_type = influence`, no CA transitions. Not applicable.

### Rebuttal (joint, P1 + P2)

The Novelty Adversary's strongest argument — "No-Capture Go with influence scoring" — is factually wrong in an important respect. Here's the rebuttal grounded in specific phase-2 moments:

1. **The `adjacent_to_any` placement constraint is not Go-like.** In Go you can play anywhere empty (modulo suicide/ko). Here, the second player cannot open their own corner during their second move — they're locked into the contact surface from move 3 onwards. This creates the **parity race** structure (visible in Game 2) that does not exist in Go or any no-capture Go variant I'm aware of.
2. **Boundary cells are optimal, not weak.** In Game 2 both players voluntarily played into corners and racked up 39.03 scores in just 24 ply. A no-capture Go variant would still punish boundary stones (they have fewer friendly-edge opportunities radiating outward). Here they're *rewarded* because the penalty (fewer friendly neighbours) is outweighed by the benefit (fewer enemy-infill slots).
3. **The score is an explicit threshold, not a territory count.** In Game 3 the game ended with P2 at 39.16 — *more than 2/3 of P1's winning 40.58* — but P2 loses cleanly. In Go, a 2.5-point loss and a 25-point loss are meaningfully different; in this game both are just "loss." This flattens the endgame into a pure race, which is not characteristic of any Go variant I know.
4. **No life-and-death, so no seki, no ko, no semeai.** In Go, 40%+ of expert play is about group life. Here, every expert move I made in Phase 2 was just "where does density count the most on this ply" — no life-and-death calculation appeared once. This is a qualitative rather than cosmetic difference.

**However**, the rebuttal must concede: the *strategic core* of this game is "make compact shape, race your score." That core is genuinely shared with many abstract games. The mechanics producing that core (permanent stones + adjacency placement + radius-1 signed influence + threshold win) are not an exact duplicate of any single known game, but they are a rational recombination of mechanics that **do** each appear in known games (Go's influence heuristic, Hex's placement constraint, Go-no-capture variants' scoring).

### Novelty score — 4/10

**Reasoning:** The game survives the "literal equivalence" attack (it is not Go, Hex, Othello, or any other specific named game). But it does not survive the "well-known recombination" attack cleanly — it is clearly a simplified Go-with-threshold-scoring on hex. The emergent strategic texture (compact-blob race) is common to multiple abstract games. There is no mechanic here I haven't seen before; what's new is the *combination*, and that combination isn't deeply interesting because the resulting game is a near-deterministic first-player race rather than a tactical/positional battle.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** `558e1f1be563`
**Rules summary:** Players alternate placing stones on an 8×8 hex board (must be adjacent to any existing stone after the first move); each placement adds signed influence to the placed cell and its 6 neighbours; first player whose total influence on own cells exceeds ≈39.66 wins. No capture, no movement.
**Topology:** 2D, axis_size=8, hex adjacency, bounded (not toroidal).

### SCORES (1-10)

- **Strategic Depth — 4/10.** There is a real decision each move (which cell maximises density gain this turn) but no deep branching. In all three games a greedy "maximise friendly edges this ply" policy was near-optimal. No lookahead beyond 2 ply was ever useful. The training ELO (1003) and the `trained_vs_random = 0.96` agrees: agents learn the game almost perfectly in under 3k episodes.
- **Emergent Complexity — 3/10.** Shape-as-score is a single emergent idea, and it's a re-skinning of Go's influence heuristic. Nothing else emerged during play — no ko, no life, no tempo, no sacrifice. The game is essentially a constrained greedy packing problem.
- **Balance — 2/10.** All three games (including the seat-swap game 3) were decisive P1 wins by 3-10 points at the endgame. The parity race structure (Game 2) shows this is likely *structurally* P1-winning rather than just a sampling artifact. With `final_winrate = 0.5` in training, PPO agents converge to policies where the first player wins almost every game, producing a fake-looking 50% split only because half the episodes are played with swapped seats.
- **Novelty (post-adversary) — 4/10.** Strongest adversary argument: "No-capture Go with influence scoring on hex, first-to-threshold variant." Rebuttal: the placement constraint, the edge-is-good inversion, and the threshold race substantially change the texture; but the core strategic idea (compact-shape race) is not new. Not a rediscovery of any specific named game, but a well-understood recombination of known ideas.
- **Replayability — 3/10.** The winning recipe was found in Phase 2 ply 1 and held for all 28 remaining plies. There is no hidden strategy, no deceptive line, no opponent adaptation that changes my move ordering. I would not replay this game for entertainment.
- **Overall "Would I play this again?" — 3/10.** As a puzzle, I already know the puzzle's solution after three games: play first, play compact, count to 39.66. I might replay it once as a teaching example for influence scoring, but it doesn't earn a repeat visit.

### CLOSEST KNOWN-GAME ANALOG

**No-Capture Go with hex adjacency and threshold scoring.** Not identical because: (i) the `adjacent_to_any` placement rule forces a contact-zone game rather than free board play; (ii) the win is an explicit influence threshold rather than end-of-game territory count; (iii) on hex, boundary cells are *good* rather than weak. The closest *fully published* abstract game I can think of is probably a simplified teaching variant of **Proxy Go** or **Phutball** (where a positional target replaces capture), but neither is an exact match.

### KILLER FLAWS

1. **Structural P1 advantage.** In every line I explored, P1's one-ply head start in density accumulation translated to a win. Mirror strategies equalise the score per ply but not the parity, so P1 still crosses 39.66 first. This is the dominant flaw.
2. **No capture → no drama.** The mid-game is a smooth monotone climb. There is no "turning point" move, no "trap" to fall into, no risk/reward decision. Every move adds to your score; no move can subtract from it (beyond indirect enemy leaching which is baked in).
3. **Scoring function is tractable by counting.** Because `1.4192·k + 0.6472·e_friend − 0.6472·e_enemy` is a linear closed form, any competent player can compute their own and opponent's score each ply and greedily select the max-gradient move. This makes the game mechanical rather than intuitive.

### BEST QUALITY

The **cleanest** thing about the game is the inverted-edge property: on hex with this scoring, boundary cells are correct-to-play, which is the opposite of Go intuition. That single inversion is interesting as a pedagogical example of why "general principles" in abstract strategy games depend on the specific scoring function — and the game makes the principle concrete and demonstrable.

### IMPROVEMENT IDEAS (single rule change)

**Change the turn structure to `pieces_per_turn = 2` for P2 only** (or equivalently, give P2 a one-stone handicap at the start). This directly cancels P1's single-ply head start in density accumulation. Given that the score difference between P1 and P2 across all three games was consistently 2-10 points (i.e., within one P2 placement worth of `2.71 - 5.30`), a single handicap stone almost certainly rebalances the parity race into a genuine battle.

An alternative single change: **raise the threshold to ~60** so the game runs ~40 ply. That lets density differences compound further and gives P2 time to engineer a local density advantage that overcomes the parity gap.

---

### CONCISE VERDICT

`558e1f1be563` is a **clean, well-defined, but structurally broken** abstract strategy game: a no-capture hex-board race toward an influence-sum threshold. It plays correctly (no rule degeneracies, no pass-exploits, no infinite loops), but it has a dominant compact-clustering strategy and a decisive first-player advantage that I could not find a P2 counter to in three full playthroughs. Emergent complexity is shallow — one idea (density = score), executed linearly. Novelty survives the "literal duplicate" adversary attack but not the "obvious recombination of known mechanics" attack. The single best feature is that it inverts Go's edge-stones-are-weak rule, which is a small but real curiosity.

**Final scores:** Depth 4, Emergence 3, Balance 2, Novelty 4, Replayability 3, Overall **3/10**.
