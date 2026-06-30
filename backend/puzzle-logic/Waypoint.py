from Position import Position

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