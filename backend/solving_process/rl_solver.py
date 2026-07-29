import time
import logging
from typing import Optional, TYPE_CHECKING

from .solver import Solver
from .solver_result import SolverResult
from .solver_status import SolverStatus
from .solver_metrics import SolverMetrics
from backend.solution_path import SolutionPath
from backend.puzzle_logic.board import Board

if TYPE_CHECKING:
    from backend.rl_components.RLAgent import RLAgent
    from backend.rl_components.RLEnvironment import RLEnvironment

logger = logging.getLogger(__name__)


class RLSolver(Solver):
    def __init__(self, model_path: str = "backend/agent.zip"):
        self._model_path = model_path
        self._agent: Optional['RLAgent'] = None
        self._environment: Optional['RLEnvironment'] = None

    def loadAgent(self) -> 'RLAgent':
        if self._environment is None:
            raise RuntimeError("Environment must be created before loading the RLAgent.")

        if self._agent is None:
            from backend.rl_components.RLAgent import RLAgent
            self._agent = RLAgent(env=self._environment, model_path=self._model_path)
        else:
            self._agent._env = self._environment
            if hasattr(self._agent, '_model') and self._agent._model is not None:
                self._agent._model.set_env(self._environment)

        return self._agent

    def runEpisode(self) -> SolverResult:
        start_time = time.time()
        steps = 0
        max_failsafe_steps = 1000
        
        obs, info = self._environment.reset()
        terminated = False
        truncated = False

        while not (terminated or truncated) and steps < max_failsafe_steps:
            # Safely unpacking SB3 Tuple
            action_array, _states = self._agent.predict(obs, deterministic=True)
            
            try:
                if hasattr(action_array, 'item'):
                    action_val = int(action_array.item())
                elif hasattr(action_array, '__iter__') and not isinstance(action_array, (str, bytes)):
                    action_val = int(next(iter(action_array)))
                else:
                    action_val = int(action_array)
            except (TypeError, ValueError, StopIteration):
                action_val = 0
            
            obs, reward, terminated, truncated, info = self._environment.step(action_val)
            steps += 1

        runtime_ms = int((time.time() - start_time) * 1000)
        metrics = SolverMetrics(runtimeMs=runtime_ms, steps=steps, attempts=1)

        if steps >= max_failsafe_steps:
            return SolverResult(
                status=SolverStatus.TIMEOUT,
                path=None,
                message="RL episode aborted: Hit hard loop limit.",
                metrics=metrics
            )

        game = self._environment.game
        raw_path = game.getState.getPath
        
        solution_path = SolutionPath()
        if raw_path is not None:
            for pos in raw_path:
                solution_path.add(pos)

        # Evaluating property safely without ()
        is_finished = getattr(game, 'isFinished', False)
        if callable(is_finished): 
            is_finished = is_finished()

        if is_finished:
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
                status=SolverStatus.UNSOLVABLE,
                path=solution_path,
                message=f"RL Agent episode terminated without finding a complete solution ({reason}).",
                metrics=metrics
            )

    def solve(self, board: Board) -> SolverResult:
        start_time = time.time()

        # Fast-fail mathematical edge cases before triggering heavy RL loads
        board_size = getattr(board, 'getSize', 0) if board else 0
        if callable(board_size):
            board_size = board_size()

        if board is None or board_size == 0:
            return SolverResult(
                status=SolverStatus.UNSOLVABLE,
                path=None,
                message="Invalid or mathematically unsolvable board dimensions.",
                metrics=SolverMetrics(runtimeMs=0, steps=0, attempts=0)
            )
        
        if self._environment is not None:
            try:
                self._environment.close()
            except Exception:
                pass
        
        try:
            from backend.rl_components.RLEnvironment import RLEnvironment
            self._environment = RLEnvironment(board)
            self.loadAgent()
            
            return self.runEpisode()
            
        except Exception as e:
            logger.exception("RLSolver crashed during execution.")
            
            if self._environment is not None:
                try:
                    self._environment.close()
                except Exception:
                    pass
            
            runtime_ms = int((time.time() - start_time) * 1000)
            metrics = SolverMetrics(runtimeMs=runtime_ms, steps=0, attempts=1)
            
            return SolverResult(
                status=SolverStatus.UNSOLVABLE,
                path=None,
                message=f"RLSolver crashed during execution: {str(e)}",
                metrics=metrics
            )