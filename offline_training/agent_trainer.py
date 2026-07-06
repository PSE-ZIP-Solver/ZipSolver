import random
from pathlib import Path

from backend.puzzle_logic import Board
from backend.rl_components import RLAgent, RLEnvironment
from offline_training.board_generator import BoardGenerator
from offline_training.training_result import TrainingResult


class AgentTrainer:
    def __init__(
        self,
        boardSize: int,
        nrOfWalls: int,
        nrOfWaypoints: int,
        modelPath: str,
        nrTrainingBoards: int = 10,
        nrEvaluationBoards: int = 10,
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
            timestepsPerBoard (int | None): Optional fixed training timesteps per board.
            loadExistingModel (bool): If True, loads modelPath if it exists.
            resetModel (bool): If True, deletes modelPath before training and starts fresh.
        """
        self.modelPath = modelPath
        self._timestepsPerBoard = timestepsPerBoard
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
        """Generate boards where each board has a random number of waypoints and walls."""
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
        """Trains one RLAgent across all configured training boards."""
        if not self.trainingBoards:
            raise ValueError("Cannot train without at least one training board.")

        firstEnv = RLEnvironment(self.trainingBoards[0])
        modelFile = Path(self.modelPath)

        if self.resetModel and modelFile.exists():
            print(f"Resetting model: deleting {self.modelPath}")
            modelFile.unlink()

        if self.loadExistingModel and modelFile.exists():
            print(f"Loading existing model from {self.modelPath}")
            agent = RLAgent(firstEnv, model_path=self.modelPath)
        else:
            print("Creating new agent")
            agent = RLAgent(
                firstEnv,
                learning_rate=0.0003,
                exploration_initial_eps=1.0,
                exploration_final_eps=0.3,
                exploration_fraction=0.6,
                learning_starts=100,
            )
        
        agent.set_exploration_schedule(
        initial_eps=1.0,
        final_eps=0.2,
        fraction=0.8,
        )

        chunk_timesteps = 1000
        max_timesteps_per_board = (
            self._timestepsPerBoard
            if self._timestepsPerBoard is not None
            else 30000
        )
        max_chunks_per_board = max_timesteps_per_board // chunk_timesteps

        for index, board in enumerate(self.trainingBoards):
            env = RLEnvironment(board)
            agent.set_env(env)

            solved = False

            for chunk in range(max_chunks_per_board):
                agent.learn(
                    total_timesteps=chunk_timesteps,
                    reset_num_timesteps=(chunk == 0), # Reset Exploration for each board
                )

                if self._can_solve_board(agent, board):
                    print(
                        f"Board {index + 1} solved after "
                        f"{(chunk + 1) * chunk_timesteps} timesteps."
                    )
                    solved = True
                    break

            if not solved:
                print(f"Board {index + 1} not solved. Moving to next board anyway.")

        return agent

    def evaluate(self, agent: RLAgent) -> TrainingResult:
        """Evaluates a trained RLAgent on all configured evaluation boards."""
        totalBoards = len(self.evaluationBoards)

        if totalBoards == 0:
            return TrainingResult(0, 0, 0.0, 0.0)

        solveCount = 0
        rewards = 0.0

        for board in self.evaluationBoards:
            env = RLEnvironment(board)
            observation, _ = env.reset()

            terminated = False
            truncated = False
            boardReward = 0.0

            while not terminated and not truncated:
                action = agent.predict(observation, deterministic=True)
                observation, reward, terminated, truncated, _ = env.step(int(action))
                boardReward += reward

            rewards += boardReward

            if terminated and env.game.isFinished():
                solveCount += 1

        averageReward = rewards / totalBoards
        successRate = solveCount / totalBoards

        return TrainingResult(solveCount, totalBoards, averageReward, successRate)

    def save(self, agent: RLAgent, modelPath: str | None = None):
        """Saves the trained agent to the provided model path."""
        path = modelPath if modelPath else self.modelPath

        if not path:
            raise ValueError("A valid model path is required.")

        agent.save(path)

    def _can_solve_board(self, agent: RLAgent, board: Board) -> bool:
        """Checks whether the agent can solve the board deterministically."""
        env = RLEnvironment(board)
        observation, _ = env.reset()

        terminated = False
        truncated = False

        while not terminated and not truncated:
            action = agent.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, _ = env.step(int(action))

        return terminated and env.game.isFinished()


if __name__ == "__main__":
    trainer = AgentTrainer(
        boardSize=3,
        nrOfWalls=5,
        nrOfWaypoints=5,
        modelPath="trained-model.zip",
        nrTrainingBoards=1,
        nrEvaluationBoards=100,
        timestepsPerBoard=10000,

        # True: use old trained-model.zip if it exists
        loadExistingModel=True,

        # True: delete old trained-model.zip and start from zero
        resetModel=True,
    )

    trainedAgent = trainer.train()
    trainer.save(trainedAgent)

    print("\nTesting trained model on training boards:")

    for index, board in enumerate(trainer.trainingBoards):
        print(f"\nTraining board {index + 1}:")
        env = RLEnvironment(board)
        trainedAgent.set_env(env)
        print(trainedAgent.solve(max_steps=env.config.max_steps, render=True))


    # EVALUATION:
    result = trainer.evaluate(trainedAgent)

    print("\nEvaluation result:")
    print("Solved:", result.getSolveCount)
    print("Total Boards:", result.getTotalBoards)
    print("Average reward:", result.getAverageReward)
    print("Success rate:", result.getSuccessRate)