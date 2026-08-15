"""Local dev bootstrapper.

Wires the real interpreter, validator, solver controller, architecture provider, and
screenshot extractor — no mocks. The frontend calls this origin directly at
http://localhost:8090 (see frontend/src/api/apiClient.ts); cross-origin access is granted
by the CORS middleware in BackendAPI, which allows the Vite dev origin :5173.

Run from the repo root (not from backend/):
    uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8090
"""

from backend.api.BackendAPI import BackendAPI
from backend.api.architecture_provider.ArchitectureProvider import (
    ArchitectureProvider,
    available_model_sizes,
)
from backend.input_validation.input_validator import InputValidator
from backend.input_validation.json_interpreter import JsonInterpreter
from backend.input_validation.screenshot import ScreenshotExtractor
from backend.solving_process.solver_controller import SolverController

# Real collaborators. buildBoard does structural parsing; InputValidator enforces the
# semantic rules and returns structured 422 codes; SolverController runs the RL-then-
# algorithmic strategy; ScreenshotExtractor turns an uploaded image into a board dict.
interpreter = JsonInterpreter()
validator = InputValidator()
controller = SolverController()
architecture = ArchitectureProvider()
extractor = ScreenshotExtractor()

app = BackendAPI(
    interpreter,
    validator,
    controller,
    architecture,
    extractor,
    # Same source of truth the architecture inventory uses, so /api/health and
    # /api/architecture can never disagree about whether a model artifact is present.
    model_loaded_provider=lambda: bool(available_model_sizes()),
).app