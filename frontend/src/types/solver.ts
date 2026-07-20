import { type Position } from "./board";

export type SolutionPath = Position[];

export type SolverStatus =
    | "SOLVED"
    | "UNSOLVABLE"
    | "TIMEOUT"
    | "FAILED";

export type SolverType =
    | "RL"
    | "DFS";

export interface SolverMetrics {
    runtimeMs: number;
    steps: number;
}

export interface SolverResponse {
    status: SolverStatus;
    success: boolean;
    solutionPath: SolutionPath | null;
    solverUsed: SolverType;
    message: string;
    metrics: SolverMetrics;
}