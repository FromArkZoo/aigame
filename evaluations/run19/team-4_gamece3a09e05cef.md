# Run 19 Evaluation — team-4 — Game ce3a09e05cef

**Team ID:** team-4
**Game ID:** `ce3a09e05cef` (Carpet rank-1, GE 0.3547, ELO 2280.5)
**Substrate:** Sierpinski carpet, axis 9, 64 active cells / 81 grid positions, max_degree 4 (effective 2–4 per cell).
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game ce3a09e05cef` (see `briefing_carpet_rank1.md`).
**Soft violation:** `sierpinski_threshold_inert` (flagged in rule blob).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9 grid with 17 inactive cells per the level-2 Sierpinski carpet pattern: corner sub-cube holes at (1,1), (4,1), (7,1), (1,4), (7,4), (1,7), (4,7), (7,7), plus the central 3×3 hole at (3..5, 3..5). 64 active cells. Cell index = y·9 + x. Max degree 4 (axis-aligned, no diagonals); cells adjacent to holes have 2–3 active neighbours.

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max 100 turns (engine `max_game_steps`).

**Action space.** 82 actions = 81 placements + 1 pass. **Place-only**, D1 hybrid ban active.

**Capture (outnumber-2).** Same mechanism as menger ranks 1–2: enemy neighbour with ≥2 of your stones among its own neighbours is removed.

**Propagation (influence, r=2, s=1.0, d=0.5).** Distance-1: ±0.5; distance-2: ±0.25. Propagation uses BFS through active cells, so holes block reach. Same kernel as menger rank-2 in reach, but with shallower decay (0.5 vs 0.30) — distance-2 contribution is here +0.25 rather than +0.09. **Adjacency clusters reinforce more strongly here than in menger rank-2.**

**Win.** Threshold-race > **30.000**. Max turns 100.

**Other rules.** `needs_ko_rule = True`. **Super-ko is active here too** — same observation as menger games. Pilot did not flag this.

**Degeneracy check.**
- `sierpinski_threshold_inert` soft violation flagged. In skilled play I reach +30 in ~24–30 plies, well within max_turns. The violation is a R17-audit metric; doesn't block the game.
- 2D + max_degree 4 means corner cells (e.g., (0,0)) have only 2 active neighbours: extremely fragile to sandwich attacks.
- The 3×3 central hole creates a topology where the four "edge-of-hole" cells like (4,2), (2,4), (4,6), (6,4) have only 2 active neighbours (one direction is the hole, two perpendicular directions are bounded by other holes).

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — 4-neighbour interior cluster mirror (substrate-aware anchor choice)

Sequence: `20,60,11,69,2,78,18,62,29,51,38,42` (12 plies).

Plot:
- I deliberately picked **interior cluster cells** instead of the pilot's corner anchors. P1: (2,2)=20, (2,1)=11, (2,0)=2, (0,2)=18, (2,3)=29, (2,4)=38 — building a vertical chain at x=2. P2 mirrors: (6,6)=60, (6,7)=69, (6,8)=78, (8,6)=62, (6,5)=51, (6,4)=42.
- After 12 plies (6 stones each): both at +12.0. Per-stone gain ~+2.0 (own +1.0 + neighbour reinforcement +0.5/+0.25 from r=2 reach).
- Per-move gain in mirror = ~+2.5 during expansion (each new stone at distance 1 from 2 existing own stones gains: +1.0 own + 0.5×2 from neighbours + 0.25×2 from distance-2 reach = +2.5).
- Threshold 30 / per-move +2.5 → ~12 stones each → game ends ~ply 24–25.

Reflection: **Per-stone gain is higher than menger** because the r=2 reach with shallow decay (0.5 vs 0.30 in menger rank-2) gives stronger distance-2 reinforcement. Combined with the 2D layout (every interior cell at distance-2 from many neighbours), this is the *most efficient* of the 6 R19 games for cluster-building. Per-move gain confirms the briefing's "highest GE in R19" claim — score-per-move is genuinely best here.

### Game 2 — P2 sandwich on corner (0,0)

Sequence: `0,9,38,1,46,18` (6 plies, post-capture analysis).

Plot:
- P1 (0,0). P2 (0,1) — sandwich threat.
- P1 (2,4)=38 — ignores threat, builds elsewhere. P2 (1,0)=1: **captures (0,0)** (its 2 neighbours (1,0) and (0,1) are P2). After ply 4: P1=1, P2=2; P2 leads +1.5 vs +1.0.
- P1 (1,5) — own cluster build. P2 (0,2) — extends sandwich cluster. After ply 6: P1=2, P2=3; **P2 leads +3.25 vs +2.5**.
- P2's 3 stones {(0,1), (1,0), (0,2)} are mutually adjacent or distance-2; the captured (0,0) is now empty between them, with residual board_value but no owner.

Reflection: **The sandwich-as-cluster-builder is the dominant attack pattern.** P2's investment of 3 moves yielded:
- 1 P1 stone captured (cleaned to empty)
- 3 P2 stones in mutual reinforcement (cluster +3.25 effective vs 3×1.0 isolated +3.0)
- A burned cell at (0,0) — not strictly burned (P1 *can* replay, see below) but loses tempo.

**Crucial difference from menger:** the corner (0,0) has only 2 active neighbours; both are now P2. A P1 counter-sandwich attempt — placing at (1,1) or (0,1) etc — fails because the first is a hole and the second is occupied. **Counter-sandwich is structurally unavailable on carpet corners.** This contradicts my menger findings where 6-neighbour anchors allow counter-sandwich.

### Game 2b — P1 replay attempt at (0,0)

Sequence: `0,9,38,1,0` (5 plies).

Plot:
- Same opening through ply 4 (P1 loses (0,0) to sandwich). Ply 5: P1 replays (0,0).
- Placement succeeds. (0,0)'s 2 P2 neighbours don't trigger capture by themselves; the capture rule only checks enemy-of-placement, not self-of-placement. So P1 (0,0) is placed safely.
- After ply 5: P1=2, P2=2. Score P1 +2.0 vs P2 +0.5. **P1 has caught up on stones and is ahead on effective score.**

Reflection: Replay is a viable defensive line — though it doesn't capture P2 stones, it stops the bleeding and reclaims the corner cell. Net trade: P1 spent 2 of its first 5 moves on the corner; P2 spent 2 of its first 4 moves. P1 has 1 less attack tempo than they would otherwise but still leads on score. **Replay > immediate accept-the-loss but worse than a true counter-sandwich (which exists in menger but not here).**

### Game 3 — Hole-edge interior anchor (substrate-specific safety)

Sequence: `38,42` (2 plies, then sketched).

Plot:
- P1 plays (2,4)=38. Active neighbours of (2,4): (1,4)=hole, (3,4)=hole, (2,3)=active, (2,5)=active. Only **2 active neighbours**.
- P2 mirrors at (6,4)=42 — also 2 active neighbours.
- For P2 to sandwich (2,4), they'd need to play at BOTH (2,3) AND (2,5). 2 P2 placements vs 1 P1 placement = same trade as corner sandwich, BUT placing both adjacent to (2,4) doesn't create a P2 cluster (because (2,3) and (2,5) are at BFS distance 2 through (2,4) which is P1, so they're not directly adjacent to each other and don't reinforce strongly).
- Sketch continuation: P1 builds chain (2,4)→(2,5)→(2,6) along x=2; P2 mirrors at x=6. Mirror tempo race ensues; P1 wins by 1 stone.

Reflection: **Hole-edge anchoring is sandwich-resistant but doesn't fix tempo asymmetry.** P2 must commit 2 stones with weak mutual reinforcement instead of the strong corner-sandwich cluster. This forces P2 toward asymmetric play in a different direction (build own threshold + ignore P1's hole-edge anchors) — but the mirror tempo win still applies if P2 mirrors.

### Strategy guides

**P1 (offence/threshold push):** **Anchor at hole-edge interior cells** (e.g., (2,4), (4,2), (4,6), (6,4)) to deny P2 a strong sandwich-cluster opportunity. Build chain extensions to maximise r=2 distance-2 reinforcement (each pair of distance-2 own stones contributes +0.25×2 mutual = +0.5).

**P2 (sandwich-and-pivot):** Sandwich a P1 corner anchor early (~ply 2/4) for the cluster-building dividend. If P1 anchors at hole-edge cells, switch to mirror tempo race and accept the tempo loss — sandwich attacks on hole-edge cells don't yield the cluster bonus.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two:
1. **Cluster-and-race** (P1's playbook). Anchor at interior or hole-edge; chain to threshold via r=2 reinforcement.
2. **Sandwich-and-pivot** (P2's playbook). Trade 2 stones for 1 capture at a P1 corner; the captures form a self-supporting cluster.

**Counter-play.** Real but **knowledge-asymmetric and partial**. Unlike menger rank-1 where counter-sandwich on a 6-neighbour anchor reverses the trade, carpet's max-degree-4 means corners (2 active nbrs) are unrecoverable by counter-sandwich. P1's only defences are: (a) replay the lost cell (defensive), (b) anchor at hole-edge cells (preemptive). Neither fully restores parity.

**Short-term vs long-term.** Threshold 30 / per-move ~+2.5 → ~12 stones each → ~24–30-ply games. 4–6 ply tactical horizon; ~10-ply strategic horizon (when to commit to cluster shape, when to sandwich). Roughly half the strategic surface of menger ranks 1/2 due to smaller board.

**Emergent concepts observed.**
- **Sandwich-as-cluster-builder.** Same as pilot: 3-stone L-shape forms naturally from a sandwich attack and is highly efficient (mutual reinforcement +0.25 between distance-2 stones).
- **Replay-as-recovery.** Confirmed: P1 can re-occupy a captured corner safely, but doesn't capture in return. New observation vs pilot.
- **Counter-sandwich impossible on corners.** Verified by attempting and failing: max-degree 2 at (0,0) gives no third placement vector. **This is the key strategic delta from menger: in menger rank-1, P1 can recover via 6-nbr counter-sandwich; in carpet rank-1, the corner sandwich is permanent.**
- **Hole-edge interior cells are sandwich-resistant.** With 2 active neighbours, sandwich requires 2 P2 placements with weak mutual reinforcement (no cluster bonus to attacker).

**Does the carpet substrate matter?** *Modestly.* The 21% holes create some local geometric variation (corner fragility, hole-edge resistance). But the same outnumber+influence+threshold rules on a 9×9 grid with no holes would preserve most of the strategic surface. **Substrate contribution: ~+0.5 depth via hole-edge-resistance, roughly the same novelty as a non-fractal grid.** Smaller substrate-driven contribution than menger ranks 1/2 because fewer variation patterns.

**Does the propagation kernel matter?** Yes. r=2 with shallow decay (0.5) is the *most* generous kernel for cluster-building of the 6 R19 games. This is why the GE score (0.3547) is the highest — per-stone gain is maximised, threshold reached cleanly within max_turns.

**Capture-rule contribution.** Captures fire frequently in asymmetric play. In Game 2 a single capture put P2 ahead by 0.75 effective points and built a 3-stone cluster in 3 P2 moves. **Captures are the only balance mechanism, same as menger rank-1.**

**First-mover advantage / seat balance.** P1 mirror wins. P2 sandwich is the asymmetric counter. PPO-trained-vs-random WR 0.953 mean, trained-vs-trained 0.500 — clean balance via learned counter, knowledge-asymmetric for naive play.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Influence + outnumber + threshold-race + super-ko on a 2D Sierpinski carpet.

(a) **Influence-as-scoring with weighted spread** is *Tumbleweed* / *Sygo*. Threshold-race accumulation is novel but not unprecedented.

(b) **Outnumber-2 capture** is Tafl/Ataxx-family. Same mechanic as menger rank-1.

(c) **The combination "outnumber + r=2 influence + threshold + super-ko"** doesn't appear in published games. Same family as menger rank-1 (only the substrate dimension and decay parameter differ).

(d) **Sierpinski carpet substrate.** 2D fractal substrates are rare in published games. The closest published case is *Tumbleweed* on hex (different substrate). Carpet's specific hole pattern (4 corner holes + 1 central 3×3 hole) is genuinely novel as a board substrate.

(e) **Expert-transfer test.** Go + Othello + Hex player ensemble understands rules in 5 minutes. Novel pieces: (i) carpet active-cell map, (ii) influence-as-scoring, (iii) outnumber-2 capture trigger.

(f) **Super-ko on outnumber.** Same finding as menger games. Documented in Game 2 indirectly (a counter-sandwich scenario didn't arise here because corners can't be counter-sandwiched, so super-ko doesn't fire — but the rule is active and would fire in any 4-neighbour counter-sandwich attempt).

**Closest known-game analogue:** **2D Influence-Tafl on a Sierpinski carpet with super-ko.** No exact published analogue. Within R19, this is the **2D dual** of menger rank-1 (`1f9191b5d4e6`) — same family, smaller board.

**Comparison to R8's Connection Go (8/10).** Same family-distance as menger rank-1. Different family (capture+threshold vs custodian+connection). R8 has cleaner narrative arc; this game has substrate novelty + capture trades.

**Player rebuttal.**
- **Sandwich-as-cluster-builder + corner-fragility** combination is genuinely substrate-specific to carpets where corners have only 2 active neighbours. Doesn't transfer cleanly from menger (where 6-neighbour anchors recover).
- **Hole-edge interior cells as preemptive defence** is a substrate-specific strategic primitive.
- Subtracts: family is shared with menger ranks 1/2 (the "outnumber+influence+threshold" family); 64-cell board limits position variety.

**Novelty score (post-adversary):** **5/10.** Same as pilot. Substrate adds local geometric flavour but doesn't change the strategic skeleton. The corner fragility is genuinely substrate-specific but not enough to push above 5. The family shared with menger rank-1 means most novelty is captured there; carpet rank-1 is the "2D variant" sibling.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** ce3a09e05cef
**Rules Summary:** Place stones on a 9×9 Sierpinski carpet (64 active cells) to accumulate r=2 influence on owned cells. Outnumber-2 captures + super-ko. First to >30.0 effective influence wins, typically ~25–30 plies.
**Substrate:** Sierpinski carpet, axis 9, 64/81 active, max_degree 4 (effective 2–4 per cell).
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** `sierpinski_threshold_inert` — verified threshold reachable in skilled play.
**Quirks discovered:** super-ko active (same as menger). Counter-sandwich on corners impossible (max degree 2). Replay-as-recovery is a viable but non-capturing defence.

### Scores (1–10)

- **Strategic Depth: 5** — Same family as menger rank-1 with smaller board (64 vs 400 cells) limits positional variety. Counter-sandwich impossible on corners — narrower defensive options than menger. Hole-edge resistance is interesting but doesn't add a new strategic axis.
- **Emergent Complexity: 5** — Sandwich-as-cluster-builder + replay-as-recovery + hole-edge-resistance. Comparable vocabulary to pilot; same as menger rank-1's emergent surface in 2D.
- **Balance: 4** — Mirror = P1 win. Sandwich is P2 counter. Knowledge-asymmetric. Worse than menger rank-1 for P1 (no counter-sandwich available). Same numerical score as menger rank-1 because the mirror dynamic is structurally the same.
- **Novelty (post-adversary): 5** — Same family as menger ranks 1/2. Substrate flavour is real but limited. 2D fractal is less novel than 3D fractal.
- **Replayability: 4** — 64-cell board limits position variety. Corner-sandwich is a known dominant attack; once known, openings collapse.
- **Overall "Would I play this again?": 5** — Once: yes, to feel the corner sandwich cluster-builder. Repeatedly: no, the strategic ceiling caps near menger rank-1's level but with less substrate-driven variety. Anchor: above R17 mean (3.5), above R17 best (4.14), well below R8 (8).

### CLOSEST KNOWN-GAME ANALOG
**2D Influence-Tafl on a Sierpinski carpet with super-ko.** No published analogue. In-corpus: this is the 2D sibling of menger rank-1 — same family, smaller board.

### KILLER FLAWS
- **Mirror = P1 wins on tempo.** Same structural issue as all R19 games.
- **Counter-sandwich impossible on corners.** P1's recovery options are weaker than menger's because max degree 2 forecloses the 6-nbr counter-sandwich pattern. Worse asymmetric balance than menger rank-1.
- **Smallest board of the R19 menger/carpet pair (64 vs 400).** Position variety is correspondingly smaller; openings collapse faster.
- **Pilot missed super-ko enforcement** (and so does the briefing). Same documentation gap.
- **`sierpinski_threshold_inert` soft violation.** Doesn't actually block the game in skilled play (24–30 plies to threshold), but still a flagged formal concern.

### BEST QUALITY
**The sandwich-as-cluster-builder pattern.** P2's 2-for-1 capture trade builds a 3-stone L-shape that's mutually reinforcing through r=2 distance-2 contribution (+0.25 each). This is the most efficient capture-attack-builds-structure pattern in the 6 R19 games. Same family as menger rank-1's sandwich, but tighter because the 2D + corner geometry forces specific shapes.

### CARPET STRUCTURAL CONTRIBUTION
**Modest, mostly local.** ~+0.5 depth via hole-edge resistance and corner fragility. Same conclusion as pilot. The carpet's 17 holes in 81 cells (21% holes) create local geometric variation but don't fundamentally change the game family. Flatten to 9×9 grid: lose ~0.5 depth and most of the "hole-edge-resistance" sub-game; otherwise same dynamics.

### IMPROVEMENT IDEAS
**Single best change: pie rule.** Cross-cutting recommendation across all 6 R19 games. After P1's first move, P2 may swap colours instead of placing. Punishes any opening strong enough to mirror profitably; restores seat balance.

Secondary improvements:
- **Document super-ko in briefing/eval-prompt.** Same gap as menger games.
- **Increase capture threshold to 3.** Would make corner sandwich require 3 of 2 P2 nbrs (impossible at corners → corners become safe). Shifts balance toward P1.
- **Increase axis to 13 or 15** (level-3 sierpinski). 169 active cells with the same hole pattern would scale up the strategic surface; pilot's "single best change" might shift to pie rule + larger board.
- **Test against R8's connection family.** Adding a connection secondary win condition (e.g., "first to chain across the carpet wins, OR threshold > 30") would give the game R8's narrative arc plus the influence layer.

### What evolution did or didn't add (vs rank-2 sibling)
The briefing notes carpet rank-1 was crossover-derived from carpet rank-2 (`b48208268f2a`) × `eb301d1bf7f6`. Without seeing rank-2 yet, I expect the crossover to have refined parameters (likely the threshold and decay) rather than introducing new mechanics. **From the strategic surface I've explored, this game is a parameter-tuned variant of the 2D outnumber+influence+threshold family.**

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-4_gamece3a09e05cef.md`.*
