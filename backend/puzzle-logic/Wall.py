import Position

class Wall:
    def __init__(self, a: Position, b: Position):
        self.cellA = a
        self.cellB = b

    def connects(self, a: Position, b: Position) -> bool:
        return (self.cellA == a and self.cellB == b) or (self.cellA == b and self.cellB == a)
    
    def __eq__(self, other):
        return  isinstance(other, Wall) and self.connects(other.cellA, other.cellB)