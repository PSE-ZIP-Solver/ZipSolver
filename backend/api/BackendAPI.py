from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Protocol

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.input_validation.errors import BoardParseError
from backend.input_validation.validation_dtos import ValidationError
from backend.puzzle_logic.board import Board
from backend.solution_path import SolutionPath
from backend.api.dtos.ArchitectureInfo import ArchitectureInfo
from backend.api.dtos.ErrorResponse import ErrorCode, ErrorResponse
from backend.api.dtos.HealthStatus import HealthStatus
from backend.api.dtos.ImportResult import ImportResult, ImportWarning
from backend.api.dtos.PuzzleRequest import PuzzleRequest
from backend.api.dtos.SolverResponse import SolverResponse
from backend.api.solver_result_adapter import to_solver_response
from backend.api.dtos.ValidationResult import ValidationResult
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus
from backend.api.version import API_VERSION


# ── Collaborator contracts (structural — real classes satisfy these without importing) ──
class JsonInterpreterProtocol(Protocol):
    # buildBoard does structural parsing and accepts either a parsed dict (from the
    # screenshot extractor / import path) or a PuzzleRequest-shaped object (from solve).
    # Typed as object so both callers satisfy it; the concrete interpreter narrows inside.
    def buildBoard(self, file: object) -> Board: ...


class InputValidatorProtocol(Protocol):
    def validate(self, board: Board) -> ValidationResult: ...


class SolverResultProtocol(Protocol):
    status: SolverStatus
    path: SolutionPath | None
    solver_used: str | None
    message: str
    metrics: SolverMetrics


class SolverControllerProtocol(Protocol):
    # The real controller returns a SolverResponse with getter properties; the API
    # normalises whatever it returns via solver_result_adapter.to_solver_response, so the
    # return is typed loosely here (object) rather than pinned to one internal shape.
    def solve(self, board: Board) -> object: ...


class ArchitectureProviderProtocol(Protocol):
    def collect(self) -> ArchitectureInfo: ...


class ScreenshotExtractorProtocol(Protocol):
    def extract_to_dict(self, image_bytes: bytes, board_size: int | None = None) -> dict: ...


# ── Domain exception → mapped to a 422 ErrorResponse by the handler below ──
class SemanticValidationError(Exception):
    """Raised when InputValidator rejects a semantically invalid board."""

    def __init__(self, result: ValidationResult) -> None:
        self.result = result
        super().__init__(result.message or "Board failed semantic validation")


# ── Domain exception → mapped to a 4xx ErrorResponse by the handler below ──
class ScreenshotImportError(Exception):
    """Raised when a screenshot cannot be turned into a board.

    ``http_status`` and ``code`` let the handler distinguish 'could not read the
    image at all' (400) from 'read a board but its waypoints were inconsistent' (422).
    """

    def __init__(self, message: str, *, http_status: int = 400,
                 code: ErrorCode = ErrorCode.MALFORMED_REQUEST) -> None:
        self.http_status = http_status
        self.code = code
        super().__init__(message)


# ── Domain exception → mapped to a 503 ErrorResponse by the handler below ──
class ArchitectureUnavailableError(Exception):
    """Raised when GET /api/architecture is called but no provider was injected.

    Distinguishes "endpoint exists but is not configured" (503) from "endpoint does
    not exist" (404), which matters for frontend advanced-mode feature detection.
    """


# ── Payload limits (§3.2.1, "payload limits & content negotiation") ──
# Two caps, because the two endpoints carry fundamentally different payloads. A JSON board
# is a few hundred bytes even at 8x8 with every wall declared; anything approaching 256 KiB
# is a mistake or an attempt to make the server do parsing work on our dime. Screenshots
# are legitimately larger, and their own 10 MiB ceiling already lives in ImageLoader — this
# mirrors it at the edge so the body is refused before it is buffered rather than after.
MAX_JSON_BODY_BYTES = 256 * 1024
MAX_UPLOAD_BODY_BYTES = 10 * 1024 * 1024

#: Image types the screenshot pipeline can actually decode. Anything else is rejected at
#: the boundary with a clear message rather than being handed to OpenCV to fail obscurely.
ALLOWED_UPLOAD_CONTENT_TYPES = frozenset(
    {"image/png", "image/jpeg", "image/jpg", "image/webp"}
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _limit_for(path: str) -> int:
    """Body-size ceiling for a request path."""
    return MAX_UPLOAD_BODY_BYTES if path == "/api/import" else MAX_JSON_BODY_BYTES


def _code_from_result(result: ValidationResult) -> ErrorCode:
    """Map the first semantic error's code onto the taxonomy; fall back to INVALID_WAYPOINTS."""
    if result.errors:
        try:
            return ErrorCode(result.errors[0].error_code)
        except ValueError:
            pass
    return ErrorCode.INVALID_WAYPOINTS


class BackendAPI:
    """Wraps the FastAPI app and the four public endpoints (§3.2.1). Collaborators
    are injected so the routing layer stays independent of concrete implementations.

    `architecture_provider` is optional: when absent, GET /api/architecture returns a
    503 rather than 404, which distinguishes "not configured" from "route missing".
    """

    def __init__(
        self,
        interpreter: JsonInterpreterProtocol,
        input_validator: InputValidatorProtocol,
        solver_controller: SolverControllerProtocol,
        architecture_provider: ArchitectureProviderProtocol | None = None,
        screenshot_extractor: ScreenshotExtractorProtocol | None = None,
        *,
        allowed_origins: list[str] | None = None,
        model_loaded_provider: Callable[[], bool] | None = None,
    ) -> None:
        self._interpreter = interpreter
        self._input_validator = input_validator
        self._solver_controller = solver_controller
        self._architecture_provider = architecture_provider
        self._screenshot_extractor = screenshot_extractor
        self._model_loaded_provider = model_loaded_provider
        self.app = FastAPI(title="ZipSolver API", version=API_VERSION)

        self.app.add_middleware(
            CORSMiddleware,
            # Both spellings of the Vite dev origin. Browsers treat "localhost" and
            # "127.0.0.1" as distinct origins, and Vite prints whichever the host resolves
            # to, so allowing only one produced CORS failures that looked like backend
            # outages.
            # Also allow deployed frontend origins from Vercel and Render, while keeping
            # local development origins intact.
            allow_origins=allowed_origins
            or [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "https://*.vercel.app",
                "https://*.onrender.com",
            ],
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )
        self._register_payload_limit()
        self._register_routes()
        self._register_exception_handlers()

    # ── Payload guard ──
    def _register_payload_limit(self) -> None:
        """Reject over-sized bodies before FastAPI parses or buffers them (§3.2.1).

        Runs as middleware rather than per-route validation because by the time a route
        handler is entered the body has already been read into memory — which is precisely
        the cost being defended against. ``Content-Length`` is the only signal available
        pre-read; a chunked request without it falls through to the per-endpoint limits
        (ImageLoader's 10 MiB cap, Pydantic's own parsing), so this is a cheap first line
        rather than the only one.
        """

        @self.app.middleware("http")
        async def _enforce_payload_limit(request: Request, call_next):
            declared = request.headers.get("content-length")
            if declared is not None:
                try:
                    size = int(declared)
                except ValueError:
                    size = 0
                limit = _limit_for(request.url.path)
                if size > limit:
                    body = ErrorResponse(
                        status=413,
                        code=ErrorCode.PAYLOAD_TOO_LARGE,
                        message=(
                            f"Request body is {size} bytes, which exceeds the "
                            f"{limit}-byte limit for this endpoint."
                        ),
                        details=None,
                        timestamp=_now_iso(),
                    )
                    return JSONResponse(
                        status_code=413,
                        content=body.model_dump(by_alias=True, mode="json"),
                    )
            return await call_next(request)

    # ── Routing ──
    def _register_routes(self) -> None:
        self.app.post("/api/solve", response_model=SolverResponse)(self.solvePuzzle)
        self.app.post("/api/import", response_model=ImportResult)(self.importPuzzle)
        self.app.get("/api/health", response_model=HealthStatus)(self.healthCheck)
        self.app.get("/api/architecture", response_model=ArchitectureInfo)(self.getArchitecture)

    def solvePuzzle(self, request: PuzzleRequest) -> SolverResponse:
        """POST /api/solve — validate, then run the solver strategy. Always 200 on a solver
        outcome; non-results (UNSOLVABLE/TIMEOUT/FAILED) return 200 with a null path.
        """
        board = self._build_and_validate(request)
        result = self._solver_controller.solve(board)

        # The controller returns a SolverResponse with getter properties; normalise it to
        # the flat API DTO here. This isolates the API from the internal result shape and
        # tolerates the controller's success-only reporting (see the adapter's docstring).
        return to_solver_response(result)

    async def importPuzzle(
        self,
        file: UploadFile = File(...),
        board_size: int | None = Form(default=None),
    ) -> ImportResult:
        """POST /api/import — extract a board from an uploaded screenshot (PNG/JPEG).

        Pipeline: image bytes -> ScreenshotExtractor -> JsonInterpreter -> InputValidator.
        Returns 200 with the extracted board and its validation outcome. The board is
        included even when semantic validation fails, so the frontend can show the user
        what was read and let them fix it rather than starting over. Extraction failures
        (unreadable image, inconsistent waypoints) surface as 4xx via the handler below.

        ``board_size`` is the grid size the user already selected in the UI. Passing it
        (as a multipart form field) lets the extractor skip fragile size-detection and use
        the known value, which is far more reliable on real screenshots. It is optional so
        older clients that omit it still work via image-only estimation.
        """
        if self._screenshot_extractor is None:
            raise ScreenshotImportError(
                "Screenshot import is not configured on this instance.",
                http_status=503,
                code=ErrorCode.INTERNAL_ERROR,
            )

        # Content negotiation before any decode work. The extractor would eventually fail
        # on a PDF or a text file, but only after buffering it and running it through
        # OpenCV — and the resulting message ("Failed to decode image data") tells the user
        # nothing about what they actually did wrong.
        content_type = (file.content_type or "").split(";")[0].strip().lower()
        if content_type not in ALLOWED_UPLOAD_CONTENT_TYPES:
            raise ScreenshotImportError(
                f"Unsupported upload type {content_type or 'unknown'!r}. "
                "Upload a PNG, JPEG, or WebP screenshot.",
                http_status=400,
                code=ErrorCode.MALFORMED_REQUEST,
            )

        # Starlette populates ``size`` from the multipart part when it knows it. Checking
        # it here refuses an oversized upload without materialising it; ImageLoader repeats
        # the check on the bytes themselves for the case where size is unknown.
        declared_size = getattr(file, "size", None)
        if declared_size is not None and declared_size > MAX_UPLOAD_BODY_BYTES:
            raise ScreenshotImportError(
                f"Uploaded image is {declared_size} bytes, which exceeds the "
                f"{MAX_UPLOAD_BODY_BYTES}-byte limit.",
                http_status=413,
                code=ErrorCode.PAYLOAD_TOO_LARGE,
            )

        image_bytes = await file.read()

        # ScreenshotExtractor bubbles ValueError (bad/unreadable image, wrong board size)
        # and WaypointDetectionError (marker unreadable, sequence gap, duplicate). Map the
        # former to 400 (image could not be read) and the latter to 422 (a board was read
        # but its waypoints are inconsistent) so the frontend can respond differently.
        # The extractor raises a typed ScreenshotError hierarchy; each subclass carries its
        # own code and http_status (NO_BOARD_DETECTED / AMBIGUOUS_BOARD / INVALID_WAYPOINTS
        # -> 422, unreadable image -> 400). Map them uniformly rather than sniffing message
        # strings. Anything else is an unexpected fault and bubbles to the 500 handler.
        try:
            board_dict = self._screenshot_extractor.extract_to_dict(
                image_bytes, board_size
            )
        except ScreenshotImportError:
            raise
        except Exception as exc:  # noqa: BLE001 - ScreenshotError carries code/status
            code = getattr(exc, "code", None)
            http_status = getattr(exc, "http_status", None)
            if code is not None and http_status is not None:
                try:
                    mapped = ErrorCode(code)
                except ValueError:
                    mapped = ErrorCode.INTERNAL_ERROR
                raise ScreenshotImportError(
                    str(exc), http_status=http_status, code=mapped
                ) from exc
            # A bare ValueError with no typed code is still a bad-image condition (the
            # extractor could not make sense of the upload) -> 400, not a 500.
            if isinstance(exc, ValueError):
                raise ScreenshotImportError(
                    str(exc), http_status=400, code=ErrorCode.MALFORMED_REQUEST
                ) from exc
            raise

        # Pull best-effort warnings the extractor attached (e.g. low-confidence waypoint
        # numbering) out of the dict before it feeds the interpreter / PuzzleRequest, which
        # only expect board fields.
        # The detector emits structured warnings ({code, message, cell}); older shapes
        # (bare strings) are still accepted so the endpoint never 500s on a warning. The
        # code is the discriminator the frontend switches on, so it must reflect what
        # actually went wrong rather than being stamped with one constant.
        raw_warnings = board_dict.pop("_warnings", []) or []
        import_warnings = [self._to_import_warning(w) for w in raw_warnings]

        # Reuse the solve-path front half: dict -> Board -> semantic validation.
        # buildBoard accepts a dict, so the extractor output feeds it directly.
        # The extractor emits each cell boundary once, so a duplicate wall is not reachable
        # here today — but mapping the parse error keeps a future detector change from
        # turning a recoverable import problem into an opaque 500.
        try:
            board = self._interpreter.buildBoard(board_dict)
        except BoardParseError as exc:
            raise ScreenshotImportError(
                str(exc), http_status=exc.http_status, code=ErrorCode(exc.code)
            ) from exc

        result = self._input_validator.validate(board)

        extracted = PuzzleRequest.model_validate(board_dict)
        return ImportResult(
            board=extracted,
            valid=result.valid,
            message=result.message,
            errors=result.errors,
            warnings=import_warnings,
        )

    @staticmethod
    def _to_import_warning(raw: object) -> ImportWarning:
        """Normalise one extractor warning into an ImportWarning.

        Accepts the structured dict the detector now produces and degrades gracefully to a
        generic code for any legacy string, so a warning can never turn a successful import
        into a 500.
        """
        if isinstance(raw, dict):
            return ImportWarning(
                code=str(raw.get("code") or "IMPORT_WARNING"),
                message=str(raw.get("message") or ""),
                cell=raw.get("cell"),
            )
        return ImportWarning(code="IMPORT_WARNING", message=str(raw), cell=None)

    def healthCheck(self) -> HealthStatus:
        """GET /api/health — cheap in-process liveness/readiness probe (§3.2.1).

        Deliberately touches neither the validation nor the solver pipeline, so it stays
        answerable even when those collaborators are degraded. `modelLoaded` is reported
        only when the RL layer has supplied a status provider.
        """
        model_loaded = self._model_loaded_provider() if self._model_loaded_provider else None
        return HealthStatus(status="ok", apiVersion=API_VERSION, modelLoaded=model_loaded)

    def getArchitecture(self) -> ArchitectureInfo:
        """GET /api/architecture — read-only runtime technical inventory (§5.5.6).

        Reports names and versions only: no file paths, secrets, model weights, or
        environment variables ever cross this boundary.
        """
        if self._architecture_provider is None:
            raise ArchitectureUnavailableError()
        return self._architecture_provider.collect()

    def _build_and_validate(self, request: PuzzleRequest) -> Board:
        """Shared front half: JSON→Board→semantic check.

        Raises SemanticValidationError on failure; returns the validated Board.
        """
        # buildBoard accepts a PuzzleRequest (its _load serialises Pydantic models) or a
        # dict; the import path passes a dict, solve passes the request DTO.
        #
        # A BoardParseError that carries a 4xx semantic code (currently only duplicate
        # walls, which the Board's wall set makes unobservable downstream — see
        # input_validation/errors.py) is re-raised as a SemanticValidationError so it lands
        # in the same 422 envelope as every other semantic failure, rather than being
        # flattened into a 400 by the generic shape handler.
        try:
            board = self._interpreter.buildBoard(request)
        except BoardParseError as exc:
            if exc.http_status == 422:
                raise SemanticValidationError(
                    ValidationResult(
                        valid=False,
                        message=str(exc),
                        errors=[
                            ValidationError(
                                errorCode=exc.code,
                                affectedField=exc.affected_field,
                                message=str(exc),
                            )
                        ],
                    )
                ) from exc
            raise

        result = self._input_validator.validate(board)
        if not result.valid:
            raise SemanticValidationError(result)
        return board

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

        @self.app.exception_handler(ArchitectureUnavailableError)
        async def _on_architecture_unavailable(
            _: Request, exc: ArchitectureUnavailableError
        ) -> JSONResponse:
            body = ErrorResponse(
                status=503,
                code=ErrorCode.INTERNAL_ERROR,
                message="Architecture inventory is not configured on this instance.",
                details=None,
                timestamp=_now_iso(),
            )
            return JSONResponse(status_code=503, content=body.model_dump(by_alias=True, mode="json"))

        @self.app.exception_handler(ScreenshotImportError)
        async def _on_screenshot(_: Request, exc: ScreenshotImportError) -> JSONResponse:
            body = ErrorResponse(
                status=exc.http_status,
                code=exc.code,
                message=str(exc),
                details=None,
                timestamp=_now_iso(),
            )
            return JSONResponse(
                status_code=exc.http_status,
                content=body.model_dump(by_alias=True, mode="json"),
            )

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