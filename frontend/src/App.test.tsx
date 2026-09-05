import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { cleanup } from "@testing-library/react";
import App from "./App";

describe("App global UI wiring", () => {
    afterEach(() => {
        cleanup();
        document.documentElement.classList.remove("dark");
        document.documentElement.style.colorScheme = "";
        window.localStorage.clear();
    });

    it("toggles the theme and persists the selected preference", () => {
        render(<App />);
        const themeButton = screen.getByRole("button", { name: "Toggle theme" });

        expect(document.documentElement.classList.contains("dark")).toBe(false);
        fireEvent.click(themeButton);

        expect(document.documentElement.classList.contains("dark")).toBe(true);
        expect(document.documentElement.style.colorScheme).toBe("dark");
        expect(window.localStorage.getItem("zipsolver-theme")).toBe("dark");
    });

    it("opens and closes the help dialog with the Escape key", () => {
        render(<App />);

        fireEvent.click(screen.getByRole("button", { name: "Open help" }));
        expect(screen.getByRole("dialog", { name: "Help & Guide" })).toBeVisible();

        fireEvent.keyDown(window, { key: "Escape" });
        expect(screen.queryByRole("dialog", { name: "Help & Guide" })).toBeNull();
    });
});