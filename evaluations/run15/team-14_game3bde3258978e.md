# Genesis Creativity Engine Run 15 — Team-14 Evaluation

**Team ID:** team-14
**Game ID:** `3bde3258978e`
**Generation:** 10 (parent `4af27911b0f5`)
**GE Score:** 0.2005 | **Non-Triviality:** 1.00 | **Strategic Depth:** 0.451 | **ELO:** 2596.5

---

## Phase 1 — Rule Comprehension

### Board & topology
- **2D grid, 8×8, Moore topology** (face + diagonal adjacency; 8 neighbours per interior cell, 3 in corners, 5 on edges).
- No wrap/torus — hard walls.
- Total cells: 64; action space: 65 (placement 0–63 at `y*8 + x`, action 64 = pass).

### Turn structure
- **ALTERNATING**, 1 piece placed per turn. Classical sequential.
- Max turns: 100. Two consecutive passes → **DRAW** (R15 rule change).

### Action types
- **Place only** (no movement). Placement target: empty cells, anywhere (first move anywhere).

### Capture rule
- **Surround capture, threshold 1** (Go-style). A group of connected same-owner stones (connectivity is Moore) with 0 liberties is removed.
- In practice this is nearly INERT on Moore-adjacent 8-neighbour liberties: a random-play probe found captures in only **3/30** random-vs-random games. Stones need to be surrounded on all 8 Moore neighbours to die, which almost never happens before the threshold win fires.

### Propagation rule
- **Influence, radius 1, strength 0.9323, decay 0.5097.**
- Each placement deposits `+strength` (for P1) or `−strength` (for P2) on the placed cell, and `+strength × decay = ±0.4753` on each of the 9 cells in the radius-1 Moore neighbourhood (self + 8 neighbours).
- Influence is ADDITIVE and persistent. Clamped to ±100.

### Win condition
- **Threshold**, value **22.6453**. A player wins when the sum of `board_values[c]` over cells THEY own (with sign flipped for P2) exceeds 22.645.
- Threshold check iterates `(1, 2)` — so on a hypothetical simultaneous tie P1 wins by iteration order, but this game is alternating, so the engine-bias note does not bite.
- Max turns 100 — if hit, engine uses piece-count majority (not draw).

### Sanity of rules (flags)
- **Capture rule is nearly inert** — Moore-8 liberties + the cluster-forming incentive (clusters score more) mean groups almost never reach 0 liberties. Not degenerate but effectively cosmetic.
- **Threshold reachable** — all three of our playthroughs resolved by threshold in 15–21 moves. No double-pass draws, no max-turn cut-offs.
- **No CA.** (The game report confirms "classic mechanics".)
- **No degenerate forced-win.** Opening move has no single dominator; all placements yield the same +0.932 to an empty board.

---

## Phase 2 — Strategic Play

All moves engine-verified with `play_helper.py --action play`. Influence values and effective totals confirmed with a harness that called `engine.board_values` directly.

### Game 1 — baseline cluster race (P1 vs P2)

| # | Player | Move | Action | P1 eff | P2 eff |
|---|---|---|---|---|---|
| 1 | P1 | (3,3) | 27 | 0.932 | 0.000 |
| 2 | P2 | (7,7) | 63 | 0.932 | 0.932 |
| 3 | P1 | (4,3) | 28 | 2.815 | 0.932 |
| 4 | P2 | (6,6) | 54 | 2.815 | 2.815 |
| 5 | P1 | (3,4) | 35 | 5.648 | 2.815 |
| 6 | P2 | (6,7) | 62 | 5.648 | 5.648 |
| 7 | P1 | (4,4) | 36 | 9.431 | 5.648 |
| 8 | P2 | (7,6) | 55 | 9.431 | 9.431 |
| 9 | P1 | (2,3) | 26 | 12.265 | 9.431 |
|10 | P2 | (5,6) | 53 | 12.265 | 12.265 |
|11 | P1 | (2,4) | 34 | 16.048 | 12.265 |
|12 | P2 | (5,7) | 61 | 16.048 | 16.048 |
|13 | P1 | (3,2) | 19 | 19.831 | 16.048 |
|14 | P2 | (6,5) | 46 | 19.831 | 19.831 |
|15 | **P1** | **(4,2)** | **20** | **23.615** | 19.831 | **WIN** |

Final position: P1 built a 2×3+1 cluster anchored in the NW quadrant; P2 mirrored in the SE. Both hit 19.831 after move 14 because each player's cluster is isomorphic. On move 15 the 8th P1 stone captured a cell with 3 existing P1 neighbours, and the latent ambient influence (+2.358) at that cell plus neighbour bonuses (+1.425) yielded +3.783 — enough to cross 22.645. P2 never got to play move 15 because the threshold is checked after each move.

**Reasoning per move (P1 side):** open central, build a 2×2, extend to 2×3, then 2×3+1; every move targeted the empty cell with the most existing P1 Moore-neighbours to exploit both (a) ambient influence already deposited on that cell and (b) +0.475 bonuses to every existing P1 stone.

**Reasoning per move (P2 side):** identical mirror strategy — deliberately chose far corner to avoid any cross-cluster adjacency penalty. This was optimal for P2's absolute score but lost because P1 gets the last cluster-closing move.

### Game 2 — P2 disruption strategy

Same opening, but at move 14 P2 deviated from mirror and placed **(4,2)** directly inside P1's cluster perimeter (3 P1 Moore-neighbours).

| # | Player | Move | Action | P1 eff | P2 eff |
|---|---|---|---|---|---|
| 1-13 | | same as G1 | | 19.831 | 16.048 |
| 14 | P2 | **(4,2) disrupt** | 20 | 18.406 | 15.555 |
| 15 | P1 | (5,3) | 29 | 20.764 | 15.080 |
| 16 | P2 | (3,5) disrupt | 43 | 19.338 | 14.586 |
| 17 | P1 | (4,5) | 44 | 21.221 | 13.636 |
| 18 | P2 | (5,4) disrupt | 37 | 19.320 | 12.667 |
| 19 | P1 | (5,5) | 45 | 20.728 | 11.242 |
| 20 | P2 | (4,6) cluster | 52 | 19.777 | 14.075 |
| 21 | **P1** | **(2,2)** | **18** | **23.561** | 14.075 | **WIN** |

**Key finding:** each P2 disruption cost P1 ~1.4 effective but also cost P2 ~0.5 (because the disrupting cell sits in positive-ambient P1 influence, which flips to a P2-owned cell at positive value — BAD for P2 since P2 wants own-cells *negative*). The exchange rate is asymmetric in P2's favor (strip 1.4, spend 0.5 = +0.9 relative swing per disrupt move), but P2 still can't out-race P1 because P1 simply plays on the "other side" of its cluster (move 15, 17, 19) — P1 had so much uncommitted perimeter that every P1 move still yielded +2 to +3.8 while each P2 disruption only swung +0.9. P1 won in 21 moves instead of 15, a delay but not a save. **Threshold satisfied, no draw.**

### Game 3 — seat-swap, central-clash opening

P1 opened off-centre at (2,2); P2 (now my primary agent) took central (4,4). Both grew symmetric 2×2→2×3 clusters but the (3,3)↔(4,4) Moore-adjacency ensured a persistent mutual-nerf of ~0.95 between clusters.

| # | Player | Move | Action | P1 eff | P2 eff |
|---|---|---|---|---|---|
| 1 | P1 | (2,2) | 18 | 0.932 | 0.000 |
| 2 | P2 | (4,4) | 36 | 0.932 | 0.932 |
| 3 | P1 | (2,3) | 26 | 2.815 | 0.932 |
| 4 | P2 | (5,4) | 37 | 2.815 | 2.815 |
| 5 | P1 | (3,2) | 19 | 5.648 | 5.648 |
| 6 | P2 | (4,5) | 44 | 5.648 | 5.648 |
| 7 | P1 | (3,3) | 27 | 8.956 | 8.956 | (mutual nerf from (3,3)↔(4,4)) |
| 8 | P2 | (5,5) | 45 | 8.956 | 8.956 |
| 9 | P1 | (4,2) | 20 | 11.789 | 11.789 |
|10 | P2 | (6,5) | 46 | 11.789 | 11.789 |
|11 | P1 | (3,1) | 11 | 15.573 | 14.622 | (P1 moves away from mutual-nerf zone) |
|12 | P2 | (6,6) | 54 | 15.573 | 14.622 |
|13 | P1 | (4,1) | 12 | 19.356 | 17.455 |
|14 | P2 | (7,6) | 55 | 19.356 | 17.455 |
|15 | **P1** | **(2,1)** | **10** | **23.140** | 17.455 | **WIN** |

P1 reaches threshold on move 15. Seat-swap bias control: even with P1 opening suboptimally (off-centre), P1 still wins because the first-mover tempo is decisive in a cluster race.

*(I also accidentally tried action 9 = (1,1) first — it had only 1 P1 neighbour, not a winning move. Action-ID convention `y*8+x` is easy to fat-finger.)*

### Per-player reflections

**Player 1 strategy guide:**
1. Open central or near-central to maximise Moore-neighbour count on future extensions.
2. Always grow the cluster CONTIGUOUSLY — each new stone should have ≥3 existing own-Moore-neighbours to capture both ambient influence and neighbour bonuses (≥+3.7 per move).
3. Ignore P2 unless P2 plays disruptively inside your cluster; if they do, play on the opposite side of your cluster and keep racing.
4. Threshold is reachable in 7–11 own moves (14–22 total); plan for the 8th own placement to be the closer.

**Player 2 strategy guide:**
1. If you're strictly racing, mirror in the opposite corner — you'll lose by one move but reach max achievable score.
2. If you think you're behind on tempo, switch to DISRUPTION: place inside P1's cluster on cells with ≥3 P1 Moore-neighbours. Each disruption strips ~1.4 from P1 at ~0.5 personal cost (relative swing ~+0.9).
3. Disruption delays but does not prevent loss on a static first-mover. To actually beat P1 you need P1 to misplay (e.g. place disconnected stones, leaving a weaker cluster).
4. Never try to capture — surround on Moore-8 is effectively impossible in the window before threshold fires.

### Game-resolution summary

| Game | Winner | Moves | Mechanism | Resolved by stated win cond? |
|---|---|---|---|---|
| G1 | P1 | 15 | Threshold | YES |
| G2 | P1 | 21 | Threshold | YES |
| G3 | P1 | 15 | Threshold | YES |

3/3 games resolved by the stated threshold condition. Zero double-pass draws. Zero max-turn timeouts. Average length 17 moves (training runs averaged 16–22.5). First-mover won all three.

---

## Phase 3 — Strategic Analysis (joint)

**Dominant vs viable strategies:** One meta-strategy dominates (cluster racing) but there are at least two viable tactical styles within it:
- **Pure cluster race**: grow your own Moore-connected block as densely as possible.
- **Disruption**: sacrifice your own score slightly to strip 1.5× as much from the opponent.

Disruption has a positive relative EV (~+0.9/move swing) but does not beat the pure racer because the racer simply grows on the opposite flank of their cluster — there is always fresh "perimeter" with 3 existing Moore-neighbours until the cluster reaches ~9 stones, which is exactly the size needed to close. So disruption delays but does not reverse.

**Counter-play:** yes, some. If P1 plays loosely (non-contiguous stones), P2 can overtake because P2's tight cluster beats P1's scattered stones. In our G3 P1 still played contiguously and still won. Counter-play exists against a weak opener but not against an optimal one.

**Short-term vs long-term tension:** weak. Every move's value is ~determined by local Moore-neighbour count; there is almost no positional sacrifice that pays off later. Cluster growth is locally greedy-optimal.

**Emergent concepts:**
- **Influence/territory** — clear, directly encoded. Not truly emergent; it IS the win condition.
- **Tempo** — strongly present. First-mover advantage dictates all three outcomes.
- **Mutual nerf / contact penalty** — genuinely interesting: a Moore-adjacent enemy stone costs BOTH players, so both sides have an incentive to *avoid* each other's clusters early, producing a "territorial" two-region equilibrium reminiscent of Go's simpler openings.
- **No ko fights, no mutual-annihilation** (latter only relevant for simultaneous games). No interesting group-life patterns because capture is inert.

**Topology:** Moore 8×8 matters in two ways: (a) it gives 8-neighbour clustering bonuses, so compact clusters strongly dominate sparse placement; (b) the corners (3 neighbours) are low-value and the centre is high-value by a factor of ~2. The hard walls (no torus) penalise edge/corner openings.

**First-mover advantage:** In our three games, P1 won 3/3. In 30 random-vs-random probe games, P1 won 13 / P2 won 16 / 1 draw — i.e., UNDER random play P2 has a slight edge (bad random players are more punished on P1 because random is more likely to be non-contiguous and waste the opening tempo). But under **competent** play P1's first-move advantage appears dominant. That gap between random-balanced and skill-unbalanced is exactly what R15's new seat-balance heuristic is supposed to catch — and here it seems to have been *fooled*: the game passed balance under random play but fails balance under skilled play.

---

## Phase 4 — Novelty Adversary

### Adversary argument

**(a) Known abstract strategy games.** This is a clear *Go variant*. The board is 8×8 (Go is 19×19 but 9×9 Go is standard), placement-only, with Go-like surround capture. The influence mechanic is unusual for Go but not unknown — it closely resembles **Tumbleweed** (Mike Zapawa, 2020), where each cell has a "stack height" counter equal to its line-of-sight to friendly stones, and you need to accumulate influence to win. Tumbleweed explicitly has a threshold / territorial win. The influence-propagation mechanic is also a direct cousin of the "area scoring" on soft-influence maps used in **computer Go evaluation functions** (see Bouzy's potential function, 1999) — the idea of radial influence with exponential decay is literally the Bouzy operator.

The cluster-adjacency bonus is also mechanically identical to **Connect6-style** scoring where connected stones are worth more than isolated ones, and more broadly to **Gomoku + influence** hybrids.

**(b) CA-based games.** N/A — this game has no cellular automaton (`propagation_rule.prop_type = "influence"`, not "cascade"; no CA rule table).

**(c) Simultaneous-game analogies.** N/A — this is ALTERNATING. No Diplomacy / Blotto / Gungo comparison applies.

**(d) Topology re-skin.** This game is essentially **Go with three modifications: (i) no komi, (ii) win by accumulating exponentially-decayed influence instead of territory count, (iii) Moore-8 liberties instead of von-Neumann-4**. All three are well-known Go variants in the literature. Modification (iii) (Moore liberties) is "Diagonal Go" or "King-move Go", documented. Modification (ii) (influence-based score) is "Bouzy area / influence Go" in CGI papers. So this is "Bouzy-influence Go on a small Moore board."

**(e) Expert transfer.** A Go player would recognise this IMMEDIATELY. Specifically: (a) the 8×8 small board, (b) place-only with surround capture, (c) "make big territory, don't leave stones alone" — these are Go mantras. They would also recognise that the capture rule being largely inert under Moore-8 liberties makes the game a TERRITORIAL RACE with no life-and-death — essentially the simplification known as "Area-Scoring Go without life-and-death", which is a very common introductory Go variant. A 3–5 kyu Go player would beat a newcomer here with no adaptation.

**Adversary verdict:** this is a modest re-parametrisation of Go/Tumbleweed. Score 3/10 on pure novelty.

### Rebuttal (P1 and P2, joint)

The adversary's Tumbleweed / Bouzy-Go comparison is the strongest. We concede it substantially. BUT, specific mechanical points the adversary missed:

1. **The "mutual-nerf on contact" isn't Go.** In Go, placing adjacent to an enemy stone is often *positive* for you (you reduce their liberties). In this game, every Moore-contact costs BOTH players ~0.475 on the contact cell and 0.475 on each stone that was near that cell. This creates a Go-unlike "avoid contact" early-game equilibrium — our G1 showed both sides playing in opposite corners. Tumbleweed doesn't have this mutual-penalty mechanic either.
2. **Ambient influence captures value.** At move 15 of G1, placing on a cell that already had +2.358 of latent P1 influence added that full amount to P1's total. Go has no "ambient influence" — territory is binary (who owns) or empty. Tumbleweed has stack heights but they're per-player, not additive cross-player. This additive-influence accounting created a real strategic motif in our games (the winning move in G1 targeted a cell already inside the cluster's influence halo).
3. **Threshold race, not last-mover.** Go is "last-mover after passes wins territory count"; this game fires INSTANTLY on threshold crossing. That means every move is potentially a winning move — it creates a race dynamic Go doesn't have. Our G1 literally ended mid-board.
4. **Capture inertness.** The adversary correctly notes capture is near-inert, but this removes an entire strategic layer from Go — there's no life-and-death, no ko, no seki. That's a simplification, not a novelty, granted. But combined with points 1–3, the strategic shape is demonstrably different: in Go you'd never build a tight 3×3 block and expect to win; here it's optimal.

**Agreed score:** Novelty **3/10**. The game is a clear incremental variant of Go / Tumbleweed / Bouzy-influence-Go — recognisable to any Go student within a few moves. The three mechanical differences we listed are genuine but modest.

---

## Phase 5 — Verdict

**Team ID:** team-14
**Game ID:** 3bde3258978e
**Rules Summary:** 8×8 Moore-topology alternating placement game. Each stone deposits radius-1 decaying influence (+0.932 self, +0.475 neighbours). First player to reach cumulative influence >22.645 on their own stones wins. Surround capture exists but is nearly inert.
**Topology:** 2D grid, 8×8, Moore adjacency (8-neighbour), hard walls (no wrap).
**Turn Structure:** ALTERNATING, 1 piece per turn.

### Scores (1–10)

- **Strategic Depth: 4** — Dominant cluster-race strategy; single meaningful counter (disruption) with positive local EV but no path to actually winning against a competent first-mover. No meaningful long-term vs short-term tension, no life-and-death, no tempo sacrifices. Legitimate but shallow.
- **Emergent Complexity: 3** — Influence arithmetic is additive and linear; there are no surprising board states. "Mutual nerf on contact" is a real emergent incentive but it just produces two-region equilibria. No truly emergent patterns like ko, seki, or mutual-annihilation.
- **Balance: 3** — First-mover won 3/3 of our skilled games. Random-vs-random baseline is balanced (P1: 13, P2: 16, draw: 1 over 30 games), which is apparently what got this game through the R15 seat-balance check — a clear false-positive. Under competent play the first-mover advantage is decisive because cluster growth is greedy-monotone.
- **Novelty (post-adversary): 3** — Recognisable to any Go student within a few moves. The influence mechanic is known (Tumbleweed, Bouzy-influence Go). Mutual-contact-nerf is a small original wrinkle but insufficient to call this a new game. Adversary's "Bouzy-influence Go on a small Moore board" framing survives rebuttal.
- **Replayability: 3** — Because the optimal strategy is well-defined (tight central cluster, claim tempo, close in 8 own moves) and P1 almost always wins, there is limited reason to replay between competent players. Between a beginner and expert, the asymmetric disruption mechanic has some teaching value.
- **Overall "Would I play this again?": 3** — I'd play it once or twice to confirm the first-mover heuristic, then never again.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed (Zapawa 2020) on an 8×8 Moore-grid, with Bouzy-style decaying influence and Go-surround capture.** Not identical because (a) Tumbleweed uses line-of-sight stacks not additive radial influence, (b) Tumbleweed has no Moore-topology board in its standard form, (c) the mutual-contact-nerf dynamic is absent in Tumbleweed, (d) capture rule differs. But the strategic feel — "claim territory by placing stones whose influence overlaps favourably" — is essentially identical.

### KILLER FLAWS
1. **Capture is nearly inert** (3/30 random games had any captures, and our skilled games had zero). A full mechanic rendered essentially decorative.
2. **First-mover wins under skilled play** (3/3 observed). Seat-balance metric was apparently satisfied by random-play symmetry but does not hold under tempo-aware play. This is exactly the failure mode the R15 seat-balance term was meant to catch.
3. **No life-and-death depth** — the core Go strategic layer (reading eye-space, ko, seki) is absent because captures don't happen.
4. **Greedy-monotone optimum** — the best move at every ply is "highest Moore-neighbour count", making the game essentially a one-heuristic game.

### BEST QUALITY
The **mutual-nerf on contact** mechanic. It's a small but genuine incentive structure that differentiates this from Go: both players are *punished* for placing near each other in the early game, which produces a territorial separation phase that feels different from Go's invasion-driven mid-game. This could be the germ of a more interesting game if amplified.

### IMPROVEMENT IDEAS
**Single rule change:** make the placement influence SIGN-ASYMMETRIC so that placing adjacent to enemy stones is MORE costly for the opponent than for self (e.g., `-strength × 2` to enemy stones, `+strength × 0.5` to self-cell). This would (a) make contact meaningful as attack (not mutual loss), (b) create a real "invade vs defend" tension analogous to Go's yose, (c) give P2 a real disruption lever that can beat first-mover. Alternatively, **reduce influence radius to 0** (self-only) so the game becomes pure placement counting with capture — that would force the surround-capture mechanic to become live, since clusters would need to be explicitly defended.
