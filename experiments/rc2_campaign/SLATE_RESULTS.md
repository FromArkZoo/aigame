# RC2 campaign — slate results [BARH-V2-REANALYSIS chain]

2026-07-05. Blind evaluation per prereg §7 on the sealed pack
`evaluations/rc2_campaign_blind` (label_seed 582931, disclosed post-unblind).
3 independent blind teams (fresh Claude instances, tmux, cwd = pack dir),
21 verdicts + 2 separate cross-game notes filed; every template placeholder
filled; DONE markers observed for all teams before unblinding.

## Blind-integrity record

- **aigame project auto-memory PARKED** during evaluation at
  `~/.claude/projects/-Users-jamesbrowne-aigame/memory.blind-hold`
  (pre-launch probe showed a fresh pack-dir instance loads the aigame
  project memory via git-root resolution — the memory names prior champions
  and scores; post-park probe verified clean; restored after unblind).
- Task-tool subagents ruled out (inherit orchestrator-scope memory
  containing slate composition); teams launched as independent instances.
- Known open channel, dispositioned pre-launch: injected git commit
  subjects (no game/family/score named).
- Orchestrator stayed blind to the mapping until the grep gate passed.

## Pre-unblind grep (§7 gate) — 13 hits, all dispositioned BENIGN

- 12 × `[R8]` (teams 1–3, various files): scoring-anchor citations —
  the BRIEFING itself mandates anchoring against R8 4.10 / R19 4.375 /
  R20 3.73 / R21 3.69. Not recognition.
- 1 × `[Connection Go]` (team-2_cross_game_notes.md: "Gonnect-like
  connection Go on 8×8"): Phase-4-mandated reduction to known priors
  (Gonnect is a published game); the same team's recognition-disclosure
  line for that game explicitly denies specific recognition and score
  recall. Not recognition.
- All 21 recognition-disclosure lines: "none" or generic prior-art
  resemblance with explicit denial of specific-game recognition and
  prior-score recall.

## Unblinded scores (Overall 1–10, per team; mean)

| label | role | id | t1 | t2 | t3 | mean |
|---|---|---|---:|---:|---:|---:|
| D | **top** | 627eb70b77ed (territory,4,0) | 4.4 | 4.3 | 4.6 | **4.433** |
| B | validity anchor | d4015a646ae3 | 4.2 | 4.2 | 4.5 | **4.300** |
| G | carry-in (not binding) | S3 | 4.1 | 4.2 | 4.2 | 4.167 |
| A | **top** | 8f1f95ef38f6 (connection,0,1) | 4.1 | 4.1 | 4.0 | 4.067 |
| C | contrast | b461c5160c5e (connection,4,1) | 4.5 | 3.9 | 3.8 | 4.067 |
| F | **top** | 764ad3ae50ec (territory,4,1) | 3.95 | 3.0 | 4.6 | 3.850 |
| E | contrast | 1c55e13164ae (territory,4,4) | 3.9 | 3.6 | 3.5 | 3.667 |

## Bars (locked `bars.slate_bars` + `decide_verdict`)

- **S-GO-1** (≥1 top-3 ≥ 4.10): **TRUE** — D at 4.433 (every team ≥ 4.3).
- **S-GO-2**: separation +0.250 vs bar +0.4; min-contrast gap 0.0521 < 0.15
  → **SEPARATION_UNDERDETERMINED** (declared by construction, exactly as
  disclosed pre-ratification in PREREGISTRATION_BARH_V2.md §4).
- **Campaign validity: d4015 = 4.300, OUTSIDE [3.48, 4.18]** → slate verdict
  **CAMPAIGN_UNRESOLVED**.

**FINAL §9 TOKEN: `CAMPAIGN_UNRESOLVED` [BARH-V2-REANALYSIS chain]**

Registered consequence (§6): **one cheap 2-team replicate slate — never
permanent closure.** Launch is owner-gated.

## Reading (non-binding)

The anchor breached its band on the HIGH side: this evaluator cohort runs
~+0.3 hot relative to the cohorts that calibrated the band (d4015 prior
blind reads ~3.8–4.0). The RELATIVE ordering is coherent and favorable:
D (top elite) > d4015 (anchor) > contrast pool, S-GO-1 fired, and D beat
the anchor by +0.133 under the same drifted scale. Interpretation: the
campaign's top territory elite is genuinely R8-parity-or-better in blind
agent-team judgment; what failed is the ABSOLUTE validity instrument
(the band), not the search signal. The replicate slate should consider
(owner decision, and it is a prereg change requiring registration):
re-anchoring the band on the current evaluator generation, or reading
validity RELATIVE to in-slate d4015 rather than an absolute band.

## Role win split (reported, not binding; line-1 results only — teams'
line-2/3 result fields used free-form phrasing)

A 2-1-0 (P1-P2-draw) · B 1-2-0 · C 2-1-0 · D 2-1-0 · E 1-0-2 · F 2-1-0 ·
G 3-0-0. No game exceeds the 80/20 flag threshold at n≥5 decisive lines
(no label reached n=5 decisive in the captured subset).

## Hypothesis scorecard (vs pre-registered 12:40 record)

- S-GO-2 precondition fails → SEPARATION_UNDERDETERMINED: **CORRECT**.
- S-GO-1 is the genuine unknown: fired **TRUE**.
- d4015 in band: **WRONG** — out of band high; the GO-PARTIAL/NO-GO fork
  never bound; CAMPAIGN_UNRESOLVED was the path not priced.
