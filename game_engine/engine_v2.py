"""V2 game execution engine for topological board games.

Replaces the V1 GameEngine (which evaluated expression trees) with a new
engine that executes games on n-dimensional topological spaces using
structured rules (placement, capture, propagation, win condition, turn
structure).
"""

from __future__ import annotations

import copy
from typing import Optional

import numpy as np

from game_engine.topology import TopologicalSpace
from game_engine.game_def_v2 import GameDefV2
from game_engine.rules import FIELD_CAPTURE_TYPES


# ----------------------------------------------------------------------
# Memoized influence kernels.
#
# A stone's influence kernel (which cells it reaches and with what
# weight) depends only on the board geometry and the propagation
# parameters — never on board state — so kernels are built once per
# unique configuration and shared process-wide. Engines are created per
# episode; without this cache every kernel application pays an
# O(total_cells) Python distance() scan, and field_flip games (which
# call _recompute_field at least twice per placement) measured at
# ~9.3 s/game on the 484-cell board vs an ~81 ms baseline.
#
# Key note: the "holes" topology takes its hole-set as free data, so the
# key includes topo._holes (None for every other topology type) — two
# games with identical scalars but different hole layouts must not
# share kernels.
# ----------------------------------------------------------------------
_KERNEL_CACHE: dict[tuple, list[tuple[np.ndarray, np.ndarray]]] = {}

# SIEGE anti-cascade-burst cap (prereg-locked): at most this many new distinct
# Maker cells can tick the quota counter per Breaker move.
QUOTA_TICK_CAP_PER_MOVE = 2

# FRONTLINE lead tolerance (prereg-locked). Kernel weights are dyadic
# (1.0/0.5/0.25) so field sums are float-exact; this only adjudicates
# genuinely tied cells (R17 ULP lesson kept for form).
CM_LEAD_TOL = 1e-9


def _influence_kernels(
    topo: TopologicalSpace, radius: int, strength: float, decay: float,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Per-cell ``(target_indices, weights)`` kernel pairs for *topo*.

    ``weights[i] = strength * decay ** distance(cell, targets[i])`` —
    exactly the terms the naive per-cell loop added, in the same target
    order, so applying a kernel with one vectorized ``+=`` is
    bit-identical to the loop (each target cell is visited exactly once
    per kernel application, and the fancy-index add performs the same
    single float64 addition per cell).
    """
    key = (
        topo.topology_type,
        topo.num_dimensions,
        topo.axis_size,
        radius,
        strength,
        decay,
        topo._holes,
    )
    kernels = _KERNEL_CACHE.get(key)
    if kernels is None:
        kernels = []
        for cell in range(topo.total_cells):
            targets = topo.cells_within_radius(cell, radius)
            idx = np.array(targets, dtype=np.intp)
            w = np.array(
                [strength * (decay ** topo.distance(cell, c)) for c in targets],
                dtype=np.float64,
            )
            kernels.append((idx, w))
        _KERNEL_CACHE[key] = kernels
    return kernels


class GameEngineV2:
    """Executes a V2 game defined by a GameDefV2 on a TopologicalSpace.

    The engine maintains the full board state and enforces all rules.
    Players are internally numbered 1 and 2; the external interface
    (get_current_player, rewards array) uses 0-indexed player ids.
    """

    def __init__(self, game: GameDefV2) -> None:
        self.game = game
        self.topo: TopologicalSpace = game.get_topology()
        self.total_cells: int = game.total_cells

        # Phase-1.5 field mechanics are alternating-only: step_simultaneous
        # never honors _field_dirty, so a simultaneous game with a field
        # win condition or field capture would double-add kernels into the
        # win-check field and leak the dirty flag. No generated game uses
        # the combination — reject it before it can reach a running engine.
        if game.turn_structure.turn_type == "simultaneous" and (
            game.win_condition.condition_type == "field_connection"
            or game.capture_rule.capture_type in FIELD_CAPTURE_TYPES
        ):
            raise ValueError(
                "simultaneous turn structure does not support "
                "field_connection wins or field captures "
                f"(capture_type={game.capture_rule.capture_type!r}): "
                "step_simultaneous does not honor the _field_dirty "
                "recompute gate"
            )

        # Phase-1.5 C3 (field_replace) supports only the configuration its
        # bookkeeping was built for. Outside it the mechanic breaks
        # silently: _handle_movement never stashes _replace_prev_owner (a
        # later non-capturing move would read the stale stash and lock an
        # innocent cell), multi_place makes the ply-indexed lockout expire
        # mid-turn, target != "empty" leaves the locked cell legal via the
        # base candidate list (and double-counts controlled enemy cells),
        # and CA games skip _apply_captures so no lockout/recompute ever
        # runs while the legality extension still fires.
        if game.capture_rule.capture_type == "field_replace" and (
            game.action_rule.has_move()
            or game.turn_structure.turn_type == "multi_place"
            or game.placement_rule.target != "empty"
            or game.uses_ca
        ):
            raise ValueError(
                "field_replace requires place-only, single-placement, "
                "target='empty', non-CA games: _replace_prev_owner is "
                "stashed only by _handle_placement and the recapture "
                "lockout is ply-indexed"
            )

        # Phase-1.5 C2 (not_enemy_controlled) reads board_values for
        # legality and force-ends stranded movers via a placement-only
        # scan. Outside its spec §4 envelope the gate breaks silently:
        # CA games and non-influence propagation never write
        # board_values (the gate degrades to "anywhere"); legacy
        # captures leave ghost influence load-bearing for legality (the
        # field recompute gate does not fire for them); move actions
        # drift the field (the from-cell kernel is never removed) and a
        # mover with moves-but-no-placements would be wrongly
        # force-ended; and step_simultaneous never runs the stranded
        # check at all.
        if game.placement_rule.constraint == "not_enemy_controlled" and (
            game.capture_rule.capture_type != "none"
            or game.propagation_rule.prop_type != "influence"
            or game.action_rule.has_move()
            or game.turn_structure.turn_type != "alternating"
            or game.uses_ca
        ):
            raise ValueError(
                "not_enemy_controlled requires capture='none', influence "
                "propagation, place-only, alternating, non-CA games: the "
                "gate reads board_values (zero/stale otherwise) and the "
                "stranded check only considers placements"
            )

        # FRONTLINE (contested_majority) supports alternating turns only:
        # _handle_placement_simultaneous does not track _placements_made,
        # so a simultaneous CM game would silently downgrade every
        # decisive resolution to a draw via the participation clause.
        if (
            game.win_condition.condition_type == "contested_majority"
            and game.turn_structure.turn_type != "alternating"
        ):
            raise ValueError(
                "contested_majority requires alternating turn structure: "
                "only _handle_placement tracks _placements_made, so the "
                "participation clause would void every decisive resolution"
            )
        # FRONTLINE: end_margin must be >= 1. An unset end_margin (0)
        # would make `lead >= 0` true on an empty board and hand P1 a
        # score_margin win at the first odd check past min_turns. The
        # related komi-phantom hazard (|komi_cells| >= end_margin lets a
        # zero-placement player win via the early-end path, which has no
        # participation clause) is enforced at HARNESS level (|komi| <
        # end_margin in the calibration ladder), not here.
        if (
            game.win_condition.condition_type == "contested_majority"
            and game.win_condition.end_margin < 1
        ):
            raise ValueError(
                "contested_majority requires end_margin >= 1: end_margin=0 "
                "makes the empty board a qualifying P1 lead and hands P1 a "
                "score_margin win at the first odd check past min_turns"
            )

        # Board state
        self.board_owners: np.ndarray = np.zeros(self.total_cells, dtype=np.int8)
        self.board_values: np.ndarray = np.zeros(self.total_cells, dtype=np.float64)
        self._field_dirty: bool = False  # set by _remove_group; triggers recompute
        # Observability: True iff the game ended via _end_by_max_turns
        # (timeout tiebreak), as opposed to a win condition firing. Lets
        # experiment classifiers distinguish a win landing exactly on the
        # final step from a timeout. Pure observability — no behavior change.
        self._ended_by_max_turns: bool = False
        # Diagnostics only: True iff the game ended because the mover had
        # no legal placement (phase-1.5 C2 stranded end). Such ends ALSO
        # set _ended_by_max_turns (the pre-registered metric keys off it);
        # this flag just disambiguates stranded ends from real timeouts.
        self._ended_by_no_moves: bool = False

        # SIEGE quota accounting (inert unless condition_type_p2 == "capture_quota")
        # Distinct Maker cells that Breaker has ever flipped (a cell in this set
        # never ticks again — kills flip-tennis); total ticks so far this game.
        self._quota_ticks: int = 0
        self._quota_cells: set[int] = set()

        # FRONTLINE contested_majority state (updated in all families;
        # read only by contested_majority resolution):
        # leader-signed early-end streak (+k = P1 qualified at k consecutive
        # ply-checks, -k = P2); per-player placement counts (participation
        # clause §3.7); end-cause observability flags.
        self._cm_streak: int = 0
        self._placements_made: list[int] = [0, 0]
        self._ended_by_score_margin: bool = False
        self._ended_by_double_pass: bool = False
        # Lazily-built active-cell index array for contested_scores. The
        # topology never changes across resets, so this is deliberately
        # NOT cleared in reset() — built once on first use.
        self._cm_active_idx: Optional[np.ndarray] = None

        # Game progression
        self.current_player: int = 1  # 1 or 2
        self.step_count: int = 0
        self.done: bool = False
        self.piece_counts: list[int] = [0, 0]  # index 0 = player 1, index 1 = player 2
        self.placements_this_turn: int = 0
        self.consecutive_passes: int = 0

        # Result tracking
        self._winner: Optional[int] = None  # 1, 2, or None
        self._last_rewards: np.ndarray = np.zeros(2, dtype=np.float64)

        # Super-ko tracking (only for games where position repetition is possible)
        self._needs_ko: bool = game.needs_ko_rule
        self._position_history: set[int] = set()

        # Phase-1.5 C3 (field_replace): one-turn recapture lockout + the
        # previous owner of the last-placed cell (set by _handle_placement,
        # consumed by _capture_field_replace).
        self._replace_prev_owner: int = 0
        self._replace_lockout_cell: int = -1
        self._replace_lockout_step: int = -1

        # Pie rule state (R20+). _pie_resolved becomes True after P2's first
        # action (regardless of whether they swapped or played normally), so
        # the swap option is offered exactly once. _pie_used records whether
        # the swap was actually exercised — surfaced via info() for diagnostics
        # and human-eval helpers.
        # _goals_swapped: when True, asymmetric-goal win conditions (currently
        # only `connection`) read their per-player target dimensions swapped.
        # Set by _handle_pie_swap so the swapper inherits the original P1's
        # goal alongside the original P1's stone — matching Hex pie semantics.
        # Symmetric-goal wins (territory/threshold/elimination/majority) are
        # unaffected by this flag.
        self._pie_resolved: bool = not game.pie_rule
        self._pie_used: bool = False
        self._goals_swapped: bool = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def reset(self, *, rng=None) -> np.ndarray:
        """Reset the game to its initial state and return the observation."""
        self.board_owners[:] = 0
        self.board_values[:] = 0.0
        self._field_dirty = False
        self._ended_by_max_turns = False
        self._ended_by_no_moves = False
        self.current_player = 1
        self.step_count = 0
        self.done = False
        self.piece_counts = [0, 0]
        self.placements_this_turn = 0
        self.consecutive_passes = 0
        self._winner = None
        self._last_rewards = np.zeros(2, dtype=np.float64)

        # Reset phase-1.5 C3 (field_replace) state
        self._replace_prev_owner = 0
        self._replace_lockout_cell = -1
        self._replace_lockout_step = -1

        # Reset SIEGE quota accounting
        self._quota_ticks = 0
        self._quota_cells = set()

        # Reset FRONTLINE contested_majority state
        self._cm_streak = 0
        self._placements_made = [0, 0]
        self._ended_by_score_margin = False
        self._ended_by_double_pass = False

        # Reset pie state
        self._pie_resolved = not self.game.pie_rule
        self._pie_used = False
        self._goals_swapped = False

        # Reset ko tracking
        self._position_history = set()
        if self._needs_ko:
            self._position_history.add(self._board_hash())

        return self._observe()

    def step(self, action: int) -> tuple[np.ndarray, np.ndarray, bool, dict]:
        """Execute one action and return (observation, rewards, done, info).

        Parameters
        ----------
        action : int
            Cell index (0..total_cells-1) for placement, or total_cells
            for a pass.

        Returns
        -------
        observation : np.ndarray
            Observation from the perspective of the *next* current player.
        rewards : np.ndarray
            Shape (2,). Non-zero only when the game ends.
        done : bool
            Whether the game has ended.
        info : dict
            Keys: "step", "player", "winner".
        """
        if self.done:
            return self._observe(), self._last_rewards, True, self._info()

        acting_player = self.current_player
        decoded = self.game.decode_action(action)
        action_type = decoded["type"]
        uses_ca = self.game.uses_ca

        # Pie swap is dispatched before the standard action machinery —
        # it bypasses placement, capture, propagation, and CA. Legality
        # is enforced via get_legal_actions; if a caller submits an
        # illegal swap we still execute it (matches the rest of step()'s
        # trust-the-caller stance), but it would have been masked.
        if action_type == "pie_swap":
            self._handle_pie_swap()
            # No win-condition check — swap can't directly trigger a win.
            # The C2 stranded check is also skipped on this path: at the
            # swap point the board holds a single stone, which cannot
            # enemy-control every empty cell.
            self.step_count += 1
            if self.step_count >= self.game.max_game_steps:
                self._end_by_max_turns()
            if self.done:
                self._compute_rewards()
            info = {
                "step": self.step_count,
                "player": acting_player - 1,
                "winner": (self._winner - 1) if self._winner is not None else None,
                "pie_swap": True,
            }
            return self._observe(), self._last_rewards, self.done, info

        # Track whether this is P2's first move (the pie-decision point).
        # Resolve the pie offer regardless of which non-swap action P2
        # chooses, so the swap is offered exactly once per game.
        is_pie_decision_step = (
            self.game.pie_rule
            and not self._pie_resolved
            and acting_player == 2
            and self.step_count == 1
        )

        if action_type == "pass":
            self._handle_pass()
            # Run CA after pass if game is still going
            if uses_ca and not self.done:
                saved_pre_ca = self._save_state()
                for _ in range(self.game.ca_rule.steps_per_turn):
                    self._run_ca_step(acting_player)
                if self._needs_ko:
                    state_hash = self._board_hash()
                    if state_hash in self._position_history:
                        self._restore_state(saved_pre_ca)
                    else:
                        self._position_history.add(state_hash)
        else:
            if self._needs_ko:
                saved = self._save_state()

            if action_type == "place":
                self._handle_placement(decoded["cell"])
            elif action_type == "move":
                self._handle_movement(decoded["from_cell"], decoded["to_cell"])

            # Run CA steps after action, before ko check
            if uses_ca:
                for _ in range(self.game.ca_rule.steps_per_turn):
                    self._run_ca_step(acting_player)

            if self._needs_ko:
                state_hash = self._board_hash()
                if state_hash in self._position_history:
                    # Super-ko violation: undo the move and treat as a pass
                    self._restore_state(saved)
                    self._handle_pass()
                else:
                    self._position_history.add(state_hash)

        # Field-coupled rules: captures must update the field before the
        # win check (spec §3.4). Gated to field_connection wins and the
        # phase-1.5 field capture types so every legacy game keeps
        # ghost-influence semantics.
        if self._field_dirty and (
            self.game.win_condition.condition_type == "field_connection"
            or self.game.capture_rule.capture_type in FIELD_CAPTURE_TYPES
        ):
            self._recompute_field()
        self._field_dirty = False

        # Check win conditions (may set self.done and self._winner)
        if not self.done:
            self._check_win_conditions()

        # Phase-1.5 C2: a mover with no legal placement ends the game
        # immediately under the timeout tiebreak (spec §4 C2). Gated on the
        # constraint so every other game skips the extra legality scan.
        if (
            not self.done
            and self.game.placement_rule.constraint == "not_enemy_controlled"
            and not self._has_legal_placement(self.current_player)
        ):
            self._ended_by_no_moves = True
            self._end_by_max_turns()

        # Increment step count; enforce max turns
        self.step_count += 1
        if not self.done and self.step_count >= self.game.max_game_steps:
            self._end_by_max_turns()

        # Compute rewards
        if self.done:
            self._compute_rewards()

        # Pie offer expires after P2's first action (whether or not it was
        # a swap; swap dispatch above already returned early).
        if is_pie_decision_step:
            self._pie_resolved = True

        info = {
            "step": self.step_count,
            "player": acting_player - 1,  # 0-indexed
            "winner": (self._winner - 1) if self._winner is not None else None,
        }

        return self._observe(), self._last_rewards, self.done, info

    def step_simultaneous(
        self, action_p1: int, action_p2: int,
    ) -> tuple[np.ndarray, np.ndarray, bool, dict]:
        """Execute one round of simultaneous play.

        Both players submit actions; resolution is:
          1. Validate each action is legal for that player independently.
          2. If both actions target the same non-pass cell → mutual
             annihilation (cell stays empty; neither piece placed).
          3. Otherwise, both placements land.
          4. Captures apply based on the combined post-placement board.
          5. CA steps run with alternating perspective (step 1 from P1,
             step 2 from P2, etc).
          6. Super-ko: if resolved state was seen before, both actions
             treated as passes.
          7. Win conditions checked.

        Returns (observation, rewards, done, info) — same shape as step().
        """
        if self.done:
            return self._observe(), self._last_rewards, True, self._info()

        uses_ca = self.game.uses_ca

        # Decode actions
        decoded_p1 = self.game.decode_action(action_p1)
        decoded_p2 = self.game.decode_action(action_p2)
        is_pass_p1 = decoded_p1["type"] == "pass"
        is_pass_p2 = decoded_p2["type"] == "pass"

        # --- Both pass: same as consecutive double-pass in alternating ---
        if is_pass_p1 and is_pass_p2:
            self.consecutive_passes = 2
            self._end_by_double_pass()
            self._compute_rewards()
            self.step_count += 1
            return self._observe(), self._last_rewards, self.done, {
                "step": self.step_count,
                "player": None,  # simultaneous has no single acting player
                "winner": (self._winner - 1) if self._winner is not None else None,
            }

        # Reset pass counter if at least one player acted
        self.consecutive_passes = 0

        # Save state for ko rollback
        if self._needs_ko:
            saved = self._save_state()

        # --- Resolve placements with mutual-annihilation on collision ---
        cell_p1 = decoded_p1.get("cell") if decoded_p1["type"] == "place" else None
        cell_p2 = decoded_p2.get("cell") if decoded_p2["type"] == "place" else None

        # Movement not supported in simultaneous MVP
        if decoded_p1["type"] == "move" or decoded_p2["type"] == "move":
            raise NotImplementedError(
                "Movement actions are not supported in simultaneous turn games"
            )

        collision = cell_p1 is not None and cell_p1 == cell_p2

        if collision:
            # Mutual annihilation: neither stone placed, cell stays as-is
            # (or if a stone already there, it survives — we just don't
            # place anything).  This is the key novel mechanic of
            # simultaneous play.
            pass
        else:
            if cell_p1 is not None:
                self._handle_placement_simultaneous(cell_p1, 1)
            if cell_p2 is not None:
                self._handle_placement_simultaneous(cell_p2, 2)

        # --- Captures: apply for any placed stone, from combined board ---
        if not uses_ca and not collision:
            # Classic capture can fire for both placements.  Order:
            # P1's captures first (arbitrary but deterministic), then P2's.
            # This is NOT order-dependent for the standard capture types
            # because they check current board state independently.
            if cell_p1 is not None:
                self.current_player = 1
                self._apply_captures(cell_p1)
                self._apply_propagation(cell_p1)
            if cell_p2 is not None:
                self.current_player = 2
                self._apply_captures(cell_p2)
                self._apply_propagation(cell_p2)

        # --- CA steps: compute both perspectives from a shared snapshot ---
        # R16 fix: the R15 "run P1 step then P2 step" left a residual bias
        # because P1's step modified the board before P2 looked at it, so
        # P1 always won empty-cell birth races. Now both perspectives are
        # computed from the same pre-step snapshot and applied together;
        # when the two perspectives produce conflicting concrete outcomes
        # on the same cell (only happens for empty-cell births under the
        # symmetric rule table), the cell stays at its snapshot value.
        if uses_ca:
            for _ in range(self.game.ca_rule.steps_per_turn):
                self._run_ca_step_symmetric()

        # --- Super-ko check ---
        if self._needs_ko:
            state_hash = self._board_hash()
            if state_hash in self._position_history:
                # Both actions become passes (rollback)
                self._restore_state(saved)
                self.consecutive_passes += 1
                if self.consecutive_passes >= 2:
                    self._end_by_double_pass()
            else:
                self._position_history.add(state_hash)

        # --- Win condition check ---
        if not self.done:
            self._check_win_conditions()

        # --- Step count + max turns ---
        self.step_count += 1
        if not self.done and self.step_count >= self.game.max_game_steps:
            self._end_by_max_turns()

        if self.done:
            self._compute_rewards()

        info = {
            "step": self.step_count,
            "player": None,  # simultaneous
            "winner": (self._winner - 1) if self._winner is not None else None,
            "collision": collision,
        }
        return self._observe(), self._last_rewards, self.done, info

    def _handle_placement_simultaneous(self, cell: int, player: int) -> None:
        """Place a piece for `player` without advancing turn or applying captures.

        Used by step_simultaneous to do placements atomically for both
        players before captures/CA run.
        """
        prev_owner = int(self.board_owners[cell])
        if prev_owner != 0 and prev_owner != player:
            self.piece_counts[prev_owner - 1] -= 1

        self.board_owners[cell] = player
        if prev_owner != player:
            self.piece_counts[player - 1] += 1

    def get_legal_actions(self, player: Optional[int] = None) -> list[int]:
        """Return a list of legal actions for *player* (1 or 2).

        If player is None, uses self.current_player (alternating games).
        For simultaneous games, caller must pass player explicitly.
        """
        if self.done:
            return []

        if player is None:
            player = self.current_player
        enemy = 3 - player
        actions: list[int] = []

        # --- Place actions (if enabled) ---
        if self.game.action_rule.has_place():
            placement_rule = self.game.placement_rule

            # Determine candidate cells based on target. Iterate active_cells
            # (defaults to all cells on rectangular topologies; excludes holes
            # on sparse topologies like sierpinski).
            if placement_rule.target == "empty":
                candidates = [c for c in self.topo.active_cells if self.board_owners[c] == 0]
            else:  # "any"
                candidates = list(self.topo.active_cells)

            # Check if first_move_anywhere applies (player has 0 pieces)
            player_has_no_pieces = self.piece_counts[player - 1] == 0

            if not (placement_rule.first_move_anywhere and player_has_no_pieces):
                # Apply constraint filtering
                constraint = placement_rule.constraint
                if constraint == "adjacent_to_own":
                    candidates = [
                        c for c in candidates
                        if any(
                            self.board_owners[nbr] == player
                            for nbr in self.topo.get_neighbors(c)
                        )
                    ]
                elif constraint == "adjacent_to_enemy":
                    candidates = [
                        c for c in candidates
                        if any(
                            self.board_owners[nbr] == enemy
                            for nbr in self.topo.get_neighbors(c)
                        )
                    ]
                elif constraint == "adjacent_to_any":
                    candidates = [
                        c for c in candidates
                        if any(
                            self.board_owners[nbr] != 0
                            for nbr in self.topo.get_neighbors(c)
                        )
                    ]
                elif constraint == "not_enemy_controlled":
                    # Phase-1.5 C2: the field gates moves. A cell is
                    # placeable unless the enemy controls it beyond the
                    # control margin (contested ties stay open to both).
                    enemy_controls = self._control_mask(enemy)
                    candidates = [
                        c for c in candidates if not enemy_controls[c]
                    ]
                # "anywhere" — no filtering

            actions.extend(candidates)

        # Phase-1.5 C3: enemy-occupied cells the mover controls (beyond the
        # control margin, with the stone's own contribution included) are
        # legal placement targets — except the cell replaced last turn.
        if (
            self.game.action_rule.has_place()
            and self.game.capture_rule.capture_type == "field_replace"
        ):
            controlled = self._control_mask(player)
            lockout = (
                self._replace_lockout_cell
                if self.step_count == self._replace_lockout_step + 1
                else -1
            )
            actions.extend(
                c for c in self.topo.active_cells
                if self.board_owners[c] == enemy
                and controlled[c]
                and c != lockout
            )

        # --- Move actions (if enabled) ---
        if self.game.action_rule.has_move():
            move_constraint = self.game.action_rule.move_constraint
            for cell in self.topo.active_cells:
                if self.board_owners[cell] != player:
                    continue
                neighbors = self.topo.get_neighbors(cell)
                for nbr_idx in range(self.topo.max_degree):
                    if nbr_idx >= len(neighbors):
                        continue
                    target = neighbors[nbr_idx]
                    if move_constraint == "adjacent_empty":
                        if self.board_owners[target] != 0:
                            continue
                    elif move_constraint == "adjacent_any":
                        if self.board_owners[target] == player:
                            continue
                    actions.append(self.game.encode_move_action(cell, nbr_idx))

        # Always include the pass action
        actions.append(self.total_cells)  # pass

        # Pie swap (R20+): legal exactly once, at P2's first action, when
        # pie_rule is enabled and the offer hasn't yet been resolved.
        if (
            self.game.pie_rule
            and not self._pie_resolved
            and player == 2
            and self.step_count == 1
        ):
            actions.append(self.game.swap_action_idx)
        return actions

    def _has_legal_placement(self, player: int) -> bool:
        """True if *player* has at least one legal place action. Raw cell
        indices are < total_cells; pass, pie-swap and move actions all
        encode at or above total_cells (moves at total_cells + 1 + ...),
        so they never count as placements here."""
        return any(a < self.total_cells for a in self.get_legal_actions(player))

    def get_current_player(self) -> int:
        """Return the current player as a 0-indexed id (0 or 1)."""
        return self.current_player - 1

    def clone(self) -> GameEngineV2:
        """Return a deep copy of this engine."""
        return copy.deepcopy(self)

    # ------------------------------------------------------------------
    # Internal: pass handling
    # ------------------------------------------------------------------

    def _handle_pass(self) -> None:
        """Handle a pass action."""
        self.consecutive_passes += 1
        if self.consecutive_passes >= 2:
            # Both players passed consecutively — draw (R15 fix).
            self._end_by_double_pass()
        else:
            self._advance_turn()

    # ------------------------------------------------------------------
    # Internal: pie swap (R20+)
    # ------------------------------------------------------------------

    def _handle_pie_swap(self) -> None:
        """Apply the pie swap.

        Flips stone colours (1↔2), negates signed influence values, swaps
        per-player piece counts, marks the offer as resolved/used, advances
        the turn to player 1, and updates super-ko history with the new
        post-swap position.

        The swap consumes P2's first action — afterwards play resumes with
        the original P2 (now playing colour-1 stones) holding the existing
        stone, and the original P1 (now playing colour-2 stones) about to
        place their next stone.
        """
        # Flip ownership: 1 ↔ 2; 0 stays 0.
        owners = self.board_owners
        is_p1 = owners == 1
        is_p2 = owners == 2
        owners[is_p1] = 2
        owners[is_p2] = 1

        # Influence values are signed (positive = P1, negative = P2).
        # Negate to preserve "this cell favours its colour-owner" semantics.
        self.board_values *= -1.0

        # Swap piece counts.
        self.piece_counts[0], self.piece_counts[1] = (
            self.piece_counts[1],
            self.piece_counts[0],
        )
        # Placement counts swap identity with the colours (inert for
        # non-frontline families).
        self._placements_made.reverse()

        self._pie_resolved = True
        self._pie_used = True
        # Goals also swap so the swapper inherits the original P1's goal
        # alongside the original P1's stone — matching Hex pie semantics.
        # Without this, asymmetric-goal wins (connection) leave the swapper
        # with a colour-flipped stone at a position that's optimal for the
        # OPPOSITE goal, which makes swap anti-balancing rather than
        # balancing. Symmetric wins (territory/threshold) are unaffected.
        self._goals_swapped = not self._goals_swapped
        self.consecutive_passes = 0

        # Turn advances to player 1 (the original P1, who now plays colour 2).
        self._advance_turn()

        # The super-ko history that was recorded before swap referred to the
        # pre-swap colour assignment. Reset it to start from the post-swap
        # state — repeats are checked against post-swap positions only.
        if self._needs_ko:
            self._position_history = {self._board_hash()}

    # ------------------------------------------------------------------
    # Internal: placement
    # ------------------------------------------------------------------

    def _handle_placement(self, cell: int) -> None:
        """Place a piece, then apply captures and propagation."""
        self.consecutive_passes = 0
        player = self.current_player

        # If the cell was occupied by someone else, update that player's count
        prev_owner = int(self.board_owners[cell])
        self._replace_prev_owner = prev_owner
        if prev_owner != 0 and prev_owner != player:
            self.piece_counts[prev_owner - 1] -= 1

        # Place the piece
        self.board_owners[cell] = player
        if prev_owner != player:
            self.piece_counts[player - 1] += 1
        # FRONTLINE participation clause (§3.7): count the mover's placement.
        # Inert for non-contested_majority families.
        self._placements_made[player - 1] += 1

        # Skip classic capture/propagation when CA is active
        if not self.game.uses_ca:
            self._apply_captures(cell)
            self._apply_propagation(cell)

        # Advance turn
        self._advance_turn()

    # ------------------------------------------------------------------
    # Internal: movement
    # ------------------------------------------------------------------

    def _handle_movement(self, from_cell: int, to_cell: int) -> None:
        """Move a piece from from_cell to to_cell, then apply captures and propagation."""
        self.consecutive_passes = 0
        player = self.current_player

        # Remove piece from source
        self.board_owners[from_cell] = 0
        self.piece_counts[player - 1] -= 1

        # If target has enemy piece and move_constraint allows capture
        target_owner = int(self.board_owners[to_cell])
        if target_owner != 0 and target_owner != player:
            self.piece_counts[target_owner - 1] -= 1

        # Place piece at target
        self.board_owners[to_cell] = player
        self.piece_counts[player - 1] += 1

        # Skip classic capture/propagation when CA is active
        if not self.game.uses_ca:
            self._apply_captures(to_cell)
            self._apply_propagation(to_cell)

        # Advance turn
        self._advance_turn()

    # ------------------------------------------------------------------
    # Internal: capture logic
    # ------------------------------------------------------------------

    def _apply_captures(self, placed_cell: int) -> None:
        """Apply the game's capture rule after a piece is placed."""
        capture_type = self.game.capture_rule.capture_type

        if capture_type == "none":
            return
        elif capture_type == "surround":
            self._capture_surround(placed_cell)
        elif capture_type == "custodian":
            self._capture_custodian(placed_cell)
        elif capture_type == "outnumber":
            self._capture_outnumber(placed_cell)
        elif capture_type == "field_flip":
            self._capture_field_flip(placed_cell)
        elif capture_type == "field_replace":
            self._capture_field_replace(placed_cell)

    def _capture_surround(self, placed_cell: int) -> None:
        """Go-style capture: remove enemy groups with 0 liberties adjacent
        to the placed cell."""
        player = self.current_player
        enemy = 3 - player

        # Collect unique enemy groups adjacent to the placed cell
        checked_cells: set[int] = set()
        for nbr in self.topo.get_neighbors(placed_cell):
            if self.board_owners[nbr] == enemy and nbr not in checked_cells:
                group = self.topo.get_group(nbr, self.board_owners)
                checked_cells.update(group)
                liberties = self.topo.get_liberties(group, self.board_owners)
                if len(liberties) == 0:
                    self._remove_group(group, enemy)

    def _capture_custodian(self, placed_cell: int) -> None:
        """Custodian capture: for each axis direction from placed cell, walk
        along collecting consecutive enemy cells. If the walk ends on a
        friendly cell, flip all those enemy cells to the current player.

        Only meaningful on grid-shaped topologies where axis-aligned walks
        make sense. On hex/moore, custodian capture is skipped. On sparse
        topologies (sierpinski), the walk terminates on a hole as if it
        were an empty cell — hole-as-wall semantics.
        """
        if self.topo.topology_type not in ("grid", "torus", "sierpinski", "holes"):
            return
        player = self.current_player
        enemy = 3 - player
        coords = list(self.topo.cell_to_coords(placed_cell))

        for dim in range(self.topo.num_dimensions):
            for delta in (-1, 1):
                captured: list[int] = []
                pos = coords[dim] + delta
                while 0 <= pos < self.topo.axis_size:
                    test_coords = list(coords)
                    test_coords[dim] = pos
                    test_cell = self.topo.coords_to_cell(tuple(test_coords))
                    if not self.topo.active_mask[test_cell]:
                        # Hole acts as a wall: no capture, no continuation.
                        break
                    owner = int(self.board_owners[test_cell])
                    if owner == enemy:
                        captured.append(test_cell)
                        pos += delta
                    elif owner == player:
                        # Bracketed — flip all captured cells
                        for c in captured:
                            self.board_owners[c] = player
                            self.piece_counts[enemy - 1] -= 1
                            self.piece_counts[player - 1] += 1
                        break
                    else:
                        # Empty cell — no capture in this direction
                        break

    def _capture_outnumber(self, placed_cell: int) -> None:
        """Outnumber capture: each adjacent enemy cell is removed if the
        number of friendly neighbours around it meets the threshold."""
        player = self.current_player
        enemy = 3 - player
        threshold = self.game.capture_rule.threshold

        to_remove: list[int] = []
        for nbr in self.topo.get_neighbors(placed_cell):
            if self.board_owners[nbr] == enemy:
                friendly_count = sum(
                    1 for n2 in self.topo.get_neighbors(nbr)
                    if self.board_owners[n2] == player
                )
                if friendly_count >= threshold:
                    to_remove.append(nbr)

        for cell in to_remove:
            self.board_owners[cell] = 0
            self.piece_counts[enemy - 1] -= 1

    def _control_mask(self, player: int) -> np.ndarray:
        """Boolean mask over all cells: does *player* control the cell
        beyond the control margin? The single definition of 'control'
        shared by field_flip, field_replace legality, and the C2 gate."""
        margin = getattr(self.game.win_condition, "control_margin", 0.0)
        sign = 1.0 if player == 1 else -1.0
        return sign * self.board_values > margin

    def _capture_field_flip(self, placed_cell: int) -> None:
        """Phase-1.5 C1: enemy stones on mover-controlled cells flip colour.

        Control is measured INCLUDING the stone's own contribution, so a
        lone stone needs net opposing pressure > 1 + margin to flip
        (3 net adjacent attackers at r=1/d=0.5/eps=0.25). Flips cascade:
        each flip raises the mover's field monotonically, so resolution
        terminates in at most #enemy-stones iterations. board_values does
        not yet include the just-placed stone here (propagation runs after
        captures), so we recompute from board_owners first; the final
        gated recompute in step() corrects propagation's later double-add.
        """
        mover = self.current_player
        enemy = 3 - mover
        self._recompute_field()
        flipped_all: list[int] = []
        while True:
            mask = self._control_mask(mover)
            to_flip = [
                c for c in self.topo.active_cells
                if self.board_owners[c] == enemy and mask[c]
            ]
            if not to_flip:
                break
            for c in to_flip:
                self.board_owners[c] = mover
            # accumulated for quota accounting (SIEGE only; see post-loop block)
            flipped_all.extend(to_flip)
            self.piece_counts[enemy - 1] -= len(to_flip)
            self.piece_counts[mover - 1] += len(to_flip)
            self._recompute_field()
        # SIEGE quota accounting — string-gated so legacy and phase-1.5 flip
        # games remain bit-identical. Constraints (prereg-locked):
        #   - Breaker-only (mover == 2): Maker flips never tick the quota.
        #   - Distinct cells: a cell in _quota_cells never ticks again
        #     (kills flip-tennis where the same stone bounces back and forth).
        #   - Per-move cap QUOTA_TICK_CAP_PER_MOVE: an avalanche from one
        #     placement can add at most this many ticks (anti-cascade-burst).
        if (
            mover == 2
            and getattr(self.game.win_condition, "condition_type_p2", "")
            == "capture_quota"
        ):
            new_cells = [c for c in flipped_all if c not in self._quota_cells]
            self._quota_cells.update(new_cells)
            self._quota_ticks += min(len(new_cells), QUOTA_TICK_CAP_PER_MOVE)
        self._field_dirty = True

    def _capture_field_replace(self, placed_cell: int) -> None:
        """Phase-1.5 C3: bookkeeping after a placement in a field_replace
        game. The replacement itself already happened in _handle_placement
        (overwrite path); here we set the one-turn recapture lockout when
        an enemy stone was displaced, and mark the field for recompute
        (the displaced stone's kernel must be rebuilt away).

        Under the current control definition the lockout is provably never
        binding at any radius/decay with positive strength and non-negative
        margin: the replacement itself swings the cell by 2*strength toward
        the mover (remove -strength, add +strength, exact recompute) and no
        other board change intervenes before the opponent's legality check,
        so opponent control of the replaced cell would need margin < -strength
        (which the non-negative margin condition rules out). It DOES bind for
        negative margins, where it works correctly as a safety net. Verified
        empirically at r=2, r=3, decay=1.5 (0 binding events with margin≥0).
        Kept as a cheap safety net for future control definitions that depend
        on more than the instantaneous field.
        """
        if self._replace_prev_owner not in (0, self.current_player):
            self._replace_lockout_cell = placed_cell
            self._replace_lockout_step = self.step_count
        self._field_dirty = True

    def _remove_group(self, group: set[int], owner: int) -> None:
        """Remove all pieces in a group from the board."""
        for cell in group:
            self.board_owners[cell] = 0
        self.piece_counts[owner - 1] -= max(0, len(group))
        self._field_dirty = True

    # ------------------------------------------------------------------
    # Internal: propagation logic
    # ------------------------------------------------------------------

    def _apply_propagation(self, placed_cell: int) -> None:
        """Apply the game's propagation rule after placement and captures."""
        prop_type = self.game.propagation_rule.prop_type

        if prop_type == "none":
            return
        elif prop_type == "influence":
            self._propagate_influence(placed_cell)
        elif prop_type == "cascade":
            self._propagate_cascade()

    def _add_influence(self, cell: int, sign: float) -> None:
        """Add one stone's influence kernel to board_values (no clamp).

        Vectorized via the module-level kernel cache — bit-identical to
        the historical per-cell loop: each target receives exactly one
        ``+=`` per kernel application, and *sign* is exactly +/-1.0, so
        factoring it out of the cached weight is float-exact. Kernels
        are looked up (not stored on the instance) so clone()'s deepcopy
        never duplicates them.
        """
        rule = self.game.propagation_rule
        idx, w = _influence_kernels(
            self.topo, rule.radius, rule.strength, rule.decay,
        )[cell]
        self.board_values[idx] += sign * w

    def _propagate_influence(self, placed_cell: int) -> None:
        """Influence propagation: add strength * decay^distance to
        board_values for cells within radius. Positive for player 1,
        negative for player 2."""
        sign = 1.0 if self.current_player == 1 else -1.0
        self._add_influence(placed_cell, sign)
        # Clamp to prevent explosion
        np.clip(self.board_values, -100.0, 100.0, out=self.board_values)

    def _recompute_field(self) -> None:
        """Rebuild board_values from scratch from stones currently on the
        board. Field-Connect only (spec §3.4: "removal recomputes the
        field") — legacy games keep ghost influence from dead stones.
        Idempotent: safe regardless of where in step() it runs.
        """
        if self.game.propagation_rule.prop_type != "influence":
            return
        self.board_values[:] = 0.0
        for cell in self.topo.active_cells:
            owner = int(self.board_owners[cell])
            if owner != 0:
                self._add_influence(cell, 1.0 if owner == 1 else -1.0)
        np.clip(self.board_values, -100.0, 100.0, out=self.board_values)

    def _per_player_fields(self) -> tuple[np.ndarray, np.ndarray]:
        """Per-player non-negative influence fields (I1, I2), recomputed
        from current owners via the kernel cache — the same arithmetic as
        _recompute_field split by owner (spec §3.1). Reads board_owners
        only, so ghost influence can never contaminate scoring."""
        rule = self.game.propagation_rule
        kernels = _influence_kernels(
            self.topo, rule.radius, rule.strength, rule.decay,
        )
        i1 = np.zeros(self.total_cells, dtype=np.float64)
        i2 = np.zeros(self.total_cells, dtype=np.float64)
        # Perf: iterate occupied cells only via flatnonzero — bit-identical
        # to the all-active-cells loop because active_cells is constructed
        # ascending in all topology constructors and flatnonzero is
        # ascending, so the float += accumulation order is unchanged
        # (stones only exist on active cells — engine invariant).
        for cell in np.flatnonzero(self.board_owners):
            owner = int(self.board_owners[cell])
            idx, w = kernels[cell]
            (i1 if owner == 1 else i2)[idx] += w
        return i1, i2

    def contested_scores(self) -> tuple[int, int, int]:
        """(S1, S2, engaged_count) for contested_majority (spec §3.2-3.3).

        Engaged: min(I1, I2) >= engage_threshold, over ACTIVE cells
        (empty and occupied both count — control-includes-empty
        convention). Score: engaged cells led beyond CM_LEAD_TOL;
        led-by-neither engaged cells score no one."""
        wc = self.game.win_condition
        i1, i2 = self._per_player_fields()
        # Perf: lazily-cached active-cell index array (the topology never
        # changes across resets, so this is built once per engine, NOT
        # cleared in reset()).
        if self._cm_active_idx is None:
            self._cm_active_idx = np.asarray(
                list(self.topo.active_cells), dtype=np.intp)
        active = self._cm_active_idx
        e1, e2 = i1[active], i2[active]
        engaged = np.minimum(e1, e2) >= wc.engage_threshold
        diff = e1 - e2
        s1 = int(np.count_nonzero(engaged & (diff > CM_LEAD_TOL)))
        s2 = int(np.count_nonzero(engaged & (diff < -CM_LEAD_TOL)))
        return s1, s2, int(np.count_nonzero(engaged))

    def _resolve_contested_by_score(self) -> None:
        """Contested-majority terminal resolution (spec §3.7), shared by
        double-pass and timeout. Order: komi-adjusted score → stones
        tiebreak on EXACT ties → participation clause → draw. A
        score-leader always wins by score; pieces only break exact ties,
        so the R13/14 piece-majority exploit cannot recur. A player who
        placed zero stones the entire game can never be declared winner
        (pass-bot inaction floor, spec §4.4)."""
        wc = self.game.win_condition
        s1, s2, _ = self.contested_scores()
        s2_eff = s2 + wc.komi_cells
        if s1 > s2_eff:
            winner: Optional[int] = 1
        elif s2_eff > s1:
            winner = 2
        else:
            p1, p2 = self.piece_counts
            winner = 1 if p1 > p2 else 2 if p2 > p1 else None
        if winner is not None and self._placements_made[winner - 1] == 0:
            winner = None
        self.done = True
        self._winner = winner

    def _propagate_cascade(self) -> None:
        """Cascade propagation: after captures, repeatedly check all enemy
        groups for 0 liberties and remove them. Only applies when
        capture_type is "surround". Limited to 10 iterations."""
        if self.game.capture_rule.capture_type != "surround":
            return

        enemy = 3 - self.current_player

        for _ in range(10):
            captured_any = False
            checked: set[int] = set()
            for cell in self.topo.active_cells:
                if self.board_owners[cell] == enemy and cell not in checked:
                    group = self.topo.get_group(cell, self.board_owners)
                    checked.update(group)
                    liberties = self.topo.get_liberties(group, self.board_owners)
                    if len(liberties) == 0:
                        self._remove_group(group, enemy)
                        captured_any = True
            if not captured_any:
                break

    # ------------------------------------------------------------------
    # Internal: cellular automaton step
    # ------------------------------------------------------------------

    def _run_ca_step_symmetric(self) -> None:
        """Run one CA step computing both perspectives from a shared snapshot.

        R16 player-symmetric replacement for the sequential _run_ca_step(1);
        _run_ca_step(2) pattern. With R15's symmetric rule tables, owned
        cells produce the same concrete outcome in both perspectives
        (invariant: T(1,f,e) = swap(T(2,e,f)) so x1's concrete = x2's
        concrete). The only conflict case is empty cells where both views
        would "birth own" — P1 view wants a P1 stone, P2 view wants a P2
        stone. Sequential ordering awarded those to P1; this implementation
        resolves them as no-op (cell stays empty), which is symmetric and
        analogous to the mutual-annihilation semantic used for placement
        collisions in simultaneous games.
        """
        ca_rule = self.game.ca_rule
        snapshot = self.board_owners.copy()
        new_owners = snapshot.copy()

        # Iterate active cells only. On rectangular topologies this is identical
        # to range(total_cells). On sierpinski it skips holes — without this,
        # a mutated CA rule with table[(0,0,0)]==1 would spawn permanent stones
        # on every hole every step (holes have friendly==0, enemy==0 always).
        for cell in self.topo.active_cells:
            cell_owner = int(snapshot[cell])

            # Count neighbors from snapshot (absolute).
            p1_neighbors = 0
            p2_neighbors = 0
            for nbr in self.topo.get_neighbors(cell):
                nbr_owner = int(snapshot[nbr])
                if nbr_owner == 1:
                    p1_neighbors += 1
                elif nbr_owner == 2:
                    p2_neighbors += 1

            # Per-player concrete outcome from the shared snapshot.
            outcomes = {}
            for acting_player in (1, 2):
                opponent = 3 - acting_player
                friendly_count = p1_neighbors if acting_player == 1 else p2_neighbors
                enemy_count = p2_neighbors if acting_player == 1 else p1_neighbors

                if cell_owner == 0:
                    abstract_state = 0
                elif cell_owner == acting_player:
                    abstract_state = 1
                else:
                    abstract_state = 2

                new_abstract = ca_rule.apply(abstract_state, friendly_count, enemy_count)

                if new_abstract == 0:
                    outcomes[acting_player] = 0
                elif new_abstract == 1:
                    outcomes[acting_player] = acting_player
                else:  # 2 = enemy from acting's perspective
                    outcomes[acting_player] = opponent

            # Resolve: agreement → apply; disagreement → keep snapshot value.
            if outcomes[1] == outcomes[2]:
                new_owners[cell] = outcomes[1]
            # else: empty-cell mutual-birth conflict, cell stays at snapshot.

        self.board_owners[:] = new_owners
        self.piece_counts[0] = int(np.sum(new_owners == 1))
        self.piece_counts[1] = int(np.sum(new_owners == 2))

    def _run_ca_step(self, acting_player: int) -> None:
        """Run one simultaneous CA step over all cells.

        All cells read from the same pre-step snapshot.  The rule is
        player-symmetric: 'friendly' always means the acting player and
        'enemy' means the opponent.  The same table is used regardless
        of who is acting — only the friendly/enemy mapping changes.

        States: 0=empty, 1=friendly (acting player), 2=enemy (opponent).
        """
        ca_rule = self.game.ca_rule
        opponent = 3 - acting_player
        snapshot = self.board_owners.copy()
        new_owners = snapshot.copy()

        # Active-cell iteration; see _run_ca_step_symmetric for rationale.
        for cell in self.topo.active_cells:
            cell_owner = int(snapshot[cell])

            # Count neighbors from snapshot (relative to acting player)
            friendly_count = 0
            enemy_count = 0
            for nbr in self.topo.get_neighbors(cell):
                nbr_owner = int(snapshot[nbr])
                if nbr_owner == acting_player:
                    friendly_count += 1
                elif nbr_owner == opponent:
                    enemy_count += 1

            # Map cell state to abstract (0=empty, 1=friendly, 2=enemy)
            if cell_owner == 0:
                abstract_state = 0
            elif cell_owner == acting_player:
                abstract_state = 1
            else:
                abstract_state = 2

            # Apply rule
            new_abstract = ca_rule.apply(abstract_state, friendly_count, enemy_count)

            # Map back to concrete owner
            if new_abstract == 0:
                new_owners[cell] = 0
            elif new_abstract == 1:
                new_owners[cell] = acting_player
            else:  # 2 = enemy
                new_owners[cell] = opponent

        # Write all changes simultaneously
        self.board_owners[:] = new_owners
        self.piece_counts[0] = int(np.sum(new_owners == 1))
        self.piece_counts[1] = int(np.sum(new_owners == 2))

    # ------------------------------------------------------------------
    # Internal: turn advancement
    # ------------------------------------------------------------------

    def _advance_turn(self) -> None:
        """Advance the turn: switch player if appropriate."""
        self.placements_this_turn += 1
        turn_type = self.game.turn_structure.turn_type

        if (
            turn_type == "alternating"
            or self.placements_this_turn >= self.game.turn_structure.pieces_per_turn
        ):
            self.current_player = 3 - self.current_player
            self.placements_this_turn = 0

    # ------------------------------------------------------------------
    # Internal: win condition checking
    # ------------------------------------------------------------------

    def _check_win_conditions(self) -> None:
        """Check the game's win condition. Sets self.done and self._winner."""
        wc = self.game.win_condition

        if getattr(wc, "condition_type_p2", ""):
            self._check_win_asymmetric(wc)
            return

        ctype = wc.condition_type

        if ctype == "territory":
            self._check_territory(wc.threshold)
        elif ctype == "elimination":
            self._check_elimination()
        elif ctype == "connection":
            dim_p2 = wc.target_dimension_p2
            if dim_p2 < 0:
                dim_p2 = (wc.target_dimension + 1) % self.game.num_dimensions
            if self._goals_swapped:
                # After pie swap, the asymmetric goals swap with the players.
                self._check_connection(dim_p2, wc.target_dimension)
            else:
                self._check_connection(wc.target_dimension, dim_p2)
        elif ctype == "majority":
            # Majority only triggers at max_turns (handled in _end_by_max_turns)
            pass
        elif ctype == "threshold":
            self._check_threshold(wc.threshold)
        elif ctype == "field_connection":
            dim_p2 = wc.target_dimension_p2
            if dim_p2 < 0:
                dim_p2 = (wc.target_dimension + 1) % self.game.num_dimensions
            margin = getattr(wc, "control_margin", 0.0)
            if self._goals_swapped:
                # After pie swap, the asymmetric goals swap with the players.
                self._check_field_connection(dim_p2, wc.target_dimension, margin)
            else:
                self._check_field_connection(wc.target_dimension, dim_p2, margin)
        elif ctype == "contested_majority":
            self._check_contested_majority(wc)

    def _check_territory(self, threshold: float) -> None:
        """Win if any player owns > threshold fraction of active cells.

        Uses num_active_cells, not total_cells: on sparse topologies the
        bounding box includes holes that can never be owned, so scaling
        by total_cells would make the threshold unreachable.

        R21 S4 komi: P2's effective count gains ``komi_p2 * num_active_cells``
        virtual cells, so P2 reaches the territory threshold sooner than P1
        by the komi fraction.
        """
        komi = getattr(self.game, "komi_p2", 0.0) * self.topo.num_active_cells
        target = threshold * self.topo.num_active_cells
        for player in (1, 2):
            owned = self.piece_counts[player - 1]
            effective = owned + (komi if player == 2 else 0.0)
            if effective > target:
                self._winner = player
                self.done = True
                return

    def _check_elimination(self) -> None:
        """Win if the enemy has 0 pieces (and the game has progressed)."""
        for player in (1, 2):
            enemy = 3 - player
            # Only check elimination if the enemy has actually had pieces
            # (i.e., at least one step has occurred)
            if self.piece_counts[enemy - 1] == 0 and self.piece_counts[player - 1] > 0:
                self._winner = player
                self.done = True
                return

    def _check_connection(self, dim_p1: int, dim_p2: int) -> None:
        """Win if a player connects opposite faces along their assigned dimension.

        P1 connects along *dim_p1*, P2 connects along *dim_p2* (Hex-style).

        R16 fix: when both players complete their connection on the same
        tick (possible in simultaneous games, and occasionally in alternating
        games on the final move), resolve as a draw instead of awarding the
        win to P1 via iteration order. Previously `for player in (1, 2)` +
        `return` on first match silently gave P1 every simultaneous
        connection tie — surfaced by 5/5 R15 sim×CA teams.
        """
        dims = {1: dim_p1, 2: dim_p2}
        connected = {}
        for player in (1, 2):
            cells = {c for c in self.topo.active_cells if self.board_owners[c] == player}
            if self.topo.connects_faces(cells, dims[player]):
                connected[player] = True
        if len(connected) == 2:
            # Both players completed connection same tick — draw.
            self._winner = None
            self.done = True
        elif len(connected) == 1:
            self._winner = next(iter(connected))
            self.done = True

    def _check_win_asymmetric(self, wc) -> None:
        """SIEGE dispatch: P1's win is wc.condition_type checked for P1 ONLY
        (field_connection); P2's win is wc.condition_type_p2 (capture_quota).
        The mover's condition is checked first so one step never awards both.
        Timeout is handled separately by _end_by_max_turns/timeout_winner.
        No _goals_swapped handling: SIEGE games are pie-OFF by pre-registration.
        Precondition: wc.condition_type == "field_connection" — this method
        hardcodes field-connection semantics for P1; a second asymmetric
        family must extend the dispatch, not reuse this.
        """
        margin = getattr(wc, "control_margin", 0.0)
        controlled_p1 = {
            c for c in self.topo.active_cells if self.board_values[c] > margin
        }
        p1_win = self.topo.connects_faces(controlled_p1, wc.target_dimension)
        p2_win = (
            wc.condition_type_p2 == "capture_quota"
            and wc.capture_quota > 0
            and self._quota_ticks >= wc.capture_quota
        )
        order = (1, 2) if self.current_player == 1 else (2, 1)
        for p in order:
            if (p == 1 and p1_win) or (p == 2 and p2_win):
                self._winner = p
                self.done = True
                return

    def _check_field_connection(
        self, dim_p1: int, dim_p2: int, margin: float,
    ) -> None:
        """Field-Connect win: a player wins when their influence-CONTROLLED
        cells connect their two target faces (Hex on the influence field).

        Control is sign-of-field with a margin: P1-controlled iff
        board_values > +margin, P2-controlled iff < -margin, else
        contested. Control includes EMPTY cells — stones matter only
        through the field they project (spec §3).
        """
        controlled = {
            1: {c for c in self.topo.active_cells
                if self.board_values[c] > margin},
            2: {c for c in self.topo.active_cells
                if self.board_values[c] < -margin},
        }
        dims = {1: dim_p1, 2: dim_p2}
        # connected: only length and first element matter (same as _check_connection).
        connected = [
            p for p in (1, 2)
            if self.topo.connects_faces(controlled[p], dims[p])
        ]
        if len(connected) == 2:
            # Control sets are disjoint for margin >= 0, so two crossings
            # cannot coexist on the rhombus; defensive draw, mirrors
            # _check_connection.
            self._winner = None
            self.done = True
        elif len(connected) == 1:
            self._winner = connected[0]
            self.done = True

    def _check_contested_majority(self, wc) -> None:
        """FRONTLINE early-end (spec §3.4): the same player must hold a
        komi-adjusted lead >= end_margin at 3 consecutive ply-checks
        ending at a round-end. At this call site step_count is
        PRE-increment, so a round-end (the check after P2's ply) is an
        ODD step_count — alternating games only, the family's sole
        registered turn structure (enforced by the __init__ guard);
        pie-swap plies skip the win check and preserve parity. Checks
        before min_turns_score_end reset the streak (they cannot count
        toward it). Leader-signed: a leader change restarts the streak
        at ±1; the intervening-odd-ply requirement means the lead
        survived the opponent's last word."""
        if self.step_count < wc.min_turns_score_end:
            self._cm_streak = 0
            return
        s1, s2, _ = self.contested_scores()
        lead = s1 - (s2 + wc.komi_cells)
        if lead >= wc.end_margin:
            self._cm_streak = self._cm_streak + 1 if self._cm_streak > 0 else 1
        elif -lead >= wc.end_margin:
            self._cm_streak = self._cm_streak - 1 if self._cm_streak < 0 else -1
        else:
            self._cm_streak = 0
            return
        if abs(self._cm_streak) >= 3 and self.step_count % 2 == 1:
            self._ended_by_score_margin = True
            self.done = True
            self._winner = 1 if self._cm_streak > 0 else 2

    def _check_threshold(self, threshold: float) -> None:
        """Win if a player's total board_values on their cells exceed threshold.

        R16 fix: previously `for player in (1, 2)` + `return` on first
        crossing gave P1 every same-tick crossing regardless of margin —
        including cases where P2's effective score was higher (R15 eval
        documented P2 at 42.6 losing to P1 at 41.85 etc). Now: compute
        both players' effective values; if both cross, higher margin
        wins; equal margins → draw.

        R17 fix: simultaneous play applies P1's then P2's _apply_propagation
        as separate `+=` passes over board_values. With overlapping radii
        the two orderings differ by FP ULPs (~1e-15 on totals of size 10).
        4 R16 sim teams hit cases where both players' true math margins
        were equal but ULP-noise made effectives[1] slightly larger and
        gave P1 a phantom win. Comparing margins under a tolerance
        (~1e-9 of threshold scale) treats those as the draws they should be.
        """
        # Tolerance scales with threshold magnitude; floor at 1e-9 so very
        # small thresholds still get a usable tolerance.
        tol = max(1e-9, 1e-9 * abs(threshold))

        # R21 S4 komi: P2's effective score gains a fraction of the win
        # target. komi_p2=0.10 + threshold=40 → P2 wins at effective ≥ 36.
        komi = getattr(self.game, "komi_p2", 0.0) * threshold

        effectives = {}
        for player in (1, 2):
            total_value = sum(
                self.board_values[c]
                for c in self.topo.active_cells
                if self.board_owners[c] == player
            )
            # Player 1's values are positive, player 2's are negative.
            # Komi is added to P2's effective score (post-negation).
            effective = total_value if player == 1 else (-total_value + komi)
            if effective > threshold:
                effectives[player] = effective
        if len(effectives) == 2:
            diff = effectives[1] - effectives[2]
            if diff > tol:
                self._winner = 1
            elif diff < -tol:
                self._winner = 2
            else:
                self._winner = None  # margins tied within FP precision → draw
            self.done = True
        elif len(effectives) == 1:
            self._winner = next(iter(effectives))
            self.done = True

    def _end_by_max_turns(self) -> None:
        """End the game by comparing piece counts (majority rule).

        Exception: field_connection games use controlled-cell count (spec §3.7),
        with komi applied using the same multiplicative convention as territory.
        """
        self._ended_by_max_turns = True
        # SIEGE: timeout_winner in {1,2} overrides the tiebreak; 0 = legacy (field_connection or piece-count).
        tw = getattr(self.game.win_condition, "timeout_winner", 0)
        if tw:
            self.done = True
            self._winner = tw
            return
        if self.game.win_condition.condition_type == "contested_majority":
            # FRONTLINE: timeout resolves by score (spec §3.6-3.7).
            self._resolve_contested_by_score()
            return
        if self.game.win_condition.condition_type == "field_connection":
            # Spec §3.7: tiebreak by controlled-cell count, komi applied
            # (multiplicative on num_active_cells, same convention as
            # territory count wins).
            self.done = True
            margin = getattr(self.game.win_condition, "control_margin", 0.0)
            p1 = sum(
                1 for c in self.topo.active_cells
                if self.board_values[c] > margin
            )
            p2 = sum(
                1 for c in self.topo.active_cells
                if self.board_values[c] < -margin
            )
            komi = getattr(self.game, "komi_p2", 0.0) * self.topo.num_active_cells
            p2_eff = p2 + komi
            if p1 > p2_eff:
                self._winner = 1
            elif p2_eff > p1:
                self._winner = 2
            else:
                self._winner = None
            return
        self.done = True
        p1 = self.piece_counts[0]
        p2 = self.piece_counts[1]
        if p1 > p2:
            self._winner = 1
        elif p2 > p1:
            self._winner = 2
        else:
            self._winner = None  # draw

    def _end_by_double_pass(self) -> None:
        """End the game when both players passed consecutively.

        Legacy: draw. Previously this resolved via piece majority (same
        as max_turns), which allowed a leading player to stop placing and
        force a win without actually meeting the stated win condition.
        R13 and R14 human evaluations saw this fire in ~30% of top-tier
        games. Treating the double-pass as a draw makes the win condition
        the only path to a decisive result.

        contested_majority (FRONTLINE, gated): the score IS the win
        condition, so at/after min_turns_score_end a double-pass resolves
        by score (spec §3.5, §3.7) — the legacy exploit cannot recur.
        Before min_turns: legacy draw (guards exploration-phase
        double-passes from instant komi wins).
        """
        self._ended_by_double_pass = True
        wc = self.game.win_condition
        if (
            wc.condition_type == "contested_majority"
            and self.step_count >= wc.min_turns_score_end
        ):
            self._resolve_contested_by_score()
            return
        self.done = True
        self._winner = None

    # ------------------------------------------------------------------
    # Internal: super-ko support
    # ------------------------------------------------------------------

    def _board_hash(self) -> int:
        """Hash the current board state for super-ko detection.

        Includes board ownership and whose turn it is, so the same board
        position with a different player to move is considered distinct.
        """
        return hash((self.board_owners.tobytes(), self.current_player))

    def _save_state(self) -> dict:
        """Snapshot mutable state for potential ko rollback."""
        return {
            "board_owners": self.board_owners.copy(),
            "board_values": self.board_values.copy(),
            "current_player": self.current_player,
            "piece_counts": self.piece_counts[:],
            # Ko rollback turns an applied placement into a pass — the
            # FRONTLINE placement count must roll back with it.
            "_placements_made": self._placements_made[:],
            "placements_this_turn": self.placements_this_turn,
            "consecutive_passes": self.consecutive_passes,
            # _field_dirty rides with the board state it tracks
            # (ko rollback must not leak a stale flag).
            "_field_dirty": self._field_dirty,
            "_replace_lockout_cell": self._replace_lockout_cell,
            "_replace_lockout_step": self._replace_lockout_step,
            "_replace_prev_owner": self._replace_prev_owner,
        }

    def _restore_state(self, saved: dict) -> None:
        """Restore mutable state from a snapshot."""
        self.board_owners[:] = saved["board_owners"]
        self.board_values[:] = saved["board_values"]
        self.current_player = saved["current_player"]
        self.piece_counts = saved["piece_counts"]
        self._placements_made = saved["_placements_made"]
        self.placements_this_turn = saved["placements_this_turn"]
        self.consecutive_passes = saved["consecutive_passes"]
        self._field_dirty = saved["_field_dirty"]
        self._replace_lockout_cell = saved["_replace_lockout_cell"]
        self._replace_lockout_step = saved["_replace_lockout_step"]
        self._replace_prev_owner = saved["_replace_prev_owner"]

    # ------------------------------------------------------------------
    # Internal: observation and rewards
    # ------------------------------------------------------------------

    def _observe(self) -> np.ndarray:
        """Build the observation vector for the current player.

        Layout:
          [owner_encoded (total_cells), board_values (total_cells),
           step_frac, own_piece_frac, enemy_piece_frac,
           quota_frac (capture_quota games only)]
        """
        p = self.current_player
        enemy = 3 - p

        # Owner encoding: +1 for own, -1 for enemy, 0 for empty
        owner_encoded = np.zeros(self.total_cells, dtype=np.float64)
        own_mask = self.board_owners == p
        enemy_mask = self.board_owners == enemy
        owner_encoded[own_mask] = 1.0
        owner_encoded[enemy_mask] = -1.0

        # Metadata
        max_turns = self.game.max_game_steps
        step_frac = self.step_count / max_turns if max_turns > 0 else 0.0
        own_pieces = self.piece_counts[p - 1]
        enemy_pieces = self.piece_counts[enemy - 1]
        own_frac = own_pieces / self.total_cells if self.total_cells > 0 else 0.0
        enemy_frac = enemy_pieces / self.total_cells if self.total_cells > 0 else 0.0

        metadata = [step_frac, own_frac, enemy_frac]
        wc = self.game.win_condition
        if getattr(wc, "condition_type_p2", "") == "capture_quota":
            q = wc.capture_quota
            # SIEGE: Breaker's quota progress; clock is already step_frac above.
            metadata.append(self._quota_ticks / q if q > 0 else 0.0)
        if wc.condition_type == "contested_majority":
            # FRONTLINE (spec §3.9): own-perspective score margin (clip
            # ±2 keeps overshoot information), engaged share, and the
            # leader-signed persistence counter (clip ±1) — without the
            # counter the defender cannot distinguish "answer now or
            # lose" from "one round of slack" (SIEGE clock_frac lesson).
            s1, s2, engaged = self.contested_scores()
            lead_p1 = s1 - (s2 + wc.komi_cells)
            lead_self = float(lead_p1 if p == 1 else -lead_p1)
            m = max(1, wc.end_margin)
            metadata.append(float(np.clip(lead_self / m, -2.0, 2.0)))
            metadata.append(engaged / self.topo.num_active_cells)
            streak_self = self._cm_streak if p == 1 else -self._cm_streak
            metadata.append(float(np.clip(streak_self / 3.0, -1.0, 1.0)))
        metadata = np.array(metadata, dtype=np.float64)

        obs = np.concatenate([owner_encoded, self.board_values, metadata])
        return obs

    def _compute_rewards(self) -> None:
        """Compute final rewards. Winner +1, loser -1, draw 0/0."""
        self._last_rewards = np.zeros(2, dtype=np.float64)
        if self._winner is not None:
            self._last_rewards[self._winner - 1] = 1.0
            self._last_rewards[2 - self._winner] = -1.0
        # Draw: both remain 0.0

    def _info(self) -> dict:
        """Build the info dict."""
        return {
            "step": self.step_count,
            "player": self.current_player - 1,
            "winner": (self._winner - 1) if self._winner is not None else None,
        }
