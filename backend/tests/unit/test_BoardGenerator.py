import unittest
from offline_training.BoardGenerator import BoardGenerator
from backend.PuzzleLogic import Board, Position

class TestBoardGenerator(unittest.TestCase):

    def setUp(self):
        # We reduce the RESULTS constant for testing purposes to keep tests fast
        BoardGenerator.RESULTS = 1
        self.sizes = [6, 8] # Excl. 7 due to the parity loop mentioned above

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
            
            # Check distinctness
            self.assertNotEqual((start.getX, start.getY), (end.getX, end.getY))
            
            # Check parity (must be different for even boards)
            if size % 2 == 0:
                start_parity = (start.getX + start.getY) % 2
                end_parity = (end.getX + end.getY) % 2
                self.assertNotEqual(start_parity, end_parity, f"Parity failed for size {size}")

    def testFindHamiltonianPath(self):
        """Tests if the path visits every cell exactly once."""
        size = 6
        board = Board(size)
        start, end = BoardGenerator._generateTwoDistinctRandomPositions(size)
        path = BoardGenerator._findHamiltonianPath(board, start, end)
        
        self.assertIsNotNone(path)
        self.assertEqual(len(path), size * size)
        
        # Check for uniqueness of all positions in path
        unique_pos = set((p.getX, p.getY) for p in path)
        self.assertEqual(len(unique_pos), size * size)
        self.assertEqual(path[-1], end)

    def testEdgeCasesPlaceRandomWaypoints(self):
        """Tests _placeRandomWaypoints with 0 and max waypoints."""
        size = 6
        board = Board(size)
        # Mock a simple path for testing (usually needs to be Hamiltonian, but method works on any list)
        path = [Position(x, 0) for x in range(size)] 
        
        # Edge Case: 0 intermediate waypoints (Only Start and End should exist)
        BoardGenerator._placeRandomWaypoints(board, path, 0)
        # Order 1 (Start) and Order 2 (End)
        self.assertEqual(len(board.getWaypoints), 2)

        # Edge Case: Max waypoints
        board_max = Board(size)
        max_wp = size * size # Requesting more than possible
        BoardGenerator._placeRandomWaypoints(board_max, path, max_wp)
        # Start + End + all intermediate points in path
        self.assertEqual(len(board_max.getWaypoints), len(path))

    def testPlaceRandomWalls(self):
        """Tests _placeRandomWalls with 0 and max walls."""
        size = 6
        board = Board(size)
        # Minimal path
        path = [Position(0, 0), Position(1, 0)]
        
        # Edge Case: 0 walls
        BoardGenerator._placeRandomWalls(board, path, 0)
        self.assertEqual(len(board.getWalls), 0)

        # Edge Case: Very high number of walls
        max_possible_walls = (size - 1) * (size - 1)
        BoardGenerator._placeRandomWalls(board, path, max_possible_walls)
        # Should not exceed available grid edges minus path edges
        self.assertLessEqual(len(board.getWalls), max_possible_walls)

    def testPlaceRandomWaypoints(self):
        """Verifies that waypoints are added in the correct order according to the path."""
        size = 6
        board = Board(size)
        path = [Position(0,0), Position(1,0), Position(1,1), Position(0,1)]
        
        # Add 2 intermediate waypoints
        BoardGenerator._placeRandomWaypoints(board, path, 2)
        
        wps = sorted(board.getWaypoints, key=lambda w: w.getOrder)
        
        # Check that the position of waypoint with order 2 comes AFTER order 1 in the path
        for i in range(len(wps) - 1):
            pos_curr = wps[i].getPosition
            pos_next = wps[i+1].getPosition
            
            idx_curr = next(j for j, p in enumerate(path) if p == pos_curr)
            idx_next = next(j for j, p in enumerate(path) if p == pos_next)
            
            self.assertLess(idx_curr, idx_next, f"Waypoint order {wps[i+1].getOrder} appeared before {wps[i].getOrder} in path")

if __name__ == '__main__':
    unittest.main()