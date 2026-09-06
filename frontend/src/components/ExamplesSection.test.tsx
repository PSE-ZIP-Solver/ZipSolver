import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import ExamplesSection from "./ExamplesSection";

afterEach(cleanup);

describe("ExamplesSection", () => {
    it("shows examples for the selected board size and reports the selected board", () => {
        const onSelectExample = vi.fn();
        render(<ExamplesSection currentBoardSize={6} onSelectExample={onSelectExample} />);

        expect(screen.getAllByText("6×6").length).toBeGreaterThan(0);
        const example = screen.getByRole("button", { name: /Vincent's Loop 6×6/i });
        fireEvent.click(example);

        expect(onSelectExample).toHaveBeenCalledWith(
            expect.objectContaining({ boardSize: 6 }),
            "Vincent's Loop",
        );
    });

    it("filters the catalogue when the board size changes", () => {
        const { rerender } = render(
            <ExamplesSection currentBoardSize={6} onSelectExample={vi.fn()} />,
        );

        expect(screen.getAllByRole("button", { name: /Vincent's Loop 6×6/i }).length).toBeGreaterThan(0);
        rerender(<ExamplesSection currentBoardSize={7} onSelectExample={vi.fn()} />);

        expect(screen.queryByText("Vincent's Loop")).toBeNull();
        expect(screen.getByText("Vincent's Heaven")).toBeVisible();
    });
});
