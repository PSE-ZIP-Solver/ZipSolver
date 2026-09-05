import { afterEach, describe, expect, it, vi } from "vitest";
import { importPuzzle, solvePuzzle } from "./apiCalls";
import type { BoardConfig } from "../types/board";

const board: BoardConfig = {
    boardSize: 6,
    waypoints: [[1, 2], [4, 5]],
    walls: [{ neighborA: [2, 3], neighborB: [2, 4] }],
};

describe("API coordinate contract", () => {
    afterEach(() => vi.restoreAllMocks());

    it("transposes board coordinates on solve and response path", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
            status: "SOLVED",
            success: true,
            solutionPath: [[2, 1], [5, 4]],
            solverUsed: "AlgorithmicSolver",
            message: "Solved",
            metrics: { runtimeMs: 1, steps: 2, attempts: 1 },
        }), { status: 200, headers: { "Content-Type": "application/json" } }));

        const result = await solvePuzzle(board);
        const request = fetchMock.mock.calls[0]?.[1];
        const body = JSON.parse(request?.body as string);

        expect(body.waypoints).toEqual([[2, 1], [5, 4]]);
        expect(body.walls).toEqual([{ neighborA: [3, 2], neighborB: [4, 2] }]);
        expect(result.solutionPath).toEqual([[1, 2], [4, 5]]);
    });

    it("uses multipart form data for screenshot import and transposes the board", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
            board: { boardSize: 6, waypoints: [[2, 1]], walls: [{ neighborA: [3, 2], neighborB: [4, 2] }] },
            valid: true,
            message: "Imported",
            errors: [],
            warnings: [],
        }), { status: 200, headers: { "Content-Type": "application/json" } }));

        const result = await importPuzzle(new File(["image"], "board.png", { type: "image/png" }), 6);
        expect(result.board).toEqual({
            boardSize: 6,
            waypoints: [[1, 2]],
            walls: [{ neighborA: [2, 3], neighborB: [2, 4] }],
        });
    });
});