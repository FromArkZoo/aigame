"""ELO Ranking and Tournament System for the Genesis Creativity Engine.

Implements a standard chess-style ELO rating system adapted for comparing
generated games against each other. Matchup outcomes are determined by
each game's Go Essence composite score. A round-robin tournament ensures
every game plays every other game exactly once per tournament round.
"""

import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from config import ArenaConfig


@dataclass
class GameEntry:
    """A game in the arena pool.

    Attributes:
        game_id: Unique identifier for the game.
        elo: Current ELO rating (starts at initial_elo from config).
        scores: Dictionary of metric_name -> value for all evaluated metrics.
        go_essence: The Go Essence composite score used to determine match outcomes.
        matches_played: Total number of matches this game has participated in.
        wins: Total wins accumulated across all tournaments.
        losses: Total losses accumulated across all tournaments.
        generation: The evolutionary generation in which this game was created.
    """
    game_id: str
    elo: float = 1500.0
    scores: dict = field(default_factory=dict)
    go_essence: float = 0.0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    generation: int = 0


class Arena:
    """Tournament and ranking system for generated games.

    Uses ELO ratings to rank games relative to each other. The outcome of
    a head-to-head match between two games is determined by comparing their
    Go Essence composite scores: the game with the higher score wins, and
    ELO ratings are updated accordingly.

    Attributes:
        config: ArenaConfig with ELO parameters (initial_elo, k_factor, etc.).
        games: Mapping of game_id to GameEntry for all games in the pool.
        match_history: Chronological list of all match results.
    """

    def __init__(self, config: ArenaConfig):
        self.config = config
        self.games: Dict[str, GameEntry] = {}
        self.match_history: List[dict] = []

    def add_game(self, game_id: str, scores: dict, generation: int = 0):
        """Add a new game to the arena pool with its metric scores.

        Args:
            game_id: Unique identifier for the game.
            scores: Dictionary of metric scores. Should include 'go_essence'
                    for match outcome determination.
            generation: The evolutionary generation this game belongs to.
        """
        entry = GameEntry(
            game_id=game_id,
            elo=self.config.initial_elo,
            scores=scores,
            go_essence=scores.get('go_essence', 0.0),
            generation=generation,
        )
        self.games[game_id] = entry

    def expected_score(self, elo_a: float, elo_b: float) -> float:
        """Calculate the expected score for player A given ELO ratings.

        Uses the standard logistic ELO formula:
            E_A = 1 / (1 + 10^((R_B - R_A) / 400))

        Args:
            elo_a: ELO rating of player A.
            elo_b: ELO rating of player B.

        Returns:
            Expected score for player A, a float in [0, 1].
        """
        return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / 400.0))

    def update_elo(self, game_a_id: str, game_b_id: str):
        """Compare two games on Go Essence and update ELO ratings.

        The game with the higher Go Essence composite score wins the matchup.
        If the difference is below a small threshold (0.01), the match is
        considered a draw and both players receive a score of 0.5.

        Args:
            game_a_id: ID of the first game.
            game_b_id: ID of the second game.

        Raises:
            KeyError: If either game_id is not found in the arena pool.
        """
        a = self.games[game_a_id]
        b = self.games[game_b_id]

        expected_a = self.expected_score(a.elo, b.elo)
        expected_b = self.expected_score(b.elo, a.elo)

        # Determine winner based on Go Essence score
        diff = a.go_essence - b.go_essence
        threshold = 0.01  # draw threshold

        if abs(diff) < threshold:
            actual_a, actual_b = 0.5, 0.5
        elif diff > 0:
            actual_a, actual_b = 1.0, 0.0
            a.wins += 1
            b.losses += 1
        else:
            actual_a, actual_b = 0.0, 1.0
            a.losses += 1
            b.wins += 1

        a.elo += self.config.k_factor * (actual_a - expected_a)
        b.elo += self.config.k_factor * (actual_b - expected_b)
        a.matches_played += 1
        b.matches_played += 1

        self.match_history.append({
            'game_a': game_a_id,
            'game_b': game_b_id,
            'score_a': actual_a,
            'score_b': actual_b,
            'elo_a': a.elo,
            'elo_b': b.elo,
        })

    def run_tournament(self):
        """Run a round-robin tournament among all games in the pool.

        Each game plays against every other game exactly once. For N games
        this produces N*(N-1)/2 matches. ELO ratings are updated after each
        individual match.
        """
        game_ids = list(self.games.keys())
        for i in range(len(game_ids)):
            for j in range(i + 1, len(game_ids)):
                self.update_elo(game_ids[i], game_ids[j])

    def get_leaderboard(self, top_n: Optional[int] = None) -> List[GameEntry]:
        """Get games sorted by ELO rating, optionally limited to top N.

        Args:
            top_n: Maximum number of entries to return. Defaults to
                   config.top_n_leaderboard if not specified.

        Returns:
            List of GameEntry objects sorted by descending ELO rating.
        """
        top_n = top_n or self.config.top_n_leaderboard
        sorted_games = sorted(self.games.values(), key=lambda g: g.elo, reverse=True)
        return sorted_games[:top_n]

    def get_top_game_ids(self, n: int) -> List[str]:
        """Get IDs of top N games by ELO.

        Args:
            n: Number of top game IDs to return.

        Returns:
            List of game_id strings for the top N rated games.
        """
        return [g.game_id for g in self.get_leaderboard(n)]

    def format_leaderboard(self, top_n: Optional[int] = None) -> str:
        """Format leaderboard as a readable string table.

        Args:
            top_n: Maximum number of entries to display. Defaults to
                   config.top_n_leaderboard if not specified.

        Returns:
            A multi-line string with columns for Rank, Game ID, ELO,
            Go Essence, W/L record, and Generation.
        """
        leaderboard = self.get_leaderboard(top_n)
        lines = []
        lines.append(
            f"{'Rank':<6}{'Game ID':<20}{'ELO':<10}{'Go Essence':<14}{'W/L':<10}{'Gen':<6}"
        )
        lines.append("-" * 66)
        for i, g in enumerate(leaderboard):
            lines.append(
                f"{i+1:<6}{g.game_id:<20}{g.elo:<10.1f}{g.go_essence:<14.4f}"
                f"{g.wins}/{g.losses:<8}{g.generation:<6}"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialize arena state for persistence.

        Returns:
            A dictionary containing:
                - 'games': dict mapping game_id to serialized GameEntry fields.
                - 'match_history': list of match result dictionaries.
                - 'config': dict of ArenaConfig fields.
        """
        return {
            'games': {
                game_id: asdict(entry)
                for game_id, entry in self.games.items()
            },
            'match_history': list(self.match_history),
            'config': {
                'initial_elo': self.config.initial_elo,
                'k_factor': self.config.k_factor,
                'top_n_leaderboard': self.config.top_n_leaderboard,
            },
        }

    @classmethod
    def from_dict(cls, data: dict, config: ArenaConfig) -> 'Arena':
        """Deserialize arena state from a dictionary.

        Restores the full arena state including all game entries and
        match history. The provided config is used for the Arena instance;
        the config stored in the serialized data is informational only.

        Args:
            data: Dictionary previously produced by to_dict().
            config: ArenaConfig to use for the restored Arena.

        Returns:
            A fully restored Arena instance.
        """
        arena = cls(config)
        for game_id, entry_data in data.get('games', {}).items():
            entry = GameEntry(
                game_id=entry_data['game_id'],
                elo=entry_data.get('elo', config.initial_elo),
                scores=entry_data.get('scores', {}),
                go_essence=entry_data.get('go_essence', 0.0),
                matches_played=entry_data.get('matches_played', 0),
                wins=entry_data.get('wins', 0),
                losses=entry_data.get('losses', 0),
                generation=entry_data.get('generation', 0),
            )
            arena.games[game_id] = entry
        arena.match_history = list(data.get('match_history', []))
        return arena
