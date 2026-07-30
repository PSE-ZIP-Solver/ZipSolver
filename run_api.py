"""Local dev bootstrapper.

All four collaborators are now REAL — the response the frontend receives reflects the
actual board the user drew, run through the actual algorithmic solver.

Run from the repo root (not from backend/):
    uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8090

Frontend picks this up automatically via the Vite proxy in ``frontend/vite.config.ts``
(all ``/api/*`` calls forwarded to 127.0.0.1:8090). No env vars needed.
"""

from backend.api.BackendAPI import BackendAPI
from backend.api.architecture_provider.ArchitectureProvider import ArchitectureProvider
from backend.input_validation import InputValidator, JsonInterpreter
from backend.solving_process.solver_controller import SolverController

# Real collaborators. No mocks. The solver internally selects between the RL and the
# algorithmic solver; today only the algorithmic path is wired (the RL model is not yet
# packaged), which is fine — every board still gets a real answer.
interp = JsonInterpreter()
val = InputValidator()
ctrl = SolverController()
arch = ArchitectureProvider()

app = BackendAPI(
    interp,
    val,
    ctrl,
    arch,
    # No RL model loaded yet; health reports the state honestly rather than lying.
    model_loaded_provider=lambda: False,
).app