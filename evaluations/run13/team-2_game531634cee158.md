# Genesis Run 13 — Team-2 Evaluation

- **Team ID**: team-2
- **Game ID**: `531634cee158` (rank 3, GE 0.482)
- **Classification**: CLASSIC (no CA)
- **Training metrics**: ELO 2972, trained-vs-random 0.84, avg game length 71.5, both seeds converge to 0.5 self-play winrate.

---

## Phase 1 — Rule Comprehension

**Topology**: 2D 8×8 hex grid, offset coordinates with row-parity tilt (even row: NW/SW neighbours at (x−1, y±1); odd row: NE/SE at (x+1, y±1)). 6 neighbours per interior cell, 4 at edges, 3 at corners. 64 cells.

**Turn structure**: Alternating, 1 placement per turn. Max 100 turns.

**Action types**: Place only. `action_rule.move_constraint: "adjacent_empty"` is vestigial since movement is disabled.

**Placement**:
- Target = empty cells.
- Constraint = `adjacent_to_own`: every placement after the first must touch at least one friendly stone.
- `first_move_anywhere = True`: a player's very first stone may be placed on any empty cell.
- Pass is always legal (action 64).

**Capture**: `outnumber`, threshold = 3. After placement, each enemy cell adjacent to the placed stone is removed if it has ≥3 friendly neighbours (i.e. at least half of the hex's 6 potential neighbours). **No chain/cascade** — only the placed stone's direct neighbours are tested.

**Propagation**: `none` (the stored strength/decay/radius are dead parameters, unused in V3 when `prop_type == "none"`).

**Win condition**: `territory`, threshold ≈ 0.5475. A player wins immediately if they own > 0.5475 × 64 = 35.04 cells (i.e. ≥ 36 stones). If neither crosses the threshold, a **double-pass** ends the game and the majority of stones wins; majority ties are drawn by `_end_by_max_turns` majority tie-breaker. Max 100 turns also triggers majority scoring.

**Super-ko**: enabled engine-wide (ko violations silently convert to a pass).

**Degeneracy checks**:
- First-move-anywhere prevents the "no legal placement" deadlock that would otherwise strike on an empty board with `adjacent_to_own`.
- Outnumber(3) on hex(6) is a real but high threshold — captures happen only at dense contact lines, not casually. During our three games roughly 3-6 stones were captured per game, which matters for final majority counts but doesn't snowball.
- No dead-win threshold (territory is reachable, though in practice most games end by double-pass majority well before 36 stones).
- **Majority-by-double-pass** gives the game an effective "Go scoring" endgame; not degenerate but exploitable if one side is trailing and both decide to pass. We did not observe a single-move exploit.

---

## Phase 2 — Strategic Play

### Game 1 (P1 = center-expand, P2 = mirror south)

Opening: P1 at (3,3), P2 at (4,4). Both extended into contiguous column-walls. By move 20 the board cleanly split across the row-3/row-4 border — P1 holding the north, P2 the south.
Middle game: P1 wrapped around the east edge (column 7 from row 4 down to row 7), breaking P2's south-side envelopment. P2 responded by squeezing out captures along (3,3) and (4,3).
Endgame: Double pass at move 75.
Final: **P1 34, P2 29 — P1 wins by majority.**

Notable: Captures triggered after about move 55 when dense contact lines formed. P1's (3,3) and (4,3) were captured (outnumber-3 by surrounding P2 stones) but P1 compensated by extending into the empty east corner.

### Game 2 (both players from opposite corners; columnar fill)

Both built rank-0 walls, then fanned down the left (P1) and right (P2) edges, converging toward the centre.
Middle game: near-symmetric fill of columns 0-3 (P1) vs 4-7 (P2). Edge parity mattered: on odd rows (1, 3, 5) the tilt favoured P2, so whenever P2 played (4, odd_row) next to P1's (3, odd_row), the P1 stone already had ≥3 P2 neighbours on its east flank → captured. This lost P1 three stones on (3,1), (3,3), (3,5).
Endgame: Double pass at move 67.
Final: **P1 30, P2 32 — P2 wins by majority.**

Notable: the "parity theft" effect — row-parity in the offset hex creates asymmetric capture risk at a column boundary. The side whose boundary pieces sit in the row orientation that points outward gets captured.

### Game 3 (seat swap; P1 = central cluster, P2 = NW corner)

Opening: P1 at (3,3), P2 at (0,0) — asymmetric corners vs centre. P2 expanded NW-corner outward. P1 clustered centre-right.
Middle game: When P1 pushed into column 4-5 north, P2 answered by wrapping across rows 0-2 and then down the west. By move 40 roughly 2/3 of the board was in P2's orbit.
Endgame: P1 tried to punch down the east corridor; P2 blocked with col-4/5 stones. Double pass at move 65.
Final: **P1 29, P2 30 — P2 wins by majority.**

Notable: Losing tempo in the opening by clustering tightly gave P2 more edge real-estate, which in territory mode matters a lot. P1 did recover captures at (3,2) and (3,3) (stones came back in sight but net-even after exchange) but could not close the territorial gap.

### Cross-game observations

| Game | Moves | Result | Margin | Captures seen |
|------|-------|--------|--------|---------------|
| 1 | 75 | P1 wins | +5 | ≈4 (both sides) |
| 2 | 67 | P2 wins | +2 | ≈3 (P1 lost) |
| 3 | 65 | P2 wins | +1 | ≈4 (both) |

Average length ≈ 69 moves — close to the engine-reported 71.5. The 50/50 trained-agent winrate is consistent with our 1-W/2-L distribution (small sample).

### P1 strategy guide
1. Open central ((3,3) or (4,4)) to maximise potential expansion in all six hex directions before committing to a region.
2. Extend toward an edge corridor early — edges are unrecapturable territory cheaply (fewer neighbours means less outnumber pressure).
3. Avoid committing stones to boundary columns on odd-rows (parity theft); if you must, plan to reinforce (2,odd_row) first so your boundary piece has its own friendly majority.
4. When the board is nearly full, prefer a PASS if you're ahead in raw piece count — double-pass wins on majority without needing to hit the 36-cell threshold.

### P2 strategy guide
1. Do not mirror P1 in the centre; take a corner. Corner cells cost one turn to claim and force P1 to spread toward you.
2. Fill columns symmetrically to P1, but delay your central column commitment one tempo so that when you commit to col 4, P1's col-3 stones already have 2 enemy neighbours and the third you add captures them.
3. Use the row-parity trick on the boundary column: on odd rows the offset puts your stones one step "east of" P1's col-3, so your flank-capture works without extra stones.
4. Mirror passes. If P1 passes while you're ahead, pass immediately.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two clear archetypes emerged:
- **Centre-first sphere** (Game 1 P1): claim (3,3) or (4,4), expand in all directions.
- **Corner-first wedge** (Games 2, 3): claim a corner, grow along two edges.
In our sample the corner strategy won 2/3 games. Centre is more flexible but the corner strategy converts edges (unrecapturable, high territorial value) more efficiently.

**Counter-play**: Definitely. Boundary commitment order is dynamic — you can see your opponent extending toward your border and either reinforce pre-emptively, or skip the column and race around. Captures are infrequent enough that every capture was a deliberate setup, not a random shock.

**Short-term vs long-term tension**: Real. Several times we faced "play an edge cell now for +1 territory" vs "play an interior cell that threatens a capture next turn". The capture trade (lose tempo, gain 2 material swing when successful) vs straight territory gain is the core decision.

**Emergent concepts**:
- **Territory** — first-class, direct from win condition.
- **Tempo** — matters because both sides can only expand from existing stones; reinforcing before committing a boundary flip can deny captures.
- **Initiative** — the player who forces the boundary shape controls where captures can land.
- **Parity asymmetry** — the row-parity of the offset hex creates real asymmetric capture threats.
- **Ko-ish recapture** — not observed in our games but theoretically possible; the super-ko rule silently demotes repeat positions to passes.
- No **influence / groups / ladders** in the Go sense (outnumber-3 doesn't chain like surround capture does).

**Does topology matter?** Enormously. A square-grid (Von Neumann) version would have only 4 neighbours, so outnumber-3 becomes "3 of 4 friendly", capturing is very rare and the game degrades toward deterministic fill. Hex's 6 neighbours is exactly the sweet spot where capture(3) is hard but not impossible. Moore or torus would break it (Moore: capture too easy with 8 neighbours; torus: no edges so no territorial asymmetry).

---

## Phase 4 — Novelty Adversary (MANDATORY)

### Adversary's case: "This is Hex-Go at best, and probably just Othello-on-hex."

**(a) Known-game correspondences**

- **Go**: hex territory + placement + pass-to-end + majority scoring. The entire Phase 2 endgame sequence — pass when ahead, opponent passes, majority wins — is pure Go. Outnumber(3) on hex is a weak, non-chaining imitation of Go's surround capture. One could describe this as "Go with a local outnumber rule instead of liberty rule". An expert Go player's territory-vs-influence instincts would transfer directly.
- **Hex (Piet Hein)**: same 8×8 hex board, same "place stones, adjacent-constrained growth". But Hex has *no captures* and a *connection* win condition; the adjacency-constraint here is a reskin of Hex's natural adjacency. A Hex expert would feel right at home in the topology.
- **Reversi/Othello**: capture-by-outnumbering. Othello flips sandwiched lines; this game removes outnumbered neighbours. A 2-neighbour outnumber on a square grid is literally Othello's flank rule with "remove" instead of "flip". At threshold 3 on hex, the flavour is "Othello where captures are harder but permanent".
- **Gomoku/Pente/Connect6**: no, different win condition.
- **Amazons, LoA, Chameleon, Mancala variants**: no structural match.
- **Life-like CA**: N/A — this is a classic game.

**(b) CA check**: N/A, no cellular automaton.

**(c) Topology transformation**: The claim is that `531634cee158` = Othello + (square→hex) + (flip→remove) + (threshold 2→3) + (territory from piece count) + (`adjacent_to_own` growth constraint borrowed from Go). Under that transformation, every rule lines up with an existing game.

**(d) Hypothesis test**: Would an Othello expert win here?
- Partial yes: Othello experts instinctively play corners and edges, which matches our observed best strategy (corner wedge wins).
- Partial no: the `adjacent_to_own` constraint is unlike Othello — Othello demands flanking lines, here you must grow a contiguous blob. Othello's "parity game" endgame tricks don't apply because there's no forced move.
Would a Go expert win here?
- Partial yes: territory reading and pass-endgame are directly useful.
- Partial no: outnumber(3) doesn't chain, so Go's group life/death reading is useless. Ladders, shicho, ko fights don't occur — captures are one-shot local.

Adversary's strongest single argument: **"This is Hex's board + Othello's scoring + Go's endgame, stitched together. No single mechanic is new; the fusion is just a crossover artefact."**

### Player 1 / Player 2 rebuttal

The rebuttal must point to concrete moments where the three analog experts would each have been misled:

- In **Game 1 around move 20**, the board cleanly split along row 3/4. A Go expert would have diagnosed this as a "settled territory" and passed. But the territorial threshold is 35.04 cells, and each side had only 10 stones — the correct move was to keep playing, because the edge corridors (col 7 for P1, col 0 for P2) were unclaimed and whoever reached them first would tip the endgame by 6-8 cells. Go's intuition about "live territory" fails here because there's no notion of dead stones; every stone counts 1-for-1 until captured.
- In **Game 2 between moves 40-60**, Othello instincts would have said "flip the boundary to turn 3 captures into 3×2=6 swings". But because captures remove (don't flip), and because the `adjacent_to_own` rule means captured enemy cells can be *re-taken but only from one's own adjacent stones*, the actual swing is +1 for attacker and only later -1 for defender if they can reach the cell. The material arithmetic is different from Othello's flip-flop.
- In **Game 3**, a Hex expert opening in a corner and growing two edges would have expected to win via connection, but there is no connection win condition. The entire board fills up and the *density of capture threats along the boundary* — which Hex experts do not think about — determined the 30-29 margin.
- **Row-parity asymmetric capture** (Game 2) has no analog in Othello (square grid, no parity) or Go (chains, not neighbour-counts). This is a genuinely novel emergent feature of offset-hex + outnumber-N.

The combination of six-neighbour hex + threshold-3 outnumber + adjacent-to-own growth + pass-to-majority produces endgames that do not resemble any of Go / Hex / Othello in reading. In particular: **stones grow in blobs (Hex-like), captures are local but non-chaining (Othello-adjacent, not Othello-identical), and majority endgame meets 36-threshold territory endgame (Go-like but with two win paths)**. No single analog player brings the full toolkit.

### Joint resolution

Novelty score: **5/10**. The individual ingredients are all borrowed from well-known games, and the adversary is right that "Hex topology + Othello-lite capture + Go endgame" describes the game. But the combination produces row-parity capture asymmetry and a dual win path (35.04 threshold OR pass-majority) that we did not find in a direct analog. It is not a re-skin of any single game, but it is clearly a hybrid. This scores above pure "X on a hex board" (2-3) but below "genuinely new dynamics" (7+).

---

## Phase 5 — Verdict

**Team ID**: team-2
**Game ID**: `531634cee158`
**Rules Summary**: On an 8×8 offset-hex board, players alternately place stones adjacent to their own (first move anywhere); placing next to an enemy with ≥3 friendly hex neighbours captures it; win by holding >54.75% of cells, or by majority when both players pass.
**Topology**: 2D offset-hex, axis_size 8, 64 cells, 6 neighbours interior.

### SCORES (1-10)

- **Strategic Depth: 7** — Three distinct viable archetypes (centre sphere, corner wedge, contested mid-column). Row-parity capture asymmetry is a real strategic factor. Captures are uncommon enough that every one is earned, not random. Endgame pass-timing is a genuine skill. Loses points for lack of chain/ladder reading and for the adjacency constraint reducing branching late-game.
- **Emergent Complexity: 6** — Territorial splits emerge naturally (Game 1's row-3/4 divide, Games 2-3's column splits). Parity-theft captures along boundaries are a non-obvious emergent consequence of offset-hex + outnumber. No chaining or ko fights, but material-vs-territory trade-offs are real.
- **Balance: 8** — Trained 50/50 in self-play, and our three games came out 1-2 from P1's perspective with margins of 1, 2, 5 — right in the expected zone. No seen first-move advantage or second-move advantage in our sample. The `first_move_anywhere` rule plus symmetric scoring keeps seats fair.
- **Novelty (post-adversary): 5** — Strongest adversary argument: Hex board + Othello-style outnumber + Go territory endgame = hybrid, not invention. Rebuttal: row-parity capture asymmetry and dual-path win condition do not appear in any single analog, but the emergence is modest rather than transformative.
- **Replayability: 6** — Meaningful strategic choices, no degenerate exploit observed, plausible board variety. Limited by only ~64 cells and by the capture mechanic being rare enough that many games devolve into territorial fill.
- **Overall "Would I play this again?": 6** — Yes, pleasant to play, moderately deep, and relatively quick (~70 moves). Not a game I'd choose over Hex or Go if I wanted maximum depth.

### CLOSEST KNOWN-GAME ANALOG
**Mixed ancestry of Hex (board + adjacency-grow constraint) and a capture-enabled 1889 Japanese game "Ninuki-renju" variant or Irensei — but the closest single analog is **Go-on-hex with outnumber capture instead of surround** (a known family of Go variants; this specific parameterisation isn't published).

### KILLER FLAWS
- **None strictly degenerate.** Captures fire but rarely, double-pass-to-majority is standard Go-style.
- Minor: double-pass exploits the majority-scoring endgame rather than forcing players to reach 36 stones. In all three games the win came via double-pass, not via the 35.04 threshold — meaning the published win threshold is rarely the actual win mechanism.

### BEST QUALITY
**Row-parity asymmetric capture at boundary columns.** This is a real strategic wrinkle that emerges from offset-hex geometry + outnumber-3. It is non-obvious, rewards attentive play, and has no direct analog in Hex/Go/Othello.

### IMPROVEMENT IDEAS
Disable the double-pass-to-majority ending (end only at the 35.04 threshold or at max_turns), or raise the territory threshold to something clearly achievable (e.g. 60%) while keeping pass-majority as a drawlike stalemate. This would force players to fight for captures or conquer enemy territory rather than settle for a fill-and-pass endgame, amplifying the outnumber-capture mechanic that gives the game its identity.

---

## Concise verdict

A competent 2D-hex Go/Hex/Othello hybrid with a modest but real emergent feature (row-parity capture asymmetry). Trained agents converge to 50/50 self-play; our three human-driven games landed at +5, −2, −1 margins — all close, all ending by double-pass majority rather than by hitting the territory threshold. No killer flaws, no breakaway novelty. Pleasant and balanced but not publishable.

**Final Scores** — Depth 7 / Emergence 6 / Balance 8 / Novelty 5 / Replayability 6 / Play-again 6.
