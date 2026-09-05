from pydantic import BaseModel, ConfigDict, Field


class HealthStatus(BaseModel):
    """200 body for GET /api/health (§3.2.1).

    A cheap in-process liveness/readiness probe. Never touches the validation or
    solver pipeline. `modelLoaded` is omitted entirely unless the RL layer supplies
    a status provider, so the endpoint stays answerable before any model is wired.
    """

    model_config = ConfigDict(populate_by_name=True)

    status: str = "ok"
    api_version: str = Field(..., alias="apiVersion")
    model_loaded: bool | None = Field(default=None, alias="modelLoaded")
