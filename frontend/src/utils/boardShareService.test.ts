import { describe, expect, it } from "vitest";
import {
    createShareUrl,
    decodeBoardFromShareToken,
    encodeBoardToShareToken,
    loadBoardFromSearch,
} from "./boardShareService";
import type { BoardConfig } from "../types/board";

const board: BoardConfig = {
    boardSize: 7,
    waypoints: [[0, 0], [2, 4], [6, 6]],
    walls: [
        { neighborA: [0, 1], neighborB: [0, 2] },
        { neighborA: [3, 3], neighborB: [4, 3] },
    ],
};

describe("share URL round-trip", () => {
    it("restores the complete board configuration from a generated URL", () => {
        const shareUrl = createShareUrl(board, "https://example.test/solver?mode=edit");
        const restoredBoard = loadBoardFromSearch(new URL(shareUrl).search);

        expect(new URL(shareUrl).searchParams.has("board")).toBe(true);
        expect(restoredBoard).toEqual(board);
    });

    it("preserves the token payload independently of URL handling", () => {
        const token = encodeBoardToShareToken(board);

        expect(decodeBoardFromShareToken(token)).toEqual(board);
    });
});