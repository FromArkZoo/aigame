# Run 19 Evaluation — team-pilot — Game b48208268f2a

**Team ID:** team-pilot
**Game ID:** `b48208268f2a` (Carpet rank-2, GE 0.3069, ELO 2255.7)
**Substrate:** Sierpinski carpet (axis 9, 64/81 active, max_degree 4)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game b48208268f2a`

---

## Phase 1 — Rule Comprehension

**Board.** Identical to carpet rank-1: 9×9 grid with 17 holes (level-2 Sierpinski carpet), 64 active cells, max_degree 4, cell index = y·9 + x.

**Turn structure.** Alternating, P1 first. Max 100 turns.

**Action space.** 82 actions = 81 placements + 1 pass. Place-only.

**Capture (custodian-2).** When you place a stone, walk axis-aligned outward in each of 4 directions. If the walk encounters a contiguous run of **at least 2 enemy stones** terminated by a friendly stone, the run flips to the placer's colour. Walks stop at boundary or empty/own. **Flipped stones change owner — they are not removed**. This is the key difference from carpet rank-1's outnumber-2.

**Propagation (influence, r=2, s=1.0, d=0.5).** Identical to carpet rank-1.

**Win (threshold-race > 30.0).** Identical to carpet rank-1.

**Degeneracy check.**
- No soft-rule violations flagged.
- Custodian threshold = 2 means walks with 0 or 1 enemy stones don't fire. Single-enemy bracket (P1-P2-P1) does NOT capture under this rule (despite typical custodian definitions). Tested empirically: `0,9,18` does flip — actually it does, the engine's "threshold" in capture_rule is min run length = 1.

**(empirical correction)**: Tested by playing P1 at (0,0), P2 at (0,1), P1 at (0,2) — the single P2 stone at (0,1) IS flipped. So `threshold=2` here means something different from "minimum run length 2". Likely it's a misnamed knob from the rule schema; effective behaviour is standard custodian (any nonempty run of enemy bracketed by friendly flips).

---

## Phase 2 — Strategic Play

### Game 1 — Symmetric corner-cluster mirror

Sequence: `0,8,2,6,18,26,20,24,1,7,9,17,11,15,19,25` (16 plies).

Plot:
- Same opening as carpet rank-1: both build 8-stone corner clusters mirrored across the centre.
- Move 16: both at +20.0 with 8 stones each. **P1 will win on the next 2-3 moves to threshold by tempo**, just as in carpet rank-1.

Reflection: **Same mirror = P1 win as carpet rank-1.** Custodian doesn't fire under symmetric play because no stone is bracketed (each side's cluster is one solid colour). Tempo race favours P1.

### Game 2 — Custodian flip on column

Sequence: `0,9,18,27,2,11,20,29` (8 plies).

Plot:
- P1 (0,0); P2 (0,1) — P2 places adjacent.
- **P1 (0,2): custodian flip of (0,1).** P1 brackets P2's stone {P1@(0,0), P2@(0,1), P1@(0,2)}, walking +y. The 1-stone P2 run flips to P1. **P1 went from 1 stone to 3 stones in one move**; P2 from 1 to 0. Score: P1 = +1.5, P2 = 0.
- P2 (0,3) — recovery attempt. P2 walks -y from (0,3): finds P1 (formerly P2) at (0,2), then P1 at (0,1), then P1 at (0,0), no closing P2 → no capture.
- P1 (2,0); P2 (2,1); P1 (2,2): another column flip — captures P2 at (2,1).
- After 8 moves: **P1 has 4 stones (with 2 captured-by-flip), P2 has 1 stone.** P1 = +2.5, P2 = +0.75.

Reflection: **Custodian rewards EARLY P1 sandwiches, not P2 sandwiches.** Because P1 moves first and can bracket any single P2 stone with two flanking P1 placements, P1 has a built-in attack pattern that P2 doesn't. P2 needs at least 4 own moves to set up a custodian flip (P2-?-P2 with P1 in between, where the middle is created by P1's choice). The asymmetry is *worse* for P2 than carpet rank-1's outnumber.

### Game 3 — P2 baits a custodian flip

Sequence: `0,9,2,1,11,20,18,27` (8 plies).

Plot:
- P1 (0,0); P2 (0,1); P1 (2,0); **P2 (1,0): does NOT flip (0,0).** Custodian needs a *bracketed run*. Walking from (1,0): -x finds P1 at (0,0), then no further cell (boundary). Walking +x: P1 at (2,0), then no further. Neither walk closes with P2. No capture.
- P1 (2,1); P2 (2,2); P1 (0,2): **flips (0,1)? Walking -y from (0,2): finds P2 at (0,1), then P1 at (0,0). Bracket {P1, P2, P1} — 1-stone run flips. Yes flipped.**
- Move 8: P2 (0,3). Walking -y from (0,3): finds P1 (just-flipped) at (0,2), P1 at (0,1) (also P1 now), P1 at (0,0), no closing P2. No flip.
- After 8 moves: P1 has 5 stones (4 placed + 1 flipped), P2 has 3 stones at (0,3), (1,0), (2,2). P1 = +3.0, P2 = +0.5.

Reflection: **P2 cannot easily flip P1 stones because P2's stones are isolated and don't form bracketing pairs with another P2 stone surrounding a P1 stone.** This is the structural P1 advantage of custodian-with-first-move: P1 already has a 2-stone pair to bracket from move 5; P2 doesn't get a second stone in good position until move 4, by which time P1 has 2 stones already on the board.

### Strategy guides

**P1 (offence):** Open at corner. Place flanking stones at 2-step axes ((0,0), (2,0), (0,2)). Each move reaches a custodian flip when an opponent stone is between two P1 stones. With first-mover advantage on flanks, P1 generates 1-2 free flips per game.

**P2 (defence):** Avoid playing between two P1 stones. Stay 2+ cells from any P1 stone. Try to set up own bracketing via long-range placement: play at (a, b) with an existing P2 stone at (a+2, b), and lure P1 into playing (a+1, b). But P1 has no incentive to walk into a sandwich, so this rarely succeeds. P2's effective option is to threaten captures via different geometric directions, hoping P1's race to threshold occasionally creates accidental brackets.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two:
1. **Cluster + flip-attack** (P1's playbook). Build at corners, set up flanking pairs (a,0) and (a+2,0), wait for P2 to play (a+1,0) or play it themselves to bait a future flip.
2. **Spread-and-survive** (P2's playbook). Keep stones distanced from P1 stones, build own cluster at far corner, race to threshold despite tempo deficit.

**Counter-play.** Real but P1-favoured. P2's only counter is to deny P1 the flanking opportunity by not placing adjacent to P1 stones. But this means P2 plays in isolated cells, missing the cluster-reinforcement bonus. **Same knowledge-asymmetric balance as rank-1, but custodian makes the asymmetry sharper.**

**Short-term vs long-term.** Same as carpet rank-1: ~15-move horizon. Custodian flips are 2-3 ply tactical decisions. Strategic horizon ~5-6 plies.

**Emergent concepts observed.**
- **Custodian flip-as-cluster-builder.** A 1-stone enemy run flipped between two own stones gives the captor a 3-stone collinear chain — high mutual reinforcement (~+5.5 contribution), better than the outnumber-2 captured-cell L-shape from carpet rank-1.
- **First-mover tempo amplification under custodian.** P1 gets free flip opportunities because flanking pairs can be set up by move 5 (3 P1 placements: (0,0), (2,0), then waiting for P2 to play between, or playing the middle themselves later).
- Same hole-bottleneck routing as carpet rank-1.

**Does the carpet substrate matter?** Same analysis as rank-1: 17 holes provide local geometric variation but don't fundamentally change strategy. Could be flattened to 9×9 grid with ~−0.5 depth.

**Does the propagation kernel matter?** Same analysis as rank-1.

**Capture-rule contribution.** Captures fired in 2 of 3 games. Custodian-by-P1 fires reliably (Game 2 and 3 both saw P1 flip an isolated P2 stone). Capture-by-P2 essentially never fires under good P1 play. **Custodian skews balance further toward P1 than outnumber.**

**First-mover advantage / seat balance.** Heavily P1-favoured under any play. The trained-vs-trained 0.500 winrate must come from PPO learning extreme defensive P2 play, possibly involving stalling tactics or threshold-race overtakes via low-density spread. The PPO trained-vs-random WR of **0.707** (lower than the other 5 games' ≥0.95) reinforces this — PPO struggled to beat random consistently as P2.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + custodian + threshold-race on a fractal substrate. Argument:

(a) **Custodian capture** is Othello/Reversi exactly — the placer flips runs of bracketed enemies. Othello goes back to 1971 (Goro Hasegawa).

(b) **Influence-based threshold-race** — same family as carpet rank-1.

(c) **Custodian + influence + threshold** combination doesn't appear in published abstract-game literature. Othello has implicit territorial scoring (count-stones-at-end); R19 carpet rank-2 has explicit influence-weighted scoring (sum-influence-on-owned-cells).

(d) **Sierpinski carpet substrate** — same novelty as rank-1.

(e) **Expert-transfer test.** An Othello player would understand 90% of the rules immediately. The novel piece is the influence-weighted scoring instead of stone-counting at end.

**Closest known-game analogue:** **Othello with influence-weighted scoring on a Sierpinski carpet.** The closest published reference is *Reversi* with the substrate change.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on 2D grid. R19 carpet rank-2 is custodian + influence + threshold on 2D fractal. **Both use custodian, neither uses connection vs threshold.** The flip mechanic in both produces "chain completion via single-move capture" feel. R19 carpet rank-2 is structurally the **closest R19 game to R8's family**. R8 wins on novelty (connection win condition is more narrative) and balance (R8 was actually balanced in the human eval); R19 carpet rank-2 loses on the P1 advantage that custodian + first-move structurally creates without a connection counter-incentive.

**Player rebuttal (P1 + P2).**
- The 3-stone collinear chain produced by custodian-flip IS a meaningful tactical pattern. The two flanking stones plus the captured middle reinforce each other (~+5.5 influence) — strong cluster from a single move.
- Subtracting from novelty: the strategic skeleton (corner-anchor + flanking + flip) is recognisable Othello strategy.

**Novelty score (post-adversary):** **5/10.** Same band as carpet rank-1. The custodian + influence combination is a real combinatorial pairing, but Othello's cluster-flip primitive is so well-known that the novelty contribution is mostly in the influence-scoring axis (which carpet rank-1 already covers).

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** b48208268f2a
**Rules Summary:** Place stones on a 9×9 carpet (17 holes) to accumulate influence on cells you own. Each placement spreads ±1.0/±0.5/±0.25 within graph-radius 2; placing brackets enemy runs (Othello-style) and flips them to your colour. First to >30.0 effective influence wins.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Custodian flip adds chain-completion tactics; flank-and-wait pattern is a real decision. Comparable to carpet rank-1 but slightly more tactical due to flip dynamics.
- **Emergent Complexity: 5** — Flank-and-flip is non-obvious if you haven't played Othello. Below 6 because the patterns are well-known to anyone who has.
- **Balance: 3** — **Worse than carpet rank-1**. Custodian + first-mover gives P1 free flip opportunities that P2 cannot reliably set up. PPO's 0.707 trained-vs-random reflects P2's structural difficulty. The trained-vs-trained 0.500 winrate is achieved only under specific learned defensive play.
- **Novelty (post-adversary): 5** — Same band as rank-1. Othello + influence + carpet is a recognisable combination; not pure re-skin but not genuinely new.
- **Replayability: 4** — Same opening collapse as rank-1, with a sharper P1 advantage adding to strategy collapse.
- **Overall "Would I play this again?": 4** — **Below carpet rank-1 by 1 point.** The custodian dynamic is more dramatic but the P1 advantage is less recoverable. R17 corpus mean was 3.50; this game is in that range — playable but unbalanced.

### CLOSEST KNOWN-GAME ANALOG
**Othello (Reversi) with influence-weighted scoring on a Sierpinski carpet.** Within this project corpus, the closest is R8's Connection Go (custodian + connection, 2D grid) — R19 carpet rank-2 swaps connection for influence-threshold but keeps the custodian primitive.

### KILLER FLAWS
- **P1 has free flip opportunities; P2 effectively does not.** The custodian + first-move + 9×9 board combination structurally favours P1, beyond carpet rank-1's mirror-tempo advantage.
- **PPO trained-vs-random 0.707** — lowest of the 6 R19 games. PPO struggled to learn dominant play, suggesting noisier strategic surface or harder-to-balance dynamics.
- **Mirror = P1 win** + custodian asymmetry compounds into a sharper imbalance than carpet rank-1.
- **Once corner-flank pattern is known, the early opening collapses to a small set.**

### BEST QUALITY
**The 3-stone collinear chain produced by custodian-flip.** A single move converts a 1-stone P2 between two P1 stones into a 3-stone P1 chain — the strongest single-move cluster contribution in any R19 game. This is the same primitive that makes R8's Connection Go work, transferred to influence-threshold. **Closest R19 game to R8's family** in terms of mechanical primitives.

### CARPET STRUCTURAL CONTRIBUTION
Same as rank-1 — modest, not transformative. Estimate −0.5 depth if flattened.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same recommendation as rank-1, but more critical here because the P1 advantage is structurally larger). Pie rule would punish P1 for any opening strong enough to reliably set up flips.

Secondary improvements:
- **Increase capture threshold to 2** (real 2-stone-run minimum). Would prevent the cheap 1-stone flips that drive P1's early lead. Closer to traditional Othello.
- **Add P2-only knowledge advantage** (e.g., P2 can pass first move). Compensates for first-mover disadvantage explicitly.
- **Test custodian + connection win condition** (the R8 family) instead of threshold-race. Connection makes captures meaningful for chain completion rather than just stone count, which matches the custodian primitive's strength.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-pilot_gameb48208268f2a.md`.*
