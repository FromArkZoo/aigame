# Stage 3 blind eval — team-1 — Game V

**Team ID:** team-1
**Game Label:** V (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6.
**Evaluator:** single-agent team running both player roles and Novelty Adversary sequentially.
**Helper:** `evaluations/stage3_ab/play.py --game V` (run `--rules` first; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Derived entirely from `play.py --game V --rules` plus observed engine behaviour.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r. Rows sheared right by r. Interior degree 6; acute-corner degree 2; obtuse-corner degree 3.

**Turn structure.** Alternating, exactly 1 stone/turn. Max_turns = 200 (then timeout tiebreak).

**Action space.** 486 actions = 484 placement (0..483) + pass (484) + pie_swap (485). Placement legal at any empty cell. Verified: opening legal-action count = 485 (484 placements + pass; swap becomes available only as P2's reply to P1's first stone).

**Placement & capture.** Capture rule = **influence-flip**. After each placement, every enemy stone standing on a cell where the *summed influence field* is dominated by the active player (P1 wants value > 0 at that cell, P2 < 0) is immediately converted to the active colour. Conversions **cascade**: each flip swings that cell by ±2 (−1 → +1), shifting the field and potentially tipping neighbouring enemy stones in the same turn. Engine-verified: surrounding a lone P2 stone (253) with three P1 neighbours flipped it (`252,253,254,484,275` → "X X X"); a saturating placement around a P2 pair (`229,230,252,231,208,484,209,484,251`) flipped **both** 230 and 231 in one move (P2 0 controlled, all X) — a genuine 2-stone cascade.

**Propagation.** Influence field: each placed stone adds ±strength·decay^dist to board_values within radius. P1 +1.0·0.5^dist; P2 −1.0·0.5^dist. Clamped [−100, 100]. **Radius = 2, strength = 1.0, decay = 0.5.** A lone stone therefore projects a radius-2 hex disc of 19 controlled cells (own +1.0; dist-1 +0.5; dist-2 +0.25).

**Win condition(s).** Influence-field **connection** (Hex-type, mutually exclusive seats):
- P1 wins by a hex-connected chain of P1-controlled cells (value > 0) linking r=0 to r=21 (top↔bottom).
- P2 wins by a hex-connected chain of P2-controlled cells (value < 0) linking q=0 to q=21 (left↔right).
Connection is over *control* cells, not stones — so it is "fat": one column of 6 stones spaced ~4 apart wins unopposed (verified `10,98,186,274,362,450` → winner=1). Checked for the active player after their move.
**Timeout (200 turns):** higher TOTAL controlled-cell count wins (not largest component); P2 gets komi_p2·484 virtual cells; equal = draw.

**Pie rule.** ON. After P1's first stone, P2 may swap (action 485): inherits the stone as P2's and P1 becomes the mover. Verified: `253,485` → P1=0, P2=19, player_to_move=P1.

**Komi_p2.** 0.0 (applies only at timeout tiebreak; with komi 0 the timeout can draw).

**Degeneracy check.**
- The influence field is **load-bearing** — it *is* the win condition, not decoration. Good (contrasts with prior runs where influence merely padded the observation tensor).
- The capture rule is field-coupled with the win (a flip is a +2 field swing toward your connection), so it is *not* inert — but it rarely fires under connection-optimal play because winning wants stones **spread**, while flipping wants them **clustered**. In every connection line I played, the result was identical to the surround game (game X) because no flip triggered. The mechanic is therefore mostly a local-scrum sideshow that a connection-focused player can ignore.
- Geometry: acute corners (degree 2) and obtuse corners (degree 3) leak influence off-board, so edge/corner stones control fewer cells and are weak openings — exactly the cells a pie-aware P1 wants for a swap-safe first move.

---

## Phase 2 — Strategic Play (both roles)

All moves engine-verified through `play.py --game V`. Action IDs = q + 22*r; pass=484; swap=485.

### Game 1 — as Player 1
Sequence: `10,220,98,224,186,228,274,232,362,236,450,240,230` (13 plies). **Winner = P1.**
Plot: I built a vertical corridor on column q=10 (r=0,4,8,12,16,20); P2 (driven competently) raced a mirror horizontal wall on row r=10 (q=0,4,8,12,16,20). After 6 stones each (`--control`), the bands crossed and **both connections were broken at the single contested centre cell** (r=10,q=10): P1=84/P2=84, neither connected. It was P1's move — I punched the crossing (230), the centre flipped to +, and my top↔bottom chain closed (P1=93). No captures fired.
Reflection: binding constraint = the **central crossing cell**; whoever holds the move when the walls meet wins. Placement order forced a tempo race, and as first mover I arrived at the crossing on my own turn. Win felt achievable but *only because of move parity*, not positional skill.

### Game 2 — as Player 2
Sequence: `21,243,23,247,111,251,199,255,287,259,375,263` (12 plies). **Winner = P2.**
Plot: competent P1 opened on an acute corner (21) — a pie-safe weak move, because a strong centre would be swapped. That cedes a tempo. I (P2) built a horizontal corridor on row r=11 (q=1,5,9,13,17,21); P1 raced a vertical column q=11. Because P1 had spent its first stone on a near-worthless corner, my corridor closed q=0↔q=21 first (P2=88, winner=2) before P1's column could contest the crossing.
Reflection: my win path is the *mirror* of P1's and interacts through the same crossing cell. The decisive lever was the **pie rule**: it forces P1 to open weakly (or be swapped), and a weak opening is exactly the lost tempo I converted into the crossing. Swapping a strong P1 centre (`253,485`) is the other competent P2 line — it transfers the strong stone to me at the cost of the move.

### Game 3 — Adversarial / novelty-stress
Sequence: `229,230,252,231,208,484,209,484,251` (cascade test) + `252,253,254,484,275` (single flip) + `10,230,98,484,186,484,274,484,362,484,450,484,231` (cut-routing test, → winner=1).
Plot: I tried to break the game three ways. (1) **Cascade:** one saturating placement around a P2 pair flipped *both* stones (P2→0). The advertised cascade is real but hard to chain past 2–3 because interior wall stones sit at ≈−2.0 field and a single +2 flip only lifts a neighbour by +1.0. (2) **Single flip** converts cleanly. (3) **Cut-routing:** a lone P2 stone dropped into my corridor (230) did *not* cut it — I won by routing around it with one stone (231), and the cut stone was never even captured. This is the key stress result: **the fat field connection cannot be severed by single stones**, so the capture mechanic is not needed to clear blockers — you just route. To actually cut, P2 must build a full negative wall, which is simply P2's own connection (Hex duality).

### Strategy guides
**As Player 1:** open swap-safe (weak corner/edge), then build a vertical corridor of stones spaced ~4 in r; never over-cluster (wastes connection reach). Win the **central crossing on tempo**; flip enemy cutters only if it also tightens your corridor.
**As Player 2:** treat the **pie swap as your first real decision** — swap any strong central P1 opening. Otherwise exploit P1's swap-safe weak move as a free tempo and race your horizontal corridor to the crossing. Block-by-building: every wall stone that cuts P1 advances your own left↔right path.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, but they are mirror-symmetric: P1 = vertical corridor, P2 = horizontal corridor, both resolved at the shared crossing. P2 additionally owns the pie-swap decision. Verified both seats win (Games 1 & 2).
**Counter-play.** Real and tight — by Hex duality, blocking the opponent *is* building your own connection. The single contested crossing cell is the whole game in symmetric lines.
**Short-term vs long-term.** Tactically thin (single-stone cuts fail; play is corridor-laying), but the 22×22 board nominally supports a long horizon. In practice play concentrates into one ~3-wide corridor and the rest of the 484 cells are irrelevant filler — the effective board is much smaller than its size.
**Emergent concepts observed.** Fat-corridor routing (route around cuts), the crossing tempo race, wall-building duality, and (V-specific) cascade flips. Influence "wells" overlap to keep corridors positive.
**Does hex_rhombus topology matter?** Yes structurally — it is the Hex substrate (opposite-edge connection on a rhombus with degree-6 adjacency and no draws-by-crossing). On a square 4-grid the connection duality weakens (diagonal crossings/draw structure differ). But the topology is doing *Hex's* job, not a novel one.
**Does the propagation kernel matter?** Materially — radius 2 / decay 0.5 is what makes connection "fat" and uncuttable by single stones, and it is the literal win substrate. Not decorative. A radius-0 kernel would collapse this to ordinary stone-Hex.
**Capture-rule contribution.** Flips fire only in dense local scrums (verified) and were **never** decisive in any connection line — every connection game I played was identical to game X. The flip is the more-integrated of the two capture options (field-based, like the win), but still a sideshow.
**First-mover advantage / seat balance.** Real first-mover edge: in symmetric races P1 reaches the crossing on its own turn and wins (Game 1); hand P2 the tempo and P2 wins (`…,484,230` → winner=2). The **pie rule neutralises this** by forcing P1 to open weakly. Balance is genuine but knife-edge and entirely pie-dependent.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of **Hex**. Argument:
(a) Win = connect your two opposite edges of a rhombus on a degree-6 hex lattice with pie rule ON. That is the *definition* of Hex. The "influence-field connection" only fattens the path; it does not change the goal or the topology.
(b) Capture analog: field-dominance flip ≈ **Othello/Reversi** conversion (enemy pieces flip when you dominate their square) — but it is bolted onto a connection game and rarely fires.
(c) "influence-flip + influence propagation + edge-connection" — the connection half is published (Hex, 1942); the Reversi-flip half is published; the *combination on a fuzzy field* is the only un-catalogued piece, and it is largely inert in optimal play. R8 "Connection Go" already explored Go×Hex hybrids; this is closer to pure Hex + a vestigial flip.
(d) Substrate: a degree-6 hex rhombus is the canonical Hex board; nothing exotic versus R17–R21's menger/carpet/grid — and notably *less* novel than those, since it is the textbook connection-game substrate.
(e) Expert transfer: a Hex player learns the core in ~3 minutes (open swap-safe, race the crossing). The only new idea to absorb is "connections are fat, and you can occasionally flip a clustered enemy stone." Irreducible novel piece: **the fuzzy radius-2 connection that makes single-stone cuts fail** — modest, and arguably a downgrade in tactical sharpness.

**Closest known-game analogue:** Hex (with a Reversi-style flip overlay and a 22×22 board).
**Comparison to R8 Connection Go (replay anchor 4.10).** Same family, thinner novelty. R8 was a Go×Hex hybrid praised as more original; this leans almost entirely on the Hex skeleton with a capture rule that doesn't drive play. Comparable playability, slightly less originality.
**Comparison to R19/R20/R21 best.** Thinner than R19's 4.8/5.0 (which earned ceiling-level depth from richer topology). Roughly on par with R20's mid-pack and a touch above R21 3.69 on raw playability, because the Hex core is genuinely sound — but the novelty wrapper is slight.

**Novelty score (post-adversary):** **4/10.** Above re-skin floor (2–3) because the fuzzy-field connection + cascade flip is a real, un-catalogued combination that changes tactics (uncuttable thin lines, occasional conversions); below genuinely-novel (8–9) because the strategic spine is textbook Hex and the distinguishing capture rule is mostly inert. Anchor: R8 4.10, R17 3.50, R19 top 4.8/5.0, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game Label:** V
**Rules Summary:** Hex on a 22×22 hex rhombus where "connection" is over influence-controlled cells (radius-2 field) rather than solid stones, with pie rule and a Reversi-style cascade flip that converts clustered enemy stones — though the flip rarely affects connection-optimal play.
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=ON, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only; plus pass and pie-swap).
**Soft violations flagged:** capture mechanic largely redundant with the connection strategy (fires only in clustered scrums, never decisive in my connection lines); timeout area-count mode effectively dormant since connection resolves long before turn 200; komi 0 permits draws at timeout.

### Per-role sub-scores (1–10)

**As Player 1:**
- Strategic Depth: 5 — real Hex-style connect/block duality and a crossing tempo race, but single-stone cuts fail so tactics are blunt; mostly corridor-laying.
- Emergent Complexity: 4 — fat-corridor routing and occasional flips emerge, but the dominant pattern is one ~3-wide lane.
- Replayability: 4 — many opening cells, yet play converges to the same crossing race once understood.

**As Player 2:**
- Strategic Depth: 5 — symmetric to P1 plus a genuine extra decision (the pie swap), which is the most interesting single choice in the game.
- Emergent Complexity: 4 — same emergent set; the swap adds one layer of opening theory.
- Replayability: 4 — swap-vs-build branching gives marginally more opening variety than P1.

### Role-averaged scores (1–10)

- **Strategic Depth: 5.0** — sound borrowed-from-Hex depth, dulled by uncuttable fat connections.
- **Emergent Complexity: 4.0** — cascade flips + routing are real but peripheral to the corridor race.
- **Balance: 3** — structurally symmetric seats; raw P1 tempo edge is neutralised by the pie rule (my games split 1–1).
- **Novelty (post-adversary): 4.0** — see Phase 4; fuzzy-field Hex + mostly-inert flip.
- **Replayability: 4.0** — large board but the effective game is one corridor; opening variety modest.
- **Overall "Would an agent team play this again?": 4.0** — a competent, genuinely playable connection game whose depth is real but borrowed from Hex, with a distinctive-but-peripheral flip. Sits just below R8's 4.10; anchored down against drift.

### Fairness perception (mandatory)

**Fairness perception: 3 — symmetric seats with the pie rule neutralising P1's real first-mover/crossing-tempo edge; my P1-role and P2-role games each won for the mover who earned the crossing tempo (1–1 split).**

### CLOSEST KNOWN-GAME ANALOG
Hex (Piet Hein / Nash) — opposite-edge connection on a hex rhombus with pie rule — overlaid with a Reversi-style field-flip. In-corpus: closest to R8 Connection Go, but more purely Hex than R8's Go hybrid.

### KILLER FLAWS
- The capture rule (the game's nominal signature) is **strategically inert** under connection-optimal play: every connection line I played was byte-identical to the surround variant, because winning wants spread stones while flipping wants clustered ones.
- **Fat connections blunt tactics**: single-stone cuts cannot sever a corridor (you just route around), so the rich ladder/cut tactics that make thin-stone connection games deep are largely absent; the game reduces to a tempo race for one crossing cell.

### BEST QUALITY
The cascade flip: a single placement converting an entire clustered enemy group via field dominance is a satisfying, legible Othello-on-a-field moment — and, unlike game X's surround, it is conceptually coherent with the field-control win (both are field-based). It just doesn't get to matter often.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
The degree-6 rhombus is doing Hex's job — opposite-edge connection with crossing-exclusivity and no draws-by-crossing — so the topology genuinely shapes strategy, but as *Hex's* known contribution, not a novel one. Against R19's menger > carpet > grid finding, this is the plainest connection substrate, not a depth-adding exotic topology. The 22×22 size adds nominal horizon but in practice the effective board is the one ~3-wide corridor, so the extra size mostly adds irrelevant filler rather than strategic depth.

### IMPROVEMENT IDEAS
**Single best change:** shrink the influence radius to 1 (or raise decay so dist-2 ≈ 0). That makes connections thin enough that single-stone cuts bite, restoring real cut/ladder tactics and giving the flip mechanic something decisive to do — a falsifiable change that should sharply raise Strategic Depth and make captures matter.
Secondary:
- Add a small positive komi_p2 and/or a turn cost so the timeout area-game becomes a live secondary objective rather than dormant.
- Make flips require strictly-dominant field (e.g. > +0.5) to enable deeper, more controllable cascades and reward setup play.

---

## Cross-game comparison (fill after all assigned games are done)

**Ranking of your assigned games by Overall score:** V=4.0, X=3.8 (D not assigned to this team).
**Which game would you most want to play again?** V.
**By how many Overall points above the next-ranked game?** +0.2 Overall.
**Key differentiator:** the capture rule. V's influence-flip is field-based — coherent with the field-control win, fires on local dominance, and cascades — whereas X's Go-surround requires full hex enclosure (6 liberties), is mechanically dissonant with a field-connection win, and almost never fires in spread connection play. Both games share an identical Hex spine, so this is the only thing separating them, and V integrates it better.

---

*Output saved to `evaluations/stage3_ab/team-1_gameV.md`.*
