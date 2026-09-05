# Reading screenshot evaluation results

Run from the repository root:

```powershell
uv run python scripts/evaluate_screenshot_import.py --repetitions 20
```

Results are written to `evaluation_results/screenshot_import/`.

| File | How to use it |
| --- | --- |
| `report.md` | Read first. Summary, individual cases, theme/size/condition comparisons, and limitations. |
| `metrics.json` | Detailed evidence: execution environment, aggregate metrics, groups and individual cases. Each case includes its first actual response, payload hash, timing samples, warnings, and stability across repetitions. |
| `cases.csv` | Open in Excel and filter by case, HTTP status, exact-board match, warning-free status, or stability. One row represents one image case, not one request. |

## Meaning of the measurements

- **Successful import**: HTTP 200 with a board marked valid. This does not prove that the board matches the screenshot.
- **Exact-board accuracy**: size, ordered waypoints, and every wall match the expected board.
- **Waypoint-order accuracy**: the complete ordered waypoint list matches.
- **Precision**: how many detected positions or walls are correct: TP / (TP + FP).
- **Recall**: how many expected positions or walls were found: TP / (TP + FN).
- **F1**: 2TP / (2TP + FP + FN). Zero means no correct matches when features exist; null/n/a means its denominator is zero.
- **TP / FP / FN**: correct detections / extra detections / missed detections.
- **Warning-free rate**: proportion of positive cases returned with no warnings.
- **Expected-error accuracy**: negative cases return both the expected HTTP status and error code.
- **Stable**: repeated response bodies match after removing error timestamps.
- **Median latency**: the middle request time. **p95**: the interpolated 95th percentile. Timings include first use, exclude image transformation, and measure the in-process backend, not a deployed network.

## Avoid misleading conclusions

The dataset has four original screenshots of two boards, 24 transformed copies, and two blank images. The original screenshots were used while fixing the importer. These are correlated development/robustness cases, not an independent accuracy sample; 600 requests do not mean 600 different screenshots.

Accuracy is scored once per case from its first response. Repetitions measure timing and stability. Inspect stability before trusting that first response as representative.

Read the original and transformed subsets separately. A failed stress case is useful evidence and remains in the denominator. Exit code 1 means mismatches or warnings were recorded; all result files are still saved. The current known stress failures concern 8x8 waypoint recognition.
