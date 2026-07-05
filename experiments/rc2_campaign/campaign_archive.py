"""Campaign MAP-Elites archive: cells stay descriptor-based (qd_archive
verbatim), displacement key = floored T1-PG, elites carry a separate
full-conv PG ledger (prereg §3 [C9]). Guard stage runs only for genomes
that would enter (BUILD_LOG decision 4)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from evolution.qd_archive import BatchResult, validity as descriptor_validity


@dataclass
class CampaignElite:
    game: object
    canon: str
    cell: tuple
    descriptor_batch: BatchResult
    t1_raw: float
    t1_floored: float
    full_conv: list = field(default_factory=list)

    @property
    def full_conv_mean_floored(self) -> float:
        """Floor-of-POOLED full-conv PG (BUILD_LOG errata #12): pool the
        elite's checkpoint batches into one PG (mean of the raw values),
        THEN floor — §6's operative text is "mean floored full-conv PG …
        (full-conv ledger, post-final-checkpoint pooled)". nan on an
        empty ledger."""
        if not self.full_conv:
            return float("nan")
        return max(float(np.mean(self.full_conv)), 0.0)


class CampaignArchive:
    def __init__(self):
        self.cells: dict[tuple, CampaignElite] = {}
        self.seen: set[str] = set()
        self.counters: dict[str, int] = {}

    def _bump(self, key):
        self.counters[key] = self.counters.get(key, 0) + 1

    def is_seen(self, canon): return canon in self.seen
    def mark_seen(self, canon): self.seen.add(canon)

    def offer(self, game, canon, cell, descriptor_batch, t1_raw, guard_fn) -> str:
        self._bump("offered")
        reason = descriptor_validity(descriptor_batch)
        if reason is not None:
            self._bump(f"invalid_{reason}")
            return f"invalid_{reason}"
        floored = max(t1_raw, 0.0)
        incumbent = self.cells.get(cell)
        if incumbent is not None and floored <= incumbent.t1_floored:
            self._bump("lost_first_batch")
            return "lost_first_batch"
        # Would enter -> run the guard stage (decision 4).
        family = game.win_condition.condition_type
        guard = guard_fn(game, canon, family)
        if not guard["passed"]:
            g = guard["vetoes"][0]
            self._bump(f"guard_vetoed_{g}")
            return f"guard_vetoed_{g}"
        elite = CampaignElite(game=game, canon=canon, cell=cell,
                              descriptor_batch=descriptor_batch,
                              t1_raw=t1_raw, t1_floored=floored)
        self.cells[cell] = elite
        self._bump("replaced" if incumbent is not None else "filled_empty_cell")
        return "replaced" if incumbent is not None else "filled_empty_cell"

    def reeval_full_conv(self, full_conv_fn) -> None:
        """One fresh full-conv PG per elite. full_conv_fn may return None on
        EVAL_TIMEOUT/EVAL_ERROR (§2): the elite keeps its existing ledger and
        the failure is counted (the Phase C QDArchive.reeval_all contract)."""
        for cell in sorted(self.cells):
            e = self.cells[cell]
            v = full_conv_fn(e.game, e.canon)
            if v is None:
                self._bump("reeval_failed")
                continue
            e.full_conv.append(v)

    def top_elites_by_full_conv(self, k):
        rated = [e for e in self.cells.values() if e.full_conv]
        return sorted(rated, key=lambda e: e.full_conv_mean_floored, reverse=True)[:k]

    @property
    def coverage(self): return len(self.cells)

    @property
    def qd_score(self): return float(sum(e.t1_floored for e in self.cells.values()))

    def to_dict(self):
        return {"seen": sorted(self.seen), "counters": dict(self.counters),
                "cells": [{"cell": list(e.cell), "canon": e.canon,
                           "game": e.game.to_dict(),
                           "descriptor_batch": e.descriptor_batch.to_dict(),
                           "t1_raw": e.t1_raw, "t1_floored": e.t1_floored,
                           "full_conv": list(e.full_conv)}
                          for e in self.cells.values()]}

    @classmethod
    def from_dict(cls, d, game_from_dict):
        a = cls(); a.seen = set(d["seen"]); a.counters = dict(d["counters"])
        for entry in d["cells"]:
            cell = tuple(entry["cell"])
            a.cells[cell] = CampaignElite(
                game=game_from_dict(entry["game"]), canon=entry["canon"], cell=cell,
                descriptor_batch=BatchResult.from_dict(entry["descriptor_batch"]),
                t1_raw=entry["t1_raw"], t1_floored=entry["t1_floored"],
                full_conv=list(entry["full_conv"]))
        return a
