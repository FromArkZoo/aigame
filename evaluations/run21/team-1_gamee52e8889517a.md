# Run 21 Agent-Team Eval — team-1 — Game e52e8889517a

**Team ID:** team-1
**Game ID:** e52e8889517a (menger slate **rank 3**, 20-seed mean GE 0.138, σ 0.090, calibrated komi_p2 0.05)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game e52e8889517a` (see `briefing_menger_e52e8889517a.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Same Menger sponge as the rest of the menger pod (9×9×9, 400/729 active, dense carpet faces at z=0/2/6/8). Cell = z·81 + y·9 + x.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **100** (the shorter-race sibling).

**Action space.** 731 actions (729 place + pass + pie 730). Place-only. `adjacent_empty` vestigial (397 legal after 4 moves — confirmed live).

**Placement & capture.** **outnumber-2**, identical to the rest of the pod: an isolated stone is cleared when enemy neighbors exceed friendly by ≥2. Verified live in pod testing (a flanked single stone is removed). Two stones spent to delete one — tempo-negative in a race; interior cluster stones are capture-immune.

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7** (vs Game 1's flat 1.0). A neighbor gets +0.7, not +1.0, so the race is slower and rewards *compact* clusters where mutual radiation compounds (two adjacent friendlies score 1.0+1.0+0.7+0.7 = 3.4).

**Win condition.** threshold-race (NOT connection). Effective owned-influence > **30.0** wins. `target_dimension_p2=-1` ⇒ P2 mirrors P1's accumulator. **Komi is applied as `komi_p2 × threshold` = 0.05 × 30 = 1.5** at the win check (see degeneracy note — the helper under-displays this).

**Pie rule.** True (action 730). P2 may swap at ply 2.

**Sibling identity (the scored differentiator).** Verified by flattened-blob diff against `1fea3357dca4`: the **only** differences are `win_condition.threshold` 30↔50 and `max_turns` 100↔200 (and game_id/seed label). Capture, decay-0.7 propagation, topology, pie, komi_p2=0.05 are byte-identical. **This game is the shorter-race variant**; its sibling is the longer grind. Per protocol I score only the threshold/length contrast, not "menger family novelty" again.

**Degeneracy check.**
- **Helper komi display bug.** The header and per-turn line print "incl komi +0.05", but the engine (`engine_v2.py:998`) uses `komi = komi_p2 * threshold = 1.5`. The true seat compensation is **1.5 points on a 30 race (5%)**, not 0.05. This materially changes balance reasoning.
- `adjacent_empty` vestigial; `target_dimension_p2=-1` is a mirror flag, not a second objective.

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — P1 packs left vs P2 packs right (uncontested mirror race) — **komi decides it**
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28,34,29,35,...` (22 plies to resolution).
Plot: Scores climb in lockstep, P1 ~3.8 ahead (its move-first tempo). Ply 21 P1 raw 29.2 (< 30, no cross). Ply 22 P2 reaches raw 29.2; **+1.5 komi → effective 30.7 > 30 → Done, Winner=2.** The komi let P2 cross at the *same* raw score where P1 stalled — the seat-balance lever working (in fact slightly over-working) in a perfect mirror.
Reflection: decay 0.7 stretches the race to ~22 plies (vs Game 1's 19 at decay 1.0). The binding constraint is still contiguity, but the **komi is now load-bearing** — it converts P1's tempo lead into a P2 win in the symmetric case.

### Game 2 — Capture-contest line
Sequence: `2,1,72,3` (isolated-stone bracket).
Plot: outnumber-2 fires exactly as in the rest of the pod — P1's lone (2,0,0) cleared once P2 holds (1,0,0)+(3,0,0). P2 paid two tempi for one deletion. Against a densely-packing P1 there are no isolated targets, so capture cannot overcome packing here either.
Reflection: capture is a deterrent against loose play; decay 0.7 doesn't change that.

### Game 3 — Pie-swap balance
Sequence: `0,730,...`.
Plot: swap flips P1's opener to P2 and hands P2 the tempo. With decay 0.7 the opening cell is worth +1.0, same as Game 1; swap neutralizes a strong opener but openings are near-equivalent, so it mostly trades tempo.
Reflection: pie + the real 1.5 komi together over-balance the mirror toward P2; against non-mirror PPO play the calibration (bias 0.015) holds.

### Strategy guides
**P1:** pack the densest carpet face, keep stones mutually adjacent (compounds under decay 0.7, also capture-immune), and try to cross 30 before komi tips an equal-raw P2 over.
**P2:** mirror-pack — the 1.5 komi means you win an equal raw race; only deviate to capture if P1 scatters. Swap only if P1 grabs a uniquely strong opener.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One dominant plan (compact packing) + binary swap, same as Game 1. DB strategic_diversity 0.667 is single-seed and optimistic; play converges.
**Counter-play.** Partial — komi/swap balance the seats; capture cannot beat packing.
**Short-term vs long-term.** Short-to-medium (22 plies); decay 0.7 adds a little spreading nuance over Game 1 but no real strategic horizon. The shorter threshold (30) keeps it from dragging.
**Emergent concepts observed.** Contiguity-as-armor; **komi-as-tiebreak** (here it decides the mirror); swap-to-inherit. Same modest set as Game 1, plus the komi tiebreak surfacing because decay 0.7 keeps raw scores closer near the line.
**Does menger matter?** Same as Game 1 — the sponge restricts where density lives; play stays on 2D faces. Would flatten to carpet with little loss.
**Does the propagation kernel matter?** Yes (it's the win metric). decay 0.7 rewards compactness slightly more subtly than flat 1.0 — a marginal richness gain.
**Capture contribution.** Deterrent only.
**First-mover advantage / seat balance.** Best-balanced of the menger pod *because the real komi (1.5) is non-trivial* — it actually flips the mirror to P2. Calibration bias 0.015 is credible. This is the **shorter-race sibling's advantage: less time for tempo to compound, so komi can finish the balancing job.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same family as Game 1: an influence/territory **packing race with flanking capture** on a fractal.
(a) Threshold-race ≈ Go area-scoring sprint.
(b) outnumber-2 ≈ Ataxx/Tafl flanking removal.
(c) The recipe is the R17–R20 menger family; this is the 30/100 parameterization. No new published-game analogue beyond Game 1's.
(d) Substrate adds restriction, not a fractal-specific tactic.
(e) Expert-transfer ~5 min for a Go/Ataxx player.

**Intra-family differentiator (the actual job).** Versus the longer sibling `1fea3357dca4` (50/200), the shorter race (30/100): resolves faster, gives the tempo edge less room to compound, and lets the proportional komi (1.5 vs the sibling's 2.5) land as a clean balancer. The slate evidence (this game held rank 3; the sibling deflated to rank 6) is consistent with **shorter = more seed-robust**. That is a *robustness* win, not a *depth* win — the games are strategically the same.
**Closest known-game analogue:** stripped-down Go-area packing race with Ataxx capture.
**Comparison to R8 (4.10).** Thinner — no asymmetric counter-strategy like R8's cut.
**Comparison to R19/R20 best.** Same family as R19 menger top (4.8); decay 0.7 here is closer to the R20 champions than Game 1's flat 1.0, but threshold-30 makes it a faster, not deeper, variant.

**Novelty score (post-adversary): 3.5/10.** Identical family to Game 1; the only intra-family novelty is "shorter race is more robust," which is a tuning property, not a new mechanic.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** e52e8889517a
**Rules Summary:** A Menger packing race to 30 points of own-color influence (decay 0.7 rewards compact clusters), with outnumber-2 flanking deletion as a deterrent and a real 1.5-point komi that balances the seats — the shorter, more seed-robust sibling of the 50/200 variant.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.05 (effective 1.5).
**Turn Structure:** alternating, 1 piece/turn.
**Hybrid actions:** no.
**Soft violations flagged:** **helper under-displays komi (shows 0.05, engine applies 1.5)**; vestigial `adjacent_empty`; `target_dimension_p2=-1` is a mirror flag.

### Scores (1–10)
- **Strategic Depth: 4** — same one-dominant-plan packing race as Game 1; decay 0.7 adds a sliver of compactness nuance. The komi tiebreak adds a thin "cross before they do" tension near the line.
- **Emergent Complexity: 3.5** — contiguity-as-armor + komi-as-tiebreak; nothing beyond the family baseline.
- **Balance: 4.5** — best of the menger pod: the real 1.5 komi (plus pie) genuinely balances and even flips the mirror to P2; calibration bias 0.015 is believable. Highest balance score I'll give in the pod.
- **Novelty (post-adversary): 3.5** — see Phase 4; intra-family difference is robustness, not depth.
- **Replayability: 3.5** — converges to compact packing; opening variety shallow.
- **Overall "Would an agent team play this again?": 4.0** — A well-balanced, cleanly-resolving member of the menger packing-race family. Above R20 production mean (3.73), below R8 (4.10) and R19 menger top (4.8); does not approach the 5.0 G1 ceiling. Marginally the better-engineered of the sibling pair on balance/robustness, but no deeper.

### CLOSEST KNOWN-GAME ANALOG
Go area-scoring packing sprint with Ataxx-style flanking capture; inside the corpus, the 30/100 sibling of the R21 menger threshold-race family.

### KILLER FLAWS
- One dominant strategy (compact packing); score-max and capture-safety coincide.
- Helper komi mis-display obscures how much balance work the komi is doing (1.5, not 0.05).
- 3D substrate barely engaged; play lives on 2D faces.

### BEST QUALITY
The seat balance: the shorter race + a properly-scaled 1.5 komi produce the cleanest mirror balance in the menger pod — the komi actually decides the symmetric race rather than being decorative.

### MENGER STRUCTURAL CONTRIBUTION
Same as the pod: restriction, not enrichment. Flattens to carpet with minimal loss.

### IMPROVEMENT IDEAS
**Single best change:** as with Game 1, break the score-max/safety coincidence (diminishing returns on saturated cells) so players must spread and expose stones — turning the packing sprint into a real risk/reward race.
Secondary:
- Fix the helper to display the true komi (`komi_p2 × threshold`).
- Keep the shorter threshold (it's the robustness win) but add a contesting incentive so the race isn't a pure mirror.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-1_gamee52e8889517a.md`.*
