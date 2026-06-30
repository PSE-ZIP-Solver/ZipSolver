from backend.PuzzleLogic import Board
import random

# number of results to generate
RESULTS = 1000

class BoardGenerator:
    @staticmethod
    def generate(boardSize: int, waypoints: int, walls: int):
        boards = list()