# Screenshot-import evaluation

Dataset: **ZipSolver screenshot regression and robustness v3**  
Role: `development_regression_and_derived_robustness`  
Execution: FastAPI TestClient (in-process POST /api/import)  
Repetitions per case: 20

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
| Median / p95 in-process latency | 150.248 ms / 449.986 ms |

## Per-case results

| Case | Condition | Theme | Size | Expected | HTTP | Exact/error match | Median ms | Stable |
| --- | --- | --- | ---: | --- | ---: | --- | ---: | --- |
| 6x6-light | original | light | 6 | success | 200 | Pass | 72.83 | Yes |
| 6x6-light--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 42.722 | Yes |
| 6x6-light--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 100.248 | Yes |
| 6x6-light--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 79.3 | Yes |
| 6x6-light--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 71.217 | Yes |
| 6x6-light--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 85.924 | Yes |
| 6x6-light--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 66.036 | Yes |
| 6x6-dark | original | dark | 6 | success | 200 | Pass | 55.084 | Yes |
| 6x6-dark--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 40.119 | Yes |
| 6x6-dark--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 77.971 | Yes |
| 6x6-dark--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 71.078 | Yes |
| 6x6-dark--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 56.867 | Yes |
| 6x6-dark--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 76.703 | Yes |
| 6x6-dark--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 52.732 | Yes |
| 8x8-light | original | light | 8 | success | 200 | Pass | 107.123 | Yes |
| 8x8-light--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 83.1 | Yes |
| 8x8-light--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 144.727 | Yes |
| 8x8-light--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 107.813 | Yes |
| 8x8-light--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 101.256 | Yes |
| 8x8-light--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 115.895 | Yes |
| 8x8-light--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 101.576 | Yes |
| 8x8-dark | original | dark | 8 | success | 200 | Pass | 109.85 | Yes |
| 8x8-dark--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 85.9 | Yes |
| 8x8-dark--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 159.849 | Yes |
| 8x8-dark--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 112.078 | Yes |
| 8x8-dark--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 119.404 | Yes |
| 8x8-dark--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 174.228 | Yes |
| 8x8-dark--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 104.825 | Yes |
| app-191913 | original | dark | 6 | success | 200 | Pass | 327.105 | Yes |
| app-191913--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 200.993 | Yes |
| app-191913--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 599.06 | Yes |
| app-191913--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 376.126 | Yes |
| app-191913--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 325.507 | Yes |
| app-191913--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 370.926 | Yes |
| app-191913--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 316.26 | Yes |
| app-191932 | original | light | 6 | success | 200 | Pass | 251.711 | Yes |
| app-191932--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 136.688 | Yes |
| app-191932--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 346.043 | Yes |
| app-191932--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 281.787 | Yes |
| app-191932--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 260.033 | Yes |
| app-191932--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 313.025 | Yes |
| app-191932--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 201.002 | Yes |
| app-191920 | original | dark | 7 | success | 200 | Pass | 314.532 | Yes |
| app-191920--scale-75 | scale-75 | dark | 7 | success | 200 | Pass | 157.003 | Yes |
| app-191920--scale-125 | scale-125 | dark | 7 | success | 200 | Pass | 468.578 | Yes |
| app-191920--jpeg-q65 | jpeg-q65 | dark | 7 | success | 200 | Pass | 292.235 | Yes |
| app-191920--blur-0.8 | blur-0.8 | dark | 7 | success | 200 | Pass | 275.791 | Yes |
| app-191920--pad-40 | pad-40 | dark | 7 | success | 200 | Pass | 373.697 | Yes |
| app-191920--crop-12 | crop-12 | dark | 7 | success | 200 | Pass | 279.144 | Yes |
| app-191940 | original | light | 7 | success | 200 | Pass | 218.384 | Yes |
| app-191940--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 120.164 | Yes |
| app-191940--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 314.362 | Yes |
| app-191940--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 276.207 | Yes |
| app-191940--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 224.782 | Yes |
| app-191940--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 294.114 | Yes |
| app-191940--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 219.523 | Yes |
| app-191951 | original | light | 8 | success | 200 | Pass | 226.146 | Yes |
| app-191951--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 133.854 | Yes |
| app-191951--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 355.502 | Yes |
| app-191951--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 332.467 | Yes |
| app-191951--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 229.37 | Yes |
| app-191951--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 291.212 | Yes |
| app-191951--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 204.371 | Yes |
| app-191959 | original | dark | 8 | success | 200 | Pass | 365.08 | Yes |
| app-191959--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 192.291 | Yes |
| app-191959--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 598.885 | Yes |
| app-191959--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 356.216 | Yes |
| app-191959--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 346.348 | Yes |
| app-191959--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 396.158 | Yes |
| app-191959--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 301.219 | Yes |
| app-192013 | original | dark | 6 | success | 200 | Pass | 325.958 | Yes |
| app-192013--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 135.383 | Yes |
| app-192013--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 391.929 | Yes |
| app-192013--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 347.998 | Yes |
| app-192013--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 348.294 | Yes |
| app-192013--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 321.96 | Yes |
| app-192013--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 306.64 | Yes |
| app-192018 | original | light | 6 | success | 200 | Pass | 232.133 | Yes |
| app-192018--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 153.486 | Yes |
| app-192018--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 357.816 | Yes |
| app-192018--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 281.662 | Yes |
| app-192018--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 266.156 | Yes |
| app-192018--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 331.726 | Yes |
| app-192018--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 276.28 | Yes |
| app-192102 | original | light | 6 | success | 200 | Pass | 337.244 | Yes |
| app-192102--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 146.833 | Yes |
| app-192102--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 504.203 | Yes |
| app-192102--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 282.22 | Yes |
| app-192102--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 256.457 | Yes |
| app-192102--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 345.846 | Yes |
| app-192102--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 298.33 | Yes |
| app-192108 | original | dark | 6 | success | 200 | Pass | 435.794 | Yes |
| app-192108--scale-75 | scale-75 | dark | 6 | success | 200 | Pass | 170.065 | Yes |
| app-192108--scale-125 | scale-125 | dark | 6 | success | 200 | Pass | 484.454 | Yes |
| app-192108--jpeg-q65 | jpeg-q65 | dark | 6 | success | 200 | Pass | 353.822 | Yes |
| app-192108--blur-0.8 | blur-0.8 | dark | 6 | success | 200 | Pass | 354.436 | Yes |
| app-192108--pad-40 | pad-40 | dark | 6 | success | 200 | Pass | 399.022 | Yes |
| app-192108--crop-12 | crop-12 | dark | 6 | success | 200 | Pass | 349.793 | Yes |
| app-192159 | original | dark | 7 | success | 200 | Pass | 189.577 | Yes |
| app-192159--scale-75 | scale-75 | dark | 7 | success | 200 | Pass | 110.67 | Yes |
| app-192159--scale-125 | scale-125 | dark | 7 | success | 200 | Pass | 300.629 | Yes |
| app-192159--jpeg-q65 | jpeg-q65 | dark | 7 | success | 200 | Pass | 219.494 | Yes |
| app-192159--blur-0.8 | blur-0.8 | dark | 7 | success | 200 | Pass | 196.414 | Yes |
| app-192159--pad-40 | pad-40 | dark | 7 | success | 200 | Pass | 239.762 | Yes |
| app-192159--crop-12 | crop-12 | dark | 7 | success | 200 | Pass | 175.941 | Yes |
| app-192206 | original | light | 7 | success | 200 | Pass | 172.57 | Yes |
| app-192206--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 110.143 | Yes |
| app-192206--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 235.708 | Yes |
| app-192206--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 187.452 | Yes |
| app-192206--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 144.64 | Yes |
| app-192206--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 216.007 | Yes |
| app-192206--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 195.873 | Yes |
| app-192257 | original | light | 8 | success | 200 | Pass | 348.669 | Yes |
| app-192257--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 207.364 | Yes |
| app-192257--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 433.643 | Yes |
| app-192257--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 353.766 | Yes |
| app-192257--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 301.208 | Yes |
| app-192257--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 322.027 | Yes |
| app-192257--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 276.398 | Yes |
| app-192303 | original | dark | 8 | success | 200 | Pass | 376.472 | Yes |
| app-192303--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 180.581 | Yes |
| app-192303--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 484.796 | Yes |
| app-192303--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 438.83 | Yes |
| app-192303--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 388.5 | Yes |
| app-192303--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 407.536 | Yes |
| app-192303--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 364.513 | Yes |
| app-192314 | original | dark | 8 | success | 200 | Pass | 210.164 | Yes |
| app-192314--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 135.876 | Yes |
| app-192314--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 305.647 | Yes |
| app-192314--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 288.544 | Yes |
| app-192314--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 219.439 | Yes |
| app-192314--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 281.701 | Yes |
| app-192314--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 217.623 | Yes |
| app-192319 | original | light | 8 | success | 200 | Pass | 282.398 | Yes |
| app-192319--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 166.395 | Yes |
| app-192319--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 435.278 | Yes |
| app-192319--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 372.34 | Yes |
| app-192319--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 320.54 | Yes |
| app-192319--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 400.943 | Yes |
| app-192319--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 273.237 | Yes |
| app-192346 | original | light | 8 | success | 200 | Pass | 300.598 | Yes |
| app-192346--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 172.611 | Yes |
| app-192346--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 440.791 | Yes |
| app-192346--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 379.21 | Yes |
| app-192346--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 296.481 | Yes |
| app-192346--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 311.971 | Yes |
| app-192346--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 255.16 | Yes |
| app-192351 | original | dark | 8 | success | 200 | Pass | 359.594 | Yes |
| app-192351--scale-75 | scale-75 | dark | 8 | success | 200 | Pass | 158.579 | Yes |
| app-192351--scale-125 | scale-125 | dark | 8 | success | 200 | Pass | 522.285 | Yes |
| app-192351--jpeg-q65 | jpeg-q65 | dark | 8 | success | 200 | Pass | 386.114 | Yes |
| app-192351--blur-0.8 | blur-0.8 | dark | 8 | success | 200 | Pass | 332.942 | Yes |
| app-192351--pad-40 | pad-40 | dark | 8 | success | 200 | Pass | 417.355 | Yes |
| app-192351--crop-12 | crop-12 | dark | 8 | success | 200 | Pass | 343.794 | Yes |
| linkedin-19.49.31 | original | light | 7 | success | 200 | Pass | 56.992 | Yes |
| linkedin-19.49.31--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 46.29 | Yes |
| linkedin-19.49.31--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 72.722 | Yes |
| linkedin-19.49.31--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 52.326 | Yes |
| linkedin-19.49.31--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 62.251 | Yes |
| linkedin-19.49.31--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 64.638 | Yes |
| linkedin-19.49.31--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 58.688 | Yes |
| linkedin-19.49.42 | original | light | 8 | success | 200 | Pass | 86.506 | Yes |
| linkedin-19.49.42--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 77.264 | Yes |
| linkedin-19.49.42--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 103.544 | Yes |
| linkedin-19.49.42--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 81.638 | Yes |
| linkedin-19.49.42--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 90.54 | Yes |
| linkedin-19.49.42--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 94.45 | Yes |
| linkedin-19.49.42--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 89.355 | Yes |
| linkedin-19.49.53 | original | light | 6 | success | 200 | Pass | 50.876 | Yes |
| linkedin-19.49.53--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 39.829 | Yes |
| linkedin-19.49.53--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 66.506 | Yes |
| linkedin-19.49.53--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 44.646 | Yes |
| linkedin-19.49.53--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 51.348 | Yes |
| linkedin-19.49.53--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 53.572 | Yes |
| linkedin-19.49.53--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 50.094 | Yes |
| linkedin-19.50.07 | original | light | 6 | success | 200 | Pass | 49.123 | Yes |
| linkedin-19.50.07--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 40.304 | Yes |
| linkedin-19.50.07--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 65.486 | Yes |
| linkedin-19.50.07--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 45.497 | Yes |
| linkedin-19.50.07--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 51.981 | Yes |
| linkedin-19.50.07--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 55.455 | Yes |
| linkedin-19.50.07--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 58.364 | Yes |
| linkedin-19.50.21 | original | light | 6 | success | 200 | Pass | 54.978 | Yes |
| linkedin-19.50.21--scale-75 | scale-75 | light | 6 | success | 200 | Pass | 46.96 | Yes |
| linkedin-19.50.21--scale-125 | scale-125 | light | 6 | success | 200 | Pass | 74.787 | Yes |
| linkedin-19.50.21--jpeg-q65 | jpeg-q65 | light | 6 | success | 200 | Pass | 47.421 | Yes |
| linkedin-19.50.21--blur-0.8 | blur-0.8 | light | 6 | success | 200 | Pass | 52.924 | Yes |
| linkedin-19.50.21--pad-40 | pad-40 | light | 6 | success | 200 | Pass | 55.15 | Yes |
| linkedin-19.50.21--crop-12 | crop-12 | light | 6 | success | 200 | Pass | 52.123 | Yes |
| linkedin-19.50.37 | original | light | 8 | success | 200 | Pass | 81.8 | Yes |
| linkedin-19.50.37--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 71.302 | Yes |
| linkedin-19.50.37--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 99.987 | Yes |
| linkedin-19.50.37--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 81.939 | Yes |
| linkedin-19.50.37--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 90.512 | Yes |
| linkedin-19.50.37--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 87.157 | Yes |
| linkedin-19.50.37--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 93.046 | Yes |
| linkedin-19.50.47 | original | light | 7 | success | 200 | Pass | 72.021 | Yes |
| linkedin-19.50.47--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 56.601 | Yes |
| linkedin-19.50.47--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 87.411 | Yes |
| linkedin-19.50.47--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 76.969 | Yes |
| linkedin-19.50.47--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 69.49 | Yes |
| linkedin-19.50.47--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 79.06 | Yes |
| linkedin-19.50.47--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 80.738 | Yes |
| linkedin-19.50.57 | original | light | 8 | success | 200 | Pass | 72.71 | Yes |
| linkedin-19.50.57--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 62.26 | Yes |
| linkedin-19.50.57--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 84.608 | Yes |
| linkedin-19.50.57--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 68.107 | Yes |
| linkedin-19.50.57--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 74.986 | Yes |
| linkedin-19.50.57--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 78.871 | Yes |
| linkedin-19.50.57--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 74.42 | Yes |
| linkedin-19.51.06 | original | light | 7 | success | 200 | Pass | 60.228 | Yes |
| linkedin-19.51.06--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 50.106 | Yes |
| linkedin-19.51.06--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 74.101 | Yes |
| linkedin-19.51.06--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 58.789 | Yes |
| linkedin-19.51.06--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 64.529 | Yes |
| linkedin-19.51.06--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 69.999 | Yes |
| linkedin-19.51.06--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 65.399 | Yes |
| linkedin-19.46.03 | original | light | 7 | success | 200 | Pass | 77.54 | Yes |
| linkedin-19.46.03--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 54.28 | Yes |
| linkedin-19.46.03--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 140.804 | Yes |
| linkedin-19.46.03--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 70.789 | Yes |
| linkedin-19.46.03--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 77.492 | Yes |
| linkedin-19.46.03--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 112.399 | Yes |
| linkedin-19.46.03--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 70.366 | Yes |
| linkedin-102225 | original | light | 8 | success | 200 | Pass | 55.887 | Yes |
| linkedin-102225--scale-75 | scale-75 | light | 8 | success | 200 | Pass | 51.363 | Yes |
| linkedin-102225--scale-125 | scale-125 | light | 8 | success | 200 | Pass | 65.967 | Yes |
| linkedin-102225--jpeg-q65 | jpeg-q65 | light | 8 | success | 200 | Pass | 59.414 | Yes |
| linkedin-102225--blur-0.8 | blur-0.8 | light | 8 | success | 200 | Pass | 58.038 | Yes |
| linkedin-102225--pad-40 | pad-40 | light | 8 | success | 200 | Pass | 55.749 | Yes |
| linkedin-102225--crop-12 | crop-12 | light | 8 | success | 200 | Pass | 54.009 | Yes |
| linkedin-102318 | original | light | 7 | success | 200 | Pass | 49.05 | Yes |
| linkedin-102318--scale-75 | scale-75 | light | 7 | success | 200 | Pass | 45.395 | Yes |
| linkedin-102318--scale-125 | scale-125 | light | 7 | success | 200 | Pass | 61.426 | Yes |
| linkedin-102318--jpeg-q65 | jpeg-q65 | light | 7 | success | 200 | Pass | 46.99 | Yes |
| linkedin-102318--blur-0.8 | blur-0.8 | light | 7 | success | 200 | Pass | 52.055 | Yes |
| linkedin-102318--pad-40 | pad-40 | light | 7 | success | 200 | Pass | 54.699 | Yes |
| linkedin-102318--crop-12 | crop-12 | light | 7 | success | 200 | Pass | 63.052 | Yes |
| blank-light | negative | light | 6 | error | 422 | Pass | 61.183 | Yes |
| blank-dark | negative | dark | 6 | error | 422 | Pass | 43.073 | Yes |

## Results by theme

| Theme | Valid | Negative | Exact-board | Expected-error | Median / p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| dark | 77 | 1 | 100.0% | 100.0% | 303.774 / 513.354 |
| light | 161 | 1 | 100.0% | 100.0% | 90.344 / 382.618 |

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
| blur-0.8 | 34 | 100.0% | n/a | 171.863 / 385.488 |
| crop-12 | 34 | 100.0% | n/a | 186.655 / 364.687 |
| jpeg-q65 | 34 | 100.0% | n/a | 201.981 / 419.313 |
| negative | 2 | n/a | 100.0% | 53.262 / 76.307 |
| original | 34 | 100.0% | n/a | 185.058 / 427.549 |
| pad-40 | 34 | 100.0% | n/a | 229.059 / 419.101 |
| scale-125 | 34 | 100.0% | n/a | 286.877 / 566.72 |
| scale-75 | 34 | 100.0% | n/a | 110.279 / 205.691 |

## Dataset coverage

- Original capture cases: 34
- Derived robustness cases: 204
- Valid image cases: 238
- Negative cases: 2
- Total cases: 240
- Measured API requests: 4800
- Supplied board sizes for valid cases: 6x6, 7x7, 8x8

Dataset notes from the manifest:
34 original captures: four legacy app screenshots, 18 app captures representing nine boards in both themes, and 12 LinkedIn captures representing eleven distinct boards. Each original is evaluated unchanged and with six fixed transformations. Two blank negative cases are included. Expected boards reuse the existing manually transcribed fixtures. Board-size hints are supplied. These are development regression and robustness cases, not independent unseen samples; transformed versions are correlated with their originals. All failures are retained.

## Interpretation and limitations

Accuracy is calculated from the first response for each case. Additional
repetitions measure latency and response consistency; they do not increase
the number of independent screenshots. Transformed versions share their
source image, and different captures can show the same puzzle.
240/240 repeatedly evaluated cases returned consistent normalized responses.

An exact-board match requires the supplied board size, ordered waypoint
positions, and complete undirected wall set to match the expected board.
Import success and warning-free responses are checked separately.
Negative-case success requires both the expected HTTP status and error code.
Failed cases remain in the accuracy denominators.

These results describe the cases and conditions listed above. This
development corpus does not establish accuracy on independent unseen images
or on image conditions absent from the dataset. Negative-case results apply
only to the included invalid inputs. Board size is supplied; automatic
size inference is not evaluated.

Latency covers in-process API requests, including first-use requests and
negative cases. Image-transformation time is excluded. These measurements
do not represent browser upload time, deployed-network latency, or concurrent
load performance. A report regenerated from saved metrics reuses the original
measurements and does not constitute a new evaluation run.

metrics.json retains the first response per case, payload SHA-256 hashes,
individual request timings, and a response-stability flag. It does not
retain every repeated response. Exit code 1 indicates an evaluation mismatch
or unstable responses; completed evaluation results are still saved.
