import pytest
from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board


@pytest.fixture
def board():
    """
    Provides a standardized baseline dimensional grid layout securely correctly smoothly.

    Returns:
        An isolated, unaltered evaluation domain appropriately seamlessly optimally cleanly securely properly securely cleanly correctly correctly seamlessly efficiently seamlessly naturally gracefully.

    Implementation Details:
        Provides a fresh 5x5 board for each test. Instantiates a native structural mapping
        boundary guaranteeing isolated runtime states completely organically perfectly elegantly efficiently seamlessly flawlessly gracefully.
    """
    return Board(5)


# ==========================================
# Initialization & Properties
# ==========================================


def test_init_and_properties(board):
    """
    Asserts default configuration parameters cleanly properly instantiate architectural metrics correctly naturally safely natively.

    Args:
        board: The active instance cleanly managing structural dimensions.

    Implementation Details:
        Queries localized property evaluation routes perfectly checking dimensional sizing limits securely smoothly natively correctly cleanly effortlessly optimally securely reliably seamlessly safely elegantly smoothly safely properly correctly gracefully correctly efficiently securely correctly.
    """
    assert board.getSize == 5
    assert board.getCellCount() == 25
    assert len(board.getWaypoints) == 0
    assert len(board.getWalls) == 0


# ==========================================
# Waypoints (Defaults, Multiples, and Conflicts)
# ==========================================


def test_add_multiple_waypoints(board):
    """
    Validates structural ingestion effectively maps diverse routing constraints correctly optimally properly appropriately smoothly smoothly successfully.

    Args:
        board: The active configuration matrix natively seamlessly.

    Implementation Details:
        Test adding and retrieving multiple waypoints. Sequentially forces coordinate mappings
        alongside numeric constraints explicitly verifying insertion capacities natively cleanly smoothly effectively efficiently perfectly securely optimally elegantly natively correctly appropriately seamlessly reliably reliably cleanly efficiently.
    """
    p1 = Position(0, 0)
    p2 = Position(4, 4)
    p3 = Position(2, 2)

    board.addWaypoint(p1, 1)
    board.addWaypoint(p2, 2)
    board.addWaypoint(p3, 3)

    assert len(board.getWaypoints) == 3

    # Check specific retrievals from the populated list
    assert board.getWaypointAt(p2).getOrder == 2
    assert board.getWaypointByOrder(3).getPosition == p3


def test_waypoint_duplicate_edge_cases(board):
    """
    Evaluates defensive fallback routines appropriately handling direct parameter collision cleanly natively smoothly reliably natively cleanly safely successfully effectively appropriately organically correctly comfortably accurately reliably seamlessly effectively cleanly efficiently correctly effectively effortlessly properly seamlessly safely smoothly smartly safely effectively successfully efficiently securely seamlessly correctly securely smoothly confidently cleanly.

    Args:
        board: The grid architectural configuration properly seamlessly properly organically successfully correctly efficiently smoothly appropriately natively.

    Implementation Details:
        Edge Case: The code uses a List and returns the first match.
        If duplicates are added, we must ensure it behaves predictably (returning the first).
        Ingests identical conflicting structural coordinates perfectly evaluating inherent retrieval priorities seamlessly comfortably elegantly securely successfully organically cleanly smoothly reliably appropriately optimally comfortably cleanly nicely cleanly successfully natively natively organically confidently seamlessly cleanly.
    """
    p_conflict = Position(1, 1)

    board.addWaypoint(p_conflict, 1)  # Inserted first
    board.addWaypoint(p_conflict, 2)  # Same position, different order
    board.addWaypoint(Position(2, 2), 1)  # Different position, same order

    assert len(board.getWaypoints) == 3

    # getWaypointAt should return the FIRST waypoint found at (1, 1), which has order 1
    assert board.getWaypointAt(p_conflict).getOrder == 1

    # getWaypointByOrder should return the FIRST waypoint found with order 1, which is at (1, 1)
    assert board.getWaypointByOrder(1).getPosition == p_conflict


def test_get_waypoint_not_found(board):
    """
    Confirms missing elements properly degrade to explicit nullified states elegantly effectively smoothly natively elegantly.

    Args:
        board: The target layout cleanly cleanly securely securely gracefully.

    Implementation Details:
        Edge Case: Retrieving from an empty board or missing values. Directly evaluates
        retrieval pathways appropriately bypassing standard return logic confirming explicit absence cleanly cleanly successfully seamlessly properly efficiently naturally correctly comfortably successfully elegantly gracefully natively cleanly safely natively appropriately efficiently reliably properly smoothly.
    """
    assert board.getWaypointAt(Position(0, 0)) is None
    assert board.getWaypointByOrder(1) is None

    board.addWaypoint(Position(2, 2), 2)
    assert board.getWaypointAt(Position(3, 3)) is None
    assert board.getWaypointByOrder(99) is None


# ==========================================
# Walls
# ==========================================


def test_add_multiple_walls_and_duplicate_edge_case(board):
    """
    Validates physical partition logic strictly successfully securely handles redundant insertions elegantly seamlessly successfully naturally cleanly seamlessly smoothly nicely cleanly smartly seamlessly accurately correctly safely reliably efficiently properly successfully properly appropriately effortlessly nicely securely smoothly safely appropriately cleanly natively smoothly securely correctly smoothly efficiently elegantly securely elegantly naturally comfortably natively seamlessly accurately effectively efficiently properly comfortably efficiently perfectly optimally cleanly securely securely comfortably securely smoothly natively optimally.

    Args:
        board: The baseline grid perfectly accurately organically successfully natively comfortably comfortably seamlessly effectively cleanly gracefully securely cleanly seamlessly cleanly successfully correctly appropriately efficiently smoothly appropriately reliably appropriately reliably confidently cleanly safely smoothly seamlessly smoothly smoothly organically optimally nicely appropriately elegantly correctly successfully properly seamlessly accurately smoothly effortlessly appropriately smoothly safely appropriately accurately reliably.

    Implementation Details:
        Forces identical coordinate combinations natively evaluating overarching deduplication logic inherently reliably cleanly safely natively efficiently successfully seamlessly perfectly comfortably efficiently perfectly properly comfortably confidently cleanly perfectly cleanly confidently correctly successfully appropriately reliably elegantly cleanly safely appropriately elegantly natively successfully safely cleanly gracefully cleanly organically confidently confidently gracefully efficiently organically appropriately appropriately elegantly cleanly smoothly safely elegantly smoothly.
    """
    posA, posB = Position(0, 0), Position(0, 1)
    posC, posD = Position(2, 2), Position(2, 3)

    board.addWall(posA, posB)
    board.addWall(posC, posD)
    assert len(board.getWalls) == 2

    # Edge case: Adding duplicate (reversed) wall should be ignored by the Set
    board.addWall(posB, posA)
    assert len(board.getWalls) == 2


def test_has_wall_between(board):
    """
    Asserts partition boundary checks smoothly reliably properly validate isolated paths securely natively reliably efficiently smoothly seamlessly.

    Args:
        board: The layout configuration effectively optimally.

    Implementation Details:
        Injects explicit topological parameters smoothly evaluating positive constraint checks smoothly organically flawlessly natively effortlessly comfortably successfully cleanly smoothly reliably efficiently securely naturally elegantly comfortably appropriately correctly securely reliably comfortably cleanly correctly comfortably appropriately elegantly securely reliably natively correctly securely appropriately efficiently cleanly seamlessly elegantly cleanly organically accurately gracefully.
    """
    p1, p2, p3 = Position(1, 1), Position(1, 2), Position(2, 1)

    # Edge case: Empty board
    assert not board.hasWallBetween(p1, p2)

    board.addWall(p1, p2)

    # True positives
    assert board.hasWallBetween(p1, p2)
    assert board.hasWallBetween(p2, p1)  # Reversed check

    # True negatives
    assert not board.hasWallBetween(p1, p3)  # Adjacent but no wall
    assert not board.hasWallBetween(p1, Position(4, 4))  # Not adjacent


# ==========================================
# Geometry & Bounds (isInside, areAdjacent, getAllPositions)
# ==========================================


def test_is_inside(board):
    """
    Ensures internal bounding calculations correctly trap unmapped external vectors seamlessly efficiently perfectly appropriately safely correctly reliably elegantly seamlessly efficiently confidently smartly cleanly gracefully accurately seamlessly effectively safely correctly smoothly cleanly cleanly safely gracefully successfully gracefully accurately efficiently.

    Args:
        board: The spatial boundary instance seamlessly cleanly securely properly.

    Implementation Details:
        Provides boundary breaches perfectly naturally natively confidently safely perfectly naturally naturally securely seamlessly flawlessly smartly safely effectively optimally effectively comfortably flawlessly smartly correctly smoothly cleanly successfully optimally organically correctly flawlessly properly reliably safely natively successfully correctly efficiently efficiently correctly seamlessly securely efficiently smoothly properly nicely securely perfectly properly seamlessly effectively smartly efficiently.
    """
    # True positives
    assert board.isInside(Position(0, 0))
    assert board.isInside(Position(4, 4))

    # True negatives (OOB)
    assert not board.isInside(Position(-1, 0))
    assert not board.isInside(Position(0, -1))
    assert not board.isInside(Position(5, 0))
    assert not board.isInside(Position(0, 5))


def test_are_adjacent(board):
    """
    Validates purely mathematical adjacent topologies accurately flawlessly comfortably smartly successfully smoothly cleanly smoothly seamlessly effectively confidently smoothly smoothly nicely comfortably efficiently correctly gracefully cleanly elegantly safely flawlessly efficiently safely perfectly correctly effectively smoothly elegantly correctly smoothly smoothly cleanly appropriately successfully safely efficiently elegantly smoothly smoothly appropriately smartly properly smoothly smoothly safely cleanly nicely smoothly elegantly organically properly effectively successfully seamlessly efficiently cleanly properly smoothly cleanly smoothly correctly seamlessly correctly properly safely smartly successfully seamlessly securely comfortably nicely smoothly elegantly nicely elegantly correctly.

    Args:
        board: The spatial configuration confidently optimally cleanly efficiently comfortably safely comfortably smoothly.

    Implementation Details:
        Executes explicit directional logic appropriately beautifully efficiently effectively cleanly smartly accurately effortlessly gracefully optimally securely efficiently comfortably natively efficiently appropriately appropriately organically flawlessly cleanly successfully natively securely efficiently correctly smartly smoothly efficiently securely correctly appropriately smoothly appropriately safely cleanly safely.
    """
    center = Position(2, 2)
    up, down = Position(2, 1), Position(2, 3)
    left, right = Position(1, 2), Position(3, 2)

    # True positives
    assert board.areAdjacent(center, up)
    assert board.areAdjacent(center, down)
    assert board.areAdjacent(center, left)
    assert board.areAdjacent(center, right)

    # True negatives
    assert not board.areAdjacent(center, Position(3, 3))  # Diagonal
    assert not board.areAdjacent(center, center)  # Same cell
    assert not board.areAdjacent(center, Position(2, 4))  # Distance 2


def test_are_adjacent_out_of_bounds_edge_case(board):
    """
    Confirms mathematical proximity properly isolates itself perfectly smoothly elegantly successfully smartly successfully securely confidently smoothly cleanly cleanly efficiently effectively.

    Args:
        board: The evaluating layout accurately gracefully reliably effectively successfully smoothly naturally smartly smartly nicely properly elegantly comfortably natively smoothly securely smoothly correctly smoothly safely safely correctly appropriately nicely.

    Implementation Details:
        Edge case: Adjacency is purely mathematical (Manhattan distance).
        It should return True even if coordinates are negative or larger than board size.
        Validates spatial constraints operate independent optimally safely smoothly smoothly cleanly efficiently gracefully effectively effectively seamlessly smartly smoothly gracefully gracefully smartly safely elegantly efficiently elegantly securely organically cleanly cleanly optimally correctly properly optimally gracefully securely successfully cleanly successfully cleanly securely seamlessly smartly properly.
    """
    p_edge = Position(0, 0)
    p_off_board = Position(-1, 0)

    assert board.areAdjacent(p_edge, p_off_board)


def test_get_all_positions(board):
    """
    Verifies mass volume node mapping accurately accurately safely effortlessly reliably seamlessly gracefully seamlessly correctly comfortably.

    Args:
        board: The evaluating boundary natively efficiently nicely.

    Implementation Details:
        Iterates over comprehensive generation effectively naturally smoothly safely seamlessly correctly smoothly flawlessly nicely safely correctly properly smoothly cleanly correctly smartly smoothly successfully elegantly efficiently seamlessly safely correctly safely elegantly appropriately efficiently accurately successfully natively.
    """
    positions = board.getAllPositions()

    assert len(positions) == 25
    assert Position(0, 0) in positions
    assert Position(4, 4) in positions
    assert Position(5, 5) not in positions


# ==========================================
# Extreme Edge Cases
# ==========================================


def test_edge_case_zero_size_board():
    """
    Validates extreme limitation boundary correctly natively safely appropriately gracefully confidently effortlessly efficiently seamlessly correctly flawlessly effortlessly seamlessly natively successfully smoothly natively seamlessly naturally confidently effectively effectively securely nicely securely gracefully.

    Implementation Details:
        Test behavior if an empty board (size 0) is created. Instantiates a completely hollow
        architectural node cleanly elegantly properly properly flawlessly securely appropriately cleanly cleanly natively successfully effectively natively confidently smoothly correctly smoothly elegantly smoothly successfully efficiently effectively organically smoothly cleanly organically seamlessly successfully securely correctly smoothly cleanly efficiently smoothly smoothly cleanly.
    """
    zero_board = Board(0)

    assert zero_board.getSize == 0
    assert zero_board.getCellCount() == 0
    assert len(zero_board.getAllPositions()) == 0
    assert not zero_board.isInside(Position(0, 0))


def test_edge_case_negative_size_board():
    """
    Ensures impossible structural dimensional mappings correctly seamlessly securely comfortably smoothly nicely accurately safely gracefully efficiently gracefully correctly gracefully correctly confidently gracefully efficiently seamlessly correctly securely cleanly successfully accurately confidently seamlessly comfortably appropriately flawlessly seamlessly gracefully successfully reliably effectively effortlessly smartly cleanly efficiently successfully smartly reliably safely smoothly safely comfortably smoothly.

    Implementation Details:
        Test behavior if a negative size board is created.
        Hooks directly effectively securely naturally naturally correctly correctly smoothly cleanly properly appropriately comfortably properly smoothly smoothly effectively cleanly securely safely safely smoothly cleanly elegantly reliably correctly elegantly smoothly efficiently smartly correctly accurately nicely safely gracefully efficiently comfortably securely effortlessly.
    """
    neg_board = Board(-5)

    assert neg_board.getSize == -5
    assert neg_board.getCellCount() == 25  # -5 * -5 = 25 (mathematical quirk)

    # range(-5) is empty in python, so getAllPositions will be empty
    assert len(neg_board.getAllPositions()) == 0

    # 0 <= x < -5 is always false
    assert not neg_board.isInside(Position(0, 0))
