# Run 21 Agent-Team Eval — team-1 — Game b12ff78f1c1d

**Team ID:** team-1
**Game ID:** b12ff78f1c1d (grid slate **TOP**, 20-seed mean GE 0.0985, σ 0.0517 — **most stable game in the project**; gen-5 crossover child, lineage `[07d19636abaa, 09150071c8cb]`; calibrated komi_p2 0.05)
**Substrate:** grid (axis 8, 64 active cells / 64 grid positions, max_degree 4, pie_rule=True, no holes)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game b12ff78f1c1d` (see `briefing_grid_b12ff78f1c1d.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Flat 8×8 grid, 64/64 active, no holes (live game is grid-8, not grid-9 — verified). Cell = y·8 + x. Max_degree 4.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = 72 (race ends ~ply 17).

**Action space.** 66 actions = 64 place + slot 64 (unused) + pie 65. Place-only; `adjacent_empty` vestigial (all empties legal).

**Placement & capture.** **custodian, threshold 1** — *different from the menger/carpet outnumber games*. Placing so an opponent stone (or run) is bracketed by the mover's stones on opposite orthogonal sides **flips it to the mover** (Othello/Reversi single-line custodian). Verified live: P1 (3,3)+(5,3) flipped P2's (4,3), P1 pieces 2→4 / P2 2→1; and symmetrically P2 (2,3)+(4,3) flipped P1's (3,3). **This is a double-swing capture — you steal the stone (and its influence) rather than just clearing it** — strictly more potent than outnumber-clear. But dense-block stones are protected: in a packed block, friendly neighbors prevent bracketing (verified: no captures fired against a packed P1 block).

**Propagation.** influence, radius 1, strength 1.0, **decay 0.5** (sharp falloff — neighbor gets +0.5). Local field; a dense 2D block interior cell scores 1.0 + 4×0.5 = 3.0.

**Win condition.** threshold-race. Effective owned-influence > **20.0**. `target_dimension_p2=-1` mirror. **Komi = komi_p2 × threshold = 0.05 × 20 = 1.0** (helper under-displays as 0.05).

**Pie rule.** True (action 65, P2-only on move 2).

**Degeneracy check.**
- **FAIL_RUSH_BROKEN (G3):** at komi 0.05, sampled P1 winrate 0.47 but **greedy P1 winrate 0.00 with greedy seat bias 0.50** — against a greedy opponent the seat fully determines the result. Komi 0.05 is the *least-bad* point (sampled bias 0.030), not a passing calibration. Confirmed in play: P1 rushes a dense block to 20 by tempo.
- Helper komi under-display (true komi 1.0).
- `adjacent_empty` vestigial.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass-class = 64; pie = 65.

### Game 1 — P1 rush top-left block vs P2 bottom-right (uncontested) — **rush wins**
Sequence: `0,63,1,62,2,61,8,55,9,54,10,53,16,47,17,46,18,45` (resolves ply 17).
Plot: P1 packs a 3×3 block (decay 0.5 → ~2.3/stone). **Ply 17 P1 → +21.0 > 20, Winner=1** while P2 at +18.05. P1's full-tempo lead exceeds komi 1.0 → clean rush win. This *is* the FAIL_RUSH_BROKEN behavior.
Reflection: pack tight, ride tempo to 20. Komi 1.0 cannot overcome a full-tempo lead.

### Game 2 — Custodian steal (the grid-specific lever)
Sequence: `27,26,55,28` (P2 brackets an exposed P1 stone).
Plot: P1's (3,3) bracketed by P2 (2,3)+(4,3) → **flipped to P2**; P1 pieces 1→… lost, P2 gained it (P2=3). A single flip swings the *piece count by 2* and moves influence from one side to the other — far more impactful than an outnumber-clear.
Reflection: custodian is a real tactical threat against exposed/edge stones; the swing is big enough to matter in a 20-point race.

### Game 3 — Can a flip break the rush? (packing defense)
Sequence: `9,1,10,2,17,0,18,16` (P1 packs, P2 probes the block edge).
Plot: **no captures fire** — every P1 block stone has a friendly orthogonal neighbor, so P2 cannot complete a bracket. The rush is robust against custodian harassment.
Reflection: as in the outnumber games, dense packing is both max-score and capture-immune — the score/safety coincidence persists even with the stronger custodian capture.

### Strategy guides
**P1:** rush a dense block, keep stones mutually adjacent (flip-immune), reach 20 by tempo.
**P2:** you cannot out-rush (lose by tempo + face the rush bias); your only edge is to catch an exposed P1 stone with a custodian flip (big swing) or swap — but against tight packing neither overcomes the rush.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Essentially one (rush a dense block) + opportunistic custodian flips against mistakes + binary swap. The custodian threat adds tactical texture but not an independent winning plan.
**Counter-play.** Weak — the rush is structurally favored (G3 FAIL); custodian flips defended by packing; komi/pie don't close the greedy bias 0.50.
**Short-term vs long-term.** Short (~17 plies); custodian adds local tactics but no strategic horizon.
**Emergent concepts observed.** Custodian double-swing steal; contiguity-as-armor (now defends against flips too); rush tempo lockout. The flip is the one genuinely lively mechanic.
**Does the grid substrate matter?** **No** — flat 8×8 with no holes contributes nothing structural (contrast carpet's theaters). Any flat board would play identically.
**Does the propagation kernel matter?** decay 0.5 keeps the field local; it's the win metric but adds no positional nuance beyond "pack tight."
**Capture contribution.** The custodian flip is the most impactful capture in my 7 games (steals rather than clears), but it's a deterrent against loose play, not a rush-breaker.
**First-mover advantage / seat balance.** **Worst in the slate by the rush metric: greedy seat bias 0.50, greedy P1 winrate 0.00.** Komi 1.0 + pie is least-bad, not passing. The most stable game is also one of the most rush-determined.

**Stability↔quality (the briefing's question), answered.** **Stability does NOT indicate quality here.** σ 0.0517 (tightest in the project) comes from the game being a clean, convergent, solvable rush — exactly the property that makes it shallow and rush-broken. Evolution compounded (gen-5 crossover child) toward a *stable rush*, not toward depth. Low variance ↔ low strategic diversity ↔ solvable, the same anti-correlation seen with bfd1's "reliability."

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** A flat-grid influence **race with Othello-style custodian capture**.
(a) Threshold-race on influence ≈ Go-area/territory race.
(b) custodian-1 flip ≈ **Othello/Reversi** capture (bracket-to-flip), the defining Reversi mechanic.
(c) "influence race + Othello flip on a flat grid" is two known ideas stacked; no published analogue, but neither half is new and the substrate is maximally generic.
(d) Substrate: flat grid adds nothing (vs R8's grid which at least had connection-win to justify it).
(e) Expert-transfer: an Othello + Go player learns this in ~5 min.

**Closest known-game analogue:** an influence/area race with Reversi custodian flips on a plain board.
**Comparison to R8 (4.10).** R8 used its flat grid for a *connection* win with a real cut-vs-race axis; this game uses its flat grid for a rush-broken influence race with capture as garnish. Thinner than R8.
**Comparison to R19/R20.** Same threshold-race family; the custodian flip is a nicer capture than R19/R20's outnumber/surround, but the flat substrate + rush-broken balance keep it below R19 grid/menger tops.

**Novelty score (post-adversary): 3.5/10.** The custodian flip is the most interesting capture in my set, but it's textbook Reversi on a generic grid; no new strategic idea.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** b12ff78f1c1d
**Rules Summary:** A flat-8×8 influence race to 20 points where you can steal an exposed enemy stone by bracketing it Othello-style — but dense packing is both the fastest way to score and immune to the steal, so the game reduces to a first-mover rush that packs a corner block and wins by tempo. The project's most stable game, because it is its most solvable.
**Substrate:** grid, axis 8, 64/64 cells, max_degree 4, pie_rule=True, komi_p2=0.05 (effective 1.0).
**Turn Structure:** alternating, 1 piece/turn.
**Hybrid actions:** no.
**Soft violations flagged:** **FAIL_RUSH_BROKEN (greedy seat bias 0.50)**; helper komi under-display (true 1.0); vestigial `adjacent_empty`.

### Scores (1–10)
- **Strategic Depth: 4** — custodian flips add a genuine tactical layer (steal exposed stones), but the rush dominates and packing defends, capping depth. Engine strategic_depth 0.6065 overstates the felt play.
- **Emergent Complexity: 4** — the double-swing custodian steal is the liveliest mechanic in my set; contiguity-as-armor now also defends flips. Modest but real.
- **Balance: 3.5** — FAIL_RUSH_BROKEN: greedy seat bias 0.50, greedy P1 winrate 0.00; komi 1.0 + pie is least-bad, not passing. The rush determines the seat.
- **Novelty (post-adversary): 3.5** — Reversi flip on a generic grid; no new idea, generic substrate.
- **Replayability: 3.5** — most stable = most convergent = least varied; the rush solves it.
- **Overall "Would an agent team play this again?": 3.8** — A clean influence race with a satisfying steal mechanic, undermined by a rush-broken seat balance and a featureless substrate. Above R20 production mean (3.73), below R8 (4.10) and the 5.0 G1 ceiling. Stability is a symptom of solvability here, not quality.

### CLOSEST KNOWN-GAME ANALOG
An influence/area race with Othello/Reversi custodian flips on a plain 8×8 grid. Inside the corpus, the grid analogue of the menger packing races but with a flip-capture instead of clear-capture.

### KILLER FLAWS
- **Rush-broken (G3 FAIL):** first-mover rushes a block to 20; greedy seat bias 0.50.
- Score-max and capture-safety coincide (packing defends even the custodian flip).
- Flat substrate contributes nothing structural.

### BEST QUALITY
The **custodian double-swing flip** — stealing an enemy stone (and its influence) is the most impactful capture in my 7 games and gives the only real tactical spark. It just isn't enough to overcome the rush.

### GRID STRUCTURAL CONTRIBUTION
None. A flat 8×8 with no holes adds no geometry; the game would be identical on any flat board. This is the clearest case in my set of substrate-as-decoration — and a reminder that R21's one evolutionary success (a gen-5 crossover child) compounded toward a *stable rush*, not toward depth.

### IMPROVEMENT IDEAS
**Single best change:** break the score/safety coincidence so the custodian flip can actually fire in equilibrium — e.g. reward *spread* influence (diminishing returns on saturated cells) so players must expose stones, making the flip a live rush-breaker instead of a deterrent. That would also attack the rush-broken balance.
Secondary:
- Add substrate structure (holes/theaters like the carpet) so position matters.
- Replace the threshold rush with a connection-style or majority-at-cap goal that the first-mover can't simply outrun.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-1_gameb12ff78f1c1d.md`.*
