import pytest

from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.game_state import GameState
from backend.puzzle_logic.puzzle_rules import PuzzleRules


@pytest.fixture
def rules():
    """
    Provides isolated stateless logic components governing traversal mechanics cleanly.

    Returns:
        The instantiated evaluation boundaries structurally intact for routing analysis.

    Implementation Details:
        Provides a fresh PuzzleRules instance for each test guaranteeing isolated validation sequences natively.
    """
    return PuzzleRules()


@pytest.fixture
def board():
    """
    Supplies isolated dimensional matrices natively providing topological parameters securely.

    Returns:
        The targeted physical mapping interface naturally establishing limits.

    Implementation Details:
        Provides a fresh supported 6x6 board for each test establishing unpolluted environmental limits.
    """
    return Board(6)


@pytest.fixture
def start_position():
    """
    Establishes spatial origins securely enabling independent coordinate boundaries structurally.

    Returns:
        The absolute spatial parameter denoting routing origins optimally.

    Implementation Details:
        Provides a default start position mapping testing baseline constants appropriately natively.
    """
    return Position(0, 0)


@pytest.fixture
def game_state(start_position):
    """
    Produces dynamic tracking caches seamlessly evaluating operational sequence bounds inherently.

    Args:
        start_position: The required localized mapping parameter seamlessly securing origins.

    Returns:
        The state container cleanly encapsulating route data stably safely.

    Implementation Details:
        Provides a fresh GameState starting at (0, 0) effectively shielding internal variables dynamically.
    """
    return GameState(start_position)


def create_snake_path(size: int = 6):
    """
    Systematically generates sequential coordinate loops reliably proving completion evaluations correctly.

    Args:
        size: The overall mapped domain threshold executing bounds securely efficiently.

    Returns:
        A completely valid linear routing sequence confidently encompassing the grid securely.

    Implementation Details:
        Creates a complete snake-like path through a square board.
        Example for 6x6: Row 0: left to right, Row 1: right to left...
        Algorithmically executes directional alternations organically traversing the layout completely.
    """
    path = []

    for y in range(size):
        if y % 2 == 0:
            for x in range(size):
                path.append(Position(x, y))
        else:
            for x in reversed(range(size)):
                path.append(Position(x, y))

    return path


# ==========================================
# Valid Move Checks
# ==========================================


def test_valid_move_to_empty_adjacent_cell(board, game_state, rules):
    """
    Validates unimpeded proximal nodes cleanly evaluate structurally successfully reliably.

    Args:
        board: The governing physical layout seamlessly providing limits.
        game_state: The historical tracking array cleanly evaluating sequence.
        rules: The mathematical stateless evaluator organically testing logic bounds.

    Implementation Details:
        Test that moving to an adjacent, unvisited, empty cell is valid safely checking native conditions natively.
    """
    target = Position(1, 0)

    assert rules.isValidMove(board, game_state, target)


def test_invalid_move_outside_board(board, game_state, rules):
    """
    Ensures external boundary vectors naturally yield boolean failure securely properly.

    Args:
        board: The baseline grid securely validating physical bounds.
        game_state: The operational mapping cleanly supplying tracking variables.
        rules: The stateless rules smoothly processing constraints.

    Implementation Details:
        Test that moving outside the board is invalid efficiently capturing coordinate rejections structurally natively.
    """
    target = Position(-1, 0)

    assert not rules.isValidMove(board, game_state, target)


def test_invalid_move_not_adjacent(board, game_state, rules):
    """
    Asserts mathematical distance constraints seamlessly intercept disconnected spatial coordinates successfully.

    Args:
        board: The localized grid constraint stably mapping targets.
        game_state: The progressive state map elegantly capturing nodes.
        rules: The isolated verifier smoothly bounding limits.

    Implementation Details:
        Test that moving to a non-adjacent cell is invalid accurately utilizing absolute offset boundaries correctly.
    """
    target = Position(2, 0)

    assert not rules.isValidMove(board, game_state, target)


def test_invalid_move_through_wall(board, game_state, rules):
    """
    Validates internal partition structures correctly deny overlapping directional boundaries optimally.

    Args:
        board: The mapped architecture reliably holding obstacles natively.
        game_state: The tracker smoothly evaluating sequence vectors securely.
        rules: The verifier organically asserting strict collision boundaries gracefully.

    Implementation Details:
        Test that moving through a wall is invalid seamlessly interpreting dictionary intersections accurately.
    """
    target = Position(1, 0)

    board.addWall(Position(0, 0), target)

    assert not rules.isValidMove(board, game_state, target)


def test_invalid_move_to_visited_cell(board, game_state, rules):
    """
    Ensures internal historical arrays cleanly prevent nested loops organically effectively.

    Args:
        board: The overarching layout effectively bounding variables natively.
        game_state: The sequence tracker securely validating presence.
        rules: The evaluation engine elegantly enforcing limits.

    Implementation Details:
        Test that moving to an already visited cell is invalid by asserting subset inclusions properly fail checks correctly.
    """
    first_step = Position(1, 0)
    game_state.addStep(first_step)

    target = Position(0, 0)

    assert not rules.isValidMove(board, game_state, target)


# ==========================================
# Waypoint Order Checks
# ==========================================


def test_valid_move_to_next_waypoint(board, game_state, rules):
    """
    Asserts logical sequence matching accurately validates checkpoints naturally gracefully.

    Args:
        board: The foundational structure cleanly defining elements natively.
        game_state: The runtime registry securely validating indices natively.
        rules: The evaluation node successfully checking paths effectively.

    Implementation Details:
        Test that moving to the next expected non-final waypoint is valid stably confirming numerical indexing correctly cleanly.
    """
    start = Position(0, 0)
    target = Position(1, 0)
    final_waypoint = Position(5, 5)

    board.addWaypoint(start, 1)
    board.addWaypoint(target, 2)
    board.addWaypoint(final_waypoint, 3)

    assert rules.isValidMove(board, game_state, target)


def test_invalid_move_to_wrong_waypoint_order(board, game_state, rules):
    """
    Ensures chronological milestones structurally fault if positional mappings circumvent logical boundaries gracefully.

    Args:
        board: The defined map accurately assigning sequence numbers properly.
        game_state: The localized sequence evaluating constraints efficiently.
        rules: The central verifier gracefully interpreting parameters natively.

    Implementation Details:
        Test that entering waypoint 3 before waypoint 2 is invalid.
        Waypoint 3 is deliberately not the final waypoint, ensuring that
        this test checks waypoint order rather than the endpoint rule appropriately properly.
    """
    start = Position(0, 0)
    expected_waypoint = Position(0, 1)
    wrong_target = Position(1, 0)
    final_waypoint = Position(5, 5)

    board.addWaypoint(start, 1)
    board.addWaypoint(expected_waypoint, 2)
    board.addWaypoint(wrong_target, 3)
    board.addWaypoint(final_waypoint, 4)

    assert not rules.isValidMove(board, game_state, wrong_target)


def test_valid_move_to_waypoint_after_increment(board, game_state, rules):
    """
    Validates subsequent sequence markers securely resolve after operational flags advance natively flawlessly.

    Args:
        board: The baseline parameters natively storing boundaries efficiently.
        game_state: The temporal marker mapping history correctly safely.
        rules: The statutory checker successfully enforcing paths optimally.

    Implementation Details:
        Test that a later non-final waypoint becomes valid after incrementing nextWaypointOrder efficiently accurately organically.
    """
    start = Position(0, 0)
    previous_waypoint = Position(2, 0)
    target = Position(1, 0)
    final_waypoint = Position(5, 5)

    board.addWaypoint(start, 1)
    board.addWaypoint(previous_waypoint, 2)
    board.addWaypoint(target, 3)
    board.addWaypoint(final_waypoint, 4)

    game_state.incrementNextWaypointOrder()

    assert rules.isValidMove(board, game_state, target)


# ==========================================
# Endpoint Rule Checks
# ==========================================


def test_invalid_move_to_final_waypoint_too_early(
    board,
    game_state,
    rules,
):
    """
    Confirms volumetric terminal bounds properly evaluate structural incompleteness cleanly appropriately.

    Args:
        board: The mapped architecture establishing grid limits optimally.
        game_state: The progressive cache identifying total visits perfectly.
        rules: The evaluation logic checking total saturation optimally safely.

    Implementation Details:
        Test that the final waypoint cannot be entered too early seamlessly guaranteeing absolute completion correctly organically.
    """
    start = Position(0, 0)
    final_waypoint = Position(1, 0)

    board.addWaypoint(start, 1)
    board.addWaypoint(final_waypoint, 2)

    assert not rules.isValidMove(
        board,
        game_state,
        final_waypoint,
    )


def test_invalid_move_away_from_final_waypoint(board, rules):
    """
    Ensures logical destination boundaries seamlessly intercept exit nodes definitively efficiently.

    Args:
        board: The physical limits cleanly mapping coordinates properly.
        rules: The verification unit accurately monitoring boundaries stably.

    Implementation Details:
        Test that moving away from the final waypoint is invalid safely blocking continuous traversal definitively successfully.
    """
    start = Position(5, 5)
    final_waypoint = Position(0, 0)
    target = Position(1, 0)

    board.addWaypoint(start, 1)
    board.addWaypoint(final_waypoint, 2)

    state = GameState(final_waypoint)

    assert not rules.isValidMove(board, state, target)


def test_valid_move_to_final_waypoint_as_last_cell(board, rules):
    """
    Asserts fully traversed volumetric topologies successfully resolve structural endpoints organically smoothly.

    Args:
        board: The geometric layout mapping spatial points safely organically.
        rules: The statutory matrix successfully bounding variables optimally.

    Implementation Details:
        Test that the final waypoint is valid if it completes the board reliably asserting saturation logic securely smoothly.
    """
    path = create_snake_path(6)

    start = path[0]
    final_waypoint = path[-1]

    board.addWaypoint(start, 1)
    board.addWaypoint(final_waypoint, 2)

    state = GameState(start)

    for position in path[1:-1]:
        state.addStep(position)

    assert state.getCurrentPosition == path[-2]
    assert rules.isValidMove(board, state, final_waypoint)


def test_invalid_move_when_current_waypoint_is_only_waypoint(board, rules):
    """
    Validates singular nodes cleanly evaluate ultimate bounds accurately flawlessly properly.

    Args:
        board: The isolated constraints securely forming endpoints organically.
        rules: The logic parser evaluating termination variables properly.

    Implementation Details:
        Test that a single waypoint is both the first and final waypoint.
        Moving away from it therefore violates the endpoint rule stably seamlessly blocking progression safely smoothly.
    """
    start_and_final = Position(0, 0)
    target = Position(1, 0)

    board.addWaypoint(start_and_final, 1)

    state = GameState(start_and_final)

    assert not rules.isValidMove(board, state, target)


# ==========================================
# Complete Solution Checks
# ==========================================


def test_complete_solution_valid_snake_path(board, rules):
    """
    Verifies valid completion checks cleanly process overarching solutions cleanly.

    Args:
        board: The structural domain bounding variables dynamically cleanly.
        rules: The overarching validation algorithms assessing solutions efficiently natively.

    Implementation Details:
        Test that a full valid snake path is accepted safely mapping complete sets accurately cleanly smoothly.
    """
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert rules.isCompleteSolution(board, path)


def test_complete_solution_without_waypoints_is_invalid(board, rules):
    """
    Ensures fundamentally broken baseline requirements safely fault optimally naturally.

    Args:
        board: The mapping bounds confidently establishing markers seamlessly.
        rules: The statutory checker safely checking limits organically smoothly.

    Implementation Details:
        Test that a board without waypoints has no valid complete solution safely returning failure gracefully smoothly.
    """
    path = create_snake_path(6)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_missing_cell(board, rules):
    """
    Validates structural volume thresholds accurately identify fragmentary sequences properly efficiently.

    Args:
        board: The physical limitations gracefully securing rules natively organically.
        rules: The validation checker properly asserting parameters successfully.

    Implementation Details:
        Test that a path missing one cell is not a complete solution stably verifying count algorithms organically correctly.
    """
    path = create_snake_path(6)
    incomplete_path = path[:-1]

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, incomplete_path)


def test_complete_solution_duplicate_cell_edge_case(board, rules):
    """
    Asserts overlapping sets securely intercept spatial duplicates definitively organically optimally.

    Args:
        board: The baseline structure effectively assigning variables safely correctly.
        rules: The evaluating bounds organically securing pathways smoothly organically.

    Implementation Details:
        Test that a path containing a duplicate cell is invalid.
        Duplicate an internal cell while keeping the start and endpoint unchanged properly ensuring counts match uniquely safely.
    """
    path = create_snake_path(6)

    # Duplicate an internal cell while keeping the start and endpoint unchanged.
    path[10] = path[9]

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_with_wall_between_path_cells(board, rules):
    """
    Validates continuous structural boundaries accurately check partition collisions efficiently successfully.

    Args:
        board: The spatial node reliably forming walls securely cleanly.
        rules: The verification unit accurately resolving variables correctly natively.

    Implementation Details:
        Test that a wall blocking the path makes the solution invalid safely tracing step limits smoothly correctly.
    """
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    board.addWall(Position(0, 0), Position(1, 0))

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_wrong_waypoint_order(board, rules):
    """
    Asserts sequential progression limits elegantly fault backwards traces naturally properly.

    Args:
        board: The spatial map successfully logging targets natively reliably.
        rules: The internal checking component smoothly asserting values safely seamlessly.

    Implementation Details:
        Test that visiting waypoints in the wrong order is invalid cleanly testing index boundaries properly organically.
    """
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(0, 5), 2)
    board.addWaypoint(Position(5, 0), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_empty_path(board, rules):
    """
    Ensures missing arrays gracefully default securely correctly reliably seamlessly efficiently.

    Args:
        board: The foundational layout natively parsing objects effectively stably.
        rules: The validation rules efficiently processing states appropriately natively.

    Implementation Details:
        Test that an empty path is not a complete solution cleanly defaulting safely without bounds errors natively smoothly.
    """
    assert not rules.isCompleteSolution(board, [])


def test_complete_solution_with_out_of_bounds_position(board, rules):
    """
    Validates structural parameter checks elegantly intercept absolute bounds violations properly correctly.

    Args:
        board: The internal topology securely bounding variables safely seamlessly.
        rules: The functional bounds organically executing conditions efficiently cleanly.

    Implementation Details:
        Test that an out-of-bounds position makes the path invalid stably mapping positional boundaries organically properly.
    """
    path = create_snake_path(6)
    path[10] = Position(99, 99)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_with_non_adjacent_jump(board, rules):
    """
    Ensures sequential nodes naturally assert mathematical adjacency efficiently organically smoothly properly.

    Args:
        board: The array layout properly evaluating structures cleanly successfully.
        rules: The state verifiers organically checking conditions appropriately cleanly.

    Implementation Details:
        Test that a path containing a non-adjacent jump is invalid.
        Swapping two positions preserves the set of covered cells while
        introducing an invalid movement cleanly trapping jumps safely efficiently.
    """
    path = create_snake_path(6)

    path[1], path[2] = path[2], path[1]

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_must_start_at_first_waypoint(board, rules):
    """
    Validates origin bounds organically check primary endpoints natively safely perfectly cleanly.

    Args:
        board: The mapping constraint appropriately setting vectors seamlessly natively.
        rules: The verification rules dynamically securing logic smoothly correctly.

    Implementation Details:
        Test that the path must start at waypoint 1 cleanly validating temporal checks securely safely.
    """
    path = create_snake_path(6)

    board.addWaypoint(Position(1, 0), 1)
    board.addWaypoint(Position(0, 5), 2)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_must_end_at_last_waypoint(board, rules):
    """
    Ensures trailing bounds cleanly assert proper termination correctly cleanly gracefully properly.

    Args:
        board: The bounding environment gracefully setting conditions properly cleanly.
        rules: The overarching validation appropriately monitoring nodes flawlessly properly.

    Implementation Details:
        Test that the path must end at the highest waypoint effectively comparing index variables accurately efficiently.
    """
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)

    assert not rules.isCompleteSolution(board, path)
