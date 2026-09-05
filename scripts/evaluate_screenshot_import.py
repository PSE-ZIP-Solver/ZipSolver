"""Evaluate screenshot import through the real POST /api/import route.

The evaluator reads a versioned manifest, repeats each request for timing, and
writes machine-readable JSON/CSV plus a Markdown report suitable for the testing
report appendix. It deliberately does not start Uvicorn: timings describe the
in-process backend pipeline and are not network/load-test measurements.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from importlib.metadata import version
import json
import platform
import statistics
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image, ImageFilter, ImageOps

from backend.api.BackendAPI import BackendAPI
from backend.input_validation.input_validator import InputValidator
from backend.input_validation.json_interpreter import JsonInterpreter
from backend.input_validation.screenshot import ScreenshotExtractor
from backend.solving_process.solver_controller import SolverController

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPOSITORY_ROOT
    / "backend"
    / "tests"
    / "fixtures"
    / "screenshots"
    / "evaluation_manifest.json"
)
DEFAULT_OUTPUT = REPOSITORY_ROOT / "evaluation_results" / "screenshot_import"


class _UnavailableRLSolver:
    """Avoid loading a model for an endpoint that never invokes the solver."""

    def solve(self, _board):
        raise FileNotFoundError("RL model is unavailable")


def _make_client() -> TestClient:
    api = BackendAPI(
        JsonInterpreter(),
        InputValidator(),
        SolverController(rl_solver=_UnavailableRLSolver()),
        screenshot_extractor=ScreenshotExtractor(),
    )
    return TestClient(api.app, raise_server_exceptions=False)


def _encode_image(image: Image.Image, image_format: str, **options: Any) -> bytes:
    output = BytesIO()
    image.save(output, format=image_format, **options)
    return output.getvalue()


def _transformed_payload(
    source: bytes, transformation: dict[str, Any]
) -> tuple[bytes, str, str]:
    """Apply one deterministic robustness transformation to a source screenshot."""

    with Image.open(BytesIO(source)) as opened:
        image = opened.convert("RGB")

    kind = transformation["type"]
    if kind == "scale":
        factor = float(transformation["factor"])
        if factor <= 0:
            raise ValueError("scale factor must be greater than zero")
        image = image.resize(
            (
                max(1, round(image.width * factor)),
                max(1, round(image.height * factor)),
            ),
            Image.Resampling.LANCZOS,
        )
        return _encode_image(image, "PNG"), "image/png", "png"
    if kind == "jpeg":
        quality = int(transformation["quality"])
        return (
            _encode_image(image, "JPEG", quality=quality, optimize=True),
            "image/jpeg",
            "jpg",
        )
    if kind == "gaussianBlur":
        radius = float(transformation["radius"])
        image = image.filter(ImageFilter.GaussianBlur(radius))
        return _encode_image(image, "PNG"), "image/png", "png"
    if kind == "pad":
        pixels = int(transformation["pixels"])
        colour = tuple(int(channel) for channel in transformation["rgb"])
        image = ImageOps.expand(image, border=pixels, fill=colour)
        return _encode_image(image, "PNG"), "image/png", "png"
    if kind == "crop":
        pixels = int(transformation["pixels"])
        if pixels < 0 or pixels * 2 >= min(image.size):
            raise ValueError("crop pixels must leave a non-empty image")
        image = image.crop(
            (pixels, pixels, image.width - pixels, image.height - pixels)
        )
        return _encode_image(image, "PNG"), "image/png", "png"
    raise ValueError(f"Unsupported screenshot transformation: {kind!r}")


def _payload(case: dict[str, Any], dataset_dir: Path) -> tuple[str, bytes, str]:
    if "image" in case:
        path = dataset_dir / case["image"]
        source = path.read_bytes()
        transformation = case.get("transformation")
        if transformation:
            payload, content_type, extension = _transformed_payload(
                source, transformation
            )
            return f"{case['id']}.{extension}", payload, content_type
        content_type = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        return path.name, source, content_type
    if "syntheticSolidRgb" in case:
        output = BytesIO()
        Image.new("RGB", (600, 600), tuple(case["syntheticSolidRgb"])).save(
            output, format="PNG"
        )
        return f"{case['id']}.png", output.getvalue()
    raise ValueError(
        f"Case {case.get('id')!r} defines neither image nor syntheticSolidRgb"
    )


def _expanded_cases(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand compact base-case/variant manifests while retaining v1 compatibility."""

    if "cases" in manifest:
        return list(manifest["cases"])

    expanded: list[dict[str, Any]] = []
    for base in manifest["baseCases"]:
        for variant in manifest["variants"]:
            variant_id = variant["id"]
            case = {
                **base,
                "id": (
                    base["id"]
                    if variant_id == "original"
                    else f"{base['id']}--{variant_id}"
                ),
                "condition": variant_id,
                "sourceKind": variant.get("sourceKind", "derived_robustness"),
            }
            if "transformation" in variant:
                transformation = dict(variant["transformation"])
                if transformation["type"] == "pad":
                    transformation["rgb"] = base["backgroundRgb"]
                case["transformation"] = transformation
            case.pop("backgroundRgb", None)
            expanded.append(case)

    for negative in manifest.get("negativeCases", []):
        expanded.append(
            {
                **negative,
                "condition": negative.get("condition", "negative"),
                "sourceKind": negative.get("sourceKind", "synthetic_negative"),
            }
        )
    return expanded


def _point(value: Any) -> tuple[int, int]:
    """Convert one JSON coordinate to the evaluator's fixed two-int type."""

    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"Invalid coordinate in evaluation data: {value!r}")
    return int(value[0]), int(value[1])


def _wall_set(
    board: dict[str, Any] | None,
) -> set[tuple[tuple[int, int], tuple[int, int]]]:
    if not board:
        return set()
    walls: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for wall in board.get("walls", []):
        first = _point(wall["neighborA"])
        second = _point(wall["neighborB"])
        walls.add((first, second) if first <= second else (second, first))
    return walls


def _position_set(board: dict[str, Any] | None) -> set[tuple[int, int]]:
    if not board:
        return set()
    return {_point(position) for position in board.get("waypoints", [])}


def _exact_board(actual: dict[str, Any] | None, expected: dict[str, Any]) -> bool:
    return bool(
        actual
        and actual.get("boardSize") == expected["boardSize"]
        and actual.get("waypoints") == expected["waypoints"]
        and _wall_set(actual) == _wall_set(expected)
        and len(actual.get("walls", [])) == len(expected["walls"])
    )


def _counts(actual: set[Any], expected: set[Any]) -> dict[str, int]:
    return {
        "tp": len(actual & expected),
        "fp": len(actual - expected),
        "fn": len(expected - actual),
    }


def _stable_response(
    response: tuple[int, dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    """Remove response fields that are intentionally different per request."""

    status, body = response
    comparable = dict(body)
    comparable.pop("timestamp", None)
    return status, comparable


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _prf(counts: dict[str, int]) -> dict[str, float | int | None]:
    precision = _ratio(counts["tp"], counts["tp"] + counts["fp"])
    recall = _ratio(counts["tp"], counts["tp"] + counts["fn"])
    f1 = _ratio(2 * counts["tp"], 2 * counts["tp"] + counts["fp"] + counts["fn"])
    return {**counts, "precision": precision, "recall": recall, "f1": f1}


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return round(ordered[lower] * (1 - fraction) + ordered[upper] * fraction, 3)


def _latency(values: list[float]) -> dict[str, float | int | None]:
    return {
        "samples": len(values),
        "minMs": round(min(values), 3) if values else None,
        "medianMs": round(statistics.median(values), 3) if values else None,
        "p95Ms": _percentile(values, 0.95),
        "maxMs": round(max(values), 3) if values else None,
    }


def _sum_counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return {
        name: sum(row.get(field, {}).get(name, 0) for row in rows)
        for name in ("tp", "fp", "fn")
    }


def _group_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if row["expectedOutcome"] == "success"]
    invalid = [row for row in rows if row["expectedOutcome"] == "error"]
    return {
        "cases": len(rows),
        "validCases": len(valid),
        "negativeCases": len(invalid),
        "successfulImportRate": _ratio(
            sum(row["importSucceeded"] for row in valid), len(valid)
        ),
        "exactBoardAccuracy": _ratio(
            sum(row["exactBoard"] for row in valid), len(valid)
        ),
        "waypointOrderAccuracy": _ratio(
            sum(row["waypointOrderExact"] for row in valid), len(valid)
        ),
        "warningFreeRate": _ratio(sum(row["warningFree"] for row in valid), len(valid)),
        "expectedErrorAccuracy": _ratio(
            sum(row["expectedErrorMatched"] for row in invalid), len(invalid)
        ),
        "waypointPositions": _prf(_sum_counts(valid, "waypointPositionCounts")),
        "walls": _prf(_sum_counts(valid, "wallCounts")),
        "latency": _latency([sample for row in rows for sample in row["latencyMs"]]),
    }


def evaluate(manifest_path: Path, repetitions: int) -> dict[str, Any]:
    if repetitions < 1:
        raise ValueError("repetitions must be at least 1")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        manifest_display = manifest_path.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        manifest_display = str(manifest_path)
    dataset_dir = manifest_path.parent
    ground_truth = json.loads(
        (dataset_dir / manifest["groundTruth"]).read_text(encoding="utf-8")
    )
    cases = _expanded_cases(manifest)
    ids = [case["id"] for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ValueError("Manifest must contain non-empty, uniquely named cases")
    for case in cases:
        if ("expectedBoardKey" in case) == ("expectedError" in case):
            raise ValueError(f"Case {case['id']} must define exactly one expected outcome")
        if "expectedBoardKey" in case:
            ground_truth[case["expectedBoardKey"]]
    rows: list[dict[str, Any]] = []

    with _make_client() as client:
        for case in cases:
            filename, payload, content_type = _payload(case, dataset_dir)
            responses: list[tuple[int, dict[str, Any]]] = []
            elapsed_ms: list[float] = []
            for _ in range(repetitions):
                started = perf_counter_ns()
                response = client.post(
                    "/api/import",
                    files={"file": (filename, payload, content_type)},
                    data={"board_size": str(case["boardSize"])},
                )
                elapsed_ms.append((perf_counter_ns() - started) / 1_000_000)
                responses.append((response.status_code, response.json()))

            status, body = responses[0]
            baseline = _stable_response(responses[0])
            stable = all(_stable_response(item) == baseline for item in responses[1:])
            expected_key = case.get("expectedBoardKey")
            expected = ground_truth[expected_key] if expected_key else None
            actual = body.get("board") if isinstance(body, dict) else None
            expected_error = case.get("expectedError")
            row: dict[str, Any] = {
                "id": case["id"],
                "theme": case["theme"],
                "boardSize": case["boardSize"],
                "condition": case.get("condition", "original"),
                "sourceKind": case.get("sourceKind", "real_original"),
                "expectedOutcome": "success" if expected is not None else "error",
                "httpStatus": status,
                "payloadSha256": hashlib.sha256(payload).hexdigest(),
                "actualResponse": body,
                "responseStable": stable,
                "latencyMs": [round(value, 3) for value in elapsed_ms],
                "latency": _latency(elapsed_ms),
                "importSucceeded": bool(
                    expected is not None
                    and status == 200
                    and body.get("valid") is True
                    and actual is not None
                ),
                "exactBoard": False,
                "waypointOrderExact": False,
                "warningFree": bool(status == 200 and body.get("warnings") == []),
                "expectedErrorMatched": bool(
                    expected_error
                    and status == expected_error["status"]
                    and body.get("code") == expected_error["code"]
                ),
                "actualErrorCode": body.get("code"),
                "warningCodes": [
                    warning.get("code") for warning in body.get("warnings", [])
                ],
                "waypointPositionCounts": {"tp": 0, "fp": 0, "fn": 0},
                "wallCounts": {"tp": 0, "fp": 0, "fn": 0},
            }
            if expected is not None:
                row["exactBoard"] = _exact_board(actual, expected)
                row["waypointOrderExact"] = bool(
                    actual and actual.get("waypoints") == expected["waypoints"]
                )
                row["waypointPositionCounts"] = _counts(
                    _position_set(actual), _position_set(expected)
                )
                row["wallCounts"] = _counts(_wall_set(actual), _wall_set(expected))
            rows.append(row)

    summary = _group_summary(rows)
    return {
        "schemaVersion": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "name": manifest["name"],
            "role": manifest["datasetRole"],
            "notes": manifest.get("notes", ""),
            "manifest": manifest_display,
        },
        "execution": {
            "mode": "FastAPI TestClient (in-process POST /api/import)",
            "repetitionsPerCase": repetitions,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {name: version(name) for name in ("fastapi", "starlette", "numpy", "opencv-python-headless", "pillow", "httpx")},
            "timingPolicy": "All repetitions including first use; image transformations excluded",
        },
        "summary": summary,
        "byTheme": {
            theme: _group_summary([row for row in rows if row["theme"] == theme])
            for theme in sorted({row["theme"] for row in rows})
        },
        "byBoardSize": {
            str(size): _group_summary([row for row in rows if row["boardSize"] == size])
            for size in sorted({row["boardSize"] for row in rows})
        },
        "byCondition": {
            condition: _group_summary(
                [row for row in rows if row["condition"] == condition]
            )
            for condition in sorted({row["condition"] for row in rows})
        },
        "bySourceKind": {
            source: _group_summary(
                [row for row in rows if row["sourceKind"] == source]
            )
            for source in sorted({row["sourceKind"] for row in rows})
        },
        "cases": rows,
    }


def _display_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Screenshot-import evaluation",
        "",
        f"Dataset: **{result['dataset']['name']}**  ",
        f"Role: `{result['dataset']['role']}`  ",
        f"Execution: {result['execution']['mode']}  ",
        f"Repetitions per case: {result['execution']['repetitionsPerCase']}",
        "",
        "> The original screenshots were used while correcting the importer, and all",
        "> robustness cases are deterministic derivatives of those sources. These results",
        "> measure regression and controlled robustness, not independent real-world accuracy.",
        "",
        "## Aggregate results",
        "",
        "| Metric | Result |",
        "| --- | ---: |",
        f"| Valid screenshot cases | {summary['validCases']} |",
        f"| Negative cases | {summary['negativeCases']} |",
        f"| Successful-import rate | {_display_ratio(summary['successfulImportRate'])} |",
        f"| Exact-board accuracy | {_display_ratio(summary['exactBoardAccuracy'])} |",
        f"| Waypoint-order accuracy | {_display_ratio(summary['waypointOrderAccuracy'])} |",
        f"| Waypoint-position precision / recall / F1 | {_display_ratio(summary['waypointPositions']['precision'])} / {_display_ratio(summary['waypointPositions']['recall'])} / {_display_ratio(summary['waypointPositions']['f1'])} |",
        f"| Wall precision / recall / F1 | {_display_ratio(summary['walls']['precision'])} / {_display_ratio(summary['walls']['recall'])} / {_display_ratio(summary['walls']['f1'])} |",
        f"| Warning-free valid imports | {_display_ratio(summary['warningFreeRate'])} |",
        f"| Expected-error accuracy | {_display_ratio(summary['expectedErrorAccuracy'])} |",
        f"| Median / p95 in-process latency | {summary['latency']['medianMs']} ms / {summary['latency']['p95Ms']} ms |",
        "",
        "## Per-case results",
        "",
        "| Case | Condition | Theme | Size | Expected | HTTP | Exact/error match | Median ms | Stable |",
        "| --- | --- | --- | ---: | --- | ---: | --- | ---: | --- |",
    ]
    for row in result["cases"]:
        matched = (
            row["exactBoard"]
            if row["expectedOutcome"] == "success"
            else row["expectedErrorMatched"]
        )
        lines.append(
            f"| {row['id']} | {row['condition']} | {row['theme']} | {row['boardSize']} | "
            f"{row['expectedOutcome']} | {row['httpStatus']} | "
            f"{'Pass' if matched else 'Fail'} | {row['latency']['medianMs']} | "
            f"{'Yes' if row['responseStable'] else 'No'} |"
        )
    lines.extend(
        [
            "",
            "## Results by theme",
            "",
            "| Theme | Valid | Negative | Exact-board | Expected-error | Median / p95 ms |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, group in result["byTheme"].items():
        lines.append(
            f"| {name} | {group['validCases']} | {group['negativeCases']} | "
            f"{_display_ratio(group['exactBoardAccuracy'])} | "
            f"{_display_ratio(group['expectedErrorAccuracy'])} | "
            f"{group['latency']['medianMs']} / {group['latency']['p95Ms']} |"
        )
    lines.extend(
        [
            "",
            "## Results by supplied board size",
            "",
            "| Size | Valid | Negative | Exact-board | Waypoint order | Wall F1 |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, group in result["byBoardSize"].items():
        lines.append(
            f"| {name}x{name} | {group['validCases']} | {group['negativeCases']} | "
            f"{_display_ratio(group['exactBoardAccuracy'])} | "
            f"{_display_ratio(group['waypointOrderAccuracy'])} | "
            f"{_display_ratio(group['walls']['f1'])} |"
        )
    lines.extend(
        [
            "",
            "## Original and robustness subsets",
            "",
            "| Source subset | Valid | Negative | Exact-board | Waypoint order | Wall F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, group in result["bySourceKind"].items():
        lines.append(
            f"| {name} | {group['validCases']} | {group['negativeCases']} | "
            f"{_display_ratio(group['exactBoardAccuracy'])} | "
            f"{_display_ratio(group['waypointOrderAccuracy'])} | "
            f"{_display_ratio(group['walls']['f1'])} |"
        )
    lines.extend(
        [
            "",
            "## Results by image condition",
            "",
            "| Condition | Cases | Exact-board | Expected-error | Median / p95 ms |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, group in result["byCondition"].items():
        lines.append(
            f"| {name} | {group['cases']} | "
            f"{_display_ratio(group['exactBoardAccuracy'])} | "
            f"{_display_ratio(group['expectedErrorAccuracy'])} | "
            f"{group['latency']['medianMs']} / {group['latency']['p95Ms']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation and limitations",
            "",
            "Accuracy uses one observation per case; repetitions measure timing and response",
            "stability, and do not increase the number of independent screenshots. The 28",
            "positive cases come from four screenshots of just two boards. Conditions were",
            "piloted before this repeated run. Failed conditions remain in the denominator.",
            "Timing includes first-use requests and excludes image-transformation time.",
            "Full responses and payload SHA-256 hashes are retained in metrics.json.",
            "Exit code 1 means evaluation mismatches were recorded; results are still saved.",
            "",
            "The strict exact-board metric passes only when board size, ordered waypoint",
            "positions, and the complete undirected wall set all match. Position and wall",
            "precision/recall show partial extraction errors that exact accuracy alone would",
            "hide. Error accuracy requires both the expected HTTP status and error code.",
            "",
            "The set covers four original 6x6 and 8x8 light/dark screenshots, controlled",
            "scale, JPEG-compression, blur, padding, and crop variants, plus two synthetic",
            "blank-image rejection cases. It contains no 7x7 board, phone photograph,",
            "LinkedIn screenshot, or held-out real failure. Board size is supplied, matching",
            "the frontend workflow; automatic size inference is not evaluated. Latency is",
            "in-process and must not be described as deployed-network or load-test performance.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(_markdown(result), encoding="utf-8")
    with (output_dir / "cases.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "case",
                "theme",
                "board_size",
                "expected_outcome",
                "http_status",
                "exact_board",
                "expected_error_matched",
                "warning_free",
                "response_stable",
                "median_ms",
                "p95_ms",
            ]
        )
        for row in result["cases"]:
            writer.writerow(
                [
                    row["id"],
                    row["theme"],
                    row["boardSize"],
                    row["expectedOutcome"],
                    row["httpStatus"],
                    row["exactBoard"],
                    row["expectedErrorMatched"],
                    row["warningFree"],
                    row["responseStable"],
                    row["latency"]["medianMs"],
                    row["latency"]["p95Ms"],
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int, default=20)
    args = parser.parse_args()

    result = evaluate(args.manifest.resolve(), args.repetitions)
    write_results(result, args.output_dir.resolve())
    summary = result["summary"]
    print(f"Dataset: {result['dataset']['name']}")
    print(
        "Exact boards: "
        f"{_display_ratio(summary['exactBoardAccuracy'])}; "
        "expected errors: "
        f"{_display_ratio(summary['expectedErrorAccuracy'])}; "
        f"median/p95: {summary['latency']['medianMs']}/{summary['latency']['p95Ms']} ms"
    )
    print(f"Results: {args.output_dir.resolve()}")
    failures = [
        row
        for row in result["cases"]
        if not row["responseStable"]
        or (
            row["expectedOutcome"] == "success"
            and (not row["importSucceeded"] or not row["exactBoard"] or not row["warningFree"])
        )
        or (row["expectedOutcome"] == "error" and not row["expectedErrorMatched"])
    ]
    if failures:
        print(
            "Failed cases: " + ", ".join(row["id"] for row in failures), file=sys.stderr
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
