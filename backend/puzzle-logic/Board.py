import Position
import Waypoint
import Wall

class Board:
    def __init__(self, size: int):
        self._size = size
        self._waypoints = list()
        self._walls = set()

    def addWaypoint(self, position: Position, order: int):
        waypoint = Waypoint(position, order)
        self._waypoints.append(waypoint)

    def addWall(self, cellA: Position, cellB: Position):
        wall = Wall(cellA, cellB)
        self._walls.add(wall)

    def isInside(self, position: Position) -> bool:
        return 0 <= position.getX() < self._size and 0 <= position.getY() < self._size

    def areAdjacent(self, a: Position, b: Position) -> bool:
        return abs(a.x - b.x) + abs(a.y - b.y) == 1

    def hasWallBetween(self, a: Position, b: Position) -> bool:
        for wall in self._walls:
            if wall.connects(a, b):
                return True
        return False

    def getWaypointAt(self, position: Position)-> Waypoint:
        for wp in self._waypoints:
            if wp.position.equals(position):
                return wp
        return None
    
    def getWaypointByOrder(self, order: int) -> Waypoint:
        for wp in self._waypoints:
            if wp.order == order:
                return wp
        return None

    def getAllPositions(self):
        positions = set()
        for y in range(self._size):
            for x in range(self._size):
                positions.add(Position(x, y))
        return positions

    def getCellCount(self) -> int:
        return self._size * self._size