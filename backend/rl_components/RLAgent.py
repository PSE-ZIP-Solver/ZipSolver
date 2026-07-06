import stable_baselines3 as sb
import gymnasium as gym

class RLAgent:
    """Wraps a Stable-Baselines3 DQN model for training and inference on RLEnvironment."""

    def __init__(self, env: gym.Env, model_path: str | None = None, **dqn_kwargs):
        self._env = env
        self.policy_kwargs = dict(
            features_extractor_class=ZipCNN,
            features_extractor_kwargs=dict(features_dim=128),
            normalize_images=False,
        )
        if model_path is not None:
            self._model = self.load(model_path)
        else:
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

    def save(self, path: str):
        """Save the trained model to disk."""
        self._model.save(path)

    def load(self, path: str) -> sb.DQN:
        """Load a trained model from disk."""
        custom_objects = {
            "policy_kwargs": self.policy_kwargs,
        }
        return sb.DQN.load(path, env=self._env, custom_objects=custom_objects)



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