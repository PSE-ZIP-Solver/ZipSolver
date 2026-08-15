/*
 * Client-side pre-checks for the screenshot import.
 *
 * Purely a usability layer, never a correctness one: the backend re-checks the content
 * type and the size at the trust boundary and is authoritative (§3.2.1). The value of
 * doing it here is latency — rejecting a 40 MB video locally is instant, whereas the same
 * rejection over the wire costs the user a full upload first.
 *
 * These limits mirror the backend's ALLOWED_UPLOAD_CONTENT_TYPES and MAX_UPLOAD_BODY_BYTES
 * exactly, so the two layers can never disagree about what is acceptable.
 */

export const ACCEPTED_IMAGE_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
] as const;

/** Mirrors the backend's 10 MiB upload ceiling. */
export const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024;

/** Value for the file input's `accept` attribute, derived so it cannot drift. */
export const IMAGE_ACCEPT_ATTRIBUTE = ACCEPTED_IMAGE_TYPES.join(",");


export type FileValidationResult =
    | { valid: true }
    | { valid: false; reason: string };


function formatMegabytes(bytes: number): string {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


export function validateImageFile(
    file: File,
): FileValidationResult {

    const type = file.type
        .split(";")[0]
        .trim()
        .toLowerCase();

    if (!ACCEPTED_IMAGE_TYPES.includes(type as typeof ACCEPTED_IMAGE_TYPES[number])) {
        return {
            valid: false,
            reason: "Choose a PNG, JPEG, or WebP screenshot",
        };
    }

    if (file.size === 0) {
        return {
            valid: false,
            reason: "That file is empty",
        };
    }

    if (file.size > MAX_IMAGE_SIZE_BYTES) {
        return {
            valid: false,
            reason:
                `That image is ${formatMegabytes(file.size)}. `
                + `The limit is ${formatMegabytes(MAX_IMAGE_SIZE_BYTES)}`,
        };
    }

    return { valid: true };
}