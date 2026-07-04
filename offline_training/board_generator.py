import argparse
import random
import sys
from pathlib import Path
from typing import List

# Direct execution makes ``offline_training`` the import root. Add the repository
# root so sibling packages such as ``backend`` remain importable.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position


# number of results to generate
RESULTS = 1000

class BoardGenerator:
    @staticmethod
    def generate(
        boardSize: int,
        intermediateWaypoints: int,
        walls: int,
        resultCount: int | None = None,
    ) -> List[Board]:
        """
        Generates a batch of solvable puzzle, as follows:
        1. Selects two distinct random positions (start and end) that satisfy 
           mathematical parity requirements for a Hamiltonian path.
        2. Finds a Hamiltonian path that visits every cell on the grid exactly once 
           using DFS with Warnsdorff's heuristic for efficiency.
        3. Places waypoints along the discovered path in ascending order, ensuring 
           the puzzle follows a specific sequence.
        4. Randomly places walls on the grid that do not obstruct the path, 
           increasing difficulty without making the board unsolvable.

        Args:
            boardSize (int): The side length of the square board (e.g., 6, 7, or 8).
            intermediateWaypoints (int): The number of waypoint markers to place 
                between the start and end positions.
            walls (int): The number of distinct walls to place on the board.

        Args:
            resultCount (int | None): Number of boards to generate. When omitted,
                the global RESULTS constant is used.

        Returns:
            List[Board]: A list containing the generated Board objects.
        """
        target_results = RESULTS if resultCount is None else resultCount
        if boardSize < 2:
            raise ValueError("boardSize must be at least 2")
        if intermediateWaypoints < 0:
            raise ValueError("intermediateWaypoints cannot be negative")
        if walls < 0:
            raise ValueError("walls cannot be negative")
        if target_results < 0:
            raise ValueError("resultCount cannot be negative")

        results: List[Board] = [] 
        
        # genrate resulting boards
        while len(results) < target_results:
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
            # select two distinct 1D-indices for the square grid (0 to boardSize-1)
            idxStart, idxEnd = random.sample(range(boardSize * boardSize), 2)
            # project the two 1D-indices to 2D- coordinates 
            start = Position(idxStart % boardSize, idxStart // boardSize)
            end = Position(idxEnd % boardSize, idxEnd // boardSize)
            
            p_start = (start.getX + start.getY) % 2
            p_end = (end.getX + end.getY) % 2

            if boardSize % 2 == 0:
                # Even board: start and end must be on different "checkerboard colors"
                if p_start != p_end:
                    return start, end
            else:
                # Odd board: both must be on the majority color (parity 0) 
                # to allow a path through all cells
                if p_start == 0 and p_end == 0:
                    return start, end
    
    @staticmethod
    def _findHamiltonianPath(board: Board, start: Position, end: Position) -> List[Position] | None:
        total_cells = board.getCellCount()
        visited = {start}
        path: List[Position] = [start]

        def get_degree(p: Position) -> int:
            """Warnsdorff's heuristic: count available unvisited neighbors."""
            count = 0
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nb = Position(p.getX + dx, p.getY + dy)
                if board.isInside(nb) and nb not in visited:
                    count += 1
            return count

        def _dfs(current: Position) -> bool:
            # Break Condition: hamiltonian path found
            if len(path) == total_cells:
                return current == end

            cx, cy = current.getX, current.getY
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = Position(cx + dx, cy + dy)
                if board.isInside(neighbor) and neighbor not in visited:
                    # only visit end as the last move 
                    if neighbor == end and len(path) < total_cells - 1:
                        continue
                    neighbors.append(neighbor)
            
            # Warnsdorff's heuristic: Sort neighbors by their degree (fewer neighbors first)
            # This speeds up finding the first valid path significantly
            neighbors.sort(key=get_degree)

            for neighbor in neighbors:
                visited.add(neighbor)
                path.append(neighbor)

                if _dfs(neighbor):
                    return True
                
                # backtracking
                path.pop()
                visited.remove(neighbor)

            return False

        # start dfs
        if _dfs(start):
            return list(path)
    
        return None
    
    @staticmethod
    def _placeRandomWaypoints(board: Board, path: List[Position], intermediateWaypoints: int) -> Board:
        # Generate positions of intermediate waypoints randomly
        
        # add all possible positions as 1D indices to allowed intermediate positions
        allowedIndices = set(range(board.getSize * board.getSize))
        # remove start and end from from allowed positions
        idxStart = path[0].getX + path[0].getY * board.getSize
        idxEnd = path[-1].getX + path[-1].getY * board.getSize
        allowedIndices.discard(idxStart)
        allowedIndices.discard(idxEnd) 
        # add random waypoints at allowed positions
        samples = min(intermediateWaypoints, len(allowedIndices))
        intermediateIndices = random.sample(list(allowedIndices), samples)
        # convert 1D indices to 2D positions
        intermediatePosition = {Position(idx % board.getSize, idx // board.getSize) for idx in intermediateIndices}
        # sort according to path
        intermediatePosition = [pos for pos in path if pos in intermediatePosition]
        
        # add waypoints

        # add waypoint at start of path
        board.addWaypoint(path[0], 1)
        # add intermediate waypoints
        nextOrder = 2
        for pos in intermediatePosition:
            board.addWaypoint(pos, nextOrder)
            nextOrder += 1
        # add waypoint at end of path
        board.addWaypoint(path[-1], nextOrder)
        
        return board
    
    @staticmethod
    def _placeRandomWalls(board: Board, path: List[Position], walls: int) -> Board:
        # Find all possible wall positions
        # Store them in sorted tuples, for (A, B) to equal (B, A)
        possibleWalls = set()
        for y in range(board.getSize):
            for x in range(board.getSize):
                current = Position(x, y)
                # right neighbor
                if x + 1 < board.getSize:
                    right = Position(x + 1, y)
                    # sort by coordinate for unique ID
                    wall = tuple(sorted([current, right], key=lambda p: (p.getX, p.getY)))
                    possibleWalls.add(wall)
                # bottom neighbor
                if y + 1 < board.getSize:
                    down = Position(x, y + 1)
                    # sort by coordinate for unique ID
                    wall = tuple(sorted([current, down], key=lambda p: (p.getX, p.getY)))
                    possibleWalls.add(wall)

        # Find wall positions, that obstruct the path
        pathObstructingWalls = set()
        for i in range(len(path) - 1):
            current = path[i]
            next = path[i+1]
            wall = tuple(sorted([current, next], key=lambda p: (p.getX, p.getY)))
            pathObstructingWalls.add(wall)
 
        # Determine allowedWallPositions
        allowedWalls = list(possibleWalls - pathObstructingWalls)

        # Select wall from allowed walls randomly  
        samples = min(walls, len(allowedWalls))
        selectedWalls = random.sample(allowedWalls, samples)

        # Add walls to the board
        for wall in selectedWalls:
            board.addWall(wall[0], wall[1])

        return board


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


def _board_size(value: str) -> int:
    parsed = int(value)
    if parsed < 2:
        raise argparse.ArgumentTypeError("board size must be at least 2")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate solvable Zip puzzle boards."
    )
    parser.add_argument("--board-size", type=_board_size, default=6)
    parser.add_argument("--intermediate-waypoints", type=_non_negative_int, default=5)
    parser.add_argument("--walls", type=_non_negative_int, default=5)
    parser.add_argument("--results", type=_non_negative_int, default=1)
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible output")
    args = parser.parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    boards = BoardGenerator.generate(
        args.board_size,
        args.intermediate_waypoints,
        args.walls,
        resultCount=args.results,
    )
    print(f"Generated {len(boards)} board(s):")
    for index, board in enumerate(boards, start=1):
        print(
            f"  {index}: {board.getSize}x{board.getSize}, "
            f"{len(board.getWaypoints)} waypoints, {len(board.getWalls)} walls"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
