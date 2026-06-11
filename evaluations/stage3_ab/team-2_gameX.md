# Stage 3 blind eval — team-2 — Game X

**Team ID:** team-2
**Game Label:** X (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6.
**Evaluator:** single-agent team running both player roles and Novelty Adversary sequentially.
**Helper:** `evaluations/stage3_ab/play.py --game X` (run `--rules` first; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Derived entirely from `play.py --game X --rules` and observed engine behaviour.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r. Rows sheared (row r shifts right by r). Neighbour set is the standard axial hex: {(±1,0),(0,±1),(+1,−1),(−1,+1)}. Interior degree 6; the acute corner (0,0) is degree 2 (verified — captured with 2 stones); obtuse corners degree 3.

**Turn structure.** Alternating, 1 stone/turn. Max_turns = 200 (timeout).

**Action space.** 486 actions = 484 placement (0..483) + 1 pass (484) + 1 pie_swap (485). Placement legal at any empty cell.

**Placement & capture.** Capture rule = **surround (Go-style)**. After a placement, any enemy GROUP (connected same-owner stones) with zero empty-cell liberties is removed and its influence vanishes. Verified: a P2 stone ringed by 6 P1 stones was cleared (P2 controlled-count → 0). On the degree-2 acute corner, 2 stones suffice. The "Threshold field=1" is explicitly vestigial for surround.

**Propagation.** Influence field radius=2, strength=1.0, decay=0.5. A placed stone adds ±1.0·0.5^dist to board_values within hex-distance 2 (P1 +, P2 −). Clamped [−100,100]. A lone interior stone controls a 19-cell hexagon (1 + 6 + 12); the footprint's top tip shifts +q, bottom tip −q (sheared). Opposing stones placed adjacently neutralise their overlap to "contested."

**Win condition(s).** Influence-field connection. A cell is P1-controlled if board_values > 0, P2 if < 0, else contested. **P1 connects r=0↔r=21; P2 connects q=0↔q=21.** Win checked after each placement. CRITICAL observed property: the win-connectivity graph does NOT include the pure-horizontal step (q±1, r). A fully P2-controlled flat row (verified 22/22 negative cells at r=8, with explicit edge stones at q=0 and q=21) did NOT register a P2 win, whereas an unopposed P2 band (thick) and any P1 vertical thread win normally. P1's goal (vary r) uses the included (0,±1)+diagonal steps; P2's goal (vary q) can only advance via the (±1,−1)/(−1,+1) diagonals, so P2 needs a ≥2-row-thick band to staircase across. Both sides' goals are NOT interchangeable under this graph.

**Pie rule.** ON. After P1's first stone, P2 may swap (action 485) → inherits the stone as its own; move passes to P1. Verified.

**Komi_p2.** 0.0 (applies only at timeout tiebreak).

**Degeneracy check.**
- **Display/win mismatch (soft violation):** the `--control` map prints "−" for every board_values<0 cell, and the status line hint says "P2 connects q=0↔q=21," yet a visually-complete negative row is NOT a win. The rendered feedback misrepresents the actual win-connectivity graph; a player reading the control map would believe they had connected when they had not. This genuinely misled me mid-evaluation.
- **Vestigial threshold field** (=1) for the surround capture path.
- **Hex-rhombus corner irregularity:** degree-2 acute corner makes corner captures cheap (2 stones) vs 6 interior; situational only.
- No non-termination: surround captures resolve instantly; timeout count rule guarantees an end.

---

## Phase 2 — Strategic Play (both roles)

All moves engine-verified through `play.py --game X`. Action IDs = q + 22*r; pass=484; swap=485.

### Game 1 — as Player 1 (P1 WINS)
Sequence: `184,181,250,187,118,178,316,190,52,196,382,404,383,405,426,449,448,471,470` (engine ended at ply 17, winner=1).
Plot: P1 opened the **central crossing** (8,8)=184; this single move makes P1's vertical band automatically cut P2's horizontal row (Hex duality) — P2's row split to a largest component of 29 while P1 led 76. P1 then ran the q=8 column up and down (118,52 top; 316 lower). P2 contested centrally (181,187,178,190,196) but each blocking stone sat in the middle and could not reach an edge. For the bottom edge P1 used a **doubled descent** (382+383, 448+449, 470) so P2's standard 2-stone bridge-cut (404,405,426) couldn't sever a 4–5-wide band. P1 connected r=0↔r=21 (component 98... 91 at the winning ply).
Reflection: binding constraint = **own the crossing first**; with tempo P1 gets it. Placement order forces P1 to secure the centre, then thicken any edge bridge P2 attacks. The win condition felt very achievable as P1 — the easier connection axis plus first move is a large edge.

### Game 2 — as Player 2 (illustrates the P2 handicap)
Sequence: `184,485,52,178,140,196,228,181,316,187,404,190,446,193` (P2 swapped, then built a full-width r=8 row; result winner=None — P2 could not connect).
Plot: P1 opened centre; as P2 I took the strong **pie swap** (485) to claim the centre stone and the initiative. I then built a spacing-3 row across r=8 (q=2,5,8,11,14,17,20) — visually a complete left-to-right wall (control map showed r=8 fully "−", 22/22). But P1's q=8 column pinched the band to a single flat row at the q=7–8 latitude, and because the win-graph excludes horizontal steps, the flat row does NOT conduct. Adding explicit edge cells (q=0, q=21) still produced NO win. P2's "finished" wall was not a connection.
Reflection: my win path and P1's are NOT symmetric. Swapping fixed tempo but did nothing for P2's structurally harder direction — P2 must keep a ≥2-row-thick band everywhere, and a single vertical pinch kills it. As P2 this felt unfair: the feedback said I controlled q=0↔q=21, the engine disagreed.

### Game 3 — Adversarial / novelty-stress
Sequence (flank/running-wall): `52,292,140,294,204,296,208,298,289,290,377,288,444` (close fight: P1 47 vs P2 64). Plus corner-capture probe `1,0,22` (P2 corner stone removed) and the 6-stone interior surround `231,230,229,484,252,484,208,484,209,484,251` (P2 centre stone cleared).
Plot: I tried to break the connection race by walling. P1 built a top anchor then descended a flank; P2 answered by extending a central wall that crept to the LEFT edge (q0–14) but never reached the right — leaving an open right flank, a classic "floating wall is flankable" Hex motif. The position stayed genuinely close (P2 actually ahead on count, 64 vs 47), confirming this is NOT a trivial rush. Captures only fired cheaply at the degree-2 corner; the interior surround cost 6 P1 moves for 1 stone — far too slow to matter in a connection race.

### Strategy guides
**As Player 1:** Take the centre crossing move 1 (or a "fair" near-centre cell if you fear a swap). Build a vertical spine; thicken (double) any bridge an edge of your column where P2 commits a 2-stone cut. Your vertical conducts through horizontal squeezes, so you rarely need captures — ignore them. Win the tempo race; you have the easier axis.
**As Player 2:** Decline the swap unless P1's opening is overwhelming (swap doesn't cure your harder direction). Build a 2-row-thick diagonal staircase, never a 1-row line. Anchor every wall to BOTH the q=0 and q=21 edges or it gets flanked. Use blocking stones that double as your own connection. Realistically you are playing for P1 to misplay or for a timeout count lead.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, but asymmetric. P1: spine-build + double-bridge defence. P2: thick-staircase + flank-anchored walls. Each role has a real playbook; P1's is meaningfully stronger.
**Counter-play.** Real and Hex-like: every blocking stone doubles as the blocker's own connection (duality). Cuts cost ~2 stones at thin bridges; defence costs ~1 doubling stone; flanks beat floating walls.
**Short-term vs long-term.** Genuine medium-horizon planning — where to cross, robust-vs-economical spacing, which flank to commit. The 22×22 board supports much longer horizons than R21's 9×9; games ran 15–25+ plies with live tension.
**Emergent concepts observed.** Influence-blob "fat" connections; contested no-man's-land on overlap; Hex bridges & 2-stone cuts; force-concentration walls; floating-wall flanking; tempo as the deciding resource.
**Does hex_rhombus topology matter?** Partly. Degree-6 adjacency sets the blob shape and the diagonal staircase requirement. But the dynamics would survive on other connection lattices; the asymmetric win-graph (not the hex-ness per se) is what shapes strategy. A square grid would lose the diagonal-staircase flavour but keep the race.
**Does the propagation kernel matter?** Materially yes — radius-2/decay-0.5 is what makes each stone a 19-cell controllable blob and defines connection thickness. It enters win logic directly (control = sign of the field). It is not mere decoration.
**Capture-rule contribution.** Minimal in practice. Surround capture fired only when I deliberately spent 6 stones (interior) or 2 (corner). In real connection play it almost never pays — rerouting is cheaper than capturing. Effectively vestigial.
**First-mover advantage / seat balance.** Large. Whoever owns the central crossing wins the race, and P1 moves first. The pie rule corrects the TEMPO half but NOT the directional half (P2 keeps the harder horizontal axis after swapping). Residual structural advantage to P1.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of **Hex** (with a Go capture bolted on and a fuzzy influence "ink"). Argument:
(a) Connect-opposite-edges win = Hex's exact victory condition; P1 top-bottom, P2 left-right is Hex's two-edge duality.
(b) The capture analog is Go (surround → liberties → removal), but it is near-inert here, so it adds little; the influence field just makes Hex stones paint fat strokes instead of single cells.
(c) "Surround capture + radius-2 influence propagation + edge-to-edge connection" is essentially Hex-with-thick-strokes; nothing published combines them, but each piece is individually old (Hex 1942; Go capture; influence/territory fields as in R8 Connection Go and the R17–R21 corpus).
(d) Substrate: a 22×22 hex-rhombus degree-6 lattice — larger and flatter than R17–R21's menger/carpet/grid substrates, but a plain hex board, not an exotic topology.
(e) Expert transfer: a Hex player learns the core in ~10 min; the only new pieces are (i) connections are influence-blobs not stones, and (ii) the win-graph excludes horizontal steps (an asymmetry a Hex player would find surprising and arguably broken).

**Closest known-game analogue:** Hex (on a rhombus) with influence-blob connections — "fat-stroke Hex."
**Comparison to R8 Connection Go (replay anchor 4.10).** Same connection family. R8 fused Go capture into a connection goal more load-bearingly; here the capture is more vestigial, but the bigger board and cleaner Hex-race give comparable depth. Roughly peer to R8, a touch below on capture integration.
**Comparison to R19/R20/R21 best.** Thinner than R19's 5.0 (no exotic topology payoff) and R20's 4.80; richer than R21's 3.69 thanks to the larger board and a clearer strategic spine. The directional-asymmetry flaw caps it.

**Novelty score (post-adversary):** **3.5**/10. Above bare re-skin (2–3) because the influence-blob connection medium and the (unusual, if likely-unintended) horizontal-exclusion asymmetry are not in plain Hex; below genuinely-novel (8–9) because the skeleton is unmistakably Hex and the capture is inert. Anchors: R17 3.50, R8 4.10, R19 4.8/5.0, R20 4.80, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game Label:** X
**Rules Summary:** Fat-stroke Hex on a 22×22 hex rhombus: place stones that paint radius-2 influence blobs, and win by linking your two edges through controlled (sign-of-field) cells; Go-style surround capture exists but rarely pays.
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=ON, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only; pass + pie-swap available)
**Soft violations flagged:** control-map/win-detection mismatch (a full-looking controlled row is not a win); vestigial threshold field; capture effectively inert in connection play.

### Per-role sub-scores (1–10)

**As Player 1:**
- Strategic Depth: 5 — own-the-crossing, spine routing, robust-vs-economical spacing, flank choice.
- Emergent Complexity: 4 — Hex bridges/cuts, force-concentration walls, blob neutralisation emerge unbidden.
- Replayability: 4 — large board gives opening variety; converges toward "centre then vertical" once solved.

**As Player 2:**
- Strategic Depth: 4 — real defensive/disruptive play, but the harder axis narrows options to staircases and flank-anchored walls.
- Emergent Complexity: 4 — same emergent motifs, experienced from the defending side.
- Replayability: 3 — directional handicap + the misleading win feedback dampen the seat; swap doesn't reopen plans.

### Role-averaged scores (1–10)

- **Strategic Depth: 4.5** — genuine medium-horizon connection-race decisions on both sides.
- **Emergent Complexity: 4.0** — bridges, cuts, walls, flanking arise from simple rules.
- **Balance: 3** — P1-favored: first-mover (pie-corrected) PLUS a structural directional advantage (pie-uncorrected).
- **Novelty (post-adversary): 3.5** — see Phase 4; fat-stroke Hex with an inert capture.
- **Replayability: 3.5** — solid but trends toward a known central spine.
- **Overall "Would an agent team play this again?": 4.0** — a real, playable connection game, peer to R8 (4.10), above R21 (3.69); held down by the P1 lean, the win-feedback wart, and a vestigial capture. Anchors: R8 4.10, R19 4.375/4.8/5.0, R20 3.73/4.80, R21 3.69.

### Fairness perception (mandatory)

**Fairness perception: 2 — P1-favored: a fully P2-controlled row (22/22 cells) failed to win while P1's column won through an equivalent horizontal squeeze, and the pie swap fixes only tempo, not P2's harder connection axis.**

### CLOSEST KNOWN-GAME ANALOG
Inside the corpus: R8 Connection Go (connection win + capture + influence). In the literature: Hex (rhombus, edge-to-edge connection) rendered with fat influence strokes.

### KILLER FLAWS
- Structural P1 advantage baked into the win-connectivity graph (horizontal step excluded), un-fixed by the pie rule.
- Control-map/win-detection mismatch: the rendered feedback tells a player they've connected when the engine says they haven't.

### BEST QUALITY
The influence-blob connection: stones paint a 19-cell controllable region, so connection is a contest over thick, neutralisable bands — and a vertical spine that naturally cuts the opponent's row. That duality is the crown jewel; it's just Hex's, lightly reskinned.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
The degree-6 lattice sets the blob hexagon and forces P2's diagonal staircase, so topology shapes tactics — but it could flatten to a square grid with only modest loss (you'd lose the staircase flavour, keep the race). It does not deliver the menger>carpet>grid topology dividend R19 found; the 22×22 size DOES open longer planning horizons than R21's 9×9, which is the main lift over the recent corpus.

### IMPROVEMENT IDEAS
**Single best change:** make the win-connectivity graph the FULL hex 6-neighbourhood (include the horizontal step) so the two seats are genuinely symmetric, then rely on the pie rule alone for balance. This directly removes the P1 structural edge and the control-map lie.
Secondary:
- Make capture matter: shrink the board or raise influence strength so surround capture is reachable in tempo, or drop it entirely (it currently decorates).
- Render the control map using the actual win-graph (or mark "this region does not yet connect") to kill the feedback mismatch.

---

## Cross-game comparison (fill after all assigned games are done)

See the full cross-game section in `team-2_gameV.md` (filed last). Summary: **V (4.2) > X (4.0)**; the differentiator is V's live influence-flip capture vs X's inert surround capture.

---

*Output saved to `evaluations/stage3_ab/team-2_gameX.md`.*
