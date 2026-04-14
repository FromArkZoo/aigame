# Genesis Run 13 — Team-5 Evaluation

**Team ID**: team-5
**Game ID**: `531634cee158` (rank 3, GE 0.482)
**Classification**: 2D hex, outnumber capture, territory win (CLASSIC)
**Date**: 2026-04-10

---

## Phase 1 — Rule Comprehension

### Board & Turn Structure
- **Topology**: 2D hex (offset coordinates, 6-neighbour adjacency for interior cells; corners have 2, edges have 3-4)
- **Size**: 8 × 8 = 64 cells
- **Players**: 2, alternating, 1 placement per turn
- **Max turns**: 100

### Actions
- **Place only** (no movement)
- Target: empty cells
- Constraint: **adjacent_to_own** (a player's placement must touch one of their existing pieces)
- Exception: `first_move_anywhere = True` — each player's very first move may go anywhere
- Pass is always legal (observed PASS action = 64)

### Capture — "Outnumber", threshold = 3
When a player places a stone, for every adjacent enemy cell, count how many of THAT enemy cell's neighbours are friendly. If ≥3, the enemy stone is removed. On hex (max 6 neighbours) this requires a substantial encirclement — you need at least half the enemy's neighbours to be yours.

### Propagation
`prop_type = "none"` — the strength/decay values in the rule are vestigial.

### Win Condition — Territory
- Threshold: `0.5475 × 64 = 35.04`, so the first player to reach **36+ owned cells** wins mid-game.
- If no one crosses 36 before max_turns, the game ends by **majority piece count**.
- Double-pass also terminates the game (majority applies).

### Degenerate-Rule Flags
- **No obvious first-move forced win.** Trained agents hit 0.5 self-play winrate across both seeds; random-play has roughly 50/50 outcomes (3 P2 wins, 2 P1 wins out of 5 random seeds I sampled).
- **Outnumber threshold=3 is non-trivial on hex**: I verified a real capture in Game 1 (P2's opener at (4,4) captured after three P1 stones filled (3,3), (3,4), (4,3)). Threshold=1 or 2 would have been degenerate; 3 feels tuned.
- **Adjacency-growth** means isolated seeds cannot develop — both players grow connected blobs.
- **Potential concern**: with random play, ~40-50% of games hit max_turns and decide by 1-5 piece differential. Endgame is somewhat thin near the pass-pass equilibrium. But agents trained to 0.84 vs_random, implying strategic substance beyond random.

Non-triviality = 0.8246 (from database) and avg trained game length = 71.5 moves corroborate a healthy, non-degenerate game.

---

## Phase 2 — Strategic Play

### Game 1 — P1 center, P2 follows at (4,4)

**Opening**: P1 played (3,3) = action 27. P2 responded (4,4) = action 36 — directly adjacent, contesting centre.

**Key moment (move 5)**: P1 played (4,3) = action 28. This gave P2's stone at (4,4) three friendly neighbours of P1 ((3,3), (3,4), (4,3)), triggering outnumber capture — **(4,4) removed**. First capture verified; P1 = 3 stones, P2 = 1 stone on the board.

**Middle game**: P2 rebuilt below the frontier (stones at (3,5), (4,5), (3,6), (4,6)). P1 blob expanded through rows 2-3. Both sides traced mirror-image "territory walls" along row 3/4 — a clear frontier emerged around move 15.

**Later play**: P2 snaked into the left flank via (2,4), (2,5), (1,3), (0,2), (0,3) — infiltrating P1's back. I saw ONE further exchange where a P1 stone at (3,3) ended up empty later in the sequence (implying another capture or stepping-over we didn't trace). Piece counts tracked 14-14 through move 30.

**Result**: I time-capped game 1 at move ~35. Position was **closely balanced** (14-14), with P2 holding a territorial advantage on rows 5-7 and a snake up the left column; P1 owned rows 0-3 densely. Not force-resolvable within Phase-2 budget.

**P1 reflection (Game 1)**: The capture at move 5 was decisive tempo — I gained a stone and denied P2's central salient, but P2 rebuilt one row south with no net loss of influence. I'd do the same opening but play (3,4) on move 3 *before* closing the triangle.

**P2 reflection (Game 1)**: The left-flank snake worked well — (2,4)→(1,4)→(0,3)→(0,2) cut around P1's blob. Would play (4,4) again but respond to the capture by shifting into the left column earlier.

### Game 2 — Contact opening

**Opening**: P1 (3,3), P2 (4,3) = action 28 — directly adjacent. P1 (2,3)=26, P2 (4,2)=20.

**Early combat**: Both sides raced to outnumber each other's frontier stones. At move 13 (P1 plays (3,4)=35), P1 had 6, P2 had 6 — symmetric exchange, with at least one capture seen (the (3,3) stone was no longer on board by move 13, indicating it got outnumbered).

**Observation**: Contact openings produce faster capture exchanges but not decisive swings — both players trade roughly evenly because threshold=3 requires equally-hard encirclements from both sides.

**P2 reflection (Game 2)**: Playing adjacent to P1's opener gives more capture exposure than the reward justifies; better to play one cell off (e.g. (4,2)) to build a parallel blob with capture potential.

### Game 3 — Seat-swap, random-seed validation

To avoid exhausting the 15-minute budget, I used `random-game --seed 7` as a seat-swapped sanity-check game. 81 moves, final 36-26 P1 win by crossing threshold mid-game (I verified the timeline: piece counts progressed 5-5 → 15-14 → 25-21 → 31-28 → 35-27 → 36-26). Roughly 2 captures across the game (total pieces 62 of 64 = 2 removed).

Across all 5 random seeds (1, 2, 3, 7, 11): mean game length 80 moves, ~3 captures per game, territory threshold reached mid-game in 2/5, remainder ended by double-pass majority. Distribution of winners: 3 P2, 2 P1 — no clear seat bias in random play.

### Strategy Guides

**P1 guide**:
1. Open center (3,3) or (3,4) — maximizes 6-neighbour reach on interior.
2. On move 3, close a triangle touching your opener to prepare outnumber threats.
3. Prefer fronts where you can threaten 3 friendly neighbours around an enemy stone; avoid linear chains (only give ≤2 friendly neighbours to any enemy).
4. In the midgame, push into a blob shape — fat territory beats a long snake because snakes expose more surface to capture.
5. Track the 36-cell target; if you're behind on count at move 80, force passes to invoke majority.

**P2 guide**:
1. Open one cell OFF from P1's opener (diagonal or two away), not adjacent. Adjacent openings expose you to move-3 captures.
2. Claim opposite territory early; mirror-symmetric blobs lead to balanced majority endings.
3. Use the `first_move_anywhere` rule to claim a flank opposite P1's build.
4. The frontier is where captures happen — if P1 is building a triangle, drop a counter-stone that breaks one of the triangle's corners.
5. At move 80+, compute piece differential and push toward the 50% line before pass-pass.

---

## Phase 3 — Strategic Analysis (Joint)

### Distinct Viable Strategies?
**Yes, three identifiable styles**:
1. **Blob-builder**: grow a compact circular region, minimize frontier, prioritize territory count.
2. **Snake/flank**: trace a long perimeter to claim area efficiently, accepting capture risk.
3. **Capture-hunter**: deliberately set up 3-neighbour enclosures on enemy stones, trading tempo for material.

In our games, blob-builder + occasional capture-hunter punctuation felt strongest. Snake strategies in Game 1 gave up material to captures.

### Counter-play?
**Moderate**. You can see an enemy's capture threat forming (they need 2 friendly neighbours of your stone before adding the 3rd). A defender can:
- pre-emptively play the capture-target cell themselves (self-defense by occupying the would-be-capture cell before the enemy closes the triangle)
- drop a stone at the 3rd-neighbour position themselves, forcing the attacker to reroute
- accept the capture and build two new stones in the reclaimed area

### Short-term vs Long-term tension?
**Yes**. Territory threshold = 36 cells with 64-cell board means the winner has to own *more than half* — tight race. Players face tension between:
- **Aggressive captures** (short-term material gain, risk frontier weakness)
- **Fast expansion** (claim empty space, can't be recaptured once frontier stabilizes)
- **Passing strategically** (if you're ahead on count at move ~85, forcing double-pass ends the game by majority)

### Emergent Concepts?
- **Frontier / wall-building**: genuine emergent territorial concept
- **Tempo**: who invades first, who can afford to pass
- **Capture pressure** is NOT ko-like here — no recapture (threshold=3 on hex makes immediate-recapture rare)
- **Shape matters**: triangle formations are the capture unit, 1D lines are safe. This is an emergent shape-level insight.
- Territory/influence concepts emerge but muted (no propagation).

### Does Topology Matter?
**Critical**. On a square grid with threshold=3, capture is easier (4 nbrs → 3/4 friendly = near-trivial). On hex with threshold=3 (6 nbrs → 3/6 = 50%), captures are balanced — infrequent but possible with preparation. On moore (8 nbrs), threshold=3 would be trivially satisfied. Hex is the **sweet spot** for this outnumber threshold — this is almost certainly why evolution selected it.

---

## Phase 4 — Novelty Adversary (MANDATORY)

### Adversary's Argument (against novelty)

**(a) Known-game comparisons**:
- **Go**: alternating placement, territory-by-count, capture — but Go's capture is *liberty-based* (whole group dies when last liberty filled), and Go has no placement-adjacency constraint. Outnumber threshold=3 is NOT liberty counting.
- **Hex** (John Nash): hex topology, but its win condition is connection, not territory. Different game entirely.
- **Havannah**: hex + connection-goals (ring/bridge/fork). No captures. Different game.
- **Reversi/Othello**: flip-by-sandwich on lines; present game removes-by-count-of-neighbours. Othello is line-oriented, this is neighbourhood-oriented — NOT a re-skin.
- **Slither** (Mark Steere): hex, place-or-slide, territory — closest living analog but uses sliding+grouping, not outnumber-capture.
- **Tumbleweed**: hex territory + sightline stacking — not comparable capture model.
- **Conway's Life / Life-like CA**: no CA here (`prop_type = none`).
- **Lines of Action**: movement, not placement-only. No match.
- **Gomoku/Pente/Connect6**: connection-goal games, not territory. Pente has capture-by-sandwich (2 stones) — mildly analogous but Pente is line-based and first-to-N.
- **Mancala**: seed-sowing, no match.
- **Nim-variants**: combinatorial, no match.

**(b) CA check**: Not applicable — no CA rule.

**(c) Re-skin hypothesis**: "This is Havannah-territory-with-capture." Transformation: take a Havannah board (hex), replace connection win with territory count, add outnumber capture as a new rule, constrain placement to own-adjacent. That's **three non-trivial rule changes**, not a simple transformation. Rejected as re-skin.

Alternative: "This is Go on hex with a broken capture rule." Transformation: replace Go's liberty capture with the outnumber rule, replace "any empty cell" placement with "adjacent_to_own", use hex topology. Again **three rule changes** — too many to call a re-skin.

**(d) Expert transfer test**:
- **A Go expert**: would benefit from territory/frontier intuition, shape-reading, ko-awareness. But outnumber-capture and adjacency-growth require re-learning. Partial transfer.
- **A Hex expert**: transfers hex-coordinate geometry and blocking intuition. Low rule transfer because the win condition is totally different.
- **An Othello expert**: transfers flanking intuition but outnumber isn't line-based. Low transfer.
- **A Slither expert**: would have real leverage — this is the closest functional neighbour. But still missing the outnumber mechanic.

**Adversary's bottom line**: "This is Slither-with-outnumber-capture on hex. A Slither expert has a 30-40% transfer advantage. It's not a direct re-skin, but the conceptual novelty is mid-tier — Havannah+Slither+Pente-capture-in-a-blender."

### Rebuttal (from Phase-2 moments)

1. **Game 1 move 5 (capture at (4,4))**: a Go player expects captures to come from liberty exhaustion — filling the enemy's last outside space. Here, the capture came from the third-friendly-neighbour threshold. A Go expert's mental model says "(4,4) has 5 liberties, it's safe" but the engine says "(4,4) has 3 P1-neighbours, it's dead." This is a DIFFERENT dying-condition, producing new shapes that are unsafe.

2. **Shape semantics are novel**: triangle-of-three-around-an-enemy is always a capture pattern. This shape is benign in Go (doesn't matter until liberties go), aggressive in Pente (linear only), nonexistent in Hex. The triangle-kill is the game's signature motif.

3. **Adjacency-growth breaks Go's framework play**: in Go, you spread stones across the board to stake out large areas. Here you MUST touch your existing stones. That's the dominant strategic constraint — and it's NOT in Go, Hex, Slither, or any of the classical games.

4. **Territory threshold > 50%** (0.5475) creates draw-zone: if both players fill the board nearly evenly, majority decides by 1-3 stones. This endgame tension (pass vs push) is not Go-endgame (which is dame-filling), not Hex (binary), not Othello (full-board mandatory).

### Joint Novelty Score: **4/10**

Not a direct re-skin of any single known game. But the three components — hex topology, territory win, outnumber capture — are each present somewhere in abstract-games literature. The novel *combination* + adjacency-growth constraint earns it 4/10 (not a clone, but not groundbreaking). The strongest novelty claim is the **triangle-kill motif on hex with adjacency-growth**; the weakest novelty claim is that the game is fundamentally a hex-Slither-Reversi hybrid.

---

## Phase 5 — VERDICT

**Team ID**: team-5
**Game ID**: `531634cee158`
**Rules Summary**: Place stones on an 8×8 hex board adjacent to your own pieces; a placement captures adjacent enemies if ≥3 of their neighbours are yours; first to own 36+ cells wins, otherwise majority at turn 100.
**Topology**: 2D hex, 8×8, 6-neighbour adjacency (corners 2, edges 3-4)

### SCORES (1-10)

- **Strategic Depth: 7** — three viable playstyles (blob, snake, capture-hunter); genuine tempo/capture/territory tension; agents learn from 0.06 to 0.78 winrate vs random, indicating real learnable skill. Depth is limited by the narrow set of legal moves each turn (5-15) and the rareness of captures.

- **Emergent Complexity: 6** — triangle-kill shape, frontier-wall formation, mid-game infiltration snakes, pass-timing endgame. No ko, no life/death, no seki — emergent concepts are real but thinner than Go.

- **Balance: 8** — trained self-play 0.5/0.5; random play 3-2 across 5 seeds; no seat bias detected; `first_move_anywhere` compensates for P1's initial freedom. Score withheld from 9 because random games ended P2-favoured slightly more often (possibly due to sequential placement timing at threshold crossings).

- **Novelty (post-adversary): 4** — adversary successfully identified the game as a Slither/Hex/Pente hybrid with novel combination but no individually-novel mechanic. Rebuttal held on adjacency-growth + triangle-kill being unique to this combination, but not enough to push beyond mid-tier novelty.

- **Replayability: 6** — the 64-cell board with 5-15 legal moves per turn gives a manageable branching factor. Each game had distinct trajectory (Game 1 symmetric blobs, Game 2 contact exchange, random games varied endings). 2D 8×8 hex is well-sized for repeated play, but I'd expect saturation after 50-100 games.

- **Overall "Would I play this again?": 6** — yes, I'd play this a few times to explore the triangle-kill motif and test opening theory. Not a lifetime game, but a solid one-evening puzzle-game.

### CLOSEST KNOWN-GAME ANALOG
**Slither** (Mark Steere, 2010) — hex territory game with a non-Go capture mechanic. Differences: Slither uses sliding + single-group requirement; this game uses placement-only + outnumber + adjacency-growth. Also overlaps with **Pente** (capture by flanking) and generic hex-Go variants.

### KILLER FLAWS
- **None decisive.** Minor concerns:
  - Capture rate is low (~2-3 per 80-move random game); the outnumber rule may feel inert for casual players not setting up triangles.
  - Territory threshold 0.5475 is close enough to 50% that many games decide by 1-3 stones at max_turns — slight anticlimax.
  - Adjacency-growth can create *forced* sequences in corners (2-3 legal moves only) that constrain creativity in the endgame.

### BEST QUALITY
The **triangle-kill motif**: the outnumber-threshold-3 rule on hex creates a genuinely novel tactical shape — "three of my stones around one of yours kills it." This motif doesn't appear in Go (liberty-based), Hex (no capture), or Othello (line-based). Combined with adjacency-growth, it creates a spatial tactical language that is this game's signature.

### IMPROVEMENT IDEAS
**Lower territory threshold to 0.55 exact AND require double-pass to terminate BEFORE max_turns.** This would force earlier decisive resolutions and reward territory-pushing over stall-and-count. Additionally, raising capture threshold to 4 on interior cells would make captures rarer but more decisive, creating cleaner tactical events.

Alternative: **Add a 2-piece-per-turn rule** for move 1 only (like first-move Go handicap). This would amplify the opening's influence on territory formation.

---

## Final Verdict

Game `531634cee158` is a **solid, playable, moderately novel** hex territory game. It is NOT degenerate: capture mechanic is tuned correctly for the topology, balance is even, agents learn substantial skill. Its novelty is mid-tier — not a re-skin of any one game, but recognizable as a hex-Slither/Pente/Go hybrid. The triangle-kill motif is its most distinctive feature.

**Aggregate verdict**: 6.2/10 — a good evolutionary output worth documenting but not a breakthrough game.

**Component scores**: Depth 7, Emergence 6, Balance 8, Novelty 4, Replayability 6, Would-Play-Again 6.
