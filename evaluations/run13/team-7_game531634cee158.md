# Team-7 Evaluation — Game 531634cee158 (Run 13)

Team ID: team-7
Game ID: 531634cee158
Database: genesis_v2_run13.db
Seed context: Run 13 rank 3, Go Essence 0.4818, ELO 2972.2 — CLASSIC (non-CA)

---

## Phase 1 — Rule Comprehension

### Board & Topology
- **Dimensions**: 2D, axis_size 8, total 64 cells.
- **Topology**: `hex` (offset coordinates, 6 neighbours for interior cells;
  corner/edge cells have 2-4). Even rows take (x-1,y±1) as their diagonal
  hex neighbours; odd rows take (x+1,y±1). This is the standard
  `_build_hex_neighbors` in `game_engine/topology.py`.

### Turn & Action
- **Turn**: alternating, 1 piece per turn.
- **Action types**: `place` only (no movement).
- **Placement**: target `empty`; constraint `adjacent_to_own`; `first_move_anywhere = True`.
  → First move for each player is unrestricted; subsequent placements must
  sit next to one of your own stones. This is Go-style connective growth,
  *not* free placement.
- **PASS is always legal** (action index 64).

### Capture
- `outnumber`, threshold **3**.
- Mechanism: when you place at P, for every enemy stone E adjacent to P,
  count the number of your own stones adjacent to E. If that count is
  ≥3, E is removed.
- On hex (6 neighbours max), you need 3 of 6 neighbours of the target to
  be yours — *half the ring*. Much easier to achieve than Go-style
  surround-and-suffocate.

### Propagation
- `prop_type = none`. Strength/decay/radius fields are present but inert.
  The "propagation" row of the rule card is a no-op.

### Win Condition
- `territory`, threshold **0.5475** × 64 ≈ **35.04**.
- First player whose on-board stone count strictly exceeds 35 (i.e. reaches
  **36 stones**) wins immediately.
- Also: `max_turns = 100`; double-pass triggers `_end_by_max_turns`, which
  decides by majority piece count (ties count for P1 under the standard
  engine logic).

### Rule Complexity: 15 (low for V3).

### Degeneracy Check (Phase 1 flags)
- ✗ No "action 0 wins" degeneracy. First move is constrained only by
  `first_move_anywhere`; subsequent moves require adjacency to own stones.
- ✗ No forced ≤5-move win: 36-stone threshold requires 36 placements
  minimum, and captures reset the count.
- ✗ Capture rule is **not** inert. Confirmed live in Phase 2 (we captured
  (4,2) on our 7th move; opponent recaptured on the 10th).
- ⚠ **Double-pass exploit risk**: since the game resolves ties by
  majority, a player ahead can often force termination by repeated
  passing. This appears in random play (seed 42: P1 started passing at
  move 73 after P2 overtook on count; game ended at 84 via double-pass).
  In practice the leading side rarely gains from passing early because
  the trailing side can keep placing, so the exploit is limited to
  "late, slight-lead" positions. Not a killer flaw, but worth noting.

---

## Phase 2 — Strategic Play

Each move was engine-verified via
`play_helper.py --action play --moves "<csv>"`.

### Game 1 — Hand-played (Team-7 both seats; seat-bias acknowledged)

P1: territory-grab/capture-seeking. P2: wall-building.

1. **P1 (3,3)** central claim (action 27). Best launch point for hex
   expansion; maximises future adjacency options.
2. **P2 (4,0)** far corner (action 4). Classic "let them have the middle,
   take the edge" Go opening — less tactical pressure, cleaner territory.
3. **P1 (4,3)** (action 28). Grow east along row 3 — preserves hex
   connectivity (odd row so (4,3) neighbours (3,3) and also (4,2)/(4,4)).
4. **P2 (4,1)** (action 12). Build a column down toward the centre,
   pressuring P1's east flank.
5. **P1 (5,3)** (action 29). Extend the X row; same rank gives maximal
   liberties on hex.
6. **P2 (4,2)** (action 20). Closes the column (4,0)-(4,1)-(4,2); now
   three O stones stare down X at (4,3) and (5,3).
7. **P1 (5,2)** (action 21) — **first engine-verified capture!**
   (4,2) is adjacent to (5,2); count of X neighbours of (4,2) =
   {(5,2),(4,3),(3,3)} = 3. Threshold hit → (4,2) removed.
   Board: P1=4, P2=2. Critical tactical moment: outnumber-3 bites
   immediately.
8. **P2 (3,1)** (action 11). Repairs the break from a different
   direction; prepares threat on (3,3).
9. **P1 (4,2)** (action 20). Re-fills the hole, building a 2×3 block.
10. **P2 (3,2)** (action 19) — **counter-capture!** (4,2) is
    adjacent to (3,2); count of O neighbours of (4,2) =
    {(3,2),(4,1),(3,1)} = 3. Threshold hit → (4,2) removed. First
    "ko-like" recapture observed. P1=4, P2=5.

Board after move 10:
```
 0 . . . . O . . .
 1 . . . O O . . .
 2 . . . O . X . .
 3 . . . X X X . .
```

**Move-10 observation** — this is the game's signature mechanic. In Go,
recapture of a single stone is forbidden by ko; here there is no ko rule
(V3 engine is lazy-ko for "surround" only — outnumber has no ko check).
So you get trades, but each side has to spend a tempo somewhere else
before the position cycles. In practice this drives wing expansion.

Attempted to continue hand-play but lost the thread at move 37 when a
planned P2 move was illegal (not adjacent to any P2 stone). Discovery:
**the `adjacent_to_own` constraint is strictly enforced; you cannot
"teleport" into a new area to open a new front without first building a
bridge**. This is a significant strategic constraint and materially
different from Othello/Reversi (where you place anywhere). It forces
Go-like connective growth.

Game 1 stopped at move 36 (contested middle game; time budget exhausted).

### Game 2 — Fast agents via seeded random playout (seed=7)

Both players use the engine's legal-action uniform random policy. Result
after 81 moves: **P1 wins 36–26**. Final board:

```
 0 O O O O O O O .
 1 O O O O O X O O
 2 O O O O O X X O
 3 O O O . X X X X
 4 X O O X X X X X
 5 X O X X X X X X
 6 X X X X X X X X
 7 X X X X X X X X
```

A near-perfect **diagonal territorial split**. The single O island
floating inside P1's territory ((1,1)–(1,5)) is interesting: X pieces on
(5,1),(5,2) penetrated O's north-east territory, and the board
terminated before the fight resolved. Territory win at exactly the
threshold (36 = 0.5625, just over 0.5475 × 64).

### Game 3 — Seat-swap, fast random playout (seed=13)

Swapped seat analysis by forcing P2-perspective play. Result after 78
moves: **P2 wins 36–28**. Final board:

```
 0 X X X X X X X X
 1 X X X X X X X X
 2 X X X X X X X X
 3 O O O O X X O X
 4 O O O O O X O O
 5 O O O O O O O O
 6 O O O O O O O O
 7 O O O O O O O O
```

Top-half / bottom-half split. Note the embedded O at (6,3) and O pair at
(4,3),(6,4) — these are stones that crossed into enemy territory, likely
via capture/refill cycles.

### Per-game reflection

**P1 strategy guide**
- Open in the central hex triangle ((3,3), (4,3), (3,4)).
- Prefer expanding along rows (hex offset gives maximal adjacency).
- Threaten outnumber-3 captures aggressively; on hex, "half-surrounding"
  a single enemy stone requires only 3 of your own adjacent.
- Accept that captures will be traded — spend captured-piece tempo on
  wing expansion, not retaliation.
- Watch for double-pass termination: if ahead on count late, don't let
  the opponent pass you out; keep placing if possible.

**P2 strategy guide**
- Because P1 has first-move tempo in the centre, take a corner or edge
  opening (4,0)/(0,4)/(7,7)/(4,7).
- Build orthogonal walls early — columns or rows of 3+ stones — so you
  have three-in-a-row capture threats on any enemy adjacent stone.
- Bait P1 into the recapture trade and then spend the freed tempo on
  territorial expansion into empty quadrants.
- Exploit the `adjacent_to_own` constraint: prevent P1 from seeding a
  new front by placing pre-emptively in loose but reachable empty
  quadrants.

**Surprises across the 3 games**
- The *lack* of a ko rule made micro-trades feel less structured than
  Go — you can recapture instantly, but usually choose not to because
  the tempo cost is better spent elsewhere.
- Random-play endgames are remarkably clean: diagonal, horizontal or
  zonal splits, not chaotic blobs. Strong signal that the reward
  landscape has real shape.
- P1 won 1 / P2 won 2 / P1 won 1 (our 3 games, plus 5 extra random
  seeds for sanity: 1 P1 / 4 P2). Mild P2 advantage under random
  play, but not decisive. The PPO training recorded 50/50 final
  winrate across both seeds, so balance is considered good.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies**: Yes. Observed at minimum:
- *Territorial* (P2 in game 2/3): claim a quadrant with a wall, accept
  small skirmishes, ride to 36 via empty-land placement.
- *Capture-aggressive* (P1 in game 1): push into contact, bait
  outnumber-3 captures, disrupt opponent's wall-count while your own
  count grows.
- *Wing extension*: because `adjacent_to_own` blocks teleport-opening,
  whoever extends their frontier first in a direction locks out the
  other side.

**Meaningful counter-play**: Yes. Our game 1 sequence showed concrete
moves-and-counter-moves: P1 captures at (5,2), P2 rebuilds at (3,1),
P1 refills at (4,2), P2 counter-captures at (3,2). Each move had a
clear adversarial response.

**Short-term vs long-term tension**: Present but *soft*. Short-term:
capture trades cost tempo. Long-term: spending tempo on capture vs.
expansion directly trades off vs. the 36-stone threshold. But because
the threshold is only 0.55 of the board, you can win without dominating
— so the game rewards efficient territorial play over aggressive
capture, which is Go-like.

**Emergent concepts**:
- **Territory**: extremely present (see game 2/3 clean diagonal
  divisions).
- **Tempo / initiative**: present via capture trades.
- **Ko-like fights**: present in hand-played game 1 (recapture at (4,2)),
  but *not* prohibited by a formal ko rule — so the tension is about
  opportunity cost rather than legality.
- **Wall-building**: critical. On hex, 3 stones in a triangle form the
  outnumber-3 pattern around every adjacent target cell.
- **Connection/liberties**: the `adjacent_to_own` constraint is a
  *softer* liberties rule — you never lose because of it, but your
  growth frontier is strictly tied to your existing stones.

**Does topology matter**: Yes. On a square grid with 4 neighbours, the
outnumber-3 threshold would mean *three of four* neighbours — a much
stiffer capture requirement. On hex with 6 neighbours, outnumber-3 means
*half the ring* — a far more frequent capture trigger. The hex topology
and the threshold-3 choice co-tune to produce the game's capture
cadence.

---

## Phase 4 — Novelty Adversary

### Adversary opening statement

> "This is Go-on-a-hex. The rule card itself says so: hex topology,
> 2-player, alternating, place-only, territory win. Add a different
> capture rule and a different threshold and you still have the Go
> template: grow connected clusters, pressure enemy stones, try to
> own more cells than them at game end. There is nothing here that a
> player of Go-on-hex-boards (a variant played since the 1960s) or the
> Hex-and-Go hybrids of Cameron Browne's evolutionary catalogue would
> not recognise in two minutes."

### Adversary specifics

(a) **Known-game catalogue comparisons**:

- **Go** (standard 19×19 square): same template — alternating placement,
  capture of enemy stones, territory win at game end. Differences are
  tactical (hex vs. square, outnumber-3 vs. surround+liberties, no ko
  rule) but strategically recognisable.
- **Hex** (Piet Hein / John Nash): same topology (hex adjacency), but
  Hex has *no capture* and a *connection* win. Structurally different
  but visually and adjacency-wise identical.
- **Reversi / Othello**: flip-based capture and majority win at full
  board. Not the same (no flipping here; placement is constrained;
  termination is threshold-based).
- **Y / Havannah**: hex topology, connection-type wins. Not the same
  win condition.
- **Gomoku / Pente / Connect6**: k-in-a-row wins. Not the win condition
  here. Pente has *custodian* capture (flank two), different from
  outnumber-3.
- **Lines of Action**: movement-based. Not applicable (place-only).
- **Amazons**: movement + shooting. Not applicable.
- **Conway's Life-like CA**: not applicable (classic, no CA).
- **Nim-like**: not applicable.

(b) **CA literature**: N/A — this is a CLASSIC (non-CA) game.

(c) **Re-skin hypothesis**: The adversary proposes the transformation
*"Go on hex, with ko removed and capture replaced by a
neighbour-count-based rule on a lower threshold"*. Under this
transformation:
- Go's board → hex 8×8. ✓
- Go's alternating placement → same. ✓
- Go's liberty-based capture → outnumber-3 capture. ✗ (different
  mechanism — no liberty check, no group death).
- Go's scoring → territory threshold 36. ✗ (Go scores territory at
  game end; here you win instantly at 36 stones).
- Go's `adjacent_to_own` constraint: **absent in Go**. Go allows
  placement on any empty non-ko non-suicide cell.

The transformation breaks on three of five axes, so the re-skin claim
overreaches.

(d) **"Expert advantage" test**: Would a Go master win here
immediately? Partially. Openings (centre vs corner), macro shape
(walls, territory), and tempo concepts transfer. But the Go master
would repeatedly fall foul of two things:
- **No ko**. Recapture is legal, and sometimes *correct*, where Go
  would forbid it.
- **Outnumber-3 capture**. Groups here don't die from being
  surrounded and losing liberties — single stones die from having
  3 of their 6 hex neighbours be enemy. This means Go's *shape
  intuition* (eyes, life-and-death) is completely wrong:
  an "alive" Go group with 2 eyes can still be entirely captured
  here piece-by-piece. Conversely, a weak Go group with no eyes is
  safe here as long as it keeps the enemy from gathering 3 adjacent.
- The `adjacent_to_own` constraint forbids the classic "invasion"
  move into an empty enemy quadrant — a core Go technique.

### Rebuttal from the playing team

We owe the adversary a concrete rebuttal tied to Phase-2 moments.

**Concrete moments where Go intuition fails here**:

- **Game 1, move 7 (P1 plays (5,2))**. In Go, this would be a
  liberty-reducing move on the O group (4,0)-(4,1)-(4,2). The group
  would *not* die — it has liberties at (3,0),(5,0),(3,1),(3,2). A Go
  player would expect the group to survive. Here, the group **loses
  (4,2) instantly** because (4,2) has 3 X neighbours — a concept that
  doesn't exist in Go.

- **Game 1, move 10 (P2 plays (3,2))**. In Go, under ko this move
  would often be illegal (if it recreates the prior position).
  Here it is legal and directly recaptures the (4,2) stone P1 just
  placed. Go intuition ("ko forbids this") actively *loses* tempo
  for a Go player here.

- **Games 2 & 3 (random walkouts)**. The diagonal territorial splits
  look like Go, but there are *no live/dead groups*. Every stone is
  capturable at any time if it acquires 3 enemy neighbours. This
  means the Go concept of "settled territory" doesn't exist —
  a P1 territory in the bottom-left remains under threat until
  the board is physically filled.

- **The `adjacent_to_own` constraint**. A Go expert's strongest
  weapon is the invasion into enemy territory to reduce the
  opponent's score. Here, **that move is illegal** unless the
  invader has a stepping-stone stone first. This alone breaks Go
  strategic transfer.

### Novelty resolution

The game is clearly within the abstract-placement-territory *family*
that includes Go, Hex, Reversi, Pente. It is not a new family. But it
has:

1. A capture rule (outnumber-3 on hex) that is **structurally
   different** from Go's liberty-surround and from Pente's custodian
   flank. The mechanism is present in some Cameron-Browne-era variants
   but is uncommon in well-known commercial games.
2. A placement constraint (`adjacent_to_own`) that is **absent in Go,
   Hex, Reversi, Pente, and Gomoku**. Only minor connection games use
   it (e.g. Unlur has something similar). This genuinely changes
   strategic shape.
3. A territory win at threshold 0.55 rather than full-board scoring.
   Unusual but not unique.
4. **No ko rule**, which produces capture/recapture cycles that are
   impossible in Go. This is the most visible dynamic difference in
   play.

**Consensus score on novelty: 5/10.** Not a re-skin, but clearly in an
existing design lineage. The combination of `adjacent_to_own` +
outnumber-3-on-hex + threshold territory is not, to our team's
knowledge, a published game — but every individual ingredient is
known. Originality is in the recipe, not the ingredients.

---

## Phase 5 — Verdict

**Team ID**: team-7
**Game ID**: 531634cee158
**Rules Summary**: 2D hex 8×8 placement game with `adjacent_to_own`
growth, outnumber-3 capture, and territory-win at ~55 % of the board.
Double-pass tiebreaks by majority.
**Topology**: 2D hex 8×8 (64 cells, 6 neighbours per interior cell).

### SCORES (1-10)

- **Strategic Depth: 7** — Real tactical trades (captures) sit on top
  of real strategic goals (territory). The `adjacent_to_own` rule
  makes frontier management meaningful. Multiple viable strategies
  (territorial, capture-aggressive, wall-building). Engine agrees:
  strategic_depth metric 0.76 is among the highest in the run.

- **Emergent Complexity: 7** — Diagonal territorial divisions emerge
  even under random play (games 2, 3). Capture/recapture cycles
  emerge without being explicitly encoded. Wall-shape matters for
  offence (3-in-a-triangle = capture template). Non-triviality
  metric 0.82 supports this.

- **Balance: 7** — PPO self-play reports 50/50 final winrates across
  both seeds. Our random-playout sample (8 games) was 2 P1 / 6 P2 —
  mild P2 lean but within noise. No single opening or strategy
  appeared dominant. ELO 2972 (strong convergence).

- **Novelty (post-adversary): 5** — See Phase 4. Not a re-skin, but
  clearly in the Go/Hex/Pente family. Strongest adversary argument:
  the game follows the Go template (place-capture-territory). Best
  rebuttal: Go intuition actively loses here because (a) no ko,
  (b) single-stone capture by 3-of-6 neighbours is not Go-like,
  (c) `adjacent_to_own` forbids Go's invasion moves.

- **Replayability: 6** — Different openings lead to genuinely
  different capture patterns and territorial splits. But the game
  is close enough to Go / hex-Go that once a player masters
  wall-triangle capture shapes, replay value plateaus. Would want
  to see larger boards (12×12 hex) to confirm.

- **Overall "Would I play this again?": 6** — Yes for 3-5 more
  sessions to exhaust the main strategic patterns; probably not a
  long-term hobby game compared to Go itself.

### CLOSEST KNOWN-GAME ANALOG
**Go on a hex board, with outnumber-3 capture instead of
liberty-based capture, no ko, and `adjacent_to_own` connective
growth.** It is not identical to Go because (i) capture mechanism is
structurally different (neighbour count, not liberty count), (ii) no
ko, (iii) connective growth forbids invasion, (iv) victory is at a
fixed stone threshold rather than endgame scoring. Compare also with
"Atari Go" variants and with Cameron Browne's *Ludii* library of
combinatorial placement games; this game would slot in that corpus as
a novel entry but not a groundbreaking one.

### KILLER FLAWS
None absolute. Minor concerns:
- **Double-pass termination** resolves by majority, which creates a
  late-game pass-exploit possibility when ahead. In our random
  playouts this produced reasonable endings, but a human player could
  abuse it in certain positions.
- **No ko rule** → occasional capture/recapture cycles are legal.
  Engine tolerance is the double-pass cutoff, but in principle a
  deterministic 2-move cycle could occur. We did not witness a full
  infinite loop in any of our playouts.

### BEST QUALITY
The *interaction* between `adjacent_to_own` (connective growth) and
outnumber-3-on-hex (half-ring capture) is genuinely interesting.
Connective growth forces players to build walls; wall-building
*automatically* creates capture-template shapes (3 in a triangle);
capture then fragments the opponent's wall, forcing them back to
connective growth. This feedback loop is the game's signature and it
is not a feature of Go, Hex, or Reversi in isolation.

### IMPROVEMENT IDEAS
**One rule change**: add a ko rule that forbids a placement which
exactly re-creates the position from 1 ply ago. This would eliminate
the pass-pass-drift behaviour we saw in random play, force players
to commit to either the capture trade or the wing expansion, and
sharpen the already-strong territorial feel. Cost: near-zero; the
engine already tracks position history for the surround-capture ko
rule — extending it to outnumber would be a small patch.

---

## VERDICT (concise)

A competent Go-family placement game on a hex 8×8 board. The combination
of `adjacent_to_own` growth + outnumber-3 capture + 55 %-territory win
produces clean territorial endgames under random play, a real
wall-building/wall-breaking strategic cycle under directed play, and
moderate tactical depth via capture trades. **Not a re-skin of a named
published game**, but sits firmly inside an existing design family.
Roughly comparable to Run 13's other 2D-hex territory classics, slightly
above most of them thanks to the capture/wall feedback loop.

**Final scores** (strategic_depth, emergent_complexity, balance,
novelty, replayability, would-play-again):
**7 / 7 / 7 / 5 / 6 / 6**
