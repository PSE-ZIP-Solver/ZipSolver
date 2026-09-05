import { act, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Grid from "./Grid";
import type { BoardConfig, Wall } from "../types/board";

const board: BoardConfig = {
    boardSize: 6,
    waypoints: [[0, 0], [0, 2]],
    walls: [],
};

function createContext() {
    return {
        clearRect: vi.fn(),
        setTransform: vi.fn(),
        beginPath: vi.fn(),
        closePath: vi.fn(),
        moveTo: vi.fn(),
        lineTo: vi.fn(),
        stroke: vi.fn(),
        fill: vi.fn(),
        arc: vi.fn(),
        fillRect: vi.fn(),
        save: vi.fn(),
        restore: vi.fn(),
    };
}

function renderGrid(solution: [number, number][] | null) {
    const onCellClick = vi.fn();
    const onWallClick = vi.fn<(wall: Wall) => void>();

    return render(
        <Grid
            board={board}
            solution={solution}
            editMode="NUMBERS"
            playerPath={[]}
            activePosition={null}
            nextWaypoint={null}
            hintPath={null}
            isPlayMode={false}
            onCellClick={onCellClick}
            onWallClick={onWallClick}
        />,
    );
}

describe("Grid path animation lifecycle", () => {
    let contexts: ReturnType<typeof createContext>[];
    let frameCallbacks: Map<number, FrameRequestCallback>;
    let cancelledFrames: number[];
    let nextFrameId: number;

    beforeEach(() => {
        contexts = [];
        frameCallbacks = new Map();
        cancelledFrames = [];
        nextFrameId = 0;

        Object.defineProperty(HTMLElement.prototype, "offsetWidth", {
            configurable: true,
            value: 640,
        });
        vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockImplementation(() => {
            const context = createContext();
            contexts.push(context);
            return context as unknown as CanvasRenderingContext2D;
        });
        vi.spyOn(window, "requestAnimationFrame").mockImplementation((callback) => {
            const id = ++nextFrameId;
            frameCallbacks.set(id, callback);
            return id;
        });
        vi.spyOn(window, "cancelAnimationFrame").mockImplementation((id) => {
            cancelledFrames.push(id);
            frameCallbacks.delete(id);
        });
    });

    afterEach(() => vi.restoreAllMocks());

    it("cancels the old solution animation and clears the canvas when the board changes", () => {
        const view = renderGrid([[0, 0], [0, 1], [0, 2]]);
        const initialFrameId = nextFrameId;

        view.rerender(
            <Grid
                board={{ ...board, waypoints: [[5, 5], [5, 4]] }}
                solution={null}
                editMode="NUMBERS"
                playerPath={[]}
                activePosition={null}
                nextWaypoint={null}
                hintPath={null}
                isPlayMode={false}
                onCellClick={vi.fn()}
                onWallClick={vi.fn()}
            />,
        );

        expect(cancelledFrames).toContain(initialFrameId);
        expect(contexts.some((context) => context.clearRect.mock.calls.length > 0)).toBe(true);
        expect(frameCallbacks.has(initialFrameId)).toBe(false);
    });

    it("draws the current path from cell centers after an animation frame", () => {
        renderGrid([[0, 0], [0, 1], [1, 1]]);
        const frameId = nextFrameId;
        const callback = frameCallbacks.get(frameId);
        expect(callback).toBeDefined();

        act(() => {
            callback?.(performance.now() + 700);
        });

        expect(contexts.some((context) => context.moveTo.mock.calls.length > 0)).toBe(true);
        expect(contexts.some((context) => context.lineTo.mock.calls.length > 0)).toBe(true);
    });

    it("does not draw a diagonal segment for a discontinuous solution", () => {
        renderGrid([[0, 0], [1, 1]]);
        const frameId = nextFrameId;
        const callback = frameCallbacks.get(frameId);

        act(() => {
            callback?.(performance.now() + 700);
        });

        const solutionContext = contexts[0];
        expect(solutionContext?.lineTo).not.toHaveBeenCalled();
    });
});