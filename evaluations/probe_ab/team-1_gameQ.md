# Probe A/B Eval — team-1 — Game Q

**Team ID:** team-1
**Game Label:** Q (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6, pie_rule=True
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `evaluations/probe_ab/play.py --game Q` (run `--rules` first for rules; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Derived entirely from `play.py --game Q --rules` and observed engine behaviour.

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r); cell index = q + 22*r. Neighbours of (q,r): (q±1,r), (q,r±1), (q+1,r−1), (q−1,r+1) — verified from the control map of a single central stone. Interior degree 6; acute corners degree 2; obtuse corners degree 3. Board displays as 22 sheared rows.

**Turn structure.** Alternating, 1 stone/turn, P1 first. Max_turns = 200.

**Action space.** 486 actions = 484 placement + 1 pass + 1 pie_swap. No move actions. Placement legal at any empty cell. pass=484, swap=485.

**Placement & capture.** Capture rule = **outnumber-2** (threshold 2). After a placement, an enemy stone is removed iff it has ≥2 friendly (mover-colour) neighbours. **Verified: the check is LOCAL** — only enemy stones *adjacent to the just-placed stone* are tested. A P2 stone sitting with 2 P1 neighbours is NOT removed until P1 plays a stone adjacent to it (confirmed: invader 274 with 2 P1 neighbours survived P1's non-adjacent move 231, then was captured when P1 played the adjacent 275). Captures are single stones only.

**Propagation.** Hex influence field, radius=1, strength=1.0, decay=0.7. Each placed stone adds ±1.0·0.7^dist to `board_values` within radius 1 (self +1.0, each neighbour +0.7). Sign +1 P1 / −1 P2. Clamped [−100,100]. **Quirk (verified): the field is NOT reversed on capture** — a captured stone leaves a permanent "ghost" footprint. Baseline (P1 never places; P2 plays 231+252) shows ONLY `−` cells; but placing P1 253 then letting it be captured leaves residual `+` cells with zero P1 stones on the board. So `board_values` is a monotone accumulation of every placement ever made; capture removes ownership and the stone, not its influence.

**Win condition.** Score race: the first player whose **sum of `board_values` over their own (stone-occupied) cells exceeds 36.0** wins (P1 positive sum; P2 negated). Komi_p2 = 0.0 (no fractional bonus). Confirmed the threshold is per-player own-sum, NOT the displayed differential: an unopposed P1 blob crosses 36 (40.40) and wins; in a balanced parallel race P1 won at a displayed differential of only 5.20 because both own-sums sat near ±36 and P1 reached its threshold one tempo first. Equal → draw. Timeout (200 turns) → **piece-count majority** (more stones on board), NOT the score; equal → draw.

**Pie rule.** After P1's first stone, P2 may swap (action 485): inherits P1's stone (now counted negative/P2) and the turn order continues. Corrects the first-mover edge.

**Degeneracy check.**
- **Permanent ghost influence** (above): captures never undo field contributions. For Q this is mostly cosmetic — only owned cells score and the timeout tiebreak is piece-count, so ghosts only marginally boost the value of cells you later occupy. A "pump a single cell by repeatedly sacrificing into it" exploit is tempo-negative (each pump cycle hands the opponent a free racing move and also feeds +0.7 to the enemy neighbours that capture you), so it is not a practical degeneracy — but it is an inelegant, leaky rule.
- **Capture is local + tempo-negative (2-for-1).** Removing one enemy stone costs two of your placements adjacent to it, and your attacking stones are themselves capturable. Disruption is strictly worse tempo than racing, so capture is a minor harassment tool, not a strategic pillar.
- **Board geometry quirks.** 484 cells is far larger than the ~11–23 stones a game actually lasts; players can build non-interacting blobs in separate regions, so hex corner/edge irregularities almost never come into play.

---

## Phase 2 — Strategic Play

All moves engine-verified through `play.py --game Q`. Action IDs = q + 22*r; pass=484; pie_swap=485. `484` used as P2 "pass" to isolate a one-sided push.

### Game 1 — P1 unopposed push (compact hex blob)
Sequence: `253,484,252,484,274,484,231,484,275,484,232,484,254,484,251,484,273,484,295,484,230,...` (P1 builds the r≤2 hex disk around centre (11,11); P2 passes).
Plot: Each added stone in the cluster is super-additive — a stone fully surrounded by friends is worth 1.0 + 6·0.7 = 5.2; a 7-stone hexagon ≈ 23.8. P1's own-sum crosses 36.0 after **11 stones** (step 21, differential 40.40) → **P1 wins**. No captures (P2 inert).
Reflection: Binding constraint is *compactness* — owned-cell value is maximised by maximising friendly-neighbour count per stone, i.e. a solid hex blob. Placement order is otherwise free.

### Game 2 — P2 contest by parallel race
Sequence: `184,322,183,321,205,343,162,300,206,344,163,301,185,323,182,320,204,342,226,364,161,299,227,365` (P1 blob around (8,8); P2 mirror blob around (14,14), far apart).
Plot: Two non-interacting blobs grow in lockstep. **P1 wins at step 21** (11 P1 stones placed vs 10 P2): displayed differential 5.20, both own-sums near ±36, P1 crosses first. Pure first-mover tempo decides — exactly one ply.
Reflection: On a 484-cell board the two armies never touched. With no forced contact, the "fight" evaporates and the game is a deterministic tempo race won by whoever did not have to spend the pie/opening tempo. **This is the central weakness: the oversized board lets both players avoid interaction.**

### Game 3 — Adversarial / capture-stress + seat swap
(a) Invasion/robustness: `253,484,252,274,231,484,275`. P2 invades the blob at 274 (2 P1 neighbours) but survives P1's non-adjacent 231 (local capture); P1's *adjacent* 275 then captures it. Net: P2 spent a move to be removed; blob interior is untouchable (all-friendly neighbours).
(b) Seat swap: `253,485`. P1 opens dead-centre (strong); P2 swaps → the central stone becomes P2's (differential −1.00, P1 to move). Demonstrates pie neutralises a strong opening, so correct P1 play is a *weak* first move.
Plot: Capture skirmishing is a sideshow; the only swing levers are (i) the pie decision and (ii) refusing to be drawn into tempo-negative captures.

### Strategy guides
**P1 (offence / score push):** Open with a deliberately mediocre stone (off-centre, near an edge) so P2 declines the swap; then build the most compact hex blob you can, ignoring the opponent. Reach own-sum 36 in ~11–12 packed stones. Never initiate captures (2-for-1 tempo loss).
**P2 (defence + contest; pie-aware):** Swap iff P1's opening is strong/central. Otherwise mirror-race your own compact blob in empty space; do not attack P1's blob (tempo-negative). Only capture when an enemy stone is already adjacent to one of yours *and* removing it is on your way (free).

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Effectively **no** — there is one dominant plan ("build the most compact blob, fastest"). Capture-harassment and area-denial are both tempo-negative, so they are never preferred. The only genuine decision is the pie swap.
**Counter-play.** Largely **absent**. You cannot efficiently stop an opponent's blob (capture costs more tempo than it denies), so you cannot interact your way to an advantage; you can only out-tempo via the pie.
**Short-term vs long-term.** Shallow. Games end in ~20–25 plies; the planning horizon is "where to seed one blob," which symmetry makes nearly irrelevant. The 22×22 board does NOT buy a longer horizon — it shortens interaction by giving everyone room to hide.
**Emergent concepts observed.** Blob super-additivity (compactness premium); capturable outer shell vs untouchable interior; permanent ghost field; first-mover tempo knife-edge. None require look-ahead beyond a couple of plies.
**Does hex_rhombus topology matter?** Barely. Degree-6 lets blobs reach 5.2/cell instead of (square-grid) 5.0/cell, and changes the optimal blob shape from a square to a hexagon — cosmetic. The same race exists on a square grid with minimal loss.
**Does the propagation kernel matter?** Radius-1/decay-0.7 sets the super-additivity slope and therefore how many stones reach 36 — it is load-bearing for *pacing* but not for *strategy*. The field enters win logic (owned-cell sum) directly, so it is not mere decoration; but it produces no spatial decision richer than "clump tightly."
**Capture-rule contribution.** Captures fired only when I forced them; in natural racing they essentially never occur. Outnumber-2 buys edge harassment and punishes lone invaders, but its 2-for-1 tempo cost and local-only firing keep it strategically marginal.
**First-mover advantage / seat balance.** Strong residual P1 edge in the raw race (wins by exactly one tempo, komi_p2=0.0). Pie is the *only* thing that balances it, and it does so by forcing P1 into a weak opening. With correct pie play, balanced; without pie, P1 wins by default.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Q is a re-skin of a **clump/territory race with Ataxx-flavoured outnumber capture**. Argument:
(a) "First to own-cell influence-sum > threshold" rewards the largest, densest connected friendly mass — functionally a **material/area race** ("build the biggest blob"), the field sum being a smooth proxy for clump size.
(b) Capture analog: **outnumber-2 → Ataxx/Tafl-style overwhelm** (numerical-superiority adjacency capture), not Go (no liberties) and not custodian/Othello (no bracketing).
(c) "outnumber + radius-1 influence + score-race threshold": the closest published relative is a **Go area-race stripped of territory subtlety** — closer to abstract clump-builders (think a continuous-scored Clobber/blob game) than to any landmark title. No exact published match, but every component is old.
(d) Substrate: hex-rhombus degree-6 lattice — the lattice does almost no work here (cosmetic blob-shape change). It does NOT exploit topology the way R17–R21's menger/carpet/grid distinctions did.
(e) Expert transfer: a Go/Ataxx player learns this in ~5 minutes — "pack tightly, race to threshold, don't bother capturing." The irreducible novel piece is only the *permanent ghost influence field*, and that quirk is inert in practice.

**Closest known-game analogue:** an abstract **blob/area race** with Ataxx-style outnumber capture — "make the densest connected group first."
**Comparison to R8 Connection Go (replay anchor 4.10).** Same broad lineage (influence + capture on a hex board) but **strictly thinner**: R8 had a *connection* objective that forced board-spanning interaction; Q's clump-race objective permits zero interaction on a large board. Sits clearly **below** R8.
**Comparison to R19/R20/R21 best.** Thinner than R19 (5.0) and R20 best (4.80); around or just below R21 (3.69). What changed: removing a connection/structural objective in favour of an additive threshold collapses the strategy space to "clump fastest."

**Novelty score (post-adversary):** **3.0/10.** Above pure re-skin (2–3) because the additive influence-sum win metric and the permanent ghost field are not standard; below novel (8–9) because the playable game is an old clump/area race and the novel bits are inert. Anchor: R17 3.50, R8 4.10, R21 3.69.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game Label:** Q
**Rules Summary:** Race to be the first to amass an influence-field sum over your own stones above 36 by packing a dense friendly blob on a 22×22 hex board; outnumber-2 capture and a pie swap are present but the game is essentially a tempo race for the biggest clump.
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=True, komi_p2=0.0.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** permanent (non-reversed) influence field after capture — a leaky/inelegant rule, harmless in practice.

### Scores (1–10)
- **Strategic Depth: 3.0** — one dominant plan (clump fastest); the only real decision is the pie swap; ~20-ply games, negligible branching.
- **Emergent Complexity: 3.0** — blob super-additivity, untouchable interior, ghost field; all surface-level, no multi-ply tactics arise in natural play.
- **Balance: 4.0** — pie corrects an otherwise decisive one-tempo first-mover win, but the underlying race is a fragile knife-edge and komi_p2=0.0 leaves pie doing all the work.
- **Novelty (post-adversary): 3.0** — see Phase 4; an old clump/area race with Ataxx-style capture; novel bits (ghost field, additive win) are inert.
- **Replayability: 3.0** — once "compact blob race" is known every game repeats; opening location is symmetric and adds no variety.
- **Overall "Would an agent team play this again?": 3.3** — a thin, low-interaction race diluted by an oversized board; below R8 4.10 and R21 3.69.

### CLOSEST KNOWN-GAME ANALOG
In-corpus: a degenerate cousin of R8 Connection Go with the connection objective replaced by an additive clump threshold. In the literature: an abstract blob/area race with Ataxx-style outnumber capture.

### KILLER FLAWS
- **Zero forced interaction on a 484-cell board** — both players build separate blobs and the game is decided by raw tempo (pie), not by play.
- **Capture is strictly tempo-negative (2-for-1, local-only)** so the only disruption mechanic is never worth using — the strategy space collapses to "pack tightly."

### BEST QUALITY
The blob super-additivity gradient (compactness premium) is a clean, legible pressure — but it is the *only* idea in the game, and it points at a single optimal shape.

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
Minimal. Degree-6 changes the optimal blob from a square to a hexagon and nudges per-cell value 5.0→5.2; the dynamics survive on a square grid essentially unchanged. The 22×22 size actively HURTS by enabling non-interaction. Against R19's "menger > carpet > grid" topology-matters finding and the R8 board-size concern, Q is on the wrong side: bigger board, less game.

### IMPROVEMENT IDEAS
**Single best change:** Replace the additive own-sum threshold with a **board-spanning connection objective** (control/own a path edge-to-edge), forcing both players to cross the board and intersect — this single change converts the non-interactive race into a contact game and would lift depth substantially (falsifiable: games would no longer be decided by tempo alone, and capture would acquire purpose as blocker-removal).
Secondary:
- Shrink the board to ~11×11 so blobs are forced into contact even under the current objective.
- Reverse field contributions on capture (remove the ghost) for rule cleanliness.
- Make capture tempo-neutral (e.g. capture clears a cell you may immediately use) so disruption becomes a real lever.

---

## Q-vs-Z Comparison

**Which game would you rather play again?** Z.
**By how many Overall points?** +0.8 Overall in favour of Z (Z 4.1 vs Q 3.3).
**Key differentiator:** Z's **connection objective forces board-spanning interaction** (you must cross the opponent, captures gain purpose as blocker-removal); Q's additive clump threshold permits two non-interacting blobs racing on tempo alone. The win condition — not the substrate, which is shared — is what separates them.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/probe_ab/team-1_gameQ.md`.*
