# Genesis Creativity Engine Run 16 — Human Evaluation

**Team ID:** team-10
**Game ID:** f8dbeb3079a5
**Generation:** 8 (R16 GE rank 2)
**Created:** 2026-04-25

---

## PHASE 1 — Rule Comprehension

### Board structure
- 2-D, 8 × 8 = 64 cells, plus action ID 64 = PASS.
- Topology: **Moore** (Chebyshev / king-move adjacency, 8 neighbours interior, hard-bounded — no torus wrap). The display in `sim_play_helper.py` mislabels it as "torus" but `topology.py` confirms moore is hard-bounded.
- Action coords: action ID `a = y * 8 + x`.

### Turn structure — SIMULTANEOUS
- Both players submit a placement on the same tick, resolved by `engine.step_simultaneous()`.
- **Collision rule:** if both pick the same non-pass cell, **mutual annihilation** — neither stone is placed and the cell stays empty. Both players still consume their move.
- Double-pass ends the game as a draw.
- Same-tick threshold crossings: **R16 margin rule** — whoever's effective value sits further above the threshold wins; equal margins → draw.

### Action types
- Place only. No movement, no capture.
- Placement constraint: target must be empty; otherwise unrestricted (`anywhere`).
- 64 placement actions + 1 pass = 65 actions.

### Capture / CA
- Capture rule: `none` (inert).
- No cellular automaton (`uses_ca = False`).

### Propagation — `influence`, radius 1
- `strength = 1.03875`, `decay = 0.37123`.
- A placed P1 stone at cell *c* adds `+s = +1.0387` to `board_values[c]` and `+s·d = +0.3855` to each cell within Chebyshev distance 1. P2 contributes the same magnitudes with negative sign.
- `board_values` is clamped to ±100 (irrelevant at the magnitudes seen here).

### Win condition — threshold
- `condition_type = threshold`, `threshold = 30.7513`, `target_dimension = 0`, `max_turns = 100`.
- "Effective value" = signed sum of `board_values[c]` over cells owned by that player, sign-corrected so both players want a *positive* total. Cross 30.7513 → win. Both cross same tick → margin tiebreak.

### Degeneracy / quirks
- **No piece can ever be removed** (no capture, no CA). The board only fills.
- A stone's own contribution to its own cell is `+s = +1.0387`. So 30 isolated stones already give `30 × 1.0387 = 31.16`, just above threshold — but the game runs out of turns far before that matters because clustering compounds quickly.
- **Symmetric play deterministically draws.** With `step_simultaneous` and a propagation that is linear and additive, two perfectly-mirrored cluster placements produce identical effective totals at every tick. The R16 margin rule resolves this as a draw, except when floating-point round-off creates a sub-1e-14 difference and the engine gives it to whichever side is computed first. This is a real engine artifact (see Phase 2 Game 1).
- **Aggressive interference is dominated.** Placing inside opponent's neighbourhood costs the attacker more (own piece loses several `−0.386` adjacency hits) than the defender (one or two `−0.386` hits). The Nash strategy is "build a tight cluster as far from the opponent as you can".
- **Finite cell budget vs. threshold.** A 3×4 rectangle (12 stones) gives `≈ 34.86` in isolation — comfortably over 30.75. Both players reach in 12 of the 100 allowed rounds.

---

## PHASE 2 — Strategic Play

### Pre-game arithmetic (used by both seats)

For an isolated rectangular cluster on Moore, per-piece contribution to own_sum:
- corner (3 in-cluster nbrs): `1.039 + 3·0.386 = 2.197`
- edge (5 in-cluster nbrs): `1.039 + 5·0.386 = 2.969`
- interior (8 in-cluster nbrs): `1.039 + 8·0.386 = 4.127`

Totals for candidate shapes:
- 3×4 = 4 corners + 6 edges + 2 interior → **34.86** (12 stones)
- 2×6 strip = 4 corners + 8 edges → **32.54** (12 stones)
- 1×12 strip = 2 endpoints + 10 interior → **22.96** (12 stones, doesn't cross)
- 4×4 = 4 + 8 + 4 → **49.05** (16 stones, overkill)

Implication: 3×4 is the best 12-stone shape. Strip and line are strictly inferior. The threshold is reached at round 11 if the 11 cells form a "3×4 minus one corner" (sum = 31.48), or round 12 for full 3×4.

### Game 1 — Both play optimally but in opposite corners (independent reasoning)

**Player 1 reasoning (sealed before P2 plan).** Build a 3×4 cluster in the NW corner. Order: place high-connectivity centres first so threshold is reached as early as possible; save corner cells for the last placements. Predict P2 will mirror; assume mutual SE cluster; do **not** invade P2's space (interference is dominated).

**Player 2 reasoning (sealed before P1 plan).** Mirror — build a 3×4 cluster in SE. Same ordering rationale. Same prediction of P1.

**Pre-commit move-by-move (engine-verified):**

| R | P1 move | P2 move | P1 sum | P2 sum | Notes |
|---|---|---|---|---|---|
| 1 | 18 (2,2) | 45 (5,5) | +1.04 | +1.04 | both centres |
| 2 | 9 (1,1)  | 54 (6,6) | +2.85 | +2.85 | diag expand |
| 3 | 10 (2,1) | 53 (5,6) | +5.43 | +5.43 | |
| 4 | 17 (1,2) | 46 (6,5) | +8.78 | +8.78 | |
| 5 | 0 (0,0)  | 63 (7,7) | +10.59 | +10.59 | corner |
| 6 | 27 (3,3) | 36 (4,4) | +12.02 | +12.02 | inner corners — adjacent across cluster boundary |
| 7 | 26 (2,3) | 37 (5,4) | +15.37 | +15.37 | |
| 8 | 19 (3,2) | 44 (4,5) | +19.49 | +19.49 | |
| 9 | 8 (0,1)  | 55 (7,6) | +22.85 | +22.85 | |
| 10 | 1 (1,0) | 62 (6,7) | +26.97 | +26.97 | |
| 11 | 16 (0,2) | 47 (7,5) | +30.32 | +30.32 | both still under threshold |
| 12 | 2 (2,0) | 61 (5,7) | +33.67 | +33.67 | both cross simultaneously |

Both effective values are **identical** to fifteen decimals (`31.4781545531...` if you stop at R11 with corner-last; `33.6741...` at R12 with this ordering). The R16 margin rule reports a draw (`winner=None`).

> **Engine-quirk note:** when the same set-up is played with cells visited in a different order, e.g. `9,10,17,18,1,2,11,8,16,19,3,0` for P1 vs `54,53,46,45,62,61,52,55,47,44,60,63` for P2, both sides cross at **R11** at exactly the same effective value — but FP round-off gives P1 a `~3.5·10⁻¹⁵` margin advantage and the engine reports `winner=0` (P1 wins). The R16 margin rule is correct in spec, but it does not resolve genuinely-tied configurations cleanly when those configurations are constructed by perfectly mirrored, finite-precision arithmetic. **This is a real, reproducible engine artefact, not a strategic insight.** I count this as a draw for evaluation purposes.

**P1 reflection.** Strategy executed cleanly. No surprises — opponent built a mirror cluster. Game ended via threshold (not double-pass, not max-turns). Would I do anything differently? I considered placing my 12th stone at (4,3) to disrupt P2's (4,4) — simulated, this *backfired*: P1's gain dropped to +1.81 (vs +3.35 in cluster) while P2 only lost ~0.39. Cluster discipline wins.

**P2 reflection.** Identical. Mirror policy is the dominant response to a clustering opponent on a board this large. Endgame reached the stated win condition (threshold), not a degenerate ending.

### Game 2 — P1 optimal cluster vs P2 inferior 2×6 strip

**P1 reasoning.** Same NW 3×4 cluster, corner-last ordering: `9,10,17,18,1,2,11,8,16,19,3,0`. Threshold should be reached at R11.

**P2 reasoning.** Test whether a 2×6 strip along the south edge is competitive. Maximises board coverage but loses ~2.3 in total per-piece value. Order: tight middle first.

| R | P1 move | P2 move | P1 sum | P2 sum |
|---|---|---|---|---|
| 1 | 9 | 59 (3,7) | 1.04 | 1.04 |
| 2 | 10 | 60 (4,7) | 2.85 | 2.85 |
| 3 | 17 | 51 (3,6) | 5.43 | 5.43 |
| 4 | 18 | 52 (4,6) | 8.78 | 8.78 |
| 5 | 1 | 58 (2,7) | 11.36 | 11.36 |
| 6 | 2 | 61 (5,7) | 14.72 | 13.95 |
| 7 | 11 | 50 (2,6) | 18.07 | 17.30 |
| 8 | 8 | 53 (5,6) | 21.42 | 20.65 |
| 9 | 16 | 57 (1,7) | 24.77 | 23.23 |
| 10 | 19 | 62 (6,7) | 28.13 | 25.81 |
| 11 | 3 | 49 (1,6) | **31.48** | 29.16 |

**P1 wins at R11.** The strip never had a chance: even at 12 stones it tops out at 32.54, and the gap opens once both players move past the 5th piece (when the strip's edges-only structure fails to compound).

**P1 reflection.** Predicted outcome exactly. The "strip" benchmark confirms 3×4 dominance.

**P2 reflection.** Surprised? No. The strip lost predictable amounts each round once the cluster started gaining its second-shell `+0.386` boosts. Lesson learned: shape > coverage. Endgame reached via threshold.

### Game 3 — Seat swap, both optimal, but **adjacent** corners

To pressure-test seat balance and to introduce some real cross-cluster contact, I swapped seats and placed clusters in NW (P1) and NE (P2) — they share the column-3/column-4 boundary. Both play 3×4 corner-last.

| R | P1 move | P2 move | P1 sum | P2 sum |
|---|---|---|---|---|
| 1 | 9 (1,1) | 13 (5,1) | 1.04 | 1.04 |
| 2 | 10 (2,1) | 14 (6,1) | 2.85 | 2.85 |
| 3 | 17 (1,2) | 21 (5,2) | 5.43 | 5.43 |
| 4 | 18 (2,2) | 22 (6,2) | 8.78 | 8.78 |
| 5 | 1 (1,0) | 5 (5,0) | 11.36 | 11.36 |
| 6 | 2 (2,0) | 6 (6,0) | 14.72 | 14.72 |
| 7 | 11 (3,1) | 12 (4,1) | 17.68 | 17.68 |
| 8 | 8 (0,1) | 20 (4,2) | 20.65 | 20.65 |
| 9 | 16 (0,2) | 15 (7,1) | 24.00 | 24.00 |
| 10 | 19 (3,2) | 23 (7,2) | 26.58 | 26.58 |
| 11 | 3 (3,0) | 4 (4,0) | 28.78 | 28.78 |
| 12 | 0 (0,0) | 7 (7,0) | **32.13** | **32.13** |

Both cross at R12 with effectively identical sums. Cross-cluster Moore adjacency between columns 3 and 4 cost both sides ~7 × 0.386 ≈ 2.7 in own_sum, dropping the at-12 total from 34.86 (isolated) to 32.13 (adjacent). The margin tie was perfect (no FP wobble this run) — engine reports `winner=None`, **clean draw**.

**P1 (post-swap) reflection.** Even with seat swap, the strategic outcome is the same: optimal mirror = draw. The mechanic of being "first player" carries no functional weight here.

**P2 (post-swap) reflection.** Same. Adjacent clusters created exactly the symmetric trade I expected — both sides leaked the same amount of value across the boundary.

### Strategy guides

**P1 / P2 (same guide — game is symmetric).**
1. Build a 3×4 cluster in a corner. 4×3 / 3×4 orientation doesn't matter; corner placement maximally protects from edge-cell wastage.
2. Place high-connectivity cells first (the central two, then edges, then corners). Save the *true* corner of your rectangle for last so the threshold is crossed at R11 rather than R12 if your opponent is slow.
3. Stay as far from your opponent as you can. Adjacent clusters cost both sides the same, but a smaller-budget asymmetric trade can punish you.
4. **Do not invade.** Placing a stone next to opponent's cluster gives you `+1.04 − k·0.386` for *k* enemy neighbours (often net-zero or negative own contribution) while your opponent loses only `k·0.386`. The exchange is unprofitable for the attacker.
5. If you sense your opponent is going strip / line / scattered, just keep clustering. You will reach threshold first.
6. Ignore PASS. There is no scenario where passing improves your effective sum (which only grows with placements, capped by clamp +100).

---

## PHASE 3 — Strategic Analysis (joint)

**Distinct viable strategies?** No. The game has a **single dominant strategy** (build dense rectangle in a corner) and every deviation is strictly punished. We confirmed three deviation classes:
- **Strip (2×N)**: under-clusters by ~2.3 in 12-stone total, loses cleanly (Game 2).
- **Linear (1×N)**: loses by ~12, can't even cross threshold in 12 stones.
- **Interference**: dominated; placer's own contribution drops faster than the defender's.

**Counter-play?** None. There is no asymmetric punishment, no resource constraint that flips who wins. The only "decision" both players make is which corner to occupy, and corners are interchangeable.

**Short- vs long-term tension?** Effectively absent. Every move you make inside your own developing cluster has the same compounding logic; the game has *no* choice points where a sacrifice now buys you something later. Even the timing decision ("when to place the corner") is a fixed schedule: corner-last is best, every game.

**Emergent concepts?**
- **Territory** appears in the most diluted possible sense (you want a corner) but there is no contest for it.
- **Influence** is real (the propagation field) but symmetric and additive — no spatial trick exploits it.
- **Tempo / initiative** is zero in simultaneous mode.
- **Mutual annihilation** (the collision rule) literally never fires in optimal play, because optimal play occupies disjoint corners and never targets the same cell.
- **Ko / mutual-annihilation tactics**: the prompt asks about these — under no-capture / no-CA, they don't exist. Collisions would only happen by mistake.

**Topology relevance?** Moore vs grid (4-neighbour) would matter — Moore's diagonal links boost cluster compounding from `1+4d` to `1+8d` per interior cell. But the choice of *moore vs grid* is a one-line rule swap; the topology *type* is essentially decorative because there is no movement, no capture, and no path-based mechanic that would distinguish them strategically. The fact that the generator downgrades moore→grid when surround-capture is on (R16 fix) is moot here — there's no capture rule.

**First-mover advantage / seat-swap evidence.** Genuine simultaneous play **does** eliminate the seat asymmetry in this game's *strategic* layer. Game 1 and Game 3 with full mirror play both produce identical effective sums. The only way "P1" wins under perfect mirror is via floating-point round-off in `_check_threshold`'s sum order — a rounding-noise artefact, not strategy. We saw both `winner=None` (Game 3) and `winner=P1 by 3.5e-15` (Game 1 sweep) on this game, depending on which order the cells were placed.

So the answer is: **simultaneous structurally removes seat advantage in this game**, but the win-condition resolution is so close to a numerical tie under symmetric play that the engine occasionally awards a "win" to whichever side benefited from FP order. The R16 margin fix is the *correct* spec; the underlying issue is that the strategic ceiling is so flat that any tiny numerical perturbation determines outcomes.

---

## PHASE 4 — Novelty Adversary (mandatory)

### Adversary's case ("this is not novel")

(a) **Catalog comparison.**
- *Reversi/Othello*: no — Othello has flips. This has no captures of any kind.
- *Go*: no — no liberties, no capture, no ko (no super-ko triggers because there's no removal mechanic). The "influence" propagation is at most a weak echo of *visualisation* tools used by Go AI (territory potential), not a Go rule.
- *Hex / Y / Havannah / Connect6 / Gomoku / Pente*: no — those are connection / N-in-a-row games. This has no path or line objective; it has a *summed scalar* objective.
- *Amazons / Lines of Action / Chameleon*: no — they are movement games with capture/blocking; this is placement-only no-capture.
- *Mancala*: not relevant — no pit-and-sow.
- *Tumbleweed*: closer cousin — Tumbleweed has line-of-sight influence and threshold-style territorial scoring on hex. But Tumbleweed has explicit attack/capture via line-of-sight stacks, height comparisons, and pie rule. This game has none of those — only additive Moore-radius-1 propagation.
- *Slither*: connection-based with sliding stones. Different objective, different action set.
- *Nim*: no.
- *Blotto*: closest in spirit (allocate finite resources across positions; symmetric pay-offs; simultaneous). But Blotto has no spatial structure and no propagation; here Moore propagation is the whole point.
- *Diplomacy*: no — D has writing-orders + multi-unit + support; nothing like this.
- *Rock-paper-scissors-scaled simultaneous games*: too abstract; doesn't bind to a board.
- *Gungo*: rock-paper-scissors-on-a-board variant — but Gungo's interaction is rock-paper-scissors local outcomes, not summed propagation.
- *Life-like CAs*: irrelevant — `uses_ca = False`.

(b) **CA literature**: doesn't apply — no CA.

(c) **Simultaneous-games literature**: Blotto-like, but with spatial Moore propagation. The combination of (i) simultaneous placement, (ii) collision = mutual annihilation, (iii) influence threshold win is uncommon. **However**, in *practice* the collision and threshold mechanics never fire interestingly: the dominant strategy never collides, and the threshold is essentially a "race-to-12-good-stones" timer rather than a contestable scoring system.

(d) **Re-skin argument.** Strip away the simultaneity and collision rule (which are unused at equilibrium) and you are left with: place stones one at a time on an 8×8 Moore board, each stone adds Gaussian-ish positive "influence" within radius 1, race to a fixed sum. That is essentially **a single-agent piece-counting game with a per-shape weight**. With both agents playing the dominant strategy it reduces to "fill a corner 3×4". The "game" portion is the *choice of which corner*. That is one bit of decision. Maybe two if you count whether to deviate (but you shouldn't).

(e) **Expert transfer.** A Go or Othello player would not transfer skills here — neither pattern recognition nor capture-counting nor liberty management applies. A *Blotto* expert would transfer the "build the most dense region" intuition immediately and become competitive in one game. A *Tumbleweed* expert would over-think the line-of-sight aspects and slightly *under*-perform.

### Rebuttal (Player 1 + Player 2)

We're rebutting *only* the claim that the game is non-novel; we agree it is shallow. The novel ingredients we observed in Phase 2:
- **Margin-tiebreak under simultaneous threshold crossing** (R16 spec) is a clean rule but produces FP-level draws in symmetric play. We saw a `3.5e-15` margin in Game 1 swept-order — that's a novel *engine* phenomenon, not a novel *game* phenomenon.
- **Mutual-annihilation collision** is a mechanic absent from the catalog — but in this game *it never fires* because both rational players occupy disjoint corners. So while structurally novel it has zero strategic surface area here.
- **Moore-propagation threshold race** is the only mechanic that genuinely defines the game, and it is most similar to **Blotto on a spatial graph with local kernel** — which we couldn't find in the catalog with that exact specification, so it earns a small novelty premium. But the strategy collapses to "fill a 3×4 in your corner" regardless of opponent action, so the novelty is pre-decisional, not in-play.

In Phase 2, no game-moment relied on a mechanic absent from the comparison set in a way that *mattered for the result*. The closest "this rule was load-bearing" moment was Game 2 R6, where P2's strip first started lagging — but that was just "less efficient cluster lost" which Blotto already covers.

### Novelty score

**3/10.** The full ruleset (simultaneous + Moore propagation + margin-tiebreak threshold + mutual annihilation) doesn't have a clean prior-art match. But:
- The *played* game collapses to "Blotto on a spatial kernel".
- Three of the four mechanics (collision, simultaneous, margin-tiebreak) are inert in equilibrium play.
- "Score on Moore-radius-1 sum" is just a known kernel applied to placement count.

I budget +1 above the "X on a hex/torus board" floor (2-3) for the genuinely-uncommon combination of mechanics, but not more, because they do not produce *gameplay* novelty — only *rule* novelty.

---

## PHASE 5 — Verdict

**Team ID:** team-10
**Game ID:** f8dbeb3079a5
**Rules Summary:** Simultaneous placement on an 8×8 Moore-adjacent board; each stone contributes Moore-radius-1 additive influence (`s=1.039, d=0.371`) to the player's effective value; first to exceed `30.751` (margin tiebreak) wins. No capture, no CA.
**Topology:** 8×8 Moore (king-move, hard-bounded), 64 cells.
**Turn Structure:** Simultaneous (collision = mutual annihilation; double-pass = draw).

### SCORES (1-10)

| Dimension | Score | Why |
|---|---|---|
| **Strategic Depth** | **2** | Single dominant strategy ("3×4 cluster, corner-last, in your corner"). Verified across three independent games. Deviations (interference, strips, lines) all strictly dominated. |
| **Emergent Complexity** | **2** | No emergent dynamics observed. The only "emergent" property — that simultaneous mirror play ties to FP precision — is a numerical artefact, not a game property. |
| **Balance** | **8 (mechanical) / 5 (effective)** | Seat-swap evidence: Game 1 (NW vs SE) and Game 3 (NW vs NE, seats swapped) both produced numerical ties with the R16 margin rule reporting draw or a sub-`10⁻¹⁴` FP-driven "winner". The mechanic correctly removes structural P1 advantage. But the equilibrium is *too* balanced — mirrored play is a near-deterministic draw, which is a kind of imbalance toward the no-decision outcome. Net: **6**. |
| **Novelty (post-adversary)** | **3** | Combination of margin-tiebreak threshold + Moore propagation + simultaneous-collision is uncommon, but reduces in play to spatial-kernel Blotto. Three of four mechanics never fire in optimal play. |
| **Replayability** | **2** | After learning "build 3×4 in a corner", every game is the same race-to-12-stones with mirror-symmetric outcome. No reason to play a second time. |
| **Overall "Would I play this again?"** | **2** | One playthrough is sufficient to enumerate the entire strategic space. |

### CLOSEST KNOWN-GAME ANALOG
**Spatial Blotto with a Moore-radius-1 kernel.** Differences: standard Blotto has no spatial structure and no collision; this has both — but the spatial structure flatlines into a corner-cluster solution, and the collision rule is never strategically invoked at equilibrium. A weaker analog is **Tumbleweed** (threshold scoring with influence-style propagation on hex), but Tumbleweed's stack/sight mechanics and pie rule produce real decisions absent here.

### KILLER FLAWS
1. **Dominant strategy.** "3×4 in a corner, corner-last" wins or ties every game. No counter-play exists.
2. **Mirror → guaranteed draw modulo FP.** Two competent players draw with probability ~1; the engine's margin rule gives a sub-`10⁻¹⁴` margin to whichever sum is computed first, awarding "wins" via floating-point order. The R16 spec is correct; the *game* is what's broken, in that its strategic surface is too flat.
3. **Inert mechanics.** Simultaneous placement, collision/mutual-annihilation, and margin-tiebreak threshold never fire in equilibrium play. They are scaffolding around a no-decision Blotto allocation.
4. **No tempo / no comeback.** A player who falls behind by one round (i.e. plays one strictly inferior move) cannot recover; the propagation is monotonic and additive.
5. **The threshold magnitude is too tight.** `30.751` requires almost exactly 12 well-clustered stones. There is no slack for tactical detour. A higher threshold would force longer games but not deeper decisions; a lower threshold would make Game 2-style asymmetric wins more frequent but still wouldn't introduce new decisions.

### BEST QUALITY
The **Moore-radius-1 additive propagation** is a clean, predictable mechanism — easy to reason about, scales linearly, and produces analytically-tractable own-sums. It is the only piece of this design that I would consider lifting into a different game.

### IMPROVEMENT IDEAS
**Add a stone-budget per turn and a *negative* propagation from your own stones beyond a threshold.** Concretely: each of your stones contributes `+1.04` to itself but only the first 6 stones in any 3×3 window contribute the `+0.39` neighbour bonus — extra crowding adds `-0.39` instead. This breaks the corner-cluster monoculture by making density costly past a point, forcing players to spread, which then makes the collision rule and adjacency interference *actually relevant*. Equivalently: cap the per-cell board_value at a small positive number after which adding a same-colour neighbour is a waste, so 3×4 stops being optimal and players have to argue about *where* to spread.

A simpler one-line change: set `decay = 0.9`, `radius = 2` so that propagation reaches further. This makes interference profitable (one well-placed enemy stone shaves `0.9 · 1.04 ≈ 0.94` off many of your cells at once) and creates real spatial contest.

---

## Summary table of outcomes

| Game | P1 strategy | P2 strategy | Result | Margin |
|---|---|---|---|---|
| 1 | NW 3×4 (mid-first) | SE 3×4 (mirror) | Draw at R12 (both 33.67) | 0 |
| 2 | NW 3×4 (corner-last) | SE 2×6 strip | **P1 wins R11** | +2.31 |
| 3 (seat-swap) | NW 3×4 (corner-last) | NE 3×4 (corner-last, adjacent) | Draw at R12 (both 32.13) | 0 |

Decisive outcomes only when one side intentionally plays a strictly inferior shape. No game reached double-pass or max_turns; all resolved on the threshold condition.
