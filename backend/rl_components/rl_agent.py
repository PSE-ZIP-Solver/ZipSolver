import gymnasium as gym
import stable_baselines3 as sb
import torch
import torch.nn as nn

from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.utils import get_linear_fn


class ZipCNN(BaseFeaturesExtractor):
    """
    Small CNN feature extractor for multi-channel grid observations.

    Responsibility:
        Serves as the foundational vision extraction architecture, analyzing the 8-channel
        spatial tensor matrices to identify localized physical walls, boundaries, and chronological
        markers for the overarching reinforcement network.

    Implementation Details:
        Inherits dynamically from Stable-Baselines3's BaseFeaturesExtractor. Implements a
        multi-stage 2D Convolutional Neural Network layered via `nn.Sequential` using `ReLU` activations.
        Crucially, uses a detached dummy tensor pass directly during instantiation to dynamically
        calculate the exact flattened dimensional mapping, allowing the network architecture to scale
        automatically regardless of whether it evaluates 6x6, 7x7, or 8x8 matrices.
    """

    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 128):
        """
        Initializes the convolutional parameters and dynamic dense layers.

        Args:
            observation_space: The strict dimensional limits and shapes defined by the environment.
            features_dim: The scalar parameter driving the concluding dense output layer size.

        Implementation Details:
            Extracts strict input channel limits explicitly defining deep padding loops to preserve
            architectural shapes across sequential strides. Forces a `torch.no_grad()` execution
            pass pushing zeroed inputs across the convolutions to seamlessly infer the exact flattened
            dimension size before permanently cementing the concluding linear classifier blocks.
        """
        super().__init__(observation_space, features_dim)

        n_input_channels = observation_space.shape[0]  # 8 channels currently

        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute flattened size dynamically so this works across board sizes.
        with torch.no_grad():
            sample = torch.zeros(1, *observation_space.shape)
            n_flatten = self.cnn(sample).shape[1]

        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        """
        Calculates the active structural propagation routing incoming matrix blocks.

        Args:
            observations: The active batched tensor mappings describing geometric states.

        Returns:
            The purely dense flattened feature tensor directly utilized by subsequent DQN pipelines.

        Implementation Details:
            Passes input mappings sequentially via raw PyTorch invocation blocks connecting
            spatial convolutions explicitly into final rectified linear layers.
        """
        return self.linear(self.cnn(observations))


class RLAgent:
    """
    Wraps a Stable-Baselines3 DQN model for training and inference.

    Responsibility:
        Functions as the high-level orchestration interface governing the complete lifecycle
        of the neural predictive agent. Secures network configurations, executes exploration
        schedules, and translates raw environmental states into active policy predictions.

    Implementation Details:
        Acts as a facade directly shielding the application from raw SB3 logic limits. Injects
        the customized `ZipCNN` extractor actively overriding default SB3 image normalization
        (since the grid tensor arrays natively reside between 0-1, bypassing standard 0-255 pixel
        adjustments). Safely encapsulates load/save capabilities mapping directly back into
        underlying device allocations.
    """

    def __init__(self, env: gym.Env, model_path: str | None = None, **dqn_kwargs):
        """
        Initializes the orchestrator bounding the network securely to targeted environments.

        Args:
            env: The structured virtual layout defining strict operational capabilities.
            model_path: The optional file boundary targeting pre-compiled weight directories.
            **dqn_kwargs: The expansive dict structure forwarding native hyperparameters to SB3.

        Implementation Details:
            Reserves explicit policy keyword rules immediately preventing normalized conversions.
            Branch logic executes directly against path presence: safely mapping saved structures
            back into memory, or initiating baseline random Deep Q-Network distributions configured
            against static fractional exploration baselines.
        """
        self._env = env

        self.policy_kwargs = dict(
            features_extractor_class=ZipCNN,
            features_extractor_kwargs=dict(features_dim=128),
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
        """
        Set a new linear exploration schedule.

        Args:
            initial_eps: The structural limit dictating maximum random policy deviations.
            final_eps: The minimal operational threshold limiting ultimate training exploration.
            fraction: The scaling constraint defining exactly when EPS hits the minimal threshold.

        Implementation Details:
            Mutates the internal protected object states forcefully overriding built-in static schedules
            with explicitly calculated linear progression models dictating stochastic decay.
        """
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
        """
        Return the action the agent chooses for a given observation.

        Args:
            observation: The extracted situational tensor defining layout progression.
            deterministic: The categorical flag isolating outputs strictly to learned optimal policies.

        Returns:
            The pure mathematical integer directly representing the resultant cardinal action.

        Implementation Details:
            Extracts predictions actively delegating execution onto the configured SB3 model, safely
            unpacking tuples to permanently strip out the secondary state sequence vectors entirely.
        """
        action, _state = self._model.predict(
            observation,
            deterministic=deterministic,
        )
        return action

    def learn(self, total_timesteps: int, reset_num_timesteps: bool = True):
        """
        Train the model for the given amount of timesteps.

        Args:
            total_timesteps: The absolute execution volume dictating maximum training limits.
            reset_num_timesteps: The binary flag resetting sequential step trackers on initiation.

        Returns:
            The structural self-reference allowing fluent method chaining architectures.

        Implementation Details:
            Invokes core underlying DQN backpropagation routines passing constraints forward, returning
            the wrapped instance mapping to support native fluent object bindings.
        """
        self._model.learn(
            total_timesteps=total_timesteps,
            reset_num_timesteps=reset_num_timesteps,
        )
        return self

    def set_env(self, env: gym.Env):
        """
        Switch the environment used by the wrapped model.

        Args:
            env: The subsequent active spatial layout replacing underlying validation configurations.

        Implementation Details:
            Updates dual memory states securely mapping the wrapper's encapsulated object reference
            and actively mutating the SB3 network's binding variables natively.
        """
        self._env = env
        self._model.set_env(env)

    def save(self, path: str):
        """
        Save the trained model to disk.

        Args:
            path: The strictly mapped spatial OS directory allocating exact archival structures.

        Implementation Details:
            Delegates execution natively into the SB3 compression utility exporting compiled tensor
            architectures mapping exactly into `.zip` structured frameworks.
        """
        self._model.save(path)

    def load(self, path: str, **dqn_kwargs) -> sb.DQN:
        """
        Load a trained model from disk.

        Args:
            path: The active directory pointing exactly at compressed evaluation topologies.
            **dqn_kwargs: The variable parameter set adjusting loaded states actively.

        Returns:
            The definitively mapped neural network natively bounding extracted values.

        Implementation Details:
            Injects explicit internal objects binding `policy_kwargs` aggressively bridging local
            custom `ZipCNN` extractors directly back into SB3 evaluation sequences utilizing
            dynamic hardware auto-allocations mapping against CUDA processors when available.
        """
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
        """
        Run the agent on the current environment until it solves or fails.

        Args:
            deterministic: The explicit toggle enforcing policy bounds without active random deviations.
            max_steps: The ultimate upper bounds forcing termination upon extreme execution durations.
            render: The boolean directive pushing visual evaluation streams natively during iterations.

        Returns:
            A structured multidimensional mapping encapsulating solution flags, rewards, and total histories.

        Raises:
            ValueError: If execution caps fail standard zero-bound math checks.

        Implementation Details:
            Instantiates unbroken iterative execution matrices trapping predictions securely. Feeds structural
            cardinal integer vectors continuously back into the active environment collecting reward scalars natively.
            Safely queries nested internal structural bounds checking exact completion flags circumventing
            standard gym truncation constraints directly before formatting final compiled state outputs.
        """
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

            observation, reward, terminated, truncated, info = self._env.step(
                action_int
            )
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
        """
        Check whether the currently assigned environment finished the puzzle.

        Returns:
            The boolean matrix dictating explicitly absolute structural puzzle completions.

        Implementation Details:
            Bypasses the `gymnasium` wrapper facade dynamically querying raw internal `Game` properties
            utilizing recursive introspection loops to securely accommodate variations arising natively
            from environments nested heavily within vectorized Gym structural tools.
        """
        if hasattr(self._env, "game"):
            return self._env.game.isFinished()

        if hasattr(self._env, "env") and hasattr(self._env.env, "game"):
            return self._env.env.game.isFinished()

        return False
