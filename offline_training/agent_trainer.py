
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
    ):
        """
        Creates a trainer configured with training/evaluation board sets.

        Args:
            boardSize (int): Side length of each square board.
            nrOfWalls (int): Number of walls per generated board.
            nrOfWaypoints (int): Number of intermediate waypoints per board.
            modelPath (str): Default path used when saving the model.
            trainingBoards (list[Board] | None): Optional externally prepared training boards.
            evaluationBoards (list[Board] | None): Optional externally prepared evaluation boards.
            timestepsPerBoard (int | None): Optional fixed training timesteps per board.
        """
        self.modelPath = modelPath
        self.trainingBoards = (
            trainingBoards
            if trainingBoards is not None
            else BoardGenerator.generate(boardSize, nrOfWaypoints, nrOfWalls, nrTrainingBoards)
        )
        self.evaluationBoards = (
            evaluationBoards
            if evaluationBoards is not None
            else BoardGenerator.generate(boardSize, nrOfWaypoints, nrOfWalls, nrEvaluationBoards)
        )
        self._timestepsPerBoard = timestepsPerBoard

    def train(self) -> RLAgent:
        """Trains one RLAgent across all configured training boards."""
        if not self.trainingBoards:
            raise ValueError("Cannot train without at least one training board.")

        firstEnv = RLEnvironment(self.trainingBoards[0])
        agent = RLAgent(
            firstEnv,
            learning_rate=0.0003,
            exploration_initial_eps=1.0,
            exploration_final_eps=0.2,
            exploration_fraction=0.7,
            learning_starts=100,
        )

        chunk_timesteps = 1000
        max_timesteps_per_board = self._timestepsPerBoard if self._timestepsPerBoard is not None else 30000
        max_chunks_per_board = max_timesteps_per_board // chunk_timesteps

        for index, board in enumerate(self.trainingBoards):
            env = RLEnvironment(board)
            agent.set_env(env)

            solved = False

            for chunk in range(max_chunks_per_board):
                agent.learn(
                    total_timesteps=chunk_timesteps,
                    reset_num_timesteps=False,
                )

                if self._can_solve_board(agent, board):
                    print(f"Board {index + 1} solved after {(chunk + 1) * chunk_timesteps} timesteps.")
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

    def save(self, agent: RLAgent, modelPath: str):
        """Saves the trained agent to the provided model path."""
        path = modelPath if modelPath else self.modelPath
        if not path:
            raise ValueError("A valid model path is required.")
        agent.save(path)


    def _can_solve_board(self, agent: RLAgent, board: Board) -> bool:
        env = RLEnvironment(board)
        observation, _ = env.reset()

        terminated = False
        truncated = False

        while not terminated and not truncated:
            action = agent.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(int(action))

        return terminated and env.game.isFinished()


if __name__ == "__main__":
    trainer = AgentTrainer(
        boardSize=3,
        nrOfWalls=0,
        nrOfWaypoints=2,
        modelPath="default-model.zip",
        nrTrainingBoards=1,
        nrEvaluationBoards=1,
        timestepsPerBoard=30000,
    )

    trainedAgent = trainer.train()
    trainer.save(trainedAgent, "trained-model.zip")

    env = RLEnvironment(trainer.trainingBoards[0])
    loadedAgent = RLAgent(env, model_path="trained-model.zip")
    print(loadedAgent.solve(max_steps=env.config.max_steps, render=True))
