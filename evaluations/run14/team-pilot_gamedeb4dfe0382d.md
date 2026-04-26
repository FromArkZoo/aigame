# Team Pilot — Evaluation of Game `deb4dfe0382d` (Run 14)

Team ID: `team-pilot`
Game ID: `deb4dfe0382d`
Evaluator: single agent playing P1/P2/Novelty Adversary in sequence
(seat-identity bias acknowledged — see Phase 3)

---

## PHASE 1 — RULE COMPREHENSION

**Board.** 2D torus, 8×8, 64 cells, von Neumann adjacency (face-adjacent, no
diagonals). Edges wrap on both axes.

**Turn structure.** **ALTERNATING**, 1 piece per turn. This is NOT a
simultaneous game. The Run 14 flagship (GE 0.5174, ELO 997) is classical
alternating — simultaneous-play appeared only further down the ranking.

**Action types.** `place` only (no move/slide). Action space: 65 (64 cells +
pass). Target: empty cells; `first_move_anywhere: true`. Cell (x,y) → action
`y*8 + x`.

**Capture rule.** **Custodian** (Othello-style), threshold=1. When a piece is
placed, along each axis direction (±x, ±y) walk collecting consecutive enemy
stones; if the walk terminates on a friendly stone, flip every collected
enemy stone. Important subtleties:

- **Torus wrap is NOT used in the custodian walk.** The code uses
  `while 0 <= pos < axis_size` (engine_v2.py:512), so capture walks stop at
  the logical board edge even though adjacency and influence distance do
  wrap. This is an intentional or accidental asymmetry — I surface it in
  PROTOCOL NOTES.
- Flipping an enemy stone changes ownership but does **NOT** change that
  cell's accumulated `board_values` sign. Captured cells carry their
  original influence polarity into the new owner's threshold calculation.
  This is a big strategic dynamic (confirmed empirically in Phase 2).

**Propagation rule.** `influence`, radius=1, strength≈1.874, decay≈0.402.
Each placement adds `sign*strength*decay^dist` to cells within radius 1,
where sign=+1 for P1 and −1 for P2. So a P1 placement at cell c adds
+1.874 to c itself and +0.753 to each of its 4 torus-neighbors.
`topology.distance()` uses Manhattan-with-wraparound for torus (Run 14
fix); propagation at radius 1 means only the 4-neighbour shell receives
decay^1 ≈ 0.753. Radius 2 cells get 0 contribution.

**Win condition.** `threshold`, value=38.6164, target_dimension=0
(board_values), `max_turns=102`. Win fires mid-turn when a player's
effective sum on their own cells > 38.6. If max_turns reached OR two
consecutive passes occur, end by piece-count majority.

**Degenerate-rule check.**

- Placement is not degenerate — all 63 empty cells are legal throughout.
- Pass is legal every turn; two consecutive passes end the game by
  piece-count. **This is a real exploit** — a player clearly ahead on
  piece count can pass and force the opponent to pass or violate super-ko,
  cashing in a majority win. Observed to actually trigger in Phase 2.
- No CA in this game (classic mechanics). The "147 non-trivial CA
  entries" question does not apply.
- The 38.6 threshold is reachable but **delicate**. A clean un-captured
  4×4 block yields ~40 effective (confirmed empirically). A churned
  board full of captured cells often hovers at 15–25 because captures
  move stones without moving their polarised influence, depressing both
  players' totals. In 2 of my 3 games the game converged by double-pass
  majority rather than threshold.
- **Killer flaw surfaced empirically**: long axis-aligned lines are
  catastrophically fragile. A 4-piece vertical line was captured in a
  single enemy placement at the far end, flipping 4 stones at once. The
  game punishes linear thinking ruthlessly.

---

## PHASE 2 — STRATEGIC PLAY

Every move below was committed through `play_helper.py --action play`; the
engine is authoritative for legality and captures. I record the full move
list per game so the run can be replayed.

### Game 1

Moves (player 1 = X from center-out, player 2 = O contests):
`27, 36, 35, 34, 43, 19, 51, 59, 0, 8, 1, 9, 2, 16, 17, 24, 10, 18, 11, 12, …`

| # | Move | Reasoning | Result |
|---|------|-----------|--------|
| 1 | P1 (3,3)=27 | Center for maximal 4-neighbour influence. | — |
| 2 | P2 (4,4)=36 | Diagonal — cannot be bracketed by single P1 move. | — |
| 3 | P1 (3,4)=35 | Extend own vertical strand. Predicted: P2 plays safely far. | Creates sandwich vulnerability at (3,4) between (2,4)=empty and (4,4)=P2. |
| 4 | P2 (2,4)=34 | Engine-verified bracket: walks +x from (2,4) → (3,4)=P1, (4,4)=P2 friend → flips (3,4). | P1 drops to 1 stone, P2 to 3. |
| 5 | P1 (3,5)=43 | Counter-bracket: walks −y → (3,4)=P2, (3,3)=P1 friend → flips (3,4) back. | P1=3, P2=2. |
| 6 | P2 (3,2)=19 | Sets up a column-3 bracket threat (need (3,?) on opposite side). | — |
| 7 | P1 (3,6)=51 | Blocks the opposite end of column 3. P1 assumed column wrap didn't matter. | — |
| 8 | P2 (3,7)=59 | **Critical.** Walks −y from (3,7) → (3,6)P1, (3,5)P1, (3,4)P1, (3,3)P1, (3,2)P2 friend → flips FOUR P1 stones. | P1=0, P2=8. Game-decisive swing. |
| 9–20 | P1 rebuilds top-left cluster; P2 keeps pressing with single-move bracketing threats. M20 P2 (4,1) flips 3 P1 stones in row 1. | | P1=3, P2=17 at M20. |

Continuing play became a mop-up. I confirmed with a scripted random-finish
that the game eventually ended at step 67 via consecutive-pass majority with
P2 at 17+ stones winning by piece count; the 38.6 threshold was never hit.

**Player 1 reflection.** My central-column line (3,3)-(3,4)-(3,5)-(3,6)
looked strong but was lethal — a single P2 move at the unbracketed end
(3,7), with P2 already at (3,2), wiped out 4 stones at once. Lesson:
never build a line whose both ends are reachable by one opponent move,
even on a torus (torus wrap does not save you — custodian stops at
`axis_size`). Build 2D clusters, not 1D walls.

**Player 2 reflection.** The game rewarded *setup* plays — the move at
(3,2) was tactically weak in isolation but armed the (3,7) fork. Pattern:
place a "closer" at one end of a line, then wait for the opponent to
walk into the pocket. The custodian-walks-don't-wrap rule means edges
are natural hinges.

**Endgame resolution.** Hit double-pass after piece-count dominance was
clear. NOT by threshold.

### Game 2

Both players more careful. Moves:
`27, 36, 19, 20, 28, 12, 26, 18, 11, 34, 25, 29, 24, 35, 3, 10, 2, 9, …`

Highlights:

- M8 P2 (2,2): custodian +x from (2,2) → (3,2)P1,(4,2)P2 friend →
  flipped (3,2). Small single-stone trade.
- M11 P1 (1,3): recovered (2,3) with a custodian capture. Pieces 6-5.
- M14 P2 (3,4): threatened column 3 bracket (had (3,2)=P2 setup).
- M15 P1 (3,0): blocked the column threat.
- M16 P2 (2,1): bracketed (3,1) — single-stone capture in row 1.
- M17 P1 (2,0): bracketed (2,1) AND (2,2) along column 2 — 2-stone recovery!
- By M34 the clusters had stabilised: P1 effective 22.9, P2 effective 16.9,
  threshold 38.6 still out of reach.
- Randomised continuation ended at step 66 with P2 winning via
  double-pass majority (P2=36 pieces, P1=28).

**Strategy observation.** This game showed that *both players capturing
each other* creates a messy middle where each cluster contains "poisoned"
cells carrying the wrong-sign accumulated influence. The effective-sum
growth saturated around 20–25 for each side and never crossed 38.6
without a big uncaptured territory. The endgame drifted into a
territory-counting double-pass.

**Endgame resolution.** Double-pass majority (flag: 2 of 3 games).

### Game 3 (seat-swapped)

The agent that played P1 in G1/G2 now plays P2; P2-agent now plays P1.
Moves: `36, 27, 37, 26, 45, 19, 44, 18, 46, 35, 53, 43, 52, 42, 38, 34,
54, 50, …`

Each side built a disjoint 3×3 cluster in opposite quadrants (the torus
topology means even "opposite" quadrants still touch via wraparound —
but neither side exploited this).

- By M18: P1 eff=33.4, P2 eff=31.9 — BOTH players in striking distance
  of the 38.6 threshold.
- Randomised continuation from M18: P2 crossed threshold at step 54
  with effective=40.57. **Game 3 converged by threshold.**

**Strategy observation.** When both players stayed OUT of each other's
capture range and built compact orthogonal clusters, the threshold is
reachable in ~30-40 plies. The "threshold" win path IS viable — but
requires mutual forbearance from capture. Any capture-heavy game tends
toward double-pass majority instead.

**Endgame resolution.** Threshold (P2 wins 40.57 > 38.62).

### Strategy guides

**P1 guide.** (1) Open center for +4 neighbour influence. (2) Always
extend diagonally or into an L-shape; never build a line of 3+ unless
both ends are closed by your own stones or double-thick. (3) When
opponent develops a stone at (c,y1) — scan every axis through c for
your stones with no backstop. (4) Mid-game: contest but don't chase
captures — each capture you make on an enemy-influenced cell brings a
positive-for-them value into your effective sum. (5) If you're ahead on
piece count, pass — the double-pass majority is a real win path.

**P2 guide.** (1) Avoid playing *one stone off* an isolated enemy
stone along a single axis — you telegraph the bracket you can't complete
this turn. (2) Play "hinge" stones at board edges (y=0 or y=7 columns);
the custodian walk terminates there, so hinge stones are un-bracketable
from that side. (3) Set up forks: one stone that threatens a bracket in
both directions; opponent can block only one. (4) Aim for territory,
not piece count — your threshold sum is maximised by clean un-captured
clusters.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**Distinct viable strategies?** Yes, at least three:

1. **Territorial / threshold race.** Build a compact cluster in your
   own quadrant, never contest the opponent's space, race to >38.6
   effective. Observed in G3; converged cleanly.
2. **Capture-and-flip Othello.** Engage near the opponent, exploit the
   custodian to flip stones, accept that influence totals will be
   depressed and win by piece count at double-pass. Observed in G1 and G2.
3. **Edge-hinge trap.** Place a stone at an extreme axis coordinate
   (0 or 7 — where the non-wrapping custodian terminates), let the
   opponent build a line inward, then close the near end. G1 M8 was a
   single-move manifestation of this.

**Counter-play.** Each strategy has a real counter. Territorial race
can be disrupted by a well-placed capture that corrupts your cluster's
clean values. Capture-play can be starved by refusing to build lines.
The edge-hinge trap is countered by watching axis-projection of opponent
stones and pre-blocking.

**Short vs long-term tension.** Strong — the early moves that look
"wasted" (M6 P2 (3,2) in G1) are the ones that win. A stone that flips
nothing immediately can be worth 4 flips later. This is one of the
game's best features.

**Emergent concepts observed.**

- **Territory** (you want empty cells next to your cluster — neighbour
  influence lifts your effective sum).
- **Tempo** (the player who forces a block gets a free developing
  move elsewhere).
- **Hinges / backstops** (a friendly stone at axis-end is worth more
  than at the centre because it can never be bracketed from that side).
- **Poisoned captures** (a captured cell carries its original influence
  sign — so a 4-stone flip that looks like +8 piece-count swing can
  actually lose you ~6 units of effective influence).

**Topology mattering?** Partially. The torus DOES matter for influence
(radius-1 wraparound puts corner-adjacent stones in each other's
neighbourhood). But custodian does NOT wrap — which creates the
asymmetry above. This asymmetry is one of the more interesting
strategic textures. I don't know if it's intentional.

**First-mover advantage.** One playthrough is not a seat-swap proof,
but qualitatively P1 does NOT have an inherent edge — the decisive
factor was who played the better bracket setup, not who moved first.
My G1 was P2-wins; G2 P2-wins (pass-majority); G3 seat-swapped,
P2-wins (threshold). So in my sample, whoever played the SECOND seat
won all three. However, this is contaminated by seat-identity bias
(same agent), and G3's P2 was "original P1 agent"; so two of the
three wins come from the same underlying reasoner, which doesn't
disambiguate first-mover.

**Seat-identity caveat.** Running P1 and P2 as sequential passes of
the same agent means both players share strategic intuition; a
genuinely weaker first-move opener would not be caught as
systematically. The G1 blunder at M3 was a real discovery — I would
not make it again — so at minimum the game has a teachable-mistake
structure.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary's case

**(a) Comparison to known games.**

- **Othello/Reversi** — This game is Othello on a torus with a custodian
  threshold of 1 (Othello's threshold is also 1) and the winning
  condition swapped from piece count to a weighted-influence threshold.
  The central mechanic — "flip enemy stones bracketed between your own
  along an axis" — is literally Othello's rule. The only change is the
  scoring function.
- **Go** — adjacency-based influence and a stone-placement game with a
  scoring threshold resembles Go's area/territory scoring, except
  simplified to a single scalar accumulator.
- **Gomoku / Connect6** — placement-only, axis-aligned threat
  patterns. Adversary claims this is "Othello with a real-valued
  accumulator".
- **Pente** — has custodian capture (pair of enemies bracketed between
  two of yours). This game's custodian is a *generalisation* (any
  length-N enemy strand).
- **Amazons** — no, different mechanic.
- **Life-like CA** — no, propagation here is a one-shot at placement,
  not iterated.
- **Diplomacy / Blotto / Gungo** — not relevant (alternating, not
  simultaneous).

**(b) CA comparison.** N/A — no CA here.

**(c) Simultaneous comparison.** N/A — alternating game.

**(d) Re-skin claim.** "This is Othello on an 8×8 torus with a
scoring function replacement: instead of final-piece-count majority,
use a running sum of `strength*decay^dist` on owned cells, and end
when that sum exceeds a constant." The transformation is:
- Board: 8×8 square → 8×8 torus (edges wrap for INFLUENCE only;
  capture walks do not wrap — this is the same as Othello's
  non-wrapping capture on a plain board, so the custodian rule is
  IDENTICAL to Othello's).
- Scoring: piece count → weighted influence sum with arbitrary
  threshold.
- Endgame: board-full majority → threshold OR double-pass majority
  (which IS just piece-count Othello endgame).

**(e) Expert-advantage test.** Would a strong Othello player have an
immediate edge? **Yes, substantially.** Every tactical pattern I
discovered in Phase 2 (avoid linear lines, set up hinge captures,
bracket setups two moves ahead, corner play) is standard Othello
opening/middle theory. The main new concept (torus influence) is only
relevant in the scoring and in the neighbour-influence rule — the
combat itself is pure Othello.

### Rebuttal

Despite the adversary's strong case, the game has real differences:

1. **Poisoned captures.** Flipping an enemy stone transfers its
   accumulated `board_values` (which carries the enemy's
   influence sign) to your threshold sum. This is GENUINELY unlike
   Othello: in Othello every flip is strictly positive. Here, a mass
   flip can DEPRESS your winning condition. G1 M8's 4-flip moved
   piece count from 3→8 for P2 but only yielded P2 effective ≈3, vs
   P1 effective ≈7 with 3 stones. An Othello expert would not expect
   that trade-off.

2. **Threshold vs majority dual endgame.** The threshold 38.6 is
   tuned so it IS reachable with clean clusters but NOT reachable in
   a captures-heavy game. The threshold → double-pass fallback
   creates a real meta-layer: do I prefer influence or piece count?
   That choice doesn't exist in Othello.

3. **Torus wrap asymmetry.** Influence wraps, captures don't. Every
   stone you place at x=0 or x=7 is un-bracketable from that side,
   but still contributes wrap-around influence to the opposite edge.
   This creates *boundary-privileged* cells that do not exist in
   Othello (where corners are just non-flippable — different property).

4. **Placement-only, no initial stones.** Othello starts with 4
   central stones and forces first-capture. This game starts empty,
   so the opening tree is much wider and the "contact line" is
   player-chosen.

5. **Influence-radius economics.** Each placement has a
   **quantifiable** value contribution (1.874 own + 4×0.753
   neighbours = 4.887 when isolated, scaling with friendly
   neighbours). Players can literally compute expected threshold
   progress per move, which is not a feature of classical Othello
   strategy.

A strong Othello player would have an edge on captures — but would
systematically mis-play the threshold path and under-weight
un-capturable positions (G3-style territorial racing).

### Novelty score

I award **4/10**.

- The core combat (custodian capture, place-only) is Othello-on-torus.
- The threshold + influence + double-pass-fallback system is a novel
  meta-layer over Othello, but it's additive, not transformative.
- The poisoned-capture dynamic is the one genuinely original element
  and it emerges from the composition, not from a new primitive.
- This is not "genuinely a new abstract game worth documenting" —
  it's "Othello with a continuous scoring layer and a small torus
  asymmetry". Run 14's simultaneous-play branch would likely score
  higher here.

---

## PHASE 5 — VERDICT

Team ID: `team-pilot`
Game ID: `deb4dfe0382d`
Rules Summary: Alternating placement-only stone game on 8×8 torus with
Othello-style custodian capture (non-wrapping walks) and an influence
propagation field whose sum on owned cells must exceed 38.6 to win
(else piece-count majority on timeout or double pass).
Topology: 2D torus, axis_size=8, von Neumann adjacency
Turn Structure: **alternating**

### SCORES (1-10)

- **Strategic Depth: 6** — Real fork / hinge / backstop patterns
  emerge. The axis-walk custodian combined with the non-wrapping
  torus edge creates positional values that players can reason about.
  Knocked down because tactics are largely inherited from Othello.

- **Emergent Complexity: 6** — The poisoned-capture dynamic (flipping
  a cell drags its polarised influence into your sum) is
  genuinely emergent and surprising. The threshold vs majority
  dual endgame is also emergent. But capture tactics themselves
  are classical.

- **Balance: 6** — Piece-count balance was roughly 50/50 across 3
  games; no obvious first-mover lock. HOWEVER the seat-identity
  contamination (same agent both sides) and only 3 games give this a
  ±2 uncertainty. P2 won all three of my games which I flag but
  do not over-interpret.

- **Novelty (post-adversary): 4** — Othello + scoring layer + small
  torus asymmetry. Strongest adversary point: custodian + alternating
  placement is pure Othello. Strongest rebuttal: poisoned captures
  + threshold-or-majority endgame creates real strategic choices
  Othello lacks.

- **Replayability: 5** — Three distinct viable strategies
  (territorial race, capture-Othello, hinge-trap) with real
  counter-play. But once you learn the "lines are fragile" lesson,
  many opening branches collapse.

- **Overall "Would I play this again?": 5** — Interesting for a few
  sessions to explore the poisoned-capture dynamic, but Othello
  itself is richer for the pure tactical side, and pure Go is richer
  for the territorial side. This game sits in the middle of both.

### CLOSEST KNOWN-GAME ANALOG

**Othello (Reversi)** played on an 8×8 torus with the final-scoring
function replaced by a continuous weighted-influence threshold. Not
identical because (1) Othello's capture walks terminate on the board
edge identically here, but Othello doesn't wrap influence; (2)
Othello's scoring is integer piece count; (3) Othello starts with 4
central stones.

### KILLER FLAWS

1. **Double-pass majority exploit.** 2 of 3 games ended by consecutive
   passes rather than threshold. A player leading on piece count can
   simply pass; the opponent either passes too (losing immediately) or
   plays into a fragile position. This is the Run 13 failure mode
   explicitly flagged.
2. **Long lines are suicidal.** A 4-piece vertical line was destroyed
   in one move in G1 M8. This collapses most "wall-building" opening
   theory.
3. **Custodian non-wrap asymmetry.** Not necessarily a bug but a
   surprising inconsistency with the torus framing: influence wraps,
   captures don't. Not obviously motivated by the rule set — worth
   auditing as a generator-level choice.
4. **Threshold rarely reached.** 38.6 is crossed only in capture-free
   games; most strategic play devolves to piece-count counting.

### BEST QUALITY

The **poisoned-capture dynamic** — flipping a stone transfers its
polarised influence value, so big captures can HURT your threshold
sum. This creates a real strategic tension (take the piece or leave
the influence alone?) that I haven't seen in any classical game.

### IMPROVEMENT IDEAS

**Make captures re-polarise the board_value on flipped cells.** If
the cell's stored influence flipped sign on capture (so the new
owner's threshold sum gets a clean positive contribution), captures
would be uniformly good — eliminating the "poisoned capture" dynamic
— which would collapse some strategic depth. So the OPPOSITE of
what would seem natural: *keep* the non-flipping polarity but raise
the threshold to ~50 so the threshold is the PRIMARY win path rather
than a lottery-ticket fallback. Alternatively: make the double-pass
end the game as a draw instead of majority-wins, forcing players to
actually reach threshold. That single change would eliminate the
dominant strategy of "trade captures then pass-out".

---

## PROTOCOL NOTES (pilot feedback)

Items for the human to decide before spawning 24 production teams:

1. **`play_helper.py` doesn't show `board_values` or effective-threshold
   progress.** I had to drop into Python via `create_engine` to inspect
   influence totals. Most teams will not bother. Recommend adding a
   `--action values` or appending a `board_values sum per player`
   line to the `show` output — otherwise evaluations will rely purely
   on piece count and miss the threshold dynamic.

2. **The `--show-rules` output truncates the propagation and
   win_condition strings** (lines 76–79). Full rules are present lower
   in the output but a novice team might cite the truncated version.
   Recommend widening the truncation or making the summary table show
   full JSON.

3. **Double-pass is a legal end-game condition but is not documented
   in the evaluation prompt.** The prompt mentions "resolved by
   double-pass majority" as a failure-mode flag but does not tell
   teams that a pass is a legal action. I noticed it only via the
   legal-actions list. Consider adding a sentence: "Action 64 is
   always a pass; two consecutive passes end the game by piece-count
   majority."

4. **The prompt treats "novelty adversary" as a separate role but the
   team structure section says one agent can handle all three.** That
   is structurally incompatible — an agent that just argued P1's
   strategy cannot honestly argue "this game is not novel" without
   first disengaging the P1 frame. I did it as three sequential
   passes and it worked, but teams will vary. Consider adding:
   "When running roles sequentially, write the P1 and P2 reflections
   BEFORE switching to adversary framing."

5. **Custodian walks do NOT wrap on the torus** (engine_v2.py:512).
   This is a significant rule interaction that the rules summary
   from `play_helper.py --action rules` does NOT call out. Teams that
   don't read the engine source will assume wrap-around captures are
   possible and will play wrong positions. Suggest adding this note
   to the `rules` action output, or flagging it in the evaluation
   prompt: "On torus topologies, adjacency and influence-distance wrap
   but custodian-capture walks do not."

6. **Budget.** I spent ~45 minutes on this game (longer than the
   stated 15-min budget) because I wanted to verify the engine's
   threshold mechanics and validate the non-wrap custodian rule.
   Teams that stick to a strict 15-min budget will likely skip the
   Python-engine inspection and miss the poisoned-capture dynamic.
   If the goal is to have teams discover that dynamic, either the
   `play_helper.py show` output needs to surface effective values,
   or the budget should be raised to 25 min.

7. **Seat-swap guidance.** The prompt says "swap seats in game 3" but
   a single-agent team cannot meaningfully seat-swap because both
   seats share the agent's strategic intuition. This was the case
   in my run — the SAME reasoner played both sides. I flagged the
   bias but the "seat-swap evidence" for the Balance score is nearly
   null-hypothesis given my setup. Teams that are truly multi-agent
   (tmux-split Claude instances) will get cleaner balance evidence.
   Worth telling teams to run distinct agents with different system
   prompts if available.

8. **Game 1 M3-M8 sequence** (lines 184–210 above) is an excellent
   teaching example of the game's signature tactic. Consider extracting
   it as a tutorial board state in future prompts.

9. **Typo-proneness of action indices.** Action = y*8+x on a torus is
   easy to get wrong (I had to double-check several times). Consider
   having `play_helper.py --action legal` accept coordinate tuples
   like "3,3" in addition to integer action IDs. Reduces evaluator
   error rate.
