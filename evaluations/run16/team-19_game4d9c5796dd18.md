# Team-19 Evaluation — Game `4d9c5796dd18`

Run 16 human evaluation. Independent verdict on a single game.

---

## Phase 1 — Rule Comprehension

### Board structure
- **Dimensions**: 2D, axis size 8 → 8×8 = 64 cells
- **Topology**: `moore` (8-neighbor adjacency including diagonals; Chebyshev distance for influence)
- **Action space**: 65 actions = 64 placement cells + 1 pass (action 64)

### Turn structure
- **ALTERNATING** (`turn_type: alternating`, 1 piece per turn). NOT simultaneous. R16's simultaneous engine fixes (margin-based threshold, snapshot CA) do not apply here.

### Action types
- Placement only (no movement). `target=empty`, `constraint=anywhere`, `first_move_anywhere=true`.

### Capture mechanic
- `capture_type: surround`, `threshold: 2`. Go-style: an enemy group with 0 liberties next to the placed stone is removed.
- **In practice this rule is essentially inert** on Moore topology. To capture even a single isolated enemy stone, you must occupy all 8 of its Moore neighbors. I verified by playing a contrived scenario where 8 P2 stones surround a single P1 stone — capture only fires on the 8th-neighbor placement. In *none* of my Phase-2 strategic games did a single capture occur.
- The prompt context confirms this: R16's generator now downgrades `moore → grid` whenever surround capture is present. This game (gen 10) appears to predate or escape that filter, so the capture rule is a vestigial mechanic.

### Cellular automaton
- None — `uses_ca = false`. Classic placement game.

### Propagation / influence
- `prop_type: influence`, `radius=2`, `strength=1.6836`, `decay=0.7205`.
- Each placement adds `±strength · decay^d` to `board_values[cell]` for every cell within Chebyshev radius 2 (a 5×5 area = up to 25 cells). Sign is `+` for P1, `−` for P2. Clamped to ±100.
- A placed stone gives itself +1.68; distance-1 neighbors get +1.21; distance-2 cells get +0.87.
- **Key emergent property**: influence is symmetric and superimposes. A P2 stone within radius 2 of a P1-owned cell *reduces* the value on that cell (which is P1-owned), thus dampening P1's effective score even though the cell is still P1-owned. This makes "interference placement" (placing close to enemy stones) a real tactical tool.

### Win condition
- `condition_type: threshold`, `threshold ≈ 50.51`, `target_dimension=0` for P1, `target_dimension_p2=-1` ⇒ engine sums `board_values` over all cells *owned by the player* and compares to threshold. P1 effective = sum of `board_values` on P1 cells; P2 effective = `−sum` on P2 cells (because P2 placements add negatives).
- `max_turns=100`. R16 engine: same-tick double crossings resolve by *higher margin*, ties → draw. R16 also: double-pass → draw (not majority).

### Empirical threshold calibration
- A tight 3×3 P1 cluster of 7 stones (no opposition) crosses threshold at the 7th stone (effective ≈ 57.3).
- Under contested play, P1 typically crosses threshold around stone #7–#13 depending on P2 interference.

### Degenerate-rule flags
- **Capture rule is inert** (Moore + surround → no captures in normal play). This is a design wart but not a winning-strategy issue.
- No degenerate forced win in ≤5 moves observed.
- Threshold is reachable with high frequency — no double-pass draws observed in 11 sweep games + 3 narrative games.
- Pass action (64) is never preferred under greedy play.

---

## Phase 2 — Strategic Play

I played 3 full alternating games with engine-verified moves. All board states and effective scores were read from `engine.board_values` and `engine.board_owners`.

### Game 1 — P1 thoughtful center cluster vs P2 mirror+interference

| Turn | Player | Move | P1 eff | P2 eff |
|------|--------|------|--------|--------|
| 1 | P1 | (3,3) | 1.68 | 0.00 |
| 2 | P2 | (5,5) | 0.81 | 0.81 |
| 3 | P1 | (4,3) | 4.05 | -0.06 |
| 4 | P2 | (4,5) | 2.30 | 2.30 |
| 5 | P1 | (3,4) | 6.75 | 0.21 |
| 6 | P2 | (5,4) | 3.78 | 3.78 |
| 7 | P1 | (2,3) | 11.19 | 2.91 |
| 8 | P2 | (6,5) | 10.32 | 10.32 |
| 9 | P1 | (2,4) | 20.16 | 9.45 |
| 10 | P2 | (6,4) | 19.28 | 19.28 |
| 11 | P1 | (3,2) | 30.87 | 18.41 |
| 12 | P2 | (5,6) | 29.99 | 29.99 |
| 13 | P1 | (4,2) | 42.45 | 28.24 |
| 14 | P2 | (4,6) | 40.70 | 40.70 |
| **15** | **P1** | **(2,2)** | **56.66** | **40.70** | done=True, **P1 wins** |

P1 reasoning: build a 3×3 cluster from center, choosing extensions away from P2's stones to minimise dampening overlap.
P2 reasoning: mirror moves to neutralise score (P2's symmetric mirror keeps scores equal until P1's killer move).
P1 strategy review: the early move (3,3) put P1 one tempo ahead. Cluster extensions chose the side AWAY from P2 to preserve own value and not feed P2's interference. Would not change the strategy.
P2 strategy review: pure mirroring guarantees parity until tempo decides — i.e. P1 wins by one move. Should have played adjacent to P1's first move (see Game 3).
Surprises: none — clean threshold crossing, no captures, no double-pass.
Win condition reached cleanly via threshold.

### Game 2 — P1 center cluster vs P2 aggressive adjacent interference

P1 plays (3,3), then (4,4),(3,4),(3,5),(2,4),(2,3),(1,3),(1,2),(2,1),(4,2). P2 plays (2,2),(5,5),(4,3),(4,5),(5,4),(2,5),(1,4),(0,3),(3,2). Both clusters overlap heavily, dampening each other's stones strongly.

| Stage | P1 eff | P2 eff | Note |
|-------|--------|--------|------|
| After T15 | 25.40 | -7.53 | P2's effective is *negative* — P2's stones have so much P1-influence over them that their net is negative |
| After T17 | 27.62 | -7.06 | P1 ahead but progress slowed dramatically |
| After T19 (P1 (4,2)) | 28.29 | -9.21 | P2 at this point cannot win without reaching far open territory |
| After greedy continuation T20–T25 | — | — | P1 wins on **T25** by P1 (2,0), reaching 51.25 |

P1 strategy review: aggressive interference by P2 actually *helps* P1 if P1 keeps building. P2's stones near P1 push P1's value down, but P2's own stones get hammered worse because P1 has more stones in the dense zone. P1 should expand into open space (top, left edges) where P2 cannot reach quickly enough. Took 25 turns vs Game 1's 15.
P2 strategy review: head-to-head adjacency dampens P1 but dampens P2's own pieces equally. Net result: longer game, but P1 still wins because P1 has the tempo to extend into open space first.
Surprises: P2's effective went *negative* — counter-intuitive. The mutual dampening is not symmetric in game-state because P1 is always one stone ahead, so the asymmetry favours the leader.
Win condition reached cleanly via threshold.

### Game 3 — Seat swap. P1 plays greedy (opponent role), I play P2 trying to win.

**Seat-identity bias acknowledged**: I'm the same agent playing both seats. As P2 I tried to (a) build a strong central cluster, (b) avoid P1's territory, (c) mirror P1's tempo as best I could.

P1 plays greedy starting with (0,0) corner. As P2 I built a center cluster (3,3),(4,4),(4,3),(3,4),(5,4),(5,5).

| Turn | Player | Move | P1 eff | P2 eff |
|------|--------|------|--------|--------|
| 1 | P1 | (0,0) | 1.68 | 0.00 |
| 2 | P2 | (3,3) | 1.68 | 1.68 |
| 3 | P1 | (1,1) | 4.92 | 0.81 |
| 4 | P2 | (4,4) | 4.92 | 4.92 |
| 5 | P1 | (1,0) | 11.46 | 4.92 |
| 6 | P2 | (4,3) | 11.46 | 11.46 |
| 7 | P1 | (0,1) | 20.42 | 11.46 |
| 8 | P2 | (3,4) | 20.42 | 20.42 |
| 9 | P1 | (2,0) | 30.45 | 20.42 |
| 10 | P2 | (5,4) | 30.45 | 30.45 |
| 11 | P1 | (2,1) | 41.16 | 28.70 |
| 12 | P2 | (5,5) | 41.16 | 40.48 |
| **13** | **P1** | **(3,0)** | **51.19** | **40.48** | **P1 wins** |

P2 strategy review: the parallel-cluster approach lost because greedy P1 had identical board geometry but with one extra tempo. As P2 I should have played adjacent to P1's first stone — I confirmed this empirically afterwards (see "Sweep results" below).

**Sweep results — seat balance under greedy play across 26 opening pairs**:

| P1 first | P2 response | Result | Turns |
|----------|-------------|--------|-------|
| (0,0) | (1,1) — diag-1 | **P2 wins** | 20 |
| (0,0) | (1,0)/(0,1) — orth-1 | P1 wins | 19 |
| (3,3) | any adjacency | P1 wins | 15–17 |
| (4,4) | any adjacency | P1 wins | 15–17 |
| (7,7) | (6,6) — diag-1 | **P2 wins** | 20 |
| (1,1) | (2,2) — diag-1 | **P2 wins** | 18 |
| (0,3) | (1,3) — orth-1 | **P2 wins** | 18 |

P2 wins ~25–30% of greedy-vs-greedy games when given the choice of opening. P1 wins ~70–75%. **First-mover advantage exists but is breakable** — there's a non-trivial space of P2 openings (corner-adjacent diagonal-1) that flip the result. This is real strategic content, not a degenerate forced-win.

### Strategy guides

**Player 1 strategy guide**:
1. Open near a corner (0,0)/(7,7) — corners reduce off-board influence loss and force P2 to either commit nearby (sharing dampening) or far away (giving you free territory).
2. Build a tight cluster — every adjacent stone you add gets +1.68 self plus +0.87–+1.21 from each previously-placed neighbor. Density compounds.
3. If P2 plays adjacent to you, *extend in the opposite direction* — the contested cells dampen mutually and the leader generally retains tempo.
4. Watch for the threshold-crossing move at stone #7–#10. Your 7th well-placed stone in a tight cluster wins outright.

**Player 2 strategy guide**:
1. **Adjacency is mandatory** — if you play far from P1, P1 wins on tempo. Play within radius 1, ideally a diagonal step (Chebyshev distance 1).
2. Choose corner-adjacent openings: P1 (0,0) → you (1,1). The mutual-dampening trade favours whoever is closer to the corner because off-board cells receive no influence and don't count.
3. Mirror to keep parity, but late game pivot to a fresh corner (P1 at (0,0), you at (7,7)) to outrun P1's saturated cluster.
4. Avoid getting boxed into a single-stone position with 8 enemy neighbors — extremely rare but the only way to lose pieces to capture.

---

## Phase 3 — Strategic Analysis (joint)

**Distinct viable strategies?** Yes, two coherent meta-strategies emerge:
- *Cluster expansion* — build a tight 3×3 in open territory; reach threshold via density.
- *Adjacent dampening* — place near opponent to mutually suppress; convert tempo when opponent over-extends.

These are mutually constraining: pure cluster loses to a well-timed adjacency response; pure adjacency loses if opponent breaks for open territory.

**Counter-play?** Yes. Each strategy has a specific counter:
- vs. cluster → adjacent diagonal-1 placement at the cluster boundary.
- vs. adjacency → expand to the opposite corner, leaving the opponent's interference structure stranded.

**Short-term vs long-term tension?** Mild. Each move's local +1.68 self-value is the short-term reward; global cluster value at game-end is the long-term goal. They mostly align (good moves are both locally and globally valuable). The interesting case is "do I block opponent or grow my own?" — usually growing wins, except in late game when opponent is one move from threshold.

**Emergent concepts**:
- *Tempo / initiative* — being one move ahead in cluster-build = +5–10 effective score.
- *Territory* — corners are strictly more valuable than edges than center? **NO — actually the opposite**: corners lose ~half the influence radius to off-board, but the *competitive* dynamic favors corners because off-board cells can't be invaded. Net: corners are slightly favored under greedy adversarial play (sweep showed (0,0) and (7,7) opens beat (3,3) opens). This is a subtle emergent property.
- *Influence cancellation* — P2 within radius 2 of P1 stone = direct value subtraction from P1's score. Real ko-like fights at the cluster boundary.
- *Capture* — does NOT meaningfully arise. Vestigial.

**Topology relevance**: The Moore (8-neighbor) topology gives Chebyshev distance, which makes the influence radius a 5×5 square instead of a 5×5 diamond (von Neumann). This means the influence area is larger (25 cells vs 13) and the "effective cluster value" is correspondingly higher. Without the engine's Moore-Chebyshev fix (which I read in `topology.py`), influence would have been broken.

**First-mover advantage**: Under greedy-vs-greedy:
- P1 wins 19/26 = 73% in opening sweep
- P2 wins 7/26 = 27%

Game 3 (seat swap) confirmed P1 wins under greedy. P1 advantage is approximately 1 tempo (i.e. ~10 effective-score units in late game), which dominates unless P2 plays a specific counter (corner-adjacent diagonal-1).

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary opens**: This game is a re-skin of standard "place-to-threshold" influence games. Specifically:

(a) **Pente / Gomoku family**: place stones, accumulate value, threshold/connection win. *Rebuttal*: Pente uses connection (5-in-a-row); Gomoku uses connection. Neither has continuous influence values — they are binary occupied/empty. The continuous influence field is materially different: in Phase-2 Game 2 P2's effective score went *negative* despite owning 7 stones, which is impossible in any connection game.

(b) **Reversi/Othello**: discrete capture and territorial accumulation. *Rebuttal*: Othello has flipping captures every move and bracketed-capture as a primary mechanic. This game's surround capture never fires; the game is decided purely by influence sum, not by stone count or flips.

(c) **Go (with area scoring)**: stones generate territory that is scored. *Rebuttal*: Go scoring is binary (a cell is your territory or not); influence here is real-valued, decays continuously with distance, and crucially can be REDUCED by enemy nearby. There is no Go equivalent of "your stone is worth less because the opponent is nearby" — Go territory is determined by surrounding-walls boolean topology.

(d) **Tumbleweed (Mark Steere)**: places stones with strength = 2 (number of friendly neighbors), area scoring. *Rebuttal*: Tumbleweed is the closest analog. Both have continuous-ish strength values driven by neighborhood count. But (i) Tumbleweed has stack heights and capture-by-stronger-stack mechanics, (ii) Tumbleweed uses hex topology, (iii) Tumbleweed's strength does not decay with distance — it's only direct line-of-sight neighbors. The decay-with-distance over a radius-2 area gives smoother, more spread-out fields than Tumbleweed.

(e) **Hex / Y / Havannah**: connection games, irrelevant — no connection here.

(f) **Lines of Action**: movement game, irrelevant.

(g) **Diplomacy / Blotto / RPS-scaled**: simultaneous games, irrelevant — this is alternating.

(h) **Life-like CA**: no CA here.

(i) **"Threshold tug-of-war on 8x8 grid with influence aura"**: this is the most accurate description, and it has no direct prior-art match I'm aware of.

**Adversary's strongest case**: This is "Tumbleweed with decay and Moore topology". An expert Tumbleweed player would recognize the strength-accumulates idea immediately.

**Phase-2 moments where the analogy fails**:
- Game 2 turn 16: P2 effective score *decreased* to -7.06 even though P2 had more pieces than turn 15. In Tumbleweed/Othello/Pente piece counts and scores monotonically increase with placement. Here, the influence field interacts: P1 placing nearby reduced the value of P2-owned cells. No board game in the standard catalog has this "your owned cells lose value when opponent moves near them" property as the *primary* dynamic.
- Game 3 turn 12: P2 (5,5) — P2's effective score went 30.45 → 40.48 with one stone placement adding +10.03 to P2. That marginal value depends entirely on the surrounding influence configuration, not on connection topology. This is a "potential field" game, not a discrete graph game.

**Novelty score**: 4/10. Closest analog (Tumbleweed) shares the spirit but differs in: (1) decay-with-distance, (2) Moore topology, (3) capture mechanic (vestigial here, present in Tumbleweed), (4) win-by-threshold vs majority. The continuous-decay-influence-field-with-threshold is mildly novel as a combination, but the underlying "place stones, accumulate area-weighted value, first to N wins" is well-trodden. With the surround capture being inert, the design is functionally simpler than its rule-string suggests — a single mechanic (influence accumulation) decides everything.

---

## Phase 5 — Verdict

**Team ID**: team-19
**Game ID**: 4d9c5796dd18
**Rules Summary**: 8×8 Moore-topology alternating placement game. Each placement adds a decaying influence field (radius 2, decay 0.72) to surrounding cells, positively for P1 and negatively for P2. First player whose owned cells sum past the threshold (~50.5) wins. Surround capture is technically present but functionally inert under Moore topology.
**Topology**: 8×8 grid, Moore (8-neighbor), Chebyshev distance for influence
**Turn Structure**: alternating

### SCORES (1-10)

- **Strategic Depth: 5** — Two coherent meta-strategies (cluster expansion vs adjacent dampening) with rock-paper-scissors-like counter-play. Tempo and influence cancellation create real tactical choices in the opening and mid-game. But the game is short (13–25 turns), the optimal cluster shape is obvious, and the "right" answer for P1 is mostly "build a tight cluster". Opening theory matters more than mid-game tactics.

- **Emergent Complexity: 5** — Influence cancellation produces non-monotonic score curves (Game 2's negative P2 effective). Tempo emerges naturally. Capture is dead, removing one mechanic that could have added complexity. No surprising long-range interactions; everything is explainable by local influence sums.

- **Balance: 4** — Greedy-vs-greedy seat-balance probe: P1 wins ~73%, P2 wins ~27%. Game 3 (seat swap) showed P1 wins again. First-mover advantage is significant but breakable by the right P2 opening (corner-adjacent diagonal-1). Unbalanced enough that R16's worst-of-three probe should flag this — though the existence of a P2 counter strategy means it's not a complete first-move win.

- **Novelty (post-adversary): 4** — Closest analog is Tumbleweed (continuous-strength placement game), with continuous-decay influence as the differentiator. The Moore-topology + threshold-win + influence-decay combination has no direct precedent in my knowledge, but the underlying primitive "place to grow value" is very well-trodden. The dead capture rule reduces effective novelty further.

- **Replayability: 4** — Games are short and resolve in 13–25 turns. Once a player learns "build a tight cluster" and "P2 must play adjacent to break tempo", optimal play converges. Limited tactical variation. Some replay value from corner choice and adjacency-vs-mirror choice, but plateau is reached quickly.

- **Overall "Would I play this again?": 4** — Once or twice for novelty and to explore the corner/adjacency theory; not as a regular game. The vestigial capture rule and short game length cap the depth. It's strictly inferior to Tumbleweed for someone wanting an influence-accumulation game.

### CLOSEST KNOWN-GAME ANALOG
Tumbleweed (Mark Steere, 2020). Both are "place stones, accumulate strength based on neighborhood, win by area/threshold". This game differs in: continuous decay over Chebyshev radius 2, square/Moore (not hex), threshold (not majority), and an inert surround-capture rule. An experienced Tumbleweed player would transfer most strategic intuitions immediately.

### KILLER FLAWS
- **Inert capture rule**: surround capture on Moore topology requires occupying 8 neighbors of an isolated stone — never happens in normal play. The capture mutation flag in the rule representation is functionally a no-op. R16 generator now downgrades this combination, but this game (gen 10) preserves the dead rule.
- **First-mover advantage**: ~73% P1 win rate under greedy play. R16 worst-of-three seat probe should catch this, though there IS a P2 counter (corner-adjacent diagonal-1 opening) that prevents it from being a forced win.
- **Short games / limited depth**: 7-stone tight cluster wins in unopposed play; 13-stone in contested. No middlegame exists in the chess sense — opening directly into endgame.

### BEST QUALITY
The mutual-dampening dynamic where both players' influences interfere on the same cell. Game 2's P2-effective-score-going-negative moment is a genuinely surprising emergent behavior that you wouldn't predict from the rules in isolation. This creates real "interference vs expansion" strategic tension in the mid-game.

### IMPROVEMENT IDEAS
**Single rule change**: switch topology from `moore` to `grid` (von Neumann, 4-neighbor). This (a) makes surround capture actually fire (4 neighbors is achievable), restoring the capture mechanic to relevance, (b) reduces the 5×5 influence area to a 13-cell diamond, slowing threshold-crossing and lengthening games to 25–40 turns, and (c) creates real tension between "extend cluster" and "defend a stone from capture". This is exactly what R16's generator now does for surround+moore games — and the comparison would test whether the downgrade improves design quality. Alternatively: increase the threshold to ~80 so games last 25+ turns and middlegame tactics emerge.
