# Run 19 Evaluation — team-pilot — Game 5048f71b62fd

**Team ID:** team-pilot
**Game ID:** `5048f71b62fd` (Menger rank-3, GE 0.3158, ELO 2354.6)
**Substrate:** Menger sponge (axis 9, 400/729 active, max_degree 6)
**Helper:** `eval_run19_helper.py --game 5048f71b62fd`
**Note:** Crossover from `ebf0a3e1c424` × `d21ef16c4945`. The eval report identifies this as the gen-6 leader that got dethroned by outnumber-based games in gens 7-8.

---

## Phase 1 — Rule Comprehension

**Board / Turn structure / Action space.** Same as menger rank-1 and rank-2.

**Capture (surround-2).** **Go-style group-liberty capture.** When you place a stone, check each enemy group adjacent to your placement: if the group has 0 liberties (no empty active cells adjacent to any group member), the entire group is removed from the board. Liberties count empty active cells; holes do NOT count as liberties. **The fractal hole pattern reduces effective liberties** — a stone surrounded by 2 holes and 2 enemies is captured.

**Propagation (influence, r=1, s=1.0, d=0.5).** Same kernel as menger rank-1.

**Win (threshold-race > 21.212).** **29% lower than rank-1's 29.7.** Combined with the harder-to-build (groups must stay alive) requirement, threshold is reached with relatively few stones. Avg game length 27.2 moves vs rank-1's 38.8 — 30% shorter.

**Degeneracy check.** No soft violations.

---

## Phase 2 — Strategic Play

### Game 1 — Surround capture in 3D corner

Sequence: `0,1,9,81,162` (5 plies).

Plot:
- P1 (0,0,0); P2 (1,0,0); P1 (0,1,0); P2 (0,0,1).
- After 4 moves: P2 has stones at (1,0,0) and (0,0,1). The single P2 stone at (0,0,1) has only 4 axis-aligned neighbours: (1,0,1) [hole], (0,1,1) [hole], (0,0,0) [P1], (0,0,2) [empty].
- **Move 5: P1 places (0,0,2). The P2 group {(0,0,1)} now has zero liberties** — all neighbours are holes or P1. Group is removed from the board.
- After 5 moves: P1 has 3 stones at (0,0,0), (0,1,0), (0,0,2). P2 has 1 stone at (1,0,0). P1 = +2.5, P2 = +0.5.

Reflection: **The fractal hole pattern makes surround capture VERY aggressive.** P2's (0,0,1) had only 1 active cell as liberty (i.e., (0,0,2) — the rest were holes or already enemies). One P1 placement closed the only liberty and captured the group. **This is a fundamental tactical change from outnumber-2 (rank-1):** outnumber needs 2 friendlies adjacent to the captured cell; surround needs 0 liberties on the entire enemy group, which can be triggered by a single placement that closes the last liberty.

### Game 2 — Group preservation strategy (P1)

(Sketched analytically.)

To win without losing groups, P1 must build "alive" groups — groups with at least 2 distinct liberties so that a single enemy placement cannot capture them. In Go this is the "two-eye" rule. On menger with r=1 influence kernel, this requires building ≥ 4-stone groups with multiple internal/boundary liberties.

Example alive shape: a 4-stone "T" at (0,0,0), (1,0,0), (0,1,0), (0,2,0). The group has liberties: (2,0,0), (1,1,0)[hole], (0,3,0)[active], (0,1,1)[hole], (0,0,1)[active]. Counting only active cells: 3 liberties. Capture requires P2 to fill ALL 3 liberties — 3 moves of investment. Meanwhile P1 builds more groups.

### Game 3 — Mirror tempo race (same as menger rank-1)

(Sketched.)

If both sides build alive groups and avoid captures, the game reduces to threshold race. P1 wins by tempo. Same first-mover dynamic as rank-1.

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** **Three** (one more than rank-1):
1. **Group preservation + threshold race** (P1's playbook). Build alive multi-stone groups; race to 21.2.
2. **Surround attack** (P2's playbook). Look for P1 single stones in corner/edge positions where holes reduce liberties; capture aggressively.
3. **Trade groups for tempo** (advanced). Sacrifice a small group to gain access to a stronger position. This is genuinely Go-like and has no analogue in carpet rank-1 or 2.

**Counter-play.** Real and richer than rank-1. Surround capture creates Go-style life-and-death tension that outnumber doesn't have. P2 has more attacking options because surround can fire from multiple positions; P1 must defend liberties as well as build influence.

**Short-term vs long-term.** ~14-ply horizon (avg game 27 moves). But each placement has potentially deeper consequences (group death) than rank-1.

**Emergent concepts observed.**
- **Go-style life-and-death** in a 3D fractal context. The fractal hole pattern reduces stone liberties, making single stones extremely vulnerable. Multi-stone alive groups are the only stable structures.
- **Capture-as-tempo-gain.** Removing an entire group adds the captured stones' influence-loss to the captor's effective lead.
- **Hole-as-liberty-stealer.** Holes count against liberties without being part of either side. This is the most genuinely substrate-driven mechanic in any R19 game I've evaluated.

**Does the menger substrate matter?** **Yes, the most of any R19 game I've seen.** Surround capture + fractal holes is a structural pairing: holes amplify capture pressure beyond what any regular substrate would allow. The same rules on a regular 9×9×9 grid would be much less aggressive — every stone would have at minimum 3 liberties from the start.

**Does the propagation kernel matter?** Same r=1 kernel as rank-1; same conclusions about adjacency vs proximity clustering.

**Capture-rule contribution.** Major. Surround capture creates Go-style strategic tension that the other 5 R19 games lack. This is the most game-defining capture rule across the 6 games.

**First-mover advantage / seat balance.** Same P1 favour from mirror dynamics. PPO trained-vs-random WR is 1.000 across all 3 seeds; final winrate 0.500 — clean training. Balance is achievable but requires the asymmetric counter (P2 plays surround attack, not mirror).

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is influence + Go-style surround + threshold-race on a 3D fractal. Argument:

(a) **Surround (Go) capture** is one of the oldest mechanics in board games (Go ~3000 BCE).
(b) **Influence-based threshold-race** — same family as carpet rank-1, menger rank-1, menger rank-2.
(c) **The combination "surround + influence + threshold"** doesn't appear in published abstract-game literature. Go has implicit territory scoring (count surrounded empty space + stones); this game has explicit influence scoring (radius-2 weight sum). Distinct mechanic, same family.

(d) **Menger sponge substrate** — same novelty axis as menger rank-1 and 2.

(e) **Expert-transfer test.** A Go player would recognise surround capture immediately. Influence-as-scoring would feel foreign but learnable in 5 minutes. Total: 5-10 minutes to functional understanding.

**Closest known-game analogue:** **Go with influence-weighted scoring on a Menger sponge.** Within R19, this is the **Go-family game**; rank-1 (`1f9191b5d4e6`) is the Tafl-family equivalent.

**Comparison to R8's Connection Go (8/10 ceiling).** R8 used custodian + connection. R19 menger rank-3 uses surround + influence-threshold. Different family. **However, this is the closest R19 game to the *Go family* that R8 belongs to.** R8 itself was framed as "Connection Go" — a Hex-Go hybrid. R19 menger rank-3 is "Influence Go on menger" — also a Go-derived hybrid. Both share the Go primitive (surround + group dynamics). R19 menger rank-3 is structurally the **closest R19 game to R8's strategic family** in terms of what makes the game interesting.

**Player rebuttal.**
- **Surround capture in 3D fractal** is a genuinely novel pairing. The fractal hole pattern's effect on liberty counts is substrate-driven and creates real Go-meets-fractal tension that doesn't exist in any published game.
- **Group preservation + influence accumulation** dual-objective is novel — Go has implicit territory; this game makes scoring explicit and weights it geometrically.
- Subtracting from novelty: Go's mechanics are extremely well-known.

**Novelty score (post-adversary):** **6/10.** Same as menger rank-1 and 2. The substrate + Go family combination is the strongest novelty driver. Above carpet rank-1/2/3 because Go-family + fractal is more structurally distinctive than influence-Tafl hybrids.

---

## Phase 5 — Verdict

**Team ID:** team-pilot
**Game ID:** 5048f71b62fd
**Rules Summary:** Place stones on a 9³ menger sponge to accumulate influence on cells you own. Go-style surround capture removes entire enemy groups with zero liberties. First to >21.2 effective influence wins — typically takes ~27 moves total.
**Substrate:** Menger sponge, axis 9, 400/729 active, max_degree 6.
**Turn Structure:** alternating, P1 first.
**Hybrid actions:** no.
**Soft violations flagged:** none.

### Scores (1–10)

- **Strategic Depth: 6** — **Highest of the 6 R19 games.** Go-style life-and-death + influence accumulation creates genuinely deeper decisions than the outnumber/custodian variants. Group preservation, sacrifice, and tempo trades are real strategic axes.
- **Emergent Complexity: 6** — **Highest of the 6 R19 games.** Go-style alive/dead groups + 3D fractal liberty geometry + influence build-up. Multiple emergent concepts (alive groups, sacrifice trade, hole-as-liberty-stealer).
- **Balance: 4** — Same mirror = P1 win. PPO trains cleanly (winrate 0.500 with high TVR), suggesting learned balance.
- **Novelty (post-adversary): 6** — Same as menger rank-1/2 in score, but driven by the Go-family + 3D fractal pairing rather than the Tafl-family.
- **Replayability: 6** — **Highest of the 6 R19 games.** Go-style strategic depth means many positions reward different play styles. The 400-cell board has lots of room for variation.
- **Overall "Would I play this again?": 6** — **Highest of the 6 R19 games I've evaluated.** Above carpet rank-1 (5), menger rank-1 (5), menger rank-2 (5), carpet rank-2 (4), carpet rank-3 (4). The Go-style mechanics give this game a strategic ceiling that the others lack.

### CLOSEST KNOWN-GAME ANALOG
**Go with influence-weighted scoring on a Menger sponge.** Within the project corpus, this is the closest R19 game to R8's "Connection Go" family — both inherit Go's surround/group primitive.

### KILLER FLAWS
- **Mirror = P1 win** (same as all R19 games).
- **Hole-as-liberty-stealer is BRUTAL for single stones.** Single stones in corner/edge positions can be captured in 2-3 moves; this might encourage overly cautious early play.
- **Short games (avg 27 moves) limit positional depth** despite high tactical depth.
- **The eval report says this game's gen-6 leadership got dethroned in gens 7-8.** Evolution preferred outnumber to surround. Possible reason: surround's high tactical complexity is harder for PPO to learn fully in 10000 episodes, so it scored lower under C2 averaging despite being a stronger game for humans.

### BEST QUALITY
**Go-style surround capture in a 3D fractal substrate.** This is the only R19 game with genuine life-and-death tension. The fractal hole pattern amplifies the capture pressure in ways no regular substrate would, creating real combinatorial novelty. **The closest R19 game to R8's family** and the strongest candidate for matching R8's 8/10 ceiling.

### MENGER STRUCTURAL CONTRIBUTION
**The largest of any R19 game.** Surround capture + fractal holes is a structural pairing that creates substrate-specific liberty geometry. Estimate: flattening to a regular 8³ or 9³ cube would lose ~2 points of depth and most of the game's distinctive character. This is the only R19 game where the substrate is *inseparable from the strategy*.

### IMPROVEMENT IDEAS
**Single best change: pie rule** (same as all R19 games — addresses the mirror = P1 win flaw).

Secondary improvements:
- **Increase threshold to 25** to extend games slightly and allow more positional development.
- **Add a "ko rule" analogue** to prevent capture-recapture loops if any exist.
- **Test against a connection secondary win** — combining surround + connection would be very close to R8's Connection Go on a 3D fractal substrate. **Strongest R20 candidate from this evaluation.**

### Notes on the dethroning
The eval report says this game led at gen 6 and was overtaken by outnumber-based games in gens 7-8. From this human evaluation, **the dethroning is likely a fitness-metric artifact, not a quality verdict.** Surround capture's strategic depth is harder for GE to measure (depends on group structure, tempo, sacrifice trades) than outnumber's local capture (depends on adjacency counts). PPO may learn surround less completely in 10000 episodes, depressing GE. **R20 should consider re-running with surround-only seeds or a longer training budget for surround-based games.**

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run19/team-pilot_game5048f71b62fd.md`.*
