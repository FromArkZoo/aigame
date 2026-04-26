# Run 15 Human Evaluation — team-13 — game 3bde3258978e

**Team ID:** team-13
**Game ID:** 3bde3258978e
**Generation:** 10 (parent 4af27911b0f5)
**Stated metrics:** GE 0.2005, Non-Triv 1.00, Strategic Depth 0.451, Rule Complexity 17, ELO 2596.5
**Sibling game:** d8f2ae54f399 (rank-2) — identical ruleset except `topology_type=grid`. This game uses Moore (8-connectivity).

---

## PHASE 1 — RULE COMPREHENSION

### Plain-English rules
- **Board:** 2D 8×8 (64 cells). Topology = `moore` (8-neighbour connectivity: every cell has up to 8 adjacent cells — orthogonal + diagonal).
- **Turn structure:** **ALTERNATING**, 1 piece per turn. P1 moves first.
- **Actions:** 64 placement actions (cell index `y*8+x`, range 0–63) + action 64 = **pass**. No movement despite `move_constraint: adjacent_empty` being listed — the `action_types` list is `['place']` only.
- **Placement constraint:** any empty cell (`first_move_anywhere: true`, `constraint: anywhere`).
- **Capture rule:** `surround`, threshold 1 — any group of your pieces with **zero Moore-liberties** is removed. On Moore this means a stone only dies when ALL 8 of its adjacent cells are enemy-occupied (for groups, all liberties of the group must be filled). Because Moore has 8 neighbours vs 4 on grid, capture is much harder on this game than on the sibling.
- **Propagation:** `influence`, radius 1, strength 0.9323, decay 0.5097. When player P places at cell C, every cell within Moore-radius 1 (the 3×3 block centred on C, including C itself) receives `±strength * decay^distance` added to `board_values`. Distance 0 (the stone's own cell) = +0.9323, distance 1 (the 8 Moore neighbours) = +0.9323 × 0.5097 ≈ +0.475. P1 adds positive, P2 adds negative (same magnitude). Values accumulate across turns and clamp to ±100.
- **Win condition:** `threshold = 22.6453` on target_dimension 0 (board_values). Engine sums `board_values[c]` over cells currently owned by the player, flips sign for P2 so higher-is-better for both, wins if `> 22.6453`. Checked after every move for both players in P1→P2 iteration order.
- **Game end:** win by threshold, OR `max_turns = 100`, OR double-pass = **DRAW** (R15 rule change).

### Sanity checks / flagged behaviour
- **Engine verified:** single P1 placement at (3,3) produces a 3×3 patch of (+0.475, +0.475, +0.475 / +0.475, +0.932, +0.475 / +0.475, +0.475, +0.475). Nothing else updated. Max possible self-cell value = 0.932 + 8 × 0.475 = 4.73 (all 8 Moore neighbours are own stones).
- **Threshold is reachable.** Random-vs-random over 50 seeds: 100% games resolve by threshold, avg length 45.5 moves, no double-pass draws, no max_turns timeouts. P1 wins 60% (30/50).
- **NOT degenerate:** rules are coherent. No obvious forced win in ≤5 moves (would need ≈24 stones of dense influence ≈ 24 placements minimum).
- **Capture rule non-inert but effectively cold.** Surrounding one isolated X stone costs P2 eight placements on the Moore ring (verified: engine captures at move 8 of the ring). In the same eight moves P1 adds eight stones of threshold progress (worth ~8 × 2–3 effective each at the margin once clustered). Capture is never tempo-positive against a connected cluster — a 2-stone cluster requires surrounding 10 liberties, a 3×3 block requires 16, etc. This makes the game **effectively a pure influence race** with capture as a red herring.
- **Threshold check-order bias:** for this alternating game, only one player moves per tick, so both-cross-same-tick is impossible and the `(1,2)` iteration order in `_check_threshold` does not bias outcomes. (Bias is a simultaneous-game concern.)

---

## PHASE 2 — STRATEGIC PLAY

All moves engine-verified. I ran 3 games as solo agent with distinct named heuristics; ran an additional game 4 (P2 aggressive defender) and game 5 (pure race with no interference) to stress-test conclusions. Seat-identity bias acknowledged — Phase 3 accounts for it.

### Game 1 — P1=greedy, P2=greedy (pure max-Δ-eff each turn)
Moves: `27, 29, 35, 37, 26, 30, 34, 38, 19, 21, 18, 22, 25, 31, 33` (engine-verified with `play_helper.py --action play`, output ends in "GAME OVER: Player 1 wins!").

Both players built mirrored 3×3 clusters at column 3 (X) and column 5 (O), one cell-gap in the middle. Threshold reached by P1 after 8 stones (final eff P1=23.61, P2=19.83). P2 built a symmetric cluster but the extra half-move behind meant P2 hit ~19.83 the instant P1 hit 23.61. **Winner: P1, 15 moves.**

P1 strategy reflection: greedy-center is dominant. No surprise.
P2 reflection: Mirroring is a losing race — P2 needed to interfere with P1's cluster instead of racing independently.

### Game 2 — P1=cluster-center(3,3), P2=cluster-opposite(5,5)
Moves: `27, 45, 19, 37, 26, 44, 18, 36, 11, 46, 20, 53, 28, 38, 35, 52, 34`.
P1 built a cluster at rows 1–4 cols 2–4, P2 at rows 4–6 cols 4–6. Clusters interfere along the diagonal (cells (3,4), (4,3), (4,4), (4,5), (5,4)) — stones in the interference zone have effective value near 0 because + and − cancel. **Winner: P1, 17 moves**, eff 25.02 vs 21.24.

P1 reflection: interference costs us ~2 points of threshold but the race still favours P1.
P2 reflection: The "stay away from enemy" strategy is too passive — the enemy still races ahead.

### Game 3 — SEAT SWAP: P1=cluster-opposite(5,5), P2=cluster-center(3,3)
Moves: `45, 27, 37, 19, 44, 26, 36, 18, 46, 11, 53, 20, 38, 28, 52, 35, 54`.
**Identical outcome:** P1 wins 25.02 vs 21.24 in 17 moves — the board is a mirror of G2. Whoever gets the first-move seat wins regardless of which side of the board they cluster to.

Strategy reflection (new P1, formerly P2): the disadvantage I saw in G2 evaporated when I got the first move. **This confirms seat-identity is the dominant factor, not board position.**

### Game 4 (diagnostic) — P1=cluster-center, P2=aggressive-defender (heavy anti-P1 weighting 1.5×)
41 moves, P1 wins 24.81 vs 20.07. Defender reduces P1's margin and stretches the game but never overtakes. Heat-map shows an interference zone where opposing clusters touch; values near zero on those cells.

### Game 5 (diagnostic) — race with complete spatial separation (P1 cluster at (2,2), P2 cluster at (5,5), no contact)
Mirror build-ups; P1 wins 23.61 vs 19.83 in 15 moves — same result as G1. Confirms: even with zero interference P1 wins by pure tempo because the threshold is reachable in 8 stones and P1 always plays the 8th stone first.

### Seat-balance probe (20 games, greedy vs greedy)
**P1 wins 20/20 (100%).** No draws, no timeouts. This is a massive first-player advantage. Random-vs-random softens it to 60% because greedy-suboptimal noise sometimes hurts P1 more than P2, but under any reasonable "play for threshold" policy P1 wins every time.

### Strategy guides

**P1 strategy:** place first stone at or near centre (3,3) or (4,4). On every subsequent move, play a Moore-neighbour of your own densest cluster cell — this maximises `Δ(own_cell_value)` because the new stone adds 0.475 to its own cell PLUS 0.475 to each existing-adjacent own stone. Do not interact with P2; the race is won by tempo alone. A compact 3×3 cluster produces ~25 points of own-cell value, exceeding threshold.

**P2 strategy:** you cannot win against competent play. Your only hope is to force P1 into a suboptimal cluster. Options tried and rejected:
1. *Mirror cluster elsewhere:* loses the race by ½ tempo (G1, G3, G5, G7).
2. *Defensive blocking:* heavy anti-P1 weighting delays P1 but does not overtake (G4: delay 17→41 moves, still loses).
3. *Surround-capture:* costs 8 P2 moves to remove 1 isolated P1 stone; impossible against a 2+ connected group. Pure tempo loss.
4. *Adjacent cluster (touching P1 at (3,4)):* creates an interference strip that wipes value off both players equally in the touching cells; P1 still reaches threshold elsewhere first.

The only theoretical P2 win requires P1 to deliberately play badly (e.g. isolated corner stones that never cluster).

---

## PHASE 3 — STRATEGIC ANALYSIS (joint P1/P2 reflection)

Acknowledgement: same agent played both seats in all 5 games. Seat-identity bias is controlled by G3's seat swap reproducing the exact same outcome as G2. First-mover advantage is structural, not attributable to my own play bias.

- **Distinct viable strategies?** No. Cluster-early-dominates. All alternatives lose to it. The game has low strategic branching.
- **Meaningful counter-play?** Effectively no. Capture is too expensive (8 P2 moves per single isolated P1 stone, impossible vs any connected group of 2+). Interference costs P2 more than P1 because P2 is already behind. Defence slows the loss but never converts it.
- **Short-term vs long-term tension?** Minimal. Each stone's contribution decays with distance 0.51 so placement quality is visible immediately. No sacrifice play because capture is too expensive to execute and nothing persists that justifies sacrifice.
- **Emergent concepts?**
  - *Influence/territory:* yes, clearly — clusters are territory battles.
  - *Tempo/initiative:* YES — this is the entire game. 1 tempo = 1 stone = ~3 threshold points in a developed cluster.
  - *Interference:* a real but minor phenomenon — cells in the boundary between X and O clusters have values near 0. This is genuinely emergent from + / − influence on Moore radius 1.
  - *Ko fights:* no (capture is rare).
  - *Mutual annihilation:* N/A (alternating not simultaneous).
- **Topology matters?** Somewhat. Moore vs grid (sibling d8f2ae54f399) changes:
  - Max own-cell-value 4.73 (Moore, 8 neighbours) vs 2.83 (grid, 4 neighbours) → threshold 22.65 reached in ~8 stones (Moore) vs ~12 (grid).
  - Liberties: 8 on Moore vs 4 on grid → capture much harder on Moore.
  - Net: the Moore variant is shorter and more tempo-sensitive. The grid version presumably lets P2 catch up or mount captures more credibly, making the P1-bias less severe.
- **First-mover advantage (alternating, per Phase-5 guidance):** **P1 dominates absolutely.** 20/20 under greedy-vs-greedy. Seat-swap G3 shows the advantage is the seat, not the player. This is a balance failure.

---

## PHASE 4 — NOVELTY ADVERSARY (MANDATORY)

### Adversary opening statement
"This game is a **simplified, de-clawed, first-player-gifted Reversi variant masquerading as a Go variant**. Let me demolish it.

**(a) Catalog comparison:**
- **Reversi/Othello:** placement on an 8×8 board, binary occupancy, influence-like flipping. This game replaces the flip with a numeric field sum, but the 'claim territory via placement' primitive is identical. A Reversi expert's intuition for edges/corners and parity transfers immediately (corners are *worse* here because fewer Moore neighbours, not better, but the 'count my influence' mental model is the same).
- **Go:** 8×8, surround capture, placement, threshold territory scoring — this is a **watered-down Go variant where territory is computed via a deterministic Gaussian blur instead of via Chinese/Japanese counting**. A Go player sees this and plays Go: make territory, cluster stones, capture only when free. Literally the same macro-game.
- **Tumbleweed:** a Go-adjacent influence-based abstract where stones cast line-of-sight influence over neighbours. This game is Tumbleweed with radius-1 Moore stencil and two-player mirror signs. Tumbleweed is a known 2018 Mike Zapawa game. This is Tumbleweed-lite.
- **Pente / Gomoku:** irrelevant, line-building not threshold accumulation.
- **Hex / Y / Havannah / Connect6:** connection games, no relation.
- **Amazons / Lines of Action / Chameleon:** movement games, no relation.
- **Conway's Life / Day & Night / HighLife / Immigration Game:** CA-driven, this has no CA (verified: `uses_ca=False`).
- **Mancala:** wrong family (seeds and stores).

**(d) Re-skin proposal:** this is **Go-on-Moore with Gaussian-radius-1 scoring**. Replace 'count stones in territory at end' with 'sum a radius-1 Moore kernel over every stone, weighted by owner sign' and you have this game. A Go player's life-and-death knowledge partially transfers (liberties, groups, surround still matter), plus Go territory valuation maps 1:1 to cluster density.

**(e) Would an expert transfer?** A strong Go player would walk in, play 'good shape' (cluster of 3×3 with extensions), avoid 'overconcentration' (except the game rewards overconcentration because own-neighbour stacking boosts own-cell value), and still win every P1 game. The only Go intuition that breaks is 'overconcentration is bad' — here it is good. That is a single-bit update. **Novelty score from adversary: 2/10 — this is Tumbleweed-meets-Go on Moore, with a broken balance.**"

### Player 1/Player 2 rebuttal

We rebut but partially concede.

- **Tumbleweed analogy (strongest):** Tumbleweed uses **line-of-sight** influence (a stone at A sees to infinity along a line until blocked) and has **piece-stacking**. This game uses **radius-1 Moore kernel** (only 8 neighbours, not line-of-sight) and **no stacking** (one-piece-per-cell). In Tumbleweed strategic decisions turn on sightline blocking and stack heights. No comparable mechanic exists here. The analogy is surface-level.
- **Reversi analogy:** completely fails. Reversi has flipping — pieces change colour mid-game via custodian rule. This game has immovable placements; colour never changes except by surround-capture (which costs 8:1 on Moore and essentially doesn't happen). Reversi corner-stability intuition does not transfer — **here (0,0) is strictly worse than (3,3)** because corners have 3 Moore neighbours vs 8. A Reversi expert who played corner-first would blow the game.
- **Go analogy (weakest of adversary's):** Go's territory-scoring works on end-game emptiness and requires reading life-and-death up to 40 plies. This game's 'territory' is a 15–17-move deterministic influence race — no reading, no group life, no ko. The Go intuition about **groups sharing liberties for survival** is nominally applicable, but since capture essentially never fires (cost 8 moves per isolated stone, impossible vs a connected group), the entire Go sub-game of life-and-death evaporates. Go players playing this would over-value capture threats and under-value raw tempo. **Concrete Phase-2 evidence:** in G4 the "aggressive defender" (which is the Go-player-mental-model — stop the enemy shape) loses harder than the simple mirror (G1).
- **Novel emergent dynamic:** the **interference zone** (cells where + and − clusters touch produce near-zero value) is genuinely emergent and has no direct Tumbleweed/Reversi/Go analog. But it is a minor second-order effect; not worth 4+ novelty points.

**Jointly awarded Novelty: 3/10** — The adversary's Tumbleweed and Go-lite comparisons land. The game is a small variation in a well-trodden "influence accumulation on a grid" design space. The Moore topology + radius-1 kernel + threshold combination isn't a direct re-skin of any single known game, so it clears a 2 ("X on a torus/hex"), but it does not contribute a new mechanic.

---

## PHASE 5 — VERDICT

**Team ID:** team-13
**Game ID:** 3bde3258978e
**Rules Summary:** Alternating placement on 8×8 Moore-connected board; each stone adds radius-1 signed influence (P1 positive, P2 negative, strength 0.932 self / 0.475 neighbours); first player to reach signed-sum ≥22.65 on their own stones wins. Surround capture exists but is too expensive to matter.
**Topology:** 8×8 Moore (8-connectivity).
**Turn Structure:** ALTERNATING, 1 piece per turn, P1 first.

### SCORES (1–10)

- **Strategic Depth: 3** — One dominant strategy ("cluster early and race"). Capture rule effectively inert under Moore 8-connectivity (8 moves to capture 1 stone, impossible vs groups). No tactical sub-games (no ko, no life-and-death, no sacrifice). Planning horizon ~2 moves (play the next Moore-neighbour of your biggest cluster).
- **Emergent Complexity: 3** — One genuine emergent phenomenon: the **interference zone** where opposing clusters touch and values cancel. Beyond that, nothing unexpected arose in 5 playthroughs. Training-run avg length 16–22 moves confirms the game is short and convergent.
- **Balance: 1** — **Severely P1-biased.** 20/20 P1 wins under greedy-vs-greedy. Seat-swap in G3 produced identical board (mirror) with identical margins, confirming the advantage is tempo not seat identity. Threshold 22.65 is reachable in exactly 8 P1 stones, and P1 always plays its 8th stone half a tempo ahead of P2's 8th. No meaningful counter-play found. The stated-rule win condition IS met (not a double-pass draw), but it's met by P1 forced-win.
- **Novelty (post-adversary): 3** — Tumbleweed and Go-lite analogies apply with modest specificity. The interference zone is minorly novel, the Moore+radius-1+threshold combo is at best a small move in known design space. Clears the "X on a torus" floor of 2 but does not establish new mechanics.
- **Replayability: 2** — After ~5 games the dominant strategy is fully understood. Games are 15–25 moves and resolve deterministically once a player commits to cluster-center. No reason to play again once solved.
- **Overall "Would I play this again?": 2**

**CLOSEST KNOWN-GAME ANALOG:** Tumbleweed (2018, Mike Zapawa) — shared "accumulate influence on a hex/grid board, territory-threshold victory" DNA. Not identical because Tumbleweed has line-of-sight propagation and stack heights; this has radius-1 Moore kernel and singleton stones. Secondary analog: simplified Go on an 8×8 with Gaussian-blur scoring instead of stone-count territory.

**KILLER FLAWS:**
1. **Hard first-mover advantage (20/20 in tests).** Threshold 22.65 is reachable in exactly 8 P1 stones and P1 always hits it first under any race-based play. Balance = 1/10.
2. **Capture rule is effectively dead** on Moore topology. Surround cost 8:1 for a lone stone and infinite for a group. The "capture_type: surround, threshold: 1" is present but never fires in realistic play. Rule is inert.
3. **One dominant strategy** collapses the state space to ~15 canonical games. Nothing to explore.
4. **Threshold reachable in <¼ of max_turns** — no endgame phase, no strategic reset, no positional sacrifice. Threshold 22.65 looks chosen to produce short decisive games; it does, at the cost of depth.

**BEST QUALITY:** The **interference zone** — where opposing clusters touch, influence cancels toward zero. This is a genuine signed-field effect that emerges from radius-1 Moore propagation with opposite signs, and it's not mechanically present in Go or Reversi. It's the only thing I'd show someone to argue the game has a mechanic.

**IMPROVEMENT IDEAS:** One rule change: **make this simultaneous (like the R15 GE champion) with mutual-annihilation on collision.** That single change neutralises the first-mover advantage (both players reach threshold on the same tick ⇒ tie broken by absolute effective value or draw) and introduces genuine Blotto/simultaneous-Go strategic pressure around whether to contest the other player's cluster or race for your own. The engine already supports this via `step_simultaneous()`. As a secondary idea: raise the capture threshold to `outnumber` or lower the Moore connectivity to von Neumann (which is the sibling d8f2ae54f399) so capture actually matters.

---

**Engine-verification note:** Phase-2 Game 1 move sequence `27,29,35,37,26,30,34,38,19,21,18,22,25,31,33` was validated end-to-end via `.venv/bin/python play_helper.py --db-path genesis_v2_run15.db --game-id 3bde3258978e --action play --moves "27,29,..."` producing "*** GAME OVER: Player 1 wins! ***" with final P1=8 pieces, P2=7 pieces. All other phases used the same engine via programmatic `create_engine(game).step()` calls with identical legal-action checks.
