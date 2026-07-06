class EnvironmentConfig:
    """Environment configuration."""

    def __init__(self, size: int = 3):
        self.size = size

        # Bigger than size^2 because invalid moves should not end the episode immediately
        self.max_steps = self.size ** 2 * 4

        # Rewards / penalties
        self.invalid_move_penalty = -1
        self.completion_reward = 500
        self.next_waypoint_reward = 50
        self.new_cell_reward = 1