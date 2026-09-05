from typing import List, Set, Optional
from .data_models import Position, Waypoint, Wall


class Board:
    """
    Manages the physical topological blueprint of the puzzle area.

    Responsibility:
        Serves as the structural baseline defining the strict 2D dimensions, specific waypoint
        sequencing targets, and static wall placements that make up a playable puzzle stage.

    Implementation Details:
        Utilizes strict internal encapsulation to track states. Walls are persisted in a hashed
        set to enable extremely fast O(1) membership lookups for movement validations. Waypoints
        are managed continuously within a list to preserve insertion or extraction ordering.
        It provides core geometric checking capabilities but strictly abstains from gameplay tracking.
    """

    def __init__(self, size: int):
        """
        Initializes an empty puzzle stage of the specified cubic dimension.

        Args:
            size: The uniform numerical span (width and height) defining the grid.

        Implementation Details:
            Saves the scalar dimension value into a protected property, sets up an empty sequential
            list to accrue upcoming waypoints, and prepares an empty optimized set to track wall barriers.
        """
        self._size = size
        self._waypoints: List[Waypoint] = []
        self._walls: Set[Wall] = set()

    def addWaypoint(self, position: Position, order: int):
        """
        Appends a sequential milestone constraint to the current puzzle configuration.

        Args:
            position: The exact spatial coordinate to anchor the requirement on.
            order: The required chronological sequencing number.

        Implementation Details:
            Dynamically initializes a new `Waypoint` instance from the supplied metrics
            and appends it strictly to the protected sequential tracking list.
        """
        waypoint = Waypoint(position, order)
        self._waypoints.append(waypoint)

    def addWall(self, cellA: Position, cellB: Position):
        """
        Inserts an impassable internal barrier bridging two distinct cell coordinates.

        Args:
            cellA: The foundation coordinate on one boundary limit.
            cellB: The contiguous coordinate mapping the remaining boundary.

        Implementation Details:
            Instantiates a new uniform `Wall` object. Incorporates it directly into the
            protected hash set, naturally avoiding duplicate boundary entries.
        """
        wall = Wall(cellA, cellB)
        self._walls.add(wall)

    def isInside(self, position: Position) -> bool:
        """
        Validates if a targeted spatial coordinate resides within the permissible physical limits.

        Args:
            position: The mathematical coordinate awaiting verification.

        Returns:
            True if both coordinate axes fit within the stage dimensions, False otherwise.

        Implementation Details:
            Evaluates the underlying top-left origin grid by verifying the target's horizontal
            and vertical axes are identically greater than or equal to 0 while remaining strictly
            inferior to the protected size boundary.
        """
        return 0 <= position.getX < self._size and 0 <= position.getY < self._size

    def areAdjacent(self, a: Position, b: Position) -> bool:
        """
        Determines if two distinct coordinates touch along cardinal axes.

        Args:
            a: The initial coordinate for comparison.
            b: The subsequent coordinate to evaluate.

        Returns:
            True if the locations share an adjoining cardinal edge, False otherwise.

        Implementation Details:
            Extracts property bounds and calculates the absolute Manhattan distance between
            both positions. A direct sum exactly equal to 1 guarantees pure cardinal adjacency
            while actively filtering diagonal or distant attempts.
        """
        return abs(a.getX - b.getX) + abs(a.getY - b.getY) == 1

    def hasWallBetween(self, a: Position, b: Position) -> bool:
        """
        Examines if a definitive physical barrier separates two requested coordinates.

        Args:
            a: The primary adjoining coordinate to check.
            b: The corresponding bordering coordinate to test against.

        Returns:
            True if an impassable blockage resides directly across the adjoining space.

        Implementation Details:
            Iterates fully over the protected hashed wall compilation, triggering the intrinsic
            direction-agnostic `connects` query on each barrier to hunt for absolute matches.
        """
        for wall in self._walls:
            if wall.connects(a, b):
                return True
        return False

    def getWaypointAt(self, position: Position) -> Optional[Waypoint]:
        """
        Retrieves a specifically requested milestone constrained at a localized coordinate.

        Args:
            position: The physical focal coordinate awaiting lookup.

        Returns:
            The located waypoint entity, or None if the designated cell is barren.

        Implementation Details:
            Performs a continuous linear sweep over the protected sequential waypoint collection.
            Cross-references physical location properties, instantly terminating and yielding upon discovery.
        """
        for wp in self._waypoints:
            if wp.getPosition == position:
                return wp
        return None

    def getWaypointByOrder(self, order: int) -> Optional[Waypoint]:
        """
        Extracts a specific milestone requirement based on its numerical sequence sequence.

        Args:
            order: The rigid numerical target to hunt for within the blueprint.

        Returns:
            The associated milestone enforcing the target sequence, or None if omitted.

        Implementation Details:
            Engages in a linear scan across the protected internal lists, inspecting chronological
            requirements via property decorators and returning upon the first rigid correlation.
        """
        for wp in self._waypoints:
            if wp.getOrder == order:
                return wp
        return None

    def getAllPositions(self) -> Set[Position]:
        """
        Compiles and yields an exhaustive collection of every valid traversable grid coordinate.

        Returns:
            A populated hash set containing coordinate instances scaling across the entire area.

        Implementation Details:
            Executes nested iterations over the bounding uniform grid size to procedurally
            instantiate fresh position components. Collects and yields these elements encapsulated
            within a natively hashed set structure to facilitate O(1) validations.
        """
        positions = set()
        for y in range(self._size):
            for x in range(self._size):
                positions.add(Position(x, y))
        return positions

    def getCellCount(self) -> int:
        """
        Calculates the complete cumulative volume of traversable cells comprising the grid.

        Returns:
            The mathematically total quantity of usable grid coordinates.

        Implementation Details:
            Multiplies the rigidly protected size boundaries symmetrically (n * n) to quickly
            quantify full Hamiltonian pathway lengths.
        """
        return self._size * self._size

    @property
    def getSize(self) -> int:
        """
        Retrieves the definitive linear edge boundary dimension.

        Returns:
            The absolute dimensional magnitude of a single edge axis.

        Implementation Details:
            Provides immutable exterior access to the rigidly encapsulated size boundary value.
        """
        return self._size

    @property
    def getWaypoints(self) -> List[Waypoint]:
        """
        Yields the full ongoing sequential compilation of required milestone cells.

        Returns:
            The linear collection outlining every configured sequenced target.

        Implementation Details:
            Unlocks superficial access to the protected internal list managing rigid constraints.
        """
        return self._waypoints

    @property
    def getWalls(self) -> Set[Wall]:
        """
        Returns the extensive internal collection of every physical grid barricade.

        Returns:
            A distinct hashed structure tracking all established coordinate bounds.

        Implementation Details:
            Unlocks localized read-access to the internally governed barricade mappings via property decorators.
        """
        return self._walls
