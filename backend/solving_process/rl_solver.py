from solver import Solver
from solver_result import SolverResult
from backend.puzzle_logic.board import Board
from backend.rl_components.RLAgent import RLAgent
from backend.rl_components.RLEnvironment import RLEnvironment


class RLSolver(Solver):
    def __init__(self):
        self._agent: RLAgent = None # TODO implement
        self._environment: RLEnvironment = None # TODO implement

    def _loadAgent(self) -> RLAgent:
        """
        Loads the pre-trained RL agent model.

        Returns:
            RLAgent: The loaded reinforcement learning agent.
        """
        # TODO implement
        pass

    def _runEpisode(self, board: Board) -> SolverResult:
        """
        Runs one RL episode for the given board and returns the resulting solver result.

        Args:
            board (Board): The board to be solved.

        Returns:
            SolverResult: The result of the solving episode containing path, status, and metrics.
        """
        # TODO implement
        pass

    def solve(self, board: Board) -> SolverResult:
        """
        Starts the RL solving attempt for the given board.

        Args:
            board (Board): The board to be solved.

        Returns:
            SolverResult: The result containing the status, path, message, and metrics.
        """
        # TODO implement
        pass