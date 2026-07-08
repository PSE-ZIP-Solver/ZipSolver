import { apiFetch } from "./apiClient";

import {
    type BoardConfig,
} from "../types/board";

import {
    type SolverResponse,
} from "../types/solver";

import {
    type ValidationResult,
} from "../types/validation";

export async function importPuzzle(
    file: File
): Promise<ValidationResult> {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    return apiFetch(
        "/api/import",
        {
            method: "POST",
            body: formData,
        }
    );
}

export async function solvePuzzle(
    board: BoardConfig,
): Promise<SolverResponse> {
    return apiFetch("/api/solve", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(board),
    });
}