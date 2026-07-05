# Blind eval — agent team briefing

You are one of 3 independent evaluator teams. You will evaluate SEVEN games,
labeled **A** through **G**, in your team's listed order (below). You are NOT
told what any game is, where it came from, whether any game differs from prior
runs, which (if any) are treatments or comparators, or anything about the
hypotheses being tested.

Do NOT read — the out-of-bounds list registered in the campaign
preregistration applies verbatim:

- EVERYTHING under `evaluations/` EXCEPT this pack directory
  (`evaluations/rc2_campaign_blind/`): no other evaluation pack, no prior verdicts,
  no summaries.
- Anything under `experiments/` (the entire directory).
- Anything under `docs/` (the entire directory).
- Any `analysis*.md` file.
- Memory files (MEMORY.md, memory/ directories, auto-memory topic files).
- Git/repo metadata: any git command (status, log, branch, diff, show) and
  anything under `.git/`.

Also out of bounds INSIDE this pack: `.blind_mapping.json` (sealed), the
game-definition JSONs under `games/`, and the source of `play.py` (usage
output only). Interact with the games ONLY by running `play.py` as shown.

> The orchestrator handles unblinding after ALL teams have filed ALL verdicts.

---

## How to run a game

    .venv/bin/python evaluations/rc2_campaign_blind/play.py --game A --rules
    .venv/bin/python evaluations/rc2_campaign_blind/play.py --game A --legal
    .venv/bin/python evaluations/rc2_campaign_blind/play.py --game A --moves "<csv action ids>" [--legal] [--values]

Substitute any label A–G.

- `--rules` prints the game's full mechanics (board, actions, captures,
  win condition, quirks). **Run it first for every game.**
- `--moves` applies a whole line of action ids from the initial position
  (the CLI is stateless — pass the full line each invocation). Each ply
  prints a board delta; the full board renders at the end.
- `--legal` prints the legal action ids for the player to move, decoded
  into coordinates (essential for games with MOVE actions).
- `--values` also renders the influence field, for games that have one.

**Action-id schemes differ per game** (different board sizes; one game has
MOVE actions; one has a PIE-SWAP). Always read the scheme from `--rules` and
decode ids with `--legal` — never assume ids carry over between games.

**Multi-dimensional boards** render as labeled 2D blocks: within each block,
columns = d0 (left→right) and rows = d1 (top→bottom); one block per
combination of the remaining coordinates (the block label gives them).
Holes render `#`, empty `.`, P1 `X`, P2 `O`.

The helper flags SUPER-KO rollbacks (an action that recreates a previous
position is converted to a pass) and marks board changes caused by
between-turn dynamics where a game has them. Trust the flags; they are
engine-verified.

---

## Your game order

Evaluate ALL 7 games, in your team's order (orders are not secret — only
identities are; do not infer anything from the order):

- **Team 1:** D, G, B, C, E, A, F
- **Team 2:** A, D, B, F, E, C, G
- **Team 3:** B, F, A, C, E, G, D

---

## Per-game protocol (5 phases, per your TEMPLATE files)

Follow the 5-phase protocol in your team's TEMPLATE files for EACH
game (`TEMPLATE_team-{N}_game{A..G}.md` — one per game).

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

In role-swapped lines, drive the opponent as a competent responder — choose
the best legal move you can reason about at each turn; do not play randomly
or throw the game. All moves engine-verified through
`play.py --game <label> --moves ...`.

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

R8 4.10, R19 4.375 (top 5.0), R20 3.73, R21 3.69.
Anchor DOWN against drift, as in R21.

> 5.0 = the never-cleared G1 ceiling. No campaign mean has ever cleared it.

---

## Cross-game comparison (after all 7 games are done)

After filing all per-game verdicts, add a final **Cross-game comparison**
section (in your last filed verdict or as a separate note). If filed as a
separate note, name it `team-{N}_<something>.md` (e.g.
`team-2_cross_game_notes.md`) so it falls inside the pre-unblind grep's
`team-*` scan glob:

- Rank all 7 games by Overall score.
- Which would you most want to play again, and by how many Overall points?
- The single mechanic or dynamic that most differentiates the top-ranked game
  from the others.

---

## File your verdicts

Write each verdict to:

    evaluations/rc2_campaign_blind/team-{N}_game{A..G}.md

(e.g. `team-2_gameC.md`). Use your team's `TEMPLATE_team-{N}_game{A..G}.md`
files as your rubric — copy each one and fill ALL `{{...}}` placeholders.

---

## ⚠ ORCHESTRATOR-ONLY — evaluators STOP READING here

**⚠ EVALUATORS: STOP. Do not read past this divider.** Everything below is
post-evaluation guidance for the person unblinding results.

### Unblinding procedure

Unblind ONLY after all 21 verdicts (3 teams × 7 games) are filed and saved
to `evaluations/rc2_campaign_blind/`. BEFORE opening the mapping, run the pre-unblind
identifier grep over the filed verdicts:

    .venv/bin/python experiments/rc2_campaign/grep_verdicts.py evaluations/rc2_campaign_blind

Run it and record every hit verbatim with your disposition (benign quote /
board vocabulary / genuine recognition → treat per the recognition-
disclosure protocol, prereg §8) BEFORE opening the mapping. Exit 1 means
hits exist to review, not that unblinding is forbidden. Only then open
`.blind_mapping.json`. Labels and per-team orders were assigned by a
runner-chosen sealed seed
(recorded inside the mapping as `label_seed` for post-campaign audit) — no
label has a fixed meaning before the mapping is opened. Apply the validity
band, the bars, and the locked decision grammar exactly as written in
`experiments/rc2_campaign/PREREGISTRATION.md` (§6–§9).

### Role win split logging

For each game, log the win split across the two roles from the evaluator game
lines (how many P1-role games did P1 win, how many P2-role games did P2 win).
Flag any game where the win split exceeds 80/20 across the filed game lines —
this is a balance signal, not a verdict invalidator. These feed the
fairness-flag reporting (pre-registered as reported-not-binding).
