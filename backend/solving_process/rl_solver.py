import hashlib
import logging
import time
from pathlib import Path

from .solver import Solver
from .solver_result import SolverResult
from .solver_status import SolverStatus
from .solver_metrics import SolverMetrics

from backend.solution_path import SolutionPath
from backend.puzzle_logic.board import Board
from backend.rl_components.rl_agent import RLAgent
from backend.rl_components.rl_environment import RLEnvironment


logger = logging.getLogger(__name__)


# Repository root:
# ZipSolver/backend/solving_process/rl_solver.py
#                               ↑
# parents[2] = ZipSolver
PROJECT_ROOT = Path(__file__).resolve().parents[2]


MODEL_PATHS: dict[int, Path] = {
    6: (
        PROJECT_ROOT
        / "offline_training"
        / "trained_models"
        / "6x6"
        / "6x6-agent.zip"
    ),

    # Later:
    # 7: (
    #     PROJECT_ROOT
    #     / "offline_training"
    #     / "trained_models"
    #     / "7x7"
    #     / "7x7-agent.zip"
    # ),
    #
     8: (
        PROJECT_ROOT
        / "offline_training"
        / "trained_models"
        / "8x8"
        / "8x8-agent.zip"
     ),
}


class RLSolver(Solver):
    """
    Solver using pre-trained reinforcement-learning agents.

    Responsibility:
        Bridges the gap between the application's domain objects and the underlying Stable-Baselines3 
        predictive networks. It manages model caching, maps dimensional constraints to appropriate weights, 
        and orchestrates the deterministic step-by-step inference lifecycle to output a compliant trajectory.

    Implementation Details:
        The correct model is selected according to the board size.
        Maintains an internal dictionary cache mapping grid sizes to instantiated neural models 
        to prevent catastrophic I/O bottlenecks during repeated requests. 

        Inference follows the same procedure as AgentTrainer evaluation:
            RLEnvironment(board)
            -> agent.set_env(env)
            -> env.reset()
            -> agent.predict(..., deterministic=True)
            -> env.step(...)
            -> repeat until terminated/truncated
    """

    def __init__(self):
        """
        Initializes the ML orchestration wrapper and its associated memory caches.

        Implementation Details:
            Sets up empty dictionaries to hold dynamically loaded agents. Environment and active 
            agent trackers are explicitly initialized to null states awaiting an execution command.
            The model therefore only has to be loaded from disk once.
        """
        # Cache one model per board size.
        # The model therefore only has to be loaded from disk once.
        self._agents: dict[int, RLAgent] = {}

        self._environment: RLEnvironment | None = None
        self._agent: RLAgent | None = None

    @staticmethod
    def _get_board_size(board: Board) -> int:
        """
        Extracts the linear dimensional parameter from a generalized blueprint.

        Args:
            board: The baseline blueprint managing spatial variables.

        Returns:
            The raw scalar boundary value strictly normalized to an integer.

        Implementation Details:
            Return board size.
            Works whether getSize is implemented as a property or a method. Uses native `callable()` 
            checks to securely adapt to shifting architectural patterns inside the board object.
        """
        size = board.getSize

        if callable(size):
            size = size()

        return int(size)

    def _get_model_path(self, board_size: int) -> Path:
        """
        Resolves the absolute file directory for a specific set of model weights based on scale.

        Args:
            board_size: The dimensional parameter acting as the lookup key.

        Returns:
            The validated filepath pointing directly at the compressed agent weights.

        Raises:
            ValueError: If the requested dimension lacks a mapped configuration entry.
            FileNotFoundError: If the mapped physical file is inexplicably absent from the disk.

        Implementation Details:
            Return the trained model for the given board size.
            Queries the global configuration dictionary and explicitly interrogates the OS file 
            system to guarantee the payload physically exists before attempting network ingestion.
        """
        if board_size not in MODEL_PATHS:
            raise ValueError(
                f"No RL model available for "
                f"{board_size}x{board_size} boards."
            )

        model_path = MODEL_PATHS[board_size]

        if not model_path.exists():
            raise FileNotFoundError(
                f"RL model not found: {model_path}"
            )

        return model_path

    def _load_agent(self, board_size: int) -> RLAgent:
        """
        Retrieves a pre-warmed neural network from cache, or initializes it directly from disk.

        Args:
            board_size: The specific scale constraint requiring a mapped network.

        Returns:
            The fully loaded predictive agent actively bound to the current environment.

        Raises:
            RuntimeError: If execution is attempted prior to properly configuring the virtual environment.

        Implementation Details:
            Load the trained agent or reuse an already loaded model.
            Checks the dictionary cache. If absent, executes expensive file I/O to build the network. 
            If present, safely mutates the existing model by overriding its bound environment reference, 
            circumventing memory leaks.
        """
        if self._environment is None:
            raise RuntimeError(
                "Environment must exist before loading the RL agent."
            )

        # First request for this board size:
        # load model from disk.
        if board_size not in self._agents:
            model_path = self._get_model_path(board_size)

            print(
                f"[RLSolver] Loading {board_size}x{board_size} model from:",
                flush=True,
            )
            print(
                f"[RLSolver] {model_path}",
                flush=True,
            )

            logger.info(
                "Loading %sx%s RL model from %s",
                board_size,
                board_size,
                model_path,
            )

            agent = RLAgent(
                env=self._environment,
                model_path=str(model_path),
            )

            self._agents[board_size] = agent

        # Model already loaded:
        # only replace the environment.
        else:
            print(
                f"[RLSolver] Reusing cached "
                f"{board_size}x{board_size} model.",
                flush=True,
            )

            agent = self._agents[board_size]
            agent.set_env(self._environment)

        self._agent = agent

        return agent

    def _print_debug_information(self, observation) -> None:
        """
        Generates robust system logging tracking virtual state permutations during execution.

        Args:
            observation: The raw multi-dimensional matrix generated by the virtual arena.

        Implementation Details:
            Print information useful for comparing API inference with AgentTrainer evaluation.
            Captures deep terminal representations and generates SHA-256 cryptographic hashes of 
            the unboxed observation matrices to ensure exact state parity verification against 
            historical training outputs. Uses broad exception catches to prevent auxiliary logging 
            from destroying the primary execution loop.
        """
        if self._environment is None:
            return

        print(
            "\n[RLSolver] Initial board seen by RL environment:",
            flush=True,
        )

        try:
            rendered_board = self._environment.render("ansi")

            if rendered_board is not None:
                print(
                    rendered_board,
                    flush=True,
                )

        except Exception as exception:
            print(
                f"[RLSolver] Could not render board: {exception}",
                flush=True,
            )

        try:
            observation_hash = hashlib.sha256(
                observation.tobytes()
            ).hexdigest()

            print(
                f"[RLSolver] Observation shape: "
                f"{observation.shape}",
                flush=True,
            )

            print(
                f"[RLSolver] Observation hash: "
                f"{observation_hash}",
                flush=True,
            )

        except Exception as exception:
            print(
                f"[RLSolver] Could not hash observation: {exception}",
                flush=True,
            )

    def _run_episode(self) -> SolverResult:
        """
        Executes an unbroken string of continuous predictions until a terminal grid state is reached.

        Returns:
            The compiled execution envelope detailing mathematical routing, statuses, and performance timings.

        Raises:
            RuntimeError: If triggered while tracking variables hold uninitialized null states.

        Implementation Details:
            Run one deterministic inference episode.
            This intentionally mirrors AgentTrainer._run_board().
            Locks the network into deterministic mode, eliminating stochastic exploration. Feeds 
            unboxed observations continually into the network, directly converting output tensors 
            into pure integers for grid processing. Actively tracks runtime MS and iteration steps. 
            If terminal success is verified natively by the environment's internal game hook, maps the 
            history array into a structured solution wrapper. Otherwise, parses truncated flags to output failures.
        """
        if self._environment is None:
            raise RuntimeError(
                "No RL environment exists."
            )

        if self._agent is None:
            raise RuntimeError(
                "No RL agent is loaded."
            )

        start_time = time.time()

        # Same reset as during AgentTrainer evaluation.
        observation, _ = self._environment.reset()

        self._print_debug_information(observation)

        terminated = False
        truncated = False
        info = {}

        steps = 0

        while not terminated and not truncated:
            # Same prediction as AgentTrainer evaluation.
            action = self._agent.predict(
                observation,
                deterministic=True,
            )

            action_int = int(action)

            print(
                f"[RLSolver] Step {steps + 1}: "
                f"predicted action = {action_int}",
                flush=True,
            )

            # Same environment step as AgentTrainer evaluation.
            (
                observation,
                reward,
                terminated,
                truncated,
                info,
            ) = self._environment.step(action_int)

            steps += 1

            print(
                f"[RLSolver] Step {steps}: "
                f"reward={float(reward):.3f}, "
                f"terminated={terminated}, "
                f"truncated={truncated}, "
                f"info={info}",
                flush=True,
            )

        runtime_ms = int(
            (time.time() - start_time) * 1000
        )

        metrics = SolverMetrics(
            runtimeMs=runtime_ms,
            steps=steps,
            attempts=1,
        )

        game = self._environment.game

        # Same success definition as AgentTrainer._run_board().
        solved = (
            terminated
            and game.isFinished()
        )

        if solved:
            print(
                f"[RLSolver] SOLVED after "
                f"{steps} steps ({runtime_ms} ms).",
                flush=True,
            )

            raw_path = game.getState.getPath

            solution_path = SolutionPath()

            if raw_path is not None:
                for position in raw_path:
                    solution_path.add(position)

            return SolverResult(
                status=SolverStatus.SOLVED,
                path=solution_path,
                message="RL Agent successfully solved the puzzle.",
                metrics=metrics,
            )

        # Determine failure reason.
        if info.get("invalid_move", False):
            reason = "invalid move"

        elif truncated:
            reason = "maximum step limit reached"

        else:
            reason = "episode ended without solving the puzzle"

        print(
            f"[RLSolver] FAILED after "
            f"{steps} steps: {reason}.",
            flush=True,
        )

        return SolverResult(
            status=SolverStatus.FAILED,
            path=None,
            message=f"RL Agent failed: {reason}.",
            metrics=metrics,
        )

    def solve(self, board: Board) -> SolverResult:
        """
        Manages the complete lifecycle mapping a static board topology into an active ML simulation.

        Args:
            board: The static structural blueprint awaiting calculation.

        Returns:
            The finalized result envelope capturing trajectory mapping and operational telemetry.

        Implementation Details:
            Select the correct model and perform deterministic inference.
            Safely tears down lingering virtual environments from prior executions, mounts the new 
            target layout natively, queries the size cache to inject the correct neural weights, and 
            delegates execution downward. Aggressively wraps logic to catch model inference exceptions 
            and package them as graceful FAILED envelopes to prevent API-level crashes.
        """
        print(
            "\n==================================================",
            flush=True,
        )

        print(
            "[RLSolver] solve() WAS CALLED",
            flush=True,
        )

        start_time = time.time()

        try:
            board_size = self._get_board_size(board)

            print(
                f"[RLSolver] Board size: "
                f"{board_size}x{board_size}",
                flush=True,
            )

            logger.info(
                "Starting RL solver for %sx%s puzzle.",
                board_size,
                board_size,
            )

            # Close previous puzzle environment.
            if self._environment is not None:
                try:
                    self._environment.close()

                except Exception:
                    logger.warning(
                        "Could not close previous RL environment.",
                        exc_info=True,
                    )

            # Exactly the same environment class used during
            # training/evaluation.
            self._environment = RLEnvironment(board)

            # Load/reuse corresponding model.
            self._load_agent(board_size)

            print(
                "[RLSolver] Starting deterministic inference...",
                flush=True,
            )

            return self._run_episode()

        except Exception as exception:
            print(
                f"[RLSolver] ERROR: "
                f"{type(exception).__name__}: {exception}",
                flush=True,
            )

            logger.exception(
                "RLSolver failed during inference."
            )

            runtime_ms = int(
                (time.time() - start_time) * 1000
            )

            return SolverResult(
                status=SolverStatus.FAILED,
                path=None,
                message=f"RLSolver error: {exception}",
                metrics=SolverMetrics(
                    runtimeMs=runtime_ms,
                    steps=0,
                    attempts=1,
                ),
            )