from pydantic import BaseModel, ConfigDict, Field

from backend.api.architecture_provider.LibraryInfo import LibraryInfo
from backend.api.architecture_provider.ModelInfo import ModelInfo


class RLStackInfo(BaseModel):
    """The reinforcement-learning stack: DL backend, RL library, environment,
    algorithm, and the trained-model metadata (§5.5.6).
    """

    model_config = ConfigDict(populate_by_name=True)

    deep_learning: LibraryInfo = Field(..., alias="deepLearning")
    rl_library: LibraryInfo = Field(..., alias="rlLibrary")
    environment: LibraryInfo
    algorithm: str
    model: ModelInfo
