# HowToRunTests.md

## Prerequisites

```powershell
uv sync
uv run python -c "import backend; print('OK')"
```

## Run everything

```powershell
uv run pytest backend/tests/api -q
```

## Run one file

```powershell
uv run pytest backend/tests/api/test_endpoint_integration.py -q
uv run pytest backend/tests/api/test_contract_validation.py -q
uv run pytest backend/tests/api/test_orchestration_flow.py -q
uv run pytest backend/tests/api/test_error_propagation.py -q
```

## Run one class or test

```powershell
uv run pytest "backend/tests/api/test_contract_validation.py::TestPuzzleRequest" -q
uv run pytest "backend/tests/api/test_error_propagation.py::test_500_message_is_generic" -q
```

## Run by marker

```powershell
uv run pytest backend/tests/api -m contract -q
uv run pytest backend/tests/api -m "not contract" -q
```

## Run by keyword

```powershell
uv run pytest backend/tests/api -k "health" -q
uv run pytest backend/tests/api -k "solve or import" -q
uv run pytest backend/tests/api -k "400 or 422 or 500" -q
```

## Verbose / list

```powershell
uv run pytest backend/tests/api -v
uv run pytest backend/tests/api --collect-only -q
```

## Coverage

```powershell
uv run pytest backend/tests/api --cov=backend/api --cov-report=term-missing
```

```powershell
uv run pytest backend/tests/api --cov=backend/api --cov-report=html
start htmlcov/index.html
```

## Failure diagnosis

```powershell
uv run pytest backend/tests/api -x -q
uv run pytest backend/tests/api --lf -q
uv run pytest backend/tests/api -q --tb=long
uv run pytest backend/tests/api -q -s
uv run pytest backend/tests/api -q --durations=10
```

## Direct execution (VS Code play button)

```powershell
uv run python backend/tests/api/test_orchestration_flow.py
uv run python backend/tests/api/test_contract_validation.py
uv run python backend/tests/api/test_endpoint_integration.py
uv run python backend/tests/api/test_error_propagation.py
```

## VS Code Test Explorer

```
Ctrl+Shift+P  ->  Python: Select Interpreter  ->  Workspace (.venv\Scripts\python.exe)
Ctrl+Shift+P  ->  Test: Refresh Tests
Ctrl+Shift+P  ->  Test: Run All Tests
```

## Type check

```powershell
npx --yes pyright backend/api backend/tests/api run_api.py
```

## Live server verification

```powershell
uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8090
```

```powershell
curl.exe http://127.0.0.1:8090/api/health
curl.exe http://127.0.0.1:8090/api/architecture
```

```powershell
curl.exe -X POST http://127.0.0.1:8090/api/solve `
  -H "Content-Type: application/json" `
  -d '{\"boardSize\":6,\"waypoints\":[[0,0],[5,5]],\"walls\":[]}'
```

```powershell
curl.exe -X POST http://127.0.0.1:8090/api/import `
  -H "Content-Type: application/json" `
  -d '{\"boardSize\":6,\"waypoints\":[[0,0],[5,5]],\"walls\":[]}'
```

```powershell
curl.exe -X POST http://127.0.0.1:8090/api/solve `
  -H "Content-Type: application/json" `
  -d '{\"boardSize\":\"six\"}'
```

```powershell
start http://127.0.0.1:8090/docs
```

## Expected

```
185 passed
backend/api  99%  (BackendAPI.py 100%)
pyright      0 errors
```

## Non-blocking known issues

```powershell
# Aborts with 4 collection errors in solving_process / rl_components (other owners)
uv run pytest

# Use this instead until fixed
uv run pytest backend/tests/api backend/tests/unit/puzzle_logic -q
```

```powershell
# Port 8000 is Windows-reserved -> use 8090
netsh interface ipv4 show excludedportrange protocol=tcp
```

## Rebuild venv

```powershell
Remove-Item -Recurse -Force .venv, *.egg-info, .pytest_cache -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
uv venv --python 3.13
uv sync
uv run pytest backend/tests/api -q
```