# Run 19 Evaluation — team-pilot — Game 98739cb0838a

**Team ID:** team-pilot
**Game ID:** `98739cb0838a` (Menger rank-2, GE 0.3213, ELO 2402.6)
**Substrate:** Menger sponge (axis 9, 400/729 active, max_degree 6)
**Helper:** `eval_run19_helper.py --game 98739cb0838a`
**Note:** Direct seed that survived 8 generations of evolution untouched. Comparing this to menger rank-1 (`1f9191b5d4e6`, crossover-derived) reveals what evolution did or didn't add to the family.

---

## Phase 1 — Rule Comprehension

**Board / Turn structure / Action space.** Same as menger rank-1: 9³ menger sponge, 400 active cells, place-only, alternating, P1 first.

**Capture (outnumber-2).** Same as rank-1.

**Propagation (influence, r=2, s=0.9895, d=0.3037).** Two key differences from rank-1:
- **r=2 not r=1.** Distance-2 cells now receive influence (≈ +0.09 each).
- **Decay 0.30 not 0.50.** Steeper decay → less reinforcement at distance 1 (+0.30 instead of +0.50).

Effective reach is wider but thinner. Adjacent pair contribution: +1.29 per stone (vs +1.50 in rank-1). 3-stone line: +4.53 total (vs +5.00 in rank-1).

**Win (threshold-race > 38.959).** **31% higher than rank-1's 29.71.** Combined with the lower per-stone reinforcement, this requires significantly more stones to win. Avg game length 54.2 moves vs rank-1's 38.8 confirms this.

**Degeneracy check.** No soft violations. The rule blob has stayed unchanged through 8 generations — evolutionary signal that this exact parameter set is a stable local optimum.

---

## Phase 2 — Strategic Play

### Game 1 — Adjacency cluster (analogue to menger rank-1 game 1b)

Sequence: `0,728,1,727,9,719,81,647` (8 plies, partial).

Plot:
- P1 builds 4-stone "plus" at origin: (0,0,0), (1,0,0), (0,1,0), (0,0,1).
- P2 mirrors at far corner.
- Move 8: P1 = +5.07 with 4 stones (vs rank-1's +7.0). **Per-stone contribution lower** because of the steeper decay kernel — adjacent cells reinforce only +0.30 instead of +0.50.

Reflection: **Same cluster strategy as rank-1, weaker per-stone contribution.** Compensating with distance-2 reach (+0.09) helps for larger clusters but doesn't close the gap for small clusters.

### Game 2 — Sandwich attack on 3D corner

Sequence: `0,1,9,81` (4 plies).

Plot:
- Same as menger rank-1 Game 2: P2 places (1,0,0), then (0,0,1), capturing (0,0,0).
- After 4 moves: P1 = +1.69, P2 = +1.49. P1 still slightly ahead due to residual board_values from (0,0,0) still in play.

Reflection: **Sandwich attack works identically to rank-1.** Outnumber-2 mechanics don't change between ranks. Same balance asymmetry: mirror = P1 win, sandwich = P2 counter.

### Game 3 — Long-game cluster expansion

(Sketched analytically, not played out.)

Threshold 38.96 / per-stone gain ≈ 1.5 → ~26 stones per side needed. With C2 averaged avg game length 54.2 moves, both sides place ~27 stones. **Game ends just as players reach threshold capacity.** This is a "tight" threshold — a small mistake (1-2 captures lost) plausibly puts you below the win line.

Strategic implication: long games favour the side that maintains capture-resistant cluster geometry (interior cells with 5-6 neighbours) over committed-but-vulnerable cluster shapes.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same two as rank-1 (cluster + race; sandwich + counter), with one addition: **long-horizon cluster maintenance**. Because the game lasts ~54 moves and threshold requires ~26 stones, the player who maintains intact clusters (no captures lost) over the full length wins. This adds a "preservation" strategic axis that rank-1's shorter games don't emphasise.

**Counter-play.** Same family as rank-1.

**Short-term vs long-term.** **Materially longer than rank-1.** ~26-30 ply horizon to threshold instead of ~15-20. Tactical decisions (4-6 ply) matter less individually because the long horizon dilutes single-move impact.

**Emergent concepts observed.**
- Same cluster + sandwich primitives as rank-1.
- **Cluster preservation across 50+ moves.** Players must defend their existing cluster shape from late-game opportunistic sandwiches that wouldn't be worth the move-cost in a shorter game.
- **Steep-decay influence routing.** Holes are even more punishing than rank-1 because the +0.09 dist-2 reach is small relative to +0.30 dist-1; one hole between stones loses ~3.3× more relative value than rank-1.

**Does the menger substrate matter?** Same conclusion as rank-1.

**Does the propagation kernel matter?** **More than rank-1.** The combination of r=2 (long reach) with steep decay (0.30) creates a "spotlight" influence pattern: strong at center, weak at edges. This is structurally different from rank-1's r=1 sharp-cutoff kernel and changes which cluster shapes are optimal.

**Capture-rule contribution.** Same as rank-1, but captures matter more because each stone is worth slightly less and the threshold is harder to reach.

**First-mover advantage / seat balance.** Same structural P1 favour. **PPO trained-vs-random WR is 1.000 across all 3 seeds** — better than rank-1's 1.000 (tied) and significantly better than carpet rank-2's 0.707. This game trains cleanly even with the longer horizon.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Largely the same as menger rank-1: influence + outnumber + threshold-race on a 3D fractal. Differences:

(a) **Steep-decay r=2 kernel** is uncommon in published games. Most influence-based games (Tumbleweed, Sygo) use either r=1 or r=2 with shallow decay. The steep decay creates a distinct "concentrated-influence" feel.

(b) **Higher threshold + longer game** shifts the design toward strategic preservation rather than tactical opportunism. This is closer in spirit to Go's late-game endgame than to Othello's swingy mid-game.

(c) Rest of the analysis is the same as menger rank-1.

**Closest known-game analogue:** **Influence-based 3D Tafl on a Menger sponge with concentrated-decay kernel.** Within the project corpus, closest is menger rank-1 — same structural family with longer-game variant.

**Comparison to R8's Connection Go (8/10 ceiling).** Same as rank-1 but slightly more interesting because the long-horizon preservation game has more in common with R8's late-game positional play than rank-1's tactical race.

**Player rebuttal.** Same as rank-1, plus: the long-horizon preservation aspect is a real differentiator from any of carpet rank-1, carpet rank-2, or menger rank-1. This game has the broadest strategic surface of the four mentioned.

**Novelty score (post-adversary):** **6/10.** Same as menger rank-1 (substrate-driven novelty dominates). Marginal +0.5 for the long-horizon design that's distinct from the other R19 games, but I'd round to 6.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** 98739cb0838a
**Rules Summary:** Place stones on a 9³ menger sponge to accumulate influence (radius-2, steep decay) on cells you own. Captures fire when an enemy stone has ≥2 friendly neighbours. First to >38.96 effective influence wins — typically takes ~54 moves total, ~27 stones per player.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 6** — Same depth as menger rank-1 (6) plus the long-horizon preservation axis. Tactical depth slightly lower per-move because each move matters less; positional depth higher because the long arc allows more meaningful build-up.
- **Emergent Complexity: 5** — Same primitives as rank-1; the long-horizon variant doesn't create new emergent vocabulary.
- **Balance: 4** — Same knowledge-asymmetric issue. PPO trains cleanly, suggesting balance is achievable through learned counter-play.
- **Novelty (post-adversary): 6** — Same as rank-1.
- **Replayability: 5** — More moves per game = more position variety, slightly above rank-1's 5.
- **Overall "Would I play this again?": 5** — Roughly same as rank-1. The longer horizon makes individual games richer but doesn't change the strategic ceiling.

### CLOSEST KNOWN-GAME ANALOG
Same as menger rank-1: **Influence-based 3D Tafl on a Menger sponge.** Within R19, this game is the long-horizon variant of rank-1.

### KILLER FLAWS
- Same as menger rank-1 (mirror = P1 win, knowledge-asymmetric balance, cluster geometry constraints).
- **Long horizon dilutes tactical depth.** Individual moves matter less; ~26+ stones per side per game means single-move tactics rarely tip the result.
- **Direct seed survived 8 generations** — evolution couldn't improve on the parameters. Either this is a strong local optimum (positive read) or evolution lacked the operators to escape it (concerning read).

### BEST QUALITY
**Long-horizon cluster preservation.** Unlike the other 3 R19 games I've evaluated (carpet rank-1/2, menger rank-1), this game's threshold + decay combination forces ~50-move strategic arcs. Players must commit to cluster shapes that survive late-game raids. This is the closest R19 game to Go-style positional play.

### MENGER STRUCTURAL CONTRIBUTION
Same as rank-1: substantive (~1 depth + 1 novelty).

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same as all R19 games).

Secondary improvements:
- **Reduce threshold to 30** to compress games to ~35 moves and tighten tactical decisions. Trades positional depth for clarity.
- **Increase decay back to 0.50** (rank-1 value). Would soften the "spotlight" influence pattern and make distance-2 cells more meaningful.
- **Test against a connection secondary win** (R8 family) — adds narrative tension.

### What evolution did or didn't add (vs rank-1)
**Both rank-1 and rank-2 are in the same strategic family with different parameters.** Evolution didn't escape the family — rank-1 is a crossover-refined parameter tweak (r=1, decay=0.5, threshold=29.7) and rank-2 is the unmodified seed (r=2, decay=0.30, threshold=38.96). Human read: rank-1 has slightly tighter tactical engagement; rank-2 has slightly more positional development. **Both score similarly (~5/10 overall).** The evolutionary process didn't find a fundamentally better game on menger — only parameter variants of the same recipe.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-pilot_game98739cb0838a.md`.*
