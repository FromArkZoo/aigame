"""TacticalAgent — WIN-IN-1 / BLOCK-WIN-IN-1 / densify agent (RC2 descriptor v2).

Implements the locked Design section of
experiments/rc2_descriptor_v2/PREREGISTRATION.md. training/ is untouched;
the densify heuristic is reimplemented locally (not imported from
training.utils) per the build contract.

Decision order per ply (select_action):
  0. PIE: when the pie swap is offered (swap action present in
     legal_actions), always swap — GreedyAgent precedent, prereg "Pie rule"
     line. Checked before the scans; the swap action is excluded from all
     scans (the engine skips the win check on the swap path, so it can
     never be a winning action).
  1. WIN-IN-1: exhaustive scan of legal actions via cloned-engine step;
     play the first action after which the clone reports
     done && _winner == self.player_num. When len(legal_actions) <= 512
     (SCAN_LIMIT) the scan covers ALL legal actions except the pie swap —
     placements, pass AND move actions (a win via move or via post-pass CA
     evolution counts; prereg "scan all legal when <= 512"). When
     len(legal_actions) > 512: top-64 (HEURISTIC_TOP_K) placement actions
     by densify score, ties broken by ascending action index
     (deterministic).
  2. BLOCK-WIN-IN-1: same scan from the opponent's seat on the current
     position, over the opponent's legal PLACEMENT actions (prereg: "if
     the opponent has winning placements"); if any opponent placement wins
     for the opponent, play into one of those cells if it is legal for us
     (seeded random choice among the legal ones), else fall through.
  3. DENSIFY: GreedyAgent's (friendly_adj - enemy_adj) placement heuristic,
     reimplemented locally, seeded tie-breaks. Restricted to
     placements + pass (build contract): if no placement is legal, pass;
     if even pass is unavailable, seeded choice among legal actions.

BLOCK-WIN-IN-1 implementation (documented per the build contract):
  GameEngineV2 has no "force the other seat to act" API, but step() is
  trust-the-caller: it executes the submitted action for whoever
  engine.current_player is. The engine therefore DOES permit constructing
  the forced opponent action exactly — no win-condition-delta approximation
  was needed. Concretely: restore the scratch clone to a full snapshot of
  the live position, overwrite scratch.current_player with the opponent's
  seat (and zero scratch.placements_this_turn, which only affects
  turn-advancement bookkeeping, never win detection), then
  scratch.step(cell). The opponent wins-in-1 at that cell iff the stepped
  clone reports done && _winner == opponent seat. Captures, propagation,
  CA evolution and the engine's own win check all run inside the clone, so
  the test is the engine's ground truth, not a reimplementation.
  Known approximations (pre-declared): (a) in multi_place games the scan
  asks whether ONE opponent placement wins immediately — the engine checks
  wins after every placement of a multi-place turn, so this is exactly the
  S1-style first-strike threat; multi-placement combinations are out of
  scope (prereg honesty note). (b) opponent wins via pass (CA evolution)
  or via move actions are not blocked — the block scan is placement-only
  per the prereg.

Clone strategy (measured 2026-06-11 on this machine, per the build
contract, on s_flip_r2 — 484-cell hex_rhombus field game — at a greedy-
played ply-40 position):
  copy.deepcopy(engine)               ~1.27 ms  (deep-copies topo's
                                                 precomputed neighbor lists
                                                 and the cached GameDefV2)
  re-create + replay 40 actions       ~15.4 ms  (re-runs capture/field
                                                 machinery for every ply;
                                                 grows with game length)
  scratch engine + full-state restore ~0.003 ms (used)
deepcopy is the faster of the two named strategies, so the deepcopy FAMILY
(state copy, not history replay) was chosen; it is implemented as a
create-once scratch engine (sharing the immutable game/topology objects,
which is what makes deepcopy slow) plus a full snapshot/restore of every
mutable engine field — semantically a clone, verified state-identical to
copy.deepcopy + step in test_rc2_descriptor_v2.py, and ~450x faster, which
is what makes the <=512-candidate exhaustive scans affordable (the
clone-step cost is then the engine step itself, ~0.5 ms on s_flip_r2).
The live engine is never mutated by the scans (also covered by a test).
"""
from __future__ import annotations

import random

from game_engine.factory import create_engine

# Prereg Design: "scan all legal when <= 512, else top-64 by heuristic".
SCAN_LIMIT = 512
HEURISTIC_TOP_K = 64

# Every mutable scalar attribute of GameEngineV2 (engine_v2.py __init__ /
# reset). Arrays/lists/sets are handled explicitly in snapshot/restore.
# game / topo / total_cells / _needs_ko are immutable per engine instance.
_SCALAR_FIELDS = (
    "current_player",
    "step_count",
    "done",
    "placements_this_turn",
    "consecutive_passes",
    "_winner",
    "_field_dirty",
    "_ended_by_max_turns",
    "_ended_by_no_moves",
    "_quota_ticks",
    "_pie_resolved",
    "_pie_used",
    "_goals_swapped",
    "_replace_prev_owner",
    "_replace_lockout_cell",
    "_replace_lockout_step",
)


def snapshot_engine(engine) -> dict:
    """Copy every mutable field of a GameEngineV2 into a snapshot dict."""
    snap = {name: getattr(engine, name) for name in _SCALAR_FIELDS}
    snap["board_owners"] = engine.board_owners.copy()
    snap["board_values"] = engine.board_values.copy()
    snap["_last_rewards"] = engine._last_rewards.copy()
    snap["piece_counts"] = list(engine.piece_counts)
    snap["_position_history"] = frozenset(engine._position_history)
    snap["_quota_cells"] = frozenset(engine._quota_cells)
    return snap


def restore_engine(engine, snap: dict) -> None:
    """Restore a GameEngineV2 to a snapshot taken by snapshot_engine.

    The engine must have been built from the same GameDefV2 (same board
    geometry); arrays are written in place.
    """
    for name in _SCALAR_FIELDS:
        setattr(engine, name, snap[name])
    engine.board_owners[:] = snap["board_owners"]
    engine.board_values[:] = snap["board_values"]
    engine._last_rewards[:] = snap["_last_rewards"]
    engine.piece_counts = list(snap["piece_counts"])
    engine._position_history = set(snap["_position_history"])
    engine._quota_cells = set(snap["_quota_cells"])


class TacticalAgent:
    """WIN-IN-1 -> BLOCK-WIN-IN-1 -> densify agent (prereg Design section).

    Constructor and select_action signatures match training.utils.
    GreedyAgent (engine positional, player_num/seed keyword-friendly;
    select_action(obs, legal_actions, deterministic) -> (action, 0.0, 0.0))
    so rollout harnesses can treat them interchangeably.
    """

    def __init__(self, engine, player_num: int, seed: int | None = None):
        self.engine = engine
        self.player_num = player_num  # 1 or 2 (concrete seat id)
        self.rng = random.Random(seed)
        self._scratch = None  # lazily built clone target (shares game/topo)

    # ------------------------------------------------------------------
    # Clone machinery
    # ------------------------------------------------------------------

    def _scratch_engine(self):
        if self._scratch is None:
            self._scratch = create_engine(self.engine.game)
            self._scratch.reset()
        return self._scratch

    def _wins_after(self, scratch, snap: dict, action: int, seat: int,
                    force_seat: bool) -> bool:
        """Does *seat* win immediately by playing *action* from *snap*?

        Restores the scratch clone to the live position and steps it; the
        live engine is never touched. force_seat=True overrides
        current_player (BLOCK-WIN-IN-1's forced opponent action — see
        module docstring).
        """
        restore_engine(scratch, snap)
        if force_seat:
            scratch.current_player = seat
            scratch.placements_this_turn = 0
        scratch.step(action)
        return scratch.done and scratch._winner == seat

    # ------------------------------------------------------------------
    # Densify heuristic (GreedyAgent's scoring, reimplemented locally)
    # ------------------------------------------------------------------

    def _densify_scores(self, placements: list[int],
                        player: int) -> list[int]:
        """(friendly_adj - enemy_adj) per candidate cell, for *player*."""
        board = self.engine.board_owners
        topo = self.engine.topo
        scores: list[int] = []
        for cell in placements:
            friendly = 0
            enemy = 0
            for nbr in topo.get_neighbors(cell):
                owner = int(board[nbr])
                if owner == player:
                    friendly += 1
                elif owner != 0:
                    enemy += 1
            scores.append(friendly - enemy)
        return scores

    def _top_k_placements(self, placements: list[int], player: int) -> list[int]:
        """Top HEURISTIC_TOP_K placements by densify score (ties: ascending
        action index — deterministic, no rng draw)."""
        scores = self._densify_scores(placements, player)
        ranked = sorted(zip(placements, scores), key=lambda t: (-t[1], t[0]))
        return [a for a, _ in ranked[:HEURISTIC_TOP_K]]

    def _win_scan_candidates(self, legal_actions: list[int],
                             player: int) -> list[int]:
        """WIN-IN-1 scan set per the prereg sizing rule.

        <= SCAN_LIMIT legal: every legal action except the pie swap
        (placements + pass + moves). Otherwise: top HEURISTIC_TOP_K
        placements by densify score.
        """
        swap_idx = (self.engine.game.swap_action_idx
                    if self.engine.game.pie_rule else None)
        if len(legal_actions) <= SCAN_LIMIT:
            return [a for a in legal_actions if a != swap_idx]
        placements = [a for a in legal_actions
                      if a < self.engine.total_cells]
        return self._top_k_placements(placements, player)

    # ------------------------------------------------------------------
    # Policy
    # ------------------------------------------------------------------

    def select_action(
        self,
        obs,
        legal_actions: list[int] | None = None,
        deterministic: bool = False,
    ) -> tuple[int, float, float]:
        if legal_actions is None or len(legal_actions) == 0:
            raise ValueError("TacticalAgent requires at least one legal action.")
        engine = self.engine
        game = engine.game

        # 0. Pie rule: always swap when offered (prereg; GreedyAgent
        # precedent). Takes precedence over the scans.
        if game.pie_rule:
            swap_idx = game.swap_action_idx
            if swap_idx in legal_actions:
                return swap_idx, 0.0, 0.0

        assert engine.current_player == self.player_num, (
            f"TacticalAgent(player_num={self.player_num}) asked to act on "
            f"player {engine.current_player}'s turn"
        )

        scratch = self._scratch_engine()
        snap = snapshot_engine(engine)
        me = self.player_num

        # 1. WIN-IN-1: play the first immediately winning action.
        for action in self._win_scan_candidates(legal_actions, me):
            if self._wins_after(scratch, snap, action, me, force_seat=False):
                return action, 0.0, 0.0

        # 2. BLOCK-WIN-IN-1: scan the opponent's legal placements on the
        # current position from their seat (forced action on the clone).
        opp = 3 - me
        opp_legal = engine.get_legal_actions(player=opp)
        opp_places = [a for a in opp_legal if a < engine.total_cells]
        if len(opp_legal) > SCAN_LIMIT:
            opp_places = self._top_k_placements(opp_places, opp)
        winning_cells = [
            c for c in opp_places
            if self._wins_after(scratch, snap, c, opp, force_seat=True)
        ]
        if winning_cells:
            my_places = {a for a in legal_actions if a < engine.total_cells}
            playable = [c for c in winning_cells if c in my_places]
            if playable:
                return self.rng.choice(playable), 0.0, 0.0
            # No legal block -> fall through to densify (prereg).

        # 3. Densify fallback (placements + pass only, per build contract).
        placements = [a for a in legal_actions if a < engine.total_cells]
        if placements:
            scores = self._densify_scores(placements, me)
            best = max(scores)
            best_actions = [a for a, s in zip(placements, scores)
                            if s == best]
            return self.rng.choice(best_actions), 0.0, 0.0
        if engine.total_cells in legal_actions:
            return engine.total_cells, 0.0, 0.0  # pass
        return self.rng.choice(list(legal_actions)), 0.0, 0.0
