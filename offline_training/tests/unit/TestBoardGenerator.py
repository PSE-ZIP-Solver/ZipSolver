import unittest
from offline_training.BoardGenerator import BoardGenerator
from backend.PuzzleLogic import Board, Position

class TestBoardGenerator(unittest.TestCase):

    def setUp(self):
        # Reduce RESULTS for faster testing
        BoardGenerator.RESULTS = 1
        # Now including size 7 as the parity logic is fixed
        self.sizes = [6, 7, 8] 

    def testGenerate(self):
        """Tests the main entry point for different sizes and basic constraints."""
        for size in self.sizes:
            # Test with moderate waypoints and walls
            results = BoardGenerator.generate(size, 5, 5)
            self.assertEqual(len(results), 1)
            self.assertIsInstance(results[0], Board)
            self.assertEqual(results[0].getSize, size)

    def testGenerateTwoDistinctRandomPositions(self):
        """Tests _generateTwoDistinctRandomPositions logic and parity."""
        for size in self.sizes:
            start, end = BoardGenerator._generateTwoDistinctRandomPositions(size)
            self.assertNotEqual(start, end)
            
            p_start = (start.getX + start.getY) % 2
            p_end = (end.getX + end.getY) % 2
            
            if size % 2 == 0:
                # Even: different parity
                self.assertNotEqual(p_start, p_end)
            else:
                # Odd: both must be parity 0 (majority color)
                self.assertEqual(p_start, 0)
                self.assertEqual(p_end, 0)

    def testFindHamiltonianPath(self):
        """Tests if the path visits every cell exactly once."""
        size = 6
        board = Board(size)
        start, end = BoardGenerator._generateTwoDistinctRandomPositions(size)
        path = BoardGenerator._findHamiltonianPath(board, start, end)
        
        self.assertIsNotNone(path)
        self.assertEqual(len(path), size * size)
        
        # Check for uniqueness using the class's built-in __hash__
        self.assertEqual(len(set(path)), size * size)
        self.assertEqual(path[-1], end)

    def testEdgeCasesPlaceRandomWaypoints(self):
        """Tests _placeRandomWaypoints with 0 and max waypoints."""
        size = 6
        board = Board(size)
        path = [Position(x, 0) for x in range(size)] 
        
        # 0 intermediate waypoints -> 2 total (Start/End)
        BoardGenerator._placeRandomWaypoints(board, path, 0)
        self.assertEqual(len(board.getWaypoints), 2)

        # Max waypoints -> All cells in path become waypoints
        board_max = Board(size)
        BoardGenerator._placeRandomWaypoints(board_max, path, 1000) 
        self.assertEqual(len(board_max.getWaypoints), len(path))

    def testPlaceRandomWalls(self):
        """Tests _placeRandomWalls with 0 and unrealistic wall counts."""
        size = 6
        board = Board(size)
        path = [Position(0, 0), Position(1, 0)]
        
        # 0 walls
        BoardGenerator._placeRandomWalls(board, path, 0)
        self.assertEqual(len(board.getWalls), 0)

        # Excess walls (should be capped safely)
        BoardGenerator._placeRandomWalls(board, path, 500)
        max_possible = (2 * size * (size - 1)) - (len(path) - 1)
        self.assertLessEqual(len(board.getWalls), max_possible)

    def testWaypointOrdering(self):
        """Verifies waypoints are in ascending order relative to the path sequence."""
        size = 6
        board = Board(size)
        path = [Position(0,0), Position(1,0), Position(1,1), Position(0,1), Position(0,2)]
        
        BoardGenerator._placeRandomWaypoints(board, path, 2)
        wps = sorted(board.getWaypoints, key=lambda w: w.getOrder)
        
        # Verify continuous ordering (1, 2, 3...)
        for i, wp in enumerate(wps):
            self.assertEqual(wp.getOrder, i + 1)

        # Verify path sequence
        for i in range(len(wps) - 1):
            idx_curr = path.index(wps[i].getPosition)
            idx_next = path.index(wps[i+1].getPosition)
            self.assertLess(idx_curr, idx_next)

if __name__ == '__main__':
    unittest.main()