from pydantic import BaseModel, ConfigDict, Field


class ArchitectureInfo(BaseModel):
    """Runtime technical inventory for GET /api/architecture (§5.5.6).

    STUB — solve/import don't use this. Nested models (RuntimeInfo, LibraryInfo,
    RLStackInfo, SolverInfo, ComponentInfo, FrontendInfo) get wired in when the
    architecture endpoint is built. Fields kept loose until then.
    """

    model_config = ConfigDict(populate_by_name=True)

    api_version: str = Field(..., alias="apiVersion")
    build_timestamp: str = Field(..., alias="buildTimestamp")
