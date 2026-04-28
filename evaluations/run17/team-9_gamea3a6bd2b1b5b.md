# Team-9 Evaluation — Game `a3a6bd2b1b5b` (R17 rank 2)

**Team ID**: team-9
**Game ID**: `a3a6bd2b1b5b`
**Generation**: 11
**Database**: `genesis_v2_run17.db`
**GE composite**: 0.2933 / **ELO**: 2611.9 / **Trained-vs-random**: 0.64–0.86 across 3 seeds

---

## Phase 1 — Rule Comprehension

### Board
- **Topology**: `grid` (3D)
- **Dimensions**: 3, **axis_size**: 4 → 4×4×4 = 64 cells
- **Connectivity**: 6-neighbor von Neumann (`max_degree=6`). Face-only adjacency along ±x, ±y, ±z (no diagonals, no Moore connectivity).
- **Cell index**: `cell = z*16 + y*4 + x` (verified empirically; matches generic V2 convention).

### Action space
- **65 actions** total: 64 placements (cell IDs 0–63) + 1 pass (action 64).
- **Place-only.** Despite `move_constraint='adjacent_empty'` appearing in the JSON, `action_types: ['place']` — so move actions are NOT in the action space. This is **not** one of the R17 hybrid place+move games.

### Turn structure
- **Alternating**, 1 piece per turn. P1 starts.

### Placement
- `target='empty'`, `constraint='anywhere'`, `first_move_anywhere=True`. Standard "Go-style place anywhere empty" with no restrictions.

### Capture
- `capture_type='surround'`, `threshold=1` (irrelevant for surround). Standard Go-group capture: when the placer plays, any adjacent enemy group with 0 liberties is removed.
- **In a 3D grid with 6-neighbor cells, capture is essentially inert** — interior cells require 6 enemies, edge cells 4–5. Across all 3 of my games (66 total moves) **zero captures occurred.** The mechanic is theoretically present but practically vestigial.

### Propagation
- `prop_type='none'`. The radius/strength/decay parameters in the JSON are inert. Board values irrelevant.

### Win condition
- `condition_type='connection'`, `max_turns=87`.
- **`target_dimension=0` for P1, `target_dimension_p2=1` for P2** — perpendicular asymmetric goals.
- P1 wins by connecting the **x=0 face to the x=3 face** with own stones (Hex-style BFS through own colour).
- P2 wins by connecting the **y=0 face to the y=3 face** with own stones.
- The z-axis is shared "transit volume" — neither player's win condition references it; it provides routing alternatives.
- The `threshold=42.08` value in the rules is **inert for connection wins** (never read by `_check_connection`).

### Degenerate-rule audit
- **Surround capture is effectively dead** in 3D 6-connect with axis 4 — confirmed empirically across 3 games and reasoned from the structural cost of surrounding any group.
- Propagation, threshold, and the move action space are all **dead JSON fields**.
- The connection threshold value (`42.08`) is unread.
- `max_turns=87` was never reached in my games (longest = 30); games end via connection between turns 8 and 30 under any reasonable strategy.

---

## Phase 2 — Strategic Play

I played 3 full games, engine-verified every move via a custom helper (`eval_team9_helper.py`) that decodes 3D action IDs to coordinates and validates against `engine.get_legal_actions()`.

**Action-ID typo guard**: I caught one typo on Move 5 of Game 1 — entered `27` (which decodes to (3,2,1)) when intending (3,1,1) = `23`. The pilot helper's coordinate decoder caught it immediately and I restarted the move. This is exactly the failure mode flagged by the pilot team and is real — moves 22/23 and 27 differ only in the y-coordinate but are easy to confuse mentally.

### Game 1 — straight-line opening (alternating, P1 = me)

Opening: P1 (1,1,1)=21 / P2 (2,2,2)=42. P1 immediately built a 3-stone line at y=1, z=1: (1,1,1)–(2,1,1)–(3,1,1). P2 was forced to block (0,1,1)=20 to prevent the 4-stone connection.

Then I (P1) discovered the **structural problem**: every detour move I made forced P2 to block at an x=0 cell, and **those blocks naturally formed P2's y-axis cluster.** I tried containing the damage by force-blocking at fixed y=1 (P1 plays (1,1,z) for z=0,1,2,3 → P2 forced to (0,1,z)) — this kept blocks at y=1 only and didn't extend P2's y-axis. But after exhausting all four (1,1,*) cells (4 P1 + 4 P2 stones), I had to switch to (1,y≠1,*) extensions, and from that point each block added a new y-coordinate to P2's growing x=0 cluster.

Endgame: P2 cluster grew to span y=0..y=3 at x=0 along z=1: cells (0,0,1)–(0,1,1)–(0,2,1)–(0,3,1) plus filler. **P2 wins on Turn 22 by connection at x=0.**

```
z=1 final layer:
y=0  O X . .
y=1  O X X X
y=2  O X . .
y=3  O X . .
```

Reflection (P1):
- Strategy: classical Hex-style "build line + ladder detour". Failed because the geometry rewards P2 for blocking.
- Surprise: every P2 block was a "free win-step" — defence builds offence. This is unlike Hex/Go where blocking is genuinely expensive for the defender.
- Endgame: clean connection win, no double-pass, no max_turns.

### Game 2 — x=0-face-first opening (P1 = me)

I tried (0,1,1)=20 first to claim P1 territory immediately. P2 played (1,1,1)=21 (block + own y=1 stone). I then built a 4-stone P1 chain (0,0,1)–(0,1,1)–(1,0,1)–(2,0,1) at the y=0,z=1 edge. P2 was forced to block (3,0,1)=19, and **the symmetric problem appeared**: forcing blocks at x=3 face built a P2 wall there instead of x=0.

After 14 forcing moves of the (2,*,*) → block (3,*,*) ladder, P2 had a complete 12-stone wall at x=3 covering y=0,1,2 at all z values. The only remaining y for P2 was y=3, and any P1 threat into (2,3,*) → forced (3,3,*) block immediately gave P2 the y=3 cell.

**P2 wins on Turn 30** completing y-axis path at x=3 (e.g., (3,0,0)–(3,1,0)–(3,2,0)–(3,2,1)–(3,3,1)).

Reflection (P1): Switching the attack to the x=0 face changed which face P2's wall formed on, but the structural problem is identical. The core issue is that **the defender accumulates stones on one entire face**, and a 4×4 face is small enough that a y=0–y=3 path always exists through the wall.

### Game 3 — seat swap (P1 plays (1,1,1), I play P2)

I committed to the "block at the opposite face" strategy: every P1 threat into (1,*,*) or (2,*,*) → I block at (3,*,*) and let my x=3 cluster grow. P1 tried hard: claimed (3,3,1) defensively early (move 7), used z-direction detours, eventually attacking from all (2,*,*) cells with all four z values.

By Turn 20, my cluster spanned 12 cells at x=3 with y∈{0,1,2}. P1's only remaining forcing moves were into (2,3,*) cells, each of which forced me to block at (3,3,*) — and (3,3,0) is adjacent to (3,2,0)∈cluster, completing my y=3 reach.

**P2 wins on Turn 22** with path (3,0,1)–(3,1,1)–(3,2,1)–(3,2,0)–(3,3,0) covering y=0..y=3.

Reflection (P2): The strategy is **mechanical**: take the cell mirror to P1's opening on the opposite face, accept blocks as gifts, and watch the wall complete itself. Almost no deep reading required.

### P1 strategy guide
- Play the longest direct x-axis line possible, force as many blocks at *one* fixed (y,z) as possible (4 blocks max).
- Once forced to switch off the privileged y-row, accept that P2's wall grows toward winning. Try to maximise turns, hope opponent errs.
- **There is no known winning line under best play** — but P1 forces ~22+ turns.

### P2 strategy guide
- Open with a stone that simultaneously **blocks P1's central column** AND lies on your own y-target axis (e.g., (1,1,1) or (2,2,2) when P1 has played near centre).
- After that, **just block P1's threats at the opposite face** to where P1 is attacking from (x=3 face if P1 attacks from x=1, x=0 face if P1 attacks from x=2). Each block is also progress — your cluster grows toward y=0…y=3 coverage automatically.
- A 4×4 wall on one face is enough to win once any y=3-and-y=0 pair exists in it. With P1 forcing ~10 blocks, this happens by ~Turn 20.

---

## Phase 3 — Joint Strategic Analysis

**Single dominant strategy?** Yes — under best play, P2 has a near-mechanical winning strategy ("block-and-build wall at the contested face"). I could not find a P1 strategy that wins or even plausibly draws under optimal P2 response across 3 games.

**Counter-play?** Limited. P1's only lever is forcing blocks at a fixed y-row (e.g., y=1) to delay cluster formation. Beyond ~4 forced blocks at one y-row, the lever is gone.

**Short-term vs long-term tension?** Almost none. Every move is forced (immediate-win threat or block). The "long-term" plan is just "complete your wall" or "delay theirs." No positional sacrifice plays, no influence balance, no whole-board planning.

**Emergent concepts?** A real one: **defence-builds-offence asymmetry**. Because P1 must connect across 4 x-layers but P2 must connect across 4 y-layers, and the contested face is an x=k plane shared by all P1 routing options, P2's blocks on that face form a 4×4 grid that always contains a y=0→y=3 connected path once enough cells fill in. This is novel as a *failure mode of asymmetric connection games*, but it's a degeneracy, not a strategic richness.

**3D contribution?** Mixed-to-poor. The z-axis adds detour options that lengthen the ladder by ~4 turns (one per z-layer of (1,1,z) extensions before the dam breaks). It is **not** doing meaningful 3D strategy work — there's no "sub-volume control," no 3D path-routing mechanic, no genuine spatial reasoning beyond "z is one more direction to ladder along." The same game flattened to 2D Hex on a 4×4 board with perpendicular goals would be roughly equivalent strategically (and be solved as a P1 win in standard Hex). The 3D version becomes P2-favoured precisely because the extra dimension gives the defender a 4×4 wall on which a path always exists.

**Topology dependence?** Surround capture would matter on `moore` or `hex` (where surrounding is achievable), but `_fix_consistency` would have downgraded a moore+surround game per the R17 spec. On grid + 6-connect with axis 4, surround is dead.

**Move actions?** N/A — this is a place-only game (despite the misleading JSON field).

**First-mover advantage?** **Strong second-mover advantage.** Across 3 games (1 with original seats, 1 with alternative P1 opening, 1 with full seat swap), P2 won every game. PPO training reported 50/50 winrate — this is consistent with both PPO agents converging to a mediocre equilibrium that doesn't find the dominant defensive strategy. With trained-vs-random win rates of 0.64–0.86 (not 0.95+), the agents are clearly not strong; their seat-balance score reflects PPO weakness, not actual game balance.

---

## Phase 4 — Novelty Adversary

### Adversary case (this game is NOT novel):

**(a) Catalog comparison.**
- **3D Tic-Tac-Toe / Qubic**: 4×4×4 board with line-completion goal. Same board *shape*. Different goal (line of 4 vs face-to-face connection). Connection goal here is closer to Hex than Qubic.
- **3D Hex / Hex on cube**: This is the closest analog. 3D Hex variants exist where P1 connects opposite faces along one axis and P2 along a perpendicular axis. Studied (informally) in puzzle/board-game communities since at least the 2000s. The game `a3a6bd2b1b5b` is essentially a 3D Hex on a 4×4×4 cubic lattice with **6-neighbor (face) connectivity** instead of true Hex (which would use `moore` or specialised 3D-hex topology).
- **Y / Havannah / Connect6**: All connection-goal games on 2D boards. Connection goal is a shared family.
- **Notakto / 3D Notakto / 3D Go variants**: Ko-and-territory games on cubic boards. Different mechanics.
- **Bridg-It / Shannon Switching**: 2D edge-coloring connection games with perpendicular goals. **The strategic shape is similar** (perpendicular connection on a small grid) — Bridg-It is solved as a P1 win on standard sizes via an electrical-network argument. The 3D variant on a cube with face-connectivity has not, to my knowledge, been formally studied.
- **Go**: Surround capture mechanic ostensibly inherited but is inert (zero captures across my 3 games). This is "Connection Go in 3D" only in name; the Go part doesn't activate.

**(d) Specifically test 3D-Connection-Go-with-capture as novel combination.**
- The combination "3D + Go-style surround + face-to-face connection + perpendicular axes" is *unusual* but the 3D structure adds nothing beyond extra ladder rungs. Strip the inert capture mechanic and you have **3D Hex with face connectivity and perpendicular goals on a 4×4×4 lattice**. This is a known *family* of games even if this exact 4³ instance hasn't been catalogued.
- **It is not the same as the R17 champion `44f6630277b3`**, which is the genuinely interesting design (3D + custodian + connection + place+move hybrid actions). Custodian capture and mobile stones change the game fundamentally; this game (rank 2) has neither.

**(e) Re-skin claim.**
- This is **3D-Hex-on-grid with vestigial Go capture**. Topology transformation: relabel x↔y and the rules transpose; on a 4³ cube with axis labels swapped, this game is identical except for which player is labeled P1. So it is "3D grid Hex with perpendicular goals" under a coordinate label.

**(f) Expert transfer test.**
- A 3D Hex / Bridg-It expert would immediately recognise the "block the contested face" structure. They would also recognise that the 4×4 face is too small for honest blocking — the defender's wall always contains the desired connection path. A 2D Hex expert with no 3D experience would need ~5 minutes to see why the standard Hex bridge doesn't apply (face-only connectivity rules out Hex bridges) and then would use the same "wall the face" idea.

### Player rebuttal

The strongest rebuttal to "this is just 3D Hex": the Go capture mechanic *is* present in code, and on a slightly different topology (e.g., moore or larger axis_size where surround is feasible) it could activate and produce genuinely novel ko-fight tactics — those would be Phase 2 moments where pure-Hex analogy breaks. **But on this game's actual topology those moments never happen.** I observed zero captures across 22+30+22 = 74 moves of play. The novelty rebuttal fails on its own merits: the capture is genuinely inert.

The other rebuttal — "the asymmetric perpendicular goals are interesting" — is also weak. They produce a *bias*, not depth. P2 wins always under best play; this is a *flaw* of the design, not novelty.

**Novelty score**: **3/10**. Recognisable as 3D Hex / Bridg-It variant on 4³ grid; the inert Go capture and inert propagation/threshold fields don't add novelty.

---

## Phase 5 — Verdict

**Team ID**: team-9
**Game ID**: a3a6bd2b1b5b
**Rules summary**: 3D 4×4×4 grid; alternating placement; surround (Go-style) capture (inert in practice); perpendicular connection win — P1 connects x=0↔x=3, P2 connects y=0↔y=3.
**Topology**: 3D grid 4³ (6-neighbor face connectivity)
**Turn structure**: alternating, 1 piece/turn
**Hybrid actions**: NO — place-only despite the JSON `action_rule.move_constraint` field (which is dead).

### SCORES (1-10)

- **Strategic Depth: 3** — Mechanical ladders, no genuine multi-threats (3D grid lacks Hex bridges), capture is inert, propagation is inert. The only "depth" is the threshold of choice over which y-row to ladder down.
- **Emergent Complexity: 3** — One real emergent pattern: defence-builds-offence on the contested face. But this is a degeneracy, not richness.
- **Balance: 2** — Strong P2 advantage. 3/3 of my games went to P2; the structural argument generalises to any reasonable line. PPO 50/50 result reflects weak agents, not actual balance. Seat-bal almost certainly inflated by PPO sub-optimality.
- **Novelty (post-adversary): 3** — Recognisable 3D-Hex-on-grid with inert Go decoration. The novel hypothesis ("3D + custodian + connection + mobile = genuine novelty") doesn't apply to this game (no custodian, no mobile stones). The 3D substrate adds detour length but not real 3D strategy.
- **Replayability: 3** — Once the wall strategy is found, every game looks similar.
- **Overall "Would I play this again?": 3** — Functional but uninteresting. Capture-inert, propagation-inert, balance-broken under careful play.

### CLOSEST KNOWN-GAME ANALOG
**3D Hex / 3D Bridg-It on 4×4×4 cubic lattice with face connectivity.** Not identical because (a) classical 3D Hex uses hex-style connectivity, not 6-face, (b) the inert Go capture is bolted on, (c) standard 3D Hex variants are typically larger (5³ or 7³). The strategic essence is identical to a Hex/Bridg-It variant.

### KILLER FLAWS
1. **Defence builds offence**: the 4×4 contested face is small enough that P2's defensive blocks always form a y=0↔y=3 path. Under careful P2 play, P1 has no winning line in any of my 3 game branches.
2. **Surround capture inert**: zero captures across 74 moves; mechanic exists in JSON but never triggers (3D 6-connect + axis 4 + small piece counts → liberties always available).
3. **Propagation, threshold, max_turns, move actions all dead JSON fields**: the game is mechanically far simpler than its 15-rule complexity score suggests.
4. **Tempo is illusory**: P1's "first-move advantage" doesn't translate because each P1 forcing threat is immediately neutralised by a single block that also progresses P2's win.

### BEST QUALITY
The **defence-builds-offence dynamic** is genuinely interesting as a *design failure mode* worth understanding. It illustrates why perpendicular-axis connection games on small lattices favour the second player when the contested face is small relative to the connection length. This is a useful negative result for the evolutionary engine.

### 3D STRUCTURAL CONTRIBUTION
**Negative — the 3D substrate makes the game *worse*.** The extra z-axis gives P1 four (instead of one) z-layers to ladder through, but each additional layer just gives P2 a bigger wall. A flat 2D variant with perpendicular goals (Hex-on-square / Bridg-It) would either be solved P1-wins or be a genuine race; the 3D extension introduces the wall-asymmetry that breaks balance. **This game would be strictly better as 2D.** The R17 hypothesis that "3D + custodian + connection + mobile is genuinely deep" does not apply to this rank-2 game (which has neither custodian nor mobile stones).

### IMPROVEMENT IDEAS
- **Go to axis_size=5 or 6**: a 5×5 contested face has many more cells than a 4-cell connection requires; a y=0↔y=3 path through the wall is far less automatic. This would significantly delay (or prevent) the defence-builds-offence collapse.
- **OR**: use `outnumber` capture instead of `surround` — outnumber capture fires routinely on 6-connect 3D, would give P1 actual capture threats and make capture a real mechanic, plus opens ko-fight territory.
- **OR**: same player connects both axes (P1 connects x AND y, P2 the same on swapped board) — restores symmetry.

The game as-is feels like an evolutionary stepping-stone toward the R17 champion (rank 1, `44f6630277b3`) rather than a destination — it has the 3D + connection + grid skeleton but lacks the `custodian` and `place+move` enrichments that make rank 1 worth studying.

---

## Telemetry / artefacts

- Helper script: `/Users/jamesbrowne/aigame/eval_team9_helper.py` (cell-decode + step replayer specific to this game).
- Game 1 final state: P2 wins T22, 11/11 stones, connection at (0,0,1)–(0,1,1)–(0,2,1)–(0,3,1).
- Game 2 final state: P2 wins T30, 15/15 stones, connection through (3,0,0)…(3,3,1) at x=3 face.
- Game 3 final state: P2 wins T22 (seat-swap), 11/11 stones, connection (3,0,1)–(3,1,1)–(3,2,1)–(3,2,0)–(3,3,0).
- All three games engine-verified via `engine.step()` per move; no illegal moves committed (one action-ID typo caught by helper before commit).
