class Position:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self._x == other._x and self._y == other._y