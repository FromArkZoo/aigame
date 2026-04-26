# Run 14 Human Evaluation — team-1 — Game `deb4dfe0382d`

**Team ID:** team-1
**Game ID:** deb4dfe0382d
**GE rank:** Run 14 champion (Go Essence = 0.5174)
**Evaluator:** single-agent sequential (acknowledged seat-identity bias)

---

## Phase 1 — Rule Comprehension

### Board
- **Dimensions:** 2D, axis size 8 → 64 cells total
- **Topology:** torus (8×8 with wraparound on both axes)
- **Adjacency:** von Neumann (4-neighbour, face-adjacent)

### Turn structure
- **Alternating** (P1, P2, P1, P2, …). One piece per turn.
- **NOT a simultaneous game** — so the R14 "simultaneous" family does not apply here.
- Max turns: 102.
- Action space: 65 actions (64 cells + action 64 = pass). Two consecutive passes end the game by majority piece count (the double-pass exploit from R13 is mechanically present).

### Actions
- Place only. No movement.
- Placement target: empty cells; constraint "anywhere"; first move anywhere.

### Capture — custodian, threshold 1
- After placing, walks along each axis direction from the placed cell; collects consecutive enemy pieces; if the walk terminates on a friendly piece, all collected enemies flip colour.
- **Walks do NOT wrap on torus** — they stop at the hard axis boundary. (Engine-confirmed: `topology.py` / `engine_v2._capture_custodian` uses `0 <= pos < axis_size`.)
- Threshold=1 means a single enemy piece between two friendlies is enough to capture.
- **Crucially, capture flips ownership but does NOT reset `board_values`.** Captured cells retain their accumulated influence from previous placements, which can mean the capturer now OWNS a cell with value opposite to their sign.

### Propagation — influence
- Radius 1 (only the placed cell + its 4 von-Neumann neighbours, torus-wrapped).
- Strength 1.874; decay 0.402.
- P1 placements add **+1.874** to the placed cell and **+0.753** (= 1.874 × 0.402) to each of the 4 neighbours. P2 is symmetric with negative sign.
- Values clamp to [−100, +100] (irrelevant for realistic play).
- Per placement total |ΔΣ| = 1.874 + 4·0.753 = **4.886**.
- Torus-wrap IS applied in influence propagation (confirmed by engine test: placing at (0,2) puts +0.75 on (7,2)).

### Win condition — threshold
- First player whose signed influence sum over cells they own exceeds **38.616** wins.
- Formally: P1 wins when Σ board_values[c] for c owned by P1 > 38.616; P2 wins when −Σ board_values[c] for c owned by P2 > 38.616.
- If max_turns (102) is reached, majority piece count decides.

### Degenerate-rule flags
- **Double-pass exploit present** but very unlikely to fire — the threshold is reachable in ~21 moves with reasonable cluster play, and passing gives up the +1 tempo P1 needs. Did not fire in any of our 3 games.
- **Custodian capture has perverse incentives** because board_values are retained on flip. Capture often produces at most a ~2× swing of a normal extension, and can even produce a NEGATIVE own-cell value for the capturer. This is a "real" anti-degenerate pressure — not an exploit, but it does mean capture is rarely strictly better than cluster-building.
- **Threshold is reachable in 21 moves given alternating 1-neighbour extensions of ~3.38 swing per move** (see Phase 2). This is well inside max_turns=102. Threshold is well-calibrated.
- Training runs agree: avg game length 22.5 and 32.5 steps — consistent with our threshold-winning games at 21-23.

---

## Phase 2 — Strategic Play

All three games were played with every move engine-verified via `play_helper.py --action play` and a custom `eval_state_helper.py` that reads `engine.board_values` directly (since `show` does not display influence). Moves numbered by ply (P1 = odd plies, P2 = even).

Notation: action ID = y·8 + x, so cell (x,y) encodes as y·8+x.

### Game 1 — classical mirror
Move sequence: `27, 36, 26, 37, 19, 44, 18, 45, 17, 46, 25, 38, 9, 54, 10, 53, 11, 52, 16, 47, 8`

- P1 opened (3,3), P2 mirrored diagonally at (4,4). Both players built 3×3 blocks on opposite "sides" of the torus.
- Cluster strategy: 1-neighbour extensions give +3.38 swing (2.62 own + 0.75 boost to adjacent own cell); 2-neighbour extensions give +4.88 swing (3.38 own + 1.50 boost).
- Through move 18 both sides held perfect symmetry at 34.94 each, then P1's extra tempo at move 19 (0,2), 21 (0,1 — 2-neighbour) crossed the threshold.
- **P1 wins at move 21** with effective 43.21 > 38.62; P2 at 38.33 (still below).
- No captures occurred in this game. Game length: 21 plies.

P1 reflection: Strategy = compact cluster build (3×3 block), only extending to 2-neighbour empties when safe from custodian bracket. Nothing would change — game 1 is the "theoretically optimal" play. P2 did not surprise me because mirror is also P2's best when P2 cannot find a safe multi-neighbour cell first.

P2 reflection: Mirror was my best available — every non-mirror move I considered gave smaller swing. I would consider opening NOT mirror on the torus' opposite corner but adjacent to P1's first move, forcing contact play earlier (tested in Game 2). Endgame reached via threshold, not double-pass.

### Game 2 — P2 plays contact opening
Move sequence: `18, 27, 26, 35, 28, 45, 17, 19, 9, 43, 10, 44, 16, 53, 8, 52, 24, 51, 25, 59, 2, 60, 1`

- P1 at (2,2). P2 chose aggressive diagonal-adjacent (3,3) — intentionally NOT mirror.
- Move 5: P1 played the tactical **capture** (4,3) — walked x-axis from (4,3) left to bracket (3,3) P2 between (2,3) P1 and (4,3) P1, flipping (3,3). This is the first actual custodian capture of the evaluation.
- **Observation:** after capture, P1's effective was UNCHANGED (4.50 → 4.50) while P2's effective dropped 4.50 → 2.63. The captured cell had retained a -1.87 P2-influenced value; when P1 took ownership it now contributes −1.12 (after propagation partially cancelled it) to P1's sum. Capture was +1.87 relative swing, strictly less than a normal +3.38 extension — **quantitative confirmation that capture is weaker than extension in typical material**.
- Move 8: P2 fought back with a counter-capture at (3,2) → bracketed the captured (3,3) P1 between (3,2) P2 and (3,4) P2. Both sides returned to 8.25 each.
- Moves 9-20: standard cluster race with occasional 2-neighbour bonuses. My (0,3)→(1,3) 2-move sequence gave a 3-P1-neighbour cell worth +6.39.
- **P1 wins at move 23** at 42.83 > 38.62. Longer than Game 1 (21) because captures redistribute value without advancing the threshold race.

P1 reflection: Capture was tempting tactically but numerically weaker than extension. Would I capture again? Only if it disrupts a P2 cluster that was ABOUT to reach threshold — i.e., as a defensive delay, not a winning blow. The real edge came from the (0,3)→(1,3) chain that built a 3-adjacency cell for +6.39 gain.

P2 reflection: Contact opening forces tactical complexity but gives up ~2 moves of tempo via the capture exchange. Still lost in 23 moves. Would try a mirror-with-slight-offset next time, or a split opening (two far-apart stones) to see if threshold from disjoint clusters wins.

### Game 3 — seat-swap intent + novel P1 opening
Move sequence: `36, 32, 35, 12, 28, 33, 27, 34, 19, 42, 20, 41, 44, 40, 43, 49, 37, 50, 29, 48, 21`

- P1 opened (4,4) centre. P2 tried territorial separation with (0,4) on the opposite side of the same row.
- P2 then extended with (4,1)=12 putting a piece IN the same column as P1's (4,4) — an interesting wedge that creates a potential custodian if P1 later plays (4,0).
- The game otherwise devolved to a race; P1's extra tempo again decided it.
- **P1 wins at move 21** at 40.95 > 38.62.
- Most instructive moment: at move 19 P1 had two 2-neighbour cells (5,3) and (5,5); (5,5) would have been CAPTURED by P2 at (6,5) bracketing between (6,5)P2 and (2,5)P2 along row y=5 (3 P1 stones captured). Going the other way (5,3) was safe. **This demonstrates that 2-neighbour cells need per-cell capture-safety analysis; not all extensions are safe.**

Seat-swap confession: I am a single reasoner; Game 3 "swap" was not a real agent swap. I rely on inter-team comparison to triangulate first-mover advantage.

### Results
| Game | P1 opening | P2 strategy | Winner | Moves | P1 final | P2 final | Captures |
|------|------------|-------------|--------|-------|----------|----------|----------|
| 1 | (3,3) | diagonal mirror | P1 | 21 | 43.21 | 38.33 | 0 |
| 2 | (2,2) | contact diagonal | P1 | 23 | 42.83 | 37.94 | 2 (1 per side) |
| 3 | (4,4) | distant (0,4) | P1 | 21 | 40.95 | 34.56 | 0 |

**All three games resolved via threshold (no double-pass, no max-turns timeout).** P1 won all three; first-mover advantage is strong and consistent.

### Strategy guides

**P1 guide**
1. Open near-centre so cluster growth has wraparound symmetry on the torus.
2. Aim for a compact 3×3 block; every move should be a 1-neighbour extension (+3.38 swing) or, when available, a 2-neighbour extension (+4.88 swing).
3. Before placing on a 2-neighbour empty, check custodian safety along both axes of the cell — if the cell's row/column has an existing P2 piece on one side and the bracket point on the other side could be P2 next turn, DON'T play there.
4. Avoid captures unless they disrupt a specific P2 threshold threat. Numerically, a normal capture yields ~+1.9 swing (half of an extension).
5. Late game, look for 3-P1-neighbour cells (forms a concave elbow around an empty) — these give +6.39 swing and typically win the race.

**P2 guide**
1. Pure mirror only loses by the one-tempo deficit (about 1.5 points less than P1 on symmetry). Try a contact opening OR a split-anchor opening to generate asymmetric positions.
2. If you contact: expect and accept 1-2 captures. Aim to make the capture exchange approximately neutral in effective value.
3. Watch for 3-neighbour extensions on your side as top priority — they erase the +tempo deficit.
4. Consider the double-pass exploit only if you have material advantage (piece count > P1) AND threshold is not approachable in remaining turns. In our games it was never warranted.

---

## Phase 3 — Strategic Analysis (joint)

**Distinct viable strategies?** Only marginally. In all three games the dominant line is "build a compact cluster and race to threshold". Variations (Game 2 contact opening, Game 3 distant anchor) did not flip the win rate — P1 won all three. Sub-strategies exist in TACTICAL choice (which 2-neighbour cell, when to capture), but the macro strategy is uniform. Rating: ~1.5 distinct strategies (cluster-race vs cluster-race-with-captures).

**Meaningful counter-play?** Moderate. Captures are a genuine tactical tool — P2 in Game 2 counter-captured and restored parity. Cluster intrusion (P1 playing into P2's radius) reduces both sides' efficiency and is a real trade-off. But no deep counter-play emerged: you can't really "outplay" superior tempo without a threshold-level blunder by P1.

**Short vs long-term tension?** Mild. Playing a 1-neighbour extension now is nearly-optimal at all moves. The only long-term thinking needed is: (a) avoid shapes that expose to multi-piece custodian capture; (b) plan the 3-adjacency cell setup (e.g., play 0,3 BEFORE 1,3 when both are available). Time horizon ≈ 2 moves.

**Emergent concepts observed**
- **Tempo** — strongly present. First-mover advantage is decisive.
- **Influence "gravity"** — clusters with internal adjacencies accumulate value faster per piece (4.89 for a central cell of 2×2 vs 1.87 for an isolated cell).
- **Custodian tension on torus** — the fact that capture walks do not wrap means the board has a *perceived* boundary despite topology being torus. Players must think about "which side of the axis am I on?" for capture analysis.
- **Captured-value paradox** — because board_values don't reset on capture, captures are rarely material-positive relative to extension. This dampens aggressive play.

**Does topology matter?** Somewhat but not as much as advertised. Because clusters never really meet in 21-23 moves, the torus wraparound on influence is mostly unused. Pure grid would play nearly identically. **The torus is cosmetic in this time horizon.**

**First-mover advantage:** P1 won 3/3. Avg final P1 lead = 4.9 points. Under mirror play, P1 reaches 2-neighbour cells one ply earlier than P2. This is a ~4.9-point structural advantage at threshold. This is NOT offset by any mechanic. Simultaneous turn structure (the R14 candidate) would eliminate this; custodian on a smaller threshold would also reduce it. **Strong balance concern.**

---

## Phase 4 — Novelty Adversary (mandatory)

### Adversary's case: "this is not novel"

**(a) Comparison against the canonical catalogue**

- **Go.** Placement on empty, capture mechanic. But Go uses surround/liberty capture, not custodian; and Go's win condition is territory-counting, not an influence threshold. Rejected as direct analog.
- **Hex / Y / Havannah.** Connection games. No capture, different win condition. Weakly similar — this game IS placement on empty cells on a grid-like topology. But the presence of capture and a numeric threshold rules out the Hex family.
- **Reversi / Othello.** **CLOSEST ANALOG.** Custodian capture is explicitly "Othello-style bracketing" per the engine's own comment (`_capture_custodian`). Othello is 8×8 with axis-aligned brackets along all 8 directions (including diagonals); this game is 8×8 with brackets along 4 directions only (von Neumann axes). So this is **"Othello on von-Neumann-only with a continuous-valued influence field layered on top, on a torus"**. The Othello expert would immediately recognise the capture tactics. Threshold ≠ "most stones at end" but threshold is still a numeric-sum end condition similar in spirit.
- **Gomoku / Pente / Connect6.** Line-forming games. No capture similarity (Pente has custodian-style bracket capture but the win condition is five-in-a-row). The INFLUENCE FIELD, not line-forming, is the win driver here. Partial match — Pente shares the bracket-capture mechanic but not the win condition.
- **Amazons / Chameleon / Lines of Action.** Movement-based; this game is placement-only. Rejected.
- **Mancala.** Sowing, not placement. Rejected.
- **Conway's Life / Day & Night / HighLife / Immigration.** Cellular automata. This game is NOT a CA game (rule report confirmed "Cellular Automaton: No (classic)"). Rejected.
- **Nim family.** Not abstract-board. Rejected.
- **Tumbleweed.** Influence-propagation placement game on a hex board with "Sightline" win. Similar philosophy (stones cast influence, territory determined by influence majorities) but on hex with fundamentally different topology and without custodian capture. Strongest philosophical cousin.
- **Slither.** Connection with sliding; different mechanic. Rejected.

**(b) CA literature.** N/A — no CA here.

**(c) Simultaneous / Blotto / Diplomacy.** N/A — alternating turns.

**(d) Re-skin argument.** The adversary's best attack is: "this is Othello with the capture-direction set reduced from 8 to 4 (von Neumann only), played on a torus (but the capture doesn't wrap, so the torus is effectively for the influence field only), with the Othello 'score by majority' win condition replaced by a weighted influence threshold that still rewards cluster formation, played on the same 8×8 board." That is: **Othello-light + influence field**. An Othello expert's intuitions about bracketing, corners (none here — torus eliminates corners), and tempo would transfer directly to the capture part of this game.

**(e) Expert test.** An Othello expert evaluating this game would immediately see:
- Custodian brackets work the same.
- The lack of diagonal brackets simplifies capture analysis (Othello-diagonal bracket would have added more capture threats).
- The "captured cell retains opponent's influence" mechanic is ALIEN to Othello and the Othello expert would misplay this. This is the strongest novelty claim.
- The influence-threshold win is ALIEN to Othello. Expert would want to maximise piece count; this game rewards cluster density instead.

**Adversary's bottom line:** 30% Othello, 30% Tumbleweed-style influence game, 40% a novel combination of the two. Score **3/10** — the novel combination is real but mostly mechanical; strategic emergence is modest.

### Player 1 / Player 2 rebuttal

**Specific moments where Othello intuition fails:**
1. Game 2, move 5: P1 captured (3,3) P2. In Othello this would be strictly positive (one stone flipped = +2 material swing in majority scoring). Here the swing was only +1.87 effective value — half of an extension move. **Reason: the captured cell retained its prior P2 influence value, which now counts AGAINST the capturer.** An Othello expert would over-value captures.
2. Game 3, move 19: P1 had the choice of 2-neighbour cell (5,5) which LOOKS like a strong interior play, but it would have been captured along a 3-in-a-row column. The capture would have flipped 3 P1 stones to P2, worth roughly −12 to P1. An Othello expert would NOT have seen this because Othello has no concept of "preemptive capture defence on an empty move" — you typically worry about the opponent flipping YOUR existing pieces, not about them capturing a piece you're about to place AND the pieces it joins.
3. Game 1 throughout: the 3×3 cluster formation is NOT an Othello-style play. In Othello you want to spread and reach corners. Here you want to BALL UP. The influence field inverts the "spread out" heuristic.
4. The **torus topology with non-wrapping custodian** creates a situation where influence communication wraps (the board is a donut) but capture geometry does not. An Othello expert has never seen this asymmetry and their tactical calculus will misapply in wrap-adjacent cells.
5. The **threshold reaching 38.6 in ~21 moves with P1 winning every time** indicates the game is mechanically short. Othello runs ~60 moves. The condensed time horizon means standard Othello opening theory (attack the corners, establish stable edges) is moot.

**Rebuttal-specific emergent concept:** Effective value per cluster geometry is non-linear — a 2×2 yields 13.5 effective, 3×3 yields 34.9 — this super-linear cluster bonus has no Othello analog.

### Novelty score (joint decision)

Taking the adversary's case seriously: this IS Othello-ish in capture, Tumbleweed-ish in influence. The novel ingredients are (a) custodian + retained board_values (which creates the capture paradox), (b) threshold-by-signed-sum win (subtle but different from piece majority), (c) non-wrapping custodian on a wrapping influence field (novel quirk). Strategic emergence is modest: one dominant macro strategy (cluster-race). Nothing resembles ko-fights, sacrifices, deep tactical sequences.

**Novelty score: 4/10.** A distinct combination of known ingredients that creates modest but non-trivial gameplay texture, not a genuinely new abstract game.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** deb4dfe0382d
**Rules Summary:** 8×8 torus, alternating placement, Othello-style custodian capture (4-axis only, no wrap on captures), influence field (r=1, strength 1.87, decay 0.40) with threshold win at effective sum > 38.62.
**Topology:** 2D torus 8×8 (wrap on influence; no-wrap on custodian).
**Turn structure:** alternating (1 piece/turn). NOT simultaneous — this is a classical game, not R14's new simultaneous family.

### Scores (1-10)

- **Strategic Depth: 4/10** — one dominant macro strategy (cluster-race). Tactical depth exists (capture safety analysis for 2-neighbour cells, captured-value paradox) but doesn't produce branching strategic lines.
- **Emergent Complexity: 4/10** — super-linear cluster bonus is genuine emergence; capture-retains-value is genuine emergence; but these don't compose into deeper dynamics. No ko, no sacrifice, no long-range positional concepts.
- **Balance: 2/10** — First-mover wins 3/3 in our games, with structural reason (P1 reaches 2-neighbour cells one ply earlier). Seat-swap was weak due to single-reasoner setup, but the structural tempo argument is mathematical, not psychological. Strong imbalance.
- **Novelty (post-adversary): 4/10** — distinct combination of Othello capture + influence threshold on torus, but each ingredient is known. Captured-cells-retain-value is the freshest mechanic.
- **Replayability: 3/10** — games converge similarly (21-23 moves, mirror-race). Openings differ but funnel to the same cluster race.
- **"Would I play this again?": 3/10** — Once to explore, but the pattern locks in too quickly. The captured-value paradox is a nice curiosity but doesn't sustain 10+ games of interest.

### Closest known-game analog

**Othello** (with two reservations): (1) only 4 directions for custodian instead of 8; (2) the scoring field is a continuous signed-influence sum rather than piece majority. If the win condition were "most pieces at move 102", it would be a direct Othello variant. The influence threshold makes the game a "speed Othello with a numerical scoreboard".

### Killer flaws

- **First-mover structural advantage is uncorrected.** Under mirror play P1 reaches the threshold exactly one ply before P2 due to tempo on 2-neighbour cells. P2 has no mechanic to neutralise this.
- **Non-wrapping custodian on a wrapping influence field is a confusing asymmetry.** It mostly doesn't matter in practice (clusters don't reach the boundary in 21 moves) but it's a UX wart.
- **Captured-cells-retain-value dampens capture as a viable strategic tool**, which in turn reduces the richness of the custodian mechanic it relies on. The game would be deeper if capture strictly paid.
- Degenerate concerns (double-pass exploit, CA dead rules) do NOT fire for this particular game — it converges cleanly via threshold.

### Best quality

The **captured-cells-retain-value paradox** is genuinely thought-provoking. It creates a principled reason to AVOID captures except as defensive tempo-breakers. Combined with the super-linear cluster bonus, it rewards a specific aesthetic: "build your own territory; don't chase your opponent." That is a legitimate design philosophy and it plays out cleanly in 20ish moves.

### Improvement idea

**Make the threshold scale with move count** (e.g., threshold = 30 + 0.2·move_count) so that P1's tempo advantage on 2-neighbour cells is offset by the threshold rising slightly in the interval between P1's and P2's moves. Alternatively, **reset board_values to 0 on custodian capture**, which would make capture a clean material swing equivalent to a normal extension. Either change would make the game genuinely fair AND more tactically interesting.
