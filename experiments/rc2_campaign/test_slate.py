import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from experiments.rc2_campaign import build_blind_pack as bbp
from experiments.rc2_campaign.campaign_archive import CampaignElite
from experiments.rc2_campaign.slate import (
    build_slate, slate_to_pack_entries, NEAR_DUP_FLOOR,
)


# ---------------------------------------------------------------------------
# Stubs (mirrors test_campaign_archive.py's StubWin/StubGame convention,
# extended with the fields slate.py's near-dup screen actually reads:
# to_dict()'s topology fields + win_condition dict + komi fields).
# ---------------------------------------------------------------------------

class StubWin:
    def __init__(self, condition_type="connection", max_turns=100, komi_cells=0):
        self.condition_type = condition_type
        self.max_turns = max_turns
        self.komi_cells = komi_cells


class StubGame:
    def __init__(self, game_id, condition_type="connection", max_turns=100,
                 axis_size=7, num_dimensions=2, topology_type="grid", holes=None,
                 komi_p2=0.0, komi_cells=0, extra=0):
        self.game_id = game_id
        self.win_condition = StubWin(condition_type, max_turns, komi_cells)
        self.axis_size = axis_size
        self.num_dimensions = num_dimensions
        self.topology_type = topology_type
        self.holes = holes
        self.komi_p2 = komi_p2
        self.extra = extra  # a non-komi rule param; differs => real rules diff

    def to_dict(self):
        d = {
            "version": 3,
            "game_id": self.game_id,
            "num_dimensions": self.num_dimensions,
            "axis_size": self.axis_size,
            "topology_type": self.topology_type,
            "win_condition": {
                "condition_type": self.win_condition.condition_type,
                "max_turns": self.win_condition.max_turns,
                "komi_cells": self.win_condition.komi_cells,
            },
            "metadata": {"lineage": self.game_id},
            "extra": self.extra,
        }
        if self.holes is not None:
            d["holes"] = list(self.holes)
        if self.komi_p2:
            d["komi_p2"] = self.komi_p2
        return d


class StubBatch:
    def __init__(self, interaction=0.1, length=40.0):
        self._interaction = interaction
        self._length = length

    def mean_interaction(self):
        return self._interaction

    def mean_length(self):
        return self._length


def make_elite(canon, full_conv, game=None, interaction=0.1, length=40.0,
                family="connection", axis_size=7, max_turns=100, komi_p2=0.0,
                komi_cells=0, extra=0, holes=None, t1=0.3):
    if game is None:
        game = StubGame(canon, condition_type=family, max_turns=max_turns,
                         axis_size=axis_size, komi_p2=komi_p2,
                         komi_cells=komi_cells, extra=extra, holes=holes)
    return CampaignElite(
        game=game, canon=canon, cell=(family, 0, 0),
        descriptor_batch=StubBatch(interaction, length),
        t1_raw=t1, t1_floored=max(t1, 0.0), full_conv=list(full_conv),
    )


D4015 = {"game": StubGame("d4015a646ae3", condition_type="connection"),
         "label": "d4015a646ae3"}


class S3Fixture:
    """Light object interface (attrs, not dict) for the carry-in."""
    def __init__(self):
        self.game = StubGame("s3_game", condition_type="connection")
        self.canon = "S3"


S3 = S3Fixture()


# ---------------------------------------------------------------------------
# 1. top-3 by PG desc + canon tiebreak
# ---------------------------------------------------------------------------

def test_top3_selects_by_pg_desc_with_canon_tiebreak():
    alpha = make_elite("alpha", [0.9], family="territory", axis_size=1)
    beta = make_elite("beta", [0.9], family="connection", axis_size=2)
    gamma = make_elite("gamma", [0.8], family="elimination", axis_size=3)
    delta = make_elite("delta", [0.5], family="threshold", axis_size=4)
    out = build_slate([alpha, beta, gamma, delta], D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    assert [g["canon"] for g in top] == ["alpha", "beta", "gamma"]


# ---------------------------------------------------------------------------
# 2. family-cap substitution (3rd same-family candidate skipped, logged)
# ---------------------------------------------------------------------------

def test_family_cap_substitutes_third_same_family_candidate():
    a1 = make_elite("a1", [0.9], family="connection", axis_size=1)
    a2 = make_elite("a2", [0.8], family="connection", axis_size=2)
    a3 = make_elite("a3", [0.7], family="connection", axis_size=3)
    b1 = make_elite("b1", [0.6], family="territory", axis_size=4)
    out = build_slate([a1, a2, a3, b1], D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    assert [g["canon"] for g in top] == ["a1", "a2", "b1"]
    assert any("family_cap_skip" in s and "a3" in s for s in out["substitutions"])


# ---------------------------------------------------------------------------
# 3. family-cap exhaustion fallback (single-family archive -> filled, no error)
# ---------------------------------------------------------------------------

def test_family_cap_exhaustion_fills_from_single_family():
    elites = [make_elite(f"c{i}", [0.9 - i * 0.1], family="connection",
                          axis_size=10 + i)
              for i in range(5)]
    out = build_slate(elites, D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    assert [g["canon"] for g in top] == ["c0", "c1", "c2"]
    assert all(g["family"] == "connection" for g in top)
    assert any("family_cap_exhausted" in s for s in out["substitutions"])


# ---------------------------------------------------------------------------
# 4. near-dup by descriptor distance (logged skip)
# ---------------------------------------------------------------------------

def test_near_dup_descriptor_distance_skips_and_logs():
    e1 = make_elite("e1", [0.9], family="connection", axis_size=7,
                     interaction=0.10, length=40.0, max_turns=100)
    # dist over (interaction, length_frac) ~ sqrt(0.001^2 + 0.005^2) < 0.02
    e2 = make_elite("e2", [0.85], family="connection", axis_size=7,
                     interaction=0.101, length=40.5, max_turns=100)
    e3 = make_elite("e3", [0.5], family="elimination", axis_size=9)
    out = build_slate([e1, e2, e3], D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    canons = [g["canon"] for g in top]
    assert "e2" not in canons
    assert canons == ["e1", "e3"]  # e2 skipped, no 3rd rated elite left
    assert any("near_dup_skip" in s and "e2" in s for s in out["substitutions"])


# ---------------------------------------------------------------------------
# 5. near-dup by komi-only rules diff
# ---------------------------------------------------------------------------

def test_near_dup_komi_only_rules_diff_skips_and_logs():
    e1 = make_elite("e1", [0.9], family="connection", axis_size=7,
                     interaction=0.5, length=50.0, max_turns=100, komi_p2=0.0)
    # Descriptors are far apart (L2 >> floor) but the ONLY dict diff after
    # stripping komi_p2/max_turns/komi_cells/identity fields is komi + max_turns.
    e2 = make_elite("e2", [0.85], family="connection", axis_size=7,
                     interaction=0.1, length=10.0, max_turns=80, komi_p2=0.2)
    e3 = make_elite("e3", [0.5], family="elimination", axis_size=9)
    dist = ((0.5 - 0.1) ** 2 + (0.5 - 0.125) ** 2) ** 0.5
    assert dist >= NEAR_DUP_FLOOR  # sanity: not caught by the distance clause
    out = build_slate([e1, e2, e3], D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    canons = [g["canon"] for g in top]
    assert "e2" not in canons
    assert canons == ["e1", "e3"]
    assert any("near_dup_skip" in s and "e2" in s for s in out["substitutions"])


def test_rules_diff_with_real_non_komi_difference_is_not_near_dup():
    # Sanity control: a real rule difference (extra=1 vs 0) alongside a komi
    # diff must NOT be screened as near-dup -- only pure komi/max_turns diffs are.
    e1 = make_elite("e1", [0.9], family="connection", axis_size=7,
                     interaction=0.5, length=50.0, max_turns=100, komi_p2=0.0,
                     extra=0)
    e2 = make_elite("e2", [0.85], family="connection", axis_size=7,
                     interaction=0.1, length=10.0, max_turns=80, komi_p2=0.2,
                     extra=1)
    out = build_slate([e1, e2], D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    assert [g["canon"] for g in top] == ["e1", "e2"]
    assert not any("near_dup_skip" in s for s in out["substitutions"])


# ---------------------------------------------------------------------------
# 6. contrast = lowest tertile, screened against top picks
# ---------------------------------------------------------------------------

def test_contrast_is_lowest_tertile_and_screened_against_top():
    e1 = make_elite("e1", [0.9], family="territory", axis_size=7,
                     interaction=0.2, length=20.0)
    e2 = make_elite("e2", [0.8], family="connection", axis_size=8)
    e3 = make_elite("e3", [0.7], family="elimination", axis_size=9)
    e4 = make_elite("e4", [0.6], family="threshold", axis_size=10)
    e5 = make_elite("e5", [0.5], family="territory", axis_size=11)
    e6 = make_elite("e6", [0.45], family="connection", axis_size=12)
    # lowest tertile (bottom 3 of 9): e7, e8, e9
    e7 = make_elite("e7", [0.3], family="territory", axis_size=7,
                     interaction=0.2, length=20.0)  # near-dup of e1 (top pick)
    e8 = make_elite("e8", [0.25], family="elimination", axis_size=20)
    e9 = make_elite("e9", [0.1], family="threshold", axis_size=21)
    out = build_slate([e1, e2, e3, e4, e5, e6, e7, e8, e9], D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    contrast = [g for g in out["games"] if g["role"] == "contrast"]
    assert [g["canon"] for g in top] == ["e1", "e2", "e3"]
    assert [g["canon"] for g in contrast] == ["e8", "e9"]
    assert any("near_dup_skip" in s and "e7" in s for s in out["substitutions"])


def test_contrast_exhausted_extends_beyond_tertile():
    # 6 rated elites, 3 clean distinct-family top picks; the lowest tertile
    # (bottom 2 of 6) are both near-dup of top pick e1 (same family +
    # topology, descriptors within the floor) -> tertile fully screened
    # out, forcing the next-lowest extension (e4, a distinct family).
    e1 = make_elite("e1", [0.9], family="connection", axis_size=1,
                     interaction=0.5, length=50.0)
    e2 = make_elite("e2", [0.8], family="territory", axis_size=2)
    e3 = make_elite("e3", [0.7], family="elimination", axis_size=3)
    e4 = make_elite("e4", [0.4], family="threshold", axis_size=50)
    e5 = make_elite("e5", [0.3], family="connection", axis_size=1,
                     interaction=0.501, length=50.1)
    e6 = make_elite("e6", [0.2], family="connection", axis_size=1,
                     interaction=0.502, length=50.2)
    out = build_slate([e1, e2, e3, e4, e5, e6], D4015, S3)
    top = [g for g in out["games"] if g["role"] == "top"]
    contrast = [g for g in out["games"] if g["role"] == "contrast"]
    assert [g["canon"] for g in top] == ["e1", "e2", "e3"]
    assert [g["canon"] for g in contrast] == ["e4"]
    subs = out["substitutions"]
    assert any("contrast_exhausted" in s for s in subs)
    assert sum("near_dup_skip" in s for s in subs) >= 2


# ---------------------------------------------------------------------------
# 7. unrated-elite exclusion
# ---------------------------------------------------------------------------

def test_unrated_elites_excluded_and_logged():
    rated = make_elite("rated1", [0.5], family="connection", axis_size=1)
    unrated = make_elite("unrated1", [], family="territory", axis_size=2)
    out = build_slate([rated, unrated], D4015, S3)
    canons = [g["canon"] for g in out["games"]]
    assert "unrated1" not in canons
    assert any("excluded_unrated" in s and "unrated1" in s
               for s in out["substitutions"])


# ---------------------------------------------------------------------------
# 8. total = 7 with d4015 + s3 tagged
# ---------------------------------------------------------------------------

def test_total_seven_games_with_fixtures_tagged():
    elites = [make_elite(f"g{i}", [0.9 - i * 0.05], family=f,
                          axis_size=100 + i)
              for i, f in enumerate(["connection", "territory", "elimination",
                                       "threshold", "connection", "territory",
                                       "elimination", "threshold", "connection"])]
    out = build_slate(elites, D4015, S3)
    assert len(out["games"]) == 7
    roles = [g["role"] for g in out["games"]]
    assert roles.count("top") == 3
    assert roles.count("contrast") == 2
    assert roles[-2] == "validity_anchor"
    assert roles[-1] == "carry_in"
    assert out["games"][-2]["canon"] == "d4015a646ae3"
    assert out["games"][-1]["canon"] == "S3"
    assert isinstance(out["family_composition"], dict)
    assert sum(out["family_composition"].values()) == 7


# ---------------------------------------------------------------------------
# 9. substitution log grows correctly
# ---------------------------------------------------------------------------

def test_substitution_log_grows_with_each_constraint_fired():
    unrated = make_elite("u1", [], family="territory", axis_size=99)
    a1 = make_elite("a1", [0.9], family="connection", axis_size=1)
    a2 = make_elite("a2", [0.85], family="connection", axis_size=2)
    a3 = make_elite("a3", [0.8], family="connection", axis_size=3)  # cap-skipped
    b1 = make_elite("b1", [0.7], family="territory", axis_size=4)
    out = build_slate([unrated, a1, a2, a3, b1], D4015, S3)
    subs = out["substitutions"]
    assert any("excluded_unrated" in s for s in subs)
    assert any("family_cap_skip" in s for s in subs)
    assert len(subs) >= 2
    # every substitution is a plain string (as documented in the interface)
    assert all(isinstance(s, str) for s in subs)


# ---------------------------------------------------------------------------
# 10. slate -> blind-pack bridge (slate_to_pack_entries feeds validate_slate)
# ---------------------------------------------------------------------------

FIXTURE_META = {
    "validity_anchor": {"game_id": "d4015a646ae3",
                        "source": "genesis_v2_run8.db"},
    "carry_in": {"game_id": "0165399e5aef",
                 "source": "rc2_planning_gap (registered carry-in)"},
}


def _nine_elites():
    return [make_elite(f"elite{i:02d}canonhash", [0.9 - i * 0.05], family=f,
                       axis_size=100 + i)
            for i, f in enumerate(["connection", "territory", "elimination",
                                   "threshold", "connection", "territory",
                                   "elimination", "threshold", "connection"])]


def test_slate_to_pack_entries_feeds_validate_slate():
    out = build_slate(_nine_elites(), D4015, S3)
    entries = slate_to_pack_entries(out, FIXTURE_META)
    assert len(entries) == 7
    json.dumps(entries)                     # JSON-serializable end-to-end
    bbp.validate_slate(entries)             # must pass unchanged (no exit)
    elites = [e for e in entries if e["role"] in ("top", "contrast")]
    assert len(elites) == 5
    for e in elites:
        assert e["slate_id"] == e["canon"][:12]
        assert isinstance(e["cell"], list)      # M-archive cell, serialized
        assert isinstance(e["game"], dict)      # game.to_dict()
        assert "full_conv_mean_floored" in e
    anchor = next(e for e in entries if e["role"] == "validity_anchor")
    assert (anchor["game_id"], anchor["source"]) == (
        "d4015a646ae3", "genesis_v2_run8.db")
    carry = next(e for e in entries if e["role"] == "carry_in")
    assert (carry["game_id"], carry["source"]) == (
        "0165399e5aef", "rc2_planning_gap (registered carry-in)")


def test_bridged_five_top_zero_contrast_still_rejected_end_to_end():
    out = build_slate(_nine_elites(), D4015, S3)
    entries = slate_to_pack_entries(out, FIXTURE_META)
    for e in entries:
        if e["role"] == "contrast":
            e["role"] = "top"               # tamper: 5-top/0-contrast
    with pytest.raises(SystemExit):
        bbp.validate_slate(entries)
