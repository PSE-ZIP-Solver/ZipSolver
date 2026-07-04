
from __future__ import annotations

import platform
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from typing import Callable

from backend.api.architecture_provider.ComponentInfo import ComponentInfo
from backend.api.architecture_provider.FrontendInfo import FrontendInfo
from backend.api.architecture_provider.LibraryInfo import LibraryInfo
from backend.api.architecture_provider.ModelInfo import ModelInfo
from backend.api.architecture_provider.RLStackInfo import RLStackInfo
from backend.api.architecture_provider.RuntimeInfo import RuntimeInfo
from backend.api.architecture_provider.SolverInfo import SolverInfo
from backend.api.dtos.ArchitectureInfo import ArchitectureInfo

_API_VERSION = "1.0.0"
_UNKNOWN = "unknown"

# Static registries — names/roles are architectural facts, not runtime state (§5.5.6).
_SOLVERS = [
    SolverInfo(name="RLSolver", kind="reinforcement-learning", default=True),
    SolverInfo(name="AlgorithmicSolver", kind="DFS", default=False),
]
_BACKEND_COMPONENTS = [
    ComponentInfo(name="BackendAPI", role="API entry / routing"),
    ComponentInfo(name="JsonInterpreter", role="JSON to Board"),
    ComponentInfo(name="InputValidator", role="semantic input validation"),
    ComponentInfo(name="SolverController", role="solver orchestration"),
    ComponentInfo(name="SolutionValidator", role="final Zip-rule validation"),
    ComponentInfo(name="ArchitectureProvider", role="runtime technical inventory"),
]
_FRONTEND = FrontendInfo(framework="React", buildTool="Vite", styling="Tailwind CSS")


def _pkg_version(dist_name: str) -> str:
    """Resolve an installed distribution's version, or 'unknown' if absent."""
    try:
        return version(dist_name)
    except PackageNotFoundError:
        return _UNKNOWN


class ArchitectureProvider:
    """Collects the runtime inventory. Model status is injected so this class stays
    decoupled from the RL layer; absent a provider it reports the model as not loaded.
    """

    def __init__(
        self,
        *,
        build_timestamp: str | None = None,
        model_status_provider: Callable[[], ModelInfo] | None = None,
    ) -> None:
        self._build_timestamp = build_timestamp or datetime.now(timezone.utc).isoformat()
        self._model_status_provider = model_status_provider

    def collect(self) -> ArchitectureInfo:
        """Assemble the full ArchitectureInfo snapshot."""
        return ArchitectureInfo(
            apiVersion=_API_VERSION,
            buildTimestamp=self._build_timestamp,
            runtime=self._runtime(),
            validation=LibraryInfo(name="Pydantic", version=_pkg_version("pydantic")),
            numerical=LibraryInfo(name="NumPy", version=_pkg_version("numpy")),
            reinforcementLearning=self._rl_stack(),
            solvers=_SOLVERS,
            backendComponents=_BACKEND_COMPONENTS,
            frontend=_FRONTEND,
        )

    def _runtime(self) -> RuntimeInfo:
        return RuntimeInfo(
            language="Python",
            languageVersion=platform.python_version(),
            asgiFramework="FastAPI",
            frameworkVersion=_pkg_version("fastapi"),
            server="Uvicorn",
            serverVersion=_pkg_version("uvicorn"),
        )

    def _rl_stack(self) -> RLStackInfo:
        return RLStackInfo(
            deepLearning=LibraryInfo(name="PyTorch", version=_pkg_version("torch")),
            rlLibrary=LibraryInfo(name="Stable-Baselines3", version=_pkg_version("stable-baselines3")),
            environment=LibraryInfo(name="Gymnasium", version=_pkg_version("gymnasium")),
            algorithm="DQN",
            model=self._model_status(),
        )

    def _model_status(self) -> ModelInfo:
        if self._model_status_provider is not None:
            return self._model_status_provider()
        return ModelInfo(name="zip-dqn", supportedBoardSizes=[6, 7, 8], loaded=False)