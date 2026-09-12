import { expect, test } from "@playwright/test";

const solvedResponse = {
    status: "SOLVED",
    success: true,
    solutionPath: [[0, 0], [1, 0]],
    solverUsed: "AlgorithmicSolver",
    message: "Solved by fallback",
    metrics: { runtimeMs: 2, steps: 2, attempts: 1 },
};

test.describe("ZipSolver mobile touch workflow", () => {
    test("moves through cells with touch pointer events instead of mouse hover", async ({ page }) => {
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
        await page.getByRole("button", { name: "Play" }).click();
        await expect(page.getByText(/Play mode:/)).toBeVisible();

        const board = page.locator(".grid-board");
        const box = await board.boundingBox();
        expect(box).not.toBeNull();
        const cellSize = (box?.width ?? 0) / 6;

        await board.dispatchEvent("pointerdown", {
            bubbles: true,
            pointerId: 1,
            pointerType: "touch",
            isPrimary: true,
            clientX: (box?.x ?? 0) + cellSize / 2,
            clientY: (box?.y ?? 0) + cellSize / 2,
        });
        await board.dispatchEvent("pointermove", {
            bubbles: true,
            pointerId: 1,
            pointerType: "touch",
            isPrimary: true,
            clientX: (box?.x ?? 0) + cellSize + cellSize / 2,
            clientY: (box?.y ?? 0) + cellSize / 2,
        });
        await board.dispatchEvent("pointerup", {
            bubbles: true,
            pointerId: 1,
            pointerType: "touch",
            isPrimary: true,
            clientX: (box?.x ?? 0) + cellSize + cellSize / 2,
            clientY: (box?.y ?? 0) + cellSize / 2,
        });

        await expect(cells.nth(1).locator("div.border-primary")).toBeVisible();
        expect(await page.evaluate(() => window.scrollY)).toBe(0);
    });
});
