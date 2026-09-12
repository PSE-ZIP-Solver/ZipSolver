import { fireEvent, render, screen, cleanup } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import ControlPanel from "../../../src/components/ControlPanel";
import ImportSizeModal from "../../../src/components/ImportSizeModal";
import ActionPanel from "../../../src/components/ActionPanel";

afterEach(() => cleanup());

describe("ControlPanel", () => {
    it("changes edit mode and board size in Build mode", () => {
        const onEditModeChange = vi.fn();
        const onGridSizeChange = vi.fn();

        render(
            <ControlPanel
                boardSize={6}
                editMode="NUMBERS"
                viewMode="BUILD"
                isSolving={false}
                isPlayCompleted={false}
                onGridSizeChange={onGridSizeChange}
                onEditModeChange={onEditModeChange}
                onHint={vi.fn()}
                onClearSolution={vi.fn()}
                onUndo={vi.fn()}
            />,
        );

        fireEvent.click(screen.getByRole("button", { name: "Walls" }));
        fireEvent.click(screen.getByRole("button", { name: "7×7" }));

        expect(onEditModeChange).toHaveBeenCalledWith("WALLS");
        expect(onGridSizeChange).toHaveBeenCalledWith(7);
        expect(screen.queryByRole("button", { name: "Take Hint" })).toBeNull();
    });

    it("shows Play controls and disables them while solving", () => {
        const onHint = vi.fn();
        const onUndo = vi.fn();

        render(
            <ControlPanel
                boardSize={6}
                editMode="NUMBERS"
                viewMode="PLAY"
                isSolving
                isPlayCompleted={false}
                onGridSizeChange={vi.fn()}
                onEditModeChange={vi.fn()}
                onHint={onHint}
                onClearSolution={vi.fn()}
                onUndo={onUndo}
            />,
        );

        const hint = screen.getByRole("button", { name: "Take Hint" });
        const undo = screen.getByRole("button", { name: "Undo" });
        expect(hint).toBeDisabled();
        expect(undo).toBeDisabled();
        fireEvent.click(hint);
        fireEvent.click(undo);
        expect(onHint).not.toHaveBeenCalled();
        expect(onUndo).not.toHaveBeenCalled();
    });

        it("keeps Clear Solution available but locks Undo after completion", () => {
            render(
                <ControlPanel
                    boardSize={6}
                    editMode="NUMBERS"
                    viewMode="PLAY"
                    isSolving={false}
                    isPlayCompleted
                    onGridSizeChange={vi.fn()}
                    onEditModeChange={vi.fn()}
                    onHint={vi.fn()}
                    onClearSolution={vi.fn()}
                    onUndo={vi.fn()}
                />,
            );

            expect(screen.getByRole("button", { name: "Clear Solution" })).toBeEnabled();
            expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
            expect(screen.getByRole("button", { name: "Take Hint" })).toBeDisabled();
        });
});

describe("ImportSizeModal", () => {
    it("selects a size, confirms, and closes on Escape or overlay click", () => {
        const onSelectSize = vi.fn();
        const onConfirm = vi.fn();
        const onCancel = vi.fn();

        const view = render(
            <ImportSizeModal
                isOpen
                selectedSize={6}
                onSelectSize={onSelectSize}
                onConfirm={onConfirm}
                onCancel={onCancel}
            />,
        );

        fireEvent.click(screen.getByRole("button", { name: "7 x 7" }));
        fireEvent.click(screen.getByRole("button", { name: "Continue import" }));
        fireEvent.keyDown(window, { key: "Escape" });

        expect(onSelectSize).toHaveBeenCalledWith(7);
        expect(onConfirm).toHaveBeenCalledOnce();
        expect(onCancel).toHaveBeenCalledOnce();

        view.rerender(
            <ImportSizeModal
                isOpen={false}
                selectedSize={6}
                onSelectSize={onSelectSize}
                onConfirm={onConfirm}
                onCancel={onCancel}
            />,
        );
        expect(document.body.style.overflow).toBe("");

        view.rerender(
            <ImportSizeModal
                isOpen
                selectedSize={6}
                onSelectSize={onSelectSize}
                onConfirm={onConfirm}
                onCancel={onCancel}
            />,
        );
        fireEvent.click(screen.getByRole("dialog").parentElement as HTMLElement);
        expect(onCancel).toHaveBeenCalledTimes(2);
    });
});

describe("ActionPanel", () => {
    it("opens screenshot size selection and confirms the selected file", () => {
        const onImport = vi.fn();

        render(
            <ActionPanel
                canSolve
                canPlay
                isSolving={false}
                isPlayCompleted={false}
                isImporting={false}
                viewMode="BUILD"
                onSolve={vi.fn()}
                onViewModeChange={vi.fn()}
                onReset={vi.fn()}
                onShare={vi.fn()}
                onImport={onImport}
            />,
        );

        const file = new File(["image"], "board.png", { type: "image/png" });
        fireEvent.change(screen.getByLabelText("Import a puzzle screenshot"), {
            target: { files: [file] },
        });

        expect(screen.getByRole("dialog", { name: "Screenshot grid size" })).toBeVisible();
        fireEvent.click(screen.getByRole("button", { name: "8 x 8" }));
        fireEvent.click(screen.getByRole("button", { name: "Continue import" }));

        expect(onImport).toHaveBeenCalledWith(file, 8);
    });
});