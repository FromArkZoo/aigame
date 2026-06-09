# Probe A/B Eval — team-1 — Game Z

**Team ID:** team-1
**Game Label:** Z (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6, pie_rule=True
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `evaluations/probe_ab/play.py --game Z` (run `--rules` first for rules; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Derived entirely from `play.py --game Z --rules` and observed engine behaviour.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r. Neighbours of (q,r): (q±1,r), (q,r±1), (q+1,r−1), (q−1,r+1). Interior degree 6; acute corners degree 2; obtuse corners degree 3. Board displays as 22 sheared rows.

**Turn structure.** Alternating, 1 stone/turn, P1 first. Max_turns = 200.

**Action space.** 486 actions = 484 placement + 1 pass + 1 pie_swap. No move actions. Placement legal at any empty cell. pass=484, swap=485.

**Placement & capture.** Capture rule = **surround** (Go-style; threshold field=1 is vestigial). After a placement, any enemy *group* (connected same-owner stones) with **zero empty-cell liberties** is removed. Verified at an acute corner (degree 2): P2 stone at 0 removed once P1 occupied both its liberties (1 and 22). On the degree-6 interior, surrounding a single stone needs all 6 neighbours, so capture is **expensive** and fires mostly at edges/corners or against shape-less groups.

**Propagation.** Hex influence field, radius=2, strength=1.0, decay=0.5. Each placed stone adds ±1.0·0.5^dist within radius 2 (self +1.0, dist-1 +0.5, dist-2 +0.25). A lone stone controls a radius-2 disk of **19 cells**. Sign +1 P1 / −1 P2. Clamped [−100,100]. **Verified: the field IS reversed on capture** — placing P2 at 0 then capturing it returns P1's controlled count to the exact no-P2 baseline (P1=10 either way). So removing an enemy stone genuinely clears its influence (contrast: this is the opposite of the other game in this pair, where capture leaves a ghost).

**Win condition.** Influence-field **connection**: a player wins when their *controlled* cells form a connected path across the board. A cell is controlled by P1 if `board_values` > 0, by P2 if < 0, else contested (·). **P1 must connect r=0 ↔ r=21** (top-to-bottom in the sheared display); **P2 must connect q=0 ↔ q=21** (left-to-right). Komi_p2 = 0.0. Equal → draw. Timeout (200 turns) → **higher TOTAL controlled-cell count** (not largest component); P2 gains komi_p2·484 virtual cells (=0 here); equal → draw.

**Pie rule.** After P1's first stone, P2 may swap (action 485): inherits the stone (now P2-controlled — verified: P2=19 controlled after swapping a central P1 stone). Standard Hex-style first-mover correction.

**Degeneracy check.**
- **Three-state control reintroduces draws.** Unlike true Hex (someone must connect), opposing stones produce a *contested* (·) seam where positive and negative influence cancel (verified: P1 253 vs adjacent P2 254 → clean contested boundary). A wall of contested cells can block BOTH players, so games can fail to connect and fall to the timeout area-count tiebreak — more Go-territory-like than Hex.
- **Capture is largely vestigial in open play.** Degree-6 surround needs ~6 stones per lone capture; in natural play captures fire only at edges/corners or to clear an isolated blocker. Its real strategic role is the rare-but-meaningful "remove an enemy stone whose negative field is cutting my connection," made worthwhile by the verified field-reversal.
- **Influence smearing widens connections.** Radius-2 disks make a board-spanning connection ~7 stones (vs ~22 in pure Hex) and fat (~3–5 cells wide), so play is faster and fuzzier than Hex; precise single-cell bridges/ladders are blunted.

---

## Phase 2 — Strategic Play

All moves engine-verified through `play.py --game Z`. Action IDs = q + 22*r; pass=484; pie_swap=485. `--control` used throughout to read the sign map.

### Game 1 — P1 unopposed vertical connection
Sequence: `33,484,99,484,165,484,231,484,297,484,363,484,429,484` (P1 column q=11 at r=1,4,7,10,13,16,19; P2 passes).
Plot: Stones spaced 3 rows apart overlap their radius-2 disks into one continuous `+` band; the r=2 disk touches r=0 and the r=19 disk touches r=21. **P1 connects r=0↔r=21 and wins at step 13** (7 stones, P1=106 controlled cells).
Reflection: Binding constraint is *vertical continuity of the controlled band* — spacing ≤3 keeps disks overlapping. Unopposed connection is cheap; the game is entirely about whether the opponent can sever or out-race.

### Game 2 — P2 contest by perpendicular cut
Sequence: `33,274,99,275,165,273,231,276,297,277,363,272,429`.
Plot: P1 builds the same column; P2 lays a **horizontal wall** at r≈10–14 across the band. Final control map shows a top `+` band (rows 0–9), a `−` wall (rows 10–14), and a bottom `+` band (rows 15–21): **P1 is cut and does NOT connect** (done=False; P1=82 controlled but largest component only 50 — fragmented). P2's wall spans cols ~6–14, not yet reaching q=0/q=21, so P2 hasn't won either. **Genuine Hex-like cut/duality confirmed.**
Reflection: The connection objective FORCES contact: P1's vertical path and P2's horizontal wall must intersect. This is the interaction Q lacks. The fight is "extend the wall to the edges (P2 wins) vs route the band around the wall (P1 wins)."

### Game 3 — Adversarial / symmetry + capture + seat swap
(a) Symmetric P2 win: `484,244,484,247,484,250,484,253,484,256,484,259,484,262` — P2's horizontal chain connects q=0↔q=21 (P2=106) and **wins**; the objective is symmetric between seats.
(b) Capture stress: `1,0,22` — corner surround removes P2's stone (Go liberties), and the field reverts to baseline, proving capture is a real (if costly) blocker-removal tool.
(c) Seat swap: `253,485` — P1 opens centre, P2 swaps and inherits the 19-cell central control. Confirms pie corrects the Hex first-mover advantage.

### Strategy guides
**P1 (connection / offence):** Open off-centre to avoid the swap; then build a vertical chain (spacing ≤3) with lateral slack so you can detour around walls. Treat P2's wall as a Hex block — go around its short end, and use a surround-capture only to delete a single pivotal blocking stone.
**P2 (defence + contest; pie-aware):** Swap a strong central opening. Otherwise build a horizontal wall that simultaneously cuts P1 and is your own q=0↔q=21 connection (Hex duality — the same stones do both). Aim the wall's ends at the side edges; contest, don't try to capture (too costly) unless a corner/edge stone is cheaply takeable.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Yes** — a connection game admits build-direct, block-and-redirect, double-threat (force the opponent to choose which cut to answer), and edge/corner capture to clear blockers. Verified that both a direct connect and a perpendicular cut are realizable.
**Counter-play.** **Real.** Every connecting attempt has a cutting answer and vice-versa (Hex duality); the contested-seam mechanic adds a third option (neutralise without committing to your own path).
**Short-term vs long-term.** Meaningfully longer horizon than Q. You must plan a board-spanning route and anticipate cuts several plies ahead; the 22×22 board with radius-2 disks gives ~7-stone connections but with genuine spatial branching at each junction. Deeper than R21's 9×9 in raw branching, though influence smearing softens precision.
**Emergent concepts observed.** Connection races, cutting walls, going-around, fragmentation (largest-component < total), contested seams as cheap blockers, capture-as-blocker-removal, Hex-style edge templates (fuzzed by radius-2).
**Does hex_rhombus topology matter?** **Yes** — connection games are sensitive to adjacency. Hex (degree-6, no 4-way mutual cuts) is the natural home of connection games precisely because it suppresses the draws that a square grid's diagonal ambiguity creates. Flattening to a square grid would change cut/connect topology materially. (Note: the three-state control here still reintroduces some draws despite hex.)
**Does the propagation kernel matter?** **Centrally** — radius-2/decay-0.5 IS the connection medium (control sign defines the path). Larger radius → fatter, faster connections and easier neutralisation; it is fully load-bearing, not decorative.
**Capture-rule contribution.** Captures fired only when forced (corner test); in open play they are rare due to degree-6 surround cost. Their meaningful contribution is the *option* to delete a single critical blocker and reclaim its territory (field reverses) — a real but seldom-used lever.
**First-mover advantage / seat balance.** Hex-type first-player advantage (the connecting player who moves first is favoured); komi_p2=0.0, so pie is the balancer and it works (swap transfers the strong opening). With correct pie play, balanced.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Z is a re-skin of **Hex with Go capture and influence-fuzzed connections**. Argument:
(a) Connection win (top↔bottom vs left↔right, the two seats racing perpendicular connections) is **Hex, exactly** — the canonical connection game — merely routed through influence-control cells instead of stone chains.
(b) Capture analog: **surround → Go** (liberties, group capture), verbatim.
(c) "surround + radius-2 influence + perpendicular connection": this is the **Go × Hex hybrid**, i.e. the *Connection Go* family the corpus already found (R8/R9 — a documented local optimum). Z lands squarely in that attractor.
(d) Substrate: hex-rhombus degree-6 lattice is the *correct* and expected substrate for a connection game (Hex is played on a rhombus of hexes); it is not a novel topology so much as the canonical one. No menger/carpet exotic structure.
(e) Expert transfer: a Hex+Go player grasps Z in ~10 minutes — "it's fuzzy Hex where you can also surround-capture and where seams can deadlock to area-count." The irreducible novel piece is **influence-field control as the connection medium** (fat fuzzy paths + a contested third state that admits draws/timeouts), plus capture-as-blocker-removal.

**Closest known-game analogue:** **Hex** (with a Go capture rule and influence-disk "control" replacing stone-adjacency) — i.e. a Connection-Go variant.
**Comparison to R8 Connection Go (replay anchor 4.10).** **Same family.** Z is essentially Connection Go on the larger 22×22 hex board with an influence-control twist. Comparable depth/playability to R8; the influence-disk control medium is a modest fresh element, the larger board a modest plus, but it does not escape R8's local optimum.
**Comparison to R19/R20/R21 best.** Richer than R21 (3.69) and around R8 (4.10); below R19's 5.0 and R20's 4.80 best. What's better than R21: a forcing connection objective that uses the whole board. What's worse than the top: it rediscovers a known family and the influence fuzz/contested-seam dynamic blunts precision and admits anticlimactic timeout finishes.

**Novelty score (post-adversary):** **4.0/10.** Above re-skin (2–3) because influence-control connection + Go capture + the contested third state combine into something not identical to any one published game; below novel (8–9) because it is recognizably the Connection-Go (Go×Hex) family the corpus already mapped. Anchor: R8 4.10, R17 3.50, R19 top 5.0, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game Label:** Z
**Rules Summary:** A fuzzy-Hex connection game on a 22×22 hex board: each stone projects a radius-2 influence disk, you win by linking your two opposite edges with a connected band of cells you control by influence sign, and you may surround-capture enemy stones (Go-style) to clear blockers; pie rule balances the first move.
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=True, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** vestigial capture-threshold field (=1, unused by surround); three-state control admits non-connection draws/timeouts (Go-territory fallback rather than a true Hex no-draw guarantee).

### Scores (1–10)
- **Strategic Depth: 4.0** — real connect/cut duality, double-threats, route-around-the-wall, capture-as-blocker-removal; forcing objective gives genuine multi-ply planning, though radius-2 fuzz softens precision.
- **Emergent Complexity: 4.0** — walls, fragmentation, contested seams, edge templates emerge from the influence + connection interplay, none written explicitly in the rules.
- **Balance: 4.5** — Hex-type first-mover edge cleanly corrected by pie (verified swap); both seats symmetric.
- **Novelty (post-adversary): 4.0** — see Phase 4; Connection-Go family with an influence-control twist and a draw-admitting third state.
- **Replayability: 4.5** — connection games reward repeated play (open routing space, many cut/connect lines); the main drag is occasional timeout/area-count anticlimax.
- **Overall "Would an agent team play this again?": 4.1** — a competent fuzzy-Hex/Connection-Go with forced board-spanning interaction; around R8 4.10, above R21 3.69, below R19/R20 best.

### CLOSEST KNOWN-GAME ANALOG
In-corpus: R8 Connection Go (Go×Hex), which this re-enters. In the literature: **Hex**, with a Go surround-capture rule and influence-disk control replacing stone-adjacency connectivity.

### KILLER FLAWS
- **Three-state control breaks Hex's no-draw guarantee** — contested seams can deadlock both players, sending decisive-looking games to an anticlimactic timeout area-count.
- **Capture is near-vestigial in open play** (degree-6 surround is too costly to fire except at edges/corners), so a headline mechanic rarely matters.

### BEST QUALITY
The forced connect/cut duality: the connection objective guarantees board-spanning contact, and the same stones that block the opponent build your own perpendicular connection — a clean, self-justifying tension (verified live). This is the crown jewel and it is genuinely Hex-grade.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
**Load-bearing.** Connection topology depends on adjacency, and hex (degree-6) is the canonical substrate that suppresses the mutual-cut draws a square grid invites — flattening to a grid would change the cut/connect calculus materially. The 22×22 size opens real routing depth (multiple board-spanning lines, room to detour around walls), the genuine upside of the large board here. Against R19's "menger > carpet > grid" finding, hex earns its keep in a connection game in a way it did not in the paired clump-race game.

### IMPROVEMENT IDEAS
**Single best change:** Make capture cheaper/more relevant — e.g. **outnumber-style capture (≥2–3 enemy-surplus neighbours) instead of full Go surround** — so blocker-removal becomes a live tactical layer in open play (falsifiable: capture frequency in self-play would rise from ~0 to a meaningful rate and cut-fights would gain a tactical dimension).
Secondary:
- Tighten the control rule (e.g. require |field| above a margin, or break ties toward connection) to reduce contested-seam deadlocks and the timeout-area anticlimax.
- Consider radius-1 influence to sharpen connections back toward Hex precision (less fuzz, clearer bridges).
- Add a small structural reward for *largest component* at timeout (not just total area) so the connection theme governs the tiebreak.

---

## Q-vs-Z Comparison

**Which game would you rather play again?** Z.
**By how many Overall points?** +0.8 Overall in favour of Z (Z 4.1 vs Q 3.3).
**Key differentiator:** The **win condition**, not the shared substrate. Z's edge-to-edge connection objective forces the two players' paths to intersect (real cut/connect fighting, captures gain purpose as blocker-removal), whereas Q's additive influence-sum threshold lets both players build non-interacting blobs and win on raw tempo. Same board, same pie, same influence machinery — Z turns it into a contact game and Q does not.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/probe_ab/team-1_gameZ.md`.*
