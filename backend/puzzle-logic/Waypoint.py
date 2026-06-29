import Position

class Waypoint:
    def __init__(self, position: Position, order: int):
        self._position = position
        self._order = order