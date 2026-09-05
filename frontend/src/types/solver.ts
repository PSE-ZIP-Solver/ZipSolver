import { type Position } from "./board";

/** Ordered path returned by the solver or built by the player. */
export type SolutionPath = Position[];

/** Outcome reported by POST /api/solve; all values are HTTP-200 solver outcomes. */
export type SolverStatus =
    | "SOLVED"
    | "UNSOLVABLE"
    | "TIMEOUT"
    | "FAILED";

/** Concrete solver implementation used for a successful attempt. */
export type SolverUsedType =
    | "RLSolver"
    | "AlgorithmicSolver";

/** Performance figures returned with every solver response. */
export interface SolverMetrics {
    runtimeMs: number;
    steps: number;
    attempts: number;
}

/** Frontend representation of the backend POST /api/solve response. */
export interface SolverResponse {
    status: SolverStatus;
    success: boolean;
    solutionPath: SolutionPath | null;
    solverUsed: SolverUsedType | null;
    message: string;
    metrics: SolverMetrics;
}