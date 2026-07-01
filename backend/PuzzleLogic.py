from typing import List, Set, Optional


class Position:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def setX(self, value: int):
        self._x = value
    
    def setY(self, value: int):
        self._y = value    

    @property
    def getX(self) -> int:
        return self._x
    
    @property
    def getY(self) -> int:
        return self._y

    def __eq__(self, other):
        return isinstance(other, Position) and self._x == other._x and self._y == other._y
    
    def __hash__(self):
        return hash((self._x, self._y))


class Waypoint:
    def __init__(self, position: Position, order: int):
        self._position = position
        self._order = order

    @property
    def getPosition(self) -> Position:
        return self._position
    
    @property
    def getOrder(self) -> Position:
        return self._order
    

class Wall:
    def __init__(self, a: Position, b: Position):
        self._cellA = a
        self._cellB = b

    @property
    def getCellA(self) -> Position:
        return self._cellA

    @property
    def getCellB(self) -> Position:
        return self._cellB
    
    def connects(self, a: Position, b: Position) -> bool:
        return (self._cellA == a and self._cellB == b) or (self._cellA == b and self._cellB == a)
    
    def __eq__(self, other):
        return  isinstance(other, Wall) and self.connects(other._cellA, other._cellB)
    
    def __hash__(self):
        cells = sorted([(self._cellA.getX, self._cellA.getY), (self._cellB.getX, self._cellB.getY)])
        return hash(tuple(cells))


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
