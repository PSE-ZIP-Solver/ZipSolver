from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, overload, Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.puzzle_logic.board import Board
from backend.SolutionPath import SolutionPath
from backend.api.dtos.ErrorResponse import ErrorCode, ErrorResponse
from backend.api.dtos.PuzzleRequest import PuzzleRequest
from backend.api.dtos.SolverResponse import SolverResponse
from backend.api.dtos.ValidationResult import ValidationResult
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus


# ── Collaborator contracts (structural — real classes satisfy these without importing) ──
class JsonInterpreterProtocol(Protocol):
    def buildBoard(self, request: PuzzleRequest) -> Board: ...


class InputValidatorProtocol(Protocol):
    def validate(self, board: Board) -> ValidationResult: ...


class SolverResultProtocol(Protocol):
    status: SolverStatus
    path: SolutionPath | None
    solver_used: str | None
    message: str
    metrics: SolverMetrics


class SolverControllerProtocol(Protocol):
    def solve(self, board: Board) -> SolverResultProtocol: ...


# ── Domain exception → mapped to a 422 ErrorResponse by the handler below ──
class SemanticValidationError(Exception):
    """Raised when InputValidator rejects a semantically invalid board."""

    def __init__(self, result: ValidationResult) -> None:
        self.result = result
        super().__init__(result.message or "Board failed semantic validation")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _code_from_result(result: ValidationResult) -> ErrorCode:
    """Map the first semantic error's code onto the taxonomy; fall back to INVALID_WAYPOINTS."""
    if result.errors:
        try:
            return ErrorCode(result.errors[0].error_code)
        except ValueError:
            pass
    return ErrorCode.INVALID_WAYPOINTS


class BackendAPI:
    """Wraps the FastAPI app and the two puzzle endpoints. Collaborators are injected."""

    def __init__(
        self,
        interpreter: JsonInterpreterProtocol,
        input_validator: InputValidatorProtocol,
        solver_controller: SolverControllerProtocol,
        *,
        allowed_origins: list[str] | None = None,
    ) -> None:
        self._interpreter = interpreter
        self._input_validator = input_validator
        self._solver_controller = solver_controller
        self.app = FastAPI(title="ZipSolver API", version="1.0.0")

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins or ["http://localhost:5173"],  # Vite dev origin
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )
        self._register_routes()
        self._register_exception_handlers()

    # ── Routing ──
    def _register_routes(self) -> None:
        self.app.post("/api/solve", response_model=SolverResponse)(self.solvePuzzle)
        self.app.post("/api/import", response_model=ValidationResult)(self.importPuzzle)

    def solvePuzzle(self, request: PuzzleRequest) -> SolverResponse:
        """POST /api/solve — validate, then run the solver strategy. Always 200 on a solver
        outcome; non-results (UNSOLVABLE/TIMEOUT/FAILED) return 200 with a null path.
        """
        board = self._build_and_validate(request)
        result = self._solver_controller.solve(board)

        solved = result.status == SolverStatus.SOLVED
        path = (
            [(p.getX, p.getY) for p in result.path.getPostions]
            if (solved and result.path is not None)
            else None
        )

        return SolverResponse(
            status=result.status,
            success=solved,
            solutionPath=path,
            solverUsed=result.solver_used,
            message=result.message,
            metrics=result.metrics,
        )

    def importPuzzle(self, request: PuzzleRequest) -> ValidationResult:
        """POST /api/import — 'validate before loading' (§2.3). Returns 200 ValidationResult
        on success; malformed shape → 400, invalid semantics → 422 via the handlers below.
        """
        return self._build_and_validate(request, return_result=True)  # type: ignore[return-value]

    @overload
    def _build_and_validate(self, request: PuzzleRequest, *, return_result: Literal[False] = ...) -> Board: ...

    @overload
    def _build_and_validate(self, request: PuzzleRequest, *, return_result: Literal[True]) -> ValidationResult: ...

    def _build_and_validate(
        self, request: PuzzleRequest, *, return_result: bool = False
    ) -> Board | ValidationResult:
        """Shared front half: JSON→Board→semantic check. Raises SemanticValidationError on
        failure. Returns the ValidationResult for /import, the Board for /solve.
        """
        board = self._interpreter.buildBoard(request)
        result = self._input_validator.validate(board)
        if not result.valid:
            raise SemanticValidationError(result)
        return result if return_result else board

    # ── Exception handlers: map failures onto the ErrorResponse taxonomy (§5.5.5) ──
    def _register_exception_handlers(self) -> None:
        @self.app.exception_handler(RequestValidationError)
        async def _on_shape(_: Request, exc: RequestValidationError) -> JSONResponse:
            # FastAPI defaults Pydantic shape failures to 422; the taxonomy wants 400.
            body = ErrorResponse(
                status=400,
                code=ErrorCode.MALFORMED_REQUEST,
                message="Request body failed shape validation.",
                details=None,
                timestamp=_now_iso(),
            )
            return JSONResponse(status_code=400, content=body.model_dump(by_alias=True, mode="json"))

        @self.app.exception_handler(SemanticValidationError)
        async def _on_semantic(_: Request, exc: SemanticValidationError) -> JSONResponse:
            body = ErrorResponse(
                status=422,
                code=_code_from_result(exc.result),
                message=exc.result.message or "Semantic validation failed.",
                details=exc.result.errors or None,
                timestamp=_now_iso(),
            )
            return JSONResponse(status_code=422, content=body.model_dump(by_alias=True, mode="json"))

        @self.app.exception_handler(Exception)
        async def _on_unhandled(_: Request, exc: Exception) -> JSONResponse:
            body = ErrorResponse(
                status=500,
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected backend error occurred.",
                details=None,
                timestamp=_now_iso(),
            )
            return JSONResponse(status_code=500, content=body.model_dump(by_alias=True, mode="json"))
