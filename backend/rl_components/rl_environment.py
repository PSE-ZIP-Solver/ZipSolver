import numpy as np
from typing import TYPE_CHECKING
from backend.rl_components.environment_config import EnvironmentConfig
from backend.puzzle_logic.game import Game
from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board

# Support type-hinting without triggering top-level ML imports during collection
if TYPE_CHECKING:
    import gymnasium as gym
    EnvBase = gym.Env
else:
    EnvBase = object


class RLEnvironment(EnvBase):
    """ Custom Gym environment for the Zip puzzle game."""
    def __init__(self, board: Board):
        # 1. FAST-FAIL: Defensive short-circuit on invalid data before loading Heavy ML Logic
        if board is None:
            raise ValueError("Board cannot be None.")
            
        size_val = getattr(board, "getSize", None)
        size = size_val() if callable(size_val) else size_val
        if size is None or size <= 0:
            raise ValueError("Board size must be greater than 0.")

        # 2. LAZY-LOAD: Lazily inject Heavy ML Dependencies
        import gymnasium as gym
        if EnvBase is object and gym.Env not in self.__class__.__bases__:
            self.__class__.__bases__ = (*self.__class__.__bases__, gym.Env)
            
        super().__init__()
        self.config = EnvironmentConfig() 
        self.config.size = size
        
        self.observation_space = gym.spaces.Box(
            low=0.0,
            high=1.0,
            shape=(7, self.config.size, self.config.size),
            dtype=np.float32
        )
        self.action_space = gym.spaces.Discrete(4)
        self.game = Game(board)

    def reset(self, seed: int = None):
        import gymnasium as gym
        super().reset(seed=seed)
        
        reset_func = getattr(self.game, "reset")
        if callable(reset_func): reset_func()
            
        return self._get_observation(), {}

    def step(self, action: int):
        # Defensively retrieve properties without assuming they are callables/methods
        state = getattr(self.game, "getState")
        current_position = getattr(state, "getCurrentPosition")
        
        try:
            target_position = self._get_target_position(current_position, action)
        except ValueError as e:
            return self._get_observation(), self.config.invalid_move_penalty, True, False, {"invalid_move": True, "error": str(e)}

        is_valid_func = getattr(self.game, "isValidNextStep")
        valid = is_valid_func(target_position) if callable(is_valid_func) else is_valid_func

        if not valid:
            return self._get_observation(), self.config.invalid_move_penalty, True, False, {"invalid_move": True}

        was_visited_attr = getattr(state, "isVisited")
        was_visited = was_visited_attr(target_position) if callable(was_visited_attr) else was_visited_attr

        board = getattr(self.game, "getBoard")
        wp_attr = getattr(board, "getWaypointAt")
        waypoint = wp_attr(target_position) if callable(wp_attr) else wp_attr

        expected_order = getattr(state, "getNextWaypointOrder")

        try:
            step_func = getattr(self.game, "step")
            if callable(step_func): step_func(target_position)
        except Exception as e:
            return self._get_observation(), self.config.invalid_move_penalty, True, False, {"invalid_move": True, "error": str(e)}

        reward = self._calculate_reward(waypoint, expected_order, was_visited)
        
        finished_attr = getattr(self.game, "isFinished")
        terminated = finished_attr() if callable(finished_attr) else finished_attr
        
        path = getattr(state, "getPath")
        truncated = len(path) >= self.config.max_steps
        
        return self._get_observation(), reward, bool(terminated), bool(truncated), {"invalid_move": False}

    def _get_observation(self) -> np.ndarray:
        size = self.config.size
        obs = np.zeros((7, size, size), dtype=np.float32)

        board = getattr(self.game, "getBoard")
        state = getattr(self.game, "getState")

        current = getattr(state, "getCurrentPosition")
        if current is not None:
            x, y = getattr(current, "getX"), getattr(current, "getY")
            obs[0, x, y] = 1.0

        visited = getattr(state, "getVisitedCells")
        for pos in visited:
            x, y = getattr(pos, "getX"), getattr(pos, "getY")
            obs[1, x, y] = 1.0

        waypoints = getattr(board, "getWaypoints")
        max_order = len(waypoints)
        if max_order > 0:
            for waypoint in waypoints:
                pos = getattr(waypoint, "getPosition")
                x, y = getattr(pos, "getX"), getattr(pos, "getY")
                order = getattr(waypoint, "getOrder")
                obs[2, x, y] = float(order) / max_order

        has_wall = getattr(board, "hasWallBetween")
        def check_wall(p1, p2):
            return has_wall(p1, p2) if callable(has_wall) else False

        for x in range(size):
            for y in range(size):
                pos = Position(x, y)
                if y > 0 and check_wall(pos, Position(x, y - 1)): obs[3, x, y] = 1.0
                if x < size - 1 and check_wall(pos, Position(x + 1, y)): obs[4, x, y] = 1.0
                if y < size - 1 and check_wall(pos, Position(x, y + 1)): obs[5, x, y] = 1.0
                if x > 0 and check_wall(pos, Position(x - 1, y)): obs[6, x, y] = 1.0

        return obs

    def _get_target_position(self, current_position, action):
        x = getattr(current_position, "getX")
        y = getattr(current_position, "getY")

        if action == 0: return Position(x, y - 1)
        elif action == 1: return Position(x + 1, y)
        elif action == 2: return Position(x, y + 1)
        elif action == 3: return Position(x - 1, y)
        else:
            raise ValueError(f"Invalid action: {action}")

    def _calculate_reward(self, waypoint, expected_order, was_visited):
        finished_attr = getattr(self.game, "isFinished")
        terminated = finished_attr() if callable(finished_attr) else finished_attr
        
        if terminated: return self.config.completion_reward

        if waypoint is not None:
            order = getattr(waypoint, "getOrder")
            if order == expected_order:
                return self.config.next_waypoint_reward

        if not was_visited: return self.config.new_cell_reward
        return 0

    def render(self, mode: str = "human"):
        size = self.config.size
        board = getattr(self.game, "getBoard")
        state = getattr(self.game, "getState")

        current = getattr(state, "getCurrentPosition")
        visited = getattr(state, "getVisitedCells")

        waypoints = getattr(board, "getWaypoints")
        waypoint_at = {
            (getattr(getattr(wp, "getPosition"), "getX"), getattr(getattr(wp, "getPosition"), "getY")): getattr(wp, "getOrder")
            for wp in waypoints
        }

        def cell_symbol(x: int, y: int) -> str:
            pos = Position(x, y)
            if pos == current: return "@"
            if (x, y) in waypoint_at: return str(waypoint_at[(x, y)])
            if pos in visited: return "x"
            return "."

        has_wall = getattr(board, "hasWallBetween")
        def check_wall(p1, p2): return has_wall(p1, p2) if callable(has_wall) else False

        lines = []
        for y in range(size):
            row = ""
            for x in range(size):
                row += f" {cell_symbol(x, y)} "
                if x < size - 1:
                    row += "|" if check_wall(Position(x, y), Position(x + 1, y)) else " "
            lines.append(row)

            if y < size - 1:
                sep = ""
                for x in range(size):
                    sep += "---" if check_wall(Position(x, y), Position(x, y + 1)) else "   "
                    if x < size - 1: sep += " "
                lines.append(sep)

        output = "\n".join(lines)
        if mode == "human":
            print(output)
            return None
        elif mode == "ansi":
            return output
        else:
            raise ValueError(f"Unsupported render mode: {mode}")