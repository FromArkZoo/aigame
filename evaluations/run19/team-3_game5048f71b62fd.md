# Run 19 Evaluation — team-3 — Game 5048f71b62fd

**Team ID:** team-3
**Game ID:** `5048f71b62fd` (Menger rank-3, GE 0.3158, ELO 2354.6)
**Substrate:** Menger sponge (axis 9, 400 active cells / 729 grid positions, max_degree 6)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 5048f71b62fd`

---

## Phase 1 — Rule Comprehension

**Board / Turn structure / Action space.** Same as menger rank-1 and rank-2 (9³ menger sponge, 400 active cells, place-only, alternating, P1 first). Max_turns = 71.

**Capture (surround-2).** **Go-style group-liberty capture.** When a stone is placed at `c`, for each enemy *group* (maximal connected component of enemy stones via axis-adjacency) adjacent to `c`, count the empty *active* cells adjacent to any group member. If liberties = 0, the entire group is removed. **Holes do NOT count as liberties** — the fractal hole pattern subtracts from each cell's effective neighbour count.

**Propagation (influence, r=1, s=1.0, d=0.5).** Same kernel as rank-1.

**Win (threshold-race > 21.212).** **−29% from rank-1's 29.71** and the lowest threshold of all 6 R19 games. Avg game length 27.2 plies (vs rank-1's 38.8) — fastest of the menger games.

**Degeneracy check.**
- The fractal hole pattern reduces single-stone liberty counts at corner/edge positions: a single P2 stone at (1,0,0) has only 2 active neighbours ((0,0,0) and (2,0,0)) because (1,1,0) and (1,0,1) are holes. Single stones in such positions are 2-move-capturable. Verified empirically in the pilot's demo: P1 closes (0,0,2) and the P2 group {(0,0,1)} dies because (1,0,1) and (0,1,1) are holes — only 1 active liberty existed.
- Despite the hole-amplification, **groups of 4+ stones are essentially immortal**: extending in any direction adds new liberties faster than P2 can close them. The "alive group" concept is trivially achieved.
- Threshold 21.2 + per-stone yield ≈ +2.0/ply means games end in ~22 plies. **Captures rarely fire after the opening** because both sides quickly enter threshold-race mode.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — Mirror (structural reference)

Sequence: `0,728,1,727,9,719,81,647,2,726,18,710,162,566,3,725,27,701,243,485,4,724,5` (23 plies, **P1 wins +23.0 vs +21.0**).

Plot:
- P1 builds corner cluster at (0,0,0); P2 mirrors at (8,8,8).
- Same +2.0/ply rate as menger rank-1 (r=1 kernel identical, capture rule doesn't fire on far-corner mirror).
- M22: both at +21.0, just below threshold.
- M23: P1 places (5,0,0), pushes to +23.0, **`Done=True Winner=1`**.

Reflection: identical mirror dynamics to rank-1 with shorter horizon (23 vs 31 plies). Threshold scales the game length but doesn't change the structural P1 tempo lead.

### Game 2 — P2 surround attack vs P1 building extension

Sequence: `0,1,9,81,18,2,162` (7 plies, P1 has captured 1 P2 stone).

Plot:
- M1: P1 (0,0,0); M2: P2 (1,0,0); M3: P1 (0,1,0); M4: P2 (0,0,1).
- After M4: P2 has 2 stones threatening surround capture of (0,0,0). But (0,0,0) belongs to P1's growing group {(0,0,0), (0,1,0)} which has liberty (0,2,0).
- M5: P1 (0,2,0) — extend, group has 3 liberties (1,2,0), (0,3,0), (0,2,1). Safe.
- M6: P2 (2,0,0). Now P2's (1,0,0) group has liberties (3,0,0), (2,1,0), (2,0,1). 3 liberties.
- M7: P1 (0,0,2). The single P2 stone {(0,0,1)} has its liberties checked: (0,0,0)P1, (0,0,2)P1, (1,0,1)hole, (0,1,1)hole. **Zero liberties → captured.** P2 drops from 3 to 2 stones.
- After M7: P1 = +4.5 with 4 stones (+1.13/stone); P2 = +2.5 with 2 stones (+1.25/stone).

Reflection: **Capture works at the corner geometry exactly as the pilot described.** But it costs P1 nothing — the capturing move (0,0,2) was a *natural extension* of P1's cluster, not a sacrifice. **The capture is essentially free; P2 invested 3 moves and got 2 stones plus a captured rebate.** Tempo says P2 is now badly behind despite the cluster preservation.

### Game 2b — Surround chase along x-axis

Sequence: `1,0,2,3,11,12,20` (7 plies).

Plot:
- M1: P1 (1,0,0). Single stone, 2 liberties (low-degree edge cell).
- M2: P2 (0,0,0). Closes 1 liberty.
- M3: P1 (2,0,0) — extend. Group {(1,0,0)+(2,0,0)} has liberties (3,0,0), (2,1,0), (2,0,1). 3.
- M4: P2 (3,0,0). Closes 1.
- M5: P1 (2,1,0). Extends. Group liberties refresh to (2,0,1), (3,1,0), (2,2,0). 3.
- M6: P2 (3,1,0). Closes 1.
- M7: P1 (2,2,0). Extends. Group has 4+ liberties.
- After M7: **P1 = +5.5 with 4 stones (+1.38/stone); P2 = +2.5 with 3 stones (+0.83/stone)**.

Reflection: **The surround chase favours the attacked side, not the attacker.** P1's chained extensions form a tight 2D adjacency cluster (4 mutually-adjacent stones) gaining +1.38/stone. P2's harassing stones land in spread-out positions (no P2-P2 adjacency until late) gaining only +0.83/stone. **The chase is a tempo trap for P2.** This is the opposite of what the pilot's "P2 surround attack is dangerous" framing suggests — in fact, P2 should not chase P1 once P1 starts extending; the chase pays back negative.

### Game 3 — Seat swap. I play P2 with the interior 6-degree cluster

Sequence: `0,182,1,181,9,183,81,173,2,191,18,101` (12 plies, both at +11.0).

Plot:
- P1 builds corner cluster (6 stones); I (P2) build the 6-degree interior cluster at (2,2,2) (6 stones, working through the same plus-prism shape).
- M12 score: **P1 = +11.0, P2 = +11.0**. Identical per-stone yield (+1.83 average) — different from rank-2 because rank-3 uses r=1 kernel (no dist-2 reach), so the interior cluster's centre doesn't get bonus reinforcement from dist-2 peripherals.
- Projected: same as rank-1 — P1 wins on tempo around M22–24.

Reflection: **Without the r=2 dist-2 reach, the interior 6-degree cluster has no advantage over corner chain** — exactly as in rank-1. The interior cluster's *only* benefit on rank-3 might be liberty-richness (more liberties than a corner cluster, harder to capture), but since both sides easily build alive clusters, this doesn't translate into actual capture immunity that matters.

### Strategy guides

**P1 (offence/threshold push):** Build adjacency cluster at any low-numbered corner ((0,0,0), (0,0,8), (0,8,0), (8,0,0), (8,8,8) etc.). Each chain-extension nets +2.0. Don't spend moves on captures unless the capturing move is *also* an extension of your own cluster. **Threshold 21.2 ≈ 11 chain stones → game ends in ~22 plies.**

**P2 (defence + offence):** Mirror loses on tempo (Game 1, P1 wins by +2.0). Surround attack is a tempo trap (Game 2b — chasing costs you per-stone yield). **The only good P2 strategies on rank-3 are (a) match P1's corner chain symmetrically and accept the tempo loss, or (b) hope P1 plays a single stone in a 1-active-liberty trap cell, which a competent P1 will never do.**

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Effectively **one** (corner/interior cluster race). The "Go-style life-and-death" the pilot identified does not materialise because:
1. Threshold 21.2 ends the game in ~22 plies — too short for capture-and-pursuit dynamics.
2. Adjacency clusters of 3+ stones are immortal (extending faster than P2 can close).
3. Single-stone captures require P1 to play at trap cells, which P1 won't.

**Counter-play.** Mostly absent. Surround capture is a *latent* threat that disciplines P1 (don't play single stones in 2-liberty edge cells), but rarely fires in actual play. Once P1 commits to corner cluster, the rest is mechanical race.

**Short-term vs long-term.** ~11-ply horizon (avg game 22 plies, half each). Tactical depth is shallow because the threshold is so low. The pilot's "Go-style life-and-death" requires longer-horizon games to develop.

**Emergent concepts observed.**
- **Hole-as-liberty-stealer.** Real and verified — single stones in 2-active-neighbour cells (e.g., (0,0,1)) can be captured in 1 P1 move if both neighbours are holes. **But this is a punishment for P1-mistakes, not a weapon for P2.**
- **Surround chase backfire.** P2 chasing P1's extension pays back negative because P1's stones cluster while P2's stones spread. This is a *negative* emergent — the rules suggest the chase should work, but the geometry says it doesn't.
- **Capture-as-free-extension.** When P1's natural extension move *also* closes the last liberty of a P2 group, P1 gets a 2-for-1 (extension + capture). This happens naturally when P2 plays sandwich-attack-style early.

**Does the menger substrate matter?** The fractal holes amplify single-stone vulnerability at low-degree cells. **But only at the opening.** Once both sides are clustering, the holes don't matter. **Net contribution: ~0.5 points of opening tactical content, 0 points after move 5.**

**Does the propagation kernel matter?** Same r=1 as rank-1, same conclusions. The kernel is shorter-reach and doesn't produce the interior-cluster advantage that rank-2's r=2 has.

**Capture-rule contribution.** **Less than expected.** The pilot rated this game's "Go-family" mechanic highly. In actual play, captures fire only:
1. When P1 plays a single stone in a 2-active-liberty trap cell (rare — P1 avoids this once the rule is internalised).
2. When P1's own extension move happens to close the last liberty of a P2 group (free 2-for-1).

Neither produces deep strategic content. **The capture rule is a constraint on opening play, not a generator of mid-game depth.**

**First-mover advantage / seat balance.** Same structural P1 favour from tempo. PPO 0.500 trained-vs-trained reflects PPO learning to defend against capture traps and play efficient cluster build. **Pie rule needed**, same as all R19 games.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + Go-style surround + threshold-race on a 3D fractal. Argument:

(a) **Surround (Go) capture** is the oldest captures rule in board games (Go, ~3000 BCE). Not novel.

(b) **Influence-based threshold-race** is the same family as menger rank-1/2 and carpet rank-1/2/3.

(c) **The combination** "surround + influence + threshold" is not in any published abstract game I know of. Within the project corpus: this is the only R19 game using surround capture (the other 5 use outnumber or — in carpet rank-2 — custodian).

(d) **Menger sponge substrate** is unprecedented. Same as rank-1/2.

(e) **Expert-transfer test.** A Go player would recognise surround immediately. Influence-as-scoring is foreign but learnable in 5 minutes. The fractal substrate adds ~5 minutes of "which cells are active" lookup. **Total: 5–10 minutes to functional understanding.** No irreducible new concept.

**Closest known-game analogue:** **Go with influence-weighted scoring on a Menger sponge.** Inside the project corpus, this is the **Go-family R19 entry**. Rank-1 (`1f9191b5d4e6`) is the Tafl-family equivalent; rank-2 (`98739cb0838a`) is the same family with parameter shift.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 = custodian + connection; R19 menger rank-3 = surround + influence-threshold. Both inherit from Go's family but differently: R8 uses Othello-style flips (custodian) + Hex-style connection win; rank-3 uses Go's surround + Tumbleweed-style threshold. **R8's mechanics interact with each other** (custodian flip can complete connection in 1 move — depth-multiplier). **Rank-3's mechanics do not interact** — captures don't help with influence accumulation; influence doesn't help with capture. They're parallel scoring systems. **This is rank-3's biggest deficit vs R8: no depth-multiplier emergent.**

**Player rebuttal (P1 + P2).**
- The **hole-as-liberty-stealer** is a genuine substrate-driven mechanic. The fractal *does* add real tactical content at the opening. Worth ~0.5 novelty points beyond influence-Tafl on a regular grid.
- **Group preservation in 3D fractal** is a real but easy-to-master skill. Doesn't deepen mid-game play.
- **Subtracting from novelty:** the threshold is set so low (21.2) that the Go-like life-and-death dynamics never get tested. With a higher threshold (e.g., 35–40), this game might earn the depth the pilot claims.
- **The pilot's "this is the deepest R19 game" claim depends on Go-like dynamics that don't actually fire.** I disagree with the pilot's framing. Empirically, the game plays as a tempo race like rank-1, not as a Go-family deep game.

**Novelty score (post-adversary):** **5/10.** Same as rank-1 — the substrate is unprecedented, the family is the same as the other R19 games, and the surround capture *almost* adds Go-like depth but doesn't fire often enough to deliver. **Anchored:** above R17 mean (3.50) by 1.5 because of substrate + Go-family combo; below R8 (8) by 3 because no depth-multiplier interaction; **same as rank-1 because the surround mechanic doesn't deliver the depth it advertises.** Half a point below the pilot's 6/10 — I think the pilot over-credited the latent capability that the threshold doesn't allow to develop.

---

## Phase 5 — Verdict

**Team ID:** team-3
**Game ID:** 5048f71b62fd
**Rules Summary:** Place stones on a 9×9×9 menger sponge. Each placement adds ±1.0 to itself and ±0.5 to active dist-1 neighbours. Go-style surround capture removes any enemy group with zero liberties (holes don't count as liberties). First to > 21.212 effective influence wins. Games typically end in ~22 plies; capture rarely fires after the opening because adjacency clusters are immortal.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Below pilot's 6 by a margin. The Go-style mechanic *advertises* depth but the threshold ends the game before mid-game life-and-death develops. The "alive group" concept is trivially achieved (any 3+ adjacency cluster). Empirically the game plays as a faster version of rank-1's tempo race, not as a Go-family deep game. **Anchor:** R17 mean 3.5 + 0.5 for opening tactical content from holes = 4.
- **Emergent Complexity: 4** — Hole-as-liberty-stealer + capture-as-free-extension are real but minor. Surround chase backfire is interesting (negative emergent — the rules look like they should reward chasing but the geometry punishes it). Total: 2 emergent patterns. Less than rank-2's 3 patterns.
- **Balance: 3** — Same mirror = P1 wins. P2 has no robust counter-strategy. The "P2 surround attack" the pilot mentions backfires (Game 2b) — chasing costs P2 per-stone yield. PPO 0.500 reflects learned defence, not human-discoverable balance.
- **Novelty (post-adversary): 5** — see Phase 4. Same substrate as rank-1; Go-family + fractal is a fresh combination but the threshold limits how much of the Go-family content actually fires.
- **Replayability: 3** — Same as rank-1. Once cluster strategy is internalised, openings collapse to "any corner". The hole-trap discipline (don't play single stones in 2-active-liberty cells) is a one-time learn. Surround chase is a one-time learn (don't do it).
- **Overall "Would I play this again?": 4** — Once: yes, the hole-as-liberty-stealer trick is interesting. Repeatedly: no — the game ends too fast for the Go-like depth to develop. **Anchor:** R17 mean 3.5 + 0.5 = 4.0. Equal to rank-1; below rank-2 (5) because rank-2's longer horizon enabled real strategic discovery and rank-3's shorter horizon prevented the surround mechanic from delivering its potential.

### CLOSEST KNOWN-GAME ANALOG
**Go with influence-weighted scoring on a Menger sponge.** Inside R19, this is the only surround-capture game (rank-1/2 use outnumber; carpet rank-2 uses custodian).

### KILLER FLAWS
- **Threshold too low.** 21.2 ends the game in ~22 plies — half what's needed for Go-style life-and-death dynamics to develop. The capture rule's potential is not realised.
- **Mirror = P1 wins on tempo.** Same structural issue.
- **Surround chase is a tempo trap for P2.** P2's natural attack pattern (chase P1's extension) loses per-stone yield because P1's chain clusters while P2's stones spread.
- **Capture rule rarely fires after move 5.** Adjacency clusters are immortal; both sides easily build alive groups.
- **No depth-multiplier emergent.** Unlike R8 (custodian-bridge completes connection) or rank-2 (interior cluster + late-game captures), there's no single-move pattern that creates strategic non-linearity. Captures are extension-side-effects, not strategic decisions.

### BEST QUALITY
**Hole-as-liberty-stealer at the opening.** The fractal hole pattern reduces edge-cell liberties enough to make corner/edge-cell single stones legitimately capturable. This is a real substrate-driven tactic — punishment for opening at low-degree cells. Game-defining for the first 4–5 plies, then irrelevant. The single most genuinely substrate-coupled mechanic in any R19 game I've evaluated, but its impact is brief.

### MENGER STRUCTURAL CONTRIBUTION
**The substrate matters at the opening, not the mid-game.** Holes amplify single-stone vulnerability for the first 4–5 moves; afterwards both sides cluster and holes become irrelevant. **Estimate: flattening to a regular 8³ cube would lose ~0.5 points of opening tactical content, ~0 points of mid-game depth.** The pilot estimated ~2 points loss; I think they're crediting a depth that would emerge with a higher threshold but doesn't with this one.

### IMPROVEMENT IDEAS

**Single best change: increase threshold to 35–40.** This is the *transformative* change for rank-3. With current threshold 21.2, the game ends in 22 plies — before Go-like life-and-death has time to develop. With threshold ~38 (similar to rank-2), games would extend to ~50 plies and the surround mechanic would have room to drive multi-stage strategic decisions. **This would likely move the game from a 4/10 to a 6/10.** The pilot's claim about Go-family depth would actually become true.

Secondary improvements:
- **Pie rule** (same as all R19 games — addresses mirror-P1-wins).
- **Add ko rule analogue** (prevents capture-recapture infinite loops; not observed in my games but theoretically possible).
- **Test against a connection secondary win** — combining surround + connection would be very close to R8's "Connection Go" on a 3D fractal substrate. **This is the strongest R20 candidate from this evaluation.** Pie rule + raised threshold + connection secondary = a plausible 6–7/10 game.
- **Penalise adjacency clusters in fitness** — encourage spread shapes that have more capture-sensitive geometry.

### Notes on the dethroning
The eval report says rank-3's surround-style game led at gen 6 and was overtaken by outnumber-based games in gens 7-8. The pilot speculated this was a "fitness-metric artifact." **I think it's a fitness-metric *and* genuine quality artifact.** GE may underweight surround's strategic depth (which depends on threshold/length to develop), but the threshold parameter chosen for this rank-3 game also genuinely caps the mechanic's payoff. The rule blob is solid; the threshold is too low. **R20 should include surround-capture games with threshold ≥ 38.**

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-3_game5048f71b62fd.md`.*
