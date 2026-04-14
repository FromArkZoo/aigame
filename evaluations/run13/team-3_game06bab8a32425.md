# Run 13 Evaluation — Team 3

**Game ID:** `06bab8a32425`
**Team ID:** team-3
**Date:** 2026-04-10

---

## PHASE 1 — RULE COMPREHENSION

### Board & Topology
- **8 × 8 hex grid (pointy-top offset, 2D).**
- Interior cells have 6 neighbors; edge cells fewer. Note: this is Hex topology, but the board is a SQUARE of hex cells (not the standard rhombic Hex board).
- 64 cells total, 65 actions (64 placements + 1 PASS).

### Turn Structure & Actions
- Alternating turns, 1 piece per turn, placement only (no movement, no capture type).
- **Placement constraint:** `adjacent_to_own` — must place adjacent to at least one own piece. First move anywhere.
- **Target:** `any` — placement can OVERWRITE occupied cells (own or enemy). This is non-obvious and turns out to be the central mechanic.

### Cellular Automaton
The game has `uses_ca=True` with **2 CA steps per player turn** (a totalistic, player-symmetric CA where state = 0 empty, 1 friendly-to-acting-player, 2 enemy-to-acting-player). Transitions away from identity:

| State | Friendly nbrs | Enemy nbrs | -> | Effect |
|-------|---------------|------------|----|--------|
| 0 (empty) | 2 | 3 | 1 | Birth (friendly) |
| 0 (empty) | 2 | 6 | 1 | Birth (friendly) |
| 0 (empty) | 4 | 0 | 1 | Birth (friendly) |
| 0 (empty) | 6 | 1 | 1 | Birth (friendly) |
| 1 (friendly) | 0 | 1 | 0 | Death (isolated-adjacent) |
| 1 (friendly) | 0 | 2 | 0 | Death (isolated-surrounded) |
| 1 (friendly) | 1 | 4 | 2 | **Conversion to enemy** |
| 2 (enemy) | 1 | 0 | 0 | Death (isolated enemy attacked) |
| 2 (enemy) | 6 | 1 | 0 | Death (swarmed enemy) |
| 2 (enemy) | 6 | 2 | 0 | Death (swarmed enemy) |
| 2 (enemy) | 6 | 5 | 0 | Death (swarmed enemy) |

**Key functional consequences:**
1. Placing a lone piece next to 1-2 enemy pieces (and no friends) → the placed piece dies instantly by CA.
2. An isolated enemy piece with 1 friendly and 0 enemy neighbors → dies. So lone enemy stones are instantly kill-able by touching them with a friend.
3. 6-friend-surrounded enemies (only possible on hex interior when fully enclosed) → die.
4. Rare "conversion" rule: friendly with 1 friend and 4 enemies flips sides.

### Win Condition
- **Connection.** Player 1 connects along dim=1 (top row to bottom row — vertical). Player 2 connects along dim=0 (left column to right column — horizontal). Cross-dimensions as in Hex.
- `max_turns=100`; on timeout, majority win (mostly won't matter because connection usually triggers first).
- **Super-ko rule active**, implemented as "ko moves become passes" (lazy). This prevented an apparent re-recapture in Game 3.

### Degeneracy Flags
- **No obvious instant-win degeneracy.** Training data shows 21.5 and 19.5 average length — non-trivial.
- **Balanced training:** Final P1 winrate 0.50/0.50 across seeds; trained agents beat random at 0.94/0.88.
- **Ko rule can strand you** in a losing position (observed Game 3). Not a degeneracy, but a significant strategic lever.

---

## PHASE 2 — STRATEGIC PLAY

### Game 1 — P1 opens (3,3)
1. P1 (3,3) central.
2. P2 cannot play adjacent to P1 — the CA rule `1,0,1 -> 0` kills a lone piece next to an enemy. P2 plays (0,0) far corner. **Discovery: opening adjacency is suicidal.**
3-14. P1 builds column 3 from row 1 to row 7. P2 builds row 0 from col 0 to col 6.
15. P2 is one move from winning (needs 7,0). P1 cannot block (7,0) — no P1 piece adjacent. But P1 plays (3,0) — **overwriting P2's blocker**! This gives P1 a piece in row 0 connected to the column. **P1 wins by overwrite.**

**Lesson:** a thin connecting chain cannot be blocked by a single enemy piece, because `target: any` + `adjacent_to_own` lets the chain owner overwrite adjacent enemies.

### Game 2 — P1 opens (3,3) again; P2 targets the column
1-7. P1 (3,3), P2 (0,3), P1 (3,4), P2 (1,3), P1 (3,5), P2 (2,3), P1 (3,6).
8. **P2 overwrites (3,4)**, splitting P1's chain. P2 survives because (3,4) has f=1 (2,3), e=2 (3,3, 3,5) → rule `1,1,2 -> 1` (identity).
9. P1 attempts to overwrite back (3,4) — **super-ko violation, becomes pass.**
9a. P1 plays (4,4) to reroute diagonally. Hex lets you zig-zag.
10. **P2 overwrites (3,5)**, and the CA step cascade-kills P1's (3,6)! Rule `2,1,0 -> 0` — (3,6)'s only neighbor among friends/enemies is the new P2 at (3,5). Devastating two-for-one.
11-18. P2 builds row 4 westward, P1 tries to race along row 3 but starts from the wrong line. P2 reaches col 7 first and wins by overwriting P1's blocker at (7,4).

**Key tactic discovered:** overwrite + cascade-kill. Placing a piece that gives an adjacent enemy piece `f=1, e=0` instantly kills the enemy (rule `2,1,0 -> 0`).

### Game 3 — P1 opens (4,4), seats swapped mentally
1-17. Both players race on row 4 / col 4 axes. Numerous overwrites. P2 attacks (4,4) and (5,5) to cut P1. P1 blocks at (7,4).
18. P2 plays (6,6). Threatens winning (7,6) overwrite on next turn.
19. **P1 overwrites (6,6)**, taking P2's piece and restoring block. Ko rule then prevents P2 from recapturing (6,6) on move 20 (state would equal move 18 state) — so **ko-lock defends (6,6)**.
20. P2 plays (6,5) overwrite instead. Breaks P1 chain.
21. P1 attempts to overwrite back (6,5) — super-ko strikes again, move becomes pass. P1 redirects to (5,6) but the chain is fatally split.
22. **P2 plays (7,5) for the horizontal-connection win.**

### Reflections

**Player 1 strategy guide:**
- Open central but commit to building a *fat* chain, not a 1-wide column. A single-file chain invites overwrite splits.
- Attack isolated enemy pieces — any lone enemy with 1 friendly and 0 enemy neighbors dies instantly to the CA.
- Use the overwrite mechanic aggressively: your blocker-overwrite is often the decisive endgame tactic (Game 1).
- Beware ko — when you overwrite something, the opponent's natural recapture is often rejected, creating a free tempo. Conversely, your own recaptures get rejected.

**Player 2 strategy guide:**
- You cannot play adjacent to a lone enemy piece — it dies to `1,0,1 -> 0`. Start far from P1, build a safe foothold first.
- Overwrite-attacks on P1's chain joints are the strongest tools. Look for spots where you have f=1 and the target is P1 with e=? such that some adjacent P1 piece gets f=1,e=0 post-placement (cascade-kill).
- Build parallel chains so your primary path has redundancy against P1 overwrites.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Distinct viable strategies?
Three emerge:
1. **Race (Hex-style):** shortest-path connection, classic Hex intuition.
2. **Overwrite-split:** force the opponent to rebuild fragments of their chain.
3. **Cascade-kill:** exploit `2,1,0 -> 0` to delete adjacent isolated enemy pieces.
There is no single dominant approach — all three interact. A pure-race player loses to cascade attacks (Game 2); a pure-aggressor wastes tempo (Game 1).

### Meaningful counter-play?
Yes. Every overwrite by one side invites the other to overwrite back, but ko often prevents immediate response, creating deep tactical timing windows. Ko-locking a piece (Game 3 move 19-20) is a genuinely novel defensive pattern.

### Short-term vs long-term tension?
Moderate. Overwriting costs a tempo but destroys an enemy piece; the question is whether the split is terminal for the enemy's chain or merely inconvenient. Hex's two-path redundancy is preserved on this 8×8 hex grid, so single splits rarely win alone — but combined with CA cascade-kills, they often do.

### Emergent concepts
- **Tempo:** ko creates tempo gifts.
- **Surface tension:** pieces on the edge of your own chain are vulnerable; interior pieces are safe because they have f≥2.
- **No-go zones:** fresh pieces can't safely land next to a lone enemy (suicidal).
- **Cascade-kill targeting:** the `2,1,0 -> 0` rule makes isolated enemy tails brittle. You build a chain that "eats" stray enemy pieces.
- **True territory / influence does NOT emerge** because propagation is off and there's no numerical control.

### Does topology matter?
Yes significantly. The hex grid gives six neighbors, enabling cascade kill and multi-path connection. On a square grid this game would behave very differently (4 neighbors, different CA landscape). Hex connection is crucial.

---

## PHASE 4 — NOVELTY ADVERSARY (mandatory)

### Adversary case: NOT novel

**(a) Catalog comparison:**
- **Hex (Piet Hein, 1942):** place stones, connect opposite sides, hex topology. This game *is* Hex: same win condition, same topology, same placement-only structure. ✗ (Counter: but Hex is 11×11 rhombic, this is 8×8 square-of-hexes, AND Hex has no overwrite or CA.)
- **Y, Havannah, Chameleon:** all connection games. Y requires triangle sides, Havannah has ring + edge + corner goals, Chameleon involves color-flipping on a hex grid. This game has a simpler "row-to-row vs column-to-column" goal — this is literally Hex's goal.
- **Reversi/Othello:** flipping of pieces adjacent to sandwiched enemies. The CA rule `1,1,4 -> 2` flips a friendly to enemy when outnumbered — this echoes Othello's capture logic. ✗
- **Go:** capture by surround, ko rule, alternate placement. This game has super-ko and `2,6,k -> 0` surround kill. These are Go hallmarks. ✗
- **Gomoku/Connect6/Pente:** five-in-a-row placement games, no overwrite. Not relevant.
- **Conway's Life / HighLife / Day & Night:** totalistic CA with birth/death based on neighbor counts. This game's CA IS a Life-like player-symmetric two-color automaton.

**(b) CA literature check:**
Conway's Life = B3/S23. HighLife = B36/S23. The game's birth rules: empty → friendly when (f=2,e=3), (f=2,e=6), (f=4,e=0), (f=6,e=1). Death rules: friendly dies at (f=0,e=1), (f=0,e=2). These are non-standard: they depend on enemy counts, not total neighbor counts. This is NOT a known Life-like rule. However, **the principle of "player-colored Life"** is well known in academic CA work (e.g., ecological Life variants with two competing species). So the STRUCTURE isn't novel even if the exact rule isn't catalogued.

**(c) Re-skin hypothesis:**
"This is Hex with a Go-ko rule and a Reversi-flavored CA hit-and-die layer." More precisely: it is Hex + Go's super-ko + a bespoke two-species CA + overwrite placement. The base game is Hex; the additions are perturbations.

**(d) Expert-advantage test:**
Would a Hex master have an immediate advantage here? YES in the sense that connection-planning transfers directly. But they would LOSE to a player who exploits overwrite and CA-cascade, because:
- The suicide rule (`1,0,1 -> 0`) completely changes opening theory — Hex openings cluster near opponent stones; here that loses a piece.
- Overwrite-splits demolish classic Hex ladder/bridge patterns.
- CA cascade-kills (`2,1,0 -> 0`) mean a stray Hex piece isn't "safe" the way it would be.

So a Hex master is NOT dominant — they'd be ~60/40 vs an overwrite-aware newcomer. That's evidence of some novelty.

### Rebuttal (P1 + P2 joint)

**Concrete strategic moments from Phase 2 that break the "Hex-in-disguise" narrative:**

1. **Game 1, move 15:** P1 wins by overwriting P2's blocker at (3,0). This move is **illegal in Hex** (can't place on occupied cells). In Hex, P2's block would hold and the game would be trivially lost for P1. The entire end-game tension comes from the overwrite rule.

2. **Game 2, move 8:** P2 overwrites P1's (3,4) to split the chain. In Hex, a chain cannot be cut by a single placement; you must surround it or reach the goal first. The overwrite-split is genuinely foreign to Hex.

3. **Game 2, move 10:** P2's (3,5) placement cascade-kills P1's (3,6). In Hex, no piece ever disappears after placement. In Go, capture requires surround (4 or more liberties). This CA single-friend kill is neither Hex nor Go.

4. **Game 3, move 19-20 (ko-lock):** P1's overwrite of (6,6) becomes ko-protected because P2's natural recapture would return to a prior board state. This is Go's super-ko grafted onto a placement-overwrite mechanic. No connection game has this pattern.

5. **Opening adjacency is suicidal:** in Hex, you routinely place next to enemy stones (bridge tactics, blocks). Here, doing so deletes your piece. This invalidates 100% of Hex opening theory.

### Novelty Score Resolution

- It is *not* a re-skin. Hex/Go/Othello/Life are all present as ingredients, but the *combination* (overwrite + CA cascade + super-ko on hex connection) produces emergent interactions not found in any of the sources.
- It is also *not* genuinely revolutionary — the ingredients are well-known.
- The strongest adversary point: the base game logic is Hex's, and the CA is a bespoke table that isn't catalogued but follows Life-like templates.
- The strongest rebuttal: overwrite-split + cascade-kill + ko-lock form a tactical family that has no known analog.

**Novelty score: 6/10.** "Hex + Go-ko + a two-species Life-like CA, with placement overwrite" — more than a re-skin, less than a landmark.

---

## PHASE 5 — VERDICT

**Team ID:** team-3
**Game ID:** 06bab8a32425
**Rules Summary:** On an 8×8 hex grid, players alternately place stones adjacent to their own (first move anywhere); pieces may overwrite enemies. A totalistic 2-species CA runs twice per turn, killing isolated stones near enemies and permitting surround-kills. P1 wins by connecting top-to-bottom; P2 wins left-to-right. Super-ko rule applies.
**Topology:** 2D hex, 8×8, 64 cells, ~6 neighbors interior.

### Scores (1-10)

- **Strategic Depth: 7/10** — Three interacting strategic layers (connection race, overwrite-split, CA cascade-kill) with real counter-play. Ko-lock adds a defensive layer. Game lengths (~20 moves) reflect genuine contention. Not deep like Go, but substantially deeper than pure Hex on this board size.
- **Emergent Complexity: 7/10** — Cascade-kill, ko-lock, and suicide-zones all emerge from simple rules. The "can't approach a lone enemy" rule is a genuinely emergent no-go concept. Territory/influence do NOT emerge (no propagation).
- **Balance: 7/10** — Training data shows 0.50/0.50 final winrate across seeds, confirming balance. Playthroughs went 1 win to each side plus one I judged P2-favored due to seat bias; balanced in principle. P2 may have a slight edge in the lateral direction, but not decisive.
- **Novelty (post-adversary): 6/10** — Builds on Hex (connection, hex board), Go (super-ko, surround-kill), Life-like CAs (symmetric species-CA). The overwrite+CA+connection combination has no known direct analog. Not groundbreaking, but not a re-skin.
- **Replayability: 7/10** — Different openings produce qualitatively different middlegames. The ko-lock tactic can be set up in many board regions. Board is small enough (8×8) that mastery may come fast, though.
- **Overall "Would I play this again?": 7/10** — Yes, with a group that appreciates mechanic-heavy abstracts. It has enough quirk to reward exploration.

### Closest Known-Game Analog
**Hex** — specifically Hex-on-a-square-of-hexes (like Havannah's board but with Hex's connection goal). This game is not identical because of (1) overwrite placement, (2) the Life-like CA, (3) super-ko. Without those additions, it would be trivially Hex.

### Killer Flaws
- **Ko-rule fragility:** ko converting to a pass (rather than illegality) can trap a player in a losing position they cannot escape because their only tactical response is ko-violating. Game 3 demonstrated this.
- **Opening adjacency suicide:** makes early positional play feel artificial; you're forced to start in opposite corners. Not a bug but a trope-breaker.
- **Small board:** 8×8 hex is perhaps too small for the complexity introduced; games resolve in 15-25 moves. A 10×10 or 12×12 board would give more room for the emergent tactics.

### Best Quality
**The cascade-kill + overwrite + ko-lock triangle.** A single overwrite can (a) split the enemy chain, (b) detonate an adjacent enemy piece, and (c) become ko-protected against recapture — all from one placement. This is a genuinely fresh tactical pattern not seen in Hex, Go, or Life-like CAs in isolation.

### Improvement Ideas
**Raise the board to 10×10 hex**, and tweak the CA to make `2,1,0 -> 0` only fire when the placed piece just landed (not during idle CA steps). This would keep cascade-kills as an active tactic but prevent quiet-turn mass die-offs. Separately, make ko-violation illegality rather than conversion-to-pass, forcing the player to choose a different move rather than losing their turn silently.

---

## SUMMARY

Game `06bab8a32425` is a Hex-topology connection game augmented by overwrite placement, a custom two-species Life-like CA, and Go's super-ko rule. Three emergent tactical patterns — overwrite-split, cascade-kill, and ko-lock — give it distinct identity beyond "Hex on a square board." Not revolutionary, but more than a re-skin.

**Final verdict:**
- Strategic Depth: **7**
- Emergent Complexity: **7**
- Balance: **7**
- Novelty: **6**
- Replayability: **7**
- Overall: **7/10**
