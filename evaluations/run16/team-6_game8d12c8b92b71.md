# Team-6 Evaluation — Run 16, Game `8d12c8b92b71`

Team ID: `team-6`
Game ID: `8d12c8b92b71`
Run: 16 (R16 GE champion)
Evaluator: single-agent running all three roles sequentially (P1, P2, Novelty Adversary)

---

## Phase 1 — Rule Comprehension

**Board structure.** 2D hex board, axis size 8 (i.e. 64 cells), `topology_type = "hex"`. Despite `play_helper.py rules` mislabelling adjacency as "von Neumann", `topology.py` confirms hex axial adjacency: each interior cell has **6 face-adjacent neighbors** (not 4). The hex distance metric is true axial distance, so `cells_within_radius(c, 2)` returns 1 (self) + 6 (d=1) + 12 (d=2) = **19 cells** for an interior placement.

**Turn structure.** **Alternating** (`turn_type: "alternating"`, `pieces_per_turn: 1`). Not simultaneous — no collision-resolution issues. Standard play_helper.py works.

**Action types.** `place` only. 65-action space: actions 0-63 place at `cell = y*8 + x`; action 64 = pass. Two consecutive passes end the game as draw.

**Placement constraints.** `target: empty`, `constraint: anywhere`, `first_move_anywhere: true`. Any empty cell is legal at any time. No komi/handicap.

**Capture.** **None** (`capture_type: "none"`). Stones never come off the board. No suicide rule, no liberty rule.

**Cellular automaton.** None — `factory.create_engine` produces a classic (non-CA) engine for this rule set. No CA rules to inspect.

**Propagation / influence.** This is the only dynamic mechanic. `prop_type: "influence"`, `radius: 2`, `strength: 0.984`, `decay: 0.695`. On each placement, the placed cell and every cell within hex-radius 2 of it gets `±strength * decay^dist` added to `engine.board_values`. P1 places add positive value, P2 places add negative value. Values clamp to [-100, 100]. The contribution per stone in the interior is therefore:

| distance | cells | per-cell contribution | row total |
|---:|---:|---:|---:|
| 0 (self) | 1 | 0.984 | 0.984 |
| 1 | 6 | 0.984 × 0.695 = 0.684 | 4.104 |
| 2 | 12 | 0.984 × 0.695² = 0.475 | 5.700 |
| **all** | **19** | — | **~10.79** |

**Win condition.** Threshold (`condition_type: "threshold"`, `threshold ≈ 34.129`). At end of every turn, the engine sums each player's `board_values` over their **own** owned cells; P2's sum is sign-flipped. The first player whose effective score exceeds 34.129 wins. R16's margin-based tie rule applies on simultaneous crossings: higher margin wins, equal margins → draw. If both players pass, draw. Max 100 turns; max-turns end-state resolves by piece majority.

**Degenerate-rule check.**
- Threshold reachable: a tight 8-stone hex cluster reached 36.10 in Game 1 — well within 100 turns and well within available stones. Not a "double-pass draw" game.
- Pass action exists but is dominated by any non-pass place that improves your score, so passes don't appear in real play.
- Capture rule is "none" but that's not a "dead rule" issue — the threshold + influence design is the engine.
- No symmetry-breaking flaws: the board is balanced, but P1 gets a 1-move tempo lead each pair of turns, which (as Phase 2 showed) is decisive.

No degenerate rules flagged.

---

## Phase 2 — Strategic Play

I ran three full games (plus a couple of strategy-probe variants for analysis). All moves were engine-verified by stepping `engine.step(action)` and reading `engine.board_values`. P1 and P2 reasoning was finalized for each move before switching roles in my head.

### Game 1 — Both players build parallel clusters

| # | Player | Move | Coord | P1 score | P2 score | Reasoning |
|---|---|---:|---|---:|---:|---|
| 1 | P1 | 27 | (3,3) | 0.98 | 0.00 | Center maximizes radius-2 area on-board. |
| 2 | P2 | 45 | (5,5) | 0.98 | 0.98 | Far enough (hex-d=3) to avoid being inside P1's radius. |
| 3 | P1 | 26 | (2,3) | 3.34 | 0.98 | Extend NW; hex-adj to (3,3); each new neighbor adds 0.684 to both stones. |
| 4 | P2 | 54 | (6,6) | 3.34 | 3.34 | Mirror extension SE. |
| 5 | P1 | 35 | (3,4) | 7.05 | 3.34 | Triangle with (3,3) and (2,3) — three-stone tight cluster jumps score. |
| 6 | P2 | 37 | (5,4) | 6.11 | 5.69 | Tighten cluster, but (5,4) is hex-d=2 from P1's (3,3) so P2 cell takes a 0.475 hit. |
| 7 | P1 | 19 | (3,2) | 10.77 | 5.69 | Continue NW cluster. |
| 8 | P2 | 53 | (5,6) | 10.77 | 10.36 | P2 keeps pace. |
| 9-14 | both | … | … | … | … | Symmetric extensions. |
| 15 | P1 | 11 | (3,1) | **36.10** | 25.43 | **Threshold crossed** — P1 wins on its 8th stone. |

**Predicted P2 response after move 14:** I expected P2 to play (7,7) or extend further. P2 played (7,7) but now had no chance — would have needed two more moves to reach threshold while P1 only needed one.

### Game 2 — P2 contests centrally

P2 plants directly in P1's radius (action 36 at (4,4), then 35 at (3,4)) to **deny synergy** rather than build parallel.

| # | Player | Move | Coord | P1 | P2 | Note |
|---|---|---:|---|---:|---:|---|
| 1 | P1 | 27 | (3,3) | 0.98 | 0.00 | Same opener. |
| 2 | P2 | 36 | (4,4) | **0.30** | 0.30 | Both stones adjacent → mutual cancellation drops effective score. |
| 3 | P1 | 19 | (3,2) | 2.18 | -0.17 | P1 retreats NW, escaping P2 influence; P2 actually goes negative. |
| 4 | P2 | 35 | (3,4) | 1.02 | 1.02 | P2 contests again. |
| 5+ | both | … | … | … | … | P1 continues NW; P2 forced to swing E to build. |
| 17 | P1 | 3 | (3,0) | **38.71** | 28.88 | P1 wins move 17. |

**Reflection.** Contesting cost P2 score early — its own stones spent turns on cells with reduced effective value because they were within P1's influence. P2 fell behind by ~10 points by move 17 even though it forced P1 to "retreat" into NW. **Pure contest is not refutation.** Net the contest didn't pay because while P1 lost ~1 move of efficiency, P2 lost the same.

### Game 3 — Seat swap (I optimize from P2 side)

I tried two P2 plans:
1. **Standard parallel cluster** (mirror of Game 1 but I'm now playing P2's perspective, P1 plays Game 1 line). Same result: P1 wins move 15 at 36.10.
2. **Sharp contest+cluster** (off-line): P2 plants at (4,4), (4,3), (5,4), (5,3), (5,2), (6,4), (6,3), (6,2). At move 16 P2 was momentarily AHEAD (33.25 vs 30.51 — see helper transcript), but P1's move 17 (action 26 at (2,3)) bridged its NW cluster and jumped to 39.82, crossing threshold.

**Final reflection (P2 side).** I could not find a P2 line that wins against optimal P1 from the canonical (3,3) opener. P2 either (a) cedes tempo and loses by ~5 points, or (b) contests sharply and gets briefly ahead but P1 finishes one move sooner due to the alternating-turn parity.

### After-game strategy guides

**P1 strategy.** (1) Open center at (3,3) or (4,4) — equivalent symmetric centers maximize on-board radius-2 cells. (2) Each subsequent move should be a hex-neighbor of an existing P1 stone — clustering compounds because each cell's value is the sum of contributions from all P1 stones within radius 2. (3) Avoid placing stones inside P2's radius-2 zone unless it's a winning move; the negative penalty offsets cluster gains. (4) End-game: count cluster-margin moves; once you can cross threshold in one move, do it (don't develop further).

**P2 strategy.** (1) Mirror P1 by hex-distance 3 to stay just out of contact — hex-d=3 means P2's first stone is unaffected by P1's radius-2 influence. (2) Build a tight cluster with the same density as P1; you cannot reach threshold first against optimal P1, so try to (3) place a contesting stone at distance 2 from P1's most central stone if and only if P1's threshold-crossing move would be undone (i.e. drained below threshold). In practice this happens rarely. P2 must accept that this game is **structurally biased toward P1**.

### Convergence

All 3 games ended at the **stated win condition** (threshold crossed). None resolved by double-pass or max-turns. Length: 15-17 moves (≈8 stones for P1, 7-8 for P2). Random vs random: 20-game self-play yielded 8 P1 wins, 3 P2 wins, 9 draws (max-turns piece-equal). Skilled play avoids draws; random play often hits draws.

---

## Phase 3 — Strategic Analysis (Joint, P1 + P2)

**Distinct viable strategies?** Two: (A) **parallel-cluster** (build away from opponent, race threshold) and (B) **contest-cluster** (place inside opponent radius to drain their score). Both lead to P1 wins given the canonical opener. There's no qualitatively winning P2 strategy I could find — but multiple viable *defensive* lines exist that lose by 2-10 points.

**Counter-play.** Yes but **asymmetric.** P2 contesting forces P1 to take less efficient cluster shapes, costing P1 ~1-2 moves of score growth. But that same cost falls on P2. The cost cancels and P1's first-move parity advantage remains.

**Short-term vs long-term tension.** Modest. Each move's local effect (the placed stone's value contributions) is also the dominant long-term effect because of clamping and decay. There's no "set up now, harvest later" dynamic — cluster growth is monotonically additive. The only long-term consideration is **shape**: putting a stone where 6 neighbors will eventually fill is worth ~0.984+6*0.684 = 5.08 in the limit, vs an edge stone reaching maybe 3.5.

**Emergent concepts.**
- **Territory & influence:** very explicit — `board_values` literally is influence.
- **Tempo:** decisive. P1's free first move corresponds to a ~5-point lead at threshold time given dense play.
- **Initiative:** weak — neither side has hard-to-predict threats; threats are scalar score deltas.
- **Ko / mutual annihilation:** none (no capture).
- **Cluster shape:** tight hex triangles maximize per-stone score. The "best shape" is roughly a hexagonal patch of ~7-10 stones, because each interior stone adds 6 neighbors at 0.684 each plus 12 second-ring at 0.475.

**Topology matters?** Yes. Hex (6-neighbor) is materially different from grid (4-neighbor): hex gives 30% more first-ring neighbors, dramatically increasing cluster synergy. On a grid the same threshold would take 2-3 more stones. The hex topology is *integral* to the game's tempo.

**First-mover advantage (quantified).** Across my 3 games + 2 probe variants:
- Canonical center opener, parallel cluster: P1 wins move 15 (36.10 vs 25.43).
- Center opener, P2 contests: P1 wins move 17 (38.71 vs 28.88).
- Seat-swap (I tried P2 hard): P1 still wins, P2 caps at ~29-33.
- P1 plays poorly (corner opener) + P2 greedy: **P2 wins** (36.64 vs 33.37) — confirms P2 can win against bad P1 play, so the game isn't a forced P1 win, but it's strongly P1-biased given competent play.

Quantitatively: P1 wins **3/3 of my contested games** when both play sensibly. The training-run data agrees: avg game length 18.5 / 26.5 across two seeds, and self-play winrate 0.5 — but self-play 0.5 is a balanced *learned* policy outcome, not balanced openings; with handcrafted strong openings, P1 dominates. **Seat-swap evidence** is unfavorable: switching colors did not switch the winner.

I acknowledge **seat-identity bias**: I (the same agent) played both sides; I may have unconsciously played P2 sub-optimally. But the structural argument (P1 has a free move; clusters are monotonically additive; threshold is hit at 8-stone density on either side) is independent of agent skill.

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary brief: this game is not novel

(a) **Catalog comparison.**
- **Go.** Hex board is unusual for Go but exists (HexGo, Y); influence is a well-studied Go concept (modeled by every modern Go bot). No-capture Go = territory game. The threshold here is just "how much influence on your own cells", which is a discretized analog of Go's influence-counting endgame. Adversary: this is **No-Capture Go on a hex board with an influence threshold** — a 2-step transformation away from Go.
- **Tumbleweed.** Tumbleweed is played on a hex board where each stone radiates "line-of-sight" to claim territory; player with most territory wins. Identical concept (radiating influence on hex), and the "stack ≥ enemy stack" rule is a contest mechanic the same as our negative-value contests. Adversary: **this is Tumbleweed with continuous decay instead of binary line-of-sight**.
- **Hex / Y / Havannah.** Connection-based, irrelevant — this game has no connection condition.
- **Reversi/Othello.** Capture by surround — not relevant, no capture.
- **Gomoku/Pente/Connect6.** N-in-a-row — not relevant.
- **Lines of Action / Amazons.** Movement-based — not relevant.
- **Slither.** Connection — not relevant.

(b) **CA literature.** N/A — no CA.

(c) **Simultaneous comparisons.** N/A — alternating game.

(d) **Re-skin argument.** This is **Tumbleweed with a continuous-decay influence model**:
- Tumbleweed stones project influence along 6 hex rays until blocked.
- This game projects influence in a 6-direction radius-2 hex disc with exponential decay 0.695^d.
- Both terminate by a numeric threshold ("territory count" vs "effective score").
- Both are alternating, no capture, hex.

(e) **Expert transfer test.** Would a strong Tumbleweed player immediately understand this? **Yes, quickly.** The transferable principles are:
- Center is best (more directions of projection / more cells in radius).
- Tight clusters beat spread placements (synergy).
- Contesting near opponent costs both sides equally.
- First-move tempo matters.

A Go-influence-experienced player would also transfer most concepts.

**Adversary verdict: novelty 2-3.**

### P1 + P2 rebuttal

The rebuttal hinges on **specific Phase-2 moments where the Tumbleweed/Go analogies fail**:

1. **Game 2, move 2 → move 3 swing**: P2 placing at (4,4) drove BOTH players' effective scores DOWN simultaneously (P1 0.98→0.30, P2 from 0 to 0.30). In Tumbleweed, placing adjacent to opponent doesn't *reduce* opponent's existing claimed territory — it only blocks new claims. The continuous overlap-cancellation here is genuinely different: **placement reshapes existing scores backwards**. This is closer to a signed-field PDE simulation than to combinatorial territory.

2. **Game 2, move 3** (P1 (3,2) → P2 effective = -0.17): a player can have **negative** effective score. In Go and Tumbleweed, your own territory is non-negative. The mechanic "you can be 'in the hole' on your own stones if surrounded by enemy influence" forces a different mid-game calculus — you must check whether your *existing* cells still pull their weight, not just plan future placements.

3. **Game 3 alternate, move 16** (P2 momentarily ahead 33.25 vs 30.51, then loses move 17 to P1's bridge move): a Go/Tumbleweed transfer player would not immediately see that "you can be ahead on raw count and still lose because the opponent's NEXT move is bigger than yours." This is a property of the **smooth gradient field**: a single placement can move both players' scores by 5+ points simultaneously, including across the threshold. Standard territory games have much lower per-move score volatility.

4. **The 0.984 / 0.695 numerics specifically.** The decay parameter 0.695 puts second-ring cells at 0.475 — significant but not dominant. This creates a **non-trivial radius-2 calculus**: placing two stones at hex-distance 4 still gives ZERO mutual contribution; at d=3 contributes 0; at d=2 contributes 0.475 each way. No standard board game has this specific 3-tier overlap mechanic.

**Score: 4/10.** I rate higher than 2-3 because of #2 (negative-score-on-own-cell is genuinely unusual) and the smooth-gradient structure (#3). But it's not a 7+ — the framework "alternating place on hex, projection-based threshold win" is solidly in the Tumbleweed/influence-Go family.

---

## Phase 5 — Verdict

**Team ID:** team-6
**Game ID:** 8d12c8b92b71
**Rules Summary:** Alternating placement on an 8×8 hex board with no capture; each placed stone radiates exponentially-decaying influence (radius 2, strength 0.984, decay 0.695) added to/subtracted from `board_values`; first player whose effective influence on their own cells exceeds 34.129 wins.
**Topology:** 2D hex, axis 8, 64 cells, 6 face-adjacent neighbors per interior cell.
**Turn Structure:** alternating (1 piece per turn).

### SCORES (1-10)

- **Strategic Depth: 5** — There's clear cluster-building skill, contest tactics, and end-game tempo counting. But the entire game collapses to "build the densest hex cluster you can while staying out of opponent's radius-2 zone". After 2-3 games, optimal play is mostly memorized: open center, hex-step-extend, race threshold. No deep tactical surprises emerged across my games. Greedy margin-maximizing play ≈ optimal play within ~1 point.

- **Emergent Complexity: 5** — Influence overlap creates non-trivial cell-value dynamics (negative own-cell values, mutual cancellation), and the smooth-gradient jumps occasionally produce surprising swing moves. But there are no emergent meta-concepts beyond cluster shape; no equivalent of Go's life-and-death, ko fights, sente/gote, or shape patterns. The CA-free, capture-free design caps the complexity at "weighted Voronoi race".

- **Balance: 3 — strong P1 bias.** Seat-swap evidence:
  - Both players use canonical center opener: P1 wins all 3 of my contested games.
  - P2 cannot find a winning line against optimal P1 from move 1.
  - Random self-play balanced (8 P1 / 3 P2 / 9 draws) but draws come from non-convergent random play; under skilled play P1 dominates.
  - Training stats show winrate 0.5 — but that's after policy convergence, where both seats learn to draw or near-draw via piece-counting; under skilled greedy play, P1's tempo wins.
  This is the *exact* type of bias the R16 worst-of-three seat-balance probe is supposed to catch (greedy-imbalanced even when random-balanced); my evidence suggests it's still slipping through for this game.

- **Novelty (post-adversary): 4** — Tumbleweed-family on hex with continuous decay and a signed-field twist. Negative-own-cell-value is a real wrinkle but not transformational.

- **Replayability: 4** — Endgame variations are limited; once you find the "open center, hex-extend, race threshold" template, ~70% of moves are forced and the game becomes a counting exercise. Different openings (corner, edge) all lose to center, so opening variety is narrow.

- **Overall "Would I play this again?": 4** — Pleasant influence-counting game once or twice for the gradient-field intuition, but the P1 bias and template-able play kill replay value.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed (on hex, with continuous decay influence)** — both project from each stone, both threshold-on-own-cells, both alternating, both hex. Differences: Tumbleweed uses line-of-sight + stack height, this uses radius-2 disc with exponential decay; Tumbleweed cannot drive own scores negative, this can.

### KILLER FLAWS
- **Significant first-mover advantage** under skilled play (P1 wins 3/3 contested games starting from canonical opener). The R16 worst-of-three seat-balance probe should have flagged this; it apparently did not (`ELO 1263.3, win rate 0.5` from training looks balanced but doesn't reflect the deterministic greedy advantage).
- **Greedy ≈ optimal**: greedy margin-maximizing search returns moves indistinguishable from human-strategic play. This means the game has very shallow horizon; little hidden structure beyond the immediate score gradient.
- **Threshold value is suspiciously well-tuned (34.13)**: it's exactly what an 8-stone hex cluster reaches, which is exactly P1's count after move 15. A slightly higher threshold (~36) might let P2 catch up; slightly lower (~30) makes P1 win even faster. Either way, the game's outcome is mostly determined by tempo parity.

### BEST QUALITY
The **negative-own-cell-value mechanic** is genuinely interesting: a player surrounded by opposing influence can have effectively negative score on their own stones, which forces "rescue moves" (place an own stone nearby to cancel the deficit) that don't appear in standard territory games. This is the one place where the game escapes the Go/Tumbleweed pull.

### IMPROVEMENT IDEAS
**Add a komi or asymmetric threshold.** Set P1 threshold to ~37 and P2 threshold to ~34 (or equivalently, give P2 a 0.5-stone score handicap). Given my Phase-2 evidence that P1 wins the canonical opener by ~5 points consistently, a 2-3 point komi would tighten balance dramatically without changing any other rule. This would convert a P1-dominated game into a near-50/50 contest — which is what the R16 fitness metric was supposed to find but missed.

Alternative: **introduce a single point of tactical decision** by adding a threshold-2 capture ("if a friendly stone has 4 enemy stones within radius 2, it's removed"). This would force defensive cluster shapes and break the "always tighten" template.
