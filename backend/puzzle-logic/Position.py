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
        return isinstance(other, Position) and self._x == other._x() and self._y == other._y()
    
    def __hash__(self):
        return hash((self._x, self._y))