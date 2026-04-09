"""SQLite database for tracking all Genesis Creativity Engine results."""

import sqlite3
import json
import os
import statistics
from typing import List, Optional, Dict

from config import TrackingConfig


class GenesisDB:
    """SQLite database for tracking all Genesis engine results."""

    def __init__(self, config: TrackingConfig):
        self.config = config
        self.db_path = config.db_path
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create all required tables."""
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                generation INTEGER,
                parent_ids TEXT,
                state_dim INTEGER,
                num_actions INTEGER,
                num_players INTEGER,
                observation_type TEXT,
                rule_representation TEXT,
                rule_complexity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scores (
                game_id TEXT PRIMARY KEY,
                rule_simplicity REAL,
                strategic_depth REAL,
                non_triviality REAL,
                strategic_diversity REAL,
                go_essence REAL,
                elo REAL DEFAULT 1500.0,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            );

            CREATE TABLE IF NOT EXISTS training_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT,
                run_seed INTEGER,
                learning_curve TEXT,
                final_winrate REAL,
                trained_vs_random REAL,
                avg_game_length REAL,
                training_steps INTEGER,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            );

            CREATE TABLE IF NOT EXISTS generations (
                generation INTEGER PRIMARY KEY,
                population_size INTEGER,
                best_go_essence REAL,
                mean_go_essence REAL,
                median_go_essence REAL,
                std_go_essence REAL,
                best_game_id TEXT,
                score_distribution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_a_id TEXT,
                game_b_id TEXT,
                score_a REAL,
                score_b REAL,
                elo_a_after REAL,
                elo_b_after REAL,
                FOREIGN KEY (game_a_id) REFERENCES games(game_id),
                FOREIGN KEY (game_b_id) REFERENCES games(game_id)
            );
        ''')
        self.conn.commit()

    # ------------------------------------------------------------------
    # Insertions
    # ------------------------------------------------------------------

    def insert_game(self, game_id: str, generation: int, parent_ids: List[str],
                    state_dim: int, num_actions: int, num_players: int,
                    observation_type: str, rule_representation: dict,
                    rule_complexity: int):
        """Insert a new game record."""
        self.conn.execute(
            '''INSERT OR REPLACE INTO games
               (game_id, generation, parent_ids, state_dim, num_actions,
                num_players, observation_type, rule_representation, rule_complexity)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                game_id,
                generation,
                json.dumps(parent_ids),
                state_dim,
                num_actions,
                num_players,
                observation_type,
                json.dumps(rule_representation),
                rule_complexity,
            ),
        )
        self.conn.commit()

    def insert_scores(self, game_id: str, scores: dict):
        """Insert metric scores for a game.

        Expected keys in *scores*: rule_simplicity, strategic_depth,
        non_triviality, strategic_diversity, go_essence.
        Optional: elo.
        """
        self.conn.execute(
            '''INSERT OR REPLACE INTO scores
               (game_id, rule_simplicity, strategic_depth, non_triviality,
                strategic_diversity, go_essence, elo)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                game_id,
                scores.get("rule_simplicity", 0.0),
                scores.get("strategic_depth", 0.0),
                scores.get("non_triviality", 0.0),
                scores.get("strategic_diversity", 0.0),
                scores.get("go_essence", 0.0),
                scores.get("elo", 1500.0),
            ),
        )
        self.conn.commit()

    def insert_training_run(self, game_id: str, run_seed: int,
                            learning_curve: List[List[float]],
                            final_winrate: float, trained_vs_random: float,
                            avg_game_length: float, training_steps: int):
        """Insert a training run record.

        *learning_curve* is a list of [episode, winrate] pairs.
        """
        self.conn.execute(
            '''INSERT INTO training_runs
               (game_id, run_seed, learning_curve, final_winrate,
                trained_vs_random, avg_game_length, training_steps)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                game_id,
                run_seed,
                json.dumps(learning_curve),
                final_winrate,
                trained_vs_random,
                avg_game_length,
                training_steps,
            ),
        )
        self.conn.commit()

    def insert_generation(self, generation: int, population_size: int,
                          scores: List[float]):
        """Insert generation-level statistics computed from *scores*.

        *scores* is a list of Go Essence values for every game in the
        generation.  Statistics (best, mean, median, std) are derived
        automatically.
        """
        if not scores:
            best = mean = median = std = 0.0
            best_game_id = None
        else:
            best = max(scores)
            mean = statistics.mean(scores)
            median = statistics.median(scores)
            std = statistics.stdev(scores) if len(scores) > 1 else 0.0
            best_game_id = None  # caller can update via separate query

        # Try to find the best game_id for this generation
        row = self.conn.execute(
            '''SELECT g.game_id FROM games g
               JOIN scores s ON g.game_id = s.game_id
               WHERE g.generation = ?
               ORDER BY s.go_essence DESC LIMIT 1''',
            (generation,),
        ).fetchone()
        if row:
            best_game_id = row["game_id"]

        self.conn.execute(
            '''INSERT OR REPLACE INTO generations
               (generation, population_size, best_go_essence, mean_go_essence,
                median_go_essence, std_go_essence, best_game_id, score_distribution)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                generation,
                population_size,
                best,
                mean,
                median,
                std,
                best_game_id,
                json.dumps(scores),
            ),
        )
        self.conn.commit()

    def insert_match(self, game_a_id: str, game_b_id: str,
                     score_a: float, score_b: float,
                     elo_a_after: float, elo_b_after: float):
        """Insert a match record between two games."""
        self.conn.execute(
            '''INSERT INTO matches
               (game_a_id, game_b_id, score_a, score_b, elo_a_after, elo_b_after)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (game_a_id, game_b_id, score_a, score_b, elo_a_after, elo_b_after),
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_game(self, game_id: str) -> Optional[dict]:
        """Get full game record including scores.

        Returns a dict with all columns from *games* and *scores* merged,
        or ``None`` if the game does not exist.
        """
        row = self.conn.execute(
            '''SELECT g.*, s.rule_simplicity, s.strategic_depth,
                      s.non_triviality, s.strategic_diversity,
                      s.go_essence, s.elo
               FROM games g
               LEFT JOIN scores s ON g.game_id = s.game_id
               WHERE g.game_id = ?''',
            (game_id,),
        ).fetchone()
        if row is None:
            return None
        result = dict(row)
        # Deserialise JSON fields
        if result.get("parent_ids"):
            result["parent_ids"] = json.loads(result["parent_ids"])
        if result.get("rule_representation"):
            result["rule_representation"] = json.loads(result["rule_representation"])
        return result

    def get_top_games(self, n: int = 20) -> List[dict]:
        """Get top *n* games ordered by Go Essence score descending."""
        rows = self.conn.execute(
            '''SELECT g.*, s.rule_simplicity, s.strategic_depth,
                      s.non_triviality, s.strategic_diversity,
                      s.go_essence, s.elo
               FROM games g
               JOIN scores s ON g.game_id = s.game_id
               ORDER BY s.go_essence DESC
               LIMIT ?''',
            (n,),
        ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            if d.get("parent_ids"):
                d["parent_ids"] = json.loads(d["parent_ids"])
            if d.get("rule_representation"):
                d["rule_representation"] = json.loads(d["rule_representation"])
            results.append(d)
        return results

    def get_generation_stats(self) -> List[dict]:
        """Get stats for all generations ordered by generation number."""
        rows = self.conn.execute(
            '''SELECT * FROM generations ORDER BY generation ASC'''
        ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            if d.get("score_distribution"):
                d["score_distribution"] = json.loads(d["score_distribution"])
            results.append(d)
        return results

    def get_lineage(self, game_id: str) -> List[dict]:
        """Trace evolutionary ancestry of a game.

        Returns a list of game dicts starting from the requested game
        and walking back through parent_ids until no more parents are
        found.  Each entry includes scores when available.
        """
        lineage: List[dict] = []
        visited: set = set()
        queue = [game_id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            game = self.get_game(current_id)
            if game is None:
                continue
            lineage.append(game)
            parents = game.get("parent_ids")
            if isinstance(parents, list):
                for pid in parents:
                    if pid not in visited:
                        queue.append(pid)

        return lineage

    def get_learning_curves(self, game_id: str) -> List[dict]:
        """Get all training runs for a game.

        Each returned dict contains the run metadata and the
        *learning_curve* deserialised to a list of ``[episode, winrate]``
        pairs.
        """
        rows = self.conn.execute(
            '''SELECT * FROM training_runs WHERE game_id = ?
               ORDER BY run_seed ASC''',
            (game_id,),
        ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            if d.get("learning_curve"):
                d["learning_curve"] = json.loads(d["learning_curve"])
            results.append(d)
        return results

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def update_elo(self, game_id: str, new_elo: float):
        """Update the ELO rating for a game in the scores table."""
        self.conn.execute(
            '''UPDATE scores SET elo = ? WHERE game_id = ?''',
            (new_elo, game_id),
        )
        self.conn.commit()

    def game_count(self) -> int:
        """Return total number of tracked games."""
        row = self.conn.execute("SELECT COUNT(*) AS cnt FROM games").fetchone()
        return row["cnt"] if row else 0

    def generation_count(self) -> int:
        """Return total number of recorded generations."""
        row = self.conn.execute("SELECT COUNT(*) AS cnt FROM generations").fetchone()
        return row["cnt"] if row else 0

    def close(self):
        """Close the database connection."""
        self.conn.close()
