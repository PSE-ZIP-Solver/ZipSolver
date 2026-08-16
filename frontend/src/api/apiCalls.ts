import { apiFetch } from "./apiClient";

import {
    type BoardConfig,
    type GridSize,
    type Position,
} from "../types/board";

import {
    type SolverResponse,
} from "../types/solver";

import {
    type ImportResult,
} from "../types/validation";


/*
 * Coordinate conventions (applies to both calls below):
 *
 * Frontend: [row, column] = [y, x]
 * Backend:  [x, y]
 *
 * Every coordinate crossing the boundary is therefore swapped.
 */
function swap(
    [a, b]: Position,
): Position {
    return [b, a];
}


export async function importPuzzle(
    file: File,
    boardSize: GridSize,
): Promise<ImportResult> {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    /*
     * board_size is authoritative.
     *
    * The screenshot grid size is provided manually (6/7/8), so the backend never
    * has to infer it from pixels. Image-only size estimation is unreliable on the
    * app's low-contrast rendering and mis-sizes even clean captures.
     */
    formData.append(
        "board_size",
        String(boardSize)
    );

    const result = await apiFetch<ImportResult>(
        "/api/import",
        {
            method: "POST",
            body: formData,
        }
    );


    if (result.board) {
        result.board = {
            ...result.board,

            waypoints: result.board.waypoints.map(swap),

            walls: result.board.walls.map((wall) => ({
                neighborA: swap(wall.neighborA),
                neighborB: swap(wall.neighborB),
            })),
        };
    }


    console.log(
        "[Frontend] Imported board:",
        result
    );


    return result;
}


export async function solvePuzzle(
    board: BoardConfig,
): Promise<SolverResponse> {

    const apiBoard = {
        ...board,

        waypoints: board.waypoints.map(swap),

        walls: board.walls.map((wall) => ({
            neighborA: swap(wall.neighborA),
            neighborB: swap(wall.neighborB),
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


    const response = await apiFetch<SolverResponse>(
        "/api/solve",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(apiBoard),
        }
    );


    if (response.solutionPath) {
        response.solutionPath = response.solutionPath.map(swap);
    }


    console.log(
        "[Frontend] Converted solver response:",
        response
    );


    return response;
}