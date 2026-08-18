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
    """
    Represents an isolated, evaluated state vector within the A* Priority Queue.

    Responsibility:
        Maintains granular snapshot data of a specific routing branch, preserving the exact 
        spatial position, the sequence history, and heuristic scorings required to accurately 
        rank the optimal exploration path.

    Implementation Details:
        Utilizes Python's `@dataclass` equipped with strict `order=True` flags for seamless 
        integration into `heapq` structures. Rapidly prunes mathematical overhead by encapsulating 
        visited cells purely as compressed binary integers (bitmasks), disabling direct evaluation 
        comparisons on spatial/pointer fields using `compare=False`.
    """
    f_score: int
    neg_depth: int
    counter: int
    pos: Position = field(compare=False)
    visited_mask: int = field(compare=False)
    next_idx: int = field(compare=False)
    parent: Optional['SearchNode'] = field(compare=False, default=None)


class AlgorithmicSolver(Solver):
    """
    A highly optimized, deterministic pathfinding engine utilizing A* heuristics.

    Responsibility:
        Functions as the mathematically flawless, exhaustive backend resolution agent. It calculates 
        perfect Hamiltonian solutions by systematically navigating graph permutations while aggressively 
        filtering out mathematically impossible states (loose ends, parity violations) to maintain speed.

    Implementation Details:
        Transforms the spatial 2D grid into a highly compressed graph layout mapped via integer dictionaries. 
        Execution relies primarily on bitwise mask operations and high-performance heuristic math 
        to track traversal histories and topological remaining requirements with minimal memory allocation.
    """
    def __init__(self, timeout: int):
        """
        Initializes the deterministic search engine with explicit operational boundaries.

        Args:
            timeout: The absolute temporal ceiling defining maximum permitted execution loops.

        Implementation Details:
            Reserves the temporal limit directly into a protected attribute, establishing 
            a localized threshold designed to aggressively break out of computationally 
            improbable permutations before stalling API threads.
        """
        self._timeout = timeout

    def _get_bit_index(self, pos: Position, board_size: int) -> int:
        """
        Translates a dimensional coordinate into a localized 1D scalar for bitwise operations.

        Args:
            pos: The requested spatial grid coordinate.
            board_size: The absolute length forming the bounding grid limitation.

        Returns:
            The normalized raw integer index mathematically mapping to the cell.

        Implementation Details:
            Extracts property bounds and multiplies the row scalar against the total 
            dimension threshold before factoring in column offsets, enabling seamless translation 
            for binary tracking arrays.
        """
        return pos.getY * board_size + pos.getX

    def _heuristic(self, current, waypoints, next_wp_idx):
        """
        Computes the optimized A* Manhattan distance remaining across upcoming sequential milestones.

        Args:
            current: The present navigational tip evaluating upcoming trajectory requirements.
            waypoints: The sorted structural milestone limits governing progression maps.
            next_wp_idx: The active tracking index noting the subsequent mandatory checkpoint.

        Returns:
            The raw scalar metric estimating minimum remaining distance requirements.

        Implementation Details:
            Dynamically computes immediate distance towards the closest upcoming waypoint natively, 
            then chains Manhattan summations linking the sequence of all remaining subsequent milestones 
            together. Yields exactly 0 if completely exhausted.
        """
        if next_wp_idx < len(waypoints):
            target_pos = waypoints[next_wp_idx].getPosition
            h = abs(current.getX - target_pos.getX) + abs(current.getY - target_pos.getY)
            for i in range(next_wp_idx, len(waypoints)-1):
                p1=waypoints[i].getPosition; p2=waypoints[i+1].getPosition
                h += abs(p1.getX-p2.getX)+abs(p1.getY-p2.getY)
            return h
        return 0

    def _parity_ok(self, visited_mask, head, target, board_size, total_cells):
        """
        Calculates strict mathematical color balance to prematurely prune impossible grid divisions.

        Args:
            visited_mask: The compressed bit-array of successfully consumed topologies.
            head: The active spatial tip currently leading the search tree.
            target: The mandatory terminal location marking the end boundary.
            board_size: The dimensional parameter mapping absolute boundaries.
            total_cells: The cumulative volume requirement dictating total traversal counts.

        Returns:
            True if the remaining graph nodes maintain valid checkerboard bipartition balance, False otherwise.

        Implementation Details:
            Projects the remaining layout onto a theoretical bipartite graph (checkerboard coloration). 
            Counts specific color arrays against the active mask and mathematically derives if traversing 
            between the remaining odd/even layouts naturally terminates at the target requirement. 
            Instantly returns true if endpoints remain unfixed.
        """
        if target is None:
            return True  # no fixed endpoint -> colour balance is unconstrained
        remaining = total_cells - visited_mask.bit_count() + 1
        count = [0, 0]
        for p in self._cells_cache:
            if (visited_mask >> self._get_bit_index(p, board_size)) & 1 == 0:
                count[(p.getX + p.getY) & 1] += 1
        head_colour = (head.getX + head.getY) & 1
        count[head_colour] += 1
        target_colour = (target.getX + target.getY) & 1
        if target_colour != (head_colour ^ ((remaining - 1) & 1)):
            return False
        return count[head_colour] == (remaining + 1) // 2 and count[1 - head_colour] == remaining // 2

    def _is_viable_state(self, visited_mask, head, target, board_size, total_cells, adj_list):
        """
        Evaluates active layout connectivity to violently reject branches forming physical chokepoints.

        Args:
            visited_mask: The encoded tracking binary array.
            head: The active focal location mapping trajectory points.
            target: The calculated terminus block dictating endpoint constraints.
            board_size: The dimensional scalar forming array sizes.
            total_cells: The exact metric counting grid completion targets.
            adj_list: The pre-compiled dictionary retaining node connections.

        Returns:
            True if the topology permits ongoing Hamiltonian flow without trapped fragments, False if fractured.

        Implementation Details:
            Executes a rapid flood-fill analysis prioritizing unvisited edges. Identifies "loose ends" 
            (unoccupied cells reduced to a single valid exit) and actively drops evaluation states if 
            multiple traps form simultaneously. Rebuilds reachable matrices and compares directly against 
            calculated untraversed volumes to verify absolute contiguous connections.
        """
        head_idx = self._get_bit_index(head, board_size)
        start_node = None
        loose_ends = 0
        for p, nbrs in adj_list.items():
                bit_idx = self._get_bit_index(p, board_size)
                if (visited_mask >> bit_idx) & 1:
                    continue
                if start_node is None:
                    start_node = p
                exits = 0
                for n in nbrs:
                    n_idx = self._get_bit_index(n, board_size)
                    if (visited_mask >> n_idx) & 1 == 0 or n_idx == head_idx:
                        exits += 1
                if target is not None:
                    if p == target:
                        if exits < 1:
                            return False
                    elif exits < 2:
                        return False
                else:
                    # No fixed endpoint: the path may finish anywhere, so at most one
                    # unvisited cell is allowed to have a single exit.
                    if exits < 1:
                        return False
                    if exits < 2:
                        loose_ends += 1
                        if loose_ends > 1:
                            return False
        if start_node is None:
            return True
        reachable_mask = 0
        queue = deque()
        for n in adj_list[head]:
            n_idx = self._get_bit_index(n, board_size)
            if (visited_mask >> n_idx) & 1 == 0:
                reachable_mask |= 1 << n_idx
                queue.append(n)
        reachable_count = reachable_mask.bit_count()
        while queue:
            curr = queue.popleft()
            for neighbor in adj_list[curr]:
                n_idx = self._get_bit_index(neighbor, board_size)
                if (visited_mask >> n_idx) & 1 == 0 and (reachable_mask >> n_idx) & 1 == 0:
                    reachable_mask |= 1 << n_idx
                    reachable_count += 1
                    queue.append(neighbor)
        expected_unvisited = total_cells - visited_mask.bit_count()
        return reachable_count == expected_unvisited

    def _reconstruct_path(self, end_node):
        """
        Crawls historically nested pointers to output the definitive solution mapping array.

        Args:
            end_node: The terminus memory block tracking the successful completion state.

        Returns:
            The structured traversal array securely formatted for orchestrator consumption.

        Implementation Details:
            Extracts coordinates sequentially by recursively querying `parent` linkages within the 
            terminal dataclass until the origin is reached. The array is mathematically reversed to 
            secure a proper start-to-finish layout before packing directly into the domain wrapper.
        """
        positions = []
        curr = end_node
        while curr:
            positions.append(curr.pos); curr = curr.parent
        positions.reverse()
        sp = SolutionPath()
        for p in positions: sp.add(p)
        return sp

    def _a_star(self, board):
        """
        Executes the primary heuristic search loop analyzing millions of graph iterations.

        Args:
            board: The structural grid layout defining constraints and barriers.

        Returns:
            A composite tuple housing the extracted path (if found), total evaluation steps, 
            and a boolean identifying if calculations hit temporal limits.

        Implementation Details:
            Sets up high-speed localized caches (adjacency lists, waypoint maps) mapped entirely 
            to bits to avoid nested Python iterations. Initializes prioritized `heapq` structures 
            employing Manhattan heuristics against node depth combinations to aggressively funnel 
            searches into promising channels. Enforces strict timeouts and dynamically alters 
            starting bounds/seeding mechanics based on raw milestone volume counts.
        """
        start_time = time.perf_counter()
        timeout_sec = self._timeout / 1000.0
        steps = 0; timed_out = False
        board_size = board.getSize
        total_cells = board.getCellCount()
        waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)
        waypoint_map = {wp.getPosition: wp for wp in waypoints}
        adj_list = {}
        for y in range(board_size):
            for x in range(board_size):
                p = Position(x, y); neighbors = []
                for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                    n_pos = Position(x+dx, y+dy)
                    if board.isInside(n_pos) and not board.hasWallBetween(p, n_pos):
                        neighbors.append(n_pos)
                adj_list[p] = neighbors
        self._cells_cache = list(adj_list.keys())
        target_mask = (1 << total_cells) - 1
        pq = []; counter = 0

        # Seeds. With >=2 waypoints the path must start at waypoint 1 and end at the last
        # one, which drives all the pruning. With 0 or 1 waypoints there is no fixed
        # endpoint: seed every cell (0 wp) or the single waypoint (1 wp) and relax the
        # target-dependent checks.
        if len(waypoints) >= 2:
            target_pos = waypoints[-1].getPosition
            seeds = [(waypoints[0].getPosition, 1)]
        elif len(waypoints) == 1:
            target_pos = None
            seeds = [(waypoints[0].getPosition, 1)]
        else:
            target_pos = None
            seeds = [(p, 0) for p in adj_list]

        for sp, sidx in seeds:
            vm = 1 << self._get_bit_index(sp, board_size)
            hh = self._heuristic(sp, waypoints, sidx)
            heapq.heappush(pq, SearchNode(-1+hh, -1, counter, sp, vm, sidx, None)); counter += 1
        closed_set = set()
        while pq:
            if time.perf_counter() - start_time > timeout_sec:
                timed_out = True; break
            steps += 1
            current_node = heapq.heappop(pq)
            if current_node.visited_mask == target_mask:
                if current_node.next_idx == len(waypoints) and (
                    target_pos is None or current_node.pos == target_pos
                ):
                    return self._reconstruct_path(current_node), steps, False
                continue
            state_key = (current_node.pos, current_node.visited_mask, current_node.next_idx)
            if state_key in closed_set: continue
            closed_set.add(state_key)
            for n_pos in adj_list[current_node.pos]:
                n_idx_bit = self._get_bit_index(n_pos, board_size)
                if (current_node.visited_mask >> n_idx_bit) & 1: continue
                n_idx = current_node.next_idx
                wp = waypoint_map.get(n_pos)
                if wp:
                    if n_idx >= len(waypoints) or wp.getOrder != waypoints[n_idx].getOrder: continue
                    n_idx += 1
                n_mask = current_node.visited_mask | (1 << n_idx_bit)
                if target_pos is not None and n_pos == target_pos and n_mask != target_mask: continue
                if n_mask != target_mask:
                    if not self._parity_ok(n_mask, n_pos, target_pos, board_size, total_cells): continue
                    if not self._is_viable_state(n_mask, n_pos, target_pos, board_size, total_cells, adj_list): continue
                n_depth = -current_node.neg_depth + 1
                n_h = self._heuristic(n_pos, waypoints, n_idx)
                heapq.heappush(pq, SearchNode(-n_depth+n_h, -n_depth, counter, n_pos, n_mask, n_idx, current_node)); counter += 1
        return None, steps, timed_out

    def solve(self, board):
        """
        Coordinates the deterministic calculation lifecycle and encapsulates final results.

        Args:
            board: The static dimensional boundaries and requirements being analyzed.

        Returns:
            The structured state package definitively reporting success vectors, timing constraints, 
            or mathematical impossibilities.

        Implementation Details:
            Actively queries core execution parameters directly against high-precision hardware clocks 
            to trace MS expenditures. Unpacks the localized search tuples into broad system outcome 
            states and constructs absolute metrics wrappers prior to dispatch.
        """
        t = time.perf_counter()
        path, steps, timed_out = self._a_star(board)
        ms = int((time.perf_counter()-t)*1000)
        m = SolverMetrics(runtimeMs=ms, steps=steps, attempts=1)
        if path: return SolverResult(status=SolverStatus.SOLVED, path=path, message="ok", metrics=m)
        if timed_out: return SolverResult(status=SolverStatus.TIMEOUT, path=None, message="timeout", metrics=m)
        return SolverResult(status=SolverStatus.UNSOLVABLE, path=None, message="unsolvable", metrics=m)