# Screenshot theme regression fixtures

Requirement: OR1 (screenshot import). These four original PNGs were supplied
by the user on 2026-09-05. The images are copied without resizing or recolouring.
The expected boards were manually transcribed from their visible numbers and
walls, using backend coordinates `[x, y]`, starting at `[0, 0]` at the top left.
Waypoint list order is significant; wall endpoint order is not.

| Fixture | Original filename | Expected waypoints | Expected walls |
| --- | --- | ---: | ---: |
| 6x6-dark.png | Screenshot 2026-09-05 110814.png | 4 | 8 |
| 6x6-light.png | Screenshot 2026-09-05 111035.png | 4 | 8 |
| 8x8-light.png | Screenshot 2026-09-05 111121.png | 16 | 10 |
| 8x8-dark.png | Screenshot 2026-09-05 111129.png | 16 | 10 |

## Reproduce

From the repository root, with the project's dependencies installed:

```sh
uv run pytest backend/tests/integration/test_screenshot_themes.py -q
uv run pytest -q
```

The focused file has 15 cases: eight exact-board checks (extractor and HTTP),
one sequence alternating themes/sizes on the same extractor, four checks with
system font loading disabled and a different working directory, and two
blank-image rejection checks. HTTP tests use the existing real backend client;
no screenshot detection, parsing, or input-validation components are mocked.

## Defect and correction

Before the fix, both dark images failed with no markers detected. The light
6x6 image preserved four positions but inferred the wrong number order and
returned only four walls. The light 8x8 image preserved sixteen positions but
inferred the wrong number order and returned only seven walls.

The fix recognises pale-orange discs, locates panels from repeated background
colours as well as brightness, reads dark or white digits, and uses a portable
bank of regular/bold digit shapes. Wall detection now measures contrast in
either direction against marker-free cell corners and requires a substantial
stroke, excluding the thin outline around waypoint 1.

All four images must return the complete expected board and no import warnings.
Blank theme-coloured images must return HTTP 422 / NO_BOARD_DETECTED.

Verification on 2026-09-05: the complete suite passed (514 cases, including all
15 new cases; 9.08 seconds in the validation environment). Two existing
Starlette/TestClient dependency deprecation warnings remain. Before production
changes, all nine initial exact-board/repeated-import regression cases failed.

The runtime requires `backend/input_validation/screenshot/digit_templates.npz`
next to `waypoint_detector.py`. No OCR service, system font, or additional
dependency is required. `scripts/build_screenshot_digit_templates.py` records
how to regenerate the bank; it is not needed for normal use.

## Evidence limits

These are development regression fixtures, not an independent accuracy dataset.
They establish correctness for these two puzzles in both themes. They do not
establish a general accuracy percentage, 7x7 reliability, arbitrary fonts,
photographs, heavy compression, scaling, or full-page screenshot reliability.
The tests supply board_size just as the frontend does; they do not test
automatic grid-size inference. Validation ran on Linux; font independence was
tested explicitly, but Windows/browser execution still needs a local smoke test.

Keep these fixtures separate from the future held-out screenshot evaluation set.

## Preliminary metrics

Run the manifest-driven evaluator from the repository root:

```sh
uv run python scripts/evaluate_screenshot_import.py
```

It sends every case through the real `POST /api/import` route twenty times and
writes `metrics.json`, `cases.csv`, and `report.md` under
`evaluation_results/screenshot_import/`. The manifest also defines two
reproducible blank-image rejection cases. A non-zero process exit means at least
one response was unstable, a valid case was not an exact warning-free match, or
an expected error status/code did not match.

The current manifest is explicitly labelled `development_regression`. Create a
separate manifest and image directory for the final held-out accuracy dataset;
do not relabel these four tuning images as independent evaluation data.
