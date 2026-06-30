from Position import Position

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