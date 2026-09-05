# Screenshot-import evaluation

Dataset: **ZipSolver screenshot regression and robustness v2**  
Role: `development_regression_and_derived_robustness`  
Execution: FastAPI TestClient (in-process POST /api/import)  
Repetitions per case: 20

> The original screenshots were used while correcting the importer, and all
> robustness cases are deterministic derivatives of those sources. These results
> measure regression and controlled robustness, not independent real-world accuracy.

## Aggregate results

| Metric | Result |
| --- | ---: |
| Valid screenshot cases | 28 |
| Negative cases | 2 |
| Successful-import rate | 100.0% |
| Exact-board accuracy | 82.1% |
| Waypoint-order accuracy | 82.1% |
| Waypoint-position precision / recall / F1 | 100.0% / 95.7% / 97.8% |
| Wall precision / recall / F1 | 100.0% / 100.0% / 100.0% |
| Warning-free valid imports | 82.1% |
| Expected-error accuracy | 100.0% |
| Median / p95 in-process latency | 93.845 ms / 201.241 ms |

## Per-case results

| Case | Condition | Theme | Size | Expected | HTTP | Exact/error match | Median ms | Stable |
| --- | --- | --- | ---: | --- | ---: | --- | ---: | --- |
| 6x6-light | original | light | 6 | success | 200 | Pass | 81.659 | Yes |
| 6x6-light--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 53.921 | Yes |
| 6x6-light--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 123.018 | Yes |
| 6x6-light--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 87.031 | Yes |
| 6x6-light--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 73.707 | Yes |
| 6x6-light--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 87.26 | Yes |
| 6x6-light--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 67.398 | Yes |
| 6x6-dark | original | dark | 6 | success | 200 | Pass | 55.882 | Yes |
| 6x6-dark--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 39.151 | Yes |
| 6x6-dark--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 80.697 | Yes |
| 6x6-dark--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 75.172 | Yes |
| 6x6-dark--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 69.458 | Yes |
| 6x6-dark--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 94.551 | Yes |
| 6x6-dark--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 56.375 | Yes |
| 8x8-light | original | light | 8 | success | 200 | Pass | 164.564 | Yes |
| 8x8-light--scale-75 | scale-75 | light | 8 | success | 200 | Fail | 85.295 | Yes |
| 8x8-light--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 160.706 | Yes |
| 8x8-light--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Fail | 115.944 | Yes |
| 8x8-light--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 102.746 | Yes |
| 8x8-light--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 138.894 | Yes |
| 8x8-light--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 214.324 | Yes |
| 8x8-dark | original | dark | 8 | success | 200 | Pass | 151.928 | Yes |
| 8x8-dark--scale-75 | scale-75 | dark | 8 | success | 200 | Fail | 86.293 | Yes |
| 8x8-dark--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 200.009 | Yes |
| 8x8-dark--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Fail | 111.822 | Yes |
| 8x8-dark--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Fail | 106.42 | Yes |
| 8x8-dark--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 130.429 | Yes |
| 8x8-dark--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 104.218 | Yes |
| blank-light | negative | light | 6 | error | 422 | Pass | 40.234 | Yes |
| blank-dark | negative | dark | 6 | error | 422 | Pass | 39.977 | Yes |

## Results by theme

| Theme | Valid | Negative | Exact-board | Expected-error | Median / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| dark | 14 | 1 | 78.6% | 100.0% | 92.172 / 189.259 |
| light | 14 | 1 | 85.7% | 100.0% | 95.004 / 212.954 |

## Results by supplied board size

| Size | Valid | Negative | Exact-board | Waypoint order | Wall F1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6x6 | 14 | 2 | 100.0% | 100.0% | 100.0% |
| 8x8 | 14 | 0 | 64.3% | 64.3% | 100.0% |

## Original and robustness subsets

| Source subset | Valid | Negative | Exact-board | Waypoint order | Wall F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| derived_robustness | 24 | 0 | 79.2% | 79.2% | 100.0% |
| real_original | 4 | 0 | 100.0% | 100.0% | 100.0% |
| synthetic_negative | 0 | 2 | n/a | n/a | n/a |

## Results by image condition

| Condition | Cases | Exact-board | Expected-error | Median / p95 ms |
| --- | ---: | ---: | ---: | ---: |
| blur-0.8 | 4 | 75.0% | n/a | 100.722 / 125.01 |
| crop-12 | 4 | 100.0% | n/a | 93.102 / 262.928 |
| jpeg-q65 | 4 | 50.0% | n/a | 104.852 / 143.908 |
| negative | 2 | n/a | 100.0% | 39.977 / 46.201 |
| original | 4 | 100.0% | n/a | 113.827 / 202.188 |
| pad-40 | 4 | 100.0% | n/a | 114.668 / 183.781 |
| scale-125 | 4 | 100.0% | n/a | 149.173 / 231.253 |
| scale-75 | 4 | 50.0% | n/a | 69.826 / 100.982 |

## Interpretation and limitations

Accuracy uses one observation per case; repetitions measure timing and response
stability, and do not increase the number of independent screenshots. The 28
positive cases come from four screenshots of just two boards. Conditions were
piloted before this repeated run. Failed conditions remain in the denominator.
Timing includes first-use requests and excludes image-transformation time.
Full responses and payload SHA-256 hashes are retained in metrics.json.
Exit code 1 means evaluation mismatches were recorded; results are still saved.

The strict exact-board metric passes only when board size, ordered waypoint
positions, and the complete undirected wall set all match. Position and wall
precision/recall show partial extraction errors that exact accuracy alone would
hide. Error accuracy requires both the expected HTTP status and error code.

The set covers four original 6x6 and 8x8 light/dark screenshots, controlled
scale, JPEG-compression, blur, padding, and crop variants, plus two synthetic
blank-image rejection cases. It contains no 7x7 board, phone photograph,
LinkedIn screenshot, or held-out real failure. Board size is supplied, matching
the frontend workflow; automatic size inference is not evaluated. Latency is
in-process and must not be described as deployed-network or load-test performance.
