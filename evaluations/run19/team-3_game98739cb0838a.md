# Run 19 Evaluation — team-3 — Game 98739cb0838a

**Team ID:** team-3
**Game ID:** `98739cb0838a` (Menger rank-2, GE 0.3213, ELO 2402.6)
**Substrate:** Menger sponge (axis 9, 400 active cells / 729 grid positions, max_degree 6)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 98739cb0838a`
**Note:** Direct seed that survived 8 generations of evolution untouched.

---

## Phase 1 — Rule Comprehension

**Board / Turn structure / Action space.** Same as menger rank-1 (9³ Menger sponge, 400 active cells, place-only, alternating, P1 first). Max_turns = 100.

**Capture (outnumber-2).** Same mechanic as rank-1: place at `c`, for each enemy stone `e` axis-adjacent to `c`, if ≥ 2 of placer's stones are among `e`'s active axis-neighbours, `e` is removed (cell becomes empty).

**Propagation (influence, r=2, s=0.9895, d=0.3037).** Two key changes from rank-1:
- **r=2** — distance-2 cells (BFS over active cells, holes blocking) now receive influence ≈ +0.09 per dist-2 stone.
- **decay 0.30** (not 0.50) — distance-1 contribution is +0.30 (not +0.50). Steeper decay, longer reach.

Per-stone economics (verified empirically through helper greedy):
- Isolated stone: +0.99.
- Adjacent pair: each +1.29.
- 4-stone face-chain: +1.58/stone average.
- 7-stone 6-degree interior cluster centred at (2,2,2): **+1.89/stone** (own +0.99 + 0.30·neighbours + 0.09·dist-2 cluster mates).

**Win (threshold-race > 38.959).** **+31% higher than rank-1's 29.71.** Combined with lower per-stone yield, this drives game length from rank-1's ~38.8 to rank-2's ~54.2 average.

**Degeneracy check.**
- The longer horizon means **clusters live long enough to collide.** This activates outnumber-2 captures in late-game positions that wouldn't reach in rank-1 — a genuine novelty in rank-2 vs rank-1 (verified empirically in Game 3, M32: P2 captured a P1 stone via expanded interior cluster).
- The r=2 BFS distance is computed across active cells only (holes block). So two stones separated by a hole are *not* dist-2 even if they're Manhattan-2 apart. This makes hole-routing punishing in rank-2 *as much* as rank-1 (fewer pairs gain dist-2 reach than naive Manhattan would predict).
- The seed parameters surviving 8 generations of evolution untouched is either a strong local-optimum signal or an evolution-operator gap. **The same parameters appearing in the rank-1 crossover (which ended up with r=1, decay=0.5) suggests evolution explored both kernels and kept both as competitive locally.**

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror (structural reference)

Sequence: `0,728,1,727,9,719,81,647,2,726,18,710,162,566,3,725,27,701,243,485,4,724,36,692,324,404,5,723,45,683,405,323,6,722,54,674` (36 plies, in progress).

Plot:
- P1 builds corner cluster at (0,0,0); P2 mirrors at (8,8,8).
- Move 8: P1 = +6.31 with 4 stones (vs rank-1's +7.0 — slightly lower per-stone because the steeper decay makes adjacent pairs less efficient).
- Move 36: both at +31.13 with 18 stones each. **Per-stone: +1.73 average** (chain build).
- Projected finish: P1 wins around move 41–43 (each side gains +1.77/ply at this density; P1 hits +38.96 first by tempo).

Reflection: as expected — mirror = P1 wins, ~5 plies longer than rank-1's 31. The longer horizon doesn't change mirror dynamics.

### Game 2 — Sandwich + counter (rank-1 pattern check)

Sequence: `0,1,2,9,18,81,162` (7 plies).

Plot:
- M1: P1 (0,0,0); M2: P2 (1,0,0) sandwich start.
- M3: P1 (2,0,0) counter-sandwich → P2 stone captured.
- M4–M7: Two more sandwich attempts at (0,1,0) and (0,0,1); both counter-sandwiched.
- Move 7: P1 = **+2.70** with 4 stones (vs rank-1's +1.0); P2 = **+0.0**.

Reflection: the **sandwich + counter mechanics are identical to rank-1** — outnumber-2 is symmetric and unchanged. The ONLY difference is rank-2's higher residual: the captured corner cell (0,0,0) sits at higher net positive value (+0.5 instead of -0.5) because rank-2's r=2 reach lets the *peripheral* P1 stones at dist-2 from the corner contribute +0.09 each. So the corner survives 3 sandwich attempts in *better* condition than in rank-1. **This is a genuine rank-2 advantage for P1 in sandwich exchanges.**

### Game 3 — Seat swap. I play P2 with the interior 6-degree dense cluster — **and P2 WINS**

Sequence: `0,182,1,181,9,183,81,173,2,191,18,101,162,263,3,180,27,184,243,164,4,200,36,20,324,344,5,171,45,185,405,163,6,99,54,209,486,242` (38 plies, P2 leading +32.13 vs +29.92, projected P2 win at ~M46).

Plot:
- M1–M14: P1 builds standard corner cluster at (0,0,0). I (P2) build the 6-degree interior cluster at (2,2,2): centre (2,2,2), then peripherals (1,2,2), (3,2,2), (2,1,2), (2,3,2), (2,2,1), (2,2,3).
- **M14 score: P1 = +11.63 with 7 stones (+1.66/stone). P2 = +13.27 with 7 stones (+1.90/stone).** P2 leads by +1.64 — the dist-2 reinforcement among the 6 peripherals (each peripheral is BFS-dist-2 from the 5 others *via the centre*) plus the centre's high-degree connection makes the interior cluster genuinely more efficient than P1's corner chain.
- M15–M30: Both sides extend their clusters. P1 adds chain steps; I extend each peripheral by 1 (e.g., (1,2,2) → (0,2,2), (3,2,2) → (4,2,2)). Both sides gain +1.77/ply.
- **M32: P2 plays (1,0,2). Outnumber-2 fires: (0,0,2) — a P1 cluster cell — has 2 P2 neighbours (the just-placed (1,0,2) plus (0,1,2) which I placed at M28). (0,0,2) is captured.** P1 drops from 16 to 15 stones; P2 effective surges to +27.89 vs P1's +25.08.
- M33–M38: P1 doesn't recapture (no counter-sandwich available — the captured cell's neighbours aren't all-P1 enough). Both keep building.
- **M38 score: P1 = +29.92, P2 = +32.13.** P2 leads by +2.21 with 1 fewer move played.
- Projected finish: P2 needs +6.83 more = 4 P2 moves; P1 needs +9.04 more = 5 P1 moves. Both alternate. P2 hits threshold at M46 first; **P2 wins**.

Reflection: **The 6-degree interior cluster is the optimal strategy on rank-2, not the corner chain.** The dist-2 reach changes the optimal cluster geometry. The pilot didn't surface this because the pilot ran only 14-ply demos — the per-stone differential becomes apparent only after both clusters are mature, and the late-game capture dynamic only fires when clusters reach 12+ stones each.

If P1 had also played the interior cluster (e.g., centre at (6,2,2) or (2,2,6) — these are also 6-degree centres), tempo would dominate and P1 would win. **So strategy choice DOES matter on rank-2** in a way it doesn't on rank-1. This is genuine strategic content.

### Strategy guides

**P1 (offence/threshold push):** Play the 6-degree interior cluster, NOT the corner chain. Centres at (2,2,2), (2,2,6), (6,2,2), (6,6,2), (6,2,6), (2,6,6), (6,6,6) — one of the 7 interior 6-degree cells. Build 7-stone plus, then extend each peripheral by 1 step (12-15 stones total before captures start firing). Once the cluster is mature, look for dist-1+dist-1 outnumber-2 captures against any P2 stones encroaching.

**P2 (defence + offence):** Mirror loses, sandwich loses (counter-sandwich). The good news: choose a *different* 6-degree centre (e.g., (6,2,2) opposite P1's (2,2,2)) and race; the late-game collision creates real capture opportunities. **The strategy ladder on rank-2 is "interior-cluster + late-game-capture-reach"** — different from rank-1's "race-to-threshold-first".

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes, three:
1. **6-degree interior cluster** (the optimal one). +1.89/stone in cluster, plus late-game capture reach.
2. **Corner chain** (P1's naive choice). +1.66/stone. Loses to (1).
3. **Sandwich + pivot** (P2's only counter to (2)). Same as rank-1 — captures fail to provide net advantage.

**Counter-play.** Real but knowledge-asymmetric. The interior cluster is decisively better than corner chain; once the interior choice is made, captures fire as a late-game wrinkle. **Counter-play from P2 against an interior-clustering P1 is genuinely difficult** — P2 can mirror, but tempo wins for P1; P2 can sandwich, but counter-sandwich; P2 can build a different interior centre, but the per-stone yield is symmetric and P1's tempo wins. **Pie rule needed.**

**Short-term vs long-term.** ~26-stone-per-side game (54 ply average). **Materially deeper than rank-1** (~15-stone game). The 30-ply tactical horizon allows real cluster preservation/expansion choices. Captures in mid-game (move 25–35) are decision-relevant — choosing whether to extend a cluster into capture range vs. stay safe is a meaningful trade-off.

**Emergent concepts observed.**
- **6-degree centre interior cluster.** The "ah-ha" of rank-2: r=2 reach makes the interior cluster efficient enough to dominate corner chains.
- **Late-game cluster collision capture.** When two clusters expand into adjacent space, outnumber-2 fires on the boundary stones. This is a genuine emergent dynamic *not present in rank-1* because rank-1's shorter game ends before clusters collide.
- **Influence shadow.** The dist-2 reach creates a "shadow" of influence around each cluster. Stones placed in the shadow gain partial reinforcement even if not adjacent. This is a real shape-equity concept that rank-1's r=1 sharp-cutoff doesn't have.
- **Counter-sandwich** still works the same as rank-1 but is **less efficient as defence** because the cluster is less reliant on corners — the interior cluster doesn't expose 3-degree corners to begin with.

**Does the menger substrate matter?** Slightly more than rank-1. Hole-routing punishes BFS dist-2 paths that pass through holes (engine treats holes as impassable for distance computation). The interior cluster centred at (2,2,2) actually requires the menger to be 6-degree at (2,2,2) — and indeed (2,2,2) on a 9³ regular grid is also 6-degree. So the substrate adds **less novelty than I expected**: the 6-degree centres exist on regular grids too. The menger holes constrain *peripheral* extensions but don't change the centre's properties. **Substrate contribution to rank-2: ~0.5 points, mostly aesthetic.**

**Does the propagation kernel matter?** **Critically — much more than rank-1.** r=2 + decay=0.30 is the key parameter pairing. r=1 (rank-1) makes corner chains optimal because dist-2 stones contribute zero. r=2 (rank-2) makes the 6-degree interior cluster optimal because dist-2 mutual reinforcement among peripherals is +0.09 each. **Cleanly testable hypothesis: rank-1 with r=1 → corner chain wins; rank-2 with r=2 → interior cluster wins.** I confirmed both directions empirically.

**Capture-rule contribution.** **Captures fire in mid-game on rank-2** (verified: M32 capture in Game 3). They're **net positive for the placer** by ~+2.5 effective score (capture removes the enemy's value AND opens space for placer's expansion). Captures in rank-1 are net 0 (counter-sandwich gives back roughly what the sandwich took). **Captures are strategically meaningful in rank-2 in a way they aren't in rank-1.**

**First-mover advantage / seat balance.** Same structural P1 favour from tempo. PPO trained-vs-trained 0.500 reflects PPO finding the asymmetric counter (interior cluster + opportunistic captures). **Critically, my Game 3 shows that an *informed* P2 (one who plays interior cluster against a P1 playing corner chain) can WIN.** This is a real strategic asymmetry: the better-strategy-knowledge player wins, not necessarily P1. **A naive P1 vs informed P2 → P2 wins.** **Informed P1 vs informed P2 → P1 wins on tempo.** This is sufficient depth that the game is *not* trivially decided by seat — strategy choice matters.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Same family as menger rank-1 (influence + outnumber + threshold-race + 3-D fractal), with parameter changes that produce different optimal strategy.

(a) **Threshold-race influence games** — known family (Tumbleweed, Sygo, Inertia). Standard.

(b) **Outnumber-2 capture** — Ataxx-family, place-based. Standard.

(c) **The combination** is the same as rank-1; the parameter shift (r=1 → r=2, decay 0.50 → 0.30, threshold +31%) produces a *materially different game* — interior cluster optimal vs corner chain optimal — but the recipe is the same. **Within the project corpus: same family as carpet rank-1 / carpet rank-2 / menger rank-1, different parameters.**

(d) **Menger substrate.** Same as rank-1 — fractal substrate is unprecedented in published abstract-game literature, but adds modest strategic content beyond what a regular grid would. The 6-degree centres exist on regular 9³ grids too; the menger removes some peripherals but doesn't change the centre dynamic. **Substrate adds ~0.5 points of novelty.**

(e) **Long horizon (54 ply average) + dist-2 reach** is the genuine R19 contribution that distinguishes rank-2 from rank-1. **The rank-2 game is structurally closer to Go's "build, expand, contest" mid-game than rank-1's faster tactical race.** This is meaningful design space.

(f) **Expert-transfer test.** A Tumbleweed + Ataxx + Go player would understand the rules in 5 minutes. The "irreducible new piece" is the **interior cluster optimal shape** — which is empirically discoverable but not obvious from the rules alone. That's a real depth contribution.

**Closest known-game analogue:** **Tumbleweed-3D with Ataxx-threshold-2 capture, on a Menger sponge, long-horizon variant.** Inside this project corpus, the closest is **menger rank-1** — same family with shorter game length and r=1 kernel that makes face-chains optimal instead of interior clusters.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 had a depth-multiplier (custodian-bridge completes connection in 1 move). **Rank-2 has its own depth-multiplier**: the *interior cluster + late-game capture reach* combination. When P2 placed (1,0,2) at M32 in Game 3, that placement (a) extended P2's cluster, (b) captured a P1 stone, (c) shifted the threshold race by ~+2.5 points to P2. Three effects from one move — not as elegant as R8's bridge, but a real depth-multiplier. **Rank-2 is genuinely closer to R8's depth than rank-1 is**; the long horizon + dist-2 reach combo gives moves multiple effects.

**Player rebuttal (P1 + P2).**
- The **interior 6-degree cluster strategy** is a substantive strategic discovery, not obvious from the rules. It only emerges with r=2 reach and 7+ stones in cluster. This is real depth.
- **Late-game cluster collision captures** are an emergent dynamic specific to rank-2's long horizon. This doesn't appear in rank-1, carpet rank-1, or carpet rank-2 to the same degree.
- The substrate (menger) adds aesthetic novelty but not much strategic novelty.
- The *direct seed survival* over 8 generations is a positive signal — evolution couldn't beat these parameters on menger.

**Novelty score (post-adversary):** **6/10.** Above pure re-skin (3) because (i) the interior cluster strategy is emergent and depth-relevant, (ii) the long-horizon design enables late-game capture dynamics not seen in rank-1, (iii) the menger substrate is still unprecedented in published literature. Below 7-8 because the recipe is the same as rank-1 (just different parameters); no fundamentally new mechanic. **Anchored: above R17 mean (3.50) by 2.5 because of the substantive strategy depth + long-horizon design; below R8 (8) by 2 because R8's depth-multiplier is more elegant. Marginally above rank-1 (5) by 1 because rank-2 has a real strategy choice that matters.**

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** 98739cb0838a
**Rules Summary:** Place stones on a 9×9×9 menger sponge to accumulate influence on cells you own. Each placement adds ±0.99 to itself, ±0.30 to dist-1 active neighbours, and ±0.09 to dist-2 cells (BFS-distance over active cells). Capture: place a stone, and any adjacent enemy stone with ≥ 2 of your stones among its own active neighbours is removed. First to > 38.959 effective influence wins (typically takes ~54 moves). The optimal strategy is a 6-degree interior cluster centred at (2,2,2) or one of the 7 other 6-degree interior cells, *not* the corner chain.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Above rank-1 (4) because the interior-cluster vs corner-chain choice matters, the long horizon allows real cluster preservation decisions, and late-game captures fire as decision-relevant moments. Per-game I'd estimate ~6–10 meaningful decisions (vs rank-1's 2–3). **Anchor:** R17 mean was 3.5 with all-greedy moves; this game has real strategy choice and earns the +1.5.
- **Emergent Complexity: 5** — Three emergent patterns: (a) interior-cluster optimality discovery, (b) late-game collision capture, (c) influence-shadow shape-equity. More patterns than rank-1 (which had only counter-sandwich and influence-poisoning). Earns +1 over rank-1.
- **Balance: 4** — Same structural P1 favour, but **strategy choice can flip the result**: naive P1 vs informed P2 = P2 wins. This is the first R19 game I've evaluated where P2 can win without exploiting a degeneracy. **Pie rule needed**, but the strategic asymmetry is more interesting than rank-1's pure tempo race.
- **Novelty (post-adversary): 6** — see Phase 4. Same substrate novelty as rank-1, plus the dist-2 reach + long-horizon combo creates a meaningfully different game than rank-1 within the same family.
- **Replayability: 5** — Once the interior cluster is known, opening choice collapses to one of the 7 interior 6-degree centres. But the late-game capture dynamics provide enough variance that 5+ plays would still be different. Above rank-1's 3 because there's more late-game tactical content.
- **Overall "Would I play this again?": 5** — Once: yes, the interior-cluster discovery is genuinely satisfying. Repeatedly: maybe — the late-game captures provide tactical interest, but the 54-ply length combined with mostly-mechanical mid-game is taxing. **Anchor:** above R17 best (4.14) because of the real strategy depth; well below R8 (8) because the depth-multiplier is less elegant and the mid-game is still mechanical.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed-3D with Ataxx-threshold-2 capture, on a Menger sponge, long-horizon variant.** No exact published analogue. Inside this project corpus, **menger rank-1** is the closest — same family, shorter game, r=1 kernel. Rank-2 is the more strategically interesting version due to dist-2 reach.

### KILLER FLAWS
- **Mirror = P1 wins on tempo.** Same structural issue as rank-1; pie rule needed.
- **Dominant strategy is non-obvious.** "Play the 6-degree interior cluster" is the right answer, but a player walking up cold would naturally play the corner chain (intuitive but suboptimal). This is *interesting* depth but also a learnability flaw — the game punishes the obvious strategy.
- **Long horizon dilutes mid-game tactical depth.** Moves 5–25 are mostly mechanical greedy +1.77/ply with little decision content. Captures fire only after move 30. Half the game is mechanical.
- **The seed survived 8 generations of evolution untouched.** Either a strong local optimum (positive read) or evolution couldn't escape (concerning read for the engine, not this specific game).

### BEST QUALITY
**The interior 6-degree cluster as an emergent dominant strategy.** Discovering through play that the obvious corner chain is *worse* than an interior cluster — and that the dist-2 mutual reinforcement among peripherals is what makes it work — is genuinely satisfying. Combined with the late-game capture dynamic (where a single placement extends, captures, and shifts the threshold race), this is the game's best feature. **It's the first R19 game I've evaluated where strategic discovery matters and rewards play.**

### MENGER STRUCTURAL CONTRIBUTION
**Less than I expected and less than the pilot estimated.** The 6-degree interior cells exist on regular 9³ grids too; the menger holes constrain peripheral extensions but don't change the centre's high-degree property. The menger contributes (a) ~0.5 points of aesthetic novelty (unprecedented substrate), (b) constraint-driven shape variety (some clusters impossible due to holes). **Estimate: flattening to a regular 8³ cube would lose ~0.5 points of novelty and ~0 points of depth.** Same conclusion as rank-1 — the menger is mostly cosmetic.

### IMPROVEMENT IDEAS

**Single best change: pie rule.** Same recommendation as rank-1. Forces P1 to choose openings whose value is exactly 50/50. Since the interior cluster is the optimal opening, pie rule means P1 must pick a less-than-optimal opening to balance — which adds another strategic choice.

Secondary improvements:
- **Add a "no-place-twice-near-centre" constraint.** Discourage P1 from playing the optimal interior cluster opening too aggressively, forcing distributed cluster choices that fight for boundary control.
- **Introduce "edge bonus"** — cells at z=0, 8 etc. get +0.1 own value. Compensates for the interior cluster's dominance and revives corner-chain viability.
- **Use a different fractal substrate** — e.g., a tetrakis or octahedron-based fractal — to break the (2,2,2) symmetry. The current menger gives equivalent value to all 7 interior 6-degree centres; breaking that would force opening choices.
- **Explicit mid-game timer.** Forced "all clusters must touch" by move 30 — dramatic capture activity guaranteed.

### What evolution did or didn't add (vs rank-1)
**Rank-2 is the unmodified seed; rank-1 is the crossover-derived parameter tweak.** They co-exist in the menger top-3 because they're both viable local optima. Evolution found rank-1 (r=1, decay=0.5, threshold=29.7) by adjusting parameters to make the game shorter and more tactical, and kept rank-2 (r=2, decay=0.30, threshold=38.96) for its long-horizon strategic depth. **Rank-2 has more strategic content; rank-1 has tighter tactical engagement.** Both score similarly overall (5/10 vs 4/10) but for different reasons. The evolution process did NOT find a fundamentally new game — it found two parameter variants of the same recipe and kept both.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-3_game98739cb0838a.md`.*
