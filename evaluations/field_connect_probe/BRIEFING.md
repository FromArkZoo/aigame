# Probe — blind agent A/B briefing

You are one of 2 independent evaluator teams. You will evaluate TWO games,
labeled **Q** and **Z**. You are NOT told which (if either) differs from
prior runs, or what any hypothesis is. Do not read `.blind_mapping.json` or anything under
`experiments/field_connect_probe/` other than `eval_helper.py` usage below.

Per game: follow the 5-phase protocol in your TEMPLATE file (same rubric as
run21). Play >= 3 full lines per game (P1 push, P2 contest, adversary
stress) via:

    python experiments/field_connect_probe/eval_helper.py --game Q \
        --moves "<csv action ids>" [--control]

**Phase 1 (Rule Comprehension):** begin by running `--rules` to obtain a
mechanical, neutral rules summary derived from the game def:

    python experiments/field_connect_probe/eval_helper.py --game Q --rules
    python experiments/field_connect_probe/eval_helper.py --game Z --rules

Derive your understanding of each game's mechanics entirely from the
`--rules` output and engine behavior you observe during play. Do not
speculate about design intent.

Both games: hex-adjacency rhombus board W=22 (484 cells), place-only,
alternating, pie rule on.

Scoring anchors (Phase 5, Overall 1-10): R8 4.10, R19 4.375 (top 5.0),
R20 3.73 (best 4.80), R21 3.69. Anchor DOWN against drift, as in R21.

Additional final section (after Phase 5, per team): **Q-vs-Z comparison** —
which game would you rather play again, and by how many Overall points?

Write verdicts to evaluations/field_connect_probe/team-{N}_game{Q,Z}.md.
