class EnvironmentConfig:
    """
    Environment configuration for the Zip RL environment.

    Responsibility:
        Centralizes the hyperparameter bounds, spatial limits, and reward scaling
        scalars utilized to guide the neural network's learning topology during execution.

    Implementation Details:
        Acts as a lightweight data configuration object. Computes rigid step ceilings
        mathematically derived from the grid's sheer dimensional volume to actively truncate
        infinite agent loops and explicitly defines floating-point scalars used for
        positive reinforcement and invalid maneuver penalization.
    """

    def __init__(self, size: int = 6):
        """
        Initializes the baseline dimensional and reward parameters for spatial interaction.

        Args:
            size: The definitive architectural length bounding the simulation grid.

        Implementation Details:
            Calculates the maximum step limit actively as the square of the dimension minus one,
            accounting for the natively pre-visited starting location. Hardcodes rigid floating-point
            rewards structurally tuned to heavily penalize wall collisions and highly reward
            sequential milestone completions.
        """
        self.size = size

        # The start cell is already visited after reset, so only size^2 - 1 moves are needed.
        self.max_steps = self.size**2 - 1

        # Rewards / penalties
        self.invalid_move_penalty = -10.0
        self.step_penalty = -0.01
        self.completion_reward = 200.0
        self.next_waypoint_reward = 25.0
        self.new_cell_reward = 2.0
