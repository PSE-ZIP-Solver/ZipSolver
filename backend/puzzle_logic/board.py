from typing import List, Set, Optional
from .models import Position, Waypoint, Wall


class Board:
    def __init__(self, size: int):
        self._size = size
        self._waypoints: List[Waypoint] = []
        self._walls: Set[Wall] = set()

    def addWaypoint(self, position: Position, order: int):
        waypoint = Waypoint(position, order)
        self._waypoints.append(waypoint)

    def addWall(self, cellA: Position, cellB: Position):
        wall = Wall(cellA, cellB)
        self._walls.add(wall)

    def isInside(self, position: Position) -> bool:
        return 0 <= position.getX < self._size and 0 <= position.getY < self._size

    def areAdjacent(self, a: Position, b: Position) -> bool:
        return abs(a.getX - b.getX) + abs(a.getY - b.getY) == 1

    def hasWallBetween(self, a: Position, b: Position) -> bool:
        for wall in self._walls:
            if wall.connects(a, b):
                return True
        return False

    def getWaypointAt(self, position: Position) -> Optional[Waypoint]:
        for wp in self._waypoints:
            if wp.getPosition == position:
                return wp
        return None
    
    def getWaypointByOrder(self, order: int) -> Optional[Waypoint]:
        for wp in self._waypoints:
            if wp.getOrder == order:
                return wp
        return None

    def getAllPositions(self) -> Set[Position]:
        positions = set()
        for y in range(self._size):
            for x in range(self._size):
                positions.add(Position(x, y))
        return positions

    def getCellCount(self) -> int:
        return self._size * self._size
    
    @property
    def getSize(self) -> int:
        return self._size
    
    @property
    def getWaypoints(self) -> List[Waypoint]:
        return self._waypoints
    
    @property
    def getWalls(self) -> Set[Wall]:
        return self._walls
