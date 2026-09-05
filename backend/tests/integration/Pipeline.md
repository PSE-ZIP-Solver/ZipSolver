New integration scenarios

test_valid_rl_output_passes_real_validation_without_fallback

Verifies the complete successful RL route:

HTTP request
→ real JSON interpreter
→ real input validator
→ real solver controller
→ controlled valid RL result
→ real solution validator
→ API response adapter
→ HTTP response

It confirms that:

The RL result is independently validated.
A valid 36-cell solution is accepted.
A* fallback is not activated.
solverUsed is RLSolver.
Solution path and metrics reach the HTTP response correctly.

test_real_rl_solver_missing_model_activates_real_a_star_fallback

Verifies the production missing-model route using the actual RLSolver, rather than merely using a fake exception.

It confirms that:

A missing model archive does not crash /api/solve.
The real RL solver reports failure safely.
The real controller activates A*.
A* returns a validated solution.
The endpoint returns HTTP 200 with AlgorithmicSolver.