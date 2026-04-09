"""Training module for the Genesis Creativity Engine.

Provides PPO-based self-play training for two-player games generated
by the game engine.
"""

from training.agent import PolicyNetwork
from training.trainer import SelfPlayTrainer
from training.utils import RandomAgent, play_game, evaluate_agents

__all__ = [
    "PolicyNetwork",
    "SelfPlayTrainer",
    "RandomAgent",
    "play_game",
    "evaluate_agents",
]
