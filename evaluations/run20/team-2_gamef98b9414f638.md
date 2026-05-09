# Run 20 Agent-Team Eval — team-2 — Game f98b9414f638

**Team ID:** team-2
**Game ID:** f98b9414f638 (rank-5 by 15-seed mean GE 0.129, σ 0.089, depth 0.597, ELO 2407)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game f98b9414f638` (see `briefing_menger_f98b9414f638.md`).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube, 400 active cells per Menger sponge level-2. Same fractal substrate as the rest of the menger slate.

**Turn structure.** Alternating, 1 piece per turn. P1 first. **Max_turns = 89** (vs 100 for siblings — slightly shorter cap).

**Action space.** 730 actions = 729 placements + 1 pass. **No move actions.**

**Placement & capture.** Place at any empty active cell. Capture rule = **outnumber-2** (threshold 2). Same as `a6385d`/`b160`/`d1dbc6`.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). Same kernel.

**Win condition.** Threshold-race. Effective sum > **29.709** wins. **The threshold is half the siblings' 57.974 — the structural odd-one-out in this slate.** P2 mirror via `target_dimension_p2 = -1`. Max-turn timeout: highest sum.

**Pie rule.** Off.

**Degeneracy check.**
- No soft violations.
- The lower threshold (29.71 vs 57.97) directly halves game length: avg 38.8 plies vs 85 plies for siblings.
- gen-4 mutation off `4afa58f6b157`. Single PPO sample (n=12) in this finalization run.
- Largest finalization collapse (−0.159, σ = 0.089) — flagged in the project report's "5 things finalization changed our minds about" as a candidate for elite-carryover bias inflation. The original 3-seed GE was 0.288 (rank-2); the 15-seed GE is 0.129 (rank-5).

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — Symmetric mirror (truncated cross-corner build): P1 wins at move 31

Sequence: `182,546,101,465,263,627,20,384,344,708,425,303,506,222,587,141,668,60,164,564,173,555,191,537,200,528,209,519,227,492,236,501` (32 plies).

Engine output: `Done=True Winner=1` at step 31, P1 score = +30.000, P2 score = +28.000. **Threshold cleared by move 31** — half the length of siblings.

Plot:
- Moves 1–18: each player builds their (z-axis) column completely. P1 = (2,2,*) all 9, P2 = (6,6,*) all 9. After move 18 both at +17 (each column = 9 stones giving +17).
- Moves 19–28: each builds part of the (y-axis) line through their hub. P1 fills (2,0,2) → (2,5,2) plus (2,7,2). P2 fills (6,0,6) → (6,5,6) plus (6,7,6).
- Move 31: P1 plays (2,8,2)=236 — completes the y-line endpoint. P1 score ticks past 29.709 → **P1 wins**.

P1 reflection: with the threshold halved, the dominant strategy is the same column build but pruned. You don't need the full cross (49 score) — you only need ~30. One column (9 stones, +17) plus 7 perpendicular line stones (+13) is exactly enough. 16 plies of building, 32-ply game total. The half-ply tempo advantage is decisive here too.

P2 reflection: at threshold 29.71, every move counts double (in proportion to budget). P1's lead is more decisive — P1 reaches 30 before P2 because the games end before tempo can be "absorbed" by long accumulation.

### Game 2 — P2 invasion (test outnumber-2 punishment in the racier setting)

Probe: P2 plays (2,2,3)=263 at move 2. P1 plays (2,2,4)=344 at move 3. **outnumber-2 fires immediately** (same as `a6385d`/`d1dbc6`); P2 (2,2,3) cleared.

Plot:
- Same capture mechanism. The shorter race makes the lost stone proportionally more painful — losing 1 stone in a 30-ply game (budget 15 P2 plies) is ~7% of P2's resources, vs 3% in the 60-ply siblings.
- After the first capture, P2 is essentially out of the race. P1 reaches threshold by move 25–28.

### Game 3 — Adversarial: P2 commits to mirror but tries the *only* asymmetry — open at (6,6,6) directly without P1 grabbing prime cells

Probe: same mirror as Game 1, P1 wins at move 31. *No genuinely distinct P2 strategy exists in this game* — strategic-diversity-0.333 (lowest in slate) is empirical reality. The shorter game reduces the time for any non-mirror strategy to bear fruit.

### Strategy guides

**P1 (offence/threshold push):** Hub-cross at (2,2,2). Build one full column (9 stones, +17). Extend along one perpendicular line until +30 reached (~6 more stones). Game over by move 30.

**P2 (defence + threshold contest):** Mirror at (6,6,6). Avoid invasion — outnumber-2 still punishes immediately. Lose by tempo in ~30 plies.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Effectively one: hub-cross. Strategic-diversity 0.333 (lowest in slate) confirms this empirically. The lower threshold removes the late-game capture-and-recapture phase that gives `5f5c72e15220` its strategic richness.

**Counter-play.** None functional. Mirror loses; invasion loses faster.

**Short-term vs long-term.** Short-term only. 30-ply games leave no room for medium-term strategy. The decisive moment is move 1 (claim the hub) and the rest is mechanical.

**Emergent concepts observed.**
- **Truncated hub-cross.** Same emergent pattern as siblings, just stopped halfway. The +17-per-column scoring is decisive — one column cleared, win.
- **Tempo-additivity** in a tighter window. P1's half-ply lead resolves to a ~+2 score differential over 30 plies (vs ~+4 over 60 plies in siblings) — but the threshold is also half, so the relative tempo matters more.
- **Capture-as-defender's-tool.** Same.

**Does menger matter?** Constraint-only role, *less prominent here* because the game is too short to traverse the substrate. With only 30 plies of placement total (15 each), neither side strays far from the corner sub-cube; the rest of the 400 active cells are wasted board.

**Does the propagation kernel matter?** Same r=1 kernel. With the lower threshold, the kernel still drives clustering, but the game ends before kernel decisions matter at the cluster-extension stage.

**Capture-rule contribution.** Same (outnumber-2 punishes invasion). The lower threshold means *one captured stone* is more decisive than in siblings — losing 1 stone of 15 (7%) vs losing 1 stone of 30 (3%).

**First-mover advantage / seat balance.** Trained-vs-trained 0.500 (balanced) is in some tension with my 3 trials all favouring P1. The balanced PPO result suggests PPO sometimes exploits a non-mirror P2 line I don't see; alternatively, with only 12 PPO runs and short games, the ratio has wide CI. **My empirical view: P1-favoured by tempo, same magnitude as `a6385d`.**

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Argument:

(a) **Threshold-race influence games** — same family as siblings, just with a lower threshold target. The lower target doesn't change the kernel.

(b) **outnumber-2 capture** — same as siblings.

(c) **The combination "outnumber-2 + influence(r=1) + threshold-race(29.71)"** — the only differentiator from siblings is the threshold parameter. **This is a parameter tweak, not a structurally novel rule.** R19 didn't have a threshold-29 menger game; R17 didn't have menger games at all. So technically novel within the corpus, but only as a 1-parameter variant.

(d) **Menger substrate.** Same constraint-only role as siblings.

(e) **Expert-transfer test.** A Reversi player who already understands `a6385d` would understand this in 30 seconds: "same game, half the threshold, half the length."

**Closest known-game analogue:** A truncated version of `a6385db22c0b`. Functionally a "speed Reversi-Race" in the menger family.

**Comparison to R8's Connection Go (8/10 ceiling).** Different family, much thinner. R8's connection wins generated genuine multi-strategy depth; f98b's threshold-29 race resolves before such depth can develop.

**Comparison to R19 best.** R19's menger top (4.8) was outnumber-2 + influence + threshold-race at the longer threshold. f98b is the same family with a tighter timer, which *strictly* reduces strategic depth.

**Player rebuttal.**
- The lower threshold compresses the game but does not produce novel strategic content.
- All emergent concepts from siblings (hub-cross, capture-defence, tempo) appear here, just with less time to play out.
- The strategic-diversity-0.333 measurement is consistent with my finding: only one strategy is viable, less than siblings' implicit two.
- The largest GE collapse (−0.159) in finalization is consistent with elite-carryover bias on a thin game — easy to look good with small samples, harder under wide-seed noise.

**Novelty score (post-adversary):** **2/10.** Above pure re-skin (1) only by virtue of the slightly different threshold parameter. Below 3 because it's *strictly thinner* than the siblings — same playbook, less room to play, and the depth metric (0.597, lowest in menger top-5) is aligned with this thinner-by-design feature.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** f98b9414f638
**Rules Summary:** Speed-version of the menger threshold race. Place stones; influence accumulates; outnumber-2 captures invasions; first to **+29.71** wins. Same substrate/kernel as `a6385d` but with half the threshold target → half the game length.
**Substrate:** menger, axis 9, 400/729, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 3** — Engine 0.597 (lowest in menger top-5) is the most accurate self-measurement in the slate. With ~30-ply games and a single viable strategy, depth is bounded above by the rule-set complexity. Anchor: below `a6385d`/`b160`/`d1dbc6` (4) because shorter games strictly remove strategic content.
- **Emergent Complexity: 3** — Same emergent concepts as siblings, but truncated. Hub-cross builder and capture-as-defence appear, but the late-game phase that would expose more complex patterns (multiple captures, recaptures, score-zeroing) doesn't happen.
- **Balance: 4** — Trained 0.500 (balanced) but my trials all favour P1. The conflict suggests a balance imbalance the metric doesn't capture (or one I'm missing). Anchor: 4 reflects "balanced per metric, P1-leaning empirically." Pie rule off; no in-game balance lever.
- **Novelty (post-adversary): 2** — see Phase 4. Strictly a parameter tweak vs siblings. Largest finalization collapse in slate suggests elite-carryover bias inflated the original GE.
- **Replayability: 3** — Same as siblings + thinner. Strategy collapses to one mostly-mechanical playbook in 30 plies.
- **Overall "Would an agent team play this again?": 3** — Once: yes for the threshold-tightening data point. Twice: no — same game compressed. Anchor: at the floor of R19 production (4.375) because of the strict-thinner-than-siblings property.

### CLOSEST KNOWN-GAME ANALOG
"Speed Reversi-Race-with-Cluster-Capture on a Menger sponge." A 1-parameter variant of `a6385db22c0b`'s family.

### KILLER FLAWS
- **Largest finalization collapse in slate (−0.159).** Flagged as a candidate for elite-carryover bias inflation. The 0.288 → 0.129 GE drop indicates the early seed-runs got a lucky basin.
- **Threshold too low for strategic content to develop.** 30-ply games are too short for the full hub-cross to play out, leaving the game in a thin truncated state.
- **strategic-diversity 0.333** (lowest in slate) — only one viable line.
- **Pie rule OFF** + tempo-driven P1 advantage. Same as siblings.
- **No structural novelty vs `a6385d`.** Same kernel, smaller threshold parameter.

### BEST QUALITY
**The fastest game in the slate.** As a *training-efficiency benchmark*, f98b is excellent — short games mean fast PPO convergence. As a *game to play*, it loses the late-game strategic content that gives the longer-threshold siblings their (modest) appeal.

### menger STRUCTURAL CONTRIBUTION
**Less than siblings.** With 30-ply games and ~15 placements per side, neither player traverses much of the 400 active cells. The Menger sponge is functionally reduced to 1 corner sub-cube + 1 partial spine. The fractal hole pattern is irrelevant for these short games — players don't ever need to cross holes.

### IMPROVEMENT IDEAS
**Single best change:** **Restore threshold to ~57.97** (matching siblings) to give the strategic content room to develop. The lower threshold is the single intervention that distinguishes this game from `a6385d`, and it's the wrong intervention.

Secondary improvements:
- Pie rule ON.
- If keeping the lower threshold, *also* lower max_turns to 50 to reflect the actual game length and avoid wasting PPO training on idle plies.
- Test whether the elite-carryover bias hypothesis is correct: re-score this game with explicit no-elite-carryover and see if the GE-Δ shrinks below −0.05.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-2_gamef98b9414f638.md`.*
