import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
    testDir: "./tests/e2e",
    testIgnore: /fullstack\.spec\.ts/,
    fullyParallel: true,
    forbidOnly: Boolean(process.env.CI),
    retries: process.env.CI ? 2 : 0,
    reporter: "html",
    use: {
        baseURL: "http://127.0.0.1:5173",
        trace: "on-first-retry",
    },
    projects: [
        {
            name: "chromium",
            testIgnore: /(?:fullstack|mobile)\.spec\.ts/,
            use: { ...devices["Desktop Chrome"] },
        },
        {
            name: "mobile-chromium",
            testMatch: /mobile\.spec\.ts/,
            use: { ...devices["Pixel 5"] },
        },
    ],
    webServer: {
        command: "npm.cmd run dev -- --host 127.0.0.1",
        url: "http://127.0.0.1:5173",
        reuseExistingServer: !process.env.CI,
    },
});