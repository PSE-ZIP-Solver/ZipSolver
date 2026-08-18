from types import SimpleNamespace

import pytest

from offline_training.agent_trainer import AgentTrainer


def test_init_generates_training_and_evaluation_boards(monkeypatch):
    """
    Verifies the initialization sequence for the agent trainer correctly dispatches board generation requests.

    Args:
        monkeypatch: The active test environment fixture responsible for safely intercepting 
            and overriding system-level namespaces or dependencies.

    Implementation Details:
        Hijacks the primary generator method to passively track invocation sequences and structural 
        parameters without executing the computationally heavy combinatorial pathfinding logic natively. 
        Suppresses the localized disk-writing mechanism via a lambda attachment to ensure the underlying 
        file system remains untouched. Asserts that the requested architectural layouts are successfully 
        partitioned into distinct arrays for training and evaluation.
    """
    calls = []

    def fake_generate(boardSize: int, intermediateWaypoints: int, walls: int, numberBoards: int = 1):
        """
        Acts as an artificial endpoint capturing requested topological parameters.

        Args:
            boardSize: The absolute spatial limitation for the requested layout.
            intermediateWaypoints: The exact internal milestone count required.
            walls: The target volume of physical barriers to distribute.
            numberBoards: The total volumetric count of layouts requested.

        Returns:
            A sequence containing artificially mapped identifier tags.

        Implementation Details:
            Intercepts the functional arguments, appends the structural configuration to an external 
            tracking array to verify sequence integrity, and securely bubbles up a synthetic placeholder array.
        """
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
    """
    Validates that a fresh neural network agent is properly instantiated and trained when no existing persistence is found.

    Args:
        monkeypatch: The active test environment fixture responsible for securely mocking system dependencies.
        tmp_path: The localized session fixture providing ephemeral directory bindings for safe file emulation.

    Implementation Details:
        Aggressively replaces the entire reinforcement learning stack with localized mock objects 
        to circumvent actual tensor allocations and heavy mathematical dependencies. Tracks the execution 
        of the core learning hook and strictly verifies that the system trains across the entirety of the 
        pooled topological environment seamlessly rather than erroneously looping sequentially per-board.
    """
    training_boards = ["train-a", "train-b", "train-c"]
    learn_calls = []
    created_agents = []

    class FakeSamplingEnv:
        """
        A localized surrogate representing the pooled training environment wrapper.

        Responsibility:
            Safely bypasses heavy domain instantiation logic, holding basic layout arrays in active 
            memory to facilitate structural continuity checks during mock training.

        Implementation Details:
            Accepts and preserves the targeted topological sequences natively upon initialization, 
            preventing recursive environment allocations.
        """
        def __init__(self, boards):
            """
            Initializes the mock sampling pool.

            Args:
                boards: The pooled sequence of topological arrays targeted for evaluation.

            Implementation Details:
                Binds the mapped arrays directly into the localized state tracker.
            """
            self.boards = boards

    class FakeMonitor:
        """
        A structural stand-in mirroring third-party telemetry wrappers.

        Responsibility:
            Acts as a safe pass-through layer, shielding the localized pipeline from requesting 
            external statistical operations that could crash headless testing loops.

        Implementation Details:
            Receives the foundational mock environment and strictly maps it natively to bypass 
            the heavy initialization sequences associated with actual metric monitoring.
        """
        def __init__(self, env):
            """
            Initializes the artificial telemetry wrapper.

            Args:
                env: The enclosed environmental domain undergoing simulated evaluation.

            Implementation Details:
                Attaches the environment target directly to an accessible internal attribute.
            """
            self.env = env

    class FakeAgent:
        """
        A heavily simplified proxy for the primary neural network resolution engine.

        Responsibility:
            Secures parameterized validation loops by artificially tracking simulation steps natively 
            without initializing actual mathematical weights or memory buffers.

        Implementation Details:
            Logs its own instantiation globally to ensure strict memory allocation limits are respected. 
            Overrides the fundamental learning hooks to record algorithmic loop execution requests natively.
        """
        def __init__(self, env, **kwargs):
            """
            Initializes the artificial neural proxy.

            Args:
                env: The bound evaluation environment targeted for optimization.
                **kwargs: Any additional configuration parameters injected by the orchestrator.

            Implementation Details:
                Preserves all execution arguments and appends itself to an external tracking array 
                to definitively verify instantiation frequency.
            """
            self.env = env
            self.kwargs = kwargs
            created_agents.append(self)

        def learn(self, total_timesteps: int, reset_num_timesteps: bool = True):
            """
            Simulates the execution of deep learning iteration cycles.

            Args:
                total_timesteps: The absolute ceiling mapping requested operational bounds.
                reset_num_timesteps: The flag dictating if internal execution histories should zero out.

            Returns:
                The active proxy instance, structurally mirroring a chainable learning method.

            Implementation Details:
                Intercepts the operational limits and writes them directly to an external global 
                array, securely bypassing heavy combinatorial evaluations.
            """
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
    """
    Ensures the evaluation sequence accurately simulates game environments and aggregates success metrics.

    Args:
        monkeypatch: The active test environment fixture responsible for securely mocking system dependencies.

    Implementation Details:
        Injects a lightweight mock environment to act as the spatial step-engine and a localized proxy 
        agent to serve as the action-predictor. Feeds predefined structural success and failure states 
        into the pipeline to strictly force exact mathematical reward distributions. Asserts that the resulting 
        telemetry wrapper properly natively calculates absolute completion counts, average rewards, and overall 
        success ratios without triggering actual graph traversal logic.
    """
    class FakeAgent:
        """
        A proxy engine mimicking prediction responses for an isolated evaluation loop.

        Responsibility:
            Provides purely synthetic navigational outputs to structurally bypass external inference layers 
            during performance evaluations.

        Implementation Details:
            Maintains localized bindings for external environments and safely maps all prediction queries 
            to a constant scalar, securely short-circuiting heavy algorithmic processing natively.
        """
        def set_env(self, env):
            """
            Binds the targeted domain configuration to the proxy model.

            Args:
                env: The spatial mock framework utilized for localized evaluation.

            Implementation Details:
                Stores the target structurally on the internal attribute registry.
            """
            self.env = env

        def predict(self, observation, deterministic: bool = True):
            """
            Yields a synthetic action vector for the evaluation pipeline.

            Args:
                observation: The current contextual snapshot produced by the simulated environment.
                deterministic: The flag dictating strict exploitation over exploration.

            Returns:
                An absolute scalar value mirroring a static navigational decision.

            Implementation Details:
                Actively ignores all temporal or spatial arguments and rigidly returns a locked integer 
                to maintain perfect execution continuity.
            """
            return 1

    class FakeEnv:
        """
        A completely synthetic simulation environment mapping internal completion states.

        Responsibility:
            Emulates the entire mechanical progression layer, seamlessly transitioning between layout 
            origins and structural conclusions natively to feed accurate metric streams into the evaluator.

        Implementation Details:
            Relies entirely on injected configuration flags. It artificially mimics successful or failed 
            state progressions by overriding standard telemetry tuples directly, ensuring the orchestration 
            engine interprets pure success and failure mathematics without graph computation.
        """
        def __init__(self, board):
            """
            Initializes the artificial progression framework.

            Args:
                board: The raw structural data proxy containing specific predetermined success flags.

            Implementation Details:
                Secures the layout configuration natively and initializes a simplistic namespace 
                acting as the overarching game orchestrator loop.
            """
            self.board = board
            self.game = SimpleNamespace(isFinished=lambda: self.board["solved"])

        def reset(self):
            """
            Reinitializes the operational boundaries for a fresh simulation run.

            Returns:
                A mock configuration tuple reflecting an untouched base state.

            Implementation Details:
                Safely bubbles up pure structural placeholders representing observational starting points.
            """
            return "obs", {}

        def step(self, action):
            """
            Simulates a discrete action execution within the localized timeline.

            Args:
                action: The synthetic action command proposed by the mocked predictor.

            Returns:
                A comprehensive tuple resolving the state transition, including the observational snapshot, 
                the accumulated mathematical reward, and absolute completion states.

            Implementation Details:
                Defensively evaluates the internalized board status proxy. Hardcodes absolute mathematical 
                success structures if the active configuration is defined as solved, or securely returns 
                negative metric punishments otherwise to verify accurate telemetry aggregations natively.
            """
            if self.board["solved"]:
                return "obs", 10.0, True, False, {}
            return "obs", -4.0, True, False, {}

        def close(self):
            """
            Formally terminates the synthetic execution loop.

            Implementation Details:
                Acts as a strictly inert endpoint, safely catching and swallowing resource teardown 
                requests to prevent execution crashes.
            """
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
    """
    Confirms that persistence requests are correctly forwarded to the internal agent model and memory structures.

    Args:
        tmp_path: The localized session fixture providing ephemeral directory bindings for safe file emulation.

    Implementation Details:
        Instruments a fake internal sub-model structure natively that logs save paths and replay buffer 
        extraction calls. Triggers the serialization workflow utilizing a custom destination string and 
        definitively asserts that both the primary architecture wrapper and the associated secondary telemetry 
        buffer accurately track the correct physical destination hooks.
    """
    saved_paths = []
    replay_buffer_calls = []

    class FakeModel:
        """
        A minimal proxy for internal graph persistence algorithms.

        Responsibility:
            Safely bypasses deep tensor serialization logic during structural teardown verifications.

        Implementation Details:
            Actively intercepts calls directed at deep structural checkpoints and logs the requested 
            destination paths securely without engaging system I/O bounds natively.
        """
        def save_replay_buffer(self, path):
            """
            Intercepts localized buffer memory persistence requests.

            Args:
                path: The mapped destination endpoint requested by the framework.

            Implementation Details:
                Logs the destination target internally to guarantee chronological order validation natively.
            """
            replay_buffer_calls.append(path)

    class FakeAgent:
        """
        An artificial primary neural entity coordinating secondary model storage commands.

        Responsibility:
            Interacts precisely with localized orchestrators to structurally map internal 
            serialization directives down to nested mathematical subsystems natively.

        Implementation Details:
            Bootstraps an artificial internal model directly. Employs a mocked persistence hook to 
            passively catalog routing trajectories requested by the overarching test orchestrator.
        """
        def __init__(self):
            """
            Initializes the simplified proxy serialization framework.

            Implementation Details:
                Directly encapsulates an artificial internal data store locally.
            """
            self._model = FakeModel()

        def save(self, path: str):
            """
            Intercepts overarching architecture persistence requests.

            Args:
                path: The targeted baseline destination endpoint.

            Implementation Details:
                Routes the provided structural string strictly into an external observation array 
                to accurately verify save loop triggering.
            """
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