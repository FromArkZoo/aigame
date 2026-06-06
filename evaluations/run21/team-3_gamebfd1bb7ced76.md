# Run 21 Agent-Team Eval — team-3 — Game bfd1bb7ced76

**Team ID:** team-3
**Game ID:** bfd1bb7ced76 (menger slate rank-5, 20-seed mean GE 0.126, σ 0.070, calibrated komi_p2 0.00)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=True)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game bfd1bb7ced76` (see `briefing_menger_bfd1bb7ced76.md`).

---

## Phase 1 — Rule Comprehension

**Board.** Menger sponge, 400/729, max_degree 6, holes break neighbourhoods. `c = z*81 + y*9 + x`.

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = **200**.

**Action space.** 731 (729 place + pass + pie 730); placement anywhere-empty.

**Placement & capture.** outnumber-2, clears to empty. Fires only against exposed stones.

**Propagation.** influence, r=1, strength 1.0, **decay 0.7**. Packing law 1 + 1.4k (line tip +2.4, inner corner +3.8) — verified.

**Win condition.** threshold-race > **30.0**; mirror P2; **engine komi = 0 × 30 = 0** (komi_p2 = 0). max_turns 200.

**Pie rule.** True (action 730) — the actual balancer (no komi).

**Degeneracy check.** `adjacent_empty` vestigial; capture inert vs packed play; threshold + decay live. No komi to mis-display. Genuinely threshold dispatch (not connection).

---

## Phase 2 — Strategic Play

All moves engine-verified.

### Game 1 — P1 corner pack vs P2 mirror (P1 tempo wins)
Sequence: `0,162,1,163,2,164,9,171,11,173,18,180,19,181,20,182,27,189,28,190,29,191,33,195` (23 plies, **P1 wins (Winner=1)**).
Plot: symmetric packing; with komi 0, P1's one-stone tempo lead crosses 30 first (ply 23). The mirror image of game e52e8889517a — *same structure, opposite winner*, decided purely by the komi sign (0 here → P1; +1.5 there → P2). This pair is a clean demonstration that the menger race's "balance" is entirely a komi-sign artifact.

### Game 2 — P2 out-packs the dense corner (density beats tempo) — the headline line
Sequence: `4,0,5,1,6,2,3,9,7,11,8,18,17,19,26,20,35,28` (18 plies). P1 spread along the y=0 row and scattered tips; P2 packed the high-coordination top-left corner block (0,1,2,9,11,18,19,20,28). **By ply 18 P2 led +20.9 vs P1 +19.5 — a tempo-down player overtaking by superior region choice.** This is the single most instructive line I played in the menger pod: it proves the game is not a pure tempo race; packing density is a real, decisive lever.

### Game 3 — Capture probe
outnumber-2 fires only when a stone has 0 friendly neighbours and ≥2 enemy flanks; never against the packed blobs both players naturally build. Inert in competent play.

### Strategy guides
**P1:** seize the densest hole-free block first (the menger solid corners), keep the blob compact; the tempo lead converts only if you don't waste it on low-contact cells.
**P2:** with komi 0 you are a tempo down — your equaliser is **out-packing**: choose a denser region than P1 and win on coordination, as in Game 2. Pie swap (730) is available if P1 grabs the best block.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Yes — highest in the menger pod (diversity 1.000, non_triviality 1.000).** Multiple packing families reach 30 in comparable plies, and (Game 2) a non-mirror denser plan can beat the tempo leader. Subjectively the richest of the four menger games.
**Counter-play.** Real: out-pack. Pie. Captures still not a counter.
**Short-term vs long-term.** ~1-ply per move, but the *region-selection* decision early on has medium-term consequence (a denser block compounds). Slightly more horizon than its siblings.
**Emergent concepts.** Density-beats-tempo (clearest here); packing law; multi-family opening freedom.
**Does menger matter?** Most of any menger game — diversity 1.0 means the fractal's varied dense regions all matter.
**Does the kernel matter?** decay 0.7 supports the region-choice nuance.
**Capture contribution.** Inert.
**First-mover / seat balance.** komi 0, residual bias ~0.06 (P1 tempo); pie is the balancer. **README "stability ↔ quality" test:** this is the most reliable learner (0% zero-failure seeds, S5 elite Δ only −0.064). My finding — reliability *does* correlate with the best play-quality in the menger pod (diversity 1.0, density lever most alive), but the per-stone game is still 1-ply packing, so the correlation is "stable ↔ moderately good," not "stable ↔ deep."

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same kernel as the menger family; differentiators are komi 0 and max_turns 200 (and the reliability profile).
(a)(b)(c) Threshold-race influence + outnumber on a sponge = R20 menger family; closest external = disc-counting territory race.
(d) Fractal = geometric novelty.
(e) ~5 min expert transfer.

**Closest known-game analogue:** R20 menger threshold-race family; the most diversity-rich member.
**Comparison to R8 (4.10).** No goal-shape, but better balanced; captures equally inert.
**Comparison to R19/R20.** Same family as R20 5f5c (my team 4.0); marginally richer opening (diversity 1.0).

**Novelty score (post-adversary):** **3/10.** Family member; its distinction is reliability + diversity, not a new mechanic. Anchor R8 4.10.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** bfd1bb7ced76
**Rules Summary:** Menger packing race to 30 with decay-0.7 influence and no komi; P1's tempo wins symmetric play, but a denser non-mirror plan (Game 2) can overtake it. The most reliable, most diversity-rich menger game.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=True, komi_p2=0.00.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** outnumber-2 inert vs packed play; `adjacent_empty` vestigial; residual P1 tempo bias ~0.06 (komi 0, pie is the only balancer).

### Scores (1–10)
- **Strategic Depth: 4** — Region-selection has the most medium-term consequence of any menger game (density compounds), but moves are still ~1-ply. DB depth 0.605 is the pod's highest and is partly justified by the diversity.
- **Emergent Complexity: 4** — Density-beats-tempo is cleanest here; multi-family openings.
- **Balance: 4** — komi 0, P1 tempo bias ~0.06; only pie balances. The out-pack counter gives P2 a genuine equaliser, which mitigates.
- **Novelty (post-adversary): 3** — Menger family member; distinction is reliability/diversity.
- **Replayability: 5** — Diversity 1.000 and the density lever make openings genuinely varied; the best replay value in the menger pod.
- **Overall "Would an agent team play this again?": 4.1** — The most playable menger game: reliably learnable, most diverse, the density-beats-tempo lever is real. Stability **did** track quality here. Still ~1-ply at the core; above R20 production (3.73), at ~R8 replay (4.10), below the R19 ceiling.

### CLOSEST KNOWN-GAME ANALOG
R20 menger threshold-race family (the diversity-rich member); externally a disc-counting territory race with no flips.

### KILLER FLAWS
- Captures inert; per-stone decisions ~1-ply.
- Balance leans on pie alone (komi 0); residual P1 tempo edge.

### BEST QUALITY
**Density-beats-tempo with diversity 1.0:** multiple dense regions compete and a tempo-down player can win on coordination — the richest opening of the four menger games, and it is also the most reliable learner (the stability↔quality finding).

### MENGER STRUCTURAL CONTRIBUTION
Highest of the menger pod — the varied dense regions of the fractal all matter for region selection. Would be markedly more trivial on a flat grid.

### IMPROVEMENT IDEAS
**Single best change:** keep decay 0.7 and diversity but add a *live* tactical layer (e.g. make captures swing the race) so the rich opening isn't followed by a mechanical 1-ply mid/endgame.
Secondary:
- Add a small komi to remove the residual P1 tempo edge without over-correcting (the e52e sibling shows 0.05 over-corrects at threshold 30 — tune lower).
