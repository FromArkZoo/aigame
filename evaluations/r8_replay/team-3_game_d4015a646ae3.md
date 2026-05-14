# R8 Replay Eval — team-3 — Game d4015a646ae3 (Connection Go)

**Team ID:** team-3
**Game ID:** `d4015a646ae3` (R8 top-1 by ELO, Feb-2026 agent eval = 8/10, GE 0.386, depth 0.545, ELO 2304.6)
**Substrate:** flat 2D grid, axis 8, 64 active cells / 64 total, max_degree 4, pie_rule=**False**
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d4015a646ae3 --db genesis_v2_run8.db` (see `briefing_r8_d4015a646ae3.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, 64 active cells, no holes. Cell index `c = y*8 + x`. Max_degree 4 (orthogonal neighbours only — **no diagonals**, so no Hex-style bridge connections are available). Interior cells = 4 neighbours, edge cells = 3, corners = 2.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 65 actions = 64 placement + 1 pass. No move actions, no pie action (pie_rule=False).

**Placement & capture.** Placement: any empty cell, no first-move restriction. Capture rule = **surround** (Go-style liberty capture). **The briefing's `threshold=3` is misleading**: I empirically verified that the engine implementation (`engine_v2.py:606` `_capture_surround`) is **true Go-style liberty capture**, NOT "≥3 neighbours of my colour". A group of any size is captured only when ALL its liberties (empty adjacent cells) are filled. The `threshold` field is **vestigial** for the surround branch.

Probe: P2 group `(0,0)+(0,1)` had one liberty `(0,2)`; P1 at (0,2) cleared both stones. Earlier attempt to capture `(4,3)` by placing 3 P1s around 3 of its 4 neighbours **did not fire** — that stone retained one liberty at (5,3).

**Propagation.** influence, r=3, strength≈0.715, decay≈0.751. Each placement deposits ±0.715 self, ±0.537 to deg-1 neighbours, ±0.403 to deg-2, ±0.303 to deg-3. With r=3 footprint up to 25 cells affected per ply.

**Win condition.** **Hex-style connection win**, NOT threshold-race. The helper's `Win: threshold-race > 0.500` header is hardcoded and false. The `_check_connection` engine path BFSes the placer's owned stones from one face to the opposite face along the player's target dimension:
- **P1 wins by connecting top↔bottom** (y=0 row to y=7 row via P1 chain).
- **P2 wins by connecting left↔right** (x=0 column to x=7 column via P2 chain).

Goals **cross** — both players contend for each cell but for orthogonal reasons.

The displayed `P1 effective score / P2 effective score` numbers are influence accumulation (threshold-race accounting), **irrelevant for win detection**. They function as a positional-pressure metric only.

**Pie rule.** Off. R8 predates pie.

**Degeneracy check.**
- `threshold=3` field on the capture rule is inert (true Go liberty capture is used).
- `threshold: 0.5` on the win condition is inert under connection-win.
- The helper's effective-score readouts mislead any agent reading them as the win condition. **Soft violation: the engine and helper disagree on what "winning" means.**
- Max_turns=100 with no draw fallback: if neither player connects, game ends Winner=None.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 64.

### Game 1 — P1 race straight vertical, P2 builds parallel column (passive P2)

Sequence: `27,28,19,20,11,12,35,36,43,44,51,52,3,5,59` (15 plies, **P1 wins** by completing column x=3 from y=0 to y=7).

Plot:
- Plies 1–12: P1 walks down x=3 (centre column), P2 mirrors at x=4. Each side has 6 stones forming parallel vertical columns by ply 12.
- P1 (3,0) at ply 13: closes the top face. P2's only "blocker" stone in P1's path was at (4,4) — but P2 had built nothing on x=3 yet. P2 plays (5,0) at ply 14, a wasted move.
- P1 (3,7) at ply 15: **engine declares Winner=1**. P1's chain (3,0)→(3,1)→(3,2)→(3,3)→(3,4)→(3,5)→(3,6)→(3,7) connects top to bottom.
- No captures fired. P2's mirror-strategy lost without resistance.

Reflection: **P2 mirroring is a losing strategy.** Since P1 goes first and both need 8 stones to wall, P1 always finishes one move ahead if P2 doesn't actively block P1's path.

### Game 2 — P2 actively blocks P1's centre column

Sequence: `27,35,19,43,11,51,3,59,18,34,26,42,50,33,58,…` (15+ plies, **game stalls — no winner through ply 24, P2 always 1 move ahead at every detour**).

Plot:
- Ply 2: P2 plays (3,4) — directly inserting into P1's intended column.
- Plies 2–8: P2 plays the lower-half of x=3: (3,4),(3,5),(3,6),(3,7). P2's defence is "build my own vertical wall splitting the board on P1's column". P2 has wasted no stones — they sit exactly where P1 would have gone.
- Plies 9–15: P1 detours via x=2, building down x=2. P2 follows down x=2 too — (2,4),(2,5),(1,4),(1,5). Each P1 advance triggers an immediate P2 block, ALWAYS one step ahead because P2 sees P1's intent and only needs to plug one cell.
- By ply 15 P1's chain is split: top group `{(3,0),(3,1),(3,2),(3,3),(2,2),(2,3)}` and bottom group `{(2,6),(2,7)}` cannot be reconnected because rows 4-5 are wall-to-wall P2 across x=1..3.
- Continued past ply 24, P1 attempted to push further to x=1 — P2 blocked (1,4) before P1 could fill it. Sequence rejected as illegal because P2 already owned the cell.
- No captures fired throughout. The P2 wall group has too many liberties on its edges.

Reflection: **The blocker has a massive structural advantage on this 8×8 4-connected board.** Once P2 commits to defence, P2 only needs to block ONE cell per row to break P1's connection (no diagonal bridges available — see Phase 4). P1 must spend 2+ moves to detour per blocker, but P2 only needs 1 to block.

### Game 3 — Adversarial: first-mover edge race (P1 wins clean in 15 plies)

Sequence: `0,7,8,15,16,23,24,31,32,39,40,47,48,55,56` (15 plies, **P1 wins** by completing column x=0 from y=0 to y=7).

Plot:
- Plies 1–14: P1 walks column x=0, P2 walks column x=7 (mirror).
- Ply 15 P1 (0,7): engine declares Winner=1. P1's left-edge wall connects top↔bottom.
- P2 has 7 stones at x=7 forming their own vertical column — **but P2 needs HORIZONTAL connection (left↔right), so P2's column doesn't win.** P2's mirror was strategically null.

Reflection: **First-mover advantage is overwhelming without pie rule.** P1 can win in exactly 8 plies if P2 doesn't interfere. P2 *must* block P1's path on every turn — but P2 has no time to also build their own connection. The trained PPO reference 0.84 winrate (trained vs random) is consistent with strong first-mover advantage.

### Strategy guides

**P1 (offence, race-to-connect):** Open in the centre (e.g. cell 27). Anticipate P2's block, then commit to a long detour while leaving multiple ambiguous paths open. **P1's only chance is to threaten two simultaneously divergent paths so P2 cannot block both** — but on a 4-connected board with no bridges this is hard. The trained PPO 0.84 vs random comes from random P2 not knowing the path; trained P2 stops P1 cold.

**P2 (defence, block + threshold contest):** **Plant directly into P1's intended path** as early as ply 2. Build a horizontal wall in the *middle* of the board (e.g. y=3 or y=4) that splits the board. P2's own win condition (left-right) is a *bonus* — most of P2's winning moves coincide with blocking P1. Wait until P1 commits a detour, then close the open side at minimum cost.

**Either side:** Captures rarely fire. The 4-neighbour-max grid means stones almost always have multiple liberties. Don't plan around captures.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** 2 main ones, both shallow:
1. **Straight-line race** — P1 builds the shortest column from face to face. Wins vs passive P2.
2. **Block-then-stall** — P2 inserts into P1's column on ply 2 and builds the bisecting wall. Forces a stall or P2 win.

A 3rd theoretical strategy — **multi-path threats / Hex ladders** — is unavailable here because **the 4-connected grid has no diagonal connectivity = no Hex bridges.** In real Hex (6-connected), a "bridge" of two stones at (a,b) and (a+2,b+1) is virtually-connected because P2 cannot block both intermediate cells. On this grid, every chain step is orthogonal-only, and P2 can always intercept a single cell to break it.

**Counter-play.** Block-then-stall is a near-complete counter to any P1 strategy because of the bridge-absence. **The game's only "strategic depth" is the race-vs-block tempo question, and the asymmetry of the goals doesn't fully save it on this small board.**

**Short-term vs long-term.** Almost no long-term planning. Games end by ply 8–20. Mid-game looks like Game 2 — both sides commit to local race-blocking exchanges. Branching factor effective: ≈ 3-5 per move (only cells along the live frontier matter).

**Emergent concepts observed.**
- **Bridge absence as core flaw.** Hex's beauty comes from 6-connected bridges that can't be blocked. The 4-connected grid kills this.
- **Wall race symmetry.** Both players build orthogonal walls; the slower-to-start (P2) always sees what P1 is doing.
- **Influence as misleading information.** The "effective score" the helper prints is *not* the win condition — agents trying to greedily maximize that number will play wrong. Influence has zero direct strategic value here.
- **Centre stones are strictly weaker than edge stones** for face-connection: a centre stone needs 2 chains to reach faces; an edge stone needs 1.

**Does the substrate matter?** Yes, **badly.** Axis-8 is too small. On axis-13+ Hex (the standard size), connection games have depth because there's room for multiple threats and ladders. Axis-8 → games end in 8–15 plies → no strategic horizon.

**Does the propagation kernel matter?** **No — it's vestigial for the win condition.** PPO sees `board_values` in the observation, so it influences policy learning, but a human/agent player reading the board for connection-win doesn't care about influence values. The kernel is *strategic noise*.

**Capture-rule contribution.** Negligible in my games. **Zero captures fired in Games 1, 3.** A single capture fired in a deliberate liberty-closing probe. On the open 8×8 grid, groups always have multiple liberties; surround captures require setup that no rational player would walk into. The capture rule is essentially inert.

**First-mover advantage / seat balance.** **Severe and uncompensated.** No pie rule = P1 wins by tempo. PPO `trained_vs_random` reference is 0.84 for both seats — this number doesn't tell us about P1 vs P2 balance, only about training stability. **Without trained-vs-trained data, the seat balance is unknown but the structural advantage is obvious**: P1 needs exactly 8 moves to win on an empty board; P2 needs 9+ (because they must block first).

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is **Hex on a 4-connected square grid with vestigial Go ornaments**:

(a) **Connection-win across asymmetric faces** is *exactly* Hex's defining structure. Identical mechanic. Hex is a well-known, theoretically deep game with 60+ years of study. **The win-condition is not original.**

(b) **Surround-capture (Go-style liberty)** is added on top. In real Go, surround capture interacts with connection because stones need eyes/liberties. Here, the 4-connected open grid + no diagonals means liberty closure almost never fires. **The Go layer is decorative — it changes nothing about how connections are won.**

(c) **Influence propagation** has zero effect on the connection-win path. It changes the PPO observation tensor (because `board_values` is part of policy input) but it is not part of the game-theoretic structure. **The influence layer is purely a training shaping hack** to give PPO a denser reward signal. It is not a game mechanic.

(d) **8×8 flat grid substrate** with 4-connectivity is **strictly worse than Hex's standard 11×11 or 13×13 with 6-connectivity**. The bridge structure that makes Hex deep is absent. **Square-grid Hex has been tried in the literature (sometimes called "Square Hex" or studied as a degenerate case) and is known to be much shallower than hex-grid Hex.**

(e) **Expert-transfer test.** A Hex player + Go player understands this game in 60 seconds: "Hex on a square grid (so worse), plus Go captures that almost never fire." The irreducible new piece is `(influence propagation field)` which an expert would correctly identify as "PPO training shaping, not strategy."

**Closest known-game analogue:** **Square-grid Hex.** Connection win on a 4-connected square grid — a well-known degenerate variant of Hex that's been discussed in the abstract-games literature. The Go-style captures and influence propagation are additive decorations, neither of which gives a player a new strategic tool.

**Comparison to R8's own "Connection Go" pitch.** The briefing claims this is novel because of "surround capture + influence on top of Hex". In play, **neither addition actually contributes strategic depth**:
- Surround captures didn't fire in any of my 3 games. The open grid means liberties are abundant.
- Influence does nothing for win detection. It exists for PPO training shaping, not for the player.

So the "Connection Go" name is **mostly aspirational**. The actual playable content reduces to "Hex on a worse grid".

**Comparison to R19/R20 production means.** R19 menger top (`5048f71b62fd`, 5.0/10) is surround-capture + threshold-race on the menger sponge. R20 top (`carpet-pie` 4.7/10) is outnumber-2 + influence + threshold-race + pie on the carpet. **Both R19/R20 games actually use their capture and substrate features in play** (captures fire, holes matter, pie balances seats). Connection Go uses **none** of its capture and propagation features meaningfully in play. **R8's novelty story is thinner than R19/R20's.**

**Player rebuttal.**
- The Hex backbone IS theoretically deep — but only at axis 11+, with 6-connectivity, and with pie. None of these are true here.
- Asymmetric goals on a 2D grid are an unusual flavour that *could* differentiate this from generic threshold-race games — but they don't substantively add depth on axis 8.
- The capture and propagation features are essentially inert decoration. A player would correctly conclude this is "small Hex with a useless extras".

**Novelty score (post-adversary):** **3/10.** Above pure re-skin (2) because the asymmetric-connection-win structure isn't shared with the R20 threshold-race corpus and that's a real architectural difference. Below "genuinely new" (8+) because connection-win is Hex's signature mechanic, the substrate is small and worse than real Hex, and the additive features (capture, influence) don't contribute. Anchor: R17 mean 3.50 — this game is *at* R17 mean for novelty, not above it. The 8/10 February rating likely conflated "structurally distinct from siblings" with "novel".

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** `d4015a646ae3`
**Rules Summary:** On an 8×8 grid each player alternately drops a stone with r=3 influence radiating around it; Go-style surround captures clear groups with all liberties filled (rarely fires); win by connecting your two assigned faces (P1 top↔bottom, P2 left↔right) via a chain of your own stones — Hex on a 4-connected square grid.
**Substrate:** flat 2D grid, axis 8, 64/64 cells, max_degree 4, pie_rule=**False**.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** capture-rule `threshold=3` field is vestigial (true Go liberty capture used); win-condition `threshold=0.5` field is vestigial under connection-win; helper's `Win: threshold-race > 0.500` header and `effective_score` lines describe the wrong win condition; no pie rule on a game with severe structural first-mover advantage.

### Scores (1–10)

- **Strategic Depth: 3** — The race-vs-block dilemma is the only real decision layer. Once the blocker commits, P1's chances drop to ~zero on an 8-wide board because there's no Hex bridge to threaten dual paths. Games resolve in 8–20 plies with branching factor ≤5 along the active frontier. Engine-measured depth 0.545 overstates the felt depth — most "decisions" are forced by the obvious immediate block or the obvious immediate race step.

- **Emergent Complexity: 3** — Almost no emergent patterns. No capture cascades (captures don't fire). No influence-based decisions (the field is non-strategic for the win condition). No territory shapes. The only emergent dynamic is "centre stones are weaker than edge stones for connection" which is a known Hex pattern, not an emergent property of THIS game.

- **Balance: 2** — Severe uncompensated first-mover advantage. Without pie rule on a small board where P1 needs 8 stones and goes first, P1's race-ahead is structural. Trained-vs-random 0.84 for both seats doesn't measure seat balance. **A trained-vs-trained reference is missing** but the structure makes the bias obvious. **This is the worst-balanced game I've evaluated.**

- **Novelty (post-adversary): 3** — See Phase 4. Hex on a square grid. The capture and influence layers are decorative and inert. Above pure re-skin only because the asymmetric-connection win is structurally distinct from R20's threshold-race corpus.

- **Replayability: 3** — Two strategy clusters (race vs block) collapse quickly. Once P2 knows to plant on P1's path at ply 2, the game has no surprises. Replay value comes from where P1 chooses to attack (centre, edge, off-axis) and where P2 places the wall — these are slight positional variations of the same template, not separate games.

- **Overall "Would an agent team play this again?": 3** — **Significantly below the February 2026 8/10 rating.** Calibration drift detected. The game I played felt like a small, broken Hex with non-functional Go decorations. R17 mean 3.50, R19 production mean 4.375, R20 production mean 3.73 — this game scores **below the R17 mean, well below R19/R20 production means, and dramatically below its own 8/10 anchor.** A 5-point drop from the historical anchor.

### CLOSEST KNOWN-GAME ANALOG

**Square-grid Hex (axis 8) with decorative Go-capture and influence-field overlays.** Inside the Genesis corpus, this is the only connection-win game on a small flat grid; outside, it's a degenerate variant of Hex that's been discussed but is not played competitively.

### KILLER FLAWS

- **No Hex bridges on a 4-connected grid.** This kills the strategic depth that connection-win would normally provide. Bridges are the mechanism that makes Hex theoretically infinite-deep; without them, connection-win becomes a tempo race that the first mover wins.
- **No pie rule** on a game with severe structural first-mover advantage. P1 needs 8 moves to win, P2 needs 9+ (block + build), and P1 goes first.
- **Captures essentially never fire in real play.** The 4-neighbour-max + open 8×8 grid makes liberty closure expensive. In my 3 games, zero captures fired in two games and one in a deliberate probe. The "capture" rule is dead code.
- **Influence propagation is non-strategic for connection-win.** It exists for PPO observation shaping, not for player decisions. An agent reading the helper output would be misled by the "effective score" metric, which has nothing to do with winning.
- **Axis 8 is too small.** Diameter 7 means the shortest connection is 8 stones. Games are over before strategic patterns can develop.
- **Helper/engine disagreement.** The helper header says "threshold-race > 0.500" while the engine uses connection-win. Any agent reading the helper output naively will play the wrong game.

### BEST QUALITY

**The asymmetric goal structure is genuinely architecturally distinct from the threshold-race corpus.** Among the R20 production slate, this is the only game where the two players have **different** win conditions. That orthogonality of objectives is the one thing that makes Connection Go feel like a different shape of game vs the R20 threshold-race siblings, and it correctly identifies the Hex backbone as the genuine novelty source. The problem is that the *implementation* (axis 8, 4-connected, no pie) cripples the goal structure before it can become deep.

### GRID STRUCTURAL CONTRIBUTION

**Negative.** The 8×8 grid with max_degree 4 is the worst possible substrate for connection-win games. Real Hex uses a 6-connected hexagonal grid at axis 11+ with pie precisely because (a) 6-connectivity enables bridges, (b) larger axis enables ladders and multi-threats, (c) pie corrects first-mover bias. This game has none of those. **A flat-grid substrate is doing negative work here** — it makes the Hex backbone shallower than it could be on its native substrate.

### IMPROVEMENT IDEAS

**Single best change:** **Switch substrate to a 6-connected hex grid at axis 11+ and add pie rule.** This is the minimum change to get from "broken small Hex" to "actual Hex with Go decorations". The propagation/capture features can stay as decorative observation-shaping — they don't need to be removed, but they don't need to be load-bearing either.

Secondary improvements:
- Add pie rule (mandatory) — fixes the first-mover catastrophe.
- Switch to axis-13+ — gives strategic horizon.
- Remove the threshold-race score from the helper output (it actively misleads agents).
- Either make captures actually relevant (lower threshold, smaller groups capturable) or remove the capture rule entirely as dead weight.
- Either make influence affect the win condition (e.g. tiebreaker for max-turn-timeout) or remove it as dead weight.

**Calibration finding (CRITICAL — see briefing § 'Three branch outcomes'):** Under the R20 protocol with the current rubric, this game scores **3/10 overall**, vs the February-2026 anchor of **8/10**. This is a **5-point drop**, consistent with R20 production mean (3.73) and well below R19 production mean (4.375). My finding is that **the February 8/10 was inflated — calibration has drifted up**, and the GE-bottleneck diagnosis is probably wrong. The game's current GE rank of 6/12 on the calibration slate may actually be accurate; what's wrong is the historical 8/10 anchor, not the modern GE ranking. Resolution: **outcome (2)** — R21 launch with `w_planning=0` looks correct on this evidence; do NOT redesign the fitness function on the assumption that the February rating is the true ceiling.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/r8_replay/team-3_game_d4015a646ae3.md`.*
