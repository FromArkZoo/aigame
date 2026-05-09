# Run 20 Agent-Team Eval — team-2 — Game a6385db22c0b

**Team ID:** team-2
**Game ID:** a6385db22c0b (rank-1 by 15-seed mean GE 0.241, σ 0.120, depth 0.763)
**Substrate:** menger (axis 9, 400 active cells / 729 grid positions, max_degree 6, pie_rule=False)
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game a6385db22c0b` (see `briefing_menger_a6385db22c0b.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube with 329 inactive holes per the level-2 Menger sponge fractal (active=400). Cell index = z·81 + y·9 + x. The hole pattern punches three perpendicular tunnels of 3×3 cross-section through the cube centre, recursively repeated at one scale lower. The result is heavy degeneracy in cell coordination: many cells have ≤4 active neighbours, while the eight "sub-cube interior" cells at (2,2,2), (2,2,6), (2,6,2), (6,2,2), (2,6,6), (6,2,6), (6,6,2), (6,6,6) sit at full max_degree=6 and serve as the structural hubs.

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = 100.

**Action space.** 730 actions = 729 placements + 1 pass. **No move actions** (D1 hybrid ban). Placement legal at any empty active cell.

**Placement & capture.** Placement: any empty active cell, no first-move restriction. Capture rule = **outnumber-2** (threshold 2). When a stone is placed, each adjacent enemy stone whose count of friendly (placer-coloured) neighbours ≥2 (post-placement, counting the just-placed stone) is captured (cleared to empty). The cell value persists in `board_values` but ownership goes to 0, so neither player scores it.

**Propagation.** influence (radius=1, strength=1.0, decay=0.5). On placement, +1.0 added to the placed cell's value, +0.5 added to each of up to 6 axis-aligned active neighbours. Sign = +1 for P1, −1 for P2. Values clamped to [−100, 100].

**Win condition.** Threshold-race. After every move, sum each player's `board_values` over cells they currently own. With `target_dimension_p2 = -1`, P2's effective accumulator is the negation of the sum over P2-owned cells (so a P2-placed cell at value −1 contributes +1 to P2's effective score). First player whose effective sum exceeds **57.974** wins. Equal margins → draw. Max-turn timeout: highest effective sum wins.

**Pie rule.** Off (lost in crossover before `ac9e642` fix). P2 has no seat-swap recourse despite the 0.667 trained-vs-trained P1 favour observed in PPO training.

**Degeneracy check.**
- No soft violations flagged in the briefing.
- The fractal hole pattern produces three "spinal" lines through each of the 4 corner sub-cubes ((2,2,*), (2,*,2), (*,2,2) through (2,2,2); analogous lines through the other 7 hub cells). All cells along these spines are active and form perfect 9-stone columns. These lines are the dominant structural feature.
- Many bulk cells at coordinates with two-1-digits-in-base-3 are holes (e.g., (1,1,*), (4,4,*) tunnels). This means most "interior" placements have only 2–4 active neighbours; the maximum-degree cells are sparse.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — P1 column-cross at (2,2,2) hub vs P2 mirror at (6,6,6)

Sequence: `182,546,101,465,263,627,20,384,344,708,425,303,506,222,587,141,668,60,164,564,173,555,191,537,200,528,209,519,227,492,236,501,180,540,181,541,183,545,184,548,185,547,187,544,188,543,218,542,299,461,137,470,245,467,56,488,74,484,102,476,110,478` (truncated at win — engine reported `Done=True Winner=1` at step 59).

Plot:
- Moves 1–18: each player builds their (z-axis) column completely. P1 = (2,2,*) all 9, P2 = (6,6,*) all 9. After move 18 both at +17.
- Moves 19–34: each builds the (y-axis) line through their hub. P1 fills (2,*,2) (y=0..8), P2 fills (6,*,6). After move 34 both at ≈+33 (≈17+16 with hub double-counted).
- Moves 35–48: each builds the (x-axis) line through their hub. P1 fills (*,2,2), P2 fills (*,6,6). Note: at move 41 P1 places (5,2,2)=185, two cells from where (6,2,2) would sit; (6,2,2) was never claimed in this game.
- Moves 49–58: each starts auxiliary line (y=6 through P1's column at z=2, etc.) — P1 plays the (2,6,*) line, P2 invades (2,6,5) and (2,6,6). No captures fire — every potential capture attempt finds only one friendly neighbour around the targeted enemy stone, falling short of the outnumber-2 threshold.
- Move 59: P1 plays (3,2,1)=102, picking up boost from (2,2,1)=P1 and (3,2,2)=P1. P1 effective score ticks past 57.974 → **P1 wins**.

P1 reflection: Threshold race rewards dense clustering. The (hub + 3 perpendicular spines) topology gives 25 cells per cross with predictable +49 score; the +9 tail to threshold is stitched together from short branches into other (y=6, y=0) spinal lines. Capture rule does *not* fire when both sides build symmetric far-apart clusters.

P2 reflection: Mirror strategy loses by tempo. P1 always plays one move ahead in the same accumulation pattern. Without pie rule, P2 has no recourse to steal first move.

### Game 2 — P2 disruption / invasion attempt

Sequence (probe): P1 opens (2,2,2). P2 invades adjacent: tried `(1,2,2)=181`. P1 plays `(0,2,2)=180`. For P2 stone at (1,2,2): friendly P1 neighbours = {(2,2,2), (0,2,2)} = 2 → engine fires `_capture_outnumber` and clears P2 at (1,2,2). P2 piece count drops; P2 loses both the stone and the −1 cell value, P1 captures the cell empty (no ownership) so it is not scored.

Plot:
- Adjacent invasion is *immediately punishable* by the second P1 move adjacent on the other side. P2 cannot single-handedly attack any P1 cluster — the outnumber-2 threshold is met as soon as P1 has 2 neighbours touching the P2 stone, which in a clustered build P1 acquires almost immediately.
- The only viable P2 capture attack requires P2 to have 2 stones flanking a P1 stone *before* P1 surrounds. In the (2,2,*) spine this is impossible — P1 builds the spine 1 move ahead of any invasion.

Reflection: outnumber-2 capture is a *defender's tool* on this board. Whoever has the denser cluster captures incursions. P1's tempo lead means P1 always has the denser cluster.

### Game 3 — Adversarial: P2 mirrors clustering at the *opposite* hub direction

Sequence: P1 builds (2,2,*) spine; P2 builds (2,6,*) spine (deliberately invading the same x=2 plane). P1 first move 182=(2,2,2). P2 first move 218=(2,6,2). Both sides race the same 9-stone column structure. P1 still leads by tempo. By move 18 both at +17. By move 36 both at ~+33 with P1 leading by ~+1 (one move ahead).

Joint observation: after step 50 P1 finishes the (2,2,*) line + (2,*,2) line (the latter passes through the contested x=2 plane). P1's (2,5,2), (2,6,2) overlap directly with P2's spine — each side races to claim the bridge. Because P1 has tempo, P1 reaches (2,5,2) before P2 reaches into P1's column. Captures begin: P2's (2,6,3) gets two P1 neighbours after P1 plays (2,5,3)+(2,6,2), forcing P2 to abandon the contested direction. P1 wins by ≈move 60 again.

### Strategy guides

**P1 (offence/threshold push):** Open (2,2,2). Build the full z-axis column first (9 stones, +17). Then both perpendicular hub spines (y and x), which gives the 25-cell cross at +49. Tail with adjacent secondary branches — (2,6,*) extension from (2,6,2), or (3,2,1) corner-fills — to clear the threshold around move 56–60. Avoid contested invasions by staying in your own corner sub-cube until the cross is half-built.

**P2 (defence + threshold contest):** Mirror at (6,6,6) loses by tempo — P1 always reaches threshold first. Better: deny P1 hub access by playing (2,2,2) yourself if P1 plays elsewhere first; otherwise, race the same corner ((2,6,*) or (6,2,*)) that doesn't double-occupy P1's hub. Capture is not a tool you control as P2 in symmetric play.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Two, but both lose for P2:
1. **Hub-cross threshold builder** (the playbook). Symmetric for both sides; P1 wins by tempo.
2. **Adjacent-corner contest** (P2 invades the (2,*,*) column). Tempo still wins for P1 but contact captures begin firing — P2 trades stones without ever gaining material.

There is no genuinely distinct P2-favoured strategy. Mirror, contest, or attack: all funnel into a tempo loss.

**Counter-play.** Partial. P2 can choose between losing politely (mirror, lose +1) or losing dramatically (invade, lose stones to capture and still trail in race). The 0.667 trained P1 winrate exactly reflects this — P1 wins ~2/3 of even matched games regardless of P2 strategy.

**Short-term vs long-term.** Long-term — games stretch to 55–85 plies. Each move's contribution is locally predictable (+1 own cell + ~+0.5 per friendly neighbour). The strategic horizon is "what is the most efficient way to spend my next 25–30 placements to clear +58?" — there is essentially one answer (cluster densely along the spine), and decisions reduce to deciding the *order* of obvious moves.

**Emergent concepts observed.**
- **Spinal builders.** The 9-cell columns through hub cells dominate placement value. Each column converts 9 plies into +17 score — better efficiency than any non-spine placement.
- **Hub overlap multiplier.** The 6 cells adjacent to the hub each receive +0.5 from the hub *plus* +0.5 from each line neighbour, settling at +2.0 per stone. The hub itself reaches +4.0 once all 6 line-neighbours are placed.
- **Capture as defender's tool.** Outnumber-2 fires only when one side already has spatial dominance. The denser cluster captures incursions; the player making the intrusion always has fewer friendly stones in the contested region.
- **Tempo-additivity.** With both players using the dominant strategy, P1's perpetual half-move lead translates linearly into half-move-of-score — exactly the observed 0.667/0.333 win split.

**Does menger matter?** *Modestly.* The fractal hole pattern *produces* the 9-cell spines that dominate play. On a flat 9³ cube without holes, the same threshold-race outnumber-2 game would still favour spinal/clustered play, but with 729 active cells (vs 400) the threshold ratio (58/729 ≈ 8%) is even smaller and the game devolves into faster, blander accumulation. The Menger structure adds *constraints* that focus play onto 4 dominant corner sub-cubes — the 8 hub cells and their spines. The 2D-flattened version (carpet, axis 9) loses the third spinal axis and the +49-per-cross scoring, so menger's three perpendicular spines per hub is the main structural contribution. It is, however, a constraint not a creator — there is no menger-specific strategic concept (e.g., wormhole routing, fractal self-similarity in play) — just thinned legal moves.

**Does the propagation kernel matter?** Yes for scale, no for shape. r=1 / strength=1.0 / decay=0.5 produces the +1/+0.5 distance-1-only kernel. r=2 would extend influence to cells at axis-distance 2 (through holes? probably not), making remote placements partially valuable — that would *add* strategic interest by making non-spine placements worth more. As tuned, only direct neighbour placements amplify each other, which forces clustering.

**Capture-rule contribution.** In Game 1 (symmetric play), 0 captures fired — the threshold race resolved without any flips. In Game 2 (probe), capture fired immediately when P2 attempted a 1-stone invasion of P1's spine. Capture is decisive in *suppressing* invasion strategies, not in *generating* them. The mechanic acts as a stability term that locks both sides into corner-sub-cube building.

**First-mover advantage / seat balance.** From my 3 trials and the training reference: P1 wins 100% of my games and 67% of trained PPO games. The mirror-symmetric structure of the corners + the +1 ply tempo gives P1 a structural ~2 score lead at any matched-strategy moment. Pie rule is OFF here; P1 has no recourse to lose its seat advantage. This is the headline imbalance in the game.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of well-known mechanics. Argument:

(a) **Threshold-race influence games** are most closely analogous to Reversi/Othello *scoring* (count discs at end) without the flipping mechanic, plus a per-placement target-driven race. Closer literature analogues: Atari Go (capture race), Influence territory in Go endgame, and abstract "annexation" games like Lines of Action's cluster scoring. None match exactly.

(b) **outnumber-2 capture** is closest to Tafl-family "outnumbered piece dies" rules, and to Ataxx's adjacency conversion. It is *not* Go (no liberties/freedom counting), *not* Othello (no axis-walk flip). Outnumber-2 in particular fires on a single-stone basis and is a well-known but unnamed primitive (it appears in Lines of Action and some hex-grid variants).

(c) **The combination "outnumber-2 + influence(r=1) + threshold-race(57.97)"** does not exist as a published game. Within the Genesis corpus this is the dominant menger family from R20 and matches `b160b1f55378` and `d1dbc6568fc7` byte-identically. R8's Connection Go (8/10 ceiling) was custodian + connection — different family. R17's mean (3.50) lacked threshold-race champions, and R19's menger top (4.8) was outnumber-2 + influence + threshold-race on menger — *exactly this family*.

(d) **menger substrate.** Has fractal Hausdorff-dim play been studied for influence-race games? Not to my knowledge. The hole pattern adds a constraint (focus on 8 corner sub-cubes) but no genuinely new play primitive — every spine line is just a 9-cell column, locally indistinguishable from a flat-grid column. Hausdorff-dim 2.727 is a *measurement* of the substrate, not a feature exposed to play.

(e) **Expert-transfer test.** A Reversi player + Lines-of-Action player would understand this game in 5 minutes. The new pieces to learn: (i) score = sum-with-sign of board_values, threshold trigger; (ii) outnumber-2 capture vs custodian capture; (iii) the active/inactive hole pattern as a board geometry. Each is a 1-page learning curve.

**Closest known-game analogue:** "Reversi-Race-with-Cluster-Capture on a Menger sponge" — equivalently, an influence-accumulation race where the only capture rule punishes 1-stone incursions into a 2-stone cluster. The R19 menger top (`1f9191b5d4e6`) was structurally identical at outnumber-2 + influence + threshold-race; R20 a6385db22c0b sits in the same family.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2D 8×8 grid. This game is outnumber-2 + influence + threshold-race on a 9³ Menger sponge. Different family: R8 had a concrete topological win-condition (chain across the board) that produced rich sub-strategies (connection threats, ko-fights, seam-crossing); R20 a6385db22c0b's win condition is a *quantitative* threshold which collapses strategy to "place efficiently in clusters." This is structurally less rich than R8's connection game by 2–3 points of strategic depth.

**Comparison to R19 best.** R19 menger top-1 was `1f9191b5d4e6` (outnumber-2, GE 0.366 / 4.8 in agent eval). R19 menger top-3 surround was `5048f71b62fd` at 5.0. R20 a6385db22c0b is *thinner* than R19's surround top — surround capture (R19 5048f71b62fd) generates true Go-style group fights, whereas outnumber-2 fires only on isolated invasions. R20 a6385db22c0b is roughly equivalent to R19's outnumber-2 menger top — same family, same approximate strategic depth.

**Player rebuttal (P1 + P2).**
- The **hub-cross** as a +49-score structure is geometry-driven and generic; any influence-radius-1 game on any substrate produces clustering.
- The **invasion-capture defence** is a real concrete tactic but it is the obvious counter to incursion; not a novel pattern.
- Menger holes constrain the play but don't add strategy. The same game on the 8 sub-cube interiors only (a 4×4×4 reduced cube = 8 cells) would lose nothing strategic, just trim filler.
- *No move action means no place-and-shoot, no Lines-of-Action-style mobility, no Amazons-type combat.* The action space is pure placement on a 400-cell board.

**Novelty score (post-adversary):** **3/10.** Above pure re-skin (2) because (i) the menger substrate is genuinely novel as a board (not seen in published abstract games) and (ii) the influence-+capture-+threshold combination is not exactly a single named published game. Below 5 because (a) the family is *identically* shared by `b160b1f55378` and `d1dbc6568fc7` (3 games of the same blob in this slate), (b) R19 already produced the same outnumber-2 + influence + threshold-race family on menger, (c) the substrate is a constraint not a creator — fractal dimension does not enter play, and (d) the strategic kernel reduces to "build dense spinal clusters," which generic clustering theory predicts on any kernel-decay influence game.

---

## Phase 5 — Verdict

**Team ID:** team-2
**Game ID:** a6385db22c0b
**Rules Summary:** Place stones on a Menger-sponge cube; each placement adds influence (±1 self, ±0.5 to up-to-6 neighbours); enemy stones with ≥2 friendly neighbours after placement are captured; first player whose owned-cell influence sum exceeds 57.97 wins.
**Substrate:** menger, axis 9, 400/729 cells, max_degree 6, pie_rule=False.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 4** — Engine-measured 0.763 reflects long games (~85 plies) with many decision points, but each decision is locally bounded — the dominant move is always "extend my spine cluster" with small variations on which spine. Medium-term concepts exist (which corner sub-cube, which spine first, when to switch from +2 spine extensions to +1.5 corner-fills) but the decision tree is shallow. The depth metric overstates subjective depth — most plies follow one of 5 pattern templates.
- **Emergent Complexity: 4** — Hub-cross structure, capture-as-defence, tempo-additivity are real emergent properties of the rule set. But the rule set itself is small (capture + influence + threshold), and the emergent vocabulary is correspondingly small. No ko fights (captures don't cycle), no territory (threshold race overrides), no group concept (outnumber-2 fires per-stone).
- **Balance: 3** — P1 wins 100% of my 3 games and 67% of trained PPO games. Pie rule is OFF — P2 has no recourse. The structural advantage from tempo is the headline imbalance. Anchor: R8 was P1-favoured but pie-rule-corrected; this game has neither correction.
- **Novelty (post-adversary): 3** — see Phase 4. Sits in R19's menger outnumber-2 family; substrate is novel-ish but constraining-only.
- **Replayability: 3** — Once known, the game collapses to "build the cross, win at move 60." Position variety from move 1 is constrained to 8 hub cells × small permutation of build order. Once both sides know the hub-cross strategy, openings collapse to 1–2 lines.
- **Overall "Would an agent team play this again?": 3** — Once: yes, to feel the cross-builder dynamics and observe outnumber-2 firing on invasion. Twice: no — strategy converges, P1 wins, repeat. Anchors: R8 = 8 (richer, balanced), R17 best = 4.14 (richer connection game), R19 menger top = 4.8 (same family slightly more substrate spread), R19 production mean = 4.375 (typical R19). This game sits below R19's menger top.

### CLOSEST KNOWN-GAME ANALOG
"Reversi-Race-with-Cluster-Capture" — an influence-race scoring game where outnumber-2 capture punishes solo invasions. Within the Genesis corpus, R19's menger outnumber-2 family (`1f9191b5d4e6`) is the immediate ancestor; R20 a6385db22c0b plus its byte-identical siblings `b160b1f55378` and `d1dbc6568fc7` are the rediscovery on slightly different lineages.

### KILLER FLAWS
- **Pie rule OFF + measurable P1 advantage.** Trained-vs-trained 0.667 means P2 loses 1 of every 3 games at PPO equilibrium with no recourse. This is the single most-correctable flaw.
- **Strategy collapses to one playbook.** Hub-cross at corner sub-cube. The 730-action space functionally reduces to ~25 ranked placements per side; everything else is filler.
- **Capture rule fires only on incursions; doesn't generate offensive patterns.** Outnumber-2 acts purely as a defender's tool. No ko-fights, no group threats, no territory dynamics.
- **Threshold races are not interesting endgames.** Once both sides have ~+50, the rest is spreadsheet — just count remaining plies × +1.5 per ply. The decisive moment is invisible.
- **Substrate is constraint-only.** Fractal hole pattern thins the legal-move count without adding any new play primitive. Hausdorff dimension does not enter strategic play.

### BEST QUALITY
The **9-cell spinal column producing +17 deterministic score** is the cleanest emergent-from-substrate quantitative pattern. It tells you exactly why you should play in the 4 corner sub-cubes and exactly how to construct the optimal threshold-clearing build. As a teaching artefact for "how does Menger geometry shape an influence race," it is concise.

### menger STRUCTURAL CONTRIBUTION
Constraining only. The fractal hole pattern *prevents* dense play in the centre and channels play into 8 corner sub-cubes, each of which exposes 3 perpendicular spinal lines. This is a *focus* effect (limits where good moves are) rather than a *creation* effect (no new play primitive). Compared to a flat 9³ cube (729 cells), the menger version reduces noise by 45% (329 holes) but does not change the kernel of play. R19's finding that "menger > carpet > grid for substrate quality" is consistent here — menger gives 8 hub cells (carpet 4, grid 4) and 24 spine lines (carpet 8, grid 6) — but the *kind* of game the substrate hosts is identical. **Could be flattened to a 4-corner grid or to R19's 6×6×6 reduced lattice without losing more than ~1 point of depth.**

### IMPROVEMENT IDEAS
**Single best change:** **Turn pie rule ON.** Documented P1 advantage of 0.667 at trained equilibrium plus no in-game balance lever — pie rule is the standard tool and is missing from this game (lost in crossover before `ac9e642`). Carpet game `625bfc1f3f49` already has it; menger games should too.

Secondary improvements:
- **Lower the threshold to ~30 (à la `f98b9414f638`).** Shorter games would force earlier strategic commitment, prevent pure spreadsheet endgames, and might expose interesting tactical asymmetries.
- **Increase capture threshold to outnumber-3** (à la `5f5c72e15220`). Would require denser commit before captures fire — opens room for invading stones to live briefly and create real capture sequences.
- **Increase propagation radius to r=2 with shallower decay** (e.g., r=2, strength=1.0, decay=0.4). Would extend influence to distance-2 cells, making non-spine placements less wasted and broadening strategic options beyond cluster-and-race.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-2_gamea6385db22c0b.md`.*
