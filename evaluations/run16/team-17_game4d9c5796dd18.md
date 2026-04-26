# Team-17 Evaluation: Game 4d9c5796dd18 (Run 16)

**Team ID:** team-17
**Game ID:** 4d9c5796dd18
**Generation:** 10  (parent fd78496038d2, mutation: capture)
**Engine reported metrics:** GE 0.088, Strategic Depth 0.637, Non-Triviality 0.849, Strategic Diversity 1.0, ELO 2640

---

## Phase 1 — Rule Comprehension

### Board Structure
- **Topology:** Moore 8×8 (verified directly: cell 27 has 8 Moore-neighbors {18,19,20,26,28,34,35,36}; corner cell 0 has 3 neighbors {1,8,9}). Note: `play_helper.py rules` mislabels Moore as "von Neumann" — the prompt warns about this; the underlying topology is in fact 8-connected Moore.
- **Cells:** 64. Action space: 65 (64 placements + pass).
- **Action mapping:** `action_id = y*8 + x`.

### Turn Structure
- **ALTERNATING.** `pieces_per_turn=1`. Played via `play_helper.py --action play`.

### Action Types
- **Place only.** Target = empty cells. `first_move_anywhere=True`. No movement, no capture-action.

### Capture Rule
- **Surround capture, threshold 2** (Go-style "0-liberties" group removal).
- **Critical observation:** with Moore-8 connectivity, an interior stone has 8 neighbors AND 8 liberties. To surround a single interior stone, an opponent must place 8 enemy stones (consuming 8 of its own moves). This is the "moore+surround inertness" phenomenon R13/R14/R15 saw.
- I verified the capture mechanic does *fire* when forced (filed a contrived sequence: P1@27, then P2 plays {18,19,20,26,28,34,35,36} while P1 plays distant cells; on the 8th surround stone, P1@27 is removed). But in any rational play it never triggers, because:
  - P1 will not leave its starter stone isolated; after a few moves P1 has multiple Moore-connected stones, and surrounding a *group* requires filling **all** liberties of the group — exponentially harder than surrounding one stone.
  - 8 P2 surround moves cost P2 ~15 own-influence (own-cells deeply polluted by P1's surrounded stone in the middle), so the surround attempt simultaneously kills P2's threshold race.

### Propagation
- **Influence**, radius 2, strength 1.684, decay 0.721.
- Per stone: cell value at d=0 → +1.684, d=1 → +1.214, d=2 → +0.875.
- Moore radius-2 = 5×5 Chebyshev disk = 25 cells (verified).
- Sign: P1 stones add positive, P2 stones add negative.

### Win Condition
- **Threshold:** "sum of board_values over own-owned cells" > **50.508** for P1 (using positive sum) or > 50.508 for P2 (using `-board_values`).
- Max turns: 100.
- R16 margin-tiebreak: equal margins on same tick → draw (didn't fire in any of my games).

### Degeneracy Flags
- **Capture rule is effectively inert in normal play.** Confirmed by my Phase 2 games (3 games, 0 captures) and the R16 generator's own moore→grid downgrade comment in `generator_v2.py:140` saying "R13/R14/R15 evals all saw 0 captures across 15+ games with this combo." The downgrade lives in `generator_v2.py` (creation) but is **not duplicated in `evolution/operators_v2.py:_fix_consistency`**. The parent `fd78496038d2` was moore+outnumber (a legal moore combo); the gen-10 `capture` mutation flipped capture_type→surround **without re-applying the moore→grid topology downgrade**. So the bug is: capture-mutation + post-mutation `_fix_consistency` does not include the surround→grid downgrade, even though the generator does. Confirms hypothesis (b) — "my fix had a hole".
- **Threshold is reachable**: 50.5 ≈ a tight 3×3 cluster (~9 own-cells × ~5.5/cell). Achievable in 9–11 moves.
- **Strong P1 (first-mover) advantage:** symmetric play gives P1 the win by 1-tempo. Quantified below.

---

## Phase 2 — Strategic Play

I played 3 full games (the same agent across roles, with role-swap discipline; finalised each role's reasoning before switching). Every move engine-verified via `play_helper.py` / direct engine calls.

### Game 1 — P1 cluster, P2 mirror cluster
Move sequence: `27, 36, 28, 35, 26, 37, 19, 44, 20, 45, 18, 34, 21, 25, 11, 12, 10, 17, 9, 43, 13`

| Stage | Board state |
|---|---|
| After move 11 | P1: 3×2 block at (2-4)×(2-3); P2: arrow shape down-right. P1 own-inf=23.4, P2=10.9 |
| After move 19 | P1 own-inf=46.8 (3×3 minus one); P2=1.65 (heavily polluted by P1) |
| After move 21 (terminal) | P1 own-inf = **56.5** > 50.5 → **P1 wins**; P1=11 stones, P2=10 stones, **0 captures** |

**P1 strategy:** seize centre, build a 3×3 block of stones, fill in interior. The decay-0.72 curve makes radius-2 contributions still meaningful (0.88 vs 1.68 at d=0), so a 3×3 block has each interior cell receiving influence from 9 stones (own + 8 nbrs), summing to ≈12 per cell.

**P2 reflection:** Mirror-clustering keeps me close on own-inf for the first 8 moves but I always trail by exactly 1 stone. P2's best move was 43 (move 20) which adds own-inf without being too close to P1's pollution zone — but it came too late.

### Game 2 — P1 cluster off-centre, P2 mirror upper-left, more disruption
Move sequence: `36, 28, 27, 35, 45, 19, 44, 18, 37, 20, 46, 25, 38, 17, 53, 10, 54`

| Stage | Result |
|---|---|
| After move 14 | P1=29.98, P2=23.77 |
| After move 16 (P2 plays 10 — strong fill-in) | P1=42.4, P2=36.2 |
| After move 17 (terminal) | P1 own-inf = **58.4** > 50.5 → **P1 wins**; 9 vs 8 stones, **0 captures** |

**Key move:** P1's 53 (move 15) — fill-in at (5,6) closing the third row of the cluster. Cell 53 had pre-placement value 5.39 from 4 own-neighbours; placement adds 1.68 self + boosts 6 existing own cells. Single-move own-inf gain ≈ 12.5.

**P2 reflection:** Mirror-style fills kept me competitive; the 10 (2,1) move replicated the same trick on P2's side. But again, **first-mover places one fill-in stone before me**, which is enough.

### Game 3 — Seat-swap probe (perfect mirror)
Move sequence: `27, 36, 18, 45, 19, 37, 26, 44, 28, 46, 10, 53, 11, 52, 12`

This was an explicit symmetry test — both players used the *same* compact-cluster heuristic, mirroring each move across the (3.5,3.5) board centre. Result:

| Move # | P1 own-inf | P2 own-inf |
|---|---|---|
| 10 | 18.07 | 18.07 |
| 12 | 29.85 | 30.53 (slight P2 lead from corner-shape geometry) |
| 14 | 42.4 | ~43 |
| **15 (P1's move 8)** | **59.3** > 50.5 → **P1 wins** | 44.7 (P2 never got move 8) |

**Auxiliary game (Game 3-alt) — P1 plays naively (4 corners spread), P2 plays cluster:** P2 wins decisively (own-inf 55.4 > 50.5 in 14 moves). Confirms the threshold race is the *only* viable strategy; spread play loses.

### Strategy Guides

**P1 strategy guide:**
1. Open at centre or near-centre (cell 27 / 36).
2. Build a *Moore-connected* cluster — diagonals matter; don't waste moves on knight-jumps.
3. Aim for a 3×3 block; the *interior* of the block is where own-inf stacks (a 3×3 yields an interior cell with influence from all 9 stones).
4. Each move pick the highest "fill-in delta" — a cell whose pre-placement value is already high (already inside the radius-2 disk of many own stones) AND whose placement boosts many existing own cells.
5. Don't engage in capture attempts. They take 8+ moves and deny you the threshold race.

**P2 strategy guide:**
1. The first-mover gap of ~1 own-inf-stone is **fatal** under perfect play. To have any chance, hope P1 misplays (plays for capture, plays scattered, plays a corner first).
2. If P1 plays cluster, your only counter is to also play cluster — adjacent or opposite-corner. Adjacent is mathematically worse (P1's stones pollute your own-cells negative-positive).
3. *Disruption moves* (placing P2 next to P1) **lose own-inf** because that cell becomes net-positive (P1's neighbours outweigh your own −1.68). I observed P2's own-inf go *negative* after a single shadow move in an early test.
4. Best disruption that doesn't backfire: place at d=2 from P1 (single step beyond Moore-adjacency) — outside P1's strongest radius-1 contribution but still applies your own −0.88 to P1's cell.

---

## Phase 3 — Strategic Analysis

### Distinct viable strategies?
**No.** The optimum is a tight Moore-connected cluster that fills in. Spreading loses. Capture-seeking loses. There is no "territory vs. influence" tension because territory does not score; only own-cell board-values matter.

### Meaningful counter-play?
**Limited.** P2's only counter-play is to mirror P1's cluster. Adjacent disruption *backfires*: P2 stones near a strong P1 cluster have a NET POSITIVE board-value (because P1's d=1 contribution +1.214 outweighs P2's self −1.684 in some configurations), making them count *against* P2's own-inf. In my Game 2 retry test, after just 4 moves of P2 shadowing, P2's own-influence was **−0.81** (negative).

### Short-term vs long-term tension?
**Mild.** Each move's own-inf delta is locally computable (it's a known sum). The strongest move is almost always the immediate fill-in. There is some tension at the edge between "extend" (new direction) vs "fill" (boost existing own cells) — fill is usually correct.

### Emergent concepts?
- **Tempo / initiative:** present and decisive.
- **Cluster geometry / "fill-in" tactics:** real but shallow.
- **Influence and territory:** influence yes; territory no — empty cells don't score.
- **Ko / mutual annihilation / capture races:** absent (capture is inert).
- **Connection / cut:** absent (Moore connectivity makes everything connected easily; no cutting threats matter).

### Topology relevance?
**Topology matters in a degenerate way.** Moore-8 (vs grid-4) *does* affect the influence radius geometry slightly (Chebyshev vs Manhattan), but the dominant effect is that Moore-8 makes the surround capture a dead rule. A grid-4 version of the *same* game would have surround capture firing in real play, fundamentally changing the strategy. So the topology choice converts a potentially deep game (grid + surround threshold) into a shallow influence-race.

### First-mover advantage (quantified)
- Game 1: P1 wins, 56.5 vs 14.4. P1 stones=11, P2=10.
- Game 2: P1 wins, 58.4 vs 36.2. P1 stones=9, P2=8.
- Game 3 (mirror): P1 wins, 59.3 vs 44.7. P1 stones=8, P2=7 (P2 never got move 8).
- Game 3-alt (P1 naive): P2 wins, 55.4 vs 16.4 — confirms P2 *can* win, but only on P1 mistakes.

**P1 wins ALL 3 games against equal-strength P2.** First-mover advantage is **dominant and structural**, not merely statistical. The R16 fitness function used a worst-of-three (trained/random/greedy probe); the trained-pair winrates in the database (0.5, 1.0, 0.5, 1.0 across 4 seeds — two seeds at 100% P1, two at 50/50) suggest the probe averaged around 0.75 for the first-player-bias check, not catching the structural imbalance. This game *should* have been seat-flagged.

---

## Phase 4 — Novelty Adversary

**Adversary's case (the game IS NOT novel):**

(a) Direct ancestor: this is **"Tumbleweed lite"**. Tumbleweed is a 2008 abstract by Mike Zapawa where players accumulate "stack height" influence on cells they reach via line-of-sight; the player whose total influence exceeds a threshold wins. Replace LOS with Chebyshev radius and the games are mechanically the same.

(b) Closest second: **Reversi/Othello-flavoured threshold race** — place stones, score by neighbourhood count. Without the flip mechanic, it's a degenerate Othello where you just keep placing in your own cluster.

(c) Re-skin claim: this is "**Genesis-style influence + Moore + threshold**" — the Run 13/14/15 evaluations have already reported games of this exact shape (e.g. R15 game `f53af23bd8c0` was hex+influence+threshold). Replace hex with Moore and the strategy transfers immediately.

(d) The Go analog (surround capture) is **purely cosmetic**. An expert in Go would *not* find the surround mechanic relevant — the rule is named but never fires. So the apparent novelty (Go-meets-influence) is a label, not a mechanic.

(e) **An expert transfer test:** a player who knows Tumbleweed + Othello + radius-influence Genesis games would solve this game in 5 minutes flat: "place at centre, build a 3×3 block, fill the corners". No new strategic concept arises that isn't trivially derivable from those references.

**P1 + P2 rebuttal:**

The adversary is essentially correct. The only mildly distinctive feature is the *combination* of:
- Moore-8 connectivity (vs Tumbleweed's LOS),
- Decay 0.721 (vs hard cutoff in some references),
- First-move-anywhere in a non-pie-rule context.

But none of those produce a *new strategic phenomenon*. The Phase-2 moves I played all fit a player who'd learned standard Genesis-style threshold-race heuristics. There was no moment in my play where I had to reach for a concept beyond "fill in your cluster".

The one rebuttable point is that the **inert surround rule** is genuinely novel as a *negative* feature — it's a label-without-mechanic — but that's a flaw, not novelty.

**Novelty score: 2/10.** Direct re-skin of Tumbleweed-style threshold-influence with a vestigial surround-label that does nothing. No expert transfer barrier.

---

## Phase 5 — Verdict

**Team ID:** team-17
**Game ID:** 4d9c5796dd18
**Rules Summary:** Moore 8×8 alternating place-only game; influence-radius 2 propagation, win by sum-of-own-cell-values exceeding 50.5; surround capture rule named but inert.
**Topology:** Moore (8-connected), 8×8, 64 cells.
**Turn Structure:** Alternating, 1 piece per turn.

### SCORES (1–10)

- **Strategic Depth: 3/10** — One viable strategy (compact-cluster fill-in). Move-selection is mostly local greedy on `delta_own_influence`. No multi-step planning or sacrifice motifs. The capture rule that nominally adds depth is mechanically inert.

- **Emergent Complexity: 2/10** — No emergent territory/initiative/sacrifice/ko dynamics. The cluster-build is literally the obvious strategy from the rules. Nothing surprised me in play.

- **Balance: 2/10** — P1 won 3/3 games against equal-strength play. P2 wins only on P1 misplay (Game 3-alt). The seat-bias is structural, ~1-stone tempo gap; the trained-pair winrates in the DB (mixed 0.5/1.0 across seeds) underestimate this. The R16 worst-of-three probe should have caught it.

- **Novelty (post-adversary): 2/10** — Direct Tumbleweed/Genesis-influence re-skin. The Moore + surround combo is a *label* — surround capture never fires. Real novelty would require the capture to fire at meaningful frequency.

- **Replayability: 3/10** — Once the cluster-fill heuristic is learned, every game converges in 15–21 moves with the same arc. Position diversity is low because the optimal cluster is geometrically constrained to one of a few shapes.

- **Overall "Would I play this again?": 2/10** — One-shot interesting (verifying inertness was educational); no pull for repeat play.

### Closest Known-Game Analog
**Tumbleweed (Mike Zapawa, 2008)** — also a threshold race over a sum of per-cell stack heights / influence values, also no captures, also strongly first-mover-favoured without a pie rule. Differences: Tumbleweed uses LOS not radius decay; uses a hex board; allows pie-rule swap. This game is a Moore-grid Tumbleweed with a vestigial surround label.

### Killer Flaws
1. **Surround capture is inert.** Across 3 full games + 1 auxiliary, 0 captures fired in real play. Only a contrived 8-stone surround sequence triggered it. The `capture_type=surround, topology=moore` combination is the exact failure mode the R16 generator was supposed to forbid (`generator_v2.py:140`); the *creation-time* downgrade exists, but the *mutation-time* `_fix_consistency` (in `evolution/operators_v2.py:_fix_consistency`, lines 50–170) does NOT include the surround→grid downgrade. The parent `fd78496038d2` was moore+outnumber (legal); the `capture`-type mutation flipped capture to surround without re-applying the topology downgrade. **This is hypothesis (b) confirmed: the R16 fix has a hole — it only enforces the rule at generation, not at mutation.** Recommended fix: add the same `if capture_type == "surround" and topology_type == "moore": topology_type = "grid"` block to `_fix_consistency`.
2. **Strong, structural P1-favour** — 3/3 P1 wins under equal play. Worst-of-three seat-balance probe didn't flag it.
3. **No multi-strategy diversity** — only "compact cluster" strategy is viable.

### Best Quality
The threshold dynamics are *cleanly designed*: 50.508 sits roughly at the threshold of a tight 3×3 cluster, so games end naturally between move 15 and 21 — no double-pass-draw, no max-turns timeout. The R16 threshold-margin tiebreak and threshold-floor-by-strength logic produce a game that at least *resolves cleanly*, which is more than several R13/R14 top games managed.

### Improvement Idea
**Replace surround → outnumber with threshold 3.** The original lineage (parent fd78496038d2) was moore+outnumber, which actually produced captures in Run 16 evaluations. Outnumber-3 on Moore means a stone with 3+ enemy Moore-neighbours dies — this *does* fire under cluster-building because clusters naturally surround opposing edge-stones. That single rule swap converts the game from "inert capture" to "live capture threat that disrupts cluster-fill", introducing genuine sacrifice/timing tension.

Alternative: keep surround but switch topology to **grid (von Neumann)**, where surround needs only 4 stones and fires routinely.

---

## Appendix — Concrete capture verification

Forced surround capture sequence (does work mechanically):
```
P1=[27, 0, 7, 56, 63, 1, 6, 57]  P2=[18, 19, 20, 26, 28, 34, 35, 36]
After P2's 8th stone (cell 36): cell 27 (P1) is captured (owner→0).
At that moment P2 own-inf = 57.35 (>50.5) → P2 wins by threshold; the capture
itself is incidental to the win condition.
```
This sequence requires P1 to actively cooperate (placing in corners while P2 fills the surround). In any non-cooperative play, P1's fill-in moves prevent the surround long before it completes.

**Conclusion:** surround capture exists in the rules and the engine; it does not exist in the reachable strategy space.
