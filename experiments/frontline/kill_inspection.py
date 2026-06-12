"""KILL_INVALID inspection diagnostic — NOT a stage rerun; replaces no stage numbers.

Question: is the Stage-1 skill-gate kill (all 6 cells tvr 0.50-0.59 vs 0.75 floor)
an implementation error (PPO silently not learning) or genuine design arithmetic
(low skill ceiling at the registered budget)?

Probe: pinned cell E1p00_M8, seed 42 (Stage-1 measured tvr 0.55).
  1. UNTRAINED tvr baseline (expect ~0.50 if tvr harness is sound).
  2. Train budget 3000, capturing the trainer's own learning curve
     (episode, wr_vs_opp, wr_vs_random) — direct evidence of learning.
  3. TRAINED tvr with full outcome decomposition (wins/draws/losses,
     end-causes, lengths) — tests the draws-counted-as-losses cap.
  4. TRAINED tvr deterministic=True — tests whether stochastic eval masks
     a learned argmax policy.
"""
import sys, time, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from config import MetricsConfig, TrainingConfig
from game_engine.factory import create_engine
from training.trainer import SelfPlayTrainer
from training.utils import RandomAgent
from experiments.field_connect_probe.calibrate import play_game
from experiments.frontline.build_games import build_f


def tvr_detail(trainer, n=100, max_steps=400, deterministic=False):
    wins = draws = losses = 0
    lengths, causes = [], []
    half = n // 2
    for i in range(n):
        engine = create_engine(trainer.game)
        if i < half:
            a0, a1, seat = trainer.agents[0], RandomAgent(seed=9000 + i), 0
        else:
            a0, a1, seat = RandomAgent(seed=9000 + i), trainer.agents[1], 1
        winner, length, _ = play_game(engine, a0, a1,
                                      deterministic=deterministic,
                                      max_steps=max_steps)
        if winner is None:
            draws += 1
        elif winner == seat:
            wins += 1
        else:
            losses += 1
        lengths.append(length)
        causes.append("score_margin" if engine._ended_by_score_margin
                      else "double_pass" if engine._ended_by_double_pass
                      else "timeout" if engine._ended_by_max_turns else "other")
    return dict(tvr=wins / n, wins=wins, draws=draws, losses=losses,
                mean_len=float(np.mean(lengths)),
                causes={c: causes.count(c) / n for c in sorted(set(causes))})


game = build_f(1.0, 8)
cfg = TrainingConfig(training_budget=3000, eval_episodes=100)
trainer = SelfPlayTrainer(game, cfg, MetricsConfig(learning_curve_checkpoints=4),
                          seed=42)

print("UNTRAINED stochastic:", json.dumps(tvr_detail(trainer)), flush=True)

t0 = time.time()
result = trainer.train()
print(f"trained in {time.time() - t0:.0f}s", flush=True)
print("LEARNING CURVE (ep, wr_vs_opp, wr_vs_random):", flush=True)
for row in result["learning_curve"]:
    print(f"  {row}", flush=True)

print("TRAINED stochastic:  ", json.dumps(tvr_detail(trainer)), flush=True)
print("TRAINED deterministic:", json.dumps(tvr_detail(trainer, deterministic=True)),
      flush=True)
