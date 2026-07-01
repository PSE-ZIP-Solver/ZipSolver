from backend.PuzzleLogic import  Position, Waypoint, Wall, Board
from typing import List
import random


# number of results to generate
RESULTS = 1000

class BoardGenerator:
    @staticmethod
    def genrate(boardSize: int, intermediateWaypoints: int, maxWalls: int) -> List[Board]:
        results: List[Board] = [] 
        
        # TODO remove?
        # Assert parameter constraints are meat
        assert 6 <= boardSize <= 8 and intermediateWaypoints <= boardSize*boardSize - 2 and maxWalls <=  (boardSize - 1) * (boardSize - 1)
        
        # genrate resulting boards
        for _ in range(RESULTS):
            board = Board(boardSize)
            start, end = BoardGenerator._generateTwoDistinctRandomPositions(boardSize)
            path = BoardGenerator._findHamitonianPath(board, start, end)
            board = BoardGenerator._placeRandomWaypoints(board, path, intermediateWaypoints)
            board = BoardGenerator._placeRandomWalls(board, path, maxWalls)
            results.append(board)
        
        return results
    
    @staticmethod
    def _generateTwoDistinctRandomPositions(boardSize: int) -> tuple[Position, Position]:
        # select two distinct 1D-indices for the square grid (0 to boardSize-1)
        idxStart, idxEnd = random.sample(range(boardSize * boardSize), 2)

        # project the two 1D-indices to 2D- coordinates (i.e. for a board of size 3: idx = 4 = 0 + 1 * 3 <=> x = idx % 3 = 1; y = idx / 3 = 1)
        start = Position(idxStart % boardSize, idxStart // boardSize)
        end = Position(idxEnd % boardSize, idxEnd // boardSize)

        return start, end
    
    @staticmethod
    def _findHamitonianPath(board: Board, start: Position, end: Position) -> List[Position]:
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
            return path
    
        # will only be reached if start or end are invalid 
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
    def _placeRandomWalls(board: Board, path: List[Position], maxWalls: int) -> Board:
        
        # TODO impl
        return None
    