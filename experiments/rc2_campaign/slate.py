"""Slate builder (prereg §7, LOCKED). Composes the 7-game blind slate from
the M archive once BAR W ∧ BAR H pass. Pure selection logic: no engine, no
I/O beyond what the caller supplies.

Composition (§7): top-3 M-elites by full-conv PG (`full_conv_mean_floored`,
descending; ties broken lexicographically on `canon`) + 2 contrast elites
(M-archive elites from the lowest tertile of floored full-conv PG,
selected best-first within the tertile under the same near-dup screen) +
d4015 (validity anchor) + S3 (registered carry-in; reported, not binding)
= 7 games. All M-archive elites are guard-passing by construction
(campaign_archive.CampaignArchive.offer's insertion gate runs the guard
stage before an elite can occupy a cell), so no extra guard filter runs
here.

Constraints, applied in PG order with next-best substitution (every
substitution logged as a string in the returned `substitutions` list):

  1. Family cap: max 2 of the top-3 per win-condition family
     (`game.win_condition.condition_type`). If fewer than 2 families hold
     rated elites (the documented Phase C exhaustion case: elimination
     ran 0-valid in both Phase C runs), the cap is unsatisfiable — degrade
     gracefully by filling from the best remaining regardless of family
     and logging `family_cap_exhausted` once. Never errors, never returns
     fewer than 3 top picks when >= 3 rated elites exist.

  2. Near-duplicate screen (BUILD_LOG.md decision #10 — the pinned floor):
     skip candidate B against an already-selected A iff identical family
     AND identical board/topology AND (L2 distance over
     (interaction_rate, length_frac) < NEAR_DUP_FLOOR OR rules-diff
     limited to komi/max_turns fields). 0.02 is < half the smallest
     interaction bin width (0.05/2 — evolution/qd_archive.py
     INTERACTION_EDGES), so the screen only fires on descriptors within
     re-binning noise of identical. Applies within the top-3, within the
     contrast pair, and between contrast picks and the top-3 (a contrast
     game near-identical to a top game destroys the S-GO-2 contrast).

Descriptor values for the L2 clause come from each elite's
`descriptor_batch` (a `evolution.qd_archive.BatchResult`):
`mean_interaction()` for interaction_rate, and
`mean_length() / game.win_condition.max_turns` clipped to [0, 1] for
length_frac — this mirrors `qd_archive.cell_key`'s arithmetic exactly
(evolution/qd_archive.py:124-137) so the near-dup screen and the cell
binning agree on what "identical dynamics" means.

Board/topology identity compares `game.to_dict()`'s topology-defining
fields: `num_dimensions`, `axis_size`, `topology_type`, `holes` (absent
key normalises to `None`, matching `GameDefV2.to_dict()`'s convention of
omitting `holes` when it is `None` — see game_engine/game_def_v2.py:226).

The rules-diff clause compares `game.to_dict()` copies with the identity
fields `game_id`/`metadata`/`version` removed (mirrors
`GameDefV2.canonical_blob`'s own exclusion list, game_engine/
game_def_v2.py:296) plus every komi-style field found in the schema:
the top-level `komi_p2` (game_engine/game_def_v2.py:74, V6 asymmetric
scoring bonus) and, nested under `win_condition`, `max_turns` (excluded
per §7's "rules-diff limited to komi/max_turns") and `komi_cells`
(game_engine/rules.py:258, FRONTLINE integer komi — same komi family as
komi_p2, included defensively even though the FRONTLINE/contested_majority
win condition is not currently generated). Equal dicts after stripping
⇒ near-dup.
"""
from __future__ import annotations

import math

#: BUILD_LOG.md decision #10 — pinned pre-data (no campaign data existed
#: at pin time). 0.02 < half the smallest interaction bin width (0.05/2),
#: so the screen can only fire on games whose descriptors are within
#: re-binning noise of identical.
NEAR_DUP_FLOOR = 0.02

#: game.to_dict() fields that define board/topology identity
#: (game_engine/game_def_v2.py:209-232). `holes` is optional in the dict
#: (only present when not None) so it is read via .get() -> None default.
_TOPOLOGY_FIELDS = ("num_dimensions", "axis_size", "topology_type", "holes")

#: identity / lineage fields stripped before the rules-diff comparison —
#: mirrors GameDefV2.canonical_blob's own exclusion list
#: (game_engine/game_def_v2.py:296).
_IDENTITY_FIELDS = ("game_id", "metadata", "version")

#: top-level komi-style fields (outside win_condition) stripped before the
#: rules-diff comparison.
_TOP_LEVEL_KOMI_FIELDS = ("komi_p2",)

#: win_condition-nested fields stripped before the rules-diff comparison:
#: max_turns (§7's explicit "komi/max_turns") and komi_cells (the
#: FRONTLINE integer-komi analogue of komi_p2, game_engine/rules.py:258).
_WIN_CONDITION_EXCLUDED_FIELDS = ("max_turns", "komi_cells")


def _descriptor_xy(elite) -> tuple[float, float]:
    """(interaction_rate, length_frac), mirroring qd_archive.cell_key's
    arithmetic (evolution/qd_archive.py:124-137)."""
    batch = elite.descriptor_batch
    interaction = batch.mean_interaction()
    max_turns = max(1, int(elite.game.win_condition.max_turns))
    length_frac = min(1.0, max(0.0, batch.mean_length() / max_turns))
    return interaction, length_frac


def _l2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _topology_key(game_dict: dict) -> tuple:
    return tuple(game_dict.get(f) for f in _TOPOLOGY_FIELDS)


def _rules_diff_excl_komi_max_turns(game_dict_a: dict, game_dict_b: dict) -> bool:
    """True iff the two game dicts are identical once identity fields and
    every komi/max_turns field are stripped (§7's "rules-diff limited to
    komi/max_turns")."""

    def strip(d: dict) -> dict:
        d = dict(d)
        for f in _IDENTITY_FIELDS + _TOP_LEVEL_KOMI_FIELDS:
            d.pop(f, None)
        wc = dict(d.get("win_condition", {}))
        for f in _WIN_CONDITION_EXCLUDED_FIELDS:
            wc.pop(f, None)
        d["win_condition"] = wc
        return d

    return strip(game_dict_a) == strip(game_dict_b)


def _is_near_dup(candidate, selected, near_dup_floor: float) -> bool:
    """§7 near-dup screen / BUILD_LOG.md decision #10."""
    cand_family = candidate.game.win_condition.condition_type
    sel_family = selected.game.win_condition.condition_type
    if cand_family != sel_family:
        return False
    cand_dict = candidate.game.to_dict()
    sel_dict = selected.game.to_dict()
    if _topology_key(cand_dict) != _topology_key(sel_dict):
        return False
    dist = _l2(_descriptor_xy(candidate), _descriptor_xy(selected))
    if dist < near_dup_floor:
        return True
    return _rules_diff_excl_komi_max_turns(cand_dict, sel_dict)


def _any_near_dup(candidate, already_selected, near_dup_floor: float) -> bool:
    return any(_is_near_dup(candidate, sel, near_dup_floor) for sel in already_selected)


def _sort_key(elite):
    # Descending full-conv PG; ties broken lexicographically on canon (§7).
    return (-elite.full_conv_mean_floored, elite.canon)


def _select_top3(rated_sorted: list, k: int, family_cap: int, near_dup_floor: float):
    """Constraint (1) then (2), in PG order, next-best substitution."""
    substitutions: list[str] = []
    distinct_families = {e.game.win_condition.condition_type for e in rated_sorted}
    exhausted_mode = len(distinct_families) < 2
    if exhausted_mode:
        substitutions.append(
            f"family_cap_exhausted: only {len(distinct_families)} family/ies "
            f"hold rated M-elites ({sorted(distinct_families)}) — family cap "
            f"(max {family_cap}/family) cannot bind; filling top-{k} by PG "
            f"regardless of family"
        )
    chosen: list = []
    family_counts: dict[str, int] = {}
    for cand in rated_sorted:
        if len(chosen) >= k:
            break
        fam = cand.game.win_condition.condition_type
        if not exhausted_mode and family_counts.get(fam, 0) >= family_cap:
            substitutions.append(
                f"family_cap_skip: top-3 candidate {cand.canon} ({fam}) would "
                f"exceed max {family_cap}/family — next-best substituted"
            )
            continue
        if _any_near_dup(cand, chosen, near_dup_floor):
            substitutions.append(
                f"near_dup_skip: top-3 candidate {cand.canon} skipped "
                f"(near-duplicate of an already-selected top pick) — "
                f"next-best substituted"
            )
            continue
        chosen.append(cand)
        family_counts[fam] = family_counts.get(fam, 0) + 1
    return chosen, substitutions


def _lowest_tertile(rated_sorted: list) -> tuple[list, int]:
    """Lowest tertile of the rated pool by full_conv_mean_floored. Small
    archives: bottom third rounded up (ceil), so >= 6 rated elites always
    yields a tertile of size >= 2 (decision #10 / this module's design)."""
    n = len(rated_sorted)
    tertile_size = math.ceil(n / 3)
    return rated_sorted[n - tertile_size:], tertile_size


def _select_contrast(rated_sorted: list, top3: list, k: int, near_dup_floor: float):
    """Constraint (2) only (no family cap on contrast picks — §7 scopes the
    cap to the top-3). Best-first within the lowest tertile; if screening
    exhausts the tertile before k picks are found, extend outward to the
    next-lowest-PG remaining candidates (decision #10 fallback).

    Tertile size is computed against the FULL rated pool (not the pool
    remaining after top-3 removal) — this module's design, needed so the
    "archive >= 6 rated elites -> tertile >= 2" guarantee holds even when
    a top-3 pick happens to fall at the tertile boundary in a small
    archive; top-3 picks are then filtered out of both the tertile and
    the extension pool (a game cannot be both a top pick and a contrast
    pick)."""
    substitutions: list[str] = []
    top3_ids = {id(e) for e in top3}
    n = len(rated_sorted)
    tertile_full, tertile_size = _lowest_tertile(rated_sorted)
    extension_full = list(reversed(rated_sorted[: n - tertile_size]))
    tertile = [e for e in tertile_full if id(e) not in top3_ids]
    extension = [e for e in extension_full if id(e) not in top3_ids]

    chosen: list = []

    def _try_pool(pool):
        for cand in pool:
            if len(chosen) >= k:
                return
            if _any_near_dup(cand, top3 + chosen, near_dup_floor):
                substitutions.append(
                    f"near_dup_skip: contrast candidate {cand.canon} skipped "
                    f"(near-duplicate of an already-selected slate game) — "
                    f"next-best substituted"
                )
                continue
            chosen.append(cand)

    _try_pool(tertile)
    if len(chosen) < k:
        substitutions.append(
            f"contrast_exhausted: lowest tertile ({tertile_size} candidate(s)) "
            f"insufficient after near-dup screen — extending to next-lowest "
            f"remaining rated elites"
        )
        _try_pool(extension)
    return chosen, substitutions


def _fixture_entry(fixture, role: str) -> dict:
    """Wrap a pre-built registered fixture (d4015 or S3) into a slate entry.

    Minimal interface: a dict or light object exposing `game` (the
    GameDefV2, for reporting only) and optionally `label` or `canon`
    (falls back to the game's `game_id`, then to the role name). Fixtures
    are appended without constraint-checking (§7: "reported, not
    binding") — no family-cap or near-dup screen runs against them.
    """
    if isinstance(fixture, dict):
        game = fixture.get("game")
        label = fixture.get("label") or fixture.get("canon")
    else:
        game = getattr(fixture, "game", None)
        label = getattr(fixture, "label", None) or getattr(fixture, "canon", None)
    if label is None and game is not None:
        label = getattr(game, "game_id", None)
    if label is None:
        label = role
    family = None
    if game is not None:
        wc = getattr(game, "win_condition", None)
        family = getattr(wc, "condition_type", None)
    return {
        "role": role,
        "canon": label,
        "game": game,
        "family": family,
        "full_conv_mean_floored": None,
    }


def build_slate(m_elites, d4015, s3, near_dup_floor: float = NEAR_DUP_FLOOR) -> dict:
    """Compose the 7-game blind slate (prereg §7).

    Args:
        m_elites: iterable of `campaign_archive.CampaignElite` from the
            M-archive (e.g. `archive.cells.values()`).
        d4015: the validity-anchor fixture (see `_fixture_entry`).
        s3: the carry-in fixture (see `_fixture_entry`).
        near_dup_floor: L2 floor for the descriptor near-dup clause
            (decision #10; overridable for testing, defaults to the
            pinned constant).

    Returns:
        {"games": list[dict], "substitutions": list[str],
         "family_composition": dict[str, int]}
    """
    m_elites = list(m_elites)
    substitutions: list[str] = []

    rated = [e for e in m_elites if e.full_conv]
    unrated = [e for e in m_elites if not e.full_conv]
    if unrated:
        substitutions.append(
            f"excluded_unrated: {len(unrated)} M-archive elite(s) excluded "
            f"(empty full_conv ledger, unranked): "
            f"{sorted(e.canon for e in unrated)}"
        )

    rated_sorted = sorted(rated, key=_sort_key)

    top3, top3_subs = _select_top3(rated_sorted, k=3, family_cap=2,
                                    near_dup_floor=near_dup_floor)
    substitutions.extend(top3_subs)

    contrast, contrast_subs = _select_contrast(rated_sorted, top3, k=2,
                                                near_dup_floor=near_dup_floor)
    substitutions.extend(contrast_subs)

    games: list[dict] = []
    for e in top3:
        games.append({
            "role": "top",
            "canon": e.canon,
            "game": e.game,
            "family": e.game.win_condition.condition_type,
            "cell": e.cell,
            "full_conv_mean_floored": e.full_conv_mean_floored,
        })
    for e in contrast:
        games.append({
            "role": "contrast",
            "canon": e.canon,
            "game": e.game,
            "family": e.game.win_condition.condition_type,
            "cell": e.cell,
            "full_conv_mean_floored": e.full_conv_mean_floored,
        })
    games.append(_fixture_entry(d4015, role="validity_anchor"))
    games.append(_fixture_entry(s3, role="carry_in"))

    family_composition: dict[str, int] = {}
    for g in games:
        fam = g.get("family")
        if fam is None:
            continue
        family_composition[fam] = family_composition.get(fam, 0) + 1

    return {
        "games": games,
        "substitutions": substitutions,
        "family_composition": family_composition,
    }


def slate_to_pack_entries(slate_result: dict, fixture_meta: dict) -> list[dict]:
    """Bridge: `build_slate` output -> the `build_blind_pack.py --slate-json`
    entry schema (documented in build_blind_pack.py's module docstring), so
    the result passes `build_blind_pack.validate_slate` unchanged.

    Lives HERE (not in build_blind_pack) because the pack builder
    deliberately treats "game" as opaque JSON with no engine import —
    serializing the live GameDefV2 objects is the slate side's job, and
    this module already owns the production side of the slate schema.

    Args:
        slate_result: the dict returned by `build_slate`.
        fixture_meta: caller-supplied provenance for the two registered
            fixtures, keyed by role::

                {"validity_anchor": {"game_id": ..., "source": ...},
                 "carry_in":        {"game_id": ..., "source": ...}}

            Extra keys (e.g. an optional "slate_id") pass through and are
            sealed into the blind mapping.

    Returns:
        A list of 7 JSON-serializable entry dicts, slate order preserved:
        every entry carries `role` + `game` (via `game.to_dict()`); elites
        ("top"/"contrast") add `slate_id` (canon[:12]), `canon`,
        `full_conv_mean_floored`, `cell` (as a list); fixtures add the
        fixture_meta fields (`game_id`/`source` required by validate_slate).
    """
    entries: list[dict] = []
    for g in slate_result["games"]:
        role = g["role"]
        entry: dict = {"role": role, "game": g["game"].to_dict()}
        if role in ("top", "contrast"):
            entry.update(
                slate_id=g["canon"][:12],
                canon=g["canon"],
                full_conv_mean_floored=g["full_conv_mean_floored"],
                cell=list(g["cell"]),
            )
        else:
            entry.update(fixture_meta[role])
        entries.append(entry)
    return entries
