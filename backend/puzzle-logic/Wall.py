import Position

class Wall:
    def __init__(self, a: Position, b: Position):
        self._cellA = a
        self._cellB = b

    def connects(self, a: Position, b: Position):
        return (self._cellA == a and self._cellB == b) or (self._cellA == b and self._cellB == a)
    
    def __eq__(self, other):
        if not isinstance(other, Wall):
            return False
        else:
            return self.connects(other._cellA, other._cellB)