# Team-4 Evaluation — Game `531634cee158` (Run 13)

Team ID: team-4
Game ID: 531634cee158
Generation: 10  ·  ELO 2972  ·  Go Essence 0.482  ·  Rule complexity 15
Archetype: 2D hex (offset), outnumber capture (thresh=3), territory win (thresh=0.5475), CLASSIC

---

## Phase 1 — Rule Comprehension

**Board**: 8×8 offset hex grid (64 cells). Each cell has 6 neighbours. The
engine uses a mixed offset layout: cells on "odd" rows have neighbours at
(x,y±1) and (x+1,y±1); cells on "even" rows have neighbours at (x-1,y±1) and
(x,y±1). (We verified this empirically: (3,3)'s neighbours are {(3,2),(4,2),
(2,3),(4,3),(3,4),(4,4)} while (2,2)'s are {(1,1),(2,1),(1,2),(3,2),(1,3),
(2,3)}.)

**Turn structure**: Alternating, 1 placement per turn. Action space is 65
(64 cells + PASS).

**Placement constraint**: `empty + adjacent_to_own`, with
`first_move_anywhere=true`. In practice **both players' very first move is
unrestricted** (any empty cell). After that, all placements must be on empty
cells adjacent to at least one of the mover's own stones.

**Capture rule**: `outnumber` with `threshold=3`. On placement, every adjacent
enemy cell is checked; an enemy cell is removed if the number of friendly
(mover-colour) stones in *its* 6-neighbourhood is ≥ 3. Because the threshold
equals half the coordination number, captures require real investment — you
need at least 3 of your stones clustered around one enemy stone already to
trigger a capture when placing the 3rd/4th.

**Propagation**: `none` (the strength/decay/radius fields are inert — this is
a "classic" game).

**Win condition**: `territory` — a player wins immediately if they own more
than 0.5475 × 64 ≈ 35.04 (i.e. ≥ 36) cells. `max_turns = 100`. On double PASS
the game ends and the player with the higher piece count wins (draws possible
but rare).

**Degeneracy check**:
- No obvious first-move forced win: the opening tree branches immediately
  because of `first_move_anywhere`.
- The capture rule is NOT inert (we saw at least one capture per playthrough).
- Territory threshold is not trivially low (no "2 stones wins").
- Threshold 0.5475 is probably *slightly too high* to reach by pure
  saturation — the games we played ended by double-pass at roughly 27–32
  stones per side, never hitting 36. This means the game **effectively
  functions as a comparative-area game under a majority tiebreaker**, rather
  than a race-to-threshold game. This is a soft flaw, not a killer.

---

## Phase 2 — Strategic Play (3 games)

### Game 1 — P1 plays centre, armies divide

Opening moves: X(3,3), O(4,4), X(4,2), O(4,3), X(3,2), O(4,5), X(3,1), O(5,4)
…

Both players converged on a **diagonal partition**: X built the upper-left
quadrant, O the lower-right. Every move was "add one stone to the front",
and the diagonal front wall stayed razor-thin with almost no interpenetration
because `adjacent_to_own` prevents invading cells that aren't already next
to one of your stones.

First capture at move 29 (P1 plays (5,2)): the enemy O at (4,3) already had
X neighbours at (4,2) and (3,3); placing at (5,2) added a 3rd X neighbour
to (4,3) → captured. A single-piece swing.

The board filled; by move 53 the territories were locked at roughly 26-vs-25.
Then came the *decisive* move.

Move 66 — **Player 2 plays (4,3)**. This cell sat at the narrow neck between
the two armies. The O placement sees three X neighbours — (4,2), (5,2), (3,3)
— and for *each* of them it counts O-neighbours:
- (4,2) has only 1 O neighbour → not captured.
- (5,2) has 4 O neighbours ((6,2),(6,3) wait — careful, (5,2) neighbours are
  (5,1),(6,1),(4,2),(6,2),(4,3),(5,3); of these O owns (6,2),(4,3)(new),
  (5,3) → 3 → captured.
- (3,3) has 3 O neighbours → captured.
→ **Two X stones captured at once, one O placed: net +3 swing in O's favour.**

P1 had no legal counter (the new holes at (3,3),(5,2) were enemy-owned
territory for O; P1's only useful empties were isolated). P1 passed, P2
passed. **Final: P1 29, P2 32 — Player 2 wins.**

P1 reflection: the move (3,3)/(5,2) threat was visible but I underestimated
the *combined* swing. The right defensive idea was to "crosscut" through the
diagonal earlier — plug (4,3) or (3,4) myself around move 50 — but
`adjacent_to_own` made that hard because my stones weren't next to those
cells yet.

P2 reflection: the winning move is a **tesuji on the diagonal**. It only
works because both (5,2) and (3,3) had been placed earlier with 2 of my
stones already adjacent to each. My opening goal should be to create cells
like these where my stones sit on *two* of the target's neighbours.

### Game 2 — P1 plays (4,4), P2 (3,3), symmetric split reversed

Same diagonal pattern emerged, mirrored. The armies wedged against each
other along the anti-diagonal. Moves 1–50 produced a mirror-image fortress
with the front at y ≈ 3-4.

P1 pushed an extra step on moves 51-55: (5,6),(4,6),(4,7),(5,7) — an
"armoured finger" down the right wing at the diagonal. This gave P1 a 28-27
edge with very few legal empties left.

Move 58 — **Player 2 plays (3,3)**. Neighbours of (3,3) include X at (4,3)
— but check: at that moment (3,3) was empty (P1 had never placed there;
X at (3,2) in row 2; O held (3,3)'s east side via (4,3)? Actually rows
were: row 3 `X X X . O O O O`, so (3,3)=., (4,3)=O, (5,3)=O, etc.
Re-reading the output more carefully: move 58 (P2 places (3,3)=O) resolved
with P2=29. One X piece captured from the wall.

Move 60: **P2 plays (5,4)**. Captures X at (4,4). P2 now at 29, P1 at 27.
Both pass. **Final P1 27, P2 29 — Player 2 wins.**

### Game 3 — Seat swap (I am P1)

I followed the same known-good opening from Game 2's perspective but with
the key tactical lesson from Games 1 & 2 in mind: **preserve a capture-ready
diagonal wedge for the endgame**. I played the opening role that had been
P1 in Game 1 but this time was determined to play the late-game invasion
move myself.

Move 58 — **Player 1 plays (3,3)**. Same tesuji, my colour: captures O at
(4,3) and (2,4) — two enemy stones, +3 swing.

Move 60 — **Player 1 plays (5,4)** (further capture of O at (4,4)) adding
more material.

Both pass. **Final P1 30, P2 24 — Player 1 wins.**

### Strategy guides (post-facto)

**As P1**:
1. Open at (3,3) or (4,4) (centre, 6 neighbours) — *do not* move to corners.
2. Race the opponent to complete "your" half of the board along whichever
   diagonal you first angle toward.
3. In the mid-game, look for cells where 2 of your stones are already
   adjacent and an enemy stone will soon be near — bait the opponent to
   complete the outnumber trap themselves (they won't, but keep the option
   alive).
4. **Save one empty cell on the main diagonal for the end**. This is the
   single most important positional goal.
5. Never pass while an unfilled "diagonal neck" cell remains.

**As P2**:
1. Mirror P1's opening at a 2-step offset (e.g. P1 (3,3) → you (4,4)).
2. Same as P1: consolidate half-board territory.
3. Same diagonal-cell hoarding.
4. You get the last-move advantage because P1 has one more parity-constrained
   "forced pass" step in many endgames — but this is subtle and didn't
   matter in our three playthroughs (2/3 went to the seat that found the
   tesuji, regardless of parity).

---

## Phase 3 — Strategic Analysis (joint)

**Distinct viable strategies?** Two: (A) maximum-area consolidation — fill
your half fast, (B) wedge-preservation — deliberately leave a gap in your
wall so you can capture into it late. In our games the wedge-preservers
(intentionally or not) always won. There is also a losing "corner-rush"
strategy that abandons the centre — we didn't play it out but it clearly
sacrifices too many mid-cell neighbour counts.

**Counter-play?** Yes. If your opponent is hoarding a diagonal gap, you can
either (i) race to fill *both* mirror-image gaps first or (ii) threaten your
own outnumber capture on the opposite wing to force them to defend. We
only saw single-cell threats, but multi-threat positions do exist.

**Short-term vs long-term tension?** Strongly present. Every mid-game move
trades "one more stone of territory" for "shape that will still be useful
in the endgame". Example: in Game 1, move 31 (P1 plays (5,1)) traded
immediate territory for a stone that became part of the *unsuccessful*
capture defence later. In Game 3 the equivalent parry worked. That delay
between a move and its evaluation is a hallmark of a non-trivial abstract.

**Emergent concepts?** We observed:
- **Territory** (obvious from the rules).
- **Tempo / last-move advantage** — the game end is usually determined by
  which player gets to play the final capturing wedge.
- **Sente/gote** — forcing moves (threat to capture 2+ stones) transfer
  initiative, and the opponent must spend a tempo defending rather than
  expanding.
- **Ko-like micro-fights** do NOT emerge (outnumber is not involutive; a
  captured stone's cell is hard to retake because you lose the neighbours
  that outnumbered it).
- **Influence / thickness** emerges from the 6-neighbour count: a stone
  with all 6 friendly neighbours is nearly unkillable; one on the edge with
  only 3 neighbours can be captured with a single invasion.

**Topology mattering?** Yes — the 6-neighbour hex count makes the
outnumber(3) threshold sit exactly at the "half coordination" sweet spot.
On a 4-connected grid, outnumber(3) would be almost impossible; on a Moore
8-connected grid, outnumber(3) would fire too readily. Hex is necessary
for this rule set to be playable.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary opening statement**: "This is Reversi on a hex grid with a
threshold generalisation. Concretely, it is a flat re-skin of **influence
territory games** that existed before our lab. Rebut if you can."

**Adversary case (a) — catalogue comparison**:

- vs **Go**: Go has groups, liberties, and surround capture. Here capture is
  per-stone, not per-group; there are no liberties. A Go expert's life-and-
  death intuition is nearly *inverted* (in Go you live by having space; here
  you live by being surrounded by your own colour).
- vs **Reversi/Othello**: Reversi uses custodian capture (flip enclosed
  lines). This game uses per-cell outnumber (remove, not flip). The
  flip/remove distinction matters: in Reversi, captured pieces become
  assets; here they vanish, and the empty cell becomes an *opportunity* for
  either side.
- vs **Hex / Y / Havannah**: those are connection games with no capture.
  This is a territory/capture game with no connection win condition. Wrong
  family entirely.
- vs **Gomoku / Pente / Connect6**: these want n-in-a-row. This game has no
  line-forming win. Pente has custodian pair capture; not the same mechanism.
- vs **Amazons**: Amazons has burning squares and queen movement. No
  correspondence.
- vs **Lines of Action**: movement-based, victory by connecting. Wrong
  family.
- vs **Mancala**: sowing mechanic, no capture-by-threshold. Wrong family.
- vs **Life-like CA (Conway, HighLife, Day&Night)**: this game has no CA
  step. The game_def explicitly reads `"prop_type": "none"`.

**Adversary case (b) — CA literature**: Not applicable; this is a classic
placement game, not a CA game.

**Adversary case (c) — re-skin argument**: "This is literally *Reversi* with
the rule 'flip→remove' and the topology 'square→hex'. Reversi→remove gives
you a deletion game. Reversi→hex means the capture lines are 6-directional
instead of 8. QED: Hex Reversi, circa 2012 abstract-game subreddit."

**Rebuttal (from our Phase 2 play)**:

1. **The capture geometry is not Reversi's.** Reversi captures bracketed
   *lines* — you must have a friendly stone at each end of a contiguous
   enemy line. This game captures *points* where the enemy is outnumbered
   3+ in its own neighbourhood, regardless of line structure. The move
   at Game 1 / move 66 (P2 plays (4,3) and captures (5,2) and (3,3)) has
   NO Reversi analog: the two captured stones are not collinear with (4,3)
   and there is no "bracket" in any direction.

2. **Reversi has no `adjacent_to_own` constraint.** In Reversi you may
   place anywhere that creates a flip. Here you can only place adjacent
   to your own existing stones (after move 1). This changes opening theory
   entirely — in Reversi the fight is about flanking the board early; here
   the fight is about *growing connected regions* while leaving capture
   gaps.

3. **Reversi is additive (pieces only get created/flipped, never removed).**
   This game is *subtractive*: stones disappear, re-opening cells for either
   player. The late-game tesujis we found (Games 1 & 3) exploit exactly
   this: a captured stone's empty cell becomes a new placement point for
   *both* sides (subject to adjacency). Reversi has nothing like this.

4. **Go-expert test**: would a Go expert have an immediate advantage?
   *Only partly*. They would intuit "build walls, fight for territory" —
   correct. They would also intuit "make eyes, don't overconcentrate" —
   *wrong*, because there are no liberties here; density is strictly
   good, not bad. We estimate a Go 5d would be about +100 Elo over a
   naive player but substantially weaker than a player who has grokked
   the outnumber tesuji. The overlap is genuine but partial.

5. **Reversi-expert test**: would a Reversi expert have an advantage?
   *Less than Go*. Reversi intuition (edge play, mobility) translates
   badly: you can't flank across a large empty region due to
   `adjacent_to_own`, and there are no "stable" pieces (anything can
   be captured if you outnumber it).

**Novelty resolution**: Team vote: **6/10**. The game is not a direct
re-skin of any single predecessor, but it sits in a well-populated design
space ("hex + per-cell capture + territory + adjacency-constrained
placement"). The two genuinely novel interactions are (a) the 3-outnumber-
on-hex-6 threshold being exactly at "half coordination", which produces
captures that are hard but not impossible, and (b) the `adjacent_to_own`
constraint interacting with `first_move_anywhere` and the outnumber rule
to create the wedge-tesuji endgame we observed. Neither is a breakthrough,
but the *combination* produces playthrough dynamics we could not map
onto any single listed predecessor without loss.

The strongest adversary argument is #3 — "this is Reversi-minus". Our
rebuttal is that the `adjacent_to_own` + subtractive-capture combination
produces a *different* strategic object (wall-building and endgame wedges)
rather than Reversi's flanking/mobility game.

---

## Phase 5 — Verdict

Team ID: **team-4**
Game ID: **531634cee158**
Rules Summary: Alternating single-stone placement on an 8×8 offset hex
grid; stones must be adjacent to one of your own (first move free).
Enemy stones with ≥3 friendly neighbours are captured; a player wins
by holding >54.75% of cells, or by piece majority at double-PASS.
Topology: 2D hex 8×8 (64 cells, 6-neighbour offset layout).

### SCORES (1–10)

- **Strategic Depth: 6** — Real tactical moments exist (the outnumber
  tesuji at the endgame wedge). Mid-game is largely parallel territory-
  growing, which dilutes depth, but the transitions between mid-game and
  endgame have non-trivial decisions. Not the depth of Go, but clearly
  above trivial.

- **Emergent Complexity: 6** — Wall-building, tempo-trading, wedge-tesuji
  at game-end, and the non-obvious interaction between `adjacent_to_own`
  and outnumber-capture all emerged in three games. No ko-like cycles.
  No large-scale "shape" vocabulary beyond "the diagonal front".

- **Balance: 7** — Across 3 games, results were P2, P2, P1. ELO-self-play
  metric is 0.5/0.5, and our seat-swapped Game 3 flipped the winner. P1's
  first-move bonus appears to be roughly neutralised by P2's ability to
  react. Slight P2 edge if both players play "greedy territorial" because
  the final-wedge tempo parity tends to favour the second player, but a
  careful P1 (as in Game 3) overcomes this.

- **Novelty (post-adversary): 6** — Survives the Reversi re-skin argument
  because of (a) capture rule structure (point, not bracket) and (b)
  placement constraint. Does NOT survive full novelty: a reader familiar
  with hex-territory variants and influence games would recognise the
  family. Rebuttal held but the closest analogs are uncomfortably close.

- **Replayability: 5** — Three games already showed the same diagonal
  partition pattern with variations on who finds the wedge. More openings
  are viable than we explored (corner-first, wing-rush), but we suspect
  they are all weaker. The tactical endgame likely has more depth than
  3 games revealed.

- **Overall "Would I play this again?": 6** — Yes for 5-10 more games to
  plumb the wedge theory; no for long-term tournament play. It is a
  solid evolutionary output and a plausible ancestor for further breeding.

**CLOSEST KNOWN-GAME ANALOG**: A hex-board variant of *influence territory
games* combined with per-cell outnumber capture. No single named analog
is closer than ~70% overlap; the nearest named relatives are (a) hex-board
Othello variants and (b) the "Squeeze" family of threshold-capture games.
It is NOT identical because `adjacent_to_own` placement + subtractive
capture change the opening and endgame fundamentally.

**KILLER FLAWS**:
- Territory threshold 0.5475 is effectively unreachable in practice (both
  sides saturate at ≈ 27–31 stones and the game ends by double-pass
  majority). This makes the nominal threshold rule dead; the game is
  silently decided by piece majority. Not catastrophic, but it means one
  of the rule parameters is cosmetic.
- Mid-game (moves ~15–45) is mostly parallel filling with little
  interaction — roughly 30 moves of "build your half" before any tension
  appears. This is a tempo/pacing flaw.

**BEST QUALITY**: The **endgame wedge tesuji**: a single placement into
the narrow diagonal neck between the two armies can capture 2+ enemy stones,
swinging the score by 3+ and frequently deciding the game. This is a
genuine tactical motif that a human player can learn, anticipate, and
engineer — and it emerges from the outnumber(3)-on-hex-6 geometry rather
than being hand-authored.

**IMPROVEMENT IDEAS**: Drop the territory threshold to **0.45** or remove
it entirely in favour of "game ends by double-pass, higher count wins".
This would acknowledge what the game actually is (an area-majority game)
and remove the cosmetic-threshold flaw. A stronger change: allow placement
on cells adjacent to *any* stone (enemy too) — this would compress the
mid-game by inviting earlier interaction and stress-test the outnumber
rule in more contested positions.

---

### Final scores table

| Metric | Score |
|---|---|
| Strategic Depth | 6 |
| Emergent Complexity | 6 |
| Balance | 7 |
| Novelty (post-adversary) | 6 |
| Replayability | 5 |
| Overall | **6/10** |

**Verdict**: A solid 6/10 hex-territory game with a genuine tactical
endgame motif. Not a breakthrough, not broken. Best feature: the
outnumber-wedge tesuji. Weakest feature: ~30 moves of parallel filling
before the game engages.
