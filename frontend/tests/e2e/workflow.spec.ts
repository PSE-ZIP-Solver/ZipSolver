/// <reference types="node" />

import { expect, test } from "@playwright/test";

const serpentinePath = Array.from({ length: 6 }, (_, row) => {
    const columns = Array.from({ length: 6 }, (_, column) => column);
    return row % 2 === 0 ? columns.map((column) => [row, column]) : columns.reverse().map((column) => [row, column]);
}).flat() as [number, number][];

const backendSerpentinePath = serpentinePath.map(([row, column]) => [column, row]);

const solvedResponse = {
    status: "SOLVED",
    success: true,
    solutionPath: backendSerpentinePath,
    solverUsed: "AlgorithmicSolver",
    message: "Solved by fallback",
    metrics: { runtimeMs: 2, steps: serpentinePath.length, attempts: 1 },
};

test.describe("ZipSolver build workflow", () => {
    test("creates a board, edits waypoints and walls, and resets it", async ({ page }) => {
        await page.goto("/");

        await page.getByRole("button", { name: "7×7" }).click();
        const cells = page.locator(".grid-cell");
        await cells.nth(0).click();
        await cells.nth(1).click();
        await expect(page.locator(".grid-board .grid-waypoint")).toHaveCount(2);

        await page.getByRole("button", { name: "Walls" }).click();
        await page.getByRole("button", { name: "Add a wall to the right of cell 1, 1" }).click();
        await expect(
            page.getByRole("button", {
                name: "Remove the wall between cells 1, 1 and 1, 2",
            }),
        ).toBeVisible();

        await page.getByRole("button", { name: "Numbers" }).click();
        await expect(page.getByRole("button", { name: "Show Solution" })).toBeEnabled();

        await page.getByRole("button", { name: "Reset" }).click();
        await expect(page.locator(".grid-board .grid-waypoint")).toHaveCount(0);
        await expect(page.getByText("Puzzle reset")).toBeVisible();
    });
});

test.describe("ZipSolver play workflow", () => {
    test("uses a hint, supports keyboard movement, and locks after completion", async ({ page }) => {
        await page.route("**/api/solve", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify(solvedResponse),
            });
        });

        await page.goto("/");
        const cells = page.locator(".grid-cell");
        await cells.nth(0).click();
        await cells.nth(1).click();

        const playResponse = page.waitForResponse(
            (response) => response.url().endsWith("/api/solve") && response.request().method() === "POST",
        );
        await page.getByRole("button", { name: "Play" }).click();
        await playResponse;

        await page.getByRole("button", { name: "Take Hint" }).click();
        await expect(page.getByText("Hint path to the next waypoint has been highlighted")).toBeVisible();

        for (let index = 1; index < serpentinePath.length; index += 1) {
            const previous = serpentinePath[index - 1];
            const current = serpentinePath[index];
            let key: "ArrowUp" | "ArrowDown" | "ArrowLeft" | "ArrowRight";

            if (current[0] > previous[0]) key = "ArrowDown";
            else if (current[0] < previous[0]) key = "ArrowUp";
            else if (current[1] > previous[1]) key = "ArrowRight";
            else key = "ArrowLeft";

            await page.keyboard.press(key);
        }

        await expect(page.getByText("Puzzle solved! You visited every cell and all waypoints in order")).toBeVisible();
        await expect(page.getByRole("button", { name: "Take Hint" })).toBeDisabled();
    });
});

test.describe("ZipSolver import and solver feedback", () => {
    test("imports a screenshot through the UI", async ({ page }) => {
        await page.route("**/api/import", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    board: { boardSize: 6, waypoints: [[0, 0], [0, 1]], walls: [] },
                    valid: true,
                    message: "Imported",
                    errors: [],
                    warnings: [],
                }),
            });
        });

        await page.goto("/");
        await page.getByLabel("Import a puzzle screenshot").setInputFiles({
            name: "board.png",
            mimeType: "image/png",
            buffer: Buffer.from("mock-image"),
        });
        await expect(page.getByRole("dialog", { name: "Screenshot grid size" })).toBeVisible();
        await page.getByRole("button", { name: "Continue import" }).click();

        await expect(page.getByText("Imported 2 waypoints and 0 walls from your screenshot")).toBeVisible();
        await expect(page.locator(".grid-board .grid-waypoint")).toHaveCount(2);
    });

    test("shows an unsolvable result in the solver UI", async ({ page }) => {
        await page.route("**/api/solve", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    status: "UNSOLVABLE",
                    success: false,
                    solutionPath: null,
                    solverUsed: "AlgorithmicSolver",
                    message: "No solution exists",
                    metrics: { runtimeMs: 3, steps: 0, attempts: 1 },
                }),
            });
        });

        await page.goto("/");
        await page.getByRole("button", { name: /Vincent's Loop 6×6/i }).click();
        await page.getByRole("button", { name: "Show Solution" }).click();

        await expect(page.getByText("No solution exists")).toBeVisible();
        await expect(page.getByText("Solver Metrics")).toBeVisible();
    });
});
