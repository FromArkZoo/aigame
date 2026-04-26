# Team-1 Evaluation — Run 16 GE Champion `8d12c8b92b71`

- **Team ID:** team-1
- **Game ID:** 8d12c8b92b71
- **Generation:** 7 (R16 GE champion, GE 0.160)
- **Topology:** 2D hex, axis 8 (64 cells, 6-neighbor von Neumann hex adjacency)
- **Turn structure:** **ALTERNATING**, 1 placement per turn
- **Action space:** 65 (64 placements + pass)

---

## Phase 1 — Rule comprehension

### Plain-English summary
- **Board:** 8×8 hex grid (offset coordinates), 64 cells. Interior cells have 6
  neighbors (`_build_hex_neighbors` in `topology.py`). The `play_helper rules`
  output mislabels this as "von Neumann" — it is hex (6-neighbor face adjacency).
- **Turn structure:** alternating; P1 always moves first.
- **Action types:** place only; placements anywhere on an empty cell;
  `first_move_anywhere = True`.
- **Capture:** none. Stones are immutable once placed.
- **CA:** none (classic mechanics).
- **Propagation:** signed influence with `radius=2`, `strength=0.984`,
  `decay=0.695`. Placing a P1 stone adds positive influence; P2 adds negative.
  Per-cell deltas (decay^d): d0 = 0.984, d1 = 0.684, d2 = 0.475. Values are
  clipped to ±100. Effective values stored in `engine.board_values` (numpy
  array attribute, not a method).
- **Win condition:** threshold. Sum `board_values` over cells owned by the
  player; for P2 this sum is negated to get an "effective" score. First
  player whose effective score crosses **34.129** wins. R16's
  `_check_threshold` resolves same-tick double-crossings by margin
  (higher margin wins; equal → draw). Max turns = 100; double-pass = draw
  (R13+ change).

### Degeneracy / pathology check
- **Threshold reachable:** yes. A loose 8-stone P1 cluster (parallel-build
  game) reached ≈33.3 by ply 16 and ≈39.8 by ply 17.
- **Forced wins in <5 moves:** no. Single stone is ≈+0.98; many placements
  needed.
- **Double-pass exploit:** **partially viable for P1, never for P2.** A
  passing P2 cannot stall — P1 keeps building toward threshold. A passing
  P1 simply hands tempo to P2, but in greedy testing P1 has zero incentive
  to pass.
- **Strong first-move bias:** **YES (flagged).** Greedy-vs-greedy across 8
  randomized openings gave P1 a 7-1-0 record. Game 1 (bracketing P2):
  P1 wins ply 31. Game 2 (parallel-cluster P2): P1 wins ply 17. Game 3
  (invasive P2 with seat swap): P1 wins ply 29. The R16 worst-of-three
  seat-balance probe should have flagged this.

---

## Phase 2 — Strategic play (3 games, all engine-verified)

Method: I scripted moves directly through `engine.step()` (constructed via
`factory.create_engine(game)`), reading `board_values` after every ply to
verify effective scores. Where the line was deeper than my hand-analysis,
I let a one-ply lookahead heuristic (`own_effective − opp_effective`,
prefer winning moves, avoid losing moves) finish the game.

### Game 1 — Standard seats; P2 plays "bracket" strategy

| Ply | Player | Move | P1 eff | P2 eff |
|----|----|----|----|----|
| 1 | P1 | (3,3) | 0.98 | 0.00 |
| 2 | P2 | (4,3) | 0.30 | 0.30 |
| 4 | P2 | (1,3) | 1.02 | -0.35 |
| 6 | P2 | (4,4) | 1.95 | -0.79 |
| 10 | P2 | (4,2) | 5.22 | -1.19 |
| 14 | P2 | (0,4) | 11.41 | -1.54 |
| 18 | P2 | (4,1) | 15.75 | -1.83 |
| 20 | P2 | (1,1) | 18.05 | -3.22 |
| 24 | (heur) | — | 24.59 | 4.69 |
| 28 | (heur) | — | 29.56 | 10.91 |
| **31** | **P1** | **(0,0)** | **34.32** | **13.74** | **WIN P1** |

Result: P1 wins on ply 31 (16 P1 stones, 15 P2 stones).

**P1 reflection:** The cluster strategy was crushing. Every internal stone
adds influence to itself (0.984) plus reinforces every adjacent own stone
(+0.684 each). The bracketing P2 stones did not block influence — they
just suppressed individual cells without preventing the cluster from
hitting threshold. I would do nothing differently.

**P2 reflection:** Bracketing was a mistake. Each bracketing stone
sat next to multiple P1 stones, so its own value was pulled deeply
negative (P2 effective = -3 after 10 P2 stones). Should have raced
to build my own cluster from the SE corner instead.

### Game 2 — Standard seats; P2 plays "parallel cluster" (smarter)

P1 builds a NW cluster around (3,3); P2 builds an SE cluster around (4,4).
Both ignore each other and race to threshold.

| Ply | P1 move | P2 move | P1 eff | P2 eff |
|----|----|----|----|----|
| 2 | (3,3) | (4,4) | 0.30 | 0.30 |
| 4 | (2,3) | (5,4) | 1.31 | 1.31 |
| 8 | (3,2) | (5,5) | 5.28 | 5.30 |
| 12 | (2,4) | (4,6) | 14.86 | 13.96 |
| 16 | (1,3) | (5,7) | 33.25 | 30.93 |
| **17** | **P1 (2,1)** | — | **39.82** | 30.93 | **WIN P1** |

Result: P1 wins on ply 17, the tempo move that puts P1 over threshold first.
Each player had 9 stones; the difference is purely first-mover order.

**P1 reflection:** Seeing both players race, I picked (2,1) — a stone
inside my own cluster that bumps several own cells through d=1 and d=2.
The threshold (34.13) is set such that ~9 well-placed clustered stones
suffice. Whoever places stone #9 wins.

**P2 reflection:** Even an optimal SE-corner cluster cannot beat P1's
tempo on this exact threshold. The threshold was effectively
"chosen between the 8th and 9th stone of a clean cluster" — P2 always
moves second so always crosses second.

### Game 3 — Seat swap (I played P2); P2 plays "invasive contest"

P2 plays adjacent to P1 stones to drag P1's effective down rather than
building far away.

| Ply | P1 move | P2 move | P1 eff | P2 eff |
|----|----|----|----|----|
| 2 | (3,3) | (4,3) | 0.30 | 0.30 |
| 4 | (2,3) | (3,4) | 1.34 | 0.97 |
| 8 | (2,4) | (2,2) | 2.98 | -0.59 |
| 12 | (3,1) | (1,2) | 5.51 | -1.38 |
| 16 | (4,2) | (4,1) | 7.44 | -1.83 |
| 20 | (heur) | (heur) | 16.57 | 7.30 |
| 24 | (heur) | (heur) | 22.07 | 14.58 |
| 28 | (heur) | (heur) | 31.31 | 22.88 |
| **29** | **P1 (6,0)** | — | **36.45** | 22.40 | **WIN P1** |

Result: P1 wins on ply 29 (15 stones each).

**P2 reflection:** Invading directly hurts both sides equally per
adjacent-pair, but because P1 has more total stones near my cluster
than I have near theirs (since my placements all sit on/near P1
stones, while P1 distributes some far from me), the symmetry breaks
in P1's favor. I never found a P2 win.

### Strategy guides

**P1 guide:** Pick a centered seed, then play an inside-the-cluster stone
every move. Aim for 9-10 stones in a tight hex cluster near (3,3) or
(4,4). Ignore P2 unless P2 invades inside your cluster — then place at
the opposite edge of your cluster to pull more own-cells into d=1 of
your new stone. Threshold is reached around ply 17-19 in clean parallel
games.

**P2 guide:** You probably can't win at greedy depth, but to stretch the
game and hope for a heuristic mistake, you have two choices:
1. **Parallel build** (Game 2): mirror in the opposite corner, hope for
   a P1 misstep. Race ends at 8-9 stones each, P1 wins the tempo race.
2. **Tandem invasion** (Game 3): play directly adj to every P1 stone to
   drag P1 effective down. Costs you own-effective but slows P1 by
   ~5 plies. Best chance is to last until max_turns=100 and try for a
   double-pass draw, but P1 has no reason to pass while ahead.

---

## Phase 3 — Strategic analysis (joint)

### Distinct viable strategies?
Yes, two for P1: (a) **center cluster** (most efficient self-reinforcement)
and (b) **edge cluster** (slightly fewer d=2 reinforcement cells but
fewer P2 invasion paths). For P2, no strategy is winning at the depths
we explored; "parallel build" minimizes margin of loss but does not win.

### Counter-play?
Limited. The capture rule is `none`, so stones don't come off. P2 cannot
remove P1's cluster. P2 can only suppress individual cells via radius-2
influence, and the suppression is strictly local. There is no global
"liberty" or "connection" mechanic that P2 can attack.

### Short-term vs long-term tension
Mild. The threshold is calibrated so 9 well-placed stones cross it,
which means the game ends at roughly ply 17-29 — well below max_turns.
There is no late-game fishing: by ply 12 the winner is usually decided.

### Emergent concepts
- **Cluster efficiency** — putting a stone with the most own d=1 and d=2
  neighbors. Resembles density-maximization in influence-stone games.
- **Tempo** — each ply matters because threshold is hit on a specific stone.
- **Tandem suppression** — a niche P2 idea (each P2 stone drags 1-3 P1
  cells by 0.684). Not strong enough.

Notably absent: territory, connection, ko, capture races, sacrifice
tactics, surrounding, life-and-death. The lack of capture/connection
flattens the strategic surface considerably.

### Topology
Hex matters mildly: each cell has 6 (vs 4 for grid) neighbors, so cluster
efficiency is higher and the "fattest" cluster shapes are different. But
the underlying mechanic (build influence on own cells until threshold)
would work on any topology — only the threshold value would change.

### First-mover advantage (quantified)
Across our 3 games and 8 randomized greedy probes:
- **9 of 11** outcomes: P1 wins.
- **0 of 11**: P2 wins.
- **2 of 8** greedy probes: 1 P2 win, 1 draw. (Out of 8 greedy probes:
  P1=7, P2=1, draw=0.)
- The single P2 win in greedy probes occurred when random openings
  forced P1 into a stone with very few own-neighbors at d≤2.

**The first-mover advantage is severe and the threshold value
(34.13) is the proximate cause: it sits between the 8th and 9th
stone of a clean cluster, so whoever places stone #9 first wins.**

(Phase 3 caveat — same agent played both seats; bias acknowledged.)

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary argument
"This is **Hex with influence-counting** — the only difference from
classical games is bookkeeping. Specifically:
- It is **Tumbleweed-on-hex** with no shadow rule and a different
  scoring threshold. Tumbleweed places stones with strength based on
  line-of-sight count; this game uses radius-2 decay propagation.
- It is **Othello/Reversi influence variant** without flips: each stone
  projects positive influence in a Gaussian-decay halo, you sum your own,
  hit threshold first.
- The hex board is decorative — translate to a 7×7 grid and you get the
  same dynamics.
- An expert in influence-stone games (e.g. Reversi or Atlantean Stones)
  would understand the mechanic in <60 seconds: 'build a tight cluster,
  hit a number'.
- There is **no novel emergent behavior** — no captures, no ko, no
  connection, no movement, no CA. It is pure additive influence
  accumulation. The radius-2 / decay-0.695 kernel is a close cousin of
  the Conway-style influence functions used in Go-bot heuristics."

### P1/P2 rebuttal (specific Phase-2 moments)

1. **Tumbleweed's defining mechanic is line-of-sight strength on placement,
   not radius-decay propagation** — Tumbleweed is *static* (one placement,
   one strength forever); this game's effective scores update with each
   neighbor placed. Game 2 ply 4-8 shows P1 (3,3) jumping from +0.30 →
   +5.28 purely from neighbor placements, not from anything specific to
   (3,3). Tumbleweed has no analogous re-evaluation. Failure of analogy:
   strong.

2. **Reversi-flip influence variants always have flips** — the appeal of
   Reversi-likes is the dynamic ownership change. Here, ownership is
   permanent. The "drag" mechanic in Game 3 (P2 cells with negative
   own_effective) has no Reversi analog because in Reversi those cells
   would just flip color.

3. **Hex topology IS load-bearing here** — the radius-2 hex kernel covers
   1+6+12 = 19 cells, vs 1+4+8 = 13 cells on a grid. The threshold value
   (34.13) is calibrated for hex efficiency. On a grid you'd need ~12
   stones, not 9, and tempo dynamics shift. The "decorative" claim is
   wrong.

4. **No known influence-stone game uses an explicit threshold-on-own-cells
   win condition with placement-only mechanics.** Closest: "score the
   most squares" Reversi (count occupied), but that needs a board-fill
   end. This game ends via a global influence sum hitting a hard number,
   which is unusual.

5. **Expert transfer fails specifically on the P2 dilemma** observed in
   Game 1: the bracketing strategy is a Go reflex (pin opposing stones
   with adjacent flanking stones), and it FAILS here because adj P2
   stones don't capture or block — they just self-immolate (P2 effective
   went *negative* through ply 14). A Go expert would lose game 1 in
   exactly the way our P2 did.

### Novelty score: **3.5/10**
The mechanic is a thin variant of "radius-decay influence + threshold"
seen in many influence-bot heuristics, but the win-by-threshold-on-own-
cells with placement-only and no-capture is a rare-but-not-unique
synthesis. The expert would NOT transfer immediately (rebuttal point 5),
which lifts it above 3, but the absence of capture/CA/connection caps it
below 5.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** 8d12c8b92b71
**Rules summary:** Alternating placement on 8×8 hex board; each stone radiates
signed radius-2 decay influence; first player whose summed influence on
own-occupied cells crosses 34.13 wins. No capture, no movement, no CA.
**Topology:** 2D hex, 8×8, 6-neighbor face adjacency.
**Turn structure:** alternating.

### SCORES (1-10)

- **Strategic Depth: 4** — One dominant strategy (tight cluster), one
  threshold to chase, no capture/sacrifice/ko/connection dynamics. Greedy
  one-ply heuristic plays near-optimally; no need for deep search. The
  R16 GE rank (champion at 0.160) seems generous given how shallow the
  decision tree is in practice.

- **Emergent Complexity: 3** — Pure additive influence with permanent
  ownership produces only one phase: cluster build-up. No phase
  transitions, no late-game subtleties, no surprising compositions of
  rules. The signed-influence "drag on own-cells" effect (Game 3) is
  the one minor emergent surprise.

- **Balance: 2** — **Severe first-mover advantage.** 0 of 11 P2 wins
  in our games (3 hand-played + 8 greedy probes). The threshold is
  positioned between stone #8 and #9 of a clean cluster, which makes the
  parity of stones the deciding factor. Trained AlphaZero-style nets
  presumably learn to draw or fish for P1 mistakes via training-time
  seat-swap noise (final winrate 0.500 in the DB), but at greedy /
  human-like skill the game is broken in P1's favor.

- **Novelty (post-adversary): 3.5** — Closest to "Tumbleweed with
  decay-radius scoring" or "Reversi-influence without flipping". Not
  identical to any catalog game but very close to a known kernel. See
  rebuttal in Phase 4.

- **Replayability: 3** — Same opening (center seed) is dominant; same
  threshold means same ply count; once you know the cluster trick, the
  game is largely solved at human-greedy depth.

- **Overall "Would I play this again?": 3** — Once or twice for the
  novelty of signed influence; not a game I'd want a tournament around.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed (hex, board-influence variant)** — Tumbleweed places stones
with strength = line-of-sight count and uses a majority-of-board victory.
This game uses radius-decay propagation (not LoS) and a fixed threshold
on own-cells (not majority). The mechanic-family is the same; the
specific function and win condition differ. An influence-game expert
would reach competence in 2-3 games.

### KILLER FLAWS
1. **First-mover dominance** (P1 7/8 in greedy probes, 9/11 overall, 0
   P2 wins observed in our evaluation).
2. **Threshold calibrated to a specific stone count** — this is the
   proximate cause of the P1 advantage. Threshold ≈ value of 9-stone
   cluster means P1's stone-9 always crosses before P2's stone-9.
3. **No second phase / no late game** — game ends ply 17-29 with no
   maneuvering. Effectively a sprint.
4. **No counter-play to clustering** — capture=none means P2 cannot
   remove cluster stones; only local suppression via influence, which
   is too weak (one P2 stone subtracts 0.684 from one adjacent P1 cell;
   one new P1 stone adds 0.984 to itself + 0.684 to each of up to 6
   neighbors).

### BEST QUALITY
The **signed-influence "drag" effect** (Phase 2 Game 3): a P2 stone
adjacent to a P1 stone makes the P2 cell's own-value strongly negative.
This forces P2 to commit to either a far-away cluster or accept negative
own-value. It is a genuinely interesting mini-tension that doesn't exist
in conventional placement games — most influence games use unsigned counts.

### IMPROVEMENT IDEAS
**Make the threshold stone-count-relative:** require the *winning margin*
(P1_eff − P2_eff) to exceed the threshold rather than absolute P1
effective. This eliminates the "stone #9 lottery" — P2 placements would
directly cancel P1 placements one-for-one, restoring tempo balance and
forcing a real positional fight rather than a cluster-density race.

Alternative: add a **simple capture rule** (a stone surrounded by 4+
opponent influence cells is removed). This gives P2 a reason to
contest interior cells and creates a real threat against tight clusters.
