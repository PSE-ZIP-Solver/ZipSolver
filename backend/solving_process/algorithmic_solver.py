import time
import heapq
from dataclasses import dataclass, field
from typing import List, Tuple, FrozenSet, Optional, Iterator

from solver import Solver, SolverStatus
from solver_result import SolverResult
from solver_metrics import SolverMetrics
from backend.solution_path import SolutionPath
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position, Waypoint


@dataclass(order=True)
class SearchNode:
    """
    Represents a single state in the A* search tree.
    
    This dataclass is heavily optimized for use in Python's `heapq`. 
    By explicitly defining `compare=False` on the complex fields (pos, visited, path, next_idx),
    we guarantee that the heap only sorts based on the numerical scores (f_score, neg_depth, counter).
    This prevents crashes when two states have the same score but cannot naturally be compared.
    """
    f_score: int
    neg_depth: int
    counter: int  # Tie-breaker to ensure stable sorting when scores are identical
    
    # Fields below are ignored by the sorting algorithm
    pos: Position = field(compare=False)
    visited: FrozenSet[Position] = field(compare=False)
    path: Tuple[Position, ...] = field(compare=False)
    next_idx: int = field(compare=False)


class AlgorithmicSolver(Solver):
    """
    A deterministic fallback solver that uses a highly optimized A* (Best-First) search 
    to find a Hamiltonian path on a given board. It includes advanced flood-fill pruning 
    to handle larger grid sizes (e.g., 6x6 to 8x8) without running out of memory.
    """

    def __init__(self, timeout: int):
        """
        Initializes the AlgorithmicSolver.
        
        Args:
            timeout (int): The maximum allowed runtime in milliseconds before aborting the search.
        """
        self._timeout = timeout

    def _heuristic(self, current: Position, waypoints: List[Waypoint], next_wp_idx: int) -> int:
        """
        Calculates the heuristic (h-score) for the A* search.
        
        Uses the Manhattan distance from the current position to the next required waypoint.
        This guides the search algorithm toward the necessary targets rather than wandering blindly.

        Args:
            current (Position): The current cell the algorithm is exploring.
            waypoints (List[Waypoint]): The sorted list of waypoints on the board.
            next_wp_idx (int): The index of the next waypoint that must be visited.

        Returns:
            int: The Manhattan distance to the next waypoint, or 0 if all waypoints are visited.
        """
        if next_wp_idx < len(waypoints):
            target_pos = waypoints[next_wp_idx].getPosition
            return abs(current.getX - target_pos.getX) + abs(current.getY - target_pos.getY)
        return 0

    def _get_valid_neighbors(self, pos: Position, board: Board) -> Iterator[Position]:
        """
        Yields all valid, adjacent positions from a given cell.
        A position is valid if it is inside the board boundaries and not blocked by a wall.
        """
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            n_pos = Position(pos.getX + dx, pos.getY + dy)
            if board.isInside(n_pos) and not board.hasWallBetween(pos, n_pos):
                yield n_pos

    def _is_viable_state(self, current_pos: Position, visited: FrozenSet[Position], board: Board, total_cells: int) -> bool:
        """
        Executes a Flood-Fill (BFS) to detect choke points and unreachable cells.
        
        Because we need a Hamiltonian path (visiting every cell exactly once), all remaining 
        unvisited cells MUST form a single connected group. If the current move splits the 
        board into disconnected "islands", the puzzle becomes mathematically unsolvable from 
        this state. Pruning these states instantly saves millions of pointless calculations.

        Args:
            current_pos (Position): The cell the algorithm just moved to.
            visited (FrozenSet[Position]): The set of all cells visited so far.
            board (Board): The game board.
            total_cells (int): Total number of cells on the board.

        Returns:
            bool: True if the state is viable, False if it leads to a dead-end.
        """
        unvisited_count = total_cells - len(visited)
        if unvisited_count == 0:
            return True  # Board is fully solved, state is highly viable!

        # 1. Find any valid, unvisited neighbor to act as the starting point for the flood fill
        start_node = None
        for n_pos in self._get_valid_neighbors(current_pos, board):
            if n_pos not in visited:
                start_node = n_pos
                break
        
        # Dead-end trigger: We haven't visited every cell, but there are no legal exits from here.
        if not start_node:
            return False 

        # 2. Perform a Breadth-First Search (BFS) to count how many unvisited cells are reachable
        queue = [start_node]
        reachable = {start_node}
        
        while queue:
            curr = queue.pop(0)
            for neighbor in self._get_valid_neighbors(curr, board):
                if neighbor not in visited and neighbor not in reachable:
                    reachable.add(neighbor)
                    queue.append(neighbor)

        # 3. If the reachable count matches the total unvisited count, the board is not fractured.
        return len(reachable) == unvisited_count

    def _a_star(self, board: Board) -> Tuple[Optional[SolutionPath], int]:
        """
        Executes the core algorithmic search for the puzzle.

        Returns:
            Tuple[Optional[SolutionPath], int]: A tuple containing the valid SolutionPath (if found), 
                                                and the total number of steps/nodes explored.
        """
        # time.perf_counter() is used instead of time.time() for high-precision, monotonic benchmarking
        start_time = time.perf_counter()
        timeout_sec = self._timeout / 1000.0
        steps = 0

        # Sort waypoints by order so we know exactly which one to aim for next
        waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)
        total_cells = board.getCellCount()

        pq: List[SearchNode] = []
        counter = 0

        # Enqueue initial states: try starting from every cell on the board
        for start_pos in board.getAllPositions():
            next_idx = 0
            wp = board.getWaypointAt(start_pos)
            
            # If we spawn directly on a waypoint, ensure it is the FIRST required waypoint
            if wp:
                if len(waypoints) > 0 and wp.getOrder != waypoints[0].getOrder:
                    continue 
                next_idx = 1
            
            # Use frozenset and tuple to massively reduce memory footprint during A* expansion
            visited = frozenset([start_pos])
            path = (start_pos,)
            depth = 1 
            h = self._heuristic(start_pos, waypoints, next_idx)
            
            # We want to find the LONGEST path (visiting everything). 
            # By negating depth (-g), we force the priority queue to pop deeper nodes first,
            # effectively turning A* into a memory-efficient Heuristic-Guided DFS.
            g = -depth 
            f = g + h
            
            heapq.heappush(pq, SearchNode(f, g, counter, start_pos, visited, path, next_idx))
            counter += 1

        # Tracks previously visited exact states to prevent calculating loops/duplicates
        closed_set = set()

        # Main Search Loop
        while pq:
            # Enforce the timeout limit
            if time.perf_counter() - start_time > timeout_sec:
                break
                
            steps += 1
            current_node = heapq.heappop(pq)
            
            # Check Win Condition: All cells visited AND all waypoints collected
            if len(current_node.visited) == total_cells:
                if current_node.next_idx == len(waypoints):
                    # Convert the tuple back into the required SolutionPath object
                    sol_path = SolutionPath()
                    for p in current_node.path:
                        sol_path.add(p)
                    return sol_path, steps

            # State Deduplication: State is defined by (position, visited_cells, waypoint_progress)
            state_key = (current_node.pos, current_node.visited, current_node.next_idx)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            # Generate neighbors
            for n_pos in self._get_valid_neighbors(current_node.pos, board):
                # Don't step on cells we've already visited in this specific path sequence
                if n_pos in current_node.visited:
                    continue
                
                # Check waypoint constraints
                n_idx = current_node.next_idx
                wp = board.getWaypointAt(n_pos)
                if wp:
                    # If it's a waypoint, it MUST match the order of the one we are currently looking for
                    if n_idx >= len(waypoints) or wp.getOrder != waypoints[n_idx].getOrder:
                        continue 
                    n_idx += 1
                    
                # Create new path/visited objects quickly using union and concatenation
                n_visited = current_node.visited | frozenset([n_pos])
                
                # Apply advanced flood-fill pruning to avoid mathematical dead-ends
                if not self._is_viable_state(n_pos, n_visited, board, total_cells):
                    continue

                n_path = current_node.path + (n_pos,)
                n_depth = len(n_path)
                n_h = self._heuristic(n_pos, waypoints, n_idx)
                n_f = -n_depth + n_h
                
                heapq.heappush(pq, SearchNode(n_f, -n_depth, counter, n_pos, n_visited, n_path, n_idx))
                counter += 1

        # Return None if the queue empties without finding a solution (Unsolvable)
        # or if the timeout breaks the loop.
        return None, steps

    def solve(self, board: Board) -> SolverResult:
        """
        Coordinates the solving process and formats the final result.

        Args:
            board (Board): The puzzle board to be solved.

        Returns:
            SolverResult: The structured outcome containing status, path, and metrics.
        """
        start_time = time.perf_counter()
        
        # Execute the core algorithm
        path, steps = self._a_star(board)
        
        # Calculate runtime in milliseconds for the metrics
        runtime_ms = int((time.perf_counter() - start_time) * 1000)
        metrics = SolverMetrics(runtimeMs=runtime_ms, steps=steps, attempts=1)
        
        # Structure the final response based on the search outcome
        if path:
            return SolverResult(
                status=SolverStatus.SOLVED,
                path=path,
                message="Successfully found a path using an optimized A* search.",
                metrics=metrics
            )
        elif runtime_ms >= self._timeout:
            return SolverResult(
                status=SolverStatus.TIMEOUT,
                path=None,
                message="Algorithmic search timed out.",
                metrics=metrics
            )
        else:
            return SolverResult(
                status=SolverStatus.UNSOLVABLE,
                path=None,
                message="No valid solution exists for this board.",
                metrics=metrics
            )