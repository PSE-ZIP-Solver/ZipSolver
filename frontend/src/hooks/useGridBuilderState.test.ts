import { act, cleanup, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { importPuzzle, solvePuzzle } from "../api/apiCalls";
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
});