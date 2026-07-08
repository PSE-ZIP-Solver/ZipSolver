from unittest.mock import MagicMock
from backend.api.BackendAPI import BackendAPI
from backend.puzzle_logic import Board, Position
from backend.solution_path import SolutionPath
from backend.api.solver_dtos.SolverStatus import SolverStatus
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.dtos.ValidationResult import ValidationResult

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

app = BackendAPI(interp, val, ctrl).app