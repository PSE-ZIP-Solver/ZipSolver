class Position:
    """
    Represents a specific two-dimensional coordinate on the puzzle grid.

    Responsibility:
        Provides a standardized mathematical representation for grid cells, allowing other
        game components to pinpoint locations, determine spatial adjacency, and define physical boundaries.

    Implementation Details:
        Follows a strict Top-Left origin (0, 0) coordinate system. The x-axis represents columns
        (horizontal) and the y-axis represents rows (vertical). Encapsulates state within protected
        attributes and overrides native equality and hashing methods to enable value-based comparisons
        and seamless integration within hash-based collections.
    """

    def __init__(self, x: int, y: int):
        """
        Initializes a spatial coordinate on the grid.

        Args:
            x: The horizontal column index.
            y: The vertical row index.

        Implementation Details:
            Assigns the provided integer coordinates directly into protected internal attributes
            to enforce strict encapsulation principles.
        """
        self._x = x
        self._y = y

    @property
    def getX(self) -> int:
        """
        Retrieves the horizontal column coordinate.

        Returns:
            The horizontal axis value.

        Implementation Details:
            Exposes read-only access to the protected horizontal coordinate attribute via
            a property decorator.
        """
        return self._x

    @property
    def getY(self) -> int:
        """
        Retrieves the vertical row coordinate.

        Returns:
            The vertical axis value.

        Implementation Details:
            Exposes read-only access to the protected vertical coordinate attribute via
            a property decorator.
        """
        return self._y

    def __eq__(self, other):
        """
        Evaluates whether this position is spatially identical to another object.

        Args:
            other: The instance to compare against.

        Returns:
            True if the other object is a valid position with identical physical coordinates, False otherwise.

        Implementation Details:
            Employs `isinstance` to ensure safe, fail-fast type comparison, then cross-references
            exact equality between the encapsulated horizontal and vertical attributes of both instances.
        """
        return (
            isinstance(other, Position) and self._x == other._x and self._y == other._y
        )

    def __hash__(self):
        """
        Generates a unique deterministic hash value for the spatial coordinate.

        Returns:
            The integer hash representation of the coordinate sequence.

        Implementation Details:
            Packs the protected internal attributes into a strictly ordered tuple and evaluates
            it using the native Python `hash()` function.
        """
        return hash((self._x, self._y))


class Waypoint:
    """
    Represents a mandatory milestone cell on the grid that must be traversed.

    Responsibility:
        Associates a specific spatial coordinate with a strict numerical sequence, dictating
        the exact chronological order in which the player must visit it to formulate a valid path.

    Implementation Details:
        Maintains strict state integrity by storing positional tracking and ordering logic internally.
        Relies purely on properties for read-only access to guarantee immutability throughout
        the application's lifecycle.
    """

    def __init__(self, position: Position, order: int):
        """
        Initializes a new sequential milestone constraint.

        Args:
            position: The exact spatial coordinate configuring the milestone's physical location.
            order: The required chronological numerical sequence value.

        Implementation Details:
            Captures the coordinate instance and sequence requirement, safely housing them
            within protected attributes.
        """
        self._position = position
        self._order = order

    @property
    def getPosition(self) -> Position:
        """
        Retrieves the physical location of the waypoint.

        Returns:
            The spatial coordinate of the cell containing the milestone.

        Implementation Details:
            Exposes read-only access to the protected coordinate object via a property decorator.
        """
        return self._position

    @property
    def getOrder(self) -> int:
        """
        Retrieves the required chronological sequence number.

        Returns:
            The strict numerical target value of the waypoint.

        Implementation Details:
            Exposes read-only access to the protected sequence sequence attribute via a property decorator.
        """
        return self._order


class Wall:
    """
    Represents an impassable physical barrier between two directly adjacent grid cells.

    Responsibility:
        Defines non-traversable boundaries internal to the grid that the Hamiltonian path
        must dynamically route around, preventing illegal coordinate movements.

    Implementation Details:
        Engineered to be entirely direction-agnostic. Safely encapsulates the two neighboring
        coordinates it separates and implements specific hashing logic to guarantee that a wall
        defining A-to-B is mathematically identical to B-to-A during complex rule validations.
    """

    def __init__(self, a: Position, b: Position):
        """
        Initializes a definitive physical barrier separating two coordinates.

        Args:
            a: The foundational coordinate on one side of the barrier.
            b: The neighboring coordinate on the opposite side.

        Implementation Details:
            Captures and isolates the boundary definitions strictly within protected cell attributes.
        """
        self._cellA = a
        self._cellB = b

    @property
    def getCellA(self) -> Position:
        """
        Retrieves the first bordering coordinate of this wall.

        Returns:
            The primary spatial coordinate location.

        Implementation Details:
            Exposes read-only access to the primary boundary definition via a property decorator.
        """
        return self._cellA

    @property
    def getCellB(self) -> Position:
        """
        Retrieves the second bordering coordinate of this wall.

        Returns:
            The secondary spatial coordinate location.

        Implementation Details:
            Exposes read-only access to the secondary boundary definition via a property decorator.
        """
        return self._cellB

    def connects(self, a: Position, b: Position) -> bool:
        """
        Determines if this wall directly separates a specific pair of coordinates.

        Args:
            a: The preliminary spatial coordinate to test.
            b: The subsequent spatial coordinate to test.

        Returns:
            A boolean indicating if the barrier spans exactly between the provided points.

        Implementation Details:
            Checks both possible bidirectional pairings (A-to-B and B-to-A) against the
            encapsulated properties, ensuring the validation logic remains inherently
            directionless and safe for all pathing algorithms.
        """
        return (self._cellA == a and self._cellB == b) or (
            self._cellA == b and self._cellB == a
        )

    def __eq__(self, other):
        """
        Evaluates whether this barrier is physically identical to another object.

        Args:
            other: The secondary instance to compare against.

        Returns:
            True if the other object is a wall occupying the exact same inter-cell space.

        Implementation Details:
            Leverages defensive type checking via `isinstance`, then invokes the internal
            direction-agnostic `connects` method to cross-reference boundary definitions.
        """
        return isinstance(other, Wall) and self.connects(other._cellA, other._cellB)

    def __hash__(self):
        """
        Computes a consistent, uniform hash for the boundary regardless of initial cell order.

        Returns:
            The deterministic integer hash value corresponding to the wall's location.

        Implementation Details:
            Extracts coordinate data manually via property getters, packs them into lexicographically
            sorted tuples to guarantee deterministic ordering, and hashes the resulting frozen structure.
        """
        cells = sorted(
            [(self._cellA.getX, self._cellA.getY), (self._cellB.getX, self._cellB.getY)]
        )
        return hash(tuple(cells))
