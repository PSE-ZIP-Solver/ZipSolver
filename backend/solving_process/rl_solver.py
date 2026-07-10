import time
import logging
from typing import Optional

# Core solver imports
from solver import Solver
from solver_result import SolverResult
from solver_status import SolverStatus
from solver_metrics import SolverMetrics
from backend.solution_path import SolutionPath

# Puzzle Logic and RL components
from backend.puzzle_logic.board import Board
from backend.rl_components.RLAgent import RLAgent
from backend.rl_components.RLEnvironment import RLEnvironment

logger = logging.getLogger(__name__)


class RLSolver(Solver):
    def __init__(self, model_path: str = "agent.zip"):
        self._model_path = model_path
        self._agent: Optional[RLAgent] = None
        self._environment: Optional[RLEnvironment] = None

    def loadAgent(self) -> RLAgent:
        """
        Loads the pre-trained RL agent model.
        Implements caching to prevent expensive disk I/O on subsequent solves.
        """
        if self._environment is None:
            raise RuntimeError("Environment must be created before loading the RLAgent.")

        if self._agent is None:
            # First execution: Load heavy PyTorch model from disk
            self._agent = RLAgent(env=self._environment, model_path=self._model_path)
        else:
            # Subsequent executions: Reuse the cached model and swap the environment.
            self._agent._env = self._environment
            if hasattr(self._agent, '_model') and self._agent._model is not None:
                self._agent._model.set_env(self._environment)

        return self._agent

    def runEpisode(self, board: Board) -> SolverResult:
        """
        Runs one RL inference episode for the given board.
        Contains fail-safes for runaway loops and unexpected return types.
        """
        start_time = time.time()
        steps = 0
        max_failsafe_steps = 1000  # Hard limit to prevent infinite loops
        
        obs, info = self._environment.reset()
        
        terminated = False
        truncated = False

        # Episode Active Loop
        while not (terminated or truncated) and steps < max_failsafe_steps:
            # Predict action deterministically
            action = self._agent.predict(obs, deterministic=True)
            
            # Defensive unboxing: Handles int, np.int64, or 1D arrays like [3]
            try:
                action_val = int(action.item()) if hasattr(action, 'item') else int(action)
            except TypeError:
                # Fallback if action is strangely shaped, e.g., [[3]]
                action_val = int(action[0])
            
            # Apply action to the environment
            obs, reward, terminated, truncated, info = self._environment.step(action_val)
            steps += 1

        runtime_ms = int((time.time() - start_time) * 1000)
        metrics = SolverMetrics(runtimeMs=runtime_ms, steps=steps, attempts=1)

        # Safety check: If we hit the fail-safe, abort
        if steps >= max_failsafe_steps:
            return SolverResult(
                status=SolverStatus.FAILED,
                path=None,
                message="RL episode aborted: Hit hard loop limit.",
                metrics=metrics
            )

        # Extract path safely
        game = self._environment.game
        raw_path = game.getState.getPath
        
        solution_path = SolutionPath()
        if raw_path is not None:
            for pos in raw_path:
                solution_path.add(pos)

        # Evaluate success
        if game.isFinished():
            return SolverResult(
                status=SolverStatus.SOLVED,
                path=solution_path,
                message="RL Agent successfully found a complete solution.",
                metrics=metrics
            )
        else:
            invalid_move = info.get("invalid_move", False)
            reason = "invalid move" if invalid_move else "max steps reached"
            
            return SolverResult(
                status=SolverStatus.FAILED,
                path=solution_path,
                message=f"RL Agent episode terminated without finding a complete solution ({reason}).",
                metrics=metrics
            )

    def solve(self, board: Board) -> SolverResult:
        """
        Starts the RL solving attempt. 
        Wrapped in a try-except to guarantee a FAILED SolverResult is returned 
        if setup/inference crashes. Also properly manages Gym resources.
        """
        start_time = time.time()
        
        # Prevent Memory Leaks: Close the old environment before making a new one
        if self._environment is not None:
            try:
                self._environment.close()
            except Exception:
                pass # Fail silently on close, as we're discarding it anyway
        
        try:
            self._environment = RLEnvironment(board)
            self.loadAgent()
            return self.runEpisode(board)
            
        except Exception as e:
            # Log the full stack trace for debugging, but return a clean object
            logger.exception("RLSolver crashed during execution.")
            
            runtime_ms = int((time.time() - start_time) * 1000)
            metrics = SolverMetrics(runtimeMs=runtime_ms, steps=0, attempts=1)
            
            return SolverResult(
                status=SolverStatus.FAILED,
                path=None,
                message=f"RLSolver crashed during execution: {str(e)}",
                metrics=metrics
            )