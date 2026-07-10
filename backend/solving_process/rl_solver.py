import time
from typing import Optional

from solver import Solver
from solver_result import SolverResult
from solver_status import SolverStatus
from solver_metrics import SolverMetrics
from backend.solution_path import SolutionPath
from backend.puzzle_logic.board import Board
from backend.rl_components.RLAgent import RLAgent
from backend.rl_components.RLEnvironment import RLEnvironment


class RLSolver(Solver):
    def __init__(self):
        self._agent: Optional[RLAgent] = None
        self._environment: Optional[RLEnvironment] = None
        self._model_path: str = "agent.zip"

    def loadAgent(self) -> RLAgent:
        """
        Loads the pre-trained RL agent model.
        Requires the RLEnvironment to be initialized first.
        """
        if self._environment is None:
            raise RuntimeError("Environment must be created before loading the RLAgent.")

        # Note on Efficiency: This currently loads the PyTorch model from disk every time.
        # For production scale, consider modifying RLAgent to allow reusing the underlying 
        # sb3 model in memory and just swapping the environment using `model.set_env()`.
        self._agent = RLAgent(env=self._environment, model_path=self._model_path)
        return self._agent

    def runEpisode(self, board: Board) -> SolverResult:
        """
        Runs one RL inference episode for the given board.
        Contains fail-safes for runaway loops.
        """
        start_time = time.time()
        steps = 0
        max_failsafe_steps = 1000  # Hard limit in case Gym environment fails to truncate
        
        obs, info = self._environment.reset()
        
        terminated = False
        truncated = False

        # Episode Active Loop
        while not (terminated or truncated) and steps < max_failsafe_steps:
            action = self._agent.predict(obs, deterministic=True)
            
            # Safely extract scalar action (SB3 can sometimes wrap outputs in numpy arrays)
            action_val = int(action.item()) if hasattr(action, 'item') else int(action)
            
            obs, reward, terminated, truncated, info = self._environment.step(action_val)
            steps += 1

        runtime_ms = int((time.time() - start_time) * 1000)
        metrics = SolverMetrics(runtimeMs=runtime_ms, steps=steps, attempts=1)

        # Safety check: If we hit the fail-safe, force a failure
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
        if raw_path:
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
        if setup/inference crashes, allowing Algorithmic fallback to take over.
        """
        start_time = time.time()
        
        try:
            self._environment = RLEnvironment(board)
            self.loadAgent()
            return self.runEpisode(board)
            
        except Exception as e:
            # Catch initialization errors (like missing waypoints) or unexpected PyTorch/Gym crashes
            runtime_ms = int((time.time() - start_time) * 1000)
            metrics = SolverMetrics(runtimeMs=runtime_ms, steps=0, attempts=1)
            
            return SolverResult(
                status=SolverStatus.FAILED,
                path=None,
                message=f"RLSolver crashed during execution: {str(e)}",
                metrics=metrics
            )