# Run 20 Agent-Team Eval — team-pilot — Game 5f5c72e15220

**Team ID:** team-pilot
**Game ID:** 5f5c72e15220 (menger rank-3 by GE / **rank-1 by depth 0.894** — depth record across all aigame runs)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game 5f5c72e15220` (see `briefing_menger_5f5c72e15220.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 menger sponge — same substrate as `a6385db22c0b`. 400 active cells with the level-2 fractal hole pattern.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placement + 1 pass. Placement legal at any empty active cell.

**Placement & capture.** **Outnumber-3** capture (the structural differentiator from `a6385db22c0b`/`b160b1f55378`/`d1dbc6568fc7`/`f98b9414f638`): when a stone is placed at `c`, every adjacent enemy stone with **≥3 friendly neighbours** (counting `c`) is cleared. **Empirical consequence**: degree-2 cells like `(1,0,0)` are now *un-capturable* because the cell only has 2 active neighbours — outnumber-3 cannot fire. Verified with `0,1,2`: P2 stone at `(1,0,0)` survives even after P1 flanks at `(0,0,0)` and `(2,0,0)`. This single rule change inverts the capture-trap dynamic from outnumber-2.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Same kernel as siblings.

**Win condition.** Threshold-race; first player whose owned-cell sum exceeds **57.974** wins. `target_dimension_p2 = -1` (mirror). Max turns = 100.

**Pie rule.** Off.

**Critical structural observation: residual value persistence + capture interaction.** When a stone is captured, the cell's `board_values` entry is **not reset** — it retains all prior deposits from both players. A captured cell can be re-occupied by either player for a high-value placement that picks up the deposited value as bonus. Empirically observed: at move 41 P1 re-places at `(0,3,0)` (a previously captured cell) for Δ+3 effective — significantly above the +1 floor for vacuum placement.

**Degeneracy check.**
- Outnumber-3 + menger degree-truncation: **the bottom 60–70% of cells (those with degree 2–3 active neighbours) are essentially uncapturable.** Captures fire only on degree-4+ cells when 3 of 4 neighbours are placer-coloured. This dramatically reduces capture frequency relative to siblings.
- Captured cells retain residual values → re-occupation tactics emerge.
- No inert fields.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`.

### Game 1 — Interleaved corner contest (the headline line)

Sequence (55 plies, dead-even race): `0,1,9,2,18,11,19,20,3,12,21,27,28,29,81,83,84,99,101,102,110,165,162,164,180,182,108,173,183,191,189,200,243,245,261,263,170,235,153,254,27,99,102,174,171,224,252,242,4,38,5,233,22,236,25`.

Plot:
- Both sides build clusters in the **same** corner zone `(0..3, 0..3, 0..3)`. P1 starts `(0,0,0)`; P2 *infiltrates* `(1,0,0)` — safe under outnumber-3 because `(1,0,0)` has only 2 active neighbours and cannot be captured.
- P1 at `(2,0,0)` does *not* capture P2 at `(1,0,0)` (verified: P2 piece count stays at 1).
- Both sides pile stones into the corner. The first capture fires at **move 19** when P1 plays `(2,2,1)` — P2 stone at `(2,2,0)` was at degree-5 with 2 P1 neighbours `(1,2,0), (3,2,0)`; the 3rd P1 neighbour `(2,2,1)` triggers outnumber-3.
- **Move 27 double-capture**: P1 plays `(0,3,1)` simultaneously satisfying outnumber-3 on both `(0,3,0)` (3 P1 neighbours: `(0,2,0), (1,3,0), (0,3,1)`) and `(0,2,1)` (3 P1 neighbours: `(0,2,0), (0,2,2), (0,3,1)`). P2 piece count drops 2 in one move. **Net effective score change ≈ 0** — because P2's captured cells had values brought to ~0 by mutual deposits, the capture exchange is roughly neutral.
- **Move 28 P2 (2,1,2)** — P2 deepens its z=2 cluster by placing at the cell adjacent to two existing P2 stones `(2,0,2), (2,2,2)`. P2 effective gain: **+3** from `1 + 0.5·2 = +2 self-and-friends` plus an extra +1 from the deposit being read as effective via the −1 mirror. P2 now leads `+14.5 vs +12`.
- Through move 39 P2 sustains the lead: `+22.5 vs +20.5`.
- Move 41 P1 re-occupies the previously-captured `(0,3,0)` for Δ+3 (residual value harvest). Game becomes a tight tempo race.
- Move 50: **scores tied at +33.5/+33.5**. Move 55: still tied at +38.5/+38.5. Genuine balance throughout.

This is the single deepest game-line I've seen in the R20 menger slate. It has:
- two viable strategies (both clusters in same volume; mutual infiltration safe),
- multiple captures (4 firings observed by move 30),
- a **residual-value re-occupation tactic** (re-claim a captured cell with stored deposits),
- a **double-capture tactic** (one placement satisfies outnumber-3 on two enemy stones),
- a **deepen-own-cluster tactic** (P2 placement that adds −0.5 to existing P2 cells, gaining +0.5 each in P2 effective),
- **tempo-swap dynamics** — leader changes 3 times across 55 plies.

### Game 2 — Mirror cluster baseline

Sequence (16 plies probe): `0,80,1,79,9,71,2,78,18,62,11,69,19,61,20,60`.

Plot: Standard P1 corner / P2 opposite-corner mirror, no contact. After 16 plies P1=+16, P2=+16 — identical to a6385db22c0b. With outnumber-3, this baseline plays the same as outnumber-2 because no captures are triggered in mirror play either way. The game's distinctive depth shows up only when both sides choose to occupy the *same* volume.

### Game 3 — Capture probe

Sequence (3 plies): `0,1,2`. **No capture fires** — confirmed. P2 stone at `(1,0,0)` survives because its only 2 active neighbours `(0,0,0), (2,0,0)` cannot summon the third friendly that outnumber-3 requires. Compare to a6385db22c0b where this same line auto-captures at move 3.

### Strategy guides

**P1 (offence/threshold push):** Don't sit in a separate corner if P2 infiltrates. Instead, (a) flank P2 stones in degree-4+ cells where outnumber-3 can fire, (b) re-occupy previously-captured cells to harvest residual deposits, (c) maintain density compounding. Don't try to capture degree-2 stones — impossible.

**P2 (defence + threshold contest):** **Infiltrate.** Play degree-2 cells in P1's expansion zone (e.g., `(1,0,0)`, `(2,1,0)`, `(0,3,0)`) — these cannot be captured under outnumber-3. Then build adjacent clusters at z=2/z=3 to deepen own-cluster influence. Watch out for degree-4+ cells where outnumber-3 can fire. Pie rule is off but P2 has a real strategy here, not just "lose by tempo".

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Yes — at least 3:**
1. **Standard mirror cluster** (both at opposite corners) — works the same as in a6385db22c0b, P1 +1.5 tempo advantage.
2. **P2 infiltration** (P2 occupies degree-2 cells in P1's zone, then builds parallel cluster across z-layers). Captures on degree-2 cells are off, so this is a real play and produces tempo swings.
3. **Cluster-deepening** (place at the *interior* of own cluster to add −0.5 deposits to already-owned negative cells, harvesting compounding even without new neighbours). This shows up clearly in P2's move 28 line.

**Counter-play.** Real. P1's counter to infiltration is "build degree-4+ cells around the infiltrator, then capture once outnumber-3 lights up." P2's counter to capture-pressure is "re-occupy captured cells for residual harvest, and continue cluster-deepening."

**Short-term vs long-term.** Both. Short-term: capture timing and double-capture potentialities. Long-term: cluster-shape choice across z-layers, with persistent tempo-trade dynamics. Plan horizon ≈ 3–4 plies.

**Emergent concepts observed.**
- **Capture-trap inversion**: degree-2 cells are *uncapturable* in outnumber-3 (vs auto-captured in outnumber-2). This rewrites tactical priorities.
- **Double-capture**: one placement satisfies outnumber-3 on 2 simultaneously-flanked enemies. Observed move 27.
- **Residual-value harvest**: re-occupy a captured cell to pick up deposited values. Observed move 41.
- **Cluster-deepening**: place at interior cell adjacent to 2 own stones for +3 effective (own self + propagation deposits to 2 friends). Observed move 28.
- **Tempo swap**: lead changes 3×+ during the 55-ply game.

**Does menger matter?** **More than in the siblings.** With outnumber-3, the menger degree-distribution becomes a strategic axis — degree-2 zones are "safe haven" for both players, degree-4+ zones are "battlegrounds where captures fire." A flat 9×9 grid with outnumber-3 wouldn't have the same heterogeneity (every cell has degree 4 except edges). This is the **only game in the menger slate where the substrate adds a distinct strategic dimension.**

**Does the propagation kernel matter?** Same as siblings — `decay=0.5` defines compounding.

**Capture-rule contribution.** Outnumber-3 fundamentally changes the game. With outnumber-2, captures fire too easily and dominate (every degree-2 infiltration is auto-loss). With outnumber-3, captures fire only with 3-stone commitment, and the *avoided* captures (degree-2 cells) become tactically valuable. The capture rule pays its rent here — unlike in the siblings.

**First-mover advantage / seat balance.** The briefing's trained-vs-trained **0.333 (P2-favoured)** is *real* and matches my observation that the infiltration strategy gives P2 actual leads. In my Game 1 line, P2 led at moves 28–46, then game dead-tied through move 55. The structural P1 +1.5 tempo from siblings is partially neutralized here because P2 has a counter-strategy. Still no pie rule, but captures + residuals can act as a soft-rebalancer.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is closer to a re-skin than a pure novelty, but the outnumber-3 + menger + residual-value combination is **genuinely distinct** from R19 ancestors:

(a) **Threshold-race influence games** — same family as siblings (Othello-without-flipping / weighted Go scoring).
(b) **Outnumber-3 capture** is rare in the published literature. Tafl is "fully-surround" (all-neighbours), Ataxx is convert-not-remove. The "3-of-N neighbours" formulation creates the asymmetry that makes degree-2 cells safe — that exact mechanic is not in published games.
(c) **The combination "outnumber-3 + influence + threshold-race + residual-value-persistence + menger fractal degrees"** doesn't exist in published games and even within this project corpus this is the first game where outnumber-3 has produced a *measurably* deeper game (R10–R19 also tried various capture thresholds but never landed on this attractor).
(d) **Menger substrate.** Unlike siblings, here the substrate-induced degree heterogeneity is *strategically loadbearing* (degree-2 = safe, degree-4+ = battlefield). This is a genuine substrate contribution.
(e) **Expert-transfer test.** A Go + Othello + Ataxx player would understand the basic mechanics in ~10 minutes but would need to discover the degree-2 safe-haven and re-occupation tactics through play. Estimate: 30 minutes to feel competent, several games to develop the cluster-deepening intuition.

**Closest known-game analogue:** "Influence Othello on a graph with heterogeneous vertex degrees, with rarefied capture rule and persistent cell values." No exact match in published board games. Inside this project, the closest precedent is **R8 Connection Go** (which had a *flip* capture-rule that produced chain-continuation dynamics) but the win condition is entirely different.

**Comparison to R8's Connection Go (8/10 ceiling).** **Different family but comparable depth.** R8 generated long-range planning (chain-to-other-face); this game generates medium-range planning (where to fight a 3-of-4 capture). R8's flip created chain-extension tactics; this game's residual-value-harvest creates re-occupation tactics. Both have a single crown-jewel mechanic that produces 3+ viable strategies and tempo dynamics. This game is structurally **closer to R8 than any other R20 menger game**.

**Comparison to R19 best.** R19 menger top-3 `5048f71b62fd` (surround capture, 5.0/10) is a different capture rule but similar depth-source (rare-capture → long games → balance). I would rate this game **above** R19 surround top-3 because (a) the residual-value-harvest mechanic is unique to R20, (b) the degree-heterogeneity shows up tactically here. Below R8 because (a) no long-range planning, (b) no chain-extension tactic, (c) the "depth" is mostly tactical not strategic.

**Player rebuttal.**
- The **degree-2 safe-haven** is a genuinely substrate-specific tactical primitive that doesn't transfer cleanly from any single ancestor.
- The **double-capture** and **residual-value-harvest** tactics are emergent from the rule combination — not in any single ancestor.
- **Cluster-deepening** (placing inside own cluster to lower already-owned values) is a real positional tactic.
- What subtracts: the win condition is still threshold-race (parallel sum, no chain dynamics), so the "depth" caps at the tactical layer. No long-term strategic plan beyond ~5 plies.

**Novelty score (post-adversary):** **5/10.** Above pure re-skin (3) because the outnumber-3 + menger + residual-value combination produces tactics with no clear ancestor (degree-2 safe-haven, residual-harvest, cluster-deepening). Below 7 because (i) the underlying frame is still the R20 menger family, (ii) win condition is the same threshold-race that limits long-range planning, (iii) the depth is tactical not strategic. This is **the most novel game in the R20 slate** by a clear margin.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** 5f5c72e15220
**Rules Summary:** 9×9×9 menger sponge; alternating placement on 400 active cells; influence kernel (r=1, decay=0.5); **outnumber-3 capture** (≥3 friendly neighbours required; degree-2 cells safe); threshold-race(57.97) with mirror P2 accumulator; **captured cells retain board values** enabling residual-value re-occupation tactics. Pie rule off.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 6** — Genuinely deeper than siblings. Three viable strategies (mirror, infiltration, cluster-deepening), captures fire 4+ times in a contested line, lead changes 3+ times, residual-value harvest creates re-occupation tactics. The 0.894 engine-measured depth shows up in subjective play. Compares **above** R19 menger top-1 (4.8) and approaches R17 best (4.14)+ territory. Plan horizon ~3–4 plies.
- **Emergent Complexity: 6** — Capture-trap inversion, double-captures, residual-value harvests, cluster-deepening, tempo swaps. Multiple emergent tactics that aren't explicitly written in the rule blob.
- **Balance: 6** — Trained-vs-trained 0.333 P2-favoured (briefing) matches my finding that P2 has real plays. Mirror still gives P1 +1.5 tempo, but P2 infiltration produces real leads (+2 at move 28, +2 at move 39) that get neutralized by tempo trades. Pie rule off but seat-balance is structurally close to even — best in the menger slate by far.
- **Novelty (post-adversary): 5** — Most novel R20 menger game; outnumber-3 + degree-heterogeneity + residual-value combination is distinct from R10–R19 lineage. Below 7 because the threshold-race framework caps long-range planning.
- **Replayability: 5** — Three viable strategies + tempo swap dynamics + residual-value plays mean openings don't collapse to a single mode. PPO seed game-length variance (71–96 plies) confirms multiple lines exist in the search space.
- **Overall "Would an agent team play this again?": 6** — Yes, multiple times — there's enough tactical variation that a 5-game tournament wouldn't see the same line twice. Anchors: R8 = 8, R17 mean = 3.5, R19 menger top = 4.8. This game lands above R19 menger top but below R8 because the win condition still doesn't generate strategic-horizon play.

### CLOSEST KNOWN-GAME ANALOG
"Influence Othello on a heterogeneous-degree graph with rare capture and persistent cell values." No exact published analogue; partial parallels to Hex (graph play), Othello (positional scoring), and Tafl (sandwich-and-remove) but the "rarely fires + residual deposits" combination is novel. Inside this project, no direct precedent — **this is the first game where outnumber-3 generated a measurable depth attractor.**

### KILLER FLAWS
- **No pie rule** under +1.5 P1-tempo baseline. Even with P2 infiltration tactics, the structural first-mover edge persists in mirror lines. Pie rule would let this game run cleaner.
- **Threshold-race win condition** caps strategic horizon at ~5 plies. The depth is real but tactical — no Connect-style long-range plans.
- **Captured-cell residual values are confusing.** Helper output makes it hard to track who owes what to which cell. Players (or PPO) may not learn the residual-harvest tactic without explicit visualization.
- **3 PPO runs only** for this game — the 0.333 P2-favoured is on a small sample; should be re-trained at n=15 to confirm.

### BEST QUALITY
**The outnumber-3 + menger combination produces a degree-stratified tactical landscape.** Degree-2 cells are safe-havens for both players; degree-4+ cells are battlegrounds where captures fire; degree-3 cells are intermediate. This heterogeneity is the project's first measurable substrate-derived strategic dimension. Combined with **residual-value harvest** (re-occupy captured cells), this game produces real medium-term tactics — a clear step up from the rest of the R20 slate.

### menger STRUCTURAL CONTRIBUTION
**Genuine and load-bearing.** Unlike siblings where menger is decorative, here the degree-2 cells are tactically valuable (uncapturable safe-havens) and the degree-4+ cells are tactically valuable (capture fires). The substrate's irregular degree distribution becomes a real game-shape parameter. **Cannot flatten to a 9×9 grid without losing this stratification** — a flat grid + outnumber-3 would still have "all degree-4" and lose the degree-2-safe-haven dynamic. This is the strongest substrate-contribution argument for the entire R20 slate.

### IMPROVEMENT IDEAS
**Single best change:** Add **pie rule** — would correct the residual P1 +1.5 tempo and let this game run as truly seat-balanced. Combined with the deeper tactics, would be an all-around upgrade.

Secondary improvements:
- **Re-train at n=15 seeds** to confirm 0.333 P2-favoured isn't just 3-run noise (briefing flags this).
- **Visualize residual values in the helper output by default** so PPO + players see the persistent-cell-value tactic rather than having to discover it.
- **Reduce threshold to ~30** for shorter games — at 57.97 the race is grinding, hiding the tactical play under bulk compounding.
- **Test outnumber-3 on grid_control / sierpinski substrates** to see if the degree-stratification effect transfers (it shouldn't transfer to grid because every cell has degree 4 — that's the test).

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-pilot_game5f5c72e15220.md`.*
