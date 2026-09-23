# Screenshot-import evaluation

Dataset: **ZipSolver screenshot regression and robustness v3**  
Role: `development_regression_and_derived_robustness`  
Execution: FastAPI TestClient (in-process POST /api/import)  
Repetitions per case: 1

> The original screenshots were used while correcting the importer, and all
> robustness cases are deterministic derivatives of those sources. These results
> measure regression and controlled robustness, not independent real-world accuracy.

## Aggregate results

| Metric | Result |
| --- | ---: |
| Valid screenshot cases | 238 |
| Negative cases | 2 |
| Successful-import rate | 100.0% |
| Exact-board accuracy | 100.0% |
| Waypoint-order accuracy | 100.0% |
| Waypoint-position precision / recall / F1 | 100.0% / 100.0% / 100.0% |
| Wall precision / recall / F1 | 100.0% / 100.0% / 100.0% |
| Warning-free valid imports | 100.0% |
| Expected-error accuracy | 100.0% |
| Median / p95 in-process latency | 163.63 ms / 451.418 ms |

## Per-case results

| Case | Condition | Theme | Size | Expected | HTTP | Exact/error match | Median ms | Stable |
| --- | --- | --- | ---: | --- | ---: | --- | ---: | --- |
| 6x6-light | original | light | 6 | success | 200 | Pass | 268.125 | Yes |
| 6x6-light--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 58.124 | Yes |
| 6x6-light--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 138.343 | Yes |
| 6x6-light--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 100.939 | Yes |
| 6x6-light--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 79.544 | Yes |
| 6x6-light--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 123.433 | Yes |
| 6x6-light--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 74.306 | Yes |
| 6x6-dark | original | dark | 6 | success | 200 | Pass | 62.049 | Yes |
| 6x6-dark--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 44.372 | Yes |
| 6x6-dark--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 98.216 | Yes |
| 6x6-dark--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 81.777 | Yes |
| 6x6-dark--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 65.779 | Yes |
| 6x6-dark--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 99.48 | Yes |
| 6x6-dark--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 55.544 | Yes |
| 8x8-light | original | light | 8 | success | 200 | Pass | 115.017 | Yes |
| 8x8-light--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 98.303 | Yes |
| 8x8-light--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 158.399 | Yes |
| 8x8-light--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 130.58 | Yes |
| 8x8-light--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 123.195 | Yes |
| 8x8-light--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 135.296 | Yes |
| 8x8-light--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 114.545 | Yes |
| 8x8-dark | original | dark | 8 | success | 200 | Pass | 125.672 | Yes |
| 8x8-dark--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 94.766 | Yes |
| 8x8-dark--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 183.009 | Yes |
| 8x8-dark--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 118.729 | Yes |
| 8x8-dark--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 127.545 | Yes |
| 8x8-dark--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 135.878 | Yes |
| 8x8-dark--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 120.041 | Yes |
| app-191913 | original | dark | 6 | success | 200 | Pass | 355.994 | Yes |
| app-191913--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 186.058 | Yes |
| app-191913--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 507.702 | Yes |
| app-191913--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 345.863 | Yes |
| app-191913--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 309.307 | Yes |
| app-191913--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 383.894 | Yes |
| app-191913--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 323.934 | Yes |
| app-191932 | original | light | 6 | success | 200 | Pass | 262.41 | Yes |
| app-191932--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 153.462 | Yes |
| app-191932--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 356.494 | Yes |
| app-191932--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 285.619 | Yes |
| app-191932--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 229.586 | Yes |
| app-191932--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 266.688 | Yes |
| app-191932--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 217.739 | Yes |
| app-191920 | original | dark | 7 | success | 200 | Pass | 318.233 | Yes |
| app-191920--scale-75 | scale-75 | dark | 7 | success | 200 | Pass | 176.939 | Yes |
| app-191920--scale-125 | scale-125 | dark | 7 | success | 200 | Pass | 473.507 | Yes |
| app-191920--jpeg-q65 | jpeg-q65 | dark | 7 | success | 200 | Pass | 325.924 | Yes |
| app-191920--blur-0.8 | blur-0.8 | dark | 7 | success | 200 | Pass | 292.545 | Yes |
| app-191920--pad-40 | pad-40 | dark | 7 | success | 200 | Pass | 399.642 | Yes |
| app-191920--crop-12 | crop-12 | dark | 7 | success | 200 | Pass | 301.019 | Yes |
| app-191940 | original | light | 7 | success | 200 | Pass | 247.976 | Yes |
| app-191940--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 134.133 | Yes |
| app-191940--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 346.862 | Yes |
| app-191940--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 288.936 | Yes |
| app-191940--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 243.481 | Yes |
| app-191940--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 302.855 | Yes |
| app-191940--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 241.558 | Yes |
| app-191951 | original | light | 8 | success | 200 | Pass | 246.969 | Yes |
| app-191951--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 151.225 | Yes |
| app-191951--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 358.779 | Yes |
| app-191951--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 371.729 | Yes |
| app-191951--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 253.987 | Yes |
| app-191951--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 320.346 | Yes |
| app-191951--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 223.373 | Yes |
| app-191959 | original | dark | 8 | success | 200 | Pass | 384.185 | Yes |
| app-191959--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 181.26 | Yes |
| app-191959--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 579.221 | Yes |
| app-191959--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 370.202 | Yes |
| app-191959--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 389.291 | Yes |
| app-191959--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 460.175 | Yes |
| app-191959--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 343.004 | Yes |
| app-192013 | original | dark | 6 | success | 200 | Pass | 356.609 | Yes |
| app-192013--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 145.782 | Yes |
| app-192013--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 419.824 | Yes |
| app-192013--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 397.359 | Yes |
| app-192013--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 341.428 | Yes |
| app-192013--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 325.027 | Yes |
| app-192013--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 308.778 | Yes |
| app-192018 | original | light | 6 | success | 200 | Pass | 238.407 | Yes |
| app-192018--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 145.005 | Yes |
| app-192018--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 384.846 | Yes |
| app-192018--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 315.676 | Yes |
| app-192018--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 255.282 | Yes |
| app-192018--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 285.087 | Yes |
| app-192018--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 263.64 | Yes |
| app-192102 | original | light | 6 | success | 200 | Pass | 306.732 | Yes |
| app-192102--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 128.88 | Yes |
| app-192102--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 457.305 | Yes |
| app-192102--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 275.142 | Yes |
| app-192102--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 253.775 | Yes |
| app-192102--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 312.575 | Yes |
| app-192102--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 277.204 | Yes |
| app-192108 | original | dark | 6 | success | 200 | Pass | 365.222 | Yes |
| app-192108--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 175.021 | Yes |
| app-192108--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 523.998 | Yes |
| app-192108--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 383.583 | Yes |
| app-192108--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 379.019 | Yes |
| app-192108--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 403.55 | Yes |
| app-192108--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 335.427 | Yes |
| app-192159 | original | dark | 7 | success | 200 | Pass | 199.055 | Yes |
| app-192159--scale-75 | scale-75 | dark | 7 | success | 200 | Pass | 116.105 | Yes |
| app-192159--scale-125 | scale-125 | dark | 7 | success | 200 | Pass | 335.733 | Yes |
| app-192159--jpeg-q65 | jpeg-q65 | dark | 7 | success | 200 | Pass | 218.912 | Yes |
| app-192159--blur-0.8 | blur-0.8 | dark | 7 | success | 200 | Pass | 221.316 | Yes |
| app-192159--pad-40 | pad-40 | dark | 7 | success | 200 | Pass | 234.742 | Yes |
| app-192159--crop-12 | crop-12 | dark | 7 | success | 200 | Pass | 185.146 | Yes |
| app-192206 | original | light | 7 | success | 200 | Pass | 182.115 | Yes |
| app-192206--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 104.985 | Yes |
| app-192206--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 247.685 | Yes |
| app-192206--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 200.638 | Yes |
| app-192206--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 168.861 | Yes |
| app-192206--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 241.006 | Yes |
| app-192206--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 213.259 | Yes |
| app-192257 | original | light | 8 | success | 200 | Pass | 327.605 | Yes |
| app-192257--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 184.869 | Yes |
| app-192257--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 436.305 | Yes |
| app-192257--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 339.682 | Yes |
| app-192257--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 291.93 | Yes |
| app-192257--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 320.055 | Yes |
| app-192257--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 282.538 | Yes |
| app-192303 | original | dark | 8 | success | 200 | Pass | 394.981 | Yes |
| app-192303--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 221.133 | Yes |
| app-192303--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 489.817 | Yes |
| app-192303--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 401.982 | Yes |
| app-192303--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 374.224 | Yes |
| app-192303--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 413.302 | Yes |
| app-192303--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 426.307 | Yes |
| app-192314 | original | dark | 8 | success | 200 | Pass | 234.099 | Yes |
| app-192314--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 136.295 | Yes |
| app-192314--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 340.983 | Yes |
| app-192314--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 307.715 | Yes |
| app-192314--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 231.688 | Yes |
| app-192314--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 284.728 | Yes |
| app-192314--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 217.707 | Yes |
| app-192319 | original | light | 8 | success | 200 | Pass | 290.207 | Yes |
| app-192319--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 170.599 | Yes |
| app-192319--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 423.628 | Yes |
| app-192319--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 349.193 | Yes |
| app-192319--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 282.992 | Yes |
| app-192319--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 459.845 | Yes |
| app-192319--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 331.65 | Yes |
| app-192346 | original | light | 8 | success | 200 | Pass | 353.702 | Yes |
| app-192346--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 277.888 | Yes |
| app-192346--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 597.9 | Yes |
| app-192346--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 448.72 | Yes |
| app-192346--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 330.26 | Yes |
| app-192346--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 364.229 | Yes |
| app-192346--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 287.343 | Yes |
| app-192351 | original | dark | 8 | success | 200 | Pass | 402.04 | Yes |
| app-192351--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 206.423 | Yes |
| app-192351--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 674.28 | Yes |
| app-192351--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 485.135 | Yes |
| app-192351--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 446.544 | Yes |
| app-192351--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 578.088 | Yes |
| app-192351--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 451.108 | Yes |
| linkedin-19.49.31 | original | light | 7 | success | 200 | Pass | 97.038 | Yes |
| linkedin-19.49.31--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 62.071 | Yes |
| linkedin-19.49.31--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 96.628 | Yes |
| linkedin-19.49.31--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 61.146 | Yes |
| linkedin-19.49.31--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 85.479 | Yes |
| linkedin-19.49.31--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 88.008 | Yes |
| linkedin-19.49.31--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 66.012 | Yes |
| linkedin-19.49.42 | original | light | 8 | success | 200 | Pass | 143.4 | Yes |
| linkedin-19.49.42--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 156.503 | Yes |
| linkedin-19.49.42--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 153.45 | Yes |
| linkedin-19.49.42--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 117.173 | Yes |
| linkedin-19.49.42--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 135.411 | Yes |
| linkedin-19.49.42--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 121.265 | Yes |
| linkedin-19.49.42--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 103.737 | Yes |
| linkedin-19.49.53 | original | light | 6 | success | 200 | Pass | 60.043 | Yes |
| linkedin-19.49.53--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 63.287 | Yes |
| linkedin-19.49.53--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 77.563 | Yes |
| linkedin-19.49.53--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 51.291 | Yes |
| linkedin-19.49.53--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 70.751 | Yes |
| linkedin-19.49.53--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 61.001 | Yes |
| linkedin-19.49.53--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 69.927 | Yes |
| linkedin-19.50.07 | original | light | 6 | success | 200 | Pass | 62.776 | Yes |
| linkedin-19.50.07--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 45.342 | Yes |
| linkedin-19.50.07--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 87.951 | Yes |
| linkedin-19.50.07--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 55.016 | Yes |
| linkedin-19.50.07--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 71.179 | Yes |
| linkedin-19.50.07--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 67.017 | Yes |
| linkedin-19.50.07--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 58.361 | Yes |
| linkedin-19.50.21 | original | light | 6 | success | 200 | Pass | 58.732 | Yes |
| linkedin-19.50.21--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 53.932 | Yes |
| linkedin-19.50.21--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 76.817 | Yes |
| linkedin-19.50.21--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 62.268 | Yes |
| linkedin-19.50.21--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 61.781 | Yes |
| linkedin-19.50.21--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 66.85 | Yes |
| linkedin-19.50.21--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 65.776 | Yes |
| linkedin-19.50.37 | original | light | 8 | success | 200 | Pass | 100.608 | Yes |
| linkedin-19.50.37--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 98.457 | Yes |
| linkedin-19.50.37--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 145.509 | Yes |
| linkedin-19.50.37--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 116.791 | Yes |
| linkedin-19.50.37--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 102.656 | Yes |
| linkedin-19.50.37--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 119.605 | Yes |
| linkedin-19.50.37--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 115.469 | Yes |
| linkedin-19.50.47 | original | light | 7 | success | 200 | Pass | 90.124 | Yes |
| linkedin-19.50.47--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 74.35 | Yes |
| linkedin-19.50.47--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 90.701 | Yes |
| linkedin-19.50.47--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 71.892 | Yes |
| linkedin-19.50.47--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 80.276 | Yes |
| linkedin-19.50.47--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 86.545 | Yes |
| linkedin-19.50.47--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 86.234 | Yes |
| linkedin-19.50.57 | original | light | 8 | success | 200 | Pass | 87.418 | Yes |
| linkedin-19.50.57--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 70.847 | Yes |
| linkedin-19.50.57--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 116.074 | Yes |
| linkedin-19.50.57--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 70.672 | Yes |
| linkedin-19.50.57--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 138.403 | Yes |
| linkedin-19.50.57--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 110.751 | Yes |
| linkedin-19.50.57--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 119.925 | Yes |
| linkedin-19.51.06 | original | light | 7 | success | 200 | Pass | 93.516 | Yes |
| linkedin-19.51.06--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 70.127 | Yes |
| linkedin-19.51.06--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 104.961 | Yes |
| linkedin-19.51.06--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 86.116 | Yes |
| linkedin-19.51.06--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 75.395 | Yes |
| linkedin-19.51.06--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 80.434 | Yes |
| linkedin-19.51.06--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 101.644 | Yes |
| linkedin-19.46.03 | original | light | 7 | success | 200 | Pass | 99.989 | Yes |
| linkedin-19.46.03--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 80.764 | Yes |
| linkedin-19.46.03--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 149.622 | Yes |
| linkedin-19.46.03--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 96.971 | Yes |
| linkedin-19.46.03--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 117.892 | Yes |
| linkedin-19.46.03--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 179.705 | Yes |
| linkedin-19.46.03--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 96.377 | Yes |
| linkedin-102225 | original | light | 8 | success | 200 | Pass | 76.554 | Yes |
| linkedin-102225--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 71.314 | Yes |
| linkedin-102225--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 116.079 | Yes |
| linkedin-102225--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 89.398 | Yes |
| linkedin-102225--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 69.227 | Yes |
| linkedin-102225--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 94.115 | Yes |
| linkedin-102225--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 81.177 | Yes |
| linkedin-102318 | original | light | 7 | success | 200 | Pass | 60.588 | Yes |
| linkedin-102318--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 55.11 | Yes |
| linkedin-102318--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 66.169 | Yes |
| linkedin-102318--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 77.989 | Yes |
| linkedin-102318--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 65.985 | Yes |
| linkedin-102318--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 72.918 | Yes |
| linkedin-102318--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 69.289 | Yes |
| blank-light | negative | light | 6 | error | 422 | Pass | 50.905 | Yes |
| blank-dark | negative | dark | 6 | error | 422 | Pass | 45.166 | Yes |

## Results by theme

| Theme | Valid | Negative | Exact-board | Expected-error | Median / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| dark | 77 | 1 | 100.0% | 100.0% | 321.084 / 510.146 |
| light | 161 | 1 | 100.0% | 100.0% | 117.532 / 363.956 |

## Results by supplied board size

| Size | Valid | Negative | Exact-board | Waypoint order | Wall F1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6x6 | 77 | 2 | 100.0% | 100.0% | 100.0% |
| 7x7 | 63 | 0 | 100.0% | 100.0% | 100.0% |
| 8x8 | 98 | 0 | 100.0% | 100.0% | 100.0% |

## Original and robustness subsets

| Source subset | Valid | Negative | Exact-board | Waypoint order | Wall F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| derived_robustness | 204 | 0 | 100.0% | 100.0% | 100.0% |
| real_original | 34 | 0 | 100.0% | 100.0% | 100.0% |
| synthetic_negative | 0 | 2 | n/a | n/a | n/a |

## Results by image condition

| Condition | Cases | Exact-board | Expected-error | Median / p95 ms |
| --- | ---: | ---: | ---: | ---: |
| blur-0.8 | 34 | 100.0% | n/a | 195.089 / 382.614 |
| crop-12 | 34 | 100.0% | n/a | 199.202 / 372.16 |
| jpeg-q65 | 34 | 100.0% | n/a | 209.775 / 418.34 |
| negative | 2 | n/a | 100.0% | 48.035 / 50.618 |
| original | 34 | 100.0% | n/a | 216.577 / 387.964 |
| pad-40 | 34 | 100.0% | n/a | 237.874 / 459.961 |
| scale-125 | 34 | 100.0% | n/a | 291.709 / 585.759 |
| scale-75 | 34 | 100.0% | n/a | 122.493 / 211.571 |

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
