# Run 21 Agent-Team Eval — team-4 — Game b12ff78f1c1d

**Team ID:** team-4
**Game ID:** b12ff78f1c1d (grid slate TOP, 20-seed mean GE 0.0985, σ 0.0517 — most stable in project, calibrated komi_p2 0.05; G3 verdict FAIL_RUSH_BROKEN)
**Substrate:** grid (axis 8, 64 active / 64 grid positions, max_degree 4, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game b12ff78f1c1d` (see `briefing_grid_b12ff78f1c1d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, 64 active / 64 (no holes); cell = y·8 + x. Interior max_degree 4, edges 3, corners 2. (Note: live game is grid-8/64, not grid-9/81 — verified.)

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 72.

**Action space.** 66 = 64 place + unused slot 64 + pie (65). Place-only; `adjacent_empty` vestigial (all empties legal from any state).

**Placement & capture.** **Custodian, threshold 1** — a stone is **flipped to the mover's colour** when sandwiched between mover stones on opposite orthogonal sides. Verified live: P1 at (3,3) then (5,3) flipped P2's (4,3) (`Captures (flipped owner): ['(4,3)']`, P1 2→4 pieces). **Crucially, custodian FLIPS (not clears) — so capture is SYNERGISTIC:** you gain the stone *and* its influence flips sign in your favor. This is the opposite of the menger/carpet outnumber rule.

**Propagation.** influence, radius 1, strength 1.0, **decay 0.5** (steepest in slate: neighbor deposit 0.5). Verified: lone stone = +1.0 self, +0.5 each of 4 neighbors; opponent overlap nets negative.

**Win condition.** threshold-race, **> 20.0**, `target_dimension_p2=-1` (P2 mirrors P1). max_turns 72; ~0–3% draws. komi_p2 = 0.05.

**Pie rule.** True (action 65, P2-only on move 2).

**Degeneracy check.** `adjacent_empty` vestigial; no holes (full 4-connectivity). **G3 FAIL_RUSH_BROKEN**: at komi 0.05 sampled P1 winrate 0.47 (balanced) BUT greedy P1 winrate 0.00 / greedy seat bias 0.50 — against a rushing opponent the seats are fully determined. komi 0.05 is the least-bad point, not a passing calibration.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass/unused = 64; pie = 65.

### Game 1 — Symmetric block race (P1 top-left 3×3, P2 bottom-right)
Sequence: `0,63,1,62,2,61,8,55,9,54,10,53,16,47,17,46,18,45`
Plot: **P1 wins at step 17 (9 stones).** A packed 3×3 corner block (decay 0.5) reaches > 20; P1 led on tempo throughout.
Reflection: Core is still a fill-race — pack the densest corner block. Decay 0.5 means it takes 9 stones (vs carpet's 8 at r2), so slightly more grind than carpet but the same plan.

### Game 2 — Custodian capture in a contested centre
Sequence: `27,28,35,36,29,20,43,21`
Plot: P1's (3,3)+(5,3) flip P2's (4,3) → P1 jumps to 4 pieces; play stays contested, ending P1 +4 / P2 +5.05 (komi). The flip is real and offensively valuable, but in a contested centre it does not dominate — P2's own stones + komi kept it close.
Reflection: **Custodian flips are the one genuine tactical lever in the entire threshold-race family** — capturing here ADDS to your accumulator (gain stone + flip its influence sign), unlike the self-harming outnumber pod. This creates a real reason to engage rather than build in isolation.

### Game 3 — Rush test / seat balance
Sequence: P1 straight corner rush vs P2 mirror.
Plot: Confirms the briefing's FAIL_RUSH_BROKEN — a first-mover corner rush is hard to stop; greedy seat bias 0.50. With sampled (non-greedy) play, komi 0.05 brings it to ~0.47, near balanced.
Reflection: Balance is opponent-dependent: balanced vs a thinking opponent, fully seat-determined vs a rusher. The custodian flip is the main way a second mover can claw back tempo (flip a P1 stone on the contested edge).

### Strategy guides
**P1:** Pack a corner block; use custodian flips opportunistically to both deny P2 and convert tempo. Rush if the opponent is greedy.
**P2:** Don't pure-mirror (loses on tempo) — contest P1's block edges with custodian flips to convert P1 stones; lean on komi 0.05.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two, weakly: (1) isolated corner-pack (tempo race), (2) contest-via-custodian (flip P1 stones to swing the accumulator). The second is real here (unlike the outnumber pod) because flips are synergistic. Strategic_diversity 1.0 (single-eval) is overstated but there IS more than one idea.
**Counter-play.** Partial and real: custodian flips let the defender convert attacker stones — the only genuine counterplay mechanic in the threshold-race family.
**Short-term vs long-term.** Mostly short (17-ply races), but custodian set-ups (place two flankers around an enemy stone) add a 2–3 ply tactical layer absent elsewhere.
**Emergent concepts observed.** Custodian flip-chains; tempo-vs-flip trade; contested-edge swings. More than the outnumber pod's single (negative) emergent property.
**Does grid matter?** The flat 8×8 + full 4-connectivity is what makes custodian flips reliable (no holes to break the sandwich). The substrate is a clean vehicle; the rules carry it.
**Does the propagation kernel matter?** decay 0.5 sets a moderate pace; the real lever is custodian, not influence shape.
**Capture-rule contribution.** **Genuinely positive here** — the standout of the slate. Custodian flips are worth playing for.
**First-mover advantage / seat balance.** FAIL_RUSH_BROKEN (greedy 0.50) but sampled ~0.47. Opponent-dependent; custodian gives P2 real claw-back. Worse than carpet's clean balance, better than the connection game's structural 0.50.
**Stability ↔ quality?** Partly. It IS the most stable game (σ 0.0517) and a verified gen-5 crossover child — and it is also the best of the threshold-race family, because the custodian flip adds the one real interaction. So here stability coincides with the family's best quality, but the lift comes from the *custodian rule*, not from stability per se.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Influence-area race + Othello-style custodian capture.
(a) Threshold-race = area/influence scoring to a target.
(b) Custodian flip = **Reversi/Othello's defining mechanic** (bracket to flip). Directly known.
(c) "Othello-flip + influence-race on a flat grid" — Othello already IS a custodian-flip area race; this is close to a small Othello variant with a fixed influence-sum target instead of final-count, and free placement instead of must-flip.
(d) Flat 8×8 grid — the literal Othello board; no fractal novelty.
(e) Expert-transfer: an Othello player learns this in ~5 min (the twist: placement is free, not flip-constrained, and you race an influence sum, not final count).

**Closest known-game analogue:** Reversi/Othello with free placement and an influence-sum target (instead of end-count). The custodian flip is pure Othello.
**Comparison to R8 (4.10):** thinner on global structure (no connection/topology) but its capture is more *usable* than R8's negative-EV surround.
**Comparison to R19/R20 best:** above R20 production (3.73) on interaction quality; below R19 top (4.8) — no global objective.

**Novelty score (post-adversary):** **3.5/10.** Above the outnumber pod (3.0) because the synergistic custodian flip is a real, playable mechanic and the family's only genuine interaction; below 4 because that mechanic IS Othello and the substrate is the literal Othello board.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** b12ff78f1c1d
**Rules Summary:** Race to 20 influence on an 8×8 grid, where Othello-style custodian flips let you convert enemy stones to swing the score — the most interactive (and most stable) member of the threshold-race family, but rush-broken against a greedy opponent.
**Substrate:** grid, axis 8, 64/64 cells, max_degree 4, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** FAIL_RUSH_BROKEN (greedy seat bias 0.50; komi 0.05 least-bad, not passing); `adjacent_empty` vestigial.

### Scores (1–10)
- **Strategic Depth: 3.7** — Fill-race core, but custodian set-ups add a real 2–3 ply tactical layer and a second viable plan (contest-via-flip). Above the outnumber pod.
- **Emergent Complexity: 3.8** — Custodian flip-chains and contested-edge swings are genuine emergent tactics — the only positive emergent behavior in the threshold-race family.
- **Balance: 3.5** — Opponent-dependent: ~0.47 vs sampled, 0.50 vs greedy (FAIL_RUSH_BROKEN). Custodian gives P2 claw-back, but the rush flaw is real.
- **Novelty (post-adversary): 3.5** — Othello custodian flip + influence-race on the literal Othello board; usable but well-known.
- **Replayability: 3.6** — Two viable plans + tactical flips give more opening/variation than the pod, capped by the rush.
- **Overall "Would an agent team play this again?": 3.7** — Best of the threshold-race family; above R20 production (3.73) by a hair, below R8 (4.10) and R19 top. The custodian flip — not stability — is what lifts it.

### CLOSEST KNOWN-GAME ANALOG
Reversi/Othello with free placement and an influence-sum target; within corpus, the most interactive R20-style grid threshold-race.

### KILLER FLAWS
- FAIL_RUSH_BROKEN: a greedy first-mover corner rush is unstoppable (seat bias 0.50); komi cannot fix it.
- Core is still a fill-race; the custodian layer is real but thin (2–3 ply tactics, no global objective).
- The substrate is the literal Othello board — the rules add little the topology demands.

### BEST QUALITY
**The synergistic custodian flip** — the one capture rule in the threshold-race family that you actually *want* to use (gain the stone AND flip its influence sign). It creates genuine reason to engage instead of building in isolation, and is the slate's best argument that capture+influence can interact constructively.

### GRID STRUCTURAL CONTRIBUTION
Vehicle, not contributor: the flat 8×8 + full 4-connectivity makes custodian sandwiches reliable, but a fractal/3D substrate would only break the mechanic. The depth is in the custodian rule, not the topology.

### IMPROVEMENT IDEAS
**Single best change:** Fix the rush — add a real first-move restriction or a proper komi/handicap so the greedy 0.50 seat bias closes; the game is balanced vs thinking play but broken vs rushing.
Secondary:
- Add a global objective (small connection target, or end-count instead of fixed influence-sum) so the custodian flips serve a longer-horizon plan rather than a 17-ply sprint.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-4_gameb12ff78f1c1d.md`.*
