# Evaluation — Game 531634cee158 — Team 6

**Run:** Run 13, Rank 3 (GE 0.482)
**Archetype:** 2D hex, outnumber capture, territory win, CLASSIC
**Seat-swap bias:** Player 1 and Player 2 were handled as sequential passes by one evaluator; seat-swap in Game 3 partially mitigated seat-identity bias but not reasoning-carryover bias.

---

## Phase 1 — Rule Comprehension

**Board:** 8×8 hexagonal grid in offset coordinates (64 cells). Each interior cell has 6 neighbors; corners have 2, edges have 3–4.

**Turn structure:** Alternating; 1 piece per turn. Actions are `place` on empty cells (0–63) plus `pass` (64).

**Placement:**
- Target: empty cells
- Constraint: `adjacent_to_own` — every placement after move 1 must be adjacent to a piece the placing player already owns.
- First move: anywhere (the very first placement by each player is free).

**Capture:** `outnumber`, threshold 3. After placement of cell `C`, each enemy cell `E` adjacent to `C` is removed if ≥3 of `E`'s 6 hex neighbors are friendly (to the placer). Capture triggers only on enemies of the *newly placed* cell, and only against cells directly adjacent to `C`. No group logic, no liberties.

**Propagation:** `none` (the strength/decay fields are vestigial).

**Win condition:** `territory`, threshold ≈ 0.5475 (~35.04 cells). First player to own **>35** cells (i.e. ≥36) wins instantly. If both players pass consecutively or 100 turns elapse, winner is whoever has more pieces; tie = draw.

**Degenerate-rule flags:** None found. No P1 auto-win, no 5-move forced kill, no inert capture (capture fires regularly at threshold-3 on hex, as observed in Phase 2). The combination is coherent and playable.

---

## Phase 2 — Strategic Play (3 games, engine-verified)

### Game 1 — P1 plays center

Openings: P1 (3,3) = 27, P2 (4,3) = 28.

Key moments:
- Move 5: P1 at (5,2) captured P2's (4,3) — first demonstration that outnumber-3 fires reliably when three friendlies surround an isolated enemy.
- Move 9: P1 at (4,3) captured P2's (4,4) — P2's attempt to salvage tempo by building a southward cluster left (4,4) exposed to a 3-of-6 squeeze.
- Moves 10–48: P1 and P2 each expanded into disjoint halves (P1 top, P2 bottom). Row 4 became the frozen border.
- Move 69: After double pass, game ended. **Final: P1 = 31, P2 = 28. P1 wins by majority.**

### Game 2 — P1 plays corner

Openings: P1 (0,0) = 0, P2 (3,3) = 27.

Key moments:
- Corner opening for P1 gave only 2 legal expansion cells ((1,0) and (0,1)), confirming that hex corners are strictly inferior openings due to 2-neighbor isolation.
- Despite the bad opening, P1 rode the top edge systematically, grabbing all of rows 0–1 (16 cells) before contact.
- Move 41: P1 played (3,2) = 19, triggering capture of P2's (4,2) — P2's push into row 2 created a piece with 3 P1 neighbors.
- **Final: P1 = 25, P2 = 20. P1 wins by double-pass majority.**

### Game 3 — Seats swapped (P1 plays what was P2's archetype)

Openings: P1 (4,4) = 36, P2 (3,3) = 27.

Key moments:
- Symmetric opening — (4,4) and (3,3) are hex-adjacent. Both sides built opposite-corner diagonals.
- P1 took the bottom half (rows 5–7) and pushed into row 4.
- P2 took the top half (rows 0–1) and pushed into row 2.
- Row 3 was the contested border. Several captures happened here in both directions.
- **Final: P1 = 32, P2 = 24. P1 wins by double-pass majority.**

### Reflections

**P1 strategy guide:**
1. Open at or near the 4×4 center — (3,3) or (4,4) — for 6 starting neighbors.
2. Expand in a rough half-plane to maximize cluster size.
3. Watch for opportunities to place a stone adjacent to an enemy piece that already has 2 of your pieces in its neighbor set — a third friendly neighbor kills it.
4. Don't over-commit to captures: each capture trades one move for one enemy stone, but may expose your capturer to counter-outnumber.
5. When both players settle into halves, pass early once the border is stable (double-pass ends the game favorably if you're ahead).

**P2 strategy guide:**
1. Given P1 took center, mirror on the opposite corner (e.g., (4,4)) — **do not** play a contested adjacency on move 2, because tempo favors P1 in outnumber exchanges (P1 gets to set up the third-neighbor move first).
2. Avoid building salients into P1's cluster — any piece with 2 of 6 hex neighbors already P1 is a capture-in-one-move.
3. Race for piece count: you can tie 32–32 or lose 32–28; push for perimeter control on one side of the board.

**Surprises:**
- The adjacent_to_own constraint locks each player into a growing "blob" — you cannot tenuki (play elsewhere) as in Go. This eliminates fuseki-style far-corner play.
- Threshold-3 captures on hex occur more often than I expected. In all 3 games, 2–5 captures happened per side.
- Corner openings are strictly dominated. The engine-enforced isolation penalty is severe.

---

## Phase 3 — Strategic Analysis (Joint)

**Distinct viable strategies?** Yes, two macro-strategies emerged:
- **Dense-cluster strategy:** hold one connected blob, play safe border moves, race for 36 pieces or double-pass majority.
- **Perimeter-first strategy:** push along an edge row to claim a row-strip quickly (game 2 showed P1 took 16 top-row cells before real contact).
Both are competitive. Corner openings are not viable.

**Counter-play?** Moderately. You can respond to an enemy attack by either (a) abandoning the threatened piece and gaining tempo elsewhere, or (b) extending your cluster to deny the attacker the third-neighbor cell. There's no true "life/death" tactical reading (because no groups), but there are meaningful local decisions.

**Short-term vs long-term tension?** Mild. Captures are worth +2 in piece-count swing (gain 0 for yourself, −1 for enemy, plus freed cell that enemy can't immediately reclaim because adjacent_to_own constrains them away from the hole). But most of the game is quiet territorial expansion.

**Emergent concepts observed:**
- **Territory** (central win condition)
- **Tempo / initiative** (first to fill the border gets the last capture)
- **Border pressure** (row 3/4 becomes a contested strip)
- **Isolation penalty** (corners / edges hurt early)
- No ko-fights, no eye-making, no groups.

**Does topology matter?** Yes — hex offset coordinates create subtly different neighbor sets for even vs. odd rows, and the 6-neighbor connectivity is what makes threshold-3 capture interesting (3 out of 6 = exactly half). On a square grid (4 neighbors), threshold-3 would require 75% coverage, which is much harder, and would change the game's character fundamentally.

---

## Phase 4 — Novelty Adversary

### Adversary's strongest arguments

1. **"This is Atari Go on a hex grid with threshold-3 outnumber instead of zero-liberties."** Both games feature placement + territory scoring + piece removal. The substitution "liberties = 0" → "friendly neighbors ≥ 3" is a local-counting re-parameterization of the same "I surround you, you die" idea.

2. **"This is a reskin of Hex with added capture."** The adjacent_to_own placement constraint is the defining rule of *connection-building* games like Hex/Y/Havannah. Add a capture mechanic and you get a common "capturing-Hex" variant proposed in abstract-strategy literature.

3. **"This is Reversi/Othello on hex, with capture rule = majority-of-neighbors instead of bracketed lines."** Both involve placing single stones and flipping/removing enemies based on geometric patterns.

4. **Expert test:** A strong Go player would find ~60% of their intuitions (thickness, border pressure, tempo) transfer, while a Hex player would find the adjacency-building placement familiar. Neither would be starting from zero.

### Rebuttal (citing Phase 2 moments)

1. **adjacent_to_own kills Go tactics.** In Game 2 when P1 opened (0,0), legal cells for move 3 were only (1,0) and (0,1). A Go player would never face this — in Go you can play anywhere. The placement tree is fundamentally different: it's a *growing-tree* game, not a *point-anywhere* game.

2. **No groups → no Go.** In Game 1, P2's (4,3) died alone on move 5 as an individual cell. Go's central mechanic — a stone lives or dies as part of a group — is absent. You cannot save a stone by keeping its chain alive. *Seki*, *ko*, *eye-making*, and *sacrifice-for-group* are all inapplicable. An Atari-Go expert's main reading skill (counting liberties of their group) is useless here.

3. **Not Hex.** Hex has no capture at all, and the win condition is connection (corner-to-corner), not piece-count. In our playthroughs, the game never rewarded connection — Game 1's P2 had a connected cluster of 28 stones and still lost on piece count.

4. **Not Reversi.** Reversi captures require a *bracketed line* of enemies between two friendlies. Here a single enemy dies based on local neighbor majority, with no line-bracketing. Game 1's capture of (4,4) involved 3 *non-collinear* P1 neighbors ((3,3), (3,4), (4,3)) — impossible in Reversi logic.

5. **Chain-capture-via-placement is novel.** In Game 1 move 9, P1's single placement at (4,3) directly captured (4,4). A subsequent placement could have triggered another capture because the first capture opened geometry. Neither Go (group-liberty-based) nor Reversi (line-based) exhibits this *single-cell cascading-majority* dynamic. The closest analog is a cellular automaton, but here the "rule" is gated by player agency — a hybrid of CA and placement.

### Novelty verdict

**Novelty score: 4/10.** The game sits squarely inside the abstract-strategy-on-a-grid family. It is *not* a radical genre innovation: the Go/Hex/Reversi shadow is visible, and an abstract-games expert would navigate it without deep confusion. However, the specific combination (hex + adjacent_to_own + outnumber≥3 + territory) yields a distinct tactical signature (no groups, individual-stone life/death, 3-of-6 majority capture) that doesn't reduce to any single cataloged game. Closest analog is "Atari Go on hex with majority capture," which isn't a real published game.

A "this is X on hex" score would be 2–3; a "radically new genre" score would be 7+. This game lands at 4 — a well-formed but recognizably derivative member of a known family, with one distinctive mechanic (outnumber-3 on hex) that isn't quite cataloged elsewhere.

---

## Phase 5 — Verdict

**Team ID:** team-6
**Game ID:** 531634cee158
**Rules Summary:** 2D 8×8 hex, 1 stone per turn placed adjacent to own, outnumber capture (enemy removed if ≥3 of 6 hex-neighbors are friendly after placement), first to own >54.75% of cells (36) or piece-majority at double-pass wins.
**Topology:** 2D hex (offset coords), 8×8 = 64 cells, 6 neighbors per interior cell.

### SCORES (1–10)

- **Strategic Depth: 5** — Meaningful choices about cluster shape, border pressure, and capture timing. But no groups mean no life/death reading, and the game often reduces to "claim your half, hope to capture one enemy stone." Trained-vs-random 0.84 and ELO 2972 confirm agents can learn nontrivial play; engine reports "strategic_depth: 0.76" (which is high for Run 13).
- **Emergent Complexity: 5** — Territory and tempo emerge cleanly. Chain-capture-via-placement is a minor emergent property. No ko fights, no eye-making, no sacrifice tactics. Non-triviality 0.82 in training metrics is credible.
- **Balance: 6** — P1 won all 3 of my games, but Game 2 (P1 from corner) was surprisingly close (25–20), and Game 3 with seat-swap showed the archetype still favors whoever opens at a central cell. Training achieved 0.50 balanced self-play winrate over 590k steps, so RL-equilibrium is balanced; human-level play may tilt to P1 due to tempo. Territory threshold 54.75% is slightly above 50% which helps prevent cheap P1 wins via draw-like double-pass ties.
- **Novelty (post-adversary): 4** — Lives inside the Go/Hex/Reversi family. Closest cataloged analog is "Atari Go on hex with threshold-3 outnumber capture," which isn't a known game. The hybrid of adjacent_to_own placement + single-stone outnumber capture is not identical to any one catalog game, but any two of its ingredients are well-known.
- **Replayability: 5** — Opening choice (center vs. offset-center vs. corner) changes strategic shape somewhat. But without deeper tactics (ko, life/death) the game's surface area is bounded. After 10–20 playthroughs, experts would likely converge on center-opening + perimeter-racing.
- **Overall "Would I play this again?": 5** — Pleasant once or twice, would teach a student as a warm-up for Go concepts, but wouldn't displace any established game from my table.

### CLOSEST KNOWN-GAME ANALOG

**"Atari Go on a hex board with majority-capture."** Not identical because (a) Atari Go uses group liberties, this uses single-stone majority; (b) Atari Go allows placement anywhere, this requires adjacent_to_own; (c) hex adjacency and 3-of-6 threshold produces different tactics than 3-of-4 on square.

A secondary analog: **"Hex with outnumber capture and territory win"** — a proposed-but-unpublished variant of Hex. Our game differs in win condition (territory, not connection).

### KILLER FLAWS

None outright fatal. Minor issues:
- Corner openings are strictly dominated — a small design asymmetry.
- Double-pass endings are common (observed in all 3 games), meaning the territory threshold (36) is rarely hit organically; the game effectively ends by piece-majority in practice.
- The propagation rule has nonzero strength/decay but `prop_type=none` — vestigial parameters bloat the rule representation without effect.

### BEST QUALITY

**The outnumber-3 capture on hex creates a tactically live but uncluttered border.** Unlike Go's eye-making complexity, this game has a single local question ("can I get 3 of 6 neighbors on that cell?") that repeats across the map. Coupled with adjacent_to_own placement, every move is committed and consequential. The 6-neighbor hex + exactly-half-threshold (3/6) is a clean design point.

### IMPROVEMENT IDEAS

**Add a 2-stones-per-turn rule with the second placement optionally non-adjacent.** This would:
- Break the pure cluster-growth dynamic by letting players establish satellite groups;
- Introduce a tactical tempo dimension (use second stone for defense or for a capture-setup);
- Recover some of the "two eyes" / sacrifice dynamics Go has but this game lacks.

Alternatively: **raise threshold to 4** — this makes captures rarer but more decisive, and forces players into deeper cluster planning.

---

## Final Verdict

Game 531634cee158 is a **competent, well-balanced abstract strategy game** with moderate strategic depth and modest novelty. It belongs to the Go/Hex family but has a distinct tactical signature (no groups, 3-of-6 single-stone majority capture). It scores well on engine metrics (Go Essence 0.48, ELO 2972) and plays cleanly — all 3 test games finished with decisive winners and no degeneracies.

**Final scores:** Depth 5 / Emergence 5 / Balance 6 / Novelty 4 / Replayability 5 / Overall 5.
