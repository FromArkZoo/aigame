"""MAP-Elites archive over the generator's genome space (RC2 Phase C).

Pure bookkeeping + decision logic — the archive never touches the engine.
Rollout batches are supplied by the caller through an ``evaluate_batch``
callback, so the registered seeding scheme (content-derived eval seeds,
batch_index counting every batch a genome has ever received) lives in the
runner and the archive stays deterministic and unit-testable.

Registered mechanics (experiments/rc2_archive/PREREGISTRATION.md, locked):
  - Cell key (family, interaction_bin, length_bin); 4 x 5 x 5 = 100 cells.
  - Quality = obs_drama pooled over all batches, weighted by each batch's
    non-draw count (equivalently: the mean over all non-draw per-rollout
    dramas the genome has ever received).
  - Insertion validity guard: non-draw rollouts >= 50% of the CANDIDATE
    batch AND mean game_length >= 6 AND obs_drama not nan.
  - Challenger eval-count matching: a challenger whose first-batch mean
    beats the incumbent's pooled mean is topped up in batches until its
    pooled rollout count >= the incumbent's; replacement iff its pooled
    mean still wins.
  - Periodic full-archive re-eval: every elite gets one fresh batch;
    stored values become the new pooled means. Re-eval never evicts.
  - Cell assignment is pinned at the candidate batch (batch 0): re-eval
    re-prices quality but never re-bins (deep-grid convention; a re-binned
    archive would let noise migrate elites between cells).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

INTERACTION_EDGES = (0.0, 0.05, 0.12, 0.20, 0.30, 1.0)
LENGTH_EDGES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
FAMILIES = ("territory", "elimination", "connection", "threshold")

#: Insertion validity guard constants (registered).
MIN_NONDRAW_FRACTION = 0.5
MIN_MEAN_GAME_LENGTH = 6.0


def bin_index(value: float, edges: tuple[float, ...]) -> int:
    """Bin of *value* under *edges*; clamps below/above into the end bins
    (registered: values > 1.0 clamp into the top bin; the last bin is
    upper-inclusive)."""
    for i in range(len(edges) - 1):
        if value < edges[i + 1]:
            return i
    return len(edges) - 2


@dataclass
class BatchResult:
    """One rollout batch's descriptor values for one genome.

    ``dramas`` holds per-rollout winner-behindness for NON-DRAW rollouts
    only (draws are skipped and counted, the Phase A convention).
    """
    batch_n: int                      # rollouts requested
    dramas: list[float]               # per-rollout drama, non-draw only
    draws: int                        # winner-None rollouts
    interactions: list[float]         # per-rollout interaction_rate
    lengths: list[float]              # per-rollout game_length (steps)

    def mean_drama(self) -> float:
        return float(np.mean(self.dramas)) if self.dramas else float("nan")

    def mean_interaction(self) -> float:
        return float(np.mean(self.interactions)) if self.interactions else 0.0

    def mean_length(self) -> float:
        return float(np.mean(self.lengths)) if self.lengths else 0.0

    def to_dict(self) -> dict:
        return {
            "batch_n": self.batch_n,
            "dramas": [float(d) for d in self.dramas],
            "draws": self.draws,
            "interactions": [float(x) for x in self.interactions],
            "lengths": [float(x) for x in self.lengths],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BatchResult":
        return cls(
            batch_n=d["batch_n"],
            dramas=list(d["dramas"]),
            draws=d["draws"],
            interactions=list(d["interactions"]),
            lengths=list(d["lengths"]),
        )


@dataclass
class Elite:
    game: object                      # GameDefV2
    canon: str                        # canonical_hash() (content hash)
    cell: tuple[str, int, int]
    batches: list[BatchResult] = field(default_factory=list)

    @property
    def pooled_dramas(self) -> list[float]:
        return [d for b in self.batches for d in b.dramas]

    @property
    def pooled_drama(self) -> float:
        pooled = self.pooled_dramas
        return float(np.mean(pooled)) if pooled else float("nan")

    @property
    def pooled_n(self) -> int:
        """Total rollouts received (the eval-count-matching unit)."""
        return sum(b.batch_n for b in self.batches)

    @property
    def next_batch_index(self) -> int:
        return len(self.batches)


#: evaluate_batch(game, batch_index, batch_n) -> BatchResult
EvaluateFn = Callable[[object, int, int], "BatchResult"]


def cell_key(game, batch0: BatchResult) -> tuple[str, int, int]:
    """Cell from the CANDIDATE batch (registered pinning).

    normalized length = mean game_length / win_condition.max_turns,
    clipped to [0, 1].
    """
    family = game.win_condition.condition_type
    max_turns = max(1, int(game.win_condition.max_turns))
    length_frac = min(1.0, max(0.0, batch0.mean_length() / max_turns))
    return (
        family,
        bin_index(batch0.mean_interaction(), INTERACTION_EDGES),
        bin_index(length_frac, LENGTH_EDGES),
    )


def validity(batch0: BatchResult) -> Optional[str]:
    """None if the candidate batch passes the registered guard, else the
    rejection reason."""
    if len(batch0.dramas) < 0.5 * batch0.batch_n:
        return "draw_majority"
    if batch0.mean_length() < MIN_MEAN_GAME_LENGTH:
        return "too_short"
    if not batch0.dramas:
        return "drama_nan"
    return None


class QDArchive:
    """One arm's archive. Both arms run identical mechanics; only the
    genome SOURCE differs (registered)."""

    def __init__(self, batch_n: int = 50) -> None:
        self.batch_n = batch_n
        self.cells: dict[tuple[str, int, int], Elite] = {}
        # Content hashes of every genome this arm has EVALUATED (consumed
        # budget). Pre-eval dedup checks against this set.
        self.seen: set[str] = set()
        self.counters: dict[str, int] = {
            "offered": 0,
            "filled_empty_cell": 0,
            "replaced": 0,
            "lost_first_batch": 0,
            "lost_after_matching": 0,
            "invalid_draw_majority": 0,
            "invalid_too_short": 0,
            "invalid_drama_nan": 0,
            "topup_rollouts": 0,
            "topup_failed": 0,
            "reeval_rollouts": 0,
            "reeval_failed": 0,
        }

    # -- dedup ---------------------------------------------------------

    def is_seen(self, canon: str) -> bool:
        return canon in self.seen

    def mark_seen(self, canon: str) -> None:
        self.seen.add(canon)

    # -- insertion -----------------------------------------------------

    def offer(self, game, canon: str, batch0: BatchResult,
              evaluate_batch: EvaluateFn) -> str:
        """Offer an evaluated candidate; returns the outcome string.

        The caller must have marked the genome seen (it consumed budget)
        BEFORE calling offer, including for candidates that turn out
        invalid.
        """
        self.counters["offered"] += 1

        reason = validity(batch0)
        if reason is not None:
            self.counters[f"invalid_{reason}"] += 1
            return f"invalid_{reason}"

        cell = cell_key(game, batch0)
        challenger = Elite(game=game, canon=canon, cell=cell,
                           batches=[batch0])
        incumbent = self.cells.get(cell)
        if incumbent is None:
            self.cells[cell] = challenger
            self.counters["filled_empty_cell"] += 1
            return "filled_empty_cell"

        if challenger.pooled_drama <= incumbent.pooled_drama:
            self.counters["lost_first_batch"] += 1
            return "lost_first_batch"

        # Challenger eval-count matching (registered): top up in batches
        # until the challenger's pooled rollout count matches or exceeds
        # the incumbent's, then compare pooled means. evaluate_batch may
        # return None (timeout/engine error); the challenge is then
        # abandoned and the incumbent stays — a failed challenger never
        # displaces a measured elite.
        while challenger.pooled_n < incumbent.pooled_n:
            batch = evaluate_batch(game, challenger.next_batch_index,
                                   self.batch_n)
            if batch is None:
                self.counters["topup_failed"] += 1
                return "lost_topup_error"
            challenger.batches.append(batch)
            self.counters["topup_rollouts"] += batch.batch_n

        if challenger.pooled_drama > incumbent.pooled_drama:
            self.cells[cell] = challenger
            self.counters["replaced"] += 1
            return "replaced"
        self.counters["lost_after_matching"] += 1
        return "lost_after_matching"

    # -- re-eval -------------------------------------------------------

    def reeval_all(self, evaluate_batch: EvaluateFn) -> list[dict]:
        """One fresh batch for every elite; never evicts (registered).

        Returns per-elite re-pricing records (the phantom diagnostic).
        """
        records = []
        # Each genome's seed stream is pinned by (canonical_hash,
        # batch_index), so iteration order cannot affect any result;
        # sorting is purely for stable logs.
        for cell in sorted(self.cells):
            elite = self.cells[cell]
            before = elite.pooled_drama
            batch = evaluate_batch(elite.game, elite.next_batch_index,
                                   self.batch_n)
            if batch is None:
                self.counters["reeval_failed"] += 1
                records.append({
                    "cell": cell, "canon": elite.canon,
                    "pooled_before": before, "fresh_batch": None,
                    "pooled_after": before,
                })
                continue
            elite.batches.append(batch)
            self.counters["reeval_rollouts"] += batch.batch_n
            records.append({
                "cell": cell,
                "canon": elite.canon,
                "pooled_before": before,
                "fresh_batch": batch.mean_drama(),
                "pooled_after": elite.pooled_drama,
            })
        return records

    # -- reporting -----------------------------------------------------

    @property
    def coverage(self) -> int:
        return len(self.cells)

    @property
    def qd_score(self) -> float:
        return float(sum(e.pooled_drama for e in self.cells.values()))

    def top_elites(self, k: int) -> list[Elite]:
        return sorted(self.cells.values(),
                      key=lambda e: e.pooled_drama, reverse=True)[:k]

    # -- persistence ---------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "batch_n": self.batch_n,
            "seen": sorted(self.seen),
            "counters": dict(self.counters),
            "cells": [
                {
                    "cell": list(e.cell),
                    "canon": e.canon,
                    "game": e.game.to_dict(),
                    "batches": [b.to_dict() for b in e.batches],
                }
                for e in self.cells.values()
            ],
        }

    @classmethod
    def from_dict(cls, d: dict, game_from_dict) -> "QDArchive":
        arch = cls(batch_n=d["batch_n"])
        arch.seen = set(d["seen"])
        arch.counters.update(d["counters"])
        for entry in d["cells"]:
            cell = tuple(entry["cell"])
            arch.cells[cell] = Elite(
                game=game_from_dict(entry["game"]),
                canon=entry["canon"],
                cell=cell,
                batches=[BatchResult.from_dict(b) for b in entry["batches"]],
            )
        return arch
