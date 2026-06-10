# Stage 3 blind eval — agent team briefing

You are one of 2 independent evaluator teams. You will evaluate up to THREE
games, labeled **D**, **V**, and **X**. You are NOT told what any game is,
whether any game differs from prior runs, which (if any) is a treatment or
comparator, or anything about the hypotheses being tested. Do not read:
`.blind_mapping.json`, the source of `play.py`, or anything under
`experiments/` (the entire directory). Also out of bounds for this
evaluation: any git commands (status, log, branch, diff) or repo metadata.
Interact with the games ONLY by running `play.py` as shown.

> **Your assigned labels will be specified in your team's task brief.**
> You will evaluate your assigned games; the orchestrator handles unblinding
> after ALL teams have filed ALL verdicts.

---

## How to run a game

    python evaluations/siege_ab/play.py --game D --rules
    python evaluations/siege_ab/play.py --game D
    python evaluations/siege_ab/play.py --game D --moves "<csv action ids>" [--control]

Substitute **V** or **X** as appropriate. `--control` renders the influence
control map alongside the board.

---

## Per-game protocol (5 phases, per TEMPLATE file)

Follow the 5-phase protocol in your TEMPLATE file for EACH assigned game.

**Phase 1 (Rule Comprehension):** run `--rules` first. Derive your entire
understanding of each game's mechanics from that output and from engine
behaviour you observe during play. Do not speculate about design intent.

**Phase 2 (Strategic Play):** play >= 3 full-game lines per game, in BOTH
roles:

- At least one line where you act as Player 1 (you drive P1 moves; script or
  narrate P2 as the opponent).
- At least one line where you act as Player 2 (you drive P2 moves; script or
  narrate P1 as the opponent).
- At least one adversarial / novelty-stress line.

All moves engine-verified through `play.py --game <label>`.
Action IDs: cell index = q + 22*r; pass=484; swap=485 (if pie rule is on).

**Phase 3 (Joint Strategic Analysis):** reasoning about tactics, counterplay,
topology, and emergent concepts — anchored to what you actually observed.

**Phase 4 (Novelty Adversary):** attempt to reduce the game to a known
prior — argue the strongest case that it is a re-skin. Then assess novelty
honestly.

**Phase 5 (Verdict):** per-role sub-scores (your Phase 2 experience as P1 /
as P2 where the game allows distinct experiences), the fairness-perception
probe, and the Overall 1-10. Role-average the sub-scores where applicable.

---

## Fairness-perception probe (mandatory, every game)

In Phase 5 of each template, answer:

> **Fairness perception (1–5 + one sentence):** Did either side feel
> structurally favored during your play? Rate 1 (strongly P1-favored) to 5
> (strongly P2-favored), with 3 = balanced. One sentence of evidence.

This applies to ALL games regardless of their rule structure.

---

## Scoring anchors (Phase 5, Overall 1-10)

R8 4.10, R19 4.375 (top 5.0), R20 3.73 (best 4.80), R21 3.69.
Anchor DOWN against drift, as in R21.

> 5.0 = clears the R19 ceiling (G1 threshold). This bar has never been
> cleared by a campaign mean.

---

## Cross-game comparison (after all assigned games are done)

After filing all per-game verdicts, add a final **Cross-game comparison**
section (in your last filed verdict or as a separate note):

- Rank your assigned games by Overall score.
- Which would you most want to play again, and by how many Overall points?
- The single mechanic or dynamic that most differentiates the top-ranked game
  from the others.

---

## File your verdicts

Write each verdict to:

    evaluations/siege_ab/team-{N}_game{D,V,X}.md

Use the TEMPLATE files (`TEMPLATE_team-N_gameD.md`, `TEMPLATE_team-N_gameV.md`,
`TEMPLATE_team-N_gameX.md`) as your rubric. Fill all `{{...}}` placeholders.

---

## ORCHESTRATOR-ONLY section

*Evaluators: stop reading here. Everything below is post-evaluation guidance
for the person unblinding results.*

### Unblinding procedure

Unblind ONLY after all 6 verdicts (2 teams × 3 games) are filed and saved
to `evaluations/siege_ab/`. Open `.blind_mapping.json` at that point.

### Role win split logging

For each game, log the win split across the two roles from the evaluator game
lines (how many P1-role games did P1 win, how many P2-role games did P2 win).
Flag any game where the win split exceeds 80/20 across the filed game lines —
this is a balance signal, not a verdict invalidator.

### Campaign validity

The A1-validity band for this campaign: blind mean for label X must fall in
[3.9, 4.4]. If X's mean across both teams is outside this range, trigger
CAMPAIGN_UNRESOLVED: do NOT permanently classify any arm; run one cheap blind
replicate before drawing conclusions.

### Decision thresholds (from preregistration)

Unblind D and V only after logging X. Then apply:

- **GO (treatment advances):** mean(D) − mean(X) >= +1.0 AND mean(D) > mean(V)
  with |mean(D) − mean(V)| >= 0.3.
- **PARTIAL:** |mean(D) − mean(V)| < 0.3, OR mean(D) > mean(V) but
  mean(D) − mean(X) < +1.0. Licensed action: exactly one re-parameterization.
- **D <= V:** treatment direction retired; assess V under z_flip_r2 grammar:
  mean(V) − mean(X) >= +1.0 reopens the FC family; mean(V) <= mean(X) closes
  it permanently (validity band guards the closure).
- **Both NO-GO:** registered escalation — see preregistration Stage 3.
