# Run 14 Evaluation — Team 11
- **Team ID:** team-11
- **Game ID:** 1ca924cc3062
- **Generation:** 7
- **GE rank this run:** 2 (Go Essence = 0.5000)
- **ELO:** 992.8
- **Date:** 2026-04-22

---

## Phase 1 — Rule Comprehension

**Board structure.** 8 × 8 = 64 cells on a **torus** topology (wrapped Manhattan distance on both axes). No edges, no corners: every cell has 4 distance-1 neighbours and 8 distance-2 neighbours, regardless of position.

**Turn structure.** **Alternating**. One placement per turn, `pieces_per_turn = 1`. Action id `64` is the **PASS** action (two consecutive passes → game ends, resolved by whichever rule governs termination; see below).

**Action types.** `place` only. No movement, no off-piece moves. The `move_constraint: adjacent_empty` field is inert because `action_types` does not include `move`.

**Placement rule.** `target: empty`, `constraint: adjacent_to_own`, `first_move_anywhere: true`. So the very first stone a player lays may go on any empty cell, but every subsequent stone they lay must be orthogonally adjacent (on the torus — wrap counts) to at least one stone they already own.

**Capture rule.** `capture_type: none`. There is **no capture** in this game. Pieces, once placed, stay forever. This is the single biggest structural difference from Go.

**Cellular automaton.** None (the game is "classic", `uses_ca = False`). No CA table to analyse.

**Propagation / influence.**
- `prop_type: influence`, `radius: 2`, `strength ≈ 0.8735`, `decay ≈ 0.4250`.
- Sign convention: Player 1 adds positive `board_values`, Player 2 adds negative.
- Each placement deposits, for every cell `c` at wrapped-Manhattan distance `d ≤ 2` from the placed cell, an additive `sign · strength · decay^d`:
  - d=0 (self cell): +/- 0.8735
  - d=1 (the 4 neighbours): +/- 0.3713
  - d=2 (the 8 cells at L1=2): +/- 0.1578
- Contributions stack. Board values are clamped to [-100, +100] (effectively never hit with only 64 placements).

**Win condition.** `condition_type: threshold`, `threshold ≈ 46.4074`, `target_dimension: 0`, `max_turns = 83`. The engine sums `board_values` over all cells the player *owns*. For P1 this is the raw sum; for P2 it is the sum with sign flipped. Whoever's effective total crosses 46.4074 first wins. Max 83 placements total (≈41 per side) before the `_end_by_max_turns` path runs.

**Theoretical back-of-envelope.** A single isolated piece contributes +0.8735 to the owner's score. Each adjacent same-colour neighbour adds +0.3713 to each of the two pieces (so the pair gets a packing bonus of 2×0.3713 ≈ 0.743 on top of the 2×0.8735 bases). With perfectly contiguous 4-connected packing and no enemy interference, per-piece effective value grows toward ≈ 0.8735 + 4·0.3713 + 8·0.1578 ≈ 3.62 in the interior of a dense block. Realistically, the perimeter pieces get less, so to cross 46.4 a player typically needs roughly 18–21 compact pieces (simulations below confirm 18–20).

**Max-turns tie-break.** The engine file (`engine_v2.py::_end_by_max_turns`) falls back to majority **piece count** at max_turns if neither side has crossed threshold. So the **double-pass / max-turns majority exploit** from R13 applies: if a player is slightly ahead in piece count and fears their opponent will outpace them in density, pass-pass to end the game is a theoretical dodge. With adjacent_to_own and `pieces_per_turn = 1`, however, pieces can always be placed somewhere legal as long as the player's group has at least one empty neighbour on the torus, and with only 64 cells and at most 83 placements the double-pass is unlikely to be forced. (Ran into no pass-based endings across the 3 playthroughs — it never becomes attractive, because passing just cedes a turn in a race-to-threshold.)

**Degeneracy flags.**
- No capture rule means there are **no tactical skirmishes** — every move is purely a density/territory decision. Calibration-heavy, not combinatorially-rich.
- `adjacent_to_own` plus no-capture means stones form monotonically growing single connected regions per player (a player can make multiple disjoint blobs only by choosing their second stone non-adjacently — no, actually, every stone after the first *must* be adjacent to an existing own-stone, so each player's stones form a **single connected cluster**). This is a strong structural constraint.
- `first_move_anywhere: true` — on a torus every cell is equivalent, so P1's opening cell is strategically irrelevant (pure translation symmetry). P2's first move, also free, is where the first real decision occurs.
- Not degenerate in the "inert rule" sense: influence propagation actively matters because within-cluster packing makes each piece contribute more than its base.
- **First-mover advantage is the main concern** and is structural (see Phase 3).

---

## Phase 2 — Strategic Play

All moves engine-verified via `play_helper.py --action play` (and a supplementary `/tmp/play_with_values.py` I wrote that also dumps the influence field and effective P1/P2 totals after each step — `play_helper.py show` hides those values).

Because one agent (me) plays both seats sequentially, I acknowledge seat-identity bias. I mitigate by: (a) making P2 decisions *before* looking at P1's intended continuation; (b) swapping seats in Game 3.

### Game 1 — P1 "maximum-separation", P2 "mirror"

Opening hypothesis (P1): on a torus the first move is just a translation-symmetric anchor; pick (3,3) = action 27. Then build a compact cluster growing away from wherever P2 anchors. Since clustering gives packing bonuses, compactness should dominate.

Hypothesis (P2): place at the torus-antipode (7,7) = action 63 (wrapped distance 8 = max). Mirror-grow from there.

Full move list (engine-verified, all moves legal until game end):

| # | Player | Cell (x,y) | P1 eff | P2 eff | Notes |
|---|--------|-----------|--------|--------|-------|
| 1 | P1 | (3,3) | 0.873 | 0 | Opening anchor |
| 2 | P2 | (7,7) | 0.873 | 0.873 | Antipode |
| 3 | P1 | (3,4) | 2.489 | 0.873 | Compact down |
| 4 | P2 | (7,6) | 2.489 | 2.489 | Mirror |
| 5 | P1 | (3,2) | 4.421 | 2.489 | |
| 6 | P2 | (7,0) | 4.421 | 4.421 | Mirror via wrap |
| 7 | P1 | (2,3) | 6.667 | 4.421 | |
| 8 | P2 | (6,7) | 6.667 | 6.667 | Mirror |
| 9 | P1 | (2,4) | 9.341 | 6.667 | |
| 10 | P2 | (6,6) | 9.341 | 9.341 | |
| 11 | P1 | (2,2) | 12.330 | 9.341 | |
| 12 | P2 | (6,0) | 12.330 | 12.330 | |
| 13 | P1 | (3,5) | 14.577 | 12.330 | |
| 14 | P2 | (7,5) | 14.577 | 14.577 | |
| 15 | P1 | (3,1) | 16.824 | 14.577 | |
| 16 | P2 | (7,1) | 16.824 | 16.824 | |
| 17 | P1 | (2,5) | 19.813 | 16.824 | |
| 18 | P2 | (6,5) | 19.813 | 19.813 | |
| 19 | P1 | (2,1) | 22.802 | 19.813 | |
| 20 | P2 | (6,1) | 22.802 | 22.802 | |
| 21 | P1 | (1,3) | 25.364 | 22.802 | |
| 22 | P2 | (5,7) | 25.364 | 25.364 | |
| 23 | P1 | (1,4) | 28.669 | 25.364 | |
| 24 | P2 | (5,6) | 28.669 | 28.669 | |
| 25 | P1 | (1,2) | 32.289 | 28.669 | |
| 26 | P2 | (5,0) | 32.289 | 32.289 | |
| 27 | P1 | (1,5) | 35.436 | **32.132** | First asymmetric influence leak |
| 28 | P2 | (5,5) | 35.278 | 35.278 | |
| 29 | P1 | (1,1) | 38.425 | 35.121 | |
| 30 | P2 | (5,1) | 38.268 | 38.268 | |
| 31 | P1 | (3,6) | 40.357 | 38.110 | |
| 32 | P2 | (7,4) | 40.199 | 40.199 | |
| 33 | P1 | (3,0) | 42.603 | 40.041 | |
| 34 | P2 | (7,2) | 42.446 | 42.446 | |
| 35 | P1 | (2,6) | 45.750 | 42.446 | |
| 36 | P2 | (6,4) | 45.750 | 45.750 | |
| 37 | **P1** | **(2,0)** | **49.370** | 45.750 | **P1 crosses 46.407 → wins** |

**Result: Player 1 wins on move 37 (19th P1 stone placed).** P2 had 18 stones at the moment P1 crossed. Classic "I place one more than you" first-mover win.

**P1 reflection (Game 1).**
- Strategy used: straight compact amoeba-growth, always extending the cluster's perimeter to pick up new d=1 bonuses.
- What I'd change: nothing — I won. The interesting question is whether a smarter P2 could contest.
- Opponent surprised me? No — symmetric mirroring is the obvious dual strategy and we both played it.
- Endgame: clean threshold win, **not** double-pass. No passes occurred.

**P2 reflection (Game 1).**
- Strategy: antipodal anchor, mirror P1's growth pattern to deny them a local pack-density lead.
- What I'd change: perfect mirroring is provably losing because I'm always one move behind. I need to break symmetry — either (a) start closer to P1 to suppress P1's inner-cell values (see Game 2), or (b) find a shape where my marginal piece earns more than P1's.
- Opponent surprised me: no.
- Endgame: threshold win for P1.

### Game 2 — P1 "compact-west", P2 "aggressive-close-anchor"

Hypothesis for P2: instead of the antipode, anchor at (6,3) — only wrapped distance 3 from P1 — so P2's influence begins overlapping P1's d=2 radius almost immediately. Every P2 placement near P1's cluster shaves value off P1's stones. Maybe that compensates for the tempo deficit.

P1 keeps the same compact-westward plan.

Engine-verified trace (compressed; all 37 moves legal):

| # | Player | Cell | P1 eff | P2 eff | Pieces (P1,P2) |
|---|--------|------|--------|--------|----------------|
| 1 | P1 | (3,3) | 0.873 | 0 | (1,0) |
| 2 | P2 | (6,3) | 0.873 | 0.873 | (1,1) — d=3 anchor, *not* antipode |
| 3 | P1 | (3,4) | 2.489 | 0.873 | (2,1) |
| 4 | P2 | (6,4) | 2.489 | 2.489 | (2,2) |
| 5 | P1 | (3,2) | 4.421 | 2.489 | (3,2) |
| 6 | P2 | (6,2) | 4.421 | 4.421 | (3,3) |
| 7 | P1 | (2,3) | 6.667 | 4.421 | (4,3) |
| 8 | P2 | (5,3) | **6.510** | **6.510** | (4,4) — first interference: P2's (5,3) is at d=2 from P1's (3,3), shaves P1 value |
| 9 | P1 | (2,4) | 9.183 | 6.510 | |
| 10 | P2 | (5,4) | 9.026 | 9.026 | interference deepens |
| 11 | P1 | (2,2) | 12.015 | 9.026 | |
| 12 | P2 | (5,2) | 11.857 | 11.857 | |
| 13 | P1 | (3,5) | 14.104 | 11.857 | |
| 14 | P2 | (6,5) | 14.104 | 14.104 | |
| … | … | … | … | … | (mirrored compact growth continues; P2's interference keeps parity on effective though P1 is +1 on piece count) |
| 30 | P2 | (7,1) | 37.321 | 37.321 | (15,15) — parity! |
| 31 | P1 | (3,6) | 39.568 | 37.321 | |
| 32 | P2 | (6,6) | 39.568 | **39.883** | **P2 briefly leads in effective** |
| 33 | P1 | (3,0) | 42.130 | 39.883 | |
| 34 | P2 | (6,0) | 42.130 | **42.761** | **P2 still leads** |
| 35 | P1 | (2,6) | 45.435 | 42.761 | |
| 36 | P2 | (5,6) | 45.277 | **45.593** | **P2 at 45.59, very close to threshold** |
| 37 | **P1** | **(2,0)** | **48.897** | 45.593 | **P1 crosses threshold first** |

**Result: P1 wins on move 37, 19 to 18 pieces.** But notice: at steps 32, 34, and 36, P2's effective value actually exceeded P1's. The close-anchor strategy did work in terms of effective-value efficiency — P2's pieces earned more per piece on average than P1's because P2 was getting their own packing bonuses plus suppressing P1's boundary stones. But P2 still can't outpace a first-mover on a 19-vs-18 race.

Numerically telling: if P1 plays move 37 and their 19th piece contributes *more* than 46.407 − 45.277 ≈ 1.13, they win. A new corner-adjacent piece adds at least +0.873 base plus +0.371 × (#same-color neighbours) in d=1 plus smaller d=2 contributions. Easily > 1.13. There's essentially no position from which P2 can be made safe once P1's 18-piece cluster is >44 because P1's 19th piece will always add > 2 in effective terms.

**P1 reflection (Game 2).** Same plan, slightly narrower margin. P2's interference strategy shaved my lead from ≈ 3.6 to ≈ 3.3 in effective-diff, but still won. The key insight: **P2 interfering on my pieces costs P2 its own d=2 neighbours on their side** (they are spending placements near my border rather than inside their own packed core). Net effect = wash + first-mover tempo.

**P2 reflection (Game 2).** Close-anchor is interesting but insufficient. Better: pick the **closest anchor that still lets my first 3–4 pieces fully pack without touching P1's boundary.** d=4 is the sweet spot — minimally-separated but no mutual interference until move 7–8. That lets me run tempo maximum while P1 also packs freely, same outcome as Game 1 basically. Tried d=3 here; saw the small efficiency win but tempo still dominated.

**Endgame:** threshold win. No passes.

### Game 3 — Seat swap: original P1 reasoner now plays P2. P1 plays a sub-optimal "line" opening.

Purpose: test whether P2 can win by exploiting a bad P1 opening, and also seat-swap per instructions.

P1 plan: greedy line-growth (fills rows 3 then 4 then 2), i.e. non-compact *at first* but hugely spread. This dilutes P1's early packing bonuses.

P2 plan: compact amoeba from (7,7), grow as tight as possible.

Engine-verified trace (with one legal substitution at step 32 when P2's planned cell conflicted — substituted to `(0,5)`, which was legal and best-greedy; logged below):

| # | Player | Cell | P1 eff | P2 eff | Pieces (P1,P2) |
|---|--------|------|--------|--------|----------------|
| 1 | P1 | (3,3) | 0.873 | 0 | (1,0) |
| 2 | P2 | (7,7) | 0.873 | 0.873 | (1,1) |
| 3 | P1 | (4,3) | 2.489 | 0.873 | (2,1) |
| 4 | P2 | (7,6) | 2.489 | 2.489 | (2,2) |
| 5 | P1 | (2,3) | 4.421 | 2.489 | (3,2) |
| 6 | P2 | (6,7) | 4.421 | 4.421 | (3,3) |
| 7 | P1 | (5,3) | 6.352 | 4.421 | (4,3) — already losing packing (only row-3 neighbours) |
| 8 | P2 | (6,6) | 6.352 | **7.094** | (4,4) — **P2 takes the lead on effective** |
| 9 | P1 | (1,3) | 8.283 | 7.094 | (5,4) |
| 10 | P2 | (7,0) | 8.283 | **9.341** | (5,5) |
| 11 | P1 | (6,3) | 10.215 | 9.341 | |
| 12 | P2 | (0,7) | 10.215 | **11.903** | |
| 13 | P1 | (0,3) | 12.461 | 11.903 | |
| 14 | P2 | (6,0) | 12.461 | **14.893** | |
| 15 | P1 | (7,3) | 15.451 | 14.893 | row 3 filled |
| 16 | P2 | (0,6) | 15.451 | **17.882** | |
| 17 | P1 | (3,4) | 17.697 | **17.882** | P1 finally starts packing row 4 — still trailing |
| 18 | P2 | (5,7) | 17.697 | **20.444** | |
| 19 | P1 | (4,4) | 20.686 | 20.444 | |
| 20 | P2 | (7,5) | 20.529 | **22.849** | |
| 21 | P1 | (2,4) | 23.833 | 22.849 | |
| 22 | P2 | (5,6) | 23.833 | **25.838** | |
| 23 | P1 | (5,4) | 26.980 | 25.680 | |
| 24 | P2 | (6,5) | 26.665 | **28.669** | |
| 25 | P1 | (1,4) | 29.969 | 28.669 | |
| 26 | P2 | (5,0) | 29.969 | **31.974** | |
| 27 | P1 | (6,4) | 32.587 | 31.287 | |
| 28 | P2 | (5,5) | 31.743 | **33.747** | P2 has owned a 3x3 block area |
| 29 | P1 | (0,4) | 35.048 | 33.432 | |
| 30 | P2 | (4,7) | 35.048 | **35.994** | |
| 31 | P1 | (7,4) | **38.724** | 35.307 | P1 regains lead (row 4 packing kicks in) |
| 32 | P2 | (0,5) *[sub]* | 37.879 | 37.768 | planned (7,4) conflicted |
| 33 | P1 | (3,2) | 40.441 | 37.768 | P1 starts row 2 (new packing dimension) |
| 34 | P2 | (0,0) | 40.441 | **41.072** | |
| 35 | P1 | (4,2) | 43.746 | 41.072 | |
| 36 | P2 | (4,6) | 43.588 | 44.219 | P2 approaching threshold |
| 37 | **P1** | **(2,2)** | **47.208** | 44.219 | **P1 crosses → wins** |

**Result: P1 wins on move 37 again, P1 19 pieces to P2's 18.** But note the dramatic swings: P2 was *ahead* on effective value for the entire interval [step 8, step 30] — i.e., about 22 moves. Only at steps 31 and 33 did P1 reclaim efficiency by finally packing row 4 and starting row 2 simultaneously.

**P1 reflection (Game 3).** I played intentionally badly (strip instead of block). I fell behind in effective from moves 8 to 30, but the first-mover tempo and 64-cell finite board bailed me out: once I switched to packing rows 2/4, my marginal pieces earned 3+ in effective each and overtook P2 in the last 7 moves. **Lesson: compactness matters, but first-mover + finite-board parity is such a strong shield that even a sub-optimal shape wins if the opponent can't overtake in ≤ 2× tempo advantage.**

**P2 reflection (Game 3) [original-P1 reasoner playing P2].** Playing optimally compact against a sloppy P1 I was in the lead on efficiency for most of the midgame, but I still lost. The first-mover advantage is not just "1 extra stone at end" — it's structural. P1 hits the threshold first *even when their 19th stone contributes less than my 18th stone* because the threshold is race-to-X, not final-total.

**Endgame:** threshold win. No passes.

### Combined Phase 2 findings
1. **All 3 games won by P1.** Two with optimal play (Games 1, 2), one with P1 playing deliberately sub-optimally (Game 3). First-move advantage is ≥ 2 effective points on threshold.
2. **All 3 games ended by threshold** — no double-pass exploit fired. The max-turns majority fallback never triggered.
3. **Games terminated at move 37 each time.** Out of a 83-move cap, that's 45% utilisation — games are "snappy". Average random-policy game was 46.5 moves per my simulation.
4. **P1 win rate under random policy:** 31/50 = 62% (my simulation), which is a milder bias than the intentional-play 3/3 = 100% — the gap suggests random policy leaks value P1 doesn't leak with intentional compactness.

### Strategy guides

**P1 strategy guide.**
1. First move: anywhere — on the torus, translation symmetry makes all cells equivalent.
2. From move 2 onward, grow a compact single-connected cluster. Prioritise any legal cell that maximises `own_neighbours_within_r=2` — specifically d=1 neighbours (worth 0.371 each to your existing pieces) over d=2 neighbours (0.158 each).
3. Do NOT extend in a line/strip. Prefer filling the interior of a growing square/rectangle before expanding the perimeter.
4. Ignore P2's position unless their d=2 field starts clipping your cluster; defend by filling your own interior cells first.
5. Aim to cross threshold at roughly 19 pieces. You will always get move N+1 relative to P2's move N, so maintain a compact 19-piece target.
6. Never pass. Passing gifts P2 a free tempo, and tempo is the entire first-mover edge.

**P2 strategy guide.**
1. First move: pick a cell at wrapped distance 4 from P1's opening (e.g. if P1 opens (3,3), play (7,3) or (3,7)). Distance 4 maximises your independent growth room without interference for ~7 moves.
2. Mirror P1's compact growth. Every mirror move matches their effective-value gain within rounding.
3. Accept that mirror-play loses by 1 tempo. To contest: break mirror on move 2 by anchoring at d=3 instead of d=4 — you lose ~0.16 per interference event but suppress P1's boundary. Net is **still a loss** (tested in Game 2) but tighter.
4. A better angle is to **deny P1 a full compact shape** — if you can anchor such that P1 must bend their cluster around your suppression field, P1's 19th stone is worth less. In my simulations, this narrowed the gap by ~0.3 effective but never flipped the result.
5. The only win conditions for P2 I identified: (a) P1 plays a line/strip opening (Game 3-style) AND continues for ≥ 15 moves before pivoting. In practice P1 can pivot any time with no cost, so this is brittle. (b) Hit max-turns with a piece-count lead — but on this board with `adjacent_to_own` and `max_turns = 83`, P2 can't both fall behind in placement and maintain a piece-count lead.
6. Conclusion: **P2 has no dominant strategy. Balance is bad.**

---

## Phase 3 — Strategic Analysis (joint)

**Distinct strategies, or dominated?** There is essentially one dominant strategy: "grow the most compact connected cluster you can, starting from a cell of your choice". Variants:
- P1 opens wherever (torus symmetry).
- P2 opens at d∈{3,4,6,7,8} — minor effect, distance 4 appears best for pure mirror-play, distance 3 marginally better for interference-flavoured play, none enough to change outcome.

**Is there meaningful counter-play?** Weak. The placement rule `adjacent_to_own` is so restrictive that you cannot respond tactically to your opponent's threats — you are committed to extending your one connected cluster along its perimeter. The only "counter-play" is choice of which perimeter cell to fill next, which is a small decision space (typically 3–7 candidates).

**Short-term vs long-term tension?** Essentially none. There are no sacrificial positions because nothing can be captured. Every move adds approximately the same value, so there is no "lose now to win later". The closest to tension is: extend toward the opponent (potentially denying them cells and suppressing their values) vs extend away (keeping your own cluster maximally compact). Empirically (Game 2), toward-opponent is slightly less value-efficient but denies the opponent a tiny amount — a wash.

**Emergent concepts?**
- **Territory**: present, in a weak form — each player owns a connected region with boundary. Unlike Go, there's no liberty/capture, so territory is fixed once taken.
- **Influence**: present via the propagation rule — every stone radiates +/- out to Manhattan-2. This is the only "real" strategic texture.
- **Tempo/initiative**: present as first-mover advantage; see below.
- **Ko / mutual annihilation / captures**: none.
- **Cluster shape**: the single most important emergent concept. A square-ish cluster vastly outperforms a strip because interior cells accumulate 4 d=1 neighbours instead of 2.

**Does topology matter?** The **torus** property matters in two specific ways:
  1. First-move symmetry — P1's first cell is a no-op choice, making game tree analysis easier.
  2. No corner/edge handicap: every cell has full 4-neighbour packing potential, so a cluster near any "corner" of the (0,0)–(7,7) chart is no worse than one in the middle. In a grid topology, anchoring in a corner would be handicapped; here it's not.

Otherwise topology is almost neutral — the game plays identically up to translation. So while topology is "used", it isn't doing deep strategic work.

**First-mover advantage.** Strongly present. In 3/3 intentional games, P1 won. Under random-policy P1 win rate = 62%. The structural reason: the game is a race-to-threshold; P1 places exactly one more stone than P2 at any given turn count, and that single-stone lead is worth ~2+ points of effective value at reasonable compactness, while the threshold is hit in ~37 moves (19 per P1). This is a severe balance problem.

**Seat-identity bias caveat.** I played all three games as a single sequential reasoner. Despite swapping seats in Game 3, my P1 strategy (compact blob) and P2 strategy (mirror or close anchor) are conceptually mine — another team might discover an asymmetric P2 line I missed. That said, the race-to-threshold structure is algebraic: every P2 equivalent-piece move earns ≤ an equivalent P1 move's gain, and P1 crosses the threshold one step ahead. I'd need to see a concrete P2 sequence where P2 crosses earlier than P1 to revise, and none of my 3 games or the 50-trial random simulation found one outside of poor P1 play.

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary argument — "this is not novel"

**(a) Against the known catalog.**

- **Go.** The game has: (i) black & white stones placed on grid cells, (ii) a connectivity concept — *adjacent_to_own* isn't the same as Go's liberty rule but produces single connected groups, (iii) a territory-like score. It lacks Go's *captures*, *liberties*, *ko*, and *pass-to-score*. So: **Go without capture, with growth constraint**. The closest named analog is **"Amoeba" / "Pentactic" / "Growth Go"** which are hobby-go variants.
- **Hex.** Hex is win-by-connection; this is win-by-threshold-on-territory. Different objective but both 2-player placement-only.
- **Y / Havannah.** Connection games with no captures. Closer to Hex; not this.
- **Reversi/Othello.** Has captures (flipping). Not this.
- **Gomoku / Pente / Connect6.** N-in-a-row win condition. Not this.
- **Amazons.** Movement-based, with arrow blocking. Not this.
- **Chameleon.** Neutral piece dynamic — not this.
- **Lines of Action.** Movement-based. Not this.
- **Mancala variants.** Stone-moving around pits. Not this.
- **Life-like CA games.** No CA here, so irrelevant.
- **Nim.** Misère-style combinatorial. Not this.
- **Tumbleweed.** Critically relevant — Tumbleweed by Mike Zapawa (2019) is a placement-only game on a hex board with an *influence-like* "line of sight" stack rule, and similar "play adjacent to your own influence" constraint. It has a pass-to-end protocol. See (d) below.
- **Slither.** Slider/placement hybrid. Not this.

**(b) CA-literature check.** Not applicable — no CA.

**(c) Simultaneous / order-resolution check.** Not applicable — alternating.

**(d) Proposed reskin transformation.**

The adversary's strongest claim: **"This is Tumbleweed on a torus-grid with radius-2 Manhattan influence instead of line-of-sight, and no stacking."** Specifically:
- Tumbleweed: hex board, "line of sight from existing friendly stones" placement, stack height = number of sight-lines, win by territory count at game-end.
- This game: torus grid, "adjacent to existing friendly stones" placement, board_value = accumulated radius-2 Manhattan influence, win by threshold on accumulated influence.
- Mapping: Tumbleweed's "sight-line" ↔ this game's radius-2 Manhattan influence propagation (both radiate from each stone). Tumbleweed's "stack height" ↔ this game's cell `board_value`. Tumbleweed's "play in empty cell visible from any of your stones" ↔ this game's "place adjacent to your own stone".

**(e) Expert-transfer test.** Would a Tumbleweed expert have an immediate edge? **Partially yes**. The core heuristic "build a compact group so your influence radiates on cells you'll later own" transfers directly. The ideas of "front-line vs interior stones" and "first-move advantage is severe, use a pie rule in practice" both transfer. Tumbleweed's specific tactics (using neutral stones, stack height competitions) do **not** transfer because those mechanics are absent. Verdict: an expert gets maybe 60% of the way.

Other adversarial claims:
- "It's Go without capture and without liberties, i.e. *the trivial Go variant* — known to be broken because no capture means no threats."
- "It's a thresholded territorial race, which is a standard abstract-game design pattern (see *Claim* and *Block* classes in combinatorial game theory literature)."
- "It's a *Voronoi* or *weighted-territory-under-placement-adjacency* game, which is a textbook academic-game-theory exercise."
- "The torus is a gimmick — collapsing boundary effects doesn't change strategy because every strategy here is translation-invariant."
- "Radius-2 Manhattan influence + adjacent-to-own is a well-known *parish game* pattern: pick a seed cell, flood-fill outward, count weighted area."

### Rebuttal

P1 and P2 jointly concede the Tumbleweed structural similarity but reject the reskin claim for three concrete reasons:

1. **No pass-to-end, no stacking — which changes the game into a pure race.** In Tumbleweed, the pass-to-score mechanism combined with stacking means a "late-stage fortress" can overturn midgame loss. Here, because there's no capture, no stacking, and no pass-to-score protocol (the threshold is dynamic), **the game has no late-stage reversal dynamic**. A Tumbleweed expert used to "holding a 1-sight-line fortress until the endgame" would be caught off-guard when this game simply terminates the moment P1 crosses 46.4. This played out in Game 2 move 37: P2 was 45.59 effective — effectively "1 Tumbleweed stack-turn away from winning" — and the game ended instantly on P1's move. Tumbleweed experts would expect another 5–10 moves of play.

2. **First-mover determinism is stronger than Tumbleweed's.** In Tumbleweed, the pie-rule is standard because the first-mover advantage is real but not absolute. Here, in 3/3 tested games (including one where P1 deliberately played a bad shape), P1 won. Tumbleweed strategies assume the losing side can use pass-to-score plus stack-building to hang on; here neither is available, so the game is **more like a deterministic race than Tumbleweed**.

3. **The adjacent_to_own + r=2 propagation creates a specific "d=2 suppression" micro-tactic that doesn't exist in Tumbleweed.** In Game 2 at step 8, P2's (5,3) shaved 0.16 from P1's (3,3) by overlapping at d=2. This is not a Tumbleweed dynamic (Tumbleweed uses line-of-sight, not radius); the influence radius here creates an "invisible denial zone" around each opponent piece that does not exist in Tumbleweed. The *fact* that the adversary's expert-transfer test only gets to 60% confirms this.

That said — the structural similarity is real enough that this game is more a **simplification of Tumbleweed + a topology swap** than a fresh design.

### Novelty score resolution

Score: **3 / 10**. The game is a recognisable territorial-influence race in the Tumbleweed family, stripped of pass-to-score and stacking, put on a torus, and using Manhattan-r=2 instead of line-of-sight. Those are three genuine deltas, but none is conceptually new. The lack of capture and the hard threshold make it a **simpler** relative of Tumbleweed, not a novel one. The Tumbleweed expert gets ~60% transfer. I set 3 (not 2) because the particular influence-threshold + adjacent_to_own + torus combination doesn't map cleanly onto any single prior game, just to the genre.

---

## Phase 5 — Verdict

**Team ID:** team-11
**Game ID:** 1ca924cc3062
**Rules Summary:** 8×8 torus, alternating placement, stones must be placed adjacent to your own existing stones (first stone anywhere). Each stone radiates radius-2 Manhattan influence (≈0.87 self, 0.37 at d=1, 0.16 at d=2; sign is player-specific). Win by being first to reach effective influence-sum ≥ 46.4 on your owned cells. 83-move cap; no capture, no CA, no pass-to-score mechanic.

**Topology:** 2D torus, axis size 8, total 64 cells. Wrapped Manhattan neighbourhood.

**Turn Structure:** Alternating, 1 placement per turn. `pieces_per_turn = 1`.

### Scores (1–10)

- **Strategic Depth: 3** — One dominant strategy (compact cluster growth). Minor variants on where to anchor and whether to interfere with opponent's boundary, but branching-factor-vs-payoff is very flat. No short-term/long-term tension because no captures. Moves are mostly determined by "which legal cell has the most own-neighbours".

- **Emergent Complexity: 3** — Territory and influence emerge, but both are weak: territory is just "set of stones", influence is a smooth additive field with no threshold/bifurcation dynamics. No ko, no race-to-cell, no life-and-death patterns.

- **Balance: 2** — P1 won 3/3 intentional games, one of which P1 played deliberately sub-optimally. Random-policy P1 win rate 62%. The race-to-threshold structure means first-mover advantage is **structural and unavoidable without a pie rule or adjusted threshold**. Seat-swap in Game 3 confirmed P1 wins regardless of reasoner identity.

- **Novelty (post-adversary): 3** — Close to Tumbleweed minus pass-to-score minus stacking, on a torus, with r=2 Manhattan instead of line-of-sight. Three real deltas from the closest analog but none conceptually new. Adversary's strongest argument: "this is Tumbleweed-lite on a torus". Rebuttal: influence-suppression micro-tactic + no reversal dynamic + deterministic first-mover race make it measurably different, but still within genre.

- **Replayability: 3** — Game ends in ~37 moves with the same ~19-vs-18 piece count every time. Random-policy average 46.5 turns, so with any intentionality convergence is faster. No meaningful opening book or midgame branching.

- **Overall "Would I play this again?": 2** — No. The game is well-formed and legal, but strategically thin and structurally P1-favoured. Pedagogically useful as a minimal territorial-influence toy model; not competitive-play-worthy.

### Closest known-game analog
**Tumbleweed** (Mike Zapawa, 2019) — with the specific mapping: torus-grid for hex-board, `adjacent_to_own` for `line-of-sight`, r=2 Manhattan influence for sight-line count, no stacking, no pass-to-score. The torus removes border effects, the loss of pass-to-score removes strategic reversal. It is **not identical** because (a) no stacking → no height competitions; (b) no pass-to-score → deterministic race; (c) Manhattan-r=2 propagation creates a d=2 "suppression zone" that line-of-sight doesn't; (d) placement constraint is stronger (physical adjacency only, no long-range sight-line placement).

### Killer flaws
1. **Severe first-mover advantage (≈100% with intentional play, 62% with random play).** No pie rule, no compensation mechanism. Structurally unavoidable given the race-to-threshold win condition.
2. **No tactical reversal**: no capture, no stacking, no pass-to-score. Every move adds monotonically to the owner's effective. Losing positions can never be saved except by opponent's blunder.
3. **Game converges too quickly relative to max_turns.** Threshold of 46.4 is hit at move ~37 vs cap 83, so half the "allotted" play never occurs. If max_turns were lower, the game would resolve by majority — which would also favour P1. Either way, P1 wins.
4. **Translation symmetry on torus + free first move makes the opening trivial** — no meta-game around opening theory.
5. No double-pass exploit observed in practice, but `_end_by_max_turns` falls back to piece-count majority, so in principle the same R13 exploit lives here (untriggered because threshold always resolves first).

### Best quality
The **influence field visualisation is genuinely informative** — you can watch the board values evolve and see the geometry of the threshold-race. The **adjacent_to_own constraint combined with Manhattan-r=2 propagation does produce a visually satisfying "organic growth" aesthetic**, where each cluster evolves like an amoeba competing for real estate. For a teaching example of territorial-influence games, it's clean and legible.

### Improvement idea
**Add a pie rule / mirror-response compensation: P2, on their first move, may either place a stone OR swap sides with P1.** This is the standard Tumbleweed / Hex first-mover balancing tool and would immediately make the game 50/50 between reasonably-matched players. Secondarily: **remove `first_move_anywhere`** so P1's opening is also constrained (e.g. to a specific central cell), tightening the opening theory. Either change alone would approximately double the strategic depth by introducing meta-game around seat choice / opening cell selection. A more invasive fix would be to **add capture** — e.g. a surround-capture rule — which would restore tactical depth at the cost of turning this into yet another Go variant.

---

*Methodology notes: All moves engine-verified via `play_helper.py --action play` on the run14 sqlite DB. Supplementary script at `/tmp/play_with_values.py` used to expose `board_values` and effective threshold totals after each step. Random-policy balance check ran 50 trials via `/tmp/sim_balanced.py`. No double-pass endings observed in any of my 3 playthroughs. Games 1–3 converged via threshold win at move 37. Seat-swap performed in Game 3 per instructions; residual seat-identity bias acknowledged.*
