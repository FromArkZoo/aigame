# Run 20 Agent-Team Eval — team-1 — Game fcedbc14043d

**Team ID:** team-1
**Game ID:** fcedbc14043d (grid_control top-1, 15-seed mean GE 0.129, σ 0.046, depth 0.593)
**Substrate:** flat 2D grid (axis 9, 81 active cells / 81 grid positions, max_degree 4, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game fcedbc14043d` (see `briefing_grid_fcedbc14043d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 9×9 grid, 81 active cells (no holes). Cell index = y·9 + x. Max_degree 4 for interior cells.

**Turn structure.** Alternating, 1 piece/turn. P1 first. **Max_turns = 72** (shortest in slate).

**Action space.** 82 actions = 81 cells + 1 pass. Place-only.

**Placement & capture.** Capture = **custodian-2** (the *only* slate game with custodian; other 6 use outnumber). When a stone is placed at `c`, the engine walks each axis outward from `c`; if a contiguous run of enemy stones is bracketed by the placer's stone (one being `c`, one being further along the axis), the entire enemy run **flips** to the placer (not cleared — this is Othello-style).

**Threshold parameter = 2** is documented as "minimum bracket length" but the empirical test (`36,37,38` = P1 (0,4), P2 (1,4), P1 (2,4)) shows that **single-stone brackets DO fire**: P2's lone (1,4) flipped to P1 on move 3. The "threshold = 2" appears to be the lower-bound semantics (a 2-stone bracket is the minimum for any flip; what matters is the bracket walk needs ≥1 enemy stone in between). Briefing's R19 carpet rank-2 lesson confirmed.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5).

**Win condition.** Threshold-race > **20.0** (lower than carpet's 30 and menger's 58). Briefing claims `target_dimension_p2 = +1` gives a "separate accumulator" — but the engine's `_check_threshold` always uses the `+sum / -sum` convention (P1 sums own values, P2 negates). The `target_dimension_p2` parameter is only consulted for connection-wins, not threshold-races. **So the briefing's claim about a "separate accumulator" is incorrect** — this game uses the same mirror-score convention as menger/carpet.

**Pie rule.** Off.

**Degeneracy check.**
- Custodian capture is *equilibrium-vestigial*: like outnumber-2 in menger, custodian-2 only fires when one side voluntarily places between two enemy stones (suicide). In cluster-vs-cluster equilibrium, no captures fire. Verified across 3 games below.
- The "fires only on placer" semantics means a stone placed *between* two existing enemy stones does **not** trigger custodian (it's the placer's bracket, not the existing flank). Once a stone settles in a sandwich position, it's permanent (until the board fills).
- Custodian fundamentally constrains *placement order*: P2 cannot place at (1,0) if P1 has both (0,0) and (2,0) — that placement would be captured. But P2 CAN place at (1,0) before P1 completes the flank (then P2 is sandwiched but not captured). The strategic content is "race to the cell."

---

## Phase 2 — Strategic Play

All moves engine-verified.

### Game 1 — P1 corner cluster vs P2 mirror cluster

Sequence (17 plies, P1 wins):
`0,80,1,79,9,71,2,78,10,70,18,62,11,69,19,61,20,60`.

Plot:
- P1 fills (0..2, 0..2) cluster; P2 mirrors at (6..8, 6..8). 
- At move 16: P1=+18, P2=+18.
- **Move 17 P1 plays `(2,2)=20`** Δ+3 (compounds with `(1,2), (2,1)` already-owned, gets +0.5 from each). **P1 score → +21 ≥ 20 → P1 wins by +3.**

Final: P1=+21, P2=+18.

No captures fired. Cluster-vs-cluster on flat grid with no holes; both sides build symmetrically.

### Game 2 — P1 center cluster spreading outward

Sequence (21 plies, P1 wins):
`40,42,30,32,21,23,12,14,11,15,3,5,4,6,13,7,22,8,31,17,49`.

Plot:
- P1 plays `(4,4)=40`. P2 plays `(6,4)=42` next to P1's center? Strange but let me trace.
- Both build crosses through middle rows. By move 8 both at +6.
- Move 13 P1 plays `(4,0)=4` — top row entry. P2 plays `(6,0)=6`. Both expand vertically.
- Through move 19 both nearing threshold. P1 places `(4,3)=31` Δ+3 → +20.0 (NOT win — strict >).
- Move 20 P2 plays `(8,1)=17`. Move 21 P1 plays `(4,5)=49` Δ+2 → +22.0. **P1 wins by +5.**

This game shows the flat-grid centre-vs-mirror dynamic: clusters grow toward each other, but the threshold is hit before they actually meet (~21 plies vs the ~30 plies it would take to fill the middle 3 rows). **No captures fired.**

### Game 3 — Custodian capture test (single-stone bracket verification)

Sequence (4 plies, capture verified):
`0,1,2,9`.

Plot:
- Move 1: P1 `(0,0)`.
- Move 2: P2 `(1,0)` — placing between P1's (0,0) and... wait, P1 has only (0,0) at this point. P2's placement at (1,0) does *not* immediately get captured (P2 isn't bracketed yet).
- **Move 3: P1 `(2,0)` — completes the bracket. Custodian fires; (1,0) flips to P1.** Engine output: `Captures (flipped owner): ['(1,0)']`. P1 piece count 1→3 in one move (gained the flipped stone).

Confirms custodian-2 fires on single-stone brackets. The trick: P2's voluntary placement at (1,0) was *suicidal* — P1 had only (0,0) at the time, but P2 still placed at the obvious bracket-candidate cell. PPO would never do this; humans wouldn't either.

### Strategy guides

**P1 (offence/threshold push):** Open at any cell — corner is fine, centre is fine. The flat grid has no degree-disparity to exploit. Build cluster greedily; ignore P2 (no capture risk in cluster-vs-cluster). Threshold 20 in ~17–22 plies depending on cluster shape.

**P2 (defence + threshold contest):** Mirror cluster from opposite corner. Don't place at suicidal bracket-completion cells (basic defence). The custodian rule constrains placement order but doesn't generate counter-strategies because the rule is symmetric and equilibrium clusters never bracket each other.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **One: corner or centre cluster.** The custodian rule constrains some placements but doesn't create distinct strategies (no equivalent of menger's wrap-capture or carpet's pie-decision).

**Counter-play.** **Effectively absent.** Cluster-vs-cluster, P1 wins by tempo +3–5 in 17–21 plies.

**Short-term vs long-term.** Tactical horizon = 1–2 plies (avoid suicide placements + greedy Δ). Strategic horizon = 0 ply (cluster choice is move 1).

**Emergent concepts observed.**
- **Cluster compounding** (same as siblings).
- **Bracket-suicide avoidance** — P2 must avoid placing at cells flanked by 1+ P1 stone with another P1 stone 2+ cells along the axis. This is a real constraint but doesn't generate strategy.
- I did **not** observe captures in equilibrium play; only the contrived `0,1,2` sequence (Game 3) fires the rule.

**Does flat grid matter?** **Compared to menger:** flat grid removes the corner-cluster-disjoint problem — clusters could meet in the middle if the game were longer. But threshold 20 ends games before clusters grow into each other. **Compared to carpet:** flat grid is similar but without the central hole. **Compared to R8:** R8 had custodian + connection on flat grid — same substrate, same capture rule, but R8's connection-win forced global plan, generating depth that this game's threshold-race doesn't.

**Does the propagation kernel matter?** Same as menger r=1: cluster compounding is the only knob.

**Capture-rule contribution.** **Zero in equilibrium.** Custodian fires only on adversarial probes (Game 3). PPO learns to avoid bracket-suicide, then plays cluster-vs-cluster.

**First-mover advantage / seat balance.** P1 wins both Games 1 and 2 by +3–5. PPO trained-vs-trained 0.500 (3 runs) suggests balance, but 3 runs is too few for confidence. Pie rule off, no compensation.

**Why does this game measure depth 0.593 (lowest in slate)?** Because the engine measures depth via PPO seed variance + game length, both of which are minimised here: 22-ply games are short (vs 85 for menger), and 3 PPO runs all converge to similar play (cluster-vs-cluster). **This is the game where engine depth tracks subjective depth correctly** — it's a shallow game and the metric agrees.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a **direct cousin of R8 Connection Go** with one rule change:

(a) **Threshold-race influence games on flat grid** — niche but documented; this is essentially Octopus's Garden with smaller numbers.

(b) **Custodian-2 capture** — Othello/Reversi family. Specifically the *flip* (not remove) variant.

(c) **The combination "custodian + influence + threshold-race" on flat grid** — the closest direct analogue is **R8's `9d33eee27c66`** (custodian + connection + flat grid). The only difference is win condition: R8 uses connection, this uses threshold-race.

(d) **Flat 9×9 grid substrate** — the most common board-game shape. Not novel.

(e) **Expert-transfer test.** A Reversi player + Octopus's Garden player would understand this game in **~2 minutes**. The custodian rule is identical to Othello (with a smaller minimum bracket); the threshold-race is straightforward.

**Closest known-game analogue:** **R8's `9d33eee27c66`** (Connection Go, 2D flat grid, custodian + connection) — this game is structurally the *same recipe minus the connection-win requirement*. It is also closely related to **published Reversi** with a numerical end-condition.

**Comparison to R8's Connection Go (8/10 ceiling).** **R8 is the direct ancestor.** R8 had custodian + connection on flat grid; this game has custodian + threshold-race on flat grid. The win-condition swap is the only delta. **R8 wins on depth** because connection-win forces global plan; threshold-race rewards local cluster compounding. R8's custodian-bridge-completes-chain mechanic is the crown jewel; this game's threshold-race has no such payoff. **This game is R8 with the depth removed.**

**Comparison to R19 best.** R19's grid_control category was generally weak. R19 menger top (4.8) and R19 carpet top (4.4) outperformed R19 grid_control. This R20 grid game is at the same level (~4) as R19's grid_control entries.

**Player rebuttal (P1 + P2).**
- The custodian rule is real but vestigial in equilibrium (same as menger outnumber).
- The flat grid prevents the menger-style cluster fragmentation, but threshold 20 ends games before clusters meet.
- **The R8-revival negative finding holds: even on flat grid with custodian, evolution dropped connection within 4 generations.** This game's gen-3 mutation switched away from connection — and it scored 0.214 in production while connection-seeded games scored ~0. The fitness function does not reward connection-wins on the menger/carpet/grid topologies in R20.
- Subtractor: short threshold + flat grid + no holes = the simplest game in slate, with the least substrate-rule fit.

**Novelty score (post-adversary):** **3/10.** Same as menger siblings. Custodian + threshold-race on flat grid is a near-Othello variant; the main novelty (vs R8) is a *negative* — they removed the connection-win that gave R8 its depth.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** fcedbc14043d
**Rules Summary:** Flat 9×9 grid; alternating placement; custodian-2 captures (single-stone bracket flips Othello-style); influence (r=1) deposits ±1 self / ±0.5 nbr. First to total-owned-influence > 20.0 wins. Closest to R8 `9d33eee27c66` minus connection-win requirement.
**Substrate:** flat grid, axis 9, 81/81 cells, max_degree 4, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no
**Soft violations flagged:** the briefing's claim about `target_dimension_p2 = +1` giving a "separate accumulator" is incorrect — the engine's `_check_threshold` uses the standard mirror-sum convention regardless of `target_dimension_p2`.

### Scores (1–10)

- **Strategic Depth: 3** — Single-strategy cluster game. Custodian rule constrains placements but doesn't generate counter-strategies. Engine depth 0.593 (lowest in slate) tracks subjective depth correctly here.
- **Emergent Complexity: 3** — Cluster compounding + bracket-suicide avoidance. Two simple emergent concepts; nothing analogous to menger's wrap-capture or carpet's pie-decision.
- **Balance: 5** — PPO 0.500 over 3 runs is the briefing's headline but 3 runs is below the noise floor. My games show P1 wins by +3–5; the structural P1 advantage is real but smaller than menger (which is +6–15).
- **Novelty (post-adversary): 3** — see Phase 4. Custodian + threshold-race on flat grid is R8 minus the connection-win. **The R20 grid_control negative finding** ("R8-revival failed") is concentrated in this game — evolution dropped connection within 4 gens, leaving a depth-poor cousin of R8.
- **Replayability: 3** — Single strategy. Short games (17–22 plies) leave little room for variation.
- **Overall "Would an agent team play this again?": 3** — On par with menger siblings. Anchored against R17 best (4.14) — slightly below because at least R17 had connection-win generating depth. Anchored against R19 menger top (4.8) — well below.

### CLOSEST KNOWN-GAME ANALOG
**R8's `9d33eee27c66`** (Connection Go, 2D flat grid, custodian + connection) — this game is the same recipe with connection-win replaced by threshold-race. Inside this project, the most direct R8-cousin in the slate. Outside this project, **Othello/Reversi with a numerical end condition** (early wins via influence accumulation rather than disc count).

### KILLER FLAWS
- **R8 minus connection-win = R8 minus depth.** Connection-win forced global plan in R8; threshold-race rewards local cluster compounding. The win-condition swap removed the depth-generating mechanic and left the substrate + capture rule isolated. This game is the **R20 grid_control negative finding personified**.
- **Custodian rule is equilibrium-vestigial.** Same as menger outnumber: the rule constrains placement but doesn't generate counter-strategies in cluster-vs-cluster play.
- **Briefing's `target_dimension_p2 = +1` claim is wrong.** The engine ignores this for threshold-race wins; both players use mirror-score regardless. Documentation drift.
- **Only 4 generations of evolution.** This is a pre-launch axis-reduction control, not a fully-evolved champion. Not directly comparable to menger/carpet which had 8 gens.
- **Flat grid + no holes + small threshold + no pie + no connection.** All the depth-generating features are absent.

### BEST QUALITY
The **direct geometric link to R8's Connection Go** is the game's only genuine value — as a control sample for testing whether connection-win or substrate-rule fit was the missing piece. The clean answer (this game scored 0.214 in production while connection-seeded games scored ~0) confirms that **fitness rewards the threshold-race + outnumber/custodian recipe over connection-wins in R20**, but agent verdicts confirm this is actually a *worse* recipe for play quality.

### GRID STRUCTURAL CONTRIBUTION
**Net positive vs menger, net wash vs carpet.** Flat grid removes menger's cluster-disjoint problem (clusters could in principle meet in the middle) but the short threshold (20) ends games before they actually meet. Compared to R19's "menger > carpet > grid" finding, **this game's grid is at the bottom for *play quality* but at the top for *agent comprehensibility*** — it's the cleanest and simplest game in the slate. **Same rules on a hex topology** would generate more structural variety.

### IMPROVEMENT IDEAS
**Single best change:** **restore the connection-win condition.** The parent `f233c2d817de` was a connection-win game; the gen-3 mutation switched to threshold-race. Reverting this single change would convert this game into a direct R8 sibling, recovering the chain-completion depth that custodian-bridge enables. The only reason evolution dropped connection is that the GE fitness function over-rewards threshold-race; **fix the fitness function**, not the game.

Secondary improvements:
- Enable pie rule (correct first-mover bias).
- Larger axis (12 instead of 9) to extend medium-term planning.
- Use `target_dimension_p2 = +1` for *connection wins* (asymmetric goals = R8-style P1-z-axis P2-x-axis).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-1_gamefcedbc14043d.md`.*
