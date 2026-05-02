# Run 19 Evaluation — team-2 — Game 98739cb0838a

**Team ID:** team-2
**Game ID:** `98739cb0838a` (Menger rank-2, GE 0.3213, ELO 2402.6)
**Substrate:** Menger sponge (axis 9, 400 active cells / 729 grid positions, max_degree 6)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 98739cb0838a` (see `briefing_menger_rank2.md`).
**Note:** Direct seed that survived 8 generations of evolution untouched.

---

## Phase 1 — Rule Comprehension

**Board.** Identical to menger rank-1: 9×9×9 cube, 400/729 active cells per the level-2 menger fractal pattern, max_degree 6 reached only at the 8 sub-cube anchor cells (2,2,2), (2,2,6), (2,6,2), (6,2,2), (2,6,6), (6,2,6), (6,6,2), (6,6,6).

**Turn structure.** Alternating, P1 first. **Max 100 turns** (vs 89 for rank-1).

**Action space.** 730 actions = 729 placements + pass. Place-only — D1 hybrid ban.

**Capture.** Outnumber, threshold 2 — same as rank-1.

**Propagation.** Influence, **r=2, strength=0.9895, decay=0.3037**. Distance-0 (placed cell) gets ±0.9895; distance-1 gets ±0.3037×0.9895 ≈ ±0.300; distance-2 gets ±0.3037²×0.9895 ≈ ±0.091. Two key differences from rank-1:
- r=2 (not r=1) — distance-2 cells now reinforce.
- Decay 0.30 (not 0.50) — steeper fall-off.

Per-stone contribution to threshold under tight cluster:
- Isolated stone: +0.989
- Adjacent pair: +1.589 each (own +0.989 + 0.300 from neighbour)
- 7-stone octahedral star: +13.27 (verified via helper) — vs +13.0 for rank-1's r=1/d=0.5 kernel.

**Win condition.** Threshold-race > **38.959** (vs rank-1's 29.709 — 31% higher). With per-stone gain ≈ +1.5-2 in established clusters, total stones to threshold ≈ 22-26 per side. Avg game length 54.2 moves confirms ~27 plies per player.

**Degeneracy check.**
- Same fractal-hole map as rank-1 (identical substrate).
- Double-pass = immediate draw (verified, not a meaningful degeneracy in practice).
- The seed survived 8 generations unchanged — evolutionary signal of stable local optimum but ALSO a signal that R19's mutation operators couldn't escape it.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror at the 6-degree interior anchor (full play-through)

Sequence: `182,546,181,545,183,547,173,537,191,555,101,465,263,627,102,626,110,618,174,554,190,538,254,474,262,466,2,726,18,710,162,566,180,548,164,564,184,544,165` (39 plies).

Plot:
- Plies 1-14: octahedral stars at (2,2,2) and (6,6,6) — 7 stones each, both at +13.27.
- Plies 15-26: shell-2 expansion (cells at axis distance 2 from anchor: (3,2,1), (2,3,1), (3,1,2), (1,3,2), (2,1,3), (1,2,3) for P1 and mirrors for P2). Each adds +2.32 (own +0.989 + 0.300 from 2 own neighbours + 0.091 distance-2 contributions). Both at +25.69 by ply 26.
- Plies 27-32: shell-2 cells at (2,0,0)=2, (0,2,0)=18, (0,0,2)=162. P1 and P2 still mirroring. Both at +29.36 by ply 32.
- Plies 33-38: more shell-2 expansion at (0,2,2)=180, (2,0,2)=164, (4,2,2)=184. Both at +38.72 by ply 38.
- **Ply 39 P1 plays (3,0,2)=165** (greedy hint says +2.557, close to threshold). **P1 score → +41.28 > 38.959 → P1 wins.** P2's 19th stone at +38.72 was their last move; P2 never gets a 20th.

**Mirror = P1 wins by exactly 1 ply at 20-vs-19 stones.** Same 1-ply tempo advantage as rank-1, but with longer game length (39 vs 25 plies). The longer horizon **does not change the structural P1 advantage**.

P1 reflection: The longer game has more "room" to absorb mistakes, but under perfect mirror, the +0.989 per placement + reinforcement compound to keep P1 exactly 1 stone ahead. P1's last move always crosses threshold first because it's the (2k+1)th placement vs P2's (2k)th.

P2 reflection: Under mirror, P2 cannot avoid losing by 1 ply. Asymmetric play required — see Game 2.

### Game 2 — P2 sandwich attack vs P1 counter-sandwich (rank-2 with r=2 kernel)

Sequence: `182,181,180,183,173,191,101,3` (8 plies).

Plot:
- P1 (2,2,2) [182] — interior anchor.
- P2 (1,2,2) [181] — sandwich attack. (1,2,2)'s influence at this point: P2 owns (1,2,2)=−0.989, but P1's anchor reduces (1,2,2) to (1.0×0.300−0.989) = −0.689 net. Score becomes P1 +0.689, P2 +0.689 (the propagation cross-contamination evens it).
- **P1 (0,2,2) [180] — counter-sandwich captures (1,2,2).** Outnumber-2 mechanic identical to rank-1 (capture rule unchanged across ranks). P1 = +1.560, P2 = 0.
- **P2 (3,2,2) [183] — sandwich resumed from +x side.**
- **P1 (2,1,2) [173] — extend cluster + threat.**
- **P2 (2,3,2) [191] — completes sandwich; (2,2,2) captured by outnumber-2.** P1 = +1.796, P2 = +1.560.
- **P1 (2,2,1) [101] — rebuild cluster from (2,2,2) along −z. Plus this also approaches a counter-sandwich on P2's (2,3,2) (need 2 P1 neighbours of (2,3,2): (2,3,1), (2,4,2), (1,3,2), (2,2,2)=empty. None are P1 yet).**
- **P2 (3,0,0) [3] — distractor at corner.** P2 can't immediately counter-sandwich back without losing tempo.

After 8 plies: P1 = 3 stones at +2.995 (with cluster around (2,2,1)/(0,2,2)/(2,1,2)). P2 = 3 stones at +2.367 (with two-of-a-pair sandwich-residue stones (3,2,2)/(2,3,2) at distance 2 — no influence reinforcement — plus a corner distractor). P1 leads by +0.628 with same piece count.

The sandwich exchange is a wash with slight P1 advantage. Identical mechanism to rank-1 Game 2; the r=2 kernel doesn't change the capture economics. **Sandwich at the 6-degree interior anchor is again a losing line for P2.**

### Game 3 — Novelty adversary: long-horizon cluster preservation test

Sequence: `182,181,180,183,173,191,101,3,263,4,191,5,191,6` (partial — 14 plies attempted).

The conceptual test: in a long-horizon game (~54 moves), the pilot suggested "cluster preservation across 50+ moves" is a distinct emergent. I tested whether P2 can disrupt an established cluster in late-game.

**Result:** Once a 7-stone octahedral star + 6 shell-2 stones is built (13 stones total), every cluster stone has ≥2 P1 neighbours among its active neighbour set. Outnumber-2 capture requires 2 P2 neighbours; **P2 cannot reach 2 P2 neighbours of any cluster stone because P2 cannot place into P1-occupied cells.** The cluster is **structurally sandwich-immune.**

Specifically, take the shell-2 stone (3,2,1): its active neighbours are (2,2,1)=P1, (3,2,2)=P1, (3,2,0)=empty (the only empty active neighbour). P2 can place (3,2,0) for 1 P2 neighbour but cannot reach 2. Same for every cluster stone in the 7+6 = 13-stone cluster.

**The pilot's "long-horizon cluster preservation" claim is false:** preservation is automatic for any cluster stone with ≥2 own-cluster neighbours; the long horizon simply gives more time for both players to reach this state. P2 cannot disrupt established clusters via outnumber-2 — the sandwich is only viable in the **early game** (first 6-8 plies before clusters consolidate).

This is a meaningful divergence from the pilot. The "long-horizon" angle is mostly a side-effect of the higher threshold + steeper decay → more stones needed → more plies, **not** a distinct strategic dimension.

### Strategy guides

**P1 (offence/threshold push):** Same as rank-1 — anchor at one of the 8 max-degree-6 interior cells, build the octahedral star, then expand to shell-2 cells. The threshold is higher so expand further: shell-3 cells (axis distance 3 from anchor) at (4,2,2), (2,4,2), (2,2,4) for the (2,2,2) anchor. Threshold reached at ~20 stones / ~39 plies.

**P2 (defence + threshold contest):** Mirror is a guaranteed 1-ply loss. Sandwich at 6-degree interior anchors is a losing line (Game 2). **There is no winning P2 line under perfect P1 anchor selection.** Best line is mirror with a single attempted sandwich harassment in plies 5-8 to reduce P1's score by ~0.5; this still loses but minimises the deficit.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same two as rank-1: (1) interior-anchor cluster + race, (2) sandwich harassment in early plies. The pilot's claimed "long-horizon preservation" is not a third strategy — it's the natural state of any consolidated cluster. Confirmed structural P1 advantage.

**Counter-play.** Asymmetric and weak. Same as rank-1.

**Short-term vs long-term.** The longer horizon (39 plies to mirror-end vs 25 in rank-1) means more total moves but **not more strategic depth per move**. Late-game moves are forced (greedy expansion to next-best-shell cell); the long horizon is "doing the same thing more times," not "doing different things later in the game."

**Emergent concepts observed.**
- Same as rank-1: 6-degree anchors, octahedral star, counter-sandwich symmetry, hole-bridge corridors (still inactive in threshold-race).
- **Cluster sandwich-immunity**: once a cluster stone has ≥2 own neighbours among its active neighbour set, it is uncapture-able by outnumber-2. This is the **structural reason "long-horizon preservation" is automatic**.
- **Shell expansion as forced sequence**: shell-2 cells > shell-3 cells > distant cells in greedy score. The cluster expansion order is essentially deterministic.

**Does the menger substrate matter?** Same as rank-1: modestly. The 8 6-degree anchor cells dominate strategic decisions; the rest of the menger structure is passive constraint.

**Does the propagation kernel matter?** **More than rank-1, but not in the way the pilot claimed.** The r=2 kernel adds distance-2 reinforcement (+0.091 each) which helps slightly for shell-2 expansion but doesn't change the cluster-shape preferences. Steeper decay (0.30 vs 0.50) makes each marginal cluster member contribute slightly less, requiring more total stones. **Net effect: the game is longer, not deeper.**

**Capture-rule contribution.** Same as rank-1: captures fire in the early game during sandwich exchanges, then become structurally unavailable once clusters consolidate. Captures are **early-game tactical only**; mid-late game has no capture activity.

**First-mover advantage / seat balance.** Same structural P1-by-1-ply advantage. **PPO trained-vs-trained 0.500** — this game's PPO must converge to a knowledge-asymmetric equilibrium where P2 plays sandwich at 3-degree corners (winnable) and P1 plays corner anchors (suboptimal). When P1 plays optimally at 6-degree anchors, the game is unbalanced.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is identical-family to menger rank-1: outnumber + influence + threshold-race on a 3D fractal. The differences are parametric (kernel, threshold, max_turns), not structural.

(a) **Threshold-race influence games** — same family as Tumbleweed/Sygo, plus this game's R19 family.

(b) **Outnumber-2 capture** — same Ataxx/Tafl-adjacent mechanic, identical to rank-1.

(c) **The combination "outnumber + influence + threshold-race"** — same R19-novel combination as rank-1.

(d) **Menger sponge substrate** — same novelty axis as rank-1.

(e) **Steep-decay r=2 kernel** is uncommon. The pilot suggests this is a meaningful novelty axis. **I disagree.** The r=2 vs r=1 kernel produces a quantitative difference in cluster economics but no qualitative difference in strategy — same anchors, same expansion pattern, same sandwich-immunity once consolidated. The game *feels* different (more stones, longer to win) but plays the same.

(f) **Direct-seed survival through 8 generations.** This is interesting: R19's mutation operators couldn't improve on these parameters. Two readings: (positive) the parameters are a stable local optimum; (concerning) the operators are too local and missed nearby better games. The fact that crossover variant rank-1 (`1f9191b5d4e6`) is also in the same family suggests the family has been thoroughly explored without finding distinct better games.

(g) **Expert-transfer test.** A Go + Othello + Hex + Score Four player would internalise the rules in 10 minutes (same as rank-1). The kernel difference would not register as a strategically-distinct game.

**Closest known-game analogue:** **Tumbleweed-on-Menger-with-Ataxx-captures, long-horizon variant.** Inside the project corpus, **menger rank-1 (`1f9191b5d4e6`) is essentially the same game with tighter parameters** — they're sibling rule sets in the same family.

**Comparison to R8's Connection Go (8/10 ceiling).** Same as rank-1: different family. R8's narrative arc (build a chain) generates tactical climax; this game's threshold race lacks an analogous moment. The longer horizon doesn't add narrative tension — it just defers the threshold-cross by 14 plies.

**Player rebuttal (P1 + P2).**
- The 6-degree interior anchor structure is genuinely substrate-driven (same as rank-1).
- The cluster-sandwich-immunity property — that any cluster stone with ≥2 own-cluster neighbours is uncapturable — is an emergent of the outnumber-2 mechanic and worth noting; it explains why the late game is structurally inactive.
- Subtracting from novelty: the identical strategic skeleton with rank-1 means evaluating both games gives correlated information. R19's evolution explored a single family in parameter space, not multiple families.

**Novelty score (post-adversary):** **5/10.** Same as rank-1. The pilot's +0.5 for "long-horizon preservation" is double-counting because the preservation property is structural (sandwich-immunity at consolidated clusters) and applies to rank-1 too — it just plays out faster there. **The two menger games are sibling rule sets, not structurally distinct games.**

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** 98739cb0838a
**Rules Summary:** Place stones on a 9×9×9 menger sponge (400 of 729 cells active) to accumulate influence on cells you own. Each placement adds ±0.99 to the placed cell, ±0.30 to active 1-neighbours, and ±0.09 to active 2-neighbours; an enemy stone is removed if it has ≥2 of your stones among its active neighbours when you place. First to >38.96 effective influence wins. Typical game length: ~39-54 plies.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 (effective 3-4 for most cells).
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Same depth as rank-1 (anchor selection + cluster expansion + early-game sandwich) **without** the pilot's claimed "long-horizon preservation" axis (which I show is structurally automatic, not strategic). The longer game length adds plies, not decisions. **Below my rank-1 score (5)** because I'm correcting for the pilot's depth-inflation on this game.

- **Emergent Complexity: 5** — Same primitives as rank-1: octahedral star, counter-sandwich, sandwich-immunity at consolidated clusters. The new emergent I'd flag — **cluster sandwich-immunity** — applies equally to rank-1 (just less visible there because the game ends sooner). No net new vocabulary.

- **Balance: 3** — Same as rank-1. Mirror = P1 wins by 1 ply (verified Game 1, P1 wins ply 39). Sandwich = losing line at 6-degree anchors (verified Game 2). PPO's reported 0.500 reflects suboptimal anchor-equilibrium, not true balance.

- **Novelty (post-adversary): 5** — see Phase 4. This is a **sibling rule set to menger rank-1, not a structurally distinct game.** Evolution didn't find a new family — only a parameter variant. Novelty score = same as rank-1.

- **Replayability: 4** — Longer games = slightly more position variety per game, but the same 8-anchor opening tree and the same forced-greedy shell expansion. Marginal.

- **Overall "Would I play this again?": 4** — Once: marginal interest beyond rank-1 (same dynamics, takes longer to play). Repeatedly: no — the long horizon makes the wash-out result more drawn-out without making it more interesting. **Below my rank-1 score (5)** because the marginal interest of "same dynamic, more plies" doesn't reward replay.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed-on-Menger-with-Ataxx-captures, long-horizon variant.** Inside this project, **R19 menger rank-1 (`1f9191b5d4e6`) is the same game in a tighter parameter regime.** The two are sibling rule sets, not structurally distinct.

### KILLER FLAWS
- **Mirror = P1 wins by 1 ply** (verified ply 39, 20 stones vs 19).
- **Cluster sandwich-immunity** makes mid/late-game tactically inactive — captures only fire in plies 5-8 during early sandwich exchanges, then never again under perfect play.
- **Direct seed survived 8 generations** — evolution didn't escape the family. R19's mutation operators may be too local; the high-fitness "menger + outnumber + influence + threshold" recipe is a basin attractor that the engine cannot leave.
- **Long horizon adds plies, not depth.** The 54-move avg game length is mostly forced shell expansion; strategic decisions are concentrated in the first 8-10 plies.
- **Two of R19's three menger top games are parametric variants of each other.** This game (rank-2) is the seed; rank-1 is a crossover refinement. The R19 menger top-3 is exploring 1.x families, not 3 distinct games.

### BEST QUALITY
**Cluster sandwich-immunity as an emergent rule property.** Once a cluster stone has ≥2 own-cluster neighbours among its active neighbour set, outnumber-2 cannot capture it (P2 cannot reach 2 P2 neighbours when 2 of N are P1). This is a clean, derivable property of the rules that explains the game's mid/late-game structure. It's not strategically interesting (it just means captures stop firing after consolidation) but it's a meaningful design observation.

### MENGER STRUCTURAL CONTRIBUTION
**Modest, same as rank-1.** The 8 6-degree anchors dominate strategic decisions; the fractal hole pattern's other contributions (z=4 hole-bridge, 2×2×2-cube-impossibility) are passive in this game's dynamics. **Estimated loss from flattening to 9³ all-active: ~0.5 point of depth, ~1 point of novelty.**

### IMPROVEMENT IDEAS
**Single best change:** **Pie rule.** Same as rank-1. Mirror's 1-ply structural win is the dominant balance issue.

Secondary improvements:
- **Reduce threshold to ~30** to compress the game to ~30 plies (matches rank-1's pace) and concentrate strategic interest.
- **Combine with secondary win condition** — e.g. connection between two opposite faces of the cube — to give the game narrative tension. Closest to R8's family.
- **Add a per-stone capture cost** (e.g., capture costs the placer 1 point of influence) to make captures expensive and keep them as a tactical resource throughout the game, not just in plies 5-8.

### What evolution did or didn't add (vs rank-1)
**Confirmed: nothing structural.** Rank-2 is the unmodified seed; rank-1 is a crossover with parameter tweaks (r=1, decay=0.5, threshold=29.7). Both are in the same outnumber-influence-threshold family. The R19 menger evolution is exploring **parameter variants of one recipe**, not multiple recipes. Compared to R8 (which generated a structurally distinct connection-game in 2D), R19 menger is a narrower exploration.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-2_game98739cb0838a.md`.*
