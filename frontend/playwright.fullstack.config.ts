import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
    testDir: "./tests/e2e",
    testMatch: /fullstack\.spec\.ts/,
    fullyParallel: false,
    forbidOnly: Boolean(process.env.CI),
    retries: process.env.CI ? 2 : 0,
    reporter: "html",
    use: {
        baseURL: "http://127.0.0.1:5173",
        trace: "on-first-retry",
    },
    projects: [
        {
            name: "chromium-fullstack",
            use: { ...devices["Desktop Chrome"] },
        },
    ],
    webServer: [
        {
            command: "uv run uvicorn run_api:app --host 127.0.0.1 --port 8090",
            cwd: "..",
            url: "http://127.0.0.1:8090/api/health",
            reuseExistingServer: !process.env.CI,
            timeout: 120_000,
        },
        {
            command: "npm.cmd run dev -- --host 127.0.0.1",
            url: "http://127.0.0.1:5173",
            reuseExistingServer: !process.env.CI,
            timeout: 120_000,
        },
    ],
});