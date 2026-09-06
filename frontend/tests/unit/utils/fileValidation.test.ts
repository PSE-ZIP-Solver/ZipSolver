import { describe, expect, it } from "vitest";
import { MAX_IMAGE_SIZE_BYTES, validateImageFile } from "../../../src/utils/fileValidation";

describe("screenshot file validation", () => {
    it("accepts supported non-empty image files", () => {
        expect(validateImageFile(new File(["image"], "board.png", { type: "image/png" }))).toEqual({ valid: true });
        expect(validateImageFile(new File(["image"], "board.jpg", { type: "image/jpeg; charset=binary" }))).toEqual({ valid: true });
    });

    it("rejects unsupported, empty, and oversized files", () => {
        expect(validateImageFile(new File(["text"], "board.txt", { type: "text/plain" })).valid).toBe(false);
        expect(validateImageFile(new File([], "empty.png", { type: "image/png" })).valid).toBe(false);
        const oversized = new File([new Uint8Array(MAX_IMAGE_SIZE_BYTES + 1)], "large.png", { type: "image/png" });
        expect(validateImageFile(oversized).valid).toBe(false);
    });
});