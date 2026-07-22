"""Local dev bootstrapper.

JsonInterpreter / InputValidator / SolverController are still MagicMock stand-ins until
the concrete classes land. ArchitectureProvider is the real implementation — it has no
dependency on the solver pipeline, so it can be wired for real today.

Run from the repo root (not from backend/):
    uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8090
"""

from unittest.mock import MagicMock

from backend.api.BackendAPI import BackendAPI
from backend.api.architecture_provider.ArchitectureProvider import ArchitectureProvider
from backend.api.dtos.ValidationResult import ValidationResult
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus
from backend.puzzle_logic import Board, Position
from backend.solution_path import SolutionPath

interp = MagicMock()
interp.buildBoard.return_value = Board(6)

val = MagicMock()
val.validate.return_value = ValidationResult(valid=True, message="ok", errors=[])

sp = SolutionPath()
for x, y in [(0, 0), (0, 1), (0, 2)]:
    sp.add(Position(x, y))

res = MagicMock()
res.status = SolverStatus.SOLVED
res.path = sp
res.solver_used = "RL"
res.message = "ok"
res.metrics = SolverMetrics(runtimeMs=142, steps=36, attempts=1)

ctrl = MagicMock()
ctrl.solve.return_value = res

# Real provider — no solver/RL dependency, so no stub needed.
arch = ArchitectureProvider()

app = BackendAPI(
    interp,
    val,
    ctrl,
    arch,
    model_loaded_provider=lambda: False,  # no artifact wired yet
).app