from pydantic import BaseModel, ConfigDict, Field

from backend.api.architecture_provider.ComponentInfo import ComponentInfo
from backend.api.architecture_provider.FrontendInfo import FrontendInfo
from backend.api.architecture_provider.LibraryInfo import LibraryInfo
from backend.api.architecture_provider.RLStackInfo import RLStackInfo
from backend.api.architecture_provider.RuntimeInfo import RuntimeInfo
from backend.api.architecture_provider.SolverInfo import SolverInfo

class ArchitectureInfo(BaseModel):
    """200 body for GET /api/architecture — the runtime technical inventory (§5.5.6)."""

    model_config = ConfigDict(populate_by_name=True)

    api_version: str = Field(..., alias="apiVersion")
    build_timestamp: str = Field(..., alias="buildTimestamp")
    runtime: RuntimeInfo
    validation: LibraryInfo
    numerical: LibraryInfo
    reinforcement_learning: RLStackInfo = Field(..., alias="reinforcementLearning")
    solvers: list[SolverInfo]
    backend_components: list[ComponentInfo] = Field(..., alias="backendComponents")
    frontend: FrontendInfo