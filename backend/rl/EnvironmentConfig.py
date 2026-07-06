class EnvironmentConfig:
    """ Environment configuration """
    def __init__(self, size: int = 6):
        self.size = size
        self.max_steps = self.size ** 2
        self.invalid_move_penalty = -100
        self.completion_reward = 100
        self.next_waypoint_reward = 10
        self.new_cell_reward = 1
