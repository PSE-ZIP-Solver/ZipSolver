import pytest
import numpy as np
import gymnasium as gym

from puzzle_logic.data_models import Position
from puzzle_logic.board import Board
from backend.rl import RLEnvironment


# ==========================================
# Setup & Fixtures
# ==========================================

@pytest.fixture
def real_board():
    """Provides a real 6x6 Board instance."""
    return Board(6)

@pytest.fixture
def env(real_board):
    """
    Creates an RLEnvironment using exclusively REAL objects.
    No stubs and no mocked Game engines.
    """
    environment = RLEnvironment(real_board)
    return environment

# ==========================================
# Gym API Contract & Spaces Tests
# ==========================================

def test_initialization(env):
    """Test that spaces strictly match the Gym API and Config."""
    assert isinstance(env.action_space, gym.spaces.Discrete)
    assert env.action_space.n == 4
    
    assert isinstance(env.observation_space, gym.spaces.Box)
    assert env.observation_space.shape == (7, 6, 6)
    assert env.observation_space.dtype == np.float32
    assert env.observation_space.low.min() == 0.0
    assert env.observation_space.high.max() == 1.0

def test_reset(env):
    """Test that reset initializes the real Game and returns standard gym tuples."""
    obs, info = env.reset(seed=42)
    
    assert obs.shape == (7, 6, 6)
    assert isinstance(info, dict)
    assert np.all((obs >= 0.0) & (obs <= 1.0))

# ==========================================
# Action & Target Logic
# ==========================================

@pytest.mark.parametrize("action, offset_x, offset_y", [
    (0, 0, -1), # UP
    (1, 1, 0),  # RIGHT
    (2, 0, 1),  # DOWN
    (3, -1, 0), # LEFT
])
def test_get_target_position(env, action, offset_x, offset_y):
    current = Position(2, 2)
    target = env._get_target_position(current, action)
    assert target.getX == current.getX + offset_x
    assert target.getY == current.getY + offset_y

def test_invalid_action_mapping_edge_case(env):
    """Ensure the environment defends against out-of-bounds discrete actions."""
    current = Position(2, 2)
    with pytest.raises(ValueError, match="Invalid action: 99"):
        env._get_target_position(current, 99)

# ==========================================
# Step Logic, Terminations, & Rewards
# ==========================================

def test_step_invalid_move(env):
    """Test penalty for invalid moves (hitting walls or bounds)."""
    env.reset()
    board = env.game.getBoard
    current = env.game.getState.getCurrentPosition
    
    # We force an invalid move by placing a wall UP, or stepping UP if on the top edge
    target_up = env._get_target_position(current, 0)
    if board.isInside(target_up):
        board.addWall(current, target_up)
        
    obs, reward, terminated, truncated, info = env.step(0) # 0 = UP
    
    assert reward == -100
    assert terminated is True
    assert truncated is False
    assert info.get("invalid_move") is True

def test_step_valid_move_new_cell(env):
    """Test standard exploration reward on the real game engine."""
    env.reset()
    board = env.game.getBoard
    current = env.game.getState.getCurrentPosition
    
    # Ensure there are no waypoints to accidentally trigger the waypoint reward
    board._waypoints.clear() 
    
    # Dynamically find a valid action that doesn't hit a wall/boundary
    valid_action = -1
    for action in range(4):
        target = env._get_target_position(current, action)
        if board.isInside(target) and not board.hasWallBetween(current, target):
            valid_action = action
            break
            
    assert valid_action != -1, "The player spawned fully boxed in, invalid test setup."
    
    obs, reward, terminated, truncated, info = env.step(valid_action)
    
    assert reward == 1
    assert terminated is False
    assert truncated is False
    assert info.get("invalid_move") is False

def test_step_valid_move_waypoint(env):
    """Test reaching a correct waypoint dynamically."""
    env.reset()
    board = env.game.getBoard
    current = env.game.getState.getCurrentPosition
    
    # Dynamically find an open adjacent cell
    valid_action = -1
    target = None
    for action in range(4):
        t = env._get_target_position(current, action)
        if board.isInside(t) and not board.hasWallBetween(current, t):
            valid_action = action
            target = t
            break
            
    # Figure out what waypoint order the real Game state is expecting next
    expected_order = env.game.getState.getNextWaypointOrder
    if expected_order is None:
        expected_order = 1
        
    # Place the real waypoint on the board
    board.addWaypoint(target, expected_order)
    
    obs, reward, terminated, truncated, info = env.step(valid_action)
    assert reward == 10
    assert terminated is False

def test_step_valid_move_finished(env):
    """
    Test episode success conditions. 
    Since solving the real puzzle takes 36 perfectly calculated steps, 
    we dynamically override the instance's isFinished method just for this one assertion.
    """
    env.reset()
    current = env.game.getState.getCurrentPosition
    
    # Find a valid move
    valid_action = -1
    for action in range(4):
        t = env._get_target_position(current, action)
        if env.game.getBoard.isInside(t):
            valid_action = action
            break

    # Trick the real environment into thinking this step is the last one
    env.game.isFinished = lambda: True
    
    obs, reward, terminated, truncated, info = env.step(valid_action)
    assert reward == 100
    assert terminated is True

def test_step_truncation_edge_case(env):
    """Test that max_steps properly raises the 'truncated' flag."""
    env.reset()
    current = env.game.getState.getCurrentPosition
    
    valid_action = -1
    for action in range(4):
        t = env._get_target_position(current, action)
        if env.game.getBoard.isInside(t):
            valid_action = action
            break
            
    # Artificially lower the configuration's max step budget so the VERY NEXT move triggers it
    current_path_length = len(env.game.getState.getPath)
    env.config.max_steps = current_path_length 
    
    obs, reward, terminated, truncated, info = env.step(valid_action)
    
    assert terminated is False
    assert truncated is True


# ==========================================
# Observation Tensor Compilation
# ==========================================

def test_get_observation_zero_waypoints_edge_case(env):
    """Verify division by zero is safely avoided if no waypoints exist on the real board."""
    env.reset()
    env.game.getBoard._waypoints.clear()
    
    obs = env._get_observation()
    assert np.all(obs[2] == 0.0) # Channel 2 should be completely empty

def test_get_observation_channels(env):
    """Ensure all 7 channels accurately represent the true board state."""
    env.reset()
    board = env.game.getBoard
    state = env.game.getState
    
    current = state.getCurrentPosition
    x, y = current.getX, current.getY
    
    # Place real waypoints on the board
    board.addWaypoint(Position(4, 4), 1)
    board.addWaypoint(Position(5, 5), 2)
    
    # Surround the player with walls (respecting boundaries so we don't hit OOB errors)
    if y > 0: board.addWall(current, Position(x, y - 1)) # Above
    if x < 5: board.addWall(current, Position(x + 1, y)) # Right
    if y < 5: board.addWall(current, Position(x, y + 1)) # Below
    if x > 0: board.addWall(current, Position(x - 1, y)) # Left
    
    obs = env._get_observation()
    
    # C0: Current Pos
    assert obs[0, x, y] == 1.0
    assert np.sum(obs[0]) == 1.0 
    
    # C1: Visited (The start position should instantly be marked visited)
    assert obs[1, x, y] == 1.0
    
    # C2: Waypoints (Scaled 1/2 and 2/2)
    assert obs[2, 4, 4] == 0.5
    assert obs[2, 5, 5] == 1.0
    
    # C3-C6: Walls dynamically checked based on where the player spawned
    if y > 0: assert obs[3, x, y] == 1.0
    if x < 5: assert obs[4, x, y] == 1.0
    if y < 5: assert obs[5, x, y] == 1.0
    if x > 0: assert obs[6, x, y] == 1.0

# ==========================================
# Rendering Tests
# ==========================================

def test_render_ansi_mode(env):
    """Test string return generation for ansi mode using real objects."""
    env.reset()
    
    output = env.render(mode="ansi")
    
    assert isinstance(output, str)
    assert "@" in output  # The current position MUST be rendered

def test_render_human_mode(env, capsys):
    """Test standard output printing via human mode."""
    env.reset()
    
    # Render human should return None and print to stdout
    result = env.render(mode="human")
    assert result is None
    
    # Capture standard output printed by the environment
    captured = capsys.readouterr()
    assert "@" in captured.out

def test_render_invalid_mode(env):
    """Test that unsupported render modes throw an exception."""
    env.reset()
    with pytest.raises(ValueError, match="Unsupported render mode"):
        env.render(mode="unsupported_mode")