import { describe, expect, it } from "vitest";
import { hasWallBetween, isValidGameMove } from "../../../src/utils/gameMode";
import type { BoardConfig } from "../../../src/types/board";

const board: BoardConfig = {
    boardSize: 6,
    waypoints: [],
    walls: [{ neighborA: [1, 1], neighborB: [1, 2] }],
};

describe("game move rules", () => {
    it("accepts adjacent moves and rejects bounds, diagonal, and wall crossings", () => {
        expect(isValidGameMove([1, 1], [1, 0], board)).toBe(true);
        expect(isValidGameMove([1, 1], [0, 0], board)).toBe(false);
        expect(isValidGameMove([0, 0], [-1, 0], board)).toBe(false);
        expect(isValidGameMove([1, 1], [1, 2], board)).toBe(false);
    });

    it("treats a wall as symmetric", () => {
        expect(hasWallBetween([1, 1], [1, 2], board.walls)).toBe(true);
        expect(hasWallBetween([1, 2], [1, 1], board.walls)).toBe(true);
        expect(hasWallBetween([1, 1], [2, 1], board.walls)).toBe(false);
    });
});