
class Position:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

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
    def getOrder(self) -> int:
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