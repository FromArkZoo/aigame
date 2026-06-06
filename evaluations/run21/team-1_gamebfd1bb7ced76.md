# Run 21 Agent-Team Eval — team-1 — Game bfd1bb7ced76

**Team ID:** team-1
**Game ID:** bfd1bb7ced76 (menger slate **rank 5**, 20-seed mean GE 0.126, σ 0.070, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game bfd1bb7ced76` (see `briefing_menger_bfd1bb7ced76.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Same Menger sponge (9×9×9, 400/729 active, dense carpet faces). Cell = z·81 + y·9 + x.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **200** — but the race ends ~ply 23, so the cap **never binds** (inert).

**Action space.** 731 actions (729 place + pass + pie 730). Place-only; `adjacent_empty` vestigial.

**Placement & capture.** **outnumber-2** (identical to the rest of the pod). Isolated stones cleared when enemy neighbors exceed friendly by ≥2; interior cluster stones immune.

**Propagation.** influence, radius 1, strength 1.0, **decay 0.7** (compounding compact clusters; two adjacent friendlies = 3.4).

**Win condition.** threshold-race. Effective owned-influence > **30.0**. `target_dimension_p2=-1` mirror. **komi_p2 = 0.00** → no engine komi (komi = 0 × 30 = 0). Balance rests on the pie swap alone.

**Pie rule.** True (action 730).

**Canonical-kernel finding (dedup / G2).** Flattened-blob diff: **bfd1bb7ced76 ≡ e52e8889517a except `max_turns` (200 vs 100)**. Everything else — decay-0.7 propagation, threshold 30, outnumber-2, topology, pie — is byte-identical. Because both games resolve ~ply 23, the max_turns difference is **inert in play**. The *only* effective difference between this game and e52 is the externally-applied komi (0 here, 0.05 there). So this is essentially "e52 with komi turned off." The slate's "7 distinct canonical kernels" claim is generous for the menger pod: it is really decay∈{0.7,1.0} × threshold∈{30,50} × komi∈{0,0.05} with max_turns inert.

**Degeneracy check.** max_turns 200 inert; `adjacent_empty` vestigial; mirror flag; helper komi display would read 0.00 (correct here since komi is genuinely 0).

---

## Phase 2 — Strategic Play

All moves engine-verified. Place ids = cell indices; pass = 729; pie = 730.

### Game 1 — P1 packs left vs P2 packs right (uncontested mirror) — **P1 tempo win**
Sequence: `0,6,1,7,2,8,9,15,11,17,18,24,19,25,20,26,27,33,28,34,29,35,36,42,38,44` (23 plies to resolution).
Plot: lockstep climb, P1 ~3.8 ahead. Ply 21 P1 raw 29.2, ply 23 **P1 → 31.6 > 30, Done, Winner=1** while P2 sits at 29.2. With komi 0, P1's move-first tempo wins cleanly — exactly Game 1's outcome but at decay-0.7 pace. Contrast with e52, where the 1.5 komi flipped the same line to P2.
Reflection: this game is the *less-balanced* sibling — same race, but the balancing komi is off, so P1's tempo edge is uncorrected (only pie can offset it).

### Game 2 — Capture-contest
Sequence: `2,1,72,3`.
Plot: outnumber-2 clears P1's isolated (2,0,0) once P2 brackets it — same deterrent dynamic; two-for-one tempo cost; useless against tight packing.

### Game 3 — Pie-swap balance
Sequence: `0,730,...`.
Plot: swap transfers P1's opener and the tempo to P2 — the only balancer present here. Without komi, a P1 who grabs the best opening must fear the swap; openings being near-equivalent, swap mostly trades tempo and leaves a residual ~0.060 P1 edge.

### Strategy guides
**P1:** pack the densest carpet face compactly, ride the tempo to 30 before P2 (no komi to fear).
**P2:** mirror-pack but you *lose* the clean mirror by a tempo (no komi); swap at ply 2 to take the tempo, or capture only if P1 scatters.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** One (compact packing) + binary swap — identical to the rest of the pod. DB strategic_diversity 1.0 is single-seed and not borne out in play.
**Counter-play.** Partial (swap only); capture can't beat packing.
**Short-term vs long-term.** Short (~23 plies). max_turns 200 is irrelevant.
**Emergent concepts observed.** Contiguity-as-armor; swap-to-inherit. No komi tiebreak (komi 0), so even thinner than e52.
**Does menger matter?** No more than the pod — restriction, not enrichment; flattens to carpet.
**Does the propagation kernel matter?** It's the win metric; decay 0.7 rewards compactness.
**Capture contribution.** Deterrent only.
**First-mover advantage / seat balance.** **Worst-balanced of the three decay-0.7 games** in the mirror: komi 0 leaves P1's tempo edge uncorrected; only pie offsets it (residual bias ~0.060). The briefing's "reliable learner" framing is about PPO training stability, not seat balance.

**Reliability↔quality (the briefing's question).** This game is the most reliable PPO learner *because* it is the most convergent packing race — the very property (one dominant strategy, pack-tight) that makes it shallow also makes it reliably trainable. So **reliability here anti-correlates with depth**: low strategic diversity → stable PPO convergence → unremarkable game. Stability is not a depth signal.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same family as Games 1–2: influence packing race + flanking capture on a fractal.
(a)–(e) identical analysis to the pod: Go-area sprint + Ataxx capture; ~5-min expert transfer; substrate restricts rather than innovates.
**Intra-family differentiator (the job):** versus e52, the only live difference is komi-off → P1 tempo win instead of P2 komi win. Versus the longer sibling 1fea, shorter/komi-less. So bfd1 is the *barest* of the pod — the control that shows the family with no balancing applied.
**Closest known-game analogue:** Go-area packing race + Ataxx capture.
**Comparison to R8 (4.10):** thinner (no counter-strategy).
**Comparison to R19/R20:** same family as R19 menger top (4.8); a plainer, komi-less parameterization.

**Novelty score (post-adversary): 3.5/10.** No new mechanic; near-duplicate kernel of e52.

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** bfd1bb7ced76
**Rules Summary:** A Menger packing race to 30 points of own-color influence (decay 0.7) with outnumber-2 flanking deletion as a deterrent — effectively the e52 sibling with the balancing komi switched off, so P1 wins the mirror by tempo and balance rests on the pie swap. The pod's most reliable PPO learner, because it is its most convergent (and therefore shallowest) member.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating, 1 piece/turn.
**Hybrid actions:** no.
**Soft violations flagged:** max_turns 200 inert; near-duplicate kernel of e52 (G2 dedup concern); vestigial `adjacent_empty`.

### Scores (1–10)
- **Strategic Depth: 4** — same one-plan packing race; decay 0.7 compactness nuance; no komi tension. Engine strategic_depth 0.605 overstates the felt experience.
- **Emergent Complexity: 3.5** — contiguity-as-armor; nothing past family baseline.
- **Balance: 4** — komi off, so the mirror has an uncorrected P1 tempo edge; only pie balances (residual ~0.060). Worse than e52's komi+pie.
- **Novelty (post-adversary): 3.5** — near-duplicate of e52; no new idea.
- **Replayability: 3.5** — converges to compact packing; the *most* convergent of the pod (hence "reliable").
- **Overall "Would an agent team play this again?": 3.9** — A clean but bare packing race; the pod's reliability-control. Above R20 production mean (3.73), below R8 (4.10) and R19 menger top (4.8); nowhere near 5.0. Reliability ≠ depth — this is the pod's plainest member.

### CLOSEST KNOWN-GAME ANALOG
Go-area packing sprint with Ataxx flanking capture; inside the corpus, a komi-less near-twin of e52e8889517a.

### KILLER FLAWS
- **Near-duplicate kernel of e52** (only max_turns differs, and it's inert) — minimal independent contribution to the slate.
- One dominant strategy; score-max and safety coincide.
- Komi off → uncorrected first-mover edge in the mirror.

### BEST QUALITY
As a *game* there is no crown jewel beyond the pod's contiguity-as-armor; its distinction is purely the PPO-training reliability, which the agent-eval is told to discount.

### MENGER STRUCTURAL CONTRIBUTION
Same as pod: restriction, not enrichment; flattens to carpet.

### IMPROVEMENT IDEAS
**Single best change:** drop this game from the slate or give it the e52 komi — as-is it duplicates e52 minus balance and adds little. If kept, break the score/safety coincidence (diminishing returns on saturated cells) as for the rest of the pod.
Secondary:
- Apply a real komi (it currently rests on pie alone).
- Use the inert max_turns 200 for something (e.g. a longer threshold) or revert it.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-1_gamebfd1bb7ced76.md`.*
