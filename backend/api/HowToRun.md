```bash
uv add fastapi "uvicorn[standard]" httpx tensorboard
uv sync
uv run pytest -q
cd frontend
npm ci
npm run build
npm run lint
cd ..
uv run uvicorn run_api:app --reload --host 127.0.0.1 --port 8000
```
