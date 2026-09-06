import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MetricsPanel from "./MetricsPanel";

describe("MetricsPanel", () => {
    it("renders default metrics without attempts when no result exists", () => {
        render(<MetricsPanel metrics={null} />);

        expect(screen.getByText("Runtime Ms")).toBeVisible();
        expect(screen.getByText("0 ms")).toBeVisible();
        expect(screen.getByText("Steps")).toBeVisible();
        expect(screen.queryByText("Attempts")).toBeNull();
    });

    it("formats runtime values and renders solver metrics", () => {
        render(
            <MetricsPanel
                metrics={{ runtimeMs: 12.5, steps: 36, attempts: 2 }}
            />,
        );

        expect(screen.getByText("12.5 ms")).toBeVisible();
        expect(screen.getByText("36")).toBeVisible();
        expect(screen.queryByText("Attempts")).toBeNull();
    });
});
