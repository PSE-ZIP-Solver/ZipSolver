import inspect
import pickle
import random
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch as th
from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor
from torch.nn import functional as F

from backend.puzzle_logic import Board
from backend.rl_components import RLAgent, RLEnvironment
from offline_training.board_generator import BoardGenerator
from offline_training.training_result import TrainingResult


class DoubleDQN(DQN):
    """DQN variant that uses Double-DQN targets during network updates."""

    def train(self, gradient_steps: int, batch_size: int = 100) -> None:
        self.policy.set_training_mode(True)
        self._update_learning_rate(self.policy.optimizer)

        losses: list[float] = []

        for _ in range(gradient_steps):
            if self.replay_buffer is None:
                raise RuntimeError("Cannot train without a replay buffer.")

            replay_data = self.replay_buffer.sample(
                batch_size,
                env=self._vec_normalize_env,
            )

            replayDiscounts = getattr(replay_data, "discounts", None)
            discounts = replayDiscounts if replayDiscounts is not None else self.gamma

            with th.no_grad():
                # Online network selects the action, target network evaluates it.
                nextOnlineQValues = self.q_net(replay_data.next_observations)
                nextActions = nextOnlineQValues.argmax(dim=1, keepdim=True)

                nextTargetQValues = self.q_net_target(replay_data.next_observations)
                nextQValues = th.gather(
                    nextTargetQValues,
                    dim=1,
                    index=nextActions,
                )

                targetQValues = (
                    replay_data.rewards
                    + (1 - replay_data.dones) * discounts * nextQValues
                )

            currentQValues = self.q_net(replay_data.observations)
            currentQValues = th.gather(
                currentQValues,
                dim=1,
                index=replay_data.actions.long(),
            )

            loss = F.smooth_l1_loss(currentQValues, targetQValues)
            losses.append(loss.item())

            self.policy.optimizer.zero_grad()
            loss.backward()
            th.nn.utils.clip_grad_norm_(
                self.policy.parameters(),
                self.max_grad_norm,
            )
            self.policy.optimizer.step()

        self._n_updates += gradient_steps
        self.logger.record(
            "train/n_updates",
            self._n_updates,
            exclude="tensorboard",
        )
        self.logger.record("train/loss", float(np.mean(losses)))


class BoardSamplingEnv(gym.Env):
    """Randomly selects one environment from the current training pool on reset."""

    def __init__(self, boards: list[Board]):
        super().__init__()
        if not boards:
            raise ValueError("BoardSamplingEnv needs at least one board.")

        self.envs = [RLEnvironment(board) for board in boards]
        self.env = self.envs[0]
        self.observation_space = self.env.observation_space
        self.action_space = self.env.action_space

    def reset(self, seed: int | None = None, options=None):
        super().reset(seed=seed)
        envIndex = int(self.np_random.integers(len(self.envs)))
        self.env = self.envs[envIndex]
        return self.env.reset(seed=seed, options=options)

    def step(self, action: int):
        return self.env.step(int(action))

    def render(self, mode: str = "human"):
        return self.env.render(mode)

    @property
    def game(self):
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
        useDoubleDQN: bool = True,
        explorationInitialEps: float = 1.0,
        explorationFinalEps: float = 0.10,
        explorationFraction: float = 0.8,
        learningRate: float = 1e-4,
        learningStarts: int = 500,
        bufferSize: int = 50_000,
        batchSize: int = 64,
        targetUpdateInterval: int = 500,
        gamma: float = 0.98,
    ):
        self.boardSize = boardSize
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
        self.useDoubleDQN = useDoubleDQN

        self.explorationInitialEps = explorationInitialEps
        self.explorationFinalEps = explorationFinalEps
        self.explorationFraction = explorationFraction
        self.learningRate = learningRate
        self.learningStarts = learningStarts
        self.bufferSize = bufferSize
        self.batchSize = batchSize
        self.targetUpdateInterval = targetUpdateInterval
        self.gamma = gamma
        self.tensorboardLog = f"./logs/zip_ddqn/{boardSize}x{boardSize}/"

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
            self.evaluationBoards = self._load_evaluation_boards()
            missingBoards = nrEvaluationBoards - len(self.evaluationBoards)

            if missingBoards > 0:
                self.evaluationBoards.extend(
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
                self._save_evaluation_boards()
                print(f"Added {missingBoards} new evaluation boards.")
            elif missingBoards < 0:
                self.evaluationBoards = self.evaluationBoards[:nrEvaluationBoards]
                print(
                    f"Using the first {nrEvaluationBoards} boards from the saved "
                    "evaluation pool."
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
        self.trainingBoardsPath.parent.mkdir(parents=True, exist_ok=True)
        with self.trainingBoardsPath.open("wb") as file:
            pickle.dump(self.trainingBoards, file)
        print(f"Saved training boards to {self.trainingBoardsPath}")

    def _load_training_boards(self) -> list[Board]:
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
        self.evaluationBoardsPath.parent.mkdir(parents=True, exist_ok=True)
        with self.evaluationBoardsPath.open("wb") as file:
            pickle.dump(self.evaluationBoards, file)
        print(f"Saved evaluation boards to {self.evaluationBoardsPath}")

    def _load_evaluation_boards(self) -> list[Board]:
        with self.evaluationBoardsPath.open("rb") as file:
            boards = pickle.load(file)

        if not isinstance(boards, list) or not boards:
            raise ValueError("The saved evaluation board file is empty or invalid.")

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
        boards: list[Board] = []

        for _ in range(numberBoards):
            nrOfWaypoints = (
                random.randint(minIntermediateWaypoints, maxIntermediateWaypoints)
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
        model = getattr(agent, "_model", None)
        if model is None:
            raise AttributeError(
                "RLAgent must store its Stable-Baselines model in self._model."
            )
        return model

    @staticmethod
    def _enable_double_dqn(agent: RLAgent):
        model = AgentTrainer._get_sb3_model(agent)

        if not isinstance(model, DQN):
            raise TypeError(
                "Double DQN can only be enabled for a Stable-Baselines DQN model."
            )

        if not isinstance(model, DoubleDQN):
            model.__class__ = DoubleDQN

        print("Double DQN target calculation enabled.")
        return model

    @staticmethod
    def _replace_replay_buffer(agent: RLAgent, bufferSize: int):
        model = AgentTrainer._get_sb3_model(agent)
        oldReplayBuffer = getattr(model, "replay_buffer", None)

        if oldReplayBuffer is None:
            raise RuntimeError("The loaded DQN model has no replay buffer.")

        replayBufferClass = type(oldReplayBuffer)
        constructorArguments = {
            "buffer_size": bufferSize,
            "observation_space": model.observation_space,
            "action_space": model.action_space,
            "device": model.device,
            "n_envs": model.n_envs,
            "optimize_memory_usage": getattr(
                model,
                "optimize_memory_usage",
                False,
            ),
            "handle_timeout_termination": True,
        }

        constructorArguments.update(
            getattr(model, "replay_buffer_kwargs", None) or {}
        )

        if getattr(model, "n_steps", 1) > 1:
            constructorArguments.setdefault("n_steps", model.n_steps)
            constructorArguments.setdefault("gamma", model.gamma)

        signature = inspect.signature(replayBufferClass.__init__)
        acceptsKeywordArguments = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )

        if not acceptsKeywordArguments:
            supportedArguments = set(signature.parameters) - {"self"}
            constructorArguments = {
                name: value
                for name, value in constructorArguments.items()
                if name in supportedArguments
            }

        model.replay_buffer = replayBufferClass(**constructorArguments)
        model.buffer_size = bufferSize
        print(f"Created a new empty replay buffer with size {bufferSize}.")

    def _configure_loaded_model(self, agent: RLAgent):
        model = self._get_sb3_model(agent)
        model.learning_rate = self.learningRate
        model.lr_schedule = lambda _: self.learningRate
        model.learning_starts = self.learningStarts
        model.target_update_interval = self.targetUpdateInterval
        model.gamma = self.gamma
        model.batch_size = self.batchSize
        model.gradient_steps = 1
        model.max_grad_norm = 10

    @staticmethod
    def _replay_buffer_path(modelPath: str) -> Path:
        modelFile = Path(modelPath)
        return modelFile.with_name(f"{modelFile.stem}_replay_buffer.pkl")

    def train(self) -> RLAgent:
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
                tensorboard_log=self.tensorboardLog,
            )

            if self.loadReplayBuffer and replayBufferFile.exists():
                self._get_sb3_model(agent).load_replay_buffer(replayBufferFile)
                print(f"Loaded replay buffer from {replayBufferFile}")
            elif self.loadReplayBuffer:
                print(f"No replay buffer found at {replayBufferFile}")
            else:
                self._replace_replay_buffer(agent, bufferSize=self.bufferSize)

            self._configure_loaded_model(agent)
            agent.set_exploration_schedule(
                initial_eps=self.explorationInitialEps,
                final_eps=self.explorationFinalEps,
                fraction=self.explorationFraction,
            )
        else:
            print("Creating new agent")
            agent = RLAgent(
                trainEnv,
                learning_rate=self.learningRate,
                exploration_initial_eps=self.explorationInitialEps,
                exploration_final_eps=self.explorationFinalEps,
                exploration_fraction=self.explorationFraction,
                learning_starts=self.learningStarts,
                buffer_size=self.bufferSize,
                batch_size=self.batchSize,
                train_freq=(1, "step"),
                gradient_steps=1,
                target_update_interval=self.targetUpdateInterval,
                gamma=self.gamma,
                max_grad_norm=10,
                seed=42,
                tensorboard_log=self.tensorboardLog,
            )

        if self.useDoubleDQN:
            self._enable_double_dqn(agent)
        else:
            print("Normal DQN target calculation enabled.")

        totalTimesteps = self._totalTimesteps or 100_000

        print(f"Training on {len(self.trainingBoards)} boards.")
        print(f"Total timesteps: {totalTimesteps}")
        print(
            "Exploration schedule: "
            f"{self.explorationInitialEps} -> {self.explorationFinalEps}"
        )

        agent.learn(
            total_timesteps=totalTimesteps,
            reset_num_timesteps=True,
        )
        return agent

    def load_saved_agent(self) -> RLAgent:
        if not Path(self.modelPath).exists():
            raise FileNotFoundError(f"Model file not found: {self.modelPath}")

        boards = self.evaluationBoards or self.trainingBoards
        if not boards:
            raise ValueError("At least one board is required to load the model.")

        return RLAgent(
            RLEnvironment(boards[0]),
            model_path=self.modelPath,
        )

    def evaluate(
        self,
        agent: RLAgent,
        boards: list[Board] | None = None,
        showExamples: bool = False,
        boardType: str = "evaluation",
    ) -> TrainingResult:
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

    def _run_board(self, agent: RLAgent, board: Board) -> tuple[bool, float]:
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
        if board is None:
            print(f"\n{missingMessage}")
            return
        self._show_agent_run(agent, board, title)

    def _show_agent_run(self, agent: RLAgent, board: Board, title: str):
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
        if not self.trainingBoards:
            print("\nNo training board available.")
            return

        self._show_agent_run(
            agent,
            self.trainingBoards[0],
            "Deterministic run on first training board after training",
        )

    def print_boards(self, boards: list[Board], title: str):
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
        print(f"\n{title}:")
        print("Solved:", result.getSolveCount)
        print("Total Boards:", result.getTotalBoards)
        print("Average reward:", result.getAverageReward)
        print("Success rate:", result.getSuccessRate)

    def save(self, agent: RLAgent, modelPath: str | None = None):
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
    BOARD_SIZE = 7

    RANDOMIZE_BOARD_COMPLEXITY = True
    MIN_NR_OF_WALLS = 0
    NR_OF_WALLS = 34
    MIN_NR_OF_WAYPOINTS = 0
    NR_OF_WAYPOINTS = 34

    NR_TRAINING_BOARDS = 40
    NR_EVALUATION_BOARDS = 100  

    # Reuse the solved first board and append two new 34/34 boards.
    USE_SAVED_TRAINING_BOARDS = True
    TRAINING_BOARDS_PATH = (
        "offline_training/training_boards/7x7/"
        "7x7-curriculum-34walls-34wp.pkl"
    )

    USE_SAVED_EVALUATION_BOARDS = True
    EVALUATION_BOARDS_PATH = (
        "offline_training/evaluation_boards/7x7/"
        "7x7-evaluation-34walls-34wp-100boards.pkl"
    )

    MODEL_PATH = (
        "offline_training/trained_models/7x7/"
        "7x7-agent.zip"
    )

    USE_DOUBLE_DQN = True

    # Continue from the successful 1-board model on the expanded 3-board pool.
    LOAD_EXISTING_MODEL = True
    RESET_MODEL = False
    LOAD_REPLAY_BUFFER = False

    TRAIN_MODEL = True
    PRINT_TRAINING_BOARDS = False
    SHOW_FIRST_TRAINING_RUN = True
    EVALUATE_TRAINING_BOARDS = True
    EVALUATE_EVALUATION_BOARDS = False
    SHOW_EVALUATION_EXAMPLES = False

    trainer = AgentTrainer(
        boardSize=BOARD_SIZE,
        nrOfWalls=NR_OF_WALLS,
        nrOfWaypoints=NR_OF_WAYPOINTS,
        modelPath=MODEL_PATH,
        minNrOfWalls=MIN_NR_OF_WALLS,
        minNrOfWaypoints=MIN_NR_OF_WAYPOINTS,
        nrTrainingBoards=NR_TRAINING_BOARDS,
        nrEvaluationBoards=NR_EVALUATION_BOARDS,
        timestepsPerBoard=1_500_000,
        loadExistingModel=LOAD_EXISTING_MODEL,
        resetModel=RESET_MODEL,
        randomizeBoardComplexity=RANDOMIZE_BOARD_COMPLEXITY,
        useSavedTrainingBoards=USE_SAVED_TRAINING_BOARDS,
        loadReplayBuffer=LOAD_REPLAY_BUFFER,
        trainingBoardsPath=TRAINING_BOARDS_PATH,
        useSavedEvaluationBoards=USE_SAVED_EVALUATION_BOARDS,
        evaluationBoardsPath=EVALUATION_BOARDS_PATH,
        useDoubleDQN=USE_DOUBLE_DQN,
        explorationInitialEps=0.5,
        explorationFinalEps=0.05,
        explorationFraction=0.8,
        learningRate=1e-4,
        learningStarts=500,
        bufferSize=50_000,
        batchSize=64,
        targetUpdateInterval=500,
        gamma=0.98,
    )

    agent = trainer.train() if TRAIN_MODEL else trainer.load_saved_agent()

    if TRAIN_MODEL:
        trainer.save(agent)

        if SHOW_FIRST_TRAINING_RUN:
            trainer.show_first_training_board_run(agent)

    if PRINT_TRAINING_BOARDS:
        trainer.print_boards(
            trainer.trainingBoards,
            "Boards used during training",
        )

    if EVALUATE_TRAINING_BOARDS:
        trainingResult = trainer.evaluate(
            agent,
            trainer.trainingBoards,
        )
        trainer.print_result(
            "Evaluation result on training boards",
            trainingResult,
        )

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
