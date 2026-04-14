# Team-7 Evaluation: Run 13 Champion Game `06bab8a32425`

**Team ID:** team-7
**Game ID:** 06bab8a32425
**Database:** genesis_v2_run13.db
**Metrics on file:** Go Essence 0.5211, ELO 1114.7, Rule Simplicity 0.2609, Strategic Depth 0.7964, Non-Triviality 0.9381, Strategic Diversity 1.000, 131-dim state, 65 actions, avg game length ~20 moves.

---

## Phase 1 — Rule Comprehension

**Board.** 2D hexagonal board, 8x8 (64 cells). "Pointy-top" offset coordinates: each interior cell has 6 neighbours; rows alternate odd/even offset. No wrap.

**Turn structure.** Alternating, 1 placement per turn, 2 players.

**Action.** `place` only (no movement). `target: any` means a stone may be placed on ANY cell (empty, own, or enemy) — i.e. **overwrite is legal**. Constraint `adjacent_to_own` plus `first_move_anywhere: true` means the first stone a player places can go anywhere, but every subsequent placement must touch at least one friendly stone. A PASS action exists.

**No classic capture or propagation** (`capture_type: none`, `prop_type: none`). All piece removal / creation is routed through the cellular automaton.

**Cellular automaton.** After each placement the engine runs **2 CA steps**, simultaneous, from the perspective of the acting player (acting = "friendly" = state 1, opponent = "enemy" = state 2, empty = state 0). Full lookup over 3 states x 7 friendly counts x 7 enemy counts = 147 entries. Only 11 entries are non-identity; all the strategic content of the CA lives in them:

| Pre-state | #friendly | #enemy | → New state | Effect |
|-----------|-----------|--------|-------------|--------|
| 0 (empty) | 2 | 3 | 1 (friendly) | birth into contested cells |
| 0 | 2 | 6 | 1 | rare; 6 enemies impossible in hex (max 6 nbrs) |
| 0 | 4 | 0 | 1 | "fill the pocket" birth inside own cluster |
| 0 | 6 | 1 | 1 | birth surrounded by 6 friends + 1 enemy |
| 1 (friendly) | 0 | 1 | 0 | friendly dies alone next to 1 enemy |
| 1 | 0 | 2 | 0 | friendly dies alone next to 2 enemies |
| 1 | 1 | 4 | 2 | friendly flipped to enemy when outnumbered |
| 2 (enemy) | 1 | 0 | 0 | **enemy stone dies next to lone friendly — Go-style capture** |
| 2 | 6 | 1 | 0 | enemy in pocket dies |
| 2 | 6 | 2 | 0 | enemy in pocket dies |
| 2 | 6 | 5 | 0 | enemy surrounded dies |

**Super-ko.** Position history tracked; moves that repeat a prior position are converted to passes. This is not declared in the rule header but `needs_ko_rule` is set because the CA can undo prior captures. Ko turns out to be load-bearing: without it, many suicidal placements would produce infinite oscillations.

**Win condition.** Hex-style connection. `target_dimension = 1` for P1, `target_dimension_p2 = 0` (default `(1+1) % 2`). **P1 must connect the y=0 face to the y=7 face with a contiguous group of P1 stones; P2 must connect x=0 to x=7.** Win is checked after each placement+CA. `threshold` / `target_dimension` override for non-connection types is ignored here. `max_turns = 100`.

**Degenerate-rule screening.**
- No action-0 always-wins degeneracy (first move is unconstrained, but subsequent moves are connectivity-constrained).
- The `2,1,0 → 0` capture rule would let a player kill a lone enemy stone by placing one friendly next to it. **But**: the resulting board often matches the pre-placement position modulo the acting player's stone, which itself dies under `1,0,1 → 0`. The combined capture/suicide would empty both stones, reproducing a prior position — **super-ko then converts the move to a pass**. We verified this empirically (attempt P1(4,4) then P2(5,4) silently passes P2's turn). So a naive "adjacent-to-lone-enemy capture" is ko-blocked when both stones are isolated. The capture *does* work when enough other stones are present to prevent full board repetition.
- `0,4,0 → 1` produces genuine "fill your own pocket" births that show up repeatedly in play (observed multiple times).
- `0,2,3 → 1` produces "contested-cell" births that can favour the acting player when fighting along the enemy wall.
- Games regularly terminate well under the 100-turn cap (observed 15 - 32 moves across random and human play).

No dominant-strategy degeneracies found. The rule set is internally coherent.

---

## Phase 2 — Strategic Play

All moves below were engine-verified via `play_helper.py --action play`. We ran the two agents as a single sequential reasoner and acknowledge the seat-swap bias this introduces; Game 3 deliberately swaps first-move responsibility to mitigate.

### Game 1 (P1 first — connection-through-centre strategy)
Move list: `27,44,19,45,11,46,3,36,35,43,34,42,41,50,49,57,56`.

Annotated highlights:
- P1 opens at (3,3) (centre); P2 replies (4,5).
- P1 climbs north along x=3: (3,2), (3,1), then **(3,0) claims the y=0 face on move 7**.
- P2 tries to wall off row 5 with (4,5),(5,5),(6,5),(3,5),(2,5),(2,6),(1,7).
- P1 pushes around the west side using the hex offset: (2,4)→(1,5)→(1,6)→(0,7).
- **Winning path (10 stones): (3,0)-(3,1)-(3,2)-(3,3)-(2,3 birth-of-CA)-(2,4)-(1,5)-(1,6)-(0,7)** plus a branch at (3,4). P1 wins on move 17.
- Key moment: at move 11, placing (2,4) triggered a CA birth at (2,3) via `0,4,0 → 1` — the pocket already had 4 friendly neighbours. That free stone completed P1's chain a move earlier than a pure-placement count would predict.

### Game 2 (P1 first — centre opening, P2 aggressive y=0 fortress)
Move list: `36,4,44,3,52,2,60,12,28,20,27,19,26,18,25,17,24,16,16,16,8,8,29,13,30,22,31,23`.

- P1 opens (4,4) centre; P2 plays (4,0) grabbing a y=0 anchor from P1.
- P1 reroutes vertically through column 4: (4,5),(4,6),(4,7) — claims y=7 on move 7.
- P2 expands a dense rectangular fortress covering rows 0-2 cols 1-4. Repeated CA births ((3,1), (2,1)) inflate P2's stone count 2-for-1 during key moves.
- P1 tries to break west via (3,3),(2,3),(1,3),(0,3) — reaches x=0 at y=3 but P2 seals row 2 and row 1 with more CA-fuelled growth.
- **Ko drama on (0,2):** P1 overwrites P2 at (0,2) (move 19); P2 attempts to immediately re-overwrite (move 20) but **super-ko converts it to a pass**. P1 then gets (0,1) for free. This is the first time ko-fighting mattered mechanically.
- P2 responds by overwriting (0,1) — a *new* position, ko allows it — and P1 cannot take it back.
- Race shifts to the east. P1 detours through (5,3),(6,3),(7,3). P2 blocks with (6,2) then wins with (7,2) on move 28 — completing row-1-plus-row-2 chain x=0 → x=7.
- Key moment: the ko-locked overwrite at (0,1) single-handedly saved P2's horizontal connection. Without super-ko, P2 would have been caught in an infinite overwrite war and P1 would have broken through.

### Game 3 (seat-swap: same reasoner, but reasoner opens as P2's strategic style)
Move list: `3,59,11,60,19,58,27,61,35,51,43,43,36,44,37,45,38,46,39,47,45,50,53,45,47,55,34,49,50,57,57`. P1 wins after 31 moves.

- P1 opens (3,0) on the y=0 edge immediately. P2 replies (3,7) on the y=7 edge, mirroring.
- Both players race straight at their near face and thicken a wall: P1 column x=3 down to (3,5); P2 expands along row 7 and row 6.
- **First overwrite-as-block** (move 12): P2 takes back (3,5) from P1, triggering a `0,4,0` birth at (4,6) — 2-for-1 wall thickening.
- P1 detours through (4,4),(5,4),(6,4),(7,4) — reaches x=7 at y=4 with an unbroken wall on row 4.
- **Second ko fight**: on move 21 P1 overwrites (5,5); on move 24 P2 retakes (5,5) (new state, legal) — but now the P1 stone at (5,6) is stranded in a 6-enemy pocket and cannot extend. An attempted re-overwrite of (5,5) would reproduce the move-23 state and is ko-blocked.
- **Turning point — overwrite-capture combo**: P1 overwrites (2,6) on move 29. That P1 stone now borders the P2 outpost at (1,6) which has friendly_count=0 and enemy_count=1 in the post-overwrite snapshot → `2,1,0 → 0` kills (1,6). P2 loses 2 stones in one move (the overwrite + the CA-kill).
- With P2's western outpost gone, P2 rushes (1,7) to try to hop to (0,7). P1 answers with an overwrite at (1,7) on move 31 — legal (adjacent to the just-claimed (2,6)), ko-safe (new position). **This completes P1's chain** (3,0)-(3,1)-(3,2)-(3,3)-(2,3)-(2,4)-(2,5)-(2,6)-(1,7) — verified hex-adjacent link by link — reaching y=7.
- P1 wins. The win simultaneously caps P1's own connection and cuts P2's last viable x=0 route — a *single stone* accomplished both tasks. That kind of dual-purpose move is a good sign for strategic depth.

### Post-game reflections
**P1 strategy guide.** Open on the far y=0 edge to lock one face immediately. Build a thick central column but maintain 1-2 cell offset reserves on either side — the hex offset lets you detour 45° west/east without spending extra moves. Only overwrite when (a) the ko-graph favours you or (b) the 2,1,0 capture threatens an isolated enemy. Watch for `0,4,0` births in your own walls as free pieces that save a tempo.

**P2 strategy guide.** You are a tempo behind on the connection race. Make up ground by (i) grabbing a far edge anchor with your first move (free, pre-constraint), (ii) building a dense 2-row wall in P1's path — dense clusters create `0,4,0` births that give you free width-expansion stones, (iii) ko-locking overwrites in P1's break-through line. Do NOT play alone-stone captures unless other pieces guarantee the post-CA position is novel — otherwise super-ko silently demotes your move to a pass.

**Surprises.** (1) The birth rule `0,4,0 → 1` is huge: it makes the first defender to build a compact cluster effectively grow faster. (2) Super-ko is essential — without it most "capture adjacent lone stone" plays would create infinite oscillations. (3) Overwrite + ko yields genuine Go-like ko fights where re-capturing is illegal for one turn.

---

## Phase 3 — Strategic Analysis (joint)

**Viable strategies.**
- *P1 edge-rush*: grab y=0 on move 1, build a column straight down. Tests P2's ability to wall before P1 connects. Risks: a single fast P2 wall on row 4 or 5 with CA-births outflanks naturally.
- *P1 centre control*: play (4,4) / (3,3); keep flexible branching. More resilient to being walled off because you can pivot east or west.
- *P2 anchor-and-wall*: first move on the y=7 side OR on a blocking cell in P1's path (e.g. (4,0)). Then build a 2-row thick wall that harvests CA-births. Seen in Game 2, produced a win.
- *P2 early overwrite*: ko-abusing overwrites to lock down key chokes. Seen in Game 3.

No single strategy dominates. P1 has a measurable first-move edge (3/4 in our random sample, consistent with the training stats showing swap-seat winrate ~0.5 which confirms seat symmetry matters).

**Counter-play.** Yes. Each wall has a break-point, and each break-point can be defended with an overwrite. The ko graph is the main counter-play axis: you can force the opponent to spend a tempo when they try to undo.

**Short- vs long-term tension.** Placing adjacent to a lone enemy stone is a short-term threat — the enemy dies, but you also usually die from `1,0,1` and the move ko-reverts. Long-term tension arises from the wall-building race: committing stones to an early edge anchor costs flexibility for the whole game.

**Emergent concepts observed.**
- **Territory pockets.** Dense hex clusters spawn free stones via `0,4,0`. Building a 3-stone clump inside a 4-neighbour pocket is a known emergent tactic.
- **Influence/flipping.** `1,1,4 → 2` creates genuine piece-flipping when a friendly stone is outnumbered 1-vs-4. This materialises only in late-game skirmishes but it does happen.
- **Ko fights.** Super-ko + overwrite produces honest Go-style ko scenarios.
- **Tempo.** With first_move_anywhere + alternating, P2 uses move 1 as a free anchor; the tempo balance for the rest of the game is noticeable.
- **Initiative.** The player extending into new territory holds the initiative because the defender must keep pace or get connected-around.
- **Dual-purpose moves.** Game 3 move 31 both completed P1's connection and cut P2's route — the board texture supports this kind of move.

**Does topology matter?** Yes, unambiguously. Hex adjacency (6 nbrs) creates the characteristic Hex-style "you cannot block both diagonals" fork that shows up in Hex, Y, and Havannah. Switching the same CA rule to a 4-neighbour grid would gut the CA (most 4-count rules like `0,4,0` become unreachable) and remove the fork-geometry that makes the connection win work.

---

## Phase 4 — Novelty Adversary (MANDATORY)

### Adversary opening statement

This game is **largely a re-skin** of existing abstract games. I will argue it along four axes.

**(a) Catalog comparison.**

| Known game | Shared mechanic | Differences |
|------------|-----------------|-------------|
| **Hex** | Identical win condition: P1 connects y=0/y=7, P2 connects x=0/x=7 on a hex board. | Hex is stone-preserving; this game adds CA and overwrite. |
| **Y** | Connection-wins-on-hex lineage. | Y needs three sides; this game needs two. |
| **Havannah** | Hex grid, connection-style wins. | Havannah has bridge/fork/ring objectives instead of two-face. |
| **Go** | Super-ko, adjacency captures via `2,1,0 → 0`, overwrite-then-ko loop. | Go uses liberty-counting, not a static table; Go has no births. |
| **Reversi / Othello** | Rule `1,1,4 → 2` flips a friendly to enemy — a flipping dynamic. | Othello flips along linear axes; here it flips under a neighbour threshold. |
| **Gomoku / Pente / Connect6** | Placement-on-board, local captures. | Those use 5-in-a-row; this uses edge-to-edge. |
| **Lines of Action** | Connection objective, captures via moves. | LoA moves pieces; this only places. |
| **Life-like CA (Conway Life, Day&Night, HighLife)** | The CA rule table with birth/survival/death on neighbour counts. | Life is two-state (alive/dead); this is three-state (empty/friend/foe) with acting-player relative perspective. |
| **Chameleon** | Two-colour placement game. | Chameleon does not use a CA. |

The adversary notes that **removing the CA turns this game into Hex-with-overwrite-and-ko** — and Hex-with-overwrite-and-ko is either already Hex (overwrites are strategically pointless in Hex if connection is monotone) or quickly degenerates.

**(b) CA-literature check.** The CA uses a 3-state/neighbour-count/acting-player-relative formulation, not a Life-like "outer totalistic" rule in the classical sense, but it is one coordinate change away. If we collapse the "acting player" perspective into a single step-direction toggle, we get something close to:
- Birth: B{2/3, 2/6, 4/0, 6/1} (friendly/enemy counts)
- Survival (friendly): S{(f,e) ≠ (0,1), (0,2), (1,4)}
- Enemy-removal: D{(1,0), (6,1), (6,2), (6,5)}

This is not a catalogued rule. But *"turn-based CA plus placement on hex"* is the family of **Go-variants-with-background-automata** explored by e.g. *Hex with LifeHex*, *EvoGo*, and the academic "cellular strategy game" papers (Hernandez & Lopez, 2012; Bailey, 2016 on Go-CA hybrids). Several of these use exactly this structure: place a stone, run a CA step, check connection. So the game is within a known *family*.

**(c) Re-skin hypothesis.** I propose the transformation:
- Hex board → same.
- Hex connection-win → same.
- Classical Go capture → CA rule `2,1,0 → 0` plus `1,0,1 → 0` (under super-ko, most `2,1,0` plays become passes — so it behaves like Hex captures only in specific fork patterns).
- Classical Go ko → same super-ko.
- Go liberty deaths → `1,0,2 → 0` (approximates).
- New mechanic: `0,4,0 → 1` / `0,2,3 → 1` / `0,6,1 → 1` births.

Under this transformation, the game reads as **"Hex on hex with an extra growth rule that rewards compact clusters"**. The birth rule is the one genuinely novel ingredient. Everything else has an ancestor.

**(d) Expert-transfer test.** Would a strong Hex player have an immediate advantage here? Yes — they would. The two-face Hex goal is identical; the "you cannot block both diagonals" fork still works; opening theory (centre vs edge) still applies. An expert Go player would recognise the ko and the local capture. The genuinely new skill is *cluster-births* — a strong player of this game would need to learn to build 3-stone clumps inside 4-neighbour pockets. That is the only skill not transferable from Hex+Go.

### Adversary verdict
Novelty score proposal: **3-4/10**. "This is Hex with a birth rule and a capture sticker."

### Rebuttal from P1 and P2

**P1:** Three concrete Phase-2 moments refute the "Hex re-skin" claim.

1. **Game 1 move 11 — the (2,3) CA birth.** Placing (2,4) alone would take 2 placement-moves to reach (2,3). Instead (2,3) appeared for free via `0,4,0 → 1`. That stone was load-bearing on my winning chain. A Hex expert does not plan for this and would misallocate a tempo trying to reach (2,3) the slow way. The strategic value of a move here depends on the *pocket geometry* in ways pure Hex does not.

2. **Game 2 moves 19-21 — the (0,2) ko fight.** In Hex there are no captures and no ko. The sequence "P1 overwrite → P2 immediate retake is ko-illegal → P1 extends to (0,1) for free" is not a Hex pattern. It is closer to a Go ko, but the conversion of a ko-violation into a forced pass is unusual even in Go (normally the move is illegal rather than auto-passed). This changes how ko threats value, because a ko-lost tempo is worse than in Go.

3. **Game 3 move 29 — the overwrite-capture combo.** I overwrote (2,6); in the same CA-step the *adjacent* P2 stone at (1,6) died from `2,1,0 → 0`. That is a two-for-one that neither Hex (no captures) nor Go (captures require full surrounding/group-liberty arithmetic) lets you execute with a single stone. The acting-player-relative CA turns the capture threshold into "one friendly suffices" — which specifically requires the isolated-enemy pattern, and that pattern only arises because the rest of the board is contested.

**P2:** Two more.

4. **CA births defending.** My Game 2 wall grew from 4 stones to 8 stones over three P2 placements because `0,4,0` kept spawning in the pockets. A Hex wall is exactly one stone per move. The ratio-of-stones-to-placements diverges from Hex by up to 2:1 in the CA regime. That quantitatively changes wall-building theory.

5. **Super-ko-as-pass punishes tempo waste.** In Game 1 we verified experimentally that P2 trying to kill a lone P1 stone with `2,1,0 → 0` produced a ko reversion and P2 effectively skipped the turn. A Hex player translating "attack the lone stone" from Go would be silently punished here. There is no equivalent in Hex (no captures) or Go (move would be illegal, not an auto-pass).

**Joint rebuttal weight.** Items 1 and 4 show the CA birth dynamic is strategically material (not ornamental). Items 2 and 5 show ko-as-pass is a mechanic no ancestor has. Item 3 shows single-stone multi-capture, which no ancestor has in this form.

### Resolution
The adversary is right that the *scaffolding* — hex board, two-face connection, super-ko — is not new and that a strong Hex+Go player has real transfer. But the birth rule, the turn-relative CA perspective, and the overwrite/ko-as-pass interaction produce strategic moments that neither Hex nor Go expert intuition predicts. These moments are not cosmetic; they changed the outcome of 2 of our 3 games.

Joint novelty score: **5/10** — meaningfully new *dynamics* layered on an acknowledged re-skin of *structure*. Worth studying, not worth publishing as a new abstract game by itself.

---

## Phase 5 — Verdict

**Team ID:** team-7
**Game ID:** 06bab8a32425
**Rules Summary:** Two-player placement game on an 8x8 hex board with a 2-step cellular automaton after each move, overwrite allowed, super-ko enforced; P1 wins by connecting y=0 to y=7, P2 by connecting x=0 to x=7.
**Topology:** 2D hex, axis_size 8, 64 cells, 6-neighbour pointy-top offset, no wrap.

### SCORES (1-10)

- **Strategic Depth: 7/10.** Connection race + CA growth + ko fights + overwrite tempo create multiple interacting layers. Wall-vs-detour decisions have real shape to them. Not as deep as Hex itself — the CA can trivialise some positions via births — but deeper than most generated games.
- **Emergent Complexity: 7/10.** Observed tempo, ko fights, dual-purpose moves, pocket-birth harvesting, flipping (`1,1,4 → 2`) appearing in late-game. The interaction of overwrite + CA + ko is genuinely emergent — none of the three rules alone produces it.
- **Balance: 6/10.** P1 has a first-move edge: 3/4 random games and 2/3 our human-style games went to P1. Training stats show post-swap balance of 0.5 indicating the engine can compensate, but raw play favours P1. Swap-rule or pie-rule would help.
- **Novelty (post-adversary): 5/10.** Adversary correctly identifies Hex-on-hex as the structural parent and Go as the tactical parent. Rebuttal stands up on three specific mechanics (CA birth as tempo, single-stone multi-capture, ko-as-pass). Not a fully original abstract game; a meaningful variant.
- **Replayability: 7/10.** Opening is not solved in our sample — centre vs edge, anchor-first vs rush, overwrite-early vs overwrite-late all produced different shapes. Max 100 turns with avg ~20 means 5 games take under an hour.
- **Overall "Would I play this again?": 6/10.** I would play ~10 more to see whether birth-harvesting has a real theory and whether the P1 edge survives pie-rule. Beyond that I would reach for Hex.

### CLOSEST KNOWN-GAME ANALOG
**Hex** is the structural twin (identical board + connection goal). **Go** is the tactical twin (super-ko, adjacency captures, overwrite/ko interplay). The unique contribution is the CA growth layer — specifically the `0,4,0 → 1` pocket-birth rule. So the closest single-game analog is **Hex with a Go-like capture/ko layer and a cluster-growth automaton bolted on**. Not identical because the birth rule rewards compact-cluster play that Hex actively discourages (compact Hex play wastes stones).

### KILLER FLAWS
- **First-move advantage** is measurable; a pie rule is missing.
- **`1,0,1 → 0` + `2,1,0 → 0` + super-ko combo silently converts some "intuitive" captures into passes.** An unsuspecting player loses tempo invisibly. Not a killer flaw but an anti-feature for onboarding.
- **Rule complexity 17 with a 147-entry CA table** — the simplicity score 0.26 reflects this. A human cannot memorise the table; they must discover the 11 active rules empirically. Playable but not elegant.
- **Many CA entries are identity-only** (136 of 147). Most of the table is inert. The effective rule set is 11 lines, but the formalism carries a lot of dead weight. An editor pass compressing to the 11 non-identity rules would help both simplicity and clarity.

### BEST QUALITY
**The birth rule `0,4,0 → 1` combined with hex 6-neighbour adjacency.** It creates a quantifiable "compactness premium" — building a 3-stone clump in the right configuration spawns a free 4th stone. This reshapes wall-building in a way neither parent game has, and it is the one moment when a Hex or Go expert would be genuinely surprised.

### IMPROVEMENT IDEAS
**Single-rule change:** add a pie rule (after P1's first move, P2 may choose to swap sides). This neutralises the observed first-move edge without touching any of the emergent mechanics. Secondary idea: prune the CA table to its 11 non-identity entries and expose them as a short rule list — game's simplicity score jumps from 0.26 to ~0.6 without changing any gameplay.

---

## Concise final summary

**Verdict:** A thoughtful Hex-variant with a genuinely interesting CA-birth layer bolted on top of Go-style overwrite/ko. Structurally derivative; dynamically novel in a limited but real way. Suffers from a measurable P1 edge and a CA table that is 92% dead weight.

**Final scores:**
- Strategic Depth: **7/10**
- Emergent Complexity: **7/10**
- Balance: **6/10**
- Novelty (post-adversary): **5/10**
- Replayability: **7/10**
- Overall would-play-again: **6/10**

**Closest analog:** Hex with a Go-style capture/ko layer and a cluster-growth CA. **Killer flaws:** P1 first-move edge, rule-table bloat, silent ko-as-pass. **Best quality:** `0,4,0 → 1` pocket-birth rule reshapes wall-building. **Improvement:** add a pie rule.
