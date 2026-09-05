# API evaluation

Mode: live HTTP
Generated: 2026-09-05T14:44:55.861865+00:00

Sequential, round-robin requests; warmups excluded from timing summaries.
Expected 400/422 rejections count as correct behavior. HTTP 200 alone is insufficient.
In-process times exclude network and Uvicorn. Live HTTP times depend on client, server, and network.
This is a fixed functional workload, not concurrent load capacity or model accuracy.

| Scenario | Matches / requests | Median ms | p95 ms | Stable |
| --- | ---: | ---: | ---: | --- |
| health | 20/20 | 2.804 | 3.669 | True |
| architecture | 20/20 | 14.788 | 22.463 | True |
| solve-valid | 20/20 | 58.338 | 83.156 | True |
| solve-unsolvable | 20/20 | 7.19 | 11.633 | True |
| solve-malformed | 20/20 | 2.344 | 3.507 | True |
| solve-invalid | 20/20 | 2.775 | 3.715 | True |
| import-light | 20/20 | 115.727 | 127.118 | True |
| import-dark | 20/20 | 88.235 | 96.894 | True |
| import-corrupt | 20/20 | 2.895 | 4.857 | True |

See metrics.json for endpoint aggregates, actual responses, status counts, warmups,
environment, and inputs. requests.csv has one measured request per row.
The fully waypoint-constrained snake is intentionally easy; its timing does not
represent arbitrary puzzles. Model availability and solverUsed affect comparisons.
Stability excludes timestamps and solver runtimeMs; other fields are compared.
No requests-per-second capacity claim is derived from these sequential timings.
