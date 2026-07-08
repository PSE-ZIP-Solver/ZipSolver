from pydantic import BaseModel, ConfigDict, Field

from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus

Coordinate = tuple[int, int]


class SolverResponse(BaseModel):
    """200 body for POST /api/solve (§5.5.2).

    A non-result (UNSOLVABLE / TIMEOUT / FAILED) is still HTTP 200 with a null path —
    never a 4xx. Internally the solvers return a SolverResult which SolverController
    wraps into this DTO.
    """

    model_config = ConfigDict(populate_by_name=True)

    status: SolverStatus
    success: bool
    solution_path: list[Coordinate] | None = Field(None, alias="solutionPath")
    solver_used: str | None = Field(None, alias="solverUsed")  # "RL" | "DFS" | None
    message: str = ""
    metrics: SolverMetrics
