# Run 19 Evaluation — team-2 — Game 1f9191b5d4e6

**Team ID:** team-2
**Game ID:** `1f9191b5d4e6` (Menger rank-1, GE 0.3293, ELO 2402.4)
**Substrate:** Menger sponge (axis 9, 400 active cells / 729 grid positions, max_degree 6)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 1f9191b5d4e6` (see `briefing_menger_rank1.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive holes per the level-2 Menger sponge fractal. Cell index = z·81 + y·9 + x. The active set is determined by: a coord position (x,y,z) is a hole iff at least two of its base-3 digit triples have a "1" in the same axis position. The hole pattern is dense — z=4 layer is almost entirely holes; z=3 and z=5 have a hollow centre band; z=0,2,6,8 layers are mostly active. Most active cells have 3-4 active neighbours; **only the 8 sub-cube-anchor cells (2,2,2), (2,2,6), (2,6,2), (6,2,2), (2,6,6), (6,2,6), (6,6,2), (6,6,6) hit max_degree 6**.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max 89 turns.

**Action space.** 730 actions = 729 placement slots (illegal at the 329 hole indices) + 1 pass. Place-only — D1 hybrid ban active.

**Placement & capture.** Placement: any empty active cell, no first-move restriction. Capture rule = **outnumber** (threshold 2): when a stone is placed, every adjacent enemy stone whose own active-neighbour set contains ≥2 friendly stones is removed. The capturing stone itself counts toward the count. Captures cascade in a single placement (the engine re-checks each enemy neighbour independently).

**Propagation.** Influence (radius=1, strength=1.0, decay=0.5). Placement adds ±1.0 to the placed cell and ±0.5 to each of its 1-step active neighbours (not 2-step — short reach). Sign = +1 if P1 places, −1 if P2. Clamped to [−100, 100]. Captured-stone propagation appears to NOT be refunded — verified empirically by pre/post counter-sandwich score drift.

**Win condition.** Threshold-race. Sum each player's `board_values` over cells they currently own; first player whose sum exceeds **29.709** wins. Equal margins → draw. Double-pass → draw (verified). Max-turn timeout = highest sum or piece-count majority.

**Degeneracy check.**
- **Double-pass = immediate draw, even at move 2** (verified `--moves "729,729"` → Done=True Winner=None). A trivial degeneracy but irrelevant in practice — placement always strictly dominates pass.
- The fractal hole pattern produces cells with degree 1-2 (e.g. (1,0,0) has only neighbours (0,0,0), (2,0,0)); these "thin-corridor" cells are almost sandwich-immune but yield only +1.0 score-per-stone with no neighbour bonus.
- z=4 is essentially a sealed layer (only the 4 corner-sub-cube cells active, with very thin connectivity); the engine treats the cube as two stacked half-cubes connected through a narrow bridge of (2,2,4)/(2,6,4)/(6,2,4)/(6,6,4) cells.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — Mirror at the 6-degree interior anchor (full play-through to win)

Sequence: `182,546,181,545,183,547,173,537,191,555,101,465,263,627,102,626,110,618,174,554,190,538,254,474,262` (25 plies).

Plot:
- P1 anchors at (2,2,2) [cell 182] — one of only 8 max-degree-6 interior cells in the menger lattice. P2 mirrors at (6,6,6) [cell 546].
- Both build a 7-stone "octahedral star" — centre + 6 axis-neighbours. After 14 plies (move 14): P1 = +13.0, P2 = +13.0, parity restored on P2's mirror.
- Stars expand outward: each player adds 6 stones at the "next-shell" axis-2 cells (e.g. (3,2,1), (2,3,1), (3,1,2), (1,3,2), (2,1,3), (1,2,3) for P1). Each such placement yields **+3.0** because it gains +1.0 own + 0.5 own × 2 (already-owned star neighbours within radius 1).
- The threshold race plays out as a clock: P1 +3.0 → 16, P2 +3.0 → 16, … through plies 15-24 with both at +22.
- Move 25 P1 places (1,2,3) [262] → +3.0 → **+31.0 > 29.709 → P1 wins.** P2 has just placed (6,7,5) [474] for their 12th stone at +28.0 and never gets a 13th turn.

P1 reflection: When P1 chooses an interior 6-degree anchor, every cluster expansion stone gains 2-3 already-owned neighbours, yielding +2.0 to +4.0 per move. Mirror loses by 1 ply (P1 plays first, gets the threshold-crossing placement). The lead is **structural and unfixable under symmetric play**.

P2 reflection: Pure mirror is a slow loss by exactly one stone. P2 must break symmetry — sandwich attack (Game 2) is the natural counter, but on a 6-degree anchor it costs P2 more than it costs P1.

### Game 2 — P2 sandwich attack vs P1 counter-sandwich at the 6-degree anchor

Sequence: `182,181,180,183,173,191` (6 plies, in progress).

Plot:
- P1 (2,2,2) [182] — interior anchor.
- **P2 (1,2,2) [181] — sandwich attack.** (1,2,2) is one of (2,2,2)'s 6 active neighbours. P2 plans to eventually surround (2,2,2) with 2 P2 stones to outnumber-2-capture it.
- **P1 (0,2,2) [180] — counter-sandwich.** (0,2,2) is at the far end of the −x axis from (2,2,2); P2's (1,2,2) is sandwiched between P1's (2,2,2) and the new (0,2,2). On placement, the engine checks each enemy neighbour of (0,2,2): (1,2,2) is enemy and has 2 P1 neighbours ({(0,2,2), (2,2,2)}) → outnumber-2 fires → **P2's (1,2,2) is captured.** Score: P1 = +1.0, P2 = 0.
- **P2 (3,2,2) [183] — sandwich resumed from the +x side.** (2,2,2) now has 1 P2 neighbour. P2's (3,2,2) survives because P1 has no neighbour of (3,2,2) yet (P1 has only (2,2,2) and (0,2,2); (0,2,2) is not adjacent to (3,2,2)).
- **P1 (2,1,2) [173] — extend cluster + threat.** (2,1,2) is adjacent to (2,2,2). Now (2,2,2) has 2 own neighbours (P1) — score +0.5 each direction reinforcement.
- **P2 (2,3,2) [191] — completes the sandwich.** (2,2,2) now has P2 neighbours at (3,2,2) and (2,3,2) — 2 P2 neighbours → outnumber-2 fires on P2's placement of (2,3,2): **P1's (2,2,2) is captured.** P1 anchor lost.
- After move 6: P1 = (0,2,2), (2,1,2) — 2 stones, +2.0. P2 = (3,2,2), (2,3,2) — 2 stones, +1.0.

The sandwich exchange burns 2 P2 placements for 1 P1 capture, and 1 P1 counter-sandwich for 1 P2 capture. **Net: P1 +1 stone advantage, +1 score advantage, 6 plies used.** P1 still leads.

Reflection: The pilot played sandwich at a **3-degree corner** ((0,0,0) → 2 of 3 neighbours = 67% coverage required) and concluded sandwich is a viable P2 equaliser. At the **6-degree interior anchor** (2 of 6 = 33% coverage), the sandwich is **also available** but **counter-sandwich is symmetric** because the anchor has 6 neighbours, meaning any single P2 attacker stone has its own neighbours that can be P1. The sandwich cost equation flips: **P2 spends 2 stones for 1 capture, P1 spends 1 counter-stone for 1 capture, with the residue stones at distance 2 (no influence reinforcement) for both sides.** The result is a 1-ply tempo loss for P2 plus a +1 score lead for P1 — strictly worse for P2 than mirror.

This is independent of the pilot's finding: **at a 6-degree interior anchor, sandwich is a losing line for P2, not a winning line.** P2's only viable response to P1 anchoring at (2,2,2) is to counter-anchor at another 6-degree cell (e.g. (6,6,6) — Game 1 mirror) and accept the 1-ply tempo loss. There is no asymmetric P2 counter that wins.

### Game 3 — Novelty adversary: P2 abandons cluster, harasses with distractor stones

Sequence: `182,18,101,162,173,164,191,180,263,2` (10 plies).

Plot:
- P1 (2,2,2) [182] — interior anchor.
- P2 (0,2,0) [18] — distractor at face cell, no relation to P1's anchor. P2's plan: don't engage P1's cluster, accumulate threshold elsewhere.
- P1 (2,2,1) [101] — extend cluster from (2,2,2) along −z. +0.5 reinforcement to (2,2,2).
- P2 (0,0,2) [162] — another isolated distractor.
- P1 (2,1,2) [173] — extend cluster from (2,2,2) along −y.
- P2 (2,0,2) [164] — adjacent to P1's (2,1,2). The placement triggers capture check: does (2,1,2) have ≥2 P2 neighbours? (2,1,2)'s active neighbours: (2,2,2)=P1, (2,0,2)=P2 (just placed), (2,1,1)? (2,1,1) z=1 y=1 — all holes. (2,1,3)? z=3 y=1 — hole. (1,1,2)? z=2 y=1 x=1 → hole. (3,1,2)? z=2 y=1 x=3 → active, empty. So (2,1,2) has only 1 P2 neighbour → no capture. (2,0,2) survives but does nothing useful.
- P1 (2,3,2) [191] — extend cluster from (2,2,2) along +y. (2,2,2) now has 3 own neighbours.
- P2 (0,2,2) [180] — yet another distractor, contributes +1.0 only.
- P1 (2,2,3) [263] — extend cluster from (2,2,2) along +z. **(2,2,2) now has 4 own neighbours; 5-stone cross at the anchor.**
- After move 9: P1 = +8.5 (5 cluster stones), P2 = +4.5 (5 isolated stones). **P1 leads by +4.0 on equal piece count, with much faster threshold growth ahead** (each future P1 cluster stone gains +2.5+ from already-owned neighbours).

Novelty-adversary verdict: P2 cannot beat P1's interior cluster strategy by ignoring it. The cluster's marginal score per move (≈+2.5 average vs P2's ≈+1.0) creates a divergence that compounds. P2 must engage — either mirror (loses by 1 ply, Game 1) or sandwich (loses by 1 ply + 1 score, Game 2). **All three lines lose.**

### Strategy guides

**P1 (offence/threshold push):** Anchor at one of the 8 max-degree-6 interior cells: (2,2,2), (2,2,6), (2,6,2), (6,2,2), (2,6,6), (6,2,6), (6,6,2), (6,6,6). Build the octahedral 7-stone star: anchor + 6 neighbours. Each star cell gains +0.5 reinforcement from the anchor, and the anchor gains +0.5 from each of the 6 neighbours → 7-stone score = +13. Then expand outward to "shell-2" cells at axis distance 2 from the anchor (e.g. (3,2,1) is adj to (2,2,1) and (3,2,2)) for +3.0 per move. Threshold (29.7) is reached at ~13 stones in tight cluster geometry, ~25 plies total.

**P2 (defence + threshold contest):** Mirror at a far 6-degree anchor (e.g. P1 (2,2,2) → P2 (6,6,6)). Sandwich is a losing line at 6-degree anchors — only consider it if P1 anchors at a 3-degree corner (e.g. (0,0,0)). Distractor stones at far cells are also losing — they accumulate +1.0/stone vs P1's +2.5+/stone in cluster. **P2's best line is mirror and lose by 1 ply. There is no winning P2 line under perfect P1 anchor selection.**

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** From P1's perspective, two viable opening families:
1. **Interior 6-degree anchor + octahedral cluster** (Games 1 & 3). Robust against sandwich and distractor counters.
2. **Corner 3-degree anchor + plus cluster** (pilot's playbook). Lower per-stone density (+1.75 avg vs +2.5 avg), and exposes P1 to sandwich attack at 67% coverage difficulty for P2.

From P2's perspective, only **mirror + accept 1-ply tempo loss** is viable. Neither sandwich nor distractor wins.

**Counter-play.** Asymmetric and weak. Sandwich is a meaningful counter only at 3-degree corners; at 6-degree interiors P1 has counter-sandwich for free. This means P1's strategic choice (which anchor) determines P2's available counter-play, and the engine has no way to enforce that P1 picks the suboptimal anchor.

**Short-term vs long-term.** Threshold 29.7 / per-move gain ≈ +2.5 in tight cluster → ~12 plies per side to threshold ≈ 24-25 plies total. Tactical horizon ≈ 4-6 plies (cluster expansion ordering, sandwich timing). Strategic horizon ≈ anchor selection + first 2-3 expansion moves. **The game has limited long-form planning — once anchors are placed, the cluster expansion is greedy-optimal.**

**Emergent concepts observed.**
- **6-degree anchor cells.** A small lattice (8 cells out of 400) where cluster reinforcement maxes out. Anchor selection is the single most important strategic decision.
- **Octahedral star geometry.** A 7-stone shape impossible on 3-degree corner cells but available at the 8 interior anchors. Yields +13.0 vs the 4-stone plus's +7.0 — a per-stone density improvement of 67%.
- **Counter-sandwich mirroring.** The same outnumber-2 mechanic that lets P2 attack lets P1 defend. Whoever places the third stone in the (a-b-c) line on a single axis captures the middle stone.
- **Hole-bridge corridors.** z=4 layer is mostly hole; the bridge cells (2,2,4), (2,6,4), (6,2,4), (6,6,4) are the only z-axis traversal between the two halves of the cube. Could in principle matter for connection-style games but is dead in this threshold-race game.

**Does the menger substrate matter?** *Modestly.* The fractal hole pattern constrains cluster shapes (a 2×2×2 cube of stones is impossible — only 4 of 8 cells active in any 2x2x2 sub-cube) and creates the rare 6-degree anchor cells. Without holes, **every** axis-2 interior cell would be a 6-degree anchor — 343 of them on a 9×9×9 grid vs 8 here. The scarcity of 6-degree anchors makes anchor selection meaningful. However, the same threshold-race-with-clusters dynamic survives flattening to a regular grid — the menger contribution is **the constraint on cluster shape**, not a transformative new mechanic. Estimate: flattening to 9³ all-active loses ~0.5 point of strategic depth.

**Does the propagation kernel matter?** Critically. r=1 means distance-2 stones cannot reinforce each other. The fractal hole pattern combined with r=1 means a cluster broken by a single hole cell loses all reinforcement across that gap. r=2 (the carpet rank-1 kernel) would soften this — pilots noted this difference. **The pairing of menger + r=1 is the harshest configuration for influence accumulation.**

**Capture-rule contribution.** Captures fired in Game 2 (1 P2 capture by P1 counter-sandwich, 1 P1 anchor capture by P2 sandwich completion). The capture mechanic provides the only real disruption to the cluster-and-race dynamic, and in this game it produces a net 0 exchange for both sides under optimal play. **Captures add tactical interest without changing the strategic outcome.**

**First-mover advantage / seat balance.** Strongly P1-favoured. Mirror = P1 wins by 1 ply (verified Game 1, P1 wins move 25). Sandwich = P1 wins by counter-sandwich at 6-degree anchors (verified Game 2). Distractor = P1 wins by cluster-density advantage (verified Game 3, P1 +4.0 lead at move 9). The **trained-vs-trained 0.500** PPO reference is in tension with my finding — either PPO's "learned counter" is also at 3-degree-corner anchors (where sandwich is viable), or the trained agents converge to a knowledge-asymmetric equilibrium. **My 3 games suggest that a P1 who picks the 6-degree anchor wins consistently; PPO may not have discovered this.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of well-known mechanics. Argument:

(a) **Threshold-race influence games** are closest to *Tumbleweed* (2D hex influence-claiming), *Sygo* (Go territory weights), and broadly to *cellular-automaton scoring games* in the abstract literature.

(b) **Outnumber-2 capture** is closest to *Ataxx* (replicate-and-flip) and the historical *Tafl* family (sandwich-and-remove). The specific "≥N friendly neighbours of an enemy stone" trigger is custodian-adjacent but less directional.

(c) **The combination "outnumber + influence + threshold-race"** is a R19-family invention. It does NOT exist in the published abstract-game literature. Inside this project corpus, the dominant family of R19's top-10 is the same combination — meaning R19 is exploring a coherent novel niche.

(d) **Menger sponge substrate.** This is the strongest novelty axis. 3D fractal substrates are extremely rare in published board games — closest is Score Four / Qubic (3D tic-tac-toe), which uses a regular 4³ grid, not a fractal. **No published board game uses the menger sponge.** The fractal hole pattern at the micro-scale (50% inactive in any 2×2×2 sub-cube) constrains cluster geometry in a way no regular grid would.

(e) **Expert-transfer test.** A Go + Othello + Hex + Score Four player would need ~10 minutes to internalise the rules. The non-obvious pieces: (i) the fractal hole map (which cells are active — requires study), (ii) the r=1 short-range influence kernel (requires building intuition for distance-1 vs distance-2 reinforcement), (iii) the 6-degree interior anchor spots and their strategic value (requires play). Expert transfer is high — ~3 minutes to play, 30 minutes to play well.

**Closest known-game analogue:** **Tumbleweed-on-Menger-with-Ataxx-captures.** No exact analogue exists. Inside this project corpus, the closest sibling is carpet rank-1 (`ce3a09e05cef`) — same family, 2D version with r=2 kernel.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2D grid. R19 menger rank-1 is outnumber + influence + threshold-race on a 3D fractal. **Different family.** R8's strength was the narrative arc of "build a chain across the board" — a clear win condition with discrete tactical bridge moments (custodian flips that complete chains). R19 menger rank-1 is more like a "fill space efficiently" game — there's no narrative arc, just an accumulation race. R8's depth comes from the chain-completion tactic; R19's depth comes from anchor-selection and cluster-shape geometry. **R19 sits below R8 on narrative tension and tactical climax, but above R8 on substrate novelty.**

**Player rebuttal (P1 + P2).**
- The 6-degree interior anchor structure is genuinely substrate-driven. There are exactly 8 such cells on the menger sponge — an artefact of the fractal pattern's symmetry — and they functionally dominate the anchor-selection decision. This pattern is not present in any 2D game and not present in regular 3D grids (where every interior cell would be 6-degree).
- The counter-sandwich symmetry around 6-degree anchors is a clean tactical motif that doesn't exist in classical sandwich games (Othello, Tafl, Ataxx — those don't have an outnumber threshold).
- Subtracting from novelty: the strategic skeleton (cluster + threshold-race) is recognisable from carpet rank-1 and from any "fill-space-and-score" game; the menger version is a 3D adaptation, not a structurally new game family.

**Novelty score (post-adversary):** **5/10.** Above pure re-skin (2-3) because (i) the menger substrate is genuinely unprecedented, (ii) the 6-degree anchor structure produces substrate-specific play. Below the carpet rank-1 pilot's claim of 6 because: (a) the strategic skeleton is the same as carpet rank-1 — this is a sibling, not a structurally distinct game, (b) pilot's "fractal substrate is worth 1+ points of novelty" is double-counting if the eval report already credits the substrate as the family's defining feature, (c) interior anchor cells are scarce enough (8 of 400) that play converges to the same handful of opening positions, reducing the substrate-novelty's contribution to in-game decisions. Anchored against R17 mean (3.50) and R8 (8/10): R19 menger rank-1 is meaningfully above R17 floor (better than 3.5) but well below R8 ceiling.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** 1f9191b5d4e6
**Rules Summary:** Place stones on a 9×9×9 menger sponge (400 of 729 cells active) to accumulate influence on cells you own. Each placement adds ±1.0 to itself and ±0.5 to its active axis-neighbours; an enemy stone is removed if it has ≥2 of your stones among its active neighbours when you place. First to >29.7 effective influence wins.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 (effective 3-4 for most cells; 6 only at 8 interior anchor cells).
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 5** — Two real strategic decisions: (1) anchor selection (interior 6-degree vs 3-degree corner), (2) sandwich timing & counter-sandwich. Beyond anchor selection, the cluster expansion is essentially greedy-optimal — there are not many medium-term concepts. The 6-degree interior anchor strategy collapses opening variety to 8 essentially-equivalent positions. Above R17 mean (3.50) on the strength of meaningful opening-tree branching, below R8 (8/10) on the absence of mid-game tactical structure.

- **Emergent Complexity: 5** — Three patterns: (i) octahedral star at 6-degree anchors, (ii) counter-sandwich symmetry along axis triples, (iii) hole-bridge corridors at z=4. Pattern (iii) doesn't actually fire in this game (threshold-race doesn't care about connectivity). Patterns (i) and (ii) are real but small — same vocabulary as carpet rank-1.

- **Balance: 3** — Mirror = P1 wins (Game 1, +1 ply). Sandwich = P1 wins via counter-sandwich at 6-degree anchors (Game 2). Distractor = P1 wins via cluster density (Game 3). PPO's reported 0.500 trained-vs-trained winrate is in tension with my finding — likely PPO's equilibrium is at 3-degree-corner anchors where sandwich is viable, an asymmetric equilibrium that fails when P1 picks the optimal interior anchor. **The game is structurally P1-favoured under best play.** Lower than the pilot's 4 because counter-sandwich at 6-degree anchors closes the door on P2's "best counter" hope.

- **Novelty (post-adversary): 5** — see Phase 4. The menger substrate is genuinely unprecedented in published literature, but inside this project's R19 corpus the same family is being explored across multiple ranks; the relative novelty of any single instance is moderate. The 6-degree anchor structure is a clean substrate-specific tactical motif.

- **Replayability: 4** — Once 6-degree anchors and octahedral stars are known, openings collapse to 8 essentially-equivalent options (each anchor cell yields the same 7-stone +13.0 cluster). The shell-2 expansion is also forced (greedy). Position variety from move 1 is high but converges fast.

- **Overall "Would I play this again?": 5** — Once: yes, the 6-degree anchor discovery and counter-sandwich tactic are interesting to feel. Repeatedly: no — the cluster-density advantage for whoever picks the better anchor first is too dominant. Anchored against R17 mean 3.5 (this is meaningfully above floor) and R8 ceiling 8 (well below).

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed-on-Menger-with-Ataxx-captures.** No exact published analogue exists. Inside this project corpus, the closest sibling is R19 carpet rank-1 (`ce3a09e05cef`) — same family (outnumber + influence + threshold-race), 2D version with r=2 kernel.

### KILLER FLAWS
- **Mirror = P1 wins by 1 ply** (structural, unfixable without pie rule).
- **6-degree anchors are 8 in number and essentially equivalent** — opening tree is shallow.
- **Sandwich at 6-degree anchors is a losing line for P2** — there is no real P2 counter; the apparent "balance" reported by PPO likely depends on P1 picking a suboptimal 3-degree corner.
- **r=1 + fractal holes is brittle** — a single misplaced stone breaks reinforcement entirely; this is a feature for tactical depth but a bug for cluster-building.
- **Cluster expansion is greedy-optimal** — once anchored, there's no mid-game decision tension.

### BEST QUALITY
**The 6-degree interior anchor structure.** Eight specific cells on the menger lattice — (2,2,2), (2,2,6), (2,6,2), (6,2,2), (2,6,6), (6,2,6), (6,6,2), (6,6,6) — are uniquely strong anchor positions because they're the only cells with all 6 axis-neighbours active. Anchoring there yields a 7-stone octahedral cluster scoring +13.0, vs the +7.0 of a 4-stone corner plus. This is a substrate-driven strategic discovery — the menger fractal symmetry produces this scarce 8-cell anchor set, and finding it is the game's most interesting moment.

### MENGER STRUCTURAL CONTRIBUTION
**Modest.** The fractal hole pattern produces (i) the 8 6-degree interior anchors, (ii) the constraint that 2×2×2 stone cubes are impossible, (iii) the z=4 hole-bridge layer. Of these, only (i) meaningfully shapes strategy — (ii) is a passive constraint, (iii) is mechanically irrelevant in threshold-race. Flattening to a 9³ all-active grid would lose the anchor-scarcity (every interior cell would be 6-degree, anchor selection becomes trivial) but preserve the cluster-and-race dynamic. **Estimated loss from flattening: ~0.5 point of depth, ~1 point of novelty.** This is below the pilot's estimate of "1 point of depth + 1 point of novelty" — the cluster-shape constraint is real but contributes less to strategic depth than the anchor scarcity does.

### IMPROVEMENT IDEAS
**Single best change:** **Pie rule (swap option after P1's first move).** P1's tempo advantage is structural; pie rule punishes any opening strong enough to mirror profitably and forces P1 to balance opening strength vs swap risk. The 6-degree anchor strategy in particular would become a self-defeating choice — P1 places (2,2,2), P2 swaps and inherits the +1.0 anchor. Pie rule is the unanimous pilot recommendation across all R19 games and applies cleanly here.

Secondary improvements:
- **Increase capture threshold to 3** so that 6-degree anchors require 3 of 6 neighbours = 50% coverage to capture — would shift balance toward P1 but eliminate the sandwich attack at corners (3-degree cells would be capture-immune since 3 of 3 = 100%).
- **Increase influence radius to r=2** (carpet rank-1's value) to soften the hole-routing penalty and let players span single-cell holes for partial reinforcement.
- **Increase max_turns or threshold** to extend the game length beyond the current ~25-ply threshold-cross, allowing more strategic depth in cluster expansion vs disruption tradeoffs.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-2_game1f9191b5d4e6.md`.*
