# R8 Replay Agent-Team Eval — team-4 — Game d4015a646ae3

**Team ID:** team-4
**Game ID:** d4015a646ae3 (R8 top-1 by ELO 2304.6, GE 0.386, depth 0.545, ND 0.825, R8 Feb-2026 rating 8/10)
**Substrate:** grid (axis 8, 64 active / 64 grid positions, max_degree 4, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game d4015a646ae3 --db genesis_v2_run8.db` (see `briefing_r8_d4015a646ae3.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid — 64 active cells of 64 grid positions (no holes). Cell index = `y*8 + x`. Interior cells have max_degree 4 (4 axial neighbours); edges have 3; corners have 2. Asymmetric face-connection goals require crossing chains.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100. No fallback decision rule for connection-win timeout — game ends without winner (draw).

**Action space.** 65 actions = 64 placement + 1 pass. No pie action. No move actions (place-only). Placement legal at any empty cell.

**Placement & capture.** Placement: empty cell anywhere, no first-move restriction. Capture rule = **surround** (threshold=3 in rule blob is **VESTIGIAL** — engine code at `engine_v2.py:606` ignores threshold and uses classical Go zero-liberties semantics). Verified empirically in adversarial probe: a P2 stone at (4,3) with neighbours (3,3)=X, (5,3)=X, (4,2)=X, (4,4)=empty was NOT captured (1 liberty); when P1 then played (4,4), the stone was cleared. Capture confirmation: `Captures (cleared to empty): ['(4,3)']` at turn 9 of probe.

**Propagation.** influence (radius=3, strength=0.7150, decay=0.7510). On placement at cell c, the engine adds ±0.715 to c itself, ±0.537 to direct neighbours (d=1), ±0.403 at d=2, ±0.303 at d=3. Sign = +1 if P1 places, -1 if P2. Clamped to [-100, 100]. **Influence is NOT the win condition** — it's a positional signal visible to PPO via `board_values` but only the connection-win matters for terminal classification.

**Win condition.** **Connection (Hex-style asymmetric goals).** First player to form a contiguous BFS-connected chain of their own stones from one face to the opposite face along their assigned dimension wins. `target_dimension=1` for P1; P2 gets dimension 0 by engine auto-assign. In coordinate terms:
- **P1 connects top↔bottom** (chain of P1 stones from y=0 to y=7).
- **P2 connects left↔right** (chain of P2 stones from x=0 to x=7).

The `threshold: 0.5` in `win_condition` is vestigial under connection-win (`topology.py:634` `connects_faces` BFS ignores it). The helper's `Win: threshold-race > 0.500` header line is hardcoded and **wrong** — verified empirically that "P1 effective score" can be +21 with `Done=True Winner=1` because connection completed, not threshold crossed.

**Pie rule.** **False.** R8 predates the pie-rule fix. First-mover advantage is uncompensated.

**Degeneracy check.**
- **Two vestigial parameters:** `capture_rule.threshold=3` is unused (engine ignores it). `win_condition.threshold=0.5` is unused under connection-win. These are dead fields visible to the GE evaluator and PPO but having no semantic effect — meaningful for novelty score (the rule blob looks richer than it plays).
- Grid has no holes. Edge / corner cells have reduced neighbour count (3 / 2). Corner cells cannot be surround-captured (only 2 neighbours = max 2 attackers, can't isolate liberty).
- Influence radius 3 on an 8×8 grid means **every cell is within influence range of every other cell** along one of the two axes — the kernel saturates the board. The decay (0.751) keeps falloff sharp but the geometry has no insulated cells.
- 8×8 is small for Hex-family games (diameter 8). Minimum-length winning chain is 8 stones.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 64.

### Game 1 — Edge-wall sanity demo (P1 x=0 column, P2 x=7 column)

Sequence: `0,7,8,15,16,23,24,31,32,39,40,47,48,55,56` (15 plies).

Plot:
- Both sides build pure straight walls. P1 wins at move 15 by completing x=0 column (y=0..y=7) = vertical = top-to-bottom connection.
- P2's parallel x=7 wall does NOT win — P2 needs horizontal (left↔right), not vertical. This is the asymmetric-goal "trap" for naive mirror play.
- No captures fire. No interaction. Pure tempo race.

Reflection: A naive mirror strategy by P2 is **strictly losing**. P2 must recognize their goal is orthogonal to P1's, and act on it. First strategic lesson the game teaches.

### Game 2 — P1 column-race, P2 row-race with contested cell (the "Hex intersection")

Sequence: `0,32,8,33,16,34,24,35,40,36,48,37,56,38,1,39` (16 plies).

Plot:
- Move 1: P1 plays (0,0), committing to column x=0.
- **Move 2: P2 plays (0,4)** — the contested cell where P1's column meets P2's chosen row y=4. P1's column will now have a gap.
- Moves 3-14: both build their respective lines. P1 fills (0,1)..(0,3) and (0,5)..(0,7); P2 fills (1,4)..(6,4).
- Move 15: P1 starts second column at (1,0) — too late, only 1 stone toward a new top↔bottom path.
- **Move 16: P2 plays (7,4) — Winner=2.** Complete row y=4 (x=0 to x=7) wins for P2.

Reflection: This is **the canonical Hex dynamic exposed**. The cell (0,4) at move 2 was decisive — whoever got it controlled their respective face-connection. P1 missed it by committing to column edge (x=0) without anticipating P2's row choice. P2 won despite moving second by playing the critical intersection.

### Game 3 — P1 centre-cluster, P2 row-race + blockade resistance

Sequence: `27,28,19,20,18,29,11,21,10,30,9,31,3,22,35,23,43,16,51,17,59` (21 plies).

Plot:
- Moves 1-12: P1 builds compact connected cluster centred on x=3 (stones at (3,3),(3,2),(2,2),(3,1),(2,1),(1,1)); P2 builds y=3 row at x=4,5,6,7.
- **Move 12: P2 has a 4-stone partial row at y=3** but blocked on the left by P1's (3,3). To bridge to x=0, P2 needs to detour through y=2 or y=4.
- Moves 13-15: P1 extends column at x=3 to (3,0) and (3,4); P2 tries detour through y=2 (places at (6,2),(7,2)).
- Move 18: P2 plays (0,2) to start a leftward y=2 detour. But P1 already occupies (2,2) AND (3,2), blocking the detour.
- Moves 19-21: P1 fills (3,5),(3,6),(3,7) to complete column x=3 = top↔bottom connection. **Winner=1 at move 21.**
- No captures fired throughout.

### Game 4 — Adversarial probe: verify surround capture mechanics

Sequence: `27,28,19,11,29,3,20,12,36` (9 plies). P1 deliberately surrounds a P2 stone.

Plot:
- P1 plays a "+" around the centre cell (3,3) with extensions to attempt to isolate P2 at (4,3).
- After move 7, P2 stone (4,3) has 3 of 4 neighbours = P1 ((3,3),(5,3),(4,2)) and 1 liberty at (4,4).
- Move 8: P2 plays (4,1) (not at (4,4)).
- **Move 9: P1 plays (4,4) — `Captures (cleared to empty): ['(4,3)']` fires.** P2 piece count 4→3.

Reflection: Captures DO work, but the **cost-benefit is awful for the attacker** in connection-win. P1 spent 4 stones (3,3)(5,3)(4,2)(4,4) to remove 1 P2 stone. In Hex-family races, every stone is worth a turn of progress toward connection — sacrificing 4 turns to remove 1 enemy turn is heavy negative-EV unless the captured stone was critical to a connection path. Captures matter most when the attacker's 4 stones happen to already lie on the attacker's own connection path AND the captured stone was blocking a contested intersection. This is plausible but rare.

### Game 5 — Surround attempt fails (cluster too small for true isolation)

In Game 5 of my exploration (truncated sequence not shown in detail), I attempted to surround a P2 chain. The surround required cells to fully encircle, and in mid-game the connection paths between P1's own stones meant my "surround" stones were always on my own connection path anyway. **Captures opportunistically integrate with connection-build** — this is the subtle interaction between the two mechanics.

### Strategy guides

**P1 (offence/connection-build):** Centre placement at (3,3) maintains flexibility — P1 hasn't committed to which column to extend yet. Then build a compact connected group around the centre, choosing the bridging axis based on P2's response. Surround captures are bonus, not primary. KEY: never let your column have a gap that P2 can plug; KEY: P2's row crosses every cell of your column — anticipate which cell P2 wants.

**P2 (defence + own-row):** **Critical move-2 decision** — play the intersection cell of P1's likely column with your chosen row. If P1 opens at (0,0), play (0,4) or similar — claim a cell on P1's column. From there, race to complete your row while detouring around any further P1 blockade. The first-move disadvantage is real but partially correctable by claiming P1's chosen column.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, at least 3 with real tradeoffs:
1. **Edge-wall** (Game 1 demo) — fastest path but predictable; vulnerable to a P2 cell-block at the intersection (Game 2).
2. **Centre-cluster** (Game 5) — slow build but maintains flexibility about which column/row to commit to, and naturally blocks any opposing row through the cluster.
3. **Contested-intersection grab** (Game 2's P2 winning move) — playing on the opponent's chosen line to forcibly block their connection.

A fourth — **surround-capture pressure** — exists in principle but in my play never determined a game outcome.

**Counter-play.** Real, not artificial. The Game 2 result (P2 winning despite second-mover) shows that the first-mover advantage is not insurmountable — careful blocking can flip the outcome. **The pie rule's absence is felt but does not make the game one-sided in practice.** P2 needs more skill but has winning lines.

**Short-term vs long-term.** Tactical depth is shallow — moves typically have 2-4 candidates. Strategic depth is substantial — the choice of WHICH column/row to commit to and WHICH cells of the opponent's likely line to claim is medium-term planning over 8-12 plies. Game length is typically 14-21 plies (in my samples, all 15-21).

**Emergent concepts observed.**
- **Connection blockade** (Game 3). P1's column naturally blocks P2's row at the intersection cell. The asymmetric goals force one critical contested cell.
- **Detour cost.** When P2 is blocked on y=3, the detour through y=2 needs additional cells. Each blockade forces ~3 additional moves of detour — a major tempo cost.
- **Capture as side-channel.** Captures don't win directly but can disrupt a connection chain mid-build (verified in Game 4). In principle, P2 could capture a critical P1 stone on the column to reopen a path.
- **First-mover x intersection-claim trade.** P2 trades their second-move position for the right to choose WHICH cell of P1's likely line to claim. This is genuinely interesting strategic asymmetry.

**Does the 8×8 grid matter?** Yes — the small size makes connection reachable in 8 plies, which makes the race tight and meaningful. On a 16×16 grid, connection would take 16+ plies and the influence kernel (r=3) would matter less geometrically. The 8×8 size is well-tuned for the rule set — it's small enough that captures bite (a single capture is 12.5% of the board) but big enough that detours exist.

**Does the propagation kernel matter?** Marginally for win-detection, since influence doesn't win the game. PPO sees board_values, so it shapes learned policy. But for human/agent strategic analysis the kernel is a distraction — the connection mechanic dominates. **Influence is vestigial-ish for terminal play but useful-ish for policy training.** Mixed grade.

**Capture-rule contribution.** Real but secondary. Captures fired in 1 of my 4 substantive games, deliberately set up. Under realistic play (Games 1, 2, 3) captures didn't trigger. They function as a **latent threat** — P2 cannot leave isolated stones in a P1 cluster, and vice versa. This is more than a vestigial rule but less than a primary mechanic.

**First-mover advantage / seat balance.** R8 era PPO reference: `trained_vs_random` 0.84 / 0.56 — P1 win rate vs random is substantially higher than P2 vs random, suggesting P1 advantage. But the gap is much smaller than the ~0.67 P1 WR in R20 menger games. In my games, P2 won 1 of 4 (the contested-intersection game). **Imbalance is present but smaller than in R20 corpus**, primarily because P2 has meaningful counter-play (intersection-block). Pie rule would help but is absent.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is **substantially a re-skin of Hex**. Argument:

(a) **Connection-win with asymmetric face goals** is the **defining structure of Hex** (invented 1942 by Piet Hein, independently 1948 by John Nash). Hex is played on a hexagonal grid; this game uses a square grid with axial (4-neighbour) connectivity. The replacement of hex tiling with square tiling is a **structurally minor change** — square + 4-neighbours still gives proper BFS-face-connection semantics, though hex's "no draw" property is weakened (square boards CAN have face-disconnecting partitions that hex cannot).

(b) **Surround capture** is the **defining structure of Go** (developed in ancient China, ~2000+ years). The engine implementation is precisely classical Go zero-liberties capture. R8's surround rule = Go rule. No novelty here.

(c) **Influence propagation** is **NOT a Go or Hex feature** but appears in: Reversi/Othello (positional weighting), Pente (influence radius implicit), neural-network Go bots (learned influence). As a hand-coded rule it appears in the engine's r/strength/decay parameterisation. **Within Genesis history**, influence + capture combos are present throughout R8-R20. Modest novelty.

(d) **The combination "surround capture + influence + Hex-style connection-win on a square grid"** — does this exist as a published game? Searched mental literature: closest analog is **"Crossings" / "Epaminondas"** (square grid, asymmetric goals, no capture) or **"Twixt"** (connection on grid with bridges, no influence). The specific combo **Hex + Go on square grid** has been proposed informally in board-game variant literature ("Hexgo") but never published as a major game. Within Genesis, this is R8's distinctive contribution — R20 production has no connection-win games. So: **mild novelty within the corpus, significant familiarity outside.**

(e) **Expert-transfer test.** A Hex + Go player understands this game in **5 minutes**. Irreducible new pieces they'd have to learn:
   - "Connection win uses 4-neighbour square BFS instead of hex" (trivial)
   - "Stones can be captured by Go-style surround" (familiar from Go)
   - "Captured chains can no longer participate in connection" (the interesting interaction)
   - "Influence accumulates but doesn't win" (cosmetic distraction, vestigial for human play)

The unique interaction is **"capture mid-chain to sever a connection"** — this exists nowhere in pure Hex (Hex has no captures) and nowhere in pure Go (Go has no face-connection goal). **This combination is genuinely emergent.** But: in my 4 substantive games, the sever-by-capture tactic never determined a result. It's a latent depth that may not manifest in agent play.

**Closest known-game analogue:** **Hex** (Piet Hein / Nash, 1942/48) — same asymmetric face-connection structure. Augmented with **Go's surround capture** as a side mechanic. Approximation: "Hex on a square grid with Go captures and an unused influence field."

**Comparison to R20 production.** R20 was outnumber-2 + influence + **threshold-race** on menger/carpet/grid. R20 has **no connection-win games** — every R20 production game is a threshold-race. R8's Connection Go is therefore in a **different rule family entirely** from R20 production. This makes direct comparison hard, but qualitatively: connection-win imposes a binary terminal condition tied to global structure (chain of stones forming a topological path), whereas threshold-race imposes a continuous accumulator. **Connection-win is structurally richer** — global topology > local accumulation — and this is the source of R8's depth advantage.

**Comparison to R19 menger top.** R19 top was `1f9191b5d4e6` outnumber-2 menger, 4.8/10 (threshold-race + capture + 3D substrate). R19 had no connection-win games either. R8's Connection Go is **definitionally richer** because the win condition itself encodes more strategic structure. But R8's `0.386` GE is below R19 top's GE — engine-measured fitness disagrees with structural richness. **This is the calibration drift hypothesis confirmed: R8's connection-Go wins on structural depth but loses on GE because GE doesn't reward connection-win structure.**

**Player rebuttal (P1 + P2).**
- The **capture-mid-chain** interaction is real and absent in any single ancestor. Hex has permanent stones; Go has no connection goal. The combination forces a defensive consideration in connection planning — every stone of yours could potentially be captured and severed. In my Game 4 probe, a chain of 4 P1 stones was reduced by 1; in a longer game, this could split a near-connection.
- The **intersection-claim** dynamic (Game 2) — P2 won by claiming (0,4) — is exactly Hex's strategy but with the square-grid 4-neighbour topology making it slightly cleaner than hex's 6-neighbour version. Not novel vs. Hex but well-executed.
- **Subtractions to novelty:**
  - `capture_rule.threshold=3` is **vestigial** (engine ignores it).
  - `win_condition.threshold=0.5` is **vestigial** (BFS ignores it).
  - Influence (r=3 decay 0.751) is **largely cosmetic** for terminal play — it shapes PPO observation but is not part of the win condition. A human/agent strategic analysis can ignore it almost entirely.
- The rule blob LOOKS richer than the game PLAYS — three of the five rule blocks (capture-threshold, win-threshold, influence) are partially or fully ignored by the engine for win-detection.

**Novelty score (post-adversary):** **5.0/10.** Above Hex re-skin (3-4) because of the genuine capture-mid-chain interaction layered onto the connection-win structure. Below "genuinely new" (8-9) because the dominant mechanic (face-connection) is Hex's defining contribution and the secondary mechanic (surround) is Go's. Within Genesis it's distinctive (no R20 game uses connection-win); within published board-game literature it's Hex+Go, a well-known if unfielded variant. Anchored against R17 mean (3.5) and R19 menger top (4.8) — slightly above R19 top because connection-win is structurally richer than threshold-race.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** d4015a646ae3
**Rules Summary:** Hex with asymmetric face-connection goals (P1 top↔bottom, P2 left↔right) on a flat 8×8 square grid (4-neighbour), augmented with Go-style surround capture and a vestigial influence field. Connection-win is decisive; influence and capture-threshold are partially or wholly ignored.
**Substrate:** grid, axis 8, 64/64 cells, max_degree 4, pie_rule=False.
**Turn Structure:** alternating, 1 piece/turn, max 100 plies.
**Hybrid actions:** no (place-only).
**Soft violations flagged:** Two vestigial parameters (`capture_rule.threshold=3` and `win_condition.threshold=0.5`). Pie rule absent — first-mover advantage uncompensated. Influence kernel mostly cosmetic for terminal play.

### Scores (1–10)

- **Strategic Depth: 6** — Real medium-term planning over 8-12 plies for cell-intersection control, chain build, and detour cost. Multiple distinct viable strategies (edge-wall, centre-cluster, intersection-grab). Above R20 top (4.80) because the connection-win imposes global-topology planning that threshold-race does not. Below 7+ because the 8×8 board diameter (8) is small and games resolve quickly; tactical decision branching at each ply is moderate (~3-5 meaningful candidates). The engine-measured 0.545 depth understates this — the game is deeper than R20 top empirically.

- **Emergent Complexity: 6** — Connection blockade, detour cost, capture-mid-chain sever, intersection-claim — these are genuinely emergent patterns from the rule combination. Above R20 production (which is mostly "cluster build for influence"). Below 8+ because the depth ceiling is bounded by Hex's known theory plus a moderate Go-flavour addition; this is not a wildly inventive game, it's a clean combination.

- **Balance: 5** — Pie rule absent. R8 PPO reference shows P1 vs random 0.84, P2 vs random 0.56 — non-trivial first-mover advantage. BUT in my play P2 won 1 of 4 (Game 2), and the intersection-claim strategy gives P2 real counter-play. The imbalance is much smaller than R20 menger's 0.667. Penalised below 6 because pie absence is a structural problem; raised above 4 because counter-play exists.

- **Novelty (post-adversary): 5** — See Phase 4. Hex re-skin on a square grid + Go capture + vestigial influence. Above R19 top (4.8) because the capture-mid-chain interaction adds genuine depth not in any single ancestor; below 7+ because the dominant Hex+Go pairing is well-known.

- **Replayability: 5** — Once the intersection-grab and centre-cluster strategies are public, openings narrow. ~3-4 distinct viable opening trees per side. The asymmetric goals do force exploration of WHICH column/row each player commits to, giving genuine position variety. Game length 14-21 plies in my samples — short enough to encourage replay, long enough to feel substantive. Above R20 (which has ~85-ply grinds) because the connection-win drives early decisive play.

- **Overall "Would an agent team play this again?": 5.5** — Yes, agents would play this again to explore the capture-mid-chain dynamic and verify the intersection-claim counter-strategy. It's the best game in the project corpus I've encountered (above R19 menger top 4.8 and R20 top 4.80). But it's NOT 8/10. **The R8 February 8/10 rating appears inflated** under current rubric, possibly because R8-era evaluators valued connection-win novelty highly without applying the standard depth/balance/novelty decomposition. Under current rubric: depth 6, complexity 6, balance 5, novelty 5, replay 5 → overall ~5.5. Calibration drift detected.

  Anchors: R8 = 8 (clearly overstated), R17 mean = 3.5 (well above), R19 menger top = 4.8 (slightly above), R20 production mean = 3.73 (well above), R20 top = 4.80 (slightly above).

### CLOSEST KNOWN-GAME ANALOG

**Hex** (Piet Hein, 1942; John Nash, 1948) — same face-connection structure with asymmetric goals. This game is Hex on a square grid with Go-style surround capture added and a vestigial influence field. Within the Genesis corpus, no R20 game uses connection-win, making this the only connection-win game in scope; the closest Genesis lineage is its own R8 parent `14be6193ffc7`.

### KILLER FLAWS

- **Two vestigial parameters in the rule blob.** `capture_rule.threshold=3` is **ignored by the engine** — surround capture uses classical Go zero-liberties semantics (`engine_v2.py:606-620`), not a 3-neighbour count threshold as the briefing speculated. `win_condition.threshold=0.5` is **ignored under connection-win** (`topology.py:634`). The rule blob looks richer than the game plays. A GE evaluator that scores rule density is rewarding fields the engine doesn't use.

- **Pie rule absent.** R8 predates the pie fix. P1 advantage of 0.84 vs random vs P2's 0.56 vs random is non-trivial. Pie would correct this in one parameter flip.

- **Influence is cosmetic for terminal play.** Influence shapes PPO observations but the win condition is BFS-face-connection, ignoring `board_values` entirely. A human or agent strategic analyst can mentally drop the entire propagation kernel and lose nothing about win-detection. The kernel exists for policy-training reasons, but for "what does this game play like" it's nearly inert.

- **8×8 is small.** Diameter 8, minimum winning chain 8 stones. Games resolve in 14-21 plies. Strategic horizons are limited compared to a 11×11 or 13×13 Hex board (the published standard). A R8-era choice to keep axis=8 keeps GE training cheap but caps depth.

- **Capture cost-benefit is heavily attacker-negative.** Verified in Game 4: P1 spent 4 stones to capture 1 P2 stone. In a connection-race where every stone is one turn of progress toward win, this 4-for-1 trade is almost never worth it unless the captured stone was on a critical contested cell. Captures therefore rarely fire in optimal play — verified across Games 1, 2, 3, 5 (zero captures under non-adversarial play).

### BEST QUALITY

The **capture-mid-chain sever as a latent threat** is the crown jewel. In Hex, every stone is permanent — once placed, it's a guaranteed link in any future chain. Here, a P1 stone with 3 P1 friends and 1 liberty can be captured by P2 plugging the liberty. This means **connection planning must consider liberty defence** — a Go-Hex hybrid concept that does not exist in either ancestor alone. In my 4 substantive games, this threat shaped play even when captures didn't fire — the centre-cluster strategy (Game 5) was partly motivated by ensuring P1's column-build stones had ample liberty. **This is real emergent depth from the rule combination**, and is the reason the game scores 5.5 rather than 4.5.

### GRID STRUCTURAL CONTRIBUTION

Minimal but appropriate. The 8×8 flat grid gives 4-neighbour BFS-face-connection that approximates Hex's 6-neighbour version. A hex tiling would be more elegant (no draws possible, classic theory transfer) but a square grid is what the engine supports. The substrate is **vehicle, not contributor** — the game's depth comes from the rules, not the topology. A 9×9 carpet or 9×9×9 menger version with the same rules would likely play similarly but slower (more cells to fill to bridge faces).

### IMPROVEMENT IDEAS

**Single best change:** **Add the pie rule.** Standard Hex remedy for first-mover advantage. The 0.84 vs 0.56 trained_vs_random asymmetry is uncorrected and is the headline structural flaw. The fix is one parameter flip and is a known-good intervention from Hex theory.

Secondary improvements:
- **Remove vestigial parameters from the rule blob.** Either make `capture_rule.threshold=3` actually do something (e.g., switch to outnumber-3 semantics so threshold matters) OR delete it. Either make `win_condition.threshold=0.5` matter (e.g., require connection AND threshold) OR delete it. Cleaner rule = cleaner GE signal.
- **Move to 11×11 grid.** Standard Hex tournament size. Doubles game length and substantially increases strategic horizon. R8's GE training cost may have been the original blocker but the project has grown.
- **Replace influence kernel with something the win-condition uses.** If influence stays cosmetic, the rule blob misrepresents the game's complexity to the GE evaluator. Either tie influence to capture probability (e.g., a stone with influence > threshold can't be captured) OR remove the field entirely. The latter is the cleaner option for an already-rich rule set.
- **Score chain-defending tactics explicitly in GE.** R8's 0.545 depth metric understates the game's actual depth empirically (5.5/10 agent eval > the 4.8 R19 menger top with depth 0.79). GE under-rewards connection-win structure relative to threshold-race structure — this is the calibration drift the campaign is trying to detect.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/r8_replay/team-4_game_d4015a646ae3.md`.*
