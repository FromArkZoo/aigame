"""Central configuration for the Genesis Creativity Engine."""

from dataclasses import dataclass, field


@dataclass
class GameConfig:
    """Parameters for game generation."""
    # --- V1 fields (kept for backward compatibility) ---
    state_dim: int = 8
    min_state_dim: int = 4
    max_state_dim: int = 8
    min_actions: int = 3
    max_actions: int = 6
    max_game_steps: int = 100
    num_players: int = 2
    min_tree_depth: int = 2
    max_tree_depth: int = 5
    observation_types: list = field(default_factory=lambda: ["full", "partial", "asymmetric"])

    # --- V2/V3 fields (topological spaces + structured rules) ---
    min_dimensions: int = 2       # minimum n-dimensional topology
    max_dimensions: int = 6       # maximum n (evolves from 2 to 12)
    max_total_cells: int = 64     # cap on axis_size^n

    # --- V3 fields ---
    topology_types: list = field(default_factory=lambda: ["grid", "torus", "hex", "moore"])
    enable_movement: bool = True  # allow "move" action type in generated games
    movement_probability: float = 0.3  # chance a new game includes movement
    ca_probability: float = 0.3  # chance a new game uses CA rules instead of classic capture/propagation


@dataclass
class TrainingConfig:
    """Parameters for RL training."""
    hidden_dim: int = 64
    num_hidden_layers: int = 2
    learning_rate: float = 3e-4
    gamma: float = 0.99
    training_budget: int = 10000  # number of episodes
    batch_size: int = 64
    entropy_coef: float = 0.01
    clip_epsilon: float = 0.2  # for PPO
    num_independent_runs: int = 3  # for strategic diversity
    eval_episodes: int = 50


@dataclass
class MetricsConfig:
    """Parameters for Go Essence metrics."""
    depth_weight: float = 1.0
    diversity_weight: float = 1.0
    simplicity_weight: float = 1.0
    learning_curve_checkpoints: int = 10
    random_baseline_episodes: int = 200


@dataclass
class ArenaConfig:
    """Parameters for tournament/ranking."""
    initial_elo: float = 1500.0
    k_factor: float = 32.0
    top_n_leaderboard: int = 20


@dataclass
class EvolutionConfig:
    """Parameters for evolutionary loop."""
    population_size: int = 50
    num_generations: int = 10
    elite_count: int = 5
    mutation_rate: float = 0.3
    crossover_rate: float = 0.3
    immigration_rate: float = 0.15
    tournament_size: int = 3
    param_mutation_std: float = 0.1


@dataclass
class TrackingConfig:
    """Parameters for tracking and analysis."""
    db_path: str = "genesis_results.db"
    log_dir: str = "logs"
    plot_dir: str = "plots"


@dataclass
class GenesisConfig:
    """Master configuration."""
    game: GameConfig = field(default_factory=GameConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    arena: ArenaConfig = field(default_factory=ArenaConfig)
    evolution: EvolutionConfig = field(default_factory=EvolutionConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    seed: int = 42
