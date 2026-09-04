from typing import List, Set, Optional
from .data_models import Position, Waypoint, Wall


class Board:
    """
    Represents the puzzle grid, including its dimensions, walls, and waypoints.

    Responsibility:
        Maintains the layout and structure of a puzzle level. It stores the grid size, 
        tracks placed waypoints and walls, and provides basic spatial checks such as 
        cell adjacency and boundary limits.

    Implementation Details:
        Stores walls in a set for fast lookup and waypoints in a list. Offers helper 
        methods to inspect the grid layout without managing active gameplay state.
    """
    def __init__(self, size: int):
        """
        Initializes a new puzzle board of the given size.

        Args:
            size: The width and height of the square grid.

        Implementation Details:
            Saves the grid size and initializes empty collections for waypoints and walls.
        """
        self._size = size
        self._waypoints: List[Waypoint] = []
        self._walls: Set[Wall] = set()

    def addWaypoint(self, position: Position, order: int):
        """
        Adds a numbered waypoint to the board.

        Args:
            position: The grid position where the waypoint should be placed.
            order: The required visit order for this waypoint.

        Returns:
            None.

        Implementation Details:
            Creates a new Waypoint object with the specified position and order, 
            and appends it to the board's internal waypoints list.
        """
        waypoint = Waypoint(position, order)
        self._waypoints.append(waypoint)

    def addWall(self, cellA: Position, cellB: Position):
        """
        Places a wall between two neighboring cells.

        Args:
            cellA: The position of the first cell.
            cellB: The position of the second cell.

        Returns:
            None.

        Implementation Details:
            Creates a new Wall instance between cellA and cellB and adds it to 
            the internal set of walls, automatically ignoring duplicates.
        """
        wall = Wall(cellA, cellB)
        self._walls.add(wall)

    def isInside(self, position: Position) -> bool:
        """
        Checks whether a position lies within the board boundaries.

        Args:
            position: The position to check.

        Returns:
            True if the position is within the grid limits; False otherwise.

        Implementation Details:
            Checks that both the x and y coordinates are greater than or equal to 0 
            and strictly less than the board size.
        """
        return 0 <= position.getX < self._size and 0 <= position.getY < self._size

    def areAdjacent(self, a: Position, b: Position) -> bool:
        """
        Checks if two positions are directly next to each other horizontally or vertically.

        Args:
            a: The first position.
            b: The second position.

        Returns:
            True if the positions share an edge; False otherwise.

        Implementation Details:
            Calculates the Manhattan distance (|x1 - x2| + |y1 - y2|) between the two 
            points and verifies that it equals exactly 1.
        """
        return abs(a.getX - b.getX) + abs(a.getY - b.getY) == 1

    def hasWallBetween(self, a: Position, b: Position) -> bool:
        """
        Checks if there is a wall between two positions.

        Args:
            a: The first position to check.
            b: The second position to check.

        Returns:
            True if a wall separates the two positions; False otherwise.

        Implementation Details:
            Iterates through the set of walls and checks if any wall connects 
            positions a and b using its direction-agnostic connects() method.
        """
        for wall in self._walls:
            if wall.connects(a, b):
                return True
        return False

    def getWaypointAt(self, position: Position) -> Optional[Waypoint]:
        """
        Finds the waypoint located at a specific position, if one exists.

        Args:
            position: The position to search for.

        Returns:
            The Waypoint at that position, or None if no waypoint is found.

        Implementation Details:
            Iterates through the waypoints list and returns the first waypoint matching 
            the given position, or None if no match is found.
        """
        for wp in self._waypoints:
            if wp.getPosition == position:
                return wp
        return None
    
    def getWaypointByOrder(self, order: int) -> Optional[Waypoint]:
        """
        Finds the waypoint with the specified visit order number.

        Args:
            order: The visit order number to look up.

        Returns:
            The Waypoint with the matching order, or None if not found.

        Implementation Details:
            Iterates through the waypoints list and returns the first waypoint whose 
            order number matches the requested order, or None if not found.
        """
        for wp in self._waypoints:
            if wp.getOrder == order:
                return wp
        return None

    def getAllPositions(self) -> Set[Position]:
        """
        Returns all valid positions that exist on the board.

        Returns:
            A set containing every grid position on the board.

        Implementation Details:
            Iterates through nested loops over row (y) and column (x) ranges from 0 to 
            size - 1, instantiates a Position for each coordinate pair, and collects them into a set.
        """
        positions = set()
        for y in range(self._size):
            for x in range(self._size):
                positions.add(Position(x, y))
        return positions

    def getCellCount(self) -> int:
        """
        Calculates the total number of cells on the board.

        Returns:
            The total cell count (size squared).

        Implementation Details:
            Calculates the total number of grid cells by squaring the grid dimension (size * size).
        """
        return self._size * self._size
    
    @property
    def getSize(self) -> int:
        """
        Gets the size of the board.

        Returns:
            The width and height of the grid.

        Implementation Details:
            Exposes read-only access to the internal size attribute via a property decorator.
        """
        return self._size
    
    @property
    def getWaypoints(self) -> List[Waypoint]:
        """
        Gets the list of all waypoints placed on the board.

        Returns:
            The list of waypoints.

        Implementation Details:
            Exposes read-only access to the internal waypoints list via a property decorator.
        """
        return self._waypoints
    
    @property
    def getWalls(self) -> Set[Wall]:
        """
        Gets the set of all walls placed on the board.

        Returns:
            The set of walls.

        Implementation Details:
            Exposes read-only access to the internal walls set via a property decorator.
        """
        return self._walls