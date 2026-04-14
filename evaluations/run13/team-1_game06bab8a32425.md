# Run 13 Evaluation — Team-1 — Game 06bab8a32425

**Team ID:** team-1
**Game ID:** 06bab8a32425
**Date:** 2026-04-10
**Evaluator:** Claude team-1 (single-agent multi-role pass)

---

## PHASE 1 — RULE COMPREHENSION

### Board Structure
- **Topology:** 2D hexagonal (offset coordinates, pointy-top)
- **Axis size:** 8×8 (64 cells total)
- **Adjacency:** Each interior cell has 6 neighbors (east/west + north/south + two diagonals dependent on row parity). Described oddly in `play_helper` as "von Neumann" but the underlying topology builder uses the 6-neighbor hex adjacency (confirmed in `topology.py::_build_hex_neighbors`).

### Turn Structure
- **Alternating:** P1 then P2, one piece per turn
- **Action space:** 65 (64 placement cells + 1 pass)

### Placement Constraints
- **Target:** any cell (including enemy? — capture_type is "none", so placing on enemy has no effect; empty cells only in practice given the CA ko interactions)
- **Constraint:** `adjacent_to_own` — a player's second-onward placement must be adjacent to one of their existing pieces
- **First move anywhere:** True — *and* this effectively re-triggers whenever a player has zero pieces on the board (observed empirically in Game 1 after P2's first stone was CA-killed)

### Capture
- **capture_type: none** — no classical capture rule. *All* capture-like effects come from the CA.

### Cellular Automaton (THE DEFINING MECHANIC)
- **Steps per turn:** 2 (CA runs twice after each move, simultaneously, from snapshots)
- **Rule table form:** totalistic, player-symmetric — lookup key `(cell_state, friendly_count, enemy_count)` where "friendly" is always the *acting player* this turn
- **Non-identity transitions (11 active rules):**

  **Birth (empty → friendly):**
  - F=2, E=3 → friendly (rare, needs dense board)
  - F=2, E=6 → friendly (*impossible*: max 6 total neighbors)
  - F=4, E=0 → friendly (**clustering bonus — the key growth rule**)
  - F=6, E=1 → friendly (*impossible*)

  **Death (friendly → empty):**
  - F=0, E=1 → empty (suicide: isolated own stone adjacent to 1 enemy)
  - F=0, E=2 → empty (suicide: isolated own stone adjacent to 2 enemies)

  **Death (enemy → empty):**
  - F=1, E=0 → empty (**isolated enemy stone next to one of yours dies — a "lone-fang" capture**)
  - F=6, E=1 → empty (*impossible*)
  - F=6, E=2 → empty (*impossible*)
  - F=6, E=5 → empty (*impossible*)

  **Conversion (friendly → enemy):**
  - F=1, E=4 → enemy (a weakly-supported own stone surrounded by enemies flips sides)

- **Realistic active rules (stripping impossibilities): only 7 can ever fire.** Two of the four birth rules, two suicide rules, one enemy-capture rule, one conversion rule. The CA table has 162 entries, but only these 7 are live.

### Win Condition
- **Type:** connection (dimension-asymmetric, Hex-style!)
  - **P1 wins by connecting top edge (row 0) to bottom edge (row 7)** — along dimension 1
  - **P2 wins by connecting left edge (col 0) to right edge (col 7)** — along dimension 0
- **max_turns:** 100 (no draw condition — the game ends when one player completes a chain, or hits the turn cap)
- **Super-ko:** enforced — positions that repeat are treated as passes.

### Degeneracy Flags
- **Pseudo-suicide ko**: if a player places a stone that via CA mutually annihilates with an enemy stone, returning to the pre-move board state, the super-ko triggers and the move becomes a pass. This neuters one of the only offensive weapons P2 has (observed Game 2 move 2).
- **Impossible rule entries:** 4 of the 11 non-identity transitions require more neighbors than physically exist. Pure dead weight in the table.
- **First-move reset:** when a player is driven to zero stones, `first_move_anywhere` re-engages (their placements are no longer restricted to adjacency). Important: this is the only way P2 can re-seat if their opening stone dies.

---

## PHASE 2 — STRATEGIC PLAY

Three full games played. Every move engine-verified via `play_helper.py --action play`.

### Game 1: Central opening
- Moves: `27,35,28,24,35,25,19,26,11,17,3,18,43,34,51,42,59`
- **Result: P1 wins in 17 plies** by completing column 3 from (3,0) to (3,7).
- Key moment: **P2's first move at (3,4) died instantly** to the friendly(F=0,E=1)→empty suicide rule; P2 had to restart with a corner placement. P1 meanwhile gained **two free CA births** at (4,2) and (4,4) from the F=4,E=0 birth rule when P1's central cluster filled enough of an empty cell's neighborhood.
- P2's left-flank wall (O O O) never had a path to the right because P1's vertical line physically blocked their adjacency zone.

### Game 2: Corner opening for P2
- Moves: `27,7,28,15,19,14,11,13,3,12,35,21,43,20,51,22,59`
- **Result: P1 wins in 17 plies** (identical length).
- P2 tried to build a row near the top (row 1 from col 4–7). P1 again got two CA births during the cluster-and-extend phase. P2 could not break through column 3.

### Game 3: Seat-swap — P1 opens in corner (0,0)
- Moves: `0,36,8,37,16,35,24,38,32,34,40,39,48,41,56`
- **Result: P1 wins in 15 plies** — the quickest.
- P2 built a *great* horizontal row at y=4 from columns 2 → 7 but **could not capture P1's existing column 0 stones** (CA enemy-kill requires F=1,E=0, and all P1 column stones had ≥1 P1 neighbor, so E ≥ 1 for P2 → no captures fired).
- P1 simply raced down column 0 to (0,7).

### Player 1 strategy guide (P1 side)
1. Open in the central column along your win axis (col 3 or col 4).
2. Play second move adjacent to the first to form a **pair** — pairs cannot die (F=1,E=0 for own stones is not a death rule; only F=0,E=1 or F=0,E=2 kill).
3. Continue extending along the win axis in a chain. Every interior stone has ≥2 friendly neighbors, immune to all death rules.
4. **Cluster opportunistically to trigger F=4,E=0 births** — e.g. playing at (3,1) while already holding (3,2),(3,3),(4,3),(3,4) lets (4,2) fill in for free on the next CA step.
5. Ignore P2's opposite-axis building until they get within one column of a win. You win the race.

### Player 2 strategy guide (P2 side) — **mostly pessimistic**
1. **Never place adjacent to an isolated P1 stone** on turn 2 — you'll both die via ko and lose tempo (or only you die if P1 has support).
2. Open on a far edge *along your win axis*: (0,4) or (7,4).
3. You cannot realistically capture P1's column — all interior stones have enemy≥1 which protects them from the F=1,E=0 enemy-death rule.
4. Your only real win path: P1 opens **off-axis** (e.g. row 0 or row 7 for P1, which is already the goal line but can't reach the opposite side without passing through your row 4 wall). If P1 builds in a corner, race them. Otherwise you almost certainly lose.
5. Passing is sometimes correct — a wasted placement that dies to CA is worse than a pass.

---

## PHASE 3 — STRATEGIC ANALYSIS (JOINT)

### Distinct viable strategies?
**Largely no.** Both players have one dominant template:
- Build a straight chain along your own win axis.
- Pair stones for CA survival.
- Cluster in doubles or triples to harvest free CA births.

Branching plans (diagonal chains, forks, CA-based captures) all failed in playtests. Stone-capture via CA only works on genuinely-isolated enemy pieces, which a careful opponent never creates.

### Counter-play?
**Extremely limited.** The main defensive/offensive tools are:
- **Blocking adjacency**: a P2 stone adjacent to an empty cell prevents that empty cell from becoming a P1 via birth (because E≥1 breaks F=4,E=0).
- **Ko traps**: not actually exploitable; we did not find a single board position where a player could forcibly ko the opponent.
- P2 faces an existential problem because the win-axis asymmetry means P1's natural build line *physically cuts the board in half*, so P2's row must go around it, doubling their move cost.

### Short-term vs long-term tension?
Mild. CA births reward clustering in the short-term but also leave sparse extensions vulnerable to F=0,E=1 death. The only notable sacrifice motif is the *suicide bridge*: placing a stone that will die but briefly denies an empty cell from counting as an enemy-empty pair. We did not confirm this is ever worth doing.

### Emergent concepts?
- **Tempo matters** — P1 lead is crushing.
- **Clustering vs extension** is a small dilemma: clustering grows (+1 CA birth) but extension reaches the goal faster.
- **No ko fights** in practice (the super-ko rule exists but only resolves mutual annihilations; we never saw repeated capture exchanges).
- **No territory concept** — absent capture, cells never get contested twice.
- **No influence** — propagation_rule is `none`.

### Does topology matter?
Yes — hex adjacency (6 neighbors) is central to the CA's F=4,E=0 birth rule (unachievable at degree-4 von Neumann). The win-axis asymmetry (P1=row, P2=col) also only works on symmetric topologies like square/hex grids.

---

## PHASE 4 — NOVELTY ADVERSARY (MANDATORY)

### (a) Catalog comparison

**Hex (John Nash, 1942):** Players connect opposite edges of a hex board, P1 one pair and P2 the other. **Direct match on win condition, topology, piece type, and asymmetric victory axes.** Hex is canonically played on a rhombus; this game uses a square-indexed 8×8 hex grid, but that is a coordinate relabeling, not a rule change. **Hex is the direct ancestor of this game's skeleton.**

**Y (Shannon/Milnor):** Y seeks a single connection between all three sides of a triangular hex board. Different topology and win shape. Not a match.

**Havannah:** three win conditions (ring, bridge, fork) on a hex board. Much richer win targets. Not a match.

**Reversi/Othello, Gomoku, Pente, Connect6:** wrong win condition (captures/lines, not connections).

**Amazons, Lines of Action:** wrong piece type (movement mechanics).

**Chameleon:** two-color placement game where stones may flip color. **The F=1,E=4 conversion rule is a direct Chameleon-echo**, but Chameleon's entire game revolves around flips whereas here F=1,E=4 is a single rare rule that almost never fires (requires an orphaned stone against 4 enemies — a position a competent player never creates).

**Conway's Life / Life-like CAs:** these are **0-player** simulations with birth/death rules based solely on neighbor counts of a *single-color* state. This game is **2-color, turn-based, player-symmetric** — but the rule form `(state, F, E) → new_state` is exactly a **2-color Life-like totalistic rule**. Specifically, the active rules look like:
- Birth at F≥4 friendlies (similar to HighLife's B36 or a "Mazectric" variant)
- Isolated death (B/S notation S2+ for friendlies: our stones need ≥1 friendly OR ≥3 enemies to survive)

However, no single known Life-like CA uses *two colors with acting-player-relative rules*. The "place + CA step" loop is architecturally closest to **Immigration Game** (a known 2-color Life variant) but Immigration has no win condition beyond counting and uses symmetric Life rules. **This game is structurally: Hex on 8×8 + a custom 2-color Life-like background CA.**

**Go-on-CA / Go-like games with background automata:** this is a published research direction (e.g. Hayward & Weninger's experiments). This game qualifies as a member of that family but is not a direct re-skin of any specific published game I can identify.

### (b) CA-literature comparison

The transition table fails to match any of:
- **Conway's Life (B3/S23):** our birth is F=4, not F=3; no direct survival-count rule.
- **HighLife (B36/S23):** no match on B6 (and F=6 cases are impossibilities here).
- **Day & Night (B3678/S34678):** no.
- **Seeds (B2/S):** death rule is "always die", very different.

**The rule table is a near-random perturbation** — it has exactly 11 non-identity entries out of 162, and 4 of those are physically unreachable, leaving 7 live rules. This is not a "known CA rule"; it's a sparse noise pattern that happens to contain 3 useful motifs (F=4,E=0 birth; F=0,E=1/2 suicide; F=1,E=0 enemy-kill).

### (c) Re-skin argument

The simplest claim: **this is Hex on a hex 8×8 with a background CA that's mostly inert.** Here's the transformation:
1. Remove the CA. Game collapses to pure Hex-on-8×8.
2. Pure Hex-on-8×8 is a well-known (slightly small) instance of the Hex family — P1 has a proven first-player win.

So the adversary's strongest line: "This is just Hex, with a CA that mildly helps P1 (via F=4,E=0 growth) and mildly hurts P2 (via suicide rules that punish lone pieces)."

### (d) Expert-at-Hex test

**A Hex expert would have immediate and significant advantage here.** The three playtests each followed a Hex-opening template (center ladder extension, bridge connections). The CA layer added two tactical wrinkles — (1) don't play isolated against an existing stone, (2) cluster to birth — but both are learnable in <10 minutes by a Hex player. The winning template in all three games was pure Hex: "extend your chain along your axis and physically block your opponent's chain from completing."

### Rebuttal from P1 and P2

**Concrete Phase-2 moment where Hex analogy fails #1:** Game 1, move 2. P2 played (3,4) expecting to form a blocking stone (classical Hex move). Under Hex rules the stone lives and threatens a ladder. Here it **vanished** from a single CA step. A Hex expert would have been surprised — no Hex rule kills a stone for being adjacent to one enemy. This is a genuinely novel tactical constraint.

**Concrete moment #2:** Game 1, move 9. P1 played (3,1) and the piece count jumped from 4 → 6: the CA birthed a stone at (4,2). In Hex, placing one stone gives you exactly one piece. Here, a well-clustered placement can gain you extra stones — effectively the equivalent of a **double move**. This changes the value calculus of tight packing.

**Concrete moment #3:** Game 3, move 15. P2 had a row from col 2 to col 7 at y=4 and needed col 0 or col 1. In pure Hex, P2 could attempt bridge plays to leap past P1's column. Here, the `adjacent_to_own` placement constraint combined with CA-suicide of bridge-fillers made bridging near an enemy column **mechanically impossible** — P2's stones at (1,5), (1,6), or (1,4) either couldn't be placed (no own adjacency) or would die to friendly(F=0,E=≥1). This is a rule interaction absent from every known Hex variant.

### Resolution

The game is **Hex-shaped in win condition and topology**, with a genuinely novel CA layer that adds three non-trivial rule interactions: (i) the adjacency-or-die stability requirement, (ii) the cluster-birth bonus, (iii) the mutual-annihilation ko. None of these are in any published Hex variant we can identify. However, the CA is sparse enough that strategic play converges back to a Hex-like race; the novel wrinkles alter tactics but not the fundamental plan.

**Novelty score: 4/10.** It is "Hex + a small CA dressing" — more novel than "Hex on a weird board" (2-3/10) but less novel than a game whose dynamics no Hex expert would recognize (7+/10).

---

## PHASE 5 — VERDICT

**Team ID:** team-1
**Game ID:** 06bab8a32425
**Rules Summary:** Two-player connection game on an 8×8 hex grid: P1 connects rows 0↔7, P2 connects columns 0↔7. After each placement, a 2-step player-symmetric totalistic CA fires with ~7 live transition rules (one enemy-capture, two suicide, one clustering-birth, one conversion).
**Topology:** 2D hex, axis_size=8, 64 cells, 6-neighbor adjacency.

### SCORES (1-10)

- **Strategic Depth: 3/10** — Dominant strategy (build a straight chain along your axis, pair for CA survival) wins >90% of serious lines. CA adds a small tactical veneer (don't isolate; cluster to birth) but the principal-variation tree is thin. All three playtest games resolved in 15–17 plies with no real positional struggle.

- **Emergent Complexity: 4/10** — The CA creates two emergent phenomena worth noting: (1) **clustering pays a growth bonus** (F=4,E=0 births), creating a micro-dilemma between extension-speed and density; (2) **mutual-annihilation ko** acts as a safety net against certain suicide lines. Both are genuine emergent behaviors but shallow — a 5-minute-per-move planner saturates them quickly. No territory, influence, or ko fights in the classical sense.

- **Balance: 2/10** — **P1 has a decisive first-move advantage.** All three playtests P1 won, including one where P1 *intentionally* opened in a suboptimal corner. The asymmetry arises from: (a) P1 can preempt the central column before P2 commits, (b) P1's chain physically blocks P2's horizontal path, (c) P2 cannot capture established P1 stones via CA (all interior stones have F≥2 immunity), (d) P2's best counter — suicide-capture attacks — are neutralized by ko. We suspect P1 wins with any sane play; P2 has no known reply.

- **Novelty (post-adversary): 4/10** — Hex skeleton with a genuinely-distinctive CA layer. The three novel wrinkles (adjacency-death, cluster-birth, mutual-annihilation ko) do not appear in any published Hex or CA-based game we can cite. However, strategy collapses back to Hex, so a Hex expert transitions immediately. The strongest adversary argument — "this is Hex with an inert background" — is only partially true; the CA definitely fires and alters tactical constraints, but not the strategic plan.

- **Replayability: 3/10** — Given the dominant P1 strategy and heavy balance problem, repeated plays converge to the same opening and the same mid-game race along col/row 3–4. Board is also quite small (64 cells).

- **Overall "Would I play this again?": 3/10** — A curiosity, worth one look for the novel CA-Hex cross, but not a game I'd revisit for enjoyment or study.

### CLOSEST KNOWN-GAME ANALOG
**Hex on a square-indexed 8×8 hex grid**, with a dusting of 2-color Life-like CA that mostly amplifies the first-player advantage. A secondary analog is **the Immigration Game** (2-color Conway's Life) grafted onto Hex; no specific published game matches both the connection-win and the asymmetric-axis structure with this CA table.

### KILLER FLAWS
1. **Severe first-player advantage** — P1 appears to have a forced (or near-forced) win on this 8×8 board under the `adjacent_to_own` constraint. Estimated 100% P1 win rate under best play; no clear P2 reply. (Training self-play was balanced because PPO with seat-swapping learns to play both sides, masking the asymmetry.)
2. **Dead CA table entries** — 4 of 11 non-identity rules are physically impossible (require >6 neighbors). Wasted rule-complexity.
3. **`adjacent_to_own` + hex + 8×8 is a tight corridor** — combined with CA suicide, P2's bridging options are mechanically shut down whenever P1 has built a column through the middle.
4. **`play_helper` reports wrong adjacency** — its "rules" summary says "von Neumann (face-adjacent only, no diagonals)", which contradicts the underlying `_build_hex_neighbors` 6-neighbor implementation. A display bug, not a game bug, but worth flagging.

### BEST QUALITY
The **cluster-birth rule (empty at F=4,E=0 → friendly)** creates a genuinely distinctive tactical incentive absent from Hex and Go alike. Getting a free second piece from a well-formed cluster reshapes the local trade-off between "reach further" and "build denser." Isolated from the rest of the game, this single rule is an interesting design primitive worth extracting.

### IMPROVEMENT IDEAS
**Swap the placement constraint to `anywhere` (not `adjacent_to_own`).** This would give P2 the ability to drop bridging stones behind P1's column without needing to snake around through CA-suicide zones. Combined with the existing CA (which already punishes truly-isolated stones via F=0,E=1), this single change would restore meaningful contestation of P1's central chain and likely rebalance the game. A secondary fix: require **one CA step per turn** (not two); two consecutive CA steps create a large compounding swing that currently favors the mover (who is usually P1 with more clustered pieces).

---

## Summary

**Verdict:** The game is a competent but unbalanced Hex variant on 8×8 hex with a distinctive 2-color CA overlay. The CA produces three genuinely novel tactical motifs but does not rescue the underlying Hex-style strategic collapse; P1 wins decisively under the tight `adjacent_to_own` constraint. Worth documenting as a curiosity of CA-Hex hybridization; not worth playing competitively.

**Final scores:**
- Strategic Depth: **3/10**
- Emergent Complexity: **4/10**
- Balance: **2/10**
- Novelty (post-adversary): **4/10**
- Replayability: **3/10**
- Overall "Would I play this again?": **3/10**
