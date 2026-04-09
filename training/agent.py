"""Policy network for game playing agents."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.distributions import Categorical


class PolicyNetwork(nn.Module):
    """MLP policy network with separate policy and value heads for PPO."""

    def __init__(
        self,
        obs_dim: int,
        num_actions: int,
        hidden_dim: int = 64,
        num_hidden: int = 2,
    ):
        super().__init__()
        self.obs_dim = obs_dim
        self.num_actions = num_actions

        # --- shared trunk ---
        layers = []
        in_dim = obs_dim
        for _ in range(num_hidden):
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.ReLU())
            in_dim = hidden_dim
        self.trunk = nn.Sequential(*layers)

        # --- policy head (logits over actions) ---
        self.policy_head = nn.Linear(hidden_dim, num_actions)

        # --- value head (scalar state value) ---
        self.value_head = nn.Linear(hidden_dim, 1)

        # Orthogonal initialisation (standard for PPO)
        self._init_weights()

    # ------------------------------------------------------------------
    def _init_weights(self):
        for module in self.trunk:
            if isinstance(module, nn.Linear):
                nn.init.orthogonal_(module.weight, gain=np.sqrt(2))
                nn.init.zeros_(module.bias)
        nn.init.orthogonal_(self.policy_head.weight, gain=0.01)
        nn.init.zeros_(self.policy_head.bias)
        nn.init.orthogonal_(self.value_head.weight, gain=1.0)
        nn.init.zeros_(self.value_head.bias)

    # ------------------------------------------------------------------
    def forward(self, x: torch.Tensor, legal_mask: torch.Tensor | None = None):
        """Forward pass.

        Args:
            x: observation tensor of shape ``(batch, obs_dim)`` or ``(obs_dim,)``.
            legal_mask: optional boolean tensor of shape ``(batch, num_actions)``
                        or ``(num_actions,)`` where ``True`` means the action is
                        legal.  Illegal actions get ``-inf`` logits.

        Returns:
            action_logits: ``(batch, num_actions)``
            value: ``(batch, 1)``
        """
        h = self.trunk(x)
        logits = self.policy_head(h)

        if legal_mask is not None:
            # Mask illegal actions to -inf so softmax assigns 0 probability.
            legal_mask = legal_mask.to(dtype=torch.bool)
            logits = logits.masked_fill(~legal_mask, float("-inf"))

        value = self.value_head(h)
        return logits, value

    # ------------------------------------------------------------------
    @torch.no_grad()
    def select_action(
        self,
        obs: np.ndarray,
        legal_actions: list[int] | None = None,
        deterministic: bool = False,
    ) -> tuple[int, float, float]:
        """Choose an action from a single observation.

        Args:
            obs: numpy array of shape ``(obs_dim,)``.
            legal_actions: list of legal action indices.  If ``None`` all
                           actions are considered legal.
            deterministic: if ``True`` pick the argmax; otherwise sample.

        Returns:
            action (int), log_prob (float), value (float)
        """
        x = torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0)

        # Build legal mask
        mask = None
        if legal_actions is not None:
            mask = torch.zeros(1, self.num_actions, dtype=torch.bool)
            mask[0, legal_actions] = True

        logits, value = self.forward(x, legal_mask=mask)
        logits = logits.squeeze(0)  # (num_actions,)
        value = value.squeeze(0).item()

        dist = Categorical(logits=logits)
        if deterministic:
            action = logits.argmax().item()
        else:
            action = dist.sample().item()

        log_prob = dist.log_prob(torch.tensor(action)).item()
        return action, log_prob, value
