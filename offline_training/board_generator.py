import random
from typing import List
from backend.puzzle_logic import Position, Board


class BoardGenerator:
    @staticmethod
    def generate(boardSize: int, intermediateWaypoints: int, walls: int, numberBoards: int = 1) -> List[Board]:
        results: List[Board] = []

        while len(results) < numberBoards:
            print(f"Generating board {len(results) + 1}/{numberBoards}")
            board = Board(boardSize)

            # 1. Pick only the start position
            idxStart = random.randint(0, boardSize * boardSize - 1)
            start = Position(idxStart % boardSize, idxStart // boardSize)

            # 2. Find ANY valid Hamiltonian path (Warnsdorff handles this instantly)
            path = BoardGenerator._findHamiltonianPath(board, start)

            if path:
                board = BoardGenerator._placeRandomWaypoints(board, path, intermediateWaypoints)
                board = BoardGenerator._placeRandomWalls(board, path, walls)
                results.append(board)

        return results

    @staticmethod
    def _findHamiltonianPath(board: Board, start: Position) -> List[Position]:
        boardSize = board.getSize
        total_cells = boardSize * boardSize
        start_idx = start.getY * boardSize + start.getX

        # Precompute 1D adjacency list for O(1) lookups
        adj = [[] for _ in range(total_cells)]
        for y in range(boardSize):
            for x in range(boardSize):
                idx = y * boardSize + x
                if x > 0: adj[idx].append(idx - 1)
                if x < boardSize - 1: adj[idx].append(idx + 1)
                if y > 0: adj[idx].append(idx - boardSize)
                if y < boardSize - 1: adj[idx].append(idx + boardSize)

        visited = [False] * total_cells
        visited[start_idx] = True
        path = [start_idx]

        def _dfs(curr_idx: int) -> bool:
            # Break Condition: 64 cells visited
            if len(path) == total_cells:
                return True

            valid_neighbors = [n for n in adj[curr_idx] if not visited[n]]

            # Warnsdorff's heuristic: Sort by fewest unvisited neighbors
            def get_degree(n):
                count = sum(1 for nn in adj[n] if not visited[nn])
                # Random tie-breaking is critical to prevent geometric loops
                return count + random.random()

            valid_neighbors.sort(key=get_degree)

            for n in valid_neighbors:
                visited[n] = True
                path.append(n)

                if _dfs(n):
                    return True

                path.pop()
                visited[n] = False

            return False

        if _dfs(start_idx):
            # Convert 1D path back to Position objects
            return [Position(idx % boardSize, idx // boardSize) for idx in path]

        return None

    # ... keep your _placeRandomWaypoints and _placeRandomWalls methods exactly as they are ...

    @staticmethod
    def _placeRandomWaypoints(board: Board, path: List[Position], intermediateWaypoints: int) -> Board:
        boardSize = board.getSize
        allowedIndices = set(range(boardSize * boardSize))

        idxStart = path[0].getX + path[0].getY * boardSize
        idxEnd = path[-1].getX + path[-1].getY * boardSize
        allowedIndices.discard(idxStart)
        allowedIndices.discard(idxEnd)

        samples = min(intermediateWaypoints, len(allowedIndices))
        intermediateIndices = set(random.sample(list(allowedIndices), samples))

        intermediatePositions = [pos for pos in path if (pos.getX + pos.getY * boardSize) in intermediateIndices]

        board.addWaypoint(path[0], 1)
        for i, pos in enumerate(intermediatePositions, start=2):
            board.addWaypoint(pos, i)
        board.addWaypoint(path[-1], len(intermediatePositions) + 2)

        return board

    @staticmethod
    def _placeRandomWalls(board: Board, path: List[Position], walls: int) -> Board:
        boardSize = board.getSize
        possibleWalls = []

        # Calculate possible walls using 1D math instead of lambda sorting
        for y in range(boardSize):
            for x in range(boardSize):
                idx = y * boardSize + x
                if x + 1 < boardSize:
                    possibleWalls.append((idx, idx + 1))
                if y + 1 < boardSize:
                    possibleWalls.append((idx, idx + boardSize))

        pathObstructingWalls = set()
        for i in range(len(path) - 1):
            idx1 = path[i].getX + path[i].getY * boardSize
            idx2 = path[i + 1].getX + path[i + 1].getY * boardSize
            pathObstructingWalls.add((min(idx1, idx2), max(idx1, idx2)))

        allowedWalls = list(set(possibleWalls) - pathObstructingWalls)
        samples = min(walls, len(allowedWalls))

        for w in random.sample(allowedWalls, samples):
            pos1 = Position(w[0] % boardSize, w[0] // boardSize)
            pos2 = Position(w[1] % boardSize, w[1] // boardSize)
            board.addWall(pos1, pos2)

        return board