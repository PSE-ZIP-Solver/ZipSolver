import random
from functools import lru_cache
from typing import Dict, List, Tuple

from backend.puzzle_logic import Position, Board

Coord = Tuple[int, int]


class BoardGenerator:
    # Precomputed once, shared across all calls.
    DIRECTIONS: Tuple[Coord, ...] = ((0, 1), (1, 0), (0, -1), (-1, 0))

    @staticmethod
    def generate(boardSize: int, intermediateWaypoints: int, walls: int, numberBoards: int = 1) -> List[Board]:
        results: List[Board] = []

        while len(results) < numberBoards:
            board = Board(boardSize)
            start, end = BoardGenerator._generateTwoDistinctRandomPositions(boardSize)

            path = BoardGenerator._findHamiltonianPath(board, start, end)

            if path:
                board = BoardGenerator._placeRandomWaypoints(board, path, intermediateWaypoints)
                board = BoardGenerator._placeRandomWalls(board, path, walls)
                results.append(board)

        return results

    @staticmethod
    def _generateTwoDistinctRandomPositions(boardSize: int) -> tuple[Position, Position]:
        while True:
            idxStart, idxEnd = random.sample(range(boardSize * boardSize), 2)
            start = Position(idxStart % boardSize, idxStart // boardSize)
            end = Position(idxEnd % boardSize, idxEnd // boardSize)

            p_start = (start.getX + start.getY) % 2
            p_end = (end.getX + end.getY) % 2

            if boardSize % 2 == 0:
                if p_start != p_end:
                    return start, end
            else:
                if p_start == 0 and p_end == 0:
                    return start, end

    @staticmethod
    @lru_cache(maxsize=16)
    def _get_adjacency(boardSize: int) -> Dict[Coord, Tuple[Coord, ...]]:
        adjacency: Dict[Coord, Tuple[Coord, ...]] = {}
        for y in range(boardSize):
            for x in range(boardSize):
                neighbors = tuple(
                    (x + dx, y + dy)
                    for dx, dy in BoardGenerator.DIRECTIONS
                    if 0 <= x + dx < boardSize and 0 <= y + dy < boardSize
                )
                adjacency[(x, y)] = neighbors
        return adjacency

    @staticmethod
    def _degree(pos: Coord, visited: set, adjacency: Dict[Coord, Tuple[Coord, ...]]) -> int:
        """Warnsdorff's heuristic: count unvisited neighbors."""
        return sum(1 for nb in adjacency[pos] if nb not in visited)

    @staticmethod
    def _findHamiltonianPath(board: Board, start: Position, end: Position) -> List[Position]:
        boardSize = board.getSize
        adjacency = BoardGenerator._get_adjacency(boardSize)
        total_cells = boardSize * boardSize

        start_t: Coord = (start.getX, start.getY)
        end_t: Coord = (end.getX, end.getY)

        visited = {start_t}
        path: List[Coord] = [start_t]

        def candidates_for(pos: Coord) -> List[Coord]:
            unvisited_count = total_cells - len(path)

            # 1. FAST CONNECTIVITY PRUNING
            # If the remaining unvisited nodes don't form a single connected component
            # that includes the end node, a path is strictly impossible.
            seen = {end_t}
            q = [end_t]
            head = 0
            while head < len(q):
                curr = q[head]
                head += 1
                for nb in adjacency[curr]:
                    if nb not in visited and nb not in seen:
                        seen.add(nb)
                        q.append(nb)

            if len(seen) < unvisited_count:
                return []  # Dead-end detected instantly; trigger backtrack.

            candidates = []
            for nb in adjacency[pos]:
                if nb in visited:
                    continue
                # Only allow visiting `end` as the very last move.
                if nb == end_t and len(path) < total_cells - 1:
                    continue
                candidates.append(nb)

            random.shuffle(candidates)
            candidates.sort(key=lambda p: BoardGenerator._degree(p, visited, adjacency))
            return candidates

        frames: List[List[Coord]] = [candidates_for(start_t)]

        # 2. MAX BACKTRACK LIMIT
        backtracks = 0
        MAX_BACKTRACKS = 5000

        while frames:
            candidates = frames[-1]

            if not candidates:
                backtracks += 1
                # Abort safely if stuck in a pathologically hard configuration
                if backtracks > MAX_BACKTRACKS:
                    return None

                frames.pop()
                visited.discard(path.pop())
                continue

            nxt = candidates.pop()
            visited.add(nxt)
            path.append(nxt)

            if len(path) == total_cells:
                return [Position(x, y) for x, y in path]

            frames.append(candidates_for(nxt))

        return None

    @staticmethod
    def _placeRandomWaypoints(board: Board, path: List[Position], intermediateWaypoints: int) -> Board:
        size = board.getSize
        allowedIndices = set(range(size * size))
        idxStart = path[0].getX + path[0].getY * size
        idxEnd = path[-1].getX + path[-1].getY * size
        allowedIndices.discard(idxStart)
        allowedIndices.discard(idxEnd)

        samples = min(intermediateWaypoints, len(allowedIndices))
        intermediateIndices = random.sample(list(allowedIndices), samples)

        # 3. RELIABLE AND FAST LOOKUPS
        # Rely on tuple (x,y) lookups rather than Object comparisons
        intermediate_coords = {(idx % size, idx // size) for idx in intermediateIndices}
        ordered_waypoints = [pos for pos in path if (pos.getX, pos.getY) in intermediate_coords]

        board.addWaypoint(path[0], 1)
        nextOrder = 2
        for pos in ordered_waypoints:
            board.addWaypoint(pos, nextOrder)
            nextOrder += 1
        board.addWaypoint(path[-1], nextOrder)

        return board

    @staticmethod
    def _placeRandomWalls(board: Board, path: List[Position], walls: int) -> Board:
        size = board.getSize

        possibleWalls: Dict[Tuple[Coord, Coord], Tuple[Position, Position]] = {}
        for y in range(size):
            for x in range(size):
                if x + 1 < size:
                    key = ((x, y), (x + 1, y))
                    possibleWalls[key] = (Position(x, y), Position(x + 1, y))
                if y + 1 < size:
                    key = ((x, y), (x, y + 1))
                    possibleWalls[key] = (Position(x, y), Position(x, y + 1))

        pathObstructingWalls = set()
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            key = tuple(sorted([(a.getX, a.getY), (b.getX, b.getY)]))
            pathObstructingWalls.add(key)

        allowedKeys = [k for k in possibleWalls if k not in pathObstructingWalls]
        samples = min(walls, len(allowedKeys))
        selectedKeys = random.sample(allowedKeys, samples)

        for key in selectedKeys:
            posA, posB = possibleWalls[key]
            board.addWall(posA, posB)

        return board