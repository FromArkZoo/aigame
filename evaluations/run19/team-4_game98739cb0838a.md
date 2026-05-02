# Run 19 Evaluation — team-4 — Game 98739cb0838a

**Team ID:** team-4
**Game ID:** `98739cb0838a` (Menger rank-2, GE 0.3213, ELO 2402.6)
**Substrate:** Menger sponge, axis 9, 400 active cells / 729 grid positions, max_degree 6 (effective 2–6).
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 98739cb0838a` (see `briefing_menger_rank2.md`).

---

## Phase 1 — Rule Comprehension

**Board / Turn / Action.** Same 9×9×9 menger sponge as rank-1: 400 active cells, place-only (D1 active), 730 actions, alternating, P1 first, max_turns = 100.

**Capture.** Outnumber-2, identical to rank-1 mechanics. Same misleading "high-degree = safer" briefing claim — debunked in rank-1, applies here too.

**Propagation.** Influence, **r=2**, strength≈0.9895, decay≈0.3037. Distance-1 contribution ≈ +0.30, distance-2 ≈ +0.09. The longer reach but steeper decay vs rank-1's r=1/decay=0.5 is the headline parameter shift.

**Win.** Threshold-race > **38.959** (31% higher than rank-1's 29.71). Max turns 100. Engine-confirmed `needs_ko_rule = True` — **super-ko is active**, identical to rank-1 (and equally undocumented in the briefing).

**Degeneracy check.**
- This is the unmodified seed `m8` that survived 8 generations of evolution untouched. That has two competing readings: (a) it's a strong local optimum nothing better exists nearby, or (b) the evolution operators didn't have a path out. Either way, the effective game I'm scoring is the m8 seed.
- Steep-decay r=2 combined with menger's hole pattern is interesting: the +0.09 dist-2 contribution is the *only* way to reinforce across a single-cell hole. So one hole between stones is recoverable here (as +0.09) where rank-1 would give 0.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — 6-neighbour octahedron mirror (per-stone gain calibration)

Sequence: `182,546,181,547,183,545,173,555,191,537,101,627,263,465,102,626,110,618,174,554,190,538,254,474,262,466,184,544,176,536,164,564` (32 plies).

Plot:
- Both players build the canonical 7-stone octahedron at their 6-neighbour anchor (P1 (2,2,2), P2 (6,6,6)). After ply 14: both at +13.27 (vs rank-1's +13.0 — distance-2 reach adds ~0.27).
- Per-stone gain during expansion: ~+2.4 per move (P1 turn 15 → +15.64; P1 turn 17 → ~+18.0). This is *higher* than rank-1's +3.0/move on first inspection, but the threshold is also higher (38.96 vs 29.71).
- Stones-to-win calculation: 38.96 / 2.4 ≈ 16 stones per side. At 32 plies, both at +30.75 — still 8 points short.
- Game would terminate ~ply 39–42 with P1 win. **Faster than the 54-move pilot estimate** because I'm using optimal anchor + octahedron + face-by-face expansion, not an arbitrary opening line.

Reflection: Mirror tempo conclusion is identical to rank-1 — **P1 wins by exactly one expansion move**. Per-stone gain is slightly higher under this kernel because adjacent-pair reinforcement (+0.30 each direction = +0.60 mutual) plus the dist-2 contribution exceeds rank-1's adjacency-only (+0.50 mutual) for tightly-packed clusters. **The pilot's "weaker per-stone contribution" claim is wrong for the octahedron shape — they only checked the 4-stone plus.**

### Game 2 — Sandwich + counter-sandwich + super-ko (rank-1 replay test)

Sequence: `182,181,173,191,200,110,182,191,209` (9 plies).

Plot:
- Identical sequence to rank-1 Game 2. P1 anchors (2,2,2); P2 sandwiches via (1,2,2)+(2,3,2), capturing (2,2,2) at ply 4.
- P1 plays (2,4,2) (only-2-active-neighbours cell, safe terminus), then (2,2,2) again — counter-sandwich captures (2,3,2). After ply 7: P1 leads +3.87 vs +1.41.
- P2 attempts re-capture at ply 8: action 191 (2,3,2). Engine accepts the action but the **resulting state matches the post-ply-6 hash → super-ko rolls back to a pass**. Confirmed by `piece_counts` being unchanged after the move.
- P1 ply 9: extends with (2,5,2). Lead grows to +5.37 vs +1.41.

Reflection: **Super-ko enforcement is identical between rank-1 and rank-2**. The rule blob differs only in propagation parameters and threshold; the capture/ko machinery is shared. So all three of my rank-1 findings transfer here verbatim:
1. Counter-sandwich is a working primitive on outnumber-2 captures.
2. Super-ko prevents the obvious re-capture, forcing the attacking side to find a different placement (or pass).
3. The 2-active-neighbour cell (2,4,2) is a safe terminus for cluster expansion — P2 can never sandwich it.

### Game 3 — Long-horizon cluster vs late-attack probe (sketched analytically + 16-ply demo)

Sequence: `182,546,181,547,183,545,173,555,191,537,101,627,263,465,102,626` (16 plies).

Plot:
- Both at +15.64 after 8 stones each. P1 attempts 545 (P2-occupied) or 626 (also P2) for an asymmetric attack — both illegal. P1's available attacks are limited to placing adjacent-to-P2's-cluster, but with both anchors fully built P2 stones each have 1 P1 neighbour at most → captures don't fire.
- This shows the symmetric-build line is "fortified" once both clusters reach octahedron. **Mid-game capture vector is closed** in the symmetric line.
- Sketch: To break this lock, the attacking side must place INSIDE the opponent's cluster footprint — but 6 of 6 anchor neighbours are already enemy stones, so any placement adjacent to anchor would be self-capture (≥2 enemy nbrs → wait, self-capture doesn't fire on outnumber, so the placement is legal but provides minimal influence on the placed cell since opponent's −0.30 propagation pulled it down). Net: capture vectors close once clusters are built. Endgame becomes pure threshold race.

Reflection: The longer horizon (39+ plies) creates a **mid-to-late-game lock-in**: once both sides build their octahedrons, neither can capture without conceding a worse trade. Rank-1's shorter horizon means captures fire mostly in the opening; rank-2's longer horizon means **most of the game is a fortified positional standoff** where each side just adds adjacent stones. This is a real difference from rank-1.

### Strategy guides

**P1 (offence/threshold push):** Anchor at one of the 8 sub-cube corners. Build the 7-stone octahedron in plies 1, 3, 5, 7, 9, 11, 13 (own side). Then expand face-by-face along whichever axis has the most active cells (z is generally best because the menger hole pattern blocks more y/x routes). Expect ~20 stones to win by ply ~40.

**P2 (sandwich-then-stall, with ko-aware re-attack):** Sandwich at ply 2/4. Anticipate counter-sandwich at ply 7. Don't try to re-capture at ply 8 — super-ko will eat the move. Instead, place at a *different* P1 stone's neighbour (e.g., attack (2,1,2) or (2,4,2) if P1 has them) to break out of the ko cycle. The longer horizon gives P2 time to recover from the initial 2-for-1 reversal if they ko-discipline correctly.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Same three as rank-1 (octahedron + sandwich + counter-sandwich/ko). Plus one new emerging strategy from the longer horizon:
4. **Mid-game cluster fortification.** Once both sides have anchored, the symmetric "build out" with no captures is mathematically a P1 win on tempo. P2 must commit to an asymmetric play (sandwich, then catch up with a 2nd cluster elsewhere) before clusters fortify.

**Counter-play.** Same recursive sandwich/counter/ko structure, identical to rank-1. The long-horizon adds patience as a strategic resource: making a sandwich move late costs more relative tempo (less remaining game to recover) but is harder to counter-sandwich (more existing cluster to defend).

**Short-term vs long-term.** Mid-late game horizon is materially longer than rank-1 (~20-stones-each instead of ~13). Tactical horizon stays at 4–6 plies; *positional* horizon stretches to 12–15 plies (when to commit to a 2nd anchor, when to force a sandwich exchange).

**Emergent concepts observed.**
- All rank-1 emergent concepts transfer (sub-cube anchors, suicide-via-ko, 2-neighbour safe terminuses, counter-sandwich).
- **Cluster fortification.** New: once both octahedrons are built, capture vectors largely close. Late game is positional rather than tactical.
- **Single-hole reinforcement.** New under r=2: a stone can reinforce another at distance 2 (across one hole) at +0.09. This is small but lets clusters span single-cell holes that rank-1 couldn't.

**Does the menger substrate matter?** Same as rank-1 — substantively. The 8 sub-cube anchors are still the only 6-neighbour cells; the hole pattern still constrains cluster shapes. The r=2 kernel softens the hole-cost slightly (single hole = ~3.3× less penalty than rank-1) but doesn't change strategic conclusions.

**Does the propagation kernel matter?** **More than rank-1, but in a subtler direction.** r=2 gives a "spotlight" influence pattern: strong centre, weak periphery, modest dist-2 reach. This makes mid-game positional play slightly more interesting (you can plan 2-step expansions across a hole), but also means each individual move matters less per-point. The pilot called this "long-horizon preservation" and that's accurate.

**Capture-rule contribution.** Captures fire less often per game (longer horizon, more fortified mid-game). When they do fire, the same sandwich/counter/ko cycle plays out.

**First-mover advantage / seat balance.** Same structural P1 favour, exactly. PPO 0.500 trained-vs-trained and 1.000 vs random — clean training signal, suggesting the agents learn the sandwich+counter+ko pattern.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Influence + outnumber + threshold + super-ko on menger, with steep-decay r=2 kernel. Differences from rank-1:

(a) **Steep-decay r=2** is uncommon in published abstract games. *Tumbleweed* uses gentle-decay distance kernels; *Sygo* uses sharp territorial weights. Steep-decay r=2 is closer in spirit to a "strength-of-influence at radius" pattern from cellular automata literature than from games.

(b) **Higher threshold + longer game** shifts toward positional preservation. This is closer in spirit to Go's late-game endgame than rank-1's quicker threshold race.

(c) **Same super-ko mechanic as rank-1** — the rule blob shares this with all R19 menger games (and presumably carpets too, to verify in later games).

**Closest known-game analogue:** **Long-form Influence-Tafl on a Menger sponge with super-ko.** No exact published analogue. In-corpus: rank-1 (`1f9191b5d4e6`) is the same family with shorter horizon.

**Comparison to R8's Connection Go (8/10).** R8's strength is the narrative arc (build a chain → win) and clean seat balance. Rank-2 has a longer arc but no narrative milestone — just keep accumulating until 38.96. The longer game brings rank-2 closer to R8's positional feel than rank-1's tactical race, but the lack of a narrative win condition still limits replayability.

**Player rebuttal.**
- **Same substrate-driven novelty as rank-1.** Sub-cube anchoring, fractal cluster geometry, super-ko discipline.
- **Long-horizon cluster fortification** is a new strategic primitive not present in any rank-1 line I played. This is genuinely a different game-feel even though the rules differ only in numeric parameters.
- **Subtracts:** rank-2 is a direct seed that survived 8 generations untouched. Either it's a stable optimum (positive) or evolution couldn't escape (concerning). The evolutionary process didn't *find* this game — it *kept* it.
- **The pie-rule recommendation that's cross-cutting across all R19 games is the right single change** — not novel-game-specific.

**Novelty score (post-adversary):** **6/10.** Same as pilot. Above pure re-skin (substrate + super-ko + steep-decay influence is a real combination) but below 7 because rank-1's rank-2 share the family and rank-1's crossover refinement is what evolution actually selected for. This game's novelty floor is shared with rank-1; its incremental contribution beyond rank-1 is small.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** 98739cb0838a
**Rules Summary:** Place stones on a 9×9×9 Menger sponge to accumulate r=2-spread influence (steep decay 0.30) on owned cells. Outnumber-2 captures + super-ko. First to >38.96 wins, typically ~40 plies. Same family as rank-1, longer-horizon variant.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.
**Quirks discovered:** super-ko is active (same as rank-1). Cluster fortification mid-game closes most capture vectors.

### Scores (1–10)

- **Strategic Depth: 6** — Same depth as rank-1 minus the per-move impact (longer game dilutes single-move significance) plus the long-horizon positional layer (cluster fortification, when to commit to a 2nd anchor). Net same as rank-1's 7 minus 1 for tactical dilution.
- **Emergent Complexity: 6** — All rank-1 emergent patterns (sub-cube anchors, super-ko discipline, counter-sandwich, 2-neighbour safe terminuses) plus cluster fortification. Same emergent vocabulary as rank-1, applied in a longer arc.
- **Balance: 4** — Same structural P1 favour. Mirror still loses for P2. Knowledge-asymmetric counter exists.
- **Novelty (post-adversary): 6** — Same as rank-1's novelty floor; rank-2 doesn't add a new dimension beyond what the family already provides. The long-horizon variant is a parameter shift, not a new mechanic.
- **Replayability: 6** — Higher than rank-1's 5 because longer game (54-ply pilot estimate; 40-ply optimal) gives more stones and more position variety. Above carpet rank-1 by margin.
- **Overall "Would I play this again?": 5** — Once: yes, to feel the long-horizon fortification dynamic. Repeatedly: only if also exposed to rank-1 first; otherwise the family-shared dynamics dominate the experience. Anchor: above R17 mean (3.5), above R17 best (4.14), well below R8 (8).

### CLOSEST KNOWN-GAME ANALOG
**Long-form Influence-Tafl on a Menger sponge with super-ko.** No published analogue. In-corpus: menger rank-1 is the same family with shorter horizon and tighter tactical engagement.

### KILLER FLAWS
- **Same as rank-1: mirror = P1 wins on tempo.** Structural; pie rule needed.
- **Long horizon dilutes per-move impact.** A sandwich gain that would decide rank-1 only counts for ~8% of the threshold here. Tactical depth pays a price for positional depth.
- **Direct seed survived 8 generations untouched.** Either local optimum or evolution couldn't escape. Either way, this game wasn't actually *discovered* by R19's evolution — it was inherited.
- **Mid-game cluster fortification is a positional dead zone.** Once both octahedrons are built, capture vectors close and the game becomes a pure threshold race with no decision content.

### BEST QUALITY
**Long-horizon cluster fortification.** This is the one strategic primitive rank-2 has that rank-1 doesn't — once clusters are built, captures rarely fire and the game becomes a positional commit-and-build exercise. It's the closest R19 menger game to Go-style late-game play, and the only one in the family that rewards strategic patience over tactical opportunism.

### MENGER STRUCTURAL CONTRIBUTION
**Same as rank-1 — substantial.** ~+1 depth, ~+1 novelty over a regular 9³ cube. The 8 sub-cube anchors, fractal cluster geometry constraints, and 2-neighbour safe-terminuses all transfer. The slightly softened hole-cost (r=2 distance-2 reach contributes +0.09 across a hole) doesn't change the substrate-driven conclusions.

### IMPROVEMENT IDEAS
**Single best change: pie rule.** Same recommendation as rank-1 (and likely all R19 games). The mirror tempo bias is structural.

Secondary improvements:
- **Lower threshold to 30** (rank-1's value). Compresses games to ~30 plies and tightens tactical decisions. Trades positional depth for tactical clarity. Pilot recommended this; I agree.
- **Document super-ko in briefing.** Same gap as rank-1.
- **Increase decay back to 0.50** (rank-1's value). Would soften the "spotlight" pattern and make the family more uniform across ranks. Less interesting from an evolutionary perspective but cleaner gameplay.
- **Allow movement actions.** With r=2 reach, movement could let stones reposition for cluster optimisation in a way rank-1's r=1 makes pointless. Tests whether D1's hybrid ban is justified for this specific game.

### What evolution did or didn't add (vs rank-1)
**Rank-2 is the unmodified seed; rank-1 is its crossover-refined descendant.** The R19 evolution found: (a) reducing radius from 2 to 1 (sharper kernel) and (b) reducing threshold from 38.96 to 29.71 (shorter game) make a more *playable* but less *positional* game. From a depth perspective, both score similarly (5–6); the differences are in feel (rank-1 tactical, rank-2 positional) rather than in absolute strength. The fact that the seed survived 8 generations untouched in its own lineage suggests either it's a very deep local optimum or the R19 mutation operators were too weak to escape it. **Net read: evolution found a parameter-tweak refinement, not a new strategic primitive.**

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-4_game98739cb0838a.md`.*
