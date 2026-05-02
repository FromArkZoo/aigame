# Run 19 Evaluation — team-1 — Game 5048f71b62fd

**Team ID:** team-1
**Game ID:** `5048f71b62fd` (Menger rank-3, GE 0.3158, ELO 2354.6)
**Substrate:** Menger sponge (axis 9, 400/729 active, max_degree 6 nominal)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 5048f71b62fd` (briefing: `briefing_menger_rank3.md`).

---

## Phase 1 — Rule Comprehension

**Board / turn structure / actions.** Same as menger rank-1 and rank-2: 9³ menger sponge, 400 active cells, place-only (D1 hybrid ban active), alternating, P1 first. Max 71 turns (lower than rank-1's 89 and rank-2's 100).

**Capture (surround, threshold 2 — but threshold field is unused for surround).** **Go-style group-liberty capture.** When you place a stone, for each enemy group adjacent to your placement: if the group's liberty count = 0, the entire group is removed. Liberties = empty active cells adjacent to any group member; **holes do NOT count as liberties**. Empirically verified by inspection of `_capture_surround` in `engine_v2.py`: threshold is read from the rule blob but not used by the surround code path.

**Propagation (influence, r=1, s=1.0, d=0.5).** Identical kernel to menger rank-1. Each placement spreads ±1.0 to itself and ±0.5 to active distance-1 neighbours; influence persists on capture.

**Win (threshold-race > 21.212).** **29% lower than rank-1's 29.7, 46% lower than rank-2's 38.96.** Combined with the Go-style capture (which can wipe entire groups), this is a fast-resolution game.

**Degeneracy check.** No soft violations. **Important geometric subtlety I missed at first**: the fractal at z=1 has a different active-cell pattern than at z=0. For example, (5,2,1) is active (L2 digits (2,2,1) → 1 one) while (5,3,0) is inactive (L1 digit y=1 makes 2 ones). **The 3D substrate has z-tunnels** — what looks like a fully-walled cell at z=0 may have an active cell directly above it at z=1, providing a liberty/escape route. **This dramatically softens the "surround capture is BRUTAL" intuition** the pilot used.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Single-stone surround near a level-1 hole-block

Sequence: `0,1,9,81,162` (5 plies, **P1 captures (0,0,1)**).

Plot:
- P1 (0,0,0). P2 (1,0,0). P1 (0,1,0). P2 (0,0,1). After move 4: P2's (0,0,1) is an isolated single stone.
- (0,0,1)'s active neighbours: (0,0,0) P1 (not a liberty), (0,0,2) empty (liberty), (1,0,1)# inactive, (0,1,1)# inactive. **1 liberty.**
- **Move 5: P1 plays (0,0,2). The single liberty is closed; (0,0,1) group has 0 liberties; captured.**
- After ply 5: P1 = 3 stones (0,0,0), (0,1,0), (0,0,2); P2 = 1 stone (1,0,0). P1 +2.5, P2 +0.5.

Reflection: **The pilot's framing — "fractal hole pattern makes surround VERY aggressive" — is half-right.** Single stones placed at cells where the L2 hole pattern reduces neighbour count to ≤2 active are vulnerable. But the framing misses that this asymmetry is **rare**: most active cells have 3+ active neighbours (verified Game 3 below). The aggressive-surround property applies mostly to cells near L1 hole-blocks (y=3-5 layer, z=3-5 layer, etc.) where multiple coordinates are at hole-positions.

### Game 2 — P2 surround on a 3D corner

Sequence: `0,1,728,9,727,81` (6 plies, **P2 captures (0,0,0)**).

Plot:
- P1 (0,0,0). P2 (1,0,0). P1 pivots to (8,8,8). P2 (0,1,0). P1 (7,8,8). **P2 (0,0,1) → captures (0,0,0).**
- After ply 6: P1 = 2 stones at far corner (cluster +3.0); P2 = 3 stones at origin (scattered, +1.5).
- **Trade economics**: P2 spent 3 plies to capture 1 P1 stone (3-for-1 stone trade). P2's 3 attackers are pairwise NOT adjacent — (1,0,0), (0,1,0), (0,0,1) form an "L2-hole-scattered" triplet because (1,1,0), (1,0,1), (0,1,1) are all inactive. **Net trade in influence**: P1 lost +1.0 (own placement at (0,0,0) now sits on an empty cell), P2 gained 3 × +0.5 effective per stone (each attacker has +0.5 from (0,0,0)'s persistent ledger contribution). Net swing = +2.5 P2 over 3 plies, but P1's same 3 plies built a +3.0 cluster at the far corner.

Reflection: **Surround at an isolated 3-neighbour corner is a 3-for-1 stone trade, ≈ 1-for-1 in influence**. Worse than rank-1's outnumber-2 sandwich (2-for-1 stone, also ≈ 1-for-1 in influence) on per-ply efficiency. The fractal pattern *prevents* P2's surround attackers from clustering because (0,0,0)'s 3 active neighbours are all pairwise NOT adjacent. **Same substrate quirk that limited outnumber sandwich profitability in rank-1 limits surround attack here.**

### Game 3 — Hole-edge group + z-tunnel escape (genuine novelty test)

Sequence: `22,21,23,24,14,5,15,6,104,105,185` (11 plies, in progress).

Plot:
- P1 builds a 4-stone group at hole-edge cells: (4,2,0), (5,2,0), (5,1,0), (6,1,0). All on the y=4 hole-block boundary at z=0; many of their non-group neighbours are inactive holes.
- P2 systematically encloses: (3,2,0), (6,2,0), (5,0,0), (6,0,0). After move 8, the group's z=0-layer liberties are all closed.
- **But the group has a liberty at (5,2,1) — z-tunnel up to z=1.** I had originally computed (5,2,1) as inactive (mistakenly applied the hole rule); the engine's adjacency reveals (5,2,1) IS active (L2 digits (2,2,1) → 1 one). My initial error mirrors the pilot's "VERY aggressive" intuition: **cells inactive at z=0 may be active at z=1**, providing escape routes the 2D analysis misses.
- **Move 9 P1 (5,2,1) — extends group up. Group is now alive with multiple liberties at z=1.**
- Move 10 P2 (6,2,1) — chases into z=1.
- Move 11 P1 (5,2,2) — extends up to z=2. Group has new liberties: (6,2,2), (4,2,2), (5,1,2).

After ply 11: **P1 = 6 stones (cluster +8.0); P2 = 5 stones (scattered +4.0).** P1 is ahead by 2 stones AND +4.0 score. The z-tunnel escape made P2's surround investment worthless.

Reflection: **The 3D substrate provides routine escape routes** for committed groups. Even when a P1 group looks "surrounded at z=0", it usually has a z-tunnel to z=1 or z=2. P2's surround attack only works on isolated single stones at L1-hole-block cells (Game 1) or on stones too far from a z-tunnel (Game 2's corner case). **Group preservation via z-extension is the dominant P1 strategy**, and it's much easier than I expected.

### Strategy guides

**P1 (offence/threshold push):** Build groups, not isolated stones. Anchor at any active cell with ≥3 active neighbours and immediately add a second stone — this gives the group 4-5 liberties before P2 even threatens. **Use z-tunnels aggressively**: when P2 attacks at z=0, extend up to z=1 or z=2; the active-cell pattern at z=1 differs from z=0 due to the level-1 vs level-2 fractal interaction. Threshold 21.2 is reached at ~14 stones (~1.5/stone), so P1 wins by ply 28-30 against any non-mirror P2 line. **Mirror still loses by tempo** (linear race; P1 reaches threshold one ply earlier than P2).

**P2 (defence + offence):** Mirror loses by tempo. Surround attacks on single stones near L1 hole-blocks (cells with active-neighbour count ≤2) can capture for 1-2 ply investment — rare but possible. Surround attacks on multi-stone groups are usually wasted because P1 escapes via z-tunnel for ~3 ply per turn extension. **Best line**: focus on isolated P1 stones; never attack multi-stone groups; build P2's own cluster and try to win the threshold race despite P1's tempo.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Three.
1. **Anchored group + threshold race** (P1's playbook). Build connected groups; rely on z-tunnel escapes; race to 21.2.
2. **Hole-edge surround** (P2's only effective attack — single stones at cells with ≤2 active neighbours can be captured for 1-2 ply investment).
3. **Corner sandwich variant** (P2 invests 3 plies to capture a corner stone; same as rank-1's sandwich but with stricter geometry constraints).

**Counter-play.** Real but **less rich than pilot claimed**. The pilot framed this as "Go-style life-and-death", but on this menger substrate **most groups are routinely alive** because z-tunnels provide easy extensions. The actual life-and-death tension is mostly limited to isolated stones near hole-blocks. This is closer to "Go without ko or seki" than to full Go.

**Short-term vs long-term.** ~14-ply horizon to threshold (avg game 27.2 moves). Tactical depth is HIGH per move (capture/escape decisions are non-trivial); positional depth is LOW (game ends before long-term plans mature).

**Emergent concepts observed.**
- **Hole-edge sandwich** (single stones at cells with ≤2 active neighbours are vulnerable in 1-2 plies) — same family as rank-1's corner sandwich, refined by the geometry.
- **Z-tunnel escape** — committed groups can extend into z+1 to gain new liberties. **This is the most game-defining positive pattern.**
- **L2-hole-scatter on attackers** — P2's surround attackers at corners always scatter because (1,1,0)/(1,0,1)/(0,1,1) etc. are all inactive (as in rank-1).
- **Ledger persistence on captures** — same as rank-1; captured stones leave permanent influence contributions.

**Does the menger substrate matter?** Yes, but **less uniformly than the pilot claimed**. The fractal pattern creates *both* aggressive surround (Game 1) AND easy escape (Game 3) — net effect is a more uneven game-flow than a regular substrate. **Flattening to a holeless 9³ would actually make the game more uniform** (no z-tunnel mismatch, no hole-edge pockets). The menger substrate adds variance, not uniform depth. Estimate: substrate contribution is ~+1 novelty, ~+0.5 depth, **vs the pilot's +2 depth claim**.

**Does the propagation kernel matter?** Same r=1 kernel as rank-1; same conclusions.

**Capture-rule contribution.** Surround capture **does** add real strategic content vs outnumber — group dynamics, life-and-death decisions are present. But on this substrate, the z-tunnel escape mechanism reduces the practical importance of capture significantly. In Game 3, P2 invested 5 surround-attack plies for 0 captures. **Surround works less reliably here than I expected from the pilot's framing.**

**First-mover advantage / seat balance.** Same structural P1 favour. PPO trained-vs-trained 0.500 confirms the asymmetric counter is learnable. Naïve P2 mirror loses 100%.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + Go-style surround + threshold-race on a 3-D fractal. Argument:

(a) **Surround capture is one of the oldest known board-game mechanics** (Go ~3000 BCE).
(b) **Influence-based threshold-race** — same family as carpet rank-1, menger rank-1, menger rank-2. Generalized influence-as-territory weighting.
(c) **The combination "surround + influence + threshold"** is novel only insofar as Go has implicit territory and this game has explicit weighted scoring.
(d) **Menger sponge substrate** — same novelty axis as menger rank-1 and 2.
(e) **Expert-transfer test.** A Go player would recognize surround capture immediately. Influence-as-scoring is a 5-minute add. **However**, the z-tunnel escape mechanic + hole-edge surround vulnerability are substrate-specific tactical patterns that need 5-10 games to internalize. Total: 15-20 minutes to functional understanding.

**Closest known-game analogue:** **Influence-weighted Go on a 3-D Menger sponge.** The pilot called this the "Go-family game" of R19 — that's correct as far as the capture primitive goes, but the play experience is closer to "Go on a substrate with built-in escape routes" than to full Go. **Within R19**, this is the only game with surround capture.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 = custodian + connection on 2-D grid. R19 menger rank-3 = surround + influence-threshold on 3-D menger. **Different families.** Pilot called this "the closest R19 game to R8's family" because both inherit Go's surround/group primitive. I disagree mildly: R8's defining feature is the *connection* goal (build a chain across the board), not the custodian. **R8 and rank-3 share the surround/group pedigree but not the strategic core.** R8 has a single-move chain-completer (custodian-bridge) that's its crown jewel; rank-3 has no comparable single-move pivot — group preservation + threshold race is fundamentally arithmetic.

**Player rebuttal.**
- **Surround capture in 3-D fractal** is a genuinely novel pairing. The hole-edge / z-tunnel asymmetry creates substrate-driven tactical patterns absent from any published game.
- **Group preservation + influence accumulation dual-objective** is novel — Go has implicit territory; this game makes scoring explicit and weights it geometrically.
- **What subtracts**: (i) the substrate-driven uneven aggression (Game 1 captures in 1 ply, Game 3 fails after 5 plies) makes the game *less* than uniform Go, not more, (ii) z-tunnel escape is so easy that life-and-death tension is mostly limited to isolated stones, (iii) per-stone arithmetic is still mostly linear at +1.5/stone.

**Novelty score (post-adversary):** **5/10.** Same as rank-1 and rank-2. The substrate + Go-family combination is a real novelty driver, but the pilot's +1 over rank-1/2 (giving 6) overweights this. **In actual play** the game has slightly more tactical depth than rank-1 (real life-and-death decisions exist) and slightly less substrate-driven gameplay uniformity (z-tunnel asymmetry creates winner-take-all positions). Net: roughly the same novelty as rank-1/2, with a different distribution of where the novelty comes from. Anchored against R17 mean 3.50 (a 5 means "noticeably above R17 average because of the substrate + Go combination, but no headline mechanic that R8 didn't already have") and R8 8/10 (significantly below — R8's connection-bridge is transformative).

---

## Phase 5 — Verdict

**Team ID:** team-1
**Game ID:** 5048f71b62fd
**Rules Summary:** Place stones on a 9³ menger sponge (400 active cells) to accumulate influence (r=1, s=1.0, d=0.5) on cells you own. Go-style surround capture removes entire enemy groups with zero liberties (holes don't count as liberties). First to >21.21 effective influence wins — typically ~27 plies, ~14 stones per player.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 nominal.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Higher than rank-1's tactical depth because of life-and-death decisions (extension vs capture). But shorter games (~27 plies vs rank-1's ~39) mean less positional development. Z-tunnel escape is a real strategic axis that rank-1 lacks. Below pilot's 6 because the z-tunnel asymmetry makes group preservation easier than expected — life-and-death tension is mostly limited to isolated stones near hole-blocks.

- **Emergent Complexity: 5** — Z-tunnel escape, hole-edge surround, L2-attacker-scatter, ledger persistence — same vocabulary as rank-1 plus the Go-style group dynamics. Below pilot's 6 because the group dynamics are simpler than full Go (no ko, no seki, no eyes — the substrate makes traditional Go shapes mostly irrelevant).

- **Balance: 4** — Mirror = P1 wins by tempo at ~ply 28. Same knowledge-asymmetric pattern: PPO learned the counter; naïve P2 mirror loses 100%. Surround as P2's main weapon is conditional on the target's geometry (works on hole-edge isolated stones, fails on z-tunnel-accessible groups).

- **Novelty (post-adversary): 5** — see Phase 4. Substrate + Go-family combination is a real novelty driver but doesn't surpass rank-1/2's substrate-driven novelty by enough to score 6. Anchored conservatively against R17 mean 3.50 and R8 8.

- **Replayability: 5** — More variety than rank-1 because surround creates capture opportunities at multiple geometric niches (hole-edge, corner, L2-scatter). But the meta collapses fast once players learn the z-tunnel defense. Above carpet rank-2/3 expectation; below R8 by considerable margin.

- **Overall "Would I play this again?": 4** — Once: yes, the surround + 3-D fractal combination is interesting to feel, especially the z-tunnel escape. Repeatedly: no — same strategic ceiling as rank-1/2 (cluster + race + capture-trade), with the additional flaw that capture outcomes are highly geometry-dependent (sometimes 1-ply captures, sometimes 5-ply futile attacks). The variance reduces my willingness to replay. **Below pilot's 6** by 2 points: the pilot's "highest of the 6 R19 games" framing relies on the Go-family + 3-D fractal combination being transformative; in actual play it's incremental over rank-1/2 with different tactical surface area.

### CLOSEST KNOWN-GAME ANALOG
**Influence-weighted Go on a 3-D Menger sponge** — closest in mechanic. Within the project corpus, R8's Connection Go shares the surround/group primitive but has a different strategic core (build a chain). **No published analogue.**

### KILLER FLAWS
- **Mirror = P1 wins** (same as all R19 games).
- **Z-tunnel escape makes most groups routinely alive.** Pilot's "VERY aggressive surround capture" framing overstates the actual game-flow — surround works on isolated stones near hole-blocks but fails on multi-stone groups. The high-variance game-flow (Game 1 captures in 1 ply; Game 3 fails after 5 plies) feels uneven.
- **Short games (~27 plies) limit positional depth** despite high tactical depth per move.
- **Capture outcomes are geometry-dependent**: ~30-40% of P2's surround attacks succeed (rough estimate from Games 1-3); the rest are wasted moves. This raises the floor on "luck-of-position" vs "skill" ratio.
- **The eval report says this game's gen-6 leadership got dethroned in gens 7-8**, suggesting evolution preferred outnumber to surround. Pilot called this a fitness-metric artifact; my read: surround's high tactical complexity also makes its strategic depth more variable than outnumber's, so PPO learns it less consistently. **The "dethroning" might reflect surround being a higher-variance design** with more volatile training outcomes.

### BEST QUALITY
**Z-tunnel escape and the geometric asymmetry of surround attack**. Surround capture in a 3-D fractal substrate creates substrate-specific tactical patterns: stones near level-1 hole-blocks are surrender-vulnerable in 1-2 plies, stones with z-tunnel access are routinely alive. **This asymmetry is the most genuinely substrate-driven tactical pattern in any R19 game I've evaluated.** The pilot was right that this game has the strongest substrate-strategy coupling; I disagree that the coupling translates to highest overall quality.

### MENGER STRUCTURAL CONTRIBUTION
**Substantial but uneven.** The fractal hole pattern creates real strategic differences: hole-edge cells are surround-vulnerable; z-tunnel-accessible cells are surround-resistant. **Flattening to a regular 9³ would lose most of the surround tension** — every cell would have 6 liberties from the start, making single-stone capture effectively impossible. Estimate: ~+1 strategic-depth point and ~+1 novelty point from the substrate. **The pilot's "+2 depth" estimate over a flat-substrate version is too high in my read** — the z-tunnel escape mechanic compensates for the hole-edge vulnerability, leaving net depth gain at ~+1.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same as cross-cutting verdict). Mirror = P1 win is the structural problem.

Secondary improvements:
- **Increase threshold to 28-30** to extend games and allow more positional development. Trades some tactical sharpness for more strategic surface area.
- **Add a "ko rule" analogue** — Go without ko allows capture-recapture infinite loops in principle. Worth checking if any cycle-detection is needed.
- **Test against a connection secondary win** — combining surround + connection on this substrate would be very close to R8's Connection Go in 3-D. **Strongest R20 candidate from this evaluation** (same as pilot's recommendation). The combination would inherit R8's narrative arc + this game's life-and-death tension.
- **Calibrate the trained budget** — surround on this substrate may train less consistently than outnumber due to capture-outcome variance. R20 should consider 2-3× training time for surround-based games to verify whether the gen-7/8 dethroning was a training-budget artifact.

### Independent disagreement with pilot
The pilot scored this 6/10 — highest of the 6 R19 games. **I score 4/10.** Two main disagreements:
1. **Z-tunnel escape mechanic**: I found Game 3's group escape route (P1 extends to z=1, then z=2). The pilot's "fractal hole pattern reduces effective liberties" framing missed that cells at z=0 may be inactive while their z=1/z=2 counterparts are active — providing routine escape routes.
2. **"Closest R19 game to R8's family"**: The pilot weighted the Go-primitive shared inheritance heavily. I weight R8's *connection* goal more heavily — R8's depth comes from the chain-completion race, not the surround mechanic. R19 menger rank-3 inherits the Go primitive but not R8's strategic core.

The pilot's verdict reads as enthusiastic about a game-family fit; my read is more skeptical because the actual game-flow has more uneven outcomes than the family-fit suggests.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-1_game5048f71b62fd.md`.*
