import { expect, test } from "@playwright/test";

test.describe("ZipSolver full-stack workflow", () => {
    test("reports backend readiness through the real API", async ({ request }) => {
        const response = await request.get("http://127.0.0.1:8090/api/health");

        expect(response.ok()).toBe(true);
        await expect(response).toBeOK();
        await expect(response.json()).resolves.toMatchObject({
            status: "ok",
        });
    });

    test("solves an example through the real frontend and backend", async ({ page }) => {
        const solveResponsePromise = page.waitForResponse(
            (response) => response.url().endsWith("/api/solve") && response.request().method() === "POST",
        );

        await page.goto("/");
        await page.getByRole("button", { name: /Tillmann's Breeze 6×6/i }).click();
        await page.getByRole("button", { name: "Show Solution" }).click();

        const solveResponse = await solveResponsePromise;
        expect(solveResponse.ok()).toBe(true);
        const payload = await solveResponse.json();

        expect(payload.status).toBe("SOLVED");
        expect(payload.success).toBe(true);
        expect(payload.solutionPath).toEqual(expect.any(Array));
        expect(["RLSolver", "AlgorithmicSolver"]).toContain(payload.solverUsed);
        await expect(page.getByText("Solver Metrics")).toBeVisible();
        await expect(page.getByText(payload.message)).toBeVisible();
    });

    test("returns a structured validation error for an invalid board", async ({ request }) => {
        const response = await request.post("http://127.0.0.1:8090/api/solve", {
            data: {
                boardSize: 6,
                waypoints: [[0, 0], [0, 0]],
                walls: [],
            },
        });

        expect(response.status()).toBe(422);
        await expect(response.json()).resolves.toMatchObject({
            code: "INVALID_WAYPOINTS",
            status: 422,
        });
    });

    test("imports a screenshot through the real API pipeline", async ({ page, request }) => {
        await page.goto("/");
        await page.getByRole("button", { name: /Tillmann's Breeze 6×6/i }).click();
        await expect(page.locator(".grid-board .grid-waypoint")).toHaveCount(3);

        const screenshot = await page.locator(".grid-board").screenshot();
        const response = await request.post("http://127.0.0.1:8090/api/import", {
            multipart: {
                file: {
                    name: "tillmanns-breeze.png",
                    mimeType: "image/png",
                    buffer: screenshot,
                },
                board_size: "6",
            },
        });

        expect(response.ok()).toBe(true);
        const payload = await response.json();
        expect(payload.board.boardSize).toBe(6);
        expect(payload.board.waypoints).toEqual(expect.arrayContaining([
            [0, 4],
            [2, 2],
            [4, 1],
        ]));
    });
});