const API_BASE_URL =
    import.meta.env.VITE_API_URL ??
    "http://localhost:8090";


/*
 * Machine-readable identifiers from the backend error taxonomy (§5.5.5).
 *
 * The backend never returns a bare failure: every 4xx/5xx carries a structured
 * ErrorResponse with a stable `code` the UI can branch on. Mirroring the union here keeps
 * the two sides of the contract in step.
 */
export type ApiErrorCode =
    | "MALFORMED_REQUEST"
    | "UNSUPPORTED_BOARD_SIZE"
    | "INVALID_WAYPOINTS"
    | "INVALID_WALLS"
    | "NO_BOARD_DETECTED"
    | "AMBIGUOUS_BOARD"
    | "PAYLOAD_TOO_LARGE"
    | "INTERNAL_ERROR";


export interface ApiErrorDetail {
    errorCode: string;
    affectedField?: string | null;
    message: string;
}


/*
 * Thrown for any non-2xx response.
 *
 * Previously this layer threw `new Error("API Error 422")`, which discarded the whole
 * envelope — so the UI could only ever say "request failed" even though the backend had
 * already explained precisely what was wrong and which field caused it.
 */
export class ApiError extends Error {

    readonly status: number;

    readonly code: ApiErrorCode | null;

    readonly details: ApiErrorDetail[];

    constructor(
        status: number,
        message: string,
        code: ApiErrorCode | null = null,
        details: ApiErrorDetail[] = [],
    ) {
        super(message);

        this.name = "ApiError";
        this.status = status;
        this.code = code;
        this.details = details;
    }
}


async function readErrorBody(
    response: Response,
): Promise<ApiError> {

    /*
     * A proxy, a network appliance, or an unhandled crash can produce a non-JSON body.
     * Falling back to the status keeps the thrown error useful instead of replacing one
     * opaque failure with another.
     */
    try {
        const body = await response.json();

        return new ApiError(
            response.status,

            typeof body?.message === "string" && body.message.length > 0
                ? body.message
                : `Request failed with status ${response.status}`,

            typeof body?.code === "string"
                ? (body.code as ApiErrorCode)
                : null,

            Array.isArray(body?.details)
                ? (body.details as ApiErrorDetail[])
                : [],
        );

    } catch {
        return new ApiError(
            response.status,
            `Request failed with status ${response.status}`,
        );
    }
}


export async function apiFetch<T>(
    endpoint: string,
    options?: RequestInit,
): Promise<T> {

    let response: Response;

    try {
        response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            options,
        );

    } catch (error) {

        /*
         * fetch only rejects for transport-level problems: the backend is not running,
         * DNS failed, or CORS blocked the response. Status 0 marks "never reached the
         * server", which points the user at a different remedy than any HTTP error.
         */
        console.error("[API] Network request failed:", error);

        throw new ApiError(
            0,
            "Could not reach the ZipSolver backend. Make sure it is running on "
            + `${API_BASE_URL}.`,
        );
    }

    if (!response.ok) {
        throw await readErrorBody(response);
    }

    return response.json() as Promise<T>;
}