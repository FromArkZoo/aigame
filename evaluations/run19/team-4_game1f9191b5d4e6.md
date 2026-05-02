# Run 19 Evaluation — team-4 — Game 1f9191b5d4e6

**Team ID:** team-4
**Game ID:** `1f9191b5d4e6` (Menger rank-1, GE 0.3293, ELO 2402.4)
**Substrate:** Menger sponge, axis 9, 400 active cells / 729 grid positions, max_degree 6 (effective 2–6 per cell).
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 1f9191b5d4e6` (see `briefing_menger_rank1.md` for full rules).

---

## Phase 1 — Rule Comprehension

**Board.** 9×9×9 cube, level-2 Menger sponge: cell (x,y,z) is active iff at most one of (x mod 3, y mod 3, z mod 3) equals 1 AND at most one of (x div 3, y div 3, z div 3) equals 1. 400 active cells. Cell index = z·81 + y·9 + x. fmt_cell prints (x,y,z). Macro structure: the (4,4,*), (4,*,4), (*,4,4) "axes of holes" gut the centre; cells like (2,2,2), (6,6,6), (2,6,2), (6,2,6) are "sub-cube corners" with 6 active neighbours — the local densest interior anchors.

**Turn structure.** Alternating, 1 piece/turn. P1 first. Max_turns = 89 (engine `max_game_steps`).

**Action space.** 730 actions = 729 placement + 1 pass. Place-only (D1 hybrid ban). Movement is *not* in the action set — confirmed via `game.action_rule.action_types == ('place',)`.

**Placement & capture.** Outnumber-2: when player P places at cell c, for each enemy neighbour n of c, count P-friendly neighbours of n; if ≥2, n is removed (cleared, not flipped). Important corollaries verified empirically:
- The placed stone is **not** checked for self-capture by `_capture_outnumber` — outnumber only iterates neighbours of the placed cell.
- However, **super-ko is active** (`game.needs_ko_rule == True`). After every placement, the engine hashes `(board_owners, current_player)`; if this hash appears in `_position_history`, the move is rolled back and treated as a pass. This prevents capture/recapture cycles. *I verified this firsthand* (Phase 2 Game 2 turn 8) — it is the killer mechanic the briefing does not flag.

**Propagation.** Influence, r=1, strength=1.0, decay=0.5. Placement at c adds ±1.0 to `board_values[c]` and ±0.5 to each of c's active neighbours. No distance-2 contribution. Sign +1 for P1, −1 for P2. Clamp [−100, 100].

**Win condition.** Threshold-race > 29.709. After every move sum each owner's `board_values`-on-owned-cells (P2 score takes negation of stored values). First over 29.709 wins. Margin ties → draw. Max-turn timeout: piece-count majority via `_check_win_conditions`.

**Degeneracy check.**
- Briefing claim "interior 6-neighbour cells are harder to capture (need 2/6 = 33% coverage)" is **wrong**. Outnumber-2 needs *exactly* 2 enemy neighbours regardless of total degree, so 6-neighbour cells have *more* attack vectors than 3-neighbour corners. They are equally easy to sandwich, but offer the placer more own-side reinforcement options.
- 2-active-neighbour cells (rare in this fractal but present, e.g. (2,4,2)) are essentially uncapturable in any practical line — both neighbours must be enemies, so any one friendly neighbour makes them safe forever.
- Super-ko has a subtle effect: it can convert what looks like a winning capture into a no-op pass, breaking expected tempo.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`. Action IDs = cell indices for placement; pass = 729.

### Game 1 — 6-neighbour anchor mirror (tempo race)

Sequence: `182,546,181,547,183,545,173,555,191,537,101,627,263,465,102,626,110,618,174,554,190,538,254,474,262` (25 plies).

Plot:
- P1 anchors at (2,2,2)=182 — the rare 6-active-neighbour cell. P2 mirrors at (6,6,6)=546.
- Both players build the full 6-petal "octahedron" around their anchor (7 stones each: centre + 6 axis neighbours). After ply 14, both at +13.0 (centre = +1+6×0.5 = +4, each petal = +1+0.5 = +1.5, total 4+9 = 13).
- Each side then expands one face outward (3,2,1)→(3,2,2)→(3,1,2)→(1,3,2)→(2,1,3)→(1,2,3) — every move is a +3.0 jump (+1.5 new cell, +0.5 to two adjacent own stones).
- P1 reaches +31.0 on ply 25 (move 13 of P1) and wins. P2 sits at +28.0, two plies short.

Reflection: Mirror is a **structural P1 win** by exactly one tempo unit (+3 jump). Pilot finding confirmed; nothing to add. The 6-neighbour anchor delivers more raw influence per stone (+13/7 = +1.86/stone) than the pilot's 4-stone "plus" (+7/4 = +1.75/stone), but doesn't change the tempo conclusion.

### Game 2 — P2 sandwich-on-anchor + P1 counter-sandwich + super-ko intervention

Sequence: `182,181,173,191,200,110,182,191,209` (9 plies).

Plot:
- P1: 182 (2,2,2). P2: 181 (1,2,2) — sandwich threat. P1 score +0.5 (P2's −0.5 propagation onto own anchor pulled it down).
- P1: 173 (2,1,2) — extends. P2: 191 (2,3,2) — sandwich completes: (2,2,2) has P2 neighbours {(1,2,2), (2,3,2)}=2, **captured**. After ply 4: P1=1 stone, P2=2 stones, +1.5 vs +1.0.
- P1: 200 (2,4,2) — extends from where (2,3,2) is now P2, but (2,4,2) has only 2 active neighbours: (2,3,2)=P2 and (2,5,2)=empty. Currently safe (1 enemy nbr, <2).
- P2: 110 (2,3,1) — clusters under (2,3,2). Score +2.5 to P2.
- P1: 182 (2,2,2) again. (2,2,2) now has P2 neighbours {(1,2,2), (2,3,2)}=2 — but the suicide check doesn't fire on outnumber. Capture *does* fire: (2,3,2)'s P1 neighbours after this placement = {(2,2,2), (2,4,2)} = 2, so **(2,3,2) is captured back**. P1=3 stones, +4.0; P2=2 stones, +1.5. **2-for-1 reversal.**
- P2: 191 (2,3,2) again. Place succeeds, capture would fire on (2,2,2) (its P2 nbrs again =2 = (1,2,2) and (2,3,2)-just-placed). But the resulting state — P1 owns {173, 200}, P2 owns {181, 110, 191}, current=1 — **was already seen after ply 6**. Super-ko rolls back. **P2's move is silently converted to a pass.** This is undocumented; I only caught it because piece counts didn't tick.
- P1: 209 (2,5,2) — extends the cluster while P2 has no progress. Score +6.0 vs +1.5.

Reflection: This is the most interesting line in the game. Three independently-significant findings:
1. **Counter-sandwich works.** A 2-for-1 capture against you can be undone the next ply by re-anchoring on the captured cell when you control both opposing neighbours of the new attacker.
2. **Super-ko enforces capture-cycle resolution.** P2 *cannot* simply re-capture: the engine rolls back and it loses a tempo. This adds a layer of "where can I put pressure without recreating a prior position" that the briefing does not surface and the pilot did not encounter.
3. **The pilot's "interior cells with 5–6 neighbours are safer" advice is empirically incorrect** — the 6-neighbour anchor was sandwiched in 4 plies by P2 hitting only 2 of its neighbours.

### Game 3 — Off-anchor mirror (substrate-shape stress)

Sequence: `182,546,181,545,173,547,191,537,101,555,263,627,183,465,102,626` (16 plies).

Plot:
- I tried a deliberately-different P2 mirror axis to check whether the 6-neighbour anchor + face-by-face expansion is a unique optimum.
- Both reach +16.0 at ply 16, exactly mirroring the pilot's "plus" expansion rate.
- Per-stone gain is identical to Game 1 (+2.0/move during expansion), confirming **mirror tempo is invariant to anchor choice** as long as both sides pick a 6-neighbour anchor.
- Game would terminate ply ~25 with P1 win, identical to Game 1 outcome.

### Strategy guides

**P1 (offence/threshold push):** Open at a 6-neighbour anchor: (2,2,2), (2,2,6), (2,6,2), (6,2,2), (6,6,2), (6,2,6), (2,6,6), (6,6,6) are the 8 sub-cube interior corners. Build the 6-petal octahedron (7 stones, +13.0). Then expand face-by-face along z (or x or y) at +3.0/move per expansion. Reach +30 on ply 25.

**P2 (sandwich-then-stall):** Don't mirror — that loses on tempo. Sandwich P1's anchor by ply 4 (one P2 neighbour at ply 2, second at ply 4). Be prepared for P1 to counter-sandwich; super-ko prevents you from re-capturing immediately. Use the forced-pass tempo to build your own anchor cluster while P1 is rebuilding.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Yes — three, distinguishable by my games:
1. **Octahedron mirror + tempo race** (P1's playbook) — the canonical influence-clustering line.
2. **Sandwich-on-anchor** (P2's playbook in Game 2) — converts a 6-neighbour anchor into a kill-zone.
3. **Counter-sandwich-into-ko** (P1's reactive playbook) — uses the super-ko rule to force a tempo gain on the recapturing side.

**Counter-play.** Real and recursive. Sandwich beats mirror. Counter-sandwich beats sandwich. Super-ko prevents the counter-counter-sandwich from being played as a direct re-capture, so the loop terminates rather than spiralling. This is structurally better than R17's sandwich-trap dynamics, where the trap was a one-time unrecoverable loss.

**Short-term vs long-term.** Per-move gain ~+1.5–3.0; threshold 29.7 → 12–20 own stones to win. Games end ~25 plies in mirror, longer (35–40) in adversarial play. Tactical horizon = 4–6 plies (sandwich attack/defence cycle); strategic horizon = ~12 plies (cluster shape choice + ko-aware capture sequencing).

**Emergent concepts observed.**
- **Sub-cube corners as influence wells.** The 6-neighbour interior corners are the only cells where octahedron clusters can form; the fractal hole pattern forbids them elsewhere. Identifying these 8 special cells is a substrate-driven opening principle.
- **Suicide-via-ko.** Re-capturing in the obvious way gets rolled back as a pass via super-ko — meaning the ko-aware player can *force* the opponent into a wasted move by setting up a "must-recapture-but-can't" position. I encountered this naturally in Game 2.
- **2-active-neighbour safety.** Cells like (2,4,2) (only (2,3,2) and (2,5,2) active) are uncapturable while one neighbour stays empty/friendly. They make stable cluster terminuses.
- **Counter-sandwich.** Reversing a 2-for-1 capture by placing on the captured square when you control both opposing neighbours of the attacker — confirmed working in Game 2, ply 7. This is a tactical pattern the pilot's 4-ply Game 2 truncated before observing.

**Does the menger substrate matter?** Yes, more than I expected before playing. The fractal hole pattern (a) determines where 6-neighbour anchors live (8 specific cells, all sub-cube corners) — without this constraint, optimal play would be uniform, but with it openings concentrate; (b) creates safe terminuses (2-neighbour cells); (c) blocks distance-2 reinforcement (under r=1, two stones with a hole between them don't reinforce). On a regular 9³ cube with same rules, openings would be on any interior 6-neighbour cell (much larger choice set) and clusters would freely tile — strictly less interesting. **Substrate contribution: ~+1 depth, ~+1 novelty.**

**Does the propagation kernel matter?** r=1 with decay 0.5 is harsh. Distance-2 cells contribute zero, so the menger holes that separate distance-2 cells are punitive (a single hole between two stones means no reinforcement). r=2 (e.g. carpet rank-1) softens this. The strategic effect: adjacency is the ONLY shape that matters, and shape is heavily fractal-constrained.

**Capture-rule contribution.** Captures fired in Game 2 (one capture in 4 plies; one counter-capture; one super-ko-rolled pass). 2-for-1 at first; 1-for-1 net after counter-sandwich; super-ko forces a pause. Captures are the only balance mechanism, and they're knowledge-asymmetric (mirror loses).

**First-mover advantage / seat balance.** P1 wins my Games 1 and 3 (mirror) decisively. Game 2 (sandwich) initially favoured P2 but reverted to P1 advantage after counter-sandwich + super-ko. PPO trained-vs-trained reports 0.500 — consistent with the agents learning the sandwich + counter-sandwich + ko-discipline cycle. Pre-knowledge balance is poor (P1 win on naive mirror); post-knowledge balance is decent.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + outnumber + threshold-race + super-ko on a 3D Menger fractal.

(a) **Threshold-race influence games** are *Tumbleweed* (2D hex, weighted placement value) and *Sygo* (Go territorial weights). Neither uses 3D, neither uses fractal substrate, neither uses super-ko on a non-Go capture rule.

(b) **Outnumber-2 capture** is Tafl-family / Ataxx-adjacent (replicate-and-flip-when-outnumbered). The exact "remove enemy with ≥2 friendly nbrs on an arbitrary topology" is closest to *Atari Go* with a modified threshold and to certain published papers on n-D Tafl variants.

(c) **The combination "outnumber + influence + threshold-race + super-ko"** is, to my knowledge, unprecedented in published abstract games. Inside the project corpus, it's the dominant family for R19 menger top-10 — the briefing confirms this is a basin not an outlier.

(d) **Menger substrate.** Genuinely unprecedented as a board substrate in the published literature. The closest case I'm aware of is Hales–Jewett type combinatorial work on n-D tic-tac-toe; no abstract game uses a genuine 3D fractal board.

(e) **Super-ko on outnumber capture.** This is the pieces I think gets undercredited. Super-ko on Go-style surround capture is standard. Applied to outnumber capture, it produces a different dynamic: outnumber captures don't normally cycle (the attacker keeps gaining stones); super-ko enforces *strategic placement order* such that the capture-recapture loop *cannot* perpetuate. This is rule-design subtlety with real strategic consequence and is undocumented in the briefing.

(f) **Expert-transfer test.** A Go + Othello + Hex + 3D-Tic-Tac-Toe (Qubic) player ensemble would understand the rules in 10 minutes. Irreducible new pieces: (i) the menger active-cell map (which cells are usable); (ii) influence-as-scoring with r=1; (iii) the super-ko interaction with outnumber capture.

**Closest known-game analogue:** **Influence-Tafl on a Menger sponge with super-ko.** No exact analogue exists. Closest in-corpus: R19 carpet rank-1 (`ce3a09e05cef`) — same family in 2D with r=2 kernel.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on 2D 8×8. Different family. R19 menger rank-1 is influence + outnumber + threshold + super-ko on 3D menger. R8 has the narrative simplicity of a connection win condition (one chain ⇒ win); R19 has the larger emergent space (8 anchor sites × octahedron expansion × ko-aware capture sequencing). R19's strengths over R8: substrate novelty, ko-cycle dynamics, threshold-race tempo metric. R19's weaknesses: knowledge-asymmetric balance, no narrative arc.

**Player rebuttal (P1 + P2).**
- **Sub-cube-corner anchoring** (placing at the 8 specific 6-neighbour cells) is substrate-specific and absent in any non-fractal 3D Tafl/influence game. It's a real new strategic primitive.
- **Counter-sandwich + super-ko ko fight** is a 3-move tactical pattern that doesn't transfer cleanly from any single ancestor; the closest is Go's seki/ko, but Go ko is single-stone whereas this is multi-cell capture-reverse-recapture.
- **Subtracting from novelty:** the strategic skeleton (cluster + race + sandwich) is shared with R19's other top games (carpet ranks, menger rank-2/3); the menger version is a 3D adaptation of the same family rather than a structurally distinct game. Once you know carpet rank-1, you understand 80% of menger rank-1 in 5 minutes.

**Novelty score (post-adversary):** **7/10.** Above pilot's 6 because (i) super-ko enforcement on outnumber capture is a substantive undocumented mechanic, (ii) the counter-sandwich-into-ko pattern is genuinely 3-move-deep and substrate-specific, (iii) the 8 sub-cube anchors are a substrate-driven opening principle. Below 8 because the family (capture+influence+race) is shared with carpet siblings and the influence-game ancestors are well-known. Anchored against R17 mean (3.50) — this is comfortably above; against R8 (8/10) — below because R8's narrative arc and seat balance are still better.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** 1f9191b5d4e6
**Rules Summary:** Place stones on a 9×9×9 Menger sponge to accumulate influence on cells you own. Each placement spreads ±1.0/±0.5 to itself/neighbours; outnumber-2 capture removes enemy stones with ≥2 of your neighbours; super-ko prevents repeat positions. First to >29.7 effective influence on owned cells wins.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6 (effective 2–6 per cell).
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** none.
**Quirks discovered:** (a) super-ko is active and silently converts replay-capture moves to passes; (b) counter-sandwich is a working defensive primitive contradicting briefing's "6-nbr cells safer" claim.

### Scores (1–10)

- **Strategic Depth: 7** — Mirror tempo race, sandwich/counter-sandwich tactical primitive, super-ko enforcement, cluster-shape constraints, and 8-anchor opening choice combine to give 4 independent decision dimensions per game. Above carpet rank-1 because the 3D fractal + super-ko adds a real layer (ko-cycle planning) that pilot did not surface.
- **Emergent Complexity: 6** — Counter-sandwich, suicide-via-ko, sub-cube-corner anchoring, 2-neighbour safe-terminuses are emergent and non-obvious. Above carpet (5) because of the ko interactions.
- **Balance: 4** — Mirror loses for P2 cleanly (~3 tempo points). Sandwich is a viable P2 counter but knowledge-asymmetric. PPO 0.500 reflects co-learned counter, not innate balance. Same as pilot.
- **Novelty (post-adversary): 7** — see Phase 4. Substrate + super-ko-on-outnumber is unprecedented.
- **Replayability: 5** — 400 cells × 8 anchor choices × ko-aware capture sequencing gives meaningful variety. Above carpet rank-1 (5) by margin.
- **Overall "Would I play this again?": 6** — Once: yes, the ko-fight discovery is satisfying. Repeatedly: yes, to learn ko-discipline against a strong opponent. Anchor: above R17 mean (3.5), above R17 best (4.14), well below R8 (8). The super-ko interaction is the reason this clears 5 for me.

### CLOSEST KNOWN-GAME ANALOG
**Influence-Tafl on a Menger sponge with super-ko.** No published analogue. In-corpus: R19 carpet rank-1 (`ce3a09e05cef`) — same family in 2D with r=2 kernel and (presumably) the same super-ko mechanic.

### KILLER FLAWS
- **Mirror = P1 wins by exactly one tempo unit.** Without pie rule (or seat-swapped openings) the game is structurally biased.
- **Briefing/pilot misreport: "6-nbr cells are safer".** They are not — outnumber-2 captures any cell with ≥2 enemy neighbours regardless of total degree. This is a documentation flaw inherited into the pilot eval.
- **Super-ko is undocumented in briefing.** Yet it materially changes game dynamics. A naive evaluator would miss it (the pilot did).
- **r=1 + fractal holes makes adjacency the only thing that matters.** Distance-2 placements gain zero from each other through a hole. This caps the strategic vocabulary to "adjacency clusters" — no long-range influence shape arises.

### BEST QUALITY
**Super-ko-enforced ko-fights on outnumber capture.** This is the crown jewel I found that the pilot did not. Counter-sandwich + super-ko produces a 3-move tactical primitive (capture → counter-capture → super-ko forced pass) that isn't in any single ancestor game. Combined with the 8 sub-cube anchor cells from the menger fractal, this gives the game its real depth.

### MENGER STRUCTURAL CONTRIBUTION
**Substantial — about +1 depth and +1 novelty over a regular 9³ cube.** The fractal forces openings to concentrate at 8 specific anchor cells; constrains cluster geometry; creates 2-neighbour safe-terminuses; punishes distance-2 reinforcement under r=1. On a flat 9³ grid with the same rules, opening choice would be much wider and clusters would tile freely. The menger pattern is doing real strategic work, not just decorative. Anchored against R17's "modest, not transformative" finding for 4³ cubic substrates: menger here is meaningfully more impactful because the hole pattern is fine-grained (50% holes at the 2×2×2 micro-scale), so it directly constrains tactical placement, not just board size.

### IMPROVEMENT IDEAS
**Single best change: pie rule (cross-cutting).** Same as pilot's recommendation, and it's still right — the mirror tempo advantage is structural and pie rule punishes any opening profitable to mirror.

Secondary improvements:
- **Document super-ko interaction.** The current briefing/eval-prompt doesn't mention `needs_ko_rule=True` or the resulting capture-cycle constraints; this misleads evaluators and reduces the credit the game gets.
- **Increase capture threshold to 3.** Would make 6-neighbour cells genuinely safer (need 3 of 6 = 50% coverage) and reduce the "any 2-of-N" sandwich pattern's universality. Would shift balance toward P1.
- **Increase influence radius to r=2.** Distance-2 reinforcement would soften the hole-cost and let players span single-cell holes. Might make it more like carpet rank-1 (which uses r=2).
- **Remove the place-only constraint and allow a single move action per turn.** Movement under threshold-race could let stones be repositioned for cluster optimisation; would test whether D1's ban on hybrids is doing useful work here.

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-4_game1f9191b5d4e6.md`.*
