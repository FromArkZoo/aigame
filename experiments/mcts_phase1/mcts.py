"""Phase-1 MCTS evaluator — PUCT with virtual loss, PPO net as prior+value.

Wraps an existing pair of trained ``PolicyNetwork`` instances (one per
seat, as produced by ``training.trainer.SelfPlayTrainer``) and uses them
to seed a PUCT search at evaluation time. The search root is always the
*live* state of a shared :class:`GameEngineV2` — :meth:`MCTSAgent.select_action`
clones from that engine, so the existing ``training.utils.play_game``
loop drives a single mutable engine while MCTSAgent does read-only
search clones underneath.

Design choices (Phase 1, deliberately minimal):
- PUCT formula:  Q + c_puct * P * sqrt(sum_N) / (1 + N), c_puct = 1.5.
- Virtual loss applied on descent (child.N += VL, child.W -= VL) and
  reverted on backup. Default VL = 1. Single-leaf evaluation per sim, so
  VL is a no-op in practice — kept correct so the code can be lifted to
  batched-leaf evaluation later without redoing the bookkeeping.
- Two-player zero-sum sign convention: each *child* edge stores W from
  the perspective of the parent's side-to-move. Backup flips sign every
  level. At a leaf, the net's value head is treated as "value to the
  player whose turn it is at the leaf" — so the first sign flip happens
  when applying to the deepest child edge.
- Net value clipped to [-1, 1]. PPO's value head is trained as a value
  function for advantage estimates, not as a calibrated [-1, 1] eval, so
  clipping rather than tanh keeps the magnitude honest near the bounds.
- Prior: softmax of legal-masked logits; illegal actions get 0 prior.
- Skips simultaneous-turn games (caller's responsibility).
- Deterministic root selection at temperature 0 (argmax visits, lowest
  action index on ties). No Dirichlet noise — this is an eval harness,
  not a self-play data generator.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import torch

from game_engine.engine_v2 import GameEngineV2
from training.agent import PolicyNetwork


C_PUCT_DEFAULT = 1.5
VIRTUAL_LOSS_DEFAULT = 1
DIRICHLET_ALPHA_DEFAULT = 0.3   # AlphaZero default; α≈10/num_legal_actions also reasonable
DIRICHLET_EPS_DEFAULT = 0.0     # 0 = pure prior (deterministic); 0.25 = AlphaZero self-play default
LEAF_EVAL_DEFAULT = "value"     # "value" = net value head; "rollout" = random playout to terminal
ROLLOUT_MAX_STEPS = 200          # cap on rollout length (matches typical max_game_steps)


# ----------------------------------------------------------------------
# Node
# ----------------------------------------------------------------------

@dataclass
class _Node:
    """One node in the PUCT tree.

    A node is created in unexpanded state when it's first reached as a
    child during selection. Expansion happens on first visit at the leaf
    of the descent, by running the net once on the engine state.

    For terminal nodes (engine.done == True at construction time),
    ``is_terminal=True`` and ``terminal_value`` is set from the engine's
    final rewards as "value to player_to_move at this node". After
    terminal, no children are created; the leaf evaluation step just
    returns terminal_value.
    """
    player_to_move: int
    expanded: bool = False
    is_terminal: bool = False
    terminal_value: float = 0.0
    # Per-action arrays, populated at expansion. Indexed positionally.
    actions: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.int64))
    priors: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.float32))
    N: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.float32))
    W: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.float32))
    # Children dict: action -> _Node, populated lazily on descent.
    children: dict = field(default_factory=dict)


# ----------------------------------------------------------------------
# Net wrapper
# ----------------------------------------------------------------------

class _NetEvaluator:
    """Thin wrapper that exposes (prior_over_legal, value_for_to_move).

    Holds one PolicyNetwork per seat. At each query the net of the
    *current* player is used. Values are clipped to [-1, 1].
    """

    def __init__(self, nets: list[PolicyNetwork]):
        if len(nets) != 2:
            raise ValueError("Expected exactly 2 nets (one per seat).")
        self.nets = nets
        for net in self.nets:
            net.eval()

    @torch.no_grad()
    def __call__(
        self, obs: np.ndarray, legal_actions: list[int], to_move: int,
    ) -> tuple[np.ndarray, float]:
        net = self.nets[to_move]
        x = torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0)
        mask = torch.zeros(1, net.num_actions, dtype=torch.bool)
        mask[0, legal_actions] = True
        logits, value = net.forward(x, legal_mask=mask)
        # Softmax over legal-masked logits gives the prior. Illegal
        # entries are -inf, so they go to 0 cleanly.
        probs = torch.softmax(logits.squeeze(0), dim=-1).numpy()
        prior_over_legal = probs[legal_actions].astype(np.float32)
        # Defensive renorm: with a fully-saturated softmax, all-zero is
        # possible when every legal logit is -inf (shouldn't happen
        # given the mask construction, but cheap to guard).
        s = prior_over_legal.sum()
        if s > 0:
            prior_over_legal /= s
        else:
            prior_over_legal = np.full_like(prior_over_legal, 1.0 / len(legal_actions))
        v = float(value.item())
        if v > 1.0:
            v = 1.0
        elif v < -1.0:
            v = -1.0
        return prior_over_legal, v


# ----------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------

class MCTSEvaluator:
    """One PUCT search, parameterised by net pair + sim budget.

    ``search(root_engine, num_sims)`` runs ``num_sims`` simulations and
    returns the action with the highest visit count at the root. The
    root engine is never mutated; each simulation works on a clone.
    """

    def __init__(
        self,
        nets: list[PolicyNetwork],
        c_puct: float = C_PUCT_DEFAULT,
        virtual_loss: float = VIRTUAL_LOSS_DEFAULT,
        dirichlet_eps: float = DIRICHLET_EPS_DEFAULT,
        dirichlet_alpha: float = DIRICHLET_ALPHA_DEFAULT,
        leaf_eval: str = LEAF_EVAL_DEFAULT,
        rng: np.random.Generator | None = None,
    ):
        self.evaluator = _NetEvaluator(nets)
        self.c_puct = c_puct
        self.virtual_loss = virtual_loss
        self.dirichlet_eps = dirichlet_eps
        self.dirichlet_alpha = dirichlet_alpha
        self.leaf_eval = leaf_eval
        self.rng = rng if rng is not None else np.random.default_rng()

    def search(self, root_engine: GameEngineV2, num_sims: int) -> int:
        if root_engine.done:
            raise ValueError("Cannot search from a terminal state.")

        root = _Node(player_to_move=root_engine.get_current_player())
        # Expand root immediately so that the very first sim's selection
        # has children to choose from.
        self._expand(root, root_engine)

        # Optional Dirichlet noise at root only (AlphaZero self-play
        # convention). Used here as a per-game variance source for
        # ladder-mode evaluation, where both sides are deterministic
        # MCTS and would otherwise produce identical games. Eps=0 (the
        # default) is a no-op — random/greedy opponents already have
        # their own per-game randomness.
        if self.dirichlet_eps > 0 and len(root.priors) > 0:
            noise = self.rng.dirichlet(
                [self.dirichlet_alpha] * len(root.priors)
            ).astype(np.float32)
            root.priors = (1.0 - self.dirichlet_eps) * root.priors \
                + self.dirichlet_eps * noise

        for _ in range(num_sims):
            self._simulate(root, root_engine)

        # Temperature-0 root policy: argmax visits, lowest action index
        # breaks ties (np.argmax does this naturally on equal floats).
        best_idx = int(np.argmax(root.N))
        return int(root.actions[best_idx])

    # ------------------------------------------------------------------
    # One simulation
    # ------------------------------------------------------------------

    def _simulate(self, root: _Node, root_engine: GameEngineV2) -> None:
        engine = root_engine.clone()
        node = root
        # Path: list of (parent_node, child_idx) pairs. Each entry says
        # "we descended from parent_node via its child at index child_idx".
        path: list[tuple[_Node, int]] = []

        # Selection: descend until we hit an unexpanded node OR a node
        # whose expansion produced no legal actions (shouldn't happen
        # since terminal nodes are caught first).
        while node.expanded and not node.is_terminal:
            child_idx = self._select_child_puct(node)
            action = int(node.actions[child_idx])

            # Apply virtual loss to discourage sibling sims from picking
            # the same path. Since we run sims serially this is a no-op
            # but keeps the bookkeeping correct under a future batched
            # leaf-eval design.
            node.N[child_idx] += self.virtual_loss
            node.W[child_idx] -= self.virtual_loss

            path.append((node, child_idx))

            # Step the cloned engine. Treat the resulting state as the
            # child node — create it if first visit.
            engine.step(action)

            child = node.children.get(action)
            if child is None:
                # If terminal, mark with terminal_value from the engine's
                # final rewards (value to *next* player to move, which is
                # the convention we backup against).
                if engine.done:
                    rewards = engine._last_rewards  # shape (2,)
                    # After engine.done the "current_player" still refers
                    # to whoever was about to move (engine doesn't
                    # advance turn at terminal). Use that as the leaf's
                    # to-move slot for sign-convention purposes.
                    next_to_move = engine.get_current_player()
                    leaf_value = float(rewards[next_to_move])
                    child = _Node(
                        player_to_move=next_to_move,
                        is_terminal=True,
                        terminal_value=leaf_value,
                    )
                else:
                    child = _Node(player_to_move=engine.get_current_player())
                node.children[action] = child
            node = child

        # Evaluation at leaf
        if node.is_terminal:
            leaf_value = node.terminal_value
        else:
            leaf_value = self._expand(node, engine)

        # Backup: walk the path from the deepest edge upward, flipping
        # the sign each level. The leaf's value is from leaf-player POV;
        # the deepest edge stores W from parent-of-leaf POV (= -leaf POV).
        sign = -1.0
        for parent, child_idx in reversed(path):
            # Revert virtual loss and apply real visit + value.
            parent.N[child_idx] += 1 - self.virtual_loss
            parent.W[child_idx] += sign * leaf_value + self.virtual_loss
            sign = -sign

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _expand(self, node: _Node, engine: GameEngineV2) -> float:
        """Expand ``node`` using the net for prior. Leaf value is either
        the net's value head or a random rollout, per ``leaf_eval``."""
        legal = engine.get_legal_actions()
        if len(legal) == 0:
            node.is_terminal = True
            node.terminal_value = 0.0
            node.expanded = True
            return 0.0
        obs = engine._observe()
        prior, net_value = self.evaluator(obs, legal, node.player_to_move)
        node.actions = np.asarray(legal, dtype=np.int64)
        node.priors = prior
        node.N = np.zeros(len(legal), dtype=np.float32)
        node.W = np.zeros(len(legal), dtype=np.float32)
        node.expanded = True
        if self.leaf_eval == "rollout":
            return self._rollout(engine.clone(), node.player_to_move)
        return net_value

    def _rollout(self, engine: GameEngineV2, leaf_player: int) -> float:
        """Play a uniform-random game from ``engine`` to terminal.
        Returns final value from ``leaf_player``'s perspective in [-1, 1]."""
        steps = 0
        while not engine.done and steps < ROLLOUT_MAX_STEPS:
            legal = engine.get_legal_actions()
            if len(legal) == 0:
                break
            action = int(legal[self.rng.integers(0, len(legal))])
            engine.step(action)
            steps += 1
        if not engine.done:
            return 0.0  # rollout cap hit → treat as draw
        return float(engine._last_rewards[leaf_player])

    def _select_child_puct(self, node: _Node) -> int:
        """Argmax over children of Q + c * P * sqrt(sum_N) / (1 + N)."""
        # Q from parent's POV: child stores W as (sum of leaf values
        # from parent's POV). Q = W/N when N > 0, else 0.
        N = node.N
        W = node.W
        sum_N = float(N.sum())
        sqrtN = math.sqrt(max(sum_N, 1.0))
        # Avoid divide-by-zero with the +1 term in the U denominator.
        Q = np.where(N > 0, W / np.maximum(N, 1e-8), 0.0)
        U = self.c_puct * node.priors * sqrtN / (1.0 + N)
        score = Q + U
        return int(np.argmax(score))


# ----------------------------------------------------------------------
# Agent adapter for play_game
# ----------------------------------------------------------------------

class MCTSAgent:
    """Plug into ``training.utils.play_game`` as agent0 or agent1.

    Holds a reference to the live :class:`GameEngineV2` driving the
    play loop. ``select_action`` uses the engine's *current* state as
    the search root — caller must guarantee the engine is at the same
    state that produced ``obs``. ``play_game`` satisfies this naturally.
    """

    def __init__(
        self,
        engine: GameEngineV2,
        nets: list[PolicyNetwork],
        num_sims: int,
        c_puct: float = C_PUCT_DEFAULT,
        virtual_loss: float = VIRTUAL_LOSS_DEFAULT,
        dirichlet_eps: float = DIRICHLET_EPS_DEFAULT,
        dirichlet_alpha: float = DIRICHLET_ALPHA_DEFAULT,
        leaf_eval: str = LEAF_EVAL_DEFAULT,
        rng_seed: int | None = None,
    ):
        self.engine = engine
        rng = np.random.default_rng(rng_seed) if rng_seed is not None else None
        self.evaluator = MCTSEvaluator(
            nets, c_puct=c_puct, virtual_loss=virtual_loss,
            dirichlet_eps=dirichlet_eps, dirichlet_alpha=dirichlet_alpha,
            leaf_eval=leaf_eval, rng=rng,
        )
        self.num_sims = num_sims

    def select_action(
        self,
        obs: np.ndarray,
        legal_actions: list[int] | None = None,
        deterministic: bool = True,
    ) -> tuple[int, float, float]:
        action = self.evaluator.search(self.engine, self.num_sims)
        return action, 0.0, 0.0
