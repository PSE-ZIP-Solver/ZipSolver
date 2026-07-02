from backend.PuzzleLogic import  Position, Board
from typing import List
import random


# number of results to generate
RESULTS = 1000

class BoardGenerator:
    @staticmethod
    def generate(boardSize: int, intermediateWaypoints: int, walls: int) -> List[Board]:
        results: List[Board] = [] 
        
        # TODO remove?
        # Assert parameter constraints are meat
        assert 6 <= boardSize <= 8 and intermediateWaypoints <= boardSize*boardSize - 2 and walls <=  (boardSize - 1) * (boardSize - 1)
        
        # genrate resulting boards
        while len(results) < RESULTS:
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
            # (i.e. for a board of size 3: idx = 4 = 0 + 1 * 3 <=> x = idx % 3 = 1; y = idx / 3 = 1)
            start = Position(idxStart % boardSize, idxStart // boardSize)
            end = Position(idxEnd % boardSize, idxEnd // boardSize)
            
            # Parity check: For even-sized boards, start and end must be on 
            # different "checkerboard colors" (one x+y sum must be even, the other odd)
            if (start.getX + start.getY) % 2 != (end.getX + end.getY) % 2:
                return start, end
    
    @staticmethod
    def _findHamiltonianPath(board: Board, start: Position, end: Position) -> List[Position]:
        total_cells = board.getCellCount()
        visited = {start}
        path: List[Position] = [start]

        def _dfs(current: Position) -> bool:
            # Break Condition: hamitonian path from start to end found
            if len(path) == total_cells:
                return current == end

            # Check neighbors
            cx, cy = current.getX, current.getY
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = Position(cx + dx, cy + dy)
                if board.isInside(neighbor) and neighbor not in visited:
                    # only visit end as the last move 
                    if neighbor == end and len(path) < total_cells - 1:
                        continue

                    # step
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
    
        # might occur if board is of odd size
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