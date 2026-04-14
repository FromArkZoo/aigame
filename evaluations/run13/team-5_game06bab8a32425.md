# Run 13 Evaluation — Team 5 — Game `06bab8a32425`

## Phase 1 — Rule Comprehension

### Board Structure
- **Dimensions:** 2
- **Axis size:** 8 (8x8 = 64 cells)
- **Topology:** hex (pointy-top offset coordinates, 6 neighbours per interior cell; even rows take `(-1,±1)` diagonals, odd rows take `(+1,±1)` diagonals)
- **Max game steps:** 100

### Turn Structure
- Alternating, 1 piece per turn.
- P1 (X) moves first.

### Action Types
- `place` only (no movement).
- `target: "any"` — placement legal on empty **or** occupied cells (i.e. overwrite is allowed).
- Placement constraint: `adjacent_to_own`. Must be adjacent to a friendly piece **unless** you currently have 0 pieces (first-move-anywhere).

### Capture Rule
- `capture_type: none` — no direct Go/custodian/surround capture routine. Captures happen **only** as emergent side-effects of the CA.

### Cellular Automaton (THE primary non-classical mechanic)
- `steps_per_turn = 2` — every action is followed by **two** CA iterations over the whole board.
- `max_neighbors = 6` (hex), so lookup space is (state × friendly × enemy) = 3·7·7 = 147 entries.
- Of those 147 entries, **only 11 are non-identity** (92% identity rate). The non-trivial rules, written as (state, friendly, enemy) → new_state, from the **acting player's** perspective:

| From        | friendly | enemy | → To     | Effect                               |
|-------------|----------|-------|----------|--------------------------------------|
| friendly    | 0        | 1     | empty    | Lone friend dies near 1 enemy        |
| friendly    | 0        | 2     | empty    | Lone friend dies near 2 enemies      |
| friendly    | 1        | 4     | **enemy**| Outnumbered friend is converted      |
| empty       | 2        | 3     | friendly | Crowded birth                        |
| empty       | 2        | 6     | friendly | Birth in deep enemy territory        |
| empty       | 4        | 0     | friendly | Safe birth (4 friends)               |
| empty       | 6        | 1     | friendly | Very crowded friendly birth          |
| enemy       | 1        | 0     | empty    | Enemy flanked by 1 friend, isolated  |
| enemy       | 6        | 1     | empty    | Surrounded enemy dies                |
| enemy       | 6        | 2     | empty    | Surrounded enemy dies                |
| enemy       | 6        | 5     | empty    | Surrounded enemy dies                |

Because `friendly` means *the acting player*, the rule applies **symmetrically**: each turn the CA sees the world from the player who just moved. The CA runs twice in a row, *both* times with the same perspective.

### Propagation
- `prop_type: none`. Not used.

### Win Condition
- `condition_type: connection` (Hex-style).
- **P1 connects dim 1** (top→bottom, y=0 to y=7).
- **P2 connects dim 0** (left→right, x=0 to x=7).
- `target_dimension=1, target_dimension_p2=0`.
- First connection wins; at `max_turns=100` majority of stones wins.

### Key Engine Quirks
- Super-ko is active (CA + overwrite + placement=any forces `needs_ko_rule=True`). If a placement+CA sequence repeats a prior `(board, next_player)` hash, the move is **undone and replaced with a pass**.
- Consequence: an overwrite that the opponent could immediately recapture becomes ko — **recapture is refused** and treated as pass. The overwriter effectively freezes the cell.

### Degeneracy / Flag Notes
- **Placement-near-unsupported-enemy is suicide.** Placing a lone friend adjacent to an isolated enemy triggers `(1,0,1)→0`: your piece dies the same turn you place it. This is a *hard filter* on legal play; it dominates tactics.
- The CA is **92% identity**. In most mid-board configurations it does nothing. The non-trivial rules fire mostly at placement boundaries.
- Adjacency constraint + CA-suicide means certain cells are effectively *untouchable* for one player even if visibly empty.

---

## Phase 2 — Strategic Play

All three games were engine-verified move-by-move via `play_helper.py`. Seat swap applied (same agent playing both sides; annotated below as seat-swap bias).

### Game 1 — P1 centre opening vs P2 flank

Move sequence (action indices): `27, 32, 19, 33, 11, 34, 3, 42, 35, 43, 36, 44, 37, 45, 38, 46, 44, 52, 52, 51, 59`.

| # | Player | Cell    | Notes                                                                                   |
|---|--------|---------|-----------------------------------------------------------------------------------------|
| 1 | P1     | (3,3)   | Centre stone.                                                                           |
| 2 | P2     | (0,4)   | Far corner — avoids CA suicide. First attempt at (4,4) as opening earlier showed that **playing adjacent to a lone enemy triggers mutual kill + ko revert**, so P2 had to stay distant. |
| 3 | P1     | (3,2)   | Build column 3 upward.                                                                  |
| 4 | P2     | (1,4)   | Extend east along row 4.                                                                |
| 5 | P1     | (3,1)   |                                                                                          |
| 6 | P2     | (2,4)   | Row-4 wall being built.                                                                 |
| 7 | P1     | (3,0)   | Reaches y=0; one face done.                                                             |
| 8 | P2     | (2,5)   | Goes *under* row 4 — (3,4) would suicide onto X(3,3).                                   |
| 9 | P1     | (3,4)   | Breaches row 4.                                                                         |
| 10| P2     | (3,5)   | Blocks column 3 below.                                                                  |
| 11| P1     | (4,4)   | Swing around P2's block.                                                                |
| 12| P2     | (4,5)   | Continues wall.                                                                         |
| 13| P1     | (5,4)   | Ladder east.                                                                            |
| 14| P2     | (5,5)   | Parallel ladder east.                                                                   |
| 15| P1     | (6,4)   |                                                                                          |
| 16| P2     | (6,5)   |                                                                                          |
| 17| P1     | (4,5) **overwrite!** | Overwrites P2's stone. Super-ko blocks P2 from recapturing (pre-state was in history, so recapture is refused as pass). |
| 18| P2     | (4,6)   | Try to rebuild chain below the breach.                                                  |
| 19| P1     | (4,6) **overwrite!** | Again not kowable (new hash). P1 now has a clear corridor through rows 4,5,6.        |
| 20| P2     | (3,6)   | Best-it-can-do cling. Cannot place at (3,7) or (4,7) — both would die to (1,0,1).        |
| 21| P1     | (3,7)   | **WIN** via chain (3,0)–(3,1)–(3,2)–(3,3)–(3,4)–(4,4)–(4,5)–(4,6)–(3,7).                |

**Result: P1 wins in 21 plies.**

**P1 reflection:** Straight-column strategy with a single lateral swing around each blocking wall was sufficient. Overwrite was the decisive tool once P2 built a horizontal wall.

**P2 reflection:** Every direct block on P1's lead stone died to CA suicide. Had to fall back to "wall 1 row below", which P1 simply overwrites. Did not see a viable blocking shape.

### Game 2 — P1 off-centre, P2 deep flank

Moves: `18, 45, 10, 44, 2, 43, 26, 42, 34, 41, 42, 50, 50, 51, 58`.

Highlights:
- P1 built a simple column at x=2 (cells 18,10,2,26,34).
- P2 built a horizontal row at y=5 (45,44,43,42,41).
- Move 11 P1 overwrites (2,5); P2 cannot recapture (ko).
- Move 12 P2 blocks (2,6); Move 13 P1 overwrites (2,6) too, again ko-protected.
- **Observed spontaneous birth**: after P2 move 12 at (2,5), the empty cell (3,4) *spontaneously* became P2 via birth rule (0,4,0)→1. This is the CA actually producing a piece.
- Move 14 P2 plays (3,6) — cannot stop (2,7) which is legal for P1 (friendly=1, enemy=0).
- Move 15 P1 wins at (2,7).

**Result: P1 wins in 15 plies.**

### Game 3 — Seat swap (corner opening)

Moves: `0, 28, 8, 29, 16, 27, 24, 26, 32, 34, 40, 42, 48, 33, 56`.

Highlights:
- P1 opens at corner (0,0) and simply sweeps down column 0.
- P2 builds a horizontal wall at y=3 (cells 28,29,27,26).
- **Critical: P2 cannot block column 0 down-sweep.** Every cell at (0,k) adjacent to (0,k-1)=X has friendly(P2)=0 and enemy(P1)=1, triggering (1,0,1)→0. Suicide.
- P1 reaches y=7 by move 15.

**Result: P1 wins in 15 plies.**

### Strategy guides

**P1 strategy guide.** Pick an edge/column (col 0 or col 3 worked). Build straight down. If P2 builds a horizontal wall, overwrite a cell in the wall — super-ko prevents immediate recapture. Two consecutive overwrites give you a corridor P2 cannot refill fast enough. The CA suicide rule means P2 can rarely place a "direct blocker" on your lead stone; you are almost always safe to extend.

**P2 strategy guide (attempted).** The only viable opening is far from P1 (to avoid mutual-kill + ko revert). Build horizontally, but cannot place adjacent to lone X because (1,0,1)→0 suicides your stone. You must always have 1+ friend adjacent to any stone you place near an X. This is so restrictive that you cannot keep pace with P1's build. Best hope: P1 misplays an overwrite sequence (didn't happen in 3 games).

### Seat-swap bias acknowledgment

Because the same agent reasoned for both sides, P1 benefited from perfect knowledge of P2's next intended move. However, P2's moves were mechanically forced by legality (most "block" moves were illegal due to CA suicide), so the bias did not decide the outcome. In Game 3 I swapped which side "led" reasoning, and still P1 won decisively. Conclusion: outcomes reflect genuine P1 advantage, not seat-swap leakage.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Not really. P1 has a dominant strategy: sweep an edge column with overwrite whenever blocked. P2 has no symmetric response; its best moves die to CA suicide or ko revert.

**Meaningful counter-play?** Weak. P2 can at most *delay* P1 by forcing overwrite sequences, but each overwrite gives P1 tempo (ko protects P1, not P2).

**Short-term vs long-term tension?** Minimal. Games end in 15–21 plies. No investment/payoff arcs observed.

**Emergent concepts?**
- **Ko-protected overwrites** — a novel dynamic: the attacker freezes a cell permanently.
- **CA dead zones** — cells adjacent to an isolated enemy are suicide.
- **Spontaneous births** — seen once in Game 2 (cell (3,4) birthed O from 4 P2 neighbours).
- **Ladder races** — Game 1's row-4/row-5 parallel ladder is real Hex-style tempo play.

**Does topology matter?** Yes. Hex adjacency with odd/even row asymmetry creates 6-neighbour connectivity that distinguishes this from a square grid, and the connection win condition lives naturally on hex. The CA threshold rules (f=4, f=6) are *tuned* for 6-neighbour spaces.

**Joint verdict:** Deep-ish tactics in the overwrite/ko layer; almost no strategic depth because P1's generic plan wins.

---

## Phase 4 — Novelty Adversary

### Adversary opening argument

> **Claim: this is Hex with CA-flavoured dressing, and specifically it is the descendant of Run 8's "Connection Go" (`d4015a646ae3`) and Run 10's `484fcb3b0471` already observed in prior evaluations. Neither the topology, the win condition, nor the overwrite+ko mechanic is new.**

1. **Win condition** = classical Hex (connect opposing faces along an assigned dimension). The per-player axes (P1 dim 1, P2 dim 0) are the standard Hex asymmetry.
2. **Topology** = classical 8x8 hex board (pointy-top). Smaller than tournament Hex (11x11) but within home variants.
3. **Placement target=any + super-ko** = Run 10's champion finding, already catalogued: "ko fights from overwrite + super-ko creates capture/recapture cycles".
4. **CA layer is 92% identity** (11/147 non-trivial rules). Of the 11, the meaningful ones reduce to:
   - "Lone stone dies near enemy" ≈ Go's liberty rule approximated.
   - "Enemy surrounded by 6 friends dies" = Go surround capture on hex (cf. 6-neighbour surround in Run 8).
   - "Cell with 4+ friends births a new friend" ≈ Conway B4 on hex; or equivalently a growth CA like "Seeds"-family.
5. The CA is *not a named Life-like rule*. It is not Conway (B3/S23), Day&Night, HighLife, nor Seeds. But it is structurally close to a "friendly surround → capture / crowded → birth" approximation — which is exactly Go-on-hex expressed as a lookup table.
6. **Closest known analog**: Hex + Go-on-hex + Tron-style overwrite. A compound but not novel.
7. **Adjacent-to-own placement constraint** is borrowed from growth-game family (ataxx, Lines of Action). Not new.

### Would a Hex expert have an advantage?

Yes. Connection theory (bridges, edge templates, parallel ladders) transfers directly. The novel tactical layer (CA suicide + overwrite + ko) adds new shapes, but none that override Hex strategy. A strong Hex player would learn the extra tactics in ~5 games and dominate.

### Adversary's strongest single argument

> "The game is a Hex/Go hybrid with an overwrite/ko rule. All three components were named as findings of Runs 8, 9, and 10. This is Run 11/12 iterating on those findings, not discovering a new genre."

### Rebuttal from P1 and P2

**P1 rebuts (pointing to specific Phase 2 moments):**
- **Game 1 moves 17 and 19** — overwriting (4,5) then (4,6) — have no Hex analog. In Hex you cannot overwrite; in Go you cannot overwrite a stone with your own. The super-ko preventing P2's recapture is a distinct dynamic. A Hex expert's bridge-template would not tell them how to use overwrite-ko offensively.
- **Game 2 move after P2 (2,5): spontaneous birth at (3,4)** — Hex/Go have no spontaneous piece creation. This is real CA content, even if rare.

**P2 rebuts:**
- In Games 1–3, the *reason* P2 lost was that most of my "Hex bridge" moves were illegal — they died to (1,0,1)→0 before they could influence the game. A Hex expert would have to unlearn ~30% of normal Hex moves because the CA filters them. That's not a trivial skill transfer.
- The "adjacent_to_own" constraint with CA suicide creates a very particular growth pattern: your chains must be *thick* (2-wide) in contested regions or they wither. Hex chains are 1-wide. A Hex expert playing 1-wide chains would lose cells to conversion rule (1,1,4)→2 in dense fights — a possibility that did not quite trigger in our games but exists.

### Resolution

Both sides agree: the **closest precedent** is `484fcb3b0471` (Run 10 hex-outnumber champion) combined with prior connection-on-hex games. The CA layer does something in principle (births, 6-neighbour kills, conversion) but in observed play most of its 147 entries never fired — only the suicide rule and overwrite-ko consistently mattered. 

**Team 5 Novelty score: 4/10.** Real novelty exists in the overwrite+ko+CA-suicide *tactical layer*, but the strategic core is a known Hex variant. A Hex or Run-10-archetype expert would outperform a naïve player after modest adaptation. The game is **not** a reskin, but it is **not** a new genre — it is an incremental variant of already-catalogued archetypes.

---

## Phase 5 — Verdict

**Team ID:** team-5
**Game ID:** `06bab8a32425`
**Rules Summary:** 8x8 hex, alternating single placements with `adjacent_to_own` constraint and overwrite permitted; each placement is followed by 2 steps of a mostly-identity cellular automaton (11/147 non-trivial rules, mostly "lone stone dies near enemy" and "crowded cell births"); Hex-style win (P1 connects y=0↔y=7, P2 connects x=0↔x=7); super-ko active.
**Topology:** 2D hex, axis_size=8, 6 neighbours per interior cell.

### SCORES (1–10)

- **Strategic Depth: 3** — P1 has a generic winning plan (sweep edge, overwrite walls). Observed tactical content lies almost entirely in overwrite-ko timing; no long-range positional trade-offs.
- **Emergent Complexity: 5** — CA suicide zones, overwrite-ko tempo, and one observed spontaneous birth give a *handful* of genuinely emergent patterns beyond Hex. But >90% of the CA table never fires.
- **Balance: 2** — P1 won all three games, two of them decisively in ≤15 plies. Every P2 blocking attempt near a lone X died to (1,0,1)→0. P2 had no counter to the overwrite+ko attack. First-move advantage plus the CA filter creates a strong P1 bias.
- **Novelty (post-adversary): 4** — The game is not a direct reskin of any single precedent, but the ingredients (hex, connection win, overwrite, super-ko, CA) are all previously catalogued in Runs 8–11. The CA layer fires too rarely to carry novelty on its own. Strongest adversary point: "Hex+Go-on-hex+Tron-overwrite with a mostly-inert CA". Best rebuttal: the overwrite+ko offensive (Game 1 moves 17/19) has no direct Hex or Go analog.
- **Replayability: 3** — With dominant P1 strategy, varied openings all collapse to the same mid-game pattern (sweep-then-overwrite). Little motivation to replay once the pattern is known.
- **Overall "Would I play this again?": 3** — Interesting once as a CA curiosity; not compelling as a standalone abstract.

### CLOSEST KNOWN-GAME ANALOG
**Hex**, hybridised with **Go** (capture dynamics approximated via CA) and **Tron/Achi**-style **overwrite** under **super-ko**. Closest in-corpus precedent: Run 10 champion `484fcb3b0471` (hex + overwrite + outnumber), and Run 8 champion `d4015a646ae3` (hex + surround + connection). This game's CA *describes* those same capture dynamics in a lookup table rather than as structured rules — and adds suicide filtering on top.

### KILLER FLAWS
1. **P1 has an apparent winning strategy**: sweep down edge column, overwrite any horizontal wall, ride super-ko to freeze the breach. All three games demonstrated this. P2 never achieved connection in any game.
2. **CA suicide filter is one-sided in effect**: because P1 always moves first and establishes isolated lead stones, P2's direct blockers always have friendly=0 next to enemy=1 → suicide. P2's legal moves are systematically pushed one row behind P1's lead.
3. **92% of the CA is inert.** The rule table is `rule_complexity=17` but only ~7 rules ever fire in a game. The rest is noise that inflates complexity without adding play value.
4. **Overwrite is extremely strong for the attacker** — super-ko's asymmetry (the attacker's post-state is new, the defender's recapture state is old) always favours the overwriter.

### BEST QUALITY
The **overwrite + super-ko tactical layer** is genuinely interesting. It produces a distinct "frozen breach" pattern: overwrite a wall stone, and the opponent cannot recapture — so the breach stays permanently, but costs you tempo equal to one move. Combined with the CA suicide rule forbidding direct counter-blocks, this gives the overwriter a "one breach = one free corridor cell" exchange rate that feels fresh. Game 1 moves 17–19 embody this.

### IMPROVEMENT IDEAS
Single rule change: **make the super-ko symmetric by requiring super-ko to also block the *overwrite itself* if the overwriter's board hash has been seen recently** (not just the defender's recapture). Currently the attacker benefits from super-ko asymmetry. An alternative single-rule change: **require placements to have ≥1 friendly neighbour pre-CA to survive** (i.e. ban the "new piece becomes empty" suicide even if the CA would kill it) — this removes the P1 bias from placement near isolated enemies. Either change would put real defensive tools in P2's hands.

---

## Summary

**Verdict:** This is a competently-built Hex variant with a thin but real CA/overwrite tactical layer. P1 appears to have a dominant strategy, making the game significantly imbalanced in observed play (3-0 for P1 across three games, median 15 plies). Go Essence 0.521 and ELO 1115 overstate the game's quality: the CA is 92% identity, and the strategic depth lives almost entirely in a single overwrite-ko pattern.

**Final scores:**
- Strategic Depth: **3**
- Emergent Complexity: **5**
- Balance: **2**
- Novelty (post-adversary): **4**
- Replayability: **3**
- Overall "Would I play this again?": **3**

**Team 5 overall rating: ~3/10.**
