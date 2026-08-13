import { type Position } from "./board";

export type SolutionPath = Position[];

export type SolverStatus =
    | "SOLVED"
    | "UNSOLVABLE"
    | "TIMEOUT"
    | "FAILED";

export type SolverUsedType =
    | "RLSolver"
    | "AlgorithmicSolver";

export interface SolverMetrics {
    runtimeMs: number;
    steps: number;
    attempts: number;
}

export interface SolverResponse {
    status: SolverStatus;
    success: boolean;
    solutionPath: SolutionPath | null;
    solverUsed: SolverUsedType;
    message: string;
    metrics: SolverMetrics;
}