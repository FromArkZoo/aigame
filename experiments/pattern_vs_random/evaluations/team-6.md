# team-6 evaluation — pattern-vs-random probe

**Team ID:** team-6
**Game order played:** fractal → structured → random → grid
**Seat assignments:**
- Player1-persona: seat-1 in games {1,3} (fractal, random); seat-2 in games {2,4} (structured, grid)
- Player2-persona: mirrored — seat-2 in games {1,3}; seat-1 in games {2,4}

(Each persona gets 2 games per seat — clean 2-2 split. Engine "P1" always moves first.)

## Phase 1 — Rule comprehension

All four candidates share an identical ruleset: alternating turns; surround-capture (Go-style, threshold=1, no propagation, no CA); single placement per turn with first-move-anywhere; connection win condition (P1 = chain from x=0 face to x=axis-1; P2 = chain from y=0 face to y=axis-1; max 100 turns). The only differences across the four files are `topology_type`, `axis_size`, and `holes`. Every condition has 64 active placement cells and is face-connected, so connection-win is feasible on each.

## Phase 2 — Strategic play

### Game 1: pat_fractal (23 moves, P1 win, decisive)

**Opening (M1–M16) — column-2 vs row-2 contest.**
- M1 P1 (4,2): central commit on a clean LR row.
- M2 P2 (2,4): central commit on a clean TB column.
- M3–M6 each side extends adjacent cells on their target line (P1 row 2, P2 col 2).
- M7 P1 (2,2): wedge between P2 stones at (2,1) and (2,3). The 3×3 center hole at rows 3–5/cols 3–5 means P2 cannot easily flank around (2,2); the hole geometry rewards the wedge.
- M8 P2 (2,1): claims the col-2 north-of-wedge cell.
- M9 P1 (1,2): extends row 2 west.
- M10 P2 (2,6): on fractal, (2,1) still has 2 liberties (cell (3,1) is *active* on fractal because row-1 holes are at x=1,4,7 only). P2 chose to extend col-2 south rather than defend.
- M11–M15: P1 fills row 2 from x=2 to x=8 (reaches x=8 face). P2 mirrors on col 2.
- M16 P2 (0,2): blocks P1's only row-2 extension west.

**Tactical phase (M17–M23) — corner-capture sequence.**
- M17 P1 (1,3): bridge stone — also creates capture threat against (0,2). On fractal, (1,3) is *active* because the central hole is rows 3–5 cols 3–5; outside that, (1,3) is a clear cell.
- M18 P2 (0,3): defends — joins (0,2) for 2 liberties.
- M19 P1 (0,5): **hole-aware tactic.** Plays *outside* the immediate fight to remove (0,4)'s future escape: on fractal, (1,4) is a hole, so (0,4) has only one liberty in the (0,5) direction. By taking (0,5) first, P1 guarantees that any later P2 stone at (0,4) will be dead.
- M20 P2 (0,4): tries to extend the corner group; this puts the {(0,2),(0,3),(0,4)} chain into atari (libs: only (0,1)).
- M21 P1 (0,1): captures 3 P2 stones.
- M22 P2 (0,3): retakes.
- M23 P1 (0,2): joins (0,3)+(0,4) island to main row-2 group; group spans x=0 (via (0,2)) to x=8 (via (8,2)). **Win.**

**Final:** P1=12, P2=8.

### Game 2: pat_structured (23 moves, P1 win, decisive)

Opened *identically* to fractal (M1–M9). The first behavioural divergence is at M9.

- M9 P1 (1,2): on structured, this immediately puts P2's (2,1) into 1-liberty atari, because *both* (1,1) and (3,1) are holes on structured (vs only (1,1) on fractal). On fractal, P2's (2,1) had 2 liberties after the same move; on structured, it has 1.
- M10 P2 (2,0): **forced defense** — P2 *must* save (2,1) by extending to (2,0). This costs P2 a tempo of column-2 development. The lost tempo never resurfaces in the rest of the game, but it's a clear hole-arrangement-driven divergence from fractal.
- M11–M16: similar to fractal, but P2 is one step behind on col 2.
- M17 P1 (0,4): on structured, (0,4) has 3 liberties — (0,3), (0,5), (1,4) — because (1,4) is *active* on structured. Compared to fractal, the wedge attack on (0,2) plays from (0,4) directly rather than needing the (0,5) prep move.
- M18 P2 (0,1): extends defensively.
- M19 P1 (0,3): pinches P2's group with two P1 stones at (0,3) and (0,4). P2 group {(0,1),(0,2)} now in atari (1 lib at (0,0)).
- M20 P2 (0,0): defensive extension; group now {(0,0),(0,1),(0,2)} but still in atari (only lib (1,0)).
- M21 P1 (1,0): captures 3 P2 stones at (0,0),(0,1),(0,2).
- M22 P2 (0,0): re-occupies the corner, capturing my (1,0) (which had become a 1-lib stone after the capture).
- M23 P1 (0,2): joins (0,3),(0,4) island to main row-2 group via the now-empty (0,2). Group spans x=0 to x=8. **Win.**

**Final:** P1=11, P2=8.

### Game 3: pat_random (17 moves, P1 win, decisive)

Random's hole-set creates the *only* fully-clean row across all conditions: row 7 (no holes). Combined with the {(8,6),(8,8),(6,8),(7,8)} bottom-right cluster, several edge cells (e.g., (8,7)) become 1-liberty stones — but the more important fact is that the clean row 7 gives P1 a **straight free lane** from x=0 to x=8.

- M1 P1 (5,7): take centre of the free lane immediately.
- M2 P2 (2,0): commit to column 2 (clean column).
- M3–M11: P1 fills row 7 westward (4,7)→(0,7). P2 fills col 2 southward (2,1)→(2,4). At M11, P1 reaches the x=0 face.
- M12–M14: P2 extends col 2 to (2,5),(2,6); but (2,7) is mine, so P2 cannot complete col 2.
- M13–M16: P1 builds row 7 east — (6,7),(7,7). P2 plays (2,8) without ever blocking row 7.
- M17 P1 (8,7): completes row 7 from x=0 to x=8. **Win.**

**Why P2 didn't block:** to block row-7 east extension, P2 would need to play (8,7) — which has 0 liberties because (8,6) and (8,8) are *both* holes. (8,7) is a suicide cell for P2 unless P2 captures something with the move. P2's only viable interdiction is (7,7) — but my game with the col-2 race already gave P1 a faster path. The random arrangement essentially handed P1 a free lane.

**Final:** P1=9, P2=8. Note: zero captures the entire game, in contrast to fractal/structured/grid which all had a multi-stone capture in the M17–M23 window.

### Game 4: pat_grid (23 moves, P1 win, decisive)

No holes. Pure connection race + capture. The opening book is closer to a Hex-style mid-board contest because there are no walls to lean against.

- M1–M14: P1 builds row 4 (1,4)→(7,4); P2 builds col 3 (3,0)→(3,6) and is forced to commit (4,3) to prevent P1 from connecting row 4 north-of-row 4. By M13 P1 reaches the x=7 face.
- M14 P2 (0,4): blocks P1's only row-4 west extension.
- M15 P1 (0,3): bridge stone at x=0 face (isolated for now).
- M16–M20: P2 extends down column 0 — (0,5),(0,6),(0,7) — building a wall to keep P1's (0,3) island separated from the main row-4 chain.
- M17, M19, M21 P1 plays (1,5),(1,6),(1,7) respectively — closing off P2's column-0 chain along its east side. Each P1 move atari-nudges the P2 group.
- M21 P1 (1,7): closes the bottom of the surrounding chain; P2 group {(0,4),(0,5),(0,6),(0,7)} has 0 liberties — captures 4 stones.
- M22 P2 (0,5): re-enters column 0, hoping to disrupt P1's connection.
- M23 P1 (0,4): joins (0,3) island to main row-4 group via the now-empty corridor. Group spans x=0 to x=7. **Win.**

**Final:** P1=12, P2=7. Largest capture of all four games.

## Phase 3 — Strategic analysis (joint)

### Did each hole-pattern play differently?

**Fractal vs structured:** The opening (M1–M9) and the *target* of the capture sequence (M17–M21) are nearly identical. But the hole arrangement *changed individual moves*:
- M10 on fractal P2 plays (2,6) (offensive); on structured P2 *must* play (2,0) defensively because (3,1) is a hole and (2,1) is at 1 liberty. **Clear arrangement-driven divergence.**
- M17 on fractal P1 plays (1,3) bridge; on structured (1,3) is a hole, so P1 plays (0,4) instead. **Different routing because of different hole placement.**
- M19 on fractal P1 must play (0,5) prep before attacking (0,4) (because (1,4) is a hole on fractal); on structured, P1 plays (0,3) directly to attack (0,2) because (0,4) was already safe (3 libs because (1,4) is *active* on structured). **The same capture goal requires a different move sequence because of one hole.**

**Random:** played categorically differently. No tactical capture occurred. The game was a 9-move row-7 construction and P2 never had a path to block. (8,7) is a 1-liberty cell because of the (8,6)+(8,8) hole cluster — P2 can't even play it as a wall. The combination of (a) one fully-clean row plus (b) the bottom-right hole cluster made row-7 effectively unblockable.

**Grid:** the longest-lived strategic phase because there are no holes to lean on. Both sides had to build full chains; the eventual decisive sequence was a standard Go-style perimeter capture (column 0 fence captured by closing along column 1).

### Self-similarity load-bearing?

**No.** The structured lattice produced the same capture mechanism as the fractal, with a *different* hole-arrangement-driven divergence at M10 (the (2,1) atari). I could not point to a single tactical affordance that the Sierpiński carpet provided which the structured lattice did not also provide via different specific holes. Both let the central column be split (fractal: 3×3 blob; structured: (4,4) singleton + lattice). Both let edge stones drop into 1-liberty traps (fractal: (0,4) via (1,4); structured: many lattice neighbours). Random produced a *different* effect — but the random effect was a flat free lane, not a self-similarity-driven affordance.

### Choke points and corridors

- **pat_fractal:** Major choke = the 3×3 central blob (rows 3–5, cols 3–5). Forces all LR traffic through y∈{0,2,6,8} and all TB traffic through x∈{0,2,6,8}. Minor 1-liberty edge cells: (0,4), (8,4), (4,0), (4,8) — each surrounded on three of four sides by either holes or the board edge.
- **pat_structured:** Major choke = the (4,4) singleton + the periodic lattice creates many *small* corridors. Every odd row is checkerboarded with holes — these rows give 5 active cells per row but only 4 of them can join to a left/right neighbour without going through the alternating holes.
- **pat_random:** Major choke = bottom-right 3-hole cluster making (8,7) suicidal-without-capture for either player. Major affordance = clean row 7 (the only fully-clean row) creating a free lane.
- **pat_grid:** No choke points. Open board.

The Sierpiński's choke (one big blob) is *qualitatively different* from structured's (many small lattice cells) only in terms of *which moves* matter — but the resulting depth was similar in my play.

### Random as control

Random's hole arrangement was strategically interesting only in a degenerate way: it broke balance. The presence of one fully-clean row plus a corner of holes that made the opposite-edge wall unbuildable handed the game to P1. This is a *high-saliency* pattern but a *negative-quality* one — random patterns can flatten play by creating unblockable lanes, not by adding depth.

### Tempo / first-move advantage

P1 won all four games. Lengths: fractal 23, structured 23, random 17, grid 23.

Ranking P1 dominance from strongest to weakest:
1. **random** (17 moves, no captures, free-lane race) — P1 advantage was overwhelming.
2. **grid** (23 moves, 4-stone capture) — P1 advantage was modest.
3. **fractal ≈ structured** (23 moves, 3-stone capture) — P1 advantage was modest.

Random is the clear outlier on first-move-advantage.

### Quantitative comparison

| Condition  | Length | Decisive | P1 final | P2 final | Captures by P1 |
|------------|--------|----------|----------|----------|----------------|
| fractal    | 23     | yes      | 12       | 8        | 3              |
| structured | 23     | yes      | 11       | 8        | 3              |
| random     | 17     | yes      | 9        | 8        | 0              |
| grid       | 23     | yes      | 12       | 7        | 4              |

The random outlier is striking on every metric.

## Phase 4 — Pattern Critic (mandatory)

### Critic argues

(a) All three 9×9 hole-conditions are essentially "17 cells removed from a 9×9 grid." From a black-box view they have the same active-cell budget (64) on the same bounding box.
(b) The Pair-C spike result was driven by hole *count* — fewer cells means more constrained interaction — not by the *arrangement* of holes.
(c) An expert at the Sierpiński game would transfer to random and structured immediately with no relearning, because the only thing that changed is which 17 cells are removed.

### Player 1 + Player 2 rebuttal

Specific Phase-2 moments where the *arrangement* (not the count) changed strategy:

1. **M10 on structured vs fractal.** Same prior 9 moves; on structured P2 is in atari (1 liberty) and must defend (2,0); on fractal P2 has 2 liberties (because (3,1) is a hole on structured but active on fractal) and can play offensive (2,6). One hole flipping between active and inactive changes which group is in atari at the same move number. *The critic cannot explain this from "17 holes is 17 holes" alone.*

2. **M17 on structured uses (0,4) directly; on fractal must use (0,5) first.** Same goal (attack the (0,2) corner group), but the move ordering is forced different by *which* hole is at (1,4): on fractal (1,4) is a hole so (0,4) is a 1-liberty trap; on structured (1,4) is active so (0,4) is safe at 3 liberties. The expert playing fractal who memorises "M17 = (0,5) then (0,4)" would *misplay* on structured, where (0,5) is unnecessary and the direct (0,4) move is correct.

3. **M17 on random — no capture sequence at all.** The game did not have an M17–M23 capture phase; it was decided by row-7 construction. An expert at the fractal game's capture sequence has zero relevant knowledge for the random game. The critic's prediction (c) is *false in the strongest sense* on random — it's not even the same kind of game.

4. **(8,7) suicide-without-capture on random** is a specific arrangement fact. It exists because (8,6) AND (8,8) are *both* holes. On fractal and structured (8,7) is a normal 2-liberty cell. The critic's "17 holes is 17 holes" claim ignores that the *spatial correlation* of holes — adjacent holes vs scattered ones — is what determines whether a cell is suicidal or playable.

That said, **partial concession to the critic:** the *outcome* (P1 wins, ~23 moves, similar capture targets) was very similar between fractal and structured. The "any structure helps over no structure" hypothesis is *more consistent* with my data than "Sierpiński is special." The critic loses on (c) (transfer is not free) but has a defensible weak version of (b): the *count* of holes plus *some* structure explains most of the depth signal; specific Sierpiński self-similarity adds little above what a generic lattice already provides.

## Phase 5 — Verdict

### pat_fractal

- **Strategic Depth:** 6 — Central 3×3 blob and corner holes create real tactical decisions; multi-move capture sequences are forced and reward looking ahead. The (1,4) hole turns (0,4) into a 1-liberty trap, which adds genuine wall-aware tactics.
- **Balance:** 5 — P1 won; 23-move game suggests modest P1 advantage. Within noise of the other 23-move games. Need n>1 to verify.
- **Novelty:** 6 — central-blob + 4 corner holes creates a recognisable fractal-style "bordered courtyard" topology that does feel different from a plain grid. But it doesn't feel categorically richer than a regular lattice.
- **Hole-arrangement saliency:** 7 — three concrete moves (M19, M17, M21) depended on *which* holes are where, not just "there are holes."
- **Overall "Would I play again?":** 6.

### pat_random

- **Strategic Depth:** 3 — Free row-7 lane trivialised the game. Only 9 P1 moves needed; no captures; P2 had no real reply.
- **Balance:** 2 — Heavily P1-favoured (17 moves vs 23 for the others); the specific random seed produced an asymmetric board.
- **Novelty:** 4 — The (8,7)-suicide cell is an interesting arrangement fact, but it never came into play because the game ended too quickly.
- **Hole-arrangement saliency:** 8 — Saliency is *high* but in a *negative* direction: the specific arrangement (clean row 7) entirely defined the game. This is exactly the kind of "arrangement matters" evidence that refutes the critic, but it argues *against* random as a substrate.
- **Overall:** 3.

### pat_structured

- **Strategic Depth:** 6 — Lattice creates many 1-liberty atari opportunities (the M10 forced-defence is a clean example). Capture sequences feasible; depth comparable to fractal.
- **Balance:** 5 — Same 23-move pattern as fractal/grid.
- **Novelty:** 5 — Periodic structure feels more mechanical than fractal's organic central blob, but produces similar tactics.
- **Hole-arrangement saliency:** 7 — The specific lattice spacing (every other row/col) creates the M10 atari and several other 1-liberty plays. Lattice ≠ generic-structure; the specific stride-2 arrangement is doing real work.
- **Overall:** 6.

### pat_grid (control)

- **Strategic Depth:** 5 — Pure Hex-like connection race + capture; no walls to exploit. Solid but unremarkable.
- **Balance:** 5 — Same 23-move P1-win pattern.
- **Novelty:** 3 — Baseline grid; this is the control.
- **Overall:** 5.

### Within-team deltas

| Δ                                | value |
|----------------------------------|-------|
| Δ Overall fractal − grid         | +1    |
| Δ Overall random − grid          | -2    |
| Δ Overall structured − grid      | +1    |
| Δ Strategic Depth fractal − grid | +1    |
| Δ Strategic Depth random − grid  | -2    |
| Δ Strategic Depth structured − grid | +1 |

### Critical assessment

- **Is Sierpiński self-similarity load-bearing? N.** Fractal and structured produced equally-deep play (Δ Overall = +1 for both vs grid; same 23-move length; same capture-sequence target). I could not identify a tactical affordance unique to the recursive hole structure that the stride-2 lattice didn't also provide via different specific cells. The "central courtyard" character of Sierpiński does feel slightly more aesthetic, but in mechanical play terms, the lattice was equivalent.

- **Did random produce comparable depth to fractal? N.** Random was *worse* than grid (Δ −2) — the specific seed produced an unblockable free lane plus a suicidal corner cell, collapsing the game into a 17-move construction race. Random arrangement is the *highest-saliency* condition (in the sense that arrangement-specific facts most strongly determine the outcome) but the saliency cuts the wrong way: it produced imbalance, not depth.

- **Did structured produce comparable depth to fractal? Y.** Same length, same capture-sequence target, same Δ vs grid. The forced-defence at M10 and the (0,4) liberty-count flip at M17 were both *arrangement-driven divergences* — the games were not literally identical — but at the depth-score level they were equivalent.

- **Recommendation for R17:** **(b)** replace with cheaper structured-hole operator.
  - The fractal-spike's depth signal is reproducible with a generic *symmetric* hole-pattern (the stride-2 lattice did fine).
  - The Sierpiński-specific generator path doesn't earn its complexity over a cheaper structured generator in my data.
  - Random as an operator is *actively bad*: with 17/81 cells removed at a uniform-random seed, I drew a free-lane board that was clearly less interesting than grid. R17 should *not* use random hole-perturbation.
  - Caveats: my conclusion rests on n=1 team; the 7-team aggregate may differ. In particular, the random condition may average to grid-like quality if the free-lane luck is rare across seeds — but my single sample suggests the variance is large enough that random-as-an-operator would inject noise into the evolution loop.
