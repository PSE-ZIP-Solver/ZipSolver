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

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv


def make_sampling_env(boards: list[Board]):
    """Factory function to create isolated env instances for multiprocessing."""
    def _init():
        # Wrap each process instance in Monitor for proper SB3 logging
        return Monitor(BoardSamplingEnv(boards))
    return _init


class DoubleDQN(DQN):
    """DQN variant that uses Double-DQN targets during network updates."""

    def train(self, gradient_steps: int, batch_size: int = 100) -> None:
        """
        Update the Q-network using Double-DQN target calculation.

        The online network selects the best next action. The target network
        evaluates only that selected action. This reduces Q-value overestimation.
        """
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
                nextOnlineQValues = self.q_net(replay_data.next_observations)
                nextActions = nextOnlineQValues.argmax(dim=1, keepdim=True)

                nextTargetQValues = self.q_net_target(
                    replay_data.next_observations
                )
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
    """Gym environment that randomly selects one of the training boards on every reset."""

    def __init__(self, boards: list[Board]):
        super().__init__()
        if not boards:
            raise ValueError("BoardSamplingEnv needs at least one board.")

        self.envs = [RLEnvironment(board) for board in boards]
        self.env = self.envs[0]
        self.observation_space = self.env.observation_space
        self.action_space = self.env.action_space

    def reset(self, seed: int | None = None, options=None):
        """Reset with a randomly selected existing environment."""
        super().reset(seed=seed)
        envIndex = int(self.np_random.integers(len(self.envs)))
        self.env = self.envs[envIndex]
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
        nEnvs: int = 24,
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
    ):
        self.nEnvs = nEnvs
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
            print(f"Generating board {len(boards) + 1}/{numberBoards}...")
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

    @staticmethod
    def _configure_loaded_model(agent: RLAgent):
        model = AgentTrainer._get_sb3_model(agent)
        fineTuningLearningRate = 3e-5
        model.learning_rate = fineTuningLearningRate
        model.lr_schedule = lambda _: fineTuningLearningRate

        model.learning_starts = 10_000
        model.target_update_interval = 5_000
        model.gamma = 0.995
        model.batch_size = 512
        model.gradient_steps = 1
        model.max_grad_norm = 10

        replayBuffer = getattr(model, "replay_buffer", None)
        replayBufferSize = getattr(replayBuffer, "buffer_size", "unknown")
        print(f"Active replay buffer size: {replayBufferSize}")

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

        # Build parallelized environment across N CPU cores
        print(f"Spawning {self.nEnvs} parallel environment processes...")
        env_factories = [make_sampling_env(self.trainingBoards) for _ in range(self.nEnvs)]
        trainEnv = SubprocVecEnv(env_factories)

        if self.loadExistingModel and modelFile.exists():
            print(f"Loading existing model from {self.modelPath}")
            agent = RLAgent(
                trainEnv,
                model_path=self.modelPath,
                tensorboard_log="./logs/zip_dqn/8x8/",
            )

            if self.loadReplayBuffer and replayBufferFile.exists():
                self._get_sb3_model(agent).load_replay_buffer(replayBufferFile)
                print(f"Loaded replay buffer from {replayBufferFile}")
            elif self.loadReplayBuffer:
                print(f"No replay buffer found at {replayBufferFile}")
            else:
                print("Starting with an empty replay buffer.")
                self._replace_replay_buffer(agent, bufferSize=2_000_000)

            self._configure_loaded_model(agent)

            agent.set_exploration_schedule(
                initial_eps=0.2,
                final_eps=0.02,
                fraction=0.3,
            )
        else:
            print("Creating new agent")
            agent = RLAgent(
                trainEnv,
                learning_rate=1e-4,
                exploration_initial_eps=1.0,
                exploration_final_eps=0.05,
                exploration_fraction=0.4,
                learning_starts=10_000,
                buffer_size=2_000_000,
                batch_size=512,
                train_freq=(1, "step"),
                gradient_steps=1,
                target_update_interval=10_000,
                gamma=0.995,
                max_grad_norm=10,
                seed=42,
                tensorboard_log="./logs/zip_dqn/8x8_v2/",
            )

        if self.useDoubleDQN:
            self._enable_double_dqn(agent)
        else:
            print("Normal DQN target calculation enabled.")

        totalTimesteps = (
            self._totalTimesteps
            if self._totalTimesteps is not None
            else 2_500_000
        )
        print(f"Training on {len(self.trainingBoards)} boards.")
        print(f"Total timesteps: {totalTimesteps}")

        agent.learn(total_timesteps=totalTimesteps, reset_num_timesteps=True)
        return agent

    def load_saved_agent(self) -> RLAgent:
        if not Path(self.modelPath).exists():
            raise FileNotFoundError(f"Model file not found: {self.modelPath}")

        boards = self.evaluationBoards or self.trainingBoards
        if not boards:
            raise ValueError("At least one board is required to load the model.")

        return RLAgent(RLEnvironment(boards[0]), model_path=self.modelPath)

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

    def evaluate_saved_model(self, showExamples: bool = False) -> TrainingResult:
        return self.evaluate(self.load_saved_agent(), showExamples=showExamples)

    def evaluate_with_examples(self, agent: RLAgent) -> TrainingResult:
        return self.evaluate(agent, showExamples=True)

    def _run_board(self, agent: RLAgent, board: Board) -> tuple[bool, float]:
        """Run one deterministic evaluation episode without setting env on the agent."""
        env = RLEnvironment(board)
        observation, _ = env.reset()
        terminated = truncated = False
        rewardSum = 0.0

        while not terminated and not truncated:
            action = agent.predict(observation, deterministic=True)


            observation, reward, terminated, truncated, _ = env.step(action)
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
        """Render one deterministic agent run on a given board manually."""
        print(f"\n{title}:")
        env = RLEnvironment(board)
        observation, _ = env.reset()
        terminated = truncated = False

        for _ in range(env.config.max_steps):
            env.render()
            action = agent.predict(observation, deterministic=True)
            observation, _, terminated, truncated, _ = env.step(int(action))

            if terminated or truncated:
                break

        env.render()
        solved = terminated and env.game.isFinished()

        print("\nRun result:")
        print(f"{{'solved': {solved}, 'truncated': {truncated}}}")
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
    RANDOMIZE_BOARD_COMPLEXITY = True
    MIN_NR_OF_WALLS = 10
    NR_OF_WALLS = 45
    MIN_NR_OF_WAYPOINTS = 0
    NR_OF_WAYPOINTS = 45

    USE_SAVED_TRAINING_BOARDS = False
    LOAD_REPLAY_BUFFER = True

    TRAINING_BOARDS_PATH = "offline_training/training_boards/8x8_V2_RUN2.pkl"

    USE_SAVED_EVALUATION_BOARDS = True
    EVALUATION_BOARDS_PATH = "offline_training/evaluation_boards/8x8-evaluation-10000boards_broad.pkl"

    USE_DOUBLE_DQN = True

    TRAIN_MODEL = True
    PRINT_TRAINING_BOARDS = False
    SHOW_FIRST_TRAINING_RUN = True
    EVALUATE_TRAINING_BOARDS = True
    EVALUATE_EVALUATION_BOARDS = True
    SHOW_EVALUATION_EXAMPLES = False

    trainer = AgentTrainer(
        boardSize=8,
        nrOfWalls=NR_OF_WALLS,
        nrOfWaypoints=NR_OF_WAYPOINTS,
        modelPath="offline_training/trained_models/8x8_V2.zip",
        minNrOfWalls=MIN_NR_OF_WALLS,
        minNrOfWaypoints=MIN_NR_OF_WAYPOINTS,
        nrTrainingBoards=10000,
        nrEvaluationBoards=10000,
        timestepsPerBoard=20_000_000,
        loadExistingModel=True,
        resetModel=False,
        randomizeBoardComplexity=RANDOMIZE_BOARD_COMPLEXITY,
        useSavedTrainingBoards=USE_SAVED_TRAINING_BOARDS,
        loadReplayBuffer=LOAD_REPLAY_BUFFER,
        trainingBoardsPath=TRAINING_BOARDS_PATH,
        useSavedEvaluationBoards=USE_SAVED_EVALUATION_BOARDS,
        evaluationBoardsPath=EVALUATION_BOARDS_PATH,
        useDoubleDQN=USE_DOUBLE_DQN,
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