# Team-7 Evaluation — Game `a3a6bd2b1b5b` (R17 rank 2)

**Team ID:** team-7
**Game ID:** `a3a6bd2b1b5b`
**Generation:** 11 (parent `8f36d001577d` had GE=0.0008; the `win_condition` mutation rescued it)
**ELO:** 2611.9 — **GE:** 0.2933 — **Strategic Depth:** 0.4692 — **Strategic Diversity:** 0.6667
**Training (3 seeds):** vs-random 0.86 / 0.64 / 0.64; final p0-vs-p1 win rate 0.5 / 0.5 / 0.5; avg game length 43–50 moves.

---

## Phase 1 — Rule comprehension

**Board:** 3-D grid, axis_size 4 → **4×4×4 = 64 cells**, von Neumann (face-only) 6-connectivity. `topology_type: grid` (no wrap).

**Turn structure:** **alternating**, 1 piece/turn. Action 64 = pass; two consecutive passes draw.

**Action types:** **place only** (despite team-lead briefing — `action_rule.action_types = ["place"]`, `num_actions = 65 = 64 + pass`; no move actions in the action space). The `move_constraint: adjacent_empty` field is dead.

**Placement:** target=empty, anywhere; `first_move_anywhere=True`.

**Capture:** **surround** (Go-style group capture, threshold=1 — threshold field unused for surround). Adjacent enemy groups with 0 liberties are removed when a friendly stone is placed.

**Propagation:** **`prop_type: none`** — `radius/strength/decay` (1.4, 0.47…) are dead values.

**Win condition:** `condition_type: connection`, `target_dimension=0` for **P1 connects x-axis** (cells with x=0 connected via P1 stones to cells with x=3), `target_dimension_p2=1` for **P2 connects y-axis** (y=0 to y=3). Z is shared/free for both. **The `threshold: 42.08` field is dead code** — `_check_connection` uses BFS face-to-face, ignoring threshold. `max_turns=87`.

### Degeneracy flags raised in Phase 1

- **Threshold=42.08 is unreachable / unused.** Connection wins are binary in the engine; the value just sits in the rule struct.
- **Propagation rule fully inert** (`prop_type: none` overrides radius/strength/decay).
- **Capture threshold=1 is unused** for surround capture.
- **Minimum win is 4 stones** — a (y\*, z\*)-row of 4 cells along x is a connection. P1 has 16 candidate rows, P2 has 16 candidate columns. Games are short.

---

## Phase 2 — Strategic play (4 games via `play_helper`-style verification)

I built `eval_team7_helper.py` to engine-verify every move (cell index = `z·16 + y·4 + x`, action 64 = pass, no move IDs). All transcripts are reproducible from the move strings below.

### Game 1 — P1 dominant, z-detour win (15 moves, P1 wins)
Moves: `21,22,23,30,26,14,27,10,6,13,20,9,5,15,7`

- T1 P1 (1,1,1) — central anchor.
- T2 P2 (2,1,1) — blocks the natural x-row at y=z=1.
- T3-T5: P1 outposts (3,1,1) and (2,2,1); P2 builds y-column (2,3,1)/(2,3,0).
- T7 P1 (3,2,1) bridges (2,2,1)↔(3,1,1).
- T9 P1 (2,1,0) — z-axis detour around the (2,1,1) block.
- T11 P1 (0,1,1) claims x=0; T13 P1 (1,1,0) and T15 P1 (3,1,0) close the chain.
- **Winning path:** (0,1,1)–(1,1,1)–(1,1,0)–(2,1,0)–(3,1,0)–(3,1,1)–(3,2,1)–(2,2,1). The z-detour was the killer move. P2's chain `(1,2,0)-(1,3,0)-(2,3,0)-(2,3,1)-(2,2,0)` got walled off from y=0 with no route home.

### Game 2 — P2 walls x=0 face, P1 finds the y=0 corner (13 moves, P1 wins)
Moves: `21,37,22,41,23,20,5,4,1,0,16,24,17`

- P2 plays a tight blockade: 20, 4, 0 (whole x=0 face on z=0, z=1).
- P1 escapes via the y=0 plane: (1,0,0)–(0,0,1)–(1,0,1) bridges (1,1,1)/(2,1,1)/(3,1,1) chain to a x=0 cell at (0,0,1). P1 mega-group spans both faces.
- P2 never assembled a y-axis-spanning chain; (1,1,2)/(1,2,2) outposts remain disconnected.
- **Lesson:** even if P2 walls one corner of x=0, P1 has 16 face-cells and 5+ z-detour options.

### Game 3 — Seat-swap test, P2 commits 4-layer z-extension (19 moves, P1 wins)
Moves: `20,21,23,25,22,29,17,5,1,37,33,53,49,26,4,30,0,10,18`

P1 opens with a corner-ish (0,1,1) instead of center; P2 grabs (1,1,1) and tries hard to push a y-column through it. P1 walls **(1,0,_) at every z-layer** (1, 0, 1)/(1, 0, 0)/(1, 0, 2)/(1, 0, 3). P2 spends 4 moves on z-extensions (5→37→53), each blocked. P2 finally pivots to a second column at x=2, but by then P1 has enough material to bridge (2,0,1) and win via the y=0 plane.

**Seat-swap reading:** even with P1 playing the slower corner opening and P2 adopting the longest realistic z-chain attack, P1 wins. The asymmetry in this game appears tempo-driven (P1 moves first in a game where the minimum win is 4 stones).

### Game 4 — P1 over-extends, P2 wins (12 moves, **P2 wins** ✓)
Moves: `21,25,22,42,23,20,5,29,6,24,7,16`

I deliberately played P1 greedy (build over block):
- T7 P1 (1,1,0) and T9 P1 (2,1,0) and T11 P1 (3,1,0) — three consecutive stones extending P1's x-chain via z=0 detour, **without ever blocking P2's emerging x=0 column**.
- P2 builds (1,2,1)→(1,3,1)→(0,1,1)→(0,2,1)→(0,0,1). The chain (0,0,1)-(0,1,1)-(0,2,1)-(1,2,1)-(1,3,1) spans y=0 to y=3.
- **P2 wins T12.**

This proves P2 can win; the game is not strictly first-player-forced. But P1 must commit a non-trivial fraction of moves to defense.

### Player reflections

**P1 strategy guide.** Open central (cell 21 = (1,1,1)) for maximum branching. After the opponent's first block, claim x=3 outpost on T3, x=2 bridge on T5, then fight for the x=0 face with z-detour. Always keep one move per round on **defending P2's y=0 entries** — `(_, 0, _)` is the chokepoint; if P2 has a y-column at (x\*, _, z\*), block (x\*, 0, z\*). 4 cells along z lets P2 escape one block; you need to wall the y=0 plane in lockstep.

**P2 strategy guide.** Don't waste moves on far-z-layer outposts (z=2, z=3). Instead pick a column (x\*, _, z\*) and **co-build with P1's blocks** — every time P1 detours through z, the path that bypasses also opens new y-routes for you. The double-threat on x=0 (game 4) works because P2's column on the x=0 face acts as both an offensive and a counter-block.

**Endgame status:** all 4 games ended via the connection win condition. Zero double-pass draws, zero max_turns timeouts, **zero captures fired across all 4 games**.

---

## Phase 3 — Strategic analysis (joint)

- **Distinct viable strategies?** Two clear archetypes: (a) **central-row tempo race** (4-stone direct line + 1-z-detour to break the inevitable block); (b) **corner-route** (commit to a y=0 or y=3 plane and fight on x=0 face). Both work for either side. Some flexibility, not deep.
- **Counter-play:** present but constrained — block-OR-build is a binary choice every turn; once you fall behind in tempo, you can rarely recover by capture (because captures don't fire) or by detour (because z-axis depth is only 4 layers).
- **Short-term vs long-term tension:** mostly short-term. Games converge in 12–19 moves; "long-term" structure barely emerges before the connection closes.
- **Emergent concepts:** modest. **3D path-routing** is real (z-detour decided games 1 and 3). **Tempo / initiative** dominates. **Sub-volume control** rarely matters because the volume needed (4 stones in a path) is much smaller than the 64-cell volume. **Influence** absent (no propagation). **Ko fights** absent (no threat of recurring captures). **Mutual annihilation** absent (captures inert).
- **Does 3D add depth vs 2D?** *Partially.* The z-detour absolutely matters — in 4×4 Connection Go (2D), P2's central block at (2,1) terminates many P1 routes, whereas here P1 always has the z-axis to reroute around. **However, more than half of the cells (z=2, z=3 layers in particular) sit unused in most games.** A 4×4×2 substrate would likely play similarly. The substrate is not fully exploited; it's used as "two paths instead of one," not as a true 3-D strategic medium.
- **Topology choice:** grid (face-only). Hex or moore would change neighbour count and make connection trivially easier (more routes), so the design hangs on the 6-connectivity grid being just-tight-enough. But this is the same trade as in 2D Connection Go.
- **Move-enabled?** No. (Confirmed: place-only, despite team-lead briefing about hybrid action space.)
- **First-mover advantage:** **P1 won 3/3 adversarial games and lost 1/4 only when P1 played greedy/sub-optimally.** Training says final p0-vs-p1 winrate is 0.50 across all 3 seeds, so trained agents balance — but the seat-balance gate (R17's 0.1 floor) clearly didn't catch a residual P1 lean visible in human play. Quantitative: in my games, P1 advantage requires only ~50% defensive moves to convert; if P1 ignores defense, P2 can punish (game 4).

---

## Phase 4 — Novelty adversary (mandatory)

The Adversary argues `a3a6bd2b1b5b` is **not novel**:

- **(a) Closest analogues.** This is *Connection Go on a 4×4×4 face-grid with asymmetric P1/P2 connection axes*. The asymmetric perpendicular-axis connection is the **Hex** scheme. The capture mechanic is **Go**'s surround. R8's champion (`evaluation_report_run8.md`, the human-rated 8/10 game) was Connection Go in 2D — same recipe minus a dimension and minus the asymmetric axes assignment (R8 was on a 2D 8×8 hex board). 3-D Connection Go with face-grid and Go-capture is the obvious "lift R8 into 3D" play.
- **(b) 3-D variants.** *3D Hex* (Steele, 1990s; Beck-style 3D Y) exists. *3D Tic-Tac-Toe / Qubic* exists but uses majority/n-in-a-row, not connection. *3D Go* (Notakto-3D et al.) exists but uses elimination/territory, not perpendicular-axis connection. **No widely-published game I can name combines 3D-grid + face-connectivity + Go-style group capture + asymmetric perpendicular-axis Hex-connection.**
- **(c) Re-skin test.** Strip the (dead) capture and propagation rules, and the game is **3D Hex on a 4-cube with face-only adjacency**. The Go capture mechanic is the only thing that *could* differentiate it from 3D-Hex-on-cube — but in my 4 games, **zero captures fired**. Empirically this game IS 3D-Hex-on-cube during normal play.
- **(d) "Just X in disguise" — would an expert transfer immediately?** A 3D Hex player would transfer **fully and immediately**. Path-routing intuition (block their column, detour through z, prefer high-degree cells) carries over directly. The Go-capture novelty does not surface because games close before groups grow large enough to lose all liberties.

### P1 / P2 rebuttal

- The **asymmetric** axis assignment (P1 on x, P2 on y, z shared) is genuinely different from standard Hex where the two players' axes are dictated by hex-tile orientation. On a cube, the asymmetry creates an interesting "P2 places at x=k blocks P1's z-detour rows at z=k for x near k, and conversely P1 placing at y=k blocks P2's columns" cross-cutting structure. Expert 3D Hex players would still transfer, but the cross-block geometry is a bit different.
- The **Go capture mechanic** is dormant in 4-cube but would re-activate on 5-cube or larger axis_size where games last long enough for groups to develop. In 4-cube the connection is reached too fast to give capture room.
- **Phase-2 specifics that fail the analogy:** In game 4, P2's win path went through (0,1,1)-(0,2,1) — a **shared column** with what P1 had to block. The cross-axis interference doesn't exist on the same form in 3D Hex on rhombic-dodecahedral packing.

### Novelty score

**Novelty: 4/10.** It's "Connection Go in 3D with asymmetric Hex-style axes" — a genuine but incremental variation on R8 and on 3D Hex. The capture mechanism is functionally absent, so the design degenerates to 3D-Hex-on-cube during normal play. Not "X on a hex board" → 2-3, but also clearly not "no known analog" → 7+.

---

## Phase 5 — Verdict

**Team ID:** team-7
**Game ID:** `a3a6bd2b1b5b`
**Rules summary:** 4×4×4 face-grid, alternating place-only, Go-style surround capture, Hex-style asymmetric connection win (P1 connects x-faces, P2 connects y-faces, z is shared routing).
**Topology:** 3D grid, axis_size=4, von Neumann 6-conn.
**Turn structure:** alternating.
**Hybrid actions:** **no** — place-only; team-lead's note about ~1700 action-space hybrid does not apply to this game (`num_actions=65`).

### Scores (1–10)

| Dimension | Score | Reasoning |
|---|---|---|
| **Strategic Depth** | **4** | Central tempo race + z-detour is the dominant pattern. Games close in 12–19 moves, well below `max_turns=87`. Some branching from z-axis routing, but minimum 4-stone path makes commitment decisions binary. Capture mechanic doesn't fire in practice. |
| **Emergent Complexity** | **3** | 3-D path routing emerges; nothing else. Capture/influence/ko/territory all absent in actual play. Half the cells (z=2, z=3 layers) are typically unused. |
| **Balance** | **5** | Training reports 0.5/0.5 p0-vs-p1, and the R17 0.1 seat-balance floor passed. In human play I saw 3/3 P1-wins in adversarial play and 1/4 P2-win when P1 over-extended. Tempo lean to P1 but P2 has a winning response if P1 doesn't defend. Not broken, not great. |
| **Novelty** (post-adversary) | **4** | "Connection Go in 3D with asymmetric Hex axes." Genuine variation but well within R8's recipe + 3D Hex tradition; capture mechanic that *could* differentiate it sits inert. |
| **Replayability** | **4** | 16 candidate P1 rows × 16 candidate P2 columns = 256 macro-openings, but the central (1,1,1) opening dominates and games converge fast. After 5–10 plays the core race pattern is solved. |
| **Overall ("would I play this again?")** | **4** | I would play it once or twice for the 3-D-routing puzzle, then move on. |

### Closest known-game analogue
**3D Hex on a 4-cube with face-only adjacency**, played with asymmetric perpendicular axes for the two players. The Go-style capture would differentiate it on a larger board but is observationally inert here. R8's 2D Connection Go is the next-closest project-internal analogue.

### Killer flaws
- **Surround capture is functionally inert** in 4-cube: zero captures fired across 4 played games. The "Go" half of "Connection Go" is missing in practice.
- **Dead rule fields:** `propagation_rule` (`prop_type: none`), `win_condition.threshold=42.08` (connection ignores threshold), `capture_rule.threshold=1` (surround ignores threshold), `action_rule.move_constraint=adjacent_empty` (no move actions exist). 4 of the rule's own fields are vestigial.
- **Short games on a 4-cube:** minimum 4-stone winning chain → games end in 12–19 moves. `max_turns=87` is wildly above realistic game length.
- **Half the board unused:** z=2, z=3 layers contribute nothing in most games. The 3-D substrate is paying for cells it doesn't use.
- **Under-stressed seat balance:** training-time PPO reaches 0.5 winrate, but in human-style adversarial play P1 has a clear tempo lean that the 0.1 seat-balance floor does not visibly catch.

### Best quality
- **z-axis detour as a real strategic tool.** The single feature that makes this more than a 4×4 Connection Go is the ability to bypass a block by stepping out of the (y, z) plane and re-entering on a different layer. This was decisive in games 1 and 3.

### 3-D structural contribution
**Mixed.** z-detour matters (it's the difference between 2D 4×4 Connection Go being almost-solved and this game being playable). But:
- Only 1–2 z-layers are used per game in practice — a 4×4×2 substrate would likely play near-identically.
- The game is essentially **3D Hex on a face-cube**; the third dimension is a routing dimension, not a strategy dimension. It does not generate qualitatively new mechanics like sub-volume control, 3-D enclosure, or stack-based capture.
- The Go capture mechanic — which *could* leverage the higher cell-count of 3D — never engages because connection fires first.

So the answer to "could this be 2D without losing strategy" is *almost yes* — it would lose the z-detour move but would otherwise play similarly. The 3-D substrate adds real but limited depth.

### Improvement idea
**Raise axis_size to 5 or 6 and switch capture to custodian.** The 4-cube + 4-stone-minimum forces games to close before captures can ever matter. On a 5- or 6-cube, the minimum chain extends to 5–6 stones, capture groups have time to form, and the Go-half of "Connection Go" actually engages. Custodian capture (the R17 champion's choice) fires more reliably than surround on grid. The current configuration is a degenerate corner of the design space where the capture rule is inert.

---

## Confirmation against R17 hypothesis

R17's headline claim: "3D + custodian + connection + mobile stones is genuinely novel." This game is the **null-test**: 3D + **surround** + connection + **place-only**. My read:

- The 3-D structural contribution is real but partial (z-detour matters, but most cells are unused).
- The capture mechanic is inert — observationally this is 3D-Hex-on-cube.
- Novelty is incremental, not fundamental (4/10 post-adversary).

This game is a credible #2 within R17's 3-D-connection basin but does **not** independently corroborate the "3-D + Connection Go is genuinely deep" hypothesis. The genuinely interesting variant is the champion (`44f6630277b3`) which has *both* custodian capture (so the Go-half engages) *and* mobile stones (so the strategic state space is larger). On its own merits, `a3a6bd2b1b5b` is a 4/10 game.
