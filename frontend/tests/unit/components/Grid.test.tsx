import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Grid from "../../../src/components/Grid";
import type { BoardConfig, Wall } from "../../../src/types/board";

afterEach(cleanup);

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

function renderInteractiveGrid(editMode: "NUMBERS" | "WALLS") {
    const onCellClick = vi.fn();
    const onWallClick = vi.fn<(wall: Wall) => void>();

    render(
        <Grid
            board={board}
            solution={null}
            editMode={editMode}
            playerPath={[]}
            activePosition={null}
            nextWaypoint={null}
            hintPath={null}
            isPlayMode={false}
            onCellClick={onCellClick}
            onWallClick={onWallClick}
        />,
    );

    return { onCellClick, onWallClick };
}

function renderPlayGrid() {
    const onCellClick = vi.fn();
    const onWallClick = vi.fn<(wall: Wall) => void>();

    render(
        <Grid
            board={board}
            solution={null}
            editMode="NUMBERS"
            playerPath={[]}
            activePosition={null}
            nextWaypoint={null}
            hintPath={null}
            isPlayMode
            onCellClick={onCellClick}
            onWallClick={onWallClick}
        />,
    );

    return { onCellClick };
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

describe("Grid interactions", () => {
    it("reports the clicked cell in number editing mode", () => {
        const { onCellClick } = renderInteractiveGrid("NUMBERS");

        const gridBoard = document.querySelector(".grid-board") as HTMLElement;
        vi.spyOn(gridBoard, "getBoundingClientRect").mockReturnValue({
            left: 0, top: 0, right: 600, bottom: 600, width: 600, height: 600,
            x: 0, y: 0, toJSON: () => ({}),
        });
        Object.assign(gridBoard, {
            setPointerCapture: vi.fn(),
            hasPointerCapture: vi.fn().mockReturnValue(true),
            releasePointerCapture: vi.fn(),
        });

        gridBoard.dispatchEvent(new MouseEvent("pointerdown", { bubbles: true, clientX: 10, clientY: 10 }));
        expect(onCellClick).not.toHaveBeenCalled();
        gridBoard.dispatchEvent(new MouseEvent("pointerup", { bubbles: true, clientX: 10, clientY: 10 }));

        expect(onCellClick).toHaveBeenCalledWith([0, 0]);
    });

    it("reports wall additions in wall editing mode", () => {
        const { onWallClick } = renderInteractiveGrid("WALLS");

        fireEvent.click(screen.getByRole("button", { name: "Add a wall to the right of cell 1, 1" }));

        expect(onWallClick).toHaveBeenCalledWith({
            neighborA: [0, 0],
            neighborB: [0, 1],
        });
    });

    it("handles Play-mode pointer swipes across adjacent cells", () => {
        const { onCellClick } = renderPlayGrid();
        const gridBoard = document.querySelector(".grid-board") as HTMLElement;
        vi.spyOn(gridBoard, "getBoundingClientRect").mockReturnValue({
            left: 0, top: 0, right: 600, bottom: 600, width: 600, height: 600,
            x: 0, y: 0, toJSON: () => ({}),
        });
        Object.assign(gridBoard, {
            setPointerCapture: vi.fn(),
            hasPointerCapture: vi.fn().mockReturnValue(true),
            releasePointerCapture: vi.fn(),
        });

        gridBoard.dispatchEvent(new MouseEvent("pointerdown", { bubbles: true, clientX: 10, clientY: 10 }));
        expect(onCellClick).not.toHaveBeenCalled();
        gridBoard.dispatchEvent(new MouseEvent("pointermove", { bubbles: true, clientX: 110, clientY: 10 }));
        gridBoard.dispatchEvent(new MouseEvent("pointermove", { bubbles: true, clientX: 210, clientY: 10 }));
        gridBoard.dispatchEvent(new MouseEvent("pointerup", { bubbles: true, clientX: 210, clientY: 10 }));

        expect(onCellClick).toHaveBeenCalledWith([0, 1]);
        expect(onCellClick).toHaveBeenCalledWith([0, 2]);
    });

    it("handles Play-mode touch swipes without relying on pointer events", () => {
        const { onCellClick } = renderPlayGrid();
        const gridBoard = document.querySelector(".grid-board") as HTMLElement;
        vi.spyOn(gridBoard, "getBoundingClientRect").mockReturnValue({
            left: 0, top: 0, right: 600, bottom: 600, width: 600, height: 600,
            x: 0, y: 0, toJSON: () => ({}),
        });

        fireEvent.touchStart(gridBoard, {
            touches: [{ identifier: 7, clientX: 10, clientY: 10 }],
        });
        fireEvent.touchMove(gridBoard, {
            touches: [{ identifier: 7, clientX: 110, clientY: 10 }],
        });
        fireEvent.touchEnd(gridBoard, {
            changedTouches: [{ identifier: 7, clientX: 210, clientY: 10 }],
        });

        expect(onCellClick).toHaveBeenCalledWith([0, 1]);
        expect(onCellClick).toHaveBeenCalledWith([0, 2]);
    });
});