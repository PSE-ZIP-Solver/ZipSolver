import { describe, expect, it } from "vitest";
import { createEmptyBoard, toggleWall, toggleWaypoint } from "./boardEditor";

describe("board editor", () => {
    it("toggles waypoints immutably", () => {
        const board = createEmptyBoard(6);
        const withWaypoint = toggleWaypoint(board, [1, 2]);

        expect(board.waypoints).toEqual([]);
        expect(withWaypoint.waypoints).toEqual([[1, 2]]);
        expect(toggleWaypoint(withWaypoint, [1, 2]).waypoints).toEqual([]);
    });

    it("toggles walls immutably", () => {
        const board = createEmptyBoard(6);
        const wall = { neighborA: [2, 2] as [number, number], neighborB: [2, 3] as [number, number] };
        const withWall = toggleWall(board, wall);

        expect(board.walls).toEqual([]);
        expect(withWall.walls).toEqual([wall]);
        expect(toggleWall(withWall, wall).walls).toEqual([]);
    });
});