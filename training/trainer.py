"""Self-play PPO trainer for two-player games."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np
import torch
import torch.nn.functional as F
from torch.optim import Adam

from config import TrainingConfig, MetricsConfig
from training.agent import PolicyNetwork
from training.utils import RandomAgent, GreedyAgent, play_game, evaluate_agents

if TYPE_CHECKING:
    from game_engine.representation import GameDef
    from game_engine.game_def_v2 import GameDefV2


# ======================================================================
# Trajectory buffer
# ======================================================================

class _PlayerBuffer:
    """Accumulates transitions for one player across many episodes."""

    __slots__ = (
        "observations",
        "actions",
        "log_probs",
        "rewards",
        "dones",
        "values",
    )

    def __init__(self):
        self.clear()

    def clear(self):
        self.observations: list[np.ndarray] = []
        self.actions: list[int] = []
        self.log_probs: list[float] = []
        self.rewards: list[float] = []
        self.dones: list[bool] = []
        self.values: list[float] = []

    def append(
        self,
        obs: np.ndarray,
        action: int,
        log_prob: float,
        reward: float,
        done: bool,
        value: float,
    ):
        self.observations.append(obs)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
        self.dones.append(done)
        self.values.append(value)

    def __len__(self):
        return len(self.actions)


# ======================================================================
# SelfPlayTrainer
# ======================================================================

class SelfPlayTrainer:
    """Trains two agents via self-play using PPO (clipped surrogate).

    Each agent is a :class:`PolicyNetwork`.  Training alternates between
    collecting batches of full episodes and running PPO gradient updates
    for each player independently.
    """

    def __init__(
        self,
        game: "GameDef",
        config: TrainingConfig,
        metrics_config: MetricsConfig | None = None,
        seed: int = 42,
    ):
        self.game = game
        self.config = config
        self.metrics_config = metrics_config or MetricsConfig()
        self.seed = seed

        # Reproducibility
        self._set_seeds(seed)

        # One policy per player
        obs_dim = game.state_dim
        num_actions = game.num_actions
        self.agents: list[PolicyNetwork] = [
            PolicyNetwork(
                obs_dim=obs_dim,
                num_actions=num_actions,
                hidden_dim=config.hidden_dim,
                num_hidden=config.num_hidden_layers,
            )
            for _ in range(game.num_players)
        ]

        self.optimizers = [
            Adam(agent.parameters(), lr=config.learning_rate)
            for agent in self.agents
        ]

        # Random baseline for evaluation
        self.random_agent = RandomAgent(seed=seed)

        # Lazy-imported engine reference (avoids circular import at module
        # load time while the ``game_engine`` package is still being built).
        self._engine = None

    # ------------------------------------------------------------------
    # Seed helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _set_seeds(seed: int):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    # ------------------------------------------------------------------
    # Engine accessor (lazy)
    # ------------------------------------------------------------------

    @property
    def engine(self):
        if self._engine is None:
            from game_engine.factory import create_engine
            self._engine = create_engine(self.game)
        return self._engine

    # ------------------------------------------------------------------
    # Episode collection
    # ------------------------------------------------------------------

    def collect_episode(self) -> dict:
        """Play one full episode of self-play and return per-player data.

        Returns
        -------
        dict
            ``{
                "buffers": [_PlayerBuffer, _PlayerBuffer],
                "winner": int | None,
                "game_length": int,
            }``
        """
        engine = self.engine
        obs = engine.reset()
        done = False
        step = 0
        max_steps = getattr(self.game, "max_game_steps", 200)

        buffers = [_PlayerBuffer() for _ in range(self.game.num_players)]

        # Pending transitions: we store (obs, action, log_prob, value) now
        # and fill in reward+done when the *next* transition (or terminal
        # signal) arrives.
        pending: dict[int, dict | None] = {i: None for i in range(self.game.num_players)}

        is_simultaneous = self.game.turn_structure.turn_type == "simultaneous"

        while not done and step < max_steps:
            if is_simultaneous:
                # --- Simultaneous path: both players act per step ---
                legal_p1 = engine.get_legal_actions(player=1)
                legal_p2 = engine.get_legal_actions(player=2)
                if len(legal_p1) == 0 or len(legal_p2) == 0:
                    break

                # Both agents condition on the same observation.
                # This mimics real simultaneous play — neither knows
                # the other's choice when committing.
                action_p1, log_prob_p1, value_p1 = self.agents[0].select_action(
                    obs, legal_actions=legal_p1, deterministic=False,
                )
                action_p2, log_prob_p2, value_p2 = self.agents[1].select_action(
                    obs, legal_actions=legal_p2, deterministic=False,
                )

                next_obs, reward, done, info = engine.step_simultaneous(
                    action_p1, action_p2,
                )
                step += 1

                per_player_reward = self._unpack_reward(reward, 0)

                for pid, (act, lp, val) in enumerate([
                    (action_p1, log_prob_p1, value_p1),
                    (action_p2, log_prob_p2, value_p2),
                ]):
                    if pending[pid] is not None:
                        p = pending[pid]
                        buffers[pid].append(
                            obs=p["obs"],
                            action=p["action"],
                            log_prob=p["log_prob"],
                            reward=per_player_reward.get(pid, 0.0),
                            done=False,
                            value=p["value"],
                        )
                    pending[pid] = {
                        "obs": obs.copy() if isinstance(obs, np.ndarray) else np.array(obs),
                        "action": act,
                        "log_prob": lp,
                        "value": val,
                    }

                obs = next_obs
                continue

            # --- Alternating / multi_place path (existing behavior) ---
            current_player = engine.get_current_player()
            legal_actions = engine.get_legal_actions()

            if len(legal_actions) == 0:
                break

            action, log_prob, value = self.agents[current_player].select_action(
                obs, legal_actions=legal_actions, deterministic=False,
            )

            next_obs, reward, done, info = engine.step(action)
            step += 1

            # Resolve reward per player ---------------------------------
            per_player_reward = self._unpack_reward(reward, current_player)

            # If there was a pending transition for the current player,
            # commit it with *intermediate* reward (usually 0 unless the
            # engine emits per-step rewards).
            if pending[current_player] is not None:
                p = pending[current_player]
                buffers[current_player].append(
                    obs=p["obs"],
                    action=p["action"],
                    log_prob=p["log_prob"],
                    reward=per_player_reward.get(current_player, 0.0),
                    done=False,
                    value=p["value"],
                )

            # Store current transition as pending (reward finalised later)
            pending[current_player] = {
                "obs": obs.copy() if isinstance(obs, np.ndarray) else np.array(obs),
                "action": action,
                "log_prob": log_prob,
                "value": value,
            }

            obs = next_obs

        # ---- finalise pending transitions at episode end ----
        terminal_rewards = self._terminal_rewards(step, max_steps, done, obs)

        for pid in range(self.game.num_players):
            if pending[pid] is not None:
                p = pending[pid]
                buffers[pid].append(
                    obs=p["obs"],
                    action=p["action"],
                    log_prob=p["log_prob"],
                    reward=terminal_rewards.get(pid, 0.0),
                    done=True,
                    value=p["value"],
                )

        winner = self._winner_from_buffers(buffers)
        return {
            "buffers": buffers,
            "winner": winner,
            "game_length": step,
        }

    # ------------------------------------------------------------------
    # Reward helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unpack_reward(reward, current_player: int) -> dict:
        """Normalise engine reward into ``{player_id: float}``."""
        if isinstance(reward, dict):
            return {int(k): float(v) for k, v in reward.items()}
        if isinstance(reward, np.ndarray):
            return {i: float(reward[i]) for i in range(len(reward))}
        return {current_player: float(reward)}

    def _terminal_rewards(
        self, step: int, max_steps: int, done: bool, last_obs
    ) -> dict:
        """Compute terminal rewards for each player.

        If the game terminated naturally (``done=True``) the reward was
        already emitted by the engine in the last ``step`` call.  If it
        hit ``max_steps`` we assign 0 to both (draw penalty handled
        elsewhere if desired).
        """
        # Terminal rewards are already folded into the last step's reward
        # by the engine.  We give 0 extra here; the last pending
        # transition's reward was set from the engine in collect_episode.
        # If the game didn't terminate (max_steps), treat it as a draw.
        if done:
            return {i: 0.0 for i in range(self.game.num_players)}
        # Timed-out => draw; small negative to discourage stalling.
        return {i: -0.01 for i in range(self.game.num_players)}

    @staticmethod
    def _winner_from_buffers(buffers: list[_PlayerBuffer]) -> int | None:
        sums = [sum(b.rewards) for b in buffers]
        if len(sums) < 2:
            return None
        if sums[0] > sums[1]:
            return 0
        elif sums[1] > sums[0]:
            return 1
        return None

    # ------------------------------------------------------------------
    # GAE computation
    # ------------------------------------------------------------------

    @staticmethod
    def compute_returns(
        rewards: list[float],
        dones: list[bool],
        values: list[float],
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Compute GAE advantages and discounted returns.

        Args:
            rewards: per-step rewards.
            dones: per-step ``done`` flags.
            values: per-step value estimates.
            gamma: discount factor.
            gae_lambda: GAE lambda.

        Returns:
            returns: ``(T,)`` tensor of discounted returns.
            advantages: ``(T,)`` tensor of GAE advantages.
        """
        T = len(rewards)
        if T == 0:
            return torch.zeros(0), torch.zeros(0)

        advantages = torch.zeros(T)
        last_gae = 0.0

        for t in reversed(range(T)):
            if dones[t]:
                next_value = 0.0
            else:
                next_value = values[t + 1] if t + 1 < T else 0.0

            delta = rewards[t] + gamma * next_value - values[t]
            mask = 0.0 if dones[t] else 1.0
            last_gae = delta + gamma * gae_lambda * mask * last_gae
            advantages[t] = last_gae

        returns = advantages + torch.tensor(values, dtype=torch.float32)
        return returns, advantages

    # ------------------------------------------------------------------
    # PPO update
    # ------------------------------------------------------------------

    def ppo_update(
        self,
        player_idx: int,
        batch: dict,
        ppo_epochs: int = 4,
        mini_batch_size: int = 64,
    ) -> dict:
        """Perform one PPO update for a single player.

        ``batch`` must contain tensors:
            observations (N, obs_dim), actions (N,), old_log_probs (N,),
            returns (N,), advantages (N,).

        Returns a dict of loss statistics.
        """
        agent = self.agents[player_idx]
        optimizer = self.optimizers[player_idx]
        clip_eps = self.config.clip_epsilon
        entropy_coef = self.config.entropy_coef
        value_coef = 0.5

        obs_t = batch["observations"]
        act_t = batch["actions"]
        old_lp = batch["old_log_probs"]
        ret_t = batch["returns"]
        adv_t = batch["advantages"]

        # Normalise advantages
        if adv_t.numel() > 1:
            adv_t = (adv_t - adv_t.mean()) / (adv_t.std() + 1e-8)

        N = obs_t.size(0)
        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        num_updates = 0

        for _epoch in range(ppo_epochs):
            indices = torch.randperm(N)
            for start in range(0, N, mini_batch_size):
                end = min(start + mini_batch_size, N)
                mb_idx = indices[start:end]

                mb_obs = obs_t[mb_idx]
                mb_act = act_t[mb_idx]
                mb_old_lp = old_lp[mb_idx]
                mb_ret = ret_t[mb_idx]
                mb_adv = adv_t[mb_idx]

                logits, values = agent(mb_obs)
                dist = torch.distributions.Categorical(logits=logits)
                new_log_probs = dist.log_prob(mb_act)
                entropy = dist.entropy().mean()

                # Clipped surrogate objective
                ratio = torch.exp(new_log_probs - mb_old_lp)
                surr1 = ratio * mb_adv
                surr2 = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * mb_adv
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss (clipped is optional; using simple MSE here)
                value_loss = F.mse_loss(values.squeeze(-1), mb_ret)

                loss = policy_loss + value_coef * value_loss - entropy_coef * entropy

                optimizer.zero_grad()
                loss.backward()
                # Gradient clipping for stability
                torch.nn.utils.clip_grad_norm_(agent.parameters(), max_norm=0.5)
                optimizer.step()

                total_policy_loss += policy_loss.item()
                total_value_loss += value_loss.item()
                total_entropy += entropy.item()
                num_updates += 1

        n = max(num_updates, 1)
        return {
            "policy_loss": total_policy_loss / n,
            "value_loss": total_value_loss / n,
            "entropy": total_entropy / n,
        }

    # ------------------------------------------------------------------
    # Full training loop
    # ------------------------------------------------------------------

    def train(self) -> dict:
        """Run the full self-play PPO training loop.

        Returns
        -------
        dict
            ``learning_curve``: list of ``(episode, eval_winrate_vs_opponent,
            eval_winrate_vs_random)`` tuples.
            ``final_agents``: the trained :class:`PolicyNetwork` list.
            ``training_steps``: total environment steps taken.
        """
        cfg = self.config
        mcfg = self.metrics_config

        learning_curve: list[tuple[int, float, float]] = []
        total_env_steps = 0
        total_episodes = 0

        # How often to checkpoint the learning curve
        checkpoint_interval = max(1, cfg.training_budget // mcfg.learning_curve_checkpoints)

        # Collect in batches, then update
        batch_size = cfg.batch_size

        # Per-player accumulated buffers for the current batch
        player_buffers: list[_PlayerBuffer] = [
            _PlayerBuffer() for _ in range(self.game.num_players)
        ]

        for ep in range(1, cfg.training_budget + 1):
            episode_data = self.collect_episode()
            total_env_steps += episode_data["game_length"]
            total_episodes += 1

            # Merge episode buffers into batch buffers
            for pid in range(self.game.num_players):
                eb = episode_data["buffers"][pid]
                pb = player_buffers[pid]
                pb.observations.extend(eb.observations)
                pb.actions.extend(eb.actions)
                pb.log_probs.extend(eb.log_probs)
                pb.rewards.extend(eb.rewards)
                pb.dones.extend(eb.dones)
                pb.values.extend(eb.values)

            # ----- PPO update every batch_size episodes -----
            if ep % batch_size == 0 or ep == cfg.training_budget:
                for pid in range(self.game.num_players):
                    pb = player_buffers[pid]
                    if len(pb) == 0:
                        continue

                    returns, advantages = self.compute_returns(
                        pb.rewards, pb.dones, pb.values, gamma=cfg.gamma,
                    )

                    batch = {
                        "observations": torch.tensor(
                            np.array(pb.observations), dtype=torch.float32
                        ),
                        "actions": torch.tensor(pb.actions, dtype=torch.long),
                        "old_log_probs": torch.tensor(
                            pb.log_probs, dtype=torch.float32
                        ),
                        "returns": returns,
                        "advantages": advantages,
                    }

                    self.ppo_update(pid, batch, mini_batch_size=cfg.batch_size)
                    pb.clear()

            # ----- Learning-curve checkpoint -----
            if ep % checkpoint_interval == 0 or ep == cfg.training_budget:
                eval_stats = self.evaluate(num_episodes=cfg.eval_episodes)
                wr_vs_opp = eval_stats["p0_winrate"]
                wr_vs_rand = eval_stats["trained_vs_random_winrate"]
                learning_curve.append((ep, wr_vs_opp, wr_vs_rand))

        return {
            "learning_curve": learning_curve,
            "final_agents": self.agents,
            "training_steps": total_env_steps,
        }

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, num_episodes: int = 100) -> dict:
        """Evaluate trained agents.

        Plays half the episodes with normal seating and half with swapped
        seats so that ``p0_winrate`` measures genuine first-player advantage
        rather than which agent is slightly stronger.  With deterministic
        play, all games within the same seat assignment are identical, so
        seat-swapping is the only source of variation.

        Returns
        -------
        dict
            p0_winrate: fraction of games won by the first player (P1),
                regardless of which agent occupied that seat.
            p1_winrate, draw_rate, avg_game_length,
            trained_vs_random_winrate
        """
        from game_engine.factory import create_engine

        engine = create_engine(self.game)
        max_steps = getattr(self.game, "max_game_steps", 200)

        # --- agent[0] vs agent[1] with seat swapping ---
        # Track wins by *seat* (P1 = seat 0), not by agent identity.
        p1_wins = 0  # times the player in seat 0 won
        p2_wins = 0
        draws = 0
        total_length = 0
        half = num_episodes // 2

        for i in range(num_episodes):
            if i < half:
                # Normal: agent[0] as P1, agent[1] as P2
                a0, a1 = self.agents[0], self.agents[1]
            else:
                # Swapped: agent[1] as P1, agent[0] as P2
                a0, a1 = self.agents[1], self.agents[0]

            winner, length, _ = play_game(
                engine, a0, a1,
                deterministic=True,
                max_steps=max_steps,
            )
            total_length += length
            if winner is None:
                draws += 1
            elif winner == 0:
                p1_wins += 1  # seat 0 (P1) won
            else:
                p2_wins += 1  # seat 1 (P2) won

        n = max(num_episodes, 1)
        p0_wr = p1_wins / n
        p1_wr = p2_wins / n
        draw_rate = draws / n
        avg_len = total_length / n

        # --- trained agent vs random (both seats) ---
        rand_wins = 0
        rand_episodes = num_episodes
        rand_half = rand_episodes // 2

        for i in range(rand_episodes):
            if i < rand_half:
                # Trained as P1
                winner, _, _ = play_game(
                    engine, self.agents[0], self.random_agent,
                    deterministic=True, max_steps=max_steps,
                )
                if winner == 0:
                    rand_wins += 1
            else:
                # Trained as P2
                winner, _, _ = play_game(
                    engine, self.random_agent, self.agents[0],
                    deterministic=True, max_steps=max_steps,
                )
                if winner == 1:
                    rand_wins += 1

        trained_vs_random_wr = rand_wins / max(rand_episodes, 1)

        # --- heuristic seat-balance probe (random vs random, seat-swapped) ---
        # Trained agents can converge to mixed strategies that mask structural
        # first-mover bias (observed in R14 sim×CA: trained 50/50, random 98/2).
        # Random-vs-random can't adapt to cancel out structural bias, so it
        # exposes it. The result feeds into the R15 seat_balance metric.
        heur_p1_wins = 0
        heur_decisive = 0
        heur_episodes = max(20, num_episodes // 2)
        heur_half = heur_episodes // 2
        # Use two distinct RandomAgents so the seat-swap halves really are
        # different agents in different seats, mirroring the trained eval.
        heur_a = RandomAgent(seed=self.seed * 7 + 11)
        heur_b = RandomAgent(seed=self.seed * 7 + 23)
        for i in range(heur_episodes):
            a0, a1 = (heur_a, heur_b) if i < heur_half else (heur_b, heur_a)
            winner, _, _ = play_game(
                engine, a0, a1,
                deterministic=False,
                max_steps=max_steps,
            )
            if winner is not None:
                heur_decisive += 1
                if winner == 0:
                    heur_p1_wins += 1
        heuristic_p1_winrate = (heur_p1_wins / heur_decisive) if heur_decisive > 0 else 0.5

        # --- greedy seat-balance probe (R16) ---
        # Random-vs-random missed the class of bias that only surfaces
        # under competent play (R15 human-eval teams flagged this:
        # rank-3 Moore was 13/16/1 in random but 20/20 P1 under greedy).
        # Greedy-vs-greedy adds that dimension: a 1-ply densify heuristic
        # where both agents apply the same strategy from different seats.
        # A structural P1 advantage shows up as high P1 winrate here.
        greedy_p1_wins = 0
        greedy_decisive = 0
        greedy_episodes = max(20, num_episodes // 2)
        # Each game uses a fresh engine so state doesn't leak between episodes.
        for i in range(greedy_episodes):
            g_engine = create_engine(self.game)
            seed_offset = self.seed * 29 + 31 * i
            a0 = GreedyAgent(g_engine, player_num=1, seed=seed_offset)
            a1 = GreedyAgent(g_engine, player_num=2, seed=seed_offset + 7)
            winner, _, _ = play_game(
                g_engine, a0, a1,
                deterministic=False,
                max_steps=max_steps,
            )
            if winner is not None:
                greedy_decisive += 1
                if winner == 0:
                    greedy_p1_wins += 1
        greedy_p1_winrate = (greedy_p1_wins / greedy_decisive) if greedy_decisive > 0 else 0.5

        return {
            "p0_winrate": p0_wr,
            "p1_winrate": p1_wr,
            "draw_rate": draw_rate,
            "avg_game_length": avg_len,
            "trained_vs_random_winrate": trained_vs_random_wr,
            "heuristic_p1_winrate": heuristic_p1_winrate,
            "heuristic_decisive_rate": heur_decisive / max(heur_episodes, 1),
            "greedy_p1_winrate": greedy_p1_winrate,
            "greedy_decisive_rate": greedy_decisive / max(greedy_episodes, 1),
        }
