import Position

class Waypoint:
    def __init__(self, position: Position, order: int):
        self.position = position
        self.order = order