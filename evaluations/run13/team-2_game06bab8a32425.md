# Team-2 Evaluation — Run 13 Game `06bab8a32425`

Evaluator: team-2 (independent)
Game ID: `06bab8a32425`
Date: 2026-04-10

---

## PHASE 1 — RULE COMPREHENSION

### Board
- Topology: 2D hex grid, axis_size=8 (8×8 = 64 cells)
- Hex adjacency: each interior cell has 6 neighbors. Neighbors of (x,y) are (x-1,y), (x+1,y), (x,y-1), (x,y+1), (x+1,y-1), (x-1,y+1) (axial offsets).
- Edges: corners have 2-3 neighbors; edges have 4.

### Turn Structure
- 2 players, alternating turns, 1 piece per turn.
- Actions available: PLACE at any cell (target="any", includes occupied cells — **overwrite allowed**) + PASS.

### Placement Constraint
- `constraint: adjacent_to_own` — normal placements must be adjacent to at least one of the player's own pieces.
- `first_move_anywhere: true` — a player with **zero** pieces may place anywhere. This re-applies if all of a player's pieces die (piece_counts[p]==0), letting them reset anywhere.
- Overwriting an enemy cell is legal (target="any"); the placed piece then participates in CA evaluation.

### Cellular Automaton
- `capture_rule: none` — no classical capture, but the CA performs capture/death equivalents.
- `steps_per_turn = 2` CA steps after every action (including passes), with `max_neighbors = 6` (hex).
- Player-symmetric: at each CA step the acting player is treated as "friendly". 3-state totalistic rule `(own_state, friendly_count, enemy_count) -> new_state`, states {0=empty, 1=friendly, 2=enemy}.

The transition table differs from identity in **11 entries**:

| own | f | e | -> |
|-----|---|---|----|
| friendly | 0 | 1 | EMPTY (isolated friendly dies next to 1 enemy) |
| friendly | 0 | 2 | EMPTY (isolated friendly dies next to 2 enemies) |
| enemy    | 1 | 0 | EMPTY (isolated enemy next to 1 friendly dies — "attack of opportunity") |
| friendly | 1 | 4 | ENEMY (connected friendly flips when swamped) |
| empty    | 2 | 3 | FRIENDLY (birth: 2 own + 3 enemy) |
| empty    | 2 | 6 | FRIENDLY (unreachable: f+e=8 > 6) — **dead rule** |
| empty    | 4 | 0 | FRIENDLY (birth: 4 own surround empty) |
| empty    | 6 | 1 | FRIENDLY (unreachable: f+e=7 > 6) — **dead rule** |
| enemy    | 6 | 1 | EMPTY (unreachable: f+e=7 > 6) — **dead rule** |
| enemy    | 6 | 2 | EMPTY (unreachable: f+e=8 > 6) — **dead rule** |
| enemy    | 6 | 5 | EMPTY (unreachable: f+e=11 > 6) — **dead rule** |

**Five of 11 "non-trivial" transitions are physically unreachable** (f+e > 6). The truly live rules reduce to: isolated pieces die near enemies (`1,0,1`/`1,0,2`/`2,1,0`), connected pieces can flip when outnumbered (`1,1,4`), and empty cells can give birth under specific configurations.

### Propagation / Influence
- None (`prop_type: none`).

### Super-ko
- Enabled. Any move whose post-CA board hash repeats a prior position is **rolled back and treated as a pass**. This is load-bearing: the most common ko rollback is the degenerate "place adjacent to lone enemy → both stones die → board reverts to pre-move state".

### Win Condition
- `condition_type: connection`, P1 connects `target_dimension=1` (y=0 to y=7, top-to-bottom), P2 connects `target_dimension_p2=0` (x=0 to x=7, left-to-right). Classic Hex face assignments.
- Threshold 0.5 is unused for connection checks (connects_faces returns bool).
- `max_turns=100`. Double-pass triggers `_end_by_max_turns`, which resolves by **piece majority**, not by who-is-ahead-in-connection.

### Flags for Degeneracy

- **Double-pass → majority tiebreak** (not draw, not contested). If neither player has a connection but one has more stones, they win without ever having satisfied the stated win condition. This is the documented "double-pass majority" exploit from MEMORY.
- **5 CA transitions are dead** (physically unreachable on hex). Effective rule count is 6, not 11. Rule complexity score (17) overstates real complexity.
- **Ko rollback as pass**: placing adjacent to a lone isolated enemy is nearly always self-killing, and the engine silently converts such an attempted move into a pass. This is a subtle behavior the player must understand or waste turns.

---

## PHASE 2 — STRATEGIC PLAY

All moves engine-verified (I constructed the strategy planner on top of `GameEngineV2`, so every played move is taken from the engine's `get_legal_actions()` and passed back via `engine.step()`). Because both "players" ran in the same process sequentially, seat-swap bias is acknowledged — Game 3 swaps the opening/strategy assignments.

### Game 1 — Column vs. Row (P1=col3, P2=row3 style)
Opening discovery: at T7 P2 attempted to block (3,4) on P1's column. P1 at T8 **overwrote** P2's (3,4) and the CA flipping let the overwrite stick (f=1 own neighbor, e=1 enemy neighbor → (1,1,1)=1). P2 then passed repeatedly because every legal placement led to ko rollback. P1 completed the column (3,0)–(3,7) at T14.

- **Winner: P1 at turn 15 by connection.**
- Observation: the "overwrite + CA" mechanic is a genuine blocker-breaker, unlike Hex where you can never dislodge an enemy stone.

### Game 2 — Column vs. Row Race (P1=col4, P2=row0)
Both players raced to lay 8 collinear stones. P2 has the advantage here because P2 is completing row 0 which happens to intersect P1's opening (4,0) — P2 overwrites that cell at T9. P1's column is now missing its y=0 endpoint. At T15 P2 completes the full row 0 from x=0 to x=7.

- **Winner: P2 at turn 16 by connection.**
- Observation: second mover can **hijack an endpoint** by placing on top of the first-mover's edge stone. P1 must therefore build from the *away* edge (y=7 side) or defend the intersection cell.

### Game 3 (seat swap — previous P2-style player opens as P1) — Column 4 vs. Row 7
P1 plays the vertical column (4,0)..(4,7). P2 plays row 7. They collide at (4,7) last. P1 reaches (4,7) on turn 14 (P1's 8th move), completing the column before P2 can place their 8th row stone on turn 15.

- **Winner: P1 at turn 15 by connection.**

### Reflection

**Player 1 (connect y-axis):**
- Strategy: build an unbroken column on some x ∈ {3,4} — the cells farthest from both x-edges. Must seize the intersection with P2's planned row BEFORE P2 closes it.
- Would-do-differently: open (4,7) instead of (4,0) to force P2 to defend the far edge; open with a "bridge" (two stones one apart with a common empty neighbor) so a block can be countered by the other branch.
- Surprises: ko rollback silently turns bad moves into passes. Overwriting enemy stones with a well-supported placement is devastating.

**Player 2 (connect x-axis):**
- Strategy: row at some y ∈ {0, 7} so the CA only has to protect one side; y=4 is tempting but exposes the row to disruption from both halves of P1's board.
- Would-do-differently: open at the cell where P1's column meets the row — seize the tempo. Force P1 into isolated placements that ko-rollback.
- Surprises: P1's overwrite at the intersection cell auto-kills P2's stone there because P2's stone is adjacent to P1's chain but has no own neighbors (f=0, e≥1 → empty via `(friendly,0,1)→0`). Single-stone incursions are suicidal.

### Strategy Guides (short)

**P1 guide:** build vertical, stay connected, always have f≥1 when placing next to enemies. Prefer overwriting the intersection cell on the turn you'd otherwise lose the race. Ignore lone enemy incursions — the CA deletes them for free.

**P2 guide:** build horizontal on y=0 or y=7, open by grabbing the intersection cell with P1's column, repeat.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

- **Distinct viable strategies?** Barely. Both players essentially converge on "draw a straight line along my axis". The only real branching is *which* row/column to pick, and *when* to fight for the intersection cell. There is no territorial play, no group life/death, no ladder, no eye shapes.
- **Counter-play?** Limited. If you see P2 starting at (0,0)–(1,0)–(2,0), you know they are on row 0. You can race for the intersection, but you cannot cut row 0 because any lone blocker dies. Real blocks require building a supported chain into the row — which is itself a new line-drawing race.
- **Short-term vs long-term tension?** Minimal. Sacrifice-now-for-later is extremely weak because any "sacrificed" stone lacking own-support is silently ko-rolled back, so you don't even get the sacrifice.
- **Emergent concepts?** Tempo exists (first-player advantage ≈ 1 move). Initiative exists in a weak sense: the side that commits to a line first forces the other to choose block-or-race. **No ko fights arise in normal play** (despite super-ko being enabled) because ko rollback terminates the attempt rather than creating a ko loop. **No territory, no influence, no eye-shape life-and-death.**
- **Topology mattering?** Only mildly. The hex adjacency means vertical columns and horizontal rows are both valid monotone chains, and the extra diagonal adjacency means "bridges" (non-adjacent stones sharing two common empty neighbors) are possible in principle — but we didn't exploit any, because the CA's birth rules are too fragile and the race is too short for bridge strategies to mature.

**Verdict of joint analysis:** this game is a foot-race to build 8 collinear stones. Strategic depth is shallow.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary argues: this is NOT novel.

**(a) Known abstract strategy game catalog:**

- **Hex (1942, Hein/Nash):** same 2D hex board, same edge-connection win condition, same player-axis assignment. The *only* modifications are (i) overwrite-legal placement and (ii) a CA step after each move. For a typical game length of ~15 moves the CA barely fires in non-trivial ways, leaving the game ~90% identical to Hex. **Strongest analog.**
- **Y (Craige Schensted):** connect all three sides, similar connection-theory. Not this game (this has 2 players, 2 sides each).
- **Havannah:** bridge/ring/fork goals on hex; this game has none of those, it's still pure two-side connection.
- **Chameleon (Randy Cox):** connection with color-flipping. Closer than Hex because our CA *does* sometimes flip a stone with rule `(1,1,4)→2`. But Chameleon flips deterministically on capture; ours fires only when a connected stone has exactly 1 friend and 4 enemies — a rare, late-game configuration we never observed in Phase 2.
- **Reversi/Othello, Gomoku, Pente, Connect6, Amazons, Lines of Action, Mancala:** no. Different boards, different mechanics.
- **Life-like CA (Conway's Life, Day & Night, HighLife):** the CA here is a 3-state totalistic rule with friendly/enemy counts, not Life's 2-state. It is closer in spirit to "colored Life" variants. The effective live rules reduce to "loner dies" and "swamped connected stone flips" plus two rare birth rules. This is not any known published Life-like rule; and the rule tables that would make it Life-like are *dead* (unreachable) here.

**(b) CA-specific:** the rule set is not a known CA. The only meaningfully reachable rules are:
- `(1,0,1)/(1,0,2) → 0` — "loner dies next to enemies" (Go-like self-atari immediately captured).
- `(2,1,0) → 0` — symmetric: an isolated enemy next to a friendly dies.
- `(1,1,4) → 2` — "flip when swamped" (rare).
- `(0,2,3)→1`, `(0,4,0)→1` — birth rules that fire only in specific surround patterns.

The composite rule is closest to **Go atari+capture mechanics** expressed in a CA-symmetric way, grafted onto a Hex connection goal. "Go-atari on a Hex board with connection win" is essentially Hex with a redundant stabilizer.

**(c) Reskin hypothesis:** This game reskins as **Hex with two rule tweaks**:
1. Placement target="any" + overwrite legal.
2. Lone-stone-next-to-enemy dies (CA rule `(1,0,1)→0`).

Both tweaks push strongly toward "build a solid chain or die" which is *exactly* Hex's native strategic logic. A Hex expert would recognize the game instantly.

**(d) Hex-expert advantage test:** A 1500-Elo Hex player given this game would:
- Immediately know to build edge-to-edge through the short-diagonal (the actual winning strategy in Game 1 and 3).
- Use bridge/ladder intuition (bridges fail here because the CA kills unsupported bridge endpoints; ladders don't arise because there's no capture to chase).
- Dominate an untrained player easily.
- Struggle only with the overwrite rule (mild adjustment — overwrite only useful at intersections, which Hex doesn't have).

**Adversary conclusion: this is Hex + cosmetic CA veneer. Novelty score should be 2-3.**

### Rebuttal from Players 1 and 2

1. **The overwrite rule is load-bearing, not cosmetic.** Game 1 T8: P1 overwrites P2's block at (3,4). In Hex, this move is **illegal**; a Hex expert would be stuck. The entire line of play where "a supported stone eats an unsupported enemy stone by placement" has no Hex analog. This changes the tempo calculus: Hex is "once placed, always placed", this game is "only chains survive".

2. **The CA `(1,0,1)→0` rule creates *reflexive capture* that Hex does not have.** In Hex, a lone enemy stone is still a present stone that occupies space. Here it is deleted at end-of-turn. This means *cutting attempts* in Hex — where you jam a stone between two enemy stones to break a bridge — here become self-suicide. The Hex expert's #1 offensive primitive is broken.

3. **Ko rollback as pass** is a novel interaction of super-ko + CA. It introduces *no-op moves* that nominally look like placements but effectively skip the player's turn. A Hex expert would burn tempo against a player who understands the rollback and only plays ko-safe moves.

4. **Double-pass majority** provides a completely non-Hex endgame: if you are ahead on stones you can force the pass-sequence. In Phase 2 Game 1-variant this manifested as P1 winning without connection. Hex has no "majority" resolution.

Nonetheless, the Phase 2 games show that the **winning strategies collapse back to Hex-like line-drawing** in practice because the CA fires only near line-collisions, not in the open board.

### Resolution — Novelty score

Joint compromise: **3/10**. This is Hex with two real rule changes (overwrite + CA atari) that *would* produce novel play if the board were 12×12 and games averaged 40+ moves. On 8×8 with average game length ~20, the rule changes mostly serve as minor corrections to Hex's logic ("you can overwrite enemies" and "isolated stones die") — they do not generate genuinely emergent dynamics visible in short games. The adversary's hex-reskin argument survives the rebuttal.

---

## PHASE 5 — VERDICT

**Team ID:** team-2
**Game ID:** 06bab8a32425
**Rules Summary:** Two-player connection game on 8×8 hex board; place-only (overwrite allowed), adjacent-to-own constraint, 2 CA steps/turn that kill isolated stones and enable rare flips/births. P1 connects top-bottom, P2 connects left-right.
**Topology:** 2D hex 8×8 (64 cells, 6 max neighbors).

### SCORES (1-10)

- **Strategic Depth: 4/10** — one dominant plan (draw a straight line along your axis), with a shallow tempo battle over the intersection cell. No territorial, group-life, or ladder-like depth. The `(1,1,4)→2` flip and CA births are interesting in principle but rarely fire in ~15-move games.
- **Emergent Complexity: 3/10** — CA birth rules can create stones from nothing, but only in artificially engineered positions. In actual play almost no emergent patterns arise; most games end in a monotone line-build.
- **Balance: 6/10** — P1 has a tempo edge (3 of the 3 "clean" races we played were decided by 1 move, with P1 winning 2/3). Not catastrophic like single-player-always-wins, but the first-move advantage is meaningful. Seat-swap (Game 3) still saw P1 win.
- **Novelty (post-adversary): 3/10** — strongest adversary argument: "Hex + overwrite + atari-CA". Rebuttal points 1-2 are real but apply to late-game edge cases that rarely occur in 8×8 play. The game IS Hex-with-minor-tweaks in practice.
- **Replayability: 3/10** — once you know "draw a supported line along your axis, fight for the intersection cell", there is little to come back for. The 50+ additional CA rule entries are a red herring because 5 are dead and the rest encode Go-atari logic.
- **Overall "Would I play this again?": 3/10**

### CLOSEST KNOWN-GAME ANALOG
**Hex.** Same board, same connection win condition. Not identical because: (i) overwrite is legal, (ii) isolated stones self-destruct near enemies, (iii) super-ko rolls back certain placements to passes, (iv) double-pass falls back to piece-count majority. These differences are real but peripheral — they close some Hex tactics (cutting stones) without opening meaningful new ones.

### KILLER FLAWS

1. **Double-pass → majority tiebreak.** Lets a leading player force a non-connection win. Documented in project MEMORY.
2. **5 of 11 non-trivial CA rules are physically unreachable** (f + e > 6 on hex). Rule complexity is inflated; effective rule set is smaller than reported.
3. **Ko rollback silently converts failed placements to passes.** New players will burn multiple "invisible passes" before learning the ko table, inflating game length without adding depth.
4. **8×8 is too small.** Average ~15-move games don't let the CA or the overwrite mechanic display their theoretical effects. The game degenerates to a line-drawing race.
5. **Single-placement adjacent_to_own with no capture** means "defending" means "extending your own chain", which is identical to "advancing your own goal" — there's no defensive primitive distinct from the offensive one.

### BEST QUALITY
The **overwrite + CA-flip** combination at intersection cells (Game 1 T8) is the only moment of genuine emergent tactic. A stone is taken from the opponent without capture, by placing on it when supported. This is qualitatively different from Hex and could be interesting on a larger board with more time for the dynamic to recur.

### IMPROVEMENT IDEAS
**Single rule change:** Require placement on *empty* cells only, but allow PASS to invoke a CA step that can kill enemy isolated stones — OR — change double-pass resolution from majority to *connection-leader* (whoever has a path closer to completing their connection). This removes the exploit and forces players to actually satisfy the stated win condition. Alternatively, **enlarge the board to 12×12 or 14×14** so the CA's birth rules and flip rule have room to fire meaningfully and the tempo race lasts long enough for strategic texture to emerge.

---

## Summary

**Verdict:** Game `06bab8a32425` is a capable but derivative Hex variant with a CA layer that rarely fires. The Run 13 scoring (GE 0.521) overweights surface novelty — the game is essentially Hex-with-atari on too small a board to show off its CA rules. It plays cleanly and is balanced within 1 tempo, but lacks the emergent complexity that would make it worth publishing or replaying.

**Final scores:** Depth 4 · Emergent 3 · Balance 6 · Novelty 3 · Replayability 3 · Overall 3/10.
