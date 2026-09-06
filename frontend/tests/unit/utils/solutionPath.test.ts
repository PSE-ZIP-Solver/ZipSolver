import { describe, expect, it } from "vitest";
import { getHintPathToNextWaypoint, normalizeSolutionPath } from "../../../src/utils/solutionPath";
import type { BoardConfig } from "../../../src/types/board";

const board: BoardConfig = {
    boardSize: 6,
    waypoints: [[1, 1], [1, 3], [3, 3]],
    walls: [],
};

describe("solution path projections", () => {
    it("prepends the current board start waypoint without mutating the solver path", () => {
        const solution = [[1, 2], [1, 3]] as [number, number][];

        expect(normalizeSolutionPath(solution, board)).toEqual([[1, 1], [1, 2], [1, 3]]);
        expect(solution).toEqual([[1, 2], [1, 3]]);
    });

    it("returns only the segment to the next required waypoint", () => {
        const solution = [[1, 1], [1, 2], [1, 3], [2, 3], [3, 3]] as [number, number][];

        expect(getHintPathToNextWaypoint(solution, board, [1, 3])).toEqual([
            [1, 1], [1, 2], [1, 3],
        ]);
        expect(getHintPathToNextWaypoint(solution, board, [3, 3])).toEqual([
            [1, 1], [1, 2], [1, 3], [2, 3], [3, 3],
        ]);
    });

    it("does not project a hint when the target is the current cell or absent", () => {
        const solution = [[1, 1], [1, 2], [1, 3]] as [number, number][];

        expect(getHintPathToNextWaypoint(solution, board, [1, 1])).toBeNull();
        expect(getHintPathToNextWaypoint(solution, board, null)).toBeNull();
        expect(getHintPathToNextWaypoint([[0, 0], [0, 1]], board, [1, 3])).toBeNull();
    });
});