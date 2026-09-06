import { act, cleanup, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { importPuzzle, solvePuzzle } from "../api/apiCalls";
import { ApiError } from "../api/apiClient";
import type { BoardConfig } from "../types/board";
import type { ImportResult } from "../types/validation";
import type { SolverResponse } from "../types/solver";
import useGridBuilderState from "./useGridBuilderState";

vi.mock("../api/apiCalls", () => ({
    importPuzzle: vi.fn(),
    solvePuzzle: vi.fn(),
}));

const mockedImportPuzzle = vi.mocked(importPuzzle);
const mockedSolvePuzzle = vi.mocked(solvePuzzle);

const board: BoardConfig = {
    boardSize: 6,
    waypoints: [[0, 0], [0, 1]],
    walls: [],
};

const solvedResponse: SolverResponse = {
    status: "SOLVED",
    success: true,
    solutionPath: [[0, 0], [0, 1]],
    solverUsed: "AlgorithmicSolver",
    message: "Solved by fallback",
    metrics: { runtimeMs: 4, steps: 2, attempts: 1 },
};

function createImportResult(overrides: Partial<ImportResult> = {}): ImportResult {
    return {
        board,
        valid: true,
        message: "Imported",
        errors: [],
        warnings: [],
        ...overrides,
    };
}

describe("useGridBuilderState workflows", () => {
    afterEach(() => {
        cleanup();
        vi.clearAllMocks();
        window.history.replaceState({}, "", "/");
    });

    it("solves the current board and exposes solution and metrics", async () => {
        mockedSolvePuzzle.mockResolvedValue(solvedResponse);
        const { result } = renderHook(() => useGridBuilderState());

        act(() => {
            result.current.handleSelectExample(board, "Test board");
        });
        await waitFor(() => expect(result.current.board).toEqual(board));

        await act(async () => {
            await result.current.handleSolveClick();
        });

        expect(mockedSolvePuzzle).toHaveBeenCalledWith(board);
        expect(result.current.solution).toEqual(solvedResponse.solutionPath);
        expect(result.current.metrics).toEqual(solvedResponse.metrics);
        expect(result.current.message.message).toBe(solvedResponse.message);
        expect(result.current.isSolving).toBe(false);

        act(() => {
            result.current.handleCellClick([2, 2]);
        });

        expect(result.current.solution).toBeNull();
        expect(result.current.metrics).toBeNull();
    });

    it("invalidates an in-flight solve when reset is pressed", async () => {
        let resolveSolve: (response: SolverResponse) => void = () => undefined;
        mockedSolvePuzzle.mockImplementation(() => new Promise((resolve) => {
            resolveSolve = resolve;
        }));
        const { result } = renderHook(() => useGridBuilderState());

        act(() => {
            result.current.handleSelectExample(board, "Test board");
        });
        await waitFor(() => expect(result.current.board).toEqual(board));
        let solving: Promise<void> | undefined;
        act(() => {
            solving = result.current.handleSolveClick();
        });

        await waitFor(() => expect(result.current.isSolving).toBe(true));
        act(() => result.current.handleReset());
        await act(async () => {
            resolveSolve(solvedResponse);
            await solving;
        });

        expect(result.current.board).toEqual({ boardSize: 6, waypoints: [], walls: [] });
        expect(result.current.solution).toBeNull();
        expect(result.current.metrics).toBeNull();
        expect(result.current.message.message).toBe("Puzzle reset");
    });

    it("imports a board with warnings and keeps the warning visible", async () => {
        mockedImportPuzzle.mockResolvedValue(createImportResult({
            warnings: [{ code: "WAYPOINT_NUMBER_UNREADABLE", message: "Unclear marker", cell: [0, 1] }],
        }));
        const { result } = renderHook(() => useGridBuilderState());
        const file = new File(["image"], "board.png", { type: "image/png" });

        await act(async () => {
            await result.current.handleImportScreenshot(file, 6);
        });

        expect(mockedImportPuzzle).toHaveBeenCalledWith(file, 6);
        expect(result.current.board).toEqual(board);
        expect(result.current.message.message).toContain("could not be read confidently");
        expect(result.current.isImporting).toBe(false);
    });

    it("rejects an unsupported screenshot before calling the API", async () => {
        const { result } = renderHook(() => useGridBuilderState());
        const file = new File(["text"], "board.txt", { type: "text/plain" });

        await act(async () => {
            await result.current.handleImportScreenshot(file, 5 as 6);
        });

        expect(mockedImportPuzzle).not.toHaveBeenCalled();
        expect(result.current.message.message).toBe("Screenshot size must be 6, 7, or 8");
    });

    it("creates a share URL through the clipboard workflow", async () => {
        const writeText = vi.fn().mockResolvedValue(undefined);
        Object.defineProperty(navigator, "clipboard", {
            configurable: true,
            value: { writeText },
        });
        const { result } = renderHook(() => useGridBuilderState());

        act(() => {
            result.current.handleSelectExample(board, "Test board");
        });
        await waitFor(() => expect(result.current.board).toEqual(board));
        await act(async () => {
            await result.current.handleShare();
        });

        expect(writeText).toHaveBeenCalledOnce();
        expect(writeText.mock.calls[0]?.[0]).toContain("board=v1.");
        expect(result.current.message.message).toBe("Share link copied to clipboard");
    });

    it("falls back to a prompt when clipboard access is denied", async () => {
        const writeText = vi.fn().mockRejectedValue(new Error("clipboard denied"));
        const prompt = vi.spyOn(window, "prompt").mockImplementation(() => null);
        Object.defineProperty(navigator, "clipboard", {
            configurable: true,
            value: { writeText },
        });
        const { result } = renderHook(() => useGridBuilderState());

        act(() => {
            result.current.handleSelectExample(board, "Test board");
        });
        await waitFor(() => expect(result.current.board).toEqual(board));
        await act(async () => {
            await result.current.handleShare();
        });

        expect(prompt).toHaveBeenCalledOnce();
        expect(result.current.message.message).toBe("Clipboard access denied. Share link opened manually");
    });

    it("shows a warning instead of calling the solver for an incomplete board", async () => {
        const { result } = renderHook(() => useGridBuilderState());

        await act(async () => {
            await result.current.handleSolveClick();
        });

        expect(mockedSolvePuzzle).not.toHaveBeenCalled();
        expect(result.current.message.message).toBe("Add at least two waypoints first");
    });

    it.each([
        ["UNSOLVABLE", "No solution exists"],
        ["TIMEOUT", "Solver timed out"],
        ["FAILED", "Solver failed"],
    ] as const)("renders a warning or error for solver status %s", async (status, message) => {
        mockedSolvePuzzle.mockResolvedValue({
            status,
            success: false,
            solutionPath: null,
            solverUsed: "AlgorithmicSolver",
            message,
            metrics: { runtimeMs: 8, steps: 0, attempts: 1 },
        });
        const { result } = renderHook(() => useGridBuilderState());

        act(() => result.current.handleSelectExample(board, "Test board"));
        await waitFor(() => expect(result.current.board).toEqual(board));
        await act(async () => {
            await result.current.handleSolveClick();
        });

        expect(result.current.solution).toBeNull();
        expect(result.current.message.message).toBe(message);
    });

    it("maps import API errors to a user-facing message", async () => {
        mockedImportPuzzle.mockRejectedValue(new ApiError(422, "No board", "NO_BOARD_DETECTED"));
        const { result } = renderHook(() => useGridBuilderState());
        const file = new File(["image"], "board.png", { type: "image/png" });

        await act(async () => {
            await result.current.handleImportScreenshot(file, 6);
        });

        expect(result.current.message.message).toBe("No Zip board found in that image. Upload a screenshot showing the full grid");
        expect(result.current.isImporting).toBe(false);
    });

    it("requires Play mode before generating a hint", async () => {
        const { result } = renderHook(() => useGridBuilderState());

        await act(async () => {
            await result.current.handleHint();
        });

        expect(mockedSolvePuzzle).not.toHaveBeenCalled();
        expect(result.current.message.message).toBe("Switch to Play mode first");
    });

    it("enters Play mode and resets the player path at the first waypoint", async () => {
        mockedSolvePuzzle.mockResolvedValue(solvedResponse);
        const { result } = renderHook(() => useGridBuilderState());

        act(() => result.current.handleSelectExample(board, "Test board"));
        await waitFor(() => expect(result.current.board).toEqual(board));
        await act(async () => {
            await result.current.handleViewModeChange("PLAY");
        });

        expect(result.current.viewMode).toBe("PLAY");
        expect(result.current.playModeState.visitedCells).toEqual([[0, 0]]);
        expect(result.current.message.message).toContain("Play mode");
    });

    it("locks Play actions after the player completes the board", async () => {
        mockedSolvePuzzle.mockResolvedValue(solvedResponse);
        const { result } = renderHook(() => useGridBuilderState());
        const path: [number, number][] = [];

        for (let row = 0; row < 6; row += 1) {
            const columns = row % 2 === 0 ? [0, 1, 2, 3, 4, 5] : [5, 4, 3, 2, 1, 0];
            for (const column of columns) {
                path.push([row, column]);
            }
        }

        act(() => result.current.handleSelectExample(board, "Test board"));
        await waitFor(() => expect(result.current.board).toEqual(board));
        await act(async () => {
            await result.current.handleViewModeChange("PLAY");
        });

        for (const position of path.slice(1)) {
            act(() => result.current.handleCellClick(position));
        }

        expect(result.current.isPlayCompleted).toBe(true);
        const completedPath = result.current.playModeState.visitedCells;
        act(() => result.current.handleCellClick(path[path.length - 2]));
        expect(result.current.playModeState.visitedCells).toEqual(completedPath);

        await act(async () => {
            await result.current.handleHint();
            await result.current.handleSolveClick();
        });
        expect(mockedSolvePuzzle).toHaveBeenCalledOnce();
        expect(result.current.playModeState.visitedCells).toEqual(completedPath);
    });
});