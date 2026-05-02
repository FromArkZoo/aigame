# Run 19 Evaluation — team-4 — Game b48208268f2a

**Team ID:** team-4
**Game ID:** `b48208268f2a` (Carpet rank-2, GE 0.3069, ELO 2255.7)
**Substrate:** Sierpinski carpet, axis 9, 64 active cells / 81 grid positions, max_degree 4 (effective 2–4).
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game b48208268f2a` (see `briefing_carpet_rank2.md`).

---

## Phase 1 — Rule Comprehension

**Board / Turn / Action.** Same 9×9 sierpinski carpet as rank-1. 64 active cells, 17 holes, max_degree 4, place-only, alternating, P1 first, max_turns = 100.

**Capture (custodian).** Othello-style sandwich-and-flip. **Empirically verified** the briefing's threshold=2 parameter is *inert*: a single P1-P2-P1 bracket DOES flip the lone P2 stone (Phase 2 Game 2 turn 3 confirmed). The engine's `_capture_custodian` (engine_v2.py:502–542) doesn't reference threshold — any non-empty contiguous run of enemies bracketed by friendlies flips. **Threshold parameter is documentation noise.**

**Propagation.** Influence, r=2, s=1.0, d=0.5. Same as rank-1.

**Win.** Threshold-race > 30.0. Max turns 100.

**Other rules.** `needs_ko_rule = True` — super-ko active. Same as all R19 games.

**Degeneracy check.**
- Capture threshold parameter is dead. Documentation says "minimum run length 2" but engine treats any-run as capturable.
- Custodian flip changes ownership but **does NOT modify board_values**. The flipped cells retain their pre-flip propagation history, including heavy negative values from prior enemy reinforcement. This is the critical observation neither the briefing nor the pilot surfaces.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — 1-stone P1 flip (briefing-quirk verification)

Sequence: `0,9,18` (3 plies).

Plot:
- P1 (0,0). P2 (0,1). P1 (0,2): walks +y from (0,2) — finds P2 at (0,1), then P1 at (0,0). Bracket; flip (0,1) to P1.
- After ply 3: P1 has 3 stones (originally 2 + 1 flipped). P2 has 0.

**Verifies the briefing-flagged quirk:** custodian-2 fires on a single-enemy bracket, contradicting the threshold=2 parameter. The team-lead's "verify behaviour empirically" instruction was correct. **Briefing's threshold reading is wrong; engine ignores threshold for custodian.**

### Game 2 — Custodian flip on 3-stone P2 chain (the Pyrrhic discovery)

Sequence: `0,9,18,1,11,2,29,3,4` (9 plies).

Plot:
- P1 (0,0); P2 (0,1); P1 (0,2) — flip (0,1) to P1. P1 has 3, P2 has 0. Score P1=+1.5, P2=0.
- P2 (1,0). P1 (2,1). P2 (2,0). Score P1=+0.75, P2=+1.75 — **P2 has overtaken**, with 2 stones in a y=0 segment.
- P1 (2,3) — defensive build. P2 (3,0) — extends chain to 3 stones {(1,0), (2,0), (3,0)}. Score P1=+2.0, P2=+4.0. **P2 leads by +2.0 with a 3-stone collinear chain.**
- **P1 (4,0): walks −x from (4,0) — P2@(3,0), P2@(2,0), P2@(1,0), P1@(0,0). Bracket! All 3 P2 stones flip to P1.** P1 piece count goes from 5 → 9 (added (4,0) + 3 flipped). P2 piece count: 3 → 0.
- **Critical: P1 score crashes from +2.0 to −1.0**. The flipped stones (1,0), (2,0), (3,0) have residual board_values −1.25, −1.00, −1.00 from prior P2 placements + P2 mutual propagation. These contribute to P1's score sum as raw negative values. P1 captured 3 stones in piece count but **lost** 3.0 effective score.

Reflection: **The Pyrrhic-flip dynamic.** This is the most significant discovery I've made across all 6 R19 games and the pilot completely missed it. The pilot's description of custodian-flip as creating a "+5.5 cluster" is wrong for chains longer than 1: longer chains carry heavy negative residual values, and flipping them transfers those values to the captor. **For a 3+ stone enemy chain, flipping is net-negative for the captor's threshold race despite gaining piece count.**

This is a *real* strategic balance restorer. P2 can build long chains specifically to make a P1 flip Pyrrhic. P1's optimal play becomes: flip *short* P2 runs (1-stone flips are net-positive: +1.0 placement, gain ownership of −0.5 cell ⇒ net +1.5 own − 0.5 capture = neutral-to-slightly-positive); avoid flipping *long* P2 chains.

### Game 3 — P2 builds "poison chain" to lure flip (sketch)

Sketch (not played out, but mechanically clear from Game 2):
- P1 anchors at corner. P2 builds a 3-stone line nearby with mutual reinforcement (each at −1.0 from placement + −0.5 from neighbours = ~−2.0 each).
- P2 deliberately leaves the bracketing gap open. P1 flips, but the captured stones are at total ~−6.0 effective.
- P1 lost ~6 effective score; P2 lost their chain's contribution. Net: P1 down ~6, P2 down ~+4 (chain effective value lost). **P2 actually gains 2 effective score** from the trade in this scenario.
- For P1 to avoid this, they must NOT flip long chains. So P2's chain is "poisoned" and forces P1 to play around it rather than capture it.

This is a genuine strategic axis the pilot didn't surface: **P2 has a real positional resource (poison chains) that P1 has to navigate around.**

### Strategy guides

**P1 (offence/threshold push):** Anchor at corner; build flanking pairs at distance 2 ((0,0), (2,0), (0,2)). **Only flip P2 runs of length 1** — these are positive-value captures (gain own stone + claim a +0 cell). **Do NOT flip P2 chains of length 3+** — those are Pyrrhic. Treat long P2 chains as if they were holes: build around them.

**P2 (defence + offence):** Don't play single stones adjacent to P1 corner pairs (avoid 1-stone flips). **Build long chains (3+ stones) deliberately** as positional resources — they're flip-poisoned and force P1 to navigate around. Race to threshold via the chain's own influence accumulation.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Three (one more than pilot identified):
1. **Cluster-and-flip-short** (P1's playbook). Anchor + flank + flip 1-stone P2 runs only.
2. **Poison-chain-and-build** (P2's playbook). Build 3+ stone chains deliberately to deny P1 the easy flip; race threshold via the chain's reinforcement.
3. **Avoid-cluster** (P2's defensive). Spread stones at distance 3+ to prevent any flip; standard mirror but with carpet-aware spacing.

**Counter-play.** Real and deeper than pilot found. Custodian's Pyrrhic-flip mechanic is a *real* P2 counter to P1's first-move advantage — the pilot's read that "custodian skews balance further toward P1 than outnumber" is incorrect because it ignores residual values.

**Short-term vs long-term.** Threshold 30 / per-stone gain ~+2.0 → ~15 stones each → ~30-ply games. Custodian flips create 4–6 ply tactical sequences with the **residual-value calculation** as the deepest decision: "should I flip this chain?" requires reading `board_values` 2-deep, not just owner counts.

**Emergent concepts observed.**
- **Pyrrhic flip / poison chain.** New: long enemy chains carry heavy negative residual values; flipping them reduces the captor's effective score. **Major strategic axis missed by pilot.**
- **Flip-as-cluster-builder for short runs.** 1-stone flips are net-positive (3-stone collinear cluster ~+5.0 effective), as pilot described. Only long runs are poisoned.
- **Hole-bottleneck routing.** Same as carpet rank-1.
- **Tempo crossover.** Same as rank-1.

**Does the carpet substrate matter?** Same modest contribution as carpet rank-1. ~+0.5 depth via hole-edge geometry. 17 holes provide local strategic variation but don't change the family.

**Does the propagation kernel matter?** **More than rank-1**, because the Pyrrhic-flip dynamic is sensitive to residual board_values. r=2 with decay 0.5 gives strong distance-2 reinforcement that makes 3+ stone chains particularly poisoned (each chain stone at −1.0 + −0.5 + −0.25 = ~−1.75 effective value). With weaker decay, chains would be less poisoned and the pilot's analysis would be more correct.

**Capture-rule contribution.** Custodian + influence + Pyrrhic-flip is a richer interaction than pilot identified. Captures fire frequently but their *value* is conditional on residual board_values — a real strategic puzzle each move.

**First-mover advantage / seat balance.** **Better than pilot's 3/10.** P1 has the first-move advantage but custodian doesn't compound it because long-chain flips are Pyrrhic. PPO trained-vs-random WR 0.707 (lower than the 5 other R19 games) — pilot read this as "harder for PPO to learn dominant play"; I read it as **"the strategic surface is genuinely noisier because Pyrrhic-flip decisions are non-monotonic"** — PPO has to learn when to flip and when to walk away, not just how to flip everything.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Influence + custodian + threshold-race + super-ko on a 2D Sierpinski carpet, with **emergent Pyrrhic-flip dynamics**.

(a) **Custodian capture** is Othello (1971). Maximum familiarity.

(b) **Influence-as-scoring with weighted spread** is *Tumbleweed* / *Sygo*. Combined with custodian, this is novel — Othello scores by piece-count-at-end, not by influence-on-owned-cells.

(c) **The Pyrrhic-flip dynamic** is **the irreducibly new piece**. In Othello the captured stones don't have weighted values — flipping is always good. Here, flipping a long chain transfers heavy negative values to the captor. **This is a genuinely new mechanical primitive.**

(d) **Sierpinski carpet substrate.** Same as rank-1.

(e) **Super-ko on custodian capture.** Standard in Go; non-standard in Othello (which doesn't normally need super-ko because flips are deterministic). Active here, presumably to prevent capture/recapture cycles in the Pyrrhic-flip space.

(f) **Expert-transfer test.** Othello + Tumbleweed player ensemble understands the rules in 5 minutes. The novel piece they'd need to learn: **the Pyrrhic-flip dynamic** (read residual board_values before flipping).

**Closest known-game analogue:** **Othello with influence-weighted scoring + Pyrrhic-flip on a Sierpinski carpet.** No published analogue. **The Pyrrhic-flip mechanic alone differentiates this from any known Othello variant.**

**Comparison to R8's Connection Go (8/10).** R8 used custodian + connection. R19 carpet rank-2 uses custodian + influence-threshold. **Both share the custodian primitive.** R19 carpet rank-2's Pyrrhic-flip dynamic is mechanically richer than R8's pure custodian-flip-fills-chain — R8 doesn't have residual values that can poison a flip. **R19 carpet rank-2 may be R19's deepest custodian-family game, even if its execution is rougher than R8's.**

**Player rebuttal.**
- **Pyrrhic-flip is a real new tactical pattern** that doesn't transfer from Othello (no influence values), Reversi (same), or any custodian game in the R8–R18 corpus (none of those used influence scoring).
- **Long-chain poisoning** is a P2 positional resource that doesn't exist in standard custodian games. The pilot missed this and scored P2 balance accordingly low.
- Subtracts: family is recognisable Othello + influence; the carpet substrate is shared with rank-1.

**Novelty score (post-adversary):** **6/10.** **Above pilot's 5.** The Pyrrhic-flip dynamic is genuinely new and the pilot didn't credit it. Above carpet rank-1 (5) by margin; same as menger ranks 1–3 (6) for novelty driven by an interaction-layer mechanic rather than substrate.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** b48208268f2a
**Rules Summary:** Place stones on a 9×9 Sierpinski carpet to accumulate r=2 influence on owned cells. Othello-style custodian flip captures bracketed enemy runs, but flipped stones retain their residual values — **flipping long enemy chains is Pyrrhic**, transferring negative values to the captor. First to >30.0 wins.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.
**Quirks discovered:** (a) custodian threshold parameter is inert (single-enemy bracket fires); (b) **Pyrrhic flip** — flipping long chains (3+ stones) transfers negative residual values to the captor and can crash effective score; (c) super-ko active.

### Scores (1–10)

- **Strategic Depth: 6** — **Above pilot's 5.** Pyrrhic-flip + poison-chain + flip-short-runs-only is a real 3-axis decision space that pilot missed. Custodian + influence interaction creates depth that simpler outnumber+influence (rank-1) doesn't.
- **Emergent Complexity: 6** — Pyrrhic-flip dynamic is non-obvious and substrate-independent (would emerge on any custodian + influence + threshold game). New emergent vocabulary beyond pilot's identification.
- **Balance: 5** — **Above pilot's 3.** Pyrrhic-flip gives P2 a real defensive resource (poison-chain). The PPO 0.707 trained-vs-random WR pilot read as "P2 weak" actually reflects "the strategic surface is non-monotonic and harder to learn" — same data, opposite conclusion. Mirror still loses for P2 but the Pyrrhic dynamic substantially closes the gap.
- **Novelty (post-adversary): 6** — Above pilot's 5. The Pyrrhic-flip mechanic is a genuinely new tactical primitive not present in any custodian-family game I'm aware of. Above carpet rank-1.
- **Replayability: 5** — Above pilot's 4. Pyrrhic-flip decisions create position variety ("should I flip?") that mirror+sandwich families don't have. 64-cell board still limits raw variety.
- **Overall "Would I play this again?": 6** — **Above pilot's 4.** Once: yes, the Pyrrhic discovery is satisfying. Repeatedly: yes, the flip-or-walk decisions are genuinely interesting. Anchor: above R17 mean (3.5), above R17 best (4.14), well below R8 (8). **Likely R19's most-underrated game by the pilot's evaluation.**

### CLOSEST KNOWN-GAME ANALOG
**Othello with influence-weighted scoring + Pyrrhic-flip on a Sierpinski carpet.** No published analogue. The Pyrrhic-flip mechanic alone differentiates from any known Othello variant. In-corpus: closest to R8's Connection Go (both share custodian primitive); arguably the closest R19 game to R8's family by mechanic.

### KILLER FLAWS
- **Custodian threshold parameter is inert.** The rule blob says threshold=2 but engine ignores it. Documentation/rule-blob hygiene issue.
- **Mirror = P1 wins on tempo** (same as all R19 games).
- **Pilot underrated this game by ~1 point on most axes.** This isn't really a flaw of the game itself but is worth noting for the cross-team variance analysis.
- **64-cell board limits position variety** despite the Pyrrhic-flip depth.
- **PPO struggled to learn cleanly** (0.707 vs random) — likely reflects non-monotonic strategic surface, but also means PPO's ELO/GE rankings may underrate this game.

### BEST QUALITY
**The Pyrrhic-flip dynamic.** Custodian + influence-weighted scoring creates an interaction where capturing long chains transfers heavy negative residual values to the captor — flipping is conditionally good. This is the most genuinely novel mechanical primitive I've encountered across all 6 R19 games. It produces real strategic depth (when to flip vs walk away), restores some seat balance (P2 has poison-chain resource), and is substrate-independent (would work on any custodian+influence+threshold game).

### CARPET STRUCTURAL CONTRIBUTION
**Modest, same as rank-1.** ~+0.5 depth via hole-edge geometry. The Pyrrhic-flip dynamic is the much bigger novelty source here, and it's substrate-independent. **The carpet is doing about half the work pilot's analysis attributed to the substrate.**

### IMPROVEMENT IDEAS
**Single best change: pie rule.** Cross-cutting recommendation. Same as all R19 games.

Secondary improvements:
- **Document Pyrrhic-flip dynamic in briefing.** This is the real depth source and the pilot's analysis missed it.
- **Strip the inert threshold parameter from custodian rule blobs.** It's documentation noise.
- **Test custodian + influence + connection win condition** (R8 family with Pyrrhic-flip). Adds narrative arc to the game's deepest mechanic. **Strongest R20 candidate from this evaluation, alongside menger rank-3.**
- **Reduce decay to 0.30** (menger rank-2's value). Would soften residual values and reduce Pyrrhic-flip severity. Would make the game feel more like standard Othello + influence; trades Pyrrhic depth for simpler balance.

### What evolution did or didn't add (vs rank-1 child)
The briefing notes carpet rank-1 was crossover-derived from this seed (rank-2) × `eb301d1bf7f6`. **Crossover replaced custodian with outnumber.** Outnumber removes the Pyrrhic dynamic entirely (captures clear stones rather than flipping them, so no residual-value transfer). The R19 evolution effectively *traded depth for clarity*: the rank-1 outnumber game scores higher GE because PPO can learn it more cleanly, but the rank-2 custodian game has richer interaction layer. **The pilot's read was correct that crossover is "what evolution did"; my read of "what was lost" is more critical: the crossover lost the Pyrrhic-flip dynamic, which I think is genuinely the deepest mechanic in the family.**

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-4_gameb48208268f2a.md`.*
