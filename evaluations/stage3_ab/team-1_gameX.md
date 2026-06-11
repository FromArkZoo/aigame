# Stage 3 blind eval — team-1 — Game X

**Team ID:** team-1
**Game Label:** X (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6.
**Evaluator:** single-agent team running both player roles and Novelty Adversary sequentially.
**Helper:** `evaluations/stage3_ab/play.py --game X` (run `--rules` first; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Derived entirely from `play.py --game X --rules` plus observed engine behaviour.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r. Rows sheared right by r. Interior degree 6; acute-corner degree 2; obtuse-corner degree 3.

**Turn structure.** Alternating, exactly 1 stone/turn. Max_turns = 200 (then timeout tiebreak).

**Action space.** 486 actions = 484 placement (0..483) + pass (484) + pie_swap (485). Placement legal at any empty cell. Opening legal-action count = 485 (swap is available only as P2's reply to P1's first stone).

**Placement & capture.** Capture rule = **surround** (Go capture). After placing, any enemy *group* (connected same-owner stones) with **zero empty-cell liberties** is immediately removed (cleared to empty). On this degree-6 lattice a lone stone needs all 6 neighbours filled to die. The rules output also reports **"Threshold field = 1 (vestigial for surround)"** — an explicitly dead parameter. Engine-verified: a lone P2 stone (253) with three P1 neighbours is **not** captured (still has liberties → "X O X"); only after all 6 liberties are filled (`252,253,254,484,275,484,231,484,232,484,274`) is it removed (centre → empty). A P2 *pair* {230,231} surrounded on the outside but retaining liberties 232/253/210 survives (`229,230,252,231,208,484,209,484,251` → P2=2, "X O O X").

**Propagation.** Influence field: each placed stone adds ±strength·decay^dist within radius. P1 +1.0·0.5^dist; P2 −1.0·0.5^dist. Clamped [−100, 100]. **Radius = 2, strength = 1.0, decay = 0.5.** A lone stone projects a radius-2 hex disc of 19 controlled cells.

**Win condition(s).** Influence-field **connection** (Hex-type, mutually exclusive seats):
- P1 wins by a hex-connected chain of P1-controlled cells (value > 0) linking r=0 to r=21 (top↔bottom).
- P2 wins by a hex-connected chain of P2-controlled cells (value < 0) linking q=0 to q=21 (left↔right).
Connection is over *control* cells, not stones — "fat": 6 spaced stones win unopposed. Checked for the active player after their move.
**Timeout (200 turns):** higher TOTAL controlled-cell count wins; P2 gets komi_p2·484 virtual cells; equal = draw.

**Pie rule.** ON. After P1's first stone, P2 may swap (485): inherit the stone, P1 becomes mover.

**Komi_p2.** 0.0 (timeout tiebreak only; draws possible).

**Degeneracy check.**
- The influence field is **load-bearing** — it is the literal win substrate, not decoration. Good.
- The **threshold field (=1) is explicitly vestigial** per the rules output — a dead parameter carried by the capture machinery.
- The surround capture is **even more inert than a flip would be**: full hex enclosure (6 liberties) is prohibitively expensive in the spread stone-placement that connection rewards, so it essentially never fires in connection play, and removing a stone is only a +1 field swing (vs a flip's +2). In every connection line I played, the result was identical to game V because no capture triggered. The capture rule is also *mechanically dissonant* with the win: it operates on stones/liberties while victory is decided by the influence field, so a removed stone can leave the field essentially unchanged where it mattered.
- Geometry: acute corners (degree 2) / obtuse corners (degree 3) leak influence off-board → weak, swap-safe opening cells.

---

## Phase 2 — Strategic Play (both roles)

All moves engine-verified through `play.py --game X`. Action IDs = q + 22*r; pass=484; swap=485.

### Game 1 — as Player 1
Sequence: `10,220,98,224,186,228,274,232,362,236,450,240,230` (13 plies). **Winner = P1.**
Plot: identical race to the connection test — vertical corridor q=10 vs competent P2 horizontal wall r=10. Bands crossed, both connections broke at the lone contested centre cell (P1=84/P2=84). On my move I punched the crossing (230) and connected top↔bottom (P1=93). **No surround capture fired** — and the result is byte-identical to the same line in game V.
Reflection: binding constraint = the central crossing cell and **move parity**; as first mover I reach it on my turn. The surround rule contributed nothing — there was never a fully enclosed group.

### Game 2 — as Player 2
Sequence: `21,243,23,247,111,251,199,255,287,259,375,263` (12 plies). **Winner = P2.**
Plot: competent P1 opened on an acute corner (21) — pie-safe but a wasted tempo. I (P2) built a horizontal corridor on row r=11; P1 raced a vertical column q=11 but, down a tempo, could not contest the crossing before my left↔right chain closed (P2=88). Identical outcome to game V's P2 line.
Reflection: my win path mirrors P1's through the same crossing cell; the decisive lever is again the **pie rule** forcing P1's weak opening. Swapping a strong central P1 first move is the alternative competent P2 plan. The surround capture never entered the game.

### Game 3 — Adversarial / novelty-stress
Sequence: `252,253,254,484,275,484,231,484,232,484,274` (full enclosure → capture) + `229,230,252,231,208,484,209,484,251` (group keeps liberties → NO capture) + `10,230,98,484,186,484,274,484,362,484,450,484,231` (cut-routing → winner=1).
Plot: I stress-tested the capture three ways. (1) **Full enclosure works** but is expensive: filling all 6 liberties of a single P2 stone to remove it costs 5–6 P1 stones for a +1 field swing — terrible value versus just laying corridor. (2) **Partial surround fails**: a P2 pair with any liberty survives, so you cannot cheaply clear a blocker. (3) **Cut-routing**: a lone P2 stone dropped in my corridor did not cut it — I routed around with one stone and won (winner=1), and crucially the blocker was *never captured* (it still had liberties). So in X you can neither cheaply remove a cutter **nor** need to — you route. The surround rule is strategically dead weight in connection play.

### Strategy guides
**As Player 1:** open swap-safe (weak corner/edge); lay a vertical corridor spaced ~4 in r; win the central crossing on tempo. **Ignore the surround rule** — chasing captures wastes the spread you need to connect.
**As Player 2:** make the **pie swap your first decision** (swap strong central P1 openings); otherwise convert P1's swap-safe weak move into a tempo and race your horizontal corridor to the crossing. Block-by-building (Hex duality). Captures are not part of any efficient plan.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes but mirror-symmetric (P1 vertical / P2 horizontal), resolved at the shared crossing; P2 additionally owns the pie-swap decision. Both seats verified winning.
**Counter-play.** Real Hex duality — blocking the opponent is building your own connection; the single contested crossing cell is the whole game in symmetric lines.
**Short-term vs long-term.** Tactically thin (single-stone cuts fail and cannot be cheaply captured); the 22×22 board nominally supports a long horizon but play concentrates into one ~3-wide corridor, leaving most cells irrelevant.
**Emergent concepts observed.** Fat-corridor routing, crossing tempo race, wall-building duality. Surround capture produced **no** emergent tactics in connection play (it only fires in artificial dense enclosures I had to construct deliberately).
**Does hex_rhombus topology matter?** Yes — it is the Hex substrate (opposite-edge connection, crossing-exclusivity, no draws-by-crossing). Doing Hex's known job, not a novel one.
**Does the propagation kernel matter?** Materially — radius 2 / decay 0.5 makes connection fat/uncuttable and is the literal win substrate. The surround capture, by contrast, is divorced from this kernel and so feels grafted on.
**Capture-rule contribution.** Effectively nil in real play: full 6-liberty enclosure is unaffordable amid the spread that connection rewards, and removing a stone is only a +1 swing. The "threshold field" is flagged vestigial. This is the weakest part of the design.
**First-mover advantage / seat balance.** Real first-mover edge (P1 reaches the crossing on its turn); neutralised by the pie rule forcing a weak P1 opening. Balance genuine but knife-edge and pie-dependent — identical to game V.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of **Hex** (with a near-dead Go-capture bolt-on). Argument:
(a) Win = connect your two opposite rhombus edges on a degree-6 hex lattice with pie rule ON — the definition of Hex. The influence field only fattens the path.
(b) Capture analog: surround/zero-liberty removal ≈ **Go** capture — but on a connection win it neither clears blockers cheaply nor is ever needed, so it is decorative.
(c) "surround + influence propagation + edge-connection": the connection half is Hex (1942), the surround half is Go (millennia); the combination is the only un-catalogued piece, and here it is inert. R8 "Connection Go" already explored Go×Hex with the capture *actually mattering*; in X the capture does not.
(d) Substrate: canonical Hex board; less exotic than R17–R21's menger/carpet/grid.
(e) Expert transfer: a Hex player is fully competent in ~3 minutes; the Go-capture adds nothing they need to learn for connection play. Irreducible novel piece: only the fuzzy radius-2 connection (single-stone cuts fail) — and the surround rule is *strictly less* coherent with that field-win than game V's flip.

**Closest known-game analogue:** Hex with a vestigial Go-capture overlay on a 22×22 board.
**Comparison to R8 Connection Go (replay anchor 4.10).** Same family, but R8's capture was load-bearing; here surround is dead weight, so X is a *thinner* Go×Hex than R8 — comparable connection playability, weaker integration.
**Comparison to R19/R20/R21 best.** Thinner than R19 4.8/5.0; on par with mid-R20 and around R21 3.69 — the sound Hex core keeps it playable, but the distinguishing rule contributes nothing.

**Novelty score (post-adversary):** **3.5/10.** Above pure re-skin (2–3) because the fuzzy-field connection genuinely alters tactics; below game V's 4 and well below novel (8–9) because the spine is textbook Hex *and* the distinguishing surround rule is inert and dissonant with the field win — less integrated than V's flip. Anchor: R17 3.50, R8 4.10, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game Label:** X
**Rules Summary:** Hex on a 22×22 hex rhombus where "connection" is over influence-controlled cells (radius-2 field) rather than stones, with pie rule and a Go-style surround capture that requires full 6-liberty enclosure and essentially never fires in connection-optimal play.
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=ON, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only; plus pass and pie-swap).
**Soft violations flagged:** "threshold field = 1" explicitly vestigial; surround capture effectively dead in connection play (full hex enclosure unaffordable, +1 swing, dissonant with the field win); timeout area-count mode dormant; komi 0 permits draws.

### Per-role sub-scores (1–10)

**As Player 1:**
- Strategic Depth: 5 — real Hex connect/block duality and a crossing tempo race, blunted by uncuttable fat connections; the surround rule adds nothing.
- Emergent Complexity: 3 — fat-corridor routing emerges, but the capture produced zero emergent tactics in play.
- Replayability: 4 — many openings, but play converges to the same crossing race.

**As Player 2:**
- Strategic Depth: 5 — symmetric to P1 plus the genuine pie-swap decision (the most interesting choice available).
- Emergent Complexity: 3 — same emergent set; surround stays dormant.
- Replayability: 4 — swap-vs-build branching gives marginally more opening variety.

### Role-averaged scores (1–10)

- **Strategic Depth: 5.0** — sound borrowed-from-Hex depth, dulled by uncuttable connections and a dead capture rule.
- **Emergent Complexity: 3.0** — routing aside, the surround capture contributes no emergent play.
- **Balance: 3** — structurally symmetric seats; P1 tempo edge neutralised by the pie rule (my games split 1–1).
- **Novelty (post-adversary): 3.5** — see Phase 4; fuzzy-field Hex + an inert Go-capture.
- **Replayability: 4.0** — large board but one effective corridor; modest opening variety.
- **Overall "Would an agent team play this again?": 3.8** — a competent, playable Hex variant whose only distinguishing rule (surround) is strategically dead and dissonant with the field win; the core keeps it afloat but offers less than game V. Anchored down against drift.

### Fairness perception (mandatory)

**Fairness perception: 3 — symmetric seats with the pie rule neutralising P1's real first-mover/crossing-tempo edge; P1-role and P2-role games each won for whoever earned the crossing tempo (1–1 split).**

### CLOSEST KNOWN-GAME ANALOG
Hex (Piet Hein / Nash) with a Go-style surround capture overlaid on an influence field. In-corpus: a thinner cousin of R8 Connection Go (where capture mattered; here it does not).

### KILLER FLAWS
- The signature rule (Go-surround) is **strategically dead**: full degree-6 enclosure is unaffordable amid connection-spread, it is never needed to clear a blocker (you route around lone cutters), and it is dissonant with a win decided by the influence field rather than by stones/liberties.
- **Fat connections blunt tactics**: single-stone cuts cannot sever a corridor, so the game collapses to a tempo race for one crossing cell — and unlike a thin-stone connection game there are no cut/ladder fights to compensate.

### BEST QUALITY
The Hex skeleton itself: the connect/block duality and the crossing tempo race are genuinely sound and make for a coherent, decisively-resolving contest — that borrowed core, not anything the capture rule adds, is what keeps X above the floor.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
The degree-6 rhombus performs Hex's role (opposite-edge connection, crossing-exclusivity), so the topology shapes strategy — but as Hex's known contribution, not a novel one, and the plainest connection substrate against R19's menger > carpet > grid finding. The 22×22 size adds nominal horizon but the effective board is one ~3-wide corridor, so extra size is mostly filler. The surround rule does not exploit the hex degree-6 structure in any positive way — it merely makes captures harder (6 liberties), pushing the rule further toward irrelevance.

### IMPROVEMENT IDEAS
**Single best change:** shrink the influence radius to 1 (or steepen decay) so connections become thin and single-stone cuts bite — this both restores real cut/ladder tactics and gives the surround capture an actual job (removing a stone could re-open a severed corridor). Falsifiable: depth and capture-relevance should rise sharply.
Secondary:
- Replace surround with a cheaper/field-coupled capture (e.g. game V's influence-flip), or reduce liberty requirements, so the capture is reachable in spread play.
- Add positive komi_p2 / a turn cost to activate the dormant timeout area-game.

---

## Cross-game comparison (fill after all assigned games are done)

**Ranking of your assigned games by Overall score:** V=4.0, X=3.8 (D not assigned to this team).
**Which game would you most want to play again?** V.
**By how many Overall points above the next-ranked game?** V is +0.2 Overall above X.
**Key differentiator:** the capture rule, the only difference between the two games. V's influence-flip is field-based (coherent with the field-control win), fires on local dominance, and cascades; X's Go-surround needs full hex enclosure, gives a smaller +1 swing, is dissonant with the field win, and never fired in any connection line. Both rest on an identical Hex spine, so this single rule — and V's better integration of it — is what separates them.

---

*Output saved to `evaluations/stage3_ab/team-1_gameX.md`.*
