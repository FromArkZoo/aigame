# Run 15 Human Evaluation — Team 10

- **Team ID:** team-10
- **Game ID:** `d8f2ae54f399`
- **Generation:** 10 (parent: `4af27911b0f5`)
- **GE score (DB):** 0.2548, Non-triviality: 1.00, ELO: 2632.8
- **Evaluator note:** single-agent-plays-all-three-roles; seat-identity bias acknowledged explicitly below.

---

## Phase 1 — Rule Comprehension

### Board and turn structure
- **Board:** 8×8 = 64 cells, 2-D **grid** (flat; NOT torus; no wrap-around).
- **Turn structure:** **Alternating**, 1 placement per turn. P1 moves first.
- **Num actions:** 65 (placements 0–63, plus action 64 = PASS).
  - Action-ID convention: `a = y·8 + x`. Confirmed via `play_helper show` (a1=(1,0), a8=(0,1)).
- **Placement rule:** Place on any empty cell (`target: empty`, `constraint: anywhere`, `first_move_anywhere: true`).
- **No movement / no CA.**

### Mechanics
- **Surround capture (Go-style):** After a placement, every adjacent enemy **group** whose liberty count drops to zero is removed. `threshold: 1` here is the standard "capture groups with zero liberties" reading (not a custodian-sandwich threshold). Source: `engine_v2.py:482 _capture_surround`.
- **Influence propagation:** `prop_type: influence`, `radius: 1`, `strength ≈ 0.932`, `decay ≈ 0.510`. Each placed piece adds a signed scalar to the per-cell `board_values` field within Chebyshev-1 (actually 4-neighbour grid; see below):
  - Own cell: +0.932 (for P1) / −0.932 (for P2).
  - Each 4-neighbour cell (N/S/E/W): +0.932·0.510 ≈ +0.475 (signed).
  - The field is a running signed sum; a P2 piece placed next to a P1 piece subtracts 0.475 from that P1 piece's cell value.
- **Win condition:** `condition_type: threshold`, `threshold ≈ 22.645`, summed over **only cells the player currently owns**, P1 using `board_values` directly, P2 using `−board_values`. First player whose effective sum exceeds 22.645 **immediately wins on that step**.
  - Iteration order in `_check_threshold` is `for player in (1,2)` but ties on a single step cannot happen in an alternating game (only one player places per step and influence is signed per-owner), so the Run-15 P1-tie-break bias does **not** apply here.
- `max_turns: 100`. Double-pass ends the game as a DRAW (Run-15 engineering change).
- **Topology:** grid, so liberties count only orthogonal neighbours; no edge wrap.

### Mechanical feasibility / degeneracy check
- **Threshold reachable?** Yes — a single isolated stone contributes only ~0.93 to effective value (radius-1 propagation spreads most of its "mass" onto neighbour cells that the placer does not own), but a densely packed cluster yields per-cell effective values of up to 2.83 (centre of a plus-shape with 4 friendly neighbours). Empirically ~10–12 tightly clustered stones reach 22.6. My three play-throughs all resolved in 21–23 moves by threshold, **never by double-pass or max-turns**.
- **Capture rule non-inert?** Alive in theory (ordinary Go liberties), but in practice the game almost never reaches capture: both players are incentivised to build on empty territory rather than contest, because invading enemy territory costs you your own influence cell's worth. Across 3 games, **zero captures occurred**. Flag: capture rule is plausibly vestigial at this parameterisation.
- **Pass exploit?** Passing yields no points; the other player can simply continue building. Not degenerate.
- **Edge cases:** No CA table to verify symmetry; topology is grid (not torus), so wrap-around quirks don't apply; threshold-order bias is alternating-immune.

---

## Phase 2 — Strategic Play

Three full games played; every move engine-verified via `play_helper.py --action play`. Effective scores read from `engine.board_values` with the in-process helper at `/tmp/game_runner.py`.

### Game 1 — Both players build adjacent clusters in the centre

| Move | Player | Action | Cell | P1 eff | P2 eff | Comment |
|---|---|---|---|---|---|---|
| 1 | P1 | 27 | (3,3) | 0.93 | 0.00 | Centre — max future 4-neighbour bonus. |
| 2 | P2 | 36 | (4,4) | 0.93 | 0.93 | Diagonal mirror. |
| 3 | P1 | 26 | (2,3) | 2.81 | 0.93 | Build west — connects (3,3)+(2,3). |
| 4 | P2 | 28 | (4,3) | 2.34 | 2.34 | Invade between my stones; tempo. |
| 5 | P1 | 19 | (3,2) | 4.22 | 2.34 | Add north; creates L-shape. |
| 6 | P2 | 20 | (4,2) | 3.75 | 3.75 | Mirror north extension. |
| 7 | P1 | 35 | (3,4) | 5.15 | 3.27 | Add south; (3,3) now has 3 P1 neighbours. |
| 8 | P2 | 11 | (3,1) | 4.68 | 3.73 | Attack — reduces (3,2) value. |
| 9–18 | … | … | … | … | … | Both continue building; P1 grows faster thanks to tempo. |
| 19 | P1 | 24 | (0,3) | 18.83 | 13.14 | West edge extension. |
| 21 | P1 | 32 | (0,4) | 21.66 | 15.03 | Edge-column lockdown. |
| **23** | **P1** | **16** | **(0,2)** | **24.02** | 16.43 | **P1 wins — threshold crossed.** |

**Winner:** P1. 12 P1 pieces vs 11 P2 pieces. Zero captures. No double-pass.

### Game 2 — Non-adjacent mirrored clusters (no contact)

Both sides deliberately kept their clusters in opposite corners (P1 in NW, P2 in SE) so the influence fields never overlapped. The effective-sum race reduces to "who can fit a tighter 3×3" + tempo.

| Move | Player | Action | Cell | P1 eff | P2 eff | Comment |
|---|---|---|---|---|---|---|
| 1 | P1 | 18 | (2,2) | 0.93 | 0.00 | NW anchor. |
| 2 | P2 | 45 | (5,5) | 0.93 | 0.93 | SE mirror. |
| 3–12 | … | … | … | … | … | Parallel 3×3 formation; scores lock-step equal through move 12 (12.25 each). |
| 13 | P1 | 26 | (2,3) | 14.13 | 12.25 | P1 extends first (tempo). |
| 15 | P1 | 25 | (1,3) | 16.96 | 14.13 | Cluster now 2×4. |
| 17 | P1 | 27 | (3,3) | 19.80 | 16.96 | 3×3 complete. |
| 18 | P2 | 57 | (1,7) | 19.80 | 17.89 | P2 finally deviates — invades P1 flank (ineffective; no contact). |
| 19 | P1 | 33 | (1,4) | 21.68 | 17.89 | Extend further. |
| 20 | P2 | 43 | (3,5) | 21.68 | 19.78 | Desperate adjacency to reduce future P1 expansion. |
| **21** | **P1** | **34** | **(2,4)** | **24.51** | 19.78 | **P1 wins — threshold crossed.** |

**Winner:** P1. 11 P1 pieces vs 10 P2 pieces. Zero captures.

### Game 3 — Seat swap: I now play as P2. P1 plays a spread-stone strategy deliberately.

| Move | Player | Action | Cell | P1 eff | P2 eff | Comment |
|---|---|---|---|---|---|---|
| 1 | P1 | 0 | (0,0) | 0.93 | 0.00 | Corner. |
| 2 | P2 | 27 | (3,3) | 0.93 | 0.93 | Take the centre. |
| 3,5,7,9,11,13,15 | P1 | various | corners + edges | … | … | P1 plays 8 non-adjacent perimeter stones. |
| 4,6,8,10,12,14,16 | P2 | 28,19,20,26,35,18,34 | central 3×3 | … | … | P2 builds tight cluster. |
| 16 | P2 | 34 | (2,4) | 7.46 | **16.96** | P2 has a full 3×3. P1 is at 7.46 (8 stones × ~0.93). |
| 20 | P2 | 44 | (4,5) | 9.32 | 21.68 | One stone from threshold. |
| **22** | **P2** | **43** | **(3,5)** | 11.21 | **24.51** | **P2 wins — threshold crossed.** |

**Winner:** P2. P1's "spread" strategy is catastrophically dominated by cluster density.

### Per-player post-game reflections

**P1 reflections (from games 1 and 2):**
- *Strategy used:* grab centre, extend one cell at a time into adjacent empties, prioritising moves that give 2+ friendly-neighbour contact.
- *What I'd change:* in Game 1 I let P2 invade (3,1), which cut off my NE expansion and forced me to run south-west. Had I played (3,4) before (3,2), I would have secured the cluster earlier and probably won a move sooner.
- *Surprised?* Yes — P2's (1,7) in Game 2 was pure desperation with no mechanical effect. Confirms that once clusters are non-contacting, the influence field is additively separable and there is no "interaction game" — it's just a tempo race.
- *Win condition reached?* All three games resolved by threshold, not by double-pass or max-turns. (0 of 3 games double-pass; no flag.)

**P2 reflections (from games 1, 2, 3):**
- *Strategy used in games 1–2:* mirror P1, attempt tactical invasions like (3,1) to reduce P1's effective value. This disruption works arithmetically (subtracts 0.475 from two adjacent P1 cells) but costs a tempo that I need to reach my own threshold. Net: lose the tempo race.
- *Strategy used in game 3 (as the faster-clustering side):* take centre, never deviate from cluster-building, ignore P1's perimeter stones entirely. Result: overwhelming win.
- *What I'd change (as P2 against a strong P1):* abandon the "disrupt P1" instinct. Build your own 3×3 faster. Invasions near P1 cost you as much as they cost them, and you started a move behind.
- *Surprised?* The fact that non-contacting clusters produce a purely additive score race is mildly disappointing — the topology adds nothing in that regime.

### Player-side strategy guides

**P1 strategy guide:**
1. Move 1: take (3,3) or (4,4). Maximise future 4-neighbour bonus potential.
2. Moves 2–6: build a 2×2 immediately; each added stone with 2 friendly neighbours contributes +1.88 effective (own 1.41 + neighbour boost 0.475).
3. Moves 7–12: extend into a 3×3; the centre now has 4 friendly neighbours for 2.83 effective.
4. Moves 13+: extend the cluster toward an edge. Edge stones have fewer enemy-adjacency risks and still add ~1.88 to the running sum.
5. Never spread. Every non-adjacent stone is worth only ~0.93.
6. Ignore P2's invasions unless they threaten a capture. Trading tempo for influence reduction is net-zero, and you're a tempo up.

**P2 strategy guide:**
1. Mirror P1's opening — take (4,4) if P1 took (3,3), or (3,3) if P1 took (4,4). Centre is critical.
2. **Build, don't disrupt.** Any invasion of P1's cluster costs you a move you can't afford.
3. Keep your cluster separate from P1's. Non-contact = separable score = you just need to tie the tempo race, and P1 is one stone ahead.
4. If P1 plays spread/perimeter (as in Game 3), build your own 3×3 and run; you will cross threshold around move 20.
5. Your only realistic path to victory when P1 plays correctly is if P1 makes a positional error. There is no "P2-specific" advantage in the rules.

---

## Phase 3 — Strategic Analysis (joint)

**Are there distinct viable strategies?**
No, **one strategy class dominates**: "take centre, build a dense cluster, avoid contact." Alternatives tested:
- Spread strategy (Game 3 P1): catastrophic loss.
- Invasion / disruption (Game 1 P2 move 8): arithmetically net-zero per move but costs initiative.
- Two-cluster strategy: untested but would almost certainly under-perform one-cluster because the 4-neighbour bonus scales super-linearly with cluster compactness.

**Meaningful counter-play?**
Limited. P2 has two tools:
1. Mirror and hope to out-build via micro-tempo opportunities (tested in Game 2 — fails by one move).
2. Disrupt P1 via invasion to reduce P1's effective value. Invasion reduces P1 cluster values by 0.475·(number of P1 adjacencies) — but the P2 invader sits in a high-P1-influence zone, so its *own* value is also reduced by the same amount. **Net-zero swap of tempo for mutual damage.**
The only real counter-play is forcing a capture, but surround capture requires fully enclosing a P1 group. Across 3 games no capture occurred; this would require sacrificing ~4–6 moves of cluster-building to execute, which is always a losing trade at this threshold.

**Short-term vs long-term tension?**
Weak. The dominant strategy has no inflection points — every move is worth roughly the same +1.88 (edge-add to cluster) or +2.83 (filling an interior hole). There is no "sacrifice now for later" — the game is linear.

**Emergent concepts?**
- **Territory** (clear): the 3×3 cluster is a territorial object.
- **Influence** (built in): literally the scoring function.
- **Tempo** (critical): P1 wins via first-mover advantage alone in contested mirrors.
- **Initiative** (limited): only matters in the first 5 moves.
- **Ko fights**: N/A — no capture events happened.
- **Mutual annihilation**: N/A (alternating, not simultaneous).

**Does topology matter?**
Marginally. A grid with influence radius 1 rewards central placement (more 4-neighbour potential) and penalises corner placement (only 2 neighbours max). On a torus this distinction would vanish. Edge/corner asymmetry is the only topology-level strategic factor, and only matters for the opening move.

**First-mover advantage (quantified):**
- P1 won 2/2 contested symmetric games (Games 1, 2). In both cases, P1 reached threshold on the 21st or 23rd move; P2 was 2–3 effective units behind.
- The **only** game P2 won (Game 3) was because P1 intentionally played a bad spread strategy.
- In a symmetric mirror, **P1 always wins by one tempo** unless P1 makes a positional error. This is a **clear, un-eliminated first-mover advantage**.
- Quantified seat-swap: 1/1 games where I played P2 optimally (Game 3), P2 won, but only vs a handicapped P1. Against mirror-strength play, I estimate P2 win-rate at a max of ~20% (relying on P1 errors).

**Seat-identity bias acknowledgement:** I played all three roles sequentially as a single agent. This means my P1 and P2 strategies share a prior and I likely over-smoothed their differences. A blind adversarial run would probably reveal sharper P2-specific tricks (e.g. targeted capture threats) that I didn't explore. However, even granting that, the mechanical analysis above (invasion = net-zero; capture = too expensive to set up) would still hold.

---

## Phase 4 — Novelty Adversary

### Adversary case (constructed against novelty)

**(a) Known-game comparison.** This is essentially **Go with a numeric territory scoring function and a fixed point threshold instead of an end-of-game count**. Evidence:
- Placement on empty cells, anywhere: Go.
- Go-style surround capture with 0-liberty groups: Go.
- Scoring based on "influence of your stones on board regions" is directly analogous to Go's **territory + influence** (e.g. the concept used in modern Go evaluators like KataGo's ownership map, or Zobrist's 1969 influence function that is literally a radius-bounded convolution very similar to this game's propagation).
- Versus **Gomoku**: no — Gomoku uses 5-in-a-row, not territory.
- Versus **Othello/Reversi**: partial — Othello uses custodian flipping (captured pieces switch sides). This game has no flipping. But both reward dense clusters.
- Versus **Hex / Y / Havannah / Connect6**: no — those are connection games, this is a threshold-on-scalar game.
- Versus **Tumbleweed**: **strong overlap**. Tumbleweed uses a "majority of line-of-sight" scoring that resembles an influence field. The present game is arguably "Tumbleweed with radius-1 isotropic influence instead of 8-direction sightlines."
- Versus **Chameleon / Lines of Action / Amazons / Mancala / Nim**: no.
- Versus **Life-like CA**: N/A — no CA in this game.
- Versus **Diplomacy / Blotto / Gungo**: N/A — alternating, not simultaneous.

**(b) CA analog.** Not applicable — no CA rules in this game.

**(c) Simultaneous analog.** Not applicable — alternating.

**(d) Topology/coordinate transformation.** The claim is: **this is Go + Zobrist-influence-scoring + a fixed-point win condition**, on an 8×8 board (smaller than typical Go but used in Go variants). The "transformation" is: take 9×9 Go, replace the final count (stones + territory) with a running influence sum, replace "two-consecutive-pass ends the game" with "first to threshold wins." An expert in **influence Go** (a recognised body of Go theory) would have immediate, strong intuition here.

**(e) Expert-transfer test.** Would a Go expert have an immediate advantage?
- **Yes, on opening theory:** centre-first, dense formations, avoid invasions you cannot support — these are all standard Go fuseki heuristics.
- **Yes, on tactical reading:** the capture rule is literally Go's.
- **Partial on endgame:** the fixed-point threshold means there is no yose (endgame) in the Go sense — you play until someone crosses the line. This is where the analogy breaks slightly.
- **Strong overall transfer.** An expert at Tumbleweed or influence-based Go evaluation would dominate a novice at this game on sight.

Adversary conclusion: this is **"Go with a Zobrist-influence fixed-point scoring rule on 8×8."** Score this no higher than 3/10 on novelty.

### Rebuttal (P1 + P2)

Specific rebuttal from Phase 2 moments:

1. **"No capture ever fires."** In 3 full games with 42 combined moves, zero captures occurred. The surround-capture rule is *formally* Go's rule but *strategically* inert at this threshold/propagation parameterisation because the score race resolves before capture can be engineered. A Go expert's tactical reading on ladders, shicho, and life-and-death is worth zero strategic points here. That's a meaningful departure.
2. **"Invasions are net-zero arithmetic."** In Go, an invasion that reduces your opponent's territory by 5 points while costing you a stone is typically worth it. Here, move 8 of Game 1 (P2 invades (3,1)) costs P2 exactly 0.475 of its own effective score AND costs P1 0.475 — **a symmetric subtraction with zero net strategic value**. Go invasions are non-symmetric (opponent's 5 points come off, yours don't). A Go expert's invasion intuition mis-fires here.
3. **"Ko is absent."** Ko is a central Go concept. The surround capture in this game never activates, so ko cannot happen. A large chunk of Go's strategic universe is inapplicable.
4. **"The win condition is on a short clock."** Games end around move 21–23 (out of max 100). Go games run 150–300 moves on 9×9. The endgame (yose) and middle-game phases of Go compress into essentially "opening theory" here — a different strategic rhythm.
5. **"The influence model is not Zobrist's exactly."** Zobrist-1969 uses iterative propagation until convergence. This game uses a single-pass radius-1 Gaussian-ish kernel with fixed strength/decay. Importantly, Zobrist influence is a **visualisation tool for Go evaluators**, not a win condition. This game uses it as the primary scoring mechanism, which changes the game theory fundamentally: players optimise directly for the influence field, which changes optimal opening shape.
6. **Vs Tumbleweed:** Tumbleweed's influence is line-of-sight (long-range, anisotropic, blocked by stones). This game's influence is radius-1 isotropic and unblocked. Strategic implication: in Tumbleweed, a single well-placed stone can dominate a long line; here, mass locality is king. These are genuinely different games.

**Net verdict:** the game shares mechanical DNA with Go and Tumbleweed, but has a *strictly simpler and more linear* strategic surface because (a) capture is inert, (b) invasions are symmetric, (c) games end before middle-game. A Go expert gets ~60% of the way by transfer but loses to a specialist who understands the fixed-point race.

**Novelty score awarded:** **4/10**. This is "scoring-variant Go" — clearly related to known games, but with enough of a strategic-flavour shift (linearised score race, inert capture, symmetric invasions) that it isn't a 1:1 re-skin.

---

## Phase 5 — Verdict

**Team ID:** team-10
**Game ID:** d8f2ae54f399
**Rules Summary:** 8×8 grid, alternating placement, Go-style surround capture, radius-1 signed-influence propagation; first player to exceed an effective-score threshold of 22.645 (summed over their own cells) wins.
**Topology:** 2-D grid, 8×8, no wrap.
**Turn Structure:** **alternating**.

### SCORES (1–10)

| Metric | Score | Rationale |
|---|---|---|
| **Strategic Depth** | **3** | One dominant strategy: cluster densely in the centre. Sub-strategies (invasion, capture, spread) are net-losing. Choices above "take centre, then extend into a 3×3" are nearly indifferent. No branching long-term plans. |
| **Emergent Complexity** | **3** | Influence field is pretty to watch but arithmetically separable when clusters don't touch (Game 2). Capture rule never fires. No meaningful emergent phenomena beyond "density beats spread." |
| **Balance** | **4** | Strong P1 first-mover advantage empirically. Two symmetric mirror games (G1, G2) both won by P1 on tempo alone; G3 P2 win required P1 to self-handicap. Estimated mirror-strength P2 win-rate ~20%. |
| **Novelty (post-adversary)** | **4** | Clear structural overlap with Go + Tumbleweed + Zobrist-influence scoring. The fixed-point win condition and radius-1 isotropic kernel give it a slightly different strategic rhythm, but a Go/Tumbleweed expert transfers most intuitions. |
| **Replayability** | **3** | Once the dominant strategy is known, games converge to the same 20–23-move script. Cluster-placement is the only meaningful choice, and corner-vs-centre variation is small. |
| **Overall "Would I play this again?"** | **3** | I'd study it once as a curiosity (the influence-field win condition is a nice toy), but I wouldn't play it for fun or competition. |

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed + Go** — the influence-score-race rhythm is Tumbleweed-like; the capture rule and placement rule are Go-like. It is *not identical* to either because (a) Tumbleweed's influence is line-of-sight, not radius-1; (b) Go scores only at game end, not as a running threshold.

### KILLER FLAWS
1. **First-mover advantage is un-eliminated.** In 2/2 optimal-play mirror games, P1 wins by one tempo. The rules do not provide a komi-style compensation.
2. **Capture rule is strategically inert.** Zero captures across 42 moves. The rule exists but never activates. An evolutionary-generated game with an inert rule is a mild indictment of the rule-selector.
3. **Invasion is net-zero.** Symmetric mutual influence reduction makes the main Go-like tactic strategically pointless.
4. **Strategic surface is linear.** Almost every non-terminal move is worth +1.88. There are no forcing sequences, no sacrifices, no long-range tactics.

### BEST QUALITY
The **influence-field fixed-point win condition is a clean, readable scoring mechanism**. Unlike Go, where evaluating a mid-game position requires expert judgement, here you can read `effective_score_P1 = sum of board_values over P1 cells` at a glance and know exactly how close each player is to winning. This is pedagogically nice and makes the game legible.

### IMPROVEMENT IDEAS
**Introduce a negative-sum invasion rule.** The dominant-strategy problem is that contact is net-zero. If the rule were: "an enemy stone adjacent to your group reduces your effective value by 1.0 (not just by the influence propagation of 0.475)," then invasions become a real tool, capture becomes valuable (removing the penalty), and P2 gains a meaningful catch-up mechanism. Alternatively, **add a komi**: P2 starts at effective value +3.0 to compensate for first-mover.

---

## Process notes

- All 23 moves of Game 1, 21 moves of Game 2, and 22 moves of Game 3 were engine-verified. No rejected moves; no illegal-action discoveries.
- No double-pass draw in any game (0/3 — no flag).
- No capture in any game — flagged above as a killer flaw.
- Single-agent seat bias: acknowledged in Phase 3.
- Time: ~15 minutes per game; well under 25-minute budget. No max-turn truncations (all games ended 21–23 moves, far below the 100-cap).
- Engine version: `game_engine/engine_v2.py`, loaded via `factory.create_engine` with rule JSON from `genesis_v2_run15.db`.
