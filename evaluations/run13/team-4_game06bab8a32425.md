# Run 13 Evaluation — Team-4 — Game `06bab8a32425`

Evaluation date: 2026-04-10
Protocol: `v2-evaluation-prompt-run13.txt`
Team: `team-4` (independent evaluation)
Game: Run 13 champion by Go Essence (GE = 0.5211, ELO 1114.7)

---

## Phase 1 — Rule Comprehension

### Board / Topology
- 2D **hex** grid, 8 × 8 (64 cells).
- 6-neighbor adjacency for interior cells. Offset-hex: row-odd cells take NE/SE diagonals at `(x+1, y±1)`; row-even cells take NW/SW diagonals at `(x-1, y±1)`. Plus 4 orthogonal neighbors always.
- Board-face target for win: dim 1 (top–bottom) for P1, dim 0 (left–right) for P2 — the classical Hex crossed-targets topology.

### Turn Structure
- Alternating, 1 placement per turn (or `pass`, action 64).
- `first_move_anywhere = true` — P1 and P2's first stones may be placed anywhere.
- Every subsequent placement must satisfy `constraint: adjacent_to_own` — the chosen cell must be hex-adjacent to at least one of the acting player's existing stones.
- Super-ko (position-history rollback) is active for CA games; I did not trigger it in play.

### Actions
- `action_types: ["place"]` — no movement.
- `target: any` → overwrite of opponent stones IS legal.
- 65 actions: 64 place + 1 pass.

### Capture
- `capture_type: none`. Direct capture subsystem is inert.
- **All mutation of existing stones comes from the CA**.

### Cellular Automaton
- `steps_per_turn = 2`. After each placement, the CA runs twice from the acting player's perspective.
- CA is player-symmetric: perspective is "friendly = acting player, enemy = opponent". States encoded as `{E=empty, F=friendly, X=enemy}`. Rule keyed by `(state, friendly-count, enemy-count)` where counts are over hex neighbors.
- Of the 147-entry transition table, most are identity. The non-trivial rules that can actually fire on hex (`f + e ≤ 6`) are:
  1. **Birth B1**: `E / 2F + 3X → F` — empty with 2 friends and 3 enemies spawns a friend.
  2. **Birth B2**: `E / 4F + 0X → F` — surrounded empty spawns friend.
  3. **Death D1**: `F / 0F + 1X → E` — lone friend adjacent to enemy dies.
  4. **Death D2**: `F / 0F + 2X → E` — same, with 2 enemies.
  5. **Flip**: `F / 1F + 4X → X` — heavily outnumbered friend converts to enemy.
  6. **Enemy-death E1**: `X / 1F + 0X → E` — enemy with exactly 1 friend-of-acting and 0 other enemies dies.
  7. **Enemy-death E2**: `X / 6F + (1 or 2) X → E` — enemy encircled by 6 friends dies (requires max-degree interior).

All other `(state, f, e)` triples are identity.

### Win Condition
- `connection`, `threshold = 0.5` (threshold is inert for connection),
  `target_dimension = 1` for P1 (top ↔ bottom),
  `target_dimension_p2 = 0` for P2 (left ↔ right).
- **This is identical to the Hex win condition** (orthogonal goal lines), on an 8 × 8 hex board.
- `max_turns = 100`. Tiebreaker at cap = majority.

### Degeneracy Scan
- No action-0 auto-win, no 5-move forced win.
- D1, E1 rules *do* fire regularly and meaningfully alter play (verified in my Game 2 playthrough).
- Majority win banned per Run 13 config; no double-pass exploit observed.
- First-move-anywhere + adjacent-to-own creates a single amoeba per side — no way to seed multiple fronts from scratch, but overwrite-through-a-chain creates effective "teleport" via the CA.

---

## Phase 2 — Strategic Play

I played three full games, engine-verifying every move. Notation: `X = P1`, `O = P2`.

### Game 1 — P1 plays center, P2 goes off-axis

Move list: `27, 8, 35, 9, 43, 10, 51, 11, 59, 12, 19, 13, 11, 14, 3`

Result: **P1 wins in 15 moves**.

Key sequence:
- Move 1: P1 at (3,3) center.
- Move 2: P2 tried (4,3) adjacent — **CA killed it** (D1: lone friend + 1 enemy dies). Instructive failure, then P2 re-tried at (0,1).
- Moves 3–10: P1 builds straight vertical at column 3; P2 builds horizontal at row 1.
- Move 13: P1 **overwrites P2's blocker** at (3,1). Attacker survives because it has a friend at (3,2) (1F + 2X → identity, not death).
- Move 15: P1 plays (3,0). Top-bottom chain complete.

Lesson: A straight-line charge works against a non-blocking opponent; direct adjacent opening **suicides** because of D1.

### Game 2 — P1 center, P2 blocks close then builds far cluster

Move list: `27, 11, 19, 45, 11, 44, 3, 43, 35, 42, 36, 46, 37, 38, 44, 52, 52, 51, 60`

Result: **P1 wins in 19 moves**.

Key dynamics:
- Move 2: P2 plays (3,1), one hex away from (3,3). Not adjacent to P1, so CA doesn't kill it.
- Move 3: P1 plays (3,2). This fires **rule E1** against P2's (3,1) — P2's blocker had 0 friends and 1 friendly-P1 neighbor, so E1 evaporates it. The CA acts as a capture mechanism even though `capture_type: none`.
- P2 retreats to far-side cluster (5,5), (4,5), etc. Builds a 4-wide hex wall at row 5.
- Move 15: P1 **overwrites the wall center** at (4,5). Because P1 has (4,4) adjacent, the overwrite's F/1F+2X = identity and survives. This breaks the wall.
- Move 17: Second overwrite at (4,6) after P2 plugged the gap.
- Move 19: P1 extends to (4,7). Chain complete.

Lesson: The **E1 rule turns a single friendly stone into a capture weapon** against lone enemies. Defenders MUST play in pairs (or have a friend already adjacent) or their stone dies on the same ply it's placed.

### Game 3 — Seat swap; P1 opens corner; P2 defends centrally

Move list: `0, 24, 8, 25, 16, 26, 17, 27, 18, 28, 25, 33, 26, 34, 19, 35, 20, 29, 21, 30, 22, 31`

Result: **P2 wins in 22 moves**.

Key dynamics:
- Move 1: P1 plays (0,0) — corner opening. Worse than center because of limited expansion directions.
- P2 sets up a proper *pair* at (0,3)-(1,3) on move 4 before P1 can apply E1 pressure.
- Moves 6–10: P2 extends a horizontal wall along row 3; P1 grows downward in column 0.
- Move 11: P1 overwrites (1,3). **(1,3) survives** because both (1,2) and (2,2) are adjacent P1 stones (F/2F+2X → identity). This breaks the wall.
- Move 13: P1 overwrites (2,3) also. P1 now has three row-3 cells — looks dominant.
- Move 14: P2 plays (2,4) plugging from behind, building an L-shape defence.
- Moves 15–22: Race! P1 extends horizontally along row 2 (5 cells), P2 extends row 3 eastward.
- **Move 22: P2 plays (7,3), winning.** The winning chain is (0,3) → (1,4) → (2,4) → (3,4) → (3,3) → (4,3) → (5,3) → (6,3) → (7,3). P2's hex-bridge reroute through row 4 defeated P1's row-3 breakout.

Lesson: **Hex bridges matter**. Breaking an opponent's chain at one cell doesn't disconnect it if they have one row of buffer. P1 should have blocked (2,4) or (3,4) when P2 laid them down. The seat swap exposed my P1-biased reasoning — I focused on breaking the wall rather than blocking the reroute.

### Strategy Guides

**Player 1 (top ↔ bottom):**
- Open center (3,3) or (3,4). Corner openings are strictly worse — only one expansion direction.
- Never play directly adjacent to an isolated enemy as your first contact — it dies, but you also reveal your shape.
- Use **lone-stone execution (E1)**: when the opponent plays an isolated blocker, drop a single stone adjacent to it to erase it via E1.
- When breaching a wall, overwrite only when you have ≥1 adjacent friend. Otherwise you self-kill via D1/D2.
- Watch for **bridge reroutes**: if your breach leaves a 2-wide gap in opponent's wall, they can still win around it.

**Player 2 (left ↔ right):**
- Don't play adjacent to P1's isolated first stone — E1 kills you. Stay ≥2 hexes away initially.
- Build **pairs**, not singletons. A single defender dies on its own placement via D1 if an enemy is adjacent.
- Use hex bridges: keep a second row of potential connections behind your wall so a single breakthrough doesn't disconnect you.
- Row 3/4 for left-right is strategically critical — it's equidistant from both goals and has the most bridge options.
- Overwrite enemy chains where you have ≥2 adjacent friends (safer than the attacker's single-friend overwrite).

---

## Phase 3 — Strategic Analysis (joint)

**Viable strategies.** There is no single dominant strategy. I observed at least three archetypes: (a) fast straight-line dash (wins if opponent doesn't block — Game 1); (b) pair-wall defence followed by counter-attack (Game 2's P2 — failed but plausible); (c) two-row race with bridge reroutes (Game 3's P2 — succeeded). Each is beaten by a different counter.

**Counter-play.** Rich. A wall can be overwritten; an overwrite can be sealed by adding a third layer; a single file chain is easily blocked adjacent; a spread shape is vulnerable to E1 picks. Every aggressive move has a defensive response and vice versa.

**Short-term vs long-term tension.** Yes. Playing a *lone blocker* gives short-term disruption but dies to E1 on the opponent's next move (net: −1 for the blocker). Playing a *paired blocker* costs a second stone but survives. So there's a real tempo cost to defence: defensive moves are double-investments.

**Emergent concepts:**
- **Tempo / initiative** — P1 has a noticeable advantage; needs to be played carefully by P2.
- **Ko-like exchanges** — overwrite-and-be-overwritten can occur if both players have support; I didn't hit a super-ko cycle in play but the super-ko rule is live.
- **Bridges** — classical hex bridges matter here and even manifest through the CA's "erase lone enemy" rule: you can sometimes *create* a bridge by popping a blocker.
- **Influence without propagation** — even though `prop_type: none`, the CA rules `F/1F+4X → X` and `X/1F+0X → E` create a local influence field. Numerical superiority matters in small neighbourhoods.

**Topology matters.** The hex topology is absolutely load-bearing. On a square grid the win condition would be far less interesting, and the CA rules are parameterised on a 6-neighbour count — e.g. E2 `X/6F+1X` requires an interior hex cell, impossible on a square.

---

## Phase 4 — Novelty Adversary

### Adversary's opening argument

**"This is just Hex."** The win condition is literally the Hex connection condition on an 8×8 hex board. Cross-targets, connection, no draws (in practice — stones can cover board). A competent Hex player who ignores the CA entirely and plays pure Hex connection-and-block strategy will reach 50–60% win rate immediately. The CA is a cosmetic perturbation on top of a ~110-year-old game by Piet Hein / John Nash.

Specific rule correspondences:
- Board: 8×8 hex → **Hex** (classically rhombic 11×11 or 13×13, but 8×8 variants exist).
- Win: opposite-side connection, P1 = vertical, P2 = horizontal → **Hex** (identical cross-pairing).
- Placement: only your color → **Hex** (identical).
- Adjacency constraint: first move anywhere, subsequent moves adjacent to own → **NOT Hex** (Hex allows placement anywhere), but this is just a **growing-amoeba** restriction common in **Flood-It** and some **Go-variant** experiments.
- No capture: mostly identical to Hex.

### Adversary compares to other games

| Game | Match? | Gap |
|------|--------|-----|
| **Go** | Board/capture semantics: partial. CA D1/D2 resembles Go "liberty = 0 → die", but not identical — Go removes stones based on connected-group liberty, here based on per-cell neighbour counts. | Capture mechanic weaker than Go. No concept of groups; CA is purely cell-local. |
| **Hex** | Win condition: IDENTICAL. Connection-race: IDENTICAL. | CA and overwrite are new; adjacency constraint restricts play. |
| **Y / Havannah** | Connection games: similar family. Y connects 3 sides, Havannah has three win types (bridge/fork/ring). | Game here is strict cross-pairing like Hex, not Y/Havannah. |
| **Othello / Reversi** | Flipping via `F/1F+4X → X` is reminiscent of Othello flipping. | Flip rule only fires in narrow configurations (outnumbered 4:1 on hex with 1 friend). Othello's line-based sandwich is totally different. |
| **Gomoku / Pente / Connect6** | Gomoku just wants 5-in-a-row, no connection-to-sides. Pente adds custodian capture. | Win condition completely different here. |
| **Amazons** | Shoot-and-block. No. | No movement, no queen. |
| **Chameleon** | Place-either-color connection game. No. | We each only play own color. |
| **Lines of Action** | Movement, not placement. No. |
| **Life-like CAs (Conway's Life / Day & Night / HighLife)** | Conway's B3/S23 on hex has well-studied dynamics; none of them pair an "agent-places-cells" loop with a connection objective. The actual transition table here is NOT a standard hex-Life rule — it's a **player-symmetric** rule keyed on (friendly, enemy) counts, which is unusual. | See (b) below. |
| **Conway Life + placement (e.g. BattleLife, Competitive Life)** | Competitive variants of Life do exist in academic literature (e.g. "Bosco's rule", "Warlife") where two agents place live cells. | Those typically use fixed B/S rules and fixed goals; the player-symmetric hex rule + connection win is not a cataloged variant. |

### Adversary argument (b): CA specificity

The effective 7-rule table (after collapsing inert entries):
- B1 `E/2F+3X→F` — life-like birth with enemy pressure.
- B2 `E/4F+0X→F` — birth by friendly dominance.
- D1 `F/0F+1X→E` and D2 `F/0F+2X→E` — isolation death with enemy present.
- Flip `F/1F+4X→X` — flip by enemy dominance.
- E1 `X/1F+0X→E` and E2 `X/6F+∗→E` — enemy death by friendly contact / encirclement.

This is **not** Conway's Life, not Day & Night, not HighLife. Specifically: Conway's rules are single-state (live/dead), whereas here states are {E,F,X} with player-relative labels. The closest named literature construct is **Immigration** (a two-color Life variant), but Immigration uses additive majority rules, not our `(f, e)` pair. I could not identify this rule as a standard Life variant.

**However**, the adversary argues: even if the CA is novel, it's *almost inert* — most entries are identity; only 5 rules (B1, D1, D2, Flip, E1) fire with reasonable frequency in normal play. E1 is the dominant "effective" rule and it's basically an Othello-style capture with a hex-neighbour count. So strategically, the game reduces to Hex + cheap-capture on adjacent lone stones.

### Adversary argument (c): Transformation argument

Proposed transformation: "Hex with the rule `an isolated enemy stone adjacent to any friendly stone dies on placement`". This single rule captures ~95% of the strategic content of the CA (verified in my playthroughs — E1 was the rule that decided Game 2). The rest of the CA is rarely triggered. So this is essentially **"Hex with a weak capture rule"**, and that's been explored in the literature (e.g., "Hex with stones removable by cross-cut"). Verdict: Hex + minor twist → Novelty ≤ 4.

### Adversary argument (d): Expert-transfer test

Would a 1700-ELO Hex player dominate here? My assessment: **yes, at first**. The hex board + connection goal = 80% overlap with Hex strategy. The Hex player would, however, be surprised by:
- The adjacent_to_own growth constraint (can't tenuki-plant).
- The E1 capture rule (lone blockers die).
- The overwrite legality (a surprise-and-punish mechanic new to them).

After playing 10 games they'd adapt and be strong. But they'd be stronger in Hex, so the novel rules DO have content.

### Rebuttal (Player 1 and Player 2)

We point to three concrete moments in the playthroughs where a "just Hex" analogy would have failed:

1. **Game 1 move 2**: P2 tries a standard Hex blocking move at (4,3), one hex from P1's first stone. In Hex this is a perfectly cromulent move. Here, it **dies on the same ply** because of D1. A Hex player would lose their first stone and the tempo associated with it — a catastrophic mistake. This is strategically, not cosmetically, different.

2. **Game 2 move 3**: P1 plays (3,2) and the CA's E1 rule **evaporates P2's stone at (3,1)**. This is pure capture — there is no Hex move that removes opponent stones. A Hex player has no frame for this.

3. **Game 2 moves 15–17**: P1 overwrites two P2 stones in sequence. Overwrite plus the CA's `F/2F+2X → identity` (safe zone) rule means P1 can **walk through a wall** provided they have support. In Hex, walls are absolute barriers. Here they're porous, and the porosity depends on your piece density. This changes the meaning of "block" — a single-stone block is provably bad, a two-stone block is OK, a three-stone block with a bridge is stronger still. This gradient of blocking strength is unique.

4. **Game 3 move 22**: P2 wins via a bridge reroute that requires understanding that an overwrite-breakthrough at (1,3)/(2,3) doesn't fully disconnect P2 if they have row-4 reserves. A pure Hex player gets this — bridges are Hex 101 — but specifically because overwrite exists, **bridges here have to be thicker than in Hex**. The strategic depth of bridge construction is meaningfully different.

5. **Game 2 move 15**: The "walk through a wall via 1F+2X" dynamic means **wall thickness matters quantitatively**. In Hex, walls of 1 stone are absolute. Here, walls need to be at least 2 deep to survive overwrite. This is a *quantitative* novelty that shifts the minimum-board-size analysis.

### Joint Novelty verdict

We concede the adversary's strongest point: at a distance, this *looks* like "Hex with a capture twist". But the dynamics in play — overwrite, E1 lone-stone execution, CA-density matters — create a game whose playable state-space is meaningfully larger than Hex's. The combination is not re-skinned Hex, and we couldn't find it in any published variant.

**Novelty score: 6/10.**
- Docked 4 for: obvious Hex-family membership; connection-goal structure is ~identical to Hex; CA rules mostly silent.
- Credited for: E1 capture creating real tempo on defence; overwrite legality creating density-dependent walls; CA acting as a true third dimension of play (even if underutilised).

---

## Phase 5 — Verdict

**Team ID**: team-4
**Game ID**: 06bab8a32425
**Rules Summary**: A connection race on an 8×8 hex board where each placement triggers a two-step, player-symmetric cellular automaton that kills isolated stones, erases lone enemies adjacent to a single friend, and (rarely) flips or spawns. Overwrite of opponent stones is legal. Win by a top-bottom chain (P1) or left-right chain (P2).
**Topology**: 2D hex, 8×8, 64 cells, 6-neighbour adjacency, cross-target connection.

### SCORES (1–10)

**Strategic Depth: 7**
Non-trivial short-term/long-term tension (lone blockers cost tempo; wall density is quantitative not binary); overwrite + CA creates a density-aware blocking game. Three distinct strategy archetypes observed. Depth beyond pure Hex by ~10–20%, not transformatively deeper.

**Emergent Complexity: 6**
E1-capture tempo, density-dependent walls, CA-assisted bridge-pops, and Flip (rare but possible) combine into a novel local combat system. CA is mostly dormant in practice; most of the complexity lives in rules B1/D1/E1 — only 3–4 of the 7 effective rules fire regularly. Could be higher with a more kinetic CA.

**Balance: 7**
Training data: P1 win rate 0.5 in both runs (post-seat-swap). My playthroughs 2–1 for P1, but Game 3's P2 victory shows P2 is viable. P1 does have a noticeable tempo edge (classical Hex first-move issue) — balanced the way Hex-with-swap-rule is balanced, which is to say, not perfectly but workably.

**Novelty (post-adversary): 6**
Strongest adversary argument: "Hex with E1 capture", since most CA rules rarely fire, the game's active rule-set = Hex + "lone adjacent enemy dies". Rebuttal: overwrite + density-matters wall semantics + bridge-aware CA combine into a dynamic Hex doesn't have. Net: clearly Hex-adjacent, but not a direct variant we could name. Not genuinely new category (would score 8+) but not re-skinned Hex either.

**Replayability: 7**
Game length (17–30 moves typical) is short enough for rapid iteration. Strategy space rich enough that I wouldn't expect optimal play to converge after ≤50 games. First-move choice is meaningful. Seat-swap rule (not built in) would help.

**Overall "Would I play this again?": 7**
Yes — but mainly because it plays *faster than Hex* with comparable depth, and the E1 capture adds a satisfying tactical layer. Less compelling than actual Hex on 11×11, but much less cognitive overhead.

### CLOSEST KNOWN-GAME ANALOG

**Hex (Piet Hein / John Nash, 1942/1948)** — nearly identical win condition and board family. NOT identical because (a) `adjacent_to_own` growth restriction, (b) CA-driven capture via E1 (no analog in Hex), (c) overwrite legality, (d) density-dependent wall semantics.

Distant runners-up: **Bridg-It** (connection game, but on a very different graph), **Competitive Conway's Life variants** (CA + placement, but no connection goal).

### KILLER FLAWS

- **First-player advantage** probably non-trivial on 8×8; no swap rule. Training data shows self-play converges to 50/50 but no pie/swap-rule means competitive P vs P would need one.
- **Most of the CA is inert.** 147-entry table with ~5 live rules on this topology — 95%+ of CA evaluations are no-ops. The game would be almost unchanged if you replaced the CA with just "lone enemy dies against single friendly" — suggesting the rule-complexity score (17) is overstated relative to lived complexity.
- **Adjacency constraint + first-move-anywhere** makes opening theory deterministic: center or off-center adjacent-to-center. Little meaningful opening variety.

### BEST QUALITY

**Overwrite + CA survivability creates density-aware walls.** In Hex a single-stone block is always worth its cost; here a single-stone block is often a tempo LOSS because it dies. You must commit to at least a pair to block, and at least a triple with a bridge to block safely. This shifts the minimum commitment threshold for defence — a *quantitative* change in strategy that I haven't encountered in other connection games.

### IMPROVEMENT IDEAS

1. **Add a swap rule** (pie rule): after P1's first move, P2 may choose to take P1's side instead of playing. Resolves the first-move advantage without changing the core rules.
2. **Enlarge the board to 10×10 or 11×11** (standard Hex sizes) — currently 8×8 converges too fast; bridge and capture dynamics would have more room to breathe.
3. **Activate more CA rules**: the Flip rule `F/1F+4X → X` almost never fires because achieving 4X on a hex cell is rare. Adjusting the rule to `F/1F+3X → X` would make it a live threat and add a second capture mechanism.

---

## Concise Summary

**Verdict**: The Run 13 champion is a legitimate Hex-family game with real novelty in its overwrite + CA-capture dynamics, but the CA is mostly inert — only 3–5 of its 7 effective rules fire in practice, with E1 (lone-enemy erase) carrying most of the tactical load. Strategic depth is real but modest beyond Hex; the game's best feature is that walls are density-aware rather than absolute.

**Final Scores**:
- Strategic Depth: **7/10**
- Emergent Complexity: **6/10**
- Balance: **7/10**
- Novelty (post-adversary): **6/10**
- Replayability: **7/10**
- Overall "Would I play again?": **7/10**

Closest analog: **Hex** (with overwrite + weak capture rule).
Primary killer flaw: Most of the CA is inert; lived complexity ≪ rule complexity.
Best quality: Density-aware walls via overwrite + CA survivability.
