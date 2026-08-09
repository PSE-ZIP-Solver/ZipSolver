import pickle
import random
from pathlib import Path

import gymnasium as gym
from stable_baselines3.common.monitor import Monitor

from backend.puzzle_logic import Board
from backend.rl_components import RLAgent, RLEnvironment
from offline_training.board_generator import BoardGenerator
from offline_training.training_result import TrainingResult


class BoardSamplingEnv(gym.Env):
    """Gym environment that randomly selects one of the training boards on every reset."""

    def __init__(self, boards: list[Board]):
        super().__init__()
        if not boards:
            raise ValueError("BoardSamplingEnv needs at least one board.")

        # Create one environment per board once.
        # This is faster than creating a new RLEnvironment on every reset.
        self.envs = [RLEnvironment(board) for board in boards]
        self.env = random.choice(self.envs)
        self.observation_space = self.env.observation_space
        self.action_space = self.env.action_space

    def reset(self, seed: int | None = None, options=None):
        """Reset with a randomly selected existing environment."""
        super().reset(seed=seed)
        self.env = random.choice(self.envs)
        return self.env.reset(seed=seed, options=options)

    def step(self, action: int):
        """Forward the action to the currently selected environment."""
        return self.env.step(int(action))

    def render(self, mode: str = "human"):
        """Render the currently selected environment."""
        return self.env.render(mode)

    @property
    def game(self):
        """Expose the current game for debugging and solve checks."""
        return self.env.game


class AgentTrainer:
    def __init__(
        self,
        boardSize: int,
        nrOfWalls: int,
        nrOfWaypoints: int,
        modelPath: str,
        nrTrainingBoards: int = 100,
        nrEvaluationBoards: int = 100,
        trainingBoards: list[Board] | None = None,
        evaluationBoards: list[Board] | None = None,
        timestepsPerBoard: int | None = None,
        loadExistingModel: bool = True,
        resetModel: bool = False,
        randomizeBoardComplexity: bool = True,
        minNrOfWalls: int = 0,
        minNrOfWaypoints: int = 0,
        useSavedTrainingBoards: bool = False,
        loadReplayBuffer: bool = True,
        trainingBoardsPath: str = "offline_training/training_boards/training-boards.pkl",
        useSavedEvaluationBoards: bool = False,
        evaluationBoardsPath: str = "offline_training/evaluation_boards/evaluation-boards.pkl",
    ):
        """
        Creates a trainer configured with training and evaluation board sets.

        Args:
            boardSize: Side length of each square board.
            nrOfWalls: Maximum number of walls per generated board.
            nrOfWaypoints: Maximum number of intermediate waypoints per generated board.
            modelPath: Path used for loading/saving the model.
            nrTrainingBoards: Number of generated training boards.
            nrEvaluationBoards: Number of generated evaluation boards.
            trainingBoards: Optional externally prepared training boards.
            evaluationBoards: Optional externally prepared evaluation boards.
            timestepsPerBoard: Kept for compatibility.
                It is now interpreted as total training timesteps.
            loadExistingModel: If True, loads modelPath if it exists.
            resetModel: If True, deletes modelPath before training and starts fresh.
            randomizeBoardComplexity: If True, randomly selects waypoint and wall
                counts between the configured minimum and maximum values. If False,
                uses the configured maximum values as exact counts.
            minNrOfWalls: Minimum number of walls for randomized board generation.
            minNrOfWaypoints: Minimum number of intermediate waypoints for randomized
                board generation.
            useSavedTrainingBoards: If True, loads the previously saved training boards.
            loadReplayBuffer: If True, loads the previously saved replay buffer.
            trainingBoardsPath: Path used for saving/loading the training board pool.
            useSavedEvaluationBoards: If True, reuses a fixed saved evaluation set.
                If the file does not exist yet, it is generated and saved automatically.
            evaluationBoardsPath: Path used for saving/loading the evaluation board set.
        """
        self.modelPath = modelPath
        self._totalTimesteps = timestepsPerBoard
        self.loadExistingModel = loadExistingModel
        self.resetModel = resetModel
        self.randomizeBoardComplexity = randomizeBoardComplexity
        self.minNrOfWalls = minNrOfWalls
        self.minNrOfWaypoints = minNrOfWaypoints
        self.loadReplayBuffer = loadReplayBuffer
        self.trainingBoardsPath = Path(trainingBoardsPath)
        self.evaluationBoardsPath = Path(evaluationBoardsPath)

        if not 0 <= self.minNrOfWalls <= nrOfWalls:
            raise ValueError("minNrOfWalls must be between 0 and nrOfWalls.")

        if not 0 <= self.minNrOfWaypoints <= nrOfWaypoints:
            raise ValueError(
                "minNrOfWaypoints must be between 0 and nrOfWaypoints."
            )

        if trainingBoards is not None:
            self.trainingBoards = trainingBoards
        elif useSavedTrainingBoards:
            self.trainingBoards = self._load_training_boards()
            missingBoards = nrTrainingBoards - len(self.trainingBoards)

            if missingBoards < 0:
                raise ValueError(
                    f"Saved pool contains {len(self.trainingBoards)} boards, but "
                    f"nrTrainingBoards is only {nrTrainingBoards}."
                )

            if missingBoards > 0:
                self.trainingBoards.extend(
                    self._generate_random_boards(
                        boardSize,
                        self.minNrOfWaypoints,
                        nrOfWaypoints,
                        self.minNrOfWalls,
                        nrOfWalls,
                        missingBoards,
                        self.randomizeBoardComplexity,
                    )
                )
                self._save_training_boards()
                print(f"Added {missingBoards} new training boards.")
        else:
            self.trainingBoards = self._generate_random_boards(
                boardSize,
                self.minNrOfWaypoints,
                nrOfWaypoints,
                self.minNrOfWalls,
                nrOfWalls,
                nrTrainingBoards,
                self.randomizeBoardComplexity,
            )
            self._save_training_boards()

        if evaluationBoards is not None:
            self.evaluationBoards = evaluationBoards
        elif useSavedEvaluationBoards and self.evaluationBoardsPath.exists():
            self.evaluationBoards = self._load_evaluation_boards(
                nrEvaluationBoards
            )
        else:
            self.evaluationBoards = self._generate_random_boards(
                boardSize,
                self.minNrOfWaypoints,
                nrOfWaypoints,
                self.minNrOfWalls,
                nrOfWalls,
                nrEvaluationBoards,
                self.randomizeBoardComplexity,
            )

            if useSavedEvaluationBoards:
                self._save_evaluation_boards()

    def _save_training_boards(self):
        """Save the generated training board pool for later training runs."""
        self.trainingBoardsPath.parent.mkdir(parents=True, exist_ok=True)
        with self.trainingBoardsPath.open("wb") as file:
            pickle.dump(self.trainingBoards, file)
        print(f"Saved training boards to {self.trainingBoardsPath}")

    def _load_training_boards(self) -> list[Board]:
        """Load the training board pool created during an earlier run."""
        if not self.trainingBoardsPath.exists():
            raise FileNotFoundError(
                f"Training board file not found: {self.trainingBoardsPath}"
            )

        with self.trainingBoardsPath.open("rb") as file:
            boards = pickle.load(file)

        if not isinstance(boards, list) or not boards:
            raise ValueError("The saved training board file is empty or invalid.")

        print(f"Loaded training boards from {self.trainingBoardsPath}")
        return boards

    def _save_evaluation_boards(self):
        """Save one fixed evaluation board set for comparable future runs."""
        self.evaluationBoardsPath.parent.mkdir(parents=True, exist_ok=True)
        with self.evaluationBoardsPath.open("wb") as file:
            pickle.dump(self.evaluationBoards, file)
        print(f"Saved evaluation boards to {self.evaluationBoardsPath}")

    def _load_evaluation_boards(
        self,
        expectedNumberBoards: int,
    ) -> list[Board]:
        """Load the fixed evaluation board set created during an earlier run."""
        with self.evaluationBoardsPath.open("rb") as file:
            boards = pickle.load(file)

        if not isinstance(boards, list) or not boards:
            raise ValueError("The saved evaluation board file is empty or invalid.")

        if len(boards) != expectedNumberBoards:
            raise ValueError(
                f"Saved evaluation set contains {len(boards)} boards, but "
                f"nrEvaluationBoards is {expectedNumberBoards}."
            )

        print(f"Loaded evaluation boards from {self.evaluationBoardsPath}")
        return boards

    def _generate_random_boards(
        self,
        boardSize: int,
        minIntermediateWaypoints: int,
        maxIntermediateWaypoints: int,
        minWalls: int,
        maxWalls: int,
        numberBoards: int,
        randomizeBoardComplexity: bool,
    ) -> list[Board]:
        """Generate random boards with fixed or random waypoint and wall counts."""
        boards: list[Board] = []

        for _ in range(numberBoards):
            nrOfWaypoints = (
                random.randint(
                    minIntermediateWaypoints,
                    maxIntermediateWaypoints,
                )
                if randomizeBoardComplexity
                else maxIntermediateWaypoints
            )
            nrOfWalls = (
                random.randint(minWalls, maxWalls)
                if randomizeBoardComplexity
                else maxWalls
            )

            boards.append(
                BoardGenerator.generate(
                    boardSize,
                    nrOfWaypoints,
                    nrOfWalls,
                    1,
                )[0]
            )

        return boards

    @staticmethod
    def _get_sb3_model(agent: RLAgent):
        """Return the Stable-Baselines model stored inside RLAgent."""
        model = getattr(agent, "_model", None)
        if model is None:
            raise AttributeError(
                "RLAgent must store its Stable-Baselines model in self._model."
            )
        return model

    @staticmethod
    def _replay_buffer_path(modelPath: str) -> Path:
        """Create a replay-buffer path next to the corresponding model file."""
        modelFile = Path(modelPath)
        return modelFile.with_name(f"{modelFile.stem}_replay_buffer.pkl")

    def train(self) -> RLAgent:
        """Train one RLAgent across randomly sampled training boards."""
        if not self.trainingBoards:
            raise ValueError("Cannot train without at least one training board.")

        modelFile = Path(self.modelPath)
        replayBufferFile = self._replay_buffer_path(self.modelPath)

        if self.resetModel:
            for file in (modelFile, replayBufferFile):
                if file.exists():
                    print(f"Resetting training data: deleting {file}")
                    file.unlink()

        trainEnv = Monitor(BoardSamplingEnv(self.trainingBoards))
        if self.loadExistingModel and modelFile.exists():
            print(f"Loading existing model from {self.modelPath}")
            agent = RLAgent(
                trainEnv,
                model_path=self.modelPath,
                tensorboard_log="./logs/zip_dqn/6x6/",
            )

            if self.loadReplayBuffer and replayBufferFile.exists():
                self._get_sb3_model(agent).load_replay_buffer(replayBufferFile)
                print(f"Loaded replay buffer from {replayBufferFile}")
            elif self.loadReplayBuffer:
                print(f"No replay buffer found at {replayBufferFile}")
            else:
                print("Starting with an empty replay buffer.")

            # Lower exploration for fine-tuning an already trained model.
            agent.set_exploration_schedule(
                initial_eps=0.2,
                final_eps=0.05,
                fraction=0.8,
            )
        else:
            print("Creating new agent")
            agent = RLAgent(
                trainEnv,
                learning_rate=1e-4,              # Controls how strongly the network weights are changed during each gradient/network update.
                exploration_initial_eps=1.0,     # Initial probability of choosing a random action.
                exploration_final_eps=0.10,      # Final minimum probability of choosing a random action.
                exploration_fraction=0.8,        # Fraction of training over which exploration is reduced.
                learning_starts=500,             # Number of steps before the model starts learning.
                buffer_size=50_000,              # Maximum number of transitions stored in the replay buffer.
                batch_size=64,                   # Number of samples used for one training update.
                train_freq=(1, "step"),          # Update neural network (training) after every completed episode.
                gradient_steps=1,                # For each training trigger, do ONE weight update using one sampled batch.
                target_update_interval=500,      # Copy the learned network weights to the target network every 500 steps.
                gamma=0.98,                      # Discount factor: controls how much future rewards matter -> makes learning more stable.
                max_grad_norm=10,                # Limits very large gradient updates to avoid unstable training.
                seed=42,                         # Sets a random seed to make training behavior more reproducible (e.g.).
                tensorboard_log="./logs/zip_dqn/6x6/",
            )

        totalTimesteps = (
            self._totalTimesteps
            if self._totalTimesteps is not None
            else 100_000
        )
        print(f"Training on {len(self.trainingBoards)} boards.")
        print(f"Total timesteps: {totalTimesteps}")

        # True resets only the SB3 step counter / exploration schedule.
        # It does not delete the loaded model weights.
        agent.learn(total_timesteps=totalTimesteps, reset_num_timesteps=True)
        return agent

    def load_saved_agent(self) -> RLAgent:
        """Load a saved model without further training."""
        if not Path(self.modelPath).exists():
            raise FileNotFoundError(f"Model file not found: {self.modelPath}")

        boards = self.evaluationBoards or self.trainingBoards
        if not boards:
            raise ValueError("At least one board is required to load the model.")

        # The loaded model needs one compatible environment.
        # During evaluation, evaluate() switches the environment for every board.
        return RLAgent(RLEnvironment(boards[0]), model_path=self.modelPath)

    def evaluate(
        self,
        agent: RLAgent,
        boards: list[Board] | None = None,
        showExamples: bool = False,
        boardType: str = "evaluation",
    ) -> TrainingResult:
        """Evaluate a trained RLAgent on the provided boards."""
        boards = self.evaluationBoards if boards is None else boards
        if not boards:
            return TrainingResult(0, 0, 0.0, 0.0)

        solveCount = 0
        rewards = 0.0
        firstSolvedBoard = None
        firstFailedBoard = None

        for board in boards:
            solved, boardReward = self._run_board(agent, board)
            rewards += boardReward
            solveCount += int(solved)

            if solved and firstSolvedBoard is None:
                firstSolvedBoard = board
            elif not solved and firstFailedBoard is None:
                firstFailedBoard = board

        if showExamples:
            self._show_example(
                agent,
                firstSolvedBoard,
                f"Example solved {boardType} board",
                f"No solved {boardType} board found.",
            )
            self._show_example(
                agent,
                firstFailedBoard,
                f"Example failed {boardType} board",
                f"No failed {boardType} board found. The agent solved all boards.",
            )

        totalBoards = len(boards)
        return TrainingResult(
            solveCount,
            totalBoards,
            rewards / totalBoards,
            solveCount / totalBoards,
        )

    def evaluate_saved_model(self, showExamples: bool = False) -> TrainingResult:
        """Load a saved model and evaluate it without further training."""
        return self.evaluate(self.load_saved_agent(), showExamples=showExamples)

    def evaluate_with_examples(self, agent: RLAgent) -> TrainingResult:
        """Evaluate the agent and afterwards show one solved and one failed example."""
        return self.evaluate(agent, showExamples=True)

    def _run_board(self, agent: RLAgent, board: Board) -> tuple[bool, float]:
        """Run one deterministic evaluation episode."""
        env = RLEnvironment(board)
        agent.set_env(env)
        observation, _ = env.reset()
        terminated = truncated = False
        rewardSum = 0.0

        while not terminated and not truncated:
            action = agent.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, _ = env.step(int(action))
            rewardSum += float(reward)

        solved = terminated and env.game.isFinished()
        env.close()
        return solved, rewardSum

    def _show_example(
        self,
        agent: RLAgent,
        board: Board | None,
        title: str,
        missingMessage: str,
    ):
        """Show an example board if one is available."""
        if board is None:
            print(f"\n{missingMessage}")
            return
        self._show_agent_run(agent, board, title)

    def _show_agent_run(self, agent: RLAgent, board: Board, title: str):
        """Render one deterministic agent run on a given board."""
        print(f"\n{title}:")
        env = RLEnvironment(board)
        agent.set_env(env)
        result = agent.solve(
            deterministic=True,
            max_steps=env.config.max_steps,
            render=True,
        )
        print("\nRun result:")
        print(result)
        env.close()

    def show_first_training_board_run(self, agent: RLAgent):
        """Render a deterministic run on the first board used during training."""
        if not self.trainingBoards:
            print("\nNo training board available.")
            return

        self._show_agent_run(
            agent,
            self.trainingBoards[0],
            "Deterministic run on first training board after training",
        )

    def print_boards(self, boards: list[Board], title: str):
        """Print the initial state of the provided boards."""
        print(f"\n{title}:")
        for index, board in enumerate(boards, start=1):
            print(f"\nBoard {index}:")
            env = RLEnvironment(board)
            env.reset()
            renderedBoard = env.render("ansi")
            if renderedBoard is not None:
                print(renderedBoard)
            env.close()

    @staticmethod
    def print_result(title: str, result: TrainingResult):
        """Print one evaluation result."""
        print(f"\n{title}:")
        print("Solved:", result.getSolveCount)
        print("Total Boards:", result.getTotalBoards)
        print("Average reward:", result.getAverageReward)
        print("Success rate:", result.getSuccessRate)

    def save(self, agent: RLAgent, modelPath: str | None = None):
        """Save the trained agent and its replay buffer."""
        path = modelPath if modelPath else self.modelPath
        if not path:
            raise ValueError("A valid model path is required.")

        modelFile = Path(path)
        modelFile.parent.mkdir(parents=True, exist_ok=True)
        agent.save(path)

        replayBufferFile = self._replay_buffer_path(path)
        self._get_sb3_model(agent).save_replay_buffer(replayBufferFile)
        print(f"Saved replay buffer to {replayBufferFile}")


if __name__ == "__main__":
    RANDOMIZE_BOARD_COMPLEXITY = True
    MIN_NR_OF_WALLS = 5
    NR_OF_WALLS = 20
    MIN_NR_OF_WAYPOINTS = 5
    NR_OF_WAYPOINTS = 20

    USE_SAVED_TRAINING_BOARDS = True
    LOAD_REPLAY_BUFFER = True # only True for several runs on same training set (continue session)
    TRAINING_BOARDS_PATH = ("offline_training/training_boards/6x6-generalization-3000boards-5to20.pkl")

    USE_SAVED_EVALUATION_BOARDS = True # Also needs to be true for saving new created ones
    EVALUATION_BOARDS_PATH = "offline_training/evaluation_boards/6x6-evaluation-5to20-1000boards.pkl"

    TRAIN_MODEL = True
    PRINT_TRAINING_BOARDS = False
    SHOW_FIRST_TRAINING_RUN = False
    EVALUATE_TRAINING_BOARDS = True
    EVALUATE_EVALUATION_BOARDS = True
    SHOW_EVALUATION_EXAMPLES = False

    trainer = AgentTrainer(
        boardSize=6,
        nrOfWalls=NR_OF_WALLS,
        nrOfWaypoints=NR_OF_WAYPOINTS,
        modelPath="offline_training/trained_models/trained-model.zip",
        minNrOfWalls=MIN_NR_OF_WALLS,
        minNrOfWaypoints=MIN_NR_OF_WAYPOINTS,

        # number of training boards in the training pool
        nrTrainingBoards=3000,

        # Evaluation boards for testing the saved model.
        nrEvaluationBoards=1000, 

        # Total time steps
        timestepsPerBoard= 1_000_000,

        loadExistingModel=True,
        resetModel=False,
        randomizeBoardComplexity=RANDOMIZE_BOARD_COMPLEXITY,
        useSavedTrainingBoards=USE_SAVED_TRAINING_BOARDS,
        loadReplayBuffer=LOAD_REPLAY_BUFFER,
        trainingBoardsPath=TRAINING_BOARDS_PATH,
        useSavedEvaluationBoards=USE_SAVED_EVALUATION_BOARDS,
        evaluationBoardsPath=EVALUATION_BOARDS_PATH,
    )

    agent = trainer.train() if TRAIN_MODEL else trainer.load_saved_agent()
    if TRAIN_MODEL:
        trainer.save(agent)

        if SHOW_FIRST_TRAINING_RUN:
            trainer.show_first_training_board_run(agent)

    if PRINT_TRAINING_BOARDS:
        trainer.print_boards(trainer.trainingBoards, "Boards used during training")

    if EVALUATE_TRAINING_BOARDS:
        trainingResult = trainer.evaluate(agent, trainer.trainingBoards)
        trainer.print_result("Evaluation result on training boards", trainingResult)

    if EVALUATE_EVALUATION_BOARDS:
        evaluationResult = trainer.evaluate(
            agent,
            trainer.evaluationBoards,
            showExamples=SHOW_EVALUATION_EXAMPLES,
        )
        trainer.print_result(
            "Evaluation result on unseen evaluation boards",
            evaluationResult,
        )
