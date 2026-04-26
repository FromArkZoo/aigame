# Team-7 Evaluation — Game 1ca924cc3062 (Run 14)

Team ID: team-7
Game ID: 1ca924cc3062
Run 14 rank: 2 (GE = 0.5000)

---

## Phase 1 — Rule Comprehension

### Board
- 8×8 torus (64 cells). Wrap-around in both dimensions.
- Von Neumann adjacency (face-adjacent; no diagonals).

### Turn structure
- **Alternating**, 1 piece per turn. Not simultaneous.

### Actions
- Place only (65-action space: 64 cells + pass at action 64).
- Constraint: first move for each player is anywhere (first_move_anywhere=True).
  Subsequent placements must be on an **empty** cell **adjacent to own** piece.
- No move/slide actions.

### Capture / cellular automaton
- `capture_type = "none"` — no custodian or surround capture.
- No cellular automaton (classic mechanics).
- **Consequence: no removal mechanism at all.** Every stone you place is permanent.

### Propagation (influence)
- `prop_type = "influence"`, `radius = 2`, `strength = 0.8734`, `decay = 0.4250`.
- On placement, `board_values[cell] += sign * strength * decay^distance` for all cells
  within von Neumann distance 2 (on torus, wrap-around distances count).
  Sign: +1 if Player 1 placed, −1 if Player 2.
- From one placement the engine adds ~+0.87 at the placed cell, +0.371 at each of 4
  distance-1 neighbors, and +0.158 at 8 distance-2 cells — total additive magnitude ≈ 3.62
  distributed across the neighborhood. Field is clipped to [−100, 100].
- Torus wrap DOES apply to propagation (verified by seeing (−0.16) at (0,0) after placing
  P2 at (7,7): cell 0 is distance 2 from cell 63 on the torus). The prompt caveat about
  custodian walks not wrapping is moot here (capture_type=none).

### Win condition
- `condition_type = threshold`, `threshold = 46.407`, `target_dimension = 0`, `max_turns = 83`.
- Evaluated as: for each player, sum `board_values[c]` over cells `c` owned by that player
  (with sign flipped for P2 so their net is positive), declare winner if > 46.407.
- Max turns 83 ≈ 41.5 placements per player. Below, I show ≥46.4 is reliably reachable in
  ~35-40 moves (17-19 stones per side), so threshold-resolution is the normal terminator.

### Degeneracy flags
- **No double-pass risk.** Since placing always improves your own total (+0.87 self + further
  positive propagation onto your already-owned cells) and you can never run out of legal
  cells until the board is full, passing is strictly dominated unless you have zero legal
  moves. The "double-pass majority exploit" from Run 13 does NOT fire here.
- **No dead rules.** Influence, placement constraint, and threshold all matter in every
  playthrough I observed.
- **One concerning constraint interaction.** `adjacent_to_own` forces a player's group to
  be a single connected blob after its first stone. Combined with a torus that wraps and
  no capture, this makes the game a race to build the densest cluster. If a player's blob
  gets pinned by the opponent's blob so that the only `adjacent_to_own` extensions run
  directly into heavy negative influence, efficiency can collapse — but in practice the
  torus is spacious enough that both players can grow roomy blobs.
- **Tight max_turns.** 83 steps ≈ 42 plies per player. My greedy playthroughs ended in
  35-39 moves, so there's headroom, but a stalling strategy has only ~4-5 moves of slack
  before max_turns majority kicks in.

---

## Phase 2 — Strategic Play

I built two tooling helpers for verification and analysis:
- `team-7_driver.py` — manual move-by-move commit with full engine state printing.
- `team-7_auto.py` — greedy lookahead-1 autoplay for either side, with optional
  "spoiler weight" that trades own-gain for opponent-cost. All moves run through
  `engine.step` and I replayed every final move-list through `play_helper.py` to
  confirm legality.

All three games were played with (P1 pure greedy) and (P2 pure greedy or spoiler-weighted).
I acknowledge the seat-identity bias: all three games were driven by the same sequential
reasoner; Game 3 is a seat-swap of OPENING STYLE rather than of agent identity.

### Game 1 — mirror race (center-diagonal corners)
- P1 opens center-ish: `27` = (3,3).
- P2 mirrors on the far diagonal: `63` = (7,7) (max torus distance 8 from P1 opener).
- I hand-played this one, building compact 2D blobs. At move 34 P2 switched from
  pure mirror to a spoiler move `37` = (5,4), which pierced P1's cluster and briefly
  dropped P1's total from 45.75 to 44.54. P1 recovered with `13` = (5,1) on move 37
  and crossed threshold: **P1 = 47.68 > 46.41 on move 37.**
- Move list: `27,63,19,55,28,62,20,54,35,47,26,56,18,48,34,49,36,46,17,41,25,57,21,61,33,50,29,45,11,39,10,40,9,42,12,37,13`
- Engine-verified via `play_helper.py`.

### Game 2 — P2 attempts spoiler opening
- P1 opens: `27` = (3,3).
- P2 opens close: `36` = (4,4) (distance 2 from P1 — immediately dumps −0.16 on P1's stone).
- I drove P1 greedily; P2 was a spoiler and actually led briefly (P2 = 5.98 vs P1 = 5.66
  after move 8), because P2's compact 2-wide cluster had higher self-overlap.
- P1 re-took the lead by move 17 (18.28 vs 16.04) once P1's blob got bigger and internal
  overlap compounded.
- Running auto-greedy completion: **P1 wins move 37 with P1 = 48.31.**
- Engine-verified.
- Key finding: P2's spoiler opening cost P1 roughly 2-3 influence points of total gain but
  did not flip the win.

### Game 3 — seat-swapped opening (corner start, P2 takes the center)
- P1 opens: `0` = (0,0). P2 opens adjacent: `9` = (1,1) to claim the center area as its
  own cluster root.
- Both sides run with spoiler_weight=0.5. P2 grows a central blob; P1 grows along the
  corners and, because the board is a torus, "corners" are fine starting points — all
  cells are equivalent under symmetry. P1's cluster ends up across the edge-wrap zones
  (corners and bottom-right) while P2 claims the center.
- Outcome: **P1 wins move 35 with P1 = 46.44** (see final position in transcript).
- Engine-verified.

### Third-party sanity check
I also ran one random-policy game via `play_helper.py --action random-game`:
**P2 won in 52 moves** (26 pieces each at game end). This confirms the game is not a
forced P1-win: the first-mover edge is real but thin, and blunders easily flip it.

### Did games reach the stated win condition?
All three strategic games ended by the threshold condition (not double-pass, not max_turns).
Random play also ended by threshold in 52 moves. No double-pass resolutions observed.

### Player reflections

**P1 strategy (all three games):**
- Open central-ish (any cell works symmetrically on the torus — what matters is early
  access to a compact 2×2 or 2×3 shape).
- Extend to adjacent empty cells that maximize overlap with your existing blob.
  Each new stone placed next to two existing own-stones buys roughly 2.6-3.0 influence
  (self 0.87 + 2×0.37 overlap bonus + 2×0.16 from distance-2 pairs).
- Ignore P2's cluster until move 30+; first-mover tempo carries you.
- Would do differently: against a spoiler P2 I'd consider opening with a sub-optimal cell
  like (2,3) instead of (3,3) so that P2's natural best response (4,4) leaves a cleaner
  P1 growth axis. In practice, not necessary.

**P2 strategy (all three games):**
- Mirror the opener across the torus diagonal to maximize separation (moves 1-20).
- Switch to spoiler placements at move ~15 when P2's cluster is big enough to extend
  toward P1's blob.
- Accept the ~1-move deficit from first-mover advantage; focus on being a close second.
- Would do differently: start spoiling EARLIER (move 3 or 4), even at the cost of own
  blob density, because the threshold race is decided by whichever player crosses first
  — denying P1's final 2-3 points matters more than adding your own 2-3 points when you
  are already behind on tempo.

### Strategy guide (short)

**P1:** first move anywhere (I prefer (3,3) or (4,4)). On subsequent moves, always play
to maximize `own_total_after_placement`. This is essentially a local greedy: pick the
empty legal cell with the highest current influence value under you, because placing
there adds +0.87 AND the +0.37/+0.16 bonuses land on already-own cells. Don't bother
interfering with P2 until move ~30.

**P2:** first move: ≈2 cells from P1 opener (e.g., (4,4) vs P1 (3,3)). This is the
sweet spot — close enough to drop −0.16 on P1's stone now and more later as you grow,
far enough that you have room for a compact 3×3 blob. Then greedy/spoiler mix:
alternate between pure-greedy own-growth moves and spoiler moves that interpose your
influence radius between P1's blob and the empty cells P1 wants next.

---

## Phase 3 — Strategic Analysis (joint)

**Distinct viable strategies?** Two clear modes: (a) pure-greedy blob-grower (dense
cluster, maximize self-overlap), and (b) spoiler (trade some blob density for blocking
opponent's access to high-value empty cells). Spoiler is a legitimate second-best
strategy but it cannot overcome the first-mover deficit with lookahead-1 play.

**Meaningful counter-play?** Yes and no. In my greedy autoplay, each move is reactive
and both players end up mirroring efficient shapes. But hand-playing Game 1 showed a
specific spoiler intervention at move 34 (`37` = (5,4)) that shaved P1's total from
45.75 to 44.54 — a meaningful one-move counter-play moment. The counter-play is real
but narrow: it lives in the endgame when the loser can identify "the empty cell P1
most needs next" and place their own stone next to it to poison the neighborhood.

**Short-term vs long-term tension?** Mild. The best move now is almost always the best
move long-term — because every stone added to an existing overlap zone is better than
a stone added at the frontier. There's no sacrifice-for-later dynamic.

**Emergent concepts observed:**
- *Territory-like blobs*: both players end up with one connected group that looks like
  a country on a map (Game 3's final position: P1 owns the corners and bottom strip,
  P2 owns the upper interior).
- *Influence decay as effective radius*: distance-3 cells contribute zero, so the game
  has a hard 5×5 locality per stone — this creates *locality of interaction* similar
  to Go's "liberties" but without captures.
- *Torus wrap as strategic asymmetry*: because the board wraps, there is no true "edge".
  A stone at (0,0) is no worse than one at (3,3) — but the intuition of a novice (who
  thinks corners are bad) will lead them astray. Experienced torus-game players will
  notice this immediately.
- No tempo/initiative beyond raw first-move priority. No ko fights (no capture).

**Does topology matter?** Yes, but mostly as a no-edge constraint. On a flat 8×8 this
game would give (0,0) lower expected value than (4,4) because corners have only 2 close
neighbors; the torus erases that asymmetry, which actually SIMPLIFIES the opening
(all first moves equivalent under translation) rather than deepening it.

**First-mover advantage.** In all 3 engine-verified strategic games, P1 won. Game 3
seat-swap used a different opener but the same P1-first turn order, so it does not
fully resolve the "does going first always win" question. Random-random play gave P2
a win in my single sanity run — so balance is not terrible. The training data (both
seeds: p1 win rate 0.500 after convergence) suggests a well-trained policy network
converges to 50/50, implying that with optimal play P2 has compensating resources.
My greedy lookahead-1 agents under-estimate those compensating resources and lose as
P2 every time.

**Summary balance verdict:** first-mover advantage is **real but modest**. Under
engine-training-convergence balance is 50/50; under naive greedy it's ~100/0 in favor
of P1. The truth is probably 55/45 P1 with strong play.

---

## Phase 4 — Novelty Adversary

### Adversary case (forceful)

**(a) Comparison to known abstract strategy games:**

*Go.* Place stones on a grid. Contiguous groups (forced by adjacent_to_own after move 1).
Strategic concepts of territory and influence. **This game is a stripped-down Go:
remove capture, remove the "liberty" rule, replace "territory at the end" with
"sum of a scalar influence field".** The propagation rule is Go's "influence/potential"
heuristic (Moyo/framework) made into the actual win condition. Expert Go players
already reason about influence radii of roughly 2-3 points; this game just makes that
math explicit.

*Reversi/Othello.* No, capture is central there.

*Hex/Y/Havannah.* No, those are connection games. This is not a connection game.

*Gomoku/Pente/Connect6.* No, those are "make N in a row" games. This is cumulative
sum, not pattern-match.

*Amazons, Lines of Action, Chameleon.* Movement games, inapplicable.

*Mancala variants.* Seed-sowing, irrelevant.

*Conway's Life / Day & Night / HighLife / Immigration Game.* No CA here.

*Tumbleweed.* Closest modern analog! Tumbleweed is a 2-player hex game where you
place stones and each stone "projects" a count to nearby cells; whoever has the higher
projected count on a cell controls it; majority of controlled cells wins. **This game
is essentially Tumbleweed with (i) square-grid + von Neumann adjacency instead of hex,
(ii) continuous threshold instead of majority, (iii) exponentially-decaying propagation
instead of line-of-sight counts, and (iv) adjacent_to_own placement instead of LoS
placement.** These are real differences but the *kernel* ("place stones that project
influence; scalar integral of projected field determines winner") is unambiguously
Tumbleweed.

*Slither.* Connection-growing game with snakes; different genre.

**(b) CA-literature check.** Not applicable — no CA.

**(c) Simultaneous-game comparison.** Not applicable — alternating.

**(d) Re-skin argument.** This is **"Tumbleweed on a torus with a threshold instead of
majority"**. The topology transformation: hex → square von-Neumann is a well-known
isomorphism at small scales (hex distance ≈ Manhattan + adjustment). The majority →
threshold transformation just picks an arbitrary scalar cutoff instead of counting cells.
An experienced Tumbleweed player would open with the symmetrical center stone, grow
a dense cluster maximizing projected-stone overlap, and probe the opponent's projected
field with adjacent placements — EXACTLY the Game 1/2/3 strategy I just played.

**(e) Would a Tumbleweed expert have an immediate advantage?** **Yes, obviously.** The
positional intuition transfers wholesale: "place where your influence compounds with
existing stones", "deny the opponent dense overlap", "the edge is no different from
the center (on this game because of torus, on Tumbleweed because of the small hex
board)". The only thing a Tumbleweed expert would have to learn is the different decay
formula and the threshold.

### Player 1 / Player 2 rebuttal

**First rebuttal — the adjacent_to_own constraint is doing real work.**
Tumbleweed lets you place anywhere in line-of-sight. This game forces every placement
to be adjacent to your existing group (after move 1). Concrete moment: in Game 2 move 4,
P2 could not play at the ideal spoiler cell (5,5) — it wasn't adjacent to P2's (4,4)
stone (distance 2). P2 had to play at (5,4) instead. This constraint means the
strategic space of "where can I project influence next" is tied to group shape; in
Tumbleweed this is not true. The "connected blob growing" dynamic is foreign to
Tumbleweed.

**Second rebuttal — exponential decay + radius-2 cap produces a different hot-spot
structure.** Tumbleweed's LoS counting gives EACH stone equal weight across its line;
this game's exponential decay means the hot cell is always directly on your own stone,
with a sharp falloff by distance 2. Concrete moment: Game 1 move 35 where the highest-
value empty cell (cell 12 = (4,1), value +1.37) happened to sit at the crux of three
overlapping P1 stones — a shape-level feature, not a line-of-sight one. Tumbleweed
experts optimize long-line projections; here, the player optimizes compact overlap
shapes. These are different visual/strategic problems.

**Third rebuttal — the torus creates wrap-overlap plays.** Game 3's final P1 shape
(corners + bottom strip) is a single connected group via torus wrap. P1's cluster
spans the (0,0)-(7,0) and (0,7)-(7,7) corners as one blob. On any non-torus board
(including Tumbleweed's hex board) this is impossible. A Tumbleweed expert would
initially misjudge corner value and under-exploit wrap-adjacency.

### Joint Novelty verdict

Novelty score: **4/10.**

The game is a close variant of Tumbleweed (continuous-field, torus-gridded,
adjacent-placement version). The adjacent_to_own rule and torus wrap are genuine
strategic additions, but the core "place stones, scalar-field integral picks winner"
kernel is not new. It's not a trivial re-skin — a Tumbleweed expert would have to
rework their evaluation function for exponential decay and torus topology — but the
strategic skill set transfers heavily. This is "a meaningful variant in the
Tumbleweed family", not "a genuinely new game".

---

## Phase 5 — Verdict

**Team ID:** team-7
**Game ID:** 1ca924cc3062
**Rules Summary:** 8×8 torus, alternating placement (first stone anywhere, subsequent
stones must be adjacent to own group). Each stone propagates a radius-2 exponentially-
decaying influence field (±strength 0.87, decay 0.425). First player whose owned-cells
total influence exceeds 46.41 wins, else majority at 83 turns.
**Topology:** 2D torus, 8×8, von Neumann adjacency (wraps both axes).
**Turn Structure:** alternating, 1 piece per turn.

### Scores (1-10)

- **Strategic Depth: 5.** Clear local-greedy policy captures ~95% of value; the
  remaining 5% is endgame spoiler tactics. No long-term sacrifice dynamics, no multi-
  turn combinations, no tempo trades. But recognition of hot-cell overlap geometry is
  a real skill, and trained agents converge to 50/50 which suggests more depth than my
  greedy autoplay used.

- **Emergent Complexity: 4.** The influence field genuinely emerges from local
  placement, and you see clear emergent-like patterns (blobs, hot-cell lattices on
  internal overlap, wrap-spanning groups on torus). But these are all direct consequences
  of a single scalar field — no qualitative regime changes, no phase transitions.

- **Balance: 6.** First-mover advantage is real: 3/3 engine-verified strategic games
  won by P1. However, one random-policy sanity game was won by P2 (52 moves), and
  the training runs report final winrates of exactly 0.500 in both seeds — so strong
  play neutralizes the advantage. My greedy agents are too shallow to find the
  compensating P2 lines. Estimated true balance: ~55/45 P1.

- **Novelty (post-adversary): 4.** Game is a close relative of Tumbleweed with
  torus + adjacent-placement + exponential-decay modifications. The modifications are
  real strategic additions (wrap-adjacency, compact-blob imperative) but the kernel
  is not original. See Phase 4 rebuttals; the strongest adversary argument is that
  a Tumbleweed expert would immediately understand strategic priorities here.

- **Replayability: 4.** Opening is essentially symmetric under torus translation, so
  meaningful opening diversity is low: "open anywhere + grow a dense blob" is the
  whole opening theory. Midgame spoiler tactics vary game-to-game. Would get stale
  after ~10 games at the same level.

- **Overall "Would I play this again?": 4.** Once or twice for curiosity; not a keeper.

### Closest known-game analog

**Tumbleweed** (Mike Zapawa, 2019). Reasons it is not identical: (i) torus vs hex board
with no edges vs edges, (ii) exponentially-decaying influence with radius cap vs
line-of-sight count, (iii) adjacent_to_own placement constraint vs free placement, (iv)
continuous threshold win vs majority-of-cells win. Secondary analog: Go's "influence/
framework" heuristic made into a literal win condition, with capture deleted.

### Killer flaws

- **No capture → no reversibility.** Every stone is permanent, so games have zero ko-
  fight / comeback dynamics. Once you're 5+ influence behind in the mid-endgame, you
  cannot recover; you just slog to the finish.
- **First-mover advantage under non-optimal play.** 3/3 engine games decided by P1.
  Training data says optimal P2 can draw, but naive play will always lose with P2.
- **`adjacent_to_own` forces monolithic blob strategy.** There is no multi-group
  strategic problem. Every decision is "extend my one blob here or there". Reduces
  tactical richness.
- **Threshold value (46.4) is within one-move precision of the game-ending state.**
  Games consistently end at ~46-48, so the final two moves decide everything and
  earlier play is just accumulation. The "tension arc" is squeezed into the last 4
  plies.

### Best quality

The **torus wrap on the influence field** is genuinely interesting. At Game 1 move 2
you can see P2 placing at (7,7) drop −0.37 on (0,7), (7,0), AND −0.16 on (0,0) (via
distance-2 wrap). This creates a mental-model challenge (wrap distances) that a
playtester has to internalize, and it makes corner openings strategically equivalent
to center openings — which eliminates the standard "control the center" heuristic.

### Improvement ideas

**Add a capture mechanic.** The single most impactful change: surround-capture (as in Go)
or threshold-capture (remove any opponent stone whose local influence field is strongly
negative, e.g., < −N). Either would:
- inject reversibility / comeback dynamics,
- break the monolithic-blob compulsion (you'd want to attack enemy blob vulnerabilities),
- create tempo and sacrifice dynamics (delayed capture threats),
- likely neutralize first-mover advantage by giving P2 a defensive weapon.

A secondary improvement: lower the threshold to ~30 and shorten max_turns to ~60, so
games finish in ~25 moves and the final-turn-decides-everything effect is less extreme.

---

## Appendix — Verified move lists

- **Game 1** (engine-verified, P1 win move 37, P1 = 47.68):
  `27,63,19,55,28,62,20,54,35,47,26,56,18,48,34,49,36,46,17,41,25,57,21,61,33,50,29,45,11,39,10,40,9,42,12,37,13`

- **Game 2** (engine-verified, P1 win move 37, P1 = 48.31):
  `27,36,19,37,11,38,18,45,10,44,26,46,17,53,9,52,25,54,2,47,1,55,3,39,8,30,16,29,0,31,24,28,57,61,58,62,4`

- **Game 3** (engine-verified, P1 win move 35, P1 = 46.44; seat-swapped opening):
  `0,9,7,10,6,11,63,18,56,17,62,19,55,26,48,25,54,27,47,20,40,28,46,12,39,3,38,2,32,4,45,1,53,21,37`

- Random sanity game (via `play_helper.py --action random-game`): **P2 wins move 52**,
  confirming the game is not forced-P1.
