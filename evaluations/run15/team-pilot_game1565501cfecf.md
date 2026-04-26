# Team-pilot evaluation — Game 1565501cfecf (R15 champion, pilot sanity check)

Team ID: team-pilot
Game ID: 1565501cfecf
Generation: 9
GE Score: 0.318
Evaluated: 2026-04-22

## Phase 1 — Rule comprehension

**Board.** 8×8 torus (64 cells). 2D. Von Neumann adjacency. All cells topologically equivalent (no true center, no corners).

**Turn structure.** `simultaneous`, `pieces_per_turn=1`. Both players submit one action per round; `step_simultaneous` resolves them atomically. **Collision rule: if both players target the same non-pass cell, mutual annihilation — neither stone placed, cell stays empty.**

**Actions.** Place-only. 65 action slots = 64 placement + 1 pass. Action ID for cell (x,y) = `y*8 + x`. Placement target = empty cells, constraint `anywhere`, `first_move_anywhere=true`. No movement.

**Capture.** `capture_type=none`. No capture mechanic — once placed, stones are permanent (cannot be removed by opponent action; only mutually annihilated on same-cell collision at placement time).

**Propagation.** `influence`, radius=3, strength=0.9657, decay=0.5867. Signed field (`board_values`): P1 placement adds `+strength·decay^dist`, P2 adds negated. Manhattan distance on torus. Per-stone footprint = 25 cells (1 + 4 + 8 + 12 at dist 0/1/2/3). Per-stone own-cell contribution (no enemy) ≈ +0.966; friendly neighbor boost at dist 1 = +0.567, dist 2 = +0.332, dist 3 = +0.195.

**Win condition.** `threshold`, threshold=38.627. Player wins when `sum(board_values[c] for c owned by player)` (sign-corrected) exceeds 38.627. `max_turns=100`. **Double-pass ends as draw** (R15 rule change).

**CA.** None.

**Degeneracy flags:**
- Threshold=38.63 with per-stone max own-contribution ≈1.0 → need roughly ~39+ own-cell-equivalents, i.e. at least ~12-15 stones played if clustered (friendly boosts push cluster own-cells above 1.0), or ~40+ if played isolated. Reachable in 10-15 rounds in practice (confirmed below).
- **The threshold-win tie-break iterates P1 before P2** (see `engine_v2.py:_check_threshold` line 748-761). If both players exceed threshold in the same simultaneous round, **P1 wins deterministically**. This is a subtle structural bias in every symmetric simultaneous threshold game.
- No capture + no CA + placement-only = monotone board state (piece counts only grow; influence only grows in magnitude). Nothing can undo a placement except collision.

## Phase 2 — Strategic play

### Protocol note (CRITICAL)

`play_helper.py --action play` calls `engine.step(move)` sequentially, which treats every move as an alternating-turn action regardless of `turn_structure`. It **does not use** `engine.step_simultaneous(a1, a2)`. Running a simultaneous game through `play_helper` in its default form silently turns it into an alternating game with the same legal-move set. **This must be flagged for the production teams** (see Protocol Notes at end).

For this evaluation I used a custom wrapper (`team_pilot_sim_helper.py`, based on `team18_sim_helper.py` from R14) that pairs moves as `p1:p2` per round and calls `step_simultaneous`. Every move below was engine-verified through that helper.

### Game 1 — Antipodal 3×3 clusters (control)

Both players build a tight 3×3 cluster at maximum mutual distance on the torus (P1 around (3,3), P2 around (7,7) which wraps to touch (0,0)/(0,7)/(7,0)). No interference zone — each stone projects fully onto own-cells.

Moves (format `p1:p2`): `27:63, 19:55, 26:62, 28:56, 35:7, 18:54, 20:0, 34:48, 36:6, 43:61`.

After R9 (9 stones each, 3×3 clusters): both own_sum = **34.71** exactly. Perfect symmetry.

R10: P1 extends to (3,5)=43, P2 extends to (5,7)=61. Both clusters gain one peripheral stone; by symmetry both reach own_sum = **39.976** simultaneously, exceeding threshold 38.627.

Win check fires: P1 checked first → **P1 wins**. Game length: 10 rounds.

### Game 2 — Offset clusters (P2 plays non-antipodal corner)

P1 centers 3×3 at (3,3); P2 builds 3×3 at (1,1) — only 2–3 cells from P1 cluster, so their radius-3 influence fields overlap heavily.

Moves: `27:0, 19:1, 26:8, 28:9, 35:2, 18:16, 20:17, 34:10, 36:24, 37:3, 29:11, 44:25`.

R12 end: P1 own_sum=**38.84** (crosses threshold), P2 own_sum=36.07. **P1 wins in 12 rounds.**

Observations:
- Contact between clusters eroded both players' own-cell values (each stone dragged by enemy within r=3).
- P1's 3×3 + small extension at (5,3),(5,4),(4,5),(4,3) pushed further into P2's field than P2's mirror extensions pushed into P1's — leading to a **2-point P1 edge by R11** (35.34 vs 32.49) that widened to **2.8 by R12**. The asymmetry emerged from P2's corner cluster touching P1's cluster on one face while P1's expansion was free on the opposite side.
- Two rounds longer than Game 1: contact costs time.

### Game 3 — Seat-swap / spoiler attempt (pilot plays P2)

Pilot now sits in P2's seat. Since Games 1–2 established P1 has a structural advantage, P2 tries a spoiler plan: mirror P1 through R9, then on R10 play **inside P1's projection field** (cell (3,5)=43) to drag P1 below threshold while P1 tries to cross at (5,3)=29.

Moves: `27:63, 19:55, 26:62, 28:56, 35:7, 18:54, 20:0, 34:48, 36:6, 29:43, 21:11`.

R10 end: P1=37.83 (just shy of threshold), P2=33.53. Spoiler briefly worked — delayed P1's win by one round.

R11: P1 plays another high-value cell (5,2)=21, crossing 41.02. P2 tries another spoiler at (3,1)=11 but just sinks own_sum further to 31.96. **P1 wins in 11 rounds.**

Post-game reflection: The spoil strategy doesn't work because every "spoiler" cell is by definition P1-dominated (high +value), so when P2 occupies it the cell's contribution to P2's own_sum is negative (the P1 projection is larger than P2's new self-projection). P2 simultaneously slows P1 and drops her own score — net lose. **There is no move-in-hand that denies P1 the win without equally hurting P2.**

### Player reflections

**P1 strategy guide:** Build antipodal 3×3 cluster. You reach ~34.71 at 9 stones for free (zero enemy drag at antipode). One more peripheral move (distance 1 from cluster edge) crosses threshold at ~39.98. If opponent plays non-antipodal or spoiler, you still win by check-order tie-break — you're either tied or ahead. Don't waste moves adjacent to opponent; keep maximum separation.

**P2 strategy guide (reluctantly):** You cannot win against a competent P1 because (a) the threshold check iterates P1 first, and (b) you have no disruption move that doesn't cost you as much as it costs P1. The least-bad plan is to play the exact antipodal mirror and hope P1 blunders by playing in your half of the torus — which an optimal P1 never will. If P1 plays sub-optimally (non-antipodal), P2's window is narrow but real (Game 2 showed symmetric mirror play leaves P2 only ~2.8 behind). **The game is broken for P2 against competent P1.**

**Did ≥2 of 3 games resolve by double-pass draw?** No — all 3 games resolved by the stated win condition (threshold).

## Phase 3 — Strategic analysis (joint)

- **Dominant strategy exists:** Play the tightest cluster with maximum distance from opponent. Specifically, a 3×3 block is near-optimal; at antipode, clusters don't interact. The game has essentially one viable opening plan for both players.
- **Meaningful counter-play:** Very limited. Because there is no capture and no movement, once P2 falls behind (or sits at tie from symmetric play), P2 cannot recover. The only P2 counter-tool is mutual-annihilation collision, which requires guessing P1's next cell in simultaneous play (1/remaining-empty probability).
- **Short-term vs long-term tension:** Essentially none. Every move adds to own_sum; no sacrifice mechanic. The only "tempo" question is whether to play cluster-interior (high own-cell boost) or cluster-boundary (more new own cells) — both equally weighted by the influence math. This produced interesting Phase-2 moments (R10 decision between (3,5), (5,3), (1,3), (3,1)) but all four are equivalent in expectation.
- **Emergent concepts:** (i) Cluster efficiency (clumping boosts own-cell values through friendly reinforcement) — mild territory concept. (ii) Mutual-annihilation as a threat (P2 can force same-cell collisions by reading P1, but simultaneity denies this). (iii) Check-order first-mover advantage — the closest thing to "initiative" in this game is that P1 breaks ties.
- **Topology matters:** Torus matters mainly because it removes corners/edges. Antipode exists uniquely on torus of even size, and the fact that clusters can be fully separated is what makes Game 1's 10-round resolution possible. On a grid (non-wrapping) the corner stone has ~half the radius coverage so the cluster strategy shifts. But within the torus frame, every cell is equivalent.
- **First-mover advantage:** Yes — **structural, via check-order tie-break**. All 3 games won by P1, including the "seat-swap" Game 3 where pilot played P2. Seat-swap evidence is clear: **simultaneous turn structure did NOT eliminate first-mover advantage here**; it just shifted it from move-order to win-check-order.

## Phase 4 — Novelty adversary

### Adversary case against novelty

**(a) Catalog comparisons:**
- **Go:** No; Go has capture, liberties, ko, adjacency. Here none of these. Only surface similarity is "place stones on a grid".
- **Hex/Y/Havannah:** No; win by connection, not threshold. Topology matches but mechanic doesn't.
- **Reversi/Othello:** No; custodian capture is absent.
- **Gomoku/Pente/Connect6:** No; not line-forming.
- **Tumbleweed:** **Closest territorial analog.** Tumbleweed uses line-of-sight stacking on hex to claim influence over cells. This game uses radius-decay on torus. Rules are formally different but the core "each stone radiates influence, score = sum of projected influence on stones you own" is conceptually the same. A Tumbleweed expert would recognize the "project influence and count" framework, though line-of-sight ≠ radius decay.
- **Blotto / Colonel Blotto:** Strongest abstract analog. Simultaneous resource allocation across cells, with collision-as-annihilation punishing coordination. This is Blotto where (i) the resource you allocate is a placement, (ii) values depend on spatial clustering, (iii) "cells" are a torus instead of independent theaters.
- **Simultaneous Go / Gungo:** Matches turn structure exactly. Different win condition and no capture.
- **Life-like CA:** Irrelevant — no CA.
- **Nim / Slither / Amazons / LoA / Mancala:** No structural match.

**(b) CA literature:** not applicable.

**(c) Simultaneous games:**
- Blotto with spatial structure — as above, closest fit.
- Diplomacy order resolution: much simpler here (only collision handled; no supports/attacks).
- Simultaneous-move guessing games (RPS-scaled): partial fit for the collision sub-game, but embedded in a positional structure.

**(d) Re-skin claim.** Strongest candidate: "**Blotto on a torus with exponential-radius scoring and mutual-annihilation**". Under the transformation:
- Cells → Blotto theaters
- Per-round placement → per-round unit deployment
- Radius-3 decay → spatial coupling between theaters
- Collision rule → deployment-conflict rule
- Threshold win → "first to accumulate X victory points"
The mapping is lossy (Blotto has no board, no wrapping, no incremental accumulation) but **captures the essential simultaneous-allocation-with-spatial-coupling flavor**.

**(e) Expert transfer test.** A Blotto expert would immediately grasp the simultaneous-allocation dimension but not the spatial-clustering math. A Tumbleweed expert would grasp the "own_sum = Σ projected influence on my stones" framework but not the simultaneous/collision layer. Neither has a *direct* advantage; a knowledgeable player of BOTH would likely beat a specialist in either alone.

### Rebuttal (from P1 and P2)

Specific moments where known-game analogies failed:

1. **Game 1, R1 (P1=27, P2=63)**: both players placed at maximum torus distance without interference. In Tumbleweed this is impossible — stones always interact via line-of-sight blocking, and the hex board has corners. The pure "antipodal no-interaction" opening is unique to this game's torus-plus-radius setup.

2. **Game 3, R10 (pilot P2's spoiler at (3,5)=43)**: the spoiler produced **negative own_sum contribution** because the cell was already at +2.15 from P1's cluster. In Blotto this doesn't exist — Blotto theaters have no pre-existing "owned by enemy" value; you either win a theater or lose it. The continuous influence field here creates a uniquely useless "spoil but self-harm" move that no Blotto analogy covers.

3. **Cluster-reinforcement gradient (visible in R9 of Game 1)**: each cell in the 3×3 ranges from +4.56 (center) down to +4.05 (edge), a smooth gradient from the sum of 9 stones' contributions. This **curved territorial value surface** has no analog in discrete territorial games (Go, Hex, Tumbleweed) and only a loose analog in Amazons' region-counting.

4. **Collision as deterrent rather than weapon**: in all 3 games, no player ever intentionally induced a collision. Because collisions are symmetric (both lose a placement) and can't be forced in sim play, they function as a *background deterrent* that keeps both players from playing Schelling-point cells too aggressively. In Diplomacy or Gungo, simultaneous-move mechanics are usually *offensively* weaponized. Here they're dormant.

### Novelty resolution

**Novelty score: 5/10.** The combination (simultaneous + collision + radius-decay influence + threshold + torus) is uncommon and I cannot name a published game that covers all five. But each component is off-the-shelf, and the game's *effective* playable strategy collapses to a short script — "build a tight cluster at antipode" — that mirrors elementary territorial intuition. The core novelty is the continuous influence-field scoring, which is genuinely interesting but produces a shallow meta-game because there's no capture to undo placements.

## Phase 5 — Verdict

Team ID: team-pilot
Game ID: 1565501cfecf
Rules Summary: 8×8 torus; simultaneous place-one-stone per round (collision = mutual annihilation); radius-3 exponential-decay influence (strength 0.966, decay 0.587); win by own-cell signed-influence sum > 38.627. No capture, no CA.
Topology: 8×8 torus, Von Neumann adjacency, 64 cells.
Turn Structure: **simultaneous**.

### SCORES (1-10)

- **Strategic Depth: 3** — Near-dominant strategy ("build 3×3 cluster at antipode") wins deterministically for P1 in 10 rounds. Spoiler plans fail structurally. Little meaningful branching.
- **Emergent Complexity: 3** — The radius-decay influence field is genuinely continuous and produces a pretty gradient, but only one behavior emerges (cluster-and-extend). No capture, no ko, no movement means the state space is effectively monotonic.
- **Balance: 2** — Seat-swap evidence: P1 wins all 3 games regardless of which seat the pilot occupied. Structural P1 advantage via threshold-check order (`_check_threshold` iterates player 1 before 2). Even against identical play, P1 wins all symmetric-threshold ties. This is a **genuine balance flaw**, not just bad play.
- **Novelty (post-adversary): 5** — Unique component combination (simultaneous + collision + radius-decay + torus threshold) with no single named analog. Closest analog: Blotto with spatial coupling. But playable strategy space is shallow and collapses to one-line prescription.
- **Replayability: 3** — Once the cluster-and-extend script is discovered, games play out in 10–12 moves with the same outcome. Only randomization source is which 9/64 cells each player picks for their cluster, and the torus makes these equivalent.
- **Overall "Would I play this again?": 2** — As a human abstract game, no. As a testbed for AI training on simultaneous mechanics, marginally yes.

### CLOSEST KNOWN-GAME ANALOG
Blotto with spatial coupling on a torus. Not identical because (i) Blotto has no board or spatial structure, (ii) influence here is continuous-valued not binary theater-win, (iii) accumulation is over rounds instead of single-allocation.

### KILLER FLAWS
1. **Structural P1 advantage via check-order tie-break** (`engine_v2.py:_check_threshold` iterates player 1 first). In perfectly symmetric simultaneous threshold games, P1 always wins. Observed in all 3 games I played including seat-swap.
2. **No counter-play mechanic for trailing player.** No capture, no movement, no CA means once behind you cannot catch up. Monotone own_sum.
3. **Dominant opening "antipodal 3×3 cluster"** resolves the game in ~10 rounds with known outcome. Search depth is trivial.

### BEST QUALITY
The continuous radius-decay influence field creates a visually rich value gradient (visible in the `--show-values` dump) and the mutual-annihilation collision is a genuinely interesting simultaneous-game mechanic. These would be worth studying in a game that *also* had some recovery/capture mechanic to prevent the monotonic dynamic.

### IMPROVEMENT IDEAS
**Add capture or "dominated cell conversion": if a cell owned by P1 has signed value < 0 (net-negative influence projected onto it), flip ownership to P2 at end of round** (or remove). This restores recovery dynamics — enemy clustering can now *reclaim* your stones by over-projecting, giving the trailing player a reason to contest rather than concede. Alternatively, **add a tie-breaker based on turn parity** (in round N, if both cross threshold, winner = player whose placement had higher own-cell value gain) — removes the arbitrary check-order bias.

---

## PROTOCOL NOTES (for production team prompt patching)

**Flagged issues specific to R15 / this eval run:**

1. **play_helper.py does NOT use `step_simultaneous`.** The `--action play --moves "a,b,c,d"` interface calls `engine.step()` sequentially for each move, which treats the game as alternating-turn regardless of `turn_structure.turn_type`. A team that follows the prompt literally ("engine-verify every move via play_helper") will accidentally play simultaneous games as alternating games, getting completely different dynamics (no collisions, move-order matters, effective board state diverges by R2). **The prompt says "both players' moves must be submitted in the same play_helper invocation. The engine resolves collisions (same cell → both stones annihilate)" — this is ONLY true through `step_simultaneous`, which play_helper does NOT expose.** Recommendation: either (a) extend play_helper with a `--rounds "a1:b1,a2:b2,..."` mode that calls `step_simultaneous`, or (b) add a prominent note to the prompt pointing to `team18_sim_helper.py` (or equivalent) as the required tool for simultaneous games. Without this fix, R15 evaluations of the 10 pure-simultaneous top-20 games will be systematically wrong.

2. **Threshold win-condition check-order bias** (`engine_v2.py:_check_threshold` line 748-761 iterates player 1 first). This is a real engine behavior. Teams evaluating simultaneous threshold games should be explicitly told to test symmetric-tie scenarios, because the bias is a game-quality signal that's easy to miss if you only play asymmetric games. Recommendation: add a Phase-1 checklist item "for simultaneous threshold games, verify whether P1 has a tie-break advantage by simulating symmetric identical-strategy play".

3. **Double-pass draw is straightforward** — the rule change is in effect and works as documented. In my 3 games none ended by double-pass, but I explicitly verified (P1=27, P2=63, then P1=pass, P2=pass → draw, step_count=2). No ambiguity for teams.

4. **New seat-balance metric.** I can confirm this game exhibits seat imbalance (P1 wins all 3 games I played, including seat-swap Game 3). The GE champion having a structural P1 bias is itself a signal — either the new seat-balance metric didn't catch this, or it did catch it but the other axes scored high enough to keep the game as champion anyway. Worth investigating whether the seat-balance probe tested deterministic tie scenarios.

5. **Prompt ambiguity on "seat swap" for a single-agent pilot.** Phase 2 says "whoever was Player 1 in games 1-2 should play Player 2 in game 3". When a single agent plays all three roles sequentially (as allowed), "swapping seats" is a notional reframe rather than a real identity change. I interpreted this as "the agent should now try P2's best strategy, not P1's" — which for this game means acknowledging that P2 has no winning line and trying spoilers. This is probably the right interpretation but it should be clarified in the prompt.

6. **`play_helper.py show`** correctly does not display the influence field (noted in the prompt). My wrapper adds `--show-values` which dumps `engine.board_values` — recommend including equivalent functionality in a production helper since threshold games are hard to reason about without the field.

7. **Time budget.** 25 minutes was comfortable for this evaluation (~20 minutes including helper authoring). Teams that start with a simultaneous game and don't have a helper ready should budget more time, or the prompt should pre-link them to `team18_sim_helper.py`.

### Summary for runner

- The eval prompt is generally sound for this game.
- **The #1 blocker is the play_helper ↔ simultaneous gap** — please patch before spawning production teams, or ~half the games will be misevaluated.
- The champion itself has a clear balance flaw (P1 advantage) that teams should find if they test symmetric play. Worth ensuring the prompt's Phase-3 "quantify first-mover advantage by seat-swap" instruction is followed rigorously.
