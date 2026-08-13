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

    /*
     * Coordinate conventions:
     *
     * Frontend: [row, column] = [y, x]
     * Backend:  [x, y]
     *
     * Therefore coordinates have to be swapped when
     * sending the board to the backend.
     */
    const apiBoard = {
        ...board,

        waypoints: board.waypoints.map(
            ([row, col]) => [col, row]
        ),

        walls: board.walls.map((wall) => ({
            neighborA: [
                wall.neighborA[1],
                wall.neighborA[0],
            ],
            neighborB: [
                wall.neighborB[1],
                wall.neighborB[0],
            ],
        })),
    };


    console.log(
        "[Frontend] Board before API conversion:",
        board
    );

    console.log(
        "[Frontend] Board sent to API:",
        apiBoard
    );


    const response = await apiFetch(
        "/api/solve",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(apiBoard),
        }
    ) as SolverResponse;


    /*
     * Backend solution path is [x, y].
     *
     * Convert it back to the frontend convention:
     * [row, column] = [y, x].
     */
    if (response.solutionPath) {
        response.solutionPath = response.solutionPath.map(
            ([x, y]) => [y, x]
        );
    }


    console.log(
        "[Frontend] Converted solver response:",
        response
    );


    return response;
}