# Team 2 — Game F verdict

> Copy this template to `team-2_gameF.md` and fill
> ALL `{{...}}` placeholders. Interaction with the game ONLY via
> `play.py --game F` (see BRIEFING.md).

## Phase 1 — Rule comprehension

- Mechanics in your own words (from `--rules` output + observed engine
  behaviour only; no speculation about design intent):
  {{rule_summary}}
- What actually ends the game, and how often each end cause occurred in your
  play (win condition / turn-limit tiebreak / double-pass draw):
  {{end_cause_notes}}
- Anything that surprised you about how the engine behaved vs. your reading
  of the rules: {{surprises}}

## Phase 2 — Strategic play (>= 3 full lines, both roles)

### Line 1 — you as P1
- Moves: `{{moves_csv_1}}`
- Plan and what happened: {{line_1_narrative}}
- Result (winner, end cause, plies): {{line_1_result}}

### Line 2 — you as P2
- Moves: `{{moves_csv_2}}`
- Plan and what happened: {{line_2_narrative}}
- Result: {{line_2_result}}

### Line 3 — adversarial / novelty-stress
- Moves: `{{moves_csv_3}}`
- What you tried to break / stress, and what happened: {{line_3_narrative}}
- Result: {{line_3_result}}

### Additional lines (optional)
{{additional_lines}}

## Phase 3 — Joint strategic analysis

- Core tactical loop (what a good move looks like, and why):
  {{tactical_loop}}
- Counterplay: when your opponent did X, what punished it? Did the game
  reward responding to the opponent at all? {{counterplay}}
- Topology/board effects on strategy: {{topology_effects}}
- Emergent concepts you'd name (or "none observed"): {{emergent_concepts}}
- Player agency: did YOUR choices decide the result, or did the engine
  dynamics / race structure decide it? {{agency_assessment}}

## Phase 4 — Novelty adversary

- Strongest case that this game is a re-skin of a known prior:
  {{reskin_case}}
- Honest novelty assessment after arguing that case: {{novelty_assessment}}

## Phase 5 — Verdict

- **Recognition disclosure (mandatory):** if you believe you can identify this game or recall a prior score, say so and continue.
  Disclosure (or "none"): {{recognition_disclosure}}
- P1-role experience sub-score (1-10): {{p1_subscore}}
- P2-role experience sub-score (1-10): {{p2_subscore}}
- Role-averaged sub-score: {{role_avg}}
- **Fairness perception (1-5, 3 = balanced; 1 = strongly P1-favored,
  5 = strongly P2-favored) + one sentence of evidence:** {{fairness_probe}}
- **Overall (1-10, anchored: R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69;
  anchor DOWN; 5.0 = the never-cleared G1 ceiling): {{overall}}**
- One-paragraph justification of the Overall, citing your Phase 2 lines:
  {{justification}}
