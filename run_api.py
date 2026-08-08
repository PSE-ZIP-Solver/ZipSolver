"""Local dev bootstrapper.

Wires the real interpreter, validator, solver controller, architecture provider, and
screenshot extractor — no mocks. The frontend reaches this via the Vite proxy in
frontend/vite.config.ts (all /api/* forwarded to 127.0.0.1:8090).

Run from the repo root (not from backend/):
    uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8090
"""

from backend.api.BackendAPI import BackendAPI
from backend.api.architecture_provider.ArchitectureProvider import ArchitectureProvider
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
    # No RL model artifact wired yet; report honestly rather than guessing True.
    model_loaded_provider=lambda: False,
).app