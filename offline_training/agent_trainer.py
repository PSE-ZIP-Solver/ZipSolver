import pickle
from pathlib import Path

from backend.rl_components import RLAgent, RLEnvironment
from backend.puzzle_logic import Board
from offline_training.training_result import TrainingResult


class AgentTrainer:
    """Evaluation-only helper for the final 6x6 daily puzzle benchmark."""

    def __init__(
        self,
        boardSize: int,
        nrEvaluationBoards: int,
        modelPath: str,
        evaluationBoardsPath: str,
    ):
        self.boardSize = boardSize
        self.nrEvaluationBoards = nrEvaluationBoards
        self.modelPath = modelPath
        self.evaluationBoardsPath = Path(evaluationBoardsPath)

        self.evaluationBoards = self._load_evaluation_boards()

    def _load_evaluation_boards(self) -> list[Board]:
        """Load the fixed 6x6 daily evaluation set."""

        if not self.evaluationBoardsPath.exists():
            raise FileNotFoundError(
                f"Evaluation board file not found: "
                f"{self.evaluationBoardsPath}"
            )

        with self.evaluationBoardsPath.open("rb") as file:
            boards = pickle.load(file)

        if not isinstance(boards, list) or not boards:
            raise ValueError(
                "Saved evaluation board file is empty or invalid."
            )

        if len(boards) != self.nrEvaluationBoards:
            raise ValueError(
                f"Saved evaluation set contains {len(boards)} boards, "
                f"but {self.nrEvaluationBoards} were expected."
            )

        print(
            f"Loaded {len(boards)} evaluation boards from "
            f"{self.evaluationBoardsPath}"
        )

        return boards

    def load_saved_agent(self) -> RLAgent:
        """Load the final 6x6 model without further training."""

        if not Path(self.modelPath).exists():
            raise FileNotFoundError(
                f"Model file not found: "
                f"{self.modelPath}"
            )

        print(
            f"Loading 6x6 agent from "
            f"{self.modelPath}"
        )

        return RLAgent(
            RLEnvironment(
                self.evaluationBoards[0]
            ),
            model_path=self.modelPath,
        )

    def evaluate(
        self,
        agent: RLAgent,
        boards: list[Board] | None = None,
    ) -> TrainingResult:
        """Evaluate deterministically on all fixed daily boards."""

        boards = (
            self.evaluationBoards
            if boards is None
            else boards
        )

        if not boards:
            return TrainingResult(
                0,
                0,
                0.0,
                0.0,
            )

        solveCount = 0
        rewardSum = 0.0

        for index, board in enumerate(
            boards,
            start=1,
        ):
            solved, boardReward = self._run_board(
                agent,
                board,
            )

            solveCount += int(solved)
            rewardSum += boardReward

            if (
                index % 20 == 0
                or index == len(boards)
            ):
                successRateSoFar = (
                    solveCount / index
                ) * 100.0

                print(
                    f"Evaluated {index}/{len(boards)} boards "
                    f"- solved so far: {solveCount} "
                    f"({successRateSoFar:.2f}%)"
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

            (
                observation,
                reward,
                terminated,
                truncated,
                _,
            ) = env.step(
                int(action)
            )

            rewardSum += float(reward)

        solved = (
            terminated
            and env.game.isFinished()
        )

        env.close()

        return solved, rewardSum

    @staticmethod
    def print_result(
        title: str,
        result: TrainingResult,
    ):
        """Print final evaluation result."""

        print(f"\n{title}:")
        print(
            "Solved:",
            result.getSolveCount,
        )
        print(
            "Total Boards:",
            result.getTotalBoards,
        )
        print(
            "Average reward:",
            result.getAverageReward,
        )
        print(
            "Success rate:",
            result.getSuccessRate,
        )
        print(
            "Success rate (%):",
            result.getSuccessRate * 100.0,
        )


if __name__ == "__main__":

    # FINAL 6x6 DAILY PUZZLE EVALUATION

    BOARD_SIZE = 6
    NR_EVALUATION_BOARDS = 240

    MODEL_PATH = (
        "offline_training/trained_models/6x6/"
        "6x6-agent.zip"
    )

    EVALUATION_BOARDS_PATH = (
        "offline_training/evaluation_boards/"
        "6x6(final_sets)/"
        "6x6-daily-evaluation-240boards.pkl"
    )

    trainer = AgentTrainer(
        boardSize=BOARD_SIZE,
        nrEvaluationBoards=NR_EVALUATION_BOARDS,
        modelPath=MODEL_PATH,
        evaluationBoardsPath=EVALUATION_BOARDS_PATH,
    )

    agent = trainer.load_saved_agent()

    result = trainer.evaluate(
        agent,
        trainer.evaluationBoards,
    )

    trainer.print_result(
        "FINAL 6x6 evaluation - Daily Puzzles",
        result,
    )