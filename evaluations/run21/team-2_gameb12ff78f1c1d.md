# Run 21 Agent-Team Eval — team-2 — Game b12ff78f1c1d

**Team ID:** team-2
**Game ID:** b12ff78f1c1d (grid slate TOP, gen-5 crossover child; 20-seed mean GE 0.0985, σ 0.0517 — most stable in the project; calibrated komi_p2 0.05, G3 verdict FAIL_RUSH_BROKEN)
**Substrate:** grid (axis 8, 64 active / 64 grid, max_degree 4, no holes, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game b12ff78f1c1d` (see `briefing_grid_b12ff78f1c1d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, fully active (64/64, no holes), max_degree 4. Cell = y·8 + x. (Note: live game is grid-8, not grid-9.)

**Turn structure.** Alternating, 1 piece/turn, P1 first. **Max_turns = 72.**

**Action space.** 66 = 64 place + pass(64) + pie(65). `first_move_anywhere`; `adjacent_empty` vestigial (all empties legal from any state, verified).

**Placement & capture.** **Custodian, threshold 1.** A stone is **flipped to the mover** when it becomes bracketed by mover stones on opposite orthogonal sides. Verified live: P1 at (4,3) bracketed by P2 (4,2)+(4,4) → flipped to P2 (P1 pieces 2→1). **This is the slate's most active capture** — flipping steals both the stone AND its influence (a double swing), and fires with just two opposite stones.

**Propagation.** `influence`, radius 1, strength 1.0, **decay 0.5**. Self +1.0, each orthogonal neighbour +0.5. Verified: lone stone +1.00 on-cell, +0.50 on 4 neighbours; opposing fields sum (contested neighbour reached −1.00).

**Win condition.** **threshold-race**, exceed **20.0**. `target_dimension_p2 = -1` ⇒ P2 mirrors P1's accumulator. komi_p2 = 0.05. max_turns 72 — but a compact block reaches +20 in ~17 plies, so the cap is irrelevant; draws possible (~0–3%) only if both stall.

**Pie rule.** On (action 65), P2-only on move 2.

**Degeneracy check.**
- **G3 FAIL_RUSH_BROKEN.** `calibrated_komi=null`; 0.05 is the least-bad point (sampled bias 0.030) but **greedy seat bias stays pinned at 0.50** for all komi ≥ 0.05 — against a greedy opponent the seats are fully determined. The race is solvable by rushing.
- `adjacent_empty` vestigial.
- Decay 0.5 (lowest in slate) + threshold 20 (lowest) → the **shortest, sharpest race** of the seven.

---

## Phase 2 — Strategic Play

Place id = cell; pass = 64; pie = 65. All engine-verified.

### Game 1 — Two compact blocks, knife-edge finish
Sequence: `27,0,28,1,35,8,36,9,29,2,37,10,26,16,34,17,43,24,44,25` (P1 packs a centre 2-row block y=3,4; P2 packs the (0,0) corner block).
Plot: At ply 16 both at +18.0 / +18.05. **Ply 17: P1 reached exactly +20.000 — and that is NOT a win (threshold is strict ">20").** Ply 18: P2's block + komi reached +20.050 → **P2 wins by 0.05.** The game is literally decided by the komi tie-break on a half-point.
Reflection: This is the rush made tactile. Two equally-efficient packers reach the bar within one ply of each other; whoever clears `>20` first wins, and komi 0.05 is precisely enough to hand it to P2. The "balance" is a coin-flip resolved by the komi constant, not by play.

### Game 2 — Custodian capture as the real lever
Sequence: `28,36,27,20,35` — P2 flips P1's (4,3) by vertical bracket (4,2)+(4,4). Custodian-1 fires trivially and swings ~+1.5 net (you gain the stone's +1 self and flip its neighbour contributions). In a +20 race this is enormous — a single well-timed flip can be worth ~1.5 of the 20 needed.
Reflection: Captures here are *not* inert (unlike the menger pod). They are the one genuine tactical layer — but the race is so short (~17 plies) that there is rarely time to set up more than one or two before someone clears the bar.

### Game 3 — Pie / rush confirmation
Pie (65) swaps on move 2. But the rush-broken nature means whoever gets the favourable seat (post-komi) in the packing race tends to win; pie lets P2 grab a strong P1 opening, but the deeper problem is the race is too short and solvable for either balancing tool to create real contest.

### Strategy guides
**P1:** pack the most compact connected block you can (centre or corner — both ~equal); race to clear >20 before P2; watch for custodian brackets on your block's edge stones.
**P2:** mirror-pack; use komi 0.05 + one custodian flip to win the half-point race; swap (65) only if P1's opening is unusually strong.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One-and-a-half: pack a compact block (primary) + opportunistic custodian flips (secondary tactical layer). No second strategic plan.
**Counter-play.** Custodian flips give real local counter-play (cut/steal an edge stone), but the race is too short for it to compound into a strategy.
**Short-term vs long-term.** Horizon ~3–4 moves; game ~17 plies — the sharpest race in the slate. Custodian adds a 1–2-move tactical wrinkle.
**Emergent concepts observed.** Compact-block compounding; **custodian flip as double-swing** (the slate's best emergent tactic); edge-stone vulnerability.
**Does grid matter?** It's a constraint-only flat board; the no-holes 8×8 gives no structural scaffolding (unlike carpet's void or menger's routing). The game would play nearly identically on any small flat board.
**Does the kernel matter?** decay 0.5 + threshold 20 set the (very short) pace; lower than the rest of the slate, making the rush sharper.
**Capture contribution.** **Real** — the only slate game where captures are a live, frequent tactical lever. This is its best feature.
**First-mover / seat balance.** **Broken at the greedy/rush level** (bias 0.50, komi-decided half-point finishes). Stability (σ 0.0517) reflects a *solved-ish rush*, not robustness of a deep game. Stability ↔ quality test: **fails** — it is stable because it is shallow and rush-solvable.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** A flat-grid influence-territory race with Othello-style custodian capture.
(a) Threshold race ≈ numeric area scoring.
(b) **Custodian capture = Othello/Reversi** verbatim (bracket-to-flip). This is the clearest published-mechanic borrow in the slate.
(c) "custodian + r1-influence + threshold-race on flat grid" is Reversi-flipping fused onto an influence-accumulation race — not a named published game, but both halves are standard.
(d) Flat 8×8: no structural contribution.
(e) An Othello player recognises the capture instantly; total transfer ~3–5 min.

**Closest known-game analogue:** Reversi/Othello flipping on an influence-area race (a "soft-Othello dash").
**Comparison to R8 (4.10):** thinner — R8's connection/cut+build gave a real strategic contest; this is a short rush with an Othello tactic bolted on.
**Comparison to R19/R20 best:** below R20 production mean once the rush-broken balance is counted; the gen-5 lineage is notable for the *project* (evolution compounded) but the product is a thin rush.

**Novelty score (post-adversary):** **3.0/10.** Custodian-on-an-influence-race is a mildly fresh fusion, but both components are standard and the board is featureless.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** b12ff78f1c1d
**Rules Summary:** On a flat 8×8, race to +20 owned-influence by packing a compact block; flip opponents Othello-style with custodian captures. A ~17-ply sprint decided by a half-point and a komi constant.
**Substrate:** grid, axis 8, 64/64 cells, max_degree 4, pie_rule=True, komi_p2=0.05.
**Turn Structure:** alternating.
**Hybrid actions:** no.
**Soft violations flagged:** **G3 FAIL_RUSH_BROKEN** (greedy bias 0.50, komi-decided finishes); vestigial `adjacent_empty`; mirror-flag `target_dimension_p2=-1`.

### Scores (1–10)
- **Strategic Depth: 3.4** — A very short rush; custodian flips add a tactical wrinkle but the race ends before it can compound. 3–4-move horizon.
- **Emergent Complexity: 3.5** — The custodian double-swing flip is the slate's best emergent tactic (captures actually matter), lifting it above the menger pod on this axis.
- **Balance: 2.8** — The weakest in the slate: rush-broken, greedy bias 0.50, finishes decided by the komi tie-break on a half-point. Stability ≠ balance.
- **Novelty (post-adversary): 3.0** — Othello-flip fused onto an influence race; standard parts, featureless board.
- **Replayability: 3.0** — One plan (pack + flip); once the rush and the half-point arithmetic are known, little to explore.
- **Overall "Would an agent team play this again?": 3.4** — Notable as the project's most stable game and only place R21 evolution compounded, and its captures are the slate's most alive — but it is a rush-broken half-point sprint. Stability here certifies shallowness, not quality. Below R20 mean once balance is counted; below R8 (4.10); does not clear 5.0.

### CLOSEST KNOWN-GAME ANALOG
Reversi/Othello flipping bolted onto a soft-influence area race; in-corpus, the grid threshold-race line with a custodian capture.

### KILLER FLAWS
- **Rush-broken (G3 FAIL):** greedy seat bias 0.50; finishes decided by the komi constant on a half-point.
- Threshold 20 + decay 0.5 make the race too short for the custodian tactic to develop into strategy.
- Flat board contributes no structure; stability is the stability of a solved rush.

### BEST QUALITY
Custodian-1 capture is the **only genuinely live capture mechanic in the slate** — flipping steals stone + influence (a ~+1.5 double swing). With a longer race or higher threshold this could be a real tactical game.

### grid STRUCTURAL CONTRIBUTION
None beyond constraint. Confirms R19's grid-is-weakest finding; the gen-5 crossover lineage compounded GE/stability but not strategic substance. The "does stability ↔ quality?" experiment returns **no**.

### IMPROVEMENT IDEAS
**Single best change:** raise the threshold substantially (e.g., 40–50) and/or lower the influence so the race lasts long enough for custodian flips to chain into real positional warfare — the capture mechanic deserves room to breathe, and a longer race would also let komi/pie actually balance the seats instead of deciding a half-point.
Secondary:
- Add board structure (the carpet void, or a connection sub-goal) so packing one block is not strictly optimal.
- Accept that "most stable" ≠ "best"; do not headline the slate on σ.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-2_gameb12ff78f1c1d.md`.*
