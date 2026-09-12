import gymnasium as gym
import numpy as np
import pytest

from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position
from backend.rl_components.rl_environment import RLEnvironment

BOARD_SIZE = 6
OBSERVATION_CHANNELS = 8
OBSERVATION_SHAPE = (
    OBSERVATION_CHANNELS,
    BOARD_SIZE,
    BOARD_SIZE,
)


# ==========================================
# Setup & Fixtures
# ==========================================


@pytest.fixture
def real_board():
    """
    Provisions a mathematically valid baseline spatial topology containing distal milestones.

    Returns:
        The structured baseline configuration dictating spatial bounds.

    Implementation Details:
        Instantiates a standard dimensional grid mapping an origin requirement natively at the
        top-left and an endpoint constraint positioned at the far opposing corner. This geometry
        ensures immediate, adjacent topological exploration from the start remains mathematically valid.
    """
    board = Board(BOARD_SIZE)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 5), 2)

    return board


@pytest.fixture
def env(real_board):
    """
    Initializes a controlled reinforcement learning simulation sandbox.

    Args:
        real_board: The static structural blueprint dictating the environmental bounds.

    Returns:
        The fully wrapped simulator mapping native spatial logic to learning matrices.

    Implementation Details:
        Directly injects the mathematical structural parameters into the customized evaluation environment natively
        orchestrating the translation between deep learning state outputs and domain rule evaluations.
    """
    return RLEnvironment(real_board)


def find_valid_action(environment: RLEnvironment):
    """
    Programmatically isolates a structurally compliant navigation maneuver from the active spatial node.

    Args:
        environment: The active learning simulator retaining the present sequence trajectory.

    Returns:
        A paired sequence containing the resolved directional command and its subsequent coordinate destination.

    Raises:
        AssertionError: If the spatial node is physically marooned without any mathematically viable exits.

    Implementation Details:
        Iterates explicitly over the bounded action limits natively tracking valid branches. Extracts target
        locations dynamically and utilizes the underlying rule engine explicitly to verify step compliance
        without actively advancing or altering the encapsulated environmental state.
    """
    current = environment.game.getState.getCurrentPosition

    for action in range(environment.action_space.n):
        target = environment._get_target_position(current, action)

        if environment.game.isValidNextStep(target):
            return action, target

    raise AssertionError("No valid action exists for the current test board.")


# ==========================================
# Gym API Contract & Spaces Tests
# ==========================================


def test_initialization(env):
    """
    Validates strict architectural adherence to external simulation space contracts.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Verifies the evaluation branches natively restrict commands to discrete cardinal directions.
        Asserts the multi-channel observation matrix mathematically matches precision limitations
        and inherently maps bounding extremes perfectly between standard analytical thresholds.
    """
    assert isinstance(env.action_space, gym.spaces.Discrete)
    assert env.action_space.n == 4

    assert isinstance(env.observation_space, gym.spaces.Box)
    assert env.observation_space.shape == OBSERVATION_SHAPE
    assert env.observation_space.dtype == np.float32
    assert env.observation_space.low.min() == 0.0
    assert env.observation_space.high.max() == 1.0

    assert env.config.size == BOARD_SIZE


def test_reset(env):
    """
    Assesses dynamic tensor regeneration during fundamental environmental cycle restarts.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Triggers a seeded sequence initialization loop natively. Asserts numerical trackers collapse safely,
        spatial markers return explicitly to origin bounds, and checks the generated observation securely
        illuminates the subsequent sequential milestone within its designated architectural channel.
    """
    observation, info = env.reset(seed=42)

    assert observation.shape == OBSERVATION_SHAPE
    assert observation.dtype == np.float32
    assert isinstance(info, dict)
    assert np.all((observation >= 0.0) & (observation <= 1.0))

    assert env.current_step_count == 0
    assert env.game.getState.getCurrentPosition == Position(0, 0)
    assert env.game.getState.getPath == [Position(0, 0)]

    # Channel 7 contains the next expected waypoint.
    assert observation[7, 5, 5] == 1.0
    assert np.sum(observation[7]) == 1.0


# ==========================================
# Action & Target Logic
# ==========================================


@pytest.mark.parametrize(
    "action, offset_x, offset_y",
    [
        (0, 0, -1),  # UP
        (1, 1, 0),  # RIGHT
        (2, 0, 1),  # DOWN
        (3, -1, 0),  # LEFT
    ],
)
def test_get_target_position(env, action, offset_x, offset_y):
    """
    Maps categorical directional inputs securely into accurate spatial coordinate offsets.

    Args:
        env: The fully configured reinforcement simulator.
        action: The simulated decision array representing the chosen directional branch.
        offset_x: The expected horizontal architectural shift.
        offset_y: The expected vertical architectural shift.

    Implementation Details:
        Utilizes parameterized test arrays tracking exact structural bounds natively against a fixed
        origin point. Directly evaluates the protected coordinate retrieval logic to assert
        mathematical translation safely computes dimensional distances.
    """
    current = Position(2, 2)

    target = env._get_target_position(current, action)

    assert target.getX == current.getX + offset_x
    assert target.getY == current.getY + offset_y


def test_invalid_action_mapping_edge_case(env):
    """
    Guarantees architectural rejection of severely out-of-bound categorical commands.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Funnels a maliciously high numerical bound directly into the translation matrix natively.
        Actively captures and safely asserts the localized exception handler successfully intercepts
        undefined operations before causing unmapped memory segment reads.
    """
    current = Position(2, 2)

    with pytest.raises(ValueError, match="Invalid action: 99"):
        env._get_target_position(current, 99)


# ==========================================
# Step Logic, Terminations & Rewards
# ==========================================


def test_step_invalid_move(env):
    """
    Verifies punitive reward applications and episode termination algorithms upon mathematical violations.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Forces a navigational sequence moving beyond spatial boundaries explicitly. Asserts the domain natively
        generates extreme negative reward matrices, securely flags the iteration as mathematically terminated,
        and fundamentally guarantees the foundational trajectory arrays remain pristine and untampered.
    """
    env.reset()

    # The game starts at (0, 0), so moving UP leaves the board.
    observation, reward, terminated, truncated, info = env.step(0)

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == env.config.invalid_move_penalty
    assert terminated is True
    assert truncated is False

    assert info.get("invalid_move") is True
    assert info.get("step_count") == 1

    # An invalid move must not modify the game state.
    assert env.game.getState.getCurrentPosition == Position(0, 0)
    assert env.game.getState.getPath == [Position(0, 0)]


def test_step_valid_move_new_cell(env):
    """
    Evaluates baseline algorithmic incentive distributions across unobstructed topographical explorations.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Derives an explicitly verified clear cell via helper computations natively. Manages a standard
        navigational execution and asserts the resulting reward precisely stacks minor time decay penalties
        against standard discovery bonuses while keeping the operational window securely open.
    """
    env.reset()

    valid_action, target = find_valid_action(env)

    # The selected adjacent cell must be empty, not a waypoint.
    assert env.game.getBoard.getWaypointAt(target) is None

    observation, reward, terminated, truncated, info = env.step(valid_action)

    expected_reward = env.config.step_penalty + env.config.new_cell_reward

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == expected_reward
    assert terminated is False
    assert truncated is False

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is False

    assert env.game.getState.getCurrentPosition == target
    assert target in env.game.getState.getVisitedCells


def test_step_valid_move_waypoint():
    """
    Confirms escalating milestone payouts natively map immediate chronological achievements.

    Implementation Details:
        Constructs a distinct spatial layout hosting nested milestones inherently near the starting point.
        Actively forces intersection with the subsequent logical constraint safely and directly maps the resulting
        array to ensure target objectives naturally cycle while compounding specific achievement metric bonuses.
    """
    board = Board(BOARD_SIZE)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWaypoint(Position(5, 5), 3)

    environment = RLEnvironment(board)
    environment.reset()

    # RIGHT: (0, 0) -> (1, 0), which contains waypoint 2.
    observation, reward, terminated, truncated, info = environment.step(1)

    expected_reward = (
        environment.config.step_penalty + environment.config.next_waypoint_reward
    )

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == expected_reward
    assert terminated is False
    assert truncated is False

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is False

    assert environment.game.getState.getCurrentPosition == Position(1, 0)
    assert environment.game.getState.getNextWaypointOrder == 3

    # Waypoint 3 must now be marked as the next expected waypoint.
    assert observation[7, 5, 5] == 1.0
    assert np.sum(observation[7]) == 1.0


def test_step_final_waypoint_too_early_is_invalid():
    """
    Validates extreme topological logic rejecting endpoint resolutions prior to full Hamiltonian traversal.

    Implementation Details:
        Positions the final milestone immediately adjacent to origin boundaries natively. Initiates direct
        penetration into the terminal node safely and explicitly asserts the rule engine punishes the sequence
        as aggressively as an uncrossable wall collision, collapsing evaluation immediately.
    """
    board = Board(BOARD_SIZE)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)

    environment = RLEnvironment(board)
    environment.reset()

    # RIGHT would enter the final waypoint immediately.
    observation, reward, terminated, truncated, info = environment.step(1)

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == environment.config.invalid_move_penalty
    assert terminated is True
    assert truncated is False

    assert info.get("invalid_move") is True
    assert info.get("step_count") == 1

    assert environment.game.getState.getCurrentPosition == Position(0, 0)
    assert environment.game.getState.getNextWaypointOrder == 2


def test_step_valid_move_finished(env, monkeypatch):
    """
    Evaluates absolute terminal payout mechanics securely concluding a perfectly validated navigation grid.

    Args:
        env: The fully configured reinforcement simulator.
        monkeypatch: The framework tool for dynamic runtime dependency alterations.

    Implementation Details:
        Aggressively stubs the heavily nested architectural rule validator mathematically concluding
        volume limits (since actively walking a full 36-step trajectory is outside boundary tests).
        Processes a generic step natively triggering the mocked completion flag and asserting the delivery
        of massive resolution multipliers ending the active sequence cleanly.
    """
    env.reset()

    valid_action, target = find_valid_action(env)

    monkeypatch.setattr(env.game, "isFinished", lambda: True)

    observation, reward, terminated, truncated, info = env.step(valid_action)

    expected_reward = env.config.step_penalty + env.config.completion_reward

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == expected_reward
    assert terminated is True
    assert truncated is False

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is True

    assert env.game.getState.getCurrentPosition == target


def test_step_truncation_edge_case(env):
    """
    Assesses systemic safety breaks definitively terminating runaway sequential navigation loops.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Re-calibrates the operational maximum loop count to an extreme fractional ceiling natively.
        Processes a fully legitimate execution map avoiding mathematical rule violations and verifies the
        engine still distinctly drops the iteration utilizing the `truncated` output field rather than `terminated`.
    """
    env.reset()

    valid_action, target = find_valid_action(env)

    # The first valid move reaches the configured limit.
    env.config.max_steps = 1

    observation, reward, terminated, truncated, info = env.step(valid_action)

    assert observation.shape == OBSERVATION_SHAPE
    assert terminated is False
    assert truncated is True

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is False

    assert env.game.getState.getCurrentPosition == target


# ==========================================
# Observation Tensor Compilation
# ==========================================


def test_get_observation_zero_waypoints_edge_case(env):
    """
    Secures mathematical normalization boundaries against unsupported unconstrained topological states.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Employs direct internal memory manipulation natively wiping out sequence objective dependencies.
        Requests a direct tensor state representation ensuring all complex fractional division calculations
        fail-safe cleanly to explicit zeros instead of propagating catastrophic divisor errors.
    """
    env.reset()

    env.game.getBoard._waypoints.clear()

    observation = env._get_observation()

    assert observation.shape == OBSERVATION_SHAPE
    assert observation.dtype == np.float32

    # Channel 2 contains normalized waypoint orders.
    assert np.all(observation[2] == 0.0)

    # Channel 7 contains the next expected waypoint.
    assert np.all(observation[7] == 0.0)


def test_get_observation_channels(env):
    """
    Exhaustively verifies localized tensor arrays distinctly illuminate spatial constraints across corresponding channels.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Manipulates architectural constraints aggressively boxing the current location within surrounding barriers safely
        respecting dimensional grids. Rebuilds the numerical state outputs natively and evaluates every independent array
        layer asserting distinct bits accurately flip verifying active positions, trajectory routes, adjacent walls,
        and progressive tracking goals map flawlessly onto neural dimensions.
    """
    env.reset()

    board = env.game.getBoard
    state = env.game.getState

    current = state.getCurrentPosition
    x = current.getX
    y = current.getY

    # Surround the current position with walls wherever the neighboring
    # cell lies inside the board.
    if y > 0:
        board.addWall(current, Position(x, y - 1))

    if x < board.getSize - 1:
        board.addWall(current, Position(x + 1, y))

    if y < board.getSize - 1:
        board.addWall(current, Position(x, y + 1))

    if x > 0:
        board.addWall(current, Position(x - 1, y))

    observation = env._get_observation()

    assert observation.shape == OBSERVATION_SHAPE
    assert observation.dtype == np.float32

    # Channel 0: current position
    assert observation[0, x, y] == 1.0
    assert np.sum(observation[0]) == 1.0

    # Channel 1: visited cells
    assert observation[1, x, y] == 1.0
    assert np.sum(observation[1]) == 1.0

    # Channel 2: waypoint values normalized by waypoint order
    assert observation[2, 0, 0] == pytest.approx(0.5)
    assert observation[2, 5, 5] == pytest.approx(1.0)

    # Channel 3: wall or boundary above
    assert observation[3, x, y] == 1.0

    # Channel 4: wall or boundary to the right
    assert observation[4, x, y] == 1.0

    # Channel 5: wall or boundary below
    assert observation[5, x, y] == 1.0

    # Channel 6: wall or boundary to the left
    assert observation[6, x, y] == 1.0

    # Channel 7: next expected waypoint
    assert observation[7, 5, 5] == 1.0
    assert np.sum(observation[7]) == 1.0


def test_observation_is_contained_in_observation_space(env):
    """
    Secures underlying tensor boundaries computationally validating structural simulation constraints.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Extracts a populated state interpretation natively and explicitly utilizes standard verification bindings
        provided by the analytical platform to guarantee matrix sizes and depth arrays accurately mimic definition specs.
    """
    observation, _ = env.reset()

    assert env.observation_space.contains(observation)


# ==========================================
# Rendering Tests
# ==========================================


def test_render_ansi_mode(env):
    """
    Confirms text-based execution interpretations cleanly form structured representations natively.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Instructs the simulation engine to distinctly route visual diagnostics natively into localized memory.
        Validates the output generates standard character placements successfully mapping structural objects without streaming errors.
    """
    env.reset()

    output = env.render(mode="ansi")

    assert isinstance(output, str)
    assert "@" in output


def test_render_human_mode(env, capsys):
    """
    Validates structural diagnostics sequentially streaming representations strictly to standardized hardware consoles.

    Args:
        env: The fully configured reinforcement simulator.
        capsys: The testing utility tracking natively piped standard output channels.

    Implementation Details:
        Commands the active simulator mapping engine dynamically towards active pipeline streams natively.
        Safely captures and reads textual buffers confirming internal visual layers accurately route expected
        character matrices without crashing runtime rendering logic.
    """
    env.reset()

    result = env.render(mode="human")

    assert result is None

    captured = capsys.readouterr()
    assert "@" in captured.out


def test_render_invalid_mode(env):
    """
    Guarantees structural protection rejecting natively unsupported telemetry representations safely.

    Args:
        env: The fully configured reinforcement simulator.

    Implementation Details:
        Violates expected processing commands injecting unknown parameters directly into standard output functions safely.
        Ensures the execution correctly rejects the sequence explicitly yielding formatted exception hierarchies over
        generating corrupted array layouts.
    """
    env.reset()

    with pytest.raises(ValueError, match="Unsupported render mode"):
        env.render(mode="unsupported_mode")
