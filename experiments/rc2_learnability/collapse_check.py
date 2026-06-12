import sys
from pathlib import Path
sys.path.insert(0, '/Users/jamesbrowne/aigame')
import numpy as np
from config import MetricsConfig, TrainingConfig
from game_engine.factory import create_engine
from training.trainer import SelfPlayTrainer
from training.utils import RandomAgent
from experiments.rc2_descriptor_v2.run_probe import load_roster_game

game = load_roster_game("d4015a646ae3")
tr = SelfPlayTrainer(game, TrainingConfig(training_budget=3000, eval_episodes=100),
                     MetricsConfig(learning_curve_checkpoints=2), seed=42)
tr.train()

# Play 20 games vs random, count trained agent's pass actions
for label, (a_tr, a_rnd, seat) in {
    "trained as P1": (tr.agents[0], RandomAgent(seed=1), 0),
    "trained as P2": (tr.agents[1], RandomAgent(seed=2), 1),
}.items():
    passes = moves = 0
    lengths = []
    for g in range(10):
        engine = create_engine(tr.game)
        obs = engine.reset()
        done = False
        steps = 0
        while not done and steps < 400:
            cur = engine.get_current_player()
            legal = engine.get_legal_actions()
            if not legal:
                break
            agent = a_tr if cur == seat else RandomAgent(seed=100 + g)
            act, _, _ = agent.select_action(obs, legal_actions=legal,
                                            deterministic=False)
            if cur == seat:
                moves += 1
                if act == engine.total_cells:
                    passes += 1
            obs, _, done, _ = engine.step(act)
            steps += 1
        lengths.append(steps)
    print(f"{label}: pass share {passes}/{moves} = {passes/max(1,moves):.2f}, "
          f"mean len {np.mean(lengths):.0f}")
