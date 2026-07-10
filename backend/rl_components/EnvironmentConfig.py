class EnvironmentConfig:
    """Environment configuration for the Zip RL environment."""

    def __init__(self, size: int = 3):
        self.size = size

        # Limit episode length.
        # A valid solution needs exactly size^2 - 1 moves after the start cell.
        # We allow a bit more so the agent can recover from small mistakes.
        self.max_steps = self.size ** 2 * 4

        # Rewards / penalties
        self.invalid_move_penalty = -10.0
        self.step_penalty = -0.01
        self.completion_reward = 200.0
        self.next_waypoint_reward = 25.0
        self.new_cell_reward = 2.0