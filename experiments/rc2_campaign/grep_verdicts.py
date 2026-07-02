#!/usr/bin/env python
"""RC2 campaign — pre-unblind verdict identifier grep (prereg §7, LOCKED
72890a0; PANEL_FINDINGS C11).

The orchestrator runs this over a blind pack AFTER all 21 verdicts are filed
and BEFORE opening `.blind_mapping.json`. Any hit is a potential blinding
breach and must be recorded and resolved before unblinding (recognition
disclosures themselves are reported-not-binding, prereg §8).

What is scanned — filed verdicts ONLY:
    every regular file in the pack directory whose name starts with
    ``team-`` (the filed-verdict convention ``team-{N}_game{L}.md``, plus
    any team-filed cross-game note). The TEMPLATE_* scaffold files are NOT
    scanned: they legitimately contain the "R8 4.10 ..." scoring-anchor
    line, and only team-WRITTEN content is evidence of contamination.

Identifier list (`STATIC_IDENTIFIERS`) — the §7-registered strings
(d4015, Connection Go, S3, run8, ...) plus this build's documented
extensions (e1453, R8, stage3, siege, menger, genesis_v2). Matching is
case-insensitive. Ambiguous tokens (`WORD_BOUNDED`) match only when not
embedded in a longer alphanumeric token, so "S3" hits but "AWS3000" does
not, "siege" hits but "besieged" does not, and "Connection Go" hits but
"connection goal(s)" — the engine helper's own status-line vocabulary —
does not; underscores and dots do NOT count as word characters here, so
"genesis_v2_run8.db" still trips "run8"/"menger"-style identifiers.

The R8/run8 carve-out (PANEL_FINDINGS.md C11 refuter 1, ~line 406):
compliant verdicts quote the briefing-supplied scoring anchor VERBATIM
("R8 4.10, R19 4.375 ..."), so a line matching "R8"/"run8" ONLY as part of
the verbatim anchor string "R8 4.10" is compliant — not a hit. The
carve-out is implemented by deleting every occurrence of the anchor string
from the line before matching those two identifiers (and ONLY those two);
any residual "R8"/"run8" on the line is a hit. "d4015" and "Connection Go"
are the clean discriminators and get no carve-out.

Dynamic identifiers (`pack_identifiers`) — defense in depth: slate
ids/canons are ALSO greppable, read from the pack's OWN anonymized
``games/*.json`` files, never from the sealed mapping. In a correctly
anonymized pack (game_id == bare label, metadata == {}) this set is empty;
if anonymization failed, the leaked strings (a non-label game_id, any
metadata string) become identifiers so the leak is caught in verdicts.

INVARIANT — the scanner must never open the sealed mapping: no code path
in this module reads `.blind_mapping.json`. Enforced structurally: the
only files opened are ``team-*`` regular files and ``games/*.json``; a
deleted or corrupted mapping does not change the scan (tested in
test_blind_pack.py), and the mapping's filename appears nowhere in this
module outside this docstring.

CLI:
    .venv/bin/python experiments/rc2_campaign/grep_verdicts.py <pack_dir>

prints every (file, identifier, line) hit; exit code 1 on any hit, 0 clean
— so the orchestrator can gate unblinding on it.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

#: Blind labels — a pack game whose game_id is one of these is correctly
#: anonymized and contributes no dynamic identifier.
LABELS = ("A", "B", "C", "D", "E", "F", "G")

#: §7-registered identifier strings ("d4015, Connection Go, S3, run8, …")
#: with the ellipsis expanded to this build's documented extensions:
#: e1453 (the R21 GE-top control), R8 (the anchor's campaign name),
#: stage3/siege (the SIEGE pack lineage), menger (the R21 family),
#: genesis_v2 (the source-db prefix).
STATIC_IDENTIFIERS = (
    "d4015",
    "Connection Go",
    "e1453",
    "run8",
    "R8",
    "S3",
    "stage3",
    "siege",
    "menger",
    "genesis_v2",
)

#: Tokens matched with alphanumeric word boundaries (no [A-Za-z0-9]
#: immediately before or after), so prose that merely contains them does
#: not false-positive: "besieged"/"AWS3000" don't trip "siege"/"S3", and —
#: verified against the 21 real rc2_phase_d verdicts — "connection goal(s)"
#: (the engine helper's own status-line vocabulary) doesn't trip
#: "Connection Go". Underscore and dot are deliberately NOT word
#: characters: "_menger.db" still hits.
WORD_BOUNDED = frozenset({"R8", "S3", "run8", "stage3", "siege", "menger",
                          "Connection Go"})

#: The verbatim briefing-supplied anchor substring that compliant verdicts
#: quote (template + BRIEFING both carry "R8 4.10"). Lines matching
#: R8/run8 ONLY inside this string are compliant (C11 carve-out).
ANCHOR_CARVEOUT = "R8 4.10"

#: Identifiers the carve-out applies to — ONLY the two the panel flagged.
CARVEOUT_IDENTIFIERS = frozenset({"R8", "run8"})

#: Minimum length for a dynamic (pack-derived) identifier — guards against
#: a degenerate leaked string like "x" flagging every line.
_MIN_DYNAMIC_LEN = 4

_CARVEOUT_RE = re.compile(re.escape(ANCHOR_CARVEOUT), re.IGNORECASE)


def _pattern(identifier: str) -> re.Pattern:
    esc = re.escape(identifier)
    if identifier in WORD_BOUNDED:
        return re.compile(rf"(?<![A-Za-z0-9]){esc}(?![A-Za-z0-9])",
                          re.IGNORECASE)
    return re.compile(esc, re.IGNORECASE)


def _metadata_strings(value) -> list[str]:
    """All string leaves in a (possibly nested) metadata value."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out = []
        for k, v in value.items():
            out.extend(_metadata_strings(k))
            out.extend(_metadata_strings(v))
        return out
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            out.extend(_metadata_strings(v))
        return out
    return []


def pack_identifiers(pack_dir: Path) -> list[str]:
    """Dynamic identifiers from the pack's OWN anonymized games — NEVER the
    sealed mapping. Empty for a correctly anonymized pack; an anonymization
    failure (non-label game_id, leftover metadata strings) is promoted to
    an identifier so it is caught in filed verdicts."""
    idents: set[str] = set()
    games_dir = Path(pack_dir) / "games"
    if not games_dir.is_dir():
        return []
    for path in sorted(games_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"WARNING: unreadable pack game {path.name}: {exc}",
                  file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        gid = data.get("game_id")
        if (isinstance(gid, str) and gid not in LABELS
                and len(gid) >= _MIN_DYNAMIC_LEN):
            idents.add(gid)
        for s in _metadata_strings(data.get("metadata")):
            if len(s) >= _MIN_DYNAMIC_LEN:
                idents.add(s)
    return sorted(idents)


def scan_verdicts(pack_dir) -> list[tuple[str, str, str]]:
    """Scan filed verdicts (team-* files) for identifier strings.

    Returns [(file_name, identifier, matching_line)], one tuple per
    (line, identifier) match, in file order. Empty list == clean.
    """
    pack_dir = Path(pack_dir)
    identifiers = list(STATIC_IDENTIFIERS)
    for ident in pack_identifiers(pack_dir):
        if ident not in identifiers:
            identifiers.append(ident)
    patterns = [(ident, _pattern(ident)) for ident in identifiers]

    hits: list[tuple[str, str, str]] = []
    for path in sorted(pack_dir.glob("team-*")):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            for ident, pat in patterns:
                haystack = line
                if ident in CARVEOUT_IDENTIFIERS:
                    haystack = _CARVEOUT_RE.sub("", line)
                if pat.search(haystack):
                    hits.append((path.name, ident, line))
    return hits


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.splitlines()[0])
        print("usage: grep_verdicts.py <pack_dir>")
        return 2
    pack_dir = Path(argv[0])
    if not pack_dir.is_dir():
        print(f"ERROR: {pack_dir} is not a directory")
        return 2
    hits = scan_verdicts(pack_dir)
    filed = [p.name for p in sorted(pack_dir.glob("team-*")) if p.is_file()]
    if hits:
        print(f"BLINDING GREP: {len(hits)} hit(s) across {len(filed)} filed "
              f"verdict file(s) — resolve BEFORE unblinding:")
        for fname, ident, line in hits:
            print(f"  {fname}: [{ident}] {line.strip()}")
        return 1
    print(f"BLINDING GREP: clean — 0 hits across {len(filed)} filed "
          f"verdict file(s). OK to open the sealed mapping.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
