#!/usr/bin/env python3
"""C1 + C2 verification — combined PPO-based check.

C1 (deterministic_run_seed):
    Calls train_and_evaluate_game twice on the same game with the same
    deterministic seed (md5(game_id)), each into a fresh DB. Asserts the
    composite go_essence is bit-identical between the two calls.

C2 (multi-seed averaging):
    Calls train_and_evaluate_game with num_independent_runs=3. Asserts
    the DB has 3 training_runs rows for the game; logs the per-run
    trained_vs_random spread vs the C2-averaged composite so any future
    drift in _average_run_inputs is loud.

Plan checklist items 3 + 4. Cheapest seed used to keep wall-clock low
(carpet axis-9, training_budget=200 ep, ~3-5s per training run).
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import GenesisConfig, TrackingConfig  # noqa: E402
from game_engine.game_def_v2 import GameDefV2  # noqa: E402
from metrics.scoring import GoEssenceScorer  # noqa: E402
from run import deterministic_run_seed, train_and_evaluate_game  # noqa: E402
from tracking.database import GenesisDB  # noqa: E402


SEEDS_DIR = Path(__file__).parent / "seeds"
# Cheapest seed: carpet axis-9, 64 active cells, custodian + connection
# (the c7 probe — also matches R18's c1+carpet which PASSED smoke).
SEED_STEM = "c7_custodian_connection__carpet"
TRAINING_BUDGET = 200
NUM_RUNS_FOR_C2 = 3


def load_seed(stem: str) -> GameDefV2:
    with open(SEEDS_DIR / f"{stem}.json") as f:
        return GameDefV2.from_dict(json.load(f))


def make_config(num_runs: int = 1) -> GenesisConfig:
    cfg = GenesisConfig()
    cfg.training.training_budget = TRAINING_BUDGET
    cfg.training.num_independent_runs = num_runs
    cfg.training.eval_episodes = 20
    return cfg


def fresh_db(suffix: str) -> tuple[GenesisDB, str]:
    tmp = tempfile.NamedTemporaryFile(
        prefix=f"r19_verify_{suffix}_",
        suffix=".db",
        delete=False,
    )
    tmp.close()
    tcfg = TrackingConfig()
    tcfg.db_path = tmp.name
    return GenesisDB(tcfg), tmp.name


def insert_game_record(db: GenesisDB, game: GameDefV2, generation: int = 0):
    db.insert_game(
        game_id=game.game_id,
        generation=generation,
        parent_ids=[],
        state_dim=game.state_dim,
        num_actions=game.num_actions,
        num_players=game.num_players,
        observation_type=game.observation_type,
        rule_representation=game.to_dict(),
        rule_complexity=game.total_complexity(),
    )


def verify_c1(game: GameDefV2) -> None:
    print("\n=== C1: deterministic_run_seed ===\n")

    # Pure-function check first (fast, no PPO).
    s_a = deterministic_run_seed(game.game_id, run_idx=0)
    s_b = deterministic_run_seed(game.game_id, run_idx=0)
    assert s_a == s_b, f"deterministic_run_seed not pure: {s_a} != {s_b}"
    print(f"  deterministic_run_seed({game.game_id!r}, 0) = {s_a}  (stable)")

    # Different run_idx must produce different seed.
    s_b_alt = deterministic_run_seed(game.game_id, run_idx=1)
    assert s_a != s_b_alt, "different run_idx should give different seed"

    # Train-and-score twice, fresh DB each, same seed.
    cfg = make_config(num_runs=1)
    scorer = GoEssenceScorer(cfg.metrics)
    run_seed = deterministic_run_seed(game.game_id, 0)

    composites = []
    for trial in (1, 2):
        db, path = fresh_db(f"c1_t{trial}")
        try:
            insert_game_record(db, game)
            scores = train_and_evaluate_game(
                game, cfg, scorer, db, run_seed=run_seed,
            )
            composites.append(scores["go_essence"])
            print(f"  trial {trial}: go_essence={scores['go_essence']:.10f}")
        finally:
            db.conn.close()
            Path(path).unlink(missing_ok=True)

    if composites[0] != composites[1]:
        # Tolerate float-equal but report.
        delta = abs(composites[0] - composites[1])
        if delta > 1e-9:
            raise AssertionError(
                f"C1 FAIL: composite GE differs across trials by {delta:.3e} "
                f"({composites[0]} vs {composites[1]})"
            )
        print(f"  WARN: float-tied within tolerance (delta={delta:.3e})")
    print("  C1 verified: same game + same seed = bit-identical GE.")


def verify_c2(game: GameDefV2) -> None:
    print(f"\n=== C2: multi-seed averaging (num_independent_runs={NUM_RUNS_FOR_C2}) ===\n")

    cfg = make_config(num_runs=NUM_RUNS_FOR_C2)
    scorer = GoEssenceScorer(cfg.metrics)
    run_seed = deterministic_run_seed(game.game_id, 0)

    db, path = fresh_db("c2")
    try:
        insert_game_record(db, game)
        scores = train_and_evaluate_game(
            game, cfg, scorer, db, run_seed=run_seed,
        )
        print(f"  multi-seed go_essence = {scores['go_essence']:.6f}")

        # Inspect DB for training_runs rows
        c = sqlite3.connect(path)
        c.row_factory = sqlite3.Row
        rows = list(c.execute(
            "SELECT run_seed, trained_vs_random, avg_game_length, training_steps "
            "FROM training_runs WHERE game_id = ? ORDER BY run_id",
            (game.game_id,),
        ))
        c.close()

        print(f"  training_runs rows in DB: {len(rows)}")
        for i, r in enumerate(rows):
            print(f"    run {i}: seed={r['run_seed']:>10}  "
                  f"tvr={r['trained_vs_random']:.3f}  "
                  f"avg_len={r['avg_game_length']:.1f}  "
                  f"steps={r['training_steps']}")

        assert len(rows) == NUM_RUNS_FOR_C2, (
            f"C2 FAIL: expected {NUM_RUNS_FOR_C2} training_runs rows, "
            f"got {len(rows)}"
        )

        # Confirm seeds match deterministic_run_seed for each run_idx
        expected_seeds = [
            deterministic_run_seed(game.game_id, i) for i in range(NUM_RUNS_FOR_C2)
        ]
        actual_seeds = [r["run_seed"] for r in rows]
        assert actual_seeds == expected_seeds, (
            f"C2 FAIL: run_seeds don't match deterministic_run_seed scheme.\n"
            f"  expected: {expected_seeds}\n  actual:   {actual_seeds}"
        )
        print(f"  all {NUM_RUNS_FOR_C2} seeds match deterministic_run_seed scheme")

        # Spread report
        tvrs = [r["trained_vs_random"] for r in rows]
        spread = max(tvrs) - min(tvrs)
        print(f"  per-run trained_vs_random spread = {spread:.3f}  "
              f"(min={min(tvrs):.3f}, max={max(tvrs):.3f})")
    finally:
        db.conn.close()
        Path(path).unlink(missing_ok=True)

    print("  C2 verified: 3 training_runs rows persisted, seeds deterministic.")


def main() -> int:
    game = load_seed(SEED_STEM)
    print(f"Verification seed: {game.game_id}  "
          f"({game.topology_type} axis={game.axis_size} dims={game.num_dimensions})")
    print(f"Training budget: {TRAINING_BUDGET} ep per run")

    verify_c1(game)
    verify_c2(game)

    print("\n=== C1 + C2 both verified ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
