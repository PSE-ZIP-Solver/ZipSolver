"""Measure sequential API requests and validate expected behavior.

Default: live HTTP against a separately started server. --in-process uses the
production run_api application via TestClient and excludes network/Uvicorn costs.
No solver outcomes are mocked. No training or model-performance claims are made.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]


def latency(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    def percentile(p: float) -> float | None:
        if not ordered:
            return None
        index = (len(ordered) - 1) * p
        low = math.floor(index)
        high = math.ceil(index)
        return round(ordered[low] + (ordered[high] - ordered[low]) * (index-low), 3)
    return {"samples": len(values), "minMs": min(ordered) if ordered else None,
            "medianMs": percentile(.5), "p95Ms": percentile(.95),
            "maxMs": max(ordered) if ordered else None}


def scenarios() -> list[dict[str, Any]]:
    # Every cell is a waypoint on a known snake: bounded, unambiguous solution.
    snake = [[x, y] for y in range(6)
             for x in (range(6) if y % 2 == 0 else range(5, -1, -1))]
    solve = {"boardSize": 6, "waypoints": snake, "walls": []}
    blocked = {"boardSize": 6, "waypoints": [[0, 0], [5, 5]], "walls": [
        {"neighborA": [0, 0], "neighborB": [1, 0]},
        {"neighborA": [0, 0], "neighborB": [0, 1]}]}
    cases = [
        {"id": "health", "method": "GET", "path": "/api/health", "status": 200},
        {"id": "architecture", "method": "GET", "path": "/api/architecture", "status": 200},
        {"id": "solve-valid", "method": "POST", "path": "/api/solve",
         "status": 200, "json": solve, "solution": snake, "outcome": "SOLVED"},
        {"id": "solve-unsolvable", "method": "POST", "path": "/api/solve",
         "status": 200, "json": blocked, "outcome": "UNSOLVABLE"},
        {"id": "solve-malformed", "method": "POST", "path": "/api/solve",
         "status": 400, "json": {}, "code": "MALFORMED_REQUEST"},
        {"id": "solve-invalid", "method": "POST", "path": "/api/solve",
         "status": 422, "json": {"boardSize": 5, "waypoints": [[0,0],[4,4]], "walls": []},
         "code": "UNSUPPORTED_BOARD_SIZE"},
    ]
    fixtures = ROOT / "backend/tests/fixtures/screenshots"
    truth = json.loads((fixtures / "expected_boards.json").read_text(encoding="utf-8"))
    for theme in ("light", "dark"):
        cases.append({"id": f"import-{theme}", "method": "POST", "path": "/api/import",
                      "status": 200, "payload": (fixtures/f"6x6-{theme}.png").read_bytes(),
                      "board": truth["6x6"]})
    cases.append({"id": "import-corrupt", "method": "POST", "path": "/api/import",
                  "status": 400, "payload": b"not an image", "code": "MALFORMED_REQUEST"})
    return cases


def canonical_board(board: dict[str, Any]) -> dict[str, Any]:
    return {"boardSize": board["boardSize"], "waypoints": board["waypoints"],
            "walls": sorted(sorted([w["neighborA"], w["neighborB"]]) for w in board["walls"])}


def check(case: dict[str, Any], status: int, body: Any) -> list[str]:
    errors: list[str] = []
    if status != case["status"]:
        errors.append(f"Expected HTTP {case['status']}, got {status}")
    if not isinstance(body, dict):
        return errors + ["Response is not a JSON object"]
    try:
        if "code" in case:
            assert body["code"] == case["code"] and body["status"] == case["status"]
            assert isinstance(body["message"], str) and body["message"]
            assert "details" in body
            assert datetime.fromisoformat(body["timestamp"]).utcoffset() is not None
        elif "outcome" in case:
            assert body["status"] == case["outcome"]
            assert body["success"] is (case["outcome"] == "SOLVED")
            assert body["solutionPath"] == case.get("solution")
            assert body["solverUsed"] in ("RLSolver", "AlgorithmicSolver")
            for key, minimum in (("runtimeMs", 0), ("steps", 0), ("attempts", 1)):
                assert type(body["metrics"][key]) is int and body["metrics"][key] >= minimum
        elif "board" in case:
            assert body["valid"] is True and body["errors"] == [] and body["warnings"] == []
            assert canonical_board(body["board"]) == canonical_board(case["board"])
        elif case["id"] == "health":
            assert body["status"] == "ok" and isinstance(body["apiVersion"], str)
            assert body["modelLoaded"] is None or type(body["modelLoaded"]) is bool
        else:
            assert isinstance(body["apiVersion"], str)
            assert {s["name"] for s in body["solvers"]} == {"RLSolver", "AlgorithmicSolver"}
            assert type(body["reinforcementLearning"]["model"]["loaded"]) is bool
    except (AssertionError, KeyError, TypeError, ValueError):
        errors.append("Response content violates scenario expectations")
    return errors


def stable_body(body: Any) -> Any:
    if not isinstance(body, dict):
        return body
    copy = dict(body)
    copy.pop("timestamp", None)
    if isinstance(copy.get("metrics"), dict):
        copy["metrics"] = dict(copy["metrics"])
        copy["metrics"].pop("runtimeMs", None)
    return copy


def request(client: Any, case: dict[str, Any], iteration: int) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if "json" in case:
        kwargs["json"] = case["json"]
    if "payload" in case:
        kwargs.update(files={"file": ("board.png", case["payload"], "image/png")},
                      data={"board_size": "6"})
    started = perf_counter()
    try:
        response = client.request(case["method"], case["path"], **kwargs)
        # Measure receipt of the full response; validation is outside the timer.
        elapsed = (perf_counter()-started)*1000
        try:
            body = response.json()
        except ValueError:
            body = response.text[:2000]
        errors = check(case, response.status_code, body)
        status = response.status_code
    except httpx.RequestError as exc:
        elapsed = (perf_counter()-started)*1000
        body, status, errors = None, None, [f"{type(exc).__name__}: {exc}"]
    return {"case": case["id"], "endpoint": case["method"]+" "+case["path"],
            "iteration": iteration, "httpStatus": status, "expectedStatus": case["status"],
            "latencyMs": round(elapsed, 3), "passed": not errors, "errors": errors,
            "body": body}


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"requests": len(rows), "passed": sum(r["passed"] for r in rows),
            "expectationMatchRate": sum(r["passed"] for r in rows)/len(rows) if rows else None,
            "statusCounts": dict(Counter(str(r["httpStatus"]) if r["httpStatus"] is not None
                                        else "transport_error" for r in rows)),
            "solverUsedCounts": dict(Counter(r["body"]["solverUsed"] for r in rows
                                             if isinstance(r["body"], dict) and r["body"].get("solverUsed"))),
            "solverOutcomeCounts": dict(Counter(r["body"]["status"] for r in rows
                                                if isinstance(r["body"], dict) and r["body"].get("solverUsed"))),
            "transportErrors": sum(r["httpStatus"] is None for r in rows),
            "serverErrors": sum(r["httpStatus"] is not None and r["httpStatus"] >= 500 for r in rows),
            "latency": latency([r["latencyMs"] for r in rows])}


def run(client: Any, cases: list[dict[str, Any]], repetitions: int, warmups: int) -> dict[str, Any]:
    warmup_rows = [request(client, case, i) for i in range(warmups) for case in cases]
    # Round-robin order deliberately interleaves valid, invalid, import, and diagnostics.
    rows = [request(client, case, i) for i in range(repetitions) for case in cases]
    groups = {c["id"]: [r for r in rows if r["case"] == c["id"]] for c in cases}
    stability = {key: all(stable_body(r["body"]) == stable_body(group[0]["body"]) for r in group)
                 for key, group in groups.items()}
    return {"summary": summarize(rows),
            "byEndpoint": {key: summarize([r for r in rows if r["endpoint"] == key])
                           for key in sorted({r["endpoint"] for r in rows})},
            "byCase": {key: {**summarize(group), "responseStable": stability[key]}
                       for key, group in groups.items()},
            "warmups": warmup_rows, "requests": rows}


def write(result: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output/"metrics.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    with (output/"requests.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case", "endpoint", "iteration", "http_status", "expected_status",
                         "latency_ms", "passed", "errors"])
        for r in result["requests"]:
            writer.writerow([r["case"], r["endpoint"], r["iteration"], r["httpStatus"],
                             r["expectedStatus"], r["latencyMs"], r["passed"], "; ".join(r["errors"])])
    lines = ["# API evaluation", "", f"Mode: {result['execution']['mode']}",
             f"Generated: {result['generatedAt']}", "",
             "Sequential, round-robin requests; warmups excluded from timing summaries.",
             "Expected 400/422 rejections count as correct behavior. HTTP 200 alone is insufficient.",
             "In-process times exclude network and Uvicorn. Live HTTP times depend on client, server, and network.",
             "This is a fixed functional workload, not concurrent load capacity or model accuracy.", "",
             "| Scenario | Matches / requests | Median ms | p95 ms | Stable |",
             "| --- | ---: | ---: | ---: | --- |"]
    for name, group in result["byCase"].items():
        lines.append(f"| {name} | {group['passed']}/{group['requests']} | "
                     f"{group['latency']['medianMs']} | {group['latency']['p95Ms']} | {group['responseStable']} |")
    lines += ["", "See metrics.json for endpoint aggregates, actual responses, status counts, warmups,",
              "environment, and inputs. requests.csv has one measured request per row.",
              "The fully waypoint-constrained snake is intentionally easy; its timing does not",
              "represent arbitrary puzzles. Model availability and solverUsed affect comparisons.",
              "Stability excludes timestamps and solver runtimeMs; other fields are compared.",
              "No requests-per-second capacity claim is derived from these sequential timings.", ""]
    (output/"report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8090")
    parser.add_argument("--in-process", action="store_true")
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"evaluation_results/api")
    args = parser.parse_args()
    if args.repetitions < 1 or args.warmups < 0 or args.timeout <= 0:
        parser.error("repetitions >= 1, warmups >= 0, timeout > 0 required")
    cases = scenarios()  # Read all required fixtures before making any requests.
    if args.in_process:
        from fastapi.testclient import TestClient
        from run_api import app
        client = TestClient(app, raise_server_exceptions=False)
    else:
        client = httpx.Client(base_url=args.base_url.rstrip("/"), timeout=args.timeout,
                              follow_redirects=False, trust_env=False)
    with client:
        result = run(client, cases, args.repetitions, args.warmups)
    result.update(schemaVersion=1, generatedAt=datetime.now(timezone.utc).isoformat(),
                  execution={"mode": "in-process" if args.in_process else "live HTTP",
                             "baseUrl": None if args.in_process else args.base_url,
                             "repetitions": args.repetitions, "warmupsPerCase": args.warmups,
                             "python": platform.python_version(), "clientPlatform": platform.platform(),
                             "serverEnvironment": "same process" if args.in_process else "record separately",
                             "timeoutSeconds": None if args.in_process else args.timeout},
                  scenarios=[{**{k:v for k,v in c.items() if k != "payload"},
                              **({"payloadSha256": hashlib.sha256(c["payload"]).hexdigest()}
                                 if "payload" in c else {})} for c in cases])
    write(result, args.output_dir)
    failures = sum(not r["passed"] for r in result["requests"]+result["warmups"])
    unstable = sum(not g["responseStable"] for g in result["byCase"].values())
    print(f"Measured: {result['summary']['passed']}/{len(result['requests'])} expectations matched.")
    print(f"Failures including warmups: {failures}; unstable scenarios: {unstable}")
    print(f"Results: {args.output_dir.resolve()}")
    return int(bool(failures or unstable))


if __name__ == "__main__":
    raise SystemExit(main())
