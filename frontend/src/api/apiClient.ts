// All API calls use relative URLs (e.g. "/api/solve"). In dev, Vite's proxy
// (vite.config.ts) forwards /api/* to the backend, so there is no host or port here
// and no CORS. In production the frontend is served from the same origin as the API,
// so the same relative URLs work unchanged.

/** Structured error thrown when the backend returns a non-2xx response. */
export class ApiError extends Error {
    readonly status: number;
    readonly code: string;
    readonly details: unknown;

    constructor(status: number, code: string, message: string, details: unknown = null) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.code = code;
        this.details = details;
    }
}

export async function apiFetch<T>(
    endpoint: string,
    options?: RequestInit,
): Promise<T> {
    let response: Response;

    try {
        response = await fetch(endpoint, options);
    } catch {
        // Network-level failure: backend down, or the Vite proxy is pointed at a port
        // nothing is listening on. This is the common cause of a blanket
        // "Solver request failed" in the UI.
        throw new ApiError(
            0,
            "NETWORK_ERROR",
            "Could not reach the server. Is the backend running on the port the Vite proxy targets?",
        );
    }

    if (!response.ok) {
        // The backend emits a structured ErrorResponse on every 4xx/5xx:
        // { status, code, message, details, timestamp }. Surface it so callers can
        // branch on `code` instead of parsing a stringified status.
        let code = "UNKNOWN_ERROR";
        let message = `Request failed with status ${response.status}.`;
        let details: unknown = null;

        try {
            const body = await response.json();
            code = body?.code ?? code;
            message = body?.message ?? message;
            details = body?.details ?? null;
        } catch {
            // Non-JSON error body — keep the defaults above.
        }

        throw new ApiError(response.status, code, message, details);
    }

    return response.json() as Promise<T>;
}