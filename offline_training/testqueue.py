import gymnasium as gym
from stable_baselines3.common.monitor import Monitor

from backend.puzzle_logic import Board
from backend.rl_components import RLAgent, RLEnvironment
from offline_training.board_generator import BoardGenerator
from offline_training.training_result import TrainingResult

test = gym
test2 = RLEnvironment
test3 = RLAgent
test4 = BoardGenerator
test5 = RLEnvironment
test6 = RLAgent
test7 = Board
test8 = TrainingResult
test9 = Monitor

print("testqueue hi")