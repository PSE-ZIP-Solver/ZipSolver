import stable_baselines3 as sb
import gymnasium as gym
from backend.rl_components.RLEnvironment import RLEnvironment

class RLAgent:
    """Wraps a Stable-Baselines3 DQN model for training and inference on RLEnvironment."""

    def __init__(self, env: RLEnvironment, model_path: str | None = None, **dqn_kwargs):
        self._env = env
        self.policy_kwargs = dict(
            features_extractor_class=ZipCNN,
            features_extractor_kwargs=dict(features_dim=128),
            normalize_images=False,
        )
        if model_path is not None:
            self._model = self.load(model_path)
        else:
            dqn_kwargs.setdefault("exploration_initial_eps", 1.0)
            dqn_kwargs.setdefault("exploration_final_eps", 0.2)
            dqn_kwargs.setdefault("exploration_fraction", 0.7)
            dqn_kwargs.setdefault("learning_starts", 100)

            self._model = sb.DQN(
                policy="CnnPolicy",
                env=self._env,
                policy_kwargs=self.policy_kwargs,
                verbose=1,
                **dqn_kwargs,
            )

    def predict(self, observation, deterministic: bool = True):
        """Return the action the agent chooses for a given observation."""
        action, _state = self._model.predict(observation, deterministic=deterministic)
        return action
    
    def learn(self, total_timesteps: int, reset_num_timesteps: bool = True):
        """Train the model for the given amount of timesteps."""
        self._model.learn(
            total_timesteps=total_timesteps,
            reset_num_timesteps=reset_num_timesteps
        )
        return self
    
    def set_env(self, env: gym.Env):
        """Switch the environment used by the wrapped model."""
        self._env = env
        self._model.set_env(env)

    def save(self, path: str):
        """Save the trained model to disk."""
        self._model.save(path)

    def load(self, path: str) -> sb.DQN:
        """Load a trained model from disk."""
        custom_objects = {
            "policy_kwargs": self.policy_kwargs,
        }
        return sb.DQN.load(path, env=self._env, custom_objects=custom_objects)

    def solve(
            self,
            deterministic: bool = True,
            max_steps: int = 99999,
            render: bool = True):
        """Run the agent on the current environment until it solves the board,
        fails, or hits the step limit.

        Args:
            deterministic (bool): Whether to use deterministic action selection.
            max_steps (int | None): Hard cap on steps; falls back to the
                environment's own configured max_steps if not provided.
            render (bool): Whether to capture rendered states along the way.

        Returns:
            dict: Summary of the rollout, including whether the board was solved.
        """
        options = {}
        observation, info = self._env.reset()

        step_limit = max_steps
        if step_limit <= 0:
            raise ValueError("max_steps must be > 0.")

        terminated = False
        truncated = False
        total_reward = 0.0
        actions: list[int] = []
        states: list[str] = []

        for _ in range(step_limit):
            if render:
                self._env.render()

            action = self.predict(observation, deterministic=deterministic)
            action_int = int(action)
            actions.append(action_int)

            observation, reward, terminated, truncated, info = self._env.step(action_int)
            total_reward += float(reward)

            if terminated or truncated:
                break

        if render:
            self._env.render()

        solved = terminated and self._env.game.isFinished()
        return {
            "solved": solved,
            "truncated": truncated,
            "total_reward": total_reward,
            "actions": actions,
            "final_info": info,
            "states": states,
        }


# CUSTOM NEW CLASS FOR CUSTOM CNN POLICY INSTEAD OF MLP POLICY
# basically turns the obs space's 7 channels and compacts it to a list of 128 numbers that 'summarize' the grid
# Normally CNN is for image-input but we treat the 7 channels as a stacked 7 layer image
import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class ZipCNN(BaseFeaturesExtractor):
    """Small CNN feature extractor sized for 6x6-8x8 multi-channel grid observations."""

    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 128):
        super().__init__(observation_space, features_dim)

        n_input_channels = observation_space.shape[0]  # 7

        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
        )

        # compute flattened size dynamically so this works across board sizes
        with torch.no_grad():
            sample = torch.zeros(1, *observation_space.shape)
            n_flatten = self.cnn(sample).shape[1]

        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        return self.linear(self.cnn(observations))