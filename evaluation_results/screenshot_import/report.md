# Screenshot-import evaluation

Dataset: **ZipSolver screenshot-import development set v1**  
Role: `development_regression`  
Execution: FastAPI TestClient (in-process POST /api/import)  
Repetitions per case: 20

> This is a development regression set. Its real screenshots were used while
> correcting the importer, so these results must not be presented as an
> independent or general screenshot-import accuracy estimate.

## Aggregate results

| Metric | Result |
| --- | ---: |
| Valid screenshot cases | 4 |
| Negative cases | 2 |
| Successful-import rate | 100.0% |
| Exact-board accuracy | 100.0% |
| Waypoint-order accuracy | 100.0% |
| Waypoint-position precision / recall / F1 | 100.0% / 100.0% / 100.0% |
| Wall precision / recall / F1 | 100.0% / 100.0% / 100.0% |
| Warning-free valid imports | 100.0% |
| Expected-error accuracy | 100.0% |
| Median / p95 in-process latency | 68.989 ms / 109.106 ms |

## Per-case results

| Case | Theme | Size | Expected | HTTP | Exact/error match | Median ms | Stable |
| --- | --- | ---: | --- | ---: | --- | ---: | --- |
| 6x6-light | light | 6 | success | 200 | Pass | 72.719 | Yes |
| 6x6-dark | dark | 6 | success | 200 | Pass | 54.855 | Yes |
| 8x8-light | light | 8 | success | 200 | Pass | 103.354 | Yes |
| 8x8-dark | dark | 8 | success | 200 | Pass | 103.798 | Yes |
| blank-light | light | 6 | error | 422 | Pass | 37.637 | Yes |
| blank-dark | dark | 6 | error | 422 | Pass | 39.854 | Yes |

## Results by theme

| Theme | Valid | Negative | Exact-board | Expected-error | Median / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| dark | 2 | 1 | 100.0% | 100.0% | 55.06 / 107.036 |
| light | 2 | 1 | 100.0% | 100.0% | 72.719 / 111.689 |

## Results by supplied board size

| Size | Valid | Negative | Exact-board | Waypoint order | Wall F1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6x6 | 2 | 2 | 100.0% | 100.0% | 100.0% |
| 8x8 | 2 | 0 | 100.0% | 100.0% | 100.0% |

## Interpretation and limitations

The strict exact-board metric passes only when board size, ordered waypoint
positions, and the complete undirected wall set all match. Position and wall
precision/recall show partial extraction errors that exact accuracy alone would
hide. Error accuracy requires both the expected HTTP status and error code.

The set currently covers matching 6x6 and 8x8 light/dark screenshots plus
synthetic blank-image rejection. It contains no 7x7 board, phone photograph,
LinkedIn screenshot, crop variation, scaling/compression variation, or held-out
real failure. Board size is supplied, matching the frontend workflow; automatic
size inference is not evaluated. Latency is in-process and must not be described
as deployed-network or load-test performance.
