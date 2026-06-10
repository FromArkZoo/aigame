# Stage 3 blind eval — team-{{TEAM_N}} — Game V

**Team ID:** team-{{TEAM_N}}
**Game Label:** V (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6.
**Evaluator:** single-agent team running both player roles and Novelty Adversary sequentially.
**Helper:** `evaluations/stage3_ab/play.py --game V` (run `--rules` first; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Run the following and derive all mechanics from its output:

    python evaluations/stage3_ab/play.py --game V --rules

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r) coordinates; cell index = q + 22*r. Interior cells degree 6; acute-corner cells degree 2; obtuse-corner cells degree 3.

**Turn structure.** {{from --rules: alternating, 1 stone/turn. Max_turns=?}}

**Action space.** {{NUM_ACTIONS}} actions = 484 placement + 1 pass {{+ 1 pie_swap if applicable}}. Placement legal at any empty cell.

**Placement & capture.** Capture rule = **{{CAPTURE_RULE}}** (from --rules output). {{Describe firing condition in your own words.}}

**Propagation.** Influence field (radius={{R}}, strength={{S}}, decay={{D}}). Placement adds ±strength·decay^dist within radius. Values clamped [-100, 100].

**Win condition(s).** {{State mechanically from --rules. If the two sides have distinct win structures, describe and score each side separately.}}

**Pie rule.** {{ON / OFF — from --rules.}}

**Komi_p2.** {{value — from --rules.}}

**Degeneracy check.**
- {{Inert fields, dead rule paths, soft violations — e.g. influence field that never enters win logic; vestigial thresholds.}}
- {{Board geometry quirks — hex-rhombus edge effects, corner irregularity, degree-2 acute corners.}}

---

## Phase 2 — Strategic Play (both roles)

All moves engine-verified through `play.py --game V`. Action IDs = cell indices (q + 22*r); pass=484; swap=485 (if pie rule is on).

Use `--control` to observe the influence control map.

### Game 1 — as Player 1
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{move-by-move; flag captures/conversions, progress toward your win condition at decision points, decisive moments.}}
Reflection: {{binding constraint? what did placement order force? did your win condition feel achievable?}}

### Game 2 — as Player 2
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{move-by-move; flag captures/conversions, progress toward your win condition.}}
Reflection: {{how did your win path interact with the opponent's? if the pie rule is on, did it change your first-move thinking?}}

### Game 3 — Adversarial / novelty-stress
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{attempt the most chaotic or atypical line — try to break assumptions.}}

### Strategy guides
**As Player 1:** {{playbook — how do you pursue your win condition? influence field use, routing, timing.}}
**As Player 2:** {{playbook — how do you pursue your win condition? defence + contest; pie/komi-aware where applicable.}}

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** {{yes/no + evidence for each role}}
**Counter-play.** {{real / partial / absent; how does each player's strategy constrain the other?}}
**Short-term vs long-term.** {{tactical depth vs strategic horizon; does the 22×22 board support longer planning horizons than R21's 9×9/9×9×9?}}
**Emergent concepts observed.** {{influence wells, capture/conversion cascades, connection races, controlled-region topology, …}}
**Does hex_rhombus topology matter?** {{would the same rules on a flat square grid preserve the dynamics? What does degree-6 hex adjacency add?}}
**Does the propagation kernel matter?** {{radius/decay value; does the influence field enter win logic materially, or just decorate the observation tensor?}}
**Capture-rule contribution.** {{did captures/conversions actually fire? how often, what did they buy in terms of game state?}}
**First-mover advantage / seat balance.** {{from your games. Did the pie rule / komi (where present) correct the bias, or does residual advantage remain for either side?}}

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of {{…}}. Argument:
(a) {{Connection ≈ Hex? Score-race influence ≈ territorial/race scoring?}}
(b) {{Capture analog: field-dominance flip ≈ Othello/Reversi? Surround ≈ Go? Outnumber ≈ Tafl/Ataxx? Custodian ≈ Othello/Reversi?}}
(c) {{Does "{{CAPTURE_RULE}} + influence propagation + {{WIN_STRUCTURE}}" exist as a published game? Reference R8 Connection Go + R17–R21 corpus.}}
(d) {{Substrate: hex-rhombus degree-6 lattice — has this exact substrate appeared in any prior run? How does it differ from the menger/carpet/grid topologies of R17–R21?}}
(e) {{Expert-transfer: could a Go+Hex+Othello player learn this in N min? What's the irreducible novel piece?}}

**Closest known-game analogue:** {{name + 1-line.}}
**Comparison to R8 Connection Go (replay anchor 4.10).** {{Same family / different? Where does this sit relative to R8's depth/playability?}}
**Comparison to R19/R20/R21 best.** {{Richer or thinner than R19 5.0 / R20 4.80 / R21 3.69? What changed?}}

**Novelty score (post-adversary):** {{N}}/10. {{Above re-skin (2–3) because X; below genuinely-novel (8–9) because Y. Anchor: R17 3.50, R8 4.10, R19 top 4.8/5.0, R20 4.80, R21 3.69.}}

---

## Phase 5 — Verdict

**Team ID:** team-{{TEAM_N}}
**Game Label:** V
**Rules Summary:** {{1–2 sentence plain-English description of the game experience.}}
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule={{ON/OFF}}, komi_p2={{KOMI}}.
**Turn Structure:** alternating
**Hybrid actions:** {{no (place-only) / yes — specify}}
**Soft violations flagged:** {{none / list}}.

### Per-role sub-scores (1–10)

**As Player 1:**
- Strategic Depth: {{N}} — {{meaningful decisions, branching, medium-term concepts.}}
- Emergent Complexity: {{N}} — {{patterns not explicitly in the rules.}}
- Replayability: {{N}} — {{opening variety, strategic depth after strategies are known.}}

**As Player 2:**
- Strategic Depth: {{N}} — {{meaningful decisions, branching, medium-term concepts.}}
- Emergent Complexity: {{N}} — {{patterns not explicitly in the rules.}}
- Replayability: {{N}} — {{opening variety, strategic depth after strategies are known.}}

### Role-averaged scores (1–10)

- **Strategic Depth: {{N}}** — {{average of P1/P2 sub-scores; one line.}}
- **Emergent Complexity: {{N}}** — {{average; one line.}}
- **Balance: {{N}}** — {{seat balance from your games. Did either role feel structurally advantaged?}}
- **Novelty (post-adversary): {{N}}** — see Phase 4. {{one line.}}
- **Replayability: {{N}}** — {{average; one line.}}
- **Overall "Would an agent team play this again?": {{N}}** — {{one line. Anchors: R8 4.10, R17 3.5/4.14, R19 4.375/4.8/5.0, R20 3.73/4.80, R21 3.69. > 5.0 clears the R19 ceiling (G1).}}

### Fairness perception (mandatory)

**Fairness perception: {{1–5}} — {{one sentence of evidence. 1=strongly P1-favored, 3=balanced, 5=strongly P2-favored.}}**

### CLOSEST KNOWN-GAME ANALOG
{{1–2 sentences: closest analog inside this corpus AND in the broader literature.}}

### KILLER FLAWS
- {{specific flaw 1}}
- {{specific flaw 2}}

### BEST QUALITY
{{the crown-jewel mechanic/pattern that lifts it above floor — or absence thereof.}}

### HEX_RHOMBUS STRUCTURAL CONTRIBUTION
{{does the degree-6 hex topology shape strategy, or could it flatten to a square grid with minimal loss? Anchor against R19's menger > carpet > grid topology finding and the R8-replay board-size-limit concern. Does 22×22 open up additional strategic depth?}}

### IMPROVEMENT IDEAS
**Single best change:** {{one specific, falsifiable change that would most improve the game.}}
Secondary:
- {{…}}

---

## Cross-game comparison (fill after all assigned games are done)

**Ranking of your assigned games by Overall score:** {{D=N, V=N, X=N (if assigned all three)}}
**Which game would you most want to play again?** {{label}}
**By how many Overall points above the next-ranked game?** {{e.g. "+0.5 Overall"}}
**Key differentiator:** {{the single mechanic or dynamic that most separates your top-ranked game from the others.}}

---

*Output saved to `evaluations/stage3_ab/team-{{TEAM_N}}_gameV.md`.*
