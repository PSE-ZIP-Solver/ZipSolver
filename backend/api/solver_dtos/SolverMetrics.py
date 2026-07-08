from pydantic import BaseModel, ConfigDict, Field


class SolverMetrics(BaseModel):
    """Per-attempt performance figures returned inside a SolverResponse (§5.5.3).
    """

    model_config = ConfigDict(populate_by_name=True)

    runtime_ms: int = Field(..., ge=0, alias="runtimeMs")
    steps: int = Field(..., ge=0)
    attempts: int = Field(..., ge=1)
