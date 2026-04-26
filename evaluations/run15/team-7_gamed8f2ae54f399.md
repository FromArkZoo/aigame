# Team-7 Evaluation — Game d8f2ae54f399 (Run 15)

- **Team ID:** team-7
- **Game ID:** d8f2ae54f399
- **Generation:** 10 (parent 4af27911b0f5)
- **R15 rank:** 2 by GE 0.255; training ELO 2632.8, trained vs random 1.00, non-triv 1.00
- **Headline:** 8×8 grid, ALTERNATING, place-anywhere, Go-style surround capture, radius-1 influence (strength=0.9323, decay=0.5097), threshold win at 22.645.

---

## Phase 1 — Rule Comprehension

**Board:** 2D 8×8 grid (64 cells), non-toroidal (hard edges). Von-Neumann (orthogonal) neighbourhood throughout (radius=1 propagation rule gives 4 orthogonal neighbours per cell).

**Turn structure:** **ALTERNATING** (one piece per turn). Not simultaneous — so the R15 simultaneous-tie P1 bias is NOT in play here. First-mover (P1) has an inherent structural advantage because P1 places stone #N before P2 places stone #N in any tied race-to-threshold scenario.

**Action types:** Place only. One placement per turn on any empty cell (`placement_rule={target: empty, constraint: anywhere, first_move_anywhere: true}`). Action space: 64 placement actions + 1 pass = 65 total. Action ID for (x, y) is `y*8 + x`.

**Capture rule:** `capture_type=surround, threshold=1`. **This is classic Go-style group capture.** Despite the rule carrying a `threshold=1` field, inspection of `engine_v2.py:_capture_surround` (lines 482-496) shows the threshold is IGNORED for surround — the engine removes any enemy group with 0 liberties adjacent to the freshly-placed stone. Threshold only affects `outnumber` capture. Verified empirically: a single adjacent enemy does NOT auto-capture (one liberty still standing); a corner stone fully bracketed by 2 enemies IS captured (verified with sequence (0,0)→(1,0)→(5,5)→(0,1) — the P1 corner stone was removed at piece_counts[1]=2).

**Propagation rule:** `prop_type=influence, radius=1, strength=0.9323, decay=0.5097`. Each placed stone adds ±strength (0.9323) to its own cell and ±strength·decay (≈0.4752) to each orthogonal neighbour. Contributions are additive and signed (P1 positive, P2 negative), so collisions cancel. Verified empirically: an isolated P1 stone gives its cell bv=+0.932 and each neighbor bv=+0.475; when a P2 stone is placed on (or adjacent to) that influence, the two fields cancel linearly.

**Win condition:** `condition_type=threshold, threshold=22.645, target_dimension=0`. `_check_threshold` (engine_v2.py:748-761) sums `board_values[c]` over cells OWNED by player (P1 sum uses values as-is; P2 sum negates). First player whose effective value strictly exceeds 22.645 wins. Max turns 100.

**Key quantitative facts:**
- Isolated stone contributes **0.932** to own-cell sum (not 2.83 — the radiating 0.475s land on EMPTY cells which aren't counted in threshold sum).
- Each friendly orthogonal neighbour adds **+0.475** to your own cell (stacked across all friend adjacencies).
- Each enemy orthogonal neighbour adds **–0.475** to your own cell (erodes).
- A 2-cluster (two friendly adjacent stones): both cells at 0.932 + 0.475 = 1.407, total 2.81.
- A 3x3 solid block (9 stones): 4 corners (1.88), 4 edges (2.36), 1 centre (2.83) → total **19.79** — just below threshold.
- A 3x3 + 2 extra attached stones typically crosses 22.65.
- Pure-isolated path to threshold: 22.645 / 0.932 ≈ 24 stones (impractical under alternation with 64 cells).

**Conclusion:** Clusters are mandatory to hit threshold in reasonable time. Each additional friend-adjacency is +0.475 of threshold credit PER involved stone. This pushes play strongly toward Go-like group formation.

**Degeneracies checked:** None found.
- No "play action 0 repeatedly" win (each cell can be placed once, subsequent step on occupied cell is filtered by `get_legal_actions` target=empty).
- Surround capture is alive (verified corner capture with 2 stones).
- Threshold is reachable (greedy-vs-greedy game ends at move 23 with P1 crossing).
- Max-turns cap never triggered across 30 random games and 3 strategic playthroughs.
- Double-pass draw never triggered (neither player has incentive to pass before threshold).

---

## Phase 2 — Strategic Play

### Game 1 — P1 (me, early-scatter) vs P2 (me, cluster-focused)

All moves engine-verified via `play_helper.py --action play`. Final verified sequence:
```
27,36,9,54,22,50,5,40,29,43,28,35,26,44,37,34,45,42,20,51,30,52,21,41,53,33
```

**Highlights:**

- **M1 P1 (3,3):** standard center opening.
- **M2 P2 (4,4):** diagonal so influence does not collide (radius-1 orthogonal only, so diagonal neighbors contribute zero).
- **M3 P1 (1,1), M4 P2 (6,6):** I pursued a spread strategy as P1 thinking each isolated interior stone was worth a full 2.83 (WRONG — it's 0.932 to threshold sum). Symmetric.
- **M5–M10:** both placed further isolated stones. Threshold sums equal at 4.66 after 10 moves. I was generating lots of "influence" but not threshold credit.
- **M11 P1 (4,3):** reconsidered and started clustering, linking (3,3) with (5,3). Threshold jumped +2.36 (own-cell 0.932 + neighbor boosts).
- **M12 P2 (3,4):** P2 started a 2x2 cluster between (4,4)(3,4)(3,5) — very efficient.
- **M18 P2 (2,5):** massive +3.78 move (3 friendly neighbors). P2 pulled ahead 13.62 vs 10.77.
- **M21 P1 (6,3):** linked my existing (5,3)-(6,2) for +2.83. Still behind.
- **M22 P2 (4,6):** P2 cluster keeps growing. 19.28 vs 12.65. I'm cooked.
- **M23 P1 (5,2):** found a 3-friend cluster move for +3.78. Caught up to 19.27 vs 19.28.
- **M24 P2 (1,5):** P2 plays +2.83, at 22.12, one safe move from winning.
- **M25 P1 (5,6):** dual-purpose attack + cluster, eroded (4,6) and (6,6) by 0.475 each and gained +0.93. P2 dropped to 21.17. But P2 still has a free +2.83 move available.
- **M26 P2 (1,4):** +2.83 → 24.00 > 22.65. **P2 wins.**

**P1 reflection (Game 1):** My strategy was wrong in the opening: I treated each isolated stone as worth 2.83 (mistaking the "influence total" for "threshold total"). The threshold check uses the own-cell sum, so isolated stones are only worth 0.932; I was building padding that didn't count. Against a cluster-focused P2, I fell behind irreparably. Lesson: **cluster early and defend cluster integrity.**

**P2 reflection (Game 1):** Intuitive cluster-building won. The (2,5) and (4,6) moves each gave +2.83+ to threshold because each had 3 friendly orthogonal neighbors (triangle-interior cells in a rectangle cluster). Once P1 fell behind in threshold, catch-up was impossible because the board was filling and remaining high-density-friend positions were limited.

**Endgame:** Resolved by threshold at move 26. Not a double-pass draw.

---

### Game 2 — Greedy-optimal P1 vs Greedy-optimal P2 (deterministic, both maximize own_sum − opponent_sum with centrality tiebreak)

Full verified sequence:
```
27,28,35,36,19,37,20,29,26,44,34,45,18,43,11,21,12,30,10,38,25,22,33
```

The two players mirrored each other's cluster growth, building mirror 3x3-ish blocks. By move 22, both at 21.19. On **move 23 P1 plays (1,4)** — a 2-friend cluster move giving +2.83, pushing P1 to 24.02 > 22.65. **P1 wins at move 23.**

This is the clean "first-mover advantage dominates" outcome:
- When both players optimize identically, every move is value-symmetric for the next move.
- P1 makes the ODD-indexed moves (1, 3, 5, …, 23), so if it takes 23 total moves, P1 made 12 and P2 made 11. P1 had 1 more stone's worth of cluster bonus.
- Final score P1=24.02, P2=21.19 — the +2.83 gap is exactly one "2-friend-cluster move" — i.e., P1's extra turn.

**P1 reflection (Game 2):** Strategy was trivial — mirror P2 and claim the extra final move. No deviation needed.

**P2 reflection (Game 2):** Mirroring gives a guaranteed loss because P1's Nth stone precedes P2's Nth stone. To win as P2, must deviate with a play that disrupts P1 more than it costs P2. The naive greedy adversary cannot find such a play.

**Endgame:** Resolved by threshold at move 23. Not a double-pass draw.

---

### Game 3 — SEAT SWAP: Greedy-optimal P1 vs me playing P2 with anti-mirror "surround" strategy

Full verified sequence:
```
27,28,35,36,19,20,26,34,18,29,43,37,44,21,11,12,10,13,25,33,17,42,9,41,51
```

P2 strategy: rather than mirror, place each stone maximizing `(#P1 neighbors * 2 + #P2 neighbors * 3)` — i.e., always stay on the contact line with P1's cluster, leveraging both erosion (each P1-neighbor costs P1 0.475) AND own-cluster continuity.

Result: P2 narrowed the gap (reached 20.22 by move 24 vs P1 at 21.17) but P1 crossed threshold first on move 25 with (3,6) at 23.05. **P1 wins at move 25.**

Takeaway: the surround strategy RECOVERS some value (game lasted 2 moves longer than greedy mirror) but still loses. The geometric reason: every P2 stone adjacent to a P1 stone erodes that P1 stone by 0.475 AND reduces its own value by 0.475 (from the P1 neighbor). This is a zero-sum exchange on the CONTACT CELL but the P2 stone's other 2-3 neighbors are wasted (either empty or own-side with less density). Meanwhile P1's isolated-side stones stack friendly-neighbor bonuses unchecked.

**P2 reflection (Game 3):** Direct contact doesn't pay; it's symmetric erosion. A better P2 deviation might be to PLAY FASTER CLUSTERS far from P1 (ignore P1's cluster and race) while delaying P1 with tactical-threat moves (ladder/capture feints). But with threshold=22.65 and 8×8 board, the race window is too short to afford the tempo loss.

**Endgame:** Resolved by threshold at move 25.

---

### Strategy guides

**As Player 1:** cluster early, cluster densely, and keep your cluster far from P2's. Because you move first, you reach each cluster-milestone one move before P2. Don't waste moves on scattered stones (they only give 0.932 to threshold vs 1.88–2.83 for cluster-extending moves). The opening 2-3 moves set the cluster seed; prefer diagonal of P2's first move (so their radius-1 influence doesn't erode yours) or adjacent to your own seed. Standard greedy sufficed to win in 23 moves.

**As Player 2:** mirroring loses by 1 tempo. You must deviate with an asymmetric investment. Candidate strategies I didn't explore exhaustively:
- **Capture race:** fork P1's cluster into two groups then reduce liberties. But this requires 5+ tempo-losing moves; likely too slow.
- **Block a 3-friend cell:** when P1 sets up a move with 3+ potential friend-neighbors (+3.78 move), pre-emptively take that square. This only works if you can predict P1's exact cluster shape.
- **Race an off-axis cluster:** build your cluster in a quadrant P1 cannot reach. With 64 cells and P1 claiming the center, this is feasible — but P1 will simply cluster faster by one tempo in their own quadrant.

Bottom line: P2 needs heuristics the pilot engine didn't find; random-vs-random confirms a 2:1 P1 advantage (20/30 P1 wins).

---

### Aggregate statistics from supplementary runs

- **Greedy vs greedy (deterministic):** 5/5 P1 wins, all in 23 moves.
- **20%-perturbed greedy:** 7/10 P1, 3/10 P2 (P2 wins when P1 randomly skips a cluster move).
- **Pure random vs random (30 seeds):** 20 P1 / 10 P2 / 0 draw / 0 max-turn. P1 win rate **67%**.
- **Double-pass draw rate:** 0/33 across all simulations.
- **Max-turn (100) rate:** 0/33.

No degenerate resolution modes observed.

---

## Phase 3 — Strategic Analysis (joint P1/P2)

**Acknowledged bias:** P1 and P2 roles were played by the same agent (me) in sequence. The Phase 2 playthroughs may share blind spots; Game 3 seat-swap partially mitigates this.

**Viable strategies.** The dominant strategic axis is **cluster-value-per-tempo**. The only non-trivial choice in the opening is:
- Where to seed the cluster (interior cells are strictly better because they have 4 potential friends vs 3 for edges and 2 for corners).
- Adjacent-to-friend vs one-space-gap (adjacent builds cluster immediately; one-space-gap preserves options but delays threshold credit by one move).

There is effectively **one dominant strategy**: claim center, grow a dense rectangular block, keep perimeter unopposed. I did not find a strategy that beats this with P1's first-move advantage.

**Meaningful counter-play.** Limited. As P2 you can:
- **Force contact and trade:** gives up own-cluster density for opponent erosion. Net neutral per contact cell; loses elsewhere.
- **Capture threats:** require 6–11 liberty fills (given cluster sizes of 7–11 stones by late game). Takes too long relative to 23–26-move game length.
- **Deny 3-friend cells:** tactical counter-play exists but requires perfect prediction of P1's cluster shape.

There IS short-term vs long-term tension: taking a +1.88 isolated move now vs a +2.83 cluster-extension move later. But the game is too short (~25 moves) for long-term planning to pay off.

**Emergent concepts observed:**
- **Territory & density:** yes, in a weak form. Large clusters produce compounding value; the cluster's own-cell sum grows super-linearly with size (N stones in a solid square ≈ N * (0.932 + 0.475 * avg_degree_inside_cluster)).
- **Tempo:** yes, critically. The game is a tempo race where each side's Nth "cluster-extension" move is +2.83. P1 always has one more such move than P2 at any balanced position.
- **Ko / repetition:** not applicable — captures rare (groups grow too fast to fall below 2+ liberties); when they happen, the captured cells become legal-again immediately (no ko rule implemented).
- **Initiative:** P1 permanently holds it in alternating threshold races.
- **Mutual annihilation:** not present (alternating game; stones don't collide).
- **Sacrifice:** I never found a winning sacrifice line — every sacrifice costs P1 ≈ 1 tempo, which P2 cannot convert without their own tempo loss.

**Topology mattering.** Very little. The 8×8 grid creates edge/corner asymmetry (edge stones have fewer neighbors), which makes interior play strictly preferred. But the game plays identically on any grid size where threshold is calibrated — there's no topology-specific tactic (unlike Hex's connection goal or Go's eye-making).

**First-mover advantage (quantified):**
- Greedy vs greedy: 5/5 P1 (100%).
- Random vs random: 20/30 P1 (67%).
- Perturbed greedy: 7/10 P1 (70%).
- In Game 1, sub-optimal P1 LOST to cluster-focused P2 → demonstrates the advantage is not hard-coded; skill matters at the margin. But against equal skill, **P1 wins deterministically**.

This is a **strong balance concern**. The game is NOT seat-balanced under optimal play.

---

## Phase 4 — Novelty Adversary (MANDATORY)

### Adversary opening statement

"This game is transparently **'Go with an arithmetic threshold instead of territory counting'**. Every rule element maps 1-to-1 onto existing abstract games. It contributes nothing new to the literature."

(a) **Direct analog comparisons:**
- **Go (13×13, 9×9, 7×7 variants):** 8×8 grid + place-anywhere + surround-capture-group is literally the Go placement/capture rule. The only change is how the game ends: Go counts territory at double-pass; this game counts a weighted sum of own-stone influence. This is a "scoring variant" of Go, not a new game.
- **Tumbleweed (Mark Steere):** threshold-style scoring on a hex grid with stacked stones. Different score formula, same conceptual move: place stones in your half of the board to accumulate score. The influence-radius-1 in d8f2ae54f399 is analogous to Tumbleweed's line-of-sight mechanic — both reward clustering.
- **Reversi/Othello:** propagation resembles Reversi's "flip enemy pieces you bracket" — here "flip" is replaced by "erode influence by 0.475", but same topological structure (orthogonal neighbours reciprocally affect each other's value).
- **Gomoku/Five-in-a-row:** threshold races on 8×8-15×15 boards with first-player advantage. Gomoku's 5-in-a-row is a first-player-wins game under best play (Allis 1994), exactly like this.
- **Go influence scoring (Bouzy, Mueller):** AI-Go literature has used the exact same exponentially-decaying influence field for territory estimation. This game literally IS a Bouzy-dilation-of-n territory estimator run as the win condition.

(b) **CA check:** N/A — this game has no cellular automaton (`uses_ca=False`). The propagation is a single-step linear influence kernel, not a life-like CA rule.

(c) **Simultaneous check:** N/A — this is an ALTERNATING game. None of Blotto, Diplomacy, or simultaneous-Go comparisons apply.

(d) **Topology re-skin:** the game is equivalent to Go played on an 8×8 grid where the scoring function is "sum over own stones of (0.932 + 0.475 × #friendly_orthogonal_neighbours − 0.475 × #enemy_orthogonal_neighbours)". This is a **thinly-disguised weighted territory count**. If you replaced the 0.932 and 0.475 constants with integer weights (e.g., 2 per stone, 1 per friendly-friend edge, −1 per enemy-friend edge), the game is unchanged modulo scaling. The threshold 22.645 corresponds to ~24 "stone-point-equivalents" — a classical Go-score quantity.

(e) **Expert test:** a strong Go player immediately recognises the core dynamic — "build large connected groups, avoid isolated stones, attack the enemy's weakest group, don't let your stones be surrounded". They would NOT need to learn any new concept. The only transfer gap is calibrating the exact threshold and realising captures are shallow (because influence scoring rewards density more than raw territory).

**Adversary verdict: novelty ≤ 3. This is Go with a specific weighted scoring rule.**

---

### P1/P2 rebuttal

We acknowledge the Go family lineage is undeniable: orthogonal placement + Go-style surround-capture is a direct structural import. However, **three concrete strategic moments from Phase 2 do not transfer from Go**:

1. **Clustering is strictly better than influencing territory** (Game 1 move 18). In Go, a large tight cluster is *wasteful* — you want stones at the edges of your territory controlling as much empty space as possible. Here, the opposite: a 3×3 solid block scores 19.8 (closer to threshold) while 9 stones spread 1-apart score only 9 × 0.932 = 8.4. **A Go expert would actively play BADLY here** by keeping stones far apart "efficiently".

2. **The radius-1 influence mechanic creates an "erosion contact zone" unknown in Go** (Game 1 move 25). When P1 plays adjacent to P2, BOTH stones' own-cell values drop by 0.475. This is symmetric mutual depreciation — a concept without a Go analog. In Go, stones adjacent to opponents are alive-but-contested; here they're arithmetically diminished. The tactical consequence is that neither side benefits from the contact line, which is the opposite of Go's "fighting is good".

3. **Threshold-race tempo math differs from territory counting** (Game 2, entire game). In Go the game ends at double-pass and the LARGER final territory wins, regardless of tempo. Here the FIRST player to cross 22.645 wins, with no mechanism to "catch up after the race closes". This creates a pure tempo game where P1's first move is mathematically decisive given equal skill — the greedy-vs-greedy result (5/5 P1 wins in 23 moves each) has no Go analog. Go's first-player advantage is ~6.5 points of komi; this game's first-player advantage, in effect, is the entire tempo margin.

Further points against specific analog candidates:
- **Not Reversi:** Reversi flips enemy stones; here enemy stones aren't captured until their group has zero liberties. Fundamentally different control mechanic.
- **Not Gomoku:** no line-shape required.
- **Not Tumbleweed:** Tumbleweed allows placing only within line-of-sight of existing own stones; this game is place-anywhere.
- **Not Bouzy's influence field (strictly):** Bouzy uses dilation-then-erosion on a discrete integer field; this uses continuous floats with a single decay step.

### Joint novelty score

The game IS much closer to a Go scoring variant than to a new abstract game. But the radius-1 erosion on contact is a non-trivial twist that changes optimal play at the moves 5–25 level. A Go expert gains a partial head-start (~70% transfer) but still must recalibrate toward tight clustering and tempo math.

**Novelty score (post-adversary): 4/10.**

- Not 2–3 because of the erosion-contact mechanic and the tempo-race end condition.
- Not 6+ because the place-anywhere + Go-surround-capture core is directly inherited, and no strategic concept emerges that isn't a re-weighting of Go ideas.

---

## Phase 5 — Verdict

**Team ID:** team-7
**Game ID:** d8f2ae54f399
**Rules summary:** 8×8 grid, alternating single placement, Go-style surround capture, radius-1 linearly-additive influence (±0.932 self, ±0.475 neighbor), first player to accumulate >22.645 own-cell influence wins; max 100 turns.
**Topology:** 8×8 non-toroidal grid (hard edges, 64 cells, von-Neumann neighbourhood).
**Turn structure:** ALTERNATING.

### Scores (1-10)

- **Strategic Depth: 4/10.** One dominant axis (cluster-value-per-tempo). Counter-play exists but is weak against a player who finds 3-friend extension cells. The game resolves within 23–26 moves under optimal play, leaving little room for multi-step planning, sacrifices, or positional subtlety. The tension between "build own cluster" vs "attack enemy cluster" collapses to a numerical swing calculation that a greedy 1-ply search solves reliably. No meaningful ko, no eye-making, no ladder tactics, no sente/gote beyond raw tempo.

- **Emergent Complexity: 4/10.** Cluster formation does exhibit emergent density effects — a 3×3 block is quantitatively much stronger than 9 isolated stones (19.8 vs 8.4 threshold contribution). That's a real emergent phenomenon: scaling is super-linear. But once this is understood, the optimal play is mechanical. No second-order emergent phenomena observed (e.g., no eye-shapes, no "living" vs "dead" groups, no shape-based heuristics).

- **Balance: 3/10.** **Strong P1 bias under optimal play.** Greedy vs greedy: 5/5 P1 in 23 moves. Random vs random: 20/30 (67%) P1. Perturbed greedy: 7/10 P1. Game 2 in Phase 2 was a clean mirror where P1 won by exactly one tempo's worth of value (+2.83). The balance failure is structural: threshold races under perfect symmetry always favour the first mover. Would require a komi-style offset or simultaneous moves to fix. This is a significant flaw given R15's new seat-balance heuristic probe — I suspect this game's metric score overstates true balance.

- **Novelty (post-adversary): 4/10.** Direct ancestry from Go (surround capture, orthogonal placement, empty-cell target). New elements are the continuous influence-with-erosion field and the threshold win condition. The erosion-contact mechanic is a real strategic twist (moves 5-25 of Phase 2 Game 1 showed this). But a strong Go player would transfer ~70% of their skill directly.

- **Replayability: 3/10.** Short games (20-30 moves). Once the clustering principle and tempo race are understood, strategic variety drops. Two experienced players would converge on near-identical openings and mid-games. The only variation is whether P2 attempts a denial strategy (doesn't work) or tries to race an off-axis cluster (doesn't work).

- **"Would I play this again?": 3/10.** Once. To understand the mechanic. Unlikely to sustain interest beyond a session or two given the P1 advantage and strategic shallowness.

### Closest known-game analog

**Go with a weighted-influence scoring rule (Bouzy-dilation-style territory estimation converted to a win threshold)**. Not identical because (1) the game ends at threshold rather than by double-pass + territory count, (2) surrounding captures use classic liberty-counting but are rare because clusters grow fast, (3) the influence field erodes symmetrically on contact — no Go analog. The novelty is confined to the scoring function, not the move structure.

### Killer flaws

1. **Structural P1 bias** under optimal play (5/5 greedy mirrors → P1 win by exactly one tempo). Random-vs-random probe gives 67% P1.
2. **One dominant strategy** (build densest cluster, prefer interior cells, defend cluster from enemy adjacency). Greedy 1-ply optimisation is near-optimal.
3. **Short decisive games** (23–26 moves typical under any competent play). Little room for multi-step tactics.

No engine-level killer flaws: no double-pass abuse, no unreachable threshold, no dead-rule (surround capture fires correctly; influence propagation works as documented). The `threshold=1` field in `capture_rule` is *dead code* (ignored by surround capture) — mildly confusing but not strategically degenerate.

### Best quality

The **continuous-influence erosion-on-contact** mechanic is the one genuinely interesting feature. When a P1 stone is adjacent to a P2 stone, both stones' threshold contributions drop by 0.475 — this is zero-sum on contact but creates an "avoid the enemy perimeter" heuristic that genuinely differs from Go's "fight in contact". It gives the game a quantitative texture that a pure Go-scoring variant wouldn't have.

### Improvement ideas

**Komi (simplest fix):** give P2 an initial +2.8 threshold offset (roughly one cluster-extension move's worth). This would flip the greedy mirror outcome to a near-draw and force meaningful play at the margin.

**Deeper fix:** switch to **simultaneous** turns (each tick both players place simultaneously, collisions empty both cells). This would eliminate tempo advantage entirely AND introduce the mutual-annihilation tactics that the R15 prompt suggests are the real strong axis. Given R15's hypothesis that "simultaneous alone is the real strong axis post-fix", re-running this exact rule set with simultaneous turns would be the most informative experiment.

**Alternative:** raise the capture threshold so that reducing liberties is a viable tactic (currently groups grow too fast to be captured). E.g., require 2 liberties instead of 0 — would make attacks strategically relevant and expand the tactical space beyond threshold-racing.

---

### Evidence checklist (R15 pilot concerns)

- [x] Double-pass ending: **not triggered** in any of 33 simulations. Game resolves by threshold.
- [x] CA step-loop: N/A (no CA in this game).
- [x] CA rule symmetry: N/A.
- [x] Seat-balance heuristic: **game FAILS heuristic balance**. 67% P1 win rate under random play, 100% P1 under greedy play. Flag for the R15 metric calibration team.
- [x] Threshold check-order (P1-first iteration): relevant only for simultaneous games, N/A here.
- [x] Torus wrap: N/A (grid topology).

### Verdict summary

Game d8f2ae54f399 is a **well-formed but shallow Go-scoring variant** with a fatal first-mover imbalance. The GE ranking of #2 (score 0.255) overstates its strategic merit: what the evolutionary pressure selected for is a game that is *easy for an RL agent to learn* (training winrate 1.0 vs random, fast convergence) and *has clean threshold resolution*, but these do not correspond to human strategic depth. The R15 seat-balance probe should have caught the structural P1 bias; our data suggests it did not penalise this game heavily enough.
