# Run 19 Evaluation — team-4 — Game 5048f71b62fd

**Team ID:** team-4
**Game ID:** `5048f71b62fd` (Menger rank-3, GE 0.3158, ELO 2354.6)
**Substrate:** Menger sponge, axis 9, 400 active cells / 729 grid positions, max_degree 6 (effective 2–6).
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run19_helper.py --game 5048f71b62fd` (see `briefing_menger_rank3.md`).

---

## Phase 1 — Rule Comprehension

**Board / Turn / Action.** Same 9×9×9 menger as ranks 1 & 2. 400 active cells, place-only (D1), 730 actions, alternating, P1 first, **max_turns = 71** (shortest of the 6).

**Capture.** Surround (Go-style group capture). After placing, the engine collects each enemy group adjacent to the placed cell; if the group has 0 liberties (no empty *active* cells adjacent to any group member), the entire group is removed. **The threshold=2 parameter is ignored** by `_capture_surround` (verified by reading engine source) — it's only the capture *type* that matters here. Critically: **holes do not count as liberties**, so the fractal hole pattern actively steals liberties.

**Propagation.** Influence, r=1, strength=1.0, decay=0.5 — identical to rank-1.

**Win condition.** Threshold-race > **21.212** — the lowest of the 6 R19 games. Combined with same per-stone gain as rank-1 (~+1.86 per stone in optimal cluster), this means games end in ~13–17 own stones (~25–35 plies).

**Other rules.** `needs_ko_rule = True` — **super-ko is active here too**, despite the pilot's recommendation to "add a ko rule analogue" (which was already active). This matters for surround capture because Go's classical ko cycle (single-stone capture/recapture) is exactly what super-ko handles.

**Degeneracy check.**
- Surround threshold parameter is dead (numeric noise).
- Pilot was right that the fractal hole pattern is the most strategically active for this game; corners and edges with mostly-hole neighbours can have effective liberty counts as low as 1, making single stones extremely fragile.
- Sub-cube interior 6-neighbour cells (e.g., (2,2,2)) are *substantially* harder to surround than to outnumber — surround needs all 6 neighbours blocked, vs outnumber's 2 of 6.

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run19_helper.py`.

### Game 1 — 6-neighbour anchor mirror (tempo + group invariance check)

Sequence: `182,546,181,547,183,545,173,555,191,537,101,627,263,465,102,626` (16 plies).

Plot:
- Both players build the 7-stone octahedron at their 6-neighbour anchor. Same scoring as rank-1 (both at +13.0 after 14 plies, +16.0 after 16 plies).
- P1 group at (2,2,2)+petals: 1 group of 7 stones. Liberties of this group = the external neighbours of the 6 petals minus holes minus other own. Each petal's external active neighbours are 2–3 cells; with overlaps removed, the group has ~12 distinct liberties. **Far from death**, even after both sides have built.
- Game ends ~ply 18–20 (P1 wins on tempo at +21.2). My run stopped at ply 16 to test stability; P1's lead at that point is +0 over P2 in the mirror but +3 ahead in tempo (P1 plays first). Win on ply ~19.

Reflection: **In mirror play, the surround mechanic is functionally inert** — no captures fire because both sides build alive 7-stone groups from move 1. The game reduces to a pure threshold race, identical in flavour to rank-1's mirror. Surround's distinctive depth shows up only in *asymmetric* lines.

### Game 2 — P2 attempts surround on the 6-neighbour anchor

Sequence: `182,181,191,173,200,263,209,101,165,183` (10 plies).

Plot:
- P1 anchors (2,2,2). P2 plays (1,2,2). P1 extends to (2,3,2) (joins group). P2 (2,1,2). P1 (2,4,2) (chain to 3). P2 (2,2,3). P1 (2,5,2) (chain to 4). P2 (2,2,1). P1 (3,0,2) — *separate* probe. P2 (3,2,2).
- After 10 plies: P2 has played 5 stones, all neighbours of (2,2,2): (1,2,2), (2,1,2), (2,2,3), (2,2,1), (3,2,2). All 5 of (2,2,2)'s 6 neighbours occupied by P2 (the 6th, (2,3,2), is P1's chain extension).
- P1's main group: {(2,2,2), (2,3,2), (2,4,2), (2,5,2)} — a 4-stone y-axis chain. Group liberties = external active empty cells of any group member. (2,2,2) contributes 0 liberties (all neighbours P2 or friend); (2,3,2) contributes (1,3,2), (2,3,1) = 2; (2,4,2) contributes 0 (4 of 4 neighbours are holes after subtracting friend); (2,5,2) contributes (1,5,2), (2,6,2) = 2. **Total: 4 liberties.**
- P2 has spent 5 moves to bring the group from 18 liberties to 4. To capture, P2 needs 4 more moves to close the remaining liberties — meanwhile P1 either extends the chain (adds liberties) or builds elsewhere. **The 5-vs-1 trade so far has cost P2 5 moves for net zero captures** while P1's chain grew to 4 stones.
- Score at ply 10: P1 +5.5, P2 +2.5. P1 ahead by 3 points, on track to threshold by ply ~17.

Reflection: This is the genuinely Go-like depth — surround attacks force a multi-move investment that the defender can match by extending the group. Pilot's claim "captures are very aggressive" applies to *isolated single stones in low-liberty positions* (Game 3 below); for the 6-neighbour anchor + chain extension, surround is *less* aggressive than rank-1's outnumber-2 because the defender can grow liberties as fast as the attacker can close them.

### Game 3 — Corner-anchor fragility (substrate-driven liberty geometry)

Sequence: `0,1,9,81,162` (5 plies, ends with capture).

Plot:
- P1 (0,0,0) — corner with 3 active neighbours: (1,0,0), (0,1,0), (0,0,1). Pilot's exact line.
- P2 (1,0,0). P1 (0,1,0) — extends. P2 (0,0,1) — places at the only remaining liberty of (0,0,0) plus a separate stone.
- (0,0,1) as an isolated P2 stone has neighbours (1,0,1)=hole, (0,1,1)=hole, (0,0,0)=P1, (0,0,2)=empty. Only 1 active empty neighbour ((0,0,2)) = 1 liberty. Fragile.
- P1 (0,0,2): closes (0,0,1)'s last liberty. **(0,0,1) captured.** Empirically confirmed.
- After ply 5: P1 has 3 stones, P2 has 1. P2 is down a stone for nothing.

Reflection: **Corner+edge cells are extremely fragile** in this game because the menger fractal pattern means many of their neighbours are holes. (0,0,1)'s 4 axis-neighbours: 2 are holes, 1 is enemy already, 1 is empty. A single placement closes the last liberty. **This is the most genuinely substrate-specific dynamic in any R19 game I've evaluated.** The same opening on a regular 9³ grid would not produce this capture (more empty neighbours = more liberties = more turns to surround).

### Strategy guides

**P1 (offence/threshold push):** Anchor at a 6-neighbour sub-cube interior corner ((2,2,2), (6,6,6), etc.). **Build chain extensions, not isolated stones.** A chain has many more liberties than the same number of isolated stones. Threshold 21.2 is reached at ~13 own stones (~25 plies); even if you lose a 2-stone group early, you can still win on tempo.

**P2 (Go-style attacker):** Don't sandwich around the 6-neighbour anchor — that's slower than outnumber's 2-move trick. Instead: (a) look for P1 single stones in corner/edge positions where the fractal kills liberties; (b) play close-but-not-adjacent to P1 to gradually close liberties on a chain extension; (c) extend your own group preemptively to ensure you stay alive. The "trade-groups-for-tempo" line the pilot mentions is real but requires reading the liberty count accurately.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** Three (one more than rank-1):
1. **Octahedron + chain extension + threshold race** (P1's playbook). Build alive groups; race to 21.2.
2. **Corner-fragility exploitation** (P2's playbook). Look for low-liberty single stones; close their last liberty.
3. **Trade groups for tempo** (advanced). Sacrifice a 2–3-stone group whose liberties are exhausted in exchange for free tempo to build an alive group elsewhere. Requires reading liberty arithmetic accurately.

**Counter-play.** Real and *richer* than rank-1. Surround creates Go-style life-and-death tension absent from outnumber/custodian. P2 has more attacking *options* (many possible surround targets); P1 has more defending *responses* (extend, sacrifice, ignore-and-build).

**Short-term vs long-term.** Threshold 21.2 / per-stone gain ~1.5–1.8 → ~12–14 stones to win → ~25 plies total. Tactical horizon = 4–8 plies (one capture sequence); strategic horizon = ~12–15 plies (group-life management). Slightly less positional than rank-2 but with richer per-move tactical content.

**Emergent concepts observed.**
- **Hole-as-liberty-stealer.** Verified empirically (Game 3). Corner cells in the menger have fewer effective liberties than corner cells on a regular 9³ grid. This is genuinely substrate-driven and not present in any non-fractal game I know.
- **Chain extension defends the anchor.** Extending an attacked group adds liberties faster than the attacker can close them. (Game 2: P2's 5 moves vs P1's 4-stone-chain growth → 4 liberties remaining.)
- **Sub-cube anchors are surround-resistant.** Same 8 cells as rank-1, but here their 6-neighbour structure is a *defensive* asset rather than an *offensive* one (you build out safely, hard to surround).
- **Super-ko + surround = classical Go ko discipline.** I didn't encounter a ko cycle in my games (surround needs more moves than outnumber for a capture, so ko cycles take longer to set up), but the rule is active and would prevent infinite recapture.

**Does the menger substrate matter?** **More than any other R19 game I've evaluated.** The fractal hole pattern's interaction with surround capture is unique: holes steal liberties, creating a topology-dependent vulnerability profile. Sub-cube interior anchors are nearly invulnerable; corner/edge stones with hole-neighbours are extremely fragile. **A 9³ regular grid with the same rules would lose 2 points of depth** — the substrate is doing essential work here.

**Does the propagation kernel matter?** Same r=1 kernel as rank-1; same conclusions.

**Capture-rule contribution.** Major. Surround creates Go-style depth that outnumber can't. **The most game-defining capture rule across the 6 R19 games.**

**First-mover advantage / seat balance.** Same structural P1 favour from mirror tempo. PPO 1.000 vs random and 0.500 trained-vs-trained — clean training signal. Same balance issue as the other 5 R19 games but the asymmetric counter (P2 plays surround attack on fragile cells, not mirror) is more available because there are more attack vectors.

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** Influence + Go-style surround + threshold + super-ko on a 3D fractal.

(a) **Surround capture is Go's defining mechanic** (~3000 BCE). Maximally well-known.
(b) **Influence-as-scoring** is *Tumbleweed* / *Sygo*. Combined with Go-surround, this is closer to a "Go variant with explicit territorial weighting" than to pure Go.
(c) **3D Go variants** exist (Cubic Go, Akron, several published). None I'm aware of use a fractal substrate.
(d) **Menger substrate + Go** is the genuinely-unprecedented combination. Hole-as-liberty-stealer is a substrate-specific dynamic that no published Go variant has.
(e) **Super-ko on Go-surround** is *classical Go's natural rule*. Standard mechanic, no novelty.
(f) **Expert-transfer test.** A Go player would understand the rules in 5 minutes. The novel pieces: (i) the menger active-cell map; (ii) influence-weighted scoring with r=1; (iii) the way fractal holes affect liberty counts. Total: 5–10 min to functional understanding.

**Closest known-game analogue:** **3D Go with influence-weighted scoring on a Menger sponge.** No published exact analogue. Within R19, this is the **Go-family** game; ranks 1 & 2 are the Tafl/outnumber-family.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on 2D 8×8 — a Hex/Othello hybrid. Rank-3 here is surround + influence-threshold on 3D menger — a Go/Tumbleweed hybrid. **Different families, but rank-3 is the closest R19 game to the Go-family that R8 is in.** Both share Go's surround/group primitive (or Hex's connection primitive — closely related). R8's strength is the narrative arc (chain → win) and 2D human-tractable scale; rank-3's strength is the Go-style life-and-death + fractal liberty geometry. **Rank-3 is the strongest R19 candidate for matching R8's strategic ceiling.**

**Player rebuttal.**
- The fractal-driven liberty geometry is **the only genuinely substrate-specific mechanic** I've encountered across the R19 games. It cannot be reproduced on any non-fractal substrate.
- Group-extension defence + sacrifice trade gives the game real Go-style depth that no R19 outnumber game provides.
- **Subtracts from novelty:** Go is maximally well-known; the surround-on-fractal pairing is novel only because no one has bothered to study it (likely because it's not a useful research direction in published Go-variant literature). The threshold-race scoring layer is shared with rank-1/2.

**Novelty score (post-adversary):** **6/10.** Same score as rank-1/2 but with different reasoning — substrate-specificity is higher here than in any other R19 game, but the Go base mechanic is universally familiar, so the net novelty lands at the same level. Above 5 because of the fractal-liberty pairing; below 7 because Go itself is ancient.

---

## Phase 5 — Verdict

**Team ID:** team-4
**Game ID:** 5048f71b62fd
**Rules Summary:** Place stones on a 9×9×9 Menger sponge to accumulate r=1 influence on owned cells. Go-style surround capture removes enemy groups with 0 liberties (holes don't count as liberties — the fractal *steals* them). Super-ko prevents repeat positions. First to >21.2 wins, typically ~25 plies.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.
**Quirks discovered:** super-ko is active (pilot's "add ko rule" recommendation was redundant). Surround threshold parameter is dead (numeric noise; engine ignores it). Corner cells with hole-neighbours can have effective liberty counts as low as 1 — extremely fragile.

### Scores (1–10)

- **Strategic Depth: 7** — Go-style group dynamics + threshold race + fractal liberty geometry. **Highest of the 6 R19 games.** Group extension, sacrifice trades, and corner-fragility exploitation are real strategic axes that rank-1/2's outnumber lacks.
- **Emergent Complexity: 6** — Alive vs dead groups, hole-as-liberty-stealer, chain-extension-defence are emergent and substrate-specific. Above rank-1/2's 6 in vocabulary.
- **Balance: 4** — Same structural P1 favour. Mirror loses for P2. Knowledge-asymmetric counter exists but requires Go-style reading.
- **Novelty (post-adversary): 6** — Substrate-specificity is highest here but the Go base is ancient. Same score as rank-1/2 with different reasoning.
- **Replayability: 6** — Group dynamics give more position variety than outnumber. Above rank-1's 5.
- **Overall "Would I play this again?": 6** — Once: yes, the corner-fragility mechanic is genuinely surprising. Repeatedly: yes — Go-style depth + substrate-specific liberty geometry give this the highest replayability ceiling of the R19 games. Anchor: above R17 mean (3.5), above R17 best (4.14), well below R8 (8) but the closest of the R19 games to R8's family.

### CLOSEST KNOWN-GAME ANALOG
**3D Go with influence-weighted scoring on a Menger sponge.** No published analogue. In-corpus: this is the closest R19 game to R8's "Connection Go" family (both share the Go group primitive).

### KILLER FLAWS
- **Mirror = P1 wins on tempo.** Same structural issue as all R19 games.
- **Surround threshold parameter is dead.** Engine ignores it; the rule blob has noise.
- **Short games (avg 27 moves, ~25 in optimal play) limit positional depth** despite high tactical depth.
- **Pilot's "add ko rule" suggestion reveals an evaluation gap.** The ko rule is already active. This is a documentation flaw inherited into evaluations.
- **The eval report's "this game's gen-6 leadership got dethroned" reading.** I think this is a fitness-metric artifact, not a quality verdict — surround's depth is harder for PPO to learn fully, depressing GE. **The dethroning underrates this game.**

### BEST QUALITY
**Surround capture in 3D fractal substrate where holes steal liberties.** The hole-as-liberty-stealer mechanic is the only genuinely substrate-specific dynamic in R19. Combined with Go-style group-life management, it gives the game a strategic ceiling that the outnumber games can't reach. **The closest R19 game to R8's family** and the strongest candidate for matching R8's 8/10 ceiling on a longer training budget.

### MENGER STRUCTURAL CONTRIBUTION
**The largest of any R19 game I've evaluated.** Surround + fractal holes is a structural pairing that creates substrate-specific liberty geometry inseparable from strategy. ~+2 depth, ~+1 novelty over a regular 9³ cube. The substrate is doing essential work — flattening to a regular cube would lose Go's most interesting mechanic on this board.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (cross-cutting recommendation across all R19 games). Same as pilot.

Secondary improvements:
- **Increase threshold to 25–28** to extend games slightly. Trades tactical compression for positional development.
- **Document the active super-ko rule** in briefing/eval-prompt — pilot wasted a recommendation slot suggesting it.
- **Strip the noise threshold parameter** from surround capture rules in the rule blob — it's inert and confuses evaluators.
- **Test against a connection secondary win** (R8 family). Surround + connection on a 3D fractal would be very close to "Connection Go on Menger" — strongest R20 candidate.
- **Longer PPO training budget for surround games** (or a different fitness metric). The pilot's intuition about the dethroning being a metric artifact is consistent with my play experience: surround's depth is real but learning it takes more episodes.

### Notes on the dethroning (vs outnumber rivals)
**I agree with the pilot's read.** This game is human-strategically deeper than ranks 1 & 2 (outnumber variants) but PPO + GE may underrate it because: (a) surround captures fire less often per game (need 0 liberties on a group, not 2 on a single stone); (b) group-life arithmetic is harder to learn than adjacency counts; (c) fractal liberty geometry compounds the learning difficulty. R20 should explicitly test surround-only seeds with longer training to see if their GE rebounds. **Rank-3 may be the most under-rated R19 game.**

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-4_game5048f71b62fd.md`.*
