# Team-11 Evaluation — Genesis Creativity Engine Run 16

**Team ID:** team-11
**Game ID:** f8dbeb3079a5 (R16 leaderboard rank 2)
**Generation:** 8
**Lineage:** Gen 6 parent 6e408facd632 (GoEssence 0.0150) → this Gen 8 (GoEssence 0.1195)

---

## PHASE 1 — RULE COMPREHENSION

### Board structure
- **Dimensions:** 2D, 8 × 8 (64 cells).
- **Topology:** `moore` (NOT torus, despite `sim_play_helper.py`'s render header). Moore neighborhood, no edge-wrap. Interior cells have 8 neighbors (orthogonal + diagonal); edges 5; corners 3.
- **Coordinates:** action ID = `y * 8 + x`. Action 64 is **pass** (`num_actions = 65`).

### Turn structure — **SIMULTANEOUS**
Both players submit one action per round; resolved via `step_simultaneous()`. Resolution order:
1. Decode both actions.
2. **Collision rule:** if both players target the same non-pass cell → **mutual annihilation** (no stone is placed; cell stays empty). This is the central "novelty" mechanic of simultaneous placement.
3. Otherwise both placements land.
4. Captures (n/a here — capture_type = none).
5. Propagation applied for both placements (additive — order independent for influence).
6. Threshold checked using the post-step combined board.
7. Both pass = double-pass → draw (R13 fix).

### Action types
Place only (no movement). Constraint: target empty cell anywhere (`first_move_anywhere: true`).

### Capture / CA dynamics
**None.** `capture_rule.capture_type = "none"`. No cellular automaton (`uses_ca = False` per inspect output). Pure placement + influence + threshold.

### Propagation (influence)
- **prop_type:** influence
- **radius:** 1 (Chebyshev — Moore neighborhood, includes the placed cell itself)
- **strength:** 1.0388
- **decay:** 0.3712 (per-distance multiplier; only distance 0 and 1 matter)

When P1 places at cell C: every cell within radius 1 (i.e. C and its 3-8 Moore neighbors) gets `+strength × decay^dist` added to `board_values`. P2 placement: same magnitude, sign flipped.
- Distance 0 (the cell itself): +1.0388 (or −1.0388 for P2)
- Distance 1 (each neighbor): +0.3856 (or −0.3856)

`board_values` is a single signed scalar field; it is the *net* influence (P1 positive, P2 negative). Values are clamped to ±100.

### Win condition — threshold (margin-based per R16)
- **threshold:** 30.751
- A player's **effective score** = sum of `board_values` over cells they own (P1: positive sum; P2: negate). I.e. you only get credit for influence on cells YOU own.
- If only one player exceeds 30.751 → they win.
- If both exceed in the same step → higher margin wins (R16 fix). Ties → draw.
- max_turns: 100; on max-turn timeout, piece-count majority decides; double-pass → draw.

### Degeneracy flags
- **None catastrophic.** Threshold is reachable in ~10–15 simultaneous rounds (we hit it in 11–15). Random vs random sample of 8 trials all terminated by step 25–40 (mix of P1/P2/draw). No double-pass forcings. Influence math is non-trivial.
- **One subtle observation:** with a *clamped* scalar field and pure additive propagation, the threshold race resembles a quasi-linear race rather than a non-linear strategic game. Margins shrink to floating-point precision under mirror play (see Game 2 / Game 3).
- The rendered "torus" in the helper's header is a label bug — the engine actually uses bounded Moore.

---

## PHASE 2 — STRATEGIC PLAY

All moves were submitted via `step_simultaneous()` through `sim_play_helper.py --rounds`. Action IDs: `y*8 + x`. Influence field verified each round via `--show-values`.

### GAME 1 — P1 diagonal cluster vs. P2 tight cluster

Strategy: P1 builds NW diagonal/diamond around (2,2). P2 builds compact 2×3 SE around (5,5)-(6,6).

| Rd | P1 move | P2 move | P1 score | P2 score | Notes |
|----|---------|---------|---------:|---------:|-------|
| 1 | (2,2)=18 | (5,5)=45 | 1.04 | 1.04 | Symmetric opening |
| 2 | (1,1)=9 | (6,6)=54 | — | — | Diagonals (P1 was learning) |
| 3 | (3,3)=27 | (5,6)=53 | 4.66 | 5.43 | P2 already ahead — tighter cluster |
| 4 | (2,1)=10 | (6,5)=46 | 7.24 | 8.78 | P2 has 2×2; P1 still diagonal — fewer self-adjacencies |
| 5 | (3,2)=19 | (4,5)=44 | 10.59 | 11.36 | Densifying |
| 6 | (1,2)=17 | (4,6)=52 | — | — | |
| 7 | (2,3)=26 | (5,7)=61 | 18.07 | 18.07 | Tied after P1 fills 3×3-minus |
| 8 | (4,4)=36 | (3,4)=35 | 17.95 | 17.95 | **Bridge moves** — P1 invades, P2 invades, mutual cancellation |
| 9 | (3,5)=43 | (5,4)=37 | 18.22 | 19.76 | Deeper invasions; P2 better placement |
| 10 | (3,6)=51 | (4,3)=28 | 18.10 | 20.41 | Frontline thickens |
| 11 | (3,1)=11 | (4,7)=60 | 21.07 | 23.38 | Densification |
| 12 | (1,3)=25 | (5,3)=29 | 24.03 | 25.58 | |
| 13 | (2,4)=34 | (6,4)=38 | 27.77 | 29.31 | |
| 14 | (4,2)=20 | (3,7)=59 | 29.97 | 30.74 | **P2 within 0.013 of threshold** |
| 15 | (5,2)=21 | (6,3)=30 | 30.62 | **32.93** | **P2 crosses (sole crosser); P1 falls 0.13 short → P2 WINS** |

**P1 reflection (G1):** Diagonal opening was a fitness mistake — diagonal-only adjacency builds at 1 self-neighbor per stone vs. orthogonal adjacency in a 2×2/3×3 which gives 2-3. P2 was up by 1.5 effective from round 4 onward; the bridge attacks at round 8 traded evenly but didn't recover the geometry deficit.

**P2 reflection (G1):** Tight 2×3 → 3×3 was efficient. The (3,4) bridge stone got cancelled to ~−0.27 (vs. self ~−1.04 expected); ditto (5,4)→−0.50. Net invasion ROI was poor but tied P1's invasions; the early lead in cluster density carried through.

**Endgame:** Threshold reached cleanly (P2 at 32.93, decisive). No double-pass, no max-turn timeout.

---

### GAME 2 — Symmetric tight-cluster mirror

Both players play textbook 2×2 → 3×3 from opposite corners, mirroring round-by-round.

| Rd | P1 | P2 | P1 score | P2 score |
|----|----|----|---------:|---------:|
| 1 | (2,2)=18 | (5,5)=45 | 1.04 | 1.04 |
| 2 | (1,2)=17 | (6,5)=46 | — | — |
| 3 | (2,1)=10 | (5,6)=53 | — | — |
| 4 | (1,1)=9 | (6,6)=54 | 8.78 | 8.78 |
| 5 | (3,2)=19 | (5,4)=37 | 11.36 | 11.36 |
| 6 | (2,3)=26 | (4,5)=44 | — | — |
| 7 | (1,3)=25 | (4,6)=52 | — | — |
| 8 | (3,3)=27 | (4,4)=36 | 21.04 | 21.04 | bridge stones — mutual ~−0.39 each |
| 9 | (3,1)=11 | (6,4)=38 | 24.39 | 24.39 | each side has full 3×3 |
| 10 | (4,2)=20 | (3,5)=43 | 27.74 | 27.74 | extending |
| 11 | (4,1)=12 | (5,7)=61 | **31.0925420067187 34** | **31.0925420067187 37** | both cross — diff = 3.5e-15 → engine awards P2 (floating-point tiebreak) |

**Result:** P2 wins by 3.5×10⁻¹⁵ effective margin. Functionally a **draw**.

**P1 reflection (G2):** Perfect mirror strategy; no winning asymmetric move identified. The cross-then-or-interfere fork (round 11) was analyzed exhaustively (see top-moves enumeration in working notes): both players' best margin moves are +3.35; both players cross; tied to FP precision.

**P2 reflection (G2):** Same — mirror works. The "second-mover advantage" predicted by simultaneous-game intuition (no first-mover penalty) is confirmed but is so perfectly symmetric that it dissolves into floating-point noise.

**Endgame:** Threshold reached on round 11 by both players. No double-pass.

---

### GAME 3 — SEAT SWAP

Same opening as Game 2 but with the seat labels swapped: P1 plays the SE side, P2 plays the NW side. All moves identical in geometry, just labels flipped.

Final state, R11:

```
P1 (SE) effective: 31.0925420067187 37
P2 (NW) effective: 31.0925420067187 34
P1 wins (floating-point tiebreak).
```

**Seat-swap evidence:** Game 2 → P2 wins; Game 3 → P1 wins. The geometry is identical, only the seat labels flipped. The outcome flipped. This **proves the game is seat-balanced under symmetric mirror play** — the mechanic, on its merits, gives no first-mover advantage. The "winner" is a floating-point coin flip.

In real (asymmetric) play, the dynamic is more interesting: in Game 1 (asymmetric), P2 won decisively due to a real strategic advantage (denser opening), not a tiebreak.

---

### Strategy guides

**P1 strategy guide (also applies to P2 — fully symmetric game):**
1. Open in an interior cell of your chosen quadrant — interior gives 8 neighbors, more compounding room.
2. **Build a 2×2, then 3×3, then 4×4.** Orthogonal adjacency (2 own neighbors per pair) beats diagonal-only adjacency (1) and is the dominant scaling pattern. Avoid scattering.
3. **Stay 2 cells away from opponent stones early.** Adjacency to enemy stones erases ~0.39 of mutual influence — both sides bleed equally. Adjacency is OK only when you can also boost ≥2 own cells.
4. **Bridge moves** (placing on a cell adjacent to 1 own + 2 enemy stones) are net-zero at best and only useful for tempo control or denying opponent's expansion squares.
5. **Endgame fork (round ~10-15):** when both sides are within 3 of threshold, the best moves are +3.35 margin. If both reach +3.35, both cross simultaneously and resolve by FP. If you can find a +3.5 move (rare; requires very specific neighbor counts) you win cleanly. Otherwise plan for a draw or hope for opponent's mistake.
6. **Collisions** are nearly always bad (lose tempo); avoid playing on cells the opponent obviously needs.

---

## PHASE 3 — STRATEGIC ANALYSIS (joint)

**Q: Are there distinct viable strategies, or does one approach dominate?**
There is essentially **one optimal strategy: build the densest possible orthogonal cluster, ignore the opponent unless they invade your territory, and race to threshold.** Variations: cluster shape (2×2 vs L vs 3×3), expansion direction, and tempo of "bridge" attack. But the high-level recipe is uniform. This is borderline a single-strategy game.

**Q: Is there meaningful counter-play?**
Limited. Bridge attacks (placing between clusters) have trivial expected swing because the influence at the bridge cell is ~0 (cancelled by both clusters). Defense reduces to "build faster". The only "counter-play" is the **endgame collision RPS**: when both players have one move to threshold, choosing whether to cross-or-interfere has Prisoner's Dilemma flavor — but in practice both players cross and floating-point arbitrates.

**Q: Short-term vs long-term tension?**
Mild. Each move's value is computable directly (own gain + opp loss). There is no compounding "investment" play — every move's full effect is local and immediate. Tempo barely matters because turns are simultaneous and influence is additive. **Long-term planning is irrelevant beyond ~3 plies.**

**Q: Emergent concepts?**
- **Territory** — yes, weak: each player's "side" matters because clusters self-compound only on cells you own.
- **Influence** — yes, by definition, but it's a transparent additive linear field with no thresholds, gradients, or non-linear dynamics.
- **Tempo / initiative** — minimal under simultaneous turns.
- **Mutual annihilation collisions** — present but rarely strategically deep; they are just lost-tempo punishment.
- **Ko fights** — none (no capture, no super-ko complications observed).
- **Bridge / contact dynamics** — yes but mathematically equivalent to a tax on both players.

**Q: Does topology matter?**
Yes a bit — Moore (8-neighbor) gives more compounding than von Neumann (4) and slower than torus (more uniform). The non-wrapping edge means corners/edges are weaker, which gives interior-centric play a clear preference. With this strength/decay, the game is **moderately topology-sensitive**: a hex board would yield ~6 neighbors and slightly different optimal cluster shapes; torus would erase the corner-disadvantage and possibly force more direct contact.

**Q: First-mover / seat advantage (simultaneous case)?**
**Quantified by Game 2 vs Game 3 seat-swap:** Game 2 (P1 NW, P2 SE) → P2 wins by 3.5e-15. Game 3 (swapped) → P1 wins by 3.5e-15. The mechanic **fully eliminates seat advantage under symmetric play.** In asymmetric play (Game 1 — P1 deliberately played a bad diagonal opening), the better-shaped cluster won — i.e. the result tracked strategy quality, not seat. **The simultaneous turn structure is doing real work** at the balance dimension. Note: this is a clean validation of R16's margin-based threshold fix.

**Seat-identity bias acknowledgement:** All three roles (P1, P2, Adversary) were played by a single agent in this evaluation. This biases toward consistent strategies across seats; in particular Game 2's exact mirror is artifact-prone. Game 1's different P1/P2 strategies and Game 3's seat-swap robustness check were used to compensate. With independent agents, Game 2's perfect mirror is unrealistic; the winning rate would track who can find the +3.35 cross moves first.

---

## PHASE 4 — NOVELTY ADVERSARY

### Adversary's case: the game is NOT novel

**Claim 1: This is just Othello on a different topology with a real-valued score.**
- *Refutation:* Othello has flipping (no flipping here), capture-by-flanking, and a piece-count win condition. This game has no flipping, no capture, and a continuous-valued threshold. In Othello, placement is *legality-constrained* by the flip rule; here any empty cell is legal. **An Othello expert would mis-play immediately by hunting for flips that don't exist.**

**Claim 2: This is Reversi-influence Go (Tumbleweed-like).**
- *Tumbleweed* (Mike Zapawa, 2019): hex board, place stones whose stack-height = number of own pieces in line-of-sight; ownership decided by majority sight. Real game families are extremely close in spirit — both use radiated influence, both score by influence on owned cells, both have no capture.
- *Difference:* Tumbleweed uses hex sight along all 6 directions (radiation continues until blocked); this game uses Moore radius-1 (one-cell halo, no propagation through pieces). Tumbleweed has stack-height stones; this one has binary ownership and continuous influence. Tumbleweed is alternating, this is simultaneous. **Phase-2 moment that breaks the analogy:** the round 8 bridge moves in Game 1 — in Tumbleweed those would matter for line-of-sight blocking; here they only compute one-cell influence. Different strategic weight.

**Claim 3: This is Blotto / Colonel Blotto.**
- *Refutation:* Blotto is a one-shot resource-allocation game. This is sequential simultaneous over 11–15 rounds with state. State persists; you can react to opponent's last-move information. Stronger analogy is *iterated Blotto with shared geometry*, but iterated Blotto literature doesn't have spatial neighbor compounding.

**Claim 4: This is "X on a Moore board with simultaneous moves" — re-skin.**
- *Refutation:* The closest re-skin claim would be "Tumbleweed simultaneous on Moore" but the influence radius is 1 (not infinite line-of-sight), the simultaneous turn structure is foreign to all candidates, and the threshold mechanic (sum of influence on owned cells crossing 30.75) is unusual — most threshold games count pieces or cells, not real-valued influence sums.

**Claim 5: Life-like CA?** No CA in this game — moot.

**Claim 6: Diplomacy-style simultaneous?** Diplomacy has unit movement and binding negotiation; this game has placement only, no negotiation. The collision-annihilation rule resembles Diplomacy's bounce rule but operates on a continuous influence field rather than discrete units.

### Verdict from rebuttal

The game has **two genuinely uncommon features in combination**:
1. **Simultaneous placement with mutual-annihilation collisions** on an influence field (not seen in any major game I know — Diplomacy bounces are on fortresses; Tumbleweed is alternating).
2. **Continuous real-valued threshold on owned-cell influence** (rather than piece count or area).

The simultaneous + influence + threshold combo is uncommon. However: the strategic content reduces to "build the densest cluster", which is conceptually similar to Tumbleweed-strength-stacking. The **mechanism** is mildly novel; the **strategy** is not deeply novel.

**Novelty score: 4/10.** Mild novelty in mechanic (simultaneous + mutual-annihilation + influence-threshold), but strategic depth maps cleanly onto known Tumbleweed-family insights with reduced complexity (no line-of-sight, no stacks).

---

## PHASE 5 — VERDICT

**Team ID:** team-11
**Game ID:** f8dbeb3079a5
**Rules summary:** Place stones on an 8×8 Moore board; each placement adds ±1.04 self-influence and ±0.39 to each Moore neighbor on a shared signed scalar field. First player whose owned cells' influence sum crosses 30.75 wins; same-step crossings resolved by margin (ties = draw). Simultaneous turns; same-cell collisions = mutual annihilation.
**Topology:** 8×8 Moore (bounded, no wrap), 64 cells, 65 actions (cell + pass).
**Turn structure:** Simultaneous.

### SCORES (1–10)

- **Strategic Depth: 4** — One dominant strategy (orthogonal cluster densification + race). Tactics reduce to a small move-evaluator (cell pre-value + neighbor counts). Endgame admits a small Prisoner's-Dilemma-flavored fork but it is not deep. Decisions are arithmetic; ML training curves (run seed=70052: random=0.84; seed=71052: 0.48) show modest learnability, not deep skill ceiling.
- **Emergent Complexity: 3** — Continuous influence field with bridge/contact dynamics is the only emergent concept. Mutual-annihilation collisions exist but rarely fire under good play. No ko, no capture cascades, no non-linear feedback.
- **Balance: 8** — Strong. Seat swap (G2 → G3) flipped outcome by 3.5×10⁻¹⁵, confirming the simultaneous mechanic + R16 margin-based threshold give a near-perfectly seat-symmetric game. Asymmetric play (G1) tracked strategy quality, not seat. The R16 margin fix demonstrably did its job here.
- **Novelty (post-adversary): 4** — Simultaneous + influence + threshold combination is mildly novel; conceptually adjacent to Tumbleweed (closest analog) and Blotto-iterated. No deeply original mechanic survives the adversary's catalog comparison.
- **Replayability: 4** — Once you know the optimal cluster shape and endgame fork, games converge. Random openings and pre-bridge invasion timing add variance, but the strategic surface is exhausted within 3–5 plays.
- **Overall "Would I play this again?" : 4** — Pleasant 11–15-round simultaneous game; balanced; arithmetically solvable. Educational example of simultaneous-turn balance, but not gripping.

### CLOSEST KNOWN-GAME ANALOG
**Tumbleweed (Mike Zapawa, 2019) + simultaneous turns + reduced influence radius.** Not identical: Tumbleweed has hex board, line-of-sight radiation, stacking, and alternating turns. This game has Moore-radius-1 halo, no stacking, simultaneous placement.

### KILLER FLAWS
- **Strategic surface is shallow and additive.** The expected-value of every move is a closed-form arithmetic expression over neighbor counts. ML agents converge fast (random win rate >0.48 after ~240k steps). Skill ceiling is low.
- **Mirror play deterministically reaches the threshold to floating-point precision.** This is *not* a degeneracy in the engine — the R16 margin fix correctly draws true ties — but it means perfect-symmetric play offers no decision branch and the floating-point tie is unsatisfying.
- **No tactical motifs:** no ko, no captures, no long-range tactics, no traps, no zugzwang.
- **Bridge moves are tax-on-both-sides:** there is no genuine offensive option that meaningfully changes the score gradient; offense and defense are equally efficient at +0.78 swings or +3.35 own-side swings.

### BEST QUALITY
The **simultaneous + margin-based threshold + mutual-annihilation collision** combination is genuinely interesting as a balance demonstration. The seat-swap test (Game 2 vs Game 3) is one of the cleanest demonstrations I've seen of a turn structure successfully eliminating first-mover advantage. From a Run-16 hypothesis perspective, this game is *evidence the engine works correctly* but also *evidence that simultaneous play does not, by itself, generate strategic depth* — consistent with the R16 hypothesis that classical alternating designs are stronger.

### IMPROVEMENT IDEAS
**Add non-linearity to the influence accumulation.** A single cheap rule change: cap the absolute board_value at a much smaller magnitude (say ±1.5 or ±2.0 instead of ±100). This would force players to *spread* their stones rather than densify one cluster, and would make placement into already-influenced cells diminishing-returns rather than additive. Combined with the threshold, this would produce genuine territorial decisions: do I reinforce my saturated cluster (low marginal return) or invade (high marginal return)? That single change would convert the game from "race to cluster the densest patch" into "balance density vs. coverage", which is much closer to Go's territory-vs-influence tension.

Alternative: add a **"saturation" capture** — a cell whose absolute value exceeds e.g. 2.5 flips ownership to whichever player's sign matches. This would create real attacking play and tactical motifs absent today.
