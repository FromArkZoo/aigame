"""Tests for Task 11: build_blind_pack.py (7-label blind-pack generator) +
grep_verdicts.py (pre-unblind identifier grep). Prereg §7 (LOCKED 72890a0).

Pure / tmp-dir tests — no engine needed except the single play.py subprocess
smoke test (which runs on the dry-run stand-ins, real GameDefV2 games from
the rc2_phase_d pack, with PYTHONPATH supplying the repo root because the
tmp pack is not under evaluations/).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.rc2_campaign import build_blind_pack as bbp
from experiments.rc2_campaign import grep_verdicts as gv

ROOT = Path(__file__).resolve().parents[2]
LABELS = ("A", "B", "C", "D", "E", "F", "G")
TEAMS = (1, 2, 3)

RECOGNITION_PHRASE = ("if you believe you can identify this game or recall "
                      "a prior score, say so and continue")

# The compliant anchor line as a team files it (copied from the template).
COMPLIANT_ANCHOR_LINE = ("- **Overall (1-10, anchored: R8 4.10, R19 4.375 "
                         "top 5.0, R20 3.73, R21 3.69;")


# ---------------------------------------------------------------------------
# Stub slate (schema documented in build_blind_pack.py's module docstring)
# ---------------------------------------------------------------------------

def stub_game(gid: str) -> dict:
    """Opaque game dict — the builder treats games as JSON, no engine."""
    return {
        "version": 2,
        "game_id": gid,
        "num_dimensions": 2,
        "axis_size": 5,
        "topology_type": "grid",
        "win_condition": {"condition_type": "connection", "max_turns": 60},
        "metadata": {"provenance": f"secret_lineage_of_{gid}"},
    }


def stub_slate() -> list:
    entries = []
    for i in range(3):
        entries.append({
            "role": "top",
            "slate_id": f"S{i + 1}",
            "canon": f"aaaa{i}cafe{i}hash",
            "full_conv_mean_floored": round(0.40 - 0.05 * i, 4),
            "cell": ["connection", 3, i],
            "game": stub_game(f"elite_top_{i}"),
        })
    for i in range(2):
        entries.append({
            "role": "contrast",
            "slate_id": f"S{i + 4}",
            "canon": f"bbbb{i}feed{i}hash",
            "full_conv_mean_floored": round(0.02 + 0.01 * i, 4),
            "cell": ["territory", 1, i],
            "game": stub_game(f"elite_contrast_{i}"),
        })
    entries.append({
        "role": "validity_anchor",
        "slate_id": "C+",
        "game_id": "d4015a646ae3",
        "source": "genesis_v2_run8.db",
        "game": stub_game("d4015a646ae3"),
    })
    entries.append({
        "role": "carry_in",
        "slate_id": "S3-carry",
        "game_id": "0165399e5aef",
        "source": "rc2_planning_gap (registered carry-in)",
        "game": stub_game("0165399e5aef"),
    })
    return entries


@pytest.fixture()
def pack(tmp_path):
    out = tmp_path / "pack"
    bbp.build(out, stub_slate(), seed=1234, dry=False)
    return out


def read_mapping_pairs(pack_dir):
    """(ordered key list, parsed dict) of the sealed mapping."""
    raw = (pack_dir / ".blind_mapping.json").read_text()
    pairs = json.loads(raw, object_pairs_hook=lambda p: p)
    return [k for k, _ in pairs], json.loads(raw)


# ---------------------------------------------------------------------------
# Pack structure
# ---------------------------------------------------------------------------

class TestPackStructure:
    def test_seven_anonymized_games(self, pack):
        for label in LABELS:
            p = pack / "games" / f"{label}.json"
            assert p.exists(), f"missing games/{label}.json"
            data = json.loads(p.read_text())
            assert data["game_id"] == label
            assert data["metadata"] == {}, "metadata must be emptied (anonymization)"
        assert len(list((pack / "games").glob("*.json"))) == 7

    def test_no_identity_leak_in_evaluator_files(self, pack):
        """No slate canon / game_id / provenance string reachable from any
        evaluator-visible file."""
        secrets = ["elite_top", "elite_contrast", "d4015", "0165399e5aef",
                   "secret_lineage", "cafe0hash", "rc2_phase_d", "Phase D"]
        visible = [pack / "BRIEFING.md", pack / "play.py"]
        visible += sorted(pack.glob("TEMPLATE_*.md"))
        visible += sorted((pack / "games").glob("*.json"))
        for f in visible:
            text = f.read_text()
            for s in secrets:
                assert s not in text, f"{s!r} leaked into {f.name}"

    def test_21_templates(self, pack):
        names = sorted(p.name for p in pack.glob("TEMPLATE_*.md"))
        expected = sorted(f"TEMPLATE_team-{t}_game{lab}.md"
                          for t in TEAMS for lab in LABELS)
        assert names == expected

    def test_templates_recognition_line_and_label(self, pack):
        for t in TEAMS:
            for lab in LABELS:
                text = (pack / f"TEMPLATE_team-{t}_game{lab}.md").read_text()
                assert RECOGNITION_PHRASE in text, \
                    f"recognition-disclosure line missing in team-{t} game{lab}"
                assert f"--game {lab}" in text
                assert f"team-{t}_game{lab}.md" in text
                assert "{{N}}" not in text and "{{LABEL}}" not in text
                # 5-phase instrument survived
                for must in ("## Phase 1", "## Phase 2", "## Phase 3",
                             "## Phase 4", "## Phase 5",
                             "Fairness perception (1-5",
                             "R8 4.10, R19 4.375 top 5.0, R20 3.73, R21 3.69"):
                    assert must in text, f"{must!r} missing in team-{t} game{lab}"

    def test_sealed_mapping_shape(self, pack):
        keys, mapping = read_mapping_pairs(pack)
        assert keys[0] == "note", "do-not-open note must be the FIRST key"
        assert keys == ["note", "labels", "team_orders", "label_seed"]
        assert mapping["label_seed"] == 1234
        assert "grep_verdicts.py" in mapping["note"]
        assert sorted(mapping["labels"]) == sorted(LABELS)
        # elites carry slate_id/canon/PG/cell/role; fixtures game_id/source/role
        roles = [v["role"] for v in mapping["labels"].values()]
        assert roles.count("validity_anchor") == 1
        assert roles.count("carry_in") == 1
        for v in mapping["labels"].values():
            assert "game" not in v, "sealed mapping must not embed the game dict"
            if v["role"] in ("top", "contrast"):
                for k in ("slate_id", "canon", "full_conv_mean_floored", "cell"):
                    assert k in v
            else:
                for k in ("game_id", "source"):
                    assert k in v
        # team orders: 3 teams, each a permutation of the 7 labels
        assert sorted(mapping["team_orders"]) == ["team-1", "team-2", "team-3"]
        for order in mapping["team_orders"].values():
            assert sorted(order) == sorted(LABELS)

    def test_briefing_contents(self, pack):
        text = (pack / "BRIEFING.md").read_text()
        # (a) §7-registered out-of-bounds list
        for must in ("EVERYTHING under `evaluations/` EXCEPT this pack",
                     "`experiments/`", "`docs/`", "`analysis*.md`",
                     "Memory files (MEMORY.md", "git"):
            assert must in text, f"out-of-bounds item {must!r} missing"
        # old (weaker) phase_d list must be GONE
        assert "evaluations/run21/" not in text
        assert "evaluations/stage3_ab/" not in text
        # (b) action-id caveat
        assert "Action-id schemes differ per game" in text
        # (d)+(e) orchestrator section: 21-verdict rule + grep-before-unblind
        assert "all 21 verdicts (3 teams × 7 games)" in text
        assert "grep_verdicts.py" in text
        assert text.index("grep_verdicts.py") > text.index("ORCHESTRATOR-ONLY")
        assert "win split exceeds 80/20" in text
        assert "balance signal, not a verdict invalidator" in text
        # instrument locks
        assert "## Fairness-perception probe (mandatory, every game)" in text
        assert "R8 4.10, R19 4.375 (top 5.0), R20 3.73, R21 3.69." in text
        assert "## Cross-game comparison (after all 7 games are done)" in text
        # pack-relative paths
        assert f"evaluations/{pack.name}/play.py" in text

    def test_briefing_orders_match_sealed_orders(self, pack):
        text = (pack / "BRIEFING.md").read_text()
        _, mapping = read_mapping_pairs(pack)
        for t in TEAMS:
            line = f"- **Team {t}:** " + ", ".join(mapping["team_orders"][f"team-{t}"])
            assert line in text, f"briefing order line for team {t} wrong/missing"

    def test_refuse_to_overwrite(self, pack):
        with pytest.raises(SystemExit):
            bbp.build(pack, stub_slate(), seed=99, dry=False)
        # the sealed mapping survived untouched
        _, mapping = read_mapping_pairs(pack)
        assert mapping["label_seed"] == 1234


# ---------------------------------------------------------------------------
# Sealed shuffle: determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def _mapping(self, tmp_path, name, seed):
        out = tmp_path / name
        bbp.build(out, stub_slate(), seed=seed, dry=False)
        return read_mapping_pairs(out)[1]

    def test_same_seed_identical(self, tmp_path):
        m1 = self._mapping(tmp_path, "p1", 4242)
        m2 = self._mapping(tmp_path, "p2", 4242)
        assert m1["labels"] == m2["labels"]
        assert m1["team_orders"] == m2["team_orders"]

    def test_different_seed_differs(self, tmp_path):
        # fixed pair verified to differ (assignment is a pure fn of the seed)
        m1 = self._mapping(tmp_path, "p1", 1)
        m2 = self._mapping(tmp_path, "p2", 2)
        assert (m1["labels"] != m2["labels"]
                or m1["team_orders"] != m2["team_orders"])


# ---------------------------------------------------------------------------
# Slate JSON schema validation
# ---------------------------------------------------------------------------

class TestSlateValidation:
    def test_wrong_count_rejected(self, tmp_path):
        with pytest.raises(SystemExit):
            bbp.build(tmp_path / "p", stub_slate()[:6], seed=1, dry=False)

    def test_missing_role_rejected(self, tmp_path):
        entries = stub_slate()
        del entries[0]["role"]
        with pytest.raises(SystemExit):
            bbp.build(tmp_path / "p", entries, seed=1, dry=False)

    def test_elite_missing_canon_rejected(self, tmp_path):
        entries = stub_slate()
        del entries[1]["canon"]
        with pytest.raises(SystemExit):
            bbp.build(tmp_path / "p", entries, seed=1, dry=False)

    def test_fixture_missing_source_rejected(self, tmp_path):
        entries = stub_slate()
        del entries[5]["source"]
        with pytest.raises(SystemExit):
            bbp.build(tmp_path / "p", entries, seed=1, dry=False)

    def test_two_anchors_rejected(self, tmp_path):
        entries = stub_slate()
        entries[6]["role"] = "validity_anchor"
        with pytest.raises(SystemExit):
            bbp.build(tmp_path / "p", entries, seed=1, dry=False)


# ---------------------------------------------------------------------------
# grep_verdicts
# ---------------------------------------------------------------------------

def file_verdict(pack_dir, name, body):
    (pack_dir / name).write_text(body)


class TestGrepVerdicts:
    def test_planted_identifier_is_hit(self, pack):
        file_verdict(pack, "team-1_gameA.md",
                     "## Phase 4\nThis feels like d4015 from the old runs.\n")
        hits = gv.scan_verdicts(pack)
        assert ("team-1_gameA.md", "d4015",
                "This feels like d4015 from the old runs.") in hits

    def test_compliant_anchor_line_is_clean(self, pack):
        file_verdict(pack, "team-2_gameB.md",
                     "## Phase 5\n" + COMPLIANT_ANCHOR_LINE + "\n"
                     "  anchor DOWN; 5.0 = the never-cleared G1 ceiling): 3.4**\n")
        assert gv.scan_verdicts(pack) == []

    def test_r8_outside_anchor_is_hit(self, pack):
        file_verdict(pack, "team-2_gameB.md",
                     "Scores like R8 4.10 suggest X. Also I remember R8 fondly.\n")
        hits = gv.scan_verdicts(pack)
        assert any(ident == "R8" for _, ident, _ in hits)

    def test_s3_word_boundary(self, pack):
        file_verdict(pack, "team-3_gameC.md",
                     "I think this is S3 from a prior probe.\n")
        assert any(i == "S3" for _, i, _ in gv.scan_verdicts(pack))

    def test_s3_inside_longer_token_is_clean(self, pack):
        file_verdict(pack, "team-3_gameC.md",
                     "The AWS3000 board and MS365 grid have nothing here.\n")
        assert gv.scan_verdicts(pack) == []

    def test_connection_go_and_menger(self, pack):
        file_verdict(pack, "team-1_gameD.md",
                     "Reminds me of Connection Go.\nAnd of the menger family.\n")
        idents = {i for _, i, _ in gv.scan_verdicts(pack)}
        assert "Connection Go" in idents and "menger" in idents

    def test_connection_goal_vocabulary_is_clean(self, pack):
        """Regression (found on the 21 real rc2_phase_d verdicts): the
        engine helper's own status line says "connection goals:" — standard
        mechanical vocabulary must not trip the "Connection Go" identifier."""
        file_verdict(pack, "team-1_gameD.md",
                     "- Surprises: the connection goal needs only 3 stones.\n"
                     "connection goals: P1 must connect d0=0 to d0=8\n")
        assert gv.scan_verdicts(pack) == []

    def test_r8_anchor_reference_prose_is_a_hit(self, pack):
        """Registered carve-out is the VERBATIM anchor string only: prose
        anchor references like "below the R8/R19 anchors" stay hits, for
        the orchestrator to review (they are exactly what the pre-unblind
        review gate exists for)."""
        file_verdict(pack, "team-3_gameF.md",
                     "That places it below the R8/R19 anchors.\n")
        assert any(i == "R8" for _, i, _ in gv.scan_verdicts(pack))

    def test_besieged_is_clean_but_siege_hits(self, pack):
        file_verdict(pack, "team-1_gameE.md", "P2 felt besieged all game.\n")
        assert gv.scan_verdicts(pack) == []
        file_verdict(pack, "team-1_gameF.md", "like the siege campaign\n")
        assert any(i == "siege" for _, i, _ in gv.scan_verdicts(pack))

    def test_templates_not_scanned(self, pack):
        # No filed verdicts; templates contain the anchor line ("R8 4.10")
        # and must NOT be scanned.
        assert gv.scan_verdicts(pack) == []

    def test_anonymization_failure_caught_via_pack_games(self, pack):
        """Dynamic identifiers come from the pack's OWN games (not the
        mapping): a leaked provenance string in games/*.json becomes an
        identifier and is caught in filed verdicts."""
        p = pack / "games" / "A.json"
        data = json.loads(p.read_text())
        data["metadata"] = {"lineage": "elite_top_0_forgotten"}
        p.write_text(json.dumps(data))
        file_verdict(pack, "team-1_gameA.md",
                     "metadata says elite_top_0_forgotten, suspicious\n")
        assert any(i == "elite_top_0_forgotten"
                   for _, i, _ in gv.scan_verdicts(pack))

    def test_never_opens_sealed_mapping(self, pack):
        """Invariant: no code path reads .blind_mapping.json — the scan works
        identically with the mapping corrupted or deleted."""
        file_verdict(pack, "team-1_gameA.md", "clean verdict text\n")
        (pack / ".blind_mapping.json").write_text("{corrupt json !!!")
        assert gv.scan_verdicts(pack) == []
        (pack / ".blind_mapping.json").unlink()
        assert gv.scan_verdicts(pack) == []
        # and the literal filename appears nowhere in the scanner's code
        # (docstring aside): strip the docstring, then grep the source.
        src = Path(gv.__file__).read_text()
        body = src.split('"""', 2)[-1]
        assert ".blind_mapping" not in body

    def test_cli_exit_codes(self, pack):
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        script = ROOT / "experiments" / "rc2_campaign" / "grep_verdicts.py"
        interp = str(ROOT / ".venv" / "bin" / "python")
        r = subprocess.run([interp, str(script), str(pack)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stdout + r.stderr
        file_verdict(pack, "team-1_gameA.md", "surely d4015 again\n")
        r = subprocess.run([interp, str(script), str(pack)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 1
        assert "d4015" in r.stdout


# ---------------------------------------------------------------------------
# Dry run + play.py smoke
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_builds_dryrun_dir(self, tmp_path):
        out = tmp_path / "pack"
        bbp.build(out.with_name(out.name + "_dryrun"),
                  bbp.dry_run_entries(), seed=7, dry=True)
        dr = tmp_path / "pack_dryrun"
        assert dr.exists()
        assert len(list((dr / "games").glob("*.json"))) == 7

    def test_play_py_loads_packed_game(self, tmp_path):
        """play.py --rules on a packed dry-run stand-in (real GameDefV2).
        PYTHONPATH supplies the repo root because the tmp pack is not under
        evaluations/ (in real use HERE.parents[1] IS the repo root)."""
        dr = tmp_path / "smoke_dryrun"
        bbp.build(dr, bbp.dry_run_entries(), seed=7, dry=True)
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        interp = str(ROOT / ".venv" / "bin" / "python")
        r = subprocess.run([interp, str(dr / "play.py"), "--game", "A",
                            "--rules"],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "=== Game A — rules (mechanics only) ===" in r.stdout
        assert "BOARD:" in r.stdout and "ACTIONS" in r.stdout
