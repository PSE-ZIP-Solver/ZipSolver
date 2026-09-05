import { expect, test } from "@playwright/test";

test.describe("Share URL round-trip", () => {
    test("restores the exact board after opening the generated URL", async ({ page, context }) => {
        await context.grantPermissions(["clipboard-read", "clipboard-write"], {
            origin: "http://127.0.0.1:5173",
        });

        await page.goto("/");
        await page.getByRole("button", { name: /Vincent's Loop 6×6/i }).click();

        await page.getByRole("button", { name: "Share" }).click();
        await expect(page.getByText("Share link copied to clipboard")).toBeVisible();

        const originalShareUrl = await page.evaluate(() => navigator.clipboard.readText());
        expect(originalShareUrl).toContain("board=v1.");

        await page.goto(originalShareUrl);
        await expect(page.getByText("Board loaded from shared link")).toBeVisible();
        await expect(page).not.toHaveURL(/board=v1\./);

        await page.getByRole("button", { name: "Share" }).click();
        const restoredShareUrl = await page.evaluate(() => navigator.clipboard.readText());

        expect(new URL(restoredShareUrl).searchParams.get("board")).toBe(
            new URL(originalShareUrl).searchParams.get("board"),
        );
    });
});