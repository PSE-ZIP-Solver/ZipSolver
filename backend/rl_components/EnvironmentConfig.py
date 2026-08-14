class EnvironmentConfig:
    """Environment configuration for the Zip RL environment."""

    def __init__(self, size: int = 8):
        self.size = size
        
        # The start cell is already visited after reset, so only size^2 - 1 moves are needed.
        self.max_steps = self.size ** 2 - 1

        # Rewards / penalties
        self.invalid_move_penalty = -5.0
        self.step_penalty = -0.02
        self.completion_reward = 300.0
        self.next_waypoint_reward = 4.0
        self.new_cell_reward = 1.0