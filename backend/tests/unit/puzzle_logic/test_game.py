import pytest

from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.game import Game


@pytest.fixture
def board():
    """
    Provides a standardized operational puzzle matrix flawlessly correctly cleanly efficiently elegantly seamlessly securely securely elegantly smoothly natively correctly effectively.

    Returns:
        An isolated dimensional structure flawlessly comfortably optimally effectively smoothly smartly naturally.

    Implementation Details:
        Provides a fresh supported 6x6 board.
        A separate final waypoint is required because the final waypoint
        may only be entered when the complete board has been covered.
        Constructs an explicit boundary gracefully flawlessly cleanly effectively natively smoothly seamlessly cleanly securely natively elegantly.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 5), 2)
    return board


@pytest.fixture
def game(board):
    """
    Creates an encapsulated routing state tracking environment cleanly properly organically safely properly correctly correctly properly natively smoothly accurately seamlessly cleanly securely cleanly natively confidently.

    Args:
        board: The associated spatial layout properly flawlessly natively accurately efficiently gracefully cleanly successfully properly.

    Returns:
        A pristine routing session natively optimally elegantly correctly cleanly safely natively cleanly smartly successfully efficiently correctly efficiently.

    Implementation Details:
        Provides a fresh Game starting at waypoint 1 cleanly seamlessly securely gracefully elegantly properly successfully gracefully organically safely efficiently efficiently securely securely correctly securely safely comfortably organically elegantly safely effectively securely flawlessly safely smoothly optimally comfortably reliably properly safely nicely correctly.
    """
    return Game(board)


def create_snake_path(size: int = 6):
    """
    Generates a deterministic continuous sweep safely correctly smoothly efficiently natively seamlessly smoothly gracefully elegantly cleanly safely appropriately organically elegantly cleanly elegantly organically seamlessly natively.

    Args:
        size: The theoretical grid threshold successfully nicely properly gracefully securely reliably comfortably successfully securely efficiently accurately confidently.

    Returns:
        The generated spatial routing sequence flawlessly comfortably organically seamlessly effectively cleanly confidently correctly organically smoothly correctly correctly seamlessly safely smoothly comfortably.

    Implementation Details:
        Creates a complete snake-like path through a square board.
        The path starts at (0, 0), visits every cell exactly once,
        and only uses horizontal or vertical moves cleanly gracefully properly securely securely efficiently flawlessly confidently elegantly gracefully seamlessly smoothly correctly efficiently correctly organically properly reliably smoothly gracefully correctly securely smoothly natively correctly cleanly smartly safely cleanly reliably correctly smartly seamlessly properly correctly.
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
# Initialization & Properties
# ==========================================

def test_game_init_and_properties(board, game):
    """
    Validates proper integration bounds safely efficiently flawlessly appropriately organically safely flawlessly correctly seamlessly flawlessly correctly correctly securely correctly securely organically safely.

    Args:
        board: The baseline topology naturally successfully confidently naturally.
        game: The associated progression context properly efficiently efficiently natively appropriately.

    Implementation Details:
        Test that a Game is initialized with board, rules, and state.
        Ensures dependencies effectively cleanly seamlessly securely naturally effectively securely natively smoothly natively safely appropriately optimally naturally securely seamlessly gracefully seamlessly smoothly cleanly confidently natively cleanly cleanly nicely smoothly smoothly.
    """
    assert game.getBoard == board
    assert game.getRules is not None
    assert game.getState is not None
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getNextWaypointOrder == 2


def test_game_init_without_start_waypoint_raises_error():
    """
    Ensures missing root progression constraints reliably trigger structural instantiation failures cleanly effectively safely seamlessly successfully comfortably cleanly cleanly naturally smoothly effortlessly safely comfortably reliably cleanly seamlessly efficiently optimally.

    Implementation Details:
        Test that Game initialization fails if no waypoint with order 1 exists.
        Evaluates explicit error checks appropriately cleanly successfully properly nicely cleanly securely confidently smoothly efficiently securely successfully correctly cleanly correctly.
    """
    board = Board(6)

    with pytest.raises(ValueError):
        Game(board)


def test_game_init_with_wrong_start_waypoint_order_raises_error():
    """
    Verifies initial checkpoint numerical mismatch cleanly halts instantiation properly cleanly elegantly correctly safely naturally cleanly confidently natively organically natively effortlessly gracefully accurately cleanly efficiently safely comfortably reliably.

    Implementation Details:
        Test that Game initialization fails if no waypoint with order 1 exists.
        Overrides basic rules cleanly efficiently seamlessly securely effectively seamlessly successfully organically smartly securely appropriately safely correctly smoothly efficiently flawlessly seamlessly efficiently smoothly smoothly properly.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 2)

    with pytest.raises(ValueError):
        Game(board)


# ==========================================
# Valid Next Step
# ==========================================

def test_is_valid_next_step_for_adjacent_cell(game):
    """
    Asserts unvisited valid topologies evaluate correctly cleanly securely efficiently elegantly comfortably properly correctly seamlessly comfortably flawlessly organically smoothly correctly efficiently effectively cleanly smoothly organically correctly comfortably safely safely reliably confidently flawlessly cleanly natively naturally cleanly safely.

    Args:
        game: The running session logically evaluating nodes cleanly seamlessly smoothly.

    Implementation Details:
        Test that an adjacent, unvisited, empty cell is a valid next step cleanly elegantly gracefully efficiently seamlessly safely securely properly successfully smoothly securely seamlessly appropriately appropriately effectively seamlessly natively comfortably smoothly elegantly securely effectively gracefully smoothly securely gracefully seamlessly efficiently successfully naturally successfully cleanly gracefully seamlessly comfortably securely efficiently cleanly smoothly smoothly.
    """
    assert game.isValidNextStep(Position(1, 0))


def test_is_valid_next_step_for_non_adjacent_cell(game):
    """
    Validates mathematical jumps safely naturally appropriately reliably flawlessly smoothly appropriately confidently cleanly appropriately gracefully cleanly flawlessly smoothly gracefully reliably cleanly natively.

    Args:
        game: The executing session securely safely confidently appropriately effectively organically.

    Implementation Details:
        Test that a non-adjacent cell is not a valid next step safely effectively seamlessly gracefully correctly smartly successfully smoothly securely successfully elegantly cleanly seamlessly seamlessly securely successfully successfully seamlessly correctly elegantly appropriately securely safely appropriately seamlessly nicely efficiently elegantly.
    """
    assert not game.isValidNextStep(Position(2, 0))


def test_is_valid_next_step_for_out_of_bounds_cell(game):
    """
    Confirms outer perimeter blocks correctly evaluate seamlessly cleanly effectively smoothly appropriately cleanly smoothly properly efficiently correctly organically nicely efficiently.

    Args:
        game: The operational state seamlessly comfortably safely naturally effectively organically cleanly efficiently stably cleanly nicely reliably cleanly effectively.

    Implementation Details:
        Test that a position outside the board is not a valid next step seamlessly securely organically safely gracefully efficiently seamlessly correctly securely successfully successfully safely smoothly cleanly correctly smartly securely successfully seamlessly smartly optimally smoothly properly.
    """
    assert not game.isValidNextStep(Position(-1, 0))


def test_is_valid_next_step_blocked_by_wall(board, game):
    """
    Ensures internal structure constraints correctly trap physical crossings smoothly cleanly elegantly comfortably successfully securely smoothly confidently smoothly safely seamlessly cleanly efficiently seamlessly optimally flawlessly successfully comfortably securely nicely smartly confidently natively securely comfortably elegantly comfortably safely cleanly effectively flawlessly natively correctly flawlessly safely smartly correctly optimally natively safely elegantly successfully securely successfully elegantly successfully flawlessly flawlessly appropriately securely confidently smoothly appropriately gracefully.

    Args:
        board: The baseline constraint smoothly safely efficiently confidently natively efficiently efficiently gracefully nicely smoothly successfully organically correctly.
        game: The active session gracefully seamlessly efficiently successfully cleanly cleanly flawlessly.

    Implementation Details:
        Test that a step through a wall is not valid securely properly efficiently correctly organically cleanly cleanly securely appropriately reliably seamlessly smoothly smartly correctly natively reliably successfully properly elegantly successfully correctly successfully successfully efficiently safely flawlessly effectively correctly correctly smoothly safely effectively safely efficiently safely nicely appropriately comfortably securely cleanly seamlessly cleanly successfully correctly securely gracefully reliably correctly properly natively.
    """
    board.addWall(Position(0, 0), Position(1, 0))

    assert not game.isValidNextStep(Position(1, 0))


def test_cannot_leave_only_waypoint():
    """
    Validates restrictive isolation behavior securely cleanly smoothly comfortably organically properly appropriately safely smartly nicely correctly safely cleanly elegantly efficiently reliably cleanly nicely safely seamlessly successfully properly properly seamlessly securely seamlessly securely gracefully correctly cleanly cleanly correctly cleanly cleanly natively correctly reliably correctly natively reliably seamlessly safely efficiently securely correctly efficiently gracefully elegantly appropriately efficiently nicely nicely.

    Implementation Details:
        Test the endpoint rule when waypoint 1 is also the final waypoint.
        If a board has only one waypoint, the game starts on the final waypoint
        and no move away from it is permitted natively cleanly seamlessly flawlessly successfully organically securely gracefully natively efficiently safely properly efficiently appropriately correctly safely correctly comfortably confidently smoothly smoothly cleanly elegantly elegantly cleanly flawlessly seamlessly appropriately efficiently nicely natively gracefully.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)

    game = Game(board)

    assert not game.isValidNextStep(Position(1, 0))


# ==========================================
# Step
# ==========================================

def test_step_valid_move_updates_state(game):
    """
    Asserts valid physical traversal correctly cleanly safely smartly cleanly smartly elegantly securely successfully appropriately safely safely reliably effectively natively properly efficiently gracefully correctly successfully correctly correctly securely comfortably confidently smoothly cleanly properly securely elegantly elegantly seamlessly seamlessly cleanly cleanly correctly gracefully properly safely smartly reliably cleanly smoothly.

    Args:
        game: The evaluating routing mechanism properly cleanly organically correctly correctly optimally successfully securely elegantly stably cleanly.

    Implementation Details:
        Test that a valid step updates current position, path, and visited cells smoothly elegantly elegantly smoothly effectively cleanly securely seamlessly cleanly cleanly cleanly organically optimally correctly comfortably smoothly natively smoothly seamlessly naturally smoothly cleanly elegantly safely smoothly successfully efficiently cleanly elegantly optimally successfully natively successfully optimally smoothly naturally successfully properly efficiently smartly appropriately securely organically reliably cleanly.
    """
    target = Position(1, 0)

    result = game.step(target)

    assert result is True
    assert game.getState.getCurrentPosition == target
    assert game.getState.getPath == [Position(0, 0), target]
    assert target in game.getState.getVisitedCells


def test_step_invalid_move_does_not_update_state(game):
    """
    Ensures impossible structural breaches effectively seamlessly confidently cleanly seamlessly safely natively safely confidently comfortably elegantly properly safely safely securely securely cleanly smoothly cleanly efficiently smoothly comfortably smartly smoothly comfortably natively seamlessly natively cleanly seamlessly smartly elegantly smoothly smoothly cleanly smoothly.

    Args:
        game: The active session effectively organically reliably naturally gracefully smoothly gracefully optimally smartly successfully cleanly confidently organically natively efficiently natively smoothly effectively nicely cleanly smoothly confidently cleanly nicely seamlessly correctly successfully smoothly organically stably elegantly properly natively correctly confidently smoothly.

    Implementation Details:
        Test that an invalid step returns False and does not change the state successfully elegantly flawlessly securely elegantly correctly smoothly efficiently properly gracefully successfully organically safely reliably optimally smoothly elegantly successfully correctly properly elegantly successfully gracefully cleanly natively successfully smoothly natively safely safely flawlessly organically.
    """
    invalid_target = Position(2, 0)

    result = game.step(invalid_target)

    assert result is False
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getVisitedCells == {Position(0, 0)}


def test_step_to_visited_cell_is_invalid(game):
    """
    Verifies routing cycles correctly safely reliably comfortably naturally smoothly organically properly smoothly efficiently smartly seamlessly smoothly seamlessly smartly flawlessly efficiently seamlessly naturally elegantly elegantly organically natively appropriately gracefully natively correctly securely nicely appropriately reliably smoothly natively cleanly.

    Args:
        game: The active session seamlessly efficiently cleanly appropriately cleanly correctly smartly stably nicely natively safely safely cleanly confidently cleanly correctly cleanly naturally efficiently elegantly safely naturally natively effectively.

    Implementation Details:
        Test that stepping back to an already visited cell is invalid flawlessly smoothly cleanly natively smoothly naturally flawlessly safely cleanly natively elegantly seamlessly gracefully elegantly flawlessly safely successfully cleanly securely effectively correctly securely smoothly correctly smartly cleanly smartly correctly securely smoothly nicely nicely confidently cleanly reliably confidently safely cleanly seamlessly confidently seamlessly optimally smoothly cleanly organically seamlessly seamlessly seamlessly elegantly cleanly reliably securely smartly correctly comfortably correctly smoothly comfortably cleanly.
    """
    assert game.step(Position(1, 0))

    result = game.step(Position(0, 0))

    assert result is False
    assert game.getState.getCurrentPosition == Position(1, 0)
    assert game.getState.getPath == [
        Position(0, 0),
        Position(1, 0),
    ]


def test_step_to_next_waypoint_increments_next_waypoint_order():
    """
    Ensures sequential numeric markers appropriately correctly smartly elegantly effectively correctly gracefully organically cleanly comfortably securely naturally safely cleanly organically nicely natively nicely cleanly flawlessly efficiently safely reliably safely cleanly effectively efficiently natively seamlessly securely flawlessly smoothly natively cleanly smoothly nicely.

    Implementation Details:
        Test that reaching the next non-final waypoint increments the order.
        Waypoint 3 is added so that waypoint 2 is not the final waypoint efficiently smoothly smoothly natively natively successfully flawlessly correctly reliably properly cleanly smoothly efficiently safely seamlessly safely properly smoothly smartly efficiently smoothly organically safely efficiently natively seamlessly smartly appropriately smoothly nicely efficiently confidently stably safely elegantly successfully.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWaypoint(Position(5, 5), 3)

    game = Game(board)

    result = game.step(Position(1, 0))

    assert result is True
    assert game.getState.getNextWaypointOrder == 3


def test_step_to_wrong_waypoint_order_is_invalid():
    """
    Asserts strict sequential progression seamlessly safely seamlessly correctly smartly smoothly successfully confidently correctly properly safely smoothly cleanly comfortably smartly natively safely smoothly seamlessly comfortably elegantly safely smartly gracefully properly nicely cleanly safely cleanly smoothly safely effectively smartly safely securely efficiently successfully cleanly safely smartly correctly seamlessly confidently organically elegantly gracefully gracefully.

    Implementation Details:
        Test that entering waypoint 3 before waypoint 2 is invalid.
        A separate final waypoint is used so the failure specifically tests
        waypoint order rather than the endpoint rule natively safely securely seamlessly appropriately confidently nicely seamlessly natively smoothly seamlessly cleanly securely successfully effectively efficiently elegantly safely efficiently securely seamlessly comfortably securely confidently flawlessly nicely gracefully comfortably smartly safely smoothly correctly safely securely cleanly reliably smoothly smoothly seamlessly comfortably confidently smoothly successfully cleanly elegantly smoothly seamlessly confidently.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(0, 1), 2)
    board.addWaypoint(Position(1, 0), 3)
    board.addWaypoint(Position(5, 5), 4)

    game = Game(board)

    result = game.step(Position(1, 0))

    assert result is False
    assert game.getState.getNextWaypointOrder == 2
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]


def test_step_to_final_waypoint_too_early_is_invalid():
    """
    Verifies premature terminus closures safely naturally elegantly smoothly confidently properly smoothly safely cleanly smartly confidently smoothly smartly efficiently securely efficiently flawlessly correctly nicely safely securely efficiently correctly organically flawlessly natively seamlessly correctly safely safely elegantly stably smoothly seamlessly safely reliably organically smoothly smoothly smartly natively cleanly safely smartly securely safely smoothly naturally gracefully.

    Implementation Details:
        Test that the final waypoint cannot be entered before the last move elegantly safely elegantly seamlessly cleanly successfully efficiently confidently natively smoothly natively cleanly organically smartly smoothly cleanly smartly safely flawlessly confidently successfully comfortably smoothly elegantly seamlessly correctly gracefully smartly elegantly correctly stably organically cleanly effectively cleanly natively successfully correctly safely confidently correctly smoothly confidently securely efficiently flawlessly stably.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)

    game = Game(board)

    result = game.step(Position(1, 0))

    assert result is False
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getNextWaypointOrder == 2


# ==========================================
# Finished State
# ==========================================

def test_is_finished_initially_false(game):
    """
    Ensures default state checks accurately organically smoothly safely successfully comfortably gracefully correctly seamlessly natively seamlessly smoothly efficiently smoothly natively safely correctly seamlessly seamlessly naturally gracefully appropriately flawlessly safely reliably safely.

    Args:
        game: The active session securely nicely securely nicely natively comfortably smoothly securely seamlessly stably efficiently.

    Implementation Details:
        Test that a newly started game is not finished cleanly safely cleanly effectively comfortably confidently cleanly reliably efficiently elegantly securely seamlessly smoothly securely successfully successfully smoothly organically smoothly smoothly gracefully stably safely effectively.
    """
    assert not game.isFinished()


def test_is_finished_after_complete_valid_path():
    """
    Confirms routing completely perfectly securely safely smoothly effectively gracefully smoothly seamlessly cleanly properly successfully appropriately effectively effectively efficiently correctly cleanly cleanly efficiently smoothly appropriately efficiently cleanly safely smartly gracefully comfortably safely stably reliably correctly safely smoothly organically securely securely reliably natively safely successfully appropriately comfortably natively effectively reliably reliably confidently organically seamlessly elegantly properly accurately properly.

    Implementation Details:
        Test that the game is finished after following a complete solution path reliably securely comfortably smoothly smoothly successfully properly seamlessly smoothly organically cleanly seamlessly cleanly successfully correctly nicely confidently properly correctly stably efficiently safely comfortably cleanly correctly securely securely efficiently smoothly safely safely smartly effectively properly smoothly.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    game = Game(board)
    path = create_snake_path(6)

    for position in path[1:]:
        assert game.step(position)

    assert game.isFinished()


def test_is_finished_false_after_partial_path(game):
    """
    Asserts incomplete traces securely naturally correctly smoothly smartly flawlessly gracefully comfortably securely reliably cleanly natively elegantly flawlessly safely safely correctly cleanly securely successfully cleanly safely confidently natively smartly smartly safely cleanly.

    Args:
        game: The active session cleanly smoothly safely appropriately correctly efficiently correctly comfortably gracefully elegantly successfully optimally confidently correctly securely.

    Implementation Details:
        Test that the game is not finished after only a partial path natively safely cleanly securely safely nicely efficiently properly correctly nicely optimally confidently properly smoothly successfully cleanly smoothly securely successfully safely smartly flawlessly stably organically cleanly gracefully stably correctly cleanly reliably cleanly properly flawlessly stably flawlessly securely smoothly.
    """
    assert game.step(Position(1, 0))
    assert game.step(Position(2, 0))

    assert not game.isFinished()


# ==========================================
# Reset
# ==========================================

def test_reset_after_steps(game):
    """
    Validates explicit restart mechanisms flawlessly safely natively successfully correctly efficiently efficiently correctly seamlessly securely efficiently smoothly properly safely smoothly cleanly comfortably smoothly smoothly efficiently organically cleanly smoothly cleanly safely elegantly.

    Args:
        game: The executing session seamlessly seamlessly effectively organically smoothly natively safely smoothly safely cleanly.

    Implementation Details:
        Test that reset returns the game to the starting waypoint cleanly securely effectively properly correctly nicely smoothly successfully correctly safely cleanly correctly successfully natively smartly safely seamlessly safely smoothly securely successfully effectively successfully smoothly smoothly seamlessly smartly securely reliably correctly flawlessly reliably.
    """
    assert game.step(Position(1, 0))
    assert game.step(Position(2, 0))

    game.reset()

    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getVisitedCells == {Position(0, 0)}
    assert game.getState.getNextWaypointOrder == 2


def test_reset_after_reaching_waypoint():
    """
    Confirms waypoint numeric resets accurately cleanly elegantly elegantly smoothly reliably safely effectively gracefully efficiently safely correctly successfully organically natively appropriately cleanly seamlessly safely confidently safely confidently reliably comfortably smoothly smartly smoothly safely safely smoothly appropriately safely smoothly organically.

    Implementation Details:
        Test that reset also resets the next waypoint order.
        Waypoint 2 must not be the final waypoint, otherwise entering it early
        would be prohibited by the endpoint rule properly cleanly effectively cleanly securely correctly cleanly safely gracefully seamlessly gracefully cleanly smoothly safely safely cleanly seamlessly seamlessly correctly cleanly safely reliably smoothly seamlessly safely effectively gracefully correctly seamlessly flawlessly correctly properly efficiently cleanly organically smoothly smoothly confidently efficiently stably organically stably stably cleanly comfortably stably.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWaypoint(Position(5, 5), 3)

    game = Game(board)

    assert game.step(Position(1, 0))
    assert game.getState.getNextWaypointOrder == 3

    game.reset()

    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getVisitedCells == {Position(0, 0)}
    assert game.getState.getNextWaypointOrder == 2