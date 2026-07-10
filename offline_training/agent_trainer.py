import random
from pathlib import Path

import gymnasium as gym
from stable_baselines3.common.monitor import Monitor

from backend.puzzle_logic import Board
from backend.rl_components import RLAgent, RLEnvironment
from offline_training.board_generator import BoardGenerator
from offline_training.training_result import TrainingResult


class BoardSamplingEnv(gym.Env):
    """Gym environment that randomly selects a training board on every reset."""

    def __init__(self, boards: list[Board]):
        super().__init__()

        if not boards:
            raise ValueError("BoardSamplingEnv needs at least one board.")

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
        """Expose current game for debugging if needed."""
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
    ):
        """
        Creates a trainer configured with training/evaluation board sets.

        Args:
            boardSize (int): Side length of each square board.
            nrOfWalls (int): Maximum number of walls per generated board.
            nrOfWaypoints (int): Maximum number of intermediate waypoints per board.
            modelPath (str): Path used for loading/saving the model.
            nrTrainingBoards (int): Number of generated training boards.
            nrEvaluationBoards (int): Number of generated evaluation boards.
            trainingBoards (list[Board] | None): Optional externally prepared training boards.
            evaluationBoards (list[Board] | None): Optional externally prepared evaluation boards.
            timestepsPerBoard (int | None): Kept for compatibility.
                Now interpreted as total training timesteps.
            loadExistingModel (bool): If True, loads modelPath if it exists.
            resetModel (bool): If True, deletes modelPath before training and starts fresh.
        """
        self.modelPath = modelPath
        self._totalTimesteps = timestepsPerBoard
        self.loadExistingModel = loadExistingModel
        self.resetModel = resetModel

        self.trainingBoards = (
            trainingBoards
            if trainingBoards is not None
            else self._generate_random_boards(
                boardSize=boardSize,
                maxIntermediateWaypoints=nrOfWaypoints,
                maxWalls=nrOfWalls,
                numberBoards=nrTrainingBoards,
            )
        )

        self.evaluationBoards = (
            evaluationBoards
            if evaluationBoards is not None
            else self._generate_random_boards(
                boardSize=boardSize,
                maxIntermediateWaypoints=nrOfWaypoints,
                maxWalls=nrOfWalls,
                numberBoards=nrEvaluationBoards,
            )
        )

    def _generate_random_boards(
        self,
        boardSize: int,
        maxIntermediateWaypoints: int,
        maxWalls: int,
        numberBoards: int,
    ) -> list[Board]:
        """Generate boards with random numbers of waypoints and walls."""
        boards: list[Board] = []

        for _ in range(numberBoards):
            intermediateWaypoints = random.randint(0, maxIntermediateWaypoints)
            walls = random.randint(0, maxWalls)

            board = BoardGenerator.generate(
                boardSize,
                intermediateWaypoints,
                walls,
                1,
            )[0]

            boards.append(board)

        return boards

    def train(self) -> RLAgent:
        """Train one RLAgent across randomly sampled training boards."""
        if not self.trainingBoards:
            raise ValueError("Cannot train without at least one training board.")

        modelFile = Path(self.modelPath)

        if self.resetModel and modelFile.exists():
            print(f"Resetting model: deleting {self.modelPath}")
            modelFile.unlink()

        trainEnv = Monitor(BoardSamplingEnv(self.trainingBoards))

        if self.loadExistingModel and modelFile.exists():
            print(f"Loading existing model from {self.modelPath}")
            agent = RLAgent(trainEnv, model_path=self.modelPath)

            agent.set_exploration_schedule(
                initial_eps=0.2,
                final_eps=0.05,
                fraction=0.8,
            )
        else:
            print("Creating new agent")
            agent = RLAgent(
                trainEnv,
                learning_rate=1e-4,
                exploration_initial_eps=0.6,
                exploration_final_eps=0.10,
                exploration_fraction=0.8,
                learning_starts=500,
                buffer_size=50_000,
                batch_size=64,
                train_freq=(1, "step"),
                gradient_steps=1,
                target_update_interval=500,
                gamma=0.95,
                max_grad_norm=10,
                seed=42,
                tensorboard_log="./logs/zip_dqn/",
            )

        totalTimesteps = (
            self._totalTimesteps
            if self._totalTimesteps is not None
            else 100_000
        )

        print(f"Training on {len(self.trainingBoards)} boards.")
        print(f"Total timesteps: {totalTimesteps}")

        agent.learn(
            total_timesteps=totalTimesteps,
            reset_num_timesteps=True,
        )

        return agent

    def evaluate(self, agent: RLAgent) -> TrainingResult:
        """Evaluate a trained RLAgent on all configured evaluation boards."""
        totalBoards = len(self.evaluationBoards)

        if totalBoards == 0:
            return TrainingResult(0, 0, 0.0, 0.0)

        solveCount = 0
        rewards = 0.0

        for board in self.evaluationBoards:
            env = RLEnvironment(board)
            agent.set_env(env)

            observation, _ = env.reset()

            terminated = False
            truncated = False
            boardReward = 0.0

            while not terminated and not truncated:
                action = agent.predict(observation, deterministic=True)
                observation, reward, terminated, truncated, _ = env.step(int(action))
                boardReward += float(reward)

            rewards += boardReward

            if terminated and env.game.isFinished():
                solveCount += 1

        averageReward = rewards / totalBoards
        successRate = solveCount / totalBoards

        return TrainingResult(
            solveCount,
            totalBoards,
            averageReward,
            successRate,
        )

    def save(self, agent: RLAgent, modelPath: str | None = None):
        """Save the trained agent to the provided model path."""
        path = modelPath if modelPath else self.modelPath

        if not path:
            raise ValueError("A valid model path is required.")

        agent.save(path)

    def _can_solve_board(self, agent: RLAgent, board: Board) -> bool:
        """Check whether the agent can solve the board deterministically."""
        env = RLEnvironment(board)
        agent.set_env(env)

        observation, _ = env.reset()

        terminated = False
        truncated = False

        while not terminated and not truncated:
            action = agent.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, _ = env.step(int(action))

        return terminated and env.game.isFinished()


if __name__ == "__main__":
    import random
    import numpy as np
    import torch

    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    trainer = AgentTrainer(
        boardSize=3,
        nrOfWalls=5,
        nrOfWaypoints=5,
        modelPath="trained-model.zip",

        # Important: with BoardSamplingEnv, use many training boards.
        nrTrainingBoards=300,
        nrEvaluationBoards=500,

        # Now interpreted as total training timesteps.
        timestepsPerBoard=300_000,

        # True: use old trained-model.zip if it exists
        loadExistingModel=True,

        # True: delete old trained-model.zip and start from zero
        resetModel=False,
    )

    trainedAgent = trainer.train()
    trainer.save(trainedAgent)

    print("\nTesting trained model on some training boards:")

    for index, board in enumerate(trainer.trainingBoards[:5]):
        print(f"\nTraining board {index + 1}:")
        env = RLEnvironment(board)
        trainedAgent.set_env(env)
        print(trainedAgent.solve(max_steps=env.config.max_steps, render=True))

    result = trainer.evaluate(trainedAgent)

    print("\nEvaluation result:")
    print("Solved:", result.getSolveCount)
    print("Total Boards:", result.getTotalBoards)
    print("Average reward:", result.getAverageReward)
    print("Success rate:", result.getSuccessRate)