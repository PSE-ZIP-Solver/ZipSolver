import gymnasium as gym
import stable_baselines3 as sb
import torch
import torch.nn as nn

from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.utils import get_linear_fn
from stable_baselines3.common.vec_env import SubprocVecEnv


class ZipCNN_Deep(BaseFeaturesExtractor):
    """Deep CNN feature extractor for complex 8x8 grid routing."""

    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 512):
        super().__init__(observation_space, features_dim)

        n_input_channels = observation_space.shape[0]  # 8 channels

        self.cnn = nn.Sequential(
            # Layer 1: Startschicht erweitert auf 64 Filter
            nn.Conv2d(n_input_channels, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),

            # Layer 2: Erweiterung auf 128 Filter für tiefere Muster
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),

            # Layer 3: Konsolidierung räumlicher Features
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),

            # Layer 4: NEU - Zwingend nötig für weitreichende Dead-End-Erkennung
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),

            nn.Flatten(),
        )

        # Berechne Flatten-Größe dynamisch (wird 128 * 8 * 8 = 8192 sein)
        with torch.no_grad():
            sample = torch.zeros(1, *observation_space.shape)
            n_flatten = self.cnn(sample).shape[1]

        # Größeres Fully-Connected-Netzwerk hinten dran, um die 8192 Features gut zu verarbeiten
        self.linear = nn.Sequential(
            nn.Linear(n_flatten, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        return self.linear(self.cnn(observations))


class RLAgent:
    """Wraps a Stable-Baselines3 DQN model for training and inference."""

    def __init__(self, env: SubprocVecEnv, model_path: str | None = None, **dqn_kwargs):
        self._env = env

        self.policy_kwargs = dict(
            features_extractor_class=ZipCNN_Deep,
            # 1. Match the new dimension from the optimized ZipCNN
            features_extractor_kwargs=dict(features_dim=512),
            # 2. Add dense layers for the Q-network to process the CNN features
            net_arch=[512, 256],
            normalize_images=False,
        )

        if model_path is not None:
            self._model = self.load(model_path, **dqn_kwargs)
        else:
            dqn_kwargs.setdefault("exploration_initial_eps", 1.0)
            dqn_kwargs.setdefault("exploration_final_eps", 0.05)
            dqn_kwargs.setdefault("exploration_fraction", 0.5)
            dqn_kwargs.setdefault("learning_starts", 2_000)

            self._model = sb.DQN(
                policy="CnnPolicy",
                env=self._env,
                policy_kwargs=self.policy_kwargs,
                verbose=1,
                device="auto",
                **dqn_kwargs,
            )

    def set_exploration_schedule(
        self,
        initial_eps: float = 1.0,
        final_eps: float = 0.05,
        fraction: float = 0.5,
    ):
        """Set a new linear exploration schedule."""
        self._model.exploration_initial_eps = initial_eps
        self._model.exploration_final_eps = final_eps
        self._model.exploration_fraction = fraction
        self._model.exploration_schedule = get_linear_fn(
            initial_eps,
            final_eps,
            fraction,
        )
        self._model.exploration_rate = initial_eps

    def predict(self, observation, deterministic: bool = True):
        """Return the action the agent chooses for a given observation."""
        action, _state = self._model.predict(
            observation,
            deterministic=deterministic,
        )
        return action

    def learn(self, total_timesteps: int, reset_num_timesteps: bool = True):
        """Train the model for the given amount of timesteps."""
        self._model.learn(
            total_timesteps=total_timesteps,
            reset_num_timesteps=reset_num_timesteps,
        )
        return self

    def set_env(self, env: gym.Env):
        """Switch the environment used by the wrapped model."""
        self._env = env
        self._model.set_env(env)

    def save(self, path: str):
        """Save the trained model to disk."""
        self._model.save(path)

    def load(self, path: str, **dqn_kwargs) -> sb.DQN:
        """Load a trained model from disk."""
        custom_objects = {
            "policy_kwargs": self.policy_kwargs,
        }

        return sb.DQN.load(
            path,
            env=self._env,
            custom_objects=custom_objects,
            device="auto",
            **dqn_kwargs,
        )

    def solve(
        self,
        deterministic: bool = True,
        max_steps: int = 99999,
        render: bool = True,
    ):
        """Run the agent on the current environment until it solves or fails."""
        observation, info = self._env.reset()

        if max_steps <= 0:
            raise ValueError("max_steps must be > 0.")

        terminated = False
        truncated = False
        total_reward = 0.0
        actions: list[int] = []
        states: list[str] = []

        for _ in range(max_steps):
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

        solved = terminated and self._is_current_env_finished()

        return {
            "solved": solved,
            "truncated": truncated,
            "total_reward": total_reward,
            "actions": actions,
            "final_info": info,
            "states": states,
        }

    def _is_current_env_finished(self) -> bool:
        """Check whether the currently assigned environment finished the puzzle."""
        if hasattr(self._env, "game"):
            return self._env.game.isFinished()

        if hasattr(self._env, "env") and hasattr(self._env.env, "game"):
            return self._env.env.game.isFinished()

        return False