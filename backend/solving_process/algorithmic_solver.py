import time
import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

from .solver import Solver
from .solver_result import SolverResult
from .solver_status import SolverStatus
from .solver_metrics import SolverMetrics
from backend.solution_path import SolutionPath
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position, Waypoint


@dataclass(order=True)
class SearchNode:
    f_score: int
    neg_depth: int
    counter: int
    pos: Position = field(compare=False)
    visited_mask: int = field(compare=False)
    next_idx: int = field(compare=False)
    parent: Optional['SearchNode'] = field(compare=False, default=None)


class AlgorithmicSolver(Solver):
    """A* search for the Zip puzzle.

    A Zip solution is a Hamiltonian path over every cell that starts at waypoint 1, ends
    at the highest-numbered waypoint, takes the waypoints in ascending order, and never
    crosses a wall.

    Because every complete solution has the same length (one visit per cell), the search
    is a satisfaction problem rather than a cost-minimisation one. The evaluation
    function therefore uses ``f = g + h`` with ``g = -depth`` — deeper states are nearer
    to a complete board and are expanded first — and ``h`` = Manhattan distance to the
    next waypoint due, which breaks ties towards the waypoint that must be reached next.

    Three defects in the previous version made it reject every valid board:

    * ``_is_viable_state`` counted only unvisited-to-unvisited edges. The last remaining
      cell is reachable solely from the head, which is already visited, so it always
      appeared to have zero exits and every path was pruned one move from completion.
      The head is now part of the induced graph.
    * The frontier was seeded from every cell on the board rather than from waypoint 1.
    * Completion did not require finishing on the final waypoint, so the search returned
      paths that ``SolutionValidator`` then rejected.
    """

    def __init__(self, timeout: int):
        # Milliseconds, matching DFS_TIMEOUT_MS in SolverController.
        self._timeout = timeout

    def _get_bit_index(self, pos: Position, board_size: int) -> int:
        return pos.getY * board_size + pos.getX

    def _heuristic(self, current: Position, waypoints: List[Waypoint], next_wp_idx: int) -> int:
        if next_wp_idx < len(waypoints):
            target_pos = waypoints[next_wp_idx].getPosition
            return abs(current.getX - target_pos.getX) + abs(current.getY - target_pos.getY)
        return 0

    def _parity_ok(
        self,
        visited_mask: int,
        head: Position,
        target: Position,
        board_size: int,
        total_cells: int,
    ) -> bool:
        """Bipartite feasibility check.

        A grid is two-colourable by ``(x + y) % 2`` and a path alternates colours on every
        step. The walk still to come covers ``{head} + unvisited`` and must finish on the
        target, which fixes both the colour balance and the target's colour. Mismatches
        can never be recovered, and the test is a couple of popcounts.
        """
        remaining = total_cells - bin(visited_mask).count("1") + 1  # + head
        count = [0, 0]
        for y in range(board_size):
            for x in range(board_size):
                if (visited_mask >> (y * board_size + x)) & 1 == 0:
                    count[(x + y) & 1] += 1
        head_colour = (head.getX + head.getY) & 1
        count[head_colour] += 1  # the head is visited but is part of the remaining walk

        target_colour = (target.getX + target.getY) & 1
        if target_colour != (head_colour ^ ((remaining - 1) & 1)):
            return False
        return count[head_colour] == (remaining + 1) // 2 and count[1 - head_colour] == remaining // 2

    def _is_viable_state(
        self,
        visited_mask: int,
        head: Position,
        target: Position,
        board_size: int,
        total_cells: int,
        adj_list: Dict[Position, List[Position]],
    ) -> bool:
        """Degree and connectivity feasibility for the remainder of the path.

        Considers the graph induced by ``{head} + unvisited``. Every unvisited cell other
        than the target must be entered and left, so it needs degree >= 2; the target is
        entered only, so it needs degree >= 1. All unvisited cells must additionally be
        reachable from the head — otherwise the path has stranded a region.
        """
        head_idx = self._get_bit_index(head, board_size)
        start_node = None

        for y in range(board_size):
            for x in range(board_size):
                p = Position(x, y)
                bit_idx = self._get_bit_index(p, board_size)
                if (visited_mask >> bit_idx) & 1:
                    continue

                if start_node is None:
                    start_node = p

                # Count exits within {head} + unvisited — crediting the head is the fix.
                exits = 0
                for n in adj_list[p]:
                    n_idx = self._get_bit_index(n, board_size)
                    if (visited_mask >> n_idx) & 1 == 0 or n_idx == head_idx:
                        exits += 1

                if p == target:
                    if exits < 1:
                        return False
                elif exits < 2:
                    return False

        if start_node is None:
            return True

        # Connectivity: flood-fill outward from the head across unvisited cells.
        reachable_mask = 0
        queue = deque()
        for n in adj_list[head]:
            n_idx = self._get_bit_index(n, board_size)
            if (visited_mask >> n_idx) & 1 == 0:
                reachable_mask |= 1 << n_idx
                queue.append(n)

        reachable_count = bin(reachable_mask).count("1")
        while queue:
            curr = queue.popleft()
            for neighbor in adj_list[curr]:
                n_idx = self._get_bit_index(neighbor, board_size)
                if (visited_mask >> n_idx) & 1 == 0 and (reachable_mask >> n_idx) & 1 == 0:
                    reachable_mask |= 1 << n_idx
                    reachable_count += 1
                    queue.append(neighbor)

        expected_unvisited = total_cells - bin(visited_mask).count("1")
        return reachable_count == expected_unvisited

    def _reconstruct_path(self, end_node: SearchNode) -> SolutionPath:
        positions = []
        curr = end_node
        while curr:
            positions.append(curr.pos)
            curr = curr.parent

        positions.reverse()

        sol_path = SolutionPath()
        for p in positions:
            sol_path.add(p)
        return sol_path

    def _a_star(self, board: Board) -> Tuple[Optional[SolutionPath], int, bool]:
        start_time = time.perf_counter()
        timeout_sec = self._timeout / 1000.0
        steps = 0
        timed_out = False

        board_size = board.getSize
        total_cells = board.getCellCount()
        waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)
        if len(waypoints) < 2:
            return None, 0, False

        # --- PRECOMPUTATION ---
        waypoint_map = {wp.getPosition: wp for wp in waypoints}

        adj_list: Dict[Position, List[Position]] = {}
        for y in range(board_size):
            for x in range(board_size):
                p = Position(x, y)
                neighbors = []
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    n_pos = Position(x + dx, y + dy)
                    if board.isInside(n_pos) and not board.hasWallBetween(p, n_pos):
                        neighbors.append(n_pos)
                adj_list[p] = neighbors
        # ----------------------

        start_pos = waypoints[0].getPosition
        target_pos = waypoints[-1].getPosition
        target_mask = (1 << total_cells) - 1

        pq: List[SearchNode] = []
        counter = 0

        # The path must begin at waypoint 1 — seeding every cell was defect #2.
        visited_mask = 1 << self._get_bit_index(start_pos, board_size)
        h = self._heuristic(start_pos, waypoints, 1)
        heapq.heappush(pq, SearchNode(-1 + h, -1, counter, start_pos, visited_mask, 1, None))
        counter += 1

        closed_set = set()

        while pq:
            if time.perf_counter() - start_time > timeout_sec:
                timed_out = True
                break

            steps += 1
            current_node = heapq.heappop(pq)

            if current_node.visited_mask == target_mask:
                # Complete only when every waypoint is consumed AND the walk ends on the
                # final waypoint — the endpoint rule was defect #3.
                if current_node.next_idx == len(waypoints) and current_node.pos == target_pos:
                    return self._reconstruct_path(current_node), steps, False
                continue

            state_key = (current_node.pos, current_node.visited_mask, current_node.next_idx)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            for n_pos in adj_list[current_node.pos]:
                n_idx_bit = self._get_bit_index(n_pos, board_size)

                if (current_node.visited_mask >> n_idx_bit) & 1:
                    continue

                n_idx = current_node.next_idx
                wp = waypoint_map.get(n_pos)
                if wp:
                    if n_idx >= len(waypoints) or wp.getOrder != waypoints[n_idx].getOrder:
                        continue
                    n_idx += 1

                n_mask = current_node.visited_mask | (1 << n_idx_bit)

                # The final waypoint terminates the path, so it is only enterable when it
                # is the last unvisited cell.
                if n_pos == target_pos and n_mask != target_mask:
                    continue

                if n_mask != target_mask:
                    if not self._parity_ok(n_mask, n_pos, target_pos, board_size, total_cells):
                        continue
                    if not self._is_viable_state(
                        n_mask, n_pos, target_pos, board_size, total_cells, adj_list
                    ):
                        continue

                n_depth = -current_node.neg_depth + 1
                n_h = self._heuristic(n_pos, waypoints, n_idx)
                n_f = -n_depth + n_h

                heapq.heappush(
                    pq, SearchNode(n_f, -n_depth, counter, n_pos, n_mask, n_idx, current_node)
                )
                counter += 1

        return None, steps, timed_out

    def solve(self, board: Board) -> SolverResult:
        start_time = time.perf_counter()
        path, steps, timed_out = self._a_star(board)
        runtime_ms = int((time.perf_counter() - start_time) * 1000)
        metrics = SolverMetrics(runtimeMs=runtime_ms, steps=steps, attempts=1)

        if path:
            return SolverResult(
                status=SolverStatus.SOLVED, path=path,
                message="Successfully found a path using A* search.", metrics=metrics
            )
        if timed_out:
            return SolverResult(
                status=SolverStatus.TIMEOUT, path=None,
                message="Algorithmic search timed out.", metrics=metrics
            )
        return SolverResult(
            status=SolverStatus.UNSOLVABLE, path=None,
            message="No valid solution exists for this board.", metrics=metrics
        )