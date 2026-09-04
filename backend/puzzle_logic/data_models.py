class Position:
    """
    Represents a coordinate on the puzzle grid.

    Responsibility:
        Identifies a specific cell on the board using column (x) and row (y) indices, 
        making it easy to track locations, check adjacency, and compare positions.

    Implementation Details:
        Uses a coordinate system where (0, 0) is the top-left corner. Stores x and y 
        internally and implements equality and hash methods so positions can be compared 
        by value and stored in sets or dictionaries.
    """
    def __init__(self, x: int, y: int):
        """
        Creates a new position on the grid.

        Args:
            x: The column index.
            y: The row index.

        Implementation Details:
            Stores the x and y coordinates in internal attributes.
        """
        self._x = x
        self._y = y

    @property
    def getX(self) -> int:
        """
        Gets the column index of this position.

        Returns:
            The x coordinate.

        Implementation Details:
            Returns the internal horizontal coordinate.
        """
        return self._x
    
    @property
    def getY(self) -> int:
        """
        Gets the row index of this position.

        Returns:
            The y coordinate.

        Implementation Details:
            Returns the internal vertical coordinate.
        """
        return self._y

    def __eq__(self, other):
        """
        Checks if another object represents the same grid position.

        Args:
            other: The object to compare with.

        Returns:
            True if other is a Position with the same x and y coordinates; False otherwise.

        Implementation Details:
            Verifies that other is a Position instance using isinstance, then checks that both 
            x and y coordinates match.
        """
        return isinstance(other, Position) and self._x == other._x and self._y == other._y
    
    def __hash__(self):
        """
        Computes a hash value based on the x and y coordinates.

        Returns:
            An integer hash representing this position.

        Implementation Details:
            Packs the x and y coordinates into a tuple (x, y) and computes its hash using 
            Python's built-in hash function.
        """
        return hash((self._x, self._y))


class Waypoint:
    """
    Represents a numbered waypoint that must be visited in order.

    Responsibility:
        Connects a grid position with a number indicating when that cell must be 
        visited in the solution path.

    Implementation Details:
        Stores the position and its visit order internally, providing read-only 
        properties to keep the waypoint data unchanged.
    """
    def __init__(self, position: Position, order: int):
        """
        Creates a new waypoint at the specified position and visit order.

        Args:
            position: The grid position of the waypoint.
            order: The number indicating when this waypoint should be visited.

        Implementation Details:
            Stores the position and order values in internal attributes.
        """
        self._position = position
        self._order = order

    @property
    def getPosition(self) -> Position:
        """
        Gets the grid position of the waypoint.

        Returns:
            The position of the waypoint.

        Implementation Details:
            Returns the internal position object.
        """
        return self._position
    
    @property
    def getOrder(self) -> int:
        """
        Gets the required visit order of the waypoint.

        Returns:
            The order number of the waypoint.

        Implementation Details:
            Returns the internal order value.
        """
        return self._order
    

class Wall:
    """
    Represents a barrier between two adjacent grid cells that blocks movement.

    Responsibility:
        Defines an obstacle between two neighboring cells so players and solvers 
        cannot move directly between them.

    Implementation Details:
        Treats the barrier as bidirectional, meaning a wall between A and B is the 
        same as between B and A. Implements equality and hashing so walls can be 
        compared and stored in sets regardless of cell order.
    """
    def __init__(self, a: Position, b: Position):
        """
        Creates a wall between two grid cells.

        Args:
            a: The position of the cell on one side of the wall.
            b: The position of the cell on the other side of the wall.

        Implementation Details:
            Stores both cell positions in internal attributes.
        """
        self._cellA = a
        self._cellB = b

    @property
    def getCellA(self) -> Position:
        """
        Gets the first cell bordering this wall.

        Returns:
            The position of the first cell.

        Implementation Details:
            Returns the internal reference to the first cell.
        """
        return self._cellA

    @property
    def getCellB(self) -> Position:
        """
        Gets the second cell bordering this wall.

        Returns:
            The position of the second cell.

        Implementation Details:
            Returns the internal reference to the second cell.
        """
        return self._cellB
    
    def connects(self, a: Position, b: Position) -> bool:
        """
        Checks if this wall sits between two specific positions.

        Args:
            a: The first position to check.
            b: The second position to check.

        Returns:
            True if the wall separates positions a and b; False otherwise.

        Implementation Details:
            Performs a bidirectional check: verifies if either (cellA equals a and cellB equals b) 
            or (cellA equals b and cellB equals a).
        """
        return (self._cellA == a and self._cellB == b) or (self._cellA == b and self._cellB == a)
    
    def __eq__(self, other):
        """
        Checks if another object represents the same wall.

        Args:
            other: The object to compare with.

        Returns:
            True if other is a Wall separating the same two cells; False otherwise.

        Implementation Details:
            Verifies that other is a Wall instance using isinstance and delegates to connects() 
            to compare the bordering cells regardless of direction.
        """
        return  isinstance(other, Wall) and self.connects(other._cellA, other._cellB)
    
    def __hash__(self):
        """
        Computes a hash value for the wall regardless of cell order.

        Returns:
            An integer hash for this wall.

        Implementation Details:
            Extracts the (x, y) coordinates of both cells, sorts them so order does not matter, 
            and hashes the resulting tuple using Python's built-in hash function.
        """
        cells = sorted([(self._cellA.getX, self._cellA.getY), (self._cellB.getX, self._cellB.getY)])
        return hash(tuple(cells))