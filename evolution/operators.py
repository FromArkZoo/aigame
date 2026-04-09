"""Mutation and crossover operators for game evolution.

Provides operators that work on ExprTree and GameDef objects to produce
offspring in the evolutionary loop.  All mutations deep-copy before
modifying so parents are never altered in place.
"""

from __future__ import annotations

import copy
import uuid
from typing import Optional

import numpy as np

from config import EvolutionConfig, GameConfig
from game_engine.representation import (
    ARITY,
    INTERNAL_OPS,
    LEAF_OPS,
    ExprTree,
    GameDef,
)

# Operator groups used when swapping an op for a compatible one.
_NUMERIC_INTERNAL_OPS: list[str] = [
    "+", "-", "*", "/safe",
    "abs", "neg",
    "mod", "clamp",
    "if_then_else",
]

_BOOLEAN_INTERNAL_OPS: list[str] = [
    ">", "<", "==",
    "and", "or", "not",
    "if_then_else",
]

_CONST_POOL: list[float] = [
    -2.0, -1.0, -0.5, 0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0,
]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _collect_nodes(tree: ExprTree) -> list[ExprTree]:
    """Return a flat list of every node in *tree* (pre-order)."""
    nodes: list[ExprTree] = [tree]
    for child in tree.children:
        nodes.extend(_collect_nodes(child))
    return nodes


def _collect_parents(tree: ExprTree) -> list[tuple[ExprTree, int]]:
    """Return ``(parent, child_index)`` for every non-root node.

    Useful for picking a random attachment point in the tree.
    """
    result: list[tuple[ExprTree, int]] = []
    for i, child in enumerate(tree.children):
        result.append((tree, i))
        result.extend(_collect_parents(child))
    return result


def _random_leaf(rng: np.random.Generator, state_dim: int) -> ExprTree:
    """Generate a random leaf node."""
    leaf_type = rng.choice(list(LEAF_OPS))
    if leaf_type == "const":
        val = float(rng.choice(_CONST_POOL))
        return ExprTree(op="const", value=val)
    if leaf_type == "state_var":
        idx = int(rng.integers(0, max(state_dim, 1)))
        return ExprTree(op="state_var", value=idx)
    if leaf_type == "action_var":
        return ExprTree(op="action_var")
    if leaf_type == "player_id":
        return ExprTree(op="player_id")
    return ExprTree(op="step")


def _random_subtree(
    rng: np.random.Generator,
    max_depth: int,
    state_dim: int,
    prefer_boolean: bool = False,
) -> ExprTree:
    """Build a random sub-tree using the *grow* method."""
    if max_depth <= 0 or (max_depth < 2 and rng.random() < 0.3):
        return _random_leaf(rng, state_dim)

    ops_pool = _BOOLEAN_INTERNAL_OPS if prefer_boolean else _NUMERIC_INTERNAL_OPS
    op = str(rng.choice(ops_pool))
    arity = ARITY[op]
    children = [
        _random_subtree(rng, max_depth - 1, state_dim, prefer_boolean=False)
        for _ in range(arity)
    ]
    return ExprTree(op=op, children=children)


def _compatible_ops(op: str) -> list[str]:
    """Return operators that have the same arity as *op*."""
    target_arity = ARITY[op]
    return [o for o in INTERNAL_OPS if ARITY[o] == target_arity and o != op]


def _clamp_state_var_indices(tree: ExprTree, state_dim: int) -> None:
    """Recursively adjust ``state_var`` indices so they stay in [0, state_dim)."""
    if tree.op == "state_var" and tree.value is not None:
        tree.value = int(tree.value) % max(state_dim, 1)
    for child in tree.children:
        _clamp_state_var_indices(child, state_dim)


# ======================================================================
# MutationOperator
# ======================================================================

class MutationOperator:
    """Mutation operators for game evolution."""

    def __init__(self, config: EvolutionConfig, rng: np.random.Generator) -> None:
        self.config = config
        self.rng = rng

    # ------------------------------------------------------------------
    # Tree-level mutations
    # ------------------------------------------------------------------

    def mutate_tree(self, tree: ExprTree, state_dim: int) -> ExprTree:
        """Mutate an expression tree.  Randomly choose one mutation:

        1. Point mutation   -- change a node's op to a compatible one
        2. Subtree replace  -- swap a random subtree with a new random one
        3. Constant perturb -- add Gaussian noise to constant values
        4. Growth           -- replace a leaf with a small subtree
        5. Shrink           -- replace a subtree with a child or leaf

        Returns a new (deep-copied) tree; the original is never modified.
        """
        tree = tree.copy()
        mutation_kind = int(self.rng.integers(0, 5))

        if mutation_kind == 0:
            self._point_mutation(tree, state_dim)
        elif mutation_kind == 1:
            tree = self._subtree_replacement(tree, state_dim)
        elif mutation_kind == 2:
            self._constant_perturbation(tree)
        elif mutation_kind == 3:
            tree = self._growth(tree, state_dim)
        else:
            tree = self._shrink(tree, state_dim)

        # Safety: make sure state_var indices are valid
        _clamp_state_var_indices(tree, state_dim)
        return tree

    # -- Point mutation ------------------------------------------------

    def _point_mutation(self, tree: ExprTree, state_dim: int) -> None:
        """Change one random internal node's op to another with the same arity."""
        nodes = _collect_nodes(tree)
        internal = [n for n in nodes if n.op in INTERNAL_OPS]
        if not internal:
            # Nothing to mutate -- perturb a constant instead
            self._constant_perturbation(tree)
            return

        node = internal[int(self.rng.integers(0, len(internal)))]
        alternatives = _compatible_ops(node.op)
        if alternatives:
            node.op = str(self.rng.choice(alternatives))

    # -- Subtree replacement -------------------------------------------

    def _subtree_replacement(self, tree: ExprTree, state_dim: int) -> ExprTree:
        """Replace a random subtree with a freshly generated one."""
        parents = _collect_parents(tree)
        if not parents:
            # The tree is a single leaf -- replace the whole thing
            return _random_subtree(self.rng, 3, state_dim)

        parent, idx = parents[int(self.rng.integers(0, len(parents)))]
        depth = int(self.rng.integers(1, 4))
        parent.children[idx] = _random_subtree(self.rng, depth, state_dim)
        return tree

    # -- Constant perturbation -----------------------------------------

    def _constant_perturbation(self, tree: ExprTree) -> None:
        """Add Gaussian noise to every constant in the tree."""
        nodes = _collect_nodes(tree)
        consts = [n for n in nodes if n.op == "const" and n.value is not None]
        if not consts:
            return
        for node in consts:
            noise = float(self.rng.normal(0.0, self.config.param_mutation_std))
            node.value = round(float(node.value) + noise, 4)

    # -- Growth --------------------------------------------------------

    def _growth(self, tree: ExprTree, state_dim: int) -> ExprTree:
        """Replace a random leaf with a small subtree."""
        nodes = _collect_nodes(tree)
        leaves = [n for n in nodes if n.op in LEAF_OPS]
        parents = _collect_parents(tree)

        # Build a mapping from id(child) -> (parent, child_index)
        child_to_parent: dict[int, tuple[ExprTree, int]] = {}
        for p, ci in parents:
            child_to_parent[id(p.children[ci])] = (p, ci)

        # Pick a random leaf that is NOT the root
        candidate_leaves = [l for l in leaves if id(l) in child_to_parent]
        if not candidate_leaves:
            # Only the root is a leaf -- replace it entirely
            return _random_subtree(self.rng, 2, state_dim)

        chosen = candidate_leaves[int(self.rng.integers(0, len(candidate_leaves)))]
        parent, ci = child_to_parent[id(chosen)]
        depth = int(self.rng.integers(1, 3))
        parent.children[ci] = _random_subtree(self.rng, depth, state_dim)
        return tree

    # -- Shrink --------------------------------------------------------

    def _shrink(self, tree: ExprTree, state_dim: int) -> ExprTree:
        """Replace a random internal subtree with one of its children or a leaf."""
        parents = _collect_parents(tree)
        # Candidates: parent entries whose child is an internal node
        internal_parents = [
            (p, ci) for (p, ci) in parents if p.children[ci].op in INTERNAL_OPS
        ]
        if not internal_parents:
            return tree  # nothing to shrink

        parent, ci = internal_parents[int(self.rng.integers(0, len(internal_parents)))]
        subtree = parent.children[ci]

        if subtree.children:
            # Replace with one of the subtree's children
            replacement = subtree.children[int(self.rng.integers(0, len(subtree.children)))]
        else:
            replacement = _random_leaf(self.rng, state_dim)

        parent.children[ci] = replacement
        return tree

    # ------------------------------------------------------------------
    # Game-level mutations
    # ------------------------------------------------------------------

    def mutate_game(self, game: GameDef) -> GameDef:
        """Mutate a game definition.  Randomly apply one or more of:

        1. Mutate transition trees
        2. Mutate termination tree
        3. Mutate reward tree
        4. Change state dimension (add/remove a dimension)
        5. Add/remove an action
        6. Change observation type/mask

        Returns a new GameDef with a new ``game_id`` and parent reference
        stored in ``metadata``.
        """
        child = game.copy()
        new_id = uuid.uuid4().hex[:12]
        generation = child.metadata.get("generation", 0) + 1

        # Decide which mutations to apply (at least one)
        mutation_flags = self.rng.random(6)
        # Ensure at least one fires
        if not any(f < 0.5 for f in mutation_flags):
            mutation_flags[int(self.rng.integers(0, 6))] = 0.0

        mutation_types: list[str] = []

        # 1. Mutate transition trees
        if mutation_flags[0] < 0.5:
            mutation_types.append("transition")
            action_idx = int(self.rng.integers(0, child.num_actions))
            dim_idx = int(self.rng.integers(0, child.state_dim))
            child.transition_trees[action_idx][dim_idx] = self.mutate_tree(
                child.transition_trees[action_idx][dim_idx],
                child.state_dim,
            )

        # 2. Mutate termination tree
        if mutation_flags[1] < 0.5:
            mutation_types.append("termination")
            child.termination_tree = self.mutate_tree(
                child.termination_tree, child.state_dim,
            )

        # 3. Mutate reward tree
        if mutation_flags[2] < 0.5:
            mutation_types.append("reward")
            child.reward_tree = self.mutate_tree(
                child.reward_tree, child.state_dim,
            )

        # 4. Change state dimension
        if mutation_flags[3] < 0.15:  # rarer -- structural change
            mutation_types.append("state_dim")
            self._mutate_state_dim(child)

        # 5. Add/remove action
        if mutation_flags[4] < 0.15:  # rarer -- structural change
            mutation_types.append("action")
            self._mutate_actions(child)

        # 6. Change observation type/mask
        if mutation_flags[5] < 0.25:
            mutation_types.append("observation")
            self._mutate_observation(child)

        child.game_id = new_id
        child.metadata = {
            "parents": [game.game_id],
            "generation": generation,
            "mutation_types": mutation_types,
        }
        return child

    # -- Structural mutation helpers -----------------------------------

    def _mutate_state_dim(self, game: GameDef) -> None:
        """Add or remove a state dimension."""
        if game.state_dim <= 2:
            change = 1
        elif game.state_dim >= 16:
            change = -1
        else:
            change = int(self.rng.choice([-1, 1]))

        new_dim = game.state_dim + change

        if change == 1:
            # Add a dimension: append a new tree to each action's list
            for action_trees in game.transition_trees:
                new_tree = _random_subtree(self.rng, 2, new_dim)
                action_trees.append(new_tree)
        else:
            # Remove last dimension
            for action_trees in game.transition_trees:
                if len(action_trees) > 1:
                    action_trees.pop()

        game.state_dim = new_dim

        # Fix state_var indices in all trees
        for action_trees in game.transition_trees:
            for t in action_trees:
                _clamp_state_var_indices(t, new_dim)
        _clamp_state_var_indices(game.termination_tree, new_dim)
        _clamp_state_var_indices(game.reward_tree, new_dim)

        # Update observation mask if needed
        if game.observation_mask is not None:
            self._resize_observation_mask(game, new_dim)

    def _mutate_actions(self, game: GameDef) -> None:
        """Add or remove an action."""
        if game.num_actions <= 2:
            change = 1
        elif game.num_actions >= 10:
            change = -1
        else:
            change = int(self.rng.choice([-1, 1]))

        if change == 1:
            # Add a new action: generate random transition trees for it
            new_action_trees: list[ExprTree] = []
            for _d in range(game.state_dim):
                new_action_trees.append(
                    _random_subtree(self.rng, 2, game.state_dim)
                )
            game.transition_trees.append(new_action_trees)
            game.num_actions += 1
        else:
            # Remove a random action
            idx = int(self.rng.integers(0, game.num_actions))
            game.transition_trees.pop(idx)
            game.num_actions -= 1

    def _mutate_observation(self, game: GameDef) -> None:
        """Tweak observation type or mask."""
        obs_types = ["full", "partial", "asymmetric"]
        new_type = str(self.rng.choice(obs_types))
        game.observation_type = new_type

        if new_type == "full":
            game.observation_mask = None
        elif new_type == "partial":
            mask = (self.rng.random(game.state_dim) > 0.3).astype(np.float64)
            if mask.sum() == 0:
                mask[0] = 1.0
            game.observation_mask = mask
        else:  # asymmetric
            mask = (self.rng.random((game.num_players, game.state_dim)) > 0.3).astype(
                np.float64
            )
            for p in range(game.num_players):
                if mask[p].sum() == 0:
                    mask[p, 0] = 1.0
            game.observation_mask = mask

    def _resize_observation_mask(self, game: GameDef, new_dim: int) -> None:
        """Resize the observation mask after a state-dim change."""
        if game.observation_mask is None:
            return
        old_mask = game.observation_mask
        if old_mask.ndim == 1:
            # Partial: 1-D mask
            if new_dim > len(old_mask):
                game.observation_mask = np.concatenate(
                    [old_mask, np.ones(new_dim - len(old_mask))]
                )
            else:
                game.observation_mask = old_mask[:new_dim]
        elif old_mask.ndim == 2:
            # Asymmetric: (num_players, state_dim)
            nplayers = old_mask.shape[0]
            old_dim = old_mask.shape[1]
            if new_dim > old_dim:
                pad = np.ones((nplayers, new_dim - old_dim))
                game.observation_mask = np.concatenate([old_mask, pad], axis=1)
            else:
                game.observation_mask = old_mask[:, :new_dim]


# ======================================================================
# CrossoverOperator
# ======================================================================

class CrossoverOperator:
    """Crossover operators for combining two games."""

    def __init__(self, config: EvolutionConfig, rng: np.random.Generator) -> None:
        self.config = config
        self.rng = rng

    # ------------------------------------------------------------------
    # Tree-level crossover
    # ------------------------------------------------------------------

    def crossover_trees(self, tree_a: ExprTree, tree_b: ExprTree) -> ExprTree:
        """Subtree crossover between two expression trees.

        Pick a random node in *tree_a*, replace it with a random subtree
        copied from *tree_b*.  Returns a new tree (deep-copied); originals
        are never modified.
        """
        offspring = tree_a.copy()

        # Get a random subtree from tree_b to donate
        donor_nodes = _collect_nodes(tree_b)
        donor = donor_nodes[int(self.rng.integers(0, len(donor_nodes)))].copy()

        # Find an attachment point in the offspring
        parents = _collect_parents(offspring)
        if not parents:
            # offspring is a single leaf -- replace entirely
            return donor

        parent, ci = parents[int(self.rng.integers(0, len(parents)))]
        parent.children[ci] = donor
        return offspring

    # ------------------------------------------------------------------
    # Game-level crossover
    # ------------------------------------------------------------------

    def crossover_games(self, game_a: GameDef, game_b: GameDef) -> GameDef:
        """Combine two games into one offspring.

        Strategies (chosen randomly):
          1. **Component swap** -- take transition rules from one parent,
             termination/reward from the other.
          2. **Action mix** -- take some actions' transition trees from
             each parent.
          3. **Tree crossover** -- apply subtree crossover on individual
             expression trees.

        Dimension mismatches are handled by adjusting to the smaller or
        randomly chosen dimension.

        Returns a new ``GameDef`` with both parents tracked in ``metadata``.
        """
        strategy = int(self.rng.integers(0, 3))

        # Decide target dimensions
        target_dim = self._resolve_state_dim(game_a, game_b)
        target_actions = self._resolve_num_actions(game_a, game_b)

        # Normalise copies
        a = self._normalise(game_a.copy(), target_dim, target_actions)
        b = self._normalise(game_b.copy(), target_dim, target_actions)

        if strategy == 0:
            child = self._component_swap(a, b)
            cross_type = "component_swap"
        elif strategy == 1:
            child = self._action_mix(a, b, target_actions)
            cross_type = "action_mix"
        else:
            child = self._tree_crossover(a, b, target_dim)
            cross_type = "tree_crossover"

        new_id = uuid.uuid4().hex[:12]
        generation = max(
            a.metadata.get("generation", 0),
            b.metadata.get("generation", 0),
        ) + 1

        child.game_id = new_id
        child.state_dim = target_dim
        child.num_actions = len(child.transition_trees)
        child.metadata = {
            "parents": [game_a.game_id, game_b.game_id],
            "generation": generation,
            "crossover_type": cross_type,
        }

        # Final safety pass on state_var indices
        for action_trees in child.transition_trees:
            for t in action_trees:
                _clamp_state_var_indices(t, target_dim)
        _clamp_state_var_indices(child.termination_tree, target_dim)
        _clamp_state_var_indices(child.reward_tree, target_dim)

        return child

    # -- Crossover strategies ------------------------------------------

    def _component_swap(self, a: GameDef, b: GameDef) -> GameDef:
        """Take transition rules from *a*, termination/reward from *b*
        (or vice-versa, randomly).
        """
        if self.rng.random() < 0.5:
            a, b = b, a

        child = a.copy()
        child.termination_tree = b.termination_tree.copy()
        child.reward_tree = b.reward_tree.copy()
        # Randomly pick observation from one parent
        if self.rng.random() < 0.5:
            child.observation_type = b.observation_type
            child.observation_mask = (
                b.observation_mask.copy() if b.observation_mask is not None else None
            )
        return child

    def _action_mix(self, a: GameDef, b: GameDef, target_actions: int) -> GameDef:
        """For each action slot, randomly take transition trees from *a* or *b*."""
        child = a.copy()
        for i in range(target_actions):
            if self.rng.random() < 0.5 and i < len(b.transition_trees):
                child.transition_trees[i] = copy.deepcopy(b.transition_trees[i])

        # Termination and reward: randomly pick a parent
        if self.rng.random() < 0.5:
            child.termination_tree = b.termination_tree.copy()
        if self.rng.random() < 0.5:
            child.reward_tree = b.reward_tree.copy()
        return child

    def _tree_crossover(self, a: GameDef, b: GameDef, target_dim: int) -> GameDef:
        """Apply subtree crossover on a subset of the game's expression trees."""
        child = a.copy()

        # Crossover some transition trees
        num_actions = len(child.transition_trees)
        num_to_cross = max(1, int(self.rng.integers(1, num_actions + 1)))
        action_indices = self.rng.choice(num_actions, size=num_to_cross, replace=False)
        for ai in action_indices:
            ai = int(ai)
            dim_idx = int(self.rng.integers(0, target_dim))
            if ai < len(b.transition_trees) and dim_idx < len(b.transition_trees[ai]):
                child.transition_trees[ai][dim_idx] = self.crossover_trees(
                    child.transition_trees[ai][dim_idx],
                    b.transition_trees[ai][dim_idx],
                )

        # Optionally crossover termination tree
        if self.rng.random() < 0.5:
            child.termination_tree = self.crossover_trees(
                child.termination_tree, b.termination_tree,
            )

        # Optionally crossover reward tree
        if self.rng.random() < 0.5:
            child.reward_tree = self.crossover_trees(
                child.reward_tree, b.reward_tree,
            )

        return child

    # -- Dimension resolution helpers ----------------------------------

    def _resolve_state_dim(self, a: GameDef, b: GameDef) -> int:
        """Pick the target state dimension for a crossover child."""
        if a.state_dim == b.state_dim:
            return a.state_dim
        # Randomly choose one parent's dimension, biased toward the smaller
        if self.rng.random() < 0.6:
            return min(a.state_dim, b.state_dim)
        return max(a.state_dim, b.state_dim)

    def _resolve_num_actions(self, a: GameDef, b: GameDef) -> int:
        """Pick the target action count for a crossover child."""
        if a.num_actions == b.num_actions:
            return a.num_actions
        if self.rng.random() < 0.5:
            return a.num_actions
        return b.num_actions

    def _normalise(
        self, game: GameDef, target_dim: int, target_actions: int,
    ) -> GameDef:
        """Pad or truncate a game's trees so it matches the target dimensions.

        This ensures both parents are structurally compatible before crossover.
        """
        # Adjust state dimension in transition trees
        for i, action_trees in enumerate(game.transition_trees):
            if len(action_trees) < target_dim:
                # Pad with random trees
                for _ in range(target_dim - len(action_trees)):
                    action_trees.append(
                        _random_subtree(self.rng, 2, target_dim)
                    )
            elif len(action_trees) > target_dim:
                game.transition_trees[i] = action_trees[:target_dim]

        # Adjust number of actions
        if len(game.transition_trees) < target_actions:
            for _ in range(target_actions - len(game.transition_trees)):
                new_action = [
                    _random_subtree(self.rng, 2, target_dim)
                    for _ in range(target_dim)
                ]
                game.transition_trees.append(new_action)
        elif len(game.transition_trees) > target_actions:
            game.transition_trees = game.transition_trees[:target_actions]

        game.state_dim = target_dim
        game.num_actions = target_actions

        # Fix all state_var references
        for action_trees in game.transition_trees:
            for t in action_trees:
                _clamp_state_var_indices(t, target_dim)
        _clamp_state_var_indices(game.termination_tree, target_dim)
        _clamp_state_var_indices(game.reward_tree, target_dim)

        # Fix observation mask
        if game.observation_mask is not None:
            if game.observation_mask.ndim == 1:
                if len(game.observation_mask) < target_dim:
                    game.observation_mask = np.concatenate([
                        game.observation_mask,
                        np.ones(target_dim - len(game.observation_mask)),
                    ])
                else:
                    game.observation_mask = game.observation_mask[:target_dim]
            elif game.observation_mask.ndim == 2:
                old_dim = game.observation_mask.shape[1]
                if old_dim < target_dim:
                    pad = np.ones(
                        (game.observation_mask.shape[0], target_dim - old_dim)
                    )
                    game.observation_mask = np.concatenate(
                        [game.observation_mask, pad], axis=1,
                    )
                else:
                    game.observation_mask = game.observation_mask[:, :target_dim]

        return game
