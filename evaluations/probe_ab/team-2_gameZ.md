# Probe A/B Eval — team-2 — Game Z

**Team ID:** team-2
**Game Label:** Z (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6, pie_rule=True
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `evaluations/probe_ab/play.py --game Z` (run `--rules` first for rules; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** All mechanics below derived from `play.py --game Z --rules` and observed engine behavior.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r. Rows sheared (row r shifts right by r). Interior degree 6; acute-corner degree 2; obtuse-corner degree 3. This is, geometrically, the standard Hex board (a rhombus of hexagons).

**Turn structure.** Alternating, 1 stone/turn, P1 first. Max_turns = 200.

**Action space.** 486 actions = 484 placement + pass(484) + pie_swap(485). Placement legal at any empty cell.

**Placement & capture.** Capture rule = **surround** (threshold field=1, vestigial for surround). After placing, any enemy *group* (connected same-owner stones) with zero empty-cell liberties is removed. Verified to fire: a lone P1 stone at 230 ringed by 6 P2 stones (`230,231,484,229,484,252,484,208,484,209,484,251`) was cleared (P1 controlled → 0). Requires a *complete* liberty-less surround — practically unreachable in sparse connection play.

**Propagation.** Influence field, radius=2, strength=1.0, decay=0.5. Each placed stone adds ±1.0·0.5^dist within hex-distance 2 (±1.0 / ±0.5 / ±0.25). Sign +1 P1 / −1 P2. Clamped [−100,100]. The field is the *win substrate*, not decoration (see Win). NOTE — the field is an **additive ledger**: removing a stone (capture) does **not** subtract its prior deposit (confirmed in Game Q; same engine). In Z this rarely matters because captures almost never occur.

**Win condition (influence-field connection).** A cell is P1-controlled if board_values > 0, P2-controlled if < 0, else contested. **P1 wins by a connected control-path r=0↔r=21 (top↔bottom); P2 by q=0↔q=21 (left↔right)** — the two opposite edge-pairs of the rhombus, exactly as in Hex. Equal → draw. Timeout (200): higher **total** controlled-cell count wins (NOT largest component); P2 +komi_p2·484 virtual cells; equal → draw. Komi_p2 = 0.0.

**Pie rule.** After P1's first stone, P2 may swap (485): inherits the stone and becomes first mover. Verified (`230,485` → the stone becomes P2's, P2 controls the full 19-cell radius-2 disk).

**Degeneracy check.**
- **Surround capture is near-vestigial.** It is mechanically live but firing it needs a full liberty-less encirclement; across all connection lines played, zero captures occurred naturally. It is dead weight on top of a connection game.
- **Threshold field=1** is vestigial for surround (liberties, not counts, decide).
- **Persistent-influence ledger** (captured deposits never subtracted) is latent but inert here because captures don't happen.
- **Geometry:** acute corner (0,0)=deg-2, obtuse corner deg-3; edge stones get clipped influence disks. The radius-2 blur means a single stone "controls" up to 19 cells, so the connection edges are easy to reach from a few stones near them.

---

## Phase 2 — Strategic Play

All moves engine-verified via `play.py --game Z`. Placement id = q + 22*r; pass=484; swap=485.

### Game 1 — P1 direct connection (uncontested)
Sequence: `10,484,76,484,142,484,208,484,274,484,340,484,406,484,472` (15 plies; P1 column q=10 at r=0,3,6,…,21; P2 passes).
Plot: With decay-0.5 radius-2 influence, stones spaced 3 rows apart leave net-positive cells between them, so the column fuses into a continuous 5-wide (+) band (q=8–12) spanning every row. Connection r=0↔r=21 completes on P1's 8th stone → **done, winner=1**, P1=110 controlled vs 0.
Reflection: A connection is *cheap* — only 8 stones bridge 22 rows because the radius-2 blur reaches between stones. The binding constraint uncontested is simply touching both target edges.

### Game 2 — P2 contests with a crossing wall (the core fight)
Sequence: `10,220,76,223,142,226,208,229,274,232,340,235,406,238,472,241` (16 plies; P1 builds the q=10 column, P2 builds a horizontal wall along r=10 at q=0,3,…,21).
Plot: After 16 plies neither side connects — a **mutual standoff**. P1's column is cut at row 10 (cell (10,10)=230 sits contested, flanked by P2); P2's wall is simultaneously cut at q=10 by P1's column. Control 93/93, **largest components 49/49** — neither edge-pair joined. The decisive point is the single contested crossing cell 230.
Continuation `…,241,230`: P1 (on move) plays the crossing cell 230 → its (+) overwhelms the contested square, the top and bottom halves fuse → **done, winner=1**, P1 comp 101 vs P2 47.
Reflection: This is the Hex connect/cut duality made explicit, blurred by influence. Whoever holds *tempo at the crossing* wins the local fight. Because cells can be neutral, **both** lines can be cut at once (a true standoff) — impossible in pure Hex.

### Game 3 — P2 as connector (seat symmetry / adversarial)
Sequence: `484,220,484,223,484,226,484,229,484,232,484,235,484,238,484,241` (16 plies; P1 passes, P2 builds horizontal r=10 line q=0,3,…,21).
Plot: P2's (−) band fuses left-to-right and touches q=0 and q=21 → **done, winner=2**, P2=110 controlled. Confirms the connecting role is fully symmetric — the only seat asymmetry is *who moves first*.

### Strategy guides
**P1 (connect top↔bottom):** Lay a roughly-vertical chain of stones spaced ~3 apart toward both edges; rely on the radius-2 blur to fuse them. Defend the chain by occupying or out-influencing any single crossing cell the opponent contests (tempo at the crossing decides). Keep one tempo in reserve for the inevitable cut fight.
**P2 (connect left↔right; pie/komi-aware):** If P1 opens centrally/strongly, **swap (485)** and take the building seat. Otherwise build the orthogonal connection while running your wall *through* P1's chain so the same stones both connect you and cut them (Hex economy). Force the standoff and aim to own the crossing cell on your move.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes but narrow: every game is "build your connection while cutting theirs through the same stones." Variety is in *route choice* on a wide board, not in different win plans.
**Counter-play.** Real and symmetric: every connection threat is countered by contesting the crossing cell; every cut is countered by re-routing or by winning tempo at the cut. Demonstrated live (Game 2 standoff then breakthrough).
**Short-term vs long-term.** Medium horizon. The 22-wide board gives many routes (more breadth than R21's 9×9), but the radius-2 blur means local fights resolve in 1–2 stones, so the tactical grain is coarse. Planning is "where to cross," not deep ladders.
**Emergent concepts observed.** Control bands (5-wide fuzzy connections), crossing/tempo battles, **mutual block → standoff → draw/timeout** (genuinely emergent and non-Hex), connection "thickness" (cuts need multiple stones, not one).
**Does hex_rhombus topology matter?** Essentially — it *is* the Hex board. The r-edge/q-edge duality and the (near-)complementarity of connect-vs-cut depend on degree-6 triangular adjacency. Flatten to a 4-neighbor square grid and the Hex duality breaks (diagonal gaps, different cut economy). Topology is structural here, not cosmetic.
**Does the propagation kernel matter?** Decisively — the field *is* the win condition (control = sign of board_values). Radius 2 / decay 0.5 sets connection "thickness": connections are 5-wide bands, so a cut needs a multi-stone wall, and a single stone reaches its edge. Change the kernel and you change the whole game.
**Capture-rule contribution.** None observed in natural play. Surround is live (verified by forced ring) but unreachable in sparse connection play — dead weight.
**First-mover advantage / seat balance.** Real first-mover edge (tempo at the crossing; P1 won both contested/uncontested building lines, P2 won only when handed free moves). Komi_p2=0 contributes nothing pre-timeout, but the **pie rule** (verified) cleanly neutralizes a strong opening. Net: balanced *with* pie.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Z is a re-skin of **Hex**. Argument:
(a) Win = connect your two opposite edges of a rhombus on a hex lattice; opponent connects the other pair. That is the definition of Hex.
(b) Capture analog: surround→Go, but it never fires — so no Go content survives; the capture rule is inert decoration.
(c) "Surround + radius-2 influence + edge-connection" is just Hex with stones replaced by fuzzy influence blobs and a never-triggered Go rule bolted on. R8 "Connection Go" is the in-corpus cousin (Go×Hex), but Z is *more* purely Hex than R8 (R8's capture mattered; here it doesn't).
(d) Substrate: hex-rhombus degree-6 lattice is the literal Hex board, distinct from R17–R21's menger/carpet/grid topologies — but distinct ≠ novel, since it is the canonical board for this exact game family.
(e) Expert transfer: a Hex player learns Z in ~5 minutes. The only irreducible new pieces are (i) "thick" connections from the influence blur (cuts need walls, not single stones) and (ii) the possibility of a **draw/timeout** via mutual blocking — both modest twists on Hex.

**Closest known-game analogue:** **Hex** (Hein/Nash) — played on its native rhombus, with influence-blurred "thick" stones and an unreachable Go capture.
**Comparison to R8 Connection Go (anchor 4.10).** Same family (connection), but R8 fused Go capture into the connection race meaningfully; Z's capture is inert, so Z is *cleaner but thinner* than R8 — comparable playability, lower mechanical richness.
**Comparison to R19/R20/R21 best.** Thinner in designed mechanics than R19's 5.0 (one live idea: blurred connection) but more *playable/decisive* than R21 3.69. The blur + draw-possibility is a genuine but small departure.

**Novelty score (post-adversary):** **3.5/10.** Above pure re-skin (2–3) because the influence-blur changes cut economy and admits draws — neither is true of Hex. Below genuinely-novel (8–9) because it is recognizably Hex on Hex's own board with a dead capture rule. Anchor: R17 3.50, R8 4.10, R19 4.8/5.0, R20 4.80, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game Label:** Z
**Rules Summary:** Hex played with fuzzy influence-blobs instead of hard stones — connect your two opposite edges of a 22×22 hex rhombus by owning a connected band of net-positive influence; an unused Go surround-capture rides along.
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=True, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** surround capture practically inert; threshold field=1 vestigial; persistent-influence ledger latent (no captures to expose it).

### Scores (1–10)
- **Strategic Depth: 5** — inherits Hex's connect/cut depth and gains route breadth from the 22-wide board, but the radius-2 blur coarsens tactics (fights resolve in 1–2 stones) and the capture adds nothing.
- **Emergent Complexity: 5** — control bands, crossing/tempo battles, and mutual-block standoffs (draws) arise beyond the written rules.
- **Balance: 6** — real first-mover edge (tempo at crossings) but the pie rule neutralizes it cleanly; symmetric seats otherwise.
- **Novelty (post-adversary): 3.5** — Hex on Hex's board; only the influence-blur "thickness" and draw-possibility are new.
- **Replayability: 5** — 22×22 yields large opening/route variety; connection games stay fresh, though the single strategic plan limits surprise.
- **Overall "Would an agent team play this again?": 4.2** — a clean, decisive, recognizably-Hex connection game; slightly above R8 (4.10) on playability, held down for derivativeness and dead capture. Anchors: R8 4.10, R19 4.8/5.0, R20 4.80, R21 3.69.

### CLOSEST KNOWN-GAME ANALOG
**Hex** (on its native rhombus), with influence-blurred stones. In-corpus cousin: R8 Connection Go — but Z is purer Hex (capture inert).

### KILLER FLAWS
- Surround capture never fires in real play — an inert rule that adds rules-complexity without gameplay.
- It is fundamentally Hex; a Hex expert needs no learning and there is one dominant strategic plan (connect-while-cutting), capping novelty/replay ceiling.

### BEST QUALITY
The influence-blur turns Hex's razor-thin connections into **"thick" connections** — cutting requires a multi-stone wall and mutual cuts can co-exist, producing genuine standoffs and the possibility of a draw, which pure Hex forbids. That is the one crown-jewel departure.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
Structural, not cosmetic: the degree-6 rhombus is the canonical Hex board and the r/q edge-pair duality (connect-vs-cut complementarity) depends on triangular adjacency. Flattening to a 4-neighbor square grid would break the duality. Per R19's menger > carpet > grid finding, this is "grid-class topology used for the one game it is perfect for," and 22×22 does open real route breadth versus R21's 9×9 — but breadth, not new depth.

### IMPROVEMENT IDEAS
**Single best change:** Make the capture rule *matter* — e.g., let capturing an enemy group flip/zero its influence deposits (lift the persistent-ledger degeneracy), so stone fights feed back into the control field. That would fuse the inert Go layer into the connection race and lift Z above pure Hex. (Falsifiable: replays should then show captures occurring and altering connection outcomes.)
Secondary:
- Reduce influence radius to 1 to sharpen connections (thinner bands → more tactical precision, closer to true Hex finesse), or conversely tune the kernel to deliberately exploit "thick connection" play.
- Add small komi or a swap-2 opening to reduce reliance on a single pie decision.

---

## Q-vs-Z Comparison

**Which game would you rather play again?** **Z.**
**By how many Overall points?** **+0.6 Overall in favour of Z** (Z 4.2 vs Q 3.6).
**Key differentiator:** Z's connect/cut duality **forces interaction** every move — you cannot ignore the opponent. Q's score race lets both players build in parallel (pure disruption demonstrably loses), so Q tends toward two solitaire cluster-builds with only local capture skirmishes. Forced, structural interaction is the single dynamic that separates them.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/probe_ab/team-2_gameZ.md`.*
