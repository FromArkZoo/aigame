# Genesis Engine — Plain English Summary

This project is an experiment: can a computer **invent a genuinely new board game** by evolving thousands of candidate games, training AI to play each one, and automatically scoring them?

Every run tries something different and teaches us something new. Here is what we have learned across 8 runs.

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

## Run 14 — Simultaneous play (just completed)

**Goal**: Fundamentally solve the first-mover advantage by adding a new turn type where **both players submit moves at the same time** and resolve together. If they pick the same cell, both stones vanish (mutual annihilation). Also fix the Manhattan distance bug from Run 13.

**What happened**: Simultaneous play was enabled and worked mechanically — games generated, trained, and scored correctly. But the mechanic didn't break through to champion status. Only 2 of top 20 were simultaneous games. The champion was a classical alternating game — torus + custodian capture + threshold win — at 0.517 (not quite beating Run 13's 0.521).

**A surprising signal**: the best simultaneous game (rank 5) was a **CA + simultaneous hybrid** at 0.420. The combination of "both players act at once + Conway-style stone dynamics" may be the unexplored frontier rather than either mechanism alone.

**What we learned**:
- Adding a new mechanic doesn't automatically beat mature mechanics. Simultaneous play needs its own evolutionary pressure to mature.
- Torus topology came back into contention — possibly because the Manhattan distance fix made influence propagation work correctly there.
- The best mechanics may combine (simultaneous + CA).

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

**Best game ever produced**: Still Run 8's "Connection Go" (8/10). No run has surpassed it.

**Most novel mechanic discovered**: Run 10's emergent ko-fights from overwrite + outnumber capture.

**Most promising unexplored combination**: Simultaneous play + cellular automata (first signal in Run 14, not yet explored deeply).

**Open technical problems**:
- The Go Essence metric systematically under-weights game balance
- The double-pass-ends-game rule lets players end many games without meeting the actual win condition
- First-mover advantage persists in all alternating placement games — simultaneous play was one attempt at solving this but the mechanic needs dedicated tuning

**Next frontier**: Probably Run 15 with heavy focus on simultaneous + CA hybrids, and a fix for the double-pass exploit.
