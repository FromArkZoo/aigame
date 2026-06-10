# Genesis Engine — Plain English Summary

This project is an experiment: can a computer **invent a genuinely new board game** by evolving thousands of candidate games, training AI to play each one, and automatically scoring them?

Every run tries something different and teaches us something new. Here is what we have learned across the project's full arc: fifteen evolution runs (7–21), an anchor recalibration, and the two pre-registered probes that followed the pivot.

---

## Run 7 — The baseline run

**Goal**: Test the first version of the system. Produce a random soup of games, train AI on them, see what survives.

**What happened**: Produced a 3D cube board game where you capture opponent stones by surrounding them. A human panel of 5 evaluation teams scored it 8/10 — surprisingly good for a first attempt. Most of the other top games were broken in subtle ways (e.g., one where 3 pieces in a row instantly win).

**What we learned**: The system works end-to-end. But the scoring was suspicious — most games showed zero "non-triviality" (the AI couldn't actually learn them), which turned out to be a bug.

---

## Run 8 — The breakthrough

**Goal**: Fix the scoring bug and add a critical training trick called "seat swapping" (making the AI play both sides during evaluation, so first-mover advantage doesn't fool the scoring).

**What happened**: The seat-swap fix alone boosted scores from ~0.005 to ~0.50 — a massive jump. Champion was "Connection Go", an 8×8 hex board where you capture surrounded stones and win by connecting two sides. Human panel: 8/10, publishable quality.

**What we learned**: Small infrastructure fixes can unlock huge improvements. Also, never use hard-zero penalties in the fitness function — they kill the evolutionary signal. Use smooth ramps instead.

---

## Run 9 — Going bigger

**Goal**: Larger population (50 games/generation instead of 20), more generations, see if quantity produces quality.

**What happened**: All top 20 games were variants of the same basic archetype: "Go on hex". The evolutionary search got stuck in a local optimum. Champion scored 7/10 (down from Run 8's 8/10). Also discovered that the "majority win" condition is always broken — it encourages both players to just pass and count stones.

**What we learned**: More search doesn't help if the mechanic vocabulary is too narrow. We needed genuinely new building blocks.

---

## Run 10 — New topologies and movement

**Goal**: Add richer board structures (hex, torus, Moore/8-connected) and let pieces move, not just get placed.

**What happened**: A genuine novel discovery — "ko fights" (capture/recapture cycles) emerged from combining overwrite placement with outnumber capture. This mechanic is **not found in any traditional board game**. Champion: hex outnumber territory, 7/10. Also learned that torus + connection is fundamentally broken (wrapping makes connecting sides trivial).

**What we learned**: Adding even modest new building blocks unlocks genuinely novel mechanics. The evolutionary search *can* discover real innovation, given the right substrate.

---

## Run 11 — First attempt at cellular automata

**Goal**: Add cellular automata rules — Conway's-Life-style mechanisms where stones live/die/multiply based on their neighbors. This should produce games fundamentally different from all traditional board games.

**What happened**: **Disaster**. Zero CA games made the top 20. Best CA score was 0.07; best classic was 0.5. CA games were being generated but were quickly eliminated by selection pressure.

**What we learned**: We could see the problem but not yet the fix. CA games had short average game lengths (4-10 moves), agents couldn't learn them, and their complexity scores were terrible.

---

## Run 12 — Diagnose why CA fails

**Goal**: Force the run to 2D only (CA seemed to struggle in 3D) and carefully measure what's wrong with CA games.

**What happened**: Still 0 CA games in top 20, but we now had data. The specific problems turned out to be:
1. CA rules gave agents nothing to learn (69% scored "zero non-triviality")
2. The 8-neighbor "Moore" topology created 243-entry transition tables that were impossibly complex
3. The rule-generator was too conservative, producing rules that barely did anything
4. A subtle bug in the stability check was rejecting valid CA rules

**What we learned**: This was diagnostic gold. We knew exactly how to fix CA generation — the fixes just hadn't been applied yet.

---

## Run 13 — CA games finally work

**Goal**: Apply all the fixes from Run 12's diagnosis — restrict CA to low-connectivity topologies, bias mutation toward keeping rules simple, give CA games a complexity discount, fix the stability check.

**What happened**: **CA games competed for the first time in the project**. 9 of top 20 games were CA. Champion `06bab8a32425` was a CA game at 0.52 (a high score by project standards). Then we did the most rigorous human evaluation yet — 22 teams across the top 3 games, each with a mandatory "Novelty Adversary" who had to argue the game was just another Hex variant in disguise.

**The humans overruled the metric**. The CA champion scored only 5/10 (P1 first-move advantage was brutal, and 136 of its 147 CA rules never fired). The real winner was the rank-3 game `531634cee158` — a hex outnumber-capture territory game — which scored 5.9/10 with unusually high agreement between teams.

**Bonus discovery**: One team found a bug in the distance function — it was using Manhattan distance on all topologies, meaning influence propagation had been subtly broken on hex/Moore/torus for every run since V3.

**What we learned**:
1. Metrics lie. Human evaluation is essential.
2. The CA substrate works — but producing a *strong* CA game needs more than producing *any* CA game.
3. The project has a chronic problem: first-mover advantage without a pie/swap rule. Every good game has been slightly broken this way.

---

## Run 14 — Simultaneous play

**Goal**: Fundamentally solve the first-mover advantage by adding a new turn type where **both players submit moves at the same time** and resolve together. If they pick the same cell, both stones vanish (mutual annihilation). Also fix the Manhattan distance bug from Run 13.

**What happened (metric-only readings)**: Simultaneous play was enabled and worked mechanically. The GE champion was a classical alternating game — torus + custodian capture + threshold win (`deb4dfe0382d`) at GE 0.517 — with a simultaneous+CA hybrid (`992bf7dfc9f4`) appearing at rank 5.

**What happened (after the 24-team human evaluation, 2026-04-22)**:

- **No game beat R8's Connection Go (8/10)**. Tier-1 human scores: champion 4.57, rank 2 3.40, rank 3 3.40, sim×CA 2.86.
- The champion has one genuinely novel mechanic: **"capture-as-poison"** — custodian-captured cells retain their pre-capture influence values, so capturing an enemy cell with negative stored value hurts the captor's threshold sum. Most games reward aggression; this one punishes it.
- **The sim×CA signal was a bug**. 7 independent teams converged on an engine defect in `engine_v2.py:252-254`: the CA loop with `steps_per_turn=1` only ever runs from P1's perspective, never alternating. P1 got all births and conversions; P2 got none. Teams also identified a secondary issue — the CA rule-table generator produces tables that aren't symmetric under player swap.
- Double-pass majority exploit (R13 failure mode) fired in ~30% of sim×CA games. Champion and rank-3 games did NOT see it — threshold reachable there.

**What we learned**:
- Simultaneous play, *as implemented*, does not eliminate first-mover advantage — and in combination with CA it actively creates new asymmetry via the step-loop bug.
- Before concluding "simultaneous didn't work" or "sim×CA is promising", you need the engine to be bias-free. Neither conclusion from metric-only reading of R14 is trustworthy.
- The project's strongest output of R14 is the diagnostic finding, not the game. Fixing the step-loop and rule-table symmetry unlocks meaningful sim×CA evaluation in R15.
- GE continues to reward asymmetry-disguised-as-non-triviality. The sim×CA game has non_triv 0.89 and Balance 1.7 — a clear signal for the planned balance sub-metric.

---

## What 8 Runs of Work Tells Us

1. **The evolutionary engine works**. It has produced genuinely novel emergent mechanics (Run 10's ko fights) and, with appropriate tuning, made new rule families viable (Run 13's CA games).

2. **The fitness metric (Go Essence) is useful but imperfect**. Human evaluation consistently disagrees with it on close calls. The metric loves strategic complexity; humans also want balance and strategic *clarity*.

3. **Most games the engine produces are shallow**. Of 500 games per run, maybe 10 score above 0.4 on the metric. Of those, maybe 1-2 score above 6/10 in human evaluation. Finding *one* genuinely good game per run is a success.

4. **Infrastructure fixes outweigh algorithmic cleverness**. The biggest score jumps in the project came from:
   - Seat-swapping during evaluation (Run 8: +0.5)
   - Fixing the CA stability check perspective (Run 13)
   - The pending effect of the Manhattan distance bug fix (Run 14+)

5. **The Go-on-hex attractor is persistent**. Many runs converge to variants of this. The best way to escape it has been adding *orthogonal* mechanics — CA (Run 13), simultaneous play (Run 14). Whether that escape is complete is still an open question.

---

## Where We Stand Today

## Run 15 — Engine fixes + simultaneous×CA + seat-balance metric

**Goal**: Ship five changes in response to R14 findings: (1) CA step-loop symmetry, (2) CA rule-table symmetry, (3) double-pass → draw, (4) seat-balance metric using random-vs-random heuristic probe, (5) sim×CA co-occurrence bias. Seed with R14 and R13 human winners.

**What happened (metric-only)**: 500 games, 11 generations, ~22h run. GE champion `1565501cfecf` at 0.318 — simultaneous torus threshold (no CA). Sim×CA did not break through; only 2 of top 20 were sim+CA.

**What happened (22-team human evaluation)**:
- Champion scored **2.43/10** — the worst champion-human-rating any run has produced. GE ranking fully inverted: the GE champion is 3rd by human verdict. Rank-2 grid game is actually best human game at 3.40.
- Sim×CA candidate scored 1.80/10 (lowest in eval). **Sim×CA premise is dead** — with R14 engine bugs fixed, the mechanic adds no value.
- **Three new engine issues surfaced**: `_check_threshold` iteration-order bias (P1 wins all same-tick crossings regardless of margin), `_check_connection` iteration-order bias (same pattern), CA step-ordering bias (P1 step runs before P2 per tick).
- **Two known issues the generator failed to filter**: torus+connection = 2-move wrap-win (regression of R10 bug), Moore+surround = dead capture (same as R13/R14).
- **The new seat-balance metric has a skilled-play blindspot**: random-vs-random probe misses bias that only surfaces under competent play (e.g., rank-3 Moore was 13/16/1 in random but 20/20 P1 under greedy).

**What we learned**:
- Engineering changes worked at the micro level (all symmetry tests pass) but fitness engineering alone doesn't catch all engine bias. The check-order bugs are invisible to the metric.
- Fully inverted GE→human ranking is a worse outcome than R14's compressed-but-correct ranking. The metric needs another pass.
- The sim×CA "signal" from R14 was entirely the step-loop bug. With the bug fixed AND rule-table symmetry enforced, sim×CA has nothing to offer beyond pure sim or pure CA.
- **Bug-finding is the main output of runs 13-15**. 9 distinct engine/generator issues found via human evaluation across three runs, none catchable by GE alone.

---

## Run 16 — Engine fixes for the R15 bugs + greedy seat-balance probe

**Goal**: Ship six fixes after R15's three new engine bugs: (1) margin-based threshold/connection resolution, (2) CA step from shared snapshot, (3) generator quick-reject torus+connection, (4) generator downgrade moore→grid for surround capture, (5) greedy-vs-greedy seat-balance probe + worst-of-three metric, (6) ca_probability 0.3 → 0.2.

**What happened (metric)**: 500 games, 11 generations, ~20h. GE champion `8d12c8b92b71` at 0.160 — hex alternating no-capture threshold. Sim×CA games scored near zero across the whole population (top sim+CA at GE 0.0026, non-triv 0.00). Sim games dropped to 23% of population (R15: 33%) as evolution selected against them.

**What happened (22-team human evaluation, 2026-04-25)**:
- **R16 human winner is `c6bb58075520`** (torus + alt + outnumber + influence + threshold) at **mean 4.40/10**. GE rank 3, human rank 1. Highest non-R8 score in three runs.
- GE champion `8d12c8b92b71` was 2nd by humans at 3.57. GE inverted at the top again.
- Sim moore game (GE rank 2) scored 2.60 but Balance 8-9/10 — proof the R16 fixes deliver real seat balance for sim play. Just shallow.
- Moore+surround game (GE rank 5) scored 2.60 — capture rule still dead. My downgrade fix has a hole: `_fix_consistency` doesn't apply the same rule, so mutation can produce moore+surround games.
- **Three new engine issues found**: FP-ordering bias in `step_simultaneous`, `_fix_consistency` skipping the moore+surround downgrade, threshold parity bias (thresholds tend to land where P1 crosses first by tempo).

**What we learned**:
- Engine fixes verifiably worked: margin-based threshold delivers Balance 8-9/10 for sim games (R15 was 1.7). CA-from-snapshot kills sim+CA inflation. Torus+connection generator filter prevents 2-move wrap-wins.
- **The 0.2 seat-balance floor in scoring caps how much imbalance can hurt the composite** — the alt-threshold champion has Balance 2-3 from humans but retained GE rank 1.
- **Strongest design family across R13-R16**: classical alternating + active capture (custodian or outnumber) + radius-1-or-2 signed influence + threshold win on non-Moore topology. R16 winner is squarely in this family.
- Sim×CA is **conclusively dead**. R14/R15 "signal" was bug-driven.
- Pure simultaneous play is balanced post-fix but mechanically thin.

---

## Run 17 — The clean-engineering run

**Goal**: After three runs whose main output was bug discovery, run one with the engineering debt actually paid: a soft-rule audit, a hard-zero on seat balance, and the first seeding of a fractal board.

**What happened**: The first run where the games that came out were not secretly broken — regressed games stayed regressed, and the champion scored 4.14/10. The experimental fractal-substrate seed collapsed under PPO training (the agents simply couldn't learn on it as seeded).

**What we learned**: Clean engineering doesn't buy depth by itself. With the bugs gone, what's left is the honest signal — and the honest signal said the games were mediocre. (A note on wording: from here on the panels are called what they are — **agent-team evaluations**. Teams of Claude agents play the games head-to-head, write strategy guides, and score them. Earlier write-ups said "human panel"; nothing about the process changed, only the honesty of the label.)

---

## Run 18 — Boards with fractional dimension

**Goal**: Hold the rules fixed and make the *board itself* the search axis — six substrates spanning Hausdorff dimension 1.465 (vicsek) to 2.727 (menger sponge).

**What happened**: Menger — the most dimensionally rich board — lifted above every flat-grid champion on peak Go Essence. But the run also exposed a nasty measurement artifact: per-generation peak scores dropped 50–80% when champions were re-trained, because PPO seeds had been generation-indexed. Much of what looked like evolution was lucky seeds.

**What we learned**: Board dimensionality is a real lever — and the scoring pipeline was measuring luck alongside skill. Deterministic, multi-seed scoring became mandatory.

---

## Run 19 — The first honest end-to-end run

**Goal**: Champion run on menger + carpet under the new discipline: deterministic per-game seeds, multi-seed-averaged scoring, and a ban on degenerate hybrid actions.

**What happened**: Carpet hit GE 0.355 (above the plan's goal); menger 0.329, inside the noise band of R18 — so the R18 lift survived honest re-measurement. The smoke-test gate turned out to be over-aggressive, rejecting five menger seeds that evolution then independently rediscovered. Agent-team evaluation (30 verdicts): production mean **4.375/10**, the strongest campaign since R8.

**What we learned**: The honest pipeline works, and 4.375 became the number to beat. The postmortem produced a two-tier smoke gate for future runs.

---

## Run 20 — A depth record, and the anchor wobbles

**Goal**: Three-substrate comparison with the pie rule (the "I cut, you choose" fairness mechanism) plus an attempt to revive Run 8's connection-game family from seed.

**What happened**: One menger game hit **0.894 strategic depth** — the deepest single game the project has ever measured (prior max ~0.55). But the R8 revival failed completely: every connection-win seed mutated into a threshold-race within five generations — evolution under GE actively walks *away* from the family that produced the best game. Honest 15-seed re-scoring also destabilized the leaderboard (the nominal champion fell to 7th of 9), and a crossover bug silently zeroed the pie rule on most descendants. Agent-team evaluation: 35 verdicts, campaign mean 3.73 — below R19.

**What we learned**: Depth exists in the search space, but the selection signal doesn't retain it. And the suspicion that something was wrong with the *anchor itself* demanded a check.

---

## The Run 8 replay — recalibrating the legend

**Goal**: Re-evaluate "Connection Go" — the 8/10 champion every run had failed to beat — under the modern rubric, with five fresh teams.

**What happened**: **4.10 ± 1.14 out of 10.** Mid-corpus, not above it. The February 8/10 had been inflated by roughly 3.9 points of rubric drift between scoring eras.

**What we learned**: The project had spent months chasing a ceiling that was partly a measurement artifact. The real question changed from "why can't we beat R8?" to "what does the corpus look like once the anchor is honest?" (A small follow-up, R20.5, fixed the pie crossover bug and established the seat-swap mirror-evaluation method that every later experiment reuses.)

---

## Run 21 — The verdict on the whole regime

**Goal**: One more champion run under the full modern stack, with an elite re-evaluation gate, to decide whether GE-driven evolution had anything left.

**What happened**: Top menger 0.177 — tied with R20 within noise; four runs with no ceiling progress. The elite re-evaluation caught a phantom champion (0.417 collapsing to 0.095 on honest re-scoring). The agent-team campaign (5 independent teams, 35 verdicts) was decisive: **no game cleared 5.0**, campaign mean 3.69, below R19 and below the recalibrated R8. Worse, GE now ranked *backwards* at the extremes — the GE-top game placed 6th of 7 with the agents, while a connection game GE had ranked dead last (0.002) tied for 1st on design. The evaluators' diagnosis: threshold-race win conditions never force the players to interact, so games become parallel packing races. A follow-up variance probe cleared PPO of blame — the noise lives in GE's own coarse estimators.

**What we learned**: The pre-committed decision rule fired: **PIVOT + SATURATION**. Two consecutive sub-5.0 campaigns, a metric anti-correlated with what it's supposed to find. Stop evolving against GE. Start testing rule ideas directly.

---

## The Field-Connect probe — the first pre-registered experiment

**Goal**: Test the smallest decisive version of the pivot's rule idea: make influence *be* the win condition — you win by connecting your two sides through cells your influence field controls — and judge it blind against a plateau baseline, with go/no-go bars locked before any data.

**What happened**: Formally a NO-GO — the mechanical screen and the blind margin (+0.70, needed +1.0) both missed their bars. But the substance was the strongest signal since Run 8: **both blind teams preferred the new game (4.15 vs 3.45)** — first build, R8-parity — and both independently named the same reason, the win condition that "means you can never ignore the opponent." The failures were specific: the influence radius blurred tactics, and the Go-style capture rule never fired once (structurally impossible on an open hex board).

**What we learned**: The lever is real; the parameterization was wrong. Total cost: about a day of build and under two hours of compute — the pre-registration discipline (calibrate → screen → blind, sealed labels, locked bars) earned its keep immediately.

---

## Phase-1.5 — the rules rethink refutes its own premise

**Goal**: Rebuild Field-Connect's rules per the probe's critique: sharpen the field (radius 1, a real contested-state margin) and replace the dead capture with mechanics anchored in published games — flip-capture (Sygo), a control-gated placement rule, and control-based replacement (Tumbleweed). Three candidates, same locked gates.

**What happened**: NO-GO at the mechanical screen — and the experiment overturned the critique it was built on. The gate candidate died in calibration (60%+ draws; self-play just stalls). The other two cleared calibration but won 1 of 4 screen signals each, with PPO training collapses. The decisive row was the *reference*: the original radius-2 game, retrained bit-identically, dominated every signal — including 2.5× the "field dynamics" the sharper field was supposed to restore. **Radius-2 overlap is what makes territory contestable; "sharpening" the field froze it.** Meanwhile the flip-capture mechanic itself worked exactly as designed: 7.1 capture events per game where the old rule managed zero.

**What we learned**: The blind evaluators' top critique, implemented faithfully, made the game worse — which is precisely why the bars get locked before the data arrives. The mechanic survived; the field it stood on didn't. (Engineering by-product: a kernel-cache rewrite made field games ~100–500× faster to simulate, with a bit-identity proof — every future run benefits.)

---

# Where things stand

**Best game by honest measurement**: the Field-Connect probe game at **4.15/10 blind** — statistically at parity with the recalibrated Run 8 anchor (4.10), achieved by one day of design rather than a month of evolution.

**Most important confirmed finding**: games go deep when the win condition **forces interaction**. The plateau's packing-race games and the probe's blind verdicts point at the same mechanism from opposite directions.

**Most novel mechanic discovered**: still Run 10's emergent ko-fights; new runner-up: field-flip capture — Go-like capture arithmetic emerging from pure influence fields, no liberty rules — which works mechanically but hasn't yet been tested on the field geometry where it could shine.

**The sharply-posed open question**: flip-capture on the radius-2 field — both halves individually validated, never tested together. Running it would be a deliberate exception to the registered next step.

**The registered next step**: leave the Field-Connect family; either a different win-condition family, or Quality-Diversity (MAP-Elites) selection to replace Go Essence — which Run 21 showed anti-correlating with agent-judged depth — as the thing evolution optimizes.

**Open technical problems**:
- Agents are flat MLPs — no spatial inductive bias, which caps measurable depth on large boards and likely contributed to the phase-1.5 training collapses
- Agent-team evaluation remains the rate limiter (30–60 minutes per game; only top candidates get scored)
- The influence-kernel cache is unbounded and needs a memory cap before any evolution-scale run
