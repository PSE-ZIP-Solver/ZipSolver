# Wire GET /api/health and GET /api/architecture

Copy the files in this folder over the same paths in `ZipSolver-dev`, preserving the
directory structure.

## Files

| Path | Change |
|---|---|
| `backend/api/version.py` | new |
| `backend/api/dtos/HealthStatus.py` | new |
| `backend/api/dtos/__init__.py` | modified — exports `HealthStatus` |
| `backend/api/BackendAPI.py` | modified — 2 routes, 2 handlers, 1 exception, 1 handler |
| `backend/api/architecture_provider/ArchitectureProvider.py` | modified — uses `API_VERSION` |
| `run_api.py` | modified — injects real `ArchitectureProvider` |

## Verify

```powershell
uv sync
uv run pytest backend/tests/unit/puzzle_logic -q
uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8090
```

```powershell
curl.exe http://127.0.0.1:8090/api/health
curl.exe http://127.0.0.1:8090/api/architecture
curl.exe -X POST http://127.0.0.1:8090/api/solve -H "Content-Type: application/json" -d '{\"boardSize\":6,\"waypoints\":[[0,0],[5,5]],\"walls\":[]}'
```

Swagger UI: <http://127.0.0.1:8090/docs>

## Expected

```
GET  /api/health        200  {"status":"ok","apiVersion":"1.0.0","modelLoaded":false}
GET  /api/architecture  200  ArchitectureInfo
POST /api/solve         200  SolverResponse
POST /api/import        200  ValidationResult
```