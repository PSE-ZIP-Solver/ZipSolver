# ZipSolver

A web application that solves LinkedIn's **Zip** puzzle, using a reinforcement-learning
agent with a deterministic search algorithm as a fallback.

Build a board in the browser — or import one straight from a screenshot — and the backend
finds a path that visits every cell exactly once while reaching the numbered waypoints in
order and never crossing a wall.

Developed as a PSE project at the Chair of Dependable Nano Computing (CDNC), Karlsruhe
Institute of Technology.

---

## Table of contents

- [What Zip is](#what-zip-is)
- [Features](#features)
- [Architecture](#architecture)
- [Technology stack](#technology-stack)
- [Getting started](#getting-started)
- [Running the application](#running-the-application)
- [API reference](#api-reference)
- [Data formats and conventions](#data-formats-and-conventions)
- [Solving strategy](#solving-strategy)
- [Reinforcement learning](#reinforcement-learning)
- [Screenshot import](#screenshot-import)
- [Testing](#testing)
- [Project layout](#project-layout)
- [Troubleshooting](#troubleshooting)
- [Team](#team)

---

## What Zip is

Zip is played on an *n* × *n* grid holding numbered waypoints and, optionally, walls
between adjacent cells. A solution is a single continuous path that:

1. starts at waypoint **1** and ends at the highest-numbered waypoint,
2. moves only horizontally or vertically between adjacent cells,
3. never crosses a wall,
4. visits **every** cell on the board exactly once, and
5. reaches the numbered waypoints in ascending order.

Requirement 4 makes this a constrained Hamiltonian path problem, which is why a naive
search blows up quickly and why the board sizes are capped at 6×6, 7×7, and 8×8.

---

## Features

- **Build boards by clicking.** Place numbered waypoints and toggle walls on a 6×6, 7×7,
  or 8×8 grid.
- **Import from a screenshot.** Upload a screenshot of a Zip puzzle and the backend reads
  the grid, the waypoint markers, and the walls out of the image.
- **Solve.** The RL agent attempts the board first; a deterministic A\* search takes over
  if it cannot produce a valid path.
- **Play mode.** Solve the puzzle yourself with click or arrow-key movement, undo, and an
  optional hint drawn from the computed solution.
- **Share by link.** Boards are encoded into the URL, so sharing a puzzle needs no server
  storage and no account.
- **Example puzzles.** A built-in set of boards per grid size for a zero-setup demo.
- **Advanced mode.** Exposes solver metrics: runtime, steps, attempts, and which solver
  produced the answer.
- **Light and dark themes.**

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Frontend  (React + Vite, :5173)                             │
│  Grid editor · play mode · share links · screenshot upload   │
└───────────────────────────┬──────────────────────────────────┘
                            │  JSON / multipart over HTTP
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  BackendAPI  (FastAPI + Uvicorn, :8090)                      │
│  Routing · Pydantic shape validation · error taxonomy · CORS │
└───────────────────────────┬──────────────────────────────────┘
                            ▼
     ┌──────────────────────┴───────────────────────┐
     ▼                                              ▼
┌─────────────────────┐                  ┌──────────────────────┐
│  Input Validation   │                  │  ScreenshotExtractor │
│  JsonInterpreter    │                  │  grid · waypoints ·  │
│  InputValidator     │                  │  walls from an image │
└──────────┬──────────┘                  └──────────────────────┘
           ▼
┌─────────────────────┐        ┌──────────────────────┐
│  SolverController   │───────▶│  RLSolver  (DQN)     │
│  strategy + retry   │        └──────────────────────┘
│                     │        ┌──────────────────────┐
│                     │───────▶│  AlgorithmicSolver   │
└──────────┬──────────┘        │  (A*, fallback)      │
           ▼                   └──────────────────────┘
┌─────────────────────┐        ┌──────────────────────┐
│  SolutionValidator  │───────▶│  Puzzle Logic        │
│  re-checks any path │        │  Board · Game ·      │
└─────────────────────┘        │  GameState · Rules   │
                               └──────────────────────┘
```

### The backend is the trust boundary

The frontend exists for usability, not correctness. Anyone can bypass it with `curl`,
Postman, or the generated Swagger UI, so the backend treats every request as potentially
malformed or hostile:

- **No raw input reaches the core.** Every request passes Pydantic shape validation, then
  `JsonInterpreter` builds the `Board`, then `InputValidator` checks semantics. Solver
  components only ever see a board that cleared all three.
- **No client-controlled solver limits.** Timeouts and step budgets are fixed backend-side
  and are never read from a request body.
- **No client-controlled model selection.** The trained artifact is chosen internally from
  the board size. Request data never influences a file path.
- **The agent is not a correctness oracle.** Every candidate path — from the RL agent
  *and* from the fallback — is re-checked by `SolutionValidator` before it is returned. An
  invalid path is never surfaced as a solution.
- **Failures are structured.** Anticipated conditions produce a typed response, never an
  unhandled 500.
- **Payload limits.** 256 KiB for JSON endpoints, 10 MiB for screenshot uploads, enforced
  before the body is buffered.
- **Stateless.** No sessions, no user data, no persistence.

---

## Technology stack

**Backend**

| Component | Choice |
|---|---|
| Language | Python 3.12+ |
| Web framework | FastAPI, served by Uvicorn |
| Schema validation | Pydantic v2 |
| RL library | Stable-Baselines3 (DQN) |
| Environment API | Gymnasium |
| Deep learning | PyTorch, with a custom `ZipCNN` feature extractor |
| Computer vision | OpenCV (headless), Pillow, pytesseract |
| Testing | pytest, FastAPI `TestClient` |
| Packaging | `uv` + hatchling |

**Frontend**

| Component | Choice |
|---|---|
| Language | TypeScript |
| Framework | React 19 (with the React Compiler) |
| Build tool | Vite 8 |
| Styling | Tailwind CSS 4 |
| Linting | oxlint |

---

## Getting started

### Prerequisites

- **Python 3.12 or newer**
- **[uv](https://docs.astral.sh/uv/)** for Python dependency management
- **Node.js 20 or newer** and npm

### Install

```bash
git clone <repository-url>
cd ZipSolver

# Backend — creates the virtualenv and installs everything from pyproject.toml
uv sync

# Frontend
cd frontend
npm ci
cd ..
```

`uv sync` installs the project itself, so `import backend` resolves from any working
directory and under any entry point (pytest, uvicorn, `python -m`, your IDE).

---

## Running the application

ZipSolver runs as two local processes. Start both.

**Terminal 1 — backend**

```bash
# Run from the repository root, not from backend/
uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8090
```

**Terminal 2 — frontend**

```bash
cd frontend
npm run dev
```

Open **http://localhost:5173**.

Interactive API documentation is generated from the Pydantic models and route signatures
at **http://localhost:8090/docs**.

### Why port 8090

Windows reserves TCP ranges that frequently include port 8000 (Hyper-V, WSL, and Docker
all claim blocks there), which made the conventional choice fail intermittently and
confusingly. 8090 sits outside those ranges.

To point the frontend somewhere else, set `VITE_API_URL`:

```bash
VITE_API_URL=http://127.0.0.1:9000 npm run dev
```

The backend accepts cross-origin requests from `http://localhost:5173` and
`http://127.0.0.1:5173` by default. Browsers treat those as distinct origins, so both are
allowed; pass `allowed_origins` to `BackendAPI` to change the list.

---

## API reference

Four endpoints. All responses are `application/json`.

| Method | Path | Request | 200 response |
|---|---|---|---|
| `POST` | `/api/solve` | `PuzzleRequest` (JSON) | `SolverResponse` |
| `POST` | `/api/import` | `multipart/form-data`: `file`, optional `board_size` | `ImportResult` |
| `GET` | `/api/health` | — | `HealthStatus` |
| `GET` | `/api/architecture` | — | `ArchitectureInfo` |

### `POST /api/solve`

```jsonc
// Request
{
  "boardSize": 6,
  "waypoints": [[0, 0], [2, 2], [4, 4]],
  "walls": [{ "neighborA": [0, 0], "neighborB": [1, 0] }]
}
```

```jsonc
// Response — 200
{
  "status": "SOLVED",
  "success": true,
  "solutionPath": [[0, 0], [1, 0], "..."],
  "solverUsed": "AlgorithmicSolver",
  "message": "Successfully solved using Algorithmic Fallback.",
  "metrics": { "runtimeMs": 3, "steps": 39, "attempts": 1 }
}
```

**A solver non-result is still HTTP 200.** `UNSOLVABLE`, `TIMEOUT`, and `FAILED` are
outcomes of a successfully processed request, not errors, so they come back as a 200 with
`solutionPath: null`. Only a bad *request* produces a 4xx.

| `status` | Meaning |
|---|---|
| `SOLVED` | A valid, re-validated path was found |
| `UNSOLVABLE` | The search proved no solution exists |
| `TIMEOUT` | A solver hit its fixed time limit |
| `FAILED` | No valid path found, or another solver failure |

### `POST /api/import`

Send the screenshot as `file` and the grid size the user already selected as `board_size`.
Supplying the size is strongly preferred: estimating it from pixels alone is unreliable on
the app's low-contrast rendering.

```jsonc
// Response — 200
{
  "board": { "boardSize": 6, "waypoints": [[0, 0], "..."], "walls": ["..."] },
  "valid": true,
  "message": "Board configuration is valid.",
  "errors": [],
  "warnings": [
    { "code": "WAYPOINT_NUMBER_UNREADABLE", "message": "...", "cell": [3, 1] }
  ]
}
```

`board` is returned **even when `valid` is false**, so the user can see what was read and
correct it instead of starting over. `errors` means the board is unusable as-is;
`warnings` means it was imported but something was read with low confidence.

### `GET /api/health`

A cheap in-process liveness probe. Deliberately touches neither the validation nor the
solver pipeline, so it stays answerable while those are degraded.

```json
{ "status": "ok", "apiVersion": "1.0.0", "modelLoaded": true }
```

`modelLoaded` is true only when a trained artifact exists on disk **and** the RL runtime
(Gymnasium, Stable-Baselines3, PyTorch) is importable — that is, only when the RL solver
could genuinely serve a request.

### `GET /api/architecture`

A read-only runtime inventory: framework and library versions, registered solvers, backend
components, and trained-model metadata. Surfaced in the frontend's advanced mode. Reports
names and versions only — never file paths, secrets, model weights, or environment
variables.

### Error responses

Every 4xx and 5xx uses one envelope:

```json
{
  "status": 422,
  "code": "INVALID_WALLS",
  "message": "Duplicate wall between (1, 0) and (0, 0).",
  "details": [{ "errorCode": "INVALID_WALLS", "affectedField": "walls", "message": "..." }],
  "timestamp": "2026-08-16T12:00:00+00:00"
}
```

| `code` | HTTP | Raised when |
|---|---|---|
| `MALFORMED_REQUEST` | 400 | Pydantic shape or type validation failed, or an unreadable upload |
| `UNSUPPORTED_BOARD_SIZE` | 422 | `boardSize` is not 6, 7, or 8 |
| `INVALID_WAYPOINTS` | 422 | Duplicate, out-of-bounds, or too few waypoints |
| `INVALID_WALLS` | 422 | Non-adjacent, out-of-bounds, or duplicate wall |
| `NO_BOARD_DETECTED` | 422 | A valid image, but no puzzle grid was found in it |
| `AMBIGUOUS_BOARD` | 422 | A grid was found but its size could not be resolved |
| `PAYLOAD_TOO_LARGE` | 413 | Request body exceeds the endpoint's fixed limit |
| `INTERNAL_ERROR` | 500 / 503 | Unexpected fault, or an optional collaborator is not configured |

---

## Data formats and conventions

### Coordinates

This is the one convention worth reading carefully, because the two halves of the stack
differ deliberately.

- **Backend and wire format:** `[x, y]`, where `x` is the column and `y` is the row.
- **Frontend:** `[row, col]`, matching how the grid is rendered and indexed in React.

Every coordinate crossing the boundary is transposed in `frontend/src/api/apiCalls.ts` —
in both directions, for waypoints, walls, and the returned solution path. Keeping the
translation in exactly one file means no other frontend or backend code needs to think
about it.

Both systems are 0-indexed with the origin at the top-left.

### Board configuration

```jsonc
{
  "boardSize": 6,                                              // 6 | 7 | 8
  "waypoints": [[0, 0], [2, 2], [4, 4]],                       // ordered: index = visit order
  "walls": [{ "neighborA": [0, 0], "neighborB": [1, 0] }],     // may be empty
  "solutionPath": []                                           // optional, ignored on input
}
```

Rules enforced by the backend:

| Field | Constraint |
|---|---|
| `boardSize` | Exactly 6, 7, or 8 |
| `waypoints` | At least 2, at most *n*², all in bounds, all distinct |
| `walls` | Both cells in bounds, cardinally adjacent, no duplicates (in either cell order) |

A wall is an **unordered** pair: `{A, B}` and `{B, A}` are the same wall, and declaring
both is a duplicate.

### Internal model

`Board` holds the static layout (size, waypoints, walls). `GameState` holds everything
that changes during a solving attempt (current position, path so far, visited cells).
`PuzzleRules` holds the rule checks, shared by the game, both solvers, and the validator —
so there is exactly one implementation of what "legal" means.

---

## Solving strategy

`SolverController` runs a two-stage strategy:

1. **`RLSolver`** performs one deterministic inference episode with the trained DQN agent.
2. If it produces no path, produces an invalid one, or raises, **`AlgorithmicSolver`**
   takes over.
3. Either way, any candidate path goes through `SolutionValidator` before it is returned.

The RL stack is imported lazily, on first use. Importing it eagerly pulls in
Gymnasium → Stable-Baselines3 → PyTorch, which previously made application startup — and
therefore `/api/health` — fail outright whenever those packages were missing. A missing RL
stack is now recorded once and the service degrades to the algorithmic solver, which is
exactly what a fallback is for.

### The algorithmic solver is A\*, not DFS

Earlier design documents call it a DFS fallback. It is an **A\* search**, and some comments
and identifiers still carry the old name. It uses:

- **Bitmask visited-set tracking**, so state comparison and copying are integer operations.
- **A summed Manhattan heuristic** across all remaining waypoint legs, not just the next
  one, which is admissible and far better informed.
- **Flood-fill pruning** that discards any state where the unvisited region has been split
  into pieces the path can no longer reach.
- **Parity checking** to reject provably impossible boards before searching at all.

Together these took a sparse 8×8 board from timing out to solving in roughly 31 ms.

---

## Reinforcement learning

The agent is trained **offline**. At runtime the backend only loads an already-trained
artifact and performs inference — no training code runs in the request path, and no
training functionality is exposed through the API.

| Aspect | Implementation |
|---|---|
| Algorithm | DQN (Stable-Baselines3) |
| Observation | 8 channels of *n* × *n*, values in `[0, 1]` |
| Action space | `Discrete(4)` — up, right, down, left |
| Feature extractor | `ZipCNN`, three convolutional layers into a 128-dim dense head |
| Episode budget | *n*² − 1 steps (the start cell counts as already visited) |
| Rewards | +200 completion, +25 per waypoint reached in order, +2 per new cell, −0.01 per step, −10 invalid move |

`offline_training/` holds the training orchestration (`AgentTrainer`), the board generator,
pre-generated training and evaluation board pools, and the trained artifacts under
`trained_models/<size>/`. Training runs were executed on the bwUniCluster.

Only a 6×6 model currently ships. Boards of other sizes are served by the algorithmic
solver, which handles them correctly — the fallback is a first-class path, not a
degraded one.

---

## Screenshot import

`backend/input_validation/screenshot/` turns an uploaded image into a board configuration
through a staged pipeline:

```
ImageLoader → PaletteDetector → GridLocalizer → WaypointDetector → WallDetector
```

- **`ImageLoader`** decodes the upload, applies EXIF rotation so phone photos arrive
  upright, caps the longest edge at 2048 px, and rejects anything over 10 MiB.
- **`PaletteDetector`** determines whether the screenshot is light or dark themed, since
  every downstream threshold depends on it.
- **`GridLocalizer`** finds the grid and computes per-cell bounding boxes using
  circle-anchored geometry: waypoint discs give a reliable pitch estimate, and the panel
  centre gives the origin.
- **`WaypointDetector`** reads the marker positions and their numbers.
- **`WallDetector`** inspects each interior cell boundary exactly once.

The pipeline is **best-effort**, which is the important design decision. Marker *positions*
are reliable; marker *numbers* are not, because reading digits accurately needs a trained
OCR model the project does not have. So a low-confidence read becomes a `warning` on an
otherwise successful import rather than a hard failure — the user checks two numbers
instead of abandoning the import.

Failures are typed rather than lumped together, because the remedies differ:
"that file isn't an image" (400), "that image has no board in it" (422
`NO_BOARD_DETECTED`), and "there's a board but I can't size it" (422 `AMBIGUOUS_BOARD`)
each tell the user something different.

**Known limitation:** digit recognition accuracy is bounded by the absence of a trained OCR
model. Always confirm imported waypoint numbers before solving.

---

## Testing

```bash
# Everything
uv run pytest -q

# By surface
uv run pytest backend/tests/api -q          # API layer: contracts, routing, errors, orchestration
uv run pytest backend/tests/unit -q         # Puzzle logic, validators, solvers, screenshot pipeline
uv run pytest offline_training/tests -q     # Board generation

# Frontend
cd frontend
npx tsc --noEmit -p tsconfig.app.json       # Type check
npm run lint                                # oxlint
npm run build                               # Production build
```

The API suite stubs collaborators at their Protocol boundaries, so it exercises routing,
schema contracts, the error taxonomy, and call ordering without depending on solver or
CV internals. The unit suite tests those internals directly. There are no automated
frontend tests; frontend behaviour is verified manually.

---

## Project layout

```
ZipSolver/
├── run_api.py                     # ASGI entry point — wires the real collaborators
├── pyproject.toml                 # Dependencies, packaging, pytest configuration
│
├── backend/
│   ├── api/
│   │   ├── BackendAPI.py          # FastAPI app: routes, middleware, exception handlers
│   │   ├── solver_result_adapter.py   # Internal solver result → API DTO
│   │   ├── version.py             # Single source of truth for the service version
│   │   ├── dtos/                  # Request/response schemas
│   │   ├── solver_dtos/           # SolverStatus, SolverMetrics
│   │   └── architecture_provider/ # Runtime inventory for /api/architecture
│   │
│   ├── input_validation/
│   │   ├── json_interpreter.py    # Payload → Board (structural)
│   │   ├── input_validator.py     # Board → ValidationResult (semantic)
│   │   ├── validation_dtos.py     # ValidationResult / ValidationError
│   │   ├── errors.py              # Typed parse errors carrying taxonomy codes
│   │   └── screenshot/            # Image → board configuration pipeline
│   │
│   ├── puzzle_logic/              # Board, Game, GameState, PuzzleRules, Position, Wall
│   ├── solving_process/           # SolverController, RLSolver, AlgorithmicSolver
│   ├── rl_components/             # RLEnvironment, RLAgent, EnvironmentConfig
│   ├── solution_validator.py      # Final Zip-rule check on any candidate path
│   └── tests/                     # pytest suites
│
├── offline_training/
│   ├── agent_trainer.py           # Training orchestration
│   ├── board_generator.py         # Random board generation
│   ├── training_boards/           # Pre-generated training pools
│   ├── evaluation_boards/         # Held-out evaluation sets
│   └── trained_models/            # Trained artifacts, by board size
│
└── frontend/
    └── src/
        ├── api/                   # apiClient (transport, errors), apiCalls (endpoints)
        ├── components/            # Grid, GridBuilder, panels, modals
        ├── types/                 # Mirrors of the backend contracts
        ├── utils/                 # Share links, play mode, game rules, file validation
        └── data/                  # Example puzzles, help content, UI copy
```

---

## Troubleshooting

**"Could not reach the ZipSolver backend"**
The backend isn't running, or it's on a different port. Start it from the repository root
and confirm `curl http://127.0.0.1:8090/api/health` responds.

**`ModuleNotFoundError: No module named 'backend'`**
Uvicorn was started from inside `backend/`. `run_api.py` lives at the repository root — run
it from there. If it persists, `uv sync` again to reinstall the project into the venv.

**CORS errors in the browser console**
The frontend is on an origin the backend doesn't allow. `localhost:5173` and
`127.0.0.1:5173` both work out of the box; anything else needs to be passed to
`BackendAPI(allowed_origins=[...])`.

**`/api/health` reports `modelLoaded: false`**
Either no trained artifact is present under `offline_training/trained_models/`, or the RL
runtime isn't installed. The application still solves every board via the algorithmic
fallback — this is a degraded, not a broken, state.

**The solver always reports `AlgorithmicSolver`**
Expected for 7×7 and 8×8, which have no trained model yet. For 6×6, check
`/api/health` and the backend log for an "RL solver unavailable" warning.

**A screenshot import reads the wrong numbers**
A known limitation — digit recognition has no trained OCR model behind it. Correct the
waypoints in the editor before solving. Full-window screenshots at native resolution read
considerably better than cropped or rescaled ones.

**`uv sync` fails to resolve**
Check your Python version: `python --version`. The project needs 3.12 or newer.

---

## Team

Vincent Heddergott · Tillmann Nickels · Franz Jakob Lutz · Dmitrii Russkikh ·
Henrik Bruder · Samoon Bharmal

Supervisors: Tara Gheshlaghi, Seyedehmaryam Ghasemi
Chair of Dependable Nano Computing (CDNC), Karlsruhe Institute of Technology
