# Team-12 Evaluation — Pair C (alt + surround + connection)

Team ID: team-12
Pair: C
Fractal candidate: `frac_C_fractal` (sierpinski 9×9, 64 active cells, 17 holes)
Control candidate: `frac_C_control` (grid 8×8, 64 cells)

---

## PHASE 1 — RULE COMPREHENSION

The two JSON files are byte-for-byte identical except for `topology_type` (`sierpinski` vs `grid`), `axis_size` (9 vs 8), the `game_id`, and the metadata `note`/`role` strings.

**Shared ruleset (3-sentence summary):** Two players alternate placing one stone per turn on any empty active cell, with first-move-anywhere; stones form Go-style groups under von Neumann adjacency, and any group reduced to zero liberties is captured (`surround`, threshold 1). Win is by **connection (Hex-style asymmetric)**: P1 wins by forming a connected own-color chain whose cells include both faces along dimension 0 (left ↔ right, columns 0 and *axis_size*−1); P2 wins along dimension 1 (top ↔ bottom, rows 0 and *axis_size*−1). No propagation, no CA; max 100 turns, fall-through is double-pass / max-turns piece-count majority.

**Degeneracy check (substrate-asymmetric):** Connection is reachable on both substrates. The fractal carpet has **four** clean horizontal highways for P1 (rows 0, 2, 6, 8 — fully traversable across cols 0–8) and four clean vertical highways for P2 (cols 0, 2, 6, 8). Rows/cols 1 and 7 are usable in segments. Row 4 / col 4 are essentially useless connectors (only four isolated 2-liberty stub cells each, mutually disconnected because the central 3×3 block plus the four sub-block centers carve them up). No win condition becomes unreachable; no rule applies "only on the fractal." The control's 8×8 grid trivially exposes 8 horizontal and 8 vertical highways.

---

## PHASE 2 — STRATEGIC PLAY

### Game 1 — FRACTAL (P1 = X, P2 = O)

**P1 plan:** Build a horizontal chain along row 2 (a clean highway with full 9 cells, well clear of the central hole). Row 2 is also useful because every stone there has 4 active neighbors (the hole at (1,1) sits in row 1, not row 2).

**P2 plan:** Mirror plan along col 2 (clean vertical highway).

| # | Player | Move | Reasoning |
|---|--------|------|-----------|
| 1 | P1 | **(4, 2)** | Centre of row 2. Note: only 2 liberties because (4,1) and (4,3) are holes — accept the local fragility for the central tempo. |
| 2 | P2 | (2, 4) | Mirror: centre of col 2 corridor. Same 2-liberty stub property because (1,4) and (3,4) are holes. |
| 3 | P1 | (3, 2) | Reinforce; now the X group has 3 liberties; keeps reaching toward (2,2) which is the row-2 / col-2 *intersection* (key contested cell). |
| 4 | P2 | (2, 3) | Same — extend O upward along col 2 toward (2,2). Both players are racing to the intersection. |
| 5 | P1 | **(2, 2)** | Critical: claim the intersection. This simultaneously (a) extends my chain leftward and (b) **cuts P2's col-2 chain in half** — P2 will have to detour. Substrate-relevant: on the fractal, the only neighbouring detours from col 2 around (2,2) are via col 1 (with holes at rows 1, 4, 7) or col 3 (with holes at rows 3–5), so the cut bites harder than on a clean grid. |
| 6 | P2 | (2, 5) | Repair southern side first; keeps liberty at (1,5)/(2,6). Predicted P1: blockage push at (1,2). |
| 7 | P1 | (5, 2) | Continue rightward instead — (5,2) is a strong cell (4 active neighbours), advances the chain. |
| 8 | P2 | (1, 2) | Block P1's left expansion AND seed the col-1 detour. |
| 9 | P1 | (2, 1) | Climb out of the blocked row-2 west; (2,1) keeps liberty options upward via (2,0). |
| 10 | P2 | (1, 3) | Bridge the col-2 gap by going around (2,2) through col 1: now (1,2)–(1,3)–(2,3) connects the northern stub to the main southern chain. |
| 11 | P1 | (6, 2) | Push right; row 2 east is wide open. |
| 12 | P2 | (2, 6) | Continue south. |
| 13 | P1 | (7, 2) | Almost at col 8. |
| 14 | P2 | (1, 5) | Add resilience along col 1 southern detour (because col 1 row 7 is a hole, this chain will need another detour soon). |
| 15 | P1 | (8, 2) | **Reaches col 8 = right face.** Now I just need col 0. |
| 16 | P2 | (1, 6) | Continue. P2 is one cell short of being forced through (0, 6)–(0, 7) corner because (1, 7) is a hole. |
| 17 | P1 | (2, 0) | Connect upward through (2, 1) → (2, 0); now I have row-2 plus a stub into row 0. |
| 18 | P2 | (2, 7) | Continue south along col 2. |
| 19 | P1 | (1, 0) | Stretch toward col 0. |
| 20 | P2 | (2, 8) | **Reaches row 8 = bottom face.** But P2 still needs row 0! And (1, 1) is a hole, (1, 0) is now X — so P2's only northward route is the long way through (0, x). |
| 21 | P1 | **(0, 0)** | **WIN.** X group spans (0,0) ↔ (8,2) — both faces along dim 0. |

**Endgame:** P1 wins by connection on move 21. No captures occurred. P2 had reached row 8 but never reached row 0 — the (1,0)/(1,1) bottleneck (hole at (1,1) plus my stone at (1,0)) made the corner unreachable in one tempo.

**Substrate-specific strategy?** Yes, weakly. Move 5 (claiming the intersection) is more decisive on fractal than on control because P2's detour around it is *forced* into col 1, and col 1 is itself fragmented (holes at rows 1, 4, 7) so the detour costs more tempi. I was deliberately exploiting "the central hole as a wall" — but only indirectly: the wall constrained where P2 could route, not where I had to.

---

### Game 2 — CONTROL 8×8 grid (P1 = X, P2 = O)

Seats nominally swapped (per protocol), but with a single agent driving both sides the move-by-move thinking is identical to Game 1; P1's strategy of row-2 horizontal and P2's strategy of col-2 vertical were ported unchanged.

| # | Player | Move | Reasoning |
|---|--------|------|-----------|
| 1 | P1 | (3, 2) | Centre of row 2 on 8×8 (col 3 is the median). |
| 2 | P2 | (2, 3) | Mirror. |
| 3 | P1 | (4, 2) | Extend right. |
| 4 | P2 | (2, 4) | Extend down. |
| 5 | P1 | **(2, 2)** | Same intersection move. |
| 6 | P2 | (1, 2) | Same block-and-detour-seed move. |
| 7 | P1 | (5, 2) | Push right. |
| 8 | P2 | (1, 3) | Bridge col-2 detour through col 1. |
| 9 | P1 | (6, 2) | Push right. |
| 10 | P2 | (2, 5) | Continue south. |
| 11 | P1 | (7, 2) | **Reaches col 7 = right face.** |
| 12 | P2 | (2, 6) | Continue south. |
| 13 | P1 | (2, 1) | Climb out west. |
| 14 | P2 | (2, 7) | **Reaches row 7 = bottom face.** |
| 15 | P1 | (1, 1) | West push. |
| 16 | P2 | (0, 2) | Reach col 0 face — but P2 needs row 0/row 7, not col face! Still, this builds the western pillar to feed into row 0 next. |
| 17 | P1 | (1, 0) | Climb. |
| 18 | P2 | (0, 1) | Build toward row 0. |
| 19 | P1 | **(0, 0)** | **WIN.** X group spans (0,0) ↔ (7,2). P2 needed one more move to reach row 0 (needed (0,0) or another row-0 cell connected to (0,1)). |

**Endgame:** P1 wins by connection on move 19. No captures.

**Substrate-specific strategy?** The plan was identical; **no move would have differed** had I been playing the fractal version with the same opening positions translated. The detour through col 1 worked equally well on the open grid.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

### Did the fractal play differently?

**Marginally.** Specific moves where the substrate mattered:

1. **Move 1 cell choice** — On fractal, every "row-2 centre" candidate has only 2 liberties because of the row-1/row-3 hole sandwich at col 4 specifically. On control, (3,2) has 4 liberties. **The fractal makes opening moves more fragile.** This is a real, observable difference, but it didn't change the *strategy*; it raised the price of every single step in the central column band.
2. **Move 5 (claiming intersection)** — Costs P2 ~2 extra detour tempi on fractal versus ~1 extra on the control, because col 1 rows 1, 4, 7 are holes and P2's detour through col 1 is itself broken into segments, forcing further weaving. On control, col 1 is a clean 8-cell line. **This is the closest thing to a substrate-novel phenomenon: cuts cost more tempi on fractal because detour corridors are themselves fragmented.**
3. **End-corner capture risk (move 21 on fractal)** — Reaching (0,0) on fractal is special because (1,0)–(0,0) is a 2-stone group with only one common liberty after (0,1) is taken; the same corner on the control has more degrees of freedom. **The corners of the carpet are tactically tighter than corners of the open grid.**

### Choke points / districts

The central 3×3 hole creates a *hard* choke between the western and eastern halves of the board — anything connecting the two halves must go through one of three rows on each side (rows 0–2 or rows 6–8 for horizontal traffic; symmetrically for vertical). On the control, no such mandatory choke exists — every row provides a corridor.

In practice, this is the only fractal-specific phenomenon that *materially* changed play: P1's row-2 chain, once cut at any cell in cols 3–5, has only rows 0, 2, 6 (above the central block) or rows 6, 8 (below) to detour through, all of which are themselves on the "highway list." The choke is not a *trap* — there's no zugzwang or forced bad move I encountered — it's just a constraint.

### Influence shadows

There is **no propagation** in this ruleset, so influence-shadow phenomena are entirely absent. (Pair C uses pure surround capture — no propagation field, no influence value.)

### Path routing (Pair C–specific)

**The forced detour around the central hole did create tempo asymmetry, but it cut both ways.** Both P1 and P2 were forced into the *same* corridor system. On the fractal, P2's col-2 detour through col 1 is *more expensive* than on the control (because col 1 has holes at rows 1, 4, 7 that the detour must avoid). Symmetrically, P1's row-2 detour would be more expensive on the fractal. Since both players pay the surcharge, **it does not produce asymmetric tempo at the player level** — but it does mean *cuts are more potent* on the fractal substrate (each cut on fractal costs more tempi than a cut on control).

### Tempo / first-move advantage

P1 won both games. Game 1 (fractal) finished move 21; Game 2 (control) finished move 19. The 2-move difference equals the increase in path length (8×8 → 9×9 outer ring). **No qualitative change in P1 dominance** — P1 advantage is intrinsic to Hex-style connection on a square lattice, not substrate-induced.

### Quantitative comparison

| Metric | Fractal | Control | Δ |
|---|---|---|---|
| Game length (moves) | 21 | 19 | +2 |
| Captures | 0 | 0 | 0 |
| Winner | P1 | P1 | same |
| P1 stones at win | 11 | 10 | +1 |
| P2 stones at win | 10 | 9 | +1 |
| "Cuts cost extra tempi" | yes (col 1 fragmented) | no | qualitative |

---

## PHASE 4 — SUBSTRATE CRITIC (mandatory)

### Critic's case

(a) **"Just 8×8 grid with extra dead cells."** Each strategic move I played on the fractal — opening on a clean row, claiming the intersection, blocking, detouring through col 1 — has a one-to-one corresponding move on the control 8×8. The set of "good moves" is a pruned subset of the rectangular set; the *concepts* are identical. The carpet introduces *no new strategic primitive* (no tunnels, no multi-component territories, no asymmetric goals beyond the standard Hex-style asymmetry which is identical across both substrates). It is "ban these specific cells" rather than "introduce a new mechanic."

(b) **"Apparent difference is artifact of denser cuts, not new strategy."** Pair C uses *connection*, not threshold, so threshold-scaling artifacts do not apply. But a parallel artifact does: the fractal increases the cost of cuts because detour corridors are themselves fragmented. This is *quantitative*, not *qualitative* — it makes blocking moves stronger uniformly for both players. It does not introduce a new tactic; it amplifies the existing tactic of cutting.

(c) **Expert-transfer test.** A Hex/Go-cross hybrid player who was strong on the rectangular control would transfer immediately to the fractal. They would already know to (i) build along outer corridors, (ii) claim intersections, (iii) detour through inner cols/rows, (iv) defend liberties. **Yes, they would transfer.** The only adjustment they'd have to make is "remember which cells are holes," which is rote memorisation, not strategic learning. This is the strongest argument that the fractal adds nothing.

### Player rebuttals

**Rebuttal from P1:** Move 5 on fractal *was* qualitatively different from move 5 on control. On the control, after I claimed (2,2), P2 had four detour corridors (col 0, col 1, col 3 going around, or even an upper bypass via row 1). On the fractal, P2 had effectively two viable corridors (col 0 going long around, or col 1 with mid-detours through the row-1 holes). The space of *responses* shrank. That is a genuine strategic difference: on the fractal, *cuts are committal* — once your opponent cuts you, your fork of options narrows more than on the control. This is a substrate-induced increase in the leverage of cuts.

**Rebuttal from P2:** The corner-capture pressure at the end of Game 1 (X group at (0,0)/(1,0) with hole at (1,1)) is a phenomenon that *cannot exist* on the control because the control has no holes adjacent to its corner. On the fractal, the corner of the board is structurally adjacent to a hole, which makes corner stones more vulnerable. I did not exploit this — but in deeper play (or with self-play training), this could be a genuine new tactical pattern: **"capture by hole-adjacency."** Both candidates have surround capture, but only on the fractal can a single stone neighbouring a hole be reduced to a single liberty by one opponent move, because holes count as non-liberties. This is a new tactical primitive.

**Critic's reply to rebuttal:** "Cuts are more committal" is *quantitative narrowing of detour set*, not new mechanics. "Capture by hole-adjacency" is real but I (the critic) note that it didn't actually fire in either of the played games — neither player attempted to exploit it. So as observed, the carpet substrate's contribution is *latent*: it *could* matter in deeper play but didn't in this evaluation.

### Substrate-novelty score (1–10)

**Score: 4/10.** Not 2–3 because the corner-vulnerability and detour-corridor-fragmentation effects are *real*, not decorative. Not 6+ because none of those effects fundamentally changed the game I played: same strategy, same opening, same response repertoire, same winner, +2 moves of game length. The closest thing to "fundamentally new" was the increased leverage of cuts, which is at best a flavour shift, not a new concept to learn from scratch.

---

## PHASE 5 — VERDICT

Team ID: team-12
Pair: C
Fractal candidate: `frac_C_fractal`
Control candidate: `frac_C_control`

### Fractal scores (1–10)

- **Strategic Depth: 5** — Connection-with-capture has real depth (intersection-claiming, cut threats, detour planning). The carpet adds modest extra depth via fragmented detours and corner vulnerability, but the central 3×3 hole is so unambiguously avoidable that play funnels into the 4 outer corridors quickly.
- **Balance: 4** — P1 won both games and was never seriously threatened. Hex-style connection without a swap-rule has a known structural P1 advantage, and we observed it. The fractal does not mitigate this; if anything, fewer corridors makes P1's tempo lead easier to convert. With a swap rule the score would rise to ~6.
- **Novelty (post-critic): 4** — Connection on a Go-capture grid is a known concept (cf. Ataxx-like and Crossings variants); the fractal carpet substrate is novel in this engine but doesn't introduce a new strategic concept.
- **Substrate-novelty: 4** — Corner-by-hole-adjacency captures and fragmented-detour corridors are real but latent — they didn't fire in observed play, and an expert-rectangular player transfers immediately.
- **Overall "Would I play this again?": 4** — I would play once more to see whether deeper play surfaces the latent fractal-tactics; I would not pick it over a hex board for serious sessions.

### Control scores (1–10)

- **Strategic Depth: 5** — Same baseline depth; same intersection / cut / detour repertoire. Slightly *more* corridor variety than the fractal but no other change.
- **Balance: 4** — Identical P1-advantage problem. Same structural flaw, same severity.
- **Novelty (post-critic): 4** — Connection-with-capture is recognisable but solid.
- **Overall "Would I play this again?": 4** — Equivalent to fractal.

### Delta (fractal − control)

- Strategic Depth: **+0** (statistically indistinguishable from observed play; the fractal's added constraints do not net out to deeper choice space — they prune options at least as much as they create them)
- Balance: **+0** (same P1 dominance on both)
- Overall: **+0**

### Critical assessment

- **"The fractal substrate genuinely added strategic depth"** — **N** (mostly no; latent yes, observed no).
- **Phenomena observed only on fractal:**
  - Higher local fragility of central-band stones (2-liberty stubs near the hole sandwich) raised the cost of opening commitments.
  - Cut leverage is amplified: cutting an opponent's chain in the central band is more punishing because the opponent's detour corridors are themselves fragmented.
  - Corner cells are adjacent to holes (e.g., (0,0) sits next to a hole at (1,1)), which reduces their effective liberty count and *could* enable "capture by hole-adjacency" tactics in deeper play. Did not fire in observed play.
  - Game length increased by ~10% (+2 moves) due to longer outer ring.
- **Phenomena observed only on control (things the substrate took away):**
  - Multiple parallel detour corridors. The control offers a richer choice of *how* to detour around a cut; the fractal funnels detours into the few remaining clean rows/cols.
  - Symmetric corner safety — corners on the control have full Manhattan-2 neighbourhoods.
  - Useful row 4 and col 4 (i.e., no "dead-zone in the middle of the board" that you have to remember to skip).
- **Recommendation for R17: drop (with a soft second-probe).**

  The fractal substrate is *not pulling its weight* on Pair C: zero captures, zero new tactics realised, identical winner, +2 moves of game length, no swap-rule mitigation of P1 advantage. The "substrate-novelty" potential (corner-by-hole, detour amplification) is real but latent and not learned by either of my opening-aligned players.

  A second-probe could be justified if it *forces* the substrate to matter — e.g., a Pair C variant where:
  - Captures count toward win (territory or threshold tiebreaker), so the corner-by-hole tactic is rewarded;
  - The opening is constrained to the central band (banned-corridor opening), so detour fragmentation matters from move 1; or
  - We add a swap rule and re-test balance, so we can distinguish "P1 wins because Hex" from "P1 wins because of substrate."

  Absent one of those, integrating the carpet on Pair C–style rules is decoration, not depth. **Drop for R17 unless paired with a rule change that makes the substrate matter; otherwise revisit only as part of a Pair C+ second-probe.**
