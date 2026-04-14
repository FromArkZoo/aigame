# Evaluation — Team-3 — Game 531634cee158 (Run 13)

**Team ID**: team-3
**Game ID**: 531634cee158
**Meta**: Rank 3, GE 0.4818, ELO 2972.2, 2D hex 8×8, outnumber capture (threshold=3), territory win, CLASSIC

---

## Phase 1 — Rule Comprehension

**Topology**: 2D hex grid, 8×8 (64 cells). Hexagonal offset adjacency (6 neighbors per interior cell).

**Turn structure**: Alternating, 1 piece per turn.

**Action**: Place only (no movement). Target empty cells. Constraint: `adjacent_to_own` (must place next to one of your own stones). Exception: first move anywhere.

**Capture (outnumber, threshold 3)**: When you place a stone at X, iterate every enemy stone E that is a neighbor of X. If E has ≥3 of YOUR stones among E's 6 neighbors, remove E.

Key quirks:
- Capture only triggers from placement-adjacency. A stone with 3 enemy neighbors sits "pre-captured" until the enemy places adjacent to it.
- No self-capture check — placing into a spot surrounded by enemies is legal but doesn't die.
- Super-ko rule enforced lazily: moves that recreate prior positions become passes.

**Propagation**: `prop_type: none`. Radius/strength/decay are present but inert.

**Win condition**: Territory — first player to own > 54.75% of 64 cells = **≥36 pieces** wins. Max turns 100. Double-pass ends game by majority (highest piece count wins; equal = draw).

**Degeneracy flags**: None severe. Propagation fields vestigial (bloats rule complexity). The 36-piece threshold is rarely reached cleanly — most games end via double-pass majority.

---

## Phase 2 — Strategic Play

### Game 1 — Thoughtful interactive play (77 moves)

Opening: P1 center (3,3), P2 (4,4). Row-3 vs row-4 mirror race developed. Heavy tactical fighting between moves 6-17, including:
- Move 7: P1 (6,4) captures (5,4) (outnumber, 3 X-neighbors)
- Move 8: P2 (2,3) captures (3,3)
- Move 10: P2 (5,4) retaken (no capture)
- Move 15: P1 (2,2) captures (2,3)
- Move 16: P2 (2,3) captures (3,3)
- Move 17 — **SUPER-KO**: P1 played (3,3) aiming to capture (2,3), but the resulting position repeated move-11 state, so the move became a pass. Real ko enforcement observed.
- Move 18: P2 (3,3) captures (4,3) (no ko conflict for P2)

From move 20 onward, both players expanded into empty territory. Clear territorial split emerged: P1 owns top-half, P2 owns bottom-half. Border skirmishes at (3,2)/(4,2) traded captures 3 times.

Final: P1 32, P2 29. Game ended by double-pass → **P1 wins by majority**.

### Game 2 — Random playout (seed 42), 84 moves

Clean vertical split. No super-ko triggered. Multiple small captures at borders. Final 34-30, **P2 wins by majority** via double-pass.

### Game 3 — Random playout (seed 7), 81 moves

P1 hit the territory threshold cleanly: final board showed P1=36 pieces. **P1 wins by territory threshold (not by double-pass)** — the first game where the win condition triggered without exhaustion.

### Game 4 — Random playout (seed 100), 84 moves

Perfect horizontal split at rows 3/4. Final **32-32 DRAW**. Demonstrates genuine equilibrium.

### Strategy guide — Player 1 (first mover)

- Take center (3,3) first move. Creates 6 expansion directions.
- Mirror or pressure P2's expansion. Avoid long linear stone rows near enemy (each stone gets 2+ enemy neighbors quickly → outnumber vulnerability).
- Watch for "fragile" stones (enemy stone with 3 of your neighbors). Place adjacent to trigger capture.
- Defend fragile OWN stones by capturing their attackers or by occupying the remaining empty adjacency (deny the capture trigger square).
- Endgame: claim as much empty space as possible, then pass. Ties go to nobody.

### Strategy guide — Player 2 (second mover)

- Don't mirror literally; P1 already has central tempo. Instead play 2-away adjacent (e.g., P1 (3,3) → P2 (4,4) or (5,5)) to contest without immediate contact.
- Prioritize territory building over captures early. Captures are expensive tempo-wise and reversible.
- Watch for double-threat moments where P1 can capture in two places. Choose the more strategically central save.
- Know the super-ko rule — if you capture in a ko shape, P1 cannot immediately recapture.

---

## Phase 3 — Strategic Analysis

**Viable strategies (multiple observed)**:
1. Central rush + expand
2. Flank race (mirror expansion, minimize contact)
3. Contact fighting (seek captures)
4. Boundary entrenchment (build a wall, claim half the board)

No single strategy dominates; all four games resolved differently (thoughtful P1 win by majority, random P2 win, random P1 win by threshold, random draw).

**Counter-play**: Yes. A placement adjacent to an enemy's fragile stone forces the enemy to defend. Defender can counter by capturing the attacker first (if positioning allows) or by occupying the threat square.

**Short vs long-term tension**: Moderate. Capturing a stone gains +1 immediate material but costs a turn (attacker could have placed elsewhere to expand territory). Observed repeatedly in Game 1 that ko-like recapture cycles cost both players tempo.

**Emergent concepts**:
- Territory and influence
- Tempo and initiative
- Fragile/pre-captured stones (unique to outnumber mechanic)
- Ko fights (enforced via super-ko-as-pass)
- Border skirmishes and equilibrium frontiers
- Genuine draws (32-32)

**Topology matters**: Hex gives 6 neighbors vs 4 on a square grid, making the "threshold 3" more tractable (half the neighborhood). On a square grid with 4 neighbors, threshold=3 would require 75% enemy encirclement — captures would be much rarer. Hex geometry sits in the tactical sweet-spot.

---

## Phase 4 — Novelty Adversary (MANDATORY)

### Adversary argument

**Strongest claim**: "This is Go-on-hex with the liberty-capture rule replaced by an outnumber-3 threshold, and area scoring replaced by piece count. Under a straightforward rule transformation (liberty=0 → outnumber≥3), an expert Go player has >70% intuition transfer."

Specific correspondences:
- **vs Go**: 2D grid placement, alternating turns, territorial endgame, ko rule, capture by adjacency. Differences are in the capture geometry only.
- **vs Othello**: Outnumber-based capture (flanking in Othello, threshold-count here). Both place-only games. Othello has forced captures; this has conditional.
- **vs Hex**: Hex board, first-move advantage, placement-only. But Hex wins by connection; this wins by area — weaker analog.
- **vs Havannah/Y**: Hex placement. Different win conditions.

No match with Reversi (different capture), CA games (no CA), Amazons (movement), LoA (movement), Mancala (sowing), Nim (pile removal).

### Player rebuttal

Concrete moments from Phase 2 where Go/Othello intuition breaks:

1. **Game 1 move 17 ko**: Super-ko enforcement-as-pass is mechanically different from Go's positional super-ko (where the move is simply illegal). A player transferring Go ko intuition would try to play the move; here the engine silently converts it to a pass, costing a tempo.

2. **Game 4 (seed 100) 32-32 draw**: Go virtually never draws under area scoring because of dame and seki handling. Othello draws are possible but rare. This game produces honest symmetrical draws because piece-count territory + double-pass has no tiebreaker.

3. **Isolated-stone immortality (observed in all random games)**: Single stones in enemy territory cannot be captured by outnumber because they have no FRIENDLY neighbors — and capture requires ≥3 OF YOUR OWN stones around an enemy. Isolated enemy stones sit forever. In Go, a lone stone in enemy territory is typically dead. This inverts Go's invasion logic.

4. **Pre-captured fragile stones** (Game 1 moves 14-17): A stone sitting with 3 enemy neighbors is "walking-dead" until triggered. This state is qualitatively different from Go (no analog; Go uses the stone's OWN liberties) and from Othello (no lingering state; captures are immediate on placement).

5. **No eye/life concept**: Go expert's primary mental tool (eye-shape, life-and-death) does not apply. Here, group survival depends on enemy stone density around each cell, not on internal eyespace. The opening and middlegame feel quite different in practice.

6. **First-move anywhere + adjacent-to-own constraint**: Forces contiguous growth from a single seed, somewhat like **territorial empire games** (Takenoko? Blooms?) rather than pure Go.

### Novelty resolution

Adversary's strongest point stands partially: the territorial framing IS Go-like, and tactical adjacency fighting transfers from Go/Othello. However, the outnumber-3 mechanic generates genuinely distinct dynamics:
- Isolated stones are immortal (inverts Go invasion)
- Pre-captured "walking-dead" stones (no Go/Othello analog)
- Lazy super-ko-as-pass (distinct enforcement)
- Natural 32-32 draws (uncommon in analogs)

**Novelty score: 4/10** — closer to "Go/Othello hex hybrid with one distinctive twist" than "genuinely novel." A Go player would have a real head start but would make concrete mistakes within the first few games.

---

## Phase 5 — Verdict

**Team ID**: team-3
**Game ID**: 531634cee158
**Rules Summary**: 2D hex 8×8 placement game. Outnumber-3 capture: place next to an enemy stone that has ≥3 of your neighbors to remove it. Win by owning 36+ of 64 cells, or by majority at double-pass.
**Topology**: 2D hex, 8×8, 64 cells, 6 neighbors per interior cell.

### SCORES (1-10)

- **Strategic Depth: 6** — Multiple viable strategies (central rush, flank race, contact fighting), meaningful tempo decisions, genuine tactical motifs (fragile stones, double threats, ko fights). Shallower than Go because no eye/life logic; deeper than Othello because groups matter and territory is contested over many turns.

- **Emergent Complexity: 6** — Territory, tempo, ko, pre-captured stones, isolated-stone immortality, border equilibria all emerge. Lacks connection goals or long-range tactical patterns, but the outnumber mechanic produces rich local fights.

- **Balance: 7** — Training win rate 50%, hand-played game 1 went to P1 by majority, random games split 1 P1 / 1 P2 / 1 draw. No structural first-move exploit; first-move-anywhere on a hex gives P1 a modest center advantage offset by P2's second-move response flexibility.

- **Novelty (post-adversary): 4** — Strongest adversary argument: Go-on-hex with outnumber capture. Strongest rebuttal: isolated stones are immortal, pre-captured walking-dead states, and natural draws differ qualitatively from Go/Othello. Net: a Go/Othello hybrid with one genuinely distinctive mechanic, but not a fundamentally new paradigm.

- **Replayability: 6** — 4 games produced 4 different outcomes (P1 win by majority, P2 win by majority, P1 win by threshold, draw). Territorial frontiers settle differently depending on opening choices. Would stay interesting for 10-20 plays; might get stale sooner than Go due to limited group-life tactics.

- **Overall "Would I play this again?": 6** — Solid enough to play casually. Not tournament-worthy but clearly above the "broken game" threshold.

### CLOSEST KNOWN-GAME ANALOG

**Go on a hex board**, with the liberty-based capture rule replaced by an outnumber-3 threshold and territory defined as piece count rather than enclosed empty regions. Also draws influence from Othello's outnumber-capture flavor. Not identical because: (a) isolated stones are immortal (no Go analog), (b) pre-captured "walking-dead" stones persist (no Go/Othello analog), (c) honest draws are common (rare in Go area scoring).

### KILLER FLAWS

- **Propagation fields inert** (prop_type=none but radius/strength/decay set) — inflates rule complexity without gameplay effect.
- **Territory threshold rarely triggers naturally** (observed only once in 4 games). Most games resolve via double-pass majority, which is a weaker termination than an explicit win condition.
- **Isolated-stone immortality** can feel degenerate late-game when an isolated stone locks up a cell the majority owner can never claim back.
- **Capture threshold=3 on hex** means captures are relatively infrequent — the game is more "placement race" than "tactical fighting." Slight tuning issue.

### BEST QUALITY

**The outnumber-3 mechanic on hex produces a distinctive "walking-dead stone" state** that doesn't exist in Go or Othello. A stone with 3 enemy neighbors is pre-captured but persists until triggered by adjacent placement — this creates strategic tension around "fragile squares" and "trigger squares" that feels genuinely different from Go's liberty counting or Othello's forced flanking.

### IMPROVEMENT IDEAS

**Increase the hex capture threshold to 4, OR introduce a "self-outnumber" rule** (a cell with 3 enemy neighbors is removed on the NEXT opponent turn automatically, not just on adjacent placement). This would:
- Force decisive commitment on walking-dead stones rather than leaving them lingering.
- Reduce the "isolated stone immortality" degeneracy (isolated stones would still be safe, but group fragments would fall faster).
- Push more games to the 36-piece threshold rather than double-pass majority.

Alternative: shrink to 7×7 hex so the 36-piece territory threshold becomes easier to cleanly hit, making the win condition more active.

---

## Final Scores Summary

| Dimension | Score |
|---|---|
| Strategic Depth | 6 |
| Emergent Complexity | 6 |
| Balance | 7 |
| Novelty (post-adversary) | 4 |
| Replayability | 6 |
| Would I play again? | 6 |

**Verdict**: A competent Go-on-hex / Othello-flavored hybrid with one distinctive mechanic (outnumber-3 creating walking-dead stones). Not groundbreaking but structurally sound. GE=0.4818 and ELO=2972 are defensible. Falls well short of being "publishable-novel" but clearly above broken/degenerate. 6/10 overall.
