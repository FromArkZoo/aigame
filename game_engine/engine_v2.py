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

        # Board state
        self.board_owners: np.ndarray = np.zeros(self.total_cells, dtype=np.int8)
        self.board_values: np.ndarray = np.zeros(self.total_cells, dtype=np.float64)

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
        self.current_player = 1
        self.step_count = 0
        self.done = False
        self.piece_counts = [0, 0]
        self.placements_this_turn = 0
        self.consecutive_passes = 0
        self._winner = None
        self._last_rewards = np.zeros(2, dtype=np.float64)

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

        # Check win conditions (may set self.done and self._winner)
        if not self.done:
            self._check_win_conditions()

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
                # "anywhere" — no filtering

            actions.extend(candidates)

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
        if prev_owner != 0 and prev_owner != player:
            self.piece_counts[prev_owner - 1] -= 1

        # Place the piece
        self.board_owners[cell] = player
        if prev_owner != player:
            self.piece_counts[player - 1] += 1

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

    def _remove_group(self, group: set[int], owner: int) -> None:
        """Remove all pieces in a group from the board."""
        for cell in group:
            self.board_owners[cell] = 0
        self.piece_counts[owner - 1] -= max(0, len(group))

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

    def _propagate_influence(self, placed_cell: int) -> None:
        """Influence propagation: add strength * decay^distance to
        board_values for cells within radius. Positive for player 1,
        negative for player 2."""
        rule = self.game.propagation_rule
        radius = rule.radius
        strength = rule.strength
        decay = rule.decay
        sign = 1.0 if self.current_player == 1 else -1.0

        cells = self.topo.cells_within_radius(placed_cell, radius)
        for cell in cells:
            dist = self.topo.distance(placed_cell, cell)
            delta = strength * (decay ** dist)
            self.board_values[cell] += sign * delta

        # Clamp to prevent explosion
        np.clip(self.board_values, -100.0, 100.0, out=self.board_values)

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
        """End the game by comparing piece counts (majority rule)."""
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
        """End the game as a draw when both players passed consecutively.

        Previously this resolved via piece majority (same as max_turns),
        which allowed a leading player to stop placing and force a win
        without actually meeting the stated win condition. R13 and R14
        human evaluations saw this fire in ~30% of top-tier games.
        Treating the double-pass as a draw makes the win condition the
        only path to a decisive result.
        """
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
            "placements_this_turn": self.placements_this_turn,
            "consecutive_passes": self.consecutive_passes,
        }

    def _restore_state(self, saved: dict) -> None:
        """Restore mutable state from a snapshot."""
        self.board_owners[:] = saved["board_owners"]
        self.board_values[:] = saved["board_values"]
        self.current_player = saved["current_player"]
        self.piece_counts = saved["piece_counts"]
        self.placements_this_turn = saved["placements_this_turn"]
        self.consecutive_passes = saved["consecutive_passes"]

    # ------------------------------------------------------------------
    # Internal: observation and rewards
    # ------------------------------------------------------------------

    def _observe(self) -> np.ndarray:
        """Build the observation vector for the current player.

        Layout:
          [owner_encoded (total_cells), board_values (total_cells),
           step_frac, own_piece_frac, enemy_piece_frac]
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

        metadata = np.array([step_frac, own_frac, enemy_frac], dtype=np.float64)

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
