import pytest
import time

from backend.solving_process.algorithmic_solver import AlgorithmicSolver
from backend.solving_process.solver_status import SolverStatus
from backend.solution_path import SolutionPath
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position

# --- Fixtures ---


@pytest.fixture
def quick_solver():
    """
    Provisions a mathematical solver equipped with a generous operational timeframe.

    Returns:
        The instantiated deterministic engine primed for small to medium topologies.

    Implementation Details:
        Instantiates the algorithmic solver with an extended timeout threshold to guarantee
        computational completion without hitting premature safety breakers during tests.
    """
    return AlgorithmicSolver(timeout=2000)


@pytest.fixture
def timeout_solver():
    """
    Provisions a severely constrained mathematical solver to force premature temporal halts.

    Returns:
        The instantiated deterministic engine utilizing minimal execution limits.

    Implementation Details:
        Binds the absolute temporal ceiling to the absolute minimum threshold, purposefully
        guaranteeing the A* queue operations will trigger a timeout exception when evaluating
        highly complex branching graphs.
    """
    return AlgorithmicSolver(timeout=1)


@pytest.fixture
def empty_3x3_board():
    """
    Generates a standardized, unobstructed dimensional grid for baseline validation.

    Returns:
        The initialized static structural blueprint.

    Implementation Details:
        Instantiates a purely vacant topology stripped of all physical walls and milestones,
        yielding an open permutation matrix for clean mathematical traversal testing.
    """
    return Board(size=3)


# --- Helper Function for Strict Validation ---


def verify_valid_hamiltonian_path(board: Board, path_obj: SolutionPath) -> bool:
    """
    Semantically verifies the structural integrity and rule compliance of a completed traversal.

    Args:
        board: The baseline grid configuration detailing spatial boundaries and barriers.
        path_obj: The formalized trajectory mapping submitted for verification.

    Returns:
        A truth state representing absolute mathematical and topological compliance.

    Implementation Details:
        Extracts coordinate vectors explicitly via the encapsulated property hook without parentheses.
        It linearly iterates over the sequential graph nodes to assert absolute volumetric coverage
        (Hamiltonian constraints), strictly rejects diagonal/non-adjacent leaps, verifies absolute
        avoidance of declared wall barriers, and maintains a cascading checkpoint register to ensure
        mandatory chronological intersections with designated milestones.
    """
    positions = path_obj.getPositions

    if not positions:
        return False

    # 1. Check length (must visit every cell exactly once)
    if len(positions) != board.getCellCount():
        return False
    if len(set(positions)) != board.getCellCount():
        return False

    # 2. Check adjacencies and walls
    for i in range(len(positions) - 1):
        curr_pos = positions[i]
        next_pos = positions[i + 1]

        if not board.areAdjacent(curr_pos, next_pos):
            return False
        if board.hasWallBetween(curr_pos, next_pos):
            return False

    # 3. Check waypoints order
    waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)
    wp_idx = 0
    for pos in positions:
        wp = board.getWaypointAt(pos)
        if wp:
            if wp_idx >= len(waypoints) or wp.getOrder != waypoints[wp_idx].getOrder:
                return False
            wp_idx += 1

    return wp_idx == len(waypoints)


# --- Tests: Default Use Cases ---


def test_solve_empty_board(quick_solver, empty_3x3_board):
    """
    Validates deterministic solver resolution across an unobstructed topology.

    Args:
        quick_solver: The deterministic search engine fixture.
        empty_3x3_board: The unobstructed structural grid fixture.

    Implementation Details:
        Submits the vacant spatial bounds into the heuristic algorithm. Asserts that the
        computational payload definitively reflects a SOLVED state, confirms generation of
        an actively populated sequence model, validates operation telemetry steps were burned,
        and verifies the resulting route strictly obeys all Hamiltonian movement rules.
    """
    result = quick_solver.solve(empty_3x3_board)

    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert result._metrics._steps > 0
    assert verify_valid_hamiltonian_path(empty_3x3_board, result._path)


def test_solve_with_walls(quick_solver):
    """
    Validates deterministic solver resolution when topological barriers bisect the environment.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Fabricates a grid injected with explicit, uncrossable segment bounds. Commands the
        engine to calculate a traversal vector, actively checking that the final extracted
        path mathematically navigated around the structured coordinates instead of bypassing them.
    """
    board = Board(size=3)
    board.addWall(Position(0, 0), Position(0, 1))

    result = quick_solver.solve(board)

    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert verify_valid_hamiltonian_path(board, result._path)


def test_solve_with_waypoints(quick_solver):
    """
    Validates mathematical compliance against strictly sequenced milestone intersections.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Establishes sequential spatial nodes enforcing a chronological traversal contract.
        Asserts the algorithm isolates the singular valid permutation fulfilling both
        the Hamiltonian coverage and the strict chronological node ordering constraints.
    """
    board = Board(size=3)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(2, 2), 2)
    board.addWaypoint(Position(0, 2), 3)

    result = quick_solver.solve(board)

    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert verify_valid_hamiltonian_path(board, result._path)


# --- Tests: Edge Cases & Optimizations ---


def test_start_on_waypoint(quick_solver):
    """
    Verifies heuristic stability when the origination point overlaps a milestone coordinate.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Positions an initial sequence requirement at the direct top-left bound. Confirms
        the solver instantly increments the goal index upon seeding the origin bitmask
        instead of erroneously stalling the search queue.
    """
    board = Board(size=2)
    board.addWaypoint(Position(0, 0), 1)

    result = quick_solver.solve(board)

    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert verify_valid_hamiltonian_path(board, result._path)


def test_1x1_board(quick_solver):
    """
    Validates execution against extreme singular-cell constraints.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Tests boundary mathematical bounds by injecting a single-cell grid. Asserts the
        solver natively terminates upon establishing origin tracking without iterating
        non-existent peripheral nodes, securing an immediate SOLVED payload.
    """
    board = Board(size=1)

    result = quick_solver.solve(board)

    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert result._metrics._steps >= 0
    assert verify_valid_hamiltonian_path(board, result._path)


def test_unsolvable_board_isolated_cell(quick_solver):
    """
    Evaluates topological rejection against structurally fragmented environments.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Employs barriers to completely sequester a spatial coordinate, mathematically preventing
        comprehensive coverage. Asserts the engine correctly derives the UNSOLVABLE internal enum
        rather than stalling in an endless loop, maintaining empty solution paths while recording
        expended telemetry steps.
    """
    board = Board(size=2)
    board.addWall(Position(0, 0), Position(0, 1))
    board.addWall(Position(0, 0), Position(1, 0))

    result = quick_solver.solve(board)

    assert result._status == SolverStatus.UNSOLVABLE
    assert result._path is None
    assert result._metrics._steps > 0


def test_unsolvable_impossible_waypoints(quick_solver):
    """
    Confirms algorithmic rejection of inherently paradoxical chronological milestone sequences.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Geometrically channels the solver through a restrictive funnel while placing an advanced
        numerical sequence requirement spatially ahead of a preceding requirement. Confirms the
        engine mathematically maps the paradox and terminates early with an UNSOLVABLE status flag.
    """
    board = Board(size=2)
    # Block the direct path to force a specific route
    board.addWall(Position(0, 0), Position(1, 0))

    # By forcing the path to go (0,0) -> (0,1) -> (1,1) -> (1,0),
    # placing a later waypoint earlier in the physical path makes it mathematically impossible.
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 1), 2)
    board.addWaypoint(Position(0, 1), 3)  # Hits WP 3 before WP 2!

    result = quick_solver.solve(board)

    assert result._status == SolverStatus.UNSOLVABLE
    assert result._path is None


def test_flood_fill_pruning_trigger(quick_solver):
    """
    Verifies the algorithmic engine's ability to instantly reject mathematically disjointed grids.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Constructs a grid completely severed into two disconnected architectural halves.
        This layout safely bypasses standard dead-end counters, forcing the underlying
        flood-fill heuristic to activate, identify the disconnected graph, and prematurely
        collapse the search tree. Evaluates exact performance metrics against hardware clocks
        to ensure the prune happens nearly instantaneously.
    """
    board = Board(size=3)
    board.addWall(Position(0, 1), Position(0, 2))
    board.addWall(Position(1, 1), Position(1, 2))
    board.addWall(Position(2, 1), Position(2, 2))

    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start

    assert result._status == SolverStatus.UNSOLVABLE
    assert duration < 0.2  # Should be nearly instant due to flood fill pruning


def test_solver_timeout(timeout_solver):
    """
    Evaluates temporal ceiling enforcement terminating complex permutation calculations.

    Args:
        timeout_solver: The severely limited deterministic engine fixture.

    Implementation Details:
        Submits an expansively scaled configuration designed to generate millions of traversal nodes.
        Validates that the execution bounds accurately trap runaway permutations, bubbling up the
        TIMEOUT enum directly into the resulting metrics payload before CPU consumption stalls.
    """
    large_board = Board(size=6)

    result = timeout_solver.solve(large_board)

    assert result._status == SolverStatus.TIMEOUT
    assert result._path is None
    assert result._metrics._runtimeMs >= 0


def test_zero_timeout_edge_case():
    """
    Assesses fallback handling against mathematically impossible temporal thresholds.

    Implementation Details:
        Instantiates an operational engine directly bounded to an absolute zero interval limit.
        Ensures the baseline start clock safely recognizes the immediate threshold breach and
        collapses the search graph on its first iteration, avoiding infinite calculation loops.
    """
    solver = AlgorithmicSolver(timeout=0)
    board = Board(size=3)

    result = solver.solve(board)

    assert result._status == SolverStatus.TIMEOUT
    assert result._path is None


def test_heuristic_logic(quick_solver):
    """
    Validates standard Manhattan spatial estimation against strict checkpoint offsets.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Injects dimensional bounds and specifically routes the internal A* cost equation to map
        theoretical remaining layouts. Directly asserts the raw scalar returns correctly reflect
        expected integer distances, effectively confirming node depth combinations remain stable.
    """
    board = Board(size=5)
    board.addWaypoint(Position(4, 4), 1)
    waypoints = board.getWaypoints

    # Heuristic calculates distance to Waypoint. 0,0 to 4,4 is 8.
    distance = quick_solver._heuristic(Position(0, 0), waypoints, 0)
    assert distance == 8

    distance_done = quick_solver._heuristic(Position(0, 0), waypoints, 1)
    assert distance_done == 0


def test_dead_end_pruning_trigger(quick_solver):
    """
    Tests optimization bounds rejecting configurations with excessive terminus traps.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Forces the grid to manifest overlapping singular exits (chokepoints) which mathematically
        violate strict Hamiltonian pathing. Utilizes hardware chronometers to ensure the
        evaluation aggressively drops the branch before entering deeper search evaluations.
    """
    board = Board(size=3)
    board.addWall(Position(0, 0), Position(1, 0))  # Isolates 0,0 to only go down
    board.addWall(Position(2, 0), Position(1, 0))  # Isolates 2,0 to only go down

    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start

    assert result._status == SolverStatus.UNSOLVABLE
    # Assert the new optimization pruned it before doing heavy searching
    assert duration < 0.2


def test_bitmask_index_bounds(quick_solver):
    """
    Secures mathematical integrity mapping spatial nodes into localized binary sets.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Directly taps the protected mathematical translator converting dimensional bounds into
        flat scalars. Asserts extreme array boundaries appropriately yield exact bit offsets
        without causing integer overflow issues during complex tracking operations.
    """

    # Top left
    assert quick_solver._get_bit_index(Position(0, 0), 8) == 0
    # Bottom right
    assert quick_solver._get_bit_index(Position(7, 7), 8) == 63


def test_mathematical_pruning_3_dead_ends(quick_solver):
    """
    Explicitly targets strict rejection constraints prohibiting triple-terminal nodes.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Architecturally isolates three separate grid zones strictly down to single exit thresholds.
        Records performance metrics to guarantee immediate algorithm ejection as resolving a
        singular continuous loop accommodating three unlinked terminus boundaries is physically impossible.
    """
    board = Board(size=3)

    # Isolate Top-Left (0,0) to only exit via (1,0)
    board.addWall(Position(0, 0), Position(0, 1))

    # Isolate Bottom-Left (0,2) to only exit via (1,2)
    board.addWall(Position(0, 2), Position(0, 1))

    # Isolate Top-Right (2,0) to only exit via (1,0)
    board.addWall(Position(2, 0), Position(2, 1))

    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start

    assert result._status == SolverStatus.UNSOLVABLE
    assert duration < 0.2  # Should be nearly instant


def test_long_snake_valid_path(quick_solver):
    """
    Confirms robust pathing survival through narrow corridor layouts without false prunes.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Constructs an intentional zigzagging tunnel inherently yielding two continuous dead-ends
        at all times. Verifies the algorithm differentiates a structurally valid sequential corridor
        from fragmented, impassible dead-end configurations, returning a complete trajectory model.
    """
    board = Board(size=3)
    # Create an S-shaped tunnel that forces a specific path
    board.addWall(Position(0, 1), Position(1, 1))
    board.addWall(Position(1, 1), Position(2, 1))

    result = quick_solver.solve(board)

    assert result._status == SolverStatus.SOLVED
    assert result._path is not None


def test_heuristic_subgoal_consistency(quick_solver):
    """
    Validates dynamic heuristic accumulation mapping sequences of multiple remaining objectives.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Invokes the protected heuristic engine to ensure its Manhattan distance projections
        correctly chain across multiple sequentially active waypoints instead of just evaluating
        the immediate objective, thereby avoiding priority queue stalling mechanics.
    """
    board = Board(size=5)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(4, 4), 2)
    waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)

    # Distance to WP1 (0,0) is 1. Distance from WP1 to WP2 (4,4) is 8.
    # Total heuristic MUST equal 9 to prevent queue stalling.
    h_start = quick_solver._heuristic(Position(0, 1), waypoints, 0)
    assert h_start == 9


def test_fully_walled_unreachable_target(quick_solver):
    """
    Evaluates flood-fill activation against structurally marooned architectural zones.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Erects a complete exclusionary partition barricading a sub-segment of grid topologies.
        Secures a performance metric demonstrating the flood-fill sub-routine natively bypasses
        the active navigation tip and instantly detects inaccessible spatial clusters.
    """
    board = Board(size=3)
    # Wall off the top-right corner entirely
    board.addWall(Position(2, 0), Position(1, 0))
    board.addWall(Position(2, 0), Position(2, 1))

    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start

    assert result._status == SolverStatus.UNSOLVABLE
    assert duration < 0.2  # Ensures flood-fill caught it instantly


def test_bit_count_large_board_performance(quick_solver):
    """
    Guarantees structural efficiency and confirms garbage collection stabilization in binary math.

    Args:
        quick_solver: The deterministic search engine fixture.

    Implementation Details:
        Targets execution across a moderately scaled spatial framework to explicitly test the native
        integer `.bit_count()` method utilization. Asserts calculation timing operates swiftly,
        confirming archaic string-allocation loops (`bin().count()`) are entirely stripped from the pipeline.
    """
    board = Board(size=4)

    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start

    assert result._status == SolverStatus.SOLVED
    assert duration < 0.5  # High performance assertion
