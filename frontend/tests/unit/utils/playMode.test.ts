import { describe, expect, it } from "vitest";
import {
    appendVisitedCell,
    createPlayModeState,
    getExpectedNextWaypoint,
    hasCompletedAllWaypoints,
    isCellAlreadyVisited,
    undoVisitedCell,
} from "../../../src/utils/playMode";
import type { BoardConfig } from "../../../src/types/board";

const board: BoardConfig = {
    boardSize: 6,
    waypoints: [[0, 0], [0, 2], [0, 1]],
    walls: [],
};

describe("play mode", () => {
    it("keeps the start cell when undoing and identifies the next waypoint", () => {
        const state = appendVisitedCell(createPlayModeState([0, 0]), [0, 1]);

        expect(undoVisitedCell(state).visitedCells).toEqual([[0, 0]]);
        expect(getExpectedNextWaypoint(state, board)).toEqual([0, 2]);
        expect(isCellAlreadyVisited(state, [0, 0])).toBe(true);
        expect(isCellAlreadyVisited(state, [1, 1])).toBe(false);
    });

    it("recognizes a complete Hamiltonian path with ordered waypoints", () => {
        const remainingCells = Array.from({ length: 6 }, (_, row) =>
            Array.from({ length: 6 }, (_, column) => [row, column] as [number, number])
        ).flat().filter(([row, column]) => !(
            (row === 0 && column === 0)
            || (row === 0 && column === 1)
            || (row === 0 && column === 2)
        ));
        const orderedPath = [[0, 0], [0, 2], ...remainingCells, [0, 1]] as [number, number][];
        const state = { visitedCells: orderedPath };
        const wrongEndpoint = [...orderedPath];
        [wrongEndpoint[wrongEndpoint.length - 2], wrongEndpoint[wrongEndpoint.length - 1]] = [
            wrongEndpoint[wrongEndpoint.length - 1],
            wrongEndpoint[wrongEndpoint.length - 2],
        ];

        expect(hasCompletedAllWaypoints(state, board)).toBe(true);
        expect(hasCompletedAllWaypoints({ visitedCells: wrongEndpoint }, board)).toBe(false);
    });
});