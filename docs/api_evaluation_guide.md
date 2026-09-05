# API statistics: run and interpret

Use two terminals, both in the ZipSolver repository root. Use your normal installed project environment.

Terminal 1: start the production application without development reload.

```powershell
uv run uvicorn run_api:app --host 127.0.0.1 --port 8090
```

Terminal 2: measure live HTTP.

```powershell
uv run python scripts/evaluate_api.py --repetitions 20 --warmups 1
```

The script uses nine scenarios: health, architecture, a solvable 6x6 board, an unsolvable board, malformed and semantically invalid requests, light/dark screenshot imports, and a corrupt image. It needs the existing 6x6-light.png, 6x6-dark.png and expected_boards.json under backend/tests/fixtures/screenshots/.

Every measurement round interleaves these scenarios. The default run records 180 measured requests plus nine warmup requests. Start with this local target; use --base-url only for a server you are authorized to test.

## Output

Files are overwritten under evaluation_results/api/ (change with --output-dir).

- **report.md**: concise scenario table for the testing report.
- **metrics.json**: overall, per-endpoint and per-scenario counts and latency; each actual response; warmup evidence; inputs and image hashes; client environment.
- **requests.csv**: one measured request per row, suitable for Excel. Warmups appear only in JSON.

**Expectation-match rate** counts requests with the expected status AND response content. Expected HTTP 400/422 errors are passes. SOLVED and UNSOLVABLE both use HTTP 200, with different checked bodies. Server errors and transport failures have separate counters. Do not describe expectation-match rate as an HTTP-2xx rate.

**Median** is the middle latency. **p95** is the linearly interpolated 95th percentile. Timing ends when the full response is received and excludes assertion checks. Warmups are excluded from summaries but their failures still fail the run. Report per-scenario timings first: endpoint totals mix cheap rejections with more expensive valid work.

**Stable** compares repeated bodies after removing error timestamps and solver runtimeMs. Changes in paths, solver selection, other metrics, or diagnostics remain visible. With one repetition stability is not meaningfully established; use the default 20.

Exit 0 means every measured and warmup response matched and repeated bodies were stable. Exit 1 means failures or instability were recorded; the output files are still written. Missing fixture files or invalid arguments abort setup instead.

## Scope and reproducibility

This is a sequential functional workload, not a concurrency/load-capacity benchmark. The valid board is a deliberately simple, fully waypoint-constrained snake. Its latency cannot represent arbitrary puzzle difficulty or RL accuracy.

The real production run_api application and solvers are used. Missing RL dependencies or model archives may cause A* fallback. Inspect solverUsed in actual responses and modelLoaded in diagnostics. Record the server commit, model files, hardware, Python/dependency versions, and whether it shares the client machine. Live mode records client environment, not remote server hardware.

Optional backend-only comparison:

```powershell
uv run python scripts/evaluate_api.py --in-process --output-dir evaluation_results/api_in_process
```

In-process mode runs the real app via TestClient, excluding Uvicorn and network. Its timeout option does not impose a solver deadline. Keep those figures separate from live HTTP results.

Postman is optional for demonstrations; this evaluator already provides repeatable request evidence and timing. Use the local run's output for the final report, and preserve it before rerunning.
