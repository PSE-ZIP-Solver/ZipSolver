import gymnasium as gym
import numpy as np
from backend.rl_components.environment_config import EnvironmentConfig
from backend.puzzle_logic.game import Game
from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board


class RLEnvironment(gym.Env):
    """
    Custom Gym environment for the Zip puzzle game.

    Responsibility:
        Translates the internal mathematical puzzle domain into a standardized virtual 
        learning arena. Enables external neural agents to systematically interact with, 
        observe, and evaluate grid states through normalized action-reward feedback loops.

    Implementation Details:
        Inherits natively from `gymnasium.Env`. Encapsulates a standalone `Game` controller 
        and defines explicit continuous spatial observation arrays paired against discrete 
        action spaces. Translates physical obstructions and milestones into distinct 
        tensor layers to feed directly into the convolutional predictive layers.
    """

    metadata = {"render_modes": ["human", "ansi"]}

    def __init__(self, board: Board):
        """
        Instantiates the simulated environment binding the structural blueprint to tracking spaces.

        Args:
            board: The static layout configuration dictating spatial structures and constraints.

        Implementation Details:
            Generates standardized multidimensional Box matrices utilizing explicit float bounds 
            to represent an 8-channel depth map. Initializes a discrete mathematical space 
            restricting inputs strictly to cardinal directions, and safely encapsulates a 
            fresh internal puzzle state controller.
        """
        super().__init__()

        self.config = EnvironmentConfig(board.getSize)

        self.observation_space = gym.spaces.Box(
            low=0,
            high=1,
            shape=(8, self.config.size, self.config.size),
            dtype=np.float32,
        )

        self.action_space = gym.spaces.Discrete(4)
        # 0 = UP, 1 = RIGHT, 2 = DOWN, 3 = LEFT

        self.game = Game(board)
        self.current_step_count = 0

    def reset(self, seed: int | None = None, options=None):
        """
        Reset the environment to the initial game state.

        Args:
            seed: The optional baseline generator seed establishing reproducible randomness.
            options: Unused optional parameter mapping for standard Gym compliance.

        Returns:
            A tuple pairing the active multi-channel observation matrix and a diagnostic info dictionary.

        Implementation Details:
            Delegates standard random seeding to the parent class before aggressively flushing 
            the internal `Game` state to clear visitation histories and coordinate trackers. 
            Regenerates the baseline tensor layers mapped to the freshly cleared layout.
        """
        super().reset(seed=seed)

        self.game.reset()
        self.current_step_count = 0

        observation = self._get_observation()
        info = {}

        return observation, info

    def step(self, action: int):
        """
        Apply the given action to the environment.

        Args:
            action: The discrete cardinal maneuver dictated by the neural agent.

        Returns:
            A composite sequence conveying the ensuing tensor observation, the calculated 
            floating-point reward, boolean flags denoting natural termination or forced truncation, 
            and a supplementary diagnostic dictionary.

        Implementation Details:
            Unboxes the incoming action cleanly and calculates the absolute spatial translation. 
            Actively intercepts invalid geometric moves (like colliding with walls or boundaries) 
            prior to evaluating state traversal, punishing the agent and instantly terminating the episode. 
            Otherwise, executes the step against the internal controller, aggregates dynamic milestone 
            rewards, and truncates evaluation loops if step limits organically expire.
        """
        action = int(action)
        self.current_step_count += 1

        current_position = self.game.getState.getCurrentPosition
        target_position = self._get_target_position(current_position, action)

        if not self.game.isValidNextStep(target_position):
            reward = self.config.invalid_move_penalty
            terminated = True
            truncated = False
            info = {
                "invalid_move": True,
                "step_count": self.current_step_count,
            }

            return self._get_observation(), reward, terminated, truncated, info

        was_visited = self.game.getState.isVisited(target_position)
        waypoint = self.game.getBoard.getWaypointAt(target_position)
        expected_order = self.game.getState.getNextWaypointOrder

        self.game.step(target_position)

        reward = self.config.step_penalty + self._calculate_reward(
            waypoint,
            expected_order,
            was_visited,
        )

        terminated = self.game.isFinished()
        truncated = (
            not terminated
            and self.current_step_count >= self.config.max_steps
        )

        info = {
            "invalid_move": False,
            "step_count": self.current_step_count,
            "is_finished": self.game.isFinished(),
        }

        return self._get_observation(), reward, terminated, truncated, info

    def _get_observation(self) -> np.ndarray:
        """
        Return the current observation as an 8-channel tensor.

        Returns:
            The normalized multidimensional array representing distinct physical and chronological states.

        Implementation Details:
            Constructs a zeroed multidimensional buffer. Actively queries the encapsulated `Board` 
            and `GameState` layers iterating completely across the layout. Projects distinct data points 
            (visited matrices, fractional waypoint sequence bounds, specific cardinal barrier nodes) 
            into isolated boolean or normalized float channels to prevent convolution entanglement.
        """
        size = self.config.size
        obs = np.zeros((8, size, size), dtype=np.float32)

        board = self.game.getBoard
        state = self.game.getState

        current = state.getCurrentPosition
        obs[0, current.getX, current.getY] = 1.0

        for pos in state.getVisitedCells:
            obs[1, pos.getX, pos.getY] = 1.0

        max_order = len(board.getWaypoints)

        if max_order > 0:
            for waypoint in board.getWaypoints:
                pos = waypoint.getPosition
                obs[2, pos.getX, pos.getY] = float(waypoint.getOrder) / max_order

        next_waypoint_order = state.getNextWaypointOrder

        for waypoint in board.getWaypoints:
            if waypoint.getOrder == next_waypoint_order:
                pos = waypoint.getPosition
                obs[7, pos.getX, pos.getY] = 1.0
                break

        for x in range(size):
            for y in range(size):
                pos = Position(x, y)

                # Wall or boundary above
                if y == 0 or board.hasWallBetween(pos, Position(x, y - 1)):
                    obs[3, x, y] = 1.0

                # Wall or boundary to the right
                if x == size - 1 or board.hasWallBetween(pos, Position(x + 1, y)):
                    obs[4, x, y] = 1.0

                # Wall or boundary below
                if y == size - 1 or board.hasWallBetween(pos, Position(x, y + 1)):
                    obs[5, x, y] = 1.0

                # Wall or boundary to the left
                if x == 0 or board.hasWallBetween(pos, Position(x - 1, y)):
                    obs[6, x, y] = 1.0

        return obs

    def _get_target_position(self, current_position: Position, action: int) -> Position:
        """
        Return the target position for the given action.

        Args:
            current_position: The exact architectural node anchoring the shift.
            action: The discrete integer mapping representing cardinal motion limits.

        Returns:
            The freshly derived destination coordinate block.

        Raises:
            ValueError: If the input directive violates standard discrete limits.

        Implementation Details:
            Extracts native limits directly generating spatial offsets structurally mapping 
            Standard Gym 0-3 actions against negative/positive geometric jumps strictly matching 
            the top-left origin design.
        """
        x = current_position.getX
        y = current_position.getY

        if action == 0:  # UP
            return Position(x, y - 1)

        if action == 1:  # RIGHT
            return Position(x + 1, y)

        if action == 2:  # DOWN
            return Position(x, y + 1)

        if action == 3:  # LEFT
            return Position(x - 1, y)

        raise ValueError(f"Invalid action: {action}")

    def _calculate_reward(self, waypoint, expected_order: int, was_visited: bool) -> float:
        """
        Calculate the reward for the latest valid move.

        Args:
            waypoint: The localized milestone node identified on the specific cell.
            expected_order: The strict chronological number the sequence necessitates natively.
            was_visited: The boolean marker defining whether the node repeats past tracks.

        Returns:
            The raw scalar valuation assigning positive values to successful progressions.

        Implementation Details:
            Evaluates terminal conditions first, injecting massive completion payouts. 
            Prioritizes valid chronological milestone intersects dynamically over raw spatial 
            explorations to guide gradient climbs toward structured sequencing instead of 
            aimless spatial mapping.
        """
        if self.game.isFinished():
            return self.config.completion_reward

        if waypoint is not None and waypoint.getOrder == expected_order:
            return self.config.next_waypoint_reward

        if not was_visited:
            return self.config.new_cell_reward

        return 0.0

    def render(self, mode: str = "human"):
        """
        Render the current board state to the terminal using ASCII symbols.

        Args:
            mode: The distinct structural flag driving visual or textual outputs.

        Returns:
            The formatted string output strictly when operating under ANSI configurations, 
            otherwise natively routes into standard output streams.

        Raises:
            ValueError: If supplied with a formatting mode unmapped within core limits.

        Implementation Details:
            Aggregates topological constraints traversing grid intersections explicitly. 
            Calculates line demarcations injecting vertical bars and horizontal hyphens natively 
            to physically symbolize barriers against distinct spatial nodes. Translates internal 
            milestones back to string indices allowing humans to visually debug internal arrays.
        """
        size = self.config.size
        board = self.game.getBoard
        state = self.game.getState

        current = state.getCurrentPosition
        visited = state.getVisitedCells

        waypoint_at = {}

        for waypoint in board.getWaypoints:
            position = waypoint.getPosition
            waypoint_at[(position.getX, position.getY)] = waypoint.getOrder

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
            row = ""

            for x in range(size):
                row += f" {cell_symbol(x, y)} "

                if x < size - 1:
                    wall = board.hasWallBetween(
                        Position(x, y),
                        Position(x + 1, y),
                    )
                    row += "|" if wall else " "

            lines.append(row)

            if y < size - 1:
                separator = ""

                for x in range(size):
                    wall = board.hasWallBetween(
                        Position(x, y),
                        Position(x, y + 1),
                    )
                    separator += "---" if wall else "   "

                    if x < size - 1:
                        separator += " "

                lines.append(separator)

        output = "\n".join(lines)

        if mode == "human":
            print(output)
            return None

        if mode == "ansi":
            return output

        raise ValueError(f"Unsupported render mode: {mode}")