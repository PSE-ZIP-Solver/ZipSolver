from backend.puzzle_logic import Position
from typing import List

class SolutionPath:
    def __init__(self):
        self._positions: List[Position] = []

    def add(self, position: Position):
        self._positions.append(position)

    @property
    def getPostions(self) -> List[Position]:
        return self._positions