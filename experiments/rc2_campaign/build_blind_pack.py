#!/usr/bin/env python
"""RC2 campaign — 7-label blind-pack builder (prereg §7, LOCKED 72890a0;
PANEL_FINDINGS C11 + C15).

Builds the blind evaluation pack for the campaign slate: 7 games labeled
A–G, 3 independent evaluator teams, 21 verdicts. Forked from
experiments/frontline/build_blind_pack.py (count-asserted `replace_exact`
substitution, sealed --seed shuffle, refuse-to-overwrite, --dry-run), with
the pack CONVENTION taken from evaluations/rc2_phase_d — the registered
convention (C15) — wherever the two differ:

* labels A–G, per-team evaluation orders for 3 teams, verdict files
  `team-{N}_game{A..G}.md`, unblind only after all 21 filed;
* play.py is rc2_phase_d's multi-dimensional engine helper (describe_rules
  / decode / print_legal / render_board — handles multi-dim boards, CA,
  MOVE, PIE), copied into the pack with ONLY its pack paths and campaign
  name substituted (each substitution count-asserted; behaviour identical).
  Rules/action-space help is REGENERATED at runtime from each packed
  game's actual GameDefV2 — the §7 obligation. Unlike frontline, no
  geometry line is baked into the BRIEFING: rc2_phase_d's registered
  "action-id schemes differ per game — read them from --rules" caveat is
  the convention for a heterogeneous slate (conflict resolved toward
  rc2_phase_d, logged);
* the BRIEFING's out-of-bounds list is REPLACED by the §7-registered one:
  everything under evaluations/ except this pack dir; experiments/; docs/;
  analysis*.md; memory files; git metadata;
* every verdict template carries the §7 mandatory recognition-disclosure
  line ("if you believe you can identify this game or recall a prior
  score, say so and continue");
* the orchestrator-only section (below the BRIEFING's STOP divider) keeps
  role win-split logging (win split >80/20 flagged; balance signal, not a
  verdict invalidator) and instructs the orchestrator to run
  experiments/rc2_campaign/grep_verdicts.py over the filed verdicts BEFORE
  opening the sealed mapping.

Anonymization (rc2_phase_d convention): each packed game is written to
games/<LABEL>.json with `game_id` rewritten to the bare label and
`metadata` emptied to {}. Pack copies are DERIVATIVES — the caller's slate
JSON and the canonical game files are never modified.

--seed is REQUIRED and has NO default, deliberately (mirroring frontline):
the label<->game assignment AND the per-team evaluation orders are a pure
function of the seed, so a default baked into this file would let anyone
who can read the script reconstruct the sealed mapping. The runner picks a
fresh seed at campaign time and keeps it out of evaluator-visible channels
until unblinding (the seed is recorded inside the sealed mapping file
itself, `label_seed`, for post-campaign audit).

Slate JSON schema (--slate-json) — produced by the orchestrator from
`slate.build_slate(...)` output (experiments/rc2_campaign/slate.py): a
JSON array of EXACTLY 7 objects, one per slate game. Every object:

    {
      "role": "top" | "contrast" | "validity_anchor" | "carry_in",
      "game": { ... GameDefV2.to_dict() ... },      # written to the pack
      ...metadata (below; sealed into .blind_mapping.json, never packed)
    }

Role composition: 5 elites (roles "top"/"contrast") + exactly one
"validity_anchor" (d4015) + exactly one "carry_in" (S3). Required
metadata per role (extra keys are allowed and sealed along):

    elites ("top"/"contrast"): "slate_id" (e.g. "S1"), "canon"
        (canonical_hash), "full_conv_mean_floored" (the §7 selection PG),
        "cell" (M-archive cell key [family, interaction_bin, length_bin]);
    fixtures ("validity_anchor"/"carry_in"): "game_id", "source"
        (e.g. "genesis_v2_run8.db"); "slate_id" optional.

The builder treats "game" as opaque JSON (no engine import): play.py
validates and describes each game from its actual definition at run time.

.blind_mapping.json is sealed with the do-not-open note FIRST, then
labels (per-label slate metadata, game dict excluded), then team_orders,
then the seed:  {"note", "labels", "team_orders", "label_seed"}.

--out-dir (default evaluations/rc2_blind) — every pack-internal path
reference follows the output directory name, so renaming the pack is
mechanical. Refuses to overwrite an existing out-dir (it may contain a
sealed mapping and filed verdicts).

--dry-run builds into <out-dir>_dryrun/ from stand-in games (the 7
already-anonymized rc2_phase_d pack games — real, heterogeneous GameDefV2
definitions covering multi-dim/CA/MOVE/PIE) so pack plumbing and play.py
can be verified before the campaign slate exists. Inspect, then delete
the directory manually. No --slate-json needed.

Usage:
    .venv/bin/python experiments/rc2_campaign/build_blind_pack.py \
        --seed <runner-chosen> --slate-json <path>
    .venv/bin/python experiments/rc2_campaign/build_blind_pack.py \
        --seed <any> --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
#: The registered pack convention this builder forks (PANEL_FINDINGS C15).
SRC = ROOT / "evaluations" / "rc2_phase_d"

LABELS = ("A", "B", "C", "D", "E", "F", "G")
TEAMS = (1, 2, 3)

ELITE_ROLES = ("top", "contrast")
FIXTURE_ROLES = ("validity_anchor", "carry_in")
ELITE_REQUIRED = ("slate_id", "canon", "full_conv_mean_floored", "cell")
FIXTURE_REQUIRED = ("game_id", "source")

#: §7's mandatory recognition-disclosure wording — the quoted phrase must
#: appear VERBATIM (and contiguously) in every verdict template.
RECOGNITION_PHRASE = ("if you believe you can identify this game or recall "
                      "a prior score, say so and continue")

SEALED_NOTE = (
    "SEALED — ORCHESTRATOR-ONLY. Do not open before all 21 verdicts "
    "(3 teams x 7 games) are filed in evaluations/{pack}/ AND "
    "experiments/rc2_campaign/grep_verdicts.py has been run and every hit "
    "recorded and dispositioned over the filed verdicts (prereg §7, LOCKED "
    "72890a0). Opening earlier unblinds and invalidates the campaign."
)


def replace_exact(text: str, old: str, new: str, expect: int = 1,
                  where: str = "BRIEFING") -> str:
    """Replace with an occurrence-count assertion — drift in the locked
    source instrument fails THIS script loudly, never silently."""
    n = text.count(old)
    if n != expect:
        sys.exit(
            f"ERROR: {where} drift — expected {expect} occurrence(s) of "
            f"{old!r}, found {n}. Re-audit substitutions against "
            f"evaluations/rc2_phase_d/ before building the pack."
        )
    return text.replace(old, new)


def _lock_guards(text: str, must: tuple[str, ...], forbidden: tuple[str, ...],
                 where: str) -> str:
    for m in must:
        if m not in text:
            sys.exit(f"ERROR: {where} instrument-lock guard failed — "
                     f"missing {m!r}.")
    for f in forbidden:
        if f in text:
            sys.exit(f"ERROR: {where} blinding guard failed — forbidden "
                     f"string {f!r} present in evaluator-visible text.")
    return text


# --------------------------------------------------------------------------
# Slate validation (schema in the module docstring)
# --------------------------------------------------------------------------

def validate_slate(entries) -> None:
    if not isinstance(entries, list) or len(entries) != len(LABELS):
        sys.exit(f"ERROR: slate JSON must be a list of exactly {len(LABELS)} "
                 f"entries (got {len(entries) if isinstance(entries, list) else type(entries).__name__}) — prereg §7 composition.")
    roles = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            sys.exit(f"ERROR: slate entry {i} is not an object.")
        role = e.get("role")
        if role not in ELITE_ROLES + FIXTURE_ROLES:
            sys.exit(f"ERROR: slate entry {i} has invalid role {role!r} "
                     f"(expected one of {ELITE_ROLES + FIXTURE_ROLES}).")
        if not isinstance(e.get("game"), dict):
            sys.exit(f"ERROR: slate entry {i} ({role}) is missing the "
                     f"'game' dict.")
        required = ELITE_REQUIRED if role in ELITE_ROLES else FIXTURE_REQUIRED
        missing = [k for k in required if k not in e]
        if missing:
            sys.exit(f"ERROR: slate entry {i} ({role}) is missing required "
                     f"metadata {missing} — see the slate JSON schema in "
                     f"build_blind_pack.py.")
        roles.append(role)
    if roles.count("validity_anchor") != 1 or roles.count("carry_in") != 1:
        sys.exit(f"ERROR: slate must contain exactly one validity_anchor and "
                 f"exactly one carry_in (got roles {roles}) — prereg §7.")
    if roles.count("top") != 3 or roles.count("contrast") != 2:
        sys.exit(f"ERROR: slate must contain exactly 3 'top' and exactly 2 "
                 f"'contrast' elites (got roles {roles}) — prereg §7 role "
                 f"split.")


# --------------------------------------------------------------------------
# play.py — rc2_phase_d's engine helper, copied with pack paths substituted.
# Change map vs evaluations/rc2_phase_d/play.py (everything else identical):
#   1. docstring first line: campaign name neutralized ("RC2 Phase D
#      blind-eval helper" -> "Blind-eval helper") — a pack must not point
#      evaluators at evaluations/rc2_phase_d/ (unblinded identity tables).
#   2. argparse description: same neutralization.
#   3. "evaluations/rc2_phase_d" -> "evaluations/<pack>" (4 occurrences:
#      the docstring games path + 3 usage lines).
# Label loading was ALREADY pack-relative in the source
# (HERE / "games" / f"{label}.json") and never touches .blind_mapping.json.
# --------------------------------------------------------------------------

def build_play_py(pack_name: str) -> str:
    text = (SRC / "play.py").read_text(encoding="utf-8")
    text = replace_exact(
        text,
        '"""RC2 Phase D blind-eval helper — self-contained player for games A-G.',
        '"""Blind-eval helper — self-contained player for games A-G.',
        1, "play.py")
    text = replace_exact(
        text,
        'description="RC2 Phase D blind-eval game runner (games A-G).")',
        'description="Blind-eval game runner (games A-G).")',
        1, "play.py")
    text = replace_exact(text, "evaluations/rc2_phase_d",
                         f"evaluations/{pack_name}", 4, "play.py")
    return _lock_guards(
        text,
        must=("def describe_rules(", "def decode(", "def print_legal(",
              "def render_board(", 'HERE / "games" / f"{label}.json"'),
        forbidden=("rc2_phase_d", "Phase D"),
        where="play.py")


# --------------------------------------------------------------------------
# BRIEFING — rc2_phase_d's, adapted by count-asserted substitution only.
# Change map vs evaluations/rc2_phase_d/BRIEFING.md:
#   1. header: campaign name neutralized;
#   2. out-of-bounds block REPLACED by the §7-registered list (C11);
#   3. per-team game orders rewritten from this pack's sealed seed;
#   4. the three TEMPLATE.md references adapted to the 21 materialized
#      TEMPLATE_team-{N}_game{L}.md files;
#   5. orchestrator-only section (below the STOP divider) rewritten:
#      21-verdict unblind rule + grep_verdicts.py-BEFORE-mapping
#      instruction + the win-split logging paragraph carried verbatim
#      (drift-guarded against the source);
#   6. pack paths: "evaluations/rc2_phase_d" -> "evaluations/<pack>";
#   7. cross-game-comparison "separate note" sentence gains one naming
#      instruction (Task-11 review minor #3): a separate note must be named
#      `team-{N}_<something>.md` so it falls inside grep_verdicts.py's
#      `team-*` scan glob (the BRIEFING already permits filing it as a
#      separate note; the scanner only ever globbed `team-*`).
# Everything else evaluators use as the instrument (5-phase protocol
# pointer, action-id caveat, fairness probe, anchors) is carried verbatim
# and lock-guarded.
# --------------------------------------------------------------------------

_OLD_HEADER = "# RC2 Phase D blind eval — agent team briefing"

_OLD_OOB_BLOCK = """Do NOT read: `.blind_mapping.json`, `PREREGISTRATION.md` (in this directory),
anything under `experiments/` (the entire directory), `evaluations/run21/`,
`evaluations/stage3_ab/`, or the source of `play.py` (usage output only).
Also out of bounds: any git commands (status, log, branch, diff) or repo
metadata. Interact with the games ONLY by running `play.py` as shown."""

_NEW_OOB_BLOCK = """Do NOT read — the out-of-bounds list registered in the campaign
preregistration applies verbatim:

- EVERYTHING under `evaluations/` EXCEPT this pack directory
  (`evaluations/{pack}/`): no other evaluation pack, no prior verdicts,
  no summaries.
- Anything under `experiments/` (the entire directory).
- Anything under `docs/` (the entire directory).
- Any `analysis*.md` file.
- Memory files (MEMORY.md, memory/ directories, auto-memory topic files).
- Git/repo metadata: any git command (status, log, branch, diff, show) and
  anything under `.git/`.

Also out of bounds INSIDE this pack: `.blind_mapping.json` (sealed), the
game-definition JSONs under `games/`, and the source of `play.py` (usage
output only). Interact with the games ONLY by running `play.py` as shown."""

_OLD_TEAM_ORDER_LINES = {
    1: "- **Team 1:** C, B, F, G, E, D, A",
    2: "- **Team 2:** F, B, A, E, G, D, C",
    3: "- **Team 3:** F, C, G, A, B, D, E",
}

#: Carried VERBATIM from rc2_phase_d's orchestrator section into the new
#: one — drift-guarded: the build fails if the source no longer contains
#: this exact text.
_WIN_SPLIT_TEXT = """### Role win split logging

For each game, log the win split across the two roles from the evaluator game
lines (how many P1-role games did P1 win, how many P2-role games did P2 win).
Flag any game where the win split exceeds 80/20 across the filed game lines —
this is a balance signal, not a verdict invalidator. These feed the
fairness-flag reporting (pre-registered as reported-not-binding)."""

_NEW_ORCHESTRATOR_BODY = """### Unblinding procedure

Unblind ONLY after all 21 verdicts (3 teams × 7 games) are filed and saved
to `evaluations/{pack}/`. BEFORE opening the mapping, run the pre-unblind
identifier grep over the filed verdicts:

    .venv/bin/python experiments/rc2_campaign/grep_verdicts.py evaluations/{pack}

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

{win_split}
"""


def build_briefing(pack_name: str, team_orders: dict[str, list[str]]) -> str:
    text = (SRC / "BRIEFING.md").read_text(encoding="utf-8")
    if _WIN_SPLIT_TEXT not in text:
        sys.exit("ERROR: BRIEFING drift — the role-win-split paragraph no "
                 "longer matches evaluations/rc2_phase_d/BRIEFING.md; "
                 "re-audit _WIN_SPLIT_TEXT before building the pack.")

    text = replace_exact(text, _OLD_HEADER,
                         "# Blind eval — agent team briefing")
    text = replace_exact(text, _OLD_OOB_BLOCK,
                         _NEW_OOB_BLOCK.format(pack=pack_name))
    for t, old in _OLD_TEAM_ORDER_LINES.items():
        text = replace_exact(
            text, old,
            f"- **Team {t}:** " + ", ".join(team_orders[f"team-{t}"]))
    text = replace_exact(
        text,
        "## Per-game protocol (5 phases, per TEMPLATE.md)",
        "## Per-game protocol (5 phases, per your TEMPLATE files)")
    text = replace_exact(
        text,
        "Follow the 5-phase protocol in `TEMPLATE.md` for EACH game (copy the\n"
        "template once per game).",
        "Follow the 5-phase protocol in your team's TEMPLATE files for EACH\n"
        "game (`TEMPLATE_team-{N}_game{A..G}.md` — one per game).")
    text = replace_exact(
        text,
        "(e.g. `team-2_gameC.md`). Use `TEMPLATE.md` as your rubric — copy it per game\n"
        "and fill ALL `{{...}}` placeholders.",
        "(e.g. `team-2_gameC.md`). Use your team's `TEMPLATE_team-{N}_game{A..G}.md`\n"
        "files as your rubric — copy each one and fill ALL `{{...}}` placeholders.")
    text = replace_exact(
        text,
        "After filing all per-game verdicts, add a final **Cross-game comparison**\n"
        "section (in your last filed verdict or as a separate note):",
        "After filing all per-game verdicts, add a final **Cross-game comparison**\n"
        "section (in your last filed verdict or as a separate note). If filed as a\n"
        "separate note, name it `team-{N}_<something>.md` (e.g.\n"
        "`team-2_cross_game_notes.md`) so it falls inside the pre-unblind grep's\n"
        "`team-*` scan glob:")

    # Orchestrator-only section: replace from the unblinding marker to EOF
    # (below the STOP divider — not part of the evaluator instrument).
    marker = "### Unblinding procedure"
    if text.count(marker) != 1:
        sys.exit("ERROR: BRIEFING drift — unblinding marker not found "
                 "exactly once.")
    text = text[: text.index(marker)] + _NEW_ORCHESTRATOR_BODY.format(
        pack=pack_name, win_split=_WIN_SPLIT_TEXT)

    # Pack paths (3 usage lines + the verdict-file path; the 5th source
    # occurrence lived in the replaced orchestrator section).
    text = replace_exact(text, "evaluations/rc2_phase_d",
                         f"evaluations/{pack_name}", 4)

    return _lock_guards(
        text,
        must=("## Fairness-perception probe (mandatory, every game)",
              "R8 4.10, R19 4.375 (top 5.0), R20 3.73, R21 3.69.",
              "Action-id schemes differ per game",
              "## Cross-game comparison (after all 7 games are done)",
              "all 21 verdicts (3 teams × 7 games)",
              "grep_verdicts.py",
              _WIN_SPLIT_TEXT),
        forbidden=("rc2_phase_d", "Phase D", "TEMPLATE.md",
                   "stage3_ab", "run21"),
        where="BRIEFING")


# --------------------------------------------------------------------------
# Verdict TEMPLATEs — rc2_phase_d/TEMPLATE.md materialized per team x game.
# Change map vs the source template:
#   1. {{N}} -> team number (2 occurrences), {{LABEL}} -> label (3);
#   2. "Copy this template once per game to" -> "Copy this template to"
#      (the pack ships one template PER game, so "once per game" would
#      contradict the file it sits in);
#   3. the §7 mandatory recognition-disclosure line inserted as the FIRST
#      Phase 5 item (before any score is written), quoted phrase verbatim.
# The 5-phase structure, per-role sub-scores, fairness probe, and Overall
# anchors are untouched and lock-guarded.
# --------------------------------------------------------------------------

_PHASE5_ANCHOR = ("## Phase 5 — Verdict\n"
                  "\n"
                  "- P1-role experience sub-score (1-10): {{p1_subscore}}")

_PHASE5_WITH_RECOGNITION = (
    "## Phase 5 — Verdict\n"
    "\n"
    "- **Recognition disclosure (mandatory):** " + RECOGNITION_PHRASE + ".\n"
    "  Disclosure (or \"none\"): {{recognition_disclosure}}\n"
    "- P1-role experience sub-score (1-10): {{p1_subscore}}")


def build_template(src_text: str, team: int, label: str) -> str:
    where = f"TEMPLATE_team-{team}_game{label}.md"
    text = replace_exact(src_text, "{{N}}", str(team), 2, where)
    text = replace_exact(text, "{{LABEL}}", label, 3, where)
    text = replace_exact(text, "Copy this template once per game to",
                         "Copy this template to", 1, where)
    text = replace_exact(text, _PHASE5_ANCHOR, _PHASE5_WITH_RECOGNITION,
                         1, where)
    return _lock_guards(
        text,
        must=("## Phase 1", "## Phase 2", "## Phase 3", "## Phase 4",
              "## Phase 5",
              "Fairness perception (1-5",
              "R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69",
              RECOGNITION_PHRASE),
        forbidden=("rc2_phase_d", "{{N}}", "{{LABEL}}"),
        where=where)


# --------------------------------------------------------------------------
# Dry-run stand-ins: the 7 already-anonymized rc2_phase_d pack games —
# real, heterogeneous GameDefV2 definitions (multi-dim, CA, MOVE, PIE)
# through which play.py's regenerated rules help can be exercised.
# --------------------------------------------------------------------------

def dry_run_entries() -> list[dict]:
    roles = ("top", "top", "top", "contrast", "contrast",
             "validity_anchor", "carry_in")
    entries = []
    for i, (src_label, role) in enumerate(zip(LABELS, roles)):
        game = json.loads(
            (SRC / "games" / f"{src_label}.json").read_text(encoding="utf-8"))
        entry: dict = {"role": role, "slate_id": f"DRY-{i + 1}", "game": game}
        if role in ELITE_ROLES:
            entry.update(
                canon=f"dryrun_standin_{src_label.lower()}",
                full_conv_mean_floored=0.0,
                cell=["dryrun", 0, i],
            )
        else:
            entry.update(
                game_id=f"dryrun_standin_{src_label.lower()}",
                source=f"evaluations/rc2_phase_d/games/{src_label}.json "
                       f"(dry-run stand-in)",
            )
        entries.append(entry)
    return entries


# --------------------------------------------------------------------------
# Pack assembly
# --------------------------------------------------------------------------

def build(out_dir: Path, entries: list[dict], seed: int, dry: bool) -> None:
    out_dir = Path(out_dir)
    pack_name = out_dir.name
    if out_dir.exists():
        sys.exit(
            f"ERROR: {out_dir} already exists — refusing to overwrite (it "
            f"may contain a sealed mapping and filed verdicts). Remove it "
            f"manually if you really mean to rebuild."
        )
    validate_slate(entries)

    # Sealed assignment + per-team orders: a pure function of --seed.
    rng = random.Random(seed)
    perm = rng.sample(range(len(LABELS)), len(LABELS))
    assignment = {LABELS[i]: entries[perm[i]] for i in range(len(LABELS))}
    team_orders = {f"team-{t}": rng.sample(LABELS, len(LABELS))
                   for t in TEAMS}

    (out_dir / "games").mkdir(parents=True)

    # Game JSONs -> anonymized pack derivatives games/<LABEL>.json
    # (rc2_phase_d convention: game_id = bare label, metadata = {}).
    for label in LABELS:
        data = dict(assignment[label]["game"])
        data["game_id"] = label
        data["metadata"] = {}
        (out_dir / "games" / f"{label}.json").write_text(
            json.dumps(data, indent=1) + "\n", encoding="utf-8")

    # Sealed mapping — do-not-open note FIRST, then labels, then
    # team_orders, then the seed.
    sealed = {
        "note": SEALED_NOTE.format(pack=pack_name),
        "labels": {label: {k: v for k, v in assignment[label].items()
                           if k != "game"}
                   for label in LABELS},
        "team_orders": team_orders,
        "label_seed": seed,
    }
    (out_dir / ".blind_mapping.json").write_text(
        json.dumps(sealed, indent=1) + "\n", encoding="utf-8")

    # BRIEFING + play.py + 21 verdict templates.
    (out_dir / "BRIEFING.md").write_text(
        build_briefing(pack_name, team_orders), encoding="utf-8")
    (out_dir / "play.py").write_text(build_play_py(pack_name),
                                     encoding="utf-8")
    template_src = (SRC / "TEMPLATE.md").read_text(encoding="utf-8")
    for t in TEAMS:
        for label in LABELS:
            (out_dir / f"TEMPLATE_team-{t}_game{label}.md").write_text(
                build_template(template_src, t, label), encoding="utf-8")

    # Report structure WITHOUT revealing the assignment (orders are not
    # secret — only identities are; rc2_phase_d BRIEFING convention).
    print(f"Blind pack built: {out_dir}")
    if dry:
        print("*** DRY RUN — rc2_phase_d stand-in games. Inspect, then "
              "delete this directory.")
    print("Structure (cf. evaluations/rc2_phase_d anatomy):")
    for f in sorted(out_dir.rglob("*")):
        if f.is_dir():
            continue
        note = "  <- SEALED, do not open" \
            if f.name == ".blind_mapping.json" else ""
        rel = f.relative_to(out_dir)
        print(f"  {str(rel):36s} {f.stat().st_size:7d} bytes{note}")
    print(f"Labels A-G randomly assigned from --seed; mapping sealed.")
    for team, order in team_orders.items():
        print(f"  {team} evaluation order: {' -> '.join(order)}")
    print("Next: 3 independent agent teams, per-team orders above; unblind "
          "only after all 21 verdicts AND "
          "experiments/rc2_campaign/grep_verdicts.py has been run with all "
          "hits dispositioned.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--seed", type=int, required=True,
        help="REQUIRED, no default — the sealed label<->game mapping and "
             "the per-team orders are a pure function of this seed, so a "
             "default would let anyone reconstruct them from the script. "
             "Pick it at campaign time.")
    p.add_argument(
        "--slate-json", default=None,
        help="path to the 7-entry slate JSON (schema in the module "
             "docstring; produced by the orchestrator from "
             "slate.build_slate output). Required unless --dry-run.")
    p.add_argument(
        "--out-dir", default="evaluations/rc2_blind",
        help="pack output directory, relative to the repo root; every "
             "pack-internal path reference follows the directory name, so "
             "renaming the pack is mechanical.")
    p.add_argument(
        "--dry-run", action="store_true",
        help="build into <out-dir>_dryrun/ with rc2_phase_d stand-in games "
             "(plumbing verification); delete after inspection.")
    args = p.parse_args()

    out_dir = ROOT / args.out_dir
    if args.dry_run:
        build(out_dir.with_name(out_dir.name + "_dryrun"),
              dry_run_entries(), args.seed, dry=True)
    else:
        if not args.slate_json:
            p.error("--slate-json is required unless --dry-run")
        try:
            entries = json.loads(
                Path(args.slate_json).read_text(encoding="utf-8"))
        except FileNotFoundError:
            sys.exit(f"ERROR: --slate-json file not found: "
                     f"{args.slate_json}")
        except json.JSONDecodeError as exc:
            sys.exit(f"ERROR: --slate-json is not valid JSON "
                     f"({args.slate_json}): {exc}")
        build(out_dir, entries, args.seed, dry=False)


if __name__ == "__main__":
    main()
