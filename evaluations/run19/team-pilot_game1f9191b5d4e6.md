# Run 19 Evaluation — team-pilot — Game 1f9191b5d4e6

**Team ID:** team-pilot
**Game ID:** `1f9191b5d4e6` (Menger rank-1, GE 0.3293, ELO 2402.4)
**Substrate:** Menger sponge (axis 9, 400 active cells / 729 grid positions, max_degree 6)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 1f9191b5d4e6`

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive cells per the level-2 Menger sponge fractal pattern: at every base-3 digit of (x, y, z), at most one coordinate's digit can equal 1. 400 active cells. Cell index = z·81 + y·9 + x. Max degree 6 (axis-aligned 3D), but corners have only 3 neighbours, edges 4, faces 5; many interior cells have only 3-4 neighbours due to the fractal hole pattern. **Holes are denser at the micro-scale than at the macro-scale**: in any 2×2×2 sub-cube, only 4 of 8 positions are active.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max 89 turns.

**Action space.** 730 actions = 729 placements + 1 pass. **Place-only**, D1 hybrid ban active.

**Capture (outnumber-2).** Same mechanism as carpet: place a stone, each enemy neighbour with ≥2 of YOUR stones among its own neighbours is removed.

**Propagation (influence, r=1, s=1.0, d=0.5).** Placement adds ±1.0 to the placed cell and ±0.5 to BFS-distance-1 (i.e., axis-adjacent active) cells only. **No distance-2 contribution** — much shorter reach than carpet rank-1's r=2 kernel. This means clustering requires *adjacency*, not just proximity. Stones at distance 2 (e.g., (0,0,0) and (2,0,0)) do not reinforce each other.

**Win (threshold-race > 29.709).** Same scoring as carpet: sum each player's `board_values` over cells they own; first over 29.709 wins.

**Degeneracy check.**
- No soft-rule violations flagged.
- The fractal hole pattern at the 2×2×2 level (50% active) makes some shapes structurally impossible. A 2×2×2 own-stone cluster cannot exist in a single sub-cube — only 4 of 8 cells are active, and those 4 are typically the corner + 3 axis-adjacent neighbours.
- 6-neighbour cells are rare. Most active cells have 3-4 neighbours. This caps the maximum cluster reinforcement per stone.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Symmetric corner-cube clusters (mirror)

Sequence: `0,728,2,726,18,710,20,708,162,566,164,564,180,548,182,546` (16 plies, in progress).

Plot:
- P1 attempts a 2×2×2 cube cluster at origin: (0,0,0), (2,0,0), (0,2,0), (2,2,0), (0,0,2), (2,0,2), (0,2,2), (2,2,2). All 8 corners of a 3-unit cube — all coords are 0 or 2 (digit-0 = 0), all active.
- P2 mirrors at the opposite corner: (8,8,8), (6,8,8), (8,6,8), (6,6,8), (8,8,6), (6,8,6), (8,6,6), (6,6,6).
- Move 16: both at +8.0 with 8 stones each. **Each stone contributes exactly +1.0 — no cluster reinforcement.**

Reflection: **r=1 punishes 2-apart placements.** All 8 stones in P1's cube are pairwise at distance ≥2 (the corners of a 2-unit-stride cube). The r=1 kernel doesn't reach across this gap, so each stone is functionally isolated. To exploit clustering, stones must be *adjacent* (distance 1).

### Game 1b — Adjacency cluster ("plus" shape)

Sequence: `0,728,1,727,9,719,81,647` (8 plies).

Plot:
- P1 builds the "plus": (0,0,0) + (1,0,0) + (0,1,0) + (0,0,1). The corner cell (0,0,0) is adjacent to all three peripheral cells. P2 mirrors at (8,8,8) + (7,8,8) + (8,7,8) + (8,8,7).
- Move 8: P1 = P2 = +7.0 with 4 stones each. **Per-stone contribution: 1.75 average.** Center stone has 3 own neighbours = +2.5; each peripheral has 1 own neighbour = +1.5.

Reflection: **Adjacency clustering pays.** A 4-stone plus gives +7.0 vs the 4-stone separated cube's +4.0. The optimal cluster shape on menger is a tightly-bonded mass — but the fractal hole pattern caps maximum local density. Beyond 4-stone plus, expanding requires moving to 1-of-3 active sub-cells (further axis-aligned cells, e.g., (2,0,0) or (0,0,2)), which break the adjacency bonus.

### Game 2 — Sandwich attack on 3D corner

Sequence: `0,1,9,81` (4 plies).

Plot:
- P1 (0,0,0); P2 (1,0,0). P2 begins corner sandwich. (0,0,0)'s only 3 active neighbours are (1,0,0), (0,1,0), (0,0,1) — all axis-adjacent, no diagonal cross-overs (the fractal kills (1,1,0), (1,0,1), (0,1,1) as inactive).
- P1 (0,1,0). P1 builds adjacent extension, ignoring threat. **P2 (0,0,1): captures (0,0,0).** (0,0,0)'s P2 neighbours = {(1,0,0), (0,0,1)} = 2 friendlies → outnumber-2 fires. P1 stone removed.
- After 4 moves: P1 has 1 stone (just (0,1,0)), P2 has 2 stones ((1,0,0)+(0,0,1)). P1 = +1.5, P2 = +1.0.

Reflection: **Sandwich works on menger corners with 2 of 3 neighbours required.** Same dynamic as carpet rank-1 but specifically dependent on the 3D corner's 3-neighbour topology. Interior cells with 6 neighbours are harder to capture (need 2 of 6 = 33% coverage instead of 67% for corners). **Corners and edges are the sandwich-vulnerable cells.**

### Strategy guides

**P1 (offence/threshold push):** Avoid corners when anchoring — they're 3-neighbour cells, sandwich-vulnerable. Prefer interior cells with 5-6 active neighbours where possible. Build 4-5 stone "plus" or short chain clusters where each stone has 2-3 own neighbours. Each such cluster contributes ~+8-10 toward threshold; ~3-4 clusters = win at +30.

**P2 (defence + offence):** Mirror loses on tempo. The corner-sandwich is the equaliser. After P1 anchors at any corner or edge, place adjacent and look to capture on the next placement when 2 of the corner's neighbours are P2. Each capture gives P2 a 2-stone cluster as side-effect — those 2 stones are mutually-adjacent (distance 1) so each contributes ≥+1.5.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, two:
1. **Adjacency cluster + threshold race** (P1's playbook). Build dense plus/chain shapes; expand into adjacent sub-cubes; race to 30.
2. **Sandwich-then-cluster** (P2's playbook). Trade 2 stones for 1 capture at a P1 corner; the captured-corner's 3 neighbour cells become a P2 cluster seed. Pivot from attack to threshold race.

**Counter-play.** Real but knowledge-asymmetric. P1's main counter is to anchor at interior cells (4-6 neighbours) where sandwich requires more committed surrounding. But interior cells in menger are not common — most are at 3-4 neighbour positions due to the hole pattern.

**Short-term vs long-term.** Threshold 29.7 / per-move gain ≈ 1.5–2.5 → ~12–20 plies per side to threshold. Real games average 38.8 moves total. ~6–10 ply tactical horizon. The 3D space is large enough that local cluster decisions don't immediately interact with global threshold race.

**Emergent concepts observed.**
- **Corner sandwich (3D).** Same family as carpet's sandwich but adapted to 3-neighbour corner geometry. P2 only needs 2 of 3 neighbour cells to trigger.
- **Adjacency cluster.** Distinct from R8/R17 connection-based games — the cluster is for influence accumulation, not chain completion.
- **Hole-shape constraint on cluster geometry.** A 2×2×2 own-stone cube is impossible (only 4 cells active); a 3×3×3 own cluster requires 20 stones (and many gaps). This is genuinely substrate-driven novelty.
- **Tempo crossover** (same as carpet): P1 wins under symmetric play due to going first.

**Does the menger substrate matter?** *Substantively, more than carpet.* The fractal's micro-scale density pattern (50% active in any 2×2×2) directly constrains cluster shapes. Players can't build "big blobs" — clusters are forced into specific fractal-allowed geometries (plus, chain, 3D-corner). On a regular 3D grid (8³ = 512 cells, all active), the same rules would allow much denser clusters and shorter games. **The menger substrate adds a real strategic axis: cluster-shape feasibility.** Estimate: the menger-specific play would lose ~1.0 point of strategic depth if flattened to an unholey cube.

**Does the propagation kernel matter?** Critically. r=1 vs r=2 (carpet rank-1's value) is the difference between "adjacency-required" and "proximity-required" clustering. r=1 makes the menger holes much more painful — distance-2 stones are useless to each other, so a hole between two intended-adjacent stones breaks the cluster.

**Capture-rule contribution.** Captures fired in Game 2. Frequency: 1 in 4 moves under sandwich attack. Same trade-economics as carpet (2-for-1 with cluster side-effect). **Captures are again the only real balance mechanism.**

**First-mover advantage / seat balance.** Heavily P1-favoured under symmetric play (Game 1 and 1b). Balanced when P2 plays sandwich counter (Game 2). Same knowledge-asymmetric balance as carpet rank-1.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + outnumber + threshold-race on a 3D fractal. Argument:

(a) **Influence-based scoring** — same family as carpet rank-1. Closest published: *Tumbleweed* (2D hex), *Sygo* (Go territorial weights). 3D fractal version is novel.

(b) **Outnumber-2 capture** — same Tafl/Ataxx adjacency mechanic.

(c) **The 3D combination** "outnumber-2 + r=1 influence + threshold-race on menger" is genuinely unprecedented in published abstract-game literature. 3D abstract games are rare (Score Four, Qubic, Connect 4-3D) and none use influence weights or fractal substrates.

(d) **Menger sponge substrate** is a 3D Hausdorff-2.727 fractal — extremely rare as a board-game substrate. The closest published case is theoretical 3D-Hex literature (Hales–Jewett); no published game uses the menger structure specifically. **This is the strongest novelty axis the game has.**

(e) **Expert-transfer test.** A Go + Othello + Hex player + 3D-Tic-Tac-Toe (Qubic) player working together would understand the rules in 10 minutes. The novel pieces they'd internalise: (i) the fractal hole pattern (which cells are active, which are not), (ii) influence-as-scoring with r=1 short range, (iii) the 3D outnumber dynamics around corners vs edges vs interior.

**Closest known-game analogue:** **Influence-based 3D Tafl on a Menger sponge.** No exact analogue exists. Inside this project corpus, the closest is R17 rank-2 (`a3a6bd2b1b5b`) which used surround capture + perpendicular-axis connection on 3D-4³ grid — different family entirely.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was 2D custodian + connection. R19 menger rank-1 is 3D outnumber + influence + threshold. Different family. R19 is more "spatial" (no narrative connectivity goal); R8 is more "narrative" (build a chain to win). R19's strength over R8: genuinely 3D + fractal substrate combinatorics. R19's weakness: lacks the clear narrative arc that R8's connection goal provides.

**Player rebuttal (P1 + P2).**
- The fractal-substrate-driven cluster geometry constraints are *substrate-specific* and not present in any pure 3D grid abstract game.
- The 3-neighbour-corner sandwich attack is structurally interesting in 3D — corners are vulnerable, interiors are safe. This isn't present in 2D where corners have 2 neighbours (still sandwichable but with different combinatorics).
- Subtracting from novelty: the strategic skeleton (cluster + race + sandwich) is recognisable from carpet rank-1; the menger version is a 3D adaptation rather than a structurally different game.

**Novelty score (post-adversary):** **6/10.** Above carpet rank-1 (5) primarily because (i) the menger substrate itself is unprecedented in published literature, (ii) 3D fractal cluster geometry is genuinely substrate-driven, (iii) the 3-neighbour-corner sandwich is geometrically distinct from 2D versions. Below 7-8 because the strategic family (capture + influence + race) is shared with carpet rank-1 and known elsewhere.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** 1f9191b5d4e6
**Rules Summary:** Place stones on a 9×9×9 menger sponge (400 of 729 cells active) to accumulate influence on cells you own. Each placement spreads ±1.0 to itself and ±0.5 to adjacent cells; capture fires when an enemy stone has ≥2 of your stones among its neighbours. First to >29.7 effective influence wins.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 (effective 3-5 for most cells).
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 6** — Slightly above carpet rank-1 because 3D + fractal cluster geometry adds a real planning dimension. Cluster shapes are constrained (no 2×2×2 cubes possible; plus/chain/L-shape are the workable patterns). Capture mechanics + clustering interplay is meaningful.
- **Emergent Complexity: 5** — Sandwich + cluster + tempo race patterns. 3D adds variety but not new emergent vocabulary beyond carpet rank-1's.
- **Balance: 4** — Same knowledge-asymmetric issue. Mirror = P1 win. Sandwich = P2 counter. Trained-vs-trained 0.500 reflects PPO learning the asymmetric counter.
- **Novelty (post-adversary): 6** — see Phase 4. The menger substrate itself is the novelty driver — unprecedented in published game literature.
- **Replayability: 5** — 400 cells gives much more position variety than carpet's 64. The fractal-constrained cluster geometry creates real opening variety. Above carpet rank-1 by 1.
- **Overall "Would I play this again?": 5** — Once: yes, the 3D sandwich and fractal cluster constraints are interesting to feel. Repeatedly: maybe — the strategic ceiling is similar to carpet rank-1, but the larger board takes more games to fully explore.

### CLOSEST KNOWN-GAME ANALOG
**Influence-based 3D Tafl on a Menger sponge.** No published analogue. Within this project corpus, the closest is the carpet rank-1 (`ce3a09e05cef`) — same strategic family, 2D version with bigger r=2 influence kernel.

### KILLER FLAWS
- **Mirror = P1 win** (structural, same as carpet rank-1).
- **r=1 makes hole-routing punishing.** A hole between two stones means they don't reinforce at all (vs r=2 where dist-2 still gives +0.25). This makes the menger substrate harsher than carpet for influence accumulation.
- **Knowledge-asymmetric balance.** PPO learned the counter, but a naïve player playing P2 with mirror loses every time.
- **Cluster geometry constrained to a small set.** 4-stone plus, 3-stone chain, 5-stone L-shape — once these are known, opening variety collapses.

### BEST QUALITY
**The menger substrate itself.** The fractal hole pattern at the 2×2×2 micro-scale forces cluster geometry into specific shapes that no regular grid would impose. This is a genuinely substrate-driven strategic constraint and the strongest novelty axis in R19. The 3D corner-sandwich (2 of 3 neighbours) is also structurally interesting and geometrically distinct from 2D sandwiches.

### MENGER STRUCTURAL CONTRIBUTION
**Substantial — more than carpet's contribution to its rank-1 game.** The fractal hole density at the micro-scale (50% in any 2×2×2) directly constrains cluster shapes and forces specific opening patterns. The 3D corner geometry (3 neighbours) creates a sandwich-vulnerability profile distinct from 2D corners (2 neighbours). Estimate: flattening to an unholey 8×8×8 cube would lose ~1 point of depth and most of the substrate-driven novelty. The menger contribution is **about 1 point of depth + 1 point of novelty** vs. a regular 3D grid analogue.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same recommendation as carpet rank-1). The mirror-favours-P1 dynamic is structural; pie rule punishes any opening strong enough to mirror profitably and forces P1 to balance opening strength vs. swap risk.

Secondary improvements:
- **Increase influence radius to r=2** to soften the hole-routing penalty and let players span across single-cell holes. Would make the game more carpet-like.
- **Increase capture threshold to 3** so corner captures require 2-of-3 + something else (impossible with 3 neighbours → corners become safe). Would shift balance toward P1.
- **Add a connection or territory secondary win condition** — purely additive — to give the game narrative tension beyond the influence threshold race. Closest to R8's family that the eval report identifies as the all-time ceiling.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-pilot_game1f9191b5d4e6.md`.*
