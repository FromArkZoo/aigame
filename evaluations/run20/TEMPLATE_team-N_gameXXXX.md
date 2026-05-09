# Run 20 Agent-Team Eval — team-{{TEAM_N}} — Game {{GAME_ID}}

**Team ID:** team-{{TEAM_N}}
**Game ID:** {{GAME_ID}} ({{SUBSTRATE_RANK}}, 15-seed mean GE {{GE15}}, σ {{SIGMA}}, depth {{DEPTH}})
**Substrate:** {{SUBSTRATE}} (axis {{AXIS}}, {{ACTIVE}} active cells / {{TOTAL}} grid positions, max_degree {{MAX_DEG}}, pie_rule={{PIE}})
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run20_helper.py --game {{GAME_ID}}` (see `briefing_{{SUBSTRATE}}_{{GAME_ID}}.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** {{Substrate description from first principles. For menger: 9×9×9 cube with 329 inactive holes per the level-2 Menger sponge fractal pattern (active=400); cell index = z*81 + y*9 + x; coords with two or three base-3 digits equal to 1 are inactive. For carpet: 9×9 grid with 17 inactive holes per the level-2 Sierpinski carpet pattern (active=64); cell index = y*9 + x. For grid: full 9×9 = 81-cell flat grid with no holes.}}

**Turn structure.** Alternating, 1 piece per turn. P1 first. Max_turns = {{MAX_TURNS}}.

**Action space.** {{NUM_ACTIONS}} actions = {{TOTAL}} placement + 1 pass{{ + 1 pie if applicable}}. **No move actions** (D1 hybrid ban active). Placement legal at any empty active cell.

**Placement & capture.** Placement: empty active cell, no first-move restriction. Capture rule = **{{CAPTURE_RULE}}** (threshold {{CAPTURE_THRESHOLD}}). {{Describe firing condition specifically: outnumber-N → place at empty cell; if N or more friendly stones are adjacent to an enemy stone, that enemy is captured (cleared). custodian-N → place such that an enemy run of length ≥1 is bracketed by N+ friendly stones along an axis, the run flips to placer.}}

**Propagation.** {{PROP_TYPE}} (radius={{R}}, strength={{S}}, decay={{D}}). On placement, the engine adds ±strength × decay^distance to `board_values[cell]` for every cell within radius. Sign = +1 if P1 places, −1 if P2. Clamped to [−100, 100].

**Win condition.** Threshold-race. After every move, sum each player's `board_values` over cells they currently own. The first player whose effective sum exceeds **{{THRESHOLD}}** wins. {{Note target_dimension_p2: -1 means P2 mirrors P1's accumulator (negated); +1 means P2 has a separate accumulator.}} Equal margins → draw. Max-turn timeout: highest effective sum wins.

**Pie rule.** {{If pie_rule=True: After P1's first move, P2 may swap seats (taking P1's first move as their own). If False: not available.}}

**Degeneracy check.**
- {{Note any inert fields, dead rule paths, or known soft violations from the briefing.}}
- {{Note board geometry quirks — fractal hole patterns, neighbour count irregularity, grid edge effects.}}

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run20_helper.py`. Action IDs = cell indices for placement; pass = {{TOTAL}}{{; pie = TOTAL+1 if pie_rule}}.

### Game 1 — {{Strategy variant 1, e.g., P1 center-grab}}

Sequence: `{{action_csv}}` ({{N}} plies).

Plot:
- {{move-by-move narrative. Flag captures, threshold totals at decision points, decisive moments.}}

Reflection (P1 / P2): {{What was the binding constraint? What did the placement order force?}}

### Game 2 — {{Strategy variant 2, e.g., P2 counter}}

Sequence: `{{action_csv}}` ({{N}} plies).

Plot:
- {{...}}

Reflection: {{...}}

### Game 3 — {{Adversarial / seat-swap / novelty-stress strategy}}

Sequence: `{{action_csv}}` ({{N}} plies).

Plot:
- {{...}}

### Strategy guides

**P1 (offence/threshold push):** {{One-paragraph playbook.}}

**P2 (defence + threshold contest):** {{One-paragraph playbook.}}

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** {{Yes/no, list them with brief evidence.}}

**Counter-play.** {{Real, partial, or absent? Each strategy's known counter.}}

**Short-term vs long-term.** {{Tactical depth vs strategic horizon. The threshold value and game length set the planning depth.}}

**Emergent concepts observed.**
- {{Named patterns: e.g., "influence wells", "threshold flip", "capture cascades", "edge stranding".}}
- {{...}}

**Does {{SUBSTRATE}} matter?** {{Specifically — would the same game on a flat 9×9 grid (or 4³ cubic for menger) preserve the dynamics? For grid_control: would the same rules on menger/carpet preserve the dynamics?}}

**Does the propagation kernel matter?** {{r=1 vs r=2; decay 0.5 vs other. Compare expected influence footprint to observed play.}}

**Capture-rule contribution.** {{Did captures actually fire in your games? How often, and what did they buy?}}

**First-mover advantage / seat balance.** {{From your games + the trained-vs-trained 0.500 reference. Did one seat dominate? Pie rule active or not — did it correct the bias?}}

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of {{...}}. Argument:

(a) **Threshold-race influence games** are {{closest analogs in the broader board-game literature: territorial scoring? race-based? Othello scoring without flipping?}}.
(b) **{{CAPTURE_RULE}} capture** is {{closest analog: outnumber→Tafl/Ataxx; surround→Go; custodian→Othello/Reversi}}.
(c) **The combination "{{CAPTURE_RULE}} + influence + threshold-race"** {{exists / does not exist as a published game; reference R17/R18/R19 prior corpus and R8 Connection Go.}}
(d) **{{SUBSTRATE}} substrate.** {{Has fractal Hausdorff-dim play on this exact substrate been studied? What does the hole pattern add or subtract? For grid: does flat-grid + custodian + influence + threshold-race exist as a published game?}}
(e) **Expert-transfer test.** {{Could a Go + Othello + Hex player understand this game in N minutes? What's the irreducible new piece they'd have to learn?}}

**Closest known-game analogue:** {{name + 1-line description.}}

**Comparison to R8's Connection Go (8/10 ceiling).** R8 was custodian + connection on a 2D grid. This game is {{CAPTURE_RULE}} + influence + threshold-race on {{SUBSTRATE}}. {{Is R20 in the same family? A different family entirely? If different, where does R20 sit relative to R8's depth/playability?}}

**Comparison to R19 best.** R19 menger top-3 was `5048f71b62fd` surround capture (5.0/10), R19 menger top-1 was `1f9191b5d4e6` outnumber-2 (4.8/10). {{Is this R20 game richer or thinner than the R19 ones? What changed?}}

**Player rebuttal (P1 + P2).**
- {{Specific patterns that don't transfer cleanly from any single ancestor.}}
- {{What the substrate-specific topology actually adds beyond what the rules alone would on a regular grid.}}
- {{What subtracts novelty — inert mechanics, vestigial fields, etc.}}

**Novelty score (post-adversary):** {{N}}/10. {{Reasoning: above pure re-skin (2-3) because X; below "genuinely new" (8-9) because Y. Anchor against R17 mean (3.50), R8 (8/10), R19 menger top (4.8).}}

---

## Phase 5 — Verdict

**Team ID:** team-{{TEAM_N}}
**Game ID:** {{GAME_ID}}
**Rules Summary:** {{1-2 sentence plain-English summary capturing the agent's experience of the game.}}
**Substrate:** {{SUBSTRATE}}, axis {{AXIS}}, {{ACTIVE}}/{{TOTAL}} cells, max_degree {{MAX_DEG}}{{, pie_rule={{PIE}}}}.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** {{none / list from briefing}}.

### Scores (1–10)

- **Strategic Depth: {{N}}** — {{Justify: number of meaningful decisions per game, branching factor at decision points, presence of medium-term concepts (territory, influence shape, race-tempo). For depth-rich games (`5f5c72e15220`, `d1dbc6568fc7`) — does the engine-measured 0.79+ depth show up subjectively or is it a metric artifact?}}
- **Emergent Complexity: {{N}}** — {{Patterns and tactics that arise from the rules but aren't explicitly written in. Threshold-flip moments, influence-shadow blocking, capture-cascade chains, etc.}}
- **Balance: {{N}}** — {{Seat balance from your games + training reference. Does one seat dominate? Pie rule active (carpet only) — does it correct or sit inert?}}
- **Novelty (post-adversary): {{N}}** — see Phase 4. {{One-line summary.}}
- **Replayability: {{N}}** — {{Once known strategies are public, does the game still reward play? Is there meaningful position variety from move 1, or do openings collapse to a small set?}}
- **Overall "Would an agent team play this again?": {{N}}** — {{One-line summary. Anchors: R8 = 8, R17 mean = 3.5, R17 best = 4.14, R19 menger top = 4.8, R19 production mean = 4.375.}}

### CLOSEST KNOWN-GAME ANALOG
{{1-2 sentences naming the closest analog inside this project corpus AND in the broader literature.}}

### KILLER FLAWS
- {{Flaw 1, with specificity.}}
- {{Flaw 2.}}
- {{...}}

### BEST QUALITY
{{What is genuinely interesting about this game? The crown-jewel mechanic or pattern that makes it score above floor.}}

### {{SUBSTRATE}} STRUCTURAL CONTRIBUTION
{{Specifically: does the fractal hole pattern shape strategy, or could this be flattened to a regular grid with the same rules and minimal loss? For grid_control: does flat-grid lose anything that menger or carpet adds? Anchor against R19's finding that menger > carpet > grid for substrate quality.}}

### IMPROVEMENT IDEAS
**Single best change:** {{One specific, falsifiable change that would most improve the game.}}

Secondary improvements:
- {{...}}
- {{...}}

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run20/team-{{TEAM_N}}_game{{GAME_ID}}.md`.*
