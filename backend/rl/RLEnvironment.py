import gymnasium as gym
import numpy as np
from backend.rl.EnvironmentConfig import EnvironmentConfig
from backend.puzzle_logic.game import Game
from puzzle_logic.data_models import Position
from puzzle_logic.board import Board

class RLEnvironment(gym.Env):
    """ Custom Gym environment for the Zip puzzle game."""
    def __init__(self, board: Board):
        super().__init__()
        self.config = EnvironmentConfig(6)
        self.observation_space = gym.spaces.Box(
            low = 0,
            high = 1,
            shape=(7, self.config.size, self.config.size),
            dtype=np.float32
        )
        self.action_space = gym.spaces.Discrete(4)
        # 0 = UP, 1 = RIGHT, 2 = DOWN, 3 = LEFT
        self.game = Game(board)

    def reset(self, seed: int = None):
        """ Reset the environment to the initial state and return the initial observation and info."""
        super().reset(seed=seed)
        self.game.reset()


        observation = self._get_observation()
        info = {}  #TODO add something here?

        return observation, info

    def step(self, action: int):
        """ Apply the given action to the environment and return (obs, reward, terminated, truncated, info)."""
        current_position = self.game.getState.getCurrentPosition
        target_position = self._get_target_position(current_position, action)

        if not self.game.isValidNextStep(target_position):
            reward = self.config.invalid_move_penalty
            terminated = True
            truncated = False
            info = {"invalid_move": True}
            return self._get_observation(), reward, terminated, truncated, info

        was_visited = self.game.getState.isVisited(target_position)
        waypoint = self.game.getBoard.getWaypointAt(target_position)
        expected_order = self.game.getState.getNextWaypointOrder

        self.game.step(target_position)

        reward = self._calculate_reward(waypoint, expected_order, was_visited)
        terminated = self.game.isFinished()
        truncated = len(self.game.getState.getPath) >= self.config.max_steps
        info = {"invalid_move": False}

        return self._get_observation(), reward, terminated, truncated, info


    def _get_observation(self) -> np.ndarray:
        """ Return the current observation of the environment as a 7-channel tensor.
            Channels:
            0: Current position of the player \n
            1: Visited cells        (1 if visited, 0 otherwise) \n
            2: Waypoints            (value = order of waypoint, 0 if not a waypoint) \n
            3: Wall above           (1 if wall exists, 0 otherwise) \n
            4: Wall to the right    (1 if wall exists, 0 otherwise) \n
            5: Wall below           (1 if wall exists, 0 otherwise) \n
            6: Wall to the left     (1 if wall exists, 0 otherwise) \n
        """
        size = self.config.size
        obs = np.zeros((7, size, size), dtype=np.float32)

        board = self.game.getBoard
        state = self.game.getState

        current = state.getCurrentPosition
        obs[0, current.getX, current.getY] = 1.0

        for pos in state.getVisitedCells:
            obs[1, pos.getX, pos.getY] = 1.0

        max_order = len(board.getWaypoints)
        for waypoint in board.getWaypoints:
            pos = waypoint.getPosition
            obs[2, pos.getX, pos.getY] = float(waypoint.getOrder)/max_order

        for x in range(size):
            for y in range(size):
                pos = Position(x, y)
                # Above
                if y > 0 and board.hasWallBetween(pos, Position(x, y - 1)):
                    obs[3, x, y] = 1.0
                #Right
                if x < size - 1 and board.hasWallBetween(pos, Position(x + 1, y)):
                    obs[4, x, y] = 1.0
                #Below
                if y < size - 1 and board.hasWallBetween(pos, Position(x, y + 1)):
                    obs[5, x, y] = 1.0
                #Left
                if x > 0 and board.hasWallBetween(pos, Position(x - 1, y)):
                    obs[6, x, y] = 1.0

        return obs

    def _get_target_position(self, current_position, action):
        """ Given the current position and an action, return the target position. """
        x, y = current_position.getX, current_position.getY

        if action == 0:  # UP
            return Position(x, y - 1)
        elif action == 1:  # RIGHT
            return Position(x + 1, y)
        elif action == 2:  # DOWN
            return Position(x, y + 1)
        elif action == 3:  # LEFT
            return Position(x - 1, y)
        else:
            raise ValueError(f"Invalid action: {action}")

    def _calculate_reward(self, waypoint, expected_order, was_visited):
        """ Calculate the reward for moving to the target position. """
        if self.game.isFinished():
            return self.config.completion_reward

        if waypoint is not None and waypoint.getOrder == expected_order:
            return self.config.next_waypoint_reward

        if not was_visited:
          return self.config.new_cell_reward

        return 0

    #NEW METHOD, JUST FOR TESTING AND VERIFYING DOESNT RENDER WALLS YET
    def render(self, mode: str = "human"):
        """Render the current board state to the terminal using ASCII symbols.

        Symbols:
            @   current position
            1-9 waypoint order
            x   visited cell (non-waypoint)
            .   unvisited cell
            |   vertical wall
            --- horizontal wall
        """
        size = self.config.size
        board = self.game.getBoard
        state = self.game.getState

        current = state.getCurrentPosition
        visited = state.getVisitedCells

        waypoint_at = {}
        for wp in board.getWaypoints:
            waypoint_at[(wp.getPosition.getX, wp.getPosition.getY)] = wp.getOrder

        def cell_symbol(x: int, y: int) -> str:
            pos = Position(x, y)
            if pos == current:
                return "@"
            if (x, y) in waypoint_at:
                return str(waypoint_at[(x, y)])
            if pos in visited:
                return "x"
            return "."

        lines = []
        for y in range(size):
            # cell row: each cell padded to 3 chars, separated by wall or space
            row = ""
            for x in range(size):
                row += f" {cell_symbol(x, y)} "
                if x < size - 1:
                    wall = board.hasWallBetween(Position(x, y), Position(x + 1, y))
                    row += "|" if wall else " "
            lines.append(row)

            # horizontal wall row between y and y+1, same column width as cell row
            if y < size - 1:
                sep = ""
                for x in range(size):
                    wall = board.hasWallBetween(Position(x, y), Position(x, y + 1))
                    sep += "---" if wall else "   "
                    if x < size - 1:
                        sep += " "
                lines.append(sep)

        output = "\n".join(lines)
        if mode == "human":
            print(output)
            return None
        elif mode == "ansi":
            return output
        else:
            raise ValueError(f"Unsupported render mode: {mode}")

