class EnvironmentConfig:
    """Environment configuration for the Zip RL environment."""

    def __init__(self, size: int = 6):
        self.size = size
        
        # The start cell is already visited after reset, so only size^2 - 1 moves are needed.
        self.max_steps = self.size ** 2 - 1

        # Rewards / penalties
        self.invalid_move_penalty = -10.0
        self.step_penalty = -0.01
        self.completion_reward = 200.0
        self.next_waypoint_reward = 25.0
        self.new_cell_reward = 2.0