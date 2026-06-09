# Probe A/B Eval — team-{{TEAM_N}} — Game Z

**Team ID:** team-{{TEAM_N}}
**Game Label:** Z (blind; do not consult `.blind_mapping.json`)
**Substrate:** hex_rhombus (axial triangular lattice), axis 22, 484 total cells / 484 active, max_degree 6, pie_rule=True
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `evaluations/probe_ab/play.py --game Z` (run `--rules` first for rules; `--control` for influence map).

---

## Phase 1 — Rule Comprehension

**Rules derivation.** Run the following and derive all mechanics from its output:

    python evaluations/probe_ab/play.py --game Z --rules

**Board.** Hex-adjacency rhombus, axis 22 (484 cells, all active). Axial (q, r) coordinates; cell index = q + 22*r. Interior cells degree 6; acute-corner cells degree 2; obtuse-corner cells degree 3. Board displays as 22 sheared rows.

**Turn structure.** Alternating, 1 stone/turn, P1 first. Max_turns = 200.

**Action space.** {{NUM_ACTIONS}} actions = 484 placement + 1 pass + 1 pie_swap. No move actions. Placement legal at any empty cell. pass=484, swap=485.

**Placement & capture.** Capture rule = **{{CAPTURE_RULE}}** (threshold {{CAPTURE_THRESHOLD}}). {{Firing condition from --rules output.}}

**Propagation.** {{PROP_TYPE}} (radius={{R}}, strength={{S}}, decay={{D}}). Placement adds ±strength·decay^dist to `board_values` within radius. Sign +1 P1 / −1 P2. Clamped [−100,100].

**Win condition.** {{From --rules: score-race threshold or influence-field connection. State mechanically. Komi_p2={{KOMI}}.}} Equal → draw. Timeout → piece-count majority (score-race game) or total controlled-cell count (influence-connection game); equal → draw.

**Pie rule.** After P1's first stone, P2 may swap seats (action 485). Pie corrects first-mover advantage.

**Degeneracy check.**
- {{Inert fields, dead rule paths, soft violations — e.g. influence field that never enters win logic; vestigial thresholds.}}
- {{Board geometry quirks — hex-rhombus edge effects, corner irregularity, degree-2 acute corners.}}

---

## Phase 2 — Strategic Play

All moves engine-verified through `play.py --game Z`. Action IDs = cell indices (q + 22*r) for placement; pass=484; pie_swap=485.

Use `--control` to observe the influence control map.

### Game 1 — {{P1 line}}
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{move-by-move; flag captures, score/control progress at decision points, decisive moments.}}
Reflection: {{binding constraint? what did placement order force?}}

### Game 2 — {{P2 contest}}
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{...}}
Reflection: {{...}}

### Game 3 — {{Adversarial / seat-swap / novelty-stress}}
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{...}}

### Strategy guides
**P1 (offence / score push or connection attempt):** {{playbook}}
**P2 (defence + contest; pie/komi-aware):** {{playbook}}

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** {{yes/no + evidence}}
**Counter-play.** {{real / partial / absent; each strategy's counter}}
**Short-term vs long-term.** {{tactical depth vs strategic horizon; does the 22×22 board support longer planning horizons than R21's 9×9/9×9×9?}}
**Emergent concepts observed.** {{influence wells, score-race pressure, capture cascades, connection races, controlled-region topology, …}}
**Does hex_rhombus topology matter?** {{would the same rules on a flat square grid preserve the dynamics? What does degree-6 hex adjacency add?}}
**Does the propagation kernel matter?** {{radius/decay value; does the influence field enter win logic or just decorate the observation tensor?}}
**Capture-rule contribution.** {{did captures actually fire? how often, what did they buy?}}
**First-mover advantage / seat balance.** {{from your games. Did komi_p2={{KOMI}} / pie correct the bias, or does residual P1 advantage remain?}}

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of {{…}}. Argument:
(a) {{Score-race influence ≈ territorial/race scoring? Connection ≈ Hex?}}
(b) {{Capture analog: outnumber→Tafl/Ataxx; surround→Go; custodian→Othello/Reversi.}}
(c) {{Does "{{CAPTURE_RULE}} + {{PROP_TYPE}} + win-condition" exist as a published game? Reference R8 Connection Go + R17–R21 corpus.}}
(d) {{Substrate: hex-rhombus degree-6 lattice — has this exact substrate appeared in any prior run? How does it differ from the menger/carpet/grid topologies of R17–R21?}}
(e) {{Expert-transfer: could a Go+Hex+Othello player learn this in N min? What's the irreducible novel piece?}}

**Closest known-game analogue:** {{name + 1-line.}}
**Comparison to R8 Connection Go (replay anchor 4.10).** {{Same family / different? Where does this sit relative to R8's depth/playability?}}
**Comparison to R19/R20/R21 best.** {{Richer or thinner than R19 5.0 / R20 4.80 / R21 3.69? What changed?}}

**Novelty score (post-adversary):** {{N}}/10. {{Above re-skin (2–3) because X; below genuinely-novel (8–9) because Y. Anchor: R17 3.50, R8 4.10, R19 top 4.8/5.0, R20 4.80, R21 3.69.}}

---

## Phase 5 — Verdict

**Team ID:** team-{{TEAM_N}}
**Game Label:** Z
**Rules Summary:** {{1–2 sentence plain-English experience of the game.}}
**Substrate:** hex_rhombus, axis 22, 484/484 cells, max_degree 6, pie_rule=True, komi_p2={{KOMI}}.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only).
**Soft violations flagged:** {{none / list}}.

### Scores (1–10)
- **Strategic Depth: {{N}}** — {{meaningful decisions/game, branching at decision points, medium-term concepts.}}
- **Emergent Complexity: {{N}}** — {{patterns/tactics not explicitly written in the rules.}}
- **Balance: {{N}}** — {{seat balance from your games + pie. Residual P1 advantage?}}
- **Novelty (post-adversary): {{N}}** — see Phase 4. {{one line.}}
- **Replayability: {{N}}** — {{once strategies are public, does it still reward play? opening variety?}}
- **Overall "Would an agent team play this again?": {{N}}** — {{one line. Anchors: R8 4.10, R17 3.5/4.14, R19 4.375/4.8/5.0, R20 3.73/4.80, R21 3.69. > 5.0 clears the R19 ceiling (G1).}}

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

## Q-vs-Z Comparison

**Which game would you rather play again?** {{Q / Z / equal}}
**By how many Overall points?** {{e.g. "+0.5 Overall in favour of one label"}}
**Key differentiator:** {{the single mechanic or dynamic that most separates Q from Z in your experience.}}

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/probe_ab/team-{{TEAM_N}}_gameZ.md`.*
