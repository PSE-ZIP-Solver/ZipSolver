import { afterEach, describe, expect, it, vi } from "vitest";
import { apiFetch, ApiError } from "../../../src/api/apiClient";

describe("apiFetch error contract", () => {
    afterEach(() => vi.restoreAllMocks());

    it("preserves structured backend validation errors", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
            code: "INVALID_WAYPOINTS",
            message: "Waypoints are invalid",
            details: [{ errorCode: "DUPLICATE", affectedField: "waypoints", message: "Duplicate cell" }],
        }), { status: 422, headers: { "Content-Type": "application/json" } }));

        await expect(apiFetch("/api/solve")).rejects.toMatchObject({
            status: 422,
            code: "INVALID_WAYPOINTS",
            message: "Waypoints are invalid",
            details: [{ errorCode: "DUPLICATE" }],
        });
    });

    it("falls back to the HTTP status for a non-JSON error response", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("proxy failure", { status: 502 }));

        await expect(apiFetch("/api/health")).rejects.toMatchObject({
            status: 502,
            message: "Request failed with status 502",
        });
    });

    it("maps transport failures to a status-zero ApiError", async () => {
        vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("offline"));

        const failure = await apiFetch("/api/health").catch((error: unknown) => error);

        expect(failure).toBeInstanceOf(ApiError);
        expect(failure as ApiError).toMatchObject({ status: 0 });
        expect((failure as ApiError).message).toContain("Could not reach the ZipSolver backend");
    });
});