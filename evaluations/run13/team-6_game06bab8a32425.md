# Team-6 Evaluation: Game 06bab8a32425 (Run 13 Champion)

**Team ID**: team-6
**Game ID**: 06bab8a32425
**Database**: genesis_v2_run13.db
**Date**: 2026-04-10

---

## Phase 1 — Rule Comprehension

### Board
- **Topology**: 2D hex, 8×8 (64 cells), offset coordinates, non-wrapping.
- **Neighborhood**: 6 hex-neighbors per interior cell (even/odd row offset scheme).

### Turn Structure
- Alternating turns, 1 placement per turn.
- Max turns: 100.

### Actions
- **Place only** (no movement).
- Placement target is **"any" cell** (empty OR occupied — **overwrite is legal**).
- Constraint: `adjacent_to_own` (must be next to one of your own stones).
- Exception: `first_move_anywhere = True` — *and this re-activates whenever you have zero pieces on the board*. A player whose stones are all wiped out can place anywhere.

### CA Dynamics (player-symmetric, runs 2 steps after every placement)
The CA operates from the acting player's perspective: 0 = empty, 1 = friendly (acting player), 2 = enemy (opponent). The reachable non-identity rules (neighbor totals ≤ 6, given hex max-degree) are:

| (state, F, E) | → | Effect |
|---|---|---|
| 0, 2, 3 | 1 | BIRTH: empty cell with 2 friendly + 3 enemy neighbors becomes friendly |
| 0, 4, 0 | 1 | BIRTH: empty cell with 4 friendly + 0 enemy neighbors becomes friendly |
| 1, 0, 1 | 0 | DEATH: isolated friendly with 1 enemy dies |
| 1, 0, 2 | 0 | DEATH: isolated friendly with 2 enemies dies |
| 1, 1, 4 | 2 | CONVERSION: friendly with 1 friendly + 4 enemy flips to enemy |
| 2, 1, 0 | 0 | ENEMY DEATH: enemy with 1 friendly + 0 enemy dies |

All other 4-connected/higher-density states are identity.

### Capture & Propagation
- `capture_type: none` — no classical capture.
- Overwrite-placement + CA together function as the de facto capture system.
- Super-ko rule is active: moves that reproduce a prior full-board position are treated as passes.

### Win Condition
- **Connection**: Hex-style. P1 connects rows 0→7 (dim 1, vertical). P2 connects cols 0→7 (dim 0, horizontal). First player whose own stones form a BFS-connected chain between the two opposing faces wins.

### Degeneracy Flags
- **NO FORCED WIN IDENTIFIED**. All three playtests went 17–28 moves with genuine contest.
- `first_move_anywhere` reactivating on piece-extinction is unusual but not degenerate — it grants a small compensation for being wiped.
- Super-ko + overwrite prevents simple ping-pong recapture loops. Good design.

---

## Phase 2 — Strategic Play

### Game 1 (P1 = vertical blitzer, P2 = peripheral builder)
Opening moves: P1 (4,4); P2 (3,4) [rejected by CA mutual-annihilation] → P2 retreats. Sequence: 35, 28, 43, 27, 27-overwrite, 33, 19, 34, 34-overwrite, 32, 11, 33, 3, 34-recap, 51, 42, 59.

**Key moments:**
- **Move 5 — P1 overwrites (3,3)**: captures 1 P2 stone; CA `2,1,0→0` kills P2's other stone via isolation. Net +2 swing. P2 reduced to zero.
- **Move 9 — P1 overwrites (2,4)**: captures 1, CA kills (1,4) (rule `2,1,0→0`), AND triggers **a BIRTH at (2,3)** via `0,4,0→1` because (2,3) had 4 friendly neighbors (3,3),(2,4),(3,4),(3,2) and 0 enemies. **Net +3 swing** in a single move.
- P2 never recovered despite `first_move_anywhere` restarts.

**Result: P1 wins move 17** (vertical col 3 from (3,0) to (3,7)).

### Game 2 (P1 = vertical, P2 = center disruptor)
Sequence: 27, 24, 35, 25, 43, 26, 26-ow, 33, 25-ow, 25-KO-pass, 19, 25-ow(non-ko), 11, 26-ow, 3, 27-ow, 34, 35-ow, 42, 28, 20, 29, 21, 37, 22, 38, 23, 39.

**Key moments:**
- **Move 8 — P2 attempts to recapture (2,3)**: triggers **super-ko violation**; becomes a pass, tempo lost. Discovery: ko-rule hard-blocks simple recapture cycles.
- **Move 18 — P2 overwrites (3,4)**: CA kills P1's (3,5) via `2,1,0→0`. Combined with move-16 capture of (3,3), this **severs P1's vertical chain entirely**.
- **Move 19 — P1 plays (2,5) self-destructively**: CA rule `1,1,4→2` flips (2,4) into enemy, then `1,0,2→0` kills (2,5) in step 2. P1 loses 2 stones from one placement — a **"CA suicide"** trap from placing into enemy-dense territory.
- P2 pivots to horizontal race on row 4.

**Result: P2 wins move 28** (horizontal connection through rows 3-4 chain from (0,3) via (1,4) → (7,4)).

### Game 3 (P1 = vertical, P2 = corner-to-wall defender)
Sequence: 35, 56, 43, 49, 27, 50, 51, 51-ow, 19, 52, 11, 53, 3, 54, 52-ow, 60, 59.

**Key moments:**
- **Move 8 — P2 overwrites (3,6)**: blocks P1's southern pathway. No CA kills (all adjacencies protected by the identity `2,1,1→2`).
- **Move 14 — P2 extends row-6 wall to (6,6)**: creates a 5-stone blocking wall cols 1-6 on row 6.
- **Move 15 — P1 overwrites (4,6)**: opens a hole in the wall and prepares a hex-diagonal bypass.
- **Move 16 — P2 cannot recapture (4,6) (super-ko)**, must play (4,7) to block. But the wall now has a structural weakness at (3,7).
- **Move 17 — P1 plays (3,7)**: bridges via (3,5)→(4,6)→(3,7), outflanking the entire wall.

**Result: P1 wins move 17.**

### Per-player strategy guides

**Player 1 (vertical connector) guide:**
1. First move near center of own axis — (3,4) or (4,4).
2. Keep stones **clustered** — every placement should be adj to ≥1 existing friendly to avoid CA death (`1,0,1→0`).
3. Exploit overwrite-capture aggressively: overwriting an enemy stone adjacent to a lone enemy kills BOTH (the target and the isolated one via `2,1,0→0`).
4. Seek `0,4,0→1` birth spots: an empty cell with 4 friendly hex-neighbors births a free friendly stone. The hex topology + column-chains produce these naturally.
5. AVOID `1,1,4→2` conversion traps: never place a stone with only 1 friendly neighbor when 4+ enemies surround it. Pre-build the 2-friend anchor first.
6. Super-ko is your ally on defense: after capturing, the opponent often cannot recapture because it reproduces a prior position.

**Player 2 (horizontal connector) guide:**
1. P2 gets move 2 — the *pie rule is absent*, so P2 has no compensation for first-move disadvantage. P2 is inherently losing material wars.
2. Play far from P1's opening (≥2 hex steps) so the opening CA doesn't mutually annihilate.
3. **Wall defense beats race**: a 5-6 stone row-6 (or row-4) wall denies P1's route faster than racing horizontally.
4. Overwrite + CA-conversion is the strongest attack: overwriting at an enemy's weak anchor while 4+ enemies cluster can flip the whole anchor via `1,1,4→2`.
5. Super-ko is a defensive wall: once you capture, P1 often literally cannot recapture.

---

## Phase 3 — Strategic Analysis (joint P1/P2)

### Distinct viable strategies?
**Yes**, at least three distinct archetypes emerged:
- **Column blitz** (Game 1, Game 3): P1 rushes a single column with `0,4,0→1` birth support from adjacent anchors.
- **Wall-and-gap** (Game 3 defense): P2 constructs a row-6 horizontal wall, forcing P1 into narrow bridge attempts.
- **Overwrite-raid** (Game 2): P2 captures P1's central stones (3,3),(3,4) to sever the vertical chain, then pivots to own axis.

### Counterplay
Meaningful. Each strategy has a known counter:
- Column blitz → wall-and-gap.
- Wall-and-gap → hex-diagonal bridge (Game 3, P1's (4,6)→(3,7)).
- Overwrite-raid → pre-anchor (build clusters BEFORE your opponent reaches overwrite range).

Super-ko + CA conversion rule create a **non-trivial capture economy**: not every overwrite succeeds (ko), and some placements self-destruct (`1,1,4→2` trap).

### Short-term vs long-term tension
Present. Immediate overwriting gains material, but advancing toward your connection face is tempo-critical. A capture that burns 2 moves to extract pays off only if the opponent's chain was 2+ moves from winning. In Game 1 P1 chose captures; in Game 3 P1 chose racing. Both worked.

### Emergent concepts
- **Tempo** — super-ko creates hard tempo penalties.
- **Shape** — `0,4,0→1` birth motif rewards convex stone clusters (similar to Go's influence but with direct material reward).
- **Ko fights** — literal super-ko enforcement + overwrite creates capture-recapture tension that one-sided resolves.
- **CA suicide zones** — empty cells with ≥4 enemy neighbors and <2 friendly neighbors are near-unplayable (`1,1,4→2` conversion kills the placement).

### Topology mattering
**Yes, strongly.** The hex grid's 6-connectivity enables:
- Hex-diagonal bridges (Game 3's (3,5)-(4,6)-(3,7) finish would be impossible on a 4-connected grid).
- The `0,4,0` birth condition is actually *reachable* on hex but rare on von Neumann (where only 4 neighbors are possible).
- Row-parity offset coordinates (even vs odd rows) create asymmetric reach patterns that P2 exploits for wall geometry.

---

## Phase 4 — Novelty Adversary (MANDATORY)

### Adversary Opening Salvo

**Claim: This game is Hex with sprinkled CA garnish. The CA rules are 90% identity; only six transitions fire; and the winning strategy in all three playtests was "make a Hex chain." No expert at a novel game would study this — a Hex master would immediately recognize vertical/horizontal connection races and win.**

**Specific rule correspondences:**

1. **vs Hex (Hein, 1942; Nash, 1948)**:
   - Identical topology (2D hex adjacency).
   - Identical win condition (connect opposite faces, asymmetric per-player axis).
   - Difference: adjacency constraint `adjacent_to_own`; overwrite-placement; CA post-processing. But Game 1 and Game 3 were *literally won by a vertical hex-chain*.
   - "Hex master advantage": absolutely. A Hex expert would understand face-connection strategy, two-bridge, edge templates.

2. **vs Y (Schensted, 1953) / Havannah (Freeling, 1979)**:
   - Weaker correspondence — Y/Havannah have different win faces and loops. Not a direct match.

3. **vs Reversi/Othello**:
   - Shared element: overwrite-placement as capture. But Reversi captures via enclosure, not direct placement. Different goal (territory vs connection).

4. **vs Chameleon / Lines of Action**:
   - Chameleon shares the "place on enemy to convert" mechanic. But Chameleon lacks connection goals. Partial overlap only.

5. **vs Pente / Gomoku / Connect6**:
   - Goal is n-in-a-row, not face-connection. No CA. Weak analog.

6. **vs Life-like CAs (Conway's Life B3/S23, Day & Night B3678/S34678, HighLife B36/S23)**:
   - Conway's Life: empty → alive if exactly 3 neighbors. Alive survives if 2-3. This game's birth rules are `(2F,3E)` and `(4F,0)` — NOT equivalent to B3 (total=3 regardless of type). Death rules require enemy presence, unlike Life. So this is **NOT a Life-like rule** — it's a two-state-with-friend/enemy distinction CA with partial-Life flavor.
   - **Closest CA analog**: Nowak & May's spatial prisoner's dilemma (two-color PD) or the voter model, not a Life derivative.

7. **vs Go**: Surround-capture absent. Not Go.

### Adversary's Topological-Transformation Argument

**"Under the transformation 'ignore CA + ignore overwrite + play only empty cells', this game is EXACTLY Hex. The CA kills 'uncommitted' stones (isolated advance scouts) — which is what Hex players already avoid by playing two-bridge shapes. Overwrite lets you capture, but super-ko prevents productive recapture cycles, so the net effect is 'Hex with expensive captures.' A Hex expert adds +2 rules and plays on."**

### Rebuttal (P1 + P2 joint)

The adversary is **partially correct but overstates**. Three concrete Phase 2 moments where a Hex-purist strategy would fail:

1. **Game 2, Move 9 — `2,1,0→0` CA kill**: P1 overwrote (1,3), expecting to kill P2's (0,3) and (1,4) via CA. **A Hex expert would not even consider CA interactions.** The move's correct calculation required knowing that `2,1,1→2` is identity (so the double-enemy-adjacent kill DOES NOT fire). Hex intuition gives no guidance here. In fact I (playing P1) incorrectly predicted the kill and was wrong about its scope — the actual outcome was +1, not +3.

2. **Game 2, Move 19 — `1,1,4→2` conversion trap**: P1 played (2,5), a move that would be **uncontroversial in Hex** (extending a chain two cells away). The CA flipped (2,4) into P2 AND killed (2,5), costing P1 two stones for one placement. **This has no analog in Hex.** A Hex expert following standard intuition would make the same blunder. Evidence: my P1 play, which I thought was reasonable, collapsed the position.

3. **Game 3, Move 15 — overwrite (4,6) + super-ko tempo**: P1 broke P2's wall by overwriting an enemy stone inside the wall. P2 **literally could not recapture because doing so reproduces move 14's state → ko violation**. In Hex, there's no analog — you can't place on enemy stones. The super-ko + overwrite-capture *interaction* creates a mechanic (locked capture) that only exists because the game has both features.

### Additional rebuttal — shape-reward via birth

The `0,4,0→1` birth rule rewards convex hex clusters with free stones. In Game 1, move 9 triggered this birth at (2,3), gifting P1 a stone. **Hex has no such material reward for shape** — Hex is purely about connection paths. The birth rule creates a Go-like "good shape" pressure that Hex entirely lacks.

### Adversary closing jab

**"OK, so it's Hex with three CA footnotes. The CA footnotes add tactical wrinkles but NOT a new strategic skeleton. The Phase 2 games all ended with a hex chain from face to face. The chain was built and broken and rebuilt, but the WIN STATE is still a Hex chain. This is 'Hex plus' — not a new game."**

### Team verdict

The adversary is right that the **win condition is Hex**. But the **move-by-move game is NOT Hex**, because:
- Legal moves include overwriting (no Hex analog).
- Correct move evaluation requires CA arithmetic (no Hex analog).
- Super-ko blocks trades that would be routine in capture games (modifies the capture-economy).
- Convex-cluster shape is rewarded by `0,4,0` birth (no Hex analog).

It sits **between** Hex-with-captures and a CA placement game. Worthy of a novelty score in the 5–6 range: not a re-skin, but not radically new either. The strongest case for novelty is **the ko-locked capture dynamic** (overwrite + super-ko) combined with **`1,1,4` conversion traps**, which together create a material economy unlike any cited reference game.

---

## Phase 5 — Verdict

**Team ID**: team-6
**Game ID**: 06bab8a32425
**Rules Summary**: 2D hex 8×8, Hex-style connection win, placements may overwrite enemies, with a 2-step CA per turn that rewards convex clusters (via birth) and punishes isolated or outnumbered stones (via death/conversion). Super-ko prevents recapture loops.
**Topology**: 8×8 hex grid, non-wrapping, 6-connected.

### SCORES (1-10)

- **Strategic Depth: 6** — Multiple viable archetypes (blitz, wall, raid) emerged in only 3 games. Correct move evaluation requires thinking about CA interactions, overwrite trades, and ko-locking simultaneously. However, many moves are mechanical (extend-adjacent-along-axis) and the central column is often decisive, which caps depth.

- **Emergent Complexity: 7** — Birth rules create Go-like shape pressure (convex clusters gain free stones). Conversion rule creates "suicide zones." Super-ko creates literal ko tempo fights around key overwrite targets. These three interact to produce non-obvious tactical moments — more complex than plain Hex, though not as deep as Go.

- **Balance: 5** — In my three games P1 won 2/3; in the random-game test P1 also won. The `first_move_anywhere` reactivation on extinction is P2's only compensation for being zero-stoned mid-game, but it doesn't match P1's first-move spatial advantage. Training logs showed 50/50 final win rate, which may reflect seat-swapping during training rather than true balance. Suspect modest P1 bias.

- **Novelty (post-adversary): 5** — Win condition is indistinguishable from Hex, which is the adversary's strongest claim and it lands. The overwrite + super-ko + CA-conversion ensemble is genuinely novel as a tactical substrate, and the Game 2 move-19 trap and Game 3 move-15 bridge have no Hex analog. But the game is describable as "Hex plus tactical CA" to any Hex player, and the strategic skeleton (build edge-to-edge chain) is inherited wholesale.

- **Replayability: 6** — Different openings lead to different archetypes (Games 1, 2, 3 were all quite different). CA adds branching tactical variance. However, the central-column race is a strong attractor — repeated play may converge on it.

- **Overall "Would I play this again?": 6** — Yes, briefly, especially to probe CA edge cases. But I wouldn't choose it over Hex for a serious match, and the CA-suicide traps feel more punishing than rewarding.

### CLOSEST KNOWN-GAME ANALOG

**Hex** (with pointy-top orientation). Identical topology, identical win structure, identical axis assignment. The novel additions are (a) overwrite-placement, (b) super-ko, and (c) the 6-rule CA. Not identical because overwrites and CA interactions produce tactics that Hex cannot express.

Secondary analogs: **Chameleon** (overwrite-flip) and a heavily-modified **Nowak-May spatial two-color voter model** (for the CA kernel).

### KILLER FLAWS

1. **P1 first-move advantage** appears material. No swap/pie rule. Three games and a random-game test all went P1-favorable.
2. **`1,1,4→2` conversion trap** is borderline degenerate — a legal placement can *cost you stones* through no visible threat. Players must be actively wary of placing near 4+ enemies; this discourages contact play.
3. **Self-destructive CA opening**: placing your first stone adjacent to P1's opening triggers mutual annihilation via `1,0,1→0` + `2,1,0→0` + super-ko → effectively a forced pass. P2 is locked into non-contact openings.
4. **Overwrite + super-ko asymmetry** — the first player to capture at a key cell often locks the capture permanently. This is interesting but creates winner-take-all moments.

### BEST QUALITY

The **overwrite + super-ko + CA conversion** combo. A player can capture a stone, and the opponent cannot recapture (ko); or a placement can *convert your own stone into an enemy* (conversion). Neither has a direct analog in mainstream abstract games. The Game 3 sequence where P1 punched a hole in P2's wall and P2 was super-ko-locked out of repair is a genuine "new game" moment.

The `0,4,0→1` birth rule also deserves credit: it rewards building convex clusters with free stones, echoing Go's good-shape concept but with direct material realization.

### IMPROVEMENT IDEAS

1. **Add a pie/swap rule** to rebalance P1's first-move advantage (standard Hex remedy).
2. **Soften `1,1,4→2`** — this conversion is so punishing it makes contact-play nearly taboo. Changing it to `1,0,4→2` (only truly isolated stones convert) would preserve the "exposed stone" motif without discouraging engagement.
3. **Optionally**: require placements to target empty cells, with a separate "overwrite/capture" action gated on a capture condition. The current "any cell" placement makes every move a potential overwrite; making overwrite explicit would clarify the game's identity.

---

## Appendix: CA Transition Table (reachable non-identity entries only)

```
(state=0, F=2, E=3) → 1    [BIRTH: contested-edge birth, F+E=5]
(state=0, F=4, E=0) → 1    [BIRTH: convex-friendly cluster, F+E=4]
(state=1, F=0, E=1) → 0    [DEATH: lone-friendly-vs-1-enemy]
(state=1, F=0, E=2) → 0    [DEATH: lone-friendly-vs-2-enemies]
(state=1, F=1, E=4) → 2    [CONVERSION: outnumbered-friendly-defects]
(state=2, F=1, E=0) → 0    [ENEMY DEATH: lone-enemy-vs-1-friendly]
```

Entries with F+E > 6 exist in the table but are unreachable on a hex grid (max 6 neighbors). All other reachable entries are identity — the CA is genuinely sparse.

---

## Final Summary

**Verdict: A well-crafted but incrementally-novel Hex variant.**

- Strategic Depth: 6
- Emergent Complexity: 7
- Balance: 5
- Novelty: 5
- Replayability: 6
- Overall: 6

Game 06bab8a32425 is Hex with a tactical CA wrapper. The CA wrapper creates genuinely new tactical moments (ko-locked overwrites, conversion traps, cluster-birth shape rewards) that a Hex expert would need to re-learn. But the strategic skeleton — connect opposite faces — is inherited from Hex verbatim, and the win condition is identical. Worth preserving as a Run-13 champion and a Hex-variant curiosity, but not a standalone novel abstract game. A pie rule and a softer conversion rule would meaningfully improve it.
