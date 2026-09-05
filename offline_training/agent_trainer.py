import pickle
import random
from pathlib import Path

from backend.rl_components import RLAgent, RLEnvironment
from backend.puzzle_logic import Board
from offline_training.board_generator import BoardGenerator
from offline_training.training_result import TrainingResult


class AgentTrainer:
    """Evaluation-only helper for the final 6x6 benchmark."""

    def __init__(
        self,
        boardSize: int,
        nrEvaluationBoards: int,
        minNrOfWalls: int,
        maxNrOfWalls: int,
        minNrOfWaypoints: int,
        maxNrOfWaypoints: int,
        modelPath: str,
        evaluationBoardsPath: str,
    ):
        self.boardSize = boardSize
        self.nrEvaluationBoards = nrEvaluationBoards
        self.minNrOfWalls = minNrOfWalls
        self.maxNrOfWalls = maxNrOfWalls
        self.minNrOfWaypoints = minNrOfWaypoints
        self.maxNrOfWaypoints = maxNrOfWaypoints
        self.modelPath = modelPath
        self.evaluationBoardsPath = Path(evaluationBoardsPath)

        if not 0 <= minNrOfWalls <= maxNrOfWalls:
            raise ValueError("Invalid wall interval.")

        if not 0 <= minNrOfWaypoints <= maxNrOfWaypoints:
            raise ValueError("Invalid waypoint interval.")

        self.evaluationBoards = self._load_or_create_evaluation_boards()

    def _load_or_create_evaluation_boards(self) -> list[Board]:
        """Load the fixed set, or create and save it once."""

        if self.evaluationBoardsPath.exists():
            with self.evaluationBoardsPath.open("rb") as file:
                boards = pickle.load(file)

            if not isinstance(boards, list) or not boards:
                raise ValueError("Saved evaluation board file is empty or invalid.")

            if len(boards) != self.nrEvaluationBoards:
                raise ValueError(
                    f"Saved evaluation set contains {len(boards)} boards, "
                    f"but {self.nrEvaluationBoards} were expected."
                )

            print(f"Loaded evaluation boards from {self.evaluationBoardsPath}")
            return boards

        print(
            f"Generating {self.nrEvaluationBoards} evaluation boards "
            f"(walls {self.minNrOfWalls}-{self.maxNrOfWalls}, "
            f"waypoints {self.minNrOfWaypoints}-{self.maxNrOfWaypoints})..."
        )

        boards: list[Board] = []

        for index in range(self.nrEvaluationBoards):
            nrOfWalls = random.randint(
                self.minNrOfWalls,
                self.maxNrOfWalls,
            )

            nrOfWaypoints = random.randint(
                self.minNrOfWaypoints,
                self.maxNrOfWaypoints,
            )

            boards.append(
                BoardGenerator.generate(
                    self.boardSize,
                    nrOfWaypoints,
                    nrOfWalls,
                    1,
                )[0]
            )

            if (
                (index + 1) % 500 == 0
                or index + 1 == self.nrEvaluationBoards
            ):
                print(
                    f"Generated {index + 1}/"
                    f"{self.nrEvaluationBoards} "
                    "evaluation boards."
                )

        self.evaluationBoardsPath.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.evaluationBoardsPath.open("wb") as file:
            pickle.dump(boards, file)

        print(f"Saved evaluation boards to {self.evaluationBoardsPath}")
        return boards

    def load_saved_agent(self) -> RLAgent:
        """Load the final 6x6 model without further training."""

        if not Path(self.modelPath).exists():
            raise FileNotFoundError(
                f"Model file not found: {self.modelPath}"
            )

        return RLAgent(
            RLEnvironment(self.evaluationBoards[0]),
            model_path=self.modelPath,
        )

    def evaluate(
        self,
        agent: RLAgent,
        boards: list[Board] | None = None,
    ) -> TrainingResult:
        """Evaluate deterministically on all boards."""

        boards = (
            self.evaluationBoards
            if boards is None
            else boards
        )

        if not boards:
            return TrainingResult(0, 0, 0.0, 0.0)

        solveCount = 0
        rewardSum = 0.0

        for index, board in enumerate(boards, start=1):
            solved, boardReward = self._run_board(agent, board)
            solveCount += int(solved)
            rewardSum += boardReward

            if index % 500 == 0 or index == len(boards):
                print(
                    f"Evaluated {index}/{len(boards)} boards "
                    f"- solved so far: {solveCount}"
                )

        totalBoards = len(boards)

        return TrainingResult(
            solveCount,
            totalBoards,
            rewardSum / totalBoards,
            solveCount / totalBoards,
        )

    @staticmethod
    def _run_board(
        agent: RLAgent,
        board: Board,
    ) -> tuple[bool, float]:
        """Run one deterministic evaluation episode."""

        env = RLEnvironment(board)
        agent.set_env(env)

        observation, _ = env.reset()
        terminated = False
        truncated = False
        rewardSum = 0.0

        while not terminated and not truncated:
            action = agent.predict(
                observation,
                deterministic=True,
            )

            observation, reward, terminated, truncated, _ = env.step(
                int(action)
            )

            rewardSum += float(reward)

        solved = terminated and env.game.isFinished()
        env.close()

        return solved, rewardSum

    @staticmethod
    def print_result(
        title: str,
        result: TrainingResult,
    ):
        """Print final evaluation result."""

        print(f"\n{title}:")
        print("Solved:", result.getSolveCount)
        print("Total Boards:", result.getTotalBoards)
        print("Average reward:", result.getAverageReward)
        print("Success rate:", result.getSuccessRate)
        print("Success rate (%):", result.getSuccessRate * 100.0)


if __name__ == "__main__":

    # FINAL 6x6 EVALUATION - SET 3 / 3: DENSE

    BOARD_SIZE = 6
    NR_EVALUATION_BOARDS = 10_000

    MIN_NR_OF_WALLS = 17
    MAX_NR_OF_WALLS = 25

    MIN_NR_OF_WAYPOINTS = 23
    MAX_NR_OF_WAYPOINTS = 34

    MODEL_PATH = (
        "offline_training/trained_models/6x6/"
        "6x6-agent.zip"
    )

    EVALUATION_BOARDS_PATH = (
        "offline_training/evaluation_boards/6x6(final_sets)/"
        "6x6-final-eval-set3-dense-"
        "17to25walls-23to34wp-10000boards.pkl"
    )

    trainer = AgentTrainer(
        boardSize=BOARD_SIZE,
        nrEvaluationBoards=NR_EVALUATION_BOARDS,
        minNrOfWalls=MIN_NR_OF_WALLS,
        maxNrOfWalls=MAX_NR_OF_WALLS,
        minNrOfWaypoints=MIN_NR_OF_WAYPOINTS,
        maxNrOfWaypoints=MAX_NR_OF_WAYPOINTS,
        modelPath=MODEL_PATH,
        evaluationBoardsPath=EVALUATION_BOARDS_PATH,
    )

    agent = trainer.load_saved_agent()

    result = trainer.evaluate(
        agent,
        trainer.evaluationBoards,
    )

    trainer.print_result(
        "FINAL 6x6 evaluation - Set 3 / Dense",
        result,
    )
