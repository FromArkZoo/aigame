# Genesis Run 13 — Team 1 Evaluation

**Team ID:** team-1
**Game ID:** 558e1f1be563
**Rank:** 2 (Go Essence 0.4864, ELO 1003.4)
**Classification:** CLASSIC (no CA), 2D hex, threshold win

---

## PHASE 1 — RULE COMPREHENSION

### Board & Topology
- **2D hex grid, 8×8 (64 cells)**, offset-coordinate hex adjacency
- Each interior cell has 6 neighbors; edge cells 3-4; corners 2-3
- No wrapping (not torus)

### Turn Structure
- Alternating, 1 piece per turn, 2 players, max 100 turns
- Action space: 64 placement actions + PASS (65 total)

### Action Types
- **Place only** (no movement, no capture)

### Placement Constraints
- Target: empty cells
- Constraint: **adjacent_to_any** (must touch any existing stone, either color)
- **first_move_anywhere: true** — applies whenever the current player has zero pieces.
  This means BOTH players' opening move is unconstrained, which I verified by test.

### Capture / CA
- **None.** Once placed, a stone is permanent.

### Propagation (Influence)
- `prop_type: influence`, `radius: 1`, `strength: 1.4192`, `decay: 0.4560`
- On each placement, add `±strength` to the placed cell (sign depends on player)
- Add `±strength * decay = ±0.6473` to each of the 6 (up to) neighbors of the placed cell
- Values clamped to [-100, 100]
- P1 contributes positive, P2 contributes negative

### Win Condition
- `condition_type: threshold`, `target_dimension: 0`, `threshold: 39.658`
- A player wins when the **sum of board_values on cells they own exceeds 39.658**
  (for P2 this is the magnitude of the negative sum)
- If max_turns (100) reached, fall back to **majority by piece count** (not by influence)
- Super-ko lazy-enforced engine-wide

### Degeneracy Scan
- Threshold 39.658 is reachable. A compact hex cluster of ~10–12 friendly stones gives
  each interior stone self=1.419 + ~4 friendly neighbours*0.647 ≈ 4.0 own-cell value, so
  10 compact stones ≈ 40 influence. Comfortable with ~50 moves available.
- The "adjacent_to_any" rule makes the overall stone graph one connected component,
  but players can still build interior blobs: enemy stones COUNT as "any", so P2 can
  extend away from the central contest by placing on the outer edge of P1's cluster
  without being blocked.
- Enemy stones on adjacent cells **reduce** own-cell influence by 0.647 each. So invading
  a cluster directly subtracts influence from the defender.
- Trained vs_random = 0.96 in both runs, self-play 50/50 — **no obvious P1 dominance in
  trained play**, though in greedy/2-ply hand-evals P1 had a tempo edge.
- Avg game length 31.5 turns — well below the max_turns cap. No escape-to-majority.

**No degeneracies flagged.** The game is well-formed and terminates cleanly.

---

## PHASE 2 — STRATEGIC PLAY

For every candidate move I ran `engine.step` through `GameEngineV2` loaded with the
actual rule set — every move reported below is engine-verified.

I played three full games. Because the same analyst drove both sides, I use three
different opening strategies and analyze each sides' motivations separately before
looking at the result. In Game 3 I seat-swap.

### Game 1 — Territorial Contact (P1: center, P2: adjacent invasion)

**P1 thesis:** Central dominance. Play (3,3)=27. Build a compact hex blob — each
interior stone yields 1.42+4×0.65 ≈ 4.0 influence, so ~10 stones → threshold.

**P2 thesis:** Invade the cluster. Each enemy stone adjacent to a P1 stone subtracts
0.65 from P1's own-cell value and also occupies a cell that would have been P1's.
So invasion doubles the damage — deny area + reduce remaining influence.

Move-by-move (engine verified):

| # | P | Move | Cell | Reasoning |
|---|---|------|------|-----------|
| 1 | P1 | 27 | (3,3) | Center — maximizes future blob neighbours |
| 2 | P2 | 35 | (3,4) | Mirror-adjacent; deny south expansion |
| 3 | P1 | 28 | (4,3) | Extend east along the contact line |
| 4 | P2 | 29 | (5,3) | Flank P1's new stone (reduces X@(4,3) by 0.65) |
| 5 | P1 | 20 | (4,2) | Go north, unblocked; builds triangle w/ 27,28 |
| 6 | P2 | 26 | (2,3) | Attack from the west |
| 7 | P1 | 19 | (3,2) | Solidify 2×2 block (3,2)(4,2)(3,3)(4,3) |
| 8 | P2 | 18 | (2,2) | Continue the wall on west flank |

After 8 moves: P1 has a 2×2 hex block, P2 has a curved enclosure around it.
Influence totals: P1=+6.1, P2=+4.8 (measured). P1 ahead by 1.3 and has denser block.

Continuing with 1-ply / 2-ply search (greedy + reply), final position after 29 turns:
- **Winner: P1** (influence 41.35 > 39.66 threshold)
- P1=41.35, P2=36.05. Pieces P1=15, P2=14.
- Both clusters mostly in top half of the board.

**P1 reflection:** Extending the cluster edge-first gave the most influence per move
because each new stone usually connected to 2-3 existing P1 stones. The 2×2 seed was
key — it converted the next 4 placements into 3-neighbour insertions.

**P2 reflection:** My invasions did reduce P1's cell values, but I paid a heavy cost:
my own stones had only 1-2 friendly neighbours because I couldn't pack as densely.
I should have seeded a second blob further away earlier.

### Game 2 — Separated Blobs (P1: center 27, P2: far corner 0)

P2 tries the "first_move_anywhere" escape: play (0,0) to build an independent cluster,
hoping that 16 stones packed in the NW corner can beat a contested central blob.

Verified: after P1=27, P2 CAN play 0 (legal, because P2's first placement is
first_move_anywhere). Legal-action set returned 64 actions after P1's move.

The game settled into **two blobs colliding around row 3**. Final state (29 moves):
- Winner: P1 (40.58 vs 31.39). P1 has 14 stones, P2 has 15.
- **P2 more stones but less influence** — P2's blob was stretched along the top edge
  (rows 0-1) which means many corner/edge stones with fewer friendly neighbours.

**Key strategic insight:** On an 8×8 hex, a blob that starts in the centre has more
room to form high-density interior cells than one in a corner. Corner cells only have
2-3 neighbours so stones there self-influence 1.42 with only ~1-2 friendly supports.
This makes far-corner first-move **dominated by center first-move** unless P2 can
migrate back toward the centre faster than P1 can consolidate — which she can't,
because P2 is always one tempo behind.

### Game 3 — Seat-swap: Player B as P1, Player A as P2, edge opening

To cancel seat-identity bias, the roles swap. P1 plays (3,0)=3 (top edge). P2 plays
(4,0)=4 adjacent.

Final after 25 moves:
- Winner: P1 (39.81 vs 37.09) — narrow win, threshold barely crossed
- Edge-opening is the weakest — top-edge cells have 3-4 neighbours max

**Seat-swap check:** Same analyst; bias acknowledged. Notably, even with a weak
opening P1 still won — reinforcing the tempo/first-move advantage hypothesis.

### Random-vs-random baseline (50 games)
P1=25 (50%), P2=11 (22%), draws=14 (28%). P1 has a notable baseline advantage but
not overwhelming — suggests komi-less tempo bias, not degenerate P1-wins-every-time.

### Strategy Guides

**P1 strategy guide.** Open at a deeply-interior cell like (3,3) or (3,4). On turn 2,
if P2 attaches to you, play the next cell that would give you a 2×2 hex block. From
there every 3rd or 4th move add a "tip" that pairs up with two existing friendly
stones — this is the fastest way to accumulate 4-neighbour interior cells. If P2
tries to build a separate blob, ignore them for 4-6 moves and keep densifying your
centre; your tempo advantage will carry you past threshold first. Only deviate to
block when P2 has committed 6+ stones to an independent cluster.

**P2 strategy guide.** You cannot win by aping P1's strategy one tempo behind. You
must either (a) invade the P1 cluster aggressively to poison its interior cells —
each enemy stone adjacent to a P1 stone subtracts 0.65 — or (b) open far from P1
and race with a denser blob, only if you can secure a 6+ stone anchor before P1
reaches threshold. In my play, option (a) was stronger because invasion both
blocks P1's potential growth cells and subtracts from existing cells, but it
requires discipline: every invading stone must have at least 2 friendly neighbours
of its own eventually, or it leaks influence to P1's surround.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Distinct viable strategies?
Two clearly distinct macro-strategies exist for both players:
1. **Blob-build (cluster-first)**: maximise own influence density
2. **Invasion (contact-first)**: reduce opponent influence by placing adjacent

They can be mixed; a typical trained-agent game alternates between densifying
and spot-poisoning. The invasion strategy is meaningfully different because the
*same* board cell has different value to you depending on whether you're scoring
or denying. This is a genuine strategic tension.

### Counter-play
Yes — if P1 plays pure blob-build, P2 can invade; if P2 invades, P1 can race to
threshold because each invasion stone is a stone P2 can't use for its own blob.
This is a rock-paper-scissors-ish triangle: blob beats slow invasion, invasion
beats slow blob, but both lose to a well-timed hybrid.

### Short-term vs long-term tension
Yes. Playing adjacent to an enemy **reduces P1's own-cell value at that cell by
0.65** if the enemy stone is inside P1's cluster surround. Short-term loss for a
long-term racing advantage is a real decision — e.g. playing a "poison" stone
that has no friendly neighbours but subtracts 1.3-2.0 from enemy influence.

### Emergent concepts
- **Tempo** — P1's extra move is decisive at high skill levels (random-game bias
  50%/22%/28%)
- **Territory** — clusters naturally form; contested borders appear
- **Influence arithmetic** — every placement is simultaneously +1.42 to own total
  and up to -3.9 to opponent's adjacent cells
- **Compactness vs reach** — players must decide between densifying existing blobs
  (high marginal influence per move) vs extending (creates future dense cells)
- **No ko, no captures, no propagation chains** — influence is strictly local

### Topology relevance
Yes, hex really matters. A square grid (4-neighbour) would make each stone's
max interior value 1.42 + 4×0.65 = 4.0, versus hex 1.42 + 6×0.65 = 5.30. Hex
dramatically boosts the marginal value of interior cells — you cross threshold
faster. Also, hex eliminates the diagonal-blocking asymmetry of Go so "eyes" and
"liberties" concepts don't translate; this is not Go on a hex board.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary brief

**Adversary:** "This game is a trivial variant of Reversi/territory Go with a
cosmetic hex skin. Let me enumerate:

(a) **Known games.** The influence-threshold mechanism is a direct simplification
of Reversi's disc-flipping. The 'most stones win' fallback at max_turns is
literally Reversi's win rule. Hex placement + majority is close to "Y" without
its connection condition. Adjacent-to-any placement with no capture is just
"Ataxx without jumps" or "Blokus on a hex grid without piece shapes." The
influence propagation is just a smoothed counter — it's equivalent to weighting
each stone by `1 + 0.456 × (friendly-neighbour count)` and summing. That's not
a new dynamic, that's Shannon-Entropy-smoothed Reversi.

(b) **CA-based analogs** — N/A (classic game, no CA).

(c) **Topology/coordinate transformation argument.** Map each hex cell to its
centroid in a skewed axial coordinate system. The resulting graph is 6-regular.
Now pick up any Reversi-like influence rule on a 6-regular graph: the game
reduces to "place on connected component; score weighted by degree." This is
isomorphic to Havannah's edge-cell bonus mechanism — a known game from 1979.

(d) **Expert-at-known-game test.** A strong Go player would immediately
recognise the 'fill to take the most central territory' strategy. A Hex player
would see the 'adjacent-to-any' constraint as similar to Hex's must-connect rule
in reverse. An Othello/Reversi expert would see the influence field as a soft
flip — the +0.647 contribution from each neighbour is literally a linearised
version of 'you flipped a disc.' A Reversi expert would have a substantial
advantage here because they already think in influence-radiation terms.

Therefore: Novelty = 3/10. This is 'Reversi without flips, on a hex grid,
with a soft-gate threshold win.'"

### Rebuttal

**Specific rebuttals citing Phase 2 moments:**

1. **The "no-flips Reversi" claim fails on invasion arithmetic.** In Reversi, a
   played stone either flips neighbours or it's illegal. In 558e1f1be563, an
   enemy stone *adjacent to your cluster* permanently subtracts from your own-
   cell value — but YOUR stone keeps its own 1.42 plus friendly contributions.
   The stone is never "flipped." In Game 1 move 4 (P2 plays 29), P1's stone at
   (4,3) has its own-cell value go from +2.71 to +2.07 because P2 added -0.647.
   No existing Reversi derivative has this "permanent local taxation" dynamic.

2. **The "hex Y/Havannah" claim ignores that there's NO connection condition.**
   Connection on hex is Hex/Havannah/Y's whole game. Here, you can win by having
   two disconnected blobs whose *sum* of own-cell values exceeds threshold. In
   Game 2 P2 had a 15-stone connected blob but lost to P1's smaller single blob,
   because blob *density* matters, not blob *connection*.

3. **The "Ataxx without jumps" claim is wrong on the win condition.** Ataxx and
   all jumping games end when no legal moves remain or the board fills. This
   game can end at turn ~15-30 well before the board is full because of the
   continuous-valued threshold. The game has a growing-gradient rather than a
   full-consumption terminal state.

4. **The "adjacent_to_any + first_move_anywhere" interaction is genuinely new.**
   I verified that P2's first move can be anywhere, creating a possible-but-
   dominated far-separation strategy. No Reversi/Hex/Y/Othello variant I know
   of has this two-tempo first-move-free rule combined with permanent stone
   placement and influence scoring. Game 2's far-corner test was a distinct
   strategic line that required Phase-2 play to evaluate.

5. **"Expert at Reversi has an advantage" test.** Partially true — Reversi
   players understand edge/corner value. But the hex topology means corner
   cells are STRONGER in Reversi (protected from flips) and WEAKER here (fewer
   neighbours → less own-cell influence). A strong Reversi player would play
   corners and lose. Game 2 demonstrates this: P2 played (0,0) corner first,
   and lost partly because the corner only contributes self=1.42 plus at most
   2 friendly neighbour bonuses = 2.71 max.

**Verdict on novelty:** The game is recognisably in the "influence + hex"
family (related to Go-like territorial games, soft-Reversi variants, and
abstract hex games), but its exact combination — continuous influence
threshold, permanent placement, adjacent-to-any growth, per-player
first-move-anywhere — is not a straightforward re-skin of any single known
game. It's in the same family-tree as Run 10's Go×Hex hybrid (`d4015a646ae3`
and seed `484fcb3b0471`). Not genuinely new abstract game — but not a trivial
re-skin either.

**Novelty score awarded: 4/10.** Family-member, not clone.

---

## PHASE 5 — VERDICT

**Team ID:** team-1
**Game ID:** 558e1f1be563
**Rules Summary:** On a 2D 8×8 hex grid, players alternately place one stone per
turn (adjacent to any existing stone, or anywhere on their first move). Stones
radiate influence (+1.42 self, +0.65 to 6 neighbours, signed by player). First
player whose own-cells sum to >39.66 influence wins; max 100 turns.
**Topology:** 2D hex, 8×8, von Neumann hex adjacency (6-neighbour interior, no
wrapping).

### SCORES (1-10)

- **Strategic Depth: 6** — Real tension between blob-densification and invasion-
  poisoning. Influence arithmetic makes every placement multi-objective
  (own-value + neighbour-bonus + enemy-denial). But no captures, no ko, no
  movement means the decision tree per turn is shallower than Go. Agent
  reaches 96% vs random — learnable.

- **Emergent Complexity: 5** — Territory, tempo, and density naturally emerge,
  but there are no surprising high-level phenomena like ko fights, sacrifice
  tactics, or ladders. The game is well-behaved without being rich.

- **Balance: 6** — Random-vs-random shows P1 advantage (50% vs 22%), but
  trained self-play after seat-swapping reached 50/50. Under reasonably strong
  play, the first-move advantage is substantive but not decisive. A small
  P2 compensation (komi-like) would improve this to 8-9.

- **Novelty (post-adversary): 4** — Rebutted the "Reversi re-skin" claim on
  several concrete grounds (Phase 2 game 1 move 4 subtraction evidence, Phase
  2 game 2 demonstrating density beats connection). But the mechanic is still
  firmly in the influence-threshold family pioneered by earlier Run-8/Run-10
  hex champions (`d4015a646ae3`, `484fcb3b0471`).

- **Replayability: 5** — 8×8 is a tractable space with ~20 credible opening
  lines and meaningful mid-game choice. However, absence of capture/movement
  means games will feel similar after ~20 plays. Fresh for casual but not
  for dedicated study.

- **Overall "Would I play this again?": 5** — Pleasant once or twice. Not a
  game I'd return to repeatedly the way I would return to Go or Hex.

### CLOSEST KNOWN-GAME ANALOG
**Closest analog:** Go-lite on hex with smooth territorial scoring
(equivalently: "Reversi without flips, win by threshold on a hex grid"). It
is not identical because (a) stones are permanent (not flipped), (b)
connection is not required, (c) the threshold is continuous so games end
mid-board, (d) per-player first-move-anywhere creates strategic two-blob
options absent from both Go and Reversi.

### KILLER FLAWS
- **P1 tempo advantage without komi.** In random play 50% vs 22% suggests a
  meaningful first-move bias. Trained play is 50/50 only because of
  seat-swapping during evaluation. Without a tie-breaker or P2 compensation,
  strong perfect play likely favours P1.
- **Endgame incentives collapse once a player is clearly ahead.** After one
  player commits to the winning blob (roughly turn 15-20 of a 31-turn average
  game), the trailing player has no recovery mechanism — no capture means no
  comeback.
- **No-pass equilibrium unclear.** The influence-gain-per-stone is always
  positive for whoever places (owing to self-contribution 1.42), so passing
  is strictly dominated. Good: no pass exploits. Neutral: no pressure
  testing of the pass-majority fallback.

### BEST QUALITY
The influence-subtraction-via-adjacency creates a genuine dual-purpose
placement decision — every stone is both offence and defence by arithmetic,
not by binary-capture logic. This "continuous poisoning" dynamic is the
most interesting property of the game and distinguishes it from its
discrete-capture cousins.

### IMPROVEMENT IDEAS
Add a **komi of +1.5 influence to P2's running total** (or equivalently a
handicap stone on P2's first move). Random-vs-random P1 advantage suggests
P2 needs ≈2 own-cells' worth of compensation. This single tuning parameter
would move Balance from 6 to 9 without changing any rule mechanics, and
likely push the self-play score beyond a pure tempo-race.

---

**Concise Verdict:** A competent, well-formed hex influence-placement game
in the same lineage as Run 8/10 champions. Real strategic depth via the
invasion-vs-blob tension but no emergent deep-tactic layer. P1 tempo bias
is a real balance concern. Not a trivial re-skin, but not genuinely novel
either — a family member.

**Final Scores:** Depth 6 / Emergent 5 / Balance 6 / Novelty 4 /
Replayability 5 / Would-play-again 5. **Aggregate: 5.2/10.**
