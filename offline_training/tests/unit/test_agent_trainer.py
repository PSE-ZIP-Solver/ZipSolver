from types import SimpleNamespace

import pytest

from offline_training.agent_trainer import AgentTrainer


def test_init_generates_training_and_evaluation_boards(monkeypatch):
    calls = []

    def fake_generate(boardSize: int, intermediateWaypoints: int, walls: int, numberBoards: int = 1):
        calls.append((boardSize, intermediateWaypoints, walls, numberBoards))
        return [f"board-{len(calls)}"]

    monkeypatch.setattr("offline_training.agent_trainer.BoardGenerator.generate", fake_generate)
    # Avoid writing a pickle file to disk when boards are freshly generated.
    monkeypatch.setattr("offline_training.agent_trainer.AgentTrainer._save_training_boards", lambda self: None)

    trainer = AgentTrainer(
        boardSize=6,
        nrOfWalls=5,
        nrOfWaypoints=3,
        modelPath="model.zip",
        nrTrainingBoards=1,
        nrEvaluationBoards=1,
        randomizeBoardComplexity=False,
    )

    # generate() is now called once per board and takes a numberBoards arg (here always 1).
    assert calls == [(6, 3, 5, 1), (6, 3, 5, 1)]
    assert trainer.trainingBoards == ["board-1"]
    assert trainer.evaluationBoards == ["board-2"]


def test_train_creates_new_agent_and_learns_once(monkeypatch, tmp_path):
    training_boards = ["train-a", "train-b", "train-c"]
    learn_calls = []
    created_agents = []

    class FakeSamplingEnv:
        """Stand-in for BoardSamplingEnv, which wraps the whole board pool."""

        def __init__(self, boards):
            self.boards = boards

    class FakeMonitor:
        """Stand-in for stable_baselines3's Monitor wrapper."""

        def __init__(self, env):
            self.env = env

    class FakeAgent:
        def __init__(self, env, **kwargs):
            self.env = env
            self.kwargs = kwargs
            created_agents.append(self)

        def learn(self, total_timesteps: int, reset_num_timesteps: bool = True):
            learn_calls.append((total_timesteps, reset_num_timesteps))
            return self

    monkeypatch.setattr("offline_training.agent_trainer.BoardSamplingEnv", FakeSamplingEnv)
    monkeypatch.setattr("offline_training.agent_trainer.Monitor", FakeMonitor)
    monkeypatch.setattr("offline_training.agent_trainer.RLAgent", FakeAgent)

    # modelPath doesn't exist on disk, so train() takes the "create new agent" branch.
    model_path = str(tmp_path / "model.zip")

    trainer = AgentTrainer(
        boardSize=6,
        nrOfWalls=4,
        nrOfWaypoints=2,
        modelPath=model_path,
        trainingBoards=training_boards,
        evaluationBoards=[],
        timestepsPerBoard=25,  # interpreted as total training timesteps
    )

    agent = trainer.train()

    assert isinstance(agent, FakeAgent)
    assert len(created_agents) == 1
    # The agent was built on a Monitor-wrapped BoardSamplingEnv over all training boards.
    assert isinstance(agent.env, FakeMonitor)
    assert isinstance(agent.env.env, FakeSamplingEnv)
    assert agent.env.env.boards == training_boards
    # learn() is called exactly once, over the full board pool, not per board.
    assert learn_calls == [(25, True)]


def test_evaluate_builds_training_result(monkeypatch):
    class FakeAgent:
        def set_env(self, env):
            self.env = env

        def predict(self, observation, deterministic: bool = True):
            return 1

    class FakeEnv:
        def __init__(self, board):
            self.board = board
            self.game = SimpleNamespace(isFinished=lambda: self.board["solved"])

        def reset(self):
            return "obs", {}

        def step(self, action):
            if self.board["solved"]:
                return "obs", 10.0, True, False, {}
            return "obs", -4.0, True, False, {}

        def close(self):
            pass

    monkeypatch.setattr("offline_training.agent_trainer.RLEnvironment", FakeEnv)

    trainer = AgentTrainer(
        boardSize=6,
        nrOfWalls=2,
        nrOfWaypoints=2,
        modelPath="model.zip",
        trainingBoards=[],
        evaluationBoards=[{"solved": True}, {"solved": False}],
    )

    result = trainer.evaluate(FakeAgent())

    assert result.getSolveCount == 1
    assert result.getTotalBoards == 2
    assert result.getAverageReward == pytest.approx(3.0)
    assert result.getSuccessRate == pytest.approx(0.5)


def test_save_delegates_to_agent_and_saves_replay_buffer(tmp_path):
    saved_paths = []
    replay_buffer_calls = []

    class FakeModel:
        def save_replay_buffer(self, path):
            replay_buffer_calls.append(path)

    class FakeAgent:
        def __init__(self):
            self._model = FakeModel()

        def save(self, path: str):
            saved_paths.append(path)

    trainer = AgentTrainer(
        boardSize=6,
        nrOfWalls=2,
        nrOfWaypoints=2,
        modelPath=str(tmp_path / "default-model.zip"),
        trainingBoards=[],
        evaluationBoards=[],
    )

    custom_path = str(tmp_path / "custom-model.zip")
    trainer.save(FakeAgent(), custom_path)

    assert saved_paths == [custom_path]
    assert len(replay_buffer_calls) == 1
    assert str(replay_buffer_calls[0]).endswith("custom-model_replay_buffer.pkl")