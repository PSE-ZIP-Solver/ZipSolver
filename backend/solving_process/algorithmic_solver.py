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
    def __init__(self, timeout: int):
        self._timeout = timeout

    def _get_bit_index(self, pos: Position, board_size: int) -> int:
        return pos.getY * board_size + pos.getX

    def _heuristic(self, current: Position, waypoints: List[Waypoint], next_wp_idx: int) -> int:
        if next_wp_idx < len(waypoints):
            # 1. Distance to the immediate next waypoint
            target_pos = waypoints[next_wp_idx].getPosition
            h = abs(current.getX - target_pos.getX) + abs(current.getY - target_pos.getY)
            
            # [CRITICAL FIX]: Add Manhattan distances of all subsequent waypoints.
            # This prevents the f-score from suddenly spiking when reaching a subgoal,
            # which would cause the Priority Queue to abandon the correct path.
            for i in range(next_wp_idx, len(waypoints) - 1):
                p1 = waypoints[i].getPosition
                p2 = waypoints[i+1].getPosition
                h += abs(p1.getX - p2.getX) + abs(p1.getY - p2.getY)
                
            return h
        return 0
    
    def _is_viable_state(self, visited_mask: int, board_size: int, total_cells: int, adj_list: Dict[Position, List[Position]], head: Optional[Position] = None, final_wp_pos: Optional[Position] = None) -> bool:
        """
        Optimized Flood-Fill and Dead-End Detection using O(1) Adjacency Lookups.

        Also applies a checkerboard-parity prune: on a bipartite grid every step flips
        colour, so the remaining unvisited cells must split into the two colours in a way
        the head can actually traverse to the final waypoint. When they can't, the branch is
        dead no matter how the search continues — a very cheap, high-yield cut for open
        boards where the flood-fill alone leaves too many live branches.
        """
        # [CRITICAL FIX]: Use native C-level bit_count() instead of bin().count()
        # Eliminates massive string-allocation garbage collection overhead in the A* loop.
        expected_unvisited = total_cells - visited_mask.bit_count()
        
        if expected_unvisited == 0:
            return True

        # PARITY PRUNE. The remaining unvisited cells (the head is already in visited_mask)
        # must be traversable as one alternating-colour walk that starts adjacent to the
        # head and ends on the final waypoint. On a checkerboard that fixes both the colour
        # counts and the colour of the last cell; any mismatch means the branch is dead.
        if head is not None and final_wp_pos is not None:
            remaining_even = 0
            remaining_odd = 0
            for p in adj_list:
                if (visited_mask & (1 << self._get_bit_index(p, board_size))) == 0:
                    if (p.getX + p.getY) & 1:
                        remaining_odd += 1
                    else:
                        remaining_even += 1
            r_total = remaining_even + remaining_odd
            if r_total > 0:
                head_color = (head.getX + head.getY) & 1
                first_color = 1 - head_color          # next step flips colour
                need_first = (r_total + 1) // 2
                need_other = r_total // 2
                need_even = need_first if first_color == 0 else need_other
                need_odd = need_first if first_color == 1 else need_other
                last_color = (first_color + (r_total - 1)) & 1
                final_color = (final_wp_pos.getX + final_wp_pos.getY) & 1
                if (
                    remaining_even != need_even
                    or remaining_odd != need_odd
                    or last_color != final_color
                ):
                    return False

        start_node = None
        dead_end_count = 0
        
        for p, neighbors in adj_list.items():
            bit_idx = self._get_bit_index(p, board_size)
            
            if (visited_mask & (1 << bit_idx)) == 0:
                if not start_node:
                    start_node = p
                    
                exits = 0
                for n in neighbors:
                    if (visited_mask & (1 << self._get_bit_index(n, board_size))) == 0:
                        exits += 1
                        
                if exits == 0 and expected_unvisited > 1:
                    return False
                
                if exits == 1:
                    dead_end_count += 1

        if not start_node:
            return True
            
        if dead_end_count > 2:
            return False

        queue = deque([start_node])
        reachable_mask = (1 << self._get_bit_index(start_node, board_size))
        reachable_count = 1
        
        while queue:
            curr = queue.popleft() 
            for neighbor in adj_list[curr]:
                n_idx = self._get_bit_index(neighbor, board_size)
                if (visited_mask & (1 << n_idx)) == 0 and (reachable_mask & (1 << n_idx)) == 0:
                    reachable_mask |= (1 << n_idx)
                    reachable_count += 1
                    queue.append(neighbor)

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

    def _a_star(self, board: Board) -> Tuple[Optional[SolutionPath], int]:
        start_time = time.perf_counter()
        timeout_sec = self._timeout / 1000.0
        steps = 0
        
        board_size = board.getSize
        total_cells = board.getCellCount()
        waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)

        # --- PRECOMPUTATION ---
        # Eliminate O(N) linear scans from the main search loop entirely
        waypoint_map = {wp.getPosition: wp for wp in waypoints}

        # The path must END at the last waypoint, not merely pass through it — but only when
        # there are at least two waypoints (a distinct start and end). With a single waypoint
        # there is no end constraint: start there and cover the board, finishing anywhere.
        final_wp_pos = waypoints[-1].getPosition if len(waypoints) >= 2 else None
        
        adj_list = {}
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

        pq: List[SearchNode] = []
        counter = 0

        # SEED ONLY FROM WAYPOINT 1. The path must START at the first waypoint, so there is
        # exactly one valid seed. Seeding from every cell (the old behaviour) let the search
        # accept paths that begin on a non-waypoint cell and merely pass through waypoint 1
        # mid-way — not a valid Zip solution. It also multiplied the frontier by the cell
        # count, which is the main reason the search blew its time budget.
        if waypoints:
            seeds = [waypoints[0].getPosition]
        else:
            seeds = list(board.getAllPositions())

        for start_pos in seeds:
            next_idx = 0
            wp = waypoint_map.get(start_pos)

            if wp:
                if len(waypoints) > 0 and wp.getOrder != waypoints[0].getOrder:
                    continue
                next_idx = 1

            visited_mask = (1 << self._get_bit_index(start_pos, board_size))
            h = self._heuristic(start_pos, waypoints, next_idx)
            g = -1
            f = g + h

            heapq.heappush(pq, SearchNode(f, g, counter, start_pos, visited_mask, next_idx, None))
            counter += 1

        closed_set = set()
        target_mask = (1 << total_cells) - 1 

        while pq:
            if time.perf_counter() - start_time > timeout_sec:
                break
                
            steps += 1
            current_node = heapq.heappop(pq)
            
            if current_node.visited_mask == target_mask:
                # Full coverage AND every waypoint visited in order AND the path terminates
                # on the final waypoint. The last condition is essential: without it the
                # search accepts paths that pass through the last waypoint mid-way and end
                # elsewhere, which is not a valid Zip solution.
                if current_node.next_idx == len(waypoints) and (
                    final_wp_pos is None or current_node.pos == final_wp_pos
                ):
                    return self._reconstruct_path(current_node), steps

            state_key = (current_node.pos, current_node.visited_mask, current_node.next_idx)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            # Use O(1) Precomputed Adjacency List
            for n_pos in adj_list[current_node.pos]:
                n_idx_bit = self._get_bit_index(n_pos, board_size)
                
                if (current_node.visited_mask & (1 << n_idx_bit)) != 0:
                    continue
                
                n_idx = current_node.next_idx
                # Use O(1) Precomputed Waypoint Map
                wp = waypoint_map.get(n_pos)
                if wp:
                    if n_idx >= len(waypoints) or wp.getOrder != waypoints[n_idx].getOrder:
                        continue 
                    n_idx += 1
                    
                n_mask = current_node.visited_mask | (1 << n_idx_bit)

                # After moving, n_pos is the new path head; parity pruning needs it and the
                # final waypoint to check the remaining-cell colour balance.
                if not self._is_viable_state(
                    n_mask, board_size, total_cells, adj_list, n_pos, final_wp_pos
                ):
                    continue

                n_depth = -current_node.neg_depth + 1
                n_h = self._heuristic(n_pos, waypoints, n_idx)
                n_f = -n_depth + n_h
                
                heapq.heappush(pq, SearchNode(n_f, -n_depth, counter, n_pos, n_mask, n_idx, current_node))
                counter += 1

        return None, steps

    def solve(self, board: Board) -> SolverResult:
        start_time = time.perf_counter()
        path, steps = self._a_star(board)
        runtime_ms = int((time.perf_counter() - start_time) * 1000)
        metrics = SolverMetrics(runtimeMs=runtime_ms, steps=steps, attempts=1)
        
        if path:
            return SolverResult(
                status=SolverStatus.SOLVED, path=path,
                message="Successfully found a path using an optimized A* search.", metrics=metrics
            )
        elif runtime_ms >= self._timeout:
            return SolverResult(
                status=SolverStatus.TIMEOUT, path=None,
                message="Algorithmic search timed out.", metrics=metrics
            )
        else:
            return SolverResult(
                status=SolverStatus.UNSOLVABLE, path=None,
                message="No valid solution exists for this board.", metrics=metrics
            )