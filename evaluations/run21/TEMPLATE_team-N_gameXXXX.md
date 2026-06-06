# Run 21 Agent-Team Eval — team-{{TEAM_N}} — Game {{GAME_ID}}

**Team ID:** team-{{TEAM_N}}
**Game ID:** {{GAME_ID}} ({{SUBSTRATE_RANK}}, 20-seed mean GE {{GE20}}, σ {{SIGMA}}, calibrated komi_p2 {{KOMI}})
**Substrate:** {{SUBSTRATE}} (axis {{AXIS}}, {{ACTIVE}} active cells / {{TOTAL}} grid positions, max_degree {{MAX_DEG}}, pie_rule={{PIE}})
**Evaluator:** single-agent team running P1 / P2 / Novelty Adversary roles sequentially.
**Helper:** `eval_run21_helper.py --game {{GAME_ID}}` (see `briefing_{{SUBSTRATE}}_{{GAME_ID}}.md` for full rules and engine internals).

---

## Phase 1 — Rule Comprehension

**Board.** {{Substrate from first principles. Menger: 9×9×9, level-2 sponge holes (400 active); cell = z*81+y*9+x. Carpet: 9×9, level-2 Sierpinski holes (64 active); cell = y*9+x. Grid: full flat 9×9 = 81 cells, no holes.}}

**Turn structure.** Alternating, 1 piece/turn, P1 first. Max_turns = {{MAX_TURNS}}.

**Action space.** {{NUM_ACTIONS}} actions = {{TOTAL}} placement + 1 pass{{ + 1 pie if pie_rule}}. No move actions (D1 hybrid ban). Placement legal at any empty active cell.

**Placement & capture.** Capture rule = **{{CAPTURE_RULE}}** (threshold {{CAPTURE_THRESHOLD}}). {{Firing condition: outnumber-N → place adjacent so an enemy stone has ≥N friendly neighbours → captured (cleared). custodian-N → bracket an enemy run by N+ friendlies along an axis → run flips. surround → Go-style liberty-zero group capture (threshold field vestigial — R8-replay finding).}}

**Propagation.** {{PROP_TYPE}} (radius={{R}}, strength={{S}}, decay={{D}}). Placement adds ±strength·decay^dist to `board_values` within radius. Sign +1 P1 / −1 P2. Clamped [−100,100].

**Win condition.** {{Threshold-race: first player whose owned-cell influence sum exceeds {{THRESHOLD}} wins; target_dimension_p2=−1 → P2 mirrors P1's accumulator. OR connection: complete a connecting path (573562833174). Komi_p2={{KOMI}} adds a fractional bonus to P2's effective score at win-check.}} Equal → draw. Timeout → highest effective sum wins.

**Pie rule.** {{If True: after P1's first move, P2 may swap seats (take P1's move as their own). The pie/swap action is the last action id. If False: not available.}}

**Degeneracy check.**
- {{Inert fields, dead rule paths, soft violations from the briefing — esp. influence field that never enters win logic; vestigial thresholds.}}
- {{Board geometry quirks — fractal holes, neighbour-count irregularity, grid edge effects.}}

---

## Phase 2 — Strategic Play

All moves engine-verified through `eval_run21_helper.py`. Action IDs = cell indices for placement; pass = {{TOTAL}}{{; pie = last id if pie_rule}}.

### Game 1 — {{P1 line}}
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{move-by-move; flag captures, threshold totals at decision points, decisive moments.}}
Reflection: {{binding constraint? what did placement order force?}}

### Game 2 — {{P2 counter}}
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{...}}
Reflection: {{...}}

### Game 3 — {{Adversarial / seat-swap / novelty-stress}}
Sequence: `{{action_csv}}` ({{N}} plies).
Plot: {{...}}

### Strategy guides
**P1 (offence / threshold push or connection):** {{playbook}}
**P2 (defence + contest; pie/komi-aware):** {{playbook}}

---

## Phase 3 — Joint Strategic Analysis

**Distinct viable strategies?** {{yes/no + evidence}}
**Counter-play.** {{real / partial / absent; each strategy's counter}}
**Short-term vs long-term.** {{tactical depth vs strategic horizon; does the board size cap planning depth — the R8-replay "8×8 too small for ladders" concern?}}
**Emergent concepts observed.** {{influence wells, threshold flip, capture cascades, edge stranding, connection races, …}}
**Does {{SUBSTRATE}} matter?** {{would the same rules on a flat 9×9 (or 4³ for menger) preserve the dynamics?}}
**Does the propagation kernel matter?** {{r=1 vs r=2; decay value; does influence enter win logic or just decorate the observation tensor?}}
**Capture-rule contribution.** {{did captures actually fire? how often, what did they buy?}}
**First-mover advantage / seat balance.** {{from your games + trained-vs-trained ref. Did komi_p2={{KOMI}} / pie correct the bias, or does residual P1 advantage remain?}}

---

## Phase 4 — Novelty Adversary (mandatory)

**Adversary case.** This game is a re-skin of {{…}}. Argument:
(a) {{Threshold-race influence ≈ territorial/race scoring? Connection ≈ Hex/R8?}}
(b) {{Capture analog: outnumber→Tafl/Ataxx; surround→Go; custodian→Othello/Reversi.}}
(c) {{Does "{{CAPTURE_RULE}} + {{PROP_TYPE}} + win-condition" exist as a published game? Reference R8 Connection Go + R17–R20 corpus.}}
(d) {{Substrate: has fractal-dim play on this exact substrate been studied? What does the hole pattern add/subtract? For grid: flat-grid analog?}}
(e) {{Expert-transfer: could a Go+Othello+Hex player learn this in N min? Irreducible new piece?}}

**Closest known-game analogue:** {{name + 1-line.}}
**Comparison to R8 Connection Go (replay anchor 4.10).** {{Same family / different? Where does this sit relative to R8's depth/playability — especially for the connection game 573562833174?}}
**Comparison to R19/R20 best.** {{Richer or thinner than R19 menger 4.8 / surround 5.0 / R20 depth-record 4.80? What changed?}}

**Novelty score (post-adversary):** {{N}}/10. {{Above re-skin (2–3) because X; below genuinely-new (8–9) because Y. Anchor: R17 3.50, R8 4.10, R19 top 4.8/5.0.}}

---

## Phase 5 — Verdict

**Team ID:** team-{{TEAM_N}}
**Game ID:** {{GAME_ID}}
**Rules Summary:** {{1–2 sentence plain-English experience of the game.}}
**Substrate:** {{SUBSTRATE}}, axis {{AXIS}}, {{ACTIVE}}/{{TOTAL}} cells, max_degree {{MAX_DEG}}, pie_rule={{PIE}}, komi_p2={{KOMI}}.
**Turn Structure:** alternating
**Hybrid actions:** no (place-only, D1 active).
**Soft violations flagged:** {{none / list}}.

### Scores (1–10)
- **Strategic Depth: {{N}}** — {{meaningful decisions/game, branching at decision points, medium-term concepts. Does engine-measured GE/depth show up subjectively or is it a metric artifact?}}
- **Emergent Complexity: {{N}}** — {{patterns/tactics not explicitly written in the rules.}}
- **Balance: {{N}}** — {{seat balance from your games + training ref + komi/pie. Residual P1 advantage?}}
- **Novelty (post-adversary): {{N}}** — see Phase 4. {{one line.}}
- **Replayability: {{N}}** — {{once strategies are public, does it still reward play? opening variety?}}
- **Overall "Would an agent team play this again?": {{N}}** — {{one line. Anchors: R8 4.10, R17 3.5/4.14, R19 4.375/4.8/5.0, R20 3.73/4.80. > 5.0 clears the R19 ceiling (G1).}}

### CLOSEST KNOWN-GAME ANALOG
{{1–2 sentences: closest analog inside this corpus AND in the broader literature.}}

### KILLER FLAWS
- {{specific flaw 1}}
- {{specific flaw 2}}

### BEST QUALITY
{{the crown-jewel mechanic/pattern that lifts it above floor — or absence thereof.}}

### {{SUBSTRATE}} STRUCTURAL CONTRIBUTION
{{does the topology shape strategy, or could it flatten to a regular grid with minimal loss? Anchor against R19's menger > carpet > grid finding and the R8-replay board-size-limit concern.}}

### IMPROVEMENT IDEAS
**Single best change:** {{one specific, falsifiable change that would most improve the game.}}
Secondary:
- {{…}}

---

*Output saved to `/Users/jamesbrowne/aigame/evaluations/run21/team-{{TEAM_N}}_game{{GAME_ID}}.md`.*
