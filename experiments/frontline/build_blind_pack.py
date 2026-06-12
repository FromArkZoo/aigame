#!/usr/bin/env python
"""FRONTLINE Stage 3 — blind-pack builder (prereg 3a378dd, Stage 3).

Builds the blind evaluation pack `evaluations/frontline_ab/` from the
`evaluations/stage3_ab/` machinery (the SIEGE campaign's pack — the locked
verdict instrument), adapted ONLY by label substitution:

    stage3_ab (SIEGE)              frontline_ab (this campaign)
    labels D / V / X          ->   labels G / J / P (random, sealed)
    pack path stage3_ab       ->   pack path frontline_ab

Everything evaluators see (the 5-phase protocol, the Overall 1-10 scale and
its anchors, the fairness-perception probe, the role-swap requirements) is
carried over verbatim. Every adaptation is an asserted exact-string
replacement: drift in the source template fails THIS script loudly rather
than silently shipping a modified instrument.

Structural notes (orchestrator-side; the evaluator instrument is untouched):

* stage3_ab's play.py was a runpy shim onto experiments/siege/eval_helper.py,
  which resolved labels through the sealed mapping at runtime. Here the pack
  is SELF-CONTAINED: the three game JSONs are copied INTO the pack as
  g.json / j.json / p.json with `game_id` rewritten to the bare label
  (mirroring stage3_ab's anonymization effect: no arm name is reachable from
  anything an evaluator touches), and the generated play.py loads by label
  without ever reading `.blind_mapping.json`. The pack copies are anonymized
  DERIVATIVES — they are never written back to experiments/frontline/games/,
  so the canonical game files (and their canonical hashes) are untouched.
  Self-contained because the contested_majority family needs its own
  rules/status rendering — siege's eval_helper has no branch for it.
* The orchestrator-only section below the BRIEFING's STOP divider (validity
  band, decision grammar) is updated to this campaign's preregistered
  values: A1 validity [3.7, 4.4], S sanity [3.7, 4.5], decision grammar per
  experiments/frontline/PREREGISTRATION.md Stage 3 (verbatim authority).
  Because labels are RANDOMLY assigned here (stage3_ab used fixed slots),
  that section refers to ARMS identified after opening the sealed mapping,
  never to labels.
* One blinding-protective clause is added to the evaluator do-not-read list:
  the pack's own game JSONs (they did not exist in stage3_ab's pack layout).

Games (real build — run AFTER Stage 2 SCREEN_GO, at campaign time):
    experiments/frontline/games/calibrated/f_frontline.json   (Stage-1 winner)
    experiments/frontline/games/s_flip_r2.json
    experiments/frontline/games/a1_field_connect.json
The calibrated treatment exists only after Stage 1; a missing file is a loud
error (exit 1), by design — the pack is built at campaign time, not build time.

--seed is REQUIRED and has NO default, deliberately: the label<->game
assignment is a pure function of the seed, so a default baked into this file
would let anyone who can read the script reconstruct the sealed mapping.
The runner picks a fresh seed at campaign time and keeps it out of
evaluator-visible channels until unblinding (the seed is recorded inside the
sealed mapping file itself for post-campaign audit).

--dry-run builds into evaluations/frontline_ab_dryrun/ using three
already-on-disk game files (the Stage-0b pinned grid cell stands in for the
calibrated treatment) so pack plumbing can be verified before Stage 1 has
run. Inspect, then delete the directory manually.

Usage:
    .venv/bin/python experiments/frontline/build_blind_pack.py --seed <runner-chosen>
    .venv/bin/python experiments/frontline/build_blind_pack.py --seed <any> --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "evaluations" / "stage3_ab"
GAMES = ROOT / "experiments" / "frontline" / "games"

LABELS = ("G", "J", "P")          # fresh labels, prereg Stage 3
OLD_LABELS = ("D", "V", "X")      # stage3_ab labels they substitute
LABEL_MAP = dict(zip(OLD_LABELS, LABELS))

REAL_ARMS = {
    "f_frontline": GAMES / "calibrated" / "f_frontline.json",
    "s_flip_r2": GAMES / "s_flip_r2.json",
    "a1_field_connect": GAMES / "a1_field_connect.json",
}
# Dry-run stand-ins: the Stage-0b pinned cell plays the treatment slot.
DRY_ARMS = {
    "f_frontline_E1p00_M8": GAMES / "f_frontline_E1p00_M8.json",
    "s_flip_r2": GAMES / "s_flip_r2.json",
    "a1_field_connect": GAMES / "a1_field_connect.json",
}

SEALED_COMMENT = (
    "SEALED — DO NOT OPEN until all 6 verdicts (2 teams x 3 games) are "
    "filed in evaluations/frontline_ab/. Opening earlier unblinds and "
    "invalidates the campaign (prereg 3a378dd, Stage 3: sealed mapping "
    "opened only after all verdicts)."
)


def replace_exact(text: str, old: str, new: str, expect: int = 1,
                  where: str = "BRIEFING") -> str:
    """Replace with an occurrence-count assertion — template drift fails loudly."""
    n = text.count(old)
    if n != expect:
        sys.exit(
            f"ERROR: {where} drift — expected {expect} occurrence(s) of "
            f"{old!r}, found {n}. Re-audit substitutions against "
            f"evaluations/stage3_ab/ before building the pack."
        )
    return text.replace(old, new)


# --------------------------------------------------------------------------
# BRIEFING — stage3_ab template, label substitution only (prereg lock)
# --------------------------------------------------------------------------

NEW_ORCHESTRATOR_BODY = """### Unblinding procedure

Team task briefs must assign OPPOSITE evaluation orders (prereg Stage 3):
team 1 evaluates G -> J -> P; team 2 evaluates P -> J -> G. No cross-reads
between teams at any point.

Unblind ONLY after all 6 verdicts (2 teams x 3 games) are filed and saved
to `evaluations/frontline_ab/`. Log all three label means FIRST, then open
`.blind_mapping.json`. Labels were assigned to arms by a runner-chosen
random seed — no label has a fixed meaning before the mapping is opened.

### Role win split logging

For each game, log the win split across the two roles from the evaluator game
lines (how many P1-role games did P1 win, how many P2-role games did P2 win).
Flag any game where the win split exceeds 80/20 across the filed game lines —
this is a balance signal, not a verdict invalidator.

### Campaign validity

After opening the mapping, identify the anchor arm (a1_field_connect). Its
blind mean across both teams must fall in [3.7, 4.4] (prereg: widened from
[3.9, 4.4] on the two on-disk observations 3.90 and 4.15). Outside the band ->
CAMPAIGN_UNRESOLVED: do NOT permanently classify any arm; run one cheap blind
replicate, whose numbers then adjudicate alone; a second consecutive validity
failure -> CAMPAIGN_INVALID (F undecided, family neither GO'd nor retired).

S sanity flag: the comparator arm (s_flip_r2) outside [3.7, 4.5] -> verdicts
provisional -> one replicate.

### Decision thresholds (from preregistration)

Apply `experiments/frontline/PREREGISTRATION.md` Stage 3 VERBATIM (locked
3a378dd) — the prereg text is the authority; this is a transcription:

- **GO:** mean(F) - mean(A1) >= +1.0 AND mean(F) > mean(S) with
  mean(F) - mean(S) >= +0.3.
- **PARTIAL:** (F > S AND F - A1 < +1.0) OR |F - S| < 0.3 -> exactly one
  licensed re-parameterization: the recorded Stage-1 runner-up cell
  (re-assert its Stage-1 gates at its registered komi — no new grid — then
  screen, then blind once; that second blind is adjudicated GO-else-NO-GO,
  no further PARTIAL, no further knobs). If no second cell passed Stage 1,
  the knob is VOID and PARTIAL -> NO-GO.
- **NO-GO** (F <= S outside the tie band): contested_majority RETIRED; the
  RC2 selection-layer workstream becomes the sole registered track.
"""


def action_id_line(games: dict[str, dict]) -> tuple[str, bool]:
    """The BRIEFING's single action-ID line, derived from the packed games.

    Returns (line, uniform). Non-uniform geometry (the W=21 mirror
    contingency world, where F switches and S/A1 stay at W=22) gets a
    per-game listing and the caller prints a loud warning.
    """
    geoms = {lab: (g["axis_size"], g["axis_size"] ** 2, g["axis_size"] ** 2 + 1)
             for lab, g in games.items()}
    if len(set(geoms.values())) == 1:
        s, pas, swp = next(iter(geoms.values()))
        return (f"Action IDs: cell index = q + {s}*r; pass={pas}; "
                f"swap={swp} (if pie rule is on)."), True
    parts = "; ".join(
        f"game {lab}: cell = q + {s}*r, pass={pas}, swap={swp}"
        for lab, (s, pas, swp) in sorted(geoms.items()))
    return f"Action IDs differ per game — {parts} (swap only if pie rule is on).", False


def build_briefing(games: dict[str, dict]) -> str:
    text = (SRC / "BRIEFING.md").read_text(encoding="utf-8")

    # Pack path (the only non-label difference allowed in the instrument).
    if "stage3_ab" not in text:
        sys.exit("ERROR: BRIEFING drift — no 'stage3_ab' path found in source.")
    text = text.replace("stage3_ab", "frontline_ab")

    # Label substitutions — each one exact and counted.
    text = replace_exact(text, "labeled **D**, **V**, and **X**",
                         "labeled **G**, **J**, and **P**")
    text = replace_exact(text, "--game D --rules", "--game G --rules")
    text = replace_exact(text, "play.py --game D\n", "play.py --game G\n")
    text = replace_exact(text, "--game D --moves", "--game G --moves")
    text = replace_exact(text, "Substitute **V** or **X** as appropriate.",
                         "Substitute **J** or **P** as appropriate.")
    text = replace_exact(text, "game{D,V,X}", "game{G,J,P}")
    for old, new in LABEL_MAP.items():
        text = replace_exact(text, f"TEMPLATE_team-N_game{old}.md",
                             f"TEMPLATE_team-N_game{new}.md")

    # Blinding-protective addition: the pack now carries its own game JSONs.
    text = replace_exact(
        text,
        "`.blind_mapping.json`, the source of `play.py`, or anything under",
        "`.blind_mapping.json`, the game-definition JSONs in this pack\n"
        "(`g.json`/`j.json`/`p.json`), the source of `play.py`, or anything under",
    )

    # Geometry line, derived from the packed games (identity at W=22).
    line, uniform = action_id_line(games)
    text = replace_exact(
        text,
        "Action IDs: cell index = q + 22*r; pass=484; swap=485 "
        "(if pie rule is on).",
        line,
    )
    if not uniform:
        print("*** WARNING: packed games have non-uniform board geometry "
              "(mirror-contingency W=21 world?) — BRIEFING action-ID line "
              "rewritten per game; re-check the TEMPLATE substrate lines.")

    # Orchestrator-only section: replace from the unblinding marker to EOF
    # with this campaign's preregistered values (below the STOP divider —
    # not part of the evaluator instrument). This also drops the SIEGE
    # S-only-mode paragraph, which has no FRONTLINE analog (F failing any
    # earlier stage means NO blind at all).
    marker = "### Unblinding procedure"
    if text.count(marker) != 1:
        sys.exit("ERROR: BRIEFING drift — unblinding marker not found exactly once.")
    text = text[: text.index(marker)] + NEW_ORCHESTRATOR_BODY

    # Lock guards: the verdict instrument must have survived intact.
    for must in (
        "## Fairness-perception probe (mandatory, every game)",
        "R8 4.10, R19 4.375 (top 5.0), R20 3.73 (best 4.80), R21 3.69.",
        "Overall 1-10",
    ):
        if must not in text:
            sys.exit(f"ERROR: instrument-lock guard failed — missing {must!r}.")
    return text


# --------------------------------------------------------------------------
# Verdict TEMPLATEs — relabeled stage3_ab templates
# --------------------------------------------------------------------------

def build_template(src_text: str, old: str, new: str, game: dict) -> str:
    """Relabel one stage3_ab TEMPLATE via explicit, count-asserted label
    contexts ONLY. A bare token substitution is deliberately avoided: the
    templates contain standalone letters that are NOT labels (the `{{D}}`
    decay placeholder, the prose placeholder "because X") and a token regex
    corrupts them — caught by diff during the build of this script."""
    text = src_text
    if "stage3_ab" not in text:
        sys.exit("ERROR: TEMPLATE drift — no 'stage3_ab' path found in source.")
    text = text.replace("stage3_ab", "frontline_ab")
    where = f"TEMPLATE_team-N_game{old}.md"
    # Own-label contexts (counts verified against the on-disk siege pack).
    for ctx, n in (
        (f"Game {old}", 1),            # title line
        (f"Game Label:** {old}", 2),   # header + Phase-5 verdict block
        (f"--game {old}", 3),          # helper line, Phase-1 cmd, Phase-2 note
        (f"game{old}", 1),             # output-path footer
    ):
        text = replace_exact(text, ctx, ctx.replace(old, new), n, where)
    # Cross-game comparison line lists all three labels in every template.
    text = replace_exact(text, "{{D=N, V=N, X=N", "{{G=N, J=N, P=N", 1, where)

    # Per-template geometry (identity at W=22; exercised only if the mirror
    # contingency moved this game to W=21).
    s = game["axis_size"]
    if s != 22:
        c = s * s
        for old, new in (
            ("axis 22", f"axis {s}"),
            ("484 total cells / 484 active", f"{c} total cells / {c} active"),
            ("q + 22*r", f"q + {s}*r"),
            ("pass=484", f"pass={c}"),
            ("swap=485", f"swap={c + 1}"),
            ("484 placement", f"{c} placement"),
        ):
            if old in text:
                text = text.replace(old, new)
        print(f"*** WARNING: TEMPLATE for game {label} rewritten for "
              f"axis_size={s} (non-registered geometry — mirror contingency?).")
    return text


# --------------------------------------------------------------------------
# play.py — self-contained evaluator entry point written into the pack.
# Adapted from experiments/siege/eval_helper.py (stage3_ab's runtime), with
# a contested_majority branch added to render/status/rules_summary and game
# loading switched to the pack's own anonymized label files (the helper
# never reads .blind_mapping.json).
# --------------------------------------------------------------------------

PLAY_PY = r'''"""Stage 3 blind eval — evaluator entry point. Usage:
    python evaluations/frontline_ab/play.py --game G --rules
    python evaluations/frontline_ab/play.py --game J --rules
    python evaluations/frontline_ab/play.py --game P --rules
    python evaluations/frontline_ab/play.py --game G
    python evaluations/frontline_ab/play.py --game G \
        --moves "245,108,246" --control

Loads game definitions via blind labels (G/J/P) from this pack. Renders the
stone board and (with --control) a control/engagement map; reports game
progress and legal actions. Run --rules first to obtain a mechanical rules
summary for each game.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from game_engine.factory import create_engine  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from game_engine.engine_v2 import (  # noqa: E402
    CM_LEAD_TOL,
    CM_PERSISTENCE_CHECKS,
)

from experiments.field_connect_probe.metrics import (  # noqa: E402
    controlled_sets,
    largest_component,
)

HERE = Path(__file__).resolve().parent


def load_game(label: str) -> GameDefV2:
    path = HERE / (label.lower() + ".json")
    if not path.exists():
        raise FileNotFoundError(
            f"Game file not found for label {label.upper()!r} — "
            f"ask the orchestrator."
        )
    return GameDefV2.from_dict(json.load(open(path, encoding="utf-8")))


def render(engine, game, show_control: bool) -> str:
    s = game.axis_size
    topo = engine.topo
    wc = game.win_condition
    out = []
    for r in range(s):
        row = [" " * r]
        for q in range(s):
            c = topo.coords_to_cell((q, r))
            o = int(engine.board_owners[c])
            row.append("X" if o == 1 else "O" if o == 2 else "·")
        out.append(" ".join(row))
    if show_control:
        out.append("")
        if wc.condition_type == "contested_majority":
            i1, i2 = engine._per_player_fields()
            e = float(wc.engage_threshold)
            out.append("engagement map (+ = engaged, P1-led; - = engaged, "
                       "P2-led; = = engaged, led by neither; · = not engaged):")
            for r in range(s):
                row = [" " * r]
                for q in range(s):
                    c = topo.coords_to_cell((q, r))
                    a, b = float(i1[c]), float(i2[c])
                    if min(a, b) >= e:
                        d = a - b
                        row.append("+" if d > CM_LEAD_TOL
                                   else "-" if d < -CM_LEAD_TOL else "=")
                    else:
                        row.append("·")
                out.append(" ".join(row))
        else:
            margin = getattr(wc, "control_margin", 0.0)
            out.append("control map (+ = P1-controlled, - = P2, · = contested):")
            for r in range(s):
                row = [" " * r]
                for q in range(s):
                    v = float(engine.board_values[topo.coords_to_cell((q, r))])
                    row.append("+" if v > margin else "-" if v < -margin else "·")
                out.append(" ".join(row))
    return "\n".join(out)


def status(engine, game) -> str:
    wc = game.win_condition
    turns_remaining = wc.max_turns - engine.step_count
    lines = [
        f"step={engine.step_count} player_to_move=P{engine.current_player} "
        f"done={engine.done} winner={engine._winner} "
        f"turns_remaining={turns_remaining}"
    ]
    s = game.axis_size

    if wc.condition_type == "contested_majority":
        s1, s2, engaged = engine.contested_scores()
        komi = wc.komi_cells
        lead = s1 - (s2 + komi)
        score_line = f"scores (engaged cells led): P1={s1} P2={s2}"
        if komi:
            score_line += f" (P2 effective {s2 + komi} with komi_cells={komi})"
        score_line += (f" | engaged cells={engaged} | "
                       f"komi-adjusted lead (P1 - P2) = {lead:+d}")
        lines.append(score_line)
        streak = int(getattr(engine, "_cm_streak", 0))
        lines.append(
            f"persistent-lead counter: {streak:+d}/{CM_PERSISTENCE_CHECKS} "
            f"(early end: same player holds a komi-adjusted lead >= "
            f"{wc.end_margin} at {CM_PERSISTENCE_CHECKS} consecutive checks "
            f"ending after a P2 ply; active from turn "
            f"{wc.min_turns_score_end})"
        )
        if engine.done:
            cause = ("score-margin early end"
                     if getattr(engine, "_ended_by_score_margin", False)
                     else "double pass"
                     if getattr(engine, "_ended_by_double_pass", False)
                     else "turn limit"
                     if getattr(engine, "_ended_by_max_turns", False)
                     else "win condition")
            lines.append(f"end cause: {cause}")
    else:
        margin = getattr(wc, "control_margin", 0.0)
        p1_cells, p2_cells = controlled_sets(engine, margin)
        lc_p1 = largest_component(engine.topo, p1_cells)
        lc_p2 = largest_component(engine.topo, p2_cells)
        quota = getattr(wc, "capture_quota", 0)
        p1_axis = "r" if wc.target_dimension == 1 else "q"
        if quota > 0:
            legend = (
                f"(P1 connects {p1_axis}=0<->{p1_axis}={s - 1}; P2 wins by "
                f"reaching the conversion total or at the turn limit; "
                f"components are progress info only)"
            )
        else:
            p2_axis = "q" if wc.target_dimension_p2 == 0 else "r"
            legend = (
                f"(P1 connects {p1_axis}=0<->{p1_axis}={s - 1}, "
                f"P2 connects {p2_axis}=0<->{p2_axis}={s - 1}; components are "
                f"progress info only — timeout is decided by total "
                f"controlled-cell count)"
            )
        lines.append(
            f"controlled cells: P1={len(p1_cells)} P2={len(p2_cells)} "
            f"largest components: P1={lc_p1} P2={lc_p2} {legend}"
        )
        if quota > 0:
            ticks = getattr(engine, "_quota_ticks", 0)
            lines.append(f"conversion count: {ticks}/{quota}")

    legal = engine.get_legal_actions()
    action_hint = (
        f"legal actions: {len(legal)} "
        f"(cell index = q + {s}*r; pass={s ** 2}"
    )
    if game.pie_rule:
        action_hint += f", swap={s ** 2 + 1}"
    action_hint += ")"
    lines.append(action_hint)
    return "\n".join(lines)


def rules_summary(game: GameDefV2) -> str:
    """Print a mechanical, neutral rules summary derived from the game
    definition — the same neutral register for all games, revealing no
    experimental identities, arm roles, or variant names."""
    topo = game.get_topology()
    wc = game.win_condition
    cap = game.capture_rule
    prop = game.propagation_rule

    lines = []
    lines.append("=== GAME RULES SUMMARY ===")
    lines.append("")

    # --- Board ---
    s = game.axis_size
    total = game.total_cells
    active = topo.num_active_cells
    max_deg = topo.max_degree
    lines.append(f"Board: {s}×{s} rhombus ({total} cells total, {active} active).")
    lines.append(f"Adjacency: triangular lattice (hex), max degree {max_deg}.")
    lines.append(f"  Cell indexing: cell = q + {s}*r  where q is column (0..{s - 1}),")
    lines.append(f"  r is row (0..{s - 1}). Rows are sheared — each row r shifts right by r.")
    lines.append("")

    # --- Placement ---
    lines.append("Placement: one stone per turn, any empty cell.")
    lines.append("")

    # --- Capture ---
    ctype = cap.capture_type
    cthresh = cap.threshold
    if ctype == "field_flip":
        lines.append(
            "Capture (influence-flip): after each placement, all enemy stones "
            "that stand on cells where the influence field is dominated by the "
            "active player are immediately converted to that player's colour. "
            "Conversions are checked after the influence field is updated and "
            "can cascade: each conversion shifts the field further, potentially "
            "triggering additional conversions in the same turn. "
            "The influence field uses the same radius/strength/decay as the "
            "propagation rule."
        )
    elif ctype == "surround":
        lines.append(
            f"Capture (surround): after placing, any enemy group with zero "
            f"empty-cell liberties is immediately removed (cleared to empty). "
            f"Groups = connected same-owner stones. Threshold field={cthresh} "
            f"(vestigial for surround)."
        )
    elif ctype == "none":
        lines.append("Capture: none.")
    else:
        lines.append(f"Capture: {ctype}, threshold={cthresh}.")
    lines.append("")

    # --- Influence / propagation ---
    ptype = prop.prop_type
    if ptype == "influence":
        r = prop.radius
        s_val = prop.strength
        d_val = prop.decay
        lines.append(
            f"Influence field: each placed stone adds ±strength·decay^dist to "
            f"board_values within radius {r}. Placing a P1 stone: +{s_val}·{d_val}^dist; "
            f"P2: -{s_val}·{d_val}^dist. Values clamped [-100, 100]. "
            f"Radius={r}, strength={s_val}, decay={d_val}."
        )
    else:
        lines.append(f"Influence/propagation: {ptype}.")
    lines.append("")

    # --- Win condition ---
    cond = wc.condition_type
    max_turns = wc.max_turns
    margin = getattr(wc, "control_margin", 0.0)

    if cond == "contested_majority":
        e = wc.engage_threshold
        m = wc.end_margin
        mt = wc.min_turns_score_end
        komi = wc.komi_cells
        lines.append("Win condition (contested-majority score race):")
        lines.append(
            f"  Influence is tracked PER PLAYER: a player's influence on a "
            f"cell is the sum of strength·decay^dist over that player's own "
            f"stones within the radius."
        )
        lines.append(
            f"  A cell is ENGAGED when BOTH players' influence on it is "
            f">= {e} (empty and occupied cells both count)."
        )
        lines.append(
            f"  A player's SCORE is the number of engaged cells where their "
            f"influence strictly leads the opponent's; engaged cells led by "
            f"neither score no one."
        )
        lines.append(
            f"  Early end (checked from turn {mt}): if the same player holds "
            f"a komi-adjusted score lead >= {m} at {CM_PERSISTENCE_CHECKS} "
            f"consecutive checks ending after a Player-2 ply, that player "
            f"wins immediately."
        )
        lines.append(
            f"  Double pass: before turn {mt} the game is a draw; at or "
            f"after turn {mt} the game ends and is resolved by score."
        )
        lines.append(
            f"  Turn limit ({max_turns} turns): the game ends and is "
            f"resolved by score."
        )
        lines.append(
            f"  Score resolution: komi-adjusted score decides; on an EXACT "
            f"tie, more stones on the board decides; a player who placed "
            f"zero stones the entire game can never be declared winner; "
            f"otherwise a draw."
        )
        lines.append(
            f"  Komi: Player 2's score gains {komi} cells at every scoring "
            f"check (komi_cells={komi})."
        )
    elif cond == "field_connection":
        p1_dim = wc.target_dimension
        p2_dim = wc.target_dimension_p2
        p1_axis = "r" if p1_dim == 1 else "q"
        p2_axis = "q" if p2_dim == 0 else "r"
        lines.append(
            f"Win condition (influence-field connection): a player wins when "
            f"their controlled cells form a connected path across the board. "
            f"A cell is controlled by P1 if board_values > +{margin}; "
            f"by P2 if board_values < -{margin}; otherwise contested."
        )
        lines.append(
            f"P1 must connect {p1_axis}=0 to {p1_axis}={s - 1} "
            f"(top-to-bottom in the sheared display)."
        )
        lines.append(
            f"P2 must connect {p2_axis}=0 to {p2_axis}={s - 1} "
            f"(left-to-right in the sheared display)."
        )
        lines.append(
            f"Komi_p2={game.komi_p2} applies at timeout tiebreak only."
        )
        lines.append(
            f"Timeout ({max_turns} turns): player with the higher TOTAL "
            f"controlled-cell count wins (NOT largest component); P2's count "
            f"gains komi_p2 * {topo.num_active_cells} virtual cells; equal is a draw."
        )
    else:
        lines.append(f"Win condition: {cond}, threshold={wc.threshold}.")
    lines.append("")

    # --- Pie rule ---
    if game.pie_rule:
        swap_idx = game.swap_action_idx
        lines.append(
            f"Pie rule: ON. After P1's first stone, P2 may swap seats (inherit P1's "
            f"stone as their own and become the first mover). Swap action index = {swap_idx}."
        )
    else:
        lines.append("Pie rule: OFF.")
    lines.append("")

    # --- Komi ---
    if cond == "contested_majority":
        lines.append(
            f"Komi_cells: {wc.komi_cells} (cells added to Player 2's score "
            f"at every scoring check)."
        )
    else:
        lines.append(
            f"Komi_p2: {game.komi_p2} (fractional advantage added to P2's "
            f"effective score)."
        )
    lines.append("")

    # --- Action space ---
    pass_idx = game.total_cells
    lines.append(f"Action space: {game.num_actions} total actions.")
    lines.append(
        f"  Placement: actions 0..{game.total_cells - 1} (cell index = q + {game.axis_size}*r)."
    )
    lines.append(f"  Pass: action {pass_idx}.")
    if game.pie_rule:
        lines.append(f"  Swap (pie): action {game.swap_action_idx}.")
    lines.append("")

    lines.append("=== END RULES ===")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(prog="play.py", description=__doc__)
    p.add_argument("--game", required=True,
                   choices=["G", "J", "P", "g", "j", "p"])
    p.add_argument("--moves", default="",
                   help="comma-separated action ids to replay")
    p.add_argument("--control", action="store_true",
                   help="also render the control/engagement map")
    p.add_argument("--rules", action="store_true",
                   help="print a neutral mechanical rules summary then exit")
    args = p.parse_args()

    label = args.game.upper()

    try:
        game = load_game(label)
    except FileNotFoundError as exc:
        print(str(exc))
        sys.exit(1)

    if args.rules:
        print(rules_summary(game))
        return

    engine = create_engine(game)
    engine.reset()
    tokens = [t.strip() for t in args.moves.split(",") if t.strip()]
    for n, tok in enumerate(tokens, start=1):
        if engine.done:
            print("game already over — remaining moves ignored")
            break
        try:
            a = int(tok)
        except ValueError:
            print(f"error: ValueError: invalid move token {tok!r} "
                  f"(must be an integer action id)")
            sys.exit(1)
        legal = engine.get_legal_actions()
        if a not in legal:
            print(f"error: illegal action {a} at step {n} — "
                  f"legal count {len(legal)}")
            sys.exit(1)
        engine.step(a)
    print(render(engine, game, args.control))
    print()
    print(status(engine, game))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {type(exc).__name__}: invalid input or internal error")
        sys.exit(1)
'''


# --------------------------------------------------------------------------
# Pack assembly
# --------------------------------------------------------------------------

def build(out_dir: Path, arms: dict[str, Path], seed: int, dry: bool) -> None:
    if out_dir.exists():
        sys.exit(
            f"ERROR: {out_dir} already exists — refusing to overwrite (it may "
            f"contain a sealed mapping and filed verdicts). Remove it manually "
            f"if you really mean to rebuild."
        )
    for name, path in arms.items():
        if not path.exists():
            if "calibrated" in path.parts:
                sys.exit(
                    f"ERROR: {path} is missing.\n"
                    f"Stage 1 has not produced the calibrated treatment yet — "
                    f"the blind pack is built AFTER Stage 2 SCREEN_GO, at "
                    f"campaign time (prereg stage order).\n"
                    f"Use --dry-run to verify pack plumbing before Stage 1."
                )
            sys.exit(f"ERROR: {path} is missing.")

    # Sealed random label<->game assignment (pure function of --seed).
    rng = random.Random(seed)
    arm_names = sorted(arms)  # deterministic base order before the shuffle
    mapping = dict(zip(LABELS, rng.sample(arm_names, len(arm_names))))

    out_dir.mkdir(parents=True)

    # Game JSONs -> anonymized pack derivatives g/j/p.json. game_id is
    # rewritten to the bare label; nothing is ever written back to the
    # canonical files under experiments/frontline/games/.
    games: dict[str, dict] = {}
    for label in LABELS:
        data = json.load(open(arms[mapping[label]], encoding="utf-8"))
        data["game_id"] = label
        games[label] = data
        (out_dir / f"{label.lower()}.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8")

    # Sealed mapping — loud do-not-open comment field first.
    sealed = {"__SEALED__": SEALED_COMMENT}
    sealed.update(mapping)
    sealed["seed"] = seed
    (out_dir / ".blind_mapping.json").write_text(
        json.dumps(sealed, indent=2) + "\n", encoding="utf-8")

    # BRIEFING (instrument lock: label substitution only) + play.py + TEMPLATEs.
    (out_dir / "BRIEFING.md").write_text(build_briefing(games), encoding="utf-8")
    (out_dir / "play.py").write_text(PLAY_PY, encoding="utf-8")
    for old, new in LABEL_MAP.items():
        src_text = (SRC / f"TEMPLATE_team-N_game{old}.md").read_text(encoding="utf-8")
        (out_dir / f"TEMPLATE_team-N_game{new}.md").write_text(
            build_template(src_text, old, new, games[new]), encoding="utf-8")

    # Report structure WITHOUT revealing the assignment.
    print(f"Blind pack built: {out_dir}")
    if dry:
        print("*** DRY RUN — stand-in games (Stage-0b pinned cell as the "
              "treatment slot). Inspect, then delete this directory.")
    print("Structure (cf. evaluations/stage3_ab anatomy):")
    for f in sorted(out_dir.iterdir(), key=lambda p: p.name):
        note = "  <- SEALED, do not open" if f.name == ".blind_mapping.json" else ""
        print(f"  {f.name:32s} {f.stat().st_size:7d} bytes{note}")
    print("Labels G/J/P randomly assigned from --seed; mapping sealed.")
    print("Next: 2 independent agent teams, opposite evaluation orders "
          "(team 1 G->J->P, team 2 P->J->G); unblind only after all 6 verdicts.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--seed", type=int, required=True,
        help="REQUIRED, no default — the sealed label<->game mapping is a "
             "pure function of this seed, so a default would let anyone "
             "reconstruct it from the script. Pick it at campaign time.")
    p.add_argument(
        "--dry-run", action="store_true",
        help="build into evaluations/frontline_ab_dryrun/ with stand-in "
             "games (plumbing verification before Stage 1); delete after "
             "inspection.")
    args = p.parse_args()

    if args.dry_run:
        build(ROOT / "evaluations" / "frontline_ab_dryrun", DRY_ARMS,
              args.seed, dry=True)
    else:
        build(ROOT / "evaluations" / "frontline_ab", REAL_ARMS,
              args.seed, dry=False)


if __name__ == "__main__":
    main()
